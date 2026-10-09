"""Retention/GC pruning of the run store (workspace.retention)."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from spicexplorer_core.workspace import (
    envelope_fields,
    iter_candidates,
    prune_run,
    prune_workspace,
    write_run_record,
)


def _make_run(
    run_dir: Path, *, retention: str = "metrics_only", status: str = "done", envelope: bool = True
) -> Path:
    """A terminal run dir with a run.json (+envelope), a heavy sim/ waveform dir,
    events.ndjson, checkpoints/, and a config snapshot."""
    (run_dir / "sim" / "run_0_tb__tt").mkdir(parents=True)
    (run_dir / "sim" / "run_0_tb__tt" / "out.raw").write_bytes(b"x" * 4096)
    (run_dir / "checkpoints").mkdir()
    (run_dir / "checkpoints" / "ckpt_0.json").write_text("{}")
    (run_dir / "events.ndjson").write_text(
        '{"iter": 1, "score": 0.5, "metrics": {"gain": 40}}\n'
        '{"checkpoint": {"id": "ckpt_0"}}\n'
        '{"iter": 2, "score": 0.9, "metrics": {"gain": 44}}\n'
    )
    (run_dir / "config_snapshot.yaml").write_text("ws_root: /abs\n")
    rec: dict = {"run_id": run_dir.name, "status": status}
    if envelope:
        rec.update(envelope_fields("optimize", retention=retention))
    write_run_record(run_dir, rec)
    return run_dir


def test_metrics_only_drops_waveforms_keeps_history(tmp_path: Path):
    run = _make_run(tmp_path / "r1", retention="metrics_only")
    rep = prune_run(run)
    assert rep["pruned"] is True
    assert rep["freed_bytes"] >= 4096
    assert not (run / "sim").exists()  # heavy waveforms gone
    assert (run / "run.json").exists()  # record kept
    assert (run / "events.ndjson").exists()  # per-trial rows kept
    assert (run / "checkpoints" / "ckpt_0.json").exists()
    assert (run / "config_snapshot.yaml").exists()


def test_none_keeps_only_the_record(tmp_path: Path):
    run = _make_run(tmp_path / "r2", retention="none")
    prune_run(run)
    survivors = sorted(p.name for p in run.iterdir())
    assert survivors == ["run.json"]


def test_full_and_legacy_and_running_are_untouched(tmp_path: Path):
    full = _make_run(tmp_path / "full", retention="full")
    legacy = _make_run(tmp_path / "legacy", envelope=False)  # no envelope
    running = _make_run(tmp_path / "running", status="running")
    for run in (full, legacy, running):
        rep = prune_run(run)
        assert rep["pruned"] is False
        assert (run / "sim").exists()


def test_prune_is_idempotent(tmp_path: Path):
    run = _make_run(tmp_path / "r3", retention="metrics_only")
    first = prune_run(run)
    second = prune_run(run)
    assert first["pruned"] is True
    assert second["pruned"] is False
    assert second["skipped"] == "already applied"


def test_dry_run_deletes_nothing(tmp_path: Path):
    run = _make_run(tmp_path / "r4", retention="metrics_only")
    rep = prune_run(run, dry_run=True)
    assert rep["dry_run"] is True
    assert rep["freed_bytes"] >= 4096
    assert (run / "sim").exists()  # nothing removed
    assert "retention_pruned" not in (run / "run.json").read_text()


def test_prune_workspace_age_gate(tmp_path: Path):
    projects = tmp_path / "projects" / "proj-0a1b2c3d" / "runs"
    fresh = _make_run(projects / "fresh", retention="metrics_only")
    stale = _make_run(projects / "stale", retention="metrics_only")
    # Backdate the stale run's terminal time past the grace window.
    old = (datetime.now() - timedelta(days=30)).isoformat(timespec="seconds")
    rec = {
        "run_id": "stale",
        "status": "done",
        "ended": old,
        **envelope_fields("optimize", retention="metrics_only"),
    }
    write_run_record(stale, rec)

    rep = prune_workspace(tmp_path, older_than_s=7 * 86400)
    assert rep["runs_pruned"] == 1
    assert not (stale / "sim").exists()  # old → pruned
    assert (fresh / "sim").exists()  # recent → kept


def test_prune_never_touches_project_objects(tmp_path: Path):
    pdir = tmp_path / "projects" / "proj-0a1b2c3d"
    (pdir / ".objects").mkdir(parents=True)
    (pdir / ".objects" / "deadbeef").write_bytes(b"blob")
    run = _make_run(pdir / "runs" / "r5", retention="none")
    prune_run(run)
    assert (pdir / ".objects" / "deadbeef").exists()  # provenance store survives


def test_iter_candidates_projects_trial_rows(tmp_path: Path):
    run = _make_run(tmp_path / "r6", retention="full")
    rows = list(iter_candidates(run))
    assert [r["iter"] for r in rows] == [1, 2]  # checkpoint event skipped
    assert rows[1]["score"] == 0.9
    # Candidate rows live in events.ndjson, which survives a metrics_only prune.
    prune_run(run, "metrics_only")
    assert [r["iter"] for r in iter_candidates(run)] == [1, 2]


def test_report_excludes_symlink_pointing_outside_run(tmp_path: Path):
    # A .raw symlink pointing OUTSIDE the run dir must not be counted as removed/freed and
    # its target must be untouched — the report + marker stay honest (safety filter first).
    external = tmp_path / "external"
    external.mkdir()
    ext = external / "big.raw"
    ext.write_bytes(b"y" * 10_000)
    run = _make_run(tmp_path / "r_sym", retention="metrics_only")  # sim/out.raw is 4096 B
    (run / "link.raw").symlink_to(ext)

    rep = prune_run(run)
    assert "link.raw" not in rep["removed"]  # skipped target not reported
    assert rep["freed_bytes"] == 4096  # only the real sim/ waveform, not the 10 000 B target
    assert ext.exists() and ext.stat().st_size == 10_000  # external file untouched
    assert (run / "link.raw").is_symlink()  # the link itself is left in place


def test_unknown_tier_rejected(tmp_path: Path):
    run = _make_run(tmp_path / "r7", retention="full")
    with pytest.raises(ValueError):
        prune_run(run, "bogus")


def test_cli_runs_as_a_module_without_the_runpy_double_import_warning():
    """`python -m spicexplorer_core.workspace.retention` is the documented GC entry point. The
    package `__init__` imports the retention module, so running that module as `__main__` made
    runpy warn on every run ("found in sys.modules ... unpredictable behaviour") and execute a
    second copy of it (OPT-17). With the warning escalated to an error, the CLI must exit 0."""
    import subprocess
    import sys

    proc = subprocess.run(
        [
            sys.executable,
            "-W",
            "error::RuntimeWarning",
            "-m",
            "spicexplorer_core.workspace.retention",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert "found in sys.modules" not in proc.stderr, proc.stderr
    assert proc.returncode == 0, proc.stderr
    assert "--older-than-days" in proc.stdout


def test_importing_the_cli_shim_runs_no_sweep(tmp_path: Path):
    """The package `__main__` only runs under `python -m`: a plain import of it (a docs autogen, a
    module walker, a `-c` one-liner) must not run a real, non-dry-run GC sweep of $WORK_ROOT and
    exit the interpreter."""
    import os
    import subprocess
    import sys

    stale = _make_run(tmp_path / "projects" / "proj-0a1b2c3d" / "runs" / "stale")
    old = (datetime.now() - timedelta(days=30)).isoformat(timespec="seconds")
    write_run_record(
        stale,
        {
            "run_id": "stale",
            "status": "done",
            "ended": old,
            **envelope_fields("optimize", retention="metrics_only"),
        },
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import spicexplorer_core.workspace.retention.__main__; print('import-returned')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "WORK_ROOT": str(tmp_path)},
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "import-returned", proc.stdout
    assert (stale / "sim").exists()  # the stale run was not pruned


def test_the_cli_shim_runs_a_dry_sweep_in_process(tmp_path: Path, monkeypatch, capsys):
    """In-process copy of the subprocess test above (so coverage counts `__main__.py`): run as
    a package `__main__`, it parses argv, runs the sweep, prints the JSON report and exits with
    `main()`'s status — with no runpy "found in sys.modules" warning (escalated to an error here)."""
    import json
    import runpy
    import sys
    import warnings

    stale = _make_run(tmp_path / "projects" / "proj-0a1b2c3d" / "runs" / "stale")
    old = (datetime.now() - timedelta(days=30)).isoformat(timespec="seconds")
    write_run_record(
        stale,
        {
            "run_id": "stale",
            "status": "done",
            "ended": old,
            **envelope_fields("optimize", retention="metrics_only"),
        },
    )
    monkeypatch.setattr(sys, "argv", ["retention", "--work-root", str(tmp_path), "--dry-run"])
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        with pytest.raises(SystemExit) as exc:
            runpy.run_module("spicexplorer_core.workspace.retention", run_name="__main__")
    assert exc.value.code == 0
    report = json.loads(capsys.readouterr().out)
    assert report["dry_run"] is True and report["runs_pruned"] == 1
    assert report["work_root"] == str(tmp_path.resolve())
    assert (stale / "sim").exists()  # a dry run deletes nothing
