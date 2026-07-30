"""Interactive Plotly figure builders over a :class:`WaveDataset`.

Notebook-first (requirement #2): every builder returns a ``plotly.graph_objects.Figure``
with zoom/pan/hover for free, and the analysis-specific builders overlay Tier-1
measurement values (UGF/PM markers on a Bode plot, settling band on a step response,
harmonic distortion labels on a PSS spectrum, …) computed by the SAME core registry the
optimizer scores with — the plots and the numbers can never disagree.

The generic entry is :func:`waveform_figure`; the rest are typed conveniences.
``log_view_html`` renders a parsed simulator log as a colourised, scrollable HTML block
for notebook display (pair with ``IPython.display.HTML``).
"""

from __future__ import annotations

import html as _html
from typing import Any, Sequence

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .dataset import WaveDataset
from .downsample import downsample_indices
from .logs import LogSummary
from .measure import measure_dataset

__all__ = [
    "waveform_figure",
    "bode_figure",
    "tran_figure",
    "dc_figure",
    "noise_figure",
    "pss_spectrum_figure",
    "fft_spectrum_figure",
    "log_view_html",
]

_Y_FORMATS = ("auto", "mag_db", "mag", "phase_deg", "re", "im")


def figure_title(fig: go.Figure) -> str:
    """The figure's current title text (``""`` when unset).

    Typed accessor: plotly's stubs don't model ``fig.layout.<attr>``, so every read
    goes through here (and tests use it too) instead of scattering ignores."""
    title = getattr(fig.layout, "title", None)
    return str(getattr(title, "text", "") or "")


def format_y(data: np.ndarray, fmt: str) -> tuple[np.ndarray, str]:
    """Transform a (possibly complex) trace for display → ``(real_array, axis_label)``."""
    arr = np.asarray(data)
    if fmt == "auto":
        fmt = "mag_db" if np.iscomplexobj(arr) else "re"
    if fmt == "mag_db":
        mag = np.abs(arr).astype(float)
        with np.errstate(divide="ignore"):
            return 20.0 * np.log10(mag), "magnitude (dB)"
    if fmt == "mag":
        return np.abs(arr).astype(float), "magnitude"
    if fmt == "phase_deg":
        return np.degrees(np.unwrap(np.angle(arr))), "phase (°)"
    if fmt == "im":
        return np.imag(arr).astype(float), "imag"
    if fmt == "re":
        return np.real(arr).astype(float), "value"
    raise ValueError(f"unknown y format {fmt!r} (one of {_Y_FORMATS})")


def _xy(
    ds: WaveDataset, analysis: str, signal: str, x: str | None, fmt: str,
    max_points: int | None, method: str,
) -> tuple[np.ndarray, np.ndarray, str]:
    an = ds.resolve_analysis(analysis)
    if an is None:
        raise KeyError(f"dataset has no analysis {analysis!r} (have {sorted(ds.analyses)})")
    sig = ds.find_signal(analysis, signal)
    if sig is None:
        raise KeyError(f"analysis {analysis!r} has no signal {signal!r} (have {sorted(an.signals)})")
    y, label = format_y(sig.data, fmt)
    x_name = x or an.sweep
    if x_name is None:
        xa = np.arange(y.size, dtype=float)
    else:
        x_sig = ds.find_signal(analysis, x_name)
        if x_sig is None:
            raise KeyError(f"analysis {analysis!r} has no x signal {x_name!r}")
        xa = np.real(np.asarray(x_sig.data)).astype(float)
    n = min(xa.size, y.size)
    xa, y = xa[:n], y[:n]
    if max_points is not None and y.size > max_points:
        idx = downsample_indices(xa, y, max_points, method=method)
        xa, y = xa[idx], y[idx]
    return xa, y, label


def waveform_figure(
    ds: WaveDataset,
    analysis: str,
    signals: Sequence[str] | None = None,
    *,
    x: str | None = None,
    fmt: str = "auto",
    logx: bool | None = None,
    logy: bool = False,
    max_points: int | None = 20_000,
    method: str = "minmax",
    title: str | None = None,
) -> go.Figure:
    """One interactive figure of any analysis' signals (the generic viewer plot).

    ``signals=None`` plots every non-abscissa trace. ``logx=None`` auto-enables a log
    frequency axis for the AC-family analyses (``ac``/``noise``/``stb``/``pnoise``).
    Large traces are downsampled for display (envelope-preserving by default).
    """
    an = ds.resolve_analysis(analysis)
    if an is None:
        raise KeyError(f"dataset has no analysis {analysis!r} (have {sorted(ds.analyses)})")
    canonical = an.analysis.split(":", 1)[0]
    if logx is None:
        logx = canonical in ("ac", "noise", "noise_spectrum", "stb", "pnoise")
    sweep_names = {an.sweep} if an.sweep else set()
    if canonical in ("ac", "noise", "noise_spectrum", "stb", "pnoise", "pss"):
        sweep_names |= {"frequency", "freq"}
    elif canonical in ("tran", "pss_td"):
        sweep_names |= {"time"}
    names = list(signals) if signals is not None else [
        n for n in an.signals if n not in sweep_names
    ]

    fig = go.Figure()
    y_label = "value"
    for name in names:
        xa, y, y_label = _xy(ds, analysis, name, x, fmt, max_points, method)
        fig.add_trace(go.Scatter(x=xa, y=y, mode="lines", name=name))
    fig.update_layout(
        title=title or f"{ds.engine}: {an.native_name}",
        xaxis_title=x or an.sweep or "index",
        yaxis_title=y_label,
        hovermode="x unified",
        template="plotly_white",
    )
    if logx:
        fig.update_xaxes(type="log")
    if logy:
        fig.update_yaxes(type="log")
    return fig


def _try_measure(ds: WaveDataset, recipe: dict[str, Any]) -> float | None:
    try:
        value = measure_dataset(ds, recipe)
    except (ValueError, KeyError, TypeError):  # TypeError: malformed recipe arg values
        return None
    return value if np.isfinite(value) else None


def bode_figure(
    ds: WaveDataset,
    out: str,
    *,
    analysis: str = "ac",
    ref: str | None = None,
    annotate: bool = True,
    title: str | None = None,
) -> go.Figure:
    """Magnitude + phase Bode plot of an AC(-like) transfer, with registry overlays.

    Works on ``analysis="ac"`` (a closed/open-loop transfer) and ``analysis="stb"``
    (a Spectre loopGain wave — pass ``out="loopGain"``). When ``annotate``, the core
    registry's ``dcgain``/``ugf``/``pm``/``f3db`` (or ``loopgain_db``/``pm_loop``/
    ``gain_margin_db`` for stb) are computed on the same data and drawn on the figure.
    """
    stb = str(analysis).strip().lower() == "stb"
    recipe_extra: dict[str, Any] = {"out": out, "analysis": analysis}
    if ref is not None:
        recipe_extra["ref"] = ref

    x_mag, mag_db, _ = _xy(ds, analysis, out, None, "mag_db", None, "none")
    x_ph, phase, _ = _xy(ds, analysis, out, None, "phase_deg", None, "none")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=("magnitude", "phase"))
    fig.add_trace(go.Scatter(x=x_mag, y=mag_db, mode="lines", name=f"|{out}| (dB)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x_ph, y=phase, mode="lines", name=f"∠{out} (°)"), row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_xaxes(type="log", title_text="frequency (Hz)", row=2, col=1)
    fig.update_yaxes(title_text="dB", row=1, col=1)
    fig.update_yaxes(title_text="°", row=2, col=1)

    labels: list[str] = []
    if annotate:
        gain_meas = "loopgain_db" if stb else "dcgain"
        pm_meas = "pm_loop" if stb else "pm"
        dcgain = _try_measure(ds, {"meas": gain_meas, **recipe_extra})
        ugf = _try_measure(ds, {"meas": "ugf", **recipe_extra} if not stb else {"meas": "ugf", "out": out, "analysis": analysis})
        pm = _try_measure(ds, {"meas": pm_meas, **recipe_extra})
        f3db = None if stb else _try_measure(ds, {"meas": "f3db", **recipe_extra})
        gm = _try_measure(ds, {"meas": "gain_margin_db", **recipe_extra}) if stb else None

        if dcgain is not None:
            labels.append(f"{'loop gain' if stb else 'DC gain'} = {dcgain:.2f} dB")
        if ugf is not None:
            fig.add_vline(x=ugf, line_dash="dot", line_color="gray")
            labels.append(f"UGF = {ugf:.4g} Hz")
        # plotly's stubs type row/col as str-only; ints are the documented subplot form
        fig.add_hline(y=0.0, line_dash="dash", line_color="lightgray", row=1, col=1)  # pyright: ignore[reportArgumentType]
        if pm is not None:
            labels.append(f"PM = {pm:.1f}°")
            if ugf is not None:
                # place the marker ON the plotted curve: the registry's pm is
                # 180 − φ₀ + φ_ugf (sign-convention agnostic), so the unwrapped phase
                # at UGF is pm − 180 + φ₀ — assuming φ₀ = 0 floats the marker 180° off
                # the trace for any inverting transfer.
                phi0 = float(phase[0]) if phase.size else 0.0
                fig.add_trace(
                    go.Scatter(x=[ugf], y=[pm - 180.0 + phi0], mode="markers+text",
                               text=[f"PM {pm:.1f}°"], textposition="top right",
                               marker=dict(size=9, color="crimson"), showlegend=False),
                    row=2, col=1,
                )
        if f3db is not None:
            fig.add_vline(x=f3db, line_dash="dot", line_color="steelblue")
            labels.append(f"f₋₃dB = {f3db:.4g} Hz")
        if gm is not None:
            labels.append(f"GM = {gm:.2f} dB")

    subtitle = " · ".join(labels)
    fig.update_layout(
        title=(title or f"{'Loop-gain' if stb else 'Bode'}: {out}")
        + (f"<br><sup>{subtitle}</sup>" if subtitle else ""),
        hovermode="x unified",
        template="plotly_white",
        height=560,
    )
    return fig


def tran_figure(
    ds: WaveDataset,
    signals: Sequence[str] | None = None,
    *,
    analysis: str = "tran",
    settle: dict[str, Any] | None = None,
    title: str | None = None,
    max_points: int | None = 20_000,
) -> go.Figure:
    """Transient traces vs time; optional settling-time overlay.

    ``settle`` is a partial ``t_settle`` recipe (``{"out": "v(out)", "tol_frac": 0.01}``
    or ``{"out": …, "tol": 1e-3}``): the registry's settling time is computed and drawn
    as a vertical marker, plus the tolerance band around the final value.
    """
    fig = waveform_figure(ds, analysis, signals, max_points=max_points, title=title, method="minmax")
    if settle:
        recipe = {"meas": "t_settle", "analysis": analysis, **settle}
        ts = _try_measure(ds, recipe)
        slew = _try_measure(ds, {"meas": "slew", "analysis": analysis, "out": settle["out"]})
        labels = []
        if ts is not None:
            fig.add_vline(x=ts, line_dash="dot", line_color="crimson")
            labels.append(f"t_settle = {ts:.4g} s")
            sig = ds.find_signal(analysis, str(settle["out"]))
            if sig is not None:
                v = np.real(np.asarray(sig.data)).astype(float)
                t_sig = ds.find_signal(analysis, str(settle.get("time", "time")))
                final = float(settle.get("final", v[-1]))
                tol = settle.get("tol")
                if tol is not None:
                    band = abs(float(tol))
                elif "tol_frac" in settle:
                    # mirror waveforms.settling_time EXACTLY: the tol_frac band is a
                    # fraction of the STEP (final − v(t_start)), not of the final value —
                    # a mid-rail step would otherwise shade a band ~|final/step|× too wide
                    # and contradict the annotated t_settle.
                    t = (
                        np.real(np.asarray(t_sig.data)).astype(float)
                        if t_sig is not None
                        else np.arange(v.size, dtype=float)
                    )
                    v0 = float(np.interp(float(settle.get("t_start", 0.0)), t, v))
                    band = abs(float(settle["tol_frac"]) * (final - v0))
                else:  # no tolerance given → t_settle was NaN/None upstream anyway
                    band = None
                if band is not None:
                    fig.add_hrect(y0=final - band, y1=final + band, fillcolor="crimson",
                                  opacity=0.08, line_width=0)
        if slew is not None:
            labels.append(f"slew = {slew:.4g} V/s")
        if labels:
            fig.update_layout(title=figure_title(fig) + f"<br><sup>{' · '.join(labels)}</sup>")
    fig.update_xaxes(title_text="time (s)")
    return fig


def dc_figure(
    ds: WaveDataset,
    out: str,
    *,
    vin: str | None = None,
    analysis: str = "dc",
    icmr: dict[str, Any] | None = None,
    title: str | None = None,
) -> go.Figure:
    """DC transfer (``out`` vs the swept input); optional ICMR band shading.

    ``icmr`` is a partial ICMR recipe (``{"vin": "v(vin)", "vtrack": 0.05}``) — the
    registry's ``icmr_min``/``icmr_max`` are computed and the tracking band shaded.
    """
    fig = waveform_figure(ds, analysis, [out], x=vin, logx=False, title=title)
    if icmr:
        base = {"analysis": analysis, "out": out, **icmr}
        lo = _try_measure(ds, {"meas": "icmr_min", **base})
        hi = _try_measure(ds, {"meas": "icmr_max", **base})
        if lo is not None and hi is not None:
            fig.add_vrect(x0=lo, x1=hi, fillcolor="seagreen", opacity=0.10, line_width=0)
            fig.update_layout(
                title=figure_title(fig)
                + f"<br><sup>ICMR = [{lo:.4g}, {hi:.4g}] V (range {hi - lo:.4g} V)</sup>"
            )
    return fig


def noise_figure(
    ds: WaveDataset,
    out: str = "onoise_spectrum",
    *,
    analysis: str = "noise_spectrum",
    total_recipe: dict[str, Any] | None = None,
    title: str | None = None,
) -> go.Figure:
    """Noise spectral density (log-log) + the integrated-total annotation.

    ngspice: density lives in ``analysis="noise_spectrum"`` (signals
    ``onoise_spectrum``/``inoise_spectrum``); Spectre: ``analysis="noise"`` (``out``/
    ``in``). ``total_recipe`` overrides the integrated total (default integrates
    ``out`` over the plotted band via the registry's ``onoise_total`` math).
    """
    fig = waveform_figure(ds, analysis, [out], logy=True, title=title)
    recipe = total_recipe or {"meas": "onoise_total", "analysis": analysis, "out": out}
    total = _try_measure(ds, recipe)
    if total is not None:
        fig.update_layout(
            title=figure_title(fig)
            + f"<br><sup>integrated ({recipe['meas']}) = {total * 1e6:.3g} µV rms</sup>"
        )
    fig.update_xaxes(title_text="frequency (Hz)")
    fig.update_yaxes(title_text="density (V/√Hz)")
    return fig


def pss_spectrum_figure(
    ds: WaveDataset,
    out: str,
    *,
    analysis: str = "pss",
    title: str | None = None,
) -> go.Figure:
    """PSS harmonic spectrum (per-harmonic |phasor|, dB) + THD/HD2/HD3/SFDR labels.

    Reads the fd-PSF's complex per-harmonic phasors (sweep = harmonic frequencies
    [0, f0, 2f0, …]) exactly as the ``thd_pss`` recipe family does.
    """
    an = ds.resolve_analysis(analysis)
    if an is None:
        raise KeyError(f"dataset has no analysis {analysis!r} (have {sorted(ds.analyses)})")
    sig = ds.find_signal(analysis, out)
    if sig is None:
        raise KeyError(f"analysis {analysis!r} has no signal {out!r} (have {sorted(an.signals)})")
    harmonics = np.asarray(sig.data)
    freq_sig = ds.find_signal(analysis, "frequency")
    freq = (
        np.real(np.asarray(freq_sig.data)).astype(float)
        if freq_sig is not None
        else np.arange(harmonics.size, dtype=float)
    )
    mag = np.abs(harmonics).astype(float)
    with np.errstate(divide="ignore"):
        mag_db = 20.0 * np.log10(np.where(mag > 0, mag, np.nan))

    fig = go.Figure(go.Bar(x=freq, y=mag_db, width=(freq[1] - freq[0]) * 0.25 if freq.size > 1 else None,
                           name=f"|{out}(k·f0)|"))
    labels = []
    for meas, fmt_label in (
        ("thd_pss_pct", "THD = {v:.4g} %"),
        ("hd2_db", "HD2 = {v:.1f} dBc"),
        ("hd3_db", "HD3 = {v:.1f} dBc"),
        ("sfdr_db", "SFDR = {v:.1f} dB"),
    ):
        v = _try_measure(ds, {"meas": meas, "analysis": analysis, "out": out})
        if v is not None:
            labels.append(fmt_label.format(v=v))
    fig.update_layout(
        title=(title or f"PSS spectrum: {out}") + (f"<br><sup>{' · '.join(labels)}</sup>" if labels else ""),
        xaxis_title="frequency (Hz)",
        yaxis_title="harmonic magnitude (dBV)",
        template="plotly_white",
    )
    return fig


def fft_spectrum_figure(
    ds: WaveDataset,
    out: str,
    *,
    analysis: str = "tran",
    window: str = "hann",
    title: str | None = None,
    max_points: int | None = None,
) -> go.Figure:
    """Quick-look FFT of a transient trace (uniform-resampled, windowed, one-sided).

    A viewer convenience — for scored distortion numbers use the registry's coherent
    ``thd``/``iip3`` recipes (via :func:`~spicexplorer_waveview.measure.measure_dataset`),
    which resample coherently and read exact integer bins.
    """
    t, v, _ = _xy(ds, analysis, out, None, "re", None, "none")
    if t.size < 8:
        raise ValueError(f"transient trace {out!r} too short for an FFT ({t.size} pts)")
    # ngspice tran output is non-uniform — resample onto a uniform grid first.
    n = int(2 ** np.ceil(np.log2(t.size)))
    tu = np.linspace(t[0], t[-1], n)
    vu = np.interp(tu, t, v)
    if window == "hann":
        w = np.hanning(n)
        cg = float(np.sum(w)) / n  # coherent gain correction
        vu = vu * w
    else:
        cg = 1.0
    spec = np.fft.rfft(vu) / (n * cg / 2.0)
    freq = np.fft.rfftfreq(n, d=(tu[1] - tu[0]))
    mag = np.abs(spec)
    with np.errstate(divide="ignore"):
        mag_db = 20.0 * np.log10(np.where(mag > 0, mag, np.nan))
    if max_points is not None and freq.size > max_points:
        idx = downsample_indices(freq, np.nan_to_num(mag_db, nan=-400.0), max_points, "minmax")
        freq, mag_db = freq[idx], mag_db[idx]
    fig = go.Figure(go.Scatter(x=freq[1:], y=mag_db[1:], mode="lines", name=f"|FFT({out})|"))
    fig.update_layout(
        title=title or f"FFT: {out} ({window} window)",
        xaxis_title="frequency (Hz)",
        yaxis_title="magnitude (dBV)",
        template="plotly_white",
    )
    fig.update_xaxes(type="log")
    return fig


_LOG_COLORS = {"error": "#d33", "warning": "#b70", "note": "#369", "info": "#666"}


def log_view_html(
    summary: LogSummary, *, max_lines: int = 2000, min_level: str = "info", height: int = 360
) -> str:
    """A parsed simulator log as colourised scrollable HTML (notebook log viewer).

    Severity-coloured lines (errors red, warnings amber), header with per-level counts,
    tail-truncated at ``max_lines`` (matching the UI console's keep-the-tail behaviour).
    Display with ``IPython.display.HTML(log_view_html(parse_sim_log(path)))``.
    """
    lines = summary.filtered(min_level)
    shown = lines[-max_lines:]
    header = " · ".join(f"{k}: {v}" for k, v in summary.counts.items() if v)
    rows = []
    if len(lines) > len(shown):
        rows.append(
            f'<div style="color:#999">… {len(lines) - len(shown)} earlier lines hidden …</div>'
        )
    for ln in shown:
        color = _LOG_COLORS.get(ln.level, "#666")
        weight = "bold" if ln.level == "error" else "normal"
        rows.append(
            f'<div style="color:{color};font-weight:{weight}">'
            f'<span style="color:#aaa">{ln.no:>5}</span>  {_html.escape(ln.text)}</div>'
        )
    src = _html.escape(str(summary.path or "<text>"))
    return (
        f'<div style="font-family:monospace;font-size:12px;border:1px solid #ddd;'
        f'border-radius:6px;padding:8px">'
        f'<div style="margin-bottom:6px;color:#333"><b>{src}</b> — {header or "no lines"}</div>'
        f'<div style="max-height:{height}px;overflow-y:auto;white-space:pre-wrap">'
        + "\n".join(rows)
        + "</div></div>"
    )
