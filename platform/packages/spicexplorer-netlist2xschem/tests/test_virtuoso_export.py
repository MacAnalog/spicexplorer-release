"""virtuoso_export (xvport) — offline tests over real corpus fixtures.

The fixtures are verbatim copies of analog-db circuits (`amp_001_5t.sch`, the ccia-02
`transmission_gate_pair.sch`); the expected pin→net tables below are their electrical ground
truth (a 5T OTA / a transmission gate), which is what pins the geometric net extractor.
The emitter tests assert structure + determinism of the `.il` artifact, not full golden text.

Live counterpart (needs the CIW daemon): both fixtures were built on IC23.1 2026-07-16 —
schCheck 0 errors / 0 warnings, with all terminal bindings and CDF-callback behavior
verified live.
"""

import math
import re
import shutil
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem.sch_parser import parse_sch
from spicexplorer_netlist2xschem.virtuoso_export import (
    ORIENT_TABLE,
    emit_schematic_il,
    extract_nets,
    load_device_map,
    orient_for,
)
from spicexplorer_netlist2xschem.virtuoso_export.symlib import symlib_for_source
from spicexplorer_netlist2xschem.virtuoso_export.xform import to_cadence

FIXTURES = Path(__file__).parent / "fixtures" / "xvport"


def _load(name: str):
    src = FIXTURES / name
    return parse_sch(src.read_text(encoding="utf-8")), symlib_for_source(src)


# --- xform -------------------------------------------------------------------


def test_orient_table_complete_and_frozen():
    assert set(ORIENT_TABLE) == {(r, f) for r in range(4) for f in (0, 1)}
    # The live-verified assignments (IC23.1 2026-07-16). Changing any entry requires
    # re-running the live orient verification AND the corpus regression in test_geometry.py.
    assert orient_for(0, 0) == "R0"
    assert orient_for(1, 0) == "R270"
    assert orient_for(2, 0) == "R180"
    assert orient_for(3, 0) == "R90"
    assert orient_for(0, 1) == "MY"
    assert orient_for(1, 1) == "MXR90"
    assert orient_for(2, 1) == "MX"
    assert orient_for(3, 1) == "MYR90"


def test_to_cadence_lands_on_snap_grid():
    # xschem grid 5 x default scale 0.0125 == the 0.0625 Cadence snap.
    x, y = to_cadence(5, -5)
    assert (x, y) == (0.0625, 0.0625)


# --- net extraction (corpus ground truth) --------------------------------------

TGATE_EXPECTED = {
    ("M1", "D"): "port_A",
    ("M1", "S"): "port_B",
    ("M1", "G"): "vctl",
    ("M1", "B"): "VSS",
    ("M2", "D"): "port_B",
    ("M2", "S"): "port_A",
    ("M2", "G"): "vctl_not",
    ("M2", "B"): "VDD",
}

AMP001_EXPECTED = {
    ("M1", "D"): "outm",
    ("M1", "G"): "vinp",
    ("M1", "S"): "tail",
    ("M1", "B"): "vss",
    ("M2", "D"): "vout",
    ("M2", "G"): "vinn",
    ("M2", "S"): "tail",
    ("M2", "B"): "vss",
    ("M3", "D"): "outm",
    ("M3", "G"): "outm",
    ("M3", "S"): "vdd",
    ("M3", "B"): "vdd",
    ("M4", "D"): "vout",
    ("M4", "G"): "outm",
    ("M4", "S"): "vdd",
    ("M4", "B"): "vdd",
    ("M5", "D"): "tail",
    ("M5", "G"): "ibias",
    ("M5", "S"): "vss",
    ("M5", "B"): "vss",
    ("M6", "D"): "ibias",
    ("M6", "G"): "ibias",
    ("M6", "S"): "vss",
    ("M6", "B"): "vss",
}


@pytest.mark.parametrize(
    ("fixture", "expected", "ports"),
    [
        (
            "transmission_gate_pair.sch",
            TGATE_EXPECTED,
            {"port_A", "port_B", "vctl", "vctl_not", "VDD", "VSS"},
        ),
        ("amp_001_5t.sch", AMP001_EXPECTED, {"vinp", "vinn", "vout", "ibias"}),
    ],
)
def test_net_extraction_matches_electrical_ground_truth(fixture, expected, ports):
    sch, symlib = _load(fixture)
    nx = extract_nets(sch, symlib)
    actual = {k: pn.net for k, pn in nx.pin_nets.items()}
    assert actual == expected
    assert {p.name for p in nx.ports} == ports
    assert nx.warnings == []
    # No synthesized nets: every pin sits on a drawn, named net in these fixtures.
    assert not [n for n in nx.nets if n.startswith("net_")]


def test_extraction_prefers_human_label_over_xschem_auto_name():
    # chopper-diff has one net whose wires still carry the CACHED auto-label '#net2'
    # while a human 'Vctl_not' label component names it. Cached wire ``lab=`` attrs are
    # not electrical labels (xschem regenerates them and ignores stale ones): they must
    # neither name the net nor reach the multiple-labels warning path — a stale cached
    # name once by-name-MERGED two distinct nets (the vo1p/VDD port regression).
    sch, symlib = _load("chopper-diff.sch")
    nx = extract_nets(sch, symlib)
    assert "Vctl_not" in nx.nets
    assert "#net2" not in nx.nets
    assert not any("multiple labels" in w for w in nx.warnings)


def test_extraction_rot_flip_devices_have_wire_following_stubs():
    sch, symlib = _load("transmission_gate_pair.sch")
    nx = extract_nets(sch, symlib)
    for pn in nx.pin_nets.values():
        assert pn.stub_dir in {(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)}


# --- emitter --------------------------------------------------------------------


def test_emit_tgate_structure_and_determinism():
    sch, symlib = _load("transmission_gate_pair.sch")
    devmap = load_device_map()
    r1 = emit_schematic_il(sch, lib="LIBX", cell="tgate", devmap=devmap, symlib=symlib)
    r2 = emit_schematic_il(sch, lib="LIBX", cell="tgate", devmap=devmap, symlib=symlib)
    assert r1.il == r2.il  # deterministic artifact

    assert r1.instances == {"M1": ("FOUNDRY_KIT", "nmos_lvt"), "M2": ("FOUNDRY_KIT", "pmos_lvt")}
    assert r1.expected_bindings[("M1", "G")] == "vctl"
    assert r1.expected_bindings[("M2", "B")] == "VDD"
    assert set(r1.expected_ports) == {"port_A", "port_B", "vctl", "vctl_not", "VDD", "VSS"}
    assert r1.expected_ports["port_A"] == "input"

    il = r1.il
    # placement with the live-verified orient (rot=3 flip=0 -> R90; rot=3 flip=1 -> MYR90)
    assert '"M1" list(7.375 3.25) "R90"' in il
    assert '"M2" list(7.375 7) "MYR90"' in il
    # CDF params go through the callback-firing helper, never dbReplaceProp-only; the
    # multiplier lands on simM (the netlister's m<-simM — CDF m is callback-derived).
    assert (
        'xvSetParams(cv "M1" list(list("fingers" "1") list("l" "0.13u") list("simM" "1") list("w" "0.15u")))'
        in il
    )
    # every terminal gets a labeled stub; interface pins exist for every port
    assert il.count('xvLabelTerm(cv "') == 8
    assert il.count("schCreatePin(") == 6
    assert "schCheck(cv)" in il and "dbSave(cv)" in il


def test_custom_map_extends_the_builtin_generic_rules(tmp_path):
    """#205: --map used to REPLACE the built-ins, so a kit map's capacitors went nowhere.

    A commercial kit's map has to exist (the generic lane's whole premise), and it covers the
    kit's own devices. Dropping analogLib with it sent a CDAC slice's two MOM capacitors to
    `<target-lib>/capa_np` — a master nothing creates — and the port died inside Virtuoso.
    """
    kit = tmp_path / "kit.yaml"
    kit.write_text(
        "devices:\n"
        '  - match: "*/nmos4.sym"\n'
        "    lib: KITLIB\n"
        "    cell: nmos_hvt\n"
        "    terms: {d: D, g: G, s: S, b: B}\n"
        "kit_libs: [KITLIB]\n"
    )
    dm = load_device_map(kit)

    def rule(symref):
        r = dm.lookup(symref)
        assert r is not None, symref
        return r

    # the caller's own rule still wins, and is tried first
    assert rule("devices/nmos4.sym").cell == "nmos_hvt"
    # ...and the analogLib primitives it never mentioned are still there
    assert rule("devices/capa.sym").lib == "analogLib"
    assert rule("devices/res.sym").cell == "res"
    assert rule("devices/vsource.sym").lib == "analogLib"
    # the NDA denylist is a UNION: naming your own kit lib must not drop the built-in ones
    assert "KITLIB" in dm.kit_libs and "FOUNDRY_KIT" in dm.kit_libs
    # the IHP->FOUNDRY_KIT MOS rules are NOT appended: an uncovered MOSFET must fail, never
    # resolve to another kit's master
    assert dm.lookup("sg13g2_pr/sg13_lv_nmos.sym") is None


def test_map_replace_restores_the_old_replacing_behaviour(tmp_path):
    kit = tmp_path / "kit.yaml"
    kit.write_text('devices:\n  - match: "*/nmos4.sym"\n    lib: KITLIB\n    cell: nmos_hvt\n')
    dm = load_device_map(kit, extend=False)
    kept = dm.lookup("devices/nmos4.sym")
    assert kept is not None and kept.cell == "nmos_hvt"
    assert dm.lookup("devices/capa.sym") is None  # exactly what #205 reported
    assert dm.lookup("devices/res.sym") is None


def test_extending_keeps_an_explicit_empty_globals(tmp_path):
    """`globals: {}` is how a caller says "this sheet has no globals" — extension respects it."""
    kit = tmp_path / "kit.yaml"
    kit.write_text("devices: []\nglobals: {}\n")
    assert load_device_map(kit).globals == {}
    kit.write_text("devices: []\n")
    assert load_device_map(kit).globals == {"0": "gnd!"}


def test_emit_unmapped_symref_is_an_error_not_a_warning():
    """A symref no rule matches and nothing creates cannot be ported (#205).

    It used to become a local master in the target library with only a warning, so the `.il`
    was written and loaded, and Virtuoso failed at the closing paren of the outermost form
    naming nothing. The emitter knows what it could not resolve; it says so and refuses.
    """
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="chopper_diff", devmap=load_device_map(), symlib=symlib
    )
    assert r.instances["x1"] == ("LIBX", "transmission_gate_pair")
    assert not any("unmapped symref" in w for w in r.warnings)
    assert any("no map rule for symref" in e for e in r.errors), r.errors
    assert any("transmission_gate_pair" in e for e in r.errors)


def test_a_code_shown_directives_block_is_not_a_device():
    """#215: a bench carries its simulator directives in a `devices/code_shown.sym` block.

    It is `code.sym`'s "show the text on the sheet *and* netlist it" variant — an annotation,
    not a circuit element. Treated as a device it became a `code_shown` cell invented in the
    target (shared, durable) OA library, and the directive text was dropped on the way with
    only a warning.
    """
    sch, symlib = _load("tb_code_shown.sch")
    assert sch.component("directives") is not None  # it IS on the sheet
    assert "directives" not in {c.name for c in sch.devices}
    r = emit_schematic_il(
        # cell name deliberately free of "code_shown" — the `.il` mentions the cell it builds
        sch,
        lib="LIBX",
        cell="tb_directives",
        devmap=load_device_map(),
        symlib=symlib,
    )
    assert r.errors == [], r.errors
    assert ("LIBX", "code_shown") not in r.instances.values()
    assert "code_shown" not in r.il
    assert not any("directives" in w for w in r.warnings), r.warnings


def test_emit_local_master_is_fine_when_this_run_creates_it():
    """The same fallback is correct when the hierarchy walk ports the symbol — no error."""
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="chopper_diff",
        devmap=load_device_map(),
        symlib=symlib,
        local_cells={"transmission_gate_pair"},
    )
    assert r.instances["x1"] == ("LIBX", "transmission_gate_pair")
    assert not r.errors, r.errors


def test_a_scale_that_packs_instances_is_refused():
    """#204: --scale scales the PLACEMENT; the masters and the stubs keep their own size.

    Tightening --scale is the obvious remedy for the default's airy sheet, and it is the one
    that silently rewires the circuit: at 0.004 five BULK terminals landed on the wrong nets
    while every device kept its model and w/l/m, so a per-device parameter diff passed it.
    """
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="chopper_diff",
        devmap=load_device_map(),
        symlib=symlib,
        scale=0.003,
    )
    msg = next((e for e in r.errors if "minimum" in e), "")
    assert msg, r.errors
    assert "--scale 0.003" in msg
    assert "silently rewire" in msg
    assert "Raise --scale to at least" in msg  # and it computes the number for you
    assert "--allow-dense" in msg


def test_allow_dense_downgrades_the_refusal_to_a_warning():
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="chopper_diff",
        devmap=load_device_map(),
        symlib=symlib,
        scale=0.003,
        allow_dense=True,
    )
    assert not any("minimum" in e for e in r.errors), r.errors
    assert any("--allow-dense" in w for w in r.warnings)


def test_the_default_scale_is_accepted():
    """The known-good configuration must stay silent, or the guard is useless.

    Calibration note: this fixture's tightest pair sits at 3.26 units at the default scale and
    at 1.04 at 0.004 — just ABOVE the 1.0 floor — which is why the refusal tests use 0.003.
    """
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="chopper_diff", devmap=load_device_map(), symlib=symlib
    )
    assert not any("minimum" in e for e in r.errors), r.errors


def test_the_stub_shrinks_with_a_tight_pitch():
    """Below the default pitch the stub shrinks with it instead of staying 0.25 units."""
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="chopper_diff",
        devmap=load_device_map(),
        symlib=symlib,
        scale=0.002,
        allow_dense=True,
    )
    stubs = re.findall(
        r'xvLabelTerm\(cv "[^"]*" "[^"]*" "[^"]*" [-0-9.]+ [-0-9.]+ ([0-9.]+)\)', r.il
    )
    assert stubs, r.il[:400]
    assert all(float(s) < 0.25 for s in stubs), sorted(set(stubs))


def test_emit_per_finger_width_and_simM_multiplier():
    # IHP xschem w is TOTAL width; FOUNDRY_KIT CDF w is PER-FINGER (wf = w*fingers), and the
    # netlister's multiplier is simM. M1 (w=2u ng=2 m=3) must emit w=1u fingers=2 simM=3;
    # M2's symbolic total (w=wtot ng=4) is undividable -> drop w with a warning rather
    # than netlist at 4x the intended size.
    sch, symlib = _load("mos_fingered.sch")
    r = emit_schematic_il(sch, lib="LIBX", cell="fingered", devmap=load_device_map(), symlib=symlib)
    il = r.il
    assert (
        'xvSetParams(cv "M1" list(list("fingers" "2") list("l" "0.13u") '
        'list("simM" "3") list("w" "1u")))'
    ) in il
    assert (
        'xvSetParams(cv "M2" list(list("fingers" "4") list("l" "0.13u") list("simM" "1")))'
    ) in il
    assert any("per-finger" in w and "M2" in w for w in r.warnings)
    assert 'list("m"' not in il  # CDF m is a silent no-op — never write it


def test_a_symbolic_param_value_fails_the_port_unless_the_caller_opts_in():
    """It used to be a WARNING the port returned 0 alongside (issue #182).

    Cadence makes a design variable out of an unresolved word, so the ported device is sized
    by whatever that variable holds — a cellview that looks built and is not the circuit. The
    value is still written (it is what localises the problem) and `--allow-symbolic` accepts
    it deliberately, but the default verdict is failure.
    """
    sch, symlib = _load("amp_001_5t.sch")
    strict = emit_schematic_il(sch, lib="LIBX", cell="amp", devmap=load_device_map(), symlib=symlib)
    assert any("symbolic parameter" in e for e in strict.errors)
    assert not any("symbolic parameter" in w for w in strict.warnings)
    assert len(strict.expected_bindings) == 24

    opted_in = emit_schematic_il(
        sch, lib="LIBX", cell="amp", devmap=load_device_map(), symlib=symlib, symbolic=True
    )
    assert any("symbolic parameter" in w for w in opted_in.warnings)
    assert opted_in.errors == []
    assert opted_in.il == strict.il  # the opt-in changes the verdict, never the artifact


def test_a_device_whose_symbol_does_not_resolve_fails_the_port():
    """It used to be a WARNING the port returned 0 alongside (issue #226).

    An instance whose ``symref`` resolves to nothing was DROPPED: the `.il` built a cellview
    with fewer components than the sheet has, and the netcheck agreed with it, because both
    ends were derived from the same unresolvable source. A comparator bench ported green with
    no comparator in it. A DEVICE that does not resolve is therefore an error — the `.il` is
    still written (it localises the problem), but nothing is loaded.

    An ANNOTATION whose symbol does not resolve (title/code/noconn) stays harmless: it is not
    a circuit element, so ``is_device`` is False and no error is raised for it.
    """
    sch, symlib = _load("tb_missing_dut.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="tb_missing_dut", devmap=load_device_map(), symlib=symlib
    )
    assert r.dropped == ["XCMP"]
    dut_errors = [e for e in r.errors if "XCMP" in e]
    assert len(dut_errors) == 1, r.errors
    assert "sar_cmp.sym" in dut_errors[0]
    assert "searched" in dut_errors[0]  # the roots that were tried, so the fix is obvious
    # the artifact is still emitted, and the instance is NOT in it
    assert 'dbOpenCellViewByType("LIBX" "tb_missing_dut"' in r.il
    assert "XCMP" not in r.instances
    # an unresolvable title block is an annotation, not a dropped device
    assert not any("TITLE" in e or "title.sym" in e for e in r.errors), r.errors
    assert "TITLE" not in r.dropped
    # the resolvable devices still ported
    assert set(r.instances) == {"VIN", "RL"}


# --- device map ------------------------------------------------------------------


def test_default_map_covers_fixture_devices_and_denylists_kit():
    m = load_device_map()
    rule = m.lookup("sg13g2_pr/sg13_lv_nmos.sym")
    assert rule is not None and (rule.lib, rule.cell) == ("FOUNDRY_KIT", "nmos_lvt")
    pmos = m.lookup("devices/sg13_lv_pmos_np.sym")
    assert pmos is not None and pmos.cell == "pmos_lvt"
    vsrc = m.lookup("devices/vsource.sym")
    assert vsrc is not None and vsrc.cell == "vdc"
    # bare basenames (no directory) must match too — corpus files reference both ways
    bare = m.lookup("capa.sym")
    assert bare is not None and bare.cell == "cap"
    assert m.lookup("not/mapped.sym") is None
    assert m.is_kit_lib("FOUNDRY_KIT") and not m.is_kit_lib("MYLIB")


def test_generic_lane_flavours_route_to_distinct_masters(tmp_path):
    """One symref, two kit devices — the generic lane's whole problem.

    A commercial kit's sheet draws every MOSFET with ``devices/{n,p}mos4.sym`` and carries
    the device on the instance (``model=``). Without an attribute key both flavours collapse
    onto whichever rule is listed first, silently.
    """
    f = tmp_path / "generic.yaml"
    f.write_text(
        """
devices:
  - match: "*/pmos4.sym"
    attrs: {model: pmos_lvt}
    lib: KITLIB
    cell: pmos_lvt
    symref: devices/pmos4.sym
    terms: {d: D, g: G, s: S, b: B}
    params: {w: w, l: l, m: simM, nf: fingers}
  - match: "*/pmos4.sym"
    lib: KITLIB
    cell: pch
    symref: devices/pmos4.sym
    terms: {d: D, g: G, s: S, b: B}
""",
        encoding="utf-8",
    )
    m = load_device_map(f)

    def cell_for(attrs=None):
        rule = m.lookup("devices/pmos4.sym", attrs)
        assert rule is not None, f"no rule matched {attrs}"
        return rule.cell

    assert cell_for({"model": "pmos_lvt"}) == "pmos_lvt"
    assert cell_for({"model": "PMOS_LVT"}) == "pmos_lvt"  # SPICE folds model-card case
    assert cell_for({"model": "pch"}) == "pch"  # falls through to the catch-all
    # a rule that asks a question about the instance must not match a caller with no answer
    assert cell_for() == "pch"


def test_attr_rule_never_matches_without_attrs():
    from spicexplorer_netlist2xschem.virtuoso_export.devmap import DeviceRule

    r = DeviceRule(match="*/nmos4.sym", lib="KITLIB", cell="nmos_lvt", attrs={"model": "nmos_lvt"})
    assert r.matches("devices/nmos4.sym", {"model": "nmos_lvt"})
    assert not r.matches("devices/nmos4.sym", {"model": "nch"})
    assert not r.matches("devices/nmos4.sym", {})
    assert not r.matches("devices/nmos4.sym")
    assert not r.matches("devices/pmos4.sym", {"model": "nmos_lvt"})
    # the reverse direction stamps an exact constraint back; a glob only says what is accepted
    assert r.literal_attrs() == {"model": "nmos_lvt"}
    glob = DeviceRule(match="x", lib="K", cell="c", attrs={"model": "nch*"})
    assert glob.literal_attrs() == {}


def test_map_yaml_roundtrip(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.devmap import DEFAULT_MAP_YAML

    f = tmp_path / "map.yaml"
    f.write_text(DEFAULT_MAP_YAML, encoding="utf-8")
    m = load_device_map(f)
    rule = m.lookup("sg13g2_pr/sg13_lv_nmos.sym")
    assert rule is not None and rule.terms["D"] == "D"


# --- symbol emitter ----------------------------------------------------------


def test_emit_symbol_chopper_diff_structure():
    from spicexplorer_netlist2xschem.virtuoso_export.symbols import emit_symbol_il_from_text

    text = (FIXTURES / "chopper-diff.sym").read_text(encoding="utf-8")
    r1 = emit_symbol_il_from_text(text, lib="LIBX", cell="chopper_diff")
    r2 = emit_symbol_il_from_text(text, lib="LIBX", cell="chopper_diff")
    assert r1.il == r2.il  # deterministic

    # the 8 pins, in xschem record order (= @pinlist = termOrder)
    assert r1.term_order == [
        "Vctl",
        "VDD",
        "VB_p",
        "VA_p",
        "Vctl_not",
        "VSS",
        "VB_n",
        "VA_n",
    ]
    assert r1.terms["VDD"] == "inputOutput"
    il = r1.il
    assert il.count("dbCreateLine(") == 36  # 36 L records (body + pin leads)
    assert il.count("dbCreatePin(") == 8
    assert il.count("dbCreateEllipse(") == 1  # the 360-degree A record (clock bubble)
    assert '"logical label" \n' not in il
    assert "[@partName]" in il and "[@instanceName]" in il  # @symname/@name texts
    assert "schCreateSymbolLabel(cv" in il and '"pin name"' in il
    assert 'list("instance" "drawing")' in il  # selection box
    assert "cv~>termOrder" in il
    assert "schSymbolToPinList" in il and "dbSave(cv)" in il


def test_parse_sym_arc_and_polygon_records():
    from spicexplorer_netlist2xschem.sch_parser import parse_sch

    text = (FIXTURES / "chopper-diff.sym").read_text(encoding="utf-8")
    sym = parse_sch(text)
    assert len(sym.arcs) == 1
    arc = sym.arcs[0]
    assert (arc.cx, arc.cy, arc.a2) == (180.0, -15.0, 360.0)
    poly = parse_sch("P 4 4 0 0 10 0 10 10 0 10 {}\n")
    assert poly.polygons[0].points == ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0))


def test_with_symbols_dependency_walk_orders_leaves_first():
    from spicexplorer_netlist2xschem.virtuoso_export.cli import _collect_dependencies
    from spicexplorer_netlist2xschem.virtuoso_export.devmap import load_device_map

    warnings: list[str] = []
    errors: list[str] = []
    seen = {"chopper_diff_top"}
    builds, _sch = _collect_dependencies(
        FIXTURES / "chopper-diff.sch", load_device_map(), 0.0125, "LIBX", seen, warnings, errors
    )
    kinds = [(k, c) for k, c, *_ in builds]
    # chopper-diff.sch instantiates transmission_gate_pair (sym + sibling .sch) only.
    assert ("sch", "transmission_gate_pair") in kinds
    assert ("sym", "transmission_gate_pair") in kinds
    # every build carries its source path (netcheck resolves sources from here)
    assert all(src.exists() for _k, _c, _r, src in builds)
    # scheduled local cells do not produce "unmapped symref" warnings
    assert not [w for w in warnings if "unmapped" in w]
    assert errors == []


# --- wire mode ----------------------------------------------------------------


def test_emit_wire_mode_draws_split_segments_and_labels_every_island():
    sch, symlib = _load("amp_001_5t.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="amp", devmap=load_device_map(), symlib=symlib, mode="wires"
    )
    il = r.il
    # real wires drawn, terminals patched geometrically (all amp_001 pins sit on wires)
    assert il.count("schCreateWire(") > 30
    assert il.count('xvPatchTerm(cv "') == 24
    assert 'xvLabelTerm(cv "' not in il
    # vss is drawn as multiple disjoint islands -> each needs its own label
    assert il.count('"vss" "lowerCenter"') >= 2
    # same bindings as labels mode
    assert r.expected_bindings[("M1", "G")] == "vinp"


def test_emit_wire_mode_stubs_label_only_pins():
    # chopper-diff.sch binds the tgate control pins via labels-on-wires but some nets are
    # label-only at pins; every pin NOT touching a wire must fall back to a named stub.
    sch, symlib = _load("chopper-diff.sch")
    nx = extract_nets(sch, symlib)
    off_wire = [k for k, pn in nx.pin_nets.items() if not pn.on_wire]
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="chopper_diff",
        devmap=load_device_map(),
        symlib=symlib,
        mode="wires",
        local_cells={"transmission_gate_pair"},
    )
    assert r.il.count('xvLabelTerm(cv "') == len(off_wire)
    assert r.il.count('xvPatchTerm(cv "') == len(nx.pin_nets) - len(off_wire)


# --- hardening (review F5-F9) ---------------------------------------------------------

_SCH_SKEL = "v {xschem version=3.4.5 file_version=1.2\n}\nG {}\nK {}\nV {}\nS {}\nE {}\n"


def _emit_text(sch_text: str, **kwargs):
    sch = parse_sch(_SCH_SKEL + sch_text)
    symlib = symlib_for_source(FIXTURES / "transmission_gate_pair.sch")
    return emit_schematic_il(
        sch, lib="LIBX", cell="t", devmap=load_device_map(), symlib=symlib, **kwargs
    )


def test_f5_instance_name_collision_gets_deterministic_suffix():
    # 'M.1' and 'M_1' both sanitize to 'M_1' — a silent collapse would drop a device
    r = _emit_text(
        "C {sg13g2_pr/sg13_lv_nmos.sym} 0 0 0 0 {name=M.1}\n"
        "C {sg13g2_pr/sg13_lv_nmos.sym} 200 0 0 0 {name=M_1}\n"
    )
    assert set(r.instances) == {"M_1", "M_1_2"}
    assert any("instance name collision" in w for w in r.warnings)


def test_f5_net_name_collision_gets_deterministic_suffix():
    # each labeled wire ends on a device gate pin (G is at (-20, 0) of the nmos symbol)
    # so both nets participate; 'n#1' and 'n.1' both sanitize to 'n_1'
    r = _emit_text(
        "N -60 0 -20 0 {\nlab=n#1}\n"
        "N 140 0 180 0 {\nlab=n.1}\n"
        "C {sg13g2_pr/sg13_lv_nmos.sym} 0 0 0 0 {name=M1}\n"
        "C {sg13g2_pr/sg13_lv_nmos.sym} 200 0 0 0 {name=M2}\n"
    )
    assert any("net name collision" in w for w in r.warnings)
    assert '"n_1"' in r.il and '"n_1_2"' in r.il


def test_f5_local_prefix_applies_to_local_masters_and_cellname():
    from spicexplorer_netlist2xschem.virtuoso_export.cli import _cellname

    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="chop",
        devmap=load_device_map(),
        symlib=symlib,
        local_prefix="xv_",
    )
    assert r.instances["x1"] == ("LIBX", "xv_transmission_gate_pair")
    assert _cellname("chopper-diff", "xv_") == "xv_chopper_diff"


def test_f6_unmapped_instance_params_warn_as_dropped():
    r = _emit_text("C {transmission_gate_pair.sym} 0 0 0 0 {name=x1 gain=2}\n")
    assert any("NOT transferred" in w and "gain" in w for w in r.warnings)


def test_f7_duplicate_instance_names_warn():
    sch = parse_sch(
        _SCH_SKEL
        + "C {sg13g2_pr/sg13_lv_nmos.sym} 0 0 0 0 {name=M1}\n"
        + "C {sg13g2_pr/sg13_lv_nmos.sym} 100 0 0 0 {name=M1}\n"
    )
    nx = extract_nets(sch, symlib_for_source(FIXTURES / "transmission_gate_pair.sch"))
    assert any("duplicate instance name 'M1'" in w for w in nx.warnings)


def test_f8_partial_arc_emits_polyline_with_correct_endpoints():
    from spicexplorer_netlist2xschem.virtuoso_export.symbols import emit_symbol_il_from_text

    sym = (
        _SCH_SKEL
        + "A 4 0 0 40 0 90 {}\n"
        + "B 5 -2.5 -2.5 2.5 2.5 {name=A dir=in}\n"
        + "T {@symname} 0 -50 0 0 0.2 0.2 {}\n"
    )
    r = emit_symbol_il_from_text(sym, lib="LIBX", cell="arcy")
    assert "dbCreateEllipse(" not in r.il  # 90-degree sweep is NOT a full ellipse
    # angles are CCW-on-screen in the y-down frame: theta=0 -> (cx+r, cy) = (40, 0);
    # theta=90 -> (cx, cy-r) = (0, -40). Cadence side: scale 0.0125 + y negation.
    import re

    polylines = [
        re.findall(r"list\(([-\d.e]+) ([-\d.e]+)\)", ln)
        for ln in r.il.splitlines()
        if "dbCreateLine(" in ln
    ]
    arc_pts = next(pts for pts in polylines if len(pts) > 2)
    xs = [float(a) for a, _ in arc_pts]
    ys = [float(b) for _, b in arc_pts]
    assert abs(xs[0] - 0.5) < 1e-9 and abs(ys[0]) < 1e-9  # start (0.5, 0)
    assert abs(xs[-1]) < 1e-9 and abs(ys[-1] - 0.5) < 1e-9  # end (0, 0.5)


def test_f9_off_grid_wire_coordinates_warn():
    sch = parse_sch(_SCH_SKEL + "N 0.3 0 10 0 {\nlab=a}\n")
    nx = extract_nets(sch, symlib_for_source(FIXTURES / "transmission_gate_pair.sch"))
    assert any("off-grid" in w for w in nx.warnings)


# --- reverse — offline: denylist, inverse transforms, record emission -------------


def test_reverse_nda_denylist_enforced_before_any_client_call():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        XvportNDAError,
        cv2sch,
        cv2sym,
    )

    m = load_device_map()
    # client=None: a denylist breach MUST raise before the client is ever touched
    with pytest.raises(XvportNDAError):
        cv2sym(None, "FOUNDRY_KIT", "nmos_lvt", m)
    with pytest.raises(XvportNDAError):
        cv2sch(None, "analogLib", "vccs", m)


def test_reverse_params_invert_simM_and_per_finger():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import _reverse_params

    rule = load_device_map().lookup("sg13g2_pr/sg13_lv_nmos.sym")
    assert rule is not None
    warnings: list[str] = []
    attrs = _reverse_params(
        rule, {"w": "1u", "l": "130n", "simM": "3", "fingers": "2", "wf": "2u"}, warnings, "M1"
    )
    # per-finger CDF w=1u x fingers=2 -> xschem TOTAL w=2u; simM -> m; wf (derived) dropped
    assert attrs == {"w": "2u", "l": "130n", "m": "3", "ng": "2"}
    assert warnings == []


def test_reverse_emit_sch_text_round_trips_through_the_forward_extractor():
    # a synthetic dump equivalent to the tgate cellview: same wires won't be reproduced,
    # but instances + pins + labels must re-extract to the SAME pin->net partition.
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        DumpInstance,
        SchDump,
        emit_sch_text,
    )
    from spicexplorer_netlist2xschem.virtuoso_export.xform import to_cadence

    def cad(x, y):
        return to_cadence(x, y)

    dump = SchDump(
        # one label per net at each device pin location (G of both devices)
        labels=[
            (*cad(590, -240), "vctl"),
            (*cad(590, -580), "vctl_not"),
            (*cad(560, -280), "port_A"),
            (*cad(620, -280), "port_B"),
            (*cad(560, -540), "port_A"),
            (*cad(620, -540), "port_B"),
            (*cad(590, -280), "VSS"),
            (*cad(590, -540), "VDD"),
        ],
        pins=[
            ("port_A", "input", *cad(380, -400)),
            ("port_B", "input", *cad(740, -400)),
            ("vctl", "input", *cad(520, -180)),
            ("vctl_not", "input", *cad(410, -620)),
            ("VDD", "input", *cad(590, -460)),
            ("VSS", "input", *cad(590, -340)),
        ],
        instances=[
            DumpInstance(
                "M1",
                "FOUNDRY_KIT",
                "nmos_lvt",
                *cad(590, -260),
                "R90",
                {"w": "150n", "l": "130n", "simM": "1", "fingers": "1"},
            ),
            DumpInstance(
                "M2",
                "FOUNDRY_KIT",
                "pmos_lvt",
                *cad(590, -560),
                "MYR90",
                {"w": "150n", "l": "130n", "simM": "1", "fingers": "1"},
            ),
        ],
    )
    text, warnings = emit_sch_text(dump, load_device_map(), lib="xvport_dev")
    assert warnings == []
    # the kit masters map back to their concrete symrefs with inverse orient + params
    assert "C {sg13g2_pr/sg13_lv_nmos.sym} 590 -260 3 0 {name=M1" in text
    assert "C {sg13g2_pr/sg13_lv_pmos.sym} 590 -560 3 1 {name=M2" in text
    assert "m=1" in text and "ng=1" in text and "w=150n" in text
    # and the emitted .sch re-extracts to the original electrical partition
    sch = parse_sch(text)
    nx = extract_nets(sch, symlib_for_source(FIXTURES / "transmission_gate_pair.sch"))
    assert {k: pn.net for k, pn in nx.pin_nets.items()} == TGATE_EXPECTED


def test_reverse_stamps_the_generic_lane_flavour_back_onto_the_instance(tmp_path):
    """A generic-lane rule is discriminated by an attribute the symref cannot carry.

    Both flavours come back as ``devices/pmos4.sym``, so without the stamp the round trip
    loses which kit device the instance was — the reverse of the forward gap.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        DumpInstance,
        SchDump,
        emit_sch_text,
    )

    f = tmp_path / "generic.yaml"
    f.write_text(
        """
devices:
  - match: "*/pmos4.sym"
    attrs: {model: pmos_lvt}
    lib: KITLIB
    cell: pmos_lvt
    symref: devices/pmos4.sym
    terms: {d: D, g: G, s: S, b: B}
    params: {w: w, l: l}
  - match: "*/pmos4.sym"
    attrs: {model: pch}
    lib: KITLIB
    cell: pch
    symref: devices/pmos4.sym
    terms: {d: D, g: G, s: S, b: B}
    params: {w: w, l: l}
""",
        encoding="utf-8",
    )
    dump = SchDump(
        labels=[],
        pins=[],
        instances=[
            DumpInstance("M1", "KITLIB", "pmos_lvt", 0, 0, "R0", {"w": "2u", "l": "1u"}),
            DumpInstance("M2", "KITLIB", "pch", 100, 0, "R0", {"w": "2u", "l": "1u"}),
        ],
    )
    text, _ = emit_sch_text(dump, load_device_map(f), lib="MYLIB")
    # same symref both times — the flavour survives only because it is stamped back
    assert text.count("C {devices/pmos4.sym}") == 2
    assert "model=pmos_lvt" in text
    m2 = text.split("name=M2")[1]
    assert "model=pch\n" in m2 and "model=pmos_lvt" not in m2


def test_reverse_emit_sym_text_shapes_and_pin_order():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import SymDump, emit_sym_text
    from spicexplorer_netlist2xschem.virtuoso_export.xform import to_cadence

    dump = SymDump(
        lines=[[to_cadence(0, 0), to_cadence(40, 0)]],
        ellipses=[(*to_cadence(10, -10), *to_cadence(20, -20))],
        labels=[(*to_cadence(0, -30), "[@partName]"), (*to_cadence(0, -40), "A")],
        pins=[("B", "inputOutput", *to_cadence(-20, 0)), ("A", "input", *to_cadence(20, 0))],
    )
    text, warnings = emit_sym_text(dump)
    assert "L 4 0 0 40 0 {}" in text
    assert "A 4 15 -15 5 0 360 {}" in text  # ellipse bbox -> full-sweep arc record
    assert "T {@symname}" in text  # NLP label mapped back
    # dumped pin order == termOrder == the @pinlist order: B first, then A
    assert text.index("{name=B dir=inout}") < text.index("{name=A dir=in}")
    assert warnings == []


def test_reverse_dump_parsers_handle_canned_records():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import dump_schematic

    class _FakeResult:
        status = type("S", (), {"value": "success"})()
        errors: list = []
        output = (
            '"W 0.5 0.0 0.5 1.0\\n'
            "L 0.5 0.5 vctl\\n"
            "P vctl input 0.5 1.0\\n"
            "I M1 FOUNDRY_KIT nmos_lvt 7.375 3.25 R90\\n"
            'M M1 simM 3\\n"'
        )

    class _FakeClient:
        def execute_skill(self, skill, timeout=120):
            assert "xvport_dev" in skill
            return _FakeResult()

    d = dump_schematic(_FakeClient(), "xvport_dev", "tgate", load_device_map())
    assert d.wires == [[(0.5, 0.0), (0.5, 1.0)]]
    assert d.labels == [(0.5, 0.5, "vctl")]
    assert d.pins == [("vctl", "input", 0.5, 1.0)]
    assert d.instances[0].name == "M1" and d.instances[0].params == {"simM": "3"}


# --- reverse: symbol arcs + the cv2sch hierarchy walk (recorded SKILL output) -----------

_OPEN = re.compile(r'dbOpenCellViewByType\("([^"]*)" "([^"]*)" "([^"]*)"')


class _RecordedSkill:
    """A bridge client that answers each dump from recorded output keyed by (lib, cell, view).

    ``None`` answers like the daemon does for a missing view (the dump's own ``error(...)``,
    worded as each SKILL dump words it); an ``Exception`` value answers with that failure text
    instead (a timeout, a broken CDF — anything that is not a missing view). Every opened
    cellview is logged in ``opened``; a KIT_LIB cellview is refused HERE, inside
    ``execute_skill``, so a walk that asks for one fails the test.
    """

    def __init__(self, views: dict[tuple[str, str, str], str | Exception | None]):
        self.views = views
        self.opened: list[tuple[str, str, str]] = []

    def execute_skill(self, skill, timeout=120):
        m = _OPEN.search(skill)
        assert m is not None, skill
        key = (m[1], m[2], m[3])
        assert "KITLIB" not in key, f"a kit cellview was dumped: {key}"
        self.opened.append(key)
        text = self.views.get(key)
        ok = isinstance(text, str)
        body = text if isinstance(text, str) else ""
        if isinstance(text, Exception):
            error = str(text)
        elif key[2] == "symbol":
            error = f"xvport: symbol view not found: {key[0]}/{key[1]}"
        else:
            error = f"xvport: cellview not found: {key[0]}/{key[1]}"

        class _Result:
            status = type("S", (), {"value": "success" if ok else "failure"})()
            errors = [] if ok else [error]
            output = '"' + body.replace("\n", "\\n") + '"'

        return _Result()


def _kit_map(tmp_path):
    f = tmp_path / "kit.yaml"
    f.write_text(
        "devices:\n"
        '  - match: "*/nmos4.sym"\n'
        "    lib: KITLIB\n"
        "    cell: nch\n"
        "    symref: devices/nmos4.sym\n"
        "    terms: {d: D, g: G, s: S, b: B}\n"
        "    params: {w: w, l: l}\n"
        "kit_libs: [KITLIB]\n",
        encoding="utf-8",
    )
    return load_device_map(f)


_SUB_SYM = (
    "SR -0.5 -0.5 0.5 0.5\n"
    "SA -0.25 -0.25 0.25 0.25 0.0 1.5707963267948966\n"
    "LB 0.0 0.75 [@partName]\n"
    "P in input -0.5 0.0\n"
    "P out output 0.5 0.0\n"
)


def test_reverse_symbol_arc_dumps_and_emits_an_xschem_A_record():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import _SYM_DUMP, cv2sym, dump_symbol
    from spicexplorer_netlist2xschem.virtuoso_export.symbols import emit_symbol_il_from_text

    # the SKILL side reads the arc's own geometry, not its drawn bBox
    assert '("arc"' in _SYM_DUMP
    assert all(a in _SYM_DUMP for a in ("~>ellipseBBox", "~>startAngle", "~>stopAngle"))

    client = _RecordedSkill({("MYLIB", "cap", "symbol"): _SUB_SYM})
    dump = dump_symbol(client, "MYLIB", "cap", load_device_map())
    assert dump.arcs == [(-0.25, -0.25, 0.25, 0.25, 0.0, 1.5707963267948966)]

    text, warnings = cv2sym(client, "MYLIB", "cap", load_device_map())
    # ellipseBBox (+-0.25 user units) -> centre (0, 0), r 20; a quarter sweep from 0 rad
    assert "A 4 0 0 20 0 90 {}" in text
    assert warnings == []
    # and the forward port keeps it: the quarter arc starts and ends where the dump's did
    fwd = emit_symbol_il_from_text(text, lib="MYLIB", cell="cap")
    arc = next(
        re.findall(r"list\(([-\d.e]+) ([-\d.e]+)\)", ln)
        for ln in fwd.il.splitlines()
        if "dbCreateLine(" in ln and ln.count("list(") > 4
    )
    (x0, y0), (x1, y1) = map(float, arc[0]), map(float, arc[-1])
    assert (round(x0, 9), round(y0, 9)) == (0.25, 0.0)
    assert (round(x1, 9), round(y1, 9)) == (0.0, 0.25)


def test_reverse_symbol_arc_sweep_wraps_and_unread_shapes_warn():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        _SYM_DUMP,
        SymDump,
        emit_sym_text,
    )

    # stop < start (the arc crosses the +x axis): the sweep is still the CCW way round
    dump = SymDump(arcs=[(-0.25, -0.25, 0.25, 0.25, 4.71238898038469, 1.5707963267948966)])
    text, _ = emit_sym_text(dump)
    assert "A 4 0 0 20 270 180 {}" in text

    # a device-layer shape the dump has no branch for used to be dropped with no warning
    assert "(t " in _SYM_DUMP
    _, warnings = emit_sym_text(SymDump(skipped=["path", "path", "donut"]))
    assert any("path" in w and "2" in w for w in warnings)
    assert any("donut" in w for w in warnings)


def test_reverse_cv2sch_with_symbols_walks_the_user_hierarchy_never_a_kit_master(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import cv2sch_hierarchy

    dm = _kit_map(tmp_path)
    client = _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): (
                "P vin input 0.0 0.0\n"
                "I X1 MYLIB sub 1.0 0.0 R0\n"
                "I X2 MYLIB sub 3.0 0.0 R0\n"  # a second instance of one master: dumped once
                "I M1 KITLIB nch 2.0 0.0 R0\n"  # mapped kit master: back through the table
                "I M9 KITLIB secret 4.0 0.0 R0\n"  # UNMAPPED kit master: still never dumped
            ),
            ("MYLIB", "sub", "schematic"): "I M2 KITLIB nch 0.0 0.0 R0\n",
            ("MYLIB", "sub", "symbol"): _SUB_SYM,
        }
    )
    files, warnings = cv2sch_hierarchy(client, "MYLIB", "top", dm)

    # a 2-level hierarchy is 3 files: the top sheet, and the sub-cell's symbol + sheet
    assert list(files) == ["top.sch", "sub.sym", "sub.sch"]
    assert "C {sub.sym} 80 0 0 0 {name=X1" in files["top.sch"]
    assert "C {devices/nmos4.sym}" in files["sub.sch"]
    assert "A 4 0 0 20 0 90 {}" in files["sub.sym"]
    # the exact, ordered log: each master opened ONCE (X2 re-uses X1's dump), symbol before
    # sheet, and neither kit master asked for
    assert client.opened == [
        ("MYLIB", "top", "schematic"),
        ("MYLIB", "sub", "symbol"),
        ("MYLIB", "sub", "schematic"),
    ]
    # exactly two warnings, both about the unmapped kit master: the mapped one (M1) and the
    # repeated instance (X2) are silent
    assert warnings == [
        "instance M9: master KITLIB/secret has no reverse mapping — emitted as a local "
        "secret.sym reference",
        "KITLIB/secret: not dumped — 'KITLIB' is in the kit_libs NDA denylist; map the master "
        "in the device table to port its instances",
    ]


def test_reverse_cv2sch_with_symbols_refuses_a_kit_top_before_any_call(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        XvportNDAError,
        cv2sch_hierarchy,
    )

    with pytest.raises(XvportNDAError):
        cv2sch_hierarchy(None, "KITLIB", "nch", _kit_map(tmp_path))


def test_reverse_cv2sch_with_symbols_ports_a_symbol_only_master_and_says_so(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import cv2sch_hierarchy

    client = _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): "I X1 MYLIB model 0.0 0.0 R0\n",
            ("MYLIB", "model", "symbol"): _SUB_SYM,
            ("MYLIB", "model", "schematic"): None,  # a behavioural cell: symbol, no sheet
        }
    )
    files, warnings = cv2sch_hierarchy(client, "MYLIB", "top", _kit_map(tmp_path))
    assert list(files) == ["top.sch", "model.sym"]
    assert any("MYLIB/model" in w and "no schematic view" in w for w in warnings)


def test_cli_cv2sch_with_symbols_writes_the_hierarchy_next_to_the_output(tmp_path, monkeypatch):
    from spicexplorer_netlist2xschem.virtuoso_export import runner
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    client = _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): "I X1 MYLIB sub 1.0 0.0 R0\n",
            ("MYLIB", "sub", "schematic"): "I M2 KITLIB nch 0.0 0.0 R0\n",
            ("MYLIB", "sub", "symbol"): _SUB_SYM,
        }
    )
    monkeypatch.setattr(runner, "connect", lambda **_kw: client)
    _kit_map(tmp_path)
    out = tmp_path / "out" / "top_port.sch"
    out.parent.mkdir()
    rc = main(
        [
            "cv2sch",
            "MYLIB",
            "top",
            "--map",
            str(tmp_path / "kit.yaml"),
            "--with-symbols",
            "-o",
            str(out),
        ]
    )
    assert rc == 0
    assert sorted(p.name for p in out.parent.iterdir()) == ["sub.sch", "sub.sym", "top_port.sch"]
    assert "C {sub.sym}" in out.read_text()


def test_cli_cv2sch_with_symbols_refuses_an_output_a_sub_cell_would_overwrite(
    tmp_path, monkeypatch, capsys
):
    from spicexplorer_netlist2xschem.virtuoso_export import runner
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    client = _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): "I X1 MYLIB sub 1.0 0.0 R0\n",
            ("MYLIB", "sub", "schematic"): "I M2 KITLIB nch 0.0 0.0 R0\n",
            ("MYLIB", "sub", "symbol"): _SUB_SYM,
        }
    )
    monkeypatch.setattr(runner, "connect", lambda **_kw: client)
    _kit_map(tmp_path)
    out = tmp_path / "sub.sch"  # the top named like its own sub-cell's sheet
    rc = main(
        [
            "cv2sch",
            "MYLIB",
            "top",
            "--map",
            str(tmp_path / "kit.yaml"),
            "--with-symbols",
            "-o",
            str(out),
        ]
    )
    # writing both would leave the SUB-cell's sheet under the name asked for the top
    assert rc == 2
    assert "sub.sch" in capsys.readouterr().err
    assert not out.exists()
    # refused BEFORE the first write: not even the sub-cell's symbol was left behind
    assert sorted(p.name for p in tmp_path.iterdir()) == ["kit.yaml"]


# --- reverse: arc angles, unread shapes, the SKILL record (edge cases) ------------------


def _arc_endpoints(il: str) -> tuple[tuple[float, float], tuple[float, float]]:
    """First and last point of the forward port's arc polyline (the one many-point line)."""
    pts = next(
        re.findall(r"list\(([-\d.e]+) ([-\d.e]+)\)", ln)
        for ln in il.splitlines()
        if "dbCreateLine(" in ln and ln.count("list(") > 4
    )
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    return (round(float(x0), 9), round(float(y0), 9)), (round(float(x1), 9), round(float(y1), 9))


@pytest.mark.parametrize(
    ("start", "stop", "a1", "sweep"),
    [
        (0.0, 0.0, "0", "360"),  # start == stop is a whole circle, never an empty arc
        (0.0, 2 * math.pi, "0", "360"),  # one full turn
        (-math.pi / 2, 0.0, "270", "90"),  # a negative start normalises into [0, 360)
        (3 * math.pi, 3.5 * math.pi, "180", "90"),  # a start past one turn does too
        # a start that ROUNDS to 360 is written as 0 (xschem's start is in [0, 360))
        (2 * math.pi - 1e-9, 2 * math.pi - 1e-9 + math.pi / 2, "0", "90"),
    ],
    ids=["closed", "full-turn", "negative-start", "past-a-turn", "rounds-to-360"],
)
def test_reverse_symbol_arc_angles_normalise_into_xschem_range(start, stop, a1, sweep):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import SymDump, emit_sym_text

    text, warnings = emit_sym_text(SymDump(arcs=[(-0.25, -0.25, 0.25, 0.25, start, stop)]))
    assert f"A 4 0 0 20 {a1} {sweep} {{}}" in text
    assert warnings == []


def test_reverse_symbol_arc_off_centre_keeps_its_place_through_both_ports():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import SymDump, emit_sym_text
    from spicexplorer_netlist2xschem.virtuoso_export.symbols import emit_symbol_il_from_text

    # centre (0.75, 0.75), r 0.25 user units; a quarter from 90 deg to 180 deg (top -> left)
    text, warnings = emit_sym_text(SymDump(arcs=[(0.5, 0.5, 1.0, 1.0, math.pi / 2, math.pi)]))
    # the y-negation moves the centre to (60, -60); the angles stay as drawn
    assert "A 4 60 -60 20 90 90 {}" in text
    assert warnings == []
    start, end = _arc_endpoints(emit_symbol_il_from_text(text, lib="MYLIB", cell="cap").il)
    assert start == (0.75, 1.0)
    assert end == (0.5, 0.75)


def test_reverse_symbol_arc_on_an_elliptical_box_is_approximated_and_says_so():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import SymDump, emit_sym_text

    # a 1.0 x 0.5 box: xschem arcs are circular, so the radius is the mean half-axis (30)
    text, warnings = emit_sym_text(SymDump(arcs=[(0.0, 0.0, 1.0, 0.5, 0.0, math.pi)]))
    assert "A 4 40 -20 30 0 180 {}" in text
    assert warnings == ["non-circular arc approximated by a circular arc in the .sym"]


def test_reverse_symbol_dump_reports_each_unread_shape_type_by_name():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import cv2sym, dump_symbol

    # the SKILL `t` branch writes `SX <objType>` for a device-layer shape it has no case for
    client = _RecordedSkill(
        {("MYLIB", "cap", "symbol"): "SX path\nSX donut\nSX path\nSX\n" + _SUB_SYM}
    )
    dump = dump_symbol(client, "MYLIB", "cap", load_device_map())
    assert dump.skipped == ["path", "donut", "path", "?"]
    assert len(dump.arcs) == 1 and len(dump.rects) == 1  # the known shapes are still read

    text, warnings = cv2sym(client, "MYLIB", "cap", load_device_map())
    tail = "not ported — the symbol dump has no branch for that shape type"
    # one warning per shape TYPE, counted, in a stable (sorted) order
    assert warnings == [
        f"1 device-layer '?' shape(s) {tail}",
        f"1 device-layer 'donut' shape(s) {tail}",
        f"2 device-layer 'path' shape(s) {tail}",
    ]
    assert "A 4 0 0 20 0 90 {}" in text


def test_reverse_symbol_skill_arc_record_matches_the_parser_field_order():
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import _SYM_DUMP

    skill = " ".join(_SYM_DUMP.split())
    # SA x1 y1 x2 y2 start stop — the order dump_symbol stores and emit_sym_text unpacks
    assert (
        'sprintf(out "%sSA %L %L %L %L %L %L\\n" out '
        "xCoord(car(sh~>ellipseBBox)) yCoord(car(sh~>ellipseBBox)) "
        "xCoord(cadr(sh~>ellipseBBox)) yCoord(cadr(sh~>ellipseBBox)) "
        "sh~>startAngle sh~>stopAngle)"
    ) in skill
    # a device-layer LABEL is written by the separate `LB` branch; without its own `nil` case
    # the catch-all would also report every label as an unported `SX label` shape
    label, catch_all = skill.index('("label" nil)'), skill.index('(t sprintf(out "%sSX %s')
    assert skill.index("case(sh~>objType") < label < catch_all
    assert 'when(sh~>objType == "label"' in skill


# --- reverse: the cv2sch --with-symbols walk (edge cases) ------------------------------


def _walk_map(tmp_path):
    """``_kit_map`` plus one USER-library master the table maps back (a characterised res)."""
    f = tmp_path / "walk.yaml"
    f.write_text(
        "devices:\n"
        '  - match: "*/nmos4.sym"\n'
        "    lib: KITLIB\n"
        "    cell: nch\n"
        "    symref: devices/nmos4.sym\n"
        "    terms: {d: D, g: G, s: S, b: B}\n"
        "    params: {w: w, l: l}\n"
        '  - match: "*/myres.sym"\n'
        "    lib: MYLIB\n"
        "    cell: res\n"
        "    symref: devices/res.sym\n"
        "    terms: {P: PLUS, M: MINUS}\n"
        "    params: {value: r}\n"
        "kit_libs: [KITLIB]\n",
        encoding="utf-8",
    )
    return load_device_map(f)


def test_reverse_cv2sch_with_symbols_walks_depth_first_through_every_level(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import cv2sch_hierarchy

    client = _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): (
                "I X1 MYLIB mid 0.0 0.0 R0\n"
                "I R1 MYLIB res 1.0 0.0 R0\n"  # a USER-lib master the table maps: not walked
                "I X2 MYLIB b 2.0 0.0 R0\n"
            ),
            ("MYLIB", "mid", "symbol"): _SUB_SYM,
            ("MYLIB", "mid", "schematic"): "I X3 USRLIB leaf 0.0 0.0 R0\n",
            ("USRLIB", "leaf", "symbol"): "SX path\n" + _SUB_SYM,
            ("USRLIB", "leaf", "schematic"): (
                "I X4 USRLIB tiny 0.0 0.0 R0\nI M2 KITLIB nch 1.0 0.0 R0\n"
            ),
            ("USRLIB", "tiny", "symbol"): _SUB_SYM,
            ("USRLIB", "tiny", "schematic"): None,
            ("MYLIB", "b", "symbol"): _SUB_SYM,
            ("MYLIB", "b", "schematic"): "I M3 KITLIB nch 0.0 0.0 R45\n",
        }
    )
    files, warnings = cv2sch_hierarchy(client, "MYLIB", "top", _walk_map(tmp_path))

    # depth-first: everything under mid (leaf, then leaf's tiny) before mid's sibling b
    assert list(files) == [
        "top.sch",
        "mid.sym",
        "mid.sch",
        "leaf.sym",
        "leaf.sch",
        "tiny.sym",
        "b.sym",
        "b.sch",
    ]
    assert client.opened == [
        ("MYLIB", "top", "schematic"),
        ("MYLIB", "mid", "symbol"),
        ("MYLIB", "mid", "schematic"),
        ("USRLIB", "leaf", "symbol"),
        ("USRLIB", "leaf", "schematic"),
        ("USRLIB", "tiny", "symbol"),
        ("USRLIB", "tiny", "schematic"),
        ("MYLIB", "b", "symbol"),
        ("MYLIB", "b", "schematic"),
    ]  # MYLIB/res is never opened: it is written as its rule's symref
    assert "C {devices/res.sym} 80 0 0 0 {name=R1" in files["top.sch"]
    # a sub-cell's sheet is emitted in ITS OWN library: USRLIB/tiny is a local cell of leaf
    assert "C {tiny.sym}" in files["leaf.sch"]
    assert not any("X4" in w or "res" in w for w in warnings)
    # every sub-cell warning (symbol, sheet or walk) names the cell it came from
    tail = "not ported — the symbol dump has no branch for that shape type"
    assert f"USRLIB/leaf: 1 device-layer 'path' shape(s) {tail}" in warnings
    assert "MYLIB/b: instance M3: orient 'R45' not in the 8-entry table — emitted unrotated" in (
        warnings
    )
    assert "USRLIB/tiny: no schematic view — ported its symbol only" in warnings


def test_reverse_cv2sch_with_symbols_never_lets_a_same_named_cell_overwrite_another(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import cv2sch_hierarchy

    client = _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): (
                "I X1 MYLIB amp 0.0 0.0 R0\n"
                "I X2 OTHERLIB amp 1.0 0.0 R0\n"  # the same cell name in another library
                "I X3 OTHERLIB top 2.0 0.0 R0\n"  # named like the top sheet itself
            ),
            ("MYLIB", "amp", "symbol"): _SUB_SYM,
            ("MYLIB", "amp", "schematic"): "",
        }
    )
    files, warnings = cv2sch_hierarchy(client, "MYLIB", "top", _kit_map(tmp_path))
    assert list(files) == ["top.sch", "amp.sym", "amp.sch"]
    assert [lib for lib, _, _ in client.opened] == ["MYLIB"] * 3  # OTHERLIB is never dumped
    assert "OTHERLIB/amp: not ported — its files would overwrite those of MYLIB/amp" in warnings
    assert "OTHERLIB/top: not ported — its files would overwrite those of MYLIB/top" in warnings


@pytest.mark.parametrize(
    ("view", "answer", "says"),
    [
        ("schematic", RuntimeError("SKILL evaluation timed out after 120 s"), "timed out"),
        ("symbol", RuntimeError("SKILL evaluation timed out after 120 s"), "timed out"),
        # an instantiated cell always has a symbol: a missing one is a failure, not a skip
        ("symbol", None, "symbol view not found"),
    ],
    ids=["sheet-error", "symbol-error", "symbol-missing"],
)
def test_reverse_cv2sch_with_symbols_raises_a_dump_failure_that_is_not_a_missing_sheet(
    tmp_path, view, answer, says
):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import cv2sch_hierarchy

    views: dict[tuple[str, str, str], str | Exception | None] = {
        ("MYLIB", "top", "schematic"): "I X1 MYLIB sub 0.0 0.0 R0\n",
        ("MYLIB", "sub", "symbol"): _SUB_SYM,
        ("MYLIB", "sub", "schematic"): "I M2 KITLIB nch 0.0 0.0 R0\n",
    }
    views[("MYLIB", "sub", view)] = answer
    with pytest.raises(RuntimeError, match=says):
        cv2sch_hierarchy(_RecordedSkill(views), "MYLIB", "top", _kit_map(tmp_path))


def _two_level_client(*, top_extra: str = "") -> _RecordedSkill:
    return _RecordedSkill(
        {
            ("MYLIB", "top", "schematic"): "I X1 MYLIB sub 1.0 0.0 R0\n" + top_extra,
            ("MYLIB", "sub", "schematic"): "I M2 KITLIB nch 0.0 0.0 R0\n",
            ("MYLIB", "sub", "symbol"): _SUB_SYM,
        }
    )


def test_cli_cv2sch_without_with_symbols_writes_the_top_sheet_only(tmp_path, monkeypatch, capsys):
    from spicexplorer_netlist2xschem.virtuoso_export import runner
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    client = _two_level_client()
    monkeypatch.setattr(runner, "connect", lambda **_kw: client)
    _kit_map(tmp_path)
    out = tmp_path / "out" / "top_port.sch"
    out.parent.mkdir()
    rc = main(["cv2sch", "MYLIB", "top", "--map", str(tmp_path / "kit.yaml"), "-o", str(out)])
    assert rc == 0
    # the pre-existing behaviour: one sheet, its sub-cell referenced but left to the caller
    assert [p.name for p in out.parent.iterdir()] == ["top_port.sch"]
    assert "C {sub.sym}" in out.read_text()
    assert client.opened == [("MYLIB", "top", "schematic")]
    assert capsys.readouterr().out.count("xvport: wrote") == 1


def test_cli_cv2sch_with_symbols_defaults_to_the_cell_name_in_the_cwd(
    tmp_path, monkeypatch, capsys
):
    from spicexplorer_netlist2xschem.virtuoso_export import runner
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    client = _two_level_client(top_extra="I M9 KITLIB secret 4.0 0.0 R0\n")
    monkeypatch.setattr(runner, "connect", lambda **_kw: client)
    _kit_map(tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    rc = main(["cv2sch", "MYLIB", "top", "--map", str(tmp_path / "kit.yaml"), "--with-symbols"])
    assert rc == 0
    assert sorted(p.name for p in work.iterdir()) == ["sub.sch", "sub.sym", "top.sch"]
    cap = capsys.readouterr()
    assert [ln for ln in cap.out.splitlines() if ln.startswith("xvport: wrote")] == [
        "xvport: wrote top.sch",
        "xvport: wrote sub.sym",
        "xvport: wrote sub.sch",
    ]
    assert "xvport: WARNING KITLIB/secret: not dumped" in cap.err


def test_cli_cv2sch_with_symbols_refuses_a_kit_top_with_exit_3(tmp_path, monkeypatch, capsys):
    from spicexplorer_netlist2xschem.virtuoso_export import runner
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    client = _RecordedSkill({})
    monkeypatch.setattr(runner, "connect", lambda **_kw: client)
    _kit_map(tmp_path)
    monkeypatch.chdir(tmp_path)
    rc = main(["cv2sch", "KITLIB", "nch", "--map", str(tmp_path / "kit.yaml"), "--with-symbols"])
    assert rc == 3
    assert "xvport: REFUSED" in capsys.readouterr().err
    assert client.opened == []
    assert sorted(p.name for p in tmp_path.iterdir()) == ["kit.yaml"]


# --- verifier (offline, mocked readback) --------------------------------------------


def _tgate_emit():
    sch, symlib = _load("transmission_gate_pair.sch")
    return emit_schematic_il(sch, lib="LIBX", cell="tgate", devmap=load_device_map(), symlib=symlib)


def _readback_for(result, tweak=None):
    """A fake ``read_schematic`` payload that matches ``result`` exactly; ``tweak``
    mutates the per-instance term tables to model a wrongly built cellview."""
    by_inst: dict[str, dict[str, str]] = {}
    for (inst, term), net in result.expected_bindings.items():
        by_inst.setdefault(inst, {})[term] = net
    if tweak:
        tweak(by_inst)
    instances = [
        {
            "name": name,
            "lib": result.instances.get(name, ("LIBX", "?"))[0],
            "cell": result.instances.get(name, ("LIBX", "?"))[1],
            "terms": terms,
        }
        for name, terms in by_inst.items()
    ]
    pins = {p: {"direction": d} for p, d in result.expected_ports.items()}
    return {"instances": instances, "pins": pins}


def test_verify_schematic_strict_ok():
    from spicexplorer_netlist2xschem.virtuoso_export.runner import verify_schematic

    r = _tgate_emit()
    data = _readback_for(r)
    report = verify_schematic(None, "LIBX", "tgate", r, reader=lambda *a, **k: data)
    assert report.ok
    assert report.checked_bindings == 8


def test_verify_schematic_rejects_misbind_onto_a_port_net():
    # Review F3 regression: a wrong readback net that HAPPENS to be a port name must fail
    # (an exemption in the shipped verifier used to let exactly this case pass).
    from spicexplorer_netlist2xschem.virtuoso_export.runner import verify_schematic

    r = _tgate_emit()

    def tweak(by_inst):
        by_inst["M1"]["G"] = "VSS"  # expected vctl; VSS is one of the port names

    data = _readback_for(r, tweak)
    report = verify_schematic(None, "LIBX", "tgate", r, reader=lambda *a, **k: data)
    assert not report.ok
    assert any("M1.G" in m for m in report.binding_mismatches)


def test_verify_schematic_coverage_extra_instances_and_missing_ports():
    from spicexplorer_netlist2xschem.virtuoso_export.runner import verify_schematic

    r = _tgate_emit()

    def tweak(by_inst):
        by_inst["M1"]["XTRA"] = "netx"  # a live terminal no expectation covers
        by_inst["M9"] = {"D": "port_A"}  # a device instance the emitter never placed

    data = _readback_for(r, tweak)
    data["pins"].pop("VDD")  # an interface pin that never got built
    report = verify_schematic(None, "LIBX", "tgate", r, reader=lambda *a, **k: data)
    assert not report.ok
    assert any("M1.XTRA" in m for m in report.uncovered_bindings)
    assert report.extra_instances == ["M9"]
    assert report.missing_ports == ["VDD"]


# --- end-to-end checks (netcheck / simcheck) ------------------------------------------
#
# The two netlist fixtures are REAL oracle outputs captured 2026-07-16: the .spice is
# verbatim `xschem -n` of transmission_gate_pair.sch; the .txt is the design section of a
# live Virtuoso createNetlist export of the ported cellview (kit include lines stripped).


def test_netcheck_fixtures_are_graph_equivalent():
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        netlists_graph_equivalent,
    )

    cmp = netlists_graph_equivalent(
        FIXTURES / "tgate_source_netlist.spice", FIXTURES / "tgate_cellview_netlist.txt"
    )
    assert cmp.equivalent, cmp.reason
    # the isomorphism recovers the real instance correspondence, not just a count match
    assert cmp.component_mapping == {"XM1": "M1", "XM2": "M2"}


# The committed fixtures are a CROSS-KIT topology port (IHP-drawn source -> FOUNDRY_KIT cells),
# so a same-kit port is synthesized from them by renaming the source models to the masters
# the cellview export actually names. Everything else stays the real captured oracle output.


def _same_kit_pair(tmp_path):
    src = (FIXTURES / "tgate_source_netlist.spice").read_text(encoding="utf-8")
    src = src.replace("sg13_lv_nmos", "nmos_lvt").replace("sg13_lv_pmos", "pmos_lvt")
    f = tmp_path / "same_kit_source.spice"
    f.write_text(src, encoding="utf-8")
    return f, (FIXTURES / "tgate_cellview_netlist.txt").read_text(encoding="utf-8")


def _cellview(tmp_path, text, name="cv.txt"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return f


def test_strict_netcheck_passes_a_clean_same_kit_port(tmp_path):
    """No false positives against a REAL Virtuoso export.

    This is the assertion the strict tier stands or falls on: the two netlisters spell the finger count
    differently (``ng`` vs ``nf``), write widths in different units (``0.15u`` vs
    ``150.0n``), and the export carries a dozen CDF-derived geometry parameters the source
    never had. A correct port must still read clean.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        _graph_pair,
        netlists_graph_equivalent,
        sizing_differences,
    )

    src, cv_text = _same_kit_pair(tmp_path)
    cv = _cellview(tmp_path, cv_text)
    assert netlists_graph_equivalent(src, cv, strict=True).equivalent
    ga, gb = _graph_pair(src, cv)
    assert sizing_differences(ga, gb, netlists_graph_equivalent(src, cv)) == []


def test_strict_netcheck_rejects_a_cross_kit_port_and_the_default_does_not():
    """Strict is opt-in for a reason: a topology port changes the master on purpose."""
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        netlists_graph_equivalent,
    )

    src = FIXTURES / "tgate_source_netlist.spice"
    cv = FIXTURES / "tgate_cellview_netlist.txt"
    assert netlists_graph_equivalent(src, cv).equivalent
    assert not netlists_graph_equivalent(src, cv, strict=True).equivalent


@pytest.mark.parametrize("card", ["x", "m"])
def test_strict_netcheck_catches_a_neighbouring_threshold_flavour(tmp_path, card):
    """The generic lane's silent failure: same type, same polarity, same wiring.

    Both card shapes, because the generic lane produces the M form: the committed fixture
    is an IHP sheet whose devices are ``.subckt`` wrappers (``XM1 … sg13_lv_nmos``), while a
    commercial kit's model is a primitive and xschem writes ``M1 d g s b nmos_lvt w= l=``.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        netlists_graph_equivalent,
    )

    src, cv_text = _same_kit_pair(tmp_path)
    if card == "m":
        text = src.read_text(encoding="utf-8").replace("XM1 ", "M1 ").replace("XM2 ", "M2 ")
        src = tmp_path / "m_cards.spice"
        src.write_text(text, encoding="utf-8")
    cv = _cellview(tmp_path, cv_text.replace("nmos_lvt", "nch", 1))
    assert netlists_graph_equivalent(src, cv).equivalent  # topology cannot see it
    assert not netlists_graph_equivalent(src, cv, strict=True).equivalent


def test_netcheck_fails_when_the_emitter_dropped_an_instance(tmp_path):
    """The self-consistency hole of issue #226, closed at the check that reported OK.

    netcheck compares the ported cellview against an xschem re-netlist of the SAME source
    file, so an instance the emitter dropped is absent from BOTH ends and the two agree about
    a circuit that is missing a component. The emitter's drop list is the one fact neither
    netlist carries; with it, the check is a finding before either netlister runs — which is
    also why it must report FAILED where an unavailable oracle would report SKIPPED.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import netcheck

    report = netcheck(
        None,  # no bridge is touched: the drop is decided before either oracle runs
        "LIBX",
        "tb_missing_dut",
        FIXTURES / "tb_missing_dut.sch",
        tmp_path,
        dropped=["XCMP"],
    )
    assert report.ok is False
    assert report.skipped is None
    assert "XCMP" in report.summary()


def test_a_missing_e2e_extra_skips_rather_than_crashes(monkeypatch):
    """The optional-extra contract: every caller treats CheckUnavailable as SKIPPED."""
    import builtins

    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        CheckUnavailable,
        netlists_graph_equivalent,
    )

    real = builtins.__import__

    def no_circuitgraph(name, *a, **k):
        if name.startswith("spicexplorer_circuitgraph"):
            raise ImportError("simulated: the [e2e] extra is not installed")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", no_circuitgraph)
    with pytest.raises(CheckUnavailable):
        netlists_graph_equivalent(
            FIXTURES / "tgate_source_netlist.spice", FIXTURES / "tgate_cellview_netlist.txt"
        )


@pytest.mark.parametrize(
    ("tamper", "want"),
    [
        (("w=150.0n", "w=155.3n"), "w"),  # 3.5 % — the per-finger/total class of error
        (("nf=1", "nf=16"), "nf"),  # a dropped finger count is a different transistor
        (("l=130.0n", "l=180.0n"), "l"),
    ],
)
def test_sizing_differences_names_the_device_and_the_attribute(tmp_path, tamper, want):
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        _graph_pair,
        netlists_graph_equivalent,
        sizing_differences,
    )

    src, cv_text = _same_kit_pair(tmp_path)
    cv = _cellview(tmp_path, cv_text.replace(tamper[0], tamper[1], 1))
    ga, gb = _graph_pair(src, cv)
    diffs = sizing_differences(ga, gb, netlists_graph_equivalent(src, cv))
    assert len(diffs) == 1 and f": {want} " in diffs[0], diffs
    assert "M1" in diffs[0]  # the pair, so a human can go straight to the device


# --- #216: pair by instance name, fall back to isomorphism ---------------------------
#
# The `devbench_*` fixtures are a bench of parallel identical-topology branches — the shape
# that has several valid isomorphisms. See their own headers: the cellview's instance ORDER
# is what provokes the mispairing, so these tests assert the provocation is still live.


def test_strict_netcheck_passes_parallel_identical_branches_that_match_by_name():
    """#216: a device-characterisation bench is not a sizing failure.

    Each branch differs from its neighbours only in size and model flavour, so the topology
    admits several isomorphisms; `compare_graphs` returns one that pairs `MNHVT10` against
    `MNHVT15` and their (correct, deliberate) size difference used to be reported as the
    finding. Compared by instance NAME every device agrees exactly — the port is right.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        _graph_pair,
        netlists_graph_equivalent,
        sizing_differences,
    )

    src = FIXTURES / "devbench_source_netlist.spice"
    cv = FIXTURES / "devbench_cellview_netlist.txt"
    cmp = netlists_graph_equivalent(src, cv, strict=True)
    assert cmp.equivalent, cmp.reason
    ga, gb = _graph_pair(src, cv)
    assert sizing_differences(ga, gb, cmp) == []
    # WHICH isomorphism `compare_graphs` returns here is not stable run to run (the branches
    # are interchangeable, so the answer follows set iteration order). That is the shape of
    # the defect — the gate failed intermittently on a correct port — and it is why the
    # deterministic statement of #216 is the test below, which hands the comparison the
    # worst-case mapping instead of hoping to draw it.


def test_a_genuine_mis_size_is_still_caught_on_the_same_bench(tmp_path):
    """Name-keyed pairing must not have bought the pass by comparing nothing."""
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        _graph_pair,
        netlists_graph_equivalent,
        sizing_differences,
    )

    text = (FIXTURES / "devbench_cellview_netlist.txt").read_text(encoding="utf-8")
    src = FIXTURES / "devbench_source_netlist.spice"
    cv = tmp_path / "devbench_cv.txt"
    cv.write_text(text.replace("nmos_lvt l=150.0n", "nmos_lvt l=180.0n"), encoding="utf-8")
    ga, gb = _graph_pair(src, cv)
    diffs = sizing_differences(ga, gb, netlists_graph_equivalent(src, cv, strict=True))
    assert diffs == ["MNHVT15->MNHVT15: l 150n vs 180.0n"], diffs


def test_a_renamed_instance_falls_back_to_the_isomorphism_and_says_so(tmp_path):
    """A name with no counterpart still gets compared — and the message flags the pairing.

    The source's `MNHVT10` is renamed (and re-sized, so a diff exists whichever partner the
    fallback lands on). `(paired by structure)` is what stops a reader taking `A->B` for a
    device compared with itself, which is the least this check owed them.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        _graph_pair,
        netlists_graph_equivalent,
        sizing_differences,
    )

    text = (FIXTURES / "devbench_source_netlist.spice").read_text(encoding="utf-8")
    text = text.replace(
        "MNHVT10 dn1 gn1 VSS VSS nmos_lvt w=1u l=100n",
        "MNLEAK dn1 gn1 VSS VSS nmos_lvt w=1u l=200n",
    )
    src = tmp_path / "renamed.spice"
    src.write_text(text, encoding="utf-8")
    cv = FIXTURES / "devbench_cellview_netlist.txt"
    ga, gb = _graph_pair(src, cv)
    diffs = sizing_differences(ga, gb, netlists_graph_equivalent(src, cv, strict=True))
    assert len(diffs) == 1, diffs
    assert diffs[0].startswith("MNLEAK->") and "(paired by structure)" in diffs[0], diffs
    assert ": l 200n vs " in diffs[0], diffs


def test_the_worst_case_isomorphism_no_longer_reports_a_sizing_failure():
    """#216, stated deterministically: hand the comparison the mapping that mispairs.

    `compare_graphs` may return any of this bench's valid isomorphisms, so the crosswise one
    is supplied here rather than drawn. Before the fix this produced
    `MNHVT10->MNHVT15: l 100n vs 150.0n; MNHVT15->MNHVT10: …` — four findings on a port where
    every device's name, model, w, l and m agree exactly.
    """
    from types import SimpleNamespace

    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        _graph_pair,
        sizing_differences,
    )

    ga, gb = _graph_pair(
        FIXTURES / "devbench_source_netlist.spice",
        FIXTURES / "devbench_cellview_netlist.txt",
    )
    crosswise = SimpleNamespace(
        component_mapping={
            "MNHVT10": "MNHVT15",
            "MNHVT15": "MNHVT10",
            "MPSTD10": "MPSTD15",
            "MPSTD15": "MPSTD10",
        }
    )
    assert sizing_differences(ga, gb, crosswise) == []


def test_pairing_prefers_names_and_labels_only_the_structural_leftovers():
    """The pairing itself, away from any netlist: names win, the isomorphism fills in."""
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import pair_components

    # the committed t-gate pair is the `X` spiceprefix case: source XM1/XM2 vs cellview M1/M2
    assert pair_components(["XM1", "XM2"], ["M1", "M2"], {"XM1": "M2", "XM2": "M1"}) == [
        ("XM1", "M1", True),
        ("XM2", "M2", True),
    ]
    # a name with no counterpart takes the isomorphism's answer, flagged
    assert pair_components(["M1", "MOLD"], ["M1", "MNEW"], {"M1": "MNEW", "MOLD": "M1"}) == [
        ("M1", "M1", True),
        ("MOLD", "MNEW", False),
    ]
    # an ambiguous key (M1 and XM1 on one side) is no basis for a pairing — isomorphism only
    assert pair_components(["M1", "XM1"], ["M1", "M2"], {"M1": "M2", "XM1": "M1"}) == [
        ("M1", "M2", False),
        ("XM1", "M1", False),
    ]


def test_netcheck_detects_a_moved_gate(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        netlists_graph_equivalent,
    )

    tampered = (FIXTURES / "tgate_cellview_netlist.txt").read_text(encoding="utf-8")
    # move M1's gate from vctl onto the VSS rail — same devices, different wiring
    tampered = tampered.replace("(port_A vctl port_B VSS)", "(port_A VSS port_B VSS)")
    bad = tmp_path / "tampered.txt"
    bad.write_text(tampered, encoding="utf-8")
    cmp = netlists_graph_equivalent(FIXTURES / "tgate_source_netlist.spice", bad)
    assert not cmp.equivalent


@pytest.mark.skipif(shutil.which("xschem") is None, reason="xschem not on PATH")
def test_xschem_source_netlist_matches_committed_oracle(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        netlists_graph_equivalent,
        xschem_source_netlist,
    )

    out = xschem_source_netlist(FIXTURES / "transmission_gate_pair.sch", tmp_path)
    assert "IS MISSING" not in out.read_text(encoding="utf-8")  # ipin/rail names resolved
    cmp = netlists_graph_equivalent(out, FIXTURES / "tgate_cellview_netlist.txt")
    assert cmp.equivalent, cmp.reason


def test_extract_design_section_drops_header_includes():
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import (
        extract_design_section,
    )

    full = "\n".join(
        [
            "// Generated for: spectre",
            "simulator lang=spectre",
            'include "ade_e.scs"',
            "global 0",
            'include "/fake/kit/path/models.txt" section=tt',
            "// Library name: LIBX",
            "// Cell name: tgate",
            "M1 (a b c d) nmos_lvt l=130.0n w=150.0n",
            "simulatorOptions options reltol=1e-3",
            "saveOptions options save=allpub",
        ]
    )
    section = extract_design_section(full)
    assert "include" not in section
    assert "simulatorOptions" not in section
    assert "M1 (a b c d) nmos_lvt" in section


def test_compose_smoke_deck_ties_ports_and_uses_only_operator_models(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import compose_smoke_deck

    deck = compose_smoke_deck(
        FIXTURES / "tgate_cellview_netlist.txt",
        ["port_A", "port_B", "vctl", "vctl_not", "VDD", "VSS"],
        "/operator/models.txt",
        "tt",
        tmp_path / "smoke.spectre",
    )
    text = deck.read_text(encoding="utf-8")
    assert text.count("resistor r=1G") == 6  # every interface net tied to ground
    assert 'include "/operator/models.txt" section=tt' in text
    assert text.count("include") == 1  # the operator include is the ONLY one (NDA guard)
    assert "xvportOp dc" in text
    assert "M1 (port_A vctl port_B VSS) nmos_lvt" in text


def test_compose_smoke_deck_injects_sim_params(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import compose_smoke_deck

    deck = compose_smoke_deck(
        FIXTURES / "tgate_cellview_netlist.txt",
        ["VDD", "VSS"],
        "/operator/models.txt",
        None,
        tmp_path / "smoke.spectre",
        params={"gm_val": "1m", "rout_val": "10M"},
    )
    assert "parameters gm_val=1m rout_val=10M" in deck.read_text(encoding="utf-8")


def test_xschem_source_netlist_fails_loudly_when_xschem_skips_a_token(tmp_path):
    """A `SKIPPING` line means xschem dropped part of the schematic and netlisted the rest anyway
    at exit 0 — the netlist is then not the schematic, so it must raise rather than be believed."""
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import _reject_skipped_tokens

    _reject_skipped_tokens(tmp_path / "ok.sch", "netlisting ok\n")  # quiet log: no error
    with pytest.raises(RuntimeError, match="skipped part of bad.sch"):
        _reject_skipped_tokens(tmp_path / "bad.sch", 'xschem: SKIPPING |"}|\n')


# --- a TESTBENCH: its ground and its sources (issue #182) --------------------------


def test_a_bench_ground_becomes_a_cadence_global():
    """SPICE `0` is not an ordinary net.

    Without the mapping `0` sanitizes to `net0`, every ground terminal lands on that
    ordinary net, and the ported bench has no ground reference at all — spectre refuses to
    read the cellview while the port still reports success.
    """
    sch, symlib = _load("tb_source.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="tb_source", devmap=load_device_map(), symlib=symlib
    )
    assert r.errors == []
    assert r.expected_bindings[("VIN", "MINUS")] == "gnd!"
    assert r.expected_bindings[("RL", "MINUS")] == "gnd!"
    assert "net0" not in r.il


def test_only_spice_zero_is_global_by_default():
    """A rail is a design choice; `0` is structural.

    Defaulting `vdd` to `vdd!` would silently turn a drawn supply port into a global on
    every sheet that has one, so a map that wants it says so.
    """
    m = load_device_map()
    assert m.global_for("0") == "gnd!"
    assert m.global_for("GND") is None and m.global_for("vdd") is None
    assert m.xschem_net("gnd!") == "0"  # the reverse port maps it back


def test_a_map_may_declare_its_own_globals(tmp_path):
    f = tmp_path / "g.yaml"
    f.write_text('devices: []\nglobals: {"0": "gnd!", vdd: "vdd!"}\n')
    m = load_device_map(f)
    assert m.global_for("VDD") == "vdd!"  # matched case-insensitively, as SPICE does
    f.write_text("devices: []\nglobals: {}\n")
    assert load_device_map(f).global_for("0") is None  # an explicit empty section disables


def test_a_source_stimulus_is_split_across_the_cdf_fields_that_hold_it():
    """`dc 0.2 ac 1` is not one number.

    Writing the whole string into `vdc` made Cadence read the word `dc` as a design
    variable, so the bench's operating point was whatever that variable happened to hold —
    reported as a warning beside a successful port.
    """
    sch, symlib = _load("tb_source.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="tb_source", devmap=load_device_map(), symlib=symlib
    )
    assert r.instances["VIN"] == ("analogLib", "vdc")
    assert 'xvSetParams(cv "VIN" list(list("acm" "1") list("vdc" "0.2")))' in r.il
    assert "dc 0.2 ac 1" not in r.il  # the string itself never reaches a CDF field


def test_a_transient_stimulus_selects_its_own_master(tmp_path):
    """analogLib spreads sources over cells: a pulse does not belong on a `vdc`."""
    src = tmp_path / "tb_pulse.sch"
    src.write_text(
        (FIXTURES / "tb_source.sch")
        .read_text()
        .replace('value="dc 0.2 ac 1"', 'value="pulse(0 1.8 1n 10p 10p 5n 10n)"')
    )
    shutil.copytree(FIXTURES.parent / "sym", tmp_path / "sym", dirs_exist_ok=True)
    sch = parse_sch(src.read_text())
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="tb_pulse",
        devmap=load_device_map(),
        symlib=symlib_for_source(FIXTURES / "tb_source.sch"),
    )
    assert r.instances["VIN"] == ("analogLib", "vpulse")
    # #214: the level fields land on the CDF names analogLib's vpulse actually has (v1/v2,
    # live-probed 2026-09-13 on IC23.1). This pinned `val1` — a canonical field name, not a
    # CDF one — and no analogLib source has it, so every ported pulse was zero-amplitude.
    assert 'list("per" "10n")' in r.il and 'list("v2" "1.8")' in r.il
    assert 'list("val1"' not in r.il
    assert r.errors == []


@pytest.mark.parametrize(
    ("symref", "kind", "cell", "want"),
    [
        # live-probed on analogLib, IC23.1, 2026-09-13 (#214)
        ("devices/vsource.sym", "pulse", "vpulse", {"val0": "v1", "val1": "v2"}),
        ("devices/isource.sym", "pulse", "ipulse", {"val0": "i1", "val1": "i2"}),
        ("devices/vsource.sym", "sin", "vsin", {"offset": "vo", "ampl": "va", "damp": "theta"}),
        ("devices/isource.sym", "sin", "isin", {"offset": "io", "ampl": "ia", "damp": "theta"}),
    ],
)
def test_the_transient_cdf_spellings_are_the_ones_analoglib_has(symref, kind, cell, want):
    """#214: `val0`/`val1`/`sinedc`/`ampl`/`damp` are CANONICAL field names, not CDF ones.

    No analogLib source carries them, so `xvSetParams` dropped every level and amplitude and
    the bench ported dead — correct timing, zero swing, and a port that reported success.
    The timing fields (`td`/`tr`/`tf`/`pw`/`per`/`freq`) were right all along.
    """
    rule = load_device_map().lookup(symref)
    assert rule is not None and rule.stimulus is not None
    spec = rule.stimulus.for_kind(kind)
    assert spec is not None and spec.cell == cell
    for canonical, cdf in want.items():
        assert spec.params[canonical] == cdf
    assert not ({"val0", "val1", "sinedc", "ampl", "damp"} & set(spec.params.values()))


def test_an_unknown_cdf_param_fails_the_load_instead_of_printing_to_the_ciw():
    """#214: the client has to SEE a CDF name the master has not got.

    The helper used to `printf` a warning into the CIW, which nothing on the xvport side ever
    reads — so a map spelling the CDF for a different kit was indistinguishable from a clean
    port. It now collects every unknown name and `error()`s, which `runner.load_il` turns
    into a non-zero exit with the text on stderr. The collect runs BEFORE the save/restore
    block, so an aborted call cannot leave the base cell's CDF holding this instance's values.
    """
    sch, symlib = _load("tb_source.sch")
    il = emit_schematic_il(
        sch, lib="LIBX", cell="tb_source", devmap=load_device_map(), symlib=symlib
    ).il
    helper = il.split("procedure( xvSetParams")[1].split("procedure( xvLabelTerm")[0]
    assert "WARNING unknown CDF param" not in helper  # the CIW-only warning is gone
    assert "unknown = nil" in helper
    assert "unknown = cons(car(pair) unknown)" in helper  # collects ALL of them, not the first
    assert "when(unknown" in helper and "error(" in helper
    # the collect precedes the block that mutates (and later restores) the base cell CDF
    assert helper.index("when(unknown") < helper.index("saved = makeTable")


def test_an_unreadable_stimulus_fails_the_port(tmp_path):
    src = tmp_path / "tb_bad.sch"
    src.write_text(
        (FIXTURES / "tb_source.sch").read_text().replace('value="dc 0.2 ac 1"', 'value="wobble 3"')
    )
    r = emit_schematic_il(
        parse_sch(src.read_text()),
        lib="LIBX",
        cell="tb_bad",
        devmap=load_device_map(),
        symlib=symlib_for_source(FIXTURES / "tb_source.sch"),
    )
    assert any("cannot read" in e and "VIN" in e for e in r.errors)


def test_a_stimulus_kind_the_map_does_not_declare_fails_the_port(tmp_path):
    """Better to refuse than to drop the fields that carry the waveform."""
    m = tmp_path / "dconly.yaml"
    m.write_text(
        """
devices:
  - match: "*/vsource.sym"
    lib: analogLib
    cell: vdc
    terms: {p: PLUS, m: MINUS}
    stimulus:
      attr: value
      types:
        dc: {params: {dc: vdc, ac_mag: acm}}
"""
    )
    src = tmp_path / "tb_pulse.sch"
    src.write_text(
        (FIXTURES / "tb_source.sch")
        .read_text()
        .replace('value="dc 0.2 ac 1"', 'value="pulse(0 1.8 1n)"')
    )
    r = emit_schematic_il(
        parse_sch(src.read_text()),
        lib="LIBX",
        cell="tb_pulse",
        devmap=load_device_map(m),
        symlib=symlib_for_source(FIXTURES / "tb_source.sch"),
    )
    assert any("declares no CDF fields for a 'pulse' stimulus" in e for e in r.errors)


def test_a_declared_kind_missing_one_field_fails_rather_than_dropping_it(tmp_path):
    m = tmp_path / "partial.yaml"
    m.write_text(
        """
devices:
  - match: "*/vsource.sym"
    lib: analogLib
    cell: vdc
    terms: {p: PLUS, m: MINUS}
    stimulus:
      attr: value
      types:
        dc: {params: {dc: vdc}}
"""
    )
    sch, symlib = _load("tb_source.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="tb_source", devmap=load_device_map(m), symlib=symlib
    )
    assert any("ac_mag=1" in e and "does not route" in e for e in r.errors)


def test_the_reverse_port_recomposes_a_source_value_and_the_ground_label():
    """cv2sch must not lose what sch2cv now spreads out.

    A source's `value=` is assembled again from the CDF fields, and a `gnd!` label maps back
    to the sheet's `0` — otherwise a bench read out of Cadence returns with blank sources and
    a ground that no longer netlists to the certified deck's `0`.
    """
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        DumpInstance,
        SchDump,
        emit_sch_text,
    )

    dump = SchDump(
        labels=[(0.0, 0.0, "gnd!"), (1.0, 0.0, "vin")],
        instances=[
            DumpInstance("VIN", "analogLib", "vdc", 0.0, 0.0, "R0", {"vdc": "0.2", "acm": "1"}),
            DumpInstance(
                "VPULSE",
                "analogLib",
                "vpulse",
                1.0,
                0.0,
                "R0",
                # CDF parameter names as a live analogLib vpulse carries them (#214) — the
                # reverse direction inverts the map, so these must be the map's own spellings
                {
                    "v1": "0",
                    "v2": "1.8",
                    "td": "1n",
                    "tr": "10p",
                    "tf": "10p",
                    "pw": "5n",
                    "per": "10n",
                },
            ),
        ],
    )
    text, warnings = emit_sch_text(dump, load_device_map(), lib="xvport_dev")
    assert warnings == []
    assert "lab=0}" in text and "gnd!" not in text
    assert 'value="dc 0.2 ac 1"' in text
    assert 'value="pulse(0 1.8 1n 10p 10p 5n 10n)"' in text


def test_the_global_name_anchors_to_the_same_supply_class_as_spice_zero():
    """netcheck's own oracle has to agree that `gnd!` IS the source's `0`.

    The check that caught the missing ground compares supply-rail POPULATION, so the fix is
    only complete if circuitgraph classifies the Cadence global and the SPICE net alike.
    Asserted here rather than assumed: the two live in different packages.
    """
    cg = pytest.importorskip("spicexplorer_circuitgraph.graph")
    mapped = load_device_map().global_for("0")
    assert mapped == "gnd!"
    assert cg._classify_supply(mapped) == cg._classify_supply("0") == (True, "GND")


# --- #236: port-named nets, colliding Mode-A labels, one .il per cellview ------------


def _parse_inline(text: str):
    """Parse an inline sheet against the fixture symbol library."""
    return parse_sch(_SCH_SKEL + text), symlib_for_source(FIXTURES / "transmission_gate_pair.sch")


_PORT_ON_WIRE = (
    "N -100 -30 100 -30 {}\nN 100 -30 100 0 {}\nC {devices/res.sym} 100 0 0 0 {name=RL value=1k}\n"
)


@pytest.mark.parametrize("port_sym", ["ipin", "opin", "iopin"])
@pytest.mark.parametrize(("px", "py"), [(-100, -30), (0, -30)])
@pytest.mark.parametrize("rot", [0, 1, 2, 3])
def test_a_port_pin_on_a_wire_names_that_wire_group(port_sym, px, py, rot):
    """A port dropped ON the net's wire names the group — the binding xschem makes (#236).

    All three port symbols carry their connection point at the symbol ORIGIN, so this holds
    at a wire endpoint, in a segment's interior, and at every rotation. The module docstring
    used to claim ports bind by ``lab`` alone; they bind both ways, and this pins it.
    """
    sch, symlib = _parse_inline(
        _PORT_ON_WIRE + f"C {{devices/{port_sym}.sym}} {px} {py} {rot} 0 {{name=p1 lab=vin}}\n"
    )
    nx = extract_nets(sch, symlib)
    assert nx.pin_nets[("RL", "P")].net == "vin"
    assert not any("RL.P" in w for w in nx.warnings)


def test_a_parked_port_still_binds_by_name_only():
    """The other half of the contract: a port far from every wire names nothing it is not
    drawn on (real corpus sheets park them), so its group stays its own."""
    sch, symlib = _parse_inline(
        _PORT_ON_WIRE + "C {devices/ipin.sym} -300 -300 0 0 {name=p1 lab=vin}\n"
    )
    nx = extract_nets(sch, symlib)
    assert nx.pin_nets[("RL", "P")].net != "vin"
    assert {p.name for p in nx.ports} == {"vin"}


def test_an_anonymous_group_warns_naming_its_terminals():
    """A group no label/port/pin name reaches is not silently auto-named any more (#236).

    Reported shape: the sheet's only name for the net is out of the extractor's reach, every
    terminal on it lands on a synthesized name, and ``--strict-netcheck`` reports only a net
    COUNT difference. The warning names the group and the terminals on it.
    """
    sch, symlib = _parse_inline(_PORT_ON_WIRE)
    nx = extract_nets(sch, symlib)
    anon = [w for w in nx.warnings if "anonymous net" in w]
    assert len(anon) == 2
    assert any("RL.P" in w for w in anon) and any("RL.M" in w for w in anon)


def test_a_stale_cached_wire_label_says_why_the_group_is_anonymous():
    """The common cause: the wire caches ``lab=vin`` while the real ``vin`` is a parked port.

    The cached label is not an electrical name (it must not by-name MERGE the two groups),
    so the group stays anonymous — but the warning now says the name was refused and why,
    instead of leaving a net count to explain it.
    """
    sch, symlib = _parse_inline(
        "N -100 -30 100 -30 {\nlab=vin}\n"
        "N 100 -30 100 0 {}\n"
        "C {devices/res.sym} 100 0 0 0 {name=RL value=1k}\n"
        "C {devices/ipin.sym} -300 -300 0 0 {name=p1 lab=vin}\n"
    )
    nx = extract_nets(sch, symlib)
    assert [w for w in nx.warnings if "RL.P" in w and "cache lab='vin'" in w]


# nmos4's b (20,0) and s (20,30) share a column: tie them with the straight run between
# them and both terminals stub in the same direction along it (the #236 case 2 shape).
_BULK_TIED_TO_SOURCE = (
    "C {devices/nmos4.sym} 0 0 0 0 {name=M1 model=nmos4 w=1u l=0.15u}\n"
    "N 20 0 20 30 {}\n"
    "C {devices/lab_wire.sym} 20 30 0 0 {name=l3 lab=src}\n"
    "N -60 0 -20 0 {}\n"
    "C {devices/lab_wire.sym} -60 0 0 0 {name=l1 lab=gate}\n"
    "N 20 -30 60 -30 {}\n"
    "C {devices/lab_wire.sym} 60 -30 0 0 {name=l2 lab=drain}\n"
)


def test_two_terminals_of_one_instance_never_label_along_one_line():
    """Bulk tied to source by the straight run between them: the two labels are fanned out.

    Both stubs would leave in the same direction along the same column. ``xvLabelTerm`` draws
    them from the *master's* pin centres, which can be a fraction of the stub length apart —
    the two labels then land on one point and one wins, leaving both terminals on an
    auto-named net (#236). Distinct directions give distinct label points for ANY master
    geometry, which is the only guarantee available offline.
    """
    sch, symlib = _parse_inline(_BULK_TIED_TO_SOURCE)
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="t",
        devmap=load_device_map(),
        symlib=symlib,
        local_cells={"nmos4"},
    )
    assert r.errors == [], r.errors
    calls = {
        line.split('"')[3]: line.split('"')[6].split()
        for line in r.il.splitlines()
        if line.strip().startswith('xvLabelTerm(cv "M1"')
    }
    assert set(calls) == {"b", "d", "g", "s"}
    aims = {t: (float(v[0]), float(v[1])) for t, v in calls.items()}
    assert aims["b"] != aims["s"]  # the collision is gone
    # and they are perpendicular, so the labels differ whatever the master's pin spacing
    assert aims["b"][0] * aims["s"][0] + aims["b"][1] * aims["s"][1] == 0
    assert [w for w in r.warnings if "M1" in w and "one line" in w]


def test_colliding_labels_are_refused_when_no_direction_fans_them_out(tmp_path):
    """No provably outward perpendicular ⇒ REFUSE, naming the instance, rather than build it.

    Both pins sit on the instance's own axis, so either perpendicular points through the
    body — where a stub can land on a neighbouring pin and rewire the cellview silently.
    """
    from spicexplorer_netlist2xschem import SymLibrary

    (tmp_path / "devices").mkdir()
    (tmp_path / "devices" / "stack2.sym").write_text(
        "v {xschem version=3.4.5 file_version=1.2\n}\nG {}\nK {type=subcircuit\n"
        'template="name=x1"}\nV {}\nS {}\nE {}\n'
        "B 5 -2.5 17.5 2.5 22.5 {name=a dir=inout}\n"
        "B 5 -2.5 47.5 2.5 52.5 {name=b dir=inout}\n",
        encoding="utf-8",
    )
    sch = parse_sch(
        _SCH_SKEL
        + "C {devices/stack2.sym} 0 0 0 0 {name=X1}\n"
        + "N 0 20 0 50 {}\n"
        + "C {devices/lab_wire.sym} 0 50 0 0 {name=l1 lab=tie}\n"
    )
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="t",
        devmap=load_device_map(),
        symlib=SymLibrary([tmp_path]),
        local_cells={"stack2"},
    )
    assert [e for e in r.errors if "X1" in e and "one line" in e], r.errors


def test_with_symbols_writes_one_il_per_cellview_in_dependency_order(tmp_path, capsys):
    """#236 case 3: 43 builds in one file fail as one line number naming nothing."""
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    src = tmp_path / "chopper-diff.sch"
    for name in ("chopper-diff.sch", "transmission_gate_pair.sch", "transmission_gate_pair.sym"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    out = tmp_path / "out.il"
    rc = main(["sch2cv", str(src), "--lib", "LIBX", "--with-symbols", "-o", str(out)])
    assert rc == 0
    parts = sorted(p.name for p in tmp_path.glob("out.*.il"))
    assert parts == [
        "out.sch.chopper_diff.il",
        "out.sch.transmission_gate_pair.il",
        "out.sym.transmission_gate_pair.il",
    ]
    # the child's cellviews come before the parent's, and each file builds exactly one
    assert not out.exists()  # no combined file: loading it is the failure this replaces
    for part in parts:
        text = (tmp_path / part).read_text(encoding="utf-8")
        assert text.count('"w")') == 1  # exactly one cellview opened for writing
    assert 'dbCreateInst(cv m "x1"' in (tmp_path / "out.sch.chopper_diff.il").read_text()
    # …and the summary line lists them in LOAD order: the child's schematic and symbol
    # before the parent that instantiates it
    # read the summary LINE, not the tail of stdout: the per-cell parameter provenance of
    # #241 prints after it, so anchoring on the last "): " in the whole capture is wrong.
    summary = next(
        ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("xvport: wrote ")
    )
    listed = summary.rsplit("): ", 1)[1].strip().split(", ")
    assert listed == [
        "out.sch.transmission_gate_pair.il",
        "out.sym.transmission_gate_pair.il",
        "out.sch.chopper_diff.il",
    ]


def test_without_symbols_the_single_build_still_goes_to_the_output_path(tmp_path):
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    src = tmp_path / "amp_001_5t.sch"
    shutil.copy(FIXTURES / "amp_001_5t.sch", src)
    out = tmp_path / "amp.il"
    rc = main(["sch2cv", str(src), "--lib", "LIBX", "--allow-symbolic", "-o", str(out)])
    assert rc == 0
    assert out.is_file() and not list(tmp_path.glob("amp.*.*.il"))


def test_load_il_failure_names_the_file_line_and_cellview(tmp_path):
    """A ``load`` error is a line number and nothing else — resolve it against the file."""
    from spicexplorer_netlist2xschem.virtuoso_export.runner import load_il

    il = tmp_path / "out.sch.tgate.il"
    il.write_text(
        'cv = dbOpenCellViewByType("LIBX" "tgate" "schematic" "schematic" "w")\n'
        'xvSetParams(cv "M1" list(list("w" "1u")))\n'
        "dbSave(cv)\n",
        encoding="utf-8",
    )

    class _Result:
        status = "failure"
        errors = ['("load" 0 t nil ("*Error* load: error while loading file - "x.il" at line 2"))']
        output = ""

    class _Client:
        def load_il(self, path, timeout=0):
            return _Result()

    with pytest.raises(RuntimeError) as exc:
        load_il(_Client(), il)
    msg = str(exc.value)
    assert "out.sch.tgate.il:2" in msg
    assert "LIBX/tgate" in msg
    assert "xvSetParams" in msg


# --- #250: a ported testbench keeps its directives (as annotation, never circuitry) -----


def test_the_parser_exposes_directive_blocks_without_making_them_devices():
    sch, _symlib = _load("tb_code_shown.sch")
    assert [c.name for c in sch.directives] == ["directives"]
    assert sch.directives[0].directive_text.strip().splitlines() == [".tran 1n 100n", ".end"]
    assert "directives" not in {c.name for c in sch.devices}  # still not a device (#215)


def test_directive_text_reaches_the_emit_result_and_the_cellview_as_notes():
    """The block is drawn into the cellview as NOTE labels — readable, and not circuitry."""
    sch, symlib = _load("tb_code_shown.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="tb_directives", devmap=load_device_map(), symlib=symlib
    )
    assert r.errors == [], r.errors
    assert [n for n, _text in r.directives] == ["directives"]
    assert ".tran 1n 100n" in r.directives[0][1]
    notes = [ln.strip() for ln in r.il.splitlines() if ln.strip().startswith("schCreateNoteLabel")]
    assert len(notes) == 3  # the block name + its two non-blank lines; blanks are skipped
    assert '".tran 1n 100n" "lowerLeft" "R0" "stick"' in notes[1]
    assert "code_shown" not in r.il  # still no invented cell, and no symref in the artifact
    # every note sits BELOW every drawn object
    note_y = [float(ln.split("list(")[1].split(")")[0].split()[1]) for ln in notes]
    drawn_y = [
        float(ln.split("list(")[1].split(")")[0].split()[1])
        for ln in r.il.splitlines()
        if "dbCreateInst(cv m" in ln
    ]
    assert drawn_y and max(note_y) < min(drawn_y)


def test_directive_notes_can_be_switched_off():
    sch, symlib = _load("tb_code_shown.sch")
    r = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="tb_directives",
        devmap=load_device_map(),
        symlib=symlib,
        directives_note=False,
    )
    assert "schCreateNoteLabel" not in r.il
    assert r.directives  # still reported, so the caller still writes and warns


def test_cli_writes_the_directives_sidecar_and_warns(tmp_path, capsys):
    """(a) the text beside the `.il`, (b) named in the summary, (c) a WARNING on stderr."""
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    src = tmp_path / "tb_code_shown.sch"
    shutil.copy(FIXTURES / "tb_code_shown.sch", src)
    out = tmp_path / "tb.il"
    assert main(["sch2cv", str(src), "--lib", "LIBX", "-o", str(out)]) == 0
    side = tmp_path / "tb.tb_code_shown.directives.txt"
    assert side.is_file()
    # verbatim: the block's own text, unescaped, nothing added
    assert (
        side.read_text(encoding="utf-8")
        == parse_sch(src.read_text(encoding="utf-8")).directives[0].directive_text
    )
    captured = capsys.readouterr()
    assert side.name in captured.out and "2 directive line(s)" in captured.out
    assert "xvport: WARNING 2 directive line(s) not ported as circuit objects" in captured.err
    assert side.name in captured.err


def test_cli_no_directives_note_still_writes_and_warns(tmp_path, capsys):
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    src = tmp_path / "tb_code_shown.sch"
    shutil.copy(FIXTURES / "tb_code_shown.sch", src)
    out = tmp_path / "tb.il"
    argv = ["sch2cv", str(src), "--lib", "LIBX", "--no-directives-note", "-o", str(out)]
    assert main(argv) == 0
    assert "schCreateNoteLabel" not in out.read_text(encoding="utf-8")
    assert (tmp_path / "tb.tb_code_shown.directives.txt").is_file()
    assert "not ported as circuit objects" in capsys.readouterr().err


def test_a_sheet_without_directives_writes_no_sidecar_and_no_warning(tmp_path, capsys):
    from spicexplorer_netlist2xschem.virtuoso_export.cli import main

    src = tmp_path / "amp_001_5t.sch"
    shutil.copy(FIXTURES / "amp_001_5t.sch", src)
    out = tmp_path / "amp.il"
    assert main(["sch2cv", str(src), "--lib", "LIBX", "--allow-symbolic", "-o", str(out)]) == 0
    assert not list(tmp_path.glob("*.directives.txt"))
    assert "not ported as circuit objects" not in capsys.readouterr().err
