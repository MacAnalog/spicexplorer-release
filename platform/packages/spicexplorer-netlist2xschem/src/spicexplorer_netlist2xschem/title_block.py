"""Draw a title block on a sheet — frame, fields and the date as an INPUT (issue #265).

Every design that keeps a *schematic of record* puts a title block on every sheet. The obvious
thing to reach for, xschem's own ``devices/title.sym``, cannot be that block:

* **Its date is a wall clock.** ``@time_last_modified`` is substituted from the ``.sch`` FILE's
  mtime, so a regeneration that changes no drawing still rewrites every SVG and every PNG with a
  new ``HH:MM:SS``. In a repo that commits its renders, a no-op rebuild churned 146 files.
  ``time_last_modified=`` on the *instance* does not override it — the token is filled from the
  file and the attribute is stored and ignored. (``@path @schname_ext`` likewise prints the
  absolute path of whatever checkout drew the sheet.)
* **Its fields move relative to its own ink as the sheet grows.** The date is drawn ``flip=1``
  (xschem's right-anchor) and, measured on xschem 3.4.4's SVG export, the offset a ``flip=1``
  record gets is a constant number of **pixels** — ``25.5 * size * len(text)`` — while the glyphs
  scale with the export zoom. One 11-character size-0.16 label shifted 44.88 px on sheets 400,
  2000, 8000 and 20000 units wide: 18.5 schematic units on the small sheet, 925 units on the large
  one. So on a large sheet the date lands hundreds of units left of where the symbol puts it —
  on the ``@author`` field, or through the symbol's own ``XSCHEM`` logo. Which pair collides
  depends only on the sheet's px/unit, which is why it reads as sheet-specific.

:func:`add_title_block` owns both problems:

* it **draws the block itself** — ``L`` lines for the frame, ``T`` records for the fields, every one
  of them ``flip=0`` — at sizes and cell widths it computes, so the geometry is the same fraction
  of the sheet at any extent and no field can reach another's cell;
* it takes the **date as an argument**. A sheet is then a function of its inputs: render it today
  and in seven hours and the SVG is byte-identical.

``devices/title.sym`` stays available for anyone who wants xschem's own block — nothing here
removes or rewrites it.

    from spicexplorer_netlist2xschem import add_title_block

    sch = add_title_block(
        sch_text, cell="ota5t", design="dn-000-demo", rev="b3", date="2026-09-21",
        author="A. Designer",
    )
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, replace
from datetime import date as _date
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, overload

from .sch_parser import Schematic, parse_sch

if TYPE_CHECKING:  # pragma: no cover - typing only (emit imports this module at runtime)
    from .emit import SchDocument

__all__ = ["TitleBlock", "add_title_block", "title_block_date", "Corner"]

Corner = Literal["bottom-right", "bottom-left", "top-right", "top-left"]

#: One text line's height in schematic units at ``size = 1``, and the advance of one character as a
#: fraction of it. Both mirror :mod:`render` (``_SCH_LINE_HEIGHT`` / ``_CHAR_ADVANCE``), measured off
#: an xschem export; 0.6 em is Courier's fixed advance and an upper bound for the proportional sans
#: xschem draws, so a cell sized from it is never too NARROW for the glyphs it has to hold.
_SCH_LINE_HEIGHT = 52.0
_CHAR_ADVANCE = 0.6

#: Text sizes at ``scale = 1``: the cell name is the field a reader looks for first.
_CELL_SIZE = 0.25
_FIELD_SIZE = 0.15
#: Gap between a cell's border and the text inside it, and between the drawing and the block.
_PAD = 10.0
_GAP = 40.0
#: The sheet extent the sizes above are drawn for. The block scales linearly with the sheet's own
#: width (see :func:`_auto_scale`), so it keeps the same share of the page — and therefore the same
#: readability — whether the sheet is 400 or 20000 units wide.
_REFERENCE_WIDTH = 1000.0
_MIN_SCALE, _MAX_SCALE = 0.25, 24.0
#: xschem's layer 3: ``#222222`` in the light scheme and ``#cccccc`` in the dark one, so the frame
#: prints as a dark rule on a white sheet rather than the cyan the stock ``devices/title.sym`` uses
#: (owner's ruling 2026-09-21: a sheet of record is read on paper and in PNGs). No ``L`` record this
#: package emits uses layer 3, so the frame is identifiable in an export (``class="l3"``).
_FRAME_LAYER = 3
#: How far a placed symbol's body reaches from its instance anchor. A ``C`` record carries only the
#: anchor; the body lives in the ``.sym``, which needs the symbol library to read — so the extent
#: treats every instance as a box this big. Over-reserving only pushes the block further clear.
_COMPONENT_REACH = 120.0


def _drop_loose_title(text: str, title: str) -> str:
    """Remove the loose ``T {title} x y 0 0 0.4 0.4 {}`` record this package writes, if present.

    The flat emitter simply does not write it when a block is drawn; the CLI's two post-pass lanes
    (``--hierarchical``, ``--annotate-existing``) only see the finished sheet, so the record is taken
    out here instead — otherwise the parent sheet carries its name twice. Only the exact record
    shape this package emits is matched, so a hand-drawn sheet's own caption is never touched.
    """
    pattern = re.compile(
        rf"^T \{{{re.escape(title)}\}} -?[\d.]+ -?[\d.]+ 0 0 0\.4 0\.4 \{{\}}\n?", re.MULTILINE
    )
    return pattern.sub("", text)


def title_block_date(env: dict[str, str] | None = None, today: _date | None = None) -> str:
    """The date to stamp when the caller did not name one: ``SOURCE_DATE_EPOCH`` (UTC) else today.

    ``SOURCE_DATE_EPOCH`` is the reproducible-builds convention, and it is the only environment this
    module reads. Nothing else is sniffed — no ``$USER`` for the author, no ``git describe`` for the
    revision: a sheet is a function of its inputs, and an input taken from the environment is a
    wall clock with extra steps.
    """
    environ = os.environ if env is None else env
    raw = environ.get("SOURCE_DATE_EPOCH", "").strip()
    if raw:
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).date().isoformat()
        except (ValueError, OverflowError, OSError):
            pass
    return (today or _date.today()).isoformat()


@dataclass(frozen=True)
class TitleBlock:
    """The fields of a title block. Every one is an explicit input — nothing is read from a clock."""

    cell: str
    design: str = ""
    rev: str = ""
    date: str = ""
    author: str = ""
    corner: Corner = "bottom-right"
    #: Size multiplier; ``None`` scales the block with the sheet (see :data:`_REFERENCE_WIDTH`).
    scale: float | None = None


def _text_width(text: str, size: float) -> float:
    """Upper bound on the width, in schematic units, of ``text`` drawn at text size ``size``."""
    return len(text) * _SCH_LINE_HEIGHT * size * _CHAR_ADVANCE


def _auto_scale(width: float) -> float:
    return min(_MAX_SCALE, max(_MIN_SCALE, width / _REFERENCE_WIDTH))


def _drawn_extent(sch: Schematic) -> tuple[float, float, float, float]:
    """``(x0, y0, x1, y1)`` covering everything the sheet draws, in schematic units.

    Text is covered by the same width estimate the fields are laid out with; an instance by a box of
    :data:`_COMPONENT_REACH` around its anchor (its body is in the ``.sym``, which is not read here).
    """
    xs: list[float] = []
    ys: list[float] = []
    for w in sch.wires:
        xs += [w.x1, w.x2]
        ys += [w.y1, w.y2]
    for ln in sch.lines:
        xs += [ln.x1, ln.x2]
        ys += [ln.y1, ln.y2]
    for b in sch.boxes:
        xs += [b.x1, b.x2]
        ys += [b.y1, b.y2]
    for a in sch.arcs:
        xs += [a.cx - a.r, a.cx + a.r]
        ys += [a.cy - a.r, a.cy + a.r]
    for poly in sch.polygons:
        xs += [p[0] for p in poly.points]
        ys += [p[1] for p in poly.points]
    for t in sch.texts:
        lines = t.text.splitlines() or [""]
        reach_x = max(_text_width(ln, abs(t.size_x)) for ln in lines)
        reach_y = _SCH_LINE_HEIGHT * abs(t.size_y) * len(lines)
        # A rotated/mirrored record is covered by a square of the larger dimension, as render's own
        # extent box does: over-reserving costs a little margin, never a collision.
        if t.rot == 0 and t.flip == 0:
            xs += [t.x, t.x + reach_x]
            ys += [t.y, t.y + reach_y]
        else:
            reach = max(reach_x, reach_y)
            xs += [t.x - reach, t.x + reach]
            ys += [t.y - reach, t.y + reach]
    for c in sch.components:
        xs += [c.x - _COMPONENT_REACH, c.x + _COMPONENT_REACH]
        ys += [c.y - _COMPONENT_REACH, c.y + _COMPONENT_REACH]
    if not xs or not ys:  # an empty sheet: give the block a page to sit on
        return 0.0, 0.0, _REFERENCE_WIDTH, _REFERENCE_WIDTH / 2
    return min(xs), min(ys), max(xs), max(ys)


def _rows(spec: TitleBlock) -> list[list[tuple[str, float]]]:
    """The block's fields, one row per line, each row a list of ``(text, size)`` cells."""
    rows: list[list[tuple[str, float]]] = [[(spec.cell, _CELL_SIZE)]]
    if spec.design:
        rows.append([(f"design  {spec.design}", _FIELD_SIZE)])
    bottom: list[tuple[str, float]] = []
    if spec.rev:
        bottom.append((f"rev  {spec.rev}", _FIELD_SIZE))
    if spec.date:
        bottom.append((spec.date, _FIELD_SIZE))
    if bottom:
        rows.append(bottom)
    if spec.author:
        rows.append([(f"drawn by  {spec.author}", _FIELD_SIZE)])
    return rows


def _block_records(spec: TitleBlock, extent: tuple[float, float, float, float]) -> list[str]:
    """The ``L`` + ``T`` records of the block, placed clear of ``extent`` at ``spec.corner``."""
    x0, y0, x1, y1 = extent
    scale = spec.scale if spec.scale is not None else _auto_scale(x1 - x0)
    pad, gap = _PAD * scale, _GAP * scale

    rows = _rows(spec)
    heights = [max(size for _, size in row) * _SCH_LINE_HEIGHT * scale + 2 * pad for row in rows]
    # Each cell is its text plus a pad each side; the frame is as wide as the widest row needs.
    cell_widths = [[_text_width(t, s * scale) + 2 * pad for t, s in row] for row in rows]
    width = max(sum(w) for w in cell_widths)
    height = sum(heights)

    right = spec.corner.endswith("right")
    bx0 = (x1 - width) if right else x0
    by0 = (y1 + gap) if spec.corner.startswith("bottom") else (y0 - gap - height)

    out: list[str] = []

    def line(ax: float, ay: float, bx: float, by: float) -> None:
        out.append(f"L {_FRAME_LAYER} {round(ax)} {round(ay)} {round(bx)} {round(by)} {{}}")

    line(bx0, by0, bx0 + width, by0)  # the frame
    line(bx0 + width, by0, bx0 + width, by0 + height)
    line(bx0 + width, by0 + height, bx0, by0 + height)
    line(bx0, by0 + height, bx0, by0)

    y = by0
    for row, row_widths, row_height in zip(rows, cell_widths, heights):
        if y > by0:
            line(bx0, y, bx0 + width, y)  # rule between two rows
        # The last cell of a row keeps its own width and sits at the right edge; any slack goes to
        # the first cell, so a wide row never squeezes the field beside it.
        x = bx0
        for i, ((text, size), cell_width) in enumerate(zip(row, row_widths)):
            if i == len(row) - 1 and len(row) > 1:
                x = bx0 + width - cell_width
                line(x, y, x, y + row_height)  # rule between two cells of one row
            out.append(
                f"T {{{text}}} {round(x + pad)} {round(y + pad)} 0 0 "
                f"{size * scale:g} {size * scale:g} {{}}"
            )
            x += cell_width
        y += row_height
    return out


@overload
def add_title_block(
    sch: str,
    *,
    cell: str,
    design: str = "",
    rev: str = "",
    date: str = "",
    author: str = "",
    corner: Corner = "bottom-right",
    scale: float | None = None,
    replaces_title: str = "",
) -> str: ...


@overload
def add_title_block(
    sch: SchDocument,
    *,
    cell: str,
    design: str = "",
    rev: str = "",
    date: str = "",
    author: str = "",
    corner: Corner = "bottom-right",
    scale: float | None = None,
    replaces_title: str = "",
) -> SchDocument: ...


def add_title_block(
    sch: str | SchDocument,
    *,
    cell: str,
    design: str = "",
    rev: str = "",
    date: str = "",
    author: str = "",
    corner: Corner = "bottom-right",
    scale: float | None = None,
    replaces_title: str = "",
) -> str | SchDocument:
    """Return ``sch`` with a drawn title block added clear of everything already on the sheet.

    ``cell`` is the sheet's own name; ``design``, ``rev``, ``date`` and ``author`` are optional and
    a field that is empty is not drawn (nor is a row reserved for it). ``date`` is a **string the
    caller supplies** — :func:`title_block_date` is the CLI's default (``SOURCE_DATE_EPOCH`` else
    today) and nothing here ever reads a clock or a file's mtime, so two renders of the same sheet
    hours apart are byte-identical.

    ``replaces_title`` names a loose ``T {…} … 0 0 0.4 0.4 {}`` title record (the one the emitter
    writes at the top-left) to take off the sheet first, so the sheet does not carry its name twice.
    Only that exact record shape is matched — a hand-drawn sheet's own caption is never touched.

    ``corner`` puts the block outside the drawn extent, below it (``bottom-*``, the default) or
    above it (``top-*``), flush with the drawing's left or right edge. ``scale`` overrides the
    automatic size, which keeps the block at a fixed share of the sheet's width.

    A ``str`` in gives the ``.sch`` text out; an :class:`~spicexplorer_netlist2xschem.emit.SchDocument`
    in gives a document with the same report and the new text. (A parsed
    :class:`~spicexplorer_netlist2xschem.sch_parser.Schematic` is not accepted: it is a lossy read
    model — draw-only records are dropped — and re-emitting a sheet from one would silently lose
    them.)
    """
    spec = TitleBlock(
        cell=cell, design=design, rev=rev, date=date, author=author, corner=corner, scale=scale
    )
    text = sch if isinstance(sch, str) else sch.text
    if replaces_title:
        text = _drop_loose_title(text, replaces_title)
    records = _block_records(spec, _drawn_extent(parse_sch(text)))
    body = text if text.endswith("\n") else text + "\n"
    out = body + "\n".join(records) + "\n"
    return out if isinstance(sch, str) else replace(sch, text=out)
