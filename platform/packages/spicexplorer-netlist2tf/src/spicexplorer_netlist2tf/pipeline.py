"""The end-to-end convenience entry — ``transfer_function`` composes S1→S5 with defaults.

This is the one-liner a notebook calls. Every stage it composes
(``ingest_netlist → small_signal_model → build_system → extract_tf → simplify_tf → describe_tf``) is
also independently callable for full control (the staged API); this just wires them with sensible
defaults and returns the single :class:`TransferFunctionResult` contract.
"""

from __future__ import annotations

from pathlib import Path

from spicexplorer_core.spice_engine import NetlistView

from .contract import TransferFunctionResult
from .describe import describe_tf
from .ingest import from_file, from_string, ingest_netlist
from .mna import build_system, detect_ac_input, extract_tf
from .model.ir import Circuit2TF, Fidelity
from .models import small_signal_model
from .simplify import DEFAULT_RATIO_FLOOR, DEFAULT_TOLERANCE, simplify_tf

__all__ = ["transfer_function"]


def _to_ir(
    source: str | Path | NetlistView | Circuit2TF,
    *,
    name: str | None,
    ports: dict[str, tuple[str, str]] | None,
    ground: str,
    flatten: bool = True,
    keep_opaque: tuple[str, ...] = (),
) -> Circuit2TF:
    if isinstance(source, Circuit2TF):
        return source
    if isinstance(source, NetlistView):
        return ingest_netlist(source, name=name or "circuit", ports=ports, ground=ground,
                              flatten=flatten, keep_opaque=keep_opaque)
    if isinstance(source, Path):
        return from_file(source, name=name, ports=ports, ground=ground,
                         flatten=flatten, keep_opaque=keep_opaque)
    # str: multi-line ⇒ SPICE text; otherwise a path (fall back to text if it doesn't exist).
    if "\n" in source or (not Path(source).exists() and source.lstrip().startswith("*")):
        return from_string(source, name=name or "circuit", ports=ports, ground=ground,
                           flatten=flatten, keep_opaque=keep_opaque)
    return from_file(source, name=name, ports=ports, ground=ground,
                     flatten=flatten, keep_opaque=keep_opaque)


def transfer_function(
    source: str | Path | NetlistView | Circuit2TF,
    output: tuple[str, str] | str,
    input: tuple[str, str] | str | None = None,
    *,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
    flatten: bool = True,
    keep_opaque: tuple[str, ...] = (),
    ratio_floor: float = DEFAULT_RATIO_FLOOR,
    tolerance: float = DEFAULT_TOLERANCE,
) -> TransferFunctionResult:
    """Run S1→S5 end to end and return the single contract.

    ``source`` is a netlist path, raw SPICE text, a ``NetlistView``, or a pre-built ``Circuit2TF``.
    ``input`` may be omitted for a *testbench-level* netlist: the input port is then auto-detected
    as the unique AC voltage source (``Vin in 0 dc VCM ac 1``) via :func:`detect_ac_input`.
    ``assumptions`` defaults to ``"full"`` (exact, with advisory suggestions surfaced in the ledger —
    the trustworthy default); pass a bundle (``"low_freq"``/``"ideal"``/``"dominant_pole"``) or a
    list of :class:`~spicexplorer_netlist2tf.assumptions.Assumption` to reduce. ``operating_point``
    enables the validation gate + numeric pole/zero coordinates; ``subs`` numericizes chosen symbols
    before the determinant (selective numericization). ``flatten``/``keep_opaque`` control subckt
    flattening at ingestion (see :func:`ingest_netlist`).
    """
    ir = _to_ir(source, name=name, ports=ports, ground=ground,
                flatten=flatten, keep_opaque=keep_opaque)
    ssir = small_signal_model(ir, level=level)
    system = build_system(ssir, subs=subs)
    if input is None:
        input = detect_ac_input(ssir)
    raw = extract_tf(system, output, input, numeric_subs=subs)
    simplified = simplify_tf(
        raw, assumptions, operating_point=operating_point,
        ratio_floor=ratio_floor, tolerance=tolerance,
    )
    return describe_tf(
        raw, simplified=simplified, operating_point=operating_point,
        model_level=level.value, ground=ir.ground,
    )
