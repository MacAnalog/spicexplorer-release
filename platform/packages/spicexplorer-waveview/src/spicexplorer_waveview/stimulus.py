"""Data stimulus: PRBS bit streams, NRZ/PAM4 symbol levels and exact UI-delayed PWL sources.

One symbol sequence drives every source; an FFE tap is the same sequence delayed ``k`` UI, so
the delay is exact by construction rather than by an on-chip delay element. The
:class:`Data` object is the shared description a bench and the :mod:`eye` measurement both
read — the eye groups samples by the *transmitted* symbol, which only works because the
bench generated them from the same PRBS.
"""

from __future__ import annotations

import dataclasses

import numpy as np

__all__ = ["Data", "prbs", "symbols", "pwl", "ideal_waveform", "PRBS_TAPS", "FORMATS"]

# x^a + x^b + 1 feedback taps for the standard PRBS orders (ITU-T O.150 / common usage).
PRBS_TAPS = {7: (7, 6), 9: (9, 5), 11: (11, 9), 15: (15, 14)}
FORMATS = ("nrz", "pam4")


def prbs(order: int, n: int, seed: int = 1) -> np.ndarray:
    """First ``n`` bits of PRBS-``order`` (``x^a + x^b + 1``) as 0/1 ints; period ``2^order - 1``."""
    if order not in PRBS_TAPS:
        raise ValueError(f"unsupported PRBS order {order} (one of {sorted(PRBS_TAPS)})")
    a, b = PRBS_TAPS[order]
    state = [(seed >> i) & 1 for i in range(order)]
    if not any(state):
        state[0] = 1
    out = np.empty(n, dtype=int)
    for i in range(n):
        new = state[a - 1] ^ state[b - 1]
        out[i] = state[a - 1]
        state = [new] + state[:-1]
    return out


def _fmt(fmt: str) -> str:
    if fmt not in FORMATS:
        raise ValueError(f"unknown format {fmt!r} ({' | '.join(FORMATS)})")
    return fmt


def symbols(fmt: str, order: int, n: int, seed: int = 1) -> np.ndarray:
    """Normalized symbols: NRZ in ``{-1, +1}``; PAM4 Gray-coded in ``{-1, -1/3, 1/3, 1}``."""
    if _fmt(fmt) == "nrz":
        return 2.0 * prbs(order, n, seed) - 1.0
    bits = prbs(order, 2 * n, seed)
    gray = {(0, 0): 0, (0, 1): 1, (1, 1): 2, (1, 0): 3}
    lvl = np.array([gray[(int(m), int(lo))] for m, lo in zip(bits[0::2], bits[1::2])])
    return (2.0 * lvl - 3.0) / 3.0


@dataclasses.dataclass(frozen=True)
class Data:
    """One stimulus: format, rate, PRBS order; ``t0`` is the first symbol edge (after the bias
    ramp); ``n_warm`` symbols are driven but not scored; ``tr_ui`` is the edge time in UI."""

    fmt: str
    rate_gbd: float
    order: int = 7
    n_warm: int = 8
    seed: int = 1
    t0: float = 8e-9
    tr_ui: float = 0.2

    def __post_init__(self) -> None:
        _fmt(self.fmt)
        if self.rate_gbd <= 0:
            raise ValueError("rate_gbd must be positive")
        if self.order not in PRBS_TAPS:
            raise ValueError(f"order must be one of {sorted(PRBS_TAPS)} (PRBS taps)")
        if not 0 < self.tr_ui < 1:
            raise ValueError("tr_ui must be in (0, 1): a zero edge repeats a PWL time point")
        if self.t0 < 0:
            raise ValueError("t0 must be >= 0")
        if self.n_warm < 0:
            raise ValueError("n_warm must be >= 0")

    @property
    def ui(self) -> float:
        return 1.0 / (self.rate_gbd * 1e9)

    @property
    def n(self) -> int:
        return self.n_warm + (2**self.order - 1)

    @property
    def syms(self) -> np.ndarray:
        return symbols(self.fmt, self.order, self.n, self.seed)

    @property
    def bits_per_symbol(self) -> int:
        return 2 if self.fmt == "pam4" else 1

    @property
    def t_end(self) -> float:
        return self.t0 + self.n * self.ui

    def window(self) -> tuple[float, float]:
        """The scored window: after the warm-up symbols, to the end of the sequence."""
        return self.t0 + self.n_warm * self.ui, self.t_end

    @classmethod
    def from_recipe(cls, recipe: dict) -> Data:
        """The stimulus a ``{meas: eye_*, fmt, rate_gbd, order?, n_warm?, seed?, t0?, tr_ui?}``
        recipe describes (the same keys as the constructor); numerics are coerced, since a
        YAML recipe may hand them over as strings."""
        kw: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name in recipe:
                v = recipe[f.name]
                kw[f.name] = str(v) if f.name == "fmt" else int(v) if f.type == "int" else float(v)
        return cls(**kw)  # type: ignore[arg-type]


def pwl(
    name: str,
    node: str,
    ref: str,
    data: Data,
    *,
    vcm: float,
    swing: float,
    delay_ui: float = 0.0,
    invert: bool = False,
) -> str:
    """A PWL source line: ``vcm + sym * swing/2`` per symbol, ``tr_ui`` edges, delayed by
    ``delay_ui`` UI; sits at ``vcm`` before its start. Time points strictly increase (a
    start at ``t=0`` is not repeated — ngspice would warn ``non-increasing PWL time points``
    and run on a distorted stimulus)."""
    s = -data.syms if invert else data.syms
    ui, tr = data.ui, data.tr_ui * data.ui
    t0 = data.t0 + delay_ui * ui
    pts = [f"0 {vcm:.6g}"] + ([f"{t0:.6e} {vcm:.6g}"] if t0 > 0 else [])
    prev = vcm
    for k, v in enumerate(s):
        lvl = vcm + float(v) * swing / 2
        t = t0 + k * ui
        if k:
            pts.append(f"{t:.6e} {prev:.6g}")
        pts.append(f"{t + tr:.6e} {lvl:.6g}")
        prev = lvl
    return f"{name} {node} {ref} PWL({' '.join(pts)})"


def ideal_waveform(t: np.ndarray, data: Data) -> np.ndarray:
    """The normalized symbol waveform sampled on ``t`` (zero outside the sequence); the
    reference the eye's latency search correlates against."""
    idx = np.floor((t - data.t0) / data.ui).astype(int)
    out = np.zeros_like(t, dtype=float)
    ok = (idx >= 0) & (idx < data.n)
    out[ok] = data.syms[idx[ok]]
    return out
