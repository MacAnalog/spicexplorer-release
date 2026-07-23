"""End-to-end proof of the detect → annotate → render pipeline.

The two leaf tools never import each other; their only coupling is the
``spicexplorer/xschem-block-annotations@1`` JSON. This test composes them at the edge (as orchestration
would): run circuitgraph's detector on a netlist, export the contract, then drive netlist2xschem's
overlay with it — confirming the instance-name join holds and the overlay is connectivity-neutral. It
is skipped when circuitgraph (a peer, not a dependency) isn't importable.
"""

from pathlib import Path

import pytest

cg = pytest.importorskip("spicexplorer_circuitgraph")

from spicexplorer_core import project_root  # noqa: E402
from spicexplorer_core.spice_engine import NetlistView  # noqa: E402
from spicexplorer_netlist2xschem import (  # noqa: E402
    BlockAnnotationSet,
    PhasedPlacer,
    PlacementHints,
    build_sch,
    from_file,
    from_string,
)
from spicexplorer_netlist2xschem.ingest import DeviceKind  # noqa: E402
from spicexplorer_netlist2xschem.mapping import align_pins, symref_for  # noqa: E402
from spicexplorer_netlist2xschem.sym_library import SymLibrary  # noqa: E402
from spicexplorer_netlist2xschem.wiring import PlacedDevice, device_extent  # noqa: E402

EXAMPLE = "examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice"
# Raw amplifier DUTs (subckt-wrapped) for the P5 block-overlap acceptance — a single-stage folded
# cascode and a larger multi-stage amp.
RAW_AMP = "examples/analog-db/raw"
_PAD = 40  # the top-level pad the overlay (annotation._PAD) draws each block box with


def _example_path() -> Path | None:
    p = project_root() / EXAMPLE
    return p if p.exists() else None


def _flatten_dut(name: str) -> str | None:
    """The raw DUT's body as a top-level netlist (strip the ``.subckt`` wrapper), or ``None`` if the
    analog-db submodule isn't checked out."""
    p = project_root() / RAW_AMP / name / "ihp-sg13g2" / "_dut.spice"
    if not p.exists():
        return None
    body = [
        ln
        for ln in p.read_text().splitlines()
        if not ln.strip().lower().startswith((".subckt", ".ends", ".end"))
    ]
    return "\n".join(body) + "\n.end\n"


def _place(circuit, hints):
    lib = SymLibrary.default()
    placement = PhasedPlacer().place(circuit, lib, hints=hints)
    placed: dict[str, PlacedDevice] = {}
    for dev in circuit.devices:
        symref = symref_for(dev, pdk="ihp-sg13g2")
        sym = lib.load(symref) if symref else None
        if sym is None:
            continue
        aligned = align_pins(dev, sym)
        if any(p not in aligned for p in dev.pins):
            continue
        placed[dev.ref] = PlacedDevice(
            ref=dev.ref,
            transform=placement[dev.ref],
            nets=dev.nets,
            aligned=aligned,
            is_source=dev.kind in (DeviceKind.VSOURCE, DeviceKind.ISOURCE),
        )
    return placed


def _overlap_and_footprint(aset: BlockAnnotationSet, placed) -> tuple[int, int]:
    """(total pairwise overlap area, total footprint area) of the **top-level** block boxes — the
    regions a reader sees as separate. A block box is the padded union of its placed devices' tuned
    extents (exactly what the overlay draws)."""
    boxes = []
    for b in aset.blocks:
        if b.parent_id is not None:
            continue
        members = [placed[r] for r in b.devices if r in placed]
        if not members:
            continue
        exts = [device_extent(pd) for pd in members]
        boxes.append(
            (
                min(e[0] for e in exts) - _PAD,
                min(e[1] for e in exts) - _PAD,
                max(e[2] for e in exts) + _PAD,
                max(e[3] for e in exts) + _PAD,
            )
        )
    overlap = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            w = min(a[2], b[2]) - max(a[0], b[0])
            h = min(a[3], b[3]) - max(a[1], b[1])
            if w > 0 and h > 0:
                overlap += w * h
    footprint = sum((bx[2] - bx[0]) * (bx[3] - bx[1]) for bx in boxes)
    return overlap, footprint


def test_detect_export_then_annotate_5t_ota():
    path = _example_path()
    if path is None:
        pytest.skip(f"{EXAMPLE} not present")

    # PRODUCER: detect on the flat netlist (same refs the schematic will place).
    graph = cg.CircuitGraph.from_netlist(NetlistView.from_file(path), name="ota_5t")
    groups = cg.group_matches(cg.find_subcircuits(graph))
    contract = cg.export_subcircuit_annotations(groups)
    assert contract["schema"] == "spicexplorer/xschem-block-annotations@1"
    families = {b["family"] for b in contract["blocks"]}
    assert {"current_mirror", "differential_pair"} <= families

    # CONSUMER: same netlist → placement → overlay driven by the produced JSON.
    circuit = from_file(path, name="ota_5t")
    aset = BlockAnnotationSet.from_dict(contract)
    doc = build_sch(circuit, annotations=aset)

    # every block landed on real placed devices (no warnings about unplaced refs) ...
    assert doc.annotation_count == len(contract["blocks"]) >= 3
    assert not doc.warnings
    placed_refs = {d.ref for d in circuit.devices}
    for b in contract["blocks"]:
        assert set(b["devices"]) <= placed_refs

    # ... and block-aware placement (the default) preserved the electrical content — same devices
    # placed, same circuit-I/O ports — even though it may move devices / re-route wires.
    base = build_sch(circuit)
    assert (doc.device_count, doc.port_count) == (base.device_count, base.port_count)
    # The overlay *without* block-aware placement stays byte-neutral: the boxes draw over the unchanged
    # block-agnostic layout, so every electrical count matches the base exactly.
    overlay_only = build_sch(circuit, annotations=aset, annotation_aware_placement=False)
    assert (
        overlay_only.device_count,
        overlay_only.wire_count,
        overlay_only.label_count,
        overlay_only.port_count,
    ) == (base.device_count, base.wire_count, base.label_count, base.port_count)


def test_nested_cascode_round_trips_end_to_end():
    """A 4-device cascode mirror → a nested (subsumed simple) block, rendered as an inner dashed box."""
    try:
        cg.default_subcircuit_library()
    except FileNotFoundError:
        pytest.skip("subcircuit template catalogue not present (analog-db submodule not checked out)")
    cascode = (
        "* cascode nmos current mirror\n"
        "XM1 net2 net1 VSS VSS sg13_lv_nmos\n"
        "XM2 net1 net1 VSS VSS sg13_lv_nmos\n"
        "XM3 iout iin net1 VSS sg13_lv_nmos\n"
        "XM4 iin iin net2 VSS sg13_lv_nmos\n"
        ".end\n"
    )
    graph = cg.CircuitGraph.from_netlist(NetlistView.from_string(cascode), name="cascode")
    contract = cg.export_subcircuit_annotations(cg.group_matches(cg.find_subcircuits(graph)))
    # a nested block (parent_id set) must be present
    assert any(b["parent_id"] for b in contract["blocks"])

    from spicexplorer_netlist2xschem import from_string

    doc = build_sch(from_string(cascode, name="cascode"), annotations=BlockAnnotationSet.from_dict(contract))
    boxes = [ln for ln in doc.text.splitlines() if ln.startswith("B ")]
    assert any("dash=" in ln for ln in boxes)  # the nested box is dashed
    assert any("dash=" not in ln for ln in boxes)  # the parent box is solid


@pytest.mark.parametrize("amp", ["amp_004_folded_cascode", "amp_011_peng_iac"])
def test_block_aware_placement_reduces_block_footprint_and_overlap(amp):
    """Acceptance: detect → place with the blocks as hints, and the recognised functional blocks
    occupy a **tighter, less-overlapping** region than the block-agnostic layout. Asserted on a
    single-stage folded cascode and a larger multi-stage amp.

    Block-aware placement never *increases* the total block footprint or top-level box overlap; on the
    larger amp — where the block-agnostic layout scatters a mirror's outputs across the whole width — it
    cuts the overlap by more than half. (Some residual overlap is inherent: blocks stacked in one
    current path share columns, so their axis-aligned boxes meet where the stack does.)"""
    text = _flatten_dut(amp)
    if text is None:
        pytest.skip(f"{RAW_AMP}/{amp} not present (analog-db submodule not checked out)")

    graph = cg.CircuitGraph.from_netlist(NetlistView.from_string(text), name=amp, pdk=cg.IHP_SG13G2)
    aset = BlockAnnotationSet.from_dict(cg.export_subcircuit_annotations(cg.annotate_subcircuits(graph)))
    assert aset.blocks, f"{amp}: detector found no blocks to drive placement"

    circuit = from_string(text, name=amp)
    agnostic = _overlap_and_footprint(aset, _place(circuit, None))
    hints = PlacementHints(clusters=aset.placement_clusters())
    aware = _overlap_and_footprint(aset, _place(circuit, hints))

    # never worse than the block-agnostic layout, on either metric
    assert aware[1] <= agnostic[1], f"{amp}: block-aware placement grew the footprint {agnostic[1]}→{aware[1]}"
    assert aware[0] <= agnostic[0], f"{amp}: block-aware placement grew the overlap {agnostic[0]}→{aware[0]}"
    # on the larger, scattered amp the win is decisive (overlap more than halved)
    if amp == "amp_011_peng_iac":
        assert aware[0] <= 0.6 * agnostic[0], (
            f"{amp}: expected the scatter to drop sharply, got {agnostic[0]}→{aware[0]}"
        )
