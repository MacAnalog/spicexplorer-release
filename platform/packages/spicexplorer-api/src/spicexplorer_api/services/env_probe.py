"""Environment probe — thin API adapter over the kernel detector.

The detection logic now lives in ``spicexplorer_core.env`` (shared by every
surface). This module adds only the API-specific bit the kernel must not know
about: the optional ``app_config.pdk_root`` override, injected as ``extra_roots``.
Re-exports the same names the routes import so call sites are unchanged.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from spicexplorer_core import env as _env

# Re-exported so routes/tests referencing the detector's constants keep working.
_PDK_TECH = _env._PDK_TECH
_PDK_MODEL_LIB = _env._PDK_MODEL_LIB
_PDK_LIB_SUBPATHS = _env._PDK_LIB_SUBPATHS
_PDK_ENV_VARS = _env._PDK_ENV_VARS


def _extra_roots() -> list[tuple[str, Path]] | None:
    """The optional app_config.pdk_root override (best-effort; never breaks the probe)."""
    try:
        from spicexplorer_api.app_config import get_app_config

        cfg_root = get_app_config().get("pdk_root")
        if cfg_root:
            return [("app_config.pdk_root", Path(str(cfg_root)).expanduser())]
    except Exception:  # noqa: BLE001 — config is optional
        return None
    return None


def probe_ngspice() -> dict[str, Any]:
    return _env.probe_ngspice()


def probe_pdk() -> dict[str, Any]:
    return _env.probe_pdk(_extra_roots())


def probe_env() -> dict[str, Any]:
    return _env.probe_env(_extra_roots())


def _candidate_pdk_roots() -> list[tuple[str, Path]]:
    return _env._candidate_pdk_roots(_extra_roots())
