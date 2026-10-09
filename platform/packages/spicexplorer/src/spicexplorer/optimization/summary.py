"""`summarize_checkpoint` — a compact, path-free summary of an optimizer run's checkpoint JSON.

The checkpoint is what `Base_Optimizer.save_checkpoint` writes:

    {"schema_version": "1.0.0", "timestamp": "...",
     "optimization_log": [{"point": {"params", "score", "metadata"}, "fit_summary", "log_file"}, ...]}

An agent (the orchestration MCP `optimization_summary` tool) needs the run's shape, not every
trial: how many trials, the best-so-far score trace, the top-N trials with each spec's value and
verdict, and how much of each knob's range the search explored (a best point at the edge of the
explored range suggests the bounds are too tight). The summary is read from the JSON directly
(no optimizer, no project YAML, no plotting library), and `log_file` is never read, so a
legacy checkpoint that stored it as a dict repr is tolerated and no local log path reaches the
payload.

A per-spec verdict is `fit_summary[spec]["score"] > -EPSILON`: the same threshold the scorer's
spec aggregation and the recorded `metadata["feasible"]` use, so "passed" means one thing across
the scorer and this summary.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from spicexplorer.core.utils import EPSILON

# `<name>_<algo>_<budget>_trial<N>[_CRASH|_FINAL]_<timestamp>.json` (Base_Optimizer.get_auto_save_name)
_TRIAL_IN_NAME = re.compile(r"_trial(\d+)(_CRASH|_FINAL)?_")


@dataclass(frozen=True)
class TrialSummary:
    """One trial of the run. `trial` is its 0-based position across the whole run."""

    trial: int
    score: float | None
    params: dict[str, float | None]
    metrics: dict[str, float | None]  # fit_summary[spec]["curr_val"]; None when not finite
    passed: dict[str, bool | None]  # score > -EPSILON; None when the spec has no score


@dataclass(frozen=True)
class CheckpointSummary:
    schema_version: str | None  # as read; a mismatch is reported, not raised
    n_trials: int
    best_score_trace: list[float | None]  # running max; None until a finite score is seen
    top: list[TrialSummary]  # best first
    knob_ranges: dict[str, tuple[float, float]]  # explored (min, max) per knob
    # file name -> why, for each *.json of a checkpoint dir that could not be read as JSON
    skipped: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """JSON-clean: no NaN, and no log path (`log_file` is never read)."""
        return asdict(self)


def summarize_checkpoint(path: str | Path, top: int = 5) -> CheckpointSummary:
    """Summarize a checkpoint JSON, or a run's checkpoint dir, into a `CheckpointSummary`.

    A directory is read as ONE run's autosave chunks — the optimizer empties its in-memory log
    after each autosave, so a long run's trials are split across files — concatenated in trial
    order (the `trial<N>` in each file name); JSON files in it that are not checkpoints are
    skipped, and a file that cannot be read as JSON (not UTF-8, or torn) is skipped and named in
    `skipped`. Raises FileNotFoundError when there is nothing to read and ValueError for a file
    that is not a checkpoint or a negative `top`."""
    if top < 0:
        raise ValueError(f"top must be >= 0, got {top}")
    entries, schema_version, skipped = _read_entries(Path(path))

    trials: list[TrialSummary] = []
    trace: list[float | None] = []
    best: float | None = None
    knob_ranges: dict[str, tuple[float, float]] = {}
    for i, entry in enumerate(entries):
        point = _as_dict(entry.get("point"))
        score = _finite_or_none(point.get("score"))
        if score is not None and (best is None or score > best):
            best = score
        trace.append(best)

        params = {str(k): _finite_or_none(v) for k, v in _as_dict(point.get("params")).items()}
        for k, v in params.items():
            if v is not None:
                lo, hi = knob_ranges.get(k, (v, v))
                knob_ranges[k] = (min(lo, v), max(hi, v))

        metrics: dict[str, float | None] = {}
        passed: dict[str, bool | None] = {}
        for spec, info in _as_dict(entry.get("fit_summary")).items():
            if isinstance(info, dict):  # {"curr_val", "score"} per spec
                metrics[str(spec)] = _finite_or_none(info.get("curr_val"))
                spec_score = _finite_or_none(info.get("score"))
                passed[str(spec)] = None if spec_score is None else spec_score > -float(EPSILON)
            else:  # an old checkpoint may hold bare scalars, which carry no verdict
                metrics[str(spec)] = _finite_or_none(info)
                passed[str(spec)] = None
        trials.append(
            TrialSummary(trial=i, score=score, params=params, metrics=metrics, passed=passed)
        )

    # Best first; an unscored trial sorts last; ties keep trial order (sorted() is stable).
    ranked = sorted(trials, key=lambda t: (t.score is None, -(t.score or 0.0)))
    return CheckpointSummary(
        schema_version=schema_version,
        n_trials=len(trials),
        best_score_trace=trace,
        top=ranked[:top],
        knob_ranges=knob_ranges,
        skipped=skipped,
    )


def _read_entries(path: Path) -> tuple[list[dict[str, Any]], str | None, dict[str, str]]:
    """The entries of a checkpoint file or dir, its schema version, and {file name: why} for each
    file of a dir that could not be read as JSON (skipped; a lone file that cannot is raised)."""
    skipped: dict[str, str] = {}
    if path.is_dir():
        chunks = []
        for f in sorted(path.glob("*.json"), key=_chunk_order):
            try:
                data = _load_json(f)
            except ValueError as exc:  # UnicodeDecodeError, JSONDecodeError
                skipped[f.name] = f"{type(exc).__name__}: {exc}"
                continue
            if _is_checkpoint(data):
                chunks.append(data)
        if not chunks:
            unread = f" ({len(skipped)} unreadable: {', '.join(skipped)})" if skipped else ""
            raise FileNotFoundError(f"no checkpoint JSON in {path}{unread}")
    elif path.is_file():
        data = _load_json(path)
        if not _is_checkpoint(data):
            raise ValueError(
                f"{path.name} is not an optimizer checkpoint (no optimization_log list)"
            )
        chunks = [data]
    else:
        raise FileNotFoundError(f"no checkpoint at {path}")
    entries = [e for c in chunks for e in c["optimization_log"] if isinstance(e, dict)]
    version = chunks[-1].get("schema_version")
    return entries, (None if version is None else str(version)), skipped


def _chunk_order(p: Path) -> tuple[int, int, str]:
    """A chunk's place in trial order. An autosave chunk `trial<N>` ends at trial N; a
    `trial<N>_CRASH` / `trial<N>_FINAL` ends at trial N-1 when trial N raised or was interrupted,
    so it sorts as N-1, after a plain chunk of that number. Within one run's dir this is the order
    the files were written; it also puts a resumed segment's chunks (numbered on from the prior
    trials) after a prior segment's `_CRASH` of the same number."""
    m = _TRIAL_IN_NAME.search(p.name)
    if m is None:
        return (-1, 0, p.name)
    end = int(m.group(1)) - (1 if m.group(2) else 0)
    return (end, 1 if m.group(2) else 0, p.name)


def _load_json(p: Path) -> Any:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_checkpoint(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(data.get("optimization_log"), list)


def _as_dict(v: Any) -> dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _finite_or_none(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None
