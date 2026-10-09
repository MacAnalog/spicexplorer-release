"""Shared test data and marks for spicexplorer.

Deliberately **not** a ``conftest.py``: the workspace test dirs are flat (no ``__init__.py``) so
every package's ``conftest`` shares the bare module name ``conftest``. In pytest's default
``prepend`` import mode the first one collected wins ``sys.modules['conftest']`` and shadows the
rest, so a ``from conftest import REPO_ROOT`` would resolve against a sibling package's conftest.
A package-unique module name (imported as ``from _spicexplorer_fixtures import REPO_ROOT``) cannot
collide. Mirrors the ``_gmid_fixtures`` pattern in spicexplorer-gmid.
"""

import importlib
import importlib.metadata
import shutil
from types import ModuleType

import pytest
from spicexplorer_core import env, project_root

REPO_ROOT = project_root()
EXAMPLE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"
EXAMPLE_DUT_NETLIST = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
EXAMPLE_TB_NETLIST = (
    REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved_tb-loopgain.spice"
)


def _ngspice_available() -> bool:
    return shutil.which("ngspice") is not None


def _pdk_available() -> bool:
    """True only when the IHP sg13g2 model lib actually resolves (a real sim can run).

    Distinct from ``_ngspice_available``: this host has ngspice but no PDK, so a test that
    runs a live simulation against the example netlists aborts (unresolved ``.lib``) rather
    than skips. Gate such tests on this so they skip cleanly off-PDK (e.g. the native Mac)
    and still run where the PDK is present (the Docker stack / CI). See ``env.probe_pdk``.
    """
    return bool(env.probe_pdk().get("pdk_ok"))


requires_ngspice = pytest.mark.skipif(
    not _ngspice_available(),
    reason="ngspice binary not found in PATH",
)

requires_pdk = pytest.mark.skipif(
    not _pdk_available(),
    reason="IHP sg13g2 PDK not found — live SPICE simulation unavailable (run in the Docker stack)",
)

slow = pytest.mark.slow

# The Ax-backend cases carry `@pytest.mark.ax` (registered in the root pyproject.toml), so
# `-m ax` selects them. Each one imports the backend through `require_ax()`, never
# `pytest.importorskip("ax")`: `test_ax_backend.py` pins both.
AX_BACKEND_MODULE = "spicexplorer.optimization.stochastic.bayesian_ax"


def ax_extra_installed() -> bool:
    """True when the optional ``ax`` extra's distribution is installed (``uv sync --extra ax``)."""
    try:
        importlib.metadata.distribution("ax-platform")
    except importlib.metadata.PackageNotFoundError:
        return False
    return True


def require_ax() -> ModuleType:
    """Import the Ax backend for an ``ax`` test; skip only when the optional extra is absent.

    ``pytest.importorskip("ax")`` skipped on ANY import failure, so with the extra installed but
    broken (a torch/botorch mismatch) every Ax case reported as skipped and a lane that synced
    the extra still passed (OPT-F1). With ``ax-platform`` installed an import failure fails."""
    try:
        return importlib.import_module(AX_BACKEND_MODULE)
    except ImportError as exc:
        if ax_extra_installed():
            pytest.fail(
                f"the ax extra (ax-platform) is installed but {AX_BACKEND_MODULE} does "
                f"not import: {exc!r}",
                pytrace=False,
            )
        pytest.skip(f"could not import ax ({exc}); install the optional extra: uv sync --extra ax")
