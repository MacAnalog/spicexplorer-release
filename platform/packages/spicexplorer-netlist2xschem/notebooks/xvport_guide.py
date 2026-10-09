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
    # `xvport` — porting xschem drawings ⇄ Virtuoso cellviews

    This guide walks the **xvport** pipeline (the `spicexplorer_netlist2xschem.virtuoso_export`
    subpackage): port **actual xschem `.sch`/`.sym` drawings** — coordinates, wires, symbol
    graphics — to Cadence Virtuoso cellviews and back. No netlist in the loop, no placement
    synthesis: the files already carry the geometry; the tool transforms and replays it.

    Everything in this notebook runs **offline** (no Cadence, no bridge): the forward emitter
    produces a deterministic, self-contained SKILL `.il` artifact; only the optional *load*
    step (`--run`) talks to a live CIW daemon through `virtuoso-bridge-lite`. The live
    transcripts at the end are recorded from IC23.1/FOUNDRY_KIT runs (2026-07-16).

    Reference: the package `README.md` (§ *Virtuoso porting*).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Forward: `.sch` → schematic cellview

    Parse → **geometric net extraction** (union-find over wire segments, T-junctions, labels
    and ports folded by name, device pins located via transformed `.sym` pin boxes) → device
    map → `.il`. Two connectivity modes: `labels` (net-label stubs at every terminal — immune
    to xschem↔kit pin-geometry mismatch) and `wires` (the drawing's wires verbatim, pre-split
    at every electrical node, one label per connected island, geometric pin patching).
    `wires` is the DEFAULT: a `labels` cellview netlists correctly and draws no wiring, which
    no check here can see and only a person opening the cellview can, so it warns once per run
    and is opt-in (#267).
    """)
    return


@app.cell
def _(mo):
    from pathlib import Path

    from spicexplorer_netlist2xschem.sch_parser import parse_sch
    from spicexplorer_netlist2xschem.virtuoso_export import (
        emit_schematic_il,
        extract_nets,
        load_device_map,
    )
    from spicexplorer_netlist2xschem.virtuoso_export.symlib import symlib_for_source

    FIX = (mo.notebook_dir() / "../tests/fixtures/xvport").resolve()
    src = FIX / "transmission_gate_pair.sch"
    sch = parse_sch(src.read_text())
    symlib = symlib_for_source(src)

    nx = extract_nets(sch, symlib)
    print("pin -> net (the extractor's electrical partition):")
    for (inst, pin), pn in sorted(nx.pin_nets.items()):
        print(f"  {inst}.{pin:>2} -> {pn.net}")
    print("ports:", sorted(p.name for p in nx.ports))
    return (
        FIX,
        Path,
        emit_schematic_il,
        extract_nets,
        load_device_map,
        nx,
        parse_sch,
        sch,
        symlib,
        symlib_for_source,
    )


@app.cell
def _(emit_schematic_il, load_device_map, sch, symlib):
    devmap = load_device_map()
    r = emit_schematic_il(sch, lib="MYLIB", cell="tgate", devmap=devmap, symlib=symlib)
    print("\n".join(r.il.splitlines()[:12]), "\n...")
    print("\ninstances:", r.instances)
    print("expected bindings:", len(r.expected_bindings), "| ports:", list(r.expected_ports))
    return (devmap,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The device map — where sizing fidelity lives

    One YAML table drives both directions (`xvport dump-map` prints it). The FOUNDRY_KIT facts
    are live-verified: CDF names are literally `w`/`l`/`fingers` (`w` is **per-finger**;
    callbacks derive `wf = w × fingers`), and the spectre netlister's `propMapping` is
    `m←simM, nf←fingers, w←wf` — so the xschem multiplier maps to **`simM`** (writing CDF `m`
    is a silent no-op) and IHP's **TOTAL** xschem `w` is divided by `ng` via the rule's
    `per_finger` option before it reaches the per-finger CDF `w`.
    """)
    return


@app.cell
def _(FIX, devmap, emit_schematic_il, parse_sch, symlib_for_source):
    rule = devmap.lookup("sg13g2_pr/sg13_lv_nmos.sym")
    print("master:", (rule.lib, rule.cell))
    print("params:", rule.params)
    print("per_finger:", rule.per_finger)
    print("reverse symref:", rule.symref)

    fingered = parse_sch((FIX / "mos_fingered.sch").read_text())
    rf = emit_schematic_il(
        fingered,
        lib="MYLIB",
        cell="fingered",
        devmap=devmap,
        symlib=symlib_for_source(FIX / "mos_fingered.sch"),
    )
    print("\nxschem w=2u ng=2 m=3 becomes:")
    print("  " + next(ln.strip() for ln in rf.il.splitlines() if 'xvSetParams(cv "M1"' in ln))
    print("warnings:", [w for w in rf.warnings if "per-finger" in w])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. End-to-end checks — the independent oracles (`--netcheck` / `--simcheck`)

    After a `--run`, two default-on checks execute (`endcheck.py`); neither reuses xvport's
    own net extractor:

    * **netcheck** — netlist the SOURCE with headless `xschem -n` and the BUILT cellview with
      Virtuoso's own netlister (spectre dialect via the bridge), then prove **circuitgraph
      graph equivalence**: a labeled bipartite-graph isomorphism over device type + MOS
      polarity + pin wiring (names/sizing ignored, supply rails anchored).
    * **simcheck** — wrap the exported cellview netlist in a smoke deck (operator
      `--sim-models`/`--sim-section`; every interface net tied to ground through 1 GΩ;
      `--sim-param name=val` for symbolic placeholders) and solve a DC operating point
      through Spectre.

    The two fixtures below are REAL oracle outputs: verbatim `xschem -n` of the source, and
    the design section of a live `createNetlist` export of the ported cellview (the export's
    kit-path model includes are STRIPPED — foundry NDA data never lands in the repo).
    """)
    return


@app.cell
def _(FIX):
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import netlists_graph_equivalent

    cmp = netlists_graph_equivalent(
        FIX / "tgate_source_netlist.spice", FIX / "tgate_cellview_netlist.txt"
    )
    print("equivalent:", cmp.equivalent)
    print("reason:", cmp.reason)
    print("component mapping:", cmp.component_mapping)
    return (netlists_graph_equivalent,)


@app.cell
def _(FIX, Path, netlists_graph_equivalent):
    # the oracle is not a rubber stamp: move one gate onto a rail and it fails
    import tempfile

    tampered = (
        (FIX / "tgate_cellview_netlist.txt")
        .read_text()
        .replace("(port_A vctl port_B VSS)", "(port_A VSS port_B VSS)")
    )
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write(tampered)
    bad = netlists_graph_equivalent(FIX / "tgate_source_netlist.spice", Path(fh.name))
    print("tampered equivalent:", bad.equivalent, "|", bad.reason)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Reverse: cellview → `.sch`/`.sym` (`cv2sch` / `cv2sym`)

    The bridge's readers don't expose wire geometry or symbol drawing shapes, so the reverse
    direction runs two SKILL dumps (in this package, via `execute_skill` — the bridge
    submodule stays pristine) and inverts every forward transform: the 8-orient table,
    scale + y-negation, and the param tables (`simM`→`m`, per-finger `w × fingers` → total).

    **NDA rule, enforced:** a cellview in a `kit_libs` library is never dumped — the guard
    raises *before any client call*. Kit-master *instances* inside a user schematic map back
    to xschem symrefs through the device table (each rule's `symref`).
    """)
    return


@app.cell
def _(load_device_map):
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import XvportNDAError, cv2sym

    try:
        cv2sym(None, "FOUNDRY_KIT", "nmos_lvt", load_device_map())  # client=None: never reached
    except XvportNDAError as exc:
        print("REFUSED:", exc)
    return


@app.cell
def _(devmap, extract_nets, nx, parse_sch, symlib):
    # offline reverse demo: a synthetic schematic dump -> .sch text -> re-extracts to the
    # SAME electrical partition the forward extractor produced in section 1
    from spicexplorer_netlist2xschem.virtuoso_export.reverse import (
        DumpInstance,
        SchDump,
        emit_sch_text,
    )
    from spicexplorer_netlist2xschem.virtuoso_export.xform import to_cadence

    cad = to_cadence
    dump = SchDump(
        labels=[
            (*cad(590, -240), "vctl"),
            (*cad(590, -580), "vctl_not"),
            (*cad(560, -280), "port_A"),
            (*cad(620, -280), "port_B"),
            (*cad(560, -540), "port_A"),
            (*cad(620, -540), "port_B"),
            (*cad(590, -280), "VSS"),
            (*cad(590, -540), "VDD"),
        ],
        pins=[
            ("port_A", "input", *cad(380, -400)),
            ("port_B", "input", *cad(740, -400)),
            ("vctl", "input", *cad(520, -180)),
            ("vctl_not", "input", *cad(410, -620)),
            ("VDD", "input", *cad(590, -460)),
            ("VSS", "input", *cad(590, -340)),
        ],
        instances=[
            DumpInstance(
                "M1",
                "FOUNDRY_KIT",
                "nmos_lvt",
                *cad(590, -260),
                "R90",
                {"w": "150n", "l": "130n", "simM": "1", "fingers": "1"},
            ),
            DumpInstance(
                "M2",
                "FOUNDRY_KIT",
                "pmos_lvt",
                *cad(590, -560),
                "MYR90",
                {"w": "150n", "l": "130n", "simM": "1", "fingers": "1"},
            ),
        ],
    )
    text, warnings = emit_sch_text(dump, devmap, lib="xvport_dev")
    print("\n".join(ln for ln in text.splitlines() if ln.startswith("C {sg13")))

    back = extract_nets(parse_sch(text), symlib)
    print(
        "\nre-extracted partition matches section 1:",
        {k: pn.net for k, pn in back.pin_nets.items()}
        == {k: pn.net for k, pn in nx.pin_nets.items()},
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The live flow (recorded 2026-07-16, IC23.1 / FOUNDRY_KIT, CIW daemon)

    Forward, hierarchy, both checks on by default:

    ```text
    $ xvport sch2cv ccia-02/rrl-switched-capa-integrator.sch --lib xvport_dev --cell rrl_wires \
        --with-symbols --mode wires --port 65192 --run --verify \
        --sim-param gm_val=1m --sim-param rout_val=10M ...
    xvport: loaded 9 cellview build(s) into xvport_dev
    xvport: sch xvport_dev/rrl_wires: verify OK: 80 terminal bindings match
    xvport: netcheck xvport_dev/rrl_wires: netcheck OK: equivalent: matched 19 components and 24 nets ...
    xvport: simcheck xvport_dev/rrl_wires: simcheck OK: spectre dc operating point solved
    ```

    Reverse + full round-trip (Cadence → xschem → Cadence, re-ported in `--mode wires` —
    reverse output is wire-accurate by construction):

    ```text
    $ xvport cv2sch xvport_dev tgate_e2e --port 65192 -o rev/tgate_e2e.sch --verify
    xvport: reverse verify OK: equivalent: matched 2 components and 6 nets ...
    $ xvport sch2cv rev/tgate_e2e.sch --lib xvport_dev --cell tgate_rt --mode wires --run --verify
    xvport: sch xvport_dev/tgate_rt: verify OK: 8 terminal bindings match
    xvport: netcheck xvport_dev/tgate_rt: netcheck OK: equivalent ...
    $ xvport cv2sym FOUNDRY_KIT nmos_lvt --port 65192          # kit master
    xvport: REFUSED — ... 'FOUNDRY_KIT' is in the kit_libs NDA denylist ...
    ```

    Operational gotchas: `--sim-env ~/.virtuoso-bridge/local.env` pins the local Spectre
    profile (bridge `.env` discovery can silently pick a remote-SSH one); `--prefix xv_`
    renames locally-created cells when an xschem basename collides with a kit cell.
    """)
    return


if __name__ == "__main__":
    app.run()
