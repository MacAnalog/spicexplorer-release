"""Derived per-project rollup: state.json (workspace.state)."""
from __future__ import annotations

import json
from pathlib import Path

from spicexplorer_core.workspace import (
    build_state,
    envelope_fields,
    read_state,
    rebuild_state,
    write_manifest,
    write_run_record,
)


def _project(tmp_path: Path) -> Path:
    pdir = tmp_path / "projects" / "ota-0a1b2c3d"
    pdir.mkdir(parents=True)
    write_manifest(pdir, {"id": "ota-0a1b2c3d", "name": "My OTA", "default_pdk": "ihp-sg13g2"})
    return pdir


def _run(pdir: Path, run_id: str, *, kind="optimize", status="done",
         best_score=None, metrics=None, corner=None, started="2026-07-15T10:00:00"):
    rd = pdir / "runs" / run_id
    rd.mkdir(parents=True)
    rec = {"run_id": run_id, "status": status, "best_score": best_score,
           "metrics": metrics or {}, "started": started,
           **envelope_fields(kind, coordinates={"corner": corner} if corner else {})}
    write_run_record(rd, rec)
    return rd


def _verify_plan(pdir: Path, body: str):
    (pdir / "verify").mkdir(parents=True, exist_ok=True)
    (pdir / "verify" / "plan.yaml").write_text(body)


def test_compliance_matrix_from_runs_and_plan(tmp_path: Path):
    pdir = _project(tmp_path)
    _verify_plan(pdir, """
    specs:
      gain_db:
        measurement: dcgain
        corners: [tt, ss, ff]
        aggregate: min
        target: ">= 40"
    """)
    _run(pdir, "r_tt", metrics={"dcgain": 44.0}, corner="tt", best_score=-1.0)
    _run(pdir, "r_ss", metrics={"dcgain": 41.0}, corner="ss", best_score=-1.2)
    _run(pdir, "r_ff", metrics={"dcgain": 39.0}, corner="ff", best_score=-1.5)

    state = build_state(pdir)
    comp = state["compliance"]["gain_db"]
    assert comp["value"] == 39.0            # worst-case (min) across corners
    assert comp["pass"] is False            # 39 < 40
    assert comp["by_corner"] == {"tt": 44.0, "ss": 41.0, "ff": 39.0}
    assert comp["n_points"] == 3
    assert state["compliance_summary"] == {"specs": 1, "checked": 1, "passing": 0, "all_pass": False}


def test_best_run_election_rule_stated(tmp_path: Path):
    pdir = _project(tmp_path)
    _run(pdir, "worse", best_score=-2.0)
    _run(pdir, "better", best_score=-0.5)
    _run(pdir, "sim1", kind="simulate", best_score=-9.0)
    best = build_state(pdir)["best_runs"]
    assert best["overall"]["run_id"] == "better"   # max best_score among optimize runs
    assert "max best_score" in best["election_rule"]
    assert best["by_kind"]["simulate"] == "sim1"


def test_cell_inventory_and_maturity(tmp_path: Path):
    pdir = _project(tmp_path)
    cell = pdir / "design" / "cells" / "ota"
    (cell / "bindings").mkdir(parents=True)
    (cell / "netlist.spice").write_text("* net\n")
    (cell / "sizing.yaml").write_text("W: 10u\n")
    (cell / "bindings" / "ihp-sg13g2.yaml").write_text("{}\n")
    cells = build_state(pdir)["cells"]
    assert cells[0]["name"] == "ota"
    assert cells[0]["maturity"] == "sized"
    assert cells[0]["bindings"] == ["ihp-sg13g2"]


def test_running_runs_excluded_and_rebuild_is_idempotent(tmp_path: Path):
    pdir = _project(tmp_path)
    _run(pdir, "done", best_score=-1.0)
    _run(pdir, "live", status="running", best_score=-0.1)
    state = rebuild_state(pdir)
    assert state["run_count"] == 1                       # running excluded
    assert read_state(pdir)["best_runs"]["overall"]["run_id"] == "done"
    # persisted + rebuildable
    again = rebuild_state(pdir)
    assert again["run_count"] == 1


def test_no_plan_no_runs_is_empty_but_valid(tmp_path: Path):
    pdir = _project(tmp_path)
    state = build_state(pdir)
    assert state["compliance"] == {}
    assert state["best_runs"]["overall"] is None
    assert state["project"]["id"] == "ota-0a1b2c3d"
    assert json.dumps(state)  # fully JSON-serializable
