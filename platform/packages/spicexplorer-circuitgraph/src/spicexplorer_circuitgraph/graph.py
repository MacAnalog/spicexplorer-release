"""CircuitGraph — a typed bipartite graph (nets ⟷ components) built from a netlist.

The graph is an undirected ``networkx.MultiGraph``: component nodes carry ``bipartite=0``, net
nodes ``bipartite=1``, and each edge is keyed by the component's pin so a diode-connected device
(DRAIN and GATE on one net) yields two distinct parallel edges. Nodes are the dataclasses from
``model/`` and are used directly as graph keys (hashed by name → one instance per name).

The prototype's four-level abstract tower (CircuitGraphBase → Bipartite → Serializable →
SpicelibTopologyGraph) is collapsed here into one concrete class: there is a single backend (the
core ``NetlistView``), so the abstraction was unused indirection. Serialization lives in the
``serialization`` subpackage — ``CircuitGraph`` exposes ``connections()`` and the graph
accessors that the strategies build every view from.
"""

from __future__ import annotations

import logging
from typing import Literal

import networkx as nx
from spicexplorer_core.spice_engine import NetlistViewLike

from .device_factory import DeviceFactory, wired_nets
from .model.edges import EdgeType, Pin, PinTypeMOSFET, SubcktPort, SubcktPortRole
from .model.nodes import ComponentNode, MosfetNode, NetNode, SubcktInstanceNode, VccsNode, VcvsNode
from .pdk import Pdk
from .port_spec import get_port_spec

logger = logging.getLogger(__name__)

NET_BIPARTITE_INDEX = 1
COMPONENT_BIPARTITE_INDEX = 0

OnUnknown = Literal["skip", "raise"]

# Net names that, after normalization, denote a supply rail. Conservative name-based heuristic
# (Phase-1 provisioning); connectivity-based detection can layer on later.
_GROUND_NAMES = {"0", "gnd", "vgnd"}
_NEG_RAIL_NAMES = {"vss", "vee", "vssa", "vssio"}
_POS_RAIL_NAMES = {"vdd", "vcc", "vpwr", "vdda", "vddio", "vcca"}


def _classify_supply(net_name: str) -> tuple[bool, str]:
    """Map a net name to ``(is_supply, supply_type)`` using a normalized exact-match lookup.

    Normalization strips underscores and a trailing global-net ``!`` and lowercases, so ``v_dd``,
    ``VDD!`` and ``vdd`` all classify as a ``VDD`` rail while signal nets (``v_out``, ``net1``)
    do not.
    """
    # Order-independent: drop separators and the global-net marker wherever they appear.
    norm = net_name.strip().lower().replace("_", "").replace("!", "")
    if norm in _GROUND_NAMES:
        return True, "GND"
    if norm in _NEG_RAIL_NAMES:
        return True, "VSS"
    if norm in _POS_RAIL_NAMES:
        return True, "VDD"
    return False, ""


class CircuitGraph:
    """A typed bipartite circuit graph (build, accessors, supply/role detection, recursion).

    Serialization to LLM-facing views lives in the ``serialization`` subpackage — call
    ``serialize(graph, "<strategy>")`` rather than a method here.
    """

    def __init__(self, name: str = "") -> None:
        self.name: str = name or "circuit"
        self.graph_description: str = ""
        # INVARIANT: these three must be mutated together — only via add_net / add_component /
        # connect. Never call self._G.add_node/add_edge directly elsewhere, or the registries
        # and the graph drift out of sync.
        self._net_map: dict[str, NetNode] = {}
        self._comp_map: dict[str, ComponentNode] = {}
        self._G: nx.MultiGraph = nx.MultiGraph(name=self.name)
        # Populated when built with recurse=True: subckt instance ref -> its expanded child graph.
        self.subgraphs: dict[str, CircuitGraph] = {}
        # References the build could NOT model (``on_unknown="skip"``), in netlist order. This
        # graph is then an INCOMPLETE picture of its netlist, so the record is load-bearing:
        # `compare_graphs` refuses to ignore it (two builds that dropped different devices are
        # not "the same circuit" just because what survived happens to match).
        self.skipped_components: list[str] = []
        # The nets each skipped reference was wired to, so the loss can be described WITHOUT its
        # instance name — see `skipped_shapes`. The name alone is not comparable across two
        # independent netlisters (Virtuoso and xschem spell the same clamp diode differently).
        self._skipped_nets: dict[str, tuple[str, ...]] = {}
        # Functional-subcircuit annotations overlaid by the matcher (e.g. detected current
        # mirrors). Empty until `match.annotate_subcircuits` runs; each entry is a MirrorGroup.
        # A non-structural overlay — it is NOT part of the contract round-trip or comparison.
        self.subcircuit_matches: list = []

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    @classmethod
    def from_netlist(
        cls,
        view: NetlistViewLike,
        *,
        name: str = "",
        pdk: Pdk | None = None,
        on_unknown: OnUnknown = "skip",
        detect_supply: bool = True,
        recurse: bool = False,
        _seen: frozenset[str] = frozenset(),
    ) -> "CircuitGraph":
        """Build a graph from a :class:`~spicexplorer_core.spice_engine.NetlistViewLike` view (one hierarchy level).

        Subcircuit instances are modeled as black-box :class:`SubcktInstanceNode`s with named,
        role-tagged ports. ``on_unknown`` controls truly untypable devices (e.g. a BJT/diode):
        ``"skip"`` warns, drops them, and records their references in
        :attr:`skipped_components` so the loss stays visible; ``"raise"`` aborts.

        With ``recurse=True``, each subckt instance is also *expanded* into a child graph stored in
        :attr:`subgraphs` (instance ref -> child) — leaving the black-box node in place, so callers
        get both representations. (Internal ``_seen`` guards against cyclic ``.subckt`` references.)
        """
        graph = cls(name)
        factory = DeviceFactory(pdk)

        for net_name in view.get_all_nodes():
            graph.add_net(NetNode(name=net_name))

        for ref in view.get_components():
            node = factory.create(ref, view)
            if node is None:
                msg = f"unsupported or malformed device {ref!r}"
                if on_unknown == "raise":
                    raise ValueError(msg)
                logger.warning("skipping %s", msg)
                graph.skipped_components.append(ref)
                # Record the wiring too: it is the only name-free evidence of what was lost.
                try:
                    graph._skipped_nets[ref] = tuple(view.get_component_nodes(ref))
                except Exception:  # pragma: no cover - a view that cannot report nets for a ref
                    graph._skipped_nets[ref] = ()
                continue
            # Add + connect atomically. The factory has already validated arity, so a component
            # node is only ever added together with its full pin↔net edge set — never a phantom
            # (typed-but-disconnected) node.
            graph.add_component(node)
            graph._connect_from_netlist(node, view)

        if detect_supply:
            graph.detect_supply_nets()
        graph._assign_subckt_port_roles()  # needs supply flags + the port-spec registry

        if recurse:
            graph._expand_subcircuits(view, pdk, on_unknown, detect_supply, _seen)
        return graph

    # --- low-level builders (also used by the round-trip deserializer in contract.py) ---
    def add_net(self, net: NetNode) -> NetNode:
        self._net_map[net.name] = net
        self._G.add_node(net, bipartite=NET_BIPARTITE_INDEX)
        return net

    def add_component(self, comp: ComponentNode) -> ComponentNode:
        self._comp_map[comp.name] = comp
        self._G.add_node(comp, bipartite=COMPONENT_BIPARTITE_INDEX)
        return comp

    def connect(
        self,
        component: ComponentNode,
        net: NetNode,
        pin: Pin,
        edge_type: EdgeType = EdgeType.ELECTRICAL,
    ) -> None:
        """Add a component↔net edge keyed by pin. Enforces the bipartite invariant."""
        if not isinstance(component, ComponentNode):
            raise TypeError("first endpoint must be a ComponentNode")
        if not isinstance(net, NetNode):
            raise TypeError("second endpoint must be a NetNode")
        self._G.add_edge(component, net, key=pin.value, edge_type=edge_type, pin=pin)

    def _connect_from_netlist(self, comp: ComponentNode, view: NetlistViewLike) -> None:
        # spicelib returns the wired nets in the device's declared terminal order; we map them
        # positionally onto the node's fixed _PIN_ORDER (wired_nets re-appends the controlling
        # pair a G/E element carries inside its value token). DeviceFactory.create has already
        # guaranteed equal counts, so strict=True documents that invariant (and fails loudly if a
        # future change ever violates it). NOTE: correctness assumes spicelib's terminal order
        # matches _PIN_ORDER — true for the SPICE primitives modeled here.
        nets = wired_nets(comp, view)
        for pin, net_name in zip(comp._PIN_ORDER, nets, strict=True):
            net = self._net_map.get(net_name)
            if net is None:
                # Expected for a G/E controlling net used nowhere else (spicelib's get_all_nodes
                # can't see inside the value token); defensive for everything else.
                if not isinstance(comp, (VccsNode, VcvsNode)):
                    logger.warning("net %r missing from registry; registering it", net_name)
                net = self.add_net(NetNode(name=net_name))
            self.connect(comp, net, pin)

    def detect_supply_nets(self) -> None:
        """Flag supply nets by name (heuristic) — see :func:`_classify_supply`."""
        for net in self._net_map.values():
            net.is_supply, net.supply_type = _classify_supply(net.name)

    def _assign_subckt_port_roles(self) -> None:
        """Fill subckt port roles: port-spec registry first, then supply-net inference, else UNKNOWN.

        Mutates the :class:`SubcktPort` objects in place — they are the same objects stored on the
        edges, so both ``_PIN_ORDER`` and the edges see the role. Requires supply detection first.
        """
        for comp in self.get_components():
            if not isinstance(comp, SubcktInstanceNode):
                continue
            spec = get_port_spec(comp.subckt_name)
            net_by_port = self._subckt_port_nets(comp)
            for port in comp.ports():
                if port.name in spec:
                    port.role = spec[port.name]
                    continue
                net = net_by_port.get(port.name)
                if net is not None and net.is_supply:
                    port.role = (
                        SubcktPortRole.POWER if net.supply_type == "VDD" else SubcktPortRole.GROUND
                    )

    def _subckt_port_nets(self, comp: SubcktInstanceNode) -> dict[str, NetNode]:
        """port-name → connected net, read from the live graph edges."""
        mapping: dict[str, NetNode] = {}
        for net in self.get_neighbourhood(comp, sort=False):
            edge_dict = self._G.get_edge_data(comp, net)
            for attrs in edge_dict.values():
                pin = attrs.get("pin")
                if isinstance(pin, SubcktPort):
                    mapping[pin.name] = net
        return mapping

    def _expand_subcircuits(
        self,
        view: NetlistViewLike,
        pdk: Pdk | None,
        on_unknown: OnUnknown,
        detect_supply: bool,
        seen: frozenset[str],
    ) -> None:
        """Step into each subckt instance, building its child graph into :attr:`subgraphs`."""
        for comp in self.get_components():
            if not isinstance(comp, SubcktInstanceNode):
                continue
            sub_name = comp.subckt_name
            if not sub_name:  # no resolved definition name — can't key the cycle guard, don't recurse
                logger.warning("subckt instance %s has no definition name; skipping expansion", comp.name)
                continue
            if sub_name in seen:  # cyclic .subckt reference down this path — stop descending
                logger.warning("cyclic subckt reference at %s (%s); not expanding", comp.name, sub_name)
                continue
            try:
                child_view = view.get_subcircuit(comp.name)
            except Exception:
                logger.warning("cannot step into subckt instance %s; skipping expansion", comp.name)
                continue
            self.subgraphs[comp.name] = CircuitGraph.from_netlist(
                child_view,
                name=sub_name,
                pdk=pdk,
                on_unknown=on_unknown,
                detect_supply=detect_supply,
                recurse=True,
                _seen=seen | {sub_name},
            )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    @property
    def component_count(self) -> int:
        return len(self._comp_map)

    @property
    def net_count(self) -> int:
        return len(self._net_map)

    def get_components(self, sort: bool = True) -> list[ComponentNode]:
        comps = list(self._comp_map.values())
        return sorted(comps, key=lambda c: c.name) if sort else comps

    def get_nets(self, sort: bool = True) -> list[NetNode]:
        nets = list(self._net_map.values())
        return sorted(nets, key=lambda n: n.name) if sort else nets

    def get_neighbourhood(self, comp: ComponentNode, sort: bool = True) -> list[NetNode]:
        neighbours = list(self._G.neighbors(comp))
        return sorted(neighbours, key=lambda n: n.name) if sort else neighbours

    def skipped_shapes(self) -> list[tuple[str, int, tuple[int, ...]]]:
        """One **name-free** shape per entry of :attr:`skipped_components`, in the same order.

        A shape is ``(SPICE device letter, wired-net count, sorted net-degree signature)`` — the
        most a dropped device can honestly be described by, given that the build never typed it:

        * the **letter** is the device class SPICE itself dispatches on (``D`` diode, ``Q`` BJT),
          not an arbitrary name;
        * the **net count** distinguishes a 2-terminal drop from a 3-terminal one;
        * the **degree signature** is how many modeled pins touch each of those nets, which pins
          the dropped device to a place in the surviving topology.

        None of the three moves when an instance is renamed, which is what makes it usable inside
        :func:`~spicexplorer_circuitgraph.compare.compare_graphs`: that comparison's contract is
        that ``D1`` → ``DCLAMP`` does not change the circuit, and two independent netlisters
        (xschem and Virtuoso, say) have no reason to agree on the spelling. Comparing raw names
        there turns a pure rename into "not equivalent"; comparing shapes still catches the thing
        worth catching — one side dropped a diode the other did not.
        """
        shapes: list[tuple[str, int, tuple[int, ...]]] = []
        for ref in self.skipped_components:
            nets = self._skipped_nets.get(ref, ())
            degrees = sorted(
                self._G.degree(self._net_map[n]) for n in nets if n in self._net_map
            )
            shapes.append((ref[:1].upper(), len(nets), tuple(degrees)))
        return shapes

    def connections(self, comp: ComponentNode, *, include_body: bool = True) -> dict[str, str]:
        """pin-name → net-name for a component, read from the live graph (deterministic order).

        Walks ALL parallel edges to each net (keyed by pin), not just the net once — a
        diode-connected MOS has DRAIN and GATE on the same net and must keep both pins. This is the
        component-centric primitive the serialization strategies build every view from (net-centric
        views simply invert it).

        ``include_body`` (default ``True``) keeps a MOSFET's ``BULK`` terminal — required by the
        lossless round-trip contract, netlist emission, and path finding. The LLM-facing description
        views pass ``include_body=False`` to drop it, since the body tie (NMOS→VSS / PMOS→VDD) is
        rarely load-bearing for topology and only clutters the description.
        """
        out: dict[str, str] = {}
        for net in self.get_neighbourhood(comp, sort=True):
            edge_dict = self._G.get_edge_data(comp, net)
            for key in sorted(edge_dict, key=str):  # edge keys are our pin.value strings
                pin = edge_dict[key].get("pin")
                if pin is not None:
                    out[str(pin.value)] = net.name
        if not include_body and isinstance(comp, MosfetNode):
            out.pop(PinTypeMOSFET.BULK.value, None)
        return out
