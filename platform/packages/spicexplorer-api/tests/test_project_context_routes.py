"""Agent context surface over HTTP (project-fs P5c): state / context / decisions + kind filter.

These expose the P4/P5 kernel (build_state, render_project_md, append_decision) so an MCP
server or the UI reads "where is this design at" without globbing — plan §3.6/D-10.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path))
    return tmp_path


@pytest.fixture()
def client(work):
    return TestClient(app)


@pytest.fixture()
def project(work):
    pid = "ota-0a1b2c3d"
    pdir = work / "projects" / pid
    pdir.mkdir(parents=True)
    (pdir / "project.yaml").write_text("ws_root: .\n")  # project_exists checks this
    return pid


def test_state_endpoint_returns_rollup(client, project):
    r = client.get(f"/api/projects/{project}/state")
    assert r.status_code == 200
    body = r.json()
    assert {"compliance", "best_runs", "cells", "compliance_summary"} <= set(body)
    assert body["project"]["id"] == project


def test_decisions_append_then_render_context(client, project):
    r = client.post(f"/api/projects/{project}/decisions",
                    json={"summary": "chose folded cascode", "by": "agent", "kind": "topology"})
    assert r.status_code == 200 and r.json()["ok"] is True

    ctx = client.get(f"/api/projects/{project}/context")
    assert ctx.status_code == 200
    body = ctx.json()
    assert "chose folded cascode" in body["markdown"]
    assert "GENERATED" in body["markdown"]
    assert len(body["decisions"]) == 1 and body["decisions"][0]["by"] == "agent"


def test_runs_kind_filter(client, project):
    # No runs yet — the filter is a passthrough that must not error.
    assert client.get(f"/api/projects/{project}/runs", params={"kind": "xschem"}).json()["runs"] == []
    assert client.get(f"/api/projects/{project}/runs").json()["runs"] == []


def test_get_state_and_context_are_side_effect_free(client, project, work):
    # A GET must not mutate the project dir — no state.json / PROJECT.md write (so it is
    # idempotent and works on a read-only mount). Only POST /decisions writes.
    pdir = work / "projects" / project
    assert client.get(f"/api/projects/{project}/state").status_code == 200
    assert client.get(f"/api/projects/{project}/context").status_code == 200
    assert not (pdir / "state.json").exists()
    assert not (pdir / "context" / "PROJECT.md").exists()


def test_unknown_project_404s(client):
    assert client.get("/api/projects/ghost-00000000/state").status_code == 404
    assert client.get("/api/projects/ghost-00000000/context").status_code == 404
    assert client.post("/api/projects/ghost-00000000/decisions",
                       json={"summary": "x"}).status_code == 404
