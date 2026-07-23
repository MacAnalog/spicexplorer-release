"""Netlist-equivalence comparison (labeled bipartite-graph isomorphism).

Covers: name/order independence, topology/polarity/count differences, passive terminal symmetry
vs polar sources, opt-in param/model/supply matching, subckt black-box matching, the convenience
builders, and the real cascode fixture.
"""

import re
from pathlib import Path

import pytest
from spicexplorer_circuitgraph import (
    IHP_SG13G2,
    CircuitGraph,
    GraphComparison,
    IOPort,
    compare_graphs,
    compare_netlists,
    graphs_equivalent,
    netlists_equivalent,
)
from spicexplorer_circuitgraph.model.nodes import StructuralRole
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"
OTA5T_TB = _FIX / "ota-5t_tb-ac.spice"  # flat testbench: a subckt instance + V/I/C sources

# A small 5T-OTA-like core: NMOS input pair on a tail, a diode-connected PMOS mirror.
OTA_CORE = """* ota core
M1 out1 vinp tail vss sg13_lv_nmos
M2 out2 vinn tail vss sg13_lv_nmos
M3 out1 out1 vdd vdd sg13_lv_pmos
M4 out2 out1 vdd vdd sg13_lv_pmos
M5 tail vbias vss vss sg13_lv_nmos
.end
"""


def _g(netlist: str, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_string(netlist), pdk=IHP_SG13G2, **kw)


def _relabel(netlist: str, mapping: dict[str, str]) -> str:
    """Whole-word substitution of instance / net identifiers (a guaranteed exact relabeling)."""
    for src, dst in mapping.items():
        netlist = re.sub(rf"\b{re.escape(src)}\b", dst, netlist)
    return netlist


# ---------------------------------------------------------------------------
# Equivalence is reflexive and name/order independent
# ---------------------------------------------------------------------------
def test_identical_netlist_is_equivalent():
    result = compare_netlists(OTA_CORE, OTA_CORE, pdk=IHP_SG13G2)
    assert result.equivalent
    assert bool(result) is True  # GraphComparison is truthy when equivalent
    assert "equivalent" in result.reason


def test_consistent_relabel_and_reorder_is_equivalent():
    renamed = _relabel(
        OTA_CORE,
        {
            "M1": "MQ", "M2": "MW", "M3": "ME", "M4": "MR", "M5": "MT",
            "out1": "a1", "out2": "a2", "tail": "tt",
            "vinp": "ip", "vinn": "in", "vbias": "bb",
        },
    )
    # reorder the device lines — order must not matter
    lines = renamed.splitlines()
    renamed = "\n".join([lines[0], *reversed(lines[1:-1]), lines[-1]]) + "\n"

    result = compare_netlists(OTA_CORE, renamed, pdk=IHP_SG13G2)
    assert result.equivalent, result.reason
    # the recovered correspondence is a complete bijection
    assert len(result.component_mapping) == 5
    assert len(result.net_mapping) == 8
    assert len(set(result.component_mapping.values())) == 5
    assert len(set(result.net_mapping.values())) == 8


def test_empty_netlists_are_equivalent():
    assert compare_netlists("* a\n.end\n", "* b\n.end\n", pdk=IHP_SG13G2).equivalent


# ---------------------------------------------------------------------------
# Real differences are caught, with useful reasons
# ---------------------------------------------------------------------------
def test_moved_gate_breaks_topology():
    # Re-wire M4's gate from out1 to out2: same devices/pins, different connectivity.
    broken = OTA_CORE.replace("M4 out2 out1 vdd vdd", "M4 out2 out2 vdd vdd")
    result = compare_netlists(OTA_CORE, broken, pdk=IHP_SG13G2)
    assert not result.equivalent
    assert "topology" in result.reason


def test_polarity_difference_is_caught_and_can_be_relaxed():
    flipped = OTA_CORE.replace(
        "M5 tail vbias vss vss sg13_lv_nmos", "M5 tail vbias vss vss sg13_lv_pmos"
    )
    strict = compare_netlists(OTA_CORE, flipped, pdk=IHP_SG13G2)
    assert not strict.equivalent
    assert "NMOS" in strict.reason and "PMOS" in strict.reason
    # ignoring polarity, the topology is identical
    assert compare_netlists(OTA_CORE, flipped, pdk=IHP_SG13G2, match_polarity=False).equivalent


def test_component_count_difference_reported():
    one = "* one\nR1 a b 1k\n.end\n"
    two = "* two\nR1 a b 1k\nR2 a b 2k\n.end\n"
    result = compare_netlists(one, two, pdk=IHP_SG13G2)
    assert not result.equivalent
    assert "component count differs" in result.reason


def test_net_count_difference_reported():
    a = "* a\nR1 a b 1k\nR2 b c 1k\n.end\n"
    b = "* b\nR1 a b 1k\nR2 c d 1k\n.end\n"
    result = compare_netlists(a, b, pdk=IHP_SG13G2)
    assert not result.equivalent
    assert "net count differs" in result.reason


def test_diode_connection_is_structural():
    # M3 diode-connected (gate=drain=out1) vs the same device with its gate on a separate net.
    undioded = OTA_CORE.replace("M3 out1 out1 vdd vdd", "M3 out1 vbias vdd vdd")
    assert not compare_netlists(OTA_CORE, undioded, pdk=IHP_SG13G2).equivalent


# A ring of six resistors (one 12-node cycle) and two triangles of three resistors (two 6-node
# cycles) have IDENTICAL device counts, net counts, pin census, and degree sequence (every net has
# degree 2) — they are distinguishable *only* by a real isomorphism test, not the cheap pre-checks.
_RING6 = "* ring\n" + "".join(f"R{i} n{i} n{i % 6 + 1} 1k\n" for i in range(1, 7)) + ".end\n"
_TWO_TRIANGLES = (
    "* triangles\n"
    "R1 a b 1k\nR2 b c 1k\nR3 c a 1k\n"
    "R4 d e 1k\nR5 e f 1k\nR6 f d 1k\n.end\n"
)


def test_same_degree_sequence_but_non_isomorphic():
    result = compare_netlists(_RING6, _TWO_TRIANGLES, pdk=IHP_SG13G2)
    assert not result.equivalent
    assert "topology" in result.reason  # reached VF2, not rejected by a count/census pre-check
    # control: the ring is still equivalent to a relabeled copy of itself (the trap pair really
    # does share every cheap invariant)
    ring_relabel = _relabel(_RING6, {f"n{i}": f"m{i}" for i in range(1, 7)})
    assert compare_netlists(_RING6, ring_relabel, pdk=IHP_SG13G2).equivalent


# ---------------------------------------------------------------------------
# Pin orientation: passives (R/C/L) are symmetric, sources (V/I) are polar.
# A polar source anchors net `a`, so swapping the passive's terminals is only equivalent when
# passive symmetry is honored — and a source swap must never be.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("dev, val", [("R", "1k"), ("C", "1p"), ("L", "1n")])
def test_passive_terminal_swap_is_symmetric_by_default(dev, val):
    base = f"* base\nV1 a 0 dc 1\n{dev}1 a b {val}\n.end\n"
    swap = f"* swap\nV1 a 0 dc 1\n{dev}1 b a {val}\n.end\n"  # terminals reversed
    assert compare_netlists(base, swap, pdk=IHP_SG13G2).equivalent
    assert not compare_netlists(base, swap, pdk=IHP_SG13G2, passive_symmetry=False).equivalent


@pytest.mark.parametrize("src", ["V", "I"])
def test_source_terminals_are_never_symmetric(src):
    base = f"* base\n{src}1 a 0 dc 1\nR1 a b 1k\n.end\n"
    swap = f"* swap\n{src}1 0 a dc 1\nR1 a b 1k\n.end\n"  # flipped source terminals
    assert not compare_netlists(base, swap, pdk=IHP_SG13G2).equivalent
    # symmetry of the passive does not rescue a flipped *source*
    assert not compare_netlists(base, swap, pdk=IHP_SG13G2, passive_symmetry=False).equivalent


# ---------------------------------------------------------------------------
# Stricter matching: params/models opt-in; supply rails anchored by default
# ---------------------------------------------------------------------------
def test_param_matching_is_opt_in():
    narrow = "* n\nM1 d g s b sg13_lv_nmos w=2u l=0.18u\n.end\n"
    wide = "* w\nM1 d g s b sg13_lv_nmos w=4u l=0.18u\n.end\n"
    assert compare_netlists(narrow, wide, pdk=IHP_SG13G2).equivalent  # sizing ignored by default
    assert not compare_netlists(narrow, wide, pdk=IHP_SG13G2, match_params=True).equivalent


def test_param_matching_normalizes_engineering_values():
    micro = "* u\nM1 d g s b sg13_lv_nmos w=0.18u l=0.18u\n.end\n"
    nano = "* n\nM1 d g s b sg13_lv_nmos w=180n l=0.18u\n.end\n"  # 180n == 0.18u
    assert compare_netlists(micro, nano, pdk=IHP_SG13G2, match_params=True).equivalent


def test_model_matching_is_opt_in():
    a = "* a\nM1 d g s b sg13_lv_nmos\n.end\n"
    b = "* b\nM1 d g s b sg13_lv_nmos_v2\n.end\n"  # different model, still NMOS
    assert compare_netlists(a, b, pdk=IHP_SG13G2).equivalent
    assert not compare_netlists(a, b, pdk=IHP_SG13G2, match_models=True).equivalent


def test_model_matching_is_case_insensitive():
    # SPICE model lookup is case-insensitive, so model-name case alone is the same circuit.
    a = "* a\nM1 d g s b sg13_lv_nmos\n.end\n"
    b = "* b\nM1 d g s b SG13_LV_NMOS\n.end\n"
    assert compare_netlists(a, b, pdk=IHP_SG13G2, match_models=True).equivalent


def test_param_difference_reason_names_the_values():
    # When devices differ ONLY in a parameter, the diff message must surface the differing values
    # (not render both sides identically).
    result = compare_netlists(
        "* a\nR1 a b 1k\n.end\n", "* b\nR1 a b 2k\n.end\n", pdk=IHP_SG13G2, match_params=True
    )
    assert not result.equivalent
    assert "1000" in result.reason and "2000" in result.reason


def test_param_matching_compares_the_declared_set():
    # match_params compares the *declared* parameters, so an explicit default that the other side
    # omits is a difference (the tool cannot know an omitted `m` defaults to 1).
    a = "* a\nM1 d g s b sg13_lv_nmos w=2u l=0.18u\n.end\n"
    b = "* b\nM1 d g s b sg13_lv_nmos w=2u l=0.18u m=1\n.end\n"
    assert compare_netlists(a, b, pdk=IHP_SG13G2).equivalent  # ignored by default
    assert not compare_netlists(a, b, pdk=IHP_SG13G2, match_params=True).equivalent


def test_param_matching_is_key_case_insensitive():
    # spicelib preserves the netlist's parameter-key case (`W` vs `w`); matching must not.
    a = "* a\nM1 d g s b sg13_lv_nmos W=2u L=0.18u\n.end\n"
    b = "* b\nM1 d g s b sg13_lv_nmos w=2u l=0.18u\n.end\n"
    assert compare_netlists(a, b, pdk=IHP_SG13G2, match_params=True).equivalent


def test_supply_rails_are_anchored_by_default():
    # Supplies are special by default: reclassifying a rail (vdd -> the unclassified 'pwr') is
    # caught, and opting out with match_supply=False makes it a pure-topology (name-blind) compare.
    rails = "* rails\nM1 out in vdd vss sg13_lv_nmos\n.end\n"
    no_rail = _relabel(rails, {"vdd": "pwr"})  # 'pwr' is not classified as a supply
    result = compare_netlists(rails, no_rail, pdk=IHP_SG13G2)
    assert not result.equivalent
    assert "supply" in result.reason
    assert compare_netlists(rails, no_rail, pdk=IHP_SG13G2, match_supply=False).equivalent


def test_supply_anchoring_distinguishes_rails_from_signals():
    # A resistor across the rails is not the same as a floating resistor — by default.
    across = "* a\nR1 vdd vss 1k\n.end\n"
    floating = "* b\nR1 n1 n2 1k\n.end\n"
    assert not compare_netlists(across, floating, pdk=IHP_SG13G2).equivalent
    assert compare_netlists(across, floating, pdk=IHP_SG13G2, match_supply=False).equivalent


def test_supply_anchoring_rejects_backwards_rail_naming():
    # Naming the rails backwards relative to the topology (NMOS sources end up on a 'vdd' net) is
    # rejected by default; pure topology sees only a cosmetic net rename.
    swapped = OTA_CORE.replace("vdd", "TMP").replace("vss", "vdd").replace("TMP", "vss")
    assert not compare_netlists(OTA_CORE, swapped, pdk=IHP_SG13G2).equivalent
    assert compare_netlists(OTA_CORE, swapped, pdk=IHP_SG13G2, match_supply=False).equivalent


def test_supply_anchoring_allows_consistent_reclassification():
    # `vdd` and `vcc` both classify as VDD, so anchoring still accepts the rename — it constrains
    # by supply *class*, not by exact name (and is not trivially always-stricter-to-failure).
    a = "* a\nM1 out in vdd vss sg13_lv_nmos\n.end\n"
    b = "* b\nM1 out in vcc vss sg13_lv_nmos\n.end\n"
    assert compare_netlists(a, b, pdk=IHP_SG13G2).equivalent


# ---------------------------------------------------------------------------
# Subcircuit instances are matched as black boxes (by definition name + wiring)
# ---------------------------------------------------------------------------
def test_identical_subckt_instances_are_equivalent():
    a = "* a\nX1 in out vdd vss ota\nX2 a b vdd vss ota\n.end\n"
    b = _relabel(a, {"X1": "XA", "X2": "XB", "in": "p1", "out": "p2"})
    assert compare_netlists(a, b, pdk=IHP_SG13G2).equivalent


def test_different_subckt_definition_is_not_equivalent():
    a = "* a\nX1 in out vdd vss ota\n.end\n"
    b = "* b\nX1 in out vdd vss ota_alt\n.end\n"  # references a different subckt
    result = compare_netlists(a, b, pdk=IHP_SG13G2)
    assert not result.equivalent
    assert "device population differs" in result.reason


# ---------------------------------------------------------------------------
# I/O port anchoring (single-ended + differential)
# ---------------------------------------------------------------------------
# Two chains that are isomorphic by pure topology, but the net *named* `vout` sits at a different
# place (a degree-1 end vs a degree-2 middle), so anchoring it must reject the match.
_CHAIN_A = "* a\nV1 vin 0 dc 1\nR1 vin mid 1k\nR2 mid vout 1k\n.end\n"
_CHAIN_B = "* b\nV1 vin 0 dc 1\nR1 vin vout 1k\nR2 vout far 1k\n.end\n"


def test_io_single_ended_anchoring_constrains_the_match():
    assert compare_netlists(_CHAIN_A, _CHAIN_B, pdk=IHP_SG13G2).equivalent  # topology only
    anchored = compare_netlists(_CHAIN_A, _CHAIN_B, pdk=IHP_SG13G2, io_ports=[IOPort("vout")])
    assert not anchored.equivalent


def test_io_single_ended_anchoring_accepts_a_consistent_match():
    # Anchoring vin/vout while only internal nets are renamed stays equivalent.
    relabeled = _relabel(_CHAIN_A, {"mid": "x", "R1": "RA", "R2": "RB", "V1": "VA"})
    result = compare_netlists(
        _CHAIN_A, relabeled, pdk=IHP_SG13G2, io_ports=[IOPort("vin"), IOPort("vout")]
    )
    assert result.equivalent


# A symmetric differential pair, and the same circuit with the +/- inputs swapped on the gates.
# Pinning the two outputs makes a +/- input swap a *real* difference under strict polarity.
_DIFF_BASE = (
    "* base\nM1 outp vinp tail vss sg13_lv_nmos\nM2 outn vinn tail vss sg13_lv_nmos\n"
    "M3 tail vb vss vss sg13_lv_nmos\n.end\n"
)
_DIFF_SWAPPED = (
    "* swapped\nM1 outp vinn tail vss sg13_lv_nmos\nM2 outn vinp tail vss sg13_lv_nmos\n"
    "M3 tail vb vss vss sg13_lv_nmos\n.end\n"
)
_OUT_PORTS = [IOPort("outp"), IOPort("outn")]


def test_io_differential_swap_is_equivalent_when_swappable():
    result = compare_netlists(
        _DIFF_BASE, _DIFF_SWAPPED, pdk=IHP_SG13G2,
        io_ports=[IOPort("vinp", "vinn"), *_OUT_PORTS],  # +/- interchangeable
    )
    assert result.equivalent


def test_io_differential_swap_is_caught_under_strict_polarity():
    result = compare_netlists(
        _DIFF_BASE, _DIFF_SWAPPED, pdk=IHP_SG13G2,
        io_ports=[IOPort("vinp", "vinn", swappable=False), *_OUT_PORTS],
    )
    assert not result.equivalent


def test_io_differential_swappable_still_rejects_a_real_topology_change():
    # The +/- swap freedom must not paper over an actual rewiring (false-positive guard).
    broken = _DIFF_BASE.replace("M3 tail vb vss vss", "M3 tail vb outp vss")  # M3 source rewired
    result = compare_netlists(
        _DIFF_BASE, broken, pdk=IHP_SG13G2, io_ports=[IOPort("vinp", "vinn"), *_OUT_PORTS]
    )
    assert not result.equivalent


def test_io_ports_b_handles_differing_net_names():
    a = "* a\nV1 vin 0 dc 1\nR1 vin out 1k\n.end\n"
    b = "* b\nV1 sigin 0 dc 1\nR1 sigin sigout 1k\n.end\n"  # same circuit, different I/O names
    result = compare_netlists(
        a, b, pdk=IHP_SG13G2,
        io_ports=[IOPort("vin"), IOPort("out")],
        io_ports_b=[IOPort("sigin"), IOPort("sigout")],  # corresponds by position
    )
    assert result.equivalent


def test_io_absent_anchored_net_raises_not_silently_unanchored():
    # An anchored net that isn't in a netlist must fail loudly — a silent no-op anchor would
    # quietly run a looser comparison than asked for.
    a = "* a\nV1 vin 0 dc 1\nR1 vin out 1k\n.end\n"
    # absent on one side (renamed)
    with pytest.raises(ValueError, match="not present"):
        compare_netlists(a, a.replace("out", "internal"), pdk=IHP_SG13G2, io_ports=[IOPort("out")])
    # absent on BOTH sides — the ghost-anchor that used to silently evaporate
    with pytest.raises(ValueError, match="not present"):
        compare_netlists(a, a, pdk=IHP_SG13G2, io_ports=[IOPort("ghost")])


def test_io_net_name_matching_is_case_insensitive():
    # SPICE net names are case-insensitive, so anchoring 'VOUT' binds the 'vout' net (it must not
    # raise as "absent", and it constrains exactly as the lowercase spelling does).
    lower = compare_netlists(_CHAIN_A, _CHAIN_B, pdk=IHP_SG13G2, io_ports=[IOPort("vout")])
    upper = compare_netlists(_CHAIN_A, _CHAIN_B, pdk=IHP_SG13G2, io_ports=[IOPort("VOUT")])
    assert lower.equivalent is False
    assert upper.equivalent is False


def test_io_port_validation():
    with pytest.raises(ValueError):
        IOPort()  # zero nets
    with pytest.raises(ValueError):
        IOPort("a", "b", "c")  # three nets
    with pytest.raises(ValueError):  # a net anchored by two ports is ambiguous
        compare_netlists(_CHAIN_A, _CHAIN_A, pdk=IHP_SG13G2, io_ports=[IOPort("vin"), IOPort("vin")])
    with pytest.raises(ValueError):  # per-side lists must line up by position
        compare_netlists(
            _CHAIN_A, _CHAIN_A, pdk=IHP_SG13G2,
            io_ports=[IOPort("vin")], io_ports_b=[IOPort("vin"), IOPort("vout")],
        )


# ---------------------------------------------------------------------------
# Structural-role matching (opt-in; roles are normally None in this tool)
# ---------------------------------------------------------------------------
_TWO_MOS = "* m\nM1 d g s b sg13_lv_nmos\nM2 d2 g s2 b sg13_lv_nmos\n.end\n"


def test_structural_role_matching_is_opt_in():
    g1, g2 = _g(_TWO_MOS), _g(_TWO_MOS)
    g1._comp_map["M1"].structural_role = StructuralRole.MOS_CURRENT_MIRROR  # one side tagged
    assert compare_graphs(g1, g2).equivalent  # roles ignored by default
    assert not compare_graphs(g1, g2, match_structural_role=True).equivalent
    # tagging both sides identically restores equivalence under the strict flag
    g2._comp_map["M1"].structural_role = StructuralRole.MOS_CURRENT_MIRROR
    assert compare_graphs(g1, g2, match_structural_role=True).equivalent


# ---------------------------------------------------------------------------
# on_unknown policy flows through the comparison builder
# ---------------------------------------------------------------------------
def test_on_unknown_skip_can_mask_an_unsupported_device():
    # A BJT (Q…) reusing existing nets is dropped under the default skip policy, so the two
    # netlists compare equal even though one has an extra device. This is the documented contract
    # of skip — use on_unknown="raise" for strictness.
    base = "* a\nM1 d g s b sg13_lv_nmos\n.end\n"
    with_bjt = "* b\nM1 d g s b sg13_lv_nmos\nQ1 d g s npn\n.end\n"  # Q reuses nets d/g/s
    assert compare_netlists(base, with_bjt, pdk=IHP_SG13G2).equivalent
    # under raise, building the second netlist aborts instead of silently dropping the BJT
    with pytest.raises(ValueError):
        compare_netlists(base, with_bjt, pdk=IHP_SG13G2, on_unknown="raise")


# ---------------------------------------------------------------------------
# Convenience builders and input coercion
# ---------------------------------------------------------------------------
def test_compare_graphs_accepts_prebuilt_graphs():
    g1, g2 = _g(OTA_CORE), _g(OTA_CORE)
    assert compare_graphs(g1, g2).equivalent


def test_boolean_shortcuts():
    assert graphs_equivalent(_g(OTA_CORE), _g(OTA_CORE))
    assert netlists_equivalent(OTA_CORE, OTA_CORE, pdk=IHP_SG13G2)
    assert not netlists_equivalent(
        OTA_CORE, OTA_CORE.replace("M4 out2 out1", "M4 out2 out2"), pdk=IHP_SG13G2
    )


def test_compare_netlists_accepts_paths_and_views():
    # path vs path
    assert compare_netlists(CASCODE_FLAT, CASCODE_FLAT, pdk=IHP_SG13G2).equivalent
    # mixed: a NetlistView vs a Path
    view = NetlistView.from_file(CASCODE_FLAT)
    assert compare_netlists(view, CASCODE_FLAT, pdk=IHP_SG13G2).equivalent


def test_unbuildable_input_raises():
    with pytest.raises(TypeError):
        compare_netlists(123, OTA_CORE)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# The returned mapping is an actual isomorphism witness, not just the right size
# ---------------------------------------------------------------------------
def test_returned_mapping_is_a_valid_isomorphism():
    # Use the all-MOSFET core (strict pins) so the witness can be checked pin-exact.
    renamed = _relabel(
        OTA_CORE,
        {"M1": "MQ", "M2": "MW", "M3": "ME", "M4": "MR", "M5": "MT",
         "out1": "a1", "out2": "a2", "tail": "tt", "vinp": "ip", "vinn": "in", "vbias": "bb"},
    )
    ga, gb = _g(OTA_CORE), _g(renamed)
    result = compare_graphs(ga, gb)
    assert result.equivalent

    # Applying the recovered net mapping to every component's wiring must reproduce the wiring of
    # its mapped counterpart — i.e. the mapping really is a connectivity-preserving bijection.
    assert len(set(result.net_mapping.values())) == len(result.net_mapping)
    for a_comp in ga.get_components():
        b_comp = gb._comp_map[result.component_mapping[a_comp.name]]
        assert type(a_comp) is type(b_comp)
        mapped = {pin: result.net_mapping[net] for pin, net in ga.connections(a_comp).items()}
        assert mapped == gb.connections(b_comp)


# ---------------------------------------------------------------------------
# Real fixtures: self-equivalent, and a single rewiring is caught
# ---------------------------------------------------------------------------
def test_real_cascode_fixture_self_equivalent():
    g = CircuitGraph.from_netlist(NetlistView.from_file(CASCODE_FLAT), pdk=IHP_SG13G2)
    assert compare_graphs(g, g).equivalent


def test_real_cascode_fixture_detects_single_rewire():
    text = CASCODE_FLAT.read_text()
    g_orig = CircuitGraph.from_netlist(NetlistView.from_string(text), pdk=IHP_SG13G2)

    # Flip one transistor's drain/source order on the first XM* device line.
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("XM1 "):
            parts = line.split()
            parts[1], parts[3] = parts[3], parts[1]  # swap drain <-> source nets
            lines[i] = " ".join(parts)
            break
    g_rewired = CircuitGraph.from_netlist(NetlistView.from_string("\n".join(lines)), pdk=IHP_SG13G2)

    result = compare_graphs(g_orig, g_rewired)
    assert isinstance(result, GraphComparison)
    assert not result.equivalent


def test_real_subckt_testbench_self_equivalent_and_detects_port_swap():
    # A flat testbench with a subckt instance (XOTA, 7 named ports) plus V/I/C sources — exercises
    # black-box subckt + source comparison on real data.
    text = OTA5T_TB.read_text()
    assert compare_netlists(text, text, pdk=IHP_SG13G2).equivalent

    # Swap two ports on the subckt-instance line (vdd-port net <-> vout-port net): a real rewiring.
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.lower().startswith("xota "):
            parts = line.split()
            parts[1], parts[2] = parts[2], parts[1]
            lines[i] = " ".join(parts)
            break
    assert not compare_netlists(text, "\n".join(lines), pdk=IHP_SG13G2).equivalent
