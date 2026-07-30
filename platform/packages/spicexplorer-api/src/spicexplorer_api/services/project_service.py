"""Project encapsulation + per-run isolation bookkeeping (report.md P2/P3).

Owns ALL of ``WORK_ROOT``: the project registry (a *directory convention*, no DB),
per-run dirs, manifests, and the single ``project_id → project.yaml`` resolver. No
filesystem logic leaks into route handlers. Every destructive/copy op is guarded to
paths strictly under ``work_root()`` (same defence-in-depth as ``delete_checkpoint``).

The layout (one directory per project, example-structured so it runs unedited):

    WORK_ROOT/projects/<slug>-<id8>/
        project.yaml        # ws_root: .   outdir: scratch  — the DEFAULT job (stays at root, D-2)
        manifest.json       # the identity record (schema v2) — core never reads it
        spice/  xschem/     # copied netlists/schematics (a "new" project gets empty dirs)
        scratch/            # ephemeral one-off sims (out of the source tree)
        runs/<run_name>/    # per-run isolation (checkpoints/, run.log, events.ndjson, …)
        spec/ topology/ design/ testbenches/ jobs/ analyses/ layout/ context/
                            # layout v2 (meta doc/plan_project_filesystem.md §3.2) —
                            # scaffolded by spicexplorer_core.workspace

The layout schema, manifest schema, and migrator live in the storage kernel
(``spicexplorer_core.workspace``) so orchestration agents speak the same contract;
this module keeps owning the API-side registry/lifecycle bookkeeping on top of it.
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from spicexplorer_core import workspace as ws

from spicexplorer_api.app_config import (
    REPO_ROOT,
    default_yaml_path,
    projects_root,
    runs_root,
    trash_root,
    work_root,
)

logger = logging.getLogger(__name__)

SCHEMA_VERSION = ws.SCHEMA_VERSION


# ---------- ids / guards ----------

def _slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "project").lower()).strip("-")
    return s[:40] or "project"


def new_project_id(name: str) -> str:
    return f"{_slugify(name)}-{uuid.uuid4().hex[:8]}"


def _assert_under_work_root(p: Path) -> Path:
    rp = p.resolve()
    wr = work_root().resolve()
    if rp != wr and wr not in rp.parents:
        raise ValueError(f"refusing to touch a path outside WORK_ROOT: {rp}")
    return rp


def project_dir(project_id: str) -> Path:
    if not project_id or "/" in project_id or "\\" in project_id or ".." in project_id:
        raise ValueError(f"invalid project id: {project_id!r}")
    return projects_root() / project_id


def manifest_path(project_id: str) -> Path:
    return project_dir(project_id) / "manifest.json"


def project_yaml(project_id: str) -> Path:
    return project_dir(project_id) / "project.yaml"


def project_exists(project_id: str) -> bool:
    try:
        return project_yaml(project_id).exists()
    except ValueError:
        return False


# ---------- manifest ----------

def read_manifest(project_id: str) -> dict[str, Any]:
    return ws.read_manifest(project_dir(project_id))


def write_manifest(project_id: str, data: dict[str, Any]) -> None:
    # Atomic (temp → fsync → replace) + monotonic ``rev`` via the storage kernel:
    # a torn manifest.json must never equal a vanished project (plan §3.8).
    _assert_under_work_root(manifest_path(project_id))
    ws.write_manifest(project_dir(project_id), data)
    # Index write-through (P2): the manifest write is the last step of every
    # project mutation (create/copy/fork/rename/touch/restore), so this ONE
    # chokepoint keeps the derived index content-fresh. Best-effort by contract
    # (the FS is canonical); lazy import avoids a module cycle.
    from spicexplorer_api.services import index_db
    index_db.notify_project_changed(project_id)


def touch_manifest(project_id: str) -> None:
    man = read_manifest(project_id)
    man["updated"] = datetime.now().isoformat(timespec="seconds")
    write_manifest(project_id, man)


# ---------- THE single resolver ----------

def resolve_yaml(project_id: str | None, yaml_path: str | None) -> Path:
    """Resolve the project YAML: ``project_id`` → its ``project.yaml``; else an explicit
    ``yaml_path``; else the default example. This is the ONE place "current project"
    is resolved, so a registry can't resurrect the ``yaml_path=""`` regression."""
    if project_id:
        yp = project_yaml(project_id)
        if not yp.exists():
            raise FileNotFoundError(f"project '{project_id}' not found")
        return yp
    if yaml_path:
        return Path(yaml_path)
    return default_yaml_path()


# ---------- runs ----------

def runs_dir(project_id: str | None) -> Path:
    base = (project_dir(project_id) / "runs") if project_id else runs_root()
    base.mkdir(parents=True, exist_ok=True)
    return base


def run_dir(project_id: str | None, run_name: str) -> Path:
    if "/" in run_name or ".." in run_name:
        raise ValueError(f"invalid run name: {run_name!r}")
    d = runs_dir(project_id) / run_name
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- the canonical run-envelope seam (plan P3 §3.3) ----------
#
# One begin/finalize pair for every ONE-SHOT run kind (simulate today;
# xschem/tf/gmid/annotate next) so the run lifecycle isn't copy-pasted into each
# route. The streaming optimizer keeps its bespoke path (SSE/threads) but writes
# the SAME envelope via the kernel primitives. This is the inverse of
# ``resolve_yaml`` — path bookkeeping stays out of the route handlers.

def project_for_yaml(yaml_path: str | Path) -> tuple[str | None, Path | None]:
    """Reverse-resolve a project's ``project.yaml`` back to ``(project_id, dir)``.
    A non-project YAML (an in-repo example, a not-yet-supported alternate job
    file) returns ``(None, None)`` → the run is recorded UNSCOPED under
    ``WORK_ROOT/runs``. The UI round-trips the path from ``GET /projects/{id}``,
    so the request carries no id of its own."""
    p = Path(yaml_path).resolve()
    if p.name == "project.yaml" and p.parent.parent == projects_root().resolve():
        pid = p.parent.name
        if project_exists(pid):
            return pid, project_dir(pid)
    return None, None


def begin_run(
    kind: str,
    *,
    project_id: str | None,
    label: str | None = None,
    input_files: dict[str, Path] | None = None,
    input_values: dict[str, Any] | None = None,
    coordinates: dict[str, Any] | None = None,
    retention: str = "metrics_only",
    record_extras: dict[str, Any] | None = None,
) -> tuple[str, Path]:
    """Mint a run dir (dir == run_id), content-address its inputs into the owning
    project's ``.objects/``, and commit an initial ``status: running`` envelope
    record. Returns ``(run_id, run_dir)``. Raises ``OSError`` if the run dir can't
    be created — the caller decides whether that's fatal."""
    run_id, rdir = ws.mint_run_dir(runs_dir(project_id), kind)
    pdir = project_dir(project_id) if project_id else None
    inputs = ws.snapshot_inputs(
        ws.project_objects_dir(pdir), files=input_files, values=input_values)
    ws.write_run_record(rdir, {
        "run_id": run_id,
        "project_id": project_id,
        "label": label,
        "status": "running",
        "started": datetime.now().isoformat(timespec="seconds"),
        **ws.envelope_fields(kind, retention=retention, inputs=inputs, coordinates=coordinates),
        # Caller-specific record fields (e.g. simulate's keep_raw flag, which the
        # waveview /runs listing surfaces as the "openable" badge) — merged last so
        # a caller can also override the label-style presentation fields.
        **(record_extras or {}),
    })
    return run_id, rdir


def finalize_run(
    project_id: str | None,
    run_dir: Path,
    *,
    status: str,
    score: float | None = None,
    metrics: dict[str, float] | None = None,
    error: str | None = None,
) -> None:
    """Move a run to a terminal status (record update + index write-through).
    Best-effort — the sim/analysis result is already the user-facing return."""
    try:
        rec = ws.read_run_record(run_dir)
        rec.update(
            status=status, best_score=score, metrics=metrics or {},
            ended=datetime.now().isoformat(timespec="seconds"),
        )
        if error:
            rec["error"] = error
        ws.write_run_record(run_dir, rec)
    except OSError:
        pass
    from spicexplorer_api.services import index_db
    index_db.notify_runs_changed(project_id)


def reconcile_stale_runs() -> int:
    """On startup, flip a ``run.json`` left ``status: running`` by a **provably dead**
    writer to ``error`` so the run list is honest (report.md §6). Returns the count.

    Owner-aware (plan §3.3): an envelope run whose owner pid is alive on this host —
    or whose heartbeat is fresh on a foreign host — is a LIVE out-of-process job
    (e.g. an agent's long run) and survives an API restart untouched. A legacy
    run.json (no ``owner`` block) keeps the old always-flip behavior."""
    fixed = 0
    # LIVE locations are owner-aware; the TRASH bin is not. A soft-deleted run was
    # quiesced (stop_runs_for) before the move, so a trashed run is never legitimately
    # live — always flip it, else a foreign-host run with a still-fresh heartbeat (or a
    # future-skewed mtime on the shared /work mount) would resurface as "running" on
    # restore, reopening BUG-B43.
    for base, owner_aware in ((projects_root(), True), (runs_root(), True),
                              (trash_root(), False)):
        for rj in base.rglob("run.json"):
            try:
                d = json.loads(rj.read_text())
            except Exception:
                continue
            if d.get("status") == "running":
                if owner_aware and not ws.owner_is_dead(d, rj.parent):
                    continue
                d["status"] = "error"
                d["ended"] = d.get("ended") or datetime.now().isoformat(timespec="seconds")
                try:
                    rj.write_text(json.dumps(d, indent=2))
                    fixed += 1
                except OSError:
                    pass
    return fixed


def list_runs(project_id: str | None) -> list[dict[str, Any]]:
    # Newest first by the RECORDED start time (dir-name order was only ever a proxy
    # via the old timestamp prefix — plan §3.3), dir name as the deterministic tiebreak.
    entries: list[tuple[str, str, dict[str, Any]]] = []
    for rd in runs_dir(project_id).glob("*"):
        rj = rd / "run.json"
        if rj.exists():
            try:
                d = json.loads(rj.read_text())
            except Exception:
                continue
            entries.append((str(d.get("started") or ""), rd.name, d))
    entries.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [d for _, _, d in entries]


# ---------- registry ----------

def list_projects() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pd in sorted(projects_root().glob("*")):
        if not (pd / "project.yaml").exists():
            continue
        man = read_manifest(pd.name)
        runs = list_runs(pd.name)
        best: float | None = None
        for r in runs:
            bs = r.get("best_score")
            if isinstance(bs, (int, float)) and (best is None or bs > best):
                best = bs
        out.append({
            "id": pd.name,
            "name": man.get("name", pd.name),
            "updated": man.get("updated") or man.get("created"),
            "run_count": len(runs),
            "best_score": best,
            "source": (man.get("source") or {}).get("kind", "unknown"),
        })
    # Newest-updated first.
    out.sort(key=lambda p: p.get("updated") or "", reverse=True)
    return out


# ---------- YAML rewrite (ws_root: . / outdir: scratch) ----------

def _rewrite_project_yaml(yaml_text: str, *, ws_root: str = ".", outdir: str = "scratch") -> str:
    """Bake the encapsulation contract into a project's YAML: ``ws_root`` becomes the
    project dir itself (portable — copy/move it and it still resolves) and ``outdir``
    moves ephemeral sims out of the source tree. NEVER touched for in-repo examples."""
    data = yaml.safe_load(yaml_text)
    if isinstance(data, dict) and isinstance(data.get("project"), dict):
        data["project"]["ws_root"] = ws_root
        data["project"]["outdir"] = outdir
    return yaml.safe_dump(data, sort_keys=False)


# ---------- examples (load demo as project) ----------

def _example_meta(examples_root: Path, yp: Path) -> dict[str, Any]:
    """One example row: key (examples/-relative path) + display name/description.

    The display name is the YAML's own ``project.name`` (path-derived fallback) —
    a path label alone collapses e.g. every analog-db circuit demo into the same
    "analog-db · circuits" string."""
    rel = yp.relative_to(examples_root)
    key = "/".join(rel.parts)
    # Path fallback: the OTA/<topology>/<pdk> portion.
    label = " · ".join(rel.parts[:-2]) if len(rel.parts) >= 2 else rel.parts[0]
    description: str | None = None
    try:
        doc = yaml.safe_load(yp.read_text()) or {}
        proj = doc.get("project") or {}
        if isinstance(proj.get("name"), str) and proj["name"].strip():
            label = proj["name"].strip()
        if isinstance(proj.get("description"), str) and proj["description"].strip():
            description = proj["description"].strip()
    except Exception:
        pass  # unparseable example YAML → keep the path label
    return {"key": key, "name": label, "description": description, "yaml_path": str(yp)}


def _manifest_examples(examples_root: Path) -> list[dict[str, Any]] | None:
    """The curated demo list from ``examples/demos.yaml``, or None to fall back to the scan.

    The manifest is the single knob deciding WHAT shows up as a demo and in what
    order (the owner-facing config file); entries are examples/-relative
    ``project_setup*.yaml`` paths. A listed-but-invalid entry is skipped with a
    warning rather than failing the whole picker."""
    mf = examples_root / "demos.yaml"
    if not mf.is_file():
        return None
    try:
        doc = yaml.safe_load(mf.read_text()) or {}
        entries = doc.get("demos")
    except Exception as e:
        logger.warning("examples/demos.yaml unreadable (%s) — falling back to scan", e)
        return None
    if not isinstance(entries, list) or not entries:
        logger.warning("examples/demos.yaml has no `demos:` list — falling back to scan")
        return None
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        try:
            # validates: under examples/, project_setup*.yaml
            yp = _example_yaml_path(str(entry), examples_root)
        except (ValueError, FileNotFoundError) as e:
            logger.warning("examples/demos.yaml: skipping %r (%s)", entry, e)
            continue
        meta = _example_meta(examples_root, yp)
        if meta["key"] in seen:
            continue
        seen.add(meta["key"])
        out.append(meta)
    return out


def list_examples() -> list[dict[str, Any]]:
    """The Studio demo registry.

    Curated: ``examples/demos.yaml`` (order = display order) when present.
    Fallback: scan every ``project_setup*.yaml`` under examples/."""
    examples_root = REPO_ROOT / "examples"
    curated = _manifest_examples(examples_root)
    if curated is not None:
        return curated
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for yp in sorted(examples_root.rglob("project_setup*.yaml")):
        meta = _example_meta(examples_root, yp)
        if meta["key"] in seen:
            continue
        seen.add(meta["key"])
        out.append(meta)
    return out


def _example_yaml_path(example_key: str, examples_root: Path | None = None) -> Path:
    if examples_root is None:
        examples_root = REPO_ROOT / "examples"
    # Traversal guard on the KEY STRING (example_key can come from an API request,
    # e.g. copy_example): reject absolute keys and any ``..`` segment. We guard the
    # key rather than the post-.resolve() location because examples/ legitimately
    # contains symlinks — notably the analog-db corpus, which resolves OUTSIDE
    # examples/ — and a "resolved path must stay under examples/" check wrongly
    # rejects those. Committed symlinks are trusted; an API caller cannot plant one.
    key = Path(example_key)
    if key.is_absolute() or ".." in key.parts:
        raise ValueError(f"invalid example key: {example_key!r}")
    # Join WITHOUT .resolve(): the returned path must stay lexically under
    # examples/ so callers can ``relative_to(examples_root)`` it (the display key,
    # asset seeding). The ``..``/absolute guard above already blocks traversal;
    # reads/copies still follow committed symlinks (e.g. examples/analog-db) via
    # the OS, and .exists() dereferences them — so resolving here buys nothing but
    # breaks the relative-path callers for symlinked corpora.
    yp = examples_root / key
    # Require the canonical filename family (project_setup.yaml + variants like
    # project_setup_advanced.yaml — the same pattern list_examples discovers).
    if not (yp.name.startswith("project_setup") and yp.suffix == ".yaml"):
        raise ValueError(f"invalid example key: {example_key!r}")
    if not yp.exists():
        raise FileNotFoundError(f"example not found: {example_key}")
    return yp


def _ws_root_dir_of(yaml_path: Path) -> Path:
    """The directory an example's ``ws_root`` resolves to (the subtree to copy)."""
    data = yaml.safe_load(yaml_path.read_text())
    wsr = ((data or {}).get("project") or {}).get("ws_root")
    wsr_s = "" if wsr is None else str(wsr).strip()
    if not wsr_s:
        return yaml_path.parent
    p = Path(wsr_s).expanduser()
    return p if p.is_absolute() else (yaml_path.parent / p).resolve()


def _empty_dirs(pid: str) -> None:
    # The v1 dirs (spice/xschem/scratch/runs) plus the full v2 structure —
    # one idempotent scaffold in the storage kernel covers both eras.
    ws.scaffold_project(project_dir(pid))


def create_project(name: str, yaml_content: str | None = None) -> str:
    """Create a NEW project = an example-structured directory under ``WORK_ROOT/projects``.

    If ``yaml_content`` is given (the wizard's generated YAML) it is written (with
    ``ws_root: .`` / ``outdir: scratch`` baked in); otherwise the default example's YAML
    seeds it. Empty ``spice/``/``xschem/``/``scratch/``/``runs/`` dirs make the layout
    match the examples so the user can drop netlists in and run.
    """
    pid = new_project_id(name)
    pd = project_dir(pid)
    _assert_under_work_root(pd)
    pd.mkdir(parents=True, exist_ok=True)
    src_text = yaml_content if yaml_content else default_yaml_path().read_text()
    project_yaml(pid).write_text(_rewrite_project_yaml(src_text))
    _empty_dirs(pid)
    now = datetime.now().isoformat(timespec="seconds")
    write_manifest(pid, ws.new_manifest(pid, name, source={"kind": "new"}, now=now))
    return pid


def _seed_example_assets(yp: Path, pd: Path) -> None:
    """Copy an example's declared schematic assets into the project's ``xschem/``.

    Demo YAMLs may carry a top-level ``assets.xschem`` list (sibling of
    ``project:``, ignored by the DSL loader): YAML-dir-relative ``.sch``/``.sym``
    paths — e.g. an analog-db circuit's vendored reference schematics, which live
    OUTSIDE the ``ws_root`` deck dir the seeding copytree covers. Structure is
    preserved so sibling ``.sym`` references keep resolving. Best-effort: a bad
    entry is skipped, never fails the load."""
    try:
        doc = yaml.safe_load(yp.read_text()) or {}
        entries = (doc.get("assets") or {}).get("xschem") or []
    except Exception:
        return
    for rel in entries:
        relp = Path(str(rel))
        # relp is the traversal guard: no ``..`` and not absolute, so it can only
        # reference files WITHIN the demo's own directory subtree. That makes the
        # join safe without a post-.resolve() "must stay under examples/" check —
        # which would wrongly drop assets reached through a committed corpus
        # symlink (e.g. examples/analog-db -> the analog-db unit), leaving the
        # seeded xschem/ empty for those demos.
        if relp.is_absolute() or ".." in relp.parts or relp.suffix not in (".sch", ".sym"):
            continue
        src = (yp.parent / relp).resolve()
        if not src.is_file():
            continue
        dest = pd / "xschem" / relp
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        except OSError:
            logger.warning("example asset copy failed: %s", src)


def copy_example(example_key: str, name: str | None = None) -> str:
    """Load a demo AS a project: copy its ``ws_root`` subtree into a fresh project dir
    and rewrite ``ws_root: .`` / ``outdir: scratch``. The in-repo example is untouched."""
    yp = _example_yaml_path(example_key)
    ws_root_dir = _ws_root_dir_of(yp)
    proj_name = name or f"{ws_root_dir.parent.name}-{ws_root_dir.name}"
    pid = new_project_id(proj_name)
    pd = project_dir(pid)
    _assert_under_work_root(pd)
    # Copy the entire ws_root subtree (netlists + schematics) into the project dir.
    shutil.copytree(ws_root_dir, pd, dirs_exist_ok=True)
    # The canonical project.yaml lives at the project root with ws_root: . — netlist
    # paths (relative to ws_root) keep resolving since the subtree was copied verbatim.
    project_yaml(pid).write_text(_rewrite_project_yaml(yp.read_text()))
    ws.scaffold_project(pd)
    _seed_example_assets(yp, pd)
    now = datetime.now().isoformat(timespec="seconds")
    write_manifest(
        pid,
        ws.new_manifest(pid, proj_name, source={"kind": "example", "ref": example_key}, now=now),
    )
    return pid


# ---------- lifecycle: rename / fork / soft-delete + restore (report.md P4) ----------
#
# The directory id (``<slug>-<id8>``) is the STABLE handle and never moves on rename —
# only the manifest ``name`` (and ``updated``) change, so checkpoint paths, run dirs, and
# the active-project pointer all stay valid. Delete is a *move* to ``trash_root()`` (never
# an ``rm``), so it is always restorable. Fork is a ``copytree`` of everything EXCEPT
# ``runs/`` (a fresh project starts with no run history) into a new id.


def rename_project(project_id: str, name: str) -> dict[str, Any]:
    """Rename a project = edit its manifest ``name`` only. The dir id is immutable, so
    nothing on disk moves and every existing path/run/checkpoint keeps resolving."""
    name = (name or "").strip()
    if not name:
        raise ValueError("project name is required")
    if not project_exists(project_id):
        raise FileNotFoundError(f"project '{project_id}' not found")
    man = read_manifest(project_id)
    man["name"] = name
    man["updated"] = datetime.now().isoformat(timespec="seconds")
    write_manifest(project_id, man)
    return man


def fork_project(project_id: str, name: str | None = None) -> str:
    """Copy a project into a NEW id, excluding ``runs/`` (a fork starts run-history-free).
    The ``project.yaml`` / netlists / schematics / scratch are duplicated verbatim."""
    if not project_exists(project_id):
        raise FileNotFoundError(f"project '{project_id}' not found")
    src = read_manifest(project_id)
    src_name = src.get("name", project_id)
    new_name = (name or "").strip() or f"{src_name} (copy)"
    new_id = new_project_id(new_name)
    dst = project_dir(new_id)
    _assert_under_work_root(dst)
    src_dir = project_dir(project_id)
    # Copy everything except per-run state (runs/ + the .trash bin if nested).
    shutil.copytree(
        src_dir, dst,
        ignore=shutil.ignore_patterns("runs", ".trash"),
        dirs_exist_ok=True,
    )
    ws.scaffold_project(dst)
    now = datetime.now().isoformat(timespec="seconds")
    write_manifest(
        new_id,
        ws.new_manifest(new_id, new_name, source={"kind": "fork", "ref": project_id}, now=now),
    )
    return new_id


def soft_delete_project(project_id: str) -> str:
    """MOVE a project dir into ``trash_root()`` (recoverable). Returns the trash id."""
    if not project_exists(project_id):
        raise FileNotFoundError(f"project '{project_id}' not found")
    src = project_dir(project_id)
    _assert_under_work_root(src)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    trash_id = f"{project_id}__{ts}"
    dst = trash_root() / trash_id
    _assert_under_work_root(dst)
    # Record where it came from + when, so restore can put it back and the trash list
    # can show a human label without re-reading the buried manifest.
    man = read_manifest(project_id)
    meta = {
        "trash_id": trash_id, "kind": "project", "project_id": project_id,
        "name": man.get("name", project_id),
        "deleted": datetime.now().isoformat(timespec="seconds"),
    }
    shutil.move(str(src), str(dst))
    (dst / ".trashmeta.json").write_text(json.dumps(meta, indent=2))
    from spicexplorer_api.services import index_db
    index_db.notify_project_deleted(project_id)
    return trash_id


def list_trash() -> list[dict[str, Any]]:
    """Deleted projects awaiting restore/purge, newest first."""
    out: list[dict[str, Any]] = []
    for td in sorted(trash_root().glob("*"), reverse=True):
        meta_p = td / ".trashmeta.json"
        if not meta_p.exists():
            continue
        try:
            out.append(json.loads(meta_p.read_text()))
        except Exception:
            pass
    return out


def purge_trash(trash_id: str) -> None:
    """PERMANENTLY delete one trash item (project or run) — no undo. The id is
    validated exactly like restore's, and the dir must be a real trash entry
    (has the ``.trashmeta.json`` sidecar) under the work root."""
    if "/" in trash_id or ".." in trash_id or "\\" in trash_id:
        raise ValueError(f"invalid trash id: {trash_id!r}")
    src = trash_root() / trash_id
    if not (src / ".trashmeta.json").exists():
        raise FileNotFoundError(f"trash item '{trash_id}' not found")
    _assert_under_work_root(src)
    shutil.rmtree(src)


def restore_project(trash_id: str) -> str:
    """MOVE a trashed item back to the registry. Returns the restored project id (for a
    run item, the OWNING project id). Refuses to clobber an existing destination.

    A trash item is either a project (``kind: project`` → restored to ``project_dir``) or a
    single run (``kind: run`` → restored to the owning project's ``runs/``). Branching on
    ``kind`` is essential: a run dir restored as a project would be a corrupt registry entry
    (no ``project.yaml``) that squats the owner's slug — so deleted runs MUST round-trip
    back into ``runs/``, never ``project_dir``."""
    if "/" in trash_id or ".." in trash_id or "\\" in trash_id:
        raise ValueError(f"invalid trash id: {trash_id!r}")
    src = trash_root() / trash_id
    sidecar = src / ".trashmeta.json"
    if not sidecar.exists():
        raise FileNotFoundError(f"trash item '{trash_id}' not found")
    # A corrupt sidecar is a data error, NOT a 409 conflict — re-raise as non-ValueError so
    # the route maps it to 500 rather than swallowing it as "already exists".
    try:
        meta = json.loads(sidecar.read_text())
    except (json.JSONDecodeError, OSError) as e:
        raise RuntimeError(f"corrupt trash metadata for '{trash_id}': {e}") from e
    _assert_under_work_root(src)

    if meta.get("kind") == "run":
        owner = meta.get("project_id") or None
        # Refuse BEFORE runs_dir() (which would mkdir the tree): restoring into a deleted
        # owner would recreate a bare projects/<owner>/ with no project.yaml — a corrupt
        # entry that then blocks the owner's own restore (dst.exists 409).
        if owner and not project_exists(owner):
            raise ValueError(
                f"cannot restore run: owning project '{owner}' no longer exists — restore it first"
            )
        dst = runs_dir(owner) / meta.get("name", trash_id)
        _assert_under_work_root(dst)
        if dst.exists():
            raise ValueError(f"cannot restore: run '{meta.get('run_id')}' already exists")
        shutil.move(str(src), str(dst))
        (dst / ".trashmeta.json").unlink(missing_ok=True)
        from spicexplorer_api.services import index_db
        index_db.notify_runs_changed(owner)
        return owner or ""

    project_id = meta.get("project_id") or trash_id.split("__", 1)[0]
    dst = project_dir(project_id)
    _assert_under_work_root(dst)
    if dst.exists():
        raise ValueError(f"cannot restore: project '{project_id}' already exists")
    shutil.move(str(src), str(dst))
    # Drop the trash sidecar — it's meaningless once restored.
    (dst / ".trashmeta.json").unlink(missing_ok=True)
    # Lazy v1→v2 migration (plan D-11): a project trashed before a workspace
    # migration ran would otherwise resurface as an unmigrated v1 dir.
    ws.migrate_project(dst)
    touch_manifest(project_id)
    return project_id


# ---------- lifecycle: per-run rename / delete ----------

def find_run_dir(project_id: str | None, run_id: str) -> Path | None:
    """Locate a run's directory by ``run_id``.

    Fast path (P3): the dir name **is** the run_id (``mint_run_dir``), so a single
    stat resolves it in O(1) — this is the scan the P3 plan promised to kill. The
    glob fallback runs only for legacy pre-P3 dirs whose name != the stored id.
    """
    if "/" in run_id or ".." in run_id:  # run_id is a single path segment
        return None
    base = runs_dir(project_id)
    direct = base / run_id
    if (direct / "run.json").is_file():
        return direct
    for rd in base.glob("*"):
        rj = rd / "run.json"
        if not rj.is_file():
            continue
        try:
            if json.loads(rj.read_text()).get("run_id") == run_id:
                return rd
        except Exception:
            continue
    return None


# Back-compat internal alias (callers predate the public name).
_find_run_dir = find_run_dir


def resolve_run_file(run_dir: Path, rel_path: str) -> Path | None:
    """Resolve a run-dir-relative artifact path to an absolute FILE, rejecting any
    escape outside the run dir (``..``/symlink). Returns ``None`` unless the target
    is a regular file strictly under ``run_dir`` — the id-addressed replacement for
    an absolute-path whitelist (plan §3.3, "artifacts addressed by identity")."""
    rd = run_dir.resolve()
    target = (rd / rel_path).resolve()
    if rd not in target.parents:
        return None
    return target if target.is_file() else None


def rename_run(project_id: str | None, run_id: str, label: str) -> dict[str, Any]:
    """Rename a run = edit its ``run.json`` ``label`` (the dir name never moves)."""
    label = (label or "").strip()
    if not label:
        raise ValueError("run label is required")
    rd = _find_run_dir(project_id, run_id)
    if rd is None:
        raise FileNotFoundError(f"run '{run_id}' not found")
    rj = rd / "run.json"
    d = json.loads(rj.read_text())
    d["label"] = label
    rj.write_text(json.dumps(d, indent=2))
    from spicexplorer_api.services import index_db
    index_db.notify_runs_changed(project_id)
    return d


def delete_run(project_id: str | None, run_id: str) -> str:
    """MOVE a single run dir into ``trash_root()`` (recoverable). Returns the trash id."""
    rd = _find_run_dir(project_id, run_id)
    if rd is None:
        raise FileNotFoundError(f"run '{run_id}' not found")
    _assert_under_work_root(rd)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Use the FULL run_id plus a random suffix: a truncated id + whole-second timestamp
    # could collide (two runs sharing an 8-hex prefix deleted in the same second), and
    # shutil.move would then nest one inside the other and clobber its sidecar (silent loss).
    trash_id = f"run__{run_id}__{ts}_{uuid.uuid4().hex[:6]}"
    dst = trash_root() / trash_id
    _assert_under_work_root(dst)
    meta = {
        "trash_id": trash_id, "kind": "run", "project_id": project_id or "",
        "run_id": run_id, "name": rd.name,
        "deleted": datetime.now().isoformat(timespec="seconds"),
    }
    shutil.move(str(rd), str(dst))
    (dst / ".trashmeta.json").write_text(json.dumps(meta, indent=2))
    from spicexplorer_api.services import index_db
    index_db.notify_runs_changed(project_id)
    return trash_id
