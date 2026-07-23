"""Circuit → xschem ``.sch`` text.

:func:`build_sch` is the end-to-end transform: map each device to a symbol, drop devices that can't be
mapped or whose pins don't fully align (recording a warning), place the rest on a grid, label every
pin with its net name, and render the ``.sch``. Output is deterministic (no timestamps / RNG) so the
golden test is byte-stable. This is the ``.sch`` analogue of ``circuitgraph``'s ``emit.to_netlist``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from .analysis import analyze
from .annotation import BlockAnnotationSet, annotation_lines
from .geometry import Transform
from .ingest import Device, DeviceKind, N2XCircuit
from .mapping import LABEL_SYMREF, align_pins, symref_for
from .placement import PhasedPlacer, PlacementHints, Placer, place_with_hints
from .stamp import TemplateStampPlacer, build_block_stamps
from .sym_library import Symbol, SymLibrary
from .wiring import PlacedDevice, build_labels, plan_connections

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


_VALUE_MAX = 24  # an attribute value longer than this is abbreviated on the schematic (display only)
_VALUE_KEEP = 12  # ... to a leading ellipsis + its last N chars, so a verbose symbolic sizing name
#                   (e.g. AnalogGym's ``MOSFET_0_8_W_BIASCM_PMOS*1'``) doesn't overrun the device grid


def _display_value(value: str | float) -> str:
    """The on-schematic form of an attribute value: abbreviated to its tail when very long.

    The symbol already draws the role prefix (``w=``/``l=``/``value=``), so keeping the last chars
    reads as ``w=…BIASCM_PMOS*1'``. This is a *display* shortening of the topology ``.sch`` only — the
    runnable decks under ``raw/<circuit>/<pdk>/`` carry the full sizing; the round-trip checks
    connectivity, not values. Short, readable names (the hand-authored ``x_dut_*`` set) are untouched."""
    s = str(value)
    return "…" + s[-_VALUE_KEEP:] if len(s) > _VALUE_MAX else s


def _needs_quote(value: str) -> bool:
    return value == "" or any(c.isspace() for c in value)


def _fmt_value(value: str | float) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    s = str(value)
    return f'"{s}"' if _needs_quote(s) else s


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
    if dev.kind is DeviceKind.MOS:
        attrs.append(("model", dev.model or sym.template.get("model", "")))
        attrs.append(("spiceprefix", sym.template.get("spiceprefix", "X")))
        for key in ("w", "l", "ng", "m"):
            val = _param(dev, key)
            if val is None and key in sym.template:
                val = sym.template[key]
            if val is None or _is_default_count(key, val):
                continue  # omit ng=1 / m=1 — the model default; drawing it just clutters the device
            attrs.append((key, _display_value(val)))
    else:
        # res/cap/ind/vsource/isource: value slot then optional non-default m.
        value = dev.model if dev.model not in (None, "") else sym.template.get("value", "")
        attrs.append(("value", _display_value(value)))
        m = _param(dev, "m")
        if m is None and "m" in sym.template:
            m = sym.template["m"]
        if m is not None and not _is_default_count("m", m):
            attrs.append(("m", m))
    return attrs


def _is_default_count(key: str, value: str | float) -> bool:
    """True for ``ng``/``m`` equal to 1 — the default finger count / multiplier, omitted to declutter."""
    return key in ("ng", "m") and str(value).strip() in ("1", "1.0")


_PARAM_X0 = 22  # where the symbol's attribute text starts, just outside the body
_PARAM_CHAR_W = 8  # approximate drawn width of one attribute-text character


def _text_reach(dev: Device, sym: Symbol) -> int:
    """How far the symbol's visible attribute text reaches from the device body.

    A MOS draws its model name and w/l/ng/m (xschem renders the template ng/m even when the instance
    omits the default 1, so they count); a passive draws its value. The wiring keep-out is sized to the
    longest of these so a net-name label is never placed on top of a device's parameter text — the
    clutter that device flipping used to cause (the text is mirrored onto the gate-opposite side)."""
    if dev.kind is DeviceKind.MOS:
        strings = [str(dev.model or sym.template.get("model", ""))]
        for key in ("w", "l", "ng", "m"):
            val = _param(dev, key)
            if val is None:
                val = sym.template.get(key)
            if val is not None:
                strings.append(f"{key}={_display_value(val)}")
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

    ``show_device_params`` (default ``False``) controls whether each device draws its parameter text
    (``model``/``w``/``l``/``value``). Off by default: devices map to clean *no-params* symbol twins
    (``devices/*_np.sym``) that have identical pins + netlist ``K``-block — so placement, wiring and
    connectivity are byte-identical and the instance still carries the full values for netlisting — they
    just don't draw the sizing text that clutters a topology schematic. Set it ``True`` to keep the text.
    """
    lib = lib or SymLibrary.default()
    placer = placer or PhasedPlacer()
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
        symref = symref_for(dev, pdk=pdk, show_params=show_device_params)
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
        missing = [p for p in dev.pins if p not in aligned]
        if missing:
            warnings.append(
                f"{dev.ref}: pins {missing} could not be aligned to {symref!r}; skipped"
            )
            continue
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
                placer, placed_circuit, lib,
                PlacementHints(clusters=annotations.placement_clusters()),
            )
    else:
        hints = (
            PlacementHints(clusters=annotations.placement_clusters())
            if annotations and mode == "block-aware"
            else None
        )
        placement = place_with_hints(placer, placed_circuit, lib, hints)

    # 3. Emit device instances. The title sits at the top-left, clear above every device — not centred,
    # where a top-row tail device (placed at x≈0) would collide with its gate label.
    lines = [_HEADER]
    if title:
        tx = min((t.x for t in placement.values()), default=0) - 40
        ty = min((t.y for t in placement.values()), default=0) - 200
        lines.append(f"T {{{title}}} {tx} {ty} 0 0 0.4 0.4 {{}}")
    placed_devices: list[PlacedDevice] = []
    for dev, symref, sym, aligned in resolved:
        t = placement[dev.ref]
        lines.append(
            f"C {{{symref}}} {t.x} {t.y} {t.rot} {t.flip} {{{_attr_string(_device_attrs(dev, sym))}}}"
        )
        placed_devices.append(
            PlacedDevice(
                ref=dev.ref,
                transform=t,
                nets=dev.nets,
                aligned=aligned,
                text_w=_text_reach(dev, sym),
                is_source=dev.kind in (DeviceKind.VSOURCE, DeviceKind.ISOURCE),
            )
        )

    # 4. Wire it: hybrid (g/s/d wires + supply rails + port pins, bulk by name) or all-labels.
    if wiring == "hybrid":
        info = analyze(placed_circuit)
        plan = plan_connections(
            placed_devices, supply=circuit.supply, port_role=info.port_role
        )
        wires, labels, ports = plan.wires, plan.labels, plan.ports
    else:
        wires, labels, ports = [], build_labels(placed_devices), []

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

    return SchDocument(
        text="\n".join(lines) + "\n",
        warnings=tuple(warnings),
        device_count=len(resolved),
        label_count=len(labels),
        wire_count=len(wires),
        port_count=len(ports),
        annotation_count=annotation_count,
    )


def to_sch(circuit: N2XCircuit, **kwargs) -> str:
    """Convenience: just the ``.sch`` text (see :func:`build_sch` for the full report)."""
    return build_sch(circuit, **kwargs).text
