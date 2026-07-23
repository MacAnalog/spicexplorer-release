"""Dialect emitters: round-trips through the core dialect readers + PDK×dialect composition.

The contract is graph isomorphism (``graphs_equivalent``), not byte equality — spicelib
normalizes case and the readers rename for prefix conformance, so bytes legitimately differ.
"""

import pytest
from spicexplorer_circuitgraph import (
    SKYWATER_SKY130,
    CircuitGraph,
    SpectreEmitter,
    graphs_equivalent,
    to_netlist,
)
from spicexplorer_core.spice_engine import NetlistDialect, NetlistView

_FIVE_T = """\
* 5t ota core with load + sources
XM1 outp vin tail vss sg13_lv_nmos w=10u ng=4 l=0.5u
XM2 outn vip tail vss sg13_lv_nmos w=10u ng=4 l=0.5u
XM3 outp outp vdd vdd sg13_lv_pmos w=5u ng=2 l=0.5u
XM4 outn outp vdd vdd sg13_lv_pmos w=5u ng=2 l=0.5u
XM5 tail vbias vss vss sg13_lv_nmos w=20u ng=8 l=1u
R1 outn 0 10k
C1 outn 0 2p
V1 vdd 0 1.8
I1 vdd vbias 20u
.end
"""


def _graph(text=_FIVE_T, dialect="spice"):
    return CircuitGraph.from_netlist(NetlistView.from_string(text, dialect=dialect), name="dut")


# ----------------------------------------------------------------------
# Round-trips
# ----------------------------------------------------------------------


def test_spice_graph_roundtrips_through_spectre():
    g = _graph()
    scs = to_netlist(g, dialect="spectre")
    assert "simulator lang=spectre" in scs
    assert "(" in scs and "resistor r=10k" in scs and "vsource dc=1.8" in scs
    g2 = _graph(scs, dialect="spectre")
    assert graphs_equivalent(g, g2)


def test_spice_graph_roundtrips_through_hspice():
    g = _graph()
    sp = to_netlist(g, dialect="hspice")
    g2 = _graph(sp, dialect="hspice")
    assert graphs_equivalent(g, g2)


def test_spectre_source_roundtrips_back_to_spectre():
    scs_in = """\
subckt amp (vdd vss in out)
M1 (out in vss vss) nch_mac l=1u w=4u multi=2
M2 (out out vdd vdd) pch_mac l=1u w=8u multi=1
R1 (out vss) resistor r=100k
ends amp
"""
    v = NetlistView.from_string(scs_in, dialect="spectre")
    amp_view = v.get_subcircuit_named("amp")
    assert amp_view is not None
    g = CircuitGraph.from_netlist(amp_view, name="amp")
    scs_out = to_netlist(g, dialect="spectre")
    # `multi` reads in as an alias of m but emits back as `m=`: Spectre honors m as the
    # device multiplier while IGNORING multi with a warning on model-card MOS (proven
    # live — the old multi= re-emission silently ran every
    # multi-finger device at m=1).
    assert "m=2" in scs_out and "multi=" not in scs_out
    g2 = _graph(scs_out, dialect="spectre")
    assert graphs_equivalent(g, g2)


def test_cross_dialect_spectre_to_spice_roundtrip():
    g = _graph()
    g_spectre = _graph(to_netlist(g, dialect="spectre"), dialect="spectre")
    g_back = _graph(to_netlist(g_spectre, dialect="spice"), dialect="spice")
    assert graphs_equivalent(g, g_back)


def test_pdk_retarget_composes_with_dialect():
    g = _graph()
    scs = to_netlist(g, pdk=SKYWATER_SKY130, dialect="spectre")
    assert "sky130_fd_pr__nfet_01v8" in scs and " nf=4" in scs and " ng=" not in scs
    g2 = _graph(scs, dialect="spectre")
    assert len(g2.get_components()) == len(g.get_components())


# ----------------------------------------------------------------------
# Wrapper + identifier rules
# ----------------------------------------------------------------------


def test_subckt_wrapper_requires_ports_and_reparses():
    g = _graph()
    with pytest.raises(ValueError, match="ports"):
        to_netlist(g, dialect="spectre", subckt="ota")
    for dialect, opener in (("spice", ".subckt ota"), ("spectre", "subckt ota")):
        text = to_netlist(g, dialect=dialect, subckt="ota", ports=["vdd", "vss", "vin", "vip", "outn"])
        assert any(line.startswith(opener) for line in text.splitlines())
        v = NetlistView.from_string(text, dialect=dialect)
        assert "ota" in v.get_subcircuit_names()


def test_spectre_identifier_sanitization_leading_digit():
    assert SpectreEmitter.sanitize_ref("5t_ota") == "x5t_ota"
    assert SpectreEmitter.sanitize_ref("ota5t") == "ota5t"
    g = _graph()
    text = to_netlist(g, dialect="spectre", subckt="5t_ota", ports=["vdd", "vss"])
    assert "subckt x5t_ota" in text and "ends x5t_ota" in text


def test_default_dialect_output_unchanged():
    g = _graph()
    assert to_netlist(g) == to_netlist(g, dialect=NetlistDialect.SPICE)
    assert to_netlist(g).splitlines()[-1] == ".end"


def test_spectre_identifier_sanitization_covers_punctuation() -> None:
    # P2 live finding: `ota-5t` lexes as a subtraction in Spectre; `5t_ota` as a number.
    assert SpectreEmitter.sanitize_ref("ota-5t") == "ota_5t"
    assert SpectreEmitter.sanitize_ref("5t-ota") == "x5t_ota"
    assert SpectreEmitter.sanitize_net("a.b<1>") == "a_b_1_"
    assert SpectreEmitter.sanitize_net("0") == "0"  # ground stays literal


def test_spectre_emits_brace_expressions_as_bare_spectre_expressions() -> None:
    # `{CL}` is SPICE brace syntax; Spectre wants the bare expression (`c=CL`).
    net = "\n".join(
        [
            "* brace fixture",
            "C1 a 0 {CL}",
            "R1 a b 1k",
            ".param CL=50f",
            ".end",
        ]
    )
    g = CircuitGraph.from_netlist(NetlistView.from_string(net, dialect="spice"))
    scs = to_netlist(g, dialect="spectre")
    assert "capacitor c=CL" in scs
    assert "{" not in scs
