"""Port-spec registry: per-subcircuit declarations of port semantic roles.

SPICE does not declare port *types*, so when we know a subcircuit's port semantics we record them
here, keyed by subckt name -> {port_name: role}. The build consults this first, then falls back to
supply-net connectivity inference, then leaves the role UNKNOWN.

Seeded for the IHP example DUTs whose ports are resolvable (hyphen-free names — spicelib truncates
hyphenated ``.subckt`` names, so those DUTs get positional ports and only supply-inferred roles
until the fixture-curation normalization lands).
"""

from __future__ import annotations

from .model.edges import SubcktPortRole

PortSpec = dict[str, SubcktPortRole]

PORT_SPEC_REGISTRY: dict[str, PortSpec] = {
    # folded-cascode DUT: `.subckt opamp vin- vin+ vout vdd ib vss`
    "opamp": {
        "vin+": SubcktPortRole.INPUT,
        "vin-": SubcktPortRole.INPUT,
        "vout": SubcktPortRole.OUTPUT,
        "vdd": SubcktPortRole.POWER,
        "vss": SubcktPortRole.GROUND,
        "ib": SubcktPortRole.BIAS,
    },
}


def get_port_spec(subckt_name: str | None) -> PortSpec:
    """The declared port roles for a subckt name (empty mapping if none registered)."""
    return PORT_SPEC_REGISTRY.get(subckt_name or "", {})
