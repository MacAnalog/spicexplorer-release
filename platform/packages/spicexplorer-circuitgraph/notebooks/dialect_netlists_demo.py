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
    # Foreign-dialect netlists: read → detect structures → re-emit

    The platform reads **Spectre** (`.scs`) and **HSPICE** netlists through the same `NetlistView`
    seam circuitgraph already consumes — the core dialect readers normalize the *structural subset*
    to canonical SPICE and preserve everything else (analyses, `.measure`, options, includes) as
    verbatim `Directive`s. On the way out, `to_netlist(dialect=…)` renders the graph in any dialect.

    Pure parsing — no ngspice / PDK needed. Fixtures are verbatim decks from analog-db's AnalogGym
    sensing-front-end reference corpus (BSD-3; see `tests/fixtures/README.md`).
    Design doc: meta-repo `doc/archive/plan_spectre_hspice_integration.md`.
    """)
    return


@app.cell
def _(mo):
    from spicexplorer_circuitgraph import (
        ANALOGGYM_REF,
        SKYWATER_SKY130,
        CircuitGraph,
        annotate_subcircuits,
        graphs_equivalent,
        to_netlist,
    )
    from spicexplorer_core.spice_engine import NetlistView

    FIX = mo.notebook_dir().parent / "tests" / "fixtures" / "dialects"
    sorted(p.name for p in FIX.iterdir())
    return (
        ANALOGGYM_REF,
        CircuitGraph,
        FIX,
        NetlistView,
        SKYWATER_SKY130,
        annotate_subcircuits,
        graphs_equivalent,
        to_netlist,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Read a verbatim Spectre deck

    `from_file` auto-detects the dialect (`.scs` extension → Spectre; content markers otherwise).
    Paren node lists, trailing-`\` continuations, `multi=`, and `subckt … ends` are normalized;
    the topology accessors then behave exactly like the classic SPICE path.
    """)
    return


@app.cell
def _(FIX, NetlistView):
    v = NetlistView.from_file(FIX / "ptat_65_classic.scs")
    print("dialect:", v.dialect.value)
    print("cells  :", v.get_subcircuit_names())
    cell = v.get_subcircuit_named("PTAT_65_classic1")
    for ref in cell.get_components():
        print(f"  {ref}: {cell.get_component_value(ref)}  nodes={cell.get_component_nodes(ref)}")
    return (cell,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Hand it to circuitgraph — unchanged

    `CircuitGraph.from_netlist` consumes the `NetlistViewLike` accessor surface, so a Spectre-read
    view needs zero circuitgraph changes. MOS polarity resolves via the `ANALOGGYM_REF` device-name
    map (or the built-in `nch`/`pch`/`nfet`/`pfet` fallback).
    """)
    return


@app.cell
def _(ANALOGGYM_REF, CircuitGraph, cell):
    g = CircuitGraph.from_netlist(cell, name="ptat_65", pdk=ANALOGGYM_REF)
    for comp in g.get_components():
        pol = getattr(comp, "polarity", None)
        print(f"  {comp.name:4} {comp.device_type.name:4} {pol.value if pol else ''}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Structure detection on the SMCNR amplifier

    The corpus's two-stage amplifier, read from its **Spectre rendering** — `annotate_subcircuits`
    finds the PMOS mirror bank and the PMOS differential pair.
    """)
    return


@app.cell
def _(ANALOGGYM_REF, CircuitGraph, FIX, NetlistView, annotate_subcircuits):
    amp_view = NetlistView.from_file(FIX / "smcnr_se_2st_amp.scs")
    amp_name = amp_view.get_subcircuit_names()[0]
    amp = CircuitGraph.from_netlist(
        amp_view.get_subcircuit_named(amp_name), name=amp_name, pdk=ANALOGGYM_REF
    )
    for grp in annotate_subcircuits(amp):
        print(f"  {grp.group_id:28} devices={grp.devices}")
    return (amp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Cross-dialect equivalence

    The same DUT exists upstream in **HSPICE** (`.orig.sp`, note the `xm…` devices, no `.end`) —
    read both forms and prove the graphs are isomorphic. Bare-subckt HSPICE fragments need the
    explicit `dialect="hspice"` hint (auto-detection is deliberately conservative).
    """)
    return


@app.cell
def _(CircuitGraph, FIX, NetlistView, amp, graphs_equivalent):
    hsp = NetlistView.from_file(FIX / "smcnr_se_2st_amp.orig.sp", dialect="hspice")
    amp_h = CircuitGraph.from_netlist(
        hsp.get_subcircuit_named("SMCNR_SE_2st_AMP"), name="amp_hspice"
    )
    print("graphs_equivalent:", graphs_equivalent(amp, amp_h))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. An HSPICE testbench: directives preserved, never translated

    Simulation cards (`.option`, `.measure`, `.lstb`, `.alter`, includes) are kept verbatim on
    `view.directives` — the topology parses cleanly around them, and foundry `.lib` paths are
    **never resolved**.
    """)
    return


@app.cell
def _(FIX, NetlistView):
    tb = NetlistView.from_file(FIX / "tb_ac_smcnr_se_2st_amp.sp")
    print(
        "dialect:",
        tb.dialect.value,
        "| devices:",
        len(tb.get_components()),
        "| directives:",
        len(tb.directives),
    )
    from collections import Counter

    print(Counter(d.kind for d in tb.directives))
    for d in tb.directives[:6]:
        print(f"  [{d.kind:8}] {d.text[:70]}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Emit back — any dialect, any PDK

    `to_netlist` renders through a per-dialect emitter family; `pdk=` composes with `dialect=`
    (cross-PDK × cross-dialect). `subckt=`/`ports=` wraps the devices as one definition — the
    shape you hand to another deck. Note the Spectre identifier rule: a name like `5t_ota`
    would be sanitized to `x5t_ota` (Spectre identifiers cannot start with a digit).
    """)
    return


@app.cell
def _(amp, to_netlist):
    print(
        to_netlist(
            amp, dialect="spectre", subckt="smcnr_amp", ports=["vdda", "gnda", "vin", "vip", "vout"]
        )
    )
    return


@app.cell
def _(SKYWATER_SKY130, amp, to_netlist):
    # the same graph, retargeted to sky130 device names, in canonical SPICE:
    print(to_netlist(amp, pdk=SKYWATER_SKY130))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Round-trip check

    Emitted Spectre re-parses through the reader to an isomorphic graph — the emitters and readers
    share one `DialectSpec` syntax table, so read and write can't drift apart.
    """)
    return


@app.cell
def _(CircuitGraph, NetlistView, amp, graphs_equivalent, to_netlist):
    scs_text = to_netlist(amp, dialect="spectre")
    amp_rt = CircuitGraph.from_netlist(
        NetlistView.from_string(scs_text, dialect="spectre"), name="rt"
    )
    print("round-trip equivalent:", graphs_equivalent(amp, amp_rt))
    return


if __name__ == "__main__":
    app.run()
