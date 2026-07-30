"""Trace snapshots + static PNG / interactive HTML export — visual verification.

The analysis flows report single figures of merit (GBW, THD, integrated noise, …);
this module keeps the *evidence*: the key simulation traces behind those numbers,
stored compactly and auto-rendered so a re-sizing or a new testbench can be
eyeballed, not just scored.

Three capabilities, composable or separate:

* **Trace store** — :func:`save_traces` serializes a :class:`~.dataset.WaveDataset`
  (or a subset of its analyses/signals) into ONE compressed ``.npz`` with an embedded
  JSON manifest; :func:`load_traces` round-trips it back to a ``WaveDataset``, so
  every downstream consumer (the Tier-1 measurement registry via ``DatasetResult``,
  the Plotly builders, this module's own renderers) works on stored traces exactly
  as on a live artifact. Complex AC-family signals survive verbatim.
* **PNG export** — :func:`export_pngs` renders each plottable analysis through a
  **per-analysis plot template** (:data:`PLOT_TEMPLATES`): Bode panels for
  ``ac``/``stb``/``pac``, time-domain for ``tran``, transfer for ``dc``, log-log
  density for ``noise``/``pnoise``, a harmonic spectrum for ``pss``. Unknown swept
  kinds fall back to a plain x-y plot (a key trace always exports *something*);
  point-data analyses (``op``) are skipped. Each analysis writes one COMBINED image
  plus (by default) one per-signal breakout — a mV ripple riding next to a
  rail-to-rail clock is invisible on the shared axis but obvious on its own.
* **HTML export** — :func:`export_htmls` writes the interactive Plotly companion of
  each combined figure (zoom/pan/hover; click a legend entry to isolate a trace, so
  breakout files are unnecessary). By default the pages share ONE ``plotly.min.js``
  written next to them (``include_plotlyjs="directory"``) — small and offline-viewable.

:func:`snapshot` is the one-liner combining all three over any result artifact path
(ngspice ``.raw`` file / Spectre psfascii raw dir — engine sniffed by
:func:`~.loaders.load_result`) or an already-loaded dataset.

Default trace selection keeps the plots honest: branch-current/instance-internal
``:`` signals are excluded (a −300 dB source current squashes the actual transfer),
as are numerically-zero traces (an AC-grounded rail is a −6000 dB floor line), the
abscissa aliases, and — on the noise family — everything but the density signals
(Spectre's noise PSF also carries the input→output ``gain`` transfer it used for
input-referral, plus per-device contributions). Top-level nets rank before
subcircuit-internal (dotted) nodes. Pin exact traces via a template's ``signals=``.

PNG rendering uses matplotlib's object-oriented Agg canvas directly — no pyplot, no
global backend mutation — so it is safe inside library/server processes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import numpy as np

from .dataset import WaveAnalysis, WaveDataset, WaveSignal

__all__ = [
    "PlotTemplate",
    "PLOT_TEMPLATES",
    "save_traces",
    "load_traces",
    "export_pngs",
    "export_htmls",
    "snapshot",
]

_STORE_VERSION = 1

# Trace-name preference when a template does not pin explicit signals: well-known
# output/probe names first, then top-level nets, then hierarchical internals.
# Names compare through _norm (the ngspice v(...) wrapper is stripped).
_PREFERRED = ("vout", "out", "loopgain", "vzd", "vzs", "in")
_MAX_TRACES = 8
#: max|x| at or below this is numerically zero — a dead trace (an AC-grounded rail)
#: that would only draw a log-floor line and squash the real transfers.
_DEGENERATE_FLOOR = 1e-18
#: noise-family default selection: DENSITY signals only. Spectre's noise PSF also
#: carries the input→output `gain` transfer it used for input-referral and per-device
#: contribution rows — meaningless on a V/√Hz axis.
_DENSITY_SIGNALS = ("out", "onoise_spectrum", "onoise", "in", "inoise_spectrum", "inoise")
_KIND_SIGNALS: dict[str, tuple[str, ...]] = {
    "noise": _DENSITY_SIGNALS,
    "noise_spectrum": _DENSITY_SIGNALS,
    "pnoise": _DENSITY_SIGNALS,
}


# ---------------------------------------------------------------------------
# Trace store — WaveDataset ⇄ one compressed .npz (+ embedded JSON manifest)
# ---------------------------------------------------------------------------
def save_traces(
    dataset: WaveDataset,
    path: str | Path,
    *,
    analyses: Iterable[str] | None = None,
    signals: Mapping[str, Iterable[str]] | None = None,
    label: str | None = None,
) -> Path:
    """Serialize ``dataset`` (or a selection) into one compressed ``.npz`` archive.

    ``analyses`` limits which analyses are stored (default: all); ``signals`` maps an
    analysis key to the signal names to keep (default: every signal — the sweep is
    always kept). The archive embeds a JSON manifest (source, engine, per-analysis
    sweep/units/scalars, ``label``) so :func:`load_traces` reconstructs a faithful
    ``WaveDataset`` with provenance.
    """
    want = set(analyses) if analyses is not None else None
    arrays: dict[str, np.ndarray] = {}
    manifest: dict[str, Any] = {
        "version": _STORE_VERSION,
        "source": dataset.source,
        "engine": dataset.engine,
        "label": label,
        "aliases": dict(dataset.aliases),
        "warnings": list(dataset.warnings),
        "analyses": {},
    }
    idx = 0
    for key, an in dataset.analyses.items():
        if want is not None and key not in want:
            continue
        keep = None
        if signals is not None and key in signals:
            keep = {str(s) for s in signals[key]}
            if an.sweep:
                keep.add(an.sweep)  # the abscissa always rides along
        entry: dict[str, Any] = {
            "native_name": an.native_name,
            "sweep": an.sweep,
            "scalars": {k: float(v) for k, v in an.scalars.items()},
            "signals": [],
        }
        for name, sig in an.signals.items():
            if keep is not None and name not in keep:
                continue
            akey = f"a{idx}"
            idx += 1
            arrays[akey] = np.asarray(sig.data)
            entry["signals"].append({"name": name, "key": akey, "units": sig.units})
        manifest["analyses"][key] = entry

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # pyright can't prove the **arrays keys miss savez's `allow_pickle` keyword — the
    # keys are generated `a<N>` names, so the collision is impossible by construction
    np.savez_compressed(
        out,
        __manifest__=np.array(json.dumps(manifest)),
        **arrays,  # pyright: ignore[reportArgumentType, reportCallIssue]
    )
    return out


def load_traces(path: str | Path) -> WaveDataset:
    """Round-trip a :func:`save_traces` archive back into a :class:`WaveDataset`."""
    with np.load(Path(path), allow_pickle=False) as npz:
        manifest = json.loads(str(npz["__manifest__"][()]))
        if int(manifest.get("version", 0)) != _STORE_VERSION:
            raise ValueError(
                f"trace store {path} has version {manifest.get('version')!r}; "
                f"this reader understands version {_STORE_VERSION}."
            )
        ds = WaveDataset(
            source=str(manifest.get("source", str(path))),
            engine=str(manifest.get("engine", "stored")),
            aliases=dict(manifest.get("aliases", {})),
            warnings=list(manifest.get("warnings", [])),
        )
        for key, entry in manifest.get("analyses", {}).items():
            an = WaveAnalysis(
                analysis=key,
                native_name=str(entry.get("native_name", key)),
                sweep=entry.get("sweep"),
                scalars={k: float(v) for k, v in entry.get("scalars", {}).items()},
            )
            for row in entry.get("signals", []):
                an.signals[row["name"]] = WaveSignal(
                    name=row["name"], data=np.array(npz[row["key"]]), units=row.get("units")
                )
            ds.analyses[key] = an
    return ds


# ---------------------------------------------------------------------------
# Per-analysis plot templates
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PlotTemplate:
    """How one analysis KIND renders to a figure.

    ``style`` picks the renderer: ``"bode"`` (two panels, dB magnitude + unwrapped
    phase vs log-f), ``"xy"`` (linear x-y), ``"loglog"`` (log-log density),
    ``"spectrum"`` (per-harmonic stem/bar, dB vs frequency). ``signals`` pins the
    traces to draw (default: preferred-name heuristic, capped at ``_MAX_TRACES``);
    ``x_label``/``y_label`` override the axis captions.
    """

    style: str
    title: str
    signals: tuple[str, ...] = ()
    x_label: str | None = None
    y_label: str | None = None
    # extra keyword hints for the renderer (e.g. {"phase": False} on a bode)
    options: Mapping[str, Any] = field(default_factory=dict)


#: The per-analysis-kind template table. Override/extend per call via
#: ``export_pngs(..., templates={...})`` — unknown swept kinds fall back to "xy".
PLOT_TEMPLATES: dict[str, PlotTemplate] = {
    "ac": PlotTemplate("bode", "AC transfer"),
    "stb": PlotTemplate("bode", "Loop gain (stb)", signals=("loopGain",)),
    "pac": PlotTemplate("bode", "Periodic AC (pac, baseband)"),
    "pac_sb": PlotTemplate("bode", "Periodic AC sideband"),
    "tran": PlotTemplate("xy", "Transient", x_label="time [s]"),
    "pss_td": PlotTemplate("xy", "PSS steady-state period", x_label="time [s]"),
    "dc": PlotTemplate("xy", "DC transfer"),
    "noise": PlotTemplate("loglog", "Noise density", y_label="V/√Hz"),
    "pnoise": PlotTemplate("loglog", "Periodic noise density", y_label="V/√Hz"),
    "pss": PlotTemplate("spectrum", "PSS harmonics"),
}

_FALLBACK = PlotTemplate("xy", "Traces")


def _slug(name: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in name)


def _pick_signals(an: WaveAnalysis, template: PlotTemplate, kind: str) -> list[WaveSignal]:
    if template.signals:
        picked = []
        for name in template.signals:
            sig = an.signals.get(name)
            if sig is None:  # case-tolerant second chance
                lowered = {k.lower(): v for k, v in an.signals.items()}
                sig = lowered.get(name.lower())
            if sig is not None:
                picked.append(sig)
        return picked

    def _norm(name: str) -> str:
        base = name.lower()
        if base.startswith("v(") and base.endswith(")"):
            base = base[2:-1]  # the ngspice node wrapper
        return base

    # never y-plot the abscissa or its canonical aliases (the loaders export the sweep
    # under its native name AND "frequency"/"time" so recipes needn't know the spelling)
    absc = {"frequency", "freq", "time", "sweep"}
    candidates = [n for n in an.signals if n != an.sweep and _norm(n) not in absc]

    # KEY traces are node voltages: drop branch currents (Spectre `VDD:p`, ngspice
    # `i(vdd)`/`#branch`) and device-internal signals (OSDI `v(n.x…#di)` nodes,
    # per-device noise rows) by default — a −300 dB source current on the same axis
    # squashes the actual transfer flat.
    def _is_internal(name: str) -> bool:
        return ":" in name or "#" in name or name.lower().startswith("i(")

    nodes = [n for n in candidates if not _is_internal(n)]
    pool = nodes or candidates
    # noise family: density signals only (Spectre's `gain` transfer curve and the
    # per-device contribution rows stay out of a V/√Hz plot)
    wanted = _KIND_SIGNALS.get(kind)
    if wanted:
        lowered = {_norm(n): n for n in pool}
        named = [lowered[w] for w in wanted if w in lowered]
        pool = named or pool
    elif any(n.lower().startswith("v(") for n in pool):
        # an ngspice raw lists deck-derived `let`/meas vectors (dcgain, ph, ugf, …)
        # as bare names NEXT TO the real v(<node>) traces — default to the nodes
        pool = [n for n in pool if n.lower().startswith("v(")]
    # numerically-zero traces (AC-grounded rails) draw only the log floor — drop them
    live = [
        n
        for n in pool
        if float(np.max(np.abs(np.asarray(an.signals[n].data)), initial=0.0))
        > _DEGENERATE_FLOOR
    ]
    pool = live or pool

    def _key(name: str) -> tuple[int, bool, str]:
        base = _norm(name)
        try:
            rank = _PREFERRED.index(base)
        except ValueError:
            rank = len(_PREFERRED)
        # top-level nets before subcircuit-internal (dotted) nodes, then case-blind
        return (rank, "." in base, base)

    ordered = sorted(pool, key=_key)[:_MAX_TRACES]
    return [an.signals[n] for n in ordered]


def _sweep_of(an: WaveAnalysis) -> np.ndarray | None:
    if an.sweep and an.sweep in an.signals:
        return np.real(np.asarray(an.signals[an.sweep].data))
    return None


def _resolve_template(
    key: str, templates: Mapping[str, PlotTemplate] | None
) -> tuple[str, PlotTemplate]:
    kind = key.split(":", 1)[0].strip().lower()
    template = None
    if templates:
        template = templates.get(key) or templates.get(kind)
    if template is None:
        template = PLOT_TEMPLATES.get(kind, _FALLBACK)
    return kind, template


def _figure_title(prefix: str, template: PlotTemplate, an: WaveAnalysis, key: str) -> str:
    title = f"{template.title} — {an.native_name}" if an.native_name != key else template.title
    if prefix:
        title = f"{prefix.rstrip('_- ')}: {title}"
    return title


# ---------------------------------------------------------------------------
# Static PNG rendering (matplotlib OO/Agg — no pyplot, no global state)
# ---------------------------------------------------------------------------
def _render_png(
    an: WaveAnalysis,
    template: PlotTemplate,
    title: str,
    annotations: Mapping[str, float] | None,
    out: Path,
    dpi: int,
    sigs: list[WaveSignal],
) -> None:
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError as exc:  # pragma: no cover - matplotlib is a declared dependency
        raise ImportError(
            "PNG export needs matplotlib (a declared spicexplorer-waveview "
            "dependency; `uv sync` installs it)."
        ) from exc

    x = _sweep_of(an)
    if x is None or not sigs:
        raise ValueError(f"analysis {an.analysis!r} has no sweep/traces to render")

    two_panel = template.style == "bode" and bool(template.options.get("phase", True))
    fig = Figure(figsize=(8.0, 6.0 if two_panel else 4.5), constrained_layout=True)
    FigureCanvasAgg(fig)

    if template.style == "bode":
        axes = fig.subplots(2 if two_panel else 1, 1, sharex=True)
        ax_mag = axes[0] if two_panel else axes
        for sig in sigs:
            h = np.asarray(sig.data)
            mag = 20.0 * np.log10(np.maximum(np.abs(h), 1e-300))
            ax_mag.semilogx(x, mag, label=sig.name)
        ax_mag.set_ylabel(template.y_label or "|H| [dB]")
        ax_mag.grid(True, which="both", alpha=0.3)
        ax_mag.legend(loc="best", fontsize=8)
        if two_panel:
            ax_ph = axes[1]
            for sig in sigs:
                ph = np.degrees(np.unwrap(np.angle(np.asarray(sig.data))))
                ax_ph.semilogx(x, ph, label=sig.name)
            ax_ph.set_ylabel("phase [deg]")
            ax_ph.set_xlabel(template.x_label or "frequency [Hz]")
            ax_ph.grid(True, which="both", alpha=0.3)
        else:
            ax_mag.set_xlabel(template.x_label or "frequency [Hz]")
        ax_anno = ax_mag
    elif template.style == "loglog":
        ax = fig.subplots()
        for sig in sigs:
            y = np.abs(np.asarray(sig.data))
            ax.loglog(x[x > 0], y[x > 0] if y.shape == x.shape else y, label=sig.name)
        ax.set_xlabel(template.x_label or "frequency [Hz]")
        ax.set_ylabel(template.y_label or "density")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(loc="best", fontsize=8)
        ax_anno = ax
    elif template.style == "spectrum":
        ax = fig.subplots()
        # ax.stem draws every call in the SAME default color — cycle explicitly, or a
        # multi-signal spectrum is an unreadable wall of identical blue stems
        for i, sig in enumerate(sigs):
            c = f"C{i % 10}"
            mags = np.abs(np.asarray(sig.data))
            db = 20.0 * np.log10(np.maximum(mags, 1e-300))
            ax.stem(x, db, linefmt=f"{c}-", markerfmt=f"{c}o", basefmt=" ", label=sig.name)
        ax.set_xlabel(template.x_label or "frequency [Hz]")
        ax.set_ylabel(template.y_label or "|harmonic| [dBV]")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
        ax_anno = ax
    else:  # "xy"
        ax = fig.subplots()
        for sig in sigs:
            ax.plot(x, np.real(np.asarray(sig.data)), label=sig.name)
        ax.set_xlabel(template.x_label or (an.sweep or "sweep"))
        ax.set_ylabel(template.y_label or "value")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
        ax_anno = ax

    fig.suptitle(title, fontsize=11)
    if annotations:
        text = "\n".join(f"{k} = {v:.6g}" for k, v in annotations.items())
        ax_anno.text(
            0.02, 0.02, text, transform=ax_anno.transAxes, fontsize=8,
            va="bottom", ha="left",
            bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.75},
        )
    fig.savefig(out, dpi=dpi, format="png")


def export_pngs(
    dataset: WaveDataset,
    out_dir: str | Path,
    *,
    analyses: Iterable[str] | None = None,
    templates: Mapping[str, PlotTemplate] | None = None,
    annotations: Mapping[str, Mapping[str, float]] | None = None,
    prefix: str = "",
    dpi: int = 130,
    per_signal: bool = True,
    on_skip: Callable[[str, str], None] | None = None,
) -> list[Path]:
    """Render PNGs for every plottable analysis of ``dataset`` into ``out_dir``.

    Each analysis writes one COMBINED image (``<prefix><analysis>.png``, all selected
    traces on shared axes) and — when ``per_signal`` and more than one trace was
    selected — one autoscaled breakout per trace (``<prefix><analysis>.<signal>.png``):
    a mV ripple next to a rail-to-rail clock is invisible combined but obvious alone.

    The template for each analysis resolves: caller ``templates`` (keyed by analysis
    key OR kind) → :data:`PLOT_TEMPLATES` by kind → an x-y fallback for any swept
    analysis. Point-data analyses (no sweep — e.g. ``op``) are skipped, reported via
    ``on_skip(analysis, reason)`` when given. ``annotations`` maps an analysis key to
    ``{label: value}`` floats stamped onto its figures (e.g. the run's measured
    metrics). Returns the written paths.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    want = set(analyses) if analyses is not None else None
    written: list[Path] = []
    for key, an in dataset.analyses.items():
        if want is not None and key not in want:
            continue
        if _sweep_of(an) is None:
            if on_skip:
                on_skip(key, "no sweep (point data)")
            continue
        kind, template = _resolve_template(key, templates)
        sigs = _pick_signals(an, template, kind)
        if not sigs:
            if on_skip:
                on_skip(key, "no plottable traces")
            continue
        safe = _slug(key)
        title = _figure_title(prefix, template, an, key)
        anno = (annotations or {}).get(key)
        try:
            path = out / f"{prefix}{safe}.png"
            _render_png(an, template, title, anno, path, dpi, sigs)
            written.append(path)
            if per_signal and len(sigs) > 1:
                for sig in sigs:
                    p_sig = out / f"{prefix}{safe}.{_slug(sig.name)}.png"
                    _render_png(an, template, f"{title} — {sig.name}", anno, p_sig, dpi, [sig])
                    written.append(p_sig)
        except ValueError as exc:
            if on_skip:
                on_skip(key, str(exc))
            continue
    return written


# ---------------------------------------------------------------------------
# Interactive HTML rendering (Plotly — the companion of each combined PNG)
# ---------------------------------------------------------------------------
def _plotly_figure(
    an: WaveAnalysis,
    template: PlotTemplate,
    title: str,
    annotations: Mapping[str, float] | None,
    sigs: list[WaveSignal],
) -> Any:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    x = _sweep_of(an)
    if x is None or not sigs:
        raise ValueError(f"analysis {an.analysis!r} has no sweep/traces to render")

    sub = " · ".join(f"{k} = {v:.6g}" for k, v in (annotations or {}).items())
    full_title = title + (f"<br><sup>{sub}</sup>" if sub else "")

    two_panel = template.style == "bode" and bool(template.options.get("phase", True))
    if template.style == "bode" and two_panel:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                            subplot_titles=("magnitude", "phase"))
        for sig in sigs:
            h = np.asarray(sig.data)
            mag = 20.0 * np.log10(np.maximum(np.abs(h), 1e-300))
            ph = np.degrees(np.unwrap(np.angle(h)))
            fig.add_trace(
                go.Scatter(x=x, y=mag, mode="lines", name=sig.name, legendgroup=sig.name),
                row=1, col=1,
            )
            fig.add_trace(
                go.Scatter(x=x, y=ph, mode="lines", name=sig.name,
                           legendgroup=sig.name, showlegend=False),
                row=2, col=1,
            )
        fig.update_xaxes(type="log", row=1, col=1)
        fig.update_xaxes(type="log", title_text=template.x_label or "frequency (Hz)",
                         row=2, col=1)
        fig.update_yaxes(title_text=template.y_label or "|H| (dB)", row=1, col=1)
        fig.update_yaxes(title_text="phase (°)", row=2, col=1)
        fig.update_layout(height=560)
    elif template.style == "bode":  # magnitude-only bode
        fig = go.Figure()
        for sig in sigs:
            mag = 20.0 * np.log10(np.maximum(np.abs(np.asarray(sig.data)), 1e-300))
            fig.add_trace(go.Scatter(x=x, y=mag, mode="lines", name=sig.name))
        fig.update_xaxes(type="log", title_text=template.x_label or "frequency (Hz)")
        fig.update_yaxes(title_text=template.y_label or "|H| (dB)")
    elif template.style == "loglog":
        fig = go.Figure()
        for sig in sigs:
            y = np.abs(np.asarray(sig.data))
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=sig.name))
        fig.update_xaxes(type="log", title_text=template.x_label or "frequency (Hz)")
        fig.update_yaxes(type="log", title_text=template.y_label or "density")
    elif template.style == "spectrum":
        fig = go.Figure()
        for sig in sigs:
            mags = np.abs(np.asarray(sig.data))
            db = 20.0 * np.log10(np.maximum(mags, 1e-300))
            fig.add_trace(go.Bar(x=x, y=db, name=sig.name))
        # grouped bars sit side-by-side at each harmonic — overlapping stems don't
        fig.update_layout(barmode="group")
        fig.update_xaxes(title_text=template.x_label or "frequency (Hz)")
        fig.update_yaxes(title_text=template.y_label or "|harmonic| (dBV)")
    else:  # "xy"
        fig = go.Figure()
        for sig in sigs:
            fig.add_trace(
                go.Scatter(x=x, y=np.real(np.asarray(sig.data)), mode="lines", name=sig.name)
            )
        fig.update_xaxes(title_text=template.x_label or (an.sweep or "sweep"))
        fig.update_yaxes(title_text=template.y_label or "value")

    fig.update_layout(title=full_title, template="plotly_white", hovermode="x unified")
    return fig


def export_htmls(
    dataset: WaveDataset,
    out_dir: str | Path,
    *,
    analyses: Iterable[str] | None = None,
    templates: Mapping[str, PlotTemplate] | None = None,
    annotations: Mapping[str, Mapping[str, float]] | None = None,
    prefix: str = "",
    include_plotlyjs: bool | str = "directory",
    on_skip: Callable[[str, str], None] | None = None,
) -> list[Path]:
    """Write one interactive Plotly HTML per plottable analysis into ``out_dir``.

    The interactive companion of :func:`export_pngs`: same template resolution, same
    trace selection, same ``annotations`` (rendered as the title's subtitle line).
    Per-signal breakout files are unnecessary here — click a legend entry to isolate
    a trace, zoom freely. ``include_plotlyjs`` is passed to plotly's ``write_html``;
    the default ``"directory"`` writes ONE shared ``plotly.min.js`` next to the pages
    so a gallery stays small and offline-viewable. Returns the written paths.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    want = set(analyses) if analyses is not None else None
    written: list[Path] = []
    for key, an in dataset.analyses.items():
        if want is not None and key not in want:
            continue
        if _sweep_of(an) is None:
            if on_skip:
                on_skip(key, "no sweep (point data)")
            continue
        kind, template = _resolve_template(key, templates)
        sigs = _pick_signals(an, template, kind)
        if not sigs:
            if on_skip:
                on_skip(key, "no plottable traces")
            continue
        title = _figure_title(prefix, template, an, key)
        try:
            fig = _plotly_figure(an, template, title, (annotations or {}).get(key), sigs)
        except ValueError as exc:
            if on_skip:
                on_skip(key, str(exc))
            continue
        path = out / f"{prefix}{_slug(key)}.html"
        fig.write_html(str(path), include_plotlyjs=include_plotlyjs)
        written.append(path)
    return written


# ---------------------------------------------------------------------------
# The one-liner
# ---------------------------------------------------------------------------
#: Analysis KINDS excluded from a default snapshot — diagnostics, not key traces
#: (a real pac run leaves one PSF per sideband: 30+ conversion-gain curves).
#: Opt back in per call via ``analyses=`` or ``include_sidebands=True``.
_DEFAULT_EXCLUDE_KINDS: frozenset[str] = frozenset({"pac_sb"})


def snapshot(
    source: str | Path | WaveDataset,
    out_dir: str | Path,
    *,
    label: str | None = None,
    traces: bool = True,
    png: bool = True,
    html: bool = True,
    analyses: Iterable[str] | None = None,
    include_sidebands: bool = False,
    templates: Mapping[str, PlotTemplate] | None = None,
    annotations: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, Any]:
    """Store key traces and/or auto-export PNGs + interactive HTMLs for one artifact.

    ``source`` is a result artifact path (ngspice ``.raw`` / Spectre psfascii raw
    dir — engine sniffed) or an already-loaded :class:`WaveDataset`. Writes
    ``<label>.traces.npz`` (when ``traces``), per-analysis PNGs — combined + per-signal
    breakouts — (when ``png``) and per-analysis interactive Plotly pages (when
    ``html``; one shared ``plotly.min.js`` rides in ``out_dir``). By default only the
    KEY analyses snapshot — pac sidebands (``pac_sb*``) are diagnostics and stay out
    unless ``include_sidebands=True`` or ``analyses`` names them. Returns
    ``{"traces": Path | None, "pngs": […], "htmls": […], "skipped": [(analysis, reason), …]}``.
    """
    if isinstance(source, WaveDataset):
        ds = source
    else:
        from .loaders import load_result

        ds = load_result(source)
    name = label or Path(str(ds.source)).stem or "result"
    out = Path(out_dir)
    if analyses is None:
        keep = None if include_sidebands else [
            k for k in ds.analyses
            if k.split(":", 1)[0].strip().lower() not in _DEFAULT_EXCLUDE_KINDS
        ]
    else:
        keep = list(analyses)
    skipped: list[tuple[str, str]] = []
    result: dict[str, Any] = {"traces": None, "pngs": [], "htmls": [], "skipped": skipped}
    if traces:
        result["traces"] = save_traces(
            ds, out / f"{name}.traces.npz", analyses=keep, label=label
        )
    if png:
        result["pngs"] = export_pngs(
            ds, out, analyses=keep, templates=templates, annotations=annotations,
            prefix=f"{name}_", on_skip=lambda a, r: skipped.append((a, r)),
        )
    if html:
        result["htmls"] = export_htmls(
            ds, out, analyses=keep, templates=templates, annotations=annotations,
            prefix=f"{name}_",
            # the PNG pass already recorded the skips; don't double-report them
            on_skip=None if png else (lambda a, r: skipped.append((a, r))),
        )
    return result
