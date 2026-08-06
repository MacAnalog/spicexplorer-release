"""Whole-deck ngspice → Spectre translation (syntax half).

Pinned against an inline IHP-style testbench that concentrates every landmine the
translator exists for: a hyphenated subckt name (invalid Spectre identifier), X-prefixed
MOS (PDK subckt devices), UPPERCASE ``.param`` canonicalization vs lowercase device
references (Spectre is case-sensitive), a bare symbolic passive value (``CL``), a
multi-token source value (``dc VCM ac 1``), and the ngspice ``GND``≡0 ground alias.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_circuitgraph import translate_ngspice_to_spectre

_TB = """* 5t ota tb (translation landmine fixture)
Vdd v_dd GND VDD
Vin v_in v_ss dc VCM ac 1
C1 v_out v_ss CL m=1
I0 v_dd net1 IBIAS
xota v_dd v_out v_in v_out net1 v_ss ota-5t

.param CL=50f
.param VDD=1.5
.param VCM=0.8
.param IBIAS=20u
.param x_w=0.5u
.param x_l=5.0u

.subckt ota-5t vdd vout vinp vinn ibias vss
XM1 g vinp t vss sg13_lv_nmos w=x_w l=x_l ng=1 m=1
XM2 vout vinn t vss sg13_lv_nmos w=x_w l=x_l ng=1 m=1
XM3 g g vdd vdd sg13_lv_pmos w=1.5u l=0.13u ng=1 m=1
.ends

.GLOBAL GND
.end
"""


@pytest.fixture()
def deck(tmp_path: Path) -> Path:
    p = tmp_path / "tb.spice"
    p.write_text(_TB)
    return p


def test_translates_dut_stimulus_params_and_ground(deck: Path) -> None:
    d = translate_ngspice_to_spectre(deck, pdk="tsmc-n65", source_pdk="ihp-sg13g2")

    # DUT block: hyphen sanitized consistently at definition AND instance master
    assert len(d.subckt_blocks) == 1
    block = d.subckt_blocks[0]
    assert block.splitlines()[0] == "subckt ota_5t vdd vout vinp vinn ibias vss"
    assert block.splitlines()[-1] == "ends ota_5t"
    assert "ota_5t" in d.stimulus  # the XOTA instance line uses the same sanitized master

    # device-model mapping (IHP → TSMC-65 names) + finger-convention retarget (ng → nf)
    assert "nch_lvt" in block and "pch_lvt" in block
    assert "sg13_lv" not in block
    assert "nf=1" in block and "ng=" not in block

    # symbolic geometry survives, in the (lowercase) parameter namespace
    assert "w=x_w" in block and "l=x_l" in block
    assert d.parameters["x_w"] == pytest.approx(0.5e-6)
    assert d.parameters["x_l"] == pytest.approx(5e-6)

    # case-folding: spicelib uppercases .param names; references must fold to lowercase
    assert "capacitor c=cl" in d.stimulus  # bare symbolic passive → expression
    assert "vsource dc=vcm mag=1" in d.stimulus  # multi-token source value folded
    assert "isource dc=ibias" in d.stimulus
    assert all(k == k.lower() for k in d.parameters)

    # ngspice ground alias made explicit
    # net names case-fold to lowercase for Spectre (SPICE is case-insensitive); the tie
    # instance LABEL keeps source case (V_tie_GND), the NET it ties folds (gnd)
    assert d.ground_ties == ("V_tie_GND (gnd 0) vsource dc=0",)
    assert "V_tie_GND" in d.design_text


def test_numeric_defaults_are_si_floats(deck: Path) -> None:
    d = translate_ngspice_to_spectre(deck, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    assert d.parameters["cl"] == pytest.approx(50e-15)
    assert d.parameters["vdd"] == pytest.approx(1.5)
    assert d.parameters["ibias"] == pytest.approx(20e-6)


def test_pdk_accepts_table_or_name_and_rejects_unknown(deck: Path) -> None:
    from spicexplorer_circuitgraph.pdk import TSMC_N65

    by_name = translate_ngspice_to_spectre(deck, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    by_table = translate_ngspice_to_spectre(deck, pdk=TSMC_N65, source_pdk="ihp-sg13g2")
    assert by_name.subckt_blocks == by_table.subckt_blocks
    with pytest.raises(ValueError, match="unknown PDK"):
        translate_ngspice_to_spectre(deck, pdk="not-a-pdk")


def test_without_target_pdk_source_models_pass_through(deck: Path) -> None:
    d = translate_ngspice_to_spectre(deck, source_pdk="ihp-sg13g2")
    assert "sg13_lv_nmos" in d.subckt_blocks[0]  # no retarget requested


def test_quoted_symbolic_passive_values_become_expressions(tmp_path: Path) -> None:
    """ngspice quote-expressions (`C1 a b 'x_c'`) are the {…} braces' twin: they must
    render as Spectre expressions (`capacitor c=x_c`), never as a phantom model master
    (`_x_c_`) — found live."""
    p = tmp_path / "quoted.spice"
    p.write_text(
        "* quoted-value fixture\n"
        "Vdd v_dd 0 1.5\n"
        "C1 v_dd v_out 'x_c'\n"
        "R1 v_out 0 'x_r*2'\n"
        ".param x_c=1p\n"
        ".param x_r=50k\n"
        ".end\n"
    )
    d = translate_ngspice_to_spectre(p)
    assert "capacitor c=x_c" in d.stimulus
    assert "resistor r=x_r*2" in d.stimulus
    assert "_x_c_" not in d.stimulus and "'" not in d.stimulus


def test_differential_ac_markers_emit_signed_mag_and_positive_pacmag(tmp_path: Path) -> None:
    """The `ac ±0.5` differential pair: `mag=` keeps the sign (Spectre ac accepts it) but
    `pacmag` must be non-negative (CMI-2048, live) — the negative side is spelled
    pacmag=|v| pacphase=180."""
    p = tmp_path / "diff.spice"
    p.write_text(
        "* differential ac fixture\n"
        "Vinp v_inp 0 dc 0.6 ac 0.5\n"
        "Vinn v_inn 0 dc 0.6 ac -0.5\n"
        "R1 v_inp v_inn 1k\n"
        ".end\n"
    )
    d = translate_ngspice_to_spectre(p)
    assert "mag=0.5 pacmag=0.5" in d.stimulus
    assert "mag=-0.5 pacmag=0.5 pacphase=180" in d.stimulus
    assert "pacmag=-" not in d.stimulus


def test_symbolic_tie_params_lose_spice_braces(tmp_path: Path) -> None:
    """SFE-874: `.param` tie/ratio exprs (`{x_a}`, `{x_b*17/3}`) must reach the Spectre
    `parameters` namespace brace-free — Spectre rejects `{…}` but accepts the
    parenthesized expression, and keeping it symbolic keeps the tie LIVE (injecting the
    free knob per candidate still moves the tied one)."""
    p = tmp_path / "ties.spice"
    p.write_text(
        "* tie fixture\n"
        "Vdd v_dd 0 1.5\n"
        "R1 v_dd v_out x_free\n"
        "R2 v_out 0 x_tied\n"
        ".param x_free=2k\n"
        ".param x_tied={x_free}\n"
        ".param x_ratio={x_free*17/3}\n"
        ".end\n"
    )
    d = translate_ngspice_to_spectre(p)
    assert d.parameters["x_free"] == pytest.approx(2e3)
    assert d.parameters["x_tied"] == "(x_free)"
    assert d.parameters["x_ratio"] == "(x_free*17/3)"
    assert not any("{" in str(v) for v in d.parameters.values())


def test_translated_example_deck_if_present() -> None:
    """The committed 5T-OTA example is the live-validated round-trip DUT (2026-07-05)."""
    from spicexplorer_core import project_root

    example = project_root() / "examples/OTA/5t-ota/ihp-sg13g2/spice/ota-5t_tb-ac.spice"
    if not example.exists():
        pytest.skip("example deck not present in this checkout")
    d = translate_ngspice_to_spectre(example, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    assert d.subckt_blocks and "subckt ota_5t" in d.subckt_blocks[0]
    assert "XOTA (v_dd v_out v_in v_out net1 v_ena v_ss) ota_5t" in d.stimulus
    assert d.parameters["x_dut_nfet_input_w"] == pytest.approx(0.5e-6)


def test_translates_pulse_source(tmp_path: Path) -> None:
    # the tran_step template's stimulus: `dc VCM pulse(V1 V2 TD TR TF PW PER)` → Spectre
    # `type=pulse val0/val1/delay/rise/fall/width/period` (positional; exprs de-braced)
    p = tmp_path / "tb_pulse.spice"
    p.write_text(
        "* pulse fixture\n"
        "Vin v_in 0 dc {VCM} pulse({VCM} {VCM+VSTEP} 1u 1n 1n 1 1)\n"
        "R1 v_in 0 1k\n"
        ".param VCM=0.8\n.param VSTEP=0.2\n"
        ".end\n"
    )
    d = translate_ngspice_to_spectre(p, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    # The timing args carry SPICE scale factors, which Spectre reads by DIFFERENT (case-sensitive)
    # rules — they are resolved to plain seconds rather than copied through as `1u`/`1n`.
    assert (
        "vsource dc=vcm type=pulse val0=vcm val1=vcm+vstep "
        "delay=1e-06 rise=1e-09 fall=1e-09 width=1 period=1" in d.stimulus
    )


def test_pulse_source_arg_count_guard(tmp_path: Path) -> None:
    p = tmp_path / "tb_pulse_bad.spice"
    p.write_text("* bad pulse\nVin a 0 pulse(1)\nR1 a 0 1k\n.end\n")
    with pytest.raises(ValueError, match="pulse"):
        translate_ngspice_to_spectre(p, pdk="tsmc-n65", source_pdk="ihp-sg13g2")


def test_translates_sin_source(tmp_path: Path) -> None:
    # the thd/iip3 templates' stimulus: `sin(VO VA FREQ)` → Spectre `type=sine sinedc/ampl/freq`
    # with VO doubling as the source's dc operating point
    p = tmp_path / "tb_sin.spice"
    p.write_text(
        "* sine fixture\n"
        "Vin v_in mid sin(0 {ASIG} 900000.0)\n"
        "Vtwo mid 0 sin({VCM} {ASIG} 1000000.0)\n"
        "R1 v_in 0 1k\n"
        ".param ASIG=0.05\n.param VCM=0.6\n"
        ".end\n"
    )
    d = translate_ngspice_to_spectre(p, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    assert "vsource dc=0 type=sine sinedc=0 ampl=asig freq=900000.0" in d.stimulus
    assert "vsource dc=vcm type=sine sinedc=vcm ampl=asig freq=1000000.0" in d.stimulus


def test_translates_viprb_marker_to_iprobe(tmp_path: Path) -> None:
    # the stb template's loop-probe marker: a 0 V source named VIPRB* → the Spectre
    # `iprobe` primitive (the `stb … probe=VIPRB` target); an ordinary 0 V source
    # (any other name) stays a vsource
    p = tmp_path / "tb_stb.spice"
    p.write_text(
        "* stb fixture\n"
        "VIPRB v_inn v_out dc 0\n"
        "Vfb v_x v_out dc 0\n"
        "R1 v_inn 0 1k\nR2 v_out 0 1k\nR3 v_x 0 1k\n"
        ".end\n"
    )
    d = translate_ngspice_to_spectre(p, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    assert "VIPRB (v_inn v_out) iprobe" in d.stimulus
    assert "VFB (v_x v_out) vsource dc=0" in d.stimulus


def test_viprb_marker_rejects_nonzero_or_stimulus(tmp_path: Path) -> None:
    # a biased/stimulated VIPRB would silently lose its value in translation — refuse it
    p = tmp_path / "tb_stb_bad.spice"
    p.write_text("* bad probe\nVIPRB a b dc 0.3\nR1 a 0 1k\nR2 b 0 1k\n.end\n")
    with pytest.raises(ValueError, match="VIPRB"):
        translate_ngspice_to_spectre(p, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
    p2 = tmp_path / "tb_stb_bad2.spice"
    p2.write_text("* bad probe\nVIPRB a b dc 0 ac 1\nR1 a 0 1k\nR2 b 0 1k\n.end\n")
    with pytest.raises(ValueError, match="VIPRB"):
        translate_ngspice_to_spectre(p2, pdk="tsmc-n65", source_pdk="ihp-sg13g2")
