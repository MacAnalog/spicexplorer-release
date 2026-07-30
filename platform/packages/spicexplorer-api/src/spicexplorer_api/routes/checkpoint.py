"""Checkpoint listing and loading routes."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from spicexplorer_api.app_config import (
    REPO_ROOT,
    auto_save_root,
    preset_checkpoint_paths,
    projects_root,
    runs_root,
    work_root,
)
from spicexplorer_api.services.checkpoint_reader import (
    compute_envelope,
    compute_scatter,
    read_checkpoint,
)

router = APIRouter()

_YAML_SUFFIXES = {".yaml", ".yml"}
_CKPT_SUFFIXES = {".json", ".csv"}
_UPLOAD_PREFIX = "spx_uploaded_"  # NamedTemporaryFile prefix used by routes/project.py


# --- Response models (see src/types/README.md) -------------------------------
class CheckpointMeta(BaseModel):
    id: str
    label: str
    path: str
    type: str          # "csv" | "json"
    score_fn: str
    n_iters: int | None  # always present (cheap trial count), null on a read error
    source: str          # "preset" | "autosave"


class ListCheckpointsResponse(BaseModel):
    checkpoints: list[CheckpointMeta]


class CheckpointData(BaseModel):
    id: str
    label: str
    type: str
    score_fn: str
    scores: list[float | None]
    best_scores: list[float | None]
    iterations: list[int]
    per_metric: dict[str, list[float | None]]
    params: dict[str, list[float | None]]
    n_iters: int


class DeleteCheckpointResponse(BaseModel):
    ok: bool
    deleted: list[str]


class EnvelopeEntry(BaseModel):
    metric: str
    best_ever: float
    target: float | None
    goal: str
    passes: bool | None


class CheckpointEnvelopeResponse(BaseModel):
    envelope: list[EnvelopeEntry]


class ScatterPoint(BaseModel):
    x: float
    y: float
    feasible: bool
    score: float | None
    iter: int


class CheckpointScatterResponse(BaseModel):
    metric_x: str
    metric_y: str
    points: list[ScatterPoint]


def _validated_yaml_path(yaml_path: str) -> Path | None:
    """Resolve a caller-supplied ``yaml_path`` to a safe, real file — or ``None``.

    Guards the arbitrary-file-read surface (BUG-B2): a ``yaml_path`` is honored only when it
    (a) has a ``.yaml``/``.yml`` suffix and (b) resolves under an allowed root. The roots are
    deliberately NARROW so this can't leak unrelated repo files (``.env`` has no .yaml suffix,
    but ``compose.yaml`` / ``.github/*.yml`` / ``.venv/**`` would be under a bare REPO_ROOT):

      - ``REPO_ROOT/examples`` — the read-only example projects (the default project lives here);
      - ``work_root()``        — encapsulated projects' ``project.yaml`` under WORK_ROOT;
      - the temp dir, but ONLY files named ``spx_uploaded_*`` — where edited/uploaded YAML lands
        (so a stray ``.yaml`` another tenant drops in a shared ``/tmp`` isn't disclosable).

    ``resolve()`` runs before the containment check, so a ``.yaml`` symlink pointing at
    ``/etc/passwd`` is rejected (the symlink TARGET is what's checked). Returns ``None`` for an
    empty / wrong-suffix / out-of-bounds path (callers decide 400 vs silent skip)."""
    if not yaml_path:
        return None
    p = Path(yaml_path)
    if p.suffix.lower() not in _YAML_SUFFIXES:
        return None
    try:
        rp = p.resolve()
    except (ValueError, OSError):
        return None  # e.g. embedded NUL byte → ValueError; don't 500
    import tempfile
    allowed: list[tuple[Path, str | None]] = [
        ((REPO_ROOT / "examples").resolve(), None),
        (work_root().resolve(), None),
    ]
    try:
        allowed.append((Path(tempfile.gettempdir()).resolve(), _UPLOAD_PREFIX))
    except Exception:
        pass
    for root, name_prefix in allowed:
        try:
            rp.relative_to(root)
        except ValueError:
            continue
        if name_prefix and not rp.name.startswith(name_prefix):
            continue  # under the temp dir but not one of OUR uploads
        return rp
    return None


def require_yaml_under_allowed_root(yaml_path: str) -> Path:
    """Funnel a REQUIRED caller-supplied ``yaml_path`` through the ``_validated_yaml_path``
    choke point, raising ``400`` when it isn't a real ``.yaml``/``.yml`` under an allowed root.

    Any route that loads a project from a caller-controlled path MUST go through this (or
    ``_validated_yaml_path`` directly). ``Project_Setup.from_yaml`` reads the file, so an
    unvalidated path is an arbitrary-file-read + existence-oracle + error-echo surface (BUG-B2):
    a wrong path leaks whether a file exists and pipes its parse errors back to the caller.
    Returns the resolved, in-bounds ``Path`` to load from (canonicalized by ``resolve()``)."""
    safe = _validated_yaml_path(yaml_path)
    if safe is None:
        raise HTTPException(400, "yaml_path must be a .yaml/.yml file under the repo or workspace")
    return safe


def _count_iters(path: Path) -> int | None:
    """Cheap trial count for the catalog listing.

    JSON: length of the top-level ``optimization_log`` array (avoids the
    eval()-based ``Optimization_Log_Visualizer.load_checkpoint``). CSV: data rows
    minus the header. Returns None on any error so the listing never 500s.
    """
    try:
        if path.suffix == ".json":
            import json
            with open(path) as f:
                data = json.load(f)
            return len(data.get("optimization_log", []))
        # CSV: count non-empty data lines after the header.
        with open(path) as f:
            rows = sum(1 for line in f if line.strip())
        return max(0, rows - 1)
    except Exception:
        return None


def _infer_score_fn(path: Path) -> str:
    name = path.name.lower()
    if "sigmoid" in name:
        return "relative-sigmoid"
    if "relabs" in name or "relativeabs" in name or "linear" in name:
        return "relative-absolute"
    return "unknown"


def _target_specs_from_yaml(yaml_path: str) -> list[dict[str, Any]] | None:
    """Load a project's target specs as plain dicts for envelope/scatter feasibility.

    Returns None when no path is given or the project fails to load.
    """
    vp = _validated_yaml_path(yaml_path)
    if vp is None:
        return None
    from spicexplorer.core.domains import Project_Setup
    try:
        project = Project_Setup.from_yaml(vp)
    except Exception:
        return None
    # Only ENABLED specs gate envelope `passes` / scatter feasibility — the optimizer scores only
    # enabled_targets(), so including disabled ones makes the analysis disagree with the run (BUG-B39).
    # tolerance is always > 0 after TargetSpec.__post_init__ (B17), so emit it directly rather than
    # a None that would later crash `target - tol` arithmetic (BUG-B35).
    return [
        {"name": s.name, "target": float(s.target), "goal": s.goal.value,
         "tolerance": float(s.tolerance)}
        for s in project.optimizer_config.target_specs.enabled_targets()
    ]


def _resolve_checkpoint_path(checkpoint_id: str) -> Path | None:
    """Resolve a checkpoint id to a file on disk.

    Tries the configured presets first, then any autosave under ``auto_save/``
    (a live run writes a FINAL .json there). Shared by load/envelope/scatter so
    the analysis views work on *live* results, not just the preset demo data.
    """
    path = preset_checkpoint_paths().get(checkpoint_id)
    if path is not None and path.exists():
        return path
    # Match on EXACT stem, not a `{id}*` prefix glob: a prefix like `..._trial2` would otherwise
    # also match `..._trial2_FINAL`/`..._trial20`/`..._trial200` and resolve the wrong file (BUG-B38).
    for autosave_root in _autosave_roots():
        candidates = sorted(p for p in autosave_root.rglob("*.json") if p.stem == checkpoint_id)
        if candidates:
            return candidates[0]
    return None


def _autosave_roots() -> list[Path]:
    """Dirs where optimizer autosaves can live. ``Base_Optimizer`` writes ``./auto_save``
    relative to the BACKEND's CWD, while the UI historically only searched
    ``REPO_ROOT/auto_save`` — they coincide only when CWD == REPO_ROOT. Search both
    (deduped) so live checkpoints + resume work regardless of where uvicorn was launched
    (BUG-A9 / OPT-3)."""
    return _autosave_roots_for(all_projects=True)


def _autosave_roots_for(project_id: str | None = None, all_projects: bool = False) -> list[Path]:
    """Checkpoint search roots.

    - ``project_id`` (and not ``all_projects``): STRICT — only that project's
      ``runs/<run>/checkpoints``. The caller adds the read-only presets separately, so
      an active project's catalog shows exactly its own runs + presets and never another
      project's (or orphan/legacy) checkpoints.
    - default: the legacy ``auto_save`` dirs + the unscoped ``runs/`` checkpoints (the
      global, project-less view).
    - ``all_projects``: also every project's per-run checkpoints — used to RESOLVE or
      DELETE a checkpoint by id regardless of the active project.
    """
    candidates: list[Path] = []
    if project_id and not all_projects:
        from spicexplorer_api.services import project_service
        try:
            pruns = project_service.project_dir(project_id) / "runs"
            candidates.extend(ck for ck in pruns.rglob("checkpoints") if ck.is_dir())
        except Exception:
            pass
    else:
        candidates = [auto_save_root(), REPO_ROOT / "auto_save", Path.cwd() / "auto_save"]
        candidates.extend(ck for ck in runs_root().rglob("checkpoints") if ck.is_dir())
        if all_projects:
            candidates.extend(ck for ck in projects_root().rglob("checkpoints") if ck.is_dir())
    roots: list[Path] = []
    seen: set[Path] = set()
    for r in candidates:
        rr = r.resolve()
        if rr not in seen and rr.exists():
            seen.add(rr)
            roots.append(rr)
    return roots


def _list_autosave_checkpoints(project_id: str | None = None) -> list[dict[str, Any]]:
    results = []
    seen_ids: set[str] = set()
    for autosave_root in _autosave_roots_for(project_id=project_id):
        for p in sorted(autosave_root.rglob("*.json")):
            if p.stem in seen_ids:  # same checkpoint reachable via two roots
                continue
            seen_ids.add(p.stem)
            results.append({
                "id": p.stem,
                "label": p.stem,
                "path": str(p),
                "type": "json",
                "score_fn": _infer_score_fn(p),
                "n_iters": _count_iters(p),
                "source": "autosave",
            })
    return results


def _example_family(parts: tuple[str, ...]) -> str | None:
    """The example a path belongs to — ``examples/OTA/<topology>/…`` → ``OTA/<topology>``."""
    if "examples" in parts:
        i = parts.index("examples")
        if i + 2 < len(parts):
            return "/".join(parts[i + 1:i + 3])
    return None


def _project_family(project_id: str) -> str | None:
    """The example family a project ultimately derives from, if any.

    A ``copy_example`` project records ``source.ref`` = the example key (``OTA/<topology>/…``).
    A ``fork`` records ``source.ref`` = the PARENT project id, so we walk the fork chain
    (bounded, cycle-guarded) until we reach the example ancestor — otherwise a forked project
    would lose its parent's example presets (the common duplicate-and-tweak case)."""
    from spicexplorer_api.services import project_service
    seen: set[str] = set()
    pid: str | None = project_id
    for _ in range(16):  # bound the walk; cheap manifests, but never loop forever
        if not pid or pid in seen:
            return None
        seen.add(pid)
        source = project_service.read_manifest(pid).get("source") or {}
        kind, ref = source.get("kind"), source.get("ref")
        if kind == "fork" and isinstance(ref, str):
            pid = ref  # follow to the parent project and re-resolve its family
            continue
        if isinstance(ref, str):
            rp = ref.split("/")
            if len(rp) >= 2:
                return "/".join(rp[:2])
        return None
    return None


@router.get("/checkpoint", response_model=ListCheckpointsResponse)
def list_checkpoints(project_id: str = Query(default="")):
    items = []
    # Preset demo checkpoints are EXAMPLE-specific (their metrics/params are that
    # topology). Show them only when no project is active, or when the active project
    # was derived from the SAME example as the preset — so e.g. the cascode presets
    # don't pollute a 5T-OTA project's catalog.
    proj_family = _project_family(project_id) if project_id else None
    for key, path in preset_checkpoint_paths().items():
        if not path.exists():
            continue
        if project_id and _example_family(path.parts) != proj_family:
            continue
        items.append({
            "id": key,
            "label": key.replace("_", " ").title(),
            "path": str(path),
            "type": "csv" if path.suffix == ".csv" else "json",
            "score_fn": _infer_score_fn(path),
            "n_iters": _count_iters(path),
            "source": "preset",
        })
    items += _list_autosave_checkpoints(project_id=project_id or None)
    return {"checkpoints": items}


@router.get("/checkpoint/{checkpoint_id}", response_model=CheckpointData)
def load_checkpoint(checkpoint_id: str, limit: int = Query(default=0)):
    path = _resolve_checkpoint_path(checkpoint_id)
    if path is None:
        raise HTTPException(404, f"Checkpoint '{checkpoint_id}' not found")

    data = read_checkpoint(path, limit=limit if limit > 0 else None)
    data["id"] = checkpoint_id
    data["label"] = checkpoint_id.replace("_", " ").title()
    data["type"] = "csv" if path.suffix == ".csv" else "json"
    data["score_fn"] = _infer_score_fn(path)
    return data


@router.delete("/checkpoint/{checkpoint_id}", response_model=DeleteCheckpointResponse)
def delete_checkpoint(
    checkpoint_id: str,
    project_id: str = Query(default=""),
    path: str = Query(default=""),
):
    """Delete an autosave checkpoint. Preset checkpoints are protected.

    A checkpoint stem carries no project/run id, so copied/forked projects — and even two RUNS
    of one project with the same algorithm+budget — produce identically-named stems, and the
    catalog dedups them to a single row (BUG-B3). Deleting by bare stem is therefore ambiguous
    and can silently unlink a same-named checkpoint the user never targeted, across projects OR
    across runs. To delete exactly the file behind a catalog row, the UI passes its resolved
    ``path``; we then delete only that file (after confirming it is a real checkpoint under an
    autosave root, not a preset). When no ``path`` is given (legacy delete-by-id), a single
    unambiguous match is deleted, but a multi-file match is REFUSED with 409 — the caller must
    disambiguate with ``path``. ``project_id`` still scopes the search to that project's runs.
    """
    presets = preset_checkpoint_paths()
    if checkpoint_id in presets:
        raise HTTPException(
            403,
            f"Checkpoint '{checkpoint_id}' is a preset and cannot be deleted from the UI.",
        )

    roots = _autosave_roots_for(project_id=project_id or None, all_projects=not project_id)
    if not roots:
        raise HTTPException(404, "No autosave directory.")
    resolved_roots = [r.resolve() for r in roots]
    preset_paths = {p.resolve() for p in presets.values()}

    def _under_autosave(p: Path) -> bool:
        parents = p.parents
        return any(root in parents for root in resolved_roots)

    # Precise delete: the UI supplies the exact file path behind the (deduped) catalog row, so
    # we remove only that one file — no stem-based fan-out across runs/projects.
    if path:
        target = Path(path).resolve()
        if target in preset_paths:
            raise HTTPException(403, "Refusing to delete a preset checkpoint.")
        if not (target.is_file() and target.suffix.lower() in _CKPT_SUFFIXES):
            raise HTTPException(404, f"Checkpoint file not found: {path}")
        if target.stem != checkpoint_id:
            raise HTTPException(400, "path does not match checkpoint id")
        if not _under_autosave(target):
            raise HTTPException(403, f"Refusing to delete file outside auto_save: {path}")
        target.unlink()
        return {"ok": True, "deleted": [str(target)]}

    # Legacy delete-by-stem. Restrict to checkpoint suffixes so a same-stemmed sidecar can't
    # inflate the count into a spurious 409 (or get caught in the fan-out).
    candidates = [
        p
        for root in roots
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in _CKPT_SUFFIXES and p.stem == checkpoint_id
    ]
    if not candidates:
        raise HTTPException(404, f"Checkpoint '{checkpoint_id}' not found in auto_save.")
    if len(candidates) > 1:
        raise HTTPException(
            409,
            f"'{checkpoint_id}' matches {len(candidates)} checkpoint files (across "
            f"projects/runs); pass the exact ?path= to delete a specific one.",
        )

    target = candidates[0]
    if not _under_autosave(target.resolve()):
        raise HTTPException(403, f"Refusing to delete file outside auto_save: {target}")
    target.unlink()
    return {"ok": True, "deleted": [str(target)]}


@router.get("/checkpoint/{checkpoint_id}/envelope", response_model=CheckpointEnvelopeResponse)
def checkpoint_envelope(checkpoint_id: str, yaml_path: str = Query(default="")):
    path = _resolve_checkpoint_path(checkpoint_id)
    if path is None:
        raise HTTPException(404, f"Checkpoint '{checkpoint_id}' not found")

    data = read_checkpoint(path)
    target_specs = _target_specs_from_yaml(yaml_path)
    return {"envelope": compute_envelope(data, target_specs)}


@router.get("/checkpoint/{checkpoint_id}/scatter", response_model=CheckpointScatterResponse)
def checkpoint_scatter(
    checkpoint_id: str,
    metric_x: str = Query(...),
    metric_y: str = Query(...),
    yaml_path: str = Query(default=""),
):
    path = _resolve_checkpoint_path(checkpoint_id)
    if path is None:
        raise HTTPException(404, f"Checkpoint '{checkpoint_id}' not found")

    data = read_checkpoint(path)
    target_specs = _target_specs_from_yaml(yaml_path)
    points = compute_scatter(data, metric_x, metric_y, target_specs)
    return {"metric_x": metric_x, "metric_y": metric_y, "points": points}


@router.get("/checkpoint/{checkpoint_id}/report")
def checkpoint_report(checkpoint_id: str, yaml_path: str = Query(default="")):
    """Bundle a run's artifacts into one downloadable zip: the checkpoint file, the
    project YAML (when a path is given), and a generated `summary.md` (final best
    score + the performance envelope per spec)."""
    import io
    import zipfile

    from fastapi.responses import StreamingResponse

    path = _resolve_checkpoint_path(checkpoint_id)
    if path is None:
        raise HTTPException(404, f"Checkpoint '{checkpoint_id}' not found")

    # Reject a yaml_path that isn't a real .yaml/.yml under an allowed root BEFORE reading it
    # into the zip — this route returns file CONTENTS, so an unvalidated path is arbitrary
    # file disclosure (BUG-B2). An empty yaml_path is fine (the YAML is just omitted).
    safe_yaml = _validated_yaml_path(yaml_path)
    if yaml_path and safe_yaml is None:
        raise HTTPException(400, "yaml_path must be a .yaml/.yml file under the repo or workspace")

    data = read_checkpoint(path)
    target_specs = _target_specs_from_yaml(yaml_path)
    envelope = compute_envelope(data, target_specs) if target_specs else []

    best_scores = [s for s in data.get("best_scores", []) if isinstance(s, (int, float))]
    final_best = best_scores[-1] if best_scores else None

    lines = [
        f"# Run report — {checkpoint_id}",
        "",
        f"- Score function: `{_infer_score_fn(path)}`",
        f"- Iterations: {data.get('n_iters', '?')}",
        f"- Final best score: {final_best if final_best is not None else 'n/a'}",
        "",
        "## Performance envelope (best per spec)",
        "",
        "| spec | goal | best | target | pass |",
        "|---|---|---|---|---|",
    ]
    for e in envelope:
        passes = e.get("passes")
        mark = "PASS" if passes else ("FAIL" if passes is False else "—")
        lines.append(
            f"| {e['metric']} | {e.get('goal', '')} | {e.get('best_ever')} | "
            f"{e.get('target')} | {mark} |"
        )
    summary_md = "\n".join(lines) + "\n"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(path.name, path.read_text())
        if safe_yaml is not None and safe_yaml.exists() and safe_yaml.is_file():
            z.writestr("project_setup.yaml", safe_yaml.read_text())
        z.writestr("summary.md", summary_md)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{checkpoint_id}-report.zip"'},
    )
