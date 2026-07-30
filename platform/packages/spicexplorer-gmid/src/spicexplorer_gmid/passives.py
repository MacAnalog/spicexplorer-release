"""Passive sizing from PDK constants (analog-db registry ``passives.models`` block).

Closed-form, no LUT: a resistor is ``R = R_sheet · (L/W)`` → squares = R/R_sheet; a MIM capacitor
is ``C = C_area · A`` → area = C/C_area. The constants (sheet resistance Ω/□, area capacitance
F/µm²) are passed in by the caller — the leaf tool never reaches into the DB.
"""

from __future__ import annotations

from .contract import SizedPassive
from .errors import GmidError


def size_resistor(target: float, sheet_res: float, *, w_um: float = 1.0) -> SizedPassive:
    """Size a resistor to ``target`` Ω from sheet resistance ``sheet_res`` Ω/□ at width ``w_um`` µm.

    Returns the number of squares and the drawn length ``L = squares · W``.
    """
    if sheet_res <= 0 or w_um <= 0 or target <= 0:
        raise GmidError(
            f"size_resistor needs target/sheet_res/w_um > 0 (got {target}, {sheet_res}, {w_um})"
        )
    squares = target / sheet_res
    l_um = squares * w_um
    return SizedPassive(
        kind="resistor",
        target=target,
        value=sheet_res * (l_um / w_um),
        w_um=w_um,
        l_um=l_um,
        squares=squares,
    )


def size_capacitor(target: float, area_cap: float) -> SizedPassive:
    """Size a capacitor to ``target`` F from area capacitance ``area_cap`` F/µm². Returns plate area."""
    if area_cap <= 0 or target <= 0:
        raise GmidError(f"size_capacitor needs target/area_cap > 0 (got {target}, {area_cap})")
    area_um2 = target / area_cap
    return SizedPassive(
        kind="capacitor",
        target=target,
        value=area_cap * area_um2,
        area_um2=area_um2,
    )
