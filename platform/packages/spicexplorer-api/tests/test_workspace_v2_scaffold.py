"""project_service ⇄ storage-kernel integration (layout v2, plan P1).

Fast, NO SPICE. Pins that the API-side registry now scaffolds the v2 layout,
writes v2 manifests atomically, and lazily migrates a v1 project on restore —
with zero behavior change to the v1 surface (covered by test_project_service.py,
which keeps passing untouched).
"""
import json
import sys

import pytest
from _api_fixtures import REPO_ROOT
from spicexplorer_core import workspace as ws

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


@pytest.fixture
def ps(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from spicexplorer_api.services import project_service as _ps
    return _ps


def test_create_project_scaffolds_v2(ps):
    pid = ps.create_project("V2 Demo")
    pd = ps.project_dir(pid)
    for rel in ws.PROJECT_DIRS_V2:
        assert (pd / rel).is_dir(), rel
    assert (pd / "context" / "PROJECT.md").exists()
    man = ps.read_manifest(pid)
    assert man["schema_version"] == ws.SCHEMA_VERSION
    assert man["default_job"] == "project.yaml" and man["rev"] == 1
    # project.yaml still at the root — the D-2 invariant the v1 surface relies on.
    assert ps.resolve_yaml(pid, None) == pd / "project.yaml"


def test_manifest_writes_are_atomic_with_monotonic_rev(ps):
    pid = ps.create_project("Rev Counter")
    rev0 = ps.read_manifest(pid)["rev"]
    ps.rename_project(pid, "Renamed Once")
    ps.touch_manifest(pid)
    man = ps.read_manifest(pid)
    assert man["name"] == "Renamed Once" and man["rev"] == rev0 + 2
    assert not list(ps.project_dir(pid).glob(".*.tmp"))  # no torn/temp leftovers


def test_fork_gets_fresh_v2_manifest_and_scaffold(ps):
    pid = ps.create_project("Origin")
    new_id = ps.fork_project(pid, "Fork")
    man = ps.read_manifest(new_id)
    assert man["source"] == {"kind": "fork", "ref": pid}
    assert man["schema_version"] == ws.SCHEMA_VERSION
    assert (ps.project_dir(new_id) / "context" / "decisions.ndjson").exists()


def test_restore_lazily_migrates_a_v1_project(ps):
    pid = ps.create_project("Time Traveler")
    pd = ps.project_dir(pid)
    # Devolve to a v1 project: strip the v2 additions, downgrade the manifest.
    import shutil
    for rel in ("spec", "topology", "design", "testbenches", "jobs", "analyses",
                "layout", "context"):
        shutil.rmtree(pd / rel)
    (pd / "manifest.json").write_text(json.dumps({
        "id": pid, "slug": pid.rsplit("-", 1)[0], "name": "Time Traveler",
        "source": {"kind": "new"}, "schema_version": 1,
    }))
    trash_id = ps.soft_delete_project(pid)
    restored = ps.restore_project(trash_id)
    assert restored == pid
    # Restore ran the additive migrator (plan D-11): v2 structure + manifest back.
    assert (pd / "spec").is_dir() and (pd / "context" / "PROJECT.md").exists()
    assert ps.read_manifest(pid)["schema_version"] == ws.SCHEMA_VERSION
