#!/usr/bin/env python
"""Ax-revival + area/power demo runner.

Sweeps the two demo projects (baseline vs. +area/power) under BOTH optimizer engines
(Nevergrad and Ax Bayesian) on an unsized amplifier, then prints a comparison table of the best
design each run found. Two circuits are wired:

  • amp_029 — the two-stage Miller OTA (the original demo vehicle; succeeded the
    retired amp_020_two_stage_miller_cmfb);
  • amp_008 — the THREE-stage nested-Miller (NMCF) op-amp, a wider 15-knob search space.

`--circuit {amp_029,amp_008,both}` picks the vehicle; `--batch-size N` (Ax only) asks Ax for N
candidates per generation call (N=1 is exact serial parity — the proven path).

Live SPICE (ngspice + ihp-sg13g2 PDK) is required, so run it in the api container / EDA base
image, e.g.:

    docker run --rm \
      -v <worktree>/packages:/app/packages -v <worktree>/examples:/app/examples \
      -w /app spicexplorer-api:ax \
      bash -lc 'python examples/ax_area_power/run_demo.py --circuit amp_008 --budget 10'

Each run resolves its engine from `optimizer_config.type` when launched via the orchestrator
with no explicit `optimizer_type` (the D-1 YAML-driven swap); here we pass the backend
explicitly so ONE process can sweep all four combos.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from spicexplorer.core.domains import Project_Setup
from spicexplorer.optimization.orchestrator import (
    Circuit_Optimizer_Orchestrator_with_SPICE,
    Optimizer_Type_Enum,
    optimizer_type_from_config,
)

HERE = Path(__file__).resolve().parent

# circuit → (baseline yaml, +area/power yaml)
CIRCUITS = {
    "amp_029": (HERE / "amp_029_baseline.yaml", HERE / "amp_029_area_power.yaml"),
    "amp_008": (HERE / "amp_008_baseline.yaml", HERE / "amp_008_area_power.yaml"),
}

ENGINES = {
    "nevergrad": Optimizer_Type_Enum.NEVERGRAD_SINGLE,
    "ax": Optimizer_Type_Enum.AX_SINGLE,
}


def _best_entry(opt):
    """The highest-scoring trial in the (autosave-disabled) log."""
    log = list(opt.optimization_log)
    if not log:
        return None
    return max(log, key=lambda e: float(e.point.score))


def run_one(yaml_path: Path, engine: str, budget: int, sim_outdir: str | None = None,
            parallel_sim: bool | None = None, batch_size: int = 1) -> dict:
    """Run one (project, engine) combo to completion; return a compact result row.

    `sim_outdir` redirects the per-trial ngspice output (default: the YAML's own `outdir`);
    `parallel_sim` overrides the YAML's setting (a bare one-off container without the image
    entrypoint can deadlock the threaded `submit()` path, so the container demo forces
    blocking `run()` with `parallel_sim=False`). `batch_size` (Ax only) asks Ax for that many
    candidates per generation call — 1 is exact serial parity; Nevergrad ignores it."""
    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=str(yaml_path),
        optimizer_type=ENGINES[engine],
        auto_load=False,
        verbose=False,
    )
    if sim_outdir is not None:
        orch.project_setup.outdir = sim_outdir
    if parallel_sim is not None:
        orch.project_setup.parallel_sim = parallel_sim
    oc = orch.project_setup.optimizer_config
    oc.budget = budget  # short demo budget
    # Ax batched generation (no-op for Nevergrad); the kwarg bag is created in __post_init__.
    if oc.optimizer_kwargs is None:
        oc.optimizer_kwargs = {}
    oc.optimizer_kwargs["batch_size"] = batch_size
    orch.initialize()
    opt = orch.get_optimizer()
    opt.disable_autosave = True  # keep the full in-memory log for the summary
    opt.parameterize()
    opt.optimize()

    best = _best_entry(opt)
    metrics: dict = {}
    if best is not None and best.fit_summary:
        for spec, info in best.fit_summary.items():
            if isinstance(info, dict) and "curr_val" in info:
                metrics[spec] = float(info["curr_val"])
    opt.close()
    return {
        "engine": engine,
        "score": float(best.point.score) if best else float("nan"),
        "metrics": metrics,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit", choices=("amp_029", "amp_008", "both"), default="amp_029",
                    help="demo vehicle: amp_029 (2-stage OTA), amp_008 (3-stage NMCF), or both")
    ap.add_argument("--budget", type=int, default=12, help="trials per run (default 12)")
    ap.add_argument("--batch-size", type=int, default=1,
                    help="Ax candidates per generation call (1 = serial parity; Nevergrad ignores)")
    ap.add_argument("--sim-outdir", default="/tmp/sxsim",
                    help="per-trial ngspice output dir (default /tmp/sxsim — keeps a bind-mounted "
                         "examples/ tree clean)")
    ap.add_argument("--parallel-sim", action="store_true",
                    help="use the threaded submit() path (default: blocking run(), container-safe)")
    args = ap.parse_args()

    circuits = list(CIRCUITS) if args.circuit == "both" else [args.circuit]

    # Show the D-1 YAML-driven engine resolution (what a no-optimizer_type launch would pick).
    for circuit in circuits:
        for yaml_path in CIRCUITS[circuit]:
            setup = Project_Setup.from_yaml(yaml_path)
            resolved = optimizer_type_from_config(setup)
            print(f"[engine-swap] {yaml_path.name}: optimizer_config.type="
                  f"{setup.optimizer_config.type!r} -> {resolved.value}")
    if args.batch_size > 1:
        print(f"[ax-batch] Ax generates {args.batch_size} candidates per generation call.")

    rows = []
    for circuit in circuits:
        baseline_yaml, area_power_yaml = CIRCUITS[circuit]
        for label, yaml_path in (("baseline", baseline_yaml), ("area+power", area_power_yaml)):
            for engine in ("nevergrad", "ax"):
                tag = f"{circuit} | {label} | {engine}"
                print(f"\n===== {tag} (budget {args.budget}) =====")
                row = run_one(yaml_path, engine, args.budget,
                              sim_outdir=args.sim_outdir,
                              parallel_sim=(True if args.parallel_sim else False),
                              batch_size=args.batch_size)
                row["label"] = f"{circuit} | {label}"
                rows.append(row)
                print(f"  best score = {row['score']:.4f}")
                for k, v in row["metrics"].items():
                    print(f"    {k:12s} = {v:.4g}")

    # Comparison table
    all_specs: list[str] = []
    for r in rows:
        for k in r["metrics"]:
            if k not in all_specs:
                all_specs.append(k)
    header = f"\n{'run':30s} {'score':>10s} " + " ".join(f"{s:>12s}" for s in all_specs)
    print("\n" + "=" * len(header))
    print("COMPARISON")
    print(header)
    for r in rows:
        cells = " ".join(f"{r['metrics'].get(s, float('nan')):>12.4g}" for s in all_specs)
        print(f"{r['label'] + ' | ' + r['engine']:30s} {r['score']:>10.4f} {cells}")


if __name__ == "__main__":
    main()
