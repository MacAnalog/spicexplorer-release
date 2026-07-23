#!/usr/bin/env python3
"""Drive the spicexplorer optimizer over an analog-db ``raw/`` export deck for a few loops.

This is the demonstration that the *generated* raw decks — the self-contained
``raw/<circuit>/<pdk>/<analysis>.spice`` files that ``analog-db export-raw`` writes — are
directly optimizable through the spicexplorer DSL, now that each deck's ``.control`` block
ends with ``quit`` (which spicelib's ngspice runner needs to hand the RAW back to the loop).

Each loop asks the optimizer for a candidate sizing, rewrites the deck's ``.param x_dut_*``
knobs, runs ngspice, reads the metric vectors the deck's ``meas``/``let`` block wrote, and
scores them against ``target_specs``. It prints the score + each spec's measured value per
loop so you can watch the search move.

PDK-gated — run where ngspice + the ihp-sg13g2 PDK exist (the api container or the base
image), e.g.:

    docker compose exec -T -w /app/examples/analog-db/raw_optimize api \\
        python run.py amp_001_5t.yaml --loops 12

For a full run (autosave checkpoints + Plotly traces) use ``optimizer.optimize(...)`` instead
(see examples/OTA/.../nevergrad_single_obj_opt.py); this script keeps a bare step loop so the
per-loop numbers are easy to read.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from spicexplorer.optimization.orchestrator import (
    Circuit_Optimizer_Orchestrator_with_SPICE as Orchestrator,
)
from spicexplorer.optimization.orchestrator import Optimizer_Type_Enum
from spicexplorer_core.logging.logger_setup import (
    setup_loggers_with_spicelib_suppression as setup_loggers,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project_setup", type=Path, help="a raw_optimize/*.yaml project setup")
    ap.add_argument("--loops", type=int, default=None,
                    help="number of optimizer steps (default: optimizer_config.budget)")
    # Until 2026-07-20 this runner PINNED the engine to NEVERGRAD_SINGLE, which silently beat
    # the YAML: the orchestrator documents that an explicit `optimizer_type` wins over the DSL,
    # so a project setup carrying `type: bayesian_ax` still ran under NGOpt with no warning.
    # Default is now None = resolve `optimizer_config.type` from the YAML (the shipped configs
    # all carry `type: nevergrad`, so their behavior is unchanged); pass --engine to override.
    ap.add_argument("--engine", choices=["nevergrad", "bayesian_ax"], default=None,
                    help="override the YAML's optimizer_config.type (default: honor the YAML)")
    args = ap.parse_args()
    setup_loggers()

    _ENGINE = {
        "nevergrad": Optimizer_Type_Enum.NEVERGRAD_SINGLE,
        "bayesian_ax": Optimizer_Type_Enum.AX_SINGLE,
    }
    orch = Orchestrator(
        project_setup_path=str(args.project_setup),
        optimizer_type=_ENGINE[args.engine] if args.engine else None,
        auto_load=False,
        verbose=False,
    )
    orch.initialize()
    opt = orch.get_optimizer()
    opt.parameterize()
    opt._create_optimizer_obj()

    ps = orch.project_setup
    loops = args.loops or ps.optimizer_config.budget
    specs = [t.name for t in ps.optimizer_config.target_specs.enabled_targets()]

    print(f"\n=== {ps.name}: {loops} optimization loops over raw/ decks ===")
    print(f"    testbenches: {[tb.name for tb in ps.testbenches if tb.enable]}")
    header = "loop | score      | " + " | ".join(f"{s:>12}" for s in specs)
    print(header)
    print("-" * len(header))

    best_score = -math.inf
    best_meta: dict = {}
    for i in range(1, loops + 1):
        _params, score, meta = opt.optimization_step()
        cells = []
        for s in specs:
            cv = float(meta.get(s, {}).get("curr_val", float("nan")))
            cells.append(f"{cv:12.4g}")
        print(f"{i:4d} | {float(score):10.4g} | " + " | ".join(cells))
        if float(score) > best_score:
            best_score, best_meta = float(score), meta

    print("-" * len(header))
    print(f"best score = {best_score:.4g}")
    print("best-loop measured metrics:")
    any_finite = False
    for s in specs:
        cv = float(best_meta.get(s, {}).get("curr_val", float("nan")))
        any_finite = any_finite or math.isfinite(cv)
        print(f"  {s:>14} = {cv:.6g}")

    ok = math.isfinite(best_score) and any_finite
    print("\nRESULT:", "OK — raw deck optimized (finite metrics extracted)"
          if ok else "FAIL — no finite metrics (deck did not bias / vectors unreadable)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
