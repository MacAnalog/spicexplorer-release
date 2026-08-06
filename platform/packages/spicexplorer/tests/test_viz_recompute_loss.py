"""`recompute_loss_from_optimization_config` writes BOTH halves of the re-score (O-6).

Re-scoring a finished run under different target specs updated each entry's per-spec
`fit_summary` but threw the recomputed total away, so `get_score()` — the loss axis of
every plot, `filter_top_n`, the best-point pick — kept reporting the score from the
config the run was originally executed under. The re-score silently did nothing.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
from spicexplorer.core.domains import (
    OptimizationLog,
    OptimizationLogEntry,
    OptimizationPoint,
)
from spicexplorer.viz.plotting import Optimization_Log_Visualizer


def _entry(score: float, gain: float, **params: float) -> OptimizationLogEntry:
    return OptimizationLogEntry(
        point=OptimizationPoint(params=params, score=np.float64(score)),
        fit_summary={"gain": {"curr_val": np.float64(gain), "score": np.float64(score)}},
    )


class _StubScorer:
    """Duck-typed stand-in for `Spice_Constraint_Satisfaction` (only `compute_fitness`
    is called). Scores a NEW config: reward proximity to a 60 dB gain target."""

    def compute_fitness(
        self, performance_array: Dict[str, float]
    ) -> Tuple[np.float64, Dict[str, Any]]:
        gain = performance_array["gain"]
        score = np.float64(-abs(gain - 60.0))
        return score, {"gain": {"curr_val": np.float64(gain), "score": score}}


def test_recompute_updates_the_entry_score_not_only_the_fit_summary() -> None:
    log = OptimizationLog([_entry(score=0.9, gain=45.0, w=1e-6), _entry(score=0.1, gain=58.0, w=2e-6)])
    vis = Optimization_Log_Visualizer(optimization_log=log)

    vis.recompute_loss_from_optimization_config(_StubScorer())  # type: ignore[arg-type]

    assert [float(e.get_score()) for e in log] == [-15.0, -2.0]  # was [0.9, 0.1]
    assert [float(s) for s in log.get_all_loss()] == [-15.0, -2.0]
    assert float(log[1].get_fit_summary()["gain"]["score"]) == -2.0  # both halves agree


def test_recompute_then_filter_top_n_keeps_the_NEW_best_point() -> None:
    """The consequence: with the score discarded, every score-ordered consumer still
    ranked by the OLD config — `filter_top_n(1)` kept the 45 dB point (old score 0.9)."""
    log = OptimizationLog([_entry(score=0.9, gain=45.0, w=1e-6), _entry(score=0.1, gain=58.0, w=2e-6)])
    vis = Optimization_Log_Visualizer(optimization_log=log)

    vis.recompute_loss_from_optimization_config(_StubScorer())  # type: ignore[arg-type]
    vis.filter_top_n(1)

    assert len(log) == 1
    assert float(log[0].get_fit_summary()["gain"]["curr_val"]) == 58.0
    assert log[0].get_param_val("w") == 2e-6
