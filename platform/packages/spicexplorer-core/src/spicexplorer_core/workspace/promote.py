"""Promotion protocol — accept a design snapshot.

Promoting an accepted design writes an immutable, **sortable** snapshot under
``design/history/<hid>/`` (each named cell's netlist + sizing + curated annotations,
self-contained) and then swaps the ``design/history/current.json`` pointer to it —
the whole read-promote-write held under a **per-project fcntl lock** so two agents
can't interleave a half-promotion. The pointer is a small JSON file (not a symlink)
so it survives a Docker bind mount. History is append-only; rollback = promote an
older snapshot again.
"""
from __future__ import annotations

import contextlib
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from spicexplorer_core.atomic_io import atomic_write_json

try:
    import fcntl  # POSIX only (Linux/macOS — the platform's lanes)
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None  # type: ignore[assignment]

HISTORY_DIR = "design/history"
CURRENT_POINTER = "current.json"
LOCK_NAME = ".promote.lock"
# The cell files a snapshot captures so a history entry is a faithful restore point.
_SNAPSHOT_FILES = ("netlist.spice", "sizing.yaml", "annotations.yaml")


def _history_id(now: datetime | None = None) -> str:
    """Sortable, collision-free snapshot id: ``{YYYYMMDD-HHMMSS}-{micros}-{hex4}`` (a
    ULID stand-in with no extra dependency). Microsecond precision keeps ids lexically
    ordered by promote time even for two promotions within the same second."""
    dt = now or datetime.now()
    return f"{dt.strftime('%Y%m%d-%H%M%S')}-{dt.microsecond:06d}-{uuid.uuid4().hex[:4]}"


@contextlib.contextmanager
def _project_lock(project_dir: Path) -> Iterator[None]:
    """Exclusive per-project lock held across the whole read-promote-write.
    A no-op where ``fcntl`` is unavailable — the atomic pointer swap still holds."""
    project_dir.mkdir(parents=True, exist_ok=True)
    if fcntl is None:
        yield
        return
    lock = project_dir / LOCK_NAME
    with open(lock, "w") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _cell_names(project_dir: Path) -> list[str]:
    base = project_dir / "design" / "cells"
    return sorted(p.name for p in base.iterdir() if p.is_dir()) if base.is_dir() else []


def promote(
    project_dir: Path,
    *,
    cells: list[str] | None = None,
    label: str | None = None,
    payload: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Snapshot the accepted design of ``cells`` (default: all) into a new sortable
    ``design/history/<hid>/`` and swap ``current`` to it — atomically, under lock.
    Returns the promotion record."""
    stamp = (now or datetime.now()).isoformat(timespec="seconds")
    names = cells if cells is not None else _cell_names(project_dir)
    with _project_lock(project_dir):
        for _ in range(8):  # retry on the astronomically rare same-µs + hex4 collision
            hid = _history_id(now)
            snap = project_dir / HISTORY_DIR / hid
            try:
                snap.mkdir(parents=True, exist_ok=False)
                break
            except FileExistsError:
                continue
        else:
            raise RuntimeError("could not mint a unique promotion id")
        captured: list[str] = []
        for name in names:
            src = project_dir / "design" / "cells" / name
            dst = snap / "cells" / name
            for fname in _SNAPSHOT_FILES:
                f = src / fname
                if f.is_file():
                    dst.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dst / fname)
                    captured.append(f"{name}/{fname}")
        record = {
            "id": hid, "at": stamp, "label": label,
            "cells": names, "captured": captured, "payload": payload or {},
        }
        atomic_write_json(snap / "promotion.json", record, indent=2)
        # Swap the current pointer LAST — an atomic rename, so a reader sees either the
        # old snapshot or the new one, never a half-written pointer.
        atomic_write_json(
            project_dir / HISTORY_DIR / CURRENT_POINTER,
            {"current": hid, "at": stamp, "label": label}, indent=2,
        )
    return record


def current_promotion(project_dir: Path) -> dict[str, Any] | None:
    """The current-accepted snapshot's ``promotion.json`` (via the pointer), or ``None``."""
    import json

    ptr = project_dir / HISTORY_DIR / CURRENT_POINTER
    try:
        hid = json.loads(ptr.read_text()).get("current")
    except Exception:
        return None
    if not hid:
        return None
    try:
        return json.loads((project_dir / HISTORY_DIR / hid / "promotion.json").read_text())
    except Exception:
        return None


def list_promotions(project_dir: Path) -> list[dict[str, Any]]:
    """Every promotion snapshot, newest first (ids sort by promote time)."""
    import json

    base = project_dir / HISTORY_DIR
    out: list[dict[str, Any]] = []
    if base.is_dir():
        for d in sorted((p for p in base.iterdir() if p.is_dir()), reverse=True):
            rec = d / "promotion.json"
            if rec.is_file():
                with contextlib.suppress(Exception):
                    out.append(json.loads(rec.read_text()))
    return out
