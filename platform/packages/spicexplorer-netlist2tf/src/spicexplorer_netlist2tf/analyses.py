"""Derived small-signal analyses, in-leaf (OD-9; P7 base set + P9 DM/CM family).

The headline numbers a designer quotes — open-loop gain, input/output impedance, CMRR, PSRR,
loop gain — are **not new machinery; they are recipes over the same MNA solve** (plan §5b). Each
reuses ``ingest → model → build → (extract_tf | driving_point | decomposition) → simplify →
describe`` and returns the **standard** :class:`TransferFunctionResult` (with an ``analysis``
provenance tag), so the whole simplification differentiator carries over for free — a *validated,
symbolic* PSRR with every assumption named, not just "PSRR(s)".

P7 shipped ``open_loop_gain`` / ``input_impedance`` / ``output_impedance`` (single solve). P9 adds
the DM/CM family: ``common_mode_gain`` (the ``drive="cm"`` excitation), the ratio metrics ``cmrr``
(``A_dm/A_cm``) and ``psrr`` (``A_dm/A_(supply→out)``, via the §5b net-role override), and the
feedback pair ``loop_gain`` / ``asymptotic_gain`` (Blackman return ratio — the determinant is
*linear* in one controlled source's gain, ``T = k·D1/D0``; SLiCAP S4b, attributed in NOTICE).
Any metric needing a *real* bias point (PDK ``.op`` / gm-ID) is an orchestrator, not a leaf
analysis.
"""

from __future__ import annotations

import sympy as sp

from .contract import TransferFunctionResult
from .describe import describe_tf
from .mna import (
    _as_pair,
    build_system,
    detect_ac_input,
    driving_point_impedance,
    extract_tf,
    gain_decomposition,
    loop_gain_from_system,
)
from .model.ir import Fidelity
from .model.raw_tf import RawTransferFunction
from .models import _label, small_signal_model
from .pipeline import _to_ir
from .simplify import DEFAULT_RATIO_FLOOR, DEFAULT_TOLERANCE, simplify_tf
from .tf import S, canonical_tf

__all__ = [
    "open_loop_gain",
    "input_impedance",
    "output_impedance",
    "common_mode_gain",
    "cmrr",
    "psrr",
    "loop_gain",
    "asymptotic_gain",
]

_Source = "str | Path | NetlistView | Circuit2TF"


def _port_nets(port, system) -> set[str]:  # noqa: ANN001
    p = _as_pair(port, system)
    nets = {p.pos, p.neg}
    nets.discard(system.ground_rep)
    return {n for n in nets if n.lower() not in ("0", "gnd")}


def open_loop_gain(
    source,  # noqa: ANN001 — _Source
    output: tuple[str, str] | str,
    input: tuple[str, str] | str,
    *,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
    ratio_floor: float = DEFAULT_RATIO_FLOOR,
    tolerance: float = DEFAULT_TOLERANCE,
) -> TransferFunctionResult:
    """Open-loop voltage gain ``A_OL(s) = V_out / V_in`` — the base case (one ``extract_tf``)."""
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    system = build_system(small_signal_model(ir, level=level), subs=subs)
    raw = extract_tf(system, output, input, analysis="open_loop_gain", numeric_subs=subs)
    simplified = simplify_tf(raw, assumptions, operating_point=operating_point,
                            ratio_floor=ratio_floor, tolerance=tolerance)
    return describe_tf(raw, simplified=simplified, operating_point=operating_point,
                       model_level=level.value, ground=ir.ground)


def _impedance(
    source,  # noqa: ANN001
    port,  # noqa: ANN001
    analysis: str,
    *,
    ground_ports,  # noqa: ANN001
    level: Fidelity,
    operating_point: dict[str, float] | None,
    subs: dict[str, float] | None,
    ports: dict[str, tuple[str, str]] | None,
    ground: str,
    name: str | None,
) -> TransferFunctionResult:
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    ssir = small_signal_model(ir, level=level)
    # First pass to resolve named ports, then ground the requested ports (source-zeroing).
    base = build_system(ssir, subs=subs)
    extra: set[str] = set()
    for gp in ground_ports or ():
        extra |= _port_nets(gp, base)
    system = build_system(ssir, subs=subs, extra_grounds=extra) if extra else base
    raw = driving_point_impedance(system, port, analysis=analysis, numeric_subs=subs)
    # Impedances default to exact (no DOMINANCE bundle); user can still pass assumptions via describe.
    simplified = simplify_tf(raw, "full", operating_point=operating_point)
    return describe_tf(raw, simplified=simplified, operating_point=operating_point,
                       model_level=level.value, ground=ir.ground)


def input_impedance(
    source,  # noqa: ANN001
    port: tuple[str, str] | str,
    *,
    ground_ports=(),  # noqa: ANN001 — ports to tie to AC ground (source-zeroing)
    level: Fidelity = Fidelity.SOME_PARASITIC,
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """Input impedance ``Z_in(s) = V_x / I_x`` at ``port`` (inject a unit test current, read V)."""
    return _impedance(source, port, "input_impedance", ground_ports=ground_ports, level=level,
                      operating_point=operating_point, subs=subs, ports=ports, ground=ground, name=name)


def output_impedance(
    source,  # noqa: ANN001
    port: tuple[str, str] | str,
    *,
    zero_input: tuple[str, str] | str | None = None,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """Output impedance ``Z_out(s)`` at ``port``. For an **open-loop** Z_out pass ``zero_input`` (the
    input port) to ground it (source-zeroing); omit it for the input-active (closed-loop) variant."""
    ground_ports = (zero_input,) if zero_input is not None else ()
    return _impedance(source, port, "output_impedance", ground_ports=ground_ports, level=level,
                      operating_point=operating_point, subs=subs, ports=ports, ground=ground, name=name)


# ------------------------------------------------------------------------
# P9 — the DM/CM family (OD-4 + OD-9)
# ------------------------------------------------------------------------
def _finish(
    raw: RawTransferFunction,
    *,
    assumptions,  # noqa: ANN001
    operating_point: dict[str, float] | None,
    level: Fidelity,
    ground: str,
    ratio_floor: float = DEFAULT_RATIO_FLOOR,
    tolerance: float = DEFAULT_TOLERANCE,
    component_tfs: dict[str, str] | None = None,
) -> TransferFunctionResult:
    """simplify → describe, shared by every P9 analysis (the differentiator carries over)."""
    simplified = simplify_tf(raw, assumptions, operating_point=operating_point,
                             ratio_floor=ratio_floor, tolerance=tolerance)
    return describe_tf(raw, simplified=simplified, operating_point=operating_point,
                       model_level=level.value, ground=ground, component_tfs=component_tfs)


def _ratio_raw(num: RawTransferFunction, den: RawTransferFunction, analysis: str) -> RawTransferFunction:
    """A ratio metric (CMRR, PSRR) as one canonical expression — simplified+validated as a whole."""
    expr = canonical_tf(sp.cancel(num.expr / den.expr))
    return RawTransferFunction(
        expr=expr, s=S, output=num.output, input=num.input, name=num.name, analysis=analysis,
        drive=num.drive, solve_path=num.solve_path, numeric_subs=dict(num.numeric_subs),
    )


def common_mode_gain(
    source,  # noqa: ANN001 — _Source
    output: tuple[str, str] | str,
    input: tuple[str, str] | str,
    *,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """Common-mode gain ``A_cm(s)``: both input nodes driven together (``drive="cm"``)."""
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    system = build_system(small_signal_model(ir, level=level), subs=subs)
    raw = extract_tf(system, output, input, analysis="common_mode_gain", drive="cm",
                     numeric_subs=subs)
    return _finish(raw, assumptions=assumptions, operating_point=operating_point,
                   level=level, ground=ir.ground)


def cmrr(
    source,  # noqa: ANN001 — _Source
    output: tuple[str, str] | str,
    input: tuple[str, str] | str,
    *,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """``CMRR(s) = A_dm / A_cm`` — two excitations of **one** built system, combined as a single
    symbolic ratio and then simplified+validated as one expression (plan §5b's combine operator).
    The component TFs ride along in ``component_tfs``."""
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    system = build_system(small_signal_model(ir, level=level), subs=subs)
    a_dm = extract_tf(system, output, input, analysis="differential_gain", numeric_subs=subs)
    a_cm = extract_tf(system, output, input, analysis="common_mode_gain", drive="cm",
                      numeric_subs=subs)
    if a_cm.expr == 0:
        raise ValueError(
            "A_cm is identically 0 (an ideal tail/current source makes CMRR infinite at this "
            "fidelity) — model the tail's finite output resistance or raise the fidelity level"
        )
    raw = _ratio_raw(a_dm, a_cm, "cmrr")
    return _finish(raw, assumptions=assumptions, operating_point=operating_point, level=level,
                   ground=ir.ground,
                   component_tfs={"a_dm": str(a_dm.expr), "a_cm": str(a_cm.expr)})


def psrr(
    source,  # noqa: ANN001 — _Source
    output: tuple[str, str] | str,
    input: tuple[str, str] | str | None = None,
    *,
    supply: str = "vdd",
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """``PSRR(s) = A_dm / A_(supply→out)`` — the §5b net-role override in action.

    ``A_dm`` comes from the normal system. For the supply path the named rail is **re-promoted to
    a signal input** (``build_system(exclude_grounds={supply})``: not merged into the AC
    reference, its bias source not shorted) while every other independent V source is zeroed
    (``short_all_sources``) — so the rail is the only excitation, exactly the PSRR measurement
    setup. ``supply`` must name the rail *as it appears at this level* (testbench rails like
    ``v_dd`` included). The signal input is auto-detected from the AC source when omitted.
    """
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    ssir = small_signal_model(ir, level=level)
    if supply not in ssir.nets:
        raise ValueError(f"supply net {supply!r} not found; nets: {sorted(ssir.nets)}")

    system_dm = build_system(ssir, subs=subs)
    if input is None:
        input = detect_ac_input(ssir)
    a_dm = extract_tf(system_dm, output, input, analysis="differential_gain", numeric_subs=subs)

    system_ps = build_system(ssir, subs=subs, exclude_grounds={supply}, short_all_sources=True)
    a_ps = extract_tf(system_ps, output, (supply, ground), analysis="supply_gain",
                      numeric_subs=subs)
    if a_ps.expr == 0:
        raise ValueError(
            f"A_({supply}→out) is identically 0 at this fidelity — nothing couples the rail to "
            "the output (PSRR is infinite); raise the fidelity or check the supply name"
        )
    raw = _ratio_raw(a_dm, a_ps, "psrr")
    return _finish(raw, assumptions=assumptions, operating_point=operating_point, level=level,
                   ground=ir.ground,
                   component_tfs={"a_dm": str(a_dm.expr), f"a_{supply}": str(a_ps.expr)})


def _probe_symbol(probe: str) -> str:
    """Resolve a device ref (``M1`` / ``XM1_XOTA``) to its minted gm symbol name."""
    return f"gm_{_label(probe)}"


def loop_gain(
    source,  # noqa: ANN001 — _Source
    probe: str,
    *,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """Loop gain (return ratio) ``T(s)`` of the feedback loop through device ``probe``.

    Blackman's convention: every independent source is zeroed (V short, I open —
    ``short_all_sources``), the homogeneous determinant is split as ``D = D0 + gm·D1`` (exactly
    linear: one VCCS is a rank-one update), and ``T = gm·D1/D0``. ``probe`` is the device ref
    whose transconductance is the reference variable (``M1``, or ``XM1_XOTA`` after flatten);
    its gm is kept symbolic even when ``subs`` numericizes the rest.
    """
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    ssir = small_signal_model(ir, level=level)
    k_name = _probe_symbol(probe)
    eff_subs = {n: v for n, v in (subs or {}).items() if n != k_name}
    system = build_system(ssir, subs=eff_subs, short_all_sources=True)
    raw = loop_gain_from_system(system, k_name, numeric_subs=eff_subs)
    return _finish(raw, assumptions=assumptions, operating_point=operating_point,
                   level=level, ground=ir.ground)


def asymptotic_gain(
    source,  # noqa: ANN001 — _Source
    output: tuple[str, str] | str,
    input: tuple[str, str] | str | None,
    probe: str,
    *,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    assumptions: str | list = "full",
    operating_point: dict[str, float] | None = None,
    subs: dict[str, float] | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    name: str | None = None,
) -> TransferFunctionResult:
    """The asymptotic-gain feedback view (SLiCAP S4b): ``H = (A∞·T + ρ)/(1 + T)``, exactly.

    Returns ``A∞`` (the ideal-feedback gain, probe's gm → ∞ — e.g. ``1`` for a unity buffer, the
    ``1/β`` of the loop) as the main TF, with the loop gain ``T``, the direct transmission ``ρ``,
    and the exact closed-loop ``H`` riding in ``component_tfs``. All four come from **one**
    augmented solve split linearly in the probe's gm, so the identity holds symbolically.
    """
    ir = _to_ir(source, name=name, ports=ports, ground=ground)
    ssir = small_signal_model(ir, level=level)
    k_name = _probe_symbol(probe)
    eff_subs = {n: v for n, v in (subs or {}).items() if n != k_name}
    system = build_system(ssir, subs=eff_subs)
    if input is None:
        input = detect_ac_input(ssir)
    parts = gain_decomposition(system, output, input, k_name, numeric_subs=eff_subs)
    return _finish(parts["asymptotic_gain"], assumptions=assumptions,
                   operating_point=operating_point, level=level, ground=ir.ground,
                   component_tfs={
                       "gain": str(parts["gain"].expr),
                       "loop_gain": str(parts["loop_gain"].expr),
                       "direct_transmission": str(parts["direct_transmission"].expr),
                   })
