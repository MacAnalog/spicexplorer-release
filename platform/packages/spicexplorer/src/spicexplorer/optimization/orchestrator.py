"""This Module implements the user endpoint for selecting optimizers types based on an input project_setup yaml file and optimization engine type"""
import logging
import os
from abc import ABC, abstractmethod

# Third-party imports
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Type

from spicexplorer.core.domains import OptimizerType, Project_Setup

# Symxplorer Specific Imports
from spicexplorer_core.spice_engine import Sim_Execution_Type, Simulator

from .base import Base_Optimizer, Spice_Base_Optimizer
from .simulator_factory import build_simulator, resolve_engine
from .stochastic.nevergrad import (
    Nevergrad_Spice_Bode_Optimizer,
    Nevergrad_Spice_Constraint_Satisfaction,
    Nevergrad_Spice_Single_Objective,
)

# ------------------ Module Logger ------------------

logger = logging.getLogger("spicexplorer.optimization.orchestrator")


def _load_ax_optimizer_classes() -> tuple[Type[Spice_Base_Optimizer], Type[Spice_Base_Optimizer]]:
    """Import Ax-backed optimizers only when the Ax extra is installed."""
    try:
        from .stochastic.bayesian_ax import (
            Ax_Spice_Constraint_Satisfaction,
            Ax_Spice_Single_Objective,
        )
    except ImportError as exc:
        raise ImportError(
            "Ax optimizers require the optional 'ax' dependencies. "
            "Install them with `uv sync --extra ax`."
        ) from exc
    return Ax_Spice_Constraint_Satisfaction, Ax_Spice_Single_Objective


# ------------------ Enums ------------------
class Optimizer_Type_Enum(Enum):
    BAYESIAN = "bayesian"
    EVOLUTIONARY = "evolutionary"
    NEVERGRAD_BODE = "nevergrad_bode"
    NEVERGRAD_CONSTRAINT = "nevergrad_constraint"
    NEVERGRAD_SINGLE = "nevergrad_single"
    AX_CONSTRAINT = "ax_constraint"
    AX_SINGLE = "ax_single"

SPICE_OPTIMIZER_CLASSES : Dict[Optimizer_Type_Enum, Callable[[], Type[Spice_Base_Optimizer]] | Type[Spice_Base_Optimizer]] = {
    Optimizer_Type_Enum.NEVERGRAD_BODE: Nevergrad_Spice_Bode_Optimizer,
    Optimizer_Type_Enum.NEVERGRAD_CONSTRAINT: Nevergrad_Spice_Constraint_Satisfaction,
    Optimizer_Type_Enum.NEVERGRAD_SINGLE: Nevergrad_Spice_Single_Objective,
    Optimizer_Type_Enum.AX_CONSTRAINT: lambda: _load_ax_optimizer_classes()[0],
    Optimizer_Type_Enum.AX_SINGLE: lambda: _load_ax_optimizer_classes()[1],
}

# The ONE place the DSL's `optimizer_config.type` (the engine selector every shipped
# YAML carries) maps to a concrete optimizer backend. Both the orchestrator and the API
# runner resolve through this, so flipping `type:` between `nevergrad` and `bayesian_ax`
# swaps the engine in every lane. `name` stays the backend-specific algorithm knob
# (Nevergrad: NGOpt/TinyCMA/…). Both engines default to the single-objective endpoint (the
# constraint-satisfaction landscape plus the satisfied-spec reward — the shipped convention).
_ENGINE_TO_OPTIMIZER: Dict[OptimizerType, Optimizer_Type_Enum] = {
    OptimizerType.NEVERGRAD: Optimizer_Type_Enum.NEVERGRAD_SINGLE,
    OptimizerType.BAYESIAN_AX: Optimizer_Type_Enum.AX_SINGLE,
}


def optimizer_type_from_config(project_setup: Project_Setup) -> Optimizer_Type_Enum:
    """Resolve a project's `optimizer_config.type` to the optimizer backend to construct.

    Fails loud on an unknown/unsupported engine (a bad `type:`, or `reinforcement_learning`
    which is still dormant) so a typo surfaces at load, not as a silent Nevergrad fallback."""
    raw = str(getattr(project_setup.optimizer_config, "type", "") or "").strip().lower()
    try:
        engine = OptimizerType(raw)
    except ValueError as exc:
        valid = [t.value for t in OptimizerType]
        raise ValueError(
            f"optimizer_config.type={raw!r} is not a known engine; choose one of {valid}."
        ) from exc
    backend = _ENGINE_TO_OPTIMIZER.get(engine)
    if backend is None:
        raise ValueError(
            f"optimizer_config.type={engine.value!r} has no optimizer backend wired "
            f"(the RL backend is dormant); choose 'nevergrad' or 'bayesian_ax'."
        )
    return backend

# ------------------ Classes ------------------

class Circuit_Optimizer_Orchestrator_Base(ABC):
    def __init__(self, project_setup_path: str | Path, optimizer_type: Optimizer_Type_Enum | None = None, auto_load: bool = True,verbose: bool = False):
        self.project_setup_path = project_setup_path
        self.verbose = verbose

        self.project_setup:     Project_Setup   = self.read_project_setup()
        logger.debug(f"created the project setup for {self.project_setup.name}")

        # Engine selection: an explicit `optimizer_type` wins (back-compat with callers that
        # pass one), otherwise resolve the DSL's `optimizer_config.type` — so a YAML
        # carrying `type: bayesian_ax` launches Ax with no code change.
        self.optimizer_type: Optimizer_Type_Enum = (
            optimizer_type if optimizer_type is not None
            else optimizer_type_from_config(self.project_setup)
        )
        logger.info(f"engine resolved to {self.optimizer_type.value} "
                    f"(optimizer_config.type={self.project_setup.optimizer_config.type!r})")

        if auto_load:
            self.initialize()

    def initialize(self):
        self.spicelib_wrappers:  Dict[str, Simulator] = self.create_spicelib_wrappers()
        logger.debug("created the spicelib_wrapper.")


    def read_project_setup(self) -> Project_Setup:
        # Load the project setup information
        try:
            PROJECT_SETUP = Project_Setup.from_yaml(yaml_path=self.project_setup_path)
        except Exception as e:
            logger.critical(
                f"Failed to load project setup from '{self.project_setup_path}': {e.__class__.__name__}: {e}"
            )
            raise RuntimeError(
                f"Error loading project setup from '{self.project_setup_path}'. "
                f"Check if the file exists, is valid YAML, and has correct structure."
            ) from e
        return PROJECT_SETUP

    def create_spicelib_wrappers(self) -> Dict[str, Simulator]:
        PROJECT_SETUP = self.project_setup

        netlist_filename = Path(PROJECT_SETUP.ws_root) / Path(PROJECT_SETUP.netlist)
        output_folder    = Path(PROJECT_SETUP.ws_root) / Path(PROJECT_SETUP.outdir)
        sim_execution_t  = Sim_Execution_Type.RUN_AND_WAIT  # only RUN_AND_WAIT is supported as of now...
        path_to_simulator=Path(PROJECT_SETUP.simulator)

        # P4: dispatch on the project's engine selector (default 'ngspice', fully
        # backward-compatible). The optimizer loop consumes the `Simulator` protocol,
        # so whatever the factory returns flows through evaluate/optimize unchanged.
        # (A spectre selection still needs a .scs netlist + the installed bridge —
        # the factory raises actionable errors for both, see _build_spectre.)
        engine = resolve_engine(getattr(PROJECT_SETUP, "sim_engine", None))
        is_spectre = engine.value == "spectre"
        # Profile pin for the Spectre bridge + OCEAN session (the bridge's own
        # `.env` discovery otherwise beats env vars — P0 finding). Same env var the
        # opt-in live tests use; None on the ngspice path.
        vb_env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE") if is_spectre else None

        logger.info("=============================================================================")
        logger.info(f"project: {PROJECT_SETUP.name} has ({len(PROJECT_SETUP.testbenches)}) testbenches.")
        logger.info(f"\tsim_engine {engine.value}")
        logger.debug(f"\tpath_to_simulator {PROJECT_SETUP.simulator}")
        logger.debug(f"\tDUT netlist {netlist_filename}")
        logger.debug(f"\toutput_folder {output_folder}")


        # Create the Spice Simulator Wrapper for each testbench
        logger.debug("Creating spicelib_wrappers for each testbench...")
        logger.debug("-----------------------------------------------------------------------------")
        spicelib_wrappers : Dict[str, Simulator] = {}

        for i, tb in enumerate(PROJECT_SETUP.testbenches):
            if not tb.enable:
                logger.info(f"({i+1}) Skipping disabled testbench: {tb.name} - {tb.description}")
                continue

            logger.debug(f"({i+1}) Creating spicelib_wrapper for testbench: {tb.name} - {tb.description}")
            logger.debug("\tspicelib_wrapper will use the following configs:")
            logger.debug(f"\t- testbench_name {tb.name}")
            logger.debug(f"\t- netlist_filename {tb.netlist}")

            # Spectre-only per-testbench dirs: the bridge persists the PSF raw under
            # `work_dir` (OCEAN reads it); each candidate's injected `.scs` lands under
            # `deck_dir`. Left None for ngspice (its builder ignores them → byte-identical runs).
            work_dir = deck_dir = None
            if is_spectre:
                tb_root = output_folder / "spectre" / tb.name
                work_dir = tb_root / "raw"
                deck_dir = tb_root / "decks"
                work_dir.mkdir(parents=True, exist_ok=True)
                deck_dir.mkdir(parents=True, exist_ok=True)

            wrapper = build_simulator(
                engine,
                testbench_name=tb.name,
                netlist_filename=Path(PROJECT_SETUP.ws_root) / Path(tb.netlist),
                output_folder=output_folder,
                sim_execution_t=sim_execution_t,
                path_to_simulator=path_to_simulator,
                verbose=self.verbose,
                work_dir=work_dir,
                deck_dir=deck_dir,
                vb_env_file=vb_env_file,
            )
            spicelib_wrappers[tb.name] = wrapper
            logger.debug(f"Created spicelib_wrapper for testbench: {tb.name}")
        logger.debug("-----------------------------------------------------------------------------")
        logger.info(f"Created ({len(spicelib_wrappers)}) spicelib_wrappers for project: {PROJECT_SETUP.name}")
        logger.info("=============================================================================")
        return spicelib_wrappers

    def get_project_setup(self) -> Project_Setup:
        return self.project_setup

    def get_spicelib_wrapper(self) -> Dict[str, Simulator]:
        return self.spicelib_wrappers

    @abstractmethod
    def get_optimizer(self) -> Base_Optimizer:
        pass


class Circuit_Optimizer_Orchestrator_with_SPICE(Circuit_Optimizer_Orchestrator_Base):
    def get_optimizer(self) -> Spice_Base_Optimizer:
        logger.info(f"creating the circuit_optimizer of type {self.optimizer_type.value}")
        optimizer_factory = SPICE_OPTIMIZER_CLASSES[self.optimizer_type]
        optimizer_cls = optimizer_factory() if callable(optimizer_factory) and not isinstance(optimizer_factory, type) else optimizer_factory
        circuit_optimizer = optimizer_cls(
            spicelib_wrappers=self.spicelib_wrappers,
            setup_obj=self.project_setup
        )
        logger.info(f"created the circuit_optimizer; type {type(circuit_optimizer)}")
        return circuit_optimizer

    def run_sanity_on_spicelib_wrapper(self, use_editor: bool = True)-> bool:
        for tb_name, spicelib_wrapper in self.spicelib_wrappers.items():
            # `run_sanity_check` is an ngspice-wrapper extra, not part of the
            # `Simulator` protocol — a backend without one has nothing to sanity-run.
            checker = getattr(spicelib_wrapper, "run_sanity_check", None)
            if not callable(checker):
                logger.info(f"backend for testbench {tb_name} has no run_sanity_check; skipping")
                continue
            logger.info(f"running sanity check on spicelib_wrapper for testbench: {tb_name}")
            if not checker(use_editor=use_editor, sim_execution_t=Sim_Execution_Type.RUN_NOW):
                logger.warning(f"sanity check failed for spicelib_wrapper for testbench: {tb_name}")
                return False
        logger.info("HOORAY! sanity check passed for all spicelib_wrappers.")
        return True
