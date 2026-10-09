"""The glyphs themselves — one function per functional icon.

Each takes the :class:`~.frame.IconFrame` the symbol generator computed and returns an
:class:`IconDrawing`:

* ``outline`` — the shape a pin lead may land on (a triangle's edges, a box). Keep it a *closed*
  shape that spans the body: :func:`~.frame.leads` ray-casts against it, so a pin on any side finds
  something to attach to whatever the pin count.
* ``detail`` — everything drawn inside (a staircase, a pass device, the ``+``/``-`` marks). Never an
  attach target, so a lead can never terminate on a decoration.
* ``notes`` — why something was *not* drawn (an input mark that could not be identified). The caller
  surfaces these as warnings; they are how a design finds out its pin names are not conventional
  rather than shipping a sheet with a mark on the wrong pin.

Shapes are written in fractions of the body half-extents (``frame.fx``/``frame.fy``), so every glyph
scales with the box the pin count produced. Marks that must stay readable (a ``+``, a clock wedge)
are in scaled drawing units (``frame.unit``) instead, so they do not grow into blobs on a 56-pin box.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .frame import IconFrame, Segment, box, clock_marks, plus_minus, polyline, staircase

__all__ = [
    "IconDrawing",
    "Glyph",
    "opamp",
    "comparator",
    "integrator",
    "chopper",
    "adc",
    "dac",
    "ldo",
    "switch",
]


@dataclass(frozen=True)
class IconDrawing:
    """What a glyph draws: the attachable outline, the inner detail, and what it refused to guess."""

    outline: tuple[Segment, ...]
    detail: tuple[Segment, ...] = ()
    notes: tuple[str, ...] = field(default=())


#: A glyph: the body box and its pins in, the lines to draw out.
Glyph = Callable[[IconFrame], IconDrawing]


def _triangle(frame: IconFrame) -> tuple[Segment, ...]:
    """The amplifier triangle: the body's left edge, apex at the right edge's midpoint."""
    w, h = frame.half_w, frame.half_h
    return polyline([(-w, -h), (w, 0), (-w, h)], close=True)


def opamp(frame: IconFrame) -> IconDrawing:
    """Opamp / OTA — the amplifier triangle with its input marks.

    The ``+``/``-`` go beside the pins that *are* the non-inverting and inverting inputs, read from
    the pin list; when the two cannot be told apart, neither is drawn (see
    :func:`~.frame.plus_minus`). A transconductor and a voltage opamp share this drawing: what
    distinguishes them is the cell, and the cell's name is already on the symbol.
    """
    marks, notes = plus_minus(frame)
    return IconDrawing(outline=_triangle(frame), detail=marks, notes=notes)


def comparator(frame: IconFrame) -> IconDrawing:
    """Comparator — the amplifier triangle, its input marks, and a clock wedge on the strobe pin."""
    marks, mark_notes = plus_minus(frame)
    clocks, clock_notes = clock_marks(frame)
    return IconDrawing(
        outline=_triangle(frame),
        detail=marks + clocks,
        notes=mark_notes + clock_notes,
    )


def integrator(frame: IconFrame) -> IconDrawing:
    """Integrator — a box holding the response that defines it: a step in, a ramp out.

    Drawn as a small plot (axes plus the ramp) rather than as an opamp-with-feedback-capacitor: the
    capacitor version needs room for a feedback path *outside* the triangle, which a body sized from
    the pin count does not have at small pin counts.
    """
    axis_x, base_y = frame.fx(-0.45), frame.fy(0.5)
    top_y, end_x = frame.fy(-0.5), frame.fx(0.6)
    axes = polyline([(axis_x, top_y), (axis_x, base_y), (end_x, base_y)])
    ramp = polyline([(axis_x, base_y), (end_x, top_y)])
    return IconDrawing(outline=box(frame.half_w, frame.half_h), detail=axes + ramp)


def chopper(frame: IconFrame) -> IconDrawing:
    """Chopper / commutator — the two crossed switch paths, plus a clock wedge on the chop clock."""
    x0, x1 = frame.fx(-0.35), frame.fx(0.35)
    lead_l, lead_r = frame.fx(-0.7), frame.fx(0.7)
    # Kept well inside the box: at ±0.45 the two paths land on the pin rows themselves at common
    # pin counts, and a pin's clock wedge is then drawn on top of a switch path.
    hi, lo = frame.fy(-0.32), frame.fy(0.32)
    paths = (
        polyline([(lead_l, hi), (x0, hi)])
        + polyline([(lead_l, lo), (x0, lo)])
        + polyline([(x1, hi), (lead_r, hi)])
        + polyline([(x1, lo), (lead_r, lo)])
        + polyline([(x0, hi), (x1, hi)])  # the straight-through pair …
        + polyline([(x0, lo), (x1, lo)])
        + polyline([(x0, hi), (x1, lo)])  # … and the crossed pair
        + polyline([(x0, lo), (x1, hi)])
    )
    clocks, notes = clock_marks(frame)
    return IconDrawing(outline=box(frame.half_w, frame.half_h), detail=paths + clocks, notes=notes)


def adc(frame: IconFrame) -> IconDrawing:
    """ADC — a continuous ramp in, a staircase (a code) out."""
    hi, lo = frame.fy(-0.45), frame.fy(0.45)
    ramp = polyline([(frame.fx(-0.75), lo), (frame.fx(-0.15), hi)])
    steps = staircase(frame.fx(0.15), lo, frame.fx(0.75), hi)
    return IconDrawing(outline=box(frame.half_w, frame.half_h), detail=ramp + steps)


def dac(frame: IconFrame) -> IconDrawing:
    """DAC — a staircase (a code) in, a continuous ramp out. The ADC glyph, read the other way."""
    hi, lo = frame.fy(-0.45), frame.fy(0.45)
    steps = staircase(frame.fx(-0.75), lo, frame.fx(-0.15), hi)
    ramp = polyline([(frame.fx(0.15), lo), (frame.fx(0.75), hi)])
    return IconDrawing(outline=box(frame.half_w, frame.half_h), detail=steps + ramp)


def ldo(frame: IconFrame) -> IconDrawing:
    """LDO — the series pass device across the top, the error amplifier under it, the feedback path.

    The three things that make a regulator a regulator, and the three a reader looks for: what
    carries the load current, what controls it, and what it is compared against.
    """
    pass_y = frame.fy(-0.5)
    dev_x, dev_y = frame.fx(0.16), frame.unit(14)
    line_in = polyline([(frame.fx(-0.8), pass_y), (-dev_x, pass_y)])
    line_out = polyline([(dev_x, pass_y), (frame.fx(0.8), pass_y)])
    device = box(dev_x, dev_y)
    device = tuple((x1, y1 + pass_y, x2, y2 + pass_y) for x1, y1, x2, y2 in device)
    amp_apex_x, amp_back_x = frame.fx(0.05), frame.fx(0.45)
    amp_top, amp_bot = frame.fy(0.1), frame.fy(0.66)
    amp_mid = (amp_top + amp_bot) // 2
    amp = polyline(
        [(amp_back_x, amp_top), (amp_apex_x, amp_mid), (amp_back_x, amp_bot)], close=True
    )
    gate = polyline([(0, pass_y + dev_y), (0, amp_mid), (amp_apex_x, amp_mid)])
    feedback = polyline(
        [
            (frame.fx(0.8), pass_y),
            (frame.fx(0.8), amp_top + (amp_mid - amp_top) // 2),
            (amp_back_x, amp_top + (amp_mid - amp_top) // 2),
        ]
    )
    ref_y = amp_bot - (amp_bot - amp_mid) // 2
    tick = frame.unit(8)
    reference = polyline([(frame.fx(0.8), ref_y), (amp_back_x, ref_y)]) + polyline(
        [(frame.fx(0.8), ref_y - tick), (frame.fx(0.8), ref_y + tick)]  # the reference itself
    )
    return IconDrawing(
        outline=box(frame.half_w, frame.half_h),
        detail=line_in + line_out + device + amp + gate + feedback + reference,
    )


def switch(frame: IconFrame) -> IconDrawing:
    """Switch / sampler — an open blade between two terminals, closed by the control pin's clock."""
    left, right = frame.fx(-0.7), frame.fx(0.7)
    node_l, node_r = frame.fx(-0.28), frame.fx(0.28)
    blade_y = frame.fy(-0.42)
    path = (
        polyline([(left, 0), (node_l, 0)])
        + polyline([(node_r, 0), (right, 0)])
        + polyline([(node_l, 0), (node_r, blade_y)])  # the open blade
    )
    clocks, notes = clock_marks(frame)
    return IconDrawing(outline=box(frame.half_w, frame.half_h), detail=path + clocks, notes=notes)
