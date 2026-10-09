"""Ax-based (Bayesian Optimization) optimizer backend.

The Bayesian twin of :mod:`spicexplorer.optimization.stochastic.nevergrad`. It reuses the
whole shared evaluation/scoring loop (``Base_Optimizer.optimize`` → ``evaluate`` →
``compute_fitness``) and only swaps the *proposer*: Ax's ``Client`` suggests each candidate
via a Gaussian-process surrogate instead of Nevergrad's evolutionary sampler.

Coordinate convention: Ax samples every parameter in the **same per-param coordinate
box** Nevergrad uses, so the shared ``Base_Optimizer.denormalize_params`` is the single
source of truth for both backends —

  * **frozen**  → excluded from the search space, re-injected at its fixed value;
  * **integer** → an Ax *integer* range over the PHYSICAL ``[min_val, max_val]`` (raw
    passthrough in ``denormalize_params``);
  * **log**     → a float range over the log box ``[log_bounds.min, log_bounds.max]`` with
    Ax ``scaling="log"`` (parity with Nevergrad's ``ng.p.Log``);
  * **linear**  → a float range over the lin box ``[lin_bounds.min, lin_bounds.max]``.

The Ax ``Client`` is configured to **maximize** the ``score`` objective directly (Nevergrad
instead minimizes ``-score``; both are correct — do not "fix" either sign). The optional
``ax`` extra is Python 3.11+ only; the orchestrator imports this module lazily so a missing
extra fails with an actionable message, not an ImportError stack.
"""

import logging
from collections.abc import Sequence
from typing import Any

import numpy as np

# Ax Imports
from ax.api.client import Client
from ax.api.configs import RangeParameterConfig
from ax.api.protocols.metric import IMetric
from ax.api.types import TParameterization
from spicexplorer.core.domains import OptimizationLogEntry, OptimizerType, Project_Setup
from spicexplorer.optimization.ax_tracking import extract_tracking_metrics
from spicexplorer.optimization.base import (
    Base_Optimizer,
    Spice_Constraint_Satisfaction,
    Spice_Single_Objective,
    _path_safe,
)

# Symxplorer Specific Imports
from spicexplorer_core.spice_engine import Simulator

logger = logging.getLogger("spicexplorer.optimization.stochastic.bayesian_ax")
logger.debug(f"imported {__name__}")


# ----------------------------
# --- Global Constants ---
# ----------------------------
SCORE_METRIC_NAME = "score"

# ----------------------------
# --- Class Definitions ---
# ----------------------------


# ------------------------------------------------
# A [ABSTRACT] Ax-client-based Optimizers
# ------------------------------------------------
class Ax_Client_Mixin(Base_Optimizer):
    """Reusable mixin for all Ax-based optimizers."""

    # --- Overwriting Some Abstract Methods ---
    def parameterize(self) -> list[RangeParameterConfig]:
        """Build the Ax search space with per-param branching, in the SAME coordinate boxes
        Nevergrad uses so the shared `denormalize_params` maps both backends identically."""
        # Frozen params are excluded here and re-injected at evaluation via the base seam.
        self._reset_frozen_params()
        ax_parameters: list[RangeParameterConfig] = []
        for param in self.setup_obj.dut_params:
            if self._register_frozen_param(param):
                continue
            if param.is_integer:
                # Sampled over the PHYSICAL integer range; `denormalize_params` passes it
                # through unchanged (parity with Nevergrad's `set_integer_casting()`).
                cfg = RangeParameterConfig(
                    name=param.name,
                    parameter_type="int",
                    bounds=(int(param.min_val), int(param.max_val)),
                )
            elif param.log_scale:
                # Log box (default [1,100]); Ax's geometric `scaling="log"` mirrors ng.p.Log.
                cfg = RangeParameterConfig(
                    name=param.name,
                    parameter_type="float",
                    bounds=self.optimizer_config.get_log_min_max(),
                    scaling="log",
                )
            else:
                cfg = RangeParameterConfig(
                    name=param.name,
                    parameter_type="float",
                    bounds=self.optimizer_config.get_lin_min_max(),
                )
            ax_parameters.append(cfg)
        self.parametrization: list[RangeParameterConfig] = ax_parameters
        return ax_parameters

    def _create_optimizer_obj(self) -> bool:
        if self.parametrization is None:
            logger.critical("NEED TO CALL self.parameterize")
            return False
        # (1) Ax - create the client
        client = Client(random_seed=self.optimizer_config.random_seed, storage_config=None)
        # (2) Ax - add the parameterization
        client.configure_experiment(parameters=self.parametrization, name="SpiceXplorer-Experiment")
        # (3) Ax - Configure the objective. A bare metric name MAXIMIZES it (a leading '-'
        #     would minimize); `evaluate` returns higher-is-better, so `score` is correct.
        client.configure_optimization(objective=SCORE_METRIC_NAME)
        # (4) Ax - Add tracking metrics (the target specs — diagnostics, not the objective)
        _tracking_metrics = self.get_tracking_metrics_from_config()
        client.configure_metrics(metrics=_tracking_metrics)
        # Set the optimizer object
        self.optimizer: Client = client
        # Candidates Ax has proposed but this loop hasn't drained yet (batched generation). Reset
        # per run so a resumed/re-created client never inherits a stale queue.
        self._trial_queue: list[tuple[int, TParameterization]] = []
        logger.info(f"Ax client ready (batch_size={self._ax_batch_size()}).")
        return True

    def _run_label(self) -> str:
        """`<project>_bayesian_ax`: Ax does not read `optimizer_config.name` (a YAML switched to Ax
        still carries e.g. `NGOpt`), so the checkpoint names carry the engine label, the one
        `OptimizeResult.optimizer` reports."""
        return f"{_path_safe(self.setup_obj.name)}_{OptimizerType.BAYESIAN_AX.value}"

    def _tell_prior_trials(self, prior_trials: Sequence[OptimizationLogEntry]) -> int:
        """Attach each prior trial to the Ax experiment (`attach_trial`) and complete it with the
        `raw_data` the loop would have sent (the score and the tracking metrics), so the surrogate
        is fitted on them and the generation strategy counts them."""
        told = 0
        for coords, score, entry in self._prior_coords(prior_trials):
            raw_data: dict[str, Any] = {SCORE_METRIC_NAME: score}
            raw_data = self.extract_tracking_metrics_from_metadata(
                metadata=entry.fit_summary or {}, save_in_dict=raw_data
            )
            try:
                trial_index = self.optimizer.attach_trial(parameters=coords)
                self.optimizer.complete_trial(trial_index=trial_index, raw_data=raw_data)
            except Exception as exc:  # Ax refuses the point: the run goes on without it
                logger.warning(f"a prior trial was not told to Ax: {exc!r}")
                continue
            told += 1
        return told

    def _ax_batch_size(self) -> int:
        """Trials Ax proposes per generation call — ``optimizer_kwargs.batch_size`` (default 1).

        1 is exact serial parity (the proven path). ``> 1`` asks Ax for a joint batch of candidates
        from the current surrogate; the loop still evaluates them one at a time. Read from the
        free-form ``optimizer_kwargs`` (the backend-knob bag) so no DSL/response-model schema changes."""
        kwargs = self.optimizer_config.optimizer_kwargs or {}
        try:
            n = int(kwargs.get("batch_size", 1))
        except (TypeError, ValueError):
            logger.warning("optimizer_kwargs.batch_size is not an int; falling back to 1.")
            n = 1
        return max(1, n)

    def optimization_step(self) -> tuple[dict[str, np.floating], np.floating, dict[str, Any]]:
        # Batched generation (``optimizer_kwargs.batch_size``, default 1 = serial parity): Ax proposes
        # `batch_size` candidates JOINTLY from the current surrogate; the shared base loop drains ONE
        # per step, so budget still counts individual trials and the per-step global-best tracking (one
        # log entry per step) is unchanged. The next batch is generated only once the queue empties — by
        # which point every trial in the previous batch is already completed — so draining/completing
        # order can never stale the next batch's generation (immediate vs deferred completion are
        # equivalent here). Evaluating a batch's candidates CONCURRENTLY would need per-candidate
        # wrappers (the shared, stateful testbench wrappers can't run two candidates at once) — a
        # documented further follow-up; batching today buys joint (space-filling) candidate proposals.
        if not self._trial_queue:
            trials = self.optimizer.get_next_trials(max_trials=self._ax_batch_size())
            if not trials:
                raise RuntimeError("Ax get_next_trials returned no candidates — cannot continue.")
            self._trial_queue = list(trials.items())
        trial_index, parameters = self._trial_queue.pop(0)

        # Map the Ax coordinate-space candidate to physical params, then re-inject any frozen params
        # (excluded from the Ax space) at their fixed value — same contract as Nevergrad, so the deck
        # is written with the full param set.
        denorm_params = self.denormalize_params(parameterization=parameters)
        denorm_params = self._reinject_frozen_params(denorm_params)
        # A non-finite candidate is ALWAYS a config bug (broken bounds, a sampler edge case) — injected
        # into a deck it becomes `w=nan` and every bench fails silently. Fail loudly (Nevergrad parity).
        bad = [
            k
            for k, v in denorm_params.items()
            if isinstance(v, (int, float, np.floating)) and not np.isfinite(v)
        ]
        if bad:
            raise RuntimeError(
                f"Ax produced non-finite values for {bad} "
                f"(budget {self.optimizer_config.budget}) — check optimizer_config bounds"
            )
        # Evaluate + score through the shared loop, then feed the result back to Ax.
        curr_score, metadata = self.evaluate(parameterization=denorm_params)
        raw_data: dict[str, Any] = {SCORE_METRIC_NAME: curr_score}
        raw_data = self.extract_tracking_metrics_from_metadata(
            metadata=metadata, save_in_dict=raw_data
        )
        self.optimizer.complete_trial(trial_index=trial_index, raw_data=raw_data)

        return parameters, curr_score, metadata

    # Helper methods
    def get_tracking_metrics_from_config(self) -> list[IMetric]:
        list_of_metrics: list[IMetric] = []
        for spec_name in self.optimizer_config.target_specs.list_target_names():
            list_of_metrics.append(IMetric(spec_name))
        return list_of_metrics

    def extract_tracking_metrics_from_metadata(
        self, metadata, save_in_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """Fold the trial's per-spec values into the Ax `raw_data` as tracking metrics.

        `metadata` is the `fit_summary` (bare spec keys in single mode, `"<corner>::<spec>"` in
        multi-corner mode). The fold itself is the ax-free
        `spicexplorer.optimization.ax_tracking.extract_tracking_metrics`, tested without the extra."""
        return extract_tracking_metrics(
            metadata,
            self.optimizer_config.target_specs.list_target_names(),
            save_in_dict=save_in_dict,
        )


# ------------------------------------------------
# B [ABSTRACT] Optimizers with Ax-client + custom-BoTorch Model
# ------------------------------------------------
class Ax_Custom_BoTorch_Mixin(Ax_Client_Mixin):
    """Not implemented: a named seam for a custom BoTorch `GenerationStrategy`, kept so
    the intent is discoverable; constructing its client raises rather than silently
    degrading to the default client."""

    def _create_optimizer_obj(self) -> bool:
        raise NotImplementedError(
            "Ax_Custom_BoTorch_Mixin (custom BoTorch generation strategy) is not implemented; "
            "use Ax_Spice_Constraint_Satisfaction / Ax_Spice_Single_Objective (default client)."
        )


# ------------------------------------------------
# B [USER-ENDPOINT] Ax-based Constraint Satisfaction
# ------------------------------------------------
class Ax_Spice_Constraint_Satisfaction(Ax_Client_Mixin, Spice_Constraint_Satisfaction):
    def __init__(
        self, setup_obj: Project_Setup, spicelib_wrappers: dict[str, Simulator], output_root=None
    ):
        # `spicelib_wrappers` (plural) + `output_root` mirror the Nevergrad endpoints so the
        # orchestrator/API runner construct every backend through ONE call surface (B1 fix).
        super().__init__(
            setup_obj=setup_obj, spicelib_wrappers=spicelib_wrappers, output_root=output_root
        )
        self.parametrization: list[RangeParameterConfig] | None = None
        logger.info(f"started the {__class__} optimizer class")


# ------------------------------------------------
# B [USER-ENDPOINT] Ax-based Single Objective Optimizer
# ------------------------------------------------
class Ax_Spice_Single_Objective(Ax_Client_Mixin, Spice_Single_Objective):
    def __init__(
        self, setup_obj: Project_Setup, spicelib_wrappers: dict[str, Simulator], output_root=None
    ):
        super().__init__(
            setup_obj=setup_obj, spicelib_wrappers=spicelib_wrappers, output_root=output_root
        )
        self.parametrization: list[RangeParameterConfig] | None = None
        logger.info(f"started the {__class__} optimizer class")
