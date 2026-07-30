"""Id-based run-artifact serving (project-fs P3.1b).

Two capabilities on top of the P3 ``dir == run_id`` layout:
  * ``project_service.find_run_dir`` — O(1) fast path (dir name is the run_id) with
    a legacy run.json scan fallback (the O(N) scan the P3 plan promised to kill);
  * ``GET /api/waveview/runs/{run_id}/artifacts/file`` — fetch ANY run artifact by
    identity ``(run_id, rel)``, traversal-safe, replacing an absolute-path whitelist.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app
from spicexplorer_api.services import project_service as ps


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path))
    return tmp_path


def _mk_run(base, dir_name, run_id, **extra):
    rd = base / dir_name
    rd.mkdir(parents=True)
    (rd / "run.json").write_text(json.dumps({"run_id": run_id, "status": "done", **extra}))
    (rd / "config_snapshot.yaml").write_text("ws_root: /abs/reproducible\n")
    (rd / "sim").mkdir()
    (rd / "sim" / "out.raw").write_bytes(b"RAW")
    return rd


# ---------- resolver unit tests ----------
def test_find_run_dir_fast_path_is_direct(work):
    base = ps.runs_dir(None)
    rid = "20260715-101010_optimize_abcd1234"
    rd = _mk_run(base, rid, rid)          # dir name == run_id (P3)
    assert ps.find_run_dir(None, rid) == rd


def test_find_run_dir_legacy_scan_fallback(work):
    base = ps.runs_dir(None)
    rd = _mk_run(base, "legacy-shortname", "the-full-legacy-id")  # dir != run_id
    assert ps.find_run_dir(None, "the-full-legacy-id") == rd
    assert ps.find_run_dir(None, "no-such-run") is None


def test_find_run_dir_rejects_traversal(work):
    assert ps.find_run_dir(None, "../escape") is None


def test_resolve_run_file_valid_nested_and_escape(tmp_path):
    rd = _mk_run(tmp_path, "run", "run")
    (tmp_path / "secret").write_text("nope")
    assert ps.resolve_run_file(rd, "run.json") == (rd / "run.json").resolve()
    assert ps.resolve_run_file(rd, "sim/out.raw") == (rd / "sim" / "out.raw").resolve()
    assert ps.resolve_run_file(rd, "../secret") is None    # escape rejected
    assert ps.resolve_run_file(rd, "sim") is None          # a dir, not a file
    assert ps.resolve_run_file(rd, "missing.txt") is None


# ---------- route tests ----------
def test_download_any_artifact_by_id(client, work):
    base = ps.runs_dir(None)
    rid = "20260715-101010_optimize_abcd1234"
    _mk_run(base, rid, rid)

    r = client.get(f"/api/waveview/runs/{rid}/artifacts/file",
                   params={"rel": "config_snapshot.yaml"})
    assert r.status_code == 200
    assert "ws_root: /abs/reproducible" in r.text

    # run.json is reachable by identity too (not just openable waveforms)
    assert client.get(f"/api/waveview/runs/{rid}/artifacts/file",
                      params={"rel": "run.json"}).json()["run_id"] == rid


def test_download_rejects_escape_and_missing(client, work):
    base = ps.runs_dir(None)
    rid = "20260715-101010_optimize_abcd1234"
    _mk_run(base, rid, rid)

    assert client.get(f"/api/waveview/runs/{rid}/artifacts/file",
                      params={"rel": "../../etc/passwd"}).status_code == 404
    assert client.get(f"/api/waveview/runs/{rid}/artifacts/file",
                      params={"rel": "nope.txt"}).status_code == 404
    assert client.get("/api/waveview/runs/ghost/artifacts/file",
                      params={"rel": "run.json"}).status_code == 404
