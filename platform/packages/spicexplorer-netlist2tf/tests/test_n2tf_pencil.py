"""Pencil-based poles/zeros — agreement with the symbolic path, and the cancellation it fixes."""

from __future__ import annotations

import numpy as np
import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    describe_tf,
    extract_tf,
    from_string,
    poles_zeros,
    small_signal_model,
)
from spicexplorer_netlist2tf.mna import _as_pair, _augment
from spicexplorer_netlist2tf.pencil import _affine_split, _finite_eigenvalues
from spicexplorer_netlist2tf.tf import S


def _system(net: str, level: Fidelity = Fidelity.FULL):
    return build_system(small_signal_model(from_string(net, name="t"), level=level))


def _roots_of(res) -> np.ndarray:
    return np.array([complex(r.value_real, r.value_imag) for r in res])


def _residual(G: np.ndarray, C: np.ndarray, s: complex) -> float:
    """σ_min(G + sC) / ‖G + sC‖ — zero iff s really is a root of det(G + sC)."""
    M = G + s * C
    sv = np.linalg.svd(M, compute_uv=False)
    return float(sv[-1] / max(sv[0], 1e-300))


# ---------------------------------------------------------------- agreement


def test_single_pole_rc_matches_the_symbolic_path():
    """One RC: the pencil and extract_tf + describe_tf must agree on the pole."""
    sysm = _system("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end")
    pz = poles_zeros(sysm, ("vout", "0"), ("vin", "0"))
    ref = describe_tf(extract_tf(sysm, ("vout", "0"), ("vin", "0")))

    assert len(pz.poles) == 1
    got = complex(pz.poles[0].value_real, pz.poles[0].value_imag)
    want = complex(ref.poles[0].value_real, ref.poles[0].value_imag)
    assert got == pytest.approx(want, rel=1e-10)
    assert got.real == pytest.approx(-1 / (1e3 * 1e-9), rel=1e-10)  # −1/RC
    assert pz.dc_gain == pytest.approx(1.0, rel=1e-12)


def test_rlc_free_biquad_reports_f0_and_q():
    """Two poles of a loaded RC pair come back sorted, with frequency_hz and q filled in."""
    sysm = _system("r1 vin n1 1e3\nc1 n1 0 1e-9\nr2 n1 vout 1e3\nc2 vout 0 1e-9\n.end")
    pz = poles_zeros(sysm, ("vout", "0"), ("vin", "0"))
    assert len(pz.poles) == 2
    assert [abs(complex(p.value_real, p.value_imag)) for p in pz.poles] == sorted(
        abs(complex(p.value_real, p.value_imag)) for p in pz.poles
    )
    for p in pz.poles:
        assert p.frequency_hz > 0
        assert p.q == pytest.approx(0.5, rel=1e-9)  # both real → Q = 1/2


def test_dm_and_cm_drive_are_both_accepted():
    net = "r1 vip n1 1e3\nc1 n1 0 1e-9\nr2 vin n2 1e3\nc2 n2 0 1e-9\n.end"
    sysm = _system(net)
    for drive in ("dm", "cm"):
        pz = poles_zeros(sysm, ("n1", "n2"), ("vip", "vin"), drive=drive)
        assert pz.drive == drive
        # the two branches are identical, so the pole is repeated, not distinct
        assert pz.n_states == 2
        assert [p.multiplicity for p in pz.poles] == [2]
        assert pz.poles[0].value_real == pytest.approx(-1e6, rel=1e-9)
    with pytest.raises(ValueError, match="drive must be"):
        poles_zeros(sysm, ("n1", "n2"), ("vip", "vin"), drive="sideways")


# ------------------------------------ nine decades of RC: both paths find the roots


def test_pencil_and_exact_expansion_agree_across_nine_decades():
    """An RC ladder whose sections span nine decades: the pencil and the expanded path agree.

    The denominator's coefficients span 1e24. This test used to assert that ``np.roots`` on them
    returns numbers that are not roots of the system — but that failure was Float ingestion,
    not rooting: ``cancel`` over ``Float`` values left the coefficients wrong (``4.12e27`` for
    the exact ``4.003002001e27``) and the numerator a phantom degree 4 (audit LEAF-F06). With
    exact-Rational ingestion the coefficients are exact, and every root from either path
    satisfies det(G + sC) = 0 to machine precision — the residual test is what checks it.
    """
    net = (
        "\n".join(
            f"r{k} {'vin' if k == 0 else f'n{k}'} n{k + 1} {1e3 * 10 ** (3 * k):g}\n"
            f"c{k} n{k + 1} 0 {1e-9 / 10 ** (3 * k):g}"
            for k in range(4)
        )
        + "\n.end"
    )
    sysm = _system(net)
    out = ("n4", "0")

    pz = poles_zeros(sysm, out, ("vin", "0"))
    A, _ = _augment(sysm, _as_pair(("vin", "0"), sysm), "dm")
    G, C = _affine_split(A, None)

    pencil_res = [_residual(G, C, complex(p.value_real, p.value_imag)) for p in pz.poles]
    assert max(pencil_res) < 1e-12, f"pencil roots are not roots: {pencil_res}"

    # the expanded-polynomial path, on the same system
    num, den = (
        sp.Poly(sp.expand(x), S)
        for x in sp.fraction(sp.together(extract_tf(sysm, out, ("vin", "0")).expr))
    )
    assert (num.degree(), den.degree()) == (0, 4)  # Float ingestion gave a degree-4 numerator
    coeffs = [complex(c) for c in den.all_coeffs()]
    mags = [abs(c) for c in coeffs if c != 0]
    assert max(mags) / min(mags) > 1e20, "test circuit is not ill-conditioned enough"

    poly_roots = sorted(np.roots(coeffs), key=abs)
    poly_res = [_residual(G, C, complex(z)) for z in poly_roots]
    assert max(poly_res) < 1e-12, f"expanded-path roots are not roots: {poly_res}"
    assert poly_roots == pytest.approx(sorted(_roots_of(pz.poles), key=abs), rel=1e-9)


# ----------------------------------------------------------------- refusals


def test_inductor_is_refused_with_an_actionable_message():
    """1/(sL) is not affine in s — say so, and say what to use instead."""
    sysm = _system("r1 vin vout 1e3\nl1 vout 0 1e-3\n.end")
    with pytest.raises(NotImplementedError, match="not affine in s"):
        poles_zeros(sysm, ("vout", "0"), ("vin", "0"))


def test_unbound_symbols_are_named():
    ir = from_string("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end", name="t")
    sysm = build_system(small_signal_model(ir, level=Fidelity.FULL))
    A = sp.Matrix([[sp.Symbol("g_unknown"), 0], [0, S * sp.Symbol("c_unknown")]])
    with pytest.raises(ValueError, match="c_unknown.*g_unknown|g_unknown.*c_unknown"):
        _affine_split(A, None)
    # ...and binding them makes it work
    G, C = _affine_split(A, {"g_unknown": 2.0, "c_unknown": 3.0})
    assert G[0, 0] == 2.0 and C[1, 1] == 3.0
    del sysm


def test_numeric_subs_binds_the_minted_symbols():
    """``gm_m1``/``ro_m1`` are minted ``positive=True``; ``numeric_subs`` keyed them as plain
    ``Symbol(name)``, which is a different symbol, so they stayed unbound."""
    deck = "M1 out in 0 0 nmos\nRL out 0 10k\nCL out 0 1p\n.end"
    ops = {
        "gm_m1": 1e-3,
        "ro_m1": 1e5,
        "cgs_m1": 1e-14,
        "cgd_m1": 2e-15,
        "cdb_m1": 3e-15,
        "csb_m1": 1e-15,
        "gmb_m1": 1e-4,
    }
    ir = from_string(deck, name="t")
    symbolic = build_system(small_signal_model(ir, level=Fidelity.FULL))
    stamped = build_system(small_signal_model(ir, level=Fidelity.FULL), subs=ops)
    got = poles_zeros(symbolic, ("out", "0"), ("in", "0"), numeric_subs=ops)
    want = poles_zeros(stamped, ("out", "0"), ("in", "0"))
    assert got.n_states == want.n_states == 1
    assert _roots_of(got.poles) == pytest.approx(_roots_of(want.poles), rel=1e-12)
    assert _roots_of(got.zeros) == pytest.approx(_roots_of(want.zeros), rel=1e-12)
    assert got.dc_gain == pytest.approx(want.dc_gain, rel=1e-12)


def test_grounded_output_port_is_refused():
    sysm = _system("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end")
    with pytest.raises(ValueError, match="entirely at AC ground"):
        poles_zeros(sysm, ("0", "0"), ("vin", "0"))


def test_no_capacitance_means_no_finite_pole():
    assert _finite_eigenvalues(np.eye(2), np.zeros((2, 2))).size == 0


# ------------------------------------------------- unmodelled-device visibility


def test_unmodelled_devices_are_inspectable_not_just_logged():
    """A device no model can expand is absent from the MNA — expose it as a field."""
    ir = from_string(
        "xq1 vout vin 0 0 some_unknown_pdk_thing w=1u l=1u\nr1 vout 0 1e6\nc1 vout 0 1e-12\n.end",
        name="t",
    )
    ssir = small_signal_model(ir, level=Fidelity.FULL)
    assert ssir.unmodelled == ("XQ1",)

    clean = small_signal_model(
        from_string("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end", name="t"), level=Fidelity.FULL
    )
    assert clean.unmodelled == ()


def test_identically_zero_transfer_reports_no_zeros_like_extract_tf():
    """A symmetric cell driven cm and observed dm has H ≡ 0 — agree with extract_tf."""
    sysm = _system("r1 vip n1 1e3\nc1 n1 0 1e-9\nr2 vin n2 1e3\nc2 n2 0 1e-9\n.end")
    assert extract_tf(sysm, ("n1", "n2"), ("vip", "vin"), drive="cm").expr == 0

    pz = poles_zeros(sysm, ("n1", "n2"), ("vip", "vin"), drive="cm")
    assert pz.zeros == []
    assert pz.dc_gain == pytest.approx(0.0, abs=1e-12)
    assert pz.n_states == 2  # the poles are still the system's natural frequencies


# --------------------------------------- zeros: only where the bordered matrix is singular

_LADDER_3 = (
    "R1 in n1 1.3k\nC1 n1 0 2.7p\nR2 n1 n2 4.7k\nC2 n2 0 1.1p\nR3 n2 out 3.3k\nC3 out 0 0.47p\n.end"
)


def test_a_constant_numerator_reports_no_zeros():
    """An RC ladder's numerator is a constant, so it has no finite zero. The bordered pencil's
    eigenvalues are then all infinite, and the solver returned two of them as zeros at
    -2.06e8 ± 3.0e16j."""
    sysm = _system(_LADDER_3)
    num, _ = sp.fraction(sp.together(extract_tf(sysm, ("out", "0"), ("in", "0")).expr))
    assert sp.Poly(sp.expand(num), S).degree() == 0  # the premise: nothing to report
    pz = poles_zeros(sysm, ("out", "0"), ("in", "0"))
    assert pz.zeros == []
    assert len(pz.poles) == 3
    assert pz.dc_gain == pytest.approx(1.0, rel=1e-12)


@pytest.mark.parametrize(
    ("deck", "zero"),
    [
        # lead: the input cap feeds in straight to out, one zero at -1/(R1·C1) = -1e6 rad/s
        ("r1 in out 1k\nc1 in out 1n\nr2 out 0 1k\n.end", -1e6),
        # high-pass: the series cap puts the zero at s = 0
        ("c1 in out 1n\nr1 out 0 1k\n.end", 0.0),
    ],
    ids=["lead_feedthrough", "highpass_dc_zero"],
)
def test_a_real_finite_zero_is_kept(deck, zero):
    pz = poles_zeros(_system(deck), ("out", "0"), ("in", "0"))
    assert len(pz.zeros) == 1
    got = complex(_roots_of(pz.zeros)[0])
    assert got == pytest.approx(zero, abs=1.0)  # 1 rad/s: 1e-6 of the lead's 1e6 rad/s zero


def _wide_ladder(n: int, step: int, extra: str = "") -> str:
    """``n`` RC sections, R stepping up ``step`` decades per section from 1 Ω, every C 1 pF:
    time constants from 1 ps over ``n·step`` decades."""
    return (
        "\n".join(
            f"r{k} {'in' if k == 0 else f'n{k}'} {'out' if k == n - 1 else f'n{k + 1}'} "
            f"{10 ** (step * k):g}\nc{k} {'out' if k == n - 1 else f'n{k + 1}'} 0 1e-12"
            for k in range(n)
        )
        + extra
        + "\n.end"
    )


def _exact_roots(poly_expr) -> list[complex]:  # noqa: ANN001
    roots = sp.Poly(sp.expand(poly_expr), S).nroots(n=30, maxsteps=200)
    return sorted((complex(z) for z in roots), key=lambda z: (abs(z), z.imag))


@pytest.mark.parametrize(
    ("deck", "n_zeros"),
    [
        # numerator s²: the singularity probe at |s| ≈ 1 rad/s read it as H ≡ 0
        ("c1 in n1 1n\nr1 n1 0 1k\nc2 n1 out 1n\nr2 out 0 1k\n.end", 2),
        # 12 decades of conductance plus a feed-through cap (zeros from 1.1e3 to 1e12 rad/s): the
        # same probe read H ≡ 0 again
        (_wide_ladder(4, 4, "\ncf in out 1e-15"), 4),
    ],
    ids=["double_dc_zero", "twelve_decade_spread"],
)
def test_zeros_survive_a_numerator_that_is_small_near_1_rad_s(deck, n_zeros):
    sysm = _system(deck)
    num, _ = sp.fraction(sp.together(extract_tf(sysm, ("out", "0"), ("in", "0")).expr))
    want = _exact_roots(num)
    assert len(want) == n_zeros  # the premise
    pz = poles_zeros(sysm, ("out", "0"), ("in", "0"))
    got = sorted(
        (z for r in pz.zeros for z in [complex(_roots_of([r])[0])] * r.multiplicity),
        key=lambda z: (abs(z), z.imag),
    )
    assert got == pytest.approx(want, rel=1e-6, abs=1.0)  # abs: DC zeros land within 1 rad/s


@pytest.mark.parametrize(("n", "step"), [(5, 3), (4, 4)])
def test_poles_over_more_than_twelve_decades_are_all_reported(n, step):
    """Time constants from 1 ps to 1 s: the eigenvalue cut at 1e-12 of the largest |λ| dropped
    the fastest pole (4 of 5, 3 of 4 reported)."""
    sysm = _system(_wide_ladder(n, step))
    _, den = sp.fraction(sp.together(extract_tf(sysm, ("out", "0"), ("in", "0")).expr))
    want = _exact_roots(den)
    pz = poles_zeros(sysm, ("out", "0"), ("in", "0"))
    got = sorted(_roots_of(pz.poles), key=lambda z: (abs(z), z.imag))
    assert pz.n_states == len(want) == n
    assert got == pytest.approx(want, rel=1e-4)  # measured 8.2e-11 (5, 3) and 4.9e-8 (4, 4)


def test_poles_over_fourteen_decades_are_solved_unshifted():
    """Eight sections, R stepping 2 decades from 1 Ω, every C 1 pF: cond(G) = 2.3e14. Without
    equilibration σ = 0 failed the 1e14 condition test, the shift ‖G‖/‖C‖ put the slowest pole
    at -9.766e-3 rad/s against the exact -9.899e-3 (1.3 %), and the bordered pencil for the
    zeros found no usable shift, so ``poles_zeros`` raised (MacAnalog/spicexplorer-platform#303).
    """
    sysm = _system(_wide_ladder(8, 2))
    _, den = sp.fraction(sp.together(extract_tf(sysm, ("out", "0"), ("in", "0")).expr))
    want = _exact_roots(den)
    A, _ = _augment(sysm, _as_pair(("in", "0"), sysm), "dm")
    G, C = _affine_split(A, None)
    assert np.linalg.cond(G) > 1e14  # the premise: σ = 0 is refused without equilibration
    pencil = sorted(_finite_eigenvalues(G, C), key=lambda z: (abs(z), z.imag))
    assert pencil == pytest.approx(want, rel=1e-4)  # measured 2.0e-7

    pz = poles_zeros(sysm, ("out", "0"), ("in", "0"))
    assert pz.n_states == len(want) == 8
    got = sorted(_roots_of(pz.poles), key=lambda z: (abs(z), z.imag))
    assert got == pytest.approx(want, rel=1e-4)
    assert pz.zeros == []  # a ladder's numerator is a constant
    assert pz.dc_gain == pytest.approx(1.0, rel=1e-9)


def test_every_returned_root_is_actually_a_root():
    """Each root must sit far below the residual a *non*-root shows for the same pencil.

    σ_min/σ_max of ``G + sC`` is ~0 exactly at a root. Comparing against a floor probed at
    generic points is what separates a real root from an eigenvalue the shift-and-invert
    merely produced. ``poles_zeros`` applies that test to every candidate pole and zero at
    runtime (a constant numerator otherwise reports the solver's infinite eigenvalues as
    zeros); this test checks the result against a wider margin, 100x below the floor.
    """
    # a feedforward cap across the series R puts a zero in H as well as a pole
    sysm = _system(
        "r1 vin n1 1e3\ncf vin n1 1e-12\nc1 n1 0 1e-9\n"
        "r2 n1 vout 1e5\ncf2 n1 vout 1e-13\nc2 vout 0 1e-11\n.end"
    )
    out, inp = ("vout", "0"), ("vin", "0")
    pz = poles_zeros(sysm, out, inp)

    A, rhs = _augment(sysm, _as_pair(inp, sysm), "dm")
    G, C = _affine_split(A, None)
    n = A.shape[0]
    L = np.zeros(n)
    L[sysm.row_of("vout")] = 1.0
    b = np.array([float(sp.sympify(x)) for x in rhs], dtype=float)
    Gm, Cm = np.zeros((n + 1, n + 1)), np.zeros((n + 1, n + 1))
    Gm[:n, :n], Cm[:n, :n] = G, C
    Gm[:n, n], Gm[n, :n] = b, L

    for kind, roots, (Gx, Cx) in (("pole", pz.poles, (G, C)), ("zero", pz.zeros, (Gm, Cm))):
        rs = [complex(r.value_real, r.value_imag) for r in roots]
        assert rs, f"expected at least one {kind} in this circuit"
        scale = float(np.median([abs(z) for z in rs]))
        floor = float(
            np.median(
                [
                    _residual(Gx, Cx, scale * z)
                    for z in (0.37 + 0.93j, -1.7 + 0.41j, 0.11 - 2.3j, 3.1 + 1.7j)
                ]
            )
        )
        worst = max(_residual(Gx, Cx, z) for z in rs)
        assert worst < floor / 100, (
            f"{kind} residual {worst:.2e} is not clearly below the non-root floor {floor:.2e}"
        )
