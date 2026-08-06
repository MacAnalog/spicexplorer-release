"""``DeviceTable`` — a typed, fail-loud wrapper over a pygmid ``Lookup`` LUT.

The committed LUTs (analog-db ``_shared/gmid/<pdk>/<device>__<corner>.pkl``) are pygmid's
dict-of-arrays format: four monotonic bias axes ``L`` (µm), ``VGS``, ``VDS``, ``VSB`` (V) and a 4-D
array per stored parameter (``ID VT GM GMB GDS CGG CGS CGD CDD …``), plus headers
``INFO CORNER TEMP NFING W``. pygmid does the multilinear interpolation and the ``GM_ID`` ratio
cross-lookups; this class adds units, an ``OperatingPoint`` view, and the no-silent-clamp contract.

The tool depends on ``pygmid`` (proven against our LUTs) — never on ``spicexplorer_analog_db``; a
``DeviceTable`` is constructed from a *path* or an already-loaded ``Lookup``, so it is decoupled
from where the data lives (plan_gmid_sizing.md §2: data-driven, no DB import).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

import numpy as np
from pygmid import Lookup

from .contract import LUTManifest, OperatingPoint
from .errors import OutOfGridError

TWO_PI = 2.0 * math.pi


def _scalar(value: object) -> float:
    """Coerce a pygmid lookup result to a Python float (it may return a 0-d/1-elem ndarray)."""
    arr = np.asarray(value, dtype=float).reshape(-1)
    if arr.size != 1:
        raise ValueError(f"expected a scalar lookup result, got shape {np.asarray(value).shape}")
    return float(arr[0])


def _rng(a: np.ndarray) -> str:
    """Format an axis vector as ``[min..max] (n=…)`` for grid-bounds error messages."""
    return f"[{a.min():.4g}..{a.max():.4g}] (n={a.size})"


@dataclass(frozen=True)
class Sweep:
    """gm/ID trade-off curves at fixed (L, VDS, VSB) — the exploration view (book Fig. style).

    Arrays are aligned 1-D over ``gm_id``; ``jd`` is A/µm, ``ft`` Hz, ``av0`` and ``gm_id`` are
    dimensionless/[1/V], ``vgs`` V.
    """

    gm_id: np.ndarray
    jd: np.ndarray
    ft: np.ndarray
    av0: np.ndarray
    vgs: np.ndarray
    L: float
    vds: float
    vsb: float


class DeviceTable:
    """Typed access to one characterized device LUT."""

    def __init__(
        self,
        lut: Lookup,
        *,
        source: Path | None = None,
        manifest: LUTManifest | None = None,
    ) -> None:
        self._lut = lut
        self.source = source
        self._manifest = manifest

    @classmethod
    def load(cls, path: str | PathLike[str]) -> DeviceTable:
        """Load a pygmid ``.pkl`` LUT from disk.

        If a ``<stem>.manifest.json`` sidecar exists next to the ``.pkl``, it is loaded
        automatically and attached as :attr:`manifest` — no separate call needed.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"LUT not found: {p}")
        man: LUTManifest | None = None
        sidecar = p.parent / (p.stem + ".manifest.json")
        if sidecar.is_file():
            try:
                man = LUTManifest.from_path(sidecar)
            except Exception:
                pass  # corrupt sidecar → skip silently; don't fail the load
        return cls(Lookup(str(p)), source=p, manifest=man)

    @property
    def manifest(self) -> LUTManifest | None:
        """The manifest sidecar (run dimensions + exact model + provenance), or ``None`` if absent."""
        return self._manifest

    # ----- raw handle + axes/headers -------------------------------------------------------

    @property
    def lut(self) -> Lookup:
        """The underlying pygmid ``Lookup`` (escape hatch for advanced cross-lookups)."""
        return self._lut

    def _axis(self, name: str) -> np.ndarray:
        return np.asarray(self._lut[name], dtype=float)

    @property
    def L_grid(self) -> np.ndarray:
        return self._axis("L")

    @property
    def VGS_grid(self) -> np.ndarray:
        return self._axis("VGS")

    @property
    def VDS_grid(self) -> np.ndarray:
        return self._axis("VDS")

    @property
    def VSB_grid(self) -> np.ndarray:
        return self._axis("VSB")

    @property
    def info(self) -> str:
        return str(self._lut["INFO"])

    @property
    def corner(self) -> str:
        return str(self._lut["CORNER"])

    @property
    def temp(self) -> float:
        return _scalar(self._lut["TEMP"])

    @property
    def w_char(self) -> float:
        """Characterization width [µm] (the W the LUT was extracted at)."""
        return _scalar(self._lut["W"])

    # ----- lookups -------------------------------------------------------------------------

    def look_up(self, out: str, **kwargs: object) -> float:
        """Scalar lookup with NaN→error. ``out`` is a stored param or an ``'A_B'`` ratio.

        Raises :class:`OutOfGridError` when a bias axis is off-grid (pygmid would extrapolate
        silently) or the result is NaN. **Caveat:** off the valid GM_ID branch pygmid returns
        finite *garbage* (a printed warning, not a NaN), so isfinite alone is not enough — the
        reachability contract is enforced in :meth:`at` / :meth:`sweep` via the gm/ID-branch gate
        (:meth:`gm_id_band`). Use :meth:`at` for sizing; this passthrough is a raw escape hatch.
        """
        self._require_axes_in_grid(kwargs)  # fail loud on off-grid bias axes (no silent extrapolation)
        val = _scalar(self._look_up_raw(out, kwargs))
        if not math.isfinite(val):
            raise OutOfGridError(self._grid_msg(out, kwargs))
        return val

    def _look_up_raw(self, out: str, coords: Mapping[str, object]) -> np.ndarray:
        """``Lookup.look_up`` with scipy's bare ``ValueError`` translated into ``OutOfGridError``.

        Every *ratio-keyed* lookup (``GM_ID=…`` / ``ID_W=…``) makes pygmid build a pchip over the
        slice's VGS locus. On a slice that carries no current the locus is flat/non-finite and
        scipy raises a bare ``ValueError`` from deep inside ``_cubic.py`` — outside this package's
        documented error hierarchy, with no mention of the bias point that caused it. VDS=0 is a
        legal grid point on every PDK sweep and degenerates exactly this way (ID→0 at every VGS).
        """
        try:
            return np.asarray(self._lut.look_up(out, **coords), dtype=float).reshape(-1)
        except ValueError as exc:
            raise OutOfGridError(self._degenerate_msg(out, coords)) from exc

    def _look_up_vgs_raw(self, gm_id: float | np.ndarray, L: float, vds: float, vsb: float) -> np.ndarray:
        """``Lookup.look_upVGS`` with the same bare-``ValueError`` translation as :meth:`_look_up_raw`."""
        coords: dict[str, object] = dict(GM_ID=gm_id, VDS=vds, VSB=vsb, L=L)
        try:
            return np.asarray(self._lut.look_upVGS(**coords), dtype=float).reshape(-1)
        except ValueError as exc:
            raise OutOfGridError(self._degenerate_msg("VGS", coords)) from exc

    def _grid_msg(self, out: str, kwargs: object) -> str:
        return (
            f"lookup of {out!r} at {kwargs} is off the characterized grid (or off the valid GM_ID "
            f"branch). Grid: L={_rng(self.L_grid)} µm, VGS={_rng(self.VGS_grid)} V, "
            f"VDS={_rng(self.VDS_grid)} V, VSB={_rng(self.VSB_grid)} V. Re-grid the LUT or move the "
            f"operating point — values are never extrapolated/clamped."
        )

    def _require_in_grid(self, name: str, value: float, grid: np.ndarray) -> None:
        # pygmid extrapolates silently outside the bias grid → guard before any lookup.
        lo, hi = float(grid.min()), float(grid.max())
        if not (lo <= value <= hi):
            raise OutOfGridError(
                f"{name}={value:g} is outside the characterized grid {_rng(grid)} — values are "
                f"never extrapolated. Re-grid the LUT or move the operating point."
            )

    # Coordinate keys that are characterized bias axes (as opposed to derived inputs like GM_ID /
    # ID_W, which have no grid and are covered by the NaN / reachability checks instead).
    _AXIS_GRIDS = ("L", "VGS", "VDS", "VSB")

    def _require_axes_in_grid(self, coords: Mapping[str, object]) -> None:
        """Bounds-check every characterized bias axis present in a lookup's coordinates.

        pygmid silently EXTRAPOLATES off the bias grid (finite garbage, not NaN), so any public
        lookup that forwards caller coordinates to pygmid must gate the physical axes first — the
        same guard :meth:`at` applies. ``look_up`` and ``sweep`` previously skipped it while the
        README promises ``OutOfGridError``. Handles scalar or array axis values (a swept axis).
        """
        for name in self._AXIS_GRIDS:
            if name not in coords:
                continue
            grid = self._axis(name)
            arr = np.atleast_1d(np.asarray(coords[name], dtype=float))
            # The extremes decide it: an out-of-grid min or max means at least one query point
            # would be extrapolated. Reuse _require_in_grid so the message matches at()'s.
            self._require_in_grid(name, float(arr.min()), grid)
            self._require_in_grid(name, float(arr.max()), grid)

    # ----- degenerate-slice diagnosis (which axis killed the interpolant) -------------------

    def _slice_carries_current(self, L: float, vds: float, vsb: float) -> bool:
        """True when the (L, VDS, VSB) slice has a usable ID/W locus across the whole VGS grid.

        A plain (non-ratio) lookup, so it never builds a pchip and never raises — it is the probe
        the error path uses to decide *why* a ratio lookup could not be interpolated, and the first
        check :meth:`gm_id_band` makes.

        "Usable" means the locus actually **varies**: more than one distinct positive sample. A
        single non-zero point is not a current locus, it is float underflow — measured on the
        committed sky130 fixture, three VDS=0 slices carry exactly one denormal sample
        (8.9e-45 / 1.1e-44 / 3.8e-56 A/µm at one VGS node and an exact 0 at the other 36), so a
        bare ``max(locus) > 0`` called them alive and handed back a gm/ID band for a dead slice.
        No magnitude threshold is involved — the test is on the *shape* of the locus, so it needs
        no per-PDK tuning.
        """
        locus = np.asarray(
            self._lut.look_up("ID_W", VGS=self.VGS_grid, VDS=vds, VSB=vsb, L=L), dtype=float
        ).reshape(-1)
        if not bool(np.all(np.isfinite(locus))):
            return False
        return int(np.unique(locus[locus > 0.0]).size) > 1

    def _degenerate_axis(self, L: float, vds: float, vsb: float) -> str | None:
        """The single bias axis whose value makes this slice carry no current, if any.

        Found by construction, not by assumption: the slice is re-probed with that one axis moved
        to each of its other grid points, and the axis that restores a usable ID/W locus is the
        culprit. VDS is tried first because VDS=0 is the case that actually occurs (ID→0 at every
        VGS, for every L and VSB). Returns ``None`` when the slice is fine, or when no single-axis
        move rescues it.
        """
        if self._slice_carries_current(L, vds, vsb):
            return None
        bias = {"L": L, "VDS": vds, "VSB": vsb}
        for name, grid in (("VDS", self.VDS_grid), ("L", self.L_grid), ("VSB", self.VSB_grid)):
            for alt in grid:
                probe = dict(bias, **{name: float(alt)})
                if self._slice_carries_current(probe["L"], probe["VDS"], probe["VSB"]):
                    return name
        return None

    def _degenerate_msg(self, out: str, coords: Mapping[str, object]) -> str:
        """Error text for a lookup scipy could not interpolate, naming the offending bias axis."""
        try:
            bias = {
                k: float(np.asarray(coords[k], dtype=float).reshape(-1)[0])
                for k in ("L", "VDS", "VSB")
            }
        except (KeyError, TypeError, ValueError):
            return self._grid_msg(out, coords)
        axis = self._degenerate_axis(bias["L"], bias["VDS"], bias["VSB"])
        if axis is None:
            return self._grid_msg(out, coords)
        return (
            f"lookup of {out!r} at {dict(coords)} could not be interpolated: the bias slice "
            f"(L={bias['L']:g} µm, VDS={bias['VDS']:g} V, VSB={bias['VSB']:g} V) carries no "
            f"current — {axis}={bias[axis]:g} is the offending axis (at that value the ID/W locus "
            f"is flat/non-finite across the whole VGS grid, so pygmid's ratio interpolant cannot "
            f"be built). {axis} grid: {_rng(self._axis(axis))}. Move {axis} off that point — "
            f"values are never extrapolated/clamped."
        )

    # ----- gm/ID reachability (the monotonic branch) ----------------------------------------

    def gm_id_band(self, L: float, vds: float, vsb: float = 0.0) -> tuple[float, float, float]:
        """The reachable gm/ID interval of one (L, VDS, VSB) slice, as ``(lo, hi, vgs_peak)``.

        gm/ID is **not** monotonic in VGS: from the top of the VGS grid it climbs towards weak
        inversion, peaks, then collapses again as the device turns off and the extracted gm/ID
        degenerates. pygmid inverts **only the falling branch** ``curve[argmax:]``
        (``Lookup.look_upVGS``) and *pchip-extrapolates* past its ends — finite garbage with a
        printed warning, never a NaN — so that branch, not the VGS grid, is the reachability
        domain every guard must use. ``hi`` is the weak-inversion peak (the maximum gm/ID this
        slice can deliver), ``lo`` the value at the top of the VGS grid, ``vgs_peak`` the VGS the
        peak sits at.

        Fail-loud like :meth:`at`: the three bias axes are bounds-checked first (pygmid
        pchip-*extrapolates* off the bias grid — an ungated ``L=1e6`` used to return a confident
        band of ``(-666233, 166965)`` instead of raising), then the slice must actually carry
        current, and the resulting interval must be strictly positive. A gm/ID band is a physical
        interval: a non-positive lower bound is not a usable one.

        Raises :class:`OutOfGridError` if the slice has no usable branch — VDS=0 degenerates
        (ID→0), and the two fixtures show both shapes of that: the IHP table leaves gm/ID
        non-finite there, the sky130 one an all-zero curve (bar float underflow at a single VGS
        node, which is why :meth:`_slice_carries_current` is the gate rather than the curve max).
        """
        self._require_in_grid("L", L, self.L_grid)
        self._require_in_grid("VDS", vds, self.VDS_grid)
        self._require_in_grid("VSB", vsb, self.VSB_grid)
        if not self._slice_carries_current(L, vds, vsb):
            raise OutOfGridError(
                f"the gm/ID-vs-VGS locus at (L={L:g} µm, VDS={vds:g} V, VSB={vsb:g} V) has no "
                f"usable branch: the slice carries no current (its ID/W locus is flat/non-finite "
                f"across the whole VGS grid — VDS=0 degenerates that way, ID→0). Re-grid the LUT "
                f"or move the bias; values are never extrapolated/clamped."
            )
        curve = self._look_up_raw(
            "GM_ID", dict(VGS=self.VGS_grid, VDS=vds, VSB=vsb, L=L)
        )
        finite = np.isfinite(curve)
        top = int(np.argmax(np.where(finite, curve, -np.inf))) if finite.any() else 0
        branch, vgs_branch = curve[top:], self.VGS_grid[top:]
        if (
            not finite.any()
            or branch.size < 2
            or not np.all(np.isfinite(branch))
            or float(branch.min()) <= 0.0
        ):
            usable = branch[np.isfinite(branch)]
            floor = float(usable.min()) if usable.size else float("nan")
            raise OutOfGridError(
                f"the gm/ID-vs-VGS locus at (L={L:g} µm, VDS={vds:g} V, VSB={vsb:g} V) has no "
                f"usable branch (spans {floor:g}..{curve[top]:g} 1/V, peak at "
                f"VGS={self.VGS_grid[top]:g} V over {branch.size} points; a band must be a "
                f"strictly positive interval) — this slice is not characterized (VDS=0 "
                f"degenerates: ID→0). Re-grid the LUT or move the bias; values are never "
                f"extrapolated/clamped."
            )
        return float(branch.min()), float(branch.max()), float(vgs_branch[0])

    # Relative width of the float-noise band around the VGS grid ends. The solved-VGS check is a
    # BACKSTOP on an interpolation artifact, not a second reachability opinion: :meth:`gm_id_band`
    # already certifies the request against the branch pygmid actually inverts, and that inversion
    # is a pchip solve whose answer at the band edge lands a few ULP outside the grid. Measured on
    # the committed sky130 fixture (whose gm/ID peaks at the VGS=0 grid EDGE on every slice), the
    # band maximum solves to VGS = -4.33681e-18 V against a [0..1.8] V grid — untoleranced, that
    # bounced the very value the band gate had just declared reachable on 62 of 147 slices, and
    # 28 of 73 band-edge sweeps with it. Scaled by the grid span so it stays float noise on any
    # LUT; anything further out than this still raises (it is a genuine extrapolation).
    _VGS_EDGE_RTOL = 1e-9

    def _snap_vgs_to_grid(self, vgs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """``(VGS snapped onto the grid ends, off-grid mask)`` for solved-VGS values.

        Excursions within :data:`_VGS_EDGE_RTOL`·span are float noise and are clipped onto the end
        they overshot (so a returned :class:`OperatingPoint` never reports a physically-impossible
        ``VGS=-4e-18 V``); anything beyond it is flagged, never clamped.
        """
        vlo, vhi = float(self.VGS_grid.min()), float(self.VGS_grid.max())
        tol = self._VGS_EDGE_RTOL * (vhi - vlo)
        arr = np.asarray(vgs, dtype=float)
        off = ~np.isfinite(arr) | (arr < vlo - tol) | (arr > vhi + tol)
        return np.clip(arr, vlo, vhi), off

    def _require_gm_id_reachable(
        self, gm_id: float | np.ndarray, L: float, vds: float, vsb: float
    ) -> None:
        """Gate a scalar gm/ID (or a whole swept vector) against the slice's monotonic branch.

        The band is an interval, so testing the extremes covers every point of a sweep. This is
        the guard the README's "never silently extrapolates" promise rests on: checking only that
        the *solved VGS* lands inside the VGS grid is not enough, because on a slice whose gm/ID
        peaks at an **interior** VGS an above-peak (unreachable) request solves back to a VGS that
        is perfectly inside the grid — and pygmid then hands back finite garbage (negative JD,
        negative widths) that passes every downstream sanity gate.
        """
        lo, hi, vgs_peak = self.gm_id_band(L, vds, vsb)
        arr = np.atleast_1d(np.asarray(gm_id, dtype=float))
        for value in (float(arr.min()), float(arr.max())):
            if math.isfinite(value) and lo <= value <= hi:
                continue
            raise OutOfGridError(
                f"gm/ID={value:g} 1/V is unreachable at (L={L:g} µm, VDS={vds:g} V, VSB={vsb:g} V): "
                f"the characterized gm/ID branch spans [{lo:.6g}..{hi:.6g}] 1/V (gm/ID is NOT "
                f"monotonic in VGS — it peaks at {hi:.6g} 1/V at VGS={vgs_peak:g} V and only the "
                f"falling branch above that VGS is invertible). Lower the target gm/ID or move the "
                f"bias — values are never extrapolated/clamped."
            )

    def at(self, gm_id: float, L: float, vds: float, vsb: float = 0.0) -> OperatingPoint:
        """The full :class:`OperatingPoint` at one (gm/ID, L, VDS, VSB).

        ``gm_id`` selects the inversion level; pygmid inverts the GM_ID-vs-VGS locus for VGS and
        reads JD, gm/gds, gm/Cgg, and the cap densities at that point. Fail-loud: the bias axes
        must lie within the grid, the target must lie on the slice's **invertible gm/ID branch**
        (:meth:`gm_id_band`), the solved VGS must land inside the characterized VGS range, and the
        resulting current density must be finite and positive — an unreachable gm/ID otherwise
        yields finite-but-garbage values (negative JD/caps, a GV-range VGS), the pitfall the
        gmid-skills warn about.
        """
        self._require_in_grid("L", L, self.L_grid)
        self._require_in_grid("VDS", vds, self.VDS_grid)
        self._require_in_grid("VSB", vsb, self.VSB_grid)
        self._require_gm_id_reachable(gm_id, L, vds, vsb)

        vgs_raw = _scalar(self._look_up_vgs_raw(gm_id, L, vds, vsb))
        snapped, off_grid = self._snap_vgs_to_grid(np.asarray([vgs_raw]))
        if bool(off_grid[0]):
            raise OutOfGridError(
                f"gm/ID={gm_id:g} 1/V is unreachable at (L={L:g} µm, VDS={vds:g} V, VSB={vsb:g} V): "
                f"the solved VGS={vgs_raw:g} V is outside the characterized VGS range {_rng(self.VGS_grid)} V. "
                f"Lower the target gm/ID or move the bias — values are never extrapolated/clamped."
            )
        vgs = float(snapped[0])

        bias = dict(VDS=vds, VSB=vsb, L=L)
        jd = self.look_up("ID_W", GM_ID=gm_id, **bias)
        if jd <= 0.0:
            raise OutOfGridError(
                f"the current density read at gm/ID={gm_id:g} 1/V, (L={L:g} µm, VDS={vds:g} V, "
                f"VSB={vsb:g} V) is JD={jd:g} A/µm — a non-positive JD is unphysical (the LUTs "
                f"store |ID| for both polarities) and means pygmid extrapolated off the "
                f"characterized branch. {self._grid_msg('ID_W', bias)}"
            )
        av0 = self.look_up("GM_GDS", GM_ID=gm_id, **bias)
        gm_cgg = self.look_up("GM_CGG", GM_ID=gm_id, **bias)  # ωT = gm/Cgg [rad/s]
        cgg_w = self.look_up("CGG_W", GM_ID=gm_id, **bias)
        cdd_w = self.look_up("CDD_W", GM_ID=gm_id, **bias)
        return OperatingPoint(
            gm_id=gm_id,
            L=L,
            vds=vds,
            vsb=vsb,
            vgs=vgs,
            jd=jd,
            av0=av0,
            ft=gm_cgg / TWO_PI,
            cgg_w=cgg_w,
            cdd_w=cdd_w,
        )

    def gm_id_for_jd(self, jd: float, L: float, vds: float, vsb: float = 0.0) -> float:
        """Inverse lookup: the gm/ID that yields current density ``jd`` [A/µm] at (L, VDS, VSB).

        The **weak-inversion entry point** — in weak inversion gm/ID plateaus (~25-30 1/V), so
        many densities map to nearly the same gm/ID and JD is the better-resolving knob. Validated
        by a round trip: the gm/ID is rejected (``OutOfGridError``) if it does not re-produce ``jd``,
        which catches an off-grid target where pygmid would otherwise hand back garbage.
        """
        self._require_in_grid("L", L, self.L_grid)
        self._require_in_grid("VDS", vds, self.VDS_grid)
        self._require_in_grid("VSB", vsb, self.VSB_grid)
        bias = dict(VDS=vds, VSB=vsb, L=L)
        gm_id = self.look_up("GM_ID", ID_W=jd, **bias)
        jd_back = self.look_up("ID_W", GM_ID=gm_id, **bias)
        if gm_id <= 0 or not math.isclose(jd_back, jd, rel_tol=0.05):
            raise OutOfGridError(
                f"jd={jd:g} A/µm does not invert consistently at (L={L:g}, VDS={vds:g}, "
                f"VSB={vsb:g}) — off the characterized current-density range. {self._grid_msg('GM_ID', bias)}"
            )
        return gm_id

    def sweep(
        self,
        *,
        gm_id: tuple[float, float] = (5.0, 25.0),
        L: float,
        vds: float,
        vsb: float = 0.0,
        n: int = 41,
    ) -> Sweep:
        """gm/ID trade-off arrays over ``gm_id=(lo, hi)`` at fixed (L, VDS, VSB).

        Fail-loud like :meth:`at`: the bias axes must be on-grid **and** the whole swept range must
        lie on the slice's invertible gm/ID branch (:meth:`gm_id_band`). Sweeping past the
        reachable maximum used to hand back finite garbage (a VGS tail in the kilovolts, a
        non-monotonic JD) because this path talked to the raw pygmid handle directly.
        """
        lo, hi = gm_id
        grid = np.linspace(lo, hi, n)
        bias = dict(VDS=vds, VSB=vsb, L=L)
        self._require_axes_in_grid(bias)  # fail loud on off-grid bias axes (no silent extrapolation)
        self._require_gm_id_reachable(grid, L, vds, vsb)
        jd = self._look_up_raw("ID_W", dict(GM_ID=grid, **bias))
        av0 = self._look_up_raw("GM_GDS", dict(GM_ID=grid, **bias))
        wt = self._look_up_raw("GM_CGG", dict(GM_ID=grid, **bias))
        vgs_raw = self._look_up_vgs_raw(grid, L, vds, vsb)
        # Same float-noise tolerance as at(): the band gate has already certified the whole
        # linspace, so an end point landing a few ULP outside the VGS grid is the pchip inversion's
        # rounding, not an extrapolation. Untoleranced it rejected 28 of 73 band-edge sweeps.
        vgs, vgs_off_grid = self._snap_vgs_to_grid(vgs_raw)
        bad = (
            ~np.isfinite(jd)
            | ~np.isfinite(av0)
            | ~np.isfinite(wt)
            | (jd <= 0.0)
            | vgs_off_grid
        )
        if bool(bad.any()):
            i = int(np.argmax(bad))
            raise OutOfGridError(
                f"the sweep point gm/ID={grid[i]:g} 1/V at (L={L:g} µm, VDS={vds:g} V, "
                f"VSB={vsb:g} V) read back JD={jd[i]:g} A/µm, VGS={vgs_raw[i]:g} V — non-finite, "
                f"non-positive or off the characterized VGS range {_rng(self.VGS_grid)} V, i.e. "
                f"pygmid extrapolated. Narrow the gm/ID range or re-grid the LUT — values are "
                f"never extrapolated/clamped."
            )
        return Sweep(gm_id=grid, jd=jd, ft=wt / TWO_PI, av0=av0, vgs=vgs, L=L, vds=vds, vsb=vsb)
