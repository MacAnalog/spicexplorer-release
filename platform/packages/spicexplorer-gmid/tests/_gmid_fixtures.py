"""Shared test data for spicexplorer-gmid.

Deliberately **not** a ``conftest.py`` (the workspace test dirs are flat and some packages do
``from conftest import …``; a second bare ``conftest`` would shadow theirs) and **not** a pytest
fixture (importing a fixture by name trips ruff F811 in every test that takes it as a parameter).
Instead this exposes one module-level ``DeviceTable`` — a read-only wrapper, so sharing it across
tests is safe and avoids re-loading the LUT per test. Import it: ``from _gmid_fixtures import NCH``.

The LUT is a copy of the committed analog-db sky130 NMOS table (``fixtures/``) — no DB import.
"""

from pathlib import Path

from spicexplorer_gmid import DeviceTable

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SKY130_NCH = FIXTURES / "sky130_fd_pr__nfet_01v8__tt.pkl"

NCH = DeviceTable.load(SKY130_NCH)
