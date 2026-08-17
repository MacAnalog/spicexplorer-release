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
# # PAM-4 driver — full signoff: DC, transient, AC, eye — pre- vs post-layout
#
# Final characterization of the *Inac et al., EuMIC 2022* PAM-4 driver
# replication (IHP SG13G2 HBT). This notebook runs **one set of testbenches**
# (`testbenches/driver_lib.py`) on **both** netlist flavors:
#
# * **schematic** DUTs (`dut_subckt`, ideal R/C values), at the nominal
#   (EIC-verified) sizing and at the final co-optimized sizing;
# * the **post-layout** netlist (gdsfactory GDS → KLayout DRC/LVS →
#   kpex 2.5D PEX → ngspice), wrapped by `pex_sim.wrap_layout_dut` into the
#   *same DUT port convention* so every bench runs on it **unmodified** via
#   the `dut_ref=` argument.
#
# Signoff suite: **DC** transfer + DAC levels + max swing, **transient**
# bias ramp + single-tone method cross-check, **AC** S21/S11/S22 sweeps,
# and the **48 GBaud PAM-4 eye**. The closing table lines up the original
# paper's specs and measurements, the EIC-designer golden reference, and our
# pre/post-layout results — **all eight post-layout specs pass** at the
# final point (§6), after the resize + RF-layout iteration documented in §7
# (the first signoff of this notebook caught S22 and swing failing; an
# expert layout review + directed re-sizing closed both).
#
# > **Did the EIC project do a layout?** No — §0 shows the evidence: its
# > `layout.gds` deliverable is a 616-byte placeholder (5 rectangles + 5
# > labels in one cell) and its DRC run errored out before checking
# > anything. All 16 verified EIC requirements are schematic-level. The
# > gdsfactory layout in `../layout/` (DRC+LVS clean, PEX'd) is the first
# > real physical design of this replication.

# %%
import sys
import random
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

NB_DIR = Path.cwd()
ROOT = NB_DIR.parent                     # ported-netlists/
sys.path.insert(0, str(ROOT / "testbenches"))
sys.path.insert(0, str(ROOT / "layout"))

from driver_lib import (DriverParams, CellParams, dut_subckt,      # noqa: E402
                        run_ac, run_ac_s22, run_dc, run_bias, run_sparam,
                        run_eye, run_deck, tb_bias)
from pex_sim import wrap_layout_dut                                # noqa: E402

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True,
                     "grid.alpha": 0.3})

# %% [markdown]
# ## 0. Did the EIC do a layout? — evidence
#
# The EIC-designer project (`~/code/EIC-designer/projects/lumped-broadband-driver`)
# ships a `deliverables/layout.gds`. Inspecting it:

# %%
import klayout.db as kdb

EIC = Path.home() / "code/EIC-designer/projects/lumped-broadband-driver"
gds = EIC / "deliverables/layout.gds"
if gds.exists():
    ly = kdb.Layout(); ly.read(str(gds))
    for c in ly.each_cell():
        n_shapes = sum(c.shapes(i).size() for i in ly.layer_indexes())
        print(f"EIC layout.gds: {gds.stat().st_size} bytes, cell '{c.name}': "
              f"{n_shapes} shapes, bbox {c.bbox().to_s()} (dbu)")
    drc = (EIC / "deliverables/drc_report.yaml").read_text()
    print("\nEIC DRC report header:")
    print("\n".join(drc.splitlines()[:6]))
else:
    print("(EIC-designer project not present on this machine — evidence "
          "recorded in the committed executed notebook: 616-byte GDS, one "
          "cell with 5 shapes + 5 labels; DRC status error, 0 rules run)")

# %% [markdown]
# A 616-byte GDS with one cell of 5 polygons + 5 labels is a **block-diagram
# placeholder**, not a layout (for scale: our smallest DUT GDS is ~100 kB
# with 11 physical devices and full BEOL routing), and
# the EIC DRC run terminated on a deck error (`passed: false`,
# `status: error`) without evaluating a single rule. **Conclusion: the EIC
# verified the design at schematic level only; no physical layout was done.**
#
# Our layout of the combined `pam4` DUT (DRC + LVS clean, kpex-extracted):

# %%
from IPython.display import Image, display
display(Image(str(ROOT / "layout/out/dut_pam4.png"), width=760))

# %% [markdown]
# ## 0b. Does `emitter_width = 0.07` invalidate the results? — No.
#
# The layout passes `emitter_width=0.07` (µm) to the foundry npn13G2 PyCell
# because the ihp-gdsfactory wrapper's default (0.7) draws an emitter the
# LVS device-recognition window (exactly 0.07 × 0.9 µm) cannot identify.
# The question is whether that choice biases the simulations. Evidence from
# the PDK model library itself:

# %%
import os
M = Path(os.environ.get("PDK_ROOT", str(Path.home() / "local/pdks")))
lib = M / "ihp-sg13g2/libs.tech/ngspice/models/sg13g2_hbt_mod.lib"
raw = lib.read_bytes().decode("latin-1").splitlines()
i0 = next(i for i, l in enumerate(raw) if l.startswith(".subckt npn13G2 "))
print("\n".join(raw[i0:i0 + 6]))
print("...")
print("\n".join(l for l in raw[i0:i0 + 100]
                if "cje" in l or "rth =" in l or "ic:" in l.lower()))
import re as _re
post = (ROOT / "layout/out/pex/dut_pam4_best_post.spice").read_text()
kq = _re.search(r"XQ_\d+ .*npn13G2.*", (ROOT /
    "layout/out/pex/pam4/dut_pam4_nomim__pam4drv_pam4_lay/"
    "pam4drv_pam4_lay_k25d_pex_netlist.spice").read_text())
print("\nkpex-extracted device card:", kq.group(0) if kq else "(n/a)")

# %% [markdown]
# Three facts close the question:
#
# 1. **The electrical model depends on `Nx` alone.** Every parameter of the
#    VBIC card scales as `(Nx*0.25)`-type expressions (`cje`, `is`, `rth`,
#    …); the declared `we`/`le` subckt parameters appear in **no**
#    expression (`El = le*1e6` is computed and never used). The 0.07 × 0.9
#    µm drawn emitter *is* the device the model describes — Nx parallel
#    fingers of the standard geometry. A 0.7 µm emitter would be a device
#    with **no model at all** (and no LVS recognition).
# 2. **The extraction agrees**: kpex returns the drawn devices as
#    `npn13G2 we=0.07 le=0.9 Nx=3` — the converter carries `Nx` to the
#    simulation subckt, identical to the schematic instantiation. Pre- and
#    post-layout therefore simulate the *same* device.
# 3. **The bias sits inside the model's stated validity**: the card is
#    specified for `ic < 3·Nx mA` and the final point runs 15 mA / 2
#    devices = 7.5 mA per device (validity 9 mA at Nx=3), i.e. **2.5
#    mA/finger — the same peak-f_T current density as the paper's 8 mA /
#    3-finger bias (2.67 mA/finger)**.

# %% [markdown]
# ## 1. The three characterization variants
#
# | variant | netlist | sizing |
# |---|---|---|
# | `schem-nominal` | schematic DUT | EIC-verified nominal (Nx=3, 16 mA, R_C=R_B=50 Ω, R_E=2.5 Ω, V_casc=3.25 V) |
# | `schem-retuned` | schematic DUT | **final co-optimized point** (Nx=3, 15 mA, R_C=50 Ω, R_B=48 Ω, R_E=3.2 Ω, C_deg=16 fF, V_casc=3.35 V) |
# | `post-layout`   | kpex 2.5D PEX netlist of the final GDS | same point + the RF layout configuration (`gen_layout.FINAL_LAYOUT`) |
#
# Note how close the final sizing sits to the *paper's* nominal: the earlier
# nx=2 / R_C=70 Ω point (notebook 02 v1) was compensating input-layout
# parasitics; once the layout review's fixes landed (center-fed H-tree
# input, M4 buses, M2 base drops, light wide-gap output buses), the
# electrical design returned to the paper's topology values with stronger
# emitter degeneration (R_E 2.5→3.2 Ω, shrinking the effective input C for
# the last of the S11 margin) and 15 mA tails.
#
# The post-layout netlist is the final signed-off extraction
# (`layout/out/pex/dut_pam4_best_post.spice`, DRC+LVS PASS; kpex CC and RC
# modes agree on every metric to 0.01 dB). `wrap_layout_dut` adapts its
# port list (explicit tails + substrate) back to the schematic convention —
# VCCS tails at 1 mA/V, grounded substrate — so `run_dc / run_bias /
# run_ac / run_sparam / run_eye` all take it via `dut_ref=`:

# %%
dp_nom = DriverParams()                      # EIC-verified nominal
dp_opt = DriverParams(cell=CellParams(nx=3, tail_ma=15.0, re_ohm=3.2,
                                      cdeg_ff=16.0, rc_ohm=50.0, rb_ohm=48.0,
                                      vcasc=3.35, vcm_in=1.9))

post_net = ROOT / "layout/out/pex/dut_pam4_best_post.spice"
pl_ref = wrap_layout_dut("pam4", str(post_net))
print(pl_ref[:pl_ref.index(".ends") + 20])

VARIANTS = {          # label -> (dp, dut_ref-or-None, plot color)
    "schem-nominal": (dp_nom, None, "tab:gray"),
    "schem-retuned": (dp_opt, None, "tab:blue"),
    "post-layout":   (dp_opt, pl_ref, "tab:red"),
}

# %% [markdown]
# ## 2. DC signoff — transfer curve, DAC levels, max output swing
#
# `.dc` sweeps of the differential source EMF through the 50 Ω/side
# terminations (ngspice-45: the self-heating VBIC HBT converges in `.op`,
# `.dc`, `.ac` — the JPP-361 failure is ngspice-44-only). Two views:
#
# * both input ports driven together (`drive='both'`) over ±800 mV — the
#   large-signal transfer/compression curve; its saturated span is the
#   **max differential output swing** (spec ≥ 2.1 Vpp);
# * MSB swept with the LSB held at ±200 mV EMF (the eye-bench drive level):
#   the four endpoints are the **PAM-4 DAC levels**.

# %%
dc_swing = {}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
for lab, (dp, ref, col) in VARIANTS.items():
    r = run_dc("pam4", drive="both", vd_max_mv=800.0, step_mv=10.0,
               dp=dp, dut_ref=ref, timeout_s=900)
    assert r["ok"], r.get("log", "")[-2000:]
    swing = float(r["vout_diff_v"].max() - r["vout_diff_v"].min())
    dc_swing[lab] = swing
    ax1.plot(r["vd_v"] * 1e3, r["vout_diff_v"], color=col,
             label=f"{lab} ({swing:.2f} Vpp)")
ax1.set_xlabel("differential source EMF [mV]")
ax1.set_ylabel("V_out differential [V]")
ax1.set_title("DC transfer, LSB+MSB driven together")
ax1.legend(fontsize=8)

dac_levels = {}
for lab, (dp, ref, col) in VARIANTS.items():
    lv = []
    for other in (-200.0, 200.0):
        r = run_dc("pam4", drive="msb", vd_max_mv=200.0, step_mv=20.0,
                   other_mv=other, dp=dp, dut_ref=ref, timeout_s=900)
        assert r["ok"], r.get("log", "")[-2000:]
        ax2.plot(r["vd_v"] * 1e3, r["vout_diff_v"], color=col, alpha=0.8,
                 ls="-" if other > 0 else "--",
                 label=lab if other > 0 else None)
        lv += [float(r["vout_diff_v"][0]), float(r["vout_diff_v"][-1])]
    dac_levels[lab] = sorted(lv)
ax2.set_xlabel("MSB differential source EMF [mV]")
ax2.set_ylabel("V_out differential [V]")
ax2.set_title("MSB sweep at LSB = ±200 mV → 4 DAC levels")
ax2.legend(fontsize=8)
fig.tight_layout()

pd.DataFrame({lab: {"max swing [Vpp]": round(dc_swing[lab], 3),
                    **{f"DC level {i} [V]": round(v, 3)
                       for i, v in enumerate(dac_levels[lab])}}
              for lab in VARIANTS}).T

# %% [markdown]
# ## 3. Transient signoff — bias ramp and method cross-check
#
# The `tran` bias bench ramps every supply from 0 (`uic`) and holds — the
# EIC-validated method that works even where `.op` does not. Schematic
# variants probe internal cascode nodes (V_CE headroom check); the
# post-layout netlist has kpex-renamed internals, so it is probed at its
# ports + wrapper tail nodes (same deck builder, `probes=` override).

# %%
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6), sharex=True)
bias_tbl = {}
for ax, (lab, (dp, ref, col)) in zip(axes, VARIANTS.items()):
    if ref is None:
        b = run_bias("pam4", dp=dp)
        assert b["ok"], b.get("log", "")[-1500:]
        bias_tbl[lab] = {"power [mW]": b["power_mw"],
                         "V_CE Q1 (input) [V]": b["vce_q1_msb"],
                         "V_CE Q3 (cascode) [V]": b["vce_q3_msb"],
                         "tail node [V]": b["tail_msb_v"]}
        probes = ["v(outp)", "v(xdut.c1M0)", "v(xdut.tmsb0)", "i(Vcc)"]
        names = ["outp", "casc mid (c1M0)", "tail", "I(VCC)"]
    else:
        probes = ["v(outp)", "v(xdut.tmsb0)", "v(xdut.tlsb0)", "i(Vcc)"]
        names = ["outp", "tail msb", "tail lsb", "I(VCC)"]
    deck, hold0, t_end = tb_bias("pam4",
                                 ref if ref is not None
                                 else dut_subckt("pam4", dp)[1],
                                 dp=dp, probes=probes)
    out, log = run_deck(deck, ["bias.csv"], timeout_s=600)
    data = out["bias.csv"]
    assert data is not None, log[-1500:]
    t_ns = data[:, 0] * 1e9
    for i, nm in enumerate(names):
        y = data[:, 1 + 2 * i]
        if nm == "I(VCC)":
            y = np.abs(y) * 50           # scale to share the axis (A→"V"·50)
            nm = "|I(VCC)|·50 [A]"
        ax.plot(t_ns, y, label=nm, lw=1.2)
    if ref is not None:
        icc = float(np.mean(np.abs(data[data[:, 0] >= hold0 * 1e-9, 7])))
        bias_tbl[lab] = {"power [mW]": icc * dp.vcc * 1e3,
                         "tail node [V]": float(
                             np.mean(data[data[:, 0] >= hold0 * 1e-9, 3]))}
    ax.set_title(lab, fontsize=10)
    ax.set_xlabel("t [ns]")
    ax.legend(fontsize=7)
axes[0].set_ylabel("V (and scaled I)")
fig.suptitle("Bias ramp-and-hold transient (all supplies PWL from 0, uic)")
fig.tight_layout()
pd.DataFrame(bias_tbl).T.round(3)

# %% [markdown]
# Method-independent cross-check: the transient single-tone DFT probe
# (golden method) vs the `.ac` sweep, at 1 GHz, on both the schematic and
# the post-layout netlist. Agreement ≤ ~0.1 dB validates the cheap `.ac`
# path used everywhere else in this notebook.

# %%
xchk = {}
for lab in ("schem-nominal", "post-layout"):
    dp, ref, _ = VARIANTS[lab]
    tr = run_sparam("pam4", f_hz=1e9, drive="msb", dp=dp, dut_ref=ref,
                    timeout_s=900)
    ac = run_ac("pam4", drive="msb", dp=dp, dut_ref=ref, timeout_s=900)
    assert tr["ok"] and ac["ok"]
    lf_ac = float(ac["s21_db"][np.argmin(np.abs(ac["f_ghz"] - 1.0))])
    xchk[lab] = {"S21@1G tran-DFT [dB]": round(tr["s21_db"], 3),
                 "S21@1G .ac [dB]": round(lf_ac, 3),
                 "delta [dB]": round(tr["s21_db"] - lf_ac, 3)}
pd.DataFrame(xchk).T

# %% [markdown]
# ## 4. AC signoff — S21 (LSB & MSB drive), S11, S22

# %%
def ac_char(dp, ref):
    """Full AC characterization of the pam4 DUT -> metrics + curves."""
    out = {}
    for drv in ("lsb", "msb"):
        r = run_ac("pam4", drive=drv, dp=dp, dut_ref=ref, timeout_s=900)
        assert r["ok"], r.get("log", "")[-2000:]
        f, s21, s11 = r["f_ghz"], r["s21_db"], r["s11_db"]
        lf = float(s21[np.argmin(np.abs(f - 1.0))])
        thr, f3 = lf - 3.0, float(f[-1])
        for i in range(len(f) - 1):
            if s21[i] >= thr > s21[i + 1]:
                f3 = float(np.interp(thr, [s21[i + 1], s21[i]],
                                     [f[i + 1], f[i]]))
                break
        out[drv] = {"f": f, "s21": s21, "s11": s11, "lf": lf, "f3db": f3,
                    "s11w": float(s11[f <= 32.0].max())}
    r22 = run_ac_s22("pam4", dp=dp, dut_ref=ref, timeout_s=900)
    assert r22["ok"], r22.get("log", "")[-2000:]
    out["s22"] = {"f": r22["f_ghz"], "s22": r22["s22_db"],
                  "s22w": float(r22["s22_db"][r22["f_ghz"] <= 50.0].max())}
    return out

AC = {lab: ac_char(dp, ref) for lab, (dp, ref, _) in VARIANTS.items()}

fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
for lab, (dp, ref, col) in VARIANTS.items():
    a = AC[lab]
    axes[0].semilogx(a["msb"]["f"], a["msb"]["s21"], color=col, label=lab)
    axes[0].semilogx(a["lsb"]["f"], a["lsb"]["s21"], color=col, ls="--",
                     alpha=0.7)
    axes[1].semilogx(a["msb"]["f"], a["msb"]["s11"], color=col, label=lab)
    axes[2].semilogx(a["s22"]["f"], a["s22"]["s22"], color=col, label=lab)
axes[0].set_title("S21 (solid MSB, dashed LSB)")
axes[0].set_ylabel("dB"); axes[0].set_ylim(-5, 12)
axes[1].set_title("S11 (MSB drive)"); axes[1].axhline(-10, color="k", lw=0.8)
axes[1].axvline(32, color="k", lw=0.6, ls=":")
axes[2].set_title("S22"); axes[2].axhline(-10, color="k", lw=0.8)
axes[2].axvline(50, color="k", lw=0.6, ls=":")
for ax in axes:
    ax.set_xlabel("f [GHz]"); ax.legend(fontsize=7)
fig.tight_layout()

pd.DataFrame({lab: {
    "LSB gain [dB]": round(a["lsb"]["lf"], 2),
    "MSB gain [dB]": round(a["msb"]["lf"], 2),
    "DAC weight [dB]": round(a["msb"]["lf"] - a["lsb"]["lf"], 2),
    "BW LSB / MSB [GHz]": f'{a["lsb"]["f3db"]:.1f} / {a["msb"]["f3db"]:.1f}',
    "S11 worst ≤32G [dB]": round(a["msb"]["s11w"], 2),
    "S22 worst ≤50G [dB]": round(a["s22"]["s22w"], 2),
} for lab, a in AC.items()}).T

# %% [markdown]
# ## 5. 48 GBaud PAM-4 eye diagrams
#
# Same stimulus as the EIC reference and `run_eye.py`: seed-7 random MSB/LSB
# streams, 120 symbols, 200 mV input swing, 4 ps edges — schematic and
# post-layout through the identical `tb_eye` deck.

# %%
BAUD, NSYM = 48e9, 120
random.seed(7)
msb_bits = [random.randint(0, 1) for _ in range(NSYM)]
lsb_bits = [random.randint(0, 1) for _ in range(NSYM)]


def eye_metrics(t, v, t0_ns, baud):
    """Fold into 2 UI; cluster mid-UI samples into 4 levels -> RLM, eyes."""
    T = 1.0 / baud
    t_an0 = t0_ns * 1e-9 + 6 * T
    m = t >= t_an0
    tt, vv = t[m], v[m]
    phase = (tt - t_an0) % (2 * T)
    win = (phase > T - 0.08 * T) & (phase < T + 0.08 * T)
    samp = np.sort(vv[win])
    cut = np.sort(np.argsort(np.diff(samp))[-3:])
    groups = np.split(samp, cut + 1)
    levels = [float(np.mean(g)) for g in groups]
    eyes = [float(groups[i + 1].min() - groups[i].max()) for i in range(3)]
    amps = np.diff(levels)
    return phase, vv, {"vout_pp_v": round(float(vv.max() - vv.min()), 3),
                       "eye_openings_v": [round(e, 3) for e in eyes],
                       "rlm": round(float(3 * amps.min() / amps.sum()), 3)}


eye_tbl = {}
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8), sharey=True)
for ax, (lab, (dp, ref, col)) in zip(axes, VARIANTS.items()):
    t, v, t0, baud, log = run_eye(msb_bits=msb_bits, lsb_bits=lsb_bits,
                                  dp=dp, dut_ref=ref, baud_hz=BAUD,
                                  vswing_mv=200.0, timeout_s=5400)
    assert t is not None, log[-2000:]
    phase, vv, met = eye_metrics(t, v, t0, baud)
    eye_tbl[lab] = met
    ax.plot(phase * 1e12, vv, ",", color=col, alpha=0.3)
    ax.set_title(f"{lab}  (RLM {met['rlm']:.3f})", fontsize=10)
    ax.set_xlabel("t within 2 UI [ps]")
axes[0].set_ylabel("V_out differential [V]")
fig.suptitle(f"PAM-4 eye @ {BAUD/1e9:.0f} GBaud, 200 mV input, {NSYM} symbols")
fig.tight_layout()
pd.DataFrame(eye_tbl).T

# %% [markdown]
# ## 6. Master spec table — paper vs EIC vs pre/post-layout
#
# Spec targets are the EIC-designer SYS-* requirement set (derived from the
# paper, `spec/integration/sim_results.yaml`); "paper (meas.)" is what
# Inac et al. report for the fabricated chip (§III / Figs. 4-5); "EIC golden"
# is the verified schematic simulation our port reproduces with zero delta.
# Block-level caveat as disclosed by the EIC verification: ideal tail
# sources / no pads, so simulated BW carries known headroom vs measurement.

# %%
paper_meas = {"LSB gain [dB]": "3.2", "MSB gain [dB]": "9.2",
              "DAC weight [dB]": "6.0", "BW [GHz]": "51–67 (meas.)",
              "S11 [dB]": "< −10", "S22 [dB]": "< −10",
              "Swing [Vpp]": "2.1", "Power [mW]": "192",
              "RLM": "—", "Area [mm²]": "0.011 (core)"}
SPEC = {"LSB gain [dB]": (">=", 2.2), "MSB gain [dB]": (">=", 8.2),
        "DAC weight [dB]": (">=", 5.0), "BW [GHz]": (">=", 50.0),
        "S11 [dB]": ("<=", -10.0), "S22 [dB]": ("<=", -10.0),
        "Swing [Vpp]": (">=", 2.1), "Power [mW]": ("<=", 192.0)}
eic = {"LSB gain [dB]": 3.10, "MSB gain [dB]": 9.07,
       "DAC weight [dB]": 5.97, "BW [GHz]": 68.5, "S11 [dB]": -10.87,
       "S22 [dB]": -14.76, "Swing [Vpp]": 2.92, "Power [mW]": 191.03,
       "RLM": 0.975, "Area [mm²]": float("nan")}


def ours(lab):
    a = AC[lab]
    return {"LSB gain [dB]": a["lsb"]["lf"], "MSB gain [dB]": a["msb"]["lf"],
            "DAC weight [dB]": a["msb"]["lf"] - a["lsb"]["lf"],
            "BW [GHz]": min(a["lsb"]["f3db"], a["msb"]["f3db"]),
            "S11 [dB]": a["msb"]["s11w"], "S22 [dB]": a["s22"]["s22w"],
            "Swing [Vpp]": dc_swing[lab],
            "Power [mW]": bias_tbl[lab]["power [mW]"],
            "RLM": eye_tbl[lab]["rlm"],
            "Area [mm²]": 0.00755 if lab == "post-layout" else float("nan")}


def fmt(vals):
    o = {}
    for k, v in vals.items():
        if isinstance(v, float) and np.isnan(v):
            o[k] = "—"
        elif k in SPEC:
            op, tgt = SPEC[k]
            ok = v >= tgt if op == ">=" else v <= tgt
            o[k] = f"{v:.2f} {'✓' if ok else '✗'}"
        else:
            o[k] = f"{v:.3f}" if isinstance(v, float) else str(v)
    return o


master = pd.DataFrame({
    "spec": {k: f"{op} {tgt:g}" for k, (op, tgt) in SPEC.items()},
    "paper (meas.)": paper_meas,
    "EIC golden (schem)": fmt(eic),
    "ours schem-nominal": fmt(ours("schem-nominal")),
    "ours schem-retuned": fmt(ours("schem-retuned")),
    "ours post-layout": fmt(ours("post-layout")),
}).reindex(list(paper_meas))
master

# %% [markdown]
# ## 7. Conclusions
#
# * **Testbench reuse** — a single bench library covers both abstraction
#   levels: the schematic DUT and the kpex post-layout netlist run the same
#   DC / tran / AC / eye decks, differing only in the `dut_ref=` string
#   (`wrap_layout_dut` supplies the port adapter + RES/CAP corner libs).
#   The tran-DFT vs `.ac` cross-check agrees on both netlists, so the two
#   measurement methods stay mutually validating after extraction.
# * **Pre-layout** — `schem-nominal` reproduces the EIC golden reference;
#   `schem-retuned` confirms the final sizing at schematic level.
# * **Post-layout: all eight specs pass.** This is the second iteration of
#   this signoff. The first (2026-08-09 morning, at notebook-02-v1's
#   nx=2 / R_C=70 Ω point) caught **S22 = −8.3 dB** and **swing =
#   2.07 Vpp** failing — metrics the v1 optimizer never scored. The fix was
#   a joint layout + sizing iteration, informed by an expert RF layout
#   review:
#
#   | step | change | effect |
#   |---|---|---|
#   | probe (rc=80, nx=2) | swing ✓ 2.18 | S22 stuck at −7.9: output C dominated, not R_C mismatch |
#   | C-budget analysis | kpex: ~14 fF/side bus-network + ~14 fF/side cascode junctions | S22 needs R_C≈50 → needs ≥15 mA → needs nx=3 → S11 becomes the binding spec |
#   | output-bus RF fixes | wide gap (8 µm), min-width TM1, slim risers/stacks, compact row | S22 −8.4 → −10.1 at R_C=50 |
#   | input-network RF fixes | center-fed H-tree R_B, M4 buses, wide pair gap, M2 base drops | msb S11 at nx=3: −8.8 → −9.9 |
#   | electrical re-tune | R_E 2.5→3.2 Ω (series feedback shrinks C_in,eff), R_B 48, tail 15, V_casc 3.35 | S11 −10.03 ✓ with gain 8.25 ✓ |
#
#   The final point is essentially the **paper's nominal topology**
#   (nx=3, R_C=50) — v1's nx=2/R_C=70 was compensating layout deficiencies.
#   kpex RC-mode extraction reproduces every CC-mode metric to 0.01 dB, and
#   DRC + LVS pass on all three DUTs.
# * **Remaining pre-tapeout flags** (from the expert layout review, not
#   covered by this block-level signoff): vcasc rail needs per-cell cmim
#   bypass + odd-mode series R (stability); via stacks and the TM1 bus need
#   an EM/current-density pass; ground cage (wide via-stacked guard ring,
#   tap fence); group-delay variation and extracted-rail stability analysis;
#   HBT/rsil dummies for matching. See `layout/README.md`.
# * **`emitter_width=0.07` does not invalidate results** — §0b: the model
#   is a function of Nx alone, the extracted and simulated devices are
#   identical, and the bias sits at the paper's peak-f_T current density
#   inside the model's stated validity.
# * **EIC layout question** — answered in §0: the EIC project produced only
#   a placeholder GDS and a failed DRC run; it did **not** do a layout. The
#   parameterized gdsfactory layout + DRC/LVS/PEX loop in `../layout/` is
#   new work, and the post-layout column above is the first
#   parasitic-aware verification of this design.

# %%
print("signoff notebook complete")
