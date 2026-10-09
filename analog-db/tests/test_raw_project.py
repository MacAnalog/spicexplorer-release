"""The raw-targeting project_setup generator (`raw_project`): deck parsing + config shape."""

from __future__ import annotations

import pytest
import yaml

from spicexplorer_analog_db import cli, paths, pdks, raw_project

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
    assert raw_project.parse_deck_metrics(ac_deck) == [
        ("dcgain", "ac"),
        ("ugf", "ac"),
        ("pm", "ac"),
    ]


def test_parse_deck_metrics_native_noise_totals():
    # `.noise` emits inoise_total/onoise_total as NATIVE voltage vectors — not a meas, not a let —
    # so `print`ing them must still yield the v()-wrapped names RawRead sees in the written raw file.
    noise_deck = (
        ".control\n set filetype=ascii\n noise v(vout) Vinp dec 50 1k 100MEG\n"
        " print inoise_total onoise_total\n write\n quit\n.endc\n.end\n"
    )
    assert raw_project.parse_deck_metrics(noise_deck) == [
        ("v(inoise_total)", "noise"),
        ("v(onoise_total)", "noise"),
    ]


def test_parse_deck_metrics_native_total_with_derived_let():
    # the ldo `print onoise_total vn_out_rms` template: onoise_total is native (→ v()-wrapped),
    # while vn_out_rms is a derived let NOT in the registry, so it's dropped — the native
    # onoise_total already scores the bench (no double-count). (ngspice's integrated totals are
    # already V rms, so the let is a plain alias — see tests/test_noise_units.py.)
    deck = (
        ".control\n noise v(vout) Vdd dec 10 10 10meg\n let vn_out_rms = onoise_total\n"
        " print onoise_total vn_out_rms\n write\n quit\n.endc\n.end\n"
    )
    assert raw_project.parse_deck_metrics(deck) == [("v(onoise_total)", "noise")]


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
    assert (
        dut["r_top"].get("freeze")
        and dut["x_dut_xmp_m"].get("freeze")
        and dut["vref_val"].get("freeze")
    )
    assert "min_val" in dut["x_dut_xmp_w"] and "min_val" in dut["i_tail"]  # geometry/bias searched
    specs = {s["name"]: s for s in doc["optimizer_config"]["target_specs"]}
    # the DC-sweep + AC + OP metrics are all present with the right plot types
    assert specs["load_reg"]["sim_type"] == "dc" and specs["line_reg"]["sim_type"] == "dc"
    assert specs["zout_peak_db"]["sim_type"] == "ac"
    assert specs["v(vout_dc)"]["target"] == 1.2  # from datasheet default_conditions.vout


def test_generate_demo_lists_schematic_assets():
    # ldo_005 vendors the TI reference schematics — the demo YAML must declare
    # them (top-level assets.xschem, YAML-dir-relative, no traversal) so the
    # platform's example seeding can copy them into the project's xschem/.
    text = raw_project.generate_demo("ldo_005_buffered_ref", "gf180mcu")
    doc = yaml.safe_load(text)
    xs = doc["assets"]["xschem"]
    assert any(p.endswith("/ldo.sch") for p in xs)
    assert all(not p.startswith("/") and ".." not in p.split("/") for p in xs)


# ───────────────────────────── engine routing (SIM-D04) ─────────────────────────────
# The generator writes `simulator: ngspice` projects only. A PDK whose committed registry marker
# (`_shared/pdk/<pdk>.yaml` sim_engine) routes it to Spectre is refused BEFORE any deck walk or
# write, with a message that names the spicexplorer_spectre lane.


def _registry_with(monkeypatch, overrides: dict[str, dict]):
    """Patch `pdks.load_registry` so the named PDKs read the given registry dicts (others: real)."""
    real = pdks.load_registry
    monkeypatch.setattr(pdks, "load_registry", lambda name: overrides.get(name, real(name)))


def test_default_pdk_is_routed_too(monkeypatch):
    # pdk=None falls back to the circuit's first binding (ihp-sg13g2 for amp_001_5t); the refusal
    # applies to that resolved PDK, not only to an explicit --pdk. The marker is written " Spectre "
    # so the lane hint below also proves it is read case- and whitespace-insensitively: read
    # verbatim it would be an unknown engine, whose refusal names no lane.
    _registry_with(monkeypatch, {"ihp-sg13g2": {"sim_engine": " Spectre "}})
    for render in (
        lambda: raw_project.generate("amp_001_5t", None, GEN_DIR),
        lambda: raw_project.generate_demo("amp_001_5t"),
    ):
        with pytest.raises(raw_project.EngineNotNgspice) as exc:
            render()
        assert "amp_001_5t@ihp-sg13g2" in str(exc.value)
        assert "spicexplorer_spectre" in str(exc.value)


@pytest.mark.parametrize("marker", ["Spectre", "SPECTRE", " spectre\n"])
def test_spectre_marker_is_read_case_and_whitespace_insensitively(monkeypatch, marker):
    _registry_with(monkeypatch, {"ihp-sg13g2": {"sim_engine": marker}})
    with pytest.raises(raw_project.EngineNotNgspice) as exc:
        raw_project.generate("amp_001_5t", "ihp-sg13g2", GEN_DIR)
    assert "spicexplorer_spectre" in str(exc.value)  # the Spectre refusal, not the generic one


@pytest.mark.parametrize("marker", ["NGSPICE", "Ngspice", " ngspice "])
def test_ngspice_marker_is_read_case_and_whitespace_insensitively(monkeypatch, marker):
    # the other side of the same normalisation: a differently written ngspice marker is not refused
    _registry_with(monkeypatch, {"ihp-sg13g2": {"sim_engine": marker}})
    doc = yaml.safe_load(raw_project.generate("amp_001_5t", "ihp-sg13g2", GEN_DIR))["project"]
    assert doc["simulator"] == "ngspice"


@pytest.mark.parametrize(
    "registry",
    [{}, {"sim_engine": None}, {"sim_engine": "ngspice"}],
    ids=["no-marker", "null-marker", "ngspice"],
)
def test_ngspice_or_unmarked_registry_renders(monkeypatch, registry):
    # no marker = the open ngspice lane (the platform's library service reads it the same way)
    _registry_with(monkeypatch, {"ihp-sg13g2": registry})
    doc = yaml.safe_load(raw_project.generate("amp_001_5t", "ihp-sg13g2", GEN_DIR))["project"]
    assert doc["simulator"] == "ngspice"


def test_unknown_engine_is_refused_without_naming_the_spectre_lane(monkeypatch):
    _registry_with(monkeypatch, {"ihp-sg13g2": {"sim_engine": "xyce"}})
    with pytest.raises(raw_project.EngineNotNgspice) as exc:
        raw_project.generate("amp_001_5t", "ihp-sg13g2", GEN_DIR)
    assert "sim_engine: xyce" in str(exc.value)
    assert "spicexplorer_spectre" not in str(exc.value)


def test_unknown_pdk_names_its_missing_registry():
    # an unknown PDK has no marker to read: say so (relative path, no host path) instead of an
    # OS error or the misleading "only i_supply is scorable"
    with pytest.raises(
        ValueError, match=r"amp_001_5t@nosuchpdk: no PDK registry _shared/pdk/nosuchpdk\.yaml$"
    ):
        raw_project.generate("amp_001_5t", "nosuchpdk", GEN_DIR)


# ───────────────────────────── --out outside the DB root (FU-EXPORT-OUT) ─────────────────────────────


def test_cli_export_raw_project_writes_to_an_out_dir_outside_the_db(tmp_path, capsys):
    """An ``--out`` outside the DB root used to write the file, then raise on ``relative_to`` in
    the log line and count the circuit twice: "1 project(s) written, 1 skipped", rc 0."""
    out_dir = tmp_path / "elsewhere"
    assert not out_dir.resolve().is_relative_to(paths.db_root())
    rc = cli.main(
        [
            "export-raw-project",
            "--circuit",
            "amp_001_5t",
            "--pdk",
            "ihp-sg13g2",
            "--out",
            str(out_dir),
        ]
    )
    captured = capsys.readouterr()
    assert rc == 0
    assert f"  wrote {out_dir / 'amp_001_5t.yaml'}\n" in captured.out
    assert "1 project(s) written, 0 skipped" in captured.out
    assert captured.err == ""
    assert yaml.safe_load((out_dir / "amp_001_5t.yaml").read_text())["project"]["name"]


def test_cli_export_raw_project_logs_a_path_inside_the_db_relative_to_it(monkeypatch, capsys):
    """The default target sits inside the DB, and its log line stays DB-root-relative. The writer
    is stubbed, so nothing is written to the committed ``raw_optimize/generated/``."""
    monkeypatch.setattr(raw_project, "write", lambda cid, _pdk, out: out / f"{cid}.yaml")
    rc = cli.main(["export-raw-project", "--circuit", "amp_001_5t", "--pdk", "ihp-sg13g2"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "  wrote raw_optimize/generated/amp_001_5t.yaml\n" in out
    assert "1 project(s) written, 0 skipped" in out


def test_cli_export_raw_project_counts_a_failed_write_as_skipped_only(
    tmp_path, monkeypatch, capsys
):
    def refuse(cid, _pdk, _out):
        raise raw_project.EngineNotNgspice(f"{cid}: refused")

    monkeypatch.setattr(raw_project, "write", refuse)
    rc = cli.main(["export-raw-project", "--circuit", "amp_001_5t", "--out", str(tmp_path)])
    captured = capsys.readouterr()
    assert rc == 1
    assert "0 project(s) written, 1 skipped" in captured.out
    assert "wrote" not in captured.out
