"""Multi-corner checkpoint-reader robustness (CKPT-1 / CKPT-2).

The Explorer reads a resumed multi-corner checkpoint whose log can mix corners
(a corner added on resume) and key styles (Phase-1 bare ``spec`` vs Phase-2
``"<corner>::spec"``). These tests pin the feasibility + scatter behavior that
keeps such a checkpoint honest instead of blank or all-red.
"""
from __future__ import annotations

from spicexplorer.core.domains import (
    OptimizationLog,
    OptimizationLogEntry,
    OptimizationPoint,
)
from spicexplorer.viz.plotting import Optimization_Log_Visualizer
from spicexplorer_api.services.checkpoint_reader import (
    compute_scatter,
    read_csv_checkpoint,
    read_json_checkpoint,
)

# ugf trivially passes (target 2e6); pm is an exact 70°±10° band.
SPECS = [
    {"name": "ugf", "goal": "exceed", "target": 2e6, "tolerance": 0.0},
    {"name": "pm", "goal": "exact", "target": 70.0, "tolerance": 10.0},
]


def _feasible_map(points):
    return {p["iter"]: p["feasible"] for p in points}


# ── CKPT-1: a corner added on resume must not condemn pre-resume trials ─────────
def test_resume_added_corner_does_not_mark_pre_resume_trial_infeasible():
    """Trial 0 ran tt+ss (both pass); ff was added on resume and is absent at
    trial 0. Old code returned False on the first None (ff::ugf) → the passing
    pre-resume design showed red. It must be feasible now."""
    data = {
        "scores": [0.5, 0.6],
        "per_metric": {
            "tt::ugf": [1e8, 1e8],
            "tt::pm": [70.0, 70.0],
            "ss::ugf": [9e7, 9e7],
            "ss::pm": [68.0, 68.0],
            "ff::ugf": [None, 2.5e8],  # ff added on resume → absent at trial 0
            "ff::pm": [None, 65.0],
        },
    }
    pts = compute_scatter(data, "tt::ugf", "tt::pm", SPECS)
    assert _feasible_map(pts) == {0: True, 1: True}


# ── CKPT-1 guard: a corner that RAN but returned NaN is still a real failure ────
def test_simulated_corner_with_nan_spec_stays_infeasible():
    """ss was simulated (ss::pm has a value) but ss::ugf came back NaN → None.
    That is a genuine violation, NOT a skip — the point must be infeasible.
    Distinguishes the fix from a naive 'skip every None'."""
    data = {
        "scores": [0.5],
        "per_metric": {
            "tt::ugf": [1e8],
            "tt::pm": [70.0],
            "ss::ugf": [None],   # ran but measurement failed
            "ss::pm": [68.0],    # proves ss WAS simulated
        },
    }
    pts = compute_scatter(data, "tt::ugf", "tt::pm", SPECS)
    assert _feasible_map(pts) == {0: False}


# ── CKPT-1 guard: a Phase-1 (bare-key) failed sim is still infeasible ───────────
def test_phase1_bare_key_nan_stays_infeasible():
    """Single-corner run, no namespaced keys: a bare ugf NaN at trial 1 is a
    real failed sim, not a not-simulated skip."""
    data = {
        "scores": [0.5, 0.4],
        "per_metric": {
            "ugf": [1e8, None],   # trial 1 failed
            "pm": [70.0, 71.0],
            "power": [1e-3, 1.1e-3],
        },
    }
    pts = compute_scatter(data, "pm", "power", SPECS)
    assert _feasible_map(pts) == {0: True, 1: False}


# ── CKPT-2 mixed log: neither key style condemns the trials that lack it ────────
def test_mixed_bare_and_namespaced_log_each_trial_judged_on_its_own_keys():
    """Old trials logged bare keys; after resume the run went multi-corner and
    logs "tt::spec". A bare-axis scatter judges the old trial on its bare keys
    (the absent tt corner is skipped), and a namespaced-axis scatter judges the
    new trial on tt (the superseded bare key is skipped) — both feasible."""
    data = {
        "scores": [0.5, 0.6],
        "per_metric": {
            "ugf": [1e8, None],
            "pm": [70.0, None],
            "tt::ugf": [None, 1.1e8],
            "tt::pm": [None, 69.0],
        },
    }
    bare = compute_scatter(data, "ugf", "pm", SPECS)
    assert _feasible_map(bare) == {0: True}  # trial 1 skipped (bare None), 0 feasible
    ns = compute_scatter(data, "tt::ugf", "tt::pm", SPECS)
    assert _feasible_map(ns) == {1: True}    # trial 0 skipped (ns None), 1 feasible


# ── CKPT-2: a bare axis vs a namespaced axis realigns instead of going blank ────
def test_scatter_realigns_non_cooccurring_axes_to_a_shared_corner():
    """Pre-resume trial 0 logged bare keys; post-resume trials 1-2 log ss::*. A
    request pairing bare 'ugf' with 'ss::dcgain' never co-occurs, so the naive
    scatter is empty. It must realign both axes onto the ss corner (their shared
    trials) and render the two post-resume points."""
    data = {
        "scores": [0.4, 0.5, 0.6],
        "per_metric": {
            "ugf": [1e8, None, None],          # bare: only trial 0
            "dcgain": [40.0, None, None],
            "ss::ugf": [None, 9e7, 1.0e8],      # namespaced: trials 1,2
            "ss::dcgain": [None, 41.0, 42.0],
        },
    }
    specs = [
        {"name": "ugf", "goal": "exceed", "target": 2e6, "tolerance": 0.0},
        {"name": "dcgain", "goal": "exceed", "target": 24.0, "tolerance": 0.0},
    ]
    pts = compute_scatter(data, "ugf", "ss::dcgain", specs)
    assert [p["iter"] for p in pts] == [1, 2]     # was [] before the fix
    assert all(p["feasible"] for p in pts)


def test_scatter_fast_path_leaves_cooccurring_axes_untouched():
    """The realignment must be inert when the requested axes already share
    trials — no surprise corner swap on a normal multi-corner checkpoint."""
    data = {
        "scores": [-10.0, -5.0],
        "per_metric": {"tt::gain": [55.0, 60.0], "ss::gain": [30.0, 52.0]},
    }
    specs = [{"name": "gain", "goal": "exceed", "target": 50.0, "tolerance": 0.0}]
    pts = compute_scatter(data, "tt::gain", "ss::gain", specs)
    assert [(p["x"], p["y"]) for p in pts] == [(55.0, 30.0), (60.0, 52.0)]


# ── CKPT-1 through the REAL reader: present-NaN key vs absent key ───────────────
# The hand-built ``data`` above carries no presence mask, so it cannot tell "a
# corner ran and every spec came back NaN" (keys PRESENT, value NaN→None) from "a
# corner was never simulated" (keys ABSENT) — both flatten to None. These round-trip
# a real checkpoint so read_json_checkpoint's ``per_metric_present`` mask carries the
# distinction, which is the whole point of the CKPT-1 fix.

def _cell(v):
    return {"curr_val": v, "score": 0.0}


def _entry(score, fit):
    return OptimizationLogEntry(
        point=OptimizationPoint(params={"w": 1.0}, score=score, metadata={}),
        fit_summary=fit,
    )


def _roundtrip(tmp_path, entries):
    vis = Optimization_Log_Visualizer(OptimizationLog(entries))
    p = tmp_path / "ckpt.json"
    vis.save_checkpoint(p)
    return read_json_checkpoint(p)


def test_reader_marks_total_blowup_corner_present_so_scatter_is_infeasible(tmp_path):
    """A corner that RAN but returned NaN at EVERY spec (a non-convergent worst-case
    corner — the dominant AC failure mode) has present keys with curr_val NaN → None.
    The reader must record it PRESENT so feasibility treats it as a real violation,
    not skip it as 'never simulated'. This is the false-positive maskless data misses."""
    nan = float("nan")
    data = _roundtrip(tmp_path, [
        _entry(-1e6, {
            "tt::ugf": _cell(1e8), "tt::pm": _cell(70.0),
            "ss::ugf": _cell(nan), "ss::pm": _cell(nan),  # ss ran, TOTAL blowup
        }),
    ])
    # The mask records ss keys PRESENT even though their values flattened to None.
    assert data["per_metric_present"]["ss::ugf"] == [True]
    assert data["per_metric"]["ss::ugf"] == [None]

    pts = compute_scatter(data, "tt::ugf", "tt::pm", SPECS)
    assert _feasible_map(pts) == {0: False}  # ss ran & failed → infeasible


def test_reader_marks_resume_added_corner_absent_so_pre_resume_trial_feasible(tmp_path):
    """ff is added on resume: absent from trial 0's keys, present at trial 1. The
    reader marks ff ABSENT at trial 0, so the passing pre-resume design stays
    feasible — the resume false-negative CKPT-1 set out to fix."""
    data = _roundtrip(tmp_path, [
        _entry(0.5, {
            "tt::ugf": _cell(1e8), "tt::pm": _cell(70.0),
            "ss::ugf": _cell(9e7), "ss::pm": _cell(68.0),
        }),
        _entry(0.6, {
            "tt::ugf": _cell(1e8), "tt::pm": _cell(70.0),
            "ss::ugf": _cell(9e7), "ss::pm": _cell(68.0),
            "ff::ugf": _cell(2.5e8), "ff::pm": _cell(65.0),  # added on resume
        }),
    ])
    assert data["per_metric_present"]["ff::ugf"] == [False, True]  # absent @ trial 0
    assert data["per_metric"]["ff::ugf"] == [None, 2.5e8]

    pts = compute_scatter(data, "tt::ugf", "tt::pm", SPECS)
    assert _feasible_map(pts) == {0: True, 1: True}  # ff@0 not simulated → skipped


def test_csv_reader_matches_json_on_resume_added_corner(tmp_path):
    """A multi-corner CSV trace is a UNION of columns (to_csv → pd.json_normalize),
    so a resume-added corner back-fills BLANK cells in pre-resume rows — never
    simulated, NOT recorded NaNs. read_csv_checkpoint must NOT claim those blanks
    are 'present' (an all-True mask would resurrect the CKPT-1 resume false-negative
    on CSV and disagree with the JSON reader). It omits the mask so compute_scatter's
    value-proxy skips the resume-added corner — matching the JSON round-trip."""
    entries = [
        _entry(0.5, {"tt::ugf": _cell(1e8), "tt::pm": _cell(70.0)}),
        _entry(0.6, {
            "tt::ugf": _cell(1e8), "tt::pm": _cell(70.0),
            "ff::ugf": _cell(2.5e8), "ff::pm": _cell(65.0),  # added on resume
        }),
    ]
    csv_path = tmp_path / "trace.csv"
    Optimization_Log_Visualizer(OptimizationLog(entries)).to_csv(csv_path)

    data = read_csv_checkpoint(csv_path)
    assert "per_metric_present" not in data          # CSV omits the mask by design
    assert data["per_metric"]["ff::ugf"] == [None, 2.5e8]  # union column, blank @0

    pts = compute_scatter(data, "tt::ugf", "tt::pm", SPECS)
    assert _feasible_map(pts) == {0: True, 1: True}  # parity with the JSON reader
