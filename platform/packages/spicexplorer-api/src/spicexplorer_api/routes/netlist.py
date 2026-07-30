"""Netlist inspection + spec-library routes used by the Setup wizard."""
from __future__ import annotations

from typing import Any

import yaml
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from spicexplorer_api.app_config import REPO_ROOT
from spicexplorer_api.services.netlist_parser import parse_meas_candidates, parse_params

router = APIRouter()

_SPEC_LIBRARY_PATH = REPO_ROOT / "examples" / "spec_library.yaml"


# --- Response models (see src/types/README.md) -------------------------------
class NetlistParam(BaseModel):
    name: str
    default_val: str


class MeasCandidate(BaseModel):
    name: str
    sim_type: str


class NetlistParseResponse(BaseModel):
    ok: bool
    filename: str | None  # Starlette UploadFile.filename is Optional; always present
    params: list[NetlistParam]
    meas_candidates: list[MeasCandidate]


class SpecLibraryResponse(BaseModel):
    # `specs` rows are read verbatim from examples/spec_library.yaml and are partial /
    # heterogeneous (only `name` is conventional) — keep them as free dicts so no key is
    # dropped. The UI keeps its richer hand-written SpecLibraryEntry for these.
    specs: list[dict[str, Any]]


@router.post("/netlist/parse", response_model=NetlistParseResponse)
async def parse_netlist(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode netlist: {e}")
    params = parse_params(text)
    # Also surface `.meas` result names so the Target-Specs step can auto-discover
    # candidate specs from the same upload (the wizard picks which to enable).
    meas_candidates = parse_meas_candidates(text)
    return {
        "ok": True,
        "filename": file.filename,
        "params": params,
        "meas_candidates": meas_candidates,
    }


@router.get("/spec-library", response_model=SpecLibraryResponse)
def spec_library():
    """Serve the shipped analog-spec templates (examples/spec_library.yaml) for the
    wizard's one-click "Spec library" adds. Returns `{specs: [...]}` (empty if the
    file is missing/unreadable, so the wizard degrades gracefully)."""
    try:
        if not _SPEC_LIBRARY_PATH.exists():
            return {"specs": []}
        data = yaml.safe_load(_SPEC_LIBRARY_PATH.read_text()) or {}
        specs = data.get("specs", []) if isinstance(data, dict) else []
        return {"specs": specs if isinstance(specs, list) else []}
    except yaml.YAMLError:
        return {"specs": []}
