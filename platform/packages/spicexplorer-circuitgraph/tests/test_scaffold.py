"""Scaffold tests for spicexplorer-circuitgraph.

Guards two invariants the whole integration depends on:
1. the package imports cleanly, and
2. importing it does NOT drag in LangGraph/LangChain (the graph model must stay
   framework-free).
"""

import sys
from pathlib import Path

_FIX = Path(__file__).resolve().parent / "fixtures"


def test_package_imports():
    import spicexplorer_circuitgraph  # noqa: F401
    from spicexplorer_circuitgraph import CircuitGraphMeta

    meta = CircuitGraphMeta(circuit_name="ota_5t", component_count=13, net_count=12)
    assert meta.circuit_name == "ota_5t"
    assert meta.component_count == 13
    assert meta.net_count == 12


def test_import_does_not_pull_langgraph():
    # Import fresh and assert no LLM-orchestration framework leaked onto the path.
    import spicexplorer_circuitgraph  # noqa: F401

    leaked = [m for m in sys.modules if m.split(".")[0] in {"langgraph", "langchain"}]
    assert not leaked, f"circuitgraph must stay framework-free, but imported: {leaked}"


def test_reaches_core_netlist_view():
    # The leaf depends on core's NetlistView seam (and nothing heavier) — exercise it
    # against a real committed IHP fixture so the consumed contract is the real one.
    from spicexplorer_core.spice_engine import NetlistView

    dut = _FIX / "ota-improved.spice"
    view = NetlistView.from_file(dut)
    assert view.get_component_value("XM1") == "sg13_lv_nmos"
