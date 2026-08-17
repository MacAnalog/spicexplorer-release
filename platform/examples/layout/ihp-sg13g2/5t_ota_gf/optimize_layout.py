#!/usr/bin/env python3
"""Layout fine-tuning for the gdsfactory-lane 5T OTA: minimize area + PEX error.

Searches the ``LayoutParams`` clearances (gap/channel/rail spacings, wire widths,
strap offsets) with nevergrad. Every candidate goes through the REAL toolchain:

    gen (subprocess) -> KLayout DRC + LVS (hard gate) -> kpex PEX -> ngspice AC

Objective (lower is better), normalized to the hand-tuned baseline:

    score = area/area_0 + ugf_loss/ugf_loss_0        (baseline score = 2.0)

where ``ugf_loss = UGF(pre-layout) - UGF(post-layout)`` is the parasitic error.
DRC/LVS failures score a large penalty — the optimizer only trades *legal* layouts.

Run (ai_env; kpex found via the pex env's bin):

    python optimize_layout.py --budget 30 --out-dir opt_out

Writes one JSONL line per trial + ``best.json``. This is the deterministic core
of the calibrate-by-feedback loop in doc/plan_layout_automation.md.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "5t_ota"))
sys.path.insert(0, os.path.join(HERE, ".."))
from gen_5t_ota_gf import LayoutParams  # noqa: E402
from pex_kpex import run_kpex  # noqa: E402
from signoff import run_drc, run_lvs  # noqa: E402
from sim_pex_compare import run_ac  # noqa: E402

GEN = os.path.join(HERE, "gen_5t_ota_gf.py")
NETLIST = os.path.join(HERE, "ota_5t_gf_lvs.spice")
CELL = "ota_5t_gf"
PEX_BIN = os.path.expanduser("~/miniconda3/envs/pex/bin")
LYP = os.path.join(os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks")),
                   "ihp-sg13g2/libs.tech/klayout/tech/sg13g2.lyp")


def render_png(gds: str, png: str) -> None:
    """Quick visual check: render the GDS with IHP layer colors (headless)."""
    import klayout.lay as klay

    lv = klay.LayoutView()
    lv.load_layout(gds, 0)
    lv.load_layer_props(LYP)
    lv.max_hier_levels = 10
    lv.zoom_fit()
    lv.save_image(png, 1000, 800)

# nevergrad bounds per LayoutParams field (um) — owned by the generator module now
from gen_5t_ota_gf import BOUNDS  # noqa: E402


def evaluate(p: LayoutParams, work: str,
             pre_ugf: float) -> dict[str, object]:
    """One full generate->verify->extract->simulate pass. Returns a result row."""
    work = os.path.abspath(work)
    os.makedirs(work, exist_ok=True)
    gds = os.path.join(work, "ota.gds")
    r = subprocess.run([sys.executable, GEN, "-o", gds,
                        "--params", json.dumps(dataclasses.asdict(p))],
                       capture_output=True, text=True)
    row: dict[str, object] = {"params": dataclasses.asdict(p)}
    if r.returncode != 0 or not os.path.exists(gds):
        row.update(status="gen_fail", score=30.0)
        return row
    area = float(r.stdout.rsplit("area um2:", 1)[1].strip())
    row["area_um2"] = round(area, 1)
    try:
        render_png(gds, os.path.join(work, "layout.png"))
    except Exception:
        pass  # a missing PNG never fails a trial

    drc_ok, _ = run_drc(gds, CELL, os.path.join(work, "drc"))
    lvs_ok, _ = run_lvs(gds, NETLIST, CELL, os.path.join(work, "lvs"))
    row.update(drc=drc_ok, lvs=lvs_ok)
    if not (drc_ok and lvs_ok):
        row.update(status="signoff_fail", score=20.0 + area / AREA0)
        return row

    # mode CC (capacitances only): validated identical UGF loss to RC on this
    # block (wire R is negligible at these dimensions), and it sidesteps kpex's
    # 2.5D R-mesh occasionally leaving a pin node dangling on the tiny gate
    # nets -> singular matrix in ngspice (the sim_fail mode of the RC runs).
    ok, spice, _ = run_kpex(gds, CELL, NETLIST, os.path.join(work, "pex"), mode="CC")
    if not ok:
        row.update(status="pex_fail", score=15.0)
        return row
    try:
        _dc, ugf, pm = run_ac(spice, CELL, "post", work)
    except RuntimeError:
        ugf = None
    if ugf is None:
        row.update(status="sim_fail", score=15.0)
        return row
    loss = (pre_ugf - ugf) / 1e6
    row.update(status="ok", ugf_mhz=round(ugf / 1e6, 3), pm_deg=round(pm or 0, 1),
               ugf_loss_mhz=round(loss, 3),
               score=round(area / AREA0 + max(loss, 0.0) / LOSS0, 4))
    return row


AREA0 = 232.1       # normalization reference: the original hand-tuned layout
LOSS0 = 0.726       # its UGF loss, MHz (LayoutParams defaults are now the optimum)


def main() -> None:
    import nevergrad as ng

    ap = argparse.ArgumentParser(description="fine-tune the gf-lane layout")
    ap.add_argument("--budget", type=int, default=30)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "opt_out"))
    ap.add_argument("--keep-all", action="store_true",
                    help="keep every trial dir (GDS + layout.png + reports), "
                         "not just the best trial's")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    os.environ["PATH"] = PEX_BIN + os.pathsep + os.environ["PATH"]  # kpex
    log = open(os.path.join(a.out_dir, "trials.jsonl"), "a")

    # pre-layout reference (constant across trials)
    _, pre_ugf, _ = run_ac(NETLIST, CELL, "pre", a.out_dir)
    assert pre_ugf is not None

    space = ng.p.Instrumentation(**{
        k: ng.p.Scalar(init=getattr(LayoutParams(), k), lower=lo, upper=hi)
        for k, (lo, hi) in BOUNDS.items()})
    opt = ng.optimizers.TwoPointsDE(parametrization=space, budget=a.budget)
    # seed with the known-good defaults and the RC-run best (opt_out 2026-07-09)
    opt.suggest(**{k: getattr(LayoutParams(), k) for k in BOUNDS})
    opt.suggest(gap_x=1.43, ch_y=0.97, edge_x=1.87, w_m1=0.36, w_m2=0.24,
                tab_w=0.45, ib_off=0.8, vdd_off=1.29, vss_off=1.8)

    best: dict[str, object] = {"score": 99.0}
    for i in range(a.budget):
        cand = opt.ask()
        # snap to a 0.01 um grid: port widths must be an even number of DBU
        p = LayoutParams(**{k: round(v, 2) for k, v in cand.kwargs.items()})
        t0 = time.time()
        work = os.path.join(a.out_dir, f"t{i:03d}")
        row = evaluate(p, work, pre_ugf)
        row.update(trial=i, secs=round(time.time() - t0, 1))
        opt.tell(cand, float(row["score"]))  # type: ignore[arg-type]
        log.write(json.dumps(row) + "\n")
        log.flush()
        marker = ""
        if float(row["score"]) < float(best["score"]):
            best = row
            marker = "  <-- best"
        print(f"[{i:03d}] {row['status']:<12} area={row.get('area_um2', '-'):>6} "
              f"loss={row.get('ugf_loss_mhz', '-'):>6} score={row['score']:<7}"
              f"{marker}", flush=True)
        if not a.keep_all and row is not best:
            shutil.rmtree(work, ignore_errors=True)   # keep only the best trial's dir

    with open(os.path.join(a.out_dir, "best.json"), "w") as f:
        json.dump(best, f, indent=2)
    print(f"\nbaseline: area={AREA0} ugf_loss={LOSS0} score=2.0")
    print(f"best:     {json.dumps(best)}")


if __name__ == "__main__":
    main()
