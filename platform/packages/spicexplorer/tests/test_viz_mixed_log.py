"""Plotting robustness on a mixed-era optimization log.

When a single-corner checkpoint is resumed into a multi-corner run, later log entries
can carry different fit_summary keys than entry[0] (a corner present in the first
entry may be absent in a later one). The trace plotter checked membership only
against entry[0] and then indexed every entry directly — a KeyError that killed
the whole plot. It must index defensively (missing cell → NaN gap) instead.
"""
from __future__ import annotations

import numpy as np
from spicexplorer.core.domains import (
    OptimizationLog,
    OptimizationLogEntry,
    OptimizationPoint,
)
from spicexplorer.viz.plotting import Optimization_Log_Visualizer


def _entry(score, fit_summary, **params):
    return OptimizationLogEntry(
        point=OptimizationPoint(params=params, score=score),
        fit_summary=fit_summary,
    )


def _cell(curr_val, score):
    return {"curr_val": curr_val, "score": score}


def test_plot_optimization_trace_survives_key_absent_in_later_entry():
    """entry[0] has tt::gain; a later entry dropped it (corner absent post-resume).
    The old direct index raised KeyError; now the missing cell becomes NaN."""
    log = OptimizationLog([
        _entry(0.5, {"tt::gain": _cell(55.0, -1.0), "ss::gain": _cell(30.0, -5.0)}, w=1e-6),
        _entry(0.6, {"ss::gain": _cell(52.0, -0.5)}, w=2e-6),  # tt::gain gone
    ])
    vis = Optimization_Log_Visualizer(optimization_log=log)

    result = vis.plot_optimization_trace("tt::gain", "ss::gain")  # must not raise
    assert result is not None
    x_values, y_values = result
    assert x_values[0] == 55.0 and np.isnan(x_values[1])  # absent cell → NaN gap
    assert list(y_values) == [30.0, 52.0]


def test_plot_optimization_trace_missing_in_first_entry_returns_none():
    """A metric absent from entry[0] is still reported as not-found (return None),
    not a crash — the pre-existing guard is preserved."""
    log = OptimizationLog([
        _entry(0.5, {"ss::gain": _cell(30.0, -5.0)}, w=1e-6),
    ])
    vis = Optimization_Log_Visualizer(optimization_log=log)
    assert vis.plot_optimization_trace("tt::gain", "ss::gain") is None
