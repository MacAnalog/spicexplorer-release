"""Tests for the recursive netlist-driven active-area walk
(:mod:`spicexplorer_core.measurements.area`): the brace/eng ``.param`` resolver, the
device walk + coverage accounting on a self-contained inline deck, and — when the
analog-db submodule is present — the two demo decks (amp_029, amp_008) where a
hand-authored recipe previously undercounted the silicon."""

from __future__ import annotations

import pytest
from spicexplorer_core.measurements import area
from spicexplorer_core.paths import project_root

# ── the .param resolver (brace expressions, ties, ratios, eng literals) ──────────


def test_resolver_plain_eng_and_number():
    assert area.resolve_param_value("2u", {}) == pytest.approx(2e-6)
    assert area.resolve_param_value("4", {}) == pytest.approx(4.0)
    assert area.resolve_param_value("1.5e-6", {}) == pytest.approx(1.5e-6)
    assert area.resolve_param_value(0.5e-6, {}) == pytest.approx(0.5e-6)  # already numeric


def test_resolver_follows_alias_and_ratio():
    params = {
        "x_dut_xm1_w": "2u",
        "x_dut_xm2_w": "{x_dut_xm1_w}",
        "x_dut_xm7_m": "4",
        "x_dut_xm19_m": "{x_dut_xm14_m*8}",
        "x_dut_xm14_m": "4",
    }
    assert area.resolve_param_value("x_dut_xm2_w", params) == pytest.approx(2e-6)
    assert area.resolve_param_value("{x_dut_xm7_m*1}", params) == pytest.approx(4.0)
    assert area.resolve_param_value("x_dut_xm19_m", params) == pytest.approx(32.0)  # 4*8


def test_resolver_eng_literal_inside_expression():
    assert area.resolve_param_value("{2u*3}", {}) == pytest.approx(6e-6)


def test_resolver_case_insensitive():
    assert area.resolve_param_value("X_DUT_W", {"x_dut_w": "3u"}) == pytest.approx(3e-6)


def test_resolver_unresolvable_returns_none():
    assert area.resolve_param_value("{missing}", {}) is None
    assert area.resolve_param_value("{a}", {"a": "{b}", "b": "{a}"}) is None  # cyclic


def test_resolver_reads_netlist_tokens_with_spice_semantics():
    """A deck token is SPICE, not the YAML DSL (OPT-04): `M` is milli and every suffix is
    case-insensitive. The DSL parser read `1M` as mega and could not read `2U` or `10K` at all."""
    assert area.resolve_param_value("1M", {}) == pytest.approx(1e-3)
    assert area.resolve_param_value("2U", {}) == pytest.approx(2e-6)
    assert area.resolve_param_value("10K", {}) == pytest.approx(1e4)
    assert area.resolve_param_value("1meg", {}) == pytest.approx(1e6)


def test_resolver_eng_literals_inside_expressions_are_spice_too():
    assert area.resolve_param_value("{2U*3}", {}) == pytest.approx(6e-6)
    assert area.resolve_param_value("{1M*2}", {}) == pytest.approx(2e-3)
    assert area.resolve_param_value("{w*1Meg}", {"w": "1u"}) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "token,expected",
    [
        ("{.5u*2}", 1e-6),  # a literal with no leading digit
        ("{2mil*1}", 50.8e-6),  # ngspice's thousandth of an inch, not milli
        ("{1g*2}", 2e9),  # giga — lowercase, and `1G` is the same number
        ("{1G*2}", 2e9),
        ("{1T*2}", 2e12),  # tera, any case (the DSL parser refuses `1T`)
        ("{3a*1}", 3e-18),  # atto
        ("{1.5E-1u*2}", 3e-7),  # exponent AND scale factor on one literal
        ("{1MEG/4}", 2.5e5),
    ],
)
def test_resolver_eng_literals_inside_expressions_cover_the_whole_table(token, expected):
    """OPT-04: every ngspice scale factor, spelled any way the bare-token parser accepts it, also
    converts inside an expression — the pre-pass pattern is not a second, narrower table."""
    assert area.resolve_param_value(token, {}) == pytest.approx(expected, rel=1e-12)


def test_resolver_leaves_identifiers_that_end_in_a_suffix_alone():
    # `x1u` is a parameter name, not `x` followed by the literal `1u`.
    assert area.resolve_param_value("{x1u*2}", {"x1u": "3"}) == pytest.approx(6.0)
    assert area.resolve_param_value("{w1*2u}", {"w1": "3"}) == pytest.approx(6e-6)


@pytest.mark.parametrize(
    "token,expected",
    [
        ("2e-6+1e-6", 3e-6),
        ("{2e-6+1e-6}", 3e-6),
        ("{3-1}", 2.0),
    ],
)
def test_resolver_number_only_arithmetic_is_evaluated_not_refused(token, expected):
    """`spice_number` RAISES on text made only of number characters that is not one number, and
    unbraced arithmetic such as `2e-6+1e-6` is exactly that. The resolver must hand it on to the
    expression evaluator — neither let the raise escape nor give up on the token."""
    assert area.resolve_param_value(token, {}) == pytest.approx(expected)


def test_resolver_malformed_number_is_unresolved_with_a_warning():
    """A typo'd width (`1.2.3`) is neither a number nor an expression: `None` plus a note, never
    an exception out of the walk and never a silently wrong value."""
    resolver = area._ParamResolver({})
    assert resolver.resolve("1.2.3") is None
    assert any("1.2.3" in w for w in resolver.warnings)


# ── the recursive walk on a self-contained inline deck (no analog-db needed) ─────

_MINI_DECK = """* mini area test deck
.param w1=2u l1=0.5u m1=1
.param w1b={w1}
.param m2={m1*4}
XDUT d g s 0 mini
.subckt mini d g s b
XM1 d g s b nmos_model w=w1 l=l1 m=m1
XM2 d g s b pmos_model w=w1b l=l1 m=m2
R1 d s 1k
C1 g s 10f
.ends
.end
"""


def test_walk_inline_deck_sums_transistors_only():
    rep = area.active_area_report(_MINI_DECK, scale=1e12)
    # XM1 = 2u*0.5u*1 = 1 µm²; XM2 = {w1}=2u * 0.5u * {m1*4}=4 = 4 µm² → total 5 µm²
    assert rep["active_area"] == pytest.approx(5.0)
    assert rep["transistor_count"] == 2
    assert rep["coverage"]["complete"] is True
    # every non-MOS instance is still accounted for in `others` (R1, C1, and the container)
    other_refs = {o["ref"] for o in rep["others"]}
    assert {"R1", "C1", "XDUT"} <= other_refs
    # accounting is complete: counted + others == every instance walked
    assert rep["coverage"]["total_instances"] == len(rep["devices"]) + len(rep["others"])
    assert rep["coverage"]["transistors_unresolved"] == 0


def test_walk_overrides_flow_through_ties():
    rep = area.active_area_report(_MINI_DECK, overrides={"w1": "4u"}, scale=1e12)
    # XM1 = 4u*0.5u*1 = 2 µm²; XM2 tie w1b={w1}=4u * 0.5u * 4 = 8 µm² → total 10 µm²
    assert rep["active_area"] == pytest.approx(10.0)


def test_walk_reports_passive_geometry_separately():
    # a resistor exposing w/l geometry is reported in `others` with an area — never in the total
    deck = _MINI_DECK.replace("R1 d s 1k", "XR1 d s res_model w=1u l=2u")
    rep = area.active_area_report(deck, scale=1e12)
    assert rep["active_area"] == pytest.approx(5.0)  # unchanged; passive not in the transistor sum
    xr1 = next(o for o in rep["others"] if o["ref"] == "XR1")
    assert xr1["area"] == pytest.approx(1e-6 * 2e-6 * 1e12)  # reported, separate bucket


def test_walk_reads_upper_case_and_milli_geometry():
    # The OPT-04 probe deck: on the DSL parser M1/M3 went unresolved (`2U`) and M2's `l=1M`
    # read as a million metres, so the partial "total" was 1e12 µm² from one device.
    deck = """* upper-case suffixes
.param w1=2U l1=1M
M1 d g s b nmos_model w=w1 l=l1
M2 d g s b nmos_model w=1u l=1M
M3 d g s b nmos_model w=2U l=0.5u
.end
"""
    rep = area.active_area_report(deck, scale=1e12)
    assert rep["coverage"]["complete"] is True
    assert rep["transistor_count"] == 3
    # 2u*1m + 1u*1m + 2u*0.5u = 2000 + 1000 + 1 µm²
    assert rep["active_area"] == pytest.approx(3001.0)


def test_walk_with_a_malformed_width_is_incomplete_not_a_crash():
    deck = """* one transistor carries a typo'd width
M1 d g s b nmos_model w=2u l=1u
M2 d g s b nmos_model w=1.2.3 l=1u
.end
"""
    rep = area.active_area_report(deck, scale=1e12)
    assert rep["coverage"]["complete"] is False
    assert rep["coverage"]["transistors_unresolved"] == 1
    assert rep["active_area"] == pytest.approx(2.0)  # M1 only — the caller must refuse it
    assert any("M2" in w for w in rep["warnings"])


# ── the two demo decks (gated on the analog-db submodule) ────────────────────────

_RAW = project_root() / "examples/analog-db/raw"
_AMP029 = _RAW / "amp_029_two_stage_miller_comp/ihp-sg13g2/dc_op.spice"
_AMP008 = _RAW / "amp_008_leung_nmcf/ihp-sg13g2/dc_op.spice"


@pytest.mark.skipif(not _AMP029.exists(), reason="analog-db submodule (amp_029) not present")
def test_amp029_counts_all_ten_transistors_including_xm9_xm10():
    rep = area.active_area_report(_AMP029, scale=1e12)
    assert rep["transistor_count"] == 10
    assert rep["coverage"]["complete"] is True
    refs = {d["ref"] for d in rep["devices"] if d["counted"]}
    # XM9/XM10 (the voutn 2nd-stage twins) were the two the hand-list omitted.
    assert {"XM9", "XM10"} <= refs
    # default sizing: Σ over all 10 devices = 58.0 µm²
    assert rep["active_area"] == pytest.approx(58.0, rel=1e-3)


@pytest.mark.skipif(not _AMP008.exists(), reason="analog-db submodule (amp_008) not present")
def test_amp008_counts_all_24_with_resolved_multipliers():
    rep = area.active_area_report(_AMP008, scale=1e12)
    assert rep["transistor_count"] == 24
    assert rep["coverage"]["complete"] is True
    by_ref = {d["ref"]: d for d in rep["devices"]}
    # multipliers resolved from the deck's `.param` ties: xm19_m = {xm14_m*8} = 32
    assert by_ref["XM19"]["m"] == pytest.approx(32.0)
    assert by_ref["XM12"]["m"] == pytest.approx(16.0)  # {xm14_m*4}
    assert by_ref["XM7"]["m"] == pytest.approx(4.0)
    # true default silicon ≈ 646 µm² after the all-spec gm/ID re-sizing of the corpus
    # (the old 7-group hand list saw ~28 µm², ~23× under; the pre-resize walk read ~236).
    assert rep["active_area"] == pytest.approx(646.07, rel=1e-3)
