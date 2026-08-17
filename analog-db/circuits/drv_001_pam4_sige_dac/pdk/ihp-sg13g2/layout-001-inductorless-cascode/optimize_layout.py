#!/usr/bin/env python3
"""In-loop layout optimization for the PAM-4 driver DUTs.

Searches the `LayoutParams` floorplan constants with nevergrad; every
candidate goes through the REAL toolchain:

    gen_layout (subprocess) -> KLayout DRC + LVS (hard gate)
                            -> kpex 2.5D PEX -> ngspice .op/.ac

Objective (lower is better), normalized to the committed default layout:

    score = area/area_0 + bw_loss/bw_loss_0

where ``bw_loss = f3dB(pre) - f3dB(post)`` is the parasitic bandwidth
penalty of the driven path (msb path for the pam4 DUT). DRC/LVS failures
score a large penalty, so the optimizer only ever trades *legal* layouts.

    python optimize_layout.py --dut lsb --budget 20 --out-dir opt_out

Same pattern as examples/layout/ihp-sg13g2/5t_ota_gf/optimize_layout.py
(the 5T-OTA lane), retargeted at the HBT driver and its bandwidth metric.
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
sys.path.insert(0, HERE)
from gen_layout import LayoutParams  # noqa: E402
import pex_sim  # noqa: E402
from signoff import run_drc, run_lvs  # noqa: E402

GEN = os.path.join(HERE, "gen_layout.py")

# search space: the spacings that trade area against coupling/loading, plus
# the resistor widths. Lengths always re-derive from the rsil model
# (R = 7*l/w + 2*4.5/w) inside gen_layout, so the resistance target holds
# for every candidate — only geometry/area/parasitics change. Lower width
# bounds respect the model's l >= 0.5 um floor (res_len raises otherwise);
# mind EM at the narrow end: RE carries 16 mA/cell, RC up to 24 mA.
BOUNDS: dict[str, tuple[float, float]] = {
    "gap_x": (6.2, 10.0),      # pair gap (Cdeg + clearances live here)
    "row_gap": (1.0, 4.0),     # input row <-> cascode row
    "cell_gap": (4.0, 9.0),    # cell pitch (pam4/msb only)
    "re_gap": (0.8, 3.0),
    "out_off": (1.2, 5.0),     # sub bus -> output buses
    "out_gap": (1.8, 5.0),     # outp <-> outn bus gap
    "out_w": (2.0, 5.0),       # output bus width (TM1)
    "w_out": (1.5, 4.0),       # output riser width (M2)
    "in_off": (1.0, 4.0),
    "rc_sep": (8.0, 20.0),
    "sub_off": (1.0, 3.0),
    # resistor widths (um): l follows from the PDK rsil model
    "re_w": (4.5, 8.0),        # 2.5 ohm needs w >= 4.43 (l floor)
    "rc_w": (1.0, 3.0),        # 50 ohm: l = (50w-9)/7 -> 8.7 um at w=1.4
    "rb_w": (0.5, 1.5),
}


def evaluate(dut: str, p: LayoutParams, work: str, pre_bw: float,
             area0: float, loss0: float, w_area: float = 1.0,
             w_s11: float = 1.0, s11_spec: float = -10.0) -> dict:
    os.makedirs(work, exist_ok=True)
    r = subprocess.run(
        [sys.executable, GEN, "--dut", dut, "--out-dir", work,
         "--params", json.dumps(dataclasses.asdict(p))],
        capture_output=True, text=True)
    row: dict = {"params": dataclasses.asdict(p)}
    gds = os.path.join(work, f"dut_{dut}.gds")
    if r.returncode != 0 or not os.path.exists(gds):
        row.update(status="gen_fail", score=30.0)
        return row
    area = float(r.stdout.rsplit("area", 1)[1].split("um2")[0])
    row["area_um2"] = round(area, 0)
    cell = f"pam4drv_{dut}_lay"
    drc_ok, _ = run_drc(gds, cell, os.path.join(work, "drc"))
    lvs_ok, _ = run_lvs(gds, os.path.join(work, f"dut_{dut}_lvs.spice"),
                        cell, os.path.join(work, "lvs"))
    row.update(drc=drc_ok, lvs=lvs_ok)
    if not (drc_ok and lvs_ok):
        row.update(status="signoff_fail", score=20.0 + area / area0)
        return row
    # PEX + post-layout AC on the trial dir
    old_out = pex_sim.OUT
    try:
        pex_sim.OUT = work
        res = pex_sim.characterize(dut, mode="CC")
    except Exception as e:  # noqa: BLE001
        row.update(status="pex_or_sim_fail", err=str(e)[-300:], score=15.0)
        return row
    finally:
        pex_sim.OUT = old_out
    drv = "msb" if dut == "pam4" else "in"
    loss = res["pre"][drv]["f3db_ghz"] - res["post"][drv]["f3db_ghz"]
    # S11 spec term: hinge penalty in dB above the spec line (post-layout,
    # worst path). No reward for over-margin — only violations cost.
    s11_post = max(res["post"][d]["s11_worst_db"] for d in res["post"])
    s11_viol = max(0.0, s11_post - s11_spec)
    row.update(status="ok",
               f3db_pre=res["pre"][drv]["f3db_ghz"],
               f3db_post=res["post"][drv]["f3db_ghz"],
               bw_loss_ghz=round(loss, 2),
               s11_post_db=round(s11_post, 2),
               s11_viol_db=round(s11_viol, 2),
               score=round(w_area * area / area0
                           + max(loss, 0.0) / loss0
                           + w_s11 * s11_viol, 4))
    return row


def main() -> None:
    import nevergrad as ng

    ap = argparse.ArgumentParser(description="layout fine-tuning loop")
    ap.add_argument("--dut", default="lsb",
                    choices=["lsb", "msb", "pam4"])
    ap.add_argument("--budget", type=int, default=20)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "opt_out"))
    ap.add_argument("--keep-all", action="store_true")
    ap.add_argument("--w-area", type=float, default=1.0,
                    help="area-term weight (score = w_area*area/area0 "
                         "+ bw_loss/loss0 + w_s11*max(0, S11-spec))")
    ap.add_argument("--w-s11", type=float, default=1.0,
                    help="weight per dB of post-layout S11 spec violation")
    ap.add_argument("--s11-spec", type=float, default=-10.0,
                    help="S11 spec line in dB (worst path, <= 32 GHz)")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    log = open(os.path.join(a.out_dir, f"trials_{a.dut}.jsonl"), "a")

    # baseline: the committed defaults
    base = os.path.join(a.out_dir, "base")
    row0 = evaluate(a.dut, LayoutParams(), base,
                    pre_bw=0.0, area0=1.0, loss0=1.0,
                    w_area=a.w_area, w_s11=a.w_s11, s11_spec=a.s11_spec)
    assert row0["status"] == "ok", row0
    area0 = float(row0["area_um2"])
    loss0 = max(float(row0["bw_loss_ghz"]), 0.5)
    print(f"baseline [{a.dut}]: area={area0} um2, bw_loss={loss0} GHz, "
          f"S11(post)={row0.get('s11_post_db')} dB "
          f"(spec {a.s11_spec} dB; baseline score = "
          f"{1.0 + a.w_area + a.w_s11 * float(row0.get('s11_viol_db', 0)):.2f})")

    space = ng.p.Instrumentation(**{
        k: ng.p.Scalar(init=getattr(LayoutParams(), k), lower=lo, upper=hi)
        for k, (lo, hi) in BOUNDS.items()})
    opt = ng.optimizers.TwoPointsDE(parametrization=space, budget=a.budget)
    opt.suggest(**{k: getattr(LayoutParams(), k) for k in BOUNDS})

    best: dict = {"score": 99.0}
    for i in range(a.budget):
        cand = opt.ask()
        p = LayoutParams(**{k: round(v, 2) for k, v in cand.kwargs.items()})
        t0 = time.time()
        work = os.path.join(a.out_dir, f"{a.dut}_t{i:03d}")
        row = evaluate(a.dut, p, work, 0.0, area0, loss0, w_area=a.w_area,
                       w_s11=a.w_s11, s11_spec=a.s11_spec)
        row.update(trial=i, secs=round(time.time() - t0, 1))
        opt.tell(cand, float(row["score"]))
        log.write(json.dumps(row) + "\n")
        log.flush()
        marker = ""
        if float(row["score"]) < float(best["score"]):
            best = row
            marker = "  <-- best"
        print(f"[{i:03d}] {row['status']:<16} area={row.get('area_um2', '-')} "
              f"bw_loss={row.get('bw_loss_ghz', '-')} "
              f"s11={row.get('s11_post_db', '-')} "
              f"score={row['score']}{marker}", flush=True)
        if not a.keep_all and row is not best:
            shutil.rmtree(work, ignore_errors=True)

    with open(os.path.join(a.out_dir, f"best_{a.dut}.json"), "w") as f:
        json.dump(best, f, indent=2)
    print(f"best: {json.dumps(best)}")


if __name__ == "__main__":
    main()
