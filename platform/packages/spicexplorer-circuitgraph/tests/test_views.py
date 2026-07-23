"""The built-in serialization strategies, exercised on the flat cascode DUT (via serialize())."""

from pathlib import Path

from spicexplorer_circuitgraph import IHP_SG13G2, CircuitGraph, serialize
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"


def _graph() -> CircuitGraph:
    return CircuitGraph.from_netlist(
        NetlistView.from_file(CASCODE_FLAT), name="ota-improved", pdk=IHP_SG13G2
    )


def test_json_flat_shape():
    flat = serialize(_graph(), "flat")
    xm1 = flat["XM1"]
    assert xm1["type"] == "Nmos_Mosfet"
    assert xm1["spice_model"] == "sg13_lv_nmos"
    # pins are inlined as top-level keys
    assert xm1["DRAIN"] == "net4" and xm1["GATE"] == "vinp"
    assert "params" not in xm1  # include_params=False


def test_json_flat_include_params():
    xm1 = serialize(_graph(), "flat", include_params=True)["XM1"]
    assert "params" in xm1 and {"w", "l"} <= {k.lower() for k in xm1["params"]}


def test_json_nested_shape():
    nested = serialize(_graph(), "nested")
    assert nested["circuit_name"] == "ota-improved"
    ids = {c["id"] for c in nested["components"]}
    assert {"XM1", "V1"} <= ids
    xm1 = next(c for c in nested["components"] if c["id"] == "XM1")
    assert xm1["polarity"] == "NMOS"
    assert xm1["connections"]["DRAIN"] == "net4"


def test_json_net_centric_inverts_graph():
    nc = serialize(_graph(), "net_centric")
    on_vdd = {e["component"] for e in nc["vdd"]}
    assert "V1" in on_vdd  # a supply source sits on vdd
    # every entry has component + pin
    assert all("component" in e and "pin" in e for entries in nc.values() for e in entries)


def test_llm_description_text():
    text = serialize(_graph(), "llm_description")
    assert text.startswith("Circuit Topology Description:")
    assert "is a Nmos_Mosfet" in text
    assert "Pin DRAIN connects to" in text


def test_role_detection_view_text():
    text = serialize(_graph(), "role_detection")
    assert text.startswith("Role-Oriented Circuit Description:")
    assert "polarity=NMOS" in text  # rendered as the enum value, not "MosPolarityType.NMOS"


def test_topology_views_has_both_adjacencies():
    text = serialize(_graph(), "topology")
    assert "Component-to-Net Adjacency:" in text
    assert "Net-to-Component Adjacency:" in text


def test_structural_role_summary_header_fixed():
    text = serialize(_graph(), "structural_role_summary")
    assert text.startswith("Structural Role Summary:")  # was the misspelled "Srtructural"
    assert "XM1 → NA" in text  # no annotation yet (Phase 6)
