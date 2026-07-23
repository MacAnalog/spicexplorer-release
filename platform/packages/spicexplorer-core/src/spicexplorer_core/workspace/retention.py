"""Artifact-tier retention + pruning — the run store's GC.

Every envelope-marked run records a ``retention`` tier in its envelope:

  ``full``          keep every artifact (elected / promoted runs)
  ``metrics_only``  keep the record + history (``run.json``, ``events.ndjson``,
                    ``checkpoints/``, ``config_snapshot.yaml``, ``run.log``) and
                    drop the heavy simulation WAVEFORMS — the ``sim/`` subtree,
                    the ``.raw`` disk hog
  ``none``          keep only ``run.json`` (the provenance record); drop the rest

:func:`prune_run` enforces one run's tier; :func:`prune_workspace` walks every
*terminal* run under ``WORK_ROOT`` and enforces its tier once it is older than a
grace period. Both are idempotent (a ``retention_pruned`` marker in ``run.json``
records what was applied) and refuse to touch a ``running`` run, a ``full``-tier
run, or a legacy run with no envelope. A cache without GC would just recreate
the unbounded-``keep_raw`` disk problem, so the GC ships with the store.

Pruning only ever deletes paths strictly *inside* a run dir; the project's
``.objects/`` provenance store lives one level up and is never touched.

Per-trial candidate rows are NOT directories — they are already columnar rows in
``events.ndjson``. :func:`iter_candidates` is the
stable reader for them, and ``events.ndjson`` survives a ``metrics_only`` prune.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Mapping

from spicexplorer_core.workspace.runs import read_run_record, write_run_record

RETENTION_TIERS: tuple[str, ...] = ("full", "metrics_only", "none")
RUN_RECORD = "run.json"
# Heavy simulation output a metrics_only run drops (dir names directly under the
# run dir). Both the optimizer (per-corner ``run_<n>_<tb>__<corner>/``) and manual
# sims write their ``.raw`` waveforms under ``sim/``.
WAVEFORM_DIRS: tuple[str, ...] = ("sim",)
# Default grace: a terminal run must be older than this before auto-pruning.
DEFAULT_GRACE_S = 7 * 24 * 3600.0
_TERMINAL_EXCLUDE = {"", "running"}


def is_terminal(record: Mapping[str, Any]) -> bool:
    """A run is terminal once its writer stopped — ``status`` present and not
    ``running``. Absent/torn status → not terminal; a stuck ``running`` run is
    left for the owner-liveness reconciler, never pruned here."""
    status = record.get("status")
    return isinstance(status, str) and status not in _TERMINAL_EXCLUDE


def run_tier(record: Mapping[str, Any]) -> str | None:
    """The retention tier to enforce, or ``None`` to leave the run alone. Only
    envelope-marked runs are eligible; a legacy run (no ``envelope``) returns ``None``
    so the GC never deletes legacy artifacts. An unknown tier value → ``"full"``."""
    if "envelope" not in record:
        return None
    tier = record.get("retention")
    return tier if tier in RETENTION_TIERS else "full"


def already_applied(record: Mapping[str, Any], tier: str) -> bool:
    """Has this exact tier already been pruned (idempotency marker)?"""
    marker = record.get("retention_pruned")
    return isinstance(marker, dict) and marker.get("tier") == tier


def _removal_targets(run_dir: Path, tier: str) -> list[Path]:
    if tier == "full":
        return []
    if tier == "metrics_only":
        out = [run_dir / d for d in WAVEFORM_DIRS if (run_dir / d).exists()]
        out += [p for p in run_dir.glob("*.raw") if p.is_file()]
        return out
    if tier == "none":
        return [c for c in run_dir.iterdir() if c.name != RUN_RECORD]
    raise ValueError(f"unknown retention tier: {tier!r}")


def _path_bytes(p: Path) -> int:
    if p.is_file():
        try:
            return p.stat().st_size
        except OSError:
            return 0
    total = 0
    for f in p.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def _remove(p: Path) -> None:
    if p.is_dir() and not p.is_symlink():
        shutil.rmtree(p, ignore_errors=True)
    else:
        try:
            p.unlink()
        except OSError:
            pass


def prune_run(
    run_dir: Path,
    tier: str | None = None,
    *,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Enforce a single run's retention tier (idempotent). ``tier`` overrides the
    run's recorded tier when given. Returns a report; only deletes paths strictly
    inside ``run_dir``."""
    record = read_run_record(run_dir)
    resolved = tier if tier is not None else run_tier(record)
    report: dict[str, Any] = {
        "run": run_dir.name, "tier": resolved,
        "removed": [], "freed_bytes": 0, "pruned": False,
    }
    if not is_terminal(record):  # never delete a live writer's in-flight artifacts
        report["skipped"] = "run not terminal"
        return report
    if resolved is None or resolved == "full":
        report["skipped"] = "tier is full / not eligible"
        return report
    if resolved not in RETENTION_TIERS:
        raise ValueError(f"unknown retention tier: {resolved!r}")
    if already_applied(record, resolved):
        report["skipped"] = "already applied"
        return report

    rd = run_dir.resolve()
    # Keep ONLY targets that are genuinely direct children of the run dir (the safety
    # rule), and filter BEFORE reporting — so `removed`/`freed_bytes` and the
    # idempotency marker never count a path the delete loop would skip (e.g. a symlink
    # resolving outside the run, whose bytes/name would otherwise inflate the report).
    targets = [t for t in _removal_targets(run_dir, resolved) if t.resolve().parent == rd]
    report["removed"] = sorted(t.name for t in targets)
    report["freed_bytes"] = sum(_path_bytes(t) for t in targets)
    if dry_run:
        report["dry_run"] = True
        return report

    for t in targets:
        _remove(t)
    stamp = (now or datetime.now()).isoformat(timespec="seconds")
    record["retention_pruned"] = {
        "tier": resolved, "at": stamp, "freed_bytes": report["freed_bytes"],
    }
    try:
        write_run_record(run_dir, record)
    except OSError:
        pass
    report["pruned"] = True
    return report


def _iter_run_dirs(base: Path) -> Iterator[Path]:
    """Every run dir under a WORK_ROOT: project-scoped ``projects/<pid>/runs/*``
    and the legacy unscoped ``runs/*``."""
    projects = base / "projects"
    if projects.is_dir():
        for pd in sorted(projects.iterdir()):
            rr = pd / "runs"
            if rr.is_dir():
                for rd in sorted(rr.iterdir()):
                    if (rd / RUN_RECORD).exists():
                        yield rd
    rr = base / "runs"
    if rr.is_dir():
        for rd in sorted(rr.iterdir()):
            if (rd / RUN_RECORD).exists():
                yield rd


def _run_age_s(run_dir: Path, record: Mapping[str, Any], now_ts: float) -> float:
    ended = record.get("ended")
    if isinstance(ended, str):
        try:
            return now_ts - datetime.fromisoformat(ended).timestamp()
        except ValueError:
            pass
    try:
        return now_ts - (run_dir / RUN_RECORD).stat().st_mtime
    except OSError:
        return 0.0


def prune_workspace(
    root: Path | None = None,
    *,
    older_than_s: float = DEFAULT_GRACE_S,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Walk every terminal run under ``root`` (default ``WORK_ROOT``) and enforce
    its retention tier once it is older than ``older_than_s``. Additive + safe:
    skips ``running``/``full``/legacy/already-pruned/too-recent runs."""
    from spicexplorer_core.workspace.layout import work_root

    base = (root or work_root()).resolve()
    now_dt = now or datetime.now()
    now_ts = now_dt.timestamp()
    pruned: list[dict[str, Any]] = []
    freed = 0
    for run_dir in _iter_run_dirs(base):
        record = read_run_record(run_dir)
        if not is_terminal(record):
            continue
        tier = run_tier(record)
        if tier is None or tier == "full" or already_applied(record, tier):
            continue
        if _run_age_s(run_dir, record, now_ts) < older_than_s:
            continue
        rep = prune_run(run_dir, tier, dry_run=dry_run, now=now_dt)
        if rep.get("pruned") or (dry_run and rep.get("removed")):
            pruned.append(rep)
            freed += rep.get("freed_bytes", 0)
    return {
        "work_root": str(base), "dry_run": dry_run, "older_than_s": older_than_s,
        "runs_pruned": len(pruned), "freed_bytes": freed, "pruned": pruned,
    }


def iter_candidates(run_dir: Path) -> Iterator[dict[str, Any]]:
    """Yield an optimizer run's per-trial candidate rows — the columnar
    "candidates table" view. These are already rows, not
    directories: each is an ``events.ndjson`` entry carrying an ``iter`` key
    (``{iter, score, best_score, metrics, …}``). A stable reader so callers do not
    couple to the raw SSE event stream; the rows survive a ``metrics_only`` prune."""
    events = run_dir / "events.ndjson"
    try:
        with events.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and "iter" in row:
                    yield row
    except OSError:
        return


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m spicexplorer_core.workspace.retention",
        description="Enforce run artifact-retention tiers under a WORK_ROOT (GC).",
    )
    ap.add_argument("--work-root", type=Path, default=None,
                    help="WORK_ROOT to prune (default: $WORK_ROOT, else <repo>/work)")
    ap.add_argument("--older-than-days", type=float, default=DEFAULT_GRACE_S / 86400,
                    help="only prune runs whose terminal age exceeds this (default 7)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be pruned without deleting anything")
    args = ap.parse_args(argv)
    report = prune_workspace(
        args.work_root, older_than_s=args.older_than_days * 86400, dry_run=args.dry_run)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
