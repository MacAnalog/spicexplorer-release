"""Waveview service — open-dataset registry + path whitelist for /api/waveview.

Datasets are loaded once (``spicexplorer_waveview.load_result``) and held in an
in-process LRU registry keyed by a content id (path + mtime), so wave/measure requests
re-read nothing from disk. Path access follows the xschem routes' whitelist posture:
absolute paths only, resolved under an allowed root — ``REPO_ROOT``, ``work_root()``,
plus any roots in the ``SPICEXPLORER_WAVEVIEW_ROOTS`` env var (``:``-separated), which
is the explicit opt-in for viewing artifacts that live outside the repo (e.g. a
Spectre work dir on the research server).
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Any, Literal

from fastapi import HTTPException
from spicexplorer_waveview import WaveDataset, load_result, merge_datasets
from spicexplorer_waveview.loaders import sniff_engine
from spicexplorer_waveview.spectre_loader import SWEEP_EXT_TO_ANALYSIS

from spicexplorer_api.app_config import REPO_ROOT, work_root
from spicexplorer_api.services import project_service

_MAX_OPEN_DATASETS = 32  # LRU-evicted beyond this (bounds resident numpy memory)

_lock = threading.Lock()
_datasets: dict[str, "OpenDataset"] = {}


@dataclass
class OpenDataset:
    """One loaded artifact in the registry."""

    dataset_id: str
    dataset: WaveDataset
    opened_at: float
    last_used: float


def allowed_roots() -> list[Path]:
    """Whitelist for absolute-path access (mirrors the xschem routes' posture)."""
    roots = [REPO_ROOT, work_root()]
    extra = os.environ.get("SPICEXPLORER_WAVEVIEW_ROOTS", "")
    for part in extra.split(":"):
        if part.strip():
            roots.append(Path(part.strip()).expanduser())
    return [p.resolve() for p in roots]


def validate_under_allowed(path: str | Path) -> Path:
    """Resolve ``path`` and require it under an allowed root (403 otherwise, 400 if relative)."""
    p = Path(path)
    if not p.is_absolute():
        raise HTTPException(400, "Path must be absolute")
    resolved = p.resolve()
    for root in allowed_roots():
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue
    raise HTTPException(
        403,
        f"Path outside allowed roots: {p} (extend SPICEXPLORER_WAVEVIEW_ROOTS to opt in)",
    )


def _dataset_id(path: Path) -> str:
    """Content-keyed id: same path re-simulated (new mtime) → a new id, no stale reads."""
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        mtime = 0
    return hashlib.sha1(f"{path}:{mtime}".encode()).hexdigest()[:12]


def open_dataset(
    path: str, engine: str | None = None, log_path: str | None = None
) -> OpenDataset:
    """Load (or return the already-loaded) dataset for an artifact path."""
    resolved = validate_under_allowed(path)
    if not resolved.exists():
        raise HTTPException(404, f"Result artifact not found: {resolved}")
    if log_path is not None:
        log_resolved = validate_under_allowed(log_path)
        if not log_resolved.is_file():
            raise HTTPException(404, f"Log file not found: {log_resolved}")
        log_path = str(log_resolved)

    dataset_id = _dataset_id(resolved)
    with _lock:
        entry = _datasets.get(dataset_id)
        if entry is not None:
            entry.last_used = time()
            return entry

    try:
        ds = load_result(resolved, engine=engine, log_path=log_path)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — surface parse failures as a clean 422
        raise HTTPException(422, f"Failed to load result artifact: {exc}") from exc

    # A discovered (not explicitly passed) log must also be servable → drop it if it
    # falls outside the whitelist (it can't: discovery stays beside the artifact — but
    # keep the invariant explicit).
    if ds.log_path is not None:
        try:
            validate_under_allowed(ds.log_path)
        except HTTPException:
            ds.warnings.append(f"discovered log outside allowed roots (dropped): {ds.log_path}")
            ds.log_path = None

    entry = OpenDataset(dataset_id=dataset_id, dataset=ds, opened_at=time(), last_used=time())
    with _lock:
        _datasets[dataset_id] = entry
        while len(_datasets) > _MAX_OPEN_DATASETS:  # LRU evict
            oldest = min(_datasets.values(), key=lambda e: e.last_used)
            del _datasets[oldest.dataset_id]
    return entry


def get_dataset(dataset_id: str) -> OpenDataset:
    with _lock:
        entry = _datasets.get(dataset_id)
        if entry is None:
            raise HTTPException(404, f"No open dataset {dataset_id!r} (open it via POST /waveview/open)")
        entry.last_used = time()
        return entry


def list_datasets() -> list[OpenDataset]:
    with _lock:
        return sorted(_datasets.values(), key=lambda e: e.opened_at)


def close_dataset(dataset_id: str) -> bool:
    with _lock:
        return _datasets.pop(dataset_id, None) is not None


def open_dataset_ids_under(root: Path) -> list[str]:
    """Ids of open datasets whose source artifact lives under ``root`` (read-only)."""
    rr = root.resolve()
    with _lock:
        return [
            did for did, e in _datasets.items()
            if rr == Path(e.dataset.source).resolve()
            or rr in Path(e.dataset.source).resolve().parents
        ]


def close_datasets_under(root: Path) -> int:
    """Evict every open dataset whose source artifact lives under ``root``.

    Called after an on-disk delete (run prune, upload removal) so the registry
    never serves a dataset whose backing files are gone — the arrays would still
    read (they are resident), but the attached log and any re-open would 404
    confusingly. Returns the number of datasets closed."""
    rr = root.resolve()
    with _lock:
        doomed = [
            did for did, e in _datasets.items()
            if rr == Path(e.dataset.source).resolve()
            or rr in Path(e.dataset.source).resolve().parents
        ]
        for did in doomed:
            del _datasets[did]
    return len(doomed)


ArtifactKind = Literal["dir", "ngspice_raw", "spectre_raw_dir", "log"]


def classify_artifact(p: Path) -> ArtifactKind | None:
    """Viewer-openable kind of a path: ``dir`` / ``ngspice_raw`` / ``spectre_raw_dir`` /
    ``log`` / None (not a result artifact). Shared by /waveview/browse and the run-artifact
    walker so both surfaces agree on what "an artifact" is."""
    if p.is_dir():
        try:
            for f in p.iterdir():
                if f.is_file() and not f.name.endswith(".cache") and any(
                    f.name.lower().endswith(ext) for ext in SWEEP_EXT_TO_ANALYSIS
                ):
                    return "spectre_raw_dir"
        except OSError:
            return None
        return "dir"
    if sniff_engine(p) == "ngspice":
        return "ngspice_raw"
    if p.suffix.lower() in (".log", ".out"):
        return "log"
    return None


# ---------- open-by-run-id (optimizer run artifacts) ----------
#
# Disk is the source of truth: every live/resumed optimizer run leaves a self-contained
# run dir (``run.json`` + ``run.log`` + ``sim/…``) under a project's ``runs/`` or the
# unscoped ``work_root()/runs`` — see ``optimizer_runner._run_live``. Resolving from those
# ``run.json`` files (not the runner's in-memory registry) means run ids stay openable
# after the run finishes and across backend restarts.

_ARTIFACT_SCAN_CAP = 10_000  # directory entries examined per run dir (runaway guard)


def list_runs(project_id: str | None = None) -> list[dict[str, Any]]:
    """Known optimizer runs (their ``run.json`` contents + ``run_dir``), newest first.

    ``project_id`` scopes to one project; default = all projects plus unscoped runs.
    """
    if project_id is not None and not project_service.project_exists(project_id):
        raise HTTPException(404, f"project {project_id!r} not found")
    scopes: list[str | None] = (
        [project_id] if project_id is not None
        else [None, *(p["id"] for p in project_service.list_projects())]
    )
    out: list[dict[str, Any]] = []
    for pid in scopes:
        for rd in project_service.runs_dir(pid).glob("*"):
            rj = rd / "run.json"
            if not rj.is_file():
                continue
            try:
                info = json.loads(rj.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(info, dict):
                out.append({**info, "run_dir": str(rd)})
    out.sort(key=lambda r: str(r.get("started") or ""), reverse=True)
    return out


def find_run(run_id: str, project_id: str | None = None) -> dict[str, Any]:
    """Resolve a run by its full ``run_id`` (or its run-dir name) to its run.json + dir.

    Uses ``project_service.find_run_dir`` (dir == run_id fast path; legacy dirs fall
    back to a run.json scan), so a single-run lookup no longer reads every run.json.
    """
    if project_id is not None and not project_service.project_exists(project_id):
        raise HTTPException(404, f"project {project_id!r} not found")
    scopes: list[str | None] = (
        [project_id] if project_id is not None
        else [None, *(p["id"] for p in project_service.list_projects())]
    )
    for pid in scopes:
        rd = project_service.find_run_dir(pid, run_id)
        if rd is not None:
            try:
                info = json.loads((rd / "run.json").read_text())
            except (OSError, json.JSONDecodeError):
                info = {}
            if isinstance(info, dict):
                return {**info, "run_dir": str(rd)}
    raise HTTPException(404, f"No run {run_id!r}"
                             + (f" in project {project_id!r}" if project_id else ""))


def list_run_artifacts(run_dir: Path) -> list[dict[str, Any]]:
    """Openable result artifacts under a run dir (recursive), newest-modified first.

    Walks the run's own tree only (``sim/`` trial folders, ``run.log``, persisted Spectre
    raw dirs); Spectre raw dirs are terminal — their member PSFs are one dataset, not
    individual artifacts. Plain files that classify as nothing (netlists, checkpoints,
    ``events.ndjson``) are skipped.
    """
    artifacts: list[dict[str, Any]] = []
    stack = [run_dir]
    examined = 0
    while stack:
        d = stack.pop()
        try:
            children = sorted(d.iterdir())
        except OSError:
            continue
        for child in children:
            if child.name.startswith("."):
                continue
            examined += 1
            if examined > _ARTIFACT_SCAN_CAP:
                return sorted(artifacts, key=lambda a: a["mtime"], reverse=True)
            kind = classify_artifact(child)
            if kind == "dir":
                stack.append(child)
                continue
            if kind is None:
                continue
            try:
                st = child.stat()
            except OSError:
                continue
            artifacts.append({
                "name": child.relative_to(run_dir).as_posix(),
                "path": str(child),
                "type": kind,
                "mtime": st.st_mtime,
                "size": st.st_size if child.is_file() else None,
            })
    artifacts.sort(key=lambda a: a["mtime"], reverse=True)
    return artifacts


def open_run_merged(run_dir: Path, artifacts: list[dict[str, Any]]) -> OpenDataset:
    """Open several of a run's raw artifacts as ONE merged multi-analysis dataset.

    Each member loads through :func:`open_dataset` (idempotent, whitelisted), so
    the merged entry shares their numpy arrays — no copies. The merged id is
    content-keyed off the member ids (path+mtime each): a re-simulated artifact
    yields a new merged id, same as single-artifact opens. The run's own
    ``run.log`` (when present) becomes the merged dataset's log; member labels
    are the artifact's run-dir-relative parent (the trial/testbench folder), so
    provenance shows up in each analysis' ``native_name``.
    """
    if not artifacts:
        raise HTTPException(404, "No artifacts to merge")
    # The merged id is derivable from paths+mtimes alone — check the cache BEFORE
    # loading any member, so a cached merged open re-reads nothing.
    member_ids = [_dataset_id(validate_under_allowed(a["path"])) for a in artifacts]
    merged_id = hashlib.sha1(("merge:" + "|".join(member_ids)).encode()).hexdigest()[:12]
    with _lock:
        entry = _datasets.get(merged_id)
        if entry is not None:
            entry.last_used = time()
            return entry
        # Members already open BEFORE this merge were opened deliberately (or by
        # another merge) and must stay registered; ones loaded just for this
        # merge get unregistered below — a merged open lists as ONE dataset,
        # not 1 + N per-testbench parts.
        preexisting = set(_datasets.keys())

    members: list[tuple[str, OpenDataset]] = []
    for a in artifacts:
        rel_parent = Path(a["name"]).parent.as_posix()
        label = "" if rel_parent == "." else rel_parent
        members.append((label, open_dataset(a["path"])))

    run_log = run_dir / "run.log"
    log_path: str | None = None
    if run_log.is_file():
        try:
            log_path = str(validate_under_allowed(run_log))
        except HTTPException:
            log_path = None
    ds = merge_datasets(
        [(label, e.dataset) for label, e in members],
        source=str(run_dir),
        log_path=log_path,
    )
    if log_path is None and ds.log_path is not None:
        # merge_datasets falls back to the first member's discovered log — keep the
        # same whitelist invariant open_dataset enforces on discovered logs.
        try:
            validate_under_allowed(ds.log_path)
        except HTTPException:
            ds.log_path = None
    entry = OpenDataset(dataset_id=merged_id, dataset=ds, opened_at=time(), last_used=time())
    with _lock:
        # Unregister members this merge loaded itself (the merged WaveDataset
        # keeps their arrays alive — shared, not copied).
        for _label, member in members:
            if member.dataset_id not in preexisting:
                _datasets.pop(member.dataset_id, None)
        _datasets[merged_id] = entry
        while len(_datasets) > _MAX_OPEN_DATASETS:  # LRU evict
            oldest = min(_datasets.values(), key=lambda e: e.last_used)
            del _datasets[oldest.dataset_id]
    return entry


def dataset_meta(entry: OpenDataset) -> dict[str, Any]:
    """The JSON-facing summary of an open dataset (no waveform payloads)."""
    ds = entry.dataset
    analyses = []
    for key, an in ds.analyses.items():
        analyses.append(
            {
                "analysis": key,
                "native_name": an.native_name,
                "sweep": an.sweep,
                "n_points": an.n_points,
                "signals": [
                    {
                        "name": s.name,
                        "units": s.units,
                        "complex": s.is_complex,
                        "n_points": s.n_points,
                    }
                    for s in an.signals.values()
                ],
                "n_scalars": len(an.scalars),
            }
        )
    return {
        "dataset_id": entry.dataset_id,
        "path": ds.source,
        "engine": ds.engine,
        "analyses": analyses,
        "log_path": ds.log_path,
        "warnings": ds.warnings,
    }
