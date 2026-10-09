"""Storage-kernel tests — layout scaffold, manifest v2, additive migrator.

Fast, NO SPICE. Everything runs in ``tmp_path``; ``WORK_ROOT`` is monkeypatched
so nothing touches a real ``./work``. Pins the storage contract: scaffold +
migration are additive and idempotent, manifest writes are atomic with a
monotonic ``rev``, and nothing a v1 reader depends on ever moves.
"""

import contextlib
import json
import logging
import os
import threading

import pytest
from spicexplorer_core import paths
from spicexplorer_core import workspace as ws
from spicexplorer_core.workspace import layout
from spicexplorer_core.workspace import manifest as manifest_mod
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
    man = ws.new_manifest(
        "proj-ab12cd34", "Proj", source={"kind": "new"}, now="2026-07-14T00:00:00"
    )
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
        "id": "demo-ab12cd34",
        "slug": "demo",
        "name": "Demo",
        "created": "2026-07-01T00:00:00",
        "updated": "2026-07-01T00:00:00",
        "source": {"kind": "example", "ref": "OTA/x"},
        "schema_version": 1,
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
    (pd / "manifest.json").write_text(
        json.dumps(
            {
                "id": "demo-ab12cd34",
                "slug": "demo",
                "name": "Demo",
                "source": {"kind": "new"},
                "schema_version": 1,
            }
        )
    )
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


# --- work_root() never resolves into a read-only install (OPT-05) ---------------------
# The lab exports SPICEXPLORER_ROOT=<shared read-only checkout> and no WORK_ROOT, so the
# default ``project_root()/work`` is somewhere a member cannot write.


@pytest.fixture
def install(tmp_path, monkeypatch):
    """SPICEXPLORER_ROOT=<a fresh install dir> with WORK_ROOT unset; yields the dir."""
    install = tmp_path / "install"
    install.mkdir()
    monkeypatch.delenv(layout.WORK_ROOT_ENV, raising=False)
    monkeypatch.setenv(paths.ROOT_ENV_VAR, str(install))
    monkeypatch.setattr(layout, "_FALLBACK_NOTED", set(), raising=False)
    paths.clear_cache()
    try:
        yield install
    finally:
        for d in (install / "work", install):
            if d.exists():
                d.chmod(0o755)
        paths.clear_cache()


@pytest.fixture
def ro_install(install):
    """``install``, for the tests that take permissions away (root ignores them)."""
    if os.geteuid() == 0:
        pytest.skip("root ignores directory permissions")
    return install


def test_work_root_falls_back_to_sx_scratch_when_default_is_read_only(
    ro_install, tmp_path, monkeypatch, caplog
):
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    ro_install.chmod(0o555)
    with caplog.at_level(logging.WARNING, logger=layout.__name__):
        root = ws.work_root()
        assert ws.work_root() == root  # stable across calls
    assert root == (tmp_path / "scratch" / "work").resolve()
    assert root.is_dir()
    assert not (ro_install / "work").exists()
    notes = [r for r in caplog.records if r.name == layout.__name__]
    assert len(notes) == 1  # said once, not per call
    msg = notes[0].getMessage()
    assert str(root) in msg and "WORK_ROOT" in msg
    assert str((ro_install / "work").resolve()) in msg  # names the default it skipped


def test_work_root_falls_back_to_per_user_dir_without_sx_scratch(ro_install, tmp_path, monkeypatch):
    monkeypatch.delenv("SX_SCRATCH", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    ro_install.chmod(0o555)
    assert ws.work_root() == (tmp_path / "home" / "sx-scratch" / "work").resolve()


def test_work_root_skips_an_existing_read_only_work_dir(ro_install, tmp_path, monkeypatch):
    # The admin ran something in the shared checkout once, so ``work/`` exists there
    # but belongs to someone else: resolving to it would defer the failure to the
    # first checkpoint write.
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    (ro_install / "work").mkdir()
    (ro_install / "work").chmod(0o555)
    assert ws.work_root() == (tmp_path / "scratch" / "work").resolve()


def test_work_root_keeps_a_writable_default(ro_install, tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    with caplog.at_level(logging.WARNING, logger=layout.__name__):
        assert ws.work_root() == (ro_install / "work").resolve()
    assert not caplog.records
    assert not (tmp_path / "scratch").exists()


def test_work_root_skips_a_work_dir_it_cannot_enter(ro_install, tmp_path, monkeypatch):
    # Writable but not searchable (no x bit): nothing can be created inside it.
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    (ro_install / "work").mkdir()
    (ro_install / "work").chmod(0o655)
    assert ws.work_root() == (tmp_path / "scratch" / "work").resolve()


def test_work_root_skips_a_file_named_work(install, tmp_path, monkeypatch):
    # A stray *file* called ``work`` — even an executable one — is not a work root;
    # resolving to it would fail on mkdir with FileExistsError.
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    (install / "work").write_text("")
    (install / "work").chmod(0o755)
    assert ws.work_root() == (tmp_path / "scratch" / "work").resolve()
    assert (install / "work").is_file()  # left alone


def test_work_root_expands_a_tilde_in_sx_scratch(ro_install, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # an unexpanded ``~`` would land under the CWD
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("SX_SCRATCH", "~/scratch")
    ro_install.chmod(0o555)
    assert ws.work_root() == (tmp_path / "home" / "scratch" / "work").resolve()
    assert not (tmp_path / "~").exists()


def test_work_root_honours_an_unwritable_explicit_work_root(
    ro_install, tmp_path, monkeypatch, caplog
):
    # WORK_ROOT is the user's stated choice: it fails loudly on mkdir instead of being
    # overridden by the scratch fallback.
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    monkeypatch.setenv(layout.WORK_ROOT_ENV, str(ro_install / "work"))
    ro_install.chmod(0o555)
    with caplog.at_level(logging.WARNING, logger=layout.__name__), pytest.raises(PermissionError):
        ws.work_root()
    assert not caplog.records
    assert not (tmp_path / "scratch").exists()


# --- manifest compare-and-swap on ``rev`` (OPT-F5, plan §3.8 rule 2) ------------------


def _seed_manifest(tmp_path):
    pd = tmp_path / "proj-ab12cd34"
    man = ws.new_manifest(
        "proj-ab12cd34", "Proj", source={"kind": "new"}, now="2026-07-14T00:00:00"
    )
    return pd, ws.write_manifest(pd, man)


def test_write_manifest_cas_rejects_the_second_stale_writer(tmp_path):
    pd, _ = _seed_manifest(tmp_path)
    a, b = ws.read_manifest(pd), ws.read_manifest(pd)  # both read rev 1
    written = ws.write_manifest(pd, dict(a, name="A"), expected_rev=a["rev"])
    assert written["rev"] == 2
    with pytest.raises(ws.ManifestConflict) as exc:
        ws.write_manifest(pd, dict(b, name="B"), expected_rev=b["rev"])
    assert (exc.value.expected, exc.value.actual) == (1, 2)
    on_disk = ws.read_manifest(pd)
    assert on_disk["name"] == "A" and on_disk["rev"] == 2  # B's write was not saved


def test_write_manifest_cas_rejects_an_expected_rev_ahead_of_disk(tmp_path):
    # The swap is on equality: a writer claiming a rev the disk never reached is as
    # wrong as a stale one.
    pd, _ = _seed_manifest(tmp_path)
    with pytest.raises(ws.ManifestConflict) as exc:
        ws.write_manifest(pd, dict(ws.read_manifest(pd), name="X"), expected_rev=5)
    err = exc.value
    assert (err.expected, err.actual) == (5, 1)
    assert isinstance(err, RuntimeError)
    assert str(pd / ws.MANIFEST_NAME) in str(err)
    assert "expected rev 5" in str(err) and "found rev 1" in str(err)
    on_disk = ws.read_manifest(pd)
    assert on_disk["name"] == "Proj" and on_disk["rev"] == 1


def test_write_manifest_cas_on_rev_zero_is_create_only(tmp_path):
    # ``expected_rev=0`` is a real expectation (no manifest yet), not "no CAS".
    pd = tmp_path / "proj-ab12cd34"  # absent: the write creates the project dir
    man = ws.new_manifest(
        "proj-ab12cd34", "Proj", source={"kind": "new"}, now="2026-07-14T00:00:00"
    )
    assert ws.write_manifest(pd, man, expected_rev=0)["rev"] == 1
    with pytest.raises(ws.ManifestConflict) as exc:
        ws.write_manifest(pd, dict(man, name="Late"), expected_rev=0)
    assert (exc.value.expected, exc.value.actual) == (0, 1)
    assert ws.read_manifest(pd)["name"] == "Proj"


@pytest.mark.parametrize("expected_rev", [None, 1], ids=["legacy", "cas"])
def test_write_manifest_holds_an_exclusive_lock_across_read_and_write(
    tmp_path, monkeypatch, expected_rev
):
    fcntl = pytest.importorskip("fcntl")
    pd, _ = _seed_manifest(tmp_path)
    data = ws.read_manifest(pd)
    seen = []

    def probed(fn):
        # A second open file is a second flock owner, even in this process: if the
        # writer holds LOCK_EX, a non-blocking shared lock must be refused.
        def wrapped(*args, **kwargs):
            with open(pd / manifest_mod.LOCK_NAME, "a") as fh:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                except BlockingIOError:
                    seen.append((fn.__name__, "held"))
                else:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                    seen.append((fn.__name__, "free"))
            return fn(*args, **kwargs)

        return wrapped

    monkeypatch.setattr(manifest_mod, "read_manifest", probed(manifest_mod.read_manifest))
    monkeypatch.setattr(manifest_mod, "atomic_write_json", probed(manifest_mod.atomic_write_json))
    ws.write_manifest(pd, data, expected_rev=expected_rev)
    assert seen == [("read_manifest", "held"), ("atomic_write_json", "held")]


def test_write_manifest_without_fcntl_still_writes_and_checks(tmp_path, monkeypatch):
    # Non-POSIX hosts: no lock file, but the atomic write and the rev check still hold.
    monkeypatch.setattr(manifest_mod, "fcntl", None)
    pd, _ = _seed_manifest(tmp_path)
    assert not (pd / manifest_mod.LOCK_NAME).exists()
    assert ws.write_manifest(pd, ws.read_manifest(pd), expected_rev=1)["rev"] == 2
    with pytest.raises(ws.ManifestConflict):
        ws.write_manifest(pd, ws.read_manifest(pd), expected_rev=1)
    assert ws.read_manifest(pd)["rev"] == 2


def test_update_manifest_retries_with_fresh_state(tmp_path):
    pd, _ = _seed_manifest(tmp_path)
    calls = []

    def rename(man):
        calls.append(man["rev"])
        if len(calls) == 1:  # another writer lands between our read and our write
            ws.write_manifest(pd, dict(ws.read_manifest(pd), default_pdk="ihp-sg13g2"))
        return dict(man, name="Renamed")

    written = ws.update_manifest(pd, rename)
    assert calls == [1, 2]  # the retry saw the concurrent write
    on_disk = ws.read_manifest(pd)
    assert on_disk == written
    assert on_disk["name"] == "Renamed" and on_disk["default_pdk"] == "ihp-sg13g2"
    assert on_disk["rev"] == 3


def test_update_manifest_gives_up_after_retries(tmp_path):
    pd, _ = _seed_manifest(tmp_path)

    def always_raced(man):
        ws.write_manifest(pd, ws.read_manifest(pd))
        return dict(man, name="never")

    with pytest.raises(ws.ManifestConflict):
        ws.update_manifest(pd, always_raced, retries=2)
    assert ws.read_manifest(pd)["name"] == "Proj"


@pytest.mark.parametrize("retries", [0, 2])
def test_update_manifest_makes_exactly_retries_plus_one_attempts(tmp_path, retries):
    pd, _ = _seed_manifest(tmp_path)
    seen_revs = []

    def always_raced(man):
        seen_revs.append(man["rev"])
        ws.write_manifest(pd, ws.read_manifest(pd))
        return dict(man, name="never")

    with pytest.raises(ws.ManifestConflict):
        ws.update_manifest(pd, always_raced, retries=retries)
    # One first try plus ``retries`` reruns, each on the state the last race left.
    assert seen_revs == list(range(1, retries + 2))


@pytest.mark.parametrize("races, gives_up", [(5, False), (6, True)])
def test_update_manifest_default_budget_is_five_retries(tmp_path, races, gives_up):
    pd, _ = _seed_manifest(tmp_path)
    calls = []

    def raced(man):
        calls.append(man["rev"])
        if len(calls) <= races:
            ws.write_manifest(pd, ws.read_manifest(pd))
        return dict(man, name="Done")

    outcome = pytest.raises(ws.ManifestConflict) if gives_up else contextlib.nullcontext()
    with outcome:
        ws.update_manifest(pd, raced)
    assert len(calls) == 6
    assert (ws.read_manifest(pd)["name"] == "Done") is not gives_up


def test_update_manifest_accepts_an_in_place_edit(tmp_path):
    pd, _ = _seed_manifest(tmp_path)

    def rename(man):
        man["name"] = "Edited"  # edits the copy it was given, returns None

    written = ws.update_manifest(pd, rename)
    assert written["name"] == "Edited" and written["rev"] == 2
    assert ws.read_manifest(pd) == written


def test_update_manifest_compares_against_the_rev_it_read(tmp_path):
    # ``fn`` edits a copy, so one that bumps ``rev`` itself cannot turn its own write
    # into a conflict (with retries=0 that would raise).
    pd, _ = _seed_manifest(tmp_path)

    def self_bumping(man):
        man["rev"] += 1
        man["name"] = "Bumped"

    written = ws.update_manifest(pd, self_bumping, retries=0)
    assert written["name"] == "Bumped"
    assert ws.read_manifest(pd) == written


def test_update_manifest_creates_a_missing_manifest(tmp_path):
    pd = tmp_path / "proj-fresh"  # no dir, no manifest: read gives {} at rev 0
    written = ws.update_manifest(pd, lambda man: dict(man, name="Fresh"))
    assert written["rev"] == 1 and written["schema_version"] == ws.SCHEMA_VERSION
    assert ws.read_manifest(pd) == written


def test_update_manifest_loses_no_concurrent_update(tmp_path):
    pd, _ = _seed_manifest(tmp_path)
    workers, per_worker = 4, 10

    def bump(man):
        return dict(man, counter=int(man.get("counter", 0)) + 1)

    errors: list[BaseException] = []

    def worker():
        try:
            for _ in range(per_worker):
                ws.update_manifest(pd, bump, retries=10_000)
        except BaseException as e:  # checked in the test thread, not left as a warning
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    on_disk = ws.read_manifest(pd)
    assert on_disk["counter"] == workers * per_worker
    assert on_disk["rev"] == 1 + workers * per_worker
