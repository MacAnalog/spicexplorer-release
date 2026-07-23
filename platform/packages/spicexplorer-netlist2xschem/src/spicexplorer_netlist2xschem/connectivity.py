"""Pure-geometry connectivity verifier — does the drawn wiring merge two distinct nets?

xschem builds a net from the wires and pins that physically touch. Two orthogonal wire segments
join when they share an endpoint, when an endpoint of one lies on the *interior* of the other (a
T-junction), or when they are collinear and overlap. A pin (or net-name label) joins the net of any
segment its point lies on. A pure 4-way crossing — two segments meeting at a point that is the
strict interior of *both* — does **not** join them (xschem needs an explicit junction), so we model
it the same way.

Given the wires we intend to draw plus the net-bearing terminals (device pins, labels, port pins),
:func:`contaminated_nets` returns the nets that would end up electrically merged with a *different*
net. The planner removes those nets' wires and falls those pins back to net-name labels, so the
emitted schematic always re-netlists to the original connectivity (the Docker round-trip is the
final gate). Modelling the merge rules here means we can wire aggressively and still never ship a
short.

Every segment we emit is axis-aligned (the router only draws horizontal/vertical wires), which is
what keeps the touch test exact and cheap.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

__all__ = ["Seg", "Terminal", "Route", "contaminated_nets", "conflicting_routes"]


@dataclass(frozen=True)
class Seg:
    """An axis-aligned wire segment, tagged with the net it is *intended* to carry.

    The tag is only used to report which net's wires to drop on a conflict — xschem itself infers a
    bare wire's net from what it touches, which is exactly the merge this module detects.
    """

    x1: int
    y1: int
    x2: int
    y2: int
    net: str


@dataclass(frozen=True)
class Terminal:
    """A net-bearing point: a device pin, a net-name label, or a port pin."""

    x: int
    y: int
    net: str


@dataclass(frozen=True)
class Route:
    """One removable bundle of wires for a single connection task (a spine, a stub, a rail).

    ``droppable=False`` marks routes that must survive (the supply rails) — on a conflict the planner
    drops the *other* offending route and falls its pins back to labels rather than tearing out a rail.
    """

    rid: int
    net: str
    segs: tuple[Seg, ...]
    droppable: bool = True


def _is_horizontal(s: Seg) -> bool:
    return s.y1 == s.y2


def _between(a: int, lo: int, hi: int) -> bool:
    return lo <= a <= hi if lo <= hi else hi <= a <= lo


def _point_on_seg(px: int, py: int, s: Seg) -> bool:
    if _is_horizontal(s):
        return py == s.y1 and _between(px, s.x1, s.x2)
    if s.x1 == s.x2:  # vertical
        return px == s.x1 and _between(py, s.y1, s.y2)
    return False  # diagonal segments are never emitted


def _segs_touch(a: Seg, b: Seg) -> bool:
    """Do segments ``a`` and ``b`` connect under xschem's rules (endpoint / T / collinear overlap)?

    Two perpendicular segments meeting at a point connect only when that point is an *endpoint* of at
    least one of them; a strict interior-of-both crossing does not connect.
    """
    ah, bh = _is_horizontal(a), _is_horizontal(b)
    if ah and bh:  # both horizontal: connect iff collinear and the x-ranges overlap/touch
        return a.y1 == b.y1 and max(min(a.x1, a.x2), min(b.x1, b.x2)) <= min(
            max(a.x1, a.x2), max(b.x1, b.x2)
        )
    if not ah and not bh:  # both vertical
        return a.x1 == b.x1 and max(min(a.y1, a.y2), min(b.y1, b.y2)) <= min(
            max(a.y1, a.y2), max(b.y1, b.y2)
        )
    # Perpendicular: orient h = horizontal one, v = vertical one. They meet at (v.x, h.y).
    h, v = (a, b) if ah else (b, a)
    px, py = v.x1, h.y1
    if not (_between(px, h.x1, h.x2) and _between(py, v.y1, v.y2)):
        return False  # they don't intersect at all
    h_endpoint = px in (h.x1, h.x2)
    v_endpoint = py in (v.y1, v.y2)
    return h_endpoint or v_endpoint  # interior-of-both crossing → no connection


class _UnionFind:
    def __init__(self, n: int) -> None:
        self._parent = list(range(n))

    def find(self, a: int) -> int:
        while self._parent[a] != a:
            self._parent[a] = self._parent[self._parent[a]]
            a = self._parent[a]
        return a

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra


def contaminated_nets(segs: list[Seg], terminals: list[Terminal]) -> set[str]:
    """Nets that the proposed wiring would short to a *different* net (so they must drop to labels).

    Builds connected components over ``segs`` ∪ ``terminals`` (wires and the pins/labels they touch),
    then flags every net that shares a component with another net. Returns an empty set when the
    wiring is electrically faithful.
    """
    ns = len(segs)
    uf = _UnionFind(ns + len(terminals))
    for i in range(ns):
        for j in range(i + 1, ns):
            if _segs_touch(segs[i], segs[j]):
                uf.union(i, j)
    coincident: dict[tuple[int, int], int] = {}
    for ti, t in enumerate(terminals):
        node = ns + ti
        for i, s in enumerate(segs):
            if _point_on_seg(t.x, t.y, s):
                uf.union(node, i)
        key = (t.x, t.y)
        if key in coincident:  # two pins/labels on the same point are the same xschem node
            uf.union(node, coincident[key])
        else:
            coincident[key] = node

    nets_in: dict[int, set[str]] = {}
    for ti, t in enumerate(terminals):
        nets_in.setdefault(uf.find(ns + ti), set()).add(t.net)
    bad: set[str] = set()
    for nets in nets_in.values():
        if len(nets) > 1:
            bad |= nets
    return bad


def conflicting_routes(routes: list[Route], terminals: list[Terminal]) -> set[int]:
    """The ``rid``s of *droppable* routes that touch foreign-net geometry (so they must drop to labels).

    Resolved in two phases so the *guilty* route is the one removed, not its innocent neighbour:

    1. **Pin grazes.** A droppable route that runs over a foreign-net **terminal** (device pin / label)
       would short to it, so it is dropped first. This is the usual culprit — a cross-circuit bias spine
       routed straight through a leg's pin — and removing it must not also tear out the leg's own stack.
    2. **Route crossings.** Among the *survivors*, two routes of different nets whose segments touch are
       both dropped (a genuine wire-to-wire short with no innocent party). Done after phase 1 so a leg's
       drain/source run kept in phase 1 is not dropped merely for having been grazed by a spine that is
       itself already gone.

    Removing a segment can only break contacts, never make new ones, so the two passes are sufficient.
    Non-droppable routes (rails) are never removed; they still count as obstacles others must avoid.
    """
    bad: set[int] = set()
    for r in routes:
        if not r.droppable:
            continue
        for t in terminals:
            if t.net != r.net and any(_point_on_seg(t.x, t.y, s) for s in r.segs):
                bad.add(r.rid)
                break
    live = [r for r in routes if r.rid not in bad]
    for a, b in combinations(live, 2):
        if a.net == b.net:
            continue
        if any(_segs_touch(sa, sb) for sa in a.segs for sb in b.segs):
            if a.droppable:
                bad.add(a.rid)
            if b.droppable:
                bad.add(b.rid)
    return bad
