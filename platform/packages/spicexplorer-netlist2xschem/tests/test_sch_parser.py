"""Parse an xschem ``.sch`` back into typed records — the reverse of emit.

Two anchors: (1) a *round-trip* — emit a ``.sch`` for a real OTA, parse it, and confirm every drawn
device reappears with the exact coordinates ``build_sch`` placed it at; (2) parsing the hand-drawn
analog-db block templates (multi-line property blocks, port pins, symmetric layout) — the geometry the
stamping placer relies on.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    PhasedPlacer,
    build_sch,
    from_file,
    parse_sch,
)
from spicexplorer_netlist2xschem.sch_parser import _brace_groups, _split_records

FIXTURES = Path(__file__).parent / "fixtures"


def test_round_trip_recovers_every_device_coordinate(sym_lib):
    """Emit → parse reproduces the placed device set, names and (x, y, rot, flip) exactly."""
    circuit = from_file(FIXTURES / "ota-improved.spice")
    placer = PhasedPlacer()
    doc = build_sch(circuit, lib=sym_lib, placer=placer)
    sch = parse_sch(doc.text)

    # Every emitted device (C-line for a real symbol) is recovered, none invented.
    drawn = {c.name: c for c in sch.devices}
    assert len(drawn) == doc.device_count

    # The placement transform of each device matches what the placer assigned (joining on the
    # spiceprefix-split name: the netlist XM1 is drawn as M1). The OTA fixtures are all-MOS, so
    # build_sch places the same device set the placer sees here.
    placement = placer.place(circuit, sym_lib)
    for ref, t in placement.items():
        comp = sch.device_by_name(ref)
        assert comp is not None, f"{ref} not found in parsed .sch"
        assert (comp.x, comp.y, comp.rot, comp.flip) == (t.x, t.y, t.rot, t.flip)


def test_parses_labels_and_ports_distinctly(sym_lib):
    """Net-label and port-pin symbols are classified apart from real devices."""
    circuit = from_file(FIXTURES / "ota-5t_tb-ac.spice")
    doc = build_sch(circuit, lib=sym_lib)
    sch = parse_sch(doc.text)

    assert all(c.is_label for c in sch.components if "lab_wire" in c.symref)
    assert all(not c.is_device for c in sch.components if c.is_label or c.is_port)
    # Devices, labels and ports partition the non-title components.
    real = [c for c in sch.components if c.symref.rsplit("/", 1)[-1] != "title.sym"]
    assert len(real) == len(sch.devices) + sum(
        1 for c in real if c.is_label or c.is_port
    )


def test_multiline_property_block_is_kept_whole():
    """A ``C`` whose ``{...}`` spans lines (one key=value per line) parses to one component."""
    text = (
        "v {xschem version=3.4.5 file_version=1.2}\n"
        "G {}\nK {}\nV {}\nS {}\nE {}\n"
        "C {sg13g2_pr/sg13_lv_nmos.sym} 440 -340 0 1 {name=M2\n"
        "l=0.13u\nw=0.15u\nng=1\nm=1\nmodel=sg13_lv_nmos\nspiceprefix=X\n}\n"
        "N 700 -310 700 -280 {\nlab=CM_tail}\n"
    )
    sch = parse_sch(text)
    assert len(sch.components) == 1
    c = sch.components[0]
    assert c.name == "M2"
    assert (c.x, c.y, c.rot, c.flip) == (440, -340, 0, 1)
    assert c.attrs["model"] == "sg13_lv_nmos"
    assert c.attrs["w"] == "0.15u"
    assert len(sch.wires) == 1
    assert sch.wires[0].lab == "CM_tail"


def test_split_records_respects_braces():
    rec = _split_records("C {a.sym} 0 0 0 0 {name=M1\nw=1u}\nN 0 0 0 10 {}\n")
    assert len(rec) == 2
    groups, tokens = _brace_groups(rec[0])
    assert groups[0] == "a.sym"
    assert tokens[:5] == ["C", "0", "0", "0", "0"]


@pytest.mark.parametrize(
    "rel",
    [
        "miscellaneous/diff_pair_nmos.sch",
        "current_mirror/nmos_current_sink/basic_current_mirror.sch",
        "current_mirror/nmos_current_sink/cascode_current_mirror.sch",
    ],
)
def test_parses_analog_db_block_templates(rel):
    """The hand-drawn block templates parse to their MOS devices + boundary port pins.

    Skips when the analog-db submodule isn't checked out (the templates live there)."""
    from spicexplorer_core import project_root

    tpl = project_root() / "examples" / "analog-db" / "templates" / rel
    if not tpl.is_file():
        pytest.skip(f"template not present: {tpl}")
    sch = parse_sch(tpl.read_text())
    mos = [c for c in sch.devices if "mos" in c.symref]
    assert len(mos) >= 2  # every mirror/pair template has at least two transistors
    ports = [c for c in sch.components if c.is_port]
    assert ports, "a block template declares its interface as ipin/iopin port pins"
    # The diff pair is laid out symmetrically: its two devices sit at mirrored flips.
    if "diff_pair" in rel:
        flips = sorted(c.flip for c in mos)
        assert flips == [0, 1]
