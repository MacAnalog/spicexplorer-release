"""Device factory, PDK map, and node-model unit tests."""

from spicexplorer_circuitgraph import IHP_SG13G2, CircuitGraph
from spicexplorer_circuitgraph.device_factory import DeviceFactory
from spicexplorer_circuitgraph.model.nodes import (
    CapacitorNode,
    CurrentSourceNode,
    DeviceType,
    MosfetNode,
    MosPolarityType,
    ResistorNode,
    SubcktInstanceNode,
    VoltageSourceNode,
)
from spicexplorer_core.spice_engine import NetlistView

_NETLIST = """\
* factory coverage
M1 d g s b sg13_lv_nmos w=1u l=0.13u
M2 d2 g2 s2 b2 sg13_lv_pmos w=2u l=0.13u
R1 a b 10k
C1 c d 50f
V1 vdd 0 1.8
I1 n 0 20u
Xsub a b mysub
.end
"""


def _factory_node(ref: str):
    view = NetlistView.from_string(_NETLIST)
    return DeviceFactory(IHP_SG13G2).create(ref, view)


def test_factory_dispatch_by_prefix():
    assert isinstance(_factory_node("M1"), MosfetNode)
    assert isinstance(_factory_node("R1"), ResistorNode)
    assert isinstance(_factory_node("C1"), CapacitorNode)
    assert isinstance(_factory_node("V1"), VoltageSourceNode)
    assert isinstance(_factory_node("I1"), CurrentSourceNode)


def test_factory_models_generic_subckt_instance():
    # Phase 2: Xsub is a generic subckt instance — now modeled as a SubcktInstanceNode.
    node = _factory_node("Xsub")
    assert isinstance(node, SubcktInstanceNode)
    assert node.device_type is DeviceType.SUBCKT
    assert node.subckt_name == "mysub"
    assert len(node.ports()) == 2  # 'a', 'b' -> positional ports (def not present)


def test_factory_returns_none_for_truly_unsupported_device():
    # A BJT has no prefix mapping and is not an X-instance — still unrecognized.
    view = NetlistView.from_string("* bjt\nQ1 c b e npn_mod\n.end\n")
    assert DeviceFactory(IHP_SG13G2).create("Q1", view) is None


def test_mos_polarity_from_substring_without_pdk():
    view = NetlistView.from_string(_NETLIST)
    factory = DeviceFactory(pdk=None)  # no PDK → substring fallback
    m1, m2 = factory.create("M1", view), factory.create("M2", view)
    assert isinstance(m1, MosfetNode) and m1.polarity is MosPolarityType.NMOS
    assert isinstance(m2, MosfetNode) and m2.polarity is MosPolarityType.PMOS


def test_mos_polarity_via_pdk_map():
    m1, m2 = _factory_node("M1"), _factory_node("M2")
    assert isinstance(m1, MosfetNode) and m1.polarity is MosPolarityType.NMOS
    assert isinstance(m2, MosfetNode) and m2.polarity is MosPolarityType.PMOS


def test_mosfet_carries_model_and_params():
    m = _factory_node("M1")
    assert isinstance(m, MosfetNode)
    assert m.device_type is DeviceType.MOS
    assert m.spice_model == "sg13_lv_nmos"
    assert {"w", "l"} <= {k.lower() for k in m.params}


def test_pdk_classify_and_reverse_lookup():
    dev = IHP_SG13G2.classify("sg13_lv_pmos")
    assert dev is not None and dev.device_type is DeviceType.MOS and dev.polarity is MosPolarityType.PMOS
    assert IHP_SG13G2.classify("sky130_fd_pr__nfet_01v8") is None  # not an IHP device
    # reverse direction (drives Phase-4 emission)
    assert IHP_SG13G2.model_for(DeviceType.MOS, MosPolarityType.NMOS) == "sg13_lv_nmos"
    assert IHP_SG13G2.model_for(DeviceType.MOS, MosPolarityType.PMOS) == "sg13_lv_pmos"
    assert IHP_SG13G2.model_for(DeviceType.CAP) == "cap_cmim"


def test_is_diode_connected_fixed():
    # M1: DRAIN and GATE share net 'd' → diode-connected; M3 does not.
    g = CircuitGraph.from_netlist(
        NetlistView.from_string("* diode\nM1 d d 0 0 nmos_x\nM3 o i 0 0 nmos_x\n.end\n")
    )
    m1, m3 = g._comp_map["M1"], g._comp_map["M3"]
    assert isinstance(m1, MosfetNode) and m1.is_diode_connected(g._G) is True
    assert isinstance(m3, MosfetNode) and m3.is_diode_connected(g._G) is False
