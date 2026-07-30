"""Sizing flows: gm-first vs current-first equivalence, the de-normalization, and sanity gates."""

import math

import pytest
from _gmid_fixtures import NCH
from spicexplorer_gmid import (
    GeometryBounds,
    size_for_current_density,
    size_for_gm,
)


def test_size_for_gm_denormalizes_correctly():
    gm, gm_id, L, vds = 1e-3, 15.0, 0.5, 0.9
    dev = size_for_gm(NCH, gm=gm, gm_id=gm_id, L=L, vds=vds)
    # ID = gm / (gm/ID); W = ID / JD
    assert dev.ID == pytest.approx(gm / gm_id)
    assert dev.gm == pytest.approx(gm)
    assert dev.W == pytest.approx(dev.ID / dev.op.jd)
    assert dev.W == pytest.approx(22.4, rel=0.08)  # ≈ ID/jd for this LUT
    assert dev.cgg == pytest.approx(dev.op.cgg_w * dev.W)
    assert dev.passed  # VDS=0.9 V clears V_Dsat≈0.13 V; gain/fT finite


def test_gm_first_and_current_first_agree():
    """The two flows are the same lookup from opposite ends → identical W at the same op."""
    gm_id, L, vds = 12.0, 1.0, 0.9
    by_gm = size_for_gm(NCH, gm=2e-3, gm_id=gm_id, L=L, vds=vds)
    by_id = size_for_current_density(NCH, ID=by_gm.ID, gm_id=gm_id, L=L, vds=vds)
    assert by_id.W == pytest.approx(by_gm.W, rel=1e-9)
    assert by_id.gm == pytest.approx(by_gm.gm, rel=1e-9)


def test_saturation_gate_fails_in_triode():
    # VDS below V_Dsat≈2/(gm/ID): at gm/ID=5, V_Dsat≈0.4 V; drive VDS=0.2 V → saturation gate fails.
    dev = size_for_gm(NCH, gm=1e-3, gm_id=5, L=0.5, vds=0.2)
    sat = next(g for g in dev.gates if g.name == "saturation")
    assert not sat.ok
    assert not dev.passed


def test_geometry_bounds_gate():
    bounds = GeometryBounds(w_min=0.42, w_max=1.0, l_min=0.15)
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, bounds=bounds)  # W≈22 µm ≫ w_max
    gw = next(g for g in dev.gates if g.name == "geometry_w")
    assert not gw.ok  # single finger (nf=1): per-finger W = total W = 22 µm > 1 µm
    assert not dev.passed


def test_geometry_gate_is_per_finger():
    # The w_max bound is PER FINGER: the same wide device passes once it fingers below w_max.
    bounds = GeometryBounds(w_min=0.42, w_max=10.0)
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, bounds=bounds, wf_max=10.0)
    gw = next(g for g in dev.gates if g.name == "geometry_w")
    assert (
        dev.W > 10.0 and dev.nf >= 2 and dev.wf <= 10.0
    )  # total W exceeds w_max, per-finger does not
    assert gw.ok and dev.passed


def test_fingering():
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=5.0)
    assert dev.nf == math.ceil(dev.W / 5.0)
    assert dev.wf <= 5.0
