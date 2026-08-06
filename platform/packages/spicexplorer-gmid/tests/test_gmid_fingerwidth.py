"""FingerWidthSet — finger-width interpolation + fail-loud bracketing.

The interpolation tests run against **two genuinely different tables**: the committed sky130 fixture
at 5 µm and a perturbed derivative at 1 µm (``_gmid_fixtures.perturbed_lut``). Registering the same
table at both widths — which is what these tests used to do — makes the arithmetic unobservable:
every operating point is then the fixed point of the interpolation, so an inverted bracket weight
and a ``_lerp`` that ignores the hi table both leave the file green.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _gmid_fixtures import NCH, perturbed_lut  # committed fixture DeviceTable (sky130 nfet)
from spicexplorer_gmid import DeviceTable, FingerWidthSet, OperatingPoint, OutOfGridError

# The bias slice every interpolation test reads (reachable on BOTH tables: the perturbed copy's
# gm/ID band is ~0.78× the fixture's, so 12 1/V stays well under either peak).
GM_ID, L, VDS, VSB = 12.0, 0.5, 0.9, 0.0

_LERPED = ("vgs", "jd", "av0", "ft", "cgg_w", "cdd_w")


@pytest.fixture
def table() -> DeviceTable:
    return NCH


@pytest.fixture(scope="module")
def narrow(tmp_path_factory: pytest.TempPathFactory) -> DeviceTable:
    """A 1 µm-finger companion: same grids, different electricals (ID/GM/GDS/CGG/CDD all moved)."""
    dest: Path = tmp_path_factory.mktemp("gmid_wf") / "sky130_fd_pr__nfet_01v8__tt__wf1u.pkl"
    return perturbed_lut(
        dest,
        scale={"ID": 1.6, "GM": 1.25, "GDS": 0.9, "CGG": 1.1, "CDD": 1.2},
        headers={"W": 1.0},
    )


def _lerp(a: float, b: float, w: float) -> float:
    return a * (1.0 - w) + b * w


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


def test_the_two_tables_really_differ(table: DeviceTable, narrow: DeviceTable):
    """Guard on the guard: if the companion ever collapses onto the fixture, the tests below go blind."""
    lo_op, hi_op = narrow.at(GM_ID, L, VDS, VSB), table.at(GM_ID, L, VDS, VSB)
    for field in _LERPED:
        assert getattr(lo_op, field) != pytest.approx(getattr(hi_op, field), rel=1e-3, abs=0.0), field


def test_grid_point_returns_that_tables_operating_point(table: DeviceTable, narrow: DeviceTable):
    """wf ON the finger-width grid must be the exact table there — no blend with its neighbour."""
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    assert fs.finger_widths == [1.0, 5.0]
    for wf, ref in ((1.0, narrow), (5.0, table)):
        op = fs.at(GM_ID, L, VDS, VSB, wf=wf)
        expected = ref.at(GM_ID, L, VDS, VSB)
        for field in _LERPED:
            assert getattr(op, field) == pytest.approx(getattr(expected, field), rel=1e-12, abs=0.0), field


@pytest.mark.parametrize("wf", [1.5, 2.0, 3.0, 4.6])
def test_interpolation_is_the_bracket_weighted_blend(table: DeviceTable, narrow: DeviceTable, wf: float):
    """Every interpolated field is lo·(1−w) + hi·w with w = (wf − 1)/(5 − 1) — the exact arithmetic.

    This is what pins the direction of the weight: at wf=1.5 the answer must sit next to the 1 µm
    table, not the 5 µm one.
    """
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    lo_op, hi_op = narrow.at(GM_ID, L, VDS, VSB), table.at(GM_ID, L, VDS, VSB)
    w = (wf - 1.0) / (5.0 - 1.0)
    op: OperatingPoint = fs.at(GM_ID, L, VDS, VSB, wf=wf)
    for field in _LERPED:
        assert getattr(op, field) == pytest.approx(
            _lerp(getattr(lo_op, field), getattr(hi_op, field), w), rel=1e-12, abs=0.0
        ), field
    # …and it is a strict blend: never outside the two endpoints it interpolates.
    span = sorted((lo_op.jd, hi_op.jd))
    assert span[0] < op.jd < span[1]


def test_interpolation_moves_monotonically_with_finger_width(table: DeviceTable, narrow: DeviceTable):
    """Walking wf from 1 → 5 µm must walk jd monotonically from the 1 µm value to the 5 µm one."""
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    jds = [fs.at(GM_ID, L, VDS, VSB, wf=wf).jd for wf in (1.0, 2.0, 3.0, 4.0, 5.0)]
    assert jds == sorted(jds) or jds == sorted(jds, reverse=True)
    assert jds[0] == pytest.approx(narrow.at(GM_ID, L, VDS, VSB).jd, rel=1e-12)
    assert jds[-1] == pytest.approx(table.at(GM_ID, L, VDS, VSB).jd, rel=1e-12)


def test_gm_id_for_jd_interpolates_across_finger_width(table: DeviceTable, narrow: DeviceTable):
    """The JD→gm/ID inversion is done per table, then blended (JD is per-finger-width).

    ``jd=3e-7`` because the blend now has to honour the same 5 % round-trip contract the per-table
    inversion does, and this pair of tables blends consistently there (0.404 % off) — see
    ``test_gm_id_for_jd_blend_that_misses_its_own_round_trip_raises`` for the other side.
    """
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    jd = 3e-7
    lo, hi = narrow.gm_id_for_jd(jd, L, VDS, VSB), table.gm_id_for_jd(jd, L, VDS, VSB)
    assert lo != pytest.approx(hi, rel=1e-3)          # the two tables disagree, as they must
    assert fs.gm_id_for_jd(jd, L, VDS, VSB, wf=1.0) == pytest.approx(lo, rel=1e-12)
    assert fs.gm_id_for_jd(jd, L, VDS, VSB, wf=5.0) == pytest.approx(hi, rel=1e-12)
    assert fs.gm_id_for_jd(jd, L, VDS, VSB, wf=2.0) == pytest.approx(_lerp(lo, hi, 0.25), rel=1e-12)


# --- the endpoint weights fast-path: an EXACT characterised width never evaluates its partner -----


def test_at_at_an_exact_upper_width_does_not_evaluate_the_zero_weight_table(
    table: DeviceTable, narrow: DeviceTable
):
    """``_bracket(5.0)`` is ``(1.0, 5.0, w=1.0)`` — the 1 µm table contributes nothing but its gates.

    Only ``w == 0.0`` was fast-pathed, so requesting an exactly-characterised width still evaluated
    the *other* bracket endpoint at weight zero: every contribution multiplied out, but its
    reachability gate live. A target inside the 5 µm table's band and above the 1 µm table's peak
    therefore raised, naming the 1 µm table's band — the same object contradicting ``table_at``.
    Reproduced on the real production {0.5, 1.0, 5.0} µm sky130 store; here the perturbed companion
    reproduces it exactly (bands ~21.11 vs ~27.03 1/V at this slice).
    """
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    assert fs._bracket(5.0) == (1.0, 5.0, 1.0)
    lo_band, hi_band = narrow.gm_id_band(L, VDS)[1], table.gm_id_band(L, VDS)[1]
    target = hi_band - 0.01
    assert target > lo_band                      # reachable ONLY in the upper table
    op = fs.at(target, L, VDS, VSB, wf=5.0)
    ref = table.at(target, L, VDS, VSB)
    for field in _LERPED:
        assert getattr(op, field) == pytest.approx(getattr(ref, field), rel=1e-12, abs=0.0), field


def test_gm_id_for_jd_at_an_exact_upper_width_does_not_consult_the_zero_weight_table(
    table: DeviceTable, narrow: DeviceTable, monkeypatch: pytest.MonkeyPatch
):
    """Same hole in the ``gm_id_for_jd`` twin this commit added — pinned by making the lower table
    explode if it is touched at all."""
    fs = FingerWidthSet({1.0: narrow, 5.0: table})

    def boom(*_args: object, **_kwargs: object) -> float:
        raise OutOfGridError("the 1 µm table must not be inverted at wf=5 µm")

    monkeypatch.setattr(narrow, "gm_id_for_jd", boom)
    assert fs.gm_id_for_jd(2e-6, L, VDS, VSB, wf=5.0) == pytest.approx(
        table.gm_id_for_jd(2e-6, L, VDS, VSB), rel=1e-12
    )


# --- the blend keeps the package's own 5 % JD round-trip contract ---------------------------------


def test_gm_id_for_jd_blend_that_misses_its_own_round_trip_raises(
    table: DeviceTable, narrow: DeviceTable
):
    """Two individually-consistent inversions do not lerp into a consistent one.

    ``DeviceTable.gm_id_for_jd`` refuses an inversion whose round trip misses by >5 %; the set's
    twin lerped two of those and never re-checked. JD runs exponentially in gm/ID through weak
    inversion, so the straight line cuts the corner: at ``jd=2e-6 A/µm, wf=2.0 µm`` the blended
    gm/ID reads back 2.14326e-06 A/µm — 7.16 % off the request, while ``_assemble`` sizes
    ``W = ID/jd`` from the REQUESTED density. Measured 7.59 % worst case on the real production
    {0.5, 1.0, 5.0} µm sky130 store, so this is not an artifact of the perturbed fixture.
    """
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    # Both endpoints invert consistently on their own …
    assert narrow.gm_id_for_jd(2e-6, L, VDS, VSB) > 0
    assert table.gm_id_for_jd(2e-6, L, VDS, VSB) > 0
    # … and the interior blend of them does not.
    with pytest.raises(OutOfGridError) as exc:
        fs.gm_id_for_jd(2e-6, L, VDS, VSB, wf=2.0)
    msg = str(exc.value)
    assert "does not invert consistently" in msg
    assert "2.14326e-06" in msg          # names the JD the blended gm/ID actually reads back
    assert "tolerance 5 %" in msg


@pytest.mark.parametrize("wf", [1.0, 1.2, 2.0, 5.0])
def test_an_accepted_jd_inversion_round_trips_within_five_percent(
    table: DeviceTable, narrow: DeviceTable, wf: float
):
    """The positive control: whatever the set DOES return must satisfy the contract it enforces."""
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    jd = 3e-7
    gm_id = fs.gm_id_for_jd(jd, L, VDS, VSB, wf=wf)
    assert fs.at(gm_id, L, VDS, VSB, wf=wf).jd == pytest.approx(jd, rel=0.05)


def test_exact_table_at_grid_point(table: DeviceTable, narrow: DeviceTable):
    fs = FingerWidthSet({1.0: narrow, 5.0: table})
    assert fs.table_at(5.0) is table
    assert fs.table_at(1.0) is narrow
    with pytest.raises(KeyError):
        fs.table_at(2.0)
