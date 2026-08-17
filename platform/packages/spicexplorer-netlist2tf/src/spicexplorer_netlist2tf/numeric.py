"""Numpy-only lambdify-at-jω — the numeric backbone of validation (and the numeric-refit path).

A torch-free reimplementation of the optimizer's ``eval_tf`` trick (the optimizer's version is a
reference, not an import — it is torch-coupled and lives in a peer). Substituting the operating point
and evaluating ``H(s=j2πf)`` over a frequency sweep is how Stage 4 (P5) turns "an approximation" into
"a *validated* approximation": lambdify exact and simplified, compare magnitude/phase over the band.
"""

from __future__ import annotations

import cmath
import math

import numpy as np
import sympy as sp

from .tf import S

__all__ = ["frequency_response", "log_sweep", "complex_value_at"]


def _substitute(expr: sp.Expr, defs: dict[str, float]) -> sp.Expr:
    """Substitute every non-``s`` free symbol by name; raise if any is left unbound."""
    repl: dict[sp.Basic, sp.Basic] = {
        sym: sp.Float(defs[str(sym)]) for sym in expr.free_symbols if str(sym) in defs
    }
    out = expr.xreplace(repl)
    unbound = sorted(str(x) for x in out.free_symbols if x != S)
    if unbound:
        raise ValueError(f"cannot evaluate numerically — unbound symbols remain: {unbound}")
    return out


def log_sweep(f_lo: float, f_hi: float, points_per_decade: int = 20) -> np.ndarray:
    """A log-spaced frequency vector (Hz) spanning ``[f_lo, f_hi]`` inclusive."""
    if f_lo <= 0 or f_hi <= f_lo:
        raise ValueError(f"need 0 < f_lo < f_hi; got {f_lo}, {f_hi}")
    decades = math.log10(f_hi / f_lo)
    n = max(2, int(round(points_per_decade * decades)) + 1)
    return np.logspace(math.log10(f_lo), math.log10(f_hi), n)


def frequency_response(
    expr: sp.Expr, defs: dict[str, float], freqs_hz: np.ndarray
) -> np.ndarray:
    """Evaluate ``H(s = j2πf)`` over ``freqs_hz`` after substituting the operating point ``defs``.

    Returns a complex ``ndarray`` the same length as ``freqs_hz``.
    """
    bound = _substitute(expr, defs)
    func = sp.lambdify(S, bound, "numpy")
    s_vals = 2j * np.pi * np.asarray(freqs_hz, dtype=float)
    out = func(s_vals)
    return np.asarray(out, dtype=complex) * np.ones_like(s_vals)  # broadcast constants


def complex_value_at(expr: sp.Expr, defs: dict[str, float], freq_hz: float = 0.0) -> complex:
    """Evaluate a (possibly constant) expression at a single frequency, returning a Python complex."""
    bound = _substitute(expr, defs)
    val = complex(bound.subs(S, 2j * math.pi * freq_hz))
    return val if not cmath.isnan(val.real) else complex(float(bound.subs(S, 0)))
