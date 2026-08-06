"""Subcircuit-as-component (typed multi-port) + recursive step-in."""

from pathlib import Path

import pytest
from spicexplorer_circuitgraph import (
    IHP_SG13G2,
    CircuitGraph,
    graphs_equivalent,
    serialize,
    to_netlist,
)
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


# --- emission of the hierarchy (a recursive graph is not write-only) -------------------------
def test_recursive_graph_emits_the_subckt_definition():
    """`recurse=True` stores the child graphs; emission has to write them out.

    It used to write only the instance line, so the deck referenced a master that appeared
    nowhere in the file — a representation nothing could read back.
    """
    g = _build(FOLDED_TB, recurse=True)
    deck = to_netlist(g)
    assert ".subckt opamp vin- vin+ vout vdd ib vss" in deck
    assert deck.count(".subckt ") == 1 and deck.count(".ends") == 1
    # the instance line still references it, and the definition precedes the top level
    assert "X1 vin- vin+ out vdd ib GND opamp" in deck
    assert deck.index(".ends") < deck.index("X1 vin-")
    # the child's devices are inside the definition, not at the top level
    body = deck.split(".subckt")[1].split(".ends")[0]
    assert "XM1 net1 vin+ net7 vdd sg13_lv_pmos" in body


def test_hierarchical_deck_round_trips_by_isomorphism():
    g = _build(FOLDED_TB, recurse=True)
    reread = CircuitGraph.from_netlist(
        NetlistView.from_string(to_netlist(g), dialect="auto"), pdk=IHP_SG13G2, recurse=True
    )
    assert graphs_equivalent(g, reread)
    assert set(reread.subgraphs) == set(g.subgraphs)
    assert graphs_equivalent(g.subgraphs["X1"], reread.subgraphs["X1"])


def test_nested_definitions_are_emitted_once_each_innermost_first():
    nl = (
        "* nested\n.subckt inner a b\nR1 a b 1k\n.ends\n"
        ".subckt outer p q\nXi1 p q inner\n.ends\n"
        "X1 n1 0 outer\nX2 n1 0 outer\nV1 n1 0 1\n.end\n"
    )
    deck = to_netlist(_from_str(nl, recurse=True))
    assert deck.count(".subckt inner") == 1  # deduped across the two `outer` instances
    assert deck.count(".subckt outer") == 1
    assert deck.index(".subckt inner") < deck.index(".subckt outer")
    assert graphs_equivalent(
        _from_str(nl, recurse=True),
        CircuitGraph.from_netlist(
            NetlistView.from_string(deck, dialect="auto"), pdk=IHP_SG13G2, recurse=True
        ),
    )


def test_spectre_emission_writes_the_definition_too():
    nl = (
        "* diff pair block\n"
        ".subckt pair vin- vin+ out vss\n"
        "M1 out vin+ vss vss sg13_lv_nmos w=2u l=0.5u\n"
        "M2 out vin- vss vss sg13_lv_nmos w=2u l=0.5u\n"
        ".ends\n"
        "X1 inm inp o 0 pair\nV1 inp 0 dc 0.9\n.end\n"
    )
    deck = to_netlist(_from_str(nl, recurse=True), dialect="spectre")
    # net sanitization applies inside the definition's port list too
    assert "subckt pair vin_m vin_p out vss" in deck
    assert "ends pair" in deck
    assert "X1 (inm inp o 0) pair" in deck


def test_a_black_box_graph_emits_instance_lines_only():
    # recurse=False carries no definition body, so the output is unchanged from before.
    deck = to_netlist(_build(FOLDED_TB))
    assert ".subckt" not in deck and "X1 vin- vin+ out vdd ib GND opamp" in deck


# --- a definition may only be emitted when it is the WHOLE child circuit ---------------------
def test_a_definition_is_refused_when_the_child_build_dropped_a_device():
    """A device the child build could not type must not vanish into a `.subckt` body.

    Emitting the surviving components as the definition produces a deck that parses and
    simulates a circuit with the BJT deleted — the loud `unknown subckt` failure of the
    pre-definition emitter replaced by a silent wrong answer (ngspice-45: `Error: unknown
    subckt` before, `v(out) = -1.56e-18` after). Neither `compare_graphs`' skip census nor
    `rests_on_skipped` catches it: both read only the TOP level, whose census here is empty.
    """
    nl = (
        "* top\n"
        ".subckt amp inp out vdd vss\n"
        "M1 out inp vss vss sg13_lv_nmos w=1u l=0.15u\n"
        "Q1 out inp vss npnmod\n"          # a BJT: unmodelable, dropped by the child build
        ".ends amp\n"
        "V1 vdd 0 1.8\n"
        "X1 in out vdd 0 amp\n"
        ".end\n"
    )
    g = _from_str(nl, recurse=True)
    assert g.skipped_components == []              # the parent census sees nothing
    assert g.subgraphs["X1"].skipped_components == ["Q1"]
    with pytest.raises(ValueError, match="incomplete circuit"):
        to_netlist(g)
    # every dialect, and the dropped device is named
    with pytest.raises(ValueError, match="Q1"):
        to_netlist(g, dialect="spectre")
    # building strictly is the way through: the loss becomes an error at BUILD time instead
    with pytest.raises(ValueError, match="unsupported or malformed"):
        _from_str(nl, recurse=True, on_unknown="raise")


def test_a_definition_is_refused_when_its_ports_name_nothing_in_its_body():
    """Positional fallback ports ('1'..'N') would emit a header wired to none of the body.

    The instance wires 4 nets to a 3-port master, so `_subckt_instance` falls back to positional
    port names. Writing those into the header while the body carries the child's real net names
    emits `.subckt amp 1 2 3 4` over a body using `out`/`inp`/`vss`: a definition that parses and
    is completely disconnected from its ports.
    """
    nl = (
        "* positional\n"
        ".subckt amp inp out vss\n"
        "M1 out inp vss vss sg13_lv_nmos w=1u l=0.15u\n"
        ".ends amp\n"
        "V1 vdd 0 1.8\n"
        "X1 in out 0 vdd amp\n"           # 4 nets onto a 3-port master
        ".end\n"
    )
    g = _from_str(nl, recurse=True)
    x1 = g._comp_map["X1"]
    assert isinstance(x1, SubcktInstanceNode)
    assert [p.name for p in x1.ports()] == ["1", "2", "3", "4"]
    with pytest.raises(ValueError, match="name no net of its body"):
        to_netlist(g)
