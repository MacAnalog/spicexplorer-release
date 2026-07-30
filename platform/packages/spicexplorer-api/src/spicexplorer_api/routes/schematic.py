"""Serve the schematic SVG asset."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from spicexplorer_api.app_config import schematic_svg_path

router = APIRouter()


@router.get("/schematic")
def get_schematic():
    path = schematic_svg_path()
    if not path.exists():
        raise HTTPException(404, "Schematic SVG not found")
    return FileResponse(str(path), media_type="image/svg+xml")
