"""Net-to-net path tracing (find_paths_between) and structural path diffing (diff_paths).

Covers: shortest vs all paths, label/touchpoint rendering, the supply-rail exclusion default,
the optional ideal-voltage-source exclusion, the max-components cap, case-insensitive/absent/identical
endpoints, diode-connected pin fan-out, the four diff verdicts (identical / pin-only / device-only /
device-pin), and JSON serialization.
"""

from pathlib import Path

import pytest
from spicexplorer_circuitgraph import (
    IHP_SG13G2,
    CircuitGraph,
    DiffKind,
    GraphPath,
    PathStep,
    StepDiffKind,
    diff_paths,
    find_paths_between,
    shortest_paths_between,
)
from spicexplorer_circuitgraph.model.nodes import DeviceType, MosfetNode, MosPolarityType
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"

# A small 5T-OTA-like core. M3 is diode-connected (gate == drain == out1), which gives two ways to
# enter it from out1 — the natural source of a pin-only difference.
OTA_CORE = """* ota core
M1 out1 vinp tail vss sg13_lv_nmos
M2 out2 vinn tail vss sg13_lv_nmos
M3 out1 out1 vdd vdd sg13_lv_pmos
M4 out2 out1 vdd vdd sg13_lv_pmos
M5 tail vbias vss vss sg13_lv_nmos
.end
"""

# Two devices with no shared net (vss is bulk only) -> 'a' and 'c' are disconnected once supply
# rails are dropped.
DISJOINT = """* disjoint
M1 a g1 b vss sg13_lv_nmos
M2 c g2 d vss sg13_lv_nmos
.end
"""

# M2 is gate-source shorted (d g s b = nmid nout nout vss): an off enhancement device sitting on the
# nin -> nout channel path.
GS_SHORT = """* gate-source short
M1 nin g1 nmid vss sg13_lv_nmos
M2 nmid nout nout vss sg13_lv_nmos
.end
"""


def _g(netlist: str, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_string(netlist), pdk=IHP_SG13G2, **kw)


def _cascode() -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(CASCODE_FLAT), pdk=IHP_SG13G2, name="ota")


def _step(comp, in_pin, out_pin, in_net="x", out_net="y", device_type=DeviceType.MOS) -> PathStep:
    return PathStep(
        component=comp, device_type=device_type, in_pin=in_pin, out_pin=out_pin,
        in_net=in_net, out_net=out_net,
    )


def _path(steps, source="A", target="Z") -> GraphPath:
    nets = [source] + [s.out_net for s in steps]
    return GraphPath(source=source, target=target, nets=nets, steps=steps)


# ---------------------------------------------------------------------------
# find_paths_between
# ---------------------------------------------------------------------------
def test_shortest_input_to_tail_is_a_single_hop():
    paths = shortest_paths_between(_g(OTA_CORE), "vinp", "tail")
    assert len(paths) == 1
    p = paths[0]
    assert p.length == 1
    assert p.label == "M1.gate->M1.source"
    assert p.touchpoints == ["M1.gate", "M1.source"]
    assert p.components == ["M1"]
    assert p.steps[0].polarity is MosPolarityType.NMOS


def test_label_and_describe_render_the_chain():
    p = shortest_paths_between(_g(OTA_CORE), "vinp", "out1")[0]
    # vinp enters M1 at the gate and leaves at the drain (out1)
    assert p.label == "M1.gate->M1.drain"
    assert "vinp" in p.describe() and "out1" in p.describe()


def test_distinct_endpoints_required():
    with pytest.raises(ValueError, match="distinct endpoints"):
        find_paths_between(_g(OTA_CORE), "vinp", "vinp")


def test_absent_net_raises():
    with pytest.raises(ValueError, match="not present"):
        find_paths_between(_g(OTA_CORE), "nope", "tail")


def test_net_resolution_is_case_insensitive():
    p = shortest_paths_between(_g(OTA_CORE), "VINP", "TAIL")
    assert p and p[0].label == "M1.gate->M1.source"


def test_no_path_returns_empty():
    assert find_paths_between(_g(DISJOINT), "a", "c") == []


def test_supply_rails_excluded_by_default():
    g = _g(OTA_CORE)
    # vinp and vinn only meet through the tail node or a rail; routing through vss only appears
    # once supply traversal is allowed.
    without = find_paths_between(g, "vinp", "vinn", max_components=4)
    through = find_paths_between(g, "vinp", "vinn", max_components=4, through_supply=True)
    assert len(through) > len(without)
    assert all(not p.through_supply for p in without)
    assert any(p.through_supply for p in through)


def test_max_components_caps_path_length():
    paths = find_paths_between(_cascode(), "vinp", "vout", max_components=3)
    assert paths
    assert all(p.length <= 3 for p in paths)


def test_shortest_is_a_minimal_length_subset():
    g = _cascode()
    every = find_paths_between(g, "vinp", "vout", max_components=6)
    shortest = shortest_paths_between(g, "vinp", "vout")
    assert shortest
    min_len = min(p.length for p in every)
    assert all(p.length == min_len for p in shortest)


def test_results_are_deterministically_sorted():
    g = _cascode()
    a = find_paths_between(g, "vinp", "vout", max_components=3)
    b = find_paths_between(g, "vinp", "vout", max_components=3)
    assert [p.label for p in a] == [p.label for p in b]
    assert [p.label for p in a] == sorted([p.label for p in a]) or \
        [(p.length, p.label) for p in a] == sorted((p.length, p.label) for p in a)


def test_diode_connected_device_fans_out_into_pin_level_paths():
    # M3 is "out1 out1 vdd vdd": DRAIN and GATE both sit on out1, SOURCE and BULK both on vdd, so a
    # single node hop fans out into the full 2x2 product of entering x leaving pins.
    paths = shortest_paths_between(_g(OTA_CORE), "out1", "vdd")
    m3 = {p.label for p in paths if p.components == ["M3"]}
    assert m3 == {
        "M3.drain->M3.source", "M3.gate->M3.source",
        "M3.drain->M3.bulk", "M3.gate->M3.bulk",
    }


# ---------------------------------------------------------------------------
# diff_paths — the four verdicts
# ---------------------------------------------------------------------------
def test_diff_identical_path_against_itself():
    p = shortest_paths_between(_g(OTA_CORE), "vinp", "tail")[0]
    d = diff_paths(p, p)
    assert d.kind is DiffKind.IDENTICAL
    assert not d.only_in_a.steps and not d.only_in_b.steps
    assert d.common.devices == ["M1"]


def test_diff_pin_only_from_diode_fanout():
    # the two ways through diode-connected M3 differ only in the entering pin
    m3 = [p for p in shortest_paths_between(_g(OTA_CORE), "out1", "vdd") if p.components == ["M3"]]
    d = diff_paths(m3[0], m3[1])
    assert d.kind is DiffKind.PIN_ONLY
    assert d.only_in_a.devices == ["M3"] and d.only_in_b.devices == ["M3"]
    assert all(s.diff_kind is StepDiffKind.PIN_ONLY for s in d.only_in_a.steps)
    assert not d.common.steps


def test_diff_device_only_disjoint_devices():
    a = _path([_step("M1", "GATE", "SOURCE"), _step("M2", "DRAIN", "SOURCE")])
    b = _path([_step("M1", "GATE", "SOURCE"), _step("M9", "DRAIN", "SOURCE")])
    d = diff_paths(a, b)
    assert d.kind is DiffKind.DEVICE_ONLY
    assert d.only_in_a.devices == ["M2"]
    assert d.only_in_b.devices == ["M9"]
    assert d.common.devices == ["M1"]
    assert all(s.diff_kind is StepDiffKind.DEVICE_ONLY for s in d.only_in_a.steps)


def test_diff_device_pin_when_both_differences_present():
    a = _path([_step("M1", "GATE", "SOURCE"), _step("M2", "DRAIN", "SOURCE")])
    b = _path([_step("M1", "GATE", "DRAIN"), _step("M9", "DRAIN", "SOURCE")])  # M1 pins differ + M2/M9
    d = diff_paths(a, b)
    assert d.kind is DiffKind.DEVICE_PIN
    assert "M1" in d.only_in_a.devices and "M2" in d.only_in_a.devices
    assert {s.diff_kind for s in d.only_in_a.steps} == {StepDiffKind.PIN_ONLY, StepDiffKind.DEVICE_ONLY}


def test_diff_direction_insensitive_is_common():
    # same device, same pin pair, opposite direction -> still common (no spurious diff)
    a = _path([_step("M1", "DRAIN", "SOURCE")])
    b = _path([_step("M1", "SOURCE", "DRAIN")])
    d = diff_paths(a, b)
    assert d.kind is DiffKind.IDENTICAL
    assert d.common.devices == ["M1"]


# ---------------------------------------------------------------------------
# serialization
# ---------------------------------------------------------------------------
def test_path_serializes_to_json_with_derived_labels():
    p = shortest_paths_between(_g(OTA_CORE), "vinp", "tail")[0]
    dumped = p.model_dump()
    assert dumped["label"] == "M1.gate->M1.source"
    assert dumped["touchpoints"] == ["M1.gate", "M1.source"]
    assert dumped["steps"][0]["device_type"] == "MOS"
    assert isinstance(p.model_dump_json(), str)


def test_diff_serializes_and_describes():
    a = _path([_step("M1", "GATE", "SOURCE"), _step("M2", "DRAIN", "SOURCE")])
    b = _path([_step("M1", "GATE", "SOURCE"), _step("M9", "DRAIN", "SOURCE")])
    d = diff_paths(a, b)
    dumped = d.model_dump()
    assert dumped["kind"] == "device_only"
    assert dumped["only_in_a"]["touchpoints"] == ["M2.drain", "M2.source"]
    assert "only in path A" in d.describe()


# ---------------------------------------------------------------------------
# MOSFET conduction state (gate-source / drain-source shorts)
# ---------------------------------------------------------------------------
def test_mosfet_short_detectors():
    g = _g(GS_SHORT)
    m1, m2 = g._comp_map["M1"], g._comp_map["M2"]
    assert isinstance(m1, MosfetNode) and isinstance(m2, MosfetNode)
    assert m2.is_gate_source_shorted(g._G) and not m2.is_drain_source_shorted(g._G)
    assert not m1.is_gate_source_shorted(g._G)
    # OTA_CORE M3 (out1 out1 vdd vdd) is diode-connected, not gate-source shorted
    core = _g(OTA_CORE)
    m3 = core._comp_map["M3"]
    assert isinstance(m3, MosfetNode)
    assert m3.is_diode_connected(core._G) and not m3.is_gate_source_shorted(core._G)


def test_respect_mosfet_state_drops_off_channel():
    g = _g(GS_SHORT)
    topo = {p.label for p in find_paths_between(g, "nmid", "nout")}
    cond = {p.label for p in find_paths_between(g, "nmid", "nout", respect_mosfet_state=True)}
    assert "M2.drain->M2.source" in topo          # the channel hop is present topologically
    assert "M2.drain->M2.source" not in cond       # …and removed when off
    assert "M2.drain->M2.gate" in cond             # gate edge remains (channel-only scope)


def test_depletion_assumption_keeps_the_channel():
    g = _g(GS_SHORT)
    cond = {p.label for p in find_paths_between(
        g, "nmid", "nout", respect_mosfet_state=True, gs_short_is_off=False)}
    assert "M2.drain->M2.source" in cond           # depletion device can still conduct at Vgs=0


def test_respect_mosfet_state_defaults_off_and_is_non_breaking():
    g = _g(GS_SHORT)
    default = [p.label for p in find_paths_between(g, "nmid", "nout")]
    explicit = [p.label for p in find_paths_between(g, "nmid", "nout", respect_mosfet_state=False)]
    assert default == explicit


def test_diode_connected_channel_is_kept_under_conduction():
    # a diode-connected device is always in saturation -> its channel stays a valid path
    core = _g(OTA_CORE)
    labels = {p.label for p in find_paths_between(core, "out1", "vdd", respect_mosfet_state=True)}
    assert any(lbl.startswith("M3.drain->M3.source") or lbl == "M3.drain->M3.source" for lbl in labels)


def test_drain_source_short_detected_on_real_decoupling_devices():
    g = _cascode()
    killed = [c.name for c in g.get_components()
              if isinstance(c, MosfetNode) and c.is_drain_source_shorted(g._G)]
    assert "XMDECOUP1" in killed and "XMDECOUP3" in killed


# ---------------------------------------------------------------------------
# Regressions (found by adversarial review)
# ---------------------------------------------------------------------------
def test_shortest_only_ignores_max_components():
    # max_components must not silently empty a shortest_only result when the shortest path is longer.
    g = _cascode()
    full = shortest_paths_between(g, "vinp", "vout")
    assert full and min(p.length for p in full) == 3
    capped = shortest_paths_between(g, "vinp", "vout", max_components=2)  # below the true shortest
    assert [p.label for p in capped] == [p.label for p in full]


def test_diff_handles_a_device_visited_twice():
    # diff_paths accepts any GraphPath; a device traversed twice must not collapse the comparison.
    twice = [_step("M1", "DRAIN", "GATE"), _step("M2", "DRAIN", "SOURCE"), _step("M1", "SOURCE", "BULK")]
    d = diff_paths(_path(list(twice)), _path(list(twice)))
    assert d.kind is DiffKind.IDENTICAL
    assert not d.only_in_a.steps and not d.only_in_b.steps
    assert len(d.common.steps) == 3


def test_diff_verdict_is_consistent_with_step_tags():
    # a step tagged PIN_ONLY must never sit under a verdict that claims only device differences
    a = _path([_step("M1", "DRAIN", "GATE")])
    b = _path([_step("M1", "DRAIN", "SOURCE"), _step("M1", "DRAIN", "GATE")])
    d = diff_paths(a, b)
    tags = {s.diff_kind for s in d.only_in_a.steps + d.only_in_b.steps}
    if StepDiffKind.PIN_ONLY in tags:
        assert d.kind in (DiffKind.PIN_ONLY, DiffKind.DEVICE_PIN)
    assert d.summary and not d.summary.endswith(": ")  # non-degenerate


# ---------------------------------------------------------------------------
# Structural invariants: loop-freeness and per-path pin uniqueness
# ---------------------------------------------------------------------------
# A pure 4-net resistor ring n1-n2-n3-n4-n1. Between n1 and n3 there are exactly two simple routes
# (over the top via n2, under via n4); a naive walk could loop (n1->n2->n1). None of the nets is a
# supply rail, so the ring is traversed whether or not through_supply is set.
RING = """* resistor ring
R1 n1 n2 1k
R2 n2 n3 1k
R3 n3 n4 1k
R4 n4 n1 1k
.end
"""


def _assert_loop_free(p: GraphPath) -> None:
    """Every path must visit each net, each device, and each device.pin touchpoint at most once."""
    assert len(set(p.nets)) == len(p.nets), f"net repeated: {p.nets}"
    assert len(set(p.components)) == len(p.components), f"device repeated: {p.components}"
    assert len(set(p.touchpoints)) == len(p.touchpoints), f"device.pin repeated: {p.touchpoints}"
    for s in p.steps:
        # consecutive nets always differ, so a step never enters and leaves on the same net,
        # and a single traversal never reuses a pin
        assert s.in_net != s.out_net, f"step sits on one net: {s.label} on {s.in_net}"
        assert s.in_pin != s.out_pin, f"step reuses one pin: {s.label}"


def test_every_path_is_loop_free_across_topologies():
    # Sweep a genuine cycle (the ring), a current-mirror core, and the flat cascode — including
    # supply-hub-heavy through_supply searches, where loop temptations are greatest.
    sweeps = [
        (_g(RING), "n1", "n3", {}),
        (_g(RING), "n1", "n3", {"through_supply": True}),
        (_g(OTA_CORE), "vinp", "vinn", {"max_components": 5}),
        (_g(OTA_CORE), "vinp", "vinn", {"max_components": 5, "through_supply": True}),
        (_g(OTA_CORE), "out1", "vdd", {}),
        (_cascode(), "vinp", "vout", {"max_components": 4}),
    ]
    total = 0
    for g, a, b, kw in sweeps:
        paths = find_paths_between(g, a, b, **kw)
        for p in paths:
            _assert_loop_free(p)
        total += len(paths)
    assert total > 0, "the sweep traced no paths — the invariant was never exercised"


def test_ring_has_exactly_two_simple_routes_each_visiting_every_node_once():
    paths = find_paths_between(_g(RING), "n1", "n3")
    assert len(paths) == 2
    assert all(p.length == 2 for p in paths)
    # the two loop-free ways around the ring — never a third that revisits a node
    assert {tuple(p.components) for p in paths} == {("R1", "R2"), ("R4", "R3")}
    for p in paths:
        _assert_loop_free(p)


def test_diode_short_is_never_traversed_as_its_own_hop():
    # M3 is diode-connected (drain == gate == out1). The drain-gate short must never surface as a
    # step (that would require entering and leaving on the same net), no matter how we search.
    g = _g(OTA_CORE)
    searches = [
        find_paths_between(g, "out1", "vdd"),
        find_paths_between(g, "out1", "vdd", through_supply=True),
        find_paths_between(g, "vinp", "out1", max_components=4),
        find_paths_between(g, "out2", "out1", max_components=4, through_supply=True),
    ]
    saw_m3 = False
    for paths in searches:
        for p in paths:
            for s in p.steps:
                if s.component == "M3":
                    saw_m3 = True
                    assert {s.in_pin, s.out_pin} != {"DRAIN", "GATE"}, \
                        f"diode short traversed as a hop: {s.label}"
    assert saw_m3, "M3 never appeared on a traced path — the guard would be vacuous"


def test_each_device_contributes_at_most_one_step_per_path():
    # The bipartite walk visits each device node once, so a device can appear in a path at most once
    # even when it offers several pin routes (diode-connected M3 fans out across *separate* paths,
    # never twice within one).
    g = _g(OTA_CORE)
    for p in find_paths_between(g, "out1", "vdd", through_supply=True, max_components=5):
        counts = {c: p.components.count(c) for c in p.components}
        assert all(n == 1 for n in counts.values()), f"a device recurs within one path: {counts}"


# ---------------------------------------------------------------------------
# Ideal-voltage-source exclusion (block_voltage_sources)
# ---------------------------------------------------------------------------
# V1 is paralleled by resistor R2 between n1 and n2, with R1/R3 completing an a->b chain. Two routes
# exist: through the ideal source V1, and through the parallel resistor R2. Blocking voltage sources
# must drop only the V1 route and keep the R2 one.
VSRC_PARALLEL = """* voltage source paralleled by a resistor
R1 a n1 1k
V1 n1 n2 1.0
R2 n1 n2 5k
R3 n2 b 1k
.end
"""

# a and b are bridged ONLY by the ideal source V1 (in series with R1) — blocking it leaves no route.
VSRC_BRIDGE = """* a and b bridged only by an ideal voltage source
R1 a mid 1k
V1 mid b 1.0
.end
"""


def test_voltage_source_is_traversed_by_default():
    # Off by default: a path may thread straight through the ideal source, alongside the R2 route.
    comps = {tuple(p.components) for p in find_paths_between(_g(VSRC_PARALLEL), "a", "b")}
    assert ("R1", "V1", "R3") in comps
    assert ("R1", "R2", "R3") in comps


def test_block_voltage_sources_drops_only_the_through_source_route():
    paths = find_paths_between(_g(VSRC_PARALLEL), "a", "b", block_voltage_sources=True)
    assert {tuple(p.components) for p in paths} == {("R1", "R2", "R3")}  # parallel route survives
    assert all("V1" not in p.components for p in paths)                  # the source is never walked


def test_block_voltage_sources_can_remove_the_only_route():
    g = _g(VSRC_BRIDGE)
    assert [p.components for p in find_paths_between(g, "a", "b")] == [["R1", "V1"]]
    assert find_paths_between(g, "a", "b", block_voltage_sources=True) == []


def test_block_voltage_sources_is_honored_by_shortest_paths():
    # The shorthand forwards the flag, so the shortest search excludes the source too.
    paths = shortest_paths_between(_g(VSRC_PARALLEL), "a", "b", block_voltage_sources=True)
    assert {tuple(p.components) for p in paths} == {("R1", "R2", "R3")}
    assert all("V1" not in p.components for p in paths)


def test_block_voltage_sources_defaults_off_and_is_a_noop_without_sources():
    # The flag defaults to False, and on a source-free graph (OTA_CORE) it changes nothing at all.
    g = _g(OTA_CORE)
    default = [p.label for p in find_paths_between(g, "out1", "vdd")]
    explicit_off = [p.label for p in find_paths_between(g, "out1", "vdd", block_voltage_sources=False)]
    blocked = [p.label for p in find_paths_between(g, "out1", "vdd", block_voltage_sources=True)]
    assert default == explicit_off == blocked


def test_block_voltage_sources_composes_with_through_supply():
    # Pruning the source is independent of the supply-rail rule: blocking still removes the V1 route
    # whether or not supply traversal is allowed.
    g = _g(VSRC_PARALLEL)
    for kw in ({}, {"through_supply": True}):
        paths = find_paths_between(g, "a", "b", block_voltage_sources=True, **kw)
        assert paths and all("V1" not in p.components for p in paths)
