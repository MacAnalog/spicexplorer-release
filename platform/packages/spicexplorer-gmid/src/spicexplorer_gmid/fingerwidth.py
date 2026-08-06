"""``FingerWidthSet`` — interpolate gm/ID operating points across **finger width**.

The gm/ID normalised parameters (JD=ID/W, gm/gds, gm/Cgg, C/W, and the solved VGS) are invariant
under adding *identical* fingers — you scale total width via the number of fingers ``m`` — but they
DO depend on the **finger width** itself (narrow-width and wide-finger effects: a 0.5 µm finger and
a 5 µm finger read a few-to-tens of % apart on gm/ID and JD). A single-finger-width :class:`DeviceTable`
is therefore only exact near its characterised finger width.

A :class:`FingerWidthSet` holds one :class:`DeviceTable` per characterised finger width (e.g.
0.5 / 1 / 5 µm) and linearly interpolates the :class:`OperatingPoint` across finger width at a fixed
(gm/ID, L, VDS, VSB). Off the finger-width grid it raises :class:`OutOfGridError` — never
extrapolated, matching the rest of the tool's fail-loud contract.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from os import PathLike

from .contract import OperatingPoint
from .errors import OutOfGridError
from .tables import DeviceTable

#: Round-trip tolerance on a JD→gm/ID inversion, mirroring :meth:`DeviceTable.gm_id_for_jd`'s own
#: ``rel_tol=0.05``. The blended answer has to honour the same contract as the per-table ones it is
#: blended from — otherwise a ``SizedDevice`` sized from the REQUESTED jd disagrees with its own
#: operating point by more than the package's own promise.
_JD_ROUND_TRIP_RTOL = 0.05


def _lerp(a: float, b: float, w: float) -> float:
    return a * (1.0 - w) + b * w


class FingerWidthSet:
    """A device characterised at several finger widths, interpolated in finger width."""

    def __init__(self, tables: Mapping[float, DeviceTable]) -> None:
        if not tables:
            raise ValueError("FingerWidthSet needs at least one DeviceTable")
        self._t: dict[float, DeviceTable] = dict(sorted(tables.items()))
        self.finger_widths: list[float] = list(self._t)

    @classmethod
    def load(cls, paths: Mapping[float, str | PathLike[str]]) -> FingerWidthSet:
        """Build from a ``{finger_width_µm: pkl_path}`` mapping."""
        return cls({float(wf): DeviceTable.load(p) for wf, p in paths.items()})

    def table_at(self, wf: float) -> DeviceTable:
        """The exact :class:`DeviceTable` at a characterised finger width (``KeyError`` if not present)."""
        for w, t in self._t.items():
            if abs(w - wf) < 1e-9:
                return t
        raise KeyError(f"no table at finger width {wf} µm; have {self.finger_widths}")

    def _bracket(self, wf: float) -> tuple[float, float, float]:
        """(wf_lo, wf_hi, weight) bracketing ``wf``; fail loud outside the characterised range."""
        ws = self.finger_widths
        if not (ws[0] - 1e-9 <= wf <= ws[-1] + 1e-9):
            raise OutOfGridError(
                f"finger width {wf:g} µm is outside the characterised set "
                f"[{ws[0]:g}..{ws[-1]:g}] µm — values are never extrapolated. Characterise that "
                f"finger width or move to one in the set {ws}."
            )
        for lo, hi in zip(ws, ws[1:]):
            if lo - 1e-9 <= wf <= hi + 1e-9:
                w = 0.0 if hi == lo else (wf - lo) / (hi - lo)
                return lo, hi, w
        return ws[-1], ws[-1], 0.0  # single-point set, wf == that point

    def at(self, gm_id: float, L: float, vds: float, vsb: float = 0.0, *, wf: float) -> OperatingPoint:
        """The :class:`OperatingPoint` at (gm/ID, L, VDS, VSB) **and finger width ``wf``**.

        Each field is linearly interpolated between the two bracketing finger-width tables (an exact
        table look-up when ``wf`` is on the finger-width grid). The bias-axis / reachability
        fail-loud contract of :meth:`DeviceTable.at` still applies to each underlying table.

        Both endpoint weights fast-path to the single table that carries the answer. Only ``w=0.0``
        used to, so asking for an exactly-characterised width still evaluated its bracket partner
        at weight **zero** — every contribution multiplied out, but its reachability gate live: on
        the production {0.5, 1.0, 5.0} µm sky130 set, ``at(26.4631, …, wf=5.0)`` raised naming the
        1 µm table's band ``[1.23262..25.8991]`` while ``table_at(5.0).at(…)`` answered fine. Same
        object, two answers, and the diagnostic pointed at the wrong table.
        """
        lo, hi, w = self._bracket(wf)
        if hi == lo or w == 0.0:
            return self._t[lo].at(gm_id, L, vds, vsb)
        if w == 1.0:
            return self._t[hi].at(gm_id, L, vds, vsb)
        op_lo = self._t[lo].at(gm_id, L, vds, vsb)
        op_hi = self._t[hi].at(gm_id, L, vds, vsb)
        return OperatingPoint(
            gm_id=gm_id, L=L, vds=vds, vsb=vsb,
            vgs=_lerp(op_lo.vgs, op_hi.vgs, w),
            jd=_lerp(op_lo.jd, op_hi.jd, w),
            av0=_lerp(op_lo.av0, op_hi.av0, w),
            ft=_lerp(op_lo.ft, op_hi.ft, w),
            cgg_w=_lerp(op_lo.cgg_w, op_hi.cgg_w, w),
            cdd_w=_lerp(op_lo.cdd_w, op_hi.cdd_w, w),
        )

    def gm_id_for_jd(self, jd: float, L: float, vds: float, vsb: float = 0.0, *, wf: float) -> float:
        """The gm/ID giving current density ``jd`` [A/µm] at (L, VDS, VSB) **and finger width ``wf``**.

        The finger-width counterpart of :meth:`DeviceTable.gm_id_for_jd` — the weak-inversion entry
        point :func:`~spicexplorer_gmid.size_for_current_density` uses when driven by ``jd=``. Each
        bracketing table is inverted on its own and the two gm/ID answers are interpolated: JD is a
        per-finger-width quantity, so inverting a width-interpolated JD would not give the same
        number. Each underlying inversion keeps its own round-trip fail-loud contract.

        The **blend** is then held to that same contract. Two individually-consistent inversions do
        not lerp into a consistent one — JD runs exponentially in gm/ID through weak inversion, so
        a straight line between them cuts the corner. Measured on the real production
        {0.5, 1.0, 5.0} µm sky130 store, the blended answer missed the requested JD by up to 7.59 %
        at an interior ``wf``, while ``_assemble`` sizes ``W = ID/jd`` from the REQUESTED density
        and ``gm`` from the BLENDED gm/ID — a :class:`~spicexplorer_gmid.SizedDevice` that
        disagreed with its own operating point, gates all green. Re-evaluating :meth:`at` at the
        blended gm/ID and demanding the same 5 % makes the inconsistency loud instead.
        """
        lo, hi, w = self._bracket(wf)
        if hi == lo or w == 0.0:
            return self._t[lo].gm_id_for_jd(jd, L, vds, vsb)
        if w == 1.0:
            return self._t[hi].gm_id_for_jd(jd, L, vds, vsb)
        gm_id = _lerp(
            self._t[lo].gm_id_for_jd(jd, L, vds, vsb),
            self._t[hi].gm_id_for_jd(jd, L, vds, vsb),
            w,
        )
        jd_back = self.at(gm_id, L, vds, vsb, wf=wf).jd
        if not math.isclose(jd_back, jd, rel_tol=_JD_ROUND_TRIP_RTOL):
            raise OutOfGridError(
                f"the finger-width blend at wf={wf:g} µm does not invert consistently: jd={jd:g} "
                f"A/µm inverts to gm/ID={gm_id:g} 1/V between the {lo:g} µm and {hi:g} µm tables "
                f"(weight {w:.4g}), but that gm/ID reads back JD={jd_back:g} A/µm "
                f"({100.0 * abs(jd_back - jd) / jd:.3g} % off, tolerance "
                f"{100.0 * _JD_ROUND_TRIP_RTOL:g} %) at (L={L:g} µm, VDS={vds:g} V, VSB={vsb:g} V)"
                f" — JD is exponential in gm/ID here, so the linear blend of two per-table "
                f"inversions is not itself an inversion. Size at a characterised finger width "
                f"{self.finger_widths} µm, or characterise one nearer {wf:g} µm — values are never "
                f"silently reconciled."
            )
        return gm_id
