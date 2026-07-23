"""Storage-kernel tests — layout scaffold, manifest v2, additive migrator.

Fast, NO SPICE. Everything runs in ``tmp_path``; ``WORK_ROOT`` is monkeypatched
so nothing touches a real ``./work``. Pins the storage contract: scaffold +
migration are additive and idempotent, manifest writes are atomic with a
monotonic ``rev``, and nothing a v1 reader depends on ever moves.
"""
import json

from spicexplorer_core import workspace as ws
from spicexplorer_core.workspace.__main__ import main as migrate_cli


def test_work_root_env(monkeypatch, tmp_path):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    root = ws.work_root()
    assert root == (tmp_path / "wr").resolve()
    assert root.is_dir()  # created on resolve


def test_scaffold_project_idempotent(tmp_path):
    pd = tmp_path / "proj-ab12cd34"
    pd.mkdir()
    created = ws.scaffold_project(pd)
    for rel in ws.PROJECT_DIRS_V2:
        assert (pd / rel).is_dir()
    assert (pd / "context" / "decisions.ndjson").exists()
    assert "GENERATED" in (pd / "context" / "PROJECT.md").read_text()
    assert created  # first pass reports work
    assert ws.scaffold_project(pd) == []  # second pass is a no-op


def test_scaffold_dry_run_writes_nothing(tmp_path):
    pd = tmp_path / "proj-ab12cd34"
    pd.mkdir()
    planned = ws.scaffold_project(pd, dry_run=True)
    assert planned
    assert list(pd.iterdir()) == []  # nothing materialized


def test_write_manifest_bumps_rev_and_leaves_no_temp(tmp_path):
    pd = tmp_path / "proj-ab12cd34"
    pd.mkdir()
    man = ws.new_manifest("proj-ab12cd34", "Proj", source={"kind": "new"}, now="2026-07-14T00:00:00")
    written = ws.write_manifest(pd, man)
    assert written["rev"] == 1 and written["schema_version"] == ws.SCHEMA_VERSION
    assert written["default_job"] == "project.yaml"
    # A stale caller copy can't rewind rev — writes advance past the on-disk value.
    written2 = ws.write_manifest(pd, dict(man, rev=0, name="Renamed"))
    assert written2["rev"] == 2
    assert ws.read_manifest(pd)["name"] == "Renamed"
    assert not list(pd.glob("*.tmp")) and not list(pd.glob(".*.tmp"))


def test_read_manifest_tolerates_missing_and_torn(tmp_path):
    pd = tmp_path / "proj-ab12cd34"
    pd.mkdir()
    assert ws.read_manifest(pd) == {}
    (pd / ws.MANIFEST_NAME).write_text('{"id": "proj-ab12cd34", "na')  # torn write
    assert ws.read_manifest(pd) == {}


def test_upgrade_manifest_v1_preserves_everything(tmp_path):
    pd = tmp_path / "demo-ab12cd34"
    pd.mkdir()
    v1 = {
        "id": "demo-ab12cd34", "slug": "demo", "name": "Demo",
        "created": "2026-07-01T00:00:00", "updated": "2026-07-01T00:00:00",
        "source": {"kind": "example", "ref": "OTA/x"}, "schema_version": 1,
        "custom_key": "survives",
    }
    (pd / ws.MANIFEST_NAME).write_text(json.dumps(v1))
    man, changed = ws.upgrade_manifest(pd)
    assert changed
    assert man["schema_version"] == ws.SCHEMA_VERSION and man["rev"] >= 1
    assert man["default_job"] == "project.yaml" and man["default_pdk"] is None
    # v1 values + unknown keys are preserved verbatim.
    for k in ("id", "slug", "name", "created", "source", "custom_key"):
        assert man[k] == v1[k]
    _, changed_again = ws.upgrade_manifest(pd)
    assert not changed_again  # idempotent


def test_upgrade_manifest_synthesizes_from_dirname(tmp_path):
    pd = tmp_path / "bare-ab12cd34"
    pd.mkdir()
    man, changed = ws.upgrade_manifest(pd)
    assert changed
    assert man["id"] == "bare-ab12cd34" and man["slug"] == "bare"


def _make_v1_workspace(root):
    """A synthetic pre-v2 WORK_ROOT: one project, legacy trees, trash, noise."""
    pd = root / "projects" / "demo-ab12cd34"
    (pd / "spice").mkdir(parents=True)
    (pd / "runs" / "run_x").mkdir(parents=True)
    (pd / "project.yaml").write_text("project:\n  ws_root: .\n  outdir: scratch\n")
    (pd / "manifest.json").write_text(json.dumps({
        "id": "demo-ab12cd34", "slug": "demo", "name": "Demo",
        "source": {"kind": "new"}, "schema_version": 1,
    }))
    (pd / "runs" / "run_x" / "run.json").write_text('{"run_id": "abc", "status": "done"}')
    (root / "auto_save" / "sim_tb").mkdir(parents=True)
    (root / "auto_save" / "sim_tb" / "ckpt.json").write_text("{}")
    (root / ".trash" / "old__20260701").mkdir(parents=True)
    (root / ".trash" / "old__20260701" / ".trashmeta.json").write_text("{}")
    (root / "projects" / "not-a-project").mkdir()
    return pd


def test_migrate_workspace_is_additive_and_idempotent(tmp_path):
    root = tmp_path / "work"
    pd = _make_v1_workspace(root)
    before_yaml = (pd / "project.yaml").read_bytes()
    before_run = (pd / "runs" / "run_x" / "run.json").read_bytes()

    report = ws.migrate_workspace(root)
    assert report["changed"]
    # v2 structure created; shared tree created.
    for rel in ws.PROJECT_DIRS_V2:
        assert (pd / rel).is_dir()
    for rel in ws.SHARED_DIRS:
        assert (root / rel).is_dir()
    man = ws.read_manifest(pd)
    assert man["schema_version"] == ws.SCHEMA_VERSION and man["name"] == "Demo"
    # NOTHING moved or rewritten: default job + run payloads byte-identical.
    assert (pd / "project.yaml").read_bytes() == before_yaml
    assert (pd / "runs" / "run_x" / "run.json").read_bytes() == before_run
    # Legacy trees + trash untouched; non-project dirs skipped, not "migrated".
    assert (root / "auto_save" / "sim_tb" / "ckpt.json").exists()
    assert (root / ".trash" / "old__20260701" / ".trashmeta.json").exists()
    assert not (root / ".trash" / "old__20260701" / "spec").exists()
    assert "not-a-project" in report["skipped"]

    # Re-run: a strict no-op.
    report2 = ws.migrate_workspace(root)
    assert not report2["changed"]
    assert all(not p["changed"] for p in report2["projects"])


def test_migrate_workspace_dry_run_writes_nothing(tmp_path):
    root = tmp_path / "work"
    pd = _make_v1_workspace(root)
    report = ws.migrate_workspace(root, dry_run=True)
    assert report["changed"] and report["dry_run"]
    assert not (pd / "spec").exists()
    assert not (root / "shared").exists()
    assert ws.read_manifest(pd)["schema_version"] == 1  # manifest untouched


def test_migrate_cli_smoke(tmp_path, capsys):
    root = tmp_path / "work"
    _make_v1_workspace(root)
    assert migrate_cli(["--work-root", str(root)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["changed"] and report["work_root"] == str(root.resolve())
