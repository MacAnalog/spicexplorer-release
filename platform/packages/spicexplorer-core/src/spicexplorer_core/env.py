"""Environment probe — detects the SPICE simulator and the IHP PDK.

This is a *cheap, no-simulation* check used to drive UI degradation (live sims vs
replay) and to annotate sanity runs with the PDK verdict. It reliably distinguishes
"simulator missing" from "PDK models missing".

Promoted from the FastAPI backend (``ui/backend/services/env_probe.py``) into the
shared kernel so every surface — the API, a future MCP server, CI — uses one
detector. **Detection lives here; provisioning (installing ngspice+PDK) is the
container's job** — the two are deliberately separate.

The backend's optional ``app_config.pdk_root`` override is no longer imported here
(core must not depend on the API). Callers pass any extra roots explicitly via the
``extra_roots`` argument, e.g.
``probe_env(extra_roots=[("app_config.pdk_root", Path(cfg_root))])``.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

# The model library the cascode/5t/folded testbenches pull in via ``.lib cornerMOSlv.lib``.
# Its presence on disk is our proxy for "the IHP sg13g2 device models are installed".
_PDK_MODEL_LIB = "cornerMOSlv.lib"
_PDK_TECH = "ihp-sg13g2"

# Env vars that, by convention, point at a PDK install root.
_PDK_ENV_VARS = ("PDK_ROOT", "PDK", "IHP_PDK_ROOT")

# Env vars that, by convention, indicate a Cadence install / a configured virtuoso-bridge
# remote. Live Spectre + FOUNDRY-65 runs happen only on a Cadence-equipped host, so
# these are near-always absent on the open-PDK lanes — which is exactly the
# point: they drive the "Cadence absent" CI skip-gate.
_CADENCE_ENV_VARS = ("VB_CADENCE_CSHRC", "CDS_INST_DIR", "CDSHOME", "CDS_ROOT")
# A configured bridge remote host implies Spectre is reachable (over SSH), even with no
# local Cadence install. `VB_SPECTRE_BIN` optionally pins the remote/local spectre binary.
_VB_REMOTE_HOST_VARS = ("VB_REMOTE_HOST",)

# Sub-paths under a candidate root where IHP ships its ngspice model libs.
_PDK_LIB_SUBPATHS = (
    _PDK_MODEL_LIB,
    f"{_PDK_TECH}/libs.tech/ngspice/{_PDK_MODEL_LIB}",
    f"{_PDK_TECH}/libs.tech/ngspice/models/{_PDK_MODEL_LIB}",  # actual IHP sg13g2 layout (PDK_ROOT parent)
    f"libs.tech/ngspice/{_PDK_MODEL_LIB}",
    f"libs.tech/ngspice/models/{_PDK_MODEL_LIB}",
)


def probe_ngspice() -> dict[str, Any]:
    """Locate the ngspice binary. Cheap: just a PATH lookup."""
    path = shutil.which("ngspice")
    return {"ngspice_path": path, "ngspice_ok": path is not None}


def _candidate_pdk_roots(
    extra_roots: list[tuple[str, Path]] | None = None
) -> list[tuple[str, Path]]:
    """Ordered (source-label, path) pairs to search for the PDK model libs.

    ``extra_roots`` lets a caller (e.g. the API, from ``app_config.pdk_root``)
    inject additional roots without core depending on that caller.
    """
    candidates: list[tuple[str, Path]] = []
    for var in _PDK_ENV_VARS:
        val = os.environ.get(var)
        if val:
            candidates.append((var, Path(val).expanduser()))
    if extra_roots:
        candidates.extend(extra_roots)
    return candidates


def _find_model_lib(root: Path) -> Path | None:
    """Return the cornerMOSlv.lib under ``root`` if resolvable, else None.

    Checks a handful of known sub-paths first (fast), then falls back to a single
    bounded ``rglob`` so an unusual layout still resolves without scanning forever.
    """
    if not root.exists():
        return None
    for sub in _PDK_LIB_SUBPATHS:
        hit = root / sub
        if hit.exists():
            return hit
    # Bounded fallback: first match only.
    for hit in root.rglob(_PDK_MODEL_LIB):
        return hit
    return None


def probe_pdk(extra_roots: list[tuple[str, Path]] | None = None) -> dict[str, Any]:
    """Detect the IHP sg13g2 PDK without running a simulation.

    Returns ``pdk_root`` (resolved install dir or None), ``pdk_ok``, and a human
    ``pdk_detail`` string suitable for the Settings/Diagnostics verdict line.
    """
    candidates = _candidate_pdk_roots(extra_roots)

    for source, root in candidates:
        lib = _find_model_lib(root)
        if lib is not None:
            return {
                "pdk_root": str(root),
                "pdk_ok": True,
                "pdk_detail": (
                    f"IHP {_PDK_TECH} models found via {source} "
                    f"({lib})."
                ),
            }

    if not candidates:
        detail = (
            f"IHP {_PDK_TECH} models not found "
            f"(PDK_ROOT/PDK unset; .lib {_PDK_MODEL_LIB} unresolved). "
            "Live simulation unavailable — replay enabled."
        )
    else:
        searched = ", ".join(f"{s}={p}" for s, p in candidates)
        detail = (
            f"IHP {_PDK_TECH} PDK root set but {_PDK_MODEL_LIB} not found under "
            f"[{searched}]. Live simulation unavailable — replay enabled."
        )
    return {"pdk_root": None, "pdk_ok": False, "pdk_detail": detail}


def probe_env(extra_roots: list[tuple[str, Path]] | None = None) -> dict[str, Any]:
    """Full environment verdict: simulator + PDK + whether live runs are possible.

    Intentionally scoped to the open-source ngspice + PDK lane — the `/api/env` contract
    the UI degrades on. The Cadence/Spectre backend has its own probes
    (`probe_spectre` / `probe_cadence` / `probe_cadence_env`) so this dict's shape (and the
    API surface built on it) is unchanged by the Cadence-lane probes below.
    """
    ng = probe_ngspice()
    pdk = probe_pdk(extra_roots)
    return {
        **ng,
        **pdk,
        "tech": _PDK_TECH,
        # Live SPICE optimization needs BOTH the binary and the device models.
        "live_runs_enabled": bool(ng["ngspice_ok"] and pdk["pdk_ok"]),
    }


# ---------------------------------------------------------------------------
# Cadence / Spectre probes (P6 — "Cadence absent" CI skip-gate)
# ---------------------------------------------------------------------------
# These mirror `probe_pdk`: a cheap, no-simulation detection so open-PDK
# CI can skip the live Spectre tests cleanly and never reach for the SSH host. Live
# Spectre + FOUNDRY-65 runs happen ONLY on a Cadence-equipped host; everywhere else these
# report False. Kept separate from `probe_env` so the open-PDK `/api/env` contract is
# untouched.


def probe_spectre() -> dict[str, Any]:
    """Detect a usable `spectre` binary (local PATH or `VB_SPECTRE_BIN`).

    Returns `spectre_bin` (resolved path or None), `spectre_ok`, and `spectre_remote_host`
    (the configured bridge remote, if any). Cheap: a PATH lookup + env reads, no exec.
    """
    which = shutil.which("spectre")
    vb_bin = os.environ.get("VB_SPECTRE_BIN", "").strip()
    vb_bin_ok = bool(vb_bin) and Path(vb_bin).expanduser().exists()
    spectre_bin = which or (vb_bin if vb_bin_ok else None)
    remote_host = ""
    for var in _VB_REMOTE_HOST_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            remote_host = val
            break
    return {
        "spectre_bin": spectre_bin,
        "spectre_ok": spectre_bin is not None,
        "spectre_remote_host": remote_host or None,
    }


def probe_cadence() -> dict[str, Any]:
    """Detect a Cadence environment (a cshrc/install env var, or a bridge remote host).

    `cadence_ok` is True when either a Cadence install env var is set (a local Cadence
    tree) or a virtuoso-bridge remote host is configured (Spectre reachable over SSH).
    Returns `cadence_ok`, a human `cadence_detail`, and the `cadence_source` var name.
    """
    for var in _CADENCE_ENV_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            return {
                "cadence_ok": True,
                "cadence_detail": f"Cadence environment detected via {var}={val}.",
                "cadence_source": var,
            }
    for var in _VB_REMOTE_HOST_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            return {
                "cadence_ok": True,
                "cadence_detail": (
                    f"virtuoso-bridge remote host configured ({var}={val}); "
                    "Spectre reachable over SSH."
                ),
                "cadence_source": var,
            }
    return {
        "cadence_ok": False,
        "cadence_detail": (
            "No Cadence environment (CDS/cshrc install vars) or virtuoso-bridge remote "
            "configured — live Spectre / FOUNDRY-65 unavailable; skip the live-Spectre gate."
        ),
        "cadence_source": None,
    }


def probe_cadence_env() -> dict[str, Any]:
    """Full Cadence-lane verdict: Spectre binary + Cadence env + `cadence_live_enabled`.

    `cadence_live_enabled` is True only when BOTH a spectre backend is reachable and a
    Cadence environment is present — the analog of `live_runs_enabled` for the closed lane.
    This is the single boolean a CI skip-gate keys off.
    """
    spectre = probe_spectre()
    cadence = probe_cadence()
    return {
        **spectre,
        **cadence,
        "cadence_live_enabled": bool(spectre["spectre_ok"] and cadence["cadence_ok"]),
    }
