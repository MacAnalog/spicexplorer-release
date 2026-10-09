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
    BlockStamp,
    PlacementHints,
    TemplateStampPlacer,
    Transform,
    build_block_stamps,
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


class _HintSpyPlacer:
    """A base placer that records the hints it was handed (and lays devices out on one row)."""

    def __init__(self) -> None:
        self.seen: PlacementHints | None = None

    def place(self, circuit, lib=None, *, hints=None):
        self.seen = hints
        return {d.ref: Transform(240 * i, 0, 0, 0) for i, d in enumerate(circuit.devices)}


def test_caller_hints_survive_alongside_the_stamp_clusters():
    """LEAF-F15 (XS-2): with a stamp present, a caller's own hints used to be dropped — the base
    placer saw only the stamp clusters. They are merged now; a device already in a stamp cluster
    stays in that cluster only (a device may belong to at most one cluster)."""
    extra = "XM3 x drain_p vss vss sg13_lv_nmos\nXM4 y x vss vss sg13_lv_nmos\n"
    circuit = from_string(_HOST.replace(".end\n", extra + ".end\n"), name="pair")
    stamp = BlockStamp(
        block_id="dp#1",
        local={"XM1": Transform(0, 0, 0, 0), "XM2": Transform(280, 0, 0, 1)},
        width=420,
    )
    spy = _HintSpyPlacer()
    caller = PlacementHints(
        clusters=(("XM2", "XM3", "XM4"),), stage={"XM3": 1}, role={"XM4": "load"}
    )
    placement = TemplateStampPlacer(stamps=(stamp,), base=spy).place(circuit, None, hints=caller)

    assert spy.seen is not None
    assert spy.seen.clusters == (("XM1", "XM2"), ("XM3", "XM4"))
    assert (spy.seen.stage, spy.seen.role) == ({"XM3": 1}, {"XM4": "load"})
    assert set(placement) == {"XM1", "XM2", "XM3", "XM4"}


_PAIR_STAMP = BlockStamp(
    block_id="dp#1",
    local={"XM1": Transform(0, 0, 0, 0), "XM2": Transform(280, 0, 0, 1)},
    width=420,
)
_STAMP_CLUSTERS = (("XM1", "XM2"),)
_CALLER_HINTS = PlacementHints(clusters=(("XM3", "XM4"),), stage={"XM3": 1}, role={"XM4": "load"})


@pytest.mark.parametrize(
    ("stamps", "hints", "seen"),
    [
        # no stamp: the caller's hints reach the base placer as given
        ((), _CALLER_HINTS, _CALLER_HINTS),
        # a stamp and no caller hints (None, or empty): the stamp clusters alone
        ((_PAIR_STAMP,), None, PlacementHints(clusters=_STAMP_CLUSTERS)),
        ((_PAIR_STAMP,), PlacementHints(), PlacementHints(clusters=_STAMP_CLUSTERS)),
        # stage/role-only caller hints (no clusters) are still passed with the stamp clusters
        (
            (_PAIR_STAMP,),
            PlacementHints(stage={"XM3": 1}, role={"XM4": "load"}),
            PlacementHints(clusters=_STAMP_CLUSTERS, stage={"XM3": 1}, role={"XM4": "load"}),
        ),
        # a caller cluster whose devices are all in the stamp is dropped, not kept empty
        (
            (_PAIR_STAMP,),
            PlacementHints(clusters=(("XM2", "XM1"), ("XM3", "XM4"))),
            PlacementHints(clusters=(("XM1", "XM2"), ("XM3", "XM4"))),
        ),
    ],
    ids=["no-stamp", "stamp-no-hints", "stamp-empty-hints", "stage-role-only", "owned-cluster"],
)
def test_base_placer_sees_the_stamp_clusters_merged_with_the_callers_hints(stamps, hints, seen):
    extra = "XM3 x drain_p vss vss sg13_lv_nmos\nXM4 y x vss vss sg13_lv_nmos\n"
    circuit = from_string(_HOST.replace(".end\n", extra + ".end\n"), name="pair")
    spy = _HintSpyPlacer()
    placement = TemplateStampPlacer(stamps=stamps, base=spy).place(circuit, None, hints=hints)
    assert spy.seen == seen
    assert set(placement) == {"XM1", "XM2", "XM3", "XM4"}


def test_a_recovered_bias_ref_slot_is_laid_out_as_a_leftover_device(tmp_path, sym_lib):
    """circuitgraph gives a recovered bias reference the synthetic slot `bias_ref`, which no
    template draws: the stamp skips that device (the block still stamps) and it is placed as a
    leftover, at its own origin."""
    tpl = tmp_path / "mini_pair.sch"
    tpl.write_text(_MINI_PAIR_SCH)
    circuit = from_string(_HOST.replace(".end\n", "XMB vb vb vss vss sg13_lv_nmos\n.end\n"))
    aset = BlockAnnotationSet(
        (
            BlockAnnotation(
                block_id="cm#1",
                devices=("XM1", "XM2", "XMB"),
                label="pair + bias reference",
                family="current_mirror",
                template_sch=str(tpl),
                device_slots=(("XM1", "XM1"), ("XM2", "XM2"), ("XMB", "bias_ref")),
            ),
        )
    )
    (stamp,) = build_block_stamps(aset, {d.ref for d in circuit.devices})
    assert stamp.devices == ("XM1", "XM2")
    placement = TemplateStampPlacer(stamps=(stamp,)).place(circuit, sym_lib)
    assert set(placement) == {"XM1", "XM2", "XMB"}
    assert len({(t.x, t.y) for t in placement.values()}) == 3

    doc = build_sch(circuit, lib=sym_lib, annotations=aset, placement_mode="template-stamp")
    assert doc.device_count == 3
    assert not any("template-stamp" in w for w in doc.warnings)


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
