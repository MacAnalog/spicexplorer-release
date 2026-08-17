# spicexplorer-analog-db

A versioned, tool-agnostic database of analog circuits. **65 verifiable circuits** across
**fifteen classes** (31 OTAs/amplifiers incl. a behavioral macromodel and a composed CMFB
closure, 5 instrumentation amplifiers, 9 LDOs, 3 dedicated CMFB networks — behavioral +
real 5T — 3 switches, 3 temperature sensors, 2 comparators, 2 support blocks, plus
ADC / gain-stage / buffer / diff-pair / sampler / trim / voltage-reference cells) are each
lowered to up to **three open PDKs**
(`ihp-sg13g2`, `sky130`, `gf180mcu`) as ready-to-run SPICE decks, with a tiered `verify` harness.
Every verifiable circuit pairs one PDK-neutral topology (lowered per-PDK via `circuitgraph`) with
class-scoped reusable analyses, a machine-readable datasheet (a `cace_format` 5.2 superset),
agent-discoverable metadata, and a **PPA scoreboard** of recorded design points (see
[Scoreboard](#scoreboard)).

Verifiable circuits carry **accession ids** — `<class-code>_<nnn>_<slug>` (`amp_001_5t`,
`ldo_004_basic_pmos`): citable, append-only numbers allocated by `analog-db new-circuit`, never
renumbered or reused (meta-repo `doc/plan_scoreboard.md` D-1). Pre-accession names live on as
`provenance.aliases`. Reference circuits keep corpus-scoped ids (`ferrosim_*`).

Alongside them are **22 `kind: reference` circuits** (plan D-9) — imported third-party decks in a
proprietary PDK/simulator (the not-yet-promotable remainder of the 30 `ferrosim_*` 28/65 nm
Spectre + 6 `sfe_*` AnalogGym Sensing Front End imports; the promotable members carry accession
ids now, with their original decks retained as in-entry `references` bindings and the exact
blocker documented in each remaining entry's README). They live in the **same `circuits/`
registry** and appear in
`catalog.json`, but are **not lowered or simulated here**: the harness runs a reference-only
Tier-0 (schema + provenance + deck-exists) and skips T1–T4. See [`corpora/ferrosim/`](corpora/ferrosim/)
and [`corpora/analoggym-sensing-fe/`](corpora/analoggym-sensing-fe/) for corpus provenance.

`kind` is **not** how a cell is retired. A verifiable circuit that should stop appearing in the
published benchmark sets **`published: false`** in its `circuit.yaml` — the de-publish marker,
orthogonal to `kind`. It drops out of the generated `scoreboard.json` index and the paper
tabulation, but stays fully lowered, drift-guarded and resolvable, which is what lets a composite
keep composing a retired cell as its core block (`amp_030_miller_cmfb_composite` still composes the
de-published `amp_029_two_stage_miller_comp`).

Works **standalone** as a benchmark and as the `examples/analog-db/` submodule of
[`spicexplorer-platform`](https://github.com/MacAnalog/spicexplorer-platform). Built per the platform
plan `doc/plan_examples_db.md` (in the meta-repo).

## Layout
```
spicexplorer-analog-db/
├─ circuits/<id>/                   # one self-contained circuit  (×65)
│  ├─ circuit.yaml                  #   topology + metadata
│  ├─ composition.yaml              #   COMPOSITES only (×2): instance DAG the flat netlist
│  │                                #   + per-PDK sizing are composed from (plan P4)
│  ├─ datasheet.yaml                #   machine-readable spec
│  ├─ abstract/
│  │  ├─ netlist.spice              #   PDK-neutral topology ((gen) for composites)
│  │  └─ topology.cgraph.json       #   (gen) lowered graph
│  ├─ reference/                    #   original upstream design sources, verbatim, if any: an AnalogGym/
│  │                                #   paper schematic snapshot (<Alias>.png) and/or the design's own
│  │                                #   source tree (LTspice .asc/.asy, xschem .sch/.sym + testbenches)
│  │                                #   with a README.md; provenance only — never consumed by the harness
│  ├─ analyses/*.yaml               #   class testbench bindings
│  ├─ pdk/<pdk>/                    #   one per PDK: ihp-sg13g2 · sky130 · gf180mcu
│  │  ├─ devices.map.yaml
│  │  ├─ sizing.yaml
│  │  ├─ corners.yaml
│  │  └─ netlist.spice              #   (gen) lowered for this PDK
│  ├─ optimizer/projection.yaml     #   optimizer circuits only
│  ├─ project_setup.yaml            #   (gen) from projection.yaml
│  └─ scoreboard/                   #   recorded design points (analog-db run --write)
│     ├─ baselines.yaml             #     the named baseline design point per PDK
│     └─ <pdk>/<design_id>.json     #     one entry per design point: sizing + per-corner
│                                   #     metrics/spec verdicts + PPA rollup
├─ circuits/<id>/                   # a kind: reference circuit (D-9)  (×22: ferrosim_* + sfe_*)
│  ├─ circuit.yaml                  #   kind: reference; class; provenance; references[] bindings
│  ├─ README.md                     #   what it is + upstream source + bindings
│  └─ spectre/<node>/…              #   authored proprietary-PDK decks (dut/tb/runs), layout verbatim
├─ corpora/<name>/                  # corpus-level provenance for reference imports (NOT a deck copy)
│  ├─ PROVENANCE.md                 #   source + license text + import metadata + circuit list
│  └─ upstream-README.md            #   vendored upstream index (byte/SHA manifest)
├─ raw/<circuit>/                   # (gen) ready-to-run decks + schematics
│  ├─ <circuit>.sch                 #   xschem schematic of the DUT topology (one per circuit)
│  ├─ <circuit>_annotated.sch       #   …with detected functional blocks as coloured boxes
│  ├─ <circuit>.structural.json     #   the detection itself (blocks, ports, per-device roles)
│  ├─ hier/<circuit>.sch + blocks/  #   the "block diagram" view (one subcircuit symbol per block)
│  ├─ *.svg                         #   rendered images of the above (analog-db export-raw --svg)
│  └─ <pdk>/
│     ├─ <testbench>.spice          #   self-contained: testbench + params + DUT
│     └─ _dut.spice                 #   standalone DUT for your own testbench
├─ catalog.json                     # (gen) class-aware index — the agent entry point
├─ scoreboard.json                  # (gen) global PPA scoreboard: class × pdk × circuit × design
│                                   #   point, Pareto-marked (see Scoreboard below)
├─ drawings/                        # hand-drawn design families: staging + landing.yaml manifests +
│                                   #   DRAWING_REVIEW.md (see drawings/README.md; edits post-landing happen
│                                   #   in-place at circuits/<id>/pdk/<pdk>/schematic/)
├─ campaigns/<name>/                # reproducible multi-circuit optimization campaigns: generator +
│                                   #   runner + generated configs + the distilled result and report
│                                   #   (per-trial histories are gitignored). See ppa_ihp130/README.md
├─ templates/                       # circuitgraph MATCHER template library (structural signatures, not designs)
├─ _shared/                         # schema, per-class metrics + templates, PDK registries, notes
├─ src/spicexplorer_analog_db/      # the harness + `analog-db` CLI
└─ notebooks/                       # executed Jupyter tours (DB, gm/ID LUT, sizing)
```
`(gen)` artifacts are produced by `analog-db generate` and byte-identical drift-guarded — edit only
the authored files. **To create a new circuit** use `analog-db new-circuit` (the CLI front-end) or
`authoring.scaffold_circuit()` (the Python API it wraps) — both allocate the next accession id and
write the full authored stub tree. A few more details the tree omits:
- Each circuit gets **three schematic views** of its DUT topology, all generated by
  `spicexplorer-netlist2xschem` (pure-Python + deterministic, drift-guarded with the decks) from the
  PDK-neutral abstract netlist + `spicexplorer-circuitgraph`'s block detection:
  - `<circuit>.sch` — the plain topology;
  - `<circuit>_annotated.sch` — the detected functional blocks (current mirrors, differential pairs incl.
    cascoded, cross-coupled pairs, inverters) drawn as labelled, coloured boxes over a block-aware placement;
  - `hier/<circuit>.sch` (+ `hier/blocks/<block>.{sch,sym}`) — the **block-diagram** view: each block is
    lifted into a child subcircuit drawn as one symbol whose pins carry the template's functional names
    (`out`, `ref_in`, `supply`, `in_p`/`in_n`, …); `xschem -n` on the parent re-netlists to the original.
  - `<circuit>.structural.json` — the detection as data: a summary (device count, blocks, per-device
    structural roles) plus each detected group (template, ports, devices).

  They open directly in the SpiceXplorer UI's xschem viewer. **Rendering** them to `.svg` needs xschem,
  so it's a separate optional step: `analog-db export-raw --svg` (run where xschem is on PATH — the base
  image / api container, or a host with xschem **3.4.8+** for per-net colouring; a no-op without xschem).
- `catalog.json` indexes every `raw/` deck and any authored xschem schematic SVGs, per circuit —
  plus, under `schematic.reference`, the original upstream snapshot (`reference/…png`) for imported
  circuits (the AnalogGym amps; `ldo_005_buffered_ref`'s TI-architecture diagram). The handful of
  upstream amps **not** imported (empty/2-stage)
  keep their snapshots under [`_shared/references/analoggym/`](_shared/references/analoggym/README.md).
- Each circuit ships an **atomic parameter inventory + declarative default ties** in
  `abstract/params.yaml` (`spicexplorer/params@1`): every instance owns a mechanically-derived
  `x_dut_<instance>_<field>` symbol (*what CAN vary*) and shipped `groups:`/`ratios:` tag which
  devices size together and why (*what SHOULD vary together*). Ties lower to `.param` lines in the
  committed decks (each deck's `** params:` banner counts free/frozen/tied/ratio knobs), and
  `pdk/<pdk>/sizing.yaml` keys on the free symbols. Contract + `gen-params` regen flow in
  [`_shared/PARAMS.md`](_shared/PARAMS.md); worked example in [`_shared/PDK_SIM.md`](_shared/PDK_SIM.md).
- `_shared/` holds the JSON-Schema agent contract, per-class metric vocab + testbench templates, PDK
  registries, and CACE/xschem/migration notes — see [`_shared/README.md`](_shared/README.md).
- `notebooks/` are executed and PDK-free except marked gated cells — see
  [`notebooks/README.md`](notebooks/README.md).

## Run a circuit
A fresh clone is runnable with no post-processing — every GENERATED artifact is committed.
**To simulate, pull a deck from `raw/`** and run it on a PDK-enabled ngspice (the EDA base image /
api container); each deck header carries the exact `docker run …` command. Decks are corner `tt` by
default — materialize another with `analog-db export-raw --corner ss` (writes `…__ss.spice`).

## Edit → regenerate
Edit any AUTHORED file, then regenerate and drift-check:
```
analog-db generate --all    # netlists/cgraph/project_setup → raw/ decks → catalog.json (in order)
analog-db verify --tier 1   # fails if any committed GENERATED file (incl. raw/) drifted from a fresh regen
```
All GENERATED artifacts (cgraph, lowered netlists, `raw/` decks, `catalog.json`) are byte-identical
drift-guarded; `analog-db export-raw --check` reports stale/missing/orphan decks without writing.

## CLI
```
analog-db verify           [--tier N ...] [--circuit ID] [--pdk PDK] [--sim] [--json]   # T0 schema · T1 generation · T2 assembly (PDK-free); --sim adds T3 sim-smoke + T4 conformance (needs ngspice + $PDK_ROOT)
analog-db generate         [--circuit ID] [--all]                              # rewrite GENERATED artifacts (--all: + raw/ + catalog + scoreboard.json)
analog-db gen-params       (--circuit ID | --all) [--write]                     # generate/refresh abstract/params.yaml (atomic inventory + proposed tying; see _shared/PARAMS.md)
analog-db export-raw       [--circuit ID] [--pdk PDK] [--corner tt[,ss,ff]] [--check] [--svg]   # materialize raw/ decks (+ plain/annotated/hier .sch + structural.json; --svg renders images)
analog-db export-raw-project [--circuit ID] [--pdk PDK] [--out DIR] [--demo]   # emit a raw-targeting project_setup.yaml (optimizer driven off the raw/ decks) into raw_optimize/generated/; --demo writes a Studio demo projection to circuits/<id>/project_setup.yaml instead
analog-db catalog          [--write]                                           # rebuild catalog.json (no --write → stdout)
analog-db scoreboard       [--write]                                           # rebuild the global scoreboard.json (no --write → stdout)
analog-db scoreboard set-baseline --circuit ID --pdk PDK --design HASH          # name a recorded design point the baseline
analog-db new-circuit      --class CLS --slug SLUG --ports p1,p2,… [--pdks …]   # allocate the next accession id + scaffold a draft
analog-db run              --circuit ID --pdk PDK [--corner tt] [--docker [SERVICE]] [--docker-image [IMAGE]] [--crosscheck] [--write]
analog-db add-binding      --circuit ID --pdk PDK [--from PDK]                  # synthesize another PDK binding (cross-PDK transfer)
analog-db gmid-extract     --pdk PDK [--device DEV] [--corner tt|tt,ss,ff|all] [--vgs/--vds/--vsb a,s,b] [--length L1,L2,…] [--width UM] [--temp K]
analog-db gmid-extract-spectre --pdk PDK [--corner tt|all] [--workers N] [--out-root DIR] [--smoke|--dry-run]  # licensed-kit lane (native Spectre, both core flavours in one pass)
analog-db import-analoggym --src <AnalogGym/Amplifier> [--circuit FOLDER]       # (re-)import the AnalogGym corpus
analog-db import-ferrosim  --src <ferrosim/tests> [--no-catalog]                # import the ferrosim corpus as kind: reference circuits (D-9)
```
`run` and `gmid-extract` need a PDK-enabled ngspice: pass `--docker-image IMAGE` (default
`spicexplorer-spice-base:local`) to spin up a fresh EDA base image, or — for `run` — `--docker
[SERVICE]` (default `api`) to use a running compose service. `gmid-extract` also runs
**docker-less** on a host with ngspice + `$PDK_ROOT` (`--runner native`; the default `auto`
picks it up), parallelized one ngspice job per L value via the registry
`gmid.simulator: {runner, workers, timeout_s}` block. `add-binding` converts an existing PDK
binding (`devices.map` + corners + unit-converted sizing) into a new one, then `generate` emits the
lowered netlist. `gmid-extract` writes a pygmid LUT to `_shared/gmid/<pdk>/<device>__<corner>.pkl`.
`gmid-extract-spectre` is the same characterization for a **Spectre-routed licensed kit**:
plain headless Spectre via the virtuoso-bridge env, config from the registry `gmid:`
block (incl. a `simulator: {workers, timeout_s}` parallelization block), LUTs out-of-repo by
default. See [`_shared/PDK_SIM.md`](_shared/PDK_SIM.md) and [`_shared/GMID.md`](_shared/GMID.md).

**`export-raw-project --demo` — the Studio demo lane.** Writes a demo-shaped
`circuits/<id>/project_setup.yaml`: named from the catalog `display_name` + accession id (the
id also seeds the description), `ws_root` pinned to `raw/<id>/<pdk>` so example seeding copies
just the decks, bare-filename netlists, a small optimizer budget (NGOpt·15), and a top-level
`assets.xschem` block listing every committed `.sch`/`.sym` under the circuit dir (the
platform's `from-example` flow copies those into the new project's `xschem/` tree). It
**refuses** a circuit that has `optimizer/projection.yaml` — that circuit's
`project_setup.yaml` is owned by `analog-db generate` (the extends lane). Which demos the
Studio actually lists (and their order) is curated platform-side in `examples/demos.yaml`.

## Scoreboard

Every simulated run recorded with `analog-db run --write` lands on the circuit's **scoreboard**
as a **design point**: the full sizing vector actually simulated (identified by a
formatting-proof content hash, `design_id`), the measured analyses **per corner** (re-running the
same design at another corner upserts into the same entry), the datasheet-mapped canonical
metrics with per-metric `pass`/`fail` spec verdicts, and a **PPA rollup** —

- **Power** — the class's canonical power metric (amplifier `i_supply`, LDO `i_q`) × typical
  VDD, at the worst recorded corner;
- **Performance** — the class's directed headline metrics (declared in
  `_shared/classes/<class>/metrics.yaml` `ppa:`), each at its worst corner;
- **Area** — `active_gate_area_um2` = Σ (w·l·m) over the lowered netlist's MOS devices at that
  sizing (a gate-area proxy — no spacing/routing/wells; ΣC/ΣR are recorded so passives can be
  costed later).

There is deliberately **no scalar "best"** — analog sizing is a tradeoff surface. Instead the
generated `scoreboard.json` marks the **Pareto front** per (circuit, pdk) over
(power, area, headline metrics), and `scoreboard/baselines.yaml` names one entry per PDK the
**baseline** (auto-named on first record; re-point with `analog-db scoreboard set-baseline`).
The catalog carries each circuit's baseline PPA + spec counts, so agents can answer
"the best 5T OTA in gf180 under 1 mW" from `catalog.json` alone. Entries are recorded artifacts
(timestamped, schema-validated at Tier 0, not byte-drift-guarded); `scoreboard.json` is
GENERATED and drift-guarded like `catalog.json`. Usage guide:
[`_shared/SCOREBOARD.md`](_shared/SCOREBOARD.md).

**Note on `active_gate_area_um2`:** it counts MOS gate area only. In the compensated
amplifier corpus capacitors *dominate* silicon — amp_008 is ~5263 µm² of cmim against
236 µm² of gate — so this number understates real area by up to ~20× for those circuits.
`c_total_f`/`r_total_ohm` are recorded alongside so passive area can be costed;
[`campaigns/ppa_ihp130/`](campaigns/ppa_ihp130/README.md) scores capacitor area explicitly.

## Verification tiers (plan §6 / D-13)
| Tier | Checks | Gate |
|---|---|---|
| T0 | schema — metadata well-formed + cross-resolvable | PDK-free, every PR |
| T1 | generation — committed == regenerated; lowered re-parses | PDK-free, every PR |
| T2 | assembly — every circuit × analysis × pdk × corner renders runnable | PDK-free, every PR |
| T3 | sim-smoke — every committed `raw/` deck runs in ngspice | PDK-gated, nightly |
| T4 | conformance — measured vs datasheet + symbolic cross-check | PDK-gated, nightly |

T0–T2 are live in `analog-db verify` (PDK-free, run on every PR). **T3 and T4 are both
implemented and opt-in behind `--sim`** — off by default so the fast gate stays PDK-free; pass
`analog-db verify --tier 3 --tier 4 --sim` on a host with ngspice + `$PDK_ROOT` (the EDA base
image / api container) to turn their skips into real results. Without `--sim` they emit `skip`
rows by design. T3 also runs in the slow pytest suite (`test_slow_sim.py`) against ngspice + the
three PDKs in the platform EDA image. T3 contract: each deck must load and resolve its PDK libs
(hard), and its metrics must extract — a baseline whose default sizing doesn't bias into a working
circuit is a *recorded floor* (skipped, but still simulated). T4 (conformance) simulates each
design and checks the measured metrics against the datasheet `spec` band, emitting real
`conform:<metric>@<pdk>` pass/skip rows (an out-of-spec untuned baseline is recorded as a skip,
not a gate; a circuit reaches `validated` only when every spec-bounded row passes). See
[`TESTING.md`](TESTING.md).

## Development & testing
Depends on the platform packages (`spicexplorer-core`, `-circuitgraph`, `-netlist2tf`), not PyPI —
develop by **borrowing the platform venv**:
```
# from a spicexplorer-platform checkout that has run `uv sync`:
uv pip install jsonschema && uv pip install --no-deps -e examples/analog-db   # --no-deps skips jsonschema, so install it first
.venv/bin/python -m pytest examples/analog-db/tests -m "not slow" -q          # NOT `uv run` (it re-syncs)
```
> The `pytest -m "not slow"` path above needs only `jsonschema`. **Executing the notebooks**
> (`notebooks/execute_all.py`, the CI notebook-smoke step) additionally needs `nbformat` and
> `nbclient` — `uv pip install nbformat nbclient` (the meta-repo's `make sync-db` installs all
> three: `jsonschema nbformat nbclient`).
`db_root()` resolves package-relative, so the harness finds `circuits/` / `_shared/` whether run
standalone or from the submodule mount. Full setup and every test tier (fast / verify / slow-sim /
in-container) are in [`TESTING.md`](TESTING.md).

## License
PolyForm Noncommercial 1.0.0 (see [`LICENSE`](LICENSE)). Derived circuit artifacts carry upstream
provenance — see [`NOTICE`](NOTICE).
