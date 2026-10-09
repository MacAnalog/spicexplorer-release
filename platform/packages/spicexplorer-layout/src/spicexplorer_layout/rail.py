"""Sheet-resistance solve on a DRAWN metal net — the series R no extractor gives you.

A 2.5-D extractor's RC mesh is joined but its terminal and via values are routinely orders out,
so every series-resistance number in a cell ends up being a *model*. A 1-D hand model is how a
return path gets credited with a strap that only spans part of it: "the ring runs the whole
170 µm" is a sentence, and the drawing says the first 66 µm is bare rail. This module solves the
drawn copper instead of describing it.

Method: rasterize one drawn layer at ``pitch`` µm, keep the 4-connected component that touches
the pin, and solve the resistor network in which each grid edge is **one square** of sheet metal
(conductance ``1/R_sheet``, independent of the pitch). Inject 1 A at a probe node, ground the pin
node, read the potential: ``R = V``. A terminal is a BOX, not a point — the grid cells it covers
are contracted to one node, because a single-cell terminal adds the grid's own spreading
resistance (+8 % on the analytic bar) while a real terminal is a contact pad or the full width of
a riser. :func:`selftest` checks the solver against an analytic bar.

The two halves are deliberately separate: :func:`solve_sheet_resistance` is pure numpy/scipy and
runs anywhere, :func:`rasterize_layer` needs klayout and a GDS. Sheet resistances and GDS layer
numbers come from the tech config (:mod:`spicexplorer_core.tech`) — never a literal here.

    from spicexplorer_layout.rail import net_resistance
    net_resistance("cell.gds", "my_cell", "Metal1", pin=(-70, -134),
                   probes={"far_end": (96.5, 2.15)}, tech="ihp-sg13g2")
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
from spicexplorer_core.tech import Tech

__all__ = [
    "GridBox",
    "Raster",
    "component_touching",
    "net_resistance",
    "rasterize_layer",
    "selftest",
    "solve_sheet_resistance",
]

#: A terminal as grid indices: ``(j0, j1, i0, i1)`` inclusive, row-major (j = y, i = x).
GridBox = tuple[int, int, int, int]


class Raster:
    """A boolean grid of one drawn layer, plus the µm origin needed to place a terminal on it."""

    def __init__(self, mask: np.ndarray, x0: float, y0: float, pitch: float):
        self.mask = mask
        self.x0 = x0
        self.y0 = y0
        self.pitch = pitch

    def box(self, spec: Sequence[float]) -> GridBox:
        """``(x, y)`` (one cell) or ``(x0, y0, x1, y1)`` (a terminal face) in µm -> grid indices."""
        v = list(spec)
        if len(v) == 2:
            v = [v[0], v[1], v[0], v[1]]
        if len(v) != 4:
            raise ValueError(f"a terminal is (x, y) or (x0, y0, x1, y1) in um, got {spec!r}")
        return (
            int(round((v[1] - self.y0) / self.pitch)),
            int(round((v[3] - self.y0) / self.pitch)),
            int(round((v[0] - self.x0) / self.pitch)),
            int(round((v[2] - self.x0) / self.pitch)),
        )


def rasterize_layer(
    gds: str | Path,
    cell: str | None,
    layer: str,
    pitch: float = 0.1,
    *,
    tech: Tech | str | Path | None = None,
) -> Raster:
    """Merge one drawn layer of ``cell`` and rasterize it at ``pitch`` µm. Needs klayout."""
    import klayout.db as db

    t = Tech.resolve(tech)
    num, dt = t.gds_layer(layer)

    ly = db.Layout()
    ly.read(str(gds))
    top = (ly.cell(cell) if cell else None) or ly.top_cell()
    reg = db.Region(top.begin_shapes_rec(ly.layer(num, dt))).merged()
    bb = reg.bbox()
    if bb.empty():
        raise ValueError(f"{gds}: cell {top.name!r} draws nothing on {layer} ({num}/{dt})")
    dbu = ly.dbu
    x0, y0 = bb.left * dbu, bb.bottom * dbu
    nx = int(np.ceil((bb.right * dbu - x0) / pitch)) + 1
    ny = int(np.ceil((bb.top * dbu - y0) / pitch)) + 1
    mask = np.zeros((ny, nx), bool)
    step = int(round(pitch / dbu))
    for j in range(ny):
        yb = bb.bottom + j * step
        strip = reg & db.Region(db.Box(bb.left, yb, bb.right, yb + 1))
        for poly in strip.each():
            b = poly.bbox()
            i0 = max(0, int(np.floor((b.left - bb.left) / step)))
            i1 = min(nx - 1, int(np.ceil((b.right - bb.left) / step)))
            mask[j, i0 : i1 + 1] = True
    return Raster(mask, x0, y0, pitch)


def component_touching(mask: np.ndarray, seed: tuple[int, int]) -> np.ndarray:
    """The 4-connected component of ``mask`` containing ``seed`` (a ``(j, i)`` index pair).

    Everything the pin cannot reach through drawn metal is not part of the net, whatever the
    layer looks like: a solve over the whole layer would short two unconnected rails.
    """
    from scipy.ndimage import label

    lab, _ = label(mask, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    k = lab[seed]
    if k == 0:
        raise ValueError(f"the seed cell {seed} is not on the drawn layer")
    return lab == k


def solve_sheet_resistance(
    mask: np.ndarray,
    r_sheet: float,
    pin_box: GridBox,
    probe_boxes: Mapping[str, GridBox],
) -> dict[str, float]:
    """``{probe: R(pin -> probe)}`` in ohms, by nodal analysis on the grid.

    Pure numpy/scipy: no GDS, no klayout, no PDK. ``r_sheet`` is ohms per square; each grid edge
    is one square whatever the pitch, so the answer does not depend on the rasterization step
    (only its accuracy does).
    """
    if mask.ndim != 2 or not mask.any():
        raise ValueError("the mask must be a non-empty 2-D boolean grid")
    from scipy.ndimage import label
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve

    idx = -np.ones(mask.shape, int)
    n = int(mask.sum())
    idx[mask] = np.arange(n)
    # A terminal reachable from the pin only through metal this net does NOT draw (a disconnected
    # island) makes the conductance matrix below singular between that island and the rest. spsolve
    # does not raise on that -- it returns a huge, meaningless finite number (reuse review F5: a
    # measured repro returned -8e13 ohms), which looks like a real answer to any caller that does
    # not know to distrust it. Check connectivity explicitly, before the solve, so a disconnected
    # mask is a loud ValueError instead of a silent wrong number.
    lab, _ = label(mask, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    rep = np.arange(n)
    groups: dict[str, int] = {}
    box_labels: dict[str, set[int]] = {}
    for name, (j0, j1, i0, i1) in {**dict(probe_boxes), "__pin__": pin_box}.items():
        cells_grid = idx[j0 : j1 + 1, i0 : i1 + 1]
        on_mask = cells_grid >= 0
        cells = cells_grid[on_mask]
        if cells.size == 0:
            raise ValueError(f"terminal {name!r} covers no cell of the net")
        rep[cells] = cells.min()
        groups[name] = int(cells.min())
        box_labels[name] = set(lab[j0 : j1 + 1, i0 : i1 + 1][on_mask].tolist())
    pin_labels = box_labels["__pin__"]
    for name in probe_boxes:
        if box_labels[name].isdisjoint(pin_labels):
            raise ValueError(
                f"terminal {name!r} is not reachable from the pin through drawn metal -- the "
                "mask has a disconnected island under this net (check the layer rasterization "
                "or the probe/pin box placement)"
            )
    # One relabelling pass is enough: the terminal boxes do not overlap.
    uniq, inv = np.unique(rep, return_inverse=True)
    m = uniq.size
    node = inv
    g = 1.0 / r_sheet
    rows, cols, vals = [], [], []
    for di, dj in ((0, 1), (1, 0)):
        a = idx[: mask.shape[0] - di, : mask.shape[1] - dj]
        b = idx[di:, dj:]
        ok = (a >= 0) & (b >= 0)
        ai, bi = node[a[ok]], node[b[ok]]
        live = ai != bi
        ai, bi = ai[live], bi[live]
        rows += [ai, bi, ai, bi]
        cols += [ai, bi, bi, ai]
        vals += [
            np.full(ai.size, g),
            np.full(ai.size, g),
            np.full(ai.size, -g),
            np.full(ai.size, -g),
        ]
    G = coo_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(m, m)
    ).tocsc()
    ref = int(node[groups["__pin__"]])
    keep = np.ones(m, bool)
    keep[ref] = False
    Gr = G[keep][:, keep].tocsc()
    kept = np.flatnonzero(keep)
    out: dict[str, float] = {}
    for name in probe_boxes:
        p = int(node[groups[name]])
        if p == ref:
            out[name] = 0.0  # the probe box touches the pin box: zero by construction
            continue
        rhs = np.zeros(m)
        rhs[p] = 1.0
        v = spsolve(Gr, rhs[keep])
        out[name] = float(v[np.searchsorted(kept, p)])
    return out


def net_resistance(
    gds: str | Path,
    cell: str | None,
    layer: str,
    *,
    pin: Sequence[float],
    probes: Mapping[str, Sequence[float]],
    tech: Tech | str | Path | None = None,
    pitch: float = 0.1,
) -> dict[str, float]:
    """End to end: rasterize ``layer``, keep the pin's component, solve. Ohms per probe.

    ``pin`` and each probe are ``(x, y)`` or ``(x0, y0, x1, y1)`` in µm.
    """
    t = Tech.resolve(tech)
    r = rasterize_layer(gds, cell, layer, pitch, tech=t)
    pin_box = r.box(pin)
    r.mask = component_touching(r.mask, (pin_box[0], pin_box[2]))
    return solve_sheet_resistance(
        r.mask, t.sheet_resistance(layer), pin_box, {k: r.box(v) for k, v in probes.items()}
    )


def selftest(pitch: float = 0.1, r_sheet: float = 0.11) -> tuple[float, float]:
    """A 10 × 1 µm bar is 10 squares end to end. Returns ``(solved, analytic)`` in ohms."""
    ny, nx = int(1 / pitch), int(10 / pitch)
    mask = np.ones((ny, nx), bool)
    got = solve_sheet_resistance(
        mask, r_sheet, (0, ny - 1, 0, 0), {"end": (0, ny - 1, nx - 1, nx - 1)}
    )
    want = (nx - 1) * pitch / (ny * pitch) * r_sheet
    return got["end"], want
