"""End-to-end OFFLINE proof that the optimizer loop is engine-neutral.

A real (tiny) Nevergrad optimization runs against the `SpectreSimulator` adapter
over a FAKE bridge — no ngspice binary, no Cadence, no virtuoso-bridge install, no
`requires_ngspice` marker. This pins the factory promise end-to-end: whatever the factory
returns (any structural `Simulator`) flows through ``evaluate`` / ``optimize``
unchanged. After this, the only gaps between the repo and a live Spectre optimization
are construction-time ones — a `.scs` deck (translated or hand-written) and the
installed bridge — both guarded with actionable errors in `simulator_factory`.
"""

from __future__ import annotations

import sys
from concurrent.futures import Future
from pathlib import Path

import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT
from spicexplorer.backends.spectre import SpectreSimulator
from spicexplorer.core.domains import Project_Setup

EXAMPLE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"
FC_YAML = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"


class _FakeBridge:
    """The exact bridge surface the adapter drives (`run_simulation` / `submit`).

    Returns a flat PSF-ish dict whose values depend monotonically on the staged
    design params, so the optimizer sees a real (if silly) landscape rather than a
    constant. Keys are bare spec names — exercising `SpectreSimResult`'s un-prefixed
    fallback lookup, the same path per-MOS op-point keys take."""

    def __init__(self, spec_names):
        self.spec_names = list(spec_names)
        self.calls = []  # (netlist, params) per completed run

    def _data(self, params):
        design = params.get("design_params") or {}
        knob = float(sum(design.values())) if design else 0.0
        return {name: 1.0 + 0.1 * knob for name in self.spec_names}

    def run_simulation(self, netlist, params):
        self.calls.append((netlist, dict(params)))
        return type("FakeSimulationResult", (), {"data": self._data(params)})()

    def submit(self, netlist, params):
        fut: Future = Future()
        fut.set_result(self.run_simulation(netlist, params))
        return fut


def _spectre_optimizer(yaml_path, tmp_path):
    from spicexplorer.optimization.stochastic.nevergrad import (
        Nevergrad_Spice_Single_Objective,
    )
    from spicexplorer_core.spice_engine import Simulator

    p = Project_Setup.from_yaml(yaml_path)
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]
    bridge = _FakeBridge(spec_names)
    # Dict is invariant, so declare the protocol type up front — dict[str, SpectreSimulator]
    # is not assignable to Dict[..., Simulator] even though the adapter conforms.
    sims: dict[str, Simulator] = {
        tb.name: SpectreSimulator(bridge, netlist=Path(p.ws_root) / Path(tb.netlist))
        for tb in p.testbenches
        if tb.enable
    }
    assert sims, "the example YAML must have at least one enabled testbench"
    opt = Nevergrad_Spice_Single_Objective(
        setup_obj=p, spicelib_wrappers=sims, output_root=tmp_path / "ckpts"
    )
    opt.disable_autosave = True
    return p, opt, bridge, spec_names


def test_evaluate_runs_offline_spectre_in_both_dispatch_modes(tmp_path):
    """One full evaluate() through the Spectre adapter — parallel (submit/Future)
    AND sequential (blocking run) — scoring every enabled spec, ngspice-free."""
    p, opt, bridge, spec_names = _spectre_optimizer(EXAMPLE_YAML, tmp_path)

    for parallel in (True, False):
        p.parallel_sim = parallel
        score, fit_summary = opt.evaluate({"W1": 2.0, "L1": 1.0}, append_to_log=False)
        assert np.isfinite(float(score))
        assert set(fit_summary) == set(spec_names), f"parallel={parallel}"
        for info in fit_summary.values():
            assert np.isfinite(float(info["curr_val"]))

    # the optimizer's design params were staged on the adapter and forwarded to the
    # bridge on every run (this is what P2's parameters-line emitter will consume)
    assert bridge.calls
    for _netlist, params in bridge.calls:
        assert params["design_params"], "design params must reach the bridge"

    # a stubbed remote run writes no local log — log harvesting must simply skip it
    assert opt.last_eval_log_files == {}


def test_tiny_optimize_runs_entirely_through_the_fake_bridge(tmp_path):
    """The actual optimization loop (ask → simulate → score → tell), budget=4,
    with every simulation served by the fake Spectre bridge."""
    p, opt, bridge, _spec_names = _spectre_optimizer(EXAMPLE_YAML, tmp_path)
    p.parallel_sim = False
    p.optimizer_config.budget = 4

    # other tests (or a live-Spectre dev venv) may already have bridge modules loaded;
    # what must hold is that the LOOP itself pulls none in.
    bridge_modules_before = {m for m in sys.modules if "virtuoso_bridge" in m}

    opt.parameterize()  # builds the Nevergrad parametrization (the documented call order)
    log = opt.optimize()

    assert log is not None and len(log) == 4
    assert all(np.isfinite(float(e.point.score)) for e in log)
    # every trial's sims went through the bridge (>= budget × enabled testbenches)
    enabled_tbs = sum(1 for tb in p.testbenches if tb.enable)
    assert len(bridge.calls) >= 4 * enabled_tbs
    # the loop pulled in neither the real bridge nor any Cadence dependency
    assert {m for m in sys.modules if "virtuoso_bridge" in m} == bridge_modules_before


@pytest.mark.skipif(not FC_YAML.exists(), reason="folded_cascode example missing")
def test_multi_corner_evaluate_through_the_spectre_adapter(tmp_path):
    """The Phase-2 multi-corner loop drives the Spectre adapter's `apply_corner`
    (include/section + temp + rails staged per corner) with corner-namespaced
    scores — engine-neutral all the way through the PVT axis."""
    p, opt, bridge, spec_names = _spectre_optimizer(FC_YAML, tmp_path)
    assert p.pvt is not None and p.pvt.is_multi()
    p.parallel_sim = False  # sequential corner loop (the parallel axis is covered above)
    corners = [c.name for c in p.pvt.corners_to_run()]

    score, fit_summary = opt.evaluate({"x": 1.0}, append_to_log=False)

    assert np.isfinite(float(score))
    assert set(fit_summary) == {f"{c}::{s}" for c in corners for s in spec_names}
    # every corner's selection reached the bridge: corner name, include lines, temp
    seen_corners = [params["corner"] for _n, params in bridge.calls if "corner" in params]
    assert set(seen_corners) == set(corners)
    for _netlist, params in bridge.calls:
        assert params["corner_includes"], "corner include lines must be staged"
        assert "temp" in params
