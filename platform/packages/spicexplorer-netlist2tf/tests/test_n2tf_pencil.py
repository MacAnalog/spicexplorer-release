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


# ------------------------------------------------- the regression that matters


def test_pencil_survives_the_dynamic_range_that_breaks_np_roots():
    """The lesson, encoded: expanded-coefficient rooting loses roots; the pencil does not.

    An RC ladder whose sections span nine decades gives a denominator whose coefficients
    span far more. ``np.roots`` on those coefficients returns numbers that are not roots of
    the system at all — the residual test below is what catches it — while every pencil
    eigenvalue satisfies det(G + sC) = 0 to machine precision.
    """
    net = "\n".join(
        f"r{k} {'vin' if k == 0 else f'n{k}'} n{k + 1} {1e3 * 10 ** (3 * k):g}\n"
        f"c{k} n{k + 1} 0 {1e-9 / 10 ** (3 * k):g}"
        for k in range(4)
    ) + "\n.end"
    sysm = _system(net)
    out = ("n4", "0")

    pz = poles_zeros(sysm, out, ("vin", "0"))
    A, _ = _augment(sysm, _as_pair(("vin", "0"), sysm), "dm")
    G, C = _affine_split(A, None)

    pencil_res = [_residual(G, C, complex(p.value_real, p.value_imag)) for p in pz.poles]
    assert max(pencil_res) < 1e-12, f"pencil roots are not roots: {pencil_res}"

    # the expanded-polynomial path, on the same system
    den = sp.Poly(sp.expand(sp.fraction(sp.together(
        extract_tf(sysm, out, ("vin", "0")).expr))[1]), S)
    coeffs = [complex(c) for c in den.all_coeffs()]
    mags = [abs(c) for c in coeffs if c != 0]
    assert max(mags) / min(mags) > 1e20, "test circuit is not ill-conditioned enough"

    poly_res = [_residual(G, C, complex(z)) for z in np.roots(coeffs)]
    assert max(poly_res) > 1e3 * max(pencil_res), (
        "expected the expanded-coefficient path to lose roots the pencil keeps; "
        f"poly residuals {poly_res}, pencil residuals {pencil_res}"
    )


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
        "xq1 vout vin 0 0 some_unknown_pdk_thing w=1u l=1u\n"
        "r1 vout 0 1e6\nc1 vout 0 1e-12\n.end", name="t")
    ssir = small_signal_model(ir, level=Fidelity.FULL)
    assert ssir.unmodelled == ("XQ1",)

    clean = small_signal_model(
        from_string("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end", name="t"), level=Fidelity.FULL)
    assert clean.unmodelled == ()


def test_identically_zero_transfer_reports_no_zeros_like_extract_tf():
    """A symmetric cell driven cm and observed dm has H ≡ 0 — agree with extract_tf."""
    sysm = _system("r1 vip n1 1e3\nc1 n1 0 1e-9\nr2 vin n2 1e3\nc2 n2 0 1e-9\n.end")
    assert extract_tf(sysm, ("n1", "n2"), ("vip", "vin"), drive="cm").expr == 0

    pz = poles_zeros(sysm, ("n1", "n2"), ("vip", "vin"), drive="cm")
    assert pz.zeros == []
    assert pz.dc_gain == pytest.approx(0.0, abs=1e-12)
    assert pz.n_states == 2  # the poles are still the system's natural frequencies


def test_every_returned_root_is_actually_a_root():
    """Each root must sit far below the residual a *non*-root shows for the same pencil.

    σ_min/σ_max of ``G + sC`` is ~0 exactly at a root. Comparing against a floor probed at
    generic points is what separates a real root from an eigenvalue the shift-and-invert
    merely produced — checked here rather than filtered at runtime, because on real
    circuits (including deliberately capacitance-ablated ones) the margin is ~1e4 or
    better and a runtime filter would be complexity with nothing to catch.
    """
    # a feedforward cap across the series R puts a zero in H as well as a pole
    sysm = _system(
        "r1 vin n1 1e3\ncf vin n1 1e-12\nc1 n1 0 1e-9\n"
        "r2 n1 vout 1e5\ncf2 n1 vout 1e-13\nc2 vout 0 1e-11\n.end")
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
        floor = float(np.median([
            _residual(Gx, Cx, scale * z)
            for z in (0.37 + 0.93j, -1.7 + 0.41j, 0.11 - 2.3j, 3.1 + 1.7j)
        ]))
        worst = max(_residual(Gx, Cx, z) for z in rs)
        assert worst < floor / 100, (
            f"{kind} residual {worst:.2e} is not clearly below the non-root floor {floor:.2e}"
        )
