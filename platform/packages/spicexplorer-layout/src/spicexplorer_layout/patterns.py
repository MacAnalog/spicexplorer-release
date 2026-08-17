"""Matching-pattern helpers generators compose. Pure functions first (orders), then thin
gdsfactory placement helpers behind a lazy import so the module loads without gdsfactory.

Vocabulary (see the workspace layout agents' technique catalogue): **interdigitate** what
sets an *offset* (ABAB / ABBA rows cancel a linear gradient along the row),
**common-centroid** what sets a *ratio* or sees a 2-D gradient (ABBA/BAAB rows, cross-quad),
dummies at both row ends so the outer members see the same etch/stress environment.
"""

from __future__ import annotations

from typing import Iterable, Sequence


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
    ``n_each`` (if given) checks the grid holds exactly n_each of each label."""
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
    return grid


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
