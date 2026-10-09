"""The symbolic-engine facade — the **only** module that touches raw symbolic algebra.

Centralizing sympy here means (a) the backend is swappable (an optional symengine fast path can be
slotted in later for the determinant/`cancel` bottleneck) and (b) determinism is defined at a single
canonicalization point: every rational result leaves through :func:`canonical_tf`, so the
byte-identical-output guarantee (plan §7) holds regardless of how the determinant was computed.
The one exception is the simplified TF of a POLE_SEPARATION step (``dominant_pole()``): it keeps
its two first-order denominator factors as built, because :func:`canonical_tf` would multiply them
back into one polynomial.

For R1 the backend is pure sympy. ``s`` is the one Laplace variable everyone shares.
"""

from __future__ import annotations

from typing import cast

import sympy as sp
from sympy.polys.matrices import DomainMatrix

__all__ = ["S", "canonical_tf", "as_num_den", "determinant", "cramer_numerator"]

#: The shared Laplace-domain variable.
S = sp.Symbol("s")


def canonical_tf(expr: sp.Expr) -> sp.Expr:
    """Reduce a rational expression in ``s`` to a single canonical ``N(s)/D(s)`` form.

    ``cancel`` puts it over one denominator and removes the common factor; the result is the fixed
    point we compare/serialize against. (Numeric equivalence — not string equality — is what tests
    assert across environments; this just makes the *same* environment reproducible.)
    """
    return cast("sp.Expr", sp.cancel(sp.together(expr)))


def as_num_den(expr: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """Numerator and denominator of the canonical form (both expanded over ``s``)."""
    num, den = sp.fraction(canonical_tf(expr))
    return sp.expand(num), sp.expand(den)


def determinant(matrix: sp.Matrix) -> sp.Expr:
    """Exact determinant. Berkowitz is division-free → robust over a symbolic matrix.

    A matrix whose only symbol is ``s`` (every device value numericized, ``subs=``) goes through
    sympy's polynomial-domain matrices instead: the same exact rational function, computed over
    ``ZZ(s)``/``QQ(s)`` without expression swell — 0.06 s on a 26-unknown analog-db bench where
    Berkowitz over generic expressions ran past 300 s (issue #310).
    """
    if matrix.shape == (0, 0):
        return sp.Integer(1)
    if matrix.free_symbols <= {S} and not matrix.has(sp.Float):
        dm = DomainMatrix.from_Matrix(matrix)
        return cast("sp.Expr", dm.domain.to_sympy(dm.det()))
    return cast("sp.Expr", matrix.det(method="berkowitz"))


def cramer_numerator(matrix: sp.Matrix, rhs: sp.Matrix, col: int) -> sp.Expr:
    """Cramer numerator for unknown ``col``: ``det(A with column col replaced by rhs)``."""
    replaced = matrix.copy()
    replaced[:, col] = rhs
    return determinant(replaced)
