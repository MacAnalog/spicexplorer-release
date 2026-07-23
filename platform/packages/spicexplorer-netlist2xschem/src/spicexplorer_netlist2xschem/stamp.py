"""Strategy 2 — stamp a hand-drawn block template's *symmetric* layout onto the host devices.

The block-aware placer only nudges a detected block's devices *adjacent*; the internal geometry
is still the algorithm's, so a differential pair's two halves are rarely mirror-symmetric. This module
instead reuses the **hand-drawn** layout shipped with each template (``examples/analog-db/templates/…``,
a symmetric schematic an engineer drew once) as the block's internal geometry — so the diff pair's two
devices land at mirrored flips, a cascode stacks straight, etc.

The trick that keeps it correct: we take *only the geometry* from the template (each device's
``(x, y, rot, flip)``), never its wiring. The host devices are then placed at those coordinates and the
**existing** connectivity-safe wiring engine wires them by net — so a stamped schematic re-netlists to
the same circuit as any other (connectivity-neutral, exactly like block-aware placement). :class:`TemplateStampPlacer` is a
drop-in :class:`~.placement.Placer`: it lets a proven base placer (``PhasedPlacer``) decide *where each
block goes* (the macro arrangement), then **rigidifies** each block's interior to its template.

Inputs travel through the ``spicexplorer/xschem-block-annotations@1`` contract: each block carries a
``template_sch`` (the layout's path, relative to the workspace root) and ``device_slots`` mapping every
host device to the template device-slot it fills (the producer computed both — see
:func:`spicexplorer_circuitgraph.export_subcircuit_annotations`). This module never imports the detector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .annotation import BlockAnnotationSet
from .geometry import Transform, snap
from .placement import PhasedPlacer, PlacementHints, Placer, place_with_hints
from .sch_parser import parse_sch
from .sym_library import SymLibrary

__all__ = [
    "BlockStamp",
    "TemplateStampPlacer",
    "resolve_template_sch",
    "build_block_stamps",
]

# Rough horizontal room a device's symbol + parameter text needs beyond its origin, used to size a
# block's footprint and the gap between blocks so stamped blocks don't visually collide.
_DEVICE_PAD = 140
_BLOCK_GAP = 120  # blank columns kept between two adjacent block/leftover units in the row


def resolve_template_sch(template_sch: str, root: Path | None = None) -> Path | None:
    """Resolve a contract ``template_sch`` (a workspace-root-relative path) to a real file, or ``None``.

    Tries, in order: the path as given (absolute or cwd-relative); ``root / template_sch`` when an
    explicit template root is supplied (tests point this at a fixture tree); and
    ``project_root() / template_sch`` (the shipped analog-db templates). Returns the first that exists.
    """
    if not template_sch:
        return None
    candidates: list[Path] = []
    p = Path(template_sch)
    candidates.append(p)
    if root is not None:
        candidates.append(root / template_sch)
    try:
        from spicexplorer_core import project_root

        candidates.append(project_root() / template_sch)
    except Exception:  # pragma: no cover - root marker absent
        pass
    return next((c for c in candidates if c.is_file()), None)


def _slot_transforms(text: str) -> dict[str, Transform]:
    """Each template device's symbol-local placement, keyed by its ``X``-normalised instance name.

    The template ``.sch`` draws ``XM1`` as ``name=M1`` (xschem strips the ``spiceprefix=X``); the
    contract's ``device_slots`` name the slot in netlist space (``XM1``). Normalising a leading ``X``
    on both sides lets them join."""
    out: dict[str, Transform] = {}
    for c in parse_sch(text).devices:
        name = c.name
        norm = name[1:] if name[:1] in "Xx" else name
        if norm:
            out[norm] = Transform(int(round(c.x)), int(round(c.y)), c.rot, c.flip)
    return out


def _norm(ref: str) -> str:
    return ref[1:] if ref[:1] in "Xx" else ref


@dataclass(frozen=True)
class BlockStamp:
    """One block's host devices laid out at its template's symmetric geometry.

    ``local`` maps each host device ref → its placement relative to the block's own origin (the block's
    bounding box is normalised so its left edge is at ``x = 0`` and it is vertically centred on
    ``y = 0``). ``width`` is the horizontal room the block needs. The transforms carry the template's
    ``rot``/``flip`` verbatim — that is what makes a differential pair's halves mirror-symmetric."""

    block_id: str
    local: dict[str, Transform]
    width: int

    @property
    def devices(self) -> tuple[str, ...]:
        return tuple(self.local)


def _build_one_stamp(
    block_id: str,
    devices: tuple[str, ...],
    device_slots: dict[str, str],
    template_sch: str,
    *,
    present: set[str],
    root: Path | None,
) -> BlockStamp | None:
    """Build a :class:`BlockStamp` for one block, or ``None`` if it can't be stamped.

    Needs the template ``.sch`` to resolve and at least one host device to have a known slot whose
    geometry the template provides. A multi-output mirror (several host devices sharing one template
    output slot) fans the extras out into successive columns so they don't stack on one spot.
    """
    path = resolve_template_sch(template_sch, root)
    if path is None:
        return None
    slots = _slot_transforms(path.read_text(encoding="utf-8", errors="replace"))
    if not slots:
        return None

    # Resolve each present host device to its template slot transform. A slot filled by more than one
    # host device (a multi-output mirror; or a degenerate group that over-merged several instances of a
    # template) would stack them on one spot — and two coincident devices merge their pins, silently
    # shorting nets. So we place into the first FREE cell, shifting right by a full device pitch until
    # clear: every host device gets a distinct origin ≥ pitch apart, so no two pins can ever coincide
    # (the connectivity invariant). The layout of such an over-matched block isn't pretty, but it stays
    # electrically correct; clean 1:1 and simple multi-output blocks are unaffected.
    pitch = max(_slot_pitch(slots), 160)
    occupied: set[tuple[int, int]] = set()
    raw: dict[str, Transform] = {}
    for ref in sorted(devices):
        if ref not in present:
            continue
        slot = _norm(device_slots.get(ref, ""))
        t = slots.get(slot)
        if t is None:
            continue
        x, y = t.x, t.y
        while (x, y) in occupied:
            x += pitch
        occupied.add((x, y))
        raw[ref] = Transform(x, y, t.rot, t.flip)
    if not raw:
        return None

    # Normalise: left edge to x=0, vertically centre on y=0 (so the block sits on its placed centre).
    min_x = min(t.x for t in raw.values())
    max_x = max(t.x for t in raw.values())
    mid_y = (min(t.y for t in raw.values()) + max(t.y for t in raw.values())) // 2
    local = {
        ref: Transform(t.x - min_x, t.y - mid_y, t.rot, t.flip) for ref, t in raw.items()
    }
    return BlockStamp(block_id=block_id, local=local, width=(max_x - min_x) + _DEVICE_PAD)


def _slot_pitch(slots: dict[str, Transform]) -> int:
    """A sensible horizontal pitch to fan duplicate slots by — the template's own device spread."""
    xs = sorted({t.x for t in slots.values()})
    if len(xs) >= 2:
        return max(xs[i + 1] - xs[i] for i in range(len(xs) - 1))
    return 240


def build_block_stamps(
    annotations: BlockAnnotationSet,
    present: set[str],
    *,
    root: Path | None = None,
) -> list[BlockStamp]:
    """Resolve every top-level annotated block to a :class:`BlockStamp` (skipping unstampable ones).

    Only **top-level** blocks (``parent_id is None``) are stamped — a nested sub-block (a simple mirror
    inside a cascode) is laid out by its parent's template, not separately. ``present`` is the set of
    device refs that actually got placed (so a block whose devices were all skipped is dropped). A block
    with no ``template_sch`` / ``device_slots`` (an older contract) simply yields no stamp and its
    devices fall back to the base placer.
    """
    stamps: list[BlockStamp] = []
    for b in annotations.blocks:
        if b.parent_id is not None:
            continue
        stamp = _build_one_stamp(
            b.block_id,
            b.devices,
            b.slots(),
            b.template_sch,
            present=present,
            root=root,
        )
        if stamp is not None:
            stamps.append(stamp)
    return stamps


def _mean(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0.0


@dataclass
class TemplateStampPlacer:
    """A :class:`~.placement.Placer` that rigidifies each detected block to its template's symmetric
    layout, arranging the blocks (and any leftover devices) left-to-right in the base placer's order.

    Construct it with the :class:`BlockStamp`\\ s for a schematic (``build_block_stamps`` from the
    annotation contract). ``base`` (default :class:`~.placement.PhasedPlacer`) decides the *macro*
    order: we run it once, read each block's centroid to order the row, then lay every block at its
    template geometry. Leftover devices (in no block) keep their relative order as single-column units.
    Output is a plain ``ref -> Transform`` dict, so wiring/emit are untouched and connectivity-neutral.
    """

    stamps: tuple[BlockStamp, ...] = ()
    base: Placer = field(default_factory=PhasedPlacer)
    gap: int = _BLOCK_GAP

    def place(
        self,
        circuit,
        lib: SymLibrary | None = None,
        *,
        hints: PlacementHints | None = None,
    ) -> dict[str, Transform]:
        # Run the base placer with block-cohesion hints so each block's baseline centroid is coherent
        # (its devices already clustered) — we only read the centroids to order the row.
        cluster_hints = PlacementHints(clusters=tuple(s.devices for s in self.stamps))
        baseline = place_with_hints(self.base, circuit, lib, cluster_hints or hints)
        if not self.stamps:
            return baseline

        block_of = {ref: i for i, s in enumerate(self.stamps) for ref in s.devices}

        # Assemble the row units: one per stampable block, plus one per leftover device.
        units: list[_Unit] = []
        for s in self.stamps:
            members = [r for r in s.devices if r in baseline]
            if not members:
                continue
            cx = _mean([baseline[r].x for r in members])
            cy = _mean([baseline[r].y for r in members])
            units.append(_Unit(center=(cx, cy), local=s.local, width=s.width, key=min(members)))
        for ref, t in baseline.items():
            if ref not in block_of:
                units.append(
                    _Unit(center=(t.x, t.y), local={ref: Transform(0, 0, t.rot, t.flip)},
                          width=_DEVICE_PAD, key=ref)
                )

        # Order left-to-right by the base placer's x (then y, then ref for determinism) and pack into a
        # row: each unit owns its own x-band, so blocks never overlap whatever their template's size.
        units.sort(key=lambda u: (u.center[0], u.center[1], u.key))
        out: dict[str, Transform] = {}
        occupied: set[tuple[int, int]] = set()
        cursor = 0
        for u in units:
            oy = int(round(u.center[1]))
            for ref, lt in sorted(u.local.items()):
                x, y = snap(cursor + lt.x), snap(oy + lt.y)
                # Final safety net: never let two devices share an origin (would merge their pins).
                while (x, y) in occupied:
                    x += self.gap
                occupied.add((x, y))
                out[ref] = Transform(x, y, lt.rot, lt.flip)
            cursor += u.width + self.gap
        return out


@dataclass
class _Unit:
    """One row element — a stamped block or a single leftover device."""

    center: tuple[float, float]
    local: dict[str, Transform]
    width: int
    key: str
