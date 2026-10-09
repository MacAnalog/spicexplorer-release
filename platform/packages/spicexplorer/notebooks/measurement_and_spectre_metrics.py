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
    # spicexplorer — engine-neutral measurements & the Spectre backend

    The **`spicexplorer`** package is the optimizer + YAML DSL, and it owns the two seams that turn a
    raw simulation into a *score*: the engine-neutral **measurement registry** and the optional
    **Cadence Spectre backend** (`backends/`). This notebook is the package's documentation tour of
    that metric path — the same figures of merit (DC gain, UGF, phase margin, f₃dB, GBW, integrated
    noise) computed identically for **ngspice and Spectre**, ending on a live **licensed-kit** run.

    **Layering.** The math itself lives one layer down in `spicexplorer-core`
    (`spicexplorer_core.measurements`: pure numpy over raw arrays — no simulator). `spicexplorer`
    wires it into the loop (`optimization/measure_integration.py`) and reads Spectre PSFs
    (`backends/spectre.py`). Nothing here needs a PDK.

    > **Runs anywhere.** Every code cell below is offline and deterministic — it feeds *analytic*
    > PSFs through the very same reader/registry the live path uses. The final section shows the
    > **recorded** live-licensed-kit numbers (reproduced by the opt-in `slow` tests); no NDA kit data is
    > ever read or embedded here.
    """)
    return


@app.cell
def _():
    import os
    import tempfile
    from importlib.util import find_spec
    from pathlib import Path

    import matplotlib.pyplot as plt
    import numpy as np

    # The optional Spectre backend — the bridge is imported lazily inside the factory, so the
    # PSF reader + deck composer imported here are free of any Cadence dependency.
    from spicexplorer.backends.spectre import SpectreSimResult, read_swept_psf
    from spicexplorer.backends.spectre_deck import (
        ac_analysis,
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
        noise_analysis,
        render_spectre_deck,
        sine_source,
        transient_analysis,
    )

    # The engine-neutral measurement library (spicexplorer-core; pure numpy, no simulator)
    from spicexplorer_core.measurements import (
        bandwidth_3db,
        dc_gain_db,
        gain_bandwidth_product,
        harmonic_amplitudes,
        known_measurements,
        magnitude_db,
        measure,
        phase_margin,
        thd_from_waveform,
        unity_gain_freq,
    )

    BRIDGE = find_spec("virtuoso_bridge") is not None
    KIT = bool(os.environ.get("SPICEXPLORER_SPECTRE_MODELS"))
    SPECTRE_LIVE = BRIDGE and KIT
    print("canonical measurements:", ", ".join(known_measurements()))
    print(
        f"virtuoso-bridge importable: {BRIDGE} | licensed kit configured: {KIT} | live Spectre: {SPECTRE_LIVE}"
    )
    print("(offline cells run anywhere; the live section shows recorded numbers)")
    return (
        Path,
        SPECTRE_LIVE,
        SpectreSimResult,
        ac_analysis,
        bandwidth_3db,
        dc_gain_db,
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
        find_spec,
        gain_bandwidth_product,
        harmonic_amplitudes,
        magnitude_db,
        measure,
        noise_analysis,
        np,
        os,
        phase_margin,
        plt,
        read_swept_psf,
        render_spectre_deck,
        sine_source,
        tempfile,
        thd_from_waveform,
        transient_analysis,
        unity_gain_freq,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · The measurement math is engine-neutral

    `spicexplorer_core.measurements.waveforms` is the single source of truth for *what UGF/PM/…
    mean* — array-in, scalar-out, unit-tested against synthetic transfer functions. Here is a
    synthetic open-loop response (DC gain 60 dB, dominant pole 1 kHz, second pole 40 MHz) with the
    figures of merit extracted straight from the arrays.
    """)
    return


@app.cell
def _(
    bandwidth_3db,
    dc_gain_db,
    gain_bandwidth_product,
    magnitude_db,
    np,
    phase_margin,
    plt,
    unity_gain_freq,
):
    f = np.logspace(0, 9, 1200)
    A0, fp1, fp2 = 1000.0, 1.0e3, 40.0e6  # 60 dB, 1 kHz dominant pole, 40 MHz second pole
    H = A0 / ((1 + 1j * f / fp1) * (1 + 1j * f / fp2))

    metrics = {
        "dc_gain_db": dc_gain_db(f, H),
        "ugf_hz": unity_gain_freq(f, H),
        "phase_margin_deg": phase_margin(f, H),
        "f3db_hz": bandwidth_3db(f, H),
        "gbw_hz": gain_bandwidth_product(f, H),
    }
    for k, v in metrics.items():
        print(f"{k:>18}: {v:.4g}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    ax1.semilogx(f, magnitude_db(H))
    ax1.axhline(0, color="k", lw=0.5, ls=":")
    ax1.axvline(
        metrics["ugf_hz"],
        color="r",
        lw=0.8,
        ls="--",
        label=f"UGF {metrics['ugf_hz'] / 1e6:.1f} MHz",
    )
    ax1.set_ylabel("|H|  [dB]")
    ax1.legend()
    ax1.grid(True, which="both", alpha=0.3)
    ax2.semilogx(f, np.degrees(np.unwrap(np.angle(H))))
    ax2.set_ylabel("phase  [deg]")
    ax2.set_xlabel("frequency  [Hz]")
    ax2.grid(True, which="both", alpha=0.3)
    fig.suptitle(f"synthetic two-pole — PM {metrics['phase_margin_deg']:.0f}°")
    fig.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · The `{meas: …}` registry over a `SimResult`

    A `TargetSpec.measurement` recipe names a canonical figure of merit and the signal it reads:
    `{meas: dcgain, out: vout}`. `measure()` pulls the wave off **any** `SimResult` and evaluates the
    pure math above — so the recipe is identical whether the run was ngspice or Spectre.

    For Spectre, a frequency-domain sweep lands in its **own** psfascii PSF (`ac.ac`) in the run's
    `-raw` dir, *not* the bridge's flat op-point dict. `SpectreSimResult.wave` reads it lazily via
    `read_swept_psf`. Below we synthesize a single-pole `ac.ac` — byte-for-byte the shape Spectre
    emits — and run the registry on it, no simulator required.
    """)
    return


@app.cell
def _(Path, SpectreSimResult, measure, np, read_swept_psf, tempfile):
    def write_ac_psf(path: Path, A0: float = 1000.0, fp: float = 1.0e3, n: int = 241) -> None:  # pyright: ignore[reportInvalidTypeForm] -- `Path` reaches this cell as a parameter of the cell function, which pyright reads as a variable
        freqs = np.logspace(0, 8, n)
        h = A0 / (1 + 1j * freqs / fp)
        lines = [
            "HEADER",
            '"PSFversion" "1.00"',
            '"analysis type" "ac"',
            "TYPE",
            '"sweep" FLOAT DOUBLE PROP(',
            '"key" "sweep"',
            ")",
            '"V" COMPLEX DOUBLE PROP(',
            '"units" "V"',
            ")",
            "SWEEP",
            '"freq" "sweep" PROP(',
            '"units" "Hz"',
            ")",
            "TRACE",
            '"vout" "V"',
            "VALUE",
        ]
        for fr, hv in zip(freqs, h):
            lines += [f'"freq" {fr:.15e}', f'"vout" ({hv.real:.15e} {hv.imag:.15e})']
        lines.append("END")
        path.write_text("\n".join(lines) + "\n")

    ac_dir = Path(tempfile.mkdtemp())
    write_ac_psf(ac_dir / "ac.ac")
    res = SpectreSimResult({}, raw_dir=str(ac_dir))  # exactly what a bridge Spectre run hands back

    for meas in ("dcgain", "ugf", "pm"):
        print(
            f"{meas:>6}: {measure(res, {'meas': meas, 'out': 'vout'}, default_analysis='ac'):.4g}"
        )
    print("\nread_swept_psf('ac') exposes:", sorted(read_swept_psf(ac_dir, "ac")))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · Integrated noise

    `inoise_total` / `onoise_total` integrate a one-sided spectral density over the swept band to an
    RMS (`integrated_noise` = √∫ S(f) df). A Spectre `noise` analysis writes its **output**- and
    **input**-referred densities as the `out` / `in` traces of a `noise.noise` PSF — read the same
    way. With a flat (white) density the integral is closed-form, so we can check the reader exactly.
    """)
    return


@app.cell
def _(Path, SpectreSimResult, measure, np, tempfile):
    def write_noise_psf(path: Path, w_out=10e-9, w_in=2e-9, flo=1.0, fhi=1e6, n=201):  # pyright: ignore[reportInvalidTypeForm] -- `Path` reaches this cell as a parameter of the cell function, which pyright reads as a variable
        freqs = np.logspace(np.log10(flo), np.log10(fhi), n)
        lines = [
            "HEADER",
            '"analysis type" "noise"',
            "TYPE",
            '"sweep" FLOAT DOUBLE PROP(',
            '"key" "sweep"',
            ")",
            '"V" FLOAT DOUBLE PROP(',
            '"units" "V/sqrt(Hz)"',
            ")",
            "SWEEP",
            '"freq" "sweep" PROP(',
            '"units" "Hz"',
            ")",
            "TRACE",
            '"out" "V"',
            '"in" "V"',
            "VALUE",
        ]
        for fr in freqs:
            lines += [f'"freq" {fr:.15e}', f'"out" {w_out:.15e}', f'"in" {w_in:.15e}']
        lines.append("END")
        path.write_text("\n".join(lines) + "\n")
        return w_out, w_in, flo, fhi

    nz_dir = Path(tempfile.mkdtemp())
    w_out, w_in, flo, fhi = write_noise_psf(nz_dir / "noise.noise")
    resn = SpectreSimResult({}, raw_dir=str(nz_dir))
    onoise = measure(resn, {"meas": "onoise_total", "out": "out"}, default_analysis="noise")
    inoise = measure(resn, {"meas": "inoise_total", "out": "in"}, default_analysis="noise")
    print(
        f"onoise_total: {onoise * 1e6:.3f} uV rms   (closed form {w_out * np.sqrt(fhi - flo) * 1e6:.3f} uV)"
    )
    print(
        f"inoise_total: {inoise * 1e6:.3f} uV rms   (closed form {w_in * np.sqrt(fhi - flo) * 1e6:.3f} uV)"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · Distortion (THD) from a transient

    THD closes the analysis-coverage gradient (op → AC → noise → **THD**), and it is engine-neutral:
    a transient output — from ngspice **or** a Spectre `tran` — becomes a total-harmonic-distortion
    number via `thd_from_waveform`, which *coherently* resamples a whole number of fundamental periods
    and takes an integer-bin FFT so every harmonic lands exactly on a bin (the discrete analogue of
    SPICE `.four`, no window needed). The `{meas: thd | thd_pct | thd_db}` recipe reads the same
    `tran.tran` wave the swept-PSF reader exposes. On the Spectre side, `transient_analysis` (named
    `tran`) + a large-signal `sine_source` compose the deck — the harmonic content is only as clean as
    the transient tolerance, so a THD deck uses `errpreset=conservative`.
    """)
    return


@app.cell
def _(
    Path,
    SpectreSimResult,
    harmonic_amplitudes,
    measure,
    np,
    sine_source,
    tempfile,
    thd_from_waveform,
    transient_analysis,
):
    # A synthetic Spectre `tran` PSF: 1 MHz fundamental (0.1 V) with a -40 dB HD2 and a -46 dB HD3,
    # exactly the tran.tran a bridge run leaves behind — read back through the SAME SimResult path.
    def write_tran_psf(
        path: Path,  # pyright: ignore[reportInvalidTypeForm] -- `Path` reaches this cell as a parameter of the cell function, which pyright reads as a variable
        f0: float,
        amps,
        dc: float = 0.6,
        n_periods: int = 20,
        spp: int = 128,
    ) -> None:
        t = np.arange(n_periods * spp) / (f0 * spp)
        v = dc + sum(a * np.sin(2 * np.pi * (k + 1) * f0 * t) for k, a in enumerate(amps))
        lines = [
            "HEADER",
            '"PSFversion" "1.00"',
            '"analysis type" "tran"',
            "TYPE",
            '"sweep" FLOAT DOUBLE PROP(',
            '"key" "sweep"',
            ")",
            '"V" FLOAT DOUBLE PROP(',
            '"units" "V"',
            ")",
            "SWEEP",
            '"time" "sweep" PROP(',
            '"units" "s"',
            ")",
            "TRACE",
            '"vout" "V"',
            "VALUE",
        ]
        for tv, vv in zip(t, v):  # pyright: ignore[reportArgumentType] -- v is an array (dc plus a sum of sine arrays); pyright infers float
            lines += [f'"time" {tv:.15e}', f'"vout" {vv:.15e}']
        path.write_text("\n".join(lines + ["END"]) + "\n")

    F0 = 1.0e6
    tran_dir = Path(tempfile.mkdtemp())
    write_tran_psf(tran_dir / "tran.tran", F0, amps=(0.1, 1.0e-3, 5.0e-4))
    res_t = SpectreSimResult({}, raw_dir=str(tran_dir))  # what a bridge Spectre tran run hands back

    t = np.real(res_t.wave("time", "tran"))
    vout = np.real(res_t.wave("vout", "tran"))
    amps = harmonic_amplitudes(t, vout, F0, n_harmonics=5)
    thd_direct = thd_from_waveform(t, vout, F0, n_harmonics=5)  # the raw engine-neutral fn
    print("harmonic amplitudes [mV]:", " ".join(f"{a * 1e3:.3f}" for a in amps))

    # the {meas: …} recipe reads the tran.tran wave and calls the SAME fn under the hood
    thd = measure(res_t, {"meas": "thd", "out": "vout", "f0": F0}, default_analysis="tran")
    thd_pct = measure(res_t, {"meas": "thd_pct", "out": "vout", "f0": F0}, default_analysis="tran")
    closed = np.sqrt(1.0e-3**2 + 5.0e-4**2) / 0.1
    print(
        f"thd_from_waveform = {thd_direct:.4e}   |   {{meas: thd}} = {thd:.4e}  ({thd_pct:.4f} %)"
    )
    print(f"closed-form        = {closed:.4e}   ({closed * 100:.4f} %)")

    # the deck-side composers that produce that tran.tran on a real run:
    print("\ntransient:", transient_analysis(20 / F0, step=1 / (F0 * 200)))
    print("stimulus :", sine_source("Vinp", "vinp", "0", dc=0.6, ampl=0.1, freq=F0))
    return (thd_direct,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4b · Native PSS harmonics vs tran+FFT — one figure, two routes

    A Spectre `pss` (composed by `pss_analysis`) lands per-harmonic **complex phasors** in the
    `pss.fd.pss` fd-PSF (sweep `freq` = [0, f₀, 2·f₀, …]) — `{meas: thd_pss | hd2 | hd3 | sfdr}`
    read them directly, with **no resample/window**. The tran+FFT `{meas: thd}` route (§4) stays
    the engine-neutral fallback (ngspice too). The same −40 dB HD2 / −46 dB HD3 signal, both ways:
    """)
    return


@app.cell
def _(measure, np, thd_direct):
    # §4's distortion, expressed as the PSS phasor array (index k = k·f0; 0 = DC)
    phasors = np.array([0.0, 0.1, 1.0e-3, 5.0e-4], dtype=complex)

    class _PssResult:  # SimResult-shaped: wave() returns the harmonic phasors
        def wave(self, name, analysis):
            assert analysis == "pss"
            return phasors

    native = {
        m: measure(_PssResult(), {"meas": m, "out": "vout"}, default_analysis="pss")
        for m in ("thd_pss_pct", "hd2_db", "hd3_db", "sfdr_db")
    }
    print("native PSS :", {k: f"{v:.4g}" for k, v in native.items()})
    print(f"tran+FFT   : thd_pct = {thd_direct * 100:.4g}   (section 4, FFT route)")
    assert abs(native["thd_pss_pct"] - thd_direct * 100) < 0.02  # two routes, one figure

    # Live on amp_022 (generic-n65 follower, 100 mV @ 1 MHz, recorded):
    #   native PSS: THD 0.076 %, HD2 -62 dBc, HD3 -82 dBc  |  tran+FFT: THD 0.077 %
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 · Composing a Spectre deck from an analog-db testbench

    The registry needs a deck to run. `deck_spec_from_ngspice` translates an analog-db ngspice
    testbench (the `amp_022` two-stage OTA) into a Spectre `SpectreDeckSpec`; the analysis builders
    compose the run: `dc_oppoint_analysis()`, `ac_analysis(...)`, and — new in P5c —
    `noise_analysis(output, iprobe=...)`, which emits a `noise ( out 0 ) noise …` statement (the
    `iprobe` is the input source instance, giving the input-referred spectrum). No corner is applied
    here, so the rendered deck carries only device *names* and symbolic sizing — never kit bytes.
    """)
    return


@app.cell
def _(
    Path,
    ac_analysis,
    dc_oppoint_analysis,
    deck_spec_from_ngspice,
    find_spec,
    noise_analysis,
    os,
    render_spectre_deck,
):
    from spicexplorer_core import project_root

    adb = Path(os.environ.get("SPICEXPLORER_ANALOG_DB") or (project_root() / "examples/analog-db"))
    deck = adb / "raw/amp_022_fer_two_stage/generic-n65/noise.spice"
    analyses = (
        dc_oppoint_analysis(),
        ac_analysis(1.0, 1e9, 20),
        noise_analysis("vout", iprobe="VINP", start=1.0e3, stop=1.0e8, dec=50),
    )

    print("composed analyses (engine-neutral -> Spectre statements):")
    for a in analyses:
        print("   ", a)

    if deck.is_file() and find_spec("spicexplorer_circuitgraph"):
        spec = deck_spec_from_ngspice(
            deck, pdk="generic-n65", source_pdk="generic-n65", analyses=analyses
        )
        tail = render_spectre_deck(spec).splitlines()[-6:]
        print("\n-- rendered deck tail (no corner => no kit includes) --")
        print("\n".join(tail))
    else:
        print(
            "\n(analog-db amp_022 generic-n65 deck not checked out here; showing the composer only)"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6 · Live on a licensed kit (recorded)

    The capstone: the registered `amp_022_fer_two_stage / generic-n65` node run on **real licensed-kit
    Spectre** over the virtuoso-bridge, with every figure of merit pulled through the *same* registry
    used above. These numbers are **recorded** from the opt-in `slow` tests — reproduce them with
    `SPICEXPLORER_SPECTRE_MODELS` + the bridge configured:

    * `packages/spicexplorer/tests/test_amp022_spectre_ac_live.py`   (op-point + AC)
    * `packages/spicexplorer/tests/test_amp022_spectre_noise_live.py` (noise)

    Condition: **tt_lvt, 27 °C, 1.2 V core rail, 20 µA bias, 500 fF load** (noise band 1 kHz–100 MHz).
    """)
    return


@app.cell
def _(SPECTRE_LIVE):
    import pandas as pd

    recorded = pd.DataFrame(
        [
            ("op", "XDUT.XM0 gm", "0.237 mS", "operating_point() — .info STRUCT gm/ID slice"),
            ("ac", "dc_gain", "47.4 dB", "measure(meas=dcgain, out=vout)"),
            ("ac", "UGF", "18.0 MHz", "measure(meas=ugf, out=vout)"),
            ("ac", "phase_margin", "61 deg", "measure(meas=pm, out=vout)"),
            ("noise", "onoise_total", "813 uV rms", "measure(meas=onoise_total, out=out)"),
            ("noise", "inoise_total", "210 uV rms", "measure(meas=inoise_total, out=in)"),
        ],
        columns=["analysis", "metric", "value", "how (same registry as the offline cells)"],
    )
    print(f"live Spectre available in THIS kernel: {SPECTRE_LIVE}  (recorded values shown below)")
    recorded
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7 · How this feeds the optimizer

    Both tiers merge post-sim, pre-score, so the scorer seam (`result.scalar(name, analysis)`) is
    unchanged and corner-correct on every eval path:

    * **Tier-1 (engine-neutral Python)** — a `measurement: {meas: …}` recipe on a `target_spec` is
      computed by `optimization/measure_integration.py::MeasureMergeContext` from the result's own
      waves. Pure `core` math, no license/process → runs for **ngspice and Spectre alike**. This is
      everything demonstrated above.
    * **Tier-2 (OCEAN)** — a `{result, expr}` / `{builder, …}` recipe is evaluated by Cadence's own
      calculators over the persisted raw dir (`optimization/ocean_integration.py`), Spectre only.

    **See also:** the package `README.md` (`backends/spectre.py`, `backends/spectre_deck.py`,
    `measure_integration.py` rows), `spicexplorer_core.measurements` (the math + registry), and the
    meta-repo `doc/archive/plan_virtuoso_bridge.md` (P5 metric-registry plan).
    """)
    return


if __name__ == "__main__":
    app.run()
