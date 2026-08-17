"""Singularity, nesting, reuse, and partial-information edges (test-suite review 2026-06-11,
items 6/12 + backlog)."""

from __future__ import annotations

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    build_system,
    extract_tf,
    from_string,
    simplify_tf,
    small_signal_model,
    transconductance_dominates,
)


def _tf(netlist: str, output, input_):
    ir = from_string(netlist)
    return extract_tf(build_system(small_signal_model(ir)), output, input_)


# ── degenerate elements / singular systems ────────────────────────────────────────────────────
def test_zero_resistance_raises_not_nan():
    """R=0 used to flow 1/0 → sympy `zoo` → a silent NaN transfer function. It must be a loud,
    device-named error instead."""
    with pytest.raises(ValueError, match="R1.*zero-resistance"):
        _tf("* short\nV1 in 0 dc 0 ac 1\nR1 in mid 0\nR2 mid 0 1k\n.end",
            ("mid", "0"), ("in", "0"))


def test_parallel_inductor_loop_is_solvable():
    """Two inductors in parallel (an L-only 'loop') is a regular system, not a singularity:
    H = R/(R + s·L∥) with a pole at R/L∥ = 2e9 rad/s."""
    raw = _tf("* L\nV1 in 0 dc 0 ac 1\nL1 in out 1u\nL2 out in 1u\nR1 out 0 1k\n.end",
              ("out", "0"), ("in", "0"))
    s = sp.Symbol("s")
    expr = sp.nsimplify(raw.expr, rational=False)
    pole = sp.solve(sp.denom(sp.together(expr)), s)
    assert pole and abs(complex(pole[0]).real + 2e9) / 2e9 < 1e-6


# ── system reuse ──────────────────────────────────────────────────────────────────────────────
def test_two_transfer_functions_from_one_system():
    """One MNA build serves multiple extractions — the staged API's whole point."""
    ir = from_string("* rc\nV1 in 0 dc 0 ac 1\nR1 in out 1k\nC1 out 0 100p\n.end")
    system = build_system(small_signal_model(ir))
    h_out = extract_tf(system, ("out", "0"), ("in", "0"))
    h_in = extract_tf(system, ("in", "0"), ("in", "0"))
    s = sp.Symbol("s")
    assert sp.simplify(sp.sympify(str(h_in.expr)) - 1) == 0          # driven node: unity
    assert float(sp.sympify(str(h_out.expr)).subs(s, 0)) == pytest.approx(1.0)   # RC at DC
    # and the first extraction is unchanged by the second (no shared-state corruption)
    h_out2 = extract_tf(system, ("out", "0"), ("in", "0"))
    assert str(h_out2.expr) == str(h_out.expr)


# ── deep nesting + param expressions through ingest ───────────────────────────────────────────
def test_three_level_subckt_flatten_accumulates_postfixes():
    nl = """* 3-level nesting
.subckt level3 a b
R3 a b 1k
.ends
.subckt level2 a b
X3 a b level3
C2 a 0 1p
.ends
.subckt level1 a b
X2 a b level2
.ends
V1 in 0 dc 0 ac 1
X1 in out level1
RL out 0 10k
.end"""
    ir = from_string(nl)
    refs = sorted(d.ref for d in ir.devices)
    assert refs == ["C2_X2_X1", "R3_X3_X2_X1", "RL", "V1"]           # instance-path postfixes
    raw = extract_tf(build_system(small_signal_model(ir)), ("out", "0"), ("in", "0"))
    s = sp.Symbol("s")
    assert sp.sympify(str(raw.expr)).subs(s, 0) == sp.Rational(10, 11)   # 10k/(1k+10k) at DC


def test_brace_param_expression_stays_symbolic():
    """`R1 … {1k*W}` keeps the value symbolic (`r1_value`) instead of mis-evaluating — pinned so
    parameterized netlists never silently get a wrong number."""
    raw = _tf("* par\n.param W=2\nV1 in 0 dc 0 ac 1\nR1 in out {1k*W}\nC1 out 0 100p\n.end",
              ("out", "0"), ("in", "0"))
    assert "r1_value" in str(raw.expr)


# ── simplification with partial operating points ──────────────────────────────────────────────
def test_simplify_with_missing_op_symbols_does_not_nan():
    """An operating point missing the symbols an assumption needs must not NaN-propagate: the
    arbiter falls back to coarse defaults and still produces the validated hand-form (current
    contract — if defaulting is ever made stricter, this test changes consciously)."""
    raw = _tf("* cs\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end",
              ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, transconductance_dominates("M2"),
                      operating_point={"gm_m1": 1e-3})               # gm_m2 / ro_* absent
    assert str(res.expr) == "-gm_m1/gm_m2"
    (step,) = res.ledger
    assert step.status == "APPLIED" and "nan" not in str(res.expr).lower()
