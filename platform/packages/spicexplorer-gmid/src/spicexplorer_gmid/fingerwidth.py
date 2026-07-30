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

from collections.abc import Mapping
from os import PathLike

from .contract import OperatingPoint
from .errors import OutOfGridError
from .tables import DeviceTable


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
        """
        lo, hi, w = self._bracket(wf)
        op_lo = self._t[lo].at(gm_id, L, vds, vsb)
        if hi == lo or w == 0.0:
            return op_lo
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
