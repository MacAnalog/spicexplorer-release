"""Strategy 2 — template stamping lays each block at its hand-drawn symmetric geometry.

Two anchors: (1) a hermetic test that a two-device block stamped from a mirror-symmetric template
``.sch`` comes out mirror-symmetric (the differential-branch requirement), driven by a hand-built
contract pointing at a fixture template; (2) an end-to-end test (circuitgraph as the producer) that
stamping a real 5T-OTA keeps the device/port set identical to block-aware placement (connectivity is
unchanged — only coordinates move).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    BlockAnnotation,
    BlockAnnotationSet,
    build_sch,
    from_string,
    parse_sch,
    resolve_template_sch,
)

FIXTURES = Path(__file__).parent / "fixtures"

# A minimal mirror-symmetric two-device template: M1 left (flip 0), M2 right (flip 1), same row.
_MINI_PAIR_SCH = (
    "v {xschem version=3.4.5 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n"
    "C {sg13g2_pr/sg13_lv_nmos.sym} 440 -340 0 0 {name=M1\nl=0.13u\nw=0.15u\n"
    "model=sg13_lv_nmos\nspiceprefix=X\n}\n"
    "C {sg13g2_pr/sg13_lv_nmos.sym} 720 -340 0 1 {name=M2\nl=0.13u\nw=0.15u\n"
    "model=sg13_lv_nmos\nspiceprefix=X\n}\n"
    "C {ipin.sym} 360 -340 0 0 {name=p1 lab=vinp}\n"
    "C {ipin.sym} 790 -340 0 1 {name=p2 lab=vinn}\n"
)

# A flat two-NMOS differential-pair-like host (the names XM1/XM2 join the contract).
_HOST = (
    "XM1 drain_p vinp tail vss sg13_lv_nmos w=0.15u l=0.13u\n"
    "XM2 drain_n vinn tail vss sg13_lv_nmos w=0.15u l=0.13u\n"
    ".end\n"
)


def _pair_annotations(template_sch: str) -> BlockAnnotationSet:
    """A one-block contract naming the host pair and the template each device fills (host→slot)."""
    return BlockAnnotationSet(
        (
            BlockAnnotation(
                block_id="dp#1",
                devices=("XM1", "XM2"),
                label="diff pair",
                family="differential_pair",
                template_sch=template_sch,
                device_slots=(("XM1", "XM1"), ("XM2", "XM2")),
            ),
        )
    )


def test_resolve_template_sch_handles_absolute_and_rooted(tmp_path):
    f = tmp_path / "mini_pair.sch"
    f.write_text(_MINI_PAIR_SCH)
    assert resolve_template_sch(str(f)) == f  # absolute
    assert resolve_template_sch("mini_pair.sch", root=tmp_path) == f  # rooted
    assert resolve_template_sch("nope.sch", root=tmp_path) is None
    assert resolve_template_sch("") is None


def test_stamped_pair_is_mirror_symmetric(tmp_path, sym_lib):
    """The two host devices land on mirrored flips and the same row — symmetric differential branches."""
    tpl = tmp_path / "mini_pair.sch"
    tpl.write_text(_MINI_PAIR_SCH)
    circuit = from_string(_HOST, name="pair")
    aset = _pair_annotations(str(tpl))

    doc = build_sch(circuit, lib=sym_lib, annotations=aset, placement_mode="template-stamp")
    sch = parse_sch(doc.text)
    m1, m2 = sch.device_by_name("XM1"), sch.device_by_name("XM2")
    assert m1 is not None and m2 is not None
    assert {m1.flip, m2.flip} == {0, 1}  # mirror symmetry carried from the template
    assert m1.y == m2.y  # same row
    assert m1.x != m2.x  # side by side


def test_unstampable_block_falls_back_to_block_aware(sym_lib):
    """A block whose template_sch can't be resolved degrades to block-aware (with a warning), not a crash."""
    circuit = from_string(_HOST, name="pair")
    aset = _pair_annotations("does/not/exist.sch")
    doc = build_sch(circuit, lib=sym_lib, annotations=aset, placement_mode="template-stamp")
    assert doc.device_count == 2  # still drawn
    assert any("template-stamp" in w for w in doc.warnings)


# --- end-to-end with the real detector + analog-db templates ----------------------------------
cg = pytest.importorskip("spicexplorer_circuitgraph")

from spicexplorer_core import project_root  # noqa: E402
from spicexplorer_core.spice_engine import NetlistView  # noqa: E402
from spicexplorer_netlist2xschem import from_file  # noqa: E402

EXAMPLE = "examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice"


def _ota5t_annotations():
    from spicexplorer_circuitgraph import (
        CircuitGraph,
        find_subcircuits,
        group_matches,
    )
    from spicexplorer_circuitgraph.annotations import export_subcircuit_annotations

    p = project_root() / EXAMPLE
    if not p.exists():
        return None, None
    g = CircuitGraph.from_netlist(NetlistView.from_file(p), name="ota5t")
    aset = BlockAnnotationSet.from_dict(
        export_subcircuit_annotations(group_matches(find_subcircuits(g)))
    )
    return from_file(p), aset


def test_template_stamp_is_device_and_port_neutral_on_5t_ota():
    """Stamping a real OTA keeps the same devices, ports and labels as block-aware — only coords move."""
    circuit, aset = _ota5t_annotations()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    assert aset and any(b.template_sch for b in aset.blocks), "producer carried template_sch"

    block = build_sch(circuit, annotations=aset, placement_mode="block-aware")
    stamp = build_sch(circuit, annotations=aset, placement_mode="template-stamp")
    assert not stamp.warnings  # every block stamped from a resolved template
    assert (stamp.device_count, stamp.port_count) == (block.device_count, block.port_count)

    # The detected differential pair is drawn mirror-symmetric (one flip 0, one flip 1).
    dp = next((b for b in aset.blocks if b.family == "differential_pair"), None)
    if dp is not None:
        sch = parse_sch(stamp.text)
        devs = [sch.device_by_name(r) for r in dp.devices]
        flips = {d.flip for d in devs if d is not None}
        assert flips == {0, 1}
