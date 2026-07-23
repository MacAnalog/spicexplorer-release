"""Overlay block boxes on an existing hand-drawn .sch — moving nothing, joining by instance name."""

from __future__ import annotations

from pathlib import Path

from spicexplorer_netlist2xschem import (
    BlockAnnotation,
    BlockAnnotationSet,
    annotate_sch,
    build_sch,
    from_file,
    parse_sch,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _existing_sch(sym_lib) -> tuple[str, list[str]]:
    """A schematic standing in for a user's hand-drawn one (generated, but treated as opaque)."""
    circuit = from_file(FIXTURES / "ota-improved.spice")
    doc = build_sch(circuit, lib=sym_lib)  # no annotations — a plain layout
    drawn = [c.name for c in parse_sch(doc.text).devices]
    return doc.text, drawn


def test_overlay_adds_boxes_without_moving_devices(sym_lib):
    sch_text, drawn = _existing_sch(sym_lib)
    before = parse_sch(sch_text)
    # Two blocks over real devices (use the drawn names, then also check the X-normalised join below).
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("b1", (drawn[0], drawn[1]), label="pair", family="differential_pair"),
            BlockAnnotation("b2", (drawn[2], drawn[3]), label="mirror", family="current_mirror"),
        )
    )
    annotated, warnings = annotate_sch(sch_text, aset)
    assert not warnings
    after = parse_sch(annotated)

    # Overlay-only: every device keeps its exact symbol + coordinate; only B/T graphics were added.
    assert {(c.name, c.x, c.y, c.rot, c.flip) for c in after.devices} == {
        (c.name, c.x, c.y, c.rot, c.flip) for c in before.devices
    }
    assert len(after.boxes) == 2  # one box per block
    assert sum(1 for t in after.texts if t.text in ("pair", "mirror")) == 2


def test_join_tolerates_the_x_spiceprefix_split(sym_lib):
    """Blocks carry netlist refs (XM…); the .sch draws M… — the overlay still finds them."""
    sch_text, drawn = _existing_sch(sym_lib)
    # All drawn devices are M… (X stripped by the spiceprefix); build the block with the X-prefixed refs.
    x_refs = tuple(f"X{n}" for n in drawn[:2])
    aset = BlockAnnotationSet((BlockAnnotation("b", x_refs, label="blk"),))
    annotated, warnings = annotate_sch(sch_text, aset)
    assert not warnings, "X-prefixed refs should still match the drawn M… devices"
    assert len(parse_sch(annotated).boxes) == 1


def test_missing_devices_are_skipped_with_a_warning(sym_lib):
    sch_text, _ = _existing_sch(sym_lib)
    aset = BlockAnnotationSet((BlockAnnotation("ghost", ("XNOPE1", "XNOPE2")),))
    annotated, warnings = annotate_sch(sch_text, aset)
    assert annotated == sch_text  # nothing drawn
    assert warnings and "ghost" in warnings[0]
