# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---


# %% [markdown]
# # PAM-4 driver — layout generation & sizing with SPICE in the loop
#
# This notebook generates DRC/LVS-clean **gdsfactory layouts** (IHP sg13g2)
# for the three driver DUTs, extracts parasitics with **kpex** (2.5D), and
# closes a sizing loop in which every candidate goes through the *real*
# toolchain:
#
#     LayoutParams -> gen_layout -> KLayout DRC + LVS (hard gate)
#                  -> kpex PEX -> ngspice .op/.ac -> metrics -> score
#
# The search space contains **both** floorplan constants and **electrical
# knobs** (`nx`, `tail_ma`, `rc_ohm`, `rb_ohm`, `cdeg_ff`, `vcasc`) — the
# generator re-derives the GDS *and* all reference netlists from the same
# records, so LVS keeps every candidate honest.
#
# Specs to pass (post-layout) — the FULL set; the first iteration of this
# loop omitted S22 and swing and paid for it (see "The co-optimization
# loop" below):
#
# | metric | spec |
# |---|---|
# | LSB / MSB LF gain | >= 2.2 / >= 8.2 dB |
# | DAC weight (MSB - LSB) | >= 5.0 dB |
# | f3dB (worst path) | >= 50 GHz |
# | S11 (worst port, <= 32 GHz) | <= -10 dB |
# | S22 (<= 50 GHz) | <= -10 dB |
# | max diff swing | >= 2.1 Vpp |
# | power (pam4) | <= 192 mW |

# %%
import sys, os, json, time, shutil, dataclasses
from pathlib import Path
import numpy as np
import yaml
import matplotlib.pyplot as plt
from IPython.display import Image, Markdown, display

ROOT = Path.cwd().resolve().parent          # ported-netlists/
LAY = ROOT / "layout"
sys.path.insert(0, str(LAY))
sys.path.insert(0, str(ROOT / "testbenches"))
import gen_layout, pex_sim, render
from gen_layout import LayoutParams
from signoff import run_drc, run_lvs

def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
    display(Markdown("\n".join(out)))

p0 = LayoutParams()
elec = ["nx", "re_ohm", "rc_ohm", "rb_ohm", "cdeg_ff", "re_w", "rc_w", "rb_w"]
print("electrical knobs :", {k: getattr(p0, k) for k in elec})
print("floorplan knobs  :", {f.name: getattr(p0, f.name)
      for f in dataclasses.fields(p0) if f.name not in elec})

# %% [markdown]
# ## Generate the three DUT layouts (nominal sizing)
#
# One mirror-symmetric gain cell: cascode quad of `npn13G2` PyCells, short
# wide Metal2 plates on the Miller-critical cascode nodes, `rsil` RE (sized
# on the PDK model **including the 4.5 ohm*um contact heads**), center `cmim`
# Cdeg, tails as ports. DUT level: TopMetal1 output buses, TopMetal2 vcc
# rail, Metal3 input buses + rsil RB, p-sub guard ring + inter-cell taps.

# %%
# baseline artifacts go to a notebook-local dir: layout/out holds the FINAL
# signed-off artifacts and must not be clobbered by this baseline run
OUT = str(Path.cwd() / "nb_opt" / "baseline")
for d in ("lsb", "msb", "pam4"):
    gen_layout.generate(d, p0, OUT)
render_dir = Path(OUT)
import render as rd
for d in ("lsb", "msb", "pam4"):
    rd.render(str(render_dir / f"dut_{d}.gds"), str(render_dir / f"dut_{d}.png"))
    display(Markdown(f"**dut_{d}**"))
    display(Image(str(render_dir / f"dut_{d}.png"), width=950))

# %% [markdown]
# ## Physical signoff — KLayout DRC + LVS (PDK decks)

# %%
rows = []
for d in ("lsb", "msb", "pam4"):
    cell = f"pam4drv_{d}_lay"
    drc_ok, _ = run_drc(f"{OUT}/dut_{d}.gds", cell, f"{OUT}/signoff/{d}/drc")
    lvs_ok, _ = run_lvs(f"{OUT}/dut_{d}.gds", f"{OUT}/dut_{d}_lvs.spice",
                        cell, f"{OUT}/signoff/{d}/lvs")
    rows.append((d, "PASS" if drc_ok else "FAIL", "PASS" if lvs_ok else "FAIL"))
md_table(["DUT", "DRC (--no_density)", "LVS"], rows)
assert all(r[1] == r[2] == "PASS" for r in rows)

# %% [markdown]
# ## Baseline: PEX + pre/post-layout comparison (nominal sizing)
#
# *pre* = the layout's exact device set on the PDK models (rsil / cap_cmim /
# npn13G2), no wiring; *post* = + kpex-extracted parasitics (mode CC; the MIM
# cap is re-inserted as a device — kpex's IHP tables cannot extract it).

# %%
base = {}
_old_out = pex_sim.OUT
try:
    pex_sim.OUT = OUT          # notebook-local baseline dir, not layout/out
    for d in ("lsb", "msb", "pam4"):
        base[d] = pex_sim.characterize(d, mode="CC")
finally:
    pex_sim.OUT = _old_out
rows = []
for d, r in base.items():
    for drv in r["pre"]:
        pre, post = r["pre"][drv], r["post"][drv]
        rows.append((f"{d}:{drv}", pre["s21_lf_db"], post["s21_lf_db"],
                     pre["f3db_ghz"], post["f3db_ghz"],
                     pre["s11_worst_db"], post["s11_worst_db"],
                     post["power_mw"]))
md_table(["DUT:path", "S21 pre", "S21 post", "BW pre", "BW post",
          "S11 pre", "S11 post", "P (mW)"], rows)
s11_msb = base["msb"]["post"]["in"]["s11_worst_db"]
s11_p4 = max(base["pam4"]["post"][d]["s11_worst_db"] for d in ("lsb", "msb"))
display(Markdown(
    f"**Nominal sizing FAILS post-layout:** msb S11 = {s11_msb} dB, "
    f"pam4 worst S11 = {s11_p4} dB (spec <= -10 dB); the MSB path also "
    "loses ~16 GHz of bandwidth to parasitics."))

# %% [markdown]
# ## The co-optimization loop — full-spec objective
#
# This loop went through two iterations, and the difference between them is
# the case study's core lesson:
#
# * **v1** scored only S11/BW/gain/power on the msb DUT. It found
#   nx=2 @ 12 mA with R_C = 70 ohm — which the wider signoff (notebook 03)
#   then caught failing **S22** (-8.3 dB) and **max swing** (2.07 Vpp):
#   metrics that were never in the objective silently paid for the ones
#   that were (R_C=70 is -15.6 dB of output mismatch before a single fF).
# * **v2** (this version) scores **all eight specs** on the **pam4** DUT
#   (the summing node, S22, swing and DAC weight only exist there), and the
#   generator carries the RF layout fixes from the expert layout review:
#   center-fed H-tree input buses (Metal4, wide pair gap), Metal2 base-drop
#   descents, light wide-gap TopMetal1 output buses, compacted row. With
#   the input-side parasitics fixed, **the electrical optimum returns to
#   the paper's nominal topology values** (nx=3, R_C=50, R_B~50) with
#   stronger degeneration (R_E 3.2 ohm — series feedback shrinks the
#   effective input C, the last 0.5 dB of S11) and 15 mA tails.
#
# Validity constraints as before: `tail_ma/2 <= 3*nx` (mA/device, the model
# card's stated I_C range) and `re_ohm*re_w >= 12.6` (rsil body floor).

# %%
import driver_lib as dl

ELEC_SPACE = {"nx": (2, 4), "tail_ma": (10.0, 17.0), "rc_ohm": (40.0, 80.0),
              "rb_ohm": (40.0, 60.0), "cdeg_ff": (12.0, 32.0),
              "vcasc": (3.0, 3.4), "re_ohm": (1.2, 3.4),
              "re_w": (4.5, 10.5)}
LAY_SPACE = {"gap_x": (5.5, 9.0), "row_gap": (1.2, 3.0),
             "out_gap": (3.0, 9.0), "rc_sep": (4.0, 16.0)}
# RF layout options fixed at the expert-review configuration (see
# gen_layout.FINAL_LAYOUT): center-fed input H-tree, M4 buses, M2 drops,
# light TM1 out buses, compact row.
RF_FIXED = {k: gen_layout.FINAL_LAYOUT[k]
            for k in ("input_feed", "in_bus_gap", "in_off", "in_bus_layer",
                      "cell_gap", "drop_layer", "out_w", "w_out", "stack_w")}
WORK = Path.cwd() / "nb_opt"
AREA0 = 7550.0


def full_metrics(work: Path, cand: dict) -> dict:
    """kpex + the reusable driver_lib benches on the pam4 DUT -> all 8
    signoff metrics (same benches notebook 03 uses, via `dut_ref=`)."""
    old = pex_sim.OUT
    try:
        pex_sim.OUT = str(work)
        raw = pex_sim.run_kpex("pam4", "CC")
    finally:
        pex_sim.OUT = old
    post = str(work / "dut_pam4_post.spice")
    pex_sim.convert_pex_netlist(raw, post)
    ref = pex_sim.wrap_layout_dut("pam4", post)
    dp = dl.DriverParams(cell=dl.CellParams(
        nx=int(round(cand["nx"])), tail_ma=cand["tail_ma"],
        re_ohm=cand["re_ohm"], cdeg_ff=cand["cdeg_ff"],
        rc_ohm=cand["rc_ohm"], rb_ohm=cand["rb_ohm"], vcasc=cand["vcasc"]))
    m, ac = {}, {}
    for drv in ("lsb", "msb"):
        r = dl.run_ac("pam4", drive=drv, dp=dp, dut_ref=ref, timeout_s=900)
        assert r["ok"], r.get("log", "")[-800:]
        f, s21, s11 = r["f_ghz"], r["s21_db"], r["s11_db"]
        lf = float(s21[np.argmin(np.abs(f - 1.0))])
        thr, f3 = lf - 3.0, float(f[-1])
        for i in range(len(f) - 1):
            if s21[i] >= thr > s21[i + 1]:
                f3 = float(np.interp(thr, [s21[i + 1], s21[i]],
                                     [f[i + 1], f[i]]))
                break
        ac[drv] = (lf, f3, float(s11[f <= 32.0].max()))
    m["lsb_gain"], m["msb_gain"] = round(ac["lsb"][0], 2), round(ac["msb"][0], 2)
    m["weight"] = round(ac["msb"][0] - ac["lsb"][0], 2)
    m["bw"] = round(min(ac["lsb"][1], ac["msb"][1]), 1)
    m["s11"] = round(max(ac["lsb"][2], ac["msb"][2]), 2)
    r22 = dl.run_ac_s22("pam4", dp=dp, dut_ref=ref, timeout_s=900)
    assert r22["ok"], r22.get("log", "")[-800:]
    m["s22"] = round(float(r22["s22_db"][r22["f_ghz"] <= 50.0].max()), 2)
    d = dl.run_dc("pam4", drive="both", vd_max_mv=900.0, step_mv=15.0,
                  dp=dp, dut_ref=ref, timeout_s=900)
    assert d["ok"], d.get("log", "")[-800:]
    m["swing"] = round(float(d["vout_diff_v"].max() - d["vout_diff_v"].min()), 3)
    deck, hold0, _ = dl.tb_bias("pam4", ref, dp=dp,
                                probes=["v(outp)", "i(Vcc)"])
    out, log = dl.run_deck(deck, ["bias.csv"], timeout_s=600)
    data = out["bias.csv"]
    assert data is not None, log[-800:]
    icc = float(np.mean(np.abs(data[data[:, 0] >= hold0 * 1e-9, 3])))
    m["power"] = round(icc * 4.0 * 1e3, 1)
    return m


def evaluate(cand: dict, tag: str) -> dict:
    nx = int(round(cand["nx"]))
    row = {"tag": tag, **{k: (nx if k == "nx" else round(v, 2))
                          for k, v in cand.items()}}
    if cand["tail_ma"] / 2 > 3 * nx:          # I_C validity (mA/device)
        row.update(status="invalid_ic", score=50.0); return row
    if cand["re_ohm"] * cand["re_w"] < 12.6:  # rsil body length floor
        row.update(status="invalid_re", score=50.0); return row
    p = LayoutParams(nx=nx,
                     rc_ohm=round(cand["rc_ohm"], 1),
                     rb_ohm=round(cand["rb_ohm"], 1),
                     cdeg_ff=round(cand["cdeg_ff"], 1),
                     re_ohm=round(cand["re_ohm"], 2),
                     re_w=round(cand["re_w"], 1),
                     **{k: round(cand[k], 2) for k in LAY_SPACE},
                     **RF_FIXED)
    work = WORK / tag
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    try:
        meta = gen_layout.generate("pam4", p, str(work))
    except Exception as e:
        row.update(status="gen_fail", err=str(e)[-150:], score=45.0); return row
    drc_ok, _ = run_drc(f"{work}/dut_pam4.gds", "pam4drv_pam4_lay",
                        f"{work}/drc")
    lvs_ok, _ = run_lvs(f"{work}/dut_pam4.gds", f"{work}/dut_pam4_lvs.spice",
                        "pam4drv_pam4_lay", f"{work}/lvs")
    if not (drc_ok and lvs_ok):
        row.update(status="signoff_fail", score=40.0); return row
    try:
        m = full_metrics(work, cand)
    except Exception as e:
        row.update(status="sim_fail", err=str(e)[-150:], score=30.0); return row
    # hinge penalties on ALL EIGHT specs (v1's blind spots included)
    pen = (3.0 * max(0.0, m["s11"] + 10.0)
           + 3.0 * max(0.0, m["s22"] + 10.0)
           + max(0.0, 50.0 - m["bw"]) / 5.0
           + max(0.0, 8.2 - m["msb_gain"])
           + 2.0 * max(0.0, 2.2 - m["lsb_gain"])
           + 2.0 * max(0.0, 5.0 - m["weight"])
           + 5.0 * max(0.0, 2.1 - m["swing"])
           + max(0.0, m["power"] - 192.0) / 10.0)
    row.update(status="ok", **m, area_um2=meta["area_um2"],
               score=round(pen + 0.2 * meta["area_um2"] / AREA0, 4))
    return row

print("evaluate() ready — one candidate = gen + DRC/LVS + kpex + 5x ngspice")

# %%
import nevergrad as ng
BUDGET = int(os.environ.get("NB_BUDGET", "8"))
FINAL = {"nx": 3, "tail_ma": 15.0, "rc_ohm": 50.0, "rb_ohm": 48.0,
         "cdeg_ff": 16.0, "vcasc": 3.35, "re_ohm": 3.2, "re_w": 4.5,
         "gap_x": 6.0, "row_gap": 1.6, "out_gap": 8.0, "rc_sep": 4.0}
space = ng.p.Instrumentation(
    **{k: ng.p.Scalar(init=FINAL[k], lower=lo, upper=hi)
       for k, (lo, hi) in {**ELEC_SPACE, **LAY_SPACE}.items()})
opt = ng.optimizers.TwoPointsDE(parametrization=space, budget=BUDGET)
# seeds: the directed-search winner (notebook 03's probe ladder) and the
# paper-nominal electrical point on the fixed RF floorplan
opt.suggest(**FINAL)
opt.suggest(nx=3, tail_ma=16.0, rc_ohm=50.0, rb_ohm=50.0, cdeg_ff=20.0,
            vcasc=3.25, re_ohm=2.5, re_w=5.0,
            gap_x=6.0, row_gap=1.6, out_gap=8.0, rc_sep=4.0)

trials, best = [], {"score": 99.0}
for i in range(BUDGET):
    cand = opt.ask()
    t0 = time.time()
    row = evaluate(dict(cand.kwargs), f"t{i:03d}")
    row["secs"] = round(time.time() - t0, 1)
    opt.tell(cand, float(row["score"]))
    trials.append(row)
    mark = ""
    if row["score"] < best["score"]:
        best, mark = row, "  <-- best"
    print(f"[{i:02d}] {row['status']:<13} nx={row['nx']} "
          f"tail={row['tail_ma']} rc={row['rc_ohm']} rb={row['rb_ohm']} "
          f"re={row['re_ohm']} | g={row.get('msb_gain', '-')} "
          f"bw={row.get('bw', '-')} s11={row.get('s11', '-')} "
          f"s22={row.get('s22', '-')} sw={row.get('swing', '-')} "
          f"score={row['score']}{mark}")
    if row is not best:
        shutil.rmtree(WORK / row["tag"], ignore_errors=True)
print("\nbest:", json.dumps(best, indent=1))

# %% [markdown]
# ## Verify the winner on the full PAM-4 system

# %%
bp = LayoutParams(nx=int(best["nx"]), rc_ohm=best["rc_ohm"],
                  rb_ohm=best["rb_ohm"], cdeg_ff=best["cdeg_ff"],
                  re_ohm=best["re_ohm"], re_w=best["re_w"],
                  **{k: best[k] for k in LAY_SPACE}, **RF_FIXED)
vwork = WORK / "pam4_best"
shutil.rmtree(vwork, ignore_errors=True); vwork.mkdir(parents=True)
meta = gen_layout.generate("pam4", bp, str(vwork))
drc_ok, _ = run_drc(f"{vwork}/dut_pam4.gds", "pam4drv_pam4_lay", f"{vwork}/drc")
lvs_ok, _ = run_lvs(f"{vwork}/dut_pam4.gds", f"{vwork}/dut_pam4_lvs.spice",
                    "pam4drv_pam4_lay", f"{vwork}/lvs")
print("pam4 [best]: DRC", "PASS" if drc_ok else "FAIL",
      "| LVS", "PASS" if lvs_ok else "FAIL")
vm = full_metrics(vwork, best)
rd.render(str(vwork / "dut_pam4.gds"), str(vwork / "dut_pam4.png"))
display(Image(str(vwork / "dut_pam4.png"), width=950))

checks = [
    ("LSB LF gain (dB)", vm["lsb_gain"], ">= 2.2", vm["lsb_gain"] >= 2.2),
    ("MSB LF gain (dB)", vm["msb_gain"], ">= 8.2", vm["msb_gain"] >= 8.2),
    ("DAC weight (dB)", vm["weight"], ">= 5.0", vm["weight"] >= 5.0),
    ("f3dB worst path (GHz)", vm["bw"], ">= 50", vm["bw"] >= 50),
    ("S11 worst <= 32G (dB)", vm["s11"], "<= -10", vm["s11"] <= -10),
    ("S22 worst <= 50G (dB)", vm["s22"], "<= -10", vm["s22"] <= -10),
    ("max diff swing (Vpp)", vm["swing"], ">= 2.1", vm["swing"] >= 2.1),
    ("power (mW)", vm["power"], "<= 192", vm["power"] <= 192),
]
md_table(["metric (post-layout, pam4)", "value", "spec", "pass"],
         [(m, v, s, "PASS" if ok else "FAIL") for m, v, s, ok in checks])
all_pass = all(ok for *_, ok in checks)
display(Markdown(f"**ALL 8 SPECS {'PASS' if all_pass else 'NOT met'}** with "
                 f"nx={best['nx']}, tail={best['tail_ma']} mA, "
                 f"rc={best['rc_ohm']} ohm, rb={best['rb_ohm']} ohm, "
                 f"re={best['re_ohm']} ohm, cdeg={best['cdeg_ff']} fF, "
                 f"vcasc={best['vcasc']} V"))

# %% [markdown]
# ## Closing the loop: re-verify the winning sizing at the schematic level
#
# The winner's electrical knobs map 1:1 onto the schematic `CellParams` — so
# the schematic-level characterization (and, when wanted, the transient
# golden method + eye of notebook 01) re-runs directly at the co-optimized
# point. This is the "fine-tune the schematic from layout findings" arrow.

# %%
import driver_lib as dl
from driver_lib import DriverParams, CellParams
cp = CellParams(nx=int(best["nx"]), tail_ma=best["tail_ma"],
                rc_ohm=best["rc_ohm"], rb_ohm=best["rb_ohm"],
                cdeg_ff=best["cdeg_ff"], vcasc=best["vcasc"],
                re_ohm=best["re_ohm"])
dp = DriverParams(cell=cp)

def metrics(r, fmax=32.0):
    f, s21, s11 = r["f_ghz"], r["s21_db"], r["s11_db"]
    lf = s21[np.argmin(np.abs(f - 1.0))]
    thr, f3 = lf - 3.0, f[-1]
    for i in range(len(f) - 1):
        if s21[i] >= thr > s21[i + 1]:
            f3 = np.interp(thr, [s21[i + 1], s21[i]], [f[i + 1], f[i]]); break
    return round(float(lf), 2), round(float(f3), 1),         round(float(s11[f <= fmax].max()), 2)

rows = []
post_gain = {"lsb": vm["lsb_gain"], "msb": vm["msb_gain"]}
for drv in ("lsb", "msb"):
    nom = metrics(dl.run_ac("pam4", drive=drv))
    ret = metrics(dl.run_ac("pam4", drive=drv, dp=dp))
    rows.append((f"pam4:{drv} S21 LF (dB)", nom[0], ret[0], post_gain[drv]))
    rows.append((f"pam4:{drv} S11 (dB)", nom[2], ret[2],
                 vm["s11"] if drv == "msb" else "-"))
s22r = dl.run_ac_s22("pam4", dp=dp)
rows.append(("pam4 S22 worst <= 50G (dB)", "-",
             round(float(s22r["s22_db"][s22r["f_ghz"] <= 50].max()), 2),
             vm["s22"]))
rows.append(("pam4 f3dB worst path (GHz)", "-", "-", vm["bw"]))
rows.append(("pam4 max swing (Vpp)", "-", "-", vm["swing"]))
b = dl.run_bias("pam4", dp=dp)
rows.append(("pam4 power (mW)", "-", round(b["power_mw"], 1), vm["power"]))
rows.append(("V_CE cascode (V, validity 0.4-2.0)", "-",
             round(b.get("vce_q3_msb", float("nan")), 3), "-"))
md_table(["metric", "schematic nominal", "schematic re-tuned",
          "post-layout (winner)"], rows)

# %% [markdown]
# ## Conclusions
#
# - The full **netlist -> layout -> DRC/LVS -> PEX -> post-layout sim** chain
#   is scriptable per candidate (~30-90 s), which makes physical-aware sizing
#   a plain optimization problem.
# - Nominal schematic sizing fails post-layout S11; the fix requires the
#   *electrical* knobs (fewer emitter fingers -> less input C, with gain
#   bought back via R_C / V_casc / tail), not floorplan tweaks alone — the
#   central case-study point for TCAS-2026.
# - The winning sizing re-verifies at the schematic level through the same
#   `CellParams`, closing the loop; the transient golden method and the
#   48 GBaud eye (notebook 01) apply unchanged for final sign-off.
