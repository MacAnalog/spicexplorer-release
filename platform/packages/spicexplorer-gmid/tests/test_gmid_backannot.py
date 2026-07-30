"""P4 — ngspice .op back-annotation: gm/ID tool predictions agree with SPICE within tolerance.

Slow (PDK + ngspice gated).  Auto-skips when ngspice is absent or the IHP PDK corner lib is
not found at the expected container path.  Runs natively inside the api container (native
ngspice + PDK) via ``pytest -m slow``.

LUT used: committed IHP sg13_lv_nmos @ tt (``tests/fixtures/``, copied from analog-db).
PDK used: IHP sg13g2 PSP/OSDI (``cornerMOSlv.lib mos_tt``), available in the spice-base image.
Why IHP: PSP devices use ``.op`` analysis and emit ``ids``/``gm`` directly — no ``.noise``
wrdata complication (unlike sky130 BSIM4).

Tolerance reference: gmid-skills ``verification.md`` table — 10% agreement is the acceptance
gate for a table-predicted VGS verified against a real .op simulation.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from spicexplorer_gmid import DeviceTable

FIXTURES = Path(__file__).resolve().parent / "fixtures"
IHP_NCH_PKL = FIXTURES / "sg13_lv_nmos__tt.pkl"

_IHP_PDK_LIB = Path("/opt/pdk/ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib")
_TOLERANCE = 0.10  # 10 % — the acceptance gate from gmid-skills/verification.md

pytestmark = pytest.mark.slow

# ── helpers ───────────────────────────────────────────────────────────────────────────────────────


def _ngspice_available() -> bool:
    return shutil.which("ngspice") is not None


def _ihp_pdk_available() -> bool:
    return _IHP_PDK_LIB.is_file()


def _run_op_deck(deck: str) -> dict[str, float]:
    """Write ``deck`` to a temp dir, run ngspice -b, parse ``key = value`` lines from stdout."""
    with tempfile.TemporaryDirectory() as d:
        sp = Path(d) / "check.sp"
        sp.write_text(deck)
        result = subprocess.run(
            [shutil.which("ngspice"), "-b", str(sp)],  # type: ignore[arg-type]
            capture_output=True, text=True, timeout=120, cwd=d,
        )
        vals: dict[str, float] = {}
        for line in result.stdout.splitlines():
            m = re.match(r"\s*(\S+)\s*=\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*$", line)
            if m:
                vals[m.group(1).lower()] = float(m.group(2))
        return vals


# ── tests ─────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("gm_id_target,L,vds", [
    (15.0, 0.5, 0.9),   # moderate inversion — the P3 golden point scaled to IHP VDD=1.5V
    (10.0, 1.0, 0.9),   # stronger inversion (higher Av0, lower fT)
])
def test_gm_id_agrees_with_spice(gm_id_target: float, L: float, vds: float) -> None:
    """gm/ID predicted by the table agrees with an ngspice .op simulation to within TOLERANCE.

    Protocol:
      1. Load the committed IHP nmos LUT from fixtures.
      2. Call DeviceTable.at() to resolve VGS for the (gm/ID, L, VDS) target.
      3. Build an IHP sg13_lv_nmos .op deck biased at (VGS, VDS) at the characterisation width.
      4. Run ngspice natively, parse gm and ids from stdout.
      5. Assert |gm_id_spice − target| / target < TOLERANCE.
    """
    if not _ngspice_available():
        pytest.skip("ngspice not in PATH")
    if not _ihp_pdk_available():
        pytest.skip(f"IHP PDK not found at {_IHP_PDK_LIB.parent} — run in the api container")

    nch = DeviceTable.load(IHP_NCH_PKL)
    op = nch.at(gm_id=gm_id_target, L=L, vds=vds)

    W_um = nch.w_char  # at the characterisation width: LUT is exact (no width de-normalisation)

    # IHP sg13_lv_nmos port order: source(0) gate(g) drain(d) bulk(b)
    # Probe path: @n.xm1.nsg13_lv_nmos[ids] / @n.xm1.nsg13_lv_nmos[gm]
    deck = (
        f"* IHP sg13 nmos .op back-annotation"
        f" gm_id={gm_id_target} L={L}u VDS={vds} V (W={W_um}um)\n"
        f"vg g 0 DC {op.vgs:.6f}\n"
        f"vd d 0 DC {vds:.6f}\n"
        f"vb b 0 0\n"
        f"XM1 0 g d b sg13_lv_nmos L={L}u W={W_um}u ng=1 m=1\n"
        f".save @n.xm1.nsg13_lv_nmos[gm]\n"
        f".save @n.xm1.nsg13_lv_nmos[ids]\n"
        f".control\n"
        f"option numdgt=7\n"
        f"op\n"
        f"print @n.xm1.nsg13_lv_nmos[gm] @n.xm1.nsg13_lv_nmos[ids]\n"
        f"quit\n"
        f".endc\n"
        f".options TEMP=26.85 TNOM=27\n"
        f".lib cornerMOSlv.lib mos_tt\n"
        f".end\n"
    )
    vals = _run_op_deck(deck)

    gm_key = "@n.xm1.nsg13_lv_nmos[gm]"
    id_key = "@n.xm1.nsg13_lv_nmos[ids]"
    if gm_key not in vals or id_key not in vals:
        pytest.fail(
            f"Could not parse gm/ids from ngspice stdout. Keys found: {sorted(vals)}.\n"
            f"Deck used:\n{deck}"
        )

    gm_spice = vals[gm_key]
    id_spice = vals[id_key]
    gm_id_spice = gm_spice / id_spice

    err = abs(gm_id_spice - gm_id_target) / gm_id_target
    assert err < _TOLERANCE, (
        f"gm/ID mismatch: LUT={gm_id_target:.1f} 1/V, SPICE={gm_id_spice:.2f} 1/V "
        f"({err * 100:.1f}% > {_TOLERANCE * 100:.0f}% tolerance). "
        f"VGS from LUT: {op.vgs:.4f} V, W={W_um:.1f}um, L={L}um, VDS={vds}V."
    )
