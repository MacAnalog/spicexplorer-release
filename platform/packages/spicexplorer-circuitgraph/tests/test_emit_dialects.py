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
    # `10k` is emitted as a plain `10000`: SPICE and Spectre disagree on scale-factor case, so the
    # Spectre lane resolves every suffix rather than copying the source token through.
    assert "(" in scs and "resistor r=10000" in scs and "vsource dc=1.8" in scs
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
M1 (out in vss vss) nmos_a l=1u w=4u multi=2
M2 (out out vdd vdd) pmos_a l=1u w=8u multi=1
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
        text = to_netlist(
            g, dialect=dialect, subckt="ota", ports=["vdd", "vss", "vin", "vip", "outn"]
        )
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
    # NETS get a per-character code instead of the lossy `_` collapse (see the differential
    # test below), so `.`/`<`/`>` stay distinguishable from each other and from a literal `_`.
    assert SpectreEmitter.sanitize_net("a.b<1>") == "a_db_lb1_rb"
    assert SpectreEmitter.sanitize_net("0") == "0"  # ground stays literal


# ----------------------------------------------------------------------
# Net renaming must be injective (distinct nets in ⇒ distinct nets out)
# ----------------------------------------------------------------------
_DIFF_PAIR = """\
* differential input pair, house `+`/`-` net convention
XM1 outn vin+ tail vss sg13_lv_nmos w=10u ng=4 l=0.5u
XM2 outp vin- tail vss sg13_lv_nmos w=10u ng=4 l=0.5u
XM3 tail vbias vss vss sg13_lv_nmos w=20u ng=8 l=1u
.end
"""


def test_spectre_net_sanitization_keeps_a_differential_pair_distinct() -> None:
    """`vin+` and `vin-` must not collapse onto one node.

    Mapping every invalid character to `_` made both `vin_`, which SHORTS the two inputs of
    every differential amplifier — in a deck that still parses. `+`/`-` are the house port
    convention (`.subckt opamp vin- vin+ …`) and appear in this package's own cora fixture.
    """
    assert SpectreEmitter.sanitize_net("vin+") == "vin_p"
    assert SpectreEmitter.sanitize_net("vin-") == "vin_m"

    ports = ["vin-", "vin+", "outp", "outn", "vss"]
    scs = to_netlist(_graph(_DIFF_PAIR), dialect="spectre", subckt="opamp", ports=ports)

    header = next(ln for ln in scs.splitlines() if ln.startswith("subckt "))
    formals = header.split()[2:]
    assert len(set(formals)) == len(ports), header  # no duplicated formal port

    gates = {
        ln.split("(", 1)[1].split()[1] for ln in scs.splitlines() if ln.startswith(("XM1 ", "XM2 "))
    }
    assert gates == {"vin_p", "vin_m"}, scs


def test_emit_refuses_a_net_rename_that_would_short_two_nets() -> None:
    """The post-emit invariant: as many distinct nets out as in, or raise.

    `sanitize_net` is identity on already-legal names, so a deck that spells one net `vin+`
    and another `vin_p` still collides. FAIL LOUD — a silent short is the whole defect class.
    """
    collide = _DIFF_PAIR.replace(
        "XM3 tail", "XM4 outp vin_p tail vss sg13_lv_nmos w=1u ng=1 l=1u\nXM3 tail"
    )
    g = _graph(collide)
    with pytest.raises(ValueError, match="not injective"):
        to_netlist(g, dialect="spectre")
    # the SPICE dialect renames nothing, so the same graph still emits there
    assert "vin_p" in to_netlist(g, dialect="spice")


def test_case_only_net_duplicates_are_still_folded_not_rejected() -> None:
    """`VOUT` and `vout` ARE one node in (case-insensitive) SPICE, so folding them is the
    earlier case-folding fix. The injectivity invariant must not undo it."""
    g = _graph("* case\nR1 VOUT 0 1k\nC1 vout 0 1p\n.end\n")
    scs = to_netlist(g, dialect="spectre")
    device_lines = [ln for ln in scs.splitlines() if ln.startswith(("R1 ", "C1 "))]
    assert len(device_lines) == 2
    assert {ln.split("(", 1)[1].split(")", 1)[0] for ln in device_lines} == {"vout 0"}


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


def test_spectre_bare_symbolic_passive_is_an_expression_not_a_phantom_master() -> None:
    # LEAF-F15: `R1 a b rload` names a VALUE (ngspice needs `l=` before a passive's token can be a
    # model), so Spectre must get `resistor r=rload` — not an instance of a master called `rload`.
    # The check used to be only in `translate.py`; a direct `to_netlist` caller got the phantom.
    net = "\n".join(
        [
            "* symbolic passive fixture",
            "R1 a b rload",
            "C1 b 0 CL m=1",
            "L1 a c lval",
            "R2 c 0 rupolym l=10u w=1u",
            "V1 a 0 1",
            ".end",
        ]
    )
    g = CircuitGraph.from_netlist(NetlistView.from_string(net, dialect="spice"))
    scs = to_netlist(g, dialect="spectre")
    assert "R1 (a b) resistor r=rload" in scs
    assert "C1 (b 0) capacitor c=CL m=1" in scs
    assert "L1 (a c) inductor l=lval" in scs
    # a model-named passive carries its geometry — there the token IS the master (unchanged)
    assert "R2 (c 0) rupolym l=1e-05 w=1e-06" in scs


def test_spectre_symbolic_passive_roundtrips_back_to_spectre() -> None:
    # `resistor r=rload` read from a Spectre deck re-emits as itself, and a model-mastered passive
    # (kept as an X-instance by the reader) keeps its master.
    scs_in = "\n".join(
        [
            "simulator lang=spectre",
            "parameters rload=1k",
            "R1 (a b) resistor r=rload",
            "R2 (b 0) rppd w=1u l=2u",
            "V1 (a 0) vsource dc=1",
        ]
    )
    g = CircuitGraph.from_netlist(NetlistView.from_string(scs_in, dialect="spectre"))
    scs = to_netlist(g, dialect="spectre")
    assert "R1 (a b) resistor r=rload" in scs
    assert "XR2 (b 0) rppd l=2e-06 w=1e-06" in scs


# How the Spectre emitter reads a passive's value token — a VALUE (`resistor r=<token>`) or the
# MASTER (a model / PDK subcircuit) — one rule per row; each card sits alone in a two-line deck.
@pytest.mark.parametrize(
    ("card", "line"),
    [
        # geometry marks a model whatever its key's case (the reader keeps `L=`/`W=` as spelled)
        ("R2 c 0 rupolym L=10u W=1u", "R2 (c 0) rupolym L=1e-05 W=1e-06"),
        # either geometry key alone is enough
        ("R3 c 0 rupolym w=1u", "R3 (c 0) rupolym w=1e-06"),
        ("C4 c 0 cmim l=10u", "C4 (c 0) cmim l=1e-05"),
        # an X-prefixed passive is a PDK subcircuit: its token is the master even with no geometry
        ("XR5 c 0 rppd", "XR5 (c 0) rppd"),
        # a non-geometry parameter does not turn a symbol into a model
        ("R6 c 0 rload m=2", "R6 (c 0) resistor r=rload m=2"),
        # a number or a brace expression stays a value even on a card that carries geometry
        ("R7 c 0 1k w=2u", "R7 (c 0) resistor r=1000 w=2e-06"),
        ("R8 c 0 {rload} l=10u", "R8 (c 0) resistor r=rload l=1e-05"),
    ],
    ids=[
        "upper-case-geometry",
        "w-only",
        "l-only",
        "x-prefix",
        "m-is-not-geometry",
        "number-with-geometry",
        "brace-with-geometry",
    ],
)
def test_spectre_passive_token_is_a_value_unless_the_card_names_a_model(
    card: str, line: str
) -> None:
    g = CircuitGraph.from_netlist(
        NetlistView.from_string(f"* passive card\n{card}\nV1 c 0 1\n.end", dialect="spice")
    )
    assert line in to_netlist(g, dialect="spectre").splitlines()


def test_spectre_unknown_master_passive_without_geometry_keeps_its_master() -> None:
    # The Spectre reader keeps an unknown-master passive as an X-instance (`R2 (b 0) rppd` → XR2);
    # with no geometry to go on, only the X prefix says `rppd` is a master, not `r=rppd`.
    scs_in = "simulator lang=spectre\nR2 (b 0) rppd\nV1 (b 0) vsource dc=1\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(scs_in, dialect="spectre"))
    assert "XR2 (b 0) rppd" in to_netlist(g, dialect="spectre").splitlines()
