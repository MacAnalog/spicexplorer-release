"""Python port of lookup.m / lookupVGS.m (Jespers & Murmann, Appendix 2).

LEGACY REFERENCE — superseded by `pygmid.Lookup` and the platform wrapper
`spicexplorer_gmid.DeviceTable` (.pkl tables, fail-loud; see SKILL.md and
references/lookup-api.md). Kept as a self-contained numpy/scipy port for
offline use with the older .npz table format.

Table format (.npz):
    axis vectors : L (um), VGS (V), VDS (V), VSB (V)   -- monotonic increasing
    4-D arrays   : ID VT GM GMB GDS CGG CGS CSG CGD CDG CGB CDD CSS STH SFL
                   indexed [iL, iVGS, iVDS, iVSB]
    header       : INFO, CORNER, TEMP, NFING, W (characterization width, um)

Conventions: W/L in microns, all electrical quantities in unscaled SI.
Ratios ending in `_W` are per micron of the characterization width.
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy.interpolate import PchipInterpolator, RegularGridInterpolator

AXES = ("L", "VGS", "VDS", "VSB")
# Ratios whose non-monotonic VGS branch is trimmed automatically in mode 3.
_TRIM_RIGHT_OF_MAX = {"GM_ID"}            # keep right of max (drop low-VGS artifact)
_TRIM_LEFT_OF_MAX = {"GM_CGG", "GM_CGS"}  # keep left of max (mobility degradation)


def load_table(path: str) -> dict:
    """Load an .npz lookup table into a plain dict of numpy arrays/scalars."""
    raw = np.load(path, allow_pickle=True)
    return {k: raw[k] for k in raw.files}


# --------------------------------------------------------------------------- #
# internals
# --------------------------------------------------------------------------- #
def _defaults(data: dict) -> dict:
    return {
        "L": float(np.min(data["L"])),
        "VGS": np.asarray(data["VGS"], dtype=float),
        "VDS": float(np.max(data["VDS"])) / 2.0,
        "VSB": 0.0,
    }


def _interp_param(data: dict, name: str, pts: dict) -> np.ndarray:
    """Multilinear interpolation of one stored parameter at the given axis
    points. Vector axes broadcast on an 'ij' meshgrid; singleton axes are
    squeezed out."""
    if name.endswith("_W") and name[:-2] in data:
        return _interp_param(data, name[:-2], pts) / float(data["W"])
    if name not in data:
        raise KeyError(f"parameter {name!r} not stored in table")
    grid = tuple(np.asarray(data[a], dtype=float) for a in AXES)
    itp = RegularGridInterpolator(
        grid, np.asarray(data[name], dtype=float),
        method="linear", bounds_error=True,
    )
    vals = [np.atleast_1d(np.asarray(pts[a], dtype=float)) for a in AXES]
    mesh = np.meshgrid(*vals, indexing="ij")
    out = itp(np.stack([m.ravel() for m in mesh], axis=-1)).reshape(mesh[0].shape)
    return np.squeeze(out)


def _eval(data: dict, outvar: str, pts: dict) -> np.ndarray:
    """Mode 1/2 evaluation: plain parameter or A_B ratio."""
    if outvar in data or (outvar.endswith("_W") and outvar[:-2] in data):
        return _interp_param(data, outvar, pts)
    if "_" in outvar:
        num, den = outvar.split("_", 1)
        return _interp_param(data, num, pts) / _interp_param(data, den, pts)
    raise KeyError(f"unknown output variable {outvar!r}")


def _trim(name: str, x: np.ndarray, ys: list[np.ndarray]) -> tuple:
    """Cut the spurious branch of a known non-monotonic ratio-vs-VGS curve."""
    if name in _TRIM_RIGHT_OF_MAX:
        i = int(np.nanargmax(x))
        return x[i:], [y[i:] for y in ys]
    if name in _TRIM_LEFT_OF_MAX:
        i = int(np.nanargmax(x))
        return x[: i + 1], [y[: i + 1] for y in ys]
    if np.any(np.diff(x) <= 0):
        raise ValueError(
            f"lookup: multiple curve intersections possible for X-variable "
            f"{name!r}; restrict the search range by passing an explicit "
            f"VGS vector, e.g. VGS=data['VGS'][10:]"
        )
    return x, ys


def _invert(x: np.ndarray, y: np.ndarray, xq, method: str, warning: bool,
            label: str) -> np.ndarray:
    """Final 1-D inversion (pchip default), NaN + warning out of range."""
    order = np.argsort(x)
    x, y = x[order], y[order]
    keep = np.isfinite(x) & np.isfinite(y)
    x, y = x[keep], y[keep]
    uniq = np.concatenate(([True], np.diff(x) > 0))   # strictly increasing
    x, y = x[uniq], y[uniq]
    xq = np.atleast_1d(np.asarray(xq, dtype=float))
    out = np.full(xq.shape, np.nan)
    inside = (xq >= x.min()) & (xq <= x.max())
    if warning and not np.all(inside):
        warnings.warn(f"lookup: {label} input outside table range (NaN output)")
    if np.any(inside):
        f = PchipInterpolator(x, y) if method == "pchip" else None
        out[inside] = f(xq[inside]) if f else np.interp(xq[inside], x, y)
    return np.squeeze(out)


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def lookup(data: dict, outvar: str, method: str = "pchip",
           warning: bool = True, **kw) -> np.ndarray:
    """Modes:
    (1) lookup(nch, 'ID',  VGS=0.5, VDS=0.8, L=0.13, VSB=0.1)
    (2) lookup(nch, 'GM_ID', VGS=0.5, VDS=0.8, L=0.13)
    (3) lookup(nch, 'GM_CGG', GM_ID=15, VDS=0.6, L=0.13)   # ratio vs ratio
    Omitted axes default to L=min(L), VGS=grid, VDS=max(VDS)/2, VSB=0.
    """
    pts = _defaults(data)
    ratio_kw = {k: v for k, v in kw.items() if k not in AXES}
    for a in AXES:
        if a in kw:
            pts[a] = kw[a]

    if not ratio_kw:                                   # modes 1 / 2
        return _eval(data, outvar, pts)

    if len(ratio_kw) != 1:
        raise ValueError("mode 3 takes exactly one input ratio")
    (xname, xq), = ratio_kw.items()                    # mode 3
    if "VGS" in kw:
        pts["VGS"] = np.asarray(kw["VGS"], dtype=float)  # user-restricted range
    else:
        pts["VGS"] = np.asarray(data["VGS"], dtype=float)
    for a in ("L", "VDS", "VSB"):
        if np.ndim(pts[a]) != 0:
            raise ValueError(f"mode 3 requires scalar {a}")
    x = np.atleast_1d(_eval(data, xname, pts))
    y = np.atleast_1d(_eval(data, outvar, pts))
    x, (y,) = _trim(xname, x, [y])
    return _invert(x, y, xq, method, warning, xname)


def lookup_vgs(data: dict, method: str = "pchip", warning: bool = True,
               **kw) -> np.ndarray:
    """Invert for VGS at a target GM_ID or ID_W.
    Mode 1 (source known):    lookup_vgs(nch, GM_ID=10, VDS=0.6, VSB=0.1, L=0.13)
    Mode 2 (source floating): lookup_vgs(nch, GM_ID=10, VDB=0.6, VGB=1.0, L=0.13)
    """
    if "GM_ID" in kw:
        xname, xq = "GM_ID", kw["GM_ID"]
    elif "ID_W" in kw:
        xname, xq = "ID_W", kw["ID_W"]
    else:
        raise ValueError("provide GM_ID or ID_W")
    L = float(kw.get("L", np.min(data["L"])))
    vgs_grid = np.asarray(data["VGS"], dtype=float)

    if "VDB" in kw or "VGB" in kw:                     # mode 2
        vdb, vgb = float(kw["VDB"]), float(kw["VGB"])
        vsb = vgb - vgs_grid                            # VS = VGB - VGS
        vds = vdb - vgb + vgs_grid
        ok = (vsb >= float(np.min(data["VSB"]))) & (vsb <= float(np.max(data["VSB"]))) \
           & (vds >= float(np.min(data["VDS"]))) & (vds <= float(np.max(data["VDS"])))
        vgs_grid, vsb, vds = vgs_grid[ok], vsb[ok], vds[ok]
        x = np.array([
            float(_eval(data, xname, {"L": L, "VGS": g, "VDS": d, "VSB": s}))
            for g, d, s in zip(vgs_grid, vds, vsb)
        ])
    else:                                               # mode 1
        pts = {"L": L, "VGS": vgs_grid,
               "VDS": float(kw.get("VDS", np.max(data["VDS"]) / 2.0)),
               "VSB": float(kw.get("VSB", 0.0))}
        x = np.atleast_1d(_eval(data, xname, pts))

    if xname == "GM_ID":
        x, (vgs_grid,) = _trim("GM_ID", x, [vgs_grid])
    return _invert(x, vgs_grid, xq, method, warning, xname)


if __name__ == "__main__":
    # Smoke test on a synthetic square-law-ish table.
    L = np.array([0.13, 0.2, 0.5, 1.0])
    VGS = np.linspace(0.0, 1.5, 61)
    VDS = np.linspace(0.0, 1.5, 31)
    VSB = np.array([0.0, 0.2, 0.4])
    Lg, Gg, Dg, Sg = np.meshgrid(L, VGS, VDS, VSB, indexing="ij")
    vov = np.maximum(Gg - 0.4, 1e-3)
    ID = 1e-3 * (10.0 / Lg) * (vov**2) * (1 + 0.05 * Dg / Lg)
    GM = 2e-3 * (10.0 / Lg) * vov * (1 + 0.05 * Dg / Lg)
    GDS = ID * 0.05 / Lg
    CGG = 2e-15 * 10.0 * Lg * np.ones_like(ID)
    tbl = dict(L=L, VGS=VGS, VDS=VDS, VSB=VSB, ID=ID, GM=GM, GDS=GDS,
               CGG=CGG, W=np.float64(10.0), NFING=np.int64(5),
               CORNER="NOM", TEMP=np.float64(300), INFO="synthetic")
    gmid = lookup(tbl, "GM_ID", VGS=0.8, VDS=0.75, L=0.13, VSB=0.0)
    jd = lookup(tbl, "ID_W", GM_ID=float(gmid), VDS=0.75, L=0.13, VSB=0.0)
    vgs = lookup_vgs(tbl, GM_ID=float(gmid), VDS=0.75, VSB=0.0, L=0.13)
    print(f"gm/ID={float(gmid):.3f} S/A  JD={float(jd):.3e} A/um  "
          f"VGS={float(vgs):.4f} V (expect ~0.8)")
    assert abs(float(vgs) - 0.8) < 5e-3
    vgs2 = lookup_vgs(tbl, GM_ID=float(gmid), VDB=0.75, VGB=0.9, L=0.13)
    print(f"mode-2 VGS={float(vgs2):.4f} V")
    print("smoke test OK")
