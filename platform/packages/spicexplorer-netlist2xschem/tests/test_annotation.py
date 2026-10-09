"""Functional-block annotation overlay — the contract, the box geometry, and the emit integration.

These tests exercise the *consumer* half (this package) with hand-authored
:class:`BlockAnnotationSet`s — no detector import. They assert the overlay is additive (connectivity
is byte-for-byte unchanged), that a box encloses its devices, that a nested block is drawn inside its
parent, that sibling blocks get distinct colours, and that the JSON contract round-trips.
"""

import re
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    ANNOTATION_SCHEMA,
    BlockAnnotation,
    BlockAnnotationSet,
    build_sch,
    from_string,
)

# A tiny self-contained 4-device netlist (a cascode-ish NMOS stack) — enough to place + box.
NETLIST = """\
* annotation test netlist
XM1 net2 net1 0 0 nmos w=1u l=0.15u
XM2 net1 net1 0 0 nmos w=1u l=0.15u
XM3 iout iin net1 0 nmos w=1u l=0.15u
XM4 iin  iin net2 0 nmos w=1u l=0.15u
.end
"""

# `B <layer> x0 y0 x1 y1 {props}`
_BOX = re.compile(r"^B (\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) \{(.*)\}$")
# `T {label} x y rot flip hs vs {props}`
_TEXT = re.compile(r"^T \{(.*)\} (-?\d+) (-?\d+) \d \d \S+ \S+ \{(.*)\}$")


def _boxes(sch_text: str):
    """Parsed (layer, x0, y0, x1, y1, props) for every `B` rectangle, in file order."""
    out = []
    for line in sch_text.splitlines():
        m = _BOX.match(line)
        if m:
            out.append((int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), m[6]))
    return out


def _texts(sch_text: str):
    """Parsed (label, x, y, props) for every `T` text record."""
    out = []
    for line in sch_text.splitlines():
        m = _TEXT.match(line)
        if m:
            out.append((m[1], int(m[2]), int(m[3]), m[4]))
    return out


def _circuit():
    return from_string(NETLIST, name="anno")


# --------------------------------------------------------------------------------------------------
# The contract
# --------------------------------------------------------------------------------------------------
def test_json_round_trip():
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("g1", ("XM1", "XM2"), label="mirror", family="current_mirror"),
            BlockAnnotation("g1/s", ("XM1",), family="current_mirror", parent_id="g1"),
        )
    )
    assert BlockAnnotationSet.from_json(aset.to_json()) == aset
    assert BlockAnnotationSet.from_dict(aset.to_dict()) == aset
    assert aset.to_dict()["schema"] == ANNOTATION_SCHEMA


def test_save_and_load_round_trip(tmp_path):
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2")),))
    p = aset.save(tmp_path / "blocks.json")
    assert BlockAnnotationSet.load(p) == aset


# --------------------------------------------------------------------------------------------------
# P8 -- fail closed on an unresolvable member (a rename/removal upstream silently emptying a block)
# --------------------------------------------------------------------------------------------------
def test_load_without_circuit_still_fails_open_by_default():
    """Unchanged default: no ``circuit`` given, an unresolvable member is trusted as-is (existing
    callers that never pass ``circuit`` see no behaviour change)."""
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "DOES_NOT_EXIST")),))
    assert aset.blocks[0].devices == ("XM1", "DOES_NOT_EXIST")


def test_validate_raises_on_unresolvable_member():
    """A block member that does not exist in the circuit must raise, naming the block and the
    device -- the recertification scenario: renaming ``XM1`` -> ``XM1_1`` silently emptied a block
    everywhere else in this module, and a downstream topology gate (component/net counts) still
    passed on the collapsed drawing."""
    circuit = _circuit()  # devices XM1..XM4
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM99")),))
    with pytest.raises(ValueError, match="g1"):
        aset.validate(circuit)
    with pytest.raises(ValueError, match="XM99"):
        aset.validate(circuit)


def test_validate_passes_when_every_member_resolves():
    circuit = _circuit()
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2")),))
    aset.validate(circuit)  # no raise


def test_load_with_circuit_validates(tmp_path):
    circuit = _circuit()
    good = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2")),))
    p_good = good.save(tmp_path / "good.json")
    assert BlockAnnotationSet.load(p_good, circuit=circuit) == good

    bad = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "RENAMED_AWAY")),))
    p_bad = bad.save(tmp_path / "bad.json")
    with pytest.raises(ValueError, match="RENAMED_AWAY"):
        BlockAnnotationSet.load(p_bad, circuit=circuit)


def test_from_dict_tolerates_minimal_block():
    aset = BlockAnnotationSet.from_dict({"blocks": [{"block_id": "g", "devices": ["XM1"]}]})
    (b,) = aset.blocks
    assert b.block_id == "g" and b.devices == ("XM1",)
    assert b.parent_id is None and b.alternates == () and b.label == ""


def test_from_dict_accepts_bare_list():
    aset = BlockAnnotationSet.from_dict([{"block_id": "g", "devices": ["XM1"]}])
    assert len(aset) == 1


def test_from_dict_tolerates_dr3_producer_keys():
    # The producer (circuitgraph) additionally emits `rules_ref` (design-rule doc pointers) and
    # `roles` (per-device deterministic roles) per block — additive, schema still @1. This consumer
    # doesn't use them; the loader must simply pass over the unknown keys.
    aset = BlockAnnotationSet.from_dict(
        {
            "schema": ANNOTATION_SCHEMA,
            "blocks": [
                {
                    "block_id": "g",
                    "devices": ["XM1", "XM2"],
                    "rules_ref": [
                        "examples/analog-db/templates/current_mirror/rules/current_mirror.md"
                    ],
                    "roles": {"XM1": "current_mirror_reference", "XM2": "current_mirror"},
                }
            ],
        }
    )
    (b,) = aset.blocks
    assert b.block_id == "g" and b.devices == ("XM1", "XM2")


def test_from_dict_rejects_a_mapping_without_blocks():
    # analog-db's `<id>.structural.json` carries the @1 schema string but keeps its detections under
    # `groups`. It used to load as ZERO blocks with no warning: an empty overlay, and no blocks for
    # `--hierarchical` to lift into subcircuits, both the same as "the detector found nothing".
    structural = {
        "schema": ANNOTATION_SCHEMA,
        "circuit": "amp",
        "summary": {"device_count": 2, "blocks_detected": 1},
        "groups": [{"group_id": "cm.nmos.simple#1", "devices": ["XM1", "XM2"]}],
    }
    with pytest.raises(ValueError, match=r"no 'blocks'.*'groups'"):
        BlockAnnotationSet.from_dict(structural)
    with pytest.raises(ValueError, match="no 'blocks'"):
        BlockAnnotationSet.from_dict({})


@pytest.mark.parametrize(
    "schema",
    [
        "spicexplorer/xschem-block-annotations@2",
        "spicexplorer/xschem-block-annotations@2.0",
        "spicexplorer/xschem-block-annotations@one",
        "spicexplorer/some-other-contract@1",
        "",
        # the major is compared whole, not as a prefix: @10 is not @1
        "spicexplorer/xschem-block-annotations@10",
        "spicexplorer/xschem-block-annotations@",
        "spicexplorer/xschem-block-annotations",  # no version at all
        # a present-but-non-string schema is refused as well, never crashed on
        None,
        1,
    ],
)
def test_from_dict_rejects_a_schema_other_than_major_1(schema):
    # @2 is by definition a change a @1 consumer cannot read correctly (plan_block_annotation P8);
    # reading it as @1 would silently drop or misread whatever the new major changed.
    with pytest.raises(ValueError, match="unsupported annotation schema"):
        BlockAnnotationSet.from_dict(
            {"schema": schema, "blocks": [{"block_id": "g", "devices": ["XM1"]}]}
        )


def test_from_dict_accepts_an_additive_minor_of_major_1():
    # additive fields keep the major (the README's contract section); a producer that labels such a
    # revision `@1.<n>` is still readable by this consumer
    aset = BlockAnnotationSet.from_dict(
        {
            "schema": ANNOTATION_SCHEMA + ".3",
            "blocks": [{"block_id": "g", "devices": ["XM1"], "confidence": 0.9}],
        }
    )
    assert [b.block_id for b in aset] == ["g"]


def test_load_names_the_file_shape_problem(tmp_path):
    p = tmp_path / "amp.structural.json"
    p.write_text('{"schema": "%s", "groups": []}' % ANNOTATION_SCHEMA)
    with pytest.raises(ValueError, match="'groups'"):
        BlockAnnotationSet.load(p)


def test_from_dict_an_empty_blocks_list_is_zero_blocks_not_an_error():
    # circuitgraph exports exactly this for a circuit with no detections: the contract is the
    # `blocks` KEY, and an empty list under it is a real (empty) answer, unlike a missing key
    empty = {"schema": ANNOTATION_SCHEMA, "blocks": []}
    aset = BlockAnnotationSet.from_dict(empty)
    assert len(aset) == 0
    assert aset.to_dict() == empty
    assert BlockAnnotationSet.from_json(aset.to_json()) == aset


def test_from_dict_ignores_unknown_top_level_keys():
    # the additive policy applies to the envelope too: a producer may add top-level metadata
    aset = BlockAnnotationSet.from_dict(
        {
            "schema": ANNOTATION_SCHEMA,
            "producer": "circuitgraph 0.9",
            "circuit": "amp",
            "blocks": [{"block_id": "g", "devices": ["XM1"]}],
        }
    )
    assert [b.block_id for b in aset] == ["g"]


def test_from_dict_names_a_new_major_even_when_blocks_are_missing_too():
    # the version is the first thing wrong with such a payload: say that, not "no blocks"
    with pytest.raises(ValueError, match="unsupported annotation schema .*@2"):
        BlockAnnotationSet.from_dict(
            {"schema": "spicexplorer/xschem-block-annotations@2", "groups": []}
        )


def test_from_dict_no_blocks_message_lists_the_keys_that_were_there():
    with pytest.raises(ValueError, match=r"keys present: none\)"):
        BlockAnnotationSet.from_dict({})
    # sorted, quoted, and a non-string key (a dict built in Python, not parsed JSON) does not
    # turn the report into a TypeError
    odd: dict[object, object] = {"groups": [], 1: "x", "circuit": "amp"}
    with pytest.raises(ValueError, match=r"keys present: '1', 'circuit', 'groups'\)"):
        BlockAnnotationSet.from_dict(odd)  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    "text",
    [
        '{"schema": "spicexplorer/xschem-block-annotations@2", "blocks": []}',
        '{"schema": "spicexplorer/xschem-block-annotations@1", "groups": []}',
    ],
    ids=["new-major", "groups-shape"],
)
def test_from_json_applies_the_same_contract_check(text):
    with pytest.raises(ValueError):
        BlockAnnotationSet.from_json(text)


def test_display_label_falls_back_and_shows_alternates():
    assert BlockAnnotation("only-id", ()).display_label() == "only-id"
    assert BlockAnnotation("g", (), family="current_mirror").display_label() == "current_mirror"
    b = BlockAnnotation("g", (), label="cascode", alternates=("cm.nmos.improved_wilson",))
    assert b.display_label() == "cascode [alt: cm.nmos.improved_wilson]"


def test_display_label_neutralises_braces():
    # Braces would terminate the xschem `T {…}` record — they must not survive into the label.
    assert "{" not in BlockAnnotation("g", (), label="a{b}c").display_label()


# --------------------------------------------------------------------------------------------------
# Emission / geometry
# --------------------------------------------------------------------------------------------------
def test_no_annotations_is_a_no_op():
    doc = build_sch(_circuit())
    assert doc.annotation_count == 0
    assert not _boxes(doc.text)
    # An empty set is also a no-op.
    assert build_sch(_circuit(), annotations=BlockAnnotationSet()).annotation_count == 0


def test_emits_one_box_and_label_per_block():
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2"), label="mirror"),))
    doc = build_sch(_circuit(), annotations=aset)
    assert doc.annotation_count == 1
    assert len(_boxes(doc.text)) == 1
    labels = [t[0] for t in _texts(doc.text)]
    assert "mirror" in labels


def test_box_encloses_member_devices():
    circuit = _circuit()
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2")),))
    doc = build_sch(circuit, annotations=aset)
    # device origins from a plain build (placement is deterministic and annotation-independent)
    from spicexplorer_netlist2xschem import PhasedPlacer, SymLibrary

    placement = PhasedPlacer().place(circuit, SymLibrary.default())
    ((_, x0, y0, x1, y1, _),) = _boxes(doc.text)
    for ref in ("XM1", "XM2"):
        t = placement[ref]
        assert x0 <= t.x <= x1 and y0 <= t.y <= y1


def test_nested_box_sits_inside_parent_and_is_dashed():
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("g1", ("XM1", "XM2", "XM3", "XM4"), label="cascode"),
            BlockAnnotation("g1/s", ("XM1", "XM2"), label="simple", parent_id="g1"),
        )
    )
    boxes = _boxes(build_sch(_circuit(), annotations=aset).text)
    assert len(boxes) == 2
    parent = next(b for b in boxes if "dash" not in b[5])
    child = next(b for b in boxes if "dash" in b[5])
    # child strictly within parent on every side
    assert parent[1] < child[1] and parent[2] < child[2]
    assert child[3] < parent[3] and child[4] < parent[4]


def test_sibling_blocks_get_distinct_colours():
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("a", ("XM1", "XM2")),
            BlockAnnotation("b", ("XM3", "XM4")),
        )
    )
    layers = [b[0] for b in _boxes(build_sch(_circuit(), annotations=aset).text)]
    assert len(set(layers)) == 2


def test_coincident_labels_are_staggered():
    # Two blocks whose boxes share a top-left corner must not stack their labels on one spot.
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("a", ("XM1", "XM2", "XM3", "XM4"), label="outer-A"),
            BlockAnnotation("b", ("XM1", "XM2", "XM3", "XM4"), label="outer-B"),
        )
    )
    texts = {t[0]: t for t in _texts(build_sch(_circuit(), annotations=aset).text)}
    assert texts["outer-A"][2] != texts["outer-B"][2]  # different y


# --------------------------------------------------------------------------------------------------
# Robustness + additivity
# --------------------------------------------------------------------------------------------------
def test_missing_device_ref_warns_but_boxes_the_rest():
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "NOPE")),))
    doc = build_sch(_circuit(), annotations=aset)
    assert doc.annotation_count == 1  # still boxed around XM1
    assert any("NOPE" in w for w in doc.warnings)


def test_block_with_no_placed_device_is_skipped_with_warning():
    aset = BlockAnnotationSet((BlockAnnotation("ghost", ("NOPE1", "NOPE2")),))
    doc = build_sch(_circuit(), annotations=aset)
    assert doc.annotation_count == 0
    assert any("ghost" in w for w in doc.warnings)


def test_overlay_only_does_not_change_connectivity():
    """With block-aware placement *off*, the overlay is purely additive: the boxes draw over the
    unchanged block-agnostic layout, so every non-``B``/``T`` line is byte-identical to the base."""
    circuit = _circuit()
    base = build_sch(circuit)
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2")),))
    over = build_sch(circuit, annotations=aset, annotation_aware_placement=False)
    # counts that define the electrical content are unchanged
    assert (over.device_count, over.wire_count, over.label_count, over.port_count) == (
        base.device_count,
        base.wire_count,
        base.label_count,
        base.port_count,
    )
    # and the non-annotation lines are byte-identical (the overlay only *adds* B/T lines)
    non_anno = [ln for ln in over.text.splitlines() if not ln.startswith(("B ", "T "))]
    base_lines = [ln for ln in base.text.splitlines() if not ln.startswith(("B ", "T "))]
    assert non_anno == base_lines


def test_block_aware_placement_preserves_device_and_port_counts():
    """Block-aware placement (the default when annotations are given) is a layout-only hint: it may
    move devices / re-route wires, but it never changes the *electrical* content — the same devices are
    placed and the same circuit-I/O ports are drawn. (Wire/label counts may differ, as the layout did.)"""
    circuit = _circuit()
    base = build_sch(circuit)
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2")),))
    aware = build_sch(circuit, annotations=aset)  # default: annotation_aware_placement=True
    assert aware.device_count == base.device_count
    assert aware.port_count == base.port_count
    assert aware.annotation_count == 1
    assert not aware.warnings
    # deterministic
    assert build_sch(circuit, annotations=aset).text == aware.text


def test_placement_clusters_merge_nested_and_device_sharing_blocks():
    """``placement_clusters`` fuses blocks that nest (``parent_id``) or share a device into one coherent
    device group, and keeps unrelated blocks apart — so block-aware placement clusters a whole cascode
    mirror (reference + cascode + subsumed simple mirror) yet still separates it from a diff pair."""
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("casc", ("XM1", "XM2", "XM3", "XM4")),
            BlockAnnotation("simple", ("XM1", "XM2"), parent_id="casc"),  # nested → merges up
            BlockAnnotation("share", ("XM4", "XM5")),  # shares XM4 with casc → merges in
            BlockAnnotation("dp", ("XM7", "XM8")),  # unrelated → its own cluster
        )
    )
    clusters = aset.placement_clusters()
    assert ("XM1", "XM2", "XM3", "XM4", "XM5") in clusters
    assert ("XM7", "XM8") in clusters
    assert len(clusters) == 2
    # deterministic + sorted
    assert aset.placement_clusters() == clusters
    assert BlockAnnotationSet(()).placement_clusters() == ()


def test_emission_is_deterministic():
    aset = BlockAnnotationSet((BlockAnnotation("g1", ("XM1", "XM2"), label="m"),))
    a = build_sch(_circuit(), annotations=aset).text
    b = build_sch(_circuit(), annotations=aset).text
    assert a == b


def test_depths_guard_against_parent_cycle():
    # A block pointing at itself (or a missing parent) must not recurse forever; it just goes top-level.
    aset = BlockAnnotationSet(
        (
            BlockAnnotation("x", ("XM1",), parent_id="x"),
            BlockAnnotation("y", ("XM2",), parent_id="missing"),
        )
    )
    doc = build_sch(_circuit(), annotations=aset)
    assert doc.annotation_count == 2  # both still drawn


@pytest.mark.parametrize("ref", ["XM1", "XM3"])
def test_single_device_block_is_boxed(ref):
    doc = build_sch(_circuit(), annotations=BlockAnnotationSet((BlockAnnotation("s", (ref,)),)))
    assert doc.annotation_count == 1


# --- the documented contract (README "The `@1` contract") ---------------------------------------

_PKG = Path(__file__).resolve().parents[1]


def _contract_section(readme: str) -> tuple[str, str]:
    """(heading text, section body) of the README's contract section."""
    lines = readme.splitlines()
    i = next(n for n, ln in enumerate(lines) if ln.startswith("### ") and "contract" in ln)
    end = next((n for n in range(i + 1, len(lines)) if lines[n].startswith("#")), len(lines))
    return lines[i][4:], "\n".join(lines[i + 1 : end])


def _table_fields(section: str) -> set[str]:
    return set(
        re.findall(r"`(\w+)`", "\n".join(ln for ln in section.splitlines() if ln.startswith("| `")))
    )


def test_readme_contract_documents_every_field_this_package_writes():
    heading, section = _contract_section((_PKG / "README.md").read_text(encoding="utf-8"))
    assert "@1" in heading
    written = set(BlockAnnotation("g", ("XM1",)).to_dict())
    missing = written - _table_fields(section)
    assert not missing, f"README contract table does not name: {sorted(missing)}"
    # the policy the loader enforces is the policy the section states
    assert ANNOTATION_SCHEMA in section and "`@2`" in section and "`blocks`" in section


def test_circuitgraph_readme_links_to_the_contract_section():
    cg_readme = _PKG.parent / "spicexplorer-circuitgraph" / "README.md"
    if not cg_readme.is_file():
        pytest.skip("circuitgraph is not checked out beside this package")
    heading, _ = _contract_section((_PKG / "README.md").read_text(encoding="utf-8"))
    # GitHub's heading anchor: lower-case, punctuation other than '-' dropped, spaces -> '-'
    anchor = re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
    assert f"../spicexplorer-netlist2xschem/README.md#{anchor}" in cg_readme.read_text(
        encoding="utf-8"
    )
