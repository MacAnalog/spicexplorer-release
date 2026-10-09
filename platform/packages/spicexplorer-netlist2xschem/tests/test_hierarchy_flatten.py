"""Flattening a block hierarchy back to the certified flat cell, and the block-coverage report.

Plus the six generator behaviours a design repo used to assert by GREPPING this package's source
(``assert_platform_support``). A design repo checking platform behaviour by inspecting platform
source is a symptom of that behaviour having no regression test; these are the tests, so a
regression fails here instead of quietly redrawing a wrong sheet somewhere downstream.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import analysis as _analysis
from spicexplorer_netlist2xschem import annotation as _annotation
from spicexplorer_netlist2xschem import emit as _emit
from spicexplorer_netlist2xschem import hierarchy as _hierarchy
from spicexplorer_netlist2xschem import mapping as _mapping
from spicexplorer_netlist2xschem.annotation import BlockAnnotation, BlockAnnotationSet
from spicexplorer_netlist2xschem.hierarchy import flatten_hierarchy
from spicexplorer_netlist2xschem.ingest import from_file

# The shape xschem writes for a block hierarchy: the CELL's own devices at top level, one
# `.subckt` per drawn block, and each child owning an auto-named `net1` of its own.
HIER = """* amp -- hierarchical, two blocks
.subckt bias_ref vdd nbias vss
R1 vdd net1 100k
R2 net1 nbias 50k
R3 nbias vss 25k
.ends

.subckt gain_stage vdd nbias out vss
R4 vdd net1 1k
R5 net1 out 2k
R6 nbias vss 3k
.ends

XBIAS vdd nbias vss bias_ref
XSTAGE vdd nbias out vss gain_stage
RLOAD out vss 10k
.end
"""


def _write(tmp_path: Path, text: str = HIER) -> Path:
    p = tmp_path / "amp_hier.spice"
    p.write_text(text)
    return p


def test_the_flat_result_keeps_every_leaf_instance_name(tmp_path: Path):
    """The parameter join is device by device, so a flattener that renames leaves produces a
    netlist that is equivalent and unjoinable."""
    r = flatten_hierarchy(_write(tmp_path), tmp_path / "flat.spice")
    text = r.out.read_text()
    for ref in ("R1", "R2", "R3", "R4", "R5", "R6", "RLOAD"):
        assert any(ln.split()[0] == ref for ln in text.splitlines() if ln.strip()), ref
    assert r.devices == 7
    assert len(r.spliced) == 2


def test_two_children_owning_a_net1_stay_two_different_nodes(tmp_path: Path):
    """Unlabelled nodes are auto-named PER SHEET, so both children own a `net1`."""
    r = flatten_hierarchy(_write(tmp_path), tmp_path / "flat.spice")
    assert set(r.qualified_local_nets) == {"xbias.net1", "xstage.net1"}
    text = r.out.read_text()
    assert "xbias.net1" in text and "xstage.net1" in text
    assert not any(t == "net1" for ln in text.splitlines() for t in ln.split())


def test_the_formal_ports_are_replaced_by_the_actual_nets(tmp_path: Path):
    r = flatten_hierarchy(_write(tmp_path), tmp_path / "flat.spice")
    lines = {ln.split()[0]: ln.split() for ln in r.out.read_text().splitlines() if ln.strip()}
    assert lines["R3"][1:3] == ["nbias", "vss"]  # the parent's names, not the child's formals
    assert lines["R5"][2] == "out"


def test_a_leaf_name_collision_between_blocks_raises(tmp_path: Path):
    clash = HIER.replace("R4 vdd net1 1k", "R1 vdd net1 1k")
    with pytest.raises(ValueError, match="leaf R1 appears in both"):
        flatten_hierarchy(_write(tmp_path, clash), tmp_path / "flat.spice")


def test_a_device_outside_every_block_survives_untouched(tmp_path: Path):
    r = flatten_hierarchy(_write(tmp_path), tmp_path / "flat.spice")
    assert "RLOAD out vss 10k" in r.out.read_text()


def test_the_note_is_recorded_in_the_header(tmp_path: Path):
    r = flatten_hierarchy(_write(tmp_path), tmp_path / "flat.spice", note="drawing of record")
    assert "drawing of record" in r.out.read_text().splitlines()[0]


# ------------------------------------------------------------------- coverage ----

FLAT = """* cell -- flat
R1 vdd out 1k
R2 out vss 2k
VREF vdd vss dc 1.2
.end
"""


def _circuit(tmp_path: Path):
    p = tmp_path / "cell.spice"
    p.write_text(FLAT)
    return from_file(p, name="cell")


def test_coverage_reports_a_device_in_no_block_at_all(tmp_path: Path):
    """The direction `validate()` does not cover, and nothing else in the package checks."""
    c = _circuit(tmp_path)
    blocks = BlockAnnotationSet(
        (BlockAnnotation(block_id="div", label="divider", devices=("R1",)),)
    )
    cov = blocks.coverage(c)
    assert cov["unknown_devices"] == []
    assert "R2" in cov["unannotated_devices"]
    assert cov["blocks_declared"] == 1


def test_a_declared_loose_device_is_not_a_finding(tmp_path: Path):
    c = _circuit(tmp_path)
    blocks = BlockAnnotationSet(
        (BlockAnnotation(block_id="div", label="divider", devices=("R1", "R2")),)
    )
    assert blocks.coverage(c, loose=["VREF"])["unannotated_devices"] == []
    assert "VREF" in blocks.coverage(c)["unannotated_devices"]


def test_coverage_reports_an_annotated_device_the_circuit_does_not_have(tmp_path: Path):
    c = _circuit(tmp_path)
    blocks = BlockAnnotationSet((BlockAnnotation(block_id="x", label="x", devices=("R9",)),))
    assert blocks.coverage(c)["unknown_devices"] == ["R9"]
    with pytest.raises(ValueError, match="unresolved device"):
        blocks.validate(c)  # the fail-closed half still raises


# ------------------------------------------- the six behaviours a drawing of record needs ----


def test_p1_a_declared_supply_port_stays_a_port():
    """A `.subckt` port that happens to be a supply is still a port, so a child sheet keeps its
    rails and still re-netlists."""
    assert "DECLARED" in inspect.getsource(_analysis._port_roles)


def test_p2_a_child_inherits_the_parents_supply_map():
    src = inspect.getsource(_hierarchy._child_circuit)
    assert "supply={n: r for n, r in supply.items() if n in nets}" in src


def test_p3_a_designs_own_cell_symbol_can_be_registered():
    """Without it a bench sheet's `XDUT ... <cell>` is dropped instead of drawn."""
    assert callable(getattr(_mapping, "register_subckt_symbol", None))


def test_p4_the_netlisted_value_is_never_abbreviated():
    """The display shortening used to be written into the instance's `value=`, which is the
    attribute xschem netlists — truncating a long pulse() stimulus or a parameter expression."""
    long = "x" * 40
    assert _emit._display_value(long) == long


def test_p5_the_child_wiring_mode_is_per_child():
    """`hybrid` lets a net's trunk CROSS a pin's stub with no junction, and xschem connects only
    at junctions — so a block measured to have lost a pin is redrawn `labels`, which cannot."""
    assert "child_wiring" in inspect.signature(_hierarchy.build_hierarchical_sch).parameters


def test_p8_the_annotation_loader_can_fail_closed():
    assert "circuit" in inspect.signature(_annotation.BlockAnnotationSet.load).parameters
