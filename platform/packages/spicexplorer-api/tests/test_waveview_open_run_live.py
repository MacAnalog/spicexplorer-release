"""LIVE end-to-end for open-by-run-id: a real optimizer run (keep_raw) → the viewer.

Drives `optimizer_runner.start_run` (the actual background-thread runner, real ngspice
on the default example project) with `keep_raw=True` and a 1-trial budget, then resolves
the finished run through /api/waveview/runs → open_run → measure. This is the pin that
keeps the fast tests' hand-built run-dir fixtures honest against what the runner really
writes (run.json fields, sim/run_<n>_<tb> layout, retained .raw files).
"""

from __future__ import annotations

import asyncio
import threading
import time

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.slow


def test_open_run_live_end_to_end(tmp_path, monkeypatch) -> None:
    from spicexplorer_core.env import probe_env

    if not probe_env().get("live_runs_enabled"):
        pytest.skip("live ngspice+PDK unavailable")

    monkeypatch.setenv("WORK_ROOT", str(tmp_path))
    from spicexplorer_api.app_config import default_yaml_path
    from spicexplorer_api.main import app
    from spicexplorer_api.services import optimizer_runner

    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()
    try:
        run_id = optimizer_runner.start_run(
            project_path=str(default_yaml_path()), budget=1, keep_raw=True, loop=loop,
        )
        deadline = time.time() + 240
        while time.time() < deadline:
            state = optimizer_runner.get_run(run_id)
            if state is None or state.done:
                break
            time.sleep(1)
        else:
            optimizer_runner.stop_run(run_id)
            pytest.fail("live run did not finish within 240 s")
    finally:
        loop.call_soon_threadsafe(loop.stop)

    client = TestClient(app)
    runs = client.get("/api/waveview/runs").json()["runs"]
    mine = [r for r in runs if r["run_id"] == run_id]
    assert mine and mine[0]["status"] == "done"
    assert mine[0]["keep_raw"] is True

    arts = client.get(f"/api/waveview/runs/{run_id}/artifacts").json()["artifacts"]
    kinds = {a["type"] for a in arts}
    assert "ngspice_raw" in kinds, f"keep_raw run retained no raw files: {sorted(a['name'] for a in arts)}"
    assert any(a["name"] == "run.log" for a in arts)

    r = client.post("/api/waveview/open_run", json={"run_id": run_id})
    assert r.status_code == 200, r.text
    meta = r.json()
    assert meta["engine"] == "ngspice"
    assert meta["analyses"], "opened trial artifact exposes no analyses"

    # the loaded artifact is measurable through the same Tier-1 registry the optimizer used
    an0 = meta["analyses"][0]
    wave_sig = next((s["name"] for s in an0["signals"] if s["name"] != an0["sweep"]), None)
    assert wave_sig is not None
