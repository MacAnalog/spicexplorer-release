"""Exact-Rational ingestion (audit LEAF-F06) and the retired ``numeric_refit`` solve path.

Netlist numbers used to ingest as sympy ``Float``s. ``cancel`` over floats cannot cancel exactly, so
the round-off residue survived as tiny leading coefficients (``7e-23·s²`` over a numerator that is
really a constant) and ``describe_tf`` rooted them into phantom poles and zeros at 1e18..1e32 rad/s
— a passive RC ladder reported two zeros it does not have, and a capacitor loop a fourth pole.
Ingesting the decimal value as an exact ``Rational`` keeps ``cancel`` exact; numbers become floats
only where they are evaluated (describe / numeric / pencil).
"""

from __future__ import annotations

import pydantic
import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    TransferFunctionResult,
    build_system,
    from_string,
    poles_zeros,
    small_signal_model,
    transfer_function,
)
from spicexplorer_netlist2tf.contract import SymbolicValue
from spicexplorer_netlist2tf.ingest import sympify_value
from spicexplorer_netlist2tf.tf import S, as_num_den

# Three RC sections with deliberately "untidy" decimal values: 1.3k, 2.7p, 4.7k, …
LADDER = """* rc ladder
R1 in n1 1.3k
C1 n1 0 2.7p
R2 n1 n2 4.7k
C2 n2 0 1.1p
R3 n2 out 3.3k
C3 out 0 0.47p
.end
"""
# C4 closes the loop C1-C4-C3 through ground: four capacitors, three independent states.
CAP_LOOP = LADDER.replace(".end", "C4 n1 out 0.33p\n.end")


def _roots(roots) -> list[complex]:
    return sorted((complex(r.value_real, r.value_imag) for r in roots), key=abs)


def _pencil_poles(deck: str) -> list[complex]:
    system = build_system(small_signal_model(from_string(deck, name="t")))
    return _roots(poles_zeros(system, ("out", "0"), ("in", "0")).poles)


def test_rc_ladder_is_a_constant_over_three_lhp_poles_matching_the_pencil():
    """The audit's acceptance as one conjunction. Float ingestion already got the poles right; the
    numerator it did not (degree 2, zeros at ±3.7e18j), so the degree assert is the one that bites."""
    res = transfer_function(LADDER, ("out", "0"), ("in", "0"))
    num, den = (sp.Poly(x, S) for x in as_num_den(res.as_sympy_exact()))
    assert (num.degree(), den.degree()) == (0, 3)
    assert res.zeros == []
    poles = _roots(res.poles)
    assert len(poles) == 3
    assert all(p.real < 0 and p.imag == 0 for p in poles)
    assert poles == pytest.approx(_pencil_poles(LADDER), rel=1e-9)
    assert res.dc_gain.value == pytest.approx(1.0, rel=1e-12)


def test_capacitor_loop_reports_three_finite_poles_not_four():
    res = transfer_function(CAP_LOOP, ("out", "0"), ("in", "0"))
    assert sp.Poly(as_num_den(res.as_sympy_exact())[1], S).degree() == 3
    poles = _roots(res.poles)
    assert len(poles) == 3 and all(abs(p) < 1e12 for p in poles)  # no ±1e20..1e32 phantom
    assert all(p.real < 0 for p in poles)
    assert poles == pytest.approx(_pencil_poles(CAP_LOOP), rel=1e-9)
    zeros = _roots(res.zeros)  # C4 feeds n1 straight to out: one conjugate pair, nothing else
    assert len(zeros) == 2 and zeros[0] == pytest.approx(zeros[1].conjugate(), rel=1e-12)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2.7p", sp.Rational(27, 10**13)),
        ("1.3k", sp.Integer(1300)),
        ("0.47p", sp.Rational(47, 10**14)),
        ("25mil", sp.Rational(127, 200000)),  # ngspice's thousandth of an inch, 25.4e-6 each
        ("-2.5m", sp.Rational(-1, 400)),
        (1.5, sp.Rational(3, 2)),
        ("1e16", sp.Integer(10**16)),
    ],
)
def test_numeric_tokens_ingest_as_exact_rationals(raw, expected):
    value = sympify_value(raw)
    assert value == expected and not isinstance(value, sp.Float)


def test_a_passive_deck_ingests_no_float_anywhere():
    ir = from_string(CAP_LOOP, name="t")
    values = [d.params["value"] for d in ir.devices]
    assert values and not any(v.atoms(sp.Float) for v in values)
    assert not transfer_function(ir, ("out", "0"), ("in", "0")).as_sympy_exact().atoms(sp.Float)


def test_a_nan_float_is_still_a_value_error():
    with pytest.raises(ValueError):
        sympify_value(float("nan"))


# ------------------------------------------------------------------------
# subs=: numbers substituted before the determinant are exact too (B-PF-3)
# ------------------------------------------------------------------------
_SYMBOLIC_LADDER = LADDER.replace("1.3k", "RA").replace("2.7p", "CA")
_LADDER_SUBS = {"ra": 1300.0, "ca": 2.7e-12}


def test_subs_before_the_determinant_keeps_the_ladder_numerator_constant():
    """``subs=`` stamped ``sp.Float`` values, so ``cancel`` left round-off in the numerator: the
    passive ladder got a degree-3 numerator with zeros at 1.65e15 ± 2.86e15j (right half plane)
    and -3.3e15. The same deck written numerically has none."""
    res = transfer_function(_SYMBOLIC_LADDER, ("out", "0"), ("in", "0"), subs=_LADDER_SUBS)
    assert res.solve_path == "selectively_numericized"
    exact = res.as_sympy_exact()
    assert not exact.atoms(sp.Float)
    num, den = (sp.Poly(x, S) for x in as_num_den(exact))
    assert (num.degree(), den.degree()) == (0, 3)
    assert res.zeros == []
    assert _roots(res.poles) == pytest.approx(_pencil_poles(LADDER), rel=1e-9)


def test_pencil_numeric_subs_matches_the_numeric_deck():
    """Guard for the pencil's own ``numeric_subs=`` site (it evaluates in floats either way)."""
    system = build_system(small_signal_model(from_string(_SYMBOLIC_LADDER, name="t")))
    res = poles_zeros(system, ("out", "0"), ("in", "0"), numeric_subs=_LADDER_SUBS)
    assert _roots(res.poles) == pytest.approx(_pencil_poles(LADDER), rel=1e-9)
    assert res.dc_gain == pytest.approx(1.0, rel=1e-12)


# ------------------------------------------------------------------------
# solve_path: the two regimes that are produced, and nothing else
# ------------------------------------------------------------------------
def _result(solve_path: str) -> TransferFunctionResult:
    return TransferFunctionResult(
        output_nodes=("out", "0"),
        input_nodes=("in", "0"),
        solve_path=solve_path,  # type: ignore[arg-type]  # the point: any str reaches the check
        tf_exact_expr="1",
        tf_simplified_expr="1",
        dc_gain=SymbolicValue(expr="1"),
    )


@pytest.mark.parametrize("solve_path", ["fully_symbolic", "selectively_numericized"])
def test_contract_accepts_the_produced_solve_paths(solve_path):
    assert _result(solve_path).solve_path == solve_path


@pytest.mark.parametrize("solve_path", ["numeric_refit", "anything_else"])
def test_contract_rejects_a_solve_path_nothing_produces(solve_path):
    """``numeric_refit`` was reserved but never produced: a consumer branching on it branched on
    a case that cannot occur."""
    with pytest.raises(pydantic.ValidationError, match="solve_path"):
        _result(solve_path)
