"""PPA extraction: active gate area, metric mapping, rollup."""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import model, ppa


def test_parse_eng():
    assert ppa.parse_eng("0.5u") == pytest.approx(5e-7)
    assert ppa.parse_eng("300k") == pytest.approx(3e5)
    assert ppa.parse_eng("2") == 2.0
    assert ppa.parse_eng("10meg") == pytest.approx(1e7)
    assert ppa.parse_eng("w_in") is None


def test_expr_arithmetic():
    syms = {"w_x": 2.0, "m_x": 3.0}
    assert ppa._eval_expr("'w_x*1'", syms, "t") == 2.0
    assert ppa._eval_expr("'4*m_x'", syms, "t") == 12.0
    assert ppa._eval_expr("w_x", syms, "t") == 2.0
    assert ppa._eval_expr("0.5u", syms, "t") == pytest.approx(5e-7)
    with pytest.raises(ppa.PpaError):
        ppa._eval_expr("'nope*2'", syms, "t")


def test_area_5t_hand_computed():
    """ihp 5T (gm/ID re-size): input 2 x (10x10) + load 2 x (10x7) + tail (3.8x1) + ref (3.8x1) = 347.6 um2, 6 MOS."""
    rep = ppa.area_report(model.load_circuit("amp_001_5t"), "ihp-sg13g2")
    assert rep["mos_count"] == 6
    assert rep["active_gate_area_um2"] == pytest.approx(347.6)


def test_area_counts_m_multiplier_and_passives():
    """basic AnalogGym LDO (sky130, bare-um units): 24 MOS with m-arithmetic, 6.8p mim, 300k+100k."""
    rep = ppa.area_report(model.load_circuit("ldo_001_analoggym_basic"), "sky130")
    assert rep["mos_count"] == 24
    assert rep["c_total_f"] == pytest.approx(6.8e-12)
    assert rep["r_total_ohm"] == pytest.approx(4e5)
    assert rep["active_gate_area_um2"] > 100  # bare-um convention applied (not 1e-12 scale)


def test_area_every_verifiable_binding():
    for cid in model.list_circuit_ids():
        c = model.load_circuit(cid)
        if c.is_reference_only:
            continue
        for pdk in c.pdks:
            rep = ppa.area_report(c, pdk)
            if rep["mos_count"] == 0:
                # MOS-less by construction (behavioral macromodels, passive sense
                # dividers) — zero gate area is the truth, nothing to resolve
                assert rep["active_gate_area_um2"] == 0, (cid, pdk, rep)
                continue
            assert rep["active_gate_area_um2"] > 0, (cid, pdk, rep)


def test_metric_values_and_spec_verdicts():
    c = model.load_circuit("ldo_007_pmos")
    analyses = {
        "dc_op": {"status": "ok", "measures": {"vout_dc": 1.2, "i_supply": 2.1e-4}},
        "load_regulation": {"status": "ok", "measures": {"load_reg": 0.002}},
        "psrr": {"status": "sim_error"},
    }
    vals = ppa.metric_values(c, analyses)
    assert vals["v_out"]["value"] == 1.2 and vals["v_out"]["spec"] == "pass"
    assert vals["i_q"]["spec"] == "pass"  # spec max 2.5e-4
    assert "psrr_vdd_db" not in vals  # analysis errored -> omitted, not guessed


def test_ppa_rollup_direction_aware():
    c = model.load_circuit("ldo_007_pmos")
    corners = {
        "tt": {"i_q": {"value": 2.0e-4, "spec": "pass"}, "load_reg": {"value": 0.002, "spec": "pass"}},
        "ss": {"i_q": {"value": 2.4e-4, "spec": "pass"}, "load_reg": {"value": 0.004, "spec": "pass"}},
    }
    roll = ppa.ppa_rollup(c, corners, {"active_gate_area_um2": 123.0})
    assert roll["power_w"] == pytest.approx(2.4e-4 * 1.8)  # worst corner x typical VDD
    assert roll["performance"]["load_reg"] == pytest.approx(0.004)  # better: min -> worst = max
    assert roll["corners_run"] == ["ss", "tt"]
    assert roll["active_gate_area_um2"] == 123.0


def test_class_ppa_declared_for_both_classes():
    for class_id in ("amplifier", "ldo"):
        decl = ppa.class_ppa(class_id)
        assert decl.get("power", {}).get("metric")
        canon = set(model.load_class(class_id).get("canonical_metrics", []))
        assert decl["power"]["metric"] in canon
        for perf in decl["performance"]:
            assert perf["metric"] in canon, perf
