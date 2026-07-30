"""Serve xschem .sch/.sym files for the in-browser viewer, and generate a .sch from a netlist."""

from __future__ import annotations

import hashlib
import os
import shutil
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel
from spicexplorer_netlist2xschem import (
    XschemFromNetlistRequest,
    XschemSchematicResult,
    build_sch,
    from_file,
    from_string,
    render,
    result_from,
)

from spicexplorer_api.app_config import REPO_ROOT, work_root
from spicexplorer_api.services import project_service

router = APIRouter()


# --- Response models (see src/types/README.md) -------------------------------
class XschemFile(BaseModel):
    path: str
    name: str


class XschemFileResponse(BaseModel):
    path: str
    content: str


class XschemResolveResponse(BaseModel):
    path: str
    content: str
    resolved_from: str


class XschemListResponse(BaseModel):
    dir: str
    files: list[XschemFile]


class XschemProjectResponse(BaseModel):
    xschem_dir: str | None  # null when no candidate xschem/ dir resolves
    files: list[XschemFile]


@lru_cache(maxsize=1)
def _xschem_share_dirs() -> list[Path]:
    """Locate xschem's bundled symbol libraries.

    xschem's default XSCHEM_LIBRARY_PATH contains both `xschem_library/` and
    `xschem_library/devices/` — symbol refs may be written either as
    `devices/foo.sym` (resolved from xschem_library/) or as bare `foo.sym`
    (resolved from xschem_library/devices/). Add both.
    """
    candidates: list[Path] = []
    binary = shutil.which("xschem")
    if binary:
        prefix = Path(binary).resolve().parent.parent
        share = prefix / "share" / "xschem" / "xschem_library"
        candidates.append(share)
        candidates.append(share / "devices")
    # XSCHEM_LIBRARY_PATH from xschemrc; also honor explicit env override.
    env = os.environ.get("XSCHEM_LIBRARY_PATH", "")
    for part in env.split(":"):
        if part:
            candidates.append(Path(part))
    # Dedup while preserving order.
    seen: set[Path] = set()
    out: list[Path] = []
    for p in candidates:
        if p.exists() and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _discover_pdk_xschem_dir() -> Path | None:
    """Locate the PDK's xschem symbol library, using the SAME root discovery as the
    env probe so the symbol search path can never be a strict subset of the sim PDK
    path (the cause of "symbols render but sims work" — device symbols turning into
    red "?" placeholders while ``pdk_ok: true``).

    For every candidate PDK root (``PDK_ROOT`` / ``PDK`` / ``IHP_PDK_ROOT`` /
    ``app_config.pdk_root``) it matches both layouts:
      - ``<root>/libs.tech/xschem``         (root already points at the tech dir)
      - ``<root>/<tech>/libs.tech/xschem``  (root is the parent of named tech dirs)
    where ``tech`` comes from ``$PDK`` and the env-probe default tech name. The old
    implementation required BOTH ``PDK_ROOT`` and ``PDK`` and only tried the second
    layout, so a ``PDK_ROOT``-only (or ``IHP_PDK_ROOT`` / app-config) deployment lost
    the PDK from the resolver path while the probe still reported the PDK present.
    """
    roots: list[Path] = []
    techs: list[str] = []
    try:
        from spicexplorer_api.services.env_probe import _PDK_TECH, _candidate_pdk_roots

        roots.extend(p for _, p in _candidate_pdk_roots())
        techs.append(_PDK_TECH)
    except Exception:  # noqa: BLE001 — env_probe is optional; fall back to raw env below.
        pass
    pdk_root = os.environ.get("PDK_ROOT")
    if pdk_root:
        roots.append(Path(pdk_root).expanduser())
    pdk = os.environ.get("PDK")  # conventional tech name, e.g. "ihp-sg13g2"
    if pdk:
        techs.insert(0, pdk)

    seen: set[Path] = set()
    for root in roots:
        if root in seen:
            continue
        seen.add(root)
        direct = root / "libs.tech" / "xschem"
        if direct.is_dir():
            return direct
        for tech in techs:
            cand = root / tech / "libs.tech" / "xschem"
            if cand.is_dir():
                return cand
    return None


_pdk_xschem_dir_cached: Path | None = None


def _pdk_xschem_dir() -> Path | None:
    """Locate the PDK xschem dir, memoizing only a SUCCESSFUL result.

    Unlike a plain ``lru_cache``, a ``None`` (PDK not yet reachable at first call) is
    never frozen — so a late-exported ``PDK`` env var or a PDK mounted after startup is
    picked up on the next call without a process restart.
    """
    global _pdk_xschem_dir_cached
    if _pdk_xschem_dir_cached is not None and _pdk_xschem_dir_cached.is_dir():
        return _pdk_xschem_dir_cached
    found = _discover_pdk_xschem_dir()
    if found is not None:
        _pdk_xschem_dir_cached = found
    return found


def _search_roots(base_dir: Path | None) -> list[Path]:
    """Ordered list of dirs to resolve a relative symbol/schematic reference against."""
    roots: list[Path] = []
    if base_dir is not None:
        roots.append(base_dir)
    pdk = _pdk_xschem_dir()
    if pdk is not None:
        roots.append(pdk)
    roots.extend(_xschem_share_dirs())
    return roots


def _allowed_roots() -> list[Path]:
    """Whitelist for absolute-path access. Anything outside these is rejected."""
    # Include WORK_ROOT: encapsulated projects (and their copied `xschem/` subtrees) live under
    # work_root() (= /work under Docker), which is OUTSIDE REPO_ROOT — without it, every
    # encapsulated project's schematic 403s under the documented Docker artifact (BUG-B14).
    roots: list[Path] = [REPO_ROOT, work_root()]
    pdk = _pdk_xschem_dir()
    if pdk is not None:
        roots.append(pdk)
    roots.extend(_xschem_share_dirs())
    return [p.resolve() for p in roots]


def _validate_under_allowed(path: Path) -> Path:
    resolved = path.resolve()
    for root in _allowed_roots():
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue
    raise HTTPException(403, f"Path outside allowed roots: {path}")


@router.get("/xschem/file", response_model=XschemFileResponse)
def get_file(path: str = Query(..., description="Absolute path to a .sch or .sym file")):
    """Return the raw text of an xschem file, gated by the allowed-roots whitelist."""
    candidate = Path(path)
    if not candidate.is_absolute():
        raise HTTPException(400, "Path must be absolute; use /xschem/resolve for relative refs")
    resolved = _validate_under_allowed(candidate)
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(404, f"Not found: {resolved}")
    if resolved.suffix not in (".sch", ".sym"):
        raise HTTPException(400, "Only .sch and .sym files are served")
    return {
        "path": str(resolved),
        "content": resolved.read_text(),
    }


@router.get("/xschem/resolve", response_model=XschemResolveResponse)
def resolve_ref(
    ref: str = Query(..., description="Reference like 'devices/foo.sym' or 'sg13g2_pr/bar.sym'"),
    base: str | None = Query(
        None, description="Absolute path of the parent .sch/.sym (for sibling refs)"
    ),
):
    """Resolve a symbol/schematic reference against the xschem search path.

    Order matches xschem's lookup: same-dir-as-base, then PDK lib, then xschem share libs.
    """
    base_dir = None
    if base:
        base_path = Path(base)
        if base_path.is_absolute():
            try:
                _validate_under_allowed(base_path)
                base_dir = base_path.parent
            except HTTPException:
                pass
    for root in _search_roots(base_dir):
        candidate = (root / ref).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            # `ref` tried to escape the search root (e.g. ../../etc/passwd).
            continue
        if candidate.exists() and candidate.is_file():
            return {
                "path": str(candidate),
                "content": candidate.read_text(),
                "resolved_from": str(root),
            }
    raise HTTPException(404, f"Could not resolve {ref!r}")


@router.get("/xschem/list", response_model=XschemListResponse)
def list_dir(
    dir: str = Query(..., description="Absolute path of a directory under the allowed roots"),
):
    """List .sch files in a directory."""
    d = Path(dir)
    if not d.is_absolute():
        raise HTTPException(400, "Path must be absolute")
    resolved = _validate_under_allowed(d)
    if not resolved.is_dir():
        raise HTTPException(404, f"Not a directory: {resolved}")
    files = sorted(p for p in resolved.glob("*.sch") if p.is_file())
    return {
        "dir": str(resolved),
        "files": [{"path": str(p), "name": p.name} for p in files],
    }


@router.get("/xschem/project", response_model=XschemProjectResponse)
def project_schematics(
    yaml_path: str = Query(..., description="Absolute path of the project YAML"),
):
    """Find the conventional xschem dir for a project YAML and list its .sch files.

    Looks for `{ws_root}/xschem/` first (sibling-of-sizing convention), then for any
    `xschem/` dir near the yaml.
    """
    yaml_p = Path(yaml_path)
    if not yaml_p.is_absolute():
        raise HTTPException(400, "yaml_path must be absolute")
    _validate_under_allowed(yaml_p)
    if not yaml_p.exists():
        raise HTTPException(404, f"YAML not found: {yaml_p}")

    candidates: list[Path] = []
    # Walk up from the yaml until we find a sibling `xschem/` dir.
    cur = yaml_p.parent
    for _ in range(6):
        sibling = cur / "xschem"
        if sibling.is_dir():
            candidates.append(sibling)
            break
        if cur.parent == cur:
            break
        cur = cur.parent

    if not candidates:
        return {"xschem_dir": None, "files": []}

    xschem_dir = candidates[0]
    try:
        _validate_under_allowed(xschem_dir)
    except HTTPException:
        return {"xschem_dir": None, "files": []}

    # Recursive: seeded demo projects keep vendored schematic TREES (e.g. a
    # circuit's reference/ti-ldo/…) under xschem/ so sibling .sym refs resolve;
    # the display name is the xschem/-relative path so subdirs stay tellable.
    files = sorted(p for p in xschem_dir.rglob("*.sch") if p.is_file())
    return {
        "xschem_dir": str(xschem_dir),
        "files": [{"path": str(p), "name": p.relative_to(xschem_dir).as_posix()} for p in files],
    }


def _slug(name: str) -> str:
    keep = "".join(c if (c.isalnum() or c in "_.-") else "_" for c in name)
    return keep.strip("_") or "schematic"


@router.post("/xschem/from-netlist", response_model=XschemSchematicResult)
def from_netlist(req: XschemFromNetlistRequest = Body(...)) -> XschemSchematicResult:
    """Generate an xschem .sch from a SPICE netlist (and optionally render it to SVG/PNG).

    The returned ``sch_content`` is viewable immediately in the in-browser viewer; the .sch is also
    persisted under ``work_root()`` so ``GET /xschem/file`` can serve it and its resolved symbols.
    Image export is additive: it degrades to ``.sch``-only when xschem (or the PNG rasterizer) is absent.

    Generation is ALSO recorded as a first-class ``kind: xschem`` run (plan §3.3 P3.1c):
    the source netlist is content-addressed into the run's provenance, the outputs are
    copied into the run's own ``artifacts/`` (self-contained, fetchable by id), and the
    run lands in the index — so "what schematics were generated, from what" is queryable.
    The recording degrades gracefully: if the run dir can't be minted, generation proceeds
    exactly as before.
    """
    if not req.netlist_path and not req.netlist_text:
        raise HTTPException(400, "Provide netlist_path or netlist_text")
    if req.netlist_path and req.netlist_text:
        raise HTTPException(400, "Provide only one of netlist_path / netlist_text")

    # Resolve the source up front — a client error (400/404) must NOT mint a run.
    resolved: Path | None = None
    input_files = None
    input_values = None
    if req.netlist_path:
        p = Path(req.netlist_path)
        if not p.is_absolute():
            raise HTTPException(400, "netlist_path must be absolute")
        resolved = _validate_under_allowed(p)
        if not resolved.is_file():
            raise HTTPException(404, f"Netlist not found: {resolved}")
        input_files = {"netlist": resolved}
    else:
        input_values = {"netlist_text": req.netlist_text}

    try:
        _run_id, rdir = project_service.begin_run(
            "xschem", project_id=None,
            input_files=input_files, input_values=input_values,
            coordinates={"pdk": req.pdk, "into": req.into, "name": req.name},
            retention="full",  # a generated schematic is the deliverable, never GC'd
        )
    except (OSError, RuntimeError):
        # mint_run_dir raises OSError (ENOSPC/permission) OR RuntimeError (id-collision
        # exhaustion) — both mean "can't mint a run dir"; degrade to schematic-only.
        rdir = None

    try:
        try:
            if resolved is not None:
                circuit = from_file(resolved, name=req.name, into=req.into)
                source_key = str(resolved)
            else:
                assert req.netlist_text is not None
                circuit = from_string(req.netlist_text, name=req.name or "schematic", into=req.into)
                source_key = req.netlist_text
        except Exception as exc:  # noqa: BLE001 — surface any parse/descent failure as a 422
            raise HTTPException(422, f"Failed to parse netlist: {exc}") from exc

        doc = build_sch(circuit, pdk=req.pdk, title=circuit.name)

        # Persist under work_root() (inside the allowed roots) so the existing file/resolve routes serve it.
        digest = hashlib.sha1(f"{source_key}|{req.pdk}|{req.into}".encode()).hexdigest()[:8]
        slug = _slug(circuit.name)
        out_dir = work_root() / "xschem" / "generated" / f"{slug}-{digest}"
        out_dir.mkdir(parents=True, exist_ok=True)
        sch_path = out_dir / f"{slug}.sch"
        sch_path.write_text(doc.text)

        render_result = None
        fmt = req.render
        if fmt != "none":
            lib_path = os.pathsep.join(str(p) for p in _search_roots(None))
            render_result = render(sch_path, fmt=fmt, outdir=out_dir, library_path=lib_path)

        if rdir is not None:
            try:  # self-contained run: copy the outputs into the run's artifacts/
                shutil.copytree(out_dir, rdir / "artifacts", dirs_exist_ok=True)
            except OSError:
                pass
            project_service.finalize_run(None, rdir, status="done")
        return result_from(doc, sch_path=str(sch_path), render=render_result)
    except Exception as exc:
        # Record the failed generation, then re-raise UNCHANGED (status codes preserved).
        if rdir is not None:
            detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
            project_service.finalize_run(None, rdir, status="error", error=str(detail))
        raise
