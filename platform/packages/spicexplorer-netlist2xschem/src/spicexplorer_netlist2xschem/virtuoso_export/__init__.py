"""xschem ⇄ Virtuoso porting (``xvport``) — export ``.sch``/``.sym`` drawings to Cadence cellviews.

The forward pipeline is pure Python and fully offline: parse the xschem file, extract nets
geometrically, map devices through a :class:`~.devmap.DeviceMap`, and emit a deterministic,
self-contained SKILL ``.il`` file. Only the optional *load* step (``--run``) talks to Cadence,
through virtuoso-bridge-lite — that import is lazy, so parsing/emitting never needs the bridge.

Coordinate/orient facts are live-verified constants (see :mod:`.xform`), not guesses.
"""

from __future__ import annotations

from .devmap import DeviceMap, DeviceRule, load_device_map
from .emit_il import emit_schematic_il
from .netex import NetExtraction, extract_nets
from .xform import ORIENT_TABLE, orient_for, to_cadence

__all__ = [
    "DeviceMap",
    "DeviceRule",
    "load_device_map",
    "NetExtraction",
    "extract_nets",
    "emit_schematic_il",
    "ORIENT_TABLE",
    "orient_for",
    "to_cadence",
]
