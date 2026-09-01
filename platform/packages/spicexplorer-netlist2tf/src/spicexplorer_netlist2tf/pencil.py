"""Poles and zeros straight from the MNA pencil — the path that survives real filters.

``describe_tf`` finds roots the textbook way: expand ``H(s)`` into numerator and
denominator polynomials and hand the coefficients to ``numpy.roots``. That is exact for
the small, hand-sized circuits Stage 4 is aimed at, and it is the right default because it
also works when the coefficients are still *symbolic*.

It stops working — quietly — on circuits that are merely medium-sized:

* **The determinant does not finish.** ``extract_tf`` computes a symbolic determinant, and
  at ``Fidelity.FULL`` a capacitance lands on nearly every branch. A 13-node cell with 16
  transistors takes minutes-to-never, and nothing about the call says so in advance.
* **Expansion destroys the roots you care about.** A 4th-order 250 Hz filter has a
  degree-15 denominator whose coefficients span tens of decades. Expanding it and rooting
  the coefficients loses the low-frequency poles to floating-point cancellation — the
  answer comes back confidently wrong, not as an error.

This module does neither. Every primitive the stamp emits is a conductance, a VCCS or
``s·C``, so the assembled matrix is **exactly affine in s**::

    Y(s) = G + s·C

and the poles are the finite generalized eigenvalues of the pencil ``(G, C)`` — a matrix
problem, with no polynomial ever formed and therefore no cancellation to lose them to.
Bordering the same matrix with the output selector gives the zeros the same way.

Numerics
--------
The eigenvalues come from ``numpy`` alone (no scipy, per the dependency charter) by
shift-and-invert: for any shift ``σ`` where ``K = G + σC`` is nonsingular,

    det(G + sC) = 0   ⇔   s = σ − 1/λ   for each nonzero eigenvalue λ of ``K⁻¹C``

and the zero eigenvalues of ``K⁻¹C`` are exactly the pencil's infinite eigenvalues, which
drop out on their own — no explicit deflation. ``σ = 0`` is tried first (the usual case,
since the source-constraint rows make ``G`` well-conditioned) and a scaled shift is used
when it is not. Validated against a scipy QZ reference on a 13-node differential filter:
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
from .mna import _as_pair, _augment
from .model import MnaSystem
from .tf import S

__all__ = ["poles_zeros"]

_HUGE = 1e18  # |s| beyond this is the pencil's "infinite" eigenvalue, not a root


def _affine_split(A: sp.Matrix, numeric_subs: dict[str, float] | None) -> tuple[np.ndarray, np.ndarray]:
    """``A(s) = G + s·C`` as two float arrays, or a clear refusal if that is not exact."""
    subs = {sp.Symbol(k): sp.Float(v) for k, v in (numeric_subs or {}).items()}
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
        K = G + sigma * C
        try:
            if np.linalg.cond(K) > 1e14:
                continue
            lam = np.linalg.eigvals(np.linalg.solve(K, C))
        except np.linalg.LinAlgError as exc:  # singular K — try the next shift
            last = exc
            continue
        if lam.size == 0:
            return np.empty(0, dtype=complex)
        # λ = 0 is an infinite eigenvalue of the pencil; it deflates itself.
        keep = np.abs(lam) > np.max(np.abs(lam)) * 1e-12
        s = sigma - 1.0 / lam[keep]
        return s[np.isfinite(s) & (np.abs(s) < _HUGE)]
    raise np.linalg.LinAlgError(
        "no usable shift found — the pencil (G, C) looks singular for every trial shift, "
        "which means the system has no unique solution (check the netlist topology)."
    ) from last



def _pencil_is_singular(G: np.ndarray, C: np.ndarray) -> bool:
    """True when ``det(G + sC) ≡ 0`` for *every* s — a singular pencil, not a regular one.

    For the bordered (zeros) matrix this means the transfer is identically zero, which is a
    legitimate answer, not a failure: driving a symmetric cell common-mode and observing it
    differentially is exactly that. ``extract_tf`` returns ``H = 0`` there, so we agree with
    it rather than raising. Tested at two generic shifts — a regular pencil is nonsingular
    at all but finitely many s, so two misses would be a coincidence.
    """
    scale = max(np.linalg.norm(G, "fro"), np.linalg.norm(C, "fro"), 1e-300)
    for sigma in (0.7231, -1.9137):
        sv = np.linalg.svd(G + sigma * scale * C, compute_uv=False)
        if sv.size == 0 or sv[-1] > sv[0] * 1e-12:
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
    this is its numeric counterpart for systems too large (or too wide in dynamic range)
    for a symbolic determinant. See the module docstring for when that is.

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

    poles = _finite_eigenvalues(G, C)
    # A singular bordered pencil means H ≡ 0 (e.g. a differential output under cm drive):
    # report no zeros, matching extract_tf, rather than failing on a degenerate eigenproblem.
    zeros = (
        np.empty(0, dtype=complex)
        if _pencil_is_singular(Gm, Cm)
        else _finite_eigenvalues(Gm, Cm)
    )

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
