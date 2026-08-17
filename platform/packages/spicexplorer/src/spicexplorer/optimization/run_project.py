"""`spicexplorer-optimize` — run ONE project YAML through the orchestrator from the shell.

    uv run spicexplorer-optimize path/to/project_setup.yaml [--budget N] [--workers K]
                                 [--outdir DIR] [--seed S] [--algo NAME] [--quiet]

Engine-agnostic: whatever `sim_engine:` the YAML names (ngspice / spectre / layout) is built
by the backend factory; the optimizer type comes from `optimizer_config.type`. The overrides
are EPHEMERAL (applied in memory, like the API's run-config overrides — the YAML on disk is
never rewritten). Prints the best point + its metrics at the end and returns 0; a project
whose optimizer never produced a trial exits 1.

This is the thin CLI equivalent of `examples/OTA/cascode/ihp-sg13g2/sizing/nevergrad_single_obj_opt.py`
(the reference script) — it exists so an example (e.g. a `sim_engine: layout` project) is
runnable with no per-example driver script.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="spicexplorer-optimize", description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("project_setup", type=Path, help="the project_setup.yaml")
    ap.add_argument("--budget", type=int, default=None, help="override optimizer_config.budget")
    ap.add_argument("--workers", type=int, default=None,
                    help="optimizer_kwargs.num_workers (Nevergrad's batch hint; the trial loop itself is sequential)")
    ap.add_argument("--seed", type=int, default=None, help="override optimizer_config.random_seed")
    ap.add_argument("--algo", default=None, help="override optimizer_config.name (e.g. TwoPointsDE, NGOpt)")
    ap.add_argument("--outdir", default=None,
                    help="override project.outdir (default: <outdir>_<timestamp>, relative to ws_root)")
    ap.add_argument("--no-timestamp", action="store_true", help="keep project.outdir verbatim")
    ap.add_argument("--quiet", action="store_true", help="less orchestrator logging")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = _build_parser().parse_args(argv)
    from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE
    from spicexplorer_core.logging.logger_setup import setup_loggers_with_spicelib_suppression

    setup_loggers_with_spicelib_suppression()
    if a.quiet:
        import logging

        logging.getLogger("spicexplorer").setLevel(logging.WARNING)

    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=a.project_setup, auto_load=False, verbose=not a.quiet
    )
    cfg = orch.project_setup.optimizer_config
    if a.budget is not None:
        cfg.budget = int(a.budget)
    if a.seed is not None:
        cfg.random_seed = int(a.seed)
    if a.algo:
        cfg.name = a.algo
    if a.workers is not None:
        cfg.optimizer_kwargs = {**(cfg.optimizer_kwargs or {}), "num_workers": int(a.workers)}
    if a.outdir:
        orch.project_setup.outdir = Path(os.path.expanduser(a.outdir))
    elif not a.no_timestamp:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        orch.project_setup.outdir = Path(f"{orch.project_setup.outdir}_{ts}")
    orch.initialize()

    opt = orch.get_optimizer()
    opt.parameterize()
    out_root = Path(orch.project_setup.ws_root) / orch.project_setup.outdir
    print(f"[spicexplorer-optimize] {orch.project_setup.name}: engine={orch.project_setup.sim_engine} "
          f"optimizer={cfg.name} budget={cfg.budget}", flush=True)
    print(f"[spicexplorer-optimize] artifacts: {out_root}", flush=True)
    print(f"[spicexplorer-optimize] checkpoints: {opt.autosave_checkpoint_dir}", flush=True)
    opt.optimize(render_optimization_trace=False, keep_history=False)

    best = opt.get_best_params()
    if best is None:
        print("[spicexplorer-optimize] no trial completed", file=sys.stderr)
        return 1
    params, score, _meta = best
    entry = getattr(opt, "global_best_entry", None)
    metrics: dict[str, Any] = {}
    fit_summary = getattr(entry, "fit_summary", None) if entry is not None else None
    if isinstance(fit_summary, dict):
        metrics = {k: (v.get("curr_val") if isinstance(v, dict) else v) for k, v in fit_summary.items()}
    print(f"[spicexplorer-optimize] best score {float(score):.6g}")
    print("[spicexplorer-optimize] best knobs: " + json.dumps({k: float(v) for k, v in params.items()}, default=str))
    if metrics:
        print("[spicexplorer-optimize] best metrics: " + json.dumps(metrics, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
