"""Tests for the multi-corner PVT system.

Layers mirror test_pvt_corner.py:

  • Layer 1 (no ngspice, no PDK): the `mode:` / `score_aggregation:` knobs parse,
    normalize their aliases, and validate (symmetric corners, enabled-corner
    presence, checkpoint-safe names); `aggregate_corner_scores` math; the new
    `.temp`-card strip in `apply_corner` (a hardcoded `.temp 27` used to override
    the injected `.options temp=` silently, pinning every corner to 27°C).
  • Layer 2 (@requires_ngspice, no sim): the multi-corner evaluate loop applies
    every enabled corner per evaluation, namespaces fit_summary as
    "<corner>::<spec>", records per-corner scores in the log metadata, and
    aggregates via the configured strategy — asserted with the SPICE run and
    metric extraction stubbed out.
  • Layer 3 (@requires_ngspice @requires_pdk @slow): one real optimization_step on
    the folded_cascode example (mode: multi, 2 enabled corners x 1 AC testbench).
"""
import json
import re
from pathlib import Path

import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT, requires_ngspice, requires_pdk, slow
from spicexplorer.core.domains import Corner, Project_Setup, PVTConfig
from spicexplorer.core.utils import aggregate_corner_scores
from spicexplorer_core.pvt import (
    ModelInclude,
    SupplyOverride,
    _normalize_pvt_block,
    normalize_score_aggregation,
)

FC_YAML = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"
FC_AC_NETLIST = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/spice/cora_testbench_ac.spice"
# This 5t-ota testbench hardcodes a `.temp 27` card — the exact shape that used to
# defeat apply_corner's `.options temp=` injection (ngspice gives `.temp` precedence).
OTA5T_TB_NETLIST = REPO_ROOT / "examples/OTA/5t-ota/ihp-sg13g2/spice/ota-5t_tb-tran.spice"


def _corner(name, enabled=True, libs=("cornerMOSlv.lib",), nodes=("VDD",), params=()):
    return Corner(
        name=name,
        enabled=enabled,
        model_includes=[ModelInclude(lib_file=lf, section="sec") for lf in libs],
        supplies=[SupplyOverride(node=n, value=1.5) for n in nodes],
        params={k: 1.0 for k in params},
    )


# ── config parsing / validation (Layer 1) ───────────────────────────────────

def test_fc_yaml_parses_multi_corner_config():
    p = Project_Setup.from_yaml(FC_YAML)
    assert p.pvt is not None
    assert p.pvt.mode == "multi"
    assert p.pvt.is_multi()
    assert p.pvt.score_aggregation == "mean"
    assert [c.name for c in p.pvt.corners_to_run()] == ["tt_27C_1V8", "ss_125C_1V62"]


def test_mode_defaults_to_single_and_runs_active_corner():
    cfg = PVTConfig(active_corner="tt", corners=[_corner("tt"), _corner("ss")])
    assert cfg.mode == "single"
    assert not cfg.is_multi()
    # single mode runs exactly the active corner, even with several enabled
    assert [c.name for c in cfg.corners_to_run()] == ["tt"]


def test_score_aggregation_aliases_normalize():
    for alias, canonical in [("add", "sum"), ("total", "sum"), ("average", "mean"),
                             ("avg", "mean"), ("Worst_Case", "min"), ("worst", "min"),
                             ("MIN", "min"), ("sum", "sum"), ("mean", "mean")]:
        cfg = PVTConfig(active_corner="tt", corners=[_corner("tt")],
                        score_aggregation=alias)
        assert cfg.score_aggregation == canonical, alias
    with pytest.raises(ValueError, match="score_aggregation"):
        normalize_score_aggregation("median")


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="pvt.mode"):
        PVTConfig(active_corner="tt", corners=[_corner("tt")], mode="dual")


def test_multi_mode_requires_an_enabled_corner():
    with pytest.raises(ValueError, match="no corner is enabled"):
        PVTConfig(active_corner="tt", corners=[_corner("tt", enabled=False)], mode="multi")


def test_multi_mode_rejects_asymmetric_corners():
    # corner 'b' overrides an extra supply rail that 'a' does not touch — its value
    # would silently leak into 'a's runs when corners are re-applied per trial.
    with pytest.raises(ValueError, match="SYMMETRIC"):
        PVTConfig(
            active_corner="a",
            corners=[_corner("a"), _corner("b", nodes=("VDD", "VDDH"))],
            mode="multi",
        )
    # same for extra `.param` overrides…
    with pytest.raises(ValueError, match="SYMMETRIC"):
        PVTConfig(
            active_corner="a",
            corners=[_corner("a", params=("ibias",)), _corner("b")],
            mode="multi",
        )
    # …and for the set of model library files
    with pytest.raises(ValueError, match="SYMMETRIC"):
        PVTConfig(
            active_corner="a",
            corners=[_corner("a", libs=("cornerMOSlv.lib", "cornerRES.lib")), _corner("b")],
            mode="multi",
        )


def test_multi_mode_rejects_checkpoint_hostile_corner_names():
    # '.' breaks the pandas dotted-column flattening; '::' breaks the key split.
    for bad in ("tt_27.5C", "tt::hot"):
        with pytest.raises(ValueError, match="corrupt"):
            PVTConfig(active_corner=bad, corners=[_corner(bad)], mode="multi")
    # single mode keeps accepting legacy names (no new load failures for Phase-1 YAMLs)
    PVTConfig(active_corner="tt_27.5C", corners=[_corner("tt_27.5C")])


def test_multi_mode_validates_active_corner_at_load(recwarn):
    # active_corner is used by manual sims / the multi->single collapse even in multi
    # mode, so an undefined one must fail at load, not lurk until a manual sim (CFG-1).
    with pytest.raises(ValueError, match="active_corner"):
        PVTConfig(active_corner="ghost", corners=[_corner("tt")], mode="multi")
    # a defined active_corner is fine
    PVTConfig(active_corner="tt", corners=[_corner("tt"), _corner("ss")], mode="multi")


def test_corner_rejects_both_singular_and_plural_supply():
    # Both `supply:` (sugar) and `supplies:` (canonical) on one corner is ambiguous —
    # the old normalizer silently dropped the singular. Now it raises (CFG-1), mirroring
    # the process/model_includes guard.
    proj = {"pvt": {"active_corner": "tt", "corners": [{
        "name": "tt",
        "model_includes": [{"lib_file": "cornerMOSlv.lib", "section": "mos_tt"}],
        "supply": {"node": "VDD", "value": 1.5},
        "supplies": [{"node": "VDD", "value": 1.5}],
    }]}}
    with pytest.raises(ValueError, match="BOTH a singular 'supply' and a plural"):
        _normalize_pvt_block(proj)
    # only the singular sugar still widens cleanly to supplies: [...]
    proj_ok = {"pvt": {"active_corner": "tt", "corners": [{
        "name": "tt",
        "model_includes": [{"lib_file": "cornerMOSlv.lib", "section": "mos_tt"}],
        "supply": {"node": "VDD", "value": 1.5},
    }]}}
    _normalize_pvt_block(proj_ok)
    assert proj_ok["pvt"]["corners"][0]["supplies"] == [{"node": "VDD", "value": 1.5}]


def test_aggregate_corner_scores_math():
    # Constraint-first: a corner total < 0 fails; >= 0 passes. If ANY corner
    # fails, only the failing corners' penalties aggregate — a passing corner's positive
    # reward can never mask a failure. Only when ALL pass do rewards aggregate.

    # ONE failing corner: every strategy collapses to that corner's penalty (the good
    # corners' +10 / +3 are discarded, so mean/sum can't out-vote the -4 failure).
    one_fail = {"tt": np.float64(10.0), "ss": np.float64(-4.0), "ff": np.float64(3.0)}
    assert aggregate_corner_scores(one_fail, "sum") == pytest.approx(-4.0)
    assert aggregate_corner_scores(one_fail, "mean") == pytest.approx(-4.0)
    assert aggregate_corner_scores(one_fail, "min") == pytest.approx(-4.0)

    # MULTIPLE failing corners: aggregate ONLY the penalties (ignore the passing +10).
    two_fail = {"tt": np.float64(10.0), "ss": np.float64(-4.0), "ff": np.float64(-6.0)}
    assert aggregate_corner_scores(two_fail, "sum") == pytest.approx(-10.0)
    assert aggregate_corner_scores(two_fail, "mean") == pytest.approx(-5.0)
    assert aggregate_corner_scores(two_fail, "min") == pytest.approx(-6.0)

    # ALL corners pass: aggregate the (positive) rewards exactly as before.
    all_pass = {"tt": np.float64(10.0), "ss": np.float64(2.0), "ff": np.float64(3.0)}
    assert aggregate_corner_scores(all_pass, "sum") == pytest.approx(15.0)
    assert aggregate_corner_scores(all_pass, "mean") == pytest.approx(5.0)
    assert aggregate_corner_scores(all_pass, "min") == pytest.approx(2.0)

    with pytest.raises(ValueError):
        aggregate_corner_scores({}, "mean")
    with pytest.raises(ValueError):
        aggregate_corner_scores(one_fail, "median")


# ── apply_corner `.temp` card strip (Layer 1, no simulation) ─────────────────

def _joined(wrapper) -> str:
    return "\n".join(ln for ln in wrapper.editor.netlist if isinstance(ln, str))


@pytest.mark.skipif(not OTA5T_TB_NETLIST.exists(), reason="5t-ota testbench netlist missing")
def test_apply_corner_strips_hardcoded_temp_card(tmp_path):
    from spicexplorer_core.spice_engine.spicelib import NGSpice_Wrapper

    w = NGSpice_Wrapper(
        netlist_filename=OTA5T_TB_NETLIST,
        testbench_name="ota5t_tb",
        output_folder=tmp_path / "temp_strip_out",
    )
    # sanity: the shipped netlist really carries the hazard
    assert re.search(r"^\s*\.temp\s+27", _joined(w), re.MULTILINE | re.IGNORECASE)

    hot = Corner(name="hot", temp=125.0)
    w.apply_corner(hot)
    joined = _joined(w)

    # the `.temp` card is gone (it would override `.options temp=` in ngspice)…
    assert not re.search(r"^\s*\.temp\s+", joined, re.MULTILINE | re.IGNORECASE)
    # …and the corner's authoritative temperature directive is in place
    assert re.search(r"\.options?\s+temp\s*=\s*125", joined)

    # re-apply stays idempotent: exactly one injected temp option line
    w.apply_corner(hot)
    joined = _joined(w)
    assert len(re.findall(r"\.options?\s+temp\s*=", joined)) == 1


@pytest.mark.skipif(not FC_AC_NETLIST.exists(), reason="folded_cascode AC netlist missing")
def test_failed_sim_degrades_to_no_raw_instead_of_raising(tmp_path):
    """A hard ngspice failure leaves the task's raw_file as None (or a path that was
    never written). load_task_outputs must degrade to curr_raw=None — the documented
    NaN → MAX_PENALTY scoring path — instead of raising out of RawRead and killing
    the whole optimization run. Under multi-corner this is load-bearing: worst-case
    corners are simulated every trial, so one non-convergent corner must cost that
    corner MAX_PENALTY, not the entire run."""
    from spicexplorer_core.spice_engine.spicelib import Ngspice_Plot_Type, NGSpice_Wrapper

    w = NGSpice_Wrapper(
        netlist_filename=FC_AC_NETLIST,
        testbench_name="tb_fail",
        output_folder=tmp_path / "fail_out",
    )

    # hard failure: no raw file at all
    w.tasks_outputs["t_none"] = (None, tmp_path / "run.fail")
    w.load_task_outputs("t_none")
    assert w.curr_raw is None
    assert w.curr_log == tmp_path / "run.fail"

    # soft failure: a raw path that was never written
    w.tasks_outputs["t_missing"] = (tmp_path / "never_written.raw", tmp_path / "run2.log")
    w.load_task_outputs("t_missing")
    assert w.curr_raw is None
    assert w.curr_log == tmp_path / "run2.log"

    # the NaN degradation the scorer documents actually engages
    out = w.extract_scalar_variable_from_raw("dcgain", plot_type=Ngspice_Plot_Type.AC)
    assert np.isnan(out["dcgain"])


# ── multi-corner evaluate loop (Layer 2 — optimizer built, SPICE stubbed) ────

class _FakeSimResult:
    """Minimal `SimResult` stand-in (the protocol is structural): every scalar reads
    the canned value. No `log_path` attribute — mirroring a stubbed sim that wrote no
    log — so `evaluate`'s log harvesting sees nothing, exactly like the old stubs."""

    def __init__(self, value: float):
        self._value = float(value)

    def scalar(self, name, analysis):
        return self._value

    def wave(self, name, analysis):
        raise KeyError(name)


def _make_fc_optimizer(tmp_path):
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective
    from spicexplorer_core.spice_engine.spicelib import NGSpice_Wrapper

    p = Project_Setup.from_yaml(FC_YAML)
    p.parallel_sim = False
    wrappers = {}
    for tb in p.testbenches:
        if not tb.enable:
            continue
        wrappers[tb.name] = NGSpice_Wrapper(
            testbench_name=tb.name,
            netlist_filename=Path(p.ws_root) / Path(tb.netlist),
            output_folder=tmp_path / f"out_{tb.name}",
        )
    opt = Nevergrad_Spice_Single_Objective(setup_obj=p, spicelib_wrappers=wrappers)
    return p, opt


@requires_ngspice
def test_resolve_fit_summary_key_defaults_to_worst_corner(tmp_path):
    """A bare spec name resolves to the WORST corner (lowest mean per-spec
    score), not the first-enumerated (easy `tt`) corner."""
    from spicexplorer.core.domains import OptimizationLogEntry, OptimizationPoint
    p, opt = _make_fc_optimizer(tmp_path)

    def _entry(tt_score, ss_score):
        return OptimizationLogEntry(
            point=OptimizationPoint(params={}, score=np.float64(0.0)),
            fit_summary={
                "tt_27C_1V8::dcgain":   {"curr_val": 50.0, "score": np.float64(tt_score)},
                "ss_125C_1V62::dcgain": {"curr_val": 20.0, "score": np.float64(ss_score)},
            },
        )

    # tt does well on dcgain (mean +1.5); ss does badly (mean -4.0) -> ss is worst.
    opt.optimization_log = [_entry(1.0, -5.0), _entry(2.0, -3.0)]
    assert opt._resolve_fit_summary_key("dcgain") == "ss_125C_1V62::dcgain"
    # an explicit "<corner>::spec" key is honored as-is (override the worst-corner default)
    assert opt._resolve_fit_summary_key("tt_27C_1V8::dcgain") == "tt_27C_1V8::dcgain"
    # a spec absent from the log resolves to None
    assert opt._resolve_fit_summary_key("nonexistent") is None


@requires_ngspice
@pytest.mark.skipif(not FC_AC_NETLIST.exists(), reason="folded_cascode AC netlist missing")
def test_multi_corner_evaluate_loops_and_aggregates(tmp_path, monkeypatch):
    p, opt = _make_fc_optimizer(tmp_path)
    corners = [c.name for c in p.pvt.corners_to_run()]
    tbs = list(opt.spicelib_wrappers)
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]
    assert len(corners) == 2 and tbs and spec_names

    # The real apply_corner still runs un-stubbed inside evaluate (so re-applying
    # different corners back-to-back on the same editor must stay legal); only the
    # simulation itself is stubbed — at the engine-neutral `simulate_circuit` seam,
    # which now returns per-testbench `SimResult`s. The sequential multi loop passes
    # the corner name as `run_label`, so the canned per-corner metric keys off it.
    run_labels = []

    # Canned per-corner metrics: the tt corner performs 2x better than ss on every
    # spec, so the two corner scores must differ.
    CANNED = {"tt_27C_1V8": 2.0, "ss_125C_1V62": 1.0}

    def fake_simulate(parameterization, run_label=None):
        run_labels.append(run_label)
        # the sequential multi loop must label every pass with its corner name
        assert run_label is not None
        return {tb: _FakeSimResult(CANNED[run_label]) for tb in tbs}

    monkeypatch.setattr(opt, "simulate_circuit", fake_simulate)

    score, fit_summary = opt.evaluate({"x": 1.0})

    # every enabled corner ran, in order, each labeling its own run folders
    assert run_labels == corners
    # fit_summary is fully corner-namespaced: {<corner>::<spec>} for every pair
    assert set(fit_summary) == {f"{c}::{s}" for c in corners for s in spec_names}
    for info in fit_summary.values():
        assert set(info) == {"curr_val", "score"}

    # per-corner totals ride in the log metadata and aggregate per the config (mean)
    entry = opt.optimization_log[-1]
    meta = entry.point.metadata
    assert meta["score_aggregation"] == "mean"
    assert set(meta["corner_scores"]) == set(corners)
    expected = {
        c: opt.compute_fitness({s: np.float64(CANNED[c]) for s in spec_names})[0]
        for c in corners
    }
    for c in corners:
        assert meta["corner_scores"][c] == pytest.approx(float(expected[c]))
    # score is the constraint-first aggregation of the per-corner totals (both corners
    # fail these unsized specs, so the penalty-subset == the full set here).
    assert score == pytest.approx(
        float(aggregate_corner_scores({c: np.float64(expected[c]) for c in corners}, "mean"))
    )

    # the two corners genuinely scored differently (the loop isn't re-running one corner)
    vals = list(meta["corner_scores"].values())
    assert vals[0] != vals[1]

    # per-corner log files would be keyed "<tb>__<corner>" (none exist here — stubbed
    # sims never write logs — so the dict is simply empty, not single-corner-shaped)
    assert entry.log_file == {}

    # switching the strategy changes only the collapse, not the per-corner scores
    p.pvt.score_aggregation = "min"
    score_min, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
    assert score_min == pytest.approx(float(min(expected.values())))
    p.pvt.score_aggregation = "sum"
    score_sum, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
    assert score_sum == pytest.approx(float(sum(expected.values())))


@requires_ngspice
@pytest.mark.skipif(not FC_AC_NETLIST.exists(), reason="folded_cascode AC netlist missing")
def test_multi_corner_parallel_corner_fanout(tmp_path, monkeypatch):
    """Corner-axis parallelism (parallel_sim=True): the multi-corner evaluate must
    LAUNCH every (corner × testbench) sim before waiting, then collect each corner's
    own results — yielding per-corner scores + aggregation identical to the
    sequential path, with no cross-corner contamination. SPICE is stubbed at the
    run_and_pass / collect seams so the fan-out logic is asserted directly."""
    from spicexplorer_core.spice_engine.spicelib import NGSpice_Wrapper

    p, opt = _make_fc_optimizer(tmp_path)
    p.parallel_sim = True  # exercise the parallel corner-fan-out path
    corners = [c.name for c in p.pvt.corners_to_run()]
    tbs = list(opt.spicelib_wrappers)
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]
    assert len(corners) == 2 and tbs and spec_names

    # A fake task carrying its "<tb>__<corner>" label; already finished (is_alive False).
    # submit() wraps it in a real NgspiceSimHandle, whose is_done() consults is_alive().
    class _FakeTask:
        def __init__(self, label):
            self.name = label
            self.label = label

        def is_alive(self):
            return False

    launched = []
    read_order = []

    def fake_run_and_pass(self, exe_log=True, label=None):
        launched.append(label)
        return _FakeTask(label)

    def fake_update_params(self, parameterization):
        return True

    # tt performs 2x better than ss on every spec -> the two corner scores must differ.
    CANNED = {"tt_27C_1V8": 2.0, "ss_125C_1V62": 1.0}

    def fake_collect(self, handle):
        # Record which (tb, corner) run is being read back; return that corner's
        # canned metrics as a self-contained result (real collect parses that
        # run's own RAW — distinct per corner).
        label = handle.task.label
        read_order.append(label)
        return _FakeSimResult(CANNED[label.split("__", 1)[1]])

    monkeypatch.setattr(NGSpice_Wrapper, "run_and_pass", fake_run_and_pass)
    monkeypatch.setattr(NGSpice_Wrapper, "update_params", fake_update_params)
    monkeypatch.setattr(NGSpice_Wrapper, "collect", fake_collect)

    score, fit_summary = opt.evaluate({"x": 1.0})

    # (1) EVERY (corner × testbench) sim was launched, as the full cross-product; the
    #     two-phase structure guarantees all launches precede all reads (fan-out, not
    #     serialized per corner).
    assert launched == [f"{tb}__{c}" for c in corners for tb in tbs]
    assert len(launched) == len(corners) * len(tbs)
    assert set(read_order) == {f"{tb}__{c}" for c in corners for tb in tbs}

    # (2) fit_summary is fully corner-namespaced and per-corner scores match the
    #     sequential expectation exactly (each corner scored on its OWN outputs).
    assert set(fit_summary) == {f"{c}::{s}" for c in corners for s in spec_names}
    entry = opt.optimization_log[-1]
    meta = entry.point.metadata
    expected = {
        c: opt.compute_fitness({s: np.float64(CANNED[c]) for s in spec_names})[0]
        for c in corners
    }
    for c in corners:
        assert meta["corner_scores"][c] == pytest.approx(float(expected[c]))
    assert meta["corner_scores"]["tt_27C_1V8"] != meta["corner_scores"]["ss_125C_1V62"]

    # (3) aggregation collapses per config (mean) — identical to the sequential loop.
    assert meta["score_aggregation"] == "mean"
    assert score == pytest.approx(float(np.mean(list(expected.values()))))


@requires_ngspice
@pytest.mark.skipif(not FC_AC_NETLIST.exists(), reason="folded_cascode AC netlist missing")
def test_single_mode_fit_summary_stays_bare_keyed(tmp_path, monkeypatch):
    """Regression: with mode switched back to single, evaluate must keep the
    legacy shape — bare spec keys, no corner metadata."""
    p, opt = _make_fc_optimizer(tmp_path)
    p.pvt.mode = "single"
    tbs = list(opt.spicelib_wrappers)
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]

    monkeypatch.setattr(
        opt, "simulate_circuit",
        lambda parameterization, run_label=None: {tb: _FakeSimResult(1.0) for tb in tbs},
    )

    score, fit_summary = opt.evaluate({"x": 1.0})
    assert set(fit_summary) == set(spec_names)
    assert opt.optimization_log[-1].point.metadata == {}


@requires_ngspice
@pytest.mark.skipif(not FC_AC_NETLIST.exists(), reason="folded_cascode AC netlist missing")
def test_multi_corner_checkpoint_carries_namespaced_keys(tmp_path, monkeypatch):
    p, opt = _make_fc_optimizer(tmp_path)
    corners = [c.name for c in p.pvt.corners_to_run()]
    tbs = list(opt.spicelib_wrappers)

    monkeypatch.setattr(
        opt, "simulate_circuit",
        lambda parameterization, run_label=None: {tb: _FakeSimResult(1.0) for tb in tbs},
    )

    opt.evaluate({"x": 1.0})
    opt.save_checkpoint(tmp_path / "mc_ckpt")

    saved = list(tmp_path.glob("mc_ckpt_*.json"))
    assert len(saved) == 1
    data = json.loads(saved[0].read_text())
    entry = data["optimization_log"][0]
    assert set(entry["point"]["metadata"]["corner_scores"]) == set(corners)
    assert entry["point"]["metadata"]["score_aggregation"] == "mean"
    assert all("::" in k for k in entry["fit_summary"])


# ── live multi-corner step (Layer 3 — real ngspice + IHP PDK) ────────────────

@requires_ngspice
@requires_pdk
@slow
def test_multi_corner_live_optimization_step(tmp_path):
    """One real trial on the folded_cascode example: 2 enabled corners x 1 enabled
    AC testbench = 2 ngspice runs, scored per corner and mean-aggregated."""
    p, opt = _make_fc_optimizer(tmp_path)
    corners = [c.name for c in p.pvt.corners_to_run()]
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]

    opt.parameterize()
    assert opt._create_optimizer_obj()
    params, score, fit_summary = opt.optimization_step()

    assert np.isfinite(score)
    assert set(fit_summary) == {f"{c}::{s}" for c in corners for s in spec_names}

    entry = opt.optimization_log[-1]
    corner_scores = entry.point.metadata["corner_scores"]
    assert set(corner_scores) == set(corners)
    # score is the constraint-first aggregation of the per-corner totals (robust to
    # whichever corners pass/fail for this random point — not hardcoded np.mean).
    assert score == pytest.approx(
        float(aggregate_corner_scores(corner_scores, "mean")), rel=1e-9)
    # every (tb, corner) sim produced its own log, keyed "<tb>__<corner>"
    assert set(entry.log_file) == {f"tb_ac__{c}" for c in corners}

    # The corners must have ACTUALLY driven the sims: tt(27°C, 1.8V, mos_tt) vs
    # ss(125°C, 1.62V, mos_ss) cannot produce identical deterministic results.
    # Guard against the silent-no-op class this feature fixed (`.temp` cards
    # pinning every corner to 27°C): dcgain is finite at both corners and must
    # differ, and so must the per-corner totals.
    dcgain = {c: float(fit_summary[f"{c}::dcgain"]["curr_val"]) for c in corners}
    assert all(np.isfinite(v) for v in dcgain.values()), dcgain
    vals = list(dcgain.values())
    assert vals[0] != pytest.approx(vals[1], rel=1e-6), (
        f"identical dcgain across corners — corner application was a no-op? {dcgain}")
    cs = list(corner_scores.values())
    assert cs[0] != pytest.approx(cs[1], rel=1e-9), corner_scores


@requires_ngspice
@requires_pdk
@slow
def test_multi_corner_parallel_matches_sequential_live(tmp_path):
    """Live equivalence: the corner-PARALLEL path (parallel_sim=True, the shipped
    default) must produce the SAME per-corner metrics and aggregate score as the
    sequential path for one fixed candidate on folded_cascode. ngspice is
    deterministic, so any drift would mean the fan-out mixed corners' RAWs."""
    p, opt = _make_fc_optimizer(tmp_path)   # _make_fc_optimizer forces parallel_sim=False
    corners = [c.name for c in p.pvt.corners_to_run()]
    spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]

    # A fixed, deterministic candidate: the resolved min/max midpoint of every
    # dut_param (always in-range, and independent of whether init/val are set).
    # evaluate takes denormalized engineering-real values directly (no ask/denormalize).
    p.resolve_all_parameter_ranges()
    params = {
        dp.name: (float(dp.min_val) + float(dp.max_val)) / 2.0
        for dp in p.dut_params
        if dp.min_val is not None and dp.max_val is not None
    }
    assert params, "no dut_params to build a candidate from"

    # Sequential reference.
    p.parallel_sim = False
    score_seq, fit_seq = opt.evaluate(params, append_to_log=False)

    # Parallel (the default production path).
    p.parallel_sim = True
    score_par, fit_par = opt.evaluate(params, append_to_log=False)

    assert set(fit_par) == set(fit_seq) == {f"{c}::{s}" for c in corners for s in spec_names}
    for key in fit_seq:
        v_seq, v_par = fit_seq[key]["curr_val"], fit_par[key]["curr_val"]
        if np.isnan(float(v_seq)) or np.isnan(float(v_par)):
            assert np.isnan(float(v_seq)) and np.isnan(float(v_par)), (key, v_seq, v_par)
        else:
            assert float(v_par) == pytest.approx(float(v_seq), rel=1e-9), (key, v_seq, v_par)
        assert float(fit_par[key]["score"]) == pytest.approx(float(fit_seq[key]["score"]), rel=1e-9)
    assert float(score_par) == pytest.approx(float(score_seq), rel=1e-9)
