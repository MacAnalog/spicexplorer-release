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
    # analog-db sizing playground — pull a circuit, twiddle knobs, see the results

    Your **manual sizing loop** over any catalogue circuit: run the committed sizing as a live
    baseline → edit an override dict → re-run → metric diff table → overlay the waveforms →
    auto-export annotated plots (the waveview *snapshot* machinery). One call — `run_circuit` —
    routes to the circuit's native engine (open PDKs → ngspice here; a closed Spectre-routed lane
    takes the *same* call, see the last section). Simulation cells are **live-gated**: without a
    working ngspice + PDK they skip with an explanation, everything else runs PDK-free.

    Related: [`analog_db_tour`](analog_db_tour.py) (the library itself) ·
    [`gmid_sizing_demo`](gmid_sizing_demo.py) (first-principles gm/ID sizing) ·
    platform `optimizer_quickstart.py` §3 (the *automatic* twin of this loop) ·
    [`ungroup_resizing`](ungroup_resizing.py) (search-space knobs).
    """)
    return


@app.cell
def _():
    # ---- pick your experiment (EDIT ME) -------------------------------------------------
    CIRCUIT = "amp_022_fer_two_stage"   # any catalog id with a lowered PDK binding
    PDK     = "ihp-sg13g2"              # open lane: ihp-sg13g2 / sky130 / gf180mcu
    BENCH   = "ac_open_loop"            # any analyses/<bench>.yaml of the circuit
    CORNER  = "tt"

    import tempfile
    from pathlib import Path

    import pandas as pd

    SCRATCH = Path(tempfile.mkdtemp(prefix="sizing_playground_"))
    print(f"{CIRCUIT} / {PDK} / {BENCH} @ {CORNER}   (scratch: {SCRATCH})")
    return BENCH, CIRCUIT, CORNER, PDK, Path, SCRATCH, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · The circuit's contract — benches + datasheet bands

    PDK-free: the committed manifest, the benches you can point `BENCH` at, and the spec bands
    your experiments are judged against.
    """)
    return


@app.cell
def _(CIRCUIT, pd):
    from spicexplorer_analog_db import model

    ckt = model.load_circuit(CIRCUIT)
    print("class:", ckt.klass, "| pdks:", ckt.pdks, "| benches:", ckt.analyses)
    pd.DataFrame(ckt.datasheet().get("specs", {})).T
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · Baseline — the committed sizing, live

    The gate: `probe_engine` reports the routed engine + availability; the baseline run itself is
    the live test (on a machine without ngspice/PDK it fails cleanly and the rest of the notebook
    no-ops). `evaluate()` scores every datasheet metric through the engine-neutral registry.
    """)
    return


@app.cell
def _(BENCH, CIRCUIT, CORNER, PDK, mo, pd):
    from spicexplorer.backends.analog_db import load_sizing, probe_engine, run_circuit

    def metric_table(run):
        ev = run.evaluate()
        return pd.DataFrame({
            name: {"measured": e.value, "spec_min": e.spec_min, "spec_max": e.spec_max,
                   "pass": e.satisfied}
            for name, e in ev.items()
        }).T

    print(probe_engine(CIRCUIT, PDK))
    LIVE, baseline, base_metrics = False, None, None
    try:
        baseline = run_circuit(CIRCUIT, PDK, testbench=BENCH, corner=CORNER, label="baseline")
        LIVE = baseline.artifact_path() is not None
    except Exception as exc:
        print(f"SKIPPED - live SPICE unavailable here ({exc}); simulation cells below no-op.")
    if LIVE:
        base_metrics = metric_table(baseline)
        mo.output.append(base_metrics)
    return LIVE, base_metrics, baseline, load_sizing, metric_table, run_circuit


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · The knobs — the committed sizing you are allowed to twiddle

    These are the circuit's `.param` sizing knobs (`pdk/<pdk>/sizing.yaml`). Values are
    engineering strings (`"8u"`, `"2e-12"`) or plain numbers.
    """)
    return


@app.cell
def _(CIRCUIT, PDK, load_sizing, pd):
    committed = load_sizing(CIRCUIT, PDK)
    pd.DataFrame({"committed": committed}).sort_index()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · Your experiment — edit `OVERRIDES`, re-run, diff

    `run_circuit(..., sizing_overrides=...)` edits the deck's `.param` knobs before the run.
    A **typo'd knob name warns and keeps the committed value** (it is never silently inserted
    as a dangling `.param`). The seeded example halves the Miller cap — watch `ugf_hz` rise
    and `pm_deg` fall in the diff.
    """)
    return


@app.cell
def _(
    BENCH,
    CIRCUIT,
    CORNER,
    LIVE,
    PDK,
    base_metrics,
    metric_table,
    mo,
    pd,
    run_circuit,
):
    OVERRIDES = {
        "x_dut_cc_value": "1p",    # committed 2e-12 - half the Miller cap
        # "x_dut_xm0_w": "16u",    # ...or widen the input pair (committed 8u)
    }

    modified = mod_metrics = None
    if LIVE:
        modified = run_circuit(CIRCUIT, PDK, testbench=BENCH, corner=CORNER,
                               sizing_overrides=OVERRIDES, label="modified")
        mod_metrics = metric_table(modified)
        diff = pd.DataFrame({
            "baseline": base_metrics["measured"],
            "modified": mod_metrics["measured"],
        })
        diff["delta"] = diff["modified"] - diff["baseline"]
        diff["spec_min"] = base_metrics["spec_min"]
        diff["spec_max"] = base_metrics["spec_max"]
        diff["pass_now"] = mod_metrics["pass"]
        mo.output.append(diff)
    return mod_metrics, modified


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 · Look at the waves — overlay + annotated snapshots

    Numbers lie by omission; traces don't. Baseline-vs-modified overlay of the bench's output
    wave, then the full **snapshot** export (combined + per-signal PNGs, interactive Plotly
    HTML twins, and a `.traces.npz` store that round-trips into the measurement registry).
    """)
    return


@app.cell
def _(
    BENCH,
    CIRCUIT,
    LIVE,
    Path,
    SCRATCH,
    baseline,
    mo,
    mod_metrics,
    modified,
):
    PLOT_SIGNALS = ["vout", "vin"]  # EDIT ME - signals to overlay, each tried engine/spelling-
                                     # tolerant (e.g. "vout" also matches ngspice's "v(vout)");
                                     # a name absent from this bench's nodes is skipped with the
                                     # bench's actual signal list printed, so you know what to swap in

    if LIVE:
        import dataclasses

        import numpy as np
        import plotly.graph_objects as go
        from spicexplorer_waveview import PLOT_TEMPLATES, PlotTemplate, load_result, snapshot

        key = baseline.analysis  # the bench's engine-neutral analysis kind
        line_style = {"baseline": "solid", "modified": "dash"}
        _fig = go.Figure()
        is_db = False
        resolved_signals = []  # actual dataset signal names behind PLOT_SIGNALS, in plot order
        for name, run in (("baseline", baseline), ("modified", modified)):
            ds = load_result(run.artifact_path())
            an = ds.resolve_analysis(key) or next(iter(ds.analyses.values()))
            x = np.real(np.asarray(an.signals[an.sweep].data))
            for base in PLOT_SIGNALS:
                sig = ds.find_signal(an.analysis, base)
                if sig is None:
                    if name == "baseline":  # warn once per signal, not once per run
                        top_level = sorted(n for n in an.signals if "#" not in n)  # drop
                        # internal OSDI model states (e.g. "n.xdut.xm0.nsg13_lv_pmos#gp") -
                        # circuit-level nodes/ports never contain "#"
                        print(f"'{base}' not in this bench - available: {top_level}")
                    continue
                if sig.name not in resolved_signals:
                    resolved_signals.append(sig.name)
                y = np.asarray(sig.data)
                if np.iscomplexobj(y):
                    is_db = True
                    y = 20 * np.log10(np.maximum(np.abs(y), 1e-300))
                else:
                    y = np.real(y)
                _fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"{name} {base}",
                                         line=dict(dash=line_style[name])))
        if is_db:
            _fig.update_xaxes(title_text="frequency (Hz)", type="log")
            _fig.update_yaxes(title_text="magnitude (dB)")
        else:
            _fig.update_xaxes(title_text=an.sweep or "sweep")
            _fig.update_yaxes(title_text="signal")
        _fig.update_layout(title=f"{CIRCUIT} / {BENCH}: baseline vs modified ({', '.join(PLOT_SIGNALS)})",
                          template="plotly_white", hovermode="x unified", height=420)
        mo.output.append(_fig)

        # pin the snapshot export to the SAME signals as the overlay above - snapshot()'s
        # own default (no templates=) falls back to its preferred-node heuristic (up to 8
        # traces), which is why the exported PNG used to show every node instead of just
        # PLOT_SIGNALS
        templates = None
        if resolved_signals:
            base_tmpl = PLOT_TEMPLATES.get(key, PlotTemplate("xy", "Traces"))
            templates = {key: dataclasses.replace(base_tmpl, signals=tuple(resolved_signals))}

        # the run's own metric values ride the figures as annotations
        anno = {key: {n: float(v) for n, v in mod_metrics["measured"].head(4).items()}}
        snap = snapshot(load_result(modified.artifact_path()), SCRATCH / "snap",
                        label="modified", annotations=anno, templates=templates)
        for p in snap["pngs"]:
            if Path(p).name.count(".") == 1:  # combined images inline; breakouts stay on disk
                mo.output.append(mo.image(src=str(p)))
        print("full set (per-signal breakouts + interactive HTML + traces):", SCRATCH / "snap")
    return (go,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6 · Mini-sweep — one knob, a few points

    The 30-second version of a sizing study. For a real search over many knobs with scoring,
    graduate to the optimizer (`optimizer_quickstart.py` §3 drives these same decks).
    """)
    return


@app.cell
def _(BENCH, CIRCUIT, CORNER, LIVE, PDK, go, mo, pd, run_circuit):
    SWEEP_KNOB    = "x_dut_xm0_w"          # input-pair width (committed 8u)
    SWEEP_VALUES  = ["4u", "8u", "16u"]
    SWEEP_METRICS = ["dc_gain_db", "ugf_hz", "pm_deg"]

    if LIVE:
        from plotly.subplots import make_subplots

        rows = []
        for v in SWEEP_VALUES:
            r = run_circuit(CIRCUIT, PDK, testbench=BENCH, corner=CORNER,
                            sizing_overrides={SWEEP_KNOB: v}, label=f"sweep_{v}")
            ev = r.evaluate()
            rows.append({"value": v, **{m: ev[m].value for m in SWEEP_METRICS if m in ev}})
        sweep = pd.DataFrame(rows).set_index("value")
        mo.output.append(sweep)

        _fig = make_subplots(rows=1, cols=len(sweep.columns), subplot_titles=list(sweep.columns))
        for i, m in enumerate(sweep.columns, start=1):
            _fig.add_trace(go.Scatter(x=list(sweep.index), y=sweep[m], mode="lines+markers",
                                     name=m, showlegend=False), row=1, col=i)
        _fig.update_layout(title=f"{SWEEP_KNOB} sweep - {BENCH}", template="plotly_white",
                          height=380)
        mo.output.append(_fig)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7 · The closed (Spectre) lane + where to go next

    The **same call** runs a Spectre-routed binding natively on Spectre when the operator kit is
    configured (kit-gated; see `analog_db_in_library.py` §4):

    ```python
    run = run_circuit(CIRCUIT, SPECTRE_PDK, testbench=BENCH,
                      model_lib_root="~/.spicexplorer/models",     # neutral corner wrapper
                      deck_dir=SCRATCH / "decks", work_dir=SCRATCH / "raw",
                      sizing_overrides=OVERRIDES)                  # same seam, same diff flow
    ```

    `evaluate()`, the overlay, and `snapshot()` work unchanged there — including the clocked
    golden benches (`ia_002` `pac_gain` / `pnoise_chopped`), whose PSS/PAC/pnoise analyses render
    through the same per-analysis plot templates.

    **Takeaways**
    * `run_circuit(..., sizing_overrides={knob: value})` — the manual sizing seam, both lanes;
      unknown knobs warn and keep the committed value.
    * `evaluate()` judges every experiment against the committed datasheet bands.
    * `snapshot(run.artifact_path(), out_dir, annotations=...)` keeps the visual evidence.
    * Auto-sizing over the same decks: `optimizer_quickstart.py` §3; first-principles device
      sizing: `gmid_sizing_demo.py`; knob grouping/`ungroup:`: `ungroup_resizing.py`.
    """)
    return


if __name__ == "__main__":
    app.run()
