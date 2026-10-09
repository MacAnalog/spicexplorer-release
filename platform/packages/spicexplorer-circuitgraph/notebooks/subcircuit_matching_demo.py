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
    # Functional sub-circuit detection — current mirrors & differential pairs

    This notebook overlays a catalogue of **pre-defined functional sub-circuits** onto input SPICE
    netlists by **labeled subgraph monomorphism** on the typed bipartite circuit graph.

    Where `compare_*` asks *"are these two whole netlists the same circuit?"*, `find_subcircuits` asks
    *"where does this small functional block appear **inside** a larger netlist?"* — a template's **port**
    nets are free to carry extra devices (just like a tail / load net inside an OTA), but its **internal**
    nets must stay private to the block. That asymmetry is the `match_internal_exact` knob in §5 — on by
    default, it is what keeps a shared internal node from being mis-reported as a clean sub-circuit.

    Some blocks are only meaningful **relative to another**. A differential pair is a real pair only when
    its shared tail is biased by a current source — so its template declares a special `CM_tail` port that
    is admitted only when it lands on a detected current-mirror output. That **dependent-template** layer
    (§6) runs on top of mirror detection.

    Everything here is **pure parsing** — no ngspice or PDK install needed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The template library

    Templates are catalogued in a YAML manifest under
    `examples/analog-db/templates/current_mirror/manifest.yaml`; each has a stable `id` that a match is
    tagged with. The catalogue ships 8 NMOS current sinks + 2 PMOS current sources, netlisted (via
    xschem) from the hand-drawn schematics.
    """)
    return


@app.cell
def _():
    from spicexplorer_circuitgraph import (
        CircuitGraph,
        annotate_subcircuits,
        default_current_mirror_library,
        default_subcircuit_library,
        find_subcircuits,
        group_matches,
    )
    from spicexplorer_core import project_root
    from spicexplorer_core.spice_engine import NetlistView

    lib = default_current_mirror_library()
    print(lib)
    for t in lib:
        print(f"  {t.id:38s} {t.polarity:4s} {t.mirror_class:30s} {t.device_count} devices")
    return (
        CircuitGraph,
        NetlistView,
        annotate_subcircuits,
        default_subcircuit_library,
        find_subcircuits,
        group_matches,
        lib,
        project_root,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Each template is itself a `CircuitGraph` (built lazily from its netlist). The match is **topological**:
    instance names, internal net names, and device sizing are all ignored — only device type, MOS
    polarity, and pin-level wiring matter.
    """)
    return


@app.cell
def _(lib):
    simple = lib.get("cm.nmos.simple")
    g_template = simple.graph
    for c in g_template.get_components():
        print(c.name, c.polarity.value, g_template.connections(c))
    print("ports:", simple.ports)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Detect mirrors in a 5T OTA

    The 5-transistor OTA has two simple mirrors: the **PMOS active load** (a diode + a copy) and the
    **NMOS tail mirror**. `annotate_subcircuits` detects them, resolves them into groups, stores the
    overlay on the graph, and tags each matched device's `structural_role`.
    """)
    return


@app.cell
def _(CircuitGraph, NetlistView, annotate_subcircuits, lib, project_root):
    nl_5t = project_root() / "examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice"
    g_5t = CircuitGraph.from_netlist(NetlistView.from_file(nl_5t), name="amp_001_5t")
    groups = annotate_subcircuits(g_5t, lib)
    for _grp in groups:
        print(
            f"{_grp.group_id:18s} {_grp.mirror_class:8s} {_grp.polarity:4s} "
            f"ref={_grp.reference_device} outputs={list(_grp.output_devices)} ports={_grp.ports}"
        )
    return g_5t, nl_5t


@app.cell
def _(g_5t):
    # the overlay is stored on the graph, and the matched devices are tagged
    print("graph.subcircuit_matches:", [grp.group_id for grp in g_5t.subcircuit_matches])
    print(
        "roles:",
        [(c.name, c.structural_role.value) for c in g_5t.get_components() if c.structural_role],
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. An array of mirrors sharing one reference

    A multi-output mirror — **one diode reference feeding N copies** — is *not* a dedicated template.
    The 2-device simple-mirror template is found once **per copy**, every match reusing the same host
    diode; `group_matches` then collapses them into a single multi-output `MirrorGroup`. The folded-
    cascode OTA has exactly this: a PMOS bias mirror (diode `XM11` → `XM0`, `XM12`) and an NMOS folding
    mirror (diode `XM13` → `XM3`, `XM4`).
    """)
    return


@app.cell
def _(
    CircuitGraph,
    NetlistView,
    find_subcircuits,
    group_matches,
    lib,
    project_root,
):
    nl_folded = (
        project_root() / "examples/analog-db/circuits/amp_004_folded_cascode/abstract/netlist.spice"
    )
    g_folded = CircuitGraph.from_netlist(NetlistView.from_file(nl_folded), name="folded_cascode")

    raw = find_subcircuits(g_folded, lib)
    print(f"{len(raw)} raw embeddings (one per copy, all reusing the shared diode):")
    for m in raw:
        print(f"  {m.template_id:16s} devices={str(list(m.devices)):28s} ref={m.reference_device}")

    print()
    for _grp in group_matches(raw):
        print(
            f"GROUP {_grp.group_id:18s} {_grp.polarity} {_grp.mirror_class:8s} "
            f"ref={_grp.reference_device} outputs={list(_grp.output_devices)}"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Subsumption and alternate labels

    Matched sub-circuits are **not** removed between templates, so a cascode mirror also yields its inner
    simple-mirror match. `group_matches` keeps the most specific (largest) match as the primary and
    records the strictly-smaller one as **subsumed**. Should two templates ever match the *exact same*
    device set, the loser is kept as
    an **alternate** rather than silently dropped. The catalogue's cascode and improved-Wilson are distinct topologies (only the super-Wilson has the feedback edge), so none appears in the run below.
    """)
    return


@app.cell
def _(
    CircuitGraph,
    NetlistView,
    find_subcircuits,
    group_matches,
    lib,
    project_root,
):
    tpl = "examples/analog-db/templates/current_mirror/nmos_current_sink/simulation/cascode_current_mirror.spice"
    g_cascode = CircuitGraph.from_netlist(
        NetlistView.from_file(project_root() / tpl), name="cascode"
    )
    for _grp in group_matches(find_subcircuits(g_cascode, lib)):
        print("PRIMARY  ", _grp.group_id, _grp.mirror_class, "devices=", list(_grp.devices))
        print("  alternates:", [a.template_id for a in _grp.alternates])
        print("  subsumed:  ", [(s.template_id, list(s.devices)) for s in _grp.subsumed])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The match knobs

    - **`match_supply`** (default `True`) — anchor `VDD`/`VSS`/`GND` by name/class; a supply rail only
      ever maps to a rail of the same class, every other net is free. (The "power supplies are special
      nodes" assumption, as a boolean.)
    - **`match_bulk`** (default `False`) — ignore the MOS bulk terminal, so a mirror is found whether its
      bulk ties to the rail or to a separate body net. (The body tie is rarely load-bearing for topology —
      which is also why the serialization *description* views drop it by default; see
      `connections(..., include_body=False)` / `serialize(..., include_body=False)`. The datamodel and the
      round-trip `CircuitGraphDoc` always keep it.)
    - **`match_polarity`** (default `True`) — keep NMOS/PMOS distinct; set `False` for a *provisioned*
      polarity-agnostic search.
    - **`match_internal_exact`** (default `True`) — a template's **internal** nets (neither a declared
      port nor a supply rail) must map to a host net of the **same degree**, so the matched internal node
      carries *no devices beyond the template's*. This is what makes monomorphism safe for detection:
      without it, a cascode whose internal node is shared with unrelated circuitry would be (wrongly)
      reported as a clean cascode. Port and supply nets stay free to fan out. Set `False` for the older,
      looser monomorphism.
    """)
    return


@app.cell
def _(CircuitGraph, NetlistView, find_subcircuits, lib):
    # a mirror whose shared source is a SIGNAL net (not a rail) and whose bulk is a separate body net
    host = """* off-rail mirror
    XM1 iin iin shared body sg13_lv_nmos
    XM2 iout iin shared body sg13_lv_nmos
    .end"""
    g_offrail = CircuitGraph.from_netlist(NetlistView.from_string(host), name="offrail")
    nmos_simple = type(lib)([lib.get("cm.nmos.simple")])  # a one-template library

    print("default (supply anchored):      ", len(find_subcircuits(g_offrail, nmos_simple)))
    print(
        "match_supply=False:             ",
        len(find_subcircuits(g_offrail, nmos_simple, match_supply=False)),
    )
    return (nmos_simple,)


@app.cell
def _(CircuitGraph, NetlistView, find_subcircuits, nmos_simple):
    # polarity-agnostic: the NMOS template matches a PMOS mirror when polarity + supply are relaxed
    pmos = """* pmos mirror
    XM1 iout iin vdd vdd sg13_lv_pmos
    XM2 iin iin vdd vdd sg13_lv_pmos
    .end"""
    gp = CircuitGraph.from_netlist(NetlistView.from_string(pmos), name="pmos")
    print("nmos template, default:           ", len(find_subcircuits(gp, nmos_simple)))
    print(
        "nmos template, polarity-agnostic: ",
        len(find_subcircuits(gp, nmos_simple, match_polarity=False, match_supply=False)),
    )
    return


@app.cell
def _(CircuitGraph, NetlistView, find_subcircuits, lib):
    # match_internal_exact (default True): the cascode's INTERNAL node (n2 — drain of the bottom device,
    # source of the cascode device) is a private node. Tap it with a stray cap and it is no longer a clean
    # cascode — yet loose monomorphism would still report one.
    casc_lib = type(lib)([lib.get("cm.nmos.cascode")])  # one-template library

    clean = """* clean cascode
    XM1 n1 n1 VSS VSS sg13_lv_nmos
    XM2 n2 n1 VSS VSS sg13_lv_nmos
    XM3 iout iin n2 VSS sg13_lv_nmos
    XM4 iin iin n1 VSS sg13_lv_nmos
    .end"""
    tapped = clean.replace(".end", "C1 n2 VSS 10f\n.end")  # extra device on the internal node n2

    gc = CircuitGraph.from_netlist(NetlistView.from_string(clean), name="clean")
    gt = CircuitGraph.from_netlist(NetlistView.from_string(tapped), name="tapped")
    print("clean cascode,        default (exact): ", len(find_subcircuits(gc, casc_lib)))  # 1
    print(
        "tapped internal node, default (exact): ", len(find_subcircuits(gt, casc_lib))
    )  # 0 — rejected
    print(
        "tapped internal node, exact OFF:       ",
        len(find_subcircuits(gt, casc_lib, match_internal_exact=False)),
    )  # 1 — false positive
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Dependent templates — the differential pair and its `CM_tail` anchor

    The full shipped catalogue (`default_subcircuit_library()`) adds a *miscellaneous* family on top of
    the mirrors — including the **differential pair**. A bare pair (two MOS sharing a source) is
    ambiguous: it is only a real input pair when that shared **tail** node is driven by a tail current
    source. We encode that as a **dependency** instead of inflating the template with the current source:
    the pair's template declares a special **`CM_tail`** port, and the matcher admits the pair **only when
    `CM_tail` lands on a net that a current mirror's `out` port also lands on**. So detection runs in two
    layers — mirrors first, then the templates anchored to their outputs.

    In the 5T OTA the tail mirror's output net *is* the pair's tail, so the pair is reported; tie the tail
    straight to the rail instead and the dependency is unmet, so it is not.
    """)
    return


@app.cell
def _(
    CircuitGraph,
    NetlistView,
    annotate_subcircuits,
    default_subcircuit_library,
    find_subcircuits,
    group_matches,
    nl_5t,
):
    full = default_subcircuit_library()  # current mirrors + miscellaneous (differential pairs, …)
    print(full, "→", [t.id for t in full if t.mirror_class == "differential_pair"])

    # the 5T OTA: input pair (XM1/XM2) tail-biased by the NMOS mirror (XM5/XM6, whose output IS `tail`)
    g_5t_full = CircuitGraph.from_netlist(NetlistView.from_file(nl_5t), name="amp_001_5t")
    for _grp in annotate_subcircuits(g_5t_full, full):
        print(
            f"{_grp.family:18s} {_grp.mirror_class:18s} {_grp.polarity:4s} devices={list(_grp.devices)}"
        )
    print(
        "roles:",
        [
            (c.name, c.structural_role.value)
            for c in g_5t_full.get_components()
            if c.structural_role
        ],
    )

    # remove the biasing mirror (tail tied straight to the rail) → the `CM_tail` dependency is unmet
    no_bias = """* 5T OTA core with the tail mirror replaced by a plain rail tie
    XM1 outm vinp tail vss sg13_lv_nmos
    XM2 vout vinn tail vss sg13_lv_nmos
    XM3 outm outm vdd vdd sg13_lv_pmos
    XM4 vout outm vdd vdd sg13_lv_pmos
    RT tail vss 1k
    .end"""
    gn = CircuitGraph.from_netlist(NetlistView.from_string(no_bias), name="no_bias")
    fams = [grp.family for grp in group_matches(find_subcircuits(gn, full))]
    print("\nwithout a tail mirror, families detected:", fams, "(no differential_pair)")
    return (full,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6a. Refining the dependency — `tail_sources` and `match_external_isolated`

    Two knobs sharpen the dependency layer:

    - **`tail_sources`** (declared per dependent template) is an allow-list of the *mirror template ids*
      whose output may legitimately anchor the pair. The shipped NMOS pair lists only NMOS mirrors (an
      NMOS tail is sunk by an NMOS mirror, never sourced by a PMOS one); an empty list accepts any mirror.
    - **`match_external_isolated`** (default **off**) is a stricter port rule: no single device *outside*
      the match may bridge two of its non-supply nets. It is opt-in because an active load *legitimately*
      bridges a differential pair's two output drains — so enabling it rejects the active-loaded pair
      while leaving the (un-bridged) mirrors intact. Use it only for sub-circuits that must be isolated
      except at ports feeding *distinct* external components.
    """)
    return


@app.cell
def _(CircuitGraph, NetlistView, find_subcircuits, full, group_matches, nl_5t):
    # (a) tail_sources — which mirror ids may anchor the pair (the NMOS pair restricts to NMOS mirrors)
    dp = full.get("dp.nmos.simple")
    print("dp.nmos.simple tail_sources:", dp.tail_sources)

    # (b) match_external_isolated (OFF by default): the active load bridges the pair's two drains, so
    #     turning isolation on rejects the otherwise-valid pair while the mirrors survive.
    g2 = CircuitGraph.from_netlist(NetlistView.from_file(nl_5t), name="amp_001_5t")
    strict = group_matches(find_subcircuits(g2, full, match_external_isolated=True))
    loose = group_matches(find_subcircuits(g2, full))
    print("isolation off  → families:", sorted({grp.family for grp in loose}))
    print("isolation on   → families:", sorted({grp.family for grp in strict}), "(pair dropped)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    - `find_subcircuits(host, library=None, …)` → raw `SubcircuitMatch` embeddings (library defaults to
      the full catalogue: mirrors + miscellaneous).
    - `group_matches(matches)` → resolved `MirrorGroup`s (multi-output collapse + subsumption + alternates).
    - `annotate_subcircuits(graph, …)` → does both, stores the overlay on `graph.subcircuit_matches`, and
      tags `structural_role` (`current_mirror` / `cascode_device` / `differential_pair`).
    - **Detection is conservative by default**: `match_internal_exact=True` rejects any embedding whose
      private internal node is shared with the rest of the host, so a reported block is the *real*
      topology, not a look-alike. Relax it with `match_internal_exact=False` only if you want the looser
      monomorphism.
    - **Dependent templates** (a `CM_tail` port) are admitted only when anchored to a detected
      current-mirror output — the differential-pair layer on top of mirror detection. A
      `tail_sources` allow-list narrows *which* mirror ids qualify; `match_external_isolated`
      (opt-in) additionally forbids a single external device from bridging two of a match's ports.
    - Add a template by dropping a netlist + a manifest entry — no code change. A *dependent* one just
      declares the `CM_tail` port.
    """)
    return


if __name__ == "__main__":
    app.run()
