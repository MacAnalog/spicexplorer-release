"""Symbol-aware NRZ/PAM4 eye metrics behind a Bessel-Thomson reference receiver.

The bench generated the symbols (:mod:`stimulus`), so samples are grouped by the *transmitted*
symbol — latency by FFT cross-correlation against the ideal symbol waveform, sampling phase
swept over one UI — instead of clustered by level gaps; a closed eye therefore returns finite
numbers (eye height <= 0, VECP capped, width 0) that a scorer can rank. Polarity-safe: an
inverting stage flips the correlation sign and the level order follows it. OMA and VECP come
from the (unclamped) level difference for any polarity; ER is defined for a unipolar input
(optical power, never negative) and is ``nan`` for a bipolar electrical one.

Registered in the core measurement registry as the ``eye`` kind (``register_measurements``),
so ``{meas: eye_h_norm, out: v(pout), fmt: pam4, rate_gbd: 10}`` runs through
``measure_dataset`` like every built-in recipe — the recipe's ``fmt``/``rate_gbd``/``order``/
``n_warm``/``seed``/``t0``/``tr_ui`` keys are the :class:`~spicexplorer_waveview.stimulus.Data`
the bench was built from; ``full_scale``, ``filtered`` and a differential ``ref`` are optional.

**Two eye-width metrics, unambiguously named.** ``eye_metrics`` reports the sampling-phase
opening over TWO different windows, and the names say which: ``eye_w_ui_1s`` counts the phases
open at a +-ONE-SAMPLE window (``UI / OVERSAMPLE`` wide — the widest, most permissive read);
``eye_w_ui_sample_window`` counts the same thing at the +-``sample_half_ui`` window the eye
HEIGHT statistic is measured over (the stricter, self-consistent one — ~0.19 UI narrower on an
ideal eye at the certified defaults). Prefer the explicit names — a consumer that assumed one
while reading the other under the shared bare spelling got a silently wrong number (reuse review
F2). ``eye_w_ui`` is kept as an alias of the WIDE metric (``eye_w_ui_1s``) only for existing
consumers that already read the bare key as a coarse "is the eye open at all" signal; a NEW
reader should always name ``eye_w_ui_1s``/``eye_w_ui_sample_window`` explicitly.

The sampling-phase count is a parameter, not a hidden constant: ``n_phases=`` (default
``PHASES``, the certified value) is recorded in the result as ``sample_phases`` so a re-run
that changes it is visible in the row itself — a coarser sweep quantizes both widths onto a
wider phase grid and is not comparable digit-for-digit against a finer one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np
from scipy import signal
from spicexplorer_core.measurements.registry import register_measurements

from .stimulus import Data, _fmt, ideal_waveform

if TYPE_CHECKING:
    from spicexplorer_core.spice_engine.protocol import SimResult

__all__ = [
    "eye_metrics",
    "fold",
    "latency",
    "levels",
    "rx_bandwidth",
    "bessel_lowpass",
    "resample",
    "EYE_MEASUREMENTS",
    "VECP_CAP_DB",
    "OVERSAMPLE",
    "PHASES",
    "SAMPLE_HALF_UI",
    "FLOOR",
]

VECP_CAP_DB = 40.0
FLOOR = 1e-6  # low-level floor (fraction of full scale) keeping ER finite
SAMPLE_HALF_UI = 0.1  # +-window around the sampling instant for level statistics
PHASES = 40  # sampling phases swept over one UI
OVERSAMPLE = 200  # samples per UI after resampling
RX_BW_X_BAUD = {"nrz": 0.75, "pam4": 0.5}  # reference receiver -3 dB point, x baud


def resample(t: np.ndarray, x: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    """``x(t)`` onto a uniform grid of step ``dt`` (linear interpolation)."""
    tu = np.arange(t[0], t[-1], dt)
    return tu, np.interp(tu, t, x)


def bessel_lowpass(t: np.ndarray, x: np.ndarray, f3db: float, order: int = 4) -> np.ndarray:
    """Bessel-Thomson low-pass (unit dc gain, -3 dB at ``f3db``) on a uniform grid; BT4 by
    default — the reference receiver of the optical eye specs."""
    fs = 1.0 / (t[1] - t[0])
    b, a = cast(
        tuple[np.ndarray, np.ndarray],
        signal.bessel(order, min(f3db / (fs / 2), 0.99), btype="low", analog=False, norm="mag"),
    )
    return signal.lfilter(b, a, x - x[0]) + x[0]


def rx_bandwidth(fmt: str, rate_gbd: float) -> float:
    """The reference receiver's -3 dB point: 0.75 x baud (NRZ), 0.5 x baud (PAM4)."""
    return RX_BW_X_BAUD[_fmt(fmt)] * rate_gbd * 1e9


def latency(t: np.ndarray, y: np.ndarray, data: Data) -> tuple[float, int]:
    """``(delay s, polarity +-1)`` maximizing ``|correlation|`` of ``y`` with the ideal symbol
    waveform (FFT correlation, lags ``0..max(3 UI, 2 ns)``)."""
    dt = t[1] - t[0]
    ideal = ideal_waveform(t, data)
    yy = y - y.mean()
    n_max = int(max(3 * data.ui, 2e-9) / dt) + 1
    c = signal.correlate(yy, ideal, mode="full", method="fft")[len(ideal) - 1 :][:n_max]
    k = int(np.argmax(abs(c)))
    return k * dt, (1 if c[k] >= 0 else -1)


def levels(fmt: str) -> np.ndarray:
    """The normalized symbol levels of ``fmt``, ascending."""
    return np.array([-1.0, 1.0]) if _fmt(fmt) == "nrz" else np.array([-1.0, -1 / 3, 1 / 3, 1.0])


def _groups(y, centers, half, sym_idx, nlv):
    """Samples within +-``half`` indices of each symbol center, grouped by transmitted level;
    None if a level is empty."""
    g: list[list[np.ndarray]] = [[] for _ in range(nlv)]
    for k, c in enumerate(centers):
        lo, hi = max(c - half, 0), min(c + half + 1, len(y))
        if lo < hi:
            g[sym_idx[k]].append(y[lo:hi])
    return None if any(not x for x in g) else [np.concatenate(x) for x in g]


def _openings(g) -> list[float]:
    return [float(g[i + 1].min() - g[i].max()) for i in range(len(g) - 1)]


def eye_metrics(
    t: np.ndarray,
    x: np.ndarray,
    data: Data,
    *,
    filtered: bool = True,
    full_scale: float = 1.0,
    n_phases: int = PHASES,
) -> dict[str, Any]:
    """Scorecard of one eye.

    Keys: ``eye_h_norm`` (worst sub-eye opening / ``full_scale``), the two eye WIDTHS --
    ``eye_w_ui_1s`` (fraction of the swept phases open at a +-one-sample window) and
    ``eye_w_ui_sample_window`` (the same fraction at the +-``SAMPLE_HALF_UI`` window the eye
    HEIGHT is measured over -- the stricter, self-consistent one, ~0.19 UI narrower on an ideal
    eye at the certified defaults; prefer these explicit names over confusing them). ``eye_w_ui``
    is also present, as a legacy alias of ``eye_w_ui_1s`` (the WIDE metric) for existing
    consumers -- plus ``sample_phases`` (= ``n_phases``, the sampling-phase
    count both widths were quantized over) and ``sample_half_ui`` (= ``SAMPLE_HALF_UI``, the
    window ``eye_w_ui_sample_window``/the height statistic use), so a row that changed either
    knob is visible in the row itself. Also: ``vecp_db`` (vertical eye-closure penalty, capped at
    ``VECP_CAP_DB``), ``er_db`` (unipolar input only, else nan), ``oma_norm``/``oma_db`` (outer
    level difference), plus ``rlm`` and ``pam4_eye_heights`` for PAM4, and the sampling point
    found (``sample_phase_ui``, ``latency_ps``, ``polarity``, ``levels``). ``ok`` is 0 when no
    phase samples every level. Plain floats only, so a row can go straight to a ledger.

    ``n_phases`` (default :data:`PHASES`, the certified value) is the sampling-phase count swept
    over one UI -- a caller that changes it gets a coarser/finer quantization of BOTH widths, and
    the value actually used rides in the result as ``sample_phases`` rather than being a silent
    module constant.
    """
    dt = data.ui / OVERSAMPLE
    unipolar = bool(np.min(x) >= 0)
    tu, y = resample(t, x, dt)
    if filtered:
        y = bessel_lowpass(tu, y, rx_bandwidth(data.fmt, data.rate_gbd))
    lag, sign = latency(tu, y, data)
    lv = levels(data.fmt)
    ks = np.arange(data.n_warm, data.n)  # the scored symbols
    sym_idx = [int(np.argmin(abs(lv - sign * s))) for s in data.syms[ks]]
    phases = np.linspace(0.0, 1.0, n_phases, endpoint=False)

    def centers(ph: float) -> np.ndarray:
        return np.rint((data.t0 + lag + (ks + ph) * data.ui - tu[0]) / dt).astype(int)

    half = round(SAMPLE_HALF_UI * OVERSAMPLE)
    best = None
    for ph in phases:
        g = _groups(y, centers(ph), half, sym_idx, len(lv))
        if g is None:
            continue
        h = _openings(g)
        if best is None or min(h) > best[1]:
            best = (float(ph), min(h), h, [float(z.mean()) for z in g])
    if best is None:
        return {
            "eye_h_norm": -1.0,
            "eye_w_ui_1s": 0.0,
            "eye_w_ui_sample_window": 0.0,
            "eye_w_ui": 0.0,  # legacy alias of eye_w_ui_1s -- see module docstring
            "sample_phases": n_phases,
            "sample_half_ui": SAMPLE_HALF_UI,
            "vecp_db": VECP_CAP_DB,
            "er_db": 0.0,
            "oma_db": -60.0,
            "ok": 0,
        }
    ph, h_min, heights, means = best
    p_hi, p_lo = means[-1], means[0]
    oma = p_hi - p_lo  # unclamped: any polarity
    sub = oma / (len(lv) - 1)  # one ideal eye's amplitude
    floor = FLOOR * full_scale

    def _open_fraction(half_idx: int) -> float:
        return (
            len(
                [
                    p
                    for p in phases
                    if (g := _groups(y, centers(p), half_idx, sym_idx, len(lv))) is not None
                    and min(_openings(g)) > 0
                ]
            )
            / n_phases
        )

    # TWO widths, because they are two different measurements and confusing them looks like a
    # design difference. `eye_w_ui_1s` counts the phases open at a +-ONE-SAMPLE window
    # (UI/OVERSAMPLE wide); `eye_w_ui_sample_window` counts them at the +-SAMPLE_HALF_UI window
    # the eye HEIGHT statistic above is taken over. The second is the stricter, self-consistent
    # one -- an eye is "open at this phase" under the same window its height was measured with --
    # and on an ideal eye it runs ~0.19 UI narrower. Report both under unambiguous names; `eye_w_ui`
    # below is kept ONLY as a legacy alias of the wide metric for existing consumers (see module
    # docstring) -- a new reader should always name `eye_w_ui_1s`/`eye_w_ui_sample_window`.
    open_frac_1s = _open_fraction(1)
    out: dict[str, Any] = {
        "sample_phase_ui": ph,
        "latency_ps": float(lag * 1e12),
        "polarity": sign,
        "levels": means,
        "eye_h_norm": float(h_min / full_scale),
        "eye_w_ui_1s": open_frac_1s,
        "eye_w_ui_sample_window": _open_fraction(half),
        "eye_w_ui": open_frac_1s,  # legacy alias of eye_w_ui_1s -- see module docstring
        "sample_phases": n_phases,
        "sample_half_ui": SAMPLE_HALF_UI,
        "oma_norm": float(oma),
        "oma_db": float(10 * np.log10(oma / full_scale)) if oma > 0 else -60.0,
        "er_db": float(10 * np.log10(max(p_hi, floor) / max(p_lo, floor)))
        if unipolar
        else float("nan"),
        "vecp_db": float(min(10 * np.log10(sub / h_min), VECP_CAP_DB))
        if h_min > 0 and sub > 0
        else VECP_CAP_DB,
        "ok": 1,
    }
    if data.fmt == "pam4":
        amps = np.diff(means)
        out["pam4_eye_heights"] = heights
        out["rlm"] = float(3 * amps.min() / amps.sum()) if amps.sum() > 0 else 0.0
    return out


def fold(
    t: np.ndarray, x: np.ndarray, data: Data, *, filtered: bool = True, n_ui: int = 2
) -> tuple[np.ndarray, np.ndarray]:
    """Eye-diagram coordinates (time within ``n_ui`` UI, value) over the scored window; for plots."""
    dt = data.ui / OVERSAMPLE
    tu, y = resample(t, x, dt)
    if filtered:
        y = bessel_lowpass(tu, y, rx_bandwidth(data.fmt, data.rate_gbd))
    w0, w1 = data.window()
    m = (tu >= w0) & (tu <= w1)
    return (tu[m] - data.t0) % (n_ui * data.ui), y[m]


# ------------------------------------------------------------------ registry ----------

# canonical name → the eye_metrics key it reads. Every one needs the stimulus description.
EYE_MEASUREMENTS: dict[str, str] = {
    "eye_h_norm": "eye_h_norm",
    "eye_w_ui_1s": "eye_w_ui_1s",
    "eye_w_ui_sample_window": "eye_w_ui_sample_window",
    "eye_w_ui": "eye_w_ui_1s",  # legacy bare spelling of the WIDE metric -- see module docstring
    "vecp_db": "vecp_db",
    "ecp_db": "vecp_db",  # the PAM4 spec spelling of the same closure penalty
    "er_db": "er_db",
    "oma_db": "oma_db",
    "oma_norm": "oma_norm",
    "rlm": "rlm",
    "eye_latency_ps": "latency_ps",
}
_EYE_REQUIRED = ("out", "fmt", "rate_gbd")


def _measure_eye(result: SimResult, recipe: dict[str, Any], analysis: str) -> float:
    t = np.real(np.asarray(result.wave(str(recipe.get("time", "time")), analysis)))
    v = np.real(np.asarray(result.wave(str(recipe["out"]), analysis)))
    if recipe.get("ref") is not None:  # differential read: out - ref
        v = v - np.real(np.asarray(result.wave(str(recipe["ref"]), analysis)))
    m = eye_metrics(
        t,
        v,
        Data.from_recipe(recipe),
        filtered=bool(recipe.get("filtered", True)),
        full_scale=float(recipe.get("full_scale", 1.0)),
    )
    return float(m.get(EYE_MEASUREMENTS[str(recipe["meas"]).strip()], float("nan")))


register_measurements(
    "eye",
    {name: _EYE_REQUIRED for name in EYE_MEASUREMENTS},
    _measure_eye,
    default_analysis="tran",
)
