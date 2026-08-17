"""Stage-4 simplification tests — the differentiator: typed assumptions, the phase pipeline, the
numeric-arbitration kernel, and the exact-vs-simplified validation gate."""

from __future__ import annotations

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    describe_tf,
    extract_tf,
    from_string,
    matched_pair,
    neglect_cgd,
    simplify_tf,
    small_signal_model,
    transconductance_dominates,
    validate_simplification,
)
from spicexplorer_netlist2tf.assumptions import Assumption, resolve
from spicexplorer_netlist2tf.model.ir import PortPair
from spicexplorer_netlist2tf.model.raw_tf import RawTransferFunction
from spicexplorer_netlist2tf.simplify import _apply_dominance
from spicexplorer_netlist2tf.tf import S, canonical_tf


def _raw(nl, out, inp, *, level=Fidelity.SOME_PARASITIC):
    ir = from_string(nl, name="c")
    system = build_system(small_signal_model(ir, level=level))
    return extract_tf(system, out, inp)


# ------------------------------------------------------------------------
# DOMINANCE — diode-loaded CS reduces to the textbook -gm1/gm2
# ------------------------------------------------------------------------
_DIODE = "* diode-loaded cs\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end"


def test_dominance_diode_load_textbook_form():
    raw = _raw(_DIODE, ("out", "0"), ("in", "0"))
    op = {"gm_m1": 1e-3, "gm_m2": 1e-3, "ro_m1": 2e5, "ro_m2": 2e5}
    res = simplify_tf(raw, transconductance_dominates("M2"), operating_point=op)
    gm1, gm2 = sp.Symbol("gm_m1", positive=True), sp.Symbol("gm_m2", positive=True)
    assert sp.simplify(res.expr - (-gm1 / gm2)) == 0
    assert res.validation is not None and res.validation.passed
    applied = [r for r in res.ledger if r.status == "APPLIED"]
    assert applied and applied[0].dropped_terms  # recorded what it dropped
    assert applied[0].numeric_ratio is not None and applied[0].numeric_ratio >= 100


def test_dominance_rejected_when_numbers_contradict():
    # Synthetic denominator gm + go where the op makes gm the SMALLER term → must REJECT, not apply.
    raw = RawTransferFunction(
        expr=canonical_tf(1 / (sp.Symbol("gm_m1", positive=True) + sp.Symbol("go", positive=True))),
        s=S, output=PortPair("o", "0"), input=PortPair("i", "0"),
    )
    a = transconductance_dominates("M1")  # claims gm_m1 dominates
    expr, rec = _apply_dominance(raw.expr, a, {"gm_m1": 1e-6, "go": 1e-3}, 100.0, 0)
    assert rec.status == "REJECTED_NUMERICS"
    assert expr == raw.expr  # nothing changed


# ------------------------------------------------------------------------
# SMALLNESS — neglect Cgd; validated when the cap is small, rejected when it matters
# ------------------------------------------------------------------------
_MILLER = "* cs miller\nM1 out in 0 0 nmos\nRL out 0 RL\n.end"


def test_smallness_neglect_cgd_validated():
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    op = {"gm_m1": 1e-3, "ro_m1": 2e5, "rl": 1e4,
          "cgs_m1": 1e-14, "cgd_m1": 1e-16, "cdb_m1": 1e-16, "csb_m1": 1e-16}
    res = simplify_tf(raw, neglect_cgd("M1"), operating_point=op)
    assert sp.Symbol("cgd_m1", positive=True) not in res.expr.free_symbols  # the cap is gone
    assert res.validation is not None and res.validation.passed and not res.unreduced
    assert any(r.status == "APPLIED" and r.kind == "SMALLNESS" for r in res.ledger)


def test_smallness_rejected_when_it_breaks_tolerance():
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    # A large Cgd contributes a real in-band pole/zero → neglecting it breaks the 5% gate → rolled back.
    op = {"gm_m1": 1e-3, "ro_m1": 2e5, "rl": 1e4,
          "cgs_m1": 1e-14, "cgd_m1": 1e-12, "cdb_m1": 1e-16, "csb_m1": 1e-16}
    res = simplify_tf(raw, neglect_cgd("M1"), operating_point=op)
    assert any(r.status == "REJECTED_VALIDATION" for r in res.ledger)
    assert res.expr == res.exact  # rolled back to exact — never ship an unvalidated approximation


# ------------------------------------------------------------------------
# EQUALITY — matched pair collapses the symbol count, losslessly
# ------------------------------------------------------------------------
_DP = ("* dp\nM1 outn vinp tail 0 nmos\nM2 outp vinn tail 0 nmos\n"
       "M3 outn outn vdd vdd pmos\nM4 outp outn vdd vdd pmos\nItail tail 0 dc ib\n.end")


def test_equality_matched_pair_collapses_symbols():
    raw = _raw(_DP, ("outp", "0"), ("vinp", "vinn"))
    res = simplify_tf(raw, matched_pair("M1", "M2"), validate=False)
    syms = {str(s) for s in res.expr.free_symbols}
    assert "gm_m2" not in syms and "ro_m2" not in syms  # M2 folded into M1
    assert "gm_m1" in syms
    assert any(r.status == "APPLIED" and r.kind == "EQUALITY" for r in res.ledger)


# ------------------------------------------------------------------------
# Phase ordering — EQUALITY (phase 0) always precedes DOMINANCE (phase 2)
# ------------------------------------------------------------------------
def test_phase_order_is_fixed():
    items = resolve([transconductance_dominates("M2"), matched_pair("M1", "M2")], set())
    ordered = sorted(items, key=lambda a: (a.phase, a.id))
    assert ordered[0].kind == "EQUALITY"
    assert ordered[-1].kind == "DOMINANCE"


# ------------------------------------------------------------------------
# Advisory mode — no assumptions asked → suggest what the op supports
# ------------------------------------------------------------------------
def test_advisory_suggests_supported_assumptions():
    raw = _raw(_DIODE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, "full")  # nothing applied
    assert res.expr == res.exact
    suggested = [r for r in res.ledger if r.status == "SUGGESTED"]
    assert any("gm_dominates" in r.name for r in suggested)


# ------------------------------------------------------------------------
# Validation helper directly
# ------------------------------------------------------------------------
def test_validate_simplification_flags_a_bad_reduction():
    exact = 1 / (1 + sp.Symbol("a") * S + sp.Symbol("b") * S**2)
    bad = sp.Integer(1)  # dropping all dynamics
    rep = validate_simplification(exact, bad, {"a": 1e-3, "b": 1e-7})
    assert rep.passed is False
    assert rep.max_relative_error is not None and rep.max_relative_error > 0.05


# ------------------------------------------------------------------------
# Bundle + end-to-end into the contract
# ------------------------------------------------------------------------
def test_simplify_feeds_contract_with_ledger():
    raw = _raw(_DIODE, ("out", "0"), ("in", "0"))
    op = {"gm_m1": 1e-3, "gm_m2": 1e-3, "ro_m1": 2e5, "ro_m2": 2e5}
    res = simplify_tf(raw, transconductance_dominates("M2"), operating_point=op)
    contract = describe_tf(raw, simplified=res, operating_point=op)
    assert contract.tf_exact_expr != contract.tf_simplified_expr  # exact AND simplified both present
    assert contract.tf_simplified_expr == "-gm_m1/gm_m2"
    assert contract.assumptions_applied  # the ledger is carried
    assert contract.validation is not None and contract.validation.passed


def test_unknown_assumption_kind_rejected():
    with pytest.raises(ValueError, match="unknown assumption kind"):
        Assumption(id="x", kind="BOGUS")
