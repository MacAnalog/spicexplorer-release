"""The netlist2tf private typed IR (model/) — separate from the wire contract (contract.py, P4).

Mirrors circuitgraph's ``model/`` vs ``contract.py`` split. These types are internal; the
serializable Pydantic contract is a distinct concern.
"""

from .ir import (
    GROUND_NAMES,
    Circuit2TF,
    Device,
    DeviceKind,
    Fidelity,
    Net,
    NetRole,
    PinRole,
    PortPair,
    Terminal,
)
from .primitives import (
    CCCS,
    CCVS,
    VCCS,
    VCVS,
    Capacitor,
    Conductance,
    IndependentI,
    IndependentV,
    Inductor,
    Nullor,
    Primitive,
)
from .raw_tf import MnaSystem, RawTransferFunction
from .ssir import SmallSignalIR

__all__ = [
    "GROUND_NAMES",
    "Circuit2TF",
    "Device",
    "DeviceKind",
    "Fidelity",
    "Net",
    "NetRole",
    "PinRole",
    "PortPair",
    "Terminal",
    # small-signal primitives + artifact
    "Primitive",
    "Conductance",
    "Capacitor",
    "Inductor",
    "VCCS",
    "VCVS",
    "CCCS",
    "CCVS",
    "Nullor",
    "IndependentV",
    "IndependentI",
    "SmallSignalIR",
    "MnaSystem",
    "RawTransferFunction",
]
