"""Functional-block annotation overlay for the xschem schematic.

Draw a labelled, coloured **bounding box** around each *recognised functional sub-circuit* (a current
mirror, a differential pair, …) that an upstream detector found in the netlist. It is a purely
diagnostic overlay — proof that the structural-detection pipeline fired, and a debugging aid for
reading larger circuits — emitted as xschem graphic rectangles (``B``) and text (``T``). It moves no
device and touches no wire, so the schematic's connectivity round-trip is unchanged (``B``/``T`` are
non-electrical).

The input is a *neutral contract*, :class:`BlockAnnotationSet`, loadable from the
``spicexplorer/xschem-block-annotations@1`` JSON a detector emits (e.g. circuitgraph's
``export_subcircuit_annotations``). This package never imports the detector; the JSON schema is the
only coupling, so any producer that emits the schema can drive the overlay. A block is joined to the
placed schematic purely by **device instance name** (``devices``) — the same refs the netlist uses.

Schema (``spicexplorer/xschem-block-annotations@1``)::

    {
      "schema": "spicexplorer/xschem-block-annotations@1",
      "blocks": [
        {
          "block_id": "cm.nmos.simple#1",   # stable, unique within the set
          "devices":  ["XM5", "XM6"],        # host instance refs — the join key (required)
          "label":    "current mirror (nmos simple)",  # optional display text
          "family":   "current_mirror",      # optional — groups/colours the box
          "parent_id": null,                  # optional — nest this box inside another block
          "alternates": [],                   # optional — other template ids on the same devices
          "template_id": "cm.nmos.simple",   # optional metadata (carried, not required to render)
          "role": "simple",                   # optional metadata
          "polarity": "nmos"                  # optional metadata
        }
      ]
    }

Nesting: when ``parent_id`` points at another block the child is drawn as a *smaller, dashed* box
inside the parent's (e.g. the simple sub-mirror subsumed inside a cascode). ``alternates`` are folded
into the label rather than drawn as their own box (they cover the *same* devices).

Three further **optional** keys (additive, schema still ``@1``) drive the block-driven renderers and are
ignored by the box overlay: ``template_sch`` (the block's hand-drawn symmetric layout, for strategy-2
stamping), ``device_slots`` (host ref → template device-slot), and ``port_names`` (boundary host net →
the template's functional port name — ``out`` / ``ref_in`` / ``supply`` / …, a fanned-out mirror's extra
outputs numbered ``out_2``, ``out_3``, …, used to label a generated block symbol's pins). A producer that
omits them, or a consumer that ignores them, is unaffected.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .wiring import Box, PlacedDevice, device_extent

__all__ = [
    "ANNOTATION_SCHEMA",
    "BlockAnnotation",
    "BlockAnnotationSet",
    "annotation_lines",
]

ANNOTATION_SCHEMA = "spicexplorer/xschem-block-annotations@1"

# --- box geometry -----------------------------------------------------------------------------
_PAD = 40  # padding from the device-extent union to a top-level block's box edge
_PAD_STEP = 22  # each nesting level draws this much tighter, so a child box sits *inside* its parent
_PAD_MIN = 8  # floor on the padding however deep the nesting goes
_LABEL_DY = 18  # the block label sits this far above the box's top edge
_LABEL_SIZE = 0.3  # label text size (the schematic title uses 0.4; block labels read a touch smaller)
_LABEL_LINE = 24  # min vertical gap between two labels before one is bumped up (anti-collision)
_LABEL_BUCKET = 60  # x-tolerance within which two labels are considered to share a column

# --- colour --------------------------------------------------------------------------------------
# xschem graphic *layers* used to colour the boxes — a curated, visually-distinct cycle tuned against
# the headless render (see notebooks/annotation_demo.ipynb). Deliberately avoids the layers that read
# as the schematic itself: green (4/11, device bodies), red (5/7, pins), cyan (1/6/17, wires & net
# labels) and white/grey (2/3/9/14/16/19, text/background). What remains is yellow, magenta, blue,
# orange, salmon, olive, pink, coral — distinct from each other and from everything already drawn.
_BOX_LAYERS = (8, 10, 12, 21, 15, 13, 18, 20)
_DASH_NESTED = 4  # dashed outline for a nested box (solid for a top-level one)


@dataclass(frozen=True)
class BlockAnnotation:
    """One recognised functional block to outline on the schematic.

    ``block_id`` is a stable identifier unique within the set; ``devices`` are the host instance refs
    that make up the block — the join key against the placed schematic (the only required pair). Every
    other field is optional and affects only how the box is labelled / coloured / nested:
    ``parent_id`` draws this block *inside* another (an inner dashed box); ``alternates`` are other
    template ids that matched the *same* devices and are shown in the label; ``family`` / ``template_id``
    / ``role`` / ``polarity`` are carried metadata.
    """

    block_id: str
    devices: tuple[str, ...]
    label: str = ""
    family: str = ""
    parent_id: str | None = None
    alternates: tuple[str, ...] = ()
    template_id: str = ""
    role: str = ""
    polarity: str = ""
    # Schematic-stamping hints (additive, schema still ``@1``): the block's hand-drawn symmetric layout
    # (``template_sch``, a path relative to the workspace root) and each host device → the template
    # device-slot it fills (``device_slots``, stored as sorted pairs to keep this frozen value
    # hashable). Both are empty for a producer/contract that doesn't carry them; the box overlay never
    # needs them, so older consumers are unaffected. See :meth:`slots`.
    template_sch: str = ""
    device_slots: tuple[tuple[str, str], ...] = ()
    # Each boundary host net → the template's **functional port name** (``out`` / ``ref_in`` / ``supply``
    # / ``in_p`` / …), a fanned-out mirror's extra outputs numbered ``out_2``, ``out_3``, …. Lets the
    # hierarchy renderer name a generated block symbol's pins by what they *are* rather than by the host
    # net on them. Stored as sorted pairs to keep this frozen value hashable; empty when the producer
    # doesn't carry it. See :meth:`port_names`.
    port_name_map: tuple[tuple[str, str], ...] = ()

    def slots(self) -> dict[str, str]:
        """``device_slots`` as a ``{host_ref: template_device}`` dict (the stamping join)."""
        return dict(self.device_slots)

    def port_names(self) -> dict[str, str]:
        """``port_name_map`` as a ``{host_net: functional_port_name}`` dict (the pin-labelling join)."""
        return dict(self.port_name_map)

    @classmethod
    def from_dict(cls, d: Mapping[str, object]) -> BlockAnnotation:
        """Build from one block entry of the JSON contract (tolerant of missing optional keys)."""
        raw_slots = d.get("device_slots", {})
        slots = raw_slots.items() if isinstance(raw_slots, Mapping) else ()
        raw_ports = d.get("port_names", {})
        ports = raw_ports.items() if isinstance(raw_ports, Mapping) else ()
        return cls(
            block_id=str(d["block_id"]),
            devices=tuple(str(r) for r in d.get("devices", ())),  # type: ignore[arg-type]
            label=str(d.get("label", "")),
            family=str(d.get("family", "")),
            parent_id=(str(d["parent_id"]) if d.get("parent_id") is not None else None),
            alternates=tuple(str(a) for a in d.get("alternates", ())),  # type: ignore[arg-type]
            template_id=str(d.get("template_id", "")),
            role=str(d.get("role", "")),
            polarity=str(d.get("polarity", "")),
            template_sch=str(d.get("template_sch", "")),
            device_slots=tuple(sorted((str(k), str(v)) for k, v in slots)),
            port_name_map=tuple(sorted((str(k), str(v)) for k, v in ports)),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialise to one block entry of the JSON contract."""
        return {
            "block_id": self.block_id,
            "devices": list(self.devices),
            "label": self.label,
            "family": self.family,
            "parent_id": self.parent_id,
            "alternates": list(self.alternates),
            "template_id": self.template_id,
            "role": self.role,
            "polarity": self.polarity,
            "template_sch": self.template_sch,
            "device_slots": self.slots(),
            "port_names": self.port_names(),
        }

    def display_label(self) -> str:
        """The text drawn at the box corner: the label (or a sensible fallback) + any alternates.

        Falls back through ``label → family → template_id → block_id`` so a box is always named. Curly
        braces are neutralised because they would terminate the xschem ``T {…}`` record."""
        base = self.label or self.family or self.template_id or self.block_id
        if self.alternates:
            base = f"{base} [alt: {', '.join(self.alternates)}]"
        return base.replace("{", "(").replace("}", ")")


@dataclass(frozen=True)
class BlockAnnotationSet:
    """A set of :class:`BlockAnnotation` — the whole overlay for one schematic.

    Loadable from the ``spicexplorer/xschem-block-annotations@1`` JSON (file, text, or dict) and
    serialisable back to it. Iterable over its blocks."""

    blocks: tuple[BlockAnnotation, ...] = ()

    # --- construction ----------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Mapping[str, object] | Sequence[object]) -> BlockAnnotationSet:
        """Build from the parsed JSON: ``{"schema":…, "blocks":[…]}`` or a bare list of block dicts."""
        entries = data.get("blocks", ()) if isinstance(data, Mapping) else data
        return cls(tuple(BlockAnnotation.from_dict(e) for e in entries))  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, text: str) -> BlockAnnotationSet:
        """Build from a JSON *string*."""
        return cls.from_dict(json.loads(text))

    @classmethod
    def load(cls, path: str | Path) -> BlockAnnotationSet:
        """Build from a JSON *file*."""
        return cls.from_json(Path(path).read_text())

    # --- serialisation ---------------------------------------------------------------------------
    def to_dict(self) -> dict[str, object]:
        return {"schema": ANNOTATION_SCHEMA, "blocks": [b.to_dict() for b in self.blocks]}

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.write_text(self.to_json() + "\n")
        return p

    # --- access ----------------------------------------------------------------------------------
    def __iter__(self):
        return iter(self.blocks)

    def __len__(self) -> int:
        return len(self.blocks)

    def __bool__(self) -> bool:
        return bool(self.blocks)

    # --- placement hint ---------------------------------------------------------------------------
    def placement_clusters(self) -> tuple[tuple[str, ...], ...]:
        """Device-ref groups for **block-aware placement** — one coherent cluster per functional block.

        Two blocks are merged into one cluster when they **nest** (``parent_id``) or **share a device**
        (a cascode mirror and its subsumed simple mirror), so the whole functional block — reference,
        cascode devices and outputs — is kept spatially together rather than split. Unrelated blocks
        (a differential pair vs its load mirror) stay separate clusters. The result feeds
        :class:`~spicexplorer_netlist2xschem.placement.PlacementHints` and is purely a *layout*
        suggestion (connectivity is untouched). Deterministic: each cluster's refs are sorted and the
        clusters are ordered by their contents."""
        blocks = list(self.blocks)
        if not blocks:
            return ()
        parent = list(range(len(blocks)))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i: int, j: int) -> None:
            parent[find(i)] = find(j)

        by_id = {b.block_id: i for i, b in enumerate(blocks)}
        for i, b in enumerate(blocks):  # nesting: child merges into parent
            if b.parent_id is not None and b.parent_id in by_id:
                union(i, by_id[b.parent_id])
        first_seen: dict[str, int] = {}  # shared device: two blocks naming one ref are the same block
        for i, b in enumerate(blocks):
            for ref in b.devices:
                if ref in first_seen:
                    union(i, first_seen[ref])
                else:
                    first_seen[ref] = i

        comp_refs: dict[int, set[str]] = {}
        for i, b in enumerate(blocks):
            comp_refs.setdefault(find(i), set()).update(b.devices)
        clusters = sorted(tuple(sorted(refs)) for refs in comp_refs.values() if refs)
        return tuple(clusters)


def _union(boxes: Iterable[Box]) -> Box:
    bs = list(boxes)
    return (
        min(b[0] for b in bs),
        min(b[1] for b in bs),
        max(b[2] for b in bs),
        max(b[3] for b in bs),
    )


def _depths(blocks: Sequence[BlockAnnotation]) -> dict[str, int]:
    """Each block's nesting depth (0 = top-level), following ``parent_id`` and guarding against a
    missing parent or an accidental cycle (an unresolved/looping parent just makes the block top-level)."""
    by_id = {b.block_id: b for b in blocks}
    cache: dict[str, int] = {}

    def depth(bid: str, seen: frozenset[str]) -> int:
        if bid in cache:
            return cache[bid]
        b = by_id.get(bid)
        if b is None or b.parent_id is None or b.parent_id == bid or b.parent_id in seen:
            cache[bid] = 0
            return 0
        d = 1 + depth(b.parent_id, seen | {bid})
        cache[bid] = d
        return d

    return {b.block_id: depth(b.block_id, frozenset()) for b in blocks}


def annotation_lines(
    annotations: BlockAnnotationSet,
    placed: Sequence[PlacedDevice],
) -> tuple[list[str], list[str]]:
    """The xschem ``B``/``T`` lines for every block's labelled box, plus warnings.

    Pure: given the placed devices and the block contract it returns ready-to-append ``.sch`` lines.
    Each block is boxed around the union of its placed devices' extents (body + parameter text), padded
    so the outline clears the devices; deeper-nested blocks are padded less so a child box sits inside
    its parent's and is drawn *dashed*. Boxes are coloured by cycling :data:`_BOX_LAYERS` in a stable
    order (parents before children), so adjacent blocks are visually distinct.

    The overlay is diagnostic, so it is lenient about the join: a block whose devices were *all* skipped
    during placement is dropped with a warning; a block missing only *some* is boxed around the rest.
    """
    by_ref = {pd.ref: pd for pd in placed}
    blocks = list(annotations.blocks)
    depths = _depths(blocks)
    # Parents before children (stable within a depth) so a smaller, dashed child box draws on top and
    # gets a later — distinct — colour from its parent.
    order = sorted(range(len(blocks)), key=lambda i: (depths[blocks[i].block_id], i))

    lines: list[str] = []
    warnings: list[str] = []
    label_ys: dict[int, list[int]] = {}  # x-bucket -> taken label y's, to stagger coincident labels
    for color_idx, i in enumerate(order):
        b = blocks[i]
        members = [by_ref[r] for r in b.devices if r in by_ref]
        missing = [r for r in b.devices if r not in by_ref]
        if not members:
            warnings.append(
                f"annotation block {b.block_id!r}: none of its devices {list(b.devices)} "
                "were placed; box skipped"
            )
            continue
        if missing:
            warnings.append(
                f"annotation block {b.block_id!r}: devices {missing} not placed; "
                "boxing the placed members only"
            )
        pad = max(_PAD_MIN, _PAD - depths[b.block_id] * _PAD_STEP)
        x0, y0, x1, y1 = _union(device_extent(pd) for pd in members)
        x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
        layer = _BOX_LAYERS[color_idx % len(_BOX_LAYERS)]
        props = "fill=0" if b.parent_id is None else f"fill=0 dash={_DASH_NESTED}"
        lines.append(f"B {layer} {x0} {y0} {x1} {y1} {{{props}}}")
        # Anchor the label above the box's top-left, bumping it up past any label already placed in the
        # same column so two boxes that still share a corner don't stack their text on one spot
        # (block-aware placement reduces, but can't always eliminate, shared corners — stacked blocks
        # in one current path overlap by construction).
        ly = _free_label_y(label_ys, x0, y0 - _LABEL_DY)
        lines.append(
            f"T {{{b.display_label()}}} {x0} {ly} 0 0 {_LABEL_SIZE} {_LABEL_SIZE} {{layer={layer}}}"
        )
    return lines, warnings


def _free_label_y(taken: dict[int, list[int]], x: int, y: int) -> int:
    """A label-y near ``y`` not within :data:`_LABEL_LINE` of one already used in ``x``'s column.

    Mutates ``taken`` to record the chosen y. Bumps *upward* (decreasing y) so stacked labels read top
    to bottom in placement order."""
    bucket = round(x / _LABEL_BUCKET)
    used = taken.setdefault(bucket, [])
    while any(abs(y - t) < _LABEL_LINE for t in used):
        y -= _LABEL_LINE
    used.append(y)
    return y
