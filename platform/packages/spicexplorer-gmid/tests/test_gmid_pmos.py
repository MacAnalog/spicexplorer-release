"""PMOS coverage: the |ID| and VSB-magnitude conventions through at / gm_id_band / sweep / sizing.

The analog-db extractor writes a pmos LUT in the Murmann/pygmid magnitude convention — every bias
axis and ``ID`` stored positive, so one sizing flow serves both polarities — and this package's
guards (``JD > 0``, a strictly positive gm/ID band, the bias-grid bounds) all depend on it. The
committed fixtures are NMOS only, so no pmos table had ever gone through them.

These run two synthetic tables (``_gmid_fixtures.synthetic_pmos_lut``, no kit data): one shaped like
the sky130 pfet (gm/ID peaks at the VGS=0 grid edge) and one like the IHP lv pmos (interior peak).
Then the convention is broken the ways an extractor could break it, and each break must be caught —
by the tool where the break is detectable (a signed ID, a signed VSB axis), and by the physics
assertions here where it is not (the VSB slices mislabelled in order).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest
from _gmid_fixtures import IHP_PCH, PCH, ihp_pmos_like, sky130_pfet_like
from spicexplorer_gmid import DeviceTable, OutOfGridError, size_for_current_density, size_for_gm

# name -> (table, fresh-dict builder, L [µm], VDS [V]): one saturated slice inside each grid.
CASES: dict[str, tuple[DeviceTable, Callable[[], dict[str, object]], float, float]] = {
    "sky130-pfet": (PCH, sky130_pfet_like, 0.5, 0.9),
    "ihp-pmos": (IHP_PCH, ihp_pmos_like, 0.13, 0.75),
}
NAMES = list(CASES)
_STORED = ("ID", "GM", "GDS", "CGG", "CDD")  # the 4-D arrays, indexed (L, VGS, VDS, VSB)


def _mutated(name: str, mutate: Callable[[dict[str, object]], None]) -> DeviceTable:
    data = CASES[name][1]()
    mutate(data)
    return DeviceTable.from_lut_dict(data)


def _signed_id(data: dict[str, object]) -> None:
    """The raw simulator sign for a pmos: drain current negative."""
    data["ID"] = -np.asarray(data["ID"])


def _signed_id_and_gm(data: dict[str, object]) -> None:
    data["ID"] = -np.asarray(data["ID"])
    data["GM"] = -np.asarray(data["GM"])


def _signed_vsb_axis(data: dict[str, object]) -> None:
    """VSB stored as the raw bulk sweep ([-0.4..0] V), the data re-ordered so it still matches."""
    data["VSB"] = -np.asarray(data["VSB"])[::-1]
    for key in _STORED:
        data[key] = np.asarray(data[key])[..., ::-1]


def _vsb_slices_reversed(data: dict[str, object]) -> None:
    """The axis reads |VSB| ascending but the slices run the other way (a sort on the signed sweep)."""
    for key in _STORED:
        data[key] = np.asarray(data[key])[..., ::-1]


# ----- the convention, held -------------------------------------------------------------------


@pytest.mark.parametrize("name", NAMES)
def test_the_synthetic_tables_store_magnitudes(name):
    """Checks the fixture: if it drifted off the convention, the other tests would miss a break."""
    table = CASES[name][0]
    for grid in (table.L_grid, table.VGS_grid, table.VDS_grid, table.VSB_grid):
        assert float(grid.min()) >= 0.0
    assert float(np.min(table.lut["ID"])) >= 0.0 and float(np.max(table.lut["ID"])) > 0.0


@pytest.mark.parametrize("name", NAMES)
def test_pmos_gm_id_band_is_a_positive_interval_where_the_shape_puts_its_peak(name):
    table, _, L, vds = CASES[name]
    for vsb in table.VSB_grid:
        lo, hi, vgs_peak = table.gm_id_band(L, vds, float(vsb))
        assert 0.0 < lo < hi
        if name == "sky130-pfet":
            assert vgs_peak == 0.0  # the edge peak
        else:
            assert table.VGS_grid.min() < vgs_peak < table.VGS_grid.max()  # the interior one
    lo, hi, _ = table.gm_id_band(L, vds)
    # A closed interval: both ends size, one step past the peak does not — on every entry point.
    assert table.at(lo, L, vds).jd > 0 and table.at(hi, L, vds).jd > 0
    with pytest.raises(OutOfGridError, match="unreachable"):
        table.at(hi * 1.01, L, vds)
    with pytest.raises(OutOfGridError, match="unreachable"):
        table.look_up("ID_W", GM_ID=hi * 1.01, L=L, VDS=vds, VSB=0.0)


@pytest.mark.parametrize("name", NAMES)
def test_pmos_at_reads_positive_magnitudes_with_the_nmos_trends(name):
    """|ID| convention: JD, |VGS|, gain, fT and the cap densities all come back positive, and a
    stronger inversion level means a larger |VGS|, JD and fT — exactly the NMOS trends."""
    table, _, L, vds = CASES[name]
    strong, weak = table.at(8.0, L, vds), table.at(16.0, L, vds)
    for op in (strong, weak):
        assert op.jd > 0 and op.av0 > 0 and op.ft > 0 and op.cgg_w > 0 and op.cdd_w > 0
        assert 0.0 < op.vgs <= float(table.VGS_grid.max())
    assert strong.vgs > weak.vgs and strong.jd > weak.jd and strong.ft > weak.ft


@pytest.mark.parametrize("name", NAMES)
def test_pmos_vsb_is_a_magnitude_and_the_body_effect_raises_vgs(name):
    """VSB is addressed by its magnitude, and a larger |VSB| raises |VT| — for either polarity.

    The signed bulk bias a pmos testbench applies (VSB=-0.2 V) is not a stored coordinate, and is
    refused rather than extrapolated.
    """
    table, _, L, vds = CASES[name]
    vgs = [table.at(12.0, L, vds, vsb).vgs for vsb in (0.0, 0.2, 0.4)]
    assert vgs[0] < vgs[1] < vgs[2]
    with pytest.raises(OutOfGridError, match="VSB=-0.2"):
        table.at(12.0, L, vds, -0.2)


@pytest.mark.parametrize("name", NAMES)
def test_pmos_sweep_across_the_whole_band_and_one_step_past_it(name):
    table, _, L, vds = CASES[name]
    lo, hi, _ = table.gm_id_band(L, vds, 0.2)
    sw = table.sweep(gm_id=(lo, hi), L=L, vds=vds, vsb=0.2, n=11)
    assert np.all(sw.jd > 0) and np.all(np.diff(sw.jd) < 0)  # JD falls towards weak inversion
    assert np.all(np.diff(sw.vgs) < 0)  # …and so does |VGS|
    assert np.all(sw.vgs >= table.VGS_grid.min()) and np.all(sw.vgs <= table.VGS_grid.max())
    with pytest.raises(OutOfGridError, match="unreachable"):
        table.sweep(gm_id=(lo, hi * 1.01), L=L, vds=vds, vsb=0.2, n=11)


@pytest.mark.parametrize("name", NAMES)
def test_pmos_size_for_gm_and_its_jd_first_twin(name):
    table, _, L, vds = CASES[name]
    gm = 1e-4
    dev = size_for_gm(table, gm=gm, gm_id=12.0, L=L, vds=vds, vsb=0.2)
    assert dev.ID == pytest.approx(gm / 12.0, rel=1e-12) and dev.ID > 0
    assert dev.W == pytest.approx(dev.ID / dev.op.jd, rel=1e-12) and dev.W > 0
    assert dev.passed
    # The JD-first flow inverts the same density back to the same inversion level and width.
    twin = size_for_current_density(table, ID=dev.ID, jd=dev.op.jd, L=L, vds=vds, vsb=0.2)
    assert twin.op.gm_id == pytest.approx(12.0, rel=0.02)
    assert twin.W == pytest.approx(dev.W, rel=1e-12)


# ----- the convention, broken -----------------------------------------------------------------


@pytest.mark.parametrize("mutate", [_signed_id, _signed_id_and_gm], ids=["ID", "ID+GM"])
@pytest.mark.parametrize("name", NAMES)
def test_a_signed_pmos_drain_current_is_refused_not_sized(name, mutate):
    """A table carrying the simulator's signed pmos current never sizes a device.

    Every entry point gates on a positive current locus, so a negative ``ID`` (whether or not
    ``GM`` came along) raises — no negative width, no sign-flipped gm/ID band.
    """
    table = _mutated(name, mutate)
    _, _, L, vds = CASES[name]
    with pytest.raises(OutOfGridError):
        table.gm_id_band(L, vds)
    with pytest.raises(OutOfGridError):
        table.at(12.0, L, vds)
    with pytest.raises(OutOfGridError):
        table.sweep(gm_id=(5.0, 20.0), L=L, vds=vds)
    with pytest.raises(OutOfGridError):
        size_for_gm(table, gm=1e-4, gm_id=12.0, L=L, vds=vds)


@pytest.mark.parametrize("name", NAMES)
def test_a_signed_vsb_axis_is_not_read_as_a_magnitude(name):
    """Stored as the raw bulk sweep, |VSB|=0.2 V is off that grid — raised, not mirrored."""
    table = _mutated(name, _signed_vsb_axis)
    _, _, L, vds = CASES[name]
    with pytest.raises(OutOfGridError, match="VSB=0.2 is outside the characterized grid"):
        table.at(12.0, L, vds, 0.2)
    with pytest.raises(OutOfGridError, match="VSB=0.2 is outside the characterized grid"):
        table.gm_id_band(L, vds, 0.2)


@pytest.mark.parametrize("name", NAMES)
def test_mislabelled_vsb_slices_reverse_the_body_effect(name):
    """The break the tool cannot see: every value is plausible, only the labels are wrong.

    This is what the extractor's ``np.abs`` before its sort prevents. The body-effect ordering
    asserted in ``test_pmos_vsb_is_a_magnitude_and_the_body_effect_raises_vgs`` flips, so that test
    is the one that catches it.
    """
    table = _mutated(name, _vsb_slices_reversed)
    _, _, L, vds = CASES[name]
    vgs = [table.at(12.0, L, vds, vsb).vgs for vsb in (0.0, 0.2, 0.4)]
    assert vgs[0] > vgs[1] > vgs[2]
