"""Regression: the scoring validity gate must reject NON-FINITE and degenerate ``log_scale`` metrics.

cross_repo_audit finding (O-1) — ``compute_fitness`` gated a candidate's metric with a bare
``not np.isnan(...)``, and the ``log_scale`` decade transform ran AFTER that gate:

* ``-inf`` passed the gate, produced an infinite REWARD on a MINIMIZE spec, and clipped to
  ``+MAX_REWARD`` — the best score the scorer can emit — so an infinitely-bad candidate became a
  permanent global best.
* ``log_space_band(0.0, …)`` returned ``-inf`` for the current value → the same ``+MAX_REWARD``.
* ``log_space_band(-5.0, …)`` returned ``nan``; every band comparison against ``nan`` is ``False``,
  so the constraint was recorded SATISFIED with zero penalty and zero reward.

Both are reachable with shipped configs: ``campaigns/ppa_ihp130/configs/*.yaml`` set
``log_scale: true`` on ``power`` / ``active_area`` / ``v(inoise_total)`` / ``cap_area``, all of
which a bad sizing legitimately drives to 0 or negative.

The fix is :func:`is_scoreable_metric` at the gate (finite AND, under ``log_scale``, strictly
positive) plus a ``_LOG_BAND_FLOOR`` on ``log_space_band``'s current value — the same guard the API
Score-Shaping preview already applied at its call site, so the two shared implementations agree.

**Reverted intermediate revision (kept as a pinned regression):** the gate was briefly made
goal-aware so a goal-ALIGNED ``+inf`` — the Tier-1 library's "perfect" sentinel — would be
scored instead of rejected. That re-opened O-1 on the 54 shipped EXCEED + linear +
relative-absolute specs, all of which are ``dcgain``, where ``+inf`` is a diverged AC solve
rather than a perfect DUT. The gate is finite-only again and
``test_a_goal_aligned_infinity_on_a_shipped_dcgain_spec_is_still_MAX_PENALTY`` holds it there.
The underlying ``inf``-overload in the registry is recorded in ``doc/TODO.md`` §22.

Exercises the scorer through a tiny concrete harness (no SPICE / optimizer build), matching
``test_missing_metric_penalty``.
"""
from __future__ import annotations

import numpy as np
import pytest
from spicexplorer.core.domains import OptimizationGoalType, Reward_Types, TargetSpec
from spicexplorer.core.utils import _LOG_BAND_FLOOR, is_scoreable_metric, log_space_band
from spicexplorer.optimization.base import MAX_PENALTY, MAX_REWARD
from spicexplorer.optimization.base import Spice_Single_Objective as _SSO


class _SpecList:
    """Stand-in for ListTargetSpec — compute_fitness only calls enabled_targets()."""

    def __init__(self, specs):
        self._specs = specs

    def enabled_targets(self):
        return [s for s in self._specs if s.enable]


class _FitnessHarness(_SSO):
    """Concrete Spice_Single_Objective with the heavy __init__ bypassed — compute_fitness reads
    only target_specs + verbose (and the sibling penalty/reward methods, inherited as-is). The
    single-objective child is the one that also awards a REWARD, which is where the degenerate
    metric used to clip to +MAX_REWARD."""

    def _create_optimizer_obj(self):  # pragma: no cover - unused abstract stub
        raise NotImplementedError

    def parameterize(self):  # pragma: no cover - unused abstract stub
        raise NotImplementedError

    def optimization_step(self):  # pragma: no cover - unused abstract stub
        raise NotImplementedError

    def __init__(self, specs):
        self.target_specs = _SpecList(specs)  # type: ignore[assignment]
        self.verbose = False


def _power_spec(*, log_scale: bool):
    """The shipped ppa-campaign shape: MINIMIZE power with a reward, optionally in decades."""
    return TargetSpec(name="power", testbench="dc_op", target=1e-3, goal="minimize",
                      sim_type="dc", log_scale=log_scale, range=1e-3, tolerance=5e-5,
                      reward_type=Reward_Types.RELATIVE_ABSOLUTE, weight=1.0)


def _cmrr_spec():
    """The shipped EXCEED shape, verbatim from
    ``examples/analog-db/campaigns/pdk_rescue/configs_sky130/amp_002_alfio_raffc.yaml:142``."""
    return TargetSpec(name="cmrr_db", testbench="cmrr_vcm", target=40.0, goal="exceed",
                      sim_type="ac", range=20.0, tolerance=1.0, weight=10.0,
                      reward_type=Reward_Types.NO_REWARD)


def _dcgain_spec():
    """The shipped EXCEED-**with-a-reward** shape, verbatim from
    ``examples/analog-db/campaigns/ppa_tsmc65/configs_r4/amp_012_peng_tcfc.yaml:129``.

    This is the shape that re-opened the ``+MAX_REWARD`` clip when the gate was made
    goal-aware: 54 of the corpus's 1249 specs are EXCEED + linear + relative-absolute, and
    all 54 are ``dcgain``."""
    return TargetSpec(name="dcgain", testbench="ac_open_loop", target=60.0, goal="exceed",
                      sim_type="ac", range=20.0, tolerance=1.0, weight=1.0,
                      reward_type=Reward_Types.RELATIVE_ABSOLUTE)


# ------------------------------------------------------------------ the shared transform
def test_log_space_band_floors_a_non_positive_value():
    """A ``log_scale`` metric at 0 / negative must land on the floor, not -inf / nan."""
    floor_decades = float(np.log10(1e-12))

    lc_neg, lt, half = log_space_band(-5.0, 40.0, 0.4)
    assert np.isfinite(lc_neg) and lc_neg == pytest.approx(floor_decades)  # was nan
    assert lt == pytest.approx(np.log10(40.0)) and half > 0.0              # bounds unchanged

    lc_zero, _, _ = log_space_band(0.0, 40.0, 0.4)
    assert np.isfinite(lc_zero) and lc_zero == pytest.approx(floor_decades)  # was -inf

    # a healthy positive reading is untouched
    lc_ok, _, _ = log_space_band(4.0, 40.0, 0.4)
    assert lc_ok == pytest.approx(np.log10(4.0))


def test_log_space_band_never_returns_nan():
    """`max(nan, floor)` returns NAN — Python's builtin `max` keeps its FIRST argument when
    the comparison is False. The transform's own docstring claimed totality it did not have."""
    lc_nan, lt, half = log_space_band(np.nan, 40.0, 0.4)
    assert np.isfinite(lc_nan) and lc_nan == pytest.approx(float(np.log10(_LOG_BAND_FLOOR)))
    assert np.isfinite(lt) and np.isfinite(half)


def test_log_space_band_does_not_saturate_sub_floor_positive_readings():
    """A positive reading BELOW the floor is real signal, not a degenerate one.

    BEFORE: `max(1e-13, 1e-12)` and `max(1e-18, 1e-12)` both clamped UP to the floor, so five
    decades of genuine improvement collapsed onto one score (-12.0) and the optimizer felt no
    gradient there — while the shipped note claimed healthy positive readings were untouched.
    """
    lc_13, _, _ = log_space_band(1e-13, 40.0, 0.4)
    lc_18, _, _ = log_space_band(1e-18, 40.0, 0.4)
    assert lc_13 == pytest.approx(-13.0)          # BEFORE: -12.0
    assert lc_18 == pytest.approx(-18.0)          # BEFORE: -12.0
    assert lc_18 < lc_13                          # BEFORE: equal — no gradient


def test_is_scoreable_metric_predicate():
    assert is_scoreable_metric(1e-3) and is_scoreable_metric(1e-3, log_scale=True)
    assert is_scoreable_metric(-5.0)                      # fine for a LINEAR spec
    assert not is_scoreable_metric(-5.0, log_scale=True)  # no decade exists
    assert not is_scoreable_metric(0.0, log_scale=True)
    for bad in (np.inf, -np.inf, np.nan):
        assert not is_scoreable_metric(bad)
        assert not is_scoreable_metric(bad, log_scale=True)


def test_is_scoreable_metric_is_finite_only_not_goal_aware():
    """The gate takes NO goal, and no goal can make a non-finite reading scoreable.

    An intermediate revision made this goal-aware so a goal-ALIGNED `+inf` (the Tier-1
    "perfect" sentinel) would be admitted. That was reverted: `+inf` is ALSO what a diverged
    solve emits and the two are indistinguishable here — see
    `test_a_goal_aligned_infinity_on_a_shipped_dcgain_spec_is_still_MAX_PENALTY`.
    """
    with pytest.raises(TypeError):
        is_scoreable_metric(np.inf, goal=OptimizationGoalType.EXCEED)  # type: ignore[call-arg]
    for goal_free_bad in (np.inf, -np.inf, np.nan):
        assert is_scoreable_metric(goal_free_bad) is False
        assert is_scoreable_metric(goal_free_bad, log_scale=True) is False


# ------------------------------------------------------------------ the scorer's gate
def test_zero_metric_under_log_scale_is_max_penalty():
    """BEFORE: log10(0) = -inf → infinite reward → clipped to +MAX_REWARD (a permanent best)."""
    score, summary = _FitnessHarness([_power_spec(log_scale=True)]).compute_fitness(
        {"power": np.float64(0.0)}
    )
    assert score == -MAX_PENALTY
    assert score != MAX_REWARD
    assert summary["power"]["curr_val"] == 0.0  # the degenerate reading stays visible


def test_negative_metric_under_log_scale_is_max_penalty():
    """BEFORE: log10(-x) = nan → every band comparison False → constraint recorded SATISFIED (0.0)."""
    score, _ = _FitnessHarness([_power_spec(log_scale=True)]).compute_fitness(
        {"power": np.float64(-5e-4)}
    )
    assert score == -MAX_PENALTY


def test_an_infinite_metric_never_scores_as_a_reward():
    """BEFORE (O-1): an infinity slipped the `isnan` gate → infinite reward → +MAX_REWARD.

    Covers BOTH directions on BOTH scales and on both goals — the gate is finite-only, so no
    infinity is ever admitted. (An intermediate revision made this goal-aware and admitted the
    goal-ALIGNED infinity; that is reverted — see the `dcgain` test below.)
    """
    for log_scale in (False, True):
        for value in (np.inf, -np.inf):
            score, _ = _FitnessHarness([_power_spec(log_scale=log_scale)]).compute_fitness(
                {"power": np.float64(value)}
            )
            assert score == -MAX_PENALTY, f"log_scale={log_scale} value={value}"

    for value in (np.inf, -np.inf):  # …and on the shipped EXCEED shape
        score, _ = _FitnessHarness([_cmrr_spec()]).compute_fitness(
            {"cmrr_db": np.float64(value)}
        )
        assert score == -MAX_PENALTY, f"cmrr_db={value}"


def test_a_goal_aligned_infinity_on_a_shipped_dcgain_spec_is_still_MAX_PENALTY():
    """Pins the O-1 pathology CLOSED on the shape that re-opened it.

    `_dcgain_spec()` is verbatim the shipped ppa_tsmc65/configs_r4 shape, and 54 of the 1249
    specs across `examples/analog-db/campaigns/**` are EXCEED + linear + relative-absolute —
    every one of them named `dcgain`. `dcgain` is `20·log10|H|` at the lowest AC point, so
    `+inf` there is a DIVERGED solve, not a perfect DUT.

    BEFORE (goal-aware gate, HEAD~1): `+inf` was admitted as goal-ALIGNED, the
    relative-absolute reward kernel returned an infinite reward, and the clip in
    `compute_fitness` turned it into `+MAX_REWARD` — the best score the scorer can emit, i.e.
    a permanent global best for a broken candidate. Now: finite-only, so `-MAX_PENALTY`.
    """
    harness = _FitnessHarness([_dcgain_spec()])
    diverged, summary = harness.compute_fitness({"dcgain": np.float64(np.inf)})
    assert diverged == -MAX_PENALTY          # BEFORE: +1000000.0
    assert diverged != MAX_REWARD
    assert summary["dcgain"]["curr_val"] == np.inf   # the reading stays visible

    # …and it must not become a global best: a healthy 80 dB DUT strictly out-scores it,
    # and the healthy score itself is untouched by the gate.
    healthy, _ = harness.compute_fitness({"dcgain": np.float64(80.0)})
    assert healthy == pytest.approx(1.05)
    assert healthy > diverged                # BEFORE: 1.05 < 1000000.0 — the diverged point WON
    assert max(healthy, diverged) == healthy

    # The mirror hole on a LINEAR MINIMIZE + reward spec (no shipped spec has this shape, but
    # the kernel is the same one): a distortion-free `-inf` must not clip to +MAX_REWARD.
    thd = TargetSpec(name="thd_db", testbench="linearity", target=-60.0, goal="minimize",
                     sim_type="tran", range=20.0, tolerance=1.0, weight=1.0,
                     reward_type=Reward_Types.RELATIVE_ABSOLUTE)
    clean, _ = _FitnessHarness([thd]).compute_fitness({"thd_db": np.float64(-np.inf)})
    assert clean == -MAX_PENALTY             # BEFORE: +1000000.0


def test_degenerate_metric_is_no_better_than_a_healthy_one():
    """The whole point: a degenerate reading must not out-score a real, feasible design."""
    harness = _FitnessHarness([_power_spec(log_scale=True)])
    healthy, _ = harness.compute_fitness({"power": np.float64(5e-4)})  # comfortably in band
    degenerate, _ = harness.compute_fitness({"power": np.float64(0.0)})
    assert healthy > 0.0            # a real design still earns its reward (unchanged)
    assert degenerate < healthy     # BEFORE: 1e6 > 1.07 — the degenerate point WON


def test_healthy_log_scale_scoring_is_unchanged():
    """The guard must not perturb the score of a valid reading."""
    score, _ = _FitnessHarness([_power_spec(log_scale=True)]).compute_fitness(
        {"power": np.float64(5e-4)}
    )
    assert score == pytest.approx(1.0740005814437774)
