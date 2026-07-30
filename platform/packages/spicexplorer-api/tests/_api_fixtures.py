"""Shared test data, marks, and a no-op optimizer for spicexplorer-api.

Deliberately **not** a ``conftest.py``: the workspace test dirs are flat (no ``__init__.py``) so
every package's ``conftest`` shares the bare module name ``conftest``. In pytest's default
``prepend`` import mode the first one collected wins ``sys.modules['conftest']`` and shadows the
rest, so a ``from conftest import REPO_ROOT`` would resolve against a sibling package's conftest.
A package-unique module name (imported as ``from _api_fixtures import REPO_ROOT``) cannot collide.
Mirrors the ``_gmid_fixtures`` pattern in spicexplorer-gmid.
"""
import shutil
from typing import Any, Dict, Tuple

import numpy as np
import pytest
from spicexplorer.optimization.base import Base_Optimizer
from spicexplorer_core import project_root

REPO_ROOT = project_root()
EXAMPLE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"
EXAMPLE_DUT_NETLIST = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
EXAMPLE_TB_NETLIST = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved_tb-loopgain.spice"


def _ngspice_available() -> bool:
    return shutil.which("ngspice") is not None


requires_ngspice = pytest.mark.skipif(
    not _ngspice_available(),
    reason="ngspice binary not found in PATH",
)

slow = pytest.mark.slow


class _NoopOpt(Base_Optimizer):
    """Concrete Base_Optimizer with no-op abstracts — shared no-op optimizer for tests."""
    def _create_optimizer_obj(self) -> bool:
        return True

    def parameterize(self) -> Any:
        return {}

    def evaluate(self, parameterization: Dict[str, float]) -> Tuple[np.floating, Dict[str, Any]]:
        return np.float64(0.0), {}

    def compute_fitness(self, performance_array):
        return np.float64(0.0), {}

    def optimization_step(self):
        return {}, np.float64(0.0), {}

    def plot_solution(self, parameterization, **kwargs):
        return None
