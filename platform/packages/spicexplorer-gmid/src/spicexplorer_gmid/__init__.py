"""SpiceXplorer gm/ID sizing tool (``spicexplorer_gmid``).

A **leaf tool** for deterministic transistor sizing with the gm/ID lookup-table methodology
(Jespers & Murmann, *Systematic Design of Analog CMOS Circuits Using Pre-Computed Lookup Tables*):
pick an inversion level (gm/ID) and channel length per device, read current density / VGS /
intrinsic gain / fT / caps off a pre-characterized LUT, and de-normalise to a width — no square-law
hand formulas, no SPICE tweaking loops, agreement with simulation to a few percent.

It reads pygmid ``.pkl`` LUTs (the committed analog-db ``_shared/gmid/<pdk>/`` tables) and depends
on ``spicexplorer-core`` + ``pygmid`` + ``numpy`` + ``pydantic`` **only** — never on a peer tool
(not ``spicexplorer`` the optimizer, not ``spicexplorer_netlist2tf``) and never on
``spicexplorer_analog_db`` (it takes LUT *paths/objects* and PDK constants as inputs; the
DB-reading composition is an orchestration concern). See meta-repo ``doc/plan_gmid_sizing.md``.

Quickstart::

    from spicexplorer_gmid import DeviceTable, size_for_gm

    nch = DeviceTable.load("…/_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl")
    op  = nch.at(gm_id=15, L=0.5, vds=0.9)            # OperatingPoint: jd, vgs, av0, ft, caps
    dev = size_for_gm(nch, gm=1e-3, gm_id=15, L=0.5, vds=0.9)   # SizedDevice(W, ID, op, gates)
    assert dev.passed                                 # all sanity gates hold
"""

from .contract import (
    AxisSpec,
    GeometryBounds,
    LUTConditions,
    LUTManifest,
    LUTModelRecord,
    LUTProvenance,
    OperatingPoint,
    SanityGate,
    SizedDevice,
    SizedPassive,
    SizingReport,
)
from .errors import GmidError, OutOfGridError
from .fingerwidth import FingerWidthSet
from .passives import size_capacitor, size_resistor
from .registry import LUTRegistry
from .sizing import size_for_current_density, size_for_gm
from .tables import DeviceTable, Sweep

__all__ = [
    # tables / exploration
    "DeviceTable",
    "Sweep",
    # finger-width interpolation (across characterised finger widths)
    "FingerWidthSet",
    # sizing flows
    "size_for_gm",
    "size_for_current_density",
    # passives
    "size_resistor",
    "size_capacitor",
    # LUT registry (enumerate + load by pdk/device/corner)
    "LUTRegistry",
    # manifest models (the typed registration record beside each .pkl)
    "LUTManifest",
    "AxisSpec",
    "LUTConditions",
    "LUTModelRecord",
    "LUTProvenance",
    # the typed I/O contract
    "OperatingPoint",
    "SizedDevice",
    "SizedPassive",
    "SizingReport",
    "SanityGate",
    "GeometryBounds",
    # errors
    "GmidError",
    "OutOfGridError",
]
