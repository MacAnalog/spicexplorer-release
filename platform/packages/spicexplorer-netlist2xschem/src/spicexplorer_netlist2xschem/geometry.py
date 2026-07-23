"""xschem instance-placement geometry.

An xschem instance places a symbol at ``(x, y)`` with an integer rotation ``rot`` (0..3, each a
**clockwise** quarter turn) and a ``flip`` (0/1, a mirror about the symbol's vertical axis). To wire
a device pin by net-name we must map the pin's *symbol-local* coordinate to its *absolute* schematic
coordinate under that placement, so a net-label can be dropped exactly on it.

The transform order (**flip first, then rotate, then translate**) matches the UI renderer
(``spicexplorer-ui/src/lib/xschem/render.ts``). The rotation *sense*, however, is pinned to real
hand-drawn schematics, not to the renderer: one ``rot`` step maps ``(x, y) → (-y, x)`` in the
file's y-down frame (clockwise as drawn on screen).

That sense was corrected 2026-07-16 against corpus ground truth (analog-db
``transmission_gate_pair.sch``: the ``rot=3`` NMOS binds G→vctl / B→VSS / D→port_A / S→port_B
only under ``(-y, x)``; the previous ``(y, -x)`` put the gate on VSS). The renderer's
``rotate(-rot·90°)`` negation assumed SVG's positive rotation is CCW — in SVG's y-down frame it
is already clockwise, so the old port inherited an inverted sense for odd ``rot``. A regression
in either the order or the sense silently mis-wires every pin of every rotated instance, so
:func:`apply_transform` is exhaustively unit-tested.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Transform", "apply_transform", "snap"]


@dataclass(frozen=True)
class Transform:
    """An xschem instance placement: origin ``(x, y)``, ``rot`` ∈ {0,1,2,3}, ``flip`` ∈ {0,1}."""

    x: int
    y: int
    rot: int = 0
    flip: int = 0


def apply_transform(t: Transform, px: float, py: float) -> tuple[int, int]:
    """Map a symbol-local pin coordinate ``(px, py)`` to absolute schematic coordinates.

    Flip is applied **before** rotate (matching xschem); ``rot`` is clockwise as drawn on
    screen, i.e. ``(x, y) → (-y, x)`` per step in the file's y-down frame (corpus-verified).
    """
    x: float = -px if t.flip else px
    y: float = py
    for _ in range(t.rot % 4):
        x, y = -y, x  # one on-screen-clockwise quarter turn in xschem's y-down frame
    return (round(t.x + x), round(t.y + y))


def snap(value: float, grid: int = 5) -> int:
    """Snap a coordinate to xschem's connection grid (default 5 units)."""
    return int(round(value / grid) * grid)
