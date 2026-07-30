"""GET /api/config — return app_config.json with resolved paths for the frontend."""
from fastapi import APIRouter
from pydantic import BaseModel

from spicexplorer_api.app_config import (
    default_yaml_path,
    preset_checkpoint_paths,
    schematic_svg_path,
)
from spicexplorer_api.routes.checkpoint import _infer_score_fn

router = APIRouter()


class PresetCheckpoint(BaseModel):
    id: str
    label: str
    path: str
    type: str
    score_fn: str
    exists: bool


class ConfigResponse(BaseModel):
    default_yaml: str
    preset_checkpoints: list[PresetCheckpoint]
    schematic_svg_path: str


@router.get("/config", response_model=ConfigResponse)
def get_config():
    checkpoints = []
    for key, path in preset_checkpoint_paths().items():
        checkpoints.append({
            "id": key,
            "label": key.replace("_", " ").title(),
            "path": str(path),
            "type": "csv" if path.suffix == ".csv" else "json",
            "score_fn": _infer_score_fn(path),  # single source of truth (also handles "linear")
            "exists": path.exists(),
        })
    return {
        "default_yaml": str(default_yaml_path()),
        "preset_checkpoints": checkpoints,
        "schematic_svg_path": str(schematic_svg_path()),
    }
