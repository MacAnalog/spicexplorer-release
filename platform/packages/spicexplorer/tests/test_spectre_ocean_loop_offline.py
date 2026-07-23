"""End-to-end OFFLINE proof of the native-Spectre + OCEAN metric path in the loop.

A real (tiny) Nevergrad optimization runs against native-`.scs` `SpectreSimulator`s over a
FAKE bridge (which persists a per-run raw dir), with the canonical metrics served by a
FAKE `ocean` (`fake_ocean.py`). No Cadence, no ngspice, no virtuoso-bridge. This pins the
whole seam: the testbench is a hand-written `.scs` FILE (the YAML `netlist:`), each
candidate's design params are rewritten into that deck's `parameters` line (the only path
that injects, since the bridge runs a fixed deck verbatim), the run's raw dir reaches the
OCEAN session, and the OCEAN scalar is merged under the target-spec name so the scorer
reads it through the unchanged `result.scalar(name, analysis)` call.
"""

from __future__ import annotations

import sys
import textwrap
from concurrent.futures import Future
from pathlib import Path

import numpy as np
import pytest
from spicexplorer.backends.ocean_metrics import OceanMetricsSession
from spicexplorer.backends.spectre import SpectreSimulator
from spicexplorer.core.domains import Project_Setup
from spicexplorer.optimization.ocean_integration import OceanMergeContext, build_recipes
from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

FAKE_OCEAN = Path(__file__).parent / "fake_ocean.py"

# A hand-written native Spectre testbench (what `netlist:` points at). Its `parameters`
# line carries the design var `w0`, rewritten per candidate.
NATIVE_TB = """// tb_ac (native Spectre)
simulator lang=spectre
global 0
parameters w0=1e-6
include "dut.scs"
v1 (vdd 0) vsource dc=1.2
xdut (v_out) dut w=w0
dcOp dc
ac ac start=1 stop=1e8 dec=101
"""

_YAML = """
project:
  name: native-spectre-loop
  description: native Spectre .scs testbench + OCEAN metrics
  simulator: spectre
  ws_root: .
  netlist: dut.scs
  outdir: out
  sim_engine: spectre
  tech_spec:
    name: tsmc-n65
    constraints: {}
  dut_params:
    - name: w0
      min_val: 1e-7
      max_val: 1e-5
  testbenches:
    - name: tb_ac
      netlist: spice/tb_ac.scs
      params: []
  optimizer_config:
    name: SamplingSearch
    type: nevergrad
    budget: 3
    target_specs:
      - name: ugf
        testbench: tb_ac
        sim_type: ac
        goal: exceed
        target: 2e6
        range: 1e6
        measurement:
          result: ac
          expr: gainBwProd(v("v_out"))
"""


class _FakeBridge:
    """The bridge surface the composed adapter drives, persisting a distinct raw dir per
    run (as the real bridge does under `work_dir=`) so OCEAN has something to open."""

    def __init__(self, raw_root: Path):
        self.raw_root = raw_root
        self.calls = []  # (netlist, params) per run
        self.decks = []  # the rendered .scs text per run (to assert injection)

    def _result(self, netlist, params):
        self.calls.append((netlist, dict(params)))
        self.decks.append(Path(netlist).read_text())
        n = len(self.calls)
        raw = self.raw_root / f"run{n:04d}.raw"
        raw.mkdir(parents=True, exist_ok=True)
        # PSF data is empty — the metric must come from OCEAN, not the flat dict
        return type("R", (), {"data": {}, "metadata": {"output_dir": str(raw)}})()

    def run_simulation(self, netlist, params):
        return self._result(netlist, params)

    def submit(self, netlist, params):
        fut: Future = Future()
        fut.set_result(self._result(netlist, params))
        return fut


def _build(tmp_path, *, yaml_body=_YAML, inject_ocean=True):
    tmp_path = Path(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    yaml_path = tmp_path / "project_setup.yaml"
    yaml_path.write_text(textwrap.dedent(yaml_body))
    proj = Project_Setup.from_yaml(yaml_path)

    bridge = _FakeBridge(tmp_path / "raws")
    sims = {}
    for tb in proj.testbenches:
        if not tb.enable:
            continue
        # materialize the testbench's native .scs at its ws_root-relative `netlist:` path
        scs = Path(proj.ws_root) / tb.netlist
        scs.parent.mkdir(parents=True, exist_ok=True)
        scs.write_text(NATIVE_TB)
        sims[tb.name] = SpectreSimulator(
            bridge, native_scs=scs, deck_dir=tmp_path / f"decks_{tb.name}"
        )

    opt = Nevergrad_Spice_Single_Objective(
        setup_obj=proj, spicelib_wrappers=sims, output_root=tmp_path / "ckpts"
    )
    opt.disable_autosave = True

    if inject_ocean:
        # Inject a fake-ocean-backed merge context (bypasses the real `from_vb_env` spawn).
        ctx = OceanMergeContext(build_recipes(proj.optimizer_config.target_specs))
        ctx._session = OceanMetricsSession(
            work_dir=tmp_path / "ocean_work", _argv=[sys.executable, str(FAKE_OCEAN)]
        )
        opt._ocean_ctx = ctx
        opt._ocean_ctx_built = True
    return proj, opt, bridge


@pytest.mark.parametrize("parallel", [False, True])
def test_evaluate_scores_the_ocean_metric_not_the_empty_psf(tmp_path, parallel):
    proj, opt, bridge = _build(tmp_path)
    proj.parallel_sim = parallel

    score, fit_summary = opt.evaluate({"w0": 2e-6}, append_to_log=False)

    assert np.isfinite(float(score))
    # the empty PSF would give NaN; the OCEAN value (fake ocean → 42.0) is what's scored
    assert set(fit_summary) == {"ugf"}
    assert fit_summary["ugf"]["curr_val"] == pytest.approx(42.0)
    # the candidate's swept design param was INJECTED into the rendered native .scs
    assert bridge.decks and all("w0=2e-06" in deck for deck in bridge.decks)


def test_tiny_optimize_runs_through_composed_deck_plus_ocean(tmp_path):
    proj, opt, bridge = _build(tmp_path)
    proj.parallel_sim = False

    import sys as _sys
    bridge_mods_before = {m for m in _sys.modules if "virtuoso_bridge" in m}

    opt.parameterize()
    log = opt.optimize()

    assert log is not None and len(log) == 3
    # every trial's score reflects the OCEAN metric surfaced under the spec name
    for entry in log:
        assert (entry.fit_summary or {})["ugf"]["curr_val"] == pytest.approx(42.0)
    # loop pulled in no real Cadence dependency
    assert {m for m in _sys.modules if "virtuoso_bridge" in m} == bridge_mods_before
    # optimize()'s finally closed the OCEAN session (license released)
    assert opt._ocean_ctx._session is None


def test_ensure_ocean_ctx_auto_builds_for_spectre_with_recipes(tmp_path):
    # The REAL trigger — not the injected ctx — must build a context for a Spectre run
    # whose target specs carry recipes, without spawning an ocean process (build is offline).
    _proj, opt, _bridge = _build(tmp_path, inject_ocean=False)
    ctx = opt._ensure_ocean_ctx()
    assert ctx is not None
    assert ctx.testbenches == frozenset({"tb_ac"})
    assert ctx._session is None  # merge-time only; nothing spawned by the guard/build
    assert opt._ensure_ocean_ctx() is ctx  # cached (one context per run)


def test_ensure_ocean_ctx_is_none_for_ngspice_and_for_no_recipe(tmp_path):
    _proj, opt, _bridge = _build(tmp_path, inject_ocean=False)
    opt.setup_obj.sim_engine = "ngspice"  # not spectre → no OCEAN path
    assert opt._ensure_ocean_ctx() is None

    # spectre but no target carries a measurement recipe → also None
    _p2, opt2, _b2 = _build(tmp_path / "b", inject_ocean=False)
    for t in opt2.target_specs.targets:
        t.measurement = None
    opt2._ocean_ctx_built = False  # re-arm the lazy build
    assert opt2._ensure_ocean_ctx() is None


def test_close_and_context_manager_release_the_ocean_session(tmp_path):
    _proj, opt, _bridge = _build(tmp_path)  # injected fake-ocean ctx with a live session
    assert opt._ocean_ctx._session is not None
    opt.close()
    assert opt._ocean_ctx._session is None
    opt.close()  # idempotent

    _p2, opt2, _b2 = _build(tmp_path / "cm")
    with opt2:
        assert opt2._ocean_ctx._session is not None
    assert opt2._ocean_ctx._session is None  # __exit__ closed it


_YAML_MULTI = _YAML.rstrip() + """
  pvt:
    mode: multi
    active_corner: tt
    score_aggregation: mean
    corners:
      - name: tt
        enabled: true
        model_includes: [{lib_file: /x/models.scs, section: tt_lvt}]
        supply: {node: VDD, value: 1.2}
        temp: 27
      - name: ss
        enabled: true
        model_includes: [{lib_file: /x/models.scs, section: ss_lvt}]
        supply: {node: VDD, value: 1.08}
        temp: 85
"""


def test_multi_corner_parallel_merges_ocean_per_corner(tmp_path):
    # The parallel-corner path (_evaluate_corners_parallel) bypasses _evaluate_at_current_corner
    # but still funnels through _extract_and_score_current, so the OCEAN merge must run per
    # corner on that corner's own raw dir — proven here with 2 corners + parallel_sim.
    proj, opt, bridge = _build(tmp_path, yaml_body=_YAML_MULTI)
    assert proj.pvt is not None and proj.pvt.is_multi()
    proj.parallel_sim = True

    score, fit_summary = opt.evaluate({"w0": 2e-6}, append_to_log=False)
    assert np.isfinite(float(score))
    # multi-mode fit_summary is keyed "<corner>::<spec>"; every corner's OCEAN metric landed
    assert set(fit_summary) == {"tt::ugf", "ss::ugf"}
    for key in ("tt::ugf", "ss::ugf"):
        assert fit_summary[key]["curr_val"] == pytest.approx(42.0)
    opt.close()
