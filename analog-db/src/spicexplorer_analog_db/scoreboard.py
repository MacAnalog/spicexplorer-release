"""The PPA scoreboard — recorded design points per (circuit, pdk).

Storage (per-circuit, self-contained — the global views are GENERATED, see ``scoreboard_index``):

  circuits/<id>/scoreboard/baselines.yaml         AUTHORED {pdk: design_id} — the named baseline
  circuits/<id>/scoreboard/<pdk>/<design_id>.json RECORDED one entry per design point

An entry is keyed by :func:`design_id` — sha256 over the canonical (circuit, pdk, sizing vector)
— so re-running the SAME design at another corner **upserts** that corner into the same entry,
and a hash hit doubles as a sim memo-cache for automation. Entries are timestamped recorded
artifacts (like the old ``results/`` files, which this module absorbed): they are NOT
byte-drift-guarded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from . import paths, ppa
from .model import Circuit, load_all_circuits

ENTRY_SCHEMA = "spicexplorer/scoreboard-entry@1"
INDEX_SCHEMA = "spicexplorer/scoreboard@1"


# --------------------------------------------------------------------------- identity / paths


def current_parameters(circuit: Circuit, pdk: str) -> dict[str, Any]:
    """The parameters in force right now: the sizing defaults (the *design*) + any per-PDK
    ``analysis_params`` (testbench conditions — recorded, but excluded from the identity hash)."""
    sizing_doc = circuit.sizing(pdk)
    sizing = {str(v["name"]): v.get("default") for v in sizing_doc.get("variables", [])}
    out: dict[str, Any] = {"sizing": sizing}
    extra = sizing_doc.get("analysis_params") or {}
    if extra:
        out["analysis_params"] = {str(k): v for k, v in extra.items()}
    return out


def design_id(circuit_id: str, pdk: str, sizing: dict[str, Any]) -> str:
    """First 10 hex of sha256 over the canonical (circuit, pdk, sizing vector) — D-6.

    Values are normalized numerically where possible (``0.5u`` ≡ ``5e-07``) so identity is
    formatting-proof; genuinely different numbers (even a rounding pass) are different designs."""
    norm = {
        k: repr(n) if (n := ppa.parse_eng(str(v))) is not None else str(v)
        for k, v in sizing.items()
    }
    canonical = json.dumps({"circuit": circuit_id, "pdk": pdk, "sizing": norm}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:10]


def scoreboard_dir(circuit: Circuit) -> Path:
    return circuit.dir / "scoreboard"


def entry_path(circuit: Circuit, pdk: str, did: str) -> Path:
    return scoreboard_dir(circuit) / pdk / f"{did}.json"


# --------------------------------------------------------------------------- read


def load_entries(circuit: Circuit, pdk: str | None = None) -> list[dict[str, Any]]:
    """Every recorded entry for the circuit (optionally one PDK), sorted by (pdk, design_id)."""
    root = scoreboard_dir(circuit)
    dirs = [root / pdk] if pdk else sorted(p for p in root.glob("*") if p.is_dir())
    out: list[dict[str, Any]] = []
    for d in dirs:
        for f in sorted(d.glob("*.json")):
            out.append(json.loads(f.read_text()))
    return out


def baselines(circuit: Circuit) -> dict[str, str]:
    """The authored ``{pdk: design_id}`` baseline pointers (empty if none named yet)."""
    f = scoreboard_dir(circuit) / "baselines.yaml"
    if not f.is_file():
        return {}
    doc = yaml.safe_load(f.read_text()) or {}
    return {str(k): str(v) for k, v in (doc.get("baselines") or {}).items()}


def set_baseline(circuit: Circuit, pdk: str, did: str) -> Path:
    """Name ``did`` the baseline for (circuit, pdk); the entry must exist."""
    if not entry_path(circuit, pdk, did).is_file():
        raise FileNotFoundError(f"{circuit.id}: no scoreboard entry {pdk}/{did}.json")
    current = baselines(circuit)
    current[pdk] = did
    f = scoreboard_dir(circuit) / "baselines.yaml"
    f.parent.mkdir(exist_ok=True)
    f.write_text(
        "# AUTHORED baseline pointers (plan_scoreboard D-8): the named design point per PDK.\n"
        "# Maintained via `analog-db scoreboard set-baseline` (or auto-named on first record).\n"
        + yaml.safe_dump({"baselines": dict(sorted(current.items()))}, sort_keys=False)
    )
    return f


# --------------------------------------------------------------------------- write / upsert


def record(
    circuit: Circuit, results: dict[str, Any], sizing_override: dict[str, Any] | None = None
) -> Path:
    """Record one ``run_circuit`` results document as/into a scoreboard entry (upsert by corner).

    The entry for the current design point (hash of today's sizing defaults — or of
    ``sizing_override``, for recording a foreign point such as an optimizer candidate) gains or
    replaces the results' corner block; metrics + PPA rollup are recomputed over every recorded
    corner. The first recorded design point for a (circuit, pdk) is auto-named its baseline."""
    pdk, corner = str(results["pdk"]), str(results["corner"])
    if sizing_override is not None:
        params: dict[str, Any] = {"sizing": {str(k): v for k, v in sizing_override.items()}}
    else:
        params = current_parameters(circuit, pdk)
    did = design_id(circuit.id, pdk, params["sizing"])
    path = entry_path(circuit, pdk, did)

    entry: dict[str, Any]
    if path.is_file():
        entry = json.loads(path.read_text())
    else:
        entry = {
            "schema": ENTRY_SCHEMA,
            "circuit": circuit.id,
            "pdk": pdk,
            "design_id": did,
            "parameters": params,
            "corners": {},
            "metrics": {},
        }
    corner_block: dict[str, Any] = {
        "analyses": results["analyses"],
        "provenance": results.get("provenance", {}),
    }
    if results.get("symbolic_crosscheck"):
        corner_block["symbolic_crosscheck"] = results["symbolic_crosscheck"]
    entry["corners"][corner] = corner_block
    entry["area"] = ppa.area_report(circuit, pdk)
    entry["metrics"] = {
        c: ppa.metric_values(circuit, block["analyses"]) for c, block in entry["corners"].items()
    }
    entry["ppa"] = ppa.ppa_rollup(circuit, entry["metrics"], entry["area"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n")

    if pdk not in baselines(circuit):
        set_baseline(circuit, pdk, did)
    return path


# --------------------------------------------------------------------------- Pareto + index


def _axes(class_id: str) -> list[tuple[str, str]]:
    """The Pareto axes for a class: power (min) + active area (min) + the declared directed
    performance metrics. Axis names address the entry's ``ppa`` block."""
    axes = [("power_w", "min"), ("active_gate_area_um2", "min")]
    for perf in ppa.class_ppa(class_id).get("performance") or []:
        axes.append((f"performance.{perf['metric']}", perf["better"]))
    return axes


def _axis_value(entry: dict[str, Any], axis: str) -> float | None:
    block = entry.get("ppa") or {}
    if axis.startswith("performance."):
        val = (block.get("performance") or {}).get(axis.split(".", 1)[1])
    else:
        val = block.get(axis)
    return float(val) if isinstance(val, (int, float)) else None


def _dominates(a: dict[str, Any], b: dict[str, Any], axes: list[tuple[str, str]]) -> bool:
    """True iff ``a`` is at least as good as ``b`` on every axis and better on one. A missing
    value counts as worst, so an unmeasured entry never dominates a measured one."""
    at_least_one_better = False
    for axis, better in axes:
        va, vb = _axis_value(a, axis), _axis_value(b, axis)
        ga = float("-inf") if va is None else (va if better == "max" else -va)
        gb = float("-inf") if vb is None else (vb if better == "max" else -vb)
        if ga < gb:
            return False
        if ga > gb:
            at_least_one_better = True
    return at_least_one_better


def pareto_front(entries: list[dict[str, Any]], class_id: str) -> set[str]:
    """The non-dominated design_ids among ``entries`` (one circuit × pdk) — never a scalar rank."""
    axes = _axes(class_id)
    return {
        e["design_id"]
        for e in entries
        if not any(_dominates(other, e, axes) for other in entries if other is not e)
    }


def _spec_counts(entry: dict[str, Any]) -> dict[str, int]:
    counts = {"pass": 0, "fail": 0, "none": 0}
    for corner_metrics in (entry.get("metrics") or {}).values():
        for m in corner_metrics.values():
            counts[m.get("spec", "none")] += 1
    return counts


def baseline_summary(circuit: Circuit) -> dict[str, Any]:
    """``{pdk: {design_id, ppa, spec}}`` for the circuit's baselines — the catalog hook."""
    out: dict[str, Any] = {}
    for pdk, did in baselines(circuit).items():
        p = entry_path(circuit, pdk, did)
        if not p.is_file():
            continue
        entry = json.loads(p.read_text())
        out[pdk] = {"design_id": did, "ppa": entry.get("ppa", {}), "spec": _spec_counts(entry)}
    return out


def index_path() -> Path:
    return paths.db_root() / "scoreboard.json"


def build_index() -> dict[str, Any]:
    """The generated global scoreboard: the owner's
    ``<class>/<pdk>/<circuit>/<design-point>`` view, derived deterministically from the
    per-circuit entries + baselines. Drift-guarded like catalog.json (Tier 0)."""
    classes: dict[str, Any] = {}
    for c in load_all_circuits():
        if c.is_reference_only:
            continue
        base = baselines(c)
        for pdk in sorted({e["pdk"] for e in load_entries(c)}):
            entries = load_entries(c, pdk)
            front = pareto_front(entries, c.klass)
            rows = [
                {
                    "design_id": e["design_id"],
                    "baseline": e["design_id"] == base.get(pdk),
                    "pareto": e["design_id"] in front,
                    "ppa": e.get("ppa", {}),
                    "spec": _spec_counts(e),
                }
                for e in entries
            ]
            classes.setdefault(c.klass, {}).setdefault(pdk, {})[c.id] = {
                "baseline": base.get(pdk),
                "entries": rows,
            }
    return {"schema": INDEX_SCHEMA, "classes": classes}


def index_json() -> str:
    return json.dumps(build_index(), indent=2, sort_keys=True) + "\n"
