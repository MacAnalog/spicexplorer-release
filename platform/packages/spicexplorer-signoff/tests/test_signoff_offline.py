"""Offline tests — no klayout executable, no PDK, no kpex needed."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from spicexplorer_signoff import DrcResult, FlowResult, LvsResult, probe, run_flow
from spicexplorer_signoff.drc import parse_lyrdb
from spicexplorer_signoff.pdk import PdkPaths, for_pdk
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


def test_summarize_parasitics_skips_a_self_loop_card():
    """LAY-D2: `Cext_51 sub sub 23.0904f` (kpex emits one per PAM-4 cell) used to be added to
    `sub` TWICE and reported as a `sub|sub` coupling; a C with both terminals on one net is
    electrically nothing, so it is neither a card nor a sum nor a pair."""
    n_c, _, per, coup = summarize_parasitics(FIX / "kpex_ground_aliases.spice")
    assert n_c == 9  # ten C cards, the self-loop is not one of them
    assert per["sub"] == pytest.approx(2.5)  # only its C to outp (was 2.5 + 2 x 23.09)
    assert not any(a == b for a, b in (k.split("|") for k in coup)), coup


def test_summarize_parasitics_ground_aliases_are_one_case_insensitive_set():
    """LAY-D3: every ground alias (0 / gnd / vss / kpex's substrate node vsubs, any case) is left
    out of BOTH the per-net sums and the coupling pairs — `VSUBS|inp` and `inp|vss` used to be
    reported as couplings, and `VSUBS` / `Vss` as signal nets."""
    _, _, per, coup = summarize_parasitics(FIX / "kpex_ground_aliases.spice")
    assert set(per) == {"$19", "$6", "inp", "outp", "sub"}
    assert per["inp"] == pytest.approx(0.5 + 0.0160676 + 0.895995)  # its ground C still counts
    assert per["outp"] == pytest.approx(2.5 + 0.5 + 1.0 + 0.25)
    assert per["$6"] == pytest.approx(1.33716 + 0.1)
    assert coup == pytest.approx({"$19|$6": 1.33716, "outp|sub": 2.5, "inp|outp": 0.5})


def test_summarize_parasitics_extra_ground_nets():
    """A substrate that carries a PIN name (`sub`) is ground only when the caller says so."""
    from spicexplorer_signoff.pex import GROUND_NETS

    _, _, per, coup = summarize_parasitics(FIX / "kpex_ground_aliases.spice", ground_nets=("SUB",))
    assert "sub" not in per and "outp|sub" not in coup
    assert per["outp"] == pytest.approx(4.25)  # its C to sub is now C to ground, still counted
    assert GROUND_NETS == {"0", "gnd", "vss", "vsubs"}


def test_summarize_parasitics_extra_ground_nets_add_to_the_default_aliases():
    """`ground_nets=` EXTENDS the default aliases, it does not replace them: with `sub` declared
    ground, VSUBS / vss / GND / Vss / 0 are still ground — no per-net sum, no coupling pair."""
    _, _, per, coup = summarize_parasitics(FIX / "kpex_ground_aliases.spice", ground_nets=["sub"])
    assert set(per) == {"$19", "$6", "inp", "outp"}
    assert coup == pytest.approx({"$19|$6": 1.33716, "inp|outp": 0.5})


def test_summarize_parasitics_ground_nets_is_idempotent_and_keyword_only():
    """Naming a net that is already ground (any case) or one the netlist does not carry changes
    nothing, any iterable works (a one-shot generator here), and `ground_nets` is keyword-only so
    the positional call of every existing caller cannot be taken for it."""
    base = summarize_parasitics(FIX / "kpex_ground_aliases.spice")
    again = summarize_parasitics(
        FIX / "kpex_ground_aliases.spice",
        ground_nets=(n for n in ("GND", "Vsubs", "0", "no_such_net")),
    )
    assert again == base
    with pytest.raises(TypeError):
        summarize_parasitics(FIX / "kpex_ground_aliases.spice", ("sub",))  # type: ignore[misc]


def test_summarize_parasitics_ground_only_cards_and_self_loops_on_ground(tmp_path):
    """A self-loop on a ground alias or on a signal net is skipped (not in n_C); a card between two
    ground aliases IS a card (n_C) but lands in no sum and no pair; R cards are counted as before;
    a netlist with no cards is all zeros."""
    net = tmp_path / "c_pex.spice"
    net.write_text(
        ".subckt c a b vss\n"
        "C1 a b 1f\n"
        "C2 vss vss 5f\n"  # self-loop on ground
        "C3 VSUBS 0 2f\n"  # ground to ground: a card, but no net and no pair
        "C4 a a 9f\n"  # self-loop on a signal net
        "C5 b GND 0.5f\n"
        "R1 a b 10\n"
        ".ends c\n"
    )
    n_c, n_r, per, coup = summarize_parasitics(net)
    assert (n_c, n_r) == (3, 1)  # C1, C3, C5
    assert per == pytest.approx({"a": 1.0, "b": 1.5})
    assert coup == pytest.approx({"a|b": 1.0})
    empty = tmp_path / "empty.spice"
    empty.write_text(".subckt c a\n.ends c\n")
    assert summarize_parasitics(empty) == (0, 0, {}, {})


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


# LAY-D7: an unsupported PDK is a structured `available=False` verdict, not a ValueError that
# crashes `run_flow` (`for_pdk` itself still raises — see test_for_pdk_unknown).
def test_run_drc_unknown_pdk_is_an_unavailable_verdict(tmp_path):
    from spicexplorer_signoff.drc import run_drc

    r = run_drc(tmp_path / "missing.gds", "c", tmp_path / "drc", pdk="nope-1um")
    assert isinstance(r, DrcResult) and not r.available and not r.passed
    assert "unknown PDK 'nope-1um'" in r.reason


def test_run_lvs_unknown_pdk_is_an_unavailable_verdict(tmp_path):
    from spicexplorer_signoff.lvs import run_lvs

    r = run_lvs(tmp_path / "missing.gds", tmp_path / "x.sp", "c", tmp_path / "lvs", pdk="nope-1um")
    assert isinstance(r, LvsResult) and not r.available and not r.passed
    assert "unknown PDK 'nope-1um'" in r.reason


def test_run_flow_unknown_pdk_yields_a_drc_verdict(tmp_path):
    (tmp_path / "c.gds").write_bytes(b"")
    r = run_flow(
        lambda _p: tmp_path / "c.gds",
        {},
        netlist=tmp_path / "x.sp",
        cell="c",
        run_dir=tmp_path / "run",
        pdk="nope-1um",
    )
    assert r.stage_failed == "drc" and r.drc is not None and not r.drc.available
    assert "unknown PDK" in r.error


def test_run_flow_unknown_pdk_with_continue_on_fail_gets_an_lvs_verdict_too(tmp_path):
    """With continue_on_fail the flow goes past DRC, so run_lvs meets the unknown PDK as well; that
    must be a second structured verdict, not the ValueError that used to escape `run_flow`."""
    import json

    (tmp_path / "c.gds").write_bytes(b"")
    r = run_flow(
        lambda _p: tmp_path / "c.gds",
        {},
        netlist=tmp_path / "x.sp",
        cell="c",
        run_dir=tmp_path / "run",
        pdk="nope-1um",
        do_pex=False,
        continue_on_fail=True,
    )
    assert r.stage_failed == "drc" and not r.ok
    assert r.drc is not None and not r.drc.available and "unknown PDK 'nope-1um'" in r.drc.reason
    assert r.lvs is not None and not r.lvs.available and not r.lvs.passed
    assert "unknown PDK 'nope-1um'" in r.lvs.reason
    assert json.loads(json.dumps(r.to_dict()))["lvs"]["available"] is False


def test_unknown_pdk_verdicts_come_before_any_side_effect(tmp_path, monkeypatch):
    """The unknown-PDK verdict is returned before a run dir is made or a klayout is looked up — so
    its reason names the PDK even on a host with no klayout — and LVS reports no tool verdict
    (matched=None: nothing was compared)."""
    from spicexplorer_signoff.drc import run_drc
    from spicexplorer_signoff.lvs import run_lvs

    def no_lookup():
        raise AssertionError("klayout looked up for a PDK that has no deck")

    monkeypatch.setattr("spicexplorer_signoff.drc.klayout_exe", no_lookup)
    monkeypatch.setattr("spicexplorer_signoff.lvs.klayout_exe", no_lookup)
    d = run_drc(tmp_path / "c.gds", "c", tmp_path / "drc", pdk="nope-1um")
    v = run_lvs(tmp_path / "c.gds", tmp_path / "c.sp", "c", tmp_path / "lvs", pdk="nope-1um")
    assert not (tmp_path / "drc").exists() and not (tmp_path / "lvs").exists()
    assert (d.passed, d.available, d.n_violations, d.report_path) == (False, False, 0, None)
    assert (v.passed, v.available, v.matched, v.netlist_sha) == (False, False, None, None)
    assert "for_pdk" in d.reason and "for_pdk" in v.reason  # for_pdk's own message, verbatim


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


# --- a crashing PDK runner must surface its traceback, not an empty reason -------------------


def _fake_pdk(tmp_path: Path, runner_body: str) -> PdkPaths:
    """A PdkPaths whose DRC/LVS runners are a tiny python script that crashes."""
    runner = tmp_path / "run_x.py"
    runner.write_text(runner_body)
    return PdkPaths(
        name="fake",
        root=tmp_path,
        klayout_tech=tmp_path,
        drc_runner=runner,
        lvs_runner=runner,
        lyp=tmp_path / "fake.lyp",
        ngspice_models=tmp_path,
    )


_CRASHER = (  # what the PDK's run_lvs.py did under a SIGNOFF_PYTHON without docopt
    "raise ModuleNotFoundError(\"No module named 'docopt'\")\n"
)


@pytest.fixture
def crashing_pdk(tmp_path, monkeypatch):
    monkeypatch.delenv("SIGNOFF_PYTHON", raising=False)  # the env may point at another interpreter
    kl = tmp_path / "klayout"
    kl.write_text("#!/bin/sh\n")
    monkeypatch.setattr("spicexplorer_signoff.lvs.klayout_exe", lambda: str(kl))
    monkeypatch.setattr("spicexplorer_signoff.drc.klayout_exe", lambda: str(kl))
    (tmp_path / "cell.gds").write_bytes(b"")
    (tmp_path / "cell.sp").write_text(".subckt cell a\n.ends\n")
    return _fake_pdk(tmp_path, _CRASHER)


def test_run_lvs_surfaces_the_runner_traceback(crashing_pdk, tmp_path):
    """The runner raises, writes no <topcell>.log, and `reason` used to come back EMPTY — the
    reviewer saw `matched=False` with no cause (the cause was a ModuleNotFoundError all along)."""
    from spicexplorer_signoff.lvs import run_lvs

    r = run_lvs(
        tmp_path / "cell.gds",
        tmp_path / "cell.sp",
        "cell",
        tmp_path / "run",
        pdk=crashing_pdk,
    )
    assert r.available and not r.passed
    assert "ModuleNotFoundError" in r.reason or "No module named" in r.reason
    assert "exited" in r.reason and "no cell.log" in r.reason


def test_run_drc_reason_carries_the_runner_output(crashing_pdk, tmp_path):
    from spicexplorer_signoff.drc import run_drc

    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert r.available and not r.passed
    assert "ModuleNotFoundError" in r.reason or "No module named" in r.reason


def test_run_drc_reason_when_a_zero_exit_runner_writes_no_report(crashing_pdk, tmp_path):
    """A runner that exits 0, prints no "DRC Check Passed" and leaves no .lyrdb is not a pass —
    and it must say why (it used to fall through to `passed=False, reason=""`)."""
    from spicexplorer_signoff.drc import run_drc

    crashing_pdk.drc_runner.write_text("print('nothing to see')\n")
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert r.available and not r.passed and r.reason
    assert "without a 'DRC Check Passed' verdict" in r.reason and "nothing to see" in r.reason


# --- a verdict may only be read out of files THIS run wrote ---------------------------------

_RUNDIR = (
    "import sys\nrd = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--run_dir=')][0]\n"
)
_EMPTY_LYRDB = "<report-database><items></items></report-database>"


def test_run_lvs_ignores_a_stale_matching_log(crashing_pdk, tmp_path):
    """THE blocker: `run_dir` is never cleared, so a fix-and-retry loop leaves the previous good
    run's `cell.log` beside a crashed runner. Parsing it reported `passed=True` with a traceback
    sitting in `reason` — a signed-off LVS for a run that never happened."""
    from spicexplorer_signoff.lvs import run_lvs

    run = tmp_path / "run"
    run.mkdir()
    (run / "cell.log").write_text("Netlists match.\n")  # left by an earlier, successful attempt
    r = run_lvs(tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", run, pdk=crashing_pdk)
    assert not r.passed and not r.matched
    assert "No module named" in r.reason


def test_run_lvs_exit0_with_an_empty_log_is_not_a_pass(crashing_pdk, tmp_path):
    """P1: a runner that exits 0 and writes an empty log stated no verdict at all. That used to
    come back `passed=False` with an EMPTY reason, indistinguishable from a real mismatch."""
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.lvs_runner.write_text(_RUNDIR + "open(rd + '/cell.log', 'w').close()\n")
    r = run_lvs(
        tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", tmp_path / "run", pdk=crashing_pdk
    )
    assert not r.passed and not r.matched and not r.unmatched
    assert "neither a 'Netlists match' verdict nor unmatched counts" in r.reason


def test_run_lvs_exit0_with_a_verdictless_log_is_not_a_pass(crashing_pdk, tmp_path):
    """P2: same, with a log that has content but no verdict line."""
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.lvs_runner.write_text(
        _RUNDIR + "open(rd + '/cell.log', 'w').write('Reading layout...\\n')\n"
    )
    r = run_lvs(
        tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", tmp_path / "run", pdk=crashing_pdk
    )
    assert not r.passed and r.reason


def test_run_drc_ignores_a_stale_report(crashing_pdk, tmp_path):
    """A previous run's .lyrdb must not be counted as this run's violations."""
    from spicexplorer_signoff.drc import run_drc

    run = tmp_path / "run"
    run.mkdir()
    (run / "cell_full.lyrdb").write_text(
        "<report-database><items><item><category>x</category></item></items></report-database>"
    )
    r = run_drc(tmp_path / "cell.gds", "cell", run, pdk=crashing_pdk)
    assert not r.passed and r.n_violations == 0 and "No module named" in r.reason


def test_run_drc_exit0_with_an_empty_report_is_not_a_pass(crashing_pdk, tmp_path):
    """P3: an empty-but-parsable .lyrdb plus a 0 exit is not a clean cell — only the runner's own
    "DRC Check Passed" line is a positive verdict."""
    from spicexplorer_signoff.drc import run_drc

    crashing_pdk.drc_runner.write_text(
        _RUNDIR + f"open(rd + '/cell_full.lyrdb', 'w').write({_EMPTY_LYRDB!r})\n"
    )
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert not r.passed and r.n_violations == 0 and r.reason


_STALLER = "import sys, time\nprint('partial output here')\nsys.stdout.flush()\ntime.sleep(30)\n"


def test_run_lvs_timeout_keeps_the_partial_output(crashing_pdk, tmp_path):
    """P5: the timeout branch threw away everything the runner had already said. Note
    `TimeoutExpired.stdout` is BYTES even though the call passed `text=True`."""
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.lvs_runner.write_text(_STALLER)
    r = run_lvs(
        tmp_path / "cell.gds",
        tmp_path / "cell.sp",
        "cell",
        tmp_path / "run",
        pdk=crashing_pdk,
        timeout_s=1,
    )
    assert not r.passed and "timed out" in r.reason
    assert "partial output here" in r.log and "partial output here" in r.reason


def test_run_drc_timeout_keeps_the_partial_output(crashing_pdk, tmp_path):
    """P6, same for DRC."""
    from spicexplorer_signoff.drc import run_drc

    crashing_pdk.drc_runner.write_text(_STALLER)
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk, timeout_s=1)
    assert not r.passed and "timed out" in r.reason
    assert "partial output here" in r.log


def test_run_pex_ignores_a_stale_netlist(tmp_path, monkeypatch):
    """kpex's `out_dir` survives between attempts too: a crashed kpex must not be summarized from
    the previous run's `*_k25d_pex_netlist.spice`."""
    from spicexplorer_signoff.pex import run_pex

    gds, sch = tmp_path / "top.gds", tmp_path / "top.sp"
    gds.write_bytes(b"")
    sch.write_text(".subckt cell a\n.ends\n")
    stale = tmp_path / "out" / "top__cell" / "cell_k25d_pex_netlist.spice"
    stale.parent.mkdir(parents=True)
    stale.write_text("C1 a b 1f\n")  # left by an earlier, successful extraction
    kp = tmp_path / "kpex"
    kp.write_text("#!/usr/bin/env python3\nraise SystemExit('kpex blew up')\n")
    kp.chmod(0o755)
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_exe", lambda: str(kp))
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_klayout_exe", lambda: str(tmp_path / "kl"))
    r = run_pex(gds, "cell", sch, tmp_path / "out")
    assert r.available and not r.ok and r.n_c == 0
    assert "during this run" in r.reason and "stale file is present" in r.reason


# --- current density: the check no rule deck and no LVS run can make ------------------------


def test_current_density_with_unset_pdk_reports_unavailable_not_ihps_table(monkeypatch):
    """With no `tech=`/`pdk=` and `$PDK` unset, `check_current_density` must behave like its
    sibling `unqualified_reason` — report the process as unresolved — instead of silently
    resolving through the `"ihp-sg13g2"` literal in its own default expression and returning a
    real (mis-attributed) violation (reuse review F9)."""
    monkeypatch.delenv("PDK", raising=False)
    from spicexplorer_signoff import Budget, check_current_density
    from spicexplorer_signoff.current_density import _limits, unqualified_reason

    # `_limits` is lru_cache'd on the "which $PDK to read" key (`""`); a prior test in this
    # process that resolved with $PDK set would otherwise poison this test with IHP's table.
    _limits.cache_clear()

    res = check_current_density([Budget("vdd", 10e-3, "Metal1", width_um=0.5)])
    assert not res.available
    assert not res.passed
    assert res.n_violations == 0
    assert "em_limits" in res.reason
    assert res.pdk != "ihp-sg13g2"  # never a mis-attributed answer from the old literal fallback
    assert "$PDK" in res.pdk

    reason = unqualified_reason("Metal1", width_um=0.5)
    assert "em_limits" in reason
    assert "ihp-sg13g2" not in reason


def test_current_density_reproduces_the_ldo_findings():
    """The LDO cell of record in an agent-first design repo: DRC-clean, LVS-matched, and
    12-28x over the metal limit on its 10 mA load path."""
    from spicexplorer_signoff import Budget, check_current_density

    res = check_current_density(
        [
            Budget("vdd", 10e-3, "Metal1", width_um=0.8, note="vdd rail (rail_w)"),
            Budget("vout", 10e-3, "Metal1", width_um=0.6, note="vout drain bus"),
            Budget("vout", 10e-3 / 19, "Metal1", width_um=0.2, note="per-finger S/D drop"),
            Budget("vout", 10e-3, "Metal1", width_um=0.2, note="vout pin track"),
            Budget("vout", 10e-3, "Via1", n_vias=1, note="vout pin via"),
        ],
        pdk="ihp-sg13g2",
    )
    assert res.available and not res.passed and res.n_violations == 5
    over = {(v.net, v.layer, v.width_um, v.n_vias): v.over_factor for v in res.violations}
    assert over[("vdd", "Metal1", 0.8, 1)] == pytest.approx(12.5)
    assert over[("vout", "Metal1", 0.6, 1)] == pytest.approx(16.667, rel=1e-3)
    assert over[("vout", "Via1", 0.0, 1)] == pytest.approx(25.0)
    assert res.violations[0].limit_a == pytest.approx(0.8e-3)
    per_finger = [v for v in res.violations if v.note == "per-finger S/D drop"][0]
    assert per_finger.limit_a == pytest.approx(0.36e-3)
    assert per_finger.over_factor == pytest.approx(1.462, rel=1e-3)


def test_current_density_passes_a_budget_that_fits():
    from spicexplorer_signoff import Budget, check_current_density

    res = check_current_density(
        [
            Budget("vout", 10e-3, "TopMetal1", width_um=2.0),  # 15 mA/µm, >= TM1.a
            Budget("vout", 10e-3, "Via1", n_vias=25),  # 0.4 mA × 25 = 10 mA exactly
            Budget("bias", 50e-6, "Metal1", width_um=0.2),  # 0.36 mA flat band
        ],
        pdk="ihp-sg13g2",
    )
    assert res.passed and res.available and res.violations == []
    assert res.to_dict()["n_violations"] == 0


def test_current_density_layer_table_matches_the_pdk_spec():
    """SG13G2 process spec §2.15: M1 is 1 mA/µm (>0.36 µm) / 0.36 mA flat (0.16–0.36 µm), but
    M2–M5 are 2 mA/µm (>0.3 µm) / 0.6 mA flat — NOT 1 mA/µm as the journal generalised."""
    from spicexplorer_signoff.current_density import limit_for

    assert limit_for("Metal1", width_um=1.0, tech="ihp-sg13g2")[0] == pytest.approx(1e-3)
    assert limit_for("Metal3", width_um=1.0, tech="ihp-sg13g2")[0] == pytest.approx(2e-3)
    assert limit_for("Metal3", width_um=0.25, tech="ihp-sg13g2")[0] == pytest.approx(0.6e-3)
    assert limit_for("TopMetal2", width_um=2.0, tech="ihp-sg13g2")[0] == pytest.approx(32e-3)
    assert limit_for("topvia2", n_vias=3, tech="ihp-sg13g2")[0] == pytest.approx(30e-3)
    assert limit_for("Contact", n_vias=10, tech="ihp-sg13g2")[0] == pytest.approx(3e-3)


def test_current_density_unknown_layer_and_pdk_are_reported_not_silently_passed():
    from spicexplorer_signoff import Budget, check_current_density

    res = check_current_density([Budget("vdd", 1e-3, "Metal1", width_um=1.0)], pdk="nope-1um")
    assert not res.available and not res.passed and "nope-1um" in res.reason

    res = check_current_density([Budget("vdd", 1e-3, "Poly", width_um=1.0)], pdk="ihp-sg13g2")
    assert res.available and not res.passed and "Poly" in res.reason and res.violations == []

    # a Metal1 narrower than the qualified band has no limit to check against
    res = check_current_density([Budget("vdd", 1e-3, "Metal1", width_um=0.1)], pdk="ihp-sg13g2")
    assert res.available and not res.passed and "0.1" in res.reason


def test_current_density_result_is_json_serializable_without_nan():
    """`to_dict()` feeds a scorecard. `float("inf")` (the old `n_vias=0` over-factor) is not JSON,
    so a run that hit it could not be written down at all."""
    import json

    from spicexplorer_signoff import Budget, check_current_density

    for b in (
        Budget("vout", 10e-3, "Via1", n_vias=0),
        Budget("vout", 10e-3, "TopMetal1"),
        Budget("vout", 10e-3, "Metal1", width_um=0.2),
        Budget("vout", 10e-3, "TopMetal1", width_um=2.0),
    ):
        json.dumps(check_current_density([b], pdk="ihp-sg13g2").to_dict(), allow_nan=False)


def test_current_density_zero_vias_is_unchecked_not_infinitely_over():
    """A 0 A limit is a check that did not run, not a limit everything violates: it used to make
    `worst_over_factor` `inf` and a violation row that could not be serialized at all."""
    from spicexplorer_signoff import Budget, check_current_density

    res = check_current_density([Budget("vout", 10e-3, "Via1", n_vias=0)], pdk="ihp-sg13g2")
    assert not res.passed and res.n_checked == 0 and res.n_violations == 0
    assert res.worst_over_factor == 0.0
    assert "at least 1" in res.reason


def test_current_density_top_metals_have_a_real_minimum_width():
    """SG13G2_os_process_spec.pdf §2.15 gives no width band for TopMetal1/2, so `wide_um=0.0`
    accepted ANY width: a 1 nm wire scored, and 10 mA "fit" in 0.67 um of TopMetal1. The floor is
    the PDK rule deck's own minimum width (TM1.a / TM2.a), so a scored width is a drawable one."""
    from spicexplorer_signoff import Budget, check_current_density
    from spicexplorer_signoff.current_density import limit_for

    assert limit_for("TopMetal1", width_um=0.001, tech="ihp-sg13g2") is None
    assert limit_for("TopMetal1", width_um=1.63, tech="ihp-sg13g2") is None
    assert limit_for("TopMetal1", width_um=1.64, tech="ihp-sg13g2")[0] == pytest.approx(24.6e-3)
    assert limit_for("TopMetal2", width_um=1.99, tech="ihp-sg13g2") is None
    assert limit_for("TopMetal2", width_um=2.0, tech="ihp-sg13g2")[0] == pytest.approx(32e-3)
    res = check_current_density(
        [Budget("vout", 10e-3, "TopMetal1", width_um=0.7)], pdk="ihp-sg13g2"
    )
    assert not res.passed and res.n_checked == 0
    assert "TM1.a" in res.reason and "1.64 um" in res.reason


def test_current_density_zero_width_metal_is_never_checked():
    """An omitted `width_um` defaults to 0.0; that must never resolve to a limit."""
    from spicexplorer_signoff.current_density import limit_for, limits

    for layer, lim in limits("ihp-sg13g2").items():
        if not lim.is_via:
            assert limit_for(layer, width_um=0.0, tech="ihp-sg13g2") is None, layer
            assert limit_for(layer, width_um=-1.0, tech="ihp-sg13g2") is None, layer


def test_current_density_with_no_budgets_is_skipped_not_passed():
    """L-PF-20: an empty budget list checks nothing, and it came back `passed=True` with
    `n_checked=0`. It is now `skipped`: not a pass, not a violation, and the reason says why."""
    from spicexplorer_signoff import Budget, check_current_density

    for empty in ([], iter(())):
        res = check_current_density(empty, tech="ihp-sg13g2")
        assert res.passed is False, "a check with no budgets was scored as a pass"
        assert res.skipped is True and res.available is True
        assert res.n_checked == 0 and res.n_violations == 0 and res.violations == []
        assert "no budget" in res.reason
        assert res.to_dict()["skipped"] is True

    res = check_current_density([Budget("vdd", 1e-6, "Metal1", width_um=1.0)], tech="ihp-sg13g2")
    assert res.passed is True and res.skipped is False
    # a process with no limits table is still reported as unavailable, budgets or not
    res = check_current_density([], tech="nope-1um")
    assert res.available is False and res.skipped is False and not res.passed


# --- nothing a runset writes may land outside the run directory (defect B) -------------------

_FAKE_KPEX = '''#!/usr/bin/env python3
"""Stands in for kpex: writes the two `<cell>_extracted.cir` strays the IHP LVS runset produces
when `target_netlist` is unset — one at `../` (the empty-CellView branch, relative to the process
cwd) and one beside the input GDS — plus the netlist kpex itself produces."""
import pathlib
import sys

argv = sys.argv


def opt(name):
    return argv[argv.index(name) + 1]


gds, cell, out = pathlib.Path(opt("--gds")), opt("--cell"), pathlib.Path(opt("--out_dir"))
pathlib.Path("..", f"{cell}_extracted.cir").write_text("* Pathname.new(\\"\\").parent == '..'\\n")
(gds.parent / f"{cell}_extracted.cir").write_text("* beside the loaded CellView's own GDS\\n")
d = out / f"{gds.stem}__{cell}"
d.mkdir(parents=True, exist_ok=True)
(d / f"{cell}_k25d_pex_netlist.spice").write_text(
    ".subckt c a b\\nM$1 a b 0 0 nmos w=1u l=1u\\nCext_1 a b 1f\\n.ends c\\n"
)
'''


def _fake_tool(path: Path, body: str) -> Path:
    path.write_text(body)
    path.chmod(0o755)
    return path


def test_run_pex_writes_nothing_outside_out_dir(tmp_path, monkeypatch):
    """Defect B: the IHP LVS runset's fallback `<cell>_extracted.cir` used to land beside the
    INPUT GDS (a repo/example tree) or at `..` of the process cwd (`Pathname.new("").parent`),
    which is how stray `.cir` files reached the meta-repo root and `external/`. kpex forwards no
    `-rd target_netlist=`, so containment is the run's cwd + the GDS it is handed."""
    from spicexplorer_signoff.pex import run_pex

    src = tmp_path / "src"
    src.mkdir()
    gds = src / "cell.gds"
    gds.write_bytes(b"")
    sch = src / "cell.sp"
    sch.write_text(".subckt c a b\n.ends c\n")
    out = tmp_path / "run" / "pex"
    kp = _fake_tool(tmp_path / "fake_kpex", _FAKE_KPEX)
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_exe", lambda: str(kp))
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_klayout_exe", lambda: str(kp))

    r = run_pex(gds, "c", sch, out, mode="CC")

    assert r.ok and r.netlist_path
    strays = [p for p in tmp_path.rglob("*_extracted.cir")]
    assert strays, "the fake runset must have written its strays somewhere"
    for s in strays:
        assert out in s.parents, f"{s} escaped the run dir"
    assert not list(src.glob("*_extracted.cir"))  # the input GDS's own directory is untouched
    assert not list(tmp_path.glob("*_extracted.cir"))  # ... and so is the tree above the run dir


def test_run_lvs_runs_from_the_run_dir(crashing_pdk, tmp_path):
    """Defect B, LVS side: the runner used to execute with the PDK deck's own directory as cwd,
    so anything a deck wrote relative to cwd landed in the shared PDK tree."""
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.lvs_runner.write_text(
        _RUNDIR
        + "import os\n"
        + "open('cell_stray.cir', 'w').write('* cwd-relative\\n')\n"
        + "open(rd + '/cell.log', 'w').write('Netlists match.\\n')\n"
    )
    run = tmp_path / "run"
    r = run_lvs(tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", run, pdk=crashing_pdk)
    assert r.passed
    assert (run / "cell_stray.cir").is_file()
    assert not (crashing_pdk.lvs_runner.parent / "cell_stray.cir").exists()


# --- RC/R: kpex's resistor mesh is an island until it is stitched (defect A) -----------------

# kpex 0.3.12 shape: the devices and the lumped `Cext_` cards use the FLAT net node, while every
# `Rext_` card lives on `<net>.<sub>` mesh nodes that no card ever joins to that flat node.
#
# Shape of the miniature below, a faithful model of the LDO's `vdd` strap: the two devices on
# `out` sit on DIFFUSION (`.25` = pSD, `.24` = nSD), each behind a 17 Ω contact stack (SG13G2
# `Cont` is 0.435 Ω·µm² over a 0.16 µm square), and the 0.5 Ω between `out.$0.18` and `out.$1.18`
# is the drawn Metal1 that a hand model would compute. `Rext_4` is 0 Ω because SG13G2 gives
# `nSD`/`pSD` 0.0 Ω/square — 3099 of the LDO's 8545 mesh cards are exactly that.
_RAW_RC = """.SUBCKT cell vdd vss out
M$1 out in vss vss nmos L=0.5U W=1U
M$2 out in vdd vdd pmos L=0.5U W=2U
R$3 out fb vss rhigh W=1U L=10U
Cext_1 out vss 1.5f
Rext_1 out.P0.25 out.$0.18 17.0 R
Rext_2 out.$0.18 out.$1.18 0.5 R
Rext_3 out.$1.18 out.P1.24 17.0 R
Rext_4 out.P1.24 out.P2.24 0 R
Rext_5 vss.P0.24 vss.$2.18 3.0 R
Rext_6 vss.$2.18 vss.P1.24 3.0 R
Rext_7 fb.P0.17 fb.$0.18 4.0 R
.ENDS cell
"""

# NOTE the `R$3` entries: kpex 0.3.12 registers NO terminal regions for its resistor devices, so
# on a real run these keys are absent and a resistor-only net comes back as a stub mesh (see
# `n_stub_nets`). They are here because a resistor terminal must be repointed like any other the
# moment kpex does emit one — the card class must not be what decides it.
_TMAP = {
    ("$1", "D"): "out.P1.24",
    ("$1", "S"): "vss.P0.24",
    ("$2", "D"): "out.P0.25",
    ("$2", "S"): "vdd.P9.25",  # no mesh node of its own in the netlist: must stay on the flat net
    ("$3", "A"): "out.P2.24",
    ("$3", "B"): "fb.P0.17",
}
# what `read_mesh_info` recovers from the same report database
_INFO = {
    "out.P0.25": ("pSD", "Device Terminal"),
    "out.P1.24": ("nSD", "Device Terminal"),
    "out.P2.24": ("nSD", "Device Terminal"),
    "vss.P0.24": ("nSD", "Device Terminal"),
    "vss.P1.24": ("nSD", "Device Terminal"),
    "vdd.P9.25": ("pSD", "Device Terminal"),
    "fb.P0.17": ("GatPoly", "Device Terminal"),
    "out.$0.18": ("Metal1", "Wire Junction"),
    "out.$1.18": ("Metal1", "Wire Junction"),
    "vss.$2.18": ("Metal1", "Wire Junction"),
    "fb.$0.18": ("Metal1", "Wire Junction"),
}
_SHEET = {
    "GatPoly": 7.0,
    "Metal1": 0.11,
    "Metal2": 0.088,
    "TopMetal1": 0.018,
    "nSD": 0.0,
    "pSD": 0.0,
}


def test_check_mesh_connectivity_fails_on_a_raw_kpex_rc_netlist():
    """THE blocker: `n_r` counted 8397 cards on the LDO while the mesh touched NOTHING — mesh ∩
    device pins was empty, so `.option rshunt=1e12` made the RC row equal the CC row to five
    digits. A verdict that reads `ok=True, n_r=8418` off that netlist is a false pass."""
    from spicexplorer_signoff.pex import check_mesh_connectivity

    ok, detail = check_mesh_connectivity(_RAW_RC)
    assert not ok
    assert detail["n_pins_on_mesh"] == 0 and detail["n_mesh_nodes"] == 10
    assert detail["n_open_nets"] == 3 and set(detail["open_nets"]) == {"out", "vss", "fb"}
    # PDK resistor devices are device pins as much as transistors are; only kpex's own `Rext_`
    # cards are parasitics. Counting only M cards is how the LDO read "33 device pins" as 14.
    assert detail["n_device_pins"] == 5  # out, in, vss, vdd, fb


def test_stitch_rc_netlist_joins_every_device_pin_to_its_mesh():
    from spicexplorer_signoff.pex import check_mesh_connectivity, stitch_rc

    out, detail = stitch_rc(_RAW_RC, _TMAP, node_info=_INFO, sheet=_SHEET)
    assert "M$1 out.P1.24 in vss.P0.24 vss nmos" in out
    assert "M$2 out.P0.25 in vdd vdd pmos" in out  # unmapped pin left on the flat net
    assert "R$3 out.P1.24 fb.P0.17 vss rhigh" in out  # a resistor device, not a parasitic card
    ok, d = check_mesh_connectivity(out)
    assert ok and d["n_open_nets"] == 0 and d["n_pins_on_mesh"] == 4
    assert d["n_stub_nets"] == 0  # every mesh has a device pin on it, not just the tie


def test_stitch_anchors_the_port_on_metal_not_on_a_device_terminal():
    """DEFECT A. The first cut anchored the flat net at `sorted(repointed device terminals)[0]`,
    which can only ever be a DEVICE terminal — on diffusion or poly, BELOW the contact stack. On
    the LDO that referred the `vdd` port to a `pSD` node, so port current ran down one device's
    contacts and back up another's and R(port → each of 39 pass columns) read 49.04–49.19 Ω,
    near-constant, against 0.63 Ω of drawn TopMetal1. Here the same defect reads: the old anchor
    `out.P0.25` puts BOTH 17 Ω contact stacks between the port and `out.P1.24` (34.5 Ω) where the
    metal answer is 17.5 Ω, and makes R(port → `out.P0.25`) exactly 0."""
    from spicexplorer_signoff.pex import stitch_rc

    out, detail = stitch_rc(_RAW_RC, _TMAP, node_info=_INFO, sheet=_SHEET)
    # the anchor is the routing node, and it is recorded with the layer it was chosen on
    assert detail["anchors"]["out"] == ["out.$0.18", "Metal1", "proxy"]
    assert detail["anchors"]["vss"] == ["vss.$2.18", "Metal1", "proxy"]
    assert detail["anchors"]["fb"] == ["fb.$0.18", "Metal1", "proxy"]
    assert detail["n_anchor_proxies"] == 3 and detail["n_anchor_pins"] == 0
    # merged, so the port IS the Metal1 node: one contact stack to each device, never two
    assert "Rext_1 out.P0.25 out 17.0 R" in out
    assert "Rext_2 out out.$1.18 0.5 R" in out
    assert "out.$0.18" not in out


def test_stitch_merges_the_net_instead_of_tying_it_with_a_zero_ohm_resistor():
    """DEFECT B. ngspice coerces a 0 Ω resistor to 1e-12 Ω (1e12 S). The LDO's `.op` dropped from
    KLU to SPARSE 1.3 and then failed gmin/source stepping on a mesh full of them — 33 of our ties
    plus 3099 of kpex's own, because SG13G2 gives nSD/pSD 0.0 Ω/square. A 0 Ω element IS one node,
    so both classes are merged rather than emitted."""
    from spicexplorer_signoff.pex import check_mesh_connectivity, stitch_rc

    out, detail = stitch_rc(_RAW_RC, _TMAP, node_info=_INFO, sheet=_SHEET)
    assert "Rstitch_" not in out and " 0 R" not in out
    assert detail["n_zero_edges_merged"] == 1 and detail["n_cards_collapsed"] == 1
    assert "Rext_4" not in out and "out.P2.24" not in out  # merged into `out.P1.24`
    assert check_mesh_connectivity(out)[0]


def test_stitch_merges_a_zero_ohm_edge_that_lands_on_a_pin_node():
    """DEFECT B, round 3. Round 2 merged a 0 Ω edge only when BOTH ends parsed as `<net>.<node>`
    mesh nodes. A kpex `[Pin]` node is spelled with the PLAIN net name, so an edge from the port
    to a coincident wire junction failed that test and was emitted verbatim. On the LDO's `it13`
    (17 pin-purpose squares added under the port labels) exactly two of 3101 zero cards are of
    that shape --

        Rext_971  fb   fb.$24.18   0 R
        Rext_7135 vref vref.$0.18  0 R

    -- and ngspice clamps each to 1e-12 Ω, putting a 1e12 S entry in a matrix whose signal
    entries are ~1e-5 S; the direct solve then returns a non-solution that violates KCL at `fb`
    by ~1.5 uA. The merge now works on the NET a node belongs to, so the mesh side is renamed
    onto the port and the card collapses -- the port name, which the subckt header carries,
    is always the class representative and so never moves."""
    from spicexplorer_signoff.pex import check_mesh_connectivity, stitch_rc

    pinned = """.SUBCKT cell vdd out fb
M$1 out in vdd vdd pmos L=0.5U W=2U
Rext_1 fb fb.$24.18 0 R
Rext_2 fb.$24.18 fb.$25.18 0.4 R
Rext_3 out out.P0.25 17.0 R
.ENDS cell
"""
    info = {
        "fb": ("Metal1", "Pin"),
        "out": ("Metal1", "Pin"),
        "fb.$24.18": ("Metal1", "Wire Junction"),
        "fb.$25.18": ("Metal1", "Wire Junction"),
        "out.P0.25": ("pSD", "Device Terminal"),
    }
    text, detail = stitch_rc(pinned, {("$1", "D"): "out.P0.25"}, node_info=info, sheet=_SHEET)
    assert " 0 R" not in text  # nothing ngspice will coerce to 1e-12
    assert "Rext_1" not in text and "fb.$24.18" not in text  # collapsed onto the port
    assert "Rext_2 fb fb.$25.18 0.4 R" in text  # the port IS the junction now
    assert ".SUBCKT cell vdd out fb" in text  # the port name never moves
    assert detail["n_zero_edges_merged"] == 1 and detail["n_cards_collapsed"] == 1
    assert check_mesh_connectivity(text)[1]["n_zero_r_cards"] == 0


def test_stitch_refuses_a_zero_ohm_edge_that_would_short_two_nets_and_says_so():
    """The other half of the same rule: a 0 Ω card whose ends belong to DIFFERENT nets is not a
    node identity, it is a short, and merging it would silently weld two nets together. It is
    left alone -- and then counted, so the stage fails loudly instead of handing ngspice a card
    it will coerce."""
    from spicexplorer_signoff.pex import check_mesh_connectivity, stitch_rc

    crossed = """.SUBCKT cell fb vref
Rext_1 fb vref.$0.18 0 R
Rext_2 vref vref.$0.18 0.4 R
.ENDS cell
"""
    info = {
        "fb": ("Metal1", "Pin"),
        "vref": ("Metal1", "Pin"),
        "vref.$0.18": ("Metal1", "Wire Junction"),
    }
    text, detail = stitch_rc(crossed, {}, node_info=info, sheet=_SHEET)
    assert "Rext_1 fb vref.$0.18 0 R" in text  # refused, not welded
    assert detail["n_zero_edges_merged"] == 0
    ok, d = check_mesh_connectivity(text)
    assert d["n_zero_r_cards"] == 1 and d["zero_r_cards"] == ["Rext_1"]


def test_pick_anchor_prefers_a_kpex_pin_node_then_the_lowest_sheet_resistance():
    """kpex names a mesh node with the plain net name only for a `[Pin]` (VertexPort) node, which
    needs a polygon on the layer's PIN purpose (`<metal>/2` in SG13G2) under the label text
    (`<metal>/25`) — `klayout_pex/klayout/lvsdb_extractor.py`, `pin_labels = labels & pins`. When
    one exists it is the port, exactly; otherwise the best proxy is the lowest-sheet-R ROUTING
    layer, never diffusion (which reads 0.0 Ω/square and would otherwise win)."""
    from spicexplorer_signoff.pex import pick_anchor

    info = {
        "n.P0.25": ("pSD", "Device Terminal"),
        "n.$0.18": ("Metal1", "Wire Junction"),
        "n.$1.22": ("TopMetal1", "Wire Junction"),
        "n": ("TopMetal1", "Pin"),
    }
    dev = {"pSD"}
    assert pick_anchor(sorted(info), info, _SHEET, dev) == ("n", "pin")
    no_pin = {k: v for k, v in info.items() if v[1] != "Pin"}
    assert pick_anchor(sorted(no_pin), no_pin, _SHEET, dev) == ("n.$1.22", "proxy")
    # with no layer information at all the anchor degrades to name order, not to a crash
    assert pick_anchor(sorted(no_pin), {}, {}, set()) == ("n.$0.18", "proxy")


def test_stitch_leaves_a_net_kpex_already_pinned_alone():
    """A layout that DOES carry pin polygons gets `[Pin]` nodes, and kpex then names the mesh node
    at the pin with the plain net name — the flat node is already on the mesh. A second tie there
    would be an arbitrary short across the net."""
    from spicexplorer_signoff.pex import stitch_rc

    pinned = """.SUBCKT cell vdd out
M$1 out in vdd vdd pmos L=0.5U W=2U
Rext_1 out out.$0.18 0.4 R
Rext_2 out.$0.18 out.P0.25 17.0 R
.ENDS cell
"""
    text, detail = stitch_rc(
        pinned,
        {("$1", "D"): "out.P0.25"},
        node_info={
            "out": ("Metal1", "Pin"),
            "out.$0.18": ("Metal1", "Wire Junction"),
            "out.P0.25": ("pSD", "Device Terminal"),
        },
        sheet=_SHEET,
    )
    assert detail["anchors"]["out"] == ["out", "Metal1", "pin"]
    assert detail["n_anchor_pins"] == 1 and detail["n_anchor_proxies"] == 0
    assert "Rext_1 out out.$0.18 0.4 R" in text  # untouched: no tie, no merge
    assert "M$1 out.P0.25 in vdd vdd pmos" in text


def test_check_mesh_connectivity_passes_a_cc_netlist_with_no_mesh():
    """CC mode has no mesh at all — the check must not invent a failure for it."""
    from spicexplorer_signoff.pex import check_mesh_connectivity

    ok, detail = check_mesh_connectivity(FIX / "mini_pex.spice")
    assert ok and detail["n_mesh_nodes"] == 0 and detail["n_nets_with_mesh"] == 0
    assert detail["n_stub_nets"] == 0


def _write_rdb(path: Path) -> Path:
    """A minimal kpex `*_k25d_pex_report.rdb.gz`: the two categories `read_terminal_map` joins."""
    import klayout.db as db
    import klayout.rdb as krdb

    rdb = krdb.ReportDatabase("")
    cell = rdb.create_cell("cell")

    def leaf(parent, name):
        return rdb.create_category(parent, name) if parent else rdb.create_category(name)

    def shape(cat, box):
        item = rdb.create_item(cell.rdb_id(), cat.rdb_id())
        item.add_value(db.DPolygon(box))

    #  (device, terminal) regions
    request = leaf(None, "[R] Extraction Request")
    conductors = leaf(leaf(request, "[R] Extraction Tech"), "Conductors")
    for idx, (name, lvs, ohm) in enumerate(
        (
            ("GatPoly", "poly_con", 7.0),
            ("Metal1", "metal1_con", 0.11),
            ("Metal2", "metal2_con", 0.088),
            ("TopMetal1", "topmetal1_con", 0.018),
            ("nSD", "nsd_fet", 0.0),
            ("pSD", "psd_fet", 0.0),
        )
    ):
        leaf(conductors, f"{idx}: {name} (LVS {lvs}), {ohm} mΩ/µm^2")
    devices = leaf(request, "Devices")
    boxes = {
        ("$1", "D", "out", "nSD"): db.DBox(0, 0, 1, 1),
        ("$1", "S", "vss", "nSD"): db.DBox(2, 0, 3, 1),
        ("$2", "D", "out", "pSD"): db.DBox(4, 0, 5, 1),
        ("$2", "S", "vdd", "pSD"): db.DBox(6, 0, 7, 1),
        ("$3", "A", "out", "nSD"): db.DBox(8, 0, 9, 1),
        ("$3", "B", "fb", "GatPoly"): db.DBox(10, 0, 11, 1),
    }
    for dev, cls in (("$1", "sg13_lv_nmos"), ("$2", "sg13_lv_pmos"), ("$3", "rhigh")):
        d = leaf(devices, f"{dev}: {cls}")
        terms = leaf(d, "Terminals")
        for (dv, tn, net, layer), box in boxes.items():
            if dv == dev:
                shape(leaf(terms, f"{tn}: net {net}, layer {layer}"), box)
    #  the mesh nodes kpex built at those regions
    nets = leaf(leaf(None, "[R] Extraction Result"), "Networks")
    nodes_for = {
        ("out", "nSD", db.DBox(0, 0, 1, 1)): "P1.24",
        ("vss", "nSD", db.DBox(2, 0, 3, 1)): "P0.24",
        ("out", "pSD", db.DBox(4, 0, 5, 1)): "P0.25",
        ("vdd", "pSD", db.DBox(6, 0, 7, 1)): "P9.25",
        ("out", "nSD", db.DBox(8, 0, 9, 1)): "P2.24",
        ("fb", "GatPoly", db.DBox(10, 0, 11, 1)): "P0.17",
        # a second `vss` terminal region, on no device the request lists: a node, not a mapping
        ("vss", "nSD", db.DBox(12, 0, 13, 1)): "P1.24",
    }
    junctions = {"out": ("$0.18", "$1.18"), "vss": ("$2.18",), "fb": ("$0.18",), "vdd": ()}
    for net in ("out", "vss", "vdd", "fb"):
        nodes = leaf(leaf(nets, f"Net {net}"), "Nodes")
        for (n, layer, box), node in nodes_for.items():
            if n == net:
                shape(
                    leaf(nodes, f"[Device Terminal] {node}, port net {net}.{node}, layer {layer}"),
                    box,
                )
        for k, node in enumerate(junctions[net]):
            shape(
                leaf(nodes, f"[Wire Junction] {node}, port net {net}.{node}, layer Metal1"),
                db.DBox(9 + k, 9, 10 + k, 10),
            )
    rdb.save(str(path))
    return path


def test_read_terminal_map_matches_device_terminals_to_mesh_nodes(tmp_path):
    """The mapping is exact, not nearest-neighbour: kpex logs the device-terminal mesh node with
    the terminal's own polygon, so (net, layer, polygon) identifies it."""
    pytest.importorskip("klayout.rdb")
    from spicexplorer_signoff.pex import read_terminal_map

    m = read_terminal_map(_write_rdb(tmp_path / "cell_k25d_pex_report.rdb"))
    assert m == _TMAP


def test_read_mesh_info_recovers_the_layer_of_every_node_and_the_sheet_resistances(tmp_path):
    """The anchor rule needs two things kpex already logs: which layer each mesh node sits on
    (with its kind, so a device terminal is recognizable) and the conductor sheet resistances.
    kpex prints the latter as `mΩ/µm^2`; the value is Ω/square (`klayout_pex/tech_info.py`)."""
    pytest.importorskip("klayout.rdb")
    from spicexplorer_signoff.pex import read_mesh_info

    info, sheet = read_mesh_info(_write_rdb(tmp_path / "cell_k25d_pex_report.rdb"))
    assert info == _INFO
    assert sheet == _SHEET


def test_run_pex_rc_refuses_an_unstitchable_mesh(tmp_path, monkeypatch):
    """No report database means no way to know which mesh node is which device terminal — that is
    a failed stage with a reason, not `ok=True, n_r=<big>`."""
    from spicexplorer_signoff.pex import run_pex

    gds, sch = tmp_path / "cell.gds", tmp_path / "cell.sp"
    gds.write_bytes(b"")
    sch.write_text(".subckt cell a\n.ends\n")
    body = (
        "#!/usr/bin/env python3\nimport pathlib, sys\na = sys.argv\n"
        "g = pathlib.Path(a[a.index('--gds') + 1]); out = pathlib.Path(a[a.index('--out_dir') + 1])\n"
        "d = out / f'{g.stem}__cell'; d.mkdir(parents=True, exist_ok=True)\n"
        f"(d / 'cell_k25d_pex_netlist.spice').write_text({_RAW_RC!r})\n"
    )
    kp = _fake_tool(tmp_path / "fake_kpex_rc", body)
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_exe", lambda: str(kp))
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_klayout_exe", lambda: str(kp))

    r = run_pex(gds, "cell", sch, tmp_path / "pex", mode="RC")
    assert not r.ok and r.available and r.n_r == 8
    assert "no cell_k25d_pex_report.rdb.gz" in r.reason

    r2 = run_pex(gds, "cell", sch, tmp_path / "pex2", mode="RC", stitch_mesh=False)
    assert not r2.ok and r2.mesh_connected is False
    assert "not connected to the circuit" in r2.reason and r2.mesh["n_pins_on_mesh"] == 0


# ----------------------------------------------------------------------
# SIGN-02 — a non-finite current is not a measurement
# ----------------------------------------------------------------------
# `if abs(b.current_a) > limit_a` is False for NaN, so a NaN current was recorded as a PASS and
# counted in `n_checked`. That is precisely what this module's own docstring rules out: "silence
# from a check that did not run is not evidence." ±Inf failed in the other direction — it became a
# violation with `over_factor=inf`, which then made `json.dumps(..., allow_nan=False)` raise,
# contradicting the JSON-safe claim on the result.


def _nonfinite_result(value: float):
    from spicexplorer_signoff import Budget, check_current_density

    return check_current_density(
        [Budget(net="vdd", layer="Metal1", current_a=value, width_um=1.0)], pdk="ihp-sg13g2"
    )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_current_fails_closed_and_is_not_counted_as_checked(value):
    r = _nonfinite_result(value)
    assert r.passed is False, "a current that is not a number was scored as a pass"
    assert r.n_checked == 0, "a budget that could not be compared was counted as checked"
    assert "vdd" in r.reason and "finite" in r.reason


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_the_result_stays_json_safe(value):
    """`to_dict()` is documented JSON-safe; ±Inf used to leak into `worst_over_factor`."""
    import json

    json.dumps(_nonfinite_result(value).to_dict(), allow_nan=False)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_width_fails_closed_and_is_not_counted_as_checked(value):
    """The same hole through the other field: `width_um=+inf` scaled the limit to infinity, so
    one amp on Metal1 came back `passed=True, n_checked=1`."""
    from spicexplorer_signoff import Budget, check_current_density

    r = check_current_density(
        [Budget(net="vdd", layer="Metal1", current_a=1.0, width_um=value)], pdk="ihp-sg13g2"
    )
    assert r.passed is False, "a width that is not a number was scored as a pass"
    assert r.n_checked == 0, "a budget that could not be compared was counted as checked"
    assert "vdd" in r.reason and "finite" in r.reason


def test_a_finite_current_is_unaffected():
    from spicexplorer_signoff import Budget, check_current_density

    r = check_current_density(
        [Budget(net="vdd", layer="Metal1", current_a=1e-6, width_um=1.0)], pdk="ihp-sg13g2"
    )
    assert r.n_checked == 1
    assert r.passed is True


# ----------------------------------------------------------------------
# SIGN-03 — `topmetal_margin_um=None` must actually keep TopMetal1
# ----------------------------------------------------------------------
# The alias defaulted to None and was applied only `if topmetal_margin_um is not None`, so the
# documented way to keep the top plates was indistinguishable from not passing it: the cut-back
# happened anyway and only the undocumented `margin_um=None` worked. The existing plumbing test
# (spicexplorer/tests/test_layout_backend.py) fakes `strip_mim_for_pex` entirely, so it asserts the
# argument ARRIVES and passes identically either way — these assert the EFFECT.

pytest.importorskip("klayout.db")


def _mim_under_topmetal(path: Path) -> None:
    """A 10x10 µm MIM plate with TopMetal1 covering exactly the same area."""
    import klayout.db as db

    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("TOP")
    top.shapes(ly.layer(36, 0)).insert(db.Box(0, 0, 10000, 10000))
    top.shapes(ly.layer(126, 0)).insert(db.Box(0, 0, 10000, 10000))
    ly.write(str(path))


def _topmetal_area_um2(path: Path) -> float:
    import klayout.db as db

    ly = db.Layout()
    ly.read(str(path))
    region = db.Region(ly.top_cell().begin_shapes_rec(ly.layer(126, 0))).merged()
    return region.area() * ly.dbu * ly.dbu


def test_topmetal_margin_none_keeps_the_plates(tmp_path: Path):
    from spicexplorer_signoff.pex import strip_mim_for_pex

    src = tmp_path / "in.gds"
    _mim_under_topmetal(src)
    assert _topmetal_area_um2(src) == pytest.approx(100.0)

    kept = tmp_path / "kept.gds"
    strip_mim_for_pex(src, kept, topmetal_margin_um=None)
    assert _topmetal_area_um2(kept) == pytest.approx(100.0), (
        "the documented spelling for keeping the top plates cut them back anyway"
    )


def test_the_default_and_an_explicit_margin_still_cut_back(tmp_path: Path):
    from spicexplorer_signoff.pex import strip_mim_for_pex

    src = tmp_path / "in.gds"
    _mim_under_topmetal(src)
    cases: tuple[tuple[str, dict[str, Any]], ...] = (
        ("default", {}),
        ("explicit", {"topmetal_margin_um": 0.2}),
    )
    for name, kw in cases:
        out = tmp_path / f"{name}.gds"
        strip_mim_for_pex(src, out, **kw)
        assert _topmetal_area_um2(out) == pytest.approx(0.0), f"{name} stopped cutting back"


def test_the_two_spellings_agree(tmp_path: Path):
    """`margin_um=None` was the only one that worked; both must now mean the same thing."""
    from spicexplorer_signoff.pex import strip_mim_for_pex

    src = tmp_path / "in.gds"
    _mim_under_topmetal(src)
    a, b = tmp_path / "alias.gds", tmp_path / "direct.gds"
    strip_mim_for_pex(src, a, topmetal_margin_um=None)
    strip_mim_for_pex(src, b, margin_um=None)
    assert _topmetal_area_um2(a) == _topmetal_area_um2(b)


def test_the_alias_still_wins_over_margin_um(tmp_path: Path):
    """Documented precedence: the alias wins when given, including when given as None."""
    from spicexplorer_signoff.pex import strip_mim_for_pex

    src = tmp_path / "in.gds"
    _mim_under_topmetal(src)
    out = tmp_path / "wins.gds"
    strip_mim_for_pex(src, out, margin_um=0.2, topmetal_margin_um=None)
    assert _topmetal_area_um2(out) == pytest.approx(100.0)


# ----------------------------------------------------------------------
# SIGN-01 — a positive verdict is necessary but not sufficient
# ----------------------------------------------------------------------
# The existing tests above harden one direction: "exits 0 having said nothing is not a pass". The
# mirror was uncovered — a runner that PRINTS the verdict and then dies still passed, because the
# exit status is ignored. Ignoring it is deliberate and correct (a deck that dies early exits 0
# often enough that trusting the status reported a silent PASS), so the fix ADDS conditions rather
# than swapping to an rc check: a pass now needs the verdict AND a clean exit AND artifacts from
# this run that actually parsed.


def test_drc_verdict_with_a_dirty_exit_is_not_a_pass(crashing_pdk, tmp_path):
    """`rc=7` + "DRC Check Passed" used to return passed=True."""
    from spicexplorer_signoff.drc import run_drc

    crashing_pdk.drc_runner.write_text("import sys\nprint('DRC Check Passed')\nsys.exit(7)\n")
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert r.available and not r.passed, "a runner that printed the verdict and then died passed"
    assert "7" in r.reason


def test_lvs_verdict_with_a_dirty_exit_is_not_a_pass(crashing_pdk, tmp_path):
    """`rc=7` + "Netlists match" used to return passed=True AND a reason saying it failed —
    the record contradicted itself."""
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.lvs_runner.write_text(
        "import sys, pathlib\n"
        "pathlib.Path('cell.log').write_text('Netlists match\\n')\n"
        "print('Netlists match')\n"
        "sys.exit(7)\n"
    )
    r = run_lvs(
        tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", tmp_path / "run", pdk=crashing_pdk
    )
    assert r.available and not r.passed
    assert r.reason, "a failing result with an empty reason tells the reviewer nothing"


def test_a_result_never_says_passed_and_carries_a_failure_reason(crashing_pdk, tmp_path):
    """The invariant behind SIGN-01, stated directly: passed and reason are mutually exclusive."""
    from spicexplorer_signoff.drc import run_drc
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.drc_runner.write_text("import sys\nprint('DRC Check Passed')\nsys.exit(7)\n")
    d = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert not (d.passed and d.reason)

    crashing_pdk.lvs_runner.write_text(
        "import sys, pathlib\n"
        "pathlib.Path('cell.log').write_text('Netlists match\\n')\n"
        "sys.exit(7)\n"
    )
    lv = run_lvs(
        tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", tmp_path / "run2", pdk=crashing_pdk
    )
    assert not (lv.passed and lv.reason)


def test_drc_an_unparseable_report_from_this_run_is_not_a_clean_cell(crashing_pdk, tmp_path):
    """A marker plus a corrupt .lyrdb used to give passed=True, n_violations=0.

    The parse error was swallowed into `viol = []`, which is indistinguishable from "no
    violations" — a truncated report is precisely when you must not report a clean cell.
    """
    from spicexplorer_signoff.drc import run_drc

    crashing_pdk.drc_runner.write_text(
        "import pathlib\n"
        "pathlib.Path('cell_full.lyrdb').write_text('<report><items><item>truncated')\n"
        "print('DRC Check Passed')\n"
    )
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert r.available and not r.passed, "an unparseable report was reported as a clean cell"
    assert "pars" in r.reason.lower()


def test_a_genuinely_clean_drc_run_still_passes(crashing_pdk, tmp_path):
    """The must-not-regress half: verdict, exit 0, no report at all is a legitimate clean run."""
    from spicexplorer_signoff.drc import run_drc

    crashing_pdk.drc_runner.write_text("print('DRC Check Passed')\n")
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=crashing_pdk)
    assert r.passed and r.n_violations == 0 and not r.reason


def test_a_genuinely_clean_lvs_run_still_passes(crashing_pdk, tmp_path):
    from spicexplorer_signoff.lvs import run_lvs

    crashing_pdk.lvs_runner.write_text(
        "import pathlib\npathlib.Path('cell.log').write_text('Netlists match\\n')\n"
    )
    r = run_lvs(
        tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", tmp_path / "run", pdk=crashing_pdk
    )
    assert r.passed and r.matched and not r.reason
