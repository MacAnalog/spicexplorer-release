"""The WORK_ROOT v2 directory schema + idempotent scaffolding.

A project dir is
self-contained and portable (trash/fork/copy move the whole dir), so every
path here is project-relative. Nothing in this module moves or deletes: scaffold
is create-missing-only, which is what makes the v1→v2 migration additive.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from spicexplorer_core.paths import project_root

WORK_ROOT_ENV = "WORK_ROOT"
SCRATCH_ENV = "SX_SCRATCH"

_log = logging.getLogger(__name__)
# Fallback roots already announced — work_root() runs on every request, say it once.
_FALLBACK_NOTED: set[Path] = set()

# --- v2 project-relative directories ------------------------------------------------
# Storage classes: design state (spec/topology/design/testbenches/layout),
# job inputs (jobs/), append-only runs (runs/), disposable caches (analyses/),
# agent context (context/). The v1 dirs (spice/xschem/scratch) are DELIBERATELY
# part of the schema: the root project.yaml's netlists keep resolving there.
PROJECT_DIRS_V2: tuple[str, ...] = (
    "spec",
    "topology",
    "design/cells",
    "design/history",
    "testbenches",
    "jobs",
    "runs",
    "analyses",
    "layout",
    "context",
    # v1 compatibility dirs — kept, not legacy debt (see module docstring).
    "spice",
    "xschem",
    "scratch",
)

# --- workspace-level shared dirs (cross-project, never inside a project) -------------
SHARED_DIRS: tuple[str, ...] = (
    "shared/gmid-luts",
    "shared/xschem-cache",
    "shared/lib",
)

# Seed files created (only if missing) inside a scaffolded project.
_DECISIONS_REL = "context/decisions.ndjson"
_PROJECT_MD_REL = "context/PROJECT.md"

_PROJECT_MD_STUB = """\
> **GENERATED** — the project's agent-facing context surface.
> Do NOT hand-edit this file:
> append decision events to `decisions.ndjson` (one JSON object per line, one
> `write()` per event) and let the renderer regenerate this document. Until the
> renderer lands this stub only marks the contract.
"""


def work_root() -> Path:
    """The single root for all MUTABLE webapp/agent state.

    ``WORK_ROOT`` env (the Docker backend sets it to ``/work``, a host bind
    mount) else ``<repo>/work`` (gitignored). This is the canonical resolver —
    the API's ``app_config.work_root`` delegates here so every process agrees.

    The ``<repo>/work`` default is only taken when this user can write there: a
    shared install exports ``SPICEXPLORER_ROOT`` at a checkout its members may only
    read, so the default falls back to ``$SX_SCRATCH/work`` (else
    ``~/sx-scratch/work``) and says so once. An explicit ``WORK_ROOT`` is honoured
    as given.
    """
    env = os.environ.get(WORK_ROOT_ENV)
    if env:
        root = Path(env).expanduser().resolve()
    else:
        root = (project_root() / "work").resolve()
        if not _writable(root):
            default, root = root, _fallback_root()
            if root not in _FALLBACK_NOTED:
                _FALLBACK_NOTED.add(root)
                _log.warning(
                    "%s is unset and the default %s is not writable; using %s "
                    "(set %s to choose the location)",
                    WORK_ROOT_ENV,
                    default,
                    root,
                    WORK_ROOT_ENV,
                )
    root.mkdir(parents=True, exist_ok=True)
    return root


def _writable(path: Path) -> bool:
    """Whether ``path`` can be written — or, when absent, created — by this user."""
    for p in (path, *path.parents):
        if p.exists():
            return p.is_dir() and os.access(p, os.W_OK | os.X_OK)
    return False


def _fallback_root() -> Path:
    # Same per-user scratch convention as the spectre lane: $SX_SCRATCH else ~/sx-scratch.
    scratch = os.environ.get(SCRATCH_ENV)
    return (
        Path(scratch) if scratch else Path.home() / "sx-scratch"
    ).expanduser().resolve() / "work"


def shared_root(root: Path | None = None) -> Path:
    """``WORK_ROOT/shared`` — cross-project assets (LUTs, caches, the user lib)."""
    d = (root or work_root()) / "shared"
    d.mkdir(parents=True, exist_ok=True)
    return d


def scaffold_project(project_dir: Path, *, dry_run: bool = False) -> list[str]:
    """Create any missing v2 structure inside ``project_dir`` (idempotent).

    Returns the project-relative paths that were (or with ``dry_run`` would be)
    created. Existing files/dirs are never touched, so calling this on a live v1
    project is safe by construction — that IS the migration primitive.
    """
    created: list[str] = []
    for rel in PROJECT_DIRS_V2:
        d = project_dir / rel
        if not d.is_dir():
            created.append(rel + "/")
            if not dry_run:
                d.mkdir(parents=True, exist_ok=True)
    for rel, content in ((_DECISIONS_REL, ""), (_PROJECT_MD_REL, _PROJECT_MD_STUB)):
        f = project_dir / rel
        if not f.exists():
            created.append(rel)
            if not dry_run:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(content)
    return created


def scaffold_shared(root: Path | None = None, *, dry_run: bool = False) -> list[str]:
    """Create any missing ``WORK_ROOT``-level shared dirs (idempotent)."""
    base = root or work_root()
    created: list[str] = []
    for rel in SHARED_DIRS:
        d = base / rel
        if not d.is_dir():
            created.append(rel + "/")
            if not dry_run:
                d.mkdir(parents=True, exist_ok=True)
    return created
