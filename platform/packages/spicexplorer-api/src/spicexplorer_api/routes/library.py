"""Reference Library routes (``/api/library/*``) — read the analog-db catalog for the UI browser.

Thin adapter over :mod:`spicexplorer_api.services.library_db`, which reads the OPTIONAL
``examples/analog-db`` submodule. analog-db is not a workspace member, so these routes degrade
gracefully: ``GET /api/library/status`` always answers (``available: false`` when the DB is
absent), and the data routes return ``503`` rather than ``500`` when it isn't checked out —
mirroring the PDK-absence contract on ``GET /api/env``.

PDK keys are the analog-db-native long names (``ihp-sg13g2``/``sky130``/``gf180mcu``); the UI
maps them to its short display keys.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from spicexplorer_api.services import library_db

router = APIRouter()


# --- Response models (see ../../../../spicexplorer-ui/src/types/README.md) ----------------------
class LibraryStatus(BaseModel):
    """Degradation probe — the library analogue of ``GET /api/env``."""

    available: bool
    db_root: str | None = None
    circuits: int = 0
    classes: list[str] = Field(default_factory=list)
    reason: str | None = None


class CatalogCircuit(BaseModel):
    # ``class`` is a Python keyword: the field is ``klass`` with the ``class`` alias, emitted as
    # ``class`` (FastAPI serializes ``response_model_by_alias=True`` by default). ``provenance``
    # is kept a free dict (source/designer/license/paper/aliases) so no field is dropped.
    model_config = ConfigDict(populate_by_name=True)

    id: str
    klass: str = Field(alias="class")
    display_name: str = ""
    compensation: str | None = None
    stages: int | None = None
    pdks: list[str] = Field(default_factory=list)
    analyses: list[str] = Field(default_factory=list)
    status: str = "draft"
    provenance: dict[str, Any] = Field(default_factory=dict)
    schematic: dict[str, str] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class CatalogResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_id: str = Field(default="", alias="schema")
    classes: dict[str, list[str]] = Field(default_factory=dict)
    circuits: list[CatalogCircuit] = Field(default_factory=list)


class CircuitResult(BaseModel):
    """One recorded SPICE result (``tt`` corner). ``measures`` flattens the per-analysis blocks;
    ``analyses`` keeps them raw; ``symbolic`` is the netlist2tf dc-gain cross-check when present."""

    corner: str = "tt"
    run_at: str | None = None
    measures: dict[str, Any] = Field(default_factory=dict)
    analyses: dict[str, Any] = Field(default_factory=dict)
    symbolic: dict[str, Any] | None = None


class CreateCircuitRequest(BaseModel):
    """The Register-wizard payload for a new draft circuit. `status` is not accepted — a scaffold is
    always a draft. `class` is the field's alias (Python keyword)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    klass: str = Field(alias="class")
    display_name: str = ""
    compensation: str | None = None
    stages: int | None = None
    ports: list[str] = Field(default_factory=list)
    pdks: list[str] = Field(default_factory=list)
    analyses: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    datasheet: dict[str, Any] | None = None


class CreateCircuitResponse(BaseModel):
    id: str
    created: bool
    circuit: CatalogCircuit


class CircuitDetail(CatalogCircuit):
    """A catalog entry plus its ports, datasheet, recorded results, and the schematic views
    that exist for it (``schematics`` maps each available mode → repo-relative ``.svg`` path;
    fetch the bytes from ``GET /library/circuits/{id}/schematic?mode=``)."""

    ports: list[str] = Field(default_factory=list)
    datasheet: dict[str, Any] = Field(default_factory=dict)
    schematics: dict[str, str] = Field(default_factory=dict)
    results: dict[str, CircuitResult] = Field(default_factory=dict)


class ResultsResponse(BaseModel):
    """Bulk recorded-results map: ``{circuit_id: {pdk: result}}`` (sparse — only measured circuits)."""

    results: dict[str, dict[str, CircuitResult]] = Field(default_factory=dict)


class ClassTestbench(BaseModel):
    """One class testbench's engine availability + authored profile, derived from the repo
    (never hardcoded): ``ngspice`` iff the committed ``.spice`` template exists, ``spectre``
    iff the bench is wired in the class ``spectre-benches.yaml``. ``slots`` are the template's
    ``${...}`` binding slots; ``spectre_*`` count the wired analyses / SKILL calculator rows."""

    name: str
    engines: list[str] = Field(default_factory=list)
    path: str | None = None
    description: str = ""
    slots: list[str] = Field(default_factory=list)
    spectre_analyses: int = 0
    spectre_calculator: int = 0


class LibraryClass(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    class_id: str = Field(alias="class")
    description: str = ""
    canonical_metrics: list[str] = Field(default_factory=list)
    templates: list[str] = Field(default_factory=list)
    testbenches: list[ClassTestbench] = Field(default_factory=list)


class ClassesResponse(BaseModel):
    classes: list[LibraryClass] = Field(default_factory=list)


class SubcircuitTemplate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    display_name: str = ""
    family: str = ""
    polarity: str | None = None
    role: str | None = None
    klass: str | None = Field(default=None, alias="class")
    netlist: str | None = None
    ports: dict[str, str] = Field(default_factory=dict)
    # Repo-relative path of the committed PNG render, or None if absent. Fetch the bytes
    # from GET /library/templates/{id}/image (this field just says whether one exists).
    image: str | None = None


class TemplatesResponse(BaseModel):
    families: list[str] = Field(default_factory=list)
    templates: list[SubcircuitTemplate] = Field(default_factory=list)


# --- Routes -------------------------------------------------------------------------------------
@router.get("/library/status", response_model=LibraryStatus, summary="Library availability probe")
def library_status():
    """Whether the analog-db catalog is reachable (always answers, even when it is not)."""
    return library_db.availability()


@router.get("/library/catalog", response_model=CatalogResponse, summary="Class-grouped catalog")
def library_catalog():
    """The full catalog — every circuit + its class grouping (the Library browse list)."""
    return library_db.load_catalog()


@router.get(
    "/library/circuits/{circuit_id}",
    response_model=CircuitDetail,
    summary="One circuit's datasheet + recorded results",
)
def library_circuit(circuit_id: str):
    """Identity + datasheet + per-PDK recorded results for one circuit (the datasheet view)."""
    try:
        return library_db.load_circuit_detail(circuit_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown circuit {circuit_id!r}")


@router.get(
    "/library/circuits/{circuit_id}/schematic",
    summary="Serve a circuit schematic SVG by mode",
    responses={200: {"content": {"image/svg+xml": {}}}},
)
def library_circuit_schematic(circuit_id: str, mode: str = "block_aware"):
    """Stream the committed schematic ``.svg`` for one circuit in one of the views
    (`block_aware` · `hierarchical` · `pure` · `abstract`). 404 when the circuit or that mode's
    render is absent (the detail's `schematics` map lists which modes exist)."""
    try:
        svg = library_db.schematic_svg(circuit_id, mode)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown circuit {circuit_id!r}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if svg is None:
        raise HTTPException(status_code=404, detail=f"no {mode!r} schematic for {circuit_id!r}")
    return Response(content=svg, media_type="image/svg+xml")


class SchematicSourceGenerated(BaseModel):
    mode: str
    path: str


class SchematicSourceReference(BaseModel):
    # reference-dir-relative name (also the fetch key for /reference-image)
    name: str
    path: str


class SchematicSourcesResponse(BaseModel):
    circuit_id: str
    # netlist2xschem export-raw renders (always browser-displayable SVGs)
    generated: list[SchematicSourceGenerated] = Field(default_factory=list)
    # displayable hand-drawn / paper images — present for SOME circuits only
    reference: list[SchematicSourceReference] = Field(default_factory=list)
    # vendored non-displayable sources (.sch etc.) — listed for honesty
    reference_other: list[str] = Field(default_factory=list)


@router.get(
    "/library/circuits/{circuit_id}/schematic-sources",
    response_model=SchematicSourcesResponse,
    summary="Every schematic the DB holds for one circuit (generated + hand-drawn)",
)
def library_schematic_sources(circuit_id: str):
    """The availability inventory behind the datasheet's "Open in Schematic" picker:
    autogenerated mode SVGs plus whatever displayable hand-drawn/paper reference images
    this circuit vendors (often none — the client offers exactly what exists)."""
    try:
        return library_db.schematic_sources(circuit_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown circuit {circuit_id!r}")


@router.get(
    "/library/circuits/{circuit_id}/reference-image",
    summary="Serve one displayable reference image (hand-drawn / paper figure)",
    responses={200: {"content": {"image/*": {}}}},
)
def library_reference_image(circuit_id: str, name: str):
    """Stream one reference image by its ``schematic-sources`` name (reference-dir-relative;
    traversal-safe). 404 when the circuit or file is unknown / not displayable."""
    try:
        result = library_db.reference_image(circuit_id, name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown circuit {circuit_id!r}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"no displayable reference {name!r}")
    data, media = result
    return Response(content=data, media_type=media)


@router.get("/library/results", response_model=ResultsResponse, summary="Bulk recorded-results map")
def library_results():
    """Every circuit's recorded results keyed `{id: {pdk: result}}` — the browse view's measured
    numbers in one call (the catalog itself carries none). Sparse: only measured circuits appear."""
    return {"results": library_db.load_all_results()}


@router.post(
    "/library/circuits",
    response_model=CreateCircuitResponse,
    status_code=201,
    summary="Scaffold a new draft circuit (Register wizard)",
)
def library_create_circuit(req: CreateCircuitRequest):
    """Create a **draft** circuit dir from the wizard payload (manifest + optional datasheet stub)
    and return its catalog entry so the UI can show it immediately. 400 on a bad manifest, 409 if
    the circuit id already exists, 503 when analog-db is unavailable."""
    try:
        return library_db.create_circuit(req.model_dump(by_alias=True))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:  # authoring.ScaffoldError (bad id / missing fields / schema failure)
        raise HTTPException(status_code=400, detail=str(e))


class SeedProjectRequest(BaseModel):
    name: str | None = Field(None, description="Project name (default: the circuit's display name)")
    pdk: str | None = Field(None, description="PDK to seed sizing from (default: the circuit's first)")


class SeedProjectResponse(BaseModel):
    id: str
    circuit_id: str
    cell: str
    pdk: str | None
    netlist_seeded: bool


@router.post(
    "/library/circuits/{circuit_id}/project",
    response_model=SeedProjectResponse,
    status_code=201,
    summary="Start a new project seeded from a catalog circuit",
)
def library_start_project(circuit_id: str, req: SeedProjectRequest):
    """Create a new WORK_ROOT v2 project seeded from an analog-db catalog circuit — its master
    netlist copied into ``design/cells/<cell>/`` and the catalog provenance recorded in
    ``topology/selection.json`` + the manifest (project-fs P5). 404 for an unknown circuit id,
    503 when analog-db is unavailable."""
    return library_db.seed_from_catalog(circuit_id, name=req.name, pdk=req.pdk)


@router.get("/library/classes", response_model=ClassesResponse, summary="Per-class metric registry")
def library_classes():
    """The per-class registry (metric vocabulary + testbench templates) for the Register wizard."""
    return {"classes": library_db.load_classes()}


class LibraryPdk(BaseModel):
    """One bound PDK and the simulator the in-library router runs it on (the committed
    ``sim_engine`` marker in ``_shared/pdk/<id>.yaml`` — repo-derived, never asserted)."""

    id: str
    sim_engine: str


class PdksResponse(BaseModel):
    pdks: list[LibraryPdk] = Field(default_factory=list)


@router.get("/library/pdks", response_model=PdksResponse, summary="PDK registry (pdk → routed engine)")
def library_pdks():
    """The honest pdk→simulator matrix: every PDK the DB binds, each with the engine its
    committed registry routes to (open PDKs → ngspice; a Spectre-routed kit → spectre)."""
    return {"pdks": library_db.load_pdks()}


class TestbenchNetlistResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    klass: str = Field(alias="class")
    name: str
    engine: str = "ngspice"
    # what the client should highlight the content as: "spice" | "yaml"
    language: str = "spice"
    # db-root-relative source path (the .spice template, or the spectre bench wiring)
    path: str
    content: str


@router.get(
    "/library/testbenches/{class_id}/{name}/netlist",
    response_model=TestbenchNetlistResponse,
    summary="One testbench's engine source (ngspice deck / Spectre bench + calculator)",
)
def library_testbench_netlist(class_id: str, name: str, engine: str = "ngspice"):
    """``engine=ngspice``: the authored ``.spice`` template (``${...}`` binding slots
    intact). ``engine=spectre``: the bench's closed-lane wiring composed with the engine
    analysis templates and the SKILL calculator expressions it references (YAML). 404
    when that engine has no source for this bench."""
    if engine not in ("ngspice", "spectre"):
        raise HTTPException(status_code=400, detail=f"unknown engine {engine!r}")
    result = library_db.testbench_netlist(class_id, name, engine=engine)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"no {engine} source for testbench {class_id}/{name}",
        )
    return result


@router.get(
    "/library/templates",
    response_model=TemplatesResponse,
    summary="Functional sub-circuit template library",
)
def library_templates():
    """The matcher's functional sub-circuit templates (current mirrors, diff pairs, …)."""
    return library_db.load_templates()


class TemplateNetlistResponse(BaseModel):
    id: str
    # db-root-relative path of the committed netlist the manifest row points at
    path: str
    language: str = "spice"
    content: str


@router.get(
    "/library/templates/{template_id}/netlist",
    response_model=TemplateNetlistResponse,
    summary="One functional template's committed netlist source",
)
def library_template_netlist(template_id: str):
    """The hand-authored netlist behind a functional template (what the circuitgraph
    matcher's topology is defined by). 404 when the id is unknown or the manifest row
    carries no ``netlist:`` file."""
    result = library_db.template_netlist(template_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"no netlist for template {template_id!r}")
    return result


@router.get(
    "/library/templates/{template_id}/image",
    summary="Serve a functional-template PNG render",
    responses={
        200: {"content": {"image/png": {}}, "description": "The template's net-colour-coded PNG"},
        404: {"description": "Unknown template id, or no committed image for it"},
    },
)
def library_template_image(template_id: str):
    """Stream the committed net-colour-coded PNG render of one functional template (the ``image:``
    beside its ``.sch``). 404 when the id is unknown or has no committed render (the
    ``/library/templates`` list's ``image`` field says which templates have one)."""
    png = library_db.template_image(template_id)
    if png is None:
        raise HTTPException(status_code=404, detail=f"no image for template {template_id!r}")
    return Response(content=png, media_type="image/png")
