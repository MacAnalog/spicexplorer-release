"""Manual single-simulation route — evaluate ONE chosen design point on demand.

Unlike /sanity-check (which sims a *random* in-bounds point via the optimizer's
`ask()`), this evaluates a *caller-supplied* param vector through the exact same
primitive a real trial uses — `Spice_Constraint_Satisfaction.evaluate(params,
append_to_log=False)` — so the returned score + per-spec `fit_summary` are directly
comparable to checkpoint rows and to Score Shaping.

Two input modes:
  • Mode B (manual): `params` — an engineering-real vector ({"x_dut_W_1": 72e-6, ...}).
    A partial dict is valid; unset params keep their netlist `.param` defaults.
  • Mode A (checkpoint): `checkpoint_id` (+ optional `point` index) — replays a stored
    point's vector. `point` omitted → the best iteration (argmax score). Re-simulating
    the best point should reproduce its stored metrics, doubling as a validation tool.

The active PVT corner (Phase 1) is applied automatically when the optimizer is
constructed; `active_corner` optionally overrides it ephemerally (never rewrites YAML).
"""
from __future__ import annotations

import asyncio
import math
from pathlib import Path
from time import perf_counter
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from spicexplorer_api.services.num import safe_float as _safe_float

router = APIRouter()


class SimulateOnceRequest(BaseModel):
    yaml_path: str
    # Mode B — explicit param vector (partial dict allowed). Values may be plain
    # numbers OR engineering strings ("250u", "0.18u"); both are parsed server-side
    # via the project DSL's parse_value, so the UI can pass raw user input.
    params: dict[str, str | float] | None = None
    # Mode A — resolve the vector from a stored checkpoint instead.
    checkpoint_id: str | None = None
    point: int | None = None  # index into the checkpoint; None → best (argmax score)
    # Optional ephemeral PVT corner override (must match a corner in the project).
    active_corner: str | None = None
    # Run testbenches × EVERY enabled corner (ephemeral pvt.mode: multi) — the
    # launch-time corners-sweep lane; the run dir gets `__<corner>` artifacts the
    # Analyze viewer's PVT mode reads. Mutually exclusive with active_corner.
    sweep_corners: bool = False
    # Monte Carlo — clone the active corner into N statistical sample corners
    # (`mc1..mcN`: process libs swapped to their `_mismatch` sections + a unique
    # `.options seed` per sample) and run them like a corner sweep. Artifacts land
    # as `run_<n>_<tb>__mc<i>`; the Analyze viewer's "Monte Carlo" mode reads them.
    # `active_corner` (optional) picks the BASE corner to perturb.
    monte_carlo: int | None = None
    # RNG seed of the first sample — sample i runs `.options seed=<mc_seed0+i-1>`,
    # so a given (seed0, N) is exactly reproducible.
    mc_seed0: int = 1
    # Retain the sim's .raw waveform files (normally deleted after scoring) so the
    # run is openable in the Analyze waveform viewer via /api/waveview/open_run.
    keep_raw: bool = False


class SpecMetric(BaseModel):
    curr_val: float | None = None
    score: float | None = None


class SimulateOnceResponse(BaseModel):
    ok: bool
    score: float | None = None
    metrics: dict[str, SpecMetric] = {}
    params_used: dict[str, float] = {}
    active_corner: str | None = None
    # The run envelope this sim ran under (kind: simulate). With keep_raw the caller
    # can hand this straight to POST /api/waveview/open_run to view the waveforms.
    run_id: str | None = None
    # Non-fatal advisories (out-of-range value, unknown param, unknown corner, …).
    warnings: list[str] = []
    log_files: dict[str, str] = {}
    log_tails: dict[str, str] = {}
    error: str | None = None
    elapsed_ms: float | None = None
    elapsed_ms_load: float | None = None
    pdk_ok: bool | None = None
    pdk_detail: str | None = None


def _resolve_params_from_checkpoint(checkpoint_id: str, point: int | None, warnings: list[str]) -> dict[str, float]:
    """Pull a single point's engineering-real param vector out of a stored checkpoint."""
    from spicexplorer_api.routes.checkpoint import _resolve_checkpoint_path
    from spicexplorer_api.services.checkpoint_reader import read_checkpoint

    path = _resolve_checkpoint_path(checkpoint_id)
    if path is None or not path.exists():
        raise FileNotFoundError(f"Checkpoint '{checkpoint_id}' not found")
    data = read_checkpoint(path)
    params: dict[str, list] = data.get("params", {})
    scores: list = data.get("scores", [])
    if not params:
        raise ValueError(f"Checkpoint '{checkpoint_id}' has no param vectors to evaluate")

    n = max((len(v) for v in params.values()), default=0)
    if point is None:
        # Best point = argmax of finite scores (checkpoints don't persist a best index).
        idx = 0
        best = -math.inf
        for i, s in enumerate(scores):
            sv = _safe_float(s)
            if sv is not None and sv > best:
                best, idx = sv, i
    else:
        idx = point
        if idx < 0 or idx >= n:
            warnings.append(f"point {point} out of range [0,{n - 1}]; clamped.")
            idx = max(0, min(idx, n - 1))

    out: dict[str, float] = {}
    for name, series in params.items():
        if idx < len(series):
            fv = _safe_float(series[idx])
            if fv is not None:
                out[name] = fv
    return out


def _validate_params(project, params: dict[str, float], warnings: list[str]) -> None:
    """Non-fatal range/identity checks — `evaluate` trusts real values, so flag (not
    reject) an unknown param or a value outside its [min_val, max_val] hint."""
    known = {p.name: p for p in project.dut_params}
    for name, val in params.items():
        p = known.get(name)
        if p is None:
            warnings.append(f"'{name}' is not a declared dut_param; it will be injected verbatim.")
            continue
        lo = float(p.min_val) if p.min_val is not None else None
        hi = float(p.max_val) if p.max_val is not None else None
        if lo is not None and val < lo:
            warnings.append(f"'{name}'={val:g} is below min_val {lo:g}.")
        if hi is not None and val > hi:
            warnings.append(f"'{name}'={val:g} is above max_val {hi:g}.")


def _run_single_sim(req: SimulateOnceRequest) -> dict[str, Any]:
    from spicexplorer.core.domains import Project_Setup, parse_value
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective
    from spicexplorer_core.pvt import monte_carlo_corners

    from spicexplorer_api.routes.sanity import _tail_log
    from spicexplorer_api.services.env_probe import probe_pdk
    from spicexplorer_api.services.optimizer_runner import _build_spicelib_wrappers

    t_start = perf_counter()
    pdk = probe_pdk()
    warnings: list[str] = []

    def _fail(error: str, **extra) -> dict[str, Any]:
        return {
            "ok": False, "error": error, "warnings": warnings,
            "elapsed_ms": (perf_counter() - t_start) * 1000,
            "pdk_ok": pdk["pdk_ok"], "pdk_detail": pdk["pdk_detail"], **extra,
        }

    # 1 — load project
    try:
        project = Project_Setup.from_yaml(req.yaml_path)
    except Exception as e:
        return _fail(f"Failed to load project: {e}")
    elapsed_load = (perf_counter() - t_start) * 1000

    # 2 — resolve the param vector (Mode A vs Mode B)
    try:
        if req.params is not None:
            params = {}
            for k, v in req.params.items():
                try:
                    params[k] = float(parse_value(v))
                except (ValueError, TypeError):
                    return _fail(f"Could not parse value for '{k}': {v!r}")
        elif req.checkpoint_id:
            params = _resolve_params_from_checkpoint(req.checkpoint_id, req.point, warnings)
        else:
            return _fail("Provide `params` (manual) or `checkpoint_id` (from a checkpoint).")
    except Exception as e:
        return _fail(str(e))
    if not params:
        return _fail("Resolved an empty param vector — nothing to simulate.")

    # 3 — ephemeral PVT corner override (applied at optimizer construction)
    active_corner: str | None = None
    # Sweep override — the launch-time "PVT corners" lane (design handoff's
    # Sweep row): force one evaluation across EVERY enabled corner even when
    # the project's YAML says mode: single. Ephemeral, like active_corner.
    if req.sweep_corners:
        if project.pvt is None or not project.pvt.corners:
            return _fail("sweep_corners requested but the project defines no PVT corners.")
        if req.active_corner:
            return _fail("sweep_corners and active_corner are mutually exclusive.")
        if req.monte_carlo is not None:
            return _fail("sweep_corners and monte_carlo are mutually exclusive.")
        if not project.pvt.is_multi():
            warnings.append(
                f"Corners sweep requested — ran all {len(project.pvt.enabled_corners())} "
                "enabled corners (project default is mode: single); metrics are "
                "'<corner>::<spec>'-keyed."
            )
            project.pvt.mode = "multi"
    # Monte Carlo lane — replace the corner set with mc1..mcN statistical samples
    # of the base corner, then run them through the same multi-corner fan-out.
    if req.monte_carlo is not None:
        if project.pvt is None or not project.pvt.corners:
            return _fail(
                "monte_carlo requested but the project defines no PVT corners "
                "(the base corner supplies the process libs to perturb)."
            )
        if not 2 <= req.monte_carlo <= 100:
            return _fail("monte_carlo must be between 2 and 100 samples.")
        if req.active_corner:
            if project.pvt.get(req.active_corner) is None:
                return _fail(f"monte_carlo base corner '{req.active_corner}' is not defined.")
            project.pvt.active_corner = req.active_corner
        mc_base = project.pvt.get_active()
        try:
            mc_samples = monte_carlo_corners(mc_base, req.monte_carlo, seed0=req.mc_seed0)
        except ValueError as e:
            return _fail(str(e))
        project.pvt.corners = mc_samples
        project.pvt.active_corner = mc_samples[0].name
        project.pvt.mode = "multi"
        warnings.append(
            f"Monte Carlo: {req.monte_carlo} statistical samples of corner '{mc_base.name}' "
            f"(seeds {req.mc_seed0}..{req.mc_seed0 + req.monte_carlo - 1}); metrics are "
            "'mc<i>::<spec>'-keyed."
        )
    if project.pvt is not None and req.monte_carlo is None:
        if req.active_corner and project.pvt.get(req.active_corner) is not None:
            project.pvt.active_corner = req.active_corner
            # Explicit corner pick = "simulate at THIS corner": collapse a
            # multi-mode project to single-corner for this one manual sim, so the
            # response's metrics stay flat spec-keyed (the Explorer contract).
            # Without an explicit pick, a multi-mode project sweeps every enabled
            # corner and returns "<corner>::<spec>"-keyed metrics + the aggregate.
            if project.pvt.is_multi():
                warnings.append(
                    f"Corner '{req.active_corner}' requested explicitly — ran single-corner "
                    f"(project default is mode: multi across "
                    f"{len(project.pvt.enabled_corners())} corners)."
                )
                project.pvt.mode = "single"
        elif req.active_corner:
            if project.pvt.is_multi():
                warnings.append(
                    f"Requested corner '{req.active_corner}' not defined; ran all "
                    f"{len(project.pvt.enabled_corners())} enabled corners (mode: multi)."
                )
            else:
                warnings.append(
                    f"Requested corner '{req.active_corner}' not defined; using "
                    f"'{project.pvt.active_corner}'."
                )
        active_corner = project.pvt.active_corner if not project.pvt.is_multi() else None

    # 4 — soft validation (non-fatal)
    _validate_params(project, params, warnings)

    # 5 — run envelope (plan_project_filesystem P3): a manual sim is a first-class
    # `kind: simulate` run — its own run dir (dir == run_id), owner/provenance
    # record, and indexed metrics — via the canonical begin_run/finalize_run seam
    # (shared with the future xschem/tf/gmid/annotate run kinds), instead of an
    # anonymous, never-cleaned scratch/manual_sim/<hex8>. The per-run dir also
    # keeps the BUG-B50 isolation (two overlapping manual sims can never share a
    # wrapper output folder).
    from spicexplorer_api.services import project_service

    project_id, _ = project_service.project_for_yaml(req.yaml_path)
    rdir: Path | None = None
    run_id: str | None = None
    try:
        run_id, rdir = project_service.begin_run(
            "simulate",
            project_id=project_id,
            label="manual sim" + (" · keep_raw" if req.keep_raw else ""),
            input_files={"project_yaml": Path(req.yaml_path)},
            input_values={"params": params, "checkpoint_id": req.checkpoint_id or ""},
            coordinates={"corner": active_corner} if active_corner else None,
            retention="full" if req.keep_raw else "metrics_only",
            # Surfaces the "openable in the waveform viewer" badge on /waveview/runs.
            record_extras={"keep_raw": req.keep_raw},
        )
    except OSError:
        # Bookkeeping must never block the sim itself — degrade to the legacy
        # isolated per-request subfolder under the project outdir, envelope-less.
        rdir = None
        run_id = None
        if req.keep_raw:
            return _fail("keep_raw requires run bookkeeping, which is unavailable.")
        warnings.append("run bookkeeping unavailable — outputs under <outdir>/manual_sim/")

    try:
        if rdir is not None:
            wrappers = _build_spicelib_wrappers(project, output_folder=rdir / "sim")
        else:
            import uuid
            wrappers = _build_spicelib_wrappers(
                project, output_subdir=f"manual_sim/{uuid.uuid4().hex[:8]}")
        opt = Nevergrad_Spice_Single_Objective(setup_obj=project, spicelib_wrappers=wrappers)
        # Same retention flag the optimizer runner sets for keep_raw live runs —
        # evaluate()'s cleanup leaves the per-sim .raw files in place.
        opt.keep_raw_artifacts = req.keep_raw
        try:
            score, fit_summary = opt.evaluate(params, append_to_log=False)
        finally:
            # Bare-evaluate() caller → explicit close (P4): the Spectre path's
            # persistent OCEAN session holds an ADE license token until closed.
            opt.close()
    except Exception as e:
        if rdir is not None:
            project_service.finalize_run(project_id, rdir, status="error", error=str(e))
        return _fail(f"Simulation failed: {e}", params_used=params,
                     active_corner=active_corner, run_id=run_id)

    metrics: dict[str, dict] = {}
    for spec_name, entry in (fit_summary or {}).items():
        if isinstance(entry, dict):
            metrics[spec_name] = {
                "curr_val": _safe_float(entry.get("curr_val")),
                "score": _safe_float(entry.get("score")),
            }
    if rdir is not None:
        # curr_val is already _safe_float'd (float | None); keep only the numeric ones.
        flat = {name: float(m["curr_val"]) for name, m in metrics.items()
                if isinstance(m["curr_val"], (int, float))}
        project_service.finalize_run(
            project_id, rdir, status="done", score=_safe_float(score), metrics=flat)

    # Prefer the evaluation's own per-run log map — in multi-corner mode it is keyed
    # "<tb>__<corner>" and covers EVERY corner, whereas wrapper.curr_log only retains
    # the last corner's log per testbench.
    eval_logs = getattr(opt, "last_eval_log_files", None)
    if eval_logs:
        log_files = {n: str(p) for n, p in eval_logs.items()}
    else:
        # getattr: the Spectre adapter has no `curr_log` (its logs live in the raw dir).
        log_files = {n: str(log) for n, w in wrappers.items()
                     if (log := getattr(w, "curr_log", None)) is not None}
    log_tails = {n: (_tail_log(p)[0] or "") for n, p in log_files.items()}

    return {
        "ok": True,
        "score": _safe_float(score),
        "metrics": metrics,
        "params_used": {k: float(v) for k, v in params.items()},
        "active_corner": active_corner,
        "run_id": run_id,
        "warnings": warnings,
        "log_files": log_files,
        "log_tails": log_tails,
        "error": None,
        "elapsed_ms": (perf_counter() - t_start) * 1000,
        "elapsed_ms_load": elapsed_load,
        "pdk_ok": pdk["pdk_ok"],
        "pdk_detail": pdk["pdk_detail"],
    }


@router.post("/simulate/once", response_model=SimulateOnceResponse)
async def simulate_once(body: SimulateOnceRequest):
    from spicexplorer_api.routes.checkpoint import require_yaml_under_allowed_root

    # Whitelist the caller path (400 if out-of-bounds) and canonicalize it BEFORE the worker
    # loads it — _run_single_sim calls Project_Setup.from_yaml on this, so an unvalidated path
    # is arbitrary-file-read + existence-oracle + error-echo (BUG-B2).
    body.yaml_path = str(require_yaml_under_allowed_root(body.yaml_path))
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_single_sim, body)
    return SimulateOnceResponse(**result)
