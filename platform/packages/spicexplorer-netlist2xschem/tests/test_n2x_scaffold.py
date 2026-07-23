"""Scaffold guards for spicexplorer-netlist2xschem.

Invariants the whole tool depends on:
1. the package imports cleanly and exposes its typed public API;
2. importing it does NOT drag in a peer tool (the optimizer, circuitgraph, netlist2tf, gmid) or the
   data repo (spicexplorer_analog_db) or torch — the leaf must stay light and behind the peer wall;
3. it reaches core (NetlistView).
"""

import subprocess
import sys


def test_package_imports():
    import spicexplorer_netlist2xschem as n2x  # noqa: F401
    from spicexplorer_netlist2xschem import (
        GridPlacer,
        N2XCircuit,
        SchDocument,
        SymLibrary,
        Transform,
        build_sch,
        from_string,
        render,
        to_sch,
    )

    assert callable(build_sch)
    assert callable(to_sch)
    assert callable(from_string)
    assert callable(render)
    assert hasattr(SymLibrary, "default")
    # contract types are constructible (pure data)
    assert Transform(0, 0).rot == 0
    doc = SchDocument(text="", warnings=(), device_count=0, label_count=0)
    assert doc.device_count == 0
    assert isinstance(GridPlacer(), GridPlacer)
    assert N2XCircuit("c", (), (), {}).name == "c"


def test_import_stays_light_and_behind_the_wall():
    # Clean interpreter: in the shared test process other packages may already have imported torch.
    code = (
        "import sys, spicexplorer_netlist2xschem\n"
        "forbidden = {'torch', 'spicexplorer', 'spicexplorer_circuitgraph',\n"
        "             'spicexplorer_netlist2tf', 'spicexplorer_gmid', 'spicexplorer_analog_db'}\n"
        "leaked = sorted(m for m in sys.modules if m.split('.')[0] in forbidden)\n"
        "assert not leaked, leaked\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"netlist2xschem must stay light + peer-free, but imported: {proc.stderr.strip()}"
    )


def test_reaches_core():
    from spicexplorer_core.spice_engine import NetlistView  # noqa: F401
