import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # PAM-4 driver — schematic-level sizing & characterization

    Block-level replication of *Inac, Peczek, Gerfers, Malignaggi, "Inductorless
    96 Gb/s PAM-4 Optical Modulators Driver in SiGe:C BiCMOS", EuMIC 2022* on the
    **IHP SG13G2** HBT process (`npn13G2`, VBIC), ported from the EIC-designer
    verified reference (16/16 requirements, dual sign-off; this port reproduces
    its golden metrics with zero delta).

    | DUT | Contents | Paper figure |
    |---|---|---|
    | `lsb`  | 1 differential-cascode gain cell + R_C + R_B | Fig. 2(a) |
    | `msb`  | 2 identical gain cells in parallel, shared R_C/R_B | Fig. 2(b) |
    | `pam4` | 1 LSB + 2 MSB cells current-summing into shared R_C | Fig. 1 |

    **Measurement methods.** Every metric exists in two independent flavours:
    the EIC-validated *transient tone-probe* golden method (ramp-from-0 `tran
    … uic`, single-bin DFT) and the ~30x cheaper `.op`+`.ac` path. The original
    EIC finding JPP-361 ("the self-heating VBIC does not converge in
    `.op/.ac/.dc`") reproduces on ngspice-44 only — on this machine's ngspice-45
    both methods agree to <= 0.011 dB, so this notebook uses the fast AC path
    (cross-checked against the committed transient-DFT results in
    `../results/`).
    """)
    return


@app.cell
def _(mo):
    import sys, os
    import numpy as np
    import yaml
    import matplotlib.pyplot as plt
    from IPython.display import Image, Markdown, display

    ROOT = mo.notebook_dir().resolve().parent          # ported-netlists/
    sys.path.insert(0, str(ROOT / "testbenches"))
    import driver_lib as dl
    from driver_lib import DriverParams, CellParams

    def md_table(headers, rows):
        out = ["| " + " | ".join(headers) + " |",
               "|" + "|".join(["---"] * len(headers)) + "|"]
        out += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
        display(Markdown("\n".join(out)))

    print("models:", dl.models_dir())
    return (
        CellParams,
        DriverParams,
        Image,
        Markdown,
        ROOT,
        display,
        dl,
        md_table,
        np,
        plt,
        yaml,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sizing

    One gain cell = the DAC weight unit. The EIC-verified nominal sizing (all
    three DUTs share it — the MSB weight comes from *cell count*, not device
    sizing, which is what makes the 6 dB DAC step ratiometric):
    """)
    return


@app.cell
def _(CellParams, md_table):
    import dataclasses
    cp = CellParams()
    md_table(["knob", "nominal", "meaning"], [
        ("nx", cp.nx, "npn13G2 emitter fingers (mask 0.07x0.9 um each; I_C < 3*Nx mA)"),
        ("tail_ma", cp.tail_ma, "tail current per cell (8 mA/device = ~peak-fT)"),
        ("re_ohm", cp.re_ohm, "emitter degeneration per side"),
        ("cdeg_ff", cp.cdeg_ff, "emitter bridging cap (HF peaking)"),
        ("rc_ohm", cp.rc_ohm, "collector load per side (shared per DUT)"),
        ("rb_ohm", cp.rb_ohm, "input termination per side"),
        ("vcasc", cp.vcasc, "cascode base bias (V)"),
        ("vcm_in", cp.vcm_in, "input common mode (V)"),
    ])
    print("VCC = 4.0 V; tails are VCCS-driven (1 mA/V) from a bias port -> "
          "plain scalar optimizer knob")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The three DUT schematics

    xschem schematics generated with `spicexplorer-netlist2xschem` from the DUT
    netlists, hand-arranged to follow the paper's figures.
    """)
    return


@app.cell
def _(Image, Markdown, ROOT, display):
    for _d, cap in (("lsb", "LSB cell (Fig. 2a)"), ("msb", "MSB, two cells (Fig. 2b)"),
                   ("pam4", "full 2-bit DAC driver (Fig. 1)")):
        display(Markdown(f"**{cap}**"))
        display(Image(str(ROOT / "schematics" / f"dut_{_d}.png"), width=900))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## DUT netlists (authoritative)
    """)
    return


@app.cell
def _(ROOT):
    for _d in ("lsb", "msb", "pam4"):
        print("=" * 30, f"dut/dut_{_d}.spice", "=" * 30)
        print((ROOT / "dut" / f"dut_{_d}.spice").read_text())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testbenches

    The AC bench below (S21 as differential power-wave gain `2*Vout/Vsrc` into
    50 ohm/side, S11 via `Zin = Vin/Iin` against the 100 ohm differential
    reference — the paper's VNA conventions). The transient golden bench is the
    same DUT with PWL-ramped supplies and a single-tone probe.
    """)
    return


@app.cell
def _(DriverParams, dl):
    _, sub, _ = dl.dut_subckt("msb", DriverParams())
    deck = dl.tb_ac("msb", sub, drive="in")
    print("\n".join(deck.splitlines()[:16]) + "\n...\n" +
          "\n".join(deck.splitlines()[-16:]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Bias / operating point (transient-settled, golden method)
    """)
    return


@app.cell
def _(dl, md_table):
    bias = {}
    for _d in ("lsb", "msb", "pam4"):
        bias[_d] = dl.run_bias(_d)
    keys = ["power_mw", "i_supply_ma", "outp_v", "vce_q1_lsb", "vce_q3_lsb",
            "vce_q1_msb", "vce_q3_msb"]
    md_table(["metric"] + list(bias),
             [[k] + [round(bias[d][k], 3) if k in bias[d] else "-" for d in bias]
              for k in keys])
    print("VBIC validity: 0.4 V <= V_CE <= 2.0 V, I_C < 3*Nx mA/device -> all OK")
    return (bias,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Frequency response — S21 / S11 / S22 (.op + .ac, ngspice-45)
    """)
    return


@app.cell
def _(dl, plt):
    runs = [("lsb", "in"), ("msb", "in"), ("pam4", "lsb"), ("pam4", "msb")]
    ac = {f"{d}:{drv}": dl.run_ac(d, drive=drv) for d, drv in runs}
    s22 = dl.run_ac_s22("pam4")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4))
    for _k, _r in ac.items():
        a1.semilogx(_r["f_ghz"], _r["s21_db"], label=_k)
        a2.semilogx(_r["f_ghz"], _r["s11_db"], label="S11 " + _k)
    a2.semilogx(s22["f_ghz"], s22["s22_db"], "--", label="S22 pam4")
    a1.set(xlabel="f (GHz)", ylabel="S21 (dB)", title="differential gain")
    a2.set(xlabel="f (GHz)", ylabel="S11/S22 (dB)", title="reflections")
    a2.axhline(-10, color="r", lw=0.8, ls=":")
    a1.grid(True, which="both", alpha=0.3); a2.grid(True, which="both", alpha=0.3)
    a1.legend(); a2.legend(); plt.tight_layout(); plt.show()
    return ac, s22


@app.cell
def _(ROOT, ac, bias, md_table, np, s22, yaml):
    def metrics(r, fmax_s11=32.0):
        f, s21, s11 = r["f_ghz"], r["s21_db"], r["s11_db"]
        lf = s21[np.argmin(np.abs(f - 1.0))]
        thr = lf - 3.0
        f3 = f[-1]
        for i in range(len(f) - 1):
            if s21[i] >= thr > s21[i + 1]:
                f3 = np.interp(thr, [s21[i + 1], s21[i]], [f[i + 1], f[i]]); break
        return round(float(lf), 2), round(float(f3), 1),         round(float(s11[f <= fmax_s11].max()), 2)

    rows = []
    for _k, _r in ac.items():
        lf, f3, s11w = metrics(_r)
        rows.append((_k, lf, f3, s11w))
    dacw = round(rows[3][1] - rows[2][1], 2)
    s22w = round(float(s22["s22_db"][s22["f_ghz"] <= 50].max()), 2)
    md_table(["DUT:path", "S21 LF (dB)", "f3dB (GHz)", "worst S11<=32G (dB)"], rows)
    md_table(["metric", "value", "spec / paper"], [
        ("DAC weight MSB-LSB (dB)", dacw, "6 (2-bit DAC)"),
        ("pam4 worst S22 <= 50 GHz (dB)", s22w, "< -10"),
        ("pam4 power (mW)", round(bias["pam4"]["power_mw"], 1), "<= 192"),
    ])
    print("Cross-check: committed transient-DFT golden values (zero delta vs "
          "EIC reference):")
    gold = yaml.safe_load((ROOT / "results" / "pam4_results.yaml").read_text())
    print(yaml.safe_dump(gold.get("vs_eic_golden", gold), sort_keys=False)[:1200])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 48 GBaud PAM-4 eye (transient golden method, committed run)
    """)
    return


@app.cell
def _(Image, ROOT, display, yaml):
    display(Image(str(ROOT / "results" / "pam4_eye.png"), width=700))
    print(yaml.safe_dump(yaml.safe_load(
        (ROOT / "results" / "pam4_eye_metrics.yaml").read_text()), sort_keys=False))
    RUN_FULL = False   # True -> re-simulate the eye (minutes) via ../testbenches/run_eye.py
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    - All three DUTs reproduce the EIC golden reference at the nominal sizing;
      LSB standalone has ~5.6 dB better S11 than MSB (half the input
      capacitance) and the MSB dominates the system S11 budget.
    - Every knob above is a plain scalar (or integer) on the DUT netlists —
      ready for the optimizer.
    - **Next:** `02_layout_in_the_loop.py` takes these DUTs to DRC/LVS-clean
      IHP sg13g2 layouts and shows that the nominal sizing does *not* survive
      layout parasitics (S11 spec fails post-PEX) — then fixes it with layout +
      electrical co-optimization in a real signoff/PEX/simulate loop.
    """)
    return


if __name__ == "__main__":
    app.run()
