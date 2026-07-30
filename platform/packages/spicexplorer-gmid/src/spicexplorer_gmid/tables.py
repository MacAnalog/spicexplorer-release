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
        reachability contract is enforced in :meth:`at` via the solved-VGS range check. Use
        :meth:`at` for sizing; this passthrough is a raw escape hatch.
        """
        self._require_axes_in_grid(kwargs)  # fail loud on off-grid bias axes (no silent extrapolation)
        val = _scalar(self._lut.look_up(out, **kwargs))
        if not math.isfinite(val):
            raise OutOfGridError(self._grid_msg(out, kwargs))
        return val

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

    def at(self, gm_id: float, L: float, vds: float, vsb: float = 0.0) -> OperatingPoint:
        """The full :class:`OperatingPoint` at one (gm/ID, L, VDS, VSB).

        ``gm_id`` selects the inversion level; pygmid inverts the GM_ID-vs-VGS locus for VGS and
        reads JD, gm/gds, gm/Cgg, and the cap densities at that point. Fail-loud: the bias axes
        must lie within the grid, and the **solved VGS must land inside the characterized VGS
        range** — an unreachable gm/ID otherwise yields finite-but-garbage values (negative caps,
        VGS in the GV range), the pitfall the gmid-skills warn about.
        """
        self._require_in_grid("L", L, self.L_grid)
        self._require_in_grid("VDS", vds, self.VDS_grid)
        self._require_in_grid("VSB", vsb, self.VSB_grid)

        vgs = _scalar(self._lut.look_upVGS(GM_ID=gm_id, VDS=vds, VSB=vsb, L=L))
        vlo, vhi = float(self.VGS_grid.min()), float(self.VGS_grid.max())
        if not (math.isfinite(vgs) and vlo <= vgs <= vhi):
            raise OutOfGridError(
                f"gm/ID={gm_id:g} 1/V is unreachable at (L={L:g} µm, VDS={vds:g} V, VSB={vsb:g} V): "
                f"the solved VGS={vgs:g} V is outside the characterized VGS range {_rng(self.VGS_grid)} V. "
                f"Lower the target gm/ID or move the bias — values are never extrapolated/clamped."
            )

        bias = dict(VDS=vds, VSB=vsb, L=L)
        jd = self.look_up("ID_W", GM_ID=gm_id, **bias)
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
        """gm/ID trade-off arrays over ``gm_id=(lo, hi)`` at fixed (L, VDS, VSB)."""
        lo, hi = gm_id
        grid = np.linspace(lo, hi, n)
        bias = dict(VDS=vds, VSB=vsb, L=L)
        self._require_axes_in_grid(bias)  # fail loud on off-grid bias axes (no silent extrapolation)
        jd = np.asarray(self._lut.look_up("ID_W", GM_ID=grid, **bias), dtype=float).reshape(-1)
        av0 = np.asarray(self._lut.look_up("GM_GDS", GM_ID=grid, **bias), dtype=float).reshape(-1)
        wt = np.asarray(self._lut.look_up("GM_CGG", GM_ID=grid, **bias), dtype=float).reshape(-1)
        vgs = np.asarray(
            self._lut.look_upVGS(GM_ID=grid, VDS=vds, VSB=vsb, L=L), dtype=float
        ).reshape(-1)
        return Sweep(gm_id=grid, jd=jd, ft=wt / TWO_PI, av0=av0, vgs=vgs, L=L, vds=vds, vsb=vsb)
