"""Typed graph nodes for the circuit graph.

Nodes are plain ``dataclasses`` used directly as NetworkX node keys (hashed by ``name``).
The serialized I/O contract is a separate concern — see ``contract.py``. The node tree is:

    CircuitNode
    ├── NetNode
    └── ComponentNode
        ├── MosfetNode            (DRAIN, GATE, SOURCE, BULK)
        ├── ResistorNode          (P, N)
        ├── CapacitorNode         (P, N)
        ├── InductorNode          (P, N)
        ├── VoltageSourceNode     (P, N)
        ├── CurrentSourceNode     (P, N)
        ├── VccsNode              (P, N, CP, CN — a linear ``G`` element)
        ├── VcvsNode              (P, N, CP, CN — a linear ``E`` element)
        └── SubcktInstanceNode    (open, named SubcktPort set — Phase 2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .edges import Pin, PinTypeControlledSource, PinTypeMOSFET, PinTypeTwoTerminal, SubcktPort

if TYPE_CHECKING:
    import networkx as nx


# ------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------
class StructuralRole(str, Enum):
    """Structural role assigned to a component from its connectivity/function in the topology."""

    MOS_DIFFERENTIAL_PAIR = "differential_pair"
    MOS_CURRENT_MIRROR = "current_mirror"
    MOS_CURRENT_MIRROR_REFERENCE = "current_mirror_reference"
    MOS_CASCODE_DEVICE = "cascode_device"
    MOS_TAIL_CURRENT_SOURCE = "tail_current_source"
    MOS_PSEUDO_RESISTOR = "pseudo_resistor"
    MOS_ANALOG_SWITCH = "analog_switch"

    ENABLE_DEVICE = "enable_device"
    BIAS_DEVICE = "bias_device"
    LOAD_DEVICE = "load_device"

    DECOUPLING_CAPACITOR = "decoupling_capacitor"
    COMPENSATION_CAPACITOR = "compensation_capacitor"

    COMPENSATION_RESISTOR = "compensation_resistor"
    DEGENERATION_RESISTOR = "degeneration_resistor"
    PASSIVE_LOAD = "passive_load"

    UNKNOWN = "unknown"


#: Per-device roles that :func:`spicexplorer_circuitgraph.match.annotate_subcircuits` assigns
#: **deterministically** from connectivity alone (see ``match._assign_roles``). A consumer layered on
#: top — e.g. the LLM topology-annotation agent — must treat these as *ground truth*: never re-derive
#: them, never override them.
DETERMINISTIC_ROLES: frozenset[StructuralRole] = frozenset(
    {
        StructuralRole.MOS_DIFFERENTIAL_PAIR,
        StructuralRole.MOS_CURRENT_MIRROR,
        StructuralRole.MOS_CURRENT_MIRROR_REFERENCE,
        StructuralRole.MOS_CASCODE_DEVICE,
        StructuralRole.MOS_TAIL_CURRENT_SOURCE,
        StructuralRole.MOS_PSEUDO_RESISTOR,
        StructuralRole.MOS_ANALOG_SWITCH,
    }
)

#: Semantic / intent roles no deterministic detector produces — only an LLM (or a future heuristic)
#: can assign them, and only to a device the matcher left unclassified. ``UNKNOWN`` is the
#: "could not determine" sentinel and is in neither partition.
RESIDUE_ROLES: frozenset[StructuralRole] = (
    frozenset(StructuralRole) - DETERMINISTIC_ROLES - {StructuralRole.UNKNOWN}
)


class SubCircuitElectricalRole(str, Enum):
    """Role of a *group* of components that together perform a function — the network tier above the
    per-device :class:`StructuralRole`. Not written by the deterministic matcher; assigned by the LLM
    annotation agent's functional-network step (each network also records *what it acts on*)."""

    CURRENT_SOURCE = "current_source"
    CURRENT_SINK = "current_sink"

    VOLTAGE_AMPLIFIER = "voltage_amplifier"
    CURRENT_AMPLIFIER = "current_amplifier"
    TRANSCONDUCTANCE_AMPLIFIER = "transconductance_amplifier"

    COMPENSATION_NETWORK = "compensation_network"
    DEGENERATION_NETWORK = "degeneration_network"
    BIAS_NETWORK = "bias_network"
    ENABLE_NETWORK = "enable_network"

    LEVEL_SHIFTER = "level_shifter"
    SWITCH = "switch"
    BYPASS = "bypass"

    UNKNOWN = "unknown"


class CircuitStageRole(str, Enum):
    """High-level, circuit-type-specific role a *functional block or network* plays in the overall
    topology — the architecture tier above :class:`StructuralRole` (per-device) and
    :class:`SubCircuitElectricalRole` (per-network). Assigned by the LLM annotation agent's
    architecture step from the detected blocks + functional networks; not produced by the
    deterministic matcher. The vocabulary is amplifier-centric but open — ``OTHER`` is the escape for
    other circuit classes, and the consumer's schema carries a free-form ``label`` for the refinement
    (e.g. ``"second gain stage"``)."""

    GAIN_STAGE = "gain_stage"
    INPUT_BUFFER = "input_buffer"
    OUTPUT_BUFFER = "output_buffer"
    COMPENSATION = "compensation"
    BIAS = "bias"
    REFERENCE = "reference"
    LOAD = "load"
    OTHER = "other"


class ParameterType(str, Enum):
    LENGTH = "length"
    WIDTH = "width"
    RESISTANCE = "resistance"
    CAPACITANCE = "capacitance"
    MULTIPLIER = "multiplier"
    FINGERS = "fingers"
    OTHER = "other"


class DeviceType(str, Enum):
    MOS = "MOS"
    RES = "RES"
    CAP = "CAP"
    IND = "IND"
    VSOURCE = "VSOURCE"
    ISOURCE = "ISOURCE"
    VCCS = "VCCS"  # voltage-controlled current source (G element)
    VCVS = "VCVS"  # voltage-controlled voltage source (E element)
    SUBCKT = "SUBCKT"  # produced for generic X… subcircuit instances (SubcktInstanceNode)
    UNKNOWN = "UNKNOWN"


class MosPolarityType(str, Enum):
    NMOS = "NMOS"
    PMOS = "PMOS"
    UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------------------
# Base node
# ------------------------------------------------------------------------
@dataclass(eq=False)
class CircuitNode:
    """Base node — identity is its ``name`` (so one instance per name in a graph)."""

    name: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name


# ------------------------------------------------------------------------
# Net
# ------------------------------------------------------------------------
@dataclass(eq=False)
class NetNode(CircuitNode):
    is_supply: bool = False
    supply_type: str = ""  # "VDD", "VSS", "GND", … (set by supply detection)


@dataclass
class TransistorOperatingPoint:
    """Small-signal/operating-point values — populated only when a sim has been run."""

    gm: float | None = None
    gds: float | None = None
    id: float | None = None
    region: str | None = None
    annotation: str | None = None


# ------------------------------------------------------------------------
# Component base
# ------------------------------------------------------------------------
@dataclass(eq=False)
class ComponentNode(CircuitNode):
    device_type: DeviceType
    _PIN_ORDER: tuple[Pin, ...]  # closed-enum pins (primitives) or open SubcktPorts (subckt)
    params: dict[str, str | float] = field(default_factory=dict)
    spice_model: str | None = None

    structural_role: StructuralRole | None = None
    subcircuit_electrical_role: SubCircuitElectricalRole | None = None


# ------------------------------------------------------------------------
# MOSFET
# ------------------------------------------------------------------------
@dataclass(eq=False)
class MosfetNode(ComponentNode):
    _PIN_ORDER: tuple[PinTypeMOSFET, ...] = (
        PinTypeMOSFET.DRAIN,
        PinTypeMOSFET.GATE,
        PinTypeMOSFET.SOURCE,
        PinTypeMOSFET.BULK,
    )
    polarity: MosPolarityType = MosPolarityType.UNKNOWN
    operating_point: TransistorOperatingPoint | None = None

    def _terminal_nets(self, graph: "nx.MultiGraph") -> dict[PinTypeMOSFET, NetNode]:
        """DRAIN/GATE/SOURCE/BULK → connected net, read from the live edges (keyed by the pin enum)."""
        nets: dict[PinTypeMOSFET, NetNode] = {}
        for _, net, _key, data in graph.edges(self, data=True, keys=True):
            pin = data.get("pin")
            if pin is not None:
                nets[pin] = net
        return nets

    def _terminals_share_net(
        self, graph: "nx.MultiGraph", a: PinTypeMOSFET, b: PinTypeMOSFET
    ) -> bool:
        nets = self._terminal_nets(graph)
        na, nb = nets.get(a), nets.get(b)
        return na is not None and nb is not None and na.name == nb.name

    def is_diode_connected(self, graph: "nx.MultiGraph") -> bool:
        """True when DRAIN and GATE share a net (a diode-connected device — always in saturation)."""
        return self._terminals_share_net(graph, PinTypeMOSFET.DRAIN, PinTypeMOSFET.GATE)

    def is_gate_source_shorted(self, graph: "nx.MultiGraph") -> bool:
        """True when GATE and SOURCE share a net — Vgs = 0, so an *enhancement* device is off
        (a depletion / negative-Vth device may still conduct)."""
        return self._terminals_share_net(graph, PinTypeMOSFET.GATE, PinTypeMOSFET.SOURCE)

    def is_drain_source_shorted(self, graph: "nx.MultiGraph") -> bool:
        """True when DRAIN and SOURCE share a net — the channel is shorted, so the transistor is
        *killed* (e.g. a MOS device wired as a decoupling capacitor)."""
        return self._terminals_share_net(graph, PinTypeMOSFET.DRAIN, PinTypeMOSFET.SOURCE)


# ------------------------------------------------------------------------
# Two-terminal passives + sources (P, N)
# ------------------------------------------------------------------------
_TWO_TERMINAL: tuple[PinTypeTwoTerminal, ...] = (PinTypeTwoTerminal.P, PinTypeTwoTerminal.N)


@dataclass(eq=False)
class ResistorNode(ComponentNode):
    _PIN_ORDER: tuple[PinTypeTwoTerminal, ...] = _TWO_TERMINAL


@dataclass(eq=False)
class CapacitorNode(ComponentNode):
    _PIN_ORDER: tuple[PinTypeTwoTerminal, ...] = _TWO_TERMINAL


@dataclass(eq=False)
class InductorNode(ComponentNode):
    _PIN_ORDER: tuple[PinTypeTwoTerminal, ...] = _TWO_TERMINAL


@dataclass(eq=False)
class VoltageSourceNode(ComponentNode):
    _PIN_ORDER: tuple[PinTypeTwoTerminal, ...] = _TWO_TERMINAL


@dataclass(eq=False)
class CurrentSourceNode(ComponentNode):
    _PIN_ORDER: tuple[PinTypeTwoTerminal, ...] = _TWO_TERMINAL


# ------------------------------------------------------------------------
# Linear controlled sources (P, N output pair + CP, CN controlling pair)
# ------------------------------------------------------------------------
_CONTROLLED_SOURCE: tuple[PinTypeControlledSource, ...] = (
    PinTypeControlledSource.P,
    PinTypeControlledSource.N,
    PinTypeControlledSource.CP,
    PinTypeControlledSource.CN,
)


@dataclass(eq=False)
class VccsNode(ComponentNode):
    """A linear voltage-controlled current source (``G`` element). The transconductance rides in
    ``params["Value"]`` verbatim — it may be a bare symbol (``GM``), an eng string, or ``{expr}``."""

    _PIN_ORDER: tuple[PinTypeControlledSource, ...] = _CONTROLLED_SOURCE


@dataclass(eq=False)
class VcvsNode(ComponentNode):
    """A linear voltage-controlled voltage source (``E`` element). The gain rides in
    ``params["Value"]`` verbatim, like :class:`VccsNode`."""

    _PIN_ORDER: tuple[PinTypeControlledSource, ...] = _CONTROLLED_SOURCE


# ------------------------------------------------------------------------
# Subcircuit instance (open, named port set — Phase 2)
# ------------------------------------------------------------------------
@dataclass(eq=False)
class SubcktInstanceNode(ComponentNode):
    """A subcircuit *instance* modeled as a single component with an open, named port set.

    Unlike the primitives, ``_PIN_ORDER`` is **per-instance** (built from the ``.SUBCKT`` header
    ports when resolvable, else positional ``"1"``…``"N"``) and holds :class:`SubcktPort`s whose
    roles are filled in after the graph is built. ``subckt_name`` is the referenced definition.
    """

    subckt_name: str | None = None

    def ports(self) -> tuple[SubcktPort, ...]:
        """The instance's ports (each a :class:`SubcktPort` carrying a name + role)."""
        return tuple(p for p in self._PIN_ORDER if isinstance(p, SubcktPort))
