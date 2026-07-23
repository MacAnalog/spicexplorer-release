"""Typed I/O contract for the netlist→xschem tool.

A single Pydantic contract describing how the tool is invoked and what it produces. The REST adapter
(``spicexplorer-api``) and any MCP adapter reuse these shapes, so the request/response are defined
once here and feed the OpenAPI→TS codegen + MCP schemas.

The models are pure data — path validation, file writing and the work-dir layout are the adapter's
concern, not the tool's.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .emit import SchDocument
from .render import RenderResult

__all__ = ["XschemFromNetlistRequest", "XschemSchematicResult", "result_from"]


class XschemFromNetlistRequest(BaseModel):
    """Generate an xschem schematic from a SPICE netlist."""

    netlist_path: str | None = Field(
        None,
        description="Absolute path to a SPICE netlist (validated under the adapter's allowed roots).",
    )
    netlist_text: str | None = Field(
        None, description="Raw SPICE text, as an alternative to netlist_path."
    )
    name: str | None = Field(
        None, description="Schematic name / title; defaults to the netlist stem."
    )
    pdk: str = Field("ihp-sg13g2", description="Target PDK for MOSFET symbol mapping.")
    into: str | None = Field(
        None, description="Optional subckt *instance* name to descend into before generating."
    )
    render: Literal["none", "svg", "png"] = Field(
        "none", description="Also render the .sch to an image via headless xschem (svg/png)."
    )


class XschemSchematicResult(BaseModel):
    """The generated schematic + optional rendered image + a report of what was drawn / skipped."""

    sch_content: str = Field(
        description="The .sch text — viewable directly in the UI's xschem viewer."
    )
    sch_path: str | None = Field(None, description="Where the .sch was written, if persisted.")
    image_path: str | None = Field(None, description="The rendered image path, if produced.")
    image_fmt: Literal["svg", "png"] | None = Field(
        None, description="Format of the rendered image."
    )
    image_available: bool = Field(
        False, description="Whether xschem was available to render an image (False ⇒ .sch only)."
    )
    device_count: int = Field(0, description="Number of devices drawn.")
    label_count: int = Field(0, description="Number of net-name labels placed.")
    warnings: list[str] = Field(
        default_factory=list, description="Devices skipped, render notes, etc."
    )


def result_from(
    doc: SchDocument,
    *,
    sch_path: str | None = None,
    render: RenderResult | None = None,
) -> XschemSchematicResult:
    """Assemble the response from the emit document and an optional render outcome (pure, no I/O)."""
    warnings = list(doc.warnings)
    image_path = image_fmt = None
    image_available = False
    if render is not None:
        image_available = render.available
        if render.image_path is not None:
            image_path = str(render.image_path)
            image_fmt = render.fmt
        elif render.log:
            warnings.append(render.log.strip().splitlines()[-1])
    return XschemSchematicResult(
        sch_content=doc.text,
        sch_path=sch_path,
        image_path=image_path,
        image_fmt=image_fmt,
        image_available=image_available,
        device_count=doc.device_count,
        label_count=doc.label_count,
        warnings=warnings,
    )
