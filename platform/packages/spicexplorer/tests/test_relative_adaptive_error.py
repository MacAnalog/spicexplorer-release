"""`relative-adaptive` error type: the running scale, its plumbing, and its failure modes.

`relative-adaptive` is the first STATEFUL error type. Everything else in `ERROR_COMPUTE_FUNCTIONS`
is a pure function of `(curr, target, coeff)`; this one carries a per-metric running scale across
evaluations, which buys unit-free comparability between specs and costs a non-stationary
objective. That trade is the thing under test here, so the suite is organised around what could
silently go wrong rather than around the happy path:

1. **The statistic is the statistic we claim.** Each strategy is pinned against its closed form,
   not merely against "the scale moved".
2. **The scale cannot become a divide-by-zero or an absorbing state.** A single `inf` observation
   folded into `running_max` would pin the scale at infinity and drive every later normalized
   error to 0 — silently disabling the spec for the rest of the run. Zero-only observations would
   divide by zero. Both are pinned closed.
3. **State reaches the kernel, and is not shared.** A stateless call degrades to
   `relative-absolute`, which is exactly the linear BASELINE this arm is supposed to be compared
   against — so an unwired seam would make the adaptive arm a duplicate of the control while
   looking like it ran. And two specs (or two concurrent runs) must never share a scale.
4. **Order dependence is real and bounded.** The same design point scores differently depending on
   history. That is the method, not a bug, but it is pinned so nobody "fixes" it later.

No SPICE, no PDK.
"""
from __future__ import annotations

import copy
import logging
import warnings
from typing import cast

import numpy as np
import pytest
from spicexplorer.core.domains import Error_Types, TargetSpec
from spicexplorer.core.utils import (
    ADAPTIVE_STRATEGIES,
    ERROR_COMPUTE_FUNCTIONS,
    ERROR_SHAPE_PARAMS,
    STATEFUL_ERROR_TYPES,
    AdaptiveNormalizer,
    compute_error,
    compute_relative_adaptive_error,
    log_space_band,
    resolve_error_params,
)
from spicexplorer.optimization.base import Spice_Constraint_Satisfaction

ADAPT = Error_Types.RELATIVE_ADAPTIVE


def _spec(**kw):
    base = dict(name="gain", testbench="tb", target=40.0, goal="exceed", sim_type="ac",
                range=10.0, tolerance=0.0, error_type="relative-adaptive")
    base.update(kw)
    return TargetSpec(**base)


def _penalty(curr_val, spec):
    """Invoke the scorer's penalty method unbound — it reads only its arguments."""
    return Spice_Constraint_Satisfaction.compute_constraint_violation_penalty_for_spec(
        cast("Spice_Constraint_Satisfaction", None), np.float64(curr_val), spec)


# =========================================================== 1. the statistic itself
def test_warmup_holds_the_static_fallback():
    """Below `warmup` the authored `range` is used verbatim — the statistic is not yet trusted."""
    n = AdaptiveNormalizer(strategy="running_mean", warmup=3)
    for _ in range(3):
        assert n.scale(7.0) == 7.0        # still in warmup on every one of the first 3
        n.observe(100.0)
    assert n.n == 3
    assert n.scale(7.0) == 100.0          # warmup satisfied -> the statistic takes over


def test_warmup_zero_engages_immediately():
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    assert n.scale(7.0) == 7.0            # n == 0: no samples yet, so the fallback still applies
    n.observe(4.0)
    assert n.scale(7.0) == 4.0


def test_running_mean_matches_the_closed_form():
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    obs = [1.0, 2.0, 6.0, 11.0]
    for i, e in enumerate(obs, start=1):
        n.observe(e)
        assert n.scale(1.0) == pytest.approx(sum(obs[:i]) / i)


def test_running_max_matches_the_closed_form():
    n = AdaptiveNormalizer(strategy="running_max", warmup=0)
    obs = [3.0, 1.0, 9.0, 2.0]
    for i, e in enumerate(obs, start=1):
        n.observe(e)
        assert n.scale(1.0) == pytest.approx(max(obs[:i]))


def test_running_max_never_decreases():
    """The defining property: it is an absorbing upper envelope, so the scale only coarsens."""
    n = AdaptiveNormalizer(strategy="running_max", warmup=0)
    prev = 0.0
    for e in (5.0, 1.0, 4.0, 20.0, 0.1):
        n.observe(e)
        cur = float(n.scale(1.0))
        assert cur >= prev
        prev = cur


def test_ema_matches_the_closed_form_and_seeds_on_the_first_observation():
    beta = 0.9
    n = AdaptiveNormalizer(strategy="ema", ema_beta=beta, warmup=0)
    n.observe(10.0)
    expected = 10.0                       # seeded, NOT (1-beta)*10 — otherwise the first scale
    assert n.scale(1.0) == pytest.approx(expected)   # would be 10x too small
    for e in (2.0, 8.0, 3.0):
        n.observe(e)
        expected = beta * expected + (1 - beta) * e
        assert n.scale(1.0) == pytest.approx(expected)


def test_ema_tracks_a_regime_change_faster_than_the_running_mean():
    """Why both exist: after a long calm period the mean is anchored, the EMA is not."""
    mean = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    ema = AdaptiveNormalizer(strategy="ema", ema_beta=0.5, warmup=0)
    for _ in range(100):
        mean.observe(1.0)
        ema.observe(1.0)
    for _ in range(5):                    # the metric's scale suddenly jumps
        mean.observe(100.0)
        ema.observe(100.0)
    assert ema.scale(1.0) > mean.scale(1.0)


def test_absolute_value_is_taken_on_the_observation():
    """The scorer passes a magnitude, but a negative must never shrink the scale."""
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    n.observe(-4.0)
    assert n.scale(1.0) == 4.0


# =========================================================== 2. degenerate observations
@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("strategy", ADAPTIVE_STRATEGIES)
def test_non_finite_observations_are_dropped_not_absorbed(strategy, bad):
    """The absorbing-state trap: one `inf` in `running_max` would pin the scale at infinity, so
    every later normalized error is `d/inf == 0` and the spec is silently switched off."""
    n = AdaptiveNormalizer(strategy=strategy, warmup=0)
    n.observe(2.0)
    n.observe(bad)
    assert n.n == 1                                   # not counted
    assert n.scale(1.0) == pytest.approx(2.0)         # not absorbed
    assert np.isfinite(n.scale(1.0))


@pytest.mark.parametrize("strategy", ADAPTIVE_STRATEGIES)
def test_all_zero_observations_fall_back_instead_of_dividing_by_zero(strategy):
    """A spec that is met exactly observes only zeros; `d/0` would be nan/inf and poison ranking."""
    n = AdaptiveNormalizer(strategy=strategy, warmup=0)
    for _ in range(5):
        n.observe(0.0)
    assert n.scale(7.0) == 7.0
    assert np.isfinite(compute_relative_adaptive_error(
        np.float64(1.0), np.float64(1.0), np.float64(7.0), strategy=strategy, warmup=0, state=n))


def test_a_zero_observation_does_not_erase_a_healthy_scale():
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    n.observe(4.0)
    n.observe(0.0)
    assert n.scale(1.0) == pytest.approx(2.0)   # counted in the mean, but the scale stays > 0


# =========================================================== 3. construction validation
@pytest.mark.parametrize("bad", ["runing_mean", "mean", "", "RUNNING MEAN", None])
def test_rejects_unknown_strategy(bad):
    with pytest.raises(ValueError, match="strategy"):
        AdaptiveNormalizer(strategy=bad)


@pytest.mark.parametrize("bad", [0.0, 1.0, -0.5, 1.5, float("nan"), float("inf")])
def test_rejects_bad_ema_beta(bad):
    """0 makes the EMA memoryless (the scale rattles trial-to-trial); 1 freezes it forever."""
    with pytest.raises(ValueError, match="ema_beta"):
        AdaptiveNormalizer(strategy="ema", ema_beta=bad)


def test_rejects_negative_warmup():
    with pytest.raises(ValueError, match="warmup"):
        AdaptiveNormalizer(warmup=-1)


def test_strategy_is_case_and_whitespace_tolerant():
    assert AdaptiveNormalizer(strategy="  Running_Mean ").strategy == "running_mean"


# =========================================================== 4. freeze / reset / isolation
def test_frozen_normalizer_ignores_observations():
    """How a manual single sim or a post-hoc re-score reads the landscape without perturbing it."""
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    n.observe(4.0)
    n.frozen = True
    n.observe(1000.0)
    assert n.n == 1
    assert n.scale(1.0) == pytest.approx(4.0)


def test_reset_returns_to_warmup():
    n = AdaptiveNormalizer(strategy="running_mean", warmup=2)
    for _ in range(5):
        n.observe(9.0)
    assert n.scale(1.0) == pytest.approx(9.0)
    n.reset()
    assert n.n == 0
    assert n.scale(1.0) == 1.0            # back to the fallback


def test_two_normalizers_do_not_share_state():
    """The parallel-safety property: state is per instance, never a module-level singleton, so two
    concurrent runs (or two specs) in one process cannot contaminate each other's scale."""
    a = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    b = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    a.observe(100.0)
    assert b.n == 0
    assert b.scale(1.0) == 1.0
    assert a.scale(1.0) == 100.0


def test_each_targetspec_owns_its_own_state():
    s1, s2 = _spec(name="a"), _spec(name="b")
    assert s1.error_state is not s2.error_state
    s1.error_state.observe(50.0)
    assert s2.error_state.n == 0


def test_deepcopy_gives_an_independent_state():
    """`Project_Setup` is copied in a few places; a shared scale across copies would couple runs."""
    s1 = _spec()
    s1.error_state.observe(50.0)
    s2 = copy.deepcopy(s1)
    s2.error_state.observe(50.0)
    assert s1.error_state.n == 1
    assert s2.error_state.n == 2


# =========================================================== 5. plumbing
def test_declared_and_implemented():
    assert Error_Types("relative-adaptive") is ADAPT
    assert ADAPT in ERROR_COMPUTE_FUNCTIONS
    assert ADAPT in ERROR_SHAPE_PARAMS
    assert ADAPT in STATEFUL_ERROR_TYPES
    assert set(ERROR_COMPUTE_FUNCTIONS) >= set(Error_Types)


def test_stateless_call_degrades_to_relative_absolute():
    """Documented degradation — and the reason it warns: silently equal to the linear BASELINE."""
    routed = compute_error(np.float64(12.0), np.float64(10.0), ADAPT, np.float64(4.0))
    baseline = compute_error(np.float64(12.0), np.float64(10.0), Error_Types.RELATIVE_ABSOLUTE,
                             np.float64(4.0))
    assert routed == pytest.approx(baseline)


def test_state_actually_reaches_the_kernel_through_compute_error():
    """A seam that failed to carry state would leave this arm indistinguishable from linear."""
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    n.observe(1.0)                        # scale is now 1.0, NOT the coeff 100.0
    routed = compute_error(np.float64(3.0), np.float64(0.0), ADAPT, np.float64(100.0),
                           error_state=n)
    stateless = compute_error(np.float64(3.0), np.float64(0.0), ADAPT, np.float64(100.0))
    assert routed != pytest.approx(stateless)
    # observing 3.0 makes the mean (1+3)/2 = 2 -> 3/2
    assert routed == pytest.approx(1.5)


def test_compute_error_forwards_the_shape_params():
    a = AdaptiveNormalizer(strategy="running_max", warmup=0)
    b = AdaptiveNormalizer(strategy="running_mean", warmup=0)
    for n in (a, b):
        n.observe(1.0)
    coeff = np.float64(100.0)
    got_max = compute_error(np.float64(3.0), np.float64(0.0), ADAPT, coeff,
                            error_params={"strategy": "running_max"}, error_state=a)
    got_mean = compute_error(np.float64(3.0), np.float64(0.0), ADAPT, coeff,
                             error_params={"strategy": "running_mean"}, error_state=b)
    assert got_max == pytest.approx(1.0)     # max(1,3) = 3 -> 3/3
    assert got_mean == pytest.approx(1.5)    # mean(1,3) = 2 -> 3/2


def test_error_state_is_ignored_by_stateless_error_types():
    """Call sites pass it unconditionally, so it must be inert everywhere else."""
    n = AdaptiveNormalizer(warmup=0)
    for etype in (Error_Types.RELATIVE_ABSOLUTE, Error_Types.RELATIVE_SIGMOID,
                  Error_Types.RELATIVE_GAUSSIAN, Error_Types.ABSOLUTE):
        coeff = np.float64(10.0) if etype.is_relative() else None
        with_state = compute_error(np.float64(41.0), np.float64(40.0), etype, coeff, error_state=n)
        without = compute_error(np.float64(41.0), np.float64(40.0), etype, coeff)
        assert with_state == pytest.approx(without), etype
    assert n.n == 0                        # and nothing was recorded against it


def test_unknown_error_param_is_rejected():
    with pytest.raises(ValueError, match="Unknown error_params"):
        resolve_error_params(ADAPT, {"stratgey": "ema"})


def test_defaults_are_the_documented_ones():
    """`warmup: 0` + `seed: target` is the shipped default: seeding gives a sensible scale from
    evaluation one, so there is nothing to burn in on."""
    assert resolve_error_params(ADAPT, None) == {
        "strategy": "running_mean", "ema_beta": 0.9, "warmup": 0,
        "window": None, "seed": "target", "seed_weight": 1}


# =========================================================== 6. load validation
def test_state_is_built_at_load_with_defaults_and_no_error_params():
    """A stateful type must get its normalizer even when the YAML names no `error_params:`."""
    spec = _spec()
    assert isinstance(spec.error_state, AdaptiveNormalizer)
    assert (spec.error_state.strategy, spec.error_state.warmup) == ("running_mean", 0)
    assert spec.error_state.seed == pytest.approx(abs(float(spec.target)))   # seeded from target
    assert spec.error_state.window is None


def test_state_honours_authored_error_params():
    spec = _spec(error_params={"strategy": "ema", "ema_beta": 0.5, "warmup": 2})
    assert (spec.error_state.strategy, spec.error_state.ema_beta, spec.error_state.warmup) == (
        "ema", 0.5, 2)


@pytest.mark.parametrize("bad", [
    {"strategy": "runing_mean"},
    {"ema_beta": 0.0},
    {"ema_beta": 1.0},
    {"warmup": -5},
    {"sigma": 1.0},                        # a gaussian key on an adaptive spec
])
def test_bad_error_params_are_rejected_at_load(bad):
    """Fails when the YAML is read, not thousands of evaluations into an overnight sweep."""
    with pytest.raises(ValueError):
        _spec(error_params=bad)


def test_non_adaptive_specs_carry_no_state():
    for etype in ("relative-absolute", "relative-sigmoid", "relative-gaussian"):
        assert _spec(error_type=etype).error_state is None


def test_error_state_is_not_a_dsl_key():
    """It is `init=False`, so a YAML that names it is rejected rather than silently honoured."""
    with pytest.raises(TypeError):
        TargetSpec(name="g", testbench="tb", target=1.0, goal="exceed", sim_type="ac",
                   range=1.0, error_type="relative-adaptive",
                   error_state=AdaptiveNormalizer())  # type: ignore[call-arg]


# =========================================================== 7. behaviour inside the scorer
def test_scorer_feeds_the_specs_own_state():
    """End-to-end through the real penalty path: repeated scoring must move the spec's scale.

    Note the errors observed are measured from the tolerance BAND EDGE (`target - tolerance`),
    not the bare target — the same convention the penalty itself uses."""
    spec = _spec(goal="exceed", target=40.0, tolerance=2.0, range=10.0,
                 error_params={"strategy": "running_mean", "warmup": 0, "seed": "none"})
    _penalty(30.0, spec)                   # |30 - 38| = 8
    assert spec.error_state.n == 1
    _penalty(20.0, spec)                   # |20 - 38| = 18
    assert spec.error_state.n == 2
    assert spec.error_state.scale(10.0) == pytest.approx(13.0)


def test_the_seed_participates_in_the_statistic_from_the_first_trial():
    """With the default `seed: target`, the scale is a blend of the prior and real evidence — so
    the FIRST violation does not normalize to exactly 1.0 the way an unseeded scale forces."""
    seeded = _spec(goal="exceed", target=40.0, tolerance=2.0, range=10.0,
                   error_params={"strategy": "running_mean", "warmup": 0})
    unseeded = _spec(goal="exceed", target=40.0, tolerance=2.0, range=10.0,
                     error_params={"strategy": "running_mean", "warmup": 0, "seed": "none"})
    assert _penalty(30.0, unseeded) == pytest.approx(1.0)      # first sample defines the scale
    assert _penalty(30.0, seeded) != pytest.approx(1.0)
    assert seeded.error_state.scale(10.0) == pytest.approx((40.0 + 8.0) / 2)


def test_a_satisfied_spec_never_leaves_warmup():
    """Only violations reach the kernel, so `S_i` calibrates to the scale of this spec's misses."""
    spec = _spec(goal="exceed", target=40.0, tolerance=1.0,
                 error_params={"strategy": "running_mean", "warmup": 0})
    for v in (45.0, 50.0, 41.0):
        assert _penalty(v, spec) == 0.0
    assert spec.error_state.n == 0


def test_the_same_design_point_scores_differently_with_history():
    """The non-stationarity is real. Pinned so it is a known property, not a later surprise."""
    fresh = _spec(error_params={"strategy": "running_mean", "warmup": 0})
    seasoned = _spec(error_params={"strategy": "running_mean", "warmup": 0})
    seasoned.error_state.observe(100.0)    # a large earlier miss coarsens the scale
    assert _penalty(30.0, fresh) != pytest.approx(_penalty(30.0, seasoned))


def test_adaptive_rescales_a_badly_authored_range():
    """The point of the error type: a `range` off by 1e6 still yields an O(1) penalty once warm."""
    absurd = _spec(range=1e12, tolerance=0.0,
                   error_params={"strategy": "running_mean", "warmup": 0})
    linear = _spec(range=1e12, tolerance=0.0, error_type="relative-absolute")
    for v in (30.0, 20.0, 35.0):           # warm the adaptive scale on real misses
        _penalty(v, absurd)
    adaptive_p = _penalty(30.0, absurd)
    linear_p = _penalty(30.0, linear)
    assert linear_p < 1e-9                 # linear: the miss all but vanishes
    assert 0.1 < adaptive_p < 10.0         # adaptive: recovered to O(1)


def test_log_scale_spec_calibrates_in_decades():
    """A `log_scale` spec's errors are DECADES, and the fallback the caller passes is the decade
    coefficient — so the statistic is in the same units with no special case in the normalizer."""
    spec = _spec(name="ugf", goal="exceed", target=1e6, range=1e6, tolerance=5e4, log_scale=True,
                 error_params={"strategy": "running_mean", "warmup": 0, "seed": "none"})
    _penalty(1e4, spec)                    # ~2 decades below target
    assert spec.error_state.n == 1
    # Expected value derived from the shared transform rather than hardcoded, so it stays correct
    # if the band definition moves: the observed error is |log10(curr) - (log_target - half_band)|.
    lc, lt, half = log_space_band(np.float64(1e4), np.float64(1e6), np.float64(5e4))
    assert spec.error_state.scale(1.0) == pytest.approx(abs(lc - (lt - half)))
    assert 1.9 < float(spec.error_state.scale(1.0)) < 2.0   # and it really is ~2 DECADES, not 1e6


def test_weights_still_scale_the_adaptive_penalty():
    kw = dict(tolerance=0.0, error_params={"strategy": "running_mean", "warmup": 0})
    one = _spec(weight=1.0, **kw)
    ten = _spec(weight=10.0, **kw)
    assert _penalty(30.0, ten) == pytest.approx(10.0 * _penalty(30.0, one))


def test_corner_evaluations_share_the_spec_scale_by_design():
    """Corners are repeated observations of the SAME metric, so they feed one scale — a trial in a
    3-corner run advances `n` by 3. This is deliberate; it is what makes the scale converge at the
    same rate per *simulation* regardless of how the corner axis is configured."""
    spec = _spec(error_params={"strategy": "running_mean", "warmup": 0})
    for _ in range(3):                     # tt / ss / ff of one trial
        _penalty(30.0, spec)
    assert spec.error_state.n == 3


# =========================================================== 8. bounded window
# An all-time mean stays anchored to the errors seen during early random exploration, which is a
# regime the search has left by the time it matters. `window` is what lets the scale forget.
def test_window_keeps_only_the_most_recent_samples():
    n = AdaptiveNormalizer(strategy="running_mean", window=3, warmup=0)
    for e in (100.0, 1.0, 2.0, 3.0):
        n.observe(e)
    assert n.scale(999.0) == pytest.approx(2.0)      # 100.0 has fallen out of the window
    assert n.n == 4                                  # ...but it was still COUNTED (drives warmup)


def test_window_lets_running_max_decrease_again():
    """Unbounded `running_max` is an absorbing envelope — one bad early trial pins the scale for
    the whole run. A window is the only thing that lets it come back down."""
    unbounded = AdaptiveNormalizer(strategy="running_max", warmup=0)
    windowed = AdaptiveNormalizer(strategy="running_max", window=2, warmup=0)
    for e in (500.0, 1.0, 2.0):
        unbounded.observe(e)
        windowed.observe(e)
    assert unbounded.scale(1.0) == pytest.approx(500.0)
    assert windowed.scale(1.0) == pytest.approx(2.0)


def test_window_of_one_is_the_last_error_only():
    n = AdaptiveNormalizer(strategy="running_mean", window=1, warmup=0, seed=None)
    for e, want in ((5.0, 5.0), (9.0, 9.0), (0.5, 0.5)):
        n.observe(e)
        assert n.scale(1.0) == pytest.approx(want)


def test_window_zero_and_none_both_mean_unbounded():
    for w in (0, None):
        n = AdaptiveNormalizer(strategy="running_mean", window=w, warmup=0, seed=None)
        for e in (1.0, 2.0, 3.0):
            n.observe(e)
        assert n.window is None
        assert n.scale(1.0) == pytest.approx(2.0)


def test_ema_ignores_the_window():
    """`ema_beta` already sets an effective memory (~1/(1-beta)); a second memory knob on the
    same statistic would just be two ways to say the same thing, disagreeing."""
    a = AdaptiveNormalizer(strategy="ema", ema_beta=0.5, warmup=0, seed=None)
    b = AdaptiveNormalizer(strategy="ema", ema_beta=0.5, warmup=0, seed=None, window=2)
    for e in (8.0, 4.0, 2.0, 1.0):
        a.observe(e)
        b.observe(e)
    assert a.scale(1.0) == pytest.approx(b.scale(1.0))


def test_rejects_negative_window():
    with pytest.raises(ValueError, match="window"):
        AdaptiveNormalizer(window=-1)


def test_window_is_bounded_in_memory():
    """The retained list must not grow with trial count — a 2000-evaluation sweep across many
    specs would otherwise accumulate one float per evaluation per spec, forever."""
    n = AdaptiveNormalizer(strategy="running_mean", window=10, warmup=0)
    for i in range(5000):
        n.observe(float(i % 7 + 1))
    assert len(n._samples) == 10
    assert n.n == 5000


# =========================================================== 9. the seed ("past" sample)
def test_seed_defaults_to_the_target_magnitude():
    """"Assume a 100 % miss until proven otherwise" — a defensible prior, and what makes
    `warmup: 0` usable."""
    spec = _spec(target=40.0)
    assert spec.error_state.seed == pytest.approx(40.0)
    assert spec.error_state.scale(np.float64(10.0)) == pytest.approx(40.0)   # before any data


def test_seed_from_range_uses_the_static_normalizer():
    """The conservative choice: start the adaptive scale exactly where the fixed-scale error
    types would have been."""
    spec = _spec(target=40.0, range=7.0, error_params={"seed": "range"})
    assert spec.error_state.seed == pytest.approx(7.0)


def test_seed_none_leaves_the_scale_undefined_until_the_first_violation():
    spec = _spec(error_params={"seed": "none"})
    assert spec.error_state.seed is None
    assert spec.error_state.scale(np.float64(10.0)) == pytest.approx(10.0)   # the fallback


def test_seed_accepts_an_explicit_magnitude():
    assert _spec(error_params={"seed": 3.5}).error_state.seed == pytest.approx(3.5)


def test_log_scale_seed_is_expressed_in_DECADES_not_in_log_of_the_target():
    """The trap this resolver exists for. Samples are decades, so a 100 % miss seeds at
    log10(2) ~= 0.301 decades — NOT |log10(1e6)| = 6, which is not an error magnitude at all and
    would start the scale 20x too coarse."""
    spec = _spec(name="ugf", target=1e6, range=1e6, log_scale=True)
    assert spec.error_state.seed == pytest.approx(float(np.log10(2.0)))
    assert spec.error_state.seed < 1.0


def test_seed_weight_sets_how_strongly_the_prior_holds():
    heavy = AdaptiveNormalizer(strategy="running_mean", warmup=0, seed=100.0, seed_weight=9)
    light = AdaptiveNormalizer(strategy="running_mean", warmup=0, seed=100.0, seed_weight=1)
    for n in (heavy, light):
        n.observe(0.0)
    assert heavy.scale(1.0) == pytest.approx(90.0)    # 9x100 + 1x0 over 10 samples
    assert light.scale(1.0) == pytest.approx(50.0)    # 1x100 + 1x0 over 2


def test_the_seed_is_evicted_first_so_the_prior_fades_with_evidence():
    """Oldest-out eviction puts the seed at the front of the queue, which is exactly what a prior
    should do: dominate when there is no data, vanish once there is."""
    n = AdaptiveNormalizer(strategy="running_mean", window=2, warmup=0, seed=100.0)
    n.observe(2.0)
    assert n.scale(1.0) == pytest.approx(51.0)        # prior still half the window
    n.observe(4.0)
    assert n.scale(1.0) == pytest.approx(3.0)         # prior gone entirely


def test_seed_weight_cannot_fill_the_whole_window():
    """Otherwise the window holds nothing but the prior and no observation can ever move it —
    a silently frozen scale, which is the worst outcome available."""
    with pytest.raises(ValueError, match="seed_weight"):
        AdaptiveNormalizer(window=3, seed=1.0, seed_weight=4)


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_rejects_a_non_positive_seed(bad):
    with pytest.raises(ValueError, match="seed"):
        AdaptiveNormalizer(seed=bad)


def test_rejects_an_unknown_seed_basis_at_load():
    with pytest.raises(ValueError, match="seed"):
        _spec(error_params={"seed": "tgt"})


def test_seed_survives_reset():
    """`reset()` returns to the STARTING point, which is the seeded state — not an empty one, or
    a re-scored replay would begin from a different prior than the original run."""
    n = AdaptiveNormalizer(strategy="running_mean", warmup=0, seed=50.0)
    n.observe(1.0)
    n.reset()
    assert n.n == 0
    assert n.scale(999.0) == pytest.approx(50.0)


def test_seed_is_dropped_when_the_target_cannot_supply_one():
    """A zero target has no magnitude to seed from; degrade to unseeded rather than to a zero
    scale (which would be a division by zero on the first violation)."""
    spec = _spec(target=0.0, range=5.0, tolerance=1.0)
    assert spec.error_state.seed is None


# =========================================================== 10. the unwired seam is LOUD
def test_unwired_seam_raises_a_runtime_warning_and_logs_an_error(caplog, monkeypatch):
    """The degradation is silent in its NUMBERS, which is the dangerous kind: the adaptive arm
    quietly becomes its own linear control. So it is reported three ways — ERROR log, a
    RuntimeWarning on stderr, and a message a `-W error::RuntimeWarning` run turns into a hard
    failure."""
    import spicexplorer.core.utils as U
    monkeypatch.setattr(U, "_WARNED_STATELESS_ADAPTIVE", False)
    with caplog.at_level(logging.ERROR, logger="spicexplorer.designer_tools.utils"):
        with pytest.warns(RuntimeWarning, match="UNWIRED SEAM"):
            compute_error(np.float64(12.0), np.float64(10.0), ADAPT, np.float64(4.0))
    assert any("UNWIRED SEAM" in r.message for r in caplog.records)
    assert any(r.levelno >= logging.ERROR for r in caplog.records)


def test_unwired_seam_warning_names_the_fix(monkeypatch):
    import spicexplorer.core.utils as U
    assert "error_state" in U.UNWIRED_ADAPTIVE_SEAM_MSG
    assert "relative-absolute" in U.UNWIRED_ADAPTIVE_SEAM_MSG


def test_unwired_seam_warns_once_not_per_evaluation(monkeypatch):
    """A 2000-evaluation run would bury its own log."""
    import spicexplorer.core.utils as U
    monkeypatch.setattr(U, "_WARNED_STATELESS_ADAPTIVE", False)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for _ in range(50):
            compute_error(np.float64(12.0), np.float64(10.0), ADAPT, np.float64(4.0))
    assert len([w for w in caught if issubclass(w.category, RuntimeWarning)]) == 1


def test_a_wired_seam_is_silent(monkeypatch):
    import spicexplorer.core.utils as U
    monkeypatch.setattr(U, "_WARNED_STATELESS_ADAPTIVE", False)
    state = AdaptiveNormalizer(warmup=0, seed=None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        compute_error(np.float64(12.0), np.float64(10.0), ADAPT, np.float64(4.0), error_state=state)
    assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]


def test_the_scorer_never_trips_the_unwired_warning(monkeypatch):
    """The guarantee that matters: a real scoring path always carries the spec's own state."""
    import spicexplorer.core.utils as U
    monkeypatch.setattr(U, "_WARNED_STATELESS_ADAPTIVE", False)
    spec = _spec(error_params={"warmup": 0})
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _penalty(30.0, spec)
        _penalty(20.0, spec)
    assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]
    assert spec.error_state.n == 2
