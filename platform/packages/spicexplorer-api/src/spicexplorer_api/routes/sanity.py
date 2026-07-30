"""Sanity check route — verifies SPICE simulator and runs one trial evaluation."""
from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Bound the per-file log payload so a runaway log doesn't bloat the response.
_LOG_TAIL_LINES = 200
_LOG_TAIL_BYTES = 16 * 1024  # 16 KB cap regardless of line count


class SanityRequest(BaseModel):
    yaml_path: str
    # Optional PVT corner the trial step runs against (must match a corner in the
    # project's `pvt:` block). None keeps the YAML's active_corner.
    active_corner: str | None = None


class TestbenchResult(BaseModel):
    name: str
    ok: bool
    error: str | None = None
    elapsed_ms: float | None = None
    log_path: str | None = None
    log_tail: str | None = None
    log_size_bytes: int | None = None


class TrialResult(BaseModel):
    ok: bool
    score: float | None = None
    metrics: dict[str, float | None] = {}
    error: str | None = None
    elapsed_ms: float | None = None
    log_files: dict[str, str] = {}
    log_tails: dict[str, str] = {}


class SanityResponse(BaseModel):
    ok: bool
    testbenches: list[TestbenchResult]
    trial: TrialResult | None = None
    error: str | None = None
    elapsed_ms_total: float | None = None
    elapsed_ms_load: float | None = None
    elapsed_ms_optimizer_init: float | None = None
    ngspice_path: str | None = None
    # PDK verdict (cheap probe folded in so a sanity run confirms the static /api/env check).
    pdk_ok: bool | None = None
    pdk_detail: str | None = None
    # PVT corner the trial step ran at (None when the project has no `pvt:` block).
    active_corner: str | None = None
    # Non-fatal advisories surfaced to the user — e.g. a requested corner that the project does
    # not define (so the default was used), or that per-testbench rows run at the netlist's
    # hardcoded corner rather than the active PVT corner (BUG-B31/B33).
    warnings: list[str] = []


def _tail_log(path_str: str | Path | None) -> tuple[str | None, int | None]:
    """Return (tail_text, full_size_bytes) for the given log file, or (None, None)."""
    if not path_str:
        return None, None
    p = Path(path_str)
    if not p.exists() or not p.is_file():
        return None, None
    try:
        size = p.stat().st_size
        # Seek-based tail to avoid loading huge files into memory
        with p.open("rb") as f:
            if size > _LOG_TAIL_BYTES:
                f.seek(size - _LOG_TAIL_BYTES)
            chunk = f.read()
        text = chunk.decode("utf-8", errors="replace")
        lines = text.splitlines()
        if len(lines) > _LOG_TAIL_LINES:
            lines = lines[-_LOG_TAIL_LINES:]
        return "\n".join(lines), size
    except OSError:
        return None, None


def _run_sanity(yaml_path: str, active_corner: str | None = None) -> dict[str, Any]:
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer.optimization.simulator_factory import build_simulator, resolve_engine
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective
    from spicexplorer_core.spice_engine import NGSpice_Wrapper, Sim_Execution_Type

    from spicexplorer_api.services.env_probe import probe_pdk

    t_start = time.perf_counter()
    t_load_start = t_start
    # Cheap PDK verdict folded into every return path so the UI can explain a sim
    # failure as "PDK missing" rather than a generic error (this Mac has ngspice but
    # no IHP PDK; on the server both are present).
    pdk = probe_pdk()
    try:
        project = Project_Setup.from_yaml(yaml_path)
    except Exception as e:
        return {
            "ok": False, "testbenches": [], "trial": None,
            "error": f"Failed to load project: {e}",
            "elapsed_ms_total": (time.perf_counter() - t_start) * 1000,
            "pdk_ok": pdk["pdk_ok"],
            "pdk_detail": pdk["pdk_detail"],
        }
    elapsed_ms_load = (time.perf_counter() - t_load_start) * 1000

    # P4: honest engine routing. The per-testbench check below IS ngspice-specific
    # (`run_sanity_check` netlist-checks + sims via the ngspice binary), so a project
    # that selects another engine gets a clear verdict instead of an ngspice error
    # against a `.scs` deck. Spectre projects verify via a live run on a Cadence host.
    engine = resolve_engine(getattr(project, "sim_engine", None))
    if engine.value != "ngspice":
        return {
            "ok": False, "testbenches": [], "trial": None,
            "error": (
                f"sanity-check drives the ngspice lane only; this project selects "
                f"sim_engine='{engine.value}'. Verify it with a live run (POST "
                f"/api/optimize/start) or the opt-in live tests on a Cadence host."
            ),
            "elapsed_ms_total": (time.perf_counter() - t_start) * 1000,
            "elapsed_ms_load": elapsed_ms_load,
            "pdk_ok": pdk["pdk_ok"],
            "pdk_detail": pdk["pdk_detail"],
        }

    # Ephemeral PVT corner override for the trial step (same in-memory, never-rewrite
    # pattern as the live run). The optimizer applies project.pvt.active_corner when
    # constructed below, so setting it here is all that's needed.
    active_corner_used: str | None = None
    warnings: list[str] = []
    if project.pvt is not None:
        if active_corner and project.pvt.get(active_corner) is not None:
            project.pvt.active_corner = active_corner
            # Explicit corner pick = "check at THIS corner": collapse a multi-mode
            # project to single-corner for this request (mirrors /optimize/start and
            # /simulate/once), so the reported active_corner matches what actually ran.
            if project.pvt.is_multi():
                warnings.append(
                    f"Corner '{active_corner}' requested explicitly — the trial step ran "
                    f"single-corner (project default is mode: multi).")
                project.pvt.mode = "single"
        elif active_corner:
            # Requested a corner the project doesn't define — surface it instead of silently
            # falling back and reporting the default as if it were honored (BUG-B31).
            if project.pvt.is_multi():
                warnings.append(
                    f"Requested corner '{active_corner}' is not defined; the trial step ran "
                    f"all {len(project.pvt.enabled_corners())} enabled corners (mode: multi).")
            else:
                warnings.append(
                    f"Requested corner '{active_corner}' is not defined; using "
                    f"'{project.pvt.active_corner}'.")
        if project.pvt.is_multi():
            # No single corner drove the trial — report the sweep instead of pretending
            # the active_corner was honored.
            corner_names = [c.name for c in project.pvt.enabled_corners()]
            warnings.append(
                f"Per-testbench checks run the netlist's hardcoded corner; the trial step "
                f"sweeps the enabled PVT corners {corner_names} (mode: multi, "
                f"score_aggregation: {project.pvt.score_aggregation}).")
        else:
            active_corner_used = project.pvt.active_corner
            # The per-testbench checks below run the netlist as-is (use_editor=False), so the PVT
            # corner is applied ONLY to the trial step — make that explicit (BUG-B33).
            warnings.append(
                f"Per-testbench checks run the netlist's hardcoded corner; the active PVT corner "
                f"'{active_corner_used}' is applied only to the trial step.")

    # Own subdir so the per-wrapper rmtree (NGSpice_Wrapper._validate) can't delete a
    # concurrent live run's outdir/live tree (BUG-A8 / OPT-2).
    output_folder = Path(project.ws_root) / Path(project.outdir) / "sanity"
    path_to_simulator = Path(project.simulator)
    wrappers: dict[str, NGSpice_Wrapper] = {}
    tb_results: list[dict] = []
    all_ok = True

    for tb in project.testbenches:
        if not tb.enable:
            continue
        tb_t0 = time.perf_counter()
        try:
            # P4: constructed through the engine factory (identical NGSpice_Wrapper —
            # the non-ngspice engines early-returned above, so the cast is sound and
            # the ngspice-specific `run_sanity_check` below stays valid).
            wrapper = cast(NGSpice_Wrapper, build_simulator(
                engine,
                testbench_name=tb.name,
                netlist_filename=Path(project.ws_root) / Path(tb.netlist),
                output_folder=output_folder,
                sim_execution_t=Sim_Execution_Type.RUN_AND_WAIT,
                path_to_simulator=path_to_simulator,
            ))
            sim_ok = wrapper.run_sanity_check(
                use_editor=False, sim_execution_t=Sim_Execution_Type.RUN_NOW
            )
            wrappers[tb.name] = wrapper
            tail, size = _tail_log(wrapper.curr_log)
            tb_results.append({
                "name": tb.name,
                "ok": sim_ok,
                "error": None,
                "elapsed_ms": (time.perf_counter() - tb_t0) * 1000,
                "log_path": str(wrapper.curr_log) if wrapper.curr_log else None,
                "log_tail": tail,
                "log_size_bytes": size,
            })
            if not sim_ok:
                all_ok = False
        except Exception as e:
            tb_results.append({
                "name": tb.name,
                "ok": False,
                "error": str(e),
                "elapsed_ms": (time.perf_counter() - tb_t0) * 1000,
                "log_path": None,
                "log_tail": None,
                "log_size_bytes": None,
            })
            all_ok = False

    if not all_ok:
        return {
            "ok": False,
            "testbenches": tb_results,
            "trial": None,
            "error": None,
            "elapsed_ms_total": (time.perf_counter() - t_start) * 1000,
            "elapsed_ms_load": elapsed_ms_load,
            "ngspice_path": str(path_to_simulator),
            "pdk_ok": pdk["pdk_ok"],
            "pdk_detail": pdk["pdk_detail"],
            "active_corner": active_corner_used,
            "warnings": warnings,
        }

    # One trial optimization step to validate the full pipeline
    trial: dict[str, Any] = {"ok": False, "score": None, "metrics": {}, "error": None}
    elapsed_ms_optimizer_init: float | None = None
    try:
        t_init0 = time.perf_counter()
        opt = Nevergrad_Spice_Single_Objective(setup_obj=project, spicelib_wrappers=wrappers)
        try:
            opt.parameterize()
            # _create_optimizer_obj() builds self.optimizer; optimization_step() calls .ask() on it.
            # Skipping this step crashes with "'NoneType' object has no attribute 'ask'".
            if not opt._create_optimizer_obj() or opt.optimizer is None:
                raise RuntimeError(
                    f"Failed to instantiate optimizer '{project.optimizer_config.name}' — "
                    "check that the algorithm name is valid and optimizer_kwargs are accepted."
                )
            elapsed_ms_optimizer_init = (time.perf_counter() - t_init0) * 1000

            trial_t0 = time.perf_counter()
            _params, score, metadata = opt.optimization_step()
            trial_elapsed = (time.perf_counter() - trial_t0) * 1000
        finally:
            # P4: bare single-step caller (no optimize()-managed teardown) — release
            # any engine-side resources deterministically. No-op on the ngspice lane.
            opt.close()

        # NevergradMixin.optimization_step() returns (params, score, fit_summary).
        # fit_summary is a dict keyed by spec name: {spec: {curr_val, score, ...}}.
        metrics: dict[str, float | None] = {}
        if isinstance(metadata, dict):
            for spec_name, entry in metadata.items():
                if isinstance(entry, dict) and entry.get("curr_val") is not None:
                    try:
                        metrics[spec_name] = float(entry["curr_val"])
                    except (TypeError, ValueError):
                        metrics[spec_name] = None
                else:
                    metrics[spec_name] = None

        # Prefer the evaluation's own per-run log map — in multi-corner mode it is
        # keyed "<tb>__<corner>" and covers EVERY corner, whereas wrapper.curr_log
        # only retains the last corner's log (mirrors routes/simulate.py).
        eval_logs = getattr(opt, "last_eval_log_files", None)
        if eval_logs:
            log_files = {n: str(p) for n, p in eval_logs.items()}
        else:
            log_files = {n: str(w.curr_log) for n, w in wrappers.items() if w.curr_log is not None}
        log_tails = {n: (_tail_log(path)[0] or "") for n, path in log_files.items()}

        trial = {
            "ok": True,
            "score": float(score) if score is not None else None,
            "metrics": metrics,
            "error": None,
            "elapsed_ms": trial_elapsed,
            "log_files": log_files,
            "log_tails": log_tails,
        }
    except Exception as e:
        trial = {"ok": False, "score": None, "metrics": {}, "error": str(e),
                 "elapsed_ms": None, "log_files": {}, "log_tails": {}}
        return {
            "ok": False,
            "testbenches": tb_results,
            "trial": trial,
            "error": None,
            "elapsed_ms_total": (time.perf_counter() - t_start) * 1000,
            "elapsed_ms_load": elapsed_ms_load,
            "elapsed_ms_optimizer_init": elapsed_ms_optimizer_init,
            "ngspice_path": str(path_to_simulator),
            "pdk_ok": pdk["pdk_ok"],
            "pdk_detail": pdk["pdk_detail"],
            "active_corner": active_corner_used,
            "warnings": warnings,
        }

    return {
        "ok": True,
        "testbenches": tb_results,
        "trial": trial,
        "error": None,
        "elapsed_ms_total": (time.perf_counter() - t_start) * 1000,
        "elapsed_ms_load": elapsed_ms_load,
        "elapsed_ms_optimizer_init": elapsed_ms_optimizer_init,
        "ngspice_path": str(path_to_simulator),
        "pdk_ok": pdk["pdk_ok"],
        "pdk_detail": pdk["pdk_detail"],
        "active_corner": active_corner_used,
        "warnings": warnings,
    }


@router.post("/sanity-check", response_model=SanityResponse)
async def sanity_check(body: SanityRequest):
    from spicexplorer_api.routes.checkpoint import require_yaml_under_allowed_root

    # Whitelist the caller path (400 if out-of-bounds) before the worker loads it — _run_sanity
    # calls Project_Setup.from_yaml on this, so an unvalidated path is arbitrary-file-read +
    # existence-oracle + error-echo (BUG-B2).
    safe_yaml = str(require_yaml_under_allowed_root(body.yaml_path))
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_sanity, safe_yaml, body.active_corner)
    return SanityResponse(**result)
