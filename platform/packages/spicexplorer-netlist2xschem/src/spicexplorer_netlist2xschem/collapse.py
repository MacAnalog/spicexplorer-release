"""Group repeated cells into one added drawing level (issue #264).

A top level of 40 subcircuit instances of 9 cells draws as 40 block symbols on one sheet. A
``--collapse`` group gathers every instance of the named cells into one new cell, drawn one level
down: the parent sheet carries one instance of the group cell, and the group cell's own sheet
carries the slices. No slice gets a sheet of its own. It is a helper a schematic agent asks for;
without it nothing changes, and the agent keeps the placement, the symbols and the hierarchy.

**Grouping is by cell name** (the subcircuit a slice instantiates), never by instance list: a slice
added to the netlist later joins its group on the next run.

**The group cell's ports are computed from the netlist.** A net the slices touch is a port when the
parent declares it (its ``.subckt`` header) or when any device outside the group touches it; every
other net stays inside the group sheet, including a slice pin nothing else connects to. Port sides
come from the slice symbols: a net on any slice's ``out`` pin is an output (right side), a VDD net
goes on top, a VSS/GND net at the bottom, every other net on the left.

:func:`check_collapsed` is the proof: it re-extracts the connectivity of the finished sheets from
their geometry, flattens each group instance through its sheet, and compares every
(instance, pin) terminal and every declared port against the input netlist, in both directions.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace

from .emit import SchDocument, _instance_name, build_sch
from .hierarchy import HierarchicalResult, _child_circuit
from .ingest import Device, DeviceKind, MosPolarity, N2XCircuit
from .mapping import align_pins, symref_for
from .placement import GridPlacer, Placer
from .sch_parser import parse_sch
from .sym_library import Symbol, SymLibrary
from .symbol_gen import BlockPin, generate_block_symbol
from .title_block import TitleBlock
from .virtuoso_export.netex import extract_nets
from .wiring import RouterMode

__all__ = [
    "CollapseGroup",
    "CollapsedResult",
    "CollapseCheck",
    "parse_collapse",
    "build_collapsed_sch",
    "check_collapsed",
]

#: A group cell's name becomes a ``.subckt`` name, a ``.sym``/``.sch`` file name and part of an
#: instance name, so it is held to a SPICE identifier.
_CELL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
#: A cell named in a group: anything a netlist can call, short of the separators the spec uses.
_FAMILY = re.compile(r"^[^\s,=]+$")
#: Grid gap, in schematic units, between the largest symbols on a collapsed sheet. Asked for
#: channels, the router widens a gap that is still too narrow for its lanes
#: (``wiring.spread_channels``).
_GAP = 120
_MIN_PITCH = 240  # GridPlacer's own pitch: a sheet of small symbols keeps the grid it always had
#: The instance key a declared port is compared under in :func:`check_collapsed`.
PORT = "<port>"


@dataclass(frozen=True)
class CollapseGroup:
    """One added drawing level: the cell ``name`` and the cells whose instances it gathers."""

    name: str
    families: tuple[str, ...]


def parse_collapse(spec: str) -> CollapseGroup:
    """Parse one ``--collapse`` value: ``CELL`` or ``GROUP=CELL[,CELL...]``.

    ``CELL`` alone names the group ``<cell>_bank``, a name that does not change when a slice is
    added. Cell names compare case-insensitively, as SPICE does; the group name keeps its case.
    """
    head, sep, tail = spec.partition("=")
    if sep:
        name, families = head.strip(), [f.strip() for f in tail.split(",")]
    else:
        name, families = f"{head.strip()}_bank", [head.strip()]
    if any(not f for f in families):
        raise ValueError(f"--collapse {spec!r}: expected CELL or GROUP=CELL[,CELL...]")
    bad = [f for f in families if not _FAMILY.match(f)]
    if bad:
        raise ValueError(f"--collapse {spec!r}: not a cell name: {', '.join(bad)}")
    if not _CELL_NAME.match(name):
        raise ValueError(
            f"--collapse {spec!r}: group name {name!r} is not a SPICE identifier "
            "(a letter or _, then letters, digits or _)"
        )
    lowered = [f.lower() for f in families]
    if len(set(lowered)) != len(lowered):
        raise ValueError(f"--collapse {spec!r}: a cell is named twice")
    return CollapseGroup(name=name, families=tuple(lowered))


@dataclass(frozen=True)
class CollapsedResult(HierarchicalResult):
    """A collapsed hierarchy; :func:`~.hierarchy.write_hierarchy` writes it like any other.

    ``block_pins`` holds each group cell's computed ports in symbol order, ``device_count`` the
    instances the input level had, and ``parent_instances`` the instances on the parent sheet.
    """

    #: group cell -> the instance refs drawn on its sheet
    groups: dict[str, tuple[str, ...]] = field(default_factory=dict)
    #: group cell -> the name of its one instance on the parent sheet
    group_instances: dict[str, str] = field(default_factory=dict)
    #: cell (lowercase) -> the symref the parent sheet draws it with (``blocks/<cell>.sym``)
    cell_symrefs: dict[str, str] = field(default_factory=dict)
    parent_instances: int = 0
    #: sheet (the parent's cell name, or a group cell) -> "channel" | "per-route"
    routers: dict[str, str] = field(default_factory=dict)
    #: sheet -> the nets that sheet still joins by name rather than by wire
    nets_by_name: dict[str, tuple[str, ...]] = field(default_factory=dict)
    #: sheet -> the document ``build_sch`` returned for it, with its measurements
    #: (:func:`~.report.sheet_report`); the parent sheet is keyed by the input's cell name
    sheets: dict[str, SchDocument] = field(default_factory=dict)
    pdk: str | None = None
    show_device_params: bool = False


def _natural(text: str) -> tuple:
    """Sort key that orders ``d2`` before ``d10``."""
    return tuple(int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", text))


def _family(dev: Device) -> str:
    return dev.model.split()[0].lower() if dev.model else ""


def _overlay(lib: SymLibrary, symbols: Mapping[str, str]) -> SymLibrary:
    """A copy of ``lib`` that also loads each ``blocks/`` symbol, under both of its symrefs."""
    out = SymLibrary(list(lib.search_paths))
    for fname, text in symbols.items():
        out.register(f"blocks/{fname}", text)
        out.register(fname, text)
    return out


def _siblings(cells: Mapping[str, str]) -> dict[str, str]:
    """The symrefs a sheet inside ``blocks/`` uses for the same symbols: the bare file name.

    xschem resolves a relative symref against the directory of the sheet that places it (the
    ``.`` entry of the library path is that directory too): ``blocks/blk_a.sym`` placed by
    ``blocks/grp.sch`` is looked up as ``blocks/blocks/blk_a.sym`` and netlisted as MISSING.
    """
    return {c: ref.removeprefix("blocks/") for c, ref in cells.items()}


def _resolve(
    dev: Device, lib: SymLibrary, pdk: str | None, cells: Mapping[str, str], show_params: bool
) -> Symbol | None:
    symref = cells.get(_family(dev)) if dev.kind is DeviceKind.SUBCKT else None
    symref = symref or symref_for(dev, pdk=pdk, show_params=show_params)
    return lib.load(symref) if symref else None


def _group_pins(
    members: Sequence[Device],
    ports: Sequence[str],
    supply: Mapping[str, str],
    syms: Mapping[str, Symbol | None],
) -> list[BlockPin]:
    """Side each port from the slice symbols' own pin directions (see the module docstring)."""
    dirs: dict[str, set[str]] = {}
    for dev in members:
        sym = syms[dev.ref]
        if sym is None:
            continue
        for canon, sp in align_pins(dev, sym).items():
            dirs.setdefault(dev.nets[canon], set()).add(sp.dir)
    pins: list[BlockPin] = []
    for net in sorted(ports, key=_natural):
        rail, seen = supply.get(net), dirs.get(net, set())
        if rail == "VDD":
            pins.append(BlockPin(net, "top", "inout"))
        elif rail in ("VSS", "GND"):
            pins.append(BlockPin(net, "bottom", "inout"))
        elif "out" in seen:
            pins.append(BlockPin(net, "right", "out"))
        elif seen <= {"in"}:
            pins.append(BlockPin(net, "left", "in"))
        else:
            pins.append(BlockPin(net, "left", "inout"))
    return pins


def _grid(devices: Sequence[Device], syms: Mapping[str, Symbol | None]) -> GridPlacer:
    """A grid whose pitch clears the largest symbol on the sheet by :data:`_GAP`.

    ``GridPlacer`` alone steps 240 units whatever the symbol size. A group cell with 20 pins spans
    about 480 units, the neighbours overlap, and the channel router finds no rows and columns.
    """
    w = h = 0.0
    for dev in devices:
        sym = syms.get(dev.ref)
        if sym is not None and sym.bbox is not None:
            x0, y0, x1, y1 = sym.bbox
            w, h = max(w, x1 - x0), max(h, y1 - y0)
    return GridPlacer(
        pitch_x=max(_MIN_PITCH, int(w) + _GAP), pitch_y=max(_MIN_PITCH, int(h) + _GAP)
    )


def _validate(circuit: N2XCircuit, groups: Sequence[CollapseGroup], present: set[str]) -> None:
    refs = {d.ref.lower() for d in circuit.devices}
    owner: dict[str, str] = {}
    names: set[str] = set()
    for g in groups:
        if g.name.lower() in names:
            raise ValueError(f"--collapse: two groups are named {g.name!r}")
        names.add(g.name.lower())
        if g.name.lower() in present or f"x{g.name}".lower() in refs:
            raise ValueError(f"--collapse: {g.name!r} is already a cell or an instance here")
        for fam in g.families:
            if fam in owner:
                raise ValueError(
                    f"--collapse: cell {fam!r} is in both {owner[fam]!r} and {g.name!r}"
                )
            owner[fam] = g.name


def build_collapsed_sch(
    circuit: N2XCircuit,
    groups: Sequence[CollapseGroup],
    *,
    pdk: str | None = "ihp-sg13g2",
    lib: SymLibrary | None = None,
    cell_symbols: Mapping[str, str] | None = None,
    placer: Placer | None = None,
    title: str | None = None,
    title_block: TitleBlock | None = None,
    show_device_params: bool = False,
    router: RouterMode = "per-route",
) -> CollapsedResult:
    """Draw ``circuit`` with each group of repeated cells moved one level down.

    ``groups`` come from :func:`parse_collapse`. ``cell_symbols`` maps a cell name to the ``.sym``
    TEXT its instances are drawn with; each is written as ``blocks/<cell>.sym`` beside the group
    sheets. A cell absent from it is drawn with the symbol registered for it
    (:func:`~.mapping.register_subckt_symbol`), as on a flat sheet.

    ``placer`` places every sheet; the default is a grid whose pitch clears the largest symbol on
    that sheet by 120 units. ``router`` is passed to :func:`~.emit.build_sch` for every sheet: the
    default draws them with the per-route planner, ``"channel"`` routes each block diagram by
    channels. Raises ``ValueError`` for a cell named in two groups, two groups of
    one name, or a group name that is already a cell or an instance (``x<name>``) at this level.
    A group that finds fewer than two instances is not formed, with a warning.
    """
    present = {_family(d) for d in circuit.devices if d.kind is DeviceKind.SUBCKT}
    _validate(circuit, groups, present)
    warnings: list[str] = []
    symbols = {f"{c}.sym": text for c, text in (cell_symbols or {}).items()}
    cells = {c.lower(): f"blocks/{c}.sym" for c in (cell_symbols or {})}
    lib_ = _overlay(lib or SymLibrary.default(), symbols)

    def resolve(dev: Device) -> Symbol | None:
        return _resolve(dev, lib_, pdk, cells, show_device_params)

    syms = {d.ref: resolve(d) for d in circuit.devices}
    sheets: dict[str, SchDocument] = {}
    block_pins: dict[str, tuple[str, ...]] = {}
    grouped: dict[str, tuple[str, ...]] = {}
    group_devices: list[Device] = []

    for g in groups:
        warnings.extend(
            f"--collapse {g.name}: no instance of {fam!r} at this level"
            for fam in g.families
            if fam not in present
        )
        members = [
            d for d in circuit.devices if d.kind is DeviceKind.SUBCKT and _family(d) in g.families
        ]
        if len(members) < 2:
            warnings.append(
                f"--collapse {g.name}: {len(members)} instance(s), nothing grouped "
                "(a group of one adds a level and removes no instance)"
            )
            continue
        member_refs = {d.ref for d in members}
        inside = {net for d in members for net in d.nets.values()}
        outside = {
            net for d in circuit.devices if d.ref not in member_refs for net in d.nets.values()
        }
        ports = [n for n in inside if n in circuit.ports or n in outside]
        if not ports:
            warnings.append(f"--collapse {g.name}: no net leaves the group, nothing grouped")
            continue
        pins = _group_pins(members, ports, circuit.supply, syms)
        order = tuple(p.net for p in pins)
        symbols[f"{g.name}.sym"] = generate_block_symbol(g.name, pins).text
        lib_.register(f"blocks/{g.name}.sym", symbols[f"{g.name}.sym"])
        lib_.register(f"{g.name}.sym", symbols[f"{g.name}.sym"])
        cells[g.name.lower()] = f"blocks/{g.name}.sym"
        sheets[g.name] = build_sch(
            _child_circuit(members, g.name, list(order), circuit.supply),
            pdk=pdk,
            lib=lib_,
            placer=placer or _grid(members, syms),
            title=g.name,
            show_device_params=show_device_params,
            cell_symbols=_siblings(cells),
            port_roles={p.net: p.direction for p in pins},
            router=router,
        )
        block_pins[g.name] = order
        grouped[g.name] = tuple(sorted(member_refs, key=_natural))
        group_devices.append(
            Device(
                ref=f"x{g.name}",
                kind=DeviceKind.SUBCKT,
                model=g.name,
                polarity=MosPolarity.UNKNOWN,
                pins=order,
                nets={p: p for p in order},
                params={},
            )
        )

    taken = {ref for refs in grouped.values() for ref in refs}
    devices = (*(d for d in circuit.devices if d.ref not in taken), *group_devices)
    nets = tuple(sorted({n for d in devices for n in d.nets.values()}))
    parent = replace(
        circuit,
        devices=devices,
        nets=nets,
        supply={n: r for n, r in circuit.supply.items() if n in nets},
        ports=tuple(p for p in circuit.ports if p in nets),
    )
    syms.update({d.ref: resolve(d) for d in group_devices})
    top = build_sch(
        parent,
        pdk=pdk,
        lib=lib_,
        placer=placer or _grid(devices, syms),
        title=title or circuit.name,
        title_block=title_block,
        show_device_params=show_device_params,
        cell_symbols=cells,
        router=router,
    )
    warnings.extend(top.warnings)
    for name, doc in sheets.items():
        warnings.extend(f"{name}: {w}" for w in doc.warnings)
    return CollapsedResult(
        parent_text=top.text,
        children={f"{name}.sch": doc.text for name, doc in sheets.items()},
        symbols=symbols,
        block_pins=block_pins,
        warnings=tuple(warnings),
        block_count=len(grouped),
        device_count=len(circuit.devices),
        groups=grouped,
        group_instances={g: f"x{g}" for g in grouped},
        cell_symrefs=cells,
        parent_instances=top.device_count,
        routers={circuit.name: top.router, **{n: d.router for n, d in sheets.items()}},
        nets_by_name={
            circuit.name: top.nets_by_name,
            **{n: d.nets_by_name for n, d in sheets.items()},
        },
        sheets={circuit.name: top, **sheets},
        pdk=pdk,
        show_device_params=show_device_params,
    )


@dataclass(frozen=True)
class CollapseCheck:
    """The finished sheets flattened through both levels, against the input netlist.

    Terminals are (instance, pin) pairs; a declared port of the drawn level counts as the
    terminal ``("<port>", name)``. ``split`` names an input net drawn as more than one net,
    ``merged`` a drawn net that joins two or more input nets, ``missing``/``extra`` a terminal
    found on one side only, ``duplicate`` an instance drawn more than once over all the sheets
    (a slice on both the parent sheet and its group sheet, or twice on one sheet), and
    ``port_mismatch`` a group whose sheet port pins differ from its symbol pins.
    """

    terminals: int
    nets: int
    split: tuple[str, ...] = ()
    merged: tuple[tuple[str, ...], ...] = ()
    missing: tuple[tuple[str, str], ...] = ()
    extra: tuple[tuple[str, str], ...] = ()
    port_mismatch: tuple[str, ...] = ()
    duplicate: tuple[str, ...] = ()

    @property
    def identical(self) -> bool:
        return not (
            self.split
            or self.merged
            or self.missing
            or self.extra
            or self.port_mismatch
            or self.duplicate
        )


def check_collapsed(
    result: CollapsedResult, circuit: N2XCircuit, *, lib: SymLibrary | None = None
) -> CollapseCheck:
    """Flatten the finished sheets of ``result`` and compare them with ``circuit``.

    Each sheet's connectivity is extracted from its geometry (wires, labels, port pins and pin
    positions; :func:`~.virtuoso_export.netex.extract_nets`), not taken from the plan that drew
    it. A group sheet's net that reaches one of its port pins is the parent net on the group
    instance's pin of that name; any other net on it belongs to that instance alone. A port pin
    on the parent sheet counts when the input declares that port; the parent sheet may draw
    more (every one-terminal net, as a flat sheet does), and those are not compared.

    Every instance must be drawn once. Terminals are compared by (instance, pin), so a slice drawn
    on both the parent sheet and its group sheet would otherwise compare as one terminal; the
    instance names on all the sheets are counted, and a repeat is reported in ``duplicate``.
    """
    lib_ = _overlay(lib or SymLibrary.default(), result.symbols)
    drawn_count: Counter[str] = Counter()

    def read(text: str):
        sch = parse_sch(text)
        drawn_count.update(c.name for c in sch.components if c.is_device)
        return extract_nets(sch, lib_)

    parent = read(result.parent_text)
    declared = set(circuit.ports)
    drawn: dict[tuple[str, str], tuple[str, str]] = {
        (PORT, p.name): ("", p.name) for p in parent.ports if p.name in declared
    }
    instances = set(result.group_instances.values())
    for (inst, pin), pn in parent.pin_nets.items():
        if inst not in instances:
            drawn[(inst, pin)] = ("", pn.net)
    mismatch: list[str] = []
    for g, inst in sorted(result.group_instances.items()):
        sheet = read(result.children[f"{g}.sch"])
        ports = set(result.block_pins[g])
        on_sheet = {p.name for p in sheet.ports}
        if on_sheet != ports:
            mismatch.append(
                f"{g}: symbol pins not on the sheet {sorted(ports - on_sheet)}, "
                f"sheet ports not on the symbol {sorted(on_sheet - ports)}"
            )
        for (cinst, pin), pn in sheet.pin_nets.items():
            outer = parent.pin_nets.get((inst, pn.net)) if pn.net in ports else None
            drawn[(cinst, pin)] = ("", outer.net) if outer is not None else (inst, pn.net)

    expected: dict[tuple[str, str], str] = {(PORT, p): p for p in circuit.ports}
    for dev in circuit.devices:
        sym = _resolve(dev, lib_, result.pdk, result.cell_symrefs, result.show_device_params)
        if sym is None:
            expected.update({(dev.ref, canon): dev.nets[canon] for canon in dev.pins})
            continue
        name = _instance_name(dev, sym)
        for canon, sp in align_pins(dev, sym).items():
            expected[(name, sp.name)] = dev.nets[canon]

    forward: dict[str, set[tuple[str, str]]] = {}
    backward: dict[tuple[str, str], set[str]] = {}
    common = set(expected) & set(drawn)
    for key in common:
        forward.setdefault(expected[key], set()).add(drawn[key])
        backward.setdefault(drawn[key], set()).add(expected[key])
    return CollapseCheck(
        terminals=len(common),
        nets=len(forward),
        split=tuple(sorted(n for n, d in forward.items() if len(d) > 1)),
        merged=tuple(sorted(tuple(sorted(e)) for e in backward.values() if len(e) > 1)),
        missing=tuple(sorted(set(expected) - set(drawn))),
        extra=tuple(sorted(set(drawn) - set(expected))),
        port_mismatch=tuple(mismatch),
        duplicate=tuple(sorted(name for name, n in drawn_count.items() if n > 1)),
    )
