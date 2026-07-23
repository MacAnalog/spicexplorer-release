"""Regression tests for the scoring-trust + infra-hardening follow-ups (no SPICE).

- The MINIMIZE reward no longer leaves a dead-zone in ``(target, target + tol]``.
- The parallel-sim wait is bounded — a never-finishing handle is degraded to a
  NaN-scoring failure (``_FailedSimResult``) instead of hanging the run forever.

Both methods are exercised UNBOUND (``Class.method(None, ...)``) because neither reads instance
state — they depend only on their arguments and module-level helpers — so no ngspice/optimizer
construction is needed.
"""
import math
from typing import Any, cast

import pytest
from spicexplorer.core.domains import Reward_Types, TargetSpec
from spicexplorer.optimization.base import (
    Spice_Base_Optimizer,
    Spice_Single_Objective,
    _FailedSimResult,
)

# Called unbound with self=None (neither method reads instance state) — cast to Any so the static
# checker doesn't object to the missing receiver; runtime behavior is what these tests assert.
_reward = cast(Any, Spice_Single_Objective.compute_reward_for_spec)
_wait_for_handles = cast(Any, Spice_Base_Optimizer._wait_for_handles)


def _minimize_spec() -> TargetSpec:
    # MINIMIZE power: target 200, tolerance 10 → satisfied region curr <= 210; range 100.
    return TargetSpec(
        name="power", testbench="tb", target=200.0, tolerance=10.0, range=100.0,
        goal="minimize", sim_type="op", reward_type=Reward_Types.RELATIVE_ABSOLUTE,
        measurement={"meas": "power_uw", "probe": "i(i_supply)"},
    )


# ── MINIMIZE reward has no dead-zone and is monotonic through feasibility ───────────────

def test_sc3_minimize_reward_fills_dead_zone():
    spec = _minimize_spec()
    # (target, target+tol] used to score ZERO reward AND zero penalty — a flat dead-zone. Now the
    # reward is positive there (measured from the target+tol boundary the penalty uses).
    r_grace = float(_reward(None, 205.0, spec))   # inside the grace band (200, 210]
    assert r_grace > 0.0, "reward must be non-zero inside the tolerance grace band (dead-zone gone)"


def test_sc3_minimize_reward_is_monotonic_and_continuous():
    spec = _minimize_spec()
    # Monotone: a lower (better) MINIMIZE value earns strictly more reward.
    r205, r195, r150 = (float(_reward(None, v, spec)) for v in (205.0, 195.0, 150.0))
    assert r150 > r195 > r205 > 0.0
    # Continuous with the zero penalty AT the boundary (curr == target + tol) and beyond it.
    assert float(_reward(None, 210.0, spec)) == 0.0   # exactly the boundary
    assert float(_reward(None, 260.0, spec)) == 0.0   # violated region → penalty owns it, no reward


def _exceed_spec() -> TargetSpec:
    # EXCEED gain: target 60, tolerance 3 → satisfied region curr >= 57; range 20.
    return TargetSpec(
        name="gain", testbench="tb", target=60.0, tolerance=3.0, range=20.0,
        goal="exceed", sim_type="ac", reward_type=Reward_Types.RELATIVE_ABSOLUTE,
        measurement={"meas": "dcgain", "out": "out"},
    )


def test_sc3_exceed_reward_fills_grace_band_and_is_monotonic():
    # EXCEED is treated symmetrically to MINIMIZE: its grace band [target - tol, target) used to earn
    # ZERO reward (dead-zone); now the reward is measured from the target-tol boundary the penalty
    # uses, so it is non-zero there and increases monotonically as gain rises.
    spec = _exceed_spec()
    assert float(_reward(None, 58.0, spec)) > 0.0     # inside the grace band [57, 60) → now rewarded
    r58, r60, r70 = (float(_reward(None, v, spec)) for v in (58.0, 60.0, 70.0))
    assert r70 > r60 > r58 > 0.0                       # monotone: more gain → more reward
    # Continuous with the zero penalty at the boundary and beyond it (into the violated region).
    assert float(_reward(None, 57.0, spec)) == 0.0    # exactly target - tol
    assert float(_reward(None, 50.0, spec)) == 0.0    # violated → penalty owns it, no reward


# ── bounded parallel-sim wait degrades a hung handle to a failure ───────────────────────

class _NeverDone:
    def is_done(self) -> bool:
        return False

    def result(self):  # pragma: no cover - must never be collected after timeout
        raise AssertionError("result() must not be called on a timed-out handle")


class _Done:
    def is_done(self) -> bool:
        return True

    def result(self):
        return _FailedSimResult()


def test_hd2_failed_sim_result_scores_as_nan():
    fr = _FailedSimResult()
    assert math.isnan(fr.scalar("gain", "ac"))     # NaN → MAX_PENALTY downstream
    with pytest.raises(KeyError):
        fr.wave("v(out)", "ac")                     # a wave is a hard request


def test_hd2_wait_for_handles_times_out_returns_pending():
    handles = {"tb_done": _Done(), "tb_hung": _NeverDone()}
    # A tiny timeout forces the bounded wait to give up quickly instead of spinning forever.
    pending = _wait_for_handles(None, handles, timeout_s=0.05)
    assert pending == ["tb_hung"]                   # only the never-finishing sim is flagged


def test_hd2_wait_for_handles_returns_empty_when_all_done():
    handles = {"a": _Done(), "b": _Done()}
    assert _wait_for_handles(None, handles, timeout_s=5.0) == []
