"""FingerWidthSet — finger-width interpolation + fail-loud bracketing."""

from __future__ import annotations

import pytest
from _gmid_fixtures import NCH  # committed fixture DeviceTable (sky130 nfet)
from spicexplorer_gmid import DeviceTable, FingerWidthSet, OutOfGridError


@pytest.fixture
def table() -> DeviceTable:
    return NCH


def test_single_width_set_returns_exact(table: DeviceTable):
    fs = FingerWidthSet({5.0: table})
    assert fs.finger_widths == [5.0]
    op = fs.at(15.0, 0.5, 0.9, 0.0, wf=5.0)
    ref = table.at(15.0, 0.5, 0.9, 0.0)
    assert op.vgs == pytest.approx(ref.vgs) and op.jd == pytest.approx(ref.jd)


def test_off_grid_finger_width_fails_loud(table: DeviceTable):
    fs = FingerWidthSet({5.0: table})
    with pytest.raises(OutOfGridError):
        fs.at(15.0, 0.5, 0.9, 0.0, wf=1.0)          # 1 µm not characterised → no extrapolation


def test_interpolation_is_convex_between_equal_tables(table: DeviceTable):
    # Same physical table registered at two finger widths → any interpolation weight must return the
    # identical operating point (a pure test of the interpolation arithmetic / bracketing).
    fs = FingerWidthSet({1.0: table, 5.0: table})
    assert fs.finger_widths == [1.0, 5.0]
    ref = table.at(12.0, 0.5, 0.9, 0.0)
    for wf in (1.0, 2.3, 3.7, 5.0):
        op = fs.at(12.0, 0.5, 0.9, 0.0, wf=wf)
        assert op.vgs == pytest.approx(ref.vgs, rel=1e-9)
        assert op.jd == pytest.approx(ref.jd, rel=1e-9)
        assert op.av0 == pytest.approx(ref.av0, rel=1e-9)


def test_exact_table_at_grid_point(table: DeviceTable):
    fs = FingerWidthSet({1.0: table, 5.0: table})
    assert fs.table_at(5.0) is table
    with pytest.raises(KeyError):
        fs.table_at(2.0)
