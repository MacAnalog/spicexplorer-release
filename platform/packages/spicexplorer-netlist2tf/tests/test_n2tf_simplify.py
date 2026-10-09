"""Stage-4 simplification tests — the differentiator: typed assumptions, the phase pipeline, the
numeric-arbitration kernel, and the exact-vs-simplified validation gate."""

from __future__ import annotations

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    describe_tf,
    dominant_pole,
    extract_tf,
    from_string,
    inband,
    matched_pair,
    neglect_cgd,
    simplify_tf,
    small_signal_model,
    transconductance_dominates,
    validate_simplification,
)
from spicexplorer_netlist2tf import simplify as simplify_module
from spicexplorer_netlist2tf.assumptions import Assumption, neglect_cap, resolve
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
        s=S,
        output=PortPair("o", "0"),
        input=PortPair("i", "0"),
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
    op = {
        "gm_m1": 1e-3,
        "ro_m1": 2e5,
        "rl": 1e4,
        "cgs_m1": 1e-14,
        "cgd_m1": 1e-16,
        "cdb_m1": 1e-16,
        "csb_m1": 1e-16,
    }
    res = simplify_tf(raw, neglect_cgd("M1"), operating_point=op)
    assert sp.Symbol("cgd_m1", positive=True) not in res.expr.free_symbols  # the cap is gone
    assert res.validation is not None and res.validation.passed and not res.unreduced
    assert any(r.status == "APPLIED" and r.kind == "SMALLNESS" for r in res.ledger)


def test_a_nan_step_error_is_rejected_not_validated(monkeypatch):
    """``nan > tolerance`` is False, so a step whose error came back NaN was recorded APPLIED and
    validated. It must be rolled back like any step that fails the gate; the other step stays."""
    real = simplify_module._relative_error

    def nan_for_the_cgd_step(exact, simplified, op, freqs):  # noqa: ANN001
        if "cgd_m1" not in {str(x) for x in simplified.free_symbols}:
            return float("nan")
        return real(exact, simplified, op, freqs)

    monkeypatch.setattr(simplify_module, "_relative_error", nan_for_the_cgd_step)
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    op = {
        "gm_m1": 1e-3,
        "ro_m1": 2e5,
        "rl": 1e4,
        "cgs_m1": 1e-14,
        "cgd_m1": 1e-16,
        "cdb_m1": 1e-16,
        "csb_m1": 1e-16,
    }
    res = simplify_tf(raw, [neglect_cap("M1", "cdb"), neglect_cgd("M1")], operating_point=op)
    by_name = {r.name: r for r in res.ledger}
    cgd, cdb = by_name["neglect_cgd:M1"], by_name["neglect_cdb:M1"]
    assert cgd.status == "REJECTED_VALIDATION" and cgd.validated is False
    assert cdb.status == "APPLIED" and cdb.validated is True
    names = {str(x) for x in res.expr.free_symbols}
    assert "cgd_m1" in names and "cdb_m1" not in names  # only the NaN step was rolled back
    assert res.unreduced is False


def test_smallness_rejected_when_it_breaks_tolerance():
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    # A large Cgd contributes a real in-band pole/zero → neglecting it breaks the 5% gate → rolled back.
    op = {
        "gm_m1": 1e-3,
        "ro_m1": 2e5,
        "rl": 1e4,
        "cgs_m1": 1e-14,
        "cgd_m1": 1e-12,
        "cdb_m1": 1e-16,
        "csb_m1": 1e-16,
    }
    res = simplify_tf(raw, neglect_cgd("M1"), operating_point=op)
    assert any(r.status == "REJECTED_VALIDATION" for r in res.ledger)
    assert res.expr == res.exact  # rolled back to exact — never ship an unvalidated approximation


# ------------------------------------------------------------------------
# EQUALITY — matched pair collapses the symbol count, losslessly
# ------------------------------------------------------------------------
_DP = (
    "* dp\nM1 outn vinp tail 0 nmos\nM2 outp vinn tail 0 nmos\n"
    "M3 outn outn vdd vdd pmos\nM4 outp outn vdd vdd pmos\nItail tail 0 dc ib\n.end"
)


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
    assert (
        contract.tf_exact_expr != contract.tf_simplified_expr
    )  # exact AND simplified both present
    assert contract.tf_simplified_expr == "-gm_m1/gm_m2"
    assert contract.assumptions_applied  # the ledger is carried
    assert contract.validation is not None and contract.validation.passed


def test_unknown_assumption_kind_rejected():
    with pytest.raises(ValueError, match="unknown assumption kind"):
        Assumption(id="x", kind="BOGUS")


# ------------------------------------------------------------------------
# BAND_LIMIT — inband(f_hi) drops the s-terms negligible up to f_hi (LEAF-F04)
# ------------------------------------------------------------------------
# 0.1 fF caps put the Miller CS pole near 84 GHz and its zero near 1.6 THz: both out of band.
_MILLER_SMALL_CAPS = {
    "gm_m1": 1e-3,
    "ro_m1": 2e5,
    "rl": 1e4,
    "cgs_m1": 1e-14,
    "cgd_m1": 1e-16,
    "cdb_m1": 1e-16,
    "csb_m1": 1e-16,
}


@pytest.mark.parametrize(
    "band",
    [
        inband(1e6),
        Assumption(id="band", kind="BAND_LIMIT", payload={"f_hi": 1e6}),  # GLOBAL scope as declared
    ],
    ids=["inband", "hand_built"],
)
def test_inband_drops_the_out_of_band_s_terms(band):
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    # _apply_band_limit passed scope= to _record, which already passes a.scope: every
    # non-no-op inband() step raised TypeError (got multiple values for 'scope').
    res = simplify_tf(raw, band, operating_point=_MILLER_SMALL_CAPS)
    rec = next(r for r in res.ledger if r.kind == "BAND_LIMIT")
    assert rec.status == "APPLIED" and rec.validated
    assert rec.scope == "BAND" and rec.dropped_terms
    assert str(res.expr) == "-gm_m1*rl*ro_m1/(rl + ro_m1)"  # the in-band form: -gm·(ro∥RL)
    assert res.validation is not None and res.validation.passed and not res.unreduced


_HAND_BUILT_BAND = Assumption(id="band", kind="BAND_LIMIT", payload={"f_hi": 1e13})  # GLOBAL


@pytest.mark.parametrize("band", [inband(1e13), _HAND_BUILT_BAND], ids=["inband", "hand_built"])
def test_inband_is_a_no_op_when_the_band_reaches_the_dynamics(band):
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    res = simplify_tf(raw, band, operating_point=_MILLER_SMALL_CAPS)
    rec = next(r for r in res.ledger if r.kind == "BAND_LIMIT")
    # a band limit records scope BAND whatever it did: the hand-built one recorded GLOBAL on
    # NO_OP and BAND when APPLIED (L-PF-3)
    assert rec.status == "NO_OP" and rec.scope == "BAND"
    assert res.expr == res.exact


# One pole at 1.6 kHz (R1·C1 = 100 us) and one at 160 MHz (R2·C2 = 1 ns).
_TWO_POLE = "* two poles\nR1 in n1 R1\nC1 n1 0 C1\nR2 n1 out R2\nC2 out 0 C2\n.end"
_TWO_POLE_OP = {"r1": 1e3, "c1": 1e-7, "r2": 1.0, "c2": 1e-9}


@pytest.mark.parametrize("f_hi", [1e4, 1e6])
def test_inband_is_validated_up_to_its_own_band(f_hi):
    """The band limit claims nothing above ``f_hi``, but it was checked over 1 Hz-1 GHz, where the
    160 MHz pole it drops gives a relative error of 6.2: every in-band reduction was rejected."""
    raw = _raw(_TWO_POLE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, inband(f_hi), operating_point=_TWO_POLE_OP)
    rec = next(r for r in res.ledger if r.kind == "BAND_LIMIT")
    assert rec.status == "APPLIED" and rec.validated
    assert rec.relative_error is not None and rec.relative_error <= 0.05
    assert sp.Poly(sp.fraction(res.expr)[1], S).degree() == 1  # the 160 MHz pole is gone
    assert res.validation is not None and res.validation.passed and not res.unreduced
    assert res.validation.freq_hz_min == pytest.approx(1.0)
    assert res.validation.freq_hz_max == pytest.approx(f_hi)


def test_a_step_after_a_band_limit_is_validated_in_that_band():
    """Poles at 1.6 kHz, 0.8 MHz and 3.2 GHz. ``inband(1e7)`` drops the 3.2 GHz one; the
    dominant-pole factorization after it is then checked up to 10 MHz (0.33 % error), not up to
    1 GHz, where the pole the band limit already dropped gives 31 %."""
    deck = (
        "* three poles\nR1 in n1 R1\nC1 n1 0 C1\nR2 n1 n2 R2\nC2 n2 0 C2\n"
        "R3 n2 out R3\nC3 out 0 C3\n.end"
    )
    op = {"r1": 1e3, "c1": 1e-7, "r2": 1e3, "c2": 1e-10, "r3": 1.0, "c3": 1e-10}
    res = simplify_tf(
        _raw(deck, ("out", "0"), ("in", "0")), [inband(1e7), dominant_pole()], operating_point=op
    )
    assert [(r.kind, r.status, r.validated) for r in res.ledger] == [
        ("BAND_LIMIT", "APPLIED", True),
        ("POLE_SEPARATION", "APPLIED", True),
    ]
    assert res.validation is not None and res.validation.passed and not res.unreduced
    assert res.validation.freq_hz_max == pytest.approx(1e7)


def test_without_a_band_limit_the_sweep_stays_1hz_to_1ghz():
    raw = _raw(_TWO_POLE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, dominant_pole(), operating_point=_TWO_POLE_OP)
    assert res.validation is not None and res.validation.freq_hz_max == pytest.approx(1e9)


# ------------------------------------------------------------------------
# POLE_SEPARATION — dominant_pole() keeps the factored form (LEAF-F04)
# ------------------------------------------------------------------------
# Two gain stages, each loaded by an RC: the audit's probe (41 ops exact, 259 after the old
# re-expansion). CA = 1 fF against CL = 1 pF separates the poles ~1000x (17 MHz vs 17 GHz).
_TWO_STAGE = (
    "* two-stage cs\nM1 a in 0 0 nmos\nRA a 0 RA\nCA a 0 CA\n"
    "M2 out a 0 0 nmos\nRL out 0 RL\nCL out 0 CL\n.end"
)
_TWO_STAGE_OP = {
    "gm_m1": 1e-3,
    "gm_m2": 1e-3,
    "ro_m1": 2e5,
    "ro_m2": 2e5,
    "ra": 1e4,
    "rl": 1e4,
    "ca": 1e-15,
    "cl": 1e-12,
}


def test_dominant_pole_keeps_the_factored_form():
    raw = _raw(_TWO_STAGE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, dominant_pole(), operating_point=_TWO_STAGE_OP)
    rec = next(r for r in res.ledger if r.kind == "POLE_SEPARATION")
    assert rec.status == "APPLIED" and rec.validated
    # (A0)/((1 + s·a1)(1 + s·b1/a1)): the denominator is two first-order factors in s ...
    _, den = sp.fraction(res.expr)
    s_factors = [f for f in sp.Mul.make_args(den) if f.has(S)]
    assert len(s_factors) == 2 and all(sp.Poly(f, S).degree() == 1 for f in s_factors)
    # ... not re-expanded through canonical_tf, which multiplied the op count ~6x (41 -> 259).
    # The factored form still repeats the s^1 coefficient once, so it is not below the exact count.
    ops = sp.count_ops(res.expr)
    assert ops < sp.count_ops(canonical_tf(res.expr))
    assert ops <= 2 * sp.count_ops(res.exact)
    assert res.validation is not None and res.validation.passed and not res.unreduced


def test_dominant_pole_bundle_feeds_the_contract_its_poles():
    raw = _raw(_TWO_STAGE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, "dominant_pole", operating_point=_TWO_STAGE_OP)
    assert any(r.kind == "POLE_SEPARATION" and r.status == "APPLIED" for r in res.ledger)
    contract = describe_tf(raw, simplified=res, operating_point=_TWO_STAGE_OP)
    exact = describe_tf(raw, operating_point=_TWO_STAGE_OP)
    got = sorted(abs(p.value_real or 0.0) for p in contract.poles)
    want = sorted(abs(p.value_real or 0.0) for p in exact.poles)
    assert len(got) == 2
    assert got == pytest.approx(want, rel=5e-3)  # the separated poles land on the exact ones


# POLE_SEPARATION is arbitrated against the ratio floor, as DOMINANCE is (#309). On the RC-RC
# ladder c1^2/(c0*c2) = p2/p1 + 2 + p1/p2 for the two real poles.
_EQUAL_SECTIONS_OP = {"r1": 1e3, "c1": 1e-9, "r2": 1e3, "c2": 1e-9}  # poles 3.8e5, 2.6e6 rad/s


def test_dominant_pole_applied_when_separated_records_the_spacing():
    # poles 1.6 kHz and 160 MHz: r = 1.0e9/9.9e3 + 2 + ... ~ 1.02e5
    raw = _raw(_TWO_POLE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, dominant_pole(), operating_point=_TWO_POLE_OP)
    rec = next(r for r in res.ledger if r.kind == "POLE_SEPARATION")
    assert rec.status == "APPLIED" and rec.validated
    assert rec.numeric_ratio == pytest.approx(1.02e5, rel=1e-2)


@pytest.mark.parametrize("validate", [True, False])
def test_dominant_pole_rejected_below_the_ratio_floor(validate):
    # equal sections: r = 9.0 < 100, so the factorization is refused before validation decides
    raw = _raw(_TWO_POLE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, dominant_pole(), operating_point=_EQUAL_SECTIONS_OP, validate=validate)
    rec = next(r for r in res.ledger if r.kind == "POLE_SEPARATION")
    assert rec.status == "REJECTED_NUMERICS" and not rec.validated
    assert rec.numeric_ratio == pytest.approx(9.0, rel=1e-6)
    assert rec.relative_error is None  # rejected before the validation gate ran
    assert sp.simplify(res.expr - res.exact) == 0  # nothing rewritten


def test_dominant_pole_with_a_nan_coefficient_is_rejected():
    raw = _raw(_TWO_POLE, ("out", "0"), ("in", "0"))
    res = simplify_tf(
        raw, dominant_pole(), operating_point={**_TWO_POLE_OP, "c2": float("nan")}, validate=False
    )
    rec = next(r for r in res.ledger if r.kind == "POLE_SEPARATION")
    assert rec.status == "REJECTED_NUMERICS"
    assert "NaN" in rec.description


def test_a_lower_ratio_floor_hands_the_decision_to_the_validation_gate():
    raw = _raw(_TWO_POLE, ("out", "0"), ("in", "0"))
    res = simplify_tf(raw, dominant_pole(), operating_point=_EQUAL_SECTIONS_OP, ratio_floor=5)
    rec = next(r for r in res.ledger if r.kind == "POLE_SEPARATION")
    assert rec.status == "REJECTED_VALIDATION"
    assert rec.relative_error == pytest.approx(0.10, abs=0.01)


# ------------------------------------------------------------------------
# The final (end-to-end) gate — UNREDUCED fallback (LEAF-F04)
# ------------------------------------------------------------------------
def test_final_gate_returns_the_exact_tf_marked_unreduced(monkeypatch):
    # The per-step gate and the final gate share the operating point, sweep and tolerance, so
    # the fallback only fires when a step slips past the per-step gate. Blind that gate and
    # let a reduction that really breaks tolerance through: the final gate must catch it.
    monkeypatch.setattr(simplify_module, "_relative_error", lambda *a, **k: 0.0)
    raw = _raw(_MILLER, ("out", "0"), ("in", "0"), level=Fidelity.FULL)
    op = {
        "gm_m1": 1e-3,
        "ro_m1": 2e5,
        "rl": 1e4,
        "cgs_m1": 1e-14,
        "cgd_m1": 1e-12,
        "cdb_m1": 1e-16,
        "csb_m1": 1e-16,
    }
    res = simplify_tf(raw, neglect_cgd("M1"), operating_point=op)
    assert any(r.kind == "SMALLNESS" and r.status == "APPLIED" for r in res.ledger)
    assert res.unreduced is True
    assert res.expr == res.exact  # never ship an unvalidated approximation
    assert res.validation is not None and res.validation.passed is False
    assert (
        res.validation.max_relative_error is not None and res.validation.max_relative_error > 0.05
    )
