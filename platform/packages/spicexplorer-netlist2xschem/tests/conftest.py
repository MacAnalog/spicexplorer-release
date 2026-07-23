"""Shared fixtures for the netlist2xschem tests — all host-runnable, no Docker, no PDK."""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import SymLibrary

FIXTURES = Path(__file__).parent / "fixtures"
SYM_ROOT = FIXTURES / "sym"


@pytest.fixture
def sym_lib() -> SymLibrary:
    """A hermetic symbol library over the checked-in ``tests/fixtures/sym/`` copies.

    Mirrors the vendored layout (``sg13g2_pr/*.sym`` + ``devices/*.sym``) so symbol parsing, pin
    alignment and emit are tested without depending on the platform's ``docker/`` tree being present.
    """
    return SymLibrary([SYM_ROOT])
