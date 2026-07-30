"""DeviceTable: axes/headers, the OperatingPoint view, sweeps, and the no-silent-clamp contract."""

import numpy as np
import pytest
from _gmid_fixtures import NCH
from spicexplorer_gmid import OutOfGridError


def test_axes_and_headers():
    assert NCH.L_grid.size == 8 and NCH.L_grid.min() == pytest.approx(0.15)
    assert NCH.VGS_grid.max() == pytest.approx(1.8)
    assert NCH.VDS_grid.size == 10
    assert NCH.VSB_grid.size == 2
    assert NCH.corner.upper() == "TT"
    assert "sky130" in NCH.info.lower()
    assert NCH.w_char == pytest.approx(5.0)


def test_at_operating_point():
    op = NCH.at(gm_id=15, L=0.5, vds=0.9)
    # physically-validated reference values for this committed LUT
    assert op.jd == pytest.approx(2.98e-6, rel=0.05)
    assert op.av0 == pytest.approx(130, rel=0.10)
    assert 0.6 < op.vgs < 0.8
    assert op.ft > 1e9  # finite, positive transit frequency
    assert op.cgg_w > 0 and op.cdd_w > 0


def test_sweep_trends_across_the_whole_grid():
    """Theme A of the test-suite review: assert *variation* across the swept axis, not slice 0.

    Textbook monotonic trends vs gm/ID (5→25): JD falls, fT falls, intrinsic gain rises.
    """
    sw = NCH.sweep(gm_id=(5, 25), L=0.5, vds=0.9, n=21)
    assert sw.gm_id.size == sw.jd.size == sw.ft.size == sw.av0.size == 21
    assert np.all(np.isfinite(sw.jd)) and np.all(np.isfinite(sw.ft))
    assert sw.jd[0] > sw.jd[-1]  # stronger inversion → higher current density
    assert sw.ft[0] > sw.ft[-1]  # stronger inversion → higher fT
    assert sw.av0[0] < sw.av0[-1]  # weaker inversion → higher intrinsic gain


def test_unreachable_gm_id_raises_not_garbage():
    # gm/ID = 80 is unreachable for this device. pygmid would return finite GARBAGE (negative caps,
    # a GV-range VGS) with only a printed warning — we must raise instead, never clamp/extrapolate.
    with pytest.raises(OutOfGridError) as exc:
        NCH.at(gm_id=80, L=0.5, vds=0.9)
    msg = str(exc.value)
    assert "unreachable" in msg and "VGS" in msg  # names the failure + the characterized envelope


def test_bias_axis_off_grid_raises():
    # VDS=5 V is outside the [0..1.8] V grid; pygmid silently extrapolates, so we guard up front.
    with pytest.raises(OutOfGridError) as exc:
        NCH.at(gm_id=15, L=0.5, vds=5.0)
    assert "VDS=5" in str(exc.value)


def test_look_up_passthrough():
    jd = NCH.look_up("ID_W", GM_ID=15, VDS=0.9, L=0.5, VSB=0.0)
    assert jd == pytest.approx(2.98e-6, rel=0.05)


# --- off-grid guard on look_up() and sweep() (cross_repo_audit: only at() guarded) --------------

def test_look_up_off_grid_bias_raises():
    """VDS=5 V is outside the [0..1.8] V grid. Before the fix pygmid extrapolated and look_up
    returned finite garbage; now the bias axis is gated up front like at()."""
    with pytest.raises(OutOfGridError) as exc:
        NCH.look_up("ID_W", GM_ID=15, VDS=5.0, L=0.5, VSB=0.0)
    assert "VDS=5" in str(exc.value)


def test_look_up_off_grid_L_raises():
    off_L = float(NCH.L_grid.max()) + 1.0  # 1 µm past the longest characterized channel
    with pytest.raises(OutOfGridError) as exc:
        NCH.look_up("ID_W", GM_ID=15, VDS=0.9, L=off_L, VSB=0.0)
    assert "L=" in str(exc.value)


def test_look_up_on_grid_value_unchanged():
    """On-grid lookups must return exactly what they did before the guard was added."""
    assert NCH.look_up("ID_W", GM_ID=15, VDS=0.9, L=0.5, VSB=0.0) == pytest.approx(2.98e-6, rel=0.05)


def test_sweep_off_grid_bias_raises():
    with pytest.raises(OutOfGridError) as exc:
        NCH.sweep(gm_id=(5, 25), L=0.5, vds=5.0, n=21)
    assert "VDS=5" in str(exc.value)


def test_sweep_on_grid_unchanged():
    """An on-grid sweep still produces the same finite trade-off arrays (guard is transparent)."""
    sw = NCH.sweep(gm_id=(5, 25), L=0.5, vds=0.9, n=21)
    assert sw.jd.size == 21
    assert np.all(np.isfinite(sw.jd)) and np.all(np.isfinite(sw.ft))
    assert sw.jd[0] > sw.jd[-1] and sw.av0[0] < sw.av0[-1]
