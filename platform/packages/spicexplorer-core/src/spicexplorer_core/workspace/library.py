"""Shared user library — publish-on-promote, copy-on-import.

``shared/lib/<cell>/<version>/`` is the cross-project reuse shelf. Publishing COPIES
a cell's accepted files there with a provenance record; importing COPIES them into a
project with an ``imported_from`` record. Copy-on-import (NOT a live reference):
an agent always inspects concrete files, and a published version is immutable — the
publisher refuses to overwrite an existing ``<cell>/<version>``.
"""
from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from spicexplorer_core.atomic_io import atomic_write_json
from spicexplorer_core.workspace.layout import shared_root

LIB_META = "lib_meta.json"
IMPORT_MARKER = ".imported_from.json"
# What a published cell version carries (the accepted design + its bindings).
_CELL_FILES = ("netlist.spice", "sizing.yaml", "annotations.yaml")
_CELL_DIRS = ("bindings",)


def lib_root(root: Path | None = None) -> Path:
    """``WORK_ROOT/shared/lib`` (or under an explicit ``root``)."""
    base = (root / "shared" / "lib") if root else (shared_root() / "lib")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _copy_cell(src: Path, dst: Path) -> list[str]:
    dst.mkdir(parents=True, exist_ok=True)
    captured: list[str] = []
    for fname in _CELL_FILES:
        f = src / fname
        if f.is_file():
            shutil.copy2(f, dst / fname)
            captured.append(fname)
    for dname in _CELL_DIRS:
        d = src / dname
        if d.is_dir():
            shutil.copytree(d, dst / dname, dirs_exist_ok=True)
            captured.append(dname + "/")
    return captured


def publish_cell(
    project_dir: Path, cell: str, *, version: str,
    root: Path | None = None, source: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Copy a project cell's accepted files to ``shared/lib/<cell>/<version>/`` with a
    provenance record. Raises ``FileExistsError`` if that version already exists (a
    published version is immutable — bump the version)."""
    src = project_dir / "design" / "cells" / cell
    if not src.is_dir():
        raise FileNotFoundError(f"cell {cell!r} not found in {project_dir}")
    dst = lib_root(root) / cell / version
    if dst.exists():
        raise FileExistsError(f"{cell}/{version} already published (versions are immutable)")
    # Stage the whole version in a temp sibling and rename it into place ONLY after its
    # lib_meta.json is written — so a mid-copy failure (ENOSPC/crash) never leaves a
    # half-published, meta-less directory that is both un-republishable (dst.exists())
    # and invisible to list_library (no meta).
    staging = dst.parent / f".{version}.staging-{uuid.uuid4().hex[:8]}"
    try:
        captured = _copy_cell(src, staging)
        record = {
            "cell": cell, "version": version,
            "published_at": (now or datetime.now()).isoformat(timespec="seconds"),
            "source_project": project_dir.name, "captured": captured, "source": source or {},
        }
        atomic_write_json(staging / LIB_META, record, indent=2)
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, dst)  # atomic dir rename (dst was absent per the check above)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return record


def import_cell(
    cell: str, version: str, project_dir: Path, *,
    root: Path | None = None, as_name: str | None = None,
    overwrite: bool = False, now: datetime | None = None,
) -> dict[str, Any]:
    """Copy a published ``<cell>/<version>`` into a project's ``design/cells/`` with an
    ``imported_from`` marker (copy-on-import). ``as_name`` renames the local cell.

    Refuses to clobber an existing local cell of the same name unless ``overwrite=True``
    (the publish side is immutable, so the import side must not silently destroy a
    hand-tuned local cell)."""
    src = lib_root(root) / cell / version
    if not src.is_dir():
        raise FileNotFoundError(f"{cell}/{version} not in the shared library")
    local = as_name or cell
    dst = project_dir / "design" / "cells" / local
    if dst.exists() and not overwrite:
        raise FileExistsError(
            f"cell {local!r} already exists in the project — pass overwrite=True to replace it")
    _copy_cell(src, dst)
    marker = {
        "cell": cell, "version": version, "imported_as": local,
        "imported_at": (now or datetime.now()).isoformat(timespec="seconds"),
        "source": str(src),
    }
    atomic_write_json(dst / IMPORT_MARKER, marker, indent=2)
    return marker


def list_library(root: Path | None = None) -> list[dict[str, Any]]:
    """Every published ``<cell>/<version>`` (its ``lib_meta.json``), cell then version."""
    base = lib_root(root)
    out: list[dict[str, Any]] = []
    for cell_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        for ver_dir in sorted(p for p in cell_dir.iterdir() if p.is_dir()):
            meta = ver_dir / LIB_META
            if meta.is_file():
                try:
                    out.append(json.loads(meta.read_text()))
                except (OSError, ValueError):
                    continue
    return out
