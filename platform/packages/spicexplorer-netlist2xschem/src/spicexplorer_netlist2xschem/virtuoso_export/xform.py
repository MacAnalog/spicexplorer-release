"""xschem → Virtuoso coordinate and orientation mapping — live-verified constants.

xschem places an instance with ``rot`` ∈ {0..3} (on-screen-clockwise quarter turns, i.e.
``(x, y) → (-y, x)`` per step in the file's y-down frame — corpus-verified, see
:mod:`spicexplorer_netlist2xschem.geometry`) and ``flip`` ∈ {0,1} (a mirror about the
symbol's vertical axis, applied *before* the rotation). Virtuoso names its placements with
the eight OpenAccess orients. Conjugating xschem's linear maps by the y-axis negation that
converts between the frames gives ``M_cadence = R270^rot ∘ MY^flip``, i.e. the table below.

The Cadence side was verified live on IC23.1 (2026-07-16) two ways: ``dbTransformPoint``
with each orient string, and a placed asymmetric kit MOS instance per orient
whose transformed pin figures matched the orient matrices exactly (R90 is CCW in y-up;
``MXR90``/``MYR90`` compose mirror-first). The xschem side is pinned by the
transmission-gate corpus regression in ``test_geometry.py``. Do not "fix" this table
without re-running both.

Scale: xschem's connection grid is 5 units; Cadence's schematic snap is 0.0625 user units.
``DEFAULT_SCALE = 0.0125`` maps one grid step exactly onto one snap step, so every ported
coordinate lands on the Cadence grid.
"""

from __future__ import annotations

__all__ = [
    "ORIENT_TABLE",
    "ORIENT_INVERSE",
    "DEFAULT_SCALE",
    "orient_for",
    "rot_flip_for",
    "to_cadence",
    "from_cadence",
    "direction_to_cadence",
]

DEFAULT_SCALE = 0.0125

# (rot, flip) -> OpenAccess orient: R270^rot ∘ MY^flip. Cadence orient matrices verified
# live 2026-07-16 (all 8, placed-instance readback); xschem sense corpus-pinned same day.
ORIENT_TABLE: dict[tuple[int, int], str] = {
    (0, 0): "R0",
    (1, 0): "R270",
    (2, 0): "R180",
    (3, 0): "R90",
    (0, 1): "MY",
    (1, 1): "MXR90",
    (2, 1): "MX",
    (3, 1): "MYR90",
}


ORIENT_INVERSE: dict[str, tuple[int, int]] = {v: k for k, v in ORIENT_TABLE.items()}


def orient_for(rot: int, flip: int) -> str:
    """The Virtuoso orient string for an xschem ``(rot, flip)`` placement."""
    return ORIENT_TABLE[(rot % 4, 1 if flip else 0)]


def rot_flip_for(orient: str) -> tuple[int, int]:
    """The xschem ``(rot, flip)`` for a Virtuoso orient string (the table inverted)."""
    return ORIENT_INVERSE[orient]


def to_cadence(x: float, y: float, scale: float = DEFAULT_SCALE) -> tuple[float, float]:
    """Map an absolute xschem point (y-down) to Virtuoso user units (y-up)."""
    return (x * scale, -y * scale)


def from_cadence(x: float, y: float, scale: float = DEFAULT_SCALE) -> tuple[float, float]:
    """Map a Virtuoso point back to xschem coordinates (the exact inverse of
    :func:`to_cadence`), snapped to xschem's 0.5-unit resolution to absorb float noise."""
    return (round(x / scale * 2) / 2, round(-y / scale * 2) / 2)


def direction_to_cadence(dx: float, dy: float) -> tuple[float, float]:
    """Map an xschem-frame direction vector to the Virtuoso frame (y negated, unscaled)."""
    return (dx, -dy)
