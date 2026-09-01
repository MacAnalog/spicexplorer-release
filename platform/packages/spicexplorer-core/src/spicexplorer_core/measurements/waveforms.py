"""Engine-neutral small-signal / transient waveform measurements.

Pure ``numpy`` functions over raw arrays — no ``SimResult``, no engine coupling. These
are the canonical, version-controlled definitions of the amplifier figures of merit
(DC gain / UGF / phase-margin / f\\ :sub:`3dB` / GBW / rejection (CMRR/PSRR) / ICMR /
settling / slew / integrated noise / harmonic distortion (FFT and PSS-phasor routes) /
two-tone IIP3) that the metric registry (:mod:`spicexplorer_core.measurements.registry`) computes
from **both** ngspice and Spectre results. Keeping the math here — array-in, scalar-out —
makes every definition unit-testable against synthetic transfer functions with no
simulator, and gives ngspice and Spectre a single source of truth for "what UGF means".

Conventions
-----------
* Frequency-domain inputs are ``freq`` (Hz, > 0) and ``h`` (complex transfer function,
  i.e. the AC response for a **unit** stimulus). Interpolation for crossings is linear in
  ``log10(freq)`` — the natural axis for a Bode magnitude/phase.
* Phase margin uses ``PM = 180 - φ₀ + φ_ugf`` (degrees, from one unwrapped phase curve),
  which is correct whether the measured open-loop transfer has a non-inverting DC phase
  (≈ 0°) or an inverting one (≈ ±180°) — it measures accumulated lag relative to DC.
* A metric that cannot be evaluated (no unity-gain crossing, empty sweep, never settles)
  returns ``float('nan')`` rather than raising, so one absent metric degrades to a scorer
  penalty instead of crashing the loop.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

# NumPy 2.0 renamed ``trapz`` → ``trapezoid``; keep working on both.
_trapezoid = getattr(np, "trapezoid", None) or np.trapz  # type: ignore[attr-defined]

__all__ = [
    "magnitude_db",
    "dc_gain_db",
    "rejection_db",
    "icmr_band",
    "unity_gain_freq",
    "phase_margin",
    "bandwidth_3db",
    "gain_bandwidth_product",
    "magnitude_at_db",
    "band_worst_db",
    "level_crossing_freq",
    "settling_time",
    "slew_rate",
    "integrated_noise",
    "spot_noise_density",
    "phase_noise_dbc",
    "harmonic_amplitudes",
    "thd_from_waveform",
    "thd_from_harmonics",
    "hd_ratio",
    "sfdr_from_harmonics",
    "two_tone_indices",
    "iip3_from_harmonics",
    "iip3_from_two_tone",
]


# --------------------------------------------------------------------------- helpers
def _sorted_by_x(x: ArrayLike, y: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(x, y)`` sorted by ascending ``x`` (frequency/time need not arrive sorted)."""
    xa = np.asarray(x, dtype=float).ravel()
    ya = np.asarray(y).ravel()
    order = np.argsort(xa)
    return xa[order], ya[order]


def _log_interp_crossing(freq: np.ndarray, y: np.ndarray, level: float) -> float:
    """First frequency where ``y(f)`` crosses ``level``, interpolated linearly in log-f.

    ``freq`` must be ascending and strictly positive. Returns NaN if ``y`` never reaches
    ``level``.
    """
    if freq.size < 2:
        return float("nan")
    d = y - level
    # sign change (strict) between consecutive samples, or an exact hit
    exact = np.where(d == 0.0)[0]
    changes = np.where(np.signbit(d[:-1]) != np.signbit(d[1:]))[0]
    if exact.size and (changes.size == 0 or exact[0] <= changes[0]):
        return float(freq[exact[0]])
    if changes.size == 0:
        return float("nan")
    i = int(changes[0])
    lf0, lf1 = np.log10(freq[i]), np.log10(freq[i + 1])
    d0, d1 = d[i], d[i + 1]
    if d1 == d0:  # pragma: no cover - degenerate flat segment
        return float(freq[i])
    lfc = lf0 + (0.0 - d0) * (lf1 - lf0) / (d1 - d0)
    return float(10.0**lfc)


def _log_interp_y(freq: np.ndarray, y: np.ndarray, f0: float) -> float:
    """Linear interpolation of ``y`` at frequency ``f0``, in ``log10(freq)``."""
    return float(np.interp(np.log10(f0), np.log10(freq), y))


# ------------------------------------------------------------------- AC / small-signal
def magnitude_db(h: ArrayLike) -> np.ndarray:
    """20·log₁₀|h| — the Bode magnitude in dB."""
    return 20.0 * np.log10(np.abs(np.asarray(h)))


def dc_gain_db(freq: ArrayLike, h: ArrayLike) -> float:
    """|H| at the lowest swept frequency, in dB (H is the unit-stimulus AC response)."""
    freq, h = _sorted_by_x(freq, h)
    if freq.size == 0:
        return float("nan")
    return float(magnitude_db(h)[0])


def dc_gain_linear(freq: ArrayLike, h: ArrayLike) -> float:
    """|H| at the lowest swept frequency, LINEAR (V/V) — the buffer-gain convention.

    The closed-loop ``gain_cl`` vocabulary (analog-db amplifier class / CACE
    ``ac_params.gain``) specs the unity buffer in V/V (e.g. ``0.97..1.03``), not dB —
    the linear twin of :func:`dc_gain_db`.
    """
    freq, h = _sorted_by_x(freq, h)
    if freq.size == 0:
        return float("nan")
    return float(np.abs(h[0]))


def rejection_db(freq: ArrayLike, h: ArrayLike) -> float:
    """A rejection ratio (CMRR/PSRR), in dB: ``-|H|_dB`` at the lowest swept frequency.

    ``h`` is the *residual* the DUT lets through under a unit disturbance — the
    unity-buffer output with 1 V AC riding the common mode (CMRR) or the supply (PSRR).
    With a unit stimulus ``|vout| = 1/rejection``, so this is the negated DC-band floor of
    :func:`dc_gain_db` (the analog-db ``cmrr_vcm``/``psrr_vdd`` template contract:
    ``cmrr = -vdb(vout)`` reported at FSTART).
    """
    return -dc_gain_db(freq, h)


def icmr_band(
    vin: ArrayLike,
    vout: ArrayLike,
    vtrack: float,
    slope_tol: float | None = 0.1,
) -> tuple[float, float]:
    """Input common-mode range: the widest contiguous tracking band of a buffer DC sweep.

    ``vin``/``vout`` are the DC transfer of a unity-buffer-connected DUT (the analog-db
    amplifier ``linearity`` template). A sweep point *tracks* when it satisfies BOTH an
    absolute-error test ``|vout - vin| <= vtrack`` AND an *activity* test
    ``|dvout/dvin - 1| <= slope_tol``; the ICMR is the widest contiguous run of tracking
    points, returned as ``(icmr_min, icmr_max)`` on the ``vin`` axis — ``(nan, nan)`` when
    nothing tracks.

    The absolute-error test alone is NOT sufficient, and that is the whole reason the slope
    test exists (found 2026-07-20). It cannot distinguish "the follower is tracking" from
    "both ends happen to sit near the same rail": where the input pair is cut off, ``vout``
    is pinned at a supply rail, and if ``vin`` is near that same rail then ``|vout - vin|``
    is small *by coincidence* and the dead region scores as tracking. Measured on
    amp_033_ti_ldo_ref_selfbias (gf180mcu, 3.3 V, vtrack 50 mV): for vin = 0..0.05 V the
    NMOS pair is off and vout sits at ~0, yet ``verr = vin <= 50 mV``, so a threshold-only
    scan reported a 3.23 V band on a 3.3 V rail. Those dead points are CONTIGUOUS with the
    real band, so a run-length scan alone cannot reject them either. amp_032 showed the same
    artifact at the top rail (output railed high while vin walked up to VDD).

    Slope rather than rail-exclusion is used because it stays correct for rail-to-rail
    parts: an RRIO buffer genuinely tracking at 50 mV has ``dvout/dvin ~ 1`` and is kept,
    whereas a fixed "output must be >= N mV off the rail" margin would reject it. Pass
    ``slope_tol=None`` to recover the legacy threshold-only behaviour.
    """
    vin_a, vout_a = _sorted_by_x(vin, np.real(np.asarray(vout)))
    if vin_a.size == 0:
        return (float("nan"), float("nan"))
    ok = np.abs(vout_a - vin_a) <= float(vtrack)
    if slope_tol is not None and vin_a.size >= 2:
        with np.errstate(divide="ignore", invalid="ignore"):
            slope = np.gradient(vout_a, vin_a)  # central differences; one-sided at the ends
        ok &= np.isfinite(slope) & (np.abs(slope - 1.0) <= float(slope_tol))
    if not bool(np.any(ok)):
        return (float("nan"), float("nan"))
    padded = np.concatenate(([False], ok, [False]))
    edges = np.flatnonzero(np.diff(padded.astype(int)))
    starts, stops = edges[::2], edges[1::2]  # [start, stop) index pairs of each True run
    widest = int(np.argmax(stops - starts))
    lo, hi = int(starts[widest]), int(stops[widest]) - 1
    return (float(vin_a[lo]), float(vin_a[hi]))


def unity_gain_freq(freq: ArrayLike, h: ArrayLike) -> float:
    """First frequency where |H| = 0 dB (gain crosses unity), interpolated in log-f."""
    freq, h = _sorted_by_x(freq, h)
    return _log_interp_crossing(freq, magnitude_db(h), 0.0)


def phase_margin(freq: ArrayLike, h: ArrayLike) -> float:
    """Phase margin (deg): ``180 - φ₀ + φ_ugf`` from one unwrapped phase curve.

    ``φ₀`` is the phase at the lowest frequency and ``φ_ugf`` the phase at the unity-gain
    frequency. This form is sign-convention agnostic: a non-inverting open-loop transfer
    (φ₀ ≈ 0°) gives ``180 + φ_ugf`` and an inverting one (φ₀ ≈ ±180°) gives the same
    physical margin. Returns NaN if the gain never crosses unity.
    """
    freq, h = _sorted_by_x(freq, h)
    fugf = _log_interp_crossing(freq, magnitude_db(h), 0.0)
    if not np.isfinite(fugf):
        return float("nan")
    phase_deg = np.degrees(np.unwrap(np.angle(h)))
    phi0 = float(phase_deg[0])
    phi_ugf = _log_interp_y(freq, phase_deg, fugf)
    return 180.0 - phi0 + phi_ugf


def gain_margin_db(freq: ArrayLike, h: ArrayLike) -> float:
    """Gain margin (dB) of a loop-gain wave: ``-|T|_dB`` at the −180° phase crossing.

    ``h`` is a loop gain (e.g. the Spectre ``stb`` analysis' ``loopGain``). Like
    :func:`phase_margin` the crossover is sign-convention agnostic, but referenced to
    the lowest-frequency phase **snapped to its nearest multiple of 180°** (the nominal
    0°/±180° start, without the real in-band lag already accrued at the first swept
    point): the crossing frequency is where the unwrapped phase reaches that reference
    − 180°, and the margin is how far below unity the magnitude is there. Returns NaN
    when the phase never reaches the crossover in-band (a one/two-pole loop — gain
    margin is unbounded).
    """
    freq, h = _sorted_by_x(freq, h)
    if freq.size == 0:
        return float("nan")
    mag = magnitude_db(h)
    phase_deg = np.degrees(np.unwrap(np.angle(h)))
    phi_ref = round(float(phase_deg[0]) / 180.0) * 180.0
    f180 = _log_interp_crossing(freq, phase_deg, phi_ref - 180.0)
    if not np.isfinite(f180):
        return float("nan")
    return -_log_interp_y(freq, mag, f180)


def bandwidth_3db(freq: ArrayLike, h: ArrayLike) -> float:
    """−3 dB frequency relative to the DC (lowest-frequency) gain."""
    freq, h = _sorted_by_x(freq, h)
    mag = magnitude_db(h)
    if mag.size == 0:
        return float("nan")
    return _log_interp_crossing(freq, mag, float(mag[0]) - 3.0)


def magnitude_at_db(freq: ArrayLike, h: ArrayLike, f0: float) -> float:
    """|H| in dB at exactly ``f0``, interpolated linearly in ``log10(freq)``.

    A spec written "S11 at 32 GHz" or "gain at 1 kHz" is a *spot* value; a swept
    ``ac dec N`` grid rarely lands on the spot (``dec 20`` from 100 MHz never samples
    32 or 50 GHz — its last in-band points are 31.62 and 44.67 GHz), so reading the
    nearest bin silently reports a neighbouring frequency. Returns NaN when the sweep
    has fewer than two points or ``f0`` is outside the swept band (no extrapolation).
    """
    freq, h = _sorted_by_x(freq, h)
    if freq.size < 2 or f0 <= 0.0 or freq[0] <= 0.0 or not (freq[0] <= f0 <= freq[-1]):
        return float("nan")
    return _log_interp_y(freq, magnitude_db(h), float(f0))


def band_worst_db(
    freq: ArrayLike,
    h: ArrayLike,
    f_edge: float,
    *,
    f_start: float | None = None,
    worst: str = "max",
) -> float:
    """Worst |H| (dB) over the band ``[f_start, f_edge]`` — **including the band edges**.

    The value every "≤ −10 dB up to f_edge" / "≥ x dB across the band" spec means: the
    max (``worst="max"``, reflection / rejection specs) or min (``worst="min"``, gain
    flatness specs) of the magnitude over the band, where the two edges are evaluated
    by log-f interpolation whether or not the sweep grid samples them. Reading
    ``max(mag[freq <= f_edge])`` off a ``dec 20`` grid stops at the last grid point
    *below* the edge and flatters a rising reflection curve by whatever it gains
    between that point and the edge (0.04–0.5 dB on the PAM-4 driver — the difference
    between passing and failing). ``f_start`` defaults to the sweep's lowest frequency.
    Returns NaN if the band lies outside the sweep.
    """
    freq, h = _sorted_by_x(freq, h)
    if freq.size < 2 or freq[0] <= 0.0 or f_edge <= 0.0:
        return float("nan")
    lo = float(freq[0]) if f_start is None else float(f_start)
    hi = float(f_edge)
    if not (freq[0] <= lo < hi <= freq[-1]):
        return float("nan")
    mag = magnitude_db(h)
    inside = (freq >= lo) & (freq <= hi)
    vals = [_log_interp_y(freq, mag, lo), _log_interp_y(freq, mag, hi)]
    if inside.any():
        vals.append(float(mag[inside].max() if worst == "max" else mag[inside].min()))
    return float(max(vals) if worst == "max" else min(vals))


def level_crossing_freq(freq: ArrayLike, h: ArrayLike, level_db: float) -> float:
    """First frequency where |H| (dB) crosses ``level_db``, log-f interpolated.

    The grid-independent twin of a band-edge spec: "S11 holds −10 dB up to X GHz"
    reported as X (the −10 dB edge) rather than as a value at a frequency. NaN if the
    magnitude never reaches ``level_db``.
    """
    freq, h = _sorted_by_x(freq, h)
    if freq.size < 2 or freq[0] <= 0.0:
        return float("nan")
    return _log_interp_crossing(freq, magnitude_db(h), float(level_db))


def gain_bandwidth_product(freq: ArrayLike, h: ArrayLike) -> float:
    """Linear DC gain × f\\ :sub:`3dB`. For a dominant-pole response this ≈ UGF."""
    freq, h = _sorted_by_x(freq, h)
    if freq.size == 0:
        return float("nan")
    g0 = float(np.abs(h[0]))
    f3 = bandwidth_3db(freq, h)
    return g0 * f3


# ----------------------------------------------------------------------------- transient
def settling_time(
    t: ArrayLike,
    v: ArrayLike,
    *,
    final: float | None = None,
    tol: float | None = None,
    tol_frac: float | None = None,
    t_start: float = 0.0,
) -> float:
    """Time (measured from ``t_start``) after which ``|v − final|`` stays inside the band.

    ``final`` defaults to the last sample. The band is an absolute ``tol`` (volts) **or** a
    fraction ``tol_frac`` of the step ``|final − v(t_start)|`` — give exactly one. Returns
    ``0.0`` if never outside the band, and ``NaN`` if it leaves the band and never
    re-enters within the captured window.
    """
    t, v = _sorted_by_x(t, np.real(np.asarray(v)))
    if t.size == 0:
        return float("nan")
    if final is None:
        final = float(v[-1])
    if tol is None:
        if tol_frac is None:
            raise ValueError("settling_time needs either `tol` or `tol_frac`.")
        v0 = float(np.interp(t_start, t, v))
        tol = abs(float(tol_frac) * (final - v0))
    outside = np.where(np.abs(v - final) > tol)[0]
    if outside.size == 0:
        return 0.0
    last = int(outside[-1])
    if last + 1 >= t.size:
        return float("nan")  # still outside at the end of the window — never settled
    return float(t[last + 1] - t_start)


def slew_rate(t: ArrayLike, v: ArrayLike) -> float:
    """Peak ``|dv/dt|`` over the waveform (volts/second)."""
    t, v = _sorted_by_x(t, np.real(np.asarray(v)))
    if t.size < 2:
        return float("nan")
    dt = np.diff(t)
    dv = np.diff(v)
    good = dt != 0.0
    if not np.any(good):
        return float("nan")
    return float(np.max(np.abs(dv[good] / dt[good])))


# --------------------------------------------------------------------------------- noise
def integrated_noise(freq: ArrayLike, density: ArrayLike) -> float:
    """RMS integral of a noise spectral density over the swept band.

    ``density`` is a one-sided spectral density (e.g. V/√Hz); the result is the total RMS
    (e.g. V) via a trapezoid integral of the power density over frequency.
    """
    freq, dens = _sorted_by_x(freq, np.abs(np.asarray(density)))
    if freq.size < 2:
        return float("nan")
    return float(np.sqrt(_trapezoid(dens**2, freq)))


def spot_noise_density(freq: ArrayLike, density: ArrayLike, f0: float) -> float:
    """Noise spectral density at one frequency (e.g. V/√Hz at ``f0``), log-f interpolated.

    The "spot noise" figure of merit: the |density| trace interpolated at ``f0`` linearly
    in ``log10(freq)`` (the natural Bode axis, matching the crossing math above). Returns
    NaN when the sweep has fewer than two points or ``f0`` falls outside the swept band —
    extrapolating a noise density is a lie, not a measurement.
    """
    freq, dens = _sorted_by_x(freq, np.abs(np.asarray(density)))
    if freq.size < 2 or not (freq[0] <= f0 <= freq[-1]) or f0 <= 0.0 or freq[0] <= 0.0:
        return float("nan")
    return _log_interp_y(freq, dens, f0)


def phase_noise_dbc(
    freq: ArrayLike, density: ArrayLike, f_offset: float, *, carrier_ampl: float
) -> float:
    """Single-sideband phase noise ℒ(f_offset) in dBc/Hz from a voltage-noise density.

    For a carrier of amplitude ``carrier_ampl`` (V peak, carrier power A²/2) with a
    one-sided voltage-noise spectral density ``density`` (V/√Hz) around it — e.g. a
    Spectre ``pnoise`` output trace — the SSB noise-to-carrier ratio at offset
    ``f_offset`` is ``ℒ(f) = Sv(f) / (A²/2)`` per Hz, i.e.
    ``10·log10(density(f)² / (carrier_ampl²/2))`` dBc/Hz. (This is total noise around
    the carrier — AM+PM; for the small-offset white/flicker sidebands of an oscillator
    it is the conventional phase-noise figure.) NaN when the spot density cannot be
    interpolated or the carrier amplitude is non-positive.
    """
    if carrier_ampl <= 0.0:
        return float("nan")
    spot = spot_noise_density(freq, density, f_offset)
    if not np.isfinite(spot) or spot <= 0.0:
        return float("nan")
    return float(10.0 * np.log10(spot**2 / (carrier_ampl**2 / 2.0)))


# ---------------------------------------------------------------------- distortion (THD)
def harmonic_amplitudes(
    t: ArrayLike,
    v: ArrayLike,
    f0: float,
    *,
    n_harmonics: int = 5,
    n_periods: int | None = None,
    samples_per_period: int = 64,
    t_start: float | None = None,
) -> np.ndarray:
    """Peak amplitudes ``[A₁, A₂, …, A_n]`` of the fundamental ``f0`` and its harmonics.

    Extracted from a transient waveform ``v(t)`` by **coherent** resampling: the analysis
    window is trimmed to a whole number of ``f0`` periods (ending at the last sample) and
    resampled onto a uniform grid, so an integer-bin ``rfft`` places every harmonic exactly
    on a bin — no spectral leakage, no window function needed (the discrete analogue of
    SPICE ``.four``). ``Aₖ`` is the **peak** amplitude of the k-th harmonic (twice the
    one-sided rfft magnitude). The startup transient is excluded by analysing the *last*
    whole periods of the record (or everything after ``t_start`` when given).

    Parameters mirror a ``.four`` control: ``n_harmonics`` harmonics returned (index 0 is
    the fundamental), ``n_periods`` caps how many whole fundamental periods to analyse
    (default: as many as fit), ``samples_per_period`` sets the resample density (must exceed
    ``2·n_harmonics`` to resolve the top harmonic). Returns an array of length
    ``n_harmonics`` whose unresolvable entries are ``NaN``; an all-``NaN`` array when the
    record is too short, ``f0`` is non-positive, or fewer than one whole period is captured.
    """
    t, v = _sorted_by_x(t, np.real(np.asarray(v)))
    n_harmonics = int(n_harmonics)
    if t.size < 2 or not np.isfinite(f0) or f0 <= 0.0 or n_harmonics < 1:
        return np.full(max(n_harmonics, 0), float("nan"))

    period = 1.0 / float(f0)
    t_end = float(t[-1])
    t_lo = float(t[0]) if t_start is None else float(t_start)
    n_avail = int(np.floor((t_end - t_lo) / period))
    if n_avail < 1:
        return np.full(n_harmonics, float("nan"))
    n_use = n_avail if n_periods is None else min(int(n_periods), n_avail)
    if n_use < 1:
        return np.full(n_harmonics, float("nan"))

    # Uniform grid over EXACTLY n_use fundamental periods (coherent sampling → the
    # fundamental lands on bin n_use and harmonic k on bin k·n_use). endpoint=False so the
    # window is periodic-consistent (the closing sample would duplicate the opening one).
    n_samples = int(samples_per_period) * n_use
    tu = np.linspace(t_end - n_use * period, t_end, n_samples, endpoint=False)
    vu = np.interp(tu, t, v)

    mag = np.abs(np.fft.rfft(vu)) / n_samples  # rfft magnitude, normalized by sample count
    amps = np.full(n_harmonics, float("nan"))
    for k in range(1, n_harmonics + 1):
        bin_k = k * n_use
        if bin_k < mag.size:
            amps[k - 1] = 2.0 * mag[bin_k]  # one-sided → peak amplitude
    return amps


def thd_from_waveform(
    t: ArrayLike,
    v: ArrayLike,
    f0: float,
    *,
    n_harmonics: int = 5,
    n_periods: int | None = None,
    samples_per_period: int = 64,
    t_start: float | None = None,
) -> float:
    """Total harmonic distortion of ``v(t)`` at fundamental ``f0`` — a linear ratio.

    ``THD = √(A₂² + A₃² + … + A_n²) / A₁`` from :func:`harmonic_amplitudes` (the IEEE
    definition, referenced to the fundamental). Engine-neutral: it reads any transient
    output wave, so ngspice and Spectre transient runs share one THD definition. The
    ``{meas: thd}`` recipe returns this ratio; ``thd_pct`` (×100) and ``thd_db``
    (20·log₁₀) are the same number rescaled. Returns ``NaN`` when the fundamental cannot be
    measured (record too short / no fundamental energy). Keyword args pass through to
    :func:`harmonic_amplitudes`.
    """
    amps = harmonic_amplitudes(
        t, v, f0,
        n_harmonics=n_harmonics,
        n_periods=n_periods,
        samples_per_period=samples_per_period,
        t_start=t_start,
    )
    if amps.size < 2 or not np.isfinite(amps[0]) or amps[0] == 0.0:
        return float("nan")
    harmonics = amps[1:][np.isfinite(amps[1:])]
    return float(np.sqrt(np.sum(harmonics**2)) / amps[0])


def thd_from_harmonics(harmonics: ArrayLike, *, n_harmonics: int | None = None) -> float:
    """THD from a complex harmonic-phasor array (index 0 = DC, 1 = fundamental, 2 = HD2, …).

    ``THD = √(Σ_{k≥2} |Hₖ|²) / |H₁|`` — the same IEEE ratio as :func:`thd_from_waveform`, but
    read straight from an engine's own harmonics (a Spectre ``pss`` fd-PSF: no resample, no
    window). ``n_harmonics`` caps how many harmonics past the fundamental to include (all
    present by default). Returns ``NaN`` when there is no usable fundamental.
    """
    mag = np.abs(np.asarray(harmonics)).ravel()
    if mag.size < 2 or not np.isfinite(mag[1]) or mag[1] == 0.0:
        return float("nan")
    hi = mag.size if n_harmonics is None else min(mag.size, 2 + int(n_harmonics))
    tail = mag[2:hi][np.isfinite(mag[2:hi])]
    return float(np.sqrt(np.sum(tail**2)) / mag[1])


def hd_ratio(harmonics: ArrayLike, n: int) -> float:
    """The nth-harmonic distortion ratio ``|Hₙ| / |H₁|`` from a harmonic-phasor array (n ≥ 2)."""
    mag = np.abs(np.asarray(harmonics)).ravel()
    if n < 2 or n >= mag.size or not np.isfinite(mag[1]) or mag[1] == 0.0:
        return float("nan")
    return float(mag[n] / mag[1])


def sfdr_from_harmonics(harmonics: ArrayLike) -> float:
    """Spurious-free dynamic range ``|H₁| / max_{k≥2} |Hₖ|`` (linear) from a harmonic array."""
    mag = np.abs(np.asarray(harmonics)).ravel()
    if mag.size < 3 or not np.isfinite(mag[1]) or mag[1] == 0.0:
        return float("nan")
    tail = mag[2:][np.isfinite(mag[2:])]
    peak = float(np.max(tail)) if tail.size else 0.0
    return float(mag[1] / peak) if peak > 0.0 else float("inf")


# ---------------------------------------------------------------- two-tone (IM3 / IIP3)
def two_tone_indices(f1: float, f2: float, max_den: int = 64) -> tuple[float, int, int]:
    """Rationalize a two-tone pair onto a common fundamental: ``(f0, n1, n2)``.

    ``f1 = n1·f0`` and ``f2 = n2·f0`` with the smallest integer ``n1 < n2`` (found via a
    continued-fraction approximation of ``f1/f2``, denominators up to ``max_den``). This is
    the beat-frequency trick that lets a *single-fundamental* steady-state analysis (Spectre
    ``pss`` at ``f0``) resolve both tones AND their intermodulation products as plain
    harmonics — e.g. 0.9/1.0 MHz → ``f0 = 100 kHz``, ``n1 = 9``, ``n2 = 10``, IM3 at
    ``2n1−n2 = 8`` and ``2n2−n1 = 11``.
    """
    from fractions import Fraction

    if not (f1 > 0.0 and f2 > 0.0) or f1 == f2:
        raise ValueError(f"two tones need two distinct positive frequencies, got {f1}, {f2}")
    lo, hi = (f1, f2) if f1 < f2 else (f2, f1)
    frac = Fraction(lo / hi).limit_denominator(int(max_den))
    n1, n2 = frac.numerator, frac.denominator
    return hi / n2, int(n1), int(n2)


def iip3_from_harmonics(harmonics: ArrayLike, n1: int, n2: int, *, ampl_in: float) -> float:
    """Input-referred third-order intercept (V, amplitude) from common-fundamental harmonics.

    ``harmonics`` is the amplitude/phasor array indexed by harmonic number of the COMMON
    fundamental ``f0`` (index 0 = DC — the PSS fd-PSF layout; a plain ``[A₁…]`` amplitude
    array from :func:`harmonic_amplitudes` should be padded with a leading DC entry by the
    caller). With both tones driven at ``ampl_in``, the classic single-point extrapolation is
    ``A_IIP3 = A_in · √(A_tone / A_IM3)`` (the IM3 products at ``2n1−n2``/``2n2−n1`` grow 3 dB
    per input dB against the tone's 1 dB — the intercept sits half the dBc gap above Pin).
    The weaker tone and the stronger IM3 side are used (the conservative reading). NaN when a
    needed index is missing/unresolved.
    """
    mag = np.abs(np.asarray(harmonics)).ravel()
    lo3, hi3 = 2 * n1 - n2, 2 * n2 - n1
    needed = [n1, n2, hi3] + ([lo3] if lo3 > 0 else [])
    if any(k >= mag.size or not np.isfinite(mag[k]) for k in needed):
        return float("nan")
    tone = float(min(mag[n1], mag[n2]))
    im3 = float(max(mag[hi3], mag[lo3])) if lo3 > 0 else float(mag[hi3])
    if tone <= 0.0 or not np.isfinite(tone):
        return float("nan")
    if im3 <= 0.0:
        return float("inf")  # no measurable IM3 → intercept beyond the record's floor
    return float(ampl_in) * float(np.sqrt(tone / im3))


def iip3_from_two_tone(
    t: ArrayLike,
    v: ArrayLike,
    f1: float,
    f2: float,
    *,
    ampl_in: float,
    n_periods: int | None = None,
    samples_per_period: int = 64,
    t_start: float | None = None,
) -> float:
    """IIP3 (V, amplitude) from a two-tone *transient* — the engine-neutral (ngspice) route.

    Rationalizes the tones onto their common fundamental (:func:`two_tone_indices`), pulls
    the tone + IM3 amplitudes with the same coherent-resample harmonic extraction THD uses
    (:func:`harmonic_amplitudes` at ``f0``), and extrapolates the intercept
    (:func:`iip3_from_harmonics`). The record must capture whole periods of the *beat*
    ``f0`` — for 0.9/1.0 MHz that is ≥ 1 period of 100 kHz, comfortably several.
    """
    f0, n1, n2 = two_tone_indices(f1, f2)
    n_h = 2 * n2 - n1  # the highest index needed (the upper IM3 product)
    amps = harmonic_amplitudes(
        t,
        v,
        f0,
        n_harmonics=n_h,
        n_periods=n_periods,
        samples_per_period=max(int(samples_per_period), 4 * n_h),
        t_start=t_start,
    )
    padded = np.concatenate(([0.0], np.asarray(amps)))  # index k ↔ k·f0 (PSS layout)
    return iip3_from_harmonics(padded, n1, n2, ampl_in=ampl_in)
