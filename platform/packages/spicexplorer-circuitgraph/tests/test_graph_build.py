"""CircuitGraph build behavior against the real IHP examples/OTA netlists."""

import glob
from pathlib import Path

import pytest
from spicexplorer_circuitgraph import IHP_SG13G2, CircuitGraph
from spicexplorer_circuitgraph.model.nodes import (
    CurrentSourceNode,
    MosfetNode,
    MosPolarityType,
    NetNode,
    SubcktInstanceNode,
    VoltageSourceNode,
)
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"
OTA5T_TB = _FIX / "ota-5t_tb-ac.spice"
FOLDED_TB = _FIX / "cora_testbench_ac.spice"
ALL_NETLISTS = sorted(glob.glob(str(_FIX / "*.spice")))


def _build(path, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(path), pdk=IHP_SG13G2, **kw)


def test_cascode_flat_counts_and_kinds():
    g = _build(CASCODE_FLAT, name="ota-improved")
    assert g.component_count == 24
    assert g.net_count == 20
    mosfets = [c for c in g.get_components() if isinstance(c, MosfetNode)]
    vsources = [c for c in g.get_components() if isinstance(c, VoltageSourceNode)]
    assert len(mosfets) == 20  # 16 XM* + 4 cascode XM*c
    assert len(vsources) == 4  # V1, V2, Vmeas1, Vmeas4


def test_mosfet_polarity_and_connections():
    g = _build(CASCODE_FLAT)
    xm1 = g._comp_map["XM1"]
    assert isinstance(xm1, MosfetNode) and xm1.polarity is MosPolarityType.NMOS
    assert xm1.spice_model == "sg13_lv_nmos"
    assert g.connections(xm1) == {"DRAIN": "net4", "GATE": "vinp", "SOURCE": "tail", "BULK": "vss"}
    xm4 = g._comp_map["XM4"]
    assert isinstance(xm4, MosfetNode) and xm4.polarity is MosPolarityType.PMOS


def test_supply_detection_names_rails():
    g = _build(CASCODE_FLAT)
    supplies = {n.name: n.supply_type for n in g.get_nets() if n.is_supply}
    assert supplies == {"vdd": "VDD", "vss": "VSS"}
    # a signal net is not a supply
    assert g._net_map["vout"].is_supply is False


def test_supply_detection_handles_underscored_and_global_names():
    # The 5t-ota testbench uses v_dd / v_ss / GND.
    g = _build(OTA5T_TB)
    supplies = {n.name: n.supply_type for n in g.get_nets() if n.is_supply}
    assert supplies.get("v_dd") == "VDD"
    assert supplies.get("v_ss") == "VSS"
    assert supplies.get("GND") == "GND"


def test_raw_testbench_graphs_with_subckt_instance_as_component():
    # Phase 2: the DUT subckt instance XOTA is modeled (not skipped), alongside the sources.
    g = _build(OTA5T_TB)
    names = {c.name for c in g.get_components()}
    assert {"XOTA", "VDD", "VSS", "C1", "VIN", "I0", "VENABLE"} <= names
    assert isinstance(g._comp_map["XOTA"], SubcktInstanceNode)  # subckt-as-component
    assert isinstance(g._comp_map["I0"], CurrentSourceNode)  # I-source coverage


def test_raise_policy_aborts_on_truly_unsupported_device():
    # A BJT (Q-prefix) has no mapping and is not a subckt instance — raise under strict policy.
    netlist = "* bjt\nM1 d g s b sg13_lv_nmos\nQ1 c base e npn_mod\n.end\n"
    with pytest.raises(ValueError, match="unsupported or malformed"):
        CircuitGraph.from_netlist(NetlistView.from_string(netlist), on_unknown="raise")


def test_step_into_subckt_then_build_folded_opamp():
    # NetlistView steps into the hyphen-free `opamp` subckt; build the DUT graph from it.
    inner = NetlistView.from_file(FOLDED_TB).get_subcircuit("X1")
    g = CircuitGraph.from_netlist(inner, name="opamp", pdk=IHP_SG13G2)
    mosfets = [c for c in g.get_components() if isinstance(c, MosfetNode)]
    assert len(mosfets) == 14
    xm0 = g._comp_map["XM0"]
    assert isinstance(xm0, MosfetNode) and xm0.polarity is MosPolarityType.PMOS


def test_bipartite_invariant_rejects_bad_edges():
    g = CircuitGraph("x")
    n1, n2 = g.add_net(NetNode("a")), g.add_net(NetNode("b"))
    from spicexplorer_circuitgraph.model.edges import PinTypeTwoTerminal

    with pytest.raises(TypeError):
        g.connect(n1, n2, PinTypeTwoTerminal.P)  # type: ignore[arg-type]  # net↔net is illegal


@pytest.mark.parametrize("path", ALL_NETLISTS, ids=lambda p: p.split("fixtures/")[-1])
def test_every_example_builds(path):
    g = _build(path)  # default skip policy — must never abort
    assert g.component_count > 0
    assert g.net_count > 0
