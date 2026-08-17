"""Offline tests — no klayout executable, no PDK, no kpex needed."""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_signoff import DrcResult, FlowResult, probe, run_flow
from spicexplorer_signoff.drc import parse_lyrdb
from spicexplorer_signoff.pdk import for_pdk
from spicexplorer_signoff.pex import _num, summarize_parasitics
from spicexplorer_signoff.postlayout import (
    deltas,
    extract_subckt,
    prep_pex_subckt,
    splice_subckt,
    to_lvs_reference,
)
from spicexplorer_signoff.sensitivity import (
    inject_caps,
    inject_isource,
    inject_resistor,
    inject_vsource,
    scale_param,
    sweep,
)

FIX = Path(__file__).parent / "fixtures"


def test_probe_shape():
    p = probe("ihp-sg13g2")
    d = p.to_dict()
    assert {"pdk_ok", "drc_ok", "lvs_ok", "pex_ok", "klayout", "kpex"} <= set(d)
    assert isinstance(p.drc_ok, bool)


def test_for_pdk_unknown():
    with pytest.raises(ValueError):
        for_pdk("nope-1um")


def test_parse_lyrdb_counts_and_locations():
    v = parse_lyrdb(FIX / "mini.lyrdb")
    assert [(x.rule, x.count) for x in v] == [("M1.a", 2), ("V1.a", 1)]
    assert v[0].locations[0] == (1.5, 2.25)


def test_si_numbers():
    assert _num("62.1879a") == pytest.approx(62.1879e-18)
    assert _num("1.5f") == pytest.approx(1.5e-15)
    assert _num("3meg") == 3e6
    assert _num("x") is None


def test_summarize_parasitics():
    n_c, n_r, per, coup = summarize_parasitics(FIX / "mini_pex.spice")
    assert (n_c, n_r) == (4, 1)
    assert per["$17"] == pytest.approx(0.2775, abs=1e-3)  # 62.19a + 215.3a
    assert per["vout"] == pytest.approx(1.5)  # to ground counts once
    assert coup["vinn|vinp"] == pytest.approx(0.0347822)
    assert "0" not in per


def test_prep_pex_subckt_rewrites_M_cards_and_renames():
    t = prep_pex_subckt(FIX / "mini_pex.spice", "ota", rename="ota_pex")
    assert "\nXM1 outm" in t and "\nXM2 vout" in t
    assert ".subckt ota_pex vdd" in t and ".ends ota_pex" in t
    assert "\n+ ps=1u" in t  # continuation kept


def test_extract_and_splice_subckt():
    core = (FIX / "core.sp").read_text()
    blk, pins = extract_subckt(core, "lpf_core")
    assert pins == ["vinp", "vinn", "vout_1", "vout_2", "vdd", "vss", "ibias"]
    deck = "* bench\n" + core + "\nX1 a b c d e f g lpf_core\n.end\n"
    new = core.replace("xr1 n1 n1 vss vss", "xr1 n1 n1 vss vss").replace("w=4u", "w=5u")
    out = splice_subckt(deck, new, "lpf_core")
    assert "w=5u" in out and out.count(".subckt lpf_core") == 1 and "X1 a b" in out
    bad = core.replace("vout_2 vdd", "vdd vout_2")
    with pytest.raises(ValueError):
        splice_subckt(deck, bad, "lpf_core")


def test_deltas():
    d = deltas({"fc": 250.0, "irn": 30.0, "s": "x"}, {"fc": 245.0, "irn": 30.0})  # type: ignore[arg-type]
    assert d["fc"]["delta"] == -5.0 and d["fc"]["rel"] == pytest.approx(-0.02)
    assert d["irn"]["delta"] == 0.0 and "s" not in d


def test_inject_caps_before_ends():
    t = inject_caps(
        FIX / "core.sp", "lpf_core", [("vout_1", "0", 1e-15), ("vout_1", "vout_2", 2e-15)]
    )
    body = t.split(".ends")[0]
    assert "Ccinj0 vout_1 0 1e-15" in body and "Ccinj1 vout_1 vout_2 2e-15" in body


def test_inject_resistor_splits_net():
    t = inject_resistor(FIX / "core.sp", "lpf_core", "n1", 1e3, at_devices=["xr1"])
    assert "xr1 n1_r n1_r vss vss" in t
    assert "xm1a n1 vinp" in t  # other pins untouched
    assert "Rinj_n1 n1 n1_r 1000" in t


def test_scale_param():
    t = scale_param(FIX / "core.sp", "lpf_core", "xm1b", "w", factor=1.1)
    assert "w=1.76e-05" in t and "xm1a n1 vinp vdd vdd sg13_hv_pmos w=16u" in t
    with pytest.raises(KeyError):
        scale_param(FIX / "core.sp", "lpf_core", "xm9", "w", 2)


def test_sweep_uses_callable_measure():
    calls: list[str] = []

    def measure(text: str) -> dict[str, float]:
        calls.append(text)
        c = text.count("Ccinj")
        return {"fc": 250.0 - 0.5 * c, "irn": 30.0}

    base, rows = sweep(
        FIX / "core.sp",
        "lpf_core",
        measure,
        nets=["vout_1"],
        pairs=[("vout_1", "vout_2")],
        c_ff=(1.0, 10.0),
    )
    assert base == {"fc": 250.0, "irn": 30.0}
    kinds = [(r.kind, r.target, r.unit) for r in rows]
    assert ("c_gnd", "vout_1", "1fF") in kinds and ("c_onesided", "vout_1|vout_2", "10fF") in kinds
    r = rows[0]
    assert r.delta["fc"] == -0.5 and r.per_unit["fc"] == -0.5 and r.to_dict()["kind"] == "c_gnd"
    assert len(calls) == 1 + len(rows)


def test_run_flow_build_failure_is_a_verdict(tmp_path):
    def boom(_p):
        raise RuntimeError("no gdsfactory here")

    r = run_flow(boom, {}, netlist=tmp_path / "x.sp", cell="c", run_dir=tmp_path)
    assert isinstance(r, FlowResult) and r.stage_failed == "build" and "no gdsfactory" in r.error
    assert r.to_dict()["ok"] is False


def test_run_flow_missing_gds_yields_drc_verdict(tmp_path):
    def fake(_p):
        return tmp_path / "missing.gds"

    r = run_flow(fake, {}, netlist=tmp_path / "x.sp", cell="c", run_dir=tmp_path)
    assert r.stage_failed == "drc" and isinstance(r.drc, DrcResult) and not r.drc.passed


def test_to_lvs_reference_translates_x_cards():
    t = to_lvs_reference(FIX / "core.sp", "lpf_core", cell="lpf_top")
    assert ".subckt lpf_top vinp vinn" in t and t.rstrip().endswith(".ends lpf_top")
    assert "Mm1a n1 vinp vdd vdd sg13_hv_pmos w=16u l=10u" in t  # ng dropped
    assert "Mr1 n1 n1 vss vss sg13_hv_nmos w=4u l=15u" in t
    assert "Cc1 vout_1 vout_2 cap_cmim w=40u l=40u m=2" in t
    core = (FIX / "core.sp").read_text().replace("w=4u l=15u", "w=4u l=15u m=4")
    assert "Mr1 n1 n1 vss vss sg13_hv_nmos w=16u l=15u" in to_lvs_reference(core, "lpf_core")
    assert "w=4u l=15u m=4" in to_lvs_reference(core, "lpf_core", combine_m=False)


def test_inject_vsource_and_isource():
    t = inject_vsource(FIX / "core.sp", "lpf_core", "xm1b", 1e-3, pin="g")
    assert (
        "xm1b n2 vinn_xm1b_v vdd vdd sg13_hv_pmos" in t
        and "Vinj_xm1b vinn_xm1b_v vinn dc 0.001" in t
    )
    t2 = inject_isource(FIX / "core.sp", "lpf_core", {"n1": 5e-12})
    assert "Iiinj_n1 0 n1 dc 5e-12" in t2.split(".ends")[0]


def test_sweep_balanced_leak_and_vpin_rows():
    def measure(text):
        return {
            "fc": 250.0 - 0.1 * text.count("Ccinj") - 2.0 * text.count("Vinj") - text.count("Iiinj")
        }

    _, rows = sweep(
        FIX / "core.sp",
        "lpf_core",
        measure,
        pairs=[("vout_1", "vout_2")],
        c_ff=(1.0,),
        i_nets=[("n1", 2e-12)],
        v_pins=[("xm1a", "g", 1e-3)],
    )
    kinds = {(r.kind, r.unit) for r in rows}
    assert (
        ("c_balanced", "1fF") in kinds and ("i_leak", "2pA") in kinds and ("v_pin", "1mV") in kinds
    )
    bal = next(r for r in rows if r.kind == "c_balanced")
    assert bal.delta["fc"] == pytest.approx(-0.2)
    vp = next(r for r in rows if r.kind == "v_pin")
    assert vp.per_unit["fc"] == pytest.approx(-2.0)


def test_strip_cards_and_strip_mim(tmp_path):
    from spicexplorer_signoff.pex import strip_cards, strip_mim_for_pex

    t = ".subckt x a b\nM1 a b c d m w=1u\nCc1 a b cap_cmim w=1u l=1u m=1\n.ends\n"
    assert "Cc1" not in strip_cards(t) and "M1 a b" in strip_cards(t)
    pytest.importorskip("klayout.db")
    import klayout.db as db

    ly = db.Layout()
    top = ly.create_cell("t")
    top.shapes(ly.layer(36, 0)).insert(db.DBox(0, 0, 10, 10))  # MIM
    top.shapes(ly.layer(129, 0)).insert(db.DBox(1, 1, 2, 2))  # Vmim
    top.shapes(ly.layer(126, 0)).insert(db.DBox(0.4, 0.4, 9.6, 9.6))  # top plate
    top.shapes(ly.layer(126, 0)).insert(db.DBox(9.0, 4, 20, 6))  # stub leaving the plate
    g = tmp_path / "a.gds"
    ly.write(str(g))
    out = strip_mim_for_pex(g, tmp_path / "b.gds")
    l2 = db.Layout()
    l2.read(str(out))
    t2 = l2.top_cell()
    assert t2.shapes(l2.layer(36, 0)).size() == 0 and t2.shapes(l2.layer(129, 0)).size() == 0
    tm = db.Region(t2.begin_shapes_rec(l2.layer(126, 0)))
    assert (
        tm.bbox().left > 10000 - 1 and tm.count() == 1
    )  # only the stub beyond the MIM+margin survives
