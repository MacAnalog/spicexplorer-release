"""gm/ID operating-point extractor — offline, no Cadence.

Drives `backends.spectre.operating_point` over a `SpectreSimResult` built from a synthetic
`.info`-STRUCT dict (the `<inst>:<param>` keys the psfascii post-parse produces), asserting
the consumer-shape fields + derived gm/ID figures and the PDK-tolerant name handling.
"""

from __future__ import annotations

import math

import pytest
from spicexplorer.backends.spectre import (
    SpectreSimResult,
    operating_point,
    operating_points,
)


def _res(data: dict) -> SpectreSimResult:
    return SpectreSimResult(data)


def test_operating_point_fields_and_derived():
    data = {
        "XOTA.XM1:id": 20e-6, "XOTA.XM1:gm": 2.0e-4, "XOTA.XM1:gds": 1.0e-6,
        "XOTA.XM1:vgs": 0.6, "XOTA.XM1:vds": 0.5, "XOTA.XM1:vth": 0.4,
        "XOTA.XM1:cgg": 5e-15, "XOTA.XM1:region": 2.0,
    }
    op = operating_point(_res(data), "XOTA.XM1")
    assert op["gm"] == pytest.approx(2.0e-4)
    assert op["region"] == 2.0
    # derived gm/ID figures
    assert op["gm_id"] == pytest.approx(2.0e-4 / 20e-6)         # 10 1/V
    assert op["gm_gds"] == pytest.approx(2.0e-4 / 1.0e-6)       # 200 (intrinsic gain)
    assert op["ft"] == pytest.approx(2.0e-4 / (2 * math.pi * 5e-15))
    # a param the kit didn't emit is omitted (not a NaN entry)
    assert "vsb" not in op and "cgd" not in op


def test_operating_point_ids_current_fallback_and_sign():
    # kit spells drain current `ids`, and it is negative (PMOS) — efficiency uses |Id|
    data = {"XM5:ids": -40e-6, "XM5:gm": 4.0e-4}
    op = operating_point(_res(data), "XM5")
    assert op["gm_id"] == pytest.approx(4.0e-4 / 40e-6)


def test_operating_point_missing_gm_has_no_derived():
    op = operating_point(_res({"XM9:vds": 0.5}), "XM9")
    assert op == {"vds": 0.5}  # no gm → no gm_id/gm_gds/ft, no crash


def test_operating_points_multiple_instances():
    data = {
        "XM1:id": 10e-6, "XM1:gm": 1e-4,
        "XM2:id": 30e-6, "XM2:gm": 3e-4,
    }
    ops = operating_points(_res(data), ["XM1", "XM2"])
    assert set(ops) == {"XM1", "XM2"}
    assert ops["XM1"]["gm_id"] == pytest.approx(10.0)
    assert ops["XM2"]["gm_id"] == pytest.approx(10.0)
