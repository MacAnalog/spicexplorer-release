"""HTTP route tests for the project/run lifecycle endpoints (report.md P4).

Fast, NO SPICE. A temp WORK_ROOT keeps the registry out of the real ./work. The
routes are thin wrappers over project_service (unit-tested in test_project_service.py),
so these assert the wiring: status codes, the soft-delete → trash → restore round-trip,
and that fork/rename reach the right service call.
"""
import sys

import pytest
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app
    return TestClient(app)


def _new(client, name="Proj") -> str:
    r = client.post("/api/projects", json={"name": name})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_rename_project_route(client):
    pid = _new(client, "Before")
    r = client.patch(f"/api/projects/{pid}", json={"name": "After"})
    assert r.status_code == 200, r.text
    assert r.json()["manifest"]["name"] == "After"
    # The renamed name shows up in the listing under the same id.
    listed = {p["id"]: p["name"] for p in client.get("/api/projects").json()["projects"]}
    assert listed[pid] == "After"


def test_rename_missing_project_404(client):
    r = client.patch("/api/projects/missing-00000000", json={"name": "x"})
    assert r.status_code == 404


def test_fork_route_creates_new_id(client):
    pid = _new(client, "Origin")
    r = client.post(f"/api/projects/{pid}/fork", json={"name": "Forked"})
    assert r.status_code == 200, r.text
    new_id = r.json()["id"]
    assert new_id != pid
    assert client.get(f"/api/projects/{new_id}").status_code == 200


def test_delete_then_trash_then_restore_roundtrip(client):
    pid = _new(client, "Trashable")
    # Soft-delete → 200 with a trash id.
    d = client.delete(f"/api/projects/{pid}")
    assert d.status_code == 200, d.text
    trash_id = d.json()["trash_id"]
    # Gone from the registry.
    assert client.get(f"/api/projects/{pid}").status_code == 404
    # Visible in the trash listing.
    trash = client.get("/api/trash").json()["trash"]
    assert any(t["trash_id"] == trash_id for t in trash)
    # Restore → back under the original id.
    rr = client.post(f"/api/trash/{trash_id}/restore")
    assert rr.status_code == 200, rr.text
    assert rr.json()["id"] == pid
    assert client.get(f"/api/projects/{pid}").status_code == 200


def test_restore_conflict_returns_409(client):
    pid = _new(client, "Clash")
    trash_id = client.delete(f"/api/projects/{pid}").json()["trash_id"]
    # Re-create a project that occupies the original id, then restore must 409.
    from spicexplorer_api.services import project_service
    project_service.project_dir(pid).mkdir(parents=True, exist_ok=True)
    project_service.project_yaml(pid).write_text("project: {}\n")
    rr = client.post(f"/api/trash/{trash_id}/restore")
    assert rr.status_code == 409


def test_run_rename_and_delete_routes(client):
    import json

    pid = _new(client, "WithRuns")
    from spicexplorer_api.services import project_service
    rd = project_service.run_dir(pid, "2026_algo_abcd1234")
    (rd / "run.json").write_text(json.dumps({"run_id": "run-1", "status": "done"}))

    pr = client.patch(f"/api/projects/{pid}/runs/run-1", json={"label": "Champion"})
    assert pr.status_code == 200, pr.text
    assert pr.json()["run"]["label"] == "Champion"

    dr = client.delete(f"/api/projects/{pid}/runs/run-1")
    assert dr.status_code == 200, dr.text
    trash_id = dr.json()["trash_id"]
    assert client.get(f"/api/projects/{pid}/runs").json()["runs"] == []
    # Deleting an already-gone run is a 404.
    assert client.delete(f"/api/projects/{pid}/runs/run-1").status_code == 404
    # The deleted run is restorable and round-trips back into the project's runs.
    rr = client.post(f"/api/trash/{trash_id}/restore")
    assert rr.status_code == 200, rr.text
    assert rr.json()["id"] == pid
    runs = client.get(f"/api/projects/{pid}/runs").json()["runs"]
    assert [r["run_id"] for r in runs] == ["run-1"]


def test_run_routes_404_on_missing_project(client):
    # rename/delete-run on a bogus project must 404 (and not mkdir a ghost project tree).
    assert client.patch("/api/projects/ghost-00000000/runs/x", json={"label": "y"}).status_code == 404
    assert client.delete("/api/projects/ghost-00000000/runs/x").status_code == 404
    from spicexplorer_api.services import project_service
    assert not project_service.project_dir("ghost-00000000").exists()


def test_fork_inherits_example_preset_family(client):
    """A fork's catalog must show its example ancestor's presets — so _project_family has to
    follow the fork's source.ref (a project id) up to the example."""
    from spicexplorer_api.routes.checkpoint import _project_family
    from spicexplorer_api.services import project_service
    examples = project_service.list_examples()
    cascode = next((e for e in examples if "cascode" in e["key"]), examples[0])
    parent = project_service.copy_example(cascode["key"], "Parent")
    fam = _project_family(parent)
    assert fam  # e.g. "OTA/cascode"
    fork = project_service.fork_project(parent, "Forked")
    assert _project_family(fork) == fam


def test_checkpoint_delete_is_project_scoped(client):
    """Deleting a checkpoint with project_id must not touch another project's same-named one."""
    import json as _json

    from spicexplorer_api.services import project_service
    a = client.post("/api/projects", json={"name": "A"}).json()["id"]
    b = client.post("/api/projects", json={"name": "B"}).json()["id"]
    paths = {}
    for pid in (a, b):
        ck = project_service.run_dir(pid, "2026_x_aaaa1111") / "checkpoints"
        ck.mkdir(parents=True, exist_ok=True)
        p = ck / "shared_LhsDE_3_1.json"
        p.write_text(_json.dumps({"optimization_log": []}))
        paths[pid] = p
    r = client.delete(f"/api/checkpoint/shared_LhsDE_3_1?project_id={a}")
    assert r.status_code == 200, r.text
    assert not paths[a].exists()      # A's copy gone
    assert paths[b].exists()          # B's identically-named copy untouched
