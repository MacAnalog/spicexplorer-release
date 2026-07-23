"""The single DB-root indirection.

Every consumer resolves the database through `db_root()` — one env-overridable seam — so the
location is decided in exactly one place. The database (``_shared/`` + ``circuits/`` +
``catalog.json``) ships **beside this package** in the ``spicexplorer-analog-db`` repo, whether
that repo is used standalone or mounted as the ``examples/analog-db/`` submodule of the platform.

Resolution order:
1. ``$SPICEXPLORER_ANALOG_DB`` if set (explicit override).
2. Package-relative repo root (``<repo>/circuits`` exists) — the normal case, layout-agnostic
   (standalone clone, submodule mount, or editable install from either).
3. Legacy in-tree fallback: ``<platform>/examples[/analog-db]`` via ``project_root()`` — kept for
   the pre-extraction transition; ignored if the workspace anchor is absent.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "SPICEXPLORER_ANALOG_DB"


def _package_relative_root() -> Path | None:
    # paths.py -> spicexplorer_analog_db -> src -> <repo root>
    root = Path(__file__).resolve().parents[2]
    return root if (root / "circuits").is_dir() else None


def _legacy_in_tree_root() -> Path | None:
    try:
        from spicexplorer_core import project_root  # optional; only present with the platform
    except Exception:
        return None
    try:
        examples = project_root() / "examples"
    except Exception:
        return None
    submodule = examples / "analog-db"
    if (submodule / "circuits").is_dir():
        return submodule
    if (examples / "circuits").is_dir():
        return examples
    return None


def db_root() -> Path:
    """The database root (contains ``_shared/`` and ``circuits/``)."""
    override = os.environ.get(ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    pkg = _package_relative_root()
    if pkg is not None:
        return pkg
    legacy = _legacy_in_tree_root()
    if legacy is not None:
        return legacy
    return Path(__file__).resolve().parents[2]


def circuits_root() -> Path:
    return db_root() / "circuits"


def shared_root() -> Path:
    return db_root() / "_shared"


def schema_root() -> Path:
    return shared_root() / "schema"


def classes_root() -> Path:
    return shared_root() / "classes"


def shared_templates_root() -> Path:
    return shared_root() / "testbench-templates"


def catalog_path() -> Path:
    return db_root() / "catalog.json"


def db_present() -> bool:
    """True iff the database is actually checked out (mirrors the PDK-absence contract)."""
    return circuits_root().is_dir()
