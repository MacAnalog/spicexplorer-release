"""Derived SQLite index over WORK_ROOT (plan_project_filesystem P2).

Fast, NO SPICE. Pins the P2 contract: indexed listers are shape/order-identical
twins of the FS scans, reads self-heal against out-of-band FS changes, write-
through keeps content fresh at the API's own mutation points, and any DB error
degrades to the FS scan (never raises).
"""
import json
import sys

import pytest
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from spicexplorer_api.services import index_db, project_service
    return project_service, index_db


def _fake_run(ps, pid, name, **over):
    """Materialize a run dir with a run.json the way the canonical writer does."""
    rd = ps.run_dir(pid, name)
    d = {"run_id": over.pop("run_id", name), "project_id": pid, "label": None,
         "kind": "live", "status": "completed", "best_score": 1.0,
         "started": "2026-07-14T00:00:00", "ended": "2026-07-14T00:01:00"}
    d.update(over)
    (rd / "run.json").write_text(json.dumps(d))
    return rd


def test_rebuild_gives_fs_parity(env):
    ps, idx = env
    a = ps.create_project("Alpha")
    b = ps.create_project("Beta")
    _fake_run(ps, a, "20260714_ng_aaaa1111", best_score=2.5)
    _fake_run(ps, a, "20260713_ng_bbbb2222", best_score=1.5)
    _fake_run(ps, None, "20260712_ng_cccc3333")  # unscoped (WORK_ROOT/runs)
    counts = idx.rebuild()
    assert counts == {"projects": 2, "runs": 3}
    # Same shape + order as the FS listers, for projects and both run scopes.
    assert idx.list_projects() == ps.list_projects()
    assert idx.list_runs(a) == ps.list_runs(a)
    assert idx.list_runs(b) == ps.list_runs(b) == []
    assert idx.list_runs(None) == ps.list_runs(None)
    # Rollup parity: run_count + max best_score.
    pa = next(p for p in idx.list_projects() if p["id"] == a)
    assert pa["run_count"] == 2 and pa["best_score"] == 2.5


def test_write_through_covers_content_changes(env):
    # A rename changes CONTENT but not the project-id set, so the read-side
    # existence probe cannot catch it — only write-through keeps it fresh.
    ps, idx = env
    pid = ps.create_project("Old Name")
    idx.rebuild()
    ps.rename_project(pid, "New Name")
    assert next(p for p in idx.list_projects() if p["id"] == pid)["name"] == "New Name"


def test_run_status_write_through(env):
    # Same reasoning for run.json content: the canonical writer notifies.
    ps, idx = env
    pid = ps.create_project("Runner")
    rd = _fake_run(ps, pid, "20260714_ng_dddd4444", status="running", best_score=None)
    idx.rebuild()
    d = json.loads((rd / "run.json").read_text())
    d.update(status="completed", best_score=3.0)
    (rd / "run.json").write_text(json.dumps(d))
    idx.notify_runs_changed(pid)  # what optimizer_runner._write_run_json calls
    (run,) = idx.list_runs(pid)
    assert run["status"] == "completed" and run["best_score"] == 3.0
    assert next(p for p in idx.list_projects() if p["id"] == pid)["best_score"] == 3.0


def test_reads_self_heal_out_of_band_create_and_delete(env):
    ps, idx = env
    pid = ps.create_project("Seen")
    idx.rebuild()
    # An agent/CLI creates a project + a run WITHOUT the API (FS is canonical).
    from spicexplorer_api.app_config import projects_root
    ghost = projects_root() / "ghost-12345678"
    (ghost / "runs").mkdir(parents=True)
    (ghost / "project.yaml").write_text("project:\n  ws_root: .\n")
    (ghost / "manifest.json").write_text(json.dumps({"id": "ghost-12345678", "name": "Ghost"}))
    _fake_run(ps, pid, "20260714_ng_eeee5555")
    assert {p["id"] for p in idx.list_projects()} == {pid, "ghost-12345678"}
    assert len(idx.list_runs(pid)) == 1
    # Out-of-band delete heals the same way.
    import shutil
    shutil.rmtree(ghost)
    assert {p["id"] for p in idx.list_projects()} == {pid}


def test_soft_delete_and_restore_round_trip_the_index(env):
    ps, idx = env
    pid = ps.create_project("Trashy")
    idx.rebuild()
    trash_id = ps.soft_delete_project(pid)
    assert all(p["id"] != pid for p in idx.list_projects())
    ps.restore_project(trash_id)
    assert any(p["id"] == pid for p in idx.list_projects())


def test_db_error_degrades_to_fs_scan(env, tmp_path, monkeypatch):
    ps, idx = env
    pid = ps.create_project("Fallback")
    # Point the index at an impossible path (a directory component that is a file).
    blocker = tmp_path / "blocker"
    blocker.write_text("")
    monkeypatch.setenv(idx.INDEX_DB_ENV, str(blocker / "nope" / "index.db"))
    projects = idx.list_projects()  # must not raise
    assert any(p["id"] == pid for p in projects)
    assert idx.list_runs(pid) == ps.list_runs(pid)


def test_cli_rebuild_smoke(env, capsys):
    ps, idx = env
    ps.create_project("CLI")
    assert idx.main([]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["projects"] == 1 and report["db"].endswith("index.db")
