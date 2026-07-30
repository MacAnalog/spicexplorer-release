"""POST /api/score — compute sigmoid vs. linear penalties for a project's specs."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from spicexplorer.core.domains import Project_Setup

from spicexplorer_api.services.score_service import apply_spec_overrides, compute_score

router = APIRouter()


def _get_project(yaml_path: str) -> Project_Setup:
    # Reload from disk every call (Project_Setup.from_yaml is cheap and
    # PDK-independent). A module-level cache previously returned stale specs
    # after the YAML was edited on disk — inconsistent with /sanity-check.
    from spicexplorer_api.routes.checkpoint import require_yaml_under_allowed_root

    # Funnel the caller path through the whitelist choke point BEFORE reading it — an
    # unvalidated path here is arbitrary-file-read + existence-oracle + error-echo (BUG-B2).
    p = require_yaml_under_allowed_root(yaml_path)  # 400 if out-of-bounds / wrong suffix
    if not p.exists():
        raise HTTPException(404, "YAML not found")  # in-bounds but missing — don't echo the path
    return Project_Setup.from_yaml(p)


class ScoreRequest(BaseModel):
    yaml_path: str
    metric_values: dict[str, float]
    selected_spec: str | None = None
    n_curve_points: int = 200
    # Ephemeral per-spec edits (Score Shaping "what-if"): spec name → partial dict of
    # {target, tolerance, weight, range, goal, enable}. Applied to the freshly-loaded
    # project before scoring; never written back to the YAML.
    spec_overrides: dict[str, dict] | None = None


# --- Response models (mirror score_service.compute_score; see src/types/README.md) ---
# Every key below is always present in compute_score's per_spec entries (the value-None
# branch and the value-present branch now share the same 8-key shape), so nullable keys
# use `X | None` with no default per the convention.
class SpecScore(BaseModel):
    linear: float | None
    sigmoid: float | None
    value: float | None
    target: float
    tolerance: float
    goal: str
    passes: bool | None
    weight: float


class ScoreCurve(BaseModel):
    values: list[float]
    linear: list[float]
    sigmoid: list[float]
    target: float
    tolerance: float
    goal: str


class ScoreAggregate(BaseModel):
    linear: float
    sigmoid: float


class ScoreResponse(BaseModel):
    per_spec: dict[str, SpecScore]
    aggregate: ScoreAggregate
    curve: ScoreCurve | None


@router.post("/score", response_model=ScoreResponse)
def score_endpoint(body: ScoreRequest):
    project = _get_project(body.yaml_path)
    apply_spec_overrides(project, body.spec_overrides)
    result = compute_score(
        project,
        body.metric_values,
        selected_spec=body.selected_spec,
        n_curve_points=body.n_curve_points,
    )
    return result
