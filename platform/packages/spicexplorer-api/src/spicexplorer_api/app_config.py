"""Backend configuration — resolves repo-relative paths from app_config.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spicexplorer_core import project_root
from spicexplorer_core.workspace import work_root as _kernel_work_root

# Workspace root (holds examples/, app_config.json). Resolved via the kernel's
# marker/env anchor — replaces the old BACKEND_DIR/UI_DIR/REPO_ROOT parent-walk.
REPO_ROOT = project_root()


def work_root() -> Path:
    """The single root for all MUTABLE state (run checkpoints, scratch sims).

    ``WORK_ROOT`` env (the Docker backend sets it to ``/work``, a host bind mount)
    else ``<repo>/work`` (gitignored). Read-only assets — examples, presets, the
    schematic SVG — stay ``REPO_ROOT``-relative via ``resolve()``; only durable run
    artifacts go under here. This de-CWDs the autosave so checkpoints survive a
    ``docker rm`` instead of dying in the ephemeral image layer (report.md P1).

    Canonical resolution lives in the storage kernel
    (``spicexplorer_core.workspace``) so orchestration agents and the API agree
    on ONE root; this is a thin delegate kept for the existing import surface.
    """
    return _kernel_work_root()


def auto_save_root() -> Path:
    """Base dir for legacy/unscoped optimizer autosave checkpoints (under ``work_root``)."""
    d = work_root() / "auto_save"
    d.mkdir(parents=True, exist_ok=True)
    return d


def projects_root() -> Path:
    """Base dir for encapsulated projects — ``WORK_ROOT/projects/<slug>-<id8>/`` (report.md P3)."""
    d = work_root() / "projects"
    d.mkdir(parents=True, exist_ok=True)
    return d


def runs_root() -> Path:
    """Fallback dir for runs NOT owned by a project (legacy yaml_path / example runs)."""
    d = work_root() / "runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def trash_root() -> Path:
    """Soft-delete bin under WORK_ROOT (recoverable). Projects/runs are MOVED here on
    delete (never rm'd), so a delete is always restorable (report.md P4)."""
    d = work_root() / ".trash"
    d.mkdir(parents=True, exist_ok=True)
    return d


_app_config: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _app_config
    if _app_config is None:
        cfg_path = REPO_ROOT / "app_config.json"
        with cfg_path.open() as f:
            raw = json.load(f)
        _app_config = raw
    return _app_config


def get_app_config() -> dict[str, Any]:
    return _load()


def resolve(repo_relative: str) -> Path:
    return REPO_ROOT / repo_relative


def default_yaml_path() -> Path:
    return resolve(get_app_config()["default_yaml"])


def preset_checkpoint_paths() -> dict[str, Path]:
    return {k: resolve(v) for k, v in get_app_config()["preset_checkpoints"].items()}


def schematic_svg_path() -> Path:
    return resolve(get_app_config()["schematic_svg"])
