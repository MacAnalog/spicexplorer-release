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

The PMOS tables are **synthetic** — :func:`synthetic_pmos_lut`, built in memory at import, no kit
file and no copy of one. ``PCH`` is shaped like the sky130 pfet (gm/ID peaks at the VGS=0 grid
edge), ``IHP_PCH`` like the IHP lv pmos (a leakage floor pulls the peak to an interior VGS). Both
store what the extractor writes for a pmos: every bias axis and ``ID`` as a positive magnitude.
"""

from __future__ import annotations

import math
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


# ----- synthetic PMOS tables (the |ID| / |VSB| convention, no kit data) --------------------------

UT_300K = 0.025852  # kT/q at 300 K [V]


def synthetic_pmos_lut(
    *,
    info: str,
    vgs_max: float,
    vds: tuple[float, ...],
    L: tuple[float, ...],
    vt0: float,
    n: float,
    ucox: float,
    leak: float,
    vsb: tuple[float, ...] = (0.0, 0.2, 0.4),
    w_um: float = 5.0,
) -> dict[str, object]:
    """A small pygmid LUT dict for a PMOS, in the magnitude convention the extractor stores.

    EKV-style drain current ``ID = IS·ln²(1+e^((VGS−VT)/2nUT))·(1−e^(−VDS/UT))·(1+λ·VDS)`` with
    ``gm``/``gds`` its analytic derivatives, ``VT`` rising with |VSB| (body effect) and a little with
    1/L, and an optional ``leak`` floor [A/µm] that carries current but no ``gm``: with it, gm/ID
    peaks at an interior VGS (the IHP shape); without it, at the VGS=0 grid edge (the sky130 shape).
    VDS=0 carries no current at all, as on the real tables. Every value is a plausible textbook
    number, not a PDK's.
    """
    Lg = np.asarray(L, dtype=float)
    VGS = np.round(np.arange(0.0, vgs_max + 1e-9, 0.05), 6)
    VDS = np.asarray(vds, dtype=float)
    VSB = np.asarray(vsb, dtype=float)
    lm, vg, vd, vb = np.meshgrid(Lg, VGS, VDS, VSB, indexing="ij")
    vt = vt0 + 0.45 * (np.sqrt(0.8 + vb) - math.sqrt(0.8)) + 0.02 / lm
    lam = 0.08 / lm
    x = (vg - vt) / (2.0 * n * UT_300K)
    soft = np.logaddexp(0.0, x)  # ln(1 + e^x), overflow-safe
    sig = 0.5 * (1.0 + np.tanh(x / 2.0))  # e^x / (1 + e^x)
    i_s = 2.0 * n * ucox * (w_um / lm) * UT_300K**2
    f_vds = (1.0 - np.exp(-vd / UT_300K)) * (1.0 + lam * vd)
    df_vds = (
        np.exp(-vd / UT_300K) / UT_300K * (1.0 + lam * vd) + (1.0 - np.exp(-vd / UT_300K)) * lam
    )
    i_dc = i_s * soft**2 + leak * w_um
    cox = 8.0e-15  # F/µm²
    return {
        "INFO": info,
        "CORNER": "TT",
        "TEMP": 300.0,
        "NFING": 1,
        "W": w_um,
        "L": Lg,
        "VGS": VGS,
        "VDS": VDS,
        "VSB": VSB,
        "ID": i_dc * f_vds,
        "GM": i_s * 2.0 * soft * sig / (2.0 * n * UT_300K) * f_vds,
        "GDS": i_dc * df_vds,
        "CGG": w_um * lm * cox * (0.3 + 0.37 * sig) + 2.0 * w_um * 0.25e-15,
        "CDD": np.full(lm.shape, w_um * 1.15e-15),
    }


def sky130_pfet_like() -> dict[str, object]:
    """A fresh synthetic table shaped like the sky130 1.8 V pfet: gm/ID peaks at the VGS=0 edge."""
    return synthetic_pmos_lut(
        info="synthetic pmos, sky130-pfet-shaped (edge gm/ID peak)",
        vgs_max=1.8,
        vds=(0.0, 0.3, 0.9, 1.8),
        L=(0.15, 0.5, 1.0),
        vt0=0.75,
        n=1.35,
        ucox=60e-6,
        leak=0.0,
    )


def ihp_pmos_like() -> dict[str, object]:
    """A fresh synthetic table shaped like the IHP lv pmos: gm/ID peaks at an interior VGS."""
    return synthetic_pmos_lut(
        info="synthetic pmos, IHP-lv-pmos-shaped (interior gm/ID peak)",
        vgs_max=1.5,
        vds=(0.0, 0.2, 0.75, 1.5),
        L=(0.13, 0.5, 1.0),
        vt0=0.40,
        n=1.25,
        ucox=80e-6,
        leak=2e-12,
    )


PCH = DeviceTable.from_lut_dict(sky130_pfet_like())
IHP_PCH = DeviceTable.from_lut_dict(ihp_pmos_like())
