"""Per-node render helpers shared by the serialization strategies.

Free functions that depend only on a :class:`ComponentNode` (not the graph), extracted from the
old ``CircuitGraph._add_*`` methods so the strategies can compose the same fields uniformly.
"""

from __future__ import annotations

from typing import Any

from ..model.edges import SubcktPortRole
from ..model.nodes import ComponentNode, MosfetNode, MosPolarityType, SubcktInstanceNode


def component_type_str(comp: ComponentNode) -> str:
    """Human/LLM-facing type label, e.g. ``"Nmos_Mosfet"``, ``"Resistor"``, ``"SubcktInstance"``."""
    label = type(comp).__name__.replace("Node", "")  # "MosfetNode" -> "Mosfet"
    if isinstance(comp, MosfetNode) and comp.polarity is not MosPolarityType.UNKNOWN:
        label = f"{comp.polarity.value.capitalize()}_{label}"  # "Nmos_Mosfet"
    return label


def polarity_str(comp: ComponentNode) -> str | None:
    """MOS polarity as a string (``"Unknown"`` for an untyped MOS); ``None`` for non-MOS."""
    if isinstance(comp, MosfetNode):
        return comp.polarity.value if comp.polarity is not MosPolarityType.UNKNOWN else "Unknown"
    return None


def add_spice_model(comp: ComponentNode, entry: dict[str, Any], *, include: bool = True) -> None:
    """Add the device's SPICE model name — unless ``include`` is False.

    ``include=False`` is the NDA-safe projection: a foundry
    model name (e.g. a kit-specific ``nch``/``pch`` variant) can hint at the process, so a
    serialization for a cloud LLM omits it *by construction* rather than stripping it after."""
    if include and comp.spice_model:
        entry["spice_model"] = comp.spice_model


def add_polarity(comp: ComponentNode, entry: dict[str, Any]) -> None:
    pol = polarity_str(comp)
    if pol is not None:
        entry["polarity"] = pol


def add_mosfet_roles(comp: ComponentNode, entry: dict[str, Any]) -> None:
    if isinstance(comp, MosfetNode):
        if comp.structural_role:
            entry["structural_role"] = comp.structural_role.value
        if comp.subcircuit_electrical_role:
            entry["subcircuit_electrical_role"] = comp.subcircuit_electrical_role.value


def add_subckt_info(comp: ComponentNode, entry: dict[str, Any], *, include_model: bool = True) -> None:
    if not isinstance(comp, SubcktInstanceNode):
        return
    # The subckt MASTER name is a foundry-identifying token in the same class as spice_model:
    # a foundry device is commonly modeled as a subckt instance (e.g. sky130_fd_pr__nfet_01v8),
    # so the NDA-safe projection (include_model=False) omits it by construction. Neutral
    # port_roles (input/output/power/…) are always kept — they carry no foundry identity.
    if include_model and comp.subckt_name:
        entry["subckt_name"] = comp.subckt_name
    roles = {
        port.name: port.role.value
        for port in comp.ports()
        if port.role is not SubcktPortRole.UNKNOWN
    }
    if roles:
        entry["port_roles"] = roles


def add_params(comp: ComponentNode, entry: dict[str, Any]) -> None:
    if comp.params:
        entry["params"] = comp.params
