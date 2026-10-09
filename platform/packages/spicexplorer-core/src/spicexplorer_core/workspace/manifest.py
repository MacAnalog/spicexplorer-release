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

Writers compare-and-swap on ``rev`` (§3.8 rule 2): ``write_manifest(...,
expected_rev=n)`` re-reads the on-disk ``rev`` under a per-project ``fcntl`` lock
and raises :class:`ManifestConflict` instead of overwriting a newer manifest;
:func:`update_manifest` is the read-modify-write loop that retries with fresh
state. Without ``expected_rev`` the write stays unconditional (legacy callers).
"""

from __future__ import annotations

import contextlib
import json
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from spicexplorer_core.atomic_io import atomic_write_json

try:
    import fcntl  # POSIX only (Linux/macOS — the platform's lanes)
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None  # type: ignore[assignment]

MANIFEST_NAME = "manifest.json"
SCHEMA_VERSION = 2
LOCK_NAME = ".manifest.lock"


class ManifestConflict(RuntimeError):
    """The on-disk ``rev`` moved past the one the writer read (a concurrent write won)."""

    def __init__(self, project_dir: Path, expected: int, actual: int):
        super().__init__(
            f"{project_dir / MANIFEST_NAME}: expected rev {expected}, found rev {actual} "
            "(another writer got there first; re-read and retry)"
        )
        self.expected = expected
        self.actual = actual


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


def write_manifest(
    project_dir: Path,
    data: dict[str, Any],
    *,
    expected_rev: int | None = None,
) -> dict[str, Any]:
    """Atomically write the manifest, stamping ``schema_version`` + bumping ``rev``.

    ``rev`` advances past both the caller's copy and the on-disk value, so
    concurrent writers produce a strictly increasing counter. With
    ``expected_rev`` the write is a compare-and-swap: when the
    on-disk ``rev`` is not ``expected_rev`` nothing is written and
    :class:`ManifestConflict` is raised. The read-compare-write runs under a
    per-project ``fcntl`` lock either way.
    """
    with _manifest_lock(project_dir):
        on_disk_rev = _int(read_manifest(project_dir).get("rev"))
        if expected_rev is not None and on_disk_rev != expected_rev:
            raise ManifestConflict(project_dir, expected_rev, on_disk_rev)
        data = dict(data)
        data["schema_version"] = SCHEMA_VERSION
        data["rev"] = max(_int(data.get("rev")), on_disk_rev) + 1
        atomic_write_json(project_dir / MANIFEST_NAME, data, indent=2)
    return data


def update_manifest(
    project_dir: Path,
    fn: Callable[[dict[str, Any]], dict[str, Any] | None],
    *,
    retries: int = 5,
) -> dict[str, Any]:
    """Read-modify-write the manifest with optimistic concurrency (§3.8 rule 2).

    ``fn`` gets a fresh copy of the on-disk manifest and returns the new one (or
    edits the copy in place and returns ``None``). The result is written with
    ``expected_rev`` set to the ``rev`` that was read; on :class:`ManifestConflict`
    the cycle reruns on fresh state, up to ``retries`` more times, then re-raises.
    ``fn`` may therefore run more than once — keep it free of side effects.
    """
    for attempt in range(retries + 1):
        current = read_manifest(project_dir)
        draft = dict(current)
        new = fn(draft)
        try:
            return write_manifest(
                project_dir,
                draft if new is None else new,
                expected_rev=_int(current.get("rev")),
            )
        except ManifestConflict:
            if attempt == retries:
                raise
    raise AssertionError("unreachable")  # pragma: no cover - the loop returns or raises


@contextlib.contextmanager
def _manifest_lock(project_dir: Path) -> Iterator[None]:
    """Exclusive per-project lock around the manifest's read-compare-write. A no-op
    where ``fcntl`` is unavailable — the atomic replace still holds."""
    project_dir.mkdir(parents=True, exist_ok=True)
    if fcntl is None:
        yield
        return
    with open(project_dir / LOCK_NAME, "w") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


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
