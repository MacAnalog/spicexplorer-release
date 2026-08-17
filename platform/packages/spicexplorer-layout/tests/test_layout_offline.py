"""Offline tests — no gdsfactory needed (a stub generator stands in for a Component)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from spicexplorer_layout import (
    GdsBuilder,
    build_gds,
    common_centroid_order,
    interdigitate_order,
    load_generator,
    params_from_json,
    params_schema,
)
from spicexplorer_layout.patterns import with_dummies

STUB = textwrap.dedent("""
    import dataclasses
    CELL = "stub_cell"
    BOUNDS = {"gap": (0.5, 2.0)}

    @dataclasses.dataclass(frozen=True)
    class LayoutParams:
        gap: float = 1.0
        n_dummy: int = 1

    class _Comp:
        def __init__(self, name, w, h, sizing):
            self.name, self.w, self.h, self.sizing = name, w, h, sizing
        def bbox(self):
            class B: pass
            b = B(); b.left, b.bottom, b.right, b.top = 0.0, 0.0, self.w, self.h
            return b
        def write_gds(self, path, **kw):
            with open(path, "wb") as f:
                f.write(f"{self.name}:{self.w}:{self.h}:{self.sizing}".encode())

    def build(params, sizing=None):
        return _Comp(CELL, 10 + params.gap, 5.0 + params.n_dummy, sizing)
""")


@pytest.fixture
def gen_path(tmp_path: Path) -> Path:
    p = tmp_path / "gen_stub.py"
    p.write_text(STUB)
    return p


def test_load_and_schema(gen_path):
    g = load_generator(gen_path)
    assert g.name == "stub_cell" and g.bounds == {"gap": (0.5, 2.0)}
    sch = {r["name"]: r for r in params_schema(g)}
    assert sch["gap"]["default"] == 1.0 and sch["gap"]["lo"] == 0.5 and sch["n_dummy"]["lo"] is None


def test_params_from_json_rejects_unknown(gen_path):
    g = load_generator(gen_path)
    assert params_from_json(g, '{"gap": 1.5}').gap == 1.5
    with pytest.raises(KeyError):
        params_from_json(g, {"nope": 1})


def test_build_gds_reports_area_and_sha(gen_path, tmp_path):
    g = load_generator(gen_path)
    r = build_gds(g, g.default_params(), tmp_path / "o" / "x.gds", sizing={"w": 4})
    assert r.area_um2 == pytest.approx(11.0 * 6.0) and Path(r.gds).is_file()
    r2 = build_gds(g, g.default_params(), tmp_path / "o" / "y.gds", sizing={"w": 4})
    assert r.sha256 == r2.sha256  # deterministic
    r3 = build_gds(g, g.params_cls(gap=1.5), tmp_path / "o" / "z.gds")
    assert r3.sha256 != r.sha256 and r3.params == {"gap": 1.5, "n_dummy": 1}


def test_gdsbuilder_inproc(gen_path, tmp_path):
    b = GdsBuilder(gen_path, tmp_path / "b", cell="stub_cell", inproc=True)
    out = b({"gap": 0.75})
    assert out.name == "stub_cell.gds" and out.is_file()
    assert b.last is not None and b.last.params["gap"] == 0.75


def test_gdsbuilder_subprocess(gen_path, tmp_path):
    b = GdsBuilder(gen_path, tmp_path / "s", cell="stub_cell")
    out = b({"gap": 0.75})
    assert out.is_file() and b.last is not None
    assert b.last.area_um2 == pytest.approx(10.75 * 6.0)


def test_interdigitate_orders():
    assert interdigitate_order("AB", 2, style="ABAB") == list("ABAB")
    assert interdigitate_order("AB", 4, style="ABBA") == list("ABBAABBA")
    with pytest.raises(ValueError):
        interdigitate_order("AB", 3, style="ABBA")


def test_common_centroid_and_dummies():
    assert common_centroid_order() == [["A", "B"], ["B", "A"]]
    g = common_centroid_order(rows=2, cols=4, n_each=4)
    assert g == [["A", "B", "B", "A"], ["B", "A", "A", "B"]]
    with pytest.raises(ValueError):
        common_centroid_order(rows=1, cols=4, n_each=3)
    assert with_dummies("AB", 2) == list("DDABDD")


# ---- layout-review DSL -------------------------------------------------------------------


def _review_dict():
    return {
        "schema": "layout-review/1",
        "cell": "c",
        "gds": "c.gds",
        "verdict": "PASS",
        "findings": [
            {
                "id": "F1",
                "severity": "major",
                "category": "matching",
                "title": "t",
                "where": [{"kind": "box", "x0": 0, "y0": 0, "x1": 1, "y1": 1}],
            },
            {
                "id": "F2",
                "severity": "note",
                "category": "well",
                "title": "u",
                "where": [{"kind": "pair", "a": {"x": 0, "y": 0}, "b": {"x": 2, "y": 2}}],
            },
        ],
    }


def test_review_validate_and_roundtrip(tmp_path):
    from spicexplorer_layout.review import Finding, Review, dump_review, load_review, validate

    assert validate(_review_dict()) == []
    bad = _review_dict()
    bad["findings"][0]["severity"] = "huge"
    bad["findings"][1]["id"] = "F1"
    errs = validate(bad)
    assert any("severity" in e for e in errs) and any("duplicate id" in e for e in errs)
    r = Review(
        cell="c",
        gds="c.gds",
        verdict="FAIL",
        findings=[
            Finding(
                "F1",
                "blocker",
                "drc",
                "x",
                where=[{"kind": "rule", "name": "M1.a", "locations": [[1, 2]]}],
            )
        ],
    )
    for ext in ("json", "yaml"):
        p = dump_review(r, tmp_path / f"r.{ext}")
        r2 = load_review(p)
        assert r2.verdict == "FAIL" and r2.findings[0].where[0]["name"] == "M1.a"


def test_anchor_bbox():
    from spicexplorer_layout.review import Finding, anchor_bbox

    f = Finding(
        "F1",
        "minor",
        "routing",
        "t",
        where=[{"kind": "point", "x": 1, "y": 2}, {"kind": "line", "points": [[0, 0], [3, 1]]}],
    )
    assert anchor_bbox(f) == (0, 0, 3, 2)
    assert (
        anchor_bbox(Finding("F2", "note", "other", "n", where=[{"kind": "net", "name": "a"}]))
        is None
    )


def test_annotate_renders_png(tmp_path):
    """Needs the klayout module + Pillow (both workspace deps); no PDK required (lyp optional)."""
    pytest.importorskip("klayout.lay")
    pytest.importorskip("PIL")
    import klayout.db as db
    from spicexplorer_layout.review import Finding, Review, annotate, annotate_crops

    ly = db.Layout()
    top = ly.create_cell("c")
    l1 = ly.layer(8, 0)
    top.shapes(l1).insert(db.DBox(0, 0, 10, 4))
    top.shapes(l1).insert(db.DBox(0, 6, 10, 10))
    gds = tmp_path / "c.gds"
    ly.write(str(gds))
    r = Review(
        cell="c",
        gds=str(gds),
        verdict="PASS with majors",
        axis={"x": 5.0},
        findings=[
            Finding(
                "F1",
                "major",
                "symmetry",
                "gap",
                where=[{"kind": "box", "x0": 0, "y0": 4, "x1": 10, "y1": 6}],
            ),
            Finding("F2", "note", "other", "legend only", where=[{"kind": "net", "name": "vdd"}]),
        ],
    )
    png = annotate(gds, r, tmp_path / "r.png", size=(400, 300), lyp=None)
    assert png.is_file() and png.stat().st_size > 1000
    crops = annotate_crops(gds, r, tmp_path / "crops", size=(200, 150), lyp=None)
    assert [p.name for p in crops] == ["F1.png"]
