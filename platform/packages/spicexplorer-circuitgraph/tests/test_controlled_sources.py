"""Controlled sources (G = VCCS, E = VCVS): build, emit, round-trip, degrade.

spicelib parses a G/E card as a two-node device with the controlling pair inside the value
token — the factory splits it back out, so the graph carries all four pins (P/N/CP/CN) and the
gain survives *verbatim* (the analog-db behavioral macromodels use bare symbols like ``GM``).
"""

import logging

from spicexplorer_circuitgraph import (
    CircuitGraph,
    CircuitGraphDoc,
    compare_graphs,
    to_netlist,
)
from spicexplorer_circuitgraph.model.nodes import DeviceType, VccsNode, VcvsNode
from spicexplorer_core.spice_engine import NetlistView

# The ideal-amp macromodel shape: a symbolic-gm VCCS + a numeric VCVS, controls sensed on nets
# that also carry other devices (vinp/vinn) — mirrors analog-db's `ideal-amp-fully-diff`.
_CS_NETLIST = """\
* controlled-source fixture
G1 voutn voutp vinp vinn GM
E1 outp outn vinp vinn 2.5
R1 voutp 0 1k
V1 vinp 0 dc 0.5
.end
"""


def _graph(text=_CS_NETLIST, name="cs"):
    return CircuitGraph.from_netlist(NetlistView.from_string(text), name=name)


# ----------------------------------------------------------------------
# Build: typed nodes, four pins, verbatim value
# ----------------------------------------------------------------------


def test_vccs_and_vcvs_nodes_built_with_control_pins():
    g = _graph()
    comps = {c.name: c for c in g.get_components()}
    g1, e1 = comps["G1"], comps["E1"]
    assert isinstance(g1, VccsNode) and g1.device_type is DeviceType.VCCS
    assert isinstance(e1, VcvsNode) and e1.device_type is DeviceType.VCVS
    # SPICE card order `G1 n+ n- nc+ nc- value` maps onto P/N/CP/CN
    assert g.connections(g1) == {"P": "voutn", "N": "voutp", "CP": "vinp", "CN": "vinn"}
    assert g.connections(e1) == {"P": "outp", "N": "outn", "CP": "vinp", "CN": "vinn"}
    # the gain/transconductance survives verbatim — a bare SYMBOL is legal
    assert g1.params["Value"] == "GM"
    assert e1.params["Value"] == "2.5"


def test_control_only_nets_are_registered():
    # spicelib's get_all_nodes can't see inside the value token, so a controlling net used
    # nowhere else must still be registered by the graph build (no phantom KeyError on emit).
    g = _graph("* ctrl-only\nG1 out 0 sensep sensen 1m\nR1 out 0 1k\n.end\n")
    assert {"sensep", "sensen"} <= {n.name for n in g.get_nets()}
    assert "sensep" in to_netlist(g)


# ----------------------------------------------------------------------
# Emit + re-parse round-trips
# ----------------------------------------------------------------------


def test_spice_emit_renders_four_terminal_card_and_reparses():
    g = _graph()
    spice = to_netlist(g)
    assert "G1 voutn voutp vinp vinn GM" in spice
    assert "E1 outp outn vinp vinn 2.5" in spice
    g2 = _graph(spice, name="reparsed")
    cmp = compare_graphs(g, g2)
    assert cmp.equivalent, cmp.reason


def test_spectre_emit_renders_vccs_and_vcvs_masters():
    scs = to_netlist(_graph(), dialect="spectre")
    assert "G1 (voutn voutp vinp vinn) vccs gm=GM" in scs
    assert "E1 (outp outn vinp vinn) vcvs gain=2.5" in scs


def test_braced_gain_and_trailing_params_roundtrip():
    net = "* braced\nG2 a 0 c d {2*GM} m=2\nR1 a 0 1k\n.end\n"
    g = _graph(net)
    g2 = g._comp_map["G2"]
    assert g2.params["Value"] == "{2*GM}" and g2.params["m"] == "2"
    spice = to_netlist(g)
    assert "G2 a 0 c d {2*GM} m=2" in spice
    assert compare_graphs(g, _graph(spice)).equivalent
    # SPICE {expr} braces render as a bare Spectre expression (emit.py `_expr` convention)
    assert "vccs gm=2*GM m=2" in to_netlist(g, dialect="spectre")


def test_doc_roundtrip_is_stable():
    g = _graph()
    doc = CircuitGraphDoc.from_graph(g)
    rebuilt = doc.to_graph()
    assert rebuilt.component_count == g.component_count
    assert rebuilt.net_count == g.net_count
    assert CircuitGraphDoc.from_graph(rebuilt).model_dump() == doc.model_dump()
    restored = CircuitGraphDoc.model_validate_json(doc.model_dump_json())
    assert CircuitGraphDoc.from_graph(restored.to_graph()).model_dump() == doc.model_dump()


# ----------------------------------------------------------------------
# Degrade: non-linear forms skip-and-warn (never a mis-pinned node)
# ----------------------------------------------------------------------


def test_nonlinear_forms_degrade_to_skip(caplog):
    net = (
        "* behavioral forms\n"
        "G1 a 0 value={v(c)*2}\n"
        "E1 x 0 POLY(2) c d e f 0 1 1\n"
        "R1 a 0 1k\n"
        ".end\n"
    )
    with caplog.at_level(logging.WARNING, logger="spicexplorer_circuitgraph"):
        g = _graph(net)
    assert [c.name for c in g.get_components()] == ["R1"]
    assert sum("linear 4-terminal" in r.message for r in caplog.records) == 2
