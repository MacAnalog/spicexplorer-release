"""This Module implements the nevergrad-based (evolutionary algorithms) optimizers """
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import nevergrad as ng
import numpy as np
from spicexplorer.core.domains import Project_Setup
from spicexplorer.optimization.base import (
    Base_Optimizer,
    Spice_Bode_Optimizer,
    Spice_Constraint_Satisfaction,
    Spice_Single_Objective,
)
from spicexplorer.optimization.stochastic.nevergrad_compat import apply_numpy2_metamodel_patch

# Symxplorer Specific Imports
from spicexplorer_core.spice_engine import Simulator

logger = logging.getLogger("spicexplorer.optimization.stochastic.nevergrad")
logger.debug(f'imported {__name__}')

# nevergrad <= 1.0.12 (the newest release) crashes with a numpy-2 `TypeError` the first time its
# metamodel engages -- for NGOpt a few hundred trials into a run, i.e. hours of SPICE thrown away
# (ledger E-052). Upstream fixed it on `main` but has cut no release, so there is no version floor
# to raise; the backport is applied here, at import of the Nevergrad backend, so EVERY path that
# constructs a Nevergrad optimizer (orchestrator, API runner, notebooks) gets it. A no-op on a
# nevergrad that does not carry the bug. See `nevergrad_compat`.
apply_numpy2_metamodel_patch()


# ----------------------------
# --- Global Constants ---
# ----------------------------


# ----------------------------
# --- Function Definitions ---
# ---------------------------

def create_optimizer(
    optimizer_name: str,
    parametrization: ng.p.Dict,
    budget: int,
    optimizer_kwargs: Optional[Dict[str, Any]] = None,
    random_seed: Optional[int] = None
) -> ng.optimizers.base.Optimizer:
    """
    Factory function to instantiate a Nevergrad optimizer from configuration.

    Handles two cases:
    1. Families: Configurable classes (e.g. DifferentialEvolution, ParametrizedCMA).
       These require a two-step init: Family(**kwargs) -> Optimizer(params, budget).
    2. Registry: Pre-configured strings (e.g. 'NGOpt', 'TwoPointsDE').
       These are instantiated directly: RegistryKey(params, budget, **kwargs).
    """
    if optimizer_kwargs is None:
        optimizer_kwargs = {}

    # 1. Set Random Seed (Global for the parametrization)
    if random_seed is not None:
        parametrization.random_state = np.random.RandomState(random_seed)

    # Make a copy of kwargs to avoid mutating the original config
    kwargs = optimizer_kwargs.copy()

    # `batch_size` is an Ax-only knob (candidates per generation call); Nevergrad has no batched
    # generation, and its registry PRESETS (e.g. NGOpt) reject unknown kwargs — so drop it here.
    # A YAML shared between backends can carry `optimizer_kwargs.batch_size` without breaking this one.
    kwargs.pop('batch_size', None)

    # Extract 'num_workers' (common to all, defaults to 1)
    num_workers = kwargs.pop('num_workers', 1)

    # -------------------------------------------------------------------------
    # CASE A: CONFIGURABLE FAMILIES
    # Check if the name exists in ng.families (e.g., "DifferentialEvolution")
    # -------------------------------------------------------------------------
    if hasattr(ng.families, optimizer_name):
        try:
            # 1. Get the Family Class
            family_class = getattr(ng.families, optimizer_name)

            # Nevergrad's sampling Rescaler normalizes across the planned sample
            # grid — with budget 1 that is a single point, so it divides by zero
            # and every candidate comes out NaN (which then lands as `w=nan` in
            # the SPICE deck). Rescaling is meaningless for <2 samples anyway.
            if kwargs.get("rescaled") and budget < 2:
                logger.warning(
                    f"'{optimizer_name}': dropping rescaled=True — rescaled sampling "
                    f"needs a budget of at least 2 (got {budget}); it would produce "
                    "NaN candidates."
                )
                kwargs = {k: v for k, v in kwargs.items() if k != "rescaled"}

            # 2. Configure the Family (Pass algorithmic settings like 'popsize', 'crossover')
            #    Any argument that the Family constructor doesn't accept will raise a TypeError here.
            optimizer_factory = family_class(**kwargs)

            # 3. Instantiate the Optimizer (Pass execution settings)
            optimizer = optimizer_factory(
                parametrization=parametrization,
                budget=budget,
                # num_workers=num_workers # FIXME: Do not enforce num_workers for now.
            )

            logger.info(f"Initialized Family '{optimizer_name}' with config: {kwargs}")
            return optimizer

        except TypeError as e:
            logger.error(f"Invalid argument provided for Family '{optimizer_name}': {e}")
            raise

    # -------------------------------------------------------------------------
    # CASE B: REGISTRY PRESETS
    # Check if the name exists in the registry (e.g., "NGOpt", "TwoPointsDE")
    # -------------------------------------------------------------------------
    registry = ng.optimizers.registry.get(optimizer_name)
    if registry is not None:
        # Registry optimizers are instantiated directly.
        # Note: They typically do NOT accept algorithmic kwargs (like 'crossover').
        # If kwargs contains something the registry opt doesn't support, it might crash or ignore it.
        try:
            optimizer = registry(
                parametrization=parametrization,
                budget=budget,
                num_workers=num_workers,
                **kwargs # Passing remaining kwargs (rarely used for registry items)
            )
            logger.info(f"Initialized Registry Optimizer '{optimizer_name}'")
            return optimizer
        except TypeError as e:
            if not kwargs:
                raise
            # Registry presets are pre-configured and reject algorithmic kwargs
            # (a config authored for a Family, or leftover kwargs after an
            # ephemeral algorithm override). Dropping them and running the preset
            # as-is beats failing the whole run before a single trial.
            logger.warning(
                f"Optimizer '{optimizer_name}' rejected extra arguments {kwargs} ({e}). "
                "Registry presets are pre-configured — running WITHOUT these kwargs. "
                "Use the Family Name instead if you want to configure it."
            )
            optimizer = registry(
                parametrization=parametrization,
                budget=budget,
                num_workers=num_workers,
            )
            logger.info(f"Initialized Registry Optimizer '{optimizer_name}' (kwargs dropped)")
            return optimizer

    # -------------------------------------------------------------------------
    # CASE C: FAILURE
    # -------------------------------------------------------------------------
    raise ValueError(
        f"Optimizer '{optimizer_name}' not found in 'ng.families' or 'ng.optimizers.registry'.\n"
        f"Available Families: {[x for x in dir(ng.families) if not x.startswith('_')]}\n"
    )

# ----------------------------
# --- Class Definitions ---
# ----------------------------

# ------------------------------------------------
# A [ABSTRACT] Nevergrad-based Optimizers
# ------------------------------------------------
class NevergradMixin(Base_Optimizer):
    """Reusable mixin for all Nevergrad-based optimizers."""
    # --- Overwriting Some Abstract Methods ---
    def parameterize(self) -> ng.p.Dict:
        parameters: Dict[str, ng.p.Scalar] = {}
        # Frozen params are excluded from the search space and injected at their fixed value
        # during evaluation via the shared base seam — same contract in every backend.
        self._reset_frozen_params()

        for param in self.setup_obj.dut_params:
            if self._register_frozen_param(param):
                continue
            if param.is_integer:
                p_obj = ng.p.Scalar(
                    lower=param.min_val,
                    upper=param.max_val)
                p_obj.set_integer_casting()

            elif param.log_scale:
                 p_obj = ng.p.Log(
                    lower=self.optimizer_config.log_variable_bounds.min,
                    upper=self.optimizer_config.log_variable_bounds.max)
            else:
                p_obj = ng.p.Scalar(
                    lower=self.optimizer_config.lin_variable_bounds.min,
                    upper=self.optimizer_config.lin_variable_bounds.max)

            parameters[param.name] = p_obj

        self.parametrization = ng.p.Dict(**parameters)
        return self.parametrization

    def _create_optimizer_obj(self) -> bool:
        if self.parametrization is None:
            logger.critical("NEED TO CALL self.parameterize")
            return False

        try:
            self.optimizer = create_optimizer(
                optimizer_name=self.optimizer_config.name,
                parametrization=self.parametrization,
                budget=self.optimizer_config.budget,
                optimizer_kwargs=self.optimizer_config.optimizer_kwargs,
                random_seed=self.optimizer_config.random_seed
            )

            # Optional: seed the search with the dut_params' `init` point (opt-in via
            # `optimizer_config.seed_from_init`), so the first ask() is the known baseline.
            if getattr(self.optimizer_config, "seed_from_init", False):
                self._suggest_init_point()

            return True

        except Exception as e:
            logger.critical(f"Failed to create optimizer: {e}")
            return False

    def _suggest_init_point(self) -> None:
        """`optimizer.suggest(...)` the dut_params' `init` values (in the search space's own
        normalized coordinates) so that point is evaluated early in the run. `suggest()` is a HINT
        to Nevergrad, not a queue: with `num_workers == 1` and most algorithms it is the first
        `ask()`, but with parallel workers / TwoPointsDE it has been observed as trial 4 — read
        the init trial back from the log by its params, do not assume index 0. A searched param
        without `init` keeps the parametrization's default value; frozen params are not in the
        space. Integer params live in physical units (see `parameterize`)."""
        if self.parametrization is None or self.optimizer is None:
            return
        cfg = self.optimizer_config
        lin, log = cfg.lin_variable_bounds, cfg.log_variable_bounds
        assert lin is not None and log is not None  # defaulted in OptimizerConfig.__post_init__
        point: Dict[str, Any] = dict(self.parametrization.value)
        n_seeded = 0
        for param in self.setup_obj.dut_params:
            if param.name not in point or param.init is None:
                continue
            init = float(param.init)  # type: ignore[arg-type]  (resolved to a number by from_yaml)
            lo = float(param.min_val)  # type: ignore[arg-type]
            hi = float(param.max_val)  # type: ignore[arg-type]
            if param.is_integer:
                point[param.name] = int(round(init))
            elif param.log_scale:
                x = (np.log10(init) - np.log10(lo)) / (np.log10(hi) - np.log10(lo))
                point[param.name] = float(log.min + x * (log.max - log.min))
            else:
                x = (init - lo) / (hi - lo)
                point[param.name] = float(lin.min + x * (lin.max - lin.min))
            n_seeded += 1
        if n_seeded:
            self.optimizer.suggest(point)
            logger.info(f"seed_from_init: suggested the `init` point for {n_seeded} dut_param(s)")

    def optimization_step(self) -> Tuple[Dict[str, np.floating] , np.floating , Dict[str, Any]]:
        # Get a new candidate
        candidate : ng.p.Parameter = self.optimizer.ask()
        # Evaluate function
        denorm_params: Dict[str, float] = self.denormalize_params(parameterization=candidate.value)
        # A non-finite candidate is ALWAYS a config bug (broken bounds, a sampler
        # edge case, …) — injected into a deck it becomes `w=nan`, every bench
        # fails, and the trial silently scores as an all-penalty point. Fail the
        # run loudly instead.
        bad = [k for k, v in denorm_params.items()
               if isinstance(v, (int, float, np.floating)) and not np.isfinite(v)]
        if bad:
            raise RuntimeError(
                f"optimizer '{self.optimizer_config.name}' produced non-finite values for "
                f"{bad} (kwargs {self.optimizer_config.optimizer_kwargs}, "
                f"budget {self.optimizer_config.budget}) — check optimizer_config"
            )
        # Re-inject any frozen params (excluded from the search space) at their fixed value.
        denorm_params = self._reinject_frozen_params(denorm_params)
        curr_score, metadata = self.evaluate(parameterization=denorm_params)
        # Provide feedback to optimizer (The negative of the fitness score is used because the optimizer is set to minimize this value... this way the optimizer will maximize the fitness score.
        self.optimizer.tell(candidate, -1 * curr_score)
        return candidate.value, curr_score, metadata

# ------------------------------------------------
# B [USER-ENDPOINT] Nevergrad-based Bode Fitter
# ------------------------------------------------
class Nevergrad_Spice_Bode_Optimizer(NevergradMixin, Spice_Bode_Optimizer):
    pass

# ------------------------------------------------
# B [USER-ENDPOINT] Nevergrad-based Constraint Satisfaction
# ------------------------------------------------
class Nevergrad_Spice_Constraint_Satisfaction(NevergradMixin, Spice_Constraint_Satisfaction):
    def __init__(self,
                 setup_obj: Project_Setup,
                 spicelib_wrappers : Dict[str, Simulator],
                 output_root: Path | None = None):
        # Accept + forward output_root so per-run checkpoint isolation works for this endpoint too,
        # matching Nevergrad_Spice_Single_Objective (BUG-B26).
        super().__init__(setup_obj = setup_obj, spicelib_wrappers = spicelib_wrappers,
                         output_root = output_root)
        self.parametrization: ng.p.Dict | None = None
        logger.info(f"started the {__class__} optimizer class")
# ------------------------------------------------
# B [USER-ENDPOINT] Nevergrad-based Single Objective Optimizer
# ------------------------------------------------
class Nevergrad_Spice_Single_Objective(NevergradMixin, Spice_Single_Objective):
    def __init__(self,
                 setup_obj: Project_Setup,
                 spicelib_wrappers : Dict[str, Simulator],
                 output_root: Path | None = None):
        super().__init__(setup_obj = setup_obj, spicelib_wrappers = spicelib_wrappers, output_root = output_root)
        self.parametrization: ng.p.Dict | None = None
        logger.info(f"started the {__class__} optimizer class")
