"""Connection planning: wire every net's gate/source/drain pins into one connected tree, with a
net-name label per surviving piece carrying connectivity wherever a wire had to be dropped.

Given a topology placement this plans, for every device terminal:

* **signal nets** (the drain/source/gate pins of a net) → an orthogonal tree of real wires: per-column
  vertical runs and per-row horizontal runs (a leg's drain/source stack and a row of mirror gates each
  become one straight wire — the latter is the gate bus), then L-bridges joining whatever the runs left
  apart (see :func:`_net_wires`). A net the verifier still leaves in two islands gets a
  three-segment **detour** attempt around the obstacle (:func:`_detour_paths`) before its pins fall
  back to names. One net-name label is dropped per surviving connected piece;
* **diode-connected devices** (gate net == drain net) → an explicit gate→drain **tie** that loops
  past the body before reaching the drain (so it clears the body pin on the drain column) — just
  another segment on its net, folded into that net's tree and labelling;
* **body (bulk) pins** → a short stub that steps out then drops clear of the device's parameter text,
  then a net-name label (the body is named, never merged into a leg);
* **supply nets** (VDD / VSS / GND) → a horizontal rail (VDD top, VSS/GND bottom); each device's
  supply drain/source pin flushes onto its rail with a short vertical stub. A supply whose terminals
  are *all* body pins still gets its rail (it is the landmark a reader looks for first), named at the
  rail and with its bulk pins labelled as usual;
* **port nets** (circuit I/O — declared ``.subckt`` ports or dangling external nodes) → an
  ``ipin``/``opin``/``iopin`` **port symbol** placed **on its net's outermost drawn wire end**
  (inputs leftmost, outputs rightmost, bidirectional lowest), so the port IS the connection and the
  net is not named twice; only a net with no drawn wire at all keeps the old parked-at-the-frame pin,
  and those are reported in :attr:`ConnectionPlan.parked_ports`;
* **independent sources** (V/I, parked bottom-left by the placer) → **both terminals named in place**
  and nothing else: a source is never wired, flushed to a rail, or joined into a net's wire tree, so it
  connects to the circuit purely by the net name on each terminal. The rest of the net is wired among
  its non-source pins exactly as if the source were absent.

Every drawn segment is checked against :mod:`.connectivity`, which models xschem's net-merge rules
exactly: any segment that would touch a foreign net's pin or wire is dropped and the pins it would have
joined fall back to net-name labels (always correct regardless of geometry). So we wire aggressively
for readability yet never ship a short, and nothing is ever left floating — the Docker round-trip
(`xschem -n -s`) is the final gate.

**A run may never end in mid-air.** Dropping one leg of an L used to leave the other leg reaching to a
point that touches nothing: a wire that *looks* like the connection, joins nothing, and hands xschem an
unnamed island — a silent open, strictly worse than the by-name fallback. So every routed run is
emitted as one indivisible route, and :func:`_prune_dangling` then drops any run whose endpoint does
not land on a pin, a wire or a label of its own net. Whatever that leaves unjoined is reported by net
name in :attr:`ConnectionPlan.by_name`, so a caller can see how much of the sheet is still drawn by
name rather than by wire.

**Channel routing is a helper the caller asks for** (``router="channel"``; issue #243). It is
off by default: with ``router="per-route"`` every sheet is drawn exactly as before it existed.
When asked, a sheet of two or more block symbols and no MOSFET (a top level) has the runs above
replaced by :mod:`.channels`: the gaps between block columns and rows are reserved as channels,
each net gets one lane per channel it enters, and each supply gets one rail per block row joined
by a spine at the sheet edge. The supply routes are verified first and then held fixed while the
signal routes are verified. Everything after route generation — the verifier, the detour pass,
the dangling-run rule, the ports and the naming — is the same code for both. Any other sheet is
drawn by the per-route planner even when channels are asked for, and :attr:`ConnectionPlan.router`
says which one drew it. Label stubs and detours are checked against a block's drawn extent
(``PlacedDevice.body``, which :func:`~.emit.build_sch` sets only when channels are asked for)
instead of the transistor-sized box; the per-route runs are not checked against it.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Literal

from .channels import DevicePins, channel_deficits, channel_layout
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
    "RouterMode",
    "check_router",
    "NetLabel",
    "Wire",
    "PortPin",
    "PlacedDevice",
    "PinRef",
    "ConnectionPlan",
    "plan_connections",
    "spread_channels",
    "build_labels",
    "device_extent",
]

#: The two routers :func:`plan_connections` can draw a sheet with. ``"per-route"`` is the default
#: and the only one used unless a caller asks; ``"channel"`` routes a block diagram by channels.
RouterMode = Literal["per-route", "channel"]
_ROUTERS: tuple[RouterMode, ...] = ("per-route", "channel")


def check_router(router: str) -> None:
    """Raise ``ValueError`` unless ``router`` names one of :data:`RouterMode`'s routers."""
    if router not in _ROUTERS:
        raise ValueError(f"router must be one of {', '.join(_ROUTERS)}, got {router!r}")


_RAIL_GAP = 80  # vertical gap from the outermost device pins to the supply rail lines
_RAIL_MARGIN = 60  # horizontal overhang of a rail past the outermost pin column
_PORT_MARGIN = 140  # gap from the device bbox to the port pins parked at the schematic edges
_PORT_STEP = 120  # vertical/horizontal spacing when several ports stack on the same edge
_DIODE_LOOP = (
    40  # how far a diode-connect gate→drain tie loops past the device to clear the body pin
)
_LABEL_STUB = 60  # length of the wire a net name is pulled onto, off the symbol, before its label
_DETOUR_LANES = (60, 120, 200, 320)  # outward lane offsets tried when routing round an obstacle
_MAX_ISLANDS = (
    8  # give up detouring a net split into more pieces than this (keeps the pass bounded)
)
_PORT_LEAD = 60  # how far a port pin is pulled out past the free wire end it attaches to
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
# 60, not 22 (issue #244): the generic MOS symbols anchor their `@w\/@l\/@m` (hsize 0.2) and
# `@model` (hsize 0.15) lines at local x=60, so the drain/source pin column at x=+-20 -- and every
# wire, lead and label stub the wiring layer draws on it -- is clear of the text instead of running
# through it. The 40 units between the column and the anchor are an overflow budget for the
# MIRRORED case: a flipped device mirrors the anchor and xschem right-justifies the string using
# its OWN width estimate, while the SVG export draws a wider proportional font from that same left
# edge, so the string overruns its box to the right -- measured ~3.0 drawn units per character at
# hsize 0.2 and ~2.4 at 0.15. 40 units therefore cover roughly 13 characters of sizing text and 16
# of model name; a longer one grazes the column again, on flipped devices only.
_TEXT_X0 = 60  # where the parameter text starts, on the +x (gate-opposite) side
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
    text_w: int = (
        _TEXT_REACH  # how far the symbol's w/l/model text reaches (sized to the actual strings)
    )
    is_source: bool = (
        False  # an independent V/I source: both terminals named, never wired (see below)
    )
    #: A block symbol (a subcircuit drawn with a design's own ``.sym``): two or more of them, and no
    #: MOSFET, make the sheet a block diagram, which ``router="channel"`` routes by channels.
    is_block: bool = False
    #: The symbol's drawn extent, symbol-local (``Symbol.bbox``). Set for a block, whose body is far
    #: larger than the transistor-sized keep-out assumed otherwise; ``None`` keeps that keep-out.
    #: :func:`~.emit.build_sch` sets it only when channel routing is asked for.
    body: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class PinRef:
    """One device pin instance on a net, at its absolute schematic coordinate."""

    x: int
    y: int


@dataclass(frozen=True)
class ConnectionPlan:
    """The planned drawing: wires, net-name labels, port pins — and what is still drawn by name.

    ``by_name`` lists every net whose terminals the drawn wiring still leaves in more than one piece,
    so its connectivity is carried by the net-name labels rather than by a wire; ``parked_ports``
    lists the circuit-I/O nets whose port pin had to fall back to a pin parked at the frame (no drawn
    wire of that net to place it on). Both are sorted and reportable — a reader of the sheet cannot
    tell a named join from a drawn one, so the planner says how many there are.
    """

    wires: list[Wire] = field(default_factory=list)
    labels: list[NetLabel] = field(default_factory=list)
    ports: list[PortPin] = field(default_factory=list)
    by_name: list[str] = field(default_factory=list)
    parked_ports: list[str] = field(default_factory=list)
    #: Which router drew the sheet: ``"channel"`` for a block diagram when channels were asked
    #: for (:mod:`.channels`), ``"per-route"`` otherwise. ``lanes`` is the number of lanes
    #: reserved per channel (``("v", i)`` / ``("h", j)``), empty for the per-route planner.
    router: str = "per-route"
    lanes: dict[tuple[str, int], int] = field(default_factory=dict)
    #: Each net in ``by_name`` that has pins in more than one drawn piece, and how many pieces.
    pieces: dict[str, int] = field(default_factory=dict)
    #: The nets the channel router left, at least in part, to their names before any wire was
    #: checked: a lane past its channel's capacity, or a pin taken out of an ordering loop.
    unrouted: list[str] = field(default_factory=list)
    #: Per supply net on the sheet: ``rails`` (the per-route planner's sheet rail, or one track
    #: per block row), ``spines`` (the channel router's outer lane joining the rails), ``taps``
    #: (the wires from supply pins to a rail) drawn, and ``refused`` (planned supply wires that the
    #: connectivity check or the dangling-run rule removed).
    supply: dict[str, dict[str, int]] = field(default_factory=dict)


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
    body: Box | None = None  # a block's absolute drawn extent (its keep-out), else None


def _abs_body(pd: PlacedDevice) -> Box | None:
    """A block's drawn extent in sheet coordinates (the symbol bbox through its placement)."""
    if pd.body is None:
        return None
    x0, y0, x1, y1 = pd.body
    pts = [apply_transform(pd.transform, x, y) for x, y in ((x0, y0), (x1, y1))]
    return (
        min(p[0] for p in pts),
        min(p[1] for p in pts),
        max(p[0] for p in pts),
        max(p[1] for p in pts),
    )


def _keepout(pd: PlacedDevice) -> list[Box]:
    """One device's keep-out boxes: a block's drawn body, else the transistor-sized body + text."""
    body = _abs_body(pd)
    if body is not None:
        return [body]
    return _dev_boxes(pd.transform.x, pd.transform.y, pd.transform.flip, pd.text_w)


def _abs_pins(placed: list[PlacedDevice]) -> list[_APin]:
    out: list[_APin] = []
    for pd in placed:
        body = _abs_body(pd)
        for canon, sp in pd.aligned.items():
            x, y = apply_transform(pd.transform, sp.x, sp.y)
            role = _PIN_ROLE.get(canon, "term")
            ex, ey = x, y
            # A source pin grows no boundary-box lead — it is never wired, only named in place.
            if (
                role != "bulk" and not pd.is_source
            ):  # extend the terminal out to its port along its normal
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
                    body=body,
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
    """The supply net (of the given role set) that gets the rail, picked deterministically by name.

    A net with a **wirable** (non-bulk) pin wins, because its pins can flush onto the rail. A supply
    whose terminals are *all* body pins used to get no rail at all and drew as a scatter of label
    stubs — the rails simply absent from a sheet whose reader looks for them first — so it is now the
    second choice rather than no choice: the rail is drawn and named, and the bulk pins keep their
    clearance-checked name stubs (a body pin shares its column with the drain/source pins of other
    nets, so a stub flushing it to the rail would be refused by the verifier every time).
    """
    for wirable in (True, False):
        for net in sorted(supply):
            pins = by_net.get(net, [])
            if supply[net] in roles and pins and any(p.role != "bulk" for p in pins) == wirable:
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


def _net_wires(pts: list[Point]) -> list[list[Wire]]:
    """Orthogonal **runs** joining all of a net's pins into one connected tree.

    Per-column **vertical runs** and per-row **horizontal runs** link pins that share an x or a y (so a
    leg's drain/source stack and a row of mirror gates each become one straight wire — the gate bus of
    requirement 4); whatever the runs leave in separate pieces is bridged by an L between the two nearest
    pins. Every run is a candidate the connectivity verifier may drop — a dropped run simply
    leaves its pins linked by net name — so this only ever *adds* readable wiring, never a short.

    Each returned element is one **indivisible** run: a straight span between adjacent pins is a
    single wire, and an L-bridge is its two legs *together*. Dropping one leg of an L on its own is
    what left a trunk ending in mid-air — a wire that joins nothing and hands xschem an unnamed
    island — so the legs stand or fall as one.
    """
    pts = sorted(set(pts))
    if len(pts) <= 1:
        return []
    segs: list[list[Wire]] = []
    by_x: dict[int, list[int]] = defaultdict(list)
    by_y: dict[int, list[int]] = defaultdict(list)
    for x, y in pts:
        by_x[x].append(y)
        by_y[y].append(x)
    # Split each run into segments between *adjacent* pins, not one span end-to-end: a gate bus that
    # must cross one foreign pin then loses only that span (the rest of the mirror stays wired).
    for x, ys in by_x.items():
        ys = sorted(set(ys))
        segs.extend([Wire(x, y1, x, y2)] for y1, y2 in zip(ys, ys[1:]))
    for y, xs in by_y.items():
        xs = sorted(set(xs))
        segs.extend([Wire(x1, y, x2, y)] for x1, x2 in zip(xs, xs[1:]))
    comps = sorted(_grid_components(pts), key=min)
    for prev, cur in zip(comps, comps[1:]):  # bridge separate pieces with an L (h-leg then v-leg)
        (ax, ay), (bx, by) = _closest_pair(prev, cur)
        if ax != bx and ay != by:
            segs.append([Wire(ax, ay, bx, ay), Wire(bx, ay, bx, by)])
        elif (ax, ay) != (bx, by):
            segs.append([Wire(ax, ay, bx, by)])
    return segs


def _detour_paths(a: Point, b: Point) -> list[list[Wire]]:
    """Three-segment routes from ``a`` to ``b`` that step out into a lane and back, nearest lane first.

    The route a designer draws when the straight join is blocked: out of the way, along, and back in.
    Both families are offered — an x-lane (out sideways, down, back) and a y-lane (out vertically,
    across, back) — because which one is free depends on what is in the way: a drain/source tie that
    must pass a body pin in its own column needs the x-lane; two pins on one row blocked by a
    foreign pin between them need the y-lane.
    """
    (ax, ay), (bx, by) = a, b
    out: list[list[Wire]] = []
    for d in _DETOUR_LANES:
        for mx in (min(ax, bx) - d, max(ax, bx) + d):
            out.append([Wire(ax, ay, mx, ay), Wire(mx, ay, mx, by), Wire(mx, by, bx, by)])
        for my in (min(ay, by) - d, max(ay, by) + d):
            out.append([Wire(ax, ay, ax, my), Wire(ax, my, bx, my), Wire(bx, my, bx, by)])
    return [[w for w in path if (w.x1, w.y1) != (w.x2, w.y2)] for path in out]


def _detour_routes(
    net: str,
    islands: list[list[Point]],
    obstacles: list[Route],
    terminals: list[Terminal],
    keepouts: list[Box],
    own: Mapping[Point, list[Box]],
    rid0: int,
) -> list[list[Wire]]:
    """Detours joining a net left in several islands — each verified so no short is ever drawn.

    Consecutive islands (ordered, so the chain ends up one piece) are joined at their closest pair of
    attachment points. A candidate must clear every device's keepout box (its own two endpoints'
    devices excepted — that is where it starts) and then survive
    :func:`~.connectivity.conflicting_routes` against the geometry already drawn, which is handed in
    as *non-droppable* obstacles so only the candidate can ever be the one refused. The first
    survivor wins and becomes an obstacle for the next join.
    """
    accepted: list[list[Wire]] = []
    if not 1 < len(islands) <= _MAX_ISLANDS:
        return accepted
    obs = list(obstacles)
    for prev, cur in zip(islands, islands[1:]):
        a, b = _closest_pair(prev, cur)
        exempt = [*own.get(a, []), *own.get(b, [])]
        for path in _detour_paths(a, b):
            if not path:
                continue
            if any(
                box not in exempt and _box_overlaps(_seg_box(w), box, 4)
                for w in path
                for box in keepouts
            ):
                continue
            cand = Route(rid0 + len(accepted), net, _to_segs(path, net))
            if cand.rid in conflicting_routes([*obs, cand], terminals):
                continue
            accepted.append(path)
            obs.append(Route(cand.rid, net, cand.segs, droppable=False))
            break
    return accepted


def _attachments(
    comp: list[Point], port_of: Mapping[Point, Point | None], drawn_ends: set[Point]
) -> list[Point]:
    """Where a detour may join an island: each pin's boundary-box port, or the pin itself.

    The port is the point outside the device body that the net's tree is wired between, so it is the
    natural place to leave from — but only when the pin's lead actually survived and put a wire end
    there. Otherwise the pin is the only point of this island a wire can legally reach."""
    return sorted({port if (port := port_of.get(pt)) in drawn_ends else pt for pt in comp})


def _prune_dangling(
    drawn: dict[str, list[tuple[list[Wire], bool]]], anchors: Mapping[str, set[Point]]
) -> list[Wire]:
    """Drop every prunable run of ``drawn`` that ends in mid-air; return what was dropped.

    A run's endpoint must land on a pin of its own net, on a label of its own net, or on another
    surviving wire of its own net. Anything else is a wire drawn to nowhere: it reads as the
    connection, carries none, and leaves xschem naming the island it failed to reach. Runs marked
    un-prunable (a terminal's own lead, a diode tie, a rail and its stubs) are anchored on a pin by
    construction and are kept — they are stubs, not joins. Removal can orphan another run, so this
    iterates to a fixed point.
    """
    dropped: list[Wire] = []
    changed = True
    while changed:
        changed = False
        for net, runs in drawn.items():
            kept: list[tuple[list[Wire], bool]] = []
            for i, (path, prunable) in enumerate(runs):
                if prunable and not _run_anchored(
                    net, path, runs, i, anchors.get(net, frozenset())
                ):
                    dropped.extend(path)
                    changed = True
                else:
                    kept.append((path, prunable))
            drawn[net] = kept
    return dropped


def _run_anchored(
    net: str,
    path: list[Wire],
    runs: list[tuple[list[Wire], bool]],
    i: int,
    anchors: frozenset[Point] | set[Point],
) -> bool:
    """Does every endpoint of run ``i`` land on something of its own net (see :func:`_prune_dangling`)?"""
    inner = [Seg(w.x1, w.y1, w.x2, w.y2, net) for w in path]
    others = [
        Seg(w.x1, w.y1, w.x2, w.y2, net)
        for j, (other, _) in enumerate(runs)
        if j != i
        for w in other
    ]
    for k, w in enumerate(path):
        for p in ((w.x1, w.y1), (w.x2, w.y2)):
            if p in anchors:
                continue
            if any(_point_on_seg(p[0], p[1], s) for s in others):
                continue
            if any(_point_on_seg(p[0], p[1], s) for j, s in enumerate(inner) if j != k):
                continue
            return False
    return True


_PORT_DIR = {
    "in": (-1, 0),
    "out": (1, 0),
    "inout": (0, 1),
}  # which way a port faces out of the sheet


def _port_rank(role: str, p: Point) -> tuple[int, int]:
    """How far out (towards this role's edge) a candidate point sits — smaller is further out."""
    dx, dy = _PORT_DIR.get(role, _PORT_DIR["in"])
    return (-(dx * p[0] + dy * p[1]), p[1] if dx else p[0])


def _port_anchor(role: str, wires: list[Wire], pin_pts: set[Point]) -> Point | None:
    """The wire end this net's port pin should sit on: outermost towards the role's edge.

    A **free** end (one wire and nothing else) is preferred over a junction, and a bare wire end over
    one that is also a device pin — a port belongs where the net runs out, not on top of a body. The
    point is an endpoint of a surviving wire of this net, and the verifier has already dropped
    anything foreign that touched it, so naming it with a port symbol can never merge two nets.
    """
    if not wires:
        return None
    segs = [Seg(w.x1, w.y1, w.x2, w.y2, "") for w in wires]
    ends = {p for w in wires for p in ((w.x1, w.y1), (w.x2, w.y2))}
    return min(
        ends,
        key=lambda p: (
            p in pin_pts,
            sum(1 for s in segs if _point_on_seg(p[0], p[1], s)) > 1,
            *_port_rank(role, p),
        ),
    )


def _port_lead(role: str, p: Point, wires: list[Wire]) -> Wire | None:
    """A short wire pulling the port pin out past a free end, when that end already faces its edge.

    Only drawn where it is the natural continuation of the run (the attached wire is collinear with
    the role's direction and comes in from the other side), so the lead never doubles back over the
    wiring it extends. The caller still verifies it like any other route.
    """
    dx, dy = _PORT_DIR.get(role, _PORT_DIR["in"])
    touching = [w for w in wires if _point_on_seg(p[0], p[1], Seg(w.x1, w.y1, w.x2, w.y2, ""))]
    if len(touching) != 1:
        return None
    w = touching[0]
    far = (w.x2, w.y2) if (w.x1, w.y1) == p else (w.x1, w.y1)
    if far == p or (far[0] - p[0]) * dx > 0 or (far[1] - p[1]) * dy > 0:
        return None  # not a free end, or the run continues the way the port would go
    if (far[0] != p[0] and dy) or (far[1] != p[1] and dx):
        return None  # the run is perpendicular to the port's direction — leave the pin on its end
    return Wire(p[0], p[1], p[0] + dx * _PORT_LEAD, p[1] + dy * _PORT_LEAD)


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


def _pin_boxes(p: _APin) -> list[Box]:
    """The keep-out boxes of the device a pin belongs to (its own body is where a stub starts)."""
    return [p.body] if p.body is not None else _dev_boxes(p.ox, p.oy, p.flip, p.tw)


def _device_keepouts(placed: list[PlacedDevice]) -> list[Box]:
    """Every device's clearance boxes (symbol + parameter text) — a label or its stub must stay out of
    these, which is what kept a flipped device's leftward w/l/model text from colliding with names."""
    return [b for pd in placed for b in _keepout(pd)]


def device_extent(pd: PlacedDevice) -> Box:
    """The absolute bounding box of one placed device: its symbol body *plus* its parameter-text band.

    The union of :func:`_dev_boxes` (the same tuned body/text geometry the wiring keep-out uses), so a
    caller that draws a box around a group of devices — the functional-block annotation overlay — can
    enclose each device without clipping its w/l/model text. Devices are only ever placed ``rot=0``, so
    the result is axis-aligned and ``flip`` only mirrors the text band's x-extent."""
    boxes = _keepout(pd)
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
            out.append(
                ([Wire(px, py, nudge, py), Wire(nudge, py, nudge, ey)], nudge, ey, rot, flip, lbox)
            )
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
    router: RouterMode = "per-route",
) -> ConnectionPlan:
    """Plan wires, labels, and port pins for a placed circuit (see the module docstring).

    ``supply`` maps a net to ``VDD``/``VSS``/``GND`` (rail hints); ``port_role`` maps a circuit-I/O net
    to ``in``/``out``/``inout`` (drawn as a port pin on that net's outermost drawn wire end). Each net
    is wired into one tree where the geometry allows it — straight runs, L-bridges, then a detour
    round the obstacle — and whatever stays apart falls back to a net-name label per piece. Every
    route is verified against :mod:`.connectivity` (so a route that would graze a foreign net is
    refused, never drawn) and every surviving run must end on its own net's geometry (so a refused
    leg can never leave the rest of the run reaching into empty space). The result always re-netlists
    to the original connectivity; :attr:`ConnectionPlan.by_name` reports what is still joined by name.

    ``router="channel"`` asks for channel routing (see the module docstring): a block diagram is then
    drawn by :mod:`.channels`, and any other sheet still by the per-route planner. The default,
    ``"per-route"``, never computes a channel layout. Any other value raises ``ValueError``.
    """
    check_router(router)
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
    xs = [
        v for p in all_pins for v in (p.x, p.ex)
    ]  # include the boundary ports in the frame extent
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
    # Asked for channels, a block diagram is routed by them (issue #243): one rail per block row
    # instead of the two sheet-wide rails, and one lane per net per channel instead of runs placed
    # one at a time. Not asked, no channel layout is computed and the sheet is drawn as before.
    layout = channel_layout(_device_pins(placed), supply) if router == "channel" else None
    vdd_net = _pick_rail_net(supply, {"VDD"}, by_net) if layout is None else None
    bot_net = _pick_rail_net(supply, {"VSS", "GND"}, by_net) if layout is None else None

    labels: list[NetLabel] = []
    ports: list[PortPin] = []
    routes: list[Route] = []
    route_terms: dict[int, tuple[str, list[_APin]]] = {}  # rid -> (net, pins to label if dropped)
    prunable: dict[int, bool] = {}  # rid -> is this run a JOIN (prunable) or a stub off a pin?
    rid = 0

    def add_route(
        net: str,
        wires: list[Wire],
        terms: list[_APin],
        *,
        droppable: bool = True,
        joins: bool = False,
    ) -> int:
        nonlocal rid
        if not wires:
            return -1
        routes.append(Route(rid, net, _to_segs(wires, net), droppable=droppable))
        route_terms[rid] = (net, terms)
        prunable[rid] = joins
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
        loop = dy + (
            _DIODE_LOOP if dy >= pd.transform.y else -_DIODE_LOOP
        )  # past the drain, off-body
        tie = [Wire(gx, gy, gx, loop), Wire(gx, loop, dx, loop), Wire(dx, loop, dx, dy)]
        add_route(gnet, tie, [])
        tied_gate.add((gx, gy))

    # Per net: route the channel (drain/source/gate) pins into one connected tree of real wires, flush
    # supply pins onto their rail, and collect each bulk pin for the clearance-aware labelling pass. A
    # net's drain/source/gate pins are joined by column runs, row/gate-bus runs and L-bridges (see
    # :func:`_net_wires`); whatever the verifier must drop just falls back to a by-name label, so the net
    # stays connected with no short. Bulk pins are named on a clearance-checked stub (see below).
    bulk_pins: list[
        _APin
    ] = []  # body pins, each named on its own stub (kept clear of the param text)
    rail_intents: list[
        tuple[str, _APin, int]
    ] = []  # net, pin, rail-stub rid (label pin if dropped)
    sig_pins: dict[str, list[Point]] = {}  # signal net -> its non-bulk pin coords (for labelling)
    port_of: dict[tuple[str, Point], Point] = {}  # (net, pin) -> its boundary-box port
    for net in sorted(by_net):
        bulk_pins.extend(p for p in by_net[net] if p.role == "bulk")
        chan = [p for p in by_net[net] if p.role != "bulk" and not p.is_source]
        if net in (
            vdd_net,
            bot_net,
        ):  # channel pins flush onto the rail (or, if a stub is dropped, a label)
            rail_y = top_y if net == vdd_net else bot_y
            for p in chan:
                rail_intents.append((net, p, add_route(net, [Wire(p.x, p.y, p.x, rail_y)], [p])))
            continue
        if not chan:
            continue
        if layout is not None:  # the channel router draws every run of the net (added below)
            sig_pins[net] = sorted({(p.x, p.y) for p in chan})
            for p in chan:
                port_of[(net, (p.x, p.y))] = (p.x, p.y)
                if len(sig_pins[net]) == 1 and (p.ex, p.ey) != (p.x, p.y):
                    # a lone pin gets its lead, so a port pin on this net has a wire to sit on
                    add_route(net, [Wire(p.x, p.y, p.ex, p.ey)], [])
            continue
        # Lead each terminal out to its boundary-box port, then wire the net's tree *between the ports*
        # (a tied diode gate is already wired to its drain, so it grows no lead). Routing from the ports
        # keeps every corner/T-junction clear of the device bodies and their parameter text.
        for p in chan:
            port_of[(net, (p.x, p.y))] = (p.ex, p.ey)
            if (p.x, p.y) not in tied_gate and (p.ex, p.ey) != (p.x, p.y):
                add_route(net, [Wire(p.x, p.y, p.ex, p.ey)], [])
        sig_pins[net] = sorted(
            {(p.x, p.y) for p in chan}
        )  # every pin, named via its connected piece
        route_pts = sorted({(p.ex, p.ey) for p in chan if (p.x, p.y) not in tied_gate})
        for run in _net_wires(route_pts):  # each run is its own droppable route, legs together
            add_route(net, run, [], joins=True)

    layout_kind: dict[int, tuple[str, str]] = {}  # rid -> (net, kind) of a channel-router route
    if layout is not None:
        for cr in layout.routes:  # supplies first: rails, spines, taps; then the signals
            rid_ = add_route(cr.net, [Wire(*w) for w in cr.wires], [], joins=True)
            layout_kind[rid_] = (cr.net, cr.kind)

    # Verify the routing/diode/rail wires against xschem's merge rules; drop any route that would graze a
    # foreign net (its pins then fall back to a by-name label).
    terminals = [Terminal(p.x, p.y, p.net) for p in all_pins] + rail_terminals
    if layout is None:
        dropped = conflicting_routes(routes, terminals)
    else:
        # Supplies first: a supply route is checked on its own, and what survives is fixed before the
        # signals are checked against it, so a signal wire that touches a rail is the one refused.
        rails = [r for r in routes if r.net in supply]
        dropped = conflicting_routes(rails, terminals)
        fixed = [
            Route(r.rid, r.net, r.segs, droppable=False) for r in rails if r.rid not in dropped
        ]
        signals = [r for r in routes if r.net not in supply]
        dropped |= conflicting_routes(fixed + signals, terminals)
    drawn: dict[str, list[tuple[list[Wire], bool]]] = defaultdict(list)  # net -> surviving runs
    layout_path: dict[int, list[Wire]] = {}  # rid -> its run as drawn (kept, so the report can
    #                                          tell which ones the dangling-run rule removes)
    for r in routes:
        if r.rid in dropped:
            continue
        path = [Wire(s.x1, s.y1, s.x2, s.y2) for s in r.segs]
        drawn[r.net].append((path, prunable[r.rid]))
        if r.rid in layout_kind:
            layout_path[r.rid] = path

    def net_wires(net: str) -> list[Wire]:
        return [w for path, _ in drawn.get(net, []) for w in path]

    def obstacles(start: int = -2) -> list[Route]:
        """Everything already drawn, as routes nothing may be checked *against* and removed."""
        return [
            Route(start - i, n, _to_segs(ws, n), droppable=False)
            for i, n in enumerate(sorted(drawn))
            if (ws := net_wires(n))
        ]

    keepouts = _device_keepouts(placed)
    own_boxes: dict[Point, list[Box]] = {}
    for p in all_pins:
        boxes = _pin_boxes(p)
        own_boxes.setdefault((p.x, p.y), boxes)
        own_boxes.setdefault((p.ex, p.ey), boxes)

    # A net the verifier left in two islands — the classic being a drain/source tie that has to pass
    # the body pin sitting between the two devices — gets a three-segment detour round the obstacle
    # before anything falls back to a name. Every candidate is checked against the drawn geometry, so
    # a detour that would short is refused rather than drawn.
    rid_detour = 100_000
    for net in sorted(sig_pins):
        pts = sig_pins[net]
        comps = _wire_components(pts, net_wires(net))
        if len(comps) < 2:
            continue
        ends = {e for w in net_wires(net) for e in ((w.x1, w.y1), (w.x2, w.y2))}
        islands = [
            _attachments(comp, {pt: port_of.get((net, pt)) for pt in pts}, ends)
            for comp in sorted(comps, key=min)
        ]
        joins = _detour_routes(
            net, islands, obstacles(), terminals, keepouts, own_boxes, rid_detour
        )
        rid_detour += len(joins) + 1
        drawn[net].extend((path, True) for path in joins)

    # Nothing may end in mid-air: a run whose endpoint lands on no pin, wire or label of its own net
    # is a wire drawn to nowhere (the silent open), so it goes and its pins fall back to names.
    anchors: dict[str, set[Point]] = defaultdict(set)
    for p in all_pins:
        anchors[p.net].add((p.x, p.y))
    for lbl in labels:
        anchors[lbl.lab].add((lbl.x, lbl.y))
    _prune_dangling(drawn, anchors)
    supply_counts = _supply_counts(
        supply, by_net, (vdd_net, bot_net), rail_intents, dropped, layout_kind, layout_path, drawn
    )

    # Circuit-I/O ports: the port pin IS the connection — it sits on the outermost end of its own
    # net's drawn wiring (pulled one short lead further out when that end already faces its edge), so
    # the net is not drawn once as a wire and again as a pin parked at the frame. Only a net with no
    # drawn wire at all keeps the parked pin, and it is reported in ``parked_ports``.
    edges: list[tuple[str, str, _APin]] = []  # net, role, anchor
    for pnet, role in sorted(port_role.items()):
        pterm = [p for p in by_net.get(pnet, []) if p.role != "bulk"]
        if pterm:
            edges.append((pnet, role, _anchor(pterm)))
    parked_edges: list[tuple[str, str, _APin]] = []
    port_pts: dict[str, set[Point]] = defaultdict(set)
    rid_port = 300_000
    for pnet, role, panchor in sorted(edges, key=lambda e: (e[1], e[2].y, e[2].x)):
        pt = _port_anchor(role, net_wires(pnet), {(p.x, p.y) for p in all_pins})
        if pt is None:
            parked_edges.append((pnet, role, panchor))
            continue
        lead = _port_lead(role, pt, net_wires(pnet))
        if lead is not None:
            cand = Route(rid_port, pnet, _to_segs([lead], pnet))
            rid_port += 1
            if cand.rid not in conflicting_routes([*obstacles(), cand], terminals):
                drawn[pnet].append(([lead], False))
                pt = (lead.x2, lead.y2)
        port_pts[pnet].add(pt)
        ports.append(PortPin(pt[0], pt[1], pnet, port_symref(role)))

    # The fallback: a port whose net has no drawn wire still parks at the schematic edge (inputs left,
    # outputs right, bidirectional below) and links to its terminal by name.
    left = _spread(sorted(a.y for _, r, a in parked_edges if r not in ("out", "inout")), _PORT_STEP)
    right = _spread(sorted(a.y for _, r, a in parked_edges if r == "out"), _PORT_STEP)
    bottom = _spread(sorted(a.x for _, r, a in parked_edges if r == "inout"), _PORT_STEP)
    lefts, rights, bottoms = iter(left), iter(right), iter(bottom)
    for pnet, role, _panchor in sorted(parked_edges, key=lambda e: (e[1], e[2].y, e[2].x)):
        if role == "out":
            px, py = x1 + _PORT_MARGIN, next(rights)
        elif role == "inout":
            px, py = next(bottoms), bot_y + _PORT_MARGIN
        else:
            px, py = x0 - _PORT_MARGIN, next(lefts)
        ports.append(PortPin(snap(px), snap(py), pnet, port_symref(role)))

    # Name every remaining terminal on its own stub, kept clear of every device's clearance box. The
    # pieces to name: one per surviving connected piece of each signal net that no port pin already
    # names (a fully-wired net → one label; a pin no wire reached → its own piece, so nothing is left
    # unnamed — diode ties share the net, so a tied gate is named with its drain), every bulk pin, and
    # any supply pin whose rail stub was dropped. Each gets a stub extended off its pin in the first
    # direction whose endpoint, label and path clear all the keepout boxes (so a flipped device's
    # parameter text never lands under a name); the label is oriented to read outward from the stub
    # end. The chosen stubs are then verified against the surviving wiring + every pin, so one that
    # would graze a foreign net drops to a bare pin label.
    pin_at: dict[tuple[str, int, int], _APin] = {}
    for p in all_pins:
        pin_at.setdefault((p.net, p.x, p.y), p)

    pieces: list[tuple[str, _APin]] = []  # (net, anchor pin) for every name to place on a stub
    for net, pts in sig_pins.items():
        named = port_pts.get(net, set())
        for comp in _wire_components([*pts, *sorted(named)], net_wires(net)):
            if any(c in named for c in comp):
                continue  # the port pin already names this piece — a second name is clutter
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
        own = _pin_boxes(p)
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
        obstacles() + stub_routes,
        [Terminal(p.x, p.y, p.net) for p in all_pins]
        + rail_terminals
        + [Terminal(p.x, p.y, p.net) for p in ports],
    )
    for i, (net, p, path, ex, ey, rot, flip) in enumerate(chosen):
        if (200_000 + i) in stub_bad:  # stub would graze a foreign net: name the pin in place
            labels.append(NetLabel(p.x, p.y, net))
        else:
            drawn[net].append((path, False))
            labels.append(NetLabel(ex, ey, net, rot=rot, flip=flip))

    # What is still carried by NAME rather than by wire: a net whose own terminals the drawn wiring
    # leaves in more than one piece (body pins and source terminals are named by design and never
    # counted), plus every port that had to park. A reader cannot tell a named join from a drawn one,
    # so the planner reports them.
    joined_pins = {
        net: sorted({(p.x, p.y) for p in ps if p.role != "bulk" and not p.is_source})
        for net, ps in by_net.items()
    }
    piece_count = {
        net: k
        for net, pts in joined_pins.items()
        if len(pts) > 1 and (k := len(_wire_components(pts, net_wires(net)))) > 1
    }
    by_name = sorted(set(piece_count) | {pnet for pnet, _r, _a in parked_edges})

    wires = [w for net in sorted(drawn) for path, _ in drawn[net] for w in path]
    named_by_port = {(p.x, p.y, p.net) for p in ports}
    labels = [lbl for lbl in labels if (lbl.x, lbl.y, lbl.lab) not in named_by_port]
    return ConnectionPlan(
        wires=_merge_collinear(wires),
        labels=_dedupe_labels(labels),
        ports=ports,
        by_name=by_name,
        parked_ports=sorted({pnet for pnet, _r, _a in parked_edges}),
        router="per-route" if layout is None else "channel",
        lanes={} if layout is None else dict(layout.lanes),
        pieces=dict(sorted(piece_count.items())),
        unrouted=[] if layout is None else list(layout.unrouted),
        supply=supply_counts,
    )


_SUPPLY_KIND = {"track": "rails", "lane": "spines", "stub": "taps"}


def _supply_counts(
    supply: Mapping[str, str],
    by_net: Mapping[str, list[_APin]],
    rail_nets: tuple[str | None, str | None],
    rail_intents: list[tuple[str, _APin, int]],
    dropped: set[int],
    layout_kind: Mapping[int, tuple[str, str]],
    layout_path: Mapping[int, list[Wire]],
    drawn: Mapping[str, list[tuple[list[Wire], bool]]],
) -> dict[str, dict[str, int]]:
    """Rails, spines and taps drawn per supply net, and the planned ones removed (see
    :attr:`ConnectionPlan.supply`). Called after the dangling-run rule, on what survived it."""
    out = {
        net: {"rails": 0, "spines": 0, "taps": 0, "refused": 0}
        for net in sorted(supply)
        if net in by_net
    }
    for net in rail_nets:  # the per-route planner's sheet rails are never refused
        if net is not None:
            out[net]["rails"] += 1
    for net, _pin, rid in rail_intents:
        out[net]["refused" if rid in dropped else "taps"] += 1
    alive = {id(path) for runs in drawn.values() for path, _ in runs}
    for rid, (net, kind) in layout_kind.items():
        if net in out:
            kept = rid in layout_path and id(layout_path[rid]) in alive
            out[net][_SUPPLY_KIND[kind] if kept else "refused"] += 1
    return out


def _device_pins(placed: list[PlacedDevice]) -> list[DevicePins]:
    """The placed devices as the channel router sees them: a box (body with pins) and the pins."""
    out: list[DevicePins] = []
    for pd in placed:
        pins = tuple(
            (canon, pd.nets[canon], *apply_transform(pd.transform, sp.x, sp.y))
            for canon, sp in pd.aligned.items()
        )
        boxes = [*_keepout(pd), *((x, y, x, y) for _c, _n, x, y in pins)]
        box = (
            min(b[0] for b in boxes),
            min(b[1] for b in boxes),
            max(b[2] for b in boxes),
            max(b[3] for b in boxes),
        )
        out.append(DevicePins(pd.ref, box, pins, is_block=pd.is_block, is_source=pd.is_source))
    return out


def spread_channels(placed: list[PlacedDevice], *, supply: Mapping[str, str]) -> list[PlacedDevice]:
    """Move the blocks of a block diagram apart until every reserved lane fits its channel.

    The placement step of channel routing (:func:`~.channels.channel_deficits`): a channel that is
    narrower than its lanes need is widened by the difference, and every block beyond it moves by
    that much, so the rows and columns keep their order. Any other sheet — and a block diagram whose
    channels already have room — is returned unchanged. :func:`plan_connections` never moves a
    device itself; a lane that does not fit is left to its net-name label and reported.
    """
    shifts = channel_deficits(_device_pins(placed), supply)
    if not shifts or not any(shifts.values()):
        return list(placed)
    out: list[PlacedDevice] = []
    for pd in placed:
        dx, dy = shifts[pd.ref]
        t = pd.transform
        out.append(replace(pd, transform=Transform(t.x + dx, t.y + dy, t.rot, t.flip)))
    return out


def _merge_collinear(wires: list[Wire]) -> list[Wire]:
    """Coalesce collinear, overlapping-or-abutting segments into maximal runs (cosmetic, connectivity-
    preserving). Each terminal's boundary-box lead is collinear with the column/row bus it joins, and
    :func:`_net_wires` splits every run at each pin — so a straight wire piles up to three-plus coincident
    endpoints at every interior tap and overlap, and xschem draws a *solder dot* there even though
    nothing branches off. Merging the pieces back into one wire leaves a dot only where a wire genuinely
    turns or tees. No short is possible: :mod:`.connectivity` guarantees only same-net wires ever
    touch, so two segments that overlap or abut on one line are always the same net (a foreign one would
    have been dropped), and the union never reaches past their combined span — no new geometry.

    **A junction is never merged away.** xschem joins two perpendicular wires only where the meeting
    point is an *endpoint* of at least one of them — a strict interior-of-both crossing is two wires
    passing over each other. So a corner where an L's two legs meet, or where a detour joins a run,
    stops being a connection the moment BOTH legs get merged past it (each piece has a collinear
    neighbour continuing beyond the corner). Every run is therefore split again at each point where a
    wire of the other axis ends: the dot stays where something genuinely tees, and the run is still
    coalesced everywhere else (that point has wires on two axes, so it is not the straight-run
    clutter this pass exists to remove)."""
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

    def split(run: tuple[int, int], breaks: set[int]) -> list[tuple[int, int]]:
        """Cut a merged run at every junction point strictly inside it (see the docstring)."""
        cuts = sorted(b for b in breaks if run[0] < b < run[1])
        edges = [run[0], *cuts, run[1]]
        return list(zip(edges, edges[1:]))

    merged_v = {x: union(ivs) for x, ivs in by_v.items()}
    merged_h = {y: union(ivs) for y, ivs in by_h.items()}

    def interior(runs: list[tuple[int, int]], v: int) -> bool:
        return any(s < v < e for s, e in runs)

    # A junction is a point where some wire ENDS (that endpoint is what made the connection). It only
    # needs rescuing when the merge would bury it inside a run on BOTH axes — a plain crossing, where
    # no wire ends, was never a connection and is left alone.
    v_breaks: dict[int, set[int]] = defaultdict(set)  # x -> the y values that column must be cut at
    ends = {(w.x1, w.y1) for w in wires} | {(w.x2, w.y2) for w in wires}
    for px, py in ends:
        if interior(merged_v.get(px, []), py) and interior(merged_h.get(py, []), px):
            v_breaks[px].add(py)
    for x, runs in sorted(merged_v.items()):
        kept.extend(Wire(x, s, x, e) for run in runs for s, e in split(run, v_breaks[x]))
    for y, runs in sorted(merged_h.items()):
        kept.extend(Wire(run[0], y, run[1], y) for run in runs)
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
