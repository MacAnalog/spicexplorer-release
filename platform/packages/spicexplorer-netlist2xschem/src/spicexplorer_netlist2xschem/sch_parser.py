"""Read an xschem ``.sch`` file back into typed records — the *reverse* of :mod:`emit`.

:mod:`emit` writes a ``.sch``; this module reads one. It is the keystone for the two jobs that start
from an existing schematic rather than a netlist:

* **template stamping** (:mod:`stamp`) — parse a hand-drawn block template ``.sch`` to recover each
  device's symmetric placement ``(x, y, rot, flip)``, then re-use it as a placement hint;
* **annotate-an-existing-.sch** — parse a schematic the user already drew to recover its device
  coordinates, so the functional-block overlay can be drawn over *their* layout (no re-placement).

The xschem text format is line-oriented, but a trailing property block ``{...}`` may span several
lines (xschem writes one ``key=value`` per line inside it). So we cannot split on ``\\n`` naively: the
record splitter below walks the text tracking brace depth (quote- and escape-aware, mirroring
:func:`spicexplorer_netlist2xschem.sym_library._extract_k_block`) and ends a record only at a newline
seen at depth 0. Each record is then parsed by its leading type letter:

* ``C {symref} x y rot flip {attrs}`` — a placed symbol instance (device, net label, or port pin);
* ``N x1 y1 x2 y2 {attrs}`` — a wire segment (``lab=`` gives its net, when present);
* ``B layer x1 y1 x2 y2 {props}`` — a graphic rectangle (an annotation box, or on layer 5 a pin);
* ``T {text} x y rot flip sx sy {props}`` — a text label (a title or a block label);
* ``L layer x1 y1 x2 y2 {props}`` — a graphic line;
* ``A layer cx cy r a1 a2 {props}`` — an arc (``a1`` start angle, ``a2`` sweep, degrees; a
  360° sweep is a full circle);
* ``P layer npoints x1 y1 … {props}`` — a polygon.

The same grammar covers ``.sym`` files (whose drawings are ``L``/``B``/``A``/``P``/``T``), which is
what the Virtuoso symbol exporter parses them with. We ignore the rest (``v/G/K/V/S/E`` …) — draw
defaults and metadata. The parser is deliberately lenient: a malformed record is skipped, not fatal,
so a slightly non-canonical hand-drawn ``.sch`` still yields the components it can.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = [
    "SchComponent",
    "SchWire",
    "SchBox",
    "SchText",
    "SchLine",
    "SchArc",
    "SchPolygon",
    "Schematic",
    "parse_sch",
]

# A `key=value` attribute inside a `{...}` block; value is a quoted string or a bare token.
_ATTR = re.compile(r"(\w+)\s*=\s*(\"(?:\\.|[^\"\\])*\"|\S+)")


@dataclass(frozen=True)
class SchComponent:
    """A placed symbol instance — a ``C {symref} x y rot flip {attrs}`` record.

    ``symref`` is the symbol reference (e.g. ``sg13g2_pr/sg13_lv_nmos.sym``); ``attrs`` is the parsed
    property block (``name``, ``model``, ``w``/``l``, ``lab`` …). Convenience accessors expose the two
    fields that join a component back to a netlist/overlay: its instance ``name`` and, for a label/port
    symbol, the net it carries (``lab``).
    """

    symref: str
    x: float
    y: float
    rot: int
    flip: int
    attrs: dict[str, str] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.attrs.get("name", "")

    @property
    def lab(self) -> str | None:
        return self.attrs.get("lab")

    @property
    def is_label(self) -> bool:
        """A net-name label symbol (``lab_wire``/``lab_pin``) — not a real device."""
        return "lab_wire" in self.symref or "lab_pin" in self.symref

    @property
    def is_port(self) -> bool:
        """A circuit-I/O port-pin symbol (``ipin``/``opin``/``iopin``)."""
        base = self.symref.rsplit("/", 1)[-1]
        return base in ("ipin.sym", "opin.sym", "iopin.sym")

    @property
    def is_device(self) -> bool:
        """A real device instance (not a net label, not a port pin, not a decorative title,
        not a no-connect marker)."""
        base = self.symref.rsplit("/", 1)[-1]
        return not (
            self.is_label or self.is_port or base in ("title.sym", "code.sym", "noconn.sym")
        )


@dataclass(frozen=True)
class SchWire:
    """A wire segment — an ``N x1 y1 x2 y2 {attrs}`` record (``lab`` names its net when present)."""

    x1: float
    y1: float
    x2: float
    y2: float
    attrs: dict[str, str] = field(default_factory=dict)

    @property
    def lab(self) -> str | None:
        return self.attrs.get("lab")


@dataclass(frozen=True)
class SchBox:
    """A graphic rectangle — a ``B layer x1 y1 x2 y2 {props}`` record (an annotation box)."""

    layer: int
    x1: float
    y1: float
    x2: float
    y2: float
    props: str = ""


@dataclass(frozen=True)
class SchText:
    """A text record — ``T {text} x y rot flip sx sy {props}`` (a title or a block label)."""

    text: str
    x: float
    y: float
    rot: int = 0
    flip: int = 0
    size_x: float = 0.4
    size_y: float = 0.4
    props: str = ""


@dataclass(frozen=True)
class SchLine:
    """A graphic line — an ``L layer x1 y1 x2 y2 {props}`` record."""

    layer: int
    x1: float
    y1: float
    x2: float
    y2: float
    props: str = ""


@dataclass(frozen=True)
class SchArc:
    """An arc — an ``A layer cx cy r a1 a2 {props}`` record (``a2 >= 360`` is a full circle)."""

    layer: int
    cx: float
    cy: float
    r: float
    a1: float = 0.0
    a2: float = 360.0
    props: str = ""


@dataclass(frozen=True)
class SchPolygon:
    """A polygon — a ``P layer npoints x1 y1 … {props}`` record."""

    layer: int
    points: tuple[tuple[float, float], ...]
    props: str = ""


@dataclass(frozen=True)
class Schematic:
    """A parsed ``.sch`` — its version line plus the records we model. Draw-only records are dropped."""

    version: str = ""
    components: tuple[SchComponent, ...] = ()
    wires: tuple[SchWire, ...] = ()
    boxes: tuple[SchBox, ...] = ()
    texts: tuple[SchText, ...] = ()
    lines: tuple[SchLine, ...] = ()
    arcs: tuple[SchArc, ...] = ()
    polygons: tuple[SchPolygon, ...] = ()

    @property
    def devices(self) -> tuple[SchComponent, ...]:
        """Just the real device instances (excludes net labels, port pins, and the title block)."""
        return tuple(c for c in self.components if c.is_device)

    def component(self, name: str) -> SchComponent | None:
        """The component whose instance ``name`` matches (exact), or ``None``."""
        return next((c for c in self.components if c.name == name), None)

    def device_by_name(self, name: str, *, strip_x: bool = True) -> SchComponent | None:
        """A device by instance name, tolerant of the ``X`` spiceprefix split.

        xschem drops a leading ``X`` from an instance whose symbol carries ``spiceprefix=X`` (so the
        netlist ``XM1`` is drawn as ``name=M1``). When ``strip_x`` we compare with a leading ``X``/``x``
        removed on both sides, so a caller holding the *netlist* name (``XM1``) still finds the drawn
        device (``M1``)."""

        def norm(s: str) -> str:
            return s[1:] if strip_x and s[:1] in "Xx" else s

        target = norm(name)
        return next((c for c in self.devices if norm(c.name) == target), None)


# ---------------------------------------------------------------------------
# Record splitting (brace-depth aware, so multi-line property blocks stay whole)
# ---------------------------------------------------------------------------
def _split_records(text: str) -> list[str]:
    """Split ``.sch`` text into one string per object.

    An object runs from its leading type letter to the newline seen at brace depth 0 — so a property
    block ``{...}`` that spans lines (xschem writes one ``key=value`` per line) keeps the object whole.
    Quote- and backslash-aware so a brace inside a quoted attribute value does not change the depth.
    """
    records: list[str] = []
    buf: list[str] = []
    depth = 0
    in_q = False
    esc = False
    for c in text:
        if esc:
            buf.append(c)
            esc = False
            continue
        if c == "\\":
            buf.append(c)
            esc = True
            continue
        if c == '"':
            in_q = not in_q
            buf.append(c)
            continue
        if not in_q and c == "{":
            depth += 1
        elif not in_q and c == "}":
            depth = max(0, depth - 1)
        if c == "\n" and depth == 0:
            rec = "".join(buf).strip()
            if rec:
                records.append(rec)
            buf = []
        else:
            buf.append(c)
    rec = "".join(buf).strip()
    if rec:
        records.append(rec)
    return records


def _brace_groups(s: str) -> tuple[list[str], list[str]]:
    """Split a record into its top-level ``{...}`` groups and the bare tokens around them.

    Returns ``(groups, tokens)`` where ``groups`` are the inner texts of each top-level brace group in
    order, and ``tokens`` are the whitespace-split bare words that sit *outside* every brace group
    (the type letter, coordinates, layer, rot/flip). Brace matching is quote- and escape-aware.
    """
    groups: list[str] = []
    outside: list[str] = []
    depth = 0
    in_q = False
    esc = False
    cur: list[str] = []  # current brace group's inner text
    out: list[str] = []  # current run of outside chars
    for c in s:
        if esc:
            (cur if depth else out).append(c)
            esc = False
            continue
        if c == "\\":
            (cur if depth else out).append(c)
            esc = True
            continue
        if c == '"':
            in_q = not in_q
            (cur if depth else out).append(c)
            continue
        if not in_q and c == "{":
            if depth == 0:
                outside.append("".join(out))
                out = []
                cur = []
            else:
                cur.append(c)
            depth += 1
            continue
        if not in_q and c == "}":
            depth -= 1
            if depth == 0:
                groups.append("".join(cur))
            else:
                cur.append(c)
            continue
        (cur if depth else out).append(c)
    outside.append("".join(out))
    tokens = [t for chunk in outside for t in chunk.split()]
    return groups, tokens


def _attrs(block: str) -> dict[str, str]:
    """Parse a ``{...}`` inner block of ``key=value`` pairs (newline- or space-separated)."""
    return {k: _unquote(v) for k, v in _ATTR.findall(block)}


def _unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        token = token[1:-1]
    return token.replace('\\"', '"').replace("\\\\", "\\")


def _num(token: str) -> float:
    return float(token)


def _int(token: str) -> int:
    return int(round(float(token)))


def parse_sch(text: str) -> Schematic:
    """Parse xschem ``.sch`` ``text`` into a :class:`Schematic` (components, wires, boxes, texts, lines).

    Lenient: a record that doesn't parse (wrong arity, non-numeric coordinate) is skipped rather than
    raising, so a slightly non-canonical hand-drawn schematic still yields everything well-formed.
    """
    version = ""
    components: list[SchComponent] = []
    wires: list[SchWire] = []
    boxes: list[SchBox] = []
    texts: list[SchText] = []
    lines: list[SchLine] = []
    arcs: list[SchArc] = []
    polygons: list[SchPolygon] = []

    for rec in _split_records(text):
        kind = rec[0]
        try:
            groups, tokens = _brace_groups(rec)
            if kind == "v":
                version = groups[0] if groups else ""
            elif kind == "C":
                # C {symref} x y rot flip {attrs}  -> tokens[0]='C', then x y rot flip
                symref = groups[0] if groups else ""
                attrs = _attrs(groups[1]) if len(groups) > 1 else {}
                components.append(
                    SchComponent(
                        symref=symref,
                        x=_num(tokens[1]),
                        y=_num(tokens[2]),
                        rot=_int(tokens[3]),
                        flip=_int(tokens[4]),
                        attrs=attrs,
                    )
                )
            elif kind == "N":
                # N x1 y1 x2 y2 {attrs}
                wires.append(
                    SchWire(
                        x1=_num(tokens[1]),
                        y1=_num(tokens[2]),
                        x2=_num(tokens[3]),
                        y2=_num(tokens[4]),
                        attrs=_attrs(groups[0]) if groups else {},
                    )
                )
            elif kind == "B":
                # B layer x1 y1 x2 y2 {props}
                boxes.append(
                    SchBox(
                        layer=_int(tokens[1]),
                        x1=_num(tokens[2]),
                        y1=_num(tokens[3]),
                        x2=_num(tokens[4]),
                        y2=_num(tokens[5]),
                        props=groups[0] if groups else "",
                    )
                )
            elif kind == "T":
                # T {text} x y rot flip sx sy {props}
                texts.append(
                    SchText(
                        text=groups[0] if groups else "",
                        x=_num(tokens[1]),
                        y=_num(tokens[2]),
                        rot=_int(tokens[3]),
                        flip=_int(tokens[4]),
                        size_x=_num(tokens[5]) if len(tokens) > 5 else 0.4,
                        size_y=_num(tokens[6]) if len(tokens) > 6 else 0.4,
                        props=groups[1] if len(groups) > 1 else "",
                    )
                )
            elif kind == "L":
                # L layer x1 y1 x2 y2 {props}
                lines.append(
                    SchLine(
                        layer=_int(tokens[1]),
                        x1=_num(tokens[2]),
                        y1=_num(tokens[3]),
                        x2=_num(tokens[4]),
                        y2=_num(tokens[5]),
                        props=groups[0] if groups else "",
                    )
                )
            elif kind == "A":
                # A layer cx cy r a1 a2 {props}
                arcs.append(
                    SchArc(
                        layer=_int(tokens[1]),
                        cx=_num(tokens[2]),
                        cy=_num(tokens[3]),
                        r=_num(tokens[4]),
                        a1=_num(tokens[5]) if len(tokens) > 5 else 0.0,
                        a2=_num(tokens[6]) if len(tokens) > 6 else 360.0,
                        props=groups[0] if groups else "",
                    )
                )
            elif kind == "P":
                # P layer npoints x1 y1 x2 y2 ... {props}
                n = _int(tokens[2])
                coords = [_num(tok) for tok in tokens[3 : 3 + 2 * n]]
                pts = tuple(zip(coords[0::2], coords[1::2]))
                if pts:
                    polygons.append(
                        SchPolygon(
                            layer=_int(tokens[1]),
                            points=pts,
                            props=groups[0] if groups else "",
                        )
                    )
            # else: v/G/K/V/S/E and any unknown record — draw defaults/metadata, ignored.
        except (IndexError, ValueError):
            continue  # lenient: skip a malformed record rather than fail the whole parse

    return Schematic(
        version=version,
        components=tuple(components),
        wires=tuple(wires),
        boxes=tuple(boxes),
        texts=tuple(texts),
        lines=tuple(lines),
        arcs=tuple(arcs),
        polygons=tuple(polygons),
    )
