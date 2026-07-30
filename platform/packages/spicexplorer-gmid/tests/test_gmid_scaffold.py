"""P1 scaffold guards for spicexplorer-gmid.

Invariants the whole tool depends on:
1. the package imports cleanly and exposes its typed public API;
2. importing it does NOT drag in a peer tool (the optimizer, netlist2tf) or the data repo
   (spicexplorer_analog_db) or torch — the leaf must stay light and behind the peer wall;
3. it reaches pygmid (the LUT reader) and core.
"""

import subprocess
import sys


def test_package_imports():
    import spicexplorer_gmid  # noqa: F401
    from spicexplorer_gmid import DeviceTable, OperatingPoint, SizedDevice, size_for_gm

    assert callable(size_for_gm)
    assert hasattr(DeviceTable, "load")
    # contract is constructible (pure data)
    op = OperatingPoint(
        gm_id=15,
        L=0.5,
        vds=0.9,
        vsb=0.0,
        vgs=0.7,
        jd=3e-6,
        av0=130,
        ft=2e10,
        cgg_w=1e-15,
        cdd_w=5e-16,
    )
    dev = SizedDevice(W=10, L=0.5, ID=5e-5, gm=7.5e-4, cgg=1e-14, cdd=5e-15, op=op)
    assert dev.wf == 10  # nf defaults to 1
    assert dev.passed  # no gates → vacuously true


def test_import_stays_light_and_behind_the_wall():
    # Clean interpreter: in the shared test process other packages may already have imported torch.
    code = (
        "import sys, spicexplorer_gmid\n"
        "forbidden = {'torch', 'spicexplorer_netlist2tf', 'spicexplorer_circuitgraph',\n"
        "             'spicexplorer_analog_db'}\n"
        "leaked = sorted(m for m in sys.modules if m.split('.')[0] in forbidden)\n"
        "assert not leaked, leaked\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"gmid must stay light + peer-free, but imported: {proc.stderr.strip()}"
    )


def test_reaches_pygmid_reader():
    # the LUT reader is the one hard non-core dependency
    from pygmid import Lookup  # noqa: F401
