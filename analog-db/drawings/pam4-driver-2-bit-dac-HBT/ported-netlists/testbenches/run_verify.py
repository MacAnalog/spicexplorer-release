"""Full characterization of one (or all) DUTs -> results/<dut>_results.yaml
plus plots. Runs BOTH methods and cross-checks them:

  tran : ramp-from-0 tone probes + single-bin DFT (EIC-validated golden method)
  ac   : direct .op/.ac (ngspice-45 only; ~30x cheaper)

Usage:  python run_verify.py [lsb|msb|pam4|all]   (default: all)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from driver_lib import (DUTS, DriverParams, run_ac, run_ac_s22, run_bias,
                        run_s22, run_sparam)

RESULTS = Path(__file__).parent.parent / "results"
RESULTS.mkdir(exist_ok=True)

FS_GHZ = [1, 5, 10, 20, 30, 40, 50, 60, 70]
S11_PTS = [2, 10, 20, 32]
S22_PTS = [2, 10, 20, 32, 40, 50]
SWING_MV = [200, 400, 800, 1200, 1600]

# EIC-designer verified reference (combined system == pam4 DUT), for delta
# reporting. Source: EIC lumped-broadband-driver sim_results.yaml.
GOLDEN_PAM4 = {
    "lsb_lf_gain_db": 3.10, "msb_lf_gain_db": 9.07,
    "lsb_bw_3db_ghz": 70.0, "msb_bw_3db_ghz": 68.5,
    "s11_worst_to_32ghz_db": -10.87, "s22_worst_to_50ghz_db": -14.76,
    "power_mw": 191.027, "max_vout_pp_v": 2.916,
}


def bw_3db(fs, g):
    ref = g[0]
    for i in range(1, len(fs)):
        if g[i] <= ref - 3:
            return fs[i-1] + (fs[i]-fs[i-1])*(ref-3-g[i-1])/(g[i]-g[i-1])
    return float(fs[-1])


def ac_at(f_ghz, arr_f, arr_v):
    return float(np.interp(f_ghz, arr_f, arr_v))


def verify_dut(dut: str) -> dict:
    dp = DriverParams()
    drives = ["lsb", "msb"] if dut == "pam4" else ["in"]
    res: dict = {"dut": dut,
                 "nominal_params": {
                     "nx": dp.cell.nx, "tail_ma_per_cell": dp.cell.tail_ma,
                     "re_ohm": dp.cell.re_ohm, "cdeg_ff": dp.cell.cdeg_ff,
                     "rc_ohm": dp.cell.rc_ohm, "rb_ohm": dp.cell.rb_ohm,
                     "vcasc": dp.cell.vcasc, "vcm_in": dp.cell.vcm_in,
                     "vcc": dp.vcc,
                     "n_lsb_cells": DUTS[dut][0], "n_msb_cells": DUTS[dut][1]}}

    # --- bias / power (tran ramp-and-hold) ---
    b = run_bias(dut, dp=dp)
    assert b["ok"], b.get("log", "")[-2000:]
    res["bias"] = {k: round(float(v), 3) for k, v in b.items() if k != "ok"}

    # --- frequency response: tran tone sweep + ac sweep, per drive ---
    tran: dict[str, dict] = {}
    phase: dict[str, list] = {}
    for drv in drives:
        s21, s11, ph = [], [], []
        for f in FS_GHZ:
            r = run_sparam(dut, f_hz=f*1e9, drive=drv, dp=dp)
            assert r["ok"], f"{dut}/{drv}/{f}GHz: " + r.get("log", "")[-2000:]
            s21.append(float(r["s21_db"]))
            s11.append(float(r["s11_db"]))
            ph.append(float(r["s21_phase_deg"]))
            print(f"  [{dut}] tran {drv} {f} GHz: S21={s21[-1]:.2f} dB", flush=True)
        tran[drv] = {"s21_db": s21, "s11_db": s11}
        phase[drv] = ph
    ac: dict[str, dict] = {}
    for drv in drives:
        a = run_ac(dut, drive=drv, dp=dp)
        assert a["ok"], a.get("log", "")[-2000:]
        ac[drv] = a

    res["small_signal"] = {"freq_ghz": FS_GHZ}
    for drv in drives:
        key = {"in": "", "lsb": "lsb_", "msb": "msb_"}[drv]
        g = tran[drv]["s21_db"]
        res["small_signal"][f"{key}s21_db_tran"] = [round(x, 2) for x in g]
        res["small_signal"][f"{key}s21_db_ac"] = [
            round(ac_at(f, ac[drv]["f_ghz"], ac[drv]["s21_db"]), 2)
            for f in FS_GHZ]
        res["small_signal"][f"{key}lf_gain_db"] = round(g[0], 2)
        res["small_signal"][f"{key}bw_3db_ghz"] = float(round(bw_3db(FS_GHZ, g), 1))
        # tran-vs-ac cross-check at the LF point
        res["small_signal"][f"{key}tran_minus_ac_lf_db"] = round(
            g[0] - ac_at(1, ac[drv]["f_ghz"], ac[drv]["s21_db"]), 3)
    if dut == "pam4":
        res["small_signal"]["dac_weight_db"] = round(
            tran["msb"]["s21_db"][0] - tran["lsb"]["s21_db"][0], 2)

    # --- group delay from tone-probe phase (main drive) ---
    main = "msb" if dut == "pam4" else "in"
    phr = np.unwrap(np.radians(phase[main]))
    gd = -np.diff(phr) / (2*np.pi*np.diff(np.array(FS_GHZ)*1e9)) * 1e12
    res["group_delay"] = {"mean_ps": round(float(gd.mean()), 2),
                          "peak_variation_ps":
                          round(float(np.max(np.abs(gd - gd.mean()))), 2)}

    # --- input match S11 (tran spot points, main drive) ---
    s11_spot = {}
    for f in S11_PTS:
        r = run_sparam(dut, f_hz=f*1e9, drive=main, dp=dp)
        s11_spot[f] = float(r["s11_db"])
    res["match"] = {
        "s11_db_tran": {f"{k}ghz": round(v, 2) for k, v in s11_spot.items()},
        "s11_worst_to_32ghz_db": round(max(s11_spot.values()), 2),
        "s11_db_ac": {f"{f}ghz": round(ac_at(f, ac[main]["f_ghz"],
                                             ac[main]["s11_db"]), 2)
                      for f in S11_PTS}}

    # --- output match S22 + large-signal swing: pam4 (system) only ---
    if dut == "pam4":
        s22_spot = {}
        for f in S22_PTS:
            r = run_s22(dut, f_hz=f*1e9, dp=dp)
            assert r["ok"], r.get("log", "")[-2000:]
            s22_spot[f] = float(r["s22_db"])
            print(f"  [{dut}] tran S22 {f} GHz: {s22_spot[f]:.2f} dB", flush=True)
        a22 = run_ac_s22(dut, dp=dp)
        res["match"]["s22_db_tran"] = {f"{k}ghz": round(v, 2)
                                       for k, v in s22_spot.items()}
        res["match"]["s22_worst_to_50ghz_db"] = round(max(s22_spot.values()), 2)
        res["match"]["s22_db_ac"] = {
            f"{f}ghz": round(ac_at(f, a22["f_ghz"], a22["s22_db"]), 2)
            for f in S22_PTS}

        swing = []
        for vin in SWING_MV:
            r = run_sparam(dut, f_hz=1e9, drive="both", vac_mv=vin,
                           window_periods=8, settle_periods=4, dp=dp)
            swing.append([float(round(r["vin_pp_mv"], 0)),
                          float(round(r["vout_pp_mv"]/1e3, 3))])
            print(f"  [{dut}] swing {vin} mV -> {swing[-1][1]:.3f} V", flush=True)
        res["swing"] = {"vin_pp_mv__vout_pp_v": swing,
                        "max_vout_pp_v": float(max(s[1] for s in swing))}

        # deltas vs the EIC golden reference
        got = {
            "lsb_lf_gain_db": res["small_signal"]["lsb_lf_gain_db"],
            "msb_lf_gain_db": res["small_signal"]["msb_lf_gain_db"],
            "lsb_bw_3db_ghz": res["small_signal"]["lsb_bw_3db_ghz"],
            "msb_bw_3db_ghz": res["small_signal"]["msb_bw_3db_ghz"],
            "s11_worst_to_32ghz_db": res["match"]["s11_worst_to_32ghz_db"],
            "s22_worst_to_50ghz_db": res["match"]["s22_worst_to_50ghz_db"],
            "power_mw": res["bias"]["power_mw"],
            "max_vout_pp_v": res["swing"]["max_vout_pp_v"]}
        res["vs_eic_golden"] = {
            k: {"got": got[k], "golden": GOLDEN_PAM4[k],
                "delta": round(got[k] - GOLDEN_PAM4[k], 3)}
            for k in GOLDEN_PAM4}

    # --- plots ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for drv in drives:
        lbl = {"in": dut.upper(), "lsb": "LSB", "msb": "MSB"}[drv]
        ax1.plot(FS_GHZ, tran[drv]["s21_db"], "o-",
                 label=f"{lbl} tran-DFT")
        ax1.plot(ac[drv]["f_ghz"], ac[drv]["s21_db"], "--", alpha=0.7,
                 label=f"{lbl} .ac")
        ax2.plot(ac[drv]["f_ghz"], ac[drv]["s11_db"], "--", alpha=0.7,
                 label=f"S11 {lbl} .ac")
        ax2.plot(S11_PTS if drv == main else [],
                 [s11_spot[f] for f in S11_PTS] if drv == main else [],
                 "o", label=f"S11 {lbl} tran" if drv == main else None)
    if dut == "pam4":
        ax2.plot(a22["f_ghz"], a22["s22_db"], ":", alpha=0.9, label="S22 .ac")
        ax2.plot(S22_PTS, [s22_spot[f] for f in S22_PTS], "s", label="S22 tran")
    ax2.axhline(-10, color="crimson", lw=0.8, ls="-.", label="-10 dB spec")
    ax1.set_xlim(0, 75)
    ax1.set_xlabel("frequency [GHz]"); ax1.set_ylabel("S21 [dB]")
    ax1.set_title(f"{dut.upper()} DUT — differential gain"); ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.set_xlim(0, 75); ax2.set_ylim(-50, 0)
    ax2.set_xlabel("frequency [GHz]"); ax2.set_ylabel("[dB]")
    ax2.set_title("port match"); ax2.grid(alpha=0.3); ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / f"{dut}_freq_response.png", dpi=130)
    plt.close(fig)

    out = RESULTS / f"{dut}_results.yaml"
    out.write_text(yaml.dump(res, sort_keys=False))
    print(f"[{dut}] written: {out}", flush=True)
    return res


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    duts = list(DUTS) if which == "all" else [which]
    for dut in duts:
        print(f"=== {dut} ===", flush=True)
        verify_dut(dut)
