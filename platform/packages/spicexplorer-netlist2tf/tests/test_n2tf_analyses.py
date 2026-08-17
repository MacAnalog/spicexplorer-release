"""P7 — derived analyses: open-loop gain + input/output impedance over the shared MNA solve.

P9 — the DM/CM family: common-mode gain, CMRR, PSRR, loop gain, and the asymptotic-gain
feedback decomposition (all recipes over the same MNA solve; see ``analyses.py``).
"""

from __future__ import annotations

from typing import cast

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Fidelity,
    asymptotic_gain,
    cmrr,
    common_mode_gain,
    input_impedance,
    loop_gain,
    open_loop_gain,
    output_impedance,
    psrr,
)


# ------------------------------------------------------------------------
# Open-loop gain — base case, just an extract_tf with provenance
# ------------------------------------------------------------------------
def test_open_loop_gain_cs():
    res = open_loop_gain("* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("out", "0"), ("in", "0"))
    assert res.analysis == "open_loop_gain"
    gm, ro, rl = sp.symbols("gm_m1 ro_m1 rl")
    assert sp.simplify(res.as_sympy_exact() - (-gm * ro * rl / (ro + rl))) == 0


# ------------------------------------------------------------------------
# Output impedance — Z_out = ro ∥ RL for a common-source (input zeroed)
# ------------------------------------------------------------------------
def test_output_impedance_common_source():
    res = output_impedance(
        "* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("out", "0"),
        zero_input=("in", "0"),  # open-loop: ground the gate (source-zeroing)
    )
    assert res.analysis == "output_impedance"
    ro, rl = sp.symbols("ro_m1 rl")
    # Z_out = ro ∥ RL = ro*RL/(ro+RL)
    assert sp.simplify(res.as_sympy_exact() - ro * rl / (ro + rl)) == 0


def test_output_impedance_numeric():
    res = output_impedance(
        "* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("out", "0"),
        zero_input=("in", "0"), operating_point={"ro_m1": 1e5, "rl": 1e5, "gm_m1": 1e-3},
    )
    # 100k ∥ 100k = 50k
    assert res.dc_gain.value == pytest.approx(5e4)


# ------------------------------------------------------------------------
# Input impedance — a resistive node gives R; an ideal gate is infinite (clean error)
# ------------------------------------------------------------------------
def test_input_impedance_resistive():
    # Z_in looking into a node with a resistor to ground = R.
    res = input_impedance("* r\nR1 in 0 R\n.end", ("in", "0"))
    assert res.analysis == "input_impedance"
    assert sp.simplify(res.as_sympy_exact() - sp.Symbol("r")) == 0


def test_input_impedance_capacitive_gate_full_fidelity():
    # At FULL fidelity the gate has Cgs+Cgd → finite (capacitive) Z_in, so the solve is well-posed.
    res = input_impedance(
        "* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("in", "0"), level=Fidelity.FULL,
    )
    # Z_in is capacitive (∝ 1/(s·C)) → it has s, it is not a constant.
    assert res.as_sympy_exact().has(sp.Symbol("s"))


def test_input_impedance_ideal_gate_is_infinite():
    # SOME_PARASITIC ideal gate: no admittance path → infinite impedance → explicit error.
    with pytest.raises(ValueError, match="singular|infinite"):
        input_impedance("* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("in", "0"))


# ------------------------------------------------------------------------
# P9 — common-mode gain: for a single-ended input, cm-drive coincides with the open-loop dm-drive
# ------------------------------------------------------------------------
_CS = "* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end"


def test_common_mode_gain_single_ended_equals_open_loop():
    # in− is ground ⇒ there is no common-mode axis ⇒ A_cm == A_OL (drive mode is a no-op).
    a_cm = common_mode_gain(_CS, ("out", "0"), ("in", "0"))
    a_ol = open_loop_gain(_CS, ("out", "0"), ("in", "0"))
    assert a_cm.analysis == "common_mode_gain"
    assert sp.simplify(a_cm.as_sympy_exact() - a_ol.as_sympy_exact()) == 0


# ------------------------------------------------------------------------
# P9 — CMRR of a long-tailed pair: A_dm/A_cm = (1 + 2·gm·R_tail)/2 (single-ended output)
# ------------------------------------------------------------------------
# Symmetric resistor-loaded diff pair with a finite tail resistance, IDEAL fidelity (gm only):
#   A_dm(out+) = −gm·rd/2,  A_cm(out+) = −gm·rd/(1+2·gm·rt)  ⇒  CMRR = (1+2·gm·rt)/2.
_DIFFPAIR = (
    "* long-tailed pair\n"
    "M1 outp inp tail 0 nmos\n"
    "M2 outn inn tail 0 nmos\n"
    "RDP outp 0 rd\n"
    "RDN outn 0 rd\n"
    "RT tail 0 rt\n"
    ".end"
)


def test_cmrr_long_tailed_pair_numeric():
    res = cmrr(
        _DIFFPAIR, ("outp", "0"), ("inp", "inn"), level=Fidelity.IDEAL,
        subs={"gm_m1": 1e-3, "gm_m2": 1e-3, "rd": 1e4, "rt": 5e4},
    )
    assert res.analysis == "cmrr"
    assert res.conv_type == "diff"  # the input pair is genuinely two-node
    # CMRR = (1 + 2·gm·rt)/2 = (1 + 2·1e-3·5e4)/2 = 101/2 = 50.5
    assert res.dc_gain.value == pytest.approx(50.5)
    # the component TFs ride along
    assert set(res.component_tfs) == {"a_dm", "a_cm"}


def test_cmrr_infinite_is_a_clean_error():
    # A *differential* output of a perfectly matched pair (equal gm) has A_cm ≡ 0 (the ideal-match
    # limit) ⇒ CMRR is infinite ⇒ a clean, explicit error rather than a division by zero.
    with pytest.raises(ValueError, match="A_cm is identically 0"):
        cmrr(_DIFFPAIR, ("outp", "outn"), ("inp", "inn"), level=Fidelity.IDEAL,
             subs={"gm_m1": 1e-3, "gm_m2": 1e-3, "rd": 1e4, "rt": 5e4})


# ------------------------------------------------------------------------
# P9 — PSRR via the net-role override: a resistor-loaded CS, load tied to the supply rail
# ------------------------------------------------------------------------
# DM path: A_dm = −gm·(rd ∥ ro).  Supply path (vdd re-promoted to input, gate zeroed):
#   A_(vdd→out) = ro/(rd+ro).   PSRR = A_dm / A_(vdd→out) = −gm·rd (exact, ro cancels).
_CS_PSRR = (
    "* cs with supply-referred load\n"
    "Vin in 0 ac 1\n"
    "Vsup vdd 0 dc 1.8\n"
    "M1 out in 0 0 nmos\n"
    "RD out vdd rd\n"
    ".end"
)


def test_psrr_common_source_supply_referred_load():
    res = psrr(_CS_PSRR, ("out", "0"), supply="vdd")  # input auto-detected from the AC source
    assert res.analysis == "psrr"
    gm, rd = sp.symbols("gm_m1 rd")
    assert sp.simplify(res.as_sympy() - (-gm * rd)) == 0
    assert set(res.component_tfs) == {"a_dm", "a_vdd"}


# ------------------------------------------------------------------------
# P9 — loop gain (return ratio) of a shunt-feedback CS stage
# ------------------------------------------------------------------------
# Homogeneous (all sources off) feedback network: Rf out→gate, Rin gate→0, RD out→0.
#   T = gm·D1/D0 = gm·rin·rd/(rin + rd + rf)   (Blackman, IDEAL fidelity).
# (``rfb``, not ``rf`` — ``rf`` sympifies to sympy's RisingFactorial, not a free symbol.)
_FB = (
    "* shunt-feedback cs\n"
    "M1 out ing 0 0 nmos\n"
    "Rf ing out rfb\n"
    "Rin ing 0 rin\n"
    "RD out 0 rd\n"
    ".end"
)


def test_loop_gain_shunt_feedback():
    res = loop_gain(_FB, "M1", level=Fidelity.IDEAL)
    assert res.analysis == "loop_gain"
    gm, rin, rd, rfb = sp.symbols("gm_m1 rin rd rfb")
    assert sp.simplify(res.as_sympy() - gm * rin * rd / (rin + rd + rfb)) == 0


# ------------------------------------------------------------------------
# P9 — asymptotic-gain decomposition: the H = (A∞·T + ρ)/(1 + T) identity holds symbolically
# ------------------------------------------------------------------------
# Inverting amp: Vin → Rs → gate, Rf gate→out (shunt-shunt feedback). A∞ (gm→∞) = −Rf/Rs.
_INV = (
    "* inverting amp\n"
    "Vin inx 0 ac 1\n"
    "Rs inx ing rs\n"
    "Rf ing out rfb\n"
    "M1 out ing 0 0 nmos\n"
    "RD out 0 rd\n"
    ".end"
)


def test_asymptotic_gain_decomposition_identity():
    res = asymptotic_gain(_INV, ("out", "0"), None, "M1", level=Fidelity.IDEAL)
    assert res.analysis == "asymptotic_gain"
    a_inf = res.as_sympy()
    gain = cast("sp.Expr", sp.sympify(res.component_tfs["gain"]))
    t = cast("sp.Expr", sp.sympify(res.component_tfs["loop_gain"]))
    rho = cast("sp.Expr", sp.sympify(res.component_tfs["direct_transmission"]))
    # the exact decomposition: H == (A∞·T + ρ)/(1 + T)
    assert sp.simplify(gain - (a_inf * t + rho) / (t + 1)) == 0
    # ideal-feedback gain of the inverting amp is −Rf/Rs
    rs, rfb = sp.symbols("rs rfb")
    assert sp.simplify(a_inf - (-rfb / rs)) == 0
