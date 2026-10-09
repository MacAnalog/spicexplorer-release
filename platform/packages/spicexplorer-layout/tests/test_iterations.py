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
    e1 = snapshot(
        it,
        note="first",
        gen_path=gen,
        gds=None,
        drc={
            "passed": False,
            "n_violations": 2,
            "violations": [{"rule": "M1.a", "count": 2, "locations": [[1, 2], [3, 4]]}],
        },
    )
    e2 = snapshot(
        it,
        note="fixed M1.a",
        gen_path=gen,
        gds=None,
        drc={"passed": True, "n_violations": 0, "violations": []},
        lvs={"passed": True, "matched": 5, "unmatched": 0},
        pex={"ok": True, "mode": "CC", "n_c": 12, "n_r": 0},
        area_um2=123.4,
    )
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
    b = _write_gds(
        tmp_path / "b.gds", [(0, 0, 10000, 2000), (0, 5000, 10000, 8000)]
    )  # top bar taller
    it = tmp_path / "iterations"
    snapshot(
        it,
        note="a",
        gen_path=gen,
        gds=a,
        render=False,
        drc={
            "passed": False,
            "n_violations": 1,
            "violations": [{"rule": "M1.a", "count": 1, "locations": [[5.0, 6.0]]}],
        },
    )
    snapshot(
        it,
        note="b",
        gen_path=gen,
        gds=b,
        render=False,
        drc={"passed": True, "n_violations": 0, "violations": []},
    )
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
    c = _write_gds(
        tmp_path / "c.gds", [(3000, 0, 13000, 2000), (3000, 5000, 13000, 7000)]
    )  # shifted
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
    assert e["note"].startswith("TM1.b") and e["detail"] == long  # long form preserved
    snapshot(it, note="short", detail="the long reasoning", gen_path=gen, gds=None)
    e2 = yaml.safe_load((it / "iterations.yaml").read_text())["iterations"][1]
    assert e2["detail"] == "the long reasoning"
    assert "| it01 | TM1.b x5 at seam: inset comb bars -> DRC 0 |" in iterations_table_md(it)


# ----------------------------------------------------------------------
# LAY-D4 — the audit trail keeps WHY a stage failed, and a crash is not a mismatch
# ----------------------------------------------------------------------
# snapshot() stored only passed/n/rules, passed/matched/unmatched/netlist_sha and ok/mode/n_c/n_r,
# so the runners' `reason` (and PEX's `mesh_connected`) never reached iterations.yaml, and the
# table rendered a crashed LVS runner as "MISMATCH" and a crashed DRC runner as "0 ()". The dicts
# below have the shape of the signoff verdicts' to_dict() (this leaf package may not import them).

_LVS_CRASH = {
    "passed": False,
    "available": True,
    "matched": False,
    "unmatched": {},
    "netlist_sha": "abc",
    "log": "…",
    "reason": "LVS runner exited 1 and wrote no c.log: "
    "Traceback …\nModuleNotFoundError: No module named 'docopt'",
}
_DRC_CRASH = {
    "passed": False,
    "available": True,
    "n_violations": 0,
    "violations": [],
    "log": "…",
    "reason": "DRC runner exited 1 without a 'DRC Check Passed' verdict and without "
    "violations from a report written by this run: deck error",
}
_PEX_OPEN = {
    "ok": False,
    "available": True,
    "mode": "RC",
    "n_c": 10,
    "n_r": 40,
    "log": "…",
    "mesh_connected": False,
    "reason": "the RC mesh touches no device pin",
}


def test_snapshot_keeps_reason_available_and_mesh_connected(tmp_path: Path):
    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    e = snapshot(
        tmp_path / "iterations",
        note="crash",
        gen_path=gen,
        gds=None,
        drc=_DRC_CRASH,
        lvs=_LVS_CRASH,
        pex=_PEX_OPEN,
    )
    assert e.lvs["available"] is True and e.lvs["reason"].endswith("No module named 'docopt'")
    assert e.drc["available"] is True and e.drc["reason"].endswith("deck error")
    assert e.pex["mesh_connected"] is False and e.pex["reason"] == _PEX_OPEN["reason"]
    import yaml

    stored = yaml.safe_load((tmp_path / "iterations" / "iterations.yaml").read_text())[
        "iterations"
    ][0]
    assert stored["lvs"]["reason"] == e.lvs["reason"] and stored["pex"]["mesh_connected"] is False
    assert "log" not in stored["lvs"]  # the raw log stays out of the trail


def test_snapshot_reason_is_a_bounded_tail(tmp_path: Path):
    from spicexplorer_layout.iterations import REASON_MAX

    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    long = "x" * 5000 + " ModuleNotFoundError: docopt"
    e = snapshot(
        tmp_path / "iterations",
        note="crash",
        gen_path=gen,
        gds=None,
        lvs={**_LVS_CRASH, "reason": long},
    )
    assert len(e.lvs["reason"]) == REASON_MAX and e.lvs["reason"].endswith("docopt")


def test_table_shows_a_crashed_runner_as_error_not_mismatch(tmp_path: Path):
    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    it = tmp_path / "iterations"
    snapshot(
        it, note="crash", gen_path=gen, gds=None, drc=_DRC_CRASH, lvs=_LVS_CRASH, pex=_PEX_OPEN
    )
    # a real mismatch keeps its word, with or without a dirty exit on top
    snapshot(
        it,
        note="mismatch",
        gen_path=gen,
        gds=None,
        lvs={"passed": False, "available": True, "matched": False, "unmatched": {"nets": 2}},
    )
    snapshot(
        it,
        note="mismatch+exit",
        gen_path=gen,
        gds=None,
        lvs={
            "passed": False,
            "available": True,
            "matched": False,
            "unmatched": {"nets": 2},
            "reason": "LVS runner exited 3 and failed: …",
        },
    )
    md = iterations_table_md(it)
    assert "| it01 | crash | ERROR | ERROR | fail |" in md
    assert "| it02 | mismatch | — | MISMATCH |" in md
    assert "| it03 | mismatch+exit | — | MISMATCH |" in md


def test_table_reads_old_logs_without_reason(tmp_path: Path):
    """iterations.yaml written before the reason was kept renders as it always did."""
    import yaml

    it = tmp_path / "iterations"
    it.mkdir()
    (it / "iterations.yaml").write_text(
        yaml.safe_dump(
            {
                "iterations": [
                    {
                        "id": "it01",
                        "note": "old",
                        "drc": {"passed": False, "n": 0, "rules": {}},
                        "lvs": {
                            "passed": False,
                            "matched": False,
                            "unmatched": {},
                            "netlist_sha": None,
                        },
                        "pex": {},
                        "files": {},
                    }
                ]
            }
        )
    )
    assert "| it01 | old | 0 () | MISMATCH | — |" in iterations_table_md(it)


@pytest.mark.skipif(not HAS_KLAYOUT, reason="klayout wheel not installed")
def test_diff_png_status_shows_a_crashed_runner_as_error(tmp_path: Path, monkeypatch):
    """diff_png's picture title is the second place a verdict is rendered: same rule."""
    from PIL import Image
    from spicexplorer_layout import iterations

    seen: list[str] = []

    def fake_annotate(gds, rv, out_png, **kw):
        seen.append(rv.verdict)
        Image.new("RGB", (40, 30), (255, 255, 255)).save(out_png)
        return Path(out_png)

    monkeypatch.setattr(iterations, "annotate", fake_annotate)
    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    a = _write_gds(tmp_path / "a.gds", [(0, 0, 10000, 2000)])
    it = tmp_path / "iterations"
    snapshot(it, note="a", gen_path=gen, gds=a, render=False, drc=_DRC_CRASH, lvs=_LVS_CRASH)
    snapshot(
        it,
        note="b",
        gen_path=gen,
        gds=a,
        render=False,
        lvs={"passed": False, "available": True, "matched": False, "unmatched": {"nets": 1}},
    )
    diff_png(it, "it01", "it02", size=(40, 30))
    assert seen[0] == "DRC ERROR · LVS ERROR"
    assert seen[1] == "LVS MISMATCH"


def test_snapshot_without_a_reason_stores_empty_not_none(tmp_path: Path):
    """A failed stage whose runner gave no reason (key absent, or ``reason: None``) keeps "" — not
    the string 'None', which the table would then read as a crash."""
    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    it = tmp_path / "iterations"
    e = snapshot(
        it,
        note="no reason",
        gen_path=gen,
        gds=None,
        drc={"passed": False, "available": True, "n_violations": 0, "violations": []},
        lvs={"passed": False, "available": True, "matched": False, "unmatched": {}, "reason": None},
        pex={"ok": False, "available": True, "mode": "RC"},
    )
    assert (e.drc["reason"], e.lvs["reason"], e.pex["reason"]) == ("", "", "")
    assert "| it01 | no reason | 0 () | MISMATCH | fail |" in iterations_table_md(it)


def test_snapshot_records_an_unavailable_runner(tmp_path: Path):
    """A runner that is not there (``available: False``, the verdicts' 'tool/deck missing') keeps
    that flag and its reason for all three stages, and the table calls it ERROR."""
    import yaml

    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    it = tmp_path / "iterations"
    off = {"passed": False, "available": False, "reason": "klayout not installed"}
    e = snapshot(
        it,
        note="no tools",
        gen_path=gen,
        gds=None,
        drc=off,
        lvs=off,
        pex={"ok": False, "available": False, "reason": "kpex not installed"},
    )
    assert (e.drc["available"], e.lvs["available"], e.pex["available"]) == (False, False, False)
    stored = yaml.safe_load((it / "iterations.yaml").read_text())["iterations"][0]
    assert stored["pex"] == {**stored["pex"], "available": False, "reason": "kpex not installed"}
    assert stored["drc"]["reason"] == stored["lvs"]["reason"] == "klayout not installed"
    assert "| it01 | no tools | ERROR | ERROR | fail |" in iterations_table_md(it)


# A DRC stage "found something" when it has per-rule counts OR a count: the signoff verdict always
# carries both, but snapshot() also takes hand-built dicts that may carry only one of them. Either
# means the runner reached a verdict, so a reason on top (a dirty exit after the report) must not
# turn real violations into ERROR.
_DRC_COUNT_ONLY = {
    "passed": False,
    "available": True,
    "n_violations": 3,
    "violations": [],
    "reason": "runner exited 1 after writing the report",
}
_DRC_RULES_ONLY = {
    "passed": False,
    "available": True,
    "violations": [{"rule": "M1.a", "count": 2}],
    "reason": "runner exited 1 after writing the report",
}


@pytest.mark.parametrize("drc,cell", [(_DRC_COUNT_ONLY, "| 3 () |"), (_DRC_RULES_ONLY, "M1.a ×2")])
def test_table_a_drc_stage_that_found_hits_is_never_error(tmp_path: Path, drc, cell):
    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    it = tmp_path / "iterations"
    snapshot(it, note="hits", gen_path=gen, gds=None, drc=drc)
    row = next(ln for ln in iterations_table_md(it).splitlines() if ln.startswith("| it01 |"))
    assert cell in row and "ERROR" not in row, row


@pytest.mark.skipif(not HAS_KLAYOUT, reason="klayout wheel not installed")
def test_diff_png_status_keeps_found_hits_and_mismatches(tmp_path: Path, monkeypatch):
    """The picture title follows the table: a mismatch after a dirty exit stays MISMATCH, and a DRC
    stage with a count or per-rule hits (plus a reason) shows the count, not ERROR."""
    from PIL import Image
    from spicexplorer_layout import iterations

    seen: list[str] = []

    def fake_annotate(gds, rv, out_png, **kw):
        seen.append(rv.verdict)
        Image.new("RGB", (40, 30), (255, 255, 255)).save(out_png)
        return Path(out_png)

    monkeypatch.setattr(iterations, "annotate", fake_annotate)
    gen = tmp_path / "gen.py"
    gen.write_text("# g\n")
    a = _write_gds(tmp_path / "a.gds", [(0, 0, 10000, 2000)])
    it = tmp_path / "iterations"
    snapshot(
        it,
        note="a",
        gen_path=gen,
        gds=a,
        render=False,
        lvs={
            "passed": False,
            "available": True,
            "matched": False,
            "unmatched": {"nets": 2},
            "reason": "LVS runner exited 3 and failed: …",
        },
    )
    snapshot(it, note="b", gen_path=gen, gds=a, render=False, drc=_DRC_COUNT_ONLY)
    snapshot(it, note="c", gen_path=gen, gds=a, render=False, drc=_DRC_RULES_ONLY)
    diff_png(it, "it01", "it02", size=(40, 30))
    diff_png(it, "it03", "it01", size=(40, 30))
    assert seen[0] == "LVS MISMATCH"
    assert seen[1] == "DRC 3"
    assert seen[2].startswith("DRC ") and "ERROR" not in seen[2], seen[2]
