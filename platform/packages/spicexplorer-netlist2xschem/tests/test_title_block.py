"""The drawn title block: the date is an input, and no field collides (issue #265).

The two halves of the issue are tested exactly as its acceptance criteria state them:

* **reproducible** — rendering the same ``.sch`` twice, hours apart (the file's mtime moved between
  renders), gives byte-identical SVGs. The control on the same sheet is xschem's own
  ``devices/title.sym``, whose ``@time_last_modified`` is read from that mtime: it *must* differ,
  or the test is not measuring anything;
* **no collision** — on sheets 1200 to 15000 units wide, no two of the block's rendered text
  extents overlap, none crosses the frame, and every one is inside it.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import build_sch, from_file
from spicexplorer_netlist2xschem.render import _text_box, render, xschem_available
from spicexplorer_netlist2xschem.sch_parser import parse_sch
from spicexplorer_netlist2xschem.title_block import (
    TitleBlock,
    add_title_block,
    title_block_date,
)

FIXTURES = Path(__file__).parent / "fixtures"
requires_xschem = pytest.mark.skipif(not xschem_available(), reason="xschem not on PATH")

CELL, DESIGN, REV, DATE, AUTHOR = "sar8_top", "dn-000-demo", "b3", "2026-09-21", "A. Designer"
FIELDS = (CELL, f"design  {DESIGN}", f"rev  {REV}", DATE, f"drawn by  {AUTHOR}")


def _sheet(width: int = 1200, height: int = 600) -> str:
    """A bare sheet ``width`` units across, drawn with plain wires (no symbol library needed)."""
    rows = [f"N 0 {y} {width} {y} {{}}" for y in range(0, height + 1, max(40, height // 8))]
    return (
        "v {xschem version=3.4.6 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n"
        + "\n".join(rows)
        + "\n"
    )


def _with_block(width: int = 1200, **kw) -> str:
    return add_title_block(
        _sheet(width), cell=CELL, design=DESIGN, rev=REV, date=DATE, author=AUTHOR, **kw
    )


# ---------------------------------------------------------------------------
# the sheet is a function of its inputs
# ---------------------------------------------------------------------------


def test_the_block_draws_its_own_fields_and_no_clock_token():
    text = _with_block()
    for field in FIELDS:
        assert f"T {{{field}}}" in text, field
    assert "@time_last_modified" not in text  # the mtime token the stock symbol carries
    assert "title.sym" not in text  # ... and the stock symbol itself is not instantiated
    assert " 0 1 " not in text.split("E {}")[-1]  # no flip=1 record: it does not survive the zoom


def test_the_same_inputs_give_the_same_bytes():
    assert _with_block() == _with_block()


def test_title_block_date_prefers_source_date_epoch():
    import datetime

    assert title_block_date({"SOURCE_DATE_EPOCH": "1600000000"}) == "2020-09-13"
    assert title_block_date({}, today=datetime.date(2026, 9, 21)) == "2026-09-21"
    # a malformed value is not a crash and not a silent "1970-01-01"
    assert title_block_date(
        {"SOURCE_DATE_EPOCH": "nonsense"}, today=datetime.date(2026, 9, 21)
    ) == ("2026-09-21")


def test_the_environment_is_not_sniffed_for_the_other_fields(monkeypatch):
    monkeypatch.setenv("USER", "somebody")
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1600000000")
    text = _with_block()
    assert "somebody" not in text
    assert "2020-09-13" not in text  # the caller named a date; the environment does not override it


def test_empty_fields_draw_no_row():
    text = add_title_block(_sheet(), cell=CELL, date=DATE)
    assert f"T {{{CELL}}}" in text and f"T {{{DATE}}}" in text
    assert "drawn by" not in text and "design  " not in text and "rev  " not in text


# ---------------------------------------------------------------------------
# placement: clear of the drawing, in the requested corner
# ---------------------------------------------------------------------------


def _block_records(text: str) -> tuple[list, list]:
    """The block's own ``L`` (layer 3) and ``T`` records, parsed back out of the sheet."""
    sch = parse_sch(text)
    return (
        [ln for ln in sch.lines if ln.layer == 3],
        [t for t in sch.texts if t.text in FIELDS],
    )


@pytest.mark.parametrize(
    ("corner", "below", "flush_right"),
    [
        ("bottom-right", True, True),
        ("bottom-left", True, False),
        ("top-right", False, True),
        ("top-left", False, False),
    ],
)
def test_the_block_sits_clear_of_the_drawing(corner, below, flush_right):
    width, height = 1200, 600
    text = _with_block(width, corner=corner)
    lines, texts = _block_records(text)
    assert len(lines) == 8 and len(texts) == len(FIELDS)
    ys = [c for ln in lines for c in (ln.y1, ln.y2)] + [t.y for t in texts]
    xs = [c for ln in lines for c in (ln.x1, ln.x2)] + [t.x for t in texts]
    if below:
        assert min(ys) > height, f"{corner}: block starts at y={min(ys)}, sheet ends at {height}"
    else:
        assert max(ys) < 0, f"{corner}: block ends at y={max(ys)}, sheet starts at 0"
    if flush_right:
        assert max(xs) == pytest.approx(width) and min(xs) > width / 2
    else:
        assert min(xs) == pytest.approx(0) and max(xs) < width


@pytest.mark.parametrize("width", [400, 1200, 5000, 20000])
def test_the_block_keeps_the_same_share_of_the_sheet_at_any_extent(width):
    """Field sizes and frame scale together with the sheet, so the layout is extent-invariant."""
    lines, texts = _block_records(_with_block(width))
    block_w = max(ln.x1 for ln in lines) - min(ln.x2 for ln in lines)
    assert 0.05 < block_w / width < 0.55, f"{width}: block is {block_w} wide"
    assert len({round(t.size_x / t.size_y, 6) for t in texts}) == 1  # never distorted


# ---------------------------------------------------------------------------
# the emitter / library entry points
# ---------------------------------------------------------------------------


def test_build_sch_without_a_title_block_is_unchanged():
    circuit = from_file(FIXTURES / "ota-improved.spice", name="ota-improved")
    before = build_sch(circuit, pdk="ihp-sg13g2", title="ota-improved").text
    assert "L 3 " not in before
    assert before.count("T {ota-improved}") == 1  # the loose title record, exactly as before


def test_build_sch_with_a_title_block_replaces_the_loose_title_record():
    circuit = from_file(FIXTURES / "ota-improved.spice", name="ota-improved")
    doc = build_sch(
        circuit,
        pdk="ihp-sg13g2",
        title="ota-improved",
        title_block=TitleBlock(
            cell="ota-improved", design=DESIGN, rev=REV, date=DATE, author=AUTHOR
        ),
    )
    assert not re.search(r"^T \{ota-improved\} .* 0 0 0\.4 0\.4 \{\}$", doc.text, re.M)
    for field in (f"design  {DESIGN}", f"rev  {REV}", DATE, f"drawn by  {AUTHOR}"):
        assert f"T {{{field}}}" in doc.text
    assert doc.device_count and doc.wire_count  # the drawing itself is untouched


def test_an_sch_document_in_gives_an_sch_document_out():
    circuit = from_file(FIXTURES / "ota-improved.spice", name="ota-improved")
    doc = build_sch(circuit, pdk="ihp-sg13g2", title="ota-improved")
    out = add_title_block(doc, cell="ota-improved", date=DATE)
    assert out.device_count == doc.device_count and out.text != doc.text


def test_the_cli_draws_the_block_and_prints_the_date(tmp_path, capsys):
    from spicexplorer_netlist2xschem.cli import main

    out = tmp_path / "ota.sch"
    rc = main(
        [
            str(FIXTURES / "ota-improved.spice"),
            "-o",
            str(out),
            "--title-block",
            "--design",
            DESIGN,
            "--rev",
            REV,
            "--date",
            DATE,
            "--author",
            AUTHOR,
        ]
    )
    assert rc == 0
    assert f"date={DATE}" in capsys.readouterr().out
    assert f"T {{drawn by  {AUTHOR}}}" in out.read_text()


def test_the_cli_defaults_the_date_and_says_which_one_it_used(tmp_path, capsys, monkeypatch):
    from spicexplorer_netlist2xschem.cli import main

    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1600000000")
    out = tmp_path / "ota.sch"
    assert main([str(FIXTURES / "ota-improved.spice"), "-o", str(out), "--title-block"]) == 0
    assert "date=2020-09-13" in capsys.readouterr().out
    assert "T {2020-09-13}" in out.read_text()


def _annotations_file(tmp_path: Path, refs) -> Path:
    from spicexplorer_netlist2xschem import BlockAnnotation, BlockAnnotationSet

    aset = BlockAnnotationSet(
        (BlockAnnotation("b1", tuple(refs), label="pair", family="differential_pair"),)
    )
    path = tmp_path / "blocks.json"
    path.write_text(aset.to_json())
    return path


def test_the_cli_draws_the_block_on_the_annotate_existing_lane(tmp_path):
    """The post-pass lane: the input IS a sheet, so the block is added to the annotated copy."""
    from spicexplorer_netlist2xschem import parse_sch as _parse
    from spicexplorer_netlist2xschem.cli import main

    circuit = from_file(FIXTURES / "ota-improved.spice", name="ota-improved")
    existing = tmp_path / "hand-drawn.sch"
    existing.write_text(build_sch(circuit, pdk="ihp-sg13g2").text)
    drawn = [c.name for c in _parse(existing.read_text()).devices][:2]
    out = tmp_path / "annotated.sch"
    rc = main(
        [
            str(existing),
            "--annotate-existing",
            "--annotations",
            str(_annotations_file(tmp_path, drawn)),
            "-o",
            str(out),
            "--title-block",
            "--design",
            DESIGN,
            "--rev",
            REV,
            "--date",
            DATE,
            "--author",
            AUTHOR,
        ]
    )
    assert rc == 0
    text = out.read_text()
    assert f"T {{drawn by  {AUTHOR}}}" in text and f"T {{{DATE}}}" in text
    assert len([ln for ln in _parse(text).lines if ln.layer == 3]) == 8
    # the existing sheet's own devices and wires are untouched by the post-pass
    assert len(_parse(text).devices) == len(_parse(existing.read_text()).devices)


def test_the_cli_draws_the_block_on_the_hierarchical_lane(tmp_path):
    """The other post-pass lane: the block goes on the PARENT sheet, after its symbols are placed."""
    from spicexplorer_netlist2xschem import parse_sch as _parse
    from spicexplorer_netlist2xschem.cli import main

    circuit = from_file(FIXTURES / "ota-improved.spice", name="ota-improved")
    refs = [d.ref for d in circuit.devices][:2]
    out = tmp_path / "top.sch"
    rc = main(
        [
            str(FIXTURES / "ota-improved.spice"),
            "-o",
            str(out),
            "--hierarchical",
            "--annotations",
            str(_annotations_file(tmp_path, refs)),
            "--title-block",
            "--design",
            DESIGN,
            "--rev",
            REV,
            "--date",
            DATE,
            "--author",
            AUTHOR,
        ]
    )
    assert rc == 0
    parent = _parse(out.read_text())
    assert len([ln for ln in parent.lines if ln.layer == 3]) == 8
    assert {f"rev  {REV}", DATE} <= {t.text for t in parent.texts}
    # ... and the sheet does not carry its name twice: the loose title record is taken off first.
    assert [t.text for t in parent.texts].count("ota-improved") == 1
    assert (tmp_path / "blocks").is_dir()  # the hierarchy itself is unchanged


def test_the_cli_says_so_when_the_fields_are_given_without_the_flag(tmp_path, capsys):
    from spicexplorer_netlist2xschem.cli import main

    out = tmp_path / "ota.sch"
    assert main([str(FIXTURES / "ota-improved.spice"), "-o", str(out), "--rev", REV]) == 0
    assert "--rev ignored" in capsys.readouterr().err
    assert "L 3 " not in out.read_text()


# ---------------------------------------------------------------------------
# rendered: reproducible, and nothing collides
# ---------------------------------------------------------------------------


def _render_twice(sch: Path, tmp_path: Path) -> tuple[bytes, bytes]:
    """Render ``sch``, move its mtime on seven hours, render again; return both SVGs."""
    os.utime(sch, (1_600_000_000, 1_600_000_000))
    first = render(sch, fmt="svg", outdir=tmp_path)
    assert first.image_path is not None, first.log
    a = first.image_path.read_bytes()
    os.utime(sch, (1_600_000_000 + 7 * 3600, 1_600_000_000 + 7 * 3600))
    second = render(sch, fmt="svg", outdir=tmp_path)
    assert second.image_path is not None, second.log
    return a, second.image_path.read_bytes()


@requires_xschem
@pytest.mark.slow
def test_rendering_the_same_sheet_hours_apart_is_byte_identical(tmp_path):
    sch = tmp_path / "block.sch"
    sch.write_text(_with_block(1200))
    a, b = _render_twice(sch, tmp_path)
    assert a == b, "the drawn title block rendered differently after the mtime moved"
    assert DATE.encode() in a


@requires_xschem
@pytest.mark.slow
def test_the_stock_title_symbol_is_the_control_and_does_churn(tmp_path):
    """The same measurement on ``devices/title.sym`` — it MUST differ, or the test above is blind."""
    sch = tmp_path / "stock.sch"
    sch.write_text(_sheet(1200) + 'C {devices/title.sym} 20 700 0 0 {name=l1 author="MacAnalog"}\n')
    a, b = _render_twice(sch, tmp_path)
    if b"MacAnalog" not in a:
        pytest.skip("devices/title.sym did not resolve on the symbol search path")
    assert a != b, "the stock title block no longer carries the file's mtime — re-check the fix"


def _px_boxes(svg: str) -> tuple[dict[str, tuple[float, float, float, float]], list[tuple]]:
    """Every field's rendered box, and the frame's segments, in SVG pixels."""
    boxes: dict[str, tuple[float, float, float, float]] = {}
    for attrs, content in re.findall(r"<text\b([^>]*)>(.*?)</text>", svg, re.DOTALL):
        text = content.strip()
        if text in FIELDS:
            xs, ys = _text_box(attrs, content)
            boxes[text] = (xs[0], ys[0], xs[1], ys[1])
    frame: list[tuple] = []
    for el in re.findall(r'<path\b[^>]*class="l3"[^>]*>', svg):
        d = re.search(r'\bd="([^"]*)"', el)
        if d:
            n = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d.group(1))]
            if len(n) >= 4:
                frame.append((n[0], n[1], n[2], n[3]))
    return boxes, frame


@requires_xschem
@pytest.mark.slow
@pytest.mark.parametrize("width", [1200, 5000, 15000])
def test_no_two_title_fields_collide_on_a_wide_sheet(tmp_path, width):
    sch = tmp_path / f"w{width}.sch"
    sch.write_text(_with_block(width))
    result = render(sch, fmt="svg", outdir=tmp_path, color_nets=False)
    assert result.image_path is not None, result.log
    boxes, frame = _px_boxes(result.image_path.read_text())
    assert set(boxes) == set(FIELDS), f"{width}: fields missing from the export: {set(boxes)}"
    assert len(frame) == 8, f"{width}: {len(frame)} frame segments in the export"

    names = sorted(boxes)
    for i, a in enumerate(names):
        ax0, ay0, ax1, ay1 = boxes[a]
        for b in names[i + 1 :]:
            bx0, by0, bx1, by1 = boxes[b]
            assert ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0, (
                f"{width}: {a!r} and {b!r} overlap ({boxes[a]} vs {boxes[b]})"
            )
        for sx0, sy0, sx1, sy1 in frame:
            lo_x, hi_x = min(sx0, sx1), max(sx0, sx1)
            lo_y, hi_y = min(sy0, sy1), max(sy0, sy1)
            crosses = ax0 < hi_x and lo_x < ax1 and ay0 < hi_y and lo_y < ay1
            assert not crosses, (
                f"{width}: {a!r} {boxes[a]} crosses the frame segment {(sx0, sy0, sx1, sy1)}"
            )

    fx = [c for seg in frame for c in (seg[0], seg[2])]
    fy = [c for seg in frame for c in (seg[1], seg[3])]
    for name, (x0, y0, x1, y1) in boxes.items():
        assert min(fx) <= x0 and x1 <= max(fx), f"{width}: {name!r} outside the frame horizontally"
        assert min(fy) <= y0 and y1 <= max(fy), f"{width}: {name!r} outside the frame vertically"
