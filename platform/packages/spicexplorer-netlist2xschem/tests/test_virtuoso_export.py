"""virtuoso_export (xvport) — offline tests over real corpus fixtures.

The fixtures are verbatim copies of analog-db circuits (`amp_001_5t.sch`, the ccia-02
`transmission_gate_pair.sch`); the expected pin→net tables below are their electrical ground
truth (a 5T OTA / a transmission gate), which is what pins the geometric net extractor.
The emitter tests assert structure + determinism of the `.il` artifact, not full golden text.

Live counterpart (needs the CIW daemon): both fixtures were built on IC23.1 2026-07-16 —
schCheck 0 errors / 0 warnings, with all terminal bindings and CDF-callback behavior
verified live.
"""

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
        ("transmission_gate_pair.sch", TGATE_EXPECTED,
         {"port_A", "port_B", "vctl", "vctl_not", "VDD", "VSS"}),
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
    # chopper-diff has one net carrying both the auto '#net2' and the human 'Vctl_not';
    # xschem's netlister publishes the human name, so the extractor must too (subckt
    # port naming drifts one hierarchy level up otherwise).
    sch, symlib = _load("chopper-diff.sch")
    nx = extract_nets(sch, symlib)
    assert "Vctl_not" in nx.nets
    assert "#net2" not in nx.nets
    assert any("multiple labels" in w for w in nx.warnings)


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

    assert r1.instances == {"M1": ("tsmcN65", "nch_lvt"), "M2": ("tsmcN65", "pch_lvt")}
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
    assert 'xvSetParams(cv "M1" list(list("fingers" "1") list("l" "0.13u") list("simM" "1") list("w" "0.15u")))' in il
    # every terminal gets a labeled stub; interface pins exist for every port
    assert il.count('xvLabelTerm(cv "') == 8
    assert il.count("schCreatePin(") == 6
    assert 'schCheck(cv)' in il and 'dbSave(cv)' in il


def test_emit_unmapped_symref_becomes_local_master_with_warning():
    sch, symlib = _load("chopper-diff.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="chopper_diff", devmap=load_device_map(), symlib=symlib
    )
    # transmission_gate_pair.sym is not in the device map -> local master in the target lib.
    assert r.instances["x1"] == ("LIBX", "transmission_gate_pair")
    assert any("unmapped symref" in w for w in r.warnings)


def test_emit_per_finger_width_and_simM_multiplier():
    # IHP xschem w is TOTAL width; tsmcN65 CDF w is PER-FINGER (wf = w*fingers), and the
    # netlister's multiplier is simM. M1 (w=2u ng=2 m=3) must emit w=1u fingers=2 simM=3;
    # M2's symbolic total (w=wtot ng=4) is undividable -> drop w with a warning rather
    # than netlist at 4x the intended size.
    sch, symlib = _load("mos_fingered.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="fingered", devmap=load_device_map(), symlib=symlib
    )
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


def test_emit_warns_on_symbolic_param_values():
    sch, symlib = _load("amp_001_5t.sch")
    r = emit_schematic_il(
        sch, lib="LIBX", cell="amp", devmap=load_device_map(), symlib=symlib
    )
    assert any("symbolic parameter" in w for w in r.warnings)
    assert len(r.expected_bindings) == 24


# --- device map ------------------------------------------------------------------


def test_default_map_covers_fixture_devices_and_denylists_kit():
    m = load_device_map()
    rule = m.lookup("sg13g2_pr/sg13_lv_nmos.sym")
    assert rule is not None and (rule.lib, rule.cell) == ("tsmcN65", "nch_lvt")
    pmos = m.lookup("devices/sg13_lv_pmos_np.sym")
    assert pmos is not None and pmos.cell == "pch_lvt"
    vsrc = m.lookup("devices/vsource.sym")
    assert vsrc is not None and vsrc.cell == "vdc"
    # bare basenames (no directory) must match too — corpus files reference both ways
    bare = m.lookup("capa.sym")
    assert bare is not None and bare.cell == "cap"
    assert m.lookup("not/mapped.sym") is None
    assert m.is_kit_lib("tsmcN65") and not m.is_kit_lib("MYLIB")


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
        "Vctl", "VDD", "VB_p", "VA_p", "Vctl_not", "VSS", "VB_n", "VA_n",
    ]
    assert r1.terms["VDD"] == "inputOutput"
    il = r1.il
    assert il.count("dbCreateLine(") == 36  # 36 L records (body + pin leads)
    assert il.count("dbCreatePin(") == 8
    assert il.count("dbCreateEllipse(") == 1  # the 360-degree A record (clock bubble)
    assert '"logical label" \n' not in il
    assert "[@partName]" in il and "[@instanceName]" in il  # @symname/@name texts
    assert 'schCreateSymbolLabel(cv' in il and '"pin name"' in il
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
    seen = {"chopper_diff_top"}
    builds, _sch = _collect_dependencies(
        FIXTURES / "chopper-diff.sch", load_device_map(), 0.0125, "LIBX", seen, warnings
    )
    kinds = [(k, c) for k, c, *_ in builds]
    # chopper-diff.sch instantiates transmission_gate_pair (sym + sibling .sch) only.
    assert ("sch", "transmission_gate_pair") in kinds
    assert ("sym", "transmission_gate_pair") in kinds
    # every build carries its source path (netcheck resolves sources from here)
    assert all(src.exists() for _k, _c, _r, src in builds)
    # scheduled local cells do not produce "unmapped symref" warnings
    assert not [w for w in warnings if "unmapped" in w]


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
        cv2sym(None, "tsmcN65", "nch_lvt", m)
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
        labels=[(*cad(590, -240), "vctl"), (*cad(590, -580), "vctl_not"),
                (*cad(560, -280), "port_A"), (*cad(620, -280), "port_B"),
                (*cad(560, -540), "port_A"), (*cad(620, -540), "port_B"),
                (*cad(590, -280), "VSS"), (*cad(590, -540), "VDD")],
        pins=[("port_A", "input", *cad(380, -400)), ("port_B", "input", *cad(740, -400)),
              ("vctl", "input", *cad(520, -180)), ("vctl_not", "input", *cad(410, -620)),
              ("VDD", "input", *cad(590, -460)), ("VSS", "input", *cad(590, -340))],
        instances=[
            DumpInstance("M1", "tsmcN65", "nch_lvt", *cad(590, -260), "R90",
                         {"w": "150n", "l": "130n", "simM": "1", "fingers": "1"}),
            DumpInstance("M2", "tsmcN65", "pch_lvt", *cad(590, -560), "MYR90",
                         {"w": "150n", "l": "130n", "simM": "1", "fingers": "1"}),
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
            "I M1 tsmcN65 nch_lvt 7.375 3.25 R90\\n"
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


# --- verifier (offline, mocked readback) --------------------------------------------


def _tgate_emit():
    sch, symlib = _load("transmission_gate_pair.sch")
    return emit_schematic_il(
        sch, lib="LIBX", cell="tgate", devmap=load_device_map(), symlib=symlib
    )


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
            "M1 (a b c d) nch_lvt l=130.0n w=150.0n",
            "simulatorOptions options reltol=1e-3",
            "saveOptions options save=allpub",
        ]
    )
    section = extract_design_section(full)
    assert "include" not in section
    assert "simulatorOptions" not in section
    assert "M1 (a b c d) nch_lvt" in section


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
    assert "M1 (port_A vctl port_B VSS) nch_lvt" in text


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
