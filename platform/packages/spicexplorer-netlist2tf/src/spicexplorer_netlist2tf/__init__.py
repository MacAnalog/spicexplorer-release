"""SpiceXplorer netlist2tf tool (``spicexplorer_netlist2tf``).

A **leaf tool** that ingests a circuit netlist, replaces each device with a small-signal model,
extracts the **exact** symbolic transfer function between two ports, and reduces it to the compact,
designer-readable hand-form by applying explicit, ordered, physically-motivated assumptions — each
one individually recorded and numerically validated against the exact TF.

It reads the netlist through ``spicexplorer_core.spice_engine.NetlistView`` and depends on
``spicexplorer-core`` + ``sympy`` + ``pydantic`` + ``numpy`` **only** — never on a peer tool
(not ``spicexplorer_circuitgraph``), never on lcapy/SLiCAP at runtime.

Stage spine (each a pure function over one immutable artifact):

    1. ingest    — netlist/JSON  -> the typed internal IR (``Circuit2TF``)         [P1, here]
    2. model     — IR            -> small-signal primitives                        [P2]
    3. build/solve — primitives  -> symbolic MNA system -> H(s)                    [P3]
    4. simplify  — exact H(s)    -> readable H(s) + validated assumption ledger    [P5]
    5. describe  — H(s)          -> DC gain / poles / zeros / ZPK / LaTeX          [P4]

See the meta-repo ``doc/plan_netlist2tf.md`` (architecture) and ``doc/todo_netlist2tf.md`` (phases).
"""

from .analyses import (
    asymptotic_gain,
    cmrr,
    common_mode_gain,
    input_impedance,
    loop_gain,
    open_loop_gain,
    output_impedance,
    psrr,
)
from .assumptions import (
    Assumption,
    dominant_pole,
    inband,
    intrinsic_gain_large,
    matched_pair,
    neglect_cgd,
    neglect_overlap_caps,
    transconductance_dominates,
)
from .contract import (
    AssumptionApplied,
    ComplexRoot,
    PoleZeroResult,
    SymbolicValue,
    TransferFunctionResult,
    ValidationReport,
)
from .describe import describe_tf
from .ingest import from_file, from_string, ingest_netlist
from .mna import build_system, detect_ac_input, extract_tf, transimpedance
from .model import (
    Circuit2TF,
    Device,
    DeviceKind,
    Fidelity,
    MnaSystem,
    Net,
    NetRole,
    PinRole,
    PortPair,
    RawTransferFunction,
    SmallSignalIR,
    Terminal,
)
from .model.raw_tf import SimplifiedTransferFunction
from .models import (
    MODEL_REGISTRY,
    SmallSignalModel,
    SymbolMint,
    register_model,
    small_signal_model,
)
from .pencil import poles_zeros
from .pipeline import transfer_function
from .simplify import simplify_tf, validate_simplification
from .tf import S

__all__ = [
    # Stage 1 — ingestion entry points
    "ingest_netlist",
    "from_file",
    "from_string",
    # the one IR
    "Circuit2TF",
    "Net",
    "NetRole",
    "Device",
    "DeviceKind",
    "Terminal",
    "PinRole",
    "PortPair",
    "Fidelity",
    # Stage 2 — small-signal modeling
    "small_signal_model",
    "SmallSignalIR",
    "SmallSignalModel",
    "SymbolMint",
    "register_model",
    "MODEL_REGISTRY",
    # Stage 3 — MNA build + symbolic solve
    "build_system",
    "detect_ac_input",
    "extract_tf",
    "transimpedance",
    "poles_zeros",
    "MnaSystem",
    "RawTransferFunction",
    "S",
    # Stage 5 — output forms + the single contract
    "describe_tf",
    "TransferFunctionResult",
    "SymbolicValue",
    "ComplexRoot",
    "PoleZeroResult",
    "AssumptionApplied",
    "ValidationReport",
    # Stage 4 — the simplification differentiator
    "simplify_tf",
    "validate_simplification",
    "SimplifiedTransferFunction",
    "Assumption",
    "intrinsic_gain_large",
    "transconductance_dominates",
    "neglect_cgd",
    "neglect_overlap_caps",
    "matched_pair",
    "dominant_pole",
    "inband",
    # end-to-end
    "transfer_function",
    # P7 derived analyses
    "open_loop_gain",
    "input_impedance",
    "output_impedance",
    # P9 DM/CM family (OD-4 + OD-9)
    "common_mode_gain",
    "cmrr",
    "psrr",
    "loop_gain",
    "asymptotic_gain",
]
