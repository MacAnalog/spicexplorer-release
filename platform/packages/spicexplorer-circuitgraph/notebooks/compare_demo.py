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
    # Comparing two netlists — *are these the same circuit?*

    `spicexplorer_circuitgraph.compare_netlists` builds a typed bipartite graph for each netlist and
    tests them for a **labeled graph isomorphism** — equal up to renaming instances/nets and reordering
    lines, while preserving device type, MOS polarity, and pin-level wiring.

    By default the test is **topological** and ignores all names, sizing, and model strings — with one
    exception: **supply rails** (`VDD`/`VSS`/`GND`) are anchored by class. Optional flags tighten it
    (`match_params`, `match_models`, …) and `IOPort` anchors named input/output ports. Everything below
    is pure parsing — **no ngspice or PDK install needed.**

    > Sister demo: [`circuitgraph_demo.py`](circuitgraph_demo.py) (build → serialize → emit → round-trip).
    """)
    return


@app.cell
def _():
    import random
    import re

    from spicexplorer_circuitgraph import (
        IHP_SG13G2,
        CircuitGraph,
        IOPort,
        compare_netlists,
        netlists_equivalent,
    )
    from spicexplorer_core import project_root
    from spicexplorer_core.spice_engine import NetlistView

    PDK = IHP_SG13G2
    load = lambda rel: (project_root() / rel).read_text()
    eq = lambda a, b, **kw: netlists_equivalent(a, b, pdk=PDK, **kw)  # -> bool
    why = lambda a, b, **kw: compare_netlists(a, b, pdk=PDK, **kw).reason  # -> explanation

    def scramble(text, *, keep=(), seed=1):
        """Same circuit, different text: rename internal nets + instances and reverse line order.
        Supply rails and any `keep` nets stay fixed (so they remain anchorable)."""
        g = CircuitGraph.from_netlist(NetlistView.from_string(text), pdk=PDK)
        keep = {k.lower() for k in keep}
        rng = random.Random(seed)
        nets = [n.name for n in g.get_nets() if not n.supply_type and n.name.lower() not in keep]
        comps = [c.name for c in g.get_components()]
        m = {n: f"q{i}" for i, n in enumerate(rng.sample(nets, len(nets)))}
        m |= {
            # keep the SPICE type letter; [A-Za-z_]* always matches, if only the empty string
            c: re.match(r"[A-Za-z_]*", c).group() + str(i)  # pyright: ignore[reportOptionalMemberAccess]
            for i, c in enumerate(rng.sample(comps, len(comps)))
        }
        out = re.sub(r"[A-Za-z_][\w.]*", lambda mo: m.get(mo.group(), mo.group()), text)
        cards = [ln for ln in out.splitlines() if ln[:1].isalpha()]
        return "\n".join(["* scrambled"] + cards[::-1] + [".end"])

    return IOPort, PDK, compare_netlists, eq, load, scramble, why


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Same circuit, different text

    Renaming every instance and net and reordering the lines does not change the circuit — on a tiny
    inline stage and on the real cascode OTA (24 devices). A match returns one valid `a→b` name mapping.
    """)
    return


@app.cell
def _(PDK, compare_netlists, eq, load, scramble):
    A = """* common-source, version A
    M1  out in 0 0 sg13_lv_nmos w=1u l=0.13u
    RL  out vdd 10k
    C1  out 0 100f
    Vdd vdd 0 1.2
    Vin in 0 dc 0.6 ac 1
    .end"""
    B = """* version B — every instance & net renamed, lines reordered
    Vsupply vdd 0 1.2
    Cload no 0 100f
    Mamp no sig 0 0 sg13_lv_nmos w=1u l=0.13u
    Vsig sig 0 dc 0.6 ac 1
    Rload no vdd 10k
    .end"""
    print("inline  A vs B          :", eq(A, B))

    OTA = load("examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice")
    res = compare_netlists(OTA, scramble(OTA), pdk=PDK)
    print("cascode OTA vs scrambled:", bool(res), "|", res.reason)
    print("  comp map e.g.:", dict(list(res.component_mapping.items())[:3]))
    print("  net  map e.g.:", dict(list(res.net_mapping.items())[:3]))
    return (OTA,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Real differences are caught — with a reason

    Touching the topology of the real OTA: move a transistor's gate, flip one NMOS to PMOS, or delete a
    device. Each is rejected with a human-readable explanation (the cheap pre-checks fire before the
    isomorphism search).
    """)
    return


@app.cell
def _(OTA, why):
    moved = OTA.replace("XM1 net4 vinp tail vss", "XM1 net4 vss tail vss")  # gate -> vss
    pol = OTA.replace(
        "XM5 net6 gate vss vss sg13_lv_nmos", "XM5 net6 gate vss vss sg13_lv_pmos"
    )  # one nmos -> pmos
    short = "\n".join(l for l in OTA.splitlines() if not l.startswith("XMpd11"))  # drop one device

    for tag, mut in [("moved gate", moved), ("nmos->pmos", pol), ("deleted dev", short)]:
        print(f"{tag:12}:", why(OTA, mut))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Passive symmetry vs. source polarity

    A resistor/cap/inductor is non-polar, so swapping its two terminals is the *same* circuit
    (`passive_symmetry=True`, default). Voltage/current sources keep their `+`/`-` orientation, and so
    do MOSFET pins.
    """)
    return


@app.cell
def _(eq):
    RA = "* a\nR1 a b 1k\nC1 b 0 1p\nV1 a 0 1\n.end"
    RB = "* b\nR1 b a 1k\nC1 0 b 1p\nV1 a 0 1\n.end"  # R and C terminals swapped
    print("R/C terminal swap, default     :", eq(RA, RB))
    print("R/C terminal swap, strict pins :", eq(RA, RB, passive_symmetry=False))

    VA = "* a\nV1 p 0 1\nR1 p 0 1k\n.end"
    VB = "* b\nV1 0 p 1\nR1 p 0 1k\n.end"  # source +/- flipped
    print("source +/- flip (stays polar)  :", eq(VA, VB))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Supply rails are special

    The one place a net *name* matters by default: rails are anchored by class, so a device tied across
    `vdd`/`vss` is not the same as a floating one. `match_supply=False` drops even that for a fully
    name-blind, pure-topology test.
    """)
    return


@app.cell
def _(eq, why):
    SA = "* a\nR1 vdd vss 1k\n.end"
    SB = "* b\nR1 n1 n2 1k\n.end"
    print("R across rails vs floating, default :", eq(SA, SB), "|", why(SA, SB))
    print("                  match_supply=False:", eq(SA, SB, match_supply=False))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Sizing & models are opt-in

    Same topology with different `W`/`L` or a different model flavor is equivalent by default. Opt in
    with `match_params` / `match_models`. Parameters are engineering-normalized, so `0.18u == 180n`.
    """)
    return


@app.cell
def _(eq):
    G1 = "* a\nM1 d g s b sg13_lv_nmos w=1u l=0.18u\nR1 d vdd 1k\n.end"
    G2 = "* b\nM1 d g s b sg13_lv_nmos w=2u l=180n\nR1 d vdd 1k\n.end"  # different W
    G3 = "* c\nM1 d g s b sg13_lv_nmos w=1u l=180n\nR1 d vdd 1k\n.end"  # l: 0.18u == 180n
    M2 = "* m\nM1 d g s b sg13_hv_nmos w=1u l=0.18u\nR1 d vdd 1k\n.end"  # hv model flavor

    print("different W,     default       :", eq(G1, G2))
    print("different W,     match_params  :", eq(G1, G2, match_params=True))
    print("0.18u vs 180n,  match_params  :", eq(G1, G3, match_params=True))
    print("different model, default      :", eq(G1, M2))
    print("different model, match_models :", eq(G1, M2, match_models=True))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Differential I/O anchoring

    `IOPort` pins a named port so it can only map to the matching port, never an internal net. A
    differential pair is *swappable* by default (a differential signal has no inherent `+`/`-`), so an
    input swap is still the same circuit; `swappable=False` commits to the polarity and flags it. When
    the two sides name their I/O differently, pass `io_ports_b` (ports correspond by position).
    """)
    return


@app.cell
def _(IOPort, eq):
    DA = """* balanced differential pair
    M1 outp vinp tail vss sg13_lv_nmos w=2u l=0.13u
    M2 outn vinn tail vss sg13_lv_nmos w=2u l=0.13u
    R1 vdd outp 5k
    R2 vdd outn 5k
    M5 tail vbias vss vss sg13_lv_nmos w=4u l=0.5u
    .end"""
    DB = """* same pair, but with vinp/vinn (+/-) swapped
    M1 outp vinn tail vss sg13_lv_nmos w=2u l=0.13u
    M2 outn vinp tail vss sg13_lv_nmos w=2u l=0.13u
    R1 vdd outp 5k
    R2 vdd outn 5k
    M5 tail vbias vss vss sg13_lv_nmos w=4u l=0.5u
    .end"""
    ports = lambda sw: [
        IOPort("vinp", "vinn", swappable=sw),  # the input pair
        IOPort("outp", "outn", swappable=False),
    ]  # outputs pinned
    print("swapped inputs, pair swappable (default):", eq(DA, DB, io_ports=ports(True)))
    print("swapped inputs, pair strict polarity    :", eq(DA, DB, io_ports=ports(False)))

    DC = (
        DA.replace("vinp", "inp").replace("vinn", "inn").replace("outp", "op").replace("outn", "on")
    )
    print(
        "sides name I/O differently (io_ports_b) :",
        eq(
            DA,
            DC,
            io_ports=[IOPort("vinp", "vinn"), IOPort("outp", "outn")],
            io_ports_b=[IOPort("inp", "inn"), IOPort("op", "on")],
        ),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Anchoring on a real design + guardrails

    Anchor the real OTA's `vinp`/`vinn`/`vout` and it still matches its scrambled twin (the anchors bind
    and the rest stays topological). Empty netlists are trivially equal. A typo'd anchor — a port net
    absent from the netlist — is a hard error, not a silently looser comparison.
    """)
    return


@app.cell
def _(IOPort, OTA, PDK, compare_netlists, eq, scramble):
    S = scramble(OTA, keep=("vinp", "vinn", "vout"))
    res_anchored = compare_netlists(
        OTA, S, pdk=PDK, io_ports=[IOPort("vinp", "vinn"), IOPort("vout")]
    )
    print("real OTA, scrambled + I/O anchored :", bool(res_anchored), "|", res_anchored.reason)
    print("empty vs empty                     :", eq("* a\n.end", "* b\n.end"))

    try:
        compare_netlists(OTA, S, pdk=PDK, io_ports=[IOPort("vinp", "vinn"), IOPort("nope")])
    except ValueError as err:
        print("typo'd anchor -> ValueError        :", err)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    **Recap.** `compare_netlists(a, b)` decides circuit equivalence via labeled graph isomorphism:
    name- and order-independent, supply-rail aware, with `match_params` / `match_models` /
    `passive_symmetry` / `match_supply` to tune strictness and `IOPort(...)` (single-ended or
    differential, swappable or strict) to anchor named ports. `compare_graphs(g1, g2, …)` is the same on
    already-built graphs; `netlists_equivalent` / `graphs_equivalent` are bool shortcuts.
    """)
    return


if __name__ == "__main__":
    app.run()
