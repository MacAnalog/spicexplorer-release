"""/api/waveview LIVE ngspice proof (opt-in, `-m slow`): real deck → API → parity.

Runs the analog-db amp_022 ihp-sg13g2 AC bench through the in-library router (a real
ngspice run), then drives the produced ``.raw`` through the REST viewer: open →
waveform → measure → log. The measured ``dc_gain_db``/``ugf_hz``/``pm_deg`` must match
the run's own ``evaluate()`` (same registry, viewer-loaded data).

Skips wherever live SPICE can't run (same gates as the open-lane router test).
"""

from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.slow

_CIRCUIT, _PDK, _TB = "amp_022_fer_two_stage", "ihp-sg13g2", "ac_open_loop"


def _marker_present() -> bool:
    try:
        from spicexplorer.backends.analog_db import pdk_sim_engine

        return pdk_sim_engine(_PDK) == "ngspice"
    except Exception:
        return False


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not on PATH")
@pytest.mark.skipif(not _marker_present(), reason="analog-db ihp sim_engine marker not present")
def test_waveview_api_live_ngspice_parity(tmp_path, monkeypatch) -> None:
    from spicexplorer.backends.analog_db import AnalogDbUnavailable, probe_engine, run_circuit
    from spicexplorer_api.main import app

    cap = probe_engine(_CIRCUIT, _PDK)
    if not cap.available:
        pytest.skip(f"open lane unavailable: {cap.reason}")
    try:
        run = run_circuit(_CIRCUIT, _PDK, testbench=_TB, output_dir=str(tmp_path / "out"))
    except AnalogDbUnavailable as exc:
        pytest.skip(f"analog-db open lane unavailable: {exc}")

    engine_evals = run.evaluate(only={"dc_gain_db", "ugf_hz", "pm_deg"})
    raws = sorted((tmp_path / "out").rglob("*.raw"))
    assert raws, "live run left no .raw artifact"

    monkeypatch.setenv("SPICEXPLORER_WAVEVIEW_ROOTS", str(tmp_path))
    client = TestClient(app)

    meta = client.post("/api/waveview/open", json={"path": str(raws[0])}).json()
    assert meta["engine"] == "ngspice", meta
    ds_id = meta["dataset_id"]
    assert meta["log_path"], "run log should be discovered next to the raw"

    # waveform: the AC transfer is present, complex, downsampled on request
    wave = client.get(
        f"/api/waveview/datasets/{ds_id}/wave",
        params={"analysis": "ac", "signals": "v(vout)", "max_points": 256},
    ).json()
    sig = wave["signals"][0]
    assert sig["n_total"] >= 100 and sig["n_returned"] <= 256

    # measurements: identical values to the run's own registry evaluation
    resp = client.post(
        f"/api/waveview/datasets/{ds_id}/measure",
        json={
            "items": [
                {"name": "dc_gain_db", "recipe": {"meas": "dcgain", "out": "v(vout)"}},
                {"name": "ugf_hz", "recipe": {"meas": "ugf", "out": "v(vout)"}},
                {"name": "pm_deg", "recipe": {"meas": "pm", "out": "v(vout)"}},
            ]
        },
    ).json()
    got = {r["name"]: r["value"] for r in resp["results"]}
    for name, ev in engine_evals.items():
        assert got[name] == pytest.approx(ev.value, rel=1e-9), (name, got[name], ev.value)

    # log viewer: the live ngspice log parses with zero errors
    log = client.get(f"/api/waveview/datasets/{ds_id}/log").json()
    assert log["counts"]["error"] == 0
    assert log["n_lines"] > 5
