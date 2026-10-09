"""Channel routing for a block-diagram sheet: supplies as rails, one lane per net per channel.

A top-level sheet of block symbols cannot be wired one route at a time. The per-route planner in
:mod:`.wiring` joins each net with straight runs and L-bridges and checks every run against what is
already drawn; on a sheet of a few dozen blocks the first net to use the gap between two block
columns takes all of it and every later net is refused (issue #243; on the 40-block test fixture,
26 of 43 signal nets in 2 to 18 pieces and ``vdd``/``vss`` in 33 pieces each). This module is a
helper a schematic agent asks for (``router="channel"`` on :func:`~.wiring.plan_connections` and
:func:`~.emit.build_sch`, ``--router channel``); it is off by default, and the placement and the
final drawing stay with the agent. Asked for, it reserves the routing space from the placement,
before any wire exists:

1. **Channels.** The blocks' x-extents are merged into column bands and their y-extents into row
   bands. The gap between two adjacent column bands is a vertical channel, the gap between two row
   bands a horizontal channel; the space outside the outermost bands gives one more channel on
   each side. Every block sits in one (row, column) cell, and no block reaches into a channel.
2. **One lane per net per channel.** A pin leaves its block along its outward normal into the
   adjacent channel. Each net gets one lane (a vertical wire at its own x) in every vertical
   channel it enters and one track (a horizontal wire at its own y) in every horizontal channel it
   enters. Lanes are numbered by the left-edge algorithm over their spans, so nets whose spans
   overlap in a channel get distinct x (or y) and nets whose spans are apart may share one.
   Two pins at the same height on the two sides of a vertical channel fix an order between their
   lanes (the lane of the left pin must lie left of the lane of the right pin, or their two stubs
   would overlap), and likewise two pins at the same x above and below a horizontal channel; an
   order that closes a loop is broken by leaving one of those pins to its net name.
3. **Supplies first.** A supply net gets one rail per block row: a track in the channel above the
   row (for the pins on top of the blocks) or below it (for the pins at the bottom), placed next
   to the row so each tap is a short vertical wire, and a spine in the outer channel joining the
   rails (VDD on the left, VSS/GND on the right). Signal nets with pins in more than one vertical
   channel get one trunk track, in the horizontal channel nearest the median of their pins.
4. **What still does not fit** — a lane past a channel's capacity, a pin left out to break an
   order loop, a route the connectivity verifier refuses — falls back to the net-name label, and
   :attr:`~.wiring.ConnectionPlan.by_name` reports the net.

The layout is a function of the (row, column) structure only, not of the exact gaps, so
:func:`channel_deficits` can report how far each channel must widen for every lane to fit, the
emitter moves the blocks apart by that much, and routing the moved blocks gives the same lanes.

**Limits.** Blocks must stand in aligned columns and rows: a block spanning two columns, or two
rows whose blocks do not line up, merges bands until two blocks share a cell, and then this module
returns ``None`` and the per-route planner draws the sheet. A sheet with a MOSFET on it is a cell
sheet, never routed here. The test is by pin role (gate, drain, source, bulk): a bipolar primitive
such as the SG13G2 HBT is a subcircuit instance with no such role, so it does not make a cell sheet.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from .geometry import snap

__all__ = [
    "LANE_PITCH",
    "LANE_MARGIN",
    "Access",
    "BlockGrid",
    "DevicePins",
    "ChannelLayout",
    "ChannelRoute",
    "block_grid",
    "channel_deficits",
    "channel_layout",
]

Box = tuple[int, int, int, int]  # (x0, y0, x1, y1), x0 <= x1, y0 <= y1
Point = tuple[int, int]

LANE_PITCH = 20  # spacing between two adjacent lanes (or tracks) in one channel
LANE_MARGIN = 20  # clearance from a band edge (the outermost pin of a block) to the nearest lane
_SHARE_GAP = 40  # two nets on one lane: their wires along it stay more than this far apart
_FAR = 10**6  # the open side of an outer channel, for the span arithmetic
_MOS_ROLES = frozenset({"GATE", "DRAIN", "SOURCE", "BULK"})


@dataclass(frozen=True)
class DevicePins:
    """What the channel router needs of one placed device: its box, and its pins with nets."""

    ref: str
    box: Box  # absolute: the body (a block symbol's drawn extent) together with its pins
    pins: tuple[tuple[str, str, int, int], ...]  # (canonical pin, net, x, y), absolute
    is_block: bool = False
    is_source: bool = False  # an independent V/I source: an obstacle, never routed


@dataclass(frozen=True)
class BlockGrid:
    """The row and column bands of a block-diagram placement, and the cell of every device.

    ``cols[i]`` is the x-range of column band ``i`` (left to right), ``rows[j]`` the y-range of
    row band ``j`` (top to bottom). Vertical channel ``v`` lies between column bands ``v - 1`` and
    ``v`` (channel 0 left of everything, channel ``len(cols)`` right of it); horizontal channel
    ``h`` likewise between row bands ``h - 1`` and ``h``.
    """

    cols: tuple[tuple[int, int], ...]
    rows: tuple[tuple[int, int], ...]
    cell: Mapping[str, tuple[int, int]]  # device ref -> (row, column)

    def v_span(self, v: int) -> tuple[int, int]:
        """The x-range of vertical channel ``v`` (an outer one is open on its outer side)."""
        lo = self.cols[v - 1][1] if v > 0 else -_FAR
        hi = self.cols[v][0] if v < len(self.cols) else _FAR
        return lo, hi

    def h_span(self, h: int) -> tuple[int, int]:
        """The y-range of horizontal channel ``h`` (an outer one is open on its outer side)."""
        lo = self.rows[h - 1][1] if h > 0 else -_FAR
        hi = self.rows[h][0] if h < len(self.rows) else _FAR
        return lo, hi


@dataclass(frozen=True)
class Access:
    """One pin entering a channel.

    ``axis`` is ``"v"`` for a pin that leaves its block sideways into vertical channel ``ch`` and
    ``"h"`` for one that leaves upward or downward into horizontal channel ``ch``. ``side`` is -1
    when the pin's block lies on the channel's low side (left of it, or above it) and +1 on its
    high side. ``at`` is the pin's coordinate along the channel (y in a vertical channel).
    """

    net: str
    x: int
    y: int
    axis: str
    ch: int
    side: int

    @property
    def at(self) -> int:
        return self.y if self.axis == "v" else self.x


@dataclass(frozen=True)
class ChannelRoute:
    """One wire group for the verifier: a pin's stub, one lane, or one track (rail, trunk)."""

    net: str
    kind: str  # "stub" | "lane" | "track"
    wires: tuple[tuple[int, int, int, int], ...]


@dataclass(frozen=True)
class ChannelLayout:
    """The routed sheet: every wire group, and what the router could not place.

    ``unrouted`` names the nets that have at least one pin the router left to its net-name label
    (a lane past a channel's capacity, or a pin removed to break an order loop between lanes).
    ``lanes`` is the number of lanes reserved in each channel, keyed ``("v", i)`` / ``("h", j)``.
    """

    grid: BlockGrid
    routes: tuple[ChannelRoute, ...]
    unrouted: tuple[str, ...] = ()
    lanes: Mapping[tuple[str, int], int] = field(default_factory=dict)


# ------------------------------------------------------------------------------ channels


def _bands(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping or touching ``(lo, hi)`` intervals into disjoint bands, in order."""
    merged: list[tuple[int, int]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def _band_of(bands: list[tuple[int, int]], lo: int) -> int:
    return next(i for i, (a, b) in enumerate(bands) if a <= lo <= b)


def block_grid(devices: Sequence[DevicePins]) -> BlockGrid | None:
    """Row and column bands of the placement, or ``None`` when two devices share a cell.

    A shared cell means the devices do not stand in aligned rows and columns: a block spanning two
    columns merges them into one band, and two blocks of another row then sit in one cell with no
    channel between them. The per-route planner draws such a sheet instead.
    """
    if not devices:
        return None
    cols = _bands([(d.box[0], d.box[2]) for d in devices])
    rows = _bands([(d.box[1], d.box[3]) for d in devices])
    cell: dict[str, tuple[int, int]] = {}
    taken: set[tuple[int, int]] = set()
    for d in devices:
        rc = (_band_of(rows, d.box[1]), _band_of(cols, d.box[0]))
        if rc in taken:
            return None
        taken.add(rc)
        cell[d.ref] = rc
    return BlockGrid(cols=tuple(cols), rows=tuple(rows), cell=cell)


def _pin_side(box: Box, x: int, y: int) -> tuple[int, int]:
    """The pin's outward direction from its body, as a unit step on one axis.

    Measured against the box rather than the symbol origin, so a pin on the top edge of a wide,
    short block (further from the origin in x than in y) still leaves upward.
    """
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    hw, hh = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
    if abs(x - cx) - hw >= abs(y - cy) - hh:
        return (1 if x >= cx else -1, 0)
    return (0, 1 if y >= cy else -1)


def _accesses(grid: BlockGrid, devices: Sequence[DevicePins]) -> list[Access]:
    out: list[Access] = []
    for d in devices:
        if d.is_source:
            continue
        r, c = grid.cell[d.ref]
        for _canon, net, x, y in d.pins:
            dx, dy = _pin_side(d.box, x, y)
            if dx:
                out.append(Access(net, x, y, "v", c + (dx > 0), -dx))
            else:
                out.append(Access(net, x, y, "h", r + (dy > 0), -dy))
    return sorted(out, key=lambda a: (a.net, a.axis, a.ch, a.at, a.side))


# --------------------------------------------------------------------------- per-net plan


@dataclass
class _Net:
    """The channels one net occupies: the accesses per lane / track, and the connectors."""

    name: str
    lanes: dict[int, list[Access]] = field(default_factory=dict)  # v -> accesses
    tracks: dict[int, list[Access]] = field(default_factory=dict)  # h -> accesses


def _median_channel(positions: list[float], count: int) -> int:
    """The channel index (0..count) closest to the given band positions, ties to the lower one."""
    return min(range(count + 1), key=lambda k: (sum(abs(p - k) for p in positions), k))


def _plan_nets(
    grid: BlockGrid, accesses: list[Access], supply: Mapping[str, str]
) -> dict[str, _Net]:
    """Which lanes and tracks each net needs, including the connectors that join them.

    Positions are band INDICES, never coordinates, so the choice survives the emitter widening a
    channel: a pin in row ``r`` sits at ``r + 0.5`` between horizontal channels ``r`` and ``r + 1``.
    """
    nets: dict[str, _Net] = {}
    by_net: dict[str, list[Access]] = defaultdict(list)
    for a in accesses:
        by_net[a.net].append(a)
    n_rows, n_cols = len(grid.rows), len(grid.cols)
    for name in sorted(by_net):
        acc = by_net[name]
        if len({(a.x, a.y) for a in acc}) < 2:
            continue  # a lone pin: nothing to join
        net = _Net(name)
        for a in acc:
            (net.lanes if a.axis == "v" else net.tracks).setdefault(a.ch, []).append(a)
        role = supply.get(name)
        if not net.tracks and len(net.lanes) > 1:
            # a trunk in the horizontal channel nearest the pins' rows
            net.tracks[_median_channel([_row_pos(grid, a) for a in acc], n_rows)] = []
        if not net.lanes and len(net.tracks) > 1:
            if role == "VDD":
                v = 0  # the VDD spine: left of every block
            elif role in ("VSS", "GND"):
                v = n_cols  # the VSS/GND spine: right of every block
            else:
                v = _median_channel([_col_pos(grid, a) for a in acc], n_cols)
            net.lanes[v] = []
        nets[name] = net
    return nets


def _row_pos(grid: BlockGrid, a: Access) -> float:
    """A sideways pin's row, in band units: row ``r`` lies between horizontal channels ``r`` and
    ``r + 1``, so its pins sit at ``r + 0.5``."""
    return next(i for i, (lo, hi) in enumerate(grid.rows) if lo <= a.y <= hi) + 0.5


def _col_pos(grid: BlockGrid, a: Access) -> float:
    """An upward or downward pin's column, in band units (see :func:`_row_pos`)."""
    return next(i for i, (lo, hi) in enumerate(grid.cols) if lo <= a.x <= hi) + 0.5


# -------------------------------------------------------------------- lane numbering


def _spans(
    grid: BlockGrid, nets: Mapping[str, _Net]
) -> dict[tuple[str, int], dict[str, tuple[int, int]]]:
    """The span every net needs along each channel it occupies, widened to whole channels.

    A lane reaching a track is taken to cover that track's WHOLE horizontal channel (and a track
    reaching a lane the lane's whole vertical channel), because where in the channel the track
    lands is only known after numbering. Two nets that the widened spans keep apart are apart at
    any lane position, so a shared lane is safe before a single coordinate is fixed.
    """
    out: dict[tuple[str, int], dict[str, tuple[int, int]]] = defaultdict(dict)
    for net in nets.values():
        for v, acc in net.lanes.items():
            pts = [a.y for a in acc]
            for h in net.tracks:
                pts.extend(grid.h_span(h))
            out[("v", v)][net.name] = (min(pts), max(pts))
        for h, acc in net.tracks.items():
            pts = [a.x for a in acc]
            for v in net.lanes:
                pts.extend(grid.v_span(v))
            out[("h", h)][net.name] = (min(pts), max(pts))
    return out


def _order_edges(
    key: tuple[str, int],
    grid: BlockGrid,
    nets: Mapping[str, _Net],
    supply: Mapping[str, str],
) -> dict[tuple[str, str], list[tuple[Access, Access]]]:
    """``(a, b) -> the pin pairs forcing it``: net ``a`` must take a lower lane than net ``b``.

    Two sources. A pin of ``a`` on the channel's low side and a pin of ``b`` on its high side at the
    same height: their stubs run toward each other on one line, so ``a``'s lane must come first. And
    supplies next to their taps: a supply whose pins all enter from the low side goes before every
    signal, one whose pins all enter from the high side after every signal, and a spine with no pin
    in an outer channel goes outermost — so a tap crosses no other wire. The second kind carries no
    pin pair (``[]``): it can never close a loop by itself (such a supply has no edge coming in, or
    none going out).
    """
    axis, ch = key
    acc = {n.name: (n.lanes if axis == "v" else n.tracks).get(ch) for n in nets.values()}
    acc = {k: v for k, v in acc.items() if v is not None}
    edges: dict[tuple[str, str], list[tuple[Access, Access]]] = defaultdict(list)
    lo_at: dict[int, list[Access]] = defaultdict(list)
    hi_at: dict[int, list[Access]] = defaultdict(list)
    for name in sorted(acc):
        for a in acc[name]:
            (lo_at if a.side < 0 else hi_at)[a.at].append(a)
    for at in sorted(set(lo_at) & set(hi_at)):
        for a in lo_at[at]:
            for b in hi_at[at]:
                if a.net != b.net:
                    edges[(a.net, b.net)].append((a, b))
    outer_lo = ch == 0
    outer_hi = ch == (len(grid.cols) if axis == "v" else len(grid.rows))
    firsts: list[str] = []
    lasts: list[str] = []
    for s in sorted(n for n in acc if n in supply):
        sides = {a.side for a in acc[s]}
        if sides == {-1} or (not sides and outer_lo):
            firsts.append(s)
        elif sides == {1} or (not sides and outer_hi):
            lasts.append(s)
    others = sorted(n for n in acc if n not in lasts)
    for s in firsts:
        for n in others:
            if n != s and n not in firsts:
                edges.setdefault((s, n), [])
    for s in lasts:
        for n in sorted(acc):
            if n not in lasts:
                edges.setdefault((n, s), [])
    return edges


def _find_cycle(nodes: list[str], edges: Mapping[tuple[str, str], object]) -> list[str] | None:
    """A cycle of the order graph as a node list ``[n0, n1, ..., n0]``, or ``None`` (deterministic)."""
    succ: dict[str, list[str]] = defaultdict(list)
    for a, b in sorted(edges):
        succ[a].append(b)
    state: dict[str, int] = {}  # 1 = on the current path, 2 = finished
    path: list[str] = []

    def visit(u: str) -> list[str] | None:
        state[u] = 1
        path.append(u)
        for w in succ[u]:
            if state.get(w) == 1:
                return [*path[path.index(w) :], w]
            if w not in state and (found := visit(w)) is not None:
                return found
        path.pop()
        state[u] = 2
        return None

    for n in nodes:
        if n not in state and (found := visit(n)) is not None:
            return found
    return None


def _left_edge(
    spans: Mapping[str, tuple[int, int]], edges: Mapping[tuple[str, str], object]
) -> dict[str, int]:
    """Number the lanes of one channel: left-edge packing under the order constraints.

    Round ``i`` fills lane ``i``: walk the nets not yet numbered in order of their span's start,
    take each one whose predecessors all sit on EARLIER lanes and whose span starts more than the
    sharing gap (40 units) past the end of the last one taken this round. Requires an acyclic
    order graph.
    """
    preds: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        preds[b].add(a)
    order = sorted(spans, key=lambda n: (spans[n][0], spans[n][1], n))
    lane: dict[str, int] = {}
    idx = 0
    while len(lane) < len(order):
        last = None
        taken: list[str] = []
        for n in order:
            if n in lane or any(p not in lane for p in preds[n]):
                continue
            if last is None or spans[n][0] > last + _SHARE_GAP:
                taken.append(n)
                last = spans[n][1]
        if not taken:  # only an order loop can stall a round, and _number removes every loop
            raise RuntimeError(f"lane order has a loop among {sorted(set(order) - set(lane))}")
        for n in taken:
            lane[n] = idx
        idx += 1
    return lane


def _number(
    grid: BlockGrid, accesses: list[Access], supply: Mapping[str, str]
) -> tuple[dict[str, _Net], dict[tuple[str, int], dict[str, int]], set[Access]]:
    """Plan every net, then number the lanes of every channel, breaking order loops.

    A loop (``a`` before ``b`` at one height, ``b`` before ``a`` at another) is broken by leaving
    one of the pins that forces it out of the channel — its net name will join it — and planning
    again. Each round removes one pin, so this ends.
    """
    removed: set[Access] = set()
    while True:
        live = [a for a in accesses if a not in removed]
        nets = _plan_nets(grid, live, supply)
        spans = _spans(grid, nets)
        numbering: dict[tuple[str, int], dict[str, int]] = {}
        loop_pin: Access | None = None
        for key in sorted(spans):
            edges = _order_edges(key, grid, nets, supply)
            cycle = _find_cycle(sorted(spans[key]), edges)
            if cycle is not None:
                # Every edge of a loop is a pin pair: a supply ordered first has no edge coming in
                # and one ordered last none going out, so neither can sit on a loop.
                pairs = [p for a, b in zip(cycle, cycle[1:]) for p in edges[(a, b)]]
                loop_pin = max(pairs, key=lambda p: (p[1].at, p[1].net, p[0].net))[1]
                break
            numbering[key] = _left_edge(spans[key], edges)
        if loop_pin is None:
            return nets, numbering, removed
        removed.add(loop_pin)


# ------------------------------------------------------------------------ coordinates


def _capacity(width: int) -> int:
    """How many lanes fit in an inner channel ``width`` wide, with the margin on both sides."""
    room = width - 2 * LANE_MARGIN
    return room // LANE_PITCH + 1 if room >= 0 else 0


def _needed(n: int) -> int:
    """The inner-channel width ``n`` lanes need (0 for none)."""
    return 2 * LANE_MARGIN + (n - 1) * LANE_PITCH if n else 0


def _coords(span: tuple[int, int], n: int, outer: int) -> list[int]:
    """The coordinate of lanes ``0..n-1`` of one channel, lane 0 at the low side.

    ``outer`` is -1 for the channel before the first band, +1 for the one after the last band and 0
    for an inner channel, whose lanes are centred in the gap."""
    lo, hi = span
    if outer < 0:
        return [hi - LANE_MARGIN - (n - 1 - i) * LANE_PITCH for i in range(n)]
    if outer > 0:
        return [lo + LANE_MARGIN + i * LANE_PITCH for i in range(n)]
    start = snap(lo + (hi - lo - (n - 1) * LANE_PITCH) / 2)
    return [start + i * LANE_PITCH for i in range(n)]


def _is_eligible(devices: Sequence[DevicePins]) -> bool:
    """A block-diagram sheet: two or more block symbols and no MOSFET (no pin with a MOS role)."""
    if sum(d.is_block for d in devices) < 2:
        return False
    return not any(canon in _MOS_ROLES for d in devices for canon, *_ in d.pins)


def _ceil5(d: int) -> int:
    """A positive shortfall rounded up to the 5-unit placement grid; 0 when there is room."""
    return -(-d // 5) * 5 if d > 0 else 0


def _prepare(
    devices: Sequence[DevicePins], supply: Mapping[str, str]
) -> tuple[BlockGrid, dict[str, _Net], dict[tuple[str, int], dict[str, int]], set[Access]] | None:
    """Grid, per-net plan and lane numbering — or ``None`` when the sheet is not routed here."""
    if not _is_eligible(devices):
        return None
    grid = block_grid(devices)
    if grid is None:
        return None
    return (grid, *_number(grid, _accesses(grid, devices), supply))


def channel_deficits(
    devices: Sequence[DevicePins], supply: Mapping[str, str]
) -> dict[str, tuple[int, int]] | None:
    """How far to move each device so every lane fits its channel, or ``None`` if not routed here.

    Returns ``{device ref: (dx, dy)}``. Every inner channel short of the width its lanes need
    (:func:`_needed`) is widened by the shortfall, rounded up to the 5-unit grid; the devices to
    its right (or below it) move by the sum of the widenings before them. :func:`channel_layout` on
    the moved devices reserves the same lanes, since the lane plan depends only on the order of the
    bands, and finds every lane within its channel's capacity.
    """
    prepared = _prepare(devices, supply)
    if prepared is None:
        return None
    grid, _, numbering, _ = prepared

    def shifts(axis: str, bands: int) -> list[int]:
        out, total = [], 0
        for k in range(bands):
            if k > 0:
                lo, hi = grid.v_span(k) if axis == "v" else grid.h_span(k)
                n = max(numbering.get((axis, k), {}).values(), default=-1) + 1
                total += _ceil5(_needed(n) - (hi - lo))
            out.append(total)
        return out

    dx, dy = shifts("v", len(grid.cols)), shifts("h", len(grid.rows))
    return {ref: (dx[c], dy[r]) for ref, (r, c) in sorted(grid.cell.items())}


def channel_layout(
    devices: Sequence[DevicePins], supply: Mapping[str, str]
) -> ChannelLayout | None:
    """Route a block-diagram sheet by channels (see the module docstring), or ``None``.

    ``None`` when the sheet is not a block diagram (fewer than two blocks, or any MOSFET) or
    its devices do not stand in aligned rows and columns; the caller then uses the per-route
    planner. Supply routes come first in the returned order.
    """
    prepared = _prepare(devices, supply)
    if prepared is None:
        return None
    grid, nets, numbering, removed = prepared

    # Lane coordinates, and which lanes fit: a lane past the channel's capacity is not drawn.
    coord: dict[tuple[str, int], dict[str, int]] = {}
    unrouted: set[str] = {a.net for a in removed}
    lanes: dict[tuple[str, int], int] = {}
    for key, lane_of in numbering.items():
        axis, ch = key
        n = max(lane_of.values()) + 1
        lanes[key] = n
        count = len(grid.cols) if axis == "v" else len(grid.rows)
        outer = -1 if ch == 0 else (1 if ch == count else 0)
        span = grid.v_span(ch) if axis == "v" else grid.h_span(ch)
        fit = n if outer else min(n, _capacity(span[1] - span[0]))
        at = _coords(span, fit, outer)
        coord[key] = {net: at[i] for net, i in lane_of.items() if i < fit}
        unrouted |= {net for net, i in lane_of.items() if i >= fit}

    routes: list[ChannelRoute] = []
    for name in sorted(nets, key=lambda n: (n not in supply, n)):
        net = nets[name]
        xs = {v: coord[("v", v)][name] for v in net.lanes if name in coord.get(("v", v), {})}
        ys = {h: coord[("h", h)][name] for h in net.tracks if name in coord.get(("h", h), {})}
        for v, x in sorted(xs.items()):
            acc = net.lanes[v]
            pts = sorted({a.y for a in acc} | set(ys.values()))
            if pts[0] != pts[-1]:  # a lane reaches every track of its net
                routes.append(ChannelRoute(name, "lane", ((x, pts[0], x, pts[-1]),)))
            routes.extend(ChannelRoute(name, "stub", ((a.x, a.y, x, a.y),)) for a in acc)
        for h, y in sorted(ys.items()):
            acc = net.tracks[h]
            pts = sorted({a.x for a in acc} | set(xs.values()))
            if pts[0] != pts[-1]:
                # A track reaches every lane of its net and is cut at each one it passes: xschem
                # joins two crossing wires only where one of them ENDS, and the lane (spanning all
                # of the net's tracks) may run straight through.
                cuts = [pts[0], *sorted(x for x in xs.values() if pts[0] < x < pts[-1]), pts[-1]]
                routes.append(
                    ChannelRoute(name, "track", tuple((a, y, b, y) for a, b in zip(cuts, cuts[1:])))
                )
            routes.extend(ChannelRoute(name, "stub", ((a.x, a.y, a.x, y),)) for a in acc)
    return ChannelLayout(
        grid=grid, routes=tuple(routes), unrouted=tuple(sorted(unrouted)), lanes=lanes
    )
