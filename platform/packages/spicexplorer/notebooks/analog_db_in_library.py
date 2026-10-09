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
    # In-library analog-db import — one router over open (ngspice) + closed (Spectre)

    The platform reads an **analog-db** circuit's committed binding YAMLs *in-process* and runs it
    through its **native** engine, chosen by a committed `sim_engine` marker in
    `_shared/pdk/<pdk>.yaml`:

    * open PDKs (`ihp-sg13g2` / `sky130` / `gf180mcu`) → **ngspice** (the self-contained raw deck),
    * the closed PDK (`generic-n65`) → **native Spectre** via the virtuoso-bridge.

    Both paths go through the **same** `run_circuit` router and yield an engine-neutral `SimResult`,
    so the **same** measurement registry scores the datasheet metrics off either — the only
    differences are one `sim_engine` marker and the output signal name (`v(vout)` for ngspice vs
    `vout` for Spectre). `probe_engine` reports which engine a `(circuit, pdk)` routes to and whether
    it can run *here*, so the closed lane **degrades honestly** (like `/api/library`) when the
    operator's licensed kit + bridge aren't present.

    > **NDA posture** — only *generic* corner labels (`tt`/`ss`/`ff`) and a *neutral* wrapper
    > filename ever appear in git; the `tt→tt_lvt` kit-section indirection lives in the operator's
    > out-of-repo `model_lib_root` wrapper. This notebook never touches kit bytes.
    """)
    return


@app.cell
def _():
    from spicexplorer.backends.analog_db import (
        analog_db_root,
        circuit_analyses,
        circuit_pdks,
        list_circuits,
        pdk_sim_engine,
        probe_engine,
        run_circuit,
    )

    CIRCUIT = (
        "amp_022_fer_two_stage"  # a ferrosim two-stage OTA bound for 3 open PDKs + generic-n65
    )
    print("analog-db root:", analog_db_root())
    return (
        CIRCUIT,
        circuit_analyses,
        circuit_pdks,
        list_circuits,
        pdk_sim_engine,
        probe_engine,
        run_circuit,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · Discover what's in the library
    The reader walks the committed `circuits/` tree — no analog-db package import, just data.
    """)
    return


@app.cell
def _(CIRCUIT, circuit_analyses, circuit_pdks, list_circuits, pdk_sim_engine):
    print("circuits in library :", len(list_circuits()))
    print("amp_022 PDKs        :", circuit_pdks(CIRCUIT))
    print("amp_022 analyses    :", circuit_analyses(CIRCUIT))
    print("per-PDK sim_engine  :", {p: pdk_sim_engine(p) for p in circuit_pdks(CIRCUIT)})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · Route — the capability probe
    `probe_engine` reads the `sim_engine` marker, then checks the environment for that engine.
    Open PDKs are runnable wherever ngspice + the PDK are on the sourcepath; the closed lane needs
    the bridge **and** the operator's neutral corner wrapper — otherwise it reports a clear reason.
    """)
    return


@app.cell
def _(CIRCUIT, circuit_pdks, probe_engine):
    for pdk in circuit_pdks(CIRCUIT):
        _cap = probe_engine(CIRCUIT, pdk)
        flag = "RUNNABLE" if _cap.available else "unavailable"
        print(f"{pdk:12s} -> {_cap.engine:8s} [{flag}]  {_cap.reason}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · Run the OPEN lane (ngspice) — live
    `run_circuit` routes `ihp-sg13g2` to ngspice, runs the circuit's self-contained raw deck, and
    `CircuitRun.evaluate()` scores each datasheet metric off the result against its **own** spec band.
    """)
    return


@app.cell
def _(CIRCUIT, run_circuit):
    def show(run):
        print(f"engine={run.engine}  pdk={run.pdk}  testbench={run.testbench}  corner={run.corner}")
        print(f"{'metric':12s} {'value':>12s}   {'spec band':>18s}   pass")
        for name, m in run.evaluate(only={"dc_gain_db", "ugf_hz", "pm_deg"}).items():
            band = f"[{m.spec_min}, {m.spec_max}]"
            print(f"{name:12s} {m.value:12.4g}   {band:>18s}   {'OK' if m.satisfied else 'FAIL'}")

    open_run = run_circuit(CIRCUIT, "ihp-sg13g2", testbench="ac_open_loop")
    show(open_run)
    return (show,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · The CLOSED lane (Spectre) — the *same* call, gated by the operator kit
    Exactly the same `run_circuit` call for `generic-n65`. Where the operator's licensed kit +
    virtuoso-bridge are configured (a research EDA host with `SPICEXPLORER_SPECTRE_MODEL_ROOT` +
    `SPICEXPLORER_VB_ENV_FILE`), this runs native Spectre and reproduces the P5b AC numbers
    **55.3 dB / 11.5 MHz / 78°** — the 2026-07-22 gm/ID re-sizing (campaign `hand_design` tag `gmid_v7`) — (verified by `tests/test_amp022_spectre_configdriven_live.py`).
    Everywhere else it degrades honestly — the probe says why, and the open lane above still runs.
    """)
    return


@app.cell
def _(CIRCUIT, probe_engine, run_circuit, show):
    _cap = probe_engine(CIRCUIT, "generic-n65")
    if _cap.available:
        import tempfile

        closed_run = run_circuit(
            CIRCUIT,
            "generic-n65",
            testbench="ac_open_loop",
            corner="tt",
            deck_dir=tempfile.mkdtemp(),
            work_dir=tempfile.mkdtemp(),
        )
        show(closed_run)
    else:
        print(f"closed lane routes to {_cap.engine!r} but is unavailable here:")
        print(f"  reason: {_cap.reason}")
        print(
            "  -> provide the operator wrapper (SPICEXPLORER_SPECTRE_MODEL_ROOT) + bridge env to run it."
        )
        print(
            "  verified live elsewhere: 55.3 dB / 11.5 MHz / 78 deg (gmid_v7 re-sizing, tt corner, 1.2 V)."
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways
    * **One source of truth** — each circuit's committed per-PDK bindings.
    * **One router** — `run_circuit` picks the engine off the `sim_engine` marker; open runs ngspice,
      closed runs native Spectre. Same `CircuitRun.evaluate()`, same registry, engine-neutral.
    * **Honest degradation** — `probe_engine` surfaces exactly why a lane can't run (missing PDK,
      missing kit wrapper, or missing bridge); the open lane is unaffected.
    * **NDA-safe** — generic corner labels + a neutral wrapper filename only; the kit indirection is
      the operator's out-of-repo artifact.

    **Go deeper:** [`analog_db_bench_validation.py`](analog_db_bench_validation.py) runs the
    FULL bench suite (CMRR/PSRR/linearity/THD/IIP3/STB) on both lanes and shows the Spectre
    template DB + SKILL calculator route (§4c); [`optimizer_quickstart.py`](optimizer_quickstart.py)
    is the *optimizer-driven* lane — sizing a circuit by driving the committed `raw/` decks
    (`raw_optimize/`), plus the engine seam and measurement recipes.
    """)
    return


if __name__ == "__main__":
    app.run()
