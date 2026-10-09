"""Generate an xschem *subcircuit* symbol (``.sym``) for a detected functional block — strategy 1.

The hierarchical mode (:mod:`hierarchy`) turns each recognised block into its own child schematic and
draws it on the parent as a single **block symbol**. xschem has no symbol for our blocks, so we emit
one: a labelled box whose pins are the block's boundary nets, declared ``type=subcircuit`` so that
``xschem -n`` descends into the matching child ``.sch`` and the parent re-netlists to the original flat
circuit.

The emitted format mirrors a stock xschem subcircuit symbol (``devices/verilog_delay.sym``): a global
``G {type=subcircuit format="@name @pinlist @symname" template="name=x1"}`` block, the body drawn as
``L`` lines, and one pin per boundary net as a ``B`` connection box ``{name=<net> dir=<in|out|inout>}``.
A pin's connection point is the box centre — :func:`generate_block_symbol` returns those points
(symbol-local) so the parent emitter can drop a net label exactly on each instantiated pin. xschem
matches a symbol pin to the child's like-named port, so the pin **names** carry the wiring; we keep the
child ``.sch`` port labels identical.

**Functional icons.** The same generator draws the block's *functional* symbol — an opamp as a
triangle, a comparator as a triangle with a clock wedge, an ADC as a staircase — by replacing the
four body ``L`` lines with a glyph from
:mod:`~spicexplorer_netlist2xschem.symbols.analog_icons` and changing **nothing else**: every ``B``
pin record, every stub and every pin label is the one the plain block symbol would have emitted, so
an icon cannot move, rename or reorder a pin, and the cell re-netlists identically (asserted, both
by byte comparison and through real xschem). The icon lives in the **per-cell** ``.sym`` — a shared
icon file cannot be placed, because xschem binds a ``type=subcircuit`` symbol's child schematic to
the symbol FILE's basename (the reason is spelled out in the icon library's docstring).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from .geometry import snap
from .symbols import analog_icons
from .symbols.analog_icons import IconFrame, IconPin, Segment

__all__ = [
    "BlockPin",
    "BlockSymbol",
    "generate_block_symbol",
    "generate_icon_symbol",
    "clean_symbol",
    "label_width",
]

# A device symbol's parameter-value *display* text — ``T {@model}``, ``T {w=@w}``, ``T {l=@l}``,
# ``T {ng=@ng}``, ``T {m=@m}``, ``T {@value}``. Matching these (but never ``@name``, ``@#…:net_name``,
# ``@spice_get_current``) lets :func:`clean_symbol` drop the sizing clutter while keeping the device's
# instance name, pins, body and the ``K``-block (so it still netlists).
_PARAM_DISPLAY = re.compile(r"@(model|value|w|l|ng|m)\b")


def clean_symbol(text: str) -> str:
    """Return ``text`` with the parameter-value *display* (``T``) records removed.

    A "no-params" variant of a device symbol: identical body, pins and ``K``-block (so a device drawn
    with it still wires and netlists exactly the same — the instance keeps its full ``model``/``w``/``l``
    attributes), but it does not draw the ``w=…``/``l=…``/``model`` text that clutters a topology
    schematic. Only complete single-line ``T`` records that show a parameter are dropped; multi-line
    records and the ``@name`` label are kept untouched.
    """
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        is_param_text = (
            s.startswith("T ")
            and s.count("{") == s.count("}")  # a complete single-line T record
            and "@name" not in s
            and _PARAM_DISPLAY.search(s) is not None
        )
        if not is_param_text:
            out.append(line)
    return "\n".join(out) + "\n"


_PIN_PITCH = 40  # vertical/horizontal spacing between adjacent pins on one side
_STUB = 20  # how far a pin's connection point sits outside the body edge
_MARGIN = 40  # body half-extent beyond the outermost pin on a side
_PIN_LAYER = 5  # xschem pin layer (red), as used by every device symbol
_BODY_LAYER = 4  # device-body layer (green)
_TEXT_LAYER = 4
_PIN_HALF = 2.5  # half-size of a pin connection box

_DIR_BY_SIDE = {"left": "in", "right": "out", "top": "inout", "bottom": "inout"}

_PIN_TEXT_SIZE = 0.16  # the size the pin-name ``T`` records are drawn at
_LABEL_INSET = 12  # how far a pin name is held clear of the body edge it belongs to
#: One text line's height in schematic units at ``size = 1``, and the per-character advance as a
#: fraction of it. Both mirror :mod:`render` (``_SCH_LINE_HEIGHT`` / ``_CHAR_ADVANCE``), measured
#: off an xschem export: 0.6 em is Courier's fixed advance and an upper bound for the proportional
#: sans xschem draws, so a width computed from it is never too SHORT. Kept local rather than
#: imported: a symbol is emitted with no renderer in sight, and ``render`` depends on the parser,
#: not the other way round.
_SCH_LINE_HEIGHT = 52.0
_CHAR_ADVANCE = 0.6


def label_width(label: str, size: float = _PIN_TEXT_SIZE) -> float:
    """Upper bound on the width, in schematic units, of ``label`` drawn at text size ``size``."""
    return len(label) * _SCH_LINE_HEIGHT * size * _CHAR_ADVANCE


@dataclass(frozen=True)
class BlockPin:
    """One boundary net of a block, as a symbol pin: which side it sits on and its signal direction.

    ``net`` is the host net the pin connects to (the pin's ``name=`` — what xschem matches to the child
    subckt port, so it must stay the net). ``label`` is the **display** text drawn beside the pin; when
    empty it falls back to ``net``. Setting it to the template's functional port name (``out`` /
    ``ref_in`` / ``supply`` / …) lets a block read like a datasheet pinout while still netlisting by net."""

    net: str
    side: str  # "left" | "right" | "top" | "bottom"
    direction: str = ""  # in | out | inout; defaults from the side when empty
    label: str = ""  # display text drawn at the pin; defaults to ``net`` when empty


@dataclass(frozen=True)
class BlockSymbol:
    """A generated block symbol: its ``.sym`` text and each pin's symbol-local connection point."""

    name: str
    text: str
    pins: dict[str, tuple[int, int]]  # net name -> (x, y) connection point in symbol-local coords
    #: The functional icon drawn in the body (``""`` for the plain box), and anything the glyph
    #: declined to draw — an input mark it could not place from the pin names, say. A note is a
    #: *drawing* defect the netlist gates cannot see, so it is surfaced, never swallowed.
    icon: str = ""
    warnings: tuple[str, ...] = field(default=())


def _side_positions(n: int, pitch: int = _PIN_PITCH) -> list[int]:
    """``n`` evenly-spaced, grid-snapped offsets centred on 0 (for pins along one side)."""
    if n == 0:
        return []
    return [snap(int((i - (n - 1) / 2) * pitch)) for i in range(n)]


@dataclass(frozen=True)
class _Layout:
    """Everything about a block symbol that is fixed before the body is drawn.

    Split out so the plain box and every functional icon are laid out by the SAME code: the pin
    records, stubs, labels and connection points are computed once, and only the body lines differ.
    That is the structural guarantee behind "an icon cannot move a pin" — it is not a promise a
    reviewer has to check, it is the only body the generator has.
    """

    half_w: int
    half_h: int
    pin_lines: tuple[str, ...]
    coords: dict[str, tuple[int, int]]
    icon_pins: tuple[IconPin, ...]


def _scaled(value: int, scale: float) -> int:
    """A geometry constant at ``scale`` — exactly itself at 1.0, so the default path is unchanged."""
    return value if scale == 1.0 else max(5, snap(value * scale))


def _layout(name: str, pins: list[BlockPin], scale: float) -> _Layout:
    """Side assignment, body size, pin records, stubs and labels — the icon-independent half.

    ``scale`` multiplies the geometry constants (pitch, stub, margin, the minimum extents) and
    nothing else: the pin ORDER, the sides and every ``name=``/``dir=`` stay exactly what the pin
    list says. It exists because the body is sized from the PIN COUNT — a 7-pin block beside a
    56-pin one comes out at a fraction of the sheet's width, and a glyph has to stay legible there.
    """
    sides: dict[str, list[BlockPin]] = {"left": [], "right": [], "top": [], "bottom": []}
    for p in pins:
        sides.get(p.side, sides["bottom"]).append(p)

    pitch = _scaled(_PIN_PITCH, scale)
    stub = _scaled(_STUB, scale)
    margin = _scaled(_MARGIN, scale)
    label_inset = _LABEL_INSET if scale == 1.0 else max(4, round(_LABEL_INSET * scale))

    n_vert = max(len(sides["left"]), len(sides["right"]), 1)
    n_horz = max(len(sides["top"]), len(sides["bottom"]), 1)
    half_h = max(_scaled(60, scale), ((n_vert - 1) * pitch) // 2 + margin)
    half_w = max(
        _scaled(80, scale),
        ((n_horz - 1) * pitch) // 2 + margin,
        _scaled(len(name) * 4 + 24, scale),
    )
    # A body is never TALLER than it is wide. With nine or more pins on one vertical side only
    # the height grew, and past roughly square the parent reaches the block with VERTICAL stubs
    # instead of horizontal ones -- at which point two net labels land on top of each other and
    # read as one net. The equivalence gate catches the merge, but only after a sheet nobody can
    # read has been drawn; widening the body is what keeps the stubs horizontal at any pin count.
    half_w = max(half_w, half_h)
    half_h, half_w = snap(half_h), snap(half_w)

    pin_lines: list[str] = []
    coords: dict[str, tuple[int, int]] = {}
    icon_pins: list[IconPin] = []

    for side, plist in sides.items():
        offsets = _side_positions(len(plist), pitch)
        for p, off in zip(plist, offsets):
            if side == "left":
                cx, cy, ex, ey = -half_w - stub, off, -half_w, off
            elif side == "right":
                cx, cy, ex, ey = half_w + stub, off, half_w, off
            elif side == "top":
                cx, cy, ex, ey = off, -half_h - stub, off, -half_h
            else:  # bottom
                cx, cy, ex, ey = off, half_h + stub, off, half_h
            direction = p.direction or _DIR_BY_SIDE.get(side, "inout")
            coords[p.net] = (cx, cy)
            pin_lines.append(
                f"B {_PIN_LAYER} {cx - _PIN_HALF} {cy - _PIN_HALF} {cx + _PIN_HALF} "
                f"{cy + _PIN_HALF} {{name={p.net} dir={direction}}}"
            )
            pin_lines.append(f"L {_BODY_LAYER} {ex} {ey} {cx} {cy} {{}}")  # stub
            # pin label (the template's functional name when given, else the net), drawn just inside
            # the body edge. The *connection* name stays the net (the ``B`` record's ``name=``) so
            # xschem still matches the pin to the child subckt port — only the drawn text changes.
            #
            # xschem text is anchored at its LEFT edge, so "12 units in from the edge" only holds on
            # the left side: a right-side name used to START 12 units inside the body and run
            # OUTWARD, its first glyph struck through by the border (issue #266, seen on 62 of 63
            # block symbols of one design). The label is therefore placed so that it ENDS 12 units
            # inside the right edge, from the width estimate above.
            #
            # xschem's own right-anchor (``flip=1``, what ``devices/title.sym`` uses for its date)
            # cannot do this: measured on xschem 3.4.4's SVG export, the anchor offset it applies is
            # a CONSTANT NUMBER OF PIXELS -- 25.5 * size * len(text) px -- while the glyphs scale
            # with the export zoom. One 11-character size-0.16 label shifted 44.9 px on every sheet:
            # 18.5 schematic units on a 400-unit sheet but 925 units on a 20000-unit one. It is
            # right-anchored only at ~1 px/unit, and lands far left of its anchor on anything wider.
            # ``floor``, not ``int``: a name long enough to start left of the symbol origin gets a
            # NEGATIVE x, and ``int`` truncates toward zero — which moves that label back out
            # towards the border it is being held off.
            label = p.label or p.net
            if side == "right":
                lx = math.floor(ex - label_inset - label_width(label))
            elif side == "left":
                lx = math.floor(ex + label_inset)
            else:
                lx = math.floor(ex)
            pin_lines.append(
                f"T {{{label}}} {lx} {ey} 0 0 {_PIN_TEXT_SIZE} {_PIN_TEXT_SIZE} "
                f"{{layer={_TEXT_LAYER}}}"
            )
            icon_pins.append(
                IconPin(net=p.net, label=p.label or p.net, side=side, x=cx, y=cy, ex=ex, ey=ey)
            )

    return _Layout(
        half_w=half_w,
        half_h=half_h,
        pin_lines=tuple(pin_lines),
        coords=coords,
        icon_pins=tuple(icon_pins),
    )


def _line(seg: Segment) -> str:
    """One glyph/body segment as an xschem ``L`` record on the device-body layer."""
    x1, y1, x2, y2 = seg
    return f"L {_BODY_LAYER} {x1} {y1} {x2} {y2} {{}}"


def generate_block_symbol(
    name: str,
    pins: list[BlockPin],
    *,
    icon: str | None = None,
    scale: float | None = None,
) -> BlockSymbol:
    """Build the ``.sym`` for a block named ``name`` with the given boundary ``pins``.

    Inputs land on the left, outputs on the right, supplies/other on the bottom — the conventional
    analog block pinout — and the body grows to fit the busiest side. Returns the text plus the
    symbol-local connection point of every pin (the parent drops a net label there).

    ``icon`` names a functional glyph from
    :mod:`~spicexplorer_netlist2xschem.symbols.analog_icons` (``"comparator"``, ``"ldo"``, or a
    scaled spec such as ``"ldo@1.6"``) to draw **in place of the plain rectangle**. Nothing else
    about the symbol changes: at the same scale the ``B`` pin records, stubs and labels are
    byte-identical to the plain block symbol's, and the ``G`` block still carries the stock
    ``@symname`` format, so the cell netlists exactly as before. ``scale`` overrides the icon's own
    default scale (see :class:`~spicexplorer_netlist2xschem.symbols.analog_icons.Icon`).
    """
    chosen = analog_icons.parse_spec(icon) if icon else None
    effective_scale = scale if scale is not None else (chosen[1] if chosen is not None else 1.0)
    geom = _layout(name, pins, effective_scale)

    notes: tuple[str, ...] = ()
    if chosen is None:
        body = [
            _line(seg)
            for seg in analog_icons.box(geom.half_w, geom.half_h)  # the plain rectangle
        ]
    else:
        segments, notes = analog_icons.draw(
            chosen[0],
            IconFrame(
                half_w=geom.half_w,
                half_h=geom.half_h,
                pins=geom.icon_pins,
                scale=effective_scale,
            ),
        )
        body = [_line(seg) for seg in segments]

    header = "v {xschem version=3.4.6 file_version=1.2}"
    # `@params` expands the instance's own `params=` attribute. Without it the symbol netlists
    # the call as `x1 <nets> <symname>` with NO parameters -- every sized device silently back at
    # its model default, on a sheet that looks correct. The template deliberately does NOT declare
    # `params=`: an EMPTY attribute in the template makes xschem emit a malformed call and the
    # hierarchy stops round-tripping (measured), while an absent one expands to nothing.
    glob = 'G {type=subcircuit\nformat="@name @pinlist @symname @params"\ntemplate="name=x1"}'
    name_label = (
        f"T {{{name}}} {-geom.half_w + 8} {-geom.half_h + 8} 0 0 0.3 0.3 {{layer={_TEXT_LAYER}}}"
    )
    inst_label = (
        f"T {{@name}} {-geom.half_w + 8} {geom.half_h - 24} 0 0 0.2 0.2 {{layer={_TEXT_LAYER}}}"
    )
    lines = [header, glob, "V {}", "S {}", "E {}", *body, *geom.pin_lines, name_label, inst_label]
    return BlockSymbol(
        name=name,
        text="\n".join(lines) + "\n",
        pins=geom.coords,
        icon=chosen[0].name if chosen is not None else "",
        warnings=notes,
    )


def generate_icon_symbol(
    name: str, pins: list[BlockPin], icon: str, *, scale: float | None = None
) -> BlockSymbol:
    """The **per-cell** functional-icon symbol for a block: :func:`generate_block_symbol` with a glyph.

    This is the call a design's own generator makes for a cell it has recognised itself (the shared
    icon file it cannot place — see the icon library's docstring)::

        sym = generate_icon_symbol("sar_cmp", pins, "comparator")
        (out / "sar_cmp.sym").write_text(sym.text)   # beside sar_cmp.sch

    ``sym.warnings`` names anything the glyph declined to draw (an input mark whose pins it could
    not identify); ``sym.pins`` is the connection point of every pin, for the parent's net labels.
    """
    return generate_block_symbol(name, pins, icon=icon, scale=scale)
