"""Run-envelope adoption in the API layer (plan_project_filesystem P3).

Fast, NO SPICE. Pins: owner-aware stale-run reconcile (an out-of-process live
run survives an API restart; legacy/dead runs still flip), started-time run
ordering (FS lister == indexed lister), and the manual-sim `kind: simulate`
envelope (run dir minted, provenance recorded, error finalized, metrics
indexed) — the sim itself is stubbed out, so no ngspice is needed.
"""
import json
import os
import sys

import pytest
from _api_fixtures import REPO_ROOT
from spicexplorer_core.workspace import runs as wr

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from spicexplorer_api.services import index_db, project_service
    return project_service, index_db


def _run(ps, pid, name, **rec):
    rd = ps.runs_dir(pid) / name
    rd.mkdir(parents=True)
    d = {"run_id": name, "project_id": pid, "status": "completed",
         "started": "2026-07-14T00:00:00"}
    d.update(rec)
    (rd / "run.json").write_text(json.dumps(d))
    return rd


# ---------- owner-aware reconcile ----------

def test_reconcile_flips_only_provably_dead_runs(env):
    ps, _ = env
    pid = ps.create_project("Reconcile")
    # Legacy running run (no owner block) → old behavior: flipped.
    legacy = _run(ps, pid, "20260714-000001_opt_aaaaaaaa", status="running")
    # Envelope run owned by THIS live process → must survive the "restart".
    alive = _run(ps, pid, "20260714-000002_opt_bbbbbbbb", status="running",
                 **wr.envelope_fields("optimize"))
    # Envelope run with a dead pid on this host → flipped.
    dead_env = wr.envelope_fields("optimize")
    dead_env["owner"]["pid"] = 2**22 + 54321
    dead = _run(ps, pid, "20260714-000003_opt_cccccccc", status="running", **dead_env)

    fixed = ps.reconcile_stale_runs()
    assert fixed == 2
    assert json.loads((legacy / "run.json").read_text())["status"] == "error"
    assert json.loads((alive / "run.json").read_text())["status"] == "running"
    assert json.loads((dead / "run.json").read_text())["status"] == "error"


# ---------- started-time ordering, FS ⇄ index parity ----------

def test_list_runs_orders_by_started_not_dir_name(env):
    ps, idx = env
    pid = ps.create_project("Ordering")
    # Dir names deliberately CONTRADICT the recorded start times.
    _run(ps, pid, "z_oldest", started="2026-07-10T00:00:00")
    _run(ps, pid, "a_newest", started="2026-07-14T09:00:00")
    _run(ps, pid, "m_middle", started="2026-07-12T00:00:00")
    want = ["a_newest", "m_middle", "z_oldest"]
    assert [r["run_id"] for r in ps.list_runs(pid)] == want
    idx.rebuild()
    assert [r["run_id"] for r in idx.list_runs(pid)] == want


# ---------- manual sim = a first-class `kind: simulate` run ----------

def test_manual_sim_records_an_envelope_run_even_on_failure(env, monkeypatch):
    ps, idx = env
    examples = ps.list_examples()
    cascode = next((e for e in examples if "cascode" in e["key"]), examples[0])
    pid = ps.copy_example(cascode["key"], "SimEnvelope")

    # Stub the wrapper factory: the envelope bookkeeping is under test, not SPICE.
    from spicexplorer_api.services import optimizer_runner

    def _no_sim(*a, **k):
        raise RuntimeError("no simulation in fast tests")
    monkeypatch.setattr(optimizer_runner, "_build_spicelib_wrappers", _no_sim)

    from spicexplorer_api.routes.simulate import SimulateOnceRequest, _run_single_sim
    req = SimulateOnceRequest(
        yaml_path=str(ps.project_yaml(pid)), params={"x_dut_W_1": "10u"})
    result = _run_single_sim(req)
    assert result["ok"] is False and "no simulation" in result["error"]

    (run,) = ps.list_runs(pid)
    assert run["kind"] == "simulate" and run["status"] == "error"
    assert run["envelope"] == wr.ENVELOPE_VERSION
    assert run["owner"]["pid"] == os.getpid()
    # Dir == run_id (D-4), and the yaml input was provenance-hashed into .objects/.
    rd = ps.runs_dir(pid) / run["run_id"]
    assert rd.is_dir()
    sha = run["inputs"]["project_yaml"]["sha256"]
    assert (ps.project_dir(pid) / ".objects" / sha).exists()
    # The index absorbed it (write-through on finalize).
    assert [r["run_id"] for r in idx.list_runs(pid)] == [run["run_id"]]


def test_manual_sim_scope_mapping(env, tmp_path):
    ps, _ = env
    pid = ps.create_project("Scoped")
    got_pid, got_dir = ps.project_for_yaml(str(ps.project_yaml(pid)))
    assert got_pid == pid and got_dir == ps.project_dir(pid)
    assert ps.project_for_yaml(str(tmp_path / "somewhere" / "example.yaml")) == (None, None)


def test_trashed_running_run_always_flips(env):
    # A soft-deleted run was quiesced before the move, so reconcile must flip it to
    # error even if its owner looks alive — else it resurfaces "running" on restore.
    ps, _ = env
    pid = ps.create_project("TrashFlip")
    _run(ps, pid, "20260714-000005_opt_ffffffff", status="running",
         **wr.envelope_fields("optimize"))  # owner = this live process
    trash_id = ps.soft_delete_project(pid)
    assert ps.reconcile_stale_runs() >= 1
    ps.restore_project(trash_id)
    (run,) = ps.list_runs(pid)
    assert run["status"] == "error"


def test_optimize_run_metrics_flow_to_index(env):
    ps, idx = env
    pid = ps.create_project("OptMetrics")
    _run(ps, pid, "20260714-000006_opt_11112222", kind="optimize", status="done",
         best_score=0.8, metrics={"dcgain_db": 47.4, "pm_deg": 61.0})
    idx.rebuild()
    import sqlite3
    with sqlite3.connect(idx.db_path()) as con:
        rows = dict(con.execute(
            "SELECT name, value FROM metrics WHERE run_id=?",
            ("20260714-000006_opt_11112222",)).fetchall())
    assert rows == {"dcgain_db": 47.4, "pm_deg": 61.0}


def test_simulate_run_metrics_land_in_index(env):
    ps, idx = env
    pid = ps.create_project("Metrics")
    _run(ps, pid, "20260714-000004_sim_dddddddd", kind="simulate", status="done",
         best_score=0.9, metrics={"gain_db": 51.2, "pm": 62.0})
    idx.rebuild()
    import sqlite3
    with sqlite3.connect(idx.db_path()) as con:
        rows = dict(con.execute(
            "SELECT name, value FROM metrics WHERE run_id=?",
            ("20260714-000004_sim_dddddddd",)).fetchall())
    assert rows == {"gain_db": 51.2, "pm": 62.0}
