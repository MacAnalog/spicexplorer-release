"""Structural comparison of two circuit graphs — *are these two netlists the same circuit?*

The comparison reduces to a **labeled bipartite-graph isomorphism**: build the nets⟷components
``MultiGraph`` for each netlist (via :class:`~spicexplorer_circuitgraph.graph.CircuitGraph`) and
look for a node bijection that preserves device type and pin-level wiring. Because isomorphism is
defined up to a relabeling of nodes, this is exactly the right notion of "the same netlist":

* renaming an instance (``M1`` → ``M7``) or a net (``net3`` → ``x``) does **not** change the circuit,
* reordering the netlist lines does **not** change the circuit,

but moving a gate to a different net, swapping NMOS for PMOS, or adding a device **does**.

What participates in a match is configurable (see :func:`compare_graphs`). By default the test is
topological — device types + MOS polarity + wiring — and ignores instance/net names, sizing
(``W``/``L``/``R``/``C``), SPICE model strings, and any heuristic roles. The one exception is
**supply rails**: ``VDD``/``VSS``/``GND`` nets are anchored by class (so a rail can never map to a
signal net, and a "resistor across the rails" is *not* the same as a floating one) — they are the
named nets an engineer treats as special. Pass ``match_supply=False`` for a pure-topology test, or
the other ``match_*`` flags to tighten further.

Two pin-orientation subtleties are handled so electrically-identical netlists are not reported as
different:

* **Passive terminal symmetry** — a resistor/capacitor/inductor is non-polar, so swapping its two
  terminals (``R1 a b`` vs ``R1 b a``) is the same circuit. Their pins are collapsed to a single
  symmetric token by default (``passive_symmetry=True``).
* **Sources stay polar** — a voltage/current source has a real ``+``/``-`` orientation, so its
  terminals are matched strictly. MOSFET ``DRAIN``/``GATE``/``SOURCE``/``BULK`` are likewise strict.

The comparison is single-level: a subcircuit instance is matched as a black box (by ``subckt_name``
and its port wiring), not stepped into. Compare expanded child graphs yourself if you need that.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from networkx.algorithms.isomorphism import MultiGraphMatcher
from spicexplorer_core.spice_engine import NetlistView, NetlistViewLike

from ._signatures import MatchOptions as _Options
from ._signatures import component_signature as _component_signature
from ._signatures import edge_match as _edge_match
from ._signatures import node_match as _node_match
from ._signatures import signature_graph as _signature_graph
from .graph import CircuitGraph, OnUnknown
from .pdk import Pdk

__all__ = [
    "GraphComparison",
    "IOPort",
    "compare_graphs",
    "compare_netlists",
    "graphs_equivalent",
    "netlists_equivalent",
]


@dataclass(frozen=True)
class GraphComparison:
    """Result of comparing two circuit graphs.

    Truthy iff the graphs are :attr:`equivalent`, so ``if compare_graphs(a, b): ...`` reads
    naturally. When equivalent, :attr:`component_mapping` / :attr:`net_mapping` give one valid
    name correspondence from the first graph to the second (there may be more than one when the
    circuit is symmetric). :attr:`reason` always carries a human-readable explanation.

    :attr:`skipped_a` / :attr:`skipped_b` carry each side's ``skipped_components`` — the devices
    the *build* could not model and dropped (``on_unknown="skip"``, the default). They are part of
    the result because an "equivalent" verdict that rests on them is a **partial** verdict: both
    netlists could carry a clamp diode that neither graph models, and the isomorphism would say
    nothing about whether the two diodes are wired the same way. :attr:`rests_on_skipped` is the
    one-line test, and the equivalent-case :attr:`reason` names the devices.
    """

    equivalent: bool
    reason: str
    component_mapping: dict[str, str] = field(default_factory=dict)
    net_mapping: dict[str, str] = field(default_factory=dict)
    skipped_a: tuple[str, ...] = ()
    skipped_b: tuple[str, ...] = ()

    def __bool__(self) -> bool:
        return self.equivalent

    @property
    def rests_on_skipped(self) -> bool:
        """True when the verdict was reached over graphs that dropped at least one device.

        Read it before trusting an ``equivalent=True``: the two netlists agree on everything that
        could be typed, and nothing is known about the rest. Build with ``on_unknown="raise"`` to
        make the gap an error instead.
        """
        return bool(self.skipped_a or self.skipped_b)


class IOPort:
    """A named I/O port to anchor in a comparison — one net (single-ended) or two (differential).

    Anchoring pins a port's net(s) so they can only correspond to the *matching* port on the other
    side, never to an internal/supply net. The single-ended vs differential distinction controls how
    the two halves of a pair are allowed to correspond:

    * **single-ended** — ``IOPort("vout")`` — the net is pinned to its own port; it must map to the
      counterpart port's net.
    * **differential, swappable** (default) — ``IOPort("vinp", "vinn")`` — the two nets are pinned to
      a *shared* port identity, so the ``+``/``-`` halves may exchange (``vinp``↔``vinn``), capturing
      the arbitrary polarity convention of a differential signal.
    * **differential, strict** — ``IOPort("voutp", "voutn", swappable=False)`` — the halves are
      pinned distinctly, so their polarity is preserved (no swap).

    When the two netlists use the *same* I/O net names, pass one ``io_ports`` list. When they differ,
    pass ``io_ports`` for the first and ``io_ports_b`` for the second; ports correspond by position.
    """

    __slots__ = ("nets", "swappable", "name")

    def __init__(self, *nets: str, swappable: bool = True, name: str = "") -> None:
        if not 1 <= len(nets) <= 2:
            raise ValueError(
                "IOPort anchors one net (single-ended) or two (a differential pair), "
                f"got {len(nets)}"
            )
        self.nets: tuple[str, ...] = tuple(nets)
        self.swappable = swappable
        self.name = name or "/".join(nets)

    @property
    def differential(self) -> bool:
        return len(self.nets) == 2

    def __repr__(self) -> str:
        kind = "diff" if self.differential else "single"
        if self.differential and not self.swappable:
            kind = "diff-strict"
        return f"IOPort({self.name!r}, {kind})"


# ---------------------------------------------------------------------------
# I/O-port anchoring (comparison-specific; the signature machinery lives in _signatures)
# ---------------------------------------------------------------------------
def _io_labels(ports: list[IOPort] | None) -> dict[str, tuple]:
    """Map each anchored net name (lower-cased — SPICE net names are case-insensitive) to its label.

    A single-ended port and a *swappable* differential port share one label across the port (so a
    swappable pair's two nets are interchangeable but still confined to that port); a *strict*
    differential port labels each half distinctly so its polarity is preserved. Ports are keyed by
    list position, so the same label ties port *i* on one side to port *i* on the other. A net used
    by two ports is ambiguous and rejected.
    """
    labels: dict[str, tuple] = {}
    for i, port in enumerate(ports or []):
        if port.differential and not port.swappable:
            entries = [(net, (i, j)) for j, net in enumerate(port.nets)]
        else:
            entries = [(net, (i,)) for net in port.nets]
        for net, label in entries:
            key = net.lower()
            if key in labels:
                raise ValueError(f"net {net!r} is anchored by more than one IOPort")
            labels[key] = label
    return labels


def _require_anchors_present(io_labels: dict[str, tuple], graph: CircuitGraph, side: str) -> None:
    """Reject anchored net names that don't exist in ``graph`` (a typo'd/absent port silently
    disabling the anchor would otherwise degrade to an unconstrained match)."""
    present = {n.name.lower() for n in graph.get_nets()}
    missing = sorted(set(io_labels) - present)
    if missing:
        raise ValueError(f"anchored I/O net(s) {missing} not present in the {side} netlist")


# ---------------------------------------------------------------------------
# Human-readable diagnostics for the cheap pre-checks
# ---------------------------------------------------------------------------
def _describe_signature(sig: tuple[object, ...]) -> str:
    """Render a component signature like ``MOS/NMOS`` or ``RES/[l=1.8e-07,w=1000]``.

    Non-string parts (the parameter frozenset added under ``match_params``) are rendered too — if
    they were dropped, two devices that differ only in a parameter would print identically on both
    sides of a "differs" message.
    """
    rendered: list[str] = []
    for part in sig[1:]:
        if isinstance(part, str):
            if part:
                rendered.append(part)
        elif isinstance(part, frozenset):
            if part:
                rendered.append("[" + ",".join(f"{k}={v}" for k, v in sorted(part)) + "]")
        else:
            rendered.append(str(part))
    return "/".join(rendered) if rendered else str(sig[1] if len(sig) > 1 else sig)


def _io_port_name(
    label: tuple, ports_a: list[IOPort] | None, ports_b: list[IOPort] | None
) -> str:
    """Render an I/O-port census label ``(i,)`` / ``(i, j)`` as a readable port name."""
    index = label[0]
    for ports in (ports_a, ports_b):
        if ports and index < len(ports):
            port = ports[index]
            if len(label) == 2 and port.differential:  # a strict-diff half
                return f"{port.name}.{port.nets[label[1]]}"
            return port.name
    return str(label)


def _describe_skip_shape(shape: tuple[str, int, tuple[int, ...]]) -> str:
    """Render one name-free skip shape for an error message."""
    letter, n_nets, degrees = shape
    signature = ",".join(str(d) for d in degrees) or "-"
    return f"a {letter!r}-class device on {n_nets} net(s) [degrees {signature}]"


def _skip_names(graph: CircuitGraph) -> str:
    """The references a build dropped, for the human reading the reason (never the decision)."""
    return ", ".join(graph.skipped_components) if graph.skipped_components else "nothing"


def _census_diff(a: Counter, b: Counter, label_fn) -> str:
    """Format the two-way difference of two multisets for an error message."""
    only_a = a - b
    only_b = b - a
    fragments: list[str] = []
    if only_a:
        items = ", ".join(f"{label_fn(k)}×{n}" for k, n in sorted(only_a.items(), key=lambda x: str(x[0])))
        fragments.append(f"only in the first: {items}")
    if only_b:
        items = ", ".join(f"{label_fn(k)}×{n}" for k, n in sorted(only_b.items(), key=lambda x: str(x[0])))
        fragments.append(f"only in the second: {items}")
    return "; ".join(fragments)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def compare_graphs(
    a: CircuitGraph,
    b: CircuitGraph,
    *,
    match_polarity: bool = True,
    match_params: bool = False,
    match_models: bool = False,
    match_supply: bool = True,
    match_structural_role: bool = False,
    passive_symmetry: bool = True,
    io_ports: list[IOPort] | None = None,
    io_ports_b: list[IOPort] | None = None,
) -> GraphComparison:
    """Decide whether two circuit graphs describe the same circuit (labeled isomorphism).

    The default test is topological — device types, MOS polarity, and pin-level wiring — and
    ignores all instance/net names, sizing, model strings, and heuristic roles, **except** that
    supply rails are anchored by class (see ``match_supply``). The flags adjust the test:

    * ``match_polarity`` (default ``True``): NMOS and PMOS are different devices. Turn off to treat
      a MOSFET as polarity-agnostic.
    * ``match_params`` (default ``False``): also require equal declared parameters (``W``/``L``/…),
      compared eng-normalized so ``"0.18u" == "180n"``.
    * ``match_models`` (default ``False``): also require equal SPICE model names (compared
      case-insensitively, since SPICE resolves model cards case-insensitively).
    * ``match_supply`` (default ``True``): require nets to share a supply classification
      (VDD/VSS/GND), so a rail can never map to a signal net. This is the one place a net *name*
      participates (via the name-based supply heuristic) — turn it **off** for a pure-topology test
      that is fully name-independent.
    * ``match_structural_role`` (default ``False``): also require equal (heuristic/LLM-assigned)
      structural roles.
    * ``passive_symmetry`` (default ``True``): treat R/C/L terminals as interchangeable. Turn off
      to match passive terminals strictly by ``P``/``N``.

    ``io_ports`` anchors named input/output ports (:class:`IOPort`): single-ended ports map by
    identity, differential ports map as a pair (with the ``+``/``-`` halves swappable by default).
    An anchored net can then only correspond to its matching port, never to an internal net. When
    the two sides use *different* I/O net names, give ``io_ports`` for ``a`` and ``io_ports_b`` for
    ``b`` (ports correspond by position); otherwise one ``io_ports`` list applies to both. Net names
    are matched case-insensitively (SPICE semantics); an anchored net that is absent from its
    netlist raises :class:`ValueError` (the anchor must apply, not silently evaporate).

    Devices the *build* dropped are never ignored: if the two graphs' skip censuses differ, the
    comparison is a definitive "not equivalent" (a graph built with ``on_unknown="skip"`` describes
    only the part of its netlist that could be typed, so an isomorphism over the survivors proves
    nothing about the whole). The censuses are compared as name-free **shapes** — device letter +
    wired-net count + net-degree signature (:meth:`~spicexplorer_circuitgraph.graph.CircuitGraph.
    skipped_shapes`) — so this stays inside the name-independence contract above: renaming an
    unmodelable ``D1`` to ``DCLAMP`` is not a different circuit. When the two censuses *agree*
    and are non-empty the comparison still runs, but the result says so: the skipped references
    ride on :attr:`GraphComparison.skipped_a` / :attr:`~GraphComparison.skipped_b` (and are named
    in the equivalent-case reason), because an equivalence resting on devices neither graph models
    is a partial answer the caller has to be able to see. ``on_unknown="raise"`` refuses to build
    such a graph in the first place.

    Returns a :class:`GraphComparison` (truthy when equivalent) carrying a reason and, on a match,
    one valid component/net name correspondence from ``a`` to ``b``.
    """
    # Every exit carries both skip censuses — see GraphComparison.rests_on_skipped.
    def verdict(
        equivalent: bool,
        reason: str,
        component_mapping: dict[str, str] | None = None,
        net_mapping: dict[str, str] | None = None,
    ) -> GraphComparison:
        return GraphComparison(
            equivalent,
            reason,
            component_mapping or {},
            net_mapping or {},
            tuple(a.skipped_components),
            tuple(b.skipped_components),
        )

    opts = _Options(
        match_polarity=match_polarity,
        match_params=match_params,
        match_models=match_models,
        match_supply=match_supply,
        match_structural_role=match_structural_role,
        passive_symmetry=passive_symmetry,
    )
    if io_ports_b is not None and len(io_ports or []) != len(io_ports_b):
        raise ValueError(
            "io_ports and io_ports_b must describe the same number of ports (matched by position)"
        )
    io_a = _io_labels(io_ports)
    io_b = _io_labels(io_ports if io_ports_b is None else io_ports_b)
    # An anchored net must actually exist on its side — otherwise the anchor would silently
    # evaporate and the comparison would run looser than the caller asked for.
    _require_anchors_present(io_a, a, "first")
    _require_anchors_present(io_b, b, "second")

    # Cheap, well-diagnosed pre-checks before the (worst-case exponential) VF2 search. Each is a
    # *necessary* condition for the labeled isomorphism, so a mismatch is a definitive "no".
    #
    # Skipped devices first: a build that dropped a device (`on_unknown="skip"`) produced an
    # INCOMPLETE picture of its netlist, so an isomorphism over what survived is not evidence
    # that the two netlists are the same circuit. Compare the census of dropped devices and
    # refuse when it differs — otherwise a round-trip that silently deleted a component would
    # certify itself as equivalent.
    #
    # The census is compared by SHAPE, never by instance name (see `CircuitGraph.skipped_shapes`).
    # This function's contract is that renaming an instance does not change the circuit, and it
    # holds for every device that IS modeled; keying the census on the raw reference made it false
    # for exactly the devices that are not, so two netlists differing only in whether their ESD
    # clamp is called `D1` or `DCLAMP` came back "not equivalent". The names still ride on
    # `skipped_a`/`skipped_b` and in the reason text, where they are diagnostics rather than the
    # decision.
    skipped_a = Counter(a.skipped_shapes())
    skipped_b = Counter(b.skipped_shapes())
    if skipped_a != skipped_b:
        diff = _census_diff(skipped_a, skipped_b, _describe_skip_shape)
        return verdict(
            False,
            f"the two builds skipped different devices ({diff}); the first dropped "
            f"{_skip_names(a)} and the second {_skip_names(b)}; at least one graph is an "
            "incomplete picture of its netlist",
        )
    if a.net_count != b.net_count:
        return verdict(
            False, f"net count differs: {a.net_count} vs {b.net_count}"
        )
    if a.component_count != b.component_count:
        return verdict(
            False, f"component count differs: {a.component_count} vs {b.component_count}"
        )

    sig_a = Counter(_component_signature(c, opts) for c in a.get_components())
    sig_b = Counter(_component_signature(c, opts) for c in b.get_components())
    if sig_a != sig_b:
        diff = _census_diff(sig_a, sig_b, _describe_signature)
        return verdict(False, f"device population differs ({diff})")

    if opts.match_supply:
        rail_a = Counter(n.supply_type for n in a.get_nets() if n.supply_type)
        rail_b = Counter(n.supply_type for n in b.get_nets() if n.supply_type)
        if rail_a != rail_b:
            diff = _census_diff(rail_a, rail_b, str)
            return verdict(False, f"supply-rail population differs ({diff})")

    if io_a or io_b:
        # Census of the anchored ports on each side — anchored nets are guaranteed present (checked
        # above), so this catches a structural mismatch between io_ports and io_ports_b (e.g. a port
        # that is single-ended on one side but differential on the other) with a clear message.
        port_a = Counter(io_a[n.name.lower()] for n in a.get_nets() if n.name.lower() in io_a)
        port_b = Counter(io_b[n.name.lower()] for n in b.get_nets() if n.name.lower() in io_b)
        if port_a != port_b:
            diff = _census_diff(port_a, port_b, lambda lbl: _io_port_name(lbl, io_ports, io_ports_b))
            return verdict(False, f"anchored I/O ports differ ({diff})")

    ga = _signature_graph(a, opts, io_a)
    gb = _signature_graph(b, opts, io_b)

    # Global pin-token census is another necessary condition and gives a crisp message when only
    # the wiring (not the device population) is off.
    pins_a = Counter(d["pin"] for _u, _v, d in ga.edges(data=True))
    pins_b = Counter(d["pin"] for _u, _v, d in gb.edges(data=True))
    if pins_a != pins_b:
        diff = _census_diff(pins_a, pins_b, str)
        return verdict(False, f"pin-connection population differs ({diff})")

    matcher = MultiGraphMatcher(ga, gb, node_match=_node_match, edge_match=_edge_match)
    if not matcher.is_isomorphic():
        return verdict(
            False,
            "same device and pin population but no wiring-preserving isomorphism exists "
            "(the topology differs)",
        )

    # matcher.mapping: a-node-id -> b-node-id, where ids are our (kind, name) tuples.
    comp_map: dict[str, str] = {}
    net_map: dict[str, str] = {}
    for (kind, name), (_kind_b, name_b) in matcher.mapping.items():
        (comp_map if kind == "comp" else net_map)[name] = name_b

    # An equivalence reached over graphs that dropped devices covers only what was modeled — say
    # so in the reason itself, so a caller reading `.reason` (a log line, an LLM, a report) cannot
    # mistake it for a whole-netlist verdict.
    caveat = ""
    if a.skipped_components:
        caveat = (
            f" — but this covers only what could be typed: both builds skipped "
            f"{len(a.skipped_components)} device(s) "
            f"({', '.join(sorted(set(a.skipped_components)))}), which the comparison never saw"
        )
    return verdict(
        True,
        f"equivalent: matched {a.component_count} components and {a.net_count} nets "
        f"under a wiring-preserving isomorphism{caveat}",
        component_mapping=comp_map,
        net_mapping=net_map,
    )


def graphs_equivalent(a: CircuitGraph, b: CircuitGraph, **kwargs) -> bool:
    """Boolean shortcut for :func:`compare_graphs` (see it for the keyword options)."""
    return compare_graphs(a, b, **kwargs).equivalent


# A netlist source the comparison can build a graph from: an already-built graph, a parsed view, a
# file path, or raw netlist text (a ``str`` containing a newline is treated as text, else a path).
NetlistLike = CircuitGraph | NetlistViewLike | str | Path


def _coerce_graph(
    obj: NetlistLike, *, pdk: Pdk | None, name: str, on_unknown: OnUnknown
) -> CircuitGraph:
    if isinstance(obj, CircuitGraph):
        return obj
    if isinstance(obj, NetlistViewLike):
        view = obj
    elif isinstance(obj, Path):
        view = NetlistView.from_file(obj)
    elif isinstance(obj, str):
        view = NetlistView.from_string(obj, dialect="auto") if "\n" in obj else NetlistView.from_file(obj)
    else:
        raise TypeError(f"cannot build a CircuitGraph from a {type(obj).__name__}")
    return CircuitGraph.from_netlist(view, name=name, pdk=pdk, on_unknown=on_unknown)


def compare_netlists(
    a: NetlistLike,
    b: NetlistLike,
    *,
    pdk: Pdk | None = None,
    on_unknown: OnUnknown = "skip",
    **kwargs,
) -> GraphComparison:
    """Build graphs for two netlists and compare them with :func:`compare_graphs`.

    Each argument may be a :class:`CircuitGraph`, a
    :class:`~spicexplorer_core.spice_engine.NetlistView`, a :class:`pathlib.Path` / filename, or raw
    netlist text (a multi-line ``str``). ``pdk`` and ``on_unknown`` are applied while building;
    every other keyword is forwarded to :func:`compare_graphs`.
    """
    ga = _coerce_graph(a, pdk=pdk, name="a", on_unknown=on_unknown)
    gb = _coerce_graph(b, pdk=pdk, name="b", on_unknown=on_unknown)
    return compare_graphs(ga, gb, **kwargs)


def netlists_equivalent(a: NetlistLike, b: NetlistLike, **kwargs) -> bool:
    """Boolean shortcut for :func:`compare_netlists`."""
    return compare_netlists(a, b, **kwargs).equivalent
