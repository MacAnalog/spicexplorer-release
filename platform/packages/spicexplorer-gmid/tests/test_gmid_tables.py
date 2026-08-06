"""DeviceTable: axes/headers, the OperatingPoint view, sweeps, and the no-silent-clamp contract."""

import numpy as np
import pytest
from _gmid_fixtures import IHP_NCH, NCH
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

    Textbook monotonic trends vs gm/ID (5→25): JD falls, fT falls, intrinsic gain rises. The
    swept range is widened to the top of the reachable band (L=0.5/VDS=0.9 peaks at 27.027 1/V)
    so the trends are pinned right up against the reachability edge, and one step past it must
    raise rather than extend the curves with extrapolated garbage.
    """
    sw = NCH.sweep(gm_id=(5, 27), L=0.5, vds=0.9, n=21)
    assert sw.gm_id.size == sw.jd.size == sw.ft.size == sw.av0.size == 21
    assert np.all(np.isfinite(sw.jd)) and np.all(np.isfinite(sw.ft))
    assert np.all(sw.jd > 0)
    assert sw.jd[0] > sw.jd[-1]  # stronger inversion → higher current density
    assert sw.ft[0] > sw.ft[-1]  # stronger inversion → higher fT
    assert sw.av0[0] < sw.av0[-1]  # weaker inversion → higher intrinsic gain
    # One notch past the reachable maximum: pygmid pchip-extrapolates, so this used to return
    # finite garbage (a rising JD tail, a VGS tail in the kilovolts) instead of raising.
    with pytest.raises(OutOfGridError):
        NCH.sweep(gm_id=(5, 28), L=0.5, vds=0.9, n=21)


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
    """An on-grid, in-band sweep still produces the same finite trade-off arrays (guard is
    transparent) — and one widened past the reachable maximum raises instead of extrapolating."""
    sw = NCH.sweep(gm_id=(5, 27), L=0.5, vds=0.9, n=21)
    assert sw.jd.size == 21
    assert np.all(np.isfinite(sw.jd)) and np.all(np.isfinite(sw.ft))
    assert np.all(sw.vgs >= NCH.VGS_grid.min()) and np.all(sw.vgs <= NCH.VGS_grid.max())
    assert sw.jd[0] > sw.jd[-1] and sw.av0[0] < sw.av0[-1]
    with pytest.raises(OutOfGridError) as exc:
        NCH.sweep(gm_id=(5, 30), L=0.5, vds=0.9, n=21)
    assert "unreachable" in str(exc.value)


# --- G-1: sweep() had NO reachability gate at all (raw pygmid handle) ----------------------------


def test_sweep_default_range_past_reachable_max_raises():
    """The DEFAULT gm/ID range trips it on a perfectly ordinary bias.

    ``sweep()`` called the raw pygmid handle, so it bypassed both ``look_up()``'s NaN check and
    ``at()``'s reachability gate. At L=0.15 µm / VDS=0.9 V this LUT tops out at 24.4013 1/V, well
    under the default ``gm_id=(5, 25)``: pygmid pchip-extrapolated and returned a vgs tail of
    ``[0.4035, 301.02, 68316.2]`` **volts** with a non-monotonic jd — finite garbage, warning
    printed to stdout only.
    """
    with pytest.raises(OutOfGridError) as exc:
        NCH.sweep(L=0.15, vds=0.9)  # every argument but the bias left at its default
    msg = str(exc.value)
    assert "unreachable" in msg
    assert "24.4013" in msg  # names the reachable maximum, not just the VGS grid


@pytest.mark.parametrize(
    "vds", [pytest.param(float(v), id=f"vds{v:g}") for v in NCH.VDS_grid if float(v) > 0.0]
)
def test_sweep_reachable_band_edges_are_inclusive(vds):
    """The gate is the branch interval itself: both ends of the band still sweep — on EVERY slice.

    Parametrized over the fixture's own VDS grid, because pinning one hand-picked slice is how the
    original version of this test certified a promise it did not keep. ``at()``/``sweep()`` gate on
    the VGS that pygmid's pchip INVERSION solves; on a slice whose gm/ID peaks at the VGS grid edge
    (every sky130 slice) the band maximum solves a few ULP outside the grid — measured
    VGS=-6.07153e-18 V — and an untoleranced bound bounced the value ``gm_id_band()`` had just
    certified. This body is unchanged from the single-slice version; only the parametrization is
    new, and at vds=1.0 and vds=1.2 it failed before the tolerance landed.

    VDS=0 is excluded because that slice has no band at all — see
    ``test_degenerate_vds0_slice_has_no_usable_band``, which covers the whole VDS=0 plane.
    """
    lo, hi, _ = NCH.gm_id_band(0.15, vds)
    sw = NCH.sweep(gm_id=(lo, hi), L=0.15, vds=vds, n=9)
    assert np.all(np.isfinite(sw.jd)) and np.all(sw.jd > 0)
    assert np.all(np.isfinite(sw.vgs))
    # …and the snapped VGS the sweep reports is inside the characterized grid, not -6e-18 V.
    assert np.all(sw.vgs >= NCH.VGS_grid.min()) and np.all(sw.vgs <= NCH.VGS_grid.max())


@pytest.mark.parametrize("table_name", ["sky130", "ihp"])
def test_at_accepts_both_band_edges_on_every_slice_of_the_grid(table_name):
    """Whatever ``gm_id_band()`` certifies, ``at()`` must deliver — on all 144/96 usable slices.

    The contract README.md:79 states ("``at()`` and ``sweep()`` both gate every requested gm/ID
    against ``[lo, hi]``") is a CLOSED interval, so a band whose own endpoints ``at()`` refuses is
    the oracle contradicting itself. Measured before the fix: 62 of 147 sky130 slices rejected
    ``at(hi)`` on the solved-VGS float artifact. Walking the full (L, VDS, VSB) product is what
    makes this insensitive to which slice anyone happens to sample.
    """
    table = NCH if table_name == "sky130" else IHP_NCH
    checked, rejected = 0, []
    for L in table.L_grid:
        for vds in table.VDS_grid:
            for vsb in table.VSB_grid:
                try:
                    lo, hi, _ = table.gm_id_band(float(L), float(vds), float(vsb))
                except OutOfGridError:
                    continue  # a slice with no usable branch (VDS=0) — covered elsewhere
                checked += 1
                for edge, target in (("lo", lo), ("hi", hi)):
                    try:
                        op = table.at(target, float(L), float(vds), float(vsb))
                    except OutOfGridError as exc:
                        rejected.append((edge, float(L), float(vds), float(vsb), str(exc)[:120]))
                        continue
                    assert op.jd > 0
                    assert table.VGS_grid.min() <= op.vgs <= table.VGS_grid.max()
    assert checked > 90, f"only {checked} slices had a band — the fixture or the guard moved"
    assert rejected == [], f"{len(rejected)} of {2 * checked} band edges were refused by at()"


# --- G-2: at()'s guard tested the VGS grid, not the monotonic gm/ID branch -----------------------
#
# gm/ID is non-monotonic in VGS (it climbs to a weak-inversion peak, then collapses as the device
# turns off). pygmid inverts only the falling branch and extrapolates past it. The sky130 fixture
# peaks at the VGS=0 grid edge, so "solved VGS inside the VGS grid" happened to work there; the IHP
# sg13g2 fixture peaks at an INTERIOR VGS on most slices, where an above-peak request solves back to
# a VGS that is comfortably inside the grid and the old guard waved it through.


def test_gm_id_band_is_the_invertible_branch_not_the_vgs_grid():
    lo, hi, vgs_peak = IHP_NCH.gm_id_band(0.13, 0.4)
    assert hi == pytest.approx(27.7928, abs=1e-4)  # the weak-inversion peak of this slice
    assert vgs_peak == pytest.approx(0.25)  # …at an INTERIOR VGS (grid is [0..1.5] V)
    assert lo == pytest.approx(1.0219, abs=1e-3)
    assert IHP_NCH.VGS_grid.min() < vgs_peak < IHP_NCH.VGS_grid.max()


def test_at_just_above_interior_peak_raises():
    """gm/ID=27.8768 sits 0.084 1/V above this slice's peak → unreachable.

    Before the fix it returned a full OperatingPoint: solved VGS=0.235535 V (inside the [0..1.5] V
    grid, so the old range check passed), jd=2.927e-09 A/µm, av0=15.9109, ft=1.08161e+07 Hz —
    i.e. ``size_for_gm(gm=2π·1e-3)`` handed back W=77004.09 µm with every sanity gate green.
    """
    with pytest.raises(OutOfGridError) as exc:
        IHP_NCH.at(gm_id=27.8768, L=0.13, vds=0.4)
    msg = str(exc.value)
    assert "unreachable" in msg and "27.7928" in msg
    # The old guard could not have caught it: the solved VGS really is inside the grid.
    vgs_solved = float(
        np.asarray(IHP_NCH.lut.look_upVGS(GM_ID=27.8768, VDS=0.4, VSB=0.0, L=0.13)).reshape(-1)[0]
    )
    assert IHP_NCH.VGS_grid.min() <= vgs_solved <= IHP_NCH.VGS_grid.max()


def test_at_just_below_interior_peak_still_succeeds():
    """…and the mirror-image request 0.096 1/V *below* the peak is untouched by the guard."""
    op = IHP_NCH.at(gm_id=27.6968, L=0.13, vds=0.4)
    assert op.vgs == pytest.approx(0.269075, abs=1e-5)
    assert op.jd == pytest.approx(3.9894e-08, rel=1e-3)
    assert op.av0 == pytest.approx(15.6675, rel=1e-3)
    assert op.ft == pytest.approx(1.35744e08, rel=1e-3)


def test_at_above_peak_never_returns_a_negative_current_density():
    """The other side of the silent band: both audited targets sit above this slice's peak.

    Peak at (L=0.13 µm, VDS=0.2 V) is 27.6268 1/V. Pre-fix, gm/ID=27.6968 read jd=-1.56981e-09
    A/µm (→ W=-22999.70 µm at gm=1 mS) and gm/ID=27.8768 read jd=-3.26476e-08 A/µm (→ W=-1098.77
    µm) — negative current densities and negative widths, straight out of the extrapolator.
    """
    for gm_id in (27.6968, 27.8768):
        with pytest.raises(OutOfGridError):
            IHP_NCH.at(gm_id=gm_id, L=0.13, vds=0.2)
    assert IHP_NCH.gm_id_band(0.13, 0.2)[1] == pytest.approx(27.6268, abs=1e-4)


@pytest.mark.parametrize(
    ("table_name", "L", "vsb"),
    [
        pytest.param(name, float(L), float(vsb), id=f"{name}-L{L:g}-vsb{vsb:g}")
        for name, table in (("sky130", NCH), ("ihp", IHP_NCH))
        for L in table.L_grid
        for vsb in table.VSB_grid
    ],
)
def test_degenerate_vds0_slice_has_no_usable_band(table_name, L, vsb):
    """VDS=0 has no invertible branch — on EVERY (L, VSB), not one hand-picked slice.

    sky130 collapses to an all-zero locus, IHP to a non-finite one; both must raise rather than
    hand back a nonsense band (and ``at()`` with it). The single-slice version of this test never
    saw that 3 of the 16 sky130 VDS=0 slices carry exactly one *denormal* ID/W sample
    (8.9e-45 / 1.1e-44 / 3.8e-56 A/µm) — enough for a ``max(locus) > 0`` liveness probe, so
    ``gm_id_band(0.18, 0.0, 0.4)`` returned ``(0.0, 27.0041, 0.0)`` for a dead device.
    """
    table = NCH if table_name == "sky130" else IHP_NCH
    with pytest.raises(OutOfGridError) as exc:
        table.gm_id_band(L, 0.0, vsb)
    assert "no usable branch" in str(exc.value)
    with pytest.raises(OutOfGridError):
        table.at(gm_id=15, L=L, vds=0.0, vsb=vsb)


# --- gm_id_band() is a public entry point, so it gates its own bias axes -------------------------


@pytest.mark.parametrize(
    ("kwargs", "needle"),
    [
        pytest.param(dict(L=1e6, vds=0.9), "L=1e+06", id="L"),
        pytest.param(dict(L=0.5, vds=99.0), "VDS=99", id="VDS"),
        pytest.param(dict(L=0.5, vds=0.9, vsb=50.0), "VSB=50", id="VSB"),
    ],
)
def test_gm_id_band_gates_its_bias_axes(kwargs, needle):
    """Every other public entry bounds-checks its bias axes; the new band oracle did not.

    pygmid pchip-EXTRAPOLATES off the bias grid (finite garbage, never NaN), so an ungated call
    returned a confident-looking band instead of raising: measured ``NCH.gm_id_band(L=1e6,
    vds=0.9)`` = ``(-666233.3420074168, 166965.16417778376, 0.0)`` and ``gm_id_band(L=0.5,
    vds=99.0)`` = ``(-23.35131840836948, 26.624836384418813, 0.0)``. This is the call the migration
    guidance points downstream consumers at, so it is the one that had to be gated.
    """
    with pytest.raises(OutOfGridError) as exc:
        NCH.gm_id_band(**kwargs)
    msg = str(exc.value)
    assert needle in msg and "outside the characterized grid" in msg


def test_gm_id_band_rejects_a_non_positive_lower_bound(monkeypatch):
    """A band is a physical interval — ``lo <= 0`` is not a usable one, whatever the liveness probe says.

    Belt-and-braces behind ``_slice_carries_current``: this pins the second, independent guard by
    forcing the probe to call a genuinely dead slice alive. (L=0.18 µm, VDS=0 V, VSB=0.4 V) on the
    committed sky130 fixture is the real measured case — its gm/ID branch runs 0..27.0041 1/V, so
    pre-fix it yielded the band ``(0.0, 27.0041, 0.0)`` for a slice carrying 8.9e-45 A/µm.
    """
    monkeypatch.setattr(type(NCH), "_slice_carries_current", lambda self, L, vds, vsb: True)
    with pytest.raises(OutOfGridError) as exc:
        NCH.gm_id_band(0.18, 0.0, 0.4)
    msg = str(exc.value)
    assert "no usable branch" in msg and "strictly positive interval" in msg


def test_at_rejects_a_non_positive_current_density(monkeypatch):
    """Hard sanity gate behind the branch check: a ≤0 JD is unphysical, never an OperatingPoint.

    The LUTs store |ID| for both polarities, so a non-positive current density can only come from
    an extrapolated lookup. Pre-fix, ``at()`` passed whatever ``look_up`` returned straight into
    the contract.
    """
    real = type(NCH).look_up

    def fake(self, out, **kwargs):
        return -1.0 if out == "ID_W" else real(self, out, **kwargs)

    monkeypatch.setattr(type(NCH), "look_up", fake)
    with pytest.raises(OutOfGridError) as exc:
        NCH.at(gm_id=15, L=0.5, vds=0.9)
    assert "JD=-1" in str(exc.value)


# --- G-5: VDS=0 escaped as a bare scipy ValueError, outside the error hierarchy -------------------
#
# Every ratio-keyed lookup (GM_ID=… / ID_W=…) makes pygmid build a pchip over the slice's VGS
# locus. At VDS=0 — a LEGAL grid point on every PDK sweep — ID→0 at every VGS, the locus is
# flat/non-finite and scipy raises `ValueError: 'x' must contain only finite values` from
# _cubic.py. The band gate covers at()/sweep(); look_up() and gm_id_for_jd() went straight through.


@pytest.mark.parametrize("table_name", ["sky130", "ihp"])
def test_look_up_at_vds0_raises_out_of_grid_not_a_bare_value_error(table_name):
    table = NCH if table_name == "sky130" else IHP_NCH
    L = float(table.L_grid[0])
    with pytest.raises(OutOfGridError) as exc:
        table.look_up("ID_W", GM_ID=15.0, L=L, VDS=0.0, VSB=0.0)
    msg = str(exc.value)
    assert "VDS=0 is the offending axis" in msg     # names the axis, not just "not finite"
    assert "carries no current" in msg


@pytest.mark.parametrize("table_name", ["sky130", "ihp"])
def test_gm_id_for_jd_at_vds0_raises_out_of_grid_not_a_bare_value_error(table_name):
    table = NCH if table_name == "sky130" else IHP_NCH
    with pytest.raises(OutOfGridError) as exc:
        table.gm_id_for_jd(1e-7, float(table.L_grid[0]), 0.0)
    assert "VDS=0 is the offending axis" in str(exc.value)


def test_the_degenerate_axis_is_found_not_assumed():
    """VDS is named because moving VDS (and only VDS) restores a usable slice — L/VSB are innocent.

    The same on-grid L and VSB work perfectly at any other VDS, so a diagnosis that blamed either
    would be wrong; the probe re-tests one axis at a time.
    """
    ok = NCH.at(gm_id=15, L=0.15, vds=float(NCH.VDS_grid[1]), vsb=0.0)
    assert ok.jd > 0
    with pytest.raises(OutOfGridError) as exc:
        NCH.look_up("ID_W", GM_ID=15.0, L=0.15, VDS=0.0, VSB=0.0)
    msg = str(exc.value)
    assert "VDS=0 is the offending axis" in msg
    assert "L=0.15 is the offending axis" not in msg and "VSB=0 is the offending axis" not in msg


def test_off_grid_bias_still_reports_the_grid_bounds_not_the_degenerate_slice():
    """The pre-existing off-grid message must not be swallowed by the new degeneracy diagnosis."""
    with pytest.raises(OutOfGridError) as exc:
        NCH.look_up("ID_W", GM_ID=15.0, L=0.15, VDS=99.0, VSB=0.0)
    assert "outside the characterized grid" in str(exc.value)
