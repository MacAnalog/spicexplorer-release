"""Regression tests for the 2026-06 audit r3 **Tier 0** (security + data-integrity) fixes.

Covers:
- BUG-B1  no eval() / no code execution when loading an untrusted checkpoint's ``log_file``.
- BUG-B2  the checkpoint-report ``yaml_path`` is gated to a .yaml/.yml file under an allowed root.
- BUG-B3  an unscoped ``DELETE /checkpoint/{id}`` refuses to wipe same-named checkpoints across projects.
- BUG-B4  ``stop_runs_for`` reports a still-alive worker, and the delete routes 409 instead of moving.

Pure dict/function transforms — no ngspice / PDK / live sim needed. Skipped unless the `ui` extra
(FastAPI) is installed, since these import the backend package.
"""
import json
import sys
import threading
import types

import pytest
from _api_fixtures import EXAMPLE_YAML, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


# ---------- BUG-B1: load_checkpoint must not execute code in log_file ----------

def _write_checkpoint(path, log_file_value):
    from spicexplorer.optimization.base import CHECKPOINT_SCHEMA_VERSION
    entry = {"point": {"params": {"x": 1.0}, "score": 0.5}, "fit_summary": {}, "log_file": log_file_value}
    path.write_text(json.dumps({"schema_version": CHECKPOINT_SCHEMA_VERSION,
                                "optimization_log": [entry]}))


def test_load_checkpoint_does_not_exec_code_in_log_file(tmp_path):
    """A malicious stringified log_file must NOT be eval()'d (BUG-B1 RCE)."""
    from spicexplorer.viz.plotting import Optimization_Log_Visualizer

    sentinel = tmp_path / "pwned"
    payload = f"__import__('pathlib').Path({str(sentinel)!r}).write_text('x')"
    ckpt = tmp_path / "evil.json"
    _write_checkpoint(ckpt, payload)

    vis = Optimization_Log_Visualizer.load_checkpoint(ckpt)  # must not run the payload

    assert not sentinel.exists(), "log_file string was executed — eval() RCE not fixed"
    # A non-literal payload is safely dropped to None (the field is Optional + unused downstream).
    assert vis.optimization_log[0].log_file is None


def test_load_checkpoint_posix_path_repr_is_dropped_not_executed(tmp_path):
    """The historical ``{'tb': PosixPath('…')}`` repr is a call, so it's dropped to None (not eval'd)."""
    from spicexplorer.viz.plotting import Optimization_Log_Visualizer
    ckpt = tmp_path / "legacy.json"
    _write_checkpoint(ckpt, "{'tb_ac': PosixPath('/x/y.log')}")
    vis = Optimization_Log_Visualizer.load_checkpoint(ckpt)
    assert vis.optimization_log[0].log_file is None


def test_load_checkpoint_plain_literal_log_file_still_parses(tmp_path):
    """A plain dict-literal log_file is still parsed (behavior preserved for literals)."""
    from spicexplorer.viz.plotting import Optimization_Log_Visualizer
    ckpt = tmp_path / "ok.json"
    _write_checkpoint(ckpt, "{'tb_ac': '/x/y.log'}")
    vis = Optimization_Log_Visualizer.load_checkpoint(ckpt)
    assert vis.optimization_log[0].log_file == {"tb_ac": "/x/y.log"}


# ---------- BUG-B2: yaml_path containment / suffix gate ----------

def test_validated_yaml_path_rejects_absolute_system_file():
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path
    assert _validated_yaml_path("/etc/passwd") is None          # wrong suffix + outside roots
    assert _validated_yaml_path("/etc/foo.yaml") is None         # right suffix, outside roots
    assert _validated_yaml_path("") is None


def test_validated_yaml_path_rejects_non_yaml_under_repo():
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path
    # A real file under REPO_ROOT but not .yaml/.yml must be refused (e.g. CLAUDE.md / .env).
    assert _validated_yaml_path(str(REPO_ROOT / "CLAUDE.md")) is None


def test_validated_yaml_path_rejects_repo_yaml_outside_examples():
    """A real .yaml at the repo root (e.g. compose.yaml) is refused — only examples/ is allowed."""
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path
    compose = REPO_ROOT / "compose.yaml"
    if not compose.exists():
        pytest.skip("compose.yaml not present")
    assert _validated_yaml_path(str(compose)) is None


def test_validated_yaml_path_handles_nul_byte_without_raising():
    """An embedded NUL must yield None, not an uncaught ValueError → 500 (B2 hardening)."""
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path
    assert _validated_yaml_path("/etc/passwd\x00.yaml") is None


def test_validated_yaml_path_accepts_example_under_repo():
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path
    out = _validated_yaml_path(str(EXAMPLE_YAML))
    assert out == EXAMPLE_YAML.resolve()


def test_validated_yaml_path_rejects_yaml_symlink_to_system_file(tmp_path, monkeypatch):
    """A .yaml symlink that resolves outside the allowed roots is rejected (resolve before check)."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from spicexplorer_api.routes.checkpoint import _validated_yaml_path
    link = tmp_path / "link.yaml"
    try:
        link.symlink_to("/etc/passwd")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    # tmp_path is under the temp dir (an allowed root), but the symlink resolves to /etc/passwd.
    assert _validated_yaml_path(str(link)) is None


def test_checkpoint_report_400s_on_bad_yaml_path():
    """End-to-end: the report endpoint rejects an out-of-bounds yaml_path with 400 (BUG-B2)."""
    from fastapi import HTTPException
    from spicexplorer_api.routes import checkpoint as C
    presets = {k: v for k, v in C.preset_checkpoint_paths().items() if v.exists()}
    if not presets:
        pytest.skip("no resolvable preset checkpoint to drive the report endpoint")
    pid = next(iter(presets))
    with pytest.raises(HTTPException) as ei:
        C.checkpoint_report(pid, yaml_path="/etc/passwd")
    assert ei.value.status_code == 400


def test_yaml_text_rejects_out_of_root_path():
    """The Setup editor's /yaml-text must not read an arbitrary .yaml on the host (B2 sibling)."""
    from fastapi import HTTPException
    from spicexplorer_api.routes.project import yaml_text
    with pytest.raises(HTTPException) as ei:
        yaml_text(path="/etc/foo.yaml")
    assert ei.value.status_code == 400


def test_yaml_text_accepts_example():
    from spicexplorer_api.routes.project import yaml_text
    out = yaml_text(path=str(EXAMPLE_YAML))
    assert "project" in out  # the example YAML has a top-level project: block


# ---------- BUG-B3: unscoped delete must not span projects ----------

def _make_ckpt(root, project_slug, run, stem):
    d = root / "projects" / project_slug / "runs" / run / "checkpoints"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{stem}.json"
    f.write_text("{}")
    return f


def test_unscoped_delete_refuses_cross_project_match(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from fastapi import HTTPException
    from spicexplorer_api.routes import checkpoint as C
    wr = tmp_path / "wr"
    fa = _make_ckpt(wr, "proja-aaaaaaaa", "run1", "ota_DE_2000_trial5")
    fb = _make_ckpt(wr, "projb-bbbbbbbb", "run1", "ota_DE_2000_trial5")  # same stem, other project

    with pytest.raises(HTTPException) as ei:
        C.delete_checkpoint("ota_DE_2000_trial5", project_id="", path="")
    assert ei.value.status_code == 409
    assert fa.exists() and fb.exists(), "409 must NOT delete anything"


def test_scoped_delete_only_touches_its_own_project(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from spicexplorer_api.routes import checkpoint as C
    wr = tmp_path / "wr"
    fa = _make_ckpt(wr, "proja-aaaaaaaa", "run1", "ota_DE_2000_trial5")
    fb = _make_ckpt(wr, "projb-bbbbbbbb", "run1", "ota_DE_2000_trial5")

    out = C.delete_checkpoint("ota_DE_2000_trial5", project_id="proja-aaaaaaaa", path="")
    assert out["ok"] is True
    assert not fa.exists(), "scoped delete should remove its own project's file"
    assert fb.exists(), "scoped delete must NOT touch another project's same-named file"


def test_unscoped_delete_single_match_still_works(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from spicexplorer_api.routes import checkpoint as C
    wr = tmp_path / "wr"
    fa = _make_ckpt(wr, "proja-aaaaaaaa", "run1", "ota_DE_2000_trial9")
    out = C.delete_checkpoint("ota_DE_2000_trial9", project_id="", path="")
    assert out["ok"] is True and not fa.exists()


def test_scoped_delete_refuses_multi_run_match_within_project(tmp_path, monkeypatch):
    """Two RUNS of one project share a stem → a bare-stem scoped delete must 409 (B3 cross-run)."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from fastapi import HTTPException
    from spicexplorer_api.routes import checkpoint as C
    wr = tmp_path / "wr"
    f1 = _make_ckpt(wr, "proja-aaaaaaaa", "run1", "ota_DE_2000_trial5_FINAL")
    f2 = _make_ckpt(wr, "proja-aaaaaaaa", "run2", "ota_DE_2000_trial5_FINAL")
    with pytest.raises(HTTPException) as ei:
        C.delete_checkpoint("ota_DE_2000_trial5_FINAL", project_id="proja-aaaaaaaa", path="")
    assert ei.value.status_code == 409
    assert f1.exists() and f2.exists(), "409 must NOT delete anything"


def test_precise_path_delete_targets_exactly_one_file(tmp_path, monkeypatch):
    """Passing the exact path deletes only that file, never the same-named twin in run2 (B3)."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from spicexplorer_api.routes import checkpoint as C
    wr = tmp_path / "wr"
    f1 = _make_ckpt(wr, "proja-aaaaaaaa", "run1", "ota_DE_2000_trial5_FINAL")
    f2 = _make_ckpt(wr, "proja-aaaaaaaa", "run2", "ota_DE_2000_trial5_FINAL")
    out = C.delete_checkpoint("ota_DE_2000_trial5_FINAL", project_id="proja-aaaaaaaa", path=str(f1))
    assert out["ok"] is True
    assert not f1.exists() and f2.exists()


def test_precise_path_delete_rejects_file_outside_autosave(tmp_path, monkeypatch):
    """A path outside the autosave roots is refused even if it's a real .json with a matching stem."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from fastapi import HTTPException
    from spicexplorer_api.routes import checkpoint as C
    wr = tmp_path / "wr"
    _make_ckpt(wr, "proja-aaaaaaaa", "run1", "ota_DE_2000_trial5")  # so roots exist
    evil = tmp_path / "evil"
    evil.mkdir()
    outside = evil / "ota_DE_2000_trial5.json"
    outside.write_text("{}")
    with pytest.raises(HTTPException) as ei:
        C.delete_checkpoint("ota_DE_2000_trial5", project_id="proja-aaaaaaaa", path=str(outside))
    assert ei.value.status_code == 403
    assert outside.exists()


# ---------- BUG-B4: stop_runs_for liveness + route 409 ----------

def test_stop_runs_for_reports_still_alive_worker():
    from spicexplorer_api.services import optimizer_runner as R
    release = threading.Event()
    t = threading.Thread(target=release.wait, daemon=True)  # simulates a long in-flight trial
    t.start()
    st = types.SimpleNamespace(run_id="r-alive", project_id="pX",
                               thread=t, stop_event=threading.Event(), done=False)
    R._runs["r-alive"] = st
    try:
        attempted, still_alive = R.stop_runs_for(project_id="pX", timeout=0.2)
        assert attempted == 1
        assert still_alive == ["r-alive"], "a worker alive past the join must be reported"
        st.stop_event.set()
        assert st.stop_event.is_set(), "stop_event must be signalled even when the join times out"
    finally:
        release.set()
        t.join(timeout=2)
        R._runs.pop("r-alive", None)
    # Once the thread is dead, a re-check reports it quiesced.
    R._runs["r-alive"] = st
    try:
        _, still_alive2 = R.stop_runs_for(project_id="pX", timeout=0.2)
        assert still_alive2 == []
    finally:
        R._runs.pop("r-alive", None)


def test_delete_project_409s_while_run_still_alive(monkeypatch):
    from fastapi import HTTPException
    from spicexplorer_api.routes import projects as P
    called = {"soft_delete": False}
    monkeypatch.setattr(P.optimizer_runner, "stop_runs_for", lambda **kw: (1, ["r-alive"]))
    monkeypatch.setattr(P.project_service, "soft_delete_project",
                        lambda pid: called.__setitem__("soft_delete", True) or "x")
    with pytest.raises(HTTPException) as ei:
        P.delete_project("proja-aaaaaaaa")
    assert ei.value.status_code == 409
    assert called["soft_delete"] is False, "must NOT move the dir while a worker is alive"


def test_delete_run_409s_while_run_still_alive(monkeypatch):
    from fastapi import HTTPException
    from spicexplorer_api.routes import projects as P
    monkeypatch.setattr(P.project_service, "project_exists", lambda pid: True)
    monkeypatch.setattr(P.optimizer_runner, "stop_runs_for", lambda **kw: (1, ["r-alive"]))
    called = {"delete_run": False}
    monkeypatch.setattr(P.project_service, "delete_run",
                        lambda pid, rid: called.__setitem__("delete_run", True) or "x")
    with pytest.raises(HTTPException) as ei:
        P.delete_run("proja-aaaaaaaa", "r-alive")
    assert ei.value.status_code == 409
    assert called["delete_run"] is False
