"""/api/waveview LIVE Spectre proof (opt-in, `-m slow`): closed lane → API → parity.

Mirror of the ngspice live proof on the tsmc-n65 closed lane: run the amp_022 AC bench
through the in-library router (native Spectre via the bridge), then open the persisted
psfascii ``-raw`` dir through the REST viewer and check the measured AC figures match
the run's own ``evaluate()``. Same opt-in gates as the config-driven closed-lane test:
bridge importable + the neutral corner wrapper at ``SPICEXPLORER_TSMC65_MODEL_ROOT``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.slow

_MODEL_ROOT = os.environ.get("SPICEXPLORER_TSMC65_MODEL_ROOT", "")
_CIRCUIT, _PDK, _TB = "amp_022_fer_two_stage", "tsmc-n65", "ac_open_loop"


@pytest.mark.skipif(
    not (_MODEL_ROOT and (Path(_MODEL_ROOT).expanduser() / "tsmc_n65_models.scs").is_file()),
    reason="set SPICEXPLORER_TSMC65_MODEL_ROOT to a dir holding the neutral corner wrapper",
)
def test_waveview_api_live_spectre_parity(tmp_path, monkeypatch) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.analog_db import (
        AnalogDbUnavailable,
        EngineUnavailable,
        probe_engine,
        run_circuit,
    )
    from spicexplorer_api.main import app

    cap = probe_engine(_CIRCUIT, _PDK, model_lib_root=_MODEL_ROOT)
    if not cap.available:
        pytest.skip(f"closed lane unavailable: {cap.reason}")
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    try:
        run = run_circuit(
            _CIRCUIT, _PDK, testbench=_TB,
            model_lib_root=_MODEL_ROOT,
            deck_dir=tmp_path / "decks", work_dir=tmp_path / "raw",
            vb_env_file=Path(env_file).expanduser() if env_file else None,
        )
    except (AnalogDbUnavailable, EngineUnavailable) as exc:
        pytest.skip(f"analog-db closed lane unavailable: {exc}")

    engine_evals = run.evaluate(only={"dc_gain_db", "ugf_hz", "pm_deg"})
    raw_dir = getattr(run.result, "raw_dir", None)
    assert raw_dir, "closed-lane run left no persisted -raw dir"

    monkeypatch.setenv("SPICEXPLORER_WAVEVIEW_ROOTS", str(tmp_path))
    client = TestClient(app)

    meta = client.post("/api/waveview/open", json={"path": str(raw_dir)}).json()
    assert meta["engine"] == "spectre", meta
    ds_id = meta["dataset_id"]
    analyses = {a["analysis"] for a in meta["analyses"]}
    assert {"ac", "op"} <= analyses, analyses

    # per-device op-point scalars came through the .info STRUCT post-parse
    scalars = client.get(
        f"/api/waveview/datasets/{ds_id}/scalars", params={"prefix": "XDUT.XM0:"}
    ).json()["scalars"]
    assert scalars.get("XDUT.XM0:gm", 0) > 0.0, "input-pair gm missing from op scalars"

    resp = client.post(
        f"/api/waveview/datasets/{ds_id}/measure",
        json={
            "items": [
                {"name": "dc_gain_db", "recipe": {"meas": "dcgain", "out": "vout"}},
                {"name": "ugf_hz", "recipe": {"meas": "ugf", "out": "vout"}},
                {"name": "pm_deg", "recipe": {"meas": "pm", "out": "vout"}},
            ]
        },
    ).json()
    got = {r["name"]: r["value"] for r in resp["results"]}
    for name, ev in engine_evals.items():
        assert got[name] == pytest.approx(ev.value, rel=1e-9), (name, got[name], ev.value)
