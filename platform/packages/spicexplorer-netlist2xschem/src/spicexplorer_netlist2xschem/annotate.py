"""Overlay functional-block annotation boxes on an **existing** (hand-drawn) xschem ``.sch``.

The block-annotation overlay normally runs *inside* generation: place a netlist, then box the blocks.
But a user often already has a schematic — drawn by hand or exported from elsewhere — and just wants to
*see* the recognised blocks outlined on it, without regenerating (and so disturbing) their layout. This
module does exactly that: parse the existing ``.sch`` for each device's placed coordinate
(:mod:`sch_parser`), then draw the same labelled boxes (:func:`~.annotation.annotation_lines`) over that
layout. It moves nothing — only ``B``/``T`` graphics are appended — so the schematic is byte-for-byte
unchanged but for the overlay.

The join is by **device instance name**, the contract's key. A subtlety: a netlist names a transistor
``XM3`` (spiceprefix ``X``) while xschem draws it as ``name=M3`` — so the blocks (which carry netlist
refs) are matched to the drawn devices with a leading ``X`` normalised away on both sides.
"""

from __future__ import annotations

from dataclasses import replace

from .annotation import BlockAnnotationSet, annotation_lines
from .geometry import Transform
from .sch_parser import parse_sch
from .wiring import PlacedDevice

__all__ = ["annotate_sch"]

_PARAM_X0 = 22  # where attribute text starts beyond the body (matches emit._text_reach)
_PARAM_CHAR_W = 8  # approximate drawn width of one attribute character
_PARAM_KEYS = ("model", "w", "l", "value", "ng", "m")


def _normx(name: str) -> str:
    return name[1:] if name[:1] in "Xx" else name


def _text_reach(attrs: dict[str, str]) -> int:
    """Approximate how far a device's parameter text reaches, from its drawn attributes — so the box
    clears the ``w/l/model`` band the same way generation's keep-out does."""
    strings = [f"{k}={attrs[k]}" for k in _PARAM_KEYS if k in attrs]
    return _PARAM_X0 + max((len(s) for s in strings), default=0) * _PARAM_CHAR_W


def annotate_sch(
    sch_text: str, annotations: BlockAnnotationSet
) -> tuple[str, tuple[str, ...]]:
    """Return ``sch_text`` with the block overlay appended, plus any warnings.

    Parses the schematic for its device coordinates and draws each block's labelled box around the
    devices it names — over the *existing* placement (nothing is moved). Blocks are joined to the drawn
    devices by instance name (tolerant of the ``X`` spiceprefix split). A block whose devices are all
    absent from the schematic is skipped with a warning (same lenient policy as in-generation overlay).

    Note: box extents assume devices are drawn upright (``rot=0``), as this tool's own generator emits;
    a hand-rotated symbol is still boxed, just with a slightly looser fit.
    """
    sch = parse_sch(sch_text)
    placed: list[PlacedDevice] = []
    drawn: dict[str, str] = {}  # X-normalised name -> the name as drawn
    for c in sch.devices:
        placed.append(
            PlacedDevice(
                ref=c.name,
                transform=Transform(int(round(c.x)), int(round(c.y)), c.rot, c.flip),
                nets={},
                aligned={},
                text_w=_text_reach(c.attrs),
            )
        )
        drawn[_normx(c.name)] = c.name

    # Remap each block's device refs to the names as drawn (XM3 -> M3 when that is how it is in the .sch).
    remapped = tuple(
        replace(b, devices=tuple(drawn.get(_normx(r), r) for r in b.devices))
        for b in annotations.blocks
    )
    lines, warnings = annotation_lines(BlockAnnotationSet(remapped), placed)
    if not lines:
        return sch_text, tuple(warnings)
    annotated = sch_text.rstrip("\n") + "\n" + "\n".join(lines) + "\n"
    return annotated, tuple(warnings)
