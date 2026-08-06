"""Shared test data for spicexplorer-gmid.

Deliberately **not** a ``conftest.py`` (the workspace test dirs are flat and some packages do
``from conftest import …``; a second bare ``conftest`` would shadow theirs) and **not** a pytest
fixture (importing a fixture by name trips ruff F811 in every test that takes it as a parameter).
Instead this exposes one module-level ``DeviceTable`` — a read-only wrapper, so sharing it across
tests is safe and avoids re-loading the LUT per test. Import it: ``from _gmid_fixtures import NCH``.

The LUTs are copies of the committed analog-db sky130 / IHP NMOS tables (``fixtures/``) — no DB
import. ``NCH`` (sky130) peaks in gm/ID at the **edge** of the VGS grid; ``IHP_NCH`` (sg13g2) peaks
at an **interior** VGS on most slices, which is the case the reachability guard has to get right.

:func:`perturbed_lut` derives a *second, genuinely different* table from one of them. There is only
one finger width committed per device, so a finger-width test written against the same table twice
cannot fail (an inverted bracket weight and a ``_lerp`` that drops the hi table both stay green);
the perturbed copy is what makes the interpolation arithmetic observable.
"""

from __future__ import annotations

import pickle
from collections.abc import Mapping
from pathlib import Path

import numpy as np
from spicexplorer_gmid import DeviceTable

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SKY130_NCH = FIXTURES / "sky130_fd_pr__nfet_01v8__tt.pkl"
IHP_SG13_NCH = FIXTURES / "sg13_lv_nmos__tt.pkl"

NCH = DeviceTable.load(SKY130_NCH)
IHP_NCH = DeviceTable.load(IHP_SG13_NCH)


def perturbed_lut(
    dest: Path,
    *,
    src: Path = SKY130_NCH,
    scale: Mapping[str, float],
    headers: Mapping[str, object] | None = None,
) -> DeviceTable:
    """Write a copy of ``src`` with named stored arrays scaled, and load it as a ``DeviceTable``.

    A pygmid LUT is a plain dict of numpy arrays keyed by parameter name (``ID``/``GM``/``GDS``/
    ``CGG``/…) plus the ``L``/``VGS``/``VDS``/``VSB`` axes and the ``INFO``/``CORNER``/``TEMP``/
    ``NFING``/``W`` headers, and ``Lookup`` only reads it from a file — so a derived table is made
    by scaling the arrays and re-pickling. Scaling ``ID`` and ``GM`` by *different* factors moves
    every derived ratio the table exposes (GM_ID, ID_W, GM_GDS, GM_CGG, CGG_W, CDD_W), which is
    what a finger-width companion table looks like from the reader's side.
    """
    with Path(src).open("rb") as fh:
        lut = pickle.load(fh)
    for key, factor in scale.items():
        lut[key] = np.asarray(lut[key], dtype=float) * factor
    for key, value in (headers or {}).items():
        lut[key] = value
    with Path(dest).open("wb") as fh:
        pickle.dump(lut, fh)
    return DeviceTable.load(dest)
