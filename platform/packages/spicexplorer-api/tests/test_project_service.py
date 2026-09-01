"""Tests for the project registry + per-run isolation service (report.md P2/P3).

Fast, NO SPICE. Uses a temp WORK_ROOT so nothing touches the real ./work.
"""
import json
import sys
from pathlib import Path

import pytest
import yaml
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


@pytest.fixture
def ps(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from spicexplorer_api.services import project_service as _ps
    return _ps


def test_create_project_scaffolds_example_structure(ps):
    pid = ps.create_project("My OTA")
    assert pid.startswith("my-ota-")
    pd = ps.project_dir(pid)
    assert (pd / "project.yaml").exists()
    for sub in ("spice", "xschem", "scratch", "runs"):
        assert (pd / sub).is_dir()
    data = yaml.safe_load((pd / "project.yaml").read_text())
    assert data["project"]["ws_root"] == "."
    assert data["project"]["outdir"] == "scratch"
    man = ps.read_manifest(pid)
    assert man["name"] == "My OTA" and man["source"]["kind"] == "new"
    assert any(p["id"] == pid for p in ps.list_projects())


def test_copy_example_registers_loadable_project(ps):
    examples = ps.list_examples()
    assert examples, "expected in-repo examples"
    cascode = next((e for e in examples if "cascode" in e["key"]), examples[0])
    pid = ps.copy_example(cascode["key"], "Demo Copy")
    pd = ps.project_dir(pid)
    data = yaml.safe_load((pd / "project.yaml").read_text())
    assert data["project"]["ws_root"] == "."
    # The copied subtree resolves — the project parses from its new home.
    from spicexplorer.core.domains import Project_Setup
    Project_Setup.from_yaml(pd / "project.yaml")
    assert ps.read_manifest(pid)["source"]["kind"] == "example"


def test_resolve_yaml_prefers_project_id_and_guards(ps):
    pid = ps.create_project("X")
    assert ps.resolve_yaml(pid, None) == ps.project_yaml(pid)
    # Unknown id raises rather than silently falling through (the yaml_path="" guard).
    with pytest.raises(FileNotFoundError):
        ps.resolve_yaml("nope-00000000", None)
    assert ps.resolve_yaml(None, "/x/y.yaml") == Path("/x/y.yaml")
    assert ps.resolve_yaml(None, None) == ps.default_yaml_path()


def test_run_dir_and_list_runs(ps):
    pid = ps.create_project("R")
    rd = ps.run_dir(pid, "2026_LhsDE_abcd1234")
    (rd / "run.json").write_text(json.dumps({"run_id": "r1", "status": "done", "best_score": 1.5}))
    runs = ps.list_runs(pid)
    assert len(runs) == 1 and runs[0]["status"] == "done"


def test_reconcile_flips_running_to_error(ps):
    pid = ps.create_project("C")
    rd = ps.run_dir(pid, "2026_x_aaaa1111")
    (rd / "run.json").write_text(json.dumps({"run_id": "r", "status": "running"}))
    assert ps.reconcile_stale_runs() == 1
    assert json.loads((rd / "run.json").read_text())["status"] == "error"


def test_guards_reject_path_traversal(ps):
    with pytest.raises(ValueError):
        ps.project_dir("../escape")
    with pytest.raises(ValueError):
        ps.project_dir("a/b")


# ---------- P4 lifecycle: rename / fork / soft-delete + restore ----------


def test_rename_project_edits_manifest_only_dir_stable(ps):
    pid = ps.create_project("Old Name")
    man = ps.rename_project(pid, "New Name")
    assert man["name"] == "New Name"
    # The dir id is the stable handle — it does NOT move on rename.
    assert ps.project_dir(pid).exists()
    assert ps.read_manifest(pid)["name"] == "New Name"
    with pytest.raises(ValueError):
        ps.rename_project(pid, "   ")
    with pytest.raises(FileNotFoundError):
        ps.rename_project("missing-00000000", "x")


def test_fork_copies_everything_except_runs(ps):
    pid = ps.create_project("Source")
    # Give the source a run + a stray netlist; the fork must copy the netlist, not the run.
    rd = ps.run_dir(pid, "2026_algo_deadbeef")
    (rd / "run.json").write_text(json.dumps({"run_id": "r1", "status": "done"}))
    (ps.project_dir(pid) / "spice" / "amp.cir").write_text("* netlist\n")

    new_id = ps.fork_project(pid, "Forked")
    assert new_id != pid
    npd = ps.project_dir(new_id)
    assert (npd / "project.yaml").exists()
    assert (npd / "spice" / "amp.cir").exists()           # design copied
    assert list((npd / "runs").glob("*")) == []           # run history NOT copied
    assert ps.read_manifest(new_id)["source"] == {"kind": "fork", "ref": pid}
    assert ps.list_runs(new_id) == []


def test_soft_delete_moves_to_trash_and_restores(ps):
    pid = ps.create_project("Doomed")
    trash_id = ps.soft_delete_project(pid)
    # Gone from the registry, present in the trash.
    assert not ps.project_exists(pid)
    assert not ps.project_dir(pid).exists()
    assert any(t["trash_id"] == trash_id for t in ps.list_trash())
    # Restore brings it back under its original id with metadata intact.
    restored = ps.restore_project(trash_id)
    assert restored == pid
    assert ps.project_exists(pid)
    assert ps.read_manifest(pid)["name"] == "Doomed"
    assert all(t["trash_id"] != trash_id for t in ps.list_trash())


def test_restore_refuses_to_clobber_existing(ps):
    pid = ps.create_project("Clash")
    trash_id = ps.soft_delete_project(pid)
    # Re-create a project that lands on the same id is impossible (uuid8), but simulate a
    # clash by recreating the dir then restoring.
    ps.project_dir(pid).mkdir(parents=True, exist_ok=True)
    ps.project_yaml(pid).write_text("project: {}\n")
    with pytest.raises(ValueError):
        ps.restore_project(trash_id)


def test_rename_and_delete_run(ps):
    pid = ps.create_project("Runs")
    rd = ps.run_dir(pid, "2026_algo_abcd1234")
    (rd / "run.json").write_text(json.dumps({"run_id": "run-xyz", "status": "done"}))
    # Rename by the stored run_id (not the dir name).
    out = ps.rename_run(pid, "run-xyz", "Best so far")
    assert out["label"] == "Best so far"
    assert json.loads((rd / "run.json").read_text())["label"] == "Best so far"
    # Delete moves the run dir into the trash (recoverable); it leaves the run list.
    ps.delete_run(pid, "run-xyz")
    assert ps.list_runs(pid) == []
    assert not rd.exists()
    with pytest.raises(FileNotFoundError):
        ps.rename_run(pid, "run-xyz", "gone")


def test_delete_run_then_restore_roundtrips_into_runs_not_project(ps):
    """A restored run must land back in the OWNER's runs/ — never as a project dir (which,
    lacking project.yaml, would be a corrupt registry entry squatting the owner's slug)."""
    pid = ps.create_project("Owner")
    rd = ps.run_dir(pid, "2026_algo_abcd1234")
    (rd / "run.json").write_text(json.dumps({"run_id": "run-1", "status": "done"}))
    trash_id = ps.delete_run(pid, "run-1")
    # The trash item is tagged kind=run, and list_trash surfaces it.
    item = next(t for t in ps.list_trash() if t["trash_id"] == trash_id)
    assert item["kind"] == "run" and item["project_id"] == pid
    # Restore returns the OWNER id and puts the run back under the project's runs/.
    assert ps.restore_project(trash_id) == pid
    runs = ps.list_runs(pid)
    assert len(runs) == 1 and runs[0]["run_id"] == "run-1"
    # The project itself is untouched (still a real, loadable project).
    assert ps.project_exists(pid)


def test_restore_run_refuses_when_owner_deleted(ps):
    """Restoring a run whose owner project is gone must refuse (else it recreates a bare,
    project.yaml-less projects/<owner>/ that blocks the owner's own restore)."""
    pid = ps.create_project("Owner")
    rd = ps.run_dir(pid, "2026_algo_abcd1234")
    (rd / "run.json").write_text(json.dumps({"run_id": "run-1", "status": "done"}))
    run_trash = ps.delete_run(pid, "run-1")
    ps.soft_delete_project(pid)  # owner now gone
    with pytest.raises(ValueError):
        ps.restore_project(run_trash)
    # And the bogus owner dir was NOT created as a side effect.
    assert not ps.project_dir(pid).exists()


def test_restore_corrupt_sidecar_raises_runtime_not_value(ps):
    """A corrupt trash sidecar is a data error (→ 500), not a clobber conflict (→ 409)."""
    pid = ps.create_project("Doomed")
    trash_id = ps.soft_delete_project(pid)
    (ps.trash_root() / trash_id / ".trashmeta.json").write_text("{not json")
    with pytest.raises(RuntimeError):
        ps.restore_project(trash_id)


def test_delete_run_trash_id_uses_full_run_id(ps):
    """The trash id embeds the FULL run id (+random suffix), not a truncated prefix, so two
    same-prefix runs deleted in the same second can't collide and clobber each other."""
    pid = ps.create_project("P")
    for rid in ("deadbeef-1111", "deadbeef-2222"):
        rd = ps.run_dir(pid, f"2026_a_{rid[:8]}_{rid[-4:]}")
        (rd / "run.json").write_text(json.dumps({"run_id": rid, "status": "done"}))
    t1 = ps.delete_run(pid, "deadbeef-1111")
    t2 = ps.delete_run(pid, "deadbeef-2222")
    assert t1 != t2
    trash_ids = {t["trash_id"] for t in ps.list_trash()}
    assert {t1, t2} <= trash_ids  # both recoverable, neither buried


# ---------- demos.yaml manifest (curated demo registry) ----------

def _unresolvable_demos() -> list[str]:
    """demos.yaml entries whose project_setup.yaml is not on disk.

    The manifest lists three `analog-db/circuits/...` raw-deck demos that live in the OPTIONAL
    nested `examples/analog-db` submodule. `list_examples()` deliberately SKIPS a listed-but-
    missing entry with a warning rather than failing the picker, so where the submodule is not
    checked out — CI uses `submodules: false` — the returned keys are a strict subset of the
    manifest and the exact-equality assertion below cannot hold. Detect that precisely instead of
    guessing at a sentinel, so the test still RUNS wherever the checkout exists."""
    examples = REPO_ROOT / "examples"
    entries = yaml.safe_load((examples / "demos.yaml").read_text())["demos"]
    return [e for e in entries if not (examples / str(e)).is_file()]


_MISSING_DEMOS = _unresolvable_demos()


@pytest.mark.skipif(
    bool(_MISSING_DEMOS),
    reason=(
        "demos.yaml entries not on disk "
        f"({', '.join(_MISSING_DEMOS)}) — the nested examples/analog-db checkout is not "
        "initialized; run `git submodule update --init examples/analog-db`"
    ),
)
def test_list_examples_follows_committed_manifest(ps):
    """The committed examples/demos.yaml is the single source of what shows up
    (order included); the analog-db mirror projections of the classics are
    curated OUT while the raw-deck demo circuits are IN."""
    manifest = yaml.safe_load((REPO_ROOT / "examples" / "demos.yaml").read_text())["demos"]
    keys = [e["key"] for e in ps.list_examples()]
    assert keys == manifest
    assert "analog-db/circuits/amp_001_5t/project_setup.yaml" not in keys  # de-duped mirror
    assert "analog-db/circuits/amp_008_leung_nmcf/project_setup.yaml" in keys  # a raw-deck demo


def test_manifest_examples_skips_invalid_entries(ps, tmp_path):
    root = tmp_path / "examples"
    (root / "a").mkdir(parents=True)
    (root / "b").mkdir()
    (root / "a" / "project_setup.yaml").write_text("project:\n  name: A\n")
    (root / "b" / "project_setup.yaml").write_text("project:\n  name: B\n")
    (root / "demos.yaml").write_text(
        "demos:\n"
        "  - b/project_setup.yaml\n"          # order: b before a
        "  - a/project_setup.yaml\n"
        "  - missing/project_setup.yaml\n"    # nonexistent → skipped
        "  - ../escape/project_setup.yaml\n"  # traversal → skipped
        "  - a/not_a_setup.yaml\n"            # wrong filename family → skipped
    )
    rows = ps._manifest_examples(root)
    assert [r["key"] for r in rows] == ["b/project_setup.yaml", "a/project_setup.yaml"]
    assert [r["name"] for r in rows] == ["B", "A"]


def test_manifest_examples_absent_falls_back_to_scan(ps, tmp_path):
    root = tmp_path / "examples"
    root.mkdir()
    assert ps._manifest_examples(root) is None


def test_copy_example_seeds_declared_schematic_assets(ps):
    """A demo YAML's top-level assets.xschem (vendored circuit schematics living
    OUTSIDE its ws_root deck dir) is copied into the project's xschem/ tree."""
    key = "analog-db/circuits/ldo_005_buffered_ref/project_setup.yaml"
    try:
        ps._example_yaml_path(key)
    except (FileNotFoundError, ValueError):
        pytest.skip("analog-db submodule not present")
    pid = ps.copy_example(key, "Sch Seed")
    schs = list((ps.project_dir(pid) / "xschem").rglob("*.sch"))
    assert schs, "declared assets.xschem must seed the project's xschem/"
