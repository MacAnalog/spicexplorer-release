"""Geometric net extraction from a parsed xschem schematic.

xschem stores no netlist in the ``.sch`` — connectivity is implied by geometry plus names,
with three binding mechanisms this module reproduces:

* **wires touch**: two ``N`` segments sharing an endpoint, or one segment ending *on* another
  (a T-junction), are the same electrical net;
* **names bind**: a ``lab_wire``/``lab_pin`` component (or a wire's own ``lab=`` attribute)
  names the net its point sits on, and *equal names join disjoint groups* — including
  circuit port pins (``ipin``/``opin``/``iopin``), which bind **by their ``lab`` only**
  (real corpus schematics park them far away from any wire);
* **pins touch**: a device pin — the transformed centre of its symbol's ``B 5`` box — joins
  whatever wire/pin group occupies that point.

The output is exactly what the Mode-A emitter needs: a net name per instance terminal, the
port list, and a stub direction per terminal (the direction the attached wire leaves the pin,
so the drawn net-label stub retraces the original drawing instead of colliding with the body).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..geometry import Transform, apply_transform
from ..sch_parser import SchComponent, Schematic
from ..sym_library import SymLibrary

__all__ = ["PinNet", "PortPin", "NetExtraction", "extract_nets"]

_TOL = 0.51  # point-coincidence tolerance in xschem units (grid is 5; keys round to 0.5)


@dataclass(frozen=True)
class PinNet:
    """One device terminal resolved to a net: absolute pin point + outward stub direction."""

    inst: str
    pin: str
    net: str
    x: float
    y: float
    stub_dir: tuple[float, float] = (1.0, 0.0)  # xschem frame, axis-aligned unit vector
    # True when the pin point touches a drawn wire segment. False means the binding came
    # from a label/port sitting directly on the pin — wire-mode must name-stub it, since a
    # geometric patch would connect to nothing.
    on_wire: bool = True


@dataclass(frozen=True)
class PortPin:
    """A circuit I/O port: net name, direction (``in``/``out``/``inout``), drawn location."""

    name: str
    direction: str
    x: float
    y: float


@dataclass
class NetExtraction:
    """The extraction result. ``pin_nets`` is keyed ``(instance name, xschem pin name)``."""

    pin_nets: dict[tuple[str, str], PinNet] = field(default_factory=dict)
    ports: list[PortPin] = field(default_factory=list)
    nets: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)
    # net name -> its wire segments (xschem coords), pre-split at every electrical node so
    # all junctions are endpoint-to-endpoint (Virtuoso does not auto-connect a wire endpoint
    # landing on another wire's interior) — what wire-mode draws.
    net_segments: dict[str, list[tuple[float, float, float, float]]] = field(default_factory=dict)


def _key(x: float, y: float) -> tuple[int, int]:
    return (round(x * 2), round(y * 2))


class _UnionFind:
    def __init__(self) -> None:
        self._parent: dict[tuple[int, int], tuple[int, int]] = {}

    def add(self, k: tuple[int, int]) -> None:
        self._parent.setdefault(k, k)

    def find(self, k: tuple[int, int]) -> tuple[int, int]:
        self.add(k)
        root = k
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[k] != root:  # path compression
            self._parent[k], k = root, self._parent[k]
        return root

    def union(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra

    def keys(self) -> list[tuple[int, int]]:
        return list(self._parent)


def _on_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> bool:
    """True when point ``(px,py)`` lies on segment ``(x1,y1)-(x2,y2)`` within tolerance."""
    if not (min(x1, x2) - _TOL <= px <= max(x1, x2) + _TOL):
        return False
    if not (min(y1, y2) - _TOL <= py <= max(y1, y2) + _TOL):
        return False
    cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    seg_len = max(abs(x2 - x1), abs(y2 - y1), 1e-9)
    return abs(cross) / seg_len <= _TOL


def _port_direction(comp: SchComponent) -> str:
    base = comp.symref.rsplit("/", 1)[-1]
    return {"ipin.sym": "in", "opin.sym": "out"}.get(base, "inout")


def _is_label_component(comp: SchComponent, symlib: SymLibrary) -> bool:
    """A net-label component: ``lab_wire``/``lab_pin`` or any symbol whose K-type is label."""
    if comp.is_label:
        return True
    sym = symlib.load(comp.symref)
    return sym is not None and sym.type == "label"


def _stub_direction(
    px: float,
    py: float,
    segments: list[tuple[float, float, float, float]],
    origin: tuple[float, float],
) -> tuple[float, float]:
    """The axis-aligned unit direction a stub should leave pin ``(px,py)``.

    Prefer the direction the attached wire leaves the pin (retraces the drawing) — but
    never INTO the instance body: labels-mode stubs start at the *kit* master's real pin
    centre, which may sit closer to the instance origin than the xschem pin; an inward
    stub can then land its labeled endpoint exactly on a neighboring kit pin and short two
    nets (found by the reverse round-trip, where dumped stub wires point at the body).
    When no wire touches the pin, point away from the instance origin.
    """
    for x1, y1, x2, y2 in segments:
        for ex, ey, ox, oy in ((x1, y1, x2, y2), (x2, y2, x1, y1)):
            if abs(ex - px) <= _TOL and abs(ey - py) <= _TOL:
                dx, dy = ox - ex, oy - ey
                if abs(dx) >= abs(dy):
                    d: tuple[float, float] = (1.0, 0.0) if dx >= 0 else (-1.0, 0.0)
                else:
                    d = (0.0, 1.0) if dy >= 0 else (0.0, -1.0)
                rx, ry = px - origin[0], py - origin[1]
                if d[0] * rx + d[1] * ry < 0:  # wire heads toward the origin — flip out
                    d = (-d[0], -d[1])
                return d
    dx, dy = px - origin[0], py - origin[1]
    if dx == dy == 0:
        return (1.0, 0.0)
    if abs(dx) >= abs(dy):
        return (1.0, 0.0) if dx >= 0 else (-1.0, 0.0)
    return (0.0, 1.0) if dy >= 0 else (0.0, -1.0)


def extract_nets(sch: Schematic, symlib: SymLibrary | None = None) -> NetExtraction:
    """Resolve every device terminal of ``sch`` to a net (see the module docstring)."""
    symlib = symlib or SymLibrary.default()
    out = NetExtraction()
    uf = _UnionFind()

    segments = [(w.x1, w.y1, w.x2, w.y2) for w in sch.wires]
    for x1, y1, x2, y2 in segments:
        uf.union(_key(x1, y1), _key(x2, y2))
        # connectivity keys snap to the 0.5 grid; an off-grid endpoint (imported/odd
        # files) can alias two distinct points onto one node — warn once
        for v in (x1, y1, x2, y2):
            if abs(v * 2 - round(v * 2)) > 1e-6:
                msg = (
                    f"off-grid wire coordinate {v!r} — connectivity keys round to the "
                    "0.5 grid; review the extraction on this drawing"
                )
                if msg not in out.warnings:
                    out.warnings.append(msg)

    # Collect every electrical point: wire endpoints are already nodes; add device pins,
    # labels, and ports, then merge T-junctions (any node lying on a segment's interior).
    pin_points: list[tuple[str, str, float, float, tuple[float, float]]] = []
    label_points: list[tuple[str, float, float]] = []  # (net name, x, y)

    for comp in sch.components:
        if _is_label_component(comp, symlib):
            sym = symlib.load(comp.symref)
            lab = comp.lab or (sym.template.get("lab", "") if sym else "")
            if lab:
                label_points.append((lab, comp.x, comp.y))
                uf.add(_key(comp.x, comp.y))
            continue
        if comp.is_port:
            lab = comp.lab or comp.name
            out.ports.append(PortPin(name=lab, direction=_port_direction(comp), x=comp.x, y=comp.y))
            label_points.append((lab, comp.x, comp.y))
            uf.add(_key(comp.x, comp.y))
            continue
        if not comp.is_device:
            continue
        sym = symlib.load(comp.symref)
        if sym is None:
            out.warnings.append(f"symbol not resolvable: {comp.symref} (instance {comp.name})")
            continue
        if any(name == comp.name for name, _pin, _x, _y, _o in pin_points):
            out.warnings.append(
                f"duplicate instance name {comp.name!r} — terminal bindings key on the "
                "name, the later definition wins; rename one instance"
            )
        t = Transform(x=int(comp.x), y=int(comp.y), rot=comp.rot, flip=comp.flip)
        for p in sym.pins:
            ax, ay = apply_transform(t, p.x, p.y)
            pin_points.append((comp.name, p.name, float(ax), float(ay), (comp.x, comp.y)))
            uf.add(_key(ax, ay))

    for w in sch.wires:
        if w.lab:
            label_points.append((w.lab, w.x1, w.y1))

    # T-junctions & pins-on-wires: union every known node with any segment it lies on.
    nodes = [(k, k[0] / 2.0, k[1] / 2.0) for k in uf.keys()]
    for x1, y1, x2, y2 in segments:
        k1 = _key(x1, y1)
        for k, px, py in nodes:
            if k != k1 and _on_segment(px, py, x1, y1, x2, y2):
                uf.union(k1, k)

    # Name the groups: labels/ports first, then union groups sharing a name (xschem's
    # by-name merge). A group with two different names is a drawn short — warn, keep the
    # lexicographically smallest so the output stays deterministic.
    names_by_root: dict[tuple[int, int], set[str]] = {}
    root_by_name: dict[str, tuple[int, int]] = {}
    for lab, x, y in label_points:
        root = uf.find(_key(x, y))
        if lab in root_by_name:
            uf.union(root_by_name[lab], root)
            root = uf.find(root)
        root_by_name[lab] = root
        names_by_root.setdefault(root, set()).add(lab)
    # Re-root the name table after the by-name merges.
    merged: dict[tuple[int, int], set[str]] = {}
    for root, names in names_by_root.items():
        merged.setdefault(uf.find(root), set()).update(names)

    def net_name(root: tuple[int, int]) -> str:
        names = sorted(merged.get(root, ()))
        if not names:
            return f"net_{root[0]}_{root[1]}".replace("-", "m")
        # xschem auto-labels ('#net2') lose to human names: xschem's own netlister
        # publishes the human label (subckt ports especially), and the built cellview's
        # net/port naming must agree with it or hierarchy netlists drift.
        human = [n for n in names if not n.startswith("#")]
        pick = (human or names)[0]
        if len(names) > 1:
            msg = f"net carries multiple labels {names} — using {pick!r}"
            if msg not in out.warnings:
                out.warnings.append(msg)
        return pick

    def touches_wire(px: float, py: float) -> bool:
        return any(_on_segment(px, py, *seg) for seg in segments)

    for inst, pin, ax, ay, origin in pin_points:
        root = uf.find(_key(ax, ay))
        net = net_name(root)
        out.nets.add(net)
        out.pin_nets[(inst, pin)] = PinNet(
            inst=inst,
            pin=pin,
            net=net,
            x=ax,
            y=ay,
            stub_dir=_stub_direction(ax, ay, segments, origin),
            on_wire=touches_wire(ax, ay),
        )
    for port in out.ports:
        out.nets.add(port.name)

    # Wire segments per net, split at every electrical node lying on them so a drawn
    # T-junction becomes two endpoint-touching wires (which Virtuoso does connect).
    node_pts = [(k[0] / 2.0, k[1] / 2.0) for k in uf.keys()]
    for seg in segments:
        x1, y1, x2, y2 = seg
        net = net_name(uf.find(_key(x1, y1)))
        out.nets.add(net)
        interior = [(px, py) for px, py in node_pts if _on_segment(px, py, x1, y1, x2, y2)]
        interior.sort(key=lambda p: (p[0] - x1) ** 2 + (p[1] - y1) ** 2)
        pieces = out.net_segments.setdefault(net, [])
        prev = (x1, y1)
        for px, py in interior:
            if (px, py) != prev:
                pieces.append((prev[0], prev[1], px, py))
                prev = (px, py)
        if prev != (x2, y2):
            pieces.append((prev[0], prev[1], x2, y2))
    return out
