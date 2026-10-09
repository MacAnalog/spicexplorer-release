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


# ----------------------------------------------------------------------
# LAY-D5 — validate() checks the values, not only that the keys are there
# ----------------------------------------------------------------------
# It accepted any top-level verdict, any finding verdict and string/None anchor coordinates —
# which then crashed anchor_bbox/annotate with a TypeError far from the file that caused it —
# and had no category for the current-density audit the reviewer is required to run.


def _one_anchor(anchor: dict) -> dict:
    d = _review_dict()
    d["findings"][0]["where"] = [anchor]
    return d


def test_review_top_level_verdict_is_an_enum():
    from spicexplorer_layout.review import validate

    for v in ("PASS", "PASS with majors", "FAIL"):
        assert validate({**_review_dict(), "verdict": v}) == []
    errs = validate({**_review_dict(), "verdict": "bogus"})
    assert len(errs) == 1 and errs[0].startswith("verdict must be one of"), errs
    errs = validate({k: v for k, v in _review_dict().items() if k != "verdict"})
    assert errs == ["missing top-level key 'verdict'"]  # one error for one absence


def test_review_finding_verdict_is_an_enum_and_optional():
    from spicexplorer_layout.review import validate

    d = _review_dict()
    assert "verdict" not in d["findings"][0] and validate(d) == []  # first reviews omit it
    for v in ("open", "fixed", "worse"):
        d["findings"][0]["verdict"] = v
        assert validate(d) == []
    d["findings"][0]["verdict"] = "maybe"
    errs = validate(d)
    assert len(errs) == 1 and errs[0].startswith("findings[0]: verdict must be one of"), errs


def test_review_vocabulary_already_in_use_stays_valid():
    """Reviews of record use 'PASS with notes' and re-review marks 'new' / 'deferred'."""
    from spicexplorer_layout.review import validate

    d = {**_review_dict(), "verdict": "PASS with notes"}
    d["findings"][0]["verdict"] = "new"
    d["findings"][1]["verdict"] = "deferred"
    assert validate(d) == []


def test_review_accepts_a_current_density_category():
    from spicexplorer_layout.review import validate

    d = _review_dict()
    d["findings"][0]["category"] = "current_density"
    assert validate(d) == []


@pytest.mark.parametrize(
    "anchor,bad",
    [
        ({"kind": "box", "x0": 1, "y0": 1, "x1": "a", "y1": 2}, "x1"),
        ({"kind": "box", "x0": 1, "y0": 1, "x1": 2, "y1": None}, "y1"),
        ({"kind": "box", "x0": 1, "y0": 1, "x1": 2, "y1": True}, "y1"),  # YAML `true` is no µm
        ({"kind": "point", "x": "3.0", "y": 1}, "x"),
        ({"kind": "pair", "a": {"x": 0, "y": 0}, "b": [2, 2]}, "b"),
        ({"kind": "pair", "a": {"x": 0, "y": 0}, "b": {"x": 2, "y": "top"}}, "b"),
        ({"kind": "line", "points": [[0, 0], [1, "a"]]}, "points"),
        ({"kind": "line", "points": [[0, 0, 0]]}, "points"),
        ({"kind": "line", "points": "0,0 1,1"}, "points"),
        ({"kind": "rule", "name": "M1.a", "locations": [[1, None]]}, "locations"),
        ({"kind": "device", "name": "xm1", "x0": "left", "y0": 0}, "x0"),
        ({"kind": "pair", "a": {"x": "left", "y": 0}, "b": {"x": 2, "y": 2}}, "a"),  # a checked too
        ({"kind": "line", "points": None}, "points"),  # YAML `points:` left blank: error, no raise
        ({"kind": "rule", "name": "M1.a", "locations": None}, "locations"),
        (
            {"kind": "line", "points": [[0, 0], [True, 1]]},
            "points",
        ),  # bool is no µm in a list either
        ({"kind": "rule", "name": "M1.a", "locations": [[1, False]]}, "locations"),
    ],
)
def test_review_anchor_coordinates_must_be_numbers(anchor, bad):
    from spicexplorer_layout.review import validate

    errs = validate(_one_anchor(anchor))
    assert len(errs) == 1 and f"({anchor['kind']})" in errs[0] and repr(bad) in errs[0], errs


def test_review_non_numeric_box_is_the_crash_validate_now_stops():
    from spicexplorer_layout.review import Finding, anchor_bbox, validate

    anchor = {"kind": "box", "x0": 1, "y0": 1, "x1": "a", "y1": None}
    with pytest.raises(TypeError):  # what annotate_crops hit, far from the file that caused it
        anchor_bbox(Finding("F1", "major", "matching", "t", where=[anchor]))
    assert validate(_one_anchor(anchor)) != []


@pytest.mark.parametrize(
    "anchor",
    [
        {"kind": "box", "x0": 0, "y0": 0.5, "x1": 1e1, "y1": -2, "layer": "Metal1"},
        {"kind": "point", "x": 1.5, "y": -3},
        {"kind": "pair", "a": {"x": 0, "y": 0}, "b": {"x": 2.5, "y": -1}},
        {"kind": "line", "points": [[0, 0], [1.0, 2.5]]},
        {"kind": "line", "points": [(0, 0), (1, 1)]},  # tuples, as Python callers build them
        {"kind": "rule", "name": "M1.a"},  # locations optional
        {"kind": "rule", "name": "M1.a", "locations": [[1, 2], [3.5, 4]]},
        {"kind": "device", "name": "xm1"},  # box optional
        {"kind": "device", "name": "xm1", "x0": 0, "y0": 0, "x1": 2},  # y1 optional
        {"kind": "net", "name": "vdd"},
        {"kind": "line", "points": []},  # boundary: empty lists carry no geometry, not a type error
        {"kind": "rule", "name": "M1.a", "locations": []},
    ],
)
def test_review_numeric_anchors_still_validate(anchor):
    from spicexplorer_layout.review import validate

    assert validate(_one_anchor(anchor)) == []


def test_load_review_refuses_a_non_numeric_anchor(tmp_path):
    import yaml
    from spicexplorer_layout.review import load_review

    p = tmp_path / "REVIEW.yaml"
    p.write_text(yaml.safe_dump(_one_anchor({"kind": "point", "x": "a", "y": 0})))
    with pytest.raises(ValueError, match=r"where\[0\] \(point\): 'x' must be a number"):
        load_review(p)


@pytest.mark.parametrize("v", [None, ""])
def test_review_blank_verdicts_are_refused_not_skipped(v):
    """A YAML ``verdict:`` left blank loads as None: the key is there, the value is no verdict —
    an enum error (not 'missing', not silently accepted), at the top level and on a finding."""
    from spicexplorer_layout.review import validate

    errs = validate({**_review_dict(), "verdict": v})
    assert len(errs) == 1 and errs[0].startswith("verdict must be one of"), errs
    d = _review_dict()
    d["findings"][1]["verdict"] = v
    errs = validate(d)
    assert len(errs) == 1 and errs[0].startswith("findings[1]: verdict must be one of"), errs


@pytest.mark.parametrize(
    "anchor,missing",
    [
        ({"kind": "box", "x0": 0, "y0": 0, "x1": 1}, "y1"),
        ({"kind": "point", "x": 0}, "y"),
        ({"kind": "pair", "a": {"x": 0, "y": 0}}, "b"),
        ({"kind": "line"}, "points"),
    ],
)
def test_review_a_missing_anchor_key_is_one_error_not_two(anchor, missing):
    """The value checks look only at keys that are there: an absent key is reported once, as
    missing — not a second time as 'must be a number, got None'."""
    from spicexplorer_layout.review import validate

    errs = validate(_one_anchor(anchor))
    assert errs == [f"findings[0].where[0] ({anchor['kind']}): missing {missing!r}"], errs


def test_review_new_vocabulary_roundtrips_through_dump_and_load(tmp_path):
    """What the Python API writes, the validator reads back: a current-density blocker under
    'PASS with majors', a re-review mark, and a Finding left at its default verdict ('open')."""
    from spicexplorer_layout.review import Finding, Review, dump_review, load_review

    r = Review(
        cell="c",
        gds="c.gds",
        verdict="PASS with majors",
        findings=[
            Finding(
                "F1",
                "blocker",
                "current_density",
                "J over via limit",
                where=[{"kind": "box", "x0": 0, "y0": 0, "x1": 1.5, "y1": 2}],
            ),
            Finding(
                "F2",
                "major",
                "matching",
                "t",
                verdict="worse",
                where=[{"kind": "line", "points": [[0, 0], [1, 1]]}],
            ),
        ],
    )
    for ext in ("yaml", "json"):
        back = load_review(dump_review(r, tmp_path / f"r.{ext}"))
        assert back.verdict == "PASS with majors"
        assert [(f.category, f.verdict) for f in back.findings] == [
            ("current_density", "open"),
            ("matching", "worse"),
        ]


# ----------------------------------------------------------------------
# LAY-01 — a common-centroid grid must actually have one centroid
# ----------------------------------------------------------------------
# The function promised "every label's centroid is the grid centre" but validated only element
# COUNTS. Five of the fifteen shapes probed came out with the labels on different centroids, and
# 3x6 did so with nine of each — the count check passed while the gradient cancellation the
# pattern exists for did not happen. That is a silent analog-matching defect: the layout looks
# deliberate and buys nothing.


def _centroid_of(grid, label):
    pts = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == label]
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


@pytest.mark.parametrize("rows,cols", [(2, 2), (2, 4), (2, 6), (4, 2), (4, 4), (3, 4), (3, 8)])
def test_the_shapes_it_returns_really_are_common_centroid(rows, cols):
    grid = common_centroid_order(("A", "B"), rows, cols)
    assert _centroid_of(grid, "A") == pytest.approx(_centroid_of(grid, "B"))


@pytest.mark.parametrize("rows,cols", [(2, 3), (3, 2), (3, 3), (3, 6), (4, 3)])
def test_a_shape_this_construction_cannot_balance_is_refused(rows, cols):
    with pytest.raises(ValueError, match="not common-centroid"):
        common_centroid_order(("A", "B"), rows, cols)


def test_equal_counts_are_not_enough():
    """3x6 holds nine of each label and is still not common-centroid — the exact gap.

    Passing the count check the function already had does not make a grid balanced, which is why
    the centroids are computed rather than inferred.
    """
    with pytest.raises(ValueError, match="not common-centroid"):
        common_centroid_order(("A", "B"), rows=3, cols=6, n_each=9)


def test_the_refusal_says_which_shapes_work():
    with pytest.raises(ValueError) as exc:
        common_centroid_order(("A", "B"), rows=3, cols=6)
    assert "2x4" in str(exc.value) and "even number of columns" in str(exc.value)


# ----------------------------------------------------------------------
# LAY-02 — the generator contract is enforced, not advertised
# ----------------------------------------------------------------------
# The README promises "a frozen LayoutParams dataclass (every field is a knob ... with a default)"
# but `load_generator` checked only `is_dataclass`. Both remaining halves fail far from their
# cause: a mutable params object lets an optimizer trial desync its GDS from its recorded
# parameters, and a defaultless field raises inside `default_params()` mid-sweep while
# `params_schema()` advertises the knob with a default of None.

_GEN_HEAD = "import dataclasses\n\nCELL = 'c'\n\n"
_GEN_TAIL = "\ndef build(params, sizing=None):\n    return params\n"


def _write_gen(tmp_path, body: str):
    from spicexplorer_layout.gen import load_generator

    p = tmp_path / "gen_c.py"
    p.write_text(_GEN_HEAD + body + _GEN_TAIL)
    return lambda: load_generator(p)


def test_a_compliant_generator_still_loads(tmp_path):
    load = _write_gen(
        tmp_path,
        "@dataclasses.dataclass(frozen=True)\nclass LayoutParams:\n    gap_x: float = 1.0\n",
    )
    gen = load()
    assert gen.default_params().gap_x == 1.0


def test_a_mutable_params_dataclass_is_refused(tmp_path):
    load = _write_gen(
        tmp_path, "@dataclasses.dataclass\nclass LayoutParams:\n    gap_x: float = 1.0\n"
    )
    with pytest.raises(TypeError, match="frozen"):
        load()


def test_a_knob_without_a_default_is_refused(tmp_path):
    """The defaultless field comes FIRST on purpose.

    Putting it after a defaulted one makes Python itself raise at class definition ("non-default
    argument follows default argument"), so the test would pass without the loader checking
    anything — this way the refusal can only come from the loader.
    """
    load = _write_gen(
        tmp_path,
        "@dataclasses.dataclass(frozen=True)\nclass LayoutParams:\n    ch_y: float\n",
    )
    with pytest.raises(TypeError, match="ch_y"):
        load()


def test_a_default_factory_counts_as_a_default(tmp_path):
    load = _write_gen(
        tmp_path,
        "@dataclasses.dataclass(frozen=True)\nclass LayoutParams:\n"
        "    layers: tuple = dataclasses.field(default_factory=tuple)\n",
    )
    assert load().default_params().layers == ()
