"""Stage 4 — the simplification differentiator: reduce exact ``H(s)`` to readable hand-form.

This is the reason the tool exists (plan §6). Each assumption is applied by a per-kind sympy primitive
in a **fixed phase order** (EQUALITY → SMALLNESS → DOMINANCE → BAND_LIMIT → POLE_SEPARATION; rewrites
don't commute), every step is **numerically arbitrated** (a DOMINANCE drop the numbers don't support is
*rejected*, not applied — which neither lcapy nor SLiCAP does), and the whole reduction is **validated
against the exact TF** (lambdify exact-vs-simplified over a sweep). A step that pushes error past
tolerance is rolled back and flagged; a failing *final* gate returns the exact TF marked UNREDUCED — we
never silently ship an unvalidated approximation. Every step is recorded as an ``AssumptionApplied``.
"""

from __future__ import annotations

import math
from typing import cast

import numpy as np
import sympy as sp

from .assumptions import (
    BAND_LIMIT,
    DOMINANCE,
    EQUALITY,
    POLE_SEPARATION,
    SMALLNESS,
    Assumption,
    intrinsic_gain_large,
    neglect_cgd,
    resolve,
    transconductance_dominates,
)
from .contract import AssumptionApplied, ValidationReport
from .model.raw_tf import RawTransferFunction, SimplifiedTransferFunction
from .numeric import frequency_response, log_sweep
from .tf import S, as_num_den, canonical_tf

__all__ = ["simplify_tf", "validate_simplification", "DEFAULT_RATIO_FLOOR", "DEFAULT_TOLERANCE"]

DEFAULT_RATIO_FLOOR = 100.0  # |dominant| ≥ 100·|dominated|  (≈ 40 dB)
DEFAULT_TOLERANCE = 0.05  # 5% max relative error over the band


# ------------------------------------------------------------------------
# Coarse operating point (ball-park magnitudes for DOMINANCE/SMALLNESS arbitration)
# ------------------------------------------------------------------------
def _coarse_op(symbols: set[str]) -> dict[str, float]:
    op: dict[str, float] = {}
    for n in symbols:
        if n.startswith("gm_"):
            op[n] = 1e-3
        elif n.startswith("gmb_"):
            op[n] = 2e-4
        elif n.startswith("ro_"):
            op[n] = 2e5  # ball-park intrinsic gain gm·ro ≈ 200 → clears the 100× DOMINANCE floor
        elif n[:1] == "c":  # cgs_/cgd_/cdb_/csb_/cl/cc …
            op[n] = 1e-14
        elif n[:1] == "r":  # rl, r, rload …
            op[n] = 1e4
        else:
            op[n] = 1.0
    return op


def _evalnum(expr: sp.Expr, op: dict[str, float]) -> float:
    repl: dict[sp.Basic, sp.Basic] = {
        sym: sp.Float(op[str(sym)]) for sym in expr.free_symbols if str(sym) in op
    }
    val = expr.xreplace(repl)
    if val.free_symbols:
        return float("nan")
    try:
        return abs(complex(val))
    except (TypeError, ValueError):
        return float("nan")


def _record(a: Assumption, order: int, **kw) -> AssumptionApplied:
    return AssumptionApplied(
        name=a.id, kind=a.kind, scope=a.scope, justification=a.justification, order=order,
        description=kw.pop("description", a.id), **kw,
    )


# ------------------------------------------------------------------------
# Per-kind rewrites
# ------------------------------------------------------------------------
def _localize(expr: sp.Expr, reference: sp.Expr) -> sp.Expr:
    """Map ``expr``'s symbols onto same-named symbols from ``reference`` so sympy ops match identity
    (payload symbols are sympified plain; the TF's are ``positive=True`` — names must bind to the
    *same* Symbol objects or ``cancel``/``xreplace`` silently miss)."""
    ref = {str(s): s for s in reference.free_symbols}
    repl: dict[sp.Basic, sp.Basic] = {s: ref[str(s)] for s in expr.free_symbols if str(s) in ref}
    return expr.xreplace(repl) if repl else expr


def _has_factor(term: sp.Expr, dom: sp.Expr) -> bool:
    """Whether ``dom`` is a multiplicative *factor* of ``term`` (``term/dom`` has no ``dom`` symbol
    left in a denominator). So ``gm_m2`` is a factor of ``gm_m2·ro_m1·ro_m2`` but not of ``ro_m1``."""
    _, den = sp.fraction(sp.cancel(term / dom))
    return not (den.free_symbols & dom.free_symbols)


def _apply_dominance(
    expr: sp.Expr, a: Assumption, op: dict[str, float], floor: float, order: int
) -> tuple[sp.Expr, AssumptionApplied]:
    dom = _localize(sp.sympify(a.payload["dominant"]), expr)
    dropped_all: list[str] = []
    ratios: list[float] = []
    contradicted = False

    def prune(add: sp.Add) -> sp.Expr:
        nonlocal contradicted
        terms = list(add.args)
        sfree = [t for t in terms if not t.has(S)]
        domterms = [t for t in sfree if _has_factor(t, dom)]
        if not domterms:
            return add
        dom_mag = max(_evalnum(t, op) for t in domterms)
        others = [t for t in sfree if t not in domterms]
        other_max = max((_evalnum(t, op) for t in others), default=0.0)
        if other_max > dom_mag:  # the declared-dominant quantity is NOT the largest → contradiction
            contradicted = True
            return add
        kept = [t for t in terms if t.has(S) or t in domterms]
        dropped: list[sp.Expr] = []
        for t in others:
            m = _evalnum(t, op)
            if m * floor < dom_mag:
                dropped.append(t)
                ratios.append(dom_mag / m if m else math.inf)
            else:
                kept.append(t)  # not dominated by the floor → keep
        if dropped:
            dropped_all.extend(str(t) for t in dropped)
            return sp.Add(*kept)
        return add

    new = cast("sp.Expr", expr.replace(lambda e: e.is_Add, prune))
    if contradicted:
        return expr, _record(a, order, status="REJECTED_NUMERICS", validated=False,
                             condition=f"{dom} >> (siblings)",
                             description=f"declared-dominant {dom} is not numerically largest")
    if not dropped_all:
        return expr, _record(a, order, status="NO_OP", condition=f"{dom} >> (siblings)",
                             description=f"no sum dominated by {dom}")
    return canonical_tf(new), _record(
        a, order, status="APPLIED", condition=f"{dom} >> (siblings)",
        description=f"dropped {', '.join(dropped_all)} (dominated by {dom})",
        dropped_terms=dropped_all, numeric_ratio=min(ratios) if ratios else None,
    )


def _apply_smallness(
    expr: sp.Expr, a: Assumption, order: int
) -> tuple[sp.Expr, AssumptionApplied]:
    sym = sp.Symbol(a.payload["symbol"], positive=True)
    if sym not in expr.free_symbols:
        # also try the assumption-free symbol (defensive)
        plain = sp.Symbol(a.payload["symbol"])
        if plain not in expr.free_symbols:
            return expr, _record(a, order, status="NO_OP",
                                 description=f"{a.payload['symbol']} not present")
        sym = plain
    new = canonical_tf(cast("sp.Expr", sp.limit(expr, sym, 0)))
    return new, _record(a, order, status="APPLIED", condition=f"{sym} -> 0",
                       description=f"neglected {sym} (limit -> 0)", substitution=f"{sym} -> 0")


def _apply_equality(
    expr: sp.Expr, a: Assumption, order: int
) -> tuple[sp.Expr, AssumptionApplied]:
    keep, repl = a.payload["a"], a.payload["b"]
    mapping: dict[sp.Basic, sp.Basic] = {}
    for sym in expr.free_symbols:
        name = str(sym)
        if name.endswith(f"_{repl}"):
            mapping[sym] = sp.Symbol(name[: -len(repl)] + keep, positive=True)
    if not mapping:
        return expr, _record(a, order, status="NO_OP",
                             description=f"no _{repl} symbols to match to _{keep}")
    new = canonical_tf(cast("sp.Expr", expr.xreplace(mapping)))
    subs_str = ", ".join(f"{k}->{v}" for k, v in mapping.items())
    return new, _record(a, order, status="APPLIED", description=f"matched: {subs_str}",
                       substitution=subs_str)


def _apply_band_limit(
    expr: sp.Expr, a: Assumption, op: dict[str, float], floor: float, order: int
) -> tuple[sp.Expr, AssumptionApplied]:
    w = 2 * math.pi * float(a.payload["f_hi"])
    num, den = as_num_den(expr)
    dropped: list[str] = []

    def prune_poly(poly_expr: sp.Expr) -> sp.Expr:
        p = sp.Poly(poly_expr, S)
        terms = [(k, c) for k, c in p.terms()]  # k=(degree,), c=coeff
        mags = [abs(_evalnum(c, op)) * (w ** k[0]) for k, c in terms]
        ref = max(mags) if mags else 0.0
        if ref == 0:
            return poly_expr
        kept = sp.Integer(0)
        for (k, c), m in zip(terms, mags):
            if m * floor < ref and k[0] > 0:
                dropped.append(f"{c}*s^{k[0]}")
            else:
                kept += c * S ** k[0]
        return kept

    new = canonical_tf(prune_poly(num) / prune_poly(den))
    if not dropped:
        return expr, _record(a, order, status="NO_OP",
                             description=f"no s-terms negligible up to {a.payload['f_hi']:g} Hz")
    return new, _record(a, order, status="APPLIED", scope="BAND",
                       description=f"dropped high-s terms in band: {', '.join(dropped)}",
                       dropped_terms=dropped)


def _apply_pole_separation(
    expr: sp.Expr, a: Assumption, order: int
) -> tuple[sp.Expr, AssumptionApplied]:
    num, den = as_num_den(expr)
    p = sp.Poly(den, S)
    if p.degree() != 2:
        return expr, _record(a, order, status="NO_OP",
                             description="dominant-pole collapse implemented for 2nd-order denom only")
    c2, c1, c0 = p.all_coeffs()
    if c0 == 0 or c1 == 0:
        return expr, _record(a, order, status="NO_OP", description="degenerate denominator")
    a1, b1 = c1 / c0, c2 / c0  # den/c0 = 1 + a1 s + b1 s^2
    factored = (1 + a1 * S) * (1 + (b1 / a1) * S)  # widely-separated-pole factorization
    new = canonical_tf((num / c0) / factored)
    return new, _record(a, order, status="APPLIED",
                       condition="p1 << p2", description="dominant-pole factorization of 2nd-order denom")


def _apply_one(
    expr: sp.Expr, a: Assumption, op: dict[str, float], floor: float, order: int
) -> tuple[sp.Expr, AssumptionApplied]:
    if a.kind == EQUALITY:
        return _apply_equality(expr, a, order)
    if a.kind == SMALLNESS:
        return _apply_smallness(expr, a, order)
    if a.kind == DOMINANCE:
        return _apply_dominance(expr, a, op, floor, order)
    if a.kind == BAND_LIMIT:
        return _apply_band_limit(expr, a, op, floor, order)
    if a.kind == POLE_SEPARATION:
        return _apply_pole_separation(expr, a, order)
    raise ValueError(f"no rewrite for kind {a.kind}")  # pragma: no cover


# ------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------
def _relative_error(exact: sp.Expr, simplified: sp.Expr, op: dict[str, float], freqs) -> float:
    he = frequency_response(exact, op, freqs)
    hs = frequency_response(simplified, op, freqs)
    denom = np.abs(he)
    denom[denom == 0] = 1e-30
    return float(np.max(np.abs(hs - he) / denom))


def validate_simplification(
    exact: sp.Expr,
    simplified: sp.Expr,
    operating_point: dict[str, float],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
    freqs=None,
) -> ValidationReport:
    """Lambdify exact-vs-simplified over a sweep and bound the error (the trust gate)."""
    if freqs is None:
        freqs = log_sweep(1.0, 1e9, points_per_decade=10)
    he = frequency_response(exact, operating_point, freqs)
    hs = frequency_response(simplified, operating_point, freqs)
    denom = np.abs(he)
    denom[denom == 0] = 1e-30
    rel = np.abs(hs - he) / denom
    mag_db = np.abs(20 * np.log10(np.abs(hs) / denom))
    phase_deg = np.abs(np.angle(hs, deg=True) - np.angle(he, deg=True))
    max_rel = float(np.max(rel))
    return ValidationReport(
        operating_point=dict(operating_point),
        freq_hz_min=float(freqs[0]), freq_hz_max=float(freqs[-1]), num_points=len(freqs),
        max_relative_error=max_rel,
        max_magnitude_error_db=float(np.max(mag_db)),
        max_phase_error_deg=float(np.max(phase_deg)),
        passed=bool(max_rel <= tolerance), tolerance=tolerance, method="lambdify_numpy",
    )


# ------------------------------------------------------------------------
# Advisory mode
# ------------------------------------------------------------------------
def _advisory(expr: sp.Expr, op: dict[str, float], floor: float) -> list[AssumptionApplied]:
    """Without applying anything, suggest the canonical assumptions the operating point supports."""
    labels = {n[len("gm_"):] for n in (str(x) for x in expr.free_symbols) if n.startswith("gm_")}
    cap_labels = {n[len("cgd_"):] for n in (str(x) for x in expr.free_symbols) if n.startswith("cgd_")}
    out: list[AssumptionApplied] = []
    order = 0
    for lb in sorted(labels):
        for cand in (transconductance_dominates(lb), intrinsic_gain_large(lb)):
            _, rec = _apply_dominance(expr, cand, op, floor, order)
            if rec.status == "APPLIED":
                rec.status = "SUGGESTED"
                out.append(rec)
                order += 1
    for lb in sorted(cap_labels):
        cand = neglect_cgd(lb)
        new, rec = _apply_smallness(expr, cand, order)
        if rec.status == "APPLIED" and new != expr:
            rec.status = "SUGGESTED"
            out.append(rec)
            order += 1
    return out


# ------------------------------------------------------------------------
# The pipeline
# ------------------------------------------------------------------------
def simplify_tf(
    raw: RawTransferFunction,
    assumptions: str | Assumption | list = "full",
    *,
    operating_point: dict[str, float] | None = None,
    ratio_floor: float = DEFAULT_RATIO_FLOOR,
    tolerance: float = DEFAULT_TOLERANCE,
    validate: bool = True,
) -> SimplifiedTransferFunction:
    """Reduce ``raw.expr`` by the resolved assumptions, in the fixed phase order, with validation.

    ``assumptions`` is a bundle name (``"full"``/``"low_freq"``/``"ideal"``/``"dominant_pole"``), a
    single :class:`Assumption`, or a list. With ``operating_point`` given, every applied step is
    validated incrementally (rolled back + flagged if it breaks tolerance) and the whole reduction is
    validated at the end (UNREDUCED fallback on failure). The numeric arbitration for DOMINANCE uses a
    ball-park coarse operating point when none is supplied.
    """
    exact = canonical_tf(raw.expr)
    symbols = {str(x) for x in exact.free_symbols if x != S}
    # Merge a ball-park coarse op under the user's: validation then always has every symbol bound.
    op = {**_coarse_op(symbols), **(operating_point or {})}
    items = sorted(resolve(assumptions, symbols), key=lambda a: (a.phase, a.id))

    ledger: list[AssumptionApplied] = []
    current = exact
    freqs = log_sweep(1.0, 1e9, points_per_decade=10) if (validate and items) else None

    for order, a in enumerate(items):
        trial, record = _apply_one(current, a, op, ratio_floor, order)
        if record.status == "APPLIED" and freqs is not None:
            # Per-step (incremental) gate: pinpoints which assumption, if any, breaks trust.
            err = _relative_error(exact, trial, op, freqs)
            record.relative_error = err
            if err > tolerance:
                record.status = "REJECTED_VALIDATION"
                record.validated = False
                ledger.append(record)
                continue  # rolled back: current unchanged
            record.validated = True
        if record.status == "APPLIED":
            current = trial
        ledger.append(record)

    # Advisory: when nothing was asked, surface what the operating point supports.
    if not items:
        ledger.extend(_advisory(exact, op, ratio_floor))

    # Final (end-to-end) gate. Authoritative at the user's operating point when supplied.
    validation: ValidationReport | None = None
    unreduced = False
    if validate and items:
        validation = validate_simplification(exact, current, op, tolerance=tolerance)
        if operating_point is None:
            validation.notes = "ball-park operating point (no defs supplied)"
        if validation.passed is False:  # safety net — never ship an unvalidated approximation
            current = exact
            unreduced = True

    return SimplifiedTransferFunction(
        expr=current, exact=exact, raw=raw, ledger=ledger, validation=validation, unreduced=unreduced,
    )
