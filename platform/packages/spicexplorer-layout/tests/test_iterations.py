"""Offline tests for the iteration audit trail (no gdsfactory; klayout-only parts skip)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from spicexplorer_layout.iterations import diff_png, iterations_table_md, snapshot

HAS_KLAYOUT = importlib.util.find_spec("klayout") is not None


def _write_gds(path: Path, boxes: list[tuple[int, int, int, int]], layer=(8, 0)) -> Path:
    import klayout.db as db

    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("top")
    li = ly.layer(*layer)
    for x0, y0, x1, y1 in boxes:
        top.shapes(li).insert(db.Box(x0, y0, x1, y1))
    ly.write(str(path))
    return path


def test_snapshot_and_table(tmp_path: Path):
    gen = tmp_path / "gen.py"
    gen.write_text("# generator\n")
    it = tmp_path / "iterations"
    e1 = snapshot(it, note="first", gen_path=gen, gds=None,
                  drc={"passed": False, "n_violations": 2,
                       "violations": [{"rule": "M1.a", "count": 2, "locations": [[1, 2], [3, 4]]}]})
    e2 = snapshot(it, note="fixed M1.a", gen_path=gen, gds=None,
                  drc={"passed": True, "n_violations": 0, "violations": []},
                  lvs={"passed": True, "matched": 5, "unmatched": 0},
                  pex={"ok": True, "mode": "CC", "n_c": 12, "n_r": 0}, area_um2=123.4)
    assert (e1.id, e2.id) == ("it01", "it02")
    assert (it / "it01" / "gen.py").is_file() and (it / "iterations.yaml").is_file()
    assert e1.drc_hits == {"M1.a": [[1.0, 2.0], [3.0, 4.0]]}
    md = iterations_table_md(it)
    assert "| it01 | first | 2 (M1.a ×2) |" in md
    assert "| it02 | fixed M1.a | **0** | match | CC 12C/0R | 123 |" in md


@pytest.mark.skipif(not HAS_KLAYOUT, reason="klayout wheel not installed")
def test_diff_png_marks_fixed_and_changed(tmp_path: Path):
    gen = tmp_path / "gen.py"
    gen.write_text("# generator\n")
    a = _write_gds(tmp_path / "a.gds", [(0, 0, 10000, 2000), (0, 5000, 10000, 7000)])
    b = _write_gds(tmp_path / "b.gds", [(0, 0, 10000, 2000), (0, 5000, 10000, 8000)])  # top bar taller
    it = tmp_path / "iterations"
    snapshot(it, note="a", gen_path=gen, gds=a, render=False,
             drc={"passed": False, "n_violations": 1,
                  "violations": [{"rule": "M1.a", "count": 1, "locations": [[5.0, 6.0]]}]})
    snapshot(it, note="b", gen_path=gen, gds=b, render=False,
             drc={"passed": True, "n_violations": 0, "violations": []})
    png = diff_png(it, "it01", "it02", size=(400, 300))
    assert png.is_file() and png.stat().st_size > 1000
    import yaml

    log = yaml.safe_load((it / "iterations.yaml").read_text())
    assert log["iterations"][1]["files"]["diff_from_it01"] == png.name


@pytest.mark.skipif(not HAS_KLAYOUT, reason="klayout wheel not installed")
def test_xor_boxes_local_vs_global(tmp_path: Path):
    from spicexplorer_layout.iterations import _xor_boxes

    a = _write_gds(tmp_path / "a.gds", [(0, 0, 10000, 2000), (0, 5000, 10000, 7000)])
    b = _write_gds(tmp_path / "b.gds", [(0, 0, 10000, 2000), (0, 5000, 10000, 8000)])
    boxes, frac = _xor_boxes(a, b)
    assert len(boxes) == 1 and boxes[0]["layers"] == ["8/0"]
    assert abs(boxes[0]["area"] - 10.0) < 0.01 and frac < 0.4
    c = _write_gds(tmp_path / "c.gds", [(3000, 0, 13000, 2000), (3000, 5000, 13000, 7000)])  # shifted
    _, frac2 = _xor_boxes(a, c)
    assert frac2 > 0.4


def test_note_headline_and_detail(tmp_path: Path):
    from spicexplorer_layout.iterations import NOTE_MAX, set_note

    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    it = tmp_path / "iterations"
    long = "x" * (NOTE_MAX + 20)
    with pytest.warns(UserWarning, match="headline"):
        snapshot(it, note=long, gen_path=gen, gds=None)
    set_note(it, "it01", "TM1.b x5 at seam: inset comb bars -> DRC 0")
    import yaml

    e = yaml.safe_load((it / "iterations.yaml").read_text())["iterations"][0]
    assert e["note"].startswith("TM1.b") and e["detail"] == long   # long form preserved
    snapshot(it, note="short", detail="the long reasoning", gen_path=gen, gds=None)
    e2 = yaml.safe_load((it / "iterations.yaml").read_text())["iterations"][1]
    assert e2["detail"] == "the long reasoning"
    assert "| it01 | TM1.b x5 at seam: inset comb bars -> DRC 0 |" in iterations_table_md(it)
