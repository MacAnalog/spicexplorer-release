"""The Circuit Optimization Module"""
# Module imports
from .orchestrator import (
    SPICE_OPTIMIZER_CLASSES,
    Circuit_Optimizer_Orchestrator_with_SPICE,
    Optimizer_Type_Enum,
)
from .sim_benchmark import SimTimeReport, TestbenchSimTiming, benchmark_simulators
from .stochastic.nevergrad import (
    Nevergrad_Spice_Bode_Optimizer,
    Nevergrad_Spice_Constraint_Satisfaction,
    Nevergrad_Spice_Single_Objective,
)

# ------------------ Module Exports ------------------

__all__ = [
    # --------------------------------
    # One endpoint for all optimizer types
    'SPICE_OPTIMIZER_CLASSES',
    'Optimizer_Type_Enum',
    'Circuit_Optimizer_Orchestrator_with_SPICE',
    # --------------------------------
    # Per-testbench sim-time benchmarking
    'SimTimeReport',
    'TestbenchSimTiming',
    'benchmark_simulators',
    # --------------------------------

    # ** For backward compatability **
    # --------------------------------
    # => Evolutionary-based Optimizers
    'Nevergrad_Spice_Bode_Optimizer',
    'Nevergrad_Spice_Constraint_Satisfaction',
    'Nevergrad_Spice_Single_Objective',
    # => BO-based Optimizers
    'Ax_Spice_Constraint_Satisfaction',
    'Ax_Spice_Single_Objective'
    # --------------------------------
    ]


def __getattr__(name: str):
    if name in {"Ax_Spice_Constraint_Satisfaction", "Ax_Spice_Single_Objective"}:
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
        return {
            "Ax_Spice_Constraint_Satisfaction": Ax_Spice_Constraint_Satisfaction,
            "Ax_Spice_Single_Objective": Ax_Spice_Single_Objective,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
