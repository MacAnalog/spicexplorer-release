# spicexplorer-circuitgraph

A leaf tool that turns a SPICE netlist into a **typed bipartite circuit graph** (nets ⟷ components),
serializes it to JSON / textual views for downstream consumption (LLMs, analysis), and round-trips a
graph **back** to a netlist with PDK-specific device names.

- **Import name:** `spicexplorer_circuitgraph`
- **Layer:** tool (leaf). Depends on `spicexplorer-core` **only** — it reads netlists through
  `spicexplorer_core.spice_engine.NetlistView` and never imports a peer tool or raw `spicelib`.
- **No LLM / framework deps.** The graph model, serialization, and emission are fully deterministic.
  LLM role-annotation is a separate, provider-agnostic capability that lives in
  `spicexplorer-orchestration` and merely *consumes* this tool's output.

## Status — deterministic core complete (frozen milestone)

Phases 0–4 are done and the deterministic core is **frozen** at this milestone (further changes are
deferred until the downstream tools are built — see the meta-repo roadmap, `doc/plan_next_steps.md`).
`CircuitGraph.from_netlist` builds a typed bipartite graph (MOS / R / C / L / V / I + linear
controlled sources G = VCCS / E = VCVS + subcircuit
instances) with a configurable skip-and-warn policy, name-based supply detection, a PDK device-name
map (IHP `sg13g2`, Skywater `sky130`, GlobalFoundries `gf180mcu`), and a round-trippable
`CircuitGraphDoc` contract. Cross-PDK retargeting is **voltage-class aware**: each `PdkDevice`
declares a `flavor` (`""` = the core device, `"hv"` = the PDK's thick-oxide/IO part), the source
device's class is read from its own PDK's declaration (`model_flavor`), and a class the target PDK
does not declare is a `ValueError` — never a fall-back onto the core model, which used to land a
3.3 V IHP device on sky130's 1.8 V `nfet_01v8` with no warning. Subcircuit
instances are modeled as black-box components with named, role-tagged ports and can be recursively
expanded (`recurse=True` → `graph.subgraphs`). Serialization is a pluggable strategy set, and
`to_netlist(graph, pdk=…, dialect=…)` emits a re-parseable netlist with per-PDK device names in a
chosen dialect (`spice` default, `spectre`, `hspice`).

**Netlist dialects (2026-07-04, `feat/spectre-hspice-support`):** ingest is dialect-aware for free
— `NetlistView.from_file(path, dialect="auto")` reads Spectre `.scs` and HSPICE decks through the
core dialect readers, and `CircuitGraph.from_netlist` consumes any `NetlistViewLike` unchanged. On
the way out, `to_netlist(dialect="spectre"|"hspice", subckt=…, ports=…)` renders through a
per-dialect emitter family (`SpiceEmitter` is byte-identical to the historical output; the Spectre
emitter handles paren node lists, primitive masters, `subckt…ends`, full identifier
sanitization — leading digits AND punctuation (`ota-5t` → `ota_5t`) — and SPICE
`{expr}` braces → bare Spectre expressions). **Net** names get the stricter, *injective*
`sanitize_net`: each illegal character has its own code (`vin+` → `vin_p`, `vin-` → `vin_m`), because
collapsing them all to `_` shorted every `+`/`-` differential pair — the house port convention
(`.subckt opamp vin- vin+ …`) — onto one node in a deck that still parsed. Emission also enforces a
post-emit invariant: as many distinct nets out as in, or `ValueError` (case-only duplicates are
exempt — SPICE resolves node names case-insensitively, so `VOUT`/`vout` *are* one node).
MOS multiplicity is emitted as `m=` VERBATIM
(`multi` stays a read-side alias only — Spectre silently IGNORES `multi=` on model-card MOS,
proven live on a licensed kit 2026-07-17: `m=4` quadruples id/gm, `multi=4` does nothing).
**Numeric values are resolved, not copied:** SPICE scale factors are case-INsensitive with `M`=milli,
Spectre's are case-sensitive with `M`=mega and no `U`/`P` at all, so the Spectre lane renders every
suffixed token as a plain literal (`w=1U` → `w=1e-06`; passing `1U` through meant *one metre*, `1P`
one farad, `1meg` one milliohm). Suffix-free numbers, symbols and `{expr}` bodies are untouched, and
the `spice`/`hspice` output still carries the source spelling byte-for-byte. Round-trips
are verified by graph isomorphism against
the real AnalogGym sensing-front-end decks — **including hierarchical ones**: a graph built with
`recurse=True` emits a `.subckt`/`subckt…ends` **definition** per referenced master (deduped, nested
masters first) alongside the instance line, so a deck whose DUT lives in a subcircuit re-parses into
an isomorphic graph. A black-box graph (`recurse=False`) has no definition body and emits instance
lines only, as before. Design: meta `doc/plan_spectre_hspice_integration.md`.

**Whole-deck translation (2026-07-05, virtuoso-bridge P2 syntax half):**
`translate_ngspice_to_spectre(netlist, pdk="generic-n65", source_pdk="ihp-sg13g2")` turns an
ngspice testbench deck into composition-ready Spectre blocks (`TranslatedDesign`: DUT
`subckt` blocks, top-level stimulus, numeric-normalized lowercase parameter defaults,
explicit `GND`→0 tie sources; stimulus source values map `dc`/`ac`/`pulse(...)`/`sin(...)` → `vsource dc=`/`mag=`/`type=pulse`/`type=sine`, added with the analog-db bench validation 2026-07-09; the `ac <mag>` marker emits BOTH `mag=` and `pacmag=` so one deck stimulus serves static `ac` AND periodic `pac` analyses (P3-2c; `pacmag` must be ≥0, so a negative marker rides `pacmag=|v| pacphase=180` — CMI-2048, live 2026-07-17); a 0 V source named `VIPRB*` is the loop-probe MARKER and emits as the Spectre `iprobe` primitive — the `stb … probe=` target — with a non-zero/stimulated `VIPRB` rejected rather than silently lost, 2026-07-10) — handling device-model retargeting (the `GENERIC_N65` device
table; names only, no foundry content), parameter-symbol case-folding (spicelib uppercases
`.param` names; Spectre is case-sensitive), and symbolic passive values — both quoted
(`'x_c'`, the ngspice quote-expression twin of `{…}`) and braced; symbolic `.param`
tie/ratio exprs (`{x_a*17/3}`) reach the Spectre parameter namespace as parenthesized
expressions (Spectre rejects braces; keeping them symbolic keeps the tie LIVE under
per-candidate injection — SFE-874). Analyses/corners
are deliberately NOT translated — the optimizer's `spicexplorer.backends.spectre_deck`
composes them (deck contract). Live-validated on licensed-kit Spectre 2026-07-05
(meta `doc/plan_virtuoso_bridge.md` P2).

**Controlled sources (2026-07-16, `feat/circuitgraph-controlled-sources`):** the linear 4-terminal
`G` (VCCS) and `E` (VCVS) cards — `G1 n+ n- nc+ nc- value` — build as 4-pin `VccsNode`/`VcvsNode`
(pins `P`/`N`/`CP`/`CN`), so analog-db's behavioral macromodel blocks (e.g.
`ideal-amp-fully-diff`'s `Gm … GM`) flow through graph → lower → verify instead of being silently
dropped. The gain rides in `params["Value"]` **verbatim** (bare symbols like `GM`, eng strings,
`{expr}` braces all survive); trailing `k=v` params (`m=2`) are kept. Emission: the SPICE/HSPICE
emitters render the 4-terminal card back; the Spectre emitter maps to the `vccs gm=…` / `vcvs
gain=…` primitives. Non-linear forms (POLY, `value=`, `table=`, `Laplace=`) degrade to the standard
skip-and-warn — never a mis-pinned node. (spicelib parses G/E as two-node devices with the
controlling pair inside the value token; `device_factory.wired_nets` splits them back out, and the
graph registers control-only nets itself.)

On top of the frozen core, two analysis capabilities build purely on the public graph API:
**comparison** (whole-netlist equivalence via labeled graph isomorphism) and **functional-subcircuit
detection** (overlay pre-defined templates — current mirrors and tail-biased differential pairs — via
labeled subgraph monomorphism, with per-family YAML template catalogues under
`examples/analog-db/templates/`).

*Deferred (not part of the frozen core):* the matplotlib `[viz]` helpers, and surface adapters
(MCP / REST / UI). Plan + task tracker live in the meta-repo
`doc/plan_circuitgraph_langgraph_integration.md` and `doc/todo_circuitgraph.md`.

## Install

```bash
uv sync   # base: networkx + pydantic  (a [viz] matplotlib extra will arrive with the viz helpers)
```

## Quickstart

> **Runnable demo:** [`examples/OTA/cascode/circuitgraph/circuitgraph_demo.ipynb`](../../examples/OTA/cascode/circuitgraph/circuitgraph_demo.ipynb)
> walks the whole flow (build → inspect → serialize → compare → emit → round-trip → subcircuits) on a
> tiny inline stage and the committed cascode OTA — no ngspice/PDK needed.

Library-first — everything below is pure parsing (no ngspice / PDK install needed). Fixtures live in
`examples/OTA/` and resolve via `spicexplorer_core.project_root()`.

```python
from spicexplorer_core import project_root
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_circuitgraph import (
    CircuitGraph, IHP_SG13G2, SKYWATER_SKY130,
    serialize, list_strategies, evaluate_strategies, to_netlist,
)

# 1. netlist -> typed bipartite graph
nl = project_root() / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
g = CircuitGraph.from_netlist(NetlistView.from_file(nl), pdk=IHP_SG13G2, name="ota")
print(g.component_count, "components,", g.net_count, "nets")

# 2. inspect connectivity (the core primitive: pin -> net, per component)
m = g.get_components()[0]
print(m.name, m.structural_role, g.connections(m))

# 3. serialize for an LLM / analysis (pluggable strategies)
print(list_strategies())                                   # flat, nested, net_centric, llm_description, ...
view = serialize(g, "net_centric", include_params=True)    # -> dict (LLM-ready JSON)
# NDA-safe projection for a cloud LLM: omit the foundry model name (and params) by construction
safe = serialize(g, "net_centric", include_params=False, include_spice_model=False)
for row in evaluate_strategies(g):                          # deterministic comparison harness
    print(row.name, row.token_estimate, row.component_coverage)

# 4. graph -> netlist, optionally retargeting device names to another PDK (#3b)
print(to_netlist(g))                                       # IHP names
print(to_netlist(g, pdk=SKYWATER_SKY130))                  # sky130 nfet/pfet names
print(to_netlist(g, pdk=SKYWATER_SKY130, dialect="spectre",
                 subckt="ota", ports=["vdd", "vss", "vinp", "vinn", "vout"]))
# cross-PDK × cross-dialect: sky130 names, Spectre syntax, wrapped as one subckt definition

# 4b. foreign-dialect ingest works the same way (Spectre/HSPICE via the core dialect readers)
scs = CircuitGraph.from_netlist(NetlistView.from_file("cell.scs"), name="dut")  # auto-detected

# 5. round-trip: the contract is the serialize/deserialize + deep-copy seam
from spicexplorer_circuitgraph import CircuitGraphDoc
doc = CircuitGraphDoc.from_graph(g)                        # pydantic, JSON-dumpable
g2 = doc.to_graph()                                        # independent rebuild
```

### Compare two netlists (are they the same circuit?)

> **Runnable demo:** [`packages/spicexplorer-circuitgraph/notebooks/compare_demo.ipynb`](./notebooks/compare_demo.ipynb)
> walks every knob (name/order invariance, caught differences, passive symmetry, supply rails,
> `match_params`/`match_models`, and differential `IOPort` anchoring) on the real cascode OTA and a
> set of edge cases — no ngspice/PDK needed.

```python
from spicexplorer_circuitgraph import compare_netlists, netlists_equivalent, IOPort

# Builds a graph for each side and tests them for a labeled bipartite-graph ISOMORPHISM:
# equal up to net/instance renaming and line reordering, preserving device type, MOS polarity,
# and pin-level wiring. Accepts netlist text, file paths, NetlistView, or CircuitGraph.
res = compare_netlists(netlist_a, netlist_b, pdk=IHP_SG13G2)
print(bool(res), res.reason)        # truthy when equivalent + a human-readable explanation
print(res.component_mapping)        # on a match: one valid a→b name correspondence
print(res.net_mapping)

netlists_equivalent(netlist_a, netlist_b, pdk=IHP_SG13G2)   # bool shortcut

# Anchor named I/O so they can only map to the matching port (never an internal net):
compare_netlists(netlist_a, netlist_b, pdk=IHP_SG13G2, io_ports=[
    IOPort("vout"),                          # single-ended — maps by identity
    IOPort("vinp", "vinn"),                  # differential — +/- halves swappable (default)
    IOPort("voutp", "voutn", swappable=False),  # differential — polarity preserved
])
# When the two sides use different I/O net names, pass io_ports_b=[...] (matched by position).
```

By default the test is **topological** — it ignores instance/net names, line order, sizing, model
strings, and heuristic roles — with one exception: **supply rails** (`VDD`/`VSS`/`GND`) are anchored
by class, so a rail never maps to a signal net and `R1 vdd vss` is *not* the same as a floating
`R1 n1 n2`. R/C/L terminals are treated as symmetric (a `R1 a b` ≡ `R1 b a` swap is the same
circuit); V/I sources and MOSFET pins stay polar/oriented. Adjust with flags: `match_supply=False`
(pure, fully name-blind topology), `match_params=True` (sizing, eng-normalized so `0.18u == 180n`),
`match_models=True`, `match_structural_role=True`, `match_polarity=False`, `passive_symmetry=False`.
`compare_graphs(g1, g2, …)` is the same on already-built graphs. The comparison is single-level
(subckt instances match as black boxes by name + wiring, not stepped into). **I/O anchoring**
(`io_ports=[IOPort(...)]`) pins named ports — single-ended (map by identity) or differential (the
`+`/`-` pair maps together, swappable by default or `swappable=False` to preserve polarity) — so an
anchored net never maps to an internal one; use `io_ports_b` when the two sides name I/O differently.

### Trace & diff paths between nets

> **Runnable demo:** [`packages/spicexplorer-circuitgraph/notebooks/paths_demo.ipynb`](./notebooks/paths_demo.ipynb)
> traces paths on the real cascode OTA, shows the supply-rail and pin-fan-out behavior, and walks all
> four diff verdicts (plus the JSON / `describe()` output) — no ngspice/PDK needed.

```python
from spicexplorer_circuitgraph import find_paths_between, shortest_paths_between, diff_paths

# Walk the bipartite graph net -> device -> net -> …; each path is a chain of device traversals
# rendered as device.pin touchpoints. Supply rails (VDD/VSS/GND) are NOT routed through by default.
for p in shortest_paths_between(graph, "vinp", "vout"):
    print(p.length, p.label)          # 3  XM1.gate->XM1.source->XM2.source->XM2.drain->XM2C.…
    print(p.touchpoints, p.components)
    print(p.describe())               # prose for an LLM / reviewer
    print(p.model_dump_json())        # JSON (pydantic) — labels/touchpoints included

find_paths_between(graph, "vinp", "vout", max_components=4)                 # all paths, capped length
find_paths_between(graph, "vinp", "vout", through_supply=True)             # allow routing via rails
find_paths_between(graph, "vinp", "vout", max_paths=50)                    # the 50 shortest
find_paths_between(graph, "vinp", "vout", max_components=3, max_paths=None)  # unbounded (small graph)

# diff_paths classifies how two paths differ — pin-only / device-only / device-pin — and splits them
# into what is exclusive to each and what is common.
d = diff_paths(path_a, path_b)
print(d.kind.value, d.summary)        # "device_pin"  "pin-only on XM1; only in B: XM1C, XM2C"
print(d.only_in_a.touchpoints)        # the device.pin label sequence exclusive to A
print(d.only_in_b.touchpoints)        # …exclusive to B
print(d.common.touchpoints)           # …shared
print(d.describe())                   # each step tagged [pin_only] / [device_only]
```

`find_paths_between(graph, a, b)` returns `GraphPath`s (sorted by length then label) connecting two
nets; a path is a sequence of `PathStep` device traversals, each entering on one pin and leaving on
another (a diode-connected device — GATE and DRAIN on one net — fans out into the distinct pin-level
paths). `shortest_only=True` (or `shortest_paths_between`) keeps just the minimal-length paths;
`max_components` caps the hop count; `through_supply=True` allows routing through `VDD`/`VSS`/`GND`
(off by default, since rails connect nearly everything). Net names resolve case-insensitively; an
absent/ambiguous name or identical endpoints raise `ValueError`. The **search itself is bounded** by
`max_paths` (default `DEFAULT_MAX_PATHS = 1000`): enumeration runs shortest-first and stops at the
cap, so the result is the *N shortest* paths and a truncation is logged at `WARNING`. This is not a
cosmetic default — the number of simple paths grows factorially, and the `through_supply=True` call
above did not finish in two minutes when `max_paths` was a post-filter over a complete enumeration.
Pass `max_paths=None` for the unbounded walk on a small graph. `diff_paths(p1, p2)` matches steps
by device (direction-insensitive pin sets) and returns a `PathDiff`: a `DiffKind` verdict
(`IDENTICAL` / `PIN_ONLY` / `DEVICE_ONLY` / `DEVICE_PIN`) plus three `PathSegment`s (`only_in_a`,
`only_in_b`, `common`). Every result is a pydantic model — `model_dump()` for JSON, `describe()` for
text.

The trace is purely topological by default. Pass `respect_mosfet_state=True` to make it
**conduction-aware**: a MOSFET's drain↔source channel is dropped when the device is *off* — i.e.
gate–source shorted (Vgs=0) — so its source–drain channel is never reported as a conduction hop. This
is *channel-only*: the gate/bulk edges stay traversable (the gate is still a signal terminal), so for
a gate–source short — where the gate sits on the source net — a `drain→gate` traversal can remain
(the path is relabeled, not removed); dropping the device outright would be a whole-device scope we
did not adopt. A drain–source-shorted ("killed") device — e.g. a MOS wired as a decoupling cap —
needs no special handling, since its drain and source are already the same net. `gs_short_is_off=True`
(default) is the global enhancement-vs-depletion assumption; set it `False` for depletion /
negative-Vth devices that can still conduct at Vgs=0. The underlying
`MosfetNode.is_gate_source_shorted(graph._G)` / `is_drain_source_shorted(graph._G)` /
`is_diode_connected(graph._G)` detectors are public.

### Subcircuits

```python
# subckt instances graph as black-box components with named, role-tagged ports
tb = project_root() / "examples/OTA/folded_cascode/ihp-sg13g2/spice/cora_testbench_ac.spice"
g = CircuitGraph.from_netlist(NetlistView.from_file(tb), pdk=IHP_SG13G2)
x1 = g._comp_map["X1"]                                      # a SubcktInstanceNode
print(x1.subckt_name, [(p.name, p.role) for p in x1.ports()])

# ...or step in: build a child graph per X… instance (the parent black box stays in place)
g_rec = CircuitGraph.from_netlist(NetlistView.from_file(tb), pdk=IHP_SG13G2, recurse=True)
print(g_rec.subgraphs.keys())

# devices the build could not model at all (on_unknown="skip") stay visible here
print(g.skipped_components)                                 # [] for a fully-typed deck
```

The `XM`/`XR`/`XC`/`XL` prefixes are only a *heuristic* over `X…` instances, so an arity mismatch
means the device is a subcircuit wearing a primitive's prefix, not a device to drop: a 3-terminal
PDK passive like the gf180 Miller nulling resistor `XRZ net_b net1 vdd ppolyf_u_3k` graphs as a
`SubcktInstanceNode` and round-trips (it used to be deleted, re-emitting the amplifier with its `Cc`
but no `RZ`). Whatever genuinely can't be typed (a BJT/diode) is recorded in `skipped_components`,
and `compare_graphs` **refuses to ignore** it — two graphs that dropped different devices are never
reported as the same circuit. When both sides dropped the *same* references the comparison still
runs, and the census rides out on the result: `GraphComparison.skipped_a` / `.skipped_b`,
the `rests_on_skipped` flag, and a caveat named in `reason` — because "equivalent" over two netlists
that each carry an unmodeled clamp diode says nothing about the diodes. `find_subcircuits` logs the
same census once per host it builds internally, since detection over a partial netlist can only
find, or rule out, what was typed.

### Detect functional sub-circuits (current mirrors + differential pairs)

> **Runnable demo:** [`packages/spicexplorer-circuitgraph/notebooks/subcircuit_matching_demo.ipynb`](./notebooks/subcircuit_matching_demo.ipynb)
> overlays the current-mirror template catalogue on the 5T and folded-cascode OTAs, shows the
> array-sharing-a-reference case, subsumption, and the match knobs — no ngspice/PDK needed.

Where `compare_*` asks *"are these two whole netlists the same circuit?"* (graph **isomorphism**),
`find_subcircuits` asks *"where does this small functional sub-circuit appear **inside** a larger
netlist?"* — labeled subgraph **monomorphism** (the host net a template net maps to is free to carry
extra devices, exactly like a tail/load net inside an OTA). Templates are catalogued in per-family YAML
manifests under [`examples/analog-db/templates/`](../../examples/analog-db/templates/) — the
[current-mirror](../../examples/analog-db/templates/current_mirror/manifest.yaml) family (18 templates —
simple / cascode / Wilson / improved-Wilson / high-swing / improved-high-swing / low-voltage / self-biased / wide-swing,
each in nmos + pmos) and the [miscellaneous](../../examples/analog-db/templates/miscellaneous/manifest.yaml)
family (7 — tail-biased differential pairs, cascoded differential pairs, cross-coupled pairs, and a
complementary inverter), plus the [pseudo-resistor](../../examples/analog-db/templates/pseudo_resistor/manifest.yaml)
family (4 — the Guglielmi 2020 Fig-3 series-symmetric two-PMOS cells, `pr.series.*`) and the
[transmission-gate](../../examples/analog-db/templates/transmission_gate/manifest.yaml) family (1 — the
CMOS pass pair `tg.pair.cmos`; its rail-bulk and body-tied drawings are one topology under the
bulk-blind default, so a single canonical template covers both); each has a stable `id` that a match
is tagged with. A **dependent** template (a
differential / cross-coupled pair's `CM_tail` port) is only admitted when its tail lands on a detected
current-mirror output, so the merged catalogue is matched in one pass.

```python
from spicexplorer_circuitgraph import (
    CircuitGraph, default_subcircuit_library,
    find_subcircuits, group_matches, annotate_subcircuits,
)
from spicexplorer_core import project_root
from spicexplorer_core.spice_engine import NetlistView

lib = default_subcircuit_library()                     # 18 CM + 7 misc + 4 pr + 1 tg templates (the default)
nl = project_root() / "examples/analog-db/circuits/amp_004_folded_cascode/abstract/netlist.spice"
g = CircuitGraph.from_netlist(NetlistView.from_file(nl), name="folded_cascode")

# one call: detect + resolve + tag the graph (mutates g in place, returns the resolved groups)
for grp in annotate_subcircuits(g, lib):
    print(grp.group_id, grp.mirror_class, grp.polarity,
          "ref=", grp.reference_device, "outputs=", grp.output_devices)
# cm.pmos.simple#1 simple pmos ref= XM11 outputs= ('XM0', 'XM12')   <- one diode, two copies
# cm.nmos.simple#1 simple nmos ref= XM13 outputs= ('XM3', 'XM4')
print(g.subcircuit_matches)                            # the overlay is stored on the graph
print([(c.name, c.structural_role) for c in g.get_components() if c.structural_role])
```

`find_subcircuits(host, library=None, …)` returns every raw embedding (each is a `SubcircuitMatch`
with `device_map`/`net_map`/`ports`/`reference_device`/`output_devices`); `host` may be a
`CircuitGraph`, `NetlistView`, path, or netlist text, and `library` defaults to the full shipped
catalogue — current mirrors **plus** the miscellaneous family (differential pairs, cross-coupled pairs,
inverter) **plus** the pseudo-resistor and transmission-gate families, merged into one library
(`default_subcircuit_library()`). `group_matches(matches)` resolves them: an **array of mirrors sharing one
diode reference** collapses into a single multi-output `MirrorGroup` (no need for a dedicated N-output
template — the 2-device simple template is found once per copy, all citing the shared reference, and
matched sub-circuits are *not* removed between templates); a match whose device set is a strict subset
of another's (the simple pair inside a cascode) is reported as `subsumed`; and templates that match
the *same* device set are reported as `alternates` rather than silently dropped.
`annotate_subcircuits(graph, …)` runs both, stores the groups on `graph.subcircuit_matches`, and tags
each matched MOS's `structural_role` (in a current mirror: diode-reference device → `MOS_CURRENT_MIRROR_REFERENCE`,
output-copy device → `MOS_CURRENT_MIRROR`, stacked cascode device → `MOS_CASCODE_DEVICE`,
tail source → `MOS_TAIL_CURRENT_SOURCE`; in a tail-biased differential pair: both pair devices →
`MOS_DIFFERENTIAL_PAIR`; in a *family-role* block, every matched MOS carries the family's role:
pseudo-resistor cell → `MOS_PSEUDO_RESISTOR`, transmission gate → `MOS_ANALOG_SWITCH`).

Detection is topological by default with three knobs (the booleans the design called for):
**`match_supply=True`** anchors `VDD`/`VSS`/`GND` by class — a supply rail only ever maps to a rail
of the same name/class, while every other net is free (set `False` for a fully name-blind search);
**`match_bulk=False`** ignores the MOS bulk/body terminal, so a mirror is found whether its bulk ties
to the rail or to a separate body net (set `True` for strict bulk matching); **`match_polarity=True`**
keeps NMOS and PMOS distinct (set `False` for a provisioned polarity-agnostic search). Pass a full
`MatchOptions(...)` via `options=` to override everything at once.

**Per-template bulk matching** — a single template can opt back into bulk matching without flipping
the whole run: the manifest key **`match_bulk: true`** (→ `SubcircuitTemplate.match_bulk`) keeps that
template's MOS bulk edges in the projection, so its drawn bulk wiring becomes part of its identity
(the rail-tied transmission-gate variant vs its body-tied twin; a pseudo-resistor cell's
isolated-well discriminator). One-way: it only *adds* the constraint. When a bulk-strict and a
bulk-blind template land on the *same* host device set, `group_matches` prefers the bulk-strict match
as the primary (the more specific claim) and keeps the bulk-blind twin as an `alternate`.

**Add a template** — drop a netlist next to the others and add an entry to the manifest (`id`,
`class`, `polarity`, `netlist`, `ports`, optional `match_bulk`); it is picked up automatically. Or build a `TemplateLibrary`
from your own manifest (`TemplateLibrary.from_manifest(path)`) or list of `SubcircuitTemplate`s.

**Export to a schematic overlay** — `export_subcircuit_annotations(groups_or_graph)` serialises the
resolved groups to the neutral `spicexplorer/xschem-block-annotations@1` JSON, and
`write_subcircuit_annotations(..., path)` writes it. `spicexplorer-netlist2xschem` consumes that JSON
(`--annotations`) to draw a labelled, coloured box around each detected block — subsumed sub-blocks
nest, alternates appear in the label. The two leaf tools never import each other; the JSON is the only
coupling (so any renderer honouring the schema works). Each block also carries two additive-optional
knowledge pointers (schema still `@1`): **`rules_ref`** — the workspace-root-relative path(s) of the
family's registered design-rule doc(s) (the manifest `rules:` block), so a downstream
symmetry/sizing/layout agent resolves "what do I do with this block" from data — and **`roles`** —
the per-device deterministic `StructuralRole` values the annotation pass assigned (populated when
exporting an *annotated* `CircuitGraph`; empty for a bare group list, where no role pass ran).

```python
from spicexplorer_circuitgraph import (
    find_subcircuits, group_matches, write_subcircuit_annotations,
)
groups = group_matches(find_subcircuits(g))
write_subcircuit_annotations(groups, "folded_cascode.blocks.json")
# then: netlist2xschem <netlist> -o out.sch --annotations folded_cascode.blocks.json --render svg
```

## Notebooks

All pure parsing — no ngspice / PDK needed. Under [`notebooks/`](./notebooks/):

- [`circuitgraph_quickstart.ipynb`](./notebooks/circuitgraph_quickstart.ipynb) — the concise tour (build → inspect → serialize → emit → retarget PDK).
- [`circuitgraph_demo.ipynb`](./notebooks/circuitgraph_demo.ipynb) — the full walkthrough (build → inspect → serialize → compare → emit → round-trip → subcircuits).
- [`compare_demo.ipynb`](./notebooks/compare_demo.ipynb) — every comparison knob (name/order invariance, passive symmetry, supply rails, `match_params`/`match_models`, differential `IOPort` anchoring).
- [`paths_demo.ipynb`](./notebooks/paths_demo.ipynb) — net-to-net path tracing, supply-rail / pin-fan-out behavior, the four `diff_paths` verdicts.
- [`subcircuit_matching_demo.ipynb`](./notebooks/subcircuit_matching_demo.ipynb) — overlay the template catalogue on the 5T and folded-cascode OTAs (array-sharing-a-reference, subsumption, match knobs).
- [`dialect_netlists_demo.ipynb`](./notebooks/dialect_netlists_demo.ipynb) — foreign-dialect netlists end-to-end: read a verbatim Spectre/HSPICE deck → detect structures → re-emit in any dialect (incl. cross-PDK × cross-dialect).

## Public API

Top-level: `CircuitGraph`, `CircuitGraphDoc` (+ `NetModel`/`ComponentModel`/`PortModel`/`CircuitGraphMeta`),
`SubcktInstanceNode`, `SubcktPort`, `SubcktPortRole`, `to_netlist` + the dialect emitter family
(`NetlistDialect` re-export, `NetlistEmitter`/`BaseNetlistEmitter`/`SpiceEmitter`/`SpectreEmitter`/`HspiceEmitter`),
the PDK map
(`Pdk`/`PdkDevice`/`IHP_SG13G2`/`SKYWATER_SKY130`/`GF180MCU`/`ANALOGGYM_REF`/`GENERIC_N65`/`get_pdk`/`mos_flavor` — `ANALOGGYM_REF`
and `GENERIC_N65` are device-**name** maps (the latter is the `translate_ngspice_to_spectre` retarget table), no foundry content;
`PdkDevice` carries a `flavor` (threshold/voltage class, e.g. `"hv"`) and `to_netlist(pdk=…)` retargets each MOS by
`(polarity, flavor)` — the abstract token `nmos`/`nmos_hv` picks the flavor via `mos_flavor`, so ONE DUT can bind two
NMOS/PMOS flavors; an unflavored token keeps the byte-identical core-device behavior), `get_port_spec`, serialization
(`serialize`/`list_strategies`/`get_strategy`/`register`/`unregister`/`Serializer`/`evaluate_strategies`/
`StrategyMetrics`), comparison
(`compare_graphs`/`compare_netlists`/`graphs_equivalent`/`netlists_equivalent`/`GraphComparison`/`IOPort`),
path tracing/diffing
(`find_paths_between`/`shortest_paths_between`/`diff_paths`/`GraphPath`/`PathStep`/`PathDiff`/`PathSegment`/`DiffKind`/`StepDiffKind`),
and functional-subcircuit detection
(`find_subcircuits`/`find_template_matches`/`group_matches`/`annotate_subcircuits`/`SubcircuitMatch`/`MirrorGroup`/`MatchOptions`
+ the template library `TemplateLibrary`/`SubcircuitTemplate`/`default_current_mirror_library`/`default_miscellaneous_library`/`default_pseudo_resistor_library`/`default_transmission_gate_library`/`default_subcircuit_library`
+ the schematic-overlay export `export_subcircuit_annotations`/`write_subcircuit_annotations`/`ANNOTATION_SCHEMA`).
Node/enum types (`MosfetNode`, `VccsNode`, `VcvsNode`, `StructuralRole`, `ParameterType`, …) live under
`spicexplorer_circuitgraph.model.nodes`.

**Add a serialization strategy** — one `@register` class implementing `Serializer.render(graph)`; it's
auto-discovered by `list_strategies()` and `evaluate_strategies()`.

## Downstream

LLM topology role-annotation (writing `structural_role` back onto the graph, building a shared-parameter
design space) is provider-agnostic and lives in **`spicexplorer-orchestration`** (`agents/annotation`),
consuming `serialize(graph, "net_centric")`. See that repo's `agents/README.md`.

## Tests

```bash
uv run pytest packages/spicexplorer-circuitgraph/tests -v
```

Pure-Python and deterministic — no ngspice / PDK install needed (no `slow` markers in this package).
