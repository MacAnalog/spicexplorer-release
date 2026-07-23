"""The built-in serialization strategies (the seven views, now pluggable).

Each is a registered :class:`Serializer` built purely from the graph's public API
(``get_components`` / ``get_nets`` / ``connections`` / ``name`` / counts) plus the per-node helpers
in ``_nodes`` — so every strategy renders primitives *and* subckt-instance components uniformly.
Add a new strategy by writing one more ``@register`` class here (or in any imported module).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import _nodes
from .base import Serializer, register

if TYPE_CHECKING:
    from ..graph import CircuitGraph


@register
class FlatJson(Serializer):
    """Flat, token-efficient: components are top-level keys, pins inlined."""

    name = "flat"
    kind = "json"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for comp in graph.get_components(sort=True):
            # Connections inlined as top-level keys; the fixed contract keys (type, spice_model,
            # subckt_name, port_roles, …) are written AFTER, so an arbitrarily-named subckt port
            # can never overwrite a documented schema field.
            entry: dict[str, Any] = dict(graph.connections(comp, include_body=include_body))
            entry["type"] = _nodes.component_type_str(comp)
            _nodes.add_spice_model(comp, entry, include=include_spice_model)
            _nodes.add_subckt_info(comp, entry, include_model=include_spice_model)
            _nodes.add_mosfet_roles(comp, entry)
            if include_params:
                _nodes.add_params(comp, entry)
            result[comp.name] = entry
        return result


@register
class NestedJson(Serializer):
    """Nested: a components list under circuit metadata (good for schema validation/tool-calling)."""

    name = "nested"
    kind = "json"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,
    ) -> dict[str, Any]:
        components: list[dict[str, Any]] = []
        for comp in graph.get_components(sort=True):
            entry: dict[str, Any] = {"id": comp.name, "type": _nodes.component_type_str(comp)}
            _nodes.add_polarity(comp, entry)
            _nodes.add_spice_model(comp, entry, include=include_spice_model)
            _nodes.add_subckt_info(comp, entry, include_model=include_spice_model)
            entry["connections"] = graph.connections(comp, include_body=include_body)
            _nodes.add_mosfet_roles(comp, entry)
            if include_params:
                _nodes.add_params(comp, entry)
            components.append(entry)
        return {
            "circuit_name": graph.name,
            "graph_description": graph.graph_description,
            "components": components,
        }


@register
class NetCentricJson(Serializer):
    """Net-centric: nets are top-level keys → the components/pins on them (inverts connections)."""

    name = "net_centric"
    kind = "json"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, list[dict[str, Any]]] = {n.name: [] for n in graph.get_nets(sort=True)}
        for comp in graph.get_components(sort=True):
            cmeta: dict[str, Any] = {"type": _nodes.component_type_str(comp)}
            _nodes.add_polarity(comp, cmeta)
            _nodes.add_spice_model(comp, cmeta, include=include_spice_model)
            if include_params:
                _nodes.add_params(comp, cmeta)
            for pin_name, net_name in graph.connections(comp, include_body=include_body).items():
                result[net_name].append({"component": comp.name, "pin": pin_name, **cmeta})
        return result


@register
class LlmDescription(Serializer):
    """Plain-text, component-centric description."""

    name = "llm_description"
    kind = "text"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,  # noqa: ARG002 — this view never shows the model
    ) -> str:
        lines = ["Circuit Topology Description:"]
        for comp in graph.get_components(sort=True):
            ctype = _nodes.component_type_str(comp)
            if include_params:
                lines.append(f"- {comp.name} is a {ctype} (Params: {comp.params}). Connections:")
            else:
                lines.append(f"- {comp.name} is a {ctype}. Connections:")
            for pin, net_name in graph.connections(comp, include_body=include_body).items():
                lines.append(f"  * Pin {pin} connects to {net_name}")
        return "\n".join(lines)


@register
class RoleDetection(Serializer):
    """Role-focused text: transistor polarity/roles + connectivity context."""

    name = "role_detection"
    kind = "text"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,
    ) -> str:
        lines = ["Role-Oriented Circuit Description:"]
        for comp in graph.get_components(sort=True):
            ctype = _nodes.component_type_str(comp)
            header = f"- {comp.name} ({comp.spice_model})" if include_spice_model else f"- {comp.name}"
            pol = _nodes.polarity_str(comp)
            if pol is not None:  # MOS only
                header += f" | polarity={pol}"
                if comp.structural_role:
                    header += f" | structural_role={comp.structural_role.value}"
                if comp.subcircuit_electrical_role:
                    header += f" | subcircuit_electrical_role={comp.subcircuit_electrical_role.value}"
            lines.append(header)
            for pin, net_name in sorted(graph.connections(comp, include_body=include_body).items()):
                lines.append(f"    {pin} → {net_name}")
            if ctype in {"Resistor", "Capacitor", "Inductor"} and comp.params:
                lines.append(f"    params: {comp.params}")
            lines.append("")
        return "\n".join(lines)


@register
class TopologyViews(Serializer):
    """Combined component-to-net and net-to-component adjacency lists."""

    name = "topology"
    kind = "text"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,
    ) -> str:
        sections = self._component_to_net(graph, include_body, include_spice_model)
        sections.append("")
        sections.extend(self._net_to_component(graph, include_body))
        return "\n".join(sections)

    @staticmethod
    def _component_to_net(
        graph: CircuitGraph, include_body: bool, include_spice_model: bool = True
    ) -> list[str]:
        lines = ["Component-to-Net Adjacency:"]
        for comp in graph.get_components(sort=True):
            conns = graph.connections(comp, include_body=include_body)
            pins = ", ".join(f"{pin}={net}" for pin, net in sorted(conns.items()))
            model = f" ({comp.spice_model})" if include_spice_model else ""
            lines.append(
                f"- {_nodes.component_type_str(comp)} {comp.name}{model}: {pins}"
            )
        return lines

    @staticmethod
    def _net_to_component(graph: CircuitGraph, include_body: bool) -> list[str]:
        lines = ["Net-to-Component Adjacency:"]
        net_to: dict[str, list[str]] = {n.name: [] for n in graph.get_nets(sort=True)}
        for comp in graph.get_components(sort=True):
            for pin_name, net_name in graph.connections(comp, include_body=include_body).items():
                net_to[net_name].append(f"{comp.name}.{pin_name}")
        for net in graph.get_nets(sort=True):
            entries = net_to[net.name]
            if entries:
                lines.append(f"- {net.name}: {', '.join(sorted(entries))}")
            else:
                lines.append(f"- {net.name}: (no connected components)")
        return lines


@register
class StructuralRoleSummary(Serializer):
    """One line per component: ``name → structural_role`` (``NA`` until annotated)."""

    name = "structural_role_summary"
    kind = "text"

    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,  # noqa: ARG002 — role summary shows no model
    ) -> str:
        out = "Structural Role Summary:\n"
        for comp in graph.get_components(sort=True):
            role = comp.structural_role.value if comp.structural_role else "NA"
            out += f"{comp.name} → {role}\n"
        return out
