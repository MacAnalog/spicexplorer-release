"""Promotion protocol: history snapshots + atomic current pointer (workspace.promote)."""
from __future__ import annotations

from pathlib import Path

from spicexplorer_core.workspace import (
    current_promotion,
    list_promotions,
    promote,
)


def _cell(pdir: Path, name: str, *, sizing: str = "W: 10u\n", netlist: str = "* net\n"):
    c = pdir / "design" / "cells" / name
    c.mkdir(parents=True, exist_ok=True)
    (c / "netlist.spice").write_text(netlist)
    (c / "sizing.yaml").write_text(sizing)


def test_promote_snapshots_and_points_current(tmp_path: Path):
    _cell(tmp_path, "ota")
    rec = promote(tmp_path, label="first sizing")
    snap = tmp_path / "design" / "history" / rec["id"]
    assert (snap / "cells" / "ota" / "sizing.yaml").read_text() == "W: 10u\n"
    assert (snap / "cells" / "ota" / "netlist.spice").is_file()
    assert (snap / "promotion.json").is_file()
    cur = current_promotion(tmp_path)
    assert cur is not None and cur["id"] == rec["id"] and cur["label"] == "first sizing"


def test_history_is_immutable_and_current_advances(tmp_path: Path):
    _cell(tmp_path, "ota", sizing="W: 10u\n")
    first = promote(tmp_path, label="v1")
    _cell(tmp_path, "ota", sizing="W: 20u\n")     # edit the live design
    second = promote(tmp_path, label="v2")

    assert first["id"] != second["id"]
    # the first snapshot still holds the OLD sizing (immutable history)
    old = tmp_path / "design" / "history" / first["id"] / "cells" / "ota" / "sizing.yaml"
    assert old.read_text() == "W: 10u\n"
    # current points at the newest
    assert current_promotion(tmp_path)["id"] == second["id"]
    # newest-first listing
    ids = [p["id"] for p in list_promotions(tmp_path)]
    assert ids == [second["id"], first["id"]]


def test_promote_specific_cells_only(tmp_path: Path):
    _cell(tmp_path, "ota")
    _cell(tmp_path, "bias")
    rec = promote(tmp_path, cells=["ota"])
    snap = tmp_path / "design" / "history" / rec["id"] / "cells"
    assert (snap / "ota").is_dir()
    assert not (snap / "bias").exists()
    assert rec["cells"] == ["ota"]


def test_no_current_before_any_promotion(tmp_path: Path):
    _cell(tmp_path, "ota")
    assert current_promotion(tmp_path) is None
    assert list_promotions(tmp_path) == []


def test_payload_is_recorded(tmp_path: Path):
    _cell(tmp_path, "ota")
    rec = promote(tmp_path, payload={"from_run": "20260715-100000_optimize_abcd1234",
                                     "best_score": -0.4})
    assert current_promotion(tmp_path)["payload"]["best_score"] == -0.4
    assert rec["payload"]["from_run"].endswith("abcd1234")
