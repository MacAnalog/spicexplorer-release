"""Corner-robust scoring: `pvt.score_aggregation: worst_spec` and `unmeasured_policy`.

Two opt-in surfaces, both defaulting to today's behaviour, both motivated by the same measured
finding (TCAS-2026 ledger E-057, cross-mining E-058):

1. **Optimizing at one corner produces corner-fragile designs.** 246 designs feasible at `tt`
   alone were re-simulated at all five MOS corners; only 98 passed everywhere. The existing
   corner strategies (`sum`/`mean`/`min`) collapse each corner's already-aggregated TOTAL, so one
   spec's failure at `ss` is averaged into `ss`'s total before it is ever compared with `tt`'s.
   `worst_spec` composes the other way round — worst corner PER SPEC, then ONE spec aggregation —
   which is the only ordering under which "this design is feasible" means "feasible at EVERY
   enabled corner".
2. **A spec that could not be measured must be a failure, not a silent pass.** The score path
   already fails closed (pinned below, deliberately, as the characterization this feature was
   scoped against). What did NOT exist is any way for anything downstream to tell a *crashed*
   trial apart from a *converged-but-terrible* one — both floor at `-MAX_PENALTY`, and the API's
   checkpoint reader re-derives feasibility from values rather than reading a recorded verdict.
   `unmeasured_policy: fail` records it.

Layer 1 is pure (no SPICE, no PDK, no ngspice binary): the reducers, the vocabulary, the config.
Layer 2 drives the REAL `evaluate()` with a fake `Simulator` and canned per-corner readings, so the
wiring — which corner binds, what lands in the metadata, what the default path does — is asserted
end to end without a simulator. There is no Layer 3: wiring a live ngspice multi-corner run buys
nothing these stubs do not already pin, and the existing `test_pvt_multi_corner.py` Layer 3 already
covers the multi-corner sim path itself.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT
from spicexplorer.core.domains import (
    Corner,
    OptimizerConfig,
    Project_Setup,
    PVTConfig,
    TargetSpec,
)
from spicexplorer.core.utils import (
    DEFAULT_UNMEASURED_POLICY,
    EPSILON,
    PER_SPEC_CORNER_AGGREGATION,
    UNMEASURED_POLICIES,
    aggregate_corner_scores,
    aggregate_corner_spec_margins,
    aggregate_corner_spec_scores,
    resolve_unmeasured_policy,
)
from spicexplorer.optimization.base import MAX_PENALTY, Spice_Single_Objective
from spicexplorer_core.pvt import (
    SCORE_AGGREGATION_STRATEGIES,
    ModelInclude,
    SupplyOverride,
    normalize_score_aggregation,
)

F = np.float64
CASCODE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"
requires_cascode = pytest.mark.skipif(not CASCODE_YAML.exists(),
                                      reason="cascode example project missing")


# ======================================================= 1. the per-spec corner reducer (pure)
def test_each_spec_keeps_its_own_worst_corner():
    """The whole point: the binding corner is decided PER SPEC. `gain` is worst at `ss`, `power`
    at `ff` — a totals reducer has to pick one corner for both."""
    per_corner = {
        "tt": {"gain": F(1.0), "power": F(1.0)},
        "ss": {"gain": F(-3.0), "power": F(2.0)},
        "ff": {"gain": F(0.5), "power": F(-4.0)},
    }
    worst, binding = aggregate_corner_spec_scores(per_corner)
    assert worst == {"gain": F(-3.0), "power": F(-4.0)}
    assert binding == {"gain": "ss", "power": "ff"}


def test_the_first_corner_wins_a_tie_so_the_reduction_is_deterministic():
    worst, binding = aggregate_corner_spec_scores(
        {"tt": {"g": F(1.0)}, "ss": {"g": F(1.0)}})
    assert worst["g"] == F(1.0) and binding["g"] == "tt"


def test_a_spec_missing_from_one_corner_still_resolves_from_the_others():
    """A corner that was not simulated for a spec (a resume-added corner) must not delete it."""
    worst, binding = aggregate_corner_spec_scores(
        {"tt": {"a": F(2.0), "b": F(1.0)}, "ss": {"a": F(-1.0)}})
    assert worst == {"a": F(-1.0), "b": F(1.0)}
    assert binding == {"a": "ss", "b": "tt"}


def test_the_reducer_refuses_an_empty_corner_set():
    with pytest.raises(ValueError, match="at least one corner"):
        aggregate_corner_spec_scores({})


def test_the_reduction_is_monotone_in_every_corners_score():
    """Search relies on it: improving any corner's spec can never worsen the reduced vector."""
    rng = np.random.default_rng(11)
    for _ in range(200):
        per_corner = {c: {s: F(rng.uniform(-5, 5)) for s in "abc"} for c in ("tt", "ss", "ff")}
        before, _ = aggregate_corner_spec_scores(per_corner)
        bumped = {c: dict(v) for c, v in per_corner.items()}
        bumped["ss"]["b"] = F(float(bumped["ss"]["b"]) + 1.0)
        after, _ = aggregate_corner_spec_scores(bumped)
        assert all(after[k] >= before[k] for k in before)


def test_margins_reduce_to_the_smallest_over_corners_and_drop_the_unmeasurable():
    per_corner = {
        "tt": {"gain": 0.9, "power": 0.4, "vos": None},
        "ss": {"gain": 0.2, "power": float("nan"), "vos": None},
    }
    assert aggregate_corner_spec_margins(per_corner) == {"gain": F(0.2), "power": F(0.4)}


def test_margin_reduction_of_no_corners_is_empty_rather_than_an_error():
    assert aggregate_corner_spec_margins({}) == {}


# ======================================================= 2. vocabulary + validation (pure)
def test_worst_spec_is_a_canonical_strategy_with_aliases():
    assert PER_SPEC_CORNER_AGGREGATION in SCORE_AGGREGATION_STRATEGIES
    for alias in ("worst_spec", "Worst-Spec", " WORSTSPEC ", "per_spec_min", "per-spec-min",
                  "worst_case_per_spec"):
        assert normalize_score_aggregation(alias) == PER_SPEC_CORNER_AGGREGATION, alias


def test_the_existing_strategies_are_untouched_by_the_new_name():
    for alias, canonical in [("add", "sum"), ("average", "mean"), ("worst_case", "min"),
                             ("worst", "min")]:
        assert normalize_score_aggregation(alias) == canonical, alias


def _corner(name, enabled=True):
    return Corner(name=name, enabled=enabled,
                  model_includes=[ModelInclude(lib_file="cornerMOSlv.lib", section=name)],
                  supplies=[SupplyOverride(node="VDD", value=1.5)])


def test_pvt_config_accepts_worst_spec_at_load():
    cfg = PVTConfig(active_corner="tt", corners=[_corner("tt"), _corner("ss")],
                    mode="multi", score_aggregation="per_spec_min")
    assert cfg.score_aggregation == PER_SPEC_CORNER_AGGREGATION


def test_asking_for_worst_spec_without_multi_mode_warns_it_is_a_no_op(caplog):
    """The footgun this feature could ship with: `worst_spec` CHANGES what "feasible" means, so
    a config that sets it but leaves `mode: single` would report robustness it never measured.
    Warn at load, naming the fix — same treatment `OptimizerConfig` gives a no-op tie_breaker."""
    import logging

    with caplog.at_level(logging.WARNING, logger="spicexplorer.designer_tools.domains"):
        cfg = PVTConfig(active_corner="tt", corners=[_corner("tt")],
                        mode="single", score_aggregation="worst_spec")
    assert cfg.score_aggregation == PER_SPEC_CORNER_AGGREGATION  # still normalized, still stored
    assert "has NO effect" in caplog.text
    assert "pvt.mode: multi" in caplog.text


def test_worst_spec_under_multi_mode_does_not_warn(caplog):
    import logging

    with caplog.at_level(logging.WARNING, logger="spicexplorer.designer_tools.domains"):
        PVTConfig(active_corner="tt", corners=[_corner("tt"), _corner("ss")],
                  mode="multi", score_aggregation="worst_spec")
    assert "has NO effect" not in caplog.text


@pytest.mark.parametrize("strategy", ["sum", "mean", "min"])
def test_the_historical_strategies_never_warn_in_single_mode(strategy, caplog):
    """Only the new strategy is corner-axis-only in a way a user can silently miss; the shipped
    three are the historical default surface and must stay silent."""
    import logging

    with caplog.at_level(logging.WARNING, logger="spicexplorer.designer_tools.domains"):
        PVTConfig(active_corner="tt", corners=[_corner("tt")],
                  mode="single", score_aggregation=strategy)
    assert "has NO effect" not in caplog.text


def test_the_totals_reducer_refuses_worst_spec_with_a_pointer_rather_than_a_key_error():
    """`worst_spec` is not a reducer over per-corner TOTALS, so it must never silently reach the
    numpy registry — a bare KeyError there would read as an unknown-strategy config typo."""
    with pytest.raises(ValueError, match="does not collapse per-corner"):
        aggregate_corner_scores({"tt": F(1.0)}, PER_SPEC_CORNER_AGGREGATION)


@pytest.mark.parametrize("policy,expected", [
    (None, DEFAULT_UNMEASURED_POLICY), ("", DEFAULT_UNMEASURED_POLICY),
    ("none", DEFAULT_UNMEASURED_POLICY), ("default", DEFAULT_UNMEASURED_POLICY),
    ("penalty", "penalty"), (" FAIL ", "fail"),
])
def test_the_unmeasured_policy_normalizes(policy, expected):
    assert resolve_unmeasured_policy(policy) == expected


def test_an_unknown_unmeasured_policy_is_rejected():
    with pytest.raises(ValueError, match="Unknown unmeasured_policy"):
        resolve_unmeasured_policy("infeasible")


def test_the_default_unmeasured_policy_is_the_historical_one():
    assert DEFAULT_UNMEASURED_POLICY == "penalty"
    assert set(UNMEASURED_POLICIES) == {"penalty", "fail"}


def _config(**kw):
    from types import SimpleNamespace
    base = dict(name="NGOpt", type="nevergrad", budget=10, optimizer_kwargs=None,
                target_specs=SimpleNamespace(targets=[]), lin_variable_bounds=None,
                log_variable_bounds=None, loss_function_config=None, random_seed=None)
    base.update(kw)
    return OptimizerConfig(**base)


def test_optimizer_config_defaults_to_the_historical_unmeasured_policy():
    assert _config().unmeasured_policy == DEFAULT_UNMEASURED_POLICY


def test_optimizer_config_validates_the_unmeasured_policy_at_load():
    with pytest.raises(ValueError, match="Unknown unmeasured_policy"):
        _config(unmeasured_policy="hard-fail")


def test_optimizer_config_normalizes_the_unmeasured_policy():
    assert _config(unmeasured_policy=" Fail ").unmeasured_policy == "fail"


# ======================================================= Layer 2 harness — real evaluate, fake sim
class _FakeResult:
    """A structural `SimResult` returning canned per-spec readings. A spec absent from the map
    reads NaN — exactly what `NgspiceSimResult.scalar` returns for a `.meas` that produced no
    vector, a run that wrote no RAW, or a Tier-1 measurement that raised."""

    def __init__(self, values: Dict[str, float]):
        self._values = dict(values)

    def scalar(self, name, analysis):
        return float(self._values.get(name, float("nan")))

    def wave(self, name, analysis):
        raise KeyError(name)


class _FakeSimulator:
    """Structural `Simulator`: records the corners applied, never runs anything."""

    def __init__(self):
        self.applied: List[str] = []
        self.params: Dict[str, float] = {}

    def update_params(self, params):
        self.params.update(params or {})

    def apply_corner(self, corner, model_lib_root=None):
        self.applied.append(corner.name)

    def run(self, **kwargs):                       # pragma: no cover - stubbed away
        raise AssertionError("simulate_circuit is stubbed in these tests")

    def submit(self, label=None):                  # pragma: no cover - stubbed away
        raise AssertionError("simulate_circuit is stubbed in these tests")


class _StubOpt(Spice_Single_Objective):
    """The real scorer / evaluate loop; only the two purely-abstract engine hooks are stubbed."""

    def _create_optimizer_obj(self) -> bool:
        self.optimizer = object()
        return True

    def parameterize(self) -> Any:
        return {}

    def optimization_step(self):                   # pragma: no cover - not exercised here
        raise NotImplementedError

    def plot_solution(self, parameterization, **kwargs):
        return None


def _spec(name, target, goal="exceed", **kw):
    base = dict(name=name, testbench="tb", target=target, goal=goal, sim_type="ac",
                range=10.0, tolerance=1.0, error_type="relative-absolute",
                reward_type="relative-absolute")
    base.update(kw)
    return TargetSpec(**base)


def _build(tmp_path, specs, corners=("tt", "ss", "ff"), **cfg_overrides):
    """A real optimizer over the cascode project with a synthetic multi-corner PVT block, fake
    simulators, and the given target specs. No ngspice, no PDK, no netlist read."""
    proj = Project_Setup.from_yaml(CASCODE_YAML)
    proj.parallel_sim = False
    proj.pvt = PVTConfig(active_corner=corners[0], corners=[_corner(c) for c in corners],
                         mode="multi", score_aggregation=PER_SPEC_CORNER_AGGREGATION)
    wrappers = {"tb": _FakeSimulator()}
    opt = _StubOpt(setup_obj=proj, spicelib_wrappers=wrappers, output_root=tmp_path / "ck")
    opt.target_specs = type(proj.optimizer_config.target_specs)(targets=list(specs))
    opt.verbose = False
    for key, value in cfg_overrides.items():
        setattr(opt.optimizer_config, key, value)
    return proj, opt


def _canned(opt, monkeypatch, per_corner: Dict[str, Dict[str, float]]):
    """Stub `simulate_circuit` so each corner returns its own canned readings. The sequential
    multi-corner loop passes the corner name as `run_label`, which is how the stub knows."""
    seen: List[str] = []

    def fake_simulate(parameterization, run_label=None):
        seen.append(run_label)
        return {"tb": _FakeResult(per_corner[run_label])}

    monkeypatch.setattr(opt, "simulate_circuit", fake_simulate)
    return seen


# ======================================================= 3. worst-case selection, per goal type
@requires_cascode
def test_worst_case_selection_for_an_exceed_goal(tmp_path, monkeypatch):
    """EXCEED: the worst corner is the one with the SMALLEST value (least headroom)."""
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {"gain": 42.0}, "ff": {"gain": 55.0}})
    opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert meta["binding_corners"] == {"gain": "ss"}


@requires_cascode
def test_worst_case_selection_for_a_minimize_goal(tmp_path, monkeypatch):
    """MINIMIZE: the worst corner is the one with the LARGEST value."""
    _, opt = _build(tmp_path, [_spec("power", 40.0, goal="minimize")])
    _canned(opt, monkeypatch, {"tt": {"power": 10.0}, "ss": {"power": 20.0},
                               "ff": {"power": 39.0}})
    opt.evaluate({"x": 1.0})
    assert opt.optimization_log[-1].point.metadata["binding_corners"] == {"power": "ff"}


@requires_cascode
def test_worst_case_selection_for_an_exact_goal_is_the_largest_deviation(tmp_path, monkeypatch):
    """EXACT is two-sided and has no one-sided margin — which is exactly why the reduction is over
    the SIGNED SCORE rather than the raw value: the largest deviation on EITHER side wins, and a
    raw-value worst case would have no defined answer here at all."""
    _, opt = _build(tmp_path, [_spec("vos", 0.0, goal="exact", range=1.0, tolerance=0.01)])
    _canned(opt, monkeypatch, {"tt": {"vos": 0.05}, "ss": {"vos": -0.30}, "ff": {"vos": 0.10}})
    opt.evaluate({"x": 1.0})
    assert opt.optimization_log[-1].point.metadata["binding_corners"] == {"vos": "ss"}


@requires_cascode
def test_different_specs_can_bind_at_different_corners(tmp_path, monkeypatch):
    """The property no totals reducer has. `gain` is tightest at `ss`, `power` at `ff`."""
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed"),
                               _spec("power", 40.0, goal="minimize")])
    _canned(opt, monkeypatch, {
        "tt": {"gain": 60.0, "power": 10.0},
        "ss": {"gain": 41.0, "power": 12.0},
        "ff": {"gain": 58.0, "power": 39.5},
    })
    opt.evaluate({"x": 1.0})
    assert opt.optimization_log[-1].point.metadata["binding_corners"] == {
        "gain": "ss", "power": "ff"}


# ======================================================= 4. feasibility means ALL corners
@requires_cascode
def test_feasible_only_when_every_corner_passes_every_spec(tmp_path, monkeypatch):
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {"gain": 55.0}, "ff": {"gain": 58.0}})
    all_pass, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
    assert all_pass > 0

    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {"gain": 20.0}, "ff": {"gain": 58.0}})
    one_fails, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
    assert one_fails < 0


@requires_cascode
def test_one_failing_corner_cannot_be_masked_by_a_comfortable_one(tmp_path, monkeypatch):
    """The failure `mean`/`sum` over totals were built to avoid on the corner axis, restated on the
    per-spec axis: a huge reward at `tt` must not out-vote a violation at `ss`."""
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    _canned(opt, monkeypatch, {"tt": {"gain": 1e4}, "ss": {"gain": 10.0}, "ff": {"gain": 1e4}})
    score, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
    assert score < 0


@requires_cascode
def test_the_reported_score_is_the_worst_corner_vector_scored_once(tmp_path, monkeypatch):
    """The exact identity: reduce per spec, then run the project's own spec aggregation ONCE — not
    an average of per-corner totals."""
    from spicexplorer.core.utils import aggregate_spec_scores

    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed"),
                               _spec("power", 40.0, goal="minimize")])
    _canned(opt, monkeypatch, {
        "tt": {"gain": 60.0, "power": 10.0},
        "ss": {"gain": 41.0, "power": 12.0},
        "ff": {"gain": 58.0, "power": 39.5},
    })
    score, _ = opt.evaluate({"x": 1.0})
    worst = opt.optimization_log[-1].point.metadata["worst_spec_scores"]
    assert float(score) == pytest.approx(float(aggregate_spec_scores(
        {k: F(v) for k, v in worst.items()}, "feasibility_reward")))


# ======================================================= 5. the default corner path is unchanged
@requires_cascode
@pytest.mark.parametrize("strategy", ("mean", "sum", "min"))
def test_the_existing_corner_strategies_are_bit_identical(tmp_path, monkeypatch, strategy):
    """Regression oracle for feature 1: with any pre-existing `score_aggregation`, the score is
    still `aggregate_corner_scores` over the per-corner TOTALS, to the bit, and none of the new
    metadata keys appear."""
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    proj.pvt.score_aggregation = strategy
    canned = {"tt": {"gain": 60.0}, "ss": {"gain": 42.0}, "ff": {"gain": 55.0}}
    _canned(opt, monkeypatch, canned)
    score, _ = opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert set(meta) == {"corner_scores", "score_aggregation"}
    expected = aggregate_corner_scores(
        {c: F(v) for c, v in meta["corner_scores"].items()}, strategy)
    assert F(score) == expected


@requires_cascode
def test_single_corner_mode_is_untouched_and_carries_no_new_metadata(tmp_path, monkeypatch):
    """Single mode never reaches the corner axis at all, so the new strategy is inert there —
    and `PVTConfig.__post_init__` says so out loud rather than silently scoring one corner
    (pinned separately in `test_asking_for_worst_spec_without_multi_mode_warns_it_is_a_no_op`)."""
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({"gain": 60.0})})
    opt.evaluate({"x": 1.0})
    assert opt.optimization_log[-1].point.metadata == {}


@requires_cascode
def test_the_fit_summary_shape_is_unchanged_under_worst_spec(tmp_path, monkeypatch):
    """`_worst_corner_key`, `_metric_series` and the Ax backend's tracking metrics all read the
    `"<corner>::<spec>"` shape — the new strategy must not add bare-name keys beside them."""
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {"gain": 42.0}, "ff": {"gain": 55.0}})
    _, fit_summary = opt.evaluate({"x": 1.0})
    assert set(fit_summary) == {"tt::gain", "ss::gain", "ff::gain"}
    for info in fit_summary.values():
        assert set(info) == {"curr_val", "score"}


# ======================================================= 6. cost + log surface
@requires_cascode
def test_every_enabled_corner_is_simulated_so_the_cost_multiplies(tmp_path, monkeypatch):
    """The documented price of the feature: one trial costs len(corners) simulations."""
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    seen = _canned(opt, monkeypatch,
                   {"tt": {"gain": 60.0}, "ss": {"gain": 42.0}, "ff": {"gain": 55.0}})
    opt.evaluate({"x": 1.0})
    assert seen == ["tt", "ss", "ff"]
    assert opt.spicelib_wrappers["tb"].applied == ["tt", "ss", "ff"]


@requires_cascode
def test_the_binding_corner_of_each_spec_is_logged(tmp_path, monkeypatch, caplog):
    """"Which corner is costing me?" is not recoverable from the aggregated scalar."""
    import logging

    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {"gain": 42.0}, "ff": {"gain": 55.0}})
    with caplog.at_level(logging.DEBUG, logger="spicexplorer.optimization.base"):
        opt.evaluate({"x": 1.0})
    assert any("worst corner 'ss'" in r.message for r in caplog.records)


# ======================================================= 7. margins follow the worst corner
@requires_cascode
def test_the_margin_reward_pays_for_worst_corner_headroom(tmp_path, monkeypatch):
    """With `worst_spec` + `margin_reward_weight`, the rewarded margin is the corner-wise worst,
    not the nominal one — otherwise the two features would disagree about which design is robust."""
    tight_run = {"tt": {"gain": 60.0}, "ss": {"gain": 44.0}, "ff": {"gain": 60.0}}
    roomy_run = {"tt": {"gain": 60.0}, "ss": {"gain": 49.0}, "ff": {"gain": 60.0}}

    def spread(weight):
        _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")],
                        margin_reward_weight=weight, margin_reward_clip=1.0)
        _canned(opt, monkeypatch, tight_run)
        tight, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
        _canned(opt, monkeypatch, roomy_run)
        roomy, _ = opt.evaluate({"x": 1.0}, append_to_log=False)
        assert roomy > tight                       # more headroom scores higher either way
        return float(roomy - tight)

    # Isolate the margin TERM: the base reward also moves between the two runs, so the *extra*
    # spread the weight buys is what pins the arithmetic. Worst-corner margins are measured from
    # the tolerance-adjusted boundary over `range`: (44-39)/10 = 0.5 and (49-39)/10 = 1.0, both
    # inside the clip, times weight 0.5 -> exactly 0.25 of extra separation.
    assert spread(0.5) - spread(0.0) == pytest.approx(0.25)


# ======================================================= 8. TODAY's unmeasured-metric behaviour
# Locked in FIRST, deliberately: the feature was scoped on the assumption that a partly-crashed
# simulation could score as a valid design point, and the honest finding is that at the SCORE level
# it cannot. These names state what today does so a future change has to argue with them.
@requires_cascode
@pytest.mark.parametrize("reading,label", [
    ({}, "missing"),                          # spec absent from the result entirely
    ({"gain": float("nan")}, "nan"),          # `.meas` produced no vector / measurement raised
    ({"gain": float("inf")}, "posinf"),       # a diverged AC solve
    ({"gain": float("-inf")}, "neginf"),
])
def test_today_an_unmeasured_spec_already_scores_max_penalty_and_is_infeasible(
        tmp_path, monkeypatch, reading, label):
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult(reading)})
    score, fit_summary = opt.evaluate({"x": 1.0})
    assert float(fit_summary["gain"]["score"]) == -float(MAX_PENALTY), label
    assert np.isnan(float(fit_summary["gain"]["curr_val"])) or not np.isfinite(
        float(fit_summary["gain"]["curr_val"])), label
    assert float(score) <= -float(MAX_PENALTY), label


@requires_cascode
def test_today_a_non_positive_log_scale_reading_is_also_unmeasurable(tmp_path, monkeypatch):
    """`0` has no decade: floored, it would read as infinitely GOOD for a MINIMIZE spec."""
    proj, opt = _build(tmp_path, [_spec("power", 1e-3, goal="minimize", log_scale=True,
                                        range=1e-3, tolerance=1e-4)])
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({"power": 0.0})})
    _, fit_summary = opt.evaluate({"x": 1.0})
    assert float(fit_summary["power"]["score"]) == -float(MAX_PENALTY)


@requires_cascode
def test_today_the_penalty_is_the_same_for_every_error_kernel_including_bounded_ones(
        tmp_path, monkeypatch):
    """The `-MAX_PENALTY` is assigned INSTEAD of running a kernel, so a bounded kernel
    (relative-sigmoid saturates near 1·weight) inherits the same defined worst case rather than
    its own ceiling — which is what stops a crashed sim from OUTSCORING a converged bad design."""
    for kernel in ("relative-absolute", "relative-sigmoid", "relative-squared"):
        proj, opt = _build(tmp_path, [_spec("gain", 40.0, error_type=kernel)])
        proj.pvt.mode = "single"
        monkeypatch.setattr(opt, "simulate_circuit",
                            lambda parameterization, run_label=None: {"tb": _FakeResult({})})
        _, fit_summary = opt.evaluate({"x": 1.0}, append_to_log=False)
        assert float(fit_summary["gain"]["score"]) == -float(MAX_PENALTY), kernel


@requires_cascode
def test_today_nothing_records_that_the_trial_was_unmeasured(tmp_path, monkeypatch):
    """The actual gap. The score fails closed, but the trial carries no machine-readable mark, and
    `-MAX_PENALTY` is also the floor a converged-but-terrible spec CLIPS to — so downstream cannot
    tell 'crashed' from 'bad' without re-deriving it from values and targets (which is exactly what
    the API's `checkpoint_reader._is_feasible` does)."""
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({})})
    opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert "unmeasured_specs" not in meta and "feasible" not in meta


@requires_cascode
def test_today_a_crashed_spec_and_a_clipped_terrible_spec_are_numerically_identical(
        tmp_path, monkeypatch):
    """Why the record is worth having: both floor at exactly `-MAX_PENALTY`."""
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed", range=1e-9)])
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({})})
    crashed = opt.evaluate({"x": 1.0}, append_to_log=False)[1]["gain"]["score"]
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({"gain": -1e9})})
    terrible = opt.evaluate({"x": 1.0}, append_to_log=False)[1]["gain"]["score"]
    assert float(crashed) == float(terrible) == -float(MAX_PENALTY)


# ======================================================= 9. `unmeasured_policy: fail`
@requires_cascode
@pytest.mark.parametrize("reading,label", [
    ({}, "missing"),
    ({"gain": float("nan")}, "nan"),
])
def test_fail_mode_records_the_unmeasured_spec_and_an_explicit_infeasible_verdict(
        tmp_path, monkeypatch, reading, label):
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")],
                       unmeasured_policy="fail")
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult(reading)})
    opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert meta["unmeasured_policy"] == "fail"
    assert meta["unmeasured_specs"] == ["gain"], label
    assert meta["feasible"] is False, label


@requires_cascode
def test_fail_mode_records_a_feasible_verdict_when_everything_measured_and_passed(
        tmp_path, monkeypatch):
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")],
                       unmeasured_policy="fail")
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({"gain": 60.0})})
    opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert meta["unmeasured_specs"] == []
    assert meta["feasible"] is True


@requires_cascode
def test_fail_mode_calls_a_measured_but_violating_trial_infeasible_not_unmeasured(
        tmp_path, monkeypatch):
    """The distinction the record exists to make: `feasible: False` with an EMPTY unmeasured list
    is 'converged, and bad'; a non-empty list is 'we never found out'."""
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")],
                       unmeasured_policy="fail")
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({"gain": 5.0})})
    opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert meta["unmeasured_specs"] == [] and meta["feasible"] is False


@requires_cascode
def test_fail_mode_does_not_change_any_score(tmp_path, monkeypatch):
    """Deliberate, and the honest reading of the characterization above: every spec-axis strategy
    already floors an unmeasured trial at or below `-MAX_PENALTY`, and both reward terms are gated
    on the same feasibility test, so there is no reachable score for the policy to change. It buys
    the RECORD, not a number — a knob that silently rescaled the objective would be worse."""
    for policy in ("penalty", "fail"):
        proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed"),
                                      _spec("power", 40.0, goal="minimize")],
                           unmeasured_policy=policy)
        proj.pvt.mode = "single"
        monkeypatch.setattr(
            opt, "simulate_circuit",
            lambda parameterization, run_label=None: {"tb": _FakeResult({"power": 10.0})})
        score, fit_summary = opt.evaluate({"x": 1.0}, append_to_log=False)
        assert float(score) <= -float(MAX_PENALTY)
        assert float(fit_summary["gain"]["score"]) == -float(MAX_PENALTY)


@requires_cascode
def test_fail_mode_namespaces_the_unmeasured_spec_by_corner(tmp_path, monkeypatch):
    """A multi-corner trial names WHICH corner lost the measurement — a spec that measures at `tt`
    and crashes at `ss` is a different diagnosis from one that never measures at all."""
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")], unmeasured_policy="fail")
    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {}, "ff": {"gain": 55.0}})
    opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert meta["unmeasured_specs"] == ["ss::gain"]
    assert meta["feasible"] is False
    # the crashed corner still binds the spec, so the design is not credited for tt/ff
    assert meta["binding_corners"]["gain"] == "ss"


@requires_cascode
def test_fail_mode_warns_so_a_crash_run_is_visible_in_the_log(tmp_path, monkeypatch, caplog):
    import logging

    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")],
                       unmeasured_policy="fail")
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({})})
    with caplog.at_level(logging.WARNING, logger="spicexplorer.optimization.base"):
        opt.evaluate({"x": 1.0})
    assert any("unmeasured_policy='fail'" in r.message for r in caplog.records)


@requires_cascode
def test_the_feasible_verdict_uses_the_same_epsilon_the_scorer_uses(tmp_path, monkeypatch):
    """One definition of feasible across the scorer and the log: penalty dust below EPSILON is
    feasible in both, or a run's own metadata contradicts its own score."""
    proj, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed", reward_type="no-reward")],
                       unmeasured_policy="fail")
    proj.pvt.mode = "single"
    monkeypatch.setattr(opt, "simulate_circuit",
                        lambda parameterization, run_label=None: {"tb": _FakeResult({"gain": 39.0})})
    score, _ = opt.evaluate({"x": 1.0})
    meta = opt.optimization_log[-1].point.metadata
    assert meta["feasible"] is (float(score) > -float(EPSILON))


@requires_cascode
def test_the_default_policy_leaves_the_metadata_shape_untouched_under_worst_spec(
        tmp_path, monkeypatch):
    _, opt = _build(tmp_path, [_spec("gain", 40.0, goal="exceed")])
    _canned(opt, monkeypatch, {"tt": {"gain": 60.0}, "ss": {"gain": 42.0}, "ff": {"gain": 55.0}})
    opt.evaluate({"x": 1.0})
    assert set(opt.optimization_log[-1].point.metadata) == {
        "corner_scores", "score_aggregation", "worst_spec_scores", "binding_corners"}
