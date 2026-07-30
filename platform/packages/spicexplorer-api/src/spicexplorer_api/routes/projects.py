"""Project registry + scaffold / copy-example / per-project runs (report.md P3).

A project IS a directory under WORK_ROOT/projects (the registry is the filesystem,
no DB). "New project" scaffolds an example-structured dir; "load example" copies a
demo into a fresh registered project. All FS bookkeeping lives in project_service.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from spicexplorer.core.domains import Project_Setup
from spicexplorer_core import workspace as ws

# `ProjectSummary` (+ its sub-model tree) is defined once in routes/project.py and
# reused here so get_project's `summary` block shares ONE OpenAPI schema (a second
# definition would make FastAPI suffix it `ProjectSummary1` and desync codegen).
from spicexplorer_api.routes.project import ProjectSummary, _summarise
from spicexplorer_api.services import index_db, optimizer_runner, project_service

router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str
    # The wizard's generated YAML (optional). When omitted, the default example seeds it.
    yaml_content: Optional[str] = None


class FromExampleRequest(BaseModel):
    example_key: str
    name: Optional[str] = None


class RenameRequest(BaseModel):
    name: str


class ForkRequest(BaseModel):
    name: Optional[str] = None


class RenameRunRequest(BaseModel):
    label: str


# --- Response models (see src/types/README.md) -------------------------------
class IdResponse(BaseModel):
    """`{id: str}` — shared by create / from-example / fork / restore."""
    id: str


class ProjectMeta(BaseModel):
    id: str
    name: str
    updated: str | None      # always present (updated|created), can be null
    run_count: int
    best_score: float | None  # always present, null until a run has a numeric score
    source: str


class ListProjectsResponse(BaseModel):
    projects: list[ProjectMeta]


class ExampleMeta(BaseModel):
    key: str
    name: str
    description: str | None = None
    yaml_path: str


class ListExamplesResponse(BaseModel):
    examples: list[ExampleMeta]


class ProjectDetailResponse(BaseModel):
    id: str
    yaml_path: str
    summary: ProjectSummary
    # Free-form manifest.json passthrough — keep `dict[str, Any]` so no manifest key
    # (id/slug/name/created/updated/source/schema_version, source being nested) is dropped.
    manifest: dict[str, Any]


class ProjectRun(BaseModel):
    """One run's `run.json` (canonical writer = optimizer_runner._write_run_json).

    Read off disk via json.loads, so EVERY field except `run_id` is defaulted: a
    partial/older run.json (or a minimal test fixture) must validate rather than 500
    under response_model. The canonical writer always sets all keys, so production
    responses are unchanged (defaults only fill genuinely-absent keys)."""
    run_id: str
    project_id: str | None = None
    label: str | None = None
    kind: str = ""
    algorithm: str | None = None
    seed: int | None = None
    budget: int | None = None
    active_corner: str | None = None
    status: str = ""
    best_score: float | None = None
    started: str | None = None
    ended: str | None = None
    resume_from: str | None = None


class ProjectRunsResponse(BaseModel):
    runs: list[ProjectRun]


class RenameProjectResponse(BaseModel):
    id: str
    manifest: dict[str, Any]


class DeleteProjectResponse(BaseModel):
    ok: bool
    trash_id: str
    stopped_runs: int  # count of in-flight runs signalled to stop (NOT a list)


class TrashItem(BaseModel):
    trash_id: str
    kind: str            # "project" | "run"
    project_id: str
    run_id: str | None = None  # present only for kind=="run" (else emitted as null)
    name: str
    deleted: str


class ListTrashResponse(BaseModel):
    trash: list[TrashItem]


class RenameRunResponse(BaseModel):
    run: ProjectRun


class DeleteRunResponse(BaseModel):
    ok: bool
    trash_id: str


@router.get("/projects", response_model=ListProjectsResponse)
def list_projects():
    # Indexed read (P2): same shape/order as the FS lister; self-heals against
    # out-of-band creates/deletes and falls back to the FS scan on any DB error.
    return {"projects": index_db.list_projects()}


@router.get("/examples", response_model=ListExamplesResponse)
def list_examples():
    """In-repo demo projects that can be loaded (copied) as a new project."""
    return {"examples": project_service.list_examples()}


@router.post("/projects", response_model=IdResponse)
def create_project(body: CreateProjectRequest):
    if not body.name.strip():
        raise HTTPException(400, "project name is required")
    try:
        pid = project_service.create_project(body.name, body.yaml_content)
    except Exception as e:
        raise HTTPException(400, f"create failed: {e}")
    return {"id": pid}


@router.post("/projects/from-example", response_model=IdResponse)
def from_example(body: FromExampleRequest):
    try:
        pid = project_service.copy_example(body.example_key, body.name)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(400, f"copy failed: {e}")
    return {"id": pid}


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str):
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    yp = project_service.project_yaml(project_id)
    try:
        project = Project_Setup.from_yaml(yp)
    except Exception as e:
        raise HTTPException(422, str(e))
    return {
        "id": project_id,
        "yaml_path": str(yp),
        "summary": _summarise(project),
        "manifest": project_service.read_manifest(project_id),
    }


@router.get("/projects/{project_id}/runs", response_model=ProjectRunsResponse)
def project_runs(
    project_id: str,
    kind: str = Query("", description="Filter to one run kind (optimize/simulate/xschem/…); blank = all"),
):
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    runs = index_db.list_runs(project_id)
    if kind:
        runs = [r for r in runs if r.get("kind") == kind]
    return {"runs": runs}


# ---------- agent context surface (plan P4/P5 §3.6, D-10) ----------


class DecisionRequest(BaseModel):
    summary: str
    kind: Optional[str] = None
    by: Optional[str] = None          # "agent" | "human" | an agent id
    refs: Optional[dict[str, Any]] = None


@router.get("/projects/{project_id}/state")
def project_state(project_id: str):
    """The derived, rebuildable per-project rollup (`state.json`): spec×corner compliance
    matrix, best-run pointers (+ the election rule), cell inventory. One read instead of
    globbing a dozen files (plan §3.6). Freshly DERIVED on each call (never stale) — and
    side-effect-free: a GET does not write, so it works on a read-only project dir."""
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    return ws.build_state(project_service.project_dir(project_id))


@router.get("/projects/{project_id}/context")
def project_context(project_id: str):
    """The generated `PROJECT.md` (from `state.json` + the decision log) as markdown —
    the agent's "where is this design at" surface (D-10). Rendered side-effect-free
    (`write=False`) so a GET never mutates the project dir or 500s on a read-only one."""
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    pdir = project_service.project_dir(project_id)
    return {"markdown": ws.render_project_md(pdir, write=False), "decisions": ws.read_decisions(pdir)}


@router.post("/projects/{project_id}/decisions")
def append_project_decision(project_id: str, body: DecisionRequest):
    """Append ONE decision event to the append-only log (D-10: agents write events, never
    documents). `PROJECT.md` regenerates from it on the next `/context` read."""
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    event = {k: v for k, v in body.model_dump().items() if v is not None}
    ev = ws.append_decision(project_service.project_dir(project_id), event)
    return {"ok": True, "event": ev}


# ---------- lifecycle: rename / fork / soft-delete + trash/restore (report.md P4) ----------


@router.patch("/projects/{project_id}", response_model=RenameProjectResponse)
def rename_project(project_id: str, body: RenameRequest):
    try:
        man = project_service.rename_project(project_id, body.name)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"id": project_id, "manifest": man}


@router.post("/projects/{project_id}/fork", response_model=IdResponse)
def fork_project(project_id: str, body: ForkRequest):
    try:
        new_id = project_service.fork_project(project_id, body.name)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(400, f"fork failed: {e}")
    return {"id": new_id}


@router.delete("/projects/{project_id}", response_model=DeleteProjectResponse)
def delete_project(project_id: str):
    # Tombstone the project for the whole stop→move window so a run that tries to START in that
    # gap is refused (begin/end around it) — closes the start-after-stop TOCTOU residual of BUG-B4.
    optimizer_runner.begin_project_delete(project_id)
    try:
        # Quiesce any in-flight live run for this project FIRST, else its writer thread
        # re-creates the moved-away run tree and defeats the soft-delete (corruption + leak).
        # If a worker is still mid-trial after the join, do NOT move the dir out from under it
        # (BUG-B4) — 409 and let the caller retry once the trial finishes.
        stopped, still_alive = optimizer_runner.stop_runs_for(project_id=project_id)
        if still_alive:
            raise HTTPException(
                409,
                f"{len(still_alive)} run(s) for '{project_id}' are still stopping; retry shortly.",
            )
        try:
            trash_id = project_service.soft_delete_project(project_id)
        except FileNotFoundError as e:
            raise HTTPException(404, str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"delete failed: {e}")
    finally:
        optimizer_runner.end_project_delete(project_id)
    return {"ok": True, "trash_id": trash_id, "stopped_runs": stopped}


@router.get("/trash", response_model=ListTrashResponse)
def list_trash():
    return {"trash": project_service.list_trash()}


class TrashPurgedResponse(BaseModel):
    ok: bool
    trash_id: str


@router.delete("/trash/{trash_id}", response_model=TrashPurgedResponse)
def purge_trash(trash_id: str):
    """Permanently delete a trashed project/run — the "delete forever" action.
    Irreversible; restore is the safe sibling."""
    try:
        project_service.purge_trash(trash_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "trash_id": trash_id}


@router.post("/trash/{trash_id}/restore", response_model=IdResponse)
def restore_trash(trash_id: str):
    try:
        pid = project_service.restore_project(trash_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))
    except RuntimeError as e:  # corrupt trash metadata — a data error, not a conflict
        raise HTTPException(500, str(e))
    return {"id": pid}


@router.patch("/projects/{project_id}/runs/{run_id}", response_model=RenameRunResponse)
def rename_run(project_id: str, run_id: str, body: RenameRunRequest):
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    try:
        run = project_service.rename_run(project_id, run_id, body.label)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"run": run}


@router.delete("/projects/{project_id}/runs/{run_id}", response_model=DeleteRunResponse)
def delete_run(project_id: str, run_id: str):
    if not project_service.project_exists(project_id):
        raise HTTPException(404, f"project '{project_id}' not found")
    # Stop the run if it's live (same writer-resurrection hazard as project delete). If it's
    # still mid-trial after the join, 409 rather than move its dir out from under it (BUG-B4).
    _, still_alive = optimizer_runner.stop_runs_for(project_id=project_id, run_id=run_id)
    if still_alive:
        raise HTTPException(409, "run is still stopping; retry shortly.")
    try:
        trash_id = project_service.delete_run(project_id, run_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    return {"ok": True, "trash_id": trash_id}
