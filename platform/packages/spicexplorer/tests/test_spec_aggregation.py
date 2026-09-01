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
    DEFAULT_MARGIN_REWARD_CLIP,
    DEFAULT_MARGIN_REWARD_WEIGHT,
    DEFAULT_TIE_BREAKER_WEIGHT,
    EPSILON,
    SPEC_SCORE_AGGREGATORS,
    aggregate_corner_scores,
    aggregate_spec_scores,
    normalized_spec_margin,
    resolve_aggregation_params,
    resolve_margin_reward,
    resolve_tie_breaker,
)
from spicexplorer.optimization.base import (
    MAX_PENALTY,
    Spice_Constraint_Satisfaction,
    Spice_Single_Objective,
)

F = np.float64


def _agg(scores, strategy="feasibility_reward", params=None):
    return aggregate_spec_scores({k: F(v) for k, v in scores.items()}, strategy, params)


def _tb(scores, strategy, params=None, tie_breaker=None,
        tie_breaker_weight=DEFAULT_TIE_BREAKER_WEIGHT):
    """`_agg` with the opt-in tie-breaker wired through (section 8)."""
    return aggregate_spec_scores({k: F(v) for k, v in scores.items()}, strategy, params,
                                 tie_breaker=tie_breaker, tie_breaker_weight=tie_breaker_weight)


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


# =========================================================== 8. the opt-in tie-breaker
# `weighted_sum` and `chebyshev` are penalty-only, so they are identically 0 EVERYWHERE in the
# feasible region (section 3 pins that). The consequence is easy to miss and expensive: every
# feasible design ties, so the "best" design such a run reports is whichever the sampler happened
# to visit first — search-order noise, not a design decision. `tie_breaker: objective` adds the
# satisfied specs' own reward mass back as a lexicographically-lower term.
#
# The organising risk here is the same as section 1's: this is an ADDITIVE key on a scorer that
# every historical checkpoint was produced by, so the default path must be bit-identical, not
# merely close. That is checked against an independent oracle of the pre-change formulas.
def _pre_tie_breaker_oracle(scores, strategy, params=None):
    """The three formulas EXACTLY as they read before `tie_breaker` existed, as an oracle."""
    penalties = [-F(s) for s in scores.values() if s < 0]
    rewards = F(sum(F(s) for s in scores.values() if s > 0))
    if not scores:
        return F(0.0)
    if strategy == "feasibility_reward":
        total_penalty = -F(sum(penalties))
        return rewards if total_penalty > -1 * EPSILON else total_penalty
    if strategy == "weighted_sum":
        return F(-1 * sum(penalties))
    if not penalties:
        return F(0.0)
    rho = F(resolve_aggregation_params("chebyshev", params)["rho"])
    return F(-1 * (max(penalties) + rho * sum(penalties)))


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_default_path_is_bit_identical_to_before_the_key_existed(strategy):
    """Not `approx`: a historical run's objective must reproduce to the last bit, and an omitted
    key and an explicit `tie_breaker=None` must be the same call."""
    rng = np.random.default_rng(20260816)
    cases = [{}, {"a": 0.0}, {"a": 5.0, "b": 2.0}, {"a": -3.0, "b": 7.0},
             {"a": -float(EPSILON) / 2, "b": 4.0}, {"a": -float(MAX_PENALTY), "b": 9.0}]
    cases += [{f"s{i}": float(v) for i, v in enumerate(rng.uniform(-10, 10, size=5))}
              for _ in range(100)]
    for scores in cases:
        expected = _pre_tie_breaker_oracle(scores, strategy)
        assert _agg(scores, strategy) == expected, (strategy, scores)
        assert aggregate_spec_scores({k: F(v) for k, v in scores.items()}, strategy,
                                     tie_breaker=None) == expected, (strategy, scores)


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
def test_the_tie_breaker_picks_the_better_feasible_design(strategy):
    """The actual defect: two feasible designs, one strictly better on the declared objectives.
    Without the flag they tie at 0 and the winner is search order; with it, the better one wins."""
    better = {"gain": 12.0, "power": 3.0}
    worse = {"gain": 4.0, "power": 3.0}
    assert _agg(better, strategy) == _agg(worse, strategy) == pytest.approx(0.0)

    tb = dict(tie_breaker="objective")
    assert _tb(better, strategy, **tb) > _tb(worse, strategy, **tb)


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
def test_the_tie_breaker_leaves_the_infeasible_region_untouched(strategy):
    """Declared semantics: the term applies ONLY where the design is feasible (Σ P > -EPSILON).
    An infeasible point's score — and therefore the whole infeasible ordering — is unchanged,
    reward mass or not."""
    rng = np.random.default_rng(20260817)
    for _ in range(200):
        scores = {f"s{i}": float(v) for i, v in enumerate(rng.uniform(-10, 10, size=4))}
        scores["violated"] = -float(rng.uniform(0.5, 50.0))          # forces infeasibility
        assert _tb(scores, strategy, tie_breaker="objective") == _agg(scores, strategy)


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
@pytest.mark.parametrize("weight", (1e-9, 1e-6, 1e-3, 1.0))
def test_the_weight_is_cosmetic_and_never_changes_the_ordering(strategy, weight):
    """The guarantee is stronger than "the weight is infinitesimal": the base score is exactly 0
    wherever the term applies, so EVERY positive weight induces the same ordering. Pinned over
    six decades so nobody has to reason about how small "small enough" is."""
    rng = np.random.default_rng(20260818)
    points = [{f"s{i}": float(v) for i, v in enumerate(rng.uniform(0.0, 500.0, size=4))}
              for _ in range(40)]
    ref = sorted(range(len(points)),
                 key=lambda i: float(_tb(points[i], strategy, tie_breaker="objective")))
    got = sorted(range(len(points)),
                 key=lambda i: float(_tb(points[i], strategy, tie_breaker="objective",
                                         tie_breaker_weight=weight)))
    assert got == ref


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
def test_feasibility_still_strictly_dominates_with_the_tie_breaker_on(strategy):
    """`R >= 0` and `w > 0`, so a feasible point never drops below 0 and an infeasible one never
    reaches it — the lexicographic ordering the flag must not be able to invert, even at w=1."""
    feasible = _tb({"a": 0.0, "b": 1e-9}, strategy, tie_breaker="objective", tie_breaker_weight=1.0)
    for penalty in (1e-9, 1.0, float(MAX_PENALTY)):
        infeasible = _tb({"a": -penalty, "b": 1e9}, strategy, tie_breaker="objective",
                         tie_breaker_weight=1.0)
        assert infeasible < 0 <= feasible, (strategy, penalty)


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_monotone_non_decreasing_with_the_tie_breaker_on(strategy):
    """Section 4's invariant is a claim about the tie-broken score too — adding a term is exactly
    how it could have been broken."""
    rng = np.random.default_rng(20260819)
    for _ in range(200):
        base = {f"s{i}": float(v) for i, v in enumerate(rng.uniform(-10, 5, size=4))}
        for key in base:
            better = dict(base)
            better[key] = base[key] + float(rng.uniform(0.01, 3.0))
            assert (_tb(better, strategy, tie_breaker="objective")
                    >= _tb(base, strategy, tie_breaker="objective") - 1e-12), (strategy, key, base)


def test_the_tie_breaker_is_a_no_op_under_feasibility_reward():
    """Its feasible branch already IS the reward term; re-adding it would rescale the historical
    objective for no gain. Declared in the docstring, pinned here."""
    rng = np.random.default_rng(20260820)
    for _ in range(100):
        scores = {f"s{i}": float(v) for i, v in enumerate(rng.uniform(-10, 10, size=4))}
        assert (_tb(scores, "feasibility_reward", tie_breaker="objective")
                == _agg(scores, "feasibility_reward"))


def test_an_unknown_tie_breaker_is_rejected():
    with pytest.raises(ValueError, match="Unknown tie_breaker"):
        _tb({"a": -1.0}, "weighted_sum", tie_breaker="objectve")


@pytest.mark.parametrize("off", (None, "", "  ", "none", "None", "null", "OFF"))
def test_the_off_spellings_all_disable_the_tie_breaker(off):
    assert resolve_tie_breaker(off) is None


@pytest.mark.parametrize("on", ("objective", "  OBJECTIVE "))
def test_the_tie_breaker_name_is_normalized(on):
    assert resolve_tie_breaker(on) == "objective"


# ---- config plumbing
def test_optimizer_config_defaults_leave_the_tie_breaker_off():
    cfg = _config()
    assert cfg.tie_breaker is None
    assert cfg.tie_breaker_weight == DEFAULT_TIE_BREAKER_WEIGHT


def test_optimizer_config_validates_the_tie_breaker_at_load():
    with pytest.raises(ValueError, match="Unknown tie_breaker"):
        _config(spec_aggregation="weighted_sum", tie_breaker="lexicographic")


@pytest.mark.parametrize("weight", (0.0, -1.0, float("nan"), float("inf")))
def test_optimizer_config_rejects_a_degenerate_tie_breaker_weight(weight):
    with pytest.raises(ValueError, match="tie_breaker_weight"):
        _config(spec_aggregation="weighted_sum", tie_breaker="objective",
                tie_breaker_weight=weight)


def test_a_degenerate_weight_is_only_checked_when_the_tie_breaker_is_on():
    """Off is off: a stale weight in a YAML must not fail a run that never uses it."""
    assert _config(tie_breaker_weight=0.0).tie_breaker is None


def test_optimizer_config_normalizes_the_tie_breaker_and_keeps_the_weight():
    cfg = _config(spec_aggregation="chebyshev", tie_breaker=" Objective ",
                  tie_breaker_weight=1e-3)
    assert cfg.tie_breaker == "objective"
    assert cfg.tie_breaker_weight == 1e-3


def test_the_tie_breaker_warns_when_it_can_have_no_effect(caplog):
    """`feasibility_reward` + `tie_breaker` is a config that does nothing — say so at load rather
    than let a study believe it changed the objective."""
    # `core/domains.py` names its logger "spicexplorer.designer_tools.domains" (module path and
    # logger name differ here) — pin the emitting logger, not the module it lives in.
    with caplog.at_level("WARNING", logger="spicexplorer.designer_tools.domains"):
        _config(spec_aggregation="feasibility_reward", tie_breaker="objective")
    warnings = [r for r in caplog.records if r.name == "spicexplorer.designer_tools.domains"]
    assert any("NO effect" in r.message for r in warnings)


# ---- through the real scorer
class _SingleObjectiveScorer(_Scorer):
    """`Spice_Single_Objective`'s scorer — the one with a reward term, hence the one whose
    feasible region the tie-breaker has anything to work with."""

    compute_fitness_for_spec = Spice_Single_Objective.compute_fitness_for_spec
    compute_reward_for_spec = Spice_Single_Objective.compute_reward_for_spec


def _scorer(strategy, tie_breaker=None, weight=DEFAULT_TIE_BREAKER_WEIGHT):
    specs = [_spec("gain", 40.0, reward_type="relative-absolute"),
             _spec("ugf", 100.0, reward_type="relative-absolute")]
    s = _SingleObjectiveScorer(specs, strategy)
    s.optimizer_config.tie_breaker = tie_breaker
    s.optimizer_config.tie_breaker_weight = weight
    return s


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_scorer_default_is_unchanged_by_the_new_key(strategy):
    """A stand-in config that predates the key (no attribute at all) must score exactly as before
    — the API's score preview builds one of those."""
    perf = {"gain": np.float64(55.0), "ugf": np.float64(140.0)}
    legacy = _SingleObjectiveScorer(
        [_spec("gain", 40.0, reward_type="relative-absolute"),
         _spec("ugf", 100.0, reward_type="relative-absolute")], strategy)
    assert not hasattr(legacy.optimizer_config, "tie_breaker")
    assert legacy.compute_fitness(perf)[0] == _scorer(strategy).compute_fitness(perf)[0]


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
def test_the_scorer_breaks_the_tie_on_the_declared_objectives(strategy):
    """End to end: two designs that both MEET every spec, one comfortably better. Flat by default;
    correctly ordered with the flag on."""
    good = {"gain": np.float64(55.0), "ugf": np.float64(140.0)}
    ok = {"gain": np.float64(41.0), "ugf": np.float64(101.0)}

    flat = _scorer(strategy)
    assert flat.compute_fitness(good)[0] == flat.compute_fitness(ok)[0] == pytest.approx(0.0)

    on = _scorer(strategy, tie_breaker="objective")
    assert on.compute_fitness(good)[0] > on.compute_fitness(ok)[0] > 0


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
def test_the_scorer_still_ranks_every_feasible_design_above_an_infeasible_one(strategy):
    on = _scorer(strategy, tie_breaker="objective")
    barely_feasible = on.compute_fitness({"gain": np.float64(39.0), "ugf": np.float64(99.0)})[0]
    infeasible = on.compute_fitness({"gain": np.float64(38.0), "ugf": np.float64(99.0)})[0]
    assert infeasible < 0 <= barely_feasible


def test_the_fit_summary_is_unaffected_by_the_tie_breaker():
    """Per-spec diagnostics must stay comparable across arms — only the SCALAR moves."""
    perf = {"gain": np.float64(55.0), "ugf": np.float64(140.0)}
    off = _scorer("weighted_sum").compute_fitness(perf)[1]
    on = _scorer("weighted_sum", tie_breaker="objective").compute_fitness(perf)[1]
    assert on.keys() == off.keys()
    for k in on:
        assert on[k]["score"] == pytest.approx(off[k]["score"])


# =========================================================== 9. the opt-in margin-aware reward
# A design that merely CLEARS its specs at the nominal corner is not a design that survives
# silicon. TCAS-2026 ledger E-057 / cross-mining E-058 re-simulated 246 `tt`-feasible best-power
# designs at all five MOS corners: only 98 passed everywhere, and the pass rate rose MONOTONICALLY
# with the design's WORST `tt` spec margin (23 % -> 67 % across margin bins, p = 0.001). The only
# campaign arm that was 100 % corner-robust AND transient-stable was the highest-margin one.
#
# So `margin_reward_weight > 0` pays a FEASIBLE design for `clip(min_i margin_i, 0, cap)`. Two
# organising risks, same shape as section 8's:
#   (a) it is an additive key on the scorer every historical checkpoint came from, so weight 0 must
#       be bit-identical — checked against the section-8 oracle over randomized cases;
#   (b) `min` (not mean) and the clip are the DESIGN, not an implementation detail: a mean lets one
#       enormous headroom paper over the one spec about to fail at `ss`, and an unclipped term lets
#       a roomy spec out-vote the declared objectives. Both are pinned below.
_MW = dict(weight=0.5)


def _mr(scores, strategy, margins=None, weight=0.0, clip=DEFAULT_MARGIN_REWARD_CLIP,
        tie_breaker=None, tie_breaker_weight=DEFAULT_TIE_BREAKER_WEIGHT, params=None):
    return aggregate_spec_scores({k: F(v) for k, v in scores.items()}, strategy, params,
                                 tie_breaker=tie_breaker, tie_breaker_weight=tie_breaker_weight,
                                 spec_margins=margins, margin_reward_weight=weight,
                                 margin_reward_clip=clip)


# ---- bit-identity of the default
@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_margin_reward_weight_zero_is_bit_identical_to_before_the_key_existed(strategy):
    """Not `approx`. Weight 0 must reproduce the pre-key formulas exactly, and passing margins
    with weight 0 must be indistinguishable from passing none at all."""
    rng = np.random.default_rng(20260823)
    cases = [{}, {"a": 0.0}, {"a": 5.0, "b": 2.0}, {"a": -3.0, "b": 7.0},
             {"a": -float(EPSILON) / 2, "b": 4.0}, {"a": -float(MAX_PENALTY), "b": 9.0}]
    cases += [{f"s{i}": float(v) for i, v in enumerate(rng.uniform(-10, 10, size=5))}
              for _ in range(100)]
    for scores in cases:
        margins = {k: float(rng.uniform(-2, 2)) for k in scores}
        expected = _pre_tie_breaker_oracle(scores, strategy)
        assert _agg(scores, strategy) == expected, (strategy, scores)
        assert _mr(scores, strategy) == expected, (strategy, scores)
        assert _mr(scores, strategy, margins=margins, weight=0.0) == expected, (strategy, scores)


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_no_margins_at_all_is_a_no_op_even_at_a_positive_weight(strategy):
    """A project with only EXACT-goal specs produces no margins; the term must vanish, not crash."""
    scores = {"a": 3.0, "b": 1.0}
    assert _mr(scores, strategy, margins=None, **_MW) == _agg(scores, strategy)
    assert _mr(scores, strategy, margins={}, **_MW) == _agg(scores, strategy)
    assert _mr(scores, strategy, margins={"a": None}, **_MW) == _agg(scores, strategy)


# ---- monotonicity: more worst-margin is worth more
@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_a_larger_worst_margin_earns_a_larger_reward_at_fixed_feasibility(strategy):
    """The claim the feature exists to make. Feasibility (the scores) is held FIXED so only the
    margin moves — otherwise the base score would confound the comparison."""
    scores = {"gain": 3.0, "power": 1.0}
    prev = None
    for worst in (0.0, 0.1, 0.25, 0.5, 0.75):
        got = _mr(scores, strategy, margins={"gain": worst, "power": worst + 0.3}, **_MW)
        if prev is not None:
            assert got > prev, (strategy, worst)
        prev = got


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_term_is_the_worst_margin_not_the_mean(strategy):
    """`min`, deliberately: E-058 measured corner survival against the WORST margin. A mean would
    rank the design with one enormous headroom and one hair-thin spec ABOVE the balanced one."""
    base = _agg({"a": 2.0, "b": 2.0}, strategy)
    lopsided = _mr({"a": 2.0, "b": 2.0}, strategy, margins={"a": 0.01, "b": 5.0}, **_MW)
    balanced = _mr({"a": 2.0, "b": 2.0}, strategy, margins={"a": 0.4, "b": 0.4}, **_MW)
    assert balanced > lopsided
    # and the lopsided design is paid for its 0.01, not for the mean of 2.5
    assert float(lopsided - base) == pytest.approx(0.5 * 0.01)


# ---- the clip
@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_reward_saturates_at_the_clip(strategy):
    base = _agg({"a": 2.0}, strategy)
    at_cap = _mr({"a": 2.0}, strategy, margins={"a": 1.0}, clip=1.0, **_MW)
    way_over = _mr({"a": 2.0}, strategy, margins={"a": 1e6}, clip=1.0, **_MW)
    assert at_cap == way_over
    assert float(at_cap - base) == pytest.approx(0.5 * 1.0)


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_clip_bounds_the_term_far_below_max_reward(strategy):
    """The point of bounding it: a merely-roomy design must never approach the best score the
    scorer can emit, or it becomes a permanent global best."""
    huge = _mr({"a": 2.0}, strategy, margins={"a": 1e9}, weight=1.0,
               clip=DEFAULT_MARGIN_REWARD_CLIP)
    assert float(huge) - float(_agg({"a": 2.0}, strategy)) <= DEFAULT_MARGIN_REWARD_CLIP


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_a_negative_worst_margin_is_clipped_to_zero_not_a_penalty(strategy):
    """Tolerance-band float dust on a just-satisfied spec must not quietly PENALIZE a feasible
    design — the term is a reward, and its floor is 0."""
    base = _agg({"a": 0.0, "b": 1.0}, strategy)
    assert _mr({"a": 0.0, "b": 1.0}, strategy, margins={"a": -1e-9, "b": 2.0}, **_MW) == base


# ---- the infeasible region is untouched
@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_an_infeasible_trial_is_unaffected_by_the_margin_reward(strategy):
    """Feasibility still strictly dominates: the term is gated on the SAME `> -EPSILON` test that
    already gates `feasibility_reward`'s reward branch."""
    scores = {"a": -3.0, "b": 7.0}
    assert _mr(scores, strategy, margins={"b": 5.0}, **_MW) == _agg(scores, strategy)


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_margin_reward_cannot_lift_an_infeasible_trial_above_a_feasible_one(strategy):
    infeasible = _mr({"a": -0.001, "b": 5.0}, strategy, margins={"a": 9.0, "b": 9.0},
                     weight=1e3, clip=1e3)
    feasible = _mr({"a": 0.0, "b": 0.0}, strategy, margins={"a": 0.0, "b": 0.0}, **_MW)
    assert infeasible < 0 <= feasible


# ---- interaction with the tie-breaker
def test_the_margin_reward_is_NOT_a_no_op_under_feasibility_reward():
    """The deliberate difference from `tie_breaker`. `feasibility_reward`'s feasible branch already
    IS the declared-objective reward, so re-adding it (tie_breaker) is pointless; the margin term
    pays for robustness geometry the objectives do not express, so it applies there too."""
    scores = {"a": 3.0, "b": 1.0}
    assert _tb(scores, "feasibility_reward", tie_breaker="objective") == _agg(
        scores, "feasibility_reward")
    assert _mr(scores, "feasibility_reward", margins={"a": 0.5, "b": 0.5}, **_MW) > _agg(
        scores, "feasibility_reward")


@pytest.mark.parametrize("strategy", ("weighted_sum", "chebyshev"))
def test_both_terms_on_compose_additively_in_the_documented_order(strategy):
    """`F = F_base + w_tb*R + w_m*clip(margin)` — pinned as an exact identity so the order can
    never silently become multiplicative or exclusive."""
    scores = {"gain": 12.0, "power": 3.0}
    margins = {"gain": 0.4, "power": 0.6}
    base = _agg(scores, strategy)
    tb_only = _tb(scores, strategy, tie_breaker="objective", tie_breaker_weight=1e-6)
    m_only = _mr(scores, strategy, margins=margins, **_MW)
    both = _mr(scores, strategy, margins=margins, tie_breaker="objective",
               tie_breaker_weight=1e-6, **_MW)
    assert float(both) == pytest.approx(float(base) + (float(tb_only) - float(base))
                                        + (float(m_only) - float(base)))


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_monotone_non_decreasing_with_the_margin_reward_on(strategy):
    """Section 4's invariant must survive the new term: improving a spec raises its score AND
    (weakly) its margin, so the aggregate can only go up."""
    rng = np.random.default_rng(7)
    for _ in range(200):
        scores = {f"s{i}": float(v) for i, v in enumerate(rng.uniform(-4, 4, size=4))}
        margins = {k: float(v) / 4.0 for k, v in scores.items()}
        bumped_s = dict(scores)
        bumped_m = dict(margins)
        key = "s2"
        bumped_s[key] += 1.0
        bumped_m[key] += 0.25
        before = _mr(scores, strategy, margins=margins, **_MW)
        after = _mr(bumped_s, strategy, margins=bumped_m, **_MW)
        assert after >= before - 1e-12, (strategy, scores, margins)


# ---- validation
@pytest.mark.parametrize("weight", [-1.0, -1e-9, float("nan"), float("inf")])
def test_a_degenerate_margin_reward_weight_is_rejected(weight):
    with pytest.raises(ValueError, match="margin_reward_weight"):
        resolve_margin_reward(weight, None)


@pytest.mark.parametrize("clip", [0.0, -1.0, float("nan"), float("inf")])
def test_a_degenerate_margin_reward_clip_is_rejected(clip):
    with pytest.raises(ValueError, match="margin_reward_clip"):
        resolve_margin_reward(1.0, clip)


def test_resolve_margin_reward_defaults_are_off_and_unit_clip():
    assert resolve_margin_reward(None, None) == (DEFAULT_MARGIN_REWARD_WEIGHT,
                                                 DEFAULT_MARGIN_REWARD_CLIP)
    assert DEFAULT_MARGIN_REWARD_WEIGHT == 0.0


def test_optimizer_config_defaults_leave_the_margin_reward_off():
    cfg = _config()
    assert cfg.margin_reward_weight == DEFAULT_MARGIN_REWARD_WEIGHT == 0.0
    assert cfg.margin_reward_clip == DEFAULT_MARGIN_REWARD_CLIP


@pytest.mark.parametrize("bad,match", [({"margin_reward_weight": -1.0}, "margin_reward_weight"),
                                       ({"margin_reward_clip": 0.0}, "margin_reward_clip")])
def test_optimizer_config_validates_the_margin_reward_at_load(bad, match):
    with pytest.raises(ValueError, match=match):
        _config(**bad)


def test_optimizer_config_keeps_an_explicit_margin_reward():
    cfg = _config(margin_reward_weight=0.25, margin_reward_clip=2.0)
    assert cfg.margin_reward_weight == 0.25
    assert cfg.margin_reward_clip == 2.0


# ---- the margin helper itself
def test_normalized_margin_uses_the_reward_boundary_and_the_spec_range():
    """NOT `(value - target)/|target|`: the platform measures from the tolerance-adjusted boundary
    and normalizes by `range`. `/|target|` would divide by zero on a legitimate `target: 0` spec
    and collapse every `log_scale` spec."""
    exceed = _spec("gain", 40.0, goal="exceed")          # range 10, tolerance 1 -> boundary 39
    assert float(normalized_spec_margin(49.0, exceed)) == pytest.approx(1.0)
    assert float(normalized_spec_margin(39.0, exceed)) == pytest.approx(0.0)
    assert float(normalized_spec_margin(29.0, exceed)) == pytest.approx(-1.0)

    mini = _spec("power", 40.0, goal="minimize")          # boundary 41
    assert float(normalized_spec_margin(31.0, mini)) == pytest.approx(1.0)
    assert float(normalized_spec_margin(41.0, mini)) == pytest.approx(0.0)
    assert float(normalized_spec_margin(51.0, mini)) == pytest.approx(-1.0)


def test_normalized_margin_agrees_in_sign_with_the_penalty_the_scorer_computes():
    """The margin and the scorer's own pass/fail verdict must never disagree — a positive margin on
    a spec the scorer is penalizing would reward a violating design."""
    scorer = _Scorer([_spec("gain", 40.0)])
    for value in (20.0, 38.5, 39.0, 39.5, 60.0):
        margin = float(normalized_spec_margin(value, _spec("gain", 40.0)))
        score = float(scorer.compute_fitness({"gain": np.float64(value)})[0])
        assert (margin >= 0) == (score >= 0), (value, margin, score)


def test_normalized_margin_is_none_for_an_exact_goal_spec():
    """EXACT is two-sided: ±x is neither headroom nor a shortfall, and it earns no reward today."""
    assert normalized_spec_margin(40.0, _spec("vos", 40.0, goal="exact")) is None


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_normalized_margin_is_none_for_an_unscoreable_reading(bad):
    assert normalized_spec_margin(bad, _spec("gain", 40.0)) is None


def test_normalized_margin_is_none_for_a_non_positive_log_scale_reading():
    assert normalized_spec_margin(0.0, _spec("power", 1e-3, goal="minimize", log_scale=True,
                                             range=1e-3, tolerance=1e-4)) is None


def test_normalized_margin_uses_decade_space_under_log_scale():
    """A log-scale spec's margin must be measured in DECADES over a decade-space range — the same
    fix the penalty path needed. A decade of headroom on a spec whose linear `range` is one decade
    wide is ~1.0, not ~0."""
    spec = _spec("gbw", 1e6, goal="exceed", log_scale=True, range=9e6, tolerance=1e5)
    ten_x = float(normalized_spec_margin(1e7, spec))
    assert 0.9 < ten_x < 1.1
    assert float(normalized_spec_margin(1e6, spec)) < ten_x


# ---- through the real scorer
def _margin_scorer(strategy, weight=0.0, clip=DEFAULT_MARGIN_REWARD_CLIP):
    specs = [_spec("gain", 40.0, reward_type="relative-absolute"),
             _spec("ugf", 100.0, reward_type="relative-absolute")]
    s = _SingleObjectiveScorer(specs, strategy)
    s.optimizer_config.tie_breaker = None
    s.optimizer_config.tie_breaker_weight = DEFAULT_TIE_BREAKER_WEIGHT
    s.optimizer_config.margin_reward_weight = weight
    s.optimizer_config.margin_reward_clip = clip
    return s


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_scorer_default_is_unchanged_by_the_margin_key(strategy):
    """A config stand-in predating the key (no attribute at all) must score exactly as before."""
    perf = {"gain": np.float64(55.0), "ugf": np.float64(140.0)}
    legacy = _SingleObjectiveScorer(
        [_spec("gain", 40.0, reward_type="relative-absolute"),
         _spec("ugf", 100.0, reward_type="relative-absolute")], strategy)
    assert not hasattr(legacy.optimizer_config, "margin_reward_weight")
    assert legacy.compute_fitness(perf)[0] == _margin_scorer(strategy).compute_fitness(perf)[0]


@pytest.mark.parametrize("strategy", SPEC_SCORE_AGGREGATORS)
def test_the_scorer_prefers_the_higher_margin_design_end_to_end(strategy):
    """The E-057 claim, through the real scorer: two designs, both feasible, one with more headroom
    on its WORST spec. Off, `weighted_sum`/`chebyshev` tie them exactly; on, the roomier wins."""
    roomy = {"gain": np.float64(48.0), "ugf": np.float64(108.0)}
    thin = {"gain": np.float64(39.5), "ugf": np.float64(99.5)}
    on = _margin_scorer(strategy, weight=0.5)
    assert on.compute_fitness(roomy)[0] > on.compute_fitness(thin)[0]


def test_the_scorer_leaves_the_fit_summary_untouched_by_the_margin_reward():
    """Per-spec diagnostics must stay comparable across arms — only the SCALAR moves."""
    perf = {"gain": np.float64(55.0), "ugf": np.float64(140.0)}
    off = _margin_scorer("weighted_sum").compute_fitness(perf)[1]
    on = _margin_scorer("weighted_sum", weight=0.5).compute_fitness(perf)[1]
    assert on.keys() == off.keys()
    for k in on:
        assert set(on[k]) == set(off[k])
        assert on[k]["score"] == pytest.approx(off[k]["score"])


def test_the_scorer_skips_the_margin_math_entirely_when_the_weight_is_zero(monkeypatch):
    """Bit-identity by construction, not by luck: at weight 0 the default path must never even
    call the margin helper."""
    import spicexplorer.optimization.base as base_mod

    calls = []
    monkeypatch.setattr(base_mod, "normalized_spec_margin",
                        lambda *a, **k: calls.append(a) or 0.0)
    _margin_scorer("feasibility_reward").compute_fitness(
        {"gain": np.float64(55.0), "ugf": np.float64(140.0)})
    assert calls == []
    _margin_scorer("feasibility_reward", weight=0.5).compute_fitness(
        {"gain": np.float64(55.0), "ugf": np.float64(140.0)})
    assert len(calls) == 2
