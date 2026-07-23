"""Emit a SKILL ``.il`` that rebuilds an xschem ``.sym`` as a Virtuoso symbol cellview.

A ``.sym`` is the same record grammar as a ``.sch`` (parsed with
:func:`~spicexplorer_netlist2xschem.sch_parser.parse_sch`), drawn instead of instantiated:

* ``L``/``P`` body graphics → ``dbCreateLine``/``dbCreatePolygon`` on ``("device" "drawing")``;
* ``A`` arcs → a full 360° sweep becomes ``dbCreateEllipse``; a partial arc is polyline-sampled
  (no headless-safe arc primitive is verified on this install);
* ``B`` on layer 5 → a real terminal: net + term + pin figure on ``("pin" "drawing")``
  (a live-verified recipe);
  other-layer ``B`` records → plain ``dbCreateRect`` graphics;
* ``T`` texts → ``@symname``/``@name`` become the native ``logical label`` (``[@partName]``)
  and ``instance label`` (``[@instanceName]``) via ``schCreateSymbolLabel``; a text equal to a
  pin name becomes that pin's native ``pin name`` label; anything else is a plain drawing label;
* the pin order (xschem's ``@pinlist``) is preserved as ``termOrder``, and a selection box on
  ``("instance" "drawing")`` wraps the whole drawing.

Because the ported symbol's pin positions are *scaled copies* of the xschem ones, hierarchical
schematics that instantiate these symbols keep their geometry meaningful — this is what makes
exact wire-mode porting possible for subcircuit instances.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from ..sch_parser import Schematic, parse_sch
from ..sym_library import parse_symbol
from .xform import DEFAULT_SCALE, to_cadence

__all__ = ["SymbolEmitResult", "emit_symbol_il"]

_NAME_OK = re.compile(r"[^A-Za-z0-9_!]")
_PIN_LAYER = 5
_ARC_SEGMENTS = 24
_DIRECTION = {"in": "input", "out": "output", "inout": "inputOutput"}
# xschem text `size` → Cadence label height (user units): empirical cap height ≈ 40 units/size.
_TEXT_HEIGHT_UNITS = 40.0


@dataclass
class SymbolEmitResult:
    """The emitted ``.il`` plus the terminal expectations ``--verify`` diffs against."""

    il: str
    terms: dict[str, str] = field(default_factory=dict)  # term name -> direction
    term_order: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _s(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _sanitize(name: str, *, prefix: str) -> str:
    clean = _NAME_OK.sub("_", name)
    if not clean:
        clean = prefix
    if clean[0].isdigit():
        clean = f"{prefix}{clean}"
    return clean


def _fmt(v: float) -> str:
    return f"{v:.6g}"


def _pts(points: list[tuple[float, float]]) -> str:
    return "list(" + " ".join(f"list({_fmt(x)} {_fmt(y)})" for x, y in points) + ")"


def _arc_points(cx: float, cy: float, r: float, a1: float, a2: float) -> list[tuple[float, float]]:
    """Sample a partial arc in xschem coordinates (angles CCW on screen, y-down frame)."""
    steps = max(2, int(_ARC_SEGMENTS * min(abs(a2), 360.0) / 360.0))
    out = []
    for i in range(steps + 1):
        theta = math.radians(a1 + a2 * i / steps)
        out.append((cx + r * math.cos(theta), cy - r * math.sin(theta)))
    return out


def emit_symbol_il(
    sym_sch: Schematic,
    sym_text: str,
    *,
    lib: str,
    cell: str,
    scale: float = DEFAULT_SCALE,
    source_name: str = "",
) -> SymbolEmitResult:
    """Render a parsed ``.sym`` (``sym_sch`` = its records, ``sym_text`` = raw text for the
    ``K{}`` block) into a symbol-view ``.il`` for ``lib/cell`` (see module docstring)."""
    result = SymbolEmitResult(il="")
    body: list[str] = []
    xs: list[float] = []
    ys: list[float] = []

    def track(x: float, y: float) -> tuple[float, float]:
        cx, cy = to_cadence(x, y, scale)
        xs.append(cx)
        ys.append(cy)
        return cx, cy

    body.append(
        f'cv = dbOpenCellViewByType("{_s(lib)}" "{_s(cell)}" "symbol" "schematicSymbol" "w")'
    )

    # --- body graphics -----------------------------------------------------------
    for line in sym_sch.lines:
        p1 = track(line.x1, line.y1)
        p2 = track(line.x2, line.y2)
        body.append(f'dbCreateLine(cv list("device" "drawing") {_pts([p1, p2])})')
    for poly in sym_sch.polygons:
        pts = [track(x, y) for x, y in poly.points]
        body.append(f'dbCreatePolygon(cv list("device" "drawing") {_pts(pts)})')
    for arc in sym_sch.arcs:
        if abs(arc.a2) >= 360.0:
            x0, y0 = track(arc.cx - arc.r, arc.cy - arc.r)
            x1, y1 = track(arc.cx + arc.r, arc.cy + arc.r)
            body.append(
                f'dbCreateEllipse(cv list("device" "drawing") '
                f"list(list({_fmt(min(x0, x1))} {_fmt(min(y0, y1))}) "
                f"list({_fmt(max(x0, x1))} {_fmt(max(y0, y1))})))"
            )
        else:
            pts = [track(x, y) for x, y in _arc_points(arc.cx, arc.cy, arc.r, arc.a1, arc.a2)]
            body.append(f'dbCreateLine(cv list("device" "drawing") {_pts(pts)})')

    # --- pins (B on layer 5, in record order = xschem @pinlist) --------------------
    pins = parse_symbol(sym_text).pins
    pin_names: list[str] = []
    for pin in pins:
        if not pin.name:
            result.warnings.append("pin box without a name — skipped")
            continue
        name = _sanitize(pin.name, prefix="P")
        direction = _DIRECTION.get(pin.dir, "inputOutput")
        px, py = track(pin.x, pin.y)
        half = max(2.5 * scale, 0.01)  # xschem pin boxes are 5x5 units
        body.append(
            "let((net term rect pin) "
            f'net = car(setof(x cv~>nets x~>name == "{_s(name)}")) '
            f'unless(net net = dbCreateNet(cv "{_s(name)}")) '
            f'term = dbCreateTerm(net "{_s(name)}" "{direction}") '
            f'unless(term error("xvport: term not created: {_s(name)}")) '
            f'rect = dbCreateRect(cv list("pin" "drawing") '
            f"list(list({_fmt(px - half)} {_fmt(py - half)}) list({_fmt(px + half)} {_fmt(py + half)}))) "
            f'pin = dbCreatePin(net rect "{_s(name)}" term) '
            f'unless(pin error("xvport: pin not created: {_s(name)}")))'
        )
        pin_names.append(name)
        result.terms[name] = direction

    # non-pin boxes are graphics
    for box in sym_sch.boxes:
        if box.layer == _PIN_LAYER:
            continue
        p1 = track(box.x1, box.y1)
        p2 = track(box.x2, box.y2)
        body.append(
            f'dbCreateRect(cv list("device" "drawing") '
            f"list(list({_fmt(min(p1[0], p2[0]))} {_fmt(min(p1[1], p2[1]))}) "
            f"list({_fmt(max(p1[0], p2[0]))} {_fmt(max(p1[1], p2[1]))})))"
        )

    # --- texts ---------------------------------------------------------------------
    pin_lookup = {p.lower() for p in pin_names}
    for t in sym_sch.texts:
        tx, ty = track(t.x, t.y)
        height = max(0.03, t.size_y * _TEXT_HEIGHT_UNITS * scale)
        rotation = "R90" if t.rot % 2 else "R0"
        text = t.text.strip()
        if text == "@symname":
            body.append(
                f'schCreateSymbolLabel(cv list({_fmt(tx)} {_fmt(ty)}) "logical label" '
                f'"[@partName]" "lowerLeft" "{rotation}" "stick" {_fmt(height)} "NLPLabel")'
            )
        elif text == "@name":
            body.append(
                f'schCreateSymbolLabel(cv list({_fmt(tx)} {_fmt(ty)}) "instance label" '
                f'"[@instanceName]" "lowerLeft" "{rotation}" "stick" {_fmt(height)} "NLPLabel")'
            )
        elif text.lower() in pin_lookup:
            body.append(
                f'schCreateSymbolLabel(cv list({_fmt(tx)} {_fmt(ty)}) "pin name" '
                f'"{_s(_sanitize(text, prefix="P"))}" "lowerLeft" "{rotation}" "stick" '
                f'{_fmt(height)} "normalLabel")'
            )
        elif text.startswith("@"):
            result.warnings.append(f"unsupported @-text {text!r} — skipped")
        else:
            body.append(
                f'dbCreateLabel(cv list("annotate" "drawing") list({_fmt(tx)} {_fmt(ty)}) '
                f'"{_s(text)}" "lowerLeft" "{rotation}" "stick" {_fmt(height)})'
            )

    # --- selection box, term order, check, save --------------------------------------
    if xs and ys:
        margin = 0.01
        body.append(
            f'dbCreateRect(cv list("instance" "drawing") '
            f"list(list({_fmt(min(xs) - margin)} {_fmt(min(ys) - margin)}) "
            f"list({_fmt(max(xs) + margin)} {_fmt(max(ys) + margin)})))"
        )
    if pin_names:
        order = " ".join(f'"{_s(n)}"' for n in pin_names)
        body.append(f"cv~>termOrder = list({order})")
        result.term_order = pin_names
    body.append(
        "let((pinList) pinList = schSymbolToPinList(cv~>libName cv~>cellName cv~>viewName) "
        f'printf("xvport: built symbol {_s(lib)}/{_s(cell)} terms=%d pinlist=%s\\n" '
        'length(cv~>terminals) if(pinList "ok" "FAILED")))'
    )
    body.append("dbSave(cv)")
    body.append("dbClose(cv)")

    src = f" from {source_name}" if source_name else ""
    header = (
        f"; xvport symbol build{src}\n"
        f"; target: {lib}/{cell}/symbol   scale={scale}   generator: spicexplorer xvport\n"
    )
    inner = "\n  ".join(body)
    result.il = f"{header}\nlet((cv)\n  {inner}\n)\n"
    return result


def emit_symbol_il_from_text(
    text: str,
    *,
    lib: str,
    cell: str,
    scale: float = DEFAULT_SCALE,
    source_name: str = "",
) -> SymbolEmitResult:
    """Convenience wrapper: parse ``.sym`` text and emit its symbol ``.il``."""
    return emit_symbol_il(
        parse_sch(text), text, lib=lib, cell=cell, scale=scale, source_name=source_name
    )
