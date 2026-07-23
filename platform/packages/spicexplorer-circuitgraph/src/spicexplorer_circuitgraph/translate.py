"""Whole-deck cross-dialect translation (ngspice/SPICE source → Spectre blocks).

Turns a SPICE testbench deck (top-level stimulus +
subckt DUT definitions) into Spectre text blocks via the graph + dialect emitters,
handling the semantics the per-line emitters cannot know:

- **device-model retargeting** via a target :class:`~spicexplorer_circuitgraph.pdk.Pdk`
  (e.g. IHP ``sg13_lv_nmos`` → a target-kit MOS model);
- **parameter-symbol case-folding** — spicelib canonicalizes ``.param`` names to
  UPPERCASE while device values keep the source's spelling; SPICE is case-insensitive,
  Spectre is case-sensitive, so every parameter symbol is folded to lowercase wherever
  it appears (definitions and references);
- **bare symbolic passive values** (``C1 a b CL``) — the emitter would render the token
  as a model master; they are brace-wrapped so the Spectre emitter renders ``c=cl``;
- **ground aliasing** — ngspice treats ``GND`` as node 0, Spectre does not: matching
  top-level nets get an explicit 0 V tie source to node ``0``;
- **numeric-normalized parameter defaults** — SPICE eng-suffix case is a Spectre
  landmine (``MEG`` vs ``M``: mega in Spectre, milli in SPICE), so defaults are parsed
  to plain floats where possible.

Analyses / control cards / ``.lib`` corners are **not** translated (the directive
invariant): the Spectre deck-side analysis contract (analyses *named* ``dcOp``/``ac`` +
``info what=oppoint`` — PSF result keys are file-name-keyed) belongs to the optimizer's
``spicexplorer.backends.spectre_deck`` composer, which consumes the blocks returned
here as plain strings.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from spicexplorer_core.eng import parse_value
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_core.spice_engine.netlist_view import NetlistViewLike

from .emit import SpectreEmitter, to_netlist
from .graph import CircuitGraph
from .model.nodes import MosfetNode, SubcktInstanceNode
from .pdk import Pdk, get_pdk

__all__ = ["TranslatedDesign", "translate_ngspice_to_spectre"]

logger = logging.getLogger(__name__)

_SYMBOL = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_BRACE_GROUP = re.compile(r"\{([^{}]*)\}")
_EMITTED_HEADER = ("//", "simulator lang=spectre")


@dataclass(frozen=True)
class TranslatedDesign:
    """Spectre text blocks + normalized parameter defaults for one translated deck.

    Everything is a plain string on purpose: downstream composition (corner includes,
    ``parameters`` injection, analyses) must not need this package.
    """

    subckt_blocks: tuple[str, ...]
    stimulus: str
    parameters: dict[str, float | str] = field(default_factory=dict)
    ground_ties: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def design_text(self) -> str:
        """All structural blocks, composition-ready (subckts, stimulus, ground ties)."""
        parts = [*self.subckt_blocks, self.stimulus, *self.ground_ties]
        return "\n\n".join(p for p in parts if p)


def _resolve_pdk(pdk: Pdk | str | None) -> Pdk | None:
    if pdk is None or isinstance(pdk, Pdk):
        return pdk
    resolved = get_pdk(pdk)
    if resolved is None:
        raise ValueError(f"unknown PDK name {pdk!r} (see spicexplorer_circuitgraph.pdk.PDKS)")
    return resolved


def _body_of(emitted: str) -> str:
    """Strip the per-emission header lines; keep the device/subckt body only."""
    return "\n".join(
        ln
        for ln in emitted.splitlines()
        if ln.strip() and not ln.startswith(_EMITTED_HEADER[0]) and ln.strip() != _EMITTED_HEADER[1]
    )


def _fold_symbols(text: str, param_names: set[str]) -> str:
    """Lowercase every token that is a known parameter symbol (case-insensitively)."""
    return _SYMBOL.sub(
        lambda m: m.group(0).lower() if m.group(0).lower() in param_names else m.group(0),
        text,
    )


def _normalize_graph_values(graph: CircuitGraph, param_names: set[str]) -> None:
    """Case-fold parameter references in component params; brace-wrap bare symbolic
    passive/source values so the Spectre emitter treats them as expressions."""
    for comp in graph.get_components(sort=True):
        model_valued = isinstance(comp, (MosfetNode, SubcktInstanceNode))
        for key, val in list(comp.params.items()):
            if not isinstance(val, str):
                continue
            if key == "Value" and model_valued:
                continue  # model / subckt master names are not parameter symbols
            raw = val.strip()
            # ngspice QUOTE-expressions ('x_cfb1', 'a*2') are the {…} braces' twin —
            # normalize them to braces so a quoted symbolic passive value renders as a
            # Spectre expression instead of a phantom model master (`CFB1 … 'x_c'` →
            # `capacitor c=x_c`, not master `_x_c_`; found live by the ia_002 CCIA
            # binding).
            if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
                raw = "{" + raw[1:-1].strip() + "}"
            folded = _fold_symbols(raw, param_names)
            if key == "Value" and folded.lower() in param_names and not folded.startswith("{"):
                folded = "{" + folded.lower() + "}"
            comp.params[key] = folded


def _collect_subckt_blocks(
    view: NetlistViewLike,
    graph: CircuitGraph,
    *,
    source_pdk: Pdk | None,
    target_pdk: Pdk | None,
    param_names: set[str],
    seen: dict[str, str],
    warnings: list[str],
) -> None:
    """DFS over subckt instances: emit one Spectre ``subckt … ends`` block per unique
    definition (dedup by master name across the whole tree)."""
    for comp in graph.get_components(sort=True):
        if not isinstance(comp, SubcktInstanceNode):
            continue
        master = comp.subckt_name or ""
        if not master or master in seen:
            continue
        ports = view.get_subcircuit_ports(comp.name)
        if ports is None:
            warnings.append(
                f"{comp.name}: subcircuit {master!r} has no visible definition "
                f"(black box) — instance emitted, definition skipped"
            )
            seen[master] = ""
            continue
        sub_view = view.get_subcircuit(comp.name)
        sub_graph = CircuitGraph.from_netlist(sub_view, name=master, pdk=source_pdk)
        _normalize_graph_values(sub_graph, param_names)
        seen[master] = ""  # reserve before recursion (cycles / self-instantiation)
        _collect_subckt_blocks(
            sub_view,
            sub_graph,
            source_pdk=source_pdk,
            target_pdk=target_pdk,
            param_names=param_names,
            seen=seen,
            warnings=warnings,
        )
        seen[master] = _body_of(
            to_netlist(sub_graph, dialect="spectre", pdk=target_pdk, subckt=master, ports=ports)
        )


def translate_ngspice_to_spectre(
    netlist: str | Path,
    *,
    pdk: Pdk | str | None = None,
    source_pdk: Pdk | str | None = None,
    ground_nets: Sequence[str] = ("GND",),
) -> TranslatedDesign:
    """Translate a SPICE/ngspice deck into Spectre structural blocks.

    ``pdk`` is the **target** device table (``model_for`` retargeting, e.g.
    ``"FOUNDRY-n65"``); ``source_pdk`` aids device classification of the source deck
    (X-prefixed MOS like IHP's ``XM1 … sg13_lv_nmos``). Returns
    :class:`TranslatedDesign`; analyses/corners are intentionally absent — compose
    them downstream.
    """
    target = _resolve_pdk(pdk)
    source = _resolve_pdk(source_pdk)
    view = NetlistView.from_file(netlist)

    deck_params = view.get_parameters()
    param_names = {k.lower() for k in deck_params}
    warnings: list[str] = []

    top_graph = CircuitGraph.from_netlist(view, name=Path(str(netlist)).stem, pdk=source)
    _normalize_graph_values(top_graph, param_names)

    seen: dict[str, str] = {}
    _collect_subckt_blocks(
        view,
        top_graph,
        source_pdk=source,
        target_pdk=target,
        param_names=param_names,
        seen=seen,
        warnings=warnings,
    )
    stimulus = _body_of(to_netlist(top_graph, dialect="spectre", pdk=target))

    # ngspice aliases GND-ish nets to node 0; Spectre needs the tie to be explicit.
    ground_lower = {g.lower() for g in ground_nets}
    ties = tuple(
        f"V_tie_{SpectreEmitter.sanitize_ref(net)} ({SpectreEmitter.sanitize_net(net)} 0) "
        f"vsource dc=0"
        for net in view.get_all_nodes()
        if net.lower() in ground_lower and net != "0"
    )

    parameters: dict[str, float | str] = {}
    for name, raw in deck_params.items():
        try:
            parameters[name.lower()] = float(parse_value(raw))
        except (ValueError, TypeError):
            # SPICE tie/ratio exprs arrive brace-wrapped (`{x_a}`, `{x_b*17/3}`); Spectre's
            # `parameters` statement REJECTS braces but accepts the parenthesized
            # expression (SFE-874). Converting — rather than resolving to a number —
            # keeps the tie LIVE: injecting the free symbol per candidate still moves
            # the tied one in the rendered deck.
            expr = _BRACE_GROUP.sub(
                lambda m: "(" + m.group(1).strip() + ")",
                _fold_symbols(str(raw).strip(), param_names),
            )
            parameters[name.lower()] = expr
            warnings.append(f"parameter {name.lower()}={raw!r} is non-numeric; kept symbolic")

    directives = getattr(view, "directives", ())
    if directives:
        kinds = sorted({d.kind for d in directives})
        warnings.append(
            f"{len(directives)} source directive(s) not translated ({', '.join(kinds)}) — "
            f"compose analyses/corners via spicexplorer.backends.spectre_deck"
        )
    for w in warnings:
        logger.warning("translate: %s", w)

    return TranslatedDesign(
        subckt_blocks=tuple(block for block in seen.values() if block),
        stimulus=stimulus,
        parameters=parameters,
        ground_ties=ties,
        warnings=tuple(warnings),
    )
