"""The class-aware ``catalog.json`` — the machine-readable entry point.

A typed, queryable index of every circuit + its derived status, grouped by class. Generated
deterministically; Tier 0 diffs the committed file against a fresh build (the determinism guard).
"""

from __future__ import annotations

import json
from typing import Any

from . import export, paths, scoreboard
from .model import Circuit, load_all_circuits

CATALOG_SCHEMA = "spicexplorer/catalog@1"


def _schematic_refs(c: Circuit) -> dict[str, str]:
    """Reference-only pointers to authored schematics that exist on disk: the abstract
    topology snapshot + each PDK's primary DUT schematic (the non-testbench ``*.svg``), plus any
    upstream reference figure (the original paper/AnalogGym snapshot under ``reference/``). xschem
    nets schematic→SPICE, not the reverse, so this only *indexes* what's authored — never generates."""
    out: dict[str, str] = {}
    root = paths.db_root()
    arts = c.manifest.get("artifacts") or {}
    art = arts.get("schematic")
    abstract = c.dir / art if art else c.dir / "abstract" / "schematic.svg"
    if abstract.is_file():
        out["abstract"] = str(abstract.relative_to(root))
    ref = arts.get("reference_schematic")
    if ref and (c.dir / ref).is_file():
        out["reference"] = str((c.dir / ref).relative_to(root))
    for pdk in c.pdks:
        sdir = c.dir / "pdk" / pdk / "schematic"
        if not sdir.is_dir():
            continue
        svgs = sorted(p for p in sdir.glob("*.svg") if "_tb" not in p.name)
        if svgs:
            out[pdk] = str(svgs[0].relative_to(root))
    return out


def _reference_index(c: Circuit) -> list[dict[str, Any]]:
    """Index a reference circuit's foreign/proprietary bindings: every authored ``.scs`` deck
    under the binding (searched recursively — upstream layouts vary), classified by its path role
    (dut / tb / runs / other), as db-root-relative paths. Lets agents find a reference circuit AND
    its testbenches without lowering anything."""
    root = paths.db_root()
    out: list[dict[str, Any]] = []
    for entry in c.references:
        bdir = c.reference_dir(entry)
        binding: dict[str, Any] = {
            "dir": str(entry.get("dir", "")),
            "tool": entry.get("tool"),
            "node": entry.get("node"),
        }
        buckets: dict[str, list[str]] = {}
        if bdir.is_dir():
            for p in sorted(bdir.rglob("*.scs")):
                segs = {s.lower() for s in p.relative_to(bdir).parts[:-1]}
                name = p.stem.lower()
                role = (
                    "tb" if ("tb" in segs or name.startswith("tb_") or name.endswith("_tb"))
                    else "runs" if ("runs" in segs or "variants" in segs)
                    else "dut" if ("dut" in segs or name.endswith("_dut"))
                    else "other"
                )
                buckets.setdefault(role, []).append(str(p.relative_to(root)))
        for role in ("dut", "tb", "runs", "other"):
            if buckets.get(role):
                binding[role] = buckets[role]
        out.append(binding)
    return out


def _params_block(c: Circuit) -> dict[str, Any] | None:
    """Per-circuit parameter-provenance summary: symbol counts by class,
    the shipped tying (group -> kind), and the detected-but-untied WARNINGS — persisted here
    so the info survives outside a verify run. Absent until the circuit adopts
    ``abstract/params.yaml``."""
    from . import params as par

    doc = par.load_params_doc(c.dir)
    if not doc:
        return None
    block: dict[str, Any] = {
        "devices": len(doc.get("devices") or {}),
        "groups": {g["name"]: g.get("kind") for g in doc.get("groups") or []},
        "ratios": len(doc.get("ratios") or []),
        "symbols": {},
    }
    for pdk in c.pdks:
        if not (c.dir / "pdk" / pdk / "sizing.yaml").is_file():
            continue
        cls = par.classify_symbols(doc, c.sizing(pdk).get("variables", []))
        block["symbols"][pdk] = {k: len(v) for k, v in cls.items()}
    cg = c.dir / "abstract" / "topology.cgraph.json"
    if cg.is_file():
        untied = par.untied_symmetries(par.load_graph(cg), doc)
        if untied:
            block["untied_symmetries"] = untied  # warnings, not gates
    return block


def build_catalog() -> dict[str, Any]:
    raw_index = (
        export.deck_index()
    )  # {circuit: {pdk: {testbench: relpath}}} — built from the same generator
    circuits: list[dict[str, Any]] = []
    by_class: dict[str, list[str]] = {}
    for c in load_all_circuits():
        m = c.manifest
        entry = {
            "id": c.id,
            "class": c.klass,
            "kind": c.kind,
            "display_name": m.get("display_name", ""),
            "compensation": m.get("compensation"),
            "stages": m.get("stages"),
            "pdks": c.pdks,
            "analyses": c.analyses,
            "status": c.status,
            "provenance": m.get("provenance", {}),
            "raw": raw_index.get(c.id, {}),
        }
        if c.references:
            entry["references"] = _reference_index(c)
        schematic = _schematic_refs(c)
        if schematic:
            entry["schematic"] = schematic
        if not c.is_reference_only:
            summary = scoreboard.baseline_summary(c)
            if summary:
                entry["scoreboard"] = summary
            params_block = _params_block(c)
            if params_block:
                entry["params"] = params_block
        circuits.append(entry)
        by_class.setdefault(c.klass, []).append(c.id)
    return {
        "schema": CATALOG_SCHEMA,
        "classes": {k: sorted(v) for k, v in sorted(by_class.items())},
        "circuits": sorted(circuits, key=lambda e: e["id"]),
    }


def catalog_json() -> str:
    return json.dumps(build_catalog(), indent=2, sort_keys=True) + "\n"
