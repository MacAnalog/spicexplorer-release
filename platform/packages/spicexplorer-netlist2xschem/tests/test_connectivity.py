"""Connectivity verifier — the geometry rules that keep aggressive wiring from shipping a short.

The two load-bearing rules are validated against real xschem (in the Docker base image): an X-crossing
of two wires whose endpoints don't meet does **not** merge their nets, while a T-junction (one wire's
endpoint on another's interior) does. ``contaminated_nets`` / ``conflicting_routes`` must mirror that.
"""

from spicexplorer_netlist2xschem import (
    Route,
    Seg,
    Terminal,
    conflicting_routes,
    contaminated_nets,
)


def test_clean_spine_not_contaminated():
    # A trunk + one drop, every terminal on net "a": faithful, no merge.
    segs = [Seg(0, 0, 100, 0, "a"), Seg(100, 0, 100, 50, "a")]
    terms = [Terminal(0, 0, "a"), Terminal(100, 50, "a")]
    assert contaminated_nets(segs, terms) == set()


def test_wire_through_foreign_pin_is_contaminated():
    # net "a"'s trunk passes through a pin of net "b" at (50, 0) -> they short.
    segs = [Seg(0, 0, 100, 0, "a")]
    terms = [Terminal(0, 0, "a"), Terminal(50, 0, "b")]
    assert contaminated_nets(segs, terms) == {"a", "b"}


def test_pure_crossing_does_not_merge():
    # Horizontal "a" and vertical "b" cross at (50,0), interior of both -> xschem keeps them separate.
    segs = [Seg(0, 0, 100, 0, "a"), Seg(50, -50, 50, 50, "b")]
    terms = [
        Terminal(0, 0, "a"),
        Terminal(100, 0, "a"),
        Terminal(50, -50, "b"),
        Terminal(50, 50, "b"),
    ]
    assert contaminated_nets(segs, terms) == set()


def test_t_junction_merges():
    # net "b"'s endpoint lands on net "a"'s interior at (50,0) -> T-junction shorts them.
    segs = [Seg(0, 0, 100, 0, "a"), Seg(50, 0, 50, 50, "b")]
    terms = [Terminal(0, 0, "a"), Terminal(50, 50, "b")]
    assert contaminated_nets(segs, terms) == {"a", "b"}


def test_collinear_overlap_merges():
    # Two vertical segments share a column and overlapping y-range -> collinear overlap merges.
    segs = [Seg(0, 0, 0, 60, "a"), Seg(0, 40, 0, 100, "b")]
    terms = [Terminal(0, 0, "a"), Terminal(0, 100, "b")]
    assert contaminated_nets(segs, terms) == {"a", "b"}


def test_conflicting_routes_drops_offender_keeps_rail():
    # A rail (non-droppable) plus a spine that crosses a foreign pin: only the spine is dropped.
    rail = Route(0, "vdd", (Seg(-10, -100, 200, -100, "vdd"),), droppable=False)
    spine = Route(1, "a", (Seg(0, 0, 100, 0, "a"),), droppable=True)
    terms = [Terminal(50, 0, "b")]  # foreign pin sitting on the spine
    assert conflicting_routes([rail, spine], terms) == {1}


def test_conflicting_routes_clean_returns_empty():
    a = Route(0, "a", (Seg(0, 0, 100, 0, "a"),))
    b = Route(1, "b", (Seg(0, 50, 100, 50, "b"),))  # parallel, never touches a
    assert conflicting_routes([a, b], [Terminal(0, 0, "a"), Terminal(0, 50, "b")]) == set()
