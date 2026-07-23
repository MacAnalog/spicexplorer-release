# `_shared/` — analog-DB infrastructure

Cross-circuit infrastructure for the SpiceXplorer analog circuit database (plan
`doc/plan_examples_db.md`). The per-circuit data lives in `../circuits/<id>/`; the typed,
class-aware index is `../catalog.json`. The verify harness + `analog-db` CLI live in the
`spicexplorer-analog-db` package.

> **Status (through Phase 6a):** Phases 0–6a are complete — schema + class library + verifiable
> circuits (41) + reference corpora (ferrosim, sfe_*, 22 `kind: reference`; 63 total) + tri-PDK
> lowering + T0–T2 verify harness + gm/ID LUT extraction (P6) + PPA scoreboard are all live. The DB
> is extracted as the `spicexplorer-analog-db` submodule at `examples/analog-db/` (P4 done). All
> consumers resolve the DB through `spicexplorer_analog_db.paths.db_root()` — one env-overridable
> seam (`$SPICEXPLORER_ANALOG_DB`). **T3 (sim smoke) and T4 (conformance) are both implemented and
> opt-in behind `--sim`** (PDK-gated — off by default so the fast gate stays PDK-free); T3 also runs
> in the slow pytest suite (nightly). See `catalog.json` / the live scoreboard for the current
> per-kind counts.

## Layout

| Path | What |
|---|---|
| `schema/*.schema.json` | JSON Schemas (draft 2020-12) — the **agent contract** (D-7). `circuit`, `datasheet`, `analysis`, `sizing`, `class`, `params`. |
| `classes/<class>/metrics.yaml` | Per-class canonical metric vocabulary + owned template set (D-10). |
| `classes/<class>/datasheet-defaults.yaml` | Class datasheet defaults a circuit inherits. |
| `classes/<class>/testbench-templates/*.spice` | Class-owned parameterized templates (D-4). |
| `testbench-templates/*.spice` | **Universal** templates (`dc_op`, `noise`, `tran_step`). |
| `spec-library.yaml` | Relocated reusable target-spec templates (see *Relocation* below). |
| `optimizer/nevergrad_reference_*.yaml` | Relocated optimizer registry references. |
| `PARAMS.md` | DUT parameterization (`spicexplorer/params@1`): atomic per-instance inventory (`x_dut_<instance>_<field>`) + declarative default tying (`abstract/params.yaml`; meta `plan_parameterization.md`). The **contract**; for a worked example (how the atomic symbols, ties, `sizing.yaml` free-symbol keying, and the `** params:` deck banner fit together) see [`PDK_SIM.md`](PDK_SIM.md) *§ Parameterization*. |
| `MIGRATION.md` | Loss-less migration audit of `examples/OTA/*` (plan §3b, follow-up #4). |
| `TEST_COUPLING.md` | The platform test-suite repoint worklist (plan §3c). |
| `CACE_FORMAT.md` | cace_format 5.2 ↔ super-DSL field mapping (resolves O-1). |
| `XSCHEM_NETLIST.md` | The Docker `xschem -n` command for `.sch → .spice` (D-11). |
| `engines/spectre/analyses.yaml` | **Spectre analysis-config template DB** (engine-level, NDA-clean): statement templates (`ac`, `dc_op`, `dc_sweep`, `noise`, `tran`, `pss`, `stb`) with `{NAME}` placeholders + `[ optional ]` segments; the platform's closed lane composes benches from it (`spicexplorer.backends.spectre_templates`, built-in fallback when absent). Statement NAMES are load-bearing (the PSF key contract). |
| `engines/spectre/calculator.yaml` | **SKILL calculator expression table** — named OCEAN `result` + one-line SKILL expressions (AC gains, PSS harmonic distortion/IIP3, native stb margins) the platform renders into its headless OCEAN metrics runner; live-parity'd against the Python registry on the same raw dirs (2026-07-10). |
| `classes/<class>/spectre-benches.yaml` | Per-testbench Spectre wiring: which analysis templates each bench composes + which calculator rows read its results (`$NAME` args pull from bench params + platform-computed extras like `RAIL`/`IIP3_*`). |
| `pdk/<pdk>.yaml` | PDK registry: corner-lib catalog, device-class map, supply/geometry, **`passives`** (R/C corner libs + measured sheet-res/cap-density), **`gmid`** (LUT-extraction defaults). |
| `PDK_SIM.md` | Simulating the DB circuits across the three PDKs (the EDA base image, the cross-PDK transfer + test matrix, the passive R/C corner libs) **and how a circuit's knobs are named + shared** (the atomic `x_dut_*` inventory, tie lowering, the `** params:` banner — worked on `amp_001_5t`; contract in [`PARAMS.md`](PARAMS.md)). |
| `GMID.md` | gm/ID LUT characterization (Phase 6): the `gmid-extract` deck generator, the pygmid `.pkl` format, the committed demo LUTs. |
| `MEASUREMENT_PITFALLS.md` | **When a bench measures the wrong thing.** The recurring failure mode where a level test alone passes a circuit that is not operating (railed output, dead loop, cut-off pair) and the *activity criterion* that fixes it — worked through the amplifier ICMR and LDO dropout cases, plus the analog-db-vs-optimizer lane split that lets the two report different numbers for the same deck. Read before authoring a new testbench template. |
| `SCOREBOARD.md` | The PPA scoreboard: recording design points (`run --write`), baselines + the Pareto-marked `scoreboard.json`, the class `ppa:` declarations, accession ids (`new-circuit`). |
| `references/analoggym/` | Snapshots of AnalogGym amplifiers **not** imported into the DB (missing upstream netlist; 2-stage `Pin_2` corpus). See the README there. |
| `gmid/<pdk>/<device>__<corner>.pkl` | GENERATED — committed gm/ID lookup tables (`analog-db gmid-extract`); read by `pygmid.Lookup`. |
| `gmid/<pdk>/<device>__<corner>.manifest.json` | Typed registration sidecar for each LUT (run dimensions, model lines, provenance). |

## GENERATED vs AUTHORED (the drift rule)

Two kinds of file live in each circuit. **AUTHORED** files are the human source of truth;
**GENERATED** files are derived and carry a header naming their source + regen command. The
verify harness re-runs the generator and diffs the committed file — a stale commit fails CI
(plan O-2; the Tier-1 drift guard lands in Phase 1, but P0 already asserts up-to-dateness).

| File | Kind | Source / regen |
|---|---|---|
| `circuits/<id>/abstract/netlist.spice` | AUTHORED | hand-written, PDK-neutral (`nmos`/`pmos`) |
| `circuits/<id>/circuit.yaml`, `datasheet.yaml`, `analyses/*`, `pdk/*/{devices.map,sizing,corners}.yaml` | AUTHORED | hand-written |
| `circuits/<id>/abstract/topology.cgraph.json` | GENERATED | `analog-db generate` (circuitgraph) |
| `circuits/<id>/pdk/<pdk>/netlist.spice` | GENERATED | `analog-db generate` (lowering) |
| `raw/<class>/<id>/<pdk>/<testbench>.spice` | GENERATED | `analog-db export-raw` (ready-to-run decks; byte-drift-guarded) |
| `catalog.json` | GENERATED | `analog-db catalog --write` (carries the `raw`/`schematic` index) |

## Commands

```bash
analog-db verify                 # T0 schema · T1 generation · T2 assembly (PDK-free); T3/T4 skip unless --sim
analog-db verify --tier 3 --tier 4 --sim   # T3 sim-smoke + T4 conformance (needs ngspice + $PDK_ROOT)
analog-db verify --tier 2        # one tier; --circuit / --pdk to narrow
analog-db generate               # rewrite the GENERATED netlists/cgraph/project_setup
analog-db generate --all         # …then the raw/ decks + catalog.json (full regen, in order)
analog-db export-raw [--check]   # materialize ready-to-run raw/ decks (--check = drift guard, no writes)
analog-db catalog --write        # rebuild catalog.json (incl. the raw/schematic index)
# PDK-gated (the EDA image has ngspice + all three PDKs; --docker pipes from the host):
analog-db run --circuit amp_001_5t --pdk ihp-sg13g2 --docker --crosscheck --write
#   runs every declared analysis, records a scoreboard entry (scoreboard/<pdk>/<design_id>.json), and checks the
#   netlist2tf symbolic prediction (at the MEASURED .op gm/ro) against the sim extract (D-5)
```

## Relocation (loss-less, plan §3b)

`spec-library.yaml` and `optimizer/nevergrad_reference_*.yaml` are **copies** of the files
still at the `examples/` root. The originals are **not** removed yet: `spec-library.yaml` has a
live runtime consumer (`spicexplorer_api/routes/netlist.py`) and the nevergrad refs are
documentation. Per the loss-less rule, nothing is deleted until consumers repoint — that
repoint happens in Phase 3 (tests) / Phase 8 (the API route). See `MIGRATION.md`.
