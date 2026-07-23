import ast
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dacite import Config, from_dict
from spicexplorer.core.domains import OptimizationLog, OptimizationLogEntry
from spicexplorer.optimization.base import CHECKPOINT_SCHEMA_VERSION, Spice_Constraint_Satisfaction
from spicexplorer_core.atomic_io import atomic_write_json

logger = logging.getLogger("spicexplorer.viz.plotting")

# ----------------------------
# --- Global Constants ---
# ----------------------------





# ----------------------------
# --- Class Definitions ---
# ----------------------------

class Optimization_Log_Visualizer:

    def __init__(self, optimization_log: OptimizationLog):
        self.optimization_log = optimization_log

    # ------------------------------------------------------------
    # Load/Save Method
    # ------------------------------------------------------------
    @classmethod
    def load_checkpoint(cls, path_to_checkpoint: str | Path, **kwargs) -> "Optimization_Log_Visualizer":
        """Load optimizer and project setup from JSON checkpoint with version validation."""
        path = Path(path_to_checkpoint)
        with open(path, "r") as f:
            data = json.load(f)

        # Validate schema version
        version = data.get("schema_version")
        if version != CHECKPOINT_SCHEMA_VERSION:
            logger.warning(f"⚠️ Checkpoint version mismatch: {version} != {CHECKPOINT_SCHEMA_VERSION}")


        raw_log_data = data.get("optimization_log", [])
        if not isinstance(raw_log_data, list):
            logger.warning("optimization_log is not a list; treating as empty")
            raw_log_data = []

        # ``log_file`` may have been serialized as the repr of a dict containing
        # ``PosixPath(...)`` wrappers. It is per-trial ngspice log paths only — never used
        # for analysis/plotting (it is popped before plotting below and ignored by the web
        # readers). Earlier code ran ``eval()`` on it, which is a remote-code-execution sink
        # for any untrusted checkpoint (checkpoints live under the writable WORK_ROOT bind
        # mount). Parse it WITHOUT executing code: ``ast.literal_eval`` accepts plain dict
        # literals and rejects calls like ``PosixPath(...)``; anything it can't parse safely
        # is dropped to ``None`` (the field is Optional and unused downstream).
        for entry in raw_log_data:
            if isinstance(entry, dict) and isinstance(entry.get("log_file"), str):
                try:
                    entry["log_file"] = ast.literal_eval(entry["log_file"])
                except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
                    logger.debug("Dropping unparseable log_file entry to None")
                    entry["log_file"] = None

        # Rebuild optimization log
        optimization_log = OptimizationLog([
            from_dict(OptimizationLogEntry, entry, Config(strict=False))
            for entry in raw_log_data
        ])

        # Recreate optimizer instance
        obj = cls(optimization_log=optimization_log, **kwargs)

        logger.info(f"✅ Checkpoint loaded successfully from {path}")
        return obj

    def save_checkpoint(self, path_to_checkpoint: str | Path) -> None:
        """
        Save the current optimization log to a JSON checkpoint.

        Handles serialization of PosixPath (to string) and Numpy types (to float/list).
        """
        path = Path(path_to_checkpoint)

        # 1. Convert internal log entries to list of dictionaries
        serializable_log = [asdict(entry) for entry in self.optimization_log]

        # 2. Construct the data wrapper
        data = {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "optimization_log": serializable_log
        }

        # 3. Define a custom encoder for Path and Numpy objects
        class SpiceXplorerEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Path):
                    return str(o)
                if isinstance(o, (np.integer, np.floating)):
                    return float(o)
                if isinstance(o, np.ndarray):
                    return o.tolist()
                return super().default(o)

        # 4. Save to file. Atomic (temp-in-same-dir → fsync → os.replace) so a
        #    process killed mid-dump can't leave a truncated checkpoint that the
        #    next load_checkpoint would choke on.
        try:
            atomic_write_json(path, data, indent=2, cls=SpiceXplorerEncoder)
            logger.info(f"💾 Checkpoint saved successfully to {path}")

        except Exception as e:
            logger.error(f"❌ Failed to save checkpoint: {e}")
            raise e

    # ------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------
    def is_empty(self) -> bool:
        if len(self.optimization_log) < 1:
            logger.warning("No optimization trace to plot")
            return True
        return False

    def has_param(self, param_name: str) -> bool:
        if not self.optimization_log.has_param(param_name=param_name):
            logger.warning(f"param '{param_name}' not found in optimization trace")
            return False
        return True

    def list_available_metrics(self) -> List[str]:
        return self.optimization_log.list_available_metrics()

    def list_available_params(self) -> List[str]:
        return self.optimization_log.list_available_params()

    def filter_top_n(self, n: int) -> None:
        """
        Filters the internal optimization log to keep only the top N entries
        based on the highest scores.

        WARNING: This permanently modifies the data stored in this Visualizer instance.
        """

        if self.is_empty():
            return

        # 1. Sort the internal log list by score (Descending: Best -> Worst)
        #    We access the underlying list via self.optimization_log.log
        sorted_entries = sorted(
            self.optimization_log.log,
            key=lambda entry: entry.get_score(),
            reverse=True
        )

        # 2. Slice the list to keep only the top n
        self.optimization_log.log = sorted_entries[:n]

        logger.info(f"✂️ Filtered optimization log: keeping top {len(self.optimization_log.log)} entries.")

    # ------------------------------------------------------------
    # Re-computing Loss
    # ------------------------------------------------------------
    def recompute_loss_from_optimization_config(self, optimizer: Spice_Constraint_Satisfaction) -> None:
        for i, entry in enumerate(self.optimization_log):
            performance_array  = entry.get_performance_params()
            total_score, fit_summary = optimizer.compute_fitness(performance_array=performance_array)
            self.optimization_log.update_entry_fit_summary(index=i, fit_summary=fit_summary)

    # ------------------------------------------------------------
    # Plotting Methods
    # ------------------------------------------------------------
    def plot_design_space_exploration(
        self,
        param_x: str,
        param_y: str,
        save_path: Path | None = None,
        show: bool = False,
        log_x: bool = False,
        log_y: bool = False
    ) -> Tuple[np.ndarray, np.ndarray] | None:

        if self.is_empty():
            logger.warning("optimizatio log is empty")
            return None

        if not self.has_param(param_x) or not self.has_param(param_y):
            logger.warning(f"param_x {param_x} or param_y {param_y} not found in optimization log")
            return None

        x_values = np.array(
            [entry.get_param_val(param_x) for entry in self.optimization_log],
            dtype=float
        )
        y_values = np.array(
            [entry.get_param_val(param_y) for entry in self.optimization_log],
            dtype=float
        )
        loss = np.array(
            [entry.get_score() for entry in self.optimization_log],
            dtype=float
        )

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode="markers",
            marker=dict(
                size=10,
                color=loss,
                colorscale="Viridis",
                colorbar=dict(title="Score"),
                showscale=True
            ),
            name="Design Space Exploration"
        ))

        fig.update_layout(
            title=f"Design Space Exploration: {param_y} vs. {param_x}",
            xaxis_title=param_x,
            yaxis_title=param_y,
            template="plotly_dark",
            showlegend=False
        )

        fig.update_xaxes(type="log" if log_x else "linear")
        fig.update_yaxes(type="log" if log_y else "linear")

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Plot saved to {save_path}")

        if show:
            fig.show()

        return x_values, y_values

    def plot_optimization_trace(
        self,
        metric_x: str,
        metric_y: str,
        save_path: Path | None = None,
        show: bool = False,
        log_x: bool = False,
        log_y: bool = False
    ) -> Tuple[np.ndarray, np.ndarray] | None:

        if self.is_empty():
            return None

        fit_summary = self.optimization_log[0].get_fit_summary()

        if metric_x not in fit_summary:
            logger.warning(f"metric_x '{metric_x}' not found in optimization log")
            return None

        if metric_y not in fit_summary:
            logger.warning(f"metric_y '{metric_y}' not found in optimization log")
            return None

        # Membership was checked only against entry[0]; a resumed/mixed log can
        # drop the key from later entries (a corner absent post-resume), so index
        # defensively — a missing cell becomes NaN (a plotted gap), not a KeyError.
        x_values = np.array(
            [entry.get_fit_summary().get(metric_x, {}).get("curr_val", np.nan)
             for entry in self.optimization_log],
            dtype=float
        )
        y_values = np.array(
            [entry.get_fit_summary().get(metric_y, {}).get("curr_val", np.nan)
             for entry in self.optimization_log],
            dtype=float
        )
        fom = np.array(
            [entry.get_score() for entry in self.optimization_log],
            dtype=float
        )

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode="markers",
            marker=dict(
                size=10,
                color=fom,
                colorscale="Viridis",
                colorbar=dict(title="FOM"),
                showscale=True
            ),
            name="Optimization Trace"
        ))

        fig.update_layout(
            title=f"Optimization Trace: {metric_y} vs. {metric_x}",
            xaxis_title=metric_x,
            yaxis_title=metric_y,
            template="plotly_dark",
            showlegend=False
        )

        fig.update_xaxes(type="log" if log_x else "linear")
        fig.update_yaxes(type="log" if log_y else "linear")

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Plot saved to {save_path}")

        if show:
            fig.show()

        return x_values, y_values

    def plot_loss_breakdown(
        self,
        save_path: Path | None = None,
        show: bool = False,
        log_y: bool = False
    ) -> go.Figure | None:
        """
        Plots the Total Score, Best Score So Far, and individual metric contributions.
        """

        if self.is_empty():
            return None

        # --- 1. Extract Data ---
        iterations = np.arange(len(self.optimization_log))

        # Current Score per iteration
        total_scores = np.array(
            [entry.get_score() for entry in self.optimization_log],
            dtype=float
        )

        # Best Score So Far (Cumulative Maximum)
        # We use maximum because you specified "most positive" is best.
        best_so_far = np.maximum.accumulate(total_scores)

        # Get metric keys for breakdown
        first_summary = self.optimization_log[0].get_fit_summary()
        metric_keys = list(first_summary.keys())

        # --- 2. Create Plotly Figure ---
        fig = go.Figure()

        # TRACE: Best Score So Far (Green Dashed Line)
        fig.add_trace(go.Scatter(
            x=iterations,
            y=best_so_far,
            mode='lines',
            name='<b>BEST SO FAR</b>',
            line=dict(width=3, color='#00FF00', dash='dash'), # Green, Dashed
            hovertemplate="Iter: %{x}<br>Best: %{y:.4f}<extra></extra>"
        ))

        # TRACE: Current Total Score (Solid White Line)
        fig.add_trace(go.Scatter(
            x=iterations,
            y=total_scores,
            mode='lines+markers',
            name='Current Score',
            line=dict(width=2, color='white'),
            marker=dict(size=5, opacity=0.8),
            hovertemplate="Iter: %{x}<br>Curr: %{y:.4f}<extra></extra>"
        ))

        # TRACES: Individual Metrics (Thinner, colored lines)
        for metric in metric_keys:
            metric_scores = []
            for entry in self.optimization_log:
                summary = entry.get_fit_summary()
                # Use .get() twice to be safe against missing keys
                val = summary.get(metric, {}).get("score", np.nan)
                metric_scores.append(val)

            fig.add_trace(go.Scatter(
                x=iterations,
                y=metric_scores,
                mode='lines',
                name=f"{metric}",
                opacity=0.5, # Transparent to keep main lines dominant
                line=dict(width=1),
                hovertemplate=f"Iter: %{{x}}<br>{metric}: %{{y:.4f}}<extra></extra>"
            ))

        # --- 3. Styling ---
        fig.update_layout(
            title="<b>Optimization Progress</b>: Best vs. Current vs. Components",
            xaxis_title="Iteration",
            yaxis_title="Score (Higher is Better)",
            template="plotly_dark",
            hovermode="x unified", # Shows all traces for an iteration on hover
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.5)"
            )
        )

        if log_y:
            fig.update_yaxes(type="log")

        # --- 4. Save/Show ---
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Loss breakdown plot saved to {save_path}")

        if show:
            fig.show()

        return fig

    def plot_best_score_evolution(
        self,
        save_path: Path | None = None,
        show: bool = False,
        log_y: bool = False
    ) -> go.Figure | None:
        """
        Plots the 'Best Score So Far' (Cumulative Maximum) for the Total Score
        and for each individual metric independently.
        """

        if self.is_empty():
            return None

        # --- 1. Extract and Process Data ---
        iterations = np.arange(len(self.optimization_log))

        # A. Total Score Best So Far
        total_scores = np.array(
            [entry.get_score() for entry in self.optimization_log],
            dtype=float
        )
        # Calculate cumulative maximum (best seen up to index i)
        total_best_so_far = np.maximum.accumulate(total_scores)

        # B. Get Metrics
        first_summary = self.optimization_log[0].get_fit_summary()
        metric_keys = list(first_summary.keys())

        # --- 2. Create Plotly Figure ---
        fig = go.Figure()

        # TRACE: Total Score Best (Thick, White)
        fig.add_trace(go.Scatter(
            x=iterations,
            y=total_best_so_far,
            mode='lines',
            name='<b>TOTAL BEST</b>',
            line=dict(width=4, color='white'),
            hovertemplate="Iter: %{x}<br>Total Best: %{y:.4f}<extra></extra>"
        ))

        # TRACES: Individual Metrics Best So Far
        for metric in metric_keys:
            metric_scores = []
            for entry in self.optimization_log:
                summary = entry.get_fit_summary()
                # Default to -inf if missing so it doesn't affect max calculation
                val = summary.get(metric, {}).get("score", -np.inf)
                metric_scores.append(val)

            metric_scores = np.array(metric_scores, dtype=float)

            # Calculate cumulative max for this specific metric
            # We use fmax to ignore NaNs if they sneak in, though we defaulted to -inf
            metric_best_so_far = np.maximum.accumulate(metric_scores)

            fig.add_trace(go.Scatter(
                x=iterations,
                y=metric_best_so_far,
                mode='lines',
                name=f"{metric} (Best)",
                opacity=0.8,
                line=dict(width=2), # Slightly thinner than total
                hovertemplate=f"Iter: %{{x}}<br>{metric} Best: %{{y:.4f}}<extra></extra>"
            ))

        # --- 3. Styling ---
        fig.update_layout(
            title="<b>Evolution of Best Scores</b>: Independent Cumulative Maximums",
            xaxis_title="Iteration",
            yaxis_title="Best Score Achieved (Higher is Better)",
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.5)"
            )
        )

        if log_y:
            fig.update_yaxes(type="log")

        # --- 4. Save/Show ---
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Best score evolution plot saved to {save_path}")

        if show:
            fig.show()

        return fig

    # ------------------------------------------------------------
    # Exporting Methods
    # ------------------------------------------------------------
    def extract_best_score_evolution(
        self,
        include_metrics: bool = True,
        running_avg_n: int | None = None
    ) -> pd.DataFrame:
        """
        Returns a DataFrame tracking the 'Best Score So Far' (Cumulative Maximum)
        for the total score and optionally for each individual metric.

        Args:
            include_metrics: If True, includes columns for individual metric scores.
            running_avg_n: If set to an integer > 1, adds columns for the
                           n-point moving average of the scores.
        """
        if self.is_empty():
            logger.warning("Optimization log is empty... returning empty dataframe.")
            return pd.DataFrame()

        # 1. Total Score Data
        total_scores = np.array(
            [entry.get_score() for entry in self.optimization_log],
            dtype=float
        )
        # Calculate cumulative maximum
        best_total = np.maximum.accumulate(total_scores)

        data = {
            "iteration": np.arange(len(self.optimization_log)),
            "score_current": total_scores,         # Raw score (useful for reference)
            "score_best_so_far": best_total        # Cumulative Max
        }

        # 2. Calculate Total Score Running Average (if requested)
        if running_avg_n is not None and running_avg_n > 1:
            # We use pandas Series for easy rolling window calculation
            data[f"score_moving_avg_{running_avg_n}"] = (
                pd.Series(total_scores).rolling(window=running_avg_n, min_periods=1).mean()
            )

        # 3. Individual Metrics (Optional)
        if include_metrics:
            # We assume the first entry has all metric keys
            first_summary = self.optimization_log[0].get_fit_summary()
            metric_keys = list(first_summary.keys())

            for metric in metric_keys:
                metric_scores = []
                for entry in self.optimization_log:
                    summary = entry.get_fit_summary()
                    # Default to NaN so it doesn't skew averages (or -inf for max)
                    val = summary.get(metric, {}).get("score", np.nan)
                    metric_scores.append(val)

                metric_scores = np.array(metric_scores, dtype=float)

                # A. Metric Best So Far (ignoring NaNs for max calculation)
                # We replace NaN with -inf just for the accumulate step, then revert if needed
                temp_scores_for_max = np.nan_to_num(metric_scores, nan=-np.inf)
                data[f"{metric}_best_so_far"] = np.maximum.accumulate(temp_scores_for_max)

                # B. Metric Running Average (if requested)
                if running_avg_n is not None and running_avg_n > 1:
                    data[f"{metric}_moving_avg_{running_avg_n}"] = (
                        pd.Series(metric_scores).rolling(window=running_avg_n, min_periods=1).mean()
                    )

        # 4. Create DataFrame
        df = pd.DataFrame(data)
        df.set_index("iteration", inplace=True)

        return df

    def to_df(self, top_n: int | None = None) -> pd.DataFrame:
        if self.is_empty():
            return pd.DataFrame()

        # 1. Sort the log entries by score (descending) if top_n is requested
        log_entries = self.optimization_log.log
        if top_n is not None:
            # Sort in-place for temporary list, or create new list
            sorted_entries = sorted(
                log_entries,
                key=lambda x: x.get_score(),
                reverse=True
            )
            log_entries = sorted_entries[:top_n]

        # 2. Convert filtered/sorted entries to dicts
        data = []
        for entry in log_entries:
            entry_dict = asdict(entry)
            entry_dict.pop("log_file", None)  # Remove log_file key
            data.append(entry_dict)

        # 3. Flatten
        return pd.json_normalize(data)

    def to_csv(self, path: Path | str, index: bool = False, top_n: int | None = None) -> None:
        """
        Export the log to a CSV file.

        Args:
            path: File path to save the CSV.
            index: Whether to write row names (index).
            top_n: If provided, writes only the top N entries sorted by score.
        """
        df = self.to_df(top_n=top_n)

        # Ensure parent directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(path, index=index)
