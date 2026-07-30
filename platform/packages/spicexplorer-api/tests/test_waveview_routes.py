"""/api/waveview/* route tests — whitelist posture, waves, measurements, logs, SSE tail.

The tmp_path fixtures sit OUTSIDE the repo/work roots, so every test that should
succeed opts in via ``SPICEXPLORER_WAVEVIEW_ROOTS`` — which simultaneously exercises
the env-extension path and keeps the 403 default posture honest.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def allowed_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("SPICEXPLORER_WAVEVIEW_ROOTS", str(tmp_path))
    return tmp_path


@pytest.fixture()
def ac_raw(allowed_tmp):
    path = allowed_tmp / "tb_ac.raw"
    truth = synth_ac_raw(path)
    (allowed_tmp / "tb_ac.log").write_text(
        "Note: Compatibility modes selected: a\nWarning: something minor\nError: nothing fatal really\n"
    )
    return path, truth


def _open(client, path, **extra):
    resp = client.post("/api/waveview/open", json={"path": str(path), **extra})
    assert resp.status_code == 200, resp.text
    return resp.json()


# --- whitelist posture --------------------------------------------------------
def test_open_outside_roots_403(client):
    resp = client.post("/api/waveview/open", json={"path": "/etc/hostname"})
    assert resp.status_code == 403
    assert "allowed roots" in resp.json()["detail"]


def test_open_relative_path_400(client):
    resp = client.post("/api/waveview/open", json={"path": "relative/tb.raw"})
    assert resp.status_code == 400


def test_open_missing_404(client, allowed_tmp):
    resp = client.post("/api/waveview/open", json={"path": str(allowed_tmp / "nope.raw")})
    assert resp.status_code == 404


def test_traversal_escape_403(client, allowed_tmp):
    sneaky = allowed_tmp / ".." / ".." / "etc" / "hostname"
    resp = client.post("/api/waveview/open", json={"path": str(sneaky)})
    assert resp.status_code == 403


# --- open / meta / lifecycle -----------------------------------------------------
def test_open_meta_and_idempotency(client, ac_raw):
    path, truth = ac_raw
    meta = _open(client, path)
    assert meta["engine"] == "ngspice"
    assert meta["log_path"] and meta["log_path"].endswith("tb_ac.log")
    analyses = {a["analysis"]: a for a in meta["analyses"]}
    assert analyses["ac"]["sweep"] == "frequency"
    names = {s["name"] for s in analyses["ac"]["signals"]}
    assert {"frequency", "v(vout)"} <= names
    assert any(s["complex"] for s in analyses["ac"]["signals"])

    again = _open(client, path)
    assert again["dataset_id"] == meta["dataset_id"]

    listed = client.get("/api/waveview/datasets").json()["datasets"]
    assert meta["dataset_id"] in {d["dataset_id"] for d in listed}

    got = client.get(f"/api/waveview/datasets/{meta['dataset_id']}")
    assert got.status_code == 200

    closed = client.delete(f"/api/waveview/datasets/{meta['dataset_id']}").json()
    assert closed == {"closed": True}
    assert client.get(f"/api/waveview/datasets/{meta['dataset_id']}").status_code == 404


def test_open_spectre_dir(client, allowed_tmp):
    d = allowed_tmp / "amp-raw"
    synth_spectre_raw_dir(d)
    meta = _open(client, d)
    assert meta["engine"] == "spectre"
    keys = {a["analysis"] for a in meta["analyses"]}
    assert {"ac", "dc", "op", "tran", "noise", "pss", "stb"} <= keys


# --- waves --------------------------------------------------------------------
def test_wave_auto_and_downsample(client, ac_raw):
    path, truth = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    r = client.get(
        f"/api/waveview/datasets/{ds_id}/wave",
        params={"analysis": "ac", "signals": "v(vout)", "max_points": 64, "method": "lttb"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    sig = body["signals"][0]
    assert sig["downsampled"] is True
    assert sig["n_total"] == truth["n"]
    assert sig["n_returned"] <= 64
    assert len(sig["x"]) == sig["n_returned"] == len(sig["y"])
    assert body["x_name"] == "frequency"


def test_wave_complex_fmt(client, ac_raw):
    path, _ = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    r = client.get(
        f"/api/waveview/datasets/{ds_id}/wave",
        params={"analysis": "ac", "signals": "v(vout)", "fmt": "complex", "method": "none"},
    )
    sig = r.json()["signals"][0]
    assert sig["y"] is None
    assert len(sig["y_re"]) == len(sig["y_im"]) == sig["n_total"]
    # strict JSON: response text must not contain bare NaN/Infinity tokens
    assert "NaN" not in r.text and "Infinity" not in r.text


def test_wave_errors(client, ac_raw):
    path, _ = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    assert client.get(
        f"/api/waveview/datasets/{ds_id}/wave", params={"analysis": "tran", "signals": "v(vout)"}
    ).status_code == 404
    assert client.get(
        f"/api/waveview/datasets/{ds_id}/wave", params={"analysis": "ac", "signals": "v(nope)"}
    ).status_code == 404
    assert client.get(
        f"/api/waveview/datasets/{ds_id}/wave",
        params={"analysis": "ac", "signals": "v(vout)", "fmt": "bogus"},
    ).status_code == 422
    assert client.get(
        "/api/waveview/datasets/nonexistent/wave", params={"analysis": "ac", "signals": "x"}
    ).status_code == 404


# --- measurements ------------------------------------------------------------------
def test_measure_endpoint(client, ac_raw):
    path, truth = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    r = client.post(
        f"/api/waveview/datasets/{ds_id}/measure",
        json={
            "items": [
                {"name": "gain", "recipe": {"meas": "dcgain", "out": "v(vout)"}},
                {"recipe": {"meas": "ugf", "out": "v(vout)"}},
                {"name": "bad", "recipe": {"meas": "dcgain", "out": "v(nope)"}},
            ]
        },
    )
    assert r.status_code == 200, r.text
    results = {x["name"]: x for x in r.json()["results"]}
    assert results["gain"]["value"] == pytest.approx(truth["dcgain_db"], abs=0.01)
    assert results["ugf"]["value"] == pytest.approx(truth["ugf_hz"], rel=0.02)
    assert results["bad"]["value"] is None and "no signal" in results["bad"]["error"]


def test_measure_null_arg_degrades_per_item(client, ac_raw):
    """A JSON-null recipe arg passes presence validation; it must degrade to a per-item
    error (TypeError from the registry's float() cast), never 500 the whole batch."""
    path, truth = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    r = client.post(
        f"/api/waveview/datasets/{ds_id}/measure",
        json={
            "items": [
                {"name": "bad", "recipe": {"meas": "thd", "out": "v(vout)", "f0": None}},
                {"name": "gain", "recipe": {"meas": "dcgain", "out": "v(vout)"}},
            ]
        },
    )
    assert r.status_code == 200, r.text
    results = {x["name"]: x for x in r.json()["results"]}
    assert results["bad"]["value"] is None and results["bad"]["error"]
    assert results["gain"]["value"] == pytest.approx(truth["dcgain_db"], abs=0.01)


def test_wave_method_none_respects_budget(client, ac_raw):
    """method=none must not bypass the point budget — 422 instead of a giant payload."""
    path, truth = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    r = client.get(
        f"/api/waveview/datasets/{ds_id}/wave",
        params={"analysis": "ac", "signals": "v(vout)", "method": "none", "max_points": 64},
    )
    assert r.status_code == 422
    assert "max_points" in r.json()["detail"]
    ok = client.get(
        f"/api/waveview/datasets/{ds_id}/wave",
        params={"analysis": "ac", "signals": "v(vout)", "method": "none",
                "max_points": truth["n"]},
    )
    assert ok.status_code == 200
    assert ok.json()["signals"][0]["n_returned"] == truth["n"]


def test_measurement_catalog_route(client):
    r = client.get("/api/waveview/measurements")
    assert r.status_code == 200
    cat = r.json()["measurements"]
    assert "dcgain" in cat and "thd_pss" in cat and "pm_loop" in cat
    assert cat["thd"]["required"] == ["out", "f0"]


def test_scalars_route(client, allowed_tmp):
    d = allowed_tmp / "amp2-raw"
    synth_spectre_raw_dir(d)
    ds_id = _open(client, d)["dataset_id"]
    r = client.get(f"/api/waveview/datasets/{ds_id}/scalars", params={"prefix": "X0.M0:"})
    assert r.status_code == 200
    scalars = r.json()["scalars"]
    assert scalars["X0.M0:gm"] == pytest.approx(1e-3)
    assert all(k.startswith("X0.M0:") for k in scalars)


# --- logs ------------------------------------------------------------------------
def test_log_endpoint(client, ac_raw):
    path, _ = ac_raw
    ds_id = _open(client, path)["dataset_id"]
    r = client.get(f"/api/waveview/datasets/{ds_id}/log")
    assert r.status_code == 200
    body = r.json()
    assert body["counts"]["warning"] == 1 and body["counts"]["error"] == 1
    r2 = client.get(f"/api/waveview/datasets/{ds_id}/log", params={"min_level": "error"})
    assert [ln["level"] for ln in r2.json()["lines"]] == ["error"]


def test_log_stream_drain(client, allowed_tmp):
    log = allowed_tmp / "live.log"
    log.write_text("line one\nWarning: two\nError: three\n")
    events = []
    with client.stream(
        "GET",
        "/api/waveview/log/stream",
        params={"path": str(log), "follow": "false"},
    ) as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        for chunk in resp.iter_lines():
            events.append(chunk)
    data_lines = [json.loads(e[6:]) for e in events if e.startswith("data: ") and e != "data: {}"]
    levels = [d.get("level") for d in data_lines if "level" in d]
    assert levels == ["info", "warning", "error"]
    assert any(e.startswith("event: eof") for e in events)


def test_log_stream_whitelist(client):
    r = client.get("/api/waveview/log/stream", params={"path": "/etc/hostname"})
    assert r.status_code == 403


def test_log_stream_rejects_non_log_files(client, ac_raw):
    """The SSE tail is not a generic file reader — non-log-shaped names are refused."""
    path, _ = ac_raw  # a .raw under the whitelisted root
    r = client.get("/api/waveview/log/stream", params={"path": str(path)})
    assert r.status_code == 400
    assert "Not a simulator log" in r.json()["detail"]


# --- browse -------------------------------------------------------------------------
def test_browse(client, allowed_tmp):
    synth_ac_raw(allowed_tmp / "a.raw")
    synth_spectre_raw_dir(allowed_tmp / "sp-raw")
    (allowed_tmp / "notes.txt").write_text("ignored")
    (allowed_tmp / "run.log").write_text("Note: hi")
    (allowed_tmp / "plain_dir").mkdir()
    r = client.get("/api/waveview/browse", params={"dir": str(allowed_tmp)})
    assert r.status_code == 200
    entries = {e["name"]: e["type"] for e in r.json()["entries"]}
    assert entries["a.raw"] == "ngspice_raw"
    assert entries["sp-raw"] == "spectre_raw_dir"
    assert entries["run.log"] == "log"
    assert entries["plain_dir"] == "dir"
    assert "notes.txt" not in entries


def test_browse_outside_roots(client):
    assert client.get("/api/waveview/browse", params={"dir": "/etc"}).status_code == 403
