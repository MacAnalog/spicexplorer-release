"""The raw-targeting project_setup generator (`raw_project`): deck parsing + config shape."""

from __future__ import annotations

import yaml

from spicexplorer_analog_db import paths, raw_project

# the real committed location (generate() only renders text — no writes — so this is safe)
GEN_DIR = paths.db_root() / "raw_optimize" / "generated"


# ───────────────────────────── deck parsing ─────────────────────────────


def test_saved_name_naming_rule():
    # a current-typed let -> i(name); a voltage-typed let -> v(name); dimensionless -> bare
    assert raw_project._saved_name("i_supply", "abs(i(Vdd))") == "i(i_supply)"
    assert raw_project._saved_name("vout_dc", "v(vout)") == "v(vout_dc)"
    assert raw_project._saved_name("load_reg", "vout_max - vout_min") == "load_reg"


def test_parse_deck_metrics_op_and_ac():
    op_deck = (
        ".control\n set filetype=ascii\n op\n let i_supply = abs(i(Vdd))\n"
        " let vout_dc = v(vout)\n print i_supply vout_dc\n write\n quit\n.endc\n.end\n"
    )
    assert raw_project.parse_deck_metrics(op_deck) == [("i(i_supply)", "op"), ("v(vout_dc)", "op")]

    ac_deck = (
        ".control\n ac dec 101 1k 100MEG\n meas ac dcgain FIND vdb(vout) AT=1k\n"
        " meas ac ugf WHEN vdb(vout)=0 FALL=1\n meas ac pm FIND ph WHEN vdb(vout)=0\n"
        " write\n quit\n.endc\n.end\n"
    )
    assert raw_project.parse_deck_metrics(ac_deck) == [("dcgain", "ac"), ("ugf", "ac"), ("pm", "ac")]


def test_parse_deck_metrics_dc_sweep_keeps_only_whitelisted():
    # vout_max/vout_min are intermediate meas results (not whitelisted) → dropped; load_reg kept.
    dc_deck = (
        ".control\n dc Iload 0 10m 0.5m\n meas dc vout_max MAX v(vout)\n"
        " meas dc vout_min MIN v(vout)\n let load_reg = vout_max - vout_min\n"
        " print load_reg\n write\n quit\n.endc\n.end\n"
    )
    assert raw_project.parse_deck_metrics(dc_deck) == [("load_reg", "dc")]


# ───────────────────────────── generated config shape ─────────────────────────────


def test_generate_amp_001_5t_config():
    text = raw_project.generate("amp_001_5t", "ihp-sg13g2", GEN_DIR)
    doc = yaml.safe_load(text)["project"]
    assert doc["ws_root"] and doc["outdir"].startswith("raw_optimize/generated/_runs")
    # dut_params come from sizing.yaml (the FREE atomic symbols); W/L knobs are searched
    # (have bounds), the frozen integer finger counts are frozen at their defaults
    dut = {p["name"]: p for p in doc["dut_params"]}
    assert "x_dut_xm1_w" in dut and "min_val" in dut["x_dut_xm1_w"]
    assert dut["x_dut_xm1_m"]["freeze"] is True and dut["x_dut_xm1_m"]["val"] == 1
    # testbenches point at the committed raw decks
    tbs = {tb["name"]: tb for tb in doc["testbenches"]}
    assert tbs["ac_open_loop"]["netlist"] == "raw/amp_001_5t/ihp-sg13g2/ac_open_loop.spice"
    # specs: AC meas results are bare, the dc_op `let i_supply` is the current-typed i(i_supply)
    specs = {s["name"]: s for s in doc["optimizer_config"]["target_specs"]}
    assert {"dcgain", "ugf", "pm", "i(i_supply)"} <= set(specs)
    assert specs["dcgain"]["sim_type"] == "ac" and specs["i(i_supply)"]["sim_type"] == "op"
    assert specs["i(i_supply)"]["goal"] == "minimize"


def test_generate_ldo_pulls_vout_target_and_freezes_passives():
    doc = yaml.safe_load(raw_project.generate("ldo_007_pmos", "ihp-sg13g2", GEN_DIR))["project"]
    dut = {p["name"]: p for p in doc["dut_params"]}
    # the divider + reference + integer multiplier are frozen (hold the regulation target / bias)
    assert dut["r_top"].get("freeze") and dut["x_dut_xmp_m"].get("freeze") and dut["vref_val"].get("freeze")
    assert "min_val" in dut["x_dut_xmp_w"] and "min_val" in dut["i_tail"]  # geometry/bias searched
    specs = {s["name"]: s for s in doc["optimizer_config"]["target_specs"]}
    # the DC-sweep + AC + OP metrics are all present with the right plot types
    assert specs["load_reg"]["sim_type"] == "dc" and specs["line_reg"]["sim_type"] == "dc"
    assert specs["zout_peak_db"]["sim_type"] == "ac"
    assert specs["v(vout_dc)"]["target"] == 1.2   # from datasheet default_conditions.vout
