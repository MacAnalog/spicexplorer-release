"""Matching-pattern helpers generators compose. Pure functions first (orders), then thin
gdsfactory placement helpers behind a lazy import so the module loads without gdsfactory.

Vocabulary (see the workspace layout agents' technique catalogue): **interdigitate** what
sets an *offset* (ABAB / ABBA rows cancel a linear gradient along the row),
**common-centroid** what sets a *ratio* or sees a 2-D gradient (ABBA/BAAB rows, cross-quad),
dummies at both row ends so the outer members see the same etch/stress environment.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def interdigitate_order(labels: Sequence[str], n_each: int, *, style: str = "ABBA") -> list[str]:
    """Finger order for a matched set. ``labels`` e.g. ("A","B"), ``n_each`` fingers per device.

    style "ABAB": plain alternation; "ABBA": palindromic (each pair of rows cancels a linear
    gradient — the usual choice for two devices). For >2 labels "ABBA" means forward then
    reversed blocks. Raises if n_each is not compatible with the palindrome (must be even
    for ABBA with 2 labels)."""
    labels = list(labels)
    k = len(labels)
    if style.upper() == "ABAB":
        return [labels[i % k] for i in range(k * n_each)]
    if style.upper() == "ABBA":
        if n_each % 2:
            raise ValueError("ABBA needs an even number of fingers per device")
        blk = labels + labels[::-1]
        return blk * (n_each // 2)
    raise ValueError(f"unknown style {style!r}")


def common_centroid_order(
    labels: Sequence[str] = ("A", "B"), rows: int = 2, cols: int = 2, n_each: int | None = None
) -> list[list[str]]:
    """2-D common-centroid grid as a list of rows. Default 2×2 → [[A,B],[B,A]] (cross-quad);
    larger grids alternate ABBA / BAAB rows so every label's centroid is the grid centre.
    ``n_each`` (if given) checks the grid holds exactly n_each of each label.

    The centroids are VERIFIED, not assumed. The docstring's promise held only for some shapes:
    2x3, 3x2, 3x3, 3x6 and 4x3 all come out with the two labels on different centroids, and 3x6
    does so with nine of each — so the count check passed while the gradient cancellation this
    pattern exists for did not happen (Codex review, item LAY-01). A grid this construction
    cannot balance now raises instead of being returned as if it were."""
    labels = list(labels)
    k = len(labels)
    if k != 2:
        raise NotImplementedError("common_centroid_order supports two labels today")
    a, b = labels
    grid: list[list[str]] = []
    for r in range(rows):
        row = []
        for c in range(cols):
            # ABBA pattern along the row, then flip on alternate rows
            v = a if (c % 4 in (0, 3)) else b
            row.append(v if r % 2 == 0 else (b if v == a else a))
        grid.append(row)
    if n_each is not None:
        cnt = sum(row.count(a) for row in grid)
        if cnt != n_each or rows * cols - cnt != n_each:
            raise ValueError(
                f"{rows}x{cols} grid holds {cnt} {a} / {rows * cols - cnt} {b}, not {n_each} each"
            )
    ca, cb = _centroid(grid, a), _centroid(grid, b)
    if ca is None or cb is None or not _same_point(ca, cb):
        raise ValueError(
            f"a {rows}x{cols} grid of {a}/{b} is not common-centroid: {a} sits at {ca} and {b} at "
            f"{cb} (row, col). Equal counts are not a common centroid — the point of the pattern is "
            "that both devices see the same 2-D gradient, which they do not here. Use an even "
            "number of columns, and with an odd number of rows a multiple of 4 (2x2, 2x4, 4x2, "
            "3x4, 3x8 work; this ABBA-by-columns construction does not balance 2x3, 3x2, 3x3, 3x6 "
            "or 4x3)."
        )
    return grid


def _centroid(grid: Sequence[Sequence[str]], label: str) -> tuple[float, float] | None:
    """Mean (row, col) of every cell carrying ``label``, or None when it appears nowhere."""
    pts = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == label]
    if not pts:
        return None
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def _same_point(p: tuple[float, float], q: tuple[float, float]) -> bool:
    """Exact-enough equality: the coordinates are small rationals, so 1e-9 is far below any real
    difference (the smallest genuine mismatch on a grid this size is 1/9)."""
    return abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9


def with_dummies(order: Sequence[str], n_dummy: int = 1, label: str = "D") -> list[str]:
    return [label] * n_dummy + list(order) + [label] * n_dummy


# ---- gdsfactory placement helpers (lazy import) --------------------------------------------


def mirror_pair(
    parent,
    comp_l,
    comp_r,
    *,
    y: float,
    gap_x: float,
    axis_x: float = 0.0,
    mirror_l: bool = True,
    mirror_r: bool = False,
):
    """Place a device pair mirrored about ``axis_x`` with inner edges at ±gap_x/2, bottoms at y.
    Returns (ref_l, ref_r). Which instance is mirrored decides which terminal faces the axis."""
    il, ir = parent << comp_l, parent << comp_r
    if mirror_l:
        il.dmirror_x()
    if mirror_r:
        ir.dmirror_x()
    il.dxmax = axis_x - gap_x / 2
    ir.dxmin = axis_x + gap_x / 2
    il.dymin = y
    ir.dymin = y
    return il, ir


def place_row(
    parent, comps: Iterable, *, y: float, x0: float, pitch: float | None = None, gap: float = 0.0
):
    """Place components left→right starting at x0 (bottom at y); ``pitch`` fixes centre spacing,
    else abutting with ``gap``. Returns the references in order."""
    refs = []
    x = x0
    for comp in comps:
        r = parent << comp
        r.dymin = y
        if pitch is None:
            r.dxmin = x
            x = r.dxmax + gap
        else:
            r.dx = x
            x += pitch
        refs.append(r)
    return refs
