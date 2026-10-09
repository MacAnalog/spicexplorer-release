"""End-to-end OFFLINE proof that the optimizer loop is engine-neutral.

A real (tiny) Nevergrad optimization runs against the `SpectreSimulator` adapter
over a FAKE bridge — no ngspice binary, no Cadence, no virtuoso-bridge install, no
`requires_ngspice` marker. This pins the factory promise end-to-end: whatever the factory
returns (any structural `Simulator`) flows through ``evaluate`` / ``optimize``
unchanged. After this, the only gaps between the repo and a live Spectre optimization
are construction-time ones — a `.scs` deck (translated or hand-written) and the
installed bridge — both guarded with actionable errors in `simulator_factory`.

It also checks the two places where the adapter must agree with `spicexplorer_spectre`:
a run the bridge calls fatal or partial scores as a failure (NaN -> MAX_PENALTY, as a
failed ngspice run does), and a corner deck writes `tnom` next to `temp`, so it passes
`spicexplorer_spectre.decklint`.
"""

from __future__ import annotations

import logging
import sys
from concurrent.futures import Future
from enum import Enum
from pathlib import Path

import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT
from spicexplorer.backends.spectre import SpectreSimResult, SpectreSimulator
from spicexplorer.backends.spectre_deck import (
    DEFAULT_SIMULATOR_OPTIONS,
    DEFAULT_TNOM,
    SpectreDeckSpec,
    dc_oppoint_analysis,
    render_native_scs,
    render_spectre_deck,
)
from spicexplorer.core.domains import Project_Setup
from spicexplorer_core.pvt import Corner, ModelInclude

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


class _Status(str, Enum):
    """The bridge's `ExecutionStatus` shape: a str-valued enum (`.value` is the word)."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


class _VerdictResult:
    """A bridge `SimulationResult` that carries its verdict, as the real one always does:
    `ok` / `status` / `errors`, and `metadata["returncode"]` once a process ran."""

    def __init__(self, *, ok, status, errors=(), returncode=None, data=None, output_dir=None):
        self.ok = ok
        self.status = status
        self.errors = list(errors)
        self.warnings = []
        self.data = dict(data or {})
        self.metadata = {}
        if returncode is not None:
            self.metadata["returncode"] = returncode
        if output_dir is not None:
            self.metadata["output_dir"] = str(output_dir)


class _FailingBridge(_FakeBridge):
    """Every run comes back FATAL with a partly-written PSF: the same numbers
    the passing bridge returns, plus the verdict that says they are not a result."""

    def run_simulation(self, netlist, params):
        self.calls.append((netlist, dict(params)))
        return _VerdictResult(
            ok=False,
            status=_Status.PARTIAL,
            errors=["FATAL: convergence failure in tran"],
            returncode=1,
            data=self._data(params),
        )


def _spectre_optimizer(yaml_path, tmp_path, bridge_cls=_FakeBridge):
    from spicexplorer.optimization.stochastic.nevergrad import (
        Nevergrad_Spice_Single_Objective,
    )
    from spicexplorer_core.spice_engine import Simulator

    p = Project_Setup.from_yaml(yaml_path)
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]
    bridge = bridge_cls(spec_names)
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


# ---------------------------------------------------------------------------
# SIM-D01 — the bridge's failure verdict reaches the score
# ---------------------------------------------------------------------------


class _VerdictBridge:
    """Hands back one fixed `_VerdictResult` per run, blocking or submitted."""

    def __init__(self, result):
        self.result = result

    def run_simulation(self, netlist, params):
        return self.result

    def submit(self, netlist, params):
        fut: Future = Future()
        fut.set_result(self.result)
        return fut


def _dispatch(sim, mode):
    return sim.run() if mode == "run" else sim.submit().result()


# Each case is a run `spicexplorer_spectre.lane._finish` reports as FAILED: the
# returncode and the bridge's `ok` are each sufficient to fail a run (Codex SPC-01).
_FAILED_RUNS = {
    # the audit's probe: FATAL in tran, PSF partly written, rc 1
    "partial-rc1": dict(
        ok=False,
        status=_Status.PARTIAL,
        errors=["FATAL: convergence failure in tran"],
        returncode=1,
    ),
    # rc 0 but the log carried a fatal error: the verdict alone must fail it
    "fatal-rc0": dict(
        ok=False, status="partial", errors=["Spectre reported a fatal error"], returncode=0
    ),
    # a nonzero exit fails the run whatever the verdict says
    "rc-nonzero": dict(ok=True, status="success", errors=[], returncode=139),
    # killed by a signal: subprocess reports it as a NEGATIVE returncode, still a failure
    "rc-signal": dict(ok=True, status="success", errors=[], returncode=-11),
    # the bridge never started a process (no metadata at all)
    "error-no-rc": dict(
        ok=False, status=_Status.ERROR, errors=["Netlist file not found"], returncode=None
    ),
}


@pytest.mark.parametrize("mode", ["run", "submit"])
@pytest.mark.parametrize("case", sorted(_FAILED_RUNS))
def test_a_failed_bridge_verdict_scores_nan_not_its_partial_psf(tmp_path, case, mode):
    """SIM-D01: a fatal/partial run's partly-written numbers must not be scored as data."""
    verdict = _FAILED_RUNS[case]
    raw = tmp_path / "input.raw"
    raw.mkdir()
    bridge = _VerdictBridge(
        _VerdictResult(**verdict, data={"dc_vout": 0.61, "M0:gm": 1e-3}, output_dir=raw)
    )
    sim = SpectreSimulator(bridge, netlist=tmp_path / "tb.scs")

    res = _dispatch(sim, mode)

    assert np.isnan(res.scalar("vout", "dc")), "a failed run's PSF values were scored"
    assert np.isnan(res.scalar("M0:gm", "op"))
    with pytest.raises(KeyError):
        res.wave("vout", "dc")
    # nothing downstream (OCEAN measurements, waveview snapshots) may read the partial PSF
    assert res.raw_dir is None
    # the verdict itself travels with the result
    assert res.ok is False
    assert res.errors == verdict["errors"]
    assert res.returncode == verdict["returncode"]
    reported = getattr(verdict["status"], "value", verdict["status"])
    assert res.status == (
        reported if reported != "success" else f"failed (rc={verdict['returncode']})"
    )


@pytest.mark.parametrize("mode", ["run", "submit"])
def test_a_successful_bridge_verdict_keeps_its_data(tmp_path, mode):
    raw = tmp_path / "input.raw"
    raw.mkdir()
    bridge = _VerdictBridge(
        _VerdictResult(
            ok=True, status=_Status.SUCCESS, returncode=0, data={"dc_vout": 0.61}, output_dir=raw
        )
    )
    res = _dispatch(SpectreSimulator(bridge, netlist=tmp_path / "tb.scs"), mode)
    assert res.scalar("vout", "dc") == pytest.approx(0.61)
    assert res.raw_dir == str(raw)
    assert res.ok is True and res.returncode == 0 and res.status == "success"
    assert res.errors == []


def test_a_result_with_no_verdict_is_read_as_before(tmp_path):
    """A duck-typed result carrying neither `ok` nor a returncode (every offline fake above)
    has no verdict to give: its data is read as it always was, and its status says success
    (not an empty string a status check would misread)."""
    bridge = _VerdictBridge(type("R", (), {"data": {"dc_vout": 0.61}})())
    res = SpectreSimulator(bridge, netlist=tmp_path / "tb.scs").run()
    assert res.scalar("vout", "dc") == pytest.approx(0.61)
    assert (res.ok, res.status, res.errors, res.returncode) == (True, "success", [], None)
    assert res.raw_dir is None


def test_failed_spectre_runs_score_max_penalty_in_the_optimizer(tmp_path):
    """SIM-D01 end to end: the optimizer scores every spec of a FATAL run as -MAX_PENALTY,
    exactly as it does a failed ngspice run (no RAW -> NaN -> MAX_PENALTY, BUG-B28)."""
    from spicexplorer.optimization.base import MAX_PENALTY

    p, opt, bridge, spec_names = _spectre_optimizer(EXAMPLE_YAML, tmp_path, _FailingBridge)
    for parallel in (True, False):
        p.parallel_sim = parallel
        _score, fit_summary = opt.evaluate({"W1": 2.0, "L1": 1.0}, append_to_log=False)
        assert set(fit_summary) == set(spec_names), f"parallel={parallel}"
        for name, info in fit_summary.items():
            assert np.isnan(float(info["curr_val"])), (
                f"{name} scored a failed run (parallel={parallel})"
            )
            assert float(info["score"]) == -MAX_PENALTY
    assert bridge.calls


# ---------------------------------------------------------------------------
# SIM-D15 — a corner deck writes tnom next to temp (and passes decklint)
# ---------------------------------------------------------------------------

_NATIVE_SCS = """// native bench
simulator lang=spectre
global 0
parameters vdd=1.2 w1=1u
include "models.scs" section=tt
V1 (vdd 0) vsource dc=vdd
R1 (vdd 0) resistor r=1k
simulatorOptions options reltol=1e-4 gmin=1e-13
dcOp dc
"""


def _corner(**options):
    return Corner(
        name="ss_125C",
        model_includes=[ModelInclude(lib_file="models.scs", section="ss")],
        temp=125.0,
        options=dict(options),
    )


def _corner_sim(tmp_path, bridge, *, native_text=None, spec_overrides=None):
    """A deck-rendering adapter: composed from a spec, or over a native `.scs` bench."""
    if native_text is None:
        spec = SpectreDeckSpec(
            **{
                "title": "tb",
                "stimulus": "V1 (vdd 0) vsource dc=vdd\nR1 (vdd 0) resistor r=1k",
                "analyses": (dc_oppoint_analysis(),),
                "parameters": {"vdd": 1.2},
                **(spec_overrides or {}),
            }
        )
        return SpectreSimulator(bridge, deck_spec=spec, deck_dir=tmp_path / "runs")
    scs = tmp_path / "tb.scs"
    scs.write_text(native_text)
    return SpectreSimulator(bridge, native_scs=scs, deck_dir=tmp_path / "runs")


def _rendered_corner_deck(
    tmp_path, *, native_text=None, corner=None, bridge=None, spec_overrides=None
):
    """Drive the adapter as the optimizer does (apply_corner -> run) and return the deck
    text the bridge was handed."""
    bridge = bridge if bridge is not None else _FakeBridge([])
    sim = _corner_sim(tmp_path, bridge, native_text=native_text, spec_overrides=spec_overrides)
    sim.apply_corner(corner or _corner(), model_lib_root="/kit")
    sim.run(label="tb__ss_125C")
    return Path(bridge.calls[-1][0]).read_text()


@pytest.mark.parametrize("deck", ["composed", "native"])
def test_a_corner_deck_passes_the_lanes_decklint(tmp_path, deck):
    """SIM-D15: `temp` without `tnom` is decklint's `temp-without-tnom` finding."""
    decklint = pytest.importorskip("spicexplorer_spectre.decklint")
    text = _rendered_corner_deck(tmp_path, native_text=_NATIVE_SCS if deck == "native" else None)
    rules = [f.rule for f in decklint.lint_deck(text)]
    assert rules == [], f"{deck} corner deck: {rules}\n{text}"
    assert "tempOptions options temp=125 tnom=27" in text  # the tool default, now stated


def test_a_native_deck_that_pins_its_own_tnom_keeps_it(tmp_path):
    """A native bench that already states `tnom` is not overridden by the default."""
    own = _NATIVE_SCS.replace("reltol=1e-4", "reltol=1e-4 tnom=25")
    text = _rendered_corner_deck(tmp_path, native_text=own)
    assert "tempOptions options temp=125\n" in text
    assert text.count("tnom=") == 1 and "tnom=25" in text


# ---------------------------------------------------------------------------
# SIM-D01 edge cases — every field of the verdict, the warning, and the lane's rule
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("returncode", "ok"), [(0, True), (2, False), (-9, False)], ids=["rc0", "rc2", "rc-signal"]
)
def test_a_result_without_ok_is_judged_on_its_returncode(tmp_path, returncode, ok):
    """No `ok` attribute but a returncode: the returncode alone decides (the lane's rule)."""
    res = _VerdictResult(
        ok=True, status=_Status.SUCCESS, returncode=returncode, data={"dc_vout": 0.61}
    )
    del res.ok, res.status
    out = SpectreSimulator(_VerdictBridge(res), netlist=tmp_path / "tb.scs").run()
    assert out.ok is ok
    if ok:
        assert out.scalar("vout", "dc") == pytest.approx(0.61) and out.status == "success"
    else:
        assert np.isnan(out.scalar("vout", "dc"))
        assert out.status == f"failed (rc={returncode})"


def test_the_result_constructor_keeps_its_pre_verdict_defaults():
    """Every existing caller builds `SpectreSimResult(data, raw_dir=...)`: it must still read
    as a passing run with no verdict detail, and `errors` is always a list."""
    res = SpectreSimResult({"dc_vout": 0.5}, raw_dir="/runs/x.raw")
    assert (res.ok, res.status, res.errors, res.returncode) == (True, "", [], None)
    assert res.raw_dir == "/runs/x.raw" and res.scalar("vout", "dc") == 0.5
    assert SpectreSimResult(None, errors=("a", "b")).errors == ["a", "b"]


_SPECTRE_LOGGER = "spicexplorer.backends.spectre"


@pytest.mark.parametrize("mode", ["run", "submit"])
def test_a_failed_run_is_announced_once_with_its_label_verdict_and_raw_dir(tmp_path, caplog, mode):
    raw = tmp_path / "input.raw"  # NOT named for the label: the label must be in the message itself
    raw.mkdir()
    res = _VerdictResult(
        ok=False,
        status=_Status.PARTIAL,
        returncode=1,
        errors=["FATAL: convergence failure in tran"],
        data={"dc_vout": 0.61},
        output_dir=raw,
    )
    sim = SpectreSimulator(_VerdictBridge(res), netlist=tmp_path / "tb.scs")
    with caplog.at_level(logging.WARNING, logger=_SPECTRE_LOGGER):
        if mode == "run":
            sim.run(label="tb__ss_125C")
        else:
            handle = sim.submit(label="tb__ss_125C")
            first = handle.result()
            assert handle.result() is first  # the verdict is read once per run
    warned = [
        r for r in caplog.records if r.name == _SPECTRE_LOGGER and r.levelno == logging.WARNING
    ]
    assert len(warned) == 1, [r.getMessage() for r in warned]
    msg = warned[0].getMessage()
    for fragment in (
        "tb__ss_125C",
        "status=partial",
        "rc=1",
        "FATAL: convergence failure",
        str(raw),
    ):
        assert fragment in msg, (fragment, msg)


def test_a_failed_run_with_no_error_text_or_raw_dir_still_says_so(tmp_path, caplog):
    res = _VerdictResult(ok=True, status="success", returncode=3)
    with caplog.at_level(logging.WARNING, logger=_SPECTRE_LOGGER):
        SpectreSimulator(_VerdictBridge(res), netlist=tmp_path / "tb.scs").run()
    msg = " ".join(r.getMessage() for r in caplog.records if r.name == _SPECTRE_LOGGER)
    assert "failed (rc=3)" in msg and "no error text" in msg and "(no raw dir)" in msg


def test_a_successful_run_is_not_announced(tmp_path, caplog):
    res = _VerdictResult(ok=True, status=_Status.SUCCESS, returncode=0, data={"dc_vout": 0.61})
    with caplog.at_level(logging.WARNING, logger=_SPECTRE_LOGGER):
        SpectreSimulator(_VerdictBridge(res), netlist=tmp_path / "tb.scs").run(label="tb")
    assert not [r for r in caplog.records if r.name == _SPECTRE_LOGGER]


# The lane's `_finish` is the rule the adapter copies (Codex SPC-01). Every verdict shape the
# bridge can hand back must reach the SAME pass/fail and the same status wording in both lanes.
# (ok, status, returncode); `_ABSENT` builds a result without `ok`/`status` at all.
_ABSENT = object()
_VERDICT_GRID = {
    "ok-rc0": (True, _Status.SUCCESS, 0),
    "ok-no-rc": (True, "success", None),
    "partial-rc0": (False, _Status.PARTIAL, 0),
    "partial-rc1": (False, _Status.PARTIAL, 1),
    "error-no-rc": (False, _Status.ERROR, None),
    "blank-status-rc1": (False, "", 1),
    "not-ok-but-says-success": (False, _Status.SUCCESS, 0),
    "ok-rc139": (True, "success", 139),
    "ok-rc-signal": (True, "success", -11),
    "no-ok-rc0": (_ABSENT, None, 0),
    "no-ok-rc3": (_ABSENT, None, 3),
    # NOT here: no `ok` AND no returncode. The lane fails it; the adapter reads it as before
    # (the documented difference, `_verdict_of`) — `test_a_result_with_no_verdict_is_read_as_before`.
}


def _lane_status(tmp_path, res):
    """The lane's own status for bridge result `res`, through `_finish` as `simulate` calls it."""
    lane = pytest.importorskip("spicexplorer_spectre.lane")
    deck = tmp_path / "lane" / "tb.scs"
    deck.parent.mkdir()
    deck.write_text("simulator lang=spectre\n")
    status = getattr(res, "status", None)
    return lane._finish(
        deck,
        out=tmp_path / "lane" / "out",
        before={},
        data={},
        rc=(getattr(res, "metadata", None) or {}).get("returncode"),
        verdict=getattr(res, "ok", None),
        reported_status=str(getattr(status, "value", status) or ""),
        errors=list(getattr(res, "errors", None) or []),
    ).status


@pytest.mark.parametrize("case", sorted(_VERDICT_GRID))
def test_the_adapter_reaches_the_lanes_verdict(tmp_path, case):
    ok, status, rc = _VERDICT_GRID[case]
    res = _VerdictResult(
        ok=ok,
        status=status,
        returncode=rc,
        data={"dc_vout": 0.61},
        errors=[] if ok is True else ["boom"],
    )
    if ok is _ABSENT:
        del res.ok, res.status
    lane_status = _lane_status(tmp_path, res)

    ours = SpectreSimulator(_VerdictBridge(res), netlist=tmp_path / "tb.scs").run()

    assert ours.status == lane_status
    assert ours.ok is (lane_status == "success")
    assert bool(np.isnan(ours.scalar("vout", "dc"))) is (not ours.ok)


# ---------------------------------------------------------------------------
# SIM-D15 edge cases — where the tnom comes from, and what counts as the deck setting it
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("deck", ["composed", "native"])
@pytest.mark.parametrize(
    ("tnom", "written"),
    [(25.0, "tnom=25"), ("25", "tnom=25"), (0.0, "tnom=0"), (26.85, "tnom=26.85")],
    ids=["float", "yaml-string", "zero", "fraction"],
)
def test_the_corner_tnom_reaches_both_deck_kinds_and_the_bridge(tmp_path, deck, tnom, written):
    """`Corner.options["tnom"]` is written beside `temp` in a composed AND a native deck; a
    zero is a value, not "unset", and a YAML string is read as a number."""
    bridge = _FakeBridge([])
    text = _rendered_corner_deck(
        tmp_path,
        native_text=_NATIVE_SCS if deck == "native" else None,
        corner=_corner(tnom=tnom),
        bridge=bridge,
    )
    assert f"tempOptions options temp=125 {written}\n" in text
    assert text.count("tnom=") == 1
    assert bridge.calls[-1][1]["tnom"] == float(tnom)


@pytest.mark.parametrize("deck", ["composed", "native"])
def test_a_corner_without_tnom_does_not_inherit_the_previous_corners(tmp_path, deck):
    """`apply_corner` does not accumulate: the next corner replaces the last one's `tnom`, and a
    corner that names none falls back to `DEFAULT_TNOM`, not to the previous corner's value."""
    bridge = _FakeBridge([])
    sim = _corner_sim(tmp_path, bridge, native_text=_NATIVE_SCS if deck == "native" else None)
    decks = []
    for corner in (_corner(tnom=25.0), _corner(), _corner(tnom=30.0), _corner()):
        sim.apply_corner(corner, model_lib_root="/kit")
        sim.run(label="tb")
        decks.append(Path(bridge.calls[-1][0]).read_text())
    tails = [next(ln for ln in d.splitlines() if ln.startswith("tempOptions")) for d in decks]
    assert tails == [
        "tempOptions options temp=125 tnom=25",
        f"tempOptions options temp=125 tnom={DEFAULT_TNOM:g}",
        "tempOptions options temp=125 tnom=30",
        f"tempOptions options temp=125 tnom={DEFAULT_TNOM:g}",
    ]
    assert "tnom" not in sim.staged_params
    assert "tnom" not in bridge.calls[-1][1]


@pytest.mark.parametrize(
    ("native_text", "spec_overrides"),
    [
        (_NATIVE_SCS.replace("reltol=1e-4", "reltol=1e-4 tnom=25"), None),
        (None, {"simulator_options": DEFAULT_SIMULATOR_OPTIONS + " tnom=25"}),
        # extra_lines are written after the analyses: the corner's line must still come after them
        (None, {"extra_lines": ("nomOptions options tnom=25",)}),
    ],
    ids=["native", "composed-simulator_options", "composed-extra_lines"],
)
def test_a_corner_tnom_is_written_even_over_the_decks_own(tmp_path, native_text, spec_overrides):
    """The deck's own `tnom` only stops the DEFAULT; an explicit corner value is always written
    — last, so it is the one Spectre applies."""
    text = _rendered_corner_deck(
        tmp_path,
        native_text=native_text,
        corner=_corner(tnom=30.0),
        spec_overrides=spec_overrides,
    )
    lines = text.splitlines()
    temp_line = next(i for i, ln in enumerate(lines) if ln.startswith("tempOptions"))
    own_line = next(i for i, ln in enumerate(lines) if "tnom=25" in ln)
    assert lines[temp_line] == "tempOptions options temp=125 tnom=30"
    assert own_line < temp_line


@pytest.mark.parametrize(
    "spec_overrides",
    [
        {"simulator_options": DEFAULT_SIMULATOR_OPTIONS + " tnom=25"},
        {"extra_lines": ("nomOptions options tnom=25",)},
    ],
    ids=["simulator_options", "extra_lines"],
)
def test_a_composed_deck_that_pins_its_own_tnom_keeps_it(tmp_path, spec_overrides):
    """The composed twin of the native case: the spec's own options (wherever the spec puts
    them) already state `tnom`, so the default is not written over it."""
    text = _rendered_corner_deck(tmp_path, spec_overrides=spec_overrides)
    assert "tempOptions options temp=125\n" in text
    assert text.count("tnom=") == 1 and "tnom=25" in text


# Native benches whose text MENTIONS tnom without setting it deck-wide (or sets it across a
# continuation). Whatever the adapter decides, decklint must agree with it.
_TNOM_LOOKALIKES = {
    # a `//` comment is not a statement
    "trailing-comment": (
        _NATIVE_SCS.replace("reltol=1e-4", "reltol=1e-4 // tnom=25 was the old default"),
        True,
    ),
    # a model card's own tnom governs that model only; the deck-wide default is still unset
    "model-card": (
        _NATIVE_SCS.replace("dcOp dc", "model nfet bsim4 type=n tnom=25\ndcOp dc"),
        True,
    ),
    # an option whose NAME merely ends in tnom is not tnom
    "lookalike-name": (_NATIVE_SCS.replace("reltol=1e-4", "reltol=1e-4 dtnom=1"), True),
    # a `\` continuation is one statement: the tnom on the next physical line IS the deck's setting
    "continued-options": (_NATIVE_SCS.replace("gmin=1e-13", "gmin=1e-13 \\\n    tnom=25"), False),
}


@pytest.mark.parametrize("case", sorted(_TNOM_LOOKALIKES))
def test_only_a_deck_wide_tnom_option_counts_as_the_decks_own(tmp_path, case):
    native, default_written = _TNOM_LOOKALIKES[case]
    text = _rendered_corner_deck(tmp_path, native_text=native)
    temp_line = next(ln for ln in text.splitlines() if ln.startswith("tempOptions"))
    expected = (
        f"tempOptions options temp=125 tnom={DEFAULT_TNOM:g}"
        if default_written
        else ("tempOptions options temp=125")
    )
    assert temp_line == expected, text
    decklint = pytest.importorskip("spicexplorer_spectre.decklint")
    assert [f.rule for f in decklint.lint_deck(text)] == [], text


def test_tnom_rides_with_temp_and_a_deck_without_a_corner_is_unchanged():
    """No `temp` → no `tempOptions` statement at all, whatever `tnom` says: a fixed-temperature
    deck renders exactly as it did before corners wrote `tnom`."""
    spec = SpectreDeckSpec(title="tb", stimulus="V1 (vdd 0) vsource dc=1")
    for text in (
        render_spectre_deck(spec, tnom=25.0),
        render_native_scs(_NATIVE_SCS, tnom=25.0),
    ):
        assert "tempOptions" not in text and "tnom" not in text
    assert render_spectre_deck(spec, tnom=25.0) == render_spectre_deck(spec)
    assert render_native_scs(_NATIVE_SCS, tnom=25.0) == render_native_scs(_NATIVE_SCS)
