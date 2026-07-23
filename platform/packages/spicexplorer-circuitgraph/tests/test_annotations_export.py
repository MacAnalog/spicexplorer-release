"""Export detected sub-circuits to the neutral xschem block-annotation contract.

Covers the producer half of the detect → annotate → render pipeline: the schema/shape of the emitted
dict, the group → block mapping, nesting from ``subsumed`` matches, alternate folding, the
annotated-graph entry point, and the file writer. Synthetic :class:`MirrorGroup` / :class:`SubcircuitMatch`
objects keep the mapping tests independent of the matcher; one integration test runs the real detector
on the shipped 5T OTA example.
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import replace

import pytest
from spicexplorer_circuitgraph import (
    ANNOTATION_SCHEMA,
    CircuitGraph,
    MirrorGroup,
    SubcircuitMatch,
    TemplateLibrary,
    annotate_subcircuits,
    export_subcircuit_annotations,
    find_subcircuits,
    group_matches,
    write_subcircuit_annotations,
)
from spicexplorer_core.spice_engine import NetlistView


def _example_netlist(rel: str):
    from spicexplorer_core import project_root

    p = project_root() / rel
    return p if p.exists() else None


def _match(template_id, mirror_class, family, devices, *, polarity="nmos") -> SubcircuitMatch:
    return SubcircuitMatch(
        template_id=template_id,
        mirror_class=mirror_class,
        polarity=polarity,
        family=family,
        devices=tuple(devices),
        device_map={},
        net_map={},
        ports={},
        reference_device=devices[0],
        output_devices=tuple(devices[1:]),
    )


def _group(group_id, mirror_class, family, devices, *, subsumed=(), alternates=()) -> MirrorGroup:
    return MirrorGroup(
        group_id=group_id,
        template_id=f"cm.nmos.{mirror_class}",
        mirror_class=mirror_class,
        polarity="nmos",
        family=family,
        reference_device=devices[0],
        output_devices=tuple(devices[1:]),
        devices=tuple(devices),
        ports={},
        subsumed=tuple(subsumed),
        alternates=tuple(alternates),
    )


# --------------------------------------------------------------------------------------------------
# Shape + mapping
# --------------------------------------------------------------------------------------------------
def test_export_empty_is_valid():
    out = export_subcircuit_annotations([])
    assert out == {"schema": ANNOTATION_SCHEMA, "blocks": []}


def test_group_maps_to_one_top_level_block():
    out = export_subcircuit_annotations([_group("cm.nmos.simple#1", "simple", "current_mirror", ["XM5", "XM6"])])
    (b,) = out["blocks"]
    assert b["block_id"] == "cm.nmos.simple#1"
    assert b["parent_id"] is None
    assert b["devices"] == ["XM5", "XM6"]
    assert b["family"] == "current_mirror"
    assert b["label"] == "NMOS Simple Current Mirror"


def test_subsumed_match_becomes_nested_block():
    grp = _group(
        "cm.nmos.cascode#1",
        "cascode",
        "current_mirror",
        ["XM1", "XM2", "XM3", "XM4"],
        subsumed=[_match("cm.nmos.simple", "simple", "current_mirror", ["XM1", "XM2"])],
    )
    blocks = export_subcircuit_annotations([grp])["blocks"]
    assert len(blocks) == 2
    parent, child = blocks[0], blocks[1]
    assert parent["parent_id"] is None
    assert child["parent_id"] == "cm.nmos.cascode#1"
    assert child["devices"] == ["XM1", "XM2"]
    assert child["template_id"] == "cm.nmos.simple"


def test_alternates_are_folded_into_the_block():
    grp = _group(
        "cm.nmos.cascode#1",
        "cascode",
        "current_mirror",
        ["XM1", "XM2", "XM3", "XM4"],
        alternates=[_match("cm.nmos.improved_wilson", "improved_wilson", "current_mirror", ["XM1", "XM2", "XM3", "XM4"])],
    )
    (b,) = export_subcircuit_annotations([grp])["blocks"]
    assert b["alternates"] == ["cm.nmos.improved_wilson"]


def test_differential_pair_label_drops_redundant_class():
    # A diff pair's class IS "differential_pair" — the label must not repeat it.
    (b,) = export_subcircuit_annotations(
        [_group("dp.nmos.simple#1", "differential_pair", "differential_pair", ["XM1", "XM2"])]
    )["blocks"]
    assert b["label"] == "NMOS Differential Pair"


def test_multi_output_mirror_label_shows_fan_out():
    # A mirror feeding more than one output advertises the 1:N fan-out (ref XM0 → XM1/XM2/XM3).
    (b,) = export_subcircuit_annotations(
        [_group("cm.nmos.simple#1", "simple", "current_mirror", ["XM0", "XM1", "XM2", "XM3"])]
    )["blocks"]
    assert b["label"] == "NMOS Simple Current Mirror (3 outputs)"


def test_port_names_map_boundary_nets_to_template_roles_with_increment():
    # A 1:2 mirror: the representative keeps the bare ``out`` role; the second branch's output net is
    # numbered ``out_2`` (the "increment per extra output" convention). Shared roles (supply/ref_in) map
    # to one net each. Built from two member matches that differ only in their ``out`` host net.
    m1 = _match("cm.nmos.simple", "simple", "current_mirror", ["XM0", "XM1"])
    m2 = _match("cm.nmos.simple", "simple", "current_mirror", ["XM0", "XM2"])
    m1 = replace(m1, ports={"supply": "vss", "ref_in": "iref", "out": "oa"})
    m2 = replace(m2, ports={"supply": "vss", "ref_in": "iref", "out": "ob"})
    grp = replace(
        _group("cm.nmos.simple#1", "simple", "current_mirror", ["XM0", "XM1", "XM2"]),
        ports={"supply": "vss", "ref_in": "iref", "out": "oa"},
        members=(m1, m2),
    )
    (b,) = export_subcircuit_annotations([grp])["blocks"]
    assert b["port_names"] == {"vss": "supply", "iref": "ref_in", "oa": "out", "ob": "out_2"}


def test_real_5t_ota_port_names_are_functional():
    path = _example_netlist("examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice")
    if path is None:
        pytest.skip("amp_001_5t example netlist not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(path), name="ota")
    out = export_subcircuit_annotations(group_matches(find_subcircuits(g)))
    pair = next(b for b in out["blocks"] if b["family"] == "differential_pair")
    # the diff pair exposes its template port roles on real host nets (the join key into the schematic)
    assert set(pair["port_names"].values()) >= {"supply", "in_p", "in_n", "out_p", "out_n", "CM_tail"}
    host_nets = {net for c in g.get_components() for net in g.connections(c).values()}
    assert set(pair["port_names"]) <= host_nets


# --------------------------------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------------------------------
def test_write_round_trips_through_json(tmp_path):
    grp = _group("cm.nmos.simple#1", "simple", "current_mirror", ["XM5", "XM6"])
    path = write_subcircuit_annotations([grp], tmp_path / "blocks.json")
    loaded = json.loads(path.read_text())
    assert loaded["schema"] == ANNOTATION_SCHEMA
    assert loaded["blocks"][0]["devices"] == ["XM5", "XM6"]


def test_export_from_annotated_graph_matches_export_from_groups():
    path = _example_netlist("examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice")
    if path is None:
        pytest.skip("amp_001_5t example netlist not present")
    view = NetlistView.from_file(path)
    groups = group_matches(find_subcircuits(CircuitGraph.from_netlist(view, name="ota")))
    g2 = CircuitGraph.from_netlist(view, name="ota")
    annotate_subcircuits(g2)  # populates g2.subcircuit_matches AND assigns per-device roles
    from_graph = export_subcircuit_annotations(g2)
    from_groups = export_subcircuit_annotations(groups)
    # `roles` is the one field only the annotated-graph path can know (the role pass runs on the
    # graph); everything else must agree bit-for-bit between the two entry points.
    assert all(b["roles"] for b in from_graph["blocks"])  # graph path carries the roles
    assert all(b["roles"] == {} for b in from_groups["blocks"])  # bare groups cannot
    for b in from_graph["blocks"]:
        b["roles"] = {}
    assert from_graph == from_groups


# --------------------------------------------------------------------------------------------------
# DR-3 — per-block `rules_ref` (governing design-rule docs) + `roles` (deterministic device roles)
# --------------------------------------------------------------------------------------------------
_SIMPLE_NMOS_MIRROR = """\
* simple nmos current mirror
XM1 iin iin VSS VSS sg13_lv_nmos w=0.15u l=0.13u
XM2 iout iin VSS VSS sg13_lv_nmos w=0.15u l=0.13u
.end
"""


def _mirror_lib_with_rules(tmp_path) -> TemplateLibrary:
    """A one-template library authored via a manifest that registers a family rules doc."""
    (tmp_path / "simple_nmos.spice").write_text(_SIMPLE_NMOS_MIRROR)
    (tmp_path / "rules").mkdir()
    (tmp_path / "rules" / "current_mirror.md").write_text("# CM rules\n")
    (tmp_path / "manifest.yaml").write_text(
        textwrap.dedent(
            """\
            schema: spicexplorer/subcircuit-template-library@1
            family: current_mirror
            rules:
              - path: rules/current_mirror.md
                title: "CM sizing + detection"
            templates:
              - id: cm.nmos.simple
                class: simple
                polarity: nmos
                netlist: simple_nmos.spice
                ports: {supply: VSS, ref_in: iin, out: iout}
            """
        )
    )
    return TemplateLibrary.from_manifest(tmp_path / "manifest.yaml")


def test_rules_ref_points_at_the_family_rule_doc(tmp_path):
    lib = _mirror_lib_with_rules(tmp_path)
    g = CircuitGraph.from_netlist(NetlistView.from_string(_SIMPLE_NMOS_MIRROR), name="host")
    annotate_subcircuits(g, lib)
    (b,) = export_subcircuit_annotations(g, library=lib)["blocks"]
    # tmp_path lives outside the workspace root, so the path is emitted absolute — still resolvable
    assert b["rules_ref"] == [str((tmp_path / "rules" / "current_mirror.md").resolve())]


def test_roles_carry_the_deterministic_per_device_assignment(tmp_path):
    lib = _mirror_lib_with_rules(tmp_path)
    g = CircuitGraph.from_netlist(NetlistView.from_string(_SIMPLE_NMOS_MIRROR), name="host")
    annotate_subcircuits(g, lib)
    (b,) = export_subcircuit_annotations(g, library=lib)["blocks"]
    # the exported roles are exactly what the deterministic pass wrote onto the graph
    assert b["roles"] == {"XM1": "current_mirror_reference", "XM2": "current_mirror"}


def test_bare_group_export_keeps_rules_ref_but_cannot_know_roles(tmp_path):
    # Exporting a bare group list: `rules_ref` still resolves through the library (it is template
    # metadata), but `roles` stays empty — no role pass ran, so there is nothing truthful to emit.
    (b,) = export_subcircuit_annotations(
        [_group("cm.nmos.simple#1", "simple", "current_mirror", ["XM5", "XM6"])],
        library=_mirror_lib_with_rules(tmp_path),
    )["blocks"]
    assert b["roles"] == {}
    assert b["rules_ref"] == [str((tmp_path / "rules" / "current_mirror.md").resolve())]


def test_real_5t_ota_yields_mirrors_and_pair():
    path = _example_netlist("examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice")
    if path is None:
        pytest.skip("amp_001_5t example netlist not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(path), name="ota")
    out = export_subcircuit_annotations(group_matches(find_subcircuits(g)))
    assert out["schema"] == ANNOTATION_SCHEMA
    families = {b["family"] for b in out["blocks"]}
    assert {"current_mirror", "differential_pair"} <= families
    # every block's devices are real host instance refs (the join key into a schematic)
    host_devs = {c.name for c in g.get_components()}
    for b in out["blocks"]:
        assert set(b["devices"]) <= host_devs
        assert b["parent_id"] is None or b["parent_id"] in {x["block_id"] for x in out["blocks"]}
