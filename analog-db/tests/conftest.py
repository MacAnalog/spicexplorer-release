"""Session-scoped corpus artifacts + the ``corpus`` marker.

The corpus sweeps (a full ``raw/`` render and the verify tiers) each walk every
circuit in the registry; profiling showed the suite used to re-run them up to
six times across test modules — once per asserting file — which dominated the
whole fast tier's wall clock. Each sweep is computed ONCE per pytest session
here and shared read-only. A test whose *point* is a fresh invocation (the
determinism check) still calls the generator itself and compares against the
shared render.

Marker taxonomy (registered in pyproject.toml):

- (no marker)  — unit tests of the package code on a couple of representative
  circuits; seconds. The everyday dev loop: ``pytest -m "not corpus and not slow"``.
- ``corpus``   — corpus-wide sweeps and per-binding parametrized checks that
  scale with the number of circuits. Part of the default / release gate run.
- ``slow``     — live ngspice + PDK simulation or xschem round-trip; opt-in
  (``-m slow``) exactly as before.
"""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import export, verify


@pytest.fixture(scope="session")
def generated_decks() -> dict[str, str]:
    """One full-corpus render, shared by every test that asserts on the deck set."""
    decks, _skipped = export.generate_all()
    return decks


@pytest.fixture(scope="session")
def tier0_results() -> list[verify.CheckResult]:
    return verify.run_tier0()


@pytest.fixture(scope="session")
def tier1_results() -> list[verify.CheckResult]:
    return verify.run_tier1()


@pytest.fixture(scope="session")
def tier2_results() -> list[verify.CheckResult]:
    return verify.run_tier2()
