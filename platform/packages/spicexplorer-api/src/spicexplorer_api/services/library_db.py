"""Read-only adapter over the OPTIONAL ``spicexplorer-analog-db`` submodule.

Backs the Reference Library routes (``/api/library/*``) that feed the UI's analog-db catalog
browser: the class-grouped catalog, per-circuit datasheets + recorded SPICE results, the
per-class metric registry, and the functional sub-circuit template library.

``spicexplorer-analog-db`` was extracted to its own repo (it is **not** a platform ``uv``
workspace member — see the root ``pyproject.toml``); it ships as the ``examples/analog-db``
submodule and is installed editable only when present. So every reader here imports it
**lazily** and reports absence through :func:`availability` — exactly the PDK-absence contract
``GET /api/env`` uses. When the submodule is not installed/checked out the routes degrade to a
``503`` (or ``available: false`` on the status probe) instead of raising a ``500``.

This module does the *reading* (locate + parse + shape) so ``routes/library.py`` stays a thin
adapter. It never regenerates anything: the catalog is the committed, drift-guarded
``catalog.json`` (built in the analog-db repo's own harness), results are the committed
``results/*.json``, and the class/template registries are plain YAML.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# Recorded results + the catalog keep the analog-db-native **long** PDK keys
# (``ihp-sg13g2``/``sky130``/``gf180mcu``) — the database is the source of truth and the UI maps
# them to its short display keys. Results live at ``circuits/<id>/results/<pdk>__tt.json``.
_TT_CORNER = "tt"


def _modules() -> SimpleNamespace | None:
    """Import the analog-db reader modules, or ``None`` if the submodule isn't installed.

    Only the light readers (``paths``, ``model``) are imported here — never ``catalog`` (which
    pulls the deck-export chain); that one is imported lazily in :func:`load_catalog`'s fallback
    branch alone, so a normal catalog request (served from the committed JSON) never touches it.
    """
    try:
        from spicexplorer_analog_db import model, paths, scoreboard
    except Exception:
        return None
    return SimpleNamespace(model=model, paths=paths, scoreboard=scoreboard)


def availability() -> dict[str, Any]:
    """``{available, db_root, circuits, classes, reason}`` — the degradation probe.

    ``available`` is true only when the package imports **and** the database is checked out
    (``circuits/`` present). ``reason`` explains a false result for the UI's library-unavailable
    state; ``circuits``/``classes`` are cheap directory counts (no parsing)."""
    mods = _modules()
    if mods is None:
        return {
            "available": False,
            "db_root": None,
            "circuits": 0,
            "classes": [],
            "reason": "spicexplorer-analog-db is not installed in this environment",
        }
    paths, model = mods.paths, mods.model
    if not paths.db_present():
        return {
            "available": False,
            "db_root": str(paths.db_root()),
            "circuits": 0,
            "classes": [],
            "reason": "analog-db submodule is not checked out (circuits/ missing)",
        }
    return {
        "available": True,
        "db_root": str(paths.db_root()),
        "circuits": len(model.list_circuit_ids()),
        "classes": list(model.list_class_ids()),
        "reason": None,
    }


def _require() -> SimpleNamespace:
    """Return the reader modules or raise a 503-shaped error when the DB is unavailable."""
    from fastapi import HTTPException

    mods = _modules()
    if mods is None or not mods.paths.db_present():
        detail = availability()["reason"] or "analog-db unavailable"
        raise HTTPException(status_code=503, detail=detail)
    return mods


# --------------------------------------------------------------------------- catalog


def load_catalog() -> dict[str, Any]:
    """The class-grouped catalog: ``{schema, classes: {class: [ids]}, circuits: [...]}``.

    Serves the committed, drift-guarded ``catalog.json`` (fast, deterministic, no regeneration).
    Only if that file is absent does it fall back to building one in-process."""
    mods = _require()
    cat_path = mods.paths.catalog_path()
    if cat_path.is_file():
        return json.loads(cat_path.read_text())
    # Fallback: no committed catalog — build one. Imported lazily so the deck-export chain is
    # touched only on this rare path, never on a normal (file-backed) request.
    from spicexplorer_analog_db import catalog

    return catalog.build_catalog()


# --------------------------------------------------------------------------- per-circuit detail


def _circuit_base(circuit: Any) -> dict[str, Any]:
    """The catalog-shaped identity block for one circuit, read straight from its manifest (so a
    detail request is correct even if ``catalog.json`` is stale or missing)."""
    m = circuit.manifest
    return {
        "id": circuit.id,
        "class": circuit.klass,
        "display_name": m.get("display_name", ""),
        "compensation": m.get("compensation"),
        "stages": m.get("stages"),
        "ports": list(m.get("ports", [])),
        "pdks": circuit.pdks,
        "analyses": circuit.analyses,
        "status": circuit.status,
        "provenance": m.get("provenance", {}),
    }


def _read_result(corner: str, block: dict[str, Any]) -> dict[str, Any]:
    """Shape one scoreboard-entry corner block into ``{corner, run_at, measures, analyses,
    symbolic}``. ``measures`` flattens every analysis's ``measures`` block (the keys are unique
    across analyses) for the headline datasheet numbers; ``analyses`` keeps the raw blocks."""
    analyses = block.get("analyses", {}) or {}
    measures: dict[str, Any] = {}
    for ablock in analyses.values():
        for key, val in (ablock.get("measures") or {}).items():
            measures[key] = val
    symbolic: dict[str, Any] | None = None
    crosscheck = block.get("symbolic_crosscheck") or {}
    dc = (crosscheck.get("metrics") or {}).get("dc_gain_db")
    if dc:
        symbolic = {
            "sym": dc.get("symbolic"),
            "sim": dc.get("sim"),
            "err": dc.get("abs_error"),
            "tol": dc.get("tolerance"),
            "agrees": dc.get("agrees"),
        }
    return {
        "corner": corner,
        "run_at": (block.get("provenance") or {}).get("run_at"),
        "measures": measures,
        "analyses": analyses,
        "symbolic": symbolic,
    }


def load_circuit_detail(circuit_id: str) -> dict[str, Any]:
    """Identity block + datasheet + recorded results (per PDK, ``tt`` corner) for one circuit.

    Raises ``KeyError`` for an unknown id (the route maps it to a 404). The datasheet is the raw
    ``datasheet.yaml`` (heterogeneous, served verbatim); ``results`` is keyed by the long PDK
    name and omits PDKs that have no recorded ``results/*.json`` yet."""
    mods = _require()
    circuit = mods.model.load_circuit(circuit_id)  # KeyError on unknown id
    detail = _circuit_base(circuit)
    try:
        detail["datasheet"] = circuit.datasheet()
    except FileNotFoundError:
        detail["datasheet"] = {}
    # Make the detail a true superset of the catalog entry: carry its schematic refs + raw deck
    # index across, read from the committed catalog.json (cheap; no regeneration). If the catalog
    # file is absent these stay empty — the model defaults handle that.
    cat_path = mods.paths.catalog_path()
    if cat_path.is_file():
        try:
            entry = next(
                (
                    e
                    for e in json.loads(cat_path.read_text()).get("circuits", [])
                    if e.get("id") == circuit_id
                ),
                None,
            )
        except json.JSONDecodeError:
            entry = None
        if entry:
            detail["schematic"] = entry.get("schematic", {})
            detail["raw"] = entry.get("raw", {})
    detail["schematics"] = {mode: _rel(mods, p) for mode, p in _schematic_paths(mods, circuit).items() if p.is_file()}
    detail["results"] = _results_for(mods, circuit)
    return detail


# --------------------------------------------------------------------------- schematics

# The committed schematic views (plan_raw_export / plan_block_annotation), one ``.svg`` each.
# ``pure`` = plain topology, ``block_aware`` = detected blocks as coloured boxes, ``hierarchical``
# = block-diagram (one symbol per block); ``abstract`` is the pre-lowering snapshot fallback.
SCHEMATIC_MODES = ("block_aware", "hierarchical", "pure", "abstract")


def _rel(mods: SimpleNamespace, p: Path) -> str:
    try:
        return str(p.relative_to(mods.paths.db_root()))
    except ValueError:
        return str(p)


def _schematic_paths(mods: SimpleNamespace, circuit: Any) -> dict[str, Path]:
    """The on-disk ``.svg`` path for each mode (existence not checked here)."""
    raw = mods.paths.db_root() / "raw" / circuit.id
    return {
        "pure": raw / f"{circuit.id}.svg",
        "block_aware": raw / f"{circuit.id}_annotated.svg",
        "hierarchical": raw / "hier" / f"{circuit.id}.svg",
        "abstract": circuit.dir / "abstract" / "schematic.svg",
    }


# Reference materials a browser can display directly (hand-drawn scans, paper
# figures, committed renders). Vendored .sch sources have no render — listed
# separately so the UI can say they exist without pretending to show them.
_REF_IMAGE_EXTS = (".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp")


def schematic_sources(circuit_id: str) -> dict[str, Any]:
    """Every schematic the DB holds for one circuit, grouped by provenance.

    ``generated``: the netlist2xschem export-raw renders (the mode SVGs the
    datasheet viewer already streams). ``reference``: displayable hand-drawn /
    paper images under ``circuits/<id>/reference/`` — present for some circuits
    only, so the UI offers exactly what exists. ``reference_other`` names the
    non-displayable vendored sources (``.sch`` etc.) for honesty."""
    mods = _require()
    circuit = mods.model.load_circuit(circuit_id)  # KeyError on unknown id
    generated = [
        {"mode": mode, "path": _rel(mods, p)}
        for mode, p in _schematic_paths(mods, circuit).items()
        if p.is_file()
    ]
    reference: list[dict[str, Any]] = []
    reference_other: list[str] = []
    ref_dir = circuit.dir / "reference"
    if ref_dir.is_dir():
        for p in sorted(ref_dir.rglob("*")):
            if not p.is_file() or p.name.startswith("."):
                continue
            rel = p.relative_to(ref_dir).as_posix()
            if p.suffix.lower() in _REF_IMAGE_EXTS:
                reference.append({"name": rel, "path": _rel(mods, p)})
            elif p.suffix.lower() in (".sch", ".sym", ".asc", ".cir", ".sp", ".spice"):
                reference_other.append(rel)
    return {"circuit_id": circuit_id, "generated": generated,
            "reference": reference, "reference_other": reference_other}


def reference_image(circuit_id: str, name: str) -> tuple[bytes, str] | None:
    """Bytes + media type of one displayable reference file, or ``None``. The
    ``name`` is the reference-dir-relative path from :func:`schematic_sources`;
    the resolved file must stay inside ``circuits/<id>/reference/``."""
    mods = _require()
    circuit = mods.model.load_circuit(circuit_id)  # KeyError on unknown id
    ref_dir = (circuit.dir / "reference").resolve()
    p = (ref_dir / name).resolve()
    if not p.is_relative_to(ref_dir) or not p.is_file():
        return None
    ext = p.suffix.lower()
    if ext not in _REF_IMAGE_EXTS:
        return None
    media = {
        ".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
    }[ext]
    return p.read_bytes(), media


def schematic_svg(circuit_id: str, mode: str) -> bytes | None:
    """The committed schematic ``.svg`` bytes for one circuit + mode, or ``None`` if that mode
    isn't rendered for this circuit. Raises ``KeyError`` for an unknown circuit, ``ValueError`` for
    an unknown mode (the route maps them to 404 / 400)."""
    if mode not in SCHEMATIC_MODES:
        raise ValueError(f"unknown schematic mode {mode!r} (have: {', '.join(SCHEMATIC_MODES)})")
    mods = _require()
    circuit = mods.model.load_circuit(circuit_id)  # KeyError on unknown id
    p = _schematic_paths(mods, circuit).get(mode)
    return p.read_bytes() if p and p.is_file() else None


def _results_for(mods: SimpleNamespace, circuit: Any) -> dict[str, Any]:
    """``{pdk(long): shaped-result}`` for one circuit — the **baseline** scoreboard entry's ``tt``
    corner per PDK (plan_scoreboard D-8, the successor of ``results/<pdk>__tt.json``; PDKs with no
    recorded baseline are omitted)."""
    out: dict[str, Any] = {}
    base = mods.scoreboard.baselines(circuit)
    for pdk in circuit.pdks:
        did = base.get(pdk)
        if not did:
            continue
        ep = mods.scoreboard.entry_path(circuit, pdk, did)
        if not ep.is_file():
            continue
        entry = json.loads(ep.read_text())
        block = (entry.get("corners") or {}).get(_TT_CORNER)
        if block:
            out[pdk] = _read_result(_TT_CORNER, block)
    return out


def create_circuit(payload: dict[str, Any]) -> dict[str, Any]:
    """Scaffold a new **draft** circuit from a wizard payload and return its fresh catalog entry.

    Delegates to analog-db's ``authoring.scaffold_circuit`` (id sanitization, schema validation,
    overwrite refusal). Raises ``authoring.ScaffoldError`` (bad manifest → 400) or ``FileExistsError``
    (already exists → 409); ``_require`` raises 503 when the DB is absent. Does **not** rebuild the
    committed ``catalog.json`` (that is a deliberate offline step) — the returned entry lets the UI
    show the draft immediately."""
    mods = _require()
    from spicexplorer_analog_db import authoring

    cdir = authoring.scaffold_circuit(payload, datasheet=payload.get("datasheet"))
    circuit = mods.model.load_circuit(cdir.name)
    return {"id": circuit.id, "created": True, "circuit": _circuit_base(circuit)}


# ------------------------------------------------------------ start-project-from-catalog (project-fs P5)


def _safe_cell(circuit_id: str) -> str:
    """A filesystem-safe cell dir name derived from a circuit id."""
    keep = "".join(c if (c.isalnum() or c in "_-") else "_" for c in circuit_id)
    return keep.strip("_") or "dut"


def _circuit_dir(mods: SimpleNamespace, circuit_id: str) -> Path:
    """The on-disk dir for a catalog circuit; rejects traversal + unknown ids (404-shaped)."""
    from fastapi import HTTPException

    if not circuit_id or "/" in circuit_id or "\\" in circuit_id or ".." in circuit_id:
        raise HTTPException(status_code=404, detail=f"unknown circuit {circuit_id!r}")
    cdir = mods.paths.db_root() / "circuits" / circuit_id
    if not cdir.is_dir():
        raise HTTPException(status_code=404, detail=f"unknown circuit {circuit_id!r}")
    return cdir


def _source_netlist(cdir: Path, pdk: str | None) -> Path | None:
    """The netlist to seed, preferring the portable ``abstract/`` master, then the chosen (or any)
    PDK-lowered one."""
    candidates = [cdir / "abstract" / "netlist.spice"]
    if pdk:
        candidates.append(cdir / "pdk" / pdk / "netlist.spice")
    if (cdir / "pdk").is_dir():
        candidates += sorted((cdir / "pdk").glob("*/netlist.spice"))
    return next((c for c in candidates if c.is_file()), None)


def seed_from_catalog(
    circuit_id: str, *, name: str | None = None, pdk: str | None = None,
) -> dict[str, Any]:
    """Create a new WORK_ROOT v2 project seeded from an analog-db catalog circuit (project-fs P5).

    Copies the circuit's master netlist into ``design/cells/<cell>/netlist.spice``, records the
    catalog provenance in ``topology/selection.json`` and the ``manifest.source``, and (when a PDK
    is chosen/available) copies that PDK's ``sizing.yaml``. The project is created via
    ``project_service.create_project`` so it is a valid, registered, browsable project — its
    ``project.yaml`` starts as the default optimize job (a template to re-target at the seeded
    cell). Degrades ``503`` when analog-db is unavailable (via ``_require``). The circuit dir is
    read directly (not the strict model loader) so a partial corpus still seeds.
    """
    import yaml
    from spicexplorer_core.atomic_io import atomic_write_json

    from spicexplorer_api.services import project_service  # lazy: avoids any import cycle

    mods = _require()
    cdir = _circuit_dir(mods, circuit_id)

    meta: dict[str, Any] = {}
    cyaml = cdir / "circuit.yaml"
    if cyaml.is_file():
        try:
            meta = yaml.safe_load(cyaml.read_text()) or {}
        except Exception:
            meta = {}

    proj_name = str(name or meta.get("display_name") or circuit_id)
    pid = project_service.create_project(proj_name)
    pd = project_service.project_dir(pid)

    cell = _safe_cell(circuit_id)
    cell_dir = pd / "design" / "cells" / cell
    cell_dir.mkdir(parents=True, exist_ok=True)

    pdks = meta.get("pdks") or []
    chosen_pdk = pdk if (pdk and (cdir / "pdk" / pdk).is_dir()) else (pdks[0] if pdks else None)

    netlist_src = _source_netlist(cdir, chosen_pdk)
    if netlist_src is not None:
        shutil.copy2(netlist_src, cell_dir / "netlist.spice")
    if chosen_pdk:
        sizing = cdir / "pdk" / chosen_pdk / "sizing.yaml"
        if sizing.is_file():
            shutil.copy2(sizing, cell_dir / "sizing.yaml")

    atomic_write_json(pd / "topology" / "selection.json", {
        "source": "analog-db",
        "circuit_id": circuit_id,
        "cell": cell,
        "class": meta.get("class"),
        "display_name": meta.get("display_name"),
        "pdk": chosen_pdk,
        "netlist_from": netlist_src.relative_to(cdir).as_posix() if netlist_src else None,
        "provenance": meta.get("provenance", {}),
        "selected_at": datetime.now().isoformat(timespec="seconds"),
    }, indent=2)

    m = project_service.read_manifest(pid)
    m["source"] = {"kind": "analog-db", "ref": circuit_id, "pdk": chosen_pdk}
    m["default_pdk"] = chosen_pdk
    project_service.write_manifest(pid, m)

    return {"id": pid, "circuit_id": circuit_id, "cell": cell, "pdk": chosen_pdk,
            "netlist_seeded": netlist_src is not None}


def load_all_results() -> dict[str, dict[str, Any]]:
    """``{circuit_id: {pdk(long): result}}`` across every circuit — the bulk recorded-results map
    the browse view needs (the catalog itself carries no measured numbers). Circuits with no
    recorded result are omitted entirely, so the map is sparse (only the few measured circuits)."""
    mods = _require()
    out: dict[str, dict[str, Any]] = {}
    for circuit in mods.model.load_all_circuits():
        per = _results_for(mods, circuit)
        if per:
            out[circuit.id] = per
    return out


# --------------------------------------------------------------------------- class registry


_SLOT_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def _load_yaml_map(p: Path) -> dict[str, Any]:
    import yaml

    try:
        data = yaml.safe_load(p.read_text()) if p.is_file() else None
    except (yaml.YAMLError, OSError):
        data = None
    return data if isinstance(data, dict) else {}


def _tb_profile(
    mods: SimpleNamespace, shared: Path, class_id: str, name: str, spectre_benches: dict[str, Any]
) -> dict[str, Any]:
    """One class testbench's engine availability + authored profile, derived from the repo:
    ``ngspice`` iff the committed ``.spice`` template resolves (class-scoped first, shared
    fallback), ``spectre`` iff the bench is wired in the class ``spectre-benches.yaml``.
    ``slots`` are the template's ``${...}`` binding slots; ``description`` the authored
    header line."""
    prof: dict[str, Any] = {
        "name": name,
        "engines": [],
        "path": None,
        "description": "",
        "slots": [],
        "spectre_analyses": 0,
        "spectre_calculator": 0,
    }
    for cand in (
        shared / "classes" / class_id / "testbench-templates" / f"{name}.spice",
        shared / "testbench-templates" / f"{name}.spice",
    ):
        if cand.is_file():
            text = cand.read_text(errors="replace")
            prof["engines"].append("ngspice")
            prof["path"] = _rel(mods, cand)
            prof["slots"] = list(dict.fromkeys(_SLOT_RE.findall(text)))
            # Authored header: "** AUTHORED TEMPLATE — class/name: <desc>" — some templates
            # carry the description after the colon, others on the next comment line. Keep
            # the first sentence of the substance.
            comments = [ln.lstrip("*").strip() for ln in text.lstrip().splitlines() if ln.startswith("*")]
            desc = ""
            if comments:
                first = comments[0]
                if ": " in first:
                    desc = first.split(": ", 1)[1]
                elif first.upper().startswith("AUTHORED TEMPLATE") and len(comments) > 1:
                    desc = comments[1]
                else:
                    desc = first
            if ". " in desc:
                desc = desc.split(". ", 1)[0] + "."
            prof["description"] = desc
            break
    bench = spectre_benches.get(name)
    if isinstance(bench, dict):
        prof["engines"].append("spectre")
        prof["spectre_analyses"] = len(bench.get("analyses") or [])
        prof["spectre_calculator"] = len(bench.get("calculator") or [])
    return prof


def load_pdks() -> list[dict[str, Any]]:
    """The PDK registry (``_shared/pdk/<id>.yaml``): which PDKs the DB binds and which
    simulator the in-library router runs each on (the committed ``sim_engine`` marker) —
    the honest pdk→engine matrix (open PDKs → ngspice; a Spectre-routed PDK → spectre)."""
    mods = _require()
    out: list[dict[str, Any]] = []
    for p in sorted((mods.paths.db_root() / "_shared" / "pdk").glob("*.yaml")):
        reg = _load_yaml_map(p)
        out.append(
            {
                "id": str(reg.get("pdk") or p.stem),
                "sim_engine": str(reg.get("sim_engine") or "ngspice"),
            }
        )
    return out


def load_classes() -> list[dict[str, Any]]:
    """The per-class registry (``_shared/classes/<id>/metrics.yaml``): the canonical metric
    vocabulary + owned testbench-template names that drive the Register wizard, each template
    enriched with its per-engine availability + authored profile (``testbenches``)."""
    mods = _require()
    shared = mods.paths.db_root() / "_shared"
    out: list[dict[str, Any]] = []
    for class_id in mods.model.list_class_ids():
        data = mods.model.load_class(class_id)
        names = list(data.get("templates", []))
        benches = (
            _load_yaml_map(shared / "classes" / class_id / "spectre-benches.yaml").get("benches")
            or {}
        )
        out.append(
            {
                "class": data.get("class", class_id),
                "description": data.get("description", "").strip(),
                "canonical_metrics": list(data.get("canonical_metrics", [])),
                "templates": names,
                "testbenches": [_tb_profile(mods, shared, class_id, n, benches) for n in names],
            }
        )
    return out


# --------------------------------------------------------------------------- testbench templates


def _safe_token(*parts: str) -> bool:
    return all(p and all(c.isalnum() or c in "_-." for c in p) and ".." not in p for p in parts)


def testbench_netlist(class_id: str, name: str, engine: str = "ngspice") -> dict[str, Any] | None:
    """One class testbench's engine source, for the Library viewer.

    ``engine="ngspice"`` (default): the authored ``.spice`` template — class-scoped
    ``_shared/classes/<class>/testbench-templates/<name>.spice`` first, else the
    cross-class ``_shared/testbench-templates/<name>.spice``.

    ``engine="spectre"``: the closed lane has no per-bench deck file — a bench is
    *wired* in ``_shared/classes/<class>/spectre-benches.yaml`` from the engine-level
    analysis templates (``engines/spectre/analyses.yaml``) and SKILL calculator
    expressions (``engines/spectre/calculator.yaml``). This composes those three into
    one bench-scoped YAML document (wiring + the referenced template/expression rows
    verbatim) so the calculator SKILL is readable in place.

    ``None`` when the bench/engine source doesn't exist (or the ids carry path
    characters — ids are always plain tokens)."""
    mods = _require()
    if not _safe_token(class_id, name):
        return None
    shared = mods.paths.db_root() / "_shared"
    if engine == "spectre":
        return _spectre_bench_view(mods, shared, class_id, name)
    for cand in (
        shared / "classes" / class_id / "testbench-templates" / f"{name}.spice",
        shared / "testbench-templates" / f"{name}.spice",
    ):
        if cand.is_file():
            return {
                "class": class_id,
                "name": name,
                "engine": "ngspice",
                "language": "spice",
                "path": _rel(mods, cand),
                "content": cand.read_text(errors="replace"),
            }
    return None


def _spectre_bench_view(
    mods: SimpleNamespace, shared: Path, class_id: str, name: str
) -> dict[str, Any] | None:
    import yaml

    bench_path = shared / "classes" / class_id / "spectre-benches.yaml"
    bench = (_load_yaml_map(bench_path).get("benches") or {}).get(name)
    if not isinstance(bench, dict):
        return None

    eng = shared / "engines" / "spectre"
    templates = _load_yaml_map(eng / "analyses.yaml").get("templates") or {}
    expressions = _load_yaml_map(eng / "calculator.yaml").get("expressions") or {}
    used_templates = [
        a["template"] for a in bench.get("analyses") or []
        if isinstance(a, dict) and a.get("template") in templates
    ]
    used_exprs = [
        c["expr"] for c in bench.get("calculator") or []
        if isinstance(c, dict) and c.get("expr") in expressions
    ]
    doc = {
        "bench": {name: bench},
        "analysis_templates": {k: templates[k] for k in dict.fromkeys(used_templates)},
        "calculator_expressions": {k: expressions[k] for k in dict.fromkeys(used_exprs)},
    }
    header = (
        f"# Spectre engine view — {class_id}/{name} (composed, read-only)\n"
        f"# bench wiring:  _shared/classes/{class_id}/spectre-benches.yaml\n"
        f"# analyses:      _shared/engines/spectre/analyses.yaml (referenced templates)\n"
        f"# calculator:    _shared/engines/spectre/calculator.yaml (referenced SKILL expressions)\n"
        f"#\n"
        f"# The deck stimulus still rides in from the class ngspice template — the closed\n"
        f"# lane only swaps the analyses + result-reading (OCEAN) route shown here.\n\n"
    )
    return {
        "class": class_id,
        "name": name,
        "engine": "spectre",
        "language": "yaml",
        "path": _rel(mods, bench_path),
        "content": header + yaml.safe_dump(doc, sort_keys=False, width=100),
    }


# --------------------------------------------------------------------------- functional templates


def _template_rows(mods: SimpleNamespace) -> Iterator[tuple[str, Path, dict[str, Any]]]:
    """Yield ``(family, family_dir, row)`` for every template row across all family manifests
    (``templates/*/manifest.yaml``). Malformed/empty manifests and rows without an ``id`` are
    skipped so one bad family can't break the panel."""
    import yaml

    root = mods.paths.db_root() / "templates"
    if not root.is_dir():
        return
    for manifest in sorted(root.glob("*/manifest.yaml")):
        try:
            data = yaml.safe_load(manifest.read_text()) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        rows = data.get("templates")
        if not isinstance(rows, list):
            continue
        family = data.get("family", manifest.parent.name)
        for row in rows:
            if isinstance(row, dict) and "id" in row:
                yield family, manifest.parent, row


def load_templates() -> dict[str, Any]:
    """The functional sub-circuit template library (``templates/*/manifest.yaml``) — the blocks
    the circuitgraph matcher overlays (current mirrors, diff pairs, …).

    Returns ``{families: [...], templates: [...]}``; each template carries ``image`` — the repo-
    relative path of its committed PNG render, or ``None`` when absent (fetch the bytes from
    ``GET /library/templates/{id}/image``)."""
    mods = _require()
    families: list[str] = []
    templates: list[dict[str, Any]] = []
    for family, family_dir, row in _template_rows(mods):
        if family not in families:
            families.append(family)
        ports = row.get("ports") or {}
        img = row.get("image")
        img_path = (family_dir / img) if isinstance(img, str) and img else None
        templates.append(
            {
                "id": row["id"],
                "display_name": row.get("display_name", ""),
                "family": family,
                "polarity": row.get("polarity"),
                "role": row.get("role"),
                "class": row.get("class"),
                "netlist": row.get("netlist"),
                "ports": ports if isinstance(ports, dict) else {},
                "image": _rel(mods, img_path) if img_path and img_path.is_file() else None,
            }
        )
    return {"families": families, "templates": templates}


def template_netlist(template_id: str) -> dict[str, Any] | None:
    """The committed netlist source for one functional template, or ``None`` when the id
    is unknown or carries no ``netlist:`` path. Same posture as :func:`template_image`:
    the id is matched against manifest rows, and the resolved file must stay inside the
    template's family dir — the manifest path is data, never a traversal vector."""
    mods = _require()
    for _family, family_dir, row in _template_rows(mods):
        if row.get("id") == template_id:
            rel = row.get("netlist")
            if not isinstance(rel, str) or not rel:
                return None
            p = (family_dir / rel).resolve()
            if not p.is_relative_to(family_dir.resolve()) or not p.is_file():
                return None
            return {
                "id": template_id,
                "path": _rel(mods, p),
                "language": "spice",
                "content": p.read_text(errors="replace"),
            }
    return None


def template_image(template_id: str) -> bytes | None:
    """The committed PNG render for one functional template, or ``None`` when the id is unknown
    or has no committed image. The id is matched against the manifest rows — never used to build a
    filesystem path directly — so it cannot traverse outside ``templates/``."""
    mods = _require()
    for _family, family_dir, row in _template_rows(mods):
        if row.get("id") == template_id:
            img = row.get("image")
            if not isinstance(img, str) or not img:
                return None
            p = family_dir / img
            return p.read_bytes() if p.is_file() else None
    return None
