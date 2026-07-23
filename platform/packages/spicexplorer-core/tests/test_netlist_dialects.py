"""Tests for spicexplorer_core.spice_engine.dialects — detection + Spectre/HSPICE readers.

Hermetic (inline strings): the syntax cases mirror the constructs observed in the real
analog-db reference corpora (AnalogGym sensing-front-end, ferrosim) that these readers were
built against; the corpus-wide sweep itself lives with the circuitgraph fixtures.
"""

import pytest
from spicexplorer_core.spice_engine import (
    DialectSyntaxError,
    NetlistDialect,
    NetlistView,
    NetlistViewLike,
    detect_dialect,
    get_reader,
)

# ----------------------------------------------------------------------
# Dialect vocabulary + detection
# ----------------------------------------------------------------------


def test_coerce_accepts_ngspice_alias_and_rejects_junk():
    assert NetlistDialect.coerce("ngspice") is NetlistDialect.SPICE
    assert NetlistDialect.coerce("SPECTRE") is NetlistDialect.SPECTRE
    assert NetlistDialect.coerce(NetlistDialect.HSPICE) is NetlistDialect.HSPICE
    with pytest.raises(ValueError, match="unknown netlist dialect"):
        NetlistDialect.coerce("eldo")


def test_detect_scs_extension_wins():
    assert detect_dialect("* anything", "input.scs") is NetlistDialect.SPECTRE


def test_detect_simulator_lang_is_definitive():
    assert detect_dialect("simulator lang=spectre\n") is NetlistDialect.SPECTRE


def test_detect_spectre_by_structural_markers():
    text = "// cell\nsubckt foo a b\nM1 (a a b b) nmod l=1u\nends foo\n"
    assert detect_dialect(text) is NetlistDialect.SPECTRE


def test_detect_hspice_needs_a_strong_marker():
    assert detect_dialect("* tb\n.option post\nR1 a b 1k\n.end\n") is NetlistDialect.HSPICE
    assert detect_dialect("* tb\n.lstb mode=single\n.end\n") is NetlistDialect.HSPICE
    # weak signals alone (`.measure` also exists in ngspice) must NOT flip the default —
    # a false HSPICE positive would change behavior for existing SPICE callers.
    assert detect_dialect("* tb\n.measure ac gain max vdb(out)\n.end\n") is NetlistDialect.SPICE


def test_detect_plain_spice_default():
    assert detect_dialect("* t\nR1 a b 1k\n.end\n") is NetlistDialect.SPICE


def test_get_reader_refuses_native_dialect():
    with pytest.raises(ValueError, match="native"):
        get_reader("spice")


# ----------------------------------------------------------------------
# Spectre reader
# ----------------------------------------------------------------------
_SPECTRE_CELL = """\
// Library name: sensor
subckt ptat GND VDD VOUT
M1 (net3 net3 GND GND) nch_mac l=60n w=200n multi=2 \\
        ad=3.5e-14 as=3.5e-14
M3 (VOUT VOUT VDD VDD) pch_mac l=60n w=200n multi=1
ends ptat
"""


def _spectre_view(text):
    return NetlistView.from_string(text, dialect="spectre")


def test_spectre_subckt_paren_nodes_and_continuation():
    v = _spectre_view(_SPECTRE_CELL)
    assert v.dialect is NetlistDialect.SPECTRE
    sub = v.get_subcircuit_named("ptat")
    assert sub is not None
    assert set(sub.get_components()) == {"M1", "M3"}
    assert sub.get_component_nodes("M1") == ["net3", "net3", "GND", "GND"]
    assert sub.get_component_value("M3") == "pch_mac"
    params = {k.lower(): val for k, val in sub.get_component_parameters("M1").items()}
    assert params["m"] == 2          # multi= → m=
    assert params["ad"] == 3.5e-14   # continuation joined


def test_spectre_parameters_and_global():
    v = _spectre_view("parameters vdd=1.8 gain=2\nglobal 0 vdd\nR1 (a vdd) resistor r=1k\n")
    assert {k.lower(): val for k, val in v.get_parameters().items()} == {"vdd": "1.8", "gain": "2"}


def test_spectre_primitive_masters_become_ref_prefixed():
    v = _spectre_view(
        "r0 (a b) resistor r=100k\nc1 (b 0) capacitor c=2p\nload2 (b 0) capacitor c=1p\n"
        "v1 (vdd 0) vsource dc=1.8\nvac (in 0) vsource dc=0 mag=1\ni1 (vdd x) isource dc=100n\n"
    )
    comps = set(v.get_components())
    assert {"R0", "C1", "CLOAD2", "V1", "VAC", "I1"} <= comps
    assert v.original_name("CLOAD2") == "load2"       # prefix-conformed, original preserved
    assert v.get_component_value("R0") == "100k"
    assert v.get_component_value("VAC") == "dc 0 ac 1"  # dc/mag assembled


def test_spectre_include_and_analyses_become_directives_never_resolved():
    v = _spectre_view(
        'include "${PDK_ROOT}/models/x.scs" section=tt\n'
        "M1 (d g s b) nch_mac l=1u w=1u\n"
        "ac1 ac start=1 stop=1G\n"
        "simulatorOptions options temp=27\n"
        "save M1:all\n"
    )
    kinds = sorted(d.kind for d in v.directives)
    assert kinds == ["analysis", "analysis", "include", "option"]
    assert any("section=tt" in d.text for d in v.directives)
    assert v.get_components() == ["M1"]  # nothing structural was lost


def test_spectre_lang_switch_segments_pass_spice_through():
    v = _spectre_view(
        "simulator lang=spice\n.subckt inv a y\nM1 y a 0 0 nmod\n.ends\nsimulator lang=spectre\n"
        "x1 (in out) inv\n"
    )
    assert "X1" in v.get_components()
    assert v.get_subcircuit_names() == ["inv"]


def test_spectre_unknown_master_typing_and_name_map():
    v = _spectre_view(
        "dev1 (a b c d) mystery_model l=1u\n"   # 4 terminals → typed as MOS
        "blob (a b) mystery2 p=1\n"             # else → black box X
    )
    assert {"MDEV1", "XBLOB"} <= set(v.get_components())
    assert v.original_name("MDEV1") == "dev1"
    assert v.original_name("XBLOB") == "blob"
    assert v.original_name("R99") == "R99"  # identity for unmapped refs


def test_spectre_bus_bits_and_plus_continuations_and_numeric_master():
    v = _spectre_view(
        "M1 (out TRIM\\<1\\> 0 0) nch_mac l=30n\n"
        "pss1 pss fund=1G\n+ saveinit=yes\n"        # SPICE-style continuation in a spectre deck
        "Vref net1 0 1.4 type=dc\n"                 # SPICE shorthand line (numeric master)
    )
    assert "TRIM_1_" in v.get_all_nodes()
    assert [d.kind for d in v.directives] == ["analysis"]
    assert "saveinit=yes" in v.directives[0].text   # continuation joined into the directive
    assert "VREF" in {c.upper() for c in v.get_components()}


def test_spectre_fail_loud_on_unparseable_structural_line():
    with pytest.raises(DialectSyntaxError):
        get_reader("spectre").read("thing_with_no_master_or_params\n")


# ----------------------------------------------------------------------
# HSPICE reader
# ----------------------------------------------------------------------
_HSPICE_TB = """\
**TestBench
.PARAM supply_voltage = 1.8
.PARAM STEP_TIME = '3.2 / GBW_ideal'
.TEMP 27
.option post probe measure
.include "../dut/amp.sp"
.lib "${PDK_ROOT}/usage.l" tt_lib
VVDDA VDDA 0 supply_voltage
VVIP VIP 0 'supply_voltage *0.5' AC=1
xi1 vdda gnda vin vip vout1 AMP    *ADM
vlstb vout1 vin dc=0  $iprobe
.measure ac gain max vdb(vout1)
.lstb mode=single vsource=vlstb
.IF(RUN_TRAN==1)
.tran 1n 1u
.ENDIF
.ALTER corner_ss
.TEMP 105
.END
"""


def _hspice_view(text):
    return NetlistView.from_string(text, dialect="hspice")


def test_hspice_cards_become_directives_devices_survive():
    v = _hspice_view(_HSPICE_TB)
    assert v.dialect is NetlistDialect.HSPICE
    assert {"VVDDA", "VVIP", "XI1", "VLSTB"} <= set(v.get_components())
    kinds = {d.kind for d in v.directives}
    assert {"option", "include", "measure", "analysis", "alter"} <= kinds
    # the .ALTER block is preserved but kept out of the base deck
    alters = [d.text for d in v.directives if d.kind == "alter"]
    assert alters == [".ALTER corner_ss", ".TEMP 105"]


def test_hspice_quoted_expressions_stay_single_tokens():
    v = _hspice_view(_HSPICE_TB)
    params = {k.lower(): val for k, val in v.get_parameters().items()}
    # de-spaced and rebraced (`'…'` → `{…}`): spicelib silently DROPS single-quoted .param
    # values, so the reader must emit the brace form. The expression itself is verbatim.
    assert params["step_time"] == "{3.2/GBW_ideal}"
    # the quoted source value parses as ONE value token (the `*0.5` never became a comment)
    assert v.get_component_value("VVIP") == "{supply_voltage*0.5}"


def test_hspice_inline_comments_stripped_quote_aware():
    v = _hspice_view(_HSPICE_TB)
    assert v.get_component_nodes("XI1") == ["vdda", "gnda", "vin", "vip", "vout1"]  # *ADM gone
    assert v.get_component_value("VLSTB").lower() == "dc=0"                        # $iprobe gone


def test_hspice_bare_subckt_file_gets_end_supplied():
    v = _hspice_view(".SUBCKT amp in out\nxm1 out in 0 0 nch_mac W=1u L=1u\n.ENDS amp\n")
    assert v.get_subcircuit_names() == ["amp"]
    amp = v.get_subcircuit_named("amp")
    assert amp is not None and amp.get_component_value("XM1") == "nch_mac"


def test_hspice_eom_is_ends():
    v = _hspice_view(".SUBCKT a x y\nR1 x y 1k\n.EOM\n")
    assert v.get_subcircuit_names() == ["a"]


# ----------------------------------------------------------------------
# NetlistView integration
# ----------------------------------------------------------------------


def test_spice_path_defaults_unchanged():
    v = NetlistView.from_string("* t\nR1 a b 1k\n.end\n")
    assert v.dialect is NetlistDialect.SPICE
    assert v.directives == ()
    assert v.original_name("R1") == "R1"
    assert isinstance(v, NetlistViewLike)


def test_from_string_auto_sniffs_spectre():
    v = NetlistView.from_string(_SPECTRE_CELL, dialect="auto")
    assert v.dialect is NetlistDialect.SPECTRE


def test_metadata_propagates_on_step_in():
    v = _spectre_view(_SPECTRE_CELL + "xdut (g v o) ptat\n")
    inner = v.get_subcircuit("XDUT")
    assert inner.dialect is NetlistDialect.SPECTRE


def test_from_file_dialect_param(tmp_path):
    p = tmp_path / "cell.scs"
    p.write_text(_SPECTRE_CELL, encoding="utf-8")
    v = NetlistView.from_file(p)  # auto: .scs extension
    assert v.dialect is NetlistDialect.SPECTRE
    assert v.get_subcircuit_names() == ["ptat"]
    q = tmp_path / "amp.sp"
    q.write_text(".SUBCKT amp a b\nR1 a b 1k\n.ENDS\n", encoding="utf-8")
    v2 = NetlistView.from_file(q, dialect="hspice")  # bare-subckt HSPICE needs the explicit hint
    assert v2.get_subcircuit_names() == ["amp"]
