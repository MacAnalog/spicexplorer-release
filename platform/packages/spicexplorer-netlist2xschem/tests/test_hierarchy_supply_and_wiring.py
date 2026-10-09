"""Hierarchy child sheets: supply-as-rail-and-port, and per-child wiring mode.

Raised while drawing a capless LDO's hierarchy as a readable schematic
(in an agent-first design repo), against a stock ``hierarchy._child_circuit`` that handed
every child ``supply={}``. Two defects, three fixes here:

* **the child must keep its rails** — ``_child_circuit`` inheriting the parent's supply map (so the
  child places rail-banded, not as one flat row) only works together with ``analysis._port_roles``
  keeping a DECLARED ``.subckt`` port a port even when it is also a supply net (otherwise the child's
  ``.subckt`` port list drops vdd/vss and the generated block symbol's pins no longer match it);
* **hybrid wiring can lose a pin** — the default ``wiring="hybrid"`` lets a net's trunk wire *cross* a
  pin's stub with no junction, and xschem connects only at a junction, so the pin can land on an
  unnamed net even though the topology gate (component/net counts) stays green. The real fix is
  computing wire pieces by xschem's own junction rule (see ``connectivity.py``'s docstring); the
  interim, contained one tested here is ``build_hierarchical_sch(..., child_wiring=...)`` — a mode (or
  a ``{block name: mode}`` map) a caller can use to rebuild just a MEASURED-bad child ``"labels"``,
  which cannot lose a pin, without forcing every other child sheet back to the plainer mode.
"""

from __future__ import annotations

from pathlib import Path

from spicexplorer_netlist2xschem import (
    BlockAnnotation,
    BlockAnnotationSet,
    analyze,
    from_string,
)
from spicexplorer_netlist2xschem.hierarchy import _child_circuit, build_hierarchical_sch
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity, N2XCircuit
from spicexplorer_netlist2xschem.sch_parser import parse_sch
from spicexplorer_netlist2xschem.sym_library import SymLibrary

FIXTURES = Path(__file__).parent / "fixtures"
SYM_ROOT = FIXTURES / "sym"


def _pmos_dev(ref: str, drain: str, gate: str, supply: str) -> Device:
    return Device(
        ref=ref,
        kind=DeviceKind.MOS,
        model="sg13_lv_pmos",
        polarity=MosPolarity.PMOS,
        pins=("DRAIN", "GATE", "SOURCE", "BULK"),
        nets={"DRAIN": drain, "GATE": gate, "SOURCE": supply, "BULK": supply},
        params={},
    )


# --------------------------------------------------------------------------------------------------
# P1 -- a declared supply port stays a port (analysis._port_roles)
# --------------------------------------------------------------------------------------------------
def test_declared_supply_port_gets_a_role_not_dropped():
    """A net that is BOTH a supply (rail) and a declared ``.subckt`` formal port must still get a
    ``port_role`` entry — otherwise the hierarchy child never draws a port-pin symbol for it, and its
    ``.subckt``'s formal port list (built from the drawn ipin/opin/iopin symbols) would not match the
    generated block symbol's pins, breaking the join the whole hierarchy strategy depends on."""
    dev = _pmos_dev("XM1", drain="vout", gate="vin", supply="vdd")
    circuit = N2XCircuit(
        name="child",
        devices=(dev,),
        nets=("vdd", "vin", "vout"),
        supply={"vdd": "VDD"},
        ports=("vdd", "vin", "vout"),
    )
    info = analyze(circuit)
    assert info.port_role.get("vdd") == "inout"


def test_undeclared_supply_net_is_not_a_port():
    """A supply net that is NOT a declared port (the ordinary case: a top-level circuit's own VDD)
    must stay off ``port_role`` -- it is drawn as a rail only. P1 only widens the exception for a
    net the circuit's own formal ports name."""
    dev = _pmos_dev("XM1", drain="vout", gate="vin", supply="vdd")
    circuit = N2XCircuit(
        name="top", devices=(dev,), nets=("vdd", "vin", "vout"), supply={"vdd": "VDD"}, ports=()
    )
    info = analyze(circuit)
    assert "vdd" not in info.port_role


# --------------------------------------------------------------------------------------------------
# P2 -- a hierarchy child inherits the parent's supply map (hierarchy._child_circuit)
# --------------------------------------------------------------------------------------------------
def test_child_circuit_inherits_parent_supply_filtered_to_its_own_nets():
    dev = _pmos_dev("XM1", drain="vout", gate="vin", supply="vdd")
    parent_supply = {"vdd": "VDD", "vss": "VSS", "unrelated": "VDD"}
    child = _child_circuit([dev], "blk1", ["vdd", "vin", "vout"], parent_supply)
    assert child.supply == {"vdd": "VDD"}  # vss/unrelated aren't among the child's own nets
    assert child.ports == ("vdd", "vin", "vout")  # boundary is untouched by the supply change
    assert child.nets == ("vdd", "vin", "vout")


def test_child_circuit_supply_empty_when_parent_has_none():
    dev = _pmos_dev("XM1", drain="vout", gate="vin", supply="vdd")
    child = _child_circuit([dev], "blk1", ["vdd", "vin", "vout"], {})
    assert child.supply == {}


# --------------------------------------------------------------------------------------------------
# P1 + P2 together, end to end: the child sheet draws the supply as BOTH a rail and a port pin.
# --------------------------------------------------------------------------------------------------
NETLIST = """\
* two mirrors sharing an output net -- current-mirror-shaped blocks (gate == drain, diode-connected)
XM1 net1 net1 vss vss sg13_lv_nmos w=1u l=0.5u
XM2 out  net1 vss vss sg13_lv_nmos w=1u l=0.5u
XM3 net2 net2 vdd vdd sg13_lv_pmos w=1u l=0.5u
XM4 out  net2 vdd vdd sg13_lv_pmos w=1u l=0.5u
.end
"""


def _two_mirrors():
    circuit = from_string(NETLIST, name="mirrors")
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("nmos_mirror", ("XM1", "XM2")),
            BlockAnnotation("pmos_mirror", ("XM3", "XM4")),
        )
    )
    return circuit, aset


def test_hierarchy_child_draws_its_supply_as_rail_and_port_pin():
    circuit, aset = _two_mirrors()
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib)
    assert not res.warnings
    child = parse_sch(res.children["nmos_mirror.sch"])
    # a port-pin symbol names vss (P1: the declared supply port kept its role)
    port_nets = {c.lab for c in child.components if c.symref.startswith("devices/iopin")}
    assert "vss" in port_nets
    # a rail wire is drawn for vss too (P2: the child inherited the supply map, so it rail-bands)
    rail_labels = {c.lab for c in child.components if c.symref == "devices/lab_wire.sym"}
    assert "vss" in rail_labels


# --------------------------------------------------------------------------------------------------
# P5 -- per-child wiring mode (the interim, contained fix for hybrid losing a pin)
# --------------------------------------------------------------------------------------------------
def _wire_count(sch_text: str) -> int:
    return len(parse_sch(sch_text).wires)


def test_default_child_wiring_is_hybrid_and_draws_wires():
    circuit, aset = _two_mirrors()
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib)
    assert _wire_count(res.children["nmos_mirror.sch"]) > 0
    assert _wire_count(res.children["pmos_mirror.sch"]) > 0


def test_child_wiring_labels_mode_draws_no_wires_for_every_block():
    circuit, aset = _two_mirrors()
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib, child_wiring="labels")
    assert _wire_count(res.children["nmos_mirror.sch"]) == 0
    assert _wire_count(res.children["pmos_mirror.sch"]) == 0
    # every pin is still named -- labels-mode never loses one
    for name in ("nmos_mirror.sch", "pmos_mirror.sch"):
        child = parse_sch(res.children[name])
        labelled = {c.lab for c in child.components if c.symref == "devices/lab_wire.sym"}
        assert {"vss", "vdd"} & labelled or {"net1", "net2"} & labelled  # sanity: it did label nets


def test_child_wiring_per_block_map_targets_only_the_measured_bad_block():
    """The primitive the design repo's shim needed: a caller measures ONE child's netlist losing a
    pin (an auto-named ``netN``) and rebuilds just that child ``labels`` -- every other, correctly
    wired child stays ``hybrid``. Before this parameter existed, the repo had to build the WHOLE
    hierarchy twice (all-hybrid, then all-labels) and splice the bad children's text out by hand."""
    circuit, aset = _two_mirrors()
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib, child_wiring={"nmos_mirror": "labels"})
    assert _wire_count(res.children["nmos_mirror.sch"]) == 0  # forced to labels
    assert _wire_count(res.children["pmos_mirror.sch"]) > 0  # untouched: still hybrid


# --------------------------------------------------------------------------------------------------
# P8 -- a declared block that formed no child must be nameable, not silently absent
# --------------------------------------------------------------------------------------------------
def test_unformed_blocks_is_empty_when_every_block_forms():
    circuit, aset = _two_mirrors()
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib)
    assert res.unformed_blocks == ()
    assert res.block_count == 2


def test_unformed_blocks_names_a_block_whose_devices_all_vanished():
    """A block naming devices absent from the circuit (a recertification renamed them, say) forms no
    child -- `build_hierarchical_sch` used to just drop it via a bare `continue`, so the only trace
    was the block *not being in* `res.children`/`res.symbols`. `unformed_blocks` names it directly,
    so a caller doesn't have to diff two block-id sets to notice."""
    circuit, aset = _two_mirrors()
    aset = BlockAnnotationSet(
        (*aset.blocks, BlockAnnotation("ghost_block", ("XM_RENAMED_1", "XM_RENAMED_2")))
    )
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib)
    assert res.unformed_blocks == ("ghost_block",)
    assert res.block_count == 2  # the two real blocks still formed


def test_unformed_blocks_names_a_single_device_block():
    """A "block" of fewer than 2 devices is also skipped (not worth a subcircuit) -- also counted."""
    circuit, aset = _two_mirrors()
    aset = BlockAnnotationSet((*aset.blocks, BlockAnnotation("lonely", ("XM1",))))
    lib = SymLibrary([SYM_ROOT])
    res = build_hierarchical_sch(circuit, aset, lib=lib)
    assert "lonely" in res.unformed_blocks
