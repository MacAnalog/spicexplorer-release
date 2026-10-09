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
M1 (net3 net3 GND GND) nmos_a l=60n w=200n multi=2 \\
        ad=3.5e-14 as=3.5e-14
M3 (VOUT VOUT VDD VDD) pmos_a l=60n w=200n multi=1
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
    assert sub.get_component_value("M3") == "pmos_a"
    params = {k.lower(): val for k, val in sub.get_component_parameters("M1").items()}
    assert params["m"] == 2  # multi= → m=
    assert params["ad"] == 3.5e-14  # continuation joined


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
    assert v.original_name("CLOAD2") == "load2"  # prefix-conformed, original preserved
    assert v.get_component_value("R0") == "100k"
    assert v.get_component_value("VAC") == "dc 0 ac 1"  # dc/mag assembled


def test_spectre_include_and_analyses_become_directives_never_resolved():
    v = _spectre_view(
        'include "${PDK_ROOT}/models/x.scs" section=tt\n'
        "M1 (d g s b) nmos_a l=1u w=1u\n"
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
        "dev1 (a b c d) mystery_model l=1u\n"  # 4 terminals → typed as MOS
        "blob (a b) mystery2 p=1\n"  # else → black box X
    )
    assert {"MDEV1", "XBLOB"} <= set(v.get_components())
    assert v.original_name("MDEV1") == "dev1"
    assert v.original_name("XBLOB") == "blob"
    assert v.original_name("R99") == "R99"  # identity for unmapped refs


def test_spectre_bus_bits_and_plus_continuations_and_numeric_master():
    v = _spectre_view(
        "M1 (out TRIM\\<1\\> 0 0) nmos_a l=30n\n"
        "pss1 pss fund=1G\n+ saveinit=yes\n"  # SPICE-style continuation in a spectre deck
        "Vref net1 0 1.4 type=dc\n"  # SPICE shorthand line (numeric master)
    )
    assert "TRIM_1_" in v.get_all_nodes()
    assert [d.kind for d in v.directives] == ["analysis"]
    assert "saveinit=yes" in v.directives[0].text  # continuation joined into the directive
    assert "VREF" in {c.upper() for c in v.get_components()}


def test_spectre_fail_loud_on_unparseable_structural_line():
    with pytest.raises(DialectSyntaxError):
        get_reader("spectre").read("thing_with_no_master_or_params\n")


_SPECTRE_IF_ELSE = """\
V0 (a 0) vsource dc=1
R0 (a 0) resistor r=1k
if (sel == 1) {
  R1 (a b) resistor r=2k
} else {
  R1 (a b) resistor r=3k
}
"""


def test_spectre_devices_inside_an_if_block_are_refused_not_dropped():
    """SIM-D12: the whole brace block used to become one `unknown` directive, so R1 vanished from
    the circuit with only a generic warning. The taken branch depends on run-time parameters,
    so the reader refuses (the HSPICE `.if` rule) and names what it would have dropped."""
    with pytest.raises(DialectSyntaxError) as exc:
        get_reader("spectre").read(_SPECTRE_IF_ELSE)
    message = str(exc.value)
    assert "R1" in message
    assert "sel == 1" in message


def test_spectre_one_line_if_block_is_refused_too():
    deck = "R0 (a 0) resistor r=1k\nif (w_sel == 2) { M1 (d g s b) nmos_a w=1u l=1u }\n"
    with pytest.raises(DialectSyntaxError, match="M1"):
        get_reader("spectre").read(deck)


def test_spectre_braced_values_outside_a_block_are_not_dropped():
    """SIM-D12 follow-up: a balanced `{…}` value on an ordinary statement opens no block, so the
    device, parameter or model line is transformed as usual — it is not made part of an
    `unknown` directive. Only a one-line `if`/`else` is read as a block on its own line."""
    deck = (
        "V0 (a 0) vsource dc=1\n"
        "parameters rval={2*rbase} rbase=1k\n"
        "R1 (a b) resistor r={rval}\n"
        "M1 (d g 0 0) nch w={W} l=1u\n"
        "M2 d g 0 0 nch w={W}\n"
        "model nch bsim4 vth0={vt}\n"
    )
    parsed = get_reader("spectre").read(deck)
    assert ".param rval={2*rbase} rbase=1k" in parsed.canonical_text
    assert [d.kind for d in parsed.directives] == ["model"]
    assert _spectre_view(deck).get_components() == ["V0", "R1", "M1", "M2"]
    with pytest.raises(DialectSyntaxError, match="R1"):
        get_reader("spectre").read(
            "V0 (a 0) vsource dc=1\nif (sel == 1) { R1 (a b) resistor r={rval} }\n"
        )


def test_spectre_brace_blocks_without_devices_stay_directives():
    """What real decks put in braces — statistics, a paramset table, a montecarlo block of
    analyses, an `if` guarding an analysis — holds no device and is still kept as a directive."""
    deck = (
        "R0 (a 0) resistor r=1k\n"
        "statistics {\n  process {\n    vary rsh dist=gauss std=0.1\n  }\n}\n"
        "paramSet1tran paramset {\ntime  maxstep  reltol\n0     1p       1E-4\n}\n"
        "mc1 montecarlo numruns=200 seed=1 {\ndcOp dc maxiters=200\n"
        "finalTimeOP info what=oppoint where=rawfile\n}\n"
        "if (run_tran == 1) {\n  tran1 tran stop=1n\n}\n"
    )
    parsed = get_reader("spectre").read(deck)
    assert [d.kind for d in parsed.directives] == ["unknown"] * 4
    assert _spectre_view(deck).get_components() == ["R0"]


def test_spectre_if_else_refusal_names_each_instance_once():
    # R1 sits in both arms; the message lists what would be dropped, not every occurrence.
    with pytest.raises(DialectSyntaxError) as exc:
        get_reader("spectre").read(_SPECTRE_IF_ELSE)
    assert str(exc.value).count("R1") == 1


def test_spectre_else_arm_on_its_own_line_is_checked_too():
    """`}` closes the `if` arm (analyses only, so it is a harmless directive), and `else {` then
    opens a block of its own. That block is a conditional too: its devices are refused."""
    deck = (
        "V0 (a 0) vsource dc=1\n"
        "if (sel == 1) {\n  tran1 tran stop=1n\n}\n"
        "else {\n  R1 (a b) resistor r=3k\n}\n"
    )
    with pytest.raises(DialectSyntaxError, match="R1") as exc:
        get_reader("spectre").read(deck)
    assert "else" in str(exc.value)


@pytest.mark.parametrize(
    "line",
    [
        "if(w_sel==2){ M1 (d g s b) nmos_a w=1u l=1u }",
        "if (a == 1) { R1 (a b) resistor r=1k } else { R2 (a b) resistor r=2k }",
        "if (a == 1) { if (b == 1) { R1 (a b) resistor r=1k } }",
    ],
)
def test_spectre_one_line_conditional_spellings_are_refused(line):
    with pytest.raises(DialectSyntaxError) as exc:
        get_reader("spectre").read("R0 (a 0) resistor r=1k\n" + line + "\n")
    message = str(exc.value)
    assert "M1" in message or "R1" in message
    if "R2" in line:
        assert "R1, R2" in message


def test_spectre_unterminated_if_block_with_a_device_is_refused():
    """A deck that ends inside an `if` block (a missing `}`) must not keep its devices in an
    opaque directive either."""
    with pytest.raises(DialectSyntaxError, match="R1"):
        get_reader("spectre").read(
            "R0 (a 0) resistor r=1k\nif (sel == 1) {\n  R1 (a b) resistor r=2k\n"
        )


def test_spectre_unterminated_block_without_devices_stays_a_directive():
    parsed = get_reader("spectre").read(
        "R0 (a 0) resistor r=1k\nif (sel == 1) {\n  tran1 tran stop=1n\n"
    )
    assert [d.kind for d in parsed.directives] == ["unknown"]
    assert "unterminated brace block preserved as a directive" in parsed.warnings


def test_spectre_conditional_of_analyses_models_and_saves_is_kept():
    """Only instances are refused. An `if` may pick an analysis — named with a node list
    (`noise1 (out 0) noise …`) or not — or a model card, an include, a save list, an option.
    Read bare, `model nch bsim4 vth0=…` and `save a b c` look like instances (a name, nodes, a
    master), so the keyword heads must be told apart first. Whether models and includes inside a
    conditional should also be refused (HSPICE refuses them) is an open question (WP-05 Next
    Steps); today they are kept."""
    deck = (
        "R0 (a 0) resistor r=1k\n"
        "if (corner == 1) {\n"
        "  noise1 (out 0) noise start=1 stop=1G\n"
        "  xf1 (out 0) xf start=1 stop=1G\n"
        "  model nch bsim4 vth0=0.4\n"
        '  include "corners.scs" section=tt\n'
        "  save a b c\n"
        "  simOpts options reltol=1e-4\n"
        "}\n"
    )
    parsed = get_reader("spectre").read(deck)
    assert [d.kind for d in parsed.directives] == ["unknown"]
    assert _spectre_view(deck).get_components() == ["R0"]


def test_spectre_deck_subckt_named_like_an_analysis_is_a_device_in_a_conditional():
    """A deck's own subckt shadows an analysis keyword (as it does in `_transform`), so an
    instance of a subckt called `ac` inside an `if` is a device and is refused."""
    deck = (
        "subckt ac (a b)\n  R0 (a b) resistor r=1k\nends ac\n"
        "V0 (n1 0) vsource dc=1\n"
        "if (use_ac == 1) {\n  X1 (n1 0) ac\n}\n"
    )
    with pytest.raises(DialectSyntaxError, match="X1"):
        get_reader("spectre").read(deck)


def test_spectre_quoted_braces_neither_open_nor_close_a_block():
    """Brace detection skips quoted text. A lone `{` inside a quoted option value must not open a
    block around the devices after it, and one inside a block must not keep it open."""
    deck = (
        "V0 (a 0) vsource dc=1\n"
        'simOpts options title="corner {tt"\n'
        "R1 (a 0) resistor r=1k\n"
        "if (run_tran == 1) {\n"
        '  tran1 tran stop=1n title="tran {"\n'
        "}\n"
        "R2 (a 0) resistor r=2k\n"
    )
    parsed = get_reader("spectre").read(deck)
    assert [d.kind for d in parsed.directives] == ["analysis", "unknown"]
    assert _spectre_view(deck).get_components() == ["V0", "R1", "R2"]


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
    assert v.get_component_value("VLSTB").lower() == "dc=0"  # $iprobe gone


def test_hspice_bare_subckt_file_gets_end_supplied():
    v = _hspice_view(".SUBCKT amp in out\nxm1 out in 0 0 nmos_a W=1u L=1u\n.ENDS amp\n")
    assert v.get_subcircuit_names() == ["amp"]
    amp = v.get_subcircuit_named("amp")
    assert amp is not None and amp.get_component_value("XM1") == "nmos_a"


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


# ----------------------------------------------------------------------
# HSPICE conditional assembly — DIA-01 / CG-02
# ----------------------------------------------------------------------
# `.if/.elseif/.else/.endif` were classified as removable `option` directives, so the CARDS were
# dropped while the device lines between them fell through as ordinary devices. Every branch's
# devices then landed in one circuit, in parallel — a deck that still simulates, and is not the
# circuit anyone wrote. `DialectSyntaxError` exists for exactly this ("fail-loud, never drop
# devices"); the branch actually taken depends on parameter values the reader does not evaluate,
# so there is no correct answer to give and the only honest move is to refuse.

CONDITIONAL_DECK = """* hspice deck with a conditional
.param mode=1
vdd vdd 0 1.8
.if (mode == 1)
r_taken in out 1k
.else
r_not_taken in out 999meg
c_not_taken out 0 1p
.endif
r_load out 0 10k
.end
"""


def test_conditional_assembly_is_refused_not_merged():
    reader = get_reader(NetlistDialect.HSPICE)
    with pytest.raises(DialectSyntaxError) as exc:
        reader.read(CONDITIONAL_DECK)
    message = str(exc.value)
    assert "r_taken" in message, "the message must name the device it refused to merge"
    # The message must tell the caller what to do about it, not just what went wrong.
    assert "resolve" in message.lower() or "expand" in message.lower()


def test_every_branch_opener_refuses_a_guarded_device():
    """Each card that OPENS an arm guards what follows it — `.elseif` and `.else` included."""
    reader = get_reader(NetlistDialect.HSPICE)
    for card in (".if (a==1)", ".elseif (a==2)", ".else"):
        deck = f"* d\nr1 in out 1k\n{card}\nr2 out 0 1k\n.end\n"
        with pytest.raises(DialectSyntaxError):
            reader.read(deck)


def test_a_stray_endif_closes_nothing_and_refuses_nothing():
    """`.endif` ends an arm, so a device after it is unguarded — refusing there would be noise."""
    reader = get_reader(NetlistDialect.HSPICE)
    deck = reader.read("* d\nr1 in out 1k\n.endif\nr2 out 0 1k\n.end\n")
    assert "r2 out 0 1k" in deck.canonical_text


def test_a_conditional_guarding_only_directives_is_accepted_and_reported():
    """The real-corpus pattern: `.IF(RUN_TRAN==1) / .tran / .ENDIF`.

    Nothing structural is inside, so no devices merge and the circuit is unaffected. Refusing here
    would break decks these readers were built against for no correctness gain — but the branch is
    still not evaluated, so it is surfaced as a `conditional` directive plus a warning instead of
    being silently classified `option` and dropped, which is what hid it before.
    """
    reader = get_reader(NetlistDialect.HSPICE)
    deck = reader.read("* d\nr1 in out 1k\n.IF(RUN_TRAN==1)\n.tran 1n 1u\n.ENDIF\n.end\n")
    assert "r1 in out 1k" in deck.canonical_text
    kinds = [d.kind for d in deck.directives]
    assert kinds.count("conditional") == 2, "the .IF and .ENDIF cards must both be visible"
    assert any("NOT evaluated" in w for w in deck.warnings)


def test_the_refusal_names_the_devices_that_would_have_been_merged():
    """A caller staring at a 4000-line deck needs to know WHERE, not just THAT."""
    reader = get_reader(NetlistDialect.HSPICE)
    with pytest.raises(DialectSyntaxError) as exc:
        reader.read(CONDITIONAL_DECK)
    assert "mode == 1" in str(exc.value)


def test_a_deck_without_conditionals_is_unaffected():
    reader = get_reader(NetlistDialect.HSPICE)
    deck = reader.read("* plain\n.param mode=1\nr1 in out 1k\nr2 out 0 10k\n.end\n")
    assert "r1 in out 1k" in deck.canonical_text
    assert "r2 out 0 10k" in deck.canonical_text


def test_a_conditional_inside_an_alter_block_does_not_refuse():
    """`.alter` is a separate run: its statements never enter the base deck, so nothing merges.

    The refusal is scoped to the defect — devices from several branches sharing one circuit — and
    an `.alter` body is already held out of the canonical text, so there is nothing to refuse.
    """
    reader = get_reader(NetlistDialect.HSPICE)
    deck = reader.read("* d\nr1 in out 1k\n.alter\n.if (mode == 1)\nr2 out 0 1k\n.endif\n.end\n")
    assert "r2 out 0 1k" not in deck.canonical_text
    assert "r1 in out 1k" in deck.canonical_text


# ----------------------------------------------------------------------
# DIA-02 — NetlistView.from_string must not write to the filesystem
# ----------------------------------------------------------------------
# `from_string` is documented as parse-only, and every dialect path funnels through it, but it used
# to spool the text to a NamedTemporaryFile just so spicelib could read it back. On a shared host
# that means netlist text — which on the Spectre lane can be kit-adjacent — briefly lands in a
# world-readable temp dir on every parse, and `delete=False` leaves a window where a killed process
# leaks the file. spicelib's parser accepts any iterator of lines, so no file was ever needed.


def _no_tempfiles(monkeypatch):
    """Make any attempt to create a temp file a loud failure."""
    import tempfile as _tf

    def _boom(*a, **k):  # noqa: ANN002, ANN003
        raise AssertionError("from_string wrote to the filesystem")

    monkeypatch.setattr(_tf, "NamedTemporaryFile", _boom)
    monkeypatch.setattr(_tf, "mkstemp", _boom)
    monkeypatch.setattr(_tf, "TemporaryDirectory", _boom)


def test_from_string_parses_without_touching_the_filesystem(monkeypatch):
    _no_tempfiles(monkeypatch)
    v = NetlistView.from_string("* d\nr1 in out 1k\nr2 out 0 1k\n.end\n")
    assert set(v.get_components()) == {"R1", "R2"}
    assert v.get_component_value("R1") == "1k"


def test_in_memory_parse_handles_subcircuits_and_continuations(monkeypatch):
    _no_tempfiles(monkeypatch)
    text = (
        "* d\n"
        ".subckt amp in out\n"
        "xm1 out in 0 0 nmos_a W=1u\n"
        "+ L=180n\n"
        ".ends amp\n"
        "xi1 a b amp\n"
        ".end\n"
    )
    v = NetlistView.from_string(text)
    assert v.get_subcircuit_names() == ["amp"]
    amp = v.get_subcircuit_named("amp")
    assert amp is not None
    # the `+` continuation was folded into the device line, not left as its own statement:
    # the parameter it carried is readable alongside the one from the first line
    assert amp.get_component_parameters("XM1")["L"] == "180n"
    assert amp.get_component_parameters("XM1")["W"] == "1u"
    assert amp.get_component_value("XM1") == "nmos_a"


def test_the_dialect_path_is_file_free_too(monkeypatch):
    """`_from_deck` funnels through `from_string`, so HSPICE/Spectre parses inherit the fix."""
    _no_tempfiles(monkeypatch)
    v = NetlistView.from_string("* d\nr1 in out 1k\n.end\n", dialect="hspice")
    assert v.dialect is NetlistDialect.HSPICE
    assert set(v.get_components()) == {"R1"}


def test_a_conditional_choosing_between_model_libraries_is_refused():
    """Corner selection is the same defect wearing different clothes.

    Keeping both arms leaves two `.model` cards for one device and two corner `.lib` sections in
    the same deck — a circuit nobody wrote, exactly as with merged devices, even though nothing
    structural appears between the conditional cards.
    """
    reader = get_reader(NetlistDialect.HSPICE)
    for guarded in ('.lib "models.l" tt', ".model nch nmos level=54 vth0=0.4", '.include "ss.sp"'):
        deck = f"* d\nr1 in out 1k\n.if (corner == 1)\n{guarded}\n.endif\n.end\n"
        with pytest.raises(DialectSyntaxError):
            reader.read(deck)


def test_libraries_outside_a_conditional_are_untouched():
    """The corpus fixture's `.include`/`.lib` sit outside its `.IF` — they must keep working."""
    reader = get_reader(NetlistDialect.HSPICE)
    deck = reader.read(
        '* d\n.include "../dut/amp.sp"\n.lib "pdk.l" tt\nr1 in out 1k\n'
        ".IF(RUN_TRAN==1)\n.tran 1n 1u\n.ENDIF\n.end\n"
    )
    assert [d.kind for d in deck.directives].count("include") == 2
    assert "r1 in out 1k" in deck.canonical_text


def test_the_acceptance_warning_does_not_overclaim():
    """It may promise the CIRCUIT is intact; it must not imply the analyses are conditional."""
    reader = get_reader(NetlistDialect.HSPICE)
    deck = reader.read("* d\nr1 in out 1k\n.IF(RUN_TRAN==1)\n.tran 1n 1u\n.ENDIF\n.end\n")
    warning = next(w for w in deck.warnings if "NOT evaluated" in w)
    assert "regardless of its condition" in warning
