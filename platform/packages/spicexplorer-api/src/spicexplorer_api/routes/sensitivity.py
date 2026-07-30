"""Spec sensitivity route — finite-difference d(metric)/d(param) for one target spec.

For a given target spec this perturbs each requested DUT parameter around a
nominal design point, re-simulates, and reports how the spec's metric responds.
It's the data the Schematic device inspector renders as per-parameter (W/L)
sensitivity bars.

Each perturbation runs a full ``evaluate()`` (all enabled testbenches, ~one
simulation each), so the request cost is ``1 + n_params`` evaluations. Callers
keep it responsive by scoping the sweep with ``?params=`` (e.g. one device's
W + L). The baseline is the centre of each parameter's resolved range; the
``?at=`` query overrides specific parameters (the inspector sends its slider
values there) so the sensitivity is computed at the operating point on screen.

Live SPICE is required — without the IHP PDK this endpoint fails the same way a
live run does (the UI gates it behind ``/api/env``).
"""
from __future__ import annotations

import asyncio
import math
import time
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from spicexplorer_api.app_config import default_yaml_path
from spicexplorer_api.services.num import safe_float as _safe_float

router = APIRouter()


class ParamSensitivity(BaseModel):
    name: str
    device: str
    kind: str  # W | L | NG | bias | other
    nominal: float
    delta: float
    perturbed_value: float
    baseline_metric: float | None = None
    perturbed_metric: float | None = None
    # Absolute slope d(metric)/d(param).
    sensitivity: float | None = None
    # Dimensionless elasticity (dmetric/metric)/(dparam/param) — comparable across params.
    elasticity: float | None = None
    ok: bool = True
    note: str | None = None


class SensitivityResponse(BaseModel):
    ok: bool
    spec: str
    testbench: str | None = None
    goal: str | None = None
    target: float | None = None
    baseline_value: float | None = None
    baseline_score: float | None = None
    rel_delta: float
    n_sims: int
    params: list[ParamSensitivity] = []
    error: str | None = None
    elapsed_ms: float | None = None


def _parse_device_kind(param_name: str) -> tuple[str, str]:
    """Parse a DUT param name into (device, kind).

    'X_DUT_M5_W' -> ('M5', 'W'); 'X_DUT_M5_NG' -> ('M5', 'NG');
    'X_DUT_V_BIAS_1' -> ('V_BIAS_1', 'bias'). The X_DUT_ prefix and the
    convention are not enforced in code, so unknown shapes fall back to 'other'.
    """
    base = param_name
    if base.startswith("X_DUT_"):
        base = base[len("X_DUT_") :]
    if "V_BIAS" in base.upper():
        return base, "bias"
    for suffix, kind in (("_W", "W"), ("_L", "L"), ("_NG", "NG")):
        if base.endswith(suffix):
            return base[: -len(suffix)], kind
    return base, "other"


def _nominal(p) -> float:
    """Nominal absolute-SI value for a DUT param.

    Prefers an explicit val/init; otherwise the centre of the resolved range
    (geometric mean for log-scale params, midpoint of [1,5] etc. for integers).
    """
    for v in (p.val, p.init):
        f = _safe_float(v)
        if f is not None:
            return f
    lo, hi = float(p.min_val), float(p.max_val)
    if p.is_integer:
        return float(round((lo + hi) / 2))
    if p.log_scale and lo > 0 and hi > 0:
        return math.sqrt(lo * hi)
    return 0.5 * (lo + hi)


def _run_sensitivity(
    spec_name: str,
    yaml_path: str,
    rel_delta: float,
    only: list[str] | None,
    overrides: dict[str, float],
) -> dict[str, Any]:
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    # Reuse the exact wrapper-construction the live runner uses, so a sensitivity
    # evaluation simulates the project identically to an optimization step.
    from spicexplorer_api.services.optimizer_runner import _build_spicelib_wrappers

    t0 = time.perf_counter()
    try:
        project = Project_Setup.from_yaml(yaml_path)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "spec": spec_name, "rel_delta": rel_delta, "n_sims": 0,
                "error": f"Failed to load project: {e}"}

    specs = project.optimizer_config.target_specs.targets
    spec = next((s for s in specs if s.name == spec_name), None)
    if spec is None:
        return {"ok": False, "spec": spec_name, "rel_delta": rel_delta, "n_sims": 0,
                "error": f"Spec '{spec_name}' not found. Available: {[s.name for s in specs]}"}

    by_name = {p.name: p for p in project.dut_params}
    bad = [n for n in (list(only or []) + list(overrides)) if n not in by_name]
    if bad:
        return {"ok": False, "spec": spec_name, "rel_delta": rel_delta, "n_sims": 0,
                "error": f"Unknown DUT param(s): {bad}. Available: {list(by_name)}"}

    sweep = [by_name[n] for n in only] if only else list(project.dut_params)

    # Baseline = per-param nominal, with explicit operating-point overrides
    # applied (clamped into each param's resolved range so a hand-crafted ?at=
    # can't push the baseline design outside its bounds).
    baseline = {p.name: _nominal(p) for p in project.dut_params}
    for name, v in overrides.items():
        bp = by_name[name]
        baseline[name] = min(max(v, float(bp.min_val)), float(bp.max_val))

    # Own output subdir so building these wrappers (which rmtree their output_folder) can't
    # wipe a concurrent live run's outdir/live tree (BUG-A8 / OPT-2 — same hole as manual sim).
    wrappers = _build_spicelib_wrappers(project, output_subdir="sensitivity")
    opt = Nevergrad_Spice_Single_Objective(setup_obj=project, spicelib_wrappers=wrappers)

    n_sims = 0
    try:
        base_score, base_fit = opt.evaluate(baseline, append_to_log=False)
    except Exception as e:  # noqa: BLE001
        opt.close()  # P4: bare-evaluate() caller must release the OCEAN session
        return {"ok": False, "spec": spec_name, "rel_delta": rel_delta, "n_sims": n_sims,
                "error": f"Baseline simulation failed: {e}"}
    n_sims += 1
    base_metric = _safe_float(base_fit.get(spec_name, {}).get("curr_val"))

    results: list[dict[str, Any]] = []
    for p in sweep:
        nominal = baseline[p.name]
        lo, hi = float(p.min_val), float(p.max_val)
        if p.is_integer:
            delta = 1.0
        elif nominal != 0:
            delta = rel_delta * abs(nominal)
        else:
            delta = rel_delta * (hi - lo)

        pert = nominal + delta
        if pert > hi:  # near the upper bound → step downward instead
            pert = nominal - delta
        pert = min(max(pert, lo), hi)
        # Recompute delta from the *actual* step taken so the slope below matches
        # the perturbation applied even when the value was clamped to a bound.
        delta = pert - nominal

        device, kind = _parse_device_kind(p.name)
        entry: dict[str, Any] = {
            "name": p.name, "device": device, "kind": kind,
            "nominal": nominal, "delta": delta, "perturbed_value": pert,
            "baseline_metric": base_metric,
        }
        if delta == 0:  # range too small to perturb without leaving bounds
            entry["ok"] = False
            entry["note"] = "parameter range too small to perturb"
            results.append(entry)
            continue
        try:
            perturbed = dict(baseline)
            perturbed[p.name] = pert
            _s, fit = opt.evaluate(perturbed, append_to_log=False)
            n_sims += 1
            m = _safe_float(fit.get(spec_name, {}).get("curr_val"))
            entry["perturbed_metric"] = m
            if base_metric is not None and m is not None and delta != 0:
                entry["sensitivity"] = (m - base_metric) / delta
                if base_metric != 0 and nominal != 0:
                    entry["elasticity"] = ((m - base_metric) / base_metric) / (delta / nominal)
                entry["ok"] = True
            else:
                entry["ok"] = False
                entry["note"] = "spec metric did not converge at this point"
        except Exception as e:  # noqa: BLE001 — one failed perturbation shouldn't kill the sweep
            entry["ok"] = False
            entry["note"] = str(e)
        results.append(entry)

    # Most-influential first (|elasticity|, falling back to |slope|).
    results.sort(key=lambda e: abs(e.get("elasticity") or 0.0) or abs(e.get("sensitivity") or 0.0),
                 reverse=True)
    opt.close()  # P4: bare-evaluate() caller must release the OCEAN session

    return {
        "ok": True,
        "spec": spec_name,
        "testbench": spec.testbench,
        "goal": getattr(spec.goal, "value", str(spec.goal)),
        "target": _safe_float(spec.target),
        "baseline_value": base_metric,
        "baseline_score": _safe_float(base_score),
        "rel_delta": rel_delta,
        "n_sims": n_sims,
        "params": results,
        "elapsed_ms": (time.perf_counter() - t0) * 1000,
    }


def _parse_overrides(at: str | None) -> dict[str, float]:
    """Parse ?at=name:value,name:value into {name: float}."""
    out: dict[str, float] = {}
    if not at:
        return out
    for pair in at.split(","):
        pair = pair.strip()
        if not pair:
            continue
        name, _, raw = pair.partition(":")
        val = _safe_float(raw)
        if not name or val is None:
            raise HTTPException(422, f"Malformed 'at' override: '{pair}' (expected name:value)")
        out[name.strip()] = val
    return out


@router.get("/spec/{name}/sensitivity", response_model=SensitivityResponse)
async def spec_sensitivity(
    name: str,
    yaml_path: str | None = Query(None),
    rel_delta: float = Query(0.05, gt=0, le=0.5, description="perturbation as a fraction of nominal"),
    params: str | None = Query(None, description="comma-separated DUT param names to limit the sweep"),
    at: str | None = Query(None, description="comma-separated name:value baseline overrides (absolute SI)"),
):
    from spicexplorer_api.routes.checkpoint import require_yaml_under_allowed_root

    # Whitelist the caller path (400 if out-of-bounds) before the worker loads it — _run_sensitivity
    # calls Project_Setup.from_yaml on this, so an unvalidated path is arbitrary-file-read +
    # existence-oracle + error-echo (BUG-B2). The default example path is in-bounds.
    path = str(require_yaml_under_allowed_root(yaml_path or str(default_yaml_path())))
    only = [p.strip() for p in params.split(",") if p.strip()] if params else None
    overrides = _parse_overrides(at)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, _run_sensitivity, name, path, rel_delta, only, overrides
    )
    if not result.get("ok"):
        detail = result.get("error") or "sensitivity computation failed"
        is_not_found = "not found" in detail or "Unknown DUT param" in detail
        raise HTTPException(404 if is_not_found else 500, detail)
    return result
