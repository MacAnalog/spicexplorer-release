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


def _make_run(run_dir: Path, *, retention: str = "metrics_only",
              status: str = "done", envelope: bool = True) -> Path:
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
    assert not (run / "sim").exists()                 # heavy waveforms gone
    assert (run / "run.json").exists()                # record kept
    assert (run / "events.ndjson").exists()           # per-trial rows kept
    assert (run / "checkpoints" / "ckpt_0.json").exists()
    assert (run / "config_snapshot.yaml").exists()


def test_none_keeps_only_the_record(tmp_path: Path):
    run = _make_run(tmp_path / "r2", retention="none")
    prune_run(run)
    survivors = sorted(p.name for p in run.iterdir())
    assert survivors == ["run.json"]


def test_full_and_legacy_and_running_are_untouched(tmp_path: Path):
    full = _make_run(tmp_path / "full", retention="full")
    legacy = _make_run(tmp_path / "legacy", envelope=False)      # no envelope
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
    assert (run / "sim").exists()                     # nothing removed
    assert "retention_pruned" not in (run / "run.json").read_text()


def test_prune_workspace_age_gate(tmp_path: Path):
    projects = tmp_path / "projects" / "proj-0a1b2c3d" / "runs"
    fresh = _make_run(projects / "fresh", retention="metrics_only")
    stale = _make_run(projects / "stale", retention="metrics_only")
    # Backdate the stale run's terminal time past the grace window.
    old = (datetime.now() - timedelta(days=30)).isoformat(timespec="seconds")
    rec = {"run_id": "stale", "status": "done", "ended": old,
           **envelope_fields("optimize", retention="metrics_only")}
    write_run_record(stale, rec)

    rep = prune_workspace(tmp_path, older_than_s=7 * 86400)
    assert rep["runs_pruned"] == 1
    assert not (stale / "sim").exists()               # old → pruned
    assert (fresh / "sim").exists()                   # recent → kept


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
    assert [r["iter"] for r in rows] == [1, 2]        # checkpoint event skipped
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
    run = _make_run(tmp_path / "r_sym", retention="metrics_only")   # sim/out.raw is 4096 B
    (run / "link.raw").symlink_to(ext)

    rep = prune_run(run)
    assert "link.raw" not in rep["removed"]        # skipped target not reported
    assert rep["freed_bytes"] == 4096              # only the real sim/ waveform, not the 10 000 B target
    assert ext.exists() and ext.stat().st_size == 10_000   # external file untouched
    assert (run / "link.raw").is_symlink()         # the link itself is left in place


def test_unknown_tier_rejected(tmp_path: Path):
    run = _make_run(tmp_path / "r7", retention="full")
    with pytest.raises(ValueError):
        prune_run(run, "bogus")
