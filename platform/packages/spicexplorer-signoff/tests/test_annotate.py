"""Offline tests for the layout-annotation method — no PDK, no klayout executable.

The schema, the frame transform and the collision stacker are pure Python and always run.
The geometry readers (:func:`instances`, :func:`regions`) and the render need the
``klayout`` module; those tests build a tiny GDS in a tmpdir and skip if it is absent.
The full :func:`annotate` pass additionally needs matplotlib.
"""

from __future__ import annotations

import pytest
from spicexplorer_signoff.annotate import (
    PALETTE,
    SCHEMA,
    SEVERITY_COLOR,
    Frame,
    Label,
    Spec,
    _anchor_point,
    annotate,
    cell_bbox,
    instances,
    layer_names,
    load_spec,
    pdk_lyp,
    regions,
    resolve_label,
    stack_labels,
    validate_spec,
)

kdb = pytest.importorskip  # alias so the intent below reads


# ------------------------------------------------------------------- schema --


def _min_spec(**kw):
    d = {"cell": "c", "labels": [{"text": "pair", "bbox": [0, 0, 10, 10]}]}
    d.update(kw)
    return d


def test_validate_accepts_minimal():
    assert validate_spec(_min_spec()) == []


def test_load_spec_defaults_and_roundtrip():
    s = load_spec(_min_spec(render={"px_per_um": 12, "ground": "white"}))
    assert isinstance(s, Spec)
    assert s.schema == SCHEMA
    assert s.render.px_per_um == 12 and s.render.ground == "white"
    assert s.render.margin_frac == 0.02  # untouched default
    assert s.labels[0].anchor == "center"


def test_load_spec_from_json_file(tmp_path):
    p = tmp_path / "labels.json"
    p.write_text('{"cell":"c","labels":[{"text":"t","point":[1,2]}]}')
    assert load_spec(p).labels[0].point == [1, 2]


@pytest.mark.parametrize(
    "bad, needle",
    [
        ({"schema": "nope"}, "schema"),
        ({"render": {"ground": "puce"}}, "render.ground"),
        ({"render": {"px_per_um": 0}}, "px_per_um"),
        ({"render": {"pxperum": 6}}, "unknown key"),
        ({"labels": [{"bbox": [0, 0, 1, 1]}]}, "text"),
        ({"labels": [{"text": "t"}]}, "'match', 'bbox', 'point'"),
        ({"labels": [{"text": "t", "point": [0, 0], "anchor": "sideways"}]}, "anchor"),
        ({"groups": [{"name": "g"}]}, "'members' or 'bbox'"),
        ({"groups": [{"name": "g", "members": ["ghost"]}]}, "not a label text"),
        ({"findings": [{"id": "F1", "severity": "bad", "text": "t", "point": [0, 0]}]}, "severity"),
        ({"findings": [{"id": "F1", "severity": "major", "text": "t"}]}, "'bbox' or 'point'"),
    ],
)
def test_validate_rejects(bad, needle):
    errs = validate_spec(_min_spec(**bad))
    assert any(needle in e for e in errs), errs


def test_duplicate_finding_ids_rejected():
    f = {"id": "F1", "severity": "major", "text": "t", "point": [0, 0]}
    assert validate_spec(_min_spec(findings=[f, dict(f)]))


def test_load_spec_raises_on_invalid():
    with pytest.raises(ValueError):
        load_spec({"labels": [{"text": "t"}]})


def test_palette_is_colour_blind_safe_and_distinct():
    assert len(set(PALETTE)) == len(PALETTE) >= 8
    assert set(SEVERITY_COLOR) == {"blocker", "major", "minor", "note"}
    assert set(SEVERITY_COLOR.values()) <= set(PALETTE)


# -------------------------------------------------------------------- frame --


def test_frame_margin_and_size():
    f = Frame.around((0, 0, 100, 50), px_per_um=6.0, margin_frac=0.02)
    assert f.x0 == pytest.approx(-2.0) and f.x1 == pytest.approx(102.0)
    assert f.y0 == pytest.approx(-2.0) and f.y1 == pytest.approx(52.0)
    assert f.size_px == (624, 324)


def test_frame_transform_corners_and_y_flip():
    f = Frame.around((0, 0, 100, 100), px_per_um=10.0, margin_frac=0.0)
    assert f.to_px(0, 100) == pytest.approx((0.0, 0.0))  # top-left
    assert f.to_px(100, 0) == pytest.approx((1000.0, 1000.0))  # bottom-right
    # y grows upward in µm and downward in pixels
    assert f.to_px(50, 75)[1] < f.to_px(50, 25)[1]


def test_frame_box_px():
    f = Frame.around((0, 0, 100, 100), px_per_um=2.0, margin_frac=0.0)
    left, top, w, h = f.box_px([10, 20, 30, 60])
    assert (left, top, w, h) == pytest.approx((20.0, 80.0, 40.0, 80.0))


def test_anchor_points():
    bb = (0, 0, 10, 20)
    assert _anchor_point(bb, "center") == (5, 10)
    assert _anchor_point(bb, "above") == (5, 20)
    assert _anchor_point(bb, "below") == (5, 0)
    assert _anchor_point(bb, "left") == (0, 10)
    assert _anchor_point(bb, "right") == (10, 10)


# ----------------------------------------------------------------- stacking --


def _rects(placed):
    return [p.rect for p in placed]


def _overlaps(rects, pad=0.0):
    for i, a in enumerate(rects):
        for b in rects[i + 1 :]:
            if not (
                a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1]
            ):
                return True
    return False


def test_stack_labels_separates_coincident_labels():
    items = [(f"L{i}", (100.0, 100.0), (60.0, 20.0), "above") for i in range(5)]
    placed = stack_labels(items, pad=4.0)
    assert len(placed) == 5
    assert not _overlaps(_rects(placed))


def test_stack_labels_stacks_along_the_anchor_direction():
    items = [("a", (0.0, 0.0), (40.0, 10.0), "right"), ("b", (0.0, 0.0), (40.0, 10.0), "right")]
    a, b = stack_labels(items, pad=2.0)
    assert b.pos_px[0] > a.pos_px[0]  # pushed sideways, not downwards
    assert b.pos_px[1] == pytest.approx(a.pos_px[1])


def test_stack_labels_leaves_a_lone_label_unmoved():
    (p,) = stack_labels([("solo", (10.0, 10.0), (20.0, 8.0), "center")], pad=2.0)
    assert p.moved is False
    assert p.pos_px == (10.0, 10.0)


def test_stack_labels_marks_displaced_labels_for_a_leader_line():
    items = [(f"L{i}", (0.0, 0.0), (30.0, 10.0), "below") for i in range(4)]
    placed = stack_labels(items, pad=2.0)
    assert placed[0].moved is False
    assert placed[-1].moved is True  # far enough to need a leader


def test_stack_labels_keeps_everything_inside_bounds():
    B = (0.0, 0.0, 400.0, 300.0)
    items = [(f"L{i}", (5.0, 150.0), (120.0, 20.0), "left") for i in range(4)]
    placed = stack_labels(items, pad=2.0, bounds=B)
    for p in placed:
        x0, y0, x1, y1 = p.rect
        assert x0 >= B[0] - 1e-6 and y0 >= B[1] - 1e-6
        assert x1 <= B[2] + 1e-6 and y1 <= B[3] + 1e-6


def test_bounds_do_not_reintroduce_collisions():
    # every label wants to go left off the frame; pinned, they must stack instead of pile up
    B = (0.0, 0.0, 400.0, 300.0)
    items = [(f"L{i}", (5.0, 20.0), (150.0, 18.0), "left") for i in range(5)]
    placed = stack_labels(items, pad=3.0, bounds=B)
    assert not _overlaps(_rects(placed))
    assert len({p.pos_px[1] for p in placed}) > 1  # they spread vertically, not sideways


def test_stack_labels_gives_up_rather_than_looping_when_boxed_in():
    tight = (0.0, 0.0, 60.0, 24.0)  # room for exactly one label
    placed = stack_labels(
        [(f"L{i}", (30.0, 12.0), (50.0, 20.0), "center") for i in range(3)], pad=2.0, bounds=tight
    )
    assert len(placed) == 3  # returns every label; the caller decides what to do about it


def test_stack_labels_is_deterministic():
    items = [(f"L{i}", (5.0 * i, 0.0), (40.0, 10.0), "above") for i in range(8)]
    assert [p.pos_px for p in stack_labels(items)] == [p.pos_px for p in stack_labels(items)]


# ------------------------------------------------------- geometry (klayout) --


@pytest.fixture
def tiny_gds(tmp_path):
    """Three instances of one 2x1 µm cell in a row, plus a ring on layer 31/0."""
    db = pytest.importorskip("klayout.db")
    ly = db.Layout()
    ly.dbu = 0.001
    unit = ly.create_cell("dev")
    unit.shapes(ly.layer(1, 0)).insert(db.Box(0, 0, 2000, 1000))
    top = ly.create_cell("top")
    for i in range(3):
        top.insert(db.CellInstArray(unit.cell_index(), db.Trans(db.Vector(i * 5000, 0))))
    # a closed ring (outer box minus inner box) and a solid box on the same layer
    nw = ly.layer(31, 0)
    reg = db.Region(db.Box(-2000, -3000, 20000, -1000)) - db.Region(db.Box(0, -2500, 18000, -1500))
    reg.insert(db.Box(-2000, 4000, 4000, 6000))  # solid, no hole
    reg.merge()
    top.shapes(nw).insert(reg)
    p = tmp_path / "tiny.gds"
    ly.write(str(p))
    return p


def test_instances_order_names_and_boxes(tiny_gds):
    got = instances(tiny_gds)
    assert len(got) == 3
    assert [i.index for i in got.values()] == [0, 1, 2]
    assert all(i.cell == "dev" for i in got.values())
    # unnamed instances get a unique synthetic key, never a collision
    assert len(set(got)) == 3
    first = list(got.values())[0]
    assert first.bbox == pytest.approx((0.0, 0.0, 2.0, 1.0))
    assert first.center == pytest.approx((1.0, 0.5))
    assert list(got.values())[2].bbox == pytest.approx((10.0, 0.0, 12.0, 1.0))


def test_cell_bbox(tiny_gds):
    assert cell_bbox(tiny_gds) == pytest.approx((-2.0, -3.0, 20.0, 6.0))


def test_regions_by_layer_number_when_no_lyp(tiny_gds):
    boxes = regions(tiny_gds, "31/0", lyp="/nonexistent.lyp")
    assert len(boxes) == 2
    assert boxes[0][2] - boxes[0][0] > boxes[1][2] - boxes[1][0]  # largest first


def test_regions_holes_only_finds_the_closed_ring(tiny_gds):
    boxes = regions(tiny_gds, "31/0", lyp="/nonexistent.lyp", holes_only=True)
    assert len(boxes) == 1
    assert boxes[0] == pytest.approx((-2.0, -3.0, 20.0, -1.0))


def test_regions_min_area_filter(tiny_gds):
    assert regions(tiny_gds, "31/0", lyp="/nonexistent.lyp", min_area_um2=1e6) == []


def test_layer_names_missing_lyp_is_empty_not_an_error():
    assert layer_names(lyp="/nonexistent.lyp") == {}


def test_pdk_lyp_unknown_pdk_is_none_not_an_error(monkeypatch, tmp_path):
    # unknown to spicexplorer_signoff.pdk AND absent from $PDK_ROOT -> None, never a raise.
    # (Callers then degrade to raw layer numbers; this is also the standalone-import path,
    # where `from . import pdk` itself fails.)
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    assert pdk_lyp("nope-1um") is None


def test_pdk_lyp_falls_back_to_pdk_root_glob(monkeypatch, tmp_path):
    tech = tmp_path / "nope-1um" / "libs.tech" / "klayout" / "tech"
    tech.mkdir(parents=True)
    (tech / "nope.lyp").write_text("<layer-properties/>")
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    assert pdk_lyp("nope-1um") == tech / "nope.lyp"


def test_layer_names_parses_a_lyp(tmp_path):
    p = tmp_path / "t.lyp"
    p.write_text(
        "<layer-properties>"
        "<properties><source>31/0@1</source><name>NWell.drawing</name></properties>"
        "<properties><source>126/0@1</source><name>TopMetal1.drawing</name></properties>"
        "<properties><source>*/*@1</source><name>ignored</name></properties>"
        "</layer-properties>"
    )
    got = layer_names(lyp=p)
    assert got[(31, 0)] == "NWell" and got[(126, 0)] == "TopMetal1"


# ------------------------------------------------------------------ resolve --


def test_resolve_explicit_bbox_and_point():
    assert resolve_label(Label("t", bbox=[1, 2, 3, 4]), {}, None, "ihp-sg13g2") == (1, 2, 3, 4)
    assert resolve_label(Label("t", point=[5, 6]), {}, None, "ihp-sg13g2") == (5, 6, 5, 6)


def test_resolve_index_range_merges_into_one_group_box(tiny_gds):
    insts = instances(tiny_gds)
    bb = resolve_label(Label("row", match={"index": [0, 2]}), insts, tiny_gds, "ihp-sg13g2")
    assert bb == pytest.approx((0.0, 0.0, 12.0, 1.0))


def test_resolve_single_index_and_cell_regex(tiny_gds):
    insts = instances(tiny_gds)
    assert resolve_label(Label("one", match={"index": 1}), insts, tiny_gds, "x")[
        0
    ] == pytest.approx(5.0)
    assert resolve_label(Label("all", match={"cell": "^dev$"}), insts, tiny_gds, "x")[
        2
    ] == pytest.approx(12.0)


def test_resolve_no_match_is_a_readable_error(tiny_gds):
    with pytest.raises(ValueError, match="selected no instance"):
        resolve_label(Label("x", match={"cell": "nothing"}), instances(tiny_gds), tiny_gds, "x")


def test_resolve_layer_match(tiny_gds):
    bb = resolve_label(
        Label("ring", match={"layer": "31/0", "holes_only": True}), {}, tiny_gds, "x"
    )
    assert bb == pytest.approx((-2.0, -3.0, 20.0, -1.0))


# ------------------------------------------------------- end-to-end (render) --


@pytest.fixture
def full_spec():
    return {
        "cell": "top",
        "render": {"px_per_um": 20, "ground": "white", "oversampling": 1, "dpi": 150},
        "labels": [
            {"text": "device row", "role": "A B A", "match": {"index": [0, 2]}, "anchor": "above"},
            {
                "text": "guard ring",
                "match": {"layer": "31/0", "holes_only": True},
                "anchor": "below",
            },
            {"text": "overlapping", "match": {"index": [0, 2]}, "anchor": "above"},
        ],
        "groups": [{"name": "core", "members": ["device row"], "note": "3 devices"}],
        "paths": [{"name": "I path", "points_um": [[0, 0], [6, 0], [12, 1]], "label": "10 mA"}],
        "findings": [
            {"id": "F1", "severity": "blocker", "text": "too narrow", "bbox": [0, 0, 2, 1]},
            {"id": "F2", "severity": "note", "text": "check tie", "point": [11, 0.5]},
        ],
        "scale_bar": {"length_um": 5, "separate_output": True},
    }


def test_annotate_writes_every_output(tmp_path, tiny_gds, full_spec):
    pytest.importorskip("klayout.lay")
    pytest.importorskip("matplotlib")
    out = annotate(tiny_gds, full_spec, tmp_path / "cell", formats=("png",))
    names = {p.name for p in out}
    assert {"cell_labelled.png", "cell_labelled_scale.png", "cell_review.png"} <= names
    assert {"F1.png", "F2.png"} == {p.name for p in (tmp_path / "cell_crops").iterdir()}
    for p in out:
        assert p.stat().st_size > 0
    # the plain render is written under its own name and never overwritten by an overlay
    assert (tmp_path / "cell_base.png").is_file()


def test_annotate_without_findings_skips_the_review_outputs(tmp_path, tiny_gds, full_spec):
    pytest.importorskip("klayout.lay")
    pytest.importorskip("matplotlib")
    full_spec.pop("findings")
    names = {p.name for p in annotate(tiny_gds, full_spec, tmp_path / "c", formats=("png",))}
    assert not any("review" in n for n in names)
    assert not (tmp_path / "c_crops").exists()


def test_quantize_shrinks_the_png_and_keeps_its_size(tmp_path, tiny_gds, full_spec):
    pytest.importorskip("klayout.lay")
    pytest.importorskip("matplotlib")
    Image = pytest.importorskip("PIL.Image")
    plain = annotate(tiny_gds, full_spec, tmp_path / "a", formats=("png",))[0]
    small = annotate(tiny_gds, full_spec, tmp_path / "b", formats=("png",), quantize=256)[0]
    assert small.stat().st_size <= plain.stat().st_size
    assert Image.open(small).size == Image.open(plain).size


def test_annotate_from_png_requires_explicit_boxes(tmp_path, tiny_gds, full_spec):
    pytest.importorskip("klayout.lay")
    pytest.importorskip("matplotlib")
    annotate(tiny_gds, full_spec, tmp_path / "c", formats=("png",))
    with pytest.raises(ValueError, match="explicit bbox"):
        annotate(tmp_path / "c_base.png", full_spec, tmp_path / "d", formats=("png",))
