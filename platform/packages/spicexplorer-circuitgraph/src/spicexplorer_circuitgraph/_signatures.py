"""Shared match-signature machinery for graph comparison and subcircuit detection.

Both *full-graph equivalence* (:mod:`compare`) and *subcircuit detection* (:mod:`match`) reduce a
:class:`~spicexplorer_circuitgraph.graph.CircuitGraph` to a plain ``networkx.MultiGraph`` whose
nodes carry a match *signature* and whose edges carry a pin *token*, then run a VF2 matcher
(``is_isomorphic`` for equivalence, ``subgraph_monomorphisms_iter`` for detection). This module
owns that projection so the two callers agree bit-for-bit on what "the same kind of device / net /
pin" means — change the rule here and both the equivalence test and the detector move together.

What participates in a match is controlled by :class:`MatchOptions`. The defaults are topological
(device type + MOS polarity + pin-level wiring) with supply rails anchored by class; everything
else (sizing, model strings, heuristic roles, and — for detection — the bulk pin) is opt-in.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import networkx as nx

from .graph import CircuitGraph
from .model.edges import PinTypeMOSFET
from .model.nodes import (
    ComponentNode,
    DeviceType,
    MosfetNode,
    NetNode,
    SubcktInstanceNode,
)

# Number of significant figures a numeric parameter is canonicalized to before comparison, so that
# eng-equal values written differently ("0.18u" vs "180n") hash and compare equal.
_PARAM_SIG_FIGS = 9

# Device types whose two terminals are electrically interchangeable (non-polar passives). Sources
# (V/I) are deliberately excluded — their terminals carry a real polarity.
_SYMMETRIC_PASSIVES = frozenset({DeviceType.RES, DeviceType.CAP, DeviceType.IND})

# The edge token used for a symmetric passive terminal — both pins collapse to it so a terminal
# swap does not perturb the wiring signature.
_SYMMETRIC_PIN = "~"

# The pin token for a MOSFET bulk/body terminal (matched only when MatchOptions.match_bulk).
_BULK_PIN = PinTypeMOSFET.BULK.value


@dataclass(frozen=True)
class MatchOptions:
    """Resolved knobs controlling what counts as "the same" device / net / wiring.

    The first six are shared with the comparison API (see
    :func:`~spicexplorer_circuitgraph.compare.compare_graphs`). ``match_bulk`` is used by the
    subcircuit detector: turning it off drops MOS bulk/body edges from the projection, so a mirror
    is recognised whether its bulk ties to the source rail or to a separate body net (standard
    practice — see the current-mirror detection notes). Comparison keeps ``match_bulk=True``.

    ``match_internal_exact`` (detection only) tightens the otherwise-pure monomorphism: when on, a
    template net that is *internal* (not a declared port and not a supply rail) must map to a host
    net of identical degree — i.e. the host node may carry no devices beyond the template's, so the
    internal node is genuinely private to the matched sub-circuit. Port and supply nets stay free to
    fan out (that is what a port *is*). **On by default** for detection (a shared internal node means
    a different topology, so accepting it would be a false positive); set it ``False`` for the older,
    looser monomorphism. Comparison ignores it. See
    :func:`~spicexplorer_circuitgraph.match.find_template_matches`.

    ``match_external_isolated`` (detection only) is a *stricter* port-isolation rule, complementary
    to ``match_internal_exact``: when on, no host device *outside* the matched sub-circuit may be
    incident to two or more of the template's (non-supply) nets. A port stays free to fan out, but
    only onto components that are not part of the same match — an external device touching two
    template nets would wire two template pins together, a connection the template does not model.
    Supply rails are exempt (they are globally shared). **Off by default**: it rejects legitimate
    structures whose interface is *meant* to be cross-wired by a single external device — e.g. an
    active-loaded differential pair, whose load-mirror output device gates off one drain and lands on
    the other, bridging both output ports. Enable it only to detect sub-circuits that must be
    isolated except at ports going to *distinct* external components. Comparison ignores it.
    """

    match_polarity: bool = True
    match_params: bool = False
    match_models: bool = False
    match_supply: bool = True
    match_structural_role: bool = False
    passive_symmetry: bool = True
    match_bulk: bool = True
    match_internal_exact: bool = True
    match_external_isolated: bool = False


# ---------------------------------------------------------------------------
# Signatures — what makes two nodes / two pins "the same kind"
# ---------------------------------------------------------------------------
def norm_value(value: str | float) -> str:
    """Canonicalize one parameter value so eng-equal forms compare equal.

    Numbers (and eng strings like ``"0.18u"``) are parsed and rendered to a fixed precision;
    anything that is not numeric is kept as a stripped, lower-cased string.
    """
    if isinstance(value, (int, float)):
        return format(float(value), f".{_PARAM_SIG_FIGS}g")
    text = str(value).strip()
    try:
        from spicexplorer_core.eng import parse_value

        return format(float(parse_value(text)), f".{_PARAM_SIG_FIGS}g")
    except Exception:
        return text.lower()


def param_signature(params: dict[str, str | float]) -> frozenset[tuple[str, str]]:
    """Order- and case-independent, eng-normalized signature of a parameter dict."""
    return frozenset((str(key).strip().lower(), norm_value(val)) for key, val in params.items())


def component_signature(comp: ComponentNode, opts: MatchOptions) -> tuple[object, ...]:
    """The label two component nodes must share to be matchable.

    Always includes the device type; a MOSFET's polarity and a subckt instance's definition name
    are part of the device identity, so they are folded in (polarity behind ``match_polarity``).
    Sizing, model strings, and heuristic roles are added only when the matching flags ask for them.
    """
    parts: list[object] = ["comp", comp.device_type.value]
    if isinstance(comp, MosfetNode) and opts.match_polarity:
        parts.append(comp.polarity.value)
    if isinstance(comp, SubcktInstanceNode):
        parts.append(comp.subckt_name or "")
    if opts.match_models:
        # SPICE resolves model cards case-insensitively, so fold case (the polarity/param/supply
        # signatures already normalize) — otherwise `nmos_x` vs `NMOS_X` is a spurious mismatch.
        parts.append((comp.spice_model or "").strip().lower())
    if opts.match_structural_role:
        parts.append(comp.structural_role.value if comp.structural_role else "")
    if opts.match_params:
        parts.append(param_signature(comp.params))
    return tuple(parts)


def net_signature(
    net: NetNode, opts: MatchOptions, io_labels: dict[str, tuple]
) -> tuple[object, ...]:
    """The label two net nodes must share.

    An anchored I/O net carries its port label (so it only maps to the matching port); otherwise the
    net is unlabeled, except that supply rails carry their class when ``match_supply`` is on.
    """
    label = io_labels.get(net.name.lower())
    if label is not None:
        return ("net", "io", *label)
    return ("net", net.supply_type if opts.match_supply else "")


def pin_token(comp: ComponentNode, pin: str, opts: MatchOptions) -> str:
    """The wiring token an edge carries — strict pin name, or a symmetric token for passives."""
    if opts.passive_symmetry and comp.device_type in _SYMMETRIC_PASSIVES:
        return _SYMMETRIC_PIN
    return pin


def signature_graph(
    graph: CircuitGraph, opts: MatchOptions, io_labels: dict[str, tuple]
) -> nx.MultiGraph:
    """Project a :class:`CircuitGraph` to a plain ``MultiGraph`` carrying only match signatures.

    Each node gets a ``sig`` attribute (its match label) and each edge a ``pin`` token; node
    identity is a ``(kind, name)`` tuple so a net and a component that happen to share a name never
    collide. The original graph is not touched. Diode-connected devices keep both pins as distinct
    parallel edges, so their wiring is preserved. When ``match_bulk`` is off, MOS bulk edges are
    dropped so body-net wiring does not constrain the match.
    """
    g = nx.MultiGraph()
    for net in graph.get_nets():
        g.add_node(("net", net.name), sig=net_signature(net, opts, io_labels))
    for comp in graph.get_components():
        cid = ("comp", comp.name)
        g.add_node(cid, sig=component_signature(comp, opts))
        for pin, net_name in graph.connections(comp).items():
            if not opts.match_bulk and comp.device_type is DeviceType.MOS and pin == _BULK_PIN:
                continue
            g.add_edge(cid, ("net", net_name), pin=pin_token(comp, pin, opts))
    return g


def node_match(a: dict, b: dict) -> bool:
    # Component vs net is separated automatically: a net sig starts with "net", a comp sig "comp".
    return a["sig"] == b["sig"]


def edge_match(a: dict, b: dict) -> bool:
    # MultiGraph hands us every parallel edge between the two matched node pairs; the *multiset* of
    # pin tokens must agree (this is what keeps a gate distinct from a drain, etc.).
    return Counter(d["pin"] for d in a.values()) == Counter(d["pin"] for d in b.values())
