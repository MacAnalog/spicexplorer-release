"""Pin and edge types for the circuit graph.

A pin comes in two flavors:

* **closed enums** for SPICE primitives — a MOSFET always has DRAIN/GATE/SOURCE/BULK; a
  two-terminal device has P/N; and
* an **open, dynamic** :class:`SubcktPort` for subcircuit *instances*, whose port set is
  arbitrary (named from the ``.SUBCKT`` header) and whose terminals are semantically
  heterogeneous (power / ground / input / output / bias / …) — something SPICE does not declare,
  so the role is carried separately and populated by deterministic heuristics.

Both flavors expose ``.value`` (the pin/port name), so the graph keys edges and serializes
uniformly across them. The union is :data:`Pin`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PinTypeBase(str, Enum):
    """Base for the closed pin enums. ``str`` mixin so members serialize as their value."""


class PinTypeMOSFET(PinTypeBase):
    DRAIN = "DRAIN"
    GATE = "GATE"
    SOURCE = "SOURCE"
    BULK = "BULK"


class PinTypeTwoTerminal(PinTypeBase):
    """Resistors, capacitors, inductors, and V/I sources (positive/negative terminal)."""

    P = "P"
    N = "N"


class PinTypeControlledSource(PinTypeBase):
    """Linear controlled sources (VCCS ``G`` / VCVS ``E``): output pair + controlling pair,
    in SPICE card order ``G1 n+ n- nc+ nc- value``."""

    P = "P"  # output +
    N = "N"  # output -
    CP = "CP"  # controlling +
    CN = "CN"  # controlling -


class SubcktPortRole(str, Enum):
    """Semantic role of a subcircuit port. Populated deterministically when known, else UNKNOWN."""

    POWER = "power"
    GROUND = "ground"
    INPUT = "input"
    OUTPUT = "output"
    BIAS = "bias"
    SIGNAL = "signal"
    UNKNOWN = "unknown"


@dataclass(eq=False)
class SubcktPort:
    """One port of a subcircuit instance (open port set).

    ``name`` is the formal ``.SUBCKT``-header port name when resolvable, else a positional
    fallback (``"1"``, ``"2"``, …). ``role`` is mutable: it is assigned after the graph is built
    (from a port-spec registry or supply-net inference). Identity is per-instance (``eq=False``),
    so two ports that happen to share a name/role are still distinct objects.
    """

    name: str
    role: SubcktPortRole = SubcktPortRole.UNKNOWN

    @property
    def value(self) -> str:
        """The port name — parity with ``PinTypeBase.value`` so edges key/serialize uniformly."""
        return self.name


# A pin is either a closed-enum primitive pin or an open subcircuit port.
Pin = PinTypeBase | SubcktPort


class EdgeType(str, Enum):
    ELECTRICAL = "electrical"
    FUNCTIONAL = "functional"
