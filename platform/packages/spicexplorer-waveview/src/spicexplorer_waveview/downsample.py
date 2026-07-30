"""Waveform downsampling for interactive display of large traces.

Two index-selecting strategies (both keep the first and last sample and preserve
x-order), applied to REAL-valued y — complex signals are transformed (mag/phase/re/im)
before downsampling:

* ``minmax_indices`` — per-bucket min+max envelope. Never loses a glitch/peak; the
  right default for transient/DC traces.
* ``lttb_indices`` — Largest-Triangle-Three-Buckets. Perceptually faithful line shape
  at very low point budgets; the usual choice for smooth frequency-domain curves.

Both return **indices** into the original arrays, so callers slice x and y
consistently (and can slice any co-indexed metadata the same way).
"""

from __future__ import annotations

import numpy as np

__all__ = ["minmax_indices", "lttb_indices", "downsample_indices"]


def minmax_indices(y: np.ndarray, n_out: int) -> np.ndarray:
    """Envelope-preserving bucket downsample → sorted unique indices (≤ ``n_out``).

    Buckets the trace into ``n_out // 2`` spans and keeps each span's min and max
    sample (plus the endpoints), so spikes survive any zoom level.
    """
    y = np.asarray(y)
    n = y.size
    if n_out >= n or n <= 2:
        return np.arange(n)
    n_buckets = max(1, n_out // 2)
    edges = np.linspace(0, n, n_buckets + 1, dtype=int)
    keep = {0, n - 1}
    for b in range(n_buckets):
        lo, hi = edges[b], edges[b + 1]
        if hi <= lo:
            continue
        seg = y[lo:hi]
        keep.add(lo + int(np.argmin(seg)))
        keep.add(lo + int(np.argmax(seg)))
    return np.array(sorted(keep), dtype=int)


def lttb_indices(x: np.ndarray, y: np.ndarray, n_out: int) -> np.ndarray:
    """Largest-Triangle-Three-Buckets downsample → sorted indices (== ``n_out`` when it fires).

    Standard LTTB (Steinarsson 2013): endpoints fixed; each interior bucket keeps the
    point forming the largest triangle with the previously kept point and the next
    bucket's mean point.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = y.size
    if n_out >= n or n <= 2 or n_out < 3:
        return np.arange(n)

    edges = np.linspace(1, n - 1, n_out - 1, dtype=int)  # interior bucket boundaries
    keep = np.empty(n_out, dtype=int)
    keep[0] = 0
    a = 0  # index of the previously selected point
    for i in range(n_out - 2):
        lo, hi = edges[i], edges[i + 1]
        if hi <= lo:
            keep[i + 1] = min(lo, n - 1)
            a = keep[i + 1]
            continue
        # next bucket's average point (the "third vertex")
        nlo, nhi = edges[i + 1], edges[min(i + 2, n_out - 2)]
        if nhi <= nlo:
            nhi = min(nlo + 1, n)
        avg_x = float(np.mean(x[nlo:nhi]))
        avg_y = float(np.mean(y[nlo:nhi]))
        seg_x = x[lo:hi]
        seg_y = y[lo:hi]
        # triangle areas vs (a, candidate, avg)
        area = np.abs(
            (x[a] - avg_x) * (seg_y - y[a]) - (x[a] - seg_x) * (avg_y - y[a])
        )
        a = lo + int(np.argmax(area))
        keep[i + 1] = a
    keep[-1] = n - 1
    return np.unique(keep)


def downsample_indices(
    x: np.ndarray, y: np.ndarray, n_out: int, method: str = "minmax"
) -> np.ndarray:
    """Dispatch: ``minmax`` (default) | ``lttb`` | ``stride`` | ``none`` → index array."""
    n = np.asarray(y).size
    if method == "none" or n_out >= n:
        return np.arange(n)
    if method == "lttb":
        return lttb_indices(x, y, n_out)
    if method == "stride":
        idx = np.linspace(0, n - 1, n_out, dtype=int)
        return np.unique(idx)
    if method == "minmax":
        return minmax_indices(y, n_out)
    raise ValueError(f"unknown downsample method {method!r} (minmax|lttb|stride|none)")
