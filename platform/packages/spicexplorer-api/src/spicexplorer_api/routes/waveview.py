"""Universal simulation-result viewer routes — /api/waveview/*.

The REST surface over ``spicexplorer_waveview``: open any ngspice ``.raw`` file or
Spectre psfascii raw dir (path-whitelisted), list its analyses/signals, fetch
display-ready (optionally downsampled) waveform data, evaluate any Tier-1 measurement
recipe against it, and read or live-tail (SSE) the simulator log.

Design notes:

* Waveform JSON is per-signal ``{x: [...], y: [...]}`` (or ``y_re``/``y_im`` for
  ``fmt=complex``) — non-finite floats serialize as ``null`` (strict-JSON safe).
* Downsampling picks indices on the display-transformed trace, so a min/max envelope
  or LTTB selection reflects what the user actually sees.
* The SSE log tail polls the file by byte offset (like ``tail -f``), classifying each
  new line's severity server-side — usable both for a finished run's log and for a log
  that is still being written by a live simulation.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
from pathlib import Path
from typing import Any, Literal

import numpy as np
from fastapi import APIRouter, Body, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from spicexplorer_core.atomic_io import atomic_write_bytes
from spicexplorer_waveview import (
    downsample_indices,
    measure_dataset,
    measurement_catalog,
    parse_log_text,
    parse_sim_log,
)
from spicexplorer_waveview.plotting import format_y

from spicexplorer_api.app_config import work_root
from spicexplorer_api.services import project_service
from spicexplorer_api.services import waveview_service as svc

router = APIRouter()


# --- Response/request models --------------------------------------------------
class SignalMeta(BaseModel):
    name: str
    units: str | None
    complex: bool
    n_points: int


class AnalysisMeta(BaseModel):
    analysis: str
    native_name: str
    sweep: str | None
    n_points: int
    signals: list[SignalMeta]
    n_scalars: int


class DatasetMeta(BaseModel):
    dataset_id: str
    path: str
    engine: str
    analyses: list[AnalysisMeta]
    log_path: str | None
    warnings: list[str]


class DatasetListResponse(BaseModel):
    datasets: list[DatasetMeta]


class DatasetClosedResponse(BaseModel):
    closed: bool


class OpenRequest(BaseModel):
    path: str = Field(..., description="Absolute path: an ngspice .raw file or a Spectre psfascii raw dir")
    engine: Literal["ngspice", "spectre"] | None = Field(
        None, description="Force the engine; default sniffs from the artifact"
    )
    log_path: str | None = Field(None, description="Absolute path of the simulator log to attach")


class WaveSignalData(BaseModel):
    name: str
    x: list[float | None]
    y: list[float | None] | None = None
    y_re: list[float | None] | None = None
    y_im: list[float | None] | None = None
    n_total: int
    n_returned: int
    downsampled: bool


class WaveResponse(BaseModel):
    dataset_id: str
    analysis: str
    x_name: str | None
    fmt: str
    signals: list[WaveSignalData]


class MeasureItem(BaseModel):
    name: str | None = Field(None, description="Label for this measurement (defaults to the meas name)")
    recipe: dict[str, Any] = Field(..., description="A Tier-1 {meas: ...} registry recipe")


class MeasureRequest(BaseModel):
    items: list[MeasureItem]


class MeasureResult(BaseModel):
    name: str
    value: float | None
    error: str | None


class MeasureResponse(BaseModel):
    dataset_id: str
    results: list[MeasureResult]


class MeasurementInfo(BaseModel):
    kind: str
    required: list[str]
    default_analysis: str


class MeasurementCatalogResponse(BaseModel):
    measurements: dict[str, MeasurementInfo]


class ScalarsResponse(BaseModel):
    dataset_id: str
    analysis: str
    scalars: dict[str, float | None]


class LogLineModel(BaseModel):
    no: int
    level: str
    text: str


class LogResponse(BaseModel):
    dataset_id: str | None
    path: str | None
    counts: dict[str, int]
    n_lines: int
    lines: list[LogLineModel]


class BrowseEntry(BaseModel):
    name: str
    path: str
    type: Literal["dir", "ngspice_raw", "spectre_raw_dir", "log"]


class BrowseResponse(BaseModel):
    dir: str
    # The directory to navigate "up" to — null when dir is already at (or its parent
    # falls outside) the allowed roots, so clients need no path arithmetic of their own.
    parent: str | None = None
    entries: list[BrowseEntry]


class UploadResponse(BaseModel):
    upload_id: str
    staged_path: str
    kind: Literal["ngspice_raw", "spectre_raw_dir", "log"]
    # Auto-opened for raw artifacts (the point of uploading); null for a bare log.
    dataset: DatasetMeta | None = None


class UploadEntry(BaseModel):
    upload_id: str
    staged_path: str
    mtime: float
    size_bytes: int
    n_files: int
    open_dataset_ids: list[str] = Field(
        default_factory=list, description="Open viewer datasets backed by this staging dir"
    )


class UploadListResponse(BaseModel):
    uploads: list[UploadEntry]


class UploadDeletedResponse(BaseModel):
    deleted: bool
    closed_datasets: int = 0


class RunInfo(BaseModel):
    run_id: str
    run_dir: str
    project_id: str | None = None
    label: str | None = None
    kind: str | None = None
    algorithm: str | None = None
    status: str | None = None
    started: str | None = None
    ended: str | None = None
    best_score: float | None = None
    budget: int | None = None
    active_corner: str | None = None
    keep_raw: bool | None = None
    retention: str | None = None
    # The GC's idempotency marker ({tier, at, freed_bytes}) — present once a run's
    # heavy artifacts were pruned, so clients can gray out the keep_raw badge.
    retention_pruned: dict[str, Any] | None = None


class RunListResponse(BaseModel):
    runs: list[RunInfo]


class RunArtifact(BaseModel):
    name: str = Field(..., description="Path relative to the run dir (e.g. sim/run_3_tb_ac__tt/tb_ac.raw)")
    path: str
    type: Literal["ngspice_raw", "spectre_raw_dir", "log"]
    mtime: float
    size: int | None


class RunArtifactsResponse(BaseModel):
    run_id: str
    run_dir: str
    artifacts: list[RunArtifact]


class OpenRunRequest(BaseModel):
    run_id: str = Field(..., description="A run's full run_id (or its run-dir name)")
    project_id: str | None = Field(None, description="Scope the lookup to one project (default: all)")
    match: str | None = Field(
        None,
        description="Substring filter on the artifact's run-dir-relative path — "
                    "e.g. a testbench or corner name like 'tb_ac' or '__ss'",
    )
    merge: bool = Field(
        False,
        description="Open the newest raw artifacts (up to `limit`) as ONE merged "
                    "multi-analysis dataset — ac+tran+noise testbench raws become one "
                    "viewer entry. Duplicate analysis keys get a '#2'/'#3' suffix.",
    )
    limit: int = Field(
        8, ge=1, le=32,
        description="With merge: how many of the newest matching artifacts to combine "
                    "(a big keep_raw run can hold hundreds of per-trial raws).",
    )


class RunPruneResponse(BaseModel):
    run_id: str
    tier: str | None = Field(None, description="The retention tier that was enforced")
    pruned: bool
    skipped: str | None = Field(None, description="Why nothing was pruned (running/already applied)")
    removed: list[str] = Field(default_factory=list, description="Run-dir children removed")
    freed_bytes: int = 0
    dry_run: bool = False
    closed_datasets: int = Field(0, description="Open viewer datasets evicted because their files went away")


# --- helpers -------------------------------------------------------------------
def _json_floats(arr: np.ndarray) -> list[float | None]:
    """numpy → JSON-safe list (NaN/±inf → null; strict parsers stay happy)."""
    a = np.asarray(arr, dtype=float)
    finite = np.isfinite(a)
    return [float(v) if ok else None for v, ok in zip(a, finite)]


# --- routes ---------------------------------------------------------------------
@router.get("/waveview/measurements", response_model=MeasurementCatalogResponse)
def get_measurement_catalog():
    """Every Tier-1 measurement the viewer can evaluate: kind, required args, default analysis."""
    return {"measurements": measurement_catalog()}


@router.post("/waveview/open", response_model=DatasetMeta)
def open_dataset(req: OpenRequest = Body(...)):
    """Open a result artifact (idempotent: same path+mtime returns the same dataset_id)."""
    entry = svc.open_dataset(req.path, engine=req.engine, log_path=req.log_path)
    return svc.dataset_meta(entry)


@router.get("/waveview/datasets", response_model=DatasetListResponse)
def get_datasets():
    """All open datasets (oldest first)."""
    return {"datasets": [svc.dataset_meta(e) for e in svc.list_datasets()]}


@router.get("/waveview/datasets/{dataset_id}", response_model=DatasetMeta)
def get_dataset(dataset_id: str):
    return svc.dataset_meta(svc.get_dataset(dataset_id))


@router.delete("/waveview/datasets/{dataset_id}", response_model=DatasetClosedResponse)
def close_dataset(dataset_id: str):
    """Drop a dataset from the registry (its arrays are freed)."""
    return {"closed": svc.close_dataset(dataset_id)}


@router.get("/waveview/datasets/{dataset_id}/wave", response_model=WaveResponse)
def get_wave(
    dataset_id: str,
    analysis: str = Query(..., description="Engine-neutral analysis key (ac/tran/dc/noise/pss/stb/…)"),
    signals: str = Query(..., description="Comma-separated signal names"),
    x: str | None = Query(None, description="Abscissa signal (default: the analysis sweep)"),
    fmt: str = Query("auto", description="auto|mag_db|mag|phase_deg|re|im|complex"),
    max_points: int = Query(4000, ge=16, le=200_000, description="Display point budget per signal"),
    method: str = Query("minmax", description="Downsample method: minmax|lttb|stride|none"),
):
    """Display-ready waveform data for one or more signals of an analysis."""
    entry = svc.get_dataset(dataset_id)
    ds = entry.dataset
    an = ds.resolve_analysis(analysis)
    if an is None:
        raise HTTPException(404, f"No analysis {analysis!r} in dataset (have {sorted(ds.analyses)})")

    if method == "none" and an.n_points > max_points:
        raise HTTPException(
            422,
            f"analysis has {an.n_points} points > max_points={max_points} and method=none "
            f"disables downsampling — raise max_points (cap 200000) or pick minmax|lttb|stride",
        )
    x_name = x or an.sweep
    x_data: np.ndarray | None = None
    if x_name is not None:
        x_sig = ds.find_signal(analysis, x_name)
        if x_sig is None:
            raise HTTPException(404, f"No x signal {x_name!r} in analysis {analysis!r}")
        x_data = np.real(np.asarray(x_sig.data)).astype(float)

    out: list[WaveSignalData] = []
    for name in [s.strip() for s in signals.split(",") if s.strip()]:
        sig = ds.find_signal(analysis, name)
        if sig is None:
            raise HTTPException(
                404, f"No signal {name!r} in analysis {analysis!r} (have {sorted(an.signals)})"
            )
        arr = np.asarray(sig.data)
        n_total = int(arr.size)
        xa = x_data if x_data is not None else np.arange(n_total, dtype=float)
        n = min(xa.size, n_total)
        xa, arr = xa[:n], arr.reshape(-1)[:n]

        if fmt == "complex":
            if method != "none" and n > max_points:
                # pick indices on the magnitude so the envelope survives
                idx = downsample_indices(xa, np.abs(arr).astype(float), max_points, method)
                xa, arr = xa[idx], arr[idx]
                downsampled = True
            else:
                downsampled = False
            out.append(
                WaveSignalData(
                    name=name, x=_json_floats(xa),
                    y_re=_json_floats(np.real(arr)), y_im=_json_floats(np.imag(arr)),
                    n_total=n_total, n_returned=int(arr.size), downsampled=downsampled,
                )
            )
            continue

        try:
            y, _label = format_y(arr, fmt)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        if method != "none" and y.size > max_points:
            idx = downsample_indices(xa, np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0), max_points, method)
            xa_s, y_s = xa[idx], y[idx]
            downsampled = True
        else:
            xa_s, y_s = xa, y
            downsampled = False
        out.append(
            WaveSignalData(
                name=name, x=_json_floats(xa_s), y=_json_floats(y_s),
                n_total=n_total, n_returned=int(y_s.size), downsampled=downsampled,
            )
        )

    return WaveResponse(
        dataset_id=dataset_id, analysis=an.analysis, x_name=x_name, fmt=fmt, signals=out
    )


@router.post("/waveview/datasets/{dataset_id}/measure", response_model=MeasureResponse)
def measure(dataset_id: str, req: MeasureRequest = Body(...)):
    """Evaluate Tier-1 measurement recipes against the dataset (per-item degradation)."""
    entry = svc.get_dataset(dataset_id)
    results: list[MeasureResult] = []
    for item in req.items:
        name = item.name or str(item.recipe.get("meas", "measurement"))
        try:
            value = measure_dataset(entry.dataset, item.recipe, name=name)
        except (ValueError, KeyError, TypeError) as exc:
            # TypeError included: a JSON null/array recipe arg passes validate_recipe
            # (presence-only) and would otherwise 500 the WHOLE batch from the
            # registry's float()/int() casts — per-item degradation is the contract.
            results.append(MeasureResult(name=name, value=None, error=str(exc)))
            continue
        if not np.isfinite(value):
            results.append(MeasureResult(name=name, value=None, error=f"non-finite result ({value})"))
        else:
            results.append(MeasureResult(name=name, value=float(value), error=None))
    return MeasureResponse(dataset_id=dataset_id, results=results)


@router.get("/waveview/datasets/{dataset_id}/scalars", response_model=ScalarsResponse)
def get_scalars(
    dataset_id: str,
    analysis: str = Query("op", description="Analysis whose point scalars to return"),
    prefix: str | None = Query(None, description="Only keys starting with this (e.g. an instance name)"),
):
    """Point scalars of an analysis — op-point node values, per-device inst:param tables."""
    entry = svc.get_dataset(dataset_id)
    an = entry.dataset.resolve_analysis(analysis)
    if an is None:
        raise HTTPException(404, f"No analysis {analysis!r} in dataset")
    items = {
        k: (float(v) if np.isfinite(v) else None)
        for k, v in sorted(an.scalars.items())
        if prefix is None or k.startswith(prefix)
    }
    return ScalarsResponse(dataset_id=dataset_id, analysis=an.analysis, scalars=items)


@router.get("/waveview/datasets/{dataset_id}/log", response_model=LogResponse)
def get_log(
    dataset_id: str,
    min_level: str = Query("info", description="Severity floor: info|note|warning|error"),
    tail: int = Query(2000, ge=1, le=50_000, description="Return at most the last N lines (after filtering)"),
):
    """The dataset's simulator log, parsed + severity-classified."""
    entry = svc.get_dataset(dataset_id)
    log_path = entry.dataset.log_path
    if not log_path:
        raise HTTPException(404, "Dataset has no simulator log (none discovered or attached)")
    try:
        summary = parse_sim_log(log_path)
    except OSError as exc:
        raise HTTPException(404, f"Could not read log {log_path}: {exc}") from exc
    lines = summary.filtered(min_level)[-tail:]
    return LogResponse(
        dataset_id=dataset_id,
        path=summary.path,
        counts=summary.counts,
        n_lines=summary.n_lines,
        lines=[LogLineModel(no=ln.no, level=ln.level, text=ln.text) for ln in lines],
    )


@router.get("/waveview/log/stream")
async def stream_log(
    request: Request,
    path: str = Query(..., description="Absolute path of a simulator log (whitelisted)"),
    from_line: int = Query(0, ge=0, description="Skip lines up to this number (resume support)"),
    follow: bool = Query(True, description="Keep tailing for new lines (tail -f); false = drain + close"),
    poll_s: float = Query(0.5, ge=0.1, le=5.0, description="Poll interval while following"),
):
    """SSE live tail of a simulator log — works while the simulation is still writing it.

    Events are ``data: {"no": N, "level": "...", "text": "..."}`` per line, with an
    ``event: eof`` marker once the current end is reached (then keeps following unless
    ``follow=false``). Comment heartbeats keep proxies from buffering the stream.
    """
    resolved = svc.validate_under_allowed(path)
    if not resolved.is_file():
        raise HTTPException(404, f"Log not found: {resolved}")
    # defense-in-depth: only tail log-shaped files (the whitelist is the real gate, but
    # this endpoint should never become a generic file reader)
    if resolved.suffix.lower() not in (".log", ".out", ".txt") and resolved.name not in (
        "logFile", "logStatus",
    ):
        raise HTTPException(400, f"Not a simulator log (by name): {resolved.name}")

    async def gen():
        offset = 0
        line_no = 0
        pending = b""
        sent_eof = False
        idle = 0.0
        while True:
            if await request.is_disconnected():
                return
            try:
                size = resolved.stat().st_size
            except OSError:
                yield 'event: gone\ndata: {}\n\n'
                return
            if size < offset:  # truncated/rotated — start over
                offset, line_no, pending = 0, 0, b""
            if size > offset:
                with resolved.open("rb") as f:
                    f.seek(offset)
                    chunk = f.read(min(size - offset, 1 << 20))
                offset += len(chunk)
                pending += chunk
                lines = pending.split(b"\n")
                pending = lines.pop()  # last element: incomplete tail (or b"")
                for raw in lines:
                    line_no += 1
                    if line_no <= from_line:
                        continue
                    text = raw.decode("utf-8", errors="replace")
                    parsed = parse_log_text(text)
                    level = parsed.lines[0].level if parsed.lines else "info"
                    payload = json.dumps({"no": line_no, "level": level, "text": text})
                    yield f"data: {payload}\n\n"
                sent_eof = False
                idle = 0.0
                continue  # there may be more to read immediately
            if not sent_eof:
                yield f'event: eof\ndata: {{"n_lines": {line_no}}}\n\n'
                sent_eof = True
                if not follow:
                    return
            await asyncio.sleep(poll_s)
            idle += poll_s
            if idle >= 10.0:  # comment heartbeat (keeps the connection visibly alive)
                idle = 0.0
                yield ": ping\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/waveview/runs", response_model=RunListResponse)
def get_runs(
    project_id: str | None = Query(None, description="Only this project's runs (default: all + unscoped)"),
):
    """Optimizer runs the viewer can open, resolved from their on-disk run.json (newest first)."""
    return {"runs": svc.list_runs(project_id)}


@router.get("/waveview/runs/{run_id}/artifacts", response_model=RunArtifactsResponse)
def get_run_artifacts(
    run_id: str,
    project_id: str | None = Query(None, description="Scope the run lookup to one project"),
):
    """Openable artifacts inside a run's dir: per-trial ngspice .raw files, Spectre raw
    dirs, and logs (incl. the run's own run.log for the SSE tail), newest-modified first."""
    info = svc.find_run(run_id, project_id)
    return {
        "run_id": info["run_id"],
        "run_dir": info["run_dir"],
        "artifacts": svc.list_run_artifacts(Path(info["run_dir"])),
    }


@router.get("/waveview/runs/{run_id}/artifacts/file")
def get_run_artifact_file(
    run_id: str,
    rel: str = Query(..., description="Run-dir-relative artifact path "
                                      "(e.g. run.json, config_snapshot.yaml, run.log)"),
    project_id: str | None = Query(None, description="Scope the run lookup to one project"),
):
    """Download ANY artifact inside a run's dir by **identity** — ``(run_id, rel)`` —
    rather than by an absolute whitelisted path. This is the id-addressed serving the
    plan calls for (§3.3): a traversal outside the run dir is rejected. Unlike
    ``/open_run`` (which loads a waveform into the viewer registry), this streams the
    raw bytes of any run file — ``run.json``, ``config_snapshot.yaml``, ``run.log``, a
    checkpoint, a ``.raw``."""
    info = svc.find_run(run_id, project_id)
    target = project_service.resolve_run_file(Path(info["run_dir"]), rel)
    if target is None:
        raise HTTPException(404, f"No artifact {rel!r} under run {run_id!r}")
    return FileResponse(str(target), filename=target.name)


class SnapshotRequest(BaseModel):
    png_base64: str = Field(..., description="PNG bytes, base64-encoded (no data: URL prefix)")
    name: str | None = Field(
        None,
        description="Snapshot label — slugified into snapshots/<name>.png; a repeat "
                    "save under the same name overwrites (the thumbnail contract)",
    )


class SnapshotResponse(BaseModel):
    run_id: str
    rel: str = Field(..., description="Run-dir-relative path (serve it back via …/artifacts/file?rel=)")
    path: str
    size_bytes: int


_SNAPSHOT_MAX_BYTES = 8 * 1024 * 1024
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@router.post("/waveview/runs/{run_id}/snapshot", response_model=SnapshotResponse)
def save_run_snapshot(
    run_id: str,
    body: SnapshotRequest,
    project_id: str | None = Query(None, description="Scope the run lookup to one project"),
):
    """Persist a rendered plot PNG into the run's own dir (``snapshots/<name>.png``).

    The viewer renders client-side (Plotly), so the snapshot travels up as base64 —
    the server only validates and stores it. Snapshots live INSIDE the run dir so they
    inherit the run's identity/retention story and are immediately fetchable by any
    surface through ``GET …/runs/{run_id}/artifacts/file?rel=snapshots/<name>.png``
    (the Library datasheet thumbnails read them this way).
    """
    info = svc.find_run(run_id, project_id)
    try:
        data = base64.b64decode(body.png_base64, validate=True)
    except Exception:
        raise HTTPException(400, "png_base64 is not valid base64")
    if len(data) > _SNAPSHOT_MAX_BYTES:
        raise HTTPException(413, f"snapshot exceeds {_SNAPSHOT_MAX_BYTES // (1024 * 1024)} MB")
    if not data.startswith(_PNG_MAGIC):
        raise HTTPException(415, "payload is not a PNG")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", body.name or "snapshot").strip("-.") or "snapshot"
    target = Path(info["run_dir"]) / "snapshots" / f"{slug}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(target, data)
    return SnapshotResponse(
        run_id=run_id, rel=f"snapshots/{slug}.png", path=str(target), size_bytes=len(data)
    )


class PvtCornerWave(BaseModel):
    corner: str
    dataset_id: str | None
    x: list[float | None] | None = None
    y: list[float | None] | None = None
    phase: list[float | None] | None = None
    """Per-measure scalar values (`meas` query, comma-separated), null on failure."""
    metrics: dict[str, float | None] = {}
    error: str | None = None


class PvtGroupResponse(BaseModel):
    run_id: str
    analysis: str
    signal: str
    corners: list[PvtCornerWave]


_CORNER_DIR_RE = re.compile(r"__([A-Za-z0-9][A-Za-z0-9_.-]*)$")


@router.get("/waveview/runs/{run_id}/pvt", response_model=PvtGroupResponse)
def pvt_group_wave(
    run_id: str,
    analysis: str = Query(..., description="Engine-neutral analysis key (ac/tran/…)"),
    signal: str = Query(..., description="Signal to extract per corner"),
    project_id: str | None = Query(None, description="Scope the run lookup to one project"),
    fmt: str = Query("auto", description="auto|mag_db|mag|phase_deg|re|im"),
    phase: bool = Query(False, description="Also return the signal's phase_deg curve"),
    meas: str | None = Query(
        None, description="Comma-separated Tier-1 measures to evaluate per corner (e.g. pm,ugf)"
    ),
    match: str | None = Query(
        None,
        description="Substring filter on the artifact's run-dir-relative path — pin the "
        "TESTBENCH (e.g. 'tb_ac'): several testbenches can emit the same analysis kind",
    ),
    out: str | None = Query(None, description="`out` argument for the measures"),
    max_points: int = Query(1500, ge=16, le=200_000),
    limit: int = Query(12, ge=1, le=64, description="Max corners"),
):
    """One corner-grouped wave call — the viewer's PVT mode (`?group=pvt` in the
    design handoff): discover the run's ``run_<n>_<tb>__<corner>/`` raw artifacts,
    open the newest artifact per corner, and return each corner's curve (+ optional
    phase and Tier-1 metrics). Corner datasets register in the viewer registry
    (cached, evictable); their ids come back so a client can track them. Per-corner
    failures degrade to ``error`` — one broken corner never 500s the sweep."""
    info = svc.find_run(run_id, project_id)
    by_corner: dict[str, list[dict[str, Any]]] = {}
    for a in svc.list_run_artifacts(Path(info["run_dir"])):
        if a["type"] not in ("ngspice_raw", "spectre_raw_dir"):
            continue
        if match and match not in a["name"]:
            continue
        m = _CORNER_DIR_RE.search(Path(a["path"]).parent.name)
        if not m:
            continue
        by_corner.setdefault(m.group(1), []).append(a)
    if not by_corner:
        raise HTTPException(
            404,
            f"Run {run_id!r} has no per-corner artifacts (…__<corner>/ folders) — "
            "run a corners sweep (pvt.mode: multi) with keep_raw",
        )
    # Nominal (tt/typ/nom) first, then lexical — the client's presentation order.
    names = sorted(
        by_corner,
        key=lambda c: (0 if re.match(r"(?i)^(tt|typ|nom)", c) else 1, c),
    )[:limit]

    meas_names = [m.strip() for m in (meas or "").split(",") if m.strip()]
    corners: list[PvtCornerWave] = []
    for c in names:
        # A multi-testbench sweep leaves one artifact per tb per corner — walk
        # newest-first until one actually carries the requested analysis.
        entry = None
        an = None
        last_err: str | None = None
        for art in sorted(by_corner[c], key=lambda a: a["mtime"], reverse=True):
            try:
                cand = svc.open_dataset(art["path"])
            except HTTPException as exc:
                last_err = str(exc.detail)
                continue
            cand_an = cand.dataset.resolve_analysis(analysis)
            if cand_an is not None:
                entry, an = cand, cand_an
                break
            last_err = f"no analysis {analysis!r} (have {sorted(cand.dataset.analyses)})"
        if entry is None or an is None:
            corners.append(
                PvtCornerWave(corner=c, dataset_id=None, error=last_err or "no artifact")
            )
            continue
        ds = entry.dataset
        an_key, an_sweep = an.analysis, an.sweep

        def _series(sig_fmt: str) -> tuple[list[float | None], list[float | None]] | None:
            sig = ds.find_signal(an_key, signal)
            if sig is None:
                return None
            arr = np.asarray(sig.data).reshape(-1)
            x_sig = ds.find_signal(an_key, an_sweep) if an_sweep else None
            xa = (
                np.real(np.asarray(x_sig.data)).astype(float).reshape(-1)
                if x_sig is not None
                else np.arange(arr.size, dtype=float)
            )
            n = min(xa.size, arr.size)
            xa, arr = xa[:n], arr[:n]
            y, _label = format_y(arr, sig_fmt)
            if y.size > max_points:
                idx = downsample_indices(
                    xa, np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0), max_points, "minmax"
                )
                xa, y = xa[idx], y[idx]
            return _json_floats(xa), _json_floats(y)

        try:
            main = _series(fmt)
        except ValueError as exc:
            corners.append(
                PvtCornerWave(corner=c, dataset_id=entry.dataset_id, error=str(exc))
            )
            continue
        phase_y: list[float | None] | None = None
        if phase and main is not None:
            try:
                ph = _series("phase_deg")
                phase_y = ph[1] if ph else None
            except ValueError:
                phase_y = None
        metrics: dict[str, float | None] = {}
        for mname in meas_names:
            recipe: dict[str, Any] = {"meas": mname}
            if out:
                recipe["out"] = out
            try:
                value = measure_dataset(ds, recipe, name=mname)
                metrics[mname] = float(value) if np.isfinite(value) else None
            except (ValueError, KeyError, TypeError):
                metrics[mname] = None
        corners.append(
            PvtCornerWave(
                corner=c,
                dataset_id=entry.dataset_id,
                x=main[0] if main else None,
                y=main[1] if main else None,
                phase=phase_y,
                metrics=metrics,
                error=None if main else f"no signal {signal!r} in {analysis!r}",
            )
        )
    return PvtGroupResponse(run_id=run_id, analysis=analysis, signal=signal, corners=corners)


_SWEEP_DIR_RE = re.compile(r"^run_\d+_(.+?)__([A-Za-z0-9][A-Za-z0-9_.-]*)$")


def _corner_rank(corner: str) -> tuple:
    """Merge preference of a sweep member's corner: nominal first, then the
    lowest-numbered MC sample, then alphabetical."""
    low = corner.lower()
    if low.startswith(("tt", "typ", "nom")):
        return (0,)
    m = re.fullmatch(r"mc[_-]?(\d+)", low)
    if m:
        return (1, int(m.group(1)))
    return (2, low)


def _one_member_per_testbench(candidates: list[dict]) -> list[dict]:
    """For corner/sample-suffixed artifacts (``run_<n>_<tb>__<corner>/``), keep ONE
    member per testbench — a sweep/MC run otherwise merges as N copies of the same
    bench from different corners (and can miss benches entirely under ``limit``).
    The nominal corner is preferred so Single mode shows unperturbed data; the
    sweep rail fetches per-corner curves via GET /runs/{id}/pvt regardless.
    Non-suffixed candidates pass through untouched, order preserved."""
    best: dict[str, dict] = {}
    order: list[str] = []
    out: list[dict] = []
    for a in candidates:
        m = _SWEEP_DIR_RE.match(Path(a["name"]).parent.name)
        if not m:
            out.append(a)
            continue
        tb, corner = m.group(1), m.group(2)
        if tb not in best:
            best[tb], order = a, order + [tb]
        elif _corner_rank(corner) < _corner_rank(
            _SWEEP_DIR_RE.match(Path(best[tb]["name"]).parent.name).group(2)  # type: ignore[union-attr]
        ):
            best[tb] = a
    return out + [best[tb] for tb in order]


@router.post("/waveview/open_run", response_model=DatasetMeta)
def open_run(req: OpenRunRequest = Body(...)):
    """Open a run's result artifact(s) by run_id — the run-picker convenience on top
    of POST /waveview/open (which it delegates to; same dataset_id semantics).

    Default: the newest artifact only. With ``merge: true``: the newest ``limit``
    raw artifacts combined server-side into one multi-analysis dataset (one tree
    entry with ac + tran + noise tabs instead of N per-testbench datasets). A
    corner/MC sweep run merges ONE member per testbench (nominal preferred)."""
    info = svc.find_run(req.run_id, req.project_id)
    candidates = [
        a for a in svc.list_run_artifacts(Path(info["run_dir"]))
        if a["type"] in ("ngspice_raw", "spectre_raw_dir")
        and (req.match is None or req.match in a["name"])
    ]
    if not candidates:
        raise HTTPException(
            404,
            f"Run {req.run_id!r} has no openable result artifacts"
            + (f" matching {req.match!r}" if req.match else "")
            + " (list them via GET /waveview/runs/{run_id}/artifacts)",
        )
    if req.merge and len(candidates) > 1:
        entry = svc.open_run_merged(
            Path(info["run_dir"]), _one_member_per_testbench(candidates)[: req.limit]
        )
    else:
        entry = svc.open_dataset(candidates[0]["path"])
    return svc.dataset_meta(entry)


@router.post("/waveview/runs/{run_id}/prune", response_model=RunPruneResponse)
def prune_run_artifacts(
    run_id: str,
    project_id: str | None = Query(None, description="Scope the run lookup to one project"),
    dry_run: bool = Query(False, description="Report what would be freed without deleting"),
):
    """Free a finished run's heavy waveforms NOW (the keep_raw disk-hog escape hatch).

    Applies the ``metrics_only`` retention tier via the core workspace GC
    (``spicexplorer_core.workspace.retention.prune_run``): the ``sim/`` subtree and
    stray ``.raw`` files go, while ``run.json``, ``events.ndjson``, checkpoints and
    logs stay. Idempotent; a still-``running`` run is refused. Open viewer datasets
    backed by the pruned files are evicted from the registry."""
    from spicexplorer_core.workspace import retention

    info = svc.find_run(run_id, project_id)
    run_dir = Path(info["run_dir"])
    report = retention.prune_run(run_dir, "metrics_only", dry_run=dry_run)
    closed = 0
    if report.get("pruned"):
        closed = svc.close_datasets_under(run_dir)
    return RunPruneResponse(
        run_id=info["run_id"],
        tier=report.get("tier"),
        pruned=bool(report.get("pruned")),
        skipped=report.get("skipped"),
        removed=list(report.get("removed") or []),
        freed_bytes=int(report.get("freed_bytes") or 0),
        dry_run=dry_run,
        closed_datasets=closed,
    )


@router.get("/waveview/browse", response_model=BrowseResponse)
def browse(
    dir: str = Query(..., description="Absolute directory under the allowed roots"),
    limit: int = Query(500, ge=1, le=5000),
):
    """List result artifacts in a directory: .raw files, Spectre raw dirs, logs, subdirs."""
    resolved = svc.validate_under_allowed(dir)
    if not resolved.is_dir():
        raise HTTPException(404, f"Not a directory: {resolved}")

    entries: list[BrowseEntry] = []
    try:
        children = sorted(resolved.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError as exc:
        raise HTTPException(404, f"Could not list {resolved}: {exc}") from exc
    for child in children:
        if child.name.startswith("."):
            continue
        kind = svc.classify_artifact(child)
        if kind is None:
            continue
        entries.append(BrowseEntry(name=child.name, path=str(child), type=kind))
        if len(entries) >= limit:
            break
    # "Up" target, whitelist-aware: only offered while the parent stays under an
    # allowed root (clients previously string-parented and could walk out of bounds).
    parent: str | None = None
    if resolved.parent != resolved:
        try:
            svc.validate_under_allowed(resolved.parent)
            parent = str(resolved.parent)
        except HTTPException:
            parent = None
    return BrowseResponse(dir=str(resolved), parent=parent, entries=entries)


# --- Upload (route "4a") ------------------------------------------------------
# Staged uploads land under work_root()/waveview_uploads/<id>/ — inside the /work
# bind-mount, so they are reviewable (and cleanable) from the host like any run.
_UPLOAD_SUBDIR = "waveview_uploads"
_MAX_UPLOAD_BYTES = 512 * 2**20  # one artifact; the loader peaks ~2× file size
_MAX_ZIP_MEMBERS = 4096
_MAX_ZIP_TOTAL_BYTES = 1024 * 2**20  # uncompressed (zip-bomb guard)
_CHUNK = 4 * 2**20
# Staged uploads are a cache, and a cache needs GC: dirs older than this are swept
# opportunistically on the next upload (0 disables). A dir still backing an OPEN
# dataset is never swept.
_UPLOAD_TTL_DAYS_ENV = "SPICEXPLORER_UPLOAD_TTL_DAYS"
_DEFAULT_UPLOAD_TTL_DAYS = 14.0

_RAW_EXTS = {".raw"}
_LOG_EXTS = {".log", ".out", ".txt"}


def _sanitize_filename(name: str | None) -> str:
    base = Path(str(name or "")).name.strip()
    if not base or base.startswith("."):
        raise HTTPException(400, "Upload needs a plain file name")
    return base


def _uploads_root() -> Path:
    return work_root() / _UPLOAD_SUBDIR


def _upload_dir(upload_id: str) -> Path:
    # Ids are server-minted hex — anything else (traversal, separators) is a 404,
    # and the resolved dir must stay a direct child of the staging root.
    if not upload_id or not all(c in "0123456789abcdef" for c in upload_id):
        raise HTTPException(404, f"No upload {upload_id!r}")
    d = (_uploads_root() / upload_id).resolve()
    if d.parent != _uploads_root().resolve():
        raise HTTPException(404, f"No upload {upload_id!r}")
    return d


def _dir_stats(d: Path) -> tuple[int, int]:
    size = n = 0
    for f in d.rglob("*"):
        if f.is_file():
            n += 1
            try:
                size += f.stat().st_size
            except OSError:
                pass
    return size, n


def _upload_ttl_s() -> float:
    """TTL in seconds; <= 0 disables the sweep."""
    import os

    raw = os.environ.get(_UPLOAD_TTL_DAYS_ENV, "")
    try:
        days = float(raw) if raw.strip() else _DEFAULT_UPLOAD_TTL_DAYS
    except ValueError:
        days = _DEFAULT_UPLOAD_TTL_DAYS
    return days * 86400.0


def sweep_stale_uploads() -> int:
    """Remove staged upload dirs older than the TTL (opportunistic GC).

    Runs in a worker thread on each new upload. A dir backing a currently-open
    dataset is skipped — its files may still be served (log tails). Returns the
    number of dirs removed."""
    import shutil
    import time

    ttl = _upload_ttl_s()
    root = _uploads_root()
    if ttl <= 0 or not root.is_dir():
        return 0
    removed = 0
    cutoff = time.time() - ttl
    for d in root.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        try:
            if d.stat().st_mtime >= cutoff:
                continue
        except OSError:
            continue
        if svc.open_dataset_ids_under(d):
            continue
        svc.close_datasets_under(d)  # racy open between checks — evict, then remove
        shutil.rmtree(d, ignore_errors=True)
        removed += 1
    return removed


@router.get("/waveview/uploads", response_model=UploadListResponse)
def list_uploads():
    """Staged uploads still on disk (newest first) — the GC's inventory surface."""
    root = _uploads_root()
    out: list[UploadEntry] = []
    if root.is_dir():
        for d in sorted(root.iterdir(), reverse=True):
            if not d.is_dir() or d.name.startswith("."):
                continue
            try:
                mtime = d.stat().st_mtime
            except OSError:
                continue
            size, n_files = _dir_stats(d)
            out.append(UploadEntry(
                upload_id=d.name,
                staged_path=str(d),
                mtime=mtime,
                size_bytes=size,
                n_files=n_files,
                open_dataset_ids=svc.open_dataset_ids_under(d),
            ))
        out.sort(key=lambda e: e.mtime, reverse=True)
    return UploadListResponse(uploads=out)


@router.delete("/waveview/uploads/{upload_id}", response_model=UploadDeletedResponse)
def delete_upload(upload_id: str):
    """Remove a staged upload dir (and evict any open datasets it was backing)."""
    import shutil

    d = _upload_dir(upload_id)
    if not d.is_dir():
        raise HTTPException(404, f"No upload {upload_id!r}")
    closed = svc.close_datasets_under(d)
    shutil.rmtree(d, ignore_errors=True)
    return UploadDeletedResponse(deleted=True, closed_datasets=closed)


async def _stream_to(dst: Path, file: UploadFile) -> int:
    """Write the upload to ``dst`` in chunks, enforcing the size cap."""
    total = 0
    with dst.open("wb") as out:
        while chunk := await file.read(_CHUNK):
            total += len(chunk)
            if total > _MAX_UPLOAD_BYTES:
                out.close()
                dst.unlink(missing_ok=True)
                raise HTTPException(413, f"Upload exceeds {_MAX_UPLOAD_BYTES // 2**20} MiB")
            out.write(chunk)
    return total


def _safe_extract_zip(zpath: Path, dest: Path) -> None:
    """Extract with traversal + bomb guards (member paths must stay inside dest)."""
    import zipfile

    try:
        zf = zipfile.ZipFile(zpath)
    except zipfile.BadZipFile as exc:
        raise HTTPException(400, f"Not a valid zip archive: {exc}") from exc
    with zf:
        infos = zf.infolist()
        if len(infos) > _MAX_ZIP_MEMBERS:
            raise HTTPException(413, f"Zip has more than {_MAX_ZIP_MEMBERS} members")
        if sum(i.file_size for i in infos) > _MAX_ZIP_TOTAL_BYTES:
            raise HTTPException(413, "Zip expands past the upload size limit")
        root = dest.resolve()
        for info in infos:
            target = (dest / info.filename).resolve()
            if not target.is_relative_to(root):
                raise HTTPException(400, f"Zip member escapes the staging dir: {info.filename}")
        zf.extractall(dest)


def _find_result_artifact(root: Path) -> tuple[Path, str] | None:
    """Newest raw artifact anywhere under ``root`` (mirrors open_run's pick).

    Spectre raw dirs are terminal: their member PSF files must not compete as
    artifacts, so anything under an already-seen spectre_raw_dir is skipped
    (rglob has no pruning; the sorted order guarantees parents come first).
    """
    best: tuple[float, Path, str] | None = None
    spectre_dirs: list[Path] = []
    for p in [root, *sorted(root.rglob("*"))]:
        if any(sd in p.parents for sd in spectre_dirs):
            continue
        kind = svc.classify_artifact(p)
        if kind == "spectre_raw_dir":
            spectre_dirs.append(p)
        if kind in ("ngspice_raw", "spectre_raw_dir"):
            mtime = p.stat().st_mtime
            if best is None or mtime > best[0]:
                best = (mtime, p, kind)
    return (best[1], best[2]) if best else None


def _process_upload(dest: Path, staged: Path, ext: str, upload_id: str) -> UploadResponse:
    """Sync tail of an upload: extract/classify/open. Runs in a worker thread —
    zip extraction and the dataset parse are CPU/disk-bound and must not stall
    the event loop (a wide raw takes ~a second to load)."""
    if ext == ".zip":
        _safe_extract_zip(staged, dest)
        staged.unlink()  # keep only the extracted tree
        found = _find_result_artifact(dest)
        if found is None:
            raise HTTPException(
                415, "Zip contained no result artifact (.raw file or Spectre raw dir)")
        artifact, kind = found
    elif ext in _LOG_EXTS:
        return UploadResponse(
            upload_id=upload_id, staged_path=str(staged), kind="log", dataset=None)
    else:
        kind = svc.classify_artifact(staged) or ""
        if kind != "ngspice_raw":
            raise HTTPException(415, f"{staged.name!r} does not look like an ngspice raw file")
        artifact = staged

    entry = svc.open_dataset(str(artifact))
    meta = svc.dataset_meta(entry)
    if not any(a["signals"] or a["n_scalars"] for a in meta["analyses"]):
        # Arbitrary bytes with a .raw suffix "parse" into an empty dataset (the
        # loader keeps unknown plots with a warning, so garbage yields one empty
        # analysis); an upload with nothing viewable is a rejection, and the empty
        # dataset must not linger in the registry.
        svc.close_dataset(meta["dataset_id"])
        raise HTTPException(415, f"{artifact.name!r} parsed but contains no waveform data")
    return UploadResponse(
        upload_id=upload_id,
        staged_path=str(artifact),
        kind=kind,  # type: ignore[arg-type]
        dataset=DatasetMeta(**meta),
    )


# --- run a netlist (the handoff's true "4a": drop a deck → run → waveforms) -----

_NETLIST_EXTS = {".spice", ".cir", ".net", ".sp"}
_MAX_NETLIST_BYTES = 2 * 2**20
_NETLIST_TIMEOUT_S = 180


class RunNetlistRequest(BaseModel):
    content: str = Field(..., description="A SELF-CONTAINED ngspice deck (its own analyses/"
                                          "includes; `.control` blocks run as written)")
    filename: str | None = Field(None, description="Display name; extension must be one of "
                                                   ".spice/.cir/.net/.sp (default deck.spice)")


class RunNetlistResponse(BaseModel):
    run_id: str
    run_dir: str
    log_tail: list[str] = Field(default_factory=list, description="Last lines of the ngspice log")
    dataset: DatasetMeta


def _run_netlist_sync(content: str, filename: str) -> RunNetlistResponse:
    from datetime import datetime

    from spicexplorer_core.env import probe_env
    from spicexplorer_core.workspace.runs import (
        envelope_fields,
        mint_run_dir,
        write_run_record,
    )

    env = probe_env()
    if not env.get("ngspice_ok"):
        raise HTTPException(503, "ngspice is not available on this host — netlist runs are disabled")

    # A first-class (unscoped) run under WORK_ROOT/runs: the runs lister, the
    # artifact routes, retention/pruning, and open_run all work on it for free.
    run_id, run_dir = mint_run_dir(work_root() / "runs", "netlist")
    deck = run_dir / filename
    deck.write_text(content)
    record: dict[str, Any] = {
        "run_id": run_id,
        "project_id": None,
        "label": f"netlist · {filename}",
        "status": "running",
        "started": datetime.now().isoformat(timespec="seconds"),
        **envelope_fields("netlist", retention="full", inputs={"netlist": str(deck)}),
    }
    write_run_record(run_dir, record)

    def _finish(status: str, error: str | None = None) -> None:
        record.update(status=status, ended=datetime.now().isoformat(timespec="seconds"))
        if error:
            record["error"] = error
        write_run_record(run_dir, record)

    import subprocess

    # -r catches decks with plain .ac/.tran cards and no explicit `write`; decks
    # whose .control writes named raws land those in cwd (= the run dir) instead.
    cmd = [str(env.get("ngspice_path") or "ngspice"), "-b", "-o", "run.log",
           "-r", "default.raw", filename]
    try:
        proc = subprocess.run(
            cmd, cwd=run_dir, timeout=_NETLIST_TIMEOUT_S, capture_output=True, text=True
        )
    except subprocess.TimeoutExpired:
        _finish("error", f"ngspice timed out after {_NETLIST_TIMEOUT_S}s")
        raise HTTPException(
            422, f"ngspice timed out after {_NETLIST_TIMEOUT_S}s (run kept: {run_id})"
        )

    log_path = run_dir / "run.log"
    if not log_path.exists() and (proc.stdout or proc.stderr):
        log_path.write_text((proc.stdout or "") + (proc.stderr or ""))
    try:
        tail = log_path.read_text(errors="replace").splitlines()[-15:]
    except OSError:
        tail = []

    raws = [p for p in run_dir.glob("*.raw") if p.stat().st_size > 0]
    if not raws:
        _finish("error", "no raw produced")
        raise HTTPException(
            422,
            "The deck ran but produced no waveform data (no non-empty .raw). "
            f"Run kept for inspection: {run_id}. Log tail: " + " | ".join(tail[-5:]),
        )
    newest = max(raws, key=lambda p: p.stat().st_mtime)
    entry = svc.open_dataset(str(newest))
    meta = svc.dataset_meta(entry)
    if not any(a["signals"] or a["n_scalars"] for a in meta["analyses"]):
        svc.close_dataset(meta["dataset_id"])
        _finish("error", "raw contains no waveform data")
        raise HTTPException(422, f"{newest.name!r} parsed but contains no waveform data (run {run_id})")
    _finish("done")
    return RunNetlistResponse(
        run_id=run_id, run_dir=str(run_dir), log_tail=tail, dataset=DatasetMeta(**meta)
    )


@router.post("/waveview/run_netlist", response_model=RunNetlistResponse)
async def run_netlist(body: RunNetlistRequest):
    """Run a SELF-CONTAINED ngspice deck and open its result in the viewer.

    The drop-zone's "4a" completion: the deck is written into a fresh first-class
    ``kind: netlist`` run under ``WORK_ROOT/runs`` (envelope + run.json, so listing,
    artifact serving, retention, and re-opening all work on it), ngspice runs it in
    batch mode with the run dir as cwd, and the newest non-empty ``.raw`` auto-opens
    (sibling ``run.log`` attaches via the usual discovery). A deck that produces no
    waveform data is a 422 whose run dir is KEPT so the log can be inspected.
    Requires ngspice on the host (503 otherwise); PDK-referencing decks additionally
    need their model libraries resolvable — a failure surfaces in the log tail.
    """
    name = _sanitize_filename(body.filename or "deck.spice")
    if Path(name).suffix.lower() not in _NETLIST_EXTS:
        raise HTTPException(
            415, f"{name!r} is not a netlist — expected one of {sorted(_NETLIST_EXTS)}"
        )
    if len(body.content.encode("utf-8", errors="replace")) > _MAX_NETLIST_BYTES:
        raise HTTPException(413, f"netlist exceeds {_MAX_NETLIST_BYTES // 2**20} MiB")
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _run_netlist_sync, body.content, name)


@router.post("/waveview/upload", response_model=UploadResponse)
async def upload_artifact(request: Request, file: UploadFile = File(...)):
    """Stage a result artifact from the browser and open it (handoff route "4a").

    Accepts an ngspice ``.raw`` file, a ``.zip`` containing a Spectre psfascii raw
    dir (or raw files), or a bare simulator log. Anything else — including netlists,
    which belong to the run flow, not the viewer — is 415. Raw artifacts auto-open;
    a sibling log inside the same staging dir is attached by the usual discovery.
    A rejected upload leaves nothing behind: every error path removes the staging dir.
    """
    import shutil
    import uuid

    name = _sanitize_filename(file.filename)
    ext = Path(name).suffix.lower()
    if ext not in _RAW_EXTS | _LOG_EXTS | {".zip"}:
        raise HTTPException(
            415,
            f"Unsupported upload {name!r} — expected a .raw file, a .zip of a Spectre "
            "raw dir, or a simulator log. (Netlists run via a project, not the viewer.)",
        )
    # Early reject on the declared size, before reading the body. (The streaming cap
    # in _stream_to still covers chunked encodings; hard body limits for an exposed
    # deployment belong to the reverse proxy.)
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > _MAX_UPLOAD_BYTES + 65536:
        raise HTTPException(413, f"Upload exceeds {_MAX_UPLOAD_BYTES // 2**20} MiB")

    loop = asyncio.get_running_loop()
    # Opportunistic TTL sweep of PREVIOUS staged uploads (worker thread — rmtree of
    # a large stale dir must not stall the event loop). The new dir is fresh, so
    # the sweep can never race it.
    await loop.run_in_executor(None, sweep_stale_uploads)

    upload_id = uuid.uuid4().hex[:12]
    dest = work_root() / _UPLOAD_SUBDIR / upload_id
    dest.mkdir(parents=True, exist_ok=False)
    staged = dest / name
    try:
        await _stream_to(staged, file)
        return await loop.run_in_executor(None, _process_upload, dest, staged, ext, upload_id)
    except Exception:
        # 413/415/422/parse failure — drop the staged bytes so rejected uploads
        # can't accumulate under /work.
        shutil.rmtree(dest, ignore_errors=True)
        raise
