"""Unit tests for the engine-neutral measurement library.

The waveform math is validated against *analytic* transfer functions (single-pole,
two-pole, sign-inverted) and closed-form step/ramp/white-noise cases — no simulator — so
these pin the canonical definitions of DC gain / UGF / phase margin / f3dB / GBW /
settling / slew / integrated noise that both ngspice and Spectre feed.
"""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_core.measurements import registry
from spicexplorer_core.measurements import waveforms as wf


# ------------------------------------------------------------------ analytic fixtures
def _freq_grid(f0: float = 1.0, f1: float = 1e9, n: int = 4000) -> np.ndarray:
    return np.logspace(np.log10(f0), np.log10(f1), n)


def _single_pole(freq: np.ndarray, a0: float = 1000.0, fp: float = 1e3) -> np.ndarray:
    """H(f) = a0 / (1 + j f/fp)."""
    return a0 / (1.0 + 1j * freq / fp)


def _two_pole(
    freq: np.ndarray, a0: float = 1000.0, fp1: float = 1e3, fp2: float = 1e6
) -> np.ndarray:
    return a0 / ((1.0 + 1j * freq / fp1) * (1.0 + 1j * freq / fp2))


# ------------------------------------------------------------------------- AC metrics
def test_dc_gain_db_single_pole():
    freq = _freq_grid()
    h = _single_pole(freq, a0=1000.0)  # 60 dB
    assert wf.dc_gain_db(freq, h) == pytest.approx(60.0, abs=0.05)


def test_bandwidth_3db_matches_pole():
    freq = _freq_grid()
    h = _single_pole(freq, a0=1000.0, fp=1e3)
    assert wf.bandwidth_3db(freq, h) == pytest.approx(1e3, rel=0.02)


def test_ugf_and_gbw_single_pole():
    freq = _freq_grid()
    h = _single_pole(freq, a0=1000.0, fp=1e3)  # GBW = a0*fp = 1e6
    assert wf.unity_gain_freq(freq, h) == pytest.approx(1e6, rel=0.02)
    # GBW = linear DC gain * f3dB ≈ UGF for a dominant-pole response
    assert wf.gain_bandwidth_product(freq, h) == pytest.approx(1e6, rel=0.02)


def test_phase_margin_single_pole_is_90():
    freq = _freq_grid()
    h = _single_pole(freq, a0=1000.0, fp=1e3)
    assert wf.phase_margin(freq, h) == pytest.approx(90.0, abs=1.0)


def test_phase_margin_two_pole_degraded():
    # a second pole near the single-pole UGF (a0*fp1) pulls the crossover down and adds
    # lag → a finite margin well below the single-pole 90° (analytically ≈ 52°).
    freq = _freq_grid()
    h = _two_pole(freq, a0=1000.0, fp1=1e3, fp2=1e6)
    pm = wf.phase_margin(freq, h)
    assert 48.0 < pm < 56.0


def test_phase_margin_sign_agnostic():
    """An inverting open-loop transfer (DC phase ≈ 180°) yields the same margin — the
    definition measures accumulated lag relative to DC, not an absolute phase."""
    freq = _freq_grid()
    h = _single_pole(freq, a0=1000.0, fp=1e3)
    assert wf.phase_margin(freq, -h) == pytest.approx(wf.phase_margin(freq, h), abs=1e-6)


def test_ugf_nan_when_gain_never_crosses_unity():
    freq = _freq_grid()
    h = np.full_like(freq, 2.0, dtype=complex)  # |H| = 2 everywhere, never 0 dB
    assert np.isnan(wf.unity_gain_freq(freq, h))
    assert np.isnan(wf.phase_margin(freq, h))


# -------------------------------------------------------------------- transient metrics
def test_settling_time_first_order():
    tau = 1e-6
    t = np.linspace(0.0, 20e-6, 20001)
    v = 1.0 - np.exp(-t / tau)  # unit step, final = 1
    # 2% band → t_settle = tau*ln(50) ≈ 3.912 µs
    ts = wf.settling_time(t, v, tol_frac=0.02)
    assert ts == pytest.approx(tau * np.log(50.0), rel=0.02)


def test_settling_time_absolute_tol_and_never_out():
    t = np.linspace(0.0, 1e-6, 1001)
    v = np.full_like(t, 0.5)  # already at final, never leaves the band
    assert wf.settling_time(t, v, final=0.5, tol=1e-3) == 0.0


def test_slew_rate_linear_ramp_exact():
    t = np.linspace(0.0, 1e-6, 501)
    v = 3.0e6 * t  # slope 3e6 V/s
    assert wf.slew_rate(t, v) == pytest.approx(3.0e6, rel=1e-6)


# ------------------------------------------------------------------------ noise metric
def test_integrated_white_noise():
    freq = np.linspace(1.0, 1e6, 200001)
    dens = np.full_like(freq, 1e-9)  # 1 nV/√Hz white
    rms = wf.integrated_noise(freq, dens)
    assert rms == pytest.approx(1e-9 * np.sqrt(1e6 - 1.0), rel=1e-3)


# --------------------------------------------------------------------- distortion (THD)
def _multitone(
    f0: float,
    amps,
    *,
    n_periods: int = 8,
    spp: int = 200,
    phases=None,
    dc: float = 0.0,
    t_start: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Uniformly-sampled Σ sinusoids: ``amps[k]`` is the peak amplitude of harmonic ``k+1``.

    A synthetic transient with *exactly known* harmonic content — the ground truth the
    coherent-FFT extractor must recover (independent of DC offset and per-tone phase).
    """
    n = int(n_periods * spp)
    t = t_start + np.arange(n) / (f0 * spp)  # spp samples/period over n_periods periods
    phases = phases if phases is not None else [0.0] * len(amps)
    v = np.full(n, float(dc))
    for k, (a, ph) in enumerate(zip(amps, phases), start=1):
        v = v + a * np.sin(2.0 * np.pi * k * f0 * t + ph)
    return t, v


def test_harmonic_amplitudes_recovers_known_tones():
    f0 = 1.0e3
    t, v = _multitone(f0, [1.0, 0.10, 0.05, 0.0, 0.0])
    got = wf.harmonic_amplitudes(t, v, f0, n_harmonics=5)
    assert got[0] == pytest.approx(1.0, rel=1e-3)
    assert got[1] == pytest.approx(0.10, rel=1e-3)
    assert got[2] == pytest.approx(0.05, rel=1e-3)
    # unexcited harmonics sit at the resample's linear-interpolation spurious floor —
    # ≥60 dB below the fundamental, far under any THD of interest, not bit-zero.
    assert got[3] == pytest.approx(0.0, abs=1e-3)
    assert got[4] == pytest.approx(0.0, abs=1e-3)


def test_thd_from_waveform_matches_closed_form_dc_and_phase_agnostic():
    f0 = 1.0e3
    # a DC offset and arbitrary per-tone phases must NOT move THD (fundamental-referenced)
    t, v = _multitone(f0, [1.0, 0.10, 0.05], dc=0.4, phases=[0.3, 1.1, -0.7])
    expected = np.sqrt(0.10**2 + 0.05**2) / 1.0
    assert wf.thd_from_waveform(t, v, f0, n_harmonics=5) == pytest.approx(expected, rel=2e-3)


def test_thd_pure_sine_is_zero():
    f0 = 2.0e6
    t, v = _multitone(f0, [0.5])
    assert wf.thd_from_waveform(t, v, f0) == pytest.approx(0.0, abs=1e-6)


def test_thd_nan_when_too_short_or_bad_f0():
    f0 = 1.0e3
    t = np.linspace(0.0, 0.5e-3, 10)  # < 1 period of 1 kHz
    v = np.sin(2.0 * np.pi * f0 * t)
    assert np.isnan(wf.thd_from_waveform(t, v, f0))
    assert np.isnan(wf.thd_from_waveform(t, v, 0.0))  # non-positive fundamental


def test_thd_n_periods_excludes_startup():
    f0 = 1.0e3
    t, v = _multitone(f0, [1.0, 0.0, 0.05], n_periods=12)  # clean THD = 0.05
    spp = v.size // 12
    # corrupt the first 4 periods with a large spurious 2nd-harmonic tone
    v[: 4 * spp] += 0.5 * np.sin(2.0 * np.pi * 2.0 * f0 * t[: 4 * spp])
    # analysing only the last 6 whole periods sees the clean tail
    assert wf.thd_from_waveform(t, v, f0, n_periods=6) == pytest.approx(0.05, rel=5e-3)


# ---------------------------------------------------------- registry over a fake result
class _FakeResult:
    """Minimal SimResult-shaped stub: preloaded waves + op scalars, mergeable."""

    def __init__(self, waves: dict, scalars: dict | None = None) -> None:
        self._w = waves
        self._s = dict(scalars or {})
        self._merged: dict[str, float] = {}

    def wave(self, name: str, analysis: str) -> np.ndarray:
        return np.asarray(self._w[name])

    def scalar(self, name: str, analysis: str) -> float:
        if name in self._merged:
            return self._merged[name]
        return float(self._s.get(name, np.nan))

    def merge_scalars(self, d: dict) -> None:
        self._merged.update({k: float(v) for k, v in d.items()})


def test_registry_measure_ac_and_op():
    freq = _freq_grid()
    h = _single_pole(freq, a0=1000.0, fp=1e3)
    res = _FakeResult({"frequency": freq, "vout": h}, {"i(vvdd)": -2.5e-4})

    assert registry.measure(res, {"meas": "dcgain", "out": "vout"}, default_analysis="ac") == pytest.approx(60.0, abs=0.05)
    assert registry.measure(res, {"meas": "ugf", "out": "vout"}, default_analysis="ac") == pytest.approx(1e6, rel=0.02)
    assert registry.measure(res, {"meas": "pm", "out": "vout"}, default_analysis="ac") == pytest.approx(90.0, abs=1.0)
    # i_supply returns magnitude by default
    assert registry.measure(res, {"meas": "i_supply", "probe": "i(vvdd)"}, default_analysis="op") == pytest.approx(2.5e-4)
    assert registry.measure(res, {"meas": "i_supply", "probe": "i(vvdd)", "signed": True}, default_analysis="op") == pytest.approx(-2.5e-4)


def test_registry_measure_thd_tran():
    f0 = 1.0e3
    t, v = _multitone(f0, [1.0, 0.10, 0.05], dc=0.6)
    res = _FakeResult({"time": t, "vout": v})
    expected = np.sqrt(0.10**2 + 0.05**2)  # referenced to a unit fundamental

    r = registry.measure(res, {"meas": "thd", "out": "vout", "f0": f0}, default_analysis="tran")
    assert r == pytest.approx(expected, rel=2e-3)
    assert registry.measure(res, {"meas": "thd_pct", "out": "vout", "f0": f0}, default_analysis="tran") == pytest.approx(expected * 100.0, rel=2e-3)
    assert registry.measure(res, {"meas": "thd_db", "out": "vout", "f0": f0}, default_analysis="tran") == pytest.approx(20.0 * np.log10(expected), rel=1e-3)


def test_harmonic_distortion_from_phasors():
    """The native-PSS harmonic math over a known complex phasor array (DC, fund, HD2, …)."""
    from spicexplorer_core.measurements import waveforms as wf

    H = np.array([0.6, 1.0, 0.02, 0.01, 0.005], dtype=complex)
    assert wf.thd_from_harmonics(H) == pytest.approx(np.sqrt(0.02**2 + 0.01**2 + 0.005**2))
    assert wf.hd_ratio(H, 2) == pytest.approx(0.02)
    assert wf.hd_ratio(H, 3) == pytest.approx(0.01)
    assert wf.sfdr_from_harmonics(H) == pytest.approx(1.0 / 0.02)  # fund / largest spur
    assert wf.thd_from_harmonics(H, n_harmonics=1) == pytest.approx(0.02)  # cap to HD2 only
    assert np.isnan(wf.hd_ratio(H, 9))  # out of range
    assert np.isnan(wf.thd_from_harmonics(np.array([0.0, 0.0], dtype=complex)))  # no fundamental


def test_registry_measure_pss_harmonics():
    """The `{meas: thd_pss|hd2|hd3|hd|sfdr}` recipes read the pss fd-PSF complex phasors."""
    H = np.array([0.6, 0.1, 7.5e-3, 1.0e-3, 2.0e-4], dtype=complex)  # DC, fund, HD2, HD3, HD4
    res = _FakeResult({"vout": H})
    thd_ref = np.sqrt(7.5e-3**2 + 1.0e-3**2 + 2.0e-4**2) / 0.1

    assert registry.measure(res, {"meas": "thd_pss", "out": "vout"}, default_analysis="pss") == pytest.approx(thd_ref)
    assert registry.measure(res, {"meas": "thd_pss_pct", "out": "vout"}, default_analysis="pss") == pytest.approx(thd_ref * 100.0)
    assert registry.measure(res, {"meas": "thd_pss_db", "out": "vout"}, default_analysis="pss") == pytest.approx(20.0 * np.log10(thd_ref))
    assert registry.measure(res, {"meas": "hd2", "out": "vout"}, default_analysis="pss") == pytest.approx(7.5e-3 / 0.1)
    assert registry.measure(res, {"meas": "hd3", "out": "vout"}, default_analysis="pss") == pytest.approx(1.0e-3 / 0.1)
    assert registry.measure(res, {"meas": "hd2_db", "out": "vout"}, default_analysis="pss") == pytest.approx(20.0 * np.log10(7.5e-3 / 0.1))
    assert registry.measure(res, {"meas": "hd", "out": "vout", "n": 4}, default_analysis="pss") == pytest.approx(2.0e-4 / 0.1)
    assert registry.measure(res, {"meas": "sfdr", "out": "vout"}, default_analysis="pss") == pytest.approx(0.1 / 7.5e-3)
    assert registry.measure(res, {"meas": "sfdr_db", "out": "vout"}, default_analysis="pss") == pytest.approx(20.0 * np.log10(0.1 / 7.5e-3))
    # n_harmonics caps the THD sum (HD2 only)
    assert registry.measure(res, {"meas": "thd_pss", "out": "vout", "n_harmonics": 1}, default_analysis="pss") == pytest.approx(7.5e-3 / 0.1)


def test_registry_pss_names_registered_and_validated():
    names = registry.known_measurements()
    for m in ("thd_pss", "thd_pss_pct", "thd_pss_db", "hd2", "hd3", "hd2_db", "hd3_db", "hd", "hd_db", "sfdr", "sfdr_db"):
        assert m in names, m
    registry.validate_recipe("dist", {"meas": "hd", "out": "vout", "n": 2})  # ok
    with pytest.raises(ValueError):
        registry.validate_recipe("dist", {"meas": "hd", "out": "vout"})  # missing n
    with pytest.raises(ValueError):
        registry.validate_recipe("dist", {"meas": "hd2"})  # missing out


def test_registry_validate_recipe_rejects_unknown_and_missing():
    with pytest.raises(ValueError, match="unknown measurement"):
        registry.validate_recipe("g", {"meas": "not_a_metric", "out": "vout"})
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("g", {"meas": "ugf"})  # missing `out`
    with pytest.raises(ValueError, match="tol"):
        registry.validate_recipe("g", {"meas": "t_settle", "out": "vout"})  # no tol/tol_frac
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("g", {"meas": "thd", "out": "vout"})  # missing `f0`
    # well-formed recipes validate silently
    registry.validate_recipe("g", {"meas": "t_settle", "out": "vout", "tol_frac": 0.02})
    registry.validate_recipe("g", {"meas": "thd", "out": "vout", "f0": 1e3})


def test_band_edge_reads_are_grid_independent():
    """The PAM-4 instrument bug: a `dec 20` grid from 100 MHz never samples 32/50 GHz."""
    fp = 20e9
    coarse = 1e8 * 10 ** (np.arange(0, 61) / 20.0)          # ac dec 20 100MHz..100GHz
    fine = np.logspace(8, 11, 20001)
    h_c, h_f = _single_pole(coarse, a0=1.0, fp=fp), _single_pole(fine, a0=1.0, fp=fp)
    # |H| falls with f, so a "≥ level in band" spec's worst is at the edge — read on the
    # coarse grid the naive `min(mag[f<=32G])` sits at 31.62 GHz, not 32.
    assert coarse[coarse <= 32e9][-1] == pytest.approx(31.62e9, rel=1e-3)
    exact = float(wf.magnitude_db(_single_pole(np.array([32e9]), a0=1.0, fp=fp))[0])
    assert wf.magnitude_at_db(coarse, h_c, 32e9) == pytest.approx(exact, abs=0.01)
    assert wf.band_worst_db(coarse, h_c, 32e9, worst="min") == pytest.approx(exact, abs=0.01)
    assert wf.band_worst_db(fine, h_f, 32e9, worst="min") == pytest.approx(exact, abs=1e-3)
    naive = float(wf.magnitude_db(h_c)[coarse <= 32e9].min())
    assert naive > exact + 0.03                          # the grid flatters the spec
    # max over a band on a rising curve (a reflection-like |1 - H|):
    r_c = 1.0 - h_c
    lo_edge = float(wf.magnitude_db(1.0 - _single_pole(np.array([1e9]), a0=1.0, fp=fp))[0])
    assert wf.band_worst_db(coarse, r_c, 32e9, f_start=1e9) == pytest.approx(
        float(wf.magnitude_db(1.0 - _single_pole(np.array([32e9]), a0=1.0, fp=fp))[0]), abs=0.01)
    assert wf.band_worst_db(coarse, r_c, 1.05e9, f_start=1e9) >= lo_edge - 1e-9
    # the exact half-power level (−3.0103 dB) crosses at the pole
    half = float(-20.0 * np.log10(np.sqrt(2.0)))
    assert wf.level_crossing_freq(fine, h_f, half) == pytest.approx(fp, rel=1e-3)
    # out-of-band / degenerate → NaN, never extrapolated
    assert np.isnan(wf.magnitude_at_db(coarse, h_c, 1e12))
    assert np.isnan(wf.band_worst_db(coarse, h_c, 1e12))
    assert np.isnan(wf.band_worst_db(coarse, h_c, 5e7))
    assert np.isnan(wf.level_crossing_freq(fine, h_f, +3.0))
    # registry recipes
    res = _FakeResult({"frequency": coarse, "vout": h_c}, {})
    assert registry.measure(res, {"meas": "mag_at_db", "out": "vout", "f": 32e9}, default_analysis="ac") == pytest.approx(exact, abs=0.01)
    assert registry.measure(res, {"meas": "band_min_db", "out": "vout", "f_edge": 32e9}, default_analysis="ac") == pytest.approx(exact, abs=0.01)
    assert registry.measure(res, {"meas": "band_max_db", "out": "vout", "f_edge": 32e9, "f_start": 1e9}, default_analysis="ac") == pytest.approx(
        float(wf.magnitude_db(_single_pole(np.array([1e9]), a0=1.0, fp=fp))[0]), abs=0.01)
    assert registry.measure(res, {"meas": "level_cross_hz", "out": "vout", "level": half}, default_analysis="ac") == pytest.approx(fp, rel=0.02)
    with pytest.raises(ValueError):
        registry.validate_recipe("s11", {"meas": "band_max_db", "out": "vout"})   # f_edge missing


def test_known_measurements_stable():
    names = registry.known_measurements()
    assert {"dcgain", "ugf", "pm", "f3db", "gbw", "t_settle", "slew",
            "thd", "thd_pct", "thd_db", "i_supply", "inoise_total"} <= set(names)


def test_rejection_db_from_residual_transfer():
    # a unity disturbance leaving a flat -46 dB residual → 46 dB rejection
    freq = np.logspace(3, 9, 61)
    resid = np.full_like(freq, 5e-3, dtype=complex)  # |vout| = 5 mV per 1 V AC
    expected = -20.0 * np.log10(5e-3)
    assert wf.rejection_db(freq, resid) == pytest.approx(expected, abs=1e-9)

    res = _FakeResult({"frequency": freq, "vout": resid})
    for meas in ("rejection_db", "cmrr_db", "psrr_vdd_db"):
        got = registry.measure(res, {"meas": meas, "out": "vout"}, default_analysis="ac")
        assert got == pytest.approx(expected, abs=1e-9)
    # the closed-loop gain is LINEAR (V/V — the buffer-spec convention), not dB
    assert registry.measure(res, {"meas": "gain_cl", "out": "vout"}, default_analysis="ac") == pytest.approx(5e-3, abs=1e-12)


def test_icmr_band_and_registry_recipes():
    # buffer sweep: tracks within 5 mV only on [0.3, 0.9]; a spurious glitch-track point
    # at 1.15 must NOT extend the band (widest contiguous run wins)
    vin = np.linspace(0.0, 1.2, 241)
    err = np.where((vin >= 0.3) & (vin <= 0.9), 0.002, 0.05)
    err[230] = 0.001  # the isolated glitch
    vout = vin + err
    lo, hi = wf.icmr_band(vin, vout, 0.005)
    assert lo == pytest.approx(0.3, abs=0.006)
    assert hi == pytest.approx(0.9, abs=0.006)

    res = _FakeResult({"vinp": vin, "vout": vout})
    recipe = {"meas": "icmr_range", "out": "vout", "vin": "vinp", "vtrack": 0.005}
    rng = registry.measure(res, recipe, default_analysis="dc")
    assert rng == pytest.approx(hi - lo, abs=1e-9)
    assert registry.measure(res, {**recipe, "meas": "icmr_min"}, default_analysis="dc") == pytest.approx(lo)
    assert registry.measure(res, {**recipe, "meas": "icmr_max"}, default_analysis="dc") == pytest.approx(hi)
    # nothing tracks → NaN degradation, not a raise
    dead = _FakeResult({"vinp": vin, "vout": vin + 0.1})
    assert np.isnan(registry.measure(dead, recipe, default_analysis="dc"))


def test_icmr_band_rejects_rail_coincidence():
    """An absolute-error test alone counts a railed output as "tracking" (2026-07-20 bug).

    Models the real amp_033_ti_ldo_ref_selfbias failure: below the input pair's turn-on the
    output is pinned at the bottom rail (vout ~ 0). Because vin is ALSO near 0 down there,
    |vout - vin| stays inside vtrack purely by coincidence, and those dead points are
    CONTIGUOUS with the genuine band — so neither a threshold test nor a run-length scan can
    reject them. Only the slope (activity) criterion can: a railed output has dvout/dvin ~ 0.
    """
    vin = np.linspace(0.0, 3.3, 331)
    vout = np.select(
        [vin < 0.05, vin < 0.15],
        [np.zeros_like(vin), (vin - 0.05) * 1.5],  # railed at 0, then catching up (slope 1.5)
        default=vin,                               # genuinely tracking (slope 1)
    )
    # Crucially |vout - vin| <= 50 mV EVERYWHERE, including the dead region — that is what makes
    # the artifact contiguous with the real band and invisible to a run-length scan.
    assert np.max(np.abs(vout - vin)) <= 0.05
    # threshold-only therefore reports a 3.3 V ICMR on a 3.3 V rail — physically impossible.
    lo_legacy, hi_legacy = wf.icmr_band(vin, vout, 0.05, slope_tol=None)
    assert hi_legacy - lo_legacy > 3.2
    assert lo_legacy == pytest.approx(0.0, abs=1e-9)
    # with the activity criterion both the railed region (slope 0) and the catch-up ramp
    # (slope 1.5) are rejected, leaving only the genuinely tracking band
    lo, hi = wf.icmr_band(vin, vout, 0.05)
    assert lo == pytest.approx(0.15, abs=0.02)
    assert hi == pytest.approx(3.3, abs=0.02)
    # the recipe honours an explicit slope_tol, including None for the legacy behaviour
    res = _FakeResult({"vinp": vin, "vout": vout})
    base = {"meas": "icmr_range", "out": "vout", "vin": "vinp", "vtrack": 0.05}
    assert registry.measure(res, base, default_analysis="dc") == pytest.approx(hi - lo, abs=1e-9)
    legacy = registry.measure(res, {**base, "slope_tol": None}, default_analysis="dc")
    assert legacy == pytest.approx(hi_legacy - lo_legacy, abs=1e-9)
    assert legacy > hi - lo  # the bug always OVER-reports


def test_new_measurements_registered_and_validated():
    known = registry.known_measurements()
    for name in ("rejection_db", "cmrr_db", "psrr_vdd_db", "gain_cl", "bw_cl",
                 "icmr_min", "icmr_max", "icmr_range"):
        assert name in known
    registry.validate_recipe("cmrr", {"meas": "cmrr_db", "out": "vout"})
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("icmr", {"meas": "icmr_range", "out": "vout"})  # missing vin/vtrack


def test_iip3_two_tone_and_pss_routes_agree():
    # -60 dBc IM3 on both sides of a 0.9/1.0 MHz pair -> IIP3 = A_in * 10^(60/40)
    f1, f2, a_in = 0.9e6, 1.0e6, 0.05
    f0, n1, n2 = wf.two_tone_indices(f1, f2)
    assert (f0, n1, n2) == (pytest.approx(1e5), 9, 10)
    im3 = a_in * 10 ** (-60 / 20)
    t = np.linspace(0, 5 / f0, 40000, endpoint=False)
    v = (a_in * np.sin(2 * np.pi * f1 * t) + a_in * np.sin(2 * np.pi * f2 * t)
         + im3 * np.sin(2 * np.pi * (2 * f1 - f2) * t) + im3 * np.sin(2 * np.pi * (2 * f2 - f1) * t))
    expect = a_in * np.sqrt(10 ** (60 / 20))
    assert wf.iip3_from_two_tone(t, v, f1, f2, ampl_in=a_in) == pytest.approx(expect, rel=1e-3)

    # the PSS-harmonic route: same signal as a phasor array (index k = k*f0)
    phasors = np.zeros(2 * n2, dtype=complex)
    phasors[n1] = phasors[n2] = a_in
    phasors[2 * n1 - n2] = phasors[2 * n2 - n1] = im3
    assert wf.iip3_from_harmonics(phasors, n1, n2, ampl_in=a_in) == pytest.approx(expect, rel=1e-9)

    # registry: tran recipe + pss recipe + the derived dBc spelling
    res_t = _FakeResult({"time": t, "vout": v})
    tran_recipe = {"meas": "iip3_dbv", "out": "vout", "f1": f1, "f2": f2, "ampl_in": a_in}
    assert registry.measure(res_t, tran_recipe, default_analysis="tran") == pytest.approx(20 * np.log10(expect), abs=0.05)
    assert registry.measure(res_t, {**tran_recipe, "meas": "im3_dbc"}, default_analysis="tran") == pytest.approx(-60.0, abs=0.05)
    res_p = _FakeResult({"vout": phasors})
    pss_recipe = {"meas": "iip3_pss_dbv", "out": "vout", "n1": n1, "n2": n2, "ampl_in": a_in}
    assert registry.measure(res_p, pss_recipe, default_analysis="pss") == pytest.approx(20 * np.log10(expect), abs=1e-6)
    # clean DUT: no measurable IM3 -> intercept +inf, dBc gap -inf
    clean = np.zeros(2 * n2, dtype=complex)
    clean[n1] = clean[n2] = a_in
    assert wf.iip3_from_harmonics(clean, n1, n2, ampl_in=a_in) == float("inf")
    res_c = _FakeResult({"vout": clean})
    assert registry.measure(res_c, {**pss_recipe, "meas": "im3_pss_dbc"}, default_analysis="pss") == float("-inf")
    registry.validate_recipe("iip3", tran_recipe)
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("iip3", {"meas": "iip3_pss", "out": "vout"})


def test_gain_margin_and_stb_loop_recipes():
    # a 3-identical-pole loop gain: phase hits -180 deg at f = fp*sqrt(3), where
    # |T| = T0/8 -> GM = -20*log10(T0/8); with T0 = 0.8 the margin is +20 dB
    fp, t0 = 1e4, 0.8
    freq = np.logspace(2, 7, 4001)
    h = t0 / (1 + 1j * freq / fp) ** 3
    assert wf.gain_margin_db(freq, h) == pytest.approx(20.0, abs=0.05)
    # a 2-pole loop never reaches -180 in-band -> unbounded margin (NaN, not a crash)
    h2 = 100.0 / (1 + 1j * freq / fp) ** 2
    assert np.isnan(wf.gain_margin_db(freq, h2))

    # registry: the stb kind reads the loopGain trace off the stb analysis by default
    t0_big = 100.0
    h_loop = t0_big / (1 + 1j * freq / fp) ** 1
    res = _FakeResult({"frequency": freq, "loopGain": h_loop})
    lg = registry.measure(res, {"meas": "loopgain_db", "out": "loopGain"}, default_analysis="stb")
    assert lg == pytest.approx(20 * np.log10(t0_big), abs=0.05)
    pm = registry.measure(res, {"meas": "pm_loop", "out": "loopGain"}, default_analysis="stb")
    # single pole: PM = 180 - atan(f_ugf/fp) ~ 90 deg for f_ugf >> fp (phase_margin's
    # phi0 convention adds the ~0.6 deg of lag already accrued at the first swept point)
    assert pm == pytest.approx(90.0, abs=2.0)
    registry.validate_recipe("stb", {"meas": "gain_margin_db", "out": "loopGain"})
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("stb", {"meas": "pm_loop"})


# ------------------------------------------------------------ periodic noise (pnoise)
def test_spot_noise_density_interpolates_log_f():
    # density ∝ 1/√f is a straight line neither in f nor log-f; use a log-log-exact
    # check at a swept point plus an interior interpolation sanity bound
    freq = np.logspace(0, 8, 81)
    dens = 1e-6 / np.sqrt(freq)
    at_point = wf.spot_noise_density(freq, dens, freq[40])
    assert at_point == pytest.approx(dens[40], rel=1e-12)
    mid = np.sqrt(freq[40] * freq[41])  # between two swept points (log midpoint)
    interp = wf.spot_noise_density(freq, dens, mid)
    assert dens[41] < interp < dens[40]
    # outside the swept band → NaN, never an extrapolation
    assert np.isnan(wf.spot_noise_density(freq, dens, 1e9))
    assert np.isnan(wf.spot_noise_density(freq, dens, 0.5))
    assert np.isnan(wf.spot_noise_density(freq[:1], dens[:1], 10.0))


def test_phase_noise_dbc_closed_form():
    # flat 10 nV/√Hz around a 1 V carrier: L(f) = (1e-8)^2 / (1/2) = 2e-16 -> -157.0 dBc/Hz
    freq = np.logspace(2, 7, 51)
    dens = np.full_like(freq, 10e-9)
    l_f = wf.phase_noise_dbc(freq, dens, 1e4, carrier_ampl=1.0)
    assert l_f == pytest.approx(10.0 * np.log10(2e-16), abs=1e-9)
    # halving the carrier costs 6 dB
    l_half = wf.phase_noise_dbc(freq, dens, 1e4, carrier_ampl=0.5)
    assert l_half - l_f == pytest.approx(20.0 * np.log10(2.0), abs=1e-9)
    # degenerate inputs -> NaN
    assert np.isnan(wf.phase_noise_dbc(freq, dens, 1e4, carrier_ampl=0.0))
    assert np.isnan(wf.phase_noise_dbc(freq, dens, 1e9, carrier_ampl=1.0))


def test_registry_pnoise_recipes():
    # white 100 nV/√Hz output / 25 nV/√Hz input-referred over 1 kHz..10 MHz
    freq = np.logspace(3, 7, 201)
    w_out, w_in = 100e-9, 25e-9
    res = _FakeResult({
        "frequency": freq,
        "out": np.full_like(freq, w_out),
        "in": np.full_like(freq, w_in),
    })
    onoise = registry.measure(res, {"meas": "onoise_pnoise_total", "out": "out"}, default_analysis="pnoise")
    inoise = registry.measure(res, {"meas": "inoise_pnoise_total", "out": "in"}, default_analysis="pnoise")
    band = np.sqrt(freq[-1] - freq[0])
    assert onoise == pytest.approx(w_out * band, rel=1e-6)
    assert inoise == pytest.approx(w_in * band, rel=1e-6)
    spot = registry.measure(res, {"meas": "pnoise_spot", "out": "out", "f": 1e5}, default_analysis="pnoise")
    assert spot == pytest.approx(w_out, rel=1e-9)
    l_f = registry.measure(
        res,
        {"meas": "phase_noise_dbc", "out": "out", "f": 1e5, "carrier_ampl": 0.1},
        default_analysis="pnoise",
    )
    assert l_f == pytest.approx(10.0 * np.log10(w_out**2 / (0.1**2 / 2.0)), abs=1e-9)


def test_registry_pnoise_names_registered_and_validated():
    known = registry.known_measurements()
    for name in ("onoise_pnoise_total", "inoise_pnoise_total", "pnoise_spot", "phase_noise_dbc"):
        assert name in known
    registry.validate_recipe("pn", {"meas": "onoise_pnoise_total", "out": "out"})
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("pn", {"meas": "pnoise_spot", "out": "out"})  # missing `f`
    with pytest.raises(ValueError, match="needs"):
        registry.validate_recipe("pn", {"meas": "phase_noise_dbc", "out": "out", "f": 1e5})  # missing carrier_ampl
