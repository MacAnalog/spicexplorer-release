"""Waveview maintenance surfaces: merged open_run, run pruning, uploads GC.

- POST /waveview/open_run {merge: true} — several per-testbench raws as ONE dataset
- POST /waveview/runs/{run_id}/prune — the keep_raw disk-hog escape hatch (core GC)
- GET/DELETE /waveview/uploads — staged-upload inventory + removal
- sweep_stale_uploads() — the opportunistic TTL sweep

All synthetic (no SPICE) under a monkeypatched WORK_ROOT.
"""

from __future__ import annotations

import json
import os
import time

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app
from spicexplorer_api.routes.waveview import sweep_stale_uploads
from spicexplorer_waveview.testing import synth_ac_raw, synth_tran_raw


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path))
    return tmp_path


def _mk_run(base, name, run_json):
    rd = base / name
    rd.mkdir(parents=True)
    (rd / "run.json").write_text(json.dumps(run_json))
    (rd / "run.log").write_text("Note: hello\n")
    return rd


@pytest.fixture()
def multi_tb_run(work):
    """One finished unscoped run with an ac and a tran testbench raw."""
    rd = _mk_run(
        work / "runs", "20260719-010000_simulate_aaaaaaaa",
        {"run_id": "20260719-010000_simulate_aaaaaaaa", "project_id": None,
         "status": "done", "started": "2026-07-19T01:00:00", "keep_raw": True},
    )
    ac = rd / "sim" / "run_1_tb_ac"
    ac.mkdir(parents=True)
    synth_ac_raw(ac / "tb_ac.raw")
    tran = rd / "sim" / "run_1_tb_tran"
    tran.mkdir(parents=True)
    synth_tran_raw(tran / "tb_tran.raw")
    return rd


# --- open_run merge -------------------------------------------------------------
def test_open_run_merge_combines_testbench_raws(client, multi_tb_run):
    res = client.post("/api/waveview/open_run",
                      json={"run_id": multi_tb_run.name, "merge": True})
    assert res.status_code == 200, res.text
    body = res.json()
    keys = {a["analysis"] for a in body["analyses"]}
    assert keys == {"ac", "tran"}
    # provenance: each analysis names its trial folder
    natives = {a["analysis"]: a["native_name"] for a in body["analyses"]}
    assert "run_1_tb_ac" in natives["ac"]
    assert "run_1_tb_tran" in natives["tran"]
    # the run's own run.log is the merged log
    assert body["log_path"].endswith("run.log")
    # idempotent: same members → same merged dataset id
    res2 = client.post("/api/waveview/open_run",
                       json={"run_id": multi_tb_run.name, "merge": True})
    assert res2.json()["dataset_id"] == body["dataset_id"]
    # merged /wave serves the suffix-free primary analysis
    wave = client.get(f"/api/waveview/datasets/{body['dataset_id']}/wave",
                      params={"analysis": "tran", "signals": "v(vout)"})
    assert wave.status_code == 200, wave.text


def test_open_run_merge_suffixes_colliding_analyses(client, work):
    rd = _mk_run(
        work / "runs", "20260719-020000_simulate_bbbbbbbb",
        {"run_id": "20260719-020000_simulate_bbbbbbbb", "project_id": None,
         "status": "done", "started": "2026-07-19T02:00:00"},
    )
    for trial in ("run_1_tb_ac", "run_2_tb_ac"):
        d = rd / "sim" / trial
        d.mkdir(parents=True)
        synth_ac_raw(d / "tb_ac.raw")
    res = client.post("/api/waveview/open_run", json={"run_id": rd.name, "merge": True})
    assert res.status_code == 200, res.text
    keys = sorted(a["analysis"] for a in res.json()["analyses"])
    assert keys == ["ac", "ac#2"]


def test_open_run_merge_single_artifact_is_plain_open(client, work):
    rd = _mk_run(
        work / "runs", "20260719-030000_simulate_cccccccc",
        {"run_id": "20260719-030000_simulate_cccccccc", "project_id": None,
         "status": "done", "started": "2026-07-19T03:00:00"},
    )
    d = rd / "sim" / "run_1_tb_ac"
    d.mkdir(parents=True)
    synth_ac_raw(d / "tb_ac.raw")
    res = client.post("/api/waveview/open_run", json={"run_id": rd.name, "merge": True})
    assert res.status_code == 200, res.text
    assert res.json()["path"].endswith("tb_ac.raw")  # not the run dir


# --- run prune ------------------------------------------------------------------
def test_prune_dry_run_then_prune_evicts_datasets(client, multi_tb_run):
    opened = client.post("/api/waveview/open_run",
                         json={"run_id": multi_tb_run.name, "merge": True}).json()
    dry = client.post(f"/api/waveview/runs/{multi_tb_run.name}/prune",
                      params={"dry_run": "true"})
    assert dry.status_code == 200, dry.text
    body = dry.json()
    assert body["dry_run"] is True and body["pruned"] is False
    assert "sim" in body["removed"] and body["freed_bytes"] > 0
    assert (multi_tb_run / "sim").is_dir()  # nothing deleted yet

    real = client.post(f"/api/waveview/runs/{multi_tb_run.name}/prune")
    assert real.status_code == 200, real.text
    body = real.json()
    assert body["pruned"] is True and body["closed_datasets"] >= 1
    assert not (multi_tb_run / "sim").exists()
    assert (multi_tb_run / "run.log").is_file()  # metrics/logs survive
    rec = json.loads((multi_tb_run / "run.json").read_text())
    assert rec["retention_pruned"]["tier"] == "metrics_only"
    # the viewer no longer serves the evicted merged dataset
    assert client.get(f"/api/waveview/datasets/{opened['dataset_id']}").status_code == 404
    # idempotent: a second prune is a no-op
    again = client.post(f"/api/waveview/runs/{multi_tb_run.name}/prune").json()
    assert again["pruned"] is False and again["skipped"] == "already applied"


def test_prune_refuses_running_run(client, work):
    rd = _mk_run(
        work / "runs", "20260719-040000_optimize_dddddddd",
        {"run_id": "20260719-040000_optimize_dddddddd", "project_id": None,
         "status": "running", "started": "2026-07-19T04:00:00"},
    )
    (rd / "sim").mkdir()
    res = client.post(f"/api/waveview/runs/{rd.name}/prune")
    assert res.status_code == 200
    body = res.json()
    assert body["pruned"] is False and "not terminal" in (body["skipped"] or "")
    assert (rd / "sim").is_dir()


# --- uploads GC -----------------------------------------------------------------
def test_uploads_list_and_delete(client, work, tmp_path):
    src = tmp_path / "tb_ac.raw"
    synth_ac_raw(src)
    up = client.post("/api/waveview/upload",
                     files={"file": ("tb_ac.raw", src.read_bytes(),
                                     "application/octet-stream")}).json()
    listing = client.get("/api/waveview/uploads").json()["uploads"]
    mine = [u for u in listing if u["upload_id"] == up["upload_id"]]
    assert len(mine) == 1
    assert mine[0]["n_files"] == 1 and mine[0]["size_bytes"] > 0
    assert up["dataset"]["dataset_id"] in mine[0]["open_dataset_ids"]

    res = client.delete(f"/api/waveview/uploads/{up['upload_id']}")
    assert res.status_code == 200 and res.json()["deleted"] is True
    assert res.json()["closed_datasets"] == 1
    assert not (work / "waveview_uploads" / up["upload_id"]).exists()
    ds = client.get(f"/api/waveview/datasets/{up['dataset']['dataset_id']}")
    assert ds.status_code == 404
    # unknown / traversal-shaped ids are 404, never path ops
    assert client.delete("/api/waveview/uploads/nope").status_code == 404
    assert client.delete("/api/waveview/uploads/%2e%2e").status_code == 404


def test_sweep_removes_stale_keeps_fresh_and_open(client, work):
    uploads = work / "waveview_uploads"
    old = time.time() - 15 * 86400  # default TTL is 14 days

    stale = uploads / "aaaaaaaaaaaa"
    stale.mkdir(parents=True)
    (stale / "junk.raw").write_bytes(b"x")
    os.utime(stale, (old, old))

    fresh = uploads / "bbbbbbbbbbbb"
    fresh.mkdir()
    (fresh / "keep.raw").write_bytes(b"x")

    held = uploads / "cccccccccccc"
    held.mkdir()
    synth_ac_raw(held / "tb_ac.raw")
    opened = client.post("/api/waveview/open",
                         json={"path": str(held / "tb_ac.raw")})
    assert opened.status_code == 200, opened.text
    os.utime(held, (old, old))

    assert sweep_stale_uploads() == 1
    assert not stale.exists()
    assert fresh.exists()
    assert held.exists()  # backing an open dataset — protected


def test_sweep_disabled_by_env(work, monkeypatch):
    monkeypatch.setenv("SPICEXPLORER_UPLOAD_TTL_DAYS", "0")
    uploads = work / "waveview_uploads"
    stale = uploads / "eeeeeeeeeeee"
    stale.mkdir(parents=True)
    old = time.time() - 100 * 86400
    os.utime(stale, (old, old))
    assert sweep_stale_uploads() == 0
    assert stale.exists()
