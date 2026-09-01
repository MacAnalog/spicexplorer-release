"""This Module includes base """
from __future__ import annotations

import ast
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple, cast

import numpy as np

# torch / sympy are OPTIONAL — only the Bode optimizer (Spice_Bode_Optimizer) and plotting
# helpers below use them at runtime. The common constraint/single-objective path is pure
# numpy, so this module must import without torch. `from __future__ import annotations`
# above keeps the `torch.Tensor` / `Expr` annotations lazy (never evaluated at import).
# Install the Bode/RL features with:  pip install 'spicexplorer[torch]'.
#
# TYPE_CHECKING branch = what a static checker sees (the real module, so `torch.Tensor`
# is a usable annotation and `torch.*` is a call on a module); the `= None` fallback is
# the RUNTIME "extra not installed" sentinel. Typing it as `Module | None` reported every
# annotation and call in this file as reportInvalidTypeForm / reportOptionalMemberAccess —
# noise about the import guard, not about the code. Runtime behaviour is unchanged.
if TYPE_CHECKING:
    import torch
else:
    try:
        import torch
    except ModuleNotFoundError:
        torch = None
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
from dacite import Config, from_dict
from tqdm import tqdm

if TYPE_CHECKING:
    from sympy import Expr
else:
    try:
        from sympy import Expr
    except ModuleNotFoundError:
        Expr = None  # annotation-only (lazy via __future__ annotations); Bode path needs sympy
from time import monotonic

from spicexplorer.core.domains import (
    ListTargetSpec,
    OptimizationGoalType,
    OptimizationLog,
    OptimizationLogEntry,
    OptimizationPoint,
    Project_Setup,
    TargetSpec,
)
from spicexplorer.core.utils import (
    DEFAULT_MARGIN_REWARD_CLIP,
    DEFAULT_MARGIN_REWARD_WEIGHT,
    DEFAULT_TIE_BREAKER_WEIGHT,
    DEFAULT_UNMEASURED_POLICY,
    EPSILON,
    PER_SPEC_CORNER_AGGREGATION,
    Frequency_Weight,
    Transfer_Func_Helper,
    aggregate_corner_scores,
    aggregate_corner_spec_margins,
    aggregate_corner_spec_scores,
    aggregate_spec_scores,
    compute_error,
    compute_reward,
    get_bode_fitness_loss,
    is_scoreable_metric,
    linear_denormalize,
    log_denormalize,
    normalized_spec_margin,
    plot_complex_response,
)

# The decade-space transforms for `log_scale` specs live in core/utils so the API Score-Shaping
# preview shares ONE implementation with this scorer (SC-4). Aliased to the historical private names
# so every call site (and any `from …base import _log_space_band` importer) is unchanged.
from spicexplorer.core.utils import log_space_band as _log_space_band
from spicexplorer.core.utils import log_space_range_coeff as _log_space_range_coeff
from spicexplorer.optimization.sim_benchmark import wait_for_handles_timed
from spicexplorer.optimization.trial_timing import (
    DEFAULT_TRIAL_TIME_REPORT_EVERY,
    TrialTimeMonitor,
)
from spicexplorer_core.atomic_io import atomic_write_json

# Symxplorer Specific Imports
from spicexplorer_core.spice_engine import SimHandle, SimResult, Simulator
from spicexplorer_core.spice_engine.spicelib import Ngspice_Plot_Type, NGSpice_Wrapper

logger = logging.getLogger("spicexplorer.optimization.base")

# Preserve the original global torch config when torch is available (no-op without it).
if torch is not None:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dtype  = torch.double
    torch.set_default_dtype(dtype)
    torch.set_default_device(device)
    logger.info(f'Using device: {device} and dtype: {dtype}')
else:
    device = None
    dtype  = None

# ----------------------------
# --- Global Constants ---
# ----------------------------
MAX_PENALTY = np.float64(1e6) # The maximum score used when a trial does not have a performance metric in it.
MAX_REWARD  = np.float64(1e6) # The maximum reward score a spec can achieve.
CHECKPOINT_SCHEMA_VERSION = "1.0.0"
# EPSILON is re-exported from core.utils (imported above) rather than redefined here: the spec-axis
# aggregators need the same feasibility threshold the scorer uses, and two literals would be free to
# drift apart. The name stays module-level so existing `from ...base import EPSILON` still resolves.

# Both parallel-sim wait loops used to poll ``is_done()`` forever with no timeout, so a
# hung/stuck ngspice child (or a bare-container submit() that never completes — observed during the
# Ax revival) stalled the WHOLE run. A bounded wait caps how long one trial waits for its outstanding
# sims; any that miss the deadline are scored as failures (NaN → MAX_PENALTY) so the TRIAL fails and
# the run keeps going. Generous by default (a legit multi-corner batch is seconds–minutes) and
# override­able for slow/loaded hosts; <= 0 restores the legacy wait-forever behavior.
_SIM_WAIT_TIMEOUT_S: float = float(os.environ.get("SPICEXPLORER_SIM_WAIT_TIMEOUT_S", "600"))


class _FailedSimResult:
    """A ``SimResult`` stand-in for a submitted sim that never completed (timed out / hung).

    Every scalar reads NaN, so the scorer applies ``MAX_PENALTY`` for that testbench exactly as it
    does for a sim that ran but wrote no RAW — the trial fails, the run continues. Waves raise
    (the protocol's "a wave is a hard request" contract); the constraint / single-objective scorer
    only reads scalars, so a timed-out corner still scores cleanly."""

    def scalar(self, name: str, analysis: str) -> float:  # noqa: D401 - protocol method
        return float("nan")

    def wave(self, name: str, analysis: str) -> np.ndarray:  # noqa: D401 - protocol method
        raise KeyError(f"no waveform '{name}' for analysis '{analysis}': sim did not complete")


# ----------------------------
# --- Class Definitions ---
# ----------------------------

# ------------------------------------------------
# [ABSTRACT] Optimizer Class
# ------------------------------------------------
class Base_Optimizer(ABC):
    """Base abstract class for all circuit optimizers"""
    def __init__(self, setup_obj: Project_Setup, output_root: Path | None = None):
        self.setup_obj = setup_obj
        self.optimizer_config = setup_obj.optimizer_config

        self._TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.autosave_checkpoint_freqeucny : int = 2500
        # Default autosave dir is `WORK_ROOT/auto_save/<run-name>` (the storage
        # kernel's resolver — meta plan_project_filesystem §6): a CLI/example/agent
        # run that passes no `output_root` lands its checkpoints in ONE discoverable
        # place instead of spraying a CWD-relative ./auto_save wherever the process
        # happened to be launched. When a caller passes `output_root` it is used AS
        # the exact checkpoint dir (the UI backend passes a per-run
        # `runs/<id>/checkpoints` under WORK_ROOT) — so a Docker run's checkpoints
        # survive `docker rm` rather than dying in the ephemeral image layer, and
        # each run's checkpoints are isolated.
        if output_root is not None:
            self.autosave_checkpoint_dir : Path = Path(output_root)
        else:
            from spicexplorer_core.workspace import work_root
            self.autosave_checkpoint_dir = work_root() / "auto_save" / (
                f"{self.setup_obj.name}_{self.setup_obj.optimizer_config.name}_{self._TIMESTAMP}")
        # Do NOT mkdir the checkpoint dir here — `save_checkpoint` creates it lazily on
        # the first autosave. The one-shot routes (/simulate, /sanity, /sensitivity)
        # build an optimizer just to call evaluate()/one step and never checkpoint, so
        # an eager mkdir leaked an empty auto_save/<...> dir per request (BUG-B41).
        logger.debug(f"Autosave checkpoints (frequency : {self.autosave_checkpoint_freqeucny}) will be placed in {self.autosave_checkpoint_dir.absolute()}.")
        self.disable_autosave : bool = False

        # Instantiated & Typed by the base class
        self.optimization_log : OptimizationLog = OptimizationLog()
        self.global_best_index: int = 0 # the best's position within the current in-memory log chunk
        # The best entry seen across the WHOLE run, tracked on the instance so it survives the
        # autosave log reset (which empties optimization_log). get_best_params() prefers this.
        self.global_best_entry: Optional["OptimizationLogEntry"] = None
        self.logger = logger
        self.verbose: bool = True
        # Instantiated & Typed by the children class
        self.parametrization : Any = None
        self.optimizer : Any = None
        # Frozen dut_params (excluded from the search space) → their fixed physical value,
        # populated by `parameterize()` (via the shared `_register_frozen_param` seam) and
        # re-injected into every candidate before `evaluate()` (via `_reinject_frozen_params`).
        # Shared by all backends so the freeze contract lives in ONE place (D-3), not copied
        # per mixin. Empty until parameterize() runs; a no-op when no param sets `freeze: true`.
        self._frozen_params: Dict[str, float] = {}
        # Per-trial wall-time telemetry (E-049), (re)built by `optimize()`; exposed on the
        # instance so a caller can read the run's cost profile after the fact. `stop_reason` is
        # None for a run that finished its budget, and a sentence for one a guard ended early —
        # the difference between "stopped" and "crashed", which a killed run cannot express.
        self.trial_time_monitor: Optional[TrialTimeMonitor] = None
        self.stop_reason: Optional[str] = None

        self._validate_constructor()

    def _validate_constructor(self) -> None:
        if self.setup_obj.optimizer_config is None:
            raise ValueError("cannot use a Null optimizer_config instance")


    # ----------------------------
    # --- Abstract Methods ---
    # ----------------------------
    @abstractmethod
    def _create_optimizer_obj(self) -> bool:
        """Instantiate the self.optimizer object based on the algorithm used (e.g., Nevergrad, Ax BO, Scikit, Torch Models, etc)."""
        pass

    @abstractmethod
    def parameterize(self) -> Any:
        """Returns the parametrization dictionary for nevergrad and any denormalization factors needed. May have different return types"""
        pass

    @abstractmethod
    def evaluate(self, parameterization: Dict[str, float | np.floating]) -> Tuple[np.floating, Dict[str, Any]]:
        """Evaluate the objective function for the given parameterization (de-normalized)"""
        pass

    @abstractmethod
    def compute_fitness(self, performance_array: Mapping[str, np.float64 | torch.Tensor]) -> Tuple[np.float64, Dict[str, Any]]:
        """Compute the fittness of a set of performance metrics provided as an input dictionary"""
        pass

    @abstractmethod
    def optimization_step(self) -> Tuple[Dict[str, np.floating], np.floating, Dict[str, Any]]:
        """Implements one optimization step. Should return the parameters, score, and an optional metadata dictionary"""
        pass

    @abstractmethod
    def plot_solution(self, parameterization: Dict[str, float], **kwargs):
        pass

    # ----------------------------
    # --- Core Methods
    # ----------------------------
    # Most optimizers would share the following code and hence do not need to modify this code
    # ----------------------------
    # ----------------------------
    # --- Frozen-param seam (D-3) — shared by every backend's parameterize/step ---
    # ----------------------------
    def _reset_frozen_params(self) -> None:
        """Start a fresh frozen-param map. Called at the top of `parameterize()`."""
        self._frozen_params = {}

    def _register_frozen_param(self, param) -> bool:
        """If `param` is frozen, record its fixed physical value and return True so the
        caller skips it from the search space; otherwise return False.

        A frozen param's value is `val` (else `init`); when neither is given it is skipped
        from the space AND left out of `_frozen_params`, so the netlist's own `.param`
        default is used — matching the historical Nevergrad behavior. Default `freeze` is
        False, so this is a no-op unless a param explicitly sets `freeze: true`."""
        if not getattr(param, "freeze", False):
            return False
        fixed = param.val if param.val is not None else param.init
        if fixed is not None:
            self._frozen_params[param.name] = float(fixed)
        return True

    def _reinject_frozen_params(self, denorm_params: Dict[str, Any]) -> Dict[str, Any]:
        """Re-inject the frozen params (excluded from the search space) at their fixed value
        just before `evaluate()`, so the deck is written with the full param set. Mutates and
        returns `denorm_params`; a no-op when nothing is frozen."""
        if self._frozen_params:
            denorm_params.update(self._frozen_params)
        return denorm_params

    def _frozen_param_defaults(self) -> Dict[str, float]:
        """Every frozen dut_param's fixed physical value (`val` → `init`), read from the project.

        Unlike `_frozen_params` (populated only by `parameterize()`), this is available on
        EVERY evaluation path — including a bare `evaluate()` (manual single sim, sensitivity
        sweep) where `parameterize()`/`optimization_step`'s re-injection never ran. It is used
        to complete the sizing for **param-derived** metrics (e.g. active area references frozen
        multipliers): a sim metric falls back to the deck's own `.param` default for an omitted
        frozen param, but a derived metric has no deck — so it must read the frozen `val` here,
        or it would `KeyError`→NaN→penalty for a design the optimizer scores finitely."""
        out: Dict[str, float] = {}
        for p in self.setup_obj.dut_params:
            if getattr(p, "freeze", False):
                fixed = p.val if p.val is not None else p.init
                if fixed is not None:
                    out[p.name] = float(fixed)
        return out

    def denormalize_params(self, parameterization: Dict[str, float | np.floating]) -> Dict[str, np.floating]:
        denorm_params: Dict[str, np.floating] = {}

        cfg = self.setup_obj.optimizer_config
        log_bounds = cfg.log_variable_bounds
        lin_bounds = cfg.lin_variable_bounds
        log_range = cfg.get_log_variable_range()  # max - min
        lin_range = cfg.get_lin_variable_range()

        for param_name in parameterization:
            val = parameterization[param_name]
            param_obj = self.setup_obj.get_param_by_name(name=param_name)

            if param_obj is None:
                raise KeyError(f"Could not find param name {param_name} in {self.setup_obj.list_params()}")

            if param_obj.is_integer:
                denorm_params[param_name] = val

            elif param_obj.log_scale:
                # nevergrad samples the candidate in [log_bounds.min, log_bounds.max]
                # (parameterize builds ng.p.Log(lower=min, upper=max)), so the [0,1] coordinate
                # is (val - min)/range — NOT val/range, which only lands in [0,1] when min==0 and
                # otherwise pushes the physical value outside [min_val, max_val] (BUG-B6).
                x = (val - log_bounds.min) / log_range
                denorm_params[param_name] = log_denormalize(x=x, pmin=param_obj.min_val, pmax=param_obj.max_val)
            else:
                x = (val - lin_bounds.min) / lin_range
                denorm_params[param_name] = linear_denormalize(x=x, pmin=param_obj.min_val, pmax=param_obj.max_val)

        return denorm_params

    def optimize(self, render_optimization_trace: bool = False, keep_history: bool = False) -> OptimizationLog | None:
        """Run the optimization process for a given budget and returns the optimization trace as
        an OptimizationLog object."""

        logger.info("Optimization process started.")
        self._create_optimizer_obj()
        if self.optimizer is None:
            logger.critical("Oops... The optimizer object was not created!")
            return None

        # Per-trial wall-time telemetry (ledger E-049). Every threshold defaults to None (off),
        # so a project that configures nothing gets the periodic INFO cadence line and no change
        # in behaviour. Read defensively: `optimize()` also runs against light config stand-ins.
        _cfg = self.optimizer_config
        _report_every = getattr(_cfg, "trial_time_report_every", None)
        trial_timer = TrialTimeMonitor(
            warn_s=getattr(_cfg, "trial_time_warn_s", None),
            warn_factor=getattr(_cfg, "trial_time_warn_factor", None),
            stop_s=getattr(_cfg, "trial_time_stop_s", None),
            report_every=(DEFAULT_TRIAL_TIME_REPORT_EVERY if _report_every is None
                          else int(_report_every)),
        )
        self.trial_time_monitor = trial_timer
        self.stop_reason = None

        # Track the score for plotting
        self.optimization_log = OptimizationLog() if not keep_history else self.optimization_log

        # Track the best across the WHOLE run on the instance, so it survives the autosave log
        # reset (the in-memory log is emptied on each autosave, but the best entry must not be
        # lost). Seed from any retained history (keep_history); a fresh run starts with no best.
        if not self.optimization_log.is_empty():
            self.global_best_index = int(np.argmax([e.point.score for e in self.optimization_log]))
            self.global_best_entry = self.optimization_log[self.global_best_index]
        else:
            self.global_best_index = 0
            self.global_best_entry = None

        # MAIN OPTIMIZATION LOOP
        try:
            with tqdm(range(self.optimizer_config.budget), desc="Optimizing", unit="trial") as pbar:
                for trial in pbar:
                    logger.debug("---------------------------------------------------------------------------")
                    logger.debug(f"STARTING trial {trial+1}/{self.optimizer_config.budget}...")

                    # (a) Perform the optimization logic for one step/trial
                    _t_trial = monotonic()
                    candidate, curr_score, metadata = self.optimization_step()
                    verdict = trial_timer.record(monotonic() - _t_trial)
                    logger.debug(f"Trial {trial+1}/{self.optimizer_config.budget} COMPLETED with score: {curr_score:.4f}")

                    # (a.1) Per-trial cost telemetry. A run's per-trial wall time is NOT constant:
                    #       a Bayesian backend's refit cost climbs with the observation count
                    #       (27 s -> 117 s -> 200-292 s in ledger E-049) while the simulation cost
                    #       is unchanged. Without this the loop gave no signal and such runs had to
                    #       be killed by hand.
                    if verdict.report is not None:
                        logger.info(verdict.report)
                    if verdict.warning is not None:
                        logger.warning(verdict.warning)

                    # (b) Update the running best. Compare against the GLOBAL best entry's score
                    #     (instance-tracked), NOT an index into the log: the log is emptied on each
                    #     autosave (step c), so indexing it by the absolute `trial` raised IndexError
                    #     and a fresh chunk could regress the best (BUG-B5). `global_best_index` is
                    #     kept as the best's position within the CURRENT chunk for back-compat.
                    last_idx = len(self.optimization_log) - 1
                    if last_idx >= 0 and (
                        self.global_best_entry is None
                        or curr_score > self.global_best_entry.point.score
                    ):
                        self.global_best_entry = self.optimization_log[last_idx]
                        self.global_best_index = last_idx
                        logger.info(f"New fit was found... trial {trial} score {curr_score:.2f}")

                    # (c) Autosave checkpoint if flag is not disabled. Resetting the in-memory log
                    #     also resets the per-chunk index; the best ENTRY survives on the instance.
                    if (not self.disable_autosave) and (self.autosave_checkpoint_freqeucny is not None) and ((trial+1) % self.autosave_checkpoint_freqeucny == 0):
                        self.save_checkpoint(name=self.get_auto_save_name(append_txt=f"trial{trial+1}"))
                        self.optimization_log = OptimizationLog()
                        self.global_best_index = 0
                        logger.debug("Reset the optimization_log after autosave")

                    # Update the progress bar from the instance-tracked best (valid across resets).
                    current_best = (
                        self.global_best_entry.point.score if self.global_best_entry is not None
                        else curr_score
                    )
                    pbar.set_postfix(score=f"{curr_score:.4f}", best=f"{current_best:.4f}")
                    logger.debug("---------------------------------------------------------------------------")

                    # (d) Optional hard stop. Placed LAST in the body so the trial is fully
                    #     recorded and autosaved first; breaking here falls through to the same
                    #     `finally` teardown and final checkpoint a completed budget takes, so the
                    #     run ends STOPPED (with a reason on the instance), not crashed.
                    if verdict.stop:
                        self.stop_reason = (
                            f"stopped by the per-trial time guard at trial {trial+1}/"
                            f"{self.optimizer_config.budget}: rolling median "
                            f"{verdict.rolling_median_s:.1f} s/trial exceeded "
                            f"trial_time_stop_s={trial_timer.stop_s}."
                        )
                        logger.warning(self.stop_reason)
                        break

        except KeyboardInterrupt:
            logger.critical("User requested interrupt")
        finally:
            # Release the persistent OCEAN session's license token if a Spectre+OCEAN run
            # spawned one (idempotent; a no-op for ngspice / metric-less runs). `optimize`
            # lives on Base_Optimizer, so guard the Spice-only teardown hook.
            close_ocean = getattr(self, "_close_ocean_ctx", None)
            if callable(close_ocean):
                close_ocean()
            close_measure = getattr(self, "_close_measure_ctx", None)
            if callable(close_measure):
                close_measure()
            close_derived = getattr(self, "_close_derived_ctx", None)
            if callable(close_derived):
                close_derived()

        if not self.disable_autosave and not self.optimization_log.is_empty():
            logger.info(f"saving the unsaved results... len = {len(self.optimization_log)} - Last Trial = {trial}")
            self.save_checkpoint(name=self.get_auto_save_name(append_txt=f"trial{trial+1}_FINAL"))


        # Plot the score as a function of optimization step
        if render_optimization_trace:
            self.plot_score(show=True)
        logger.info("Optimization process completed.")
        return self.optimization_log

    def get_best_params(self, verbose: bool = False) -> Tuple[Dict[str, float], float, Dict[str, Any]] | None:
        """Retrieve the best parameters and corresponding score from the optimization trace."""

        if self.optimizer is None:
            logger.info("Need to set the optimizer by calling self.create_experiment")
            return

        # Prefer the instance-tracked best entry — it survives the autosave log reset, so a run
        # that ended exactly on a reset boundary (in-memory log empty) still reports its best.
        entry = getattr(self, "global_best_entry", None)
        if entry is None:
            if len(self.optimization_log) < 1:
                logger.info("need to run self.optimize")
                return
            entry = self.optimization_log[self.global_best_index]

        best_solution : Dict[str, np.floating | float]  = entry.get_params()
        score : float                                   = float(entry.get_score())
        metadata : Dict[str, Any] | None                = entry.get_metadata()

        if verbose:
            logger.info("Optimized x - normalized:", best_solution)
            logger.info("Optimized x - de-normalized:", self.denormalize_params(best_solution))
        logger.info(f"best score: {float(score)}")

        return best_solution, score, metadata

    def plot_score(self, save_path: Path | None = None, show: bool = False):
        """Plot the score as a function of optimization steps with Plotly."""
        logger = logging.getLogger("SpiceXplorer.plotter")

        if len(self.optimization_log) < 1:
            logger.warning("No optimization trace to plot")
            return

        score_values = [entry.get_score() for entry in self.optimization_log]
        x_values = list(range(len(score_values)))

        # Compute running best (cumulative maximum)
        best_scores = np.maximum.accumulate(np.array(score_values))

        fig = go.Figure()

        # Plot raw score values
        fig.add_trace(go.Scatter(
            x=x_values,
            y=score_values,
            mode="markers+lines",
            name="Score",
            line=dict(color="blue", width=2),
            opacity=0.6
        ))

        # Plot best-so-far curve
        fig.add_trace(go.Scatter(
            x=x_values,
            y=best_scores,
            mode="lines",
            name="Best Score So Far",
            line=dict(color="red", width=2)
        ))

        fig.update_layout(
            title="Score vs. Optimization Trial",
            xaxis_title="Optimization Step",
            yaxis_title="Score",
            template="plotly_dark",
            showlegend=True
        )

        # Save to file if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Plot saved to {save_path}")

        # Optionally show interactively (browser popup)
        if show:
            logger.info("Opening interactive plot in browser...")
            fig.show()

    def plot_design_space_exploration(self, param_x: str, param_y: str, save_path: Path | None = None, show: bool = False, denorm: bool = False) -> Tuple[torch.Tensor, torch.Tensor] | None:
        """Plot the exploration of the design space in terms of two parameters with Plotly."""
        logger = logging.getLogger("SpiceXplorer.plotter")

        if len(self.optimization_log) < 1:
            logger.warning("No optimization trace to plot")
            return None

        if not self.optimization_log.has_param(param_name=param_x):
            logger.warning(f"param_x '{param_x}' not found in optimization trace")
            return None
        if not self.optimization_log.has_param(param_name=param_y):
            logger.warning(f"param_y '{param_y}' not found in optimization trace")
            return None

        # De-normalize
        if denorm:
            denormalized_params = [self.denormalize_params(entry.get_params()) for entry in self.optimization_log]
            x_values = torch.tensor([entry[param_x] for entry in denormalized_params], device=device)
            y_values = torch.tensor([entry[param_y] for entry in denormalized_params], device=device)
        else:
            x_values = torch.tensor([entry.get_param_val(param_x) for entry in self.optimization_log], device=device)
            y_values = torch.tensor([entry.get_param_val(param_y) for entry in self.optimization_log], device=device)

        loss      = torch.tensor([entry.get_score() for entry in self.optimization_log], device=device)


        fig = go.Figure()

        # Scatter with heatmap coloring by FOM
        fig.add_trace(go.Scatter(
            x=x_values.cpu().numpy(),
            y=y_values.cpu().numpy(),
            mode="markers",
            marker=dict(
                size=10,
                color=loss.cpu().numpy(),   # heatmap coloring
                colorscale="Viridis",      # you can change to "Plasma", "Cividis", etc.
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

        # Save to file if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Plot saved to {save_path}")

        # Optionally show interactively (browser popup)
        if show:
            logger.info("Opening interactive plot in browser...")
            fig.show()

        return x_values, y_values

    def _resolve_fit_summary_key(self, metric: str) -> str | None:
        """Resolve a metric name against the first log entry's fit_summary keys.

        A multi-corner log namespaces keys as ``"<corner>::<spec>"``, so a legacy
        bare spec name (``"ugf"``) no longer matches exactly. Fall back to the
        namespaced candidate for the **worst corner** on this spec — the one with the
        lowest mean per-spec score across the log (PLOT-1) — rather than the
        first-enumerated corner (usually ``tt``, the easy one), so a bare-name plot is
        sign-off-honest. Pass the full ``"corner::spec"`` key to choose a specific
        corner. Returns None when nothing matches."""
        logger = logging.getLogger("SpiceXplorer.plotter")
        fit_summary = self.optimization_log[0].get_fit_summary()
        if metric in fit_summary:
            return metric
        candidates = [k for k in fit_summary if k.split("::")[-1] == metric]
        if candidates:
            chosen = self._worst_corner_key(candidates)
            logger.warning(
                f"metric '{metric}' is corner-namespaced in this log — plotting the "
                f"worst corner '{chosen}' (available: {candidates}; pass the full "
                f"'<corner>::{metric}' key to pick a corner)")
            return chosen
        logger.warning(f"metric '{metric}' not found in optimization log")
        return None

    def _worst_corner_key(self, candidates: List[str]) -> str:
        """Of several ``"<corner>::<spec>"`` keys for one spec, return the corner that
        performs worst on it — the lowest mean per-spec ``score`` over the log (lower
        score = closer to / further into constraint violation). Ties keep the earlier
        candidate; falls back to the first candidate if no finite scores exist."""
        worst_key, worst_agg = candidates[0], float("inf")
        for key in candidates:
            vals = []
            for entry in self.optimization_log:
                cell = (entry.fit_summary or {}).get(key)
                if isinstance(cell, dict) and cell.get("score") is not None:
                    s = float(cell["score"])
                    if np.isfinite(s):
                        vals.append(s)
            agg = float(np.mean(vals)) if vals else float("inf")
            if agg < worst_agg:
                worst_agg, worst_key = agg, key
        return worst_key

    def plot_optimization_trace(self, metric_x: str, metric_y: str, save_path: Path | None = None, show: bool = False) -> Tuple[torch.Tensor, torch.Tensor] | None:
        logger = logging.getLogger("SpiceXplorer.plotter")
        if len(self.optimization_log) < 1:
            logger.warning("No optimization log to plot")
            return None

        metric_x = self._resolve_fit_summary_key(metric_x)
        if metric_x is None:
            return None

        metric_y = self._resolve_fit_summary_key(metric_y)
        if metric_y is None:
            return None

        x_values = torch.tensor([entry.get_fit_summary()[metric_x]['curr_val'] for entry in self.optimization_log], device=device)
        y_values = torch.tensor([entry.get_fit_summary()[metric_y]['curr_val'] for entry in self.optimization_log], device=device)
        fom      = torch.tensor([entry.get_score() for entry in self.optimization_log], device=device)

        fig = go.Figure()

        # Scatter with heatmap coloring by FOM
        fig.add_trace(go.Scatter(
            x=x_values.cpu().numpy(),
            y=y_values.cpu().numpy(),
            mode="markers",
            marker=dict(
                size=10,
                color=fom.cpu().numpy(),   # heatmap coloring
                colorscale="Viridis",      # you can change to "Plasma", "Cividis", etc.
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

        # Save to file if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Plot saved to {save_path}")

        # Optionally show interactively (browser popup)
        if show:
            logger.info("Opening interactive plot in browser...")
            fig.show()

        return x_values, y_values

    # Saving & Checkpointing
    def save_checkpoint(self, name: str | Path) -> None:
        """Save optimizer state to JSON with schema versioning."""

        # Serialize each entry. `log_file` is Optional[Dict[str, str|Path]]; asdict
        # leaves the Path VALUES as Path objects (not JSON-serializable). The old
        # code stringified the WHOLE dict to a repr ("{'ac': PosixPath('…')}") AND
        # mutated the live entry — that repr can't be fed back through dacite, which
        # is exactly why load_checkpoint choked on real runs. Convert per value so
        # the field stays a proper Dict[str, str]: JSON-clean AND round-trippable.
        cleaned_optimization_log = []
        for e in self.optimization_log:
            d = asdict(e)
            lf = d.get("log_file")
            if isinstance(lf, dict):
                d["log_file"] = {str(k): str(v) for k, v in lf.items()}
            elif lf is not None and not isinstance(lf, str):
                d["log_file"] = str(lf)
            cleaned_optimization_log.append(d)

        # Create a filename-friendly timestamp (e.g. 2025-10-09_02-35-10)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        checkpoint = {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "timestamp": timestamp,
            "optimization_log": cleaned_optimization_log,
        }

        p = Path(name).with_suffix(".json")
        path = p.with_name(f"{p.stem}_{timestamp}{p.suffix}")

        # Atomic write: a torn autosave (process killed mid-dump) would make the
        # NEXT resume unparseable, silently discarding every trial since the last
        # good checkpoint. atomic_write_json swaps the file in via os.replace so a
        # crash leaves the previous complete checkpoint intact.
        atomic_write_json(path, checkpoint, indent=2)
        logger.info(f"✅ Checkpoint saved to {path}")

    @classmethod
    def load_checkpoint(cls, setup_obj: Project_Setup, path_to_checkpoint: str | Path, **kwargs) -> "Base_Optimizer":
        """Load optimizer and project setup from JSON checkpoint with version validation."""
        path = Path(path_to_checkpoint)
        with open(path, "r") as f:
            data = json.load(f)

        # Validate schema version
        version = data.get("schema_version")
        if version != CHECKPOINT_SCHEMA_VERSION:
            logger.warning(f"⚠️ Checkpoint version mismatch: {version} != {CHECKPOINT_SCHEMA_VERSION}")

        # Recreate optimizer instance
        obj = cls(setup_obj=setup_obj, **kwargs)

        # Tolerate a LEGACY checkpoint whose `log_file` was serialized as the repr
        # of the whole dict (a string, possibly containing PosixPath(...), which is
        # NOT a Python literal). dacite would reject that string for the Dict-typed
        # field (WrongTypeError) — the bug that forced callers to route around this
        # method. Parse it WITHOUT executing code (ast.literal_eval rejects calls),
        # dropping to None on anything it can't parse; per-trial ngspice log paths
        # are not needed to resume. New checkpoints store a real dict → untouched.
        raw_entries = data.get("optimization_log", [])
        for entry in raw_entries:
            if isinstance(entry, dict) and isinstance(entry.get("log_file"), str):
                try:
                    entry["log_file"] = ast.literal_eval(entry["log_file"])
                except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
                    entry["log_file"] = None

        # Rebuild optimization log
        obj.optimization_log = OptimizationLog([
            from_dict(OptimizationLogEntry, entry, Config(strict=False))
            for entry in raw_entries
        ])

        logger.info(f"✅ Checkpoint loaded successfully from {path}")
        return obj

    def get_auto_save_name(self, append_txt: str ) -> Path:
        return self.autosave_checkpoint_dir / Path(f"{self.setup_obj.name}_{self.setup_obj.optimizer_config.name}_{self.setup_obj.optimizer_config.budget}_{append_txt}")
# ------------------------------------------------
# A [ABSTRACT] SPICE-based Optimizers
# ------------------------------------------------
class Spice_Base_Optimizer(Base_Optimizer):
    """ Base class for optimizers that use SPICE simulations.

    ``spicelib_wrappers`` is any mapping of testbench name → `Simulator` (the
    structural protocol in `spicexplorer_core.spice_engine.protocol`): the concrete
    `NGSpice_Wrapper`, the optional Spectre adapter, or a test fake. The attribute
    keeps its historical name so checkpoints/callers are untouched."""
    def __init__(self,
                setup_obj: Project_Setup,
                spicelib_wrappers : Dict[str, Simulator],
                output_root: Path | None = None):
        super().__init__(setup_obj = setup_obj, output_root = output_root)
        self.spicelib_wrappers = spicelib_wrappers
        # Opt-in artifact retention: when True the per-trial raw-file cleanup at the end of
        # every evaluate() is skipped, so run dirs keep their .raw waveforms for the result
        # viewer (/api/waveview/open_run). Default False — disk use grows with
        # budget × testbenches when enabled.
        self.keep_raw_artifacts: bool = False
        # Per-testbench wall time of the MOST RECENT simulate_circuit pass, keyed like
        # its results (bare testbench name; the multi-corner parallel fan-out uses
        # "<tb>__<corner>"). Parallel spans are each sim's own submit→done window, so a
        # fast bench is not billed for a slow sibling — but they do include any wait in
        # the runner's concurrency queue.
        self.last_sim_timings_s: Dict[str, float] = {}
        self.__post_init__()

    def __post_init__(self):
        # ----------------------------------------
        # Update the tb parameters
        # ----------------------------------------
        for tb in self.setup_obj.testbenches:
            # Wrappers are built only for ENABLED testbenches (orchestrator /
            # _build_spicelib_wrappers skip disabled ones), but this list includes
            # disabled testbenches too — indexing a missing wrapper would raise
            # KeyError. Skip any testbench without a wrapper.
            if tb.name not in self.spicelib_wrappers:
                continue
            tb_params = {param.name : param.get_val() for param in tb.params if param.has_val()}
            if tb_params:
                logger.info(f"updating the parameters for testbench {tb.name} with the following values:")
                for param_name, param_val in tb_params.items():
                    logger.info(f"\t{param_name}: {param_val}")
                logger.info("")
            self.spicelib_wrappers[tb.name].update_params(tb_params)
            logger.info(f"parameter update is compeleted for testbench {tb.name}")
        # ----------------------------------------
        # Apply the active PVT corner (Phase 1) — one-time netlist preparation.
        # When `pvt` is configured in SINGLE mode, the chosen corner's `.lib`/temp/
        # supply are applied to every (enabled) testbench wrapper ONCE here, before
        # the optimization loop; each subsequent trial inherits it because the
        # SpiceEditor state persists. When `pvt` is None this is a no-op and the
        # corner is whatever the netlist hardcodes (legacy behavior).
        # In MULTI mode (Phase 2) the one-time apply is skipped: every evaluation
        # re-applies each enabled corner right before its own sims (see
        # Spice_Constraint_Satisfaction.evaluate), so priming one corner here would
        # be immediately overwritten.
        # ----------------------------------------
        pvt = getattr(self.setup_obj, "pvt", None)
        if pvt is not None:
            if getattr(pvt, "is_multi", lambda: False)():
                corners = [c.name for c in pvt.corners_to_run()]
                logger.info(
                    f"🌡️  PVT multi-corner mode: {len(corners)} enabled corner(s) "
                    f"{corners} will be applied per evaluation "
                    f"(score_aggregation='{pvt.score_aggregation}')"
                )
            else:
                corner = pvt.get_active()
                logger.info(
                    f"🌡️  Applying PVT corner '{corner.name}' to "
                    f"{len(self.spicelib_wrappers)} testbench(es)"
                )
                for tb_name, wrapper in self.spicelib_wrappers.items():
                    wrapper.apply_corner(corner, model_lib_root=pvt.model_lib_root)
        # ----------------------------------------
        # Canonical OCEAN metric path (Spectre only). Built lazily on first score —
        # `target_specs` is set by the concrete subclass AFTER this __post_init__ runs —
        # and stays None for ngspice or a Spectre run with no `measurement` recipes. Typed
        # `Any` (a lazily-imported optional handle — an OceanMergeContext or None).
        self._ocean_ctx: Any = None
        self._ocean_ctx_built: bool = False
        # Tier-1 (engine-neutral Python) measurement context — a MeasureMergeContext or
        # None. Built for ANY engine whose target specs carry a `{meas: …}` recipe (no
        # license/process, so unlike OCEAN it isn't gated on sim_engine).
        self._measure_ctx: Any = None
        self._measure_ctx_built: bool = False
        # Param-derived metric context — a DerivedMetricContext or None. Built when any
        # enabled target carries a `{derived: …}` recipe (e.g. active area): computed from
        # the candidate sizing, no simulation, so it too is engine-agnostic.
        self._derived_ctx: Any = None
        self._derived_ctx_built: bool = False

    def _ensure_ocean_ctx(self) -> Any:
        """Lazily construct (once) the OCEAN merge context for a Spectre run whose target
        specs carry `measurement` recipes; `None` otherwise. Held for the run's lifetime
        (one persistent OCEAN session ≈ one license token) and closed in `optimize`."""
        if self._ocean_ctx_built:
            return self._ocean_ctx
        self._ocean_ctx_built = True
        target_specs = getattr(self, "target_specs", None)
        if target_specs is not None and getattr(self.setup_obj, "sim_engine", "ngspice") == "spectre":
            from spicexplorer.optimization.ocean_integration import OceanMergeContext

            self._ocean_ctx = OceanMergeContext.build(
                target_specs, vb_env_file=os.environ.get("SPICEXPLORER_VB_ENV_FILE")
            )
        return self._ocean_ctx

    def _close_ocean_ctx(self) -> None:
        """Release the OCEAN session's license token if one was ever spawned (idempotent)."""
        ctx = getattr(self, "_ocean_ctx", None)
        if ctx is not None:
            ctx.close()

    def _ensure_measure_ctx(self) -> Any:
        """Lazily construct (once) the Tier-1 measurement context when any enabled target
        carries a `{meas: …}` recipe; `None` otherwise. Engine-neutral — no license, no
        process — so it is built regardless of `sim_engine`."""
        if self._measure_ctx_built:
            return self._measure_ctx
        self._measure_ctx_built = True
        target_specs = getattr(self, "target_specs", None)
        if target_specs is not None:
            from spicexplorer.optimization.measure_integration import MeasureMergeContext

            self._measure_ctx = MeasureMergeContext.build(target_specs)
        return self._measure_ctx

    def _close_measure_ctx(self) -> None:
        """Symmetry with `_close_ocean_ctx` — the Tier-1 context holds no resource, but
        closing it uniformly keeps the teardown path engine-agnostic (idempotent)."""
        ctx = getattr(self, "_measure_ctx", None)
        if ctx is not None:
            ctx.close()

    def _ensure_derived_ctx(self) -> Any:
        """Lazily construct (once) the param-derived metric context when any enabled target
        carries a `{derived: …}` recipe; `None` otherwise. Engine-neutral and sim-free —
        no license, no process — so it is built regardless of `sim_engine`."""
        if self._derived_ctx_built:
            return self._derived_ctx
        self._derived_ctx_built = True
        target_specs = getattr(self, "target_specs", None)
        if target_specs is not None:
            from spicexplorer.optimization.derived_integration import DerivedMetricContext

            self._derived_ctx = DerivedMetricContext.build(
                target_specs, netlist_path=self._resolve_dut_deck()
            )
        return self._derived_ctx

    def _resolve_dut_deck(self) -> Any:
        """The DUT self-contained deck (`ws_root/netlist`), used by a netlist-driven derived
        metric (active_area) to walk every device. `None` if it can't be resolved — the derived
        context then degrades that metric to NaN rather than crashing."""
        setup = getattr(self, "setup_obj", None)
        if setup is None or getattr(setup, "netlist", None) is None:
            return None
        deck = Path(setup.netlist)
        if not deck.is_absolute():
            deck = Path(setup.ws_root) / deck
        return deck if deck.exists() else None

    def _close_derived_ctx(self) -> None:
        """Symmetry with the other measurement contexts (no resource to release; idempotent)."""
        ctx = getattr(self, "_derived_ctx", None)
        if ctx is not None:
            ctx.close()

    def close(self) -> None:
        """Release any run-scoped resources (the OCEAN license token). Idempotent.

        `optimize()` closes automatically in its `finally`; a caller driving the optimizer
        by **bare `evaluate()`** (a manual single sim, a sensitivity sweep) must call this
        when done — or use the optimizer as a context manager — so a Spectre+OCEAN run's
        persistent session doesn't outlive the batch. (A GC/atexit finalizer on the OCEAN
        context is a backstop, but explicit close is deterministic.)"""
        self._close_ocean_ctx()
        self._close_measure_ctx()
        self._close_derived_ctx()

    def __enter__(self) -> "Spice_Base_Optimizer":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # --- Helper Methods (only in child class) ---
    @staticmethod
    def _collect_result(sim: Simulator, handle: SimHandle) -> SimResult:
        """Read a submitted run back as a `SimResult`.

        Prefer the backend's own duck-typed ``collect`` when it offers one (ngspice:
        parses the RAW exactly once AND refreshes ``curr_raw``/``curr_log`` for legacy
        readers like ``plot_solution``); otherwise fall back to ``handle.result()``,
        which any `SimHandle` provides."""
        collect = getattr(sim, "collect", None)
        if callable(collect):
            # duck-typed: `collect` is outside the protocol, so its return is untyped
            return cast(SimResult, collect(handle))
        return handle.result()

    def _wait_for_handles(
        self, handles: Dict[str, SimHandle], timeout_s: float | None = None
    ) -> Tuple[List[str], Dict[str, float]]:
        """Poll ``handles`` until all are ``is_done()`` or ``timeout_s`` elapses.

        Returns ``(pending, done_at)``: ``pending`` are the keys whose sim did NOT finish
        in time — the caller degrades those to a ``_FailedSimResult`` (NaN metrics →
        MAX_PENALTY) so a hung child fails the TRIAL, not the whole run — and ``done_at``
        maps each completed key to the ``monotonic()`` stamp of its ``is_done()`` flip,
        so the caller can attribute a per-testbench sim time even though the batch ran
        concurrently. ``timeout_s`` defaults to ``_SIM_WAIT_TIMEOUT_S``; ``<= 0`` waits
        forever (the legacy behavior). The ``SimHandle`` protocol has no cancel, so a
        timed-out sim's OS process is left to finish on its own (it may still hold a
        runner slot) — bounding the WAIT, not the child, is the engine-neutral guarantee
        available here."""
        if timeout_s is None:
            timeout_s = _SIM_WAIT_TIMEOUT_S
        pending, done_at = wait_for_handles_timed(handles, timeout_s=timeout_s)
        if pending:
            logger.error(
                f"Timed out after {timeout_s:.0f}s waiting for {len(pending)} sim(s) "
                f"[{', '.join(pending)}]; scoring them as failures so this trial fails, not the "
                f"run. Raise SPICEXPLORER_SIM_WAIT_TIMEOUT_S for a legitimately slow batch."
            )
        return pending, done_at

    def simulate_circuit(self, parameterization: Dict[str, float], run_label: str | None = None) -> Dict[str, SimResult]:
        """Run every enabled testbench once with the given params, returning each
        testbench's `SimResult`.

        Engine-neutral: blocking runs go through the `Simulator` protocol's ``run()``,
        parallel ones through ``submit()`` + `_collect_result`. A failed sim (ngspice:
        no RAW written) still yields a result — its scalars read NaN and score as
        MAX_PENALTY downstream (BUG-B28), the failed testbench just no longer drops
        out of the returned dict.

        ``run_label`` (multi-corner mode: the corner name) is appended to each
        testbench's run-folder label — ``run_<n>_<tb>__<corner>`` — so the
        per-corner artifacts of one trial don't overwrite each other. ``None``
        keeps the legacy per-testbench label."""
        logger.debug("Simulating the circuit with the given parameterization")
        results :  Dict[str, SimResult] = {}
        handles : Dict[str, SimHandle] = {}
        submitted_at : Dict[str, float] = {}
        timings : Dict[str, float] = {}
        tb_idx = 0

        for tb, sim in self.spicelib_wrappers.items():
            tb_idx += 1
            logger.debug(f"\t({tb_idx} / {len(self.setup_obj.testbenches)}) Testbench: {tb}")

            sim.update_params(parameterization)
            label = f"{tb}__{run_label}" if run_label else None

            if not self.setup_obj.parallel_sim:
                logger.debug("parallel_sim: FALSE -> blocking run()")
                t0 = monotonic()
                result = sim.run(label=label)
                timings[tb] = monotonic() - t0
                # Non-convergence on an extreme candidate is routine in analog sizing —
                # the None-backed result degrades to NaN metrics, never an abort. The
                # `raw` probe is ngspice's; other engines simply don't warn here.
                if getattr(result, "raw", True) is None:
                    logger.warning(
                        f"No RAW generated for testbench '{tb}' (sim failed/diverged); this trial's "
                        f"'{tb}' metrics will score as failures.")
                results[tb] = result

            else:
                logger.debug("parallel_sim: TRUE -> non-blocking submit()")
                submitted_at[tb] = monotonic()
                handles[tb] = sim.submit(label=label)

        if self.setup_obj.parallel_sim:
            logger.debug("Waiting for tasks to finish.")
            pending, done_at = self._wait_for_handles(handles)
            timed_out = set(pending)
            t_end = monotonic()
            logger.debug("All tasks completed." if not timed_out
                         else f"{len(timed_out)} sim(s) timed out; scoring as failures.")
            for tb, handle in handles.items():
                # Per-testbench span: this sim's own submit→done window (a timed-out sim
                # is billed up to the wait bound), NOT the batch wall time.
                timings[tb] = (done_at[tb] if tb not in timed_out else t_end) - submitted_at[tb]
                # A timed-out handle is NOT collected — result()/collect() would block on the hung
                # child. Substitute a NaN-scoring failure so only this trial's `tb` metrics fail.
                results[tb] = (_FailedSimResult() if tb in timed_out
                               else self._collect_result(self.spicelib_wrappers[tb], handle))
        self.last_sim_timings_s = timings
        for tb, secs in timings.items():
            logger.debug(f"\t⏱️  sim time for testbench '{tb}': {secs:.3f} s")
        return results

    def plot_score_value_by_spec(self, spec_name: str, save_path: Path | None = None, show: bool = False):
        """
        Plot the score value for a specific target spec over the optimization trials.
        Includes target spec value, tolerance band, and error type information.
        """
        logger = logging.getLogger("spicexplorer.plotter")
        if len(self.optimization_log) < 1:
            logger.warning("No optimization log to plot")
            return

        spec_name = self._resolve_fit_summary_key(spec_name)
        if spec_name is None:
            return

        # Extract values from optimization log. _resolve_fit_summary_key matched
        # against entry[0]; a resumed/mixed log can lack that key in later entries
        # (a corner absent post-resume), so index defensively — a missing cell is
        # NaN (a plotted gap), not a KeyError that kills the whole plot.
        spec_values = [entry.get_fit_summary().get(spec_name, {}).get('curr_val', np.nan) for entry in self.optimization_log]
        score_values = [entry.get_fit_summary().get(spec_name, {}).get('score', np.nan) for entry in self.optimization_log]

        finite_scores = [s for s in score_values if s is not None and not np.isnan(s)]
        if finite_scores:
            logger.info(f"\tmin score {min(finite_scores)}; max score {max(finite_scores)}")

        # Get TargetSpec definition. A multi-corner log namespaces the fit_summary
        # key as "<corner>::<spec>" — the spec definition is looked up by the bare
        # spec name (the target/tolerance are corner-independent).
        target_spec = self.setup_obj.optimizer_config.target_specs.get_target_by_name(spec_name.split("::")[-1])
        if target_spec is None:
            logger.warning(f"No TargetSpec found for '{spec_name}'")
            return

        target_val = float(target_spec.target)
        tolerance  = float(target_spec.tolerance if target_spec.tolerance is not None else 0.0)
        error_type = target_spec.error_type

        fig = go.Figure()

        # Scatter plot
        fig.add_trace(go.Scatter(
            x=spec_values,
            y=score_values,
            mode="markers",
            name=f"Score: {spec_name}",
            marker=dict(color="blue", size=8, opacity=0.7, symbol="circle"),
        ))

        # Add vertical line at target value
        fig.add_vline(
            x=target_val,
            line=dict(color="red", width=2, dash="dash"),
            annotation_text=f"Target = {target_val:.2e}",
            annotation_position="top right",
            annotation_font=dict(color="red")
        )

        # Add tolerance bounds if available
        if tolerance is not None:
            if target_spec.goal != OptimizationGoalType.MINIMIZE:
                fig.add_vline(
                    x=target_val - tolerance,
                    line=dict(color="green", width=1, dash="dot"),
                    annotation_text=f"-tol ({target_val - tolerance:.2e})",
                    annotation_position="bottom left",
                    annotation_font=dict(color="green")
                )

            if target_spec.goal != OptimizationGoalType.EXCEED:
                fig.add_vline(
                    x=target_val + tolerance,
                    line=dict(color="green", width=1, dash="dot"),
                    annotation_text=f"+tol ({target_val + tolerance:.2e})",
                    annotation_position="bottom right",
                    annotation_font=dict(color="green")
                )

        # Dynamic title with error type info
        error_type_str = error_type.value if error_type else "unknown"
        goal_type_str = target_spec.goal.value if target_spec.goal else "unknown"

        fig.update_layout(
            title=f"Score for Spec '{spec_name}' (Error: {error_type_str}, Goal {goal_type_str})",
            xaxis_title=f"{spec_name} Value",
            yaxis_title="Score",
            template="plotly_dark",
            showlegend=True
        )

        # Save to file if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            logger.info(f"📊 Plot saved to {save_path}")

        # Optionally show interactively
        if show:
            logger.info("Opening interactive plot in browser...")
            fig.show()

    def plot_solution(self, parameterization: Dict[str, float], **kwargs):

        score, fit_summary = self.evaluate(parameterization, append_to_log=False)

        logger.info(f"total score: {score}")
        for spec_name, spec_info in fit_summary.items():
            logger.info(f"\tSpec '{spec_name}': curr_val={spec_info['curr_val']}, score={spec_info['score']}")

        if kwargs.get("show_plot", False):

            try:
                trace_name = kwargs["trace_name"]
            except KeyError:
                logger.error("To plot the solution, trace_name must be provided in kwargs")
                raise RuntimeError("To plot the solution, trace_name must be provided in kwargs")

            try:
                plot_type : Ngspice_Plot_Type = kwargs["plot_type"]
            except KeyError:
                logger.error("To plot the solution, plot_type must be provided in kwargs")
                raise RuntimeError("To plot the solution, plot_type must be provided in kwargs")

            try:
                tb_name : str = kwargs["testbench_name"]
            except KeyError:
                logger.error("To plot the solution, testbench_name must be provided in kwargs")
                raise RuntimeError("To plot the solution, testbench_name must be provided in kwargs")

            wrapper = self.spicelib_wrappers[tb_name]
            if not isinstance(wrapper, NGSpice_Wrapper):
                raise NotImplementedError(
                    "plot_solution's trace plotting reads ngspice plots (it takes an "
                    "Ngspice_Plot_Type) and is ngspice-only for now.")
            trace = torch.from_numpy(wrapper.extract_wave(trace_name, plot_type=plot_type, is_real=False))

            plot_complex_response(
                frequencies=torch.from_numpy(wrapper.extract_wave("frequency", plot_type=plot_type, is_real=True)),
                complex_response_list=[trace],
                labels = kwargs.get("labels", [trace_name]),
                title  = kwargs.get("title", f"Response: {trace_name}")
                )

    def clean_up(self, delete_raw_only: bool = False) -> None:
        """Clean up all SPICE simulations if needed."""
        if delete_raw_only and getattr(self, "keep_raw_artifacts", False):
            logger.debug("keep_raw_artifacts set — leaving per-trial raw files in place")
            return
        logger.debug(f"Cleaning up all SPICE simulation (delete raws only? {delete_raw_only})...")
        for tb, wrapper in self.spicelib_wrappers.items():
            # `clean_up` is outside the `Simulator` protocol (a local-artifact concern);
            # a backend with no local artifacts (Spectre runs remotely) simply lacks it.
            cleanup = getattr(wrapper, "clean_up", None)
            if not callable(cleanup):
                logger.debug(f"Backend for testbench {tb} keeps no local artifacts; nothing to clean")
                continue
            logger.debug(f"Cleaning up SPICE wrapper for testbench: {tb}")
            if delete_raw_only: cleanup(keep_netlist=True, keep_logs=True, keep_raw=False)
            else:               cleanup(delete_directories=True)
        logger.debug("✅ Clean up completed for all SPICE wrappers.")
        logger.debug("")

# ------------------------------------------------
# A.1 [ABSTRACT] Bode Fitter
# ------------------------------------------------
class Spice_Bode_Optimizer(Spice_Base_Optimizer):
    """ Nevergrad optimizer that fits a SPICE-simulated transfer function to a target transfer function. """
    def __init__(self,
                 setup_obj: Project_Setup,
                 spicelib_wrappers : Dict[str, Simulator],
                 target_tf: Expr,
                 output_node: str = "Vout", # FIXME this needs to go into the spicelib_wrapper
                 frequency_weight: Frequency_Weight | None = None,
                 output_root: Path | None = None,
                 ):

        # Forward output_root so per-run checkpoint isolation works for Bode runs too (BUG-B26).
        super().__init__(setup_obj = setup_obj, spicelib_wrappers = spicelib_wrappers,
                         output_root = output_root)

        self.target_tf = target_tf
        self.output_node = output_node
        self.frequency_weight  = frequency_weight

        self.helper_functions = Transfer_Func_Helper()
        # To be calculated during the program runtime
        self.target_complex_response: torch.Tensor  | None = None
        self.frequency_array: torch.Tensor | None = None # is resolved the first time the LTspice is run

    # --- Overwriting the Abstract Methods ---
    def evaluate(self, parameterization: Dict[str, float]) -> Tuple[np.float64, Dict[str, Any]]:
        """
        Evaluate the given parameterization by running a SPICE simulation,
        computing the fitness score, and returning it as np.float64.
        """
        # 1 - Run a SPICE simulation
        # ---------------------------------------------------------------
        self.simulate_circuit(parameterization=parameterization)

        # 2 - Extract frequency array (first run only)
        # ---------------------------------------------------------------
        self.prepare_frequency_array()

        # 3 - Extract circuit response
        # ---------------------------------------------------------------
        current_complex_response = self.extract_circuit_response_from_latest_run()

        # 4 - Compute the fitness
        # ---------------------------------------------------------------
        fitness_score, fit_summary = self.compute_fitness({"current_complex_response" : current_complex_response})

        # --- Log results ---
        mag_loss   = fit_summary['mag_loss']
        phase_loss = fit_summary['phase_loss']

        self.optimization_log.append(
            OptimizationLogEntry(
                OptimizationPoint(
                    params=parameterization,
                    score=np.float64(fitness_score),
                    metadata={"complex_response": current_complex_response}
                ),
                fit_summary={
                    "mag_loss": np.float64(mag_loss),
                    "phase_loss": np.float64(phase_loss),
                    "max_mag": np.float64(fit_summary['curr_max_mag'])
                },
                log_file=None
                )
            )

        logger.debug("finished the trial evaluation.... summary")
        logger.debug(f"\tmetric_value = {fitness_score}")
        logger.debug(f"\t\t- mag_loss : {mag_loss}")
        logger.debug(f"\t\t- phase_loss : {phase_loss}")

        self.clean_up(delete_raw_only=True)

        return np.float64(fitness_score), fit_summary

    # --- Helper Methods (only in child class) ---
    def extract_circuit_response_from_latest_run(self) -> torch.Tensor:
        logger.debug("Extracting the circuit response from the latest RAW file")
        current_complex_response = torch.from_numpy(self.spicelib_wrappers.extract_wave(self.output_node))
        return current_complex_response

    def examine_target(self, f_array: torch.Tensor):
        logger.info(f"computing the target complex response for {self.target_tf}")
        self.target_complex_response = self.helper_functions.eval_tf(tf=self.target_tf, f_val=f_array)
        # mag, _ = self.helper_functions.get_mag_phase_from_complex_response(self.target_complex_response)

    def compute_fitness(self, performance_array: Mapping[str, np.float64 | torch.Tensor]) -> Tuple[np.float64, Dict[str, Any]]:

        current_complex_response: torch.Tensor = performance_array["current_complex_response"]

        if self.setup_obj.optimizer_config is None:
            raise RuntimeError("Optimizer config cannot be None.")
        if self.target_complex_response is None:
            raise RuntimeError("Reached the comparison between target and simulated performance but the target was not computed... make sure self.examine_target works correctly.")

        loss_fn_config = self.setup_obj.optimizer_config.loss_function_config
        fit_summary = get_bode_fitness_loss(
            current_complex_response=current_complex_response,
            target_complex_response=self.target_complex_response,
            freq_weights=self.frequency_weight.weights,
            norm_method=loss_fn_config.loss_norm_method,
            loss_type=loss_fn_config.loss_type,
            rescale=loss_fn_config.rescale_mag
        )

        mag_loss   = fit_summary['mag_loss']
        phase_loss = fit_summary['phase_loss']

        mag, _ = self.helper_functions.get_mag_phase_from_complex_response(
            complex_response_array=current_complex_response
        )

        # --- Compute final metric (NumPy only) ---
        metric_value = np.float64(0.0)
        metric_value += np.float64(mag_loss if loss_fn_config.include_mag_loss else 0.0)
        metric_value += np.float64(phase_loss if loss_fn_config.include_phase_loss else 0.0)
        metric_value += np.float64(
            max(0.0, fit_summary['target_max_mag'] - fit_summary['curr_max_mag']) ** 2
        )

        return metric_value, fit_summary

    def prepare_frequency_array(self):
        if self.frequency_array is None:
            try:
                self.frequency_array = torch.from_numpy(self.spicelib_wrappers.extract_wave("frequency", is_real=True))
            except IndexError:
                logger.critical("Attempted to look up the 'frequency' trace but it doesnt exist in the RAW file")
                raise RuntimeError("Attempted to look up the 'frequency' trace but it doesnt exist in the RAW file")
            self.examine_target(f_array=self.frequency_array)

        if self.frequency_weight is None:
            raise RuntimeError("frequency_weight must be specified.")
        if self.frequency_weight.weights is None:
            self.frequency_weight.parent_frequency_array = self.frequency_array
            self.frequency_weight.compute_weights()

    # --- Visualization Methods ---
    # Over-writing the abstract method
    def plot_solution(self, parameterization: Dict[str, float], **kwargs):

        self.simulate_circuit(parameterization)
        current_complex_response = self.extract_circuit_response_from_latest_run()
        self.prepare_frequency_array()

        loss, fit_summary = self.compute_fitness({"current_complex_response" : current_complex_response})

        logger.info(f"total loss: {loss}")
        logger.info(f"mag_loss {fit_summary['mag_loss']}, phase_loss {fit_summary['phase_loss']}")

        plot_complex_response(
            frequencies=self.frequency_array if self.frequency_array is not None else torch.tensor([]),
            complex_response_list=[self.target_complex_response, current_complex_response],
            labels=['Target', 'Optimized']
            )

# ------------------------------------------------
# A.2 [ABSTRACT] Constraint Satisfaction
# ------------------------------------------------
class Spice_Constraint_Satisfaction(Spice_Base_Optimizer):
    def __init__(self,
                 setup_obj: Project_Setup,
                 spicelib_wrappers : Dict[str, Simulator],
                 output_root: Path | None = None):
        """
        A Concrete implementation of Spice_Base_Optimizer that evaluates a circuit
        against a list of TargetSpecs.

        This class implements the 'evaluate' and 'compute_fitness' methods to:
        1. Run the simulation.
        2. Extract scalar metrics defined in TargetSpecs.
        3. Calculate a scalar fitness score (Penalty only).
        """
        super().__init__(setup_obj = setup_obj, spicelib_wrappers = spicelib_wrappers, output_root = output_root)
        self.target_specs: ListTargetSpec = setup_obj.optimizer_config.target_specs
        logger.info(f"Initialized the Nevergrad_Spice_Multi_Spec_Optimizer with {len(self.target_specs.targets)} target specs")

    # --- Overwriting the Abstract Methods ---
    def _extract_and_score_current(
        self, results: Dict[str, SimResult], parameterization: Dict[str, float] | None = None
    ) -> Tuple[np.float64, Dict[str, Any]]:
        """Extract each enabled target spec's scalar from this pass's `SimResult`s
        and score them with ``compute_fitness``.

        Engine-neutral: `SimResult.scalar(name, analysis)` replaces the old
        wrapper-state read (`extract_scalar_variable_from_raw` over `curr_raw`) —
        same numbers (the ngspice result's parity with the legacy extractor is
        pinned in core's protocol tests), but each pass's results are now
        self-contained objects instead of a mutable slot on the wrapper, which is
        what lets the corner-PARALLEL path score corners independently. A spec whose
        sim produced no data reads NaN and scores as MAX_PENALTY exactly as before;
        a spec naming a testbench that has no simulator (a disabled testbench) still
        raises KeyError — that is a config error and should stay loud.

        For a Spectre run, canonical OCEAN measurements are evaluated here — post-sim,
        on each result's own PSF raw dir — and merged into the `SimResult` under their
        spec name BEFORE the scalar reads below. This is the single seam every eval path
        funnels through (single / sequential-multi / parallel-corner), and it receives
        the corner-correct `results`, so per-corner metrics are read from the right raw
        dir for free. Ngspice runs skip it (no context).

        `parameterization` (the denormalized, frozen-injected candidate) feeds any
        param-derived specs (`{derived: …}`, e.g. active area): their scalar is computed
        from the sizing itself and OVERLAID onto the performance map, so `compute_fitness`
        normalizes/aggregates them exactly like a sim metric. It is passed at every eval
        site; `None` (or no derived specs) simply reads all specs from the sims as before."""
        ocean_ctx = self._ensure_ocean_ctx()
        if ocean_ctx is not None:
            ocean_ctx.merge(results)
        # Tier-1 (engine-neutral Python) measurements: computed from each result's own
        # waves and merged under the spec name, same seam/order as OCEAN so the scalar
        # reads below find them. Runs for ngspice and Spectre alike; None when no target
        # carries a `{meas: …}` recipe.
        measure_ctx = self._ensure_measure_ctx()
        if measure_ctx is not None:
            measure_ctx.merge(results)
        # Param-derived metrics (`{derived: …}`) are computed from the candidate sizing, not
        # a sim result — so they are read from this dict instead of `results[...]` below.
        # Complete the sizing with the frozen params' fixed values so a derived metric sees
        # the FULL geometry on every eval path — including a bare `evaluate()` (manual sim /
        # sensitivity) whose partial vector omits frozen params (optimization_step's
        # re-injection didn't run); the passed `parameterization` wins any overlap.
        derived_ctx = self._ensure_derived_ctx()
        derived_vals: Dict[str, float] = {}
        if derived_ctx is not None and parameterization is not None:
            full_params = {**self._frozen_param_defaults(), **parameterization}
            derived_vals = derived_ctx.compute(full_params)
            # Opt-in per-device area audit (SPICEXPLORER_AREA_DEBUG=1): dump the recursive
            # breakdown table so every counted transistor + multiplier is visible for one point.
            if os.environ.get("SPICEXPLORER_AREA_DEBUG") and hasattr(derived_ctx, "report"):
                try:
                    from spicexplorer_core.measurements.area import format_area_table

                    logger.info("active-area breakdown:\n%s",
                                format_area_table(derived_ctx.report(full_params)))
                except Exception as exc:  # never let a debug dump break scoring
                    logger.debug("area breakdown unavailable: %s", exc)
        performance_array = {}
        for target in self.target_specs.enabled_targets():
            if target.name in derived_vals:  # param-derived (corner-independent): no sim read
                performance_array[target.name] = np.float64(derived_vals[target.name])
                continue
            result = results[target.testbench]
            performance_array[target.name] = np.float64(
                result.scalar(target.name, target.get_analysis())
            )
        return self.compute_fitness(performance_array=performance_array)

    # ---- per-TRIAL accumulators (reset by `evaluate`, folded in after every scoring pass) ----
    def _reset_trial_records(self) -> None:
        """Start a fresh trial's by-product accumulators.

        `compute_fitness` publishes each scoring pass's unmeasured-spec names and per-spec margins
        on the instance (it cannot widen its return tuple — light scorer stand-ins unpack exactly
        two values). A multi-corner trial scores once PER CORNER, so those single-pass slots are
        overwritten; these accumulators keep the whole trial's, namespaced by corner."""
        self._trial_unmeasured: List[str] = []
        self._trial_spec_margins: Dict[str, Dict[str, Any]] = {}

    def _record_trial_pass(self, corner_name: str | None = None) -> None:
        """Fold the pass `compute_fitness` just finished into this trial's accumulators.

        `corner_name` is the corner that pass ran at (multi-corner) or `None` (single corner),
        and namespaces the recorded spec keys exactly as `fit_summary` namespaces its own."""
        if not hasattr(self, "_trial_unmeasured"):
            self._reset_trial_records()
        prefix = f"{corner_name}::" if corner_name else ""
        for name in getattr(self, "_last_unmeasured_specs", ()) or ():
            self._trial_unmeasured.append(f"{prefix}{name}")
        self._trial_spec_margins[corner_name or ""] = dict(
            getattr(self, "_last_spec_margins", {}) or {})

    def _evaluate_at_current_corner(self, parameterization: Dict[str, float], run_label: str | None = None) -> Tuple[np.float64, Dict[str, Any], Dict[str, SimResult]]:
        """One full pass at whatever corner the wrappers' netlists currently carry:
        simulate every enabled testbench, extract each enabled target spec's scalar,
        and score it. This is the Phase-1 evaluation body, factored out so the
        multi-corner loop can call it once per corner. Also returns the per-testbench
        `SimResult`s so the caller can harvest per-run log files."""
        results = self.simulate_circuit(parameterization=parameterization, run_label=run_label)
        score, fit_summary = self._extract_and_score_current(results, parameterization)
        # `run_label` IS the corner name on the sequential multi-corner path and None in single
        # mode, which is exactly the namespace this pass's by-products belong under.
        self._record_trial_pass(run_label)
        return score, fit_summary, results

    def _evaluate_corners_parallel(
        self, parameterization: Dict[str, float], pvt
    ) -> Tuple[Dict[str, np.float64], Dict[str, Any], Dict[str, Any]]:
        """Multi-corner evaluation with the CORNER axis fanned out in parallel.

        The corner loop used to be strictly sequential — each corner's sims ran to
        completion before the next corner's began — so one trial's wall-time was the
        SUM over corners. But corners are independent given a fixed candidate, and
        ``run_and_pass`` writes the (corner-applied) netlist to that run's own folder
        synchronously *before* the sim launches, so we can apply-and-launch every
        (corner, testbench) sim first and only then wait + read. That overlaps the
        corners' ngspice runs (each testbench's own runner still bounds its own
        concurrency) instead of serializing them. Returns
        ``(corner_scores, fit_summary, log_files)`` — the same three products the
        sequential loop builds, so aggregation/logging downstream is unchanged.

        Requires ``parallel_sim`` (it uses ``run_and_pass``); ``evaluate`` keeps a
        sequential fallback for ``parallel_sim: false``.
        """
        corners = pvt.corners_to_run()

        # PHASE 1 — apply each corner and LAUNCH its sims without waiting. Each
        # submit() snapshots the current (corner-applied) netlist into its own
        # run_<n>_<tb>__<corner> folder, so re-applying the next corner to the same
        # editor cannot disturb an already-launched run.
        launched: Dict[str, Dict[str, SimHandle]] = {}
        submitted_at: Dict[str, float] = {}
        for corner in corners:
            handles: Dict[str, SimHandle] = {}
            for tb, sim in self.spicelib_wrappers.items():
                sim.apply_corner(corner, model_lib_root=pvt.model_lib_root)
                sim.update_params(parameterization)
                submitted_at[f"{corner.name}::{tb}"] = monotonic()
                handles[tb] = sim.submit(label=f"{tb}__{corner.name}")
            launched[corner.name] = handles

        # PHASE 2 — wait for EVERY (corner, testbench) sim across all corners (bounded).
        flat_handles: Dict[str, SimHandle] = {
            f"{corner_name}::{tb}": h
            for corner_name, tb_map in launched.items()
            for tb, h in tb_map.items()
        }
        logger.debug(
            f"Waiting for {len(flat_handles)} sim(s) across {len(corners)} corner(s) "
            f"(parallel corner axis)."
        )
        pending, done_at = self._wait_for_handles(flat_handles)
        timed_out = set(pending)
        t_end = monotonic()
        logger.debug("All corner×testbench sims completed." if not timed_out
                     else f"{len(timed_out)} corner×testbench sim(s) timed out; scoring as failures.")
        # Per-(corner, testbench) sim spans, keyed "<tb>__<corner>" like the log files.
        timings: Dict[str, float] = {}
        for key in flat_handles:
            corner_name, tb = key.split("::", 1)
            timings[f"{tb}__{corner_name}"] = (
                (done_at[key] if key not in timed_out else t_end) - submitted_at[key])
        self.last_sim_timings_s = timings
        for run_key, secs in timings.items():
            logger.debug(f"\t⏱️  sim time for '{run_key}': {secs:.3f} s")

        # PHASE 3 — collect each corner's results and extract + score that corner.
        # Every corner's results are self-contained `SimResult`s (no shared
        # curr_raw/curr_log slot to keep pointed at the right corner any more);
        # `_collect_result` still cycles the ngspice wrapper's state per corner for
        # legacy readers, ending on the last corner exactly as before.
        corner_scores: Dict[str, np.float64] = {}
        fit_summary: Dict[str, Any] = {}
        log_files: Dict[str, Any] = {}
        for corner in corners:
            corner_results: Dict[str, SimResult] = {
                tb: (_FailedSimResult() if f"{corner.name}::{tb}" in timed_out
                     else self._collect_result(self.spicelib_wrappers[tb], launched[corner.name][tb]))
                for tb in self.spicelib_wrappers
            }
            corner_score, corner_fit = self._extract_and_score_current(corner_results, parameterization)
            self._record_trial_pass(corner.name)
            corner_scores[corner.name] = np.float64(corner_score)
            for spec_name, spec_info in corner_fit.items():
                fit_summary[f"{corner.name}::{spec_name}"] = spec_info
            for tb, result in corner_results.items():
                log_path = getattr(result, "log_path", None)
                if log_path is not None:
                    log_files[f"{tb}__{corner.name}"] = log_path
            logger.debug(f"\tcorner '{corner.name}' score = {corner_score}")

        return corner_scores, fit_summary, log_files

    def _spec_axis_kwargs(self) -> Dict[str, Any]:
        """The spec-axis aggregation knobs, resolved off `optimizer_config` with the SAME
        defensive defaults `compute_fitness` uses (it is also invoked unbound against light
        stand-ins that carry no config). One resolver, so the per-corner scorer and the
        `worst_spec` re-aggregation can never disagree about the project's strategy."""
        cfg = getattr(self, "optimizer_config", None)
        tb_weight = getattr(cfg, "tie_breaker_weight", None)
        margin_w = getattr(cfg, "margin_reward_weight", None)
        margin_clip = getattr(cfg, "margin_reward_clip", None)
        return dict(
            strategy=getattr(cfg, "spec_aggregation", "feasibility_reward"),
            params=getattr(cfg, "aggregation_params", None),
            tie_breaker=getattr(cfg, "tie_breaker", None),
            tie_breaker_weight=(DEFAULT_TIE_BREAKER_WEIGHT if tb_weight is None
                                else float(tb_weight)),
            margin_reward_weight=(DEFAULT_MARGIN_REWARD_WEIGHT if margin_w is None
                                  else float(margin_w)),
            margin_reward_clip=(DEFAULT_MARGIN_REWARD_CLIP if margin_clip is None
                                else float(margin_clip)),
        )

    def _aggregate_worst_spec_over_corners(
        self, fit_summary: Dict[str, Any]
    ) -> Tuple[np.float64, Dict[str, Any]]:
        """`pvt.score_aggregation: worst_spec` — worst corner PER SPEC, then ONE spec aggregation.

        Reads the per-corner per-spec scores back out of the `"<corner>::<spec>"`-keyed
        `fit_summary` the multi-corner paths already build, so neither corner loop needs a wider
        return type and `fit_summary`'s shape is untouched (`_worst_corner_key`, `_metric_series`
        and the Ax backend's corner-aware tracking metrics all read that shape). The margins the
        opt-in margin reward consumes come from this trial's own accumulator, reduced the same way
        — worst corner per spec — so a margin-rewarded multi-corner run pays for worst-CORNER
        headroom rather than nominal headroom.

        Returns `(score, metadata_extras)`; the extras name the corner that BOUND each spec, which
        is the diagnostic a user actually wants ("which corner is costing me?") and is not
        recoverable from the aggregated scalar.
        """
        per_corner_spec_scores: Dict[str, Dict[str, np.float64]] = {}
        for key, info in fit_summary.items():
            corner_name, sep, spec_name = str(key).partition("::")
            if not sep:  # a bare (non-namespaced) key cannot be attributed to a corner
                continue
            per_corner_spec_scores.setdefault(corner_name, {})[spec_name] = np.float64(
                info["score"])
        worst_scores, binding = aggregate_corner_spec_scores(per_corner_spec_scores)
        worst_margins = aggregate_corner_spec_margins(
            getattr(self, "_trial_spec_margins", {}) or {})
        score = aggregate_spec_scores(
            worst_scores, spec_margins=worst_margins, **self._spec_axis_kwargs()
        )
        for spec_name in sorted(worst_scores):
            logger.debug(
                f"\tspec '{spec_name}': worst corner '{binding[spec_name]}' "
                f"score = {worst_scores[spec_name]}"
            )
        logger.debug(
            f"\t'{PER_SPEC_CORNER_AGGREGATION}': {len(worst_scores)} spec(s) reduced over "
            f"{len(per_corner_spec_scores)} corner(s) -> {score} "
            f"(binding corners: {binding})"
        )
        return np.float64(score), {
            "worst_spec_scores": {k: float(v) for k, v in worst_scores.items()},
            "binding_corners": dict(binding),
        }

    def evaluate(self, parameterization: Dict[str, float], append_to_log: bool = True) ->  Tuple[np.floating, Dict[str, Any]]:
        """
        Evaluate the given parameterization by running a SPICE simulation,
        computing the fitness score, and returning it as np.float64 plus a metadata dictionary.

        With ``pvt.mode: multi`` (Phase 2) this runs the whole
        {enabled testbenches} × {enabled corners} cross-product: each enabled corner
        is applied to every wrapper, simulated, and scored on its own, then the
        per-corner scores are collapsed into ONE scalar via
        ``pvt.score_aggregation`` (sum / mean / min). The returned ``fit_summary``
        is keyed ``"<corner>::<spec>"`` and the per-corner totals ride along in the
        log entry's ``metadata`` (``corner_scores`` / ``score_aggregation``).
        Single mode is byte-identical to Phase 1 (bare spec keys, no metadata).
        """
        pvt = getattr(self.setup_obj, "pvt", None)

        self._reset_trial_records()
        metadata: Dict[str, Any] = {}
        log_files: Dict[str, Any] = {}
        if pvt is None or not getattr(pvt, "is_multi", lambda: False)():
            fitness_score, fit_summary, results = self._evaluate_at_current_corner(parameterization)
            log_files = {}
            for tb, result in results.items():
                log_path = getattr(result, "log_path", None)
                if log_path is not None:
                    log_files[tb] = log_path
        else:
            if self.setup_obj.parallel_sim:
                # Corner axis fanned out in parallel: apply+launch every
                # (corner, testbench) sim, then wait + read + score. Corners overlap
                # in wall-time instead of running back-to-back.
                corner_scores, fit_summary, log_files = self._evaluate_corners_parallel(
                    parameterization, pvt
                )
            else:
                # Sequential fallback (parallel_sim: false): one corner fully
                # simulated + scored before the next — the exact pre-parallel behavior.
                corner_scores: Dict[str, np.float64] = {}
                fit_summary = {}
                for corner in pvt.corners_to_run():
                    for sim in self.spicelib_wrappers.values():
                        sim.apply_corner(corner, model_lib_root=pvt.model_lib_root)
                    corner_score, corner_fit, corner_results = self._evaluate_at_current_corner(
                        parameterization, run_label=corner.name
                    )
                    corner_scores[corner.name] = np.float64(corner_score)
                    for spec_name, spec_info in corner_fit.items():
                        fit_summary[f"{corner.name}::{spec_name}"] = spec_info
                    # each corner's results are self-contained — key its logs now.
                    for tb, result in corner_results.items():
                        log_path = getattr(result, "log_path", None)
                        if log_path is not None:
                            log_files[f"{tb}__{corner.name}"] = log_path
                    logger.debug(f"\tcorner '{corner.name}' score = {corner_score}")

            metadata = {
                "corner_scores": {k: float(v) for k, v in corner_scores.items()},
                "score_aggregation": pvt.score_aggregation,
            }
            if pvt.score_aggregation == PER_SPEC_CORNER_AGGREGATION:
                # `worst_spec`: reduce the SPEC axis across corners FIRST — each spec keeps its
                # worst corner — then aggregate the spec axis ONCE with the project's own
                # `spec_aggregation`. The resulting score (and therefore the reported best design
                # and its feasibility) means "feasible at EVERY enabled corner", which the totals
                # reducers cannot express: they average a spec's `ss` failure into `ss`'s total
                # before it is ever compared with `tt`'s.
                fitness_score, extra = self._aggregate_worst_spec_over_corners(fit_summary)
                metadata.update(extra)
            else:
                fitness_score = aggregate_corner_scores(corner_scores, pvt.score_aggregation)
                logger.debug(
                    f"\taggregated {len(corner_scores)} corner scores via "
                    f"'{pvt.score_aggregation}' -> {fitness_score}"
                )

        # OPT-IN unmeasured-metric record (`unmeasured_policy: fail`). The SCORE already fails
        # closed under every policy — an unmeasured spec takes `compute_fitness`'s else-branch and
        # is assigned `-MAX_PENALTY` *instead of* running any error kernel, so even a bounded
        # kernel (relative-sigmoid) inherits that same defined, bounded worst case and the trial
        # cannot come out feasible. What did NOT exist is any way to tell that apart afterwards
        # from a design that converged to a terrible value and clipped to the same floor: the API
        # checkpoint reader RE-DERIVES feasibility from values and targets, and `fit_summary` only
        # carries `curr_val: nan`. `fail` records it explicitly on the trial.
        _policy = getattr(self.optimizer_config, "unmeasured_policy", None) or DEFAULT_UNMEASURED_POLICY
        if _policy == "fail":
            unmeasured = list(getattr(self, "_trial_unmeasured", []))
            metadata = dict(metadata)
            metadata["unmeasured_policy"] = _policy
            metadata["unmeasured_specs"] = unmeasured
            # An explicit, recorded feasibility verdict: no spec went unmeasured AND the aggregate
            # is not a net violation. `> -EPSILON` is the SAME threshold `aggregate_spec_scores`
            # uses, so "feasible" means one thing across the scorer and the log.
            metadata["feasible"] = bool(
                not unmeasured and float(fitness_score) > -float(EPSILON))
            if unmeasured:
                logger.warning(
                    f"unmeasured_policy='fail': {len(unmeasured)} enabled spec(s) had no "
                    f"measurable value this trial {unmeasured} — the trial is recorded INFEASIBLE "
                    f"(each such spec already scores -MAX_PENALTY)."
                )

        # Expose this evaluation's per-run log files (multi mode: keyed
        # "<tb>__<corner>") to one-shot callers like the manual-sim route —
        # wrapper.curr_log only retains the LAST corner's log, so without this a
        # multi-corner manual sim could surface only one corner's logs.
        self.last_eval_log_files = dict(log_files)

        # --- Log results ---
        if append_to_log:
            self.optimization_log.append(OptimizationLogEntry(
                OptimizationPoint(
                    params=parameterization,
                    score=fitness_score,
                    metadata=metadata,
                ),
                fit_summary=fit_summary,
                log_file=log_files
                ))

        logger.debug("finished the trial evaluation.... summary")
        logger.debug(f"\tmetric_value = {fitness_score}")

        self.clean_up(delete_raw_only=True)

        return fitness_score, fit_summary

    def compute_fitness(self, performance_array: Mapping[str, float | np.float64 | torch.Tensor]) -> Tuple[np.float64, Dict[str, Any]]:
        """ Compute the fitness based on the performance metrics extracted from SPICE simulations and the target specs. """
        # Initialize variables
        reward      : np.float64 = np.float64(0.0)
        penalty     : np.float64 = np.float64(0.0)
        total_score : np.float64 = np.float64(0.0)
        fit_summary : Dict[str, Any] = {}
        spec_scores : Dict[str, np.float64] = {}
        # Enabled specs this pass could NOT measure (missing key / non-finite / non-positive under
        # log_scale). Recorded ALWAYS (it costs one list append on a path that is already taking
        # the failure branch) and consumed only by `unmeasured_policy: fail` — see `evaluate`.
        unmeasured_specs : List[str] = []
        # Per-spec normalized margins, populated only when the opt-in margin reward is ON, so the
        # default path never enters `normalized_spec_margin` at all (bit-identity by construction).
        spec_margins : Dict[str, Any] = {}
        _cfg = getattr(self, "optimizer_config", None)
        _margin_w = getattr(_cfg, "margin_reward_weight", None)
        _margin_w = (DEFAULT_MARGIN_REWARD_WEIGHT if _margin_w is None else float(_margin_w))
        _margin_clip = getattr(_cfg, "margin_reward_clip", None)
        _margin_clip = (DEFAULT_MARGIN_REWARD_CLIP if _margin_clip is None else float(_margin_clip))

        # Iterate over each target specification
        # ------------------------------------------------------------------------------
        for spec in self.target_specs.enabled_targets():
            spec_fitness: np.float64 = np.float64(0.0)
            # a - Compute the spec score
            if (
                spec.name in performance_array
                and performance_array[spec.name] is not None
                and is_scoreable_metric(performance_array[spec.name], log_scale=spec.log_scale)
            ):
                spec_fitness = self.compute_fitness_for_spec(curr_val=performance_array[spec.name], target_spec=spec)
                spec_fitness = np.clip(spec_fitness, -1 * MAX_PENALTY, MAX_REWARD) # cap the score to avoid overflow
                if _margin_w > 0:
                    # Same geometry the reward kernels use (boundary + normalizing_coeff), shared
                    # rather than re-derived — see `core.utils.normalized_spec_margin`.
                    spec_margins[spec.name] = normalized_spec_margin(
                        performance_array[spec.name], spec)
            else:
                if self.verbose:
                    logger.debug(f"Target spec name '{spec.name}' not found in performance array keys: {list(performance_array.keys())}")
                    logger.debug(f"assigning large penalty to the {spec.name} spec")
                # A missing/degenerate metric means the sim failed or diverged: score it as the
                # maximal penalty for EVERY error type, so a failed sim strictly dominates any
                # converged in-band violation (matching the documented run_and_wait failure contract
                # above). The old RELATIVE_SIGMOID carve-out scored a failure as only -weight (≈ -1) —
                # bounded like a sigmoid violation — which let a crashed sim OUTSCORE a bad-but-
                # converged design and pulled the optimizer toward crashes (cross_repo_audit).
                # "Degenerate" is `is_scoreable_metric`: NON-FINITE (`nan`/`±inf`), or
                # non-positive under `log_scale`. The gate used to be a bare `isnan`, so `-inf`
                # (and a `log_scale` metric at 0, which the decade transform turns into `-inf`)
                # slipped through and earned an infinite reward that clipped to +MAX_REWARD — a
                # permanent global best for the worst possible candidate. It is deliberately NOT
                # goal-aware: the Tier-1 library does return ±inf as a PERFECT sentinel too, but
                # it is the SAME value a diverged solve returns, and the shipped EXCEED+reward
                # specs are all `dcgain`, where +inf means the AC blew up. See
                # `is_scoreable_metric` and doc/TODO.md §22.
                spec_fitness = -1 * np.float64(MAX_PENALTY)  # assign the maximal penalty if the spec is not found
                unmeasured_specs.append(spec.name)
            # b - Log the spec score
            fit_summary[spec.name] = {
                "curr_val": performance_array.get(spec.name, np.nan) ,
                "score": spec_fitness
            }
            # c - Update the overall fitness
            spec_scores[spec.name] = spec_fitness
            if spec_fitness > 0:    reward  += spec_fitness
            else:                   penalty += spec_fitness
        # ------------------------------------------------------------------------------

        # SPEC-AXIS aggregation, selected by `optimizer_config.spec_aggregation` (validated at
        # load). The default `feasibility_reward` is the historical hardcoded rule and is what the
        # `reward if penalty > -EPSILON else penalty` line here used to compute inline:
        # constraint-FIRST (lexicographic) — while ANY spec is violated the score is the penalty sum
        # alone, and reward from satisfied specs is surfaced only once every constraint is met.
        # Intended (drive feasibility first, then optimize), though it does flatten the landscape
        # across the infeasible region (BUG-B23 — a design note, not a defect).
        # `weighted_sum` and `chebyshev` are the alternative scalarizations; see
        # `core.utils.aggregate_spec_scores` for the math and what each one flattens instead.
        # Resolved defensively off `self`: `compute_fitness` is also invoked unbound against light
        # scorer stand-ins (tests, the API's score preview) that carry only the spec list, and a
        # hard `self.optimizer_config` read would turn those into AttributeErrors. A caller with no
        # config gets the historical default.
        # `tie_breaker` is the OPT-IN escape from the reward-less strategies' flat feasible
        # region (every feasible design scores 0, so the reported "best" is search-order noise).
        # Default `None` -> the aggregation is bit-identical to before this key existed.
        # `margin_reward_weight` is the OTHER opt-in escape, and a different one: it pays a
        # FEASIBLE design for its worst normalized spec margin, the quantity E-057/E-058 measured
        # as the predictor of corner survival. Default 0 -> `margin_reward_term` returns None and
        # every historical return statement hands back its exact original object.
        _tb_weight = getattr(_cfg, "tie_breaker_weight", None)
        total_score = aggregate_spec_scores(
            spec_scores,
            strategy=getattr(_cfg, "spec_aggregation", "feasibility_reward"),
            params=getattr(_cfg, "aggregation_params", None),
            tie_breaker=getattr(_cfg, "tie_breaker", None),
            tie_breaker_weight=(DEFAULT_TIE_BREAKER_WEIGHT if _tb_weight is None
                                else float(_tb_weight)),
            spec_margins=spec_margins,
            margin_reward_weight=_margin_w,
            margin_reward_clip=_margin_clip,
        )
        # Publish this pass's by-products on the instance so the (corner-aware) `evaluate` can
        # namespace and record them WITHOUT changing this method's return shape — `compute_fitness`
        # is also invoked unbound against light scorer stand-ins whose callers unpack exactly two
        # values. `setattr` is guarded: a stand-in may be a slotted/frozen object.
        try:
            self._last_unmeasured_specs = tuple(unmeasured_specs)
            self._last_spec_margins = dict(spec_margins)
        except AttributeError:  # pragma: no cover - exotic slotted stand-in
            pass

        logger.debug(f"Computed fitness: {total_score} for performance array: {performance_array}")
        logger.debug(f"\tReward: {reward}")
        logger.debug(f"\tPenalty: {penalty}")
        return total_score, fit_summary

    def compute_fitness_for_spec(self, curr_val: np.float64 | float, target_spec: TargetSpec) -> np.float64:
        """Computes the fitness score for current achieved metric given the target spec. Negative values """
        score = np.float64(0.0)
        # (1) Only return the constraint satisfaction score.
        score += -1 * self.compute_constraint_violation_penalty_for_spec(curr_val=curr_val, target_spec=target_spec)
        return score

    # --- Helper Methods (only in this child class) ---
    def compute_constraint_violation_penalty_for_spec(self, curr_val: np.float64 | float, target_spec: TargetSpec) -> np.float64:
        """ Compute a non-negative value representing the penalty for constraint violation. If zero is returned, the constraint is satisfied."""
        spec_penalty:           np.float64 = np.float64(0.0)
        spec_penalty_weighted:  np.float64 = np.float64(0.0)

        spec_curr_val: np.float64 = np.float64(curr_val)
        target_val: np.float64 = np.float64(target_spec.target)
        tolerance:  np.float64 = np.float64(target_spec.tolerance)

        if target_spec.log_scale:
            # The decade-space error below must be normalized by a DECADE-space range, derived from
            # the ORIGINAL linear target/range BEFORE _log_space_band overwrites target_val — dividing
            # a decades-sized miss by the raw linear range collapses the penalty to ~0 (BUG: GBW-type
            # log-scale constraints were silently dead).
            normalizing_coeff = _log_space_range_coeff(target_val, np.float64(target_spec.range))
            spec_curr_val, target_val, tolerance = _log_space_band(curr_val, target_val, tolerance)
        else:
            normalizing_coeff = np.float64(target_spec.range)
        # --------------------------
        # Case 1: Exact Match
        # --------------------------
        adjusted_target = target_val - tolerance if spec_curr_val < target_val else target_val + tolerance
        if target_spec.goal == OptimizationGoalType.EXACT:
            if abs(spec_curr_val - target_val) > tolerance:
                spec_penalty = compute_error(curr_val=spec_curr_val, target_val=adjusted_target, error_type=target_spec.error_type, normalizing_coeff=normalizing_coeff, error_params=target_spec.error_params, error_state=target_spec.error_state)
            else:
                spec_penalty = np.float64(0.0)
        # --------------------------
        # Case 2: Exceed the Target
        # --------------------------
        elif target_spec.goal == OptimizationGoalType.EXCEED:
            if spec_curr_val < target_val - tolerance:
                spec_penalty = compute_error(curr_val=spec_curr_val, target_val=adjusted_target, error_type=target_spec.error_type, normalizing_coeff=normalizing_coeff, error_params=target_spec.error_params, error_state=target_spec.error_state)
            elif spec_curr_val > target_val + tolerance:
                spec_penalty = np.float64(0.0)
        # --------------------------
        # Case 3: Minimize the Target
        # --------------------------
        elif target_spec.goal == OptimizationGoalType.MINIMIZE:
            if spec_curr_val > target_val + tolerance:
                spec_penalty = compute_error(curr_val=spec_curr_val, target_val=adjusted_target, error_type=target_spec.error_type, normalizing_coeff=normalizing_coeff, error_params=target_spec.error_params, error_state=target_spec.error_state)
            else:
                spec_penalty = np.float64(0.0)

        # --------------------------
        # Case 4: Invalid Goal Type
        # --------------------------
        else:
            logger.error(f"Unknown optimization goal type: {target_spec.goal}")
            raise ValueError(f"Unknown optimization goal type: {target_spec.goal}")
        # --------------------------

        spec_penalty_weighted = spec_penalty * np.float64(target_spec.weight)
        logger.debug(f"Computed Penalty - Spec '{target_spec.name}': curr_val={curr_val}, target={target_spec.target}, penalty={spec_penalty}, weighted_penalty={spec_penalty_weighted} - (goal={target_spec.goal})")
        return spec_penalty_weighted

# ------------------------------------------------
# A.3 [ABSTRACT] Single-objective
# ------------------------------------------------
class Spice_Single_Objective(Spice_Constraint_Satisfaction):
    def __init__(self,
                setup_obj: Project_Setup,
                spicelib_wrappers : Dict[str, Simulator],
                output_root: Path | None = None):
        super().__init__(setup_obj = setup_obj, spicelib_wrappers = spicelib_wrappers, output_root = output_root)

    def compute_fitness_for_spec(self, curr_val: np.float64 | float, target_spec: TargetSpec) -> np.float64:
        """Computes the fitness score for current achieved metric given the target spec. Negative values """
        score = np.float64(0.0)
        # (1) Only return the constraint satisfaction score.
        score += -1 * self.compute_constraint_violation_penalty_for_spec(curr_val=curr_val, target_spec=target_spec)
        score +=      self.compute_reward_for_spec(curr_val=curr_val, target_spec=target_spec)
        return score

    # --- Helper Methods (only in this child class) ---
    def compute_reward_for_spec(self, curr_val: np.float64 | float, target_spec: TargetSpec) -> np.float64:
        """ Compute a non-negative value representing the reward. Returns zero if the constraint is violated"""
        spec_reward:           np.float64 = np.float64(0.0)
        spec_reward_weighted:  np.float64 = np.float64(0.0)

        spec_curr_val: np.float64 = np.float64(curr_val)
        target_val: np.float64 = np.float64(target_spec.target)
        tolerance:  np.float64 = np.float64(target_spec.tolerance)

        if target_spec.log_scale:
            # The decade-space error below must be normalized by a DECADE-space range, derived from
            # the ORIGINAL linear target/range BEFORE _log_space_band overwrites target_val — dividing
            # a decades-sized miss by the raw linear range collapses the penalty to ~0 (BUG: GBW-type
            # log-scale constraints were silently dead).
            normalizing_coeff = _log_space_range_coeff(target_val, np.float64(target_spec.range))
            spec_curr_val, target_val, tolerance = _log_space_band(curr_val, target_val, tolerance)
        else:
            normalizing_coeff = np.float64(target_spec.range)
        # --------------------------
        # Case 1: Exceed the Target
        # --------------------------
        if target_spec.goal == OptimizationGoalType.EXCEED:
            # Reward THROUGH the whole feasible band, measured from the tolerance-adjusted boundary
            # (target - tolerance) the penalty uses, NOT the bare target — symmetric with the MINIMIZE
            # fix (§1.13 / SC-3). The old gate `curr > target` left a flat dead-zone across the grace
            # band [target - tolerance, target) where a satisfied design earned neither penalty nor
            # reward. Measuring from `reward_boundary` makes the reward continuous with the zero penalty
            # at the boundary (both 0 there) and monotonically increasing as curr rises, so a smooth
            # uphill gradient runs through the whole feasible region. (The old dead `elif curr >
            # target + tolerance` branch that only re-assigned the default is gone; BUG-B20.)
            reward_boundary = target_val - tolerance
            if spec_curr_val > reward_boundary:
                spec_reward = compute_reward(curr_val=spec_curr_val, target_val=reward_boundary, reward_type=target_spec.reward_type, normalizing_coeff=normalizing_coeff)
        # --------------------------
        # Case 2: Minimize the Target
        # --------------------------
        elif target_spec.goal == OptimizationGoalType.MINIMIZE:
            # Reward THROUGH the whole feasible band, measured from the tolerance-adjusted
            # boundary the penalty uses (target + tolerance), NOT the bare target. The old gate
            # `curr < target` switched the reward on only BELOW the bare target, leaving a flat
            # dead-zone across (target, target + tolerance] where a design that already SATISFIES
            # the constraint (zero penalty) earned zero reward too — no gradient toward improvement,
            # and a kink at the bare target instead of a smooth downhill through feasibility
            # (§1.13 / SC-3). Measuring the reward from `reward_boundary` makes it continuous with
            # the zero penalty at that boundary (both are 0 there) and monotonically increasing as
            # `curr` drops, so a MINIMIZE spec (power, area, …) always feels downward pressure while
            # feasible. EXCEED (Case 1 above) is treated symmetrically — reward measured from
            # target - tolerance — so both goals have a smooth gradient through their grace band.
            reward_boundary = target_val + tolerance
            if spec_curr_val < reward_boundary:
                spec_reward = compute_reward(curr_val=spec_curr_val, target_val=reward_boundary, reward_type=target_spec.reward_type, normalizing_coeff=normalizing_coeff)
            else:
                spec_reward = np.float64(0.0)
        # --------------------------
        # Case 3: Minimize the Target
        # --------------------------
        elif target_spec.goal == OptimizationGoalType.EXACT:
            spec_reward = np.float64(0.0)

        # --------------------------
        # Case 4: Invalid Goal Type
        # --------------------------
        else:
            logger.error(f"Unknown optimization goal type: {target_spec.goal}")
            raise ValueError(f"Unknown optimization goal type: {target_spec.goal}")
        # --------------------------

        spec_reward_weighted = spec_reward * np.float64(target_spec.weight)
        logger.debug(f"Computed Reward - Spec '{target_spec.name}': curr_val={curr_val}, target={target_spec.target}, reward={spec_reward}, weighted_reward={spec_reward_weighted} - (goal={target_spec.goal})")
        return spec_reward_weighted

# ------------------------------------------------
