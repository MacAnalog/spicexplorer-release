"""`relative-gaussian` error type: kernel shape, parameter plumbing, and aggregation behaviour.

Added alongside the error type itself. Three things are being pinned down:

1. **The kernel is the shape we claim it is.** Bounded in [0, 1) like `relative-sigmoid`, but
   with a slope that VANISHES at the target instead of being maximal there. That contrast is the
   entire reason the error type exists — it is the controlled comparison for whether the benefit
   of `relative-sigmoid` comes from *bounding* the error or from *smoothing* it. A test that only
   checked "penalty grows with error" would pass for either shape and prove nothing.

2. **`sigma` actually reaches the kernel.** It is swept by the study, and the dispatch table holds
   pure `(curr, target, coeff)` callables, so the parameter needed a seam (`TargetSpec.error_params`
   -> `compute_error(error_params=...)`). An unswept parameter silently pinned at its default
   would invalidate the sweep while looking like it ran.

3. **Aggregation still behaves as documented** with a bounded error type in play — the
   constraint-first switch, and the corner reducer's failing-subset partition.

No SPICE, no PDK. The scoring methods read only their arguments, so they are invoked unbound.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import numpy as np
import pytest
from spicexplorer.core.domains import Error_Types, TargetSpec
from spicexplorer.core.utils import (
    ERROR_COMPUTE_FUNCTIONS,
    ERROR_SHAPE_PARAMS,
    aggregate_corner_scores,
    compute_error,
    compute_relative_gaussian_error,
    resolve_error_params,
)
from spicexplorer.optimization.base import Spice_Constraint_Satisfaction

GAUSS = Error_Types.RELATIVE_GAUSSIAN


def _penalty(curr_val, spec):
    return Spice_Constraint_Satisfaction.compute_constraint_violation_penalty_for_spec(
        cast("Spice_Constraint_Satisfaction", None), np.float64(curr_val), spec)


def _spec(**kw):
    base = dict(name="gain", testbench="tb", target=40.0, goal="exceed", sim_type="ac",
                range=10.0, tolerance=0.0, error_type="relative-gaussian")
    base.update(kw)
    return TargetSpec(**base)


class _Scorer:
    """Minimal stand-in exposing only what `compute_fitness` reads off `self`."""

    def __init__(self, specs):
        self.target_specs = SimpleNamespace(enabled_targets=lambda: specs)
        self.verbose = False

    compute_fitness = Spice_Constraint_Satisfaction.compute_fitness
    compute_fitness_for_spec = Spice_Constraint_Satisfaction.compute_fitness_for_spec
    compute_constraint_violation_penalty_for_spec = (
        Spice_Constraint_Satisfaction.compute_constraint_violation_penalty_for_spec)


# --------------------------------------------------------------------------- 1. kernel shape
def test_zero_error_at_target():
    assert compute_relative_gaussian_error(np.float64(40.0), np.float64(40.0), np.float64(10.0)) == 0.0


def test_bounded_in_unit_interval_and_saturates():
    """Bounded like relative-sigmoid: no single metric can dominate the aggregate."""
    for d in (0.0, 0.5, 1.0, 3.0, 10.0, 1e3, 1e12):
        e = compute_relative_gaussian_error(np.float64(d), np.float64(0.0), np.float64(1.0))
        assert 0.0 <= e <= 1.0, d
        assert np.isfinite(e), d
    # a wildly out-of-range metric saturates rather than overflowing
    assert compute_relative_gaussian_error(np.float64(1e30), np.float64(0.0), np.float64(1.0)) == pytest.approx(1.0)


def test_saturates_to_exactly_one_far_sooner_than_sigmoid():
    """Documents where the landscape goes FLAT — a real constraint on choosing sigma.

    In float64, 1 - exp(-d^2/2) rounds to exactly 1.0 once d exceeds ~9, so past that the
    optimizer sees no gradient whatsoever. relative-sigmoid decays only exponentially in d and
    stays below 1.0 out to d ~ 36. Not a rounding curiosity: with sigma = 1 a metric 10
    range-units off target is indistinguishable from one a million units off.
    """
    from spicexplorer.core.utils import compute_relative_sigmoid_error
    def at(d):
        return compute_relative_gaussian_error(np.float64(d), np.float64(0.0), np.float64(1.0))

    assert at(8.0) < 1.0                       # still has gradient
    assert at(10.0) == 1.0                     # fully saturated
    assert compute_relative_sigmoid_error(np.float64(10.0), np.float64(0.0), np.float64(1.0)) < 1.0
    # a larger sigma pushes the flat region out, which is how to keep gradient far from target
    assert compute_relative_gaussian_error(np.float64(10.0), np.float64(0.0), np.float64(1.0), sigma=4.0) < 1.0


def test_monotone_and_symmetric_in_the_normalized_error():
    errs = [compute_relative_gaussian_error(np.float64(d), np.float64(0.0), np.float64(1.0))
            for d in (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)]
    assert errs == sorted(errs)
    assert len(set(errs)) == len(errs)
    for d in (0.3, 1.7, 5.0):
        assert (compute_relative_gaussian_error(np.float64(d), np.float64(0.0), np.float64(1.0))
                == pytest.approx(compute_relative_gaussian_error(np.float64(-d), np.float64(0.0), np.float64(1.0))))


def test_matches_the_closed_form():
    """Pin the actual formula, not just its qualitative shape."""
    for d, sigma in ((1.0, 1.0), (2.0, 1.0), (1.0, 0.5), (3.0, 2.0)):
        got = compute_relative_gaussian_error(np.float64(d), np.float64(0.0), np.float64(1.0), sigma=sigma)
        assert got == pytest.approx(1.0 - np.exp(-(d ** 2) / (2 * sigma ** 2)))
    # one decimal anchor so a sign/factor slip cannot hide behind the same expression
    assert compute_relative_gaussian_error(np.float64(1.0), np.float64(0.0), np.float64(1.0), sigma=1.0) \
        == pytest.approx(0.3934693402873666)


def test_slope_vanishes_at_target_unlike_sigmoid():
    """THE defining contrast. Sigmoid is steepest at the target; gaussian is flattest there.

    If this ever inverts, the head-to-head comparison the error type exists for is meaningless.
    """
    from spicexplorer.core.utils import compute_relative_sigmoid_error
    h = 1e-6
    g_slope = compute_relative_gaussian_error(np.float64(h), np.float64(0.0), np.float64(1.0)) / h
    s_slope = compute_relative_sigmoid_error(np.float64(h), np.float64(0.0), np.float64(1.0)) / h
    assert g_slope == pytest.approx(0.0, abs=1e-5)
    assert s_slope > 0.4                      # sigmoid derivative at 0 is 1/2
    assert g_slope < s_slope


def test_smaller_sigma_penalizes_a_near_miss_harder():
    d = np.float64(0.5)
    tight = compute_relative_gaussian_error(d, np.float64(0.0), np.float64(1.0), sigma=0.25)
    loose = compute_relative_gaussian_error(d, np.float64(0.0), np.float64(1.0), sigma=4.0)
    assert tight > loose


@pytest.mark.parametrize("sigma", [0.0, -1.0, float("nan"), float("inf")])
def test_rejects_bad_sigma(sigma):
    with pytest.raises(ValueError):
        compute_relative_gaussian_error(np.float64(1.0), np.float64(0.0), np.float64(1.0), sigma=sigma)


# --------------------------------------------------------------------------- 2. plumbing
def test_declared_and_implemented():
    """Guards the trap two Reward_Types already fall into: in the enum, absent from the dict.

    Those raise KeyError mid-optimization instead of failing validation at load.
    """
    assert Error_Types("relative-gaussian") is GAUSS
    assert GAUSS in ERROR_COMPUTE_FUNCTIONS
    assert set(ERROR_COMPUTE_FUNCTIONS) >= {e for e in Error_Types}


def test_compute_error_routes_and_forwards_sigma():
    direct = compute_relative_gaussian_error(np.float64(41.0), np.float64(40.0), np.float64(10.0), sigma=0.5)
    routed = compute_error(np.float64(41.0), np.float64(40.0), GAUSS, np.float64(10.0), error_params={"sigma": 0.5})
    assert routed == pytest.approx(direct)
    # and the default is genuinely applied when nothing is passed
    assert compute_error(np.float64(41.0), np.float64(40.0), GAUSS, np.float64(10.0)) == pytest.approx(
        compute_relative_gaussian_error(np.float64(41.0), np.float64(40.0), np.float64(10.0), sigma=1.0))


def test_sigma_actually_changes_the_routed_result():
    """A swept parameter that never reaches the kernel would invalidate the sweep silently."""
    vals = {s: compute_error(np.float64(45.0), np.float64(40.0), GAUSS, np.float64(10.0),
                             error_params={"sigma": s}) for s in (0.25, 1.0, 4.0)}
    assert len(set(vals.values())) == 3
    assert vals[0.25] > vals[1.0] > vals[4.0]


def test_unknown_error_param_is_rejected():
    with pytest.raises(ValueError, match="Unknown error_params"):
        resolve_error_params(GAUSS, {"sgima": 1.0})


def test_error_params_ignored_for_types_that_take_none():
    assert resolve_error_params(Error_Types.RELATIVE_ABSOLUTE, {"sigma": 2.0}) == {}
    # and passing them does not break the call
    assert compute_error(np.float64(41.0), np.float64(40.0), Error_Types.RELATIVE_ABSOLUTE,
                         np.float64(10.0), error_params={"sigma": 2.0}) == pytest.approx(0.1)


@pytest.mark.parametrize("etype", [e for e in Error_Types if e not in ERROR_SHAPE_PARAMS])
def test_existing_error_types_are_unchanged(etype):
    """Regression: the new keyword must not perturb any error type that takes no shape params.

    Driven off `ERROR_SHAPE_PARAMS` rather than an explicit exclusion list, so a later shaped
    error type is covered by its own suite instead of silently failing the `is None` assertion
    here (`relative-adaptive` was the first to hit that)."""
    coeff = np.float64(10.0) if etype.is_relative() else None
    before = ERROR_COMPUTE_FUNCTIONS[etype](np.float64(41.0), np.float64(40.0), *( [coeff] if coeff else [] ))
    after = compute_error(np.float64(41.0), np.float64(40.0), etype, coeff)
    assert after == pytest.approx(before)
    assert ERROR_SHAPE_PARAMS.get(etype) is None


# --------------------------------------------------------------------------- 3. load validation
def test_targetspec_accepts_and_coerces_sigma():
    spec = _spec(error_params={"sigma": "0.5"})
    assert spec.error_params["sigma"] == pytest.approx(0.5)
    assert isinstance(spec.error_params["sigma"], float)


@pytest.mark.parametrize("bad", [0, -1, "abc", float("nan")])
def test_targetspec_rejects_bad_sigma_at_load(bad):
    """Fail at config load, not thousands of evaluations into a run."""
    with pytest.raises(ValueError):
        _spec(error_params={"sigma": bad})


def test_targetspec_rejects_unknown_error_param_at_load():
    with pytest.raises(ValueError):
        _spec(error_params={"with": 1.0})


def test_spec_without_error_params_is_untouched():
    assert _spec().error_params is None


# --------------------------------------------------------------------------- 4. scoring
def test_penalty_is_zero_when_the_spec_is_met():
    assert _penalty(45.0, _spec()) == 0.0        # exceed 40, measured 45
    assert _penalty(40.0, _spec()) == 0.0        # exactly at target


def test_penalty_is_bounded_by_the_weight():
    """A bounded error type means one violated spec contributes at most `weight`."""
    spec = _spec(weight=1.0)
    for measured in (39.0, 30.0, 0.0, -1e9):
        assert 0.0 <= _penalty(measured, spec) <= 1.0


def test_outlier_cannot_dominate_the_way_relative_absolute_does():
    """The paper's 'outlier dominance' failure, and the reason for a bounded shape.

    A wildly-off metric under relative-absolute swamps a near-miss on another spec; under
    relative-gaussian both saturate, so the near-miss stays visible to the optimizer.
    """
    near_miss, blowup = 35.0, -1e6
    lin_near = _penalty(near_miss, _spec(error_type="relative-absolute"))
    lin_far = _penalty(blowup, _spec(error_type="relative-absolute"))
    g_near = _penalty(near_miss, _spec())
    g_far = _penalty(blowup, _spec())
    assert lin_near > 0 and g_near > 0       # guard: the near miss must actually be penalized
    assert g_far <= 1.0                      # bounded, whatever the metric does

    # The claim is RELATIVE, so assert it relatively rather than against a magic threshold:
    # under linear the outlier outweighs the near-miss by ~5 orders of magnitude, so the
    # near-miss is invisible in the sum; under gaussian the two stay within ~1.5 orders.
    linear_dominance = lin_far / lin_near
    gaussian_dominance = g_far / g_near
    assert linear_dominance > 1e4
    assert gaussian_dominance < linear_dominance / 1e3

    # Stated the way it matters to the optimizer: the near-miss's share of the total penalty.
    assert lin_near / (lin_near + lin_far) < 1e-4      # linear: drowned out
    assert g_near / (g_near + g_far) > 0.04            # gaussian: still steers the search


def test_tolerance_is_honoured_exactly_as_authored():
    """Regression for a trap this suite used to DOCUMENT rather than fix.

    `tolerance` was falsy-checked rather than None-checked, so `tolerance: 0` — the natural way to
    write "no dead band" — was discarded and replaced by 5 % of target. An author who wrote 0 and
    expected an exact constraint silently got a 2.0-wide band on a target of 40, and nothing about
    the run looked wrong. Now every authored value is honoured verbatim, zero included, and an
    OMITTED tolerance defaults to zero rather than inventing a 5 % relaxation.
    """
    assert _spec(tolerance=0.0).tolerance == pytest.approx(0.0)
    assert _spec(tolerance=None).tolerance == pytest.approx(0.0)   # the default is exact
    assert _spec(tolerance=0.5).tolerance == pytest.approx(0.5)
    # consequence: a metric off target now scores a real penalty instead of hiding in a band
    assert _penalty(39.0, _spec(tolerance=0.0)) > 0.0
    assert _penalty(39.0, _spec(tolerance=2.0)) == 0.0


# --------------------------------------------------------------------------- 5. aggregation
def test_reward_is_suppressed_while_any_spec_is_violated():
    """Constraint-first aggregation: penalties alone until every spec passes."""
    specs = [_spec(name="gain", target=40.0), _spec(name="ugf", target=100.0)]
    total_bad, summary = _Scorer(specs).compute_fitness({"gain": 45.0, "ugf": 50.0})
    assert total_bad < 0                                  # the violated spec sets the score
    assert summary["gain"]["score"] == 0.0                # satisfied spec contributes nothing
    total_ok, _ = _Scorer(specs).compute_fitness({"gain": 45.0, "ugf": 120.0})
    assert total_ok == 0.0                                # all constraints met, no reward configured
    assert total_ok > total_bad


def test_weights_scale_the_penalty():
    heavy = _Scorer([_spec(weight=4.0)]).compute_fitness({"gain": 35.0})[0]
    light = _Scorer([_spec(weight=1.0)]).compute_fitness({"gain": 35.0})[0]
    assert heavy == pytest.approx(4.0 * light)


def test_missing_metric_outranks_any_bounded_violation():
    """A failed sim must dominate a converged-but-bad design, even against a bounded error type.

    This is the carve-out that was removed for relative-sigmoid; relative-gaussian is bounded
    the same way and must inherit the same treatment rather than reintroduce the bug.
    """
    worst_converged = _Scorer([_spec()]).compute_fitness({"gain": -1e9})[0]
    missing = _Scorer([_spec()]).compute_fitness({})[0]
    diverged = _Scorer([_spec()]).compute_fitness({"gain": np.nan})[0]
    assert missing < worst_converged
    assert diverged < worst_converged
    assert missing == diverged


# --- corner reduction -------------------------------------------------------
def test_corner_failing_subset_takes_precedence():
    """A comfortably-passing corner must not out-vote a failing one (the masking bug)."""
    scores = {"tt": np.float64(5.0), "ss": np.float64(-2.0), "ff": np.float64(9.0)}
    assert aggregate_corner_scores(scores, "mean") < 0
    assert aggregate_corner_scores(scores, "sum") == pytest.approx(-2.0)
    assert aggregate_corner_scores(scores, "min") == pytest.approx(-2.0)


def test_corner_mean_divides_by_the_total_corner_count():
    """AGG-2 monotonicity: improving a marginal corner must never make the aggregate worse."""
    before = aggregate_corner_scores({"a": np.float64(-10.0), "b": np.float64(-2.0)}, "mean")
    after = aggregate_corner_scores({"a": np.float64(-10.0), "b": np.float64(1.0)}, "mean")
    assert before == pytest.approx(-6.0)
    assert after == pytest.approx(-5.0)
    assert after > before


def test_corner_all_passing_aggregates_rewards():
    scores = {"tt": np.float64(4.0), "ss": np.float64(2.0)}
    assert aggregate_corner_scores(scores, "min") == pytest.approx(2.0)
    assert aggregate_corner_scores(scores, "mean") == pytest.approx(3.0)
    assert aggregate_corner_scores(scores, "sum") == pytest.approx(6.0)


def test_corner_rejects_unknown_strategy_and_empty_input():
    with pytest.raises(ValueError):
        aggregate_corner_scores({"tt": np.float64(1.0)}, "cvar")
    with pytest.raises(ValueError):
        aggregate_corner_scores({}, "mean")


# --------------------------------------------------------------------------- 6. sigmoid `alpha`
# `alpha` (paper Eq.2's saturation rate) was hardcoded at 1.0 until it became a swept parameter.
# It is added here rather than in its own file because every test below is a direct contrast
# against the gaussian's `sigma` — the two are the shaping knobs the study sweeps against each
# other, and the point is that they behave differently.
SIGMOID = Error_Types.RELATIVE_SIGMOID


def test_sigmoid_alpha_defaults_to_the_previously_hardcoded_value():
    """Regression: every spec authored before `alpha` existed must score identically."""
    from spicexplorer.core.utils import compute_relative_sigmoid_error
    for d in (0.0, 0.3, 1.0, 5.0, 50.0):
        legacy = 2.0 / (1.0 + np.exp(-d)) - 1.0
        assert compute_relative_sigmoid_error(np.float64(d), np.float64(0.0), np.float64(1.0)) == pytest.approx(legacy)
    assert ERROR_SHAPE_PARAMS[SIGMOID] == {"alpha": 1.0}


def test_sigmoid_alpha_actually_changes_the_routed_result():
    """The whole reason to add it: an unswept parameter invalidates the sweep silently."""
    vals = {a: compute_error(np.float64(41.0), np.float64(40.0), SIGMOID, np.float64(10.0),
                             error_params={"alpha": a}) for a in (0.25, 1.0, 4.0)}
    assert len(set(vals.values())) == 3
    assert vals[0.25] < vals[1.0] < vals[4.0]     # larger alpha saturates sooner => harsher


def test_sigmoid_stays_bounded_and_finite_for_any_alpha():
    for a in (0.01, 1.0, 1e3):
        for d in (0.0, 1.0, 1e6, 1e30):
            e = compute_error(np.float64(d), np.float64(0.0), SIGMOID, np.float64(1.0),
                              error_params={"alpha": a})
            assert 0.0 <= e <= 1.0 and np.isfinite(e), (a, d)


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf")])
def test_sigmoid_rejects_bad_alpha_at_load(bad):
    with pytest.raises(ValueError, match="alpha"):
        _spec(error_type="relative-sigmoid", error_params={"alpha": bad})


def test_sigmoid_alpha_is_coerced_from_a_yaml_string():
    spec = _spec(error_type="relative-sigmoid", error_params={"alpha": "0.5"})
    assert spec.error_params["alpha"] == pytest.approx(0.5)


def test_alpha_and_sigma_are_not_interchangeable():
    """Both are "width" knobs but shape the near-target region differently: at a small miss the
    sigmoid is already steep while the gaussian is still flat, which is the contrast the study
    is built to measure. Equal parameter values must NOT give equal penalties."""
    d, coeff = np.float64(1.0), np.float64(10.0)
    sig = compute_error(d, np.float64(0.0), SIGMOID, coeff, error_params={"alpha": 1.0})
    gau = compute_error(d, np.float64(0.0), GAUSS, coeff, error_params={"sigma": 1.0})
    assert sig > gau                                   # near target: sigmoid steeper


# --------------------------------------------------------------------------- 7. tolerance == 0
# `tolerance: 0` used to be swallowed by a falsy test and replaced with 5 % of target — the exact
# OPPOSITE of what authoring 0 asks for, and invisible from outside because the run still scores.
# A zero band is the textbook form: the constraint becomes `m >= T` and the penalty is measured
# from the bare target, matching the published Eq.1 instead of the band-edge variant.
def test_explicit_zero_tolerance_is_honoured():
    spec = _spec(target=40.0, tolerance=0)
    assert float(spec.tolerance) == 0.0


def test_zero_tolerance_measures_the_penalty_from_the_BARE_target():
    """With tolerance 0 the implementation and paper Eq.1 finally agree."""
    spec = _spec(goal="exceed", target=40.0, range=10.0, tolerance=0,
                 error_type="relative-absolute")
    assert _penalty(30.0, spec) == pytest.approx(1.0)          # |30 - 40| / 10, not |30 - 38|
    assert _penalty(40.0, spec) == pytest.approx(0.0)          # exactly on target passes


@pytest.mark.parametrize("goal,at_target,just_inside,just_outside", [
    ("exceed", 40.0, 40.0 + 1e-9, 40.0 - 1e-9),
    ("minimize", 40.0, 40.0 - 1e-9, 40.0 + 1e-9),
])
def test_zero_tolerance_makes_the_constraint_exact(goal, at_target, just_inside, just_outside):
    spec = _spec(goal=goal, target=40.0, range=10.0, tolerance=0, error_type="relative-absolute")
    assert _penalty(at_target, spec) == 0.0
    assert _penalty(just_inside, spec) == 0.0
    assert _penalty(just_outside, spec) > 0.0


def test_zero_tolerance_is_numerically_safe_on_every_error_type():
    """Nothing divides by tolerance, but pin it: a zero band must not produce nan/inf anywhere."""
    for etype in [e for e in Error_Types if e.is_relative()]:
        spec = _spec(goal="exceed", target=40.0, range=10.0, tolerance=0, error_type=etype.value)
        for v in (39.0, 40.0, 41.0, 0.0, -5.0, 1e9):
            p = _penalty(v, spec)
            assert np.isfinite(p), (etype, v)


def test_zero_tolerance_is_safe_under_log_scale():
    """`log_space_band` computes a half-width from log10(T +/- tol); at tol 0 that collapses to 0
    rather than dividing or taking log10(0)."""
    spec = _spec(name="ugf", goal="exceed", target=1e6, range=1e6, tolerance=0, log_scale=True,
                 error_type="relative-absolute")
    assert np.isfinite(_penalty(1e4, spec))
    assert _penalty(1e6, spec) == pytest.approx(0.0)


def test_the_default_tolerance_is_zero():
    """An omitted tolerance means the target IS the constraint. The old 5 %-of-target inference
    invented a relaxation nobody authored, so a spec reading `target: 200e6` enforced >= 195e6."""
    assert float(_spec(target=40.0, tolerance=None).tolerance) == 0.0
    assert float(_spec(target=1e6, range=1e6, tolerance=None).tolerance) == 0.0


def test_a_zero_target_with_no_tolerance_needs_no_special_floor():
    """The BUG-B17 floor existed only to keep the `tolerance > 0` invariant alive. Zero is a legal
    ordinary value now, so a zero target needs no rescue."""
    spec = _spec(target=0.0, range=5.0, tolerance=None)
    assert float(spec.tolerance) == 0.0
    assert np.isfinite(_penalty(1.0, spec))


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("-inf")])
def test_a_negative_or_non_finite_tolerance_is_rejected(bad):
    """Previously swallowed by the same falsy test and silently turned into 5 %. It is a typo."""
    with pytest.raises(ValueError, match="tolerance"):
        _spec(target=40.0, tolerance=bad)
