"""Metric registry: canonical measurement name → value from a ``SimResult``.

This is the engine-neutral Tier-1 measurement path. A ``TargetSpec.measurement`` recipe of
the form ``{meas: <name>, ...args}`` names a canonical figure of merit — the AC family
(``dcgain``/``ugf``/``pm``/``f3db``/``gbw``, closed-loop ``gain_cl``/``bw_cl``, rejection
``cmrr_db``/``psrr_vdd_db``/``rejection_db``), the DC-sweep ICMR family (``icmr_min/max/
range``), transient (``t_settle``/``slew``, FFT ``thd*`` and two-tone ``iip3*``/``im3_dbc``),
their native-PSS twins (``thd_pss*``/``hd*``/``sfdr*``/``iip3_pss*``), op-point ``i_supply``,
noise ``inoise_total``/``onoise_total``, and periodic noise (``onoise_pnoise_total``/
``inoise_pnoise_total``/``pnoise_spot``/``phase_noise_dbc``, the Spectre ``pnoise``-riding-PSS
family) — plus the signal(s) it reads. :func:`measure` pulls those waves/scalars
off any :class:`~spicexplorer_core.spice_engine.protocol.SimResult` (ngspice **or**
Spectre) and evaluates the pure math in :mod:`~spicexplorer_core.measurements.waveforms`.

The recipe is the same declarative object the OCEAN (Tier-2) path uses, so a project can
mix Tier-1 Python metrics and Tier-2 OCEAN metrics per target spec. The math is defined
once here and validated on ngspice first (the datasheet ``extract: {meas: …}`` vocabulary
is a direct match), which is what makes the definitions engine-neutral.

Layering: lives in ``spicexplorer-core`` beside the ``SimResult`` protocol — pure numpy,
no simulator, no bridge, no upward dependency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple

import numpy as np

from spicexplorer_core.measurements import waveforms as _wf

if TYPE_CHECKING:
    from spicexplorer_core.spice_engine.protocol import SimResult

__all__ = ["measure", "validate_recipe", "known_measurements", "measurement_table", "kind_default_analysis"]


# Each canonical name → (kind, required-arg keys). `kind` picks the analysis default and
# the extractor; `required` are the recipe keys that must be present (checked at load, so
# a typo'd recipe fails before any simulation runs — symmetric with the OCEAN builders).
_MEAS_TABLE: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    # AC (frequency-domain transfer, unit-stimulus response)
    "dcgain": ("ac", ("out",)),
    "dc_gain_db": ("ac", ("out",)),
    "ugf": ("ac", ("out",)),
    "ugf_hz": ("ac", ("out",)),
    "pm": ("ac", ("out",)),
    "pm_deg": ("ac", ("out",)),
    "phase_margin": ("ac", ("out",)),
    "f3db": ("ac", ("out",)),
    "bandwidth": ("ac", ("out",)),
    "bw_3db": ("ac", ("out",)),
    "gbw": ("ac", ("out",)),
    "gain_bw_product": ("ac", ("out",)),
    # closed-loop AC — the analog-db `ac_closed_loop` datasheet vocabulary. NOTE
    # `gain_cl` is LINEAR (V/V): the buffer-gain spec convention (CACE ac_params.gain,
    # e.g. 0.97..1.03), not dB. `bw_cl` is the same −3 dB math as `bw_3db`.
    "gain_cl": ("ac", ("out",)),
    "bw_cl": ("ac", ("out",)),
    # rejection ratios — the unity-buffer disturbance templates (`cmrr_vcm`/`psrr_vdd`):
    # a unit AC rides the common mode / the supply, and the output residual IS the
    # reciprocal rejection, so the figure is -dcgain of the residual transfer.
    "rejection_db": ("ac", ("out",)),
    "cmrr_db": ("ac", ("out",)),
    "psrr_vdd_db": ("ac", ("out",)),
    # input impedance — two forms. Direct: |V(out)| under a UNIT current drive
    # (`ac mag=1` / `pac pacmag=1` on a *current* source): the node voltage IS the
    # impedance. Series-sense (high-impedance ports whose large-signal bias must stay
    # stiff — the chopper Zin bench): drive through a known series R and read the
    # RATIO `out`/`ref` (port voltage over series drop), scaled by `scale` (= 2·Rs for
    # a differential pair). Optional spot `f` (nearest bin); the band's low edge by
    # default. With `{analysis: pac}` this is the chopper/SC Z_in — the periodic-OP
    # input impedance a static ac cannot see.
    "zin_mag": ("ac", ("out",)),
    # DC sweep — the buffer-connected linearity template (input common-mode range)
    "icmr_min": ("dc", ("out", "vin", "vtrack")),
    "icmr_max": ("dc", ("out", "vin", "vtrack")),
    "icmr_range": ("dc", ("out", "vin", "vtrack")),
    # transient
    "t_settle": ("tran", ("out",)),
    "slew": ("tran", ("out",)),
    # distortion — transient + coherent FFT (engine-neutral, the SPICE `.four` analogue)
    "thd": ("tran", ("out", "f0")),
    "thd_pct": ("tran", ("out", "f0")),
    "thd_db": ("tran", ("out", "f0")),
    # two-tone intermodulation — transient route (coherent FFT at the common fundamental)
    "iip3": ("tran", ("out", "f1", "f2", "ampl_in")),
    "iip3_dbv": ("tran", ("out", "f1", "f2", "ampl_in")),
    "im3_dbc": ("tran", ("out", "f1", "f2", "ampl_in")),
    # distortion — native PSS harmonics (Spectre `pss` fd-PSF; higher fidelity, no window/resample)
    "thd_pss": ("pss", ("out",)),
    "thd_pss_pct": ("pss", ("out",)),
    "thd_pss_db": ("pss", ("out",)),
    "hd2": ("pss", ("out",)),
    "hd3": ("pss", ("out",)),
    "hd2_db": ("pss", ("out",)),
    "hd3_db": ("pss", ("out",)),
    "hd": ("pss", ("out", "n")),
    "hd_db": ("pss", ("out", "n")),
    "sfdr": ("pss", ("out",)),
    "sfdr_db": ("pss", ("out",)),
    # two-tone intermodulation — native PSS route: both tones share the fundamental
    # (f1=n1·f0, f2=n2·f0), so the IM3 products are plain harmonics of the fd-PSF
    "iip3_pss": ("pss", ("out", "n1", "n2", "ampl_in")),
    "iip3_pss_dbv": ("pss", ("out", "n1", "n2", "ampl_in")),
    "im3_pss_dbc": ("pss", ("out", "n1", "n2", "ampl_in")),
    # loop gain — the Spectre `stb` analysis' loopGain wave (the stb bench); same AC math
    # as pm/dcgain but read from the stb.stb PSF, and the only wave a LOOP phase/gain
    # margin is honestly defined on (a closed-loop AC transfer never crosses unity)
    "pm_loop": ("stb", ("out",)),
    "gain_margin_db": ("stb", ("out",)),
    "loopgain_db": ("stb", ("out",)),
    # operating point (scalar reads)
    "i_supply": ("op", ("probe",)),
    # DC offset — the difference of two op-point NODE voltages, `out` - `ref`. The analog-db
    # `dc_op` templates all define `vos` this way inside an ngspice `.control` block
    # (`let vos = v(voutp)-v(voutn)` differential, `let vos = v(vout)-v(vinp)` for the
    # unity-follower biaswrap variant). Spectre never executes `.control`, so the closed lane
    # had no `vos` at all: `_MEAS_TABLE['vos']` raised `KeyError` and `evaluate()` degraded it
    # to NaN on every FOUNDRY-n65 amplifier that declares it. Reading the two op-point node
    # scalars reproduces the deck's own definition engine-neutrally (both nodes are in the
    # ngspice op plot AND the Spectre op PSF); the caller names the pair.
    "vos": ("op", ("out", "ref")),
    # output COMMON mode (voutp+voutn)/2 — the same two op-point node scalars as `vos`,
    # averaged instead of differenced. The headline of any CMFB'd fully-differential cell
    # (where the commanded CM landed, and the static CM error against it); the ngspice
    # dc_op_diff deck computes it in-deck, but in-deck measures do not exist on the
    # Spectre lane, so a CMFB'd cell was unreadable there without this.
    "vocm": ("op", ("out", "ref")),
    # static supply power P = |I_supply|·VDD, read off the same op-point supply-current
    # probe as `i_supply` plus the rail `vdd` (V). Three spellings share one extractor —
    # watts / mW / µW — so an amplifier's ~sub-mW power lands on a human-readable scale
    # without the spec having to pre-scale the target. Engine-neutral (ngspice op scalar
    # or a Spectre operating-point probe).
    "power": ("op", ("probe", "vdd")),
    "power_mw": ("op", ("probe", "vdd")),
    "power_uw": ("op", ("probe", "vdd")),
    # noise
    "inoise_total": ("noise", ("out",)),
    "onoise_total": ("noise", ("out",)),
    # periodic noise — Spectre `pnoise` riding a PSS solution (the `pnoise.pnoise` swept
    # PSF: `out`/`in` V/√Hz densities under periodic large-signal drive). The totals are
    # the same trapezoid RMS integral as onoise/inoise; `pnoise_spot` is the density at
    # one offset; `phase_noise_dbc` the SSB noise-to-carrier ratio at an offset for an
    # explicit carrier amplitude (V peak).
    "onoise_pnoise_total": ("pnoise", ("out",)),
    "inoise_pnoise_total": ("pnoise", ("out",)),
    "pnoise_spot": ("pnoise", ("out", "f")),
    "phase_noise_dbc": ("pnoise", ("out", "f", "carrier_ampl")),
}

_KIND_DEFAULT_ANALYSIS: Dict[str, str] = {
    "ac": "ac",
    "dc": "dc",
    "tran": "tran",
    "op": "op",
    "noise": "noise",
    "pnoise": "pnoise",
    "pss": "pss",
    "stb": "stb",
}

# stb figures of merit — ``fn(freq, loopGain)`` (the same shape as the AC table).
_STB_FN: Dict[str, Callable[[Any, Any], float]] = {
    "pm_loop": _wf.phase_margin,
    "gain_margin_db": _wf.gain_margin_db,
    "loopgain_db": _wf.dc_gain_db,
}

# AC figures of merit that are computed as ``fn(freq, h)``.
_AC_FN: Dict[str, Callable[[Any, Any], float]] = {
    "dcgain": _wf.dc_gain_db,
    "dc_gain_db": _wf.dc_gain_db,
    "ugf": _wf.unity_gain_freq,
    "ugf_hz": _wf.unity_gain_freq,
    "pm": _wf.phase_margin,
    "pm_deg": _wf.phase_margin,
    "phase_margin": _wf.phase_margin,
    "f3db": _wf.bandwidth_3db,
    "bandwidth": _wf.bandwidth_3db,
    "bw_3db": _wf.bandwidth_3db,
    "gbw": _wf.gain_bandwidth_product,
    "gain_bw_product": _wf.gain_bandwidth_product,
    "gain_cl": _wf.dc_gain_linear,
    "bw_cl": _wf.bandwidth_3db,
    "rejection_db": _wf.rejection_db,
    "cmrr_db": _wf.rejection_db,
    "psrr_vdd_db": _wf.rejection_db,
}


def known_measurements() -> Tuple[str, ...]:
    """The canonical measurement names accepted in a ``{meas: …}`` recipe."""
    return tuple(sorted(_MEAS_TABLE))


def measurement_table() -> Dict[str, Tuple[str, Tuple[str, ...]]]:
    """A copy of the canonical measurement table: name → ``(kind, required-arg keys)``.

    The public read surface for tools that enumerate the recipe vocabulary (e.g. the
    waveview result viewer's measurement catalog) — never mutate the returned dict."""
    return dict(_MEAS_TABLE)


def kind_default_analysis() -> Dict[str, str]:
    """A copy of the kind → default engine-neutral analysis-string map."""
    return dict(_KIND_DEFAULT_ANALYSIS)


def validate_recipe(spec_name: str, recipe: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if ``recipe`` names an unknown measurement or omits a required
    argument. Called at project load (before any sim) so typos fail loudly and early."""
    meas = str(recipe.get("meas", "")).strip()
    entry = _MEAS_TABLE.get(meas)
    if entry is None:
        raise ValueError(
            f"target '{spec_name}': unknown measurement meas={meas!r}; "
            f"valid: {list(known_measurements())}."
        )
    _kind, required = entry
    missing = [k for k in required if k not in recipe]
    if missing:
        raise ValueError(
            f"target '{spec_name}': measurement {meas!r} needs {list(required)}; missing {missing}."
        )
    if meas == "t_settle" and "tol" not in recipe and "tol_frac" not in recipe:
        raise ValueError(
            f"target '{spec_name}': measurement 't_settle' needs `tol` or `tol_frac`."
        )


def _real_wave(result: "SimResult", name: str, analysis: str) -> np.ndarray:
    return np.real(np.asarray(result.wave(name, analysis)))


def _iip3_variant(meas: str, iip3_v: float, ampl_in: float) -> float:
    """One IIP3 figure, three spellings: amplitude (V), dBV, or the IM3 dBc gap.

    ``A_IIP3 = A_in·√(tone/IM3)`` ⇒ ``im3_dbc = −40·log10(A_IIP3/A_in)`` — derived rather
    than re-measured so the three recipes can never disagree.
    """
    if meas.endswith("_dbv"):
        if not np.isfinite(iip3_v):
            return float(iip3_v)
        return float(20.0 * np.log10(iip3_v)) if iip3_v > 0.0 else float("nan")
    if meas.endswith("_dbc"):  # im3_dbc / im3_pss_dbc (negative for any real amplifier)
        if not np.isfinite(iip3_v):
            return float(-iip3_v) if iip3_v == float("inf") else float("nan")
        return float(-40.0 * np.log10(iip3_v / ampl_in)) if iip3_v > 0.0 and ampl_in > 0.0 else float("nan")
    return float(iip3_v)


def _ac_transfer(
    result: "SimResult", analysis: str, recipe: Dict[str, Any]
) -> tuple[np.ndarray, np.ndarray]:
    freq = _real_wave(result, str(recipe.get("freq", "frequency")), analysis)
    h = np.asarray(result.wave(str(recipe["out"]), analysis))
    ref = recipe.get("ref")
    if ref is not None:  # normalize by an explicit input signal when it isn't unit
        h = h / np.asarray(result.wave(str(ref), analysis))
    return freq, h


def measure(
    result: "SimResult", recipe: Dict[str, Any], *, default_analysis: str
) -> float:
    """Evaluate one ``{meas: …}`` recipe against ``result`` → a scalar.

    ``default_analysis`` is the target's engine-neutral analysis string (from
    ``TargetSpec.get_analysis()``); a recipe may override it with an ``analysis`` key.
    Missing signals propagate as the ``SimResult``'s own behavior (NaN scalar / raising
    wave); the caller (``MeasureMergeContext``) turns a raised extraction into NaN so one
    bad metric degrades to a scorer penalty.
    """
    meas = str(recipe["meas"]).strip()
    kind, _required = _MEAS_TABLE[meas]
    analysis = str(recipe.get("analysis") or _KIND_DEFAULT_ANALYSIS.get(kind, default_analysis))

    if kind == "ac":
        freq, h = _ac_transfer(result, analysis, recipe)
        if meas == "zin_mag":  # |V| under unit-current drive (or scale·|out/ref|); spot f or low edge
            mag = np.abs(h) * float(recipe.get("scale", 1.0))
            at = float(recipe["f"]) if "f" in recipe else float(np.min(freq))
            return float(mag[int(np.argmin(np.abs(freq - at)))])
        return float(_AC_FN[meas](freq, h))

    if kind == "stb":  # loop-gain wave (Spectre stb) — AC math on the loopGain trace
        freq, h = _ac_transfer(result, analysis, recipe)
        return float(_STB_FN[meas](freq, h))

    if kind == "dc":  # buffer-connected DC sweep: ICMR from the (vin, vout) transfer
        vin = _real_wave(result, str(recipe["vin"]), analysis)
        vout = _real_wave(result, str(recipe["out"]), analysis)
        # `slope_tol` is the activity criterion that rejects rail-coincidence "tracking"
        # (see waveforms.icmr_band); omit it to take the 0.1 default, or set it to null in
        # the datasheet extract to recover the legacy threshold-only behaviour.
        _stol = recipe.get("slope_tol", 0.1)
        lo, hi = _wf.icmr_band(
            vin,
            vout,
            float(recipe["vtrack"]),
            slope_tol=None if _stol is None else float(_stol),
        )
        if meas == "icmr_min":
            return lo
        if meas == "icmr_max":
            return hi
        return hi - lo  # icmr_range

    if kind == "tran":
        t = _real_wave(result, str(recipe.get("time", "time")), analysis)
        v = _real_wave(result, str(recipe["out"]), analysis)
        if recipe.get("ref") is not None:
            # differential read: v = out - ref (fully-diff benches, e.g. voutp/voutn)
            v = v - _real_wave(result, str(recipe["ref"]), analysis)
        if meas in ("iip3", "iip3_dbv", "im3_dbc"):
            a = _wf.iip3_from_two_tone(
                t,
                v,
                float(recipe["f1"]),
                float(recipe["f2"]),
                ampl_in=float(recipe["ampl_in"]),
                n_periods=recipe.get("n_periods"),
                samples_per_period=int(recipe.get("samples_per_period", 64)),
                t_start=recipe.get("t_start"),
            )
            return _iip3_variant(meas, a, float(recipe["ampl_in"]))
        if meas in ("thd", "thd_pct", "thd_db"):
            ratio = _wf.thd_from_waveform(
                t,
                v,
                float(recipe["f0"]),
                n_harmonics=int(recipe.get("n_harmonics", 5)),
                n_periods=recipe.get("n_periods"),
                samples_per_period=int(recipe.get("samples_per_period", 64)),
                t_start=recipe.get("t_start"),
            )
            if meas == "thd_pct":
                return ratio * 100.0
            if meas == "thd_db":
                return float(20.0 * np.log10(ratio)) if ratio > 0.0 else float("nan")
            return ratio
        if meas == "slew":
            return _wf.slew_rate(t, v)
        # t_settle
        return _wf.settling_time(
            t,
            v,
            final=recipe.get("final"),
            tol=recipe.get("tol"),
            tol_frac=recipe.get("tol_frac"),
            t_start=float(recipe.get("t_start", 0.0)),
        )

    if kind == "pss":  # native distortion off the pss fd-PSF complex harmonic phasors
        harmonics = np.asarray(result.wave(str(recipe["out"]), analysis))
        if meas in ("iip3_pss", "iip3_pss_dbv", "im3_pss_dbc"):
            a = _wf.iip3_from_harmonics(
                harmonics,
                int(recipe["n1"]),
                int(recipe["n2"]),
                ampl_in=float(recipe["ampl_in"]),
            )
            return _iip3_variant(meas, a, float(recipe["ampl_in"]))
        if meas in ("thd_pss", "thd_pss_pct", "thd_pss_db"):
            ratio = _wf.thd_from_harmonics(harmonics, n_harmonics=recipe.get("n_harmonics"))
        elif meas in ("hd2", "hd2_db"):
            ratio = _wf.hd_ratio(harmonics, 2)
        elif meas in ("hd3", "hd3_db"):
            ratio = _wf.hd_ratio(harmonics, 3)
        elif meas in ("hd", "hd_db"):
            ratio = _wf.hd_ratio(harmonics, int(recipe["n"]))
        else:  # sfdr / sfdr_db
            ratio = _wf.sfdr_from_harmonics(harmonics)
        if meas.endswith("_pct"):
            return ratio * 100.0
        if meas.endswith("_db"):
            if not np.isfinite(ratio):  # e.g. sfdr of a perfectly clean signal → +inf
                return float(ratio)
            return float(20.0 * np.log10(ratio)) if ratio > 0.0 else float("nan")
        return float(ratio)

    if kind == "op":  # supply-current scalar (i_supply) or the power derived from it
        if meas in ("vos", "vocm"):  # difference / mean of two op-point node voltages
            out = float(result.scalar(str(recipe["out"]), analysis))
            ref = float(result.scalar(str(recipe["ref"]), analysis))
            return out - ref if meas == "vos" else (out + ref) / 2.0
        val = float(result.scalar(str(recipe["probe"]), analysis))
        if meas == "i_supply":  # signed current scalar, magnitude by default
            return val if bool(recipe.get("signed", False)) else abs(val)
        # power = |I_supply|·VDD (always positive); watts, or mW / µW spellings
        power_w = abs(val) * float(recipe["vdd"])
        if meas == "power_mw":
            return power_w * 1e3
        if meas == "power_uw":
            return power_w * 1e6
        return power_w

    if kind == "pnoise":  # periodic noise density (Spectre pnoise riding a PSS solution)
        freq = _real_wave(result, str(recipe.get("freq", "frequency")), analysis)
        density = np.asarray(result.wave(str(recipe["out"]), analysis))
        if meas == "pnoise_spot":
            return _wf.spot_noise_density(freq, density, float(recipe["f"]))
        if meas == "phase_noise_dbc":
            return _wf.phase_noise_dbc(
                freq, density, float(recipe["f"]), carrier_ampl=float(recipe["carrier_ampl"])
            )
        return _wf.integrated_noise(freq, density)  # onoise_pnoise_total / inoise_pnoise_total

    # noise — integrate the input/output-referred spectral density over the band
    freq = _real_wave(result, str(recipe.get("freq", "frequency")), analysis)
    density = np.asarray(result.wave(str(recipe["out"]), analysis))
    return _wf.integrated_noise(freq, density)
