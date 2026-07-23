"""Connection planning: wire every net's gate/source/drain pins into one connected tree, with a
net-name label per surviving piece carrying connectivity wherever a wire had to be dropped.

Given a topology placement this plans, for every device terminal:

* **signal nets** (the drain/source/gate pins of a net) → an orthogonal tree of real wires: per-column
  vertical runs and per-row horizontal runs (a leg's drain/source stack and a row of mirror gates each
  become one straight wire — the latter is the gate bus), then L-bridges joining whatever the runs left
  apart (see :func:`_net_wires`). One net-name label is dropped per surviving connected piece;
* **diode-connected devices** (gate net == drain net) → an explicit gate→drain **tie** that loops
  past the body before reaching the drain (so it clears the body pin on the drain column) — just
  another segment on its net, folded into that net's tree and labelling;
* **body (bulk) pins** → a short stub that steps out then drops clear of the device's parameter text,
  then a net-name label (the body is named, never merged into a leg);
* **supply nets** (VDD / VSS / GND) → a horizontal rail (VDD top, VSS/GND bottom); each device's
  supply drain/source pin flushes onto its rail with a short vertical stub;
* **port nets** (circuit I/O — declared ``.subckt`` ports or dangling external nodes) → an
  ``ipin``/``opin``/``iopin`` **port symbol** parked at the schematic edge (inputs left, outputs
  right, bidirectional below), linked to its terminal by net name;
* **independent sources** (V/I, parked bottom-left by the placer) → **both terminals named in place**
  and nothing else: a source is never wired, flushed to a rail, or joined into a net's wire tree, so it
  connects to the circuit purely by the net name on each terminal. The rest of the net is wired among
  its non-source pins exactly as if the source were absent.

Every drawn segment is checked against :mod:`.connectivity`, which models xschem's net-merge rules
exactly: any segment that would touch a foreign net's pin or wire is dropped and the pins it would have
joined fall back to net-name labels (always correct regardless of geometry). So we wire aggressively
for readability yet never ship a short, and nothing is ever left floating — the Docker round-trip
(`xschem -n -s`) is the final gate.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field

from .connectivity import (
    Route,
    Seg,
    Terminal,
    _point_on_seg,
    _segs_touch,
    conflicting_routes,
)
from .geometry import Transform, apply_transform, snap
from .mapping import port_symref
from .sym_library import SymPin

__all__ = [
    "NetLabel",
    "Wire",
    "PortPin",
    "PlacedDevice",
    "PinRef",
    "ConnectionPlan",
    "plan_connections",
    "build_labels",
    "device_extent",
]

_RAIL_GAP = 80  # vertical gap from the outermost device pins to the supply rail lines
_RAIL_MARGIN = 60  # horizontal overhang of a rail past the outermost pin column
_PORT_MARGIN = 140  # gap from the device bbox to the port pins parked at the schematic edges
_PORT_STEP = 120  # vertical/horizontal spacing when several ports stack on the same edge
_DIODE_LOOP = 40  # how far a diode-connect gate→drain tie loops past the device to clear the body pin
_LABEL_STUB = 60  # length of the wire a net name is pulled onto, off the symbol, before its label
_LEAD = 30  # how far each terminal extends past the symbol body before any routing begins (the
#             "boundary-box port"): a net's tree is wired between these ports, not the raw pins, so a
#             corner or T-junction never lands inside a device body or on its parameter text.

# --- device keepout geometry (the "clearance box" — symbol body + the symbol-baked parameter text).
# A MOS symbol draws its w/l/model text just outside the body on the +x side (mirrored to −x by a
# device flip); we model that as a rectangle so labels and label-stubs can be kept out of it. Coords
# are symbol-local (before the placement transform); a device is only ever placed with rot=0, so flip
# just negates the x-extent. See ``placement.TopologyPlacer`` whose pitches reserve a lane for this.
_SYM_HALF_X = 30  # half-width of the device body + pins (gate at −20, drain/source/bulk at +20)
_SYM_HALF_Y = 38  # half-height (drain/source pins at ±30)
_TEXT_X0 = 22  # the parameter text starts just outside the body, on the +x (gate-opposite) side
_TEXT_REACH = 165  # how far the longest w/l/model string reaches from the body
_TEXT_Y0, _TEXT_Y1 = -32, 34  # vertical span of the w/l/model text block
_CLEAR = 20  # clearance margin kept around every keepout box
_CHAR_W = 7  # approximate drawn width of one net-name character (size-0.27 label text)
_LABEL_H = 22  # approximate drawn height of a net-name label

Box = tuple[int, int, int, int]  # (x0, y0, x1, y1), x0<=x1, y0<=y1


@dataclass(frozen=True)
class NetLabel:
    """A placed net-name label (``lab_wire.sym``) at absolute ``(x, y)``."""

    x: int
    y: int
    lab: str
    rot: int = 0
    flip: int = 0


@dataclass(frozen=True)
class Wire:
    """An orthogonal wire segment (``N x1 y1 x2 y2``)."""

    x1: int
    y1: int
    x2: int
    y2: int


@dataclass(frozen=True)
class PortPin:
    """A circuit-I/O port drawn as a pin symbol (``ipin``/``opin``/``iopin``) carrying the net name."""

    x: int
    y: int
    net: str
    symref: str
    rot: int = 0
    flip: int = 0


@dataclass(frozen=True)
class PlacedDevice:
    """A device ready to wire: its placement, pin→net map, and aligned symbol-pin geometry."""

    ref: str
    transform: Transform
    nets: Mapping[str, str]  # canonical pin -> net
    aligned: Mapping[str, SymPin]  # canonical pin -> symbol pin
    text_w: int = _TEXT_REACH  # how far the symbol's w/l/model text reaches (sized to the actual strings)
    is_source: bool = False  # an independent V/I source: both terminals named, never wired (see below)


@dataclass(frozen=True)
class PinRef:
    """One device pin instance on a net, at its absolute schematic coordinate."""

    x: int
    y: int


@dataclass(frozen=True)
class ConnectionPlan:
    """The planned drawing: wires, net-name labels, and port pins."""

    wires: list[Wire] = field(default_factory=list)
    labels: list[NetLabel] = field(default_factory=list)
    ports: list[PortPin] = field(default_factory=list)


# Canonical pin name -> wiring role. Anything else (passive P/N, subckt ports) is a generic terminal.
_PIN_ROLE = {"GATE": "gate", "DRAIN": "drain", "SOURCE": "source", "BULK": "bulk"}


@dataclass(frozen=True)
class _APin:
    """An absolute device pin: its net, wiring role, schematic coordinate, and its device origin.

    ``(x, y)`` is the symbol pin; ``(ex, ey)`` is its **boundary-box port** — the pin pulled a short
    lead out along its outward normal, clear of the body. Net routing happens between ports; a lead
    segment joins each port back to its pin."""

    net: str
    role: str
    x: int
    y: int
    ex: int  # boundary-box port x (pin extended out along its normal; == x for a bulk pin)
    ey: int  # boundary-box port y
    ox: int  # the device's placement x (so a bulk pin knows which side of its body it sits on)
    oy: int  # the device's placement y (kept alongside ox for the bulk-stub direction test)
    flip: int = 0  # the device's flip (so a label stub knows which side the parameter text is on)
    tw: int = _TEXT_REACH  # the device's parameter-text reach (so a stub knows how far to clear it)
    is_source: bool = False  # a V/I source pin: named in place, never joined into a net's wire tree


def _abs_pins(placed: list[PlacedDevice]) -> list[_APin]:
    out: list[_APin] = []
    for pd in placed:
        for canon, sp in pd.aligned.items():
            x, y = apply_transform(pd.transform, sp.x, sp.y)
            role = _PIN_ROLE.get(canon, "term")
            ex, ey = x, y
            # A source pin grows no boundary-box lead — it is never wired, only named in place.
            if role != "bulk" and not pd.is_source:  # extend the terminal out to its port along its normal
                dx, dy = x - pd.transform.x, y - pd.transform.y
                if abs(dy) >= abs(dx):  # vertical pin (drain/source/passive lead): extend along y
                    ey = y + (_LEAD if dy >= 0 else -_LEAD)
                else:  # horizontal pin (gate): extend along x
                    ex = x + (_LEAD if dx >= 0 else -_LEAD)
            out.append(
                _APin(
                    net=pd.nets[canon],
                    role=role,
                    x=x,
                    y=y,
                    ex=ex,
                    ey=ey,
                    ox=pd.transform.x,
                    oy=pd.transform.y,
                    flip=pd.transform.flip,
                    tw=pd.text_w,
                    is_source=pd.is_source,
                )
            )
    return out


def _anchor(pins: list[_APin]) -> _APin:
    """The topmost-then-leftmost pin of a net — a stable, visible spot for its name label / port."""
    return min(pins, key=lambda p: (p.y, p.x))


def _spread(values: list[int], step: int) -> list[int]:
    """Push a sorted list of coordinates apart so consecutive ones are at least ``step`` apart."""
    out: list[int] = []
    for v in values:
        out.append(max(v, out[-1] + step) if out else v)
    return out


def _to_segs(wires: list[Wire], net: str) -> tuple[Seg, ...]:
    return tuple(Seg(w.x1, w.y1, w.x2, w.y2, net) for w in wires)


def _pick_rail_net(
    supply: Mapping[str, str], roles: set[str], by_net: dict[str, list[_APin]]
) -> str | None:
    """The supply net (of the given role set) with a wirable pin, picked deterministically by name."""
    for net in sorted(supply):
        if supply[net] in roles and any(p.role != "bulk" for p in by_net.get(net, [])):
            return net
    return None


Point = tuple[int, int]


def _closest_pair(a: list[Point], b: list[Point]) -> tuple[Point, Point]:
    """The (point in ``a``, point in ``b``) pair with the smallest Manhattan distance (deterministic)."""
    return min(
        ((pa, pb) for pa in a for pb in b),
        key=lambda pq: (abs(pq[0][0] - pq[1][0]) + abs(pq[0][1] - pq[1][1]), pq[0], pq[1]),
    )


def _grid_components(pts: list[Point]) -> list[list[Point]]:
    """Group points joined (transitively) by a shared x (a column run) or a shared y (a row run)."""
    idx = {p: i for i, p in enumerate(pts)}
    parent = list(range(len(pts)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_x: dict[int, list[Point]] = defaultdict(list)
    by_y: dict[int, list[Point]] = defaultdict(list)
    for p in pts:
        by_x[p[0]].append(p)
        by_y[p[1]].append(p)
    for grp in (*by_x.values(), *by_y.values()):
        for q in grp[1:]:
            parent[find(idx[grp[0]])] = find(idx[q])
    comps: dict[int, list[Point]] = defaultdict(list)
    for p in pts:
        comps[find(idx[p])].append(p)
    return list(comps.values())


def _net_wires(pts: list[Point]) -> list[Wire]:
    """Orthogonal wires joining all of a net's pins into one connected tree.

    Per-column **vertical runs** and per-row **horizontal runs** link pins that share an x or a y (so a
    leg's drain/source stack and a row of mirror gates each become one straight wire — the gate bus of
    requirement 4); whatever the runs leave in separate pieces is bridged by an L between the two nearest
    pins. Every segment is a candidate the connectivity verifier may drop — a dropped segment simply
    leaves its pins linked by net name — so this only ever *adds* readable wiring, never a short.
    """
    pts = sorted(set(pts))
    if len(pts) <= 1:
        return []
    segs: list[Wire] = []
    by_x: dict[int, list[int]] = defaultdict(list)
    by_y: dict[int, list[int]] = defaultdict(list)
    for x, y in pts:
        by_x[x].append(y)
        by_y[y].append(x)
    # Split each run into segments between *adjacent* pins, not one span end-to-end: a gate bus that
    # must cross one foreign pin then loses only that span (the rest of the mirror stays wired).
    for x, ys in by_x.items():
        ys = sorted(set(ys))
        segs.extend(Wire(x, y1, x, y2) for y1, y2 in zip(ys, ys[1:]))
    for y, xs in by_y.items():
        xs = sorted(set(xs))
        segs.extend(Wire(x1, y, x2, y) for x1, x2 in zip(xs, xs[1:]))
    comps = sorted(_grid_components(pts), key=min)
    for prev, cur in zip(comps, comps[1:]):  # bridge separate pieces with an L (h-leg then v-leg)
        (ax, ay), (bx, by) = _closest_pair(prev, cur)
        if ax != bx and ay != by:
            segs.append(Wire(ax, ay, bx, ay))
            segs.append(Wire(bx, ay, bx, by))
        elif (ax, ay) != (bx, by):
            segs.append(Wire(ax, ay, bx, by))
    return segs


def _wire_components(pts: list[Point], wires: list[Wire]) -> list[list[Point]]:
    """Connected components of ``pts`` over the drawn ``wires`` (xschem's exact merge rules).

    Used after the verifier has dropped any shorting segment, to drop **one** net-name label per
    surviving connected piece (a fully-wired net gets a single label; a pin no wire reached is its own
    piece and keeps its own label, so nothing is ever left unnamed)."""
    segs = [Seg(w.x1, w.y1, w.x2, w.y2, "") for w in wires]
    ns = len(segs)
    parent = list(range(ns + len(pts)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        parent[find(i)] = find(j)

    for i in range(ns):
        for j in range(i + 1, ns):
            if _segs_touch(segs[i], segs[j]):
                union(i, j)
    coincident: dict[Point, int] = {}
    for k, p in enumerate(pts):
        node = ns + k
        for i, s in enumerate(segs):
            if _point_on_seg(p[0], p[1], s):
                union(node, i)
        if p in coincident:
            union(node, coincident[p])
        else:
            coincident[p] = node
    comps: dict[int, list[Point]] = defaultdict(list)
    for k, p in enumerate(pts):
        comps[find(ns + k)].append(p)
    return list(comps.values())


def _dev_boxes(ox: int, oy: int, flip: int, reach: int = _TEXT_REACH) -> list[Box]:
    """One device's two keepout boxes: its symbol body, and the parameter-text band beside it.

    The symbol draws w/l/model text on the +x side (mirrored to −x by ``flip``); ``reach`` is how far
    that text extends, sized to the device's actual strings. Devices are always placed rot=0, so both
    boxes are axis-aligned and flip just negates the text x-extent."""
    sym = (ox - _SYM_HALF_X, oy - _SYM_HALF_Y, ox + _SYM_HALF_X, oy + _SYM_HALF_Y)
    if flip:
        txt = (ox - _TEXT_X0 - reach, oy + _TEXT_Y0, ox - _TEXT_X0, oy + _TEXT_Y1)
    else:
        txt = (ox + _TEXT_X0, oy + _TEXT_Y0, ox + _TEXT_X0 + reach, oy + _TEXT_Y1)
    return [sym, txt]


def _device_keepouts(placed: list[PlacedDevice]) -> list[Box]:
    """Every device's clearance boxes (symbol + parameter text) — a label or its stub must stay out of
    these, which is what kept a flipped device's leftward w/l/model text from colliding with names."""
    return [
        b for pd in placed for b in _dev_boxes(pd.transform.x, pd.transform.y, pd.transform.flip, pd.text_w)
    ]


def device_extent(pd: PlacedDevice) -> Box:
    """The absolute bounding box of one placed device: its symbol body *plus* its parameter-text band.

    The union of :func:`_dev_boxes` (the same tuned body/text geometry the wiring keep-out uses), so a
    caller that draws a box around a group of devices — the functional-block annotation overlay — can
    enclose each device without clipping its w/l/model text. Devices are only ever placed ``rot=0``, so
    the result is axis-aligned and ``flip`` only mirrors the text band's x-extent."""
    boxes = _dev_boxes(pd.transform.x, pd.transform.y, pd.transform.flip, pd.text_w)
    return (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def _box_overlaps(a: Box, b: Box, margin: int = 0) -> bool:
    return not (
        a[2] + margin < b[0] or a[0] - margin > b[2] or a[3] + margin < b[1] or a[1] - margin > b[3]
    )


def _seg_box(w: Wire) -> Box:
    return (min(w.x1, w.x2), min(w.y1, w.y2), max(w.x1, w.x2), max(w.y1, w.y2))


# Stub direction → (label rot, flip) so the name reads *outward*, away from the wire (see the
# orientation probe): right→text-right, left→text-left, up→horizontal above, down→horizontal below.
def _label_box(ex: int, ey: int, name: str, dirx: int, diry: int) -> tuple[int, int, Box]:
    """The (rot, flip, text-bbox) for a label at stub endpoint ``(ex, ey)`` reading away from the wire."""
    width = max(_LABEL_STUB, len(name) * _CHAR_W)
    if diry < 0:  # stub points up — text horizontal, above the endpoint, reading right
        return 0, 1, (ex, ey - _LABEL_H, ex + width, ey)
    if diry > 0:  # stub points down — text horizontal, below the endpoint, reading right
        return 2, 0, (ex, ey, ex + width, ey + _LABEL_H)
    if dirx >= 0:  # stub points right — text continues right
        return 0, 1, (ex, ey - _LABEL_H, ex + width, ey)
    return 0, 0, (ex - width, ey - _LABEL_H, ex, ey)  # stub points left — text continues left


def _pin_out_dir(p: _APin) -> tuple[int, int]:
    """The pin's outward normal (away from its device body), as a unit (dx, dy) on one axis."""
    dx, dy = p.x - p.ox, p.y - p.oy
    if abs(dy) > abs(dx):
        return (0, 1 if dy > 0 else -1)
    return (1 if dx >= 0 else -1, 0)


def _label_candidates(p: _APin, name: str) -> list[tuple[list[Wire], int, int, int, int, Box]]:
    """Ordered (stub-path, ex, ey, rot, flip, label-box) options for naming pin ``p``, best first.

    A signal/gate/drain/source pin steps straight out along its outward normal, then tries the
    perpendiculars and the reverse. A **bulk** pin is collinear with the drain/source column on the
    parameter-text side, so it can't step straight out without grazing the text or a sibling pin —
    instead it nudges off the column then drops into the clear inter-row gap, away from the text.

    The stub starts at the *pin* (not its boundary port), so a pin is always named directly — even in
    the rare case its lead was dropped — while the net's routing tree still starts from the ports."""
    px, py = p.x, p.y
    text_sign = -1 if p.flip else 1  # the side the device's parameter text occupies
    out: list[tuple[list[Wire], int, int, int, int, Box]] = []
    if p.role == "bulk":
        nudge = px + text_sign * (_SYM_HALF_X + 30)  # off the drain/source column, into open x
        for vdir in (1, -1):  # drop into the inter-row gap below, else above
            ey = py + vdir * (_TEXT_Y1 + _LABEL_STUB if vdir > 0 else -(-_TEXT_Y0 + _LABEL_STUB))
            rot, flip, lbox = _label_box(nudge, ey, name, 0, vdir)
            out.append(([Wire(px, py, nudge, py), Wire(nudge, py, nudge, ey)], nudge, ey, rot, flip, lbox))
        return out
    primary = _pin_out_dir(p)
    perp = (primary[1], primary[0])
    dirs = [primary, perp, (-perp[0], -perp[1]), (-primary[0], -primary[1])]
    seen: set[tuple[int, int]] = set()
    for d in dirs:
        if d in seen or d == (text_sign, 0):  # never step straight into the device's own text band
            continue
        seen.add(d)
        ex, ey = px + d[0] * _LABEL_STUB, py + d[1] * _LABEL_STUB
        rot, flip, lbox = _label_box(ex, ey, name, d[0], d[1])
        out.append(([Wire(px, py, ex, ey)], ex, ey, rot, flip, lbox))
    return out


def _accept(path: list[Wire], lbox: Box, keepouts: list[Box], own: list[Box]) -> bool:
    """The label box clears every device box (incl. its own) and the stub clears every *other* box."""
    if any(_box_overlaps(lbox, b, _CLEAR) for b in keepouts):
        return False
    for w in path:
        sb = _seg_box(w)
        if any(b not in own and _box_overlaps(sb, b, 4) for b in keepouts):
            return False
    return True


def plan_connections(
    placed: list[PlacedDevice],
    *,
    supply: Mapping[str, str],
    port_role: Mapping[str, str],
    rail_gap: int = _RAIL_GAP,
) -> ConnectionPlan:
    """Plan wires, labels, and port pins for a placed circuit (see the module docstring).

    ``supply`` maps a net to ``VDD``/``VSS``/``GND`` (rail hints); ``port_role`` maps a circuit-I/O net
    to ``in``/``out``/``inout`` (drawn as an edge port pin). Every device terminal is extended by a
    short stub wire and labelled with its net name (drain/source pins on a supply net flush onto the
    rail instead); connectivity is carried by the labels, so same-net stubs link by name. Each stub is
    still verified against :mod:`.connectivity` — a stub that would graze a foreign net drops back to a
    bare pin label — so the result always re-netlists to the original connectivity.
    """
    by_net: dict[str, list[_APin]] = defaultdict(list)
    for p in _abs_pins(placed):
        by_net[p.net].append(p)
    if not by_net:
        return ConnectionPlan()

    all_pins = [p for ps in by_net.values() for p in ps]
    # Source (V/I) pins are named in place and never routed: they stay out of the rails, the diode ties
    # and every net's wire tree, so the circuit wires only its own (non-source) connections; the source
    # then shows its hook-up purely by the net name on each terminal (placed at the bottom-left stack).
    source_pins = [p for p in all_pins if p.is_source]
    xs = [v for p in all_pins for v in (p.x, p.ex)]  # include the boundary ports in the frame extent
    ys = [v for p in all_pins for v in (p.y, p.ey)]
    # Also reach to the outermost device's parameter text so an edge column's (mirrored) w/l/model
    # band sits *inside* the rails instead of floating past them — the "text far from the circuit" look.
    text_xs = [
        pd.transform.x + (-_TEXT_X0 - pd.text_w if pd.transform.flip else _TEXT_X0 + pd.text_w)
        for pd in placed
    ]
    top_y, bot_y = snap(min(ys) - rail_gap), snap(max(ys) + rail_gap)
    x0 = snap(min([*xs, *text_xs]) - _RAIL_MARGIN)
    x1 = snap(max([*xs, *text_xs]) + _RAIL_MARGIN)
    vdd_net = _pick_rail_net(supply, {"VDD"}, by_net)
    bot_net = _pick_rail_net(supply, {"VSS", "GND"}, by_net)

    labels: list[NetLabel] = []
    ports: list[PortPin] = []
    routes: list[Route] = []
    route_terms: dict[int, tuple[str, list[_APin]]] = {}  # rid -> (net, pins to label if dropped)
    rid = 0

    def add_route(net: str, wires: list[Wire], terms: list[_APin], *, droppable: bool = True) -> int:
        nonlocal rid
        if not wires:
            return -1
        routes.append(Route(rid, net, _to_segs(wires, net), droppable=droppable))
        route_terms[rid] = (net, terms)
        rid += 1
        return rid - 1

    # Supply rails: non-droppable, above/below every pin so they can never cross a device pin.
    rail_terminals: list[Terminal] = []
    for net, rail_y in ((vdd_net, top_y), (bot_net, bot_y)):
        if net is not None:
            add_route(net, [Wire(x0, rail_y, x1, rail_y)], [], droppable=False)
            labels.append(NetLabel(x0, rail_y, net))
            rail_terminals.append(Terminal(x0, rail_y, net))

    # Diode-connected devices (gate net == drain net): draw the gate→drain tie as a wire that loops
    # past the body before reaching the drain (so it clears the bulk pin on the drain column). The tied
    # gate pin is then already wired to the drain, so it is skipped by the routing pass below; the tie
    # is just another segment on its net, folded into that net's connectivity + labelling.
    tied_gate: set[tuple[int, int]] = set()
    for pd in placed:
        gnet, dnet = pd.nets.get("GATE"), pd.nets.get("DRAIN")
        gsp, dsp = pd.aligned.get("GATE"), pd.aligned.get("DRAIN")
        if gnet is None or gnet != dnet or gsp is None or dsp is None:
            continue
        gx, gy = apply_transform(pd.transform, gsp.x, gsp.y)
        dx, dy = apply_transform(pd.transform, dsp.x, dsp.y)
        loop = dy + (_DIODE_LOOP if dy >= pd.transform.y else -_DIODE_LOOP)  # past the drain, off-body
        tie = [Wire(gx, gy, gx, loop), Wire(gx, loop, dx, loop), Wire(dx, loop, dx, dy)]
        add_route(gnet, tie, [])
        tied_gate.add((gx, gy))

    # Per net: route the channel (drain/source/gate) pins into one connected tree of real wires, flush
    # supply pins onto their rail, and collect each bulk pin for the clearance-aware labelling pass. A
    # net's drain/source/gate pins are joined by column runs, row/gate-bus runs and L-bridges (see
    # :func:`_net_wires`); whatever the verifier must drop just falls back to a by-name label, so the net
    # stays connected with no short. Bulk pins are named on a clearance-checked stub (see below).
    bulk_pins: list[_APin] = []  # body pins, each named on its own stub (kept clear of the param text)
    rail_intents: list[tuple[str, _APin, int]] = []  # net, pin, rail-stub rid (label pin if dropped)
    sig_pins: dict[str, list[Point]] = {}  # signal net -> its non-bulk pin coords (for labelling)
    for net in sorted(by_net):
        bulk_pins.extend(p for p in by_net[net] if p.role == "bulk")
        chan = [p for p in by_net[net] if p.role != "bulk" and not p.is_source]
        if net in (vdd_net, bot_net):  # channel pins flush onto the rail (or, if a stub is dropped, a label)
            rail_y = top_y if net == vdd_net else bot_y
            for p in chan:
                rail_intents.append((net, p, add_route(net, [Wire(p.x, p.y, p.x, rail_y)], [p])))
            continue
        if not chan:
            continue
        # Lead each terminal out to its boundary-box port, then wire the net's tree *between the ports*
        # (a tied diode gate is already wired to its drain, so it grows no lead). Routing from the ports
        # keeps every corner/T-junction clear of the device bodies and their parameter text.
        for p in chan:
            if (p.x, p.y) not in tied_gate and (p.ex, p.ey) != (p.x, p.y):
                add_route(net, [Wire(p.x, p.y, p.ex, p.ey)], [])
        sig_pins[net] = sorted({(p.x, p.y) for p in chan})  # every pin, named via its connected piece
        route_pts = sorted({(p.ex, p.ey) for p in chan if (p.x, p.y) not in tied_gate})
        for w in _net_wires(route_pts):  # each segment is its own droppable route
            add_route(net, [w], [])

    # Circuit-I/O ports park at the schematic edges — inputs left, outputs right, bidirectional below —
    # and link to their net by name (the terminal that owns the net is already stub-labelled).
    edges: list[tuple[str, str, _APin]] = []  # net, role, anchor
    for pnet, role in sorted(port_role.items()):
        pterm = [p for p in by_net.get(pnet, []) if p.role != "bulk"]
        if pterm:
            edges.append((pnet, role, _anchor(pterm)))
    left = _spread(sorted(a.y for _, r, a in edges if r not in ("out", "inout")), _PORT_STEP)
    right = _spread(sorted(a.y for _, r, a in edges if r == "out"), _PORT_STEP)
    bottom = _spread(sorted(a.x for _, r, a in edges if r == "inout"), _PORT_STEP)
    lefts, rights, bottoms = iter(left), iter(right), iter(bottom)
    for edge in sorted(edges, key=lambda e: (e[1], e[2].y, e[2].x)):
        pnet, role = edge[0], edge[1]
        if role == "out":
            px, py = x1 + _PORT_MARGIN, next(rights)
        elif role == "inout":
            px, py = next(bottoms), bot_y + _PORT_MARGIN
        else:
            px, py = x0 - _PORT_MARGIN, next(lefts)
        ports.append(PortPin(snap(px), snap(py), pnet, port_symref(role)))

    # Verify the routing/diode/rail wires against xschem's merge rules; drop any route that would graze a
    # foreign net (its pins then fall back to a by-name label).
    terminals = [Terminal(p.x, p.y, p.net) for p in all_pins] + rail_terminals
    dropped = conflicting_routes(routes, terminals)
    wires: list[Wire] = []
    survived: dict[str, list[Wire]] = defaultdict(list)  # net -> the wires that survived (per net)
    for r in routes:
        if r.rid in dropped:
            continue
        rw = [Wire(s.x1, s.y1, s.x2, s.y2) for s in r.segs]
        wires.extend(rw)
        survived[r.net].extend(rw)

    # Name every remaining terminal on its own stub, kept clear of every device's clearance box. The
    # pieces to name: one per surviving connected piece of each signal net (a fully-wired net → one
    # label; a pin no wire reached → its own piece, so nothing is left unnamed — diode ties share the
    # net, so a tied gate is named with its drain), every bulk pin, and any supply pin whose rail stub
    # was dropped. Each gets a stub extended off its pin in the first direction whose endpoint, label and
    # path clear all the keepout boxes (so a flipped device's parameter text never lands under a name);
    # the label is oriented to read outward from the stub end. The chosen stubs are then verified against
    # the surviving wiring + every pin, so one that would graze a foreign net drops to a bare pin label.
    pin_at: dict[tuple[str, int, int], _APin] = {}
    for p in all_pins:
        pin_at.setdefault((p.net, p.x, p.y), p)
    keepouts = _device_keepouts(placed)
    obstacles = [
        Route(-2 - i, n, _to_segs(ws, n), droppable=False)
        for i, (n, ws) in enumerate(survived.items())
        if ws
    ]

    pieces: list[tuple[str, _APin]] = []  # (net, anchor pin) for every name to place on a stub
    for net, pts in sig_pins.items():
        for comp in _wire_components(pts, survived.get(net, [])):
            ax, ay = min(comp, key=lambda c: (c[1], c[0]))
            p = pin_at.get((net, ax, ay))
            if p is None:
                labels.append(NetLabel(ax, ay, net))
            else:
                pieces.append((net, p))
    pieces.extend((p.net, p) for p in bulk_pins)
    pieces.extend((p.net, p) for p in source_pins)  # both terminals of every source, named in place
    pieces.extend((net, p) for net, p, rid_ in rail_intents if rid_ in dropped)

    # Pick each piece's stub: the first clearance-clean candidate, else its first candidate (still better
    # than a name jammed on the pin). Collect them, then batch-verify against the drawn wiring.
    chosen: list[tuple[str, _APin, list[Wire], int, int, int, int]] = []
    for net, p in pieces:
        own = _dev_boxes(p.ox, p.oy, p.flip, p.tw)
        cands = _label_candidates(p, net)
        path, ex, ey, rot, flip, _ = next(
            (c for c in cands if _accept(c[0], c[5], keepouts, own)),
            cands[0] if cands else ([Wire(p.x, p.y, p.x, p.y)], p.x, p.y, 0, 0, own[0]),
        )
        chosen.append((net, p, path, ex, ey, rot, flip))

    stub_routes = [
        Route(200_000 + i, net, _to_segs(path, net)) for i, (net, _, path, *_) in enumerate(chosen)
    ]
    stub_bad = conflicting_routes(
        obstacles + stub_routes,
        [Terminal(p.x, p.y, p.net) for p in all_pins] + rail_terminals,
    )
    for i, (net, p, path, ex, ey, rot, flip) in enumerate(chosen):
        if (200_000 + i) in stub_bad:  # stub would graze a foreign net: name the pin in place
            labels.append(NetLabel(p.x, p.y, net))
        else:
            wires.extend(path)
            labels.append(NetLabel(ex, ey, net, rot=rot, flip=flip))

    return ConnectionPlan(wires=_merge_collinear(wires), labels=_dedupe_labels(labels), ports=ports)


def _merge_collinear(wires: list[Wire]) -> list[Wire]:
    """Coalesce collinear, overlapping-or-abutting segments into maximal runs (cosmetic, connectivity-
    preserving). Each terminal's boundary-box lead is collinear with the column/row bus it joins, and
    :func:`_net_wires` splits every run at each pin — so a straight wire piles up to three-plus coincident
    endpoints at every interior tap and overlap, and xschem draws a *solder dot* there even though
    nothing branches off. Merging the pieces back into one wire leaves a dot only where a wire genuinely
    turns or tees. Safe to do unconditionally: :mod:`.connectivity` guarantees only same-net wires ever
    touch, so two segments that overlap or abut on one line are always the same net (a foreign one would
    have been dropped), and the union never reaches past their combined span — no new geometry, no short."""
    by_v: dict[int, list[tuple[int, int]]] = defaultdict(list)  # x -> (y0, y1) vertical intervals
    by_h: dict[int, list[tuple[int, int]]] = defaultdict(list)  # y -> (x0, x1) horizontal intervals
    kept: list[Wire] = []
    for w in wires:
        if w.x1 == w.x2 and w.y1 == w.y2:
            continue  # degenerate point (a dropped-stub fallback) — never emit it
        if w.x1 == w.x2:
            by_v[w.x1].append((min(w.y1, w.y2), max(w.y1, w.y2)))
        elif w.y1 == w.y2:
            by_h[w.y1].append((min(w.x1, w.x2), max(w.x1, w.x2)))
        else:
            kept.append(w)  # not axis-aligned (shouldn't arise) — leave untouched

    def union(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
        merged: list[tuple[int, int]] = []
        for s, e in sorted(intervals):
            if merged and s <= merged[-1][1]:  # overlaps or abuts the run so far → extend it
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        return merged

    for x, ivs in sorted(by_v.items()):
        kept.extend(Wire(x, s, x, e) for s, e in union(ivs))
    for y, ivs in sorted(by_h.items()):
        kept.extend(Wire(s, y, e, y) for s, e in union(ivs))
    return kept


def _dedupe_labels(labels: list[NetLabel]) -> list[NetLabel]:
    """Drop labels that repeat an identical ``(x, y, lab)`` so net names aren't drawn twice over."""
    seen: set[tuple[int, int, str]] = set()
    out: list[NetLabel] = []
    for lbl in labels:
        key = (lbl.x, lbl.y, lbl.lab)
        if key not in seen:
            seen.add(key)
            out.append(lbl)
    return out


def build_labels(placed: list[PlacedDevice]) -> list[NetLabel]:
    """Label every device pin with its net name (the simple, always-correct wiring mode)."""
    labels: list[NetLabel] = []
    for pd in placed:
        for canon, sym_pin in pd.aligned.items():
            ax, ay = apply_transform(pd.transform, sym_pin.x, sym_pin.y)
            labels.append(NetLabel(x=ax, y=ay, lab=pd.nets[canon]))
    return labels
