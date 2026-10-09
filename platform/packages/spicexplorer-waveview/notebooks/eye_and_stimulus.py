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
    # Stimulus and the data eye — PRBS/PAM4 in, BT4 eye metrics out

    `spicexplorer_waveview.stimulus` builds the data stream a transmitter bench drives (PRBS bits →
    NRZ or Gray-coded PAM4 symbols → exact PWL source lines, an FFE tap being the same stream delayed
    `k` UI); `spicexplorer_waveview.eye` scores the resulting waveform behind a 4th-order
    Bessel-Thomson reference receiver, grouping samples by the *transmitted* symbol so a closed eye
    still returns finite numbers. The eye is a registered measurement kind, so the same numbers come
    out of `measure_dataset(ds, {"meas": "vecp_db", …})` on any loaded rawfile.

    Pure Python — nothing is simulated here; a synthetic first-order channel stands in for the DUT.
    """)
    return


@app.cell
def _():
    import numpy as np
    from scipy import signal
    from spicexplorer_waveview import (
        Data,
        WaveAnalysis,
        WaveDataset,
        WaveSignal,
        eye_metrics,
        fold,
        ideal_waveform,
        measure_dataset,
        measure_many,
        measurement_catalog,
        prbs,
        pwl,
        rx_bandwidth,
    )

    return (
        Data,
        WaveAnalysis,
        WaveDataset,
        WaveSignal,
        eye_metrics,
        fold,
        ideal_waveform,
        measure_dataset,
        measure_many,
        measurement_catalog,
        np,
        prbs,
        pwl,
        rx_bandwidth,
        signal,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The stimulus

    `Data(fmt, rate_gbd, order, n_warm, seed, t0, tr_ui)` is the whole description: format, baud,
    PRBS order, warm-up symbols (driven, not scored), the first symbol edge and the edge time. One
    `Data` drives every source of a bench.
    """)
    return


@app.cell
def _(Data, np, prbs):
    bits = prbs(7, 20)
    print("PRBS-7 head:", "".join(map(str, bits)), "| period", 2**7 - 1)

    d = Data("pam4", rate_gbd=10.0, order=7, n_warm=8)
    print(
        f"{d.fmt.upper()} {d.rate_gbd:g} GBd: UI = {d.ui * 1e12:.0f} ps, {d.n} symbols, "
        f"scored window {d.window()[0] * 1e9:.1f}-{d.window()[1] * 1e9:.1f} ns"
    )
    print("levels:", sorted(set(np.round(d.syms, 3).tolist())))
    return (d,)


@app.cell
def _(d, pwl):
    # the source lines a bench emits: the main tap and a post-cursor FFE tap = the same stream 1 UI late, inverted
    main = pwl("Vin", "in", "0", d, vcm=0.5, swing=0.4)
    tap1 = pwl("Vtap1", "tap1", "0", d, vcm=0.5, swing=0.1, delay_ui=1.0, invert=True)
    print(main[:120] + " …")
    print(tap1[:120] + " …")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. A synthetic channel and its eye

    A first-order low-pass at 0.8 × baud stands in for a DUT; the reference receiver (BT4 at
    0.5 × baud for PAM4) is applied inside `eye_metrics`. The metrics are plain floats — a ledger row.
    """)
    return


@app.cell
def _(d, eye_metrics, ideal_waveform, np, rx_bandwidth, signal):
    t = np.arange(0.0, d.t_end + 2e-9, d.ui / 50)
    x_ideal = 0.5 + 0.2 * ideal_waveform(t, d)  # unipolar, 0.3..0.7 (an optical power, say)
    b, a = signal.butter(1, 0.8 * d.rate_gbd * 1e9 / (0.5 / (t[1] - t[0])))
    x = signal.lfilter(b, a, x_ideal - x_ideal[0]) + x_ideal[0]

    m = eye_metrics(t, x, d)
    print(f"reference receiver: {rx_bandwidth(d.fmt, d.rate_gbd) / 1e9:g} GHz")
    for k in (
        "eye_h_norm",
        "eye_w_ui_1s",
        "vecp_db",
        "er_db",
        "oma_db",
        "rlm",
        "latency_ps",
        "polarity",
    ):
        print(f"{k:>12}: {m[k]:.3f}" if isinstance(m[k], float) else f"{k:>12}: {m[k]}")
    return m, t, x


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    An inverting stage is handled (polarity −1, the same eye); a bipolar electrical signal has
    OMA/VECP but no extinction ratio (`nan`), and a closed eye stays finite.
    """)
    return


@app.cell
def _(d, eye_metrics, m, np, t, x):
    inv = eye_metrics(t, 1.0 - x, d)
    bip = eye_metrics(t, 2 * (x - 0.5), d, full_scale=0.8)
    closed = eye_metrics(t, 0.5 + 0.02 * np.random.default_rng(0).standard_normal(t.size), d)
    print(
        f"inverted : polarity {inv['polarity']:+d}, VECP {inv['vecp_db']:.2f} dB (upright {m['vecp_db']:.2f})"
    )
    print(f"bipolar  : ER {bip['er_db']}, OMA {bip['oma_norm']:.3f}, VECP {bip['vecp_db']:.2f} dB")
    print(
        f"closed   : eye_h {closed['eye_h_norm']:.3f}, width {closed['eye_w_ui_1s']:.2f} UI, VECP {closed['vecp_db']:.0f} dB (cap)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The eye as a registry measurement

    Wrap the waveform in a `WaveDataset` (a rawfile loads into the same object) and ask for the eye
    by recipe. The recipe carries the stimulus (`fmt`, `rate_gbd`, and any `Data` field that is not
    the default), so the measurement is reproducible from the row alone.
    """)
    return


@app.cell
def _(
    WaveAnalysis,
    WaveDataset,
    WaveSignal,
    measure_dataset,
    measure_many,
    measurement_catalog,
    t,
    x,
):
    tran = WaveAnalysis(
        analysis="tran",
        native_name="Transient Analysis",
        signals={"time": WaveSignal("time", t, "s"), "v(pout)": WaveSignal("v(pout)", x, "V")},
        sweep="time",
    )
    ds = WaveDataset(source="synthetic", engine="ngspice", analyses={"tran": tran})

    base = {"out": "v(pout)", "fmt": "pam4", "rate_gbd": 10.0}
    print({k: v for k, v in measurement_catalog().items() if v["kind"] == "eye"})
    print("vecp_db via recipe:", round(measure_dataset(ds, {"meas": "vecp_db", **base}), 3))
    rows = measure_many(
        ds, {n: {"meas": n, **base} for n in ("eye_h_norm", "eye_w_ui_1s", "er_db", "rlm")}
    )
    print(
        {
            k: (round(v["value"], 3) if v["value"] is not None else v["error"])
            for k, v in rows.items()
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The fold plot

    `fold()` returns eye-diagram coordinates over the scored window (two UI wide); draw it with any
    plotting library.
    """)
    return


@app.cell
def _(d, fold, m, t, x):
    import matplotlib.pyplot as plt
    from IPython.display import display

    fig, axs = plt.subplots(1, 2, figsize=(8, 3), dpi=100)
    for ax, filt, lab in (
        (axs[0], False, "unfiltered"),
        (axs[1], True, "after the BT4 reference receiver"),
    ):
        ph, y = fold(t, x, d, filtered=filt)
        ax.plot(ph * 1e12, y, ",", color="navy", alpha=0.4)
        ax.set_xlabel("time within 2 UI [ps]")
        ax.set_title(lab, fontsize=9)
    axs[0].set_ylabel("signal")
    fig.suptitle(
        f"PAM4 {d.rate_gbd:g} GBd PRBS{d.order} — VECP {m['vecp_db']:.2f} dB, RLM {m['rlm']:.2f}",
        fontsize=9,
    )
    fig.tight_layout()
    display(fig)
    plt.close(fig)
    return


if __name__ == "__main__":
    app.run()
