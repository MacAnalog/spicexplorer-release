"""Additive, idempotent v1→v2 workspace migration.

The migrator ONLY creates missing structure and fills missing manifest fields —
it never moves, renames, or deletes anything. Consequences that make it safe to
run against a live WORK_ROOT:

- ``project.yaml`` stays at the project root (moving it would silently re-anchor
  its relative ``ws_root``), so every existing endpoint, run
  dir, and checkpoint path keeps resolving;
- legacy trees (``auto_save/``, unscoped ``runs/``, ``xschem/generated``) and
  ``.trash/`` are left untouched — trashed v1 projects are migrated **lazily on
  restore** (the ``project_service`` restore hook calls
  :func:`migrate_project`);
- re-running reports zero changes (the tests pin this).

CLI: ``python -m spicexplorer_core.workspace [--work-root PATH] [--dry-run]``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from spicexplorer_core.workspace.layout import (
    scaffold_project,
    scaffold_shared,
    work_root,
)
from spicexplorer_core.workspace.manifest import MANIFEST_NAME, upgrade_manifest


def is_project_dir(p: Path) -> bool:
    """A registry entry is a dir carrying a ``project.yaml`` (v1 identity) or a
    ``manifest.json`` (v2 identity). Anything else under ``projects/`` is noise."""
    return p.is_dir() and ((p / "project.yaml").exists() or (p / MANIFEST_NAME).exists())


def migrate_project(project_dir: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Upgrade ONE project dir in place (additive): scaffold missing v2 dirs +
    seed files, fill missing manifest fields. Idempotent; returns a report."""
    created = scaffold_project(project_dir, dry_run=dry_run)
    _, manifest_changed = upgrade_manifest(project_dir, dry_run=dry_run)
    return {
        "project": project_dir.name,
        "created": created,
        "manifest_upgraded": manifest_changed,
        "changed": bool(created) or manifest_changed,
    }


def migrate_workspace(root: Path | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    """Upgrade every registered project under ``WORK_ROOT/projects`` + ensure the
    ``shared/`` tree. Additive + idempotent; returns an aggregate report."""
    base = (root or work_root()).resolve()
    shared_created = scaffold_shared(base, dry_run=dry_run)
    projects: list[dict[str, Any]] = []
    skipped: list[str] = []
    projects_root = base / "projects"
    if projects_root.is_dir():
        for pd in sorted(projects_root.iterdir()):
            if is_project_dir(pd):
                projects.append(migrate_project(pd, dry_run=dry_run))
            else:
                skipped.append(pd.name)
    changed = bool(shared_created) or any(p["changed"] for p in projects)
    return {
        "work_root": str(base),
        "dry_run": dry_run,
        "shared_created": shared_created,
        "projects": projects,
        "skipped": skipped,
        "changed": changed,
    }
