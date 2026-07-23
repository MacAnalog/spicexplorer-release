"""Strategy 1 — render a netlist as a *true xschem hierarchy* of block symbols.

Where strategy 2 (:mod:`stamp`) keeps one flat schematic and just lays each block out symmetrically,
this mode lifts each recognised block into its **own** child schematic and draws it on the parent as a
single labelled block symbol — the way an engineer reads an OTA: a differential pair box, a mirror box,
wired together, each openable. It is the documented "blocks → subcircuit symbols on the parent" form.

For each top-level block we:

1. compute its **boundary nets** (the nets it shares with the rest of the circuit, plus supplies) — they
   become the block's interface; nets touched only inside the block stay private;
2. extract the block's devices into a child :class:`~.ingest.N2XCircuit` (boundary nets as ``ports``)
   and render it with :func:`~.emit.build_sch` → a child ``.sch`` (the ``.subckt`` definition);
3. generate a ``type=subcircuit`` symbol for it (:func:`~.symbol_gen.generate_block_symbol`) whose pins
   are the boundary nets.

The parent instantiates every block symbol and the leftover (un-blocked) devices and wires them with the
**same connection engine the flat schematic uses** (:func:`~.wiring.plan_connections`): VDD/VSS **rails**
with each block's supply pin flushed onto them (the symbol exposes VDD on its top edge, VSS on its
bottom), independent **sources grouped** in a bottom-left stack and named in place, circuit-I/O **ports**
at the edges, and signal nets drawn as wires (falling back to a net-name label where a wire would short).
A block is just a multi-pin device to that engine — each boundary-net pin's name *is* its net. Because
the child ports, the symbol pins and the parent labels/rails all carry the *same* net names, ``xschem
-n`` on the parent descends into the children and re-netlists to the original flat circuit
(connectivity-neutral; verified by the round-trip).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .analysis import analyze
from .emit import _HEADER, _attr_string, _device_attrs, _fmt_value, build_sch
from .geometry import Transform, apply_transform, snap
from .ingest import Device, DeviceKind, N2XCircuit
from .mapping import LABEL_SYMREF, align_pins, symref_for
from .sym_library import Symbol, SymLibrary
from .symbol_gen import BlockPin, BlockSymbol, generate_block_symbol

__all__ = ["HierarchicalResult", "build_hierarchical_sch", "write_hierarchy"]

_BLOCK_GAP = 220  # horizontal gap between block symbols on the parent
_ROW_GAP = 240  # vertical gap from the block band to a rail-affinity leftover-device row
_DEV_PITCH = 220  # horizontal pitch between leftover devices on one parent row
_SRC_PITCH = 220  # vertical pitch of the bottom-left independent-source stack
_STUB = 40  # length of the short wire stub grown off each pin (so net colouring shows a coloured lead)
_DRIVEN_ROLES = frozenset({"DRAIN", "SOURCE", "P", "N"})  # a net a block *drives* (an output side)
_SOURCE_KINDS = frozenset({DeviceKind.VSOURCE, DeviceKind.ISOURCE})  # independent V/I sources


@dataclass(frozen=True)
class HierarchicalResult:
    """A hierarchical schematic: the parent text plus the child ``.sch`` and ``.sym`` files it needs."""

    parent_text: str
    children: dict[str, str] = field(default_factory=dict)  # "<name>.sch" -> text
    symbols: dict[str, str] = field(default_factory=dict)  # "<name>.sym" -> text
    block_pins: dict[str, tuple[str, ...]] = field(default_factory=dict)  # "<name>" -> boundary nets
    warnings: tuple[str, ...] = ()
    block_count: int = 0
    device_count: int = 0


def _safe_name(block_id: str, taken: set[str]) -> str:
    """A unique, netlist-legal subckt name from a block id (``cm.nmos.simple#1`` → ``cm_nmos_simple_1``)."""
    base = re.sub(r"[^0-9A-Za-z]+", "_", block_id).strip("_").lower() or "block"
    if base[0].isdigit():
        base = f"b_{base}"
    name = base
    i = 1
    while name in taken:
        i += 1
        name = f"{base}_{i}"
    taken.add(name)
    return name


def _boundary_pins(
    circuit: N2XCircuit,
    block_devs: list[Device],
    boundary: list[str],
    port_names: Mapping[str, str] | None = None,
) -> list[BlockPin]:
    """Classify each boundary net into a symbol pin: VDD on **top**, VSS/GND on the **bottom**,
    gate-only inputs left, driven nets (a drain/source/passive terminal) outputs right. Deterministic
    (sorted by net).

    Siding the supplies by rail is what lets the parent's VDD/VSS rails connect cleanly: a block's VDD
    pin faces *up* toward the top rail and its VSS pin faces *down* toward the bottom rail, instead of
    both hanging off the symbol's bottom edge and crossing the body to reach a rail.

    ``port_names`` (from the contract: host net → the template's functional port name) sets each pin's
    **display label** — so the box reads ``out`` / ``ref_in`` / ``supply`` instead of the host net. The
    pin's connection ``name`` stays the net (xschem still matches it to the child port); only the drawn
    text changes. A net absent from the map keeps the net as its label."""
    port_names = port_names or {}
    roles: dict[str, set[str]] = {}
    for dev in block_devs:
        for pin, net in dev.nets.items():
            roles.setdefault(net, set()).add(pin)
    pins: list[BlockPin] = []
    for net in sorted(boundary):
        label = port_names.get(net, "")
        rail = circuit.supply.get(net)
        if rail == "VDD":
            pins.append(BlockPin(net, "top", "inout", label=label))
        elif rail in ("VSS", "GND"):
            pins.append(BlockPin(net, "bottom", "inout", label=label))
        elif roles.get(net, set()) & _DRIVEN_ROLES:
            pins.append(BlockPin(net, "right", "out", label=label))
        else:
            pins.append(BlockPin(net, "left", "in", label=label))
    return pins


def _child_circuit(
    block_devs: list[Device], name: str, boundary: list[str]
) -> N2XCircuit:
    """Extract the block's devices into a sub-circuit whose ports are *all* its boundary nets.

    Supplies are passed as ``supply={}`` deliberately: a boundary supply must surface as a real subckt
    **port** (an ``iopin``), not a drawn rail — otherwise the child's ``.subckt`` port list wouldn't
    match the generated symbol's pins and the hierarchy wouldn't re-netlist. Standard practice anyway:
    an IC sub-block exposes VDD/VSS as explicit power pins. Wiring is still by net name inside.
    """
    nets = tuple(sorted({net for dev in block_devs for net in dev.nets.values()}))
    return N2XCircuit(
        name=name,
        devices=tuple(block_devs),
        nets=nets,
        supply={},
        ports=tuple(sorted(boundary)),
    )


def _symbol_extent(sym: BlockSymbol) -> tuple[int, int]:
    """(half-width, half-height) of a block symbol from its outermost pin connection points."""
    if not sym.pins:
        return (80, 60)
    hw = max(abs(x) for x, _ in sym.pins.values())
    hh = max(abs(y) for _, y in sym.pins.values())
    return (hw, hh)


def build_hierarchical_sch(
    circuit: N2XCircuit,
    annotations,
    *,
    pdk: str | None = "ihp-sg13g2",
    lib: SymLibrary | None = None,
    title: str | None = None,
    child_placement: str = "block-aware",
    template_root: Path | None = None,
    show_device_params: bool = False,
) -> HierarchicalResult:
    """Render ``circuit`` as a hierarchy: one block symbol per detected block on a parent schematic.

    ``annotations`` is the recognised-block contract (its *top-level* blocks become subcircuits).
    ``child_placement`` is the placement mode for each block's interior (``"template-stamp"`` makes the
    children symmetric too); ``template_root`` is forwarded to stamping. Returns the parent text plus the
    child ``.sch`` / ``.sym`` files; :func:`write_hierarchy` materialises them.
    """
    lib = lib or SymLibrary.default()
    warnings: list[str] = []

    # Circuit-level I/O nets (e.g. a differential pair's gate inputs, which touch *only* the block but
    # still go to the outside world). They must count as boundary nets even though no other device shares
    # them — otherwise a block's pure inputs/outputs would vanish from its symbol.
    io_nets = set(analyze(circuit).port_role)

    # Map ref -> device, and the set of refs each top-level block owns.
    dev_by_ref = {d.ref: d for d in circuit.devices}
    blocks = [b for b in annotations.blocks if b.parent_id is None] if annotations else []
    blocked_refs: set[str] = set()
    taken_names: set[str] = set()

    children: dict[str, str] = {}
    symbols: dict[str, str] = {}
    block_pins: dict[str, tuple[str, ...]] = {}
    placed_blocks: list[tuple[str, BlockSymbol]] = []  # (instance name, block symbol)

    for b in blocks:
        members = [dev_by_ref[r] for r in b.devices if r in dev_by_ref]
        if len(members) < 2:
            continue  # a 1-device "block" isn't worth a subcircuit
        member_refs = {d.ref for d in members}
        block_nets = {net for d in members for net in d.nets.values()}
        outside_nets = {
            net
            for d in circuit.devices
            if d.ref not in member_refs
            for net in d.nets.values()
        } | set(circuit.supply) | set(circuit.ports)
        # A net is a boundary pin if it is shared with another device, is a supply/port, is a circuit
        # I/O net (a diff pair's gate inputs touch only the block, yet are external), or is one of the
        # block's own declared template ports (``port_names`` — authoritative, so an input that nothing
        # else shares still surfaces). The intersection with ``block_nets`` keeps internal nets out.
        boundary = sorted(block_nets & (outside_nets | io_nets | set(b.port_names())))
        if not boundary:
            continue  # fully internal (can't happen for a real sub-block) — skip
        name = _safe_name(b.block_id, taken_names)

        child = _child_circuit(members, name, boundary)
        child_doc = build_sch(
            child,
            pdk=pdk,
            lib=lib,
            title=name,
            annotations=_single_block_annotations(b) if child_placement == "template-stamp" else None,
            placement_mode=child_placement if child_placement == "template-stamp" else None,
            template_root=template_root,
            show_device_params=show_device_params,
        )
        warnings.extend(f"{name}: {w}" for w in child_doc.warnings)
        children[f"{name}.sch"] = child_doc.text

        sym = generate_block_symbol(
            name, _boundary_pins(circuit, members, boundary, b.port_names())
        )
        symbols[f"{name}.sym"] = sym.text
        block_pins[name] = tuple(boundary)

        placed_blocks.append((f"x{name}", sym))
        blocked_refs |= member_refs

    leftover = [d for d in circuit.devices if d.ref not in blocked_refs]
    parent_text = _emit_parent(
        placed_blocks, leftover, lib, circuit=circuit, pdk=pdk,
        title=title or circuit.name, warnings=warnings,
        show_device_params=show_device_params,
    )
    return HierarchicalResult(
        parent_text=parent_text,
        children=children,
        symbols=symbols,
        block_pins=block_pins,
        warnings=tuple(warnings),
        block_count=len(placed_blocks),
        device_count=len(circuit.devices),
    )


def _single_block_annotations(block):
    """A one-block annotation set (the given block) — to template-stamp a child's interior."""
    from .annotation import BlockAnnotationSet

    return BlockAnnotationSet((block,))


def _rail_affinity(dev: Device, supply: Mapping[str, str]) -> str:
    """Which rail band a leftover device belongs in: ``"top"`` (touches VDD only), ``"bottom"``
    (touches VSS/GND only), or ``"mid"`` (both or neither). The analogue, for the parent's loose
    devices, of the flat placer's VDD-at-top / VSS-at-bottom banding."""
    nets = set(dev.nets.values())
    vdd = any(supply.get(n) == "VDD" for n in nets)
    vss = any(supply.get(n) in ("VSS", "GND") for n in nets)
    if vdd and not vss:
        return "top"
    if vss and not vdd:
        return "bottom"
    return "mid"


def _parent_floorplan(
    placed_blocks: list[tuple[str, BlockSymbol]],
    leftover_resolved: list[tuple[Device, str, Symbol, dict]],
    supply: Mapping[str, str],
) -> dict[str, Transform]:
    """A rail-aware floorplan for the parent: block symbols in a centred row at ``y=0``; leftover
    devices banded above/below by rail affinity (VDD-only just above the blocks, VSS-only below);
    independent sources grouped in a stack at the bottom-left, out of the signal path. Returns a
    ``ref/instance -> Transform`` map (block instances keyed by their ``x…`` instance name)."""
    pos: dict[str, Transform] = {}

    # Blocks: a centred row at y=0, packed left-to-right by symbol width.
    exts = [(inst, sym, _symbol_extent(sym)) for inst, sym in placed_blocks]
    total_w = sum(2 * hw for _, _, (hw, _) in exts) + _BLOCK_GAP * max(len(exts) - 1, 0)
    cursor = -total_w / 2.0
    block_half_h = 60
    for inst, _sym, (hw, hh) in exts:
        pos[inst] = Transform(snap(int(round(cursor + hw))), 0, 0, 0)
        block_half_h = max(block_half_h, hh)
        cursor += 2 * hw + _BLOCK_GAP

    # Leftover devices: sources go bottom-left; everything else bands above/below by rail affinity. A
    # VDD-only device rides one row *above* the blocks (near the top rail), everything else one row
    # below (kept to a single row so a loose device never drags the bottom rail — and its supply stubs —
    # far down the page).
    sources = [r for r in leftover_resolved if r[0].kind in _SOURCE_KINDS]
    above: list[tuple[Device, str, Symbol, dict]] = []
    below: list[tuple[Device, str, Symbol, dict]] = []
    for r in leftover_resolved:
        if r[0].kind in _SOURCE_KINDS:
            continue
        (above if _rail_affinity(r[0], supply) == "top" else below).append(r)

    for items, y in ((above, -(block_half_h + _ROW_GAP)), (below, block_half_h + _ROW_GAP)):
        n = len(items)
        for i, (dev, *_rest) in enumerate(sorted(items, key=lambda r: r[0].ref)):
            x = snap(int(round((i - (n - 1) / 2.0) * _DEV_PITCH)))
            pos[dev.ref] = Transform(x, snap(int(y)), 0, 0)

    # Independent sources: a stack at the bottom-left, climbing *upward* from the floor (as the flat
    # placer does) so they sit beside the circuit instead of below it — never dragging the VSS rail down.
    # They wire by net name only (never routed), so this just groups the bias/test sources out of the way.
    if sources:
        xs = [t.x for t in pos.values()] or [0]
        ys = [t.y for t in pos.values()] or [0]
        sx, sy = snap(min(xs) - _DEV_PITCH), max(ys)
        for dev, *_rest in sorted(sources, key=lambda r: r[0].ref):
            pos[dev.ref] = Transform(sx, snap(int(sy)), 0, 0)
            sy -= _SRC_PITCH
    return pos


def _pin_stub(px: int, py: int, ox: int, oy: int) -> tuple[int, int, int, int]:
    """A short **outward** stub off a pin, plus the ``(rot, flip)`` that makes its net-name label read
    away from the block. The stub is what render-time net colouring paints, so two pins on one net show
    the same coloured lead — the block-diagram stand-in for a routed wire."""
    dx, dy = px - ox, py - oy
    if abs(dy) >= abs(dx):  # vertical pin (a block's top/bottom edge): stub up or down
        if dy >= 0:
            return px, py + _STUB, 2, 0  # downward — label below the endpoint, reading right
        return px, py - _STUB, 0, 1  # upward — label above the endpoint, reading right
    if dx >= 0:
        return px + _STUB, py, 0, 1  # rightward — label continues to the right
    return px - _STUB, py, 0, 0  # leftward — label continues to the left


def _emit_parent(
    placed_blocks: list[tuple[str, BlockSymbol]],
    leftover: list[Device],
    lib: SymLibrary,
    *,
    circuit: N2XCircuit,
    pdk: str | None,
    title: str,
    warnings: list[str],
    show_device_params: bool = False,
) -> str:
    """Draw the parent: block symbols + leftover devices laid out rail-aware, their connections shown by
    **render-time net colouring** rather than routed wires.

    Wiring big block symbols into a flat tree reads as a tangle; instead every pin grows a short
    **stub + net-name label**, and the renderer colours each net's stubs and labels with one palette
    colour — so two pins on the same net show the same coloured lead and read as one node. Independent
    sources are still grouped bottom-left (placement, not wiring). A block's interior stays in its child
    ``.sch``; here it is one box whose boundary-net pins are named and colour-coded."""
    # Resolve a symbol for each leftover device (skip + warn on the unmappable), exactly as build_sch.
    resolved: list[tuple[Device, str, Symbol, dict]] = []
    for dev in leftover:
        symref = symref_for(dev, pdk=pdk, show_params=show_device_params)
        sym = lib.load(symref) if symref else None
        if symref is None or sym is None:
            warnings.append(f"{dev.ref}: no symbol for kind={dev.kind.value}; omitted from parent")
            continue
        aligned = align_pins(dev, sym)
        if any(p not in aligned for p in dev.pins):
            warnings.append(f"{dev.ref}: pins could not be aligned; omitted from parent")
            continue
        resolved.append((dev, symref, sym, aligned))

    pos = _parent_floorplan(placed_blocks, resolved, circuit.supply)

    lines = [_HEADER]
    if title:
        tx = min((t.x for t in pos.values()), default=0) - 40
        ty = min((t.y for t in pos.values()), default=0) - 200
        lines.append(f"T {{{title}}} {tx} {ty} 0 0 0.4 0.4 {{}}")

    # Instances: block symbols, then leftover devices.
    for inst, sym in placed_blocks:
        t = pos[inst]
        lines.append(f"C {{blocks/{sym.name}.sym}} {t.x} {t.y} 0 0 {{name={inst}}}")
    for dev, symref, sym, _aligned in resolved:
        t = pos[dev.ref]
        lines.append(
            f"C {{{symref}}} {t.x} {t.y} {t.rot} {t.flip} {{{_attr_string(_device_attrs(dev, sym))}}}"
        )

    # Connections: a colour-coded stub + net-name label off every pin (blocks then leftover devices). No
    # routed tree and no rails — render-time net colouring is what shows two same-net pins are one node.
    idx = 0

    def stub_label(px: int, py: int, ox: int, oy: int, net: str) -> None:
        nonlocal idx
        ex, ey, rot, flip = _pin_stub(px, py, ox, oy)
        lines.append(f"N {px} {py} {ex} {ey} {{}}")
        lines.append(
            f"C {{{LABEL_SYMREF}}} {ex} {ey} {rot} {flip} {{name=l{idx} lab={_fmt_value(net)}}}"
        )
        idx += 1

    for inst, sym in placed_blocks:
        t = pos[inst]
        for net, (sx, sy) in sym.pins.items():
            stub_label(t.x + sx, t.y + sy, t.x, t.y, net)
    for dev, _symref, sym, aligned in resolved:
        t = pos[dev.ref]
        for canon, sp in aligned.items():
            ax, ay = apply_transform(t, sp.x, sp.y)
            stub_label(ax, ay, t.x, t.y, dev.nets[canon])
    return "\n".join(lines) + "\n"


def write_hierarchy(
    result: HierarchicalResult, outdir: str | Path, *, parent_name: str = "parent"
) -> Path:
    """Materialise a :class:`HierarchicalResult` under ``outdir``: parent ``.sch`` + ``blocks/*.{sym,sch}``.

    The children and symbols go in a ``blocks/`` subdirectory the parent references as ``blocks/<name>.sym``;
    xschem resolves both the symbol and its like-named child schematic there. Returns the parent path.
    """
    out = Path(outdir)
    (out / "blocks").mkdir(parents=True, exist_ok=True)
    for fname, text in result.symbols.items():
        (out / "blocks" / fname).write_text(text)
    for fname, text in result.children.items():
        (out / "blocks" / fname).write_text(text)
    parent = out / f"{parent_name}.sch"
    parent.write_text(result.parent_text)
    return parent
