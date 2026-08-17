"""Regression: log-scale specs must normalize their DECADE-space error by a DECADE-space range.

For a ``log_scale`` spec the optimizer measures the error in decades
(via ``_log_space_band``) but divided it by ``target_spec.range``, a LINEAR magnitude. A ~1-decade
GBW miss (numerator ~1) divided by e.g. 1e8 gave a penalty ~1e-8 — effectively zero — so GBW-type
log-scale constraints were silently dead and never steered the optimizer. The fix normalizes the
decade error by the decade span of the range (``log10(target+range) - log10(target)``).

The penalty/reward methods use no instance state, so they're invoked with ``self=None`` — no SPICE,
PDK, or optimizer construction required.
"""
from __future__ import annotations

from typing import cast

import numpy as np
import pytest
from spicexplorer.core.domains import Reward_Types, TargetSpec
from spicexplorer.optimization.base import (
    Spice_Constraint_Satisfaction,
    Spice_Single_Objective,
)


# The scoring methods read only the spec + curr_val (never self), so they can be invoked unbound
# with a None self — cast keeps that intentional and pyright-clean.
def _penalty(curr_val, spec):
    return Spice_Constraint_Satisfaction.compute_constraint_violation_penalty_for_spec(
        cast("Spice_Constraint_Satisfaction", None), np.float64(curr_val), spec)


def _reward(curr_val, spec):
    return Spice_Single_Objective.compute_reward_for_spec(
        cast("Spice_Single_Objective", None), np.float64(curr_val), spec)


def test_log_scale_penalty_normalized_in_decade_space():
    """A one-decade GBW violation must produce a MATERIAL penalty, not a dead ~0.

    GBW exceed-spec at 100 MHz (log-scale); a design one decade low (10 MHz) violates it.
    decade miss = 1.000 decade; decade range = log10(2e8) - log10(1e8) = 0.301 decade.
      BEFORE (÷ linear range 1e8): 1.000 / 1e8 = 1e-8    → constraint silently dead
      AFTER  (÷ decade range 0.301): 1.000 / 0.301 ≈ 3.32 → materially penalized

    The miss is exactly 1.000 decade because tolerance now defaults to 0 (the target IS the
    constraint). Under the old 5 %-of-target default it was 0.978 and the penalty 3.25.
    """
    spec = TargetSpec(name="gbw", testbench="ac_tb", target=1e8, goal="exceed",
                      sim_type="ac", log_scale=True)  # range→1e8, tolerance→0 (defaults)

    penalty = _penalty(1e7, spec)
    assert penalty == pytest.approx(1.0 / 0.30103, rel=0.02)   # = 3.32
    assert penalty > 1.0  # material — the whole point (was ~9.8e-9 before the fix)

    # the linear-range normalizer the bug used (range defaults to the 1e8 target) was ~8 orders of
    # magnitude larger than the decade range, collapsing the penalty to ~zero
    buggy_linear = 1.0 / 1e8
    assert buggy_linear < 1e-6 and penalty / buggy_linear > 1e6

    # a design that EXCEEDS the target by a decade is satisfied → no penalty (still correct)
    assert _penalty(1e9, spec) == np.float64(0.0)


def test_log_scale_reward_normalized_in_decade_space():
    """The reward site (same bug, second location) also normalizes in decade space now.

    The EXCEED reward is measured from the tolerance-adjusted boundary (target - tol) the
    penalty uses, in decade space — so the grace band earns a smooth reward rather than a dead-zone.
    """
    spec = TargetSpec(name="gbw", testbench="ac_tb", target=1e8, goal="exceed", sim_type="ac",
                      log_scale=True, reward_type=Reward_Types.RELATIVE_ABSOLUTE)
    # curr 1e9 (one decade over): decade distance from the boundary (log10(1e8) - 0.0223 ≈ 7.9777)
    # is 9 - 7.9777 = 1.0223, over decade range 0.301 → ≈ 3.40 (was 1.0/1e8 ≈ 1e-8 before the fix).
    reward = _reward(1e9, spec)
    assert reward == pytest.approx(3.32, rel=0.02)
    assert reward > 1.0


def test_linear_spec_penalty_unchanged():
    """A non-log spec takes the else-branch (linear range) — behavior must be byte-for-byte the same."""
    spec = TargetSpec(name="pm", testbench="ac_tb", target=100.0, goal="exceed", sim_type="ac")
    # |50 - (100 - 5)| / 100 = 45/100 = 0.45
    # |50 - 100| / 100 — measured from the BARE target now, not from target - 5 %.
    assert _penalty(50.0, spec) == pytest.approx(0.50, rel=1e-9)
