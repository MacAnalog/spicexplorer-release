"""Stage 5 — parameterize ``H(s)`` into the readable forms and assemble the single contract.

``describe_tf`` turns a :class:`RawTransferFunction` (or, later, a simplified one) into a
:class:`TransferFunctionResult`: DC gain, poles, zeros, ZPK/Q/ω₀, LaTeX. Thin sympy wrappers,
uncapped in order (past SymXplorer's order-2 biquad limit); the output-form *vocabulary* mirrors
lcapy/SLiCAP but is reimplemented sympy-native.
"""

from __future__ import annotations

import math

import numpy as np
import sympy as sp

from .contract import ComplexRoot, SymbolicValue, TransferFunctionResult
from .model.ir import GROUND_NAMES, PortPair
from .model.raw_tf import RawTransferFunction, SimplifiedTransferFunction
from .tf import S, as_num_den

__all__ = ["describe_tf"]


def _bind(expr: sp.Expr, defs: dict[str, float] | None) -> sp.Expr:
    """Substitute numeric values by symbol *name* (assumption-insensitive — minted symbols are
    ``positive=True``, so matching plain ``Symbol(name)`` keys would silently miss)."""
    if not defs:
        return expr
    repl: dict[sp.Basic, sp.Basic] = {
        sym: sp.Float(defs[str(sym)]) for sym in expr.free_symbols if str(sym) in defs
    }
    return expr.xreplace(repl) if repl else expr


def _is_numeric(expr: sp.Expr) -> bool:
    return all(x == S for x in expr.free_symbols)


def _symbolic_value(expr: sp.Expr, defs: dict[str, float] | None) -> SymbolicValue:
    expr = sp.nsimplify(expr) if expr.is_number and not expr.free_symbols else expr
    value: float | None = None
    num = _bind(expr, defs)
    if _is_numeric(num):
        try:
            value = float(sp.re(complex(num)))
        except (TypeError, ValueError):
            value = None
    return SymbolicValue(expr=str(expr), latex=sp.latex(expr), value=value)


def _complex_root(z: complex, multiplicity: int = 1) -> ComplexRoot:
    """A numeric root in the ``s`` (rad/s) plane → a :class:`ComplexRoot`."""
    freq = abs(z) / (2 * math.pi) if z != 0 else 0.0
    q = None
    if abs(z.imag) > 1e-9 * (abs(z.real) + abs(z.imag)) and abs(z.real) > 0:
        q = abs(z) / (2 * abs(z.real))
    return ComplexRoot(
        expr=str(sp.nsimplify(z.real)) if z.imag == 0 else str(z),
        value_real=float(z.real),
        value_imag=float(z.imag),
        frequency_hz=float(freq),
        q=float(q) if q is not None else None,
        multiplicity=multiplicity,
    )


def _roots(poly_expr: sp.Expr, defs: dict[str, float] | None) -> list[ComplexRoot]:
    """Roots of ``poly_expr`` (a polynomial in ``s``) as :class:`ComplexRoot`s.

    Numeric coefficients (after optionally substituting ``defs``) → ``numpy.roots``; symbolic ones →
    ``sympy.roots`` closed forms (uncapped order) with numeric coordinates when ``defs`` resolve them.
    """
    expr = sp.expand(_bind(poly_expr, defs))
    if expr == 0 or not expr.has(S):
        return []
    poly = sp.Poly(expr, S)

    if _is_numeric(expr):
        coeffs = [complex(c) for c in poly.all_coeffs()]
        roots = np.roots(coeffs) if len(coeffs) > 1 else np.array([])
        return [_complex_root(complex(z)) for z in roots]

    # Symbolic: closed-form roots; numeric coordinates if defs resolve them.
    out: list[ComplexRoot] = []
    try:
        rdict = sp.roots(poly)
    except Exception:  # noqa: BLE001 — high-degree symbolic may be unsolvable
        rdict = {}
    for root, mult in rdict.items():
        num = _bind(root, defs)
        cr = ComplexRoot(expr=str(root), latex=sp.latex(root), multiplicity=int(mult))
        if not num.free_symbols:
            z = complex(num)
            cr.value_real, cr.value_imag = float(z.real), float(z.imag)
            cr.frequency_hz = abs(z) / (2 * math.pi)
        out.append(cr)
    return out


def _conv_type(inp: PortPair, ground: str, drive: str = "dm") -> str:
    single = inp.neg == ground or inp.neg.lower() in GROUND_NAMES
    if not single and drive == "cm":
        return "cm"
    return "se" if single else "diff"


def describe_tf(
    raw: RawTransferFunction,
    *,
    simplified: SimplifiedTransferFunction | None = None,
    operating_point: dict[str, float] | None = None,
    model_level: str = "some_parasitic",
    ground: str = "0",
    component_tfs: dict[str, str] | None = None,
) -> TransferFunctionResult:
    """Parameterize a TF into the single :class:`TransferFunctionResult`.

    With ``simplified`` (the Stage-4 output, P5), the readable parameterization (DC gain / poles /
    zeros) is taken from the *simplified* TF and the assumption ledger + validation are carried;
    the exact TF is always also present. ``operating_point`` enables numeric coordinates.
    """
    exact = raw.expr
    h = simplified.expr if simplified is not None else exact  # parameterize the readable form
    num, den = as_num_den(h)
    dc = sp.limit(h, S, 0)

    zeros = _roots(num, operating_point)
    poles = _roots(den, operating_point)
    dc_gain = _symbolic_value(dc, operating_point)

    # GBW from a single dominant (real) pole, when numeric.
    gbw: SymbolicValue | None = None
    real_poles = [p for p in poles if p.value_real is not None and p.value_imag == 0.0]
    if dc_gain.value is not None and len(real_poles) >= 1:
        dom = min(real_poles, key=lambda p: abs(p.value_real or 0.0))
        if dom.value_real:
            gbw_hz = abs(dc_gain.value) * abs(dom.value_real) / (2 * math.pi)
            gbw = SymbolicValue(expr=str(gbw_hz), value=gbw_hz)

    return TransferFunctionResult(
        name=raw.name,
        output_nodes=(raw.output.pos, raw.output.neg),
        input_nodes=(raw.input.pos, raw.input.neg),
        conv_type=_conv_type(raw.input, ground, raw.drive),
        component_tfs=dict(component_tfs or {}),
        model_level=model_level,
        kept_symbolic=list(raw.kept_symbolic),
        solve_path=raw.solve_path,
        free_symbols=sorted(str(x) for x in exact.free_symbols if x != S),
        analysis=raw.analysis,
        tf_exact_expr=str(exact),
        tf_exact_latex=sp.latex(exact),
        tf_simplified_expr=str(h),  # == exact unless Stage 4 reduced it
        tf_simplified_latex=sp.latex(h),
        dc_gain=dc_gain,
        poles=poles,
        zeros=zeros,
        gbw_hz=gbw,
        assumptions_applied=list(simplified.ledger) if simplified is not None else [],
        validation=simplified.validation if simplified is not None else None,  # type: ignore[arg-type]
    )
