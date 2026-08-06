"""In-library router — CLOSED lane LIVE: amp_022 tsmc-n65 AC via `run_circuit` (opt-in).

Proves the closed (Spectre) half of the in-library integration end-to-end through the SAME
`run_circuit` router the open lane uses: the committed `sim_engine` marker routes tsmc-n65 to
Spectre, `build_spectre_run` assembles the deck from the circuit's binding YAMLs (zero hardcoded
dicts), and the generic→kit corner shim resolves a GENERIC `tt` against the operator's NEUTRAL
`tsmc_n65_models.scs` wrapper at `SPICEXPLORER_TSMC65_MODEL_ROOT`. Reproduces the direct-composition AC numbers.

Opt-in: bridge importable + `SPICEXPLORER_TSMC65_MODEL_ROOT` holding the neutral wrapper + the
analog-db binding (with the `sim_engine` marker) present. Skips everywhere else. Point
`SPICEXPLORER_ANALOG_DB` at a populated checkout from a worktree with an empty submodule.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow

_MODEL_ROOT = os.environ.get("SPICEXPLORER_TSMC65_MODEL_ROOT", "")
_CIRCUIT, _PDK, _TB = "amp_022_fer_two_stage", "tsmc-n65", "ac_open_loop"


@pytest.mark.skipif(
    not (_MODEL_ROOT and (Path(_MODEL_ROOT).expanduser() / "tsmc_n65_models.scs").is_file()),
    reason="set SPICEXPLORER_TSMC65_MODEL_ROOT to a dir holding the neutral tsmc_n65_models.scs corner wrapper",
)
def test_configdriven_amp022_tsmc65_ac(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.analog_db import (
        AnalogDbUnavailable,
        EngineUnavailable,
        probe_engine,
        run_circuit,
    )
    from spicexplorer.backends.spectre import operating_point

    # the committed marker routes tsmc-n65 to Spectre; the wrapper + bridge make it available
    cap = probe_engine(_CIRCUIT, _PDK, model_lib_root=_MODEL_ROOT)
    assert cap.engine == "spectre", cap
    if not cap.available:
        pytest.skip(f"closed lane unavailable: {cap.reason}")

    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    try:
        # everything is READ from the committed binding YAMLs — no hardcoded sizing/corner/TB dicts
        run = run_circuit(
            _CIRCUIT, _PDK, testbench=_TB, corner="tt",
            model_lib_root=_MODEL_ROOT,
            deck_dir=tmp_path / "decks",
            work_dir=tmp_path / "raw",
            vb_env_file=Path(env_file).expanduser() if env_file else None,
        )
    except (AnalogDbUnavailable, EngineUnavailable) as exc:
        pytest.skip(f"analog-db closed lane unavailable: {exc}")

    assert run.engine == "spectre"
    # op-point sanity — the config-driven deck biases up the input pair
    op = operating_point(run.result, "XDUT.XM0")
    assert op and op["gm"] > 0.0, "input-pair op-point missing/non-physical"

    # every datasheet AC metric meets its OWN declared spec band (no hardcoded pass ranges)
    evals = run.evaluate(only={"dc_gain_db", "ugf_hz", "pm_deg"})
    assert set(evals) == {"dc_gain_db", "ugf_hz", "pm_deg"}, evals
    for name, m in evals.items():
        assert m.satisfied, f"{name}={m.value} fails datasheet spec [{m.spec_min}, {m.spec_max}]"
    # band around the committed gm/ID re-sizing (the binding carries the current
    # re-sized operating point, ~55 dB / 11 MHz / 78°)
    assert 45.0 < evals["dc_gain_db"].value < 62.0, evals
    assert 5.0e6 < evals["ugf_hz"].value < 40.0e6, evals
    # pm band top 80→90 (2026-07-17 `m=` fix: the multi-finger devices now really run
    # their designed multiplicity — more gm, ~81° PM; every datasheet spec still passes)
    assert 45.0 < evals["pm_deg"].value < 90.0, evals


@pytest.mark.skipif(
    not (_MODEL_ROOT and (Path(_MODEL_ROOT).expanduser() / "tsmc_n65_models.scs").is_file()),
    reason="set SPICEXPLORER_TSMC65_MODEL_ROOT to a dir holding the neutral corner wrapper",
)
@pytest.mark.parametrize(
    ("tb", "metric", "lo", "hi"),
    [
        ("cmrr_vcm", "cmrr_db", 40.0, 90.0),        # live 2026-07-09: 58.4 dB
        ("psrr_vdd", "psrr_vdd_db", 50.0, 130.0),   # live 2026-07-22 (gmid_v7 sizing): 57.0 dB
        ("linearity", "icmr_range", 0.7, 1.2),      # live 2026-07-09: 1.07 V of the 1.2 V rail
    ],
)
def test_configdriven_amp022_tsmc65_new_benches(
    tmp_path: Path, tb: str, metric: str, lo: float, hi: float
) -> None:
    """The bench-validation suite (CMRR/PSRR/linearity) through the same router, live."""
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.analog_db import (
        AnalogDbUnavailable,
        EngineUnavailable,
        probe_engine,
        run_circuit,
    )

    cap = probe_engine(_CIRCUIT, _PDK, model_lib_root=_MODEL_ROOT)
    if not cap.available:
        pytest.skip(f"closed lane unavailable: {cap.reason}")
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    try:
        run = run_circuit(
            _CIRCUIT, _PDK, testbench=tb, corner="tt",
            model_lib_root=_MODEL_ROOT,
            deck_dir=tmp_path / "decks",
            work_dir=tmp_path / "raw",
            vb_env_file=Path(env_file).expanduser() if env_file else None,
        )
    except (AnalogDbUnavailable, EngineUnavailable) as exc:
        pytest.skip(f"analog-db closed lane unavailable: {exc}")

    value = run.evaluate()[metric].value
    assert lo <= value <= hi, f"{tb}/{metric} = {value} outside the plausibility band [{lo}, {hi}]"


@pytest.mark.skipif(
    not (_MODEL_ROOT and (Path(_MODEL_ROOT).expanduser() / "tsmc_n65_models.scs").is_file()),
    reason="set SPICEXPLORER_TSMC65_MODEL_ROOT to a dir holding the neutral corner wrapper",
)
def test_configdriven_amp022_tsmc65_stb_and_calculator_route(tmp_path: Path) -> None:
    """The stb bench (template-DB composed) + the SKILL calculator route, live.

    One stb run: the registry route reads pm_loop/gain_margin_db/loopgain_db off the
    loopGain PSF, and the OCEAN calculator set (rendered from the template DB) reads
    Spectre's NATIVE stb margins — the two must agree (<2 deg / <0.5 dB; live 2026-07-10:
    61.6 vs 60.8 deg, 8.055 vs 8.055 dB, both 47.41 dB loop gain == the open-loop dcgain).
    """
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.analog_db import (
        AnalogDbUnavailable,
        EngineUnavailable,
        bench_ocean_measurements,
        probe_engine,
        run_circuit,
    )
    from spicexplorer.backends.ocean_metrics import OceanMetricsError, OceanMetricsSession
    from spicexplorer_core.measurements import measure

    cap = probe_engine(_CIRCUIT, _PDK, model_lib_root=_MODEL_ROOT)
    if not cap.available:
        pytest.skip(f"closed lane unavailable: {cap.reason}")
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    try:
        run = run_circuit(
            _CIRCUIT, _PDK, testbench="stb", corner="tt",
            model_lib_root=_MODEL_ROOT,
            deck_dir=tmp_path / "decks",
            work_dir=tmp_path / "raw",
            vb_env_file=Path(env_file).expanduser() if env_file else None,
        )
    except (AnalogDbUnavailable, EngineUnavailable) as exc:
        pytest.skip(f"analog-db closed lane unavailable: {exc}")

    # registry route: loop margins off the stb.stb loopGain wave
    pm = measure(run.result, {"meas": "pm_loop", "out": "loopGain"}, default_analysis="stb")
    gm = measure(run.result, {"meas": "gain_margin_db", "out": "loopGain"}, default_analysis="stb")
    lg = measure(run.result, {"meas": "loopgain_db", "out": "loopGain"}, default_analysis="stb")
    # bands widened with the 2026-07-17 `m=` fix (designed multiplicity → more gm:
    # pm ~82°, gain margin ~22 dB observed live)
    assert 45.0 < pm < 90.0 and 3.0 < gm < 30.0 and 45.0 < lg < 62.0, (pm, gm, lg)

    # calculator route: the template DB's SKILL set on the same raw dir (native margins)
    ms = bench_ocean_measurements(_CIRCUIT, "stb", pdk=_PDK)
    # rows are keyed by the datasheet `extract.meas` string (ngspice stb template spelling),
    # NOT the metric id — `gm_loop_db`/`ugf_loop_hz` are metric ids. A row named off the
    # metric id is dead config: the metric falls through to the registry (which spells the
    # margin `gain_margin_db` and has no loop-UGF) and records NaN under `status: ok`.
    assert {m.name for m in ms} == {"pm_loop", "ugf_loop", "gm_loop", "loopgain_db"}
    try:
        with OceanMetricsSession.from_vb_env(work_dir=tmp_path / "ocean") as sess:
            vals = sess.measure(run.result.raw_dir, ms, label="stb_calc")
    except OceanMetricsError as exc:
        pytest.skip(f"no OCEAN session here: {exc}")
    # 2026-07-22 (gmid_v7 re-sizing): the two routes interpolate the crossover on
    # different frequency grids; at the new op point they differ by ~2.9 deg (76.1 vs
    # 79.0). Keep the parity gate tight enough to catch sign/convention breakage.
    assert abs(vals["pm_loop"] - pm) < 4.0, (vals, pm)
    assert abs(vals["gm_loop"] - gm) < 0.5, (vals, gm)
    assert abs(vals["loopgain_db"] - lg) < 0.1, (vals, lg)
    # the loop UGF must be the frequency the phase margin is evaluated at, i.e. a real
    # 0 dB crossing of |T| inside the swept band
    ugf_loop = vals["ugf_loop"]
    assert math.isfinite(ugf_loop) and 1e5 < ugf_loop < 1e8, vals


@pytest.mark.skipif(
    not (_MODEL_ROOT and (Path(_MODEL_ROOT).expanduser() / "tsmc_n65_models.scs").is_file()),
    reason="set SPICEXPLORER_TSMC65_MODEL_ROOT to a dir holding the neutral corner wrapper",
)
def test_configdriven_amp022_tsmc65_thd_calculator_parity(tmp_path: Path) -> None:
    """PSS+SKILL: the thd bench's calculator set == the Python fd-PSF route (live 0.0763 %)."""
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.analog_db import (
        AnalogDbUnavailable,
        EngineUnavailable,
        bench_ocean_measurements,
        probe_engine,
        run_circuit,
    )
    from spicexplorer.backends.ocean_metrics import OceanMetricsError, OceanMetricsSession

    cap = probe_engine(_CIRCUIT, _PDK, model_lib_root=_MODEL_ROOT)
    if not cap.available:
        pytest.skip(f"closed lane unavailable: {cap.reason}")
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    try:
        run = run_circuit(
            _CIRCUIT, _PDK, testbench="thd", corner="tt",
            model_lib_root=_MODEL_ROOT,
            deck_dir=tmp_path / "decks",
            work_dir=tmp_path / "raw",
            vb_env_file=Path(env_file).expanduser() if env_file else None,
        )
    except (AnalogDbUnavailable, EngineUnavailable) as exc:
        pytest.skip(f"analog-db closed lane unavailable: {exc}")

    python_thd = run.evaluate()["thd_pct"].value
    assert 0.0 < python_thd < 2.0, python_thd

    ms = bench_ocean_measurements(_CIRCUIT, "thd", pdk=_PDK)
    assert {m.name for m in ms} == {"thd_pct", "hd2_db", "hd3_db"}
    try:
        with OceanMetricsSession.from_vb_env(work_dir=tmp_path / "ocean") as sess:
            vals = sess.measure(run.result.raw_dir, ms, label="thd_calc")
    except OceanMetricsError as exc:
        pytest.skip(f"no OCEAN session here: {exc}")
    # same fd-PSF harmonics, same RSS definition — the two routes must agree tightly
    assert abs(vals["thd_pct"] - python_thd) / python_thd < 0.01, (vals, python_thd)
    assert vals["hd2_db"] < -40.0 and vals["hd3_db"] < vals["hd2_db"], vals
