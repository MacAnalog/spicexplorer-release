"""Circuit → xschem ``.sch`` text.

:func:`build_sch` is the end-to-end transform: map each device to a symbol, drop devices that can't be
mapped or whose pins don't fully align (recording a warning), place the rest on a grid, label every
pin with its net name, and render the ``.sch``. Output is deterministic (no timestamps / RNG) so the
golden test is byte-stable. This is the ``.sch`` analogue of ``circuitgraph``'s ``emit.to_netlist``.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Literal

from .analysis import analyze
from .annotation import BlockAnnotationSet, annotation_lines
from .geometry import Transform
from .ingest import Device, DeviceKind, N2XCircuit
from .mapping import LABEL_SYMREF, align_pins, body_pin, is_pdk_primitive, symref_for
from .placement import PhasedPlacer, PlacementHints, Placer, place_with_hints
from .stamp import TemplateStampPlacer, build_block_stamps
from .sym_library import Symbol, SymLibrary
from .title_block import TitleBlock, add_title_block
from .wiring import (
    PlacedDevice,
    RouterMode,
    build_labels,
    check_router,
    plan_connections,
    spread_channels,
)

__all__ = ["SchDocument", "build_sch", "to_sch"]

WiringMode = Literal["hybrid", "labels"]
PlacementMode = Literal["block-aware", "template-stamp", "flat"]

_HEADER = "v {xschem version=3.4.6 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}"


@dataclass(frozen=True)
class SchDocument:
    """The emitted schematic plus a report of what was drawn / skipped."""

    text: str
    warnings: tuple[str, ...]
    device_count: int
    label_count: int
    wire_count: int = 0
    port_count: int = 0
    annotation_count: int = 0  # functional-block boxes drawn over the placement (see build_sch)
    # What the sheet still joins by NAME rather than by wire: the nets whose terminals the wiring
    # left in more than one piece, and the port pins that had to park at the frame. A reader cannot
    # tell a named join from a drawn one, so the emitter reports them (see wiring.ConnectionPlan).
    nets_by_name: tuple[str, ...] = ()
    parked_ports: tuple[str, ...] = ()
    #: The router that drew the sheet: ``"channel"`` when channel routing was asked for
    #: (``router="channel"``) and the sheet is a block diagram (issue #243), else ``"per-route"``
    #: (``"labels"`` in the all-labels wiring mode).
    router: str = "per-route"
    #: The measurements behind those counts, for a caller that acts on them (see
    #: :mod:`.report`): drawn pieces per net carried by name, lanes reserved per channel, nets the
    #: channel router did not route, and rails / spines / taps / refused per supply net
    #: (:class:`~.wiring.ConnectionPlan`). None of them is written into :attr:`text`.
    pieces: Mapping[str, int] = field(default_factory=dict)
    lanes: Mapping[tuple[str, int], int] = field(default_factory=dict)
    unrouted: tuple[str, ...] = ()
    supply: Mapping[str, Mapping[str, int]] = field(default_factory=dict)


_VALUE_MAX = (
    24  # an attribute value longer than this is abbreviated on the schematic (display only)
)
_VALUE_KEEP = 12  # ... to a leading ellipsis + its last N chars, so a verbose symbolic sizing name
#                   (e.g. AnalogGym's ``MOSFET_0_8_W_BIASCM_PMOS*1'``) doesn't overrun the device grid


def _display_value(value: str | float) -> str:
    """The on-schematic form of an attribute value.

    This used to abbreviate anything over ``_VALUE_MAX`` characters to its tail. It could not: the
    string it returns is written into the instance's ``value=`` attribute, which is the attribute
    xschem NETLISTS. Sizing symbols are short enough that it never showed, but a transient stimulus
    (``pulse(1.4 1.65 1u 100n 100n 10u 20u)``) came back out of the netlister as ``…00n 10u 20u)`` —
    a silently broken bench. A shortening meant for the drawing has to be drawn, not stored; if the
    text is ever wanted shorter, it belongs in a separate display-only attribute."""
    return str(value)


_BRACE = re.compile(r"[{}]")


def _needs_quote(value: str) -> bool:
    """Quote empties, anything carrying whitespace, and anything carrying a brace.

    A brace is xschem's own attribute-block delimiter, so an unquoted ``value={vref_val}`` ends the
    ``{...}`` block at the first ``}`` and the netlister emits ``V1 a b {vref_val`` — the closing
    brace and everything after it are gone.
    """
    return value == "" or any(c.isspace() for c in value) or bool(_BRACE.search(value))


def _fmt_value(value: str | float) -> str:
    """One attribute value, quoted and brace-escaped the way xschem's own parser writes them.

    A ``.param`` reference (``dc {vref_val}``) has to reach the ``.sch`` as ``"dc \\{vref_val\\}"``:
    quoting alone is NOT enough — xschem's tokenizer still takes the inner ``}`` for the end of the
    attribute block, drops the attribute *silently* (exit 0, no diagnostic) and substitutes the
    SYMBOL template's default, so ``VREF vref vss dc {vref_val}`` came back out of the netlister as
    ``VREF vref vss 3`` (``vsource.sym`` says ``value=3``). Escaping both braces round-trips the
    expression verbatim, and is what xschem writes itself for a braced value.
    """
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    s = str(value)
    if not _needs_quote(s):
        return s
    return '"' + _BRACE.sub(lambda m: "\\" + m.group(0), s) + '"'


def _attr_string(attrs: list[tuple[str, str | float]]) -> str:
    return " ".join(f"{k}={_fmt_value(v)}" for k, v in attrs)


def _param(dev: Device, key: str) -> str | float | None:
    for k, v in dev.params.items():
        if k.lower() == key:
            return v
    return None


def _instance_name(dev: Device, sym: Symbol) -> str:
    """xschem prepends ``spiceprefix`` to the instance name; if the symbol carries ``spiceprefix=X``
    (the IHP MOS convention) strip one leading X from the ref so re-netlisting reproduces it."""
    if sym.template.get("spiceprefix", "").upper() == "X" and dev.ref[:1] in "Xx":
        return dev.ref[1:]
    return dev.ref


def _device_attrs(dev: Device, sym: Symbol) -> list[tuple[str, str | float]]:
    """The ``{name=… …}`` attributes for a device instance, drawn from device params then symbol
    template defaults, in a stable order."""
    attrs: list[tuple[str, str | float]] = [("name", _instance_name(dev, sym))]
    body = body_pin(dev, sym)
    if is_pdk_primitive(dev, sym):
        # A PDK primitive drawn with the PDK's own symbol: the SG13G2 poly resistors and HBTs, and
        # the two-net primitives (cap_cmim, the antenna diodes) that the prefix test types as
        # plain CAPs. Its `format` line netlists `@model` plus the template's own parameter keys —
        # `w=@w l=@l m=@m b=@b` for rhigh, `w=@w l=@l m=@m` for cap_cmim, `Nx=@Nx` for npn13G2 —
        # so the sizing MUST be on the instance. Written into the generic `value` slot instead it
        # was simply not netlisted, and xschem substituted the symbol template's default.
        attrs.append(("model", dev.model or sym.template.get("model", "")))
        attrs.append(("spiceprefix", sym.template.get("spiceprefix", "X")))
        if body is not None:
            # A 3-node subckt on a 2-pin symbol (`XR1 P M sub rhigh`): the substrate node is the
            # `body=` attribute, not a pin. `format` reads "@pinlist @body @model ...".
            attrs.append(("body", dev.nets.get(body, sym.template.get("body", ""))))
        seen = {k for k, _ in attrs}
        for key in template_param_keys(sym):
            val = _param(dev, key.lower())
            if val is None or _is_default_count(key.lower(), val):
                # w/l absent: the attribute is OMITTED, never back-filled from the symbol template.
                # The template's default is the SYMBOL author's, not the model's — sg13g2_pr's
                # rhigh.sym says l=0.5e-6 while the model library's `.subckt rhigh` defaults to
                # l=0.96e-6 — so writing it in would have stated a size the netlist never gave and
                # silently changed the device. `pdk_param_warnings` says so out loud instead.
                # (m=1 is the default multiplier; b is written only when the netlist set it.)
                continue
            attrs.append((key, _display_value(val)))
            seen.add(key)
        # Everything else the netlist set rides along on the instance. It is NOT netlisted back
        # (the symbol's `format` line names only the keys above), but dropping it silently lost
        # information the .sch can perfectly well carry — see `pdk_param_warnings`.
        lower_seen = {k.lower() for k in seen}
        for key, val in dev.params.items():
            if key.lower() in lower_seen or val in (None, ""):
                continue
            attrs.append((key, _display_value(val)))
        return attrs
    if dev.kind is DeviceKind.MOS:
        attrs.append(("model", dev.model or sym.template.get("model", "")))
        # Only a symbol that DECLARES a spiceprefix gets one on the instance. A PDK MOS shipped as
        # a subcircuit says `spiceprefix=X` in its template and must keep it; xschem's generic
        # `nmos4.sym`/`pmos4.sym` declare none, because a plain SPICE MOSFET netlists as `m1 …`.
        # Defaulting to "X" here emitted `Xm1 …` for the generic symbols, which re-netlists as a
        # subcircuit call and fails the netlist-identity gate.
        prefix = sym.template.get("spiceprefix")
        if prefix:
            attrs.append(("spiceprefix", prefix))
        for key in ("w", "l", "ng", "m"):
            val = _param(dev, key)
            if val is None and key in sym.template:
                val = sym.template[key]
            if val is None or _is_default_count(key, val):
                continue  # omit ng=1 / m=1 — the model default; drawing it just clutters the device
            attrs.append((key, _display_value(val)))
        extra = _extra_params(dev, sym)
        if extra:
            attrs.append(("extra", extra))
    else:
        # res/cap/ind/vsource/isource: value slot then optional non-default m.
        value = dev.model if dev.model not in (None, "") else sym.template.get("value", "")
        attrs.append(("value", _display_value(value)))
        m = _param(dev, "m")
        if m is None and "m" in sym.template:
            m = sym.template["m"]
        if m is not None and not _is_default_count("m", m):
            attrs.append(("m", m))
        # xschem's source symbols netlist through a `tcleval()` ternary on `savecurrent`. With the
        # key absent from the INSTANCE the substitution leaks the template's literal into the card
        # — `VBNC vbnc 0 0.894false` — which no simulator accepts and which only shows up once the
        # sheet is re-netlisted. Carrying it explicitly is what keeps the emitted netlist valid.
        if "savecurrent" in sym.template:
            attrs.append(("savecurrent", sym.template["savecurrent"]))
    return attrs


def _extra_params(dev: Device, sym: Symbol) -> str:
    """The netlist parameters this symbol's ``format`` line would otherwise DROP, as ``@extra``.

    xschem's generic MOS netlists exactly what its format line names::

        format="@spiceprefix@name @pinlist @model w=@w l=@l @extra m=@m"

    so ``w``, ``l``, ``m`` and whatever sits in ``extra`` — and nothing else. Every other sizing
    parameter the netlist carried was silently discarded, which on a kit where ``w`` is the TOTAL
    width and ``nf`` divides it into fingers re-netlists a ``w=32.4747u nf=16`` device as a 32 µm
    SINGLE-FINGER one: a different transistor, whose gm/ID is several percent off the table the
    design was sized from, drawn on a sheet that is supposed to BE the record. Measured on that
    kit: ``w=2u nf=4`` reads 3.5 % off in gm/ID against a 2 µm characterisation.

    ``extra`` substitutes verbatim, so the parameters ride back into the netlist under **the names
    the netlist used** — ``nf=16`` stays ``nf``, ``ng=2`` stays ``ng``. Nothing is renamed or
    invented: a key this symbol already netlists by name is left to that path.
    """
    if not sym.netlists("extra"):
        return ""
    carried = [
        f"{key}={_display_value(val)}"
        for key, val in dev.params.items()
        if val not in (None, "") and not sym.netlists(key) and key.lower() != "extra"
    ]
    return " ".join(carried)


_TEMPLATE_ROLE_KEYS = frozenset({"name", "model", "spiceprefix", "body"})
"""Template keys that name the instance's *role*, not one of its parameters."""


def template_param_keys(sym: Symbol) -> list[str]:
    """The parameter keys a PDK symbol's ``format`` line netlists, read off its own template.

    Derived rather than hard-coded, because the keys differ per primitive — ``w l m b`` (rhigh),
    ``w l m`` (cap_cmim), ``w l wfeed`` (cap_rfcmim), ``w l`` (the antenna diodes), ``Nx``
    (npn13G2). They arrive lowercased from :func:`~.sym_library._parse_template`, which is why a
    primitive whose ``format`` names an uppercase key (``cap_cpara``'s ``C=@C``) is not mapped.
    """
    return [k for k in sym.template if k.lower() not in _TEMPLATE_ROLE_KEYS]


def pdk_param_warnings(dev: Device, sym: Symbol) -> list[str]:
    """What a reader of the generated ``.sch`` must be told about a PDK-primitive instance.

    Two lossy spots, both silent before: a missing ``w``/``l`` (xschem falls back to the SYMBOL's
    template default, which need not be the model's) and any other parameter (kept on the
    instance, but the symbol's fixed ``format`` line will not netlist it back).
    """
    if not is_pdk_primitive(dev, sym):
        return []
    out: list[str] = []
    absent = [k for k in ("w", "l") if _param(dev, k) is None and k in sym.template]
    if absent:
        shown = ", ".join(f"{k}={sym.template[k]}" for k in absent)
        out.append(
            f"{dev.ref}: the netlist sets no {'/'.join(absent)}, so the instance omits "
            f"{'it' if len(absent) == 1 else 'them'} and xschem will netlist the SYMBOL "
            f"template's default ({shown}) — which is not necessarily the model's default "
            f"(sg13g2_pr/rhigh.sym says l=0.5e-6; the model library's `.subckt rhigh` says "
            f"l=0.96e-6). Size the device in the netlist to make the round trip exact"
        )
    netlisted = template_param_keys(sym)
    keep = {k.lower() for k in netlisted}
    extra = sorted(k for k in dev.params if k.lower() not in keep)
    if extra:
        out.append(
            f"{dev.ref}: parameter(s) {extra} are kept as instance attributes, but the symbol's "
            f"`format` line netlists only {netlisted} — they will NOT reappear in a "
            f"netlist-back round trip"
        )
    return out


def _is_default_count(key: str, value: str | float) -> bool:
    """True for ``ng``/``m`` equal to 1 — the default finger count / multiplier, omitted to declutter."""
    return key in ("ng", "m") and str(value).strip() in ("1", "1.0")


_PARAM_X0 = 60  # where the symbol's attribute text starts (see wiring._TEXT_X0: issue #244)
_PARAM_CHAR_W = 8  # approximate drawn width of one attribute-text character


def _text_reach(dev: Device, sym: Symbol) -> int:
    """How far the symbol's visible attribute text reaches from the device body.

    A MOS draws its model name and w/l/ng/m (xschem renders the template ng/m even when the instance
    omits the default 1, so they count); a passive draws its value. The wiring keep-out is sized to the
    longest of these so a net-name label is never placed on top of a device's parameter text — the
    clutter that device flipping used to cause (the text is mirrored onto the gate-opposite side)."""
    if dev.kind is DeviceKind.MOS or body_pin(dev, sym) is not None:
        strings = [str(dev.model or sym.template.get("model", ""))]
        sizes: list[str] = []
        for key in ("w", "l", "ng", "m"):
            val = _param(dev, key)
            if val is None:
                val = sym.template.get(key)
            if val is not None:
                strings.append(f"{key}={_display_value(val)}")
                sizes.append(str(_display_value(val)))
        # The symbol does not draw `key=value` per line — it draws ONE concatenated run,
        # `T {@w\\/@l\\/@m}` (devices/nmos4.sym), e.g. `44.7128u/0.5u/1`. That is wider than the
        # longest single pair, so sizing the keep-out from the pairs put a net-name label on top
        # of the next device's size text (issue #159); `--show-params` had to be left off.
        if sizes:
            strings.append("/".join(sizes))
    else:
        value = dev.model if dev.model not in (None, "") else sym.template.get("value", "")
        strings = [_display_value(value)]
    return _PARAM_X0 + max((len(s) for s in strings), default=0) * _PARAM_CHAR_W


def build_sch(
    circuit: N2XCircuit,
    *,
    pdk: str | None = "ihp-sg13g2",
    lib: SymLibrary | None = None,
    placer: Placer | None = None,
    wiring: WiringMode = "hybrid",
    title: str | None = None,
    annotations: BlockAnnotationSet | None = None,
    annotation_aware_placement: bool = True,
    placement_mode: PlacementMode | None = None,
    template_root: Path | None = None,
    show_device_params: bool = False,
    title_block: TitleBlock | None = None,
    cell_symbols: Mapping[str, str] | None = None,
    port_roles: Mapping[str, str] | None = None,
    router: RouterMode = "per-route",
) -> SchDocument:
    """Render ``circuit`` to an xschem ``.sch`` document (text + warnings + counts).

    ``wiring="hybrid"`` (default) draws signal nets as wires and labels only supply nets (plus VDD/VSS
    rails); ``wiring="labels"`` labels every pin (the simplest, always-correct mode).

    ``annotations`` is an optional :class:`~spicexplorer_netlist2xschem.annotation.BlockAnnotationSet`
    (recognised functional sub-circuits from an upstream detector): each block is drawn as a labelled,
    coloured bounding box *over* the placement — a purely diagnostic overlay that moves no device and
    adds no wire, so connectivity is unchanged. Joined to the schematic by device instance name.

    ``annotation_aware_placement`` (default ``True``, **block-aware placement**) additionally feeds
    those blocks to the placer as :class:`~spicexplorer_netlist2xschem.placement.PlacementHints`, so a
    block's devices are clustered into a tight, non-overlapping region under its box instead of being
    scattered by raw topology. It is a layout-only hint — connectivity is identical either way. Set it
    ``False`` to keep the block-agnostic layout and draw the boxes *over* it (the original overlay
    behaviour); with ``annotations=None`` it has no effect (the layout is unchanged regardless).

    ``placement_mode`` selects how recognised blocks drive the layout (it supersedes
    ``annotation_aware_placement`` when given):

    * ``"block-aware"`` — P5: cluster each block's devices (the barycentre nudge above);
    * ``"template-stamp"`` — strategy 2: lay each block at its **hand-drawn template's symmetric
      geometry** (a differential pair's halves drawn mirror-symmetric), arranging the blocks in the base
      placer's left-to-right order. Needs the contract's ``template_sch`` / ``device_slots`` (resolved
      against ``template_root``, default the shipped analog-db templates); a block lacking them falls
      back to block-aware. Still connectivity-neutral — only device coordinates change.
    * ``"flat"`` — the block-agnostic layout (draw boxes over raw topology).

    When ``placement_mode is None`` the mode is ``"block-aware"`` if ``annotation_aware_placement`` else
    ``"flat"`` — so existing callers are byte-for-byte unchanged.

    ``title_block`` (default ``None``) draws a real title block — a frame with the cell name, the
    design, a revision, a date and an author — clear of everything on the sheet, *instead of* the
    loose ``title`` text record (:func:`~spicexplorer_netlist2xschem.title_block.add_title_block`).
    Its date is an INPUT, so two renders of the sheet hours apart are byte-identical; xschem's own
    ``devices/title.sym`` cannot be used for this (issue #265) and is left untouched for anyone who
    wants it. With ``title_block=None`` the sheet is byte-for-byte what it was.

    ``show_device_params`` (default ``False``) controls whether each device draws its parameter text
    (``model``/``w``/``l``/``value``). Off by default: devices map to clean *no-params* symbol twins
    (``devices/*_np.sym``) that have identical pins + netlist ``K``-block — so placement, wiring and
    connectivity are byte-identical and the instance still carries the full values for netlisting — they
    just don't draw the sizing text that clutters a topology schematic. Set it ``True`` to keep the text.

    ``cell_symbols`` maps a subcircuit name (lowercase) to the symref its instances are drawn with,
    for this call only; a name absent from it resolves as before
    (:func:`~.mapping.register_subckt_symbol`). :func:`~.collapse.build_collapsed_sch` passes the
    group cells it generates here.

    ``port_roles`` (``{net: "in" | "out" | "inout"}``) names exactly the nets drawn as port pins
    and their direction, in place of the ones :func:`~.analysis.analyze` infers (declared ports
    plus every net with one terminal, directions from MOSFET pin roles). A group cell's sheet
    passes its symbol's pins, so the sheet and the symbol declare the same ports: xschem reports
    an error for a port pin whose direction differs from the symbol pin's.

    ``router`` is off by default: ``"per-route"`` draws every sheet exactly as before channel
    routing existed. ``"channel"`` is a helper a caller (the schematic agent) asks for on a top
    level of block symbols: on a sheet of two or more blocks and no MOSFET the blocks are moved
    apart until every lane fits (:func:`~.wiring.spread_channels`) and the sheet is routed by
    channels (:mod:`.channels`); any other sheet is still drawn by the per-route planner, with
    label stubs kept off each block's drawn body. :attr:`SchDocument.router` says which one drew it.
    """
    check_router(router)
    lib = lib or SymLibrary.default()
    placer = placer or PhasedPlacer()
    cell_symbols = cell_symbols or {}
    mode: PlacementMode = placement_mode or (
        "block-aware" if annotation_aware_placement else "flat"
    )
    warnings: list[str] = []

    # 1. Resolve a symbol for every device; keep only the fully-alignable ones. With params suppressed
    # (the default) each device maps to its clean "no-params" symbol twin — same pins and netlist
    # K-block (so placement, wiring and connectivity are byte-identical), only the w/l/model display text
    # is gone. The instance attributes stay full, so the runnable values still round-trip.
    resolved: list[tuple[Device, str, Symbol, dict]] = []
    for dev in circuit.devices:
        symref = (
            cell_symbols.get((dev.model or "").split()[0].lower() if dev.model else "")
            if dev.kind is DeviceKind.SUBCKT
            else None
        ) or symref_for(dev, pdk=pdk, show_params=show_device_params)
        if symref is None:
            warnings.append(
                f"{dev.ref}: no symbol mapping for kind={dev.kind.value} "
                f"polarity={dev.polarity.value} (pdk={pdk}); skipped"
            )
            continue
        sym = lib.load(symref)
        if sym is None:
            warnings.append(f"{dev.ref}: symbol {symref!r} not found on the search path; skipped")
            continue
        aligned = align_pins(dev, sym)
        body = body_pin(dev, sym)  # a body node is an attribute, never an unaligned pin
        missing = [p for p in dev.pins if p not in aligned and p != body]
        if missing:
            warnings.append(
                f"{dev.ref}: pins {missing} could not be aligned to {symref!r}; skipped"
            )
            continue
        warnings.extend(pdk_param_warnings(dev, sym))
        resolved.append((dev, symref, sym, aligned))

    # 2. Place only the emittable devices (so skipped ones don't leave grid gaps). When annotations are
    # supplied the recognised blocks drive the layout per `mode` (P5 block-aware clustering, strategy-2
    # template stamping, or flat/block-agnostic). Every mode is layout-only — connectivity is identical,
    # and (annotations is None) or mode="flat" reproduces the block-agnostic placement exactly.
    placed_circuit = replace(circuit, devices=tuple(r[0] for r in resolved))
    if annotations and mode == "template-stamp":
        present = {dev.ref for dev, _, _, _ in resolved}
        stamps = build_block_stamps(annotations, present, root=template_root)
        if stamps:
            stamp_placer = TemplateStampPlacer(stamps=tuple(stamps), base=placer)
            placement: dict[str, Transform] = stamp_placer.place(placed_circuit, lib)
        else:  # no stampable block (older contract / templates absent) — fall back to block-aware
            warnings.append(
                "template-stamp: no block carried a resolvable template_sch/device_slots; "
                "falling back to block-aware placement"
            )
            placement = place_with_hints(
                placer,
                placed_circuit,
                lib,
                PlacementHints(clusters=annotations.placement_clusters()),
            )
    else:
        hints = (
            PlacementHints(clusters=annotations.placement_clusters())
            if annotations and mode == "block-aware"
            else None
        )
        placement = place_with_hints(placer, placed_circuit, lib, hints)

    placed_devices: list[PlacedDevice] = []
    channels = router == "channel"
    for dev, _symref, sym, aligned in resolved:
        # A block: a subcircuit drawn with a design's own symbol (not a PDK primitive's). Two or
        # more of them and no MOSFET make the sheet a block diagram, which is routed by channels
        # when the caller asks for it. Not asked, no device is a block and every keep-out is the
        # transistor-sized one the sheet was always drawn with.
        is_block = (
            channels
            and dev.kind is DeviceKind.SUBCKT
            and not is_pdk_primitive(dev, sym)
            and body_pin(dev, sym) is None
        )
        placed_devices.append(
            PlacedDevice(
                ref=dev.ref,
                transform=placement[dev.ref],
                nets=dev.nets,
                aligned=aligned,
                text_w=_text_reach(dev, sym),
                is_source=dev.kind in (DeviceKind.VSOURCE, DeviceKind.ISOURCE),
                is_block=is_block,
                body=sym.bbox if is_block else None,
            )
        )
    if wiring == "hybrid" and channels:
        # Channel routing reserves a lane per net in every gap between block columns and rows;
        # where a gap is too narrow for its lanes, the blocks beyond it move apart (block diagrams
        # only — any other sheet comes back unchanged).
        placed_devices = spread_channels(placed_devices, supply=circuit.supply)

    # 3. Emit device instances. The title sits at the top-left, clear above every device — not centred,
    # where a top-row tail device (placed at x≈0) would collide with its gate label.
    lines = [_HEADER]
    if title and title_block is None:
        # Over every transform the placer returned, a device the emitter skipped included, as the
        # sheet has always been drawn; with channels asked for, over the blocks as moved apart.
        origins = [pd.transform for pd in placed_devices] if channels else list(placement.values())
        tx = min((t.x for t in origins), default=0) - 40
        ty = min((t.y for t in origins), default=0) - 200
        lines.append(f"T {{{title}}} {tx} {ty} 0 0 0.4 0.4 {{}}")
    for (dev, symref, sym, _aligned), pd in zip(resolved, placed_devices):
        t = pd.transform
        lines.append(
            f"C {{{symref}}} {t.x} {t.y} {t.rot} {t.flip} {{{_attr_string(_device_attrs(dev, sym))}}}"
        )

    # 4. Wire it: hybrid (g/s/d wires + supply rails + port pins, bulk by name) or all-labels.
    if wiring == "hybrid":
        info = analyze(placed_circuit)
        plan = plan_connections(
            placed_devices,
            supply=circuit.supply,
            port_role=info.port_role if port_roles is None else port_roles,
            router=router,
        )
        wires, labels, ports = plan.wires, plan.labels, plan.ports
        by_name, parked = tuple(plan.by_name), tuple(plan.parked_ports)
        drawn_by = plan.router
        pieces, lanes, unrouted, supply = plan.pieces, plan.lanes, tuple(plan.unrouted), plan.supply
    else:
        wires, labels, ports = [], build_labels(placed_devices), []
        # Labels mode joins EVERYTHING by name, so every net with more than one terminal to join is
        # carried by name (same definition as the plan's: body pins and source terminals are named
        # by design and never counted).
        joined: dict[str, int] = defaultdict(int)
        for pd in placed_devices:
            if pd.is_source:
                continue
            for canon, net in pd.nets.items():
                if canon != "BULK":
                    joined[net] += 1
        by_name, parked = tuple(sorted(n for n, k in joined.items() if k > 1)), ()
        drawn_by = "labels"
        # every terminal of a net carried by name is its own piece; nothing is routed
        pieces = {n: joined[n] for n in by_name}
        lanes, unrouted, supply = {}, (), {}

    for w in wires:
        lines.append(f"N {w.x1} {w.y1} {w.x2} {w.y2} {{}}")
    for i, lbl in enumerate(labels):
        lines.append(
            f"C {{{LABEL_SYMREF}}} {lbl.x} {lbl.y} {lbl.rot} {lbl.flip} "
            f"{{name=l{i} lab={_fmt_value(lbl.lab)}}}"
        )
    for i, port in enumerate(ports):
        lines.append(
            f"C {{{port.symref}}} {port.x} {port.y} {port.rot} {port.flip} "
            f"{{name=p{i} lab={_fmt_value(port.net)}}}"
        )

    # 5. Functional-block annotation overlay (additive; drawn last so the boxes/labels sit on top).
    annotation_count = 0
    if annotations:
        ann_lines, ann_warnings = annotation_lines(annotations, placed_devices)
        lines.extend(ann_lines)
        warnings.extend(ann_warnings)
        annotation_count = sum(1 for ln in ann_lines if ln.startswith("B "))

    text = "\n".join(lines) + "\n"
    if title_block is not None:
        # Last: the block is placed clear of the DRAWN extent, which is only known once every
        # device, wire, label and annotation box is on the sheet.
        text = add_title_block(
            text,
            cell=title_block.cell,
            design=title_block.design,
            rev=title_block.rev,
            date=title_block.date,
            author=title_block.author,
            corner=title_block.corner,
            scale=title_block.scale,
        )

    return SchDocument(
        text=text,
        warnings=tuple(warnings),
        device_count=len(resolved),
        label_count=len(labels),
        wire_count=len(wires),
        port_count=len(ports),
        nets_by_name=by_name,
        parked_ports=parked,
        router=drawn_by,
        annotation_count=annotation_count,
        pieces=pieces,
        lanes=lanes,
        unrouted=unrouted,
        supply=supply,
    )


def to_sch(circuit: N2XCircuit, **kwargs) -> str:
    """Convenience: just the ``.sch`` text (see :func:`build_sch` for the full report)."""
    return build_sch(circuit, **kwargs).text
