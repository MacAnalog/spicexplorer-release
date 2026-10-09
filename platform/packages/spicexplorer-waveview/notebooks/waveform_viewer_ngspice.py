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
    # Waveform viewer — live ngspice tour

    The **universal result viewer** (`spicexplorer_waveview`) on real ngspice artifacts: this
    notebook runs analog-db benches for `amp_022_fer_two_stage` on `ihp-sg13g2` through the
    in-library router (a real ngspice simulation per bench), then loads each run's `.raw`
    into a `WaveDataset` and demonstrates:

    - interactive Plotly figures per analysis (Bode / transient / DC sweep / noise / FFT),
      with **Tier-1 registry measurements drawn on the plots** — the same math the optimizer
      scores with, so the numbers and the curves can never disagree;
    - the measurement API (`measure_dataset` / `measure_many`) — every `{meas: …}` recipe the
      registry knows runs against viewer-loaded data;
    - the **simulator log viewer** (severity-classified, colourised).

    Requires live SPICE: ngspice on `PATH` + the IHP PDK resolvable (the research server or
    the Docker `api` container). The REST twin of everything here is
    [`waveview_api_tour.py`](waveview_api_tour.py).
    """)
    return


@app.cell
def _():
    import plotly.io as pio

    pio.renderers.default = "notebook_connected"

    from spicexplorer_core import project_root
    from spicexplorer_core.env import probe_env

    ENV = probe_env()
    assert ENV["live_runs_enabled"], f"live SPICE unavailable here: {ENV}"
    WORK = project_root() / "work" / "waveview_demo_ngspice"
    print({k: ENV[k] for k in ("ngspice_ok", "pdk_ok", "tech", "live_runs_enabled")})
    return WORK, project_root


@app.cell
def _(WORK, project_root):
    # one real ngspice run per bench (the in-library router; ~5-15 s each)
    from spicexplorer.backends.analog_db import run_circuit

    CIRCUIT, PDK = "amp_022_fer_two_stage", "ihp-sg13g2"
    BENCHES = ["ac_open_loop", "tran_step", "linearity", "noise", "thd"]
    runs, raws = {}, {}
    for tb in BENCHES:
        outdir = WORK / tb
        runs[tb] = run_circuit(CIRCUIT, PDK, testbench=tb, output_dir=str(outdir))
        raws[tb] = sorted(outdir.rglob("*.raw"))[0]
        print(f"{tb:14s} -> {raws[tb].relative_to(project_root())}")
    return raws, runs


@app.cell
def _(raws):
    # a path is all the viewer needs — engine sniffing, log discovery, analysis mapping
    from spicexplorer_waveview import load_result

    ds_ac = load_result(raws["ac_open_loop"])
    print(f"engine={ds_ac.engine}  log={ds_ac.log_path is not None}")
    for key, _an in ds_ac.analyses.items():
        print(
            f"  {key:6s} ({_an.native_name}): sweep={_an.sweep!r}, {len(_an.signals)} signals, {_an.n_points} pts"
        )
    return ds_ac, load_result


@app.cell
def _(ds_ac):
    # Bode plot with the registry's own numbers annotated (dcgain / UGF / PM / f3dB)
    from spicexplorer_waveview import bode_figure

    bode_figure(ds_ac, "v(vout)", title="amp_022 open-loop transfer (ihp-sg13g2, live ngspice)")
    return


@app.cell
def _(ds_ac, runs):
    # ... and the same figures as numbers: any Tier-1 recipe evaluates on the loaded data.
    # Cross-checked against the run's own datasheet evaluation (identical registry math).
    import pandas as pd
    from spicexplorer_waveview import measure_many

    table = measure_many(
        ds_ac,
        {
            "dcgain [dB]": {"meas": "dcgain", "out": "v(vout)"},
            "ugf [Hz]": {"meas": "ugf", "out": "v(vout)"},
            "pm [deg]": {"meas": "pm", "out": "v(vout)"},
            "f3db [Hz]": {"meas": "f3db", "out": "v(vout)"},
            "gbw [Hz·dB]": {"meas": "gbw", "out": "v(vout)"},
        },
    )
    engine = {f"{m.name}": m.value for m in runs["ac_open_loop"].evaluate().values()}
    print("router's own evaluate():", {k: round(v, 4) for k, v in engine.items()})
    pd.DataFrame(table).T
    return


@app.cell
def _(load_result, raws):
    # transient bench: settling overlay (t_settle band + slew) straight from the registry
    from spicexplorer_waveview import tran_figure

    ds_tr = load_result(raws["tran_step"])
    tran_figure(
        ds_tr,
        ["v(vout)"],
        settle={"out": "v(vout)", "tol_frac": 0.01},
        title="amp_022 buffer step response (live ngspice)",
    )
    return


@app.cell
def _(load_result, raws):
    # DC linearity sweep: the ICMR tracking band shaded on the transfer
    # (the deck sweeps the buffer input at v(vinp); its in-deck CROSS meas is only a hint —
    #  the registry's icmr_band reads the widest contiguous tracking band)
    from spicexplorer_waveview import dc_figure

    ds_dc = load_result(raws["linearity"])
    dc_figure(
        ds_dc,
        "v(vout)",
        vin="v(vinp)",
        icmr={"vin": "v(vinp)", "vtrack": 0.05},
        title="amp_022 buffer DC transfer + ICMR (live ngspice)",
    )
    return


@app.cell
def _(load_result, raws):
    # noise: this deck integrates IN-DECK (ngspice writes the Integrated Noise plot),
    # so the viewer reads the totals as scalars. Density-sweep viewing (loglog figure +
    # registry integration) is demonstrated on the Spectre lane's noise.noise PSF.

    ds_no = load_result(raws["noise"])
    an = ds_no.analyses["noise"]
    print("plot in raw:", an.native_name)
    {k: f"{v * 1e6:.2f} µV rms" for k, v in an.scalars.items()}
    return


@app.cell
def _(load_result, raws, runs):
    # distortion bench: quick-look FFT of the tran + the scored coherent THD recipe
    from spicexplorer_core.eng import parse_value
    from spicexplorer_waveview import fft_spectrum_figure, measure_dataset

    ds_thd = load_result(raws["thd"])
    f0 = float(parse_value(str(runs["thd"].params.get("F0", "1e6"))))
    thd = measure_dataset(ds_thd, {"meas": "thd_pct", "out": "v(vout)", "f0": f0})
    print(f"registry thd_pct = {thd:.4f} %  (f0 = {f0:.3g} Hz)")
    fft_spectrum_figure(ds_thd, "v(vout)", title=f"amp_022 THD bench FFT (thd = {thd:.4f} %)")
    return


@app.cell
def _(ds_ac):
    # the log viewer: severity-classified, colourised, scrollable (works on any sim log)
    from IPython.display import HTML
    from spicexplorer_waveview import log_view_html, parse_sim_log

    summary = parse_sim_log(ds_ac.log_path)
    print("severity counts:", summary.counts)
    HTML(log_view_html(summary, height=260))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Where next** — the REST twin ([`waveview_api_tour.py`](waveview_api_tour.py))
    serves these exact capabilities over `/api/waveview/*` (open/wave/measure/scalars/log +
    an SSE live tail); [`waveform_viewer_spectre.py`](waveform_viewer_spectre.py) is
    the same tour on Cadence Spectre PSF results (PSS spectrum, stb loop gain, per-device
    op-point tables).
    """)
    return


if __name__ == "__main__":
    app.run()
