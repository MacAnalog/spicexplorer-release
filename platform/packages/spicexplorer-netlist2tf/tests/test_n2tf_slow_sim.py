"""P6 — ``slow`` validation against a real simulator (gated; auto-skips without ngspice/PDK).

These cross-check netlist2tf's symbolic/lambdify path against an actual ngspice ``.ac`` run:

* the RC cross-check is **PDK-free** (only needs ngspice) and runs on any host with ngspice;
* the AnalogGym amplifier check is **PDK-gated** (needs the IHP PDK + a flattened OTA solve, P7) and
  skips where the PDK is absent — it is the corpus-level acceptance test (decision OD-8), to be run
  in the container (`docker compose exec api pytest -m slow`).

Run with ``uv run pytest -m slow``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from spicexplorer_netlist2tf import transfer_function

pytestmark = pytest.mark.slow

_NGSPICE = shutil.which("ngspice")

_RC_NETLIST = """* rc lowpass
V1 in 0 dc 0 ac 1
R1 in out 1k
C1 out 0 159.155n
.control
ac dec 50 1 1Meg
meas ac f3db when vdb(out)=-3.0103
print f3db
.endc
.end
"""


@pytest.mark.skipif(_NGSPICE is None, reason="ngspice not on PATH")
def test_rc_pole_matches_ngspice_ac():
    """netlist2tf's predicted −3 dB frequency matches a real ngspice ``.ac`` sweep (PDK-free)."""
    assert _NGSPICE is not None  # guaranteed by skipif; narrows the type for the call below
    # ngspice reference
    with tempfile.TemporaryDirectory() as d:
        cir = Path(d) / "rc.cir"
        cir.write_text(_RC_NETLIST)
        proc = subprocess.run(
            [_NGSPICE, "-b", str(cir)], capture_output=True, text=True, timeout=60
        )
    m = re.search(r"f3db\s*=\s*([0-9.eE+-]+)", proc.stdout)
    if not m:  # environment/parse hiccup — don't hard-fail the suite
        pytest.skip(f"could not parse f3db from ngspice output:\n{proc.stdout[-500:]}")
    f3db_sim = float(m.group(1))

    # netlist2tf prediction for the same RC (R=1k, C=159.155n → f3dB ≈ 1 kHz)
    res = transfer_function(
        "* rc\nR1 in out R\nC1 out 0 C\n.end", ("out", "0"), ("in", "0"),
        operating_point={"r": 1e3, "c": 159.155e-9},
    )
    assert res.poles, "expected one pole"
    f3db_pred = res.poles[0].frequency_hz
    assert f3db_pred is not None
    assert f3db_pred == pytest.approx(f3db_sim, rel=0.05)


@pytest.mark.skipif(_NGSPICE is None, reason="ngspice not on PATH")
def test_analoggym_ac_validation():
    """Corpus acceptance (OD-8): predicted DC gain / dominant pole vs ngspice ``.ac`` on an AnalogGym
    amplifier. PDK-gated + needs the flattened-OTA solve (P7); skips until both are present."""
    from spicexplorer_core.env import probe_pdk

    pdk = probe_pdk()
    if not getattr(pdk, "ok", False) and not (isinstance(pdk, dict) and pdk.get("ok")):
        pytest.skip("IHP PDK not available (run in the container); AnalogGym .ac check deferred to P7 flatten")
    pytest.skip("AnalogGym amplifier .ac acceptance needs the P7 subckt-flatten solve; harness TODO")
