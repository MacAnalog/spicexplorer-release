"""The reusable **functional-icon** library: an opamp is a triangle, not a rectangle.

A top sheet drawn as forty identical boxes is a netlist with corners. The standard analog blocks —
opamp/OTA, comparator, integrator, chopper, ADC/DAC, LDO, switch/sampler — have a drawing every
analog engineer reads at a glance, and this module is where that drawing lives once for every
design (platform#264).

**A glyph is code, not a checked-in ``.sym``**, for a measured reason. An xschem ``type=subcircuit``
symbol binds its child schematic to the **symbol FILE's basename**, not to the master the netlist
ends up with: a sheet that places one SHARED ``comparator.sym`` for cell ``sar_cmp`` netlists an
*empty* ``.subckt comparator`` (the real cell is never descended into) and, with a ``@value``-style
format line, an extra ``value`` port on top — so the call has N nets and the cell declares N+1 and
the hierarchy stops round-tripping. Adding ``schematic=<master>`` on the instance makes xschem
descend correctly and *still* emits the empty block and the extra port. The shape that works, and
the one this library ships, is therefore: keep the glyph shared, and write a **per-cell ``.sym``**
that carries it with the stock ``@symname`` format —
:func:`~spicexplorer_netlist2xschem.symbol_gen.generate_icon_symbol` does exactly that, so an icon
costs a design nothing it can see.

The second consequence of "a glyph is code": it is a **function of the generated pin geometry**. The
body box is sized from the pin count, so a glyph that was drawn by hand at one size would be wrong
at every other; a glyph here receives the box and its pins (:class:`~.frame.IconFrame`) and draws to
fit. ``+``/``-`` and clock marks are placed beside the pins they belong to, read from the pin list —
never at a fixed spot on the body (see :func:`~.frame.plus_minus`).

Usage::

    from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_icon_symbol

    sym = generate_icon_symbol("sar_cmp", [BlockPin("clk", "left"), ...], "comparator")
    Path("blocks/sar_cmp.sym").write_text(sym.text)     # a per-cell symbol, glyph included

Adding a glyph upstream: write the function in :mod:`.glyphs` (outline + detail + notes), register
it in :data:`ICONS` with its aliases and scale, and add it to the round-trip test's icon list. A
recognised block type only auto-maps (:data:`FAMILY_ICONS`) when the mapping is *unambiguous*.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import glyphs
from .frame import IconFrame, IconPin, Segment, box, leads
from .glyphs import Glyph, IconDrawing

__all__ = [
    "Icon",
    "IconDrawing",
    "IconFrame",
    "IconPin",
    "Segment",
    "box",
    "ICONS",
    "FAMILY_ICONS",
    "icon_names",
    "resolve",
    "parse_spec",
    "icon_for_family",
    "draw",
]


@dataclass(frozen=True)
class Icon:
    """One registered icon: its glyph, the names it answers to, and its default scale.

    ``scale`` multiplies the body geometry the symbol generator computes from the pin count (pitch,
    margins, stub, minimum extents — never the pin *order*, names or sides). It exists because
    ``symbol_gen`` sizes a body from its PIN COUNT: a 7-pin comparator beside a 56-pin array comes
    out at a fraction of the sheet's width, and a glyph with several parts inside it (the LDO's pass
    device, error amp and feedback path; the chopper's four switch paths) stops being readable long
    before a plain rectangle does. A caller can override it per instance (``--icon cell=ldo@1.6``).
    """

    name: str
    glyph: Glyph
    summary: str
    scale: float = 1.0
    aliases: tuple[str, ...] = field(default=())


_ICON_LIST: tuple[Icon, ...] = (
    Icon(
        "opamp",
        glyphs.opamp,
        "amplifier triangle with +/- input marks (opamp, OTA, transconductor)",
        aliases=("ota", "amp", "amplifier", "opamp_ota"),
    ),
    Icon(
        "comparator",
        glyphs.comparator,
        "amplifier triangle with +/- marks and a clock wedge on the strobe pin",
        aliases=("cmp", "comp", "latched_comparator"),
    ),
    Icon("integrator", glyphs.integrator, "step-in / ramp-out response in a box", aliases=("int",)),
    Icon(
        "chopper",
        glyphs.chopper,
        "crossed switch paths (commutator) with a clock wedge",
        scale=1.15,
        aliases=("commutator", "mixer"),
    ),
    Icon("adc", glyphs.adc, "ramp in, staircase (code) out", aliases=("adc_generic", "a2d")),
    Icon("dac", glyphs.dac, "staircase (code) in, ramp out", aliases=("dac_generic", "d2a")),
    Icon(
        "ldo",
        glyphs.ldo,
        "series pass device, error amplifier and feedback path",
        scale=1.3,
        aliases=("regulator", "ldo_regulator"),
    ),
    Icon(
        "switch",
        glyphs.switch,
        "open blade between two terminals, closed by the control clock",
        aliases=(
            "sampler",
            "sample",
            "sample_hold",
            "transmission_gate",
            "tgate",
            "tg",
            "pass_gate",
        ),
    ),
)

#: Every registered icon, by its canonical name **and** by each alias.
ICONS: dict[str, Icon] = {}
for _icon in _ICON_LIST:
    ICONS[_icon.name] = _icon
    for _alias in _icon.aliases:
        ICONS[_alias] = _icon

#: Recognised block **family** → icon, for the automatic mapping (``--annotations``' ``family``
#: field, as circuitgraph's ``export_subcircuit_annotations`` writes it). Only mappings that are
#: unambiguous belong here. The shipped detector catalogue recognises transistor-level families
#: (``current_mirror``, ``differential_pair``, ``cross_coupled``, ``inverter``, ``pseudo_resistor``,
#: ``transmission_gate``); of those exactly one names a block this library draws — a transmission
#: gate IS an analog switch. A differential pair is *not* an opamp (it is one stage of one), so it
#: maps to nothing: a recognised block with no unambiguous icon is drawn as the plain box it always
#: was. A producer that emits a functional family of its own (``comparator``, ``ldo``, …) is matched
#: through :data:`ICONS` by name, so the table grows by itself as upstream recognition does.
FAMILY_ICONS: dict[str, str] = {
    "transmission_gate": "switch",
}


def icon_names() -> tuple[str, ...]:
    """Every canonical icon name, sorted — what a CLI prints when it rejects an unknown one."""
    return tuple(sorted(i.name for i in _ICON_LIST))


def resolve(name: str) -> Icon | None:
    """The :class:`Icon` for a canonical name or alias (case/format-insensitive), else ``None``."""
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    return ICONS.get(key)


def parse_spec(spec: str) -> tuple[Icon, float]:
    """Parse an ``<icon>`` or ``<icon>@<scale>`` request into the icon and the scale to draw it at.

    ``opamp`` uses the icon's registered scale; ``ldo@1.6`` overrides it (the knob a design reaches
    for when one small block has to hold its own beside a many-pin one on the same sheet). Raises
    :class:`ValueError` with the available names — a caller surfaces that as a usage error.
    """
    text = spec.strip()
    scale: float | None = None
    if "@" in text:
        text, _, raw = text.partition("@")
        try:
            scale = float(raw)
        except ValueError:
            raise ValueError(f"icon scale must be a number, got {raw!r}") from None
        if not 0.1 <= scale <= 10.0:
            raise ValueError(f"icon scale must be between 0.1 and 10, got {scale}")
    icon = resolve(text)
    if icon is None:
        raise ValueError(f"unknown icon {text!r}; available: {', '.join(icon_names())}")
    return icon, scale if scale is not None else icon.scale


def icon_for_family(family: str = "", template_id: str = "") -> Icon | None:
    """The icon a recognised block maps to *unambiguously*, or ``None`` — never a guess.

    Tries the annotation's ``family`` against :data:`FAMILY_ICONS`, then the family and the
    ``template_id``'s leading segment (``tg.pair.cmos`` → ``tg``) against the icon names and aliases.
    Recognition that returns nothing for a cell leaves that cell a plain box: an icon asserts what a
    block IS, and a wrong assertion survives every netlist gate there is.
    """
    key = (family or "").strip().lower()
    if key in FAMILY_ICONS:
        return resolve(FAMILY_ICONS[key])
    direct = resolve(key) if key else None
    if direct is not None:
        return direct
    head = (template_id or "").strip().lower().split(".")[0]
    return resolve(head) if head else None


def draw(icon: Icon, frame: IconFrame) -> tuple[tuple[Segment, ...], tuple[str, ...]]:
    """Every line of ``icon`` inside ``frame``: pin leads, outline, inner detail — plus its notes.

    The leads come first and are computed from the *outline only*, so a pin can never be joined to a
    decoration, and no pin's stub is left ending in empty space.
    """
    drawing = icon.glyph(frame)
    return leads(frame, drawing.outline) + drawing.outline + drawing.detail, drawing.notes
