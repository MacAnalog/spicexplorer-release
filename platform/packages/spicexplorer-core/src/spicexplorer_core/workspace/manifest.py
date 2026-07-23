"""``manifest.json`` — the project's identity record (schema v2).

v2 makes the manifest (not the optimizer YAML) the project identity: a
project that only annotates or analyzes a netlist is still a project. Schema:

- v1 (legacy): ``{id, slug, name, created, updated, source, schema_version: 1}``
  — written by the pre-v2 ``project_service``.
- v2 adds: ``rev`` (monotonic write counter — the optimistic-concurrency
  seam), ``default_job`` (project-relative path of the default job config;
  ``"project.yaml"`` — which stays at the project root) and ``default_pdk``
  (a pointer only; real PDK bindings are per-cell).

Every write is atomic (:func:`spicexplorer_core.atomic_io.atomic_write_json`)
and bumps ``rev`` — a torn manifest must never equal a vanished project. Unknown
keys are always preserved (forward compatibility both ways).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from spicexplorer_core.atomic_io import atomic_write_json

MANIFEST_NAME = "manifest.json"
SCHEMA_VERSION = 2


def read_manifest(project_dir: Path) -> dict[str, Any]:
    """Read ``manifest.json`` tolerantly: missing/torn → ``{}`` (never raises)."""
    p = project_dir / MANIFEST_NAME
    if p.exists():
        try:
            data = json.loads(p.read_text())
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def write_manifest(project_dir: Path, data: dict[str, Any]) -> dict[str, Any]:
    """Atomically write the manifest, stamping ``schema_version`` + bumping ``rev``.

    ``rev`` advances past both the caller's copy and the on-disk value, so
    concurrent read-modify-write cycles produce a strictly increasing counter
    (full compare-and-swap enforcement is intentionally not implemented here).
    """
    on_disk = read_manifest(project_dir)
    data = dict(data)
    data["schema_version"] = SCHEMA_VERSION
    data["rev"] = max(_int(data.get("rev")), _int(on_disk.get("rev"))) + 1
    atomic_write_json(project_dir / MANIFEST_NAME, data, indent=2)
    return data


def new_manifest(
    project_id: str,
    name: str,
    *,
    source: dict[str, Any],
    now: str,
) -> dict[str, Any]:
    """A fresh v2 manifest dict (not yet written — pass to :func:`write_manifest`)."""
    return {
        "id": project_id,
        "slug": project_id.rsplit("-", 1)[0],
        "name": name,
        "created": now,
        "updated": now,
        "source": source,
        "schema_version": SCHEMA_VERSION,
        "rev": 0,  # write_manifest bumps to 1
        "default_job": "project.yaml",
        "default_pdk": None,
    }


def upgrade_manifest(project_dir: Path, *, dry_run: bool = False) -> tuple[dict[str, Any], bool]:
    """Fill any missing v2 fields in an existing (possibly v1 / absent) manifest.

    Additive only: existing values — including unknown keys — are preserved
    verbatim; a missing manifest is synthesized from the directory name. Returns
    ``(manifest, changed)``; writes (atomically) only when something changed.
    """
    man = read_manifest(project_dir)
    upgraded = dict(man)
    pid = str(upgraded.get("id") or project_dir.name)
    upgraded.setdefault("id", pid)
    upgraded.setdefault("slug", _slug_of(pid))
    upgraded.setdefault("name", pid)
    upgraded.setdefault("source", {"kind": "unknown"})
    upgraded.setdefault("default_job", "project.yaml")
    upgraded.setdefault("default_pdk", None)
    upgraded.setdefault("rev", 0)
    changed = upgraded != man or _int(man.get("schema_version")) < SCHEMA_VERSION
    if changed and not dry_run:
        upgraded = write_manifest(project_dir, upgraded)
    return upgraded, changed


def _slug_of(project_id: str) -> str:
    # <slug>-<id8> → slug; anything else → the id itself.
    m = re.fullmatch(r"(.+)-[0-9a-f]{8}", project_id)
    return m.group(1) if m else project_id


def _int(v: Any) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0
