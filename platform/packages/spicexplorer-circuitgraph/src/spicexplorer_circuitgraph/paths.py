"""Trace device-level paths between two nets, and diff two paths structurally.

Two complementary capabilities on top of the nets⟷components bipartite graph
(:class:`~spicexplorer_circuitgraph.graph.CircuitGraph`):

* :func:`find_paths_between` walks the graph from one net to another and returns the device-level
  paths connecting them. A path is a sequence of *device traversals* — each one entering a component
  on one pin and leaving on another — rendered as ``device.pin`` touchpoints, e.g.
  ``M1.drain->M1.source->M2.gate->M2.source``. Pass ``shortest_only=True`` (or call
  :func:`shortest_paths_between`) for just the minimal-length paths.
* :func:`diff_paths` compares two paths and reports, with a single ``pin-only`` / ``device-only`` /
  ``device-pin`` verdict, three analysis objects: what is exclusive to the first path, exclusive to
  the second, and common to both.

Every result is a pydantic model (the house contract style — see ``contract.py``), so it serializes
to JSON via ``model_dump()`` / ``model_dump_json()`` and also renders a prose ``describe()`` for an
LLM or a human reviewer.

Two modeling choices worth stating up front:

* **Supply rails are not traversed by default.** ``VDD``/``VSS``/``GND`` are high-degree hubs that
  touch almost every device, so routing *through* them yields a combinatorial blowup of
  electrically-uninteresting paths. They are removed as intermediate nets unless ``through_supply``
  is set (an endpoint may still be a rail).
* **Paths are simple.** The underlying walk (``networkx.all_simple_paths`` /
  ``all_shortest_paths``) never repeats a node, so a path visits each net and each device at most
  once — there are no loops, and every device contributes exactly one traversal.
* **Ideal voltage sources can be excluded.** With ``block_voltage_sources`` set, a ``V`` source is
  dropped as a traversable device, so a path never threads *through* a bias source from one terminal
  to the other. Off by default — a voltage source is walked like any other two-terminal element.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from enum import Enum
from itertools import product
from typing import Iterable, Iterator

import networkx as nx
from pydantic import BaseModel, Field, computed_field

from .graph import CircuitGraph
from .model.nodes import (
    ComponentNode,
    DeviceType,
    MosfetNode,
    MosPolarityType,
    NetNode,
    VoltageSourceNode,
)

__all__ = [
    "DiffKind",
    "StepDiffKind",
    "PathStep",
    "GraphPath",
    "PathList",
    "PathSegment",
    "PathDiff",
    "DEFAULT_MAX_PATHS",
    "find_paths_between",
    "shortest_paths_between",
    "diff_paths",
]

logger = logging.getLogger(__name__)

#: Default cap on how many paths :func:`find_paths_between` collects. The number of simple paths
#: between two nets grows factorially with circuit size — on a 16-device amplifier with
#: ``through_supply=True`` the *complete* enumeration does not finish in minutes — so the search is
#: bounded rather than filtered after the fact. Pass ``max_paths=None`` to opt back into the
#: unbounded enumeration when you genuinely need every path of a small graph.
DEFAULT_MAX_PATHS = 1000


# ---------------------------------------------------------------------------
# Classification enums
# ---------------------------------------------------------------------------
class DiffKind(str, Enum):
    """The overall verdict for a pair of paths (see :func:`diff_paths`)."""

    IDENTICAL = "identical"  # same devices traversed through the same pins
    PIN_ONLY = "pin_only"  # same set of devices, but ≥1 is traversed through different pins
    DEVICE_ONLY = "device_only"  # ≥1 device appears in only one of the paths; no pin-only diffs
    DEVICE_PIN = "device_pin"  # both kinds of difference are present


class StepDiffKind(str, Enum):
    """How one device traversal relates to the other path (set on steps inside a :class:`PathDiff`)."""

    COMMON = "common"  # present in both paths through the same pins
    PIN_ONLY = "pin_only"  # device present in both, but traversed through different pins here
    DEVICE_ONLY = "device_only"  # device present in only this path


# ---------------------------------------------------------------------------
# Data contracts (pydantic, mirroring contract.py)
# ---------------------------------------------------------------------------
class PathStep(BaseModel):
    """One device traversal: enter via ``in_pin``, exit via ``out_pin``.

    ``in_pin``/``out_pin`` carry the canonical graph pin tokens (``DRAIN``/``GATE``/``SOURCE``/``BULK``
    for a MOSFET, ``P``/``N`` for a passive or source, the port name for a subckt instance); the
    rendered ``label``/touchpoints lower-case them for readability. ``diff_kind`` is populated only
    when the step lives inside a :class:`PathDiff` segment — it is ``None`` in a plain
    :func:`find_paths_between` result.
    """

    component: str
    device_type: DeviceType
    polarity: MosPolarityType | None = None  # MOS only
    in_pin: str
    out_pin: str
    in_net: str
    out_net: str
    diff_kind: StepDiffKind | None = None

    @computed_field
    @property
    def touchpoints(self) -> list[str]:
        """The two ``device.pin`` endpoints of this traversal (lower-cased)."""
        return [f"{self.component}.{self.in_pin.lower()}", f"{self.component}.{self.out_pin.lower()}"]

    @computed_field
    @property
    def label(self) -> str:
        """e.g. ``"M1.drain->M1.source"``."""
        return "->".join(self.touchpoints)


class GraphPath(BaseModel):
    """An ordered chain of device traversals connecting :attr:`source` to :attr:`target`."""

    source: str
    target: str
    nets: list[str] = Field(description="The nets visited, in order: [source, …, target].")
    steps: list[PathStep]
    through_supply: bool = False

    @computed_field
    @property
    def length(self) -> int:
        """Number of device hops on the path."""
        return len(self.steps)

    @computed_field
    @property
    def components(self) -> list[str]:
        return [s.component for s in self.steps]

    @computed_field
    @property
    def touchpoints(self) -> list[str]:
        """The flattened ``device.pin`` sequence, e.g. ``[M1.drain, M1.source, M2.gate, M2.source]``."""
        out: list[str] = []
        for s in self.steps:
            out.extend(s.touchpoints)
        return out

    @computed_field
    @property
    def label(self) -> str:
        """e.g. ``"M1.drain->M1.source->M2.gate->M2.source"``."""
        return "->".join(self.touchpoints)

    def describe(self) -> str:
        """A prose rendering of the chain for an LLM/human."""
        if not self.steps:
            return f"trivial path at net {self.source!r} (no devices)"
        chain = self.source
        for i, s in enumerate(self.steps):
            chain += f"  ──[{s.component}: {s.in_pin.lower()}→{s.out_pin.lower()}]──>  {self.nets[i + 1]}"
        hops = f"{self.length} device hop{'s' if self.length != 1 else ''}"
        rail = " (through a supply rail)" if self.through_supply else ""
        return f"Path {self.source!r} → {self.target!r} — {hops}{rail}:\n  {chain}"


class PathSegment(BaseModel):
    """One of the three analysis objects in a :class:`PathDiff` (exclusive-to-A / -B / common)."""

    label: str
    steps: list[PathStep]

    @computed_field
    @property
    def devices(self) -> list[str]:
        """Distinct device names in this segment, in order."""
        seen: set[str] = set()
        out: list[str] = []
        for s in self.steps:
            if s.component not in seen:
                seen.add(s.component)
                out.append(s.component)
        return out

    @computed_field
    @property
    def touchpoints(self) -> list[str]:
        """The ``device.pin`` label sequence for this segment."""
        out: list[str] = []
        for s in self.steps:
            out.extend(s.touchpoints)
        return out

    def describe(self) -> str:
        if not self.steps:
            return f"{self.label}: (none)"
        lines = [f"{self.label}:"]
        for s in self.steps:
            tag = f" [{s.diff_kind.value}]" if s.diff_kind else ""
            lines.append(
                f"  - {s.component}.{s.in_pin.lower()}->{s.out_pin.lower()} "
                f"({_device_label(s)}; {s.in_net}→{s.out_net}){tag}"
            )
        return "\n".join(lines)


class PathDiff(BaseModel):
    """Structural difference of two paths: a verdict plus three analysis objects."""

    kind: DiffKind
    summary: str
    only_in_a: PathSegment
    only_in_b: PathSegment
    common: PathSegment

    def describe(self) -> str:
        return "\n\n".join(
            [self.summary, self.only_in_a.describe(), self.only_in_b.describe(), self.common.describe()]
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _device_label(step: PathStep) -> str:
    """A short device label: the MOS polarity when known, else the device type."""
    if (
        step.device_type is DeviceType.MOS
        and step.polarity is not None
        and step.polarity is not MosPolarityType.UNKNOWN
    ):
        return step.polarity.value
    return step.device_type.value


def _resolve_net(graph: CircuitGraph, name: str) -> NetNode:
    """Look up a net by name (exact first, then a unique case-insensitive match — SPICE semantics)."""
    node = graph._net_map.get(name)
    if node is not None:
        return node
    low = name.lower()
    matches = [n for key, n in graph._net_map.items() if key.lower() == low]
    if not matches:
        raise ValueError(f"net {name!r} is not present in the graph")
    if len(matches) > 1:
        names = sorted(m.name for m in matches)
        raise ValueError(f"net {name!r} is ambiguous (case-insensitive matches: {names})")
    return matches[0]


def _without_supply(G: nx.MultiGraph, keep: set[NetNode]) -> nx.MultiGraph:
    """A read-only view of ``G`` with supply-rail nets removed (except those in ``keep``)."""
    drop = {n for n in G if isinstance(n, NetNode) and n.is_supply and n not in keep}
    if not drop:
        return G
    return G.subgraph([n for n in G if n not in drop])


def _without_voltage_sources(G: nx.MultiGraph) -> nx.MultiGraph:
    """A read-only view of ``G`` with ideal voltage-source *components* removed.

    A ``V`` element is an ideal (zero-impedance) two-terminal source; routing a signal path *through*
    one — in one terminal, out the other — is a bias artifact rather than a real signal connection. We
    drop only the source component node, by element type and regardless of its value (a 0 V "ammeter"
    probe source counts too); the nets it sat on remain and stay reachable by any other route.
    """
    drop = {n for n in G if isinstance(n, VoltageSourceNode)}
    if not drop:
        return G
    return G.subgraph([n for n in G if n not in drop])


# A MOSFET's conduction channel is the DRAIN–SOURCE pair. When the device is off, this traversal is
# not a valid conducting path (the gate/bulk edges are unaffected — gate is still a signal terminal).
_CHANNEL = frozenset({"DRAIN", "SOURCE"})


def _off_channel_mosfets(
    graph: CircuitGraph, respect_mosfet_state: bool, gs_short_is_off: bool
) -> frozenset[str]:
    """Names of MOSFETs whose source–drain channel should be treated as non-conducting.

    A gate–source short pins Vgs to 0, turning an *enhancement* device off; this is suppressed when
    ``gs_short_is_off`` is ``False`` (the global depletion / negative-Vth assumption — those devices
    can still conduct at Vgs = 0). A drain–source short ("killed") needs no entry here: its DRAIN and
    SOURCE are then the same net, so a channel hop between two distinct nets never arises.
    """
    if not (respect_mosfet_state and gs_short_is_off):
        return frozenset()
    return frozenset(
        c.name
        for c in graph.get_components(sort=False)
        if isinstance(c, MosfetNode) and c.is_gate_source_shorted(graph._G)
    )


def _make_step(
    comp: ComponentNode, in_pin: str, out_pin: str, in_net: str, out_net: str
) -> PathStep:
    polarity = comp.polarity if isinstance(comp, MosfetNode) else None
    return PathStep(
        component=comp.name,
        device_type=comp.device_type,
        polarity=polarity,
        in_pin=in_pin,
        out_pin=out_pin,
        in_net=in_net,
        out_net=out_net,
    )


def _expand_node_path(
    graph: CircuitGraph, node_path: list, off_channel: frozenset[str] = frozenset()
) -> Iterator[GraphPath]:
    """Turn one node-level path (net, comp, net, …, net) into its pin-level :class:`GraphPath`\\ s.

    A device may touch the entering or leaving net through more than one pin (e.g. a diode-connected
    MOSFET with DRAIN and GATE on the same net), so a single node path can fan out into several
    distinct pin-level traversals — the cartesian product over each hop's pin choices. Devices in
    ``off_channel`` have their DRAIN↔SOURCE traversal removed (the channel does not conduct); if that
    leaves a hop with no way through, the whole node path is dropped.
    """
    if len(node_path) < 3:  # need at least net → comp → net
        return
    nets: list[NetNode] = node_path[::2]
    comps: list[ComponentNode] = node_path[1::2]

    step_options: list[list[tuple[str, str]]] = []
    for i, comp in enumerate(comps):
        prev_net, next_net = nets[i], nets[i + 1]
        conns = graph.connections(comp)  # pin token -> net name
        in_pins = [p for p, net_name in conns.items() if net_name == prev_net.name]
        out_pins = [p for p, net_name in conns.items() if net_name == next_net.name]
        opts = [(ip, op) for ip in in_pins for op in out_pins if ip != op]
        if comp.name in off_channel:  # the off transistor cannot conduct drain↔source
            opts = [(ip, op) for ip, op in opts if {ip, op} != _CHANNEL]
        if not opts:  # no traversable pin pair left for this hop → this node path is invalid
            return
        step_options.append(opts)

    net_names = [n.name for n in nets]
    through_supply = any(n.is_supply for n in nets[1:-1])
    for combo in product(*step_options):
        steps = [
            _make_step(comp, combo[i][0], combo[i][1], net_names[i], net_names[i + 1])
            for i, comp in enumerate(comps)
        ]
        yield GraphPath(
            source=net_names[0],
            target=net_names[-1],
            nets=net_names,
            steps=steps,
            through_supply=through_supply,
        )


def _node_paths_shortest_first(
    G: nx.MultiGraph, source: NetNode, target: NetNode, max_hops: int
) -> Iterator[list]:
    """Yield node-level simple paths ``source``→``target`` in **nondecreasing hop order**.

    Iterative deepening over ``networkx.all_simple_paths``: round *d* enumerates with
    ``cutoff=2d`` edges (the bipartite graph alternates net/component, so one device hop is two
    edges) and keeps only the paths of exactly that length, which the previous rounds have not
    already yielded. In exchange the caller can stop after *N* paths and know it holds the *N
    shortest* ones.

    The redundant work is **not** the ~2× an earlier version of this note claimed ("each round
    costs at most what the next one does"): when the cap is never reached, every round runs a
    near-full-cost DFS, so the overhead grows with the component count. Measured on
    ``tests/fixtures/ota-improved.spice`` (24 components, the same 88 paths either way): one plain
    ``all_simple_paths`` pass enumerates them in ~0.03 s, this generator in ~0.45 s. Bounded shapes
    (``max_components<=6``, ``shortest_only``) stay near the cheap end. The trade is deliberate — a
    truncated DFS stream is an arbitrary sample labeled "the paths" — but it is a real cost on the
    unbounded call.

    That ordering is the whole point: ``all_simple_paths`` alone is a DFS, so truncating its
    stream keeps whichever paths the traversal stumbled on first (measured on the improved-OTA
    fixture: the first 1000 were of lengths 4 and 9–17, with every path of length 5–8 missed).
    """
    for depth in range(1, max_hops + 1):
        cutoff = 2 * depth
        for node_path in nx.all_simple_paths(G, source, target, cutoff=cutoff):
            if len(node_path) - 1 == cutoff:
                yield node_path


class PathList(list["GraphPath"]):
    """The list of paths a search returned, carrying whether the search was **cut short**.

    A plain ``list`` in every other respect (indexing, iteration, ``==`` against a plain list), so
    existing callers are unaffected — but a caller can now *act* on truncation:

    >>> paths = find_paths_between(graph, "vinp", "vout")   # doctest: +SKIP
    >>> if paths.truncated:                                  # doctest: +SKIP
    ...     ...  # this is the `paths.cap` shortest paths, not every path

    The ``WARNING`` log line remains, but a log line is not something a program can branch on, and
    the truncated answer is otherwise indistinguishable from a complete one.

    :attr:`truncated` is ``True`` only when paths were actually left unenumerated: a search whose
    complete answer happens to be exactly ``max_paths`` long reports ``False``. Within the last,
    partially-enumerated length band the *choice* of paths follows the underlying DFS order, so
    ties at the cap boundary are arbitrary (the band itself is not: the result is contiguous from
    the shortest length up).
    """

    truncated: bool = False
    cap: int | None = None

    def __init__(
        self,
        paths: Iterable["GraphPath"] = (),
        *,
        truncated: bool = False,
        cap: int | None = None,
    ) -> None:
        super().__init__(paths)
        self.truncated = truncated
        self.cap = cap


# ---------------------------------------------------------------------------
# Public API — path finding
# ---------------------------------------------------------------------------
def find_paths_between(
    graph: CircuitGraph,
    net_a: str,
    net_b: str,
    *,
    shortest_only: bool = False,
    max_components: int | None = None,
    through_supply: bool = False,
    block_voltage_sources: bool = False,
    max_paths: int | None = DEFAULT_MAX_PATHS,
    respect_mosfet_state: bool = False,
    gs_short_is_off: bool = True,
) -> PathList:
    """All device-level paths connecting ``net_a`` to ``net_b`` (deterministically ordered).

    Each path is a chain of device traversals — ``M1.drain->M1.source->M2.gate->M2.source`` — built
    by walking the bipartite graph net→device→net→…→net. Net names are resolved case-insensitively
    (an absent or ambiguous name raises :class:`ValueError`); the two endpoints must be distinct.

    * ``shortest_only`` (default ``False``): return only the minimal-length paths (fewest device
      hops). :func:`shortest_paths_between` is the shorthand.
    * ``max_components`` (default ``None``): cap the number of device hops per path (bounds the
      search on dense graphs); ignored when ``shortest_only`` is set.
    * ``through_supply`` (default ``False``): allow routing *through* ``VDD``/``VSS``/``GND`` nets.
      Off by default because supply rails connect nearly everything and explode the path count; an
      endpoint may still be a rail.
    * ``block_voltage_sources`` (default ``False``): drop ideal voltage sources (``V…`` elements) as
      traversable devices, so no path threads *through* one (in one terminal, out the other). Off by
      default — a voltage source is walked like any other two-terminal device — so existing results
      are unchanged; turn it on to keep bias sources from bridging otherwise-separate signal nets. The
      source's terminal nets stay in the graph and remain reachable by any other route.
    * ``max_paths`` (default :data:`DEFAULT_MAX_PATHS`): **bound the search** at this many paths.
      The enumeration runs shortest-first and stops as soon as the cap is reached, so the result is
      the ``max_paths`` shortest paths — it is not a post-filter over a complete enumeration, which
      is why the cap exists at all (the number of simple paths grows factorially: the complete
      ``through_supply=True`` enumeration on a 16-device amplifier does not finish in minutes). A
      truncated result is reported at ``WARNING`` level *and* on the result itself
      (:attr:`PathList.truncated` / :attr:`PathList.cap`), because it is a *sample*, not the full
      set — and a log line is not something a caller can branch on. Pass ``None`` for the unbounded
      enumeration (only sane on a small graph, or with ``max_components``). The cap applies to
      :func:`shortest_paths_between` too, which forwards every keyword here.
    * ``respect_mosfet_state`` (default ``False``): make the trace conduction-aware. A MOSFET's
      DRAIN↔SOURCE channel is dropped when the device is off — i.e. gate–source shorted (Vgs = 0) —
      so its source–drain channel is never reported as a conduction hop. This is *channel-only*: the
      gate/bulk edges are left intact (the gate is still a signal terminal), so for a gate–source
      short — where the gate sits on the source net — a DRAIN↔GATE traversal can remain (the path is
      relabeled rather than removed); dropping the device outright is the deliberately-unadopted
      whole-device scope. A drain–source-shorted ("killed") device needs no special handling, since
      its DRAIN and SOURCE are already the same net (no channel hop arises). Off by default, so the
      trace is purely topological unless asked otherwise.
    * ``gs_short_is_off`` (default ``True``): the global enhancement-vs-depletion assumption used by
      ``respect_mosfet_state``. ``True`` treats a gate–source short as off; set ``False`` for
      depletion / negative-Vth devices that can still conduct at Vgs = 0 (then no channel is dropped).

    Returns a :class:`PathList` of :class:`GraphPath` (a ``list`` subclass, possibly empty when no
    path exists), sorted by length then label so the output is stable, and carrying whether the
    search was cut short by ``max_paths``.
    """
    na = _resolve_net(graph, net_a)
    nb = _resolve_net(graph, net_b)
    if na is nb:
        raise ValueError(
            f"net_a and net_b are the same net ({na.name!r}); a path needs two distinct endpoints"
        )
    if max_paths is not None and max_paths < 1:
        raise ValueError(f"max_paths must be a positive count or None, got {max_paths!r}")

    H = graph._G if through_supply else _without_supply(graph._G, keep={na, nb})
    if block_voltage_sources:
        H = _without_voltage_sources(H)
    if na not in H or nb not in H or not nx.has_path(H, na, nb):
        return PathList(cap=max_paths)

    off_channel = _off_channel_mosfets(graph, respect_mosfet_state, gs_short_is_off)
    # max_components bounds the all-paths search; it does not apply in shortest mode (the shortest
    # paths are returned whatever their length).
    eff_max = None if shortest_only else max_components

    # With channel filtering active, the topology-shortest path may route through an off transistor
    # while a valid longer one exists — so enumerate simple paths shortest-first and take the
    # shortest *valid* ones rather than trusting the node-level shortest search.
    if shortest_only and not off_channel:
        node_paths: Iterator[list] = iter(nx.all_shortest_paths(H, na, nb))
    else:
        # A simple path visits each device at most once, so the component count is the hop ceiling.
        hop_ceiling = sum(1 for n in H if isinstance(n, ComponentNode))
        max_hops = min(eff_max, hop_ceiling) if eff_max is not None else hop_ceiling
        node_paths = _node_paths_shortest_first(H, na, nb, max_hops)

    # Stream the enumeration and stop at the cap: `max_paths` is a bound ON the search, not a slice
    # of a finished list. The generator is shortest-first, so stopping early keeps the SHORTEST
    # paths (and `shortest_only` can stop the moment the hop count grows).
    paths: list[GraphPath] = []
    seen: set[tuple] = set()
    stopped_at_cap = False
    for node_path in node_paths:
        if shortest_only and paths and (len(node_path) - 1) // 2 > paths[0].length:
            break
        for path in _expand_node_path(graph, node_path, off_channel):
            key = (path.source, path.target, tuple(path.nets), path.label)
            if key not in seen:
                seen.add(key)
                paths.append(path)
        if max_paths is not None and len(paths) >= max_paths:
            stopped_at_cap = True
            break

    # Stopping AT the cap is not the same as leaving paths behind: a complete answer of exactly
    # `max_paths` paths trips the same `>=`. Ask the generator for one more before claiming the
    # result is a sample — otherwise the one signal a caller has that the answer is partial fires
    # on answers that are whole.
    truncated = stopped_at_cap and (
        (max_paths is not None and len(paths) > max_paths) or next(node_paths, None) is not None
    )

    if shortest_only and paths:
        shortest = min(p.length for p in paths)
        paths = [p for p in paths if p.length == shortest]
    paths.sort(key=lambda p: (p.length, p.label, tuple(p.nets)))
    if max_paths is not None and len(paths) > max_paths:
        paths = paths[:max_paths]
    if truncated:
        logger.warning(
            "find_paths_between(%r, %r): stopped at max_paths=%d inside the length-%d band — the "
            "result is the %d shortest paths, NOT the complete set (ties within that last band are "
            "arbitrary); raise max_paths, or bound the search with "
            "max_components/through_supply=False",
            na.name, nb.name, max_paths, paths[-1].length if paths else 0, len(paths),
        )
    return PathList(paths, truncated=truncated, cap=max_paths)


def shortest_paths_between(graph: CircuitGraph, net_a: str, net_b: str, **kwargs) -> PathList:
    """Shorthand for :func:`find_paths_between` with ``shortest_only=True``.

    Every keyword of :func:`find_paths_between` applies, **including ``max_paths``** — this
    entry point inherits its default of :data:`DEFAULT_MAX_PATHS`, so a query with more than that
    many equally-shortest paths returns a truncated shortest-set. Check ``result.truncated`` (or
    pass ``max_paths=None``) when the complete set matters.
    """
    kwargs.pop("shortest_only", None)
    return find_paths_between(graph, net_a, net_b, shortest_only=True, **kwargs)


# ---------------------------------------------------------------------------
# Public API — path diffing
# ---------------------------------------------------------------------------
def _pin_set(step: PathStep) -> frozenset[str]:
    """The unordered pin pair of a traversal — direction-insensitive (drain→source ≡ source→drain)."""
    return frozenset({step.in_pin, step.out_pin})


def _tag(step: PathStep, kind: StepDiffKind) -> PathStep:
    return step.model_copy(update={"diff_kind": kind})


def diff_paths(path_a: GraphPath, path_b: GraphPath) -> PathDiff:
    """Compare two paths device-by-device and classify how they differ.

    Steps are matched by device name; a matched device is *common* when both paths traverse it
    through the same pin pair (direction-insensitive), otherwise it is a *pin-only* difference (its
    two variants land in the respective exclusive segments). A device present in only one path is a
    *device-only* difference. The overall :attr:`PathDiff.kind` is ``IDENTICAL`` /
    ``PIN_ONLY`` / ``DEVICE_ONLY`` / ``DEVICE_PIN`` depending on which kinds of difference occur.

    Comparison is by device/net *name*, so the two paths should come from the same circuit (or two
    that share naming) for the result to be meaningful — typically two paths from one graph.
    """
    # Pair steps by device *occurrence*, not just by name: paths from find_paths_between visit a
    # device once, but diff_paths accepts any hand-built GraphPath, so a device may legitimately
    # recur. Keying on (name, k-th occurrence) — rather than collapsing to one step per name — keeps
    # the verdict correct when a device is traversed more than once.
    a_by: dict[str, list[PathStep]] = defaultdict(list)
    b_by: dict[str, list[PathStep]] = defaultdict(list)
    for step in path_a.steps:
        a_by[step.component].append(step)
    for step in path_b.steps:
        b_by[step.component].append(step)

    only_a: list[PathStep] = []
    only_b: list[PathStep] = []
    common: list[PathStep] = []
    has_pin_diff = False
    has_device_diff = False

    seen_a: dict[str, int] = defaultdict(int)
    for step in path_a.steps:  # walk A in order
        k = seen_a[step.component]
        seen_a[step.component] += 1
        peers = b_by[step.component]
        if k >= len(peers):  # B has no matching occurrence of this device
            only_a.append(_tag(step, StepDiffKind.DEVICE_ONLY))
            has_device_diff = True
        elif _pin_set(step) == _pin_set(peers[k]):
            common.append(_tag(step, StepDiffKind.COMMON))
        else:
            only_a.append(_tag(step, StepDiffKind.PIN_ONLY))
            has_pin_diff = True

    seen_b: dict[str, int] = defaultdict(int)
    for step in path_b.steps:  # the B side of each difference, in B order
        k = seen_b[step.component]
        seen_b[step.component] += 1
        peers = a_by[step.component]
        if k >= len(peers):
            only_b.append(_tag(step, StepDiffKind.DEVICE_ONLY))
            has_device_diff = True
        elif _pin_set(step) != _pin_set(peers[k]):
            only_b.append(_tag(step, StepDiffKind.PIN_ONLY))
            has_pin_diff = True
        # an equal pin set is a common step, already emitted from the A side

    if not only_a and not only_b:
        kind = DiffKind.IDENTICAL
    elif has_pin_diff and has_device_diff:
        kind = DiffKind.DEVICE_PIN
    elif has_pin_diff:
        kind = DiffKind.PIN_ONLY
    else:
        kind = DiffKind.DEVICE_ONLY

    return PathDiff(
        kind=kind,
        summary=_diff_summary(kind, only_a, only_b, common),
        only_in_a=PathSegment(label="only in path A", steps=only_a),
        only_in_b=PathSegment(label="only in path B", steps=only_b),
        common=PathSegment(label="common", steps=common),
    )


def _diff_summary(
    kind: DiffKind, only_a: list[PathStep], only_b: list[PathStep], common: list[PathStep]
) -> str:
    if kind is DiffKind.IDENTICAL:
        return f"Paths are identical: {len(common)} shared device traversal(s), no differences."
    pin_devs = sorted({s.component for s in only_a if s.diff_kind is StepDiffKind.PIN_ONLY})
    dev_a = sorted({s.component for s in only_a if s.diff_kind is StepDiffKind.DEVICE_ONLY})
    dev_b = sorted({s.component for s in only_b if s.diff_kind is StepDiffKind.DEVICE_ONLY})
    bits: list[str] = []
    if pin_devs:
        bits.append(f"pin-only on {', '.join(pin_devs)}")
    if dev_a:
        bits.append(f"only in A: {', '.join(dev_a)}")
    if dev_b:
        bits.append(f"only in B: {', '.join(dev_b)}")
    return f"{kind.value} difference ({len(common)} common): " + "; ".join(bits)
