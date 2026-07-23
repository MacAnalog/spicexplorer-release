"""Offline: the in-library router (probe + discovery + builders) over analog-db.

Proves the Layer-B surface of `backends.analog_db` WITHOUT any SPICE/bridge/kit: the committed
`sim_engine` marker routes a (circuit, pdk) to an engine, discovery lists the tree, the probe
degrades honestly, and the engine-neutral signal-name convention + corner guard are correct.
Live open/closed runs live in the `*_live.py` opt-in tests. Gated on the analog-db submodule
(with the `sim_engine` marker) being checked out — point `SPICEXPLORER_ANALOG_DB` at it.
"""

from __future__ import annotations

import pytest
from spicexplorer.backends.analog_db import (
    AnalogDbUnavailable,
    CircuitRun,
    EngineCapability,
    EngineUnavailable,
    analog_db_root,
    build_ngspice_run,
    circuit_analyses,
    circuit_pdks,
    list_circuits,
    pdk_sim_engine,
    probe_engine,
    run_circuit,
)

_CIRCUIT = "amp_022_fer_two_stage"


def _have_marker() -> bool:
    try:
        return (
            analog_db_root() / "circuits" / _CIRCUIT / "pdk" / "FOUNDRY-n65" / "sizing.yaml"
        ).is_file() and pdk_sim_engine("FOUNDRY-n65") is not None
    except Exception:
        return False


_needs_marker = pytest.mark.skipif(
    not _have_marker(),
    reason="analog-db checkout with the sim_engine PDK marker not present (set SPICEXPLORER_ANALOG_DB)",
)


# ------------------------------------------------------------------ pure (no analog-db)
def test_engine_capability_is_truthy_by_availability():
    assert bool(EngineCapability(_CIRCUIT, "FOUNDRY-n65", "spectre", True, "ok"))
    assert not EngineCapability(_CIRCUIT, "FOUNDRY-n65", "spectre", False, "no kit")


def test_circuitrun_out_signal_convention_per_engine():
    # engine-neutral registry, engine-specific signal name: ngspice wraps v(...), Spectre is bare
    ng = CircuitRun(_CIRCUIT, "ihp-sg13g2", "ngspice", "ac_open_loop", "tt", None, [])
    sp = CircuitRun(_CIRCUIT, "FOUNDRY-n65", "spectre", "ac_open_loop", "tt", None, [])
    assert ng._out("vout") == "v(vout)"
    assert sp._out("vout") == "vout"
    assert ng.analysis == "ac" and sp.analysis == "ac"


def test_artifact_path_reads_ngspice_raw_path(tmp_path):
    """The ngspice artifact seam rides `NgspiceSimResult.raw_path` (the wrapper records
    it) — spicelib's RawRead does NOT retain its filename, so reading `raw.raw_filename`
    silently yields None (the bug the live gallery surfaced)."""
    from spicexplorer_core.spice_engine.spicelib import NgspiceSimResult

    raw_file = tmp_path / "tb_1.raw"
    raw_file.write_text("stub")
    res = NgspiceSimResult(None, log_path=None, raw_path=str(raw_file))
    run = CircuitRun(_CIRCUIT, "ihp-sg13g2", "ngspice", "ac_open_loop", "tt", res, [])
    assert run.artifact_path() == raw_file
    # a recorded path whose file is gone degrades to None, never a dangling Path
    raw_file.unlink()
    assert run.artifact_path() is None
    assert CircuitRun(
        _CIRCUIT, "ihp-sg13g2", "ngspice", "ac_open_loop", "tt",
        NgspiceSimResult(None), [],
    ).artifact_path() is None


@_needs_marker
def test_build_ngspice_run_swaps_corner_without_touching_supply(monkeypatch, tmp_path):
    # a non-tt corner resolves the circuit's own corners.yaml into apply_corner — process
    # section + temp only, with NO SupplyOverride (the deck's authored VDD is the open
    # lane's operating point of record; see effective_supply)
    import spicexplorer_core.spice_engine as se

    seen: dict[str, object] = {}

    class _StubWrapper:
        def __init__(self, **kwargs):
            seen["init"] = kwargs

        def apply_corner(self, corner, model_lib_root=None):
            seen["corner"] = corner

        def run(self):
            seen["ran"] = True
            return "stub-result"

    monkeypatch.setattr(se, "NGSpice_Wrapper", _StubWrapper)
    out = build_ngspice_run(
        _CIRCUIT, "ihp-sg13g2", "ac_open_loop", corner="ss", output_dir=tmp_path
    )
    assert out == "stub-result" and seen.get("ran")
    corner = seen["corner"]
    assert corner.name == "ihp-sg13g2_ss"  # type: ignore[attr-defined]
    assert [i.section for i in corner.model_includes] == ["mos_ss"]  # type: ignore[attr-defined]
    assert corner.supplies == []  # type: ignore[attr-defined]


@_needs_marker
def test_build_ngspice_run_applies_sizing_overrides(monkeypatch, tmp_path):
    """The sizing-experiment seam: declared .param knobs are edited on the deck before
    the run; an unknown knob is SKIPPED (spicelib would silently insert a dangling
    .param — BUG-B12), keeping the committed value."""
    import spicexplorer_core.spice_engine as se

    seen: dict[str, object] = {}

    class _StubEditor:
        def get_all_parameter_names(self):
            return ["x_dut_xm1_w", "VDD"]

        def set_parameter(self, key, value):
            seen.setdefault("set", []).append((key, value))  # type: ignore[union-attr]

    class _StubWrapper:
        def __init__(self, **kwargs):
            self.editor = _StubEditor()

        def run(self):
            return "stub-result"

    monkeypatch.setattr(se, "NGSpice_Wrapper", _StubWrapper)
    out = build_ngspice_run(
        _CIRCUIT, "ihp-sg13g2", "ac_open_loop", output_dir=tmp_path,
        sizing_overrides={"x_dut_xm1_w": "9.9u", "no_such_knob": 1.0},
    )
    assert out == "stub-result"
    assert seen["set"] == [("x_dut_xm1_w", "9.9u")]  # unknown knob skipped, not inserted


@_needs_marker
def test_build_ngspice_run_unknown_corner_raises_keyerror():
    with pytest.raises(KeyError, match="corner 'xx'"):
        build_ngspice_run(_CIRCUIT, "ihp-sg13g2", "ac_open_loop", corner="xx")


# ------------------------------------------------------------ marker-driven routing (data only)
@_needs_marker
def test_sim_engine_marker_routes_open_vs_closed():
    assert pdk_sim_engine("FOUNDRY-n65") == "spectre"
    for open_pdk in ("ihp-sg13g2", "sky130", "gf180mcu"):
        assert pdk_sim_engine(open_pdk) == "ngspice"


@_needs_marker
def test_discovery_lists_circuit_pdks_and_analyses():
    assert _CIRCUIT in list_circuits()
    assert set(circuit_pdks(_CIRCUIT)) >= {"ihp-sg13g2", "sky130", "FOUNDRY-n65"}
    assert "ac_open_loop" in circuit_analyses(_CIRCUIT)


@_needs_marker
def test_probe_engine_reports_engine_and_degrades_honestly():
    # closed lane routes to spectre; without an operator wrapper it is unavailable with a reason
    cap = probe_engine(_CIRCUIT, "FOUNDRY-n65", model_lib_root="/nonexistent/model/root")
    assert cap.engine == "spectre"
    assert not cap.available and "wrapper" in cap.reason
    # open lane routes to ngspice; availability tracks the ngspice binary (engine is deterministic)
    assert probe_engine(_CIRCUIT, "ihp-sg13g2").engine == "ngspice"
    # an unknown PDK registry is unavailable, not a crash
    assert not probe_engine(_CIRCUIT, "no-such-pdk").available


@_needs_marker
def test_probe_engine_missing_circuit_binding():
    cap = probe_engine(_CIRCUIT, "sky130")
    assert cap.engine == "ngspice"  # sky130 is bound for amp_022
    with pytest.raises(AnalogDbUnavailable):
        circuit_pdks("no_such_circuit_xyz")


@_needs_marker
def test_run_circuit_raises_engine_unavailable_when_closed_lane_absent():
    # deterministic offline: no wrapper => the router refuses the closed lane with the probe reason
    with pytest.raises(EngineUnavailable, match="wrapper"):
        run_circuit(
            _CIRCUIT, "FOUNDRY-n65", model_lib_root="/nonexistent/model/root",
            deck_dir="/tmp/x", work_dir="/tmp/y",
        )


@_needs_marker
def test_effective_supply_pins_the_two_truths():
    from spicexplorer.backends.analog_db import effective_supply

    sup = effective_supply(_CIRCUIT, "FOUNDRY-n65", "ac_open_loop")
    # amp_022's analyses bake VDD=1.5 (authored operating point) while the FOUNDRY-n65
    # registry rail is 1.2 — the closed lane runs the rail, the open lane runs the deck
    assert sup["deck_vdd"] == pytest.approx(1.5)
    assert sup["pdk_rail"] == pytest.approx(1.2)
    assert sup["open_lane"] == pytest.approx(1.5)
    assert sup["closed_lane"] == pytest.approx(1.2)


def test_evaluate_matches_metrics_by_analysis_id():
    import numpy as np
    from spicexplorer.backends.analog_db import MetricTarget

    class _Res:
        def wave(self, name, analysis):
            freq = np.logspace(3, 9, 31)
            return freq if name == "v(frequency)" or name == "frequency" else np.full(31, 0.01, dtype=complex)

    metrics = [
        MetricTarget("cmrr_db", {"meas": "cmrr_db", "out": "vout"}, "ac", 20.0, None, "cmrr_vcm"),
        MetricTarget("dcgain", {"meas": "dcgain", "out": "vout"}, "ac", None, None, "ac_open_loop"),
    ]
    run = CircuitRun("c", "ihp-sg13g2", "ngspice", "cmrr_vcm", "tt", _Res(), metrics)
    evals = run.evaluate()
    # same KIND (ac), different bench: only the cmrr metric scores on the cmrr run
    assert set(evals) == {"cmrr_db"}
    assert evals["cmrr_db"].value == pytest.approx(40.0, abs=0.01)  # -20log10(0.01)
    assert evals["cmrr_db"].satisfied


def test_spectre_analyses_compose_per_testbench():
    from spicexplorer.backends.analog_db import _spectre_analyses

    ac_params = {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}
    for tb in ("ac_open_loop", "ac_closed_loop", "cmrr_vcm", "psrr_vdd"):
        op, ac = _spectre_analyses(tb, ac_params)
        assert op == "dcOp dc" and ac.startswith("ac ac start=1000 stop=1000000000 dec=101")
    assert _spectre_analyses("dc_op", {}) == ("dcOp dc",)
    op, nz = _spectre_analyses("noise", {"FSTART": "1k", "FSTOP": "100MEG", "PPD": 50})
    assert nz.startswith("noise ( vout 0 ) noise") and "iprobe=VINP" in nz
    op, tr = _spectre_analyses("tran_step", {"TSTOP": "5u", "TSTEP": "1n"})
    assert tr.startswith("tran tran stop=5e-06")
    # linearity: sweep-only (no dcOp beside the dc.dc PSF), rail-bounded via `supply`
    (sweep,) = _spectre_analyses("linearity", {"VDD": 1.5, "VSWEEP_STEP": "5m"}, supply=1.2)
    assert sweep == "dc dc dev=VINP param=dc start=0 stop=1.2 step=0.005"
    with pytest.raises(NotImplementedError):
        _spectre_analyses("no_such_bench", {})


def test_spectre_analyses_thd_iip3_native_pss():
    from spicexplorer.backends.analog_db import _spectre_analyses

    (pss,) = _spectre_analyses("thd", {"F0": "1.0e6", "HARMS": 7})
    assert pss == "pss pss fund=1000000 harms=7 errpreset=conservative"
    # two tones on the 100 kHz common fundamental -> harms cover the upper IM3 (2*n2+1)
    (pss,) = _spectre_analyses("iip3", {"F1": "0.9e6", "F2": "1.0e6"})
    assert pss.startswith("pss pss fund=100000 harms=21")


def test_evaluate_swaps_fft_recipes_for_pss_twins_on_spectre():
    import numpy as np
    from spicexplorer.backends.analog_db import MetricTarget

    a_in, n1, n2 = 0.05, 9, 10
    phasors = np.zeros(2 * n2 + 2, dtype=complex)
    phasors[1] = 0.1  # a thd run's fundamental would sit here; unused by the iip3 metric
    phasors[n1] = phasors[n2] = a_in
    phasors[2 * n2 - n1] = a_in * 1e-3

    class _PssRes:
        def wave(self, name, analysis):
            assert analysis == "pss"  # the swap must re-route the analysis too
            return phasors

    metrics = [MetricTarget(
        "iip3_dbv", {"meas": "iip3_dbv", "out": "vout", "f1": 0.9e6, "f2": 1.0e6, "ampl_in": a_in},
        "tran", -10.0, None, "iip3",
    )]
    run = CircuitRun("c", "FOUNDRY-n65", "spectre", "iip3", "tt", _PssRes(), metrics)
    got = run.evaluate()["iip3_dbv"].value
    expect = 20 * np.log10(a_in * np.sqrt(1e3))
    assert got == pytest.approx(expect, abs=1e-6)
