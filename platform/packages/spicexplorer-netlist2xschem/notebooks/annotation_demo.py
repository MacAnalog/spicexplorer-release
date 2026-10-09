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
    # netlist2xschem — functional-block annotation overlay

    Once an upstream detector recognises the **functional sub-circuits** in a netlist (current mirrors,
    differential pairs, …), this tool can draw them onto the schematic as labelled, coloured **bounding
    boxes** — proof that the structural-detection pipeline fired, and a debugging aid for reading larger
    circuits.

    Three things make this clean:

    * **It is additive.** Boxes are xschem graphic rectangles (`B`) + text (`T`) drawn *over* the existing
      placement. No device moves, no wire is added, so the schematic's connectivity round-trip is
      unchanged.
    * **It is decoupled.** The input is a *neutral contract* — the `spicexplorer/xschem-block-annotations@1`
      JSON. `netlist2xschem` never imports the detector; any producer that emits the schema can drive the
      overlay. Here the producer is `circuitgraph`'s `export_subcircuit_annotations`.
    * **It joins by instance name.** A block lists the device refs it contains (`XM5`, `XM6`, …) — the same
      refs the netlist uses — so the overlay lands on exactly those placed devices.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The contract — `BlockAnnotation` / `BlockAnnotationSet`
    """)
    return


@app.cell
def _():
    from spicexplorer_netlist2xschem import (
        ANNOTATION_SCHEMA,
        BlockAnnotation,
        BlockAnnotationSet,
    )

    # Hand-author a tiny overlay: one current mirror made of two devices.
    aset = BlockAnnotationSet(
        (
            BlockAnnotation(
                block_id="cm.nmos.simple#1",
                devices=("XM5", "XM6"),  # the join key — host instance refs
                label="current mirror (nmos)",
                family="current_mirror",
            ),
        )
    )
    print("schema:", ANNOTATION_SCHEMA)
    print(aset.to_json())
    return BlockAnnotationSet, aset


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It round-trips through JSON (file, string, or dict) — that JSON is the only thing the detector and
    the renderer share.
    """)
    return


@app.cell
def _(BlockAnnotationSet, aset):
    roundtrip = BlockAnnotationSet.from_json(aset.to_json())
    assert roundtrip == aset
    print("round-trip OK:", roundtrip == aset)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. End to end on a 5T OTA — detect → export → annotate

    We compose the two leaf tools the way orchestration would: `circuitgraph` detects the sub-circuits and
    exports the contract; `netlist2xschem` consumes it. Both read the *same* netlist, so the instance-name
    join is exact.
    """)
    return


@app.cell
def _():
    from spicexplorer_circuitgraph import (
        CircuitGraph,
        export_subcircuit_annotations,
        find_subcircuits,
        group_matches,
    )
    from spicexplorer_core import project_root
    from spicexplorer_core.spice_engine import NetlistView
    from spicexplorer_netlist2xschem import build_sch, from_file

    netlist_5t = project_root() / "examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice"

    # --- PRODUCER: detect, then export the neutral contract -----------------------------------------
    graph = CircuitGraph.from_netlist(NetlistView.from_file(netlist_5t), name="ota_5t")
    groups = group_matches(find_subcircuits(graph))
    contract_5t = export_subcircuit_annotations(groups)

    for _b in contract_5t["blocks"]:
        print(f"{_b['block_id']:22s} {_b['family']:17s} {_b['devices']}")
    return (
        CircuitGraph,
        NetlistView,
        build_sch,
        contract_5t,
        export_subcircuit_annotations,
        find_subcircuits,
        from_file,
        group_matches,
        netlist_5t,
        project_root,
    )


@app.cell
def _(BlockAnnotationSet, build_sch, contract_5t, from_file, netlist_5t):
    # --- CONSUMER: place the netlist and draw the blocks over it ------------------------------------
    circuit_5t = from_file(netlist_5t, name="ota_5t")
    doc_5t = build_sch(circuit_5t, annotations=BlockAnnotationSet.from_dict(contract_5t))

    print(
        f"{doc_5t.device_count} devices, {doc_5t.annotation_count} blocks, {len(doc_5t.warnings)} warnings"
    )
    # the overlay only *adds* B/T lines — these are the boxes and their labels:
    for _line in doc_5t.text.splitlines():
        if _line.startswith(("B ", "T ")):
            print(" ", _line)
    return circuit_5t, doc_5t


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three blocks: the PMOS load mirror, the NMOS tail mirror, and the differential pair (admitted only
    because its tail sits on the NMOS mirror's output). Each box is a different colour (`B <layer> …`) and
    its label is tinted to match (`T … {layer=<layer>}`).

    **Connectivity is untouched** — the overlay is purely graphical:
    """)
    return


@app.cell
def _(build_sch, circuit_5t, doc_5t):
    base = build_sch(circuit_5t)  # no annotations
    assert (doc_5t.wire_count, doc_5t.label_count, doc_5t.port_count) == (
        base.wire_count,
        base.label_count,
        base.port_count,
    )
    print(
        "wires/labels/ports unchanged by the overlay:",
        (doc_5t.wire_count, doc_5t.label_count, doc_5t.port_count),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Nesting and alternates — a cascode mirror

    A cascode current mirror *contains* a simple mirror. The detector reports the simple pair as
    **subsumed** inside the cascode; the exporter emits it as a nested block (`parent_id` set), and the
    renderer draws it as a smaller **dashed** box inside the parent. Templates that match the *same*
    devices (here `improved_wilson`, byte-identical to the cascode) are folded into the label as
    `[alt: …]` rather than drawn as their own box.
    """)
    return


@app.cell
def _(
    BlockAnnotationSet,
    CircuitGraph,
    NetlistView,
    build_sch,
    export_subcircuit_annotations,
    find_subcircuits,
    group_matches,
):
    cascode = """* cascode nmos current mirror
    XM1 net2 net1 VSS VSS sg13_lv_nmos
    XM2 net1 net1 VSS VSS sg13_lv_nmos
    XM3 iout iin net1 VSS sg13_lv_nmos
    XM4 iin iin net2 VSS sg13_lv_nmos
    .end
    """
    from spicexplorer_netlist2xschem import from_string

    g_cascode = CircuitGraph.from_netlist(NetlistView.from_string(cascode), name="cascode")
    contract_cascode = export_subcircuit_annotations(group_matches(find_subcircuits(g_cascode)))
    for _b in contract_cascode["blocks"]:
        kind = "nested" if _b["parent_id"] else "top  "
        print(f"[{kind}] {_b['block_id']:40s} devs={_b['devices']}")

    doc_cascode = build_sch(
        from_string(cascode, name="cascode"),
        annotations=BlockAnnotationSet.from_dict(contract_cascode),
    )
    print()
    for _line in doc_cascode.text.splitlines():
        if _line.startswith(("B ", "T ")):
            print(" ", _line)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The nested `B … {fill=0 dash=4}` box sits inside the solid parent box — you can see its `x0/y0/x1/y1`
    are bracketed by the parent's.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. It scales — a folded-cascode OTA (16 devices)

    On a larger circuit the blocks don't just get boxed — by default they **drive the placement**.
    `build_sch(circuit, annotations=…)` feeds the detected blocks to the placer as `PlacementHints`, so
    each block's devices are clustered into a tight, mostly-separate region under its box instead of being
    scattered by raw topology. It is a layout-only hint — connectivity is identical either way (a Docker
    `xschem -n` round-trip confirms it). On the multi-stage amplifiers this cuts the total block-box
    overlap by ~50% (one case −77%); see the before/after review set under
    `examples/analog-db/raw/_p5_block_aware_placement/`. Pass `annotation_aware_placement=False` (CLI
    `--no-block-placement`) to keep the older block-agnostic layout and draw the boxes over it.
    """)
    return


@app.cell
def _(
    BlockAnnotationSet,
    CircuitGraph,
    NetlistView,
    build_sch,
    export_subcircuit_annotations,
    find_subcircuits,
    from_file,
    group_matches,
    project_root,
):
    netlist_folded = (
        project_root() / "examples/analog-db/circuits/amp_004_folded_cascode/abstract/netlist.spice"
    )
    g_folded = CircuitGraph.from_netlist(
        NetlistView.from_file(netlist_folded), name="folded_cascode"
    )
    contract_folded = export_subcircuit_annotations(group_matches(find_subcircuits(g_folded)))
    circuit_folded = from_file(netlist_folded, name="folded_cascode")
    doc_folded = build_sch(
        circuit_folded, annotations=BlockAnnotationSet.from_dict(contract_folded)
    )
    print(f"{doc_folded.device_count} devices placed, {doc_folded.annotation_count} blocks drawn")
    for _b in contract_folded["blocks"]:
        print(f"  {_b['family']:17s} {_b['devices']}")
    return (doc_folded,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Render it (needs xschem)

    `render()` rasterises the `.sch` via headless xschem (the EDA Docker image; not the macOS host). When
    xschem is absent it returns `available=False` and the `.sch` is still valid for the UI viewer. The
    boxes render in the same `.sch` you'd open in the Studio Schematic tab.
    """)
    return


@app.cell
def _(doc_folded, mo):
    from spicexplorer_netlist2xschem import render, xschem_available

    out = mo.notebook_dir() / "folded_cascode_annotated.sch"
    out.write_text(doc_folded.text)
    if xschem_available():
        result = render(out, fmt="svg")
        print("rendered:", result.image_path.name if result.image_path else None)
        from IPython.display import SVG, display

        if result.image_path:
            display(SVG(filename=str(result.image_path)))
    else:
        print(
            "xschem not on PATH — wrote",
            out,
            "(open it in the Studio viewer, or render in the EDA container).",
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. CLI

    The producer writes the contract; the consumer reads it with `--annotations`:

    ```bash
    # 1. detect + export (circuitgraph) — write the neutral JSON
    python -c "from spicexplorer_core.spice_engine import NetlistView; \
    from spicexplorer_circuitgraph import CircuitGraph, find_subcircuits, group_matches, write_subcircuit_annotations; \
    g = CircuitGraph.from_netlist(NetlistView.from_file('ota.spice'), name='ota'); \
    write_subcircuit_annotations(group_matches(find_subcircuits(g)), 'ota.blocks.json')"

    # 2. generate the schematic with block-aware placement + the boxes (netlist2xschem)
    netlist2xschem ota.spice -o ota.sch --annotations ota.blocks.json --render svg
    #   add --no-block-placement to box the old block-agnostic layout instead
    ```

    ## Summary

    * **`BlockAnnotation` / `BlockAnnotationSet`** — the neutral `xschem-block-annotations@1` contract,
      joined to the schematic by device instance name.
    * **`build_sch(circuit, annotations=…)`** / **`netlist2xschem --annotations`** — draw each block as a
      labelled, coloured box, nested boxes for subsumed sub-blocks, alternates in the label.
    * **Block-aware placement (default on)** — the same blocks become `PlacementHints` that cluster each
      block's devices into its own region (`annotation_aware_placement=False` / `--no-block-placement`
      keeps the old layout). Connectivity is unchanged; the detector is reached only through the JSON
      (`circuitgraph.export_subcircuit_annotations` is one producer).
    """)
    return


if __name__ == "__main__":
    app.run()
