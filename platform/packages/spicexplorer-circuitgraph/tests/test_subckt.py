"""Subcircuit-as-component (typed multi-port) + recursive step-in."""

from pathlib import Path

from spicexplorer_circuitgraph import IHP_SG13G2, CircuitGraph, serialize
from spicexplorer_circuitgraph.model.edges import SubcktPortRole
from spicexplorer_circuitgraph.model.nodes import MosfetNode, SubcktInstanceNode
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
FOLDED_TB = _FIX / "cora_testbench_ac.spice"
OTA5T_TB = _FIX / "ota-5t_tb-ac.spice"
CASCODE_FLAT = _FIX / "ota-improved.spice"


def _build(path, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(path), pdk=IHP_SG13G2, **kw)


# --- 2A: subckt-as-component with formal, role-tagged ports (resolvable subckt) ------------
def test_resolvable_subckt_has_formal_named_ports_and_roles():
    g = _build(FOLDED_TB)
    x1 = g._comp_map["X1"]
    assert isinstance(x1, SubcktInstanceNode)
    assert x1.subckt_name == "opamp"
    roles = {p.name: p.role for p in x1.ports()}
    # registry-driven roles
    assert roles["vin+"] is SubcktPortRole.INPUT
    assert roles["vin-"] is SubcktPortRole.INPUT
    assert roles["vout"] is SubcktPortRole.OUTPUT
    assert roles["ib"] is SubcktPortRole.BIAS
    # supply-consistent rails
    assert roles["vdd"] is SubcktPortRole.POWER
    assert roles["vss"] is SubcktPortRole.GROUND
    # formal port -> actual net connections
    assert g.connections(x1) == {
        "vin-": "vin-", "vin+": "vin+", "vout": "out", "vdd": "vdd", "ib": "ib", "vss": "GND",
    }


def test_subckt_info_in_json_views():
    g = _build(FOLDED_TB)
    flat = serialize(g, "flat")["X1"]
    assert flat["type"] == "SubcktInstance"
    assert flat["subckt_name"] == "opamp"
    assert flat["port_roles"]["vdd"] == "power"


# --- hyphenated subckt: resolved via core's truncated-prefix fallback ----------------------
def test_hyphenated_subckt_resolves_to_formal_ports():
    g = _build(OTA5T_TB)
    xota = g._comp_map["XOTA"]
    assert isinstance(xota, SubcktInstanceNode)
    assert xota.subckt_name == "ota-5t"  # full name from the instance value token
    names = [p.name for p in xota.ports()]
    assert names == ["vdd", "vout", "vinp", "vinn", "ibias_20u", "d_ena", "vss"]
    roles = {p.name: p.role for p in xota.ports()}
    assert roles["vdd"] is SubcktPortRole.POWER
    assert roles["vss"] is SubcktPortRole.GROUND


# --- genuinely unresolvable subckt: positional ports + supply-inferred roles ---------------
def test_unresolvable_subckt_falls_back_to_positional_ports():
    nl = "* missing def\nX1 v_dd sig v_ss elsewhere\nVdd v_dd 0 1.5\nVss v_ss 0 0\n.end\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    x1 = g._comp_map["X1"]
    assert isinstance(x1, SubcktInstanceNode)
    assert x1.subckt_name == "elsewhere"
    names = [p.name for p in x1.ports()]
    assert names == ["1", "2", "3"]  # positional fallback
    # supply inference still tags the rail ports (port 1 -> v_dd, port 3 -> v_ss)
    roles = {p.name: p.role for p in x1.ports()}
    assert roles["1"] is SubcktPortRole.POWER
    assert roles["3"] is SubcktPortRole.GROUND


# --- 2B: recursive step-in -----------------------------------------------------------------
def test_recurse_expands_resolvable_subckt_to_matching_child_graph():
    g = _build(FOLDED_TB, recurse=True)
    assert "X1" in g.subgraphs
    child = g.subgraphs["X1"]
    # child equals a directly-built DUT graph
    direct = CircuitGraph.from_netlist(
        NetlistView.from_file(FOLDED_TB).get_subcircuit("X1"), name="opamp", pdk=IHP_SG13G2
    )
    assert child.component_count == direct.component_count
    assert child.net_count == direct.net_count
    assert len([c for c in child.get_components() if isinstance(c, MosfetNode)]) == 14


def test_recurse_expands_hyphenated_subckt_via_fallback():
    # XOTA references the hyphenated 'ota-5t' — resolved through core's truncated-prefix fallback.
    g = _build(OTA5T_TB, recurse=True)
    assert "XOTA" in g.subgraphs
    assert g.subgraphs["XOTA"].component_count == 13  # the 5T OTA core + enable chain
    assert isinstance(g._comp_map["XOTA"], SubcktInstanceNode)  # still modeled as a component


def test_recurse_skips_unresolvable_subckt():
    # a genuinely missing definition: no expansion, no crash.
    nl = "* missing def\nX1 a b elsewhere\nR1 a b 1k\n.end\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2, recurse=True)
    assert "X1" not in g.subgraphs
    assert isinstance(g._comp_map["X1"], SubcktInstanceNode)  # still modeled as a component


def test_primitive_only_netlist_has_no_subckt_nodes_or_recursion():
    g = _build(CASCODE_FLAT, recurse=True)
    assert not any(isinstance(c, SubcktInstanceNode) for c in g.get_components())
    assert g.subgraphs == {}


def test_same_net_on_multiple_ports_is_preserved():
    # XOTA wires v_out to two ports (positions 2 and 4) — both must survive as distinct ports.
    g = _build(OTA5T_TB)
    conns = g.connections(g._comp_map["XOTA"])
    assert sum(1 for net in conns.values() if net == "v_out") == 2


# --- review-driven regressions -------------------------------------------------------------
def _from_str(netlist: str, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_string(netlist), pdk=IHP_SG13G2, **kw)


def test_duplicate_formal_ports_fall_back_to_positional_no_lost_net():
    # A .subckt with two identically-named ports would collide on a name-keyed edge; the factory
    # rejects non-unique formal ports and uses positional names, so no terminal is dropped.
    nl = "* dup\n.subckt buf inp inp outp\nR1 inp outp 1k\n.ends\nX1 na nb nc buf\n.end\n"
    g = _from_str(nl)
    x1 = g._comp_map["X1"]
    assert isinstance(x1, SubcktInstanceNode)
    assert [p.name for p in x1.ports()] == ["1", "2", "3"]  # positional, unique
    assert len(g.connections(x1)) == 3  # all three terminals preserved


def test_flat_view_metadata_survives_colliding_port_name():
    # A subckt port literally named "type" must not overwrite the documented "type" field.
    nl = "* col\n.subckt s type vdd\nR1 type vdd 1k\n.ends\nX1 na vdd s\n.end\n"
    flat = serialize(_from_str(nl), "flat")["X1"]
    assert flat["type"] == "SubcktInstance"  # contract field intact, not clobbered by the net


def test_assigned_role_is_visible_on_the_edge_pin():
    # Locks the shared-SubcktPort-identity invariant: role assigned post-build shows on the edge.
    g = _build(FOLDED_TB)
    x1 = g._comp_map["X1"]
    edge_pins = [data["pin"] for _, _, data in g._G.edges(x1, data=True)]
    vdd_pin = next(p for p in edge_pins if getattr(p, "name", None) == "vdd")
    assert vdd_pin.role is SubcktPortRole.POWER


def test_nested_recursion_two_levels():
    nl = (
        "* nested\n.subckt inner a b\nR1 a b 1k\n.ends\n"
        ".subckt outer p q\nXi1 p q inner\n.ends\n"
        "X1 n1 0 outer\nV1 n1 0 1\n.end\n"
    )
    g = _from_str(nl, recurse=True)
    assert "X1" in g.subgraphs
    outer = g.subgraphs["X1"]
    assert "XI1" in outer.subgraphs  # spicelib upper-cases the instance ref
    assert [c.name for c in outer.subgraphs["XI1"].get_components()] == ["R1"]


def test_recursion_terminates_on_cyclic_subckt():
    # `a` instantiates itself — the _seen guard (keyed on subckt_name) must stop the descent.
    nl = "* cyc\n.subckt a p q\nXself p q a\n.ends\nX1 n1 n2 a\n.end\n"
    g = _from_str(nl, recurse=True)
    assert "X1" in g.subgraphs
    assert g.subgraphs["X1"].subgraphs == {}  # Xself expansion skipped (cycle)
