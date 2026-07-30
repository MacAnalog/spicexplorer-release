"""Passive sizing from PDK sheet-resistance / area-capacitance constants (closed-form)."""

import pytest
from spicexplorer_gmid import GmidError, size_capacitor, size_resistor


def test_size_resistor():
    r = size_resistor(10_000, sheet_res=355, w_um=1.0)  # sky130 p-poly-ish
    assert r.kind == "resistor"
    assert r.squares == pytest.approx(10_000 / 355)
    assert r.l_um == pytest.approx(10_000 / 355)  # L = squares · w_um, w_um = 1.0 µm
    assert r.value == pytest.approx(10_000, rel=1e-9)


def test_size_capacitor():
    c = size_capacitor(2e-12, area_cap=2.07e-15)  # F/µm² (MIM-ish)
    assert c.kind == "capacitor"
    assert c.area_um2 == pytest.approx(2e-12 / 2.07e-15)
    assert c.value == pytest.approx(2e-12, rel=1e-9)


def test_invalid_inputs_raise():
    with pytest.raises(GmidError):
        size_resistor(-1, sheet_res=355)
    with pytest.raises(GmidError):
        size_capacitor(1e-12, area_cap=0)
