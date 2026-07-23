"""Round-trip: CircuitGraph -> CircuitGraphDoc -> CircuitGraph -> CircuitGraphDoc must be stable."""

import glob
from pathlib import Path

import pytest
from spicexplorer_circuitgraph import IHP_SG13G2, CircuitGraph, CircuitGraphDoc
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"
ALL_NETLISTS = sorted(glob.glob(str(_FIX / "*.spice")))


def _graph(path) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(path), pdk=IHP_SG13G2)


def test_from_graph_meta_matches():
    g = _graph(CASCODE_FLAT)
    doc = CircuitGraphDoc.from_graph(g)
    assert doc.meta.component_count == g.component_count == 24
    assert doc.meta.net_count == g.net_count == 20
    assert len(doc.components) == 24 and len(doc.nets) == 20


def test_doc_preserves_device_metadata():
    doc = CircuitGraphDoc.from_graph(_graph(CASCODE_FLAT))
    xm1 = next(c for c in doc.components if c.id == "XM1")
    assert xm1.device_type.value == "MOS"
    assert xm1.polarity is not None and xm1.polarity.value == "NMOS"
    assert xm1.connections["DRAIN"] == "net4"
    # the round-trip contract is lossless: the body/BULK terminal is retained (unlike the
    # description views, which drop it by default to reduce clutter)
    assert "BULK" in xm1.connections
    assert "w" in {k.lower() for k in xm1.params}


@pytest.mark.parametrize("path", ALL_NETLISTS, ids=lambda p: p.split("fixtures/")[-1])
def test_roundtrip_is_stable(path):
    g = _graph(path)
    doc = CircuitGraphDoc.from_graph(g)
    rebuilt = doc.to_graph()
    # structural identity: same component/net counts after a rebuild
    assert rebuilt.component_count == g.component_count
    assert rebuilt.net_count == g.net_count
    # and the serialized form is byte-stable across the round-trip
    assert CircuitGraphDoc.from_graph(rebuilt).model_dump() == doc.model_dump()


def test_roundtrip_via_json_string():
    doc = CircuitGraphDoc.from_graph(_graph(CASCODE_FLAT))
    restored = CircuitGraphDoc.model_validate_json(doc.model_dump_json())
    assert CircuitGraphDoc.from_graph(restored.to_graph()).model_dump() == doc.model_dump()
