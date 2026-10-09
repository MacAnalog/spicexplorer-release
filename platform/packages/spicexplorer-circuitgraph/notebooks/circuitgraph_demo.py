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
    # spicexplorer-circuitgraph — a netlist as a typed circuit graph

    `spicexplorer-circuitgraph` turns a SPICE netlist into a **typed bipartite graph** (nets ⟷
    components), serializes it to JSON / textual views for downstream consumption (LLMs, analysis),
    and round-trips a graph **back** to a netlist with PDK-specific device names.

    It is a **leaf tool**: it reads netlists through `spicexplorer_core.spice_engine.NetlistView`,
    depends on `spicexplorer-core` only, and is fully deterministic (no LLM/framework deps). Everything
    below is pure parsing — **no ngspice or PDK install needed.**

    > Sister demo: `examples/OTA/cascode/netlist2tf/netlist2tf_demo.py` (symbolic transfer functions).
    """)
    return


@app.cell
def _():
    from spicexplorer_circuitgraph import (
        IHP_SG13G2,
        SKYWATER_SKY130,
        CircuitGraph,
        CircuitGraphDoc,
        evaluate_strategies,
        list_strategies,
        serialize,
        to_netlist,
    )
    from spicexplorer_core import project_root
    from spicexplorer_core.spice_engine import NetlistView

    return (
        CircuitGraph,
        CircuitGraphDoc,
        IHP_SG13G2,
        NetlistView,
        SKYWATER_SKY130,
        evaluate_strategies,
        list_strategies,
        project_root,
        serialize,
        to_netlist,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Netlist → typed bipartite graph

    `CircuitGraph.from_netlist` reads a `NetlistView` and builds the graph. We start with a tiny
    inline common-source stage (a `NetlistView.from_string`); a `pdk=` map tells it how to recognise
    device names (here IHP `sg13g2`). The graph is **bipartite**: component nodes and net nodes, with
    a pin-labelled edge for every terminal.
    """)
    return


@app.cell
def _(CircuitGraph, IHP_SG13G2, NetlistView):
    CS = """* common-source stage
    M1  out in 0 0 sg13_lv_nmos W=1u L=0.13u
    RL  out vdd 10k
    C1  out 0   100f
    Vdd vdd 0   1.2
    Vin in 0    dc 0.6 ac 1
    .end"""

    g = CircuitGraph.from_netlist(NetlistView.from_string(CS), pdk=IHP_SG13G2, name="cs")
    print(g.component_count, "components,", g.net_count, "nets")
    return (g,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Inspect connectivity — the core primitive (pin → net, per component)

    `g.get_components()` returns the typed component nodes (MOS / R / C / L / V / I); `g.connections(c)`
    is that component's `{pin: net}` map. Each node carries its kind (the Python type), its device
    `parameters`, and a `structural_role` slot that an LLM annotator fills in downstream (it is `None`
    here — the deterministic core never guesses roles).

    `connections(c)` is **lossless** — it includes the MOSFET `BULK` (body) terminal, which is what the
    round-trip contract and netlist emission rely on. The *description* views in §3 drop `BULK` by
    default (`include_body=False`) since the body tie — NMOS→VSS / PMOS→VDD — rarely carries topological
    meaning and just clutters the output; pass `include_body=True` to keep it.
    """)
    return


@app.cell
def _(g):
    for c in g.get_components():
        kind = type(c).__name__
        print(f"{c.name:5} {kind:16} role={c.structural_role}  {g.connections(c)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Serialize for an LLM / analysis — pluggable strategies

    The same graph renders into several **views**, each a registered strategy. `net_centric` is the
    LLM-ready JSON keyed by net; `llm_description` is a prose topology walk. Pick whichever fits the
    consumer — they all describe the *same* deterministic graph.
    """)
    return


@app.cell
def _(g, list_strategies, serialize):
    print("available strategies:", list_strategies())
    print()

    # net-centric JSON view (keyed by net name) — what an LLM topology annotator consumes
    nc = serialize(g, "net_centric", include_params=True)
    print("net_centric nets:", list(nc))
    print('  net "out" ->', nc["out"])
    return


@app.cell
def _(g, serialize):
    # ...or a prose description of the same graph
    print(serialize(g, "llm_description"))
    return


@app.cell
def _(g, serialize):
    # Body/BULK pin: dropped from the description views by default, kept on demand with include_body=True.
    print("default (no body):  M1 ->", serialize(g, "flat")["M1"])
    print("include_body=True:  M1 ->", serialize(g, "flat", include_body=True)["M1"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Compare views deterministically — `evaluate_strategies`

    Different consumers have different token budgets. `evaluate_strategies` renders every strategy and
    reports a token estimate + component coverage, so you can pick the cheapest view that still covers
    the whole circuit. Here on the real committed cascode OTA fixture (24 components).
    """)
    return


@app.cell
def _(
    CircuitGraph,
    IHP_SG13G2,
    NetlistView,
    evaluate_strategies,
    project_root,
):
    nl = project_root() / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
    ota = CircuitGraph.from_netlist(NetlistView.from_file(nl), pdk=IHP_SG13G2, name="ota")
    print(ota.component_count, "components,", ota.net_count, "nets\n")

    print(f"{'strategy':26} {'~tokens':>8}  coverage")
    for r in evaluate_strategies(ota):
        print(f"{r.name:26} {r.token_estimate:8}  {r.component_coverage}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Graph → netlist, retargeting device names to another PDK

    `to_netlist` emits a **re-parseable** netlist. Pass a different `pdk=` and the device names are
    retargeted — the same topology, IHP `sg13g2` names vs Skywater `sky130` names. (Parameters and
    connectivity are unchanged; only the model/device tokens map.)
    """)
    return


@app.cell
def _(SKYWATER_SKY130, g, to_netlist):
    print("--- IHP sg13g2 ---")
    print(to_netlist(g))
    print("--- Skywater sky130 ---")
    print(to_netlist(g, pdk=SKYWATER_SKY130))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Round-trip through the JSON contract

    `CircuitGraphDoc` is the serialize/deserialize seam — a Pydantic model you can dump to JSON and
    rebuild an independent, equal graph from. This is the boundary the REST/MCP adapters will speak.
    """)
    return


@app.cell
def _(CircuitGraphDoc, g):
    doc = CircuitGraphDoc.from_graph(g)  # pydantic, JSON-dumpable
    blob = doc.model_dump_json()
    print("contract JSON:", len(blob), "chars; top-level keys:", list(doc.model_dump())[:6])

    g2 = CircuitGraphDoc.model_validate_json(blob).to_graph()  # independent rebuild
    print(
        "rebuilt graph:",
        g2.component_count,
        "components,",
        g2.net_count,
        "nets",
        "| matches original:",
        g2.component_count == g.component_count,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Subcircuits — black-box ports, or step in recursively

    An `X…` subcircuit instance graphs as a **black-box component** with named, role-tagged ports
    (INPUT / OUTPUT / POWER / GROUND / BIAS …). Pass `recurse=True` to also build a child graph per
    instance (`graph.subgraphs`) while the parent black box stays in place.
    """)
    return


@app.cell
def _(CircuitGraph, IHP_SG13G2, NetlistView, project_root):
    tb = project_root() / "examples/OTA/folded_cascode/ihp-sg13g2/spice/cora_testbench_ac.spice"
    gtb = CircuitGraph.from_netlist(NetlistView.from_file(tb), pdk=IHP_SG13G2)

    x1 = gtb._comp_map["X1"]  # a SubcktInstanceNode
    print(x1.name, "->", x1.subckt_name)
    for p in x1.ports():
        print(f"   port {p.name:6} role={p.role}")
    return (tb,)


@app.cell
def _(CircuitGraph, IHP_SG13G2, NetlistView, tb):
    # ...or step inside: a child graph per X… instance
    grec = CircuitGraph.from_netlist(NetlistView.from_file(tb), pdk=IHP_SG13G2, recurse=True)
    for name, sub in grec.subgraphs.items():
        print(f"subgraph {name!r}: {sub.component_count} components, {sub.net_count} nets")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Where this goes

    * **Downstream LLM role-annotation** — writing `structural_role` back onto the graph from a
      `serialize(graph, 'net_centric')` view — is provider-agnostic and lives in
      `spicexplorer-orchestration` (`agents/annotation`), not in this deterministic leaf.
    * **Surface adapters** (MCP / REST / UI) and the matplotlib `[viz]` helpers are deferred.

    README: `packages/spicexplorer-circuitgraph/README.md` · plan + tracker live in the meta-repo.
    """)
    return


if __name__ == "__main__":
    app.run()
