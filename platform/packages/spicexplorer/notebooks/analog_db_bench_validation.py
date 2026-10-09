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
    # analog-db bench validation — CMRR · PSRR · linearity · THD · IIP3 · STB on both engines

    **TL;DR** — every analog-db amplifier testbench (`ac_open_loop`, `ac_closed_loop`, `cmrr_vcm`,
    `psrr_vdd`, `linearity`, `dc_op`, `noise`, `tran_step`, `thd`, `iip3`, `stb`) now runs through
    the **one** in-library router `run_circuit` on **both** lanes — open (ngspice raw deck) and
    closed (native Spectre via the bridge) — and every datasheet metric scores through the **same**
    measurement registry. The closed lane's analysis statements + SKILL calculator expressions are
    **data** (the analog-db Spectre template DB, §4c), not code.
    Live matrix (tt, recorded 2026-07-09):

    | metric | amp_001_5t ihp (ngspice) | amp_001_5t generic-n65 (Spectre) | amp_022 ihp (ngspice) | amp_022 generic-n65 (Spectre) |
    |---|---|---|---|---|
    | dc_gain_db | 29.8 | 26.1 | 51.5 | 47.4 |
    | ugf_hz | 30.2 M | 32.2 M | 20.9 M | 18.0 M |
    | pm_deg | 61.5° | 78.4° | 80.9° | 60.9° |
    | **cmrr_db** | 29.7 | 33.9 | 64.3 | 58.4 |
    | **psrr_vdd_db** | 29.7 | 28.1 | 76.4 | 96.6 |
    | **icmr_range (V)** | 0.88 | 0.47 | 1.37 | 1.07 |
    | i_supply | 27.5 µA | 25.5 µA | 246 µA | 98.6 µA |
    | vn_in (rms) | 1.71 mV | 1.34 mV | 244 µV | 210 µV |
    | t_settle | 24 ns | 33 ns | 38 ns | 37 ns |
    | **thd_pct** (100 mV @ 1 MHz) | 1.62 % | 1.30 % | 0.023 % | 0.076 % |
    | **iip3_dbv** (0.9/1.0 MHz, 50 mV/tone) | −1.5 | +5.9 | +23.6 | +17.9 |

    Cross-checks that pin the harness (not just the numbers): amp_022's Spectre `vn_in` (210 µV)
    equals the P5c record; `t_settle` agrees across engines (37 vs 38 ns); and an independent OCEAN
    `dB20@1kHz` pass over the same PSFs reproduces every rejection figure (−58.4/−96.6/−33.9/−28.1).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · Discover, then route
    Same surface as `analog_db_in_library.py` — the committed `sim_engine` marker routes each
    (circuit, pdk); the new benches just appear in `circuit_analyses`:
    """)
    return


@app.cell
def _():
    import os

    from spicexplorer.backends.analog_db import (
        circuit_analyses,
        effective_supply,
        probe_engine,
        run_circuit,
    )

    ADB = os.environ.get("SPICEXPLORER_ANALOG_DB")  # point at an analog-db checkout
    for circ in ("amp_001_5t", "amp_022_fer_two_stage"):
        print(f"{circ}: {circuit_analyses(circ, root=ADB)}")
    return ADB, circuit_analyses, effective_supply, probe_engine, run_circuit


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · The two operating-point truths (the 1.2 V-vs-1.5 V pin)
    A circuit's `analyses/*.yaml` params are its **authored operating point** — one set across all
    of its PDKs. The per-PDK registry `supply.default` is the **process rail**. They legitimately
    differ (amp_022 is authored at 1.5 V; generic-n65 runs 1.2 V): the **open lane executes the deck
    as committed**, the **closed lane always injects the rail**; `effective_supply` surfaces both.
    When a bench needs a *different* bias on one PDK, the binding's `sizing.yaml analysis_params`
    re-biases it per-PDK — that is how amp_001_5t's generic-n65 decks run VDD 1.2 / VCM 0.45 (the live
    tracking band at 1.2 V is [0.20, 0.67] V, so the cross-PDK VCM 0.8 would sit *outside* it and
    kill every AC bench — the linearity sweep itself diagnosed that).
    """)
    return


@app.cell
def _(ADB, effective_supply):
    for pdk in ("ihp-sg13g2", "generic-n65"):
        print(pdk, effective_supply("amp_022_fer_two_stage", pdk, root=ADB))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · Run EVERY bench type — and extract its metrics (open lane, live)
    One call shape for all eleven bench types: `run_circuit(circuit, pdk, testbench=tb)`, then
    `CircuitRun.evaluate()` measures exactly the datasheet metrics bound to THAT bench (matching
    is by analysis **id**, so `cmrr_vcm` never cross-scores `ac_open_loop`'s gain) and checks
    each against its own spec band. A bench with no datasheet metrics (`stb` — loop figures are
    closed-lane-only by design) returns `{}`; §3b shows how to extract *any* registered metric
    directly. A non-`tt` corner swaps the process section + temperature via the circuit's own
    `corners.yaml` — the deck's authored supply stays put:
    """)
    return


@app.cell
def _(ADB, circuit_analyses, run_circuit):
    import shutil
    import tempfile

    runs = {}
    if shutil.which("ngspice"):
        for _tb in circuit_analyses("amp_001_5t", root=ADB):  # all 11 bench types
            run = run_circuit(
                "amp_001_5t",
                "ihp-sg13g2",
                testbench=_tb,
                root=ADB,
                output_dir=tempfile.mkdtemp(),
                label=f"nb_{_tb}",
            )
            runs[_tb] = run
            evals = {
                k: f"{v.value:.4g}" + ("" if v.satisfied else " MISS")
                for k, v in run.evaluate().items()
            }
            print(f"{_tb:15s} -> {evals if evals else 'no datasheet metrics bind (see 3b)'}")
        for corner in ("ss", "tt", "ff"):
            run = run_circuit(
                "amp_001_5t",
                "ihp-sg13g2",
                testbench="cmrr_vcm",
                corner=corner,
                root=ADB,
                output_dir=tempfile.mkdtemp(),
                label=f"nb_{corner}",
            )
            print(f"corner {corner}: cmrr_db = {run.evaluate()['cmrr_db'].value:.4g}")
    else:
        print(
            "ngspice not on PATH — recorded (tt): gain 29.8/UGF 30M/PM 61; gain_cl ~1; cmrr 29.7"
            " MISS | psrr 29.7 | icmr 0.88 V | i_supply 27.5u | vn_in 1.71m | t_settle 24n |"
            " thd 1.62% | iip3 -1.5 dBV; corners ss/tt/ff = 30.8/29.7/28.3 dB"
        )
    return (runs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3b · The bench → extraction-recipe catalog
    What each bench's deck does, which datasheet metrics bind to it, the registry recipe that
    extracts them, and where the data lives per engine. Every recipe below also works *directly*
    (`spicexplorer_core.measurements.measure(run.result, recipe, default_analysis=kind)`) — the
    datasheet is just committed defaults:

    | bench | the deck | metrics · recipe | kind → Spectre PSF | engine notes |
    |---|---|---|---|---|
    | `ac_open_loop` | open-loop AC, `mag=1` on vinp | `dc_gain_db`/`ugf_hz`/`pm_deg` · `{meas: dcgain\|ugf\|pm, out: vout}` | `ac` → `ac.ac` | signal is `v(vout)` on ngspice, bare `vout` on Spectre — `evaluate()` translates |
    | `ac_closed_loop` | unity-buffer AC | `gain_cl`/`bw_cl_hz` · `{meas: gain_cl\|bw_cl}` | `ac` → `ac.ac` | `gain_cl` is **LINEAR V/V** (the CACE buffer-gain spec, e.g. 0.97..1.03); `bw_cl` = the −3 dB point |
    | `cmrr_vcm` | 1 V AC riding BOTH buffer inputs | `cmrr_db` · `{meas: cmrr_db}` = −dcgain of the residual | `ac` → `ac.ac` | the bench identity lives in the deck *stimulus*, not the analysis |
    | `psrr_vdd` | 1 V AC riding the supply | `psrr_vdd_db` · `{meas: psrr_vdd_db}` | `ac` → `ac.ac` | ditto |
    | `dc_op` | operating point | `i_supply` · `{meas: i_supply}` | `op` → `dcOp.dc` | probe differs — `i(i_supply)` (ngspice let-vector) vs `VDD:p` (Spectre); `evaluate()` fills it |
    | `noise` | small-signal noise, input source as iprobe | `vn_in` · `{meas: inoise_total, out: vout}` | `noise` → `noise.noise` | ngspice deck writes **integrated totals** (scalar read); Spectre writes densities (registry integrates) |
    | `tran_step` | small input step | `t_settle` · `{meas: t_settle}` (tolerance from the bench's `VTOL`; `slew` also registered) | `tran` → `tran.tran` | |
    | `linearity` | buffer DC sweep 0→rail | `icmr_min/max/range` · `{meas: icmr_*, vin: vinp, vtrack: 0.02}` | `dc` → `dc.dc` | widest CONTIGUOUS tracking band; the in-deck CROSS pair is a hint only |
    | `thd` | large-signal sine at F0 | `thd_pct` · `{meas: thd_pct, f0}` | `tran` (ng) / `pss` → `pss.fd.pss` (Spectre) | engine-split: ngspice = tran + coherent FFT; Spectre = native PSS, recipes auto-swap to `thd_pss_*` |
    | `iip3` | two tones on a common fundamental | `iip3_dbv`/`im3_dbc` · `{meas: iip3_dbv, f1, f2, ampl_in}` | `tran` (ng) / `pss` (Spectre) | auto-swap to `iip3_pss_*` with harmonic indices n₁/n₂ derived from f1/f2 |
    | `stb` | unity buffer with the `VIPRB` loop probe | *(none in the datasheet — on purpose)* | `stb` → `stb.stb` | closed lane: `{meas: pm_loop\|gain_margin_db\|loopgain_db, out: loopGain}` or the §4c calculator set; on ngspice the deck is a closed-loop AC eyeball only |

    And nothing limits you to the datasheet set — any registered measurement extracts off any
    compatible run:
    """)
    return


@app.cell
def _(runs):
    from spicexplorer_core.measurements import known_measurements, measure

    if runs:
        ac, tr = runs["ac_open_loop"].result, runs["tran_step"].result
        for label, res, recipe, kind, unit in [
            ("bw_3db", ac, {"meas": "bw_3db", "out": "v(vout)"}, "ac", "Hz"),
            ("gbw", ac, {"meas": "gbw", "out": "v(vout)"}, "ac", "Hz"),
            ("slew", tr, {"meas": "slew", "out": "v(vout)"}, "tran", "V/s"),
        ]:
            print(
                f"{label:7s} = {measure(res, recipe, default_analysis=kind):.4g} {unit}"
                "   (not in the datasheet — extracted directly)"
            )
    else:
        print("recorded: bw_3db ~0.9 MHz, gbw ~28 MHz, slew ~5 V/us")
    print(f"\n{len(known_measurements())} registered measurements:")
    print(", ".join(known_measurements()))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · Closed lane — same call, native Spectre
    With a bridge env (`SPICEXPLORER_VB_ENV_FILE`) + the operator's neutral corner wrapper
    (`SPICEXPLORER_SPECTRE_MODEL_ROOT`), the *same* `run_circuit` call runs the generic-n65 binding
    natively: the raw deck's stimulus translates (AC magnitudes ride the right sources; the
    tran-step `pulse(...)` maps to `type=pulse`), the analyses compose from the same YAML params
    (`cmrr_vcm`/`psrr_vdd` are one AC sweep — the bench identity lives in the stimulus; `linearity`
    is a rail-bounded `dc` sweep read from the `dc.dc` PSF), and the generic corner resolves
    against the out-of-repo wrapper. Without that env it degrades honestly:
    """)
    return


@app.cell
def _(ADB, probe_engine):
    cap = probe_engine("amp_001_5t", "generic-n65", root=ADB)
    print(f"engine={cap.engine} available={cap.available}")
    print("reason:", cap.reason)
    # with the env set, the full 7-bench matrix ran live on BOTH circuits — see the TL;DR table;
    # each bench is ~1 s/run through the local bridge.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4b · THD & IIP3 — one bench, two native routes
    ngspice has **no PSS**, so the `thd`/`iip3` benches are engine-split by the router: the open
    lane runs the deck's **tran** and the registry computes the figures by coherent FFT
    (`{meas: thd_pct, f0}` / `{meas: iip3_dbv, f1, f2, ampl_in}` — exact bins, no window); the
    closed lane swaps in a **native Spectre `pss`** and `evaluate()` re-routes the recipes to
    their harmonic-phasor twins (`thd_pss_*`, `iip3_pss_*`). The IIP3 trick: both tones share a
    common fundamental (0.9/1.0 MHz → 100 kHz, n₁ = 9, n₂ = 10), so ONE single-fundamental pss
    resolves the tones AND the IM3 products (2f₁−f₂, 2f₂−f₁) as plain harmonics of the fd-PSF.
    Internal coherence of the live matrix: within each circuit, the lane with lower THD also
    shows the higher IIP3. amp_022's Spectre THD (0.076 %) reproduces the P5d record exactly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4c · Spectre analysis configs + SKILL calculator expressions are DATA
    The closed lane composes its analyses from an **engine template database** committed in
    analog-db — the ADE analogue of "analysis configs + calculator expressions":

    | file | holds |
    |---|---|
    | `_shared/engines/spectre/analyses.yaml` | analysis **statement templates** (`ac`, `dc_op`, `dc_sweep`, `noise`, `tran`, `pss`, `stb`) with `{NAME}` placeholders + `[ optional ]` segments |
    | `_shared/engines/spectre/calculator.yaml` | named **SKILL calculator expressions** (one OCEAN `result` + one SKILL line each) |
    | `_shared/classes/amplifier/spectre-benches.yaml` | per-**testbench** wiring: which templates compose, which calculator rows read the results |

    `_spectre_analyses` renders from the DB when present (built-in composition is the fallback and
    parity reference); `bench_ocean_measurements(circuit, tb)` renders the bench's calculator set
    for `OceanMetricsSession` — the **PSS+SKILL route** for THD/IIP3 and the **STB route** for loop
    margins. The new `stb` bench marks its loop probe with a 0 V source `VIPRB` that the emitter
    translates to a Spectre `iprobe` (`stb … probe=VIPRB`); ngspice (no stb analysis) runs that
    deck as a plain closed-loop AC.

    Live parity (amp_022 generic-n65 tt, 2026-07-10) — Python fd-PSF registry vs OCEAN calculator on
    the SAME raw dirs:

    | figure | Python registry | OCEAN/SKILL | cross-check |
    |---|---|---|---|
    | thd_pct (100 mV @ 1 MHz) | 0.07632 % | 0.07632 % | == P5d record |
    | hd2_db / hd3_db | — | −62.4 / −81.8 dBc | == P5d records |
    | iip3_dbv (0.9/1.0 MHz) | +17.93 | +17.93 (im3 −87.9 dBc) | == bench record |
    | cmrr_db | 58.39 | 58.39 | == bench record |
    | stb pm_loop | 61.6° | 60.8° (Spectre's native margin) | open-loop pm 60.9° |
    | stb gain margin | 8.055 dB | 8.055 dB | registry == Spectre native |
    | stb loop gain @DC | 47.41 dB | 47.41 dB | == open-loop dcgain (β = 1) |

    amp_001_5t stb: pm_loop 88.9° (≈ single-pole), gain margin honestly `NaN` on BOTH routes (a 5T
    OTA's loop phase never reaches −180° in-band). Footgun pinned: `phaseMargin(loopGain)` at the
    wave level reads 180° low — Spectre's `loopGain` carries the −T sign convention (phase starts
    at ±180°), so the calculator reads Spectre's **native** `stb_margin` result instead.
    """)
    return


@app.cell
def _(ADB):
    from spicexplorer.backends.analog_db import (
        _spectre_context,
        bench_ocean_measurements,
        load_analysis,
    )
    from spicexplorer.backends.spectre_templates import bench_analyses

    for _tb in ("thd", "iip3", "stb"):
        params = load_analysis("amp_022_fer_two_stage", _tb, root=ADB).get("params", {})
        ctx = _spectre_context(_tb, params, supply=1.2)
        print(f"-- {_tb}")
        for s in bench_analyses(_tb, ctx, root=ADB):
            print("   analysis :", s)
        for m in bench_ocean_measurements(
            "amp_022_fer_two_stage", _tb, pdk="generic-n65", root=ADB
        ):
            print(f"   calc {m.name:11s} [{m.result}]: {m.expr}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 · What the linearity bench measures (and why the registry owns it)
    `linearity` sweeps the unity-buffer input 0→VDD and the **ICMR** is the widest *contiguous*
    band where the follower tracks within `VTRACK` (20 mV). The in-deck ngspice `CROSS` meas pair
    is only a hint — it misreads a DUT that already tracks at vin = 0 (amp_022 ihp: 0.105 V vs the
    true 1.37 V) — so the registry recipe `{meas: icmr_range, vin: vinp, vtrack: 0.02}` computes the
    contiguous band from the written sweep on either engine:
    """)
    return


@app.cell
def _():
    import numpy as np
    from spicexplorer_core.measurements import icmr_band

    vin = np.linspace(0, 1.2, 241)
    verr = np.where(
        (vin > 0.195) & (vin < 0.665), 0.004, 0.08
    )  # the live amp_001 generic-n65 shape
    lo, hi = icmr_band(vin, vin + verr, vtrack=0.02)
    print(f"tracking band [{lo:.3f}, {hi:.3f}] V  →  icmr_range = {hi - lo:.3f} V")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6 · Cheatsheet
    ```python
    # any bench, any bound PDK — the router picks the native engine off the committed marker
    run = run_circuit(circuit, pdk, testbench='cmrr_vcm', corner='tt', root=ADB,
                      output_dir=...,                       # open lane
                      deck_dir=..., work_dir=...)           # closed lane (+ bridge env vars)
    run.evaluate()      # {metric: MetricEval(value, satisfied, spec bounds)} for THIS bench
    effective_supply(circuit, pdk, testbench)  # the supply pin: deck VDD vs PDK rail per lane
    ```
    Env: `SPICEXPLORER_ANALOG_DB` (checkout), and for the closed lane
    `SPICEXPLORER_VB_ENV_FILE` + `SPICEXPLORER_SPECTRE_MODEL_ROOT`.
    THD/IIP3 recipes carry their stimulus facts (`f0` / `f1,f2,ampl_in`) in the datasheet extract.
    Data side (analog-db): a bench = `analyses/<tb>.yaml` (+ entry in `circuit.yaml` `analyses:`)
    + datasheet metric with `analysis: <tb>`; per-PDK re-bias via `sizing.yaml analysis_params`;
    re-render with `analog-db export-raw --circuit <id>`.
    Spectre engine config is data too (§4c): a new analysis type = a row in
    `_shared/engines/spectre/analyses.yaml`; a new SKILL metric = a row in `calculator.yaml`;
    wiring = the class `spectre-benches.yaml`. Loop margins: `{meas: pm_loop|gain_margin_db|
    loopgain_db, out: loopGain}` on an `stb` run, or `bench_ocean_measurements(circ, 'stb')`.
    """)
    return


if __name__ == "__main__":
    app.run()
