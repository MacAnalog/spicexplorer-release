"""Functional-subcircuit detection — overlay pre-defined templates onto an input netlist.

Where :mod:`compare` asks *"are these two whole netlists the same circuit?"* (labeled graph
**isomorphism**), this module asks *"where does this small functional sub-circuit appear inside a
larger netlist?"* — labeled **subgraph monomorphism**. We build the nets⟷components ``MultiGraph``
for the template and the host (via :class:`~spicexplorer_circuitgraph.graph.CircuitGraph`), project
both to match signatures with the shared :mod:`_signatures` machinery, then enumerate every
wiring-preserving embedding of the template into the host with networkx's VF2
``subgraph_monomorphisms_iter`` (monomorphism, not induced isomorphism: the host net a template net
maps to is free to carry *extra* devices — exactly what a tail/load net does inside an OTA).

**Internal-node exactness.** Plain monomorphism lets *every* template net — including a sub-circuit's
private internal nodes — pick up extra host devices. For an internal node that is the wrong answer: a
cascode mirror's intermediate node (source of the cascode device) shared with unrelated circuitry is
no longer a clean cascode, yet monomorphism would still report one. ``match_internal_exact`` (**on by
default**) closes this hole: an *internal* template net — one that is neither a declared
:attr:`~spicexplorer_circuitgraph.templates.SubcircuitTemplate.ports` net nor a supply rail — must
map to a host net of *identical degree*, so it carries no devices beyond the template's. Port nets
(the sub-circuit's interface) and supply rails stay free to fan out, which is the asymmetry real
sub-circuit recognition needs. ``match_external_isolated`` (off by default) is the stricter,
opt-in companion: it keeps ports free to fan out but forbids a *single* external device from
bridging two of them — see :class:`~spicexplorer_circuitgraph._signatures.MatchOptions`.

Defaults match the current-mirror detection rules:

* **topology only** — device type + MOS polarity + pin-level wiring; instance/net names and sizing
  are ignored (``match_params``/``match_models`` off);
* **supply rails anchored by name/class** — ``VDD``/``VSS``/``GND`` only ever map to a rail of the
  same class (``match_supply=True``, the boolean the request asked for); every other net is free;
* **bulk ignored** (``match_bulk=False``) — a mirror is found whether its bulk ties to the source
  rail or to a separate body net (standard practice; see Aggarwal, Gupta & Gupta,
  *Microelectronics Journal* 53 (2016) 134-155). A template
  whose identity *is* its bulk wiring opts back in per-template via
  :attr:`SubcircuitTemplate.match_bulk <spicexplorer_circuitgraph.templates.SubcircuitTemplate.match_bulk>`
  (manifest key ``match_bulk: true``) — that one template is then matched with bulk edges kept while
  the rest of the run stays bulk-blind (see :func:`find_template_matches`);
* **internal nodes private** (``match_internal_exact=True``) — a template's internal nets must not
  pick up host devices beyond the template's (see the Internal-node exactness note above).

Setting ``match_polarity=False`` gives a polarity-agnostic search (provisioned, not the default).

**Arrays sharing a reference.** A multi-output mirror (one diode reference, N copies) is *not* a
single template — it is N embeddings of the 2-device simple-mirror template that all reuse the same
host diode. The enumerator finds them all (each copy → one match, every match citing the shared
reference), and :func:`group_matches` folds matches that share a reference device into one
multi-output :class:`MirrorGroup`. Matched sub-circuits are NOT removed from the host between
templates, so a cascode also yields its inner simple-mirror match; subsumption (a match whose device
set is a strict subset of another's) drops those from the primary list during grouping.

**Dependent (anchored) templates.** Some sub-circuits are only meaningful relative to another. A
differential pair, for instance, is a real diff-pair only when its shared tail node is biased by a
tail current source — two common-source devices that merely share a node are not. We model that as a
dependency instead of inflating the template: a template that declares a :data:`TAIL_BIAS_PORT`
(``CM_tail``) port is matched independently, then admitted by :func:`_admit_anchored` only when that
port lands on a net a current mirror's ``out`` port also lands on. So detection runs in two layers —
current mirrors first, then the templates anchored to their outputs — exactly the "layer on top of
current-mirror detection" the feature calls for. A dependent template may restrict *which* mirrors
are valid anchors via its
:attr:`~spicexplorer_circuitgraph.templates.SubcircuitTemplate.tail_sources` allow-list (mirror
template ids); an empty list accepts any detected mirror.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path

import networkx as nx
from networkx.algorithms.isomorphism import MultiGraphMatcher
from spicexplorer_core.spice_engine import NetlistView, NetlistViewLike

from ._signatures import (
    MatchOptions,
    component_signature,
    edge_match,
    node_match,
    signature_graph,
)
from .graph import CircuitGraph, OnUnknown
from .model.nodes import MosfetNode, StructuralRole
from .pdk import Pdk
from .templates import SubcircuitTemplate, TemplateLibrary, default_subcircuit_library

logger = logging.getLogger(__name__)

__all__ = [
    "SubcircuitMatch",
    "MirrorGroup",
    "find_template_matches",
    "find_subcircuits",
    "group_matches",
    "annotate_subcircuits",
]

# Tie-break order, preferred-first — used ONLY to pick the primary label when two templates match the
# *exact same* host device set (the loser becomes an `alternate`). Subset relationships are handled
# by device-count subsumption, not this list. The 4T double-cascode and the super-Wilson are distinct
# topologies (the Wilson feedback edge, output node → output-device gate, is present only in the
# latter), so they should not collide on a real host; `cascode` is ranked above `improved_wilson`
# only as a defensive default for the more-constrained reading. Unknown classes sort last.
_CLASS_SPECIFICITY = [
    "improved_high_swing_cascode",
    "selfbiased_high_swing_cascode",
    "high_swing_cascode",
    "cascode",
    "improved_wilson",
    "low_voltage_cascode",
    "wilson",
    "simple",
]


def _class_rank(mirror_class: str) -> int:
    try:
        return _CLASS_SPECIFICITY.index(mirror_class)
    except ValueError:
        return len(_CLASS_SPECIFICITY)


# Dependent ("anchored") templates -----------------------------------------------------------------
# A template port role whose host net must coincide with a detected current-mirror output for the
# match to be admitted. A differential pair declares this port on its shared tail node: the pair is a
# real diff-pair only when that tail is biased by a current source, so we resolve it as a *layer* on
# top of current-mirror detection rather than baking the source into the template. A template that
# declares this port is "dependent" and is matched in a second pass, after the independent
# (current-mirror) matches are known. Extend by giving a new dependent family the same port role.
TAIL_BIAS_PORT = "CM_tail"

# The port role a current-mirror template uses for its mirrored output branch — the set of host nets
# these land on are the valid anchors for a `TAIL_BIAS_PORT`.
_MIRROR_OUT_PORT = "out"

# Whole-block structural roles keyed off a template's *family*. For these families every matched MOS
# carries the family's role (there is no reference/output/cascode anatomy to distinguish — a
# pseudo-resistor cell or a pass gate is a symmetric two-terminal block), and the mirror-position
# logic in `_assign_roles` would otherwise mislabel them (their sources sit on signal nets, which
# reads as "cascode"). Extend by mapping a new family name to its per-device role.
_FAMILY_ROLES: dict[str, StructuralRole] = {
    "pseudo_resistor": StructuralRole.MOS_PSEUDO_RESISTOR,
    "transmission_gate": StructuralRole.MOS_ANALOG_SWITCH,
}


# ---------------------------------------------------------------------------
# Match results
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SubcircuitMatch:
    """One embedding of a template into the host (a single wiring-preserving placement).

    ``device_map`` / ``net_map`` map template names → host names; ``ports`` maps the template's port
    roles (``supply`` / ``ref_in`` / ``out`` / …) to the host nets they landed on.
    :attr:`reference_device` is the host image of the template's diode reference (``None`` for the
    diodeless externally-biased templates), and :attr:`output_devices` the host copy/cascode-output
    device(s). :attr:`match_bulk` records whether this embedding was matched with MOS bulk edges in
    play (the template's per-template ``match_bulk`` opt-in, or a global bulk-strict run) — a
    bulk-strict match is strictly more constrained than a bulk-blind one over the same devices, so
    :func:`group_matches` prefers it as the primary when both fire on the same device set.
    """

    template_id: str
    mirror_class: str
    polarity: str
    family: str
    devices: tuple[str, ...]  # host device names (sorted) — the matched cluster
    device_map: dict[str, str]  # template device name -> host device name
    net_map: dict[str, str]  # template net name -> host net name
    ports: dict[str, str]  # port role -> host net name
    reference_device: str | None
    output_devices: tuple[str, ...]
    match_bulk: bool = False  # matched with bulk edges kept (per-template opt-in or global)

    @property
    def device_set(self) -> frozenset[str]:
        return frozenset(self.devices)


@dataclass(frozen=True)
class MirrorGroup:
    """One resolved functional sub-circuit: primary matches that share a reference, merged.

    A simple mirror with N copies collapses into a single group whose :attr:`output_devices` lists
    all N (the request's "array of mirrors sharing the same reference + diode-connected MOSFET").
    :attr:`subsumed` carries the smaller matches absorbed into this one (e.g. the simple sub-mirror
    inside a cascode); :attr:`alternates` carries other templates that match the *same* device set
    (a genuine topological ambiguity) — both kept for transparency rather than silently dropped.
    """

    group_id: str
    template_id: str
    mirror_class: str
    polarity: str
    family: str
    reference_device: str | None
    output_devices: tuple[str, ...]
    devices: tuple[str, ...]
    ports: dict[str, str]
    members: tuple[SubcircuitMatch, ...] = field(repr=False, default=())
    subsumed: tuple[SubcircuitMatch, ...] = field(repr=False, default=())
    alternates: tuple[SubcircuitMatch, ...] = field(repr=False, default=())


# ---------------------------------------------------------------------------
# Template anatomy (intrinsic to a template — computed once, before matching)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Anatomy:
    reference_dev: str | None  # primary diode-connected device whose source is on the supply rail
    output_devs: tuple[str, ...]  # devices whose drain is the `out` port net


def _mos_terminals(graph: CircuitGraph, comp: MosfetNode) -> tuple[str | None, str | None, str | None]:
    """(drain, gate, source) net names for a MOS, from the live graph wiring."""
    conn = graph.connections(comp)
    return conn.get("DRAIN"), conn.get("GATE"), conn.get("SOURCE")


def _template_anatomy(template: SubcircuitTemplate) -> _Anatomy:
    """Locate the reference diode + output device(s) inside a template, in template-name space.

    The reference is the diode-connected MOS (drain net == gate net) whose source sits on the
    declared supply rail — the bottom diode every diode mirror is built around. Output devices are
    those whose drain lands on the declared ``out`` port net. Both are mapped to host names per match.
    """
    tg = template.graph
    supply = template.ports.get("supply")
    out_net = template.ports.get("out")
    diode_on_rail: list[str] = []
    output_devs: list[str] = []
    for comp in tg.get_components():
        if not isinstance(comp, MosfetNode):
            continue
        drain, gate, source = _mos_terminals(tg, comp)
        if drain is not None and drain == gate and source == supply:
            diode_on_rail.append(comp.name)
        if out_net is not None and drain == out_net:
            output_devs.append(comp.name)
    reference_dev = sorted(diode_on_rail)[0] if diode_on_rail else None
    return _Anatomy(reference_dev=reference_dev, output_devs=tuple(sorted(output_devs)))


def _bias_reference(host_graph: CircuitGraph, bias_net: str, polarity: str) -> str | None:
    """Find the diode-connected MOS that generates an *externally-biased* cascode's bias rail.

    The ``low_voltage_cascode`` template models its cascode bias as an external ``bias`` *port* — there
    is no diode in the 4-device template, so the match's ``reference_device`` is None. In a real
    circuit that bias node is set by a diode-connected device on the supply rail
    (``drain == gate == bias_net``, source on a rail). Recovering it lets the detector name the
    mirror's reference and fold the bias generator into the block, rather than reporting a
    reference-less cascode. Returns the host device name, or None when the bias is not a simple
    on-rail diode (e.g. a more elaborate bias generator — left to a future template).
    """
    net_by_name = {n.name: n for n in host_graph.get_nets()}
    for comp in host_graph.get_components():
        if not isinstance(comp, MosfetNode) or comp.polarity.value.lower() != polarity.lower():
            continue
        drain, gate, source = _mos_terminals(host_graph, comp)
        if drain is None or drain != gate or drain != bias_net:
            continue  # not a diode-connected device sitting on the bias node
        snet = net_by_name.get(source) if source else None
        if snet is not None and snet.is_supply:
            return comp.name
    return None


# ---------------------------------------------------------------------------
# Coercion + options
# ---------------------------------------------------------------------------
HostLike = CircuitGraph | NetlistViewLike | str | Path


def _as_graph(host: HostLike, *, pdk: Pdk | None, on_unknown: OnUnknown) -> CircuitGraph:
    if isinstance(host, CircuitGraph):
        return host
    if isinstance(host, NetlistViewLike):
        view = host
    elif isinstance(host, Path):
        view = NetlistView.from_file(host)
    elif isinstance(host, str):
        view = NetlistView.from_string(host, dialect="auto") if "\n" in host else NetlistView.from_file(host)
    else:
        raise TypeError(f"cannot build a CircuitGraph from a {type(host).__name__}")
    graph = CircuitGraph.from_netlist(view, name="host", pdk=pdk, on_unknown=on_unknown)
    if graph.skipped_components:
        # The caller handed raw netlist text/a path, so this graph is built and discarded in here —
        # its `skipped_components` would never be reachable. Detection ran over an INCOMPLETE host:
        # a template can only be found in, or ruled out of, the part that could be typed. Say it
        # once, with the census (from_netlist's own per-device warnings do not add up to a verdict).
        logger.warning(
            "host netlist: %d device(s) could not be modeled and are invisible to subcircuit "
            "detection (%s); pass on_unknown='raise' to refuse an incomplete host",
            len(graph.skipped_components),
            ", ".join(sorted(set(graph.skipped_components))),
        )
    return graph


def _resolve_options(
    options: MatchOptions | None,
    *,
    match_supply: bool,
    match_polarity: bool,
    match_bulk: bool,
    match_internal_exact: bool,
    match_external_isolated: bool = False,
) -> MatchOptions:
    if options is not None:
        return options
    return MatchOptions(
        match_supply=match_supply,
        match_polarity=match_polarity,
        match_bulk=match_bulk,
        match_internal_exact=match_internal_exact,
        match_external_isolated=match_external_isolated,
        # detection is purely topological: never gate on sizing/model/role
        match_params=False,
        match_models=False,
        match_structural_role=False,
    )


def _population_covers(host_graph: CircuitGraph, template: CircuitGraph, opts: MatchOptions) -> bool:
    """Cheap necessary condition: the host must contain ≥ the template's count of each device kind.

    Lets us skip the (worst-case exponential) VF2 enumeration for templates that cannot possibly
    embed — e.g. a 5-device template against a host with only 2 NMOS.
    """
    host_pop = Counter(component_signature(c, opts) for c in host_graph.get_components())
    tpl_pop = Counter(component_signature(c, opts) for c in template.get_components())
    return all(host_pop[sig] >= n for sig, n in tpl_pop.items())


# ---------------------------------------------------------------------------
# Core matching
# ---------------------------------------------------------------------------
def _internal_net_degrees(
    template: SubcircuitTemplate, g_tpl: nx.MultiGraph
) -> dict[str, int]:
    """Required signature-graph degree of each *internal* template net.

    Internal = not a declared port and not a supply rail; those are the nodes that must stay private
    to the sub-circuit. Ports (the interface) and supply rails are intentionally absent — they are
    allowed to fan out. Degrees are read from the signature graph ``g_tpl`` so they already reflect
    the active options (e.g. dropped bulk edges, passive-symmetry collapsing), matching how the host
    side will be measured.
    """
    port_nets = set(template.ports.values())
    return {
        net.name: g_tpl.degree(("net", net.name))
        for net in template.graph.get_nets()
        if net.name not in port_nets and not net.is_supply
    }


def _internal_nets_exact(
    g_host: nx.MultiGraph, net_h2t: dict[str, str], internal_degrees: dict[str, int]
) -> bool:
    """True if every internal template net maps to a host net of identical degree.

    Equal degree means the host node carries no devices beyond the template's, so the matched
    internal node is genuinely private to the sub-circuit rather than shared with the rest of the
    host. Template nets not in ``internal_degrees`` (ports, supply rails) are skipped — they are free
    to fan out.
    """
    return all(
        g_host.degree(("net", host_net)) == degree
        for host_net, tpl_net in net_h2t.items()
        if (degree := internal_degrees.get(tpl_net)) is not None
    )


def _external_isolated(
    g_host: nx.MultiGraph,
    net_h2t: dict[str, str],
    matched_devs: set[str],
    supply_tpl_nets: frozenset[str],
) -> bool:
    """True if no host device *outside* the match bridges two of the match's non-supply template nets.

    A port may fan out, but only onto components that are not part of this same sub-circuit: an
    external device incident to two of the template's nets would wire two template pins together (a
    connection the template does not model), so the embedding is rejected. Supply rails are exempt —
    they are globally shared. Counted on the signature graph, so dropped bulk edges (when
    ``match_bulk`` is off) do not register as bridges, consistent with the rest of the match.
    """
    touched: dict[str, int] = {}
    for host_net, tpl_net in net_h2t.items():
        if tpl_net in supply_tpl_nets:
            continue
        for neighbor in g_host.neighbors(("net", host_net)):
            dev = neighbor[1]
            if dev in matched_devs:
                continue
            touched[dev] = touched.get(dev, 0) + 1
            if touched[dev] >= 2:
                return False
    return True


def find_template_matches(
    host_graph: CircuitGraph,
    template: SubcircuitTemplate,
    opts: MatchOptions,
) -> list[SubcircuitMatch]:
    """Every embedding of one ``template`` into ``host_graph`` (deduped by host device set).

    Automorphic duplicates (the same host devices reached via the template's own symmetry, e.g. two
    parallel diodes) collapse to one match; genuinely distinct placements (different output copies)
    are all kept. ``opts.match_internal_exact`` drops embeddings whose internal nodes are shared with
    the rest of the host, and ``opts.match_external_isolated`` drops embeddings whose ports are
    cross-wired by a single external device (see :func:`_internal_nets_exact` / :func:`_external_isolated`).

    **Per-template bulk matching.** A template flagged ``match_bulk``
    (:attr:`~spicexplorer_circuitgraph.templates.SubcircuitTemplate.match_bulk`) is matched with MOS
    bulk/body edges *kept* in both the host and template projections, even when the run-level option
    dropped them — so the template's drawn bulk wiring (a rail tie, an isolated well) becomes part of
    its identity. One-way: the flag can only add the constraint, never relax a global
    ``match_bulk=True``. Every other template in the same run stays bulk-blind.
    """
    if template.match_bulk and not opts.match_bulk:
        opts = replace(opts, match_bulk=True)
    tg = template.graph
    if not _population_covers(host_graph, tg, opts):
        return []

    g_host = signature_graph(host_graph, opts, {})
    g_tpl = signature_graph(tg, opts, {})
    matcher = MultiGraphMatcher(g_host, g_tpl, node_match=node_match, edge_match=edge_match)

    anat = _template_anatomy(template)
    internal_degrees = _internal_net_degrees(template, g_tpl) if opts.match_internal_exact else {}
    supply_tpl_nets = (
        frozenset(n.name for n in tg.get_nets() if n.is_supply)
        if opts.match_external_isolated
        else frozenset()
    )
    # An automorphic template — a differential pair's two symmetric halves, a mirror's interchangeable
    # outputs — admits several monomorphisms onto the *same* host device set, and
    # ``subgraph_monomorphisms_iter`` yields them in hash-dependent order. Keeping the first seen made the
    # port orientation (which input gate is ``in_p`` vs ``in_n``, which drain ``out_p`` vs ``out_n``)
    # non-deterministic across runs. Instead keep, per host device set, the embedding with the
    # lexicographically smallest port mapping — a canonical, run-stable choice that fixes the orientation.
    best: dict[frozenset[str], tuple[tuple[tuple[str, str], ...], SubcircuitMatch]] = {}
    for iso in matcher.subgraph_monomorphisms_iter():
        # iso: host (kind, name) -> template (kind, name), over the matched subset.
        dev_h2t = {h[1]: t[1] for h, t in iso.items() if h[0] == "comp"}
        net_h2t = {h[1]: t[1] for h, t in iso.items() if h[0] == "net"}
        # Reject embeddings whose internal nodes pick up extra host devices, or (when isolation is
        # requested) whose ports are cross-wired by an external device — done before the canonical pick
        # so a rejected automorphic variant can never displace a valid one of equal devices.
        if internal_degrees and not _internal_nets_exact(g_host, net_h2t, internal_degrees):
            continue
        if opts.match_external_isolated and not _external_isolated(
            g_host, net_h2t, set(dev_h2t), supply_tpl_nets
        ):
            continue

        device_map = {t: h for h, t in dev_h2t.items()}
        net_map = {t: h for h, t in net_h2t.items()}
        ports = {
            role: net_map[tnet] for role, tnet in template.ports.items() if tnet in net_map
        }
        key = frozenset(dev_h2t)
        canon = tuple(sorted(ports.items()))
        if key in best and canon >= best[key][0]:
            continue  # a canonical (or equal) variant of this device set is already kept

        reference_device = device_map.get(anat.reference_dev) if anat.reference_dev else None
        # Externally-biased cascodes carry no diode in the template (reference is None); recover the
        # on-rail diode that generates the bias from the host and fold it into the block.
        recovered: tuple[str, ...] = ()
        if reference_device is None and "bias" in template.ports:
            bias_net = ports.get("bias")
            ref = _bias_reference(host_graph, bias_net, template.polarity) if bias_net else None
            if ref is not None and ref not in dev_h2t:
                reference_device, recovered = ref, (ref,)
        output_devices = tuple(
            sorted(device_map[d] for d in anat.output_devs if d in device_map)
        )
        best[key] = (
            canon,
            SubcircuitMatch(
                template_id=template.id,
                mirror_class=template.mirror_class,
                polarity=template.polarity,
                family=template.family,
                devices=tuple(sorted(set(dev_h2t) | set(recovered))),
                device_map=device_map,
                net_map=net_map,
                ports=ports,
                reference_device=reference_device,
                output_devices=output_devices,
                match_bulk=opts.match_bulk,
            ),
        )
    # Deterministic order (the iterator's is hash-dependent): by template then host device set.
    return [m for _, m in sorted(best.values(), key=lambda cm: (cm[1].template_id, cm[1].devices))]


def _rail_driven_nets(host_graph: CircuitGraph) -> dict[str, set[str]]:
    """Map each net that is the drain of a *rail-sourced* MOS → the set of supply rails it is driven
    from.

    Such a net is the output of a current source (a device whose source sits on a supply rail) — a
    valid tail-bias node *even when that source's mirror was not detected as its own block*. Many real
    amplifiers bias the input pair's tail from an externally-biased mirror leg (its gate is set by a
    cascode/mirror output, not an on-rail diode), so the leg matches no diode-referenced template and
    leaves no ``out`` port to anchor to. This recovers exactly that case.
    """
    net_by_name = {n.name: n for n in host_graph.get_nets()}
    driven: dict[str, set[str]] = {}
    for comp in host_graph.get_components():
        if not isinstance(comp, MosfetNode):
            continue
        drain, _gate, source = _mos_terminals(host_graph, comp)
        if drain is None or source is None:
            continue
        snet = net_by_name.get(source)
        if snet is not None and snet.is_supply:
            driven.setdefault(drain, set()).add(source)
    return driven


def _admit_anchored(
    dependent: list[SubcircuitMatch],
    anchors: list[SubcircuitMatch],
    tail_sources: dict[str, tuple[str, ...]],
    host_graph: CircuitGraph,
) -> list[SubcircuitMatch]:
    """Keep the dependent matches whose tail port is biased by a current source.

    ``anchors`` are the independently-detected matches (the current mirrors); their ``out`` port nets
    are the *primary* valid anchors — a dependent match (e.g. a differential pair) is admitted when
    its :data:`TAIL_BIAS_PORT` coincides with a detected mirror's output (filtered by the
    ``tail_sources`` allow-list: an NMOS pair anchors to NMOS mirrors, a PMOS pair to PMOS ones; an
    empty list accepts any).

    **Fallback (externally-biased tail).** When the tail lands on *no detected mirror output at all*,
    it is still admitted if a rail-sourced MOS drives the tail net *from the pair's own supply rail* —
    i.e. the tail is biased by a current source whose mirror simply was not recognised (a
    missing-template coverage gap, not a missing tail bias). The fallback is deliberately scoped to the
    *un-anchored* tail only: if the tail *is* a detected mirror output but of a type the
    ``tail_sources`` allow-list disallows, that is a considered rejection and stands (the allow-list is
    not bypassed). Two common-source devices sharing a node that nothing drives from the rail are still
    dropped (no tail bias).
    """
    if not dependent:
        return []
    # Group the available anchor output nets by the mirror template that produced them, so an
    # allow-list can select a subset; `any_out` is every detected mirror output (any template).
    out_by_source: dict[str, set[str]] = {}
    for m in anchors:
        net = m.ports.get(_MIRROR_OUT_PORT)
        if net is not None:
            out_by_source.setdefault(m.template_id, set()).add(net)
    any_out: set[str] = set().union(*out_by_source.values()) if out_by_source else set()
    rail_driven = _rail_driven_nets(host_graph)

    admitted: list[SubcircuitMatch] = []
    for m in dependent:
        tail = m.ports.get(TAIL_BIAS_PORT)
        if tail is None:
            continue
        allowed_ids = tail_sources.get(m.template_id) or ()
        valid = set().union(*(out_by_source.get(s, set()) for s in allowed_ids)) if allowed_ids else any_out
        if tail in valid:
            admitted.append(m)
            continue
        if tail in any_out:
            continue  # the tail IS a detected mirror output, just not an allowed one — respect that
        # The tail is anchored to no detected mirror: recover a real pair on an externally-biased tail
        # (a current source on the pair's own supply rail whose mirror was not recognised).
        supply = m.ports.get("supply")
        if supply is not None and supply in rail_driven.get(tail, set()):
            admitted.append(m)
    return admitted


def _warn_unknown_tail_sources(
    tail_sources: dict[str, tuple[str, ...]], known_ids: set[str]
) -> None:
    """Warn if an allow-list names a template id absent from the library (likely a typo).

    An unknown id silently contributes no anchor net, so a fully-mistyped allow-list would drop every
    match with no other signal — surface it once per offending dependent template instead.
    """
    for dep_id, sources in tail_sources.items():
        unknown = [s for s in sources if s not in known_ids]
        if unknown:
            logger.warning(
                "template %r lists tail_sources not in the library: %s", dep_id, sorted(unknown)
            )


def find_subcircuits(
    host: HostLike,
    library: TemplateLibrary | None = None,
    *,
    match_supply: bool = True,
    match_polarity: bool = True,
    match_bulk: bool = False,
    match_internal_exact: bool = True,
    match_external_isolated: bool = False,
    options: MatchOptions | None = None,
    pdk: Pdk | None = None,
    on_unknown: OnUnknown = "skip",
) -> list[SubcircuitMatch]:
    """All raw template embeddings found in ``host`` (across every template in ``library``).

    ``host`` may be a :class:`CircuitGraph`, a
    :class:`~spicexplorer_core.spice_engine.NetlistView`, a path, or raw netlist text. ``library``
    defaults to the full shipped catalogue (current mirrors + miscellaneous). Pass ``options`` to
    override the booleans with a full :class:`~spicexplorer_circuitgraph._signatures.MatchOptions`.
    Use :func:`group_matches` to resolve these raw matches into multi-output groups.

    **Dependent templates.** A template that declares a :data:`TAIL_BIAS_PORT` (``CM_tail``) port is
    *anchored*: it is matched independently, then admitted only if its tail port lands on a net that a
    current mirror's ``out`` port also lands on. This runs as a layer on top of current-mirror
    detection, so a differential pair is reported only when its tail is biased by a detected mirror.
    A dependent template may further restrict *which* mirrors qualify via its
    :attr:`~spicexplorer_circuitgraph.templates.SubcircuitTemplate.tail_sources` allow-list (see
    :func:`_admit_anchored`).

    ``match_internal_exact`` rejects embeddings whose internal (non-port, non-supply) nets pick up
    host devices beyond the template's; ``match_external_isolated`` additionally rejects embeddings
    whose ports are cross-wired by a single external device (off by default — see
    :class:`~spicexplorer_circuitgraph._signatures.MatchOptions`). See :func:`find_template_matches`.
    """
    lib = library if library is not None else default_subcircuit_library()
    opts = _resolve_options(
        options,
        match_supply=match_supply,
        match_polarity=match_polarity,
        match_bulk=match_bulk,
        match_internal_exact=match_internal_exact,
        match_external_isolated=match_external_isolated,
    )
    host_graph = _as_graph(host, pdk=pdk, on_unknown=on_unknown)
    independent: list[SubcircuitMatch] = []
    dependent: list[SubcircuitMatch] = []
    tail_sources: dict[str, tuple[str, ...]] = {}
    for template in lib:
        if TAIL_BIAS_PORT in template.ports:
            dependent.extend(find_template_matches(host_graph, template, opts))
            tail_sources[template.id] = tuple(template.tail_sources)
        else:
            independent.extend(find_template_matches(host_graph, template, opts))
    _warn_unknown_tail_sources(tail_sources, {t.id for t in lib})
    return independent + _admit_anchored(dependent, independent, tail_sources, host_graph)


# ---------------------------------------------------------------------------
# Resolution — subsumption + shared-reference grouping
# ---------------------------------------------------------------------------
def group_matches(matches: list[SubcircuitMatch]) -> list[MirrorGroup]:
    """Resolve raw matches into functional sub-circuit groups.

    Three steps:

    1. **maximality** — a match whose host device set is a *strict subset* of another's (the simple
       sub-mirror inside a cascode) is dropped from the primaries and attached to the group(s) that
       contain it as ``subsumed``.
    2. **equal-set collapse** — when several templates match the *exact same* device set (e.g. two
       hand-drawn templates that are topologically identical), the preferred class becomes the
       primary and the rest are recorded as ``alternates``. Within a class rank, a **bulk-strict
       match wins over a bulk-blind one**: a template matched with its bulk edges in play
       (per-template ``match_bulk``) asserts strictly more about the host than its bulk-blind twin,
       so it is the more specific label — e.g. the rail-tied transmission gate becomes the primary
       on a rail-bulk host, with the bulk-blind canonical pair kept as its alternate.
    3. **shared-reference grouping** — among the surviving primaries, those sharing a
       ``(polarity, reference_device, mirror_class)`` merge into one multi-output group (the array
       case). Primaries without a reference device each form their own group.
    """
    if not matches:
        return []

    # --- step 1: maximality ---------------------------------------------------------------------
    maximal: list[SubcircuitMatch] = []
    subsumed_all: list[SubcircuitMatch] = []
    for m in matches:
        if any(m.device_set < o.device_set for o in matches):
            subsumed_all.append(m)
        else:
            maximal.append(m)

    # --- step 2: collapse equal-device-set maximal matches → primary + alternates ---------------
    by_set: dict[frozenset[str], list[SubcircuitMatch]] = {}
    for m in maximal:
        by_set.setdefault(m.device_set, []).append(m)
    primaries: list[SubcircuitMatch] = []
    alternates_of: dict[int, list[SubcircuitMatch]] = {}
    for candidates in by_set.values():
        # Rank: class specificity, then bulk-strictness (a bulk-aware match is the more specific
        # claim about the same devices — see the docstring), then template id for determinism.
        ranked = sorted(
            candidates,
            key=lambda x: (_class_rank(x.mirror_class), not x.match_bulk, x.template_id),
        )
        primaries.append(ranked[0])
        if len(ranked) > 1:
            alternates_of[id(ranked[0])] = ranked[1:]

    # --- step 3: shared-reference grouping ------------------------------------------------------
    grouped: dict[tuple, list[SubcircuitMatch]] = {}
    standalone: list[SubcircuitMatch] = []
    for m in primaries:
        if m.reference_device is None:
            standalone.append(m)
        else:
            grouped.setdefault((m.polarity, m.reference_device, m.mirror_class), []).append(m)

    counters: dict[str, int] = {}

    def _next_id(template_id: str) -> str:
        counters[template_id] = counters.get(template_id, 0) + 1
        return f"{template_id}#{counters[template_id]}"

    def _subsumed_for(devices: frozenset[str]) -> tuple[SubcircuitMatch, ...]:
        return tuple(
            sorted((s for s in subsumed_all if s.device_set < devices), key=lambda x: x.devices)
        )

    def _alternates_for(members: list[SubcircuitMatch]) -> tuple[SubcircuitMatch, ...]:
        out: list[SubcircuitMatch] = []
        for mem in members:
            out.extend(alternates_of.get(id(mem), []))
        return tuple(out)

    result: list[MirrorGroup] = []

    # grouped (shared-reference) — deterministic order by reference device, then class, then polarity
    for _, members in sorted(grouped.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        members = sorted(members, key=lambda x: x.devices)
        rep = members[0]
        outputs = tuple(sorted({d for mem in members for d in mem.output_devices}))
        devices_set: frozenset[str] = frozenset().union(*(mem.device_set for mem in members))
        result.append(
            MirrorGroup(
                group_id=_next_id(rep.template_id),
                template_id=rep.template_id,
                mirror_class=rep.mirror_class,
                polarity=rep.polarity,
                family=rep.family,
                reference_device=rep.reference_device,
                output_devices=outputs,
                devices=tuple(sorted(devices_set)),
                ports=dict(rep.ports),
                members=tuple(members),
                subsumed=_subsumed_for(devices_set),
                alternates=_alternates_for(members),
            )
        )

    # standalone (no reference device — externally-biased cascodes, etc.)
    for m in sorted(standalone, key=lambda x: x.devices):
        result.append(
            MirrorGroup(
                group_id=_next_id(m.template_id),
                template_id=m.template_id,
                mirror_class=m.mirror_class,
                polarity=m.polarity,
                family=m.family,
                reference_device=m.reference_device,
                output_devices=m.output_devices,
                devices=m.devices,
                ports=dict(m.ports),
                members=(m,),
                subsumed=_subsumed_for(m.device_set),
                alternates=_alternates_for([m]),
            )
        )
    return result


# ---------------------------------------------------------------------------
# Annotation — write the overlay back onto a graph
# ---------------------------------------------------------------------------
def annotate_subcircuits(
    graph: CircuitGraph,
    library: TemplateLibrary | None = None,
    *,
    match_supply: bool = True,
    match_polarity: bool = True,
    match_bulk: bool = False,
    match_internal_exact: bool = True,
    match_external_isolated: bool = False,
    options: MatchOptions | None = None,
    set_roles: bool = True,
) -> list[MirrorGroup]:
    """Detect functional sub-circuits in ``graph`` and overlay them (mutates ``graph`` in place).

    Runs :func:`find_subcircuits` + :func:`group_matches`, stores the resolved groups on
    ``graph.subcircuit_matches``, and (when ``set_roles``) tags the matched MOS devices'
    ``structural_role``: in a current mirror, a device whose source sits on a supply rail →
    :attr:`StructuralRole.MOS_CURRENT_MIRROR`, a stacked device (source on an internal net) →
    :attr:`StructuralRole.MOS_CASCODE_DEVICE`; in a tail-biased differential pair, both devices →
    :attr:`StructuralRole.MOS_DIFFERENTIAL_PAIR` and the device biasing the tail →
    :attr:`StructuralRole.MOS_TAIL_CURRENT_SOURCE`. Returns the groups.

    The graph is mutated in place; pass a copy (``CircuitGraphDoc.from_graph(g).to_graph()``) first
    if you need to keep the original pristine.
    """
    matches = find_subcircuits(
        graph,
        library,
        match_supply=match_supply,
        match_polarity=match_polarity,
        match_bulk=match_bulk,
        match_internal_exact=match_internal_exact,
        match_external_isolated=match_external_isolated,
        options=options,
    )
    groups = group_matches(matches)
    graph.subcircuit_matches = list(groups)
    if set_roles:
        _assign_roles(graph, groups)
    return groups


def _assign_roles(graph: CircuitGraph, groups: list[MirrorGroup]) -> None:
    """Tag matched MOS devices with a structural role from their position in the sub-circuit.

    The roles are deliberately fine-grained so downstream consumers (LLM annotation, gm/ID sizing,
    block-aware placement) can act on a device's *function*, not just its membership:

    * the mirror's **reference** — the diode-connected device that sets the bias current —
      → :attr:`StructuralRole.MOS_CURRENT_MIRROR_REFERENCE` (the one a sizer solves first);
    * the mirror's **output copy/copies** (also rail-sourced) → :attr:`StructuralRole.MOS_CURRENT_MIRROR`;
    * a **stacked** device whose source sits on an internal node → :attr:`StructuralRole.MOS_CASCODE_DEVICE`;
    * both devices of a tail-biased **differential pair** → :attr:`StructuralRole.MOS_DIFFERENTIAL_PAIR`;
    * the device **biasing the pair's tail** (drain on the ``CM_tail`` net) →
      :attr:`StructuralRole.MOS_TAIL_CURRENT_SOURCE` (overriding a plain mirror-output label, but not a
      cascode — see the second pass below);
    * every device of a **family-role** group — a whole-block role keyed off the template's family
      (:data:`_FAMILY_ROLES`): a pseudo-resistor cell → :attr:`StructuralRole.MOS_PSEUDO_RESISTOR`, a
      transmission gate → :attr:`StructuralRole.MOS_ANALOG_SWITCH`. These families are neither mirrors
      nor tail-anchored pairs, so the mirror-position logic below would mislabel them (their sources
      sit on signal nets, which reads as "cascode").
    """
    comp_by_name = {c.name: c for c in graph.get_components()}
    net_by_name = {n.name: n for n in graph.get_nets()}
    for group in groups:
        # A tail-biased group (the differential pair) is not a mirror — its devices are the pair.
        is_diff_pair = TAIL_BIAS_PORT in group.ports
        family_role = _FAMILY_ROLES.get(group.family)
        for dev_name in group.devices:
            comp = comp_by_name.get(dev_name)
            if not isinstance(comp, MosfetNode):
                continue  # role taxonomy here covers the MOS sub-circuit core only
            if family_role is not None:
                comp.structural_role = family_role
                continue
            if is_diff_pair:
                comp.structural_role = StructuralRole.MOS_DIFFERENTIAL_PAIR
                continue
            source_net = graph.connections(comp).get("SOURCE")
            net = net_by_name.get(source_net) if source_net else None
            on_rail = net is not None and net.is_supply
            if not on_rail:
                comp.structural_role = StructuralRole.MOS_CASCODE_DEVICE
            elif dev_name == group.reference_device:
                comp.structural_role = StructuralRole.MOS_CURRENT_MIRROR_REFERENCE
            else:
                comp.structural_role = StructuralRole.MOS_CURRENT_MIRROR

    # Second pass — the differential pair's tail current source. A pair is admitted only when its
    # shared-source ``CM_tail`` net is biased by a current source (``_admit_anchored``), but that
    # biasing device is *not* a member of the pair's group: it is the MOS whose **drain** sits on the
    # tail net (sourcing the bias current into the pair). Tag it ``MOS_TAIL_CURRENT_SOURCE`` — its
    # role in the diff-pair context. This takes precedence over a plain ``MOS_CURRENT_MIRROR`` it may
    # have earned as a mirror output, but it does not override a ``MOS_CASCODE_DEVICE`` (a cascoded
    # tail's top device stays a cascode, sourced on an internal node, not the tail net's driver).
    tail_nets = {g.ports[TAIL_BIAS_PORT] for g in groups if TAIL_BIAS_PORT in g.ports}
    if tail_nets:
        for comp in comp_by_name.values():
            if not isinstance(comp, MosfetNode):
                continue
            if graph.connections(comp).get("DRAIN") in tail_nets and comp.structural_role in (
                None,
                StructuralRole.MOS_CURRENT_MIRROR,
            ):
                comp.structural_role = StructuralRole.MOS_TAIL_CURRENT_SOURCE
