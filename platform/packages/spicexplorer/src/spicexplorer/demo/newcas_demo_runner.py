"""NEWCAS cascode OTA demo data bridge.

This module intentionally keeps the UI integration separate from the optimizer
core. It exposes JSON-friendly helpers and a small CLI used by the local
Next.js demo app.
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path
from typing import Any, cast

import pandas as pd
import yaml
from spicexplorer_core import project_root
from spicexplorer_core.env import probe_ngspice

REPO_ROOT = project_root()
CASE_ROOT = REPO_ROOT / "examples" / "OTA" / "cascode"
IHP_ROOT = CASE_ROOT / "ihp-sg13g2"
PROJECT_SETUP_PATH = IHP_ROOT / "sizing" / "project_setup.yaml"
TRACE_ROOT = CASE_ROOT / "NEWCAS_SUBMISSION_APPENDIX"
SCHEMATIC_PATH = IHP_ROOT / "xschem" / "ota-improved.svg"

METRIC_PREFIX = "fit_summary."
METRIC_VALUE_SUFFIX = ".curr_val"
METRIC_SCORE_SUFFIX = ".score"
PARAM_PREFIX = "point.params."


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if pd.isna(value):
        return None
    return value


def _sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_json(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if not isinstance(value, str) and _safe_float(value) is not None:
        return _safe_float(value)
    return value


def emit_json(data: Any) -> None:
    print(json.dumps(_sanitize_json(data), default=_json_default, allow_nan=False), flush=True)


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _safe_value(value: Any) -> Any:
    number = _safe_float(value)
    if number is not None:
        return number
    if value is None or pd.isna(value):
        return None
    return value


def _load_project_yaml() -> dict[str, Any]:
    with PROJECT_SETUP_PATH.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj)

    project = data["project"]
    project["ws_root"] = str(IHP_ROOT)
    return project


def load_demo_config() -> dict[str, Any]:
    project = _load_project_yaml()
    optimizer = project["optimizer_config"]
    targets = optimizer["target_specs"]
    testbenches = project["testbenches"]
    dut_params = project["dut_params"]

    return {
        "project": {
            "name": project["name"],
            "description": project["description"],
            "simulator": project["simulator"],
            "wsRoot": project["ws_root"],
            "netlist": project["netlist"],
            "outdir": project["outdir"],
            "saveSim": project.get("save_sim", False),
            "parallelSim": project.get("parallel_sim", True),
        },
        "technology": project["tech_spec"],
        "dutParams": dut_params,
        "testbenches": testbenches,
        "enabledTestbenches": [tb for tb in testbenches if tb.get("enable", True)],
        "optimizer": {
            "type": optimizer["type"],
            "name": optimizer["name"],
            "budget": optimizer["budget"],
            "randomSeed": optimizer.get("random_seed"),
            "linVariableBounds": optimizer.get("lin_variable_bounds"),
            "logVariableBounds": optimizer.get("log_variable_bounds"),
        },
        "targetSpecs": targets,
        "assets": {
            "schematic": "/api/demo/asset/schematic",
            "projectSetup": str(PROJECT_SETUP_PATH.relative_to(REPO_ROOT)),
            "traceRoot": str(TRACE_ROOT.relative_to(REPO_ROOT)),
        },
    }


def _trace_label(path: Path) -> str:
    label = path.stem.removeprefix("CASCODE-OTA_")
    return label.replace("_", " ")


def _infer_trace_kind(path: Path) -> str:
    name = path.name.lower()
    if "sigmoid" in name:
        return "relative-sigmoid"
    if "relabs" in name or "relativeabs" in name:
        return "relative-absolute"
    return "unknown"


def _count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as file_obj:
        return max(sum(1 for _ in file_obj) - 1, 0)


def list_traces() -> list[dict[str, Any]]:
    traces = []
    for path in sorted(TRACE_ROOT.glob("CASCODE-OTA_*.csv")):
        if path.stem.endswith("_top100"):
            continue
        top_path = path.with_name(f"{path.stem}_top100.csv")
        traces.append(
            {
                "id": path.stem,
                "label": _trace_label(path),
                "file": str(path.relative_to(REPO_ROOT)),
                "rows": _count_csv_rows(path),
                "scoreShape": _infer_trace_kind(path),
                "hasTop100": top_path.exists(),
            }
        )
    return traces


def _resolve_trace(trace_id: str) -> Path:
    candidates = {path.stem: path for path in TRACE_ROOT.glob("CASCODE-OTA_*.csv")}
    if trace_id not in candidates or candidates[trace_id].stem.endswith("_top100"):
        raise FileNotFoundError(f"Unknown demo trace: {trace_id}")
    return candidates[trace_id]


def _metric_names(columns: list[str]) -> list[str]:
    names = []
    for column in columns:
        if column.startswith(METRIC_PREFIX) and column.endswith(METRIC_VALUE_SUFFIX):
            names.append(column[len(METRIC_PREFIX) : -len(METRIC_VALUE_SUFFIX)])
    return names


def _param_names(columns: list[str]) -> list[str]:
    return [column[len(PARAM_PREFIX) :] for column in columns if column.startswith(PARAM_PREFIX)]


def load_trace(trace_id: str, limit: int | None = None) -> dict[str, Any]:
    path = _resolve_trace(trace_id)
    frame = pd.read_csv(path)
    if limit is not None and limit > 0:
        frame = frame.head(limit)

    metrics = _metric_names(list(frame.columns))
    params = _param_names(list(frame.columns))
    rows = []
    best_score: float | None = None
    best_index = 0

    for index, row in frame.iterrows():
        score = _safe_float(row.get("point.score"))
        if score is not None and (best_score is None or score > best_score):
            best_score = score
            best_index = int(cast(int, index))

        row_metrics = {
            metric: {
                "value": _safe_value(row.get(f"{METRIC_PREFIX}{metric}{METRIC_VALUE_SUFFIX}")),
                "score": _safe_value(row.get(f"{METRIC_PREFIX}{metric}{METRIC_SCORE_SUFFIX}")),
            }
            for metric in metrics
        }
        row_params = {
            param: _safe_value(row.get(f"{PARAM_PREFIX}{param}"))
            for param in params
        }
        rows.append(
            {
                "index": int(cast(int, index)),
                "score": score,
                "bestScore": best_score,
                "metrics": row_metrics,
                "params": row_params,
            }
        )

    top_candidates = sorted(
        rows,
        key=lambda item: item["score"] if item["score"] is not None else -math.inf,
        reverse=True,
    )[:10]

    return {
        "id": path.stem,
        "label": _trace_label(path),
        "file": str(path.relative_to(REPO_ROOT)),
        "scoreShape": _infer_trace_kind(path),
        "metrics": metrics,
        "params": params,
        "rows": rows,
        "rowCount": len(rows),
        "bestIndex": best_index,
        "bestScore": best_score,
        "topCandidates": top_candidates,
    }


def _patched_project_setup(budget: int) -> Path:
    project = _load_project_yaml()
    project["optimizer_config"]["budget"] = budget
    project["save_sim"] = False
    project["parallel_sim"] = False

    temp_dir = Path(tempfile.mkdtemp(prefix="spicexplorer-newcas-"))
    yaml_path = temp_dir / "project_setup.yaml"
    with yaml_path.open("w", encoding="utf-8") as file_obj:
        yaml.safe_dump({"project": project}, file_obj, sort_keys=False)
    return yaml_path


def run_live_demo(budget: int) -> int:
    if not probe_ngspice()["ngspice_ok"]:
        emit_json(
            {
                "type": "unavailable",
                "message": "NGSpice was not found on PATH. Replay mode remains available.",
            }
        )
        return 0

    try:
        from spicexplorer.optimization.orchestrator import (
            Circuit_Optimizer_Orchestrator_with_SPICE,
            Optimizer_Type_Enum,
        )
        from spicexplorer_core.logging.logger_setup import (
            setup_loggers_with_spicelib_suppression as setup_loggers,
        )

        setup_loggers()
        yaml_path = _patched_project_setup(budget=budget)
        orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
            project_setup_path=yaml_path,
            optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
            auto_load=True,
            verbose=False,
        )
        optimizer = orchestrator.get_optimizer()
        optimizer.disable_autosave = True
        optimizer.parameterize()
        optimizer._create_optimizer_obj()

        emit_json({"type": "started", "budget": budget})
        for trial in range(budget):
            candidate, score, metadata = optimizer.optimization_step()
            emit_json(
                {
                    "type": "trial",
                    "trial": trial + 1,
                    "budget": budget,
                    "score": _safe_value(score),
                    "candidate": candidate,
                    "metrics": metadata,
                }
            )
        emit_json({"type": "completed", "budget": budget})
        return 0
    except Exception as exc:  # pragma: no cover - depends on local simulator stack
        emit_json({"type": "error", "message": f"{exc.__class__.__name__}: {exc}"})
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEWCAS demo data bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("config")
    subparsers.add_parser("traces")

    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("trace_id")
    trace_parser.add_argument("--limit", type=int, default=None)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--budget", type=int, default=8)

    args = parser.parse_args(argv)
    if args.command == "config":
        emit_json(load_demo_config())
    elif args.command == "traces":
        emit_json(list_traces())
    elif args.command == "trace":
        emit_json(load_trace(args.trace_id, limit=args.limit))
    elif args.command == "run":
        return run_live_demo(budget=max(1, min(args.budget, 50)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
