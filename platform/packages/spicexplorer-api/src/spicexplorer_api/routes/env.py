"""Environment route — reports simulator + PDK availability for graceful degradation.

The Studio UI calls ``GET /api/env`` on load to decide whether live optimization is
possible. On a machine without the IHP ``ihp-sg13g2`` PDK (e.g. this personal Mac),
``live_runs_enabled`` is False and the frontend steers the user to Replay.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from spicexplorer_api.services.env_probe import probe_env

router = APIRouter()


class EnvResponse(BaseModel):
    """Simulator + PDK availability — drives the UI's live-vs-replay degradation.

    Matches ``probe_env()`` exactly, so declaring it as ``response_model`` types the
    OpenAPI schema (→ codegen) without changing what the route returns.
    """
    ngspice_path: str | None
    ngspice_ok: bool
    pdk_root: str | None
    pdk_ok: bool
    pdk_detail: str
    tech: str
    live_runs_enabled: bool


@router.get("/env", response_model=EnvResponse)
def get_env():
    """Cheap, no-simulation probe of ngspice + the IHP PDK."""
    return probe_env()
