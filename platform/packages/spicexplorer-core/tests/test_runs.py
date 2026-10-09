"""Run-envelope tests: ``begin_run``/``finalize_run`` + ``RunWriter``.

Fast, NO SPICE. Tests the kernel begin/finalize pair (OPT-F4; the API's one-shot
routes use it today, the optimizer CLI and orchestration campaigns are to) and
the incremental ``RunWriter`` lifted from orchestration's ``RunMirror`` whose
context manager finishes a run ``error`` when the body raises, without ever
masking that exception (ORCH-F05).
"""

import json
import os

import pytest
from spicexplorer_core import workspace
from spicexplorer_core.workspace import runs as wr
from spicexplorer_core.workspace.retention import iter_candidates


def test_seam_is_exported_from_the_workspace_package():
    # Hosts import these functions from the package (the API calls ``ws.begin_run``).
    assert workspace.begin_run is wr.begin_run and workspace.finalize_run is wr.finalize_run
    assert workspace.RunWriter is wr.RunWriter
    assert {"begin_run", "finalize_run", "RunWriter"} <= set(workspace.__all__)


# ---------- begin_run / finalize_run ----------


def test_begin_run_commits_a_running_envelope(tmp_path):
    proj = tmp_path / "projects" / "amp-1234abcd"
    yml = tmp_path / "project.yaml"
    yml.write_text("project: {name: amp}\n")
    seen = []

    def on_change(run_dir):  # the record is already committed when the hook fires
        seen.append(run_dir)
        assert wr.read_run_record(run_dir).get("status") == "running"

    rid, d = wr.begin_run(
        proj / "runs",
        "simulate",
        project_id="amp-1234abcd",
        project_dir=proj,
        label="manual sim",
        inputs={"harness": "demo"},
        input_files={"project_yaml": yml},
        input_values={"params": {"W1": 2e-6}},
        coordinates={"corner": "tt"},
        retention="full",
        record_extras={"keep_raw": True},
        on_change=on_change,
    )
    assert d == proj / "runs" / rid and d.is_dir() and "_simulate_" in rid
    rec = wr.read_run_record(d)
    # The API's record shape, key order included (its /runs responses are these dicts).
    assert list(rec)[:5] == ["run_id", "project_id", "label", "status", "started"]
    assert rec["run_id"] == rid and rec["project_id"] == "amp-1234abcd"
    assert rec["status"] == wr.STATUS_RUNNING == "running" and rec["label"] == "manual sim"
    assert rec["envelope"] == wr.ENVELOPE_VERSION and rec["kind"] == "simulate"
    assert rec["retention"] == "full" and rec["coordinates"] == {"corner": "tt"}
    assert rec["keep_raw"] is True
    # Pre-built provenance is merged as-is; files/values are content-addressed into the project.
    assert rec["inputs"]["harness"] == "demo"
    sha = rec["inputs"]["project_yaml"]["sha256"]
    assert (proj / ".objects" / sha).read_bytes() == yml.read_bytes()
    assert "sha256" in rec["inputs"]["params"]
    # One notification after the commit; no heartbeat (a one-shot run relies on its run.json mtime).
    assert seen == [d]
    assert not (d / wr.HEARTBEAT_NAME).exists()


def test_begin_run_unscoped_and_extras_win(tmp_path):
    yml = tmp_path / "job.yaml"
    yml.write_text("x: 1\n")
    rid, d = wr.begin_run(
        tmp_path / "runs", "xschem", input_files={"yaml": yml}, record_extras={"label": "override"}
    )
    rec = wr.read_run_record(d)
    assert rec["project_id"] is None and rec["label"] == "override"
    assert rec["inputs"]["yaml"]["sha256"]  # hashed…
    assert not list(tmp_path.rglob(".objects"))  # …but nothing stored without a project
    # Defaults: the envelope's metrics_only tier, empty coordinates, no heartbeat.
    assert rec["retention"] == "metrics_only" and rec["coordinates"] == {}
    assert not (d / wr.HEARTBEAT_NAME).exists()


def test_begin_run_minimal_call_and_str_runs_base(tmp_path):
    # A bare call (no project, no inputs, no hook) still commits a full running
    # envelope, and a str base is accepted like a Path (mint_run_dir needs a Path).
    rid, d = wr.begin_run(str(tmp_path / "runs"), "xschem")  # pyright: ignore[reportArgumentType]
    assert d == tmp_path / "runs" / rid and d.is_dir()
    rec = wr.read_run_record(d)
    assert rec["status"] == "running" and rec["label"] is None and rec["project_id"] is None
    assert rec["inputs"] == {} and rec["kind"] == "xschem"


def test_begin_run_snapshot_wins_over_caller_inputs_on_a_name_clash(tmp_path):
    # ``inputs`` is provenance the caller already holds; a same-named file/value is
    # content-addressed here, and the hash is what a run record must dereference.
    _, d = wr.begin_run(
        tmp_path / "runs",
        "simulate",
        inputs={"params": "caller-side", "harness": "demo"},
        input_values={"params": {"W1": 1e-6}},
    )
    rec = wr.read_run_record(d)
    assert "sha256" in rec["inputs"]["params"] and rec["inputs"]["harness"] == "demo"


def test_finalize_run_stamps_terminal_record_then_notifies(tmp_path):
    rid, d = wr.begin_run(tmp_path / "runs", "simulate")
    seen = []

    def on_change(run_dir):  # the record is already committed when the hook fires
        seen.append((run_dir, wr.read_run_record(run_dir)["status"]))

    rec = wr.finalize_run(
        d,
        status=wr.STATUS_DONE,
        score=1.5,
        metrics={"gain_db": 40.0},
        record_extras={"n_events": 3},
        on_change=on_change,
    )
    assert seen == [(d, "done")]
    assert rec == wr.read_run_record(d)
    assert rec["status"] == "done" and rec["best_score"] == 1.5
    assert rec["metrics"] == {"gain_db": 40.0} and rec["n_events"] == 3
    assert rec["started"] <= rec["ended"] and "error" not in rec
    # Defaults: best_score/metrics are always present (the index reads them), error only when given.
    _, d2 = wr.begin_run(tmp_path / "runs", "simulate")
    rec2 = wr.finalize_run(d2, status=wr.STATUS_ERROR, error="sim failed")
    assert rec2["best_score"] is None and rec2["metrics"] == {}
    assert rec2["status"] == "error" and rec2["error"] == "sim failed"
    # The begin fields survive the terminal stamp (it updates, never replaces).
    assert rec2["kind"] == "simulate" and rec2["run_id"] and rec2["started"]


def test_finalize_run_extras_merge_last_and_status_is_not_validated(tmp_path):
    _, d = wr.begin_run(tmp_path / "runs", "optimize")
    # record_extras land after the terminal fields (the docstring's order), so a
    # caller-held value wins a clash; ``stopped`` is a legal optimizer ending here.
    rec = wr.finalize_run(
        d, status="stopped", score=1.0, error="", record_extras={"best_score": 99.0, "n_trials": 7}
    )
    assert rec["status"] == "stopped" and rec["best_score"] == 99.0 and rec["n_trials"] == 7
    assert "error" not in rec  # an empty error is no error
    assert wr.read_run_record(d) == rec


def test_finalize_run_write_failure_raises_but_still_notifies(tmp_path, monkeypatch):
    _, d = wr.begin_run(tmp_path / "runs", "simulate")
    seen = []

    def boom(run_dir, record):
        raise OSError("disk full")

    monkeypatch.setattr(wr, "write_run_record", boom)
    with pytest.raises(OSError, match="disk full"):
        wr.finalize_run(d, status="done", on_change=seen.append)
    # A derived view re-reads the (unchanged) disk state: the files on disk are the record.
    assert seen == [d]


# ---------- RunWriter (ORCH-F05) ----------


@pytest.mark.parametrize(
    "exc, text",
    [
        (
            RuntimeError("reserved column(s) ['raw_bytes']"),
            "RuntimeError: reserved column(s) ['raw_bytes']",
        ),
        (KeyboardInterrupt(), "KeyboardInterrupt"),
    ],
)
def test_run_writer_exception_finishes_error(tmp_path, exc, text):
    with pytest.raises(type(exc)):
        with wr.RunWriter(tmp_path / "runs", kind="campaign") as w:
            w.append({"tag": "a", "fc_hz": 250.0})
            raise exc
    rec = wr.read_run_record(w.run_dir)
    assert rec["status"] == wr.STATUS_ERROR and rec["n_events"] == 1
    assert rec["error"] == text and rec["started"] <= rec["ended"]


def test_run_writer_exit_never_masks_the_original_exception(tmp_path, monkeypatch):
    def boom(run_dir, record):
        raise OSError("disk full")

    with pytest.raises(ValueError, match="the real failure"):
        with wr.RunWriter(tmp_path / "runs", kind="campaign") as w:
            monkeypatch.setattr(wr, "write_run_record", boom)
            raise ValueError("the real failure")
    monkeypatch.undo()
    assert wr.read_run_record(w.run_dir)["status"] == "running"  # the finish write failed


def test_run_writer_clean_exit_and_explicit_finish(tmp_path):
    with wr.RunWriter(tmp_path / "runs", kind="campaign", label="c1") as w:
        w.append({"tag": "a"})
        w.append({"tag": "b"})
    rec = wr.read_run_record(w.run_dir)
    assert rec["status"] == "done" and rec["n_events"] == 2 and rec["label"] == "c1"
    # An explicit finish inside the block is the run's verdict — the exit keeps it, even
    # when later (post-run) code raises.
    with pytest.raises(RuntimeError):
        with wr.RunWriter(tmp_path / "runs", kind="campaign") as w2:
            w2.append({"tag": "a"})
            w2.finish(wr.STATUS_DONE, best_score=1.0, metrics={"n_rows": 1})
            raise RuntimeError("summary step failed")
    rec2 = wr.read_run_record(w2.run_dir)
    assert rec2["status"] == "done" and rec2["best_score"] == 1.0 and "error" not in rec2


def test_run_writer_keeps_the_run_mirror_contract(tmp_path):
    # The RunMirror API that orchestration's campaign/tests use (the re-export there is pending).
    w = wr.RunWriter(
        tmp_path / "runs",
        kind="Camp Aign!",
        label="import",
        inputs={"harness": "demo-lpf"},
        coordinates={"corner": "tt"},
    )
    assert w.run_dir == tmp_path / "runs" / w.run_id and "_camp-aign_" in w.run_id
    rec = wr.read_run_record(w.run_dir)
    assert rec["status"] == "running" and rec["n_events"] == 0 and rec["envelope"] == 1
    assert rec["inputs"] == {"harness": "demo-lpf"} and rec["coordinates"] == {"corner": "tt"}
    assert set(rec["owner"]) >= {"pid", "hostname", "started"}
    assert (w.run_dir / wr.HEARTBEAT_NAME).exists()
    # Strict JSON event lines: non-JSON values stringify, non-finite numbers become null.
    ev = w.append(
        {"tag": "x", "fc_hz": 1.0, "obj": object(), "irn": float("nan"), "p": (1, float("inf"))}
    )
    assert ev["event"] == wr.EVENT_LEDGER_ROW == "ledger_row" and ev["iter"] == 1
    assert ev["data"]["irn"] is None and ev["data"]["p"] == [1, None]
    line = (w.run_dir / wr.EVENTS_FILE).read_text()
    assert "NaN" not in line and "Infinity" not in line
    assert json.loads(line)["data"]["obj"].startswith("<object")
    w.append({"tag": "y"})
    assert [c["iter"] for c in iter_candidates(w.run_dir)] == [1, 2]
    with pytest.raises(ValueError, match="not a terminal platform run status"):
        w.finish("failed")  # the platform vocabulary is running | done | error
    # A refused status is checked before any write: the run is still open.
    assert wr.read_run_record(w.run_dir)["status"] == "running" and w.finished is False
    rec = w.finish(wr.STATUS_ERROR, best_score=-1.0, metrics={"n": 2})
    assert rec["status"] == "error" and rec["n_events"] == 2 and rec["best_score"] == -1.0
    assert wr.read_run_record(w.run_dir)["metrics"] == {"n": 2}
    assert wr.TERMINAL_STATUSES == {wr.STATUS_DONE, wr.STATUS_ERROR}
    assert wr.sanitize({"a": [float("-inf"), {"b": 1.5}], 3: True}) == {
        "a": [None, {"b": 1.5}],
        "3": True,
    }


def test_run_writer_defaults_match_run_mirror(tmp_path):
    # RunMirror's defaults, so orchestration's ``events.py`` can re-export it unchanged.
    w = wr.RunWriter(tmp_path / "runs")
    rec = wr.read_run_record(w.run_dir)
    assert rec["kind"] == "campaign" and "_campaign_" in w.run_id
    assert rec["label"] == "" and rec["retention"] == "metrics_only"
    assert rec["inputs"] == {} and rec["coordinates"] == {} and rec["project_id"] is None
    assert w.n == 0 and w.finished is False
    assert not (w.run_dir / wr.EVENTS_FILE).exists()  # no event until the first row


def test_run_writer_forwards_retention_and_event_name(tmp_path):
    w = wr.RunWriter(tmp_path / "runs", kind="campaign", retention="full")
    assert wr.read_run_record(w.run_dir)["retention"] == "full"
    ev = w.append({"step": 1}, event="checkpoint")
    w.append({"step": 2})
    lines = [json.loads(s) for s in (w.run_dir / wr.EVENTS_FILE).read_text().splitlines()]
    assert ev["event"] == "checkpoint" and lines[0] == ev
    assert [e["event"] for e in lines] == ["checkpoint", wr.EVENT_LEDGER_ROW]
    assert [e["iter"] for e in lines] == [1, 2]


def test_run_writer_append_touches_the_heartbeat(tmp_path):
    # Each row touches the heartbeat (a run owned by another host is judged dead by its mtime).
    w = wr.RunWriter(tmp_path / "runs", kind="campaign")
    hb = w.run_dir / wr.HEARTBEAT_NAME
    os.utime(hb, (0, 0))
    w.append({"tag": "a"})
    assert hb.stat().st_mtime > 1e9
    # Rows alone never rewrite run.json (no index rewrite per point); finish does.
    assert wr.read_run_record(w.run_dir)["n_events"] == 0
    assert w.finish()["n_events"] == 1


def test_sanitize_edge_values():
    assert wr.sanitize(frozenset({3})) == [3] and wr.sanitize({"k"}) == ["k"]
    assert wr.sanitize((1, "a", None, True)) == [1, "a", None, True]
    assert wr.sanitize(-0.0) == 0.0 and wr.sanitize(float("-inf")) is None
    assert wr.sanitize({}) == {} and wr.sanitize([]) == []
    assert wr.sanitize({None: {2: float("nan")}}) == {"None": {"2": None}}
    assert wr.sanitize(b"x") == "b'x'"
