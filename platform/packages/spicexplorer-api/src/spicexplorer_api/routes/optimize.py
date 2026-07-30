"""Optimization run management: start, stop, and SSE stream."""
from __future__ import annotations

import asyncio
import functools
import json
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from spicexplorer_api.app_config import preset_checkpoint_paths
from spicexplorer_api.services import optimizer_runner as runner
from spicexplorer_api.services import project_service
from spicexplorer_api.services.env_probe import probe_env

router = APIRouter()


class StartRequest(BaseModel):
    yaml_path: str | None = None
    # The owning project (report.md P3). When set, the run is resolved + isolated
    # under WORK_ROOT/projects/<id>/runs/; yaml_path stays as a back-compat fallback.
    project_id: str | None = None
    label: str | None = None
    replay: bool = False
    checkpoint_id: str | None = None
    budget: int = 200
    # Ephemeral live-run overrides (applied in-memory to the loaded project; the
    # YAML on disk is never rewritten). Ignored for replay runs.
    algorithm: str | None = None
    seed: int | None = None
    # PVT corner to optimize against (must match a corner in the project's `pvt:`
    # block). None keeps the YAML's active_corner.
    active_corner: str | None = None
    # Checkpointing (live runs only). autosave_every writes a cumulative
    # checkpoint every N trials; resume_checkpoint_id continues a prior run from
    # a saved checkpoint (load_checkpoint + optimize(keep_history=True)).
    autosave_every: int | None = None
    resume_checkpoint_id: str | None = None
    # Keep per-trial raw waveforms in the run dir so /api/waveview/open_run can view
    # them afterwards. Default False (trial raws are deleted each evaluate) — enabling
    # grows the run dir with budget × testbenches raw files.
    keep_raw: bool = False


# --- Response models (see src/types/README.md) -------------------------------
class RunStartResponse(BaseModel):
    run_id: str
    replay: bool
    resumed: bool        # `resume_path is not None` — always a real bool
    n_iters: int | None  # replayed-checkpoint row count; null for live/resume runs


class OkResponse(BaseModel):
    ok: bool


class AlgorithmsResponse(BaseModel):
    recommended: list[str]  # curated known-good presets (Run popover default set)
    families: list[str]     # configurable classes — accept optimizer_kwargs in YAML
    registry: list[str]     # every pre-configured Nevergrad preset name


# Curated subset for the Run popover's primary group. Backend-owned so the UI
# never hardcodes algorithm names; filtered against the installed Nevergrad at
# request time so a version bump can't advertise a name that won't construct.
_RECOMMENDED_ALGORITHMS = [
    "NGOpt", "LhsDE", "TwoPointsDE", "DE", "CMA", "PSO", "OnePlusOne",
    "TBPSA", "RandomSearch", "LHSSearch", "LogBFGSCMAPlus", "SamplingSearch",
]


@functools.lru_cache(maxsize=1)
def _algorithm_lists() -> tuple[list[str], list[str], list[str]]:
    import nevergrad as ng  # deferred: heavy import, already loaded once a run starts

    registry = sorted(ng.optimizers.registry.keys())
    families = sorted(
        n for n in dir(ng.families)
        if not n.startswith("_") and isinstance(getattr(ng.families, n), type)
    )
    known = set(registry) | set(families)
    recommended = [n for n in _RECOMMENDED_ALGORITHMS if n in known]
    return recommended, families, registry


@router.get("/optimize/algorithms", response_model=AlgorithmsResponse)
def list_algorithms():
    """Selectable optimizer algorithms, derived from the installed Nevergrad.

    ``recommended`` drives the Run popover's primary group; ``families`` are the
    configurable classes (their kwargs live in the project YAML); ``registry``
    is the full preset list for power users.
    """
    recommended, families, registry = _algorithm_lists()
    return {"recommended": recommended, "families": families, "registry": registry}


@router.post("/optimize/start", response_model=RunStartResponse)
async def start_run(body: StartRequest, request: Request):
    loop = asyncio.get_event_loop()

    # A replay needs a checkpoint to replay — reject the no-id case up front instead of scheduling
    # nothing and leaving the SSE stream heartbeating "running" forever (BUG-B36).
    if body.replay and not body.checkpoint_id:
        raise HTTPException(400, "replay requires a checkpoint_id")

    # Refuse to start a run for a project whose delete is in flight — otherwise this run could
    # re-create the project tree the delete is about to move to trash (start-after-stop TOCTOU,
    # the B4 residual).
    if runner.is_project_deleting(body.project_id):
        raise HTTPException(409, "project is being deleted; cannot start a run")

    # Single resolver: project_id → its project.yaml; else yaml_path; else default.
    try:
        yaml_path = str(project_service.resolve_yaml(body.project_id, body.yaml_path))
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        # malformed project_id (path separators / '..') → 400, not an opaque 500 (BUG-B37)
        raise HTTPException(400, str(e))

    # Live and resume runs need real SPICE: refuse cleanly (409) when the
    # environment can't run it, instead of failing deep in the engine. Replay
    # needs no PDK, so it is exempt. (The client also gates this; this is the
    # server-side enforcement so direct/programmatic callers get a clear error.)
    if not body.replay:
        env = probe_env()
        if not env.get("live_runs_enabled", False):
            raise HTTPException(409, env.get("pdk_detail") or "Live runs disabled: ngspice/PDK unavailable.")

    checkpoint_path: Path | None = None
    replay_len: int | None = None
    if body.replay and body.checkpoint_id:
        presets = preset_checkpoint_paths()
        checkpoint_path = presets.get(body.checkpoint_id)
        if checkpoint_path is None or not checkpoint_path.exists():
            raise HTTPException(404, f"Checkpoint '{body.checkpoint_id}' not found")
        # Report the row count so the UI's progress denominator is the checkpoint
        # length, not the unrelated live-run budget (default 200).
        try:
            from spicexplorer_api.services.checkpoint_reader import read_checkpoint
            replay_len = read_checkpoint(checkpoint_path).get("n_iters")
        except Exception:
            replay_len = None

    # Resume: resolve the checkpoint to continue a live run from (presets or autosaves).
    resume_path: str | None = None
    if body.resume_checkpoint_id and not body.replay:
        from spicexplorer_api.routes.checkpoint import _resolve_checkpoint_path

        resolved = _resolve_checkpoint_path(body.resume_checkpoint_id)
        if resolved is None:
            raise HTTPException(404, f"Resume checkpoint '{body.resume_checkpoint_id}' not found")
        resume_path = str(resolved)

    run_id = runner.start_run(
        project_path=yaml_path if not body.replay else None,
        project_id=body.project_id,
        label=body.label,
        replay=body.replay,
        checkpoint_id=body.checkpoint_id,
        checkpoint_path=checkpoint_path,
        budget=body.budget,
        algorithm=body.algorithm,
        seed=body.seed,
        active_corner=body.active_corner,
        autosave_every=body.autosave_every,
        resume_path=resume_path,
        keep_raw=body.keep_raw,
        loop=loop,
    )
    return {"run_id": run_id, "replay": body.replay, "resumed": resume_path is not None, "n_iters": replay_len}


@router.post("/optimize/stop/{run_id}", response_model=OkResponse)
def stop_run(run_id: str):
    runner.stop_run(run_id)
    return {"ok": True}


# SSE stream tuning. Poll for client disconnect this often so a dropped viewer promptly
# stops its background run (checked at the next trial boundary) instead of burning the
# whole budget unwatched; emit a keep-alive heartbeat only every _HEARTBEAT_SECONDS so the
# tighter poll cadence doesn't spam the client.
_DISCONNECT_POLL_SECONDS = 2.0
_HEARTBEAT_SECONDS = 30.0


@router.get("/optimize/stream/{run_id}")
async def stream_run(run_id: str, request: Request):
    state = runner.get_run(run_id)
    if state is None:
        raise HTTPException(404, f"Run '{run_id}' not found")

    async def event_generator():
        # A dropped client must not leave the optimizer running its full budget with nobody
        # listening while its bounded queue churns (cross_repo_audit: the SSE stream never
        # checked for disconnect). Two disconnect signals both funnel into `stop_run`:
        #  - the `is_disconnected()` poll below (wins under ASGI spec >= 2.4), and
        #  - task cancellation by the ASGI server's own disconnect listener (uvicorn's HTTP
        #    protocol advertises spec 2.3, so Starlette cancels this generator on disconnect).
        # `completed` distinguishes a genuine end-of-run (the None sentinel) from either, so a
        # finished run is never needlessly re-stopped.
        completed = False
        last_sent = time.monotonic()
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(state.queue.get(), timeout=_DISCONNECT_POLL_SECONDS)
                except asyncio.TimeoutError:
                    if time.monotonic() - last_sent >= _HEARTBEAT_SECONDS:
                        last_sent = time.monotonic()
                        yield "data: {\"heartbeat\": true}\n\n"
                    continue

                last_sent = time.monotonic()
                if event is None:
                    completed = True
                    yield 'data: {"done": true}\n\n'
                    break
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            if not completed:
                runner.stop_run(run_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
