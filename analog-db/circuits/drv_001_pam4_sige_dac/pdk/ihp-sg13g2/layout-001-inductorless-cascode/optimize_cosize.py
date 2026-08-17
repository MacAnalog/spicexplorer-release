#!/usr/bin/env python3
"""Layout-aware sizing loop — JOINT schematic + floorplan co-optimization.

This is the case-study showcase (TCAS-2026): unlike optimize_layout.py, which
tunes only the floorplan at fixed electrical sizing, this driver searches the
SCHEMATIC sizing knobs and the layout floorplan knobs *together*, and scores
every candidate on its POST-EXTRACTION (kpex) metrics — so the schematic and
the physical design are co-optimized against the same extracted netlist.

    schematic sizing knobs            floorplan knobs
    (pdk/../sizing.yaml, shared)      (this layout entry)
              \\                        /
               nevergrad joint search
                        |
      gen_layout  ->  DRC + LVS (HARD GATE)  ->  kpex 2.5D  ->  ngspice .op/.ac
                        |
             score = Σ w_spec·hinge(post-layout spec)  +  w_area·area/area_ref

The ELECTRICAL knobs and their bounds are read from the circuit's
``pdk/ihp-sg13g2/sizing.yaml`` (the single source of truth, per layout.yaml
``knob_map``): x_dut_{nx,re,rc,rb,cdeg_ff} drive LayoutParams geometry;
x_dut_{itail_ma,vcasc,vcm_in} drive the bench operating point (``biases=``).
Structural RF-review floorplan choices (center-fed input, M4 buses, thick TM1
output) are held fixed; the continuous floorplan spacings/widths are searched.

    python optimize_cosize.py --dut pam4 --budget 10 --out-dir cosize_out
    python optimize_cosize.py --dut lsb  --budget 4          # quick sanity

Needs the full toolchain wired (see layout.yaml ``requires``):
    PDK_ROOT, KPEX, KPEX_KLAYOUT_EXE (Ruby>=2.6 KLayout for kpex LVS).
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

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_layout import LayoutParams, FINAL_LAYOUT  # noqa: E402
import pex_sim  # noqa: E402
from signoff import run_drc, run_lvs  # noqa: E402

GEN = os.path.join(HERE, "gen_layout.py")
SIZING_YAML = os.path.normpath(os.path.join(HERE, "..", "sizing.yaml"))

# --- knob_map (mirrors layout.yaml) ----------------------------------------
# sizing.yaml x_dut_*  ->  LayoutParams field (geometry re-derives)
ELECTRICAL_GEOMETRY = {
    "x_dut_nx": "nx", "x_dut_re": "re_ohm", "x_dut_rc": "rc_ohm",
    "x_dut_rb": "rb_ohm", "x_dut_cdeg_ff": "cdeg_ff"}
# sizing.yaml x_dut_*  ->  bench operating point (biases=, not geometry)
ELECTRICAL_BIAS = {
    "x_dut_itail_ma": "tail_ma", "x_dut_vcasc": "vcasc", "x_dut_vcm_in": "vcmb"}
# Golden operating point = sizing.yaml defaults (== datasheet default_conditions).
# An UN-searched bias knob pins here, so a scoped --knobs run keeps a well-defined
# golden baseline (gen_layout.FINAL_BIASES is the manual-review answer, not the start).
GOLDEN_BIASES = {"vcc": 4.0, "vcasc": 3.25, "vcmb": 1.9, "tail_ma": 16.0}

# Continuous floorplan knobs searched here (LayoutParams fields, um). Ranges
# bracket both the LayoutParams defaults and gen_layout.FINAL_LAYOUT.
FLOORPLAN = {
    "gap_x":   (6.0, 10.0),
    "cell_gap": (4.0, 9.0),
    "rc_sep":  (4.0, 14.0),
    "out_off": (1.2, 5.0),
    "in_off":  (1.5, 4.0),
    "re_w":    (4.5, 8.0),
}
# Structural RF-review choices held fixed (qualitative, not continuous) — the
# center-fed H-tree input + M4 buses + thick light TM1 output that make the
# post-layout S11/S22 pass (see LAYOUT_REVIEW.md / gen_layout.FINAL_LAYOUT).
FLOORPLAN_FIXED = dict(
    input_feed="center", in_bus_layer="Metal4", drop_layer="Metal2",
    out_gap=8.0, out_w=1.64, w_out=1.5, stack_w=1.7, in_bus_gap=3.0)

# --- post-layout spec targets (mirror datasheet.yaml `optimize` blocks) -----
# Hinge penalties in each spec's own unit; pex_sim.characterize supplies
# gain / f3dB / worst-S11 / power per drive. S22 and swing are the notebook-03
# driver_lib benches (out of this fast loop) — validated at the final point.
# The pam4 DAC scores BOTH weights (msb + lsb drives); a standalone lsb/msb
# cell scores its own gain against its own LF-S21 floor.
GAIN_TARGET = {"lsb": 2.2, "msb": 8.2}   # datasheet LF-S21 floor per weight


def load_electrical_bounds() -> dict:
    """Read the shared electrical knob bounds from the circuit's sizing.yaml."""
    doc = yaml.safe_load(open(SIZING_YAML))
    out = {}
    for v in doc["variables"]:
        if v["name"] in ELECTRICAL_GEOMETRY or v["name"] in ELECTRICAL_BIAS:
            out[v["name"]] = {"min": float(v["min"]), "max": float(v["max"]),
                              "default": float(v["default"]),
                              "is_integer": bool(v.get("is_integer", False))}
    return out


def build_params(vals: dict) -> LayoutParams:
    """Assemble a LayoutParams from searched electrical-geometry + floorplan
    values (rest = LayoutParams defaults + fixed RF-review structure)."""
    kw = dict(FLOORPLAN_FIXED)
    for sname, field in ELECTRICAL_GEOMETRY.items():
        if sname in vals:
            v = vals[sname]
            kw[field] = int(round(v)) if field == "nx" else round(float(v), 3)
    for fp in FLOORPLAN:
        # searched value if present, else pin to the DRC-clean FINAL geometry
        kw[fp] = round(
            float(vals[fp]) if fp in vals
            else FINAL_LAYOUT.get(fp, getattr(LayoutParams(), fp)), 2)
    # RE rsil width floor: gen_layout needs body length l >= 0.5 um, i.e.
    # w >= (rsh*0.5 + 2*RZ)/re_ohm = 12.5/re_ohm (rsh=7, 2*RZ=9). Clamp the
    # searched re_w so a small re_ohm stays LEGAL (it just costs area) rather
    # than gen-failing — keeps re_ohm and re_w jointly searchable.
    re_ohm = kw.get("re_ohm", LayoutParams().re_ohm)
    kw["re_w"] = max(kw.get("re_w", LayoutParams().re_w),
                     round(12.5 / re_ohm + 0.05, 2))
    return LayoutParams(**kw)


def build_biases(vals: dict) -> dict:
    b = dict(GOLDEN_BIASES)  # unsearched biases pin at golden; vcc frozen at 4.0
    for sname, key in ELECTRICAL_BIAS.items():
        if sname in vals:
            b[key] = round(float(vals[sname]), 3)
    return b


def _spec_terms(res: dict, dut: str) -> tuple[dict, float]:
    """Post-layout spec hinge violations. Returns (viol_by_spec, weighted_total).

    Each term is max(0, shortfall) in the spec's own unit (BW/power scaled to
    ~dB so the weights are comparable); total 0 == every spec met post-extraction.
    """
    viol: dict = {}

    def add(name: str, m: float, goal: str, target: float, w: float,
            norm: float = 1.0) -> float:
        v = (max(0.0, target - m) if goal == "min" else max(0.0, m - target)) / norm
        viol[name] = round(v, 3)
        return w * v

    total = 0.0
    if dut == "pam4":
        post = res["post"]
        total += add("msb_gain_db", post["msb"]["s21_lf_db"],    "min", 8.2,   4.0)
        total += add("lsb_gain_db", post["lsb"]["s21_lf_db"],    "min", 2.2,   2.0)
        total += add("bw_ghz",      post["msb"]["f3db_ghz"],     "min", 50.0,  0.1, 10.0)
        total += add("s11_db",      post["msb"]["s11_worst_db"], "max", -10.0, 2.0)
        total += add("power_mw",    post["msb"]["power_mw"],     "max", 192.0, 0.05, 10.0)
    else:
        d = res["post"]["in"]
        total += add("gain_db",  d["s21_lf_db"],    "min", GAIN_TARGET[dut], 4.0)
        total += add("bw_ghz",   d["f3db_ghz"],     "min", 50.0,  0.1, 10.0)
        total += add("s11_db",   d["s11_worst_db"], "max", -10.0, 2.0)
        total += add("power_mw", d["power_mw"],     "max", 192.0, 0.05, 10.0)
    return viol, round(total, 4)


def evaluate(dut: str, vals: dict, work: str, area_ref: float,
             w_area: float = 0.3) -> dict:
    os.makedirs(work, exist_ok=True)
    lp = build_params(vals)
    biases = build_biases(vals)
    row: dict = {"params": dataclasses.asdict(lp), "biases": biases}
    r = subprocess.run(
        [sys.executable, GEN, "--dut", dut, "--out-dir", work,
         "--params", json.dumps(dataclasses.asdict(lp))],
        capture_output=True, text=True)
    gds = os.path.join(work, f"dut_{dut}.gds")
    if r.returncode != 0 or not os.path.exists(gds):
        return {**row, "status": "gen_fail", "score": 30.0,
                "err": (r.stderr or r.stdout)[-200:]}
    area = float(r.stdout.rsplit("area", 1)[1].split("um2")[0])
    row["area_um2"] = round(area, 0)
    cell = f"pam4drv_{dut}_lay"
    drc_ok, _ = run_drc(gds, cell, os.path.join(work, "drc"))
    lvs_ok, _ = run_lvs(gds, os.path.join(work, f"dut_{dut}_lvs.spice"),
                        cell, os.path.join(work, "lvs"))
    row.update(drc=drc_ok, lvs=lvs_ok)
    if not (drc_ok and lvs_ok):
        return {**row, "status": "signoff_fail", "score": 20.0 + area / area_ref}
    old_out = pex_sim.OUT
    try:
        pex_sim.OUT = work
        res = pex_sim.characterize(dut, mode="CC", biases=biases)
    except Exception as e:  # noqa: BLE001
        return {**row, "status": "pex_or_sim_fail", "score": 15.0,
                "err": str(e)[-200:]}
    finally:
        pex_sim.OUT = old_out
    viol, viol_total = _spec_terms(res, dut)
    feasible = viol_total == 0.0
    score = round(viol_total + w_area * area / area_ref, 4)
    post = {d: res["post"][d] for d in res["post"]}
    return {**row, "status": "ok", "feasible": feasible, "viol": viol,
            "viol_total": viol_total, "post": post, "score": score}


def main() -> None:
    import nevergrad as ng

    ap = argparse.ArgumentParser(description="joint schematic+floorplan co-opt")
    ap.add_argument("--dut", default="pam4", choices=["lsb", "msb", "pam4"])
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "cosize_out"))
    ap.add_argument("--w-area", type=float, default=0.3)
    ap.add_argument(
        "--search", default="joint", choices=["joint", "electrical"],
        help="joint: electrical + floorplan knobs together (broad, DRC-noisy). "
        "electrical: pin the floorplan at the DRC-clean FINAL geometry and search "
        "only the schematic sizing knobs against the extracted metrics (converges).",
    )
    ap.add_argument(
        "--knobs", default=None,
        help="comma-list of sizing knob names to search (subset of sizing.yaml "
        "x_dut_*); the rest pin at their golden default. E.g. the sensitivity-"
        "ranked fix: x_dut_re,x_dut_cdeg_ff,x_dut_itail_ma,x_dut_vcasc",
    )
    ap.add_argument("--keep-all", action="store_true")
    a = ap.parse_args()
    # absolute: pex_sim writes .include paths into decks that ngspice reads from
    # a temp cwd, so a relative out-dir would break the post-layout AC include.
    a.out_dir = os.path.abspath(a.out_dir)
    os.makedirs(a.out_dir, exist_ok=True)
    elec = load_electrical_bounds()

    # search space. `electrical` mode pins nx (a device-count change risks DRC at
    # a fixed floorplan) and pins the whole floorplan at the DRC-clean FINAL
    # geometry, searching only the continuous sizing knobs against the extracted
    # metrics — the layout-aware SIZING loop. `joint` also searches floorplan.
    skip = {"x_dut_nx"} if a.search == "electrical" else set()
    want = set(a.knobs.split(",")) if a.knobs else None  # None = all (minus skip)
    params: dict = {}
    for sname, meta in elec.items():
        if sname in skip or (want is not None and sname not in want):
            continue
        s = ng.p.Scalar(init=meta["default"], lower=meta["min"], upper=meta["max"])
        if meta["is_integer"]:
            s = s.set_integer_casting()
        params[sname] = s
    if a.search == "joint":
        for fp, (lo, hi) in FLOORPLAN.items():
            init = min(max(float(FINAL_LAYOUT.get(fp, getattr(LayoutParams(), fp))), lo), hi)
            params[fp] = ng.p.Scalar(init=init, lower=lo, upper=hi)
    space = ng.p.Instrumentation(**params)

    # baseline: the golden schematic sizing on the RF-reviewed floorplan
    base_vals = {k: params[k].value for k in params}
    log = open(os.path.join(a.out_dir, f"trials_{a.dut}.jsonl"), "a")
    n_fp = len(FLOORPLAN) if a.search == "joint" else 0
    print(f"[cosize {a.dut}] search={a.search}: {len(params)} knobs "
          f"({len(params) - n_fp} electrical from sizing.yaml"
          + (f" + {n_fp} floorplan)" if n_fp else ", floorplan pinned at FINAL)")
          + f"; budget {a.budget}")
    base = evaluate(a.dut, base_vals, os.path.join(a.out_dir, "base"),
                    area_ref=1.0, w_area=a.w_area)
    assert base["status"] == "ok", base
    area_ref = float(base["area_um2"])
    base["score"] = round(base["viol_total"] + a.w_area, 4)  # normalized
    base.update(trial=-1, tag="baseline")
    log.write(json.dumps(base) + "\n"); log.flush()
    print(f"  baseline: area={area_ref} um2 feasible={base['feasible']} "
          f"viol={base['viol']} score={base['score']}")

    opt = ng.optimizers.TwoPointsDE(parametrization=space, budget=a.budget)
    opt.suggest(**base_vals)
    best = dict(base)
    for i in range(a.budget):
        cand = opt.ask()
        vals = dict(cand.kwargs)
        t0 = time.time()
        work = os.path.join(a.out_dir, f"{a.dut}_t{i:03d}")
        row = evaluate(a.dut, vals, work, area_ref=area_ref, w_area=a.w_area)
        row.update(trial=i, secs=round(time.time() - t0, 1))
        opt.tell(cand, float(row["score"]))
        log.write(json.dumps(row) + "\n"); log.flush()
        mark = ""
        if float(row["score"]) < float(best["score"]):
            best = row; mark = "  <-- best"
        gains = ""
        if row["status"] == "ok":
            pm = row["post"].get("msb", row["post"].get("in", {}))
            gains = (f"gain={pm.get('s21_lf_db')} bw={pm.get('f3db_ghz')} "
                     f"s11={pm.get('s11_worst_db')} feas={row['feasible']}")
        print(f"[{i:03d}] {row['status']:<15} area={row.get('area_um2','-')} "
              f"{gains} score={row['score']}{mark}", flush=True)
        if not a.keep_all and row is not best:
            shutil.rmtree(work, ignore_errors=True)

    with open(os.path.join(a.out_dir, f"best_{a.dut}.json"), "w") as f:
        json.dump(best, f, indent=2)
    print(f"\nbest [{a.dut}]: score={best['score']} feasible={best.get('feasible')} "
          f"area={best.get('area_um2')} um2")
    print("  electrical: " + ", ".join(
        f"{k}={best['params'].get(v)}" for k, v in ELECTRICAL_GEOMETRY.items()) +
        ", " + ", ".join(f"{k}={best['biases'].get(v)}" for k, v in ELECTRICAL_BIAS.items()))
    print(f"  -> {os.path.join(a.out_dir, f'best_{a.dut}.json')}")


if __name__ == "__main__":
    main()
