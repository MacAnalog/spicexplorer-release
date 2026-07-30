"""Project loading and YAML validation routes."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from spicexplorer.core.domains import Project_Setup

from spicexplorer_api.services.yaml_generator import generate_yaml, project_dict_to_form

router = APIRouter()


class LoadRequest(BaseModel):
    yaml_path: Optional[str] = None
    yaml_content: Optional[str] = None  # apply edited/uploaded YAML that isn't on disk
    project_id: Optional[str] = None  # load a registered project (report.md P3)


class ValidateRequest(BaseModel):
    yaml_content: str


class GenerateRequest(BaseModel):
    form: Dict[str, Any]
    save_path: Optional[str] = None  # absolute or workspace-relative path; if set, write to disk


class ParseToFormRequest(BaseModel):
    yaml_path: Optional[str] = None
    yaml_content: Optional[str] = None


# --- Response models ---------------------------------------------------------
# These mirror the producer dicts EXACTLY (see src/types/README.md): every key the
# producer emits is declared so response_model neither drops nor injects a key. Keys
# that are always present but can be null use `X | None` with NO default (per the
# convention, e.g. EnvResponse.ngspice_path). The `ProjectSummary` tree below is the
# `_summarise()` shape and is imported by routes/projects.py (get_project reuses it),
# so it is defined ONCE here to avoid a duplicate OpenAPI schema name.

class DutParam(BaseModel):
    name: str
    min_val: float | None
    max_val: float | None
    val: float | None
    init: float | None
    is_integer: bool
    log_scale: bool
    freeze: bool


class TbParam(BaseModel):
    name: str
    val: str | None
    description: str | None


class Testbench(BaseModel):
    name: str
    netlist: str
    enable: bool
    description: str | None
    params: list[TbParam]


class TargetSpec(BaseModel):
    name: str
    testbench: str
    goal: str
    target: float
    tolerance: float | None
    range: float | None
    weight: float
    error_type: str
    reward_type: str
    enable: bool
    description: str | None


class SupplyOverride(BaseModel):
    node: str
    value: float


class ModelInclude(BaseModel):
    lib_file: str
    section: str


class PVTCornerDef(BaseModel):
    name: str
    enabled: bool
    temp: float
    supplies: list[SupplyOverride]
    model_includes: list[ModelInclude]
    params: dict[str, float]


class PVTConfig(BaseModel):
    active_corner: str
    model_lib_root: str | None
    corners: list[PVTCornerDef]
    # Multi-corner (Phase 2): "single" runs the active corner; "multi" runs every
    # enabled corner per trial and aggregates the per-corner scores.
    mode: str
    score_aggregation: str


class TechSpec(BaseModel):
    name: str
    constraints: dict[str, float]


class OptimizerSummary(BaseModel):
    type: str
    name: str
    budget: int
    random_seed: int | None


class ProjectSummary(BaseModel):
    name: str
    description: str
    simulator: str
    ws_root: str
    netlist: str
    schematic: str | None
    tech: TechSpec
    pvt: PVTConfig | None
    dut_params: list[DutParam]
    testbenches: list[Testbench]
    optimizer: OptimizerSummary
    target_specs: list[TargetSpec]


class LoadProjectResponse(BaseModel):
    ok: bool
    summary: ProjectSummary
    yaml_path: str


class ValidateResponse(BaseModel):
    ok: bool
    errors: list[str]


class GenerateProjectResponse(BaseModel):
    ok: bool
    yaml: str
    errors: list[str]
    saved_path: str | None


# Wizard-form tree — the `project_dict_to_form()` shape (inverse of /project/generate).
# Every leaf is a string/bool (None-coerced to "" by the producer), except a corner's
# per-`.param` overrides which pass through verbatim (`dict[str, Any]`). Distinct from
# the ProjectSummary tree above: here budget/seed/target/etc. are STRINGS, not numbers.

class ConstraintRow(BaseModel):
    key: str
    value: str


class WizardTech(BaseModel):
    name: str
    constraints: list[ConstraintRow]


class WizardProjectInfo(BaseModel):
    name: str
    description: str
    simulator: str
    save_sim: bool
    parallel_sim: bool
    ws_root: str
    netlist: str
    outdir: str
    schematic: str


class WizardExtraSupply(BaseModel):
    node: str
    value: str


class WizardModelInclude(BaseModel):
    lib_file: str
    section: str


class WizardPVTCorner(BaseModel):
    name: str
    temp: str
    supply_node: str
    supply_value: str
    extra_supplies: list[WizardExtraSupply]
    enabled: bool
    includes: list[WizardModelInclude]
    params: dict[str, Any]


class WizardPVTConfig(BaseModel):
    active_corner: str
    corners: list[WizardPVTCorner]
    model_lib_root: str
    mode: str
    score_aggregation: str


class WizardDutParam(BaseModel):
    name: str
    min_val: str
    max_val: str
    init: str
    val: str
    is_integer: bool
    log_scale: bool
    freeze: bool
    source: str


class WizardTbParam(BaseModel):
    name: str
    val: str
    description: str
    source: str


class WizardTestbench(BaseModel):
    name: str
    netlist: str
    enable: bool
    description: str
    params: list[WizardTbParam]


class WizardTargetSpec(BaseModel):
    name: str
    testbench: str
    sim_type: str
    goal: str
    target: str
    range: str
    tolerance: str
    weight: str
    log_scale: bool
    error_type: str
    reward_type: str
    enable: bool
    description: str


class OptimizerKwargRow(BaseModel):
    key: str
    value: str


class WizardOptimizer(BaseModel):
    type: str
    name: str
    budget: str
    random_seed: str
    lin_min: str
    lin_max: str
    log_min: str
    log_max: str
    optimizer_kwargs: list[OptimizerKwargRow]


class WizardForm(BaseModel):
    project: WizardProjectInfo
    tech: WizardTech
    pvt: WizardPVTConfig
    dut_params: list[WizardDutParam]
    testbenches: list[WizardTestbench]
    target_specs: list[WizardTargetSpec]
    optimizer: WizardOptimizer


class ParseProjectResponse(BaseModel):
    ok: bool
    form: WizardForm


def _summarise(project: Project_Setup) -> dict[str, Any]:
    specs = []
    for s in project.optimizer_config.target_specs.targets:
        specs.append({
            "name": s.name,
            "testbench": s.testbench,
            "goal": s.goal.value,
            "target": float(s.target),
            "tolerance": float(s.tolerance) if s.tolerance else None,
            "range": float(s.range) if s.range else None,
            "weight": float(s.weight) if s.weight is not None else 1.0,
            "error_type": s.error_type.value if hasattr(s.error_type, "value") else str(s.error_type),
            "reward_type": s.reward_type.value if hasattr(s.reward_type, "value") else str(s.reward_type),
            "enable": s.enable,
            "description": s.description,
        })

    dut_params = []
    for p in project.dut_params:
        dut_params.append({
            "name": p.name,
            "min_val": float(p.min_val) if p.min_val is not None else None,
            "max_val": float(p.max_val) if p.max_val is not None else None,
            # Resolved operating-point value (if the YAML set val/init), so the
            # Schematic inspector seeds its slider from the same nominal the
            # sensitivity backend uses. Non-numeric (unresolved) -> None.
            "val": float(p.val) if isinstance(p.val, (int, float)) else None,
            "init": float(p.init) if isinstance(p.init, (int, float)) else None,
            "is_integer": p.is_integer,
            "log_scale": p.log_scale,
            "freeze": p.freeze,
        })

    testbenches = []
    for tb in project.testbenches:
        testbenches.append({
            "name": tb.name,
            "netlist": str(tb.netlist),
            "enable": tb.enable,
            "description": tb.description,
            "params": [
                {"name": p.name, "val": str(p.val) if p.val is not None else None, "description": p.description}
                for p in tb.params
            ],
        })

    # PVT corner system (Phase 1) — the simulator-driving config. `None` when the
    # project has no `pvt:` block (legacy / netlist-hardcoded corner).
    pvt_config: dict[str, Any] | None = None
    if project.pvt is not None:
        pvt_config = {
            "active_corner": project.pvt.active_corner,
            "model_lib_root": project.pvt.model_lib_root,
            "mode": project.pvt.mode,
            "score_aggregation": project.pvt.score_aggregation,
            "corners": [
                {
                    "name": c.name,
                    "enabled": c.enabled,
                    "temp": float(c.temp),
                    "supplies": [{"node": s.node, "value": float(s.value)} for s in c.supplies],
                    "model_includes": [
                        {"lib_file": m.lib_file, "section": m.section} for m in c.model_includes
                    ],
                    "params": {k: float(v) for k, v in c.params.items()},
                }
                for c in project.pvt.corners
            ],
        }

    return {
        "name": project.name,
        "description": project.description,
        "simulator": project.simulator,
        "ws_root": str(project.ws_root),
        "netlist": str(project.netlist),
        "schematic": str(project.schematic) if project.schematic is not None else None,
        "tech": {
            "name": project.tech_spec.name,
            "constraints": {k: float(v) for k, v in project.tech_spec.constraints.items()},
        },
        "pvt": pvt_config,
        "dut_params": dut_params,
        "testbenches": testbenches,
        "optimizer": {
            "type": project.optimizer_config.type,
            "name": project.optimizer_config.name,
            "budget": project.optimizer_config.budget,
            "random_seed": project.optimizer_config.random_seed,
        },
        "target_specs": specs,
    }


def _write_content_to_temp(yaml_content: str, base_yaml_path: str | None) -> str:
    """Persist edited/uploaded YAML to a real temp path and return it.

    When `base_yaml_path` is given (the user edited a loaded example in Monaco and
    hit Apply), a relative/empty ``ws_root`` is rewritten to an ABSOLUTE path
    anchored at the ORIGINAL YAML's directory before writing — so netlist/ws_root
    resolution is identical to applying the on-disk file, even though the temp lives
    elsewhere. Without this, the committed examples (``ws_root: ..``) would resolve
    against the temp dir and break live runs.
    """
    import tempfile
    text = yaml_content
    if base_yaml_path:
        try:
            data = yaml.safe_load(yaml_content)
            proj = data.get("project") if isinstance(data, dict) else None
            if isinstance(proj, dict):
                base = Path(base_yaml_path).expanduser().resolve().parent
                wsr = proj.get("ws_root")
                wsr_s = "" if wsr is None else str(wsr).strip()
                if not wsr_s:
                    proj["ws_root"] = str(base)
                elif not wsr_s.startswith("~") and not Path(wsr_s).is_absolute():
                    proj["ws_root"] = str((base / wsr_s).resolve())
                text = yaml.safe_dump(data, sort_keys=False)
        except yaml.YAMLError:
            text = yaml_content  # let from_yaml surface the real parse error below
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, prefix="spx_uploaded_"
    ) as tmp:
        tmp.write(text)
        return tmp.name


@router.post("/project/load", response_model=LoadProjectResponse)
def load_project(body: LoadRequest):
    # Load a registered project by id (report.md P3) → resolve to its project.yaml.
    if body.project_id:
        from spicexplorer_api.services import project_service
        try:
            yp = project_service.resolve_yaml(body.project_id, None)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValueError as e:
            # malformed project_id (path separators / '..') → 400, not an opaque 500 (BUG-B37)
            raise HTTPException(status_code=400, detail=str(e))
        try:
            project = Project_Setup.from_yaml(yp)
            return {"ok": True, "summary": _summarise(project), "yaml_path": str(yp)}
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

    # Apply from raw content (uploaded or edited YAML with no on-disk path). The
    # parsed summary doesn't need the netlist/ws_root paths to exist — those only
    # matter for live SPICE — so a project with relative paths still summarises.
    if body.yaml_content:
        import os
        # Persist the uploaded/edited YAML to a real path and RETURN that path, so
        # every path-keyed endpoint (optimize/score/sanity/sensitivity) resolves to
        # THIS project. Previously this returned yaml_path="", which made a live run
        # silently optimize the default cascode example instead of the applied YAML.
        tmp_path = _write_content_to_temp(body.yaml_content, body.yaml_path)
        try:
            project = Project_Setup.from_yaml(tmp_path)
            return {"ok": True, "summary": _summarise(project), "yaml_path": tmp_path}
        except Exception as e:
            os.unlink(tmp_path)
            raise HTTPException(status_code=422, detail=str(e))

    if not body.yaml_path:
        raise HTTPException(status_code=400, detail="Provide yaml_path or yaml_content")
    path = Path(body.yaml_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"YAML file not found: {path}")
    try:
        project = Project_Setup.from_yaml(path)
        return {"ok": True, "summary": _summarise(project), "yaml_path": str(path)}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/yaml-text", response_class=PlainTextResponse)
def yaml_text(path: str = Query(..., description="Absolute path of a project YAML")):
    """Return the raw text of a project YAML for the Setup editor.

    The Setup view populates Monaco from this after /project/load fills the
    rails. Served as plain text (the client reads ``response.text()``).

    Gated through the shared path validator (BUG-B2 sibling): the path must be a .yaml/.yml
    file resolving under an allowed root (examples / WORK_ROOT / an ``spx_uploaded_*`` temp),
    so this can't be turned into an arbitrary-file read of any YAML on the host.
    """
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path

    resolved = _validated_yaml_path(path)
    if resolved is None:
        raise HTTPException(
            status_code=400,
            detail="path must be a .yaml/.yml file under the repo examples or workspace",
        )
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"YAML file not found: {resolved}")
    return resolved.read_text()


@router.post("/project/validate", response_model=ValidateResponse)
def validate_yaml(body: ValidateRequest):
    errors: list[str] = []
    try:
        data = yaml.safe_load(body.yaml_content)
        if not isinstance(data, dict) or "project" not in data:
            errors.append("Top-level 'project:' key is required")
            return {"ok": False, "errors": errors}
    except yaml.YAMLError as e:
        return {"ok": False, "errors": [f"YAML parse error: {e}"]}

    # Write to a temp file and try full parse
    import os
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
        tmp.write(body.yaml_content)
        tmp_path = tmp.name
    try:
        Project_Setup.from_yaml(tmp_path)
        return {"ok": True, "errors": []}
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}
    finally:
        os.unlink(tmp_path)


@router.post("/project/generate", response_model=GenerateProjectResponse)
def generate_project(body: GenerateRequest):
    """Render wizard form → YAML string. If `save_path` is given, also write to disk."""
    try:
        yaml_text = generate_yaml(body.form)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"YAML generation failed: {e}")

    saved_path: Optional[str] = None
    if body.save_path:
        path = Path(body.save_path).expanduser()
        # A relative path would be resolved against the backend's CWD (/app in the
        # container → a non-writable root like /project_setup.yaml). Require an
        # absolute path so the target is unambiguous and writable.
        if not path.is_absolute():
            raise HTTPException(
                status_code=400,
                detail=(
                    f"save_path must be an absolute path (got '{body.save_path}'). "
                    "Enter an absolute Save path, e.g. /work/project_setup.yaml."
                ),
            )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml_text)
            saved_path = str(path)
        except OSError as e:
            raise HTTPException(status_code=400, detail=f"Could not write YAML to {path}: {e}")

    # Best-effort validation; surface errors but still return the rendered YAML
    errors: list[str] = []
    import os
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
        tmp.write(yaml_text)
        tmp_path = tmp.name
    try:
        Project_Setup.from_yaml(tmp_path)
    except Exception as e:
        errors.append(str(e))
    finally:
        os.unlink(tmp_path)

    return {
        "ok": not errors,
        "yaml": yaml_text,
        "errors": errors,
        "saved_path": saved_path,
    }


@router.post("/project/parse-to-form", response_model=ParseProjectResponse)
def parse_project_to_form(body: ParseToFormRequest):
    """Inverse of /project/generate — load a YAML and return a wizard-form dict."""
    if not body.yaml_path and not body.yaml_content:
        raise HTTPException(status_code=400, detail="Provide yaml_path or yaml_content")
    try:
        if body.yaml_content:
            data = yaml.safe_load(body.yaml_content)
        else:
            path = Path(body.yaml_path)  # type: ignore[arg-type]
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"YAML file not found: {path}")
            with path.open() as f:
                data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=422, detail=f"YAML parse error: {e}")

    if not isinstance(data, dict) or "project" not in data:
        raise HTTPException(status_code=422, detail="Top-level 'project:' key is required")

    form = project_dict_to_form(data)
    return {"ok": True, "form": form}
