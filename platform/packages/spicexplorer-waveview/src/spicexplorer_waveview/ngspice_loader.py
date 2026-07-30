"""ngspice ``.raw`` → :class:`~spicexplorer_waveview.dataset.WaveDataset`.

Reads any ngspice raw file (binary or ascii, single- or multi-plot) via spicelib's
``RawRead`` — the same reader the platform's run path uses — and maps each plot title
to the engine-neutral analysis vocabulary that ``spicexplorer_core.spice_engine.spicelib``
speaks (``resolve_ngspice_plot_type``'s table, reversed). Unknown plot titles are kept
(slugified) rather than dropped, with a warning — a *universal* viewer never discards
data it merely doesn't recognise.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from spicelib import RawRead

from .dataset import WaveAnalysis, WaveDataset, WaveSignal

__all__ = ["load_ngspice_raw", "PLOT_TITLE_TO_ANALYSIS"]

# ngspice plot title → engine-neutral analysis key. The exact reverse of core's
# `_ANALYSIS_TO_PLOT_TYPE` (spice_engine/spicelib.py) so a recipe evaluated through
# `DatasetResult` reads the SAME plot the optimizer's `NgspiceSimResult` would.
PLOT_TITLE_TO_ANALYSIS: dict[str, str] = {
    "AC Analysis": "ac",
    "DC transfer characteristic": "dc",
    "Operating Point": "op",
    "Transient Analysis": "tran",
    "Integrated Noise": "noise",
    "Noise Spectral Density Curves": "noise_spectrum",
}

# ngspice alias chain (mirrors core's map; the cross-engine commons live in dataset.py).
_NGSPICE_ALIASES: dict[str, str] = {}

# spicelib trace `whattype` → display units.
_WHATTYPE_UNITS: dict[str, str] = {
    "voltage": "V",
    "current": "A",
    "time": "s",
    "frequency": "Hz",
    "temperature": "°C",
}


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", title.strip().lower()).strip("_")
    return s or "plot"


def _unique_key(base: str, taken: set[str]) -> str:
    if base not in taken:
        return base
    n = 2
    while f"{base}:{n}" in taken:
        n += 1
    return f"{base}:{n}"


def load_ngspice_raw(path: str | Path) -> WaveDataset:
    """Load one ngspice ``.raw`` file into a :class:`WaveDataset`.

    Every plot in the file becomes one analysis. When two plots share a title (e.g.
    two ``tran`` runs in one raw) the FIRST keeps the canonical key — matching
    ``_extract_wave_from_raw``'s first-match semantics — and later ones get
    ``<key>:2``, ``<key>:3``, … so nothing is dropped.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"ngspice raw file not found: {p}")

    raw = RawRead(raw_filename=str(p))
    ds = WaveDataset(source=str(p), engine="ngspice", aliases=dict(_NGSPICE_ALIASES))

    plots = list(getattr(raw, "plots", None) or [raw])
    taken: set[str] = set()
    for plot in plots:
        title = str(plot.get_plot_name() or "").strip()
        base = PLOT_TITLE_TO_ANALYSIS.get(title)
        if base is None:
            base = _slug(title)
            ds.warnings.append(
                f"unrecognised ngspice plot title {title!r} kept under analysis key {base!r}"
            )
        key = _unique_key(base, taken)
        taken.add(key)

        an = WaveAnalysis(analysis=key, native_name=title or key)

        trace_names = [str(n) for n in plot.get_trace_names()]

        # Batch-read the whole plot ONCE before touching individual traces. spicelib's
        # lazy Normal-Access path re-reads the plot's ENTIRE binary section on every
        # cache-miss `get_wave(name)` and caches each trace as a VIEW pinning that
        # call's full-file buffer — one buffer per trace. On a wide raw (a loopgain tb
        # saving 3239 signals × 57 MB) that is traces × file-size ≈ 180 GB and OOM-kills
        # the API worker. One bulk read = one shared buffer.
        read_all = getattr(plot, "read_trace_data", None)
        if callable(read_all) and trace_names:
            try:
                read_all(trace_names)
            except Exception:  # noqa: BLE001 — fall back to per-trace reads below
                pass

        for trace_name in trace_names:
            try:
                # np.array (copy) — not asarray: get_wave returns a view into the
                # bulk-read buffer; copying detaches the ~n_points signal so the
                # whole-file buffer can be freed once this loop ends.
                data = np.array(plot.get_wave(trace_name))
            except Exception as exc:  # noqa: BLE001 — keep loading the other traces
                ds.warnings.append(f"{title!r}: could not read trace {trace_name!r}: {exc}")
                continue
            units: str | None = None
            try:
                trace = plot.get_trace(trace_name)
                units = _WHATTYPE_UNITS.get(str(getattr(trace, "whattype", "")).lower())
            except Exception:  # noqa: BLE001 — units are cosmetic
                pass
            an.signals[str(trace_name)] = WaveSignal(name=str(trace_name), data=data, units=units)

        # Read the sweep AFTER the traces: on spicelib's lazy binary path `plot.axis`
        # is only materialized by the reads above — probing it up front (as this
        # loader once did) reported sweep=None for every binary raw, which degraded
        # /wave's default abscissa to the point index.
        axis = getattr(plot, "axis", None)
        if axis is not None:
            an.sweep = str(getattr(axis, "name", "") or "") or None

        # Point analyses (op / integrated noise) are single-value traces — surface them
        # as scalars too, so `DatasetResult.scalar` and the API's meta view see them.
        if an.sweep is None:
            for sig in an.signals.values():
                arr = np.asarray(sig.data).reshape(-1)
                if arr.size == 1:
                    an.scalars[sig.name] = float(np.real(arr[0]))

        ds.analyses[key] = an

    if not ds.analyses:
        ds.warnings.append("raw file parsed but contains no plots")
    return ds
