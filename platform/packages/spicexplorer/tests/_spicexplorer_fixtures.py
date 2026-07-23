"""Shared test data and marks for spicexplorer.

Deliberately **not** a ``conftest.py``: the workspace test dirs are flat (no ``__init__.py``) so
every package's ``conftest`` shares the bare module name ``conftest``. In pytest's default
``prepend`` import mode the first one collected wins ``sys.modules['conftest']`` and shadows the
rest, so a ``from conftest import REPO_ROOT`` would resolve against a sibling package's conftest.
A package-unique module name (imported as ``from _spicexplorer_fixtures import REPO_ROOT``) cannot
collide. Mirrors the ``_gmid_fixtures`` pattern in spicexplorer-gmid.
"""
import shutil

import pytest
from spicexplorer_core import env, project_root

REPO_ROOT = project_root()
EXAMPLE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"
EXAMPLE_DUT_NETLIST = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
EXAMPLE_TB_NETLIST = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved_tb-loopgain.spice"


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
