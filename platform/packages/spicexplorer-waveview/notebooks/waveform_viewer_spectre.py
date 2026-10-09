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
    # Waveform viewer — Cadence Spectre (PSF) tour

    The same universal viewer on **Spectre psfascii raw dirs**: run analog-db benches for
    `amp_022_fer_two_stage` on the closed `generic-n65` lane (native Spectre via
    virtuoso-bridge), then point `load_result` at each persisted `-raw` directory.

    Spectre-specific goodies demonstrated here:

    - the **PSS harmonic spectrum** (`pss.fd.pss` complex phasors) with THD/HD2/HD3/SFDR
      labels from the native-PSS recipe family;
    - the **stb loop-gain** Bode with `pm_loop`/`gain_margin_db` — cross-checked against
      Spectre's own `stb.margin.stb` native margins;
    - **per-device op-point tables** from the `*.info` STRUCT post-parse (`inst:param`
      scalars: gm, vth, ids, …) — the ADE model dumps are never read (NDA guard).

    Opt-in environment (the P5c live-bridge recipe): `virtuoso_bridge` importable,
    `SPICEXPLORER_SPECTRE_MODEL_ROOT` → the neutral corner wrapper dir,
    `SPICEXPLORER_VB_ENV_FILE` → the bridge env (local mode on the research server).
    """)
    return


@app.cell
def _():
    import os

    import plotly.io as pio

    pio.renderers.default = "notebook_connected"

    from spicexplorer_core import project_root

    MODEL_ROOT = os.environ.get(
        "SPICEXPLORER_SPECTRE_MODEL_ROOT", os.path.expanduser("~/.spicexplorer/models")
    )
    VB_ENV = os.environ.get(
        "SPICEXPLORER_VB_ENV_FILE", os.path.expanduser("~/.virtuoso-bridge/local.env")
    )
    WORK = project_root() / "work" / "waveview_demo_spectre"

    import importlib.util
    from pathlib import Path

    assert importlib.util.find_spec("virtuoso_bridge"), "virtuoso-bridge not installed in this venv"
    assert Path(MODEL_ROOT, "generic_n65_models.scs").is_file(), MODEL_ROOT
    print("bridge + model wrapper OK")
    return MODEL_ROOT, VB_ENV, WORK


@app.cell
def _(MODEL_ROOT, VB_ENV, WORK):
    # one native-Spectre run per bench (composed decks; the persistent daemon makes these fast)
    from spicexplorer.backends.analog_db import run_circuit

    CIRCUIT, PDK = "amp_022_fer_two_stage", "generic-n65"
    BENCHES = ["ac_open_loop", "noise", "thd", "stb"]
    runs, rawdirs = {}, {}
    for tb in BENCHES:
        base = WORK / tb
        runs[tb] = run_circuit(
            CIRCUIT,
            PDK,
            testbench=tb,
            model_lib_root=MODEL_ROOT,
            deck_dir=base / "decks",
            work_dir=base / "raw",
            vb_env_file=VB_ENV,
        )
        rawdirs[tb] = runs[tb].result.raw_dir
        print(f"{tb:14s} -> {rawdirs[tb]}")
    return rawdirs, runs


@app.cell
def _(rawdirs):
    # a Spectre raw dir loads exactly like an ngspice .raw — one call, engine-sniffed
    from spicexplorer_waveview import load_result

    ds_ac = load_result(rawdirs["ac_open_loop"])
    print(f"engine={ds_ac.engine}")
    for key, an in ds_ac.analyses.items():
        print(
            f"  {key:6s} ({an.native_name}): sweep={an.sweep!r}, {len(an.signals)} signals, {len(an.scalars)} scalars"
        )
    return ds_ac, load_result


@app.cell
def _(ds_ac):
    from spicexplorer_waveview import bode_figure

    bode_figure(ds_ac, "vout", title="amp_022 open-loop transfer (generic-n65, live Spectre)")
    return (bode_figure,)


@app.cell
def _(ds_ac, runs):
    # parity: viewer measurements == the router's own datasheet evaluation, engine-neutrally
    import pandas as pd
    from spicexplorer_waveview import measure_many

    table = measure_many(
        ds_ac,
        {
            "dcgain [dB]": {"meas": "dcgain", "out": "vout"},
            "ugf [Hz]": {"meas": "ugf", "out": "vout"},
            "pm [deg]": {"meas": "pm", "out": "vout"},
        },
    )
    engine = {
        m.name: m.value
        for m in runs["ac_open_loop"].evaluate(only={"dc_gain_db", "ugf_hz", "pm_deg"}).values()
    }
    print("router's own evaluate():", {k: round(v, 4) for k, v in engine.items()})
    pd.DataFrame(table).T
    return (pd,)


@app.cell
def _(ds_ac, pd):
    # per-device op-point (the *.info STRUCT post-parse): gm/ID-speak for every device
    op = ds_ac.analyses["op"].scalars
    devices = sorted({k.rsplit(":", 1)[0] for k in op if ":" in k})
    params = ["ids", "gm", "gds", "vth", "vdsat", "region"]
    pd.DataFrame({d: {p: op.get(f"{d}:{p}") for p in params} for d in devices}).T
    return


@app.cell
def _(load_result, rawdirs):
    # native-PSS distortion: harmonic phasor spectrum + the thd_pss recipe family
    from spicexplorer_waveview import pss_spectrum_figure

    ds_thd = load_result(rawdirs["thd"])
    pss_spectrum_figure(ds_thd, "vout", title="amp_022 follower PSS spectrum (generic-n65)")
    return


@app.cell
def _(bode_figure, load_result, rawdirs):
    # stb loop gain: registry margins on the loopGain wave, cross-checked against
    # Spectre's own stb.margin.stb native values (loaded as scalars on the stb: sibling)
    from spicexplorer_waveview import measure_dataset

    ds_stb = load_result(rawdirs["stb"])
    margin = next(an for k, an in ds_stb.analyses.items() if k.startswith("stb:"))
    pm = measure_dataset(ds_stb, {"meas": "pm_loop", "out": "loopGain"})
    gm = measure_dataset(ds_stb, {"meas": "gain_margin_db", "out": "loopGain"})
    print(f"registry: pm_loop={pm:.2f} deg, gain_margin={gm:.3f} dB")
    print(
        f"Spectre native: phaseMargin={margin.scalars['phaseMargin']:.2f} deg, "
        f"gainMargin={margin.scalars['gainMargin']:.3f} dB"
    )
    bode_figure(ds_stb, "loopGain", analysis="stb", title="amp_022 loop gain (stb bench)")
    return


@app.cell
def _(load_result, rawdirs):
    # noise density + integrated total (same recipe the datasheet scores)
    from spicexplorer_waveview import noise_figure

    ds_no = load_result(rawdirs["noise"])
    noise_figure(ds_no, "out", analysis="noise", title="amp_022 output noise density (generic-n65)")
    return


@app.cell
def _(ds_ac):
    # the Spectre run log through the same log viewer
    from IPython.display import HTML
    from spicexplorer_waveview import log_view_html, parse_sim_log

    summary = parse_sim_log(ds_ac.log_path) if ds_ac.log_path else None
    print("severity counts:", summary.counts if summary else "(no log discovered)")
    HTML(log_view_html(summary, height=240)) if summary else None
    return


if __name__ == "__main__":
    app.run()
