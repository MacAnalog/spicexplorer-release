"""The gm/ID sizing flows: pick an inversion level (gm/ID) and length, read JD off the table, and
de-normalise a transconductance or a bias current into a width.

The two entry points are the same lookup approached from opposite ends:

* :func:`size_for_gm` — *gm-first* (the canonical 5-step): you have a gm spec (e.g. from a target
  GBW and load), choose gm/ID and L, then ``ID = gm / (gm/ID)`` and ``W = ID / JD``.
* :func:`size_for_current_density` — *current-first / JD flow*: you fix the bias current (head-room
  / power budget) and the inversion level, then ``W = ID / JD`` and ``gm = (gm/ID)·ID``.

Both accept **either** table type: a single-finger-width :class:`~spicexplorer_gmid.DeviceTable`, or
a :class:`~spicexplorer_gmid.FingerWidthSet` (which additionally needs ``wf=`` — the finger width to
interpolate at, passed through as the keyword-only argument that class requires).

Both attach a :class:`~spicexplorer_gmid.contract.SizedDevice` carrying the operating point and a
ledger of sanity gates (saturation head-room, geometry envelope, finger width vs the table's
characterization width, finite intrinsic gain/fT). Each gate is three-state — ``ok`` / ``fail`` /
``unchecked``, the last an **advisory** that is reported but does not veto ``passed`` (see
:func:`_finger_width_gate`). Nothing is silently clamped — an off-grid request raises from the
table layer.
"""

from __future__ import annotations

import math

from .contract import GeometryBounds, OperatingPoint, SanityGate, SizedDevice
from .errors import GmidError
from .fingerwidth import FingerWidthSet
from .tables import DeviceTable

SizingTable = DeviceTable | FingerWidthSet
"""Either table type may drive a sizing flow (a :class:`FingerWidthSet` also needs ``wf=``)."""

# The LUT's normalised parameters (JD, gm/gds, C/W) are extracted for ONE finger of the table's
# characterization width. They stay invariant as you ADD identical fingers, and are essentially flat
# for fingers WIDER than that — that width-invariance is the assumption the whole methodology rests
# on, and `wf_max` / `bounds.w_max` already police the wide side as a layout rule. Fingers materially
# NARROWER than the characterization width are the ones that break it (narrow-width effects: a
# 0.5 µm and a 5 µm finger read a few-to-tens of % apart — exactly what `FingerWidthSet` exists for).
#
# The 2× default is argued from that physics, NOT measured against a live PDK sweep — so it is a
# caller knob, and *who it is allowed to veto* is deliberately narrow. See `_finger_width_gate`:
# the gate is a HARD gate only where the caller stated a finger-width intent (`wf=` or `wf_max=`);
# with no intent stated, `W/nf` is not a finger choice at all — it is the total width the physics
# demanded — so the check is reported as an **advisory** (`status="unchecked"`) and does not veto
# `SizedDevice.passed`.
_WF_RATIO_MAX = 2.0


def _require_positive(name: str, value: float, unit: str) -> None:
    """Fail loud on a non-finite or non-positive sizing quantity.

    Currents, transconductances, current densities and widths are magnitudes here (the LUTs store
    |ID|/|GM| for both polarities), so a NaN/inf/≤0 is never a valid answer — it is a garbage
    lookup or a nonsensical target leaking into a :class:`SizedDevice`. Raising beats returning a
    negative width with green sanity gates.
    """
    if not math.isfinite(value) or value <= 0.0:
        raise GmidError(
            f"{name}={value:g} {unit} is not a finite positive quantity — refusing to emit a "
            f"confidently-wrong size. Check the gm/ID target, the bias point and the LUT."
        )


def _require_ratio_max(wf_ratio_max: float) -> None:
    """``wf_ratio_max`` is a *widening* factor — anything under 1 inverts the gate it configures.

    The gate's window is ``[w_ref/wf_ratio_max .. w_ref·wf_ratio_max]``, so 1.0 is "the realised
    finger must be exactly the characterization width" and larger values loosen it. Below 1 that
    window turns inside-out (its lower bound rises *above* ``w_ref``), which silently reverses the
    check's meaning, and 0 divides by zero — a ``ZeroDivisionError`` outside this package's error
    hierarchy. Reject both rather than emit a ``SizedDevice`` whose ledger means the opposite of
    what it says.

    ``math.inf`` **is** accepted: it is the natural spelling of "no opinion" and yields the
    well-defined window ``[0 .. inf]``, strictly more permissive than the ``1e9`` that was already
    legal. Banning it left ``1e9`` as the only idiom for switching the gate off. Only NaN and
    values below 1 are rejected.
    """
    if math.isnan(wf_ratio_max) or wf_ratio_max < 1.0:
        raise GmidError(
            f"wf_ratio_max={wf_ratio_max:g} is not a usable widening factor — it must be ≥ 1 "
            f"(the finger_width gate allows [w_char/wf_ratio_max .. w_char·wf_ratio_max]; below 1 "
            f"that window inverts). Pass 1.0 for an exact-width requirement, or math.inf for none."
        )


def _require_wf(table: FingerWidthSet, wf: float | None) -> float:
    """A :class:`FingerWidthSet` has no single characterised width — ``wf`` is not optional there."""
    if wf is None:
        raise GmidError(
            "sizing against a FingerWidthSet needs an explicit wf=<finger width µm> — it selects "
            f"the finger width to interpolate the operating point at. Characterised widths: "
            f"{table.finger_widths} µm."
        )
    return wf


def _operating_point(
    table: SizingTable, gm_id: float, L: float, vds: float, vsb: float, wf: float | None
) -> tuple[OperatingPoint, float]:
    """``(operating point, the finger width its normalised parameters describe [µm])``.

    A :class:`FingerWidthSet` is interpolated **at** ``wf``, so ``wf`` is what its numbers describe;
    a :class:`DeviceTable` only ever describes its own ``w_char``, whatever finger width the caller
    intends to draw — which is precisely what the ``finger_width`` gate then compares against.
    """
    if isinstance(table, FingerWidthSet):
        w_ref = _require_wf(table, wf)
        return table.at(gm_id, L, vds, vsb, wf=w_ref), w_ref
    return table.at(gm_id, L, vds, vsb), table.w_char


def _resolve_gm_id_for_jd(
    table: SizingTable, jd: float, L: float, vds: float, vsb: float, wf: float | None
) -> float:
    """The JD→gm/ID inversion on either table type (keyword-passing ``wf`` where it is required)."""
    if isinstance(table, FingerWidthSet):
        return table.gm_id_for_jd(jd, L, vds, vsb, wf=_require_wf(table, wf))
    return table.gm_id_for_jd(jd, L, vds, vsb)


def _fingers(w_total: float, wf_max: float | None, wf: float | None = None) -> int:
    """Number of fingers: ``ceil(W/wf_max)`` under a per-finger maximum, else the count that lands
    the realised finger width nearest a requested ``wf`` (1 when neither is given)."""
    if wf_max is not None and wf_max > 0:
        return max(1, math.ceil(w_total / wf_max))
    if wf is not None and wf > 0:
        return max(1, round(w_total / wf))
    return 1


def _finger_width_gate(
    w_total: float, nf: int, w_ref: float, *, stated_wf: bool, stated_intent: bool, ratio_max: float
) -> SanityGate:
    """Realised finger width ``W/nf`` vs the width the operating point was characterized at.

    ``w_ref`` is the table's ``w_char`` (or, on a :class:`FingerWidthSet`, the requested ``wf``).
    The measurement is always reported; what varies is whether it is allowed to **veto** the sizing:

    * ``stated_intent`` (the caller passed ``wf=`` or ``wf_max=``) makes the NARROW side a hard
      gate — they chose a finger geometry, and below ``w_ref/ratio_max`` the LUT's normalised
      parameters were never extracted there.
    * ``stated_wf`` (the caller passed ``wf=`` specifically) additionally makes the WIDE side hard:
      a stated finger width is an intent the realised geometry has to match.
    * Otherwise the out-of-window measurement is reported as ``status="unchecked"`` — an advisory.
      With no ``wf``/``wf_max``, ``W/nf`` is not a finger choice at all: ``nf`` is 1 and ``W`` is
      whatever the physics demanded, so the ledger is really reporting LUT *coverage*, not caller
      geometry. Gating on it flipped ``passed`` True→False on 4 of 7 ordinary ``size_for_gm``
      calls — every device under W < w_char/2 (below ~7.5 µA on the 5 µm sky130 LUT), i.e. the
      whole low-current half of the design space, which is where gm/ID methodology is most used.
      The advisory keeps that visible (``ok=False``) without vetoing it.

    The wide side under ``wf_max`` alone is likewise advisory rather than green: ``wf_max=23`` on
    the sky130 fixture realises a 22.37 µm finger off a 5 µm table (+347.3 %), and reporting that
    ``ok=True`` was the ledger claiming a direction it had not checked.

    Note what this gate does **not** do, since it has been claimed otherwise: ``wf_max`` is not
    policed on the wide side within the window. ``wf_max=10`` realises a 7.46 µm finger off that
    same 5 µm table — +49.1 %, ``status="ok"``, ``passed`` True — because +49.1 % is inside the 2×
    window. Only gross narrowing is a hard fail. The 2× value is argued, not measured (see
    ``_WF_RATIO_MAX``), so tightening it is an owner decision.
    """
    wf = w_total / nf
    if not math.isfinite(w_ref) or w_ref <= 0.0:
        return SanityGate(
            name="finger_width",
            ok=False,
            status="fail",
            detail=f"W/nf={wf:.4g} µm vs an unusable characterization width w_char={w_ref:g} µm",
        )
    ratio = wf / w_ref
    floor = 1.0 / ratio_max
    if ratio < floor:
        status = "fail" if stated_intent else "unchecked"
    elif ratio > ratio_max:
        status = "fail" if stated_wf else "unchecked"
    else:
        status = "ok"
    window = f"[{floor:.3g}..{ratio_max:.3g}]"
    note = (
        " — advisory only (status='unchecked'): the caller stated no wf=/wf_max= in that "
        "direction, so this does not gate `passed`"
        if status == "unchecked"
        else ""
    )
    return SanityGate(
        name="finger_width",
        ok=status == "ok",
        status=status,
        detail=(
            f"W/nf={wf:.4g} µm vs characterization width {w_ref:.4g} µm "
            f"(ratio {ratio:.3g}, allowed {window}){note}"
        ),
    )


def _gates(
    op: OperatingPoint,
    w_total: float,
    nf: int,
    bounds: GeometryBounds | None,
    *,
    w_ref: float,
    stated_wf: bool,
    stated_intent: bool,
    wf_ratio_max: float,
) -> list[SanityGate]:
    """The standard sizing sanity gates (the gmid-skills verification list, encoded)."""
    gates: list[SanityGate] = []

    # Saturation head-room: VDS must clear the saturation voltage. The methodology's quick estimate
    # is V_Dsat ≈ 2/(gm/ID) in strong inversion (floored near a few U_T in weak inversion).
    vdsat = max(2.0 / op.gm_id, 0.1)
    gates.append(
        SanityGate(
            name="saturation",
            ok=op.vds >= vdsat,
            detail=f"VDS={op.vds:.3g} V vs V_Dsat≈{vdsat:.3g} V (≈2/(gm/ID))",
        )
    )

    # Intrinsic gain / fT must be finite & positive (a NaN here would have raised already).
    gates.append(
        SanityGate(
            name="intrinsic_gain",
            ok=math.isfinite(op.av0) and op.av0 > 0,
            detail=f"av0=gm/gds={op.av0:.3g}",
        )
    )
    gates.append(
        SanityGate(
            name="ft",
            ok=math.isfinite(op.ft) and op.ft > 0,
            detail=f"fT={op.ft:.4g} Hz",
        )
    )

    # Finger width: the LUT's per-µm numbers only describe a finger of the characterization width.
    gates.append(
        _finger_width_gate(
            w_total,
            nf,
            w_ref,
            stated_wf=stated_wf,
            stated_intent=stated_intent,
            ratio_max=wf_ratio_max,
        )
    )

    # Geometry envelope (only when the caller supplies PDK bounds). The w_min/w_max bounds are
    # PER-FINGER (a finger has a min manufacturable width and a max before you must add fingers),
    # so the check is on W/nf, not the total W — a multi-finger device's total W legitimately
    # exceeds the single-finger max.
    if bounds is not None:
        wf = w_total / nf
        w_ok = True
        bits = []
        if bounds.w_min is not None:
            w_ok = w_ok and wf >= bounds.w_min
            bits.append(f"w_min={bounds.w_min:g}")
        if bounds.w_max is not None:
            w_ok = w_ok and wf <= bounds.w_max
            bits.append(f"w_max={bounds.w_max:g}")
        gates.append(
            SanityGate(
                name="geometry_w",
                ok=w_ok,
                detail=f"W/nf={wf:.4g} µm (W={w_total:.4g}, nf={nf}) vs {{{', '.join(bits) or 'no W bounds'}}}",
            )
        )
        if bounds.l_min is not None or bounds.l_max is not None:
            l_ok = True
            lbits = []
            if bounds.l_min is not None:
                l_ok = l_ok and op.L >= bounds.l_min
                lbits.append(f"l_min={bounds.l_min:g}")
            if bounds.l_max is not None:
                l_ok = l_ok and op.L <= bounds.l_max
                lbits.append(f"l_max={bounds.l_max:g}")
            gates.append(
                SanityGate(
                    name="geometry_l",
                    ok=l_ok,
                    detail=f"L={op.L:.4g} µm vs {{{', '.join(lbits)}}}",
                )
            )
    return gates


def _assemble(
    op: OperatingPoint,
    *,
    ID: float,
    gm: float,
    wf_max: float | None,
    bounds: GeometryBounds | None,
    w_ref: float,
    wf: float | None = None,
    wf_ratio_max: float = _WF_RATIO_MAX,
    jd: float | None = None,
) -> SizedDevice:
    # Width from current density. When the caller specified a target JD (the JD-first flow), size to
    # THAT density; otherwise use the table value at the chosen gm/ID. (They agree to the LUT's
    # forward/inverse interpolation tolerance.)
    density = jd if jd is not None else op.jd
    _require_ratio_max(wf_ratio_max)
    _require_positive("gm", gm, "S")
    _require_positive("ID", ID, "A")
    _require_positive("jd", density, "A/µm")
    w_total = ID / density
    # Belt-and-braces: a width is a manufacturable dimension. A non-finite or non-positive W is a
    # confidently-wrong size, and must never leave this function with `passed=True` attached.
    _require_positive("W", w_total, "µm")
    nf = _fingers(w_total, wf_max, wf)
    return SizedDevice(
        W=w_total,
        L=op.L,
        nf=nf,
        ID=ID,
        gm=gm,
        cgg=op.cgg_w * w_total,
        cdd=op.cdd_w * w_total,
        op=op,
        gates=_gates(
            op,
            w_total,
            nf,
            bounds,
            w_ref=w_ref,
            stated_wf=wf is not None,
            stated_intent=wf is not None or wf_max is not None,
            wf_ratio_max=wf_ratio_max,
        ),
    )


def size_for_gm(
    table: SizingTable,
    *,
    gm: float,
    gm_id: float,
    L: float,
    vds: float,
    vsb: float = 0.0,
    wf: float | None = None,
    wf_max: float | None = None,
    wf_ratio_max: float = _WF_RATIO_MAX,
    bounds: GeometryBounds | None = None,
) -> SizedDevice:
    """Size a device to a transconductance target (the canonical gm-first 5-step flow).

    ``ID = gm / (gm/ID)`` sets the bias current, then ``W = ID / JD`` from the table's current
    density. ``gm`` in S, ``gm_id`` in 1/V, ``L`` in µm, voltages in V.

    ``table`` may be a :class:`~spicexplorer_gmid.DeviceTable` or a
    :class:`~spicexplorer_gmid.FingerWidthSet`; the latter **requires** ``wf`` (µm), the finger
    width to interpolate at. ``wf`` on a plain ``DeviceTable`` is the finger width you intend to
    draw: it picks the finger count (nearest integer) and makes the ``finger_width`` gate a
    two-sided **hard** gate against the table's ``w_char``. ``wf_max`` (a per-finger maximum,
    ``ceil``) takes precedence over ``wf`` for the finger count, and hard-gates the narrow side
    only. With neither stated, the ``finger_width`` check is advisory (``status="unchecked"``) and
    never flips ``passed`` — see :func:`_finger_width_gate`.
    """
    op, w_ref = _operating_point(table, gm_id, L, vds, vsb, wf)
    ID = gm / gm_id
    return _assemble(
        op,
        ID=ID,
        gm=gm,
        wf_max=wf_max,
        bounds=bounds,
        w_ref=w_ref,
        wf=wf,
        wf_ratio_max=wf_ratio_max,
    )


def size_for_current_density(
    table: SizingTable,
    *,
    ID: float,
    gm_id: float | None = None,
    jd: float | None = None,
    L: float,
    vds: float,
    vsb: float = 0.0,
    wf: float | None = None,
    wf_max: float | None = None,
    wf_ratio_max: float = _WF_RATIO_MAX,
    bounds: GeometryBounds | None = None,
) -> SizedDevice:
    """Size a device from a fixed bias current and inversion level (current-first / JD flow).

    Give **exactly one** of ``gm_id`` (1/V) or ``jd`` (current density A/µm — the weak-inversion
    knob, where gm/ID plateaus). ``W = ID / JD`` from the table; ``gm = (gm/ID)·ID`` falls out.
    ``table`` / ``wf`` / ``wf_max`` behave exactly as in :func:`size_for_gm`.
    """
    if (gm_id is None) == (jd is None):
        raise GmidError("size_for_current_density needs exactly one of gm_id or jd")
    if jd is not None:
        gm_id = _resolve_gm_id_for_jd(table, jd, L, vds, vsb, wf)
    if gm_id is None:  # unreachable (guarded above) but narrows the type for pyright
        raise GmidError("gm_id unresolved")
    op, w_ref = _operating_point(table, gm_id, L, vds, vsb, wf)
    gm = gm_id * ID
    return _assemble(
        op,
        ID=ID,
        gm=gm,
        wf_max=wf_max,
        bounds=bounds,
        w_ref=w_ref,
        wf=wf,
        wf_ratio_max=wf_ratio_max,
        jd=jd,
    )
