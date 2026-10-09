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
    # spicexplorer-circuitgraph quickstart

    A SPICE netlist becomes a **typed bipartite graph** (components ↔ nets) you can inspect,
    serialize for an LLM, and emit back — optionally **retargeted to another PDK**. This is the
    concise tour; the full walkthrough (strategy metrics, recursion, JSON contract details) is
    `circuitgraph_demo.py`, beside this notebook.
    """)
    return


@app.cell
def _(mo):
    from spicexplorer_circuitgraph import IHP_SG13G2, CircuitGraph
    from spicexplorer_core.spice_engine import NetlistView

    g = CircuitGraph.from_netlist(
        NetlistView.from_file(mo.notebook_dir() / "../tests/fixtures/ota-improved.spice"),
        pdk=IHP_SG13G2,
        name="ota",
    )
    print(g.component_count, "components,", g.net_count, "nets")
    return CircuitGraph, IHP_SG13G2, NetlistView, g


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inspect — the core primitive is `connections()` (pin → net)
    """)
    return


@app.cell
def _(g):
    m = g.get_components()[0]
    print(f"{m.name}  role={m.structural_role}")
    print("pins:", g.connections(m))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Practical: "what touches this net?"

    The bipartite structure makes net-centric questions one-liners — every component whose
    neighbourhood contains the net.
    """)
    return


@app.cell
def _(g):
    NET = "vout"
    on_net = [c.name for c in g.get_components() if NET in g.connections(c).values()]
    print(f"components on {NET!r}:", on_net)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Serialize for an LLM — pluggable strategies

    Each strategy is a different *view* of the same graph; `llm_description` is prose,
    `net_centric` is connection-oriented JSON.
    """)
    return


@app.cell
def _(g):
    from spicexplorer_circuitgraph import list_strategies, serialize

    print(list_strategies())
    print()
    print(serialize(g, "llm_description")[:400], "…")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cross-PDK retargeting — one graph, three foundries

    `to_netlist(g, pdk=…)` re-emits with the target PDK's device names + finger convention
    (e.g. sky130's per-finger `w`+`nf` vs IHP's total-`w`+`ng`). This is the engine behind the
    analog-db's tri-PDK lowering.
    """)
    return


@app.cell
def _(g):
    from spicexplorer_circuitgraph import GF180MCU, SKYWATER_SKY130, to_netlist

    def device_lines(netlist, n=2):
        return [l for l in netlist.splitlines() if l.lower().startswith("xm")][:n]

    for pdk, label in [(None, "IHP (source)"), (SKYWATER_SKY130, "sky130"), (GF180MCU, "gf180mcu")]:
        print(f"── {label}")
        for l in device_lines(to_netlist(g, pdk=pdk) if pdk else to_netlist(g)):
            print("  ", l)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Round-trip through the JSON contract

    `CircuitGraphDoc` is the Pydantic seam: JSON-dumpable, rebuildable, deep-copy safe — the
    contract agents and services exchange.
    """)
    return


@app.cell
def _(g):
    from spicexplorer_circuitgraph import CircuitGraphDoc

    doc = CircuitGraphDoc.from_graph(g)
    g2 = doc.to_graph()
    assert (g2.component_count, g2.net_count) == (g.component_count, g.net_count)
    print("round-trip OK —", len(doc.model_dump_json()), "bytes of JSON contract")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Subcircuits — black box or step in
    """)
    return


@app.cell
def _(CircuitGraph, IHP_SG13G2, NetlistView, mo):
    tb = CircuitGraph.from_netlist(
        NetlistView.from_file(mo.notebook_dir() / "../tests/fixtures/cora_testbench_ac.spice"),
        pdk=IHP_SG13G2,
        recurse=True,
    )
    x1 = tb._comp_map["X1"]
    print(
        "instance:",
        x1.subckt_name,
        "| ports:",
        [(p.name, str(p.role)) for p in x1.ports()][:4],
        "…",
    )
    print("child graphs:", {k: f"{v.component_count} comps" for k, v in tb.subgraphs.items()})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where to go next

    - The **full demo**: `circuitgraph_demo.py` in this folder (strategy
      metrics with `evaluate_strategies`, role detection, recursion details).
    - **analog-db** uses this engine to lower 20 circuits × 3 PDKs (`examples/analog-db/notebooks/`).
    - The **LLM annotation agent** (spicexplorer-orchestration) consumes the `llm_description` /
      `net_centric` views.
    """)
    return


if __name__ == "__main__":
    app.run()
