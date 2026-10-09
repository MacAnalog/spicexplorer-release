"""Environment probe — detects the SPICE simulator and the open PDKs' ngspice models.

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

The open PDKs the ngspice lane runs are one table, :data:`OPEN_PDKS`, keyed by the design
registry's PDK id (``registry/pdks.json`` rows with ``open: true``): the install directories
under ``$PDK_ROOT`` and the corner lib the committed decks ``.lib``. ``probe_pdk`` /
``probe_env`` take ``tech=`` (default :data:`DEFAULT_TECH`, IHP SG13G2, whose result is
unchanged key for key), and :func:`probe_pdk_models` answers ``{pdk_id: bool}`` for every row.
Only open PDKs belong in the table; a commercial kit runs on the Spectre lane.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The model library the cascode/5t/folded testbenches pull in via ``.lib cornerMOSlv.lib``.
# Its presence on disk is our proxy for "the IHP sg13g2 device models are installed".
_PDK_MODEL_LIB = "cornerMOSlv.lib"
_PDK_TECH = "ihp-sg13g2"

# Env vars that, by convention, point at a PDK install root.
_PDK_ENV_VARS = ("PDK_ROOT", "PDK", "IHP_PDK_ROOT")

# Env vars that, by convention, indicate a Cadence install / a configured virtuoso-bridge
# remote. Live Spectre + licensed-kit runs happen only on a Cadence-equipped host, so
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
    extra_roots: list[tuple[str, Path]] | None = None,
    env_vars: tuple[str, ...] = _PDK_ENV_VARS,
) -> list[tuple[str, Path]]:
    """Ordered (source-label, path) pairs to search for the PDK model libs.

    ``extra_roots`` lets a caller (e.g. the API, from ``app_config.pdk_root``)
    inject additional roots without core depending on that caller.
    """
    candidates: list[tuple[str, Path]] = []
    for var in env_vars:
        val = os.environ.get(var)
        if val:
            candidates.append((var, Path(val).expanduser()))
    if extra_roots:
        candidates.extend(extra_roots)
    return candidates


# The fallback search's reach: an ngspice ``libs.tech`` subtree at the root or at most two
# directory levels below it (``<root>/<src>/<tech>/libs.tech/ngspice/…`` for an unpacked source
# tree). Anchoring on ``libs.tech/ngspice`` keeps a stray copy of the lib (a design's scratch, a
# test fixture) and the PDK's own Xyce copy from passing for an ngspice install.
_PDK_LIB_FALLBACK_GLOBS = (
    f"libs.tech/ngspice/**/{_PDK_MODEL_LIB}",
    f"*/libs.tech/ngspice/**/{_PDK_MODEL_LIB}",
    f"*/*/libs.tech/ngspice/**/{_PDK_MODEL_LIB}",
)


@dataclass(frozen=True)
class OpenPdk:
    """One open PDK the ngspice lane runs: where its ngspice corner lib sits under a PDK root.

    ``install_dirs`` are the directory names under ``$PDK_ROOT`` in search order and
    ``corner_lib`` is the lib the decks ``.lib``, relative to ``<install dir>/libs.tech/ngspice/``.
    ``subpaths`` / ``fallback_globs`` are the probe's search below each candidate root, ``env_vars``
    the env vars whose values are candidate roots. ``vendor`` and ``unset_hint`` only shape the
    human ``pdk_detail`` line.
    """

    pdk_id: str
    vendor: str
    install_dirs: tuple[str, ...]
    corner_lib: str
    subpaths: tuple[str, ...]
    fallback_globs: tuple[str, ...] = ()
    env_vars: tuple[str, ...] = ("PDK_ROOT",)
    unset_hint: str = "PDK_ROOT"

    @property
    def model_lib(self) -> str:
        """The corner lib's file name (what an unresolved ``.lib`` line names)."""
        return self.corner_lib.rsplit("/", 1)[-1]


def _installed_lib_subpaths(install_dirs: tuple[str, ...], corner_lib: str) -> tuple[str, ...]:
    return tuple(f"{d}/libs.tech/ngspice/{corner_lib}" for d in install_dirs)


_SKY130_DIRS = ("sky130A", "sky130B", "sky130")
_SKY130_LIB = "sky130.lib.spice"
_GF180_DIRS = ("gf180mcuD", "gf180mcuC", "gf180mcuB", "gf180mcuA", "gf180mcu")
_GF180_LIB = "sm141064.ngspice"

#: The PDK ``probe_pdk`` / ``probe_env`` answer for when no ``tech`` is given.
DEFAULT_TECH = _PDK_TECH

#: The open PDKs the ngspice lane runs, by registry PDK id (same layout analog-db's native
#: runner resolves). IHP keeps its historical search (flat lib, nested source trees, the bounded
#: fallback, three env vars) so its result is byte-identical; the others are looked up at
#: ``$PDK_ROOT/<install dir>/libs.tech/ngspice/<corner lib>`` only.
OPEN_PDKS: dict[str, OpenPdk] = {
    _PDK_TECH: OpenPdk(
        pdk_id=_PDK_TECH,
        vendor="IHP",
        install_dirs=(_PDK_TECH,),
        corner_lib=f"models/{_PDK_MODEL_LIB}",
        subpaths=_PDK_LIB_SUBPATHS,
        fallback_globs=_PDK_LIB_FALLBACK_GLOBS,
        env_vars=_PDK_ENV_VARS,
        unset_hint="PDK_ROOT/PDK",
    ),
    "sky130": OpenPdk(
        pdk_id="sky130",
        vendor="SkyWater",
        install_dirs=_SKY130_DIRS,
        corner_lib=_SKY130_LIB,
        subpaths=_installed_lib_subpaths(_SKY130_DIRS, _SKY130_LIB),
    ),
    "gf180mcu": OpenPdk(
        pdk_id="gf180mcu",
        vendor="GlobalFoundries",
        install_dirs=_GF180_DIRS,
        corner_lib=_GF180_LIB,
        subpaths=_installed_lib_subpaths(_GF180_DIRS, _GF180_LIB),
    ),
}


def open_pdk(tech: str) -> OpenPdk:
    """The :data:`OPEN_PDKS` row for ``tech``; an unknown id is a ``ValueError`` naming the known ones."""
    row = OPEN_PDKS.get(tech)
    if row is None:
        known = ", ".join(sorted(OPEN_PDKS))
        raise ValueError(f"unknown open PDK {tech!r}; known: {known}")
    return row


def _find_model_lib(root: Path, pdk: OpenPdk | None = None) -> Path | None:
    """Return the PDK's ngspice corner lib under ``root`` if resolvable, else None.

    Checks the row's known sub-paths first (fast), then (IHP) falls back to a search bounded to
    ngspice ``libs.tech`` subtrees near the root, so an unusual layout still resolves without
    scanning the whole tree — and without promoting any file that merely shares the name.
    """
    row = pdk or OPEN_PDKS[DEFAULT_TECH]
    if not root.exists():
        return None
    for sub in row.subpaths:
        hit = root / sub
        if hit.exists():
            return hit
    for pattern in row.fallback_globs:
        for hit in sorted(root.glob(pattern)):
            return hit
    return None


def probe_pdk(
    extra_roots: list[tuple[str, Path]] | None = None, *, tech: str = DEFAULT_TECH
) -> dict[str, Any]:
    """Detect one open PDK's ngspice models (default IHP sg13g2) without running a simulation.

    Returns ``pdk_root`` (resolved install dir or None), ``pdk_ok``, and a human
    ``pdk_detail`` string suitable for the Settings/Diagnostics verdict line. ``tech`` is an
    :data:`OPEN_PDKS` id; an unknown one is a ``ValueError``.
    """
    row = open_pdk(tech)
    candidates = _candidate_pdk_roots(extra_roots, row.env_vars)

    for source, root in candidates:
        lib = _find_model_lib(root, row)
        if lib is not None:
            return {
                "pdk_root": str(root),
                "pdk_ok": True,
                "pdk_detail": (f"{row.vendor} {row.pdk_id} models found via {source} ({lib})."),
            }

    if not candidates:
        detail = (
            f"{row.vendor} {row.pdk_id} models not found "
            f"({row.unset_hint} unset; .lib {row.model_lib} unresolved). "
            "Live simulation unavailable — replay enabled."
        )
    else:
        searched = ", ".join(f"{s}={p}" for s, p in candidates)
        detail = (
            f"{row.vendor} {row.pdk_id} PDK root set but {row.model_lib} not found under "
            f"[{searched}]. Live simulation unavailable — replay enabled."
        )
    return {"pdk_root": None, "pdk_ok": False, "pdk_detail": detail}


def probe_pdk_models(extra_roots: list[tuple[str, Path]] | None = None) -> dict[str, bool]:
    """Whether each :data:`OPEN_PDKS` row's ngspice models are installed, ``{pdk_id: bool}``.

    Booleans only, sorted by id: the root or lib path that answered is never returned, so the
    result is safe to hand to a cloud model. Each value equals ``probe_pdk(tech=id)["pdk_ok"]``.
    """
    return {
        pdk_id: bool(probe_pdk(extra_roots, tech=pdk_id)["pdk_ok"]) for pdk_id in sorted(OPEN_PDKS)
    }


def probe_env(
    extra_roots: list[tuple[str, Path]] | None = None, *, tech: str = DEFAULT_TECH
) -> dict[str, Any]:
    """Full environment verdict: simulator + PDK + whether live runs are possible.

    Intentionally scoped to the open-source ngspice + PDK lane — the `/api/env` contract
    the UI degrades on. The Cadence/Spectre backend has its own probes
    (`probe_spectre` / `probe_cadence` / `probe_cadence_env`) so this dict's shape (and the
    API surface built on it) is unchanged by the Cadence-lane probes below. ``tech`` picks the
    :data:`OPEN_PDKS` row the flat ``pdk_*`` keys answer for (default IHP, unchanged).
    """
    ng = probe_ngspice()
    pdk = probe_pdk(extra_roots, tech=tech)
    return {
        **ng,
        **pdk,
        "tech": tech,
        # Live SPICE optimization needs BOTH the binary and the device models.
        "live_runs_enabled": bool(ng["ngspice_ok"] and pdk["pdk_ok"]),
    }


# ---------------------------------------------------------------------------
# Cadence / Spectre probes (P6 — "Cadence absent" CI skip-gate)
# ---------------------------------------------------------------------------
# These mirror `probe_pdk`: a cheap, no-simulation detection so open-PDK
# CI can skip the live Spectre tests cleanly and never reach for the SSH host. Live
# Spectre + licensed-kit runs happen ONLY on a Cadence-equipped host; everywhere else these
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
            "configured — live Spectre unavailable; skip the live-Spectre gate."
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
