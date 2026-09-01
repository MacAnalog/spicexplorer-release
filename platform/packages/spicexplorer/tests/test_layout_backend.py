"""Layout-flow backend (`sim_engine: layout`) — OFFLINE tests.

A fake generator file (introspected via ast) + monkeypatched leaf-tool runners (GdsBuilder /
run_drc / run_lvs / run_pex) stand in for gdsfactory, KLayout and kpex, so this pins — with no
tool installed —

* the DSL: `SimType.LAYOUT` survives `TargetSpec` coercion (`get_analysis()` == "layout"),
  `Project_Setup.from_yaml` accepts `sim_engine: layout`, the factory dispatches to
  `LayoutSimulator` (and rejects a non-YAML "netlist" actionably);
* the flow spec loader (`layout-flow/1`) + knob casting (ints, bools, 0.01 grid, unknown knob);
* the gate/NaN semantics (DRC fail → LVS/PEX/measure NaN while area still scores; LVS
  mismatch → PEX/measure NaN; measure scalars merged on a clean run);
* `scalar`/`log_path`/`submit`+`collect`, the parasitic-scalar and PEX-subckt helpers;
* the whole optimizer loop end-to-end through the orchestrator (`seed_from_init` puts the
  `init` point first; the layout backend's summary.json is the trial's log_file).

The live counterpart (real 5T OTA generator + tools) is `test_layout_backend_live.py` (slow).
"""

from __future__ import annotations

import json
import math
import sys
import textwrap
from pathlib import Path

import numpy as np
import pytest
import yaml
from spicexplorer.backends import layout as layout_mod
from spicexplorer.backends.layout import (
    LayoutFlowSpec,
    LayoutSimResult,
    LayoutSimulator,
    create_layout_simulator,
    parasitic_scalars,
    prepare_pex_subckt,
    snap_to_grid,
)
from spicexplorer.core.domains import Project_Setup, SimType, SpiceSimulatorType, TargetSpec
from spicexplorer.optimization.simulator_factory import (
    SIMULATOR_BUILDERS,
    build_simulator,
    resolve_engine,
)

FAKE_GEN = textwrap.dedent(
    '''
    """A fake generator: the contract's LayoutParams/BOUNDS/build, never built offline."""
    from dataclasses import dataclass

    @dataclass
    class LayoutParams:
        gap_x: float = 1.0
        ch_y: float = 2.0
        n_cols: int = 2
        mirror: bool = True
        mode: str = "a"

    BOUNDS = {"gap_x": (0.5, 2.0), "ch_y": (1.0, 4.0), "n_cols": (1, 4),
              "mirror": (False, True), "mode": ("a", "b")}

    def build(p=LayoutParams(), sizing=None):
        raise RuntimeError("the fake generator is never built in-process")

    def write_lvs_reference(p, out=None):
        open(out, "w").write(".subckt cell a b\\nM1 a b 0 0 nmos w=1u l=1u\\nC1 a 0 1f\\n.ends\\n")
        return out

    def write_pex_schematic(p, out=None, sizing=None):
        # kpex flavour (3-terminal R) — differs from the LVS reference on purpose
        open(out, "w").write(".subckt cell a b\\nM1 a b 0 0 nmos w=1u l=1u\\nR1 a b 0 rsil w=1u l=1u\\nC1 a 0 1f\\n.ends\\n")
        return out
    '''
)

FAKE_MEASURE = textwrap.dedent(
    """
    def measure(req):
        p = req["params"]
        out = {"ugf_mhz": 10.0 * p["gap_x"], "pm_deg": 60.0, "corner_temp": (req.get("corner") or {}).get("temp", -1)}
        # co-optimization: the hook sees the candidate's sizing + bench-only deck params
        out["sizing_in_w"] = float((req.get("sizing") or {}).get("in_w", -1))
        out["deck_tail_ma"] = float((req.get("deck_params") or {}).get("tail_ma", -1))
        if req.get("extra", {}).get("fail"):
            raise RuntimeError("bench blew up")
        return out
    """
)


# ---------------------------------------------------------------------------
# fakes for the leaf tools
# ---------------------------------------------------------------------------
class _State:
    """Per-test switches the fake runners read."""

    def __init__(self):
        self.drc_pass = True
        self.lvs_match = True
        self.pex_ok = True
        self.calls: list[str] = []


def _install_fakes(monkeypatch, state: _State):
    import spicexplorer_layout
    import spicexplorer_signoff
    from spicexplorer_layout.gen import GdsBuild
    from spicexplorer_signoff.results import DrcResult, DrcViolation, LvsResult, PexResult

    class FakeBuilder:
        def __init__(self, gen_path, out_dir, *, cell=None, sizing_json=None, inproc=False, python=None):
            self.out_dir = Path(out_dir)
            self.cell = cell or "cell"
            self.python = python
            self.last = None

        def __call__(self, params):
            state.calls.append("build")
            self.out_dir.mkdir(parents=True, exist_ok=True)
            gds = self.out_dir / f"{self.cell}.gds"
            gds.write_bytes(b"GDS")
            w, h = 10.0 * float(params.get("gap_x", 1.0)), 5.0 * float(params.get("ch_y", 2.0))
            self.last = GdsBuild(str(gds), self.cell, dict(params), (0.0, 0.0, w, h), w * h, "deadbeef")
            return gds

    def fake_drc(gds, topcell, run_dir, **kw):
        state.calls.append("drc")
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        if state.drc_pass:
            return DrcResult(True, True, 0, [], report_path=str(Path(run_dir) / "r.lyrdb"))
        return DrcResult(False, True, 3, [DrcViolation("M1.a", 3)], report_path=str(Path(run_dir) / "r.lyrdb"))

    def fake_lvs(gds, netlist, topcell, run_dir, **kw):
        state.calls.append("lvs")
        assert Path(netlist).is_file(), "the LVS reference must exist (writer ran)"
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        return LvsResult(state.lvs_match, True, matched=state.lvs_match, netlist_path=str(netlist))

    def fake_pex(gds, cell, schematic, out_dir, *, mode="CC", **kw):
        state.calls.append("pex")
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        if not state.pex_ok:
            return PexResult(False, True, mode, reason="kpex exited 1")
        net = out_dir / f"{cell}_k25d_pex_netlist.spice"
        net.write_text(
            f".subckt {cell} a b\n+ VSS\nM1 a b VSS VSS sg13_lv_nmos w=1u l=1u\n"
            "C1 a VSS 1.5f\nC2 a b 0.5f\nC3 b VSUBS 2f\nC4 VSS VSS 9f\n.ends\n"
        )
        return PexResult(True, True, mode, netlist_path=str(net), n_c=4, n_r=0,
                         per_net_c_ff={"a": 2.0, "b": 2.5}, coupling_ff={"a|b": 0.5, "VSS|a": 1.5, "VSUBS|b": 2.0})

    monkeypatch.setattr(spicexplorer_layout, "GdsBuilder", FakeBuilder)
    monkeypatch.setattr(spicexplorer_signoff, "run_drc", fake_drc)
    monkeypatch.setattr(spicexplorer_signoff, "run_lvs", fake_lvs)
    monkeypatch.setattr(spicexplorer_signoff, "run_pex", fake_pex)


def _write_flow(tmp_path: Path, *, lvs="writer", measure=True, extra=None, ac_gnd=None) -> Path:
    gen = tmp_path / "gen_fake.py"
    gen.write_text(FAKE_GEN)
    (tmp_path / "measure_fake.py").write_text(FAKE_MEASURE)
    ref = tmp_path / "ref.sp"
    ref.write_text(".subckt cell a b\n.ends\n")
    spec = {
        "schema": "layout-flow/1",
        "generator": "gen_fake.py",
        "cell": "cell",
        "gds_python": sys.executable,
        "fixed_params": {"mode": "b"},
        "drc": {"enabled": True},
        "lvs": {"writer": "write_lvs_reference"} if lvs == "writer" else {"reference": "ref.sp"},
        "pex": {"mode": "CC", "ports": "a b", **({"ac_gnd_nets": ac_gnd} if ac_gnd else {})},
    }
    if measure:
        spec["measure"] = {"module": "measure_fake.py", "callable": "measure", "python": sys.executable,
                           "extra": extra or {}}
    p = tmp_path / "flow.yaml"
    p.write_text(yaml.safe_dump(spec))
    return p


# ---------------------------------------------------------------------------
# DSL: enums, TargetSpec coercion, Project_Setup, factory
# ---------------------------------------------------------------------------
def test_layout_enums_and_target_spec_coercion():
    assert SimType("layout") is SimType.LAYOUT
    assert SpiceSimulatorType("layout") is SpiceSimulatorType.LAYOUT
    assert resolve_engine("layout") is SpiceSimulatorType.LAYOUT
    assert SpiceSimulatorType.LAYOUT in SIMULATOR_BUILDERS
    spec = TargetSpec(name="area_um2", testbench="layout", target=100.0, goal="minimize", sim_type="layout")
    assert spec.sim_type is SimType.LAYOUT
    assert spec.get_analysis() == "layout"
    with pytest.raises(ValueError):
        spec.get_equivalent_ngspice_plot_type()
    # the other sim types are untouched by the carve-out
    ac = TargetSpec(name="ugf", testbench="tb", target=1.0, goal="exceed", sim_type="ac")
    assert ac.get_analysis() == "ac"


def test_factory_rejects_non_yaml_flow_spec(tmp_path: Path):
    deck = tmp_path / "dut.spice"
    deck.write_text("* not a flow spec\n")
    with pytest.raises(NotImplementedError, match="layout-flow"):
        build_simulator("layout", netlist_filename=deck, output_folder=tmp_path)


def test_factory_builds_layout_simulator(tmp_path: Path, monkeypatch):
    _install_fakes(monkeypatch, _State())
    flow = _write_flow(tmp_path)
    sim = build_simulator("layout", netlist_filename=flow, testbench_name="lay", output_folder=tmp_path / "out")
    assert isinstance(sim, LayoutSimulator)
    assert sim.output_folder == (tmp_path / "out" / "layout" / "lay").resolve()
    from spicexplorer_core.spice_engine import Simulator

    assert isinstance(sim, Simulator)  # runtime_checkable protocol


# ---------------------------------------------------------------------------
# spec loading + knob casting
# ---------------------------------------------------------------------------
def test_flow_spec_loads_and_casts(tmp_path: Path):
    flow = _write_flow(tmp_path)
    spec = LayoutFlowSpec.from_yaml(flow)
    assert spec.cell == "cell" and spec.generator == (tmp_path / "gen_fake.py").resolve()
    assert spec.param_defaults == {"gap_x": 1.0, "ch_y": 2.0, "n_cols": 2, "mirror": True, "mode": "a"}
    assert spec.bounds["gap_x"] == (0.5, 2.0)
    assert spec.lvs is not None and spec.lvs.writer == "write_lvs_reference"
    assert spec.pex is not None and spec.pex.ports == "a b"
    cast = spec.cast_params({"gap_x": 1.23456, "n_cols": 2.6, "mirror": 0, "ch_y": np.float64(3.004)})
    assert cast == {"gap_x": 1.23, "n_cols": 3, "mirror": False, "ch_y": 3.0}
    with pytest.raises(KeyError, match="not a knob"):
        spec.cast_params({"nope": 1})


def test_flow_spec_errors(tmp_path: Path):
    bad = tmp_path / "flow.yaml"
    bad.write_text(yaml.safe_dump({"schema": "layout-flow/1", "generator": "missing.py", "cell": "c"}))
    with pytest.raises(FileNotFoundError):
        LayoutFlowSpec.from_yaml(bad)
    (tmp_path / "gen_fake.py").write_text(FAKE_GEN)
    bad.write_text(yaml.safe_dump({"schema": "nope/9", "generator": "gen_fake.py", "cell": "c"}))
    with pytest.raises(ValueError, match="schema"):
        LayoutFlowSpec.from_yaml(bad)
    bad.write_text(yaml.safe_dump({"schema": "layout-flow/1", "generator": "gen_fake.py", "cell": "c",
                                   "lvs": {"reference": "x.sp", "writer": "w"}}))
    with pytest.raises(ValueError, match="exactly one"):
        LayoutFlowSpec.from_yaml(bad)
    bad.write_text(yaml.safe_dump({"schema": "layout-flow/1", "generator": "gen_fake.py", "cell": "c",
                                   "fixed_params": {"unknown_knob": 1}}))
    with pytest.raises(ValueError, match="fixed_params"):
        LayoutFlowSpec.from_yaml(bad)
    bad.write_text(yaml.safe_dump({"schema": "layout-flow/1", "generator": "gen_fake.py", "cell": "c",
                                   "pex": {"mode": "CC"}}))
    with pytest.raises(ValueError, match="pex"):
        LayoutFlowSpec.from_yaml(bad)


# ---------------------------------------------------------------------------
# run(): gates + NaN semantics, scalars, log_path, submit/collect
# ---------------------------------------------------------------------------
def _sim(tmp_path, monkeypatch, state, **flow_kw) -> LayoutSimulator:
    _install_fakes(monkeypatch, state)
    flow = _write_flow(tmp_path, **flow_kw)
    return create_layout_simulator(flow, output_folder=tmp_path / "out", testbench_name="layout")


def test_clean_run_scalars_and_log_path(tmp_path: Path, monkeypatch):
    state = _State()
    sim = _sim(tmp_path, monkeypatch, state, ac_gnd=["b"])
    sim.update_params({"gap_x": 1.5, "ch_y": 2.0, "n_cols": 3})
    res = sim.run(label="layout__tt")
    assert isinstance(res, LayoutSimResult)
    assert res.status == "ok"
    assert state.calls == ["build", "drc", "lvs", "pex"]
    assert res.scalar("area_um2", "layout") == pytest.approx(150.0)
    assert res.scalar("width_um", "layout") == pytest.approx(15.0)
    assert res.scalar("drc_pass", "layout") == 1.0 and res.scalar("lvs_match", "layout") == 1.0
    assert res.scalar("pex_ok", "layout") == 1.0 and res.scalar("pex_n_c", "layout") == 4.0
    assert res.scalar("ugf_mhz", "layout") == pytest.approx(15.0)  # measure ran (10 * gap_x)
    assert res.scalar("pm_deg", "layout") == 60.0
    assert math.isnan(res.scalar("no_such_metric", "layout"))
    # per-net C from the fake PexResult: a: 2.0 total, of which 0.5 to b (ac gnd) + 1.5 to VSS
    assert res.scalar("ctot_a_ff", "layout") == pytest.approx(2.0)
    assert res.scalar("c_a__b_ff", "layout") == pytest.approx(0.5)
    assert res.scalar("c_a_ff", "layout") == pytest.approx(2.0)  # C(a→VSS)+C(a→b, b is ac gnd)
    assert res.scalar("c_b_ff", "layout") == pytest.approx(2.0)  # 2.5 total − 0.5 to a (not ac gnd)
    with pytest.raises(NotImplementedError):
        res.wave("x", "layout")
    # log_path = the run's summary.json, under run_<n>_<label>
    assert res.log_path is not None and res.log_path.name == "summary.json"
    assert res.log_path.parent.name == "run_1_layout__tt"
    summary = json.loads(res.log_path.read_text())
    assert summary["status"] == "ok" and summary["params"]["mode"] == "b"  # fixed_params pinned
    assert summary["params"]["n_cols"] == 3
    # the prepared subckt: header rewritten to the ports, VSS→0, 0-0 elements dropped, M→XM
    sub = Path(summary["stages"]["pex"]["subckt"]).read_text()
    assert sub.splitlines()[0] == ".subckt cell a b"
    assert "XM1 a b 0 0" in sub and "C4" not in sub and "VSUBS" not in sub


def test_drc_failure_gates_downstream_but_area_scores(tmp_path: Path, monkeypatch):
    state = _State()
    state.drc_pass = False
    sim = _sim(tmp_path, monkeypatch, state)
    sim.update_params({"gap_x": 1.0, "ch_y": 1.0})
    res = sim.run()
    assert res.status == "drc_fail"
    assert state.calls == ["build", "drc"]
    assert res.scalar("area_um2", "layout") == pytest.approx(50.0)  # still scores
    assert res.scalar("drc_pass", "layout") == 0.0 and res.scalar("drc_violations", "layout") == 3.0
    for k in ("lvs_match", "pex_ok", "c_a_ff", "ugf_mhz"):
        assert math.isnan(res.scalar(k, "layout")), k
    assert res.log_path is not None and res.log_path.parent.name == "run_1_layout"


def test_lvs_mismatch_gates_pex_and_measure(tmp_path: Path, monkeypatch):
    state = _State()
    state.lvs_match = False
    sim = _sim(tmp_path, monkeypatch, state)
    sim.update_params({"gap_x": 1.0})
    res = sim.run()
    assert res.status == "lvs_fail" and state.calls == ["build", "drc", "lvs"]
    assert res.scalar("drc_pass", "layout") == 1.0 and res.scalar("lvs_match", "layout") == 0.0
    assert math.isnan(res.scalar("pex_ok", "layout")) and math.isnan(res.scalar("ugf_mhz", "layout"))


def test_pex_failure_and_measure_error_never_raise(tmp_path: Path, monkeypatch):
    state = _State()
    state.pex_ok = False
    sim = _sim(tmp_path, monkeypatch, state)
    sim.update_params({"gap_x": 1.0})
    res = sim.run()
    assert res.status == "pex_fail" and res.scalar("pex_ok", "layout") == 0.0
    assert math.isnan(res.scalar("ugf_mhz", "layout"))
    # a bench that raises → status measure_fail, its scalars NaN, everything upstream intact
    state2 = _State()
    (tmp_path / "b").mkdir()
    sim2 = _sim(tmp_path / "b", monkeypatch, state2, extra={"fail": True})
    sim2.update_params({"gap_x": 1.0})
    res2 = sim2.run()
    assert res2.status == "measure_fail"
    assert res2.scalar("pex_ok", "layout") == 1.0 and math.isnan(res2.scalar("ugf_mhz", "layout"))


def test_gates_off_keeps_going(tmp_path: Path, monkeypatch):
    state = _State()
    state.drc_pass = False
    _install_fakes(monkeypatch, state)
    flow = _write_flow(tmp_path)
    d = yaml.safe_load(flow.read_text())
    d["gates"] = {"drc": False}
    flow.write_text(yaml.safe_dump(d))
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out")
    sim.update_params({"gap_x": 1.0})
    res = sim.run()
    assert res.status == "drc_fail"  # still reported…
    assert state.calls == ["build", "drc", "lvs", "pex"]  # …but not blocking
    assert res.scalar("lvs_match", "layout") == 1.0 and res.scalar("ugf_mhz", "layout") == 10.0


def test_submit_collect_and_corner_forwarding(tmp_path: Path, monkeypatch):
    from spicexplorer_core.pvt import Corner

    state = _State()
    sim = _sim(tmp_path, monkeypatch, state)
    sim.update_params({"gap_x": 2.0})
    sim.apply_corner(Corner(name="hot", temp=85.0))
    h1 = sim.submit(label="layout__hot")
    h2 = sim.submit(label="layout__hot")
    r1, r2 = sim.collect(h1), h2.result()
    assert h1.is_done() and h2.is_done()
    assert {r1.log_path.parent.name, r2.log_path.parent.name} == {"run_1_layout__hot", "run_2_layout__hot"}  # type: ignore[union-attr]
    assert r1.scalar("corner_temp", "layout") == 85.0  # the corner reached the bench
    assert json.loads(r1.log_path.read_text())["corner"]["name"] == "hot"  # type: ignore[union-attr]
    sim.close()


def test_unknown_knob_raises_at_update_params(tmp_path: Path, monkeypatch):
    # no `postlayout`/`measure` stage to forward a bench-only param to → a typo is an error
    sim = _sim(tmp_path, monkeypatch, _State(), measure=False)
    with pytest.raises(KeyError, match="not knobs"):
        sim.update_params({"typo_knob": 1.0})


def test_measure_flow_accepts_bench_only_params_and_forwards_sizing(tmp_path: Path, monkeypatch):
    """A `measure:` flow (no `postlayout:`) may carry dut_params that are neither knobs nor
    sizing keys (bias currents/voltages the block's benches take): they reach the hook as
    `deck_params`; the merged sizing reaches it as `sizing`."""
    state = _State()
    _install_fakes(monkeypatch, state)
    flow = _write_flow(tmp_path)
    (tmp_path / "sizing.json").write_text(json.dumps({"in_w": 1e-6, "tail_w": 2e-6}))
    d = yaml.safe_load(flow.read_text())
    d["sizing"] = "sizing.json"
    d["sizing_params"] = ["in_w"]
    flow.write_text(yaml.safe_dump(d))
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out")
    sim.update_params({"gap_x": 1.5, "in_w": 3e-6, "tail_ma": 15.0})  # knob + sizing + bench-only
    res = sim.run()
    assert res.status == "ok", res.summary["error"]
    assert res.scalar("sizing_in_w", "layout") == 3e-6
    assert res.scalar("deck_tail_ma", "layout") == 15.0
    assert res.summary["deck_params"] == {"tail_ma": 15.0}
    assert res.summary["sizing"] == {"in_w": 3e-6} and "tail_ma" not in res.summary["params"]
    # …but a flow with neither postlayout nor measure still rejects them
    d.pop("measure")
    flow.write_text(yaml.safe_dump(d))
    sim2 = create_layout_simulator(flow, output_folder=tmp_path / "out2")
    with pytest.raises(KeyError, match="not knobs"):
        sim2.update_params({"tail_ma": 15.0})


def test_pex_schematic_writer_and_strip_mim_options(tmp_path: Path, monkeypatch):
    """`pex.schematic_writer` hands kpex a per-trial schematic written by the generator (the
    3-terminal-R flavour) instead of the LVS reference; `strip_mim_layers` /
    `strip_mim_topmetal_margin_um` reach `strip_mim_for_pex`."""
    import spicexplorer_signoff

    state = _State()
    _install_fakes(monkeypatch, state)
    seen: dict = {}

    def fake_strip(gds_in, gds_out, **kw):
        seen.update(kw)
        Path(gds_out).write_bytes(b"GDS-nomim")
        return Path(gds_out)

    monkeypatch.setattr(spicexplorer_signoff.pex, "strip_mim_for_pex", fake_strip)
    real_pex = spicexplorer_signoff.run_pex

    def spy_pex(gds, cell, schematic, out_dir, **kw):
        seen["schematic"] = Path(schematic).read_text()
        seen["gds"] = Path(gds).name
        seen["halo_um"] = kw.get("halo_um")
        return real_pex(gds, cell, schematic, out_dir, **kw)

    monkeypatch.setattr(spicexplorer_signoff, "run_pex", spy_pex)
    flow = _write_flow(tmp_path)
    d = yaml.safe_load(flow.read_text())
    d["pex"].update({"schematic_writer": "write_pex_schematic", "strip_mim": True,
                     "strip_mim_layers": [[36, 0], [129, 0], [69, 0]], "strip_mim_topmetal_margin_um": None,
                     "halo_um": 20})
    flow.write_text(yaml.safe_dump(d))
    spec = LayoutFlowSpec.from_yaml(flow)
    assert spec.pex is not None and spec.pex.schematic_writer == "write_pex_schematic"
    assert spec.pex.strip_mim_layers == ((36, 0), (129, 0), (69, 0)) and spec.pex.strip_mim_topmetal_margin_um is None
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out")
    sim.update_params({"gap_x": 1.0})
    res = sim.run()
    assert res.status == "ok", res.summary["error"]
    assert "rsil" in seen["schematic"] and "C1" not in seen["schematic"]  # writer's flavour, C cards stripped
    assert seen["gds"].endswith("_nomim.gds")
    assert seen["layers"] == ((36, 0), (129, 0), (69, 0)) and seen["topmetal_margin_um"] is None
    assert spec.pex.halo_um == 20.0 and seen["halo_um"] == 20.0  # kpex --halo forwarded
    # schematic + schematic_writer together is a load error
    d["pex"]["schematic"] = "ref.sp"
    flow.write_text(yaml.safe_dump(d))
    with pytest.raises(ValueError, match="OR"):
        LayoutFlowSpec.from_yaml(flow)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def test_parasitic_scalars_ac_ground_math():
    per = {"net2": 33.0, "vdd": 5.0, "VSUBS": 40.0}
    coup = {"net2|vdd": 3.0, "net2|vout": 2.0, "VSUBS|net2": 4.0}
    s = parasitic_scalars(per, coup)  # no ac_gnd_nets → c_ == ctot_
    assert s["c_net2_ff"] == 33.0 == s["ctot_net2_ff"] and s["c_net2__vdd_ff"] == 3.0
    assert "c_VSUBS_ff" not in s and s["ctot_VSUBS_ff"] == 40.0
    s = parasitic_scalars(per, coup, ac_gnd_nets=["vdd"])
    # to node 0: 33 − (3+2+4) = 24; + VSUBS 4 + vdd 3 = 31 (vout is NOT ac ground)
    assert s["c_net2_ff"] == pytest.approx(31.0) and s["ctot_net2_ff"] == 33.0


def test_prepare_pex_subckt_reinserts_schematic_cards(tmp_path: Path):
    from spicexplorer_signoff.postlayout import prep_pex_subckt

    raw = ".subckt lpf_core a\n+ b VSS\nM1 a b VSS VSS nmos\nR1 VSS VSUBS 1\nC1 a 0 1f\n.ends lpf_core\n"
    cards = tmp_path / "core.sp"
    cards.write_text("* schematic\nxc1 a b cap_cmim w=1u l=1u\nXC2 b a cap_cmim\nR9 a b 1k\n")
    out = prepare_pex_subckt(raw, "lpf_core", prep_pex_subckt, ports="a b", cards_from=cards)
    lines = out.splitlines()
    assert lines[0] == ".subckt lpf_core a b"
    assert "XM1 a b 0 0 nmos" in lines and "R1 0 0 1" not in out
    assert lines[-3:] == ["xc1 a b cap_cmim w=1u l=1u", "XC2 b a cap_cmim", ".ends lpf_core"]
    # without ports/cards it is exactly the M→XM prep
    assert prepare_pex_subckt(raw, "lpf_core", prep_pex_subckt) == prep_pex_subckt(raw, "lpf_core")


def test_measure_protocol_roundtrip():
    import io

    from spicexplorer_layout.measure_protocol import RESULT_MARK, parse_result, write_result

    buf = io.StringIO()
    write_result({"a": 1.5, "b": float("nan"), "c": "x"}, stream=buf)
    line = buf.getvalue()
    assert line.startswith(RESULT_MARK)
    d = parse_result("noise\n" + line + "more noise\n")
    assert d == {"scalars": {"a": 1.5, "b": None, "c": None}, "status": "ok"}
    assert parse_result("nothing here") is None
    assert parse_result('{"scalars": {"z": 2}}') == {"scalars": {"z": 2}}  # bare-JSON tolerance


# ---------------------------------------------------------------------------
# end-to-end: the optimizer loop through the orchestrator (offline)
# ---------------------------------------------------------------------------
def _project_yaml(tmp_path: Path, flow: Path) -> Path:
    doc = {
        "project": {
            "name": "FAKE-LAYOUT",
            "description": "offline layout-flow project",
            "simulator": "none",
            "save_sim": False,
            "parallel_sim": True,
            "sim_engine": "layout",
            "ws_root": ".",
            "netlist": flow.name,
            "outdir": "out",
            "tech_spec": {"name": "fake", "constraints": {}},
            "dut_params": [
                {"name": "gap_x", "min_val": 0.5, "max_val": 2.0, "init": 1.25},
                {"name": "ch_y", "min_val": 1.0, "max_val": 4.0, "init": 2.5},
                {"name": "n_cols", "min_val": 1, "max_val": 4, "init": 3, "is_integer": True},
            ],
            "testbenches": [{"name": "layout", "netlist": flow.name, "params": [], "enable": True}],
            "optimizer_config": {
                "type": "nevergrad",
                "name": "TwoPointsDE",
                "budget": 2,
                "random_seed": 1,
                "seed_from_init": True,
                "optimizer_kwargs": {"num_workers": 1},
                "lin_variable_bounds": {"min": 0, "max": 1},
                "log_variable_bounds": {"min": 1, "max": 100},
                "target_specs": [
                    {"name": "area_um2", "testbench": "layout", "sim_type": "layout", "goal": "minimize",
                     "target": 200, "range": 100, "tolerance": 0, "weight": 1, "reward_type": "relative-log"},
                    {"name": "ugf_mhz", "testbench": "layout", "sim_type": "layout", "goal": "exceed",
                     "target": 5.0, "range": 5, "tolerance": 0, "weight": 1, "reward_type": "none"},
                    {"name": "c_a_ff", "testbench": "layout", "sim_type": "layout", "goal": "minimize",
                     "target": 3.0, "range": 1, "tolerance": 0, "weight": 1, "reward_type": "none"},
                    {"name": "drc_pass", "testbench": "layout", "sim_type": "layout", "goal": "exact",
                     "target": 1, "range": 1, "tolerance": 0, "weight": 10, "reward_type": "none"},
                ],
            },
        }
    }
    p = tmp_path / "project_setup.yaml"
    p.write_text(yaml.safe_dump(doc))
    return p


def test_project_setup_from_yaml_accepts_layout_engine(tmp_path: Path):
    flow = _write_flow(tmp_path)
    p = Project_Setup.from_yaml(_project_yaml(tmp_path, flow))
    assert p.sim_engine == "layout"
    assert all(t.get_analysis() == "layout" for t in p.optimizer_config.target_specs.targets)
    assert p.optimizer_config.seed_from_init is True


def test_orchestrator_runs_layout_flow_end_to_end(tmp_path: Path, monkeypatch):
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    state = _State()
    _install_fakes(monkeypatch, state)
    flow = _write_flow(tmp_path)
    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=_project_yaml(tmp_path, flow), optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE
    )
    sims = orch.get_spicelib_wrapper()
    assert set(sims) == {"layout"} and isinstance(sims["layout"], LayoutSimulator)
    opt = orch.get_optimizer()
    opt.disable_autosave = True
    opt.autosave_checkpoint_dir = tmp_path / "ckpt"
    opt.parameterize()
    opt.optimize(render_optimization_trace=False, keep_history=False)
    log = opt.optimization_log
    assert len(log) == 2
    # trial 0 = the `init` point (seed_from_init), on the 0.01 grid, ints cast
    first = log[0].get_params()
    assert first["gap_x"] == pytest.approx(1.25, abs=1e-9) and first["n_cols"] == 3
    fs = log[0].get_fit_summary()
    assert fs["area_um2"]["curr_val"] == pytest.approx(10 * 1.25 * 5 * 2.5)
    assert fs["ugf_mhz"]["curr_val"] == pytest.approx(12.5) and fs["drc_pass"]["curr_val"] == 1.0
    assert fs["c_a_ff"]["curr_val"] == pytest.approx(2.0)
    # the layout run's summary.json is the trial's log_file
    lf = log[0].log_file
    assert lf and Path(next(iter(lf.values()))).name == "summary.json"
    assert state.calls.count("build") == 2


def test_lazy_extra_import_error_is_actionable(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name.startswith("spicexplorer_layout") or name.startswith("spicexplorer_signoff"):
            raise ImportError("simulated missing extra")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match="uv sync --extra layout"):
        layout_mod._import_leaf_tools()


# ---------------------------------------------------------------------------
# postlayout: platform testbenches on the extracted subckt (fake ngspice) + delegation
# ---------------------------------------------------------------------------
FAKE_DUT = ".subckt cell a b vss\nXM1 a b vss vss nmos w=1u l=1u\n.ends\n"
FAKE_TB_INCLUDE = "* bench\n.lib cornerMOSlv.lib mos_tt\n.include dut.spice\n.param W1 = 1u\nV1 a 0 1\nXDUT a b 0 cell\n.ac dec 10 1 1e6\n.end\n"
FAKE_TB_INLINE = "* bench\nV1 a 0 1\n.subckt cell a b vss\nXM1 a b vss vss nmos w=1u l=1u\n.ends cell\nXDUT a b 0 cell\n.ac dec 10 1 1e6\n.end\n"


class _FakeNgspiceResult:
    """A NgspiceSimResult stand-in: op scalars + an AC transfer with a known UGF/PM."""

    def __init__(self, tag: str, params: dict):
        self.raw = object()  # not None → "produced a RAW"
        self.log_path = f"/fake/{tag}.log"
        self.raw_path = f"/fake/{tag}.raw"
        self._merged: dict[str, float] = {}
        self.params = dict(params)
        self.tag = tag

    def merge_scalars(self, scalars):
        self._merged.update({k: float(v) for k, v in scalars.items()})

    def scalar(self, name, analysis, is_real=True):
        if name in self._merged:
            return self._merged[name]
        if analysis == "op" and name == "v(vout)":
            return 0.6
        if analysis == "op" and name == "i(vdd)":
            return -2.7e-5 if self.tag == "tb_ac" else -1e-6
        return float("nan")

    def wave(self, name, analysis, is_real=False):
        if analysis != "ac":
            raise RuntimeError("no such plot")
        f = np.logspace(0, 8, 400)
        if name == "frequency":
            return f
        if name == "v(vout)":
            # single-pole 100 V/V amp, pole at 100 kHz → ugf ≈ 10 MHz, pm ≈ 90°
            return 100.0 / (1 + 1j * f / 1e5)
        raise IndexError(name)


def _install_fake_ngspice(monkeypatch, calls: list):
    import spicexplorer.optimization.simulator_factory as fac

    class FakeNgspice:
        def __init__(self, netlist_filename, testbench_name, output_folder, **kw):
            self.deck = Path(netlist_filename)
            self.tb = testbench_name
            self.params: dict = {}
            self.corner = None
            calls.append(("build", testbench_name, str(self.deck)))

        def update_params(self, params):
            self.params.update(params)
            calls.append(("params", self.tb, dict(params)))
            return True

        def apply_corner(self, corner, model_lib_root=None):
            self.corner = corner
            calls.append(("corner", self.tb, getattr(corner, "name", None)))

        def run(self, label=None, **kw):
            calls.append(("run", self.tb, label))
            return _FakeNgspiceResult(self.tb, self.params)

    real = fac.build_simulator

    def fake_build(engine, **kw):
        if str(getattr(engine, "value", engine)).lower() == "ngspice":
            return FakeNgspice(**kw)
        return real(engine, **kw)

    monkeypatch.setattr(fac, "build_simulator", fake_build)


def _write_flow_postlayout(tmp_path: Path, *, inline=False, two_tbs=False, ground_nets=None) -> Path:
    flow = _write_flow(tmp_path, measure=False)
    (tmp_path / "dut.spice").write_text(FAKE_DUT)
    (tmp_path / "tb_ac.spice").write_text(FAKE_TB_INLINE if inline else FAKE_TB_INCLUDE)
    (tmp_path / "tb_op.spice").write_text(FAKE_TB_INCLUDE)
    d = yaml.safe_load(flow.read_text())
    d["postlayout"] = {
        "dut": "dut.spice",
        "subckt": "cell",
        "testbenches": [{"name": "tb_ac", "netlist": "tb_ac.spice"}] + ([{"name": "tb_op", "netlist": "tb_op.spice"}] if two_tbs else []),
        "params": {"W1": 2e-6},
        **({"ground_nets": ground_nets} if ground_nets else {}),
    }
    flow.write_text(yaml.safe_dump(d))
    return flow


def test_postlayout_spec_validation(tmp_path: Path):
    flow = _write_flow_postlayout(tmp_path)
    spec = LayoutFlowSpec.from_yaml(flow)
    assert spec.postlayout is not None and spec.postlayout.dut_ports == ["a", "b", "vss"]
    # a deck that references the DUT neither way is a load-time config error
    (tmp_path / "tb_ac.spice").write_text("* no dut here\nV1 a 0 1\n.end\n")
    with pytest.raises(ValueError, match="cannot swap the DUT"):
        LayoutFlowSpec.from_yaml(flow)
    # a DUT without the subckt
    (tmp_path / "tb_ac.spice").write_text(FAKE_TB_INCLUDE)
    (tmp_path / "dut.spice").write_text(".subckt other a b\n.ends\n")
    with pytest.raises(ValueError, match="no `.subckt cell`"):
        LayoutFlowSpec.from_yaml(flow)
    # pin-set mismatch between the LVS reference and the DUT is caught at load
    (tmp_path / "dut.spice").write_text(FAKE_DUT)
    d = yaml.safe_load(flow.read_text())
    d["lvs"] = {"reference": "ref.sp"}  # ref.sp: `.subckt cell a b` (no vss)
    flow.write_text(yaml.safe_dump(d))
    with pytest.raises(ValueError, match="pin set"):
        LayoutFlowSpec.from_yaml(flow)


def test_swap_dut_reference_include_and_inline(tmp_path: Path):
    from spicexplorer.backends.layout import swap_dut_reference

    dut = tmp_path / "dut.spice"
    dut.write_text(FAKE_DUT)
    (tmp_path / "cornerMOSlv.lib").write_text("* lib\n")
    pex = tmp_path / "run" / "dut_postlayout.spice"
    text, how = swap_dut_reference(FAKE_TB_INCLUDE, dut_path=dut, subckt="cell", pex_path=pex, base_dirs=(tmp_path,))
    assert how == "include"
    assert f".include {pex}" in text and ".include dut.spice" not in text
    assert f".lib {tmp_path.resolve() / 'cornerMOSlv.lib'} mos_tt" in text  # other relative refs absolutised
    assert ".param W1 = 1u" in text  # the deck's own params survive (NGSpice_Wrapper injects the fixed sizing)
    text, how = swap_dut_reference(FAKE_TB_INLINE, dut_path=dut, subckt="cell", pex_path=pex, base_dirs=(tmp_path,))
    assert how == "inline"
    assert ".subckt cell" not in text and "XM1 a b vss" not in text and f".include {pex}" in text
    assert "XDUT a b 0 cell" in text
    with pytest.raises(ValueError, match="neither"):
        swap_dut_reference("V1 a 0 1\n.end\n", dut_path=dut, subckt="cell", pex_path=pex, base_dirs=(tmp_path,))


def test_build_postlayout_dut_reorders_pins_and_checks_set():
    from spicexplorer.backends.layout import build_postlayout_dut
    from spicexplorer_signoff.postlayout import prep_pex_subckt

    raw = ".SUBCKT cell vss b\n+ a\nM1 a b vss vss nmos L=1U W=1U\nC1 a VSUBS 1f\nC2 VSUBS vss 2f\n.ENDS cell\n"
    out = build_postlayout_dut(raw, "cell", "cell", ["a", "b", "vss"], prep_pex_subckt, ground_nets=["VSUBS"])
    lines = out.splitlines()
    assert lines[0] == ".subckt cell a b vss"  # DUT pin ORDER, kpex's dropped
    assert "XM1 a b vss vss nmos L=1U W=1U" in lines
    assert "C1 a 0 1f" in lines and "C2 0 vss 2f" in lines  # VSUBS → 0, the vss PORT untouched
    # rename to the schematic subckt name when it differs from the cell
    out2 = build_postlayout_dut(raw, "cell", "ota", ["a", "b", "vss"], prep_pex_subckt)
    assert out2.splitlines()[0] == ".subckt ota a b vss" and "C1 a VSUBS 1f" in out2
    with pytest.raises(ValueError, match="pin set"):
        build_postlayout_dut(raw, "cell", "cell", ["a", "b", "vdd"], prep_pex_subckt)


def test_postlayout_runs_platform_testbenches_and_delegates(tmp_path: Path, monkeypatch):
    from spicexplorer_core.measurements import registry
    from spicexplorer_core.pvt import Corner

    calls: list = []
    state = _State()
    _install_fakes(monkeypatch, state)
    _install_fake_ngspice(monkeypatch, calls)
    flow = _write_flow_postlayout(tmp_path, two_tbs=True)
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out", path_to_simulator="ngspice")
    sim.update_params({"gap_x": 1.5, "CL": 5e-14})  # CL is not a knob → forwarded to the decks
    sim.apply_corner(Corner(name="tt", temp=27.0))
    res = sim.run(label="layout__tt")
    assert res.status == "ok", res.summary["error"]
    assert res.scalar("postlayout_ok", "layout") == 1.0
    assert set(res.inner) == {"tb_ac", "tb_op"}
    # the decks were built through the factory, corner applied, fixed sizing + forwarded params injected
    kinds = [c[0] for c in calls]
    assert kinds.count("build") == 2 and kinds.count("run") == 2
    assert ("corner", "tb_ac", "tt") in calls
    assert ("params", "tb_ac", {"W1": 2e-6, "CL": 5e-14}) in calls
    # the swapped deck includes the trial's dut_postlayout.spice, whose header is the DUT's
    pl = res.summary["stages"]["postlayout"]
    assert pl["tb_ac"]["dut_swap"] == "include"
    deck = Path(pl["tb_ac"]["deck"]).read_text()
    assert f".include {pl['dut']}" in deck
    assert Path(pl["dut"]).read_text().splitlines()[0] == ".subckt cell a b vss"
    # delegation: own scalars first, then <tb>:<name>, then inner search in spec order
    assert res.scalar("area_um2", "layout") == pytest.approx(150.0)
    assert res.scalar("tb_op:i(vdd)", "op") == pytest.approx(-1e-6)
    assert res.scalar("i(vdd)", "op") == pytest.approx(-2.7e-5)  # first inner (tb_ac) wins
    assert res.scalar("v(vout)", "op") == 0.6 and math.isnan(res.scalar("nope", "op"))
    w = res.wave("v(vout)", "ac")
    assert w.shape == (400,) and np.iscomplexobj(w)
    assert res.wave("tb_op:frequency", "ac").shape == (400,)
    with pytest.raises(KeyError):
        res.wave("nope", "ac")
    # the registry (Tier-1 {meas: …}) runs unchanged on the layout result
    ugf = registry.measure(res, {"meas": "ugf", "out": "v(vout)"}, default_analysis="ac")
    assert ugf == pytest.approx(1e7, rel=0.05)
    pm = registry.measure(res, {"meas": "pm", "out": "v(vout)"}, default_analysis="ac")
    assert 85 < pm < 95
    # merged scalars are authoritative and win collisions
    res.merge_scalars({"ugf": ugf, "area_um2": -1.0})
    assert res.scalar("ugf", "ac") == ugf and res.scalar("area_um2", "layout") == -1.0
    # the pre-layout reference runs the same decks with the DUT include untouched
    pre = sim.run_prelayout_reference(tmp_path / "pre")
    assert set(pre) == {"tb_ac", "tb_op"}
    pre_deck = (tmp_path / "pre" / "tb_ac.spice").read_text()
    assert f".include {(tmp_path / 'dut.spice')}" in pre_deck


def test_postlayout_gated_by_pex_failure(tmp_path: Path, monkeypatch):
    calls: list = []
    state = _State()
    state.pex_ok = False
    _install_fakes(monkeypatch, state)
    _install_fake_ngspice(monkeypatch, calls)
    flow = _write_flow_postlayout(tmp_path)
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out")
    sim.update_params({"gap_x": 1.0})
    res = sim.run()
    assert res.status == "pex_fail" and not calls  # no post-layout sim ran
    assert math.isnan(res.scalar("postlayout_ok", "layout"))
    with pytest.raises(NotImplementedError):
        res.wave("v(vout)", "ac")  # no inner results → no waves


def test_orchestrator_scores_postlayout_registry_metrics(tmp_path: Path, monkeypatch):
    """End-to-end: `{name: ugf, testbench: layout, sim_type: ac, measurement: {meas: ugf, …}}`
    is scored from the post-layout waves via measure_integration — no new scorer code."""
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    calls: list = []
    state = _State()
    _install_fakes(monkeypatch, state)
    _install_fake_ngspice(monkeypatch, calls)
    flow = _write_flow_postlayout(tmp_path)
    proj = _project_yaml(tmp_path, flow)
    d = yaml.safe_load(proj.read_text())
    d["project"]["optimizer_config"]["target_specs"] = [
        {"name": "area_um2", "testbench": "layout", "sim_type": "layout", "goal": "minimize",
         "target": 200, "range": 100, "tolerance": 0, "reward_type": "relative-log"},
        {"name": "ugf", "testbench": "layout", "sim_type": "ac", "goal": "exceed", "target": 5e6,
         "range": 5e6, "tolerance": 0, "reward_type": "none", "measurement": {"meas": "ugf", "out": "v(vout)"}},
        {"name": "pm", "testbench": "layout", "sim_type": "ac", "goal": "exceed", "target": 60,
         "range": 30, "tolerance": 0, "reward_type": "none", "measurement": {"meas": "pm", "out": "v(vout)"}},
        {"name": "tb_ac:v(vout)", "testbench": "layout", "sim_type": "op", "goal": "exceed", "target": 0.5,
         "range": 1, "tolerance": 0, "reward_type": "none"},
        {"name": "postlayout_ok", "testbench": "layout", "sim_type": "layout", "goal": "exact", "target": 1,
         "range": 1, "tolerance": 0, "reward_type": "none"},
    ]
    d["project"]["optimizer_config"]["budget"] = 1
    proj.write_text(yaml.safe_dump(d))
    orch = Circuit_Optimizer_Orchestrator_with_SPICE(project_setup_path=proj, optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE)
    opt = orch.get_optimizer()
    opt.disable_autosave = True
    opt.autosave_checkpoint_dir = tmp_path / "ckpt"
    opt.parameterize()
    opt.optimize(render_optimization_trace=False, keep_history=False)
    fs = opt.optimization_log[0].get_fit_summary()
    assert fs["ugf"]["curr_val"] == pytest.approx(1e7, rel=0.05)
    assert 85 < fs["pm"]["curr_val"] < 95
    assert fs["tb_ac:v(vout)"]["curr_val"] == 0.6
    assert fs["postlayout_ok"]["curr_val"] == 1.0
    assert all(v["score"] >= 0 for k, v in fs.items() if k != "area_um2")  # every constraint met


def test_sizing_params_route_to_build_sizing_and_postlayout_decks(tmp_path: Path, monkeypatch):
    """Co-optimization: a dut_param listed in `sizing_params` is not a layout knob — it overlays
    the sizing JSON handed to build(params, sizing) (per-run sizing.json) AND is injected into
    the post-layout decks' `.param`s."""
    import spicexplorer_layout

    calls: list = []
    state = _State()
    _install_fakes(monkeypatch, state)
    _install_fake_ngspice(monkeypatch, calls)
    seen: dict = {}
    real_builder = spicexplorer_layout.GdsBuilder

    class SpyBuilder(real_builder):  # type: ignore[misc,valid-type]
        def __init__(self, gen_path, out_dir, *, sizing_json=None, **kw):
            seen["sizing_json"] = sizing_json
            super().__init__(gen_path, out_dir, sizing_json=sizing_json, **kw)

    monkeypatch.setattr(spicexplorer_layout, "GdsBuilder", SpyBuilder)
    flow = _write_flow_postlayout(tmp_path)
    (tmp_path / "sizing.json").write_text(json.dumps({"in_w": 1e-6, "tail_w": 2e-6}))
    d = yaml.safe_load(flow.read_text())
    d["sizing"] = "sizing.json"
    d["sizing_params"] = {"W1": "in_w"}
    flow.write_text(yaml.safe_dump(d))
    spec = LayoutFlowSpec.from_yaml(flow)
    assert spec.sizing_params == {"W1": "in_w"}
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out")
    sim.update_params({"gap_x": 1.0, "W1": 3e-6})
    res = sim.run()
    assert res.status == "ok", res.summary["error"]
    assert seen["sizing_json"] is not None and Path(seen["sizing_json"]).name == "sizing.json"
    assert json.loads(Path(seen["sizing_json"]).read_text()) == {"in_w": 3e-6, "tail_w": 2e-6}
    assert res.summary["sizing"] == {"in_w": 3e-6} and "W1" not in res.summary["params"]
    assert ("params", "tb_ac", {"W1": 3e-6}) in calls  # deck `.param W1` gets the candidate (over postlayout.params)
    # a sizing name that is also a knob is rejected at load
    d["sizing_params"] = {"gap_x": "in_w"}
    flow.write_text(yaml.safe_dump(d))
    with pytest.raises(ValueError, match="also LayoutParams knobs"):
        LayoutFlowSpec.from_yaml(flow)


def test_sizing_grid_snaps_sizing_candidates(tmp_path: Path, monkeypatch):
    """`sizing_grid` (opt-in) rounds the `sizing_params` candidates onto a manufacturing grid.

    A raw optimizer float reaches the generator as a device width; drawn off-grid it makes
    KLayout report a wall of `OffGrid.*` violations, so the candidate is rejected for a reason
    unrelated to the design. The knobs already snap to `param_grid`; sizing needs its OWN grid
    because a sizing dict's units are the generator's (um here, but metres elsewhere), which is
    why the default is None = passthrough.
    """
    import spicexplorer_layout

    calls: list = []
    state = _State()
    _install_fakes(monkeypatch, state)
    _install_fake_ngspice(monkeypatch, calls)
    seen: dict = {}
    real_builder = spicexplorer_layout.GdsBuilder

    class SpyBuilder(real_builder):  # type: ignore[misc,valid-type]
        def __init__(self, gen_path, out_dir, *, sizing_json=None, **kw):
            seen["sizing_json"] = sizing_json
            super().__init__(gen_path, out_dir, sizing_json=sizing_json, **kw)

    monkeypatch.setattr(spicexplorer_layout, "GdsBuilder", SpyBuilder)
    flow = _write_flow_postlayout(tmp_path)
    (tmp_path / "sizing.json").write_text(json.dumps({"in_w": 0.5, "tail_w": 2.0}))
    d = yaml.safe_load(flow.read_text())
    d["sizing"] = "sizing.json"
    d["sizing_params"] = ["in_w"]
    flow.write_text(yaml.safe_dump(d))

    # default: no sizing_grid → the raw float is passed straight through
    assert LayoutFlowSpec.from_yaml(flow).sizing_grid is None
    sim = create_layout_simulator(flow, output_folder=tmp_path / "out")
    sim.update_params({"gap_x": 1.0, "in_w": 0.5052731805394455})
    assert sim.run().summary["sizing"] == {"in_w": 0.5052731805394455}

    # opt in → snapped, in the sizing dict AND in the deck's `.param`
    d["sizing_grid"] = 0.01
    flow.write_text(yaml.safe_dump(d))
    spec = LayoutFlowSpec.from_yaml(flow)
    assert spec.sizing_grid == 0.01
    assert spec.snap_sizing(0.5052731805394455) == 0.51
    sim2 = create_layout_simulator(flow, output_folder=tmp_path / "out2")
    sim2.update_params({"gap_x": 1.0, "in_w": 0.5052731805394455})
    res = sim2.run()
    assert res.summary["sizing"] == {"in_w": 0.51}
    assert json.loads(Path(seen["sizing_json"]).read_text()) == {"in_w": 0.51, "tail_w": 2.0}
    deck_params = [c[2] for c in calls if c[0] == "params" and c[1] == "tb_ac"]
    assert any(d.get("in_w") == 0.51 for d in deck_params), deck_params
    assert snap_to_grid(0.5052731805394455, None) == 0.5052731805394455
