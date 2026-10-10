"""Recorded outputs of the 5,000-trial LHSSearch run of ``explore_nevergrad_single_obj.py``.

This script replaces ``explore_nevergrad_single_obj.recorded-outputs.html``, the static HTML
record of that run, and holds the same results as text and data instead of HTML.

What it records: the saved outputs of
``examples/OTA/folded_cascode/ihp-sg13g2/sizing/test_nevergrad_single_obj.ipynb`` at
``d85614c`` (the notebook is now the marimo notebook ``explore_nevergrad_single_obj.py`` beside
this file). The run was a one-off Nevergrad LHSSearch of 5,000 trials (budget 5000, random
seed 48) on the folded-cascode OTA in IHP SG13G2, simulated with ngspice on 2026-02-02:
optimization from 00:05:48 to 01:14:23 (1 h 08 min 35 s by the progress bar), checkpoint
``LHSSearch_5000_2026-02-02_08-45-53.json`` saved at 08:45:54. Only the AC testbench
(``tb_ac``) was enabled; the targets were ``ugf``, ``dcgain`` and ``pm``.

These outputs cannot be reproduced by re-running the notebook: ``project_setup.yaml`` in this
folder has changed since and now names SamplingSearch with a budget of 5 trials. Home and
scratch paths read ``/home/<user>/`` and ``/scratch/<user>/``, as in the HTML record.

Data: the per-trial table, the source of every figure, is
``explore_nevergrad_single_obj.recorded-outputs.csv`` beside this file, one row per trial
(0-based, as the notebook's "New fit ... trial N" lines count them) with the trial score, the
measured ``ugf`` [Hz], ``dcgain`` [dB] and ``pm`` [deg], their per-spec scores and the 16 design
parameters. Widths and lengths are in micrometres (``*_um``), the bias current in microamperes
(``x_dut_IB_uA``) and ``x_dut_Vb1`` in volts. An empty cell is a measurement the simulation did
not produce (NaN in the run: 2,206 of the 5,000 trials have no ``ugf``/``pm``).

Run ``python explore_nevergrad_single_obj_recorded_outputs.py`` to print the recorded text
outputs and tables and to rebuild the three Plotly figures; ``--show`` opens the figures and
``--out-dir DIR`` writes them to DIR (PNG when ``kaleido`` is installed, Plotly JSON otherwise).
No figure is written by default.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections.abc import Sequence
from pathlib import Path

import plotly.graph_objects as go

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "explore_nevergrad_single_obj.recorded-outputs.csv"

METRICS = ("ugf", "dcgain", "pm")
PARAMETERS = (
    "x_dut_W_1",
    "x_dut_L_1",
    "x_dut_W_2",
    "x_dut_L_2",
    "x_dut_W_3",
    "x_dut_L_3",
    "x_dut_W_4",
    "x_dut_L_4",
    "x_dut_W_5",
    "x_dut_L_5",
    "x_dut_W_6",
    "x_dut_L_6",
    "x_dut_W_7",
    "x_dut_L_7",
    "x_dut_Vb1",
    "x_dut_IB",
)

# Each trial's log file, kept as this pattern instead of 5,000 paths (all 5,000 matched it).
LOG_FILE_PATTERN = (
    "/home/<user>/code/TCAD/modules/SpiceXplorer/examples/OTA/folded_cascode/ihp-sg13g2/"
    "spice/spice_out/run_{n}_tb_ac/cora_testbench_ac_{n}.log  (n = trial + 1)"
)

# The notebook's text outputs before the optimization, verbatim: (prompt, code, output).
RECORDED_CELLS: tuple[tuple[str, str, str], ...] = (
    (
        "In [1] (cell 0)",
        (
            "from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum\n"
            "from spicexplorer_core.logging.logger_setup import setup_loggers, setup_loggers_with_spicelib_suppression\n"
            "\n"
            "from pathlib import Path\n"
            "\n"
            "logger = setup_loggers_with_spicelib_suppression()\n"
            "# logger = setup_loggers()"
        ),
        (
            "00:05:48 - spicexplorer: [INFO] 🚀 Logger initialized!\n"
            "00:05:48 - spicexplorer: [INFO] 📄 Log file: /home/<user>/code/TCAD/modules/SpiceXplorer/examples/OTA/folded_cascode/ihp-sg13g2/sizing/logs/SpiceXplorer_2026-02-02_00-05-48.log\n"
            "00:05:48 - spicexplorer: [INFO] 👀 TQDM and Errors will still show in console (stderr).\n"
            "00:05:48 - spicexplorer: [INFO] 🔇 Standard outputs and SPICE logs are redirected to file (stdout).\n"
        ),
    ),
    (
        "In [3] (cell 7)",
        (
            "orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(\n"
            "    project_setup_path=path_to_project_setup,\n"
            "    optimizer_type=optimizer_type,\n"
            "    verbose=True\n"
            ")"
        ),
        (
            "00:05:48 - spicexplorer.designer_tools.domains: [INFO] Initialized OptimizerConfig: LHSSearch, type=nevergrad, budget=5000, random_seed=48\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [WARNING] No lin_variable_bounds provided; using default [0.0, 1.0].\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [WARNING] No log_variable_bounds provided; using default [0.0, 1.0].\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [WARNING] No loss_function_config provided; using default values.\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [INFO] Project 'FOLDED-CASCODE-OTA' initialized with simulator 'ngspice'\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [INFO] \tWorkspace root: /home/<user>/code/TCAD/modules/SpiceXplorer/examples/OTA/folded_cascode/ihp-sg13g2\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [INFO] \tNetlist path: spice/cora_testbench.spice\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [INFO] \tOutput directory: spice/spice_out\n"
            "00:05:48 - spicexplorer.designer_tools.domains: [INFO] ✅ Project setup successfully created\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] =============================================================================\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] project: FOLDED-CASCODE-OTA has (4) testbenches.\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] 📂 Creating output directory for the first time: /home/<user>/code/TCAD/modules/SpiceXplorer/examples/OTA/folded_cascode/ihp-sg13g2/spice/spice_out\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] --------------------------------------------------\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] 🚀 Spicelib_Wrapper initialized successfully!\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] \t📝 Testbench: tb_ac\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] \t📜 Schematic: cora_testbench_ac\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] \t📂 Output Folder: /home/<user>/code/TCAD/modules/SpiceXplorer/examples/OTA/folded_cascode/ihp-sg13g2/spice/spice_out\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] --------------------------------------------------\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] Using ngspice from ['ngspice']\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] 📊 --- Circuit Information ---\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] 🔗 Nodes in the netlist: ['vdd', 'GND', 'out', 'vin+', 'vin-', 'ib']\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] Testbench parameters: [('CL', '5p'), ('TEMP', '27'), ('VCM', '900m'), ('VDD', '1.8')]\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] DUT parameters: [('X_DUT_IB', '34u'), ('X_DUT_L_1', '2u'), ('X_DUT_L_2', '2u'), ('X_DUT_L_3', '2.5u'), ('X_DUT_L_4', '2u'), ('X_DUT_L_5', '4.5u'), ('X_DUT_L_6', '3u'), ('X_DUT_L_7', '3u'), ('X_DUT_NG_1', '8'), ('X_DUT_NG_2', '11'), ('X_DUT_NG_3', '5'), ('X_DUT_NG_4', '8'), ('X_DUT_NG_5', '19'), ('X_DUT_NG_6', '5'), ('X_DUT_NG_7', '5'), ('X_DUT_VB1', '1.225'), ('X_DUT_VB2', '1.275'), ('X_DUT_W_1', '72u'), ('X_DUT_W_2', '106.5u'), ('X_DUT_W_3', '44u'), ('X_DUT_W_4', '78u'), ('X_DUT_W_5', '183u'), ('X_DUT_W_6', '50u'), ('X_DUT_W_7', '50u')]\n"
            "00:05:48 - spicexplorer.spice_engine.spicelib: [INFO] ✅ --- Circuit info printed successfully --- 🎉 \n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] (2) Skipping disabled testbench: tb_noise - Noise analysis for input referred noise\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] (3) Skipping disabled testbench: tb_tran - Transient analysis for slew rate and settling time\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] (4) Skipping disabled testbench: tb_op - Operating point analysis\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] Created (1) spicelib_wrappers for project: FOLDED-CASCODE-OTA\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] =============================================================================\n"
        ),
    ),
    (
        "In [4] (cell 8)",
        ("optimizer = orchestrator.get_optimizer()"),
        (
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] creating the circuit_optimizer of type nevergrad_constraint\n"
            "00:05:48 - spicexplorer.optimization.base: [INFO] Initialized the Nevergrad_Spice_Multi_Spec_Optimizer with 3 target specs\n"
            "00:05:48 - spicexplorer.optimization.stochastic.nevergrad: [INFO] started the <class 'spicexplorer.optimization.stochastic.nevergrad.Nevergrad_Spice_Constraint_Satisfaction'> optimizer class\n"
            "00:05:48 - spicexplorer.optimization.orchestrator: [INFO] created the circuit_optimizer; type <class 'spicexplorer.optimization.stochastic.nevergrad.Nevergrad_Spice_Constraint_Satisfaction'>\n"
        ),
    ),
    (
        "In [6] (cell 10)",
        ("optimizer.parameterize()"),
        (
            "Dict(x_dut_IB=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_1=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_2=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_3=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_4=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_5=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_6=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_L_7=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_Vb1=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_1=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_2=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_3=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_4=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_5=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_6=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}],x_dut_W_7=Scalar{Cl(0,1,b)}[sigma=Scalar{exp=2.03}]):{'x_dut_W_1': 0.5, 'x_dut_L_1': 0.5, 'x_dut_W_2': 0.5, 'x_dut_L_2': 0.5, 'x_dut_W_3': 0.5, 'x_dut_L_3': 0.5, 'x_dut_W_4': 0.5, 'x_dut_L_4': 0.5, 'x_dut_W_5': 0.5, 'x_dut_L_5': 0.5, 'x_dut_W_6': 0.5, 'x_dut_L_6': 0.5, 'x_dut_W_7': 0.5, 'x_dut_L_7': 0.5, 'x_dut_Vb1': 0.5, 'x_dut_IB': 0.5}"
        ),
    ),
)
# The optimize() cell printed 4,427 outputs. Kept verbatim: every INFO line and the final
# progress bar. Collapsed: the ERROR lines, all instances of seven messages, to one count each.
OPTIMIZE_CODE = "optimizer.optimize()"
OPTIMIZE_INFO = (
    "00:05:48 - spicexplorer.optimization.base: [INFO] Optimization process started.",
    "00:05:48 - spicexplorer.optimization.stochastic.nevergrad: [INFO] Optimizer is set to"
    " LHSSearch with budget = 5000",
    "00:07:42 - spicexplorer.optimization.base: [INFO] a New fit was found... trial 110 score -100.00",
    "00:09:54 - spicexplorer.optimization.base: [INFO] a New fit was found... trial 289 score -100.00",
    "00:16:48 - spicexplorer.optimization.base: [INFO] a New fit was found... trial 882 score -79.58",
    "00:19:39 - spicexplorer.optimization.base: [INFO] a New fit was found... trial 1063 score -76.86",
    "01:05:26 - spicexplorer.optimization.base: [INFO] a New fit was found... trial 4373 score -54.69",
    "01:14:23 - spicexplorer.optimization.base: [INFO] Optimization process completed.",
)
OPTIMIZE_PROGRESS_FINAL = "Optimizing: 100%|██████████| 5000/5000 [1:08:35<00:00,  1.22trial/s]"
# (count, first seen, message) for every ERROR line of the optimize() cell.
OPTIMIZE_ERRORS = (
    (
        2175,
        "00:05:50",
        "spicexplorer.spice_engine.spicelib: [ERROR] ❌ Waveform 'ugf' not found in plot 'AC Analysis'.",
    ),
    (
        2206,
        "00:05:50",
        "spicexplorer.spice_engine.spicelib: [ERROR] ❌ Scalar Variable ugf not found in the raw file for plot AC Analysis",
    ),
    (
        2175,
        "00:05:50",
        "spicexplorer.spice_engine.spicelib: [ERROR] ❌ Waveform 'pm' not found in plot 'AC Analysis'.",
    ),
    (
        2206,
        "00:05:50",
        "spicexplorer.spice_engine.spicelib: [ERROR] ❌ Scalar Variable pm not found in the raw file for plot AC Analysis",
    ),
    (
        93,
        "00:07:35",
        "spicexplorer.spice_engine.spicelib: [ERROR] ❌ Plot type 'AC Analysis' not found in raw file.",
    ),
    (
        93,
        "00:07:35",
        "spicexplorer.spice_engine.spicelib: [ERROR] ℹ️ Available plots: ['constants']",
    ),
    (
        31,
        "00:07:35",
        "spicexplorer.spice_engine.spicelib: [ERROR] ❌ Scalar Variable dcgain not found in the raw file for plot AC Analysis",
    ),
)

PLOT_SCORE_CODE = "optimizer.plot_score(show=True)"
PLOT_TRACE_CODE = (
    'optimizer.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True,'
    ' save_path="./ugf_dcgain.html")\n'
    'optimizer.plot_optimization_trace(metric_x="ugf", metric_y="pm", show=True,'
    ' save_path="./ugf_pm.html")'
)
# The value the trace cell returned, verbatim (the ugf and pm columns of the last trace).
PLOT_TRACE_RESULT = (
    "(tensor([1359089., 4469581.,      nan,  ...,      nan, 4760460., 4680791.]),\n"
    " tensor([ 99., 107.,  nan,  ...,  nan, 122., 108.]))"
)

CHECKPOINT_CELL = (
    "In [11] (cell 15)",
    (
        'optimizer.save_checkpoint(name=f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}")'
    ),
    (
        "08:45:54 - spicexplorer.optimization.base: [INFO] ✅ Checkpoint saved to LHSSearch_5000_2026-02-02_08-45-53.json\n"
    ),
)


def _column_scale(name: str) -> tuple[str, float]:
    """Return the CSV column of design parameter ``name`` and its factor back to SI units."""
    if "_W_" in name or "_L_" in name:
        return f"{name}_um", 1e-6
    if name.endswith("_IB"):
        return f"{name}_uA", 1e-6
    return name, 1.0


def load_trials(path: Path = DATA_FILE) -> dict[str, list[float]]:
    """Load the per-trial table as columns in SI units; a missing value is ``nan``."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    def column(name: str, scale: float = 1.0) -> list[float]:
        return [float(row[name]) * scale if row[name] else math.nan for row in rows]

    trials: dict[str, list[float]] = {"trial": column("trial"), "score": column("score")}
    for metric in METRICS:
        trials[metric] = column(metric)
        trials[f"{metric}_score"] = column(f"{metric}_score")
    for name in PARAMETERS:
        trials[name] = column(*_column_scale(name))
    return trials


def best_so_far(scores: Sequence[float]) -> list[float]:
    """Return the running maximum of ``scores`` (the 'Best Score So Far' line)."""
    best, running = [], -math.inf
    for score in scores:
        running = max(running, score)
        best.append(running)
    return best


def new_fit_trials(scores: Sequence[float]) -> list[int]:
    """Return the trials that raised the best score, as the notebook's 'New fit' lines name them."""
    best = best_so_far(scores)
    return [i for i in range(1, len(best)) if best[i] > best[i - 1]]


def _print_cell(prompt: str, code: str, output: str) -> None:
    print(f"--- {prompt} ---")
    print("\n".join(f">>> {line}" for line in code.splitlines()))
    print(output.rstrip("\n"))
    print()


def print_recorded_outputs(trials: dict[str, list[float]]) -> None:
    """Print the recorded text outputs and the tables derived from the per-trial data."""
    for prompt, code, output in RECORDED_CELLS:
        _print_cell(prompt, code, output)

    print("--- In [7] (cell 11) ---")
    print(f">>> {OPTIMIZE_CODE}")
    print("\n".join(OPTIMIZE_INFO))
    print(OPTIMIZE_PROGRESS_FINAL)
    print("ERROR lines, collapsed to one count per message:")
    for count, first_seen, message in OPTIMIZE_ERRORS:
        print(f"  {count:5d} x (first {first_seen})  {message}")
    print()

    scores = trials["score"]
    print("New fits (trials that raised the best score), from the per-trial table:")
    header = f"{'trial':>6} {'score':>12} {'ugf [Hz]':>12} {'dcgain [dB]':>12} {'pm [deg]':>9}"
    print(header)
    for i in new_fit_trials(scores):
        print(
            f"{i:6d} {scores[i]:12.6f} {trials['ugf'][i]:12.6g} "
            f"{trials['dcgain'][i]:12.6g} {trials['pm'][i]:9.4g}"
        )
    print()

    best = max(range(len(scores)), key=scores.__getitem__)
    print(f"Best trial {best} (score {scores[best]:.6f}):")
    for metric in METRICS:
        print(
            f"  {metric:<8} {trials[metric][best]:12.6g}   score {trials[f'{metric}_score'][best]:.6f}"
        )
    for name in PARAMETERS:
        print(f"  {name:<10} {trials[name][best]:.7g}")
    print(f"  log file: {LOG_FILE_PATTERN.format(n=best + 1)}")
    missing = sum(math.isnan(v) for v in trials["ugf"])
    print(f"Trials with no ugf/pm measurement: {missing} of {len(scores)}")
    print()

    print("--- In [8] (cell 13) ---")
    print(f">>> {PLOT_SCORE_CODE}")
    print("[figure 1: Score vs. Optimization Trial]")
    print()
    print("--- In [14] (cell 14) ---")
    print("\n".join(f">>> {line}" for line in PLOT_TRACE_CODE.splitlines()))
    print("[figure 2: Optimization Trace: dcgain vs. ugf]")
    print("[figure 3: Optimization Trace: pm vs. ugf]")
    print(PLOT_TRACE_RESULT)
    print()
    _print_cell(*CHECKPOINT_CELL)


def build_figures(trials: dict[str, list[float]]) -> dict[str, go.Figure]:
    """Rebuild the run's three Plotly figures from the per-trial table, keyed by file stem."""
    steps = list(range(len(trials["score"])))
    score = go.Figure(
        [
            go.Scatter(
                x=steps,
                y=trials["score"],
                mode="markers+lines",
                name="Score",
                opacity=0.6,
                line={"color": "blue", "width": 2},
            ),
            go.Scatter(
                x=steps,
                y=best_so_far(trials["score"]),
                mode="lines",
                name="Best Score So Far",
                line={"color": "red", "width": 2},
            ),
        ]
    )
    score.update_layout(
        template="plotly_dark",
        title="Score vs. Optimization Trial",
        xaxis_title="Optimization Step",
        yaxis_title="Score",
        showlegend=True,
    )
    figures = {"score": score}
    for metric in ("dcgain", "pm"):
        trace = go.Figure(
            go.Scatter(
                x=trials["ugf"],
                y=trials[metric],
                mode="markers",
                name="Optimization Trace",
                marker={
                    "size": 10,
                    "color": trials["score"],
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {"title": {"text": "FOM"}},
                },
            )
        )
        trace.update_layout(
            template="plotly_dark",
            title=f"Optimization Trace: {metric} vs. ugf",
            xaxis_title="ugf",
            yaxis_title=metric,
            showlegend=False,
        )
        figures[f"ugf_{metric}"] = trace
    return figures


def write_figures(figures: dict[str, go.Figure], out_dir: Path) -> list[Path]:
    """Write each figure to ``out_dir``: PNG when kaleido can render it, Plotly JSON otherwise."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for stem, figure in figures.items():
        png = out_dir / f"{stem}.png"
        try:
            figure.write_image(png)
            written.append(png)
        except (ImportError, ValueError, RuntimeError) as exc:
            json_path = out_dir / f"{stem}.json"
            figure.write_json(json_path)
            print(f"PNG export unavailable ({type(exc).__name__}); wrote {json_path.name}")
            written.append(json_path)
    return written


def main(argv: Sequence[str] | None = None) -> None:
    """Print the recorded outputs and rebuild the figures; optionally show or write them."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("--show", action="store_true", help="open the figures in a browser")
    parser.add_argument("--out-dir", type=Path, help="write the figures to this directory")
    args = parser.parse_args(argv)

    trials = load_trials()
    print_recorded_outputs(trials)
    figures = build_figures(trials)
    print(f"Built {len(figures)} figures: {', '.join(figures)}")
    if args.out_dir is not None:
        for path in write_figures(figures, args.out_dir):
            print(f"wrote {path}")
    if args.show:
        for figure in figures.values():
            figure.show()


if __name__ == "__main__":
    main()
