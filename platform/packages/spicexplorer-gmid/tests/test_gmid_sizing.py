"""Sizing flows: gm-first vs current-first equivalence, the de-normalization, and sanity gates."""

import math
from pathlib import Path

import pytest
from _gmid_fixtures import IHP_NCH, NCH, perturbed_lut
from spicexplorer_gmid import (
    DeviceTable,
    FingerWidthSet,
    GeometryBounds,
    GmidError,
    OutOfGridError,
    SizedDevice,
    size_for_current_density,
    size_for_gm,
)


@pytest.fixture(scope="module")
def narrow_table(tmp_path_factory: pytest.TempPathFactory) -> DeviceTable:
    """A 1 µm-finger companion to the 5 µm sky130 fixture (see ``_gmid_fixtures.perturbed_lut``)."""
    dest: Path = tmp_path_factory.mktemp("gmid_size_wf") / "sky130_fd_pr__nfet_01v8__tt__wf1u.pkl"
    return perturbed_lut(
        dest,
        scale={"ID": 1.6, "GM": 1.25, "GDS": 0.9, "CGG": 1.1, "CDD": 1.2},
        headers={"W": 1.0},
    )


@pytest.fixture(scope="module")
def fset(narrow_table: DeviceTable) -> FingerWidthSet:
    return FingerWidthSet({1.0: narrow_table, 5.0: NCH})


def _gate(dev: SizedDevice, name: str):
    return next(g for g in dev.gates if g.name == name)


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


# --- fail-loud sizing gates (no confidently-wrong width) -----------------------------------------


def test_size_for_gm_above_the_gm_id_peak_raises_instead_of_a_plausible_width():
    """The silent band: a designer chasing maximum gm/ID used to get a *plausible* answer.

    (L=0.13 µm, VDS=0.4 V) on the IHP fixture peaks at 27.7928 1/V. Pre-fix, asking for 27.8768
    returned W=77004.09 µm with ``passed=True`` and every gate green; 27.6968 (just under the peak)
    is genuinely reachable and still sizes to W=5686.47 µm.
    """
    ok = size_for_gm(IHP_NCH, gm=2 * math.pi * 1e-3, gm_id=27.6968, L=0.13, vds=0.4)
    assert ok.W == pytest.approx(5686.47, rel=1e-4)
    with pytest.raises(OutOfGridError):
        size_for_gm(IHP_NCH, gm=2 * math.pi * 1e-3, gm_id=27.8768, L=0.13, vds=0.4)


def test_size_for_gm_never_returns_a_negative_width_as_passed():
    """(L=0.13 µm, VDS=0.2 V) peaks at 27.6268 1/V, so both audited targets are unreachable.

    Pre-fix at gm=1 mS they produced W=-22999.70 µm and W=-1098.77 µm — negative widths that the
    ``SizedDevice`` gate ledger has no opinion about (it never checks the sign of W).
    """
    for gm_id in (27.6968, 27.8768):
        with pytest.raises(OutOfGridError):
            size_for_gm(IHP_NCH, gm=1e-3, gm_id=gm_id, L=0.13, vds=0.2)


@pytest.mark.parametrize("gm", [-1e-3, 0.0, float("nan")])
def test_size_for_gm_rejects_a_non_positive_transconductance(gm):
    """gm is a magnitude here — a ≤0/NaN target used to flow straight through into W and ID."""
    with pytest.raises(GmidError):
        size_for_gm(NCH, gm=gm, gm_id=15, L=0.5, vds=0.9)


@pytest.mark.parametrize("ID", [-50e-6, 0.0])
def test_size_for_current_density_rejects_a_non_positive_bias_current(ID):
    with pytest.raises(GmidError):
        size_for_current_density(NCH, ID=ID, gm_id=15, L=0.5, vds=0.9)


# --- a FingerWidthSet is a usable table in the sizing flows ---------------------------------------


def test_size_for_gm_accepts_a_finger_width_set(fset: FingerWidthSet, narrow_table: DeviceTable):
    """``FingerWidthSet.at`` takes ``wf`` keyword-ONLY, so the positional call used to TypeError.

    The finger-width axis was therefore unreachable from the sizing API entirely.
    """
    dev = size_for_gm(fset, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=1.0)
    ref = narrow_table.at(15.0, 0.5, 0.9, 0.0)
    assert dev.op.jd == pytest.approx(ref.jd, rel=1e-12)  # the 1 µm table, not the 5 µm fixture
    assert dev.W == pytest.approx(dev.ID / ref.jd, rel=1e-12)
    assert dev.nf == round(dev.W / 1.0)  # fingers land on the requested width
    assert dev.passed


def test_size_for_gm_on_a_finger_width_set_interpolates_between_the_tables(
    fset: FingerWidthSet, narrow_table: DeviceTable
):
    """An off-grid (but bracketed) wf sizes off the blended table, not either endpoint."""
    mid = size_for_gm(fset, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=3.0)
    lo = size_for_gm(fset, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=1.0)
    hi = size_for_gm(fset, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=5.0)
    assert min(lo.op.jd, hi.op.jd) < mid.op.jd < max(lo.op.jd, hi.op.jd)
    assert min(lo.W, hi.W) < mid.W < max(lo.W, hi.W)
    assert hi.op.jd == pytest.approx(NCH.at(15.0, 0.5, 0.9, 0.0).jd, rel=1e-12)
    assert lo.op.jd == pytest.approx(narrow_table.at(15.0, 0.5, 0.9, 0.0).jd, rel=1e-12)


def test_size_for_current_density_accepts_a_finger_width_set(fset: FingerWidthSet):
    """Both flows, including the JD-first one (which needs ``gm_id_for_jd`` per finger width).

    ``jd=3e-7`` rather than the ``2e-6`` this test shipped with: at ``2e-6``/``wf=2.0`` the blend
    misses its own 5 % round trip by 7.16 % and now raises — this test was pinning a ``SizedDevice``
    whose ``op`` disagreed with its own ``W``. See
    ``test_a_jd_sized_device_agrees_with_its_own_operating_point``.
    """
    by_gm_id = size_for_current_density(fset, ID=50e-6, gm_id=12, L=0.5, vds=0.9, wf=2.0)
    assert by_gm_id.gm == pytest.approx(12 * 50e-6)
    by_jd = size_for_current_density(fset, ID=50e-6, jd=3e-7, L=0.5, vds=0.9, wf=2.0)
    assert by_jd.op.gm_id == pytest.approx(
        fset.gm_id_for_jd(3e-7, 0.5, 0.9, 0.0, wf=2.0), rel=1e-12
    )
    assert by_jd.W == pytest.approx(50e-6 / 3e-7, rel=1e-12)  # W = ID/JD at the TARGET density


def test_a_jd_sized_device_agrees_with_its_own_operating_point(fset: FingerWidthSet):
    """``W = ID/jd`` is sized from the REQUESTED density — so ``op.jd`` has to be that density.

    The JD-first flow on a set lerped two per-table gm/ID inversions and never round-tripped the
    blend, so a returned ``SizedDevice`` could disagree with its own operating point by more than
    the 5 % ``DeviceTable.gm_id_for_jd`` enforces — 7.16 % on this fixture at the shipped test's own
    call shape (W=25 µm reported, W=23.3289 µm implied by ``op.jd``), gates all green, ``passed``
    True. Now every accepted answer honours the contract, and the ones that cannot raise.
    """
    jd = 3e-7
    dev = size_for_current_density(fset, ID=50e-6, jd=jd, L=0.5, vds=0.9, wf=2.0)
    assert dev.op.jd == pytest.approx(jd, rel=0.05)
    assert dev.W == pytest.approx(dev.ID / dev.op.jd, rel=0.05)
    with pytest.raises(OutOfGridError, match="does not invert consistently"):
        size_for_current_density(fset, ID=50e-6, jd=2e-6, L=0.5, vds=0.9, wf=2.0)


@pytest.mark.parametrize(
    "call",
    [
        lambda t: size_for_gm(t, gm=1e-3, gm_id=15, L=0.5, vds=0.9),
        lambda t: size_for_current_density(t, ID=50e-6, gm_id=15, L=0.5, vds=0.9),
        lambda t: size_for_current_density(t, ID=50e-6, jd=2e-6, L=0.5, vds=0.9),
    ],
)
def test_sizing_a_finger_width_set_without_wf_raises_gmid_error(fset: FingerWidthSet, call):
    """A set has no single characterised width — the omission is a GmidError, not a bare TypeError."""
    with pytest.raises(GmidError, match="wf="):
        call(fset)


# --- the finger-width gate (the LUT only describes its characterization width) --------------------


def test_finger_width_gate_fails_when_wf_max_fingers_far_below_w_char():
    """``wf_max`` used to finger a device arbitrarily far off ``w_char`` with every gate green.

    The sky130 fixture is characterized at W=5 µm; ``wf_max=1`` realises ~0.97 µm fingers, i.e. the
    narrow-width regime the LUT's per-µm numbers were never extracted in.
    """
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=1.0)
    assert NCH.w_char == pytest.approx(5.0)
    assert dev.wf == pytest.approx(dev.W / dev.nf) and dev.wf < 1.0
    gate = _gate(dev, "finger_width")
    assert not gate.ok
    assert "5" in gate.detail  # names the characterization width
    assert not dev.passed


def test_finger_width_gate_passes_near_the_characterization_width():
    """The everyday call — fingers at the width the table was extracted at — stays green."""
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=5.0)
    assert _gate(dev, "finger_width").ok and dev.passed


def test_finger_width_gate_is_advisory_until_a_width_is_stated():
    """No ``wf``: fingering WIDER than w_char is the method's own width-invariance, not a defect.

    But it is also a direction nobody checked, so it must not render as **green** either — the gate
    reports ``status="unchecked"`` (``ok=False``, advisory) and leaves ``passed`` alone. Stating
    ``wf=`` turns it into an intent the realised geometry has to match, so the same geometry then
    goes hard red.
    """
    wide = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9)  # nf=1, W≈22 µm ≫ 5 µm
    assert wide.nf == 1 and wide.W > 4 * NCH.w_char
    gate = _gate(wide, "finger_width")
    assert gate.status == "unchecked" and not gate.ok and not gate.blocking
    assert "advisory only" in gate.detail
    assert wide.passed  # …and it does NOT veto
    stated = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=5.0, wf_max=30.0)
    assert stated.nf == 1  # wf_max wins the count
    assert _gate(stated, "finger_width").status == "fail"
    assert not _gate(stated, "finger_width").ok and not stated.passed


@pytest.mark.parametrize(
    ("wf_max", "ratio", "expect_status"),
    [
        pytest.param(10.0, 1.491, "ok", id="wf_max10-plus49pct-INSIDE-the-2x-window"),
        pytest.param(23.0, 4.473, "unchecked", id="wf_max23-plus347pct-outside"),
        pytest.param(5.0, 0.8951, "ok", id="wf_max5-near-w_char"),
        pytest.param(1.0, 0.1945, "fail", id="wf_max1-minus81pct-narrow"),
    ],
)
def test_the_finger_width_gate_under_wf_max_is_narrow_side_only(wf_max, ratio, expect_status):
    """Pins what ``wf_max`` actually polices, against a commit message that claimed more.

    Measured on the shipped sky130 fixture (``w_char`` = 5 µm, W = 22.3658 µm): ``wf_max=10`` → nf=3,
    W/nf = 7.4553 µm — **+49.1 % off ``w_char`` and still green**, because +49.1 % is *inside* the
    2× window. That is the exact measurement the commit message cites as the defect this gate
    closes, and it is not closed: only gross NARROWING is a hard fail. (The 2× threshold is
    explicitly unmeasured and its value is an owner decision, so it is pinned here, not changed.)

    ``wf_max=23`` → nf=1, 22.3658 µm (+347.3 %) is outside the window on the *wide* side, which
    nothing checks without a stated ``wf`` — it used to read ``ok=True`` all the same. It now reads
    ``status="unchecked"``: reported, not green, and still not a veto.
    """
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=wf_max)
    gate = _gate(dev, "finger_width")
    assert dev.wf / NCH.w_char == pytest.approx(ratio, rel=1e-3)
    assert gate.status == expect_status
    assert dev.passed is (expect_status != "fail")  # only a hard fail vetoes


@pytest.mark.parametrize(
    ("gm", "expect_status"),
    [
        pytest.param(1e-3, "unchecked", id="W22.4-wide"),
        pytest.param(3e-4, "ok", id="W6.71"),
        pytest.param(1.5e-4, "ok", id="W3.36"),
        pytest.param(1e-4, "unchecked", id="W2.24-narrow"),
        pytest.param(5e-5, "unchecked", id="W1.12-narrow"),
        pytest.param(2e-5, "unchecked", id="W0.45-narrow"),
        pytest.param(1e-5, "unchecked", id="W0.22-narrow"),
    ],
)
def test_a_plain_size_for_gm_is_never_vetoed_by_the_finger_width_gate(gm, expect_status):
    """No ``wf``, no ``wf_max`` — no finger-width intent, so nothing to gate on.

    The gate as first written checked the narrow side unconditionally, flipping ``passed``
    True→False on 4 of these 7 ordinary calls: everything under W < w_char/2 = 2.5 µm, i.e. below
    ~7.5 µA on this LUT — the whole low-current half of the design space, which is where gm/ID
    methodology is most used. With no ``wf``/``wf_max`` and nf=1, ``W/nf`` is not a finger choice
    at all: it is the total width the physics demanded, so the ledger is reporting LUT coverage,
    not caller geometry. It stays visible (``status="unchecked"``, ``ok=False``) and stops voting.
    """
    dev = size_for_gm(NCH, gm=gm, gm_id=15, L=0.5, vds=0.9)
    gate = _gate(dev, "finger_width")
    assert dev.nf == 1
    assert gate.status == expect_status
    assert dev.passed, "a call that stated no finger-width intent must not be vetoed by one"


def test_a_stated_wf_max_still_hard_gates_the_narrow_side():
    """Control for the advisory above: the narrow check is not gone, it is scoped to stated intent.

    Same LUT, same slice, same ~0.97 µm realised finger — red once ``wf_max`` says the caller chose
    the geometry.
    """
    intent = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=1.0)
    none = size_for_gm(NCH, gm=2e-5, gm_id=15, L=0.5, vds=0.9)
    assert intent.wf < 1.0 and none.wf < 1.0  # both well under w_char/2
    assert _gate(intent, "finger_width").status == "fail" and not intent.passed
    assert _gate(none, "finger_width").status == "unchecked" and none.passed


def test_wf_drives_the_finger_count_when_no_maximum_is_given():
    """``wf`` alone picks the finger count that lands nearest the requested finger width."""
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=5.0)
    assert dev.nf == round(dev.W / 5.0) >= 2
    assert _gate(dev, "finger_width").ok


def test_stated_wf_on_a_single_width_table_is_gated_against_that_tables_w_char():
    """A 5 µm table cannot describe a 1 µm finger — asking for one is red, not silently accepted."""
    dev = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=1.0)
    assert dev.wf == pytest.approx(1.0, rel=0.05)
    assert not _gate(dev, "finger_width").ok and not dev.passed


@pytest.mark.parametrize("wf_ratio_max", [0.0, 0.5, -1.0, float("nan")])
def test_a_wf_ratio_max_below_one_is_rejected_not_silently_inverted(wf_ratio_max):
    """The gate's own knob is gated: below 1 its window turns inside-out, and 0 divides by zero.

    ``wf_ratio_max`` widens the allowed band to ``[w_char/r .. w_char·r]``, so r<1 puts the LOWER
    bound *above* the characterization width — the check then means the opposite of its ``detail``
    string. Unvalidated, ``r=0`` escaped as a bare ``ZeroDivisionError`` (outside the package's
    ``GmidError``/``OutOfGridError`` hierarchy) and ``r=0.5`` returned a ``SizedDevice`` reporting
    ``allowed ≥2`` while passing a 4.47 ratio.
    """
    with pytest.raises(GmidError, match="wf_ratio_max"):
        size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_ratio_max=wf_ratio_max)


def test_wf_ratio_max_accepts_infinity_as_no_opinion():
    """``math.inf`` is the natural spelling of "don't gate finger width" and was rejected.

    It yields the well-defined window ``[0 .. inf]`` — strictly more permissive than the ``1e9``
    that was already accepted, so banning it left ``1e9`` as the only idiom for switching the gate
    off. NaN and anything below 1 stay rejected (the test above).
    """
    off = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=1.0, wf_ratio_max=math.inf)
    assert _gate(off, "finger_width").status == "ok" and off.passed
    default = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=1.0)
    assert _gate(default, "finger_width").status == "fail"  # …the same geometry at the 2× default
    assert off.W == pytest.approx(default.W) and off.nf == default.nf


def test_wf_ratio_max_of_exactly_one_is_the_tight_end_of_the_domain():
    """Accept-side control for the rejection above: r=1 is legal (the bound is inclusive).

    At r=1 the allowed window collapses to the characterization width itself, so the same geometry
    that passes at the 2× default goes red — which is the knob doing its job, not the guard
    over-reaching. Keeps the rejection test from being satisfiable by simply banning the knob.
    """
    tight = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=5.0, wf_ratio_max=1.0)
    loose = size_for_gm(NCH, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf_max=5.0)
    assert tight.wf == pytest.approx(loose.wf)  # identical geometry, different tolerance
    assert _gate(loose, "finger_width").ok  # ratio 0.895 is inside the 2× window
    assert not _gate(tight, "finger_width").ok  # …and outside the 1× one
