"""Open-by-run-id: /api/waveview/runs, .../artifacts, /api/waveview/open_run.

Resolution is DISK truth (run.json files under WORK_ROOT), mirroring what
``optimizer_runner._run_live`` leaves behind — so these fixtures build that exact
layout (projects/<pid>/runs/<name>/{run.json, run.log, sim/run_<n>_<tb>__<corner>/…})
under a monkeypatched WORK_ROOT and never touch the runner itself.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir, synth_tran_raw


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path))
    return tmp_path


def _mk_run(base, name, run_json, *, log_lines="Note: hello\n"):
    rd = base / name
    rd.mkdir(parents=True)
    (rd / "run.json").write_text(json.dumps(run_json))
    (rd / "run.log").write_text(log_lines)
    (rd / "events.ndjson").write_text('{"iter": 1}\n')  # never an artifact
    return rd


@pytest.fixture()
def populated(work):
    """Two projects-scoped runs + one unscoped run, with trial artifacts."""
    proj = work / "projects" / "ota-abc12345"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text("project: {}\n")

    rd1 = _mk_run(
        proj / "runs", "2026-07-12_10-00_NGOpt_11111111",
        {"run_id": "1111-full-id", "project_id": "ota-abc12345", "label": "morning",
         "algorithm": "NGOpt", "status": "done", "started": "2026-07-12T10:00:00",
         "best_score": -1.5},
    )
    sim1 = rd1 / "sim" / "run_1_tb_ac__tt"
    sim1.mkdir(parents=True)
    synth_ac_raw(sim1 / "tb_ac.raw")
    (sim1 / "tb_ac.log").write_text("Note: trial 1\n")
    (sim1 / "tb_ac.net").write_text("* netlist — never an artifact\n")
    (rd1 / "checkpoints").mkdir()
    (rd1 / "checkpoints" / "auto_1.json").write_text("{}")
    sim2 = rd1 / "sim" / "run_2_tb_tran__tt"
    sim2.mkdir(parents=True)
    synth_tran_raw(sim2 / "tb_tran.raw")

    rd2 = _mk_run(
        proj / "runs", "2026-07-12_11-00_TwoPointsDE_22222222",
        {"run_id": "2222-full-id", "project_id": "ota-abc12345", "label": "later",
         "algorithm": "TwoPointsDE", "status": "running", "started": "2026-07-12T11:00:00"},
    )

    rd3 = _mk_run(
        work / "runs", "2026-07-11_09-00_NGOpt_33333333",
        {"run_id": "3333-full-id", "project_id": None, "label": None,
         "algorithm": "NGOpt", "status": "done", "started": "2026-07-11T09:00:00"},
    )
    synth_spectre_raw_dir(rd3 / "sim" / "candidate-raw")

    return {"proj_id": "ota-abc12345", "rd1": rd1, "rd2": rd2, "rd3": rd3}


# --- listing --------------------------------------------------------------------
def test_list_runs_all_scopes_newest_first(client, populated):
    r = client.get("/api/waveview/runs")
    assert r.status_code == 200, r.text
    runs = r.json()["runs"]
    assert [x["run_id"] for x in runs] == ["2222-full-id", "1111-full-id", "3333-full-id"]
    by_id = {x["run_id"]: x for x in runs}
    assert by_id["1111-full-id"]["algorithm"] == "NGOpt"
    assert by_id["1111-full-id"]["best_score"] == pytest.approx(-1.5)
    assert by_id["3333-full-id"]["project_id"] is None  # unscoped runs are included
    assert by_id["1111-full-id"]["run_dir"].endswith("2026-07-12_10-00_NGOpt_11111111")


def test_list_runs_project_scope(client, populated):
    r = client.get("/api/waveview/runs", params={"project_id": populated["proj_id"]})
    ids = {x["run_id"] for x in r.json()["runs"]}
    assert ids == {"1111-full-id", "2222-full-id"}


def test_list_runs_unknown_project_404(client, work):
    assert client.get("/api/waveview/runs", params={"project_id": "nope-00000000"}).status_code == 404


# --- artifacts ------------------------------------------------------------------
def test_run_artifacts(client, populated):
    r = client.get("/api/waveview/runs/1111-full-id/artifacts")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["run_dir"].endswith("2026-07-12_10-00_NGOpt_11111111")
    arts = {a["name"]: a["type"] for a in body["artifacts"]}
    assert arts["sim/run_1_tb_ac__tt/tb_ac.raw"] == "ngspice_raw"
    assert arts["sim/run_2_tb_tran__tt/tb_tran.raw"] == "ngspice_raw"
    assert arts["sim/run_1_tb_ac__tt/tb_ac.log"] == "log"
    assert arts["run.log"] == "log"  # the run's own log rides along for the SSE tail
    # non-artifacts never leak: netlists, checkpoints, events.ndjson, run.json
    assert not any(n.endswith((".net", ".json", ".ndjson")) for n in arts)


def test_run_artifacts_spectre_dir_is_terminal(client, populated):
    r = client.get("/api/waveview/runs/3333-full-id/artifacts")
    arts = {a["name"]: a["type"] for a in r.json()["artifacts"]}
    assert arts["sim/candidate-raw"] == "spectre_raw_dir"
    # the dir is ONE dataset — its member PSFs are not listed individually
    assert not any(n.startswith("sim/candidate-raw/") for n in arts)


def test_run_artifacts_unknown_run_404(client, populated):
    assert client.get("/api/waveview/runs/never-heard-of-it/artifacts").status_code == 404


# --- open_run ---------------------------------------------------------------------
def test_open_run_delegates_to_open(client, populated):
    r = client.post("/api/waveview/open_run", json={"run_id": "1111-full-id"})
    assert r.status_code == 200, r.text
    meta = r.json()
    assert meta["engine"] == "ngspice"
    assert meta["path"].startswith(str(populated["rd1"]))
    # same dataset_id as opening that path directly (idempotent delegation)
    again = client.post("/api/waveview/open", json={"path": meta["path"]})
    assert again.json()["dataset_id"] == meta["dataset_id"]


def test_open_run_match_filter(client, populated):
    r = client.post(
        "/api/waveview/open_run", json={"run_id": "1111-full-id", "match": "tb_ac"}
    )
    assert r.status_code == 200, r.text
    meta = r.json()
    assert meta["path"].endswith("tb_ac.raw")
    assert {a["analysis"] for a in meta["analyses"]} == {"ac"}
    # attached log was discovered beside the raw
    assert meta["log_path"] and meta["log_path"].endswith("tb_ac.log")


def test_open_run_spectre(client, populated):
    r = client.post("/api/waveview/open_run", json={"run_id": "3333-full-id"})
    assert r.status_code == 200, r.text
    assert r.json()["engine"] == "spectre"


def test_open_run_by_dir_name(client, populated):
    r = client.post(
        "/api/waveview/open_run",
        json={"run_id": "2026-07-12_10-00_NGOpt_11111111", "project_id": populated["proj_id"]},
    )
    assert r.status_code == 200, r.text


def test_open_run_no_artifacts_404(client, populated):
    r = client.post("/api/waveview/open_run", json={"run_id": "2222-full-id"})
    assert r.status_code == 404
    assert "no openable result artifacts" in r.json()["detail"]


def test_open_run_bad_match_404(client, populated):
    r = client.post(
        "/api/waveview/open_run", json={"run_id": "1111-full-id", "match": "tb_nonexistent"}
    )
    assert r.status_code == 404


# --- snapshots -------------------------------------------------------------------
import base64  # noqa: E402

_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24
_PNG_B64 = base64.b64encode(_PNG_BYTES).decode()


def test_snapshot_save_overwrite_and_fetch(client, populated):
    r = client.post(
        "/api/waveview/runs/1111-full-id/snapshot",
        json={"png_base64": _PNG_B64, "name": "AC Bode #2"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    # label slugified; snapshots live INSIDE the run dir
    assert body["rel"] == "snapshots/AC-Bode-2.png"
    assert body["size_bytes"] == len(_PNG_BYTES)
    assert (populated["rd1"] / "snapshots" / "AC-Bode-2.png").read_bytes() == _PNG_BYTES

    # a repeat save under the same name OVERWRITES (the thumbnail contract)
    r2 = client.post(
        "/api/waveview/runs/1111-full-id/snapshot",
        json={"png_base64": _PNG_B64, "name": "AC Bode #2"},
    )
    assert r2.status_code == 200 and r2.json()["rel"] == body["rel"]

    # and the existing id-addressed artifact route serves it back
    f = client.get(
        "/api/waveview/runs/1111-full-id/artifacts/file", params={"rel": body["rel"]}
    )
    assert f.status_code == 200
    assert f.content == _PNG_BYTES


def test_snapshot_rejects_bad_payloads(client, populated):
    # not base64 at all
    r = client.post(
        "/api/waveview/runs/1111-full-id/snapshot", json={"png_base64": "@@not-b64@@"}
    )
    assert r.status_code == 400
    # valid base64, but not a PNG
    r = client.post(
        "/api/waveview/runs/1111-full-id/snapshot",
        json={"png_base64": base64.b64encode(b"GIF89a not a png").decode()},
    )
    assert r.status_code == 415
    # unknown run
    r = client.post(
        "/api/waveview/runs/nope/snapshot", json={"png_base64": _PNG_B64}
    )
    assert r.status_code == 404


# --- run_netlist (drop a deck → run → waveforms) ---------------------------------
import spicexplorer_core.env as core_env  # noqa: E402


def _stub_ngspice(tmp_path, script_body: str):
    """A fake ngspice binary + a probe_env pointing at it (the route only reads
    ngspice_ok/ngspice_path)."""
    stub = tmp_path / "fake-ngspice"
    stub.write_text("#!/bin/sh\n" + script_body)
    stub.chmod(0o755)
    return {"ngspice_ok": True, "ngspice_path": str(stub)}


def test_run_netlist_happy_path(client, work, tmp_path, monkeypatch):
    raw_src = tmp_path / "src.raw"
    synth_ac_raw(raw_src)
    monkeypatch.setattr(
        core_env, "probe_env",
        lambda: _stub_ngspice(tmp_path, f"cp {raw_src} out.raw\necho 'Note: ok' > run.log\n"),
    )
    r = client.post(
        "/api/waveview/run_netlist",
        json={"content": "* tiny deck\n.end\n", "filename": "my_amp.spice"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["dataset"]["engine"] == "ngspice"
    assert body["log_tail"] == ["Note: ok"]
    # a first-class unscoped run: dir name == run_id, envelope written, deck kept
    rd = work / "runs" / body["run_id"]
    assert rd.is_dir() and (rd / "my_amp.spice").is_file()
    rec = json.loads((rd / "run.json").read_text())
    assert rec["kind"] == "netlist" and rec["status"] == "done"
    # the runs lister picks it up (label carries the deck name)
    runs = client.get("/api/waveview/runs").json()["runs"]
    mine = next(x for x in runs if x["run_id"] == body["run_id"])
    assert mine["label"] == "netlist · my_amp.spice"


def test_run_netlist_no_raw_is_422_and_run_kept(client, work, tmp_path, monkeypatch):
    monkeypatch.setattr(
        core_env, "probe_env",
        lambda: _stub_ngspice(tmp_path, "echo 'Error: no circuit' > run.log\nexit 1\n"),
    )
    r = client.post("/api/waveview/run_netlist", json={"content": "* broken\n"})
    assert r.status_code == 422
    assert "no waveform data" in r.json()["detail"]
    # the failed run dir survives for log inspection, marked error
    runs = list((work / "runs").iterdir())
    assert len(runs) == 1
    rec = json.loads((runs[0] / "run.json").read_text())
    assert rec["status"] == "error"


def test_run_netlist_validation(client, work, monkeypatch):
    # wrong extension → 415 (before any run dir is minted)
    r = client.post(
        "/api/waveview/run_netlist", json={"content": "x", "filename": "results.raw"}
    )
    assert r.status_code == 415
    # ngspice absent → 503
    monkeypatch.setattr(core_env, "probe_env", lambda: {"ngspice_ok": False})
    r = client.post("/api/waveview/run_netlist", json={"content": "* d\n.end\n"})
    assert r.status_code == 503
