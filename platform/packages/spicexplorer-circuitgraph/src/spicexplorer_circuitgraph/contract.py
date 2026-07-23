"""Typed I/O contract for the circuit-graph tool.

This module is the **single source** for the tool's serialized shapes — it feeds OpenAPI ->
TS codegen and MCP schemas later, so the graph builder, serialization strategies, and the
REST/MCP adapters all agree on the same pydantic models rather than ad-hoc dicts. (Named
``contract`` to avoid confusion with the ``model/`` subpackage, which holds the *graph* model.)

:class:`CircuitGraphDoc` is the round-trippable form: ``from_graph`` serializes a
:class:`~spicexplorer_circuitgraph.graph.CircuitGraph` and ``to_graph`` reconstructs an
equivalent graph (closing the prototype's one-way-only gap).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .graph import CircuitGraph
from .model.edges import SubcktPort, SubcktPortRole
from .model.nodes import (
    CapacitorNode,
    ComponentNode,
    CurrentSourceNode,
    DeviceType,
    InductorNode,
    MosfetNode,
    MosPolarityType,
    NetNode,
    ResistorNode,
    StructuralRole,
    SubCircuitElectricalRole,
    SubcktInstanceNode,
    VccsNode,
    VcvsNode,
    VoltageSourceNode,
)

__all__ = ["CircuitGraphMeta", "NetModel", "PortModel", "ComponentModel", "CircuitGraphDoc"]


class CircuitGraphMeta(BaseModel):
    """Header common to every serialized circuit graph."""

    circuit_name: str = Field("", description="Name of the (sub)circuit this graph represents.")
    component_count: int = Field(0, ge=0, description="Number of component nodes.")
    net_count: int = Field(0, ge=0, description="Number of net nodes.")


class NetModel(BaseModel):
    """A net (node) and its supply classification."""

    name: str
    is_supply: bool = False
    supply_type: str = ""


class PortModel(BaseModel):
    """A subcircuit-instance port: its name and (deterministically assigned) semantic role."""

    name: str
    role: SubcktPortRole = SubcktPortRole.UNKNOWN


class ComponentModel(BaseModel):
    """A component, its typed metadata, and its pin → net connections."""

    id: str
    device_type: DeviceType
    polarity: MosPolarityType | None = None  # MOS only
    spice_model: str | None = None
    subckt_name: str | None = None  # subckt instances only
    ports: list[PortModel] | None = None  # subckt instances only (names + roles, in port order)
    connections: dict[str, str] = Field(default_factory=dict, description="pin name -> net name")
    params: dict[str, str | float] = Field(default_factory=dict)
    structural_role: StructuralRole | None = None
    subcircuit_electrical_role: SubCircuitElectricalRole | None = None


# device_type -> the concrete node class to rebuild on deserialize
_NODE_BY_DEVICE_TYPE: dict[DeviceType, type[ComponentNode]] = {
    DeviceType.MOS: MosfetNode,
    DeviceType.RES: ResistorNode,
    DeviceType.CAP: CapacitorNode,
    DeviceType.IND: InductorNode,
    DeviceType.VSOURCE: VoltageSourceNode,
    DeviceType.ISOURCE: CurrentSourceNode,
    DeviceType.VCCS: VccsNode,
    DeviceType.VCVS: VcvsNode,
}


def _model_to_node(cm: ComponentModel) -> ComponentNode:
    if cm.device_type is DeviceType.SUBCKT:
        return SubcktInstanceNode(
            name=cm.id,
            device_type=DeviceType.SUBCKT,
            _PIN_ORDER=tuple(SubcktPort(p.name, p.role) for p in (cm.ports or [])),
            subckt_name=cm.subckt_name,
            spice_model=cm.spice_model,
            params=dict(cm.params),
            structural_role=cm.structural_role,
            subcircuit_electrical_role=cm.subcircuit_electrical_role,
        )
    cls = _NODE_BY_DEVICE_TYPE.get(cm.device_type)
    if cls is None:
        raise ValueError(
            f"cannot deserialize device_type {cm.device_type} for {cm.id!r} "
            f"(supported: MOS/RES/CAP/IND/VSOURCE/ISOURCE/VCCS/VCVS/SUBCKT)"
        )
    kwargs: dict[str, Any] = {
        "name": cm.id,
        "device_type": cm.device_type,
        "params": dict(cm.params),
        "spice_model": cm.spice_model,
        "structural_role": cm.structural_role,
        "subcircuit_electrical_role": cm.subcircuit_electrical_role,
    }
    if cls is MosfetNode:
        kwargs["polarity"] = cm.polarity or MosPolarityType.UNKNOWN
    return cls(**kwargs)


class CircuitGraphDoc(BaseModel):
    """The full, round-trippable serialized graph."""

    meta: CircuitGraphMeta
    nets: list[NetModel] = Field(default_factory=list)
    components: list[ComponentModel] = Field(default_factory=list)

    @classmethod
    def from_graph(cls, graph: CircuitGraph) -> "CircuitGraphDoc":
        """Serialize a live :class:`CircuitGraph` into the contract (deterministic ordering)."""
        nets = [
            NetModel(name=n.name, is_supply=n.is_supply, supply_type=n.supply_type)
            for n in graph.get_nets(sort=True)
        ]
        components = [
            ComponentModel(
                id=comp.name,
                device_type=comp.device_type,
                polarity=comp.polarity if isinstance(comp, MosfetNode) else None,
                spice_model=comp.spice_model,
                subckt_name=comp.subckt_name if isinstance(comp, SubcktInstanceNode) else None,
                ports=(
                    [PortModel(name=p.name, role=p.role) for p in comp.ports()]
                    if isinstance(comp, SubcktInstanceNode)
                    else None
                ),
                connections=graph.connections(comp),
                params=dict(comp.params),
                structural_role=comp.structural_role,
                subcircuit_electrical_role=comp.subcircuit_electrical_role,
            )
            for comp in graph.get_components(sort=True)
        ]
        return cls(
            meta=CircuitGraphMeta(
                circuit_name=graph.name,
                component_count=graph.component_count,
                net_count=graph.net_count,
            ),
            nets=nets,
            components=components,
        )

    def to_graph(self) -> CircuitGraph:
        """Reconstruct an equivalent :class:`CircuitGraph` from the contract."""
        graph = CircuitGraph(self.meta.circuit_name)
        net_by_name = {
            nm.name: graph.add_net(
                NetNode(name=nm.name, is_supply=nm.is_supply, supply_type=nm.supply_type)
            )
            for nm in self.nets
        }
        comp_by_id: dict[str, ComponentNode] = {}
        for cm in self.components:
            comp_by_id[cm.id] = graph.add_component(_model_to_node(cm))

        for cm in self.components:
            node = comp_by_id[cm.id]
            pin_by_value = {pin.value: pin for pin in node._PIN_ORDER}
            for pin_str, net_name in cm.connections.items():
                pin = pin_by_value.get(pin_str)
                if pin is None:
                    raise ValueError(
                        f"{cm.id!r}: pin {pin_str!r} not valid for {type(node).__name__}"
                    )
                net = net_by_name.get(net_name)
                if net is None:
                    raise ValueError(f"{cm.id!r}: connection to unknown net {net_name!r}")
                graph.connect(node, net, pin)
        return graph
