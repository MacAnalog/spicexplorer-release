"""P0 scaffold guards for spicexplorer-netlist2tf.

Invariants the whole tool depends on:
1. the package imports cleanly;
2. importing it does NOT drag in torch, lcapy, SLiCAP, or the circuitgraph peer (the leaf must
   stay light and behind the peer wall — doc/plan_netlist2tf.md §1);
3. it reaches core's NetlistView seam and nothing heavier.
"""

import subprocess
import sys
from pathlib import Path

_FIX = Path(__file__).resolve().parent / "fixtures"


def test_package_imports():
    import spicexplorer_netlist2tf  # noqa: F401
    from spicexplorer_netlist2tf import Circuit2TF, DeviceKind, NetRole

    assert Circuit2TF(name="empty").name == "empty"
    assert NetRole.SUPPLY_DC.value == "supply_dc"
    assert DeviceKind.NMOS.value == "nmos"


def test_import_stays_light_and_behind_the_wall():
    # Must run in a CLEAN interpreter: in the shared test process other packages (the optimizer)
    # have already imported torch, so inspecting this process's sys.modules would be meaningless.
    code = (
        "import sys, spicexplorer_netlist2tf\n"
        "forbidden = {'torch', 'lcapy', 'SLiCAP', 'slicap', 'spicexplorer_circuitgraph'}\n"
        "leaked = sorted(m for m in sys.modules if m.split('.')[0] in forbidden)\n"
        "assert not leaked, leaked\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"netlist2tf must stay light + peer-free, but imported: {proc.stderr.strip()}"
    )


def test_reaches_core_netlist_view():
    from spicexplorer_core.spice_engine import NetlistView

    dut = _FIX / "ota-improved.spice"
    view = NetlistView.from_file(dut)
    assert view.get_component_value("XM1") == "sg13_lv_nmos"
    # the new global-.param accessor this tool relies on
    assert isinstance(view.get_parameters(), dict)
