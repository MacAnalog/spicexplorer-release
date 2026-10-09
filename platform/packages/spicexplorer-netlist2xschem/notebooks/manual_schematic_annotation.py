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
    # netlist2xschem — annotate a hand-drawn schematic

    The [annotation overlay](annotation_demo.py) normally runs *inside* generation: place a netlist,
    then box the recognised functional blocks. But often you already **have** a schematic — drawn by hand
    in xschem — and just want to *see* the blocks outlined on it, without regenerating (and so disturbing)
    your layout. That is what `annotate_sch` (CLI `--annotate-existing`) does:

    * **Nothing moves.** The existing `.sch` is parsed only for each device's placed coordinate; the output
      is the input **byte-for-byte** plus appended `B` (box) / `T` (label) graphic records.
    * **Same neutral contract.** The blocks come in as `spicexplorer/xschem-block-annotations@1` JSON —
      hand-authored, or produced by `circuitgraph`'s deterministic detector. The join key is the **device
      instance name**, tolerant of the `XM3`↔`M3` spiceprefix split (a netlist says `XM3`, xschem draws
      `name=M3`).
    * **Lenient.** A block whose devices aren't found in the drawing is skipped with a warning, never an
      error.

    This walkthrough runs on a genuinely hand-drawn schematic: the IHP-sg13g2 **5T OTA** by H. Pretl
    (13 transistors incl. an enable/power-down cell) committed under `examples/OTA/5t-ota/`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Load the hand-drawn `.sch`

    `parse_sch` reads the drawing back: every placed device with its coordinate — the geometry the boxes will be fitted to.
    """)
    return


@app.cell
def _():
    from spicexplorer_core import project_root
    from spicexplorer_netlist2xschem import annotate_sch, parse_sch

    sch_path = project_root() / "examples/OTA/5t-ota/ihp-sg13g2/xschem/ota-5t.sch"
    sch_text = sch_path.read_text()

    sch = parse_sch(sch_text)
    print(f"{len(sch.devices)} drawn devices:")
    for d in sch.devices:
        print(f"  {d.name:5s} at ({d.x:6.0f},{d.y:6.0f})  {d.symref}")
    return annotate_sch, project_root, sch_text


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Hand-author the blocks

    You know your own circuit — the quickest overlay is a minimal JSON naming the devices of each block.
    Note we deliberately write the refs netlist-style (`XM1`) while the drawing says `name=M1`: the
    `X`-prefix normalisation joins them.
    """)
    return


@app.cell
def _():
    from spicexplorer_netlist2xschem import BlockAnnotation, BlockAnnotationSet

    manual = BlockAnnotationSet(
        (
            BlockAnnotation(
                block_id="dp.nmos#input",
                devices=("XM1", "XM2"),  # drawn as M1 / M2 — the X is normalised away
                label="input pair (hand-tagged)",
                family="differential_pair",
            ),
            BlockAnnotation(
                block_id="cm.pmos#load",
                devices=("XM3", "XM4"),
                label="PMOS load mirror (hand-tagged)",
                family="current_mirror",
            ),
        )
    )
    print(manual.to_json())
    return BlockAnnotationSet, manual


@app.cell
def _(annotate_sch, manual, sch_text):
    annotated_manual, warnings_manual = annotate_sch(sch_text, manual)

    # The output is the input byte-for-byte, plus appended B/T records only:
    base = sch_text.rstrip("\n") + "\n"
    assert annotated_manual.startswith(base), "devices moved — should never happen"
    tail = annotated_manual[len(base) :].splitlines()
    assert all(ln.startswith(("B ", "T ")) for ln in tail if ln.strip())

    print(f"warnings: {list(warnings_manual)}")
    print("appended overlay records:")
    for ln in tail:
        print(" ", ln)
    return (base,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Or detect the blocks — the real producer

    For anything bigger than a couple of blocks, let `circuitgraph` find them. The detector reads a
    **netlist**, so we take the schematic's own SPICE — here the OTA's subcircuit body as netlisted into
    the sibling testbench (`spice/ota-5t_tb-ac.spice`) — and export the same neutral contract.
    """)
    return


@app.cell
def _(project_root):
    import re

    from spicexplorer_circuitgraph import (
        CircuitGraph,
        export_subcircuit_annotations,
        find_subcircuits,
        group_matches,
    )
    from spicexplorer_core.spice_engine import NetlistView

    tb = (project_root() / "examples/OTA/5t-ota/ihp-sg13g2/spice/ota-5t_tb-ac.spice").read_text()
    body = re.search(r"^\.subckt ota-5t .*?\n(.*?)^\.ends", tb, re.S | re.M).group(1)  # pyright: ignore[reportOptionalMemberAccess] -- the committed testbench defines .subckt ota-5t
    netlist = (
        "* ota-5t DUT body\n"
        + "\n".join(ln for ln in body.splitlines() if ln.startswith("XM"))
        + "\n.end\n"
    )

    graph = CircuitGraph.from_netlist(NetlistView.from_string(netlist), name="ota_5t")
    contract = export_subcircuit_annotations(group_matches(find_subcircuits(graph)))
    for b in contract["blocks"]:
        print(f"{b['block_id']:22s} {b['family']:17s} {b['devices']}")
    return (contract,)


@app.cell
def _(BlockAnnotationSet, annotate_sch, base, contract, sch_text):
    detected = BlockAnnotationSet.from_dict(contract)
    annotated, warnings_detected = annotate_sch(sch_text, detected)

    n_boxes = sum(1 for ln in annotated[len(base) :].splitlines() if ln.startswith("B "))
    print(
        f"{len(detected)} detected blocks -> {n_boxes} boxes drawn, {len(warnings_detected)} warnings"
    )
    for w in warnings_detected:
        print("WARN:", w)
    return (annotated,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Every detected block got a box: the PMOS load mirror, the NMOS input pair, and the **two enable
    inverters** of the power-down cell. One honest miss worth knowing about: the NMOS **tail mirror**
    (`M5`/`M6`) is *not* detected — the enable devices (`M9` pulling the mirror gate down, `M10` in series
    with the diode ref) sit inside the mirror's gate net, so the deterministic template no longer matches.
    Hand-drawn production circuits often carry such power-down circuitry; when the detector misses a block
    you care about, just add it to the JSON by hand (§2) — the two sources compose in one
    `BlockAnnotationSet`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Render it (needs xschem)

    Write the annotated `.sch` somewhere scratch and render before/after with headless xschem. When xschem
    (or the PDK's symbol library) is absent this degrades gracefully — the `.sch` is still valid and opens
    in xschem or the Studio viewer.
    """)
    return


@app.cell
def _(annotated):
    import tempfile
    from pathlib import Path

    from spicexplorer_netlist2xschem import render, xschem_available

    outdir = Path(tempfile.mkdtemp(prefix="ota5t_annotated_"))
    out_sch = outdir / "ota-5t.annotated.sch"
    out_sch.write_text(annotated)
    print("wrote", out_sch)

    if xschem_available():
        result = render(out_sch, fmt="svg", outdir=outdir)
        if result.image_path:
            from IPython.display import SVG, display

            display(SVG(filename=str(result.image_path)))
        else:
            print("xschem ran but produced no SVG (symbol library not found?):", result.log[:300])
    else:
        print("xschem not on PATH — render skipped; open the .sch in xschem or the Studio viewer.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The CLI equivalent

    The same round-trip from the shell — `INPUT` is your existing `.sch`, not a netlist:

    ```bash
    # blocks.json: hand-authored, or written by circuitgraph's write_subcircuit_annotations(...)
    netlist2xschem ota-5t.sch --annotate-existing --annotations blocks.json -o ota-5t.annotated.sch
    ```

    ## Summary

    * `annotate_sch(sch_text, annotations)` overlays block boxes on a schematic **you already have** —
      hand-drawn layouts included — appending `B`/`T` graphics only; devices and wires are untouched.
    * The blocks JSON can be **hand-authored** (you know your circuit) or **detected** by `circuitgraph`
      from the schematic's own netlist; the two compose.
    * Instance-name join is `X`-prefix tolerant (`XM1` in the netlist ↔ `name=M1` in the drawing); a block
      whose devices aren't in the drawing warns and is skipped.
    * Contrast with the [auto-generation path](annotation_demo.py) (netlist → placement → boxes): that
      path *creates* a layout and is best-effort on complex circuits; this path respects yours.
    """)
    return


if __name__ == "__main__":
    app.run()
