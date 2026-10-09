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
    # netlist2xschem — quickstart

    Turn a SPICE netlist into an **xschem schematic** (`.sch`), then (optionally) render it to **SVG/PNG**.

    Pipeline: `ingest → map → place → wire → emit`. Devices are placed on a grid and wired by net-name
    label (`lab_wire.sym`) — correct and round-trips through xschem, no auto-router. The generated `.sch`
    opens directly in the SpiceXplorer UI's Schematic viewer; image export is additive (and degrades
    gracefully when xschem isn't installed).
    """)
    return


@app.cell
def _():
    from spicexplorer_core import project_root
    from spicexplorer_netlist2xschem import build_sch, from_file

    # A committed flat IHP netlist (telescopic cascode OTA).
    netlist = project_root() / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
    circuit = from_file(netlist, name="ota-improved")
    doc = build_sch(circuit, pdk="ihp-sg13g2", title="ota-improved")
    print(f"{doc.device_count} devices, {doc.label_count} net-labels, {len(doc.warnings)} warnings")
    doc.warnings
    return circuit, doc


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The model is just enough to place + wire: each device carries its pin→net map.
    """)
    return


@app.cell
def _(circuit):
    for d in circuit.devices[:6]:
        print(f"{d.ref:8s} {d.kind.value:7s} {d.polarity.value:7s} {dict(d.nets)}")
    print("...\nnets:", circuit.nets)
    return


@app.cell
def _(doc, mo):
    # The .sch text — paste/upload this into the UI's Schematic viewer, or write it to disk.
    out = mo.notebook_dir() / "ota-improved.sch"
    out.write_text(doc.text)
    print("\n".join(doc.text.splitlines()[:12]))
    return (out,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Render to an image

    `render()` needs `xschem` on `PATH` (the EDA Docker image; not the macOS host). PNG additionally needs
    the `[render]` extra (`cairosvg`). When xschem is absent it returns `available=False` with no image —
    the `.sch` is still valid for the UI viewer.
    """)
    return


@app.cell
def _(out):
    from spicexplorer_netlist2xschem import render, xschem_available

    if xschem_available():
        result = render(out, fmt="svg")
        print("rendered:", result.image_path)
        from IPython.display import SVG, display

        if result.image_path:
            display(SVG(filename=str(result.image_path)))
    else:
        print("xschem not on PATH — skipping image render.")
        print("The .sch above is still valid; open it in the SpiceXplorer UI's Schematic viewer,")
        print("or run this notebook inside the EDA container (docker compose exec api ...).")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CLI

    ```bash
    netlist2xschem ota-improved.spice -o ota.sch --render svg
    netlist2xschem ota-5t_tb.spice --into xota -o ota5t.sch --render png --out-image ota5t.png
    ```

    Or over REST: `POST /api/xschem/from-netlist` (the UI's **“From netlist”** button in the Schematic tab).
    """)
    return


if __name__ == "__main__":
    app.run()
