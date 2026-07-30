"""Golden-value tests — pin the tool's output to the published P0 notebook results.

The values here are the exact numbers printed by the analog-db
`notebooks/gmid_sizing_demo.ipynb`, which runs the canonical flows on the SAME committed sky130
NMOS LUT used as this package's fixture. If these drift, either the notebook or the tool changed —
reconcile them deliberately (the notebook is the human-facing reference for the API). This is the
plan_gmid_sizing.md P3 gate: golden values vs the P0 notebook.
"""

import math

import pytest
from _gmid_fixtures import NCH
from spicexplorer_gmid import (
    OutOfGridError,
    size_capacitor,
    size_for_current_density,
    size_for_gm,
    size_resistor,
)


def test_golden_5step_flow():
    """gmid_sizing_demo §'canonical 5-step flow': fu=10 MHz into CL=2 pF, gm/ID=15, L=0.5, VDS=0.9."""
    fu, CL = 10e6, 2e-12
    gm = 2 * math.pi * fu * CL
    dev = size_for_gm(NCH, gm=gm, gm_id=15, L=0.5, vds=0.9)
    assert dev.W == pytest.approx(2.811, abs=0.005)  # notebook: W = 2.811 µm
    assert dev.op.vgs == pytest.approx(0.7106, abs=0.001)  # notebook VGS
    assert dev.op.av0 == pytest.approx(130.1, rel=0.01)  # notebook gm/gds
    assert dev.op.ft / fu == pytest.approx(236, abs=1)  # notebook fT/fu = 236
    assert dev.passed  # all three sanity gates pass in the notebook


def test_golden_jd_first_weak_inversion():
    """gmid_sizing_demo §'JD-first flow': JD=5e-8 A/µm at L=0.5, VDS=0.9 → gm/ID≈23.8, 1 µA → W=20 µm."""
    gm_id = NCH.gm_id_for_jd(5e-8, L=0.5, vds=0.9)
    assert gm_id == pytest.approx(23.8, abs=0.3)  # notebook interp gave 23.8 (pchip ~23.7)
    dev = size_for_current_density(NCH, ID=1e-6, jd=5e-8, L=0.5, vds=0.9)
    assert dev.W == pytest.approx(20.0, rel=1e-6)  # W = ID/JD = 1µA / 50 nA/µm
    assert dev.gm == pytest.approx(gm_id * 1e-6, rel=1e-9)


def test_jd_first_off_grid_rejected():
    # a current density far above the table's range must raise, not invert to garbage.
    with pytest.raises(OutOfGridError):
        NCH.gm_id_for_jd(1e-2, L=0.5, vds=0.9)


def test_golden_passives():
    """gmid_sizing_demo §'Passives': sky130 high-po sheet 355 Ω/□, MIM 2.07 fF/µm²."""
    r = size_resistor(10e3, sheet_res=355, w_um=1.0)
    assert r.squares == pytest.approx(28.2, abs=0.1)  # notebook: 28.2 squares
    assert r.l_um == pytest.approx(28.2, abs=0.1)  # L = 28.2 µm at W = 1 µm
    c = size_capacitor(1e-12, area_cap=2.07e-15)
    assert c.area_um2 == pytest.approx(483, abs=1)  # notebook: 483 µm²
