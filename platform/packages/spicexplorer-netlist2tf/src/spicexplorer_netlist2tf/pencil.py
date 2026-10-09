"""Poles and zeros straight from the MNA pencil, with no symbolic determinant.

``describe_tf`` finds roots the textbook way: expand ``H(s)`` into numerator and
denominator polynomials and hand the coefficients to ``numpy.roots``. That is exact for
the small, hand-sized circuits Stage 4 is aimed at, and it is the right default because it
also works when the coefficients are still *symbolic*.

It stops working on circuits that are merely medium-sized, because **the determinant does
not finish.** ``extract_tf`` computes a symbolic determinant, and at ``Fidelity.FULL`` a
capacitance lands on nearly every branch. A 13-node cell with 16 transistors takes
minutes-to-never, and nothing about the call says so in advance.

Rooting the expanded coefficients is not the weak point once they are exact, and ingestion
keeps netlist numbers as exact rationals (audit LEAF-F06). On a 4-section RC ladder whose
denominator coefficients span 1e24, ``numpy.roots`` finds roots with a residual of 1.75e-22
and the pencil 2.79e-22 (``notebooks/pencil_poles_zeros.py``, section 2). This docstring
used to say that a 4th-order 250 Hz filter (degree-15 denominator) loses its low-frequency
poles to expansion; that was observed while numbers were still ingested as floats, and the
filter has not been re-run since.

This module never forms the determinant. Every primitive the stamp emits is a conductance,
a VCCS or ``s·C``, so the assembled matrix is **exactly affine in s**::

    Y(s) = G + s·C

and the poles are the finite generalized eigenvalues of the pencil ``(G, C)`` — a matrix
problem, with no polynomial ever formed. Bordering the same matrix with the output selector
gives the zeros the same way.

Numerics
--------
The eigenvalues come from ``numpy`` alone (no scipy, per the dependency charter) by
shift-and-invert: for any shift ``σ`` where ``K = G + σC`` is nonsingular,

    det(G + sC) = 0   ⇔   s = σ − 1/λ   for each nonzero eigenvalue λ of ``K⁻¹C``

and the zero eigenvalues of ``K⁻¹C`` are exactly the pencil's infinite eigenvalues, which
drop out on their own — no explicit deflation. Rounding can leave one of them as a tiny
nonzero ``λ``, a finite-looking ``s``, so every candidate pole and zero is kept only where
``G + s·C`` is numerically singular (``_is_root``). Each ``K`` is equilibrated (rows, then
columns, divided by powers of two) before its condition test and solve; ``σ = 0`` is tried
first and a scaled shift is used when the equilibrated ``K`` is singular or has a condition
number above 1e14. Validated against a scipy QZ reference on a 13-node differential filter:
all 11 finite poles agreed to 7.3e-15 relative.

This is a *numeric* path — it needs every symbol but ``s`` bound, via ``numeric_subs`` or a
system already stamped numerically. For a symbolic answer on a circuit small enough to
afford one, use ``extract_tf`` + ``describe_tf``.
"""

from __future__ import annotations

import cmath
import math
from typing import cast

import numpy as np
import sympy as sp

from .contract import ComplexRoot, PoleZeroResult
from .ingest import _as_number
from .mna import _as_pair, _augment
from .model import MnaSystem
from .tf import S

__all__ = ["poles_zeros"]

_HUGE = 1e18  # |s| beyond this is the pencil's "infinite" eigenvalue, not a root
# A candidate pole or zero is kept when σ_min/σ_max of its matrix there is at most this
# fraction of the same ratio at generic points of the same modulus. Measured: a real root
# sits at <= 8e-6 of that floor (the fastest pole of an RC ladder spanning 13 decades; the
# rest <= 6e-10), a solver-made one (an infinite eigenvalue) at 0.14-0.54.
_ROOT_MARGIN = 1e-2
_PROBE_DIRECTIONS = tuple(cmath.exp(1j * t) for t in (1.19, 2.90, 4.66, 5.83))


def _affine_split(
    A: sp.Matrix, numeric_subs: dict[str, float] | None
) -> tuple[np.ndarray, np.ndarray]:
    """``A(s) = G + s·C`` as two float arrays, or a clear refusal if that is not exact."""
    # Bound by *name*: the minted symbols (gm_m1, ro_m1, …) are positive=True, and a plain
    # Symbol(name) key is a different symbol that would leave them unbound.
    values = numeric_subs or {}
    subs = {x: _as_number(float(values[str(x)])) for x in A.free_symbols if str(x) in values}
    n = A.shape[0]
    G = np.zeros((n, n))
    C = np.zeros((n, n))
    unbound: set[str] = set()
    split: list[tuple[int, int, sp.Expr, sp.Expr]] = []
    for i in range(n):
        for j in range(n):
            entry = cast("sp.Expr", sp.sympify(A[i, j]))
            e = sp.expand(entry.xreplace(subs) if subs else entry)
            if e.is_zero:
                continue
            g = cast("sp.Expr", sp.sympify(e.coeff(S, 0)))
            c = cast("sp.Expr", sp.sympify(e.coeff(S, 1)))
            if sp.simplify(e - (g + S * c)) != 0:
                raise NotImplementedError(
                    f"entry [{i},{j}] is not affine in s ({e}) — the pencil path needs "
                    f"Y(s) = G + s·C exactly. An inductor stamps 1/(s·L), which is not; "
                    f"use extract_tf + describe_tf for circuits containing one."
                )
            unbound |= {str(x) for x in (g.free_symbols | c.free_symbols) if x != S}
            split.append((i, j, g, c))
    if unbound:
        raise ValueError(
            "cannot solve the pencil numerically — unbound symbols remain: "
            f"{sorted(unbound)}. Pass numeric_subs={{...}} binding them, or build the "
            "system with subs= so it is stamped numerically."
        )
    for i, j, g, c in split:
        G[i, j], C[i, j] = float(g), float(c)
    return G, C


def _equilibrate(K: np.ndarray, C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``(D_r·K·D_c, D_r·C·D_c)``: each row of ``K``, then each column, divided by the power
    of two nearest its largest entry.

    ``(D_r K D_c)⁻¹ (D_r C D_c) = D_c⁻¹ (K⁻¹C) D_c`` has the eigenvalues of ``K⁻¹C``, and
    powers of two scale without rounding. A zero row or column is left as it is: ``K`` is
    then singular at this shift, and the condition test rejects it.
    """
    for axis in (1, 0):
        m = np.abs(K).max(axis=axis)
        d = np.exp2(-np.round(np.log2(np.where(m > 0, m, 1.0))))
        d = d[:, None] if axis == 1 else d[None, :]
        K, C = K * d, C * d
    return K, C


def _finite_eigenvalues(G: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Finite ``s`` with ``det(G + s·C) = 0``, by numpy shift-and-invert (see module docstring)."""
    if G.shape[0] == 0:
        return np.empty(0, dtype=complex)
    nG, nC = np.linalg.norm(G, "fro"), np.linalg.norm(C, "fro")
    if nC == 0:
        return np.empty(0, dtype=complex)  # no state: no finite pole
    scale = nG / nC if nG > 0 else 1.0
    last: Exception | None = None
    for sigma in (0.0, scale, -2.7 * scale, 11.3 * scale, -37.1 * scale):
        # Equilibrated before the condition test and the solve. An RC ladder with time
        # constants over 14 decades has cond(G) = 2.3e14 unscaled, so σ = 0 was skipped and
        # the shift ‖G‖/‖C‖ put the slowest pole 1.3 % off; scaled, cond is 15
        # (MacAnalog/spicexplorer-platform#303).
        K, Ck = _equilibrate(G + sigma * C, C)
        try:
            if np.linalg.cond(K) > 1e14:
                continue
            lam = np.linalg.eigvals(np.linalg.solve(K, Ck))
        except np.linalg.LinAlgError as exc:  # singular K — try the next shift
            last = exc
            continue
        if lam.size == 0:
            return np.empty(0, dtype=complex)
        # λ = 0 is an infinite eigenvalue of the pencil; it deflates itself. No cut relative
        # to the largest |λ|: that dropped real poles more than 12 decades above the slowest
        # one. A rounding-made λ is removed by the singularity check in poles_zeros instead.
        s = sigma - 1.0 / lam[lam != 0]
        return s[np.isfinite(s) & (np.abs(s) < _HUGE)]
    raise np.linalg.LinAlgError(
        "no usable shift found — the pencil (G, C) looks singular for every trial shift, "
        "which means the system has no unique solution (check the netlist topology)."
    ) from last


def _sv_ratio(G: np.ndarray, C: np.ndarray, s: complex) -> float:
    """σ_min / σ_max of ``G + s·C``: 0 exactly where ``s`` is a root of ``det(G + s·C)``."""
    sv = np.linalg.svd(G + s * C, compute_uv=False)
    return float(sv[-1] / sv[0]) if sv[0] > 0 else 0.0


def _is_root(G: np.ndarray, C: np.ndarray, s: complex, scale: float) -> bool:
    """True when ``G + s·C`` is numerically singular at ``s``.

    ``σ_min/σ_max`` alone cannot decide it: far above the circuit's own frequencies ``s·C``
    dominates, and ``C`` is rank-deficient, so the ratio is tiny at every point of that
    modulus (3e-29 at 3e16 rad/s on a 3-section RC ladder). The ratio at ``s`` is therefore
    compared with its median at generic points of the same modulus. The modulus is at least
    ``scale = ‖G‖/‖C‖``, so a zero at or near ``s = 0`` (a high-pass) is compared with the
    ratio where ``G`` and ``s·C`` are of one size, not with the singular ``G`` itself.
    """
    m = max(abs(s), scale)
    floor = float(np.median([_sv_ratio(G, C, m * u) for u in _PROBE_DIRECTIONS]))
    return _sv_ratio(G, C, s) <= _ROOT_MARGIN * floor


def _verified(G: np.ndarray, C: np.ndarray, roots: np.ndarray) -> np.ndarray:
    """The candidate ``roots`` at which ``G + s·C`` really is singular (see :func:`_is_root`)."""
    if not roots.size:
        return roots
    scale = float(np.linalg.norm(G, "fro") / np.linalg.norm(C, "fro"))
    return np.array([z for z in roots if _is_root(G, C, complex(z), scale)], dtype=complex)


def _transfer_is_zero(G: np.ndarray, C: np.ndarray, b: np.ndarray, L: np.ndarray) -> bool:
    """True when ``H(s) = Lᵀ(G + s·C)⁻¹b`` is identically zero (the bordered pencil is singular).

    That is a legitimate answer, not a failure: driving a symmetric cell common-mode and
    observing it differentially is exactly that. ``extract_tf`` returns ``H = 0`` there, so we
    agree with it rather than raising. Judged on ``H`` itself at two generic points of modulus
    ``‖G‖/‖C‖``: the terms of ``Lᵀx`` must cancel to rounding (a regular pencil's ``H`` vanishes
    at finitely many ``s``, so two misses would be a coincidence). The bordered matrix's
    ``σ_min/σ_max`` near 1 rad/s, used before, is also tiny for a numerator that is merely small
    there: an ``s²`` numerator, or a 12-decade conductance spread, read as ``H ≡ 0``.
    """
    nG, nC = np.linalg.norm(G, "fro"), np.linalg.norm(C, "fro")
    scale = nG / nC if nG > 0 and nC > 0 else 1.0
    for u in _PROBE_DIRECTIONS[:2]:
        terms = L * np.linalg.solve(G + scale * u * C, b)
        if abs(terms.sum()) > 1e-12 * np.abs(terms).sum():
            return False
    return True


def _root(s: complex) -> ComplexRoot:
    """One eigenvalue as a :class:`ComplexRoot`, with the ω₀/Q a designer reads off it."""
    w0 = abs(s)
    return ComplexRoot(
        expr=str(complex(s)),
        value_real=float(s.real),
        value_imag=float(s.imag),
        frequency_hz=float(w0 / (2 * math.pi)),
        q=float(w0 / (2 * abs(s.real))) if s.real != 0 else None,
    )


def _dedupe(roots: np.ndarray, tol: float = 1e-9) -> list[ComplexRoot]:
    """Sort by frequency and fold numerically-equal eigenvalues into one multiplicity."""
    vals: list[complex] = []
    mults: list[int] = []
    for raw in sorted(roots, key=lambda z: (abs(z), z.imag)):
        z = complex(raw)
        if vals and abs(vals[-1] - z) <= tol * max(abs(vals[-1]), abs(z), 1.0):
            mults[-1] += 1
            continue
        vals.append(z)
        mults.append(1)
    out: list[ComplexRoot] = []
    for z, mult in zip(vals, mults, strict=True):
        root = _root(z)
        root.multiplicity = mult
        out.append(root)
    return out


def poles_zeros(
    system: MnaSystem,
    output,  # noqa: ANN001 — PortLike
    input,  # noqa: ANN001 — PortLike
    *,
    drive: str = "dm",
    numeric_subs: dict[str, float] | None = None,
) -> PoleZeroResult:
    """Poles and zeros of ``H = V[output] / V[input]``, without ever forming a polynomial.

    Same ports, same ``drive`` convention and same ``numeric_subs`` as :func:`extract_tf` —
    this is its numeric counterpart for systems too large for a symbolic determinant. See the
    module docstring for when that is.

    The augmented matrix ``A(s)`` of the driven system supplies both answers: the **poles**
    are the finite eigenvalues of its pencil, and the **zeros** are those of ``A`` bordered
    with the output selector, ``M = [[A, rhs], [Lᵀ, 0]]``, whose determinant is the
    numerator of Cramer's rule. Because the input coupling stays inside ``A``, feed-through
    zeros (an input capacitance driving the output directly) land where they belong.

    The two lists are reported as computed, *not* cross-cancelled: a root appearing in both
    is a genuine pole–zero cancellation of the topology, and seeing it is usually the point.
    Compare them if you want the reduced ZPK. When the transfer is identically zero (a
    differential output under ``drive="cm"``, say) ``zeros`` is empty and ``dc_gain`` is 0 —
    the same answer ``extract_tf`` gives.

    Returns a :class:`PoleZeroResult`; ``poles``/``zeros`` are sorted by ``|s|`` with
    ``frequency_hz`` and ``q`` filled in, and repeated roots folded into ``multiplicity``.
    """
    if drive not in ("dm", "cm"):
        raise ValueError(f"drive must be 'dm' or 'cm', got {drive!r}")
    out = _as_pair(output, system)
    inp = _as_pair(input, system)
    A, rhs = _augment(system, inp, drive)

    G, C = _affine_split(A, numeric_subs)
    n = A.shape[0]

    # Output selector over the augmented unknowns: +1 on out.pos, −1 on out.neg.
    L = np.zeros(n)
    for net, sign in ((out.pos, 1.0), (out.neg, -1.0)):
        r = system.row_of(net)
        if r is not None:
            L[r] += sign
    if not L.any():
        raise ValueError(
            f"output port {(out.pos, out.neg)} is entirely at AC ground — nothing to observe"
        )

    # rhs is s-free by construction (the augmentation stamps constant source levels).
    b = np.array([float(cast("sp.Expr", sp.sympify(x))) for x in rhs], dtype=float)
    Gm = np.zeros((n + 1, n + 1))
    Cm = np.zeros((n + 1, n + 1))
    Gm[:n, :n], Cm[:n, :n] = G, C
    Gm[:n, n] = b
    Gm[n, :n] = L

    poles = _verified(G, C, _finite_eigenvalues(G, C))
    # H ≡ 0 (e.g. a differential output under cm drive) makes the bordered pencil singular:
    # report no zeros, matching extract_tf, rather than failing on a degenerate eigenproblem.
    zeros = (
        np.empty(0, dtype=complex) if _transfer_is_zero(G, C, b, L) else _finite_eigenvalues(Gm, Cm)
    )
    # A constant numerator leaves the bordered pencil with only infinite eigenvalues, and the
    # solver returns some of them as finite ones (±3e16j on an RC ladder). Keep a zero only
    # where the bordered matrix really is singular.
    zeros = _verified(Gm, Cm, zeros)

    # DC gain from the same matrices — one dense solve at s = 0, no extra machinery.
    try:
        dc = complex(L @ np.linalg.solve(G, b))
    except np.linalg.LinAlgError:
        dc = complex("nan")

    return PoleZeroResult(
        analysis="poles_zeros",
        output=f"{out.pos},{out.neg}",
        input=f"{inp.pos},{inp.neg}",
        drive=drive,
        poles=_dedupe(poles),
        zeros=_dedupe(zeros),
        dc_gain=None if cmath.isnan(dc) else float(dc.real),
        n_states=int(len(poles)),
    )
