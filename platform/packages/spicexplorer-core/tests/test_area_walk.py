"""Tests for the recursive netlist-driven active-area walk
(:mod:`spicexplorer_core.measurements.area`): the brace/eng ``.param`` resolver, the
device walk + coverage accounting on a self-contained inline deck, and — when the
analog-db submodule is present — the two demo decks (amp_020, amp_008) where a
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
    params = {"x_dut_xm1_w": "2u", "x_dut_xm2_w": "{x_dut_xm1_w}",
              "x_dut_xm7_m": "4", "x_dut_xm19_m": "{x_dut_xm14_m*8}", "x_dut_xm14_m": "4"}
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


# ── the two demo decks (gated on the analog-db submodule) ────────────────────────

_RAW = project_root() / "examples/analog-db/raw"
_AMP020 = _RAW / "amp_020_two_stage_miller_cmfb/ihp-sg13g2/dc_op.spice"
_AMP008 = _RAW / "amp_008_leung_nmcf/ihp-sg13g2/dc_op.spice"


@pytest.mark.skipif(not _AMP020.exists(), reason="analog-db submodule (amp_020) not present")
def test_amp020_counts_all_ten_transistors_including_xm9_xm10():
    rep = area.active_area_report(_AMP020, scale=1e12)
    assert rep["transistor_count"] == 10
    assert rep["coverage"]["complete"] is True
    refs = {d["ref"] for d in rep["devices"] if d["counted"]}
    # XM9/XM10 (the voutn 2nd-stage twins) were the two the hand-list omitted.
    assert {"XM9", "XM10"} <= refs
    # default sizing: Σ over all 10 devices ≈ 20.8 µm²
    assert rep["active_area"] == pytest.approx(20.8, rel=1e-3)


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
    # true default silicon ≈ 236 µm² — the old 7-group hand list saw ~28 µm² (~10× under).
    assert rep["active_area"] == pytest.approx(236.0, rel=1e-3)
