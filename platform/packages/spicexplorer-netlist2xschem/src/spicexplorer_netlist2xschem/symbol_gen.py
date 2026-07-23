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
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .geometry import snap

__all__ = ["BlockPin", "BlockSymbol", "generate_block_symbol", "clean_symbol"]

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


def _side_positions(n: int) -> list[int]:
    """``n`` evenly-spaced, grid-snapped offsets centred on 0 (for pins along one side)."""
    if n == 0:
        return []
    return [snap(int((i - (n - 1) / 2) * _PIN_PITCH)) for i in range(n)]


def generate_block_symbol(name: str, pins: list[BlockPin]) -> BlockSymbol:
    """Build the ``.sym`` for a block named ``name`` with the given boundary ``pins``.

    Inputs land on the left, outputs on the right, supplies/other on the bottom — the conventional
    analog block pinout — and the body grows to fit the busiest side. Returns the text plus the
    symbol-local connection point of every pin (the parent drops a net label there)."""
    sides: dict[str, list[BlockPin]] = {"left": [], "right": [], "top": [], "bottom": []}
    for p in pins:
        sides.get(p.side, sides["bottom"]).append(p)

    n_vert = max(len(sides["left"]), len(sides["right"]), 1)
    n_horz = max(len(sides["top"]), len(sides["bottom"]), 1)
    half_h = max(60, ((n_vert - 1) * _PIN_PITCH) // 2 + _MARGIN)
    half_w = max(80, ((n_horz - 1) * _PIN_PITCH) // 2 + _MARGIN, len(name) * 4 + 24)
    half_h, half_w = snap(half_h), snap(half_w)

    body = [
        f"L {_BODY_LAYER} {-half_w} {-half_h} {half_w} {-half_h} {{}}",
        f"L {_BODY_LAYER} {half_w} {-half_h} {half_w} {half_h} {{}}",
        f"L {_BODY_LAYER} {half_w} {half_h} {-half_w} {half_h} {{}}",
        f"L {_BODY_LAYER} {-half_w} {half_h} {-half_w} {-half_h} {{}}",
    ]
    pin_lines: list[str] = []
    coords: dict[str, tuple[int, int]] = {}

    for side, plist in sides.items():
        offsets = _side_positions(len(plist))
        for p, off in zip(plist, offsets):
            if side == "left":
                cx, cy, ex, ey = -half_w - _STUB, off, -half_w, off
            elif side == "right":
                cx, cy, ex, ey = half_w + _STUB, off, half_w, off
            elif side == "top":
                cx, cy, ex, ey = off, -half_h - _STUB, off, -half_h
            else:  # bottom
                cx, cy, ex, ey = off, half_h + _STUB, off, half_h
            direction = p.direction or _DIR_BY_SIDE.get(side, "inout")
            coords[p.net] = (cx, cy)
            pin_lines.append(
                f"B {_PIN_LAYER} {cx - _PIN_HALF} {cy - _PIN_HALF} {cx + _PIN_HALF} "
                f"{cy + _PIN_HALF} {{name={p.net} dir={direction}}}"
            )
            pin_lines.append(f"L {_BODY_LAYER} {ex} {ey} {cx} {cy} {{}}")  # stub
            # pin label (the template's functional name when given, else the net), nudged just inside the
            # body edge. The *connection* name stays the net (the ``B`` record's ``name=``) so xschem
            # still matches the pin to the child subckt port — only the drawn text changes.
            lx = ex + (12 if side == "left" else -12 if side == "right" else 0)
            pin_lines.append(
                f"T {{{p.label or p.net}}} {lx} {ey} 0 0 0.16 0.16 {{layer={_TEXT_LAYER}}}"
            )

    header = "v {xschem version=3.4.6 file_version=1.2}"
    glob = (
        'G {type=subcircuit\n'
        'format="@name @pinlist @symname"\n'
        'template="name=x1"}'
    )
    name_label = f"T {{{name}}} {-half_w + 8} {-half_h + 8} 0 0 0.3 0.3 {{layer={_TEXT_LAYER}}}"
    inst_label = f"T {{@name}} {-half_w + 8} {half_h - 24} 0 0 0.2 0.2 {{layer={_TEXT_LAYER}}}"
    lines = [header, glob, "V {}", "S {}", "E {}", *body, *pin_lines, name_label, inst_label]
    return BlockSymbol(name=name, text="\n".join(lines) + "\n", pins=coords)
