"""Regression: a failed/missing simulation metric must score as the maximal penalty for EVERY
error type, so a crashed sim strictly dominates any converged in-band violation.

compute_fitness scored a missing metric as ``-weight`` for a
RELATIVE_SIGMOID spec but ``-MAX_PENALTY`` for every other error type. Because a sigmoid penalty is
bounded by ``weight``, that made a CRASHED sigmoid spec no worse than the best-scoring converged
violation — and, across specs, a design whose sim crashed could OUTSCORE a fully-converged design
that merely violated another spec, pulling the optimizer toward crashes. The fix drops the
carve-out: a missing metric is ``-MAX_PENALTY`` for all error types (the documented run_and_wait
failure contract).

Exercises compute_fitness directly through a tiny concrete harness (no SPICE / optimizer build).
"""
from __future__ import annotations

import numpy as np
import pytest
from spicexplorer.core.domains import Error_Types, TargetSpec
from spicexplorer.optimization.base import MAX_PENALTY
from spicexplorer.optimization.base import Spice_Constraint_Satisfaction as _SCS


class _SpecList:
    """Stand-in for ListTargetSpec — compute_fitness only calls enabled_targets()."""
    def __init__(self, specs):
        self._specs = specs

    def enabled_targets(self):
        return [s for s in self._specs if s.enable]


class _FitnessHarness(_SCS):
    """Concrete Spice_Constraint_Satisfaction with the heavy __init__ bypassed — compute_fitness
    reads only target_specs + verbose (and the sibling penalty methods, inherited as-is). The three
    abstract methods are never called here; they only make the class concrete."""

    def _create_optimizer_obj(self):  # pragma: no cover - unused abstract stub
        raise NotImplementedError

    def parameterize(self):  # pragma: no cover - unused abstract stub
        raise NotImplementedError

    def optimization_step(self):  # pragma: no cover - unused abstract stub
        raise NotImplementedError

    def __init__(self, specs):
        self.target_specs = _SpecList(specs)  # type: ignore[assignment]
        self.verbose = False


def _sigmoid_spec():
    return TargetSpec(name="gain", testbench="ac", target=40.0, goal="exceed", sim_type="ac",
                      error_type=Error_Types.RELATIVE_SIGMOID, weight=1.0)


def _abs_spec():
    return TargetSpec(name="gain", testbench="ac", target=40.0, goal="exceed", sim_type="ac",
                      error_type=Error_Types.RELATIVE_ABSOLUTE, weight=1.0)


def test_missing_metric_penalty_unified_across_error_types():
    """A missing metric scores -MAX_PENALTY for BOTH error types (was -weight for sigmoid)."""
    sig_score, _ = _FitnessHarness([_sigmoid_spec()]).compute_fitness({})   # metric absent
    abs_score, _ = _FitnessHarness([_abs_spec()]).compute_fitness({})
    assert sig_score == -MAX_PENALTY   # BEFORE: -weight = -1.0
    assert abs_score == -MAX_PENALTY   # unchanged
    assert sig_score == abs_score      # unified


def test_failure_strictly_dominates_worst_converged_sigmoid():
    """A crashed sigmoid spec (-MAX_PENALTY) must be strictly worse than the WORST converged sigmoid
    violation, whose penalty is bounded by weight (~-1) — before the fix they tied at -weight."""
    h = _FitnessHarness([_sigmoid_spec()])
    missing, _ = h.compute_fitness({})                       # crashed
    worst_converged, _ = h.compute_fitness({"gain": np.float64(-1e6)})  # far out of band, but ran
    assert missing == -MAX_PENALTY
    assert -1.0 <= worst_converged < 0.0                     # sigmoid penalty bounded by weight
    assert missing < worst_converged                          # strict dominance


def test_crashed_sim_no_longer_outscores_a_converged_violation():
    """The cross-spec bug: a design whose sim crashed on the sigmoid spec once OUTSCORED a
    fully-converged design that violated another spec. Failure must now dominate."""
    leak = TargetSpec(name="leak", testbench="dc", target=100.0, goal="minimize", sim_type="dc",
                      error_type=Error_Types.RELATIVE_ABSOLUTE, range=1.0, weight=1.0)
    h = _FitnessHarness([_sigmoid_spec(), leak])

    # Design A: the gain sim CRASHED (metric missing); leakage is fine.
    a_score, _ = h.compute_fitness({"leak": np.float64(50.0)})
    # Design B: everything converged, but leakage violates its spec (|200-(100+5)|/1 = 95).
    b_score, _ = h.compute_fitness({"gain": np.float64(50.0), "leak": np.float64(200.0)})

    assert a_score == -MAX_PENALTY
    # 100 over a target of 100 with the default (now zero) tolerance -> the full 100, where the
    # old 5 % default made it 95.
    assert b_score == pytest.approx(-100.0)
    # AFTER the fix the crashed design is far worse; the OLD -weight carve-out gave A = -1.0, which
    # would have BEATEN B = -95.0 and steered the optimizer toward the crash.
    assert a_score < b_score
