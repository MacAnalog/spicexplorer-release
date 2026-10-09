"""A generated block symbol's pin names stay INSIDE its body (issue #266).

xschem text is anchored at its left edge, so an offset that reads "12 units in from the edge" only
works on the LEFT side: on the right edge the label used to *start* 12 units inside and run outward,
its first glyph struck through by the body's own border.

Two tests, deliberately at different levels:

* :func:`test_right_side_pin_labels_end_inside_the_body` reads the emitted ``.sym`` and checks the
  text's estimated extent against the body edge — it runs everywhere, no xschem needed;
* :func:`test_rendered_right_side_pin_labels_do_not_cross_the_body_edge` renders a sheet carrying the
  generated symbol with real xschem and measures the exported ``<text>`` elements, which is the thing
  the issue was actually about.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem.render import _text_box, render, xschem_available
from spicexplorer_netlist2xschem.sch_parser import parse_sch
from spicexplorer_netlist2xschem.symbol_gen import (
    _PIN_HALF,
    _STUB,
    BlockPin,
    generate_block_symbol,
    label_width,
)

requires_xschem = pytest.mark.skipif(not xschem_available(), reason="xschem not on PATH")

#: Pin names as long as the ones the issue was measured on (an 8-bit SAR's control bus).
_RIGHT_NAMES = ["sample_ready", "cmp_out_valid", "dac_settled", "eoc_strobe"]
_LEFT_NAMES = ["clk_in", "rst_n"]


def _block():
    return generate_block_symbol(
        "sar_swdrv_bank",
        [BlockPin(net=n, side="left") for n in _LEFT_NAMES]
        + [BlockPin(net=n, side="right") for n in _RIGHT_NAMES],
    )


def _body_half_width(sym_text: str) -> float:
    """Half-width of the body rectangle (the four ``L`` lines drawn around the block)."""
    xs = [c for ln in parse_sch(sym_text).lines for c in (ln.x1, ln.x2)]
    # the stubs stick out past the body; the body edge is the second-largest distinct |x|
    return sorted({abs(x) for x in xs})[-2]


def test_right_side_pin_labels_end_inside_the_body():
    """Each right-side name's drawn extent ends at least 12 units short of the body's right edge."""
    sym = _block()
    half_w = _body_half_width(sym.text)
    right = {t.text: t for t in parse_sch(sym.text).texts if t.text in _RIGHT_NAMES}
    assert set(right) == set(_RIGHT_NAMES), right
    for name, t in right.items():
        assert t.flip == 0, f"{name}: flip=1 does not survive the export zoom (see symbol_gen)"
        end = t.x + label_width(name, t.size_x)
        assert end <= half_w - 12 + 1e-6, f"{name}: text runs to {end}, body edge at {half_w}"
        assert t.x > -half_w, f"{name}: text starts left of the body ({t.x} < {-half_w})"


def test_a_long_right_side_name_still_ends_inside_the_body():
    """A name long enough to start left of the symbol origin: the placement rounds the RIGHT way."""
    long_name = "sample_ready_early"  # 18 characters: its anchor lands at x < 0 on this body
    sym = generate_block_symbol(
        "sar_swdrv_bank",
        [BlockPin(net=n, side="left") for n in _LEFT_NAMES]
        + [BlockPin(net=long_name, side="right")],
    )
    half_w = _body_half_width(sym.text)
    t = next(t for t in parse_sch(sym.text).texts if t.text == long_name)
    assert t.x < 0, "pick a longer name: this one no longer exercises the negative-anchor case"
    assert t.x + label_width(long_name, t.size_x) <= half_w - 12 + 1e-6


def test_left_side_pin_labels_still_start_inside_the_left_edge():
    sym = _block()
    half_w = _body_half_width(sym.text)
    left = {t.text: t for t in parse_sch(sym.text).texts if t.text in _LEFT_NAMES}
    assert set(left) == set(_LEFT_NAMES), left
    for name, t in left.items():
        assert t.x == pytest.approx(-half_w + 12), name
        assert t.flip == 0, name


def test_pin_connection_boxes_are_untouched_by_the_label_move():
    """Geometry only: every ``B`` pin record still sits one stub outside the body edge."""
    sym = _block()
    half_w = _body_half_width(sym.text)
    for name in _RIGHT_NAMES:
        assert f"{{name={name} dir=out}}" in sym.text
        assert sym.pins[name][0] == pytest.approx(half_w + _STUB)


@requires_xschem
@pytest.mark.slow
def test_rendered_right_side_pin_labels_do_not_cross_the_body_edge(tmp_path: Path):
    """Render the symbol with real xschem: no right-side name's glyphs reach the body border."""
    sym = _block()
    lib = tmp_path / "blocks"
    lib.mkdir()
    (lib / "sar_swdrv_bank.sym").write_text(sym.text)
    sch = tmp_path / "sheet.sch"
    sch.write_text(
        "v {xschem version=3.4.6 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n"
        "C {blocks/sar_swdrv_bank.sym} 0 0 0 0 {name=x1}\n"
    )
    result = render(sch, fmt="svg", outdir=tmp_path, library_path=str(tmp_path), color_nets=False)
    assert result.available and result.image_path is not None, result.log
    svg = result.image_path.read_text()

    # px/unit and origin from the drawing's own extremes: the outermost ink on this sheet is the
    # pin connection box, at |x| = half_w + _STUB + _PIN_HALF.
    half_w = _body_half_width(sym.text)
    reach = half_w + _STUB + _PIN_HALF
    xs = [
        float(v)
        for el in re.findall(r"<(?:path|line|polyline|polygon|rect)\b[^>]*>", svg)
        for run in re.findall(r'\b(?:d|points)="([^"]*)"', el)
        for v in re.findall(r"-?\d+(?:\.\d+)?", run)[0::2]
    ] + [
        float(v)
        for el in re.findall(r"<(?:line|rect)\b[^>]*>", svg)
        for k, v in re.findall(r'\b(x|x1|x2)="(-?[\d.]+)"', el)
    ]
    assert xs, "no drawn geometry in the export"
    scale = (max(xs) - min(xs)) / (2 * reach)
    body_right_px = min(xs) + (reach + half_w) * scale

    seen = 0
    for attrs, content in re.findall(r"<text\b([^>]*)>(.*?)</text>", svg, re.DOTALL):
        if content.strip() not in _RIGHT_NAMES:
            continue
        seen += 1
        box, _ = _text_box(attrs, content)
        assert box[1] <= body_right_px, (
            f"{content.strip()!r} runs to x={box[1]:.1f} px, past the body edge at "
            f"{body_right_px:.1f} px"
        )
    assert seen == len(_RIGHT_NAMES), f"only {seen} right-side names rendered"
