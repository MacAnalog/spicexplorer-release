"""The geometry a functional-icon glyph is drawn against, plus the shared drawing primitives.

A glyph never invents a size. It receives an :class:`IconFrame` — the body box
:func:`~spicexplorer_netlist2xschem.symbol_gen.generate_block_symbol` already computed from the pin
list, plus every pin with the side it sits on, its connection point and the point where its stub
meets the body edge — and returns line segments inside that box. That is what makes one glyph fit a
3-pin comparator and a 56-pin array: the box grows with the pin count and the drawing grows with it.

Three rules the primitives here exist to keep:

* **Only ``L`` (line) records.** Every consumer of a generated ``.sym`` reads lines: xschem, the
  Studio viewer's TS parser, and ``xvport``'s symbol port to Virtuoso. Arcs and polygons are read by
  some and sampled/approximated by others, so a glyph that needs a curve draws it as a polyline.
  Everything stays ASCII (a ``+``/``-`` mark is *drawn*, never typed, so no Unicode minus reaches a
  SKILL file or a cairo export).
* **A pin is never left hanging in space.** The plain block symbol is a rectangle, so every stub ends
  on a drawn edge. A glyph is not a rectangle, so :func:`leads` casts a ray inward from each pin's
  edge point and draws the short lead that lands it on the glyph's outline.
* **A mark is placed BESIDE the pin it belongs to, read from the pin list** (:func:`plus_minus`,
  :func:`clock_marks`). Never at a fixed "upper third": a ``.subckt`` header that lists ``clk vin
  vip`` puts the inverting input on top, and a hard-coded ``+`` there is a *wrong* drawing that
  re-netlists perfectly. When the inputs cannot be identified unambiguously, no mark is drawn and
  the reason is returned as a note.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "Segment",
    "IconPin",
    "IconFrame",
    "box",
    "polyline",
    "staircase",
    "leads",
    "plus_minus",
    "clock_marks",
    "wedge",
    "mark_anchor",
    "label_width",
]

#: One drawn line: ``(x1, y1, x2, y2)`` in symbol-local coordinates (xschem's y grows *downward*).
Segment = tuple[int, int, int, int]


def _token(text: str) -> str:
    """A pin name normalised for role matching: lowercase, runs of punctuation → ``_``."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


# A non-inverting / inverting input, by the name the *pin* carries — its contract port name when the
# producer gave one (``in_p``), else the host net (``vip``). Exact tokens only: a suffix rule such as
# "ends in m or n" reads ``vcm`` as the inverting input, which is precisely the silent mis-drawing
# these tables exist to prevent. ``vin`` is listed as inverting because it only ever *marks* anything
# when a non-inverting partner is found too (see :func:`plus_minus`) — a lone ``vin`` marks nothing.
_PLUS_TOKENS = frozenset(
    {
        "p",
        "plus",
        "pos",
        "vp",
        "ip",
        "in_p",
        "inp",
        "in_pos",
        "inpos",
        "in_plus",
        "inplus",
        "vip",
        "vinp",
        "vin_p",
        "v_p",
        "noninv",
        "non_inv",
        "noninverting",
        "non_inverting",
    }
)
_MINUS_TOKENS = frozenset(
    {
        "n",
        "m",
        "minus",
        "neg",
        "vn",
        "vm",
        "in_n",
        "inn",
        "inm",
        "in_neg",
        "inneg",
        "in_minus",
        "inminus",
        "vin",
        "vim",
        "vinn",
        "vinm",
        "vin_n",
        "v_n",
        "inv",
        "inverting",
    }
)
# A clock / control pin: the thing a comparator is strobed by and a sampler is closed by.
_CLOCK_TOKENS = frozenset(
    {
        "clk",
        "clkb",
        "clk_b",
        "clkn",
        "ck",
        "ckb",
        "clock",
        "phi",
        "phi1",
        "phi2",
        "phib",
        "strobe",
        "latch",
        "sample",
        "samp",
        "smp",
        "s_h",
        "sh",
    }
)


@dataclass(frozen=True)
class IconPin:
    """One pin of the generated symbol, as a glyph sees it.

    ``net`` is the connection name (what xschem matches to the child subckt port — a glyph must never
    change it), ``label`` the text drawn beside it, ``side`` one of ``left``/``right``/``top``/
    ``bottom``. ``(x, y)`` is the connection point *outside* the body; ``(ex, ey)`` is where the pin's
    stub meets the body edge — the point a glyph lead starts from.
    """

    net: str
    label: str
    side: str
    x: int
    y: int
    ex: int
    ey: int

    @property
    def token(self) -> str:
        """The drawn name, normalised for role matching (``In_P`` → ``in_p``)."""
        return _token(self.label or self.net)

    @property
    def is_clock(self) -> bool:
        """True when this pin's name is a clock / strobe / sample control."""
        return self.token in _CLOCK_TOKENS


@dataclass(frozen=True)
class IconFrame:
    """The body box a glyph draws in, with the pins that sit on it.

    ``half_w``/``half_h`` are the generated body half-extents (the box the plain block symbol would
    have drawn), ``scale`` the per-icon scale that produced them — carried so a glyph can size a
    detail in *drawing* units rather than in fractions of the box when it needs to.
    """

    half_w: int
    half_h: int
    pins: tuple[IconPin, ...]
    scale: float = 1.0

    def on(self, side: str) -> tuple[IconPin, ...]:
        """The pins on one side, in the order the symbol generator placed them."""
        return tuple(p for p in self.pins if p.side == side)

    def fx(self, fraction: float) -> int:
        """An x coordinate given as a fraction of the half-width (``-1`` … ``1``)."""
        return round(self.half_w * fraction)

    def fy(self, fraction: float) -> int:
        """A y coordinate given as a fraction of the half-height (``-1`` … ``1``, y downward)."""
        return round(self.half_h * fraction)

    def unit(self, size: float) -> int:
        """A drawing length in *scaled* units — a mark that must stay legible at any box size."""
        return max(4, round(size * self.scale))


def box(half_w: int, half_h: int) -> tuple[Segment, ...]:
    """The four sides of a rectangle — the plain block body, and many glyphs' outline."""
    return (
        (-half_w, -half_h, half_w, -half_h),
        (half_w, -half_h, half_w, half_h),
        (half_w, half_h, -half_w, half_h),
        (-half_w, half_h, -half_w, -half_h),
    )


def polyline(points: list[tuple[int, int]], *, close: bool = False) -> tuple[Segment, ...]:
    """Consecutive points joined by lines (optionally closed back to the first)."""
    pts = list(points) + ([points[0]] if close and len(points) > 2 else [])
    return tuple((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(len(pts) - 1))


def staircase(x0: int, y0: int, x1: int, y1: int, steps: int = 4) -> tuple[Segment, ...]:
    """A quantised ramp from ``(x0, y0)`` to ``(x1, y1)`` — the ADC/DAC staircase.

    Tread then riser, ``steps`` times: the drawing that says "this signal is a code, not a
    continuum". It is a polyline, so it survives every consumer that reads only ``L`` records.
    """
    pts: list[tuple[int, int]] = [(x0, y0)]
    for i in range(1, steps + 1):
        xi = round(x0 + (x1 - x0) * i / steps)
        yi = round(y0 + (y1 - y0) * i / steps)
        pts.append((xi, pts[-1][1]))  # tread
        pts.append((xi, yi))  # riser
    return polyline(pts)


#: The inset the emitter holds a pin label off its body edge (mirrors ``symbol_gen._LABEL_INSET``;
#: a mark steps past the label, so it is measured from the same place).
_LABEL_INSET = 12

_INWARD: dict[str, tuple[int, int]] = {
    "left": (1, 0),
    "right": (-1, 0),
    "top": (0, 1),
    "bottom": (0, -1),
}


def _hit(px: float, py: float, dx: float, dy: float, seg: Segment, reach: float) -> float | None:
    """Distance along the ray ``(px,py) + t(dx,dy)`` at which it crosses ``seg`` (else ``None``)."""
    x1, y1, x2, y2 = seg
    sx, sy = x2 - x1, y2 - y1
    denom = dx * sy - dy * sx
    if abs(denom) < 1e-9:
        return None  # parallel (a collinear overlap needs no lead — the pin is already on the line)
    t = ((x1 - px) * sy - (y1 - py) * sx) / denom
    u = ((x1 - px) * dy - (y1 - py) * dx) / denom
    if t < -1e-6 or t > reach or u < -1e-6 or u > 1 + 1e-6:
        return None
    return t


def leads(frame: IconFrame, outline: tuple[Segment, ...]) -> tuple[Segment, ...]:
    """Short lines joining each pin's body-edge point to the glyph's outline.

    The plain block symbol is a box, so every stub lands on a drawn edge. A triangle does not reach
    the box corners, so without this a pin's stub would end in empty space and the sheet would read
    as a broken connection (it netlists fine either way — which is exactly why it has to be *drawn*
    right). A ray is cast inward from the edge point; the lead runs to the nearest crossing. A pin
    whose ray meets nothing gets a short tick inward, so it still reads as entering the glyph.
    """
    out: list[Segment] = []
    reach = 2 * (frame.half_w + frame.half_h)
    tick = frame.unit(24)
    for pin in frame.pins:
        dx, dy = _INWARD.get(pin.side, (0, 0))
        if dx == 0 and dy == 0:
            continue
        hits = [
            t for t in (_hit(pin.ex, pin.ey, dx, dy, s, reach) for s in outline) if t is not None
        ]
        distance = min(hits) if hits else float(tick)
        if distance < 1.0:
            continue  # the pin already sits on the glyph (a triangle's own vertical edge)
        out.append((pin.ex, pin.ey, round(pin.ex + dx * distance), round(pin.ey + dy * distance)))
    return tuple(out)


def plus_minus(frame: IconFrame) -> tuple[tuple[Segment, ...], tuple[str, ...]]:
    """The ``+`` / ``-`` input marks, each drawn beside the pin it belongs to.

    Both marks are drawn only when exactly one pin names itself non-inverting **and** exactly one
    names itself inverting. Anything else — no match, two matches, one of the two missing — draws
    nothing and returns a note saying so, because an input mark on the wrong pin is a drawing error
    a netlist gate can never catch.
    """
    plus = [p for p in frame.pins if p.token in _PLUS_TOKENS]
    minus = [p for p in frame.pins if p.token in _MINUS_TOKENS]
    if len(plus) != 1 or len(minus) != 1:
        named = ", ".join(sorted(p.token for p in frame.pins)) or "(no pins)"
        return (), (
            f"no +/- input marks: need exactly one non-inverting and one inverting pin name, "
            f"found {len(plus)} and {len(minus)} in [{named}]",
        )
    segs: list[Segment] = []
    arm = frame.unit(9)
    for pin, is_plus in ((plus[0], True), (minus[0], False)):
        cx, cy = mark_anchor(frame, pin, arm)
        segs.append((cx - arm, cy, cx + arm, cy))
        if is_plus:
            segs.append((cx, cy - arm, cx, cy + arm))
    return tuple(segs), ()


def label_width(text: str) -> int:
    """How wide a generated pin label draws, from the emitter's OWN estimate.

    Delegates to :func:`spicexplorer_netlist2xschem.symbol_gen.label_width` — the same function
    that decides where the label is placed (a right-side name is anchored so that it *ends* an
    inset inside the body, #266/#270). A mark placed from a second, private estimate would drift
    off the text the moment that one changed. Imported inside the call because ``symbol_gen``
    imports this package.
    """
    from ...symbol_gen import label_width as _emitter_label_width

    return round(_emitter_label_width(text))


def mark_anchor(frame: IconFrame, pin: IconPin, half: int) -> tuple[int, int]:
    """Where a mark of half-size ``half`` sits for one pin: on that pin's own row, past its label.

    The generated pin label is anchored at the body edge and reads inward, so a mark at a fixed
    inset lands *on* the text (measured: a ``-`` vanished under the cell-name label), and a mark
    nudged vertically instead sits halfway between two pins and reads as belonging to either.
    Staying on the pin's row and stepping past its label is what keeps "this mark belongs to THIS
    pin" unambiguous at any pin count.
    """
    inset = frame.unit(_LABEL_INSET) + label_width(pin.label or pin.net) + half + frame.unit(6)
    drop = frame.unit(4)  # a label's text box hangs just below its anchor
    if pin.side == "left":
        return pin.ex + inset, pin.ey + drop
    if pin.side == "right":
        return pin.ex - inset, pin.ey + drop
    if pin.side == "top":
        return pin.ex, pin.ey + frame.unit(16) + half
    return pin.ex, pin.ey - frame.unit(6) - half


def wedge(frame: IconFrame, pin: IconPin) -> tuple[Segment, ...]:
    """The clock triangle for one pin: a ``>`` on the pin's row, pointing the way the signal enters.

    Placed by the same rule as the input marks — past that pin's label, on its row — so it reads as
    *that* pin's mark and never lands on the text.
    """
    size = frame.unit(10)
    dx, dy = _INWARD.get(pin.side, (1, 0))
    cx, cy = mark_anchor(frame, pin, size)
    tip = (cx + dx * size, cy + dy * size)
    bx, by = -dy, dx  # the back edge is perpendicular to the pin's own direction
    back_a = (cx - dx * size + bx * size, cy - dy * size + by * size)
    back_b = (cx - dx * size - bx * size, cy - dy * size - by * size)
    return polyline([back_a, tip, back_b])


def clock_marks(frame: IconFrame) -> tuple[tuple[Segment, ...], tuple[str, ...]]:
    """A clock wedge at every pin whose name says it is a clock — or a note when there is none.

    Every marked pin carries its own wedge, so a differential clock pair (``clk``/``clkb``) is marked
    twice and stays unambiguous; a cell whose control pin is named something else is left unmarked
    rather than guessed at.
    """
    clocks = [p for p in frame.pins if p.is_clock]
    if not clocks:
        named = ", ".join(sorted(p.token for p in frame.pins)) or "(no pins)"
        return (), (f"no clock mark: no pin names a clock in [{named}]",)
    segs: list[Segment] = []
    for pin in clocks:
        segs.extend(wedge(frame, pin))
    return tuple(segs), ()
