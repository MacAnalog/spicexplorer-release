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
    # analog-db tour — the circuit database as a library

    The [`spicexplorer-analog-db`](https://github.com/MacAnalog/spicexplorer-analog-db) is a canonical,
    tool-agnostic database of analog circuits: one **PDK-neutral abstract topology** per circuit, lowered
    to **three PDKs** (ihp-sg13g2, sky130, gf180mcu) via circuitgraph, with class-scoped analyses, a
    machine-readable datasheet, sizing knobs, recorded baselines, and a tiered verify harness. The CLI
    (`analog-db …`, see the repo README) wraps the same library this notebook drives directly.
    """)
    return


@app.cell
def _():
    import json
    import pandas as pd

    from spicexplorer_analog_db import assemble, catalog, model, paths

    cat = catalog.build_catalog()
    df = pd.DataFrame([{
        "id": c["id"], "class": c.get("class", ""), "status": c.get("status", ""),
        "pdks": ", ".join(c.get("pdks", [])), "analyses": len(c.get("analyses", [])),
    } for c in cat["circuits"]]).set_index("id")
    print(f"{len(df)} circuits | classes: {sorted(df['class'].unique())}")
    df
    return assemble, cat, json, model, paths, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One circuit, fully loaded

    `load_circuit` gives the manifest + typed accessors for the datasheet, per-PDK sizing, and the
    analysis definitions. The 5T OTA is the proof-of-schema circuit (fullest cross-repo coverage).
    """)
    return


@app.cell
def _(model, pd):
    ckt = model.load_circuit("amp_001_5t")
    print("class:", ckt.klass, "| status:", ckt.status, "| pdks:", ckt.pdks, "| analyses:", ckt.analyses)

    specs = ckt.datasheet().get("specs", {})
    pd.DataFrame(specs).T
    return (ckt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## AUTHORED vs GENERATED — the abstract topology and its lowerings

    The hand-written source of truth is the PDK-neutral `abstract/netlist.spice` (generic `nmos`/`pmos`
    subckt devices). circuitgraph lowers it to each bound PDK (`analog-db generate`); the committed
    lowered netlists are drift-guarded by the verify harness (Tier 1).
    """)
    return


@app.cell
def _(ckt):
    abstract = (ckt.dir / "abstract" / "netlist.spice").read_text()
    print("── abstract (PDK-neutral) ──")
    print("\n".join(abstract.splitlines()[:14]), "\n…")
    for pdk in ckt.pdks[:2]:
        lowered = (ckt.dir / "pdk" / pdk / "netlist.spice").read_text()
        body = [l for l in lowered.splitlines() if l.lower().startswith("xm")][:3]
        print(f"\n── lowered → {pdk} (device lines) ──")
        print("\n".join(body))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sizing knobs + PDK registry

    Each binding carries its sizing variables (defaults + bounds, in the PDK's native geometry
    notation); the PDK registry holds the corner-lib catalog, geometry rules, gm/ID characterization
    defaults, and measured passive constants.
    """)
    return


@app.cell
def _(ckt, pd):
    sizing = ckt.sizing("ihp-sg13g2")
    pd.DataFrame(sizing["variables"]).set_index("name").head(8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Assemble a runnable testbench

    `assemble` resolves a class testbench template + the circuit's conditions + corner libs + sizing
    defaults + the DUT subckt into one runnable ngspice deck — **PDK-free** (no simulator needed to
    build it; this is verify Tier 2 across every circuit × analysis × pdk × corner).
    """)
    return


@app.cell
def _(assemble, ckt):
    assembled_deck = assemble.assemble(ckt, "ac_open_loop", "ihp-sg13g2", "tt")
    lines = assembled_deck.splitlines()
    print("\n".join(lines[:18]))
    print(f"… ({len(lines)} lines total)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pull a ready-to-run deck from `raw/`

    `assemble` builds that deck in memory; **`analog-db export-raw` persists it** to `raw/<class>/<circuit>/<pdk>/<testbench>.spice` — one self-contained file (testbench + bound params + the lowered DUT subckt) you can pull and simulate directly. `catalog.json` indexes every deck under each circuit's `raw` block (and `export.deck_path(...)` gives the path programmatically); each deck's header carries the exact `docker run` command. A standalone `_dut.spice` holds just the lowered DUT subckt for your own testbench.
    """)
    return


@app.cell
def _(cat, paths):
    # every committed deck is indexed in catalog.json under its circuit's `raw` block:
    #   {pdk: {testbench: path}}
    raw_index = next(c for c in cat["circuits"] if c["id"] == "amp_001_5t")["raw"]
    print("amp_001_5t sky130 decks:", ", ".join(raw_index["sky130"]))

    # pull one self-contained, ready-to-run deck and show its self-documenting header
    raw_deck = paths.db_root() / raw_index["sky130"]["ac_open_loop"]
    print(f"\n\u2500\u2500 {raw_deck.relative_to(paths.db_root())} \u2500\u2500")
    print("\n".join(raw_deck.read_text().splitlines()[:9]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The scoreboard — recorded design points + PPA

    Every `analog-db run --write` records a **design point** on the circuit's scoreboard
    (`scoreboard/<pdk>/<design_id>.json`): the sizing vector actually simulated (content-hashed, so a
    re-run at a new corner upserts the same entry), the per-corner metrics with datasheet-spec
    verdicts, and the **PPA rollup** — worst-corner power, the class's directed headline metrics, and
    `active_gate_area_um2` = Σ(w·l·m). These are the floors the optimizer must beat.
    """)
    return


@app.cell
def _(ckt, pd):
    from spicexplorer_analog_db import scoreboard

    baseline_ids = scoreboard.baselines(ckt)
    rows = {}
    for e in scoreboard.load_entries(ckt):
        tag = f"{e['pdk']} · {e['design_id']}" + (" ★" if baseline_ids.get(e["pdk"]) == e["design_id"] else "")
        rows[tag] = {"corners": ",".join(e["ppa"]["corners_run"]),
                     "power_w": e["ppa"].get("power_w"),
                     "area_um2": e["ppa"]["active_gate_area_um2"],
                     **e["ppa"]["performance"]}
    pd.DataFrame(rows).T  # ★ = the named baseline (scoreboard/baselines.yaml)
    return (scoreboard,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### No scalar "best" — the Pareto front

    Sizing is a tradeoff surface, so the generated `scoreboard.json` never ranks; it marks the
    **non-dominated set** per (circuit, pdk) over power ↓, active area ↓ and the class's directed
    metrics. The telescopic cascode already shows a real two-point front on ihp-sg13g2: the committed
    defaults vs the NEWCAS-2026 optimizer best — each wins different axes.
    """)
    return


@app.cell
def _(json, paths, pd):
    sb = json.loads((paths.db_root() / "scoreboard.json").read_text())
    tele = sb["classes"]["amplifier"]["ihp-sg13g2"]["amp_018_telescopic_cascode"]
    pd.DataFrame([{
        "design_id": r["design_id"], "baseline": r["baseline"], "pareto": r["pareto"],
        "power_w": r["ppa"].get("power_w"), "area_um2": r["ppa"]["active_gate_area_um2"],
        "spec_pass": r["spec"]["pass"], "spec_fail": r["spec"]["fail"],
        **r["ppa"]["performance"],
    } for r in tele["entries"]]).set_index("design_id")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Run it live (PDK-gated)

    With ngspice + the ihp-sg13g2 PDK on this host (`runner.native_pdk_runner`), or with the EDA base image present, run one matrix cell and compare against the committed baseline —
    the same path as `analog-db run --circuit amp_001_5t --pdk ihp-sg13g2` (add `--docker-image` for the image).
    """)
    return


@app.cell
def _():
    # PDK-gated cells: real simulation needs ngspice + the ihp-sg13g2 PDK, either on this host
    # (ngspice on PATH, the PDK's models under $PDK_ROOT; tried first) or in the EDA base image
    # (ngspice + the three PDKs).
    # Build it once in spicexplorer-platform:  docker compose --profile base build spice-base
    # (probe with a real `docker run` — `docker image inspect` can false-negative under the
    #  containerd image store)
    import shutil
    import subprocess

    def base_image_available(image: str = "spicexplorer-spice-base:local") -> bool:
        if shutil.which("docker") is None:
            return False
        return subprocess.run(["docker", "run", "--rm", image, "true"],
                              capture_output=True, timeout=120).returncode == 0

    from spicexplorer_analog_db.runner import native_pdk_available

    NATIVE_OK = native_pdk_available("ihp-sg13g2")  # ngspice on PATH + the PDK under $PDK_ROOT
    PDK_OK = NATIVE_OK or base_image_available()  # the image is probed only when the host lacks either
    LANE = "this host (native ngspice)" if NATIVE_OK else "the EDA base image" if PDK_OK else "none"
    print("simulation lane:", LANE, "" if PDK_OK else "→ the simulation cells below will skip (everything else runs PDK-free)")
    return NATIVE_OK, PDK_OK


@app.cell
def _(NATIVE_OK, PDK_OK, ckt, json, mo, pd, scoreboard):
    if not PDK_OK:
        print("SKIPPED — needs ngspice + the PDK on this host, or the EDA base image, to simulate (everything above ran PDK-free).")
    else:
        from spicexplorer_analog_db import runner
        live = runner.run_cell(ckt, "ac_open_loop", "ihp-sg13g2", "tt",
                               runner.native_pdk_runner("ihp-sg13g2") if NATIVE_OK else runner.base_image_runner())
        did = scoreboard.baselines(ckt)["ihp-sg13g2"]
        entry = json.loads(scoreboard.entry_path(ckt, "ihp-sg13g2", did).read_text())
        baseline_measures = entry["corners"]["tt"]["analyses"]["ac_open_loop"]["measures"]
        cmp = pd.DataFrame({"committed baseline": baseline_measures, "this run": live})
        mo.output.append(cmp.map("{:.4g}".format))
        assert abs(live["dcgain"] - baseline_measures["dcgain"]) < 0.5, "DC gain (dB) drifted vs baseline"
        print("live run matches the committed baseline.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The harness + CLI cheatsheet

    ```bash
    analog-db verify                  # tiered checks: T0 schema · T1 generation-drift · T2 assembly (PDK-free)
    analog-db generate [--all]        # rewrite GENERATED artifacts (--all: + raw/ + catalog.json + scoreboard.json)
    analog-db export-raw [--check]    # materialize ready-to-run raw/ decks (--check: drift guard, no writes)
    analog-db catalog --write         # rebuild catalog.json (incl. the raw/schematic index)
    analog-db run --circuit ID --pdk PDK --docker-image --write   # simulate + record a scoreboard design point (PDK-gated)
    analog-db scoreboard [--write] | set-baseline ...             # global PPA index (Pareto-marked) / name a baseline
    analog-db new-circuit --class CLS --slug SLUG --ports ...     # allocate the next accession id + scaffold
    analog-db add-binding --circuit ID --pdk PDK                  # synthesize another PDK binding
    analog-db gmid-extract --pdk PDK                              # gm/ID LUT characterization (PDK-gated)
    analog-db import-analoggym --src <AnalogGym/Amplifier>        # corpus (re-)import
    ```

    Deeper docs: repo `README.md` + `TESTING.md`, `_shared/PDK_SIM.md`, `_shared/SCOREBOARD.md` (tri-PDK sims + cross-PDK
    matrix), `_shared/GMID.md` (LUTs). The gm/ID companions: `gmid_tables_tour.py`,
    `gmid_sizing_demo.py`.
    """)
    return


if __name__ == "__main__":
    app.run()
