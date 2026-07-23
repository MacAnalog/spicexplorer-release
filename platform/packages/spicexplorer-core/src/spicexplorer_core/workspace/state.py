"""Derived per-project rollup — ``state.json``.

The rebuildable summary an agent reads instead of globbing a dozen racing files:

- the spec × corner **compliance matrix** (``verify/plan.yaml`` × run history),
- **best-run pointers** WITH the election rule stated (never an unexplained "best"),
- the **cell inventory** (netlist/sizing/annotations presence + maturity).

Same contract as ``index.db``: derived, never hand-edited, ``rebuild`` heals. Pure
FS derivation — it reads run records, it never runs a simulation.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from spicexplorer_core.atomic_io import atomic_write_json
from spicexplorer_core.workspace.manifest import read_manifest
from spicexplorer_core.workspace.verify import VerifyPlan, load_verify_plan

STATE_NAME = "state.json"
STATE_VERSION = 1
# best = the terminal run with the greatest best_score (higher is better — the
# optimizer maximizes), preferring kind 'optimize'. Stated in the output so a
# reader never has to guess what "best" meant.
ELECTION_RULE = "max best_score among terminal runs (kind 'optimize' preferred)"
_TERMINAL_EXCLUDE = {"", "running"}


def _terminal_runs(project_dir: Path) -> list[dict[str, Any]]:
    """Every terminal run's record (+ ``run_dir`` name), newest first."""
    base = project_dir / "runs"
    out: list[dict[str, Any]] = []
    if base.is_dir():
        for rd in base.iterdir():
            rj = rd / "run.json"
            if not rj.is_file():
                continue
            try:
                rec = json.loads(rj.read_text())
            except (OSError, ValueError):
                continue
            if isinstance(rec, dict) and rec.get("status") not in _TERMINAL_EXCLUDE:
                out.append({**rec, "run_dir": rd.name})
    out.sort(key=lambda r: str(r.get("started") or ""), reverse=True)
    return out


def _measured_for(spec_id: str, measurement: str, runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pull (value, corner, run) points for a spec from run metrics — matching the
    metric key on either the spec id or its measurement name."""
    pts: list[dict[str, Any]] = []
    for r in runs:
        metrics = r.get("metrics")
        if not isinstance(metrics, dict):
            continue
        for key in (spec_id, measurement):
            if key in metrics and isinstance(metrics[key], (int, float)):
                coords = r.get("coordinates") or {}
                pts.append({
                    "value": float(metrics[key]),
                    "corner": coords.get("corner"),
                    "run": r.get("run_id") or r.get("run_dir"),
                })
                break
    return pts


def _compliance(plan: VerifyPlan | None, runs: list[dict[str, Any]]) -> dict[str, Any]:
    if plan is None:
        return {}
    out: dict[str, Any] = {}
    for sid, spec in plan.specs.items():
        pts = _measured_for(sid, spec.measurement, runs)
        values = [p["value"] for p in pts]
        agg = spec.aggregate_value(values)
        out[sid] = {
            "measurement": spec.measurement,
            "aggregate": spec.aggregate,
            "target": spec.target.raw if spec.target else None,
            "value": agg,
            "pass": spec.passes(values),
            "n_points": len(values),
            "by_corner": {p["corner"]: p["value"] for p in pts if p["corner"]},
            "from_runs": sorted({str(p["run"]) for p in pts}),
        }
    return out


def _best_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    def _score(r: dict[str, Any]) -> float:
        s = r.get("best_score")
        return float(s) if isinstance(s, (int, float)) else float("-inf")

    scored = [r for r in runs if isinstance(r.get("best_score"), (int, float))]
    optimize = [r for r in scored if r.get("kind") == "optimize"]
    pool = optimize or scored
    if not pool:
        return {"election_rule": ELECTION_RULE, "overall": None, "by_kind": {}}
    best = max(pool, key=_score)
    by_kind: dict[str, Any] = {}
    for r in scored:
        k = str(r.get("kind") or "unknown")
        if k not in by_kind or _score(r) > _score(by_kind[k]):
            by_kind[k] = r
    return {
        "election_rule": ELECTION_RULE,
        "overall": {"run_id": best.get("run_id") or best.get("run_dir"),
                    "best_score": best.get("best_score"), "kind": best.get("kind")},
        "by_kind": {k: (v.get("run_id") or v.get("run_dir")) for k, v in by_kind.items()},
    }


def _cells(project_dir: Path) -> list[dict[str, Any]]:
    base = project_dir / "design" / "cells"
    cells: list[dict[str, Any]] = []
    if base.is_dir():
        for cell in sorted(p for p in base.iterdir() if p.is_dir()):
            has_netlist = (cell / "netlist.spice").is_file()
            has_sizing = (cell / "sizing.yaml").is_file()
            has_annotations = (cell / "annotations.yaml").is_file()
            bindings = sorted(p.stem for p in (cell / "bindings").glob("*.yaml")) \
                if (cell / "bindings").is_dir() else []
            # maturity: netlist(master) → sized → verified-ish by presence of curated data
            maturity = "empty"
            if has_netlist:
                maturity = "sized" if has_sizing else "netlist"
            cells.append({
                "name": cell.name, "netlist": has_netlist, "sizing": has_sizing,
                "annotations": has_annotations, "bindings": bindings, "maturity": maturity,
            })
    return cells


def build_state(project_dir: Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Derive the whole ``state.json`` for a project (does not write it)."""
    manifest = read_manifest(project_dir)
    plan = load_verify_plan(project_dir)
    runs = _terminal_runs(project_dir)
    compliance = _compliance(plan, runs)
    passing = [s for s in compliance.values() if s["pass"] is True]
    checked = [s for s in compliance.values() if s["pass"] is not None]
    return {
        "state_version": STATE_VERSION,
        "generated_at": (now or datetime.now()).isoformat(timespec="seconds"),
        "project": {
            "id": manifest.get("id") or project_dir.name,
            "name": manifest.get("name"),
            "pdk": manifest.get("default_pdk"),
        },
        "compliance": compliance,
        "compliance_summary": {
            "specs": len(compliance), "checked": len(checked),
            "passing": len(passing),
            "all_pass": bool(checked) and len(passing) == len(checked),
        },
        "best_runs": _best_runs(runs),
        "cells": _cells(project_dir),
        "run_count": len(runs),
    }


def write_state(project_dir: Path, state: dict[str, Any]) -> None:
    atomic_write_json(project_dir / STATE_NAME, state, indent=2)


def read_state(project_dir: Path) -> dict[str, Any]:
    """Tolerant read: missing/torn → ``{}`` (rebuild heals)."""
    try:
        data = json.loads((project_dir / STATE_NAME).read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def rebuild_state(project_dir: Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Derive + persist ``state.json`` (the self-healing entry point)."""
    state = build_state(project_dir, now=now)
    write_state(project_dir, state)
    return state
