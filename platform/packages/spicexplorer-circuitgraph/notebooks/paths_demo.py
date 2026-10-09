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
    # Path tracing & path diffing

    Two capabilities on top of the bipartite circuit graph:

    - **`find_paths_between(graph, a, b)`** — the device-level paths joining two nets, each a
      `device.pin` chain like `XM1.gate->XM1.source`. `shortest_only=True` keeps the minimal ones.
    - **`diff_paths(p1, p2)`** — how two paths differ: a `pin_only` / `device_only` / `device_pin`
      verdict plus three segments (exclusive to each, and common).

    Everything is a pydantic model: `.model_dump()` / `.model_dump_json()` for JSON, `.describe()` for
    prose. Pure parsing — no ngspice/PDK install needed.
    """)
    return


@app.cell
def _():
    import itertools
    import json

    from spicexplorer_circuitgraph import (
        IHP_SG13G2,
        CircuitGraph,
        DiffKind,
        diff_paths,
        find_paths_between,
        shortest_paths_between,
    )
    from spicexplorer_circuitgraph.model.nodes import MosfetNode
    from spicexplorer_core import project_root
    from spicexplorer_core.spice_engine import NetlistView

    nl = project_root() / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
    ota = CircuitGraph.from_netlist(NetlistView.from_file(nl), pdk=IHP_SG13G2, name="ota")

    def show(paths):
        for p in paths:
            print(f"  [{p.length}] {p.label}")

    print(ota.component_count, "components,", ota.net_count, "nets")
    print("signal nets:", [n.name for n in ota.get_nets() if not n.is_supply][:8], "...")
    return (
        CircuitGraph,
        DiffKind,
        IHP_SG13G2,
        MosfetNode,
        NetlistView,
        diff_paths,
        find_paths_between,
        itertools,
        json,
        ota,
        shortest_paths_between,
        show,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.image(
        src=mo.notebook_dir() / "../../../examples/OTA/cascode/ihp-sg13g2/xschem/ota-improved.svg",
        alt="alt text",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Trace a path — input to the tail node
    """)
    return


@app.cell
def _(ota, shortest_paths_between):
    p = shortest_paths_between(ota, "vinp", "tail")[0]
    print(p.label)
    print(p.touchpoints)
    print(p.components)
    print()
    print(p.describe())
    return (p,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. All paths (bounded), and the data shape
    """)
    return


@app.cell
def _(find_paths_between, ota, show):
    paths = find_paths_between(ota, "vinp", "vout", max_components=3)
    print(len(paths), "paths (<=3 hops), shortest first:")
    show(paths)

    one = paths[0]
    print("\nas JSON:")
    print(one.model_dump_json(indent=2)[:420], "...")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Shortest vs all
    """)
    return


@app.cell
def _(find_paths_between, ota, shortest_paths_between, show):
    every = find_paths_between(ota, "vinp", "vout", max_components=6)
    short = shortest_paths_between(ota, "vinp", "vout")
    print(f"{len(every)} total paths (<=6 hops); {len(short)} shortest at {short[0].length} hops")
    show(short)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Supply rails are not traversed by default
    """)
    return


@app.cell
def _(find_paths_between, ota):
    without = find_paths_between(ota, "vinp", "vinn", max_components=4)
    through = find_paths_between(ota, "vinp", "vinn", max_components=4, through_supply=True)
    print(f"vinp->vinn: {len(without)} paths (default), {len(through)} when supply is allowed")
    rail = next(p for p in through if p.through_supply)
    print("a rail route:", rail.label)
    return


@app.cell
def _(ota, shortest_paths_between):
    # shortest path between two inputs
    _shortest = shortest_paths_between(graph=ota, net_a="vinp", net_b="vinn")
    print(f"found {len(_shortest)} shortest paths")

    for _path in _shortest:
        print("-", _path.label)
    return


@app.cell
def _(ota, shortest_paths_between):
    # shortest path between inputs and output
    _shortest = shortest_paths_between(graph=ota, net_a="vinp", net_b="vout")
    print(f"found {len(_shortest)} shortest paths")

    for _path in _shortest:
        print("-", _path.label)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Pin-level fan-out (diode-connected device)

    A diode-connected MOSFET has GATE and DRAIN on one net, so a single hop fans out into the distinct
    pin-level traversals. Here `M3` is `out1 out1 vdd vdd` (gate=drain=out1, source=bulk=vdd).
    """)
    return


@app.cell
def _(CircuitGraph, IHP_SG13G2, NetlistView, shortest_paths_between, show):
    core = CircuitGraph.from_netlist(
        NetlistView.from_string("""* ota core
    M1 out1 vinp tail vss sg13_lv_nmos
    M3 out1 out1 vdd vdd sg13_lv_pmos
    M4 out2 out1 vdd vdd sg13_lv_pmos
    .end"""),
        pdk=IHP_SG13G2,
    )

    m3 = {p.label: p for p in shortest_paths_between(core, "out1", "vdd") if p.components == ["M3"]}
    show(m3.values())
    return (m3,)


@app.cell
def _(m3):
    print(m3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. `diff_paths` — the four verdicts
    """)
    return


@app.cell
def _(diff_paths, p):
    # identical: a path against itself
    d_identical = diff_paths(p, p)
    print(d_identical.kind.value, "|", d_identical.summary)
    return


@app.cell
def _(diff_paths, m3):
    # pin_only: the same device entered through a different pin
    d_pin_only = diff_paths(m3["M3.drain->M3.source"], m3["M3.gate->M3.source"])
    print(d_pin_only.kind.value, "|", d_pin_only.summary)
    print("  only in A:", d_pin_only.only_in_a.touchpoints)
    print("  only in B:", d_pin_only.only_in_b.touchpoints)
    return


@app.cell
def _(DiffKind, diff_paths, find_paths_between, itertools, ota):
    # device_only: two routes between the same nets through different devices
    routes = find_paths_between(ota, "d_ena", "dp_casc", max_components=3)
    d_device_only = next(
        d_device_only
        for a, b in itertools.combinations(routes, 2)
        if (d_device_only := diff_paths(a, b)).kind is DiffKind.DEVICE_ONLY
    )
    print(d_device_only.kind.value, "|", d_device_only.summary)
    print(
        "  only A:", d_device_only.only_in_a.devices, "| only B:", d_device_only.only_in_b.devices
    )
    print("  common:", d_device_only.common.touchpoints)
    return


@app.cell
def _(diff_paths, ota, shortest_paths_between):
    # device_pin: both a missing device and a re-pinned device
    d_device_pin = diff_paths(
        shortest_paths_between(ota, "vinp", "tail")[0],
        shortest_paths_between(ota, "vinp", "vout")[0],
    )
    print(d_device_pin.kind.value, "|", d_device_pin.summary)
    return (d_device_pin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. JSON & text for an LLM / reviewer
    """)
    return


@app.cell
def _(d_device_pin, json):
    print(d_device_pin.describe())
    print("\n--- structured (JSON) ---")
    print(json.dumps({k: d_device_pin.model_dump()[k] for k in ("kind", "summary")}, indent=2))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Conduction-aware tracing (MOSFET on/off state)

    `respect_mosfet_state=True` drops a MOSFET's drain↔source **channel** when the device is off —
    gate–source shorted (Vgs=0). Gate edges stay (channel-only scope), and `gs_short_is_off=False` is
    the depletion / negative-Vth escape hatch. Drain–source-shorted devices are *killed* (e.g. MOS
    decoupling caps), detected via `is_drain_source_shorted`.
    """)
    return


@app.cell
def _(CircuitGraph, IHP_SG13G2, NetlistView, find_paths_between):
    off = CircuitGraph.from_netlist(
        NetlistView.from_string("""* gate-source short
    M1 nin g1 nmid vss sg13_lv_nmos
    M2 nmid nout nout vss sg13_lv_nmos
    .end"""),
        pdk=IHP_SG13G2,
    )

    print("M2 gate-source shorted (off)?", off._comp_map["M2"].is_gate_source_shorted(off._G))
    trace = lambda **k: [p.label for p in find_paths_between(off, "nmid", "nout", **k)]
    print("topological:  ", trace())
    print("conduction:   ", trace(respect_mosfet_state=True))  # channel dropped
    print("depletion-on: ", trace(respect_mosfet_state=True, gs_short_is_off=False))  # channel kept
    return


@app.cell
def _(MosfetNode, ota):
    # real "killed" devices: MOS decoupling caps (drain=source=bulk=rail) in the cascode OTA
    killed = [
        c.name
        for c in ota.get_components()
        if isinstance(c, MosfetNode) and c.is_drain_source_shorted(ota._G)
    ]
    print("drain-source shorted (MOS-cap / killed):", killed)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Excluding ideal voltage sources

    Like supply rails (§4), an **ideal voltage source** can be pruned so a path never threads *through*
    it — in one terminal, out the other — which keeps a DC bias source from bridging otherwise-separate
    signal nets. `block_voltage_sources=True` drops only those through-source routes; it is **off by
    default**, so every trace above is unaffected. Here one `vinp→vout` route runs through the bias
    source `V2` (seen in §2) and disappears once sources are blocked.
    """)
    return


@app.cell
def _(ota, shortest_paths_between, show):
    with_v = shortest_paths_between(ota, "vinp", "vout")
    no_v = shortest_paths_between(ota, "vinp", "vout", block_voltage_sources=True)
    print(
        f"vinp->vout: {len(with_v)} shortest (default), {len(no_v)} when voltage sources are blocked\n"
    )

    through_vsrc = lambda p: any(s.device_type.value == "VSOURCE" for s in p.steps)
    print("dropped (threads through a V source):")
    for _p in with_v:
        if through_vsrc(_p):
            print("  -", _p.label)
    print("kept:")
    show(no_v)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Edge cases & guardrails
    """)
    return


@app.cell
def _(
    CircuitGraph,
    IHP_SG13G2,
    NetlistView,
    find_paths_between,
    ota,
    shortest_paths_between,
):
    for a, b in [("vinp", "vinp"), ("nope", "tail")]:
        try:
            find_paths_between(ota, a, b)
        except ValueError as e:
            print(f"{a!r},{b!r} -> ValueError: {e}")

    print(
        "disconnected nets ->",
        find_paths_between(
            CircuitGraph.from_netlist(
                NetlistView.from_string("""* disjoint
    M1 a g1 b vss sg13_lv_nmos
    M2 c g2 d vss sg13_lv_nmos
    .end"""),
                pdk=IHP_SG13G2,
            ),
            "a",
            "c",
        ),
    )

    print("case-insensitive ->", shortest_paths_between(ota, "VINP", "TAIL")[0].label)
    return


if __name__ == "__main__":
    app.run()
