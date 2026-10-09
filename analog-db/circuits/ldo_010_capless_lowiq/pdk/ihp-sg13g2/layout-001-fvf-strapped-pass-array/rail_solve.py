"""Sheet-resistance solve on a drawn metal net — the `vss` return path (review-004 **F9**).

There is no extracted resistance to read: kpex's RC mesh is joined but its terminal/via values
are three orders out (REPORT section 5), so every series-R number in this cell is a model. A
1-D hand model is what got REPORT section 6.4 wrong: it credited the row-A ptap ring over the
whole 170 um of the return when the ring spans only x = -3.4 .. 105.6, so the first 66.6 um is
bare rail. This solves the drawn copper instead of describing it.

Method: rasterize one drawn layer at `--pitch` um, keep the 4-connected component that touches
the pin, and solve the resistor network in which each grid edge is one square of sheet metal
(conductance = 1 / R_sheet, independent of the pitch). Inject 1 A at a probe node, ground the
pin node, read the potential: R = V. Validated against an analytic bar by `--selftest`.

    python rail_solve.py <gds> --net-pin -70,-134 --probe 96.5,2.15
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

# Sheet resistance, Ohm/square (IHP SG13G2 process spec section 2.15).
R_SHEET = {"Metal1": 0.110, "Metal2": 0.088, "Metal3": 0.088, "Metal4": 0.088,
           "Metal5": 0.088, "TopMetal1": 0.018}
LAYER = {"Metal1": (8, 0), "Metal2": (10, 0), "Metal3": (30, 0), "Metal4": (50, 0),
         "Metal5": (67, 0), "TopMetal1": (126, 0)}


def rasterize(gds: str, cell: str, layer: str, pitch: float):
    """`(mask, x0, y0)` — a boolean grid of the merged layer at `pitch` um."""
    import klayout.db as db

    ly = db.Layout()
    ly.read(gds)
    top = ly.cell(cell) or ly.top_cell()
    reg = db.Region(top.begin_shapes_rec(ly.layer(*LAYER[layer]))).merged()
    bb = reg.bbox()
    dbu = ly.dbu
    x0, y0 = bb.left * dbu, bb.bottom * dbu
    nx = int(np.ceil((bb.right * dbu - x0) / pitch)) + 1
    ny = int(np.ceil((bb.top * dbu - y0) / pitch)) + 1
    mask = np.zeros((ny, nx), bool)
    step = int(round(pitch / dbu))
    for j in range(ny):
        yb = bb.bottom + j * step
        strip = reg & db.Region(db.Box(bb.left, yb, bb.right, yb + 1))
        for p in strip.each():
            b = p.bbox()
            i0 = max(0, int(np.floor((b.left - bb.left) / step)))
            i1 = min(nx - 1, int(np.ceil((b.right - bb.left) / step)))
            mask[j, i0:i1 + 1] = True
    return mask, x0, y0


def component(mask, seed_ij):
    """The 4-connected component of `mask` containing `seed_ij`."""
    from scipy.ndimage import label

    lab, _ = label(mask, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    k = lab[seed_ij]
    if k == 0:
        raise SystemExit(f"the seed cell {seed_ij} is not on the layer")
    return lab == k


def solve(mask, rsheet: float, pin_box, probe_boxes):
    """`{probe: R(pin -> probe)}` in Ohm, by nodal analysis on the grid.

    A terminal is a BOX, not a point: the grid cells it covers are contracted to one node. A
    single-cell terminal adds the grid's own spreading resistance (+8 % on the self-test bar);
    a real terminal is a contact pad or the full width of a riser, and shorting its cells is
    both closer to the drawing and what makes the self-test land on the analytic value.
    """
    idx = -np.ones(mask.shape, int)
    n = int(mask.sum())
    idx[mask] = np.arange(n)
    rep = np.arange(n)
    groups = {}
    for name, (j0, j1, i0, i1) in {**probe_boxes, "__pin__": pin_box}.items():
        cells = idx[j0:j1 + 1, i0:i1 + 1]
        cells = cells[cells >= 0]
        if cells.size == 0:
            raise SystemExit(f"terminal {name} covers no cell of the net")
        rep[cells] = cells.min()
        groups[name] = int(cells.min())
    # one relabelling pass is enough: the boxes do not overlap
    uniq, inv = np.unique(rep, return_inverse=True)
    m = uniq.size
    node = inv                                   # old node -> contracted node
    g = 1.0 / rsheet                             # one square per grid edge, whatever the pitch
    rows, cols, vals = [], [], []
    for di, dj in ((0, 1), (1, 0)):
        a = idx[:mask.shape[0] - di, :mask.shape[1] - dj]
        b = idx[di:, dj:]
        ok = (a >= 0) & (b >= 0)
        ai, bi = node[a[ok]], node[b[ok]]
        live = ai != bi
        ai, bi = ai[live], bi[live]
        rows += [ai, bi, ai, bi]
        cols += [ai, bi, bi, ai]
        vals += [np.full(ai.size, g), np.full(ai.size, g),
                 np.full(ai.size, -g), np.full(ai.size, -g)]
    G = coo_matrix((np.concatenate(vals),
                    (np.concatenate(rows), np.concatenate(cols))), shape=(m, m)).tocsc()
    ref = int(node[groups["__pin__"]])
    keep = np.ones(m, bool); keep[ref] = False
    Gr = G[keep][:, keep].tocsc()
    kept = np.flatnonzero(keep)
    out = {}
    for name in probe_boxes:
        p = int(node[groups[name]])
        rhs = np.zeros(m); rhs[p] = 1.0
        v = spsolve(Gr, rhs[keep])
        out[name] = float(v[np.searchsorted(kept, p)])
    return out


def selftest() -> int:
    """A 10 um x 1 um bar is 10 squares: 10 * R_sheet, end to end (terminals = the end faces)."""
    pitch, rs = 0.1, 0.11
    ny, nx = int(1 / pitch), int(10 / pitch)
    mask = np.ones((ny, nx), bool)
    r = solve(mask, rs, (0, ny - 1, 0, 0), {"end": (0, ny - 1, nx - 1, nx - 1)})
    want = (nx - 1) * pitch / (ny * pitch) * rs
    err = (r["end"] - want) / want
    print(f"bar {(nx - 1) * pitch:g}x{ny * pitch:g} um: solved {r['end']:.4f} Ohm, "
          f"analytic {want:.4f}, error {err * 100:+.2f} %")
    return 0 if abs(err) < 0.01 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("gds", nargs="?")
    ap.add_argument("--cell", default="ldo_ihp_capless")
    ap.add_argument("--layer", default="Metal1")
    ap.add_argument("--pitch", type=float, default=0.1)
    ap.add_argument("--pin", default="", help="x,y of the pin (um)")
    ap.add_argument("--probe", action="append", default=[], help="name=x,y (um), repeatable")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    mask, x0, y0 = rasterize(a.gds, a.cell, a.layer, a.pitch)

    def box(s):
        """"x0,y0,x1,y1" (a terminal face) or "x,y" (one cell) -> grid index box."""
        v = [float(t) for t in s.split(",")]
        if len(v) == 2:
            v = [v[0], v[1], v[0], v[1]]
        return (int(round((v[1] - y0) / a.pitch)), int(round((v[3] - y0) / a.pitch)),
                int(round((v[0] - x0) / a.pitch)), int(round((v[2] - x0) / a.pitch)))

    pinb = box(a.pin)
    mask = component(mask, (pinb[0], pinb[2]))
    print(f"{a.layer}: {mask.sum()} cells on the pin's component at {a.pitch} um")
    probes = {}
    for spec in a.probe:
        name, _, xy = spec.partition("=")
        probes[name] = box(xy)
    for k, v in sorted(solve(mask, R_SHEET[a.layer], pinb, probes).items()):
        print(f"  R(pin -> {k}) = {v:.3f} Ohm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
