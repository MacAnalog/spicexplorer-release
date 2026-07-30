"""SpiceXplorer UI — FastAPI backend."""
import logging
import os
from contextlib import asynccontextmanager

from spicexplorer_core import project_root

# Configure root logger so uvicorn/fastapi messages appear consistently.
# basicconfig is idempotent so it's safe to call at import time in both
# the reloader parent and the worker child.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

_LOG_LEVEL_NAME = os.environ.get("LOG_LEVEL", "INFO").upper()
_LOG_LEVEL = getattr(logging, _LOG_LEVEL_NAME, logging.INFO)
_REPO_ROOT = project_root()

from fastapi import (
    FastAPI,  # noqa: E402 (imports follow the top-of-file logging.basicConfig by design)
)
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.routing import APIRoute  # noqa: E402

from spicexplorer_api.routes import (  # noqa: E402
    checkpoint,
    config,
    env,
    library,
    netlist,
    optimize,
    project,
    projects,
    sanity,
    schematic,
    score,
    sensitivity,
    simulate,
    waveview,
    xschem,
)


def _operation_id(route: APIRoute) -> str:
    """Clean, stable OpenAPI operationIds for a generator-friendly spec.

    Replaces FastAPI's auto-mangled default (``get_config_api_config_get``) with
    ``<tag>_<function name>`` (``config_get_config``). The tag prefix guarantees
    uniqueness across routers; the handler name is unique within a router. Feeds the
    UI codegen's `operations` block (todo_openapi.md #4)."""
    tag = route.tags[0] if route.tags else "api"
    return f"{tag}_{route.name}"


# (router, tag) — one tag per router groups the OpenAPI by domain.
_ROUTERS = [
    (config.router, "config"),
    (project.router, "project"),
    (score.router, "score"),
    (optimize.router, "optimize"),
    (checkpoint.router, "checkpoint"),
    (schematic.router, "schematic"),
    (sanity.router, "sanity"),
    (netlist.router, "netlist"),
    (xschem.router, "xschem"),
    (env.router, "env"),
    (sensitivity.router, "sensitivity"),
    (simulate.router, "simulate"),
    (projects.router, "projects"),
    (library.router, "library"),
    (waveview.router, "waveview"),
]

_OPENAPI_TAGS = [
    {"name": "config", "description": "App config + preset checkpoints for the frontend."},
    {"name": "project", "description": "Load / validate / generate / parse a project YAML."},
    {"name": "projects", "description": "Project registry, per-run lifecycle, soft-delete trash."},
    {"name": "score", "description": "Sigmoid vs. linear score shaping for target specs."},
    {"name": "optimize", "description": "Start / stop a run and stream live progress (SSE)."},
    {"name": "checkpoint", "description": "List / load checkpoints + envelope / scatter analyses."},
    {"name": "sanity", "description": "Pre-flight testbench + single-trial sanity check."},
    {"name": "simulate", "description": "Evaluate one chosen design point (manual single sim)."},
    {"name": "sensitivity", "description": "Per-parameter sensitivity sweep."},
    {"name": "netlist", "description": "Netlist param inspection + the wizard spec library."},
    {"name": "schematic", "description": "Project schematic SVG."},
    {"name": "xschem", "description": "Serve xschem .sch/.sym files for the in-browser viewer."},
    {"name": "env", "description": "Simulator + PDK availability probe (live-vs-replay degradation)."},
    {"name": "library", "description": "Reference Library: the analog-db catalog, datasheets, class registry + templates."},
    {"name": "waveview", "description": "Universal result viewer: open ngspice .raw / Spectre PSF artifacts, waveforms, Tier-1 measurements, log viewer + SSE tail."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs only in the uvicorn worker process, not the WatchFiles reloader parent,
    # so exactly one log file is created per server start.
    from spicexplorer_core.logging import setup_loggers
    setup_loggers(
        out_logname="SpiceXplorer",
        parent_folder=_REPO_ROOT,
        console_level=_LOG_LEVEL,
    )
    # Flip any run left "running" by a crashed backend to "error" so the run list is
    # honest on restart (report.md §6 reconciler).
    try:
        from spicexplorer_api.services import project_service
        fixed = project_service.reconcile_stale_runs()
        if fixed:
            logging.getLogger(__name__).info("reconciled %d stale 'running' run(s) -> error", fixed)
    except Exception:
        pass
    # Rebuild the derived WORK_ROOT index from the (canonical) filesystem AFTER the
    # reconciler, so out-of-band edits made while the API was down are re-absorbed
    # (plan_project_filesystem P2). Best-effort: a failed rebuild only costs the
    # indexed fast path — reads fall back to FS scans.
    try:
        from spicexplorer_api.services import index_db
        counts = index_db.rebuild()
        logging.getLogger(__name__).info(
            "work index rebuilt: %(projects)d project(s), %(runs)d run(s)", counts)
    except Exception:
        logging.getLogger(__name__).warning("work index rebuild failed — FS fallback", exc_info=True)
    yield


app = FastAPI(
    title="SpiceXplorer API",
    version="1.0.0",
    description=(
        "REST adapter over the SpiceXplorer optimizer + SPICE kernel. The OpenAPI here "
        "is the single contract the Next.js UI generates its TypeScript types from "
        "(openapi.json → openapi-typescript)."
    ),
    openapi_tags=_OPENAPI_TAGS,
    generate_unique_id_function=_operation_id,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for _router, _tag in _ROUTERS:
    app.include_router(_router, prefix="/api", tags=[_tag])


@app.get("/health", tags=["env"], summary="Liveness probe")
def health():
    return {"status": "ok"}
