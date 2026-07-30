"""spicexplorer-waveview — the universal simulation-result viewer backend.

One call loads any result artifact into an engine-neutral dataset::

    from spicexplorer_waveview import load_result, measure_dataset, bode_figure

    ds = load_result("runs/tb_ac/run_1/netlist.raw")          # ngspice .raw
    ds = load_result("spectre_work/amp022-raw")               # Spectre psfascii dir

    measure_dataset(ds, {"meas": "ugf", "out": "v(vout)"})    # any Tier-1 recipe
    bode_figure(ds, "v(vout)").show()                          # interactive plot

Layering: a leaf tool over ``spicexplorer-core`` only (protocol + measurement registry);
the REST surface lives in ``spicexplorer-api``'s ``/api/waveview/*`` routes.
"""

from .dataset import DatasetResult, WaveAnalysis, WaveDataset, WaveSignal, merge_datasets
from .downsample import downsample_indices, lttb_indices, minmax_indices
from .loaders import load_result, sniff_engine
from .logs import LogLine, LogSummary, classify_line, discover_log, parse_log_text, parse_sim_log
from .measure import measure_dataset, measure_many, measurement_catalog
from .ngspice_loader import load_ngspice_raw
from .plotting import (
    bode_figure,
    dc_figure,
    fft_spectrum_figure,
    log_view_html,
    noise_figure,
    pss_spectrum_figure,
    tran_figure,
    waveform_figure,
)
from .snapshot import (
    PLOT_TEMPLATES,
    PlotTemplate,
    export_htmls,
    export_pngs,
    load_traces,
    save_traces,
    snapshot,
)
from .spectre_loader import load_spectre_raw_dir

__all__ = [
    # dataset model
    "WaveSignal",
    "WaveAnalysis",
    "WaveDataset",
    "DatasetResult",
    "merge_datasets",
    # loaders
    "load_result",
    "sniff_engine",
    "load_ngspice_raw",
    "load_spectre_raw_dir",
    # measurements
    "measure_dataset",
    "measure_many",
    "measurement_catalog",
    # trace snapshots + static PNG / interactive HTML export
    "snapshot",
    "save_traces",
    "load_traces",
    "export_pngs",
    "export_htmls",
    "PlotTemplate",
    "PLOT_TEMPLATES",
    # logs
    "LogLine",
    "LogSummary",
    "parse_sim_log",
    "parse_log_text",
    "classify_line",
    "discover_log",
    # downsampling
    "downsample_indices",
    "minmax_indices",
    "lttb_indices",
    # plotting
    "waveform_figure",
    "bode_figure",
    "tran_figure",
    "dc_figure",
    "noise_figure",
    "pss_spectrum_figure",
    "fft_spectrum_figure",
    "log_view_html",
]
