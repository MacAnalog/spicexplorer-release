"""Live ``ungroup:`` re-sizing demo on amp_022 — the parameterization layer, end-to-end.

The notebook ``notebooks/ungroup_resizing.ipynb`` is the guided counterpart; this script is
the reusable engine both it and a CI smoke can call. It runs TWO short, seeded live ngspice
optimizations over amp_022's committed ihp-sg13g2 decks:

  (a) TIED     — the shipped ties intact: a curated low-dim GROUP-addressed search
                 (``input_pair.w`` etc. resolve to the group's first-member atomic symbol).
                 The mirror-load width knob ``x_dut_xm3_w`` drives XM3, XM4 AND XM2 together
                 (the ``stage2_load_width`` shared_geometry tie: ``.param x_dut_xm2_w={x_dut_xm3_w}``).
  (b) UNGROUPED — same projection + ``ungroup: [stage2_load_width]`` dissolving that one tie,
                 plus ``x_dut_xm2_w`` promoted to its own free knob. The 2nd-stage CS device's
                 width is now searched INDEPENDENT of the mirror load. Search space gains
                 exactly one dimension.

This is a DEMONSTRATION of the affordance (tens of trials, a few minutes) — NOT an
optimization campaign. Numbers are REAL (live ngspice), seeded for reproducibility.

Run (native research server):
    PATH=/home/.../local/bin:$PATH PDK_ROOT=/home/.../local/pdks \\
        $VENV/bin/python raw_optimize/ungroup_demo.py
"""

from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

# quiet the optimizer's chatty INFO stream — we print our own summary.
logging.disable(logging.INFO)

HERE = Path(__file__).resolve().parent          # raw_optimize/
BASE_YAML = HERE / "amp_022_ungroup_demo.yaml"   # the hand-authored curated projection
PARAMS_YAML = "circuits/amp_022_fer_two_stage/abstract/params.yaml"
DECK = "raw/amp_022_fer_two_stage/ihp-sg13g2/ac_open_loop.spice"

# The one tie the demo argues is worth freeing: the legacy x_nload_w opinion tying the
# 2nd-stage CS device (XM2) width to the stage-1 mirror-load width (XM3). Freeing it lets
# the 2nd stage set its own gm/output-swing without disturbing the mirror.
DISSOLVE = "stage2_load_width"
FREED_SYMBOL = "x_dut_xm2_w"      # XM2 width — the symbol the tie shadows
FREED_BOUNDS = {"min_val": "3u", "max_val": "12u"}

# The metrics we report (the deck's own meas/let vectors).
METRICS = ["dcgain", "ugf", "pm", "i(i_supply)"]


def _free_and_frozen(project) -> tuple[list[str], list[tuple[str, Any]]]:
    free = [d.name for d in project.dut_params if not d.freeze]
    frozen = [(d.name, d.val) for d in project.dut_params if d.freeze]
    return free, frozen


def load_projection(*, ungroup: bool) -> dict:
    """The base curated projection dict, optionally with the stage2_load_width tie dissolved."""
    data = yaml.safe_load(BASE_YAML.read_text())
    if ungroup:
        proj = data["project"]
        proj["ungroup"] = [DISSOLVE]
        # promote the freed symbol to its OWN free knob (bounds = a band around its 6u default).
        proj["dut_params"] = deepcopy(proj["dut_params"]) + [{"name": FREED_SYMBOL, **FREED_BOUNDS}]
    return data


def _write_variant(data: dict, name: str) -> Path:
    """Write a projection variant next to the base YAML so its `ws_root: ..` still resolves."""
    out = HERE / f"_demo_{name}.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False))
    return out


def resolved_dims(*, ungroup: bool) -> dict:
    """Load the projection through the platform and report the resolved dimensionality.

    Returns {free, frozen, params_file source, dissolved shadow symbols}. No simulation —
    this is the STATIC half of the story (the search space before/after ungroup).
    """
    from spicexplorer.backends.params import (
        load_params_file,
        netlist_param_defaults,
        shadow_params,
    )
    from spicexplorer.core.domains import Project_Setup

    data = load_projection(ungroup=ungroup)
    variant = _write_variant(data, "ungrouped_dims" if ungroup else "tied_dims")
    try:
        proj = Project_Setup.from_yaml(variant)
    finally:
        variant.unlink(missing_ok=True)
    free, frozen = _free_and_frozen(proj)

    # what the PURE ungroup would shadow (independent of the free-knob promotion) — the
    # "dissolved symbols" the affordance exposes.
    cp = load_params_file(Path(proj.ws_root) / PARAMS_YAML)
    deck_defaults = netlist_param_defaults(Path(proj.ws_root) / DECK)
    shadow = shadow_params(cp, [DISSOLVE], deck_defaults) if ungroup else {}
    return {"free": free, "frozen": frozen, "shadow": shadow, "ws_root": proj.ws_root}


def run_optimization(*, ungroup: bool) -> dict:
    """Run ONE short seeded live optimization; return best params + best metrics + n trials."""
    import os

    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE as Orch,
    )
    from spicexplorer.optimization.orchestrator import Optimizer_Type_Enum

    # Keep the committed notebook output clean: the optimizer wraps its loop in a tqdm bar that
    # writes many carriage-return frames to stderr. TQDM_DISABLE silences it without touching the
    # optimizer code (the numbers are unaffected).
    os.environ.setdefault("TQDM_DISABLE", "1")

    data = load_projection(ungroup=ungroup)
    label = "ungrouped" if ungroup else "tied"
    # give each run its own outdir so parallel scratch dirs don't collide.
    data["project"]["outdir"] = f"raw_optimize/_runs/amp_022_ungroup_demo_{label}"
    variant = _write_variant(data, label)
    try:
        orch = Orch(str(variant), Optimizer_Type_Enum.NEVERGRAD_SINGLE, auto_load=False, verbose=False)
        orch.initialize()
        opt = orch.get_optimizer()
        opt.parameterize()
        # Keep autosave checkpoints inside the gitignored scratch outdir (default is a
        # CWD-relative ./auto_save/, which would scatter JSON into notebooks/ when the demo
        # runs from a notebook). Resolve against the project's own outdir.
        opt.autosave_checkpoint_dir = (
            Path(opt.setup_obj.ws_root) / opt.setup_obj.outdir / "auto_save"
        )
        opt.optimize(render_optimization_trace=False, keep_history=False)
        best = opt.get_best_params(verbose=False)
    finally:
        variant.unlink(missing_ok=True)

    best_params, best_score, _meta = best
    # de-normalize the best point and re-read its metrics from the best log entry's fit_summary.
    entry = opt.global_best_entry
    metrics = {m: (entry.fit_summary.get(m, {}) or {}).get("curr_val") for m in METRICS}
    denorm = opt.denormalize_params(best_params)
    n_trials = len(opt.optimization_log)
    free = [d.name for d in opt.setup_obj.dut_params if not d.freeze]
    return {
        "label": label,
        "n_trials": n_trials,
        "n_free": len(free),
        "free": free,
        "best_score": float(best_score),
        "best_params": {k: float(v) for k, v in denorm.items()},
        "metrics": metrics,
    }


def _fmt_metrics(m: dict) -> str:
    def g(k):
        v = m.get(k)
        return "n/a" if v is None else v
    return (f"dcgain={g('dcgain'):>7} dB  ugf={g('ugf'):>12} Hz  "
            f"pm={g('pm'):>7} deg  i_supply={g('i(i_supply)')} A")


def main() -> int:
    import time

    from spicexplorer_core.env import probe_env

    env = probe_env()
    print("=== live-SPICE env ===")
    print(f"  ngspice_ok={env['ngspice_ok']}  pdk_ok={env['pdk_ok']}  "
          f"live_runs_enabled={env['live_runs_enabled']}  tech={env.get('tech')}")
    if not env["live_runs_enabled"]:
        print("  live runs unavailable — this demo needs ngspice + ihp-sg13g2. Skipping.")
        return 0

    print("\n=== STATIC: dimensionality before/after ungroup ===")
    tied_d = resolved_dims(ungroup=False)
    ung_d = resolved_dims(ungroup=True)
    print(f"  (a) tied      : {len(tied_d['free'])} free knobs  {tied_d['free']}")
    print(f"  (b) ungrouped : {len(ung_d['free'])} free knobs  {ung_d['free']}")
    print(f"  dissolved tie '{DISSOLVE}' shadow symbols: {ung_d['shadow']}")
    print(f"  Δ dimension   : +{len(ung_d['free']) - len(tied_d['free'])} "
          f"({FREED_SYMBOL} freed from x_dut_xm3_w)")

    print("\n=== LIVE: two short seeded optimizations ===")
    t0 = time.time()
    tied = run_optimization(ungroup=False)
    t1 = time.time()
    ung = run_optimization(ungroup=True)
    t2 = time.time()

    print(f"\n  (a) tied      [{tied['n_trials']} trials, {t1 - t0:.0f}s, {tied['n_free']} knobs]  "
          f"score={tied['best_score']:.4f}")
    print(f"        {_fmt_metrics(tied['metrics'])}")
    print(f"  (b) ungrouped [{ung['n_trials']} trials, {t2 - t1:.0f}s, {ung['n_free']} knobs]  "
          f"score={ung['best_score']:.4f}")
    print(f"        {_fmt_metrics(ung['metrics'])}")
    print(f"        best x_dut_xm2_w = {ung['best_params'].get(FREED_SYMBOL)} "
          f"(vs tied, where it tracks x_dut_xm3_w = {tied['best_params'].get('x_dut_xm3_w')})")
    print(f"\n  total runtime: {t2 - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
