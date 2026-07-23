"""Spectre `Simulator` adapter, unit-tested against a FAKE bridge (no Cadence).

Covers: protocol conformance, the flat-PSF `SimResult` lookup (prefix + bare + per-MOS
op-point + missing→NaN/raise), blocking `run()` / non-blocking `submit()`, the corner →
`include "…" section=…` emission, design-param staging, and the lazy factory's
import-guard + non-clobbering `VB_*` pre-set. None of this touches virtuoso-bridge or an
SSH host — the bridge is a stand-in with the two methods the adapter calls.
"""

from __future__ import annotations

import importlib.util
from concurrent.futures import Future
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from spicexplorer.backends.spectre import (
    SpectreSimHandle,
    SpectreSimResult,
    SpectreSimulator,
    create_spectre_simulator,
    parse_psfascii_oppoint,
)
from spicexplorer.backends.spectre_deck import SpectreDeckSpec
from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride
from spicexplorer_core.spice_engine import SimHandle, SimResult, Simulator


class _FakeSimulationResult:
    """Stand-in for the bridge's `SimulationResult` — `.data` + `.metadata` are read."""

    def __init__(self, data: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        self.data = data
        self.metadata = metadata or {}


class _FakeBridge:
    """Duck-typed stand-in for the bridge `SpectreSimulator`.

    Records the (netlist, params) it was handed so tests can assert what the adapter
    staged, and returns a canned flat-PSF dict.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._data = data or {}
        self.metadata: dict[str, Any] = {}
        self.calls: list[tuple[Path, dict[str, Any]]] = []

    def run_simulation(self, netlist: Path, params: dict[str, Any]) -> _FakeSimulationResult:
        self.calls.append((Path(netlist), dict(params)))
        return _FakeSimulationResult(self._data, dict(self.metadata))

    def submit(self, netlist: Path, params: dict[str, Any]) -> "Future[_FakeSimulationResult]":
        self.calls.append((Path(netlist), dict(params)))
        fut: Future[_FakeSimulationResult] = Future()
        fut.set_result(_FakeSimulationResult(self._data, dict(self.metadata)))
        return fut


# ---------------------------------------------------------------------------
# Conformance
# ---------------------------------------------------------------------------
def test_spectre_adapter_satisfies_the_protocols() -> None:
    assert issubclass(SpectreSimulator, Simulator)
    assert issubclass(SpectreSimResult, SimResult)
    assert issubclass(SpectreSimHandle, SimHandle)

    sim = SpectreSimulator(_FakeBridge(), Path("tb.scs"))
    assert isinstance(sim, Simulator)


# ---------------------------------------------------------------------------
# SimResult over the flat PSF dict
# ---------------------------------------------------------------------------
def test_simresult_scalar_lookup_prefix_bare_and_op_point() -> None:
    # Key shapes mirror a real FOUNDRY-65 run (P0 live, 2026-07-05): ac_/dc_ prefixed
    # node signals from the bridge parser, bare `<inst>:<param>` op scalars from our
    # info-file post-parse, bare tran signals.
    res = SpectreSimResult(
        {
            "ac_out": np.array([1 + 2j, 3 + 4j]),  # analysis-prefixed AC signal
            "M0:gm": 1.5e-3,                        # per-MOS op-point scalar (bare key)
            "dc_VOUT": 0.94,                        # dcOp node voltage → dc_ prefix
            "vout": 0.9,                            # bare signal
        }
    )
    # prefixed lookup: first point, real part (mirrors ngspice is_real scalar)
    assert res.scalar("out", "ac") == pytest.approx(1.0)
    # bare op-point scalar
    assert res.scalar("M0:gm", "op") == pytest.approx(1.5e-3)
    # op-point NODE voltage: the "op" chain falls through bare → dc_ (dcOp.dc reality)
    assert res.scalar("VOUT", "op") == pytest.approx(0.94)
    # tran signals merge bare in the bridge parser — no tran_ prefix exists
    assert res.scalar("vout", "tran") == pytest.approx(0.9)
    # bare fallback when no prefixed key exists
    assert res.scalar("vout", "dc") == pytest.approx(0.9)
    # missing → NaN, never a crash
    assert np.isnan(res.scalar("nope", "ac"))


def test_simresult_wave_returns_array_and_raises_when_missing() -> None:
    res = SpectreSimResult({"ac_out": np.array([1 + 2j, 3 + 4j])})
    wave = res.wave("out", "ac")
    np.testing.assert_array_equal(wave, np.array([1 + 2j, 3 + 4j]))
    with pytest.raises(KeyError):
        res.wave("missing", "ac")


def test_simresult_empty_data_degrades() -> None:
    res = SpectreSimResult(None)
    assert np.isnan(res.scalar("anything", "op"))
    with pytest.raises(KeyError):
        res.wave("anything", "op")


# ---------------------------------------------------------------------------
# psfascii info-file op-point post-parse (the bridge parser drops STRUCT values)
# ---------------------------------------------------------------------------
# Shape copied from a real FOUNDRY-65 `finalTimeOP.info` (P0 live run): per-model STRUCT
# defs in TYPE (with nested PROP(...) blocks), then per-instance value blocks. Values
# here are synthetic.
_INFO_PSFASCII = """HEADER
"PSFversion" "1.00"
"analysis type" "info"
"analysis name" "finalTimeOP"
"AnalysisType" "dcOp"
TYPE
"bsim4" STRUCT(
"ids" FLOAT DOUBLE PROP(
"units" "A"
"description" "Resistive drain-to-source current"
)
"gm" FLOAT DOUBLE PROP(
"units" "S"
"description" "Common source transconductance"
)
"vth" FLOAT DOUBLE PROP(
"units" "V"
"description" "Threshold voltage"
)
"region" INT BYTE PROP(
"description" "Estimated operating region"
)
)
"vsource" STRUCT(
"v" FLOAT DOUBLE PROP(
"units" "V"
"description" "Voltage across the source"
)
"i" FLOAT DOUBLE PROP(
"units" "A"
"description" "Current through the source"
)
)
VALUE
"X0.M0" "bsim4" (
2.813561446398000e-05
2.751980125954339e-04
3.843490744464556e-01
2
) PROP(
"model" "nch_x.1"
)
"Vdd" "vsource" (
1.200000000000000e+00
-4.709620273388057e-05
)
END
"""


def test_parse_psfascii_oppoint_extracts_struct_scalars(tmp_path: Path) -> None:
    (tmp_path / "finalTimeOP.info").write_text(_INFO_PSFASCII)
    # ADE model dump — must be skipped (NDA hygiene + noise), even with parseable structs
    (tmp_path / "modelParameter.info").write_text(_INFO_PSFASCII)

    got = parse_psfascii_oppoint(tmp_path)
    assert got == pytest.approx(
        {
            "X0.M0:ids": 2.813561446398000e-05,
            "X0.M0:gm": 2.751980125954339e-04,
            "X0.M0:vth": 3.843490744464556e-01,
            "X0.M0:region": 2.0,
            "Vdd:v": 1.2,
            "Vdd:i": -4.709620273388057e-05,
        }
    )


def test_parse_psfascii_oppoint_degrades_on_missing_or_malformed(tmp_path: Path) -> None:
    assert parse_psfascii_oppoint(tmp_path / "nope") == {}
    (tmp_path / "broken.info").write_text("HEADER\nTYPE\nVALUE\ngarbage (\n")
    assert parse_psfascii_oppoint(tmp_path) == {}


def test_run_merges_oppoint_post_parse_from_output_dir(tmp_path: Path) -> None:
    (tmp_path / "finalTimeOP.info").write_text(_INFO_PSFASCII)
    bridge = _FakeBridge({"dc_VOUT": 0.94, "finalTimeOP_X0.M0": "bsim4"})
    bridge.metadata = {"output_dir": str(tmp_path)}
    sim = SpectreSimulator(bridge, Path("tb.scs"))

    res = sim.run()
    # bridge-parsed keys survive untouched…
    assert res.scalar("VOUT", "op") == pytest.approx(0.94)
    # …and the per-MOS struct scalars the bridge dropped are merged in bare
    assert res.scalar("X0.M0:gm", "op") == pytest.approx(2.751980125954339e-04)
    assert res.scalar("X0.M0:region", "op") == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# run() / submit()
# ---------------------------------------------------------------------------
def test_run_blocking_wraps_bridge_result() -> None:
    bridge = _FakeBridge({"M0:vth": 0.42})
    sim = SpectreSimulator(bridge, Path("tb.scs"))
    res = sim.run()
    assert isinstance(res, SimResult)
    assert res.scalar("M0:vth", "op") == pytest.approx(0.42)
    assert bridge.calls and bridge.calls[0][0] == Path("tb.scs")


def test_submit_nonblocking_wraps_future() -> None:
    bridge = _FakeBridge({"M0:vth": 0.42})
    sim = SpectreSimulator(bridge, Path("tb.scs"))
    handle = sim.submit()
    assert isinstance(handle, SimHandle)
    assert handle.is_done() is True  # the fake future is already resolved
    res = handle.result()
    assert isinstance(res, SimResult)
    assert res.scalar("M0:vth", "op") == pytest.approx(0.42)
    assert handle.result() is res  # cached


# ---------------------------------------------------------------------------
# apply_corner + update_params staging
# ---------------------------------------------------------------------------
def test_apply_corner_emits_spectre_include_section_and_rails() -> None:
    bridge = _FakeBridge()
    sim = SpectreSimulator(bridge, Path("tb.scs"))
    corner = Corner(
        name="ss_hot",
        model_includes=[
            ModelInclude(lib_file="FOUNDRY65.scs", section="ss"),
            ModelInclude(lib_file="FOUNDRY65_rc.scs", section="rc_worst"),
        ],
        temp=85.0,
        supplies=[SupplyOverride(node="VDD", value=1.1)],
        params={"vcm": 0.55},
    )
    sim.apply_corner(corner)
    staged = sim.staged_params
    assert staged["corner"] == "ss_hot"
    assert staged["corner_includes"] == [
        'include "FOUNDRY65.scs" section=ss',
        'include "FOUNDRY65_rc.scs" section=rc_worst',
    ]
    assert staged["temp"] == 85.0
    assert staged["corner_params"] == {"VDD": 1.1, "vcm": 0.55}

    # idempotent: re-applying a different corner replaces, never accumulates
    sim.apply_corner(Corner(name="tt", model_includes=[ModelInclude("FOUNDRY65.scs", "tt")]))
    assert sim.staged_params["corner"] == "tt"
    assert sim.staged_params["corner_includes"] == ['include "FOUNDRY65.scs" section=tt']


def test_update_params_stages_design_variables() -> None:
    sim = SpectreSimulator(_FakeBridge(), Path("tb.scs"))
    assert sim.update_params({"W_M0": 2e-6, "L_M0": 6e-8}) is True
    assert sim.staged_params["design_params"] == {"W_M0": 2e-6, "L_M0": 6e-8}
    # forwarded to the bridge on run()
    sim.run()
    _, params = sim._bridge.calls[0]  # type: ignore[attr-defined]
    assert params["design_params"] == {"W_M0": 2e-6, "L_M0": 6e-8}


# ---------------------------------------------------------------------------
# Lazy factory: import guard + non-clobbering VB_* pre-set
# ---------------------------------------------------------------------------
# These exercise the missing-bridge ImportError path, so they only make sense in a venv
# without virtuoso-bridge — which is CI and every ngspice-only checkout. A live-Spectre
# dev venv (bridge pip-installed for test_spectre_live.py) skips them.
_HAS_BRIDGE = importlib.util.find_spec("virtuoso_bridge") is not None
_needs_bridgeless = pytest.mark.skipif(
    _HAS_BRIDGE, reason="tests the ImportError guard; needs a venv without virtuoso-bridge"
)


@_needs_bridgeless
def test_create_spectre_simulator_raises_without_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    # virtuoso_bridge is not installed in the ngspice-only venv → actionable ImportError.
    with pytest.raises(ImportError, match="virtuoso-bridge"):
        create_spectre_simulator(Path("tb.scs"), vb_env={"VB_REMOTE_HOST": "srv"})


@_needs_bridgeless
def test_create_spectre_simulator_vb_env_never_clobbers(monkeypatch: pytest.MonkeyPatch) -> None:
    # A pre-existing VB_* value must survive (setdefault semantics), and the pre-set must
    # happen BEFORE the (failing) bridge import.
    monkeypatch.setenv("VB_REMOTE_HOST", "already-set")
    with pytest.raises(ImportError):
        create_spectre_simulator(Path("tb.scs"), vb_env={"VB_REMOTE_HOST": "override", "VB_NEW": "x"})
    import os

    assert os.environ["VB_REMOTE_HOST"] == "already-set"  # not clobbered
    assert os.environ.get("VB_NEW") == "x"                # newly set


# ---------------------------------------------------------------------------
# Composed-deck mode: per-run materialization + `parameters` injection
# ---------------------------------------------------------------------------
def _deck_spec() -> SpectreDeckSpec:
    return SpectreDeckSpec(
        title="composed tb",
        stimulus="V1 (vdd 0) vsource dc=vdd\nX0 (vdd out) ota_5t",
        subckt_blocks=(
            "subckt ota_5t vdd out\nM1 (out vdd 0 0) nch_lvt w=w1 l=6e-08\nends ota_5t",
        ),
        analyses=("dcOp dc", "ac ac start=1000 stop=100000000 dec=101"),
        parameters={"vdd": 1.5, "w1": 1e-6},
    )


def test_composed_mode_materializes_staged_params_per_run(tmp_path: Path) -> None:
    bridge = _FakeBridge()
    sim = SpectreSimulator(bridge, deck_spec=_deck_spec(), deck_dir=tmp_path)
    sim.update_params({"w1": 2e-6})
    sim.apply_corner(
        Corner(
            name="ss_125C_1V35",
            model_includes=[ModelInclude(lib_file="models.scs", section="ss_lvt")],
            temp=125.0,
            supplies=[SupplyOverride(node="VDD", value=1.35)],
        ),
        model_lib_root="/opt/FOUNDRY",
    )
    sim.run(label="tb__ss")

    netlist, params = bridge.calls[-1]
    assert netlist.parent == tmp_path  # materialized under deck_dir, not the spec
    text = netlist.read_text()
    assert 'include "/opt/FOUNDRY/models.scs" section=ss_lvt' in text  # corner selection
    assert "w1=2e-06" in text                     # design param injected over the default
    assert "vdd=1.35" in text                     # corner supply wins (lowercase namespace)
    assert "tempOptions options temp=125" in text
    assert "dcOp dc" in text
    assert "finalTimeOP info what=oppoint where=rawfile" in text
    assert "subckt ota_5t vdd out" in text
    assert params["run_label"] == "tb__ss"


def test_composed_mode_each_run_is_a_fresh_deck_and_labels_are_filename_safe(
    tmp_path: Path,
) -> None:
    bridge = _FakeBridge()
    sim = SpectreSimulator(bridge, deck_spec=_deck_spec(), deck_dir=tmp_path)
    sim.run(label="tb_ac__tt_27C_1V50")
    sim.update_params({"w1": 3e-6})
    sim.run(label="tb::weird label")  # checkpoint-style separators must not hit the fs
    (first, _), (second, _) = bridge.calls
    assert first != second
    assert "w1=1e-06" in first.read_text()   # spec default at run 1
    assert "w1=3e-06" in second.read_text()  # updated staging materialized at run 2
    assert ":" not in second.name and " " not in second.name


def test_composed_mode_submit_also_materializes(tmp_path: Path) -> None:
    bridge = _FakeBridge()
    sim = SpectreSimulator(bridge, deck_spec=_deck_spec(), deck_dir=tmp_path)
    sim.submit(label="bg").result()
    netlist, _ = bridge.calls[-1]
    assert netlist.parent == tmp_path and netlist.suffix == ".scs"


def test_simulator_requires_a_netlist_or_a_deck_spec() -> None:
    with pytest.raises(ValueError, match="native_scs|deck_spec"):
        SpectreSimulator(_FakeBridge())
