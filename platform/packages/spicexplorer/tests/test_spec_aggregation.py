"""Spec-axis aggregation: `feasibility_reward` | `weighted_sum` | `chebyshev`.

Until now the scalarizer was hardcoded inside `compute_fitness` — one rule, not selectable from
YAML. This suite covers making it a choice, and it is organised around the two ways that change
could go wrong:

1. **Regression.** `feasibility_reward` is the DEFAULT and must reproduce the old inline
   `reward if penalty > -EPSILON else penalty` line exactly, for every project that names no key.
   A silent change here would re-scale every historical checkpoint's objective.
2. **The new strategies must actually differ, in the direction claimed.** Three scalarizations
   that all "go down when things get worse" prove nothing; what distinguishes them is *which
   design they prefer when two are equally bad in total*, and *what they flatten*. Those are the
   properties pinned below.

Also covered because gradient-free search silently depends on them: monotonicity in every
strategy (improving one spec must never worsen the aggregate), and the interaction with the two
sentinel magnitudes — `MAX_PENALTY` for a failed simulation, and the reward branch.

There are TWO aggregation axes and they compose: this one reduces {specs} -> scalar (once per
corner), then `aggregate_corner_scores` reduces {corners} -> scalar. The final section pins that
composition.

No SPICE, no PDK.
"""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest
from spicexplorer.core.domains import OptimizerConfig, TargetSpec
from spicexplorer.core.utils import (
    AGGREGATION_SHAPE_PARAMS,
    EPSILON,
    SPEC_SCORE_AGGREGATORS,
    aggregate_corner_scores,
    aggregate_spec_scores,
    resolve_aggregation_params,
)
from spicexplorer.optimization.base import MAX_PENALTY, Spice_Constraint_Satisfaction

F = np.float64


def _agg(scores, strategy="feasibility_reward", params=None):
    return aggregate_spec_scores({k: F(v) for k, v in scores.items()}, strategy, params)


def _legacy(scores):
    """The exact rule `compute_fitness` used to inline, kept as an independent oracle."""
    reward = sum(F(s) for s in scores.values() if s > 0)
    penalty = sum(F(s) for s in scores.values() if s <= 0)
    return F(reward) if penalty > -1 * EPSILON else F(penalty)


# =========================================================== 1. regression: the historical default
@pytest.mark.parametrize("scores", [
    {},                                            # degenerate: every spec disabled
    {"a": 0.0},                                    # exactly met
    {"a": 5.0, "b": 2.0},                          # all satisfied, rewards present
    {"a": -3.0},                                   # one violation
    {"a": -3.0, "b": -1.0},                        # several violations
    {"a": -3.0, "b": 7.0},                         # mixed: reward must be masked
    {"a": -1e-15},                                 # penalty dust below EPSILON -> feasible
    {"a": -float(MAX_PENALTY)},                    # failed simulation
    {"a": -float(MAX_PENALTY), "b": 9.0},
])
def test_feasibility_reward_reproduces_the_old_inline_rule(scores):
    assert _agg(scores) == pytest.approx(_legacy(scores))


def test_default_strategy_is_feasibility_reward():
    scores = {"a": -3.0, "b": 7.0}
    assert aggregate_spec_scores({k: F(v) for k, v in scores.items()}) == pytest.approx(_agg(scores))


def test_epsilon_dust_counts_as_feasible():
    """Float dust in a satisfied spec must not suppress the whole reward landscape."""
    assert _agg({"a": -float(EPSILON) / 2, "b": 4.0}) == pytest.approx(4.0)
    assert _agg({"a": -float(EPSILON) * 10, "b": 4.0}) < 0


# =========================================================== 2. what each strategy computes
def test_weighted_sum_is_the_plain_penalty_sum():
    assert _agg({"a": -3.0, "b": -1.0, "c": -0.5}, "weighted_sum") == pytest.approx(-4.5)


def test_chebyshev_is_the_worst_spec_plus_the_augmentation_term():
    scores = {"a": -3.0, "b": -1.0, "c": -0.5}
    rho = AGGREGATION_SHAPE_PARAMS["chebyshev"]["rho"]
    assert _agg(scores, "chebyshev") == pytest.approx(-(3.0 + rho * 4.5))


def test_chebyshev_rho_zero_is_pure_min_max():
    assert _agg({"a": -3.0, "b": -1.0}, "chebyshev", {"rho": 0.0}) == pytest.approx(-3.0)


def test_chebyshev_prefers_balanced_violations_where_weighted_sum_is_indifferent():
    """The whole reason to offer min-max. Two designs with the SAME total error: one badly
    lopsided, one balanced. `weighted_sum` cannot tell them apart; `chebyshev` prefers balance."""
    lopsided = {"a": -9.0, "b": -1.0}
    balanced = {"a": -5.0, "b": -5.0}
    assert _agg(lopsided, "weighted_sum") == pytest.approx(_agg(balanced, "weighted_sum"))
    assert _agg(balanced, "chebyshev") > _agg(lopsided, "chebyshev")


def test_augmentation_breaks_ties_the_pure_min_max_cannot_see():
    """Without the rho term, progress on every non-worst spec is invisible — a flat plateau the
    search cannot descend. Same worst spec, strictly better elsewhere, must score strictly better."""
    worse = {"a": -5.0, "b": -4.0}
    better = {"a": -5.0, "b": -0.1}
    assert _agg(better, "chebyshev", {"rho": 0.0}) == pytest.approx(_agg(worse, "chebyshev", {"rho": 0.0}))
    assert _agg(better, "chebyshev") > _agg(worse, "chebyshev")


def test_rho_stays_small_enough_that_the_worst_spec_still_dominates():
    """If rho were large, chebyshev would silently become a weighted sum."""
    rho = AGGREGATION_SHAPE_PARAMS["chebyshev"]["rho"]
    many_small = {f"s{i}": -1.0 for i in range(20)}      # sum 20, worst 1
    one_big = {"s": -5.0}                                # sum 5, worst 5
    assert _agg(one_big, "chebyshev") < _agg(many_small, "chebyshev")
    assert rho < 0.05


# =========================================================== 3. the feasible region
def test_only_feasibility_reward_exposes_a_reward_gradient():
    """`weighted_sum` and `chebyshev` are penalty-only, so they are FLAT at 0 once feasible. That
    is the honest reading of each formula and is exactly why they are baselines, not defaults."""
    feasible = {"a": 4.0, "b": 6.0}
    assert _agg(feasible, "feasibility_reward") == pytest.approx(10.0)
    assert _agg(feasible, "weighted_sum") == pytest.approx(0.0)
    assert _agg(feasible, "chebyshev") == pytest.approx(0.0)


def test_penalty_only_strategies_ignore_reward_even_while_infeasible():
    with_reward = {"a": -2.0, "b": 50.0}
    without = {"a": -2.0}
    for strategy in ("weighted_sum", "chebyshev"):
        assert _agg(with_reward, strategy) == pytest.approx(_agg(without, strategy))


def test_reward_cannot_buy_off_a_violation_in_any_strategy():
    """The masking bug the lexicographic rule exists to prevent, checked across all three."""
    for strategy in SPEC_SCORE_AGGREGATORS:
        assert _agg({"a": -1.0, "b": 1e9}, strategy) < 0, strategy


# =========================================================== 4. invariants search relies on
@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_monotone_non_decreasing_in_every_spec(strategy):
    """Gradient-free search reads a decrease as "that change hurt". Improving ANY single spec must
    never lower the aggregate — the trap `aggregate_corner_scores` already documents as AGG-2."""
    rng = np.random.default_rng(20260812)
    for _ in range(200):
        base = {f"s{i}": float(v) for i, v in enumerate(rng.uniform(-10, 5, size=4))}
        for key in base:
            better = dict(base)
            better[key] = base[key] + float(rng.uniform(0.01, 3.0))
            assert _agg(better, strategy) >= _agg(base, strategy) - 1e-12, (strategy, key, base)


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_a_failed_simulation_dominates_any_converged_violation(strategy):
    """MAX_PENALTY is the "no metric" sentinel; if a converged-but-bad design could outscore it,
    the optimizer would be pulled toward crashes."""
    crashed = {"a": -float(MAX_PENALTY), "b": 0.0}
    bad_but_converged = {"a": -999.0, "b": -999.0}
    assert _agg(crashed, strategy) < _agg(bad_but_converged, strategy), strategy


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_finite_and_ordered_on_extreme_magnitudes(strategy):
    for scores in ({"a": -1e300}, {"a": -1e-300}, {"a": 1e300}, {"a": -1e300, "b": 1e300}):
        assert np.isfinite(_agg(scores, strategy)), (strategy, scores)


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_empty_input_returns_zero_rather_than_raising(strategy):
    """Every spec `enable: false` is degenerate, not a crash — and `max()` over an empty set would
    raise, which is the specific way chebyshev could have blown up."""
    assert aggregate_spec_scores({}, strategy) == 0.0


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_insensitive_to_spec_ordering(strategy):
    a = {"x": -3.0, "y": -1.0, "z": 2.0}
    b = {"z": 2.0, "y": -1.0, "x": -3.0}
    assert _agg(a, strategy) == pytest.approx(_agg(b, strategy))


# =========================================================== 5. validation
def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="Unknown spec_aggregation"):
        _agg({"a": -1.0}, "min_max")


def test_unknown_aggregation_param_is_rejected():
    with pytest.raises(ValueError, match="Unknown aggregation_params"):
        resolve_aggregation_params("chebyshev", {"rhoo": 1.0})


def test_params_on_a_strategy_that_takes_none_are_ignored():
    assert resolve_aggregation_params("weighted_sum", {"rho": 1.0}) == {}
    assert _agg({"a": -2.0}, "weighted_sum", {"rho": 1.0}) == pytest.approx(-2.0)


def _config(**kw):
    base = dict(name="NGOpt", type="nevergrad", budget=10, optimizer_kwargs=None,
                target_specs=SimpleNamespace(targets=[]), lin_variable_bounds=None,
                log_variable_bounds=None, loss_function_config=None, random_seed=None)
    base.update(kw)
    return OptimizerConfig(**base)


def test_optimizer_config_defaults_preserve_historical_behaviour():
    cfg = _config()
    assert cfg.spec_aggregation == "feasibility_reward"
    assert cfg.aggregation_params == {}


def test_optimizer_config_validates_the_strategy_at_load():
    with pytest.raises(ValueError, match="Unknown spec_aggregation"):
        _config(spec_aggregation="cheby")


def test_optimizer_config_validates_params_at_load():
    with pytest.raises(ValueError, match="Unknown aggregation_params"):
        _config(spec_aggregation="chebyshev", aggregation_params={"rhoo": 1.0})


def test_optimizer_config_resolves_defaults_for_the_chosen_strategy():
    cfg = _config(spec_aggregation="chebyshev")
    assert cfg.aggregation_params == AGGREGATION_SHAPE_PARAMS["chebyshev"]
    cfg = _config(spec_aggregation="  CHEBYSHEV ", aggregation_params={"rho": 0.5})
    assert cfg.spec_aggregation == "chebyshev"
    assert cfg.aggregation_params == {"rho": 0.5}


# =========================================================== 6. through the real scorer
class _Scorer:
    """Minimal stand-in exposing only what `compute_fitness` reads off `self`."""

    def __init__(self, specs, strategy="feasibility_reward", params=None):
        self.target_specs = SimpleNamespace(enabled_targets=lambda: specs)
        self.verbose = False
        self.optimizer_config = SimpleNamespace(
            spec_aggregation=strategy, aggregation_params=params)

    compute_fitness = Spice_Constraint_Satisfaction.compute_fitness
    compute_fitness_for_spec = Spice_Constraint_Satisfaction.compute_fitness_for_spec
    compute_constraint_violation_penalty_for_spec = (
        Spice_Constraint_Satisfaction.compute_constraint_violation_penalty_for_spec)


def _spec(name, target, goal="exceed", **kw):
    # `tolerance` is stated EXPLICITLY and non-zero on purpose: `0` is falsy and is silently
    # replaced by 5 % of target (pinned in test_relative_gaussian_error), and the penalty is
    # measured from the band edge `target - tolerance`, not from the bare target. Leaving it at 0
    # would make every expected number below an accident of that substitution.
    base = dict(name=name, testbench="tb", target=target, goal=goal, sim_type="ac",
                range=10.0, tolerance=1.0, error_type="relative-absolute")
    base.update(kw)
    return TargetSpec(**base)


# Penalty is |curr - (target - tolerance)| / range for an unmet EXCEED spec:
#   gain: |30 - 39| / 10 = 0.9      ugf: |96 - 99| / 10 = 0.3
_P_GAIN, _P_UGF = 0.9, 0.3


def test_compute_fitness_honours_the_selected_strategy():
    specs = [_spec("gain", 40.0), _spec("ugf", 100.0)]
    perf = {"gain": np.float64(30.0), "ugf": np.float64(96.0)}
    scores = {}
    for strategy in SPEC_SCORE_AGGREGATORS:
        total, _ = _Scorer(specs, strategy).compute_fitness(perf)
        scores[strategy] = float(total)
    total_p = _P_GAIN + _P_UGF
    assert scores["weighted_sum"] == pytest.approx(-total_p)
    assert scores["chebyshev"] == pytest.approx(-(max(_P_GAIN, _P_UGF) + 1e-3 * total_p))
    assert scores["feasibility_reward"] == pytest.approx(-total_p)  # no rewards while infeasible


def test_compute_fitness_without_an_optimizer_config_falls_back_to_the_default():
    """The API's score preview and the test stand-ins invoke this unbound; it must not explode."""
    specs = [_spec("gain", 40.0)]
    scorer = _Scorer(specs)
    del scorer.optimizer_config
    total, _ = scorer.compute_fitness({"gain": np.float64(30.0)})
    assert float(total) == pytest.approx(-_P_GAIN)


def test_fit_summary_is_unaffected_by_the_strategy():
    """Per-spec diagnostics must stay comparable across arms — only the SCALAR changes."""
    specs = [_spec("gain", 40.0), _spec("ugf", 100.0)]
    perf = {"gain": np.float64(30.0), "ugf": np.float64(99.0)}
    summaries = [_Scorer(specs, s).compute_fitness(perf)[1] for s in SPEC_SCORE_AGGREGATORS]
    for other in summaries[1:]:
        assert other.keys() == summaries[0].keys()
        for k in other:
            assert other[k]["score"] == pytest.approx(summaries[0][k]["score"])


def test_a_missing_metric_still_scores_max_penalty_under_every_strategy():
    specs = [_spec("gain", 40.0), _spec("ugf", 100.0)]
    perf = {"gain": np.float64(45.0)}                    # `ugf` never measured
    for strategy in SPEC_SCORE_AGGREGATORS:
        total, summary = _Scorer(specs, strategy).compute_fitness(perf)
        assert summary["ugf"]["score"] == pytest.approx(-float(MAX_PENALTY))
        assert float(total) <= -float(MAX_PENALTY), strategy


# =========================================================== 7. composition with the corner axis
def test_spec_then_corner_aggregation_composes():
    """A multi-corner trial reduces specs FIRST (per corner), then corners. Pinned end-to-end so
    the two axes cannot be silently swapped."""
    per_corner_specs = {
        "tt": {"gain": -1.0, "ugf": -3.0},
        "ss": {"gain": -2.0, "ugf": -2.0},
    }
    for strategy in SPEC_SCORE_AGGREGATORS:
        corner_scores = {c: _agg(s, strategy) for c, s in per_corner_specs.items()}
        worst = aggregate_corner_scores(corner_scores, "min")
        assert worst == pytest.approx(min(corner_scores.values())), strategy

    # chebyshev prefers the balanced corner; weighted_sum is indifferent between them
    cheb = {c: _agg(s, "chebyshev") for c, s in per_corner_specs.items()}
    ws = {c: _agg(s, "weighted_sum") for c, s in per_corner_specs.items()}
    assert cheb["ss"] > cheb["tt"]
    assert ws["ss"] == pytest.approx(ws["tt"])
