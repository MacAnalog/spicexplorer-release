"""The gm/ID sizing flows: pick an inversion level (gm/ID) and length, read JD off the table, and
de-normalise a transconductance or a bias current into a width.

The two entry points are the same lookup approached from opposite ends:

* :func:`size_for_gm` — *gm-first* (the canonical 5-step): you have a gm spec (e.g. from a target
  GBW and load), choose gm/ID and L, then ``ID = gm / (gm/ID)`` and ``W = ID / JD``.
* :func:`size_for_current_density` — *current-first / JD flow*: you fix the bias current (head-room
  / power budget) and the inversion level, then ``W = ID / JD`` and ``gm = (gm/ID)·ID``.

Both attach a :class:`~spicexplorer_gmid.contract.SizedDevice` carrying the operating point and a
ledger of pass/fail sanity gates (saturation head-room, geometry envelope, finite intrinsic
gain/fT). Nothing is silently clamped — an off-grid request raises from the table layer.
"""

from __future__ import annotations

import math

from .contract import GeometryBounds, OperatingPoint, SanityGate, SizedDevice
from .errors import GmidError
from .tables import DeviceTable


def _fingers(w_total: float, wf_max: float | None) -> int:
    """Number of fingers so each is ≤ ``wf_max`` µm (1 if no max is given)."""
    if wf_max is None or wf_max <= 0:
        return 1
    return max(1, math.ceil(w_total / wf_max))


def _gates(
    op: OperatingPoint, w_total: float, nf: int, bounds: GeometryBounds | None
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
    jd: float | None = None,
) -> SizedDevice:
    # Width from current density. When the caller specified a target JD (the JD-first flow), size to
    # THAT density; otherwise use the table value at the chosen gm/ID. (They agree to the LUT's
    # forward/inverse interpolation tolerance.)
    w_total = ID / (jd if jd is not None else op.jd)
    nf = _fingers(w_total, wf_max)
    return SizedDevice(
        W=w_total,
        L=op.L,
        nf=nf,
        ID=ID,
        gm=gm,
        cgg=op.cgg_w * w_total,
        cdd=op.cdd_w * w_total,
        op=op,
        gates=_gates(op, w_total, nf, bounds),
    )


def size_for_gm(
    table: DeviceTable,
    *,
    gm: float,
    gm_id: float,
    L: float,
    vds: float,
    vsb: float = 0.0,
    wf_max: float | None = None,
    bounds: GeometryBounds | None = None,
) -> SizedDevice:
    """Size a device to a transconductance target (the canonical gm-first 5-step flow).

    ``ID = gm / (gm/ID)`` sets the bias current, then ``W = ID / JD`` from the table's current
    density. ``gm`` in S, ``gm_id`` in 1/V, ``L`` in µm, voltages in V.
    """
    op = table.at(gm_id, L, vds, vsb)
    ID = gm / gm_id
    return _assemble(op, ID=ID, gm=gm, wf_max=wf_max, bounds=bounds)


def size_for_current_density(
    table: DeviceTable,
    *,
    ID: float,
    gm_id: float | None = None,
    jd: float | None = None,
    L: float,
    vds: float,
    vsb: float = 0.0,
    wf_max: float | None = None,
    bounds: GeometryBounds | None = None,
) -> SizedDevice:
    """Size a device from a fixed bias current and inversion level (current-first / JD flow).

    Give **exactly one** of ``gm_id`` (1/V) or ``jd`` (current density A/µm — the weak-inversion
    knob, where gm/ID plateaus). ``W = ID / JD`` from the table; ``gm = (gm/ID)·ID`` falls out.
    """
    if (gm_id is None) == (jd is None):
        raise GmidError("size_for_current_density needs exactly one of gm_id or jd")
    if jd is not None:
        gm_id = table.gm_id_for_jd(jd, L, vds, vsb)
    if gm_id is None:  # unreachable (guarded above) but narrows the type for pyright
        raise GmidError("gm_id unresolved")
    op = table.at(gm_id, L, vds, vsb)
    gm = gm_id * ID
    return _assemble(op, ID=ID, gm=gm, wf_max=wf_max, bounds=bounds, jd=jd)
