"""The API's run-envelope pair calls the core kernel's run functions (OPT-F4).

Fast, NO SPICE. ``project_service.begin_run``/``finalize_run`` keep their
signatures and record shape (the /runs responses are these records) but the
lifecycle itself is implemented in ``spicexplorer_core.workspace.runs``, the entry
point the optimizer CLI (OPT-F7) and orchestration campaigns are to share. The
index write-through runs in the kernel's ``on_change`` hook, also on the
best-effort path where the terminal record could not be written.
"""

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


def _spy(monkeypatch, name):
    calls = []
    real = getattr(wr, name)

    def spy(*a, **kw):
        calls.append((a, kw))
        return real(*a, **kw)

    # Both the module and the package namespace (project_service calls ``ws.<name>``).
    monkeypatch.setattr(wr, name, spy)
    monkeypatch.setattr("spicexplorer_core.workspace." + name, spy)
    return calls


def test_project_service_run_pair_delegates_to_core(env, monkeypatch, tmp_path):
    ps, idx = env
    pid = ps.create_project("Seam")
    begun, finalized = _spy(monkeypatch, "begin_run"), _spy(monkeypatch, "finalize_run")
    notified = []
    monkeypatch.setattr(idx, "notify_runs_changed", notified.append)
    net = tmp_path / "amp.spice"
    net.write_text("* amp\n.end\n")

    run_id, rdir = ps.begin_run(
        "simulate",
        project_id=pid,
        label="manual sim",
        input_files={"netlist": net},
        input_values={"params": {"W1": 1e-6}},
        coordinates={"corner": "tt"},
        retention="full",
        record_extras={"keep_raw": False},
    )
    assert len(begun) == 1 and rdir == ps.runs_dir(pid) / run_id
    rec = wr.read_run_record(rdir)
    assert list(rec)[:5] == ["run_id", "project_id", "label", "status", "started"]
    assert rec["project_id"] == pid and rec["status"] == "running" and rec["keep_raw"] is False
    # Every adapter argument reaches the kernel record.
    assert rec["label"] == "manual sim" and rec["kind"] == "simulate"
    assert rec["retention"] == "full" and rec["coordinates"] == {"corner": "tt"}
    objects = ps.project_dir(pid) / ".objects"
    assert (objects / rec["inputs"]["params"]["sha256"]).exists()
    assert (objects / rec["inputs"]["netlist"]["sha256"]).read_bytes() == net.read_bytes()
    assert notified == []  # begin: the index's existence probe picks up a new run dir

    ps.finalize_run(pid, rdir, status="done", score=2.0, metrics={"gain_db": 40.0})
    assert len(finalized) == 1 and notified == [pid]
    rec = wr.read_run_record(rdir)
    assert rec["status"] == "done" and rec["best_score"] == 2.0
    assert rec["metrics"] == {"gain_db": 40.0} and "error" not in rec

    _, rdir2 = ps.begin_run("simulate", project_id=pid)
    ps.finalize_run(pid, rdir2, status="error", error="ngspice exited 1")
    rec2 = wr.read_run_record(rdir2)
    assert rec2["status"] == "error" and rec2["error"] == "ngspice exited 1"
    assert notified == [pid, pid]


def test_finalize_run_stays_best_effort_and_still_indexes(env, monkeypatch):
    ps, idx = env
    _, rdir = ps.begin_run("xschem", project_id=None)
    notified = []
    monkeypatch.setattr(idx, "notify_runs_changed", notified.append)

    def boom(run_dir, record):
        raise OSError("disk full")

    monkeypatch.setattr(wr, "write_run_record", boom)
    ps.finalize_run(None, rdir, status="error", error="netlist failed")  # never raises
    # The terminal write failed (the patch reached the core function) ...
    assert wr.read_run_record(rdir)["status"] == "running"
    # ... and the index was told anyway.
    assert notified == [None]


def test_finalize_run_best_effort_covers_only_os_errors(env, monkeypatch):
    # Best-effort means a full disk, not a bug: anything but OSError still raises,
    # after the index hook has fired.
    ps, idx = env
    _, rdir = ps.begin_run("xschem", project_id=None)
    notified = []
    monkeypatch.setattr(idx, "notify_runs_changed", notified.append)

    def bug(run_dir, record):
        raise RuntimeError("record encoder bug")

    monkeypatch.setattr(wr, "write_run_record", bug)
    with pytest.raises(RuntimeError, match="record encoder bug"):
        ps.finalize_run(None, rdir, status="done")
    assert notified == [None]
    assert wr.read_run_record(rdir)["status"] == "running"
