"""Read and normalize checkpoint data from both JSON (OptimizationLog) and CSV trace files."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, cast

import pandas as pd

from spicexplorer_api.services.num import safe_float as _safe_float

# ---------- JSON checkpoint reader ----------

def read_json_checkpoint(path: Path, limit: int | None = None) -> dict[str, Any]:
    from spicexplorer.viz.plotting import Optimization_Log_Visualizer

    vis = Optimization_Log_Visualizer.load_checkpoint(path)
    log = vis.optimization_log

    scores, best_scores, iterations = [], [], []
    per_metric: dict[str, list[float | None]] = {}
    # Per-metric KEY presence, in lockstep with per_metric. This is the ONLY signal
    # that tells "a corner ran this trial and its spec came back NaN" (key present,
    # value NaN→None) apart from "the corner was never simulated this trial" (key
    # absent) — the None-flattening below erases that distinction, and scatter
    # feasibility needs it to avoid condemning resume-added corners OR excusing a
    # total-blowup corner (CKPT-1).
    per_present: dict[str, list[bool]] = {}
    params_out: dict[str, list[float | None]] = {}
    best = -math.inf

    for i, entry in enumerate(log):
        if limit and i >= limit:
            break  # honor `limit` like the CSV reader's df.head(limit)
        s = _safe_float(entry.get_score())
        if s is not None and s > best:
            best = s
        scores.append(s)
        best_scores.append(best if math.isfinite(best) else None)
        iterations.append(i)

        # Entries may not all carry the same keys (e.g. a pre-Phase-2 checkpoint with
        # bare spec keys resumed into a multi-corner run with "<corner>::<spec>" keys).
        # Pad every series to this entry's position so per_metric[k][i] always lines
        # up with iteration i — bare setdefault().append() silently compacted sparse
        # keys and misaligned scatter/feasibility downstream.
        pos = len(scores) - 1

        fs = entry.fit_summary or {}
        for metric, vals in fs.items():
            # Some optimizers (e.g. the Bode path) store bare scalars in fit_summary
            # rather than {"curr_val": ...} dicts — skip those instead of crashing.
            if not isinstance(vals, dict):
                continue
            series = per_metric.setdefault(metric, [])
            series.extend([None] * (pos - len(series)))
            series.append(_safe_float(vals.get("curr_val")))

            # Record that this key was PRESENT at this trial (regardless of NaN).
            pres = per_present.setdefault(metric, [])
            pres.extend([False] * (pos - len(pres)))
            pres.append(True)

        for pname, pval in entry.get_params().items():
            series = params_out.setdefault(pname, [])
            series.extend([None] * (pos - len(series)))
            series.append(_safe_float(pval))

    # trailing pad: a key absent from the final entries must not leave a short series
    for series in per_metric.values():
        series.extend([None] * (len(scores) - len(series)))
    for pres in per_present.values():
        pres.extend([False] * (len(scores) - len(pres)))
    for series in params_out.values():
        series.extend([None] * (len(scores) - len(series)))

    return {
        "scores": scores,
        "best_scores": best_scores,
        "iterations": iterations,
        "per_metric": per_metric,
        "per_metric_present": per_present,
        "params": params_out,
        "n_iters": len(scores),
    }


# ---------- CSV trace reader ----------

METRIC_PREFIX = "fit_summary."
METRIC_VALUE_SUFFIX = ".curr_val"
PARAM_PREFIX = "point.params."


def read_csv_checkpoint(path: Path, limit: int | None = None) -> dict[str, Any]:
    df = pd.read_csv(path)
    if limit:
        df = df.head(limit)

    scores, best_scores, iterations = [], [], []
    per_metric: dict[str, list[float | None]] = {}
    params_out: dict[str, list[float | None]] = {}
    best = -math.inf

    metric_cols = [c for c in df.columns if c.startswith(METRIC_PREFIX) and c.endswith(METRIC_VALUE_SUFFIX)]
    param_cols = [c for c in df.columns if c.startswith(PARAM_PREFIX)]
    metric_names = [c[len(METRIC_PREFIX):-len(METRIC_VALUE_SUFFIX)] for c in metric_cols]
    param_names = [c[len(PARAM_PREFIX):] for c in param_cols]

    for i, row in df.iterrows():
        s = _safe_float(row.get("point.score"))
        if s is not None and s > best:
            best = s
        scores.append(s)
        best_scores.append(best if math.isfinite(best) else None)
        # `i` is a pandas index label (numpy int) — cast to a native int so the JSON
        # body and the CheckpointData response_model (`iterations: list[int]`) are clean.
        iterations.append(int(cast(int, i)))

        for mn, mc in zip(metric_names, metric_cols):
            per_metric.setdefault(mn, []).append(_safe_float(row.get(mc)))
        for pn, pc in zip(param_names, param_cols):
            params_out.setdefault(pn, []).append(_safe_float(row.get(pc)))

    # Deliberately NO per_metric_present for CSV. A CSV trace is a UNION of columns
    # (Optimization_Log_Visualizer.to_csv → pd.json_normalize), so a blank cell is
    # ambiguous: a corner ADDED on resume back-fills blank cells in pre-resume rows
    # (never simulated → must be skipped) exactly like a recorded NaN (a real
    # failure). CSV flattened that distinction at write time — it cannot be
    # recovered here. Omitting the mask lets compute_scatter fall back to the
    # value-proxy, which skips a resume-added corner (correct) and still fails a
    # single-corner blank (a bare key with no namespaced siblings → treated as a
    # recorded NaN). Marking every column present instead would resurrect the CKPT-1
    # resume false-negative on CSV — the JSON reader (the real autosave/resume path)
    # is where the accurate presence mask lives.
    return {
        "scores": scores,
        "best_scores": best_scores,
        "iterations": iterations,
        "per_metric": per_metric,
        "params": params_out,
        "n_iters": len(scores),
    }


# ---------- unified loader ----------

def read_checkpoint(path: Path, limit: int | None = None) -> dict[str, Any]:
    if path.suffix == ".json":
        return read_json_checkpoint(path, limit=limit)
    return read_csv_checkpoint(path, limit=limit)


# ---------- envelope ----------

def compute_envelope(
    data: dict[str, Any],
    target_specs: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Per-metric best-ever value across all sampled designs, independent of other specs."""
    results = []
    per_metric = data.get("per_metric", {})

    spec_map: dict[str, dict] = {}
    if target_specs:
        for s in target_specs:
            spec_map[s["name"]] = s

    for metric, values in per_metric.items():
        clean = [v for v in values if v is not None]
        if not clean:
            continue
        # A multi-corner checkpoint namespaces metric keys as "<corner>::<spec>";
        # the spec definition (target/goal/tolerance) is corner-independent, so
        # look it up by the bare spec name. Single-corner keys pass through as-is.
        spec = spec_map.get(metric, spec_map.get(metric.split("::")[-1], {}))
        goal = spec.get("goal", "exceed")
        target = spec.get("target")

        if goal == "minimize":
            best_ever = min(clean)
        elif goal == "exact" and target is not None:
            # Closest sample to the target — NOT the max. An exact-goal spec (e.g.
            # phase margin 60°±10°) would otherwise report a 120° outlier as "best".
            best_ever = min(clean, key=lambda v: abs(v - target))
        else:
            best_ever = max(clean)

        passes: bool | None = None
        if target is not None:
            # Default 0, matching TargetSpec: an omitted tolerance means the target IS the
            # constraint. A 5 % default here would redraw a checkpoint's pass/fail band
            # differently from the run that produced it.
            tol = spec.get("tolerance", 0.0)
            if goal == "exceed":
                passes = best_ever >= target - tol
            elif goal == "minimize":
                passes = best_ever <= target + tol
            else:  # exact
                passes = abs(best_ever - target) <= tol

        results.append({
            "metric": metric,
            "best_ever": best_ever,
            "target": target,
            "goal": goal,
            "passes": passes,
        })
    return results


# ---------- scatter ----------

def _populated_at(series: list[float | None] | None) -> set[int]:
    """Trial indices where ``series`` holds a value (not None)."""
    return {i for i, v in enumerate(series or []) if v is not None}


def _resolve_scatter_axes(
    per_metric: dict[str, list[float | None]],
    metric_x: str,
    metric_y: str,
) -> tuple[str, str]:
    """Choose the actual ``(x_key, y_key)`` to plot for a possibly mixed-era log.

    Fast path: if the two requested keys already hold a value at some common
    trial, use them unchanged. Otherwise the caller paired axes that never
    co-occur — e.g. a Phase-1 bare ``spec`` (only in pre-resume trials) against a
    ``"<corner>::spec"`` key (only in post-resume trials) — which naively yields a
    scatter with ZERO points (CKPT-2). Realign onto same-named keys that DO share
    trials (preferring one corner) so the chart renders the coherent overlap
    instead of blank. Returns the request unchanged when nothing co-occurs (an
    honest empty).
    """
    if _populated_at(per_metric.get(metric_x)) & _populated_at(per_metric.get(metric_y)):
        return metric_x, metric_y

    def _bare(k: str) -> str:
        return k.split("::")[-1]

    def _corner(k: str) -> str | None:
        return k.split("::")[0] if "::" in k else None

    x_cands = [k for k in per_metric if _bare(k) == _bare(metric_x) and _populated_at(per_metric[k])]
    y_cands = [k for k in per_metric if _bare(k) == _bare(metric_y) and _populated_at(per_metric[k])]

    best: tuple[tuple[int, bool], str, str] | None = None
    for xk in x_cands or [metric_x]:
        xp = _populated_at(per_metric.get(xk))
        for yk in y_cands or [metric_y]:
            overlap = len(xp & _populated_at(per_metric.get(yk)))
            if overlap == 0:
                continue
            # Rank by shared-trial count, then prefer one physical corner.
            rank = (overlap, _corner(xk) is not None and _corner(xk) == _corner(yk))
            if best is None or rank > best[0]:
                best = (rank, xk, yk)
    return (best[1], best[2]) if best is not None else (metric_x, metric_y)


def compute_scatter(
    data: dict[str, Any],
    metric_x: str,
    metric_y: str,
    target_specs: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return all design points in 2D metric space with feasibility tags."""
    per_metric = data.get("per_metric", {})
    # Accurate key-presence from the readers (None only for legacy/hand-built data).
    present = data.get("per_metric_present")
    scores = data.get("scores", [])

    metric_x, metric_y = _resolve_scatter_axes(per_metric, metric_x, metric_y)
    xs = per_metric.get(metric_x, [])
    ys = per_metric.get(metric_y, [])

    # Build spec map for feasibility check (against ALL specs that have target info)
    spec_map: dict[str, dict] = {}
    if target_specs:
        for s in target_specs:
            spec_map[s["name"]] = s

    def _corners_simulated_at(i: int) -> set[str]:
        """Corner prefixes with ≥1 non-None value at trial ``i`` — the *maskless*
        proxy for "which corners ran". Used only when ``per_metric_present`` is
        absent (legacy/hand-built ``data``); the readers now supply the exact mask.
        NOTE: this proxy cannot see a corner that ran but returned NaN at EVERY spec
        (no non-None value → looks un-simulated); the mask path below can.
        """
        seen: set[str] = set()
        for mn, vals in per_metric.items():
            if "::" not in mn:
                continue
            v = vals[i] if i < len(vals) else None
            if v is not None:
                seen.add(mn.split("::", 1)[0])
        return seen

    def _ran(mn: str, i: int) -> bool:
        """Was metric ``mn`` actually recorded for trial ``i`` (vs never simulated)?

        With the reader's key-presence mask this is exact: present → the corner ran
        and a None here is a NaN measurement (a real violation); absent → the corner
        was never simulated this trial (resume-added corner, or a bare key superseded
        once the run went multi-corner) → skip. Without a mask, fall back to the
        value proxy: a corner "ran" if any of its keys held a value this trial, and a
        bare key is superseded once the trial produced any namespaced value.
        """
        if present is not None:
            p = present.get(mn)
            return bool(p[i]) if (p is not None and i < len(p)) else False
        if "::" in mn:
            return mn.split("::", 1)[0] in _corners_simulated_at(i)
        return not _corners_simulated_at(i)

    def _fails_spec(spec: dict, target: float, v: float) -> bool:
        goal = spec.get("goal", "exceed")
        # Default 0, matching TargetSpec: an omitted tolerance means the target IS the
        # constraint. A 5 % default here would redraw a checkpoint's pass/fail band
        # differently from the run that produced it.
        tol = spec.get("tolerance", 0.0)
        if goal == "exceed":
            return v < target - tol
        if goal == "minimize":
            return v > target + tol
        if goal == "exact":
            return abs(v - target) > tol
        return False

    def _is_feasible(i: int) -> bool:
        # A point is feasible only if it passes at every corner it was SIMULATED at
        # (CKPT-1). A None value is a real violation only when the key WAS recorded
        # this trial (the corner ran, the measurement was NaN); a key absent this
        # trial — a resume-added corner or a superseded bare key — is not judgeable
        # and is skipped, never condemned.
        for mn, vals in per_metric.items():
            # Multi-corner keys are "<corner>::<spec>": each corner's value is
            # checked against the (corner-independent) bare-spec target.
            spec = spec_map.get(mn) or spec_map.get(mn.split("::")[-1])
            if spec is None:
                continue
            target = spec.get("target")
            if target is None:
                continue
            v = vals[i] if i < len(vals) else None
            if v is None:
                if _ran(mn, i):
                    return False   # recorded but NaN → a real violation
                continue           # never simulated this trial → skip
            if _fails_spec(spec, target, v):
                return False
        return True

    points = []
    n = min(len(xs), len(ys))
    for i in range(n):
        xv, yv = xs[i], ys[i]
        if xv is None or yv is None:
            continue
        points.append({
            "x": xv,
            "y": yv,
            "feasible": _is_feasible(i),
            "score": scores[i] if i < len(scores) else None,
            "iter": i,
        })
    return points
