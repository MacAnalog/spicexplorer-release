"""Recorded outputs of the last run of the load-optimization-trace notebook (static record).

This script replaces ``explore_load_optimization_trace.recorded-outputs.html``. It holds what that
page recorded: the saved outputs of ``test_load_optimization_trace.ipynb`` at commit ``d85614c``
(the notebook is now ``explore_load_optimization_trace.py`` beside this file), run on 2026-02-03
at 15:26. The run loaded ``checkpoints/LHSSearch_2000.json``, a 2,000-trial LHSSearch checkpoint
that is in no repository, so these outputs cannot be reproduced by re-running the notebook;
``project_setup.yaml`` in this folder now names SamplingSearch with a budget of 5. Home and
scratch paths read ``/home/<user>/`` and ``/scratch/<user>/``.

What is kept:

- every code cell of the run and its text output, verbatim (the two logger blocks, the parameter
  and metric lists, and the four returned-array reprs);
- the data behind the seven Plotly figures, one row per trial in
  ``explore_load_optimization_trace.recorded-outputs.csv``: the two swept widths
  ``x_dut_nfet_input_w`` and ``x_dut_nfet_mirror_w`` (9 significant figures), the metrics
  ``ugf``, ``dcgain``, ``tsettle`` (7) and ``v(inoise_total)`` (9), and the optimizer ``score``
  that colours every marker (10). An empty field is NaN: 605 trials have no ``tsettle`` and one has
  no ``v(inoise_total)``.

The figures are rebuilt with Plotly (marker size 10, the Viridis colour scale the page used, and
each figure's title, axis titles and linear/log axes).

Usage::

    python explore_load_optimization_trace_recorded_outputs.py            # print, build figures
    python explore_load_optimization_trace_recorded_outputs.py --show     # open figures
    python explore_load_optimization_trace_recorded_outputs.py --out DIR  # write figure JSON

Nothing is written unless ``--out`` is given; keep that directory out of the repository.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import plotly.graph_objects as go

DATA_FILE = Path(__file__).with_name("explore_load_optimization_trace.recorded-outputs.csv")

COLUMNS = (
    "x_dut_nfet_input_w",
    "x_dut_nfet_mirror_w",
    "ugf",
    "dcgain",
    "v(inoise_total)",
    "tsettle",
    "score",
)


@dataclass(frozen=True)
class FigureSpec:
    """One recorded Plotly scatter: which columns it plots and how its axes were set."""

    key: str
    title: str
    x: str
    y: str
    log_x: bool
    log_y: bool
    colorbar: str


FIGURES = (
    FigureSpec(
        "fig-1",
        "Design Space Exploration: x_dut_nfet_mirror_w vs. x_dut_nfet_input_w",
        "x_dut_nfet_input_w",
        "x_dut_nfet_mirror_w",
        False,
        False,
        "Score",
    ),
    FigureSpec("fig-2", "Optimization Trace: dcgain vs. ugf", "ugf", "dcgain", False, False, "FOM"),
    FigureSpec("fig-3", "Optimization Trace: dcgain vs. ugf", "ugf", "dcgain", True, False, "FOM"),
    FigureSpec("fig-4", "Optimization Trace: dcgain vs. ugf", "ugf", "dcgain", False, True, "FOM"),
    FigureSpec("fig-5", "Optimization Trace: dcgain vs. ugf", "ugf", "dcgain", True, True, "FOM"),
    FigureSpec(
        "fig-6",
        "Optimization Trace: dcgain vs. v(inoise_total)",
        "v(inoise_total)",
        "dcgain",
        True,
        False,
        "FOM",
    ),
    FigureSpec(
        "fig-7", "Optimization Trace: dcgain vs. tsettle", "tsettle", "dcgain", True, False, "FOM"
    ),
)


@dataclass(frozen=True)
class Cell:
    """One code cell of the recorded run, its text outputs and the figures it drew."""

    prompt: str
    code: str
    outputs: tuple[str, ...]
    figures: tuple[str, ...] = ()


CELLS = (
    Cell(
        "In [1] (cell 0)",
        "from spicexplorer.optimization      import Circuit_Optimizer_Orchestrator_with_SPICE\n"
        "from spicexplorer.viz               import Optimization_Log_Visualizer\n"
        "from spicexplorer_core.logging.logger_setup               import"
        " setup_loggers_with_spicelib_suppression as setup_loggers\n"
        "\n"
        "from pathlib import Path\n"
        "\n"
        "logger = setup_loggers()\n"
        'logger.info("Spicelib_Wrapper imported successfully.")',
        (
            "15:26:03 - spicexplorer: [INFO] 🚀 Logger initialized!\n"
            "15:26:03 - spicexplorer: [INFO] 📄 Log file: /home/<user>/code/TCAD/modules/"
            "SpiceXplorer/examples/OTA/5t-ota/ihp-sg13g2/sizing/logs/"
            "SpiceXplorer_2026-02-03_15-26-03.log\n"
            "15:26:03 - spicexplorer: [INFO] 👀 TQDM and Errors will still show in console"
            " (stderr).\n"
            "15:26:03 - spicexplorer: [INFO] 🔇 Standard outputs and SPICE logs are redirected"
            " to file (stdout).\n"
            "15:26:03 - spicexplorer: [INFO] Spicelib_Wrapper imported successfully.\n",
        ),
    ),
    Cell(
        "In [2] (cell 1)",
        'path_to_checkpoint = Path("./checkpoints/LHSSearch_2000.json")\n'
        "viz = Optimization_Log_Visualizer.load_checkpoint(path_to_checkpoint=path_to_checkpoint)",
        (
            "15:26:03 - spicexplorer.viz.plotting: [INFO] ✅ Checkpoint loaded successfully from"
            " checkpoints/LHSSearch_2000.json\n",
        ),
    ),
    Cell(
        "In [3] (cell 2)",
        "viz.list_available_params()",
        (
            "['x_dut_nfet_input_w',\n"
            " 'x_dut_nfet_input_l',\n"
            " 'x_dut_nfet_mirror_w',\n"
            " 'x_dut_nfet_mirror_l',\n"
            " 'x_dut_nfet_mirror_ref_w',\n"
            " 'x_dut_nfet_mirror_ref_l',\n"
            " 'x_dut_pfet_load_w',\n"
            " 'x_dut_pfet_load_l']",
        ),
    ),
    Cell(
        "In [4] (cell 3)",
        "viz.list_available_metrics()",
        ("['ugf', 'dcgain', 'pm', 'v(inoise_total)', 'tsettle']",),
    ),
    Cell(
        "In [5] (cell 4)",
        'viz.plot_design_space_exploration(param_x="x_dut_nfet_input_w",'
        ' param_y="x_dut_nfet_mirror_w", show=True)',
        (
            "(array([5.40205495e-06, 4.67323955e-06, 2.67720805e-06, ...,\n"
            "        3.52599165e-06, 6.75923967e-06, 5.38144072e-07], shape=(2000,)),\n"
            " array([7.89253219e-06, 2.09709038e-06, 9.72380874e-06, ...,\n"
            "        5.39345659e-06, 3.85326729e-06, 6.76527834e-07], shape=(2000,)))",
        ),
        ("fig-1",),
    ),
    Cell(
        "In [6] (cell 5)",
        'viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True)\n'
        'viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True,'
        " log_x=True, log_y=False)\n"
        'viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True,'
        " log_x=False, log_y=True)\n"
        'viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True,'
        " log_x=True, log_y=True)",
        (
            "(array([49598520., 24681150., 44901200., ..., 48550200., 31640920.,\n"
            "         5716487.], shape=(2000,)),\n"
            " array([28.14692, 31.92036, 30.18431, ..., 27.77705, 29.63118, 33.69205],\n"
            "       shape=(2000,)))",
        ),
        ("fig-2", "fig-3", "fig-4", "fig-5"),
    ),
    Cell(
        "In [7] (cell 6)",
        'viz.plot_optimization_trace(metric_x="v(inoise_total)", metric_y="dcgain", show=True,'
        " log_x=True, log_y=False)",
        (
            "(array([0.00047568, 0.00080318, 0.0006804 , ..., 0.00069399, 0.00092998,\n"
            "        0.00299395], shape=(2000,)),\n"
            " array([28.14692, 31.92036, 30.18431, ..., 27.77705, 29.63118, 33.69205],\n"
            "       shape=(2000,)))",
        ),
        ("fig-6",),
    ),
    Cell(
        "In [8] (cell 7)",
        'viz.plot_optimization_trace(metric_x="tsettle", metric_y="dcgain", show=True,'
        " log_x=True, log_y=False)",
        (
            "(array([1.10489e-07, 1.47553e-07, 1.13928e-07, ..., 1.13048e-07,\n"
            "        1.66511e-07, 2.94464e-07], shape=(2000,)),\n"
            " array([28.14692, 31.92036, 30.18431, ..., 27.77705, 29.63118, 33.69205],\n"
            "       shape=(2000,)))",
        ),
        ("fig-7",),
    ),
)


def load_trials(path: Path = DATA_FILE) -> dict[str, list[float]]:
    """Read the recorded trials as one list per column; an empty CSV field becomes NaN."""
    columns: dict[str, list[float]] = {name: [] for name in COLUMNS}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            for name in COLUMNS:
                field = row[name]
                columns[name].append(float(field) if field else math.nan)
    return columns


def build_figure(spec: FigureSpec, trials: dict[str, list[float]]) -> go.Figure:
    """Rebuild one recorded scatter, coloured by the optimizer score of each trial."""
    trace_name = spec.title.split(":")[0]
    figure = go.Figure(
        go.Scatter(
            x=trials[spec.x],
            y=trials[spec.y],
            mode="markers",
            name=trace_name,
            marker={
                "color": trials["score"],
                "colorscale": "Viridis",
                "colorbar": {"title": {"text": spec.colorbar}},
                "showscale": True,
                "size": 10,
            },
        )
    )
    figure.update_layout(
        title={"text": spec.title},
        showlegend=False,
        xaxis={"title": {"text": spec.x}, "type": "log" if spec.log_x else "linear"},
        yaxis={"title": {"text": spec.y}, "type": "log" if spec.log_y else "linear"},
    )
    return figure


def build_figures(trials: dict[str, list[float]]) -> dict[str, go.Figure]:
    """Rebuild all seven recorded figures, keyed ``fig-1`` … ``fig-7`` as on the old page."""
    return {spec.key: build_figure(spec, trials) for spec in FIGURES}


def print_record(trials: dict[str, list[float]]) -> None:
    """Print each recorded cell: its code, its text outputs, and a line per figure it drew."""
    specs = {spec.key: spec for spec in FIGURES}
    for cell in CELLS:
        print(f"=== {cell.prompt}")
        print(cell.code)
        for key in cell.figures:
            spec = specs[key]
            print(
                f"--- figure {key}: {spec.title}"
                f" (x {'log' if spec.log_x else 'linear'}, y {'log' if spec.log_y else 'linear'},"
                f" {len(trials[spec.x])} points)"
            )
        for text in cell.outputs:
            print("--- output")
            print(text.rstrip("\n"))
        print()


def main(argv: list[str] | None = None) -> None:
    """Print the recorded outputs and rebuild the figures; write or show them on request."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("--out", type=Path, help="write each figure as Plotly JSON into DIR")
    parser.add_argument("--show", action="store_true", help="open each figure (needs a browser)")
    args = parser.parse_args(argv)

    trials = load_trials()
    figures = build_figures(trials)
    print_record(trials)
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        for key, figure in figures.items():
            figure.write_json(args.out / f"{key}.json")
        print(f"wrote {len(figures)} figures to {args.out}")
    if args.show:
        for figure in figures.values():
            figure.show()


if __name__ == "__main__":
    main()
