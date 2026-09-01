"""Stage-3 MNA + symbolic-solve tests.

Exact transfer functions are verified against hand-derived closed forms on small circuits (an RC
low-pass, a common-source stage, a Miller-zero stage); a real differential-pair topology exercises
the selectively-numericized path. Equivalence is checked by ``simplify(... ) == 0`` (numeric/symbolic
identity), never string equality.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    extract_tf,
    from_file,
    from_string,
    small_signal_model,
)
from spicexplorer_netlist2tf.tf import S, as_num_den

_FIX = Path(__file__).resolve().parent / "fixtures"


def _tf(netlist: str, output, input, *, level=Fidelity.SOME_PARASITIC, subs=None, name="c"):
    ir = from_string(netlist, name=name)
    ssir = small_signal_model(ir, level=level)
    system = build_system(ssir, subs=subs)
    return extract_tf(system, output, input, numeric_subs=subs)


def _equal(a: sp.Expr, b: sp.Expr) -> bool:
    return sp.simplify(a - b) == 0


# ------------------------------------------------------------------------
# RC low-pass — H = 1/(1 + s R C)
# ------------------------------------------------------------------------
def test_rc_lowpass_exact():
    raw = _tf("* rc\nR1 in out R\nC1 out 0 C\n.end", ("out", "0"), ("in", "0"))
    r, c = sp.Symbol("r"), sp.Symbol("c")
    assert _equal(raw.expr, 1 / (1 + r * c * S))
    assert raw.solve_path == "fully_symbolic"


# ------------------------------------------------------------------------
# Common-source — Av = -gm·(ro ∥ RL)
# ------------------------------------------------------------------------
def test_common_source_gain_exact():
    raw = _tf(
        "* cs\nM1 out in 0 0 nmos\nRload out 0 RL\n.end",
        ("out", "0"), ("in", "0"),
    )
    gm = sp.Symbol("gm_m1", positive=True)
    ro = sp.Symbol("ro_m1", positive=True)
    rl = sp.Symbol("rl")
    assert _equal(raw.expr, -gm * ro * rl / (ro + rl))
    # DC gain is frequency-independent here (no caps at SOME_PARASITIC)
    assert raw.expr.free_symbols == {gm, ro, rl}


# ------------------------------------------------------------------------
# Common-source with Miller Cgd — feedforward zero at s = +gm/Cgd
# ------------------------------------------------------------------------
def test_common_source_miller_zero():
    raw = _tf(
        "* cs miller\nM1 out in 0 0 nmos\nRload out 0 RL\n.end",
        ("out", "0"), ("in", "0"), level=Fidelity.FULL,
    )
    num, _den = as_num_den(raw.expr)
    gm = sp.Symbol("gm_m1", positive=True)
    cgd = sp.Symbol("cgd_m1", positive=True)
    # the numerator vanishes at the RHP zero s = gm/Cgd
    assert sp.simplify(num.subs(S, gm / cgd)) == 0


# ------------------------------------------------------------------------
# Determinism — same query → identical canonical expression
# ------------------------------------------------------------------------
def test_solve_is_deterministic():
    nl = "* cs\nM1 out in 0 0 nmos\nRload out 0 RL\n.end"
    a = _tf(nl, ("out", "0"), ("in", "0")).expr
    b = _tf(nl, ("out", "0"), ("in", "0")).expr
    assert sp.srepr(a) == sp.srepr(b)


# ------------------------------------------------------------------------
# Selective numericization — keep gm symbolic, numericize the rest
# ------------------------------------------------------------------------
def test_selective_numericization():
    subs = {"ro_m1": 2e4, "rl": 1e4}
    raw = _tf(
        "* cs\nM1 out in 0 0 nmos\nRload out 0 RL\n.end",
        ("out", "0"), ("in", "0"), subs=subs,
    )
    gm = sp.Symbol("gm_m1", positive=True)
    assert raw.kept_symbolic == ("gm_m1",)
    assert raw.solve_path == "selectively_numericized"
    # -gm·(20k ∥ 10k) = -gm·6666.67  (float coefficient → compare with tolerance)
    coeff = raw.expr.coeff(gm)
    assert coeff is not None
    assert float(coeff) == pytest.approx(-(2e4 * 1e4 / (2e4 + 1e4)))


# ------------------------------------------------------------------------
# Singular system — a floating high-impedance gate node raises cleanly
# ------------------------------------------------------------------------
def test_floating_internal_node_is_singular():
    # 'mid' is M2's gate only (a control node with no admittance path) and is NOT excited → its
    # matrix row is all-zero → the system is singular. Caught and reported, not returned as garbage.
    nl = "* float\nM1 out in 0 0 nmos\nM2 z mid 0 0 nmos\nRload out 0 RL\n.end"
    with pytest.raises(ValueError, match="singular"):
        _tf(nl, ("out", "0"), ("in", "0"))


# ------------------------------------------------------------------------
# Real differential-pair topology (5T OTA core) — single-ended output
# ------------------------------------------------------------------------
_DIFF_PAIR = """* 5T OTA core (diff pair + mirror load), ideal tail
M1 outn vinp tail 0 nmos
M2 outp vinn tail 0 nmos
M3 outn outn vdd vdd pmos
M4 outp outn vdd vdd pmos
Itail tail 0 dc ibias
.end
"""


def test_diff_pair_builds_and_solves_numericized():
    subs = {
        "gm_m1": 1e-3, "gm_m2": 1e-3, "gm_m3": 1e-3, "gm_m4": 1e-3,
        "ro_m1": 5e4, "ro_m2": 5e4, "ro_m3": 8e4, "ro_m4": 8e4,
    }
    raw = _tf(_DIFF_PAIR, ("outp", "0"), ("vinp", "vinn"), subs=subs)
    # A well-posed, frequency-independent (no caps) numeric gain of the right order.
    assert raw.expr.is_number
    av = complex(raw.expr)
    assert abs(av) > 10  # a real OTA single-ended gain, magnitude well above unity


def test_build_system_over_real_cascode():
    # Structural check on a real IHP DUT: the system assembles, the rails merge to the AC-ground
    # reference, and the input-pair small-signal symbols are present. (Not solved end-to-end: the
    # committed netlist's DC-only enable gates float at the bare-subckt level — that's the stimulus
    # overlay's job in P7, and the ceiling benchmark's territory.)
    ir = from_file(
        _FIX / "ota-improved.spice", name="cascode"
    )
    system = build_system(small_signal_model(ir, level=Fidelity.SOME_PARASITIC))
    assert system.n > 5
    assert {"gm_m1", "ro_m1", "gm_m2"} <= system.free_symbols
    # both rails are the AC-ground reference (no row); the DC bias sources V1/V2 shorted their nets
    assert system.row_of("vdd") is None
    assert system.row_of("vss") is None


def test_diff_pair_symbolic_gm_only():
    # Keep the two input-pair gm's symbolic, numericize everything else → readable gm-form.
    subs = {
        "gm_m3": 1e-3, "gm_m4": 1e-3,
        "ro_m1": 5e4, "ro_m2": 5e4, "ro_m3": 8e4, "ro_m4": 8e4,
    }
    raw = _tf(_DIFF_PAIR, ("outp", "0"), ("vinp", "vinn"), subs=subs)
    assert set(raw.kept_symbolic) == {"gm_m1", "gm_m2"}
    assert raw.expr.diff(sp.Symbol("gm_m1", positive=True)) != 0  # gain depends on gm1


# ------------------------------------------------------------------------
# Transimpedance — the test-current primitive read at a *different* port
# ------------------------------------------------------------------------
def _sys(netlist: str, *, level=Fidelity.SOME_PARASITIC, name="c"):
    return build_system(small_signal_model(from_string(netlist, name=name), level=level))


def test_transimpedance_rc_is_the_shunt_impedance():
    # I forced into `out` sees R ∥ (1/sC) — the closed form, read at the injected node's own port
    # via the two-port entry (so this also pins Z_T == Z_in when the ports coincide).
    from spicexplorer_netlist2tf import transimpedance

    system = _sys("* rc\nR1 out 0 R\nC1 out 0 C\n.end")
    zt = transimpedance(system, ("out", "0"), ("out", "0"))
    r, c = sp.Symbol("r"), sp.Symbol("c")
    assert _equal(zt.expr, r / (1 + r * c * S))
    assert zt.analysis == "transimpedance"


def test_transimpedance_common_source_drain_injection():
    # A current forced into the CS drain (drain→source, i.e. the channel-noise generator's own
    # port) develops i·(ro ∥ RL) at the output: the gate is quiet, so no gm term appears.
    from spicexplorer_netlist2tf import transimpedance

    system = _sys("* cs\nM1 out in 0 0 nmos\nRload out 0 RL\nRg in 0 RG\n.end")
    zt = transimpedance(system, ("out", "0"), ("out", "0"))
    ro, rl = sp.Symbol("ro_m1", positive=True), sp.Symbol("rl")
    assert _equal(zt.expr, ro * rl / (ro + rl))


def test_transimpedance_is_forward_transfer_not_self_port():
    # Injecting at node `a` of an R-divider and reading at node `b` must give the *transfer*
    # impedance, which is strictly smaller than the driving-point impedance at `a`.
    from spicexplorer_netlist2tf import transimpedance
    from spicexplorer_netlist2tf.mna import driving_point_impedance

    system = _sys("* divider\nR1 a 0 1k\nR2 a b 2k\nR3 b 0 3k\n.end")
    z_self = driving_point_impedance(system, ("a", "0"))
    z_t = transimpedance(system, ("b", "0"), ("a", "0"))
    # a: 1k ∥ (2k + 3k) = 833.33 Ω ; transfer: that, divided down by 3k/(2k+3k)
    assert abs(float(z_self.expr) - 1e3 * 5e3 / 6e3) < 1e-6
    assert abs(float(z_t.expr) - float(z_self.expr) * 3.0 / 5.0) < 1e-6


def test_transimpedance_reciprocity_on_a_passive_network():
    # A network of R and C only is reciprocal: Z_T(out←in) == Z_T(in←out). The MNA stamp must
    # preserve that, and it is the cheapest correctness check on the injection RHS.
    from spicexplorer_netlist2tf import transimpedance

    system = _sys("* ladder\nR1 a b 1k\nC1 b 0 1p\nR2 b c 2k\nC2 c 0 3p\n.end")
    fwd = transimpedance(system, ("c", "0"), ("a", "0"))
    rev = transimpedance(system, ("a", "0"), ("c", "0"))
    assert _equal(fwd.expr, rev.expr)


def test_transimpedance_rejects_ac_ground_injection():
    from spicexplorer_netlist2tf import transimpedance

    system = _sys("* rc\nR1 out 0 R\nC1 out 0 C\n.end")
    with pytest.raises(ValueError, match="entirely at AC ground"):
        transimpedance(system, ("out", "0"), ("0", "0"))
