# Running the analog-db test cases

This package has two kinds of test, plus the `analog-db verify` harness. All of it depends on the
platform packages (`spicexplorer-core`, `spicexplorer-circuitgraph`, `spicexplorer-netlist2tf`),
which are NOT on PyPI — so you run from a **spicexplorer-platform checkout** and borrow its venv.

## 0. One-time setup (borrow the platform venv)

```bash
cd spicexplorer-platform
uv sync                                   # build the platform venv
uv pip install jsonschema                 # the one extra runtime dep
uv pip install --no-deps -e examples/analog-db   # install this package editable
```

> ⚠️ **Do not use `uv run` for analog-db.** `uv run` re-syncs the env to `uv.lock` and *uninstalls*
> the two lines above (analog-db left the workspace at Phase 4). Always invoke the venv directly:
> `.venv/bin/python -m pytest …` and `.venv/bin/analog-db …` (or activate the venv).

## 1. Fast tests (PDK-free, no Docker) — every change

Three markers split the suite by what a test's cost scales with:

- **(no marker) — unit**: the package code (loaders, assembler, CLI, params/gmid plumbing) on a
  couple of representative circuits. Seconds; the everyday dev loop.
- **`corpus`**: corpus-wide sweeps and per-binding parametrized checks that scale with the number
  of circuits (verify tiers, raw drift, structural detection, metric-route/sizing integrity). Each
  expensive sweep (full render, tier runs) is computed ONCE per session in `tests/conftest.py`
  and shared — never call `verify.run_tier*()`/`export.generate_all()` directly from a new
  corpus-asserting test; consume the session fixtures.
- **`slow`**: live ngspice/PDK simulation or the xschem round-trip — opt-in, unchanged (§3).

```bash
.venv/bin/python -m pytest examples/analog-db/tests -m "not slow" -q                # unit + corpus — the CI / release gate
.venv/bin/python -m pytest examples/analog-db/tests -m "not slow and not corpus" -q # unit only — seconds, every edit
```

Covers: schema + cross-ref (Tier 0), generation drift (Tier 1), assembly (Tier 2), the optimizer
projection / NEWCAS gate, the AnalogGym import, the netlist2tf symbolic plumbing, reference-circuit
Tier-0, authoring (`scaffold_circuit`), and gm/ID LUT plumbing — all without ngspice or a PDK.
(YAML reads are memoized per file mtime via `spicexplorer_analog_db.yamlio` — the corpus is read
far more often than it changes; that cache is what keeps the corpus sweeps in seconds.)

## 2. The verify harness (the same tiers, as a CLI)

```bash
.venv/bin/analog-db verify                       # T0–T2 (PDK-free); T3/T4 skip unless --sim
.venv/bin/analog-db verify --tier 0 --circuit amp_001_5t
.venv/bin/analog-db verify --tier 3 --tier 4 --sim   # T3 sim-smoke + T4 conformance (needs ngspice + $PDK_ROOT)
.venv/bin/analog-db verify --json                # machine-readable matrix report
```
`--sim` is the flag that turns the PDK-gated Tier-3/Tier-4 opt-in skips into real pass/skip
results — run it on a host with ngspice + `$PDK_ROOT` (the EDA base image / api container).

## 3. Slow / simulation tests (Docker + PDK) — the sim pyramid

Requires Docker and the EDA base image (ngspice + all three PDKs):

```bash
cd spicexplorer-platform
docker compose --profile base build spice-base   # build once (cached after)
.venv/bin/python -m pytest examples/analog-db/tests -m slow -q
```
The slow suite (`tests/test_slow_sim.py`) is the bottom-to-top pyramid:
`L0 syntax → L1 feature → L1b PDK-swap → L1c symbolic-vs-sim crosscheck → T3 raw sweep → L2 spicelib wrapper → L3 project_setup`.
L0/L1/L1b/L1c/T3 drive ngspice via one long-lived base-image container, started once per test
session (`docker run -d`) and reused via `docker exec` per deck — much cheaper than a fresh
`docker run --rm` per call, which used to dominate the T3 sweep's wall clock (no running compose
service needed either way; falls back to a per-call `docker run` if the container can't start).
**L2/L3 need a
running api container** (`docker compose up -d api`) and skip cleanly without it. The **gf180mcu**
tier (`test_L0_gf180_netlist_parses` + `test_L1_gf180_simulates`) skips until the base image is
rebuilt with the gf180 PDK (`docker compose --profile base build spice-base`); it covers the third
PDK for cross-PDK benchmarking.

The **T3 raw sweep** (`test_T3_every_raw_deck_runs_and_extracts_or_floors`) runs *every committed
`raw/` deck* through ngspice — the comprehensive "does each ready-to-run deck actually run?" gate.
Two-level contract: the deck must **load + resolve its PDK libs** (hard fail otherwise), and its
**metrics must extract** (finite measures) — a baseline whose default sizing doesn't bias into a
working circuit (no convergence, W out of the model bin, no finite measure) is a **recorded floor**
that *skips* rather than fails, but its SPICE run is still exercised. Run just this tier with
`-k T3_every_raw_deck`; the curated `test_L1_committed_raw_deck_simulates` adds strong gain
assertions on the known-good amp_001_5t baselines (so a regression there fails, not skips).

The **schematic round-trip** (`tests/test_slow_sch_roundtrip.py`) is a separate slow gate that is
**xschem-gated, not ngspice/PDK-gated**: it re-netlists *every committed `raw/` schematic* — the plain
`<id>.sch`, the `<id>_annotated.sch` overlay, and the `_block_placement_strategies/<id>/*.sch` variants
— with `xschem -n` and asserts the result is the **same circuit** as its `ihp-sg13g2` source via
`circuitgraph.compare_netlists` (labeled bipartite-graph **isomorphism** — structural, not name/text).
It catches any place where place→wire→map or a block overlay silently dropped/added/mis-wired a device,
which the byte-drift guard can't see. Needs xschem (3.4.8+) on PATH with the IHP symbols resolvable (a
host EDA setup or the base image) and skips cleanly otherwise. The hierarchical `hier/` view re-netlists
to subckt instances that need flattening first — covered for a sample in `spicexplorer-netlist2xschem`'s
`test_hierarchy_round_trips_via_xschem`.

Run sims directly (outside pytest):
```bash
.venv/bin/analog-db run --circuit amp_003_fan_smc --pdk sky130 --docker-image --write
.venv/bin/analog-db run --circuit amp_001_5t --pdk ihp-sg13g2 --docker-image --crosscheck
```
`--docker-image` = a fresh `docker run` of the base image (all three PDKs); `--docker` = a running api
service. See `_shared/PDK_SIM.md` for the tri-PDK setup + the sky130 `scale=1u` (bare-µm) convention.
`--write` records the run as a **scoreboard design point** (`scoreboard/<pdk>/<design_id>.json`,
upserting per corner) — see `_shared/SCOREBOARD.md`; afterwards `analog-db generate --all` refreshes
the derived `catalog.json` + `scoreboard.json`.

## 4. In the api container (L2/L3, or the whole suite)

```bash
docker compose up -d api
docker compose exec api uv run pytest examples/analog-db -m slow   # mounted at examples/analog-db
```
(See the Docker note in `_shared/PDK_SIM.md` — the api image rebuild against a new base can be
flaky; the base-image runner path above avoids needing the api image for L0–L1c.)

## 5. Regenerating committed artifacts (the extractor / generators)

GENERATED files are committed so a clone is ready-to-run; regenerate them after editing an
AUTHORED source (`abstract/netlist.spice`, `circuit.yaml`, `datasheet.yaml`, sizing):

```bash
.venv/bin/analog-db generate --all               # cgraph.json + pdk/*/netlist.spice + project_setup + raw/ + catalog.json
# …or the individual generators:
.venv/bin/analog-db generate                     # cgraph.json + pdk/*/netlist.spice + project_setup.yaml
.venv/bin/analog-db export-raw                    # raw/<class>/<circuit>/<pdk>/<testbench>.spice ready-to-run decks
.venv/bin/analog-db export-raw --check            # drift guard: stale/missing/orphan decks (no writes)
.venv/bin/analog-db catalog --write              # catalog.json (incl. the raw/schematic blocks)
.venv/bin/analog-db import-analoggym --src <path-to-external-AnalogGym-checkout>/AnalogGym/Amplifier
# (the AnalogGym submodule was removed from the platform in Dev #12; use an external checkout or
#  $IIC_JKU_GMID_DIR-style env var; the meta-repo snapshot is at external/AnalogGym-remainder)
.venv/bin/analog-db add-binding --circuit amp_003_fan_smc --pdk ihp-sg13g2   # cross-PDK transfer (then `generate`)
.venv/bin/analog-db verify --tier 0 --tier 1     # confirm no drift (catalog⇄raw cross-ref + raw byte-drift)
```
`add-binding` synthesizes a target PDK binding (devices.map + corners + unit-converted sizing) so a
clone is ready-to-run on each of the three PDKs; see `_shared/PDK_SIM.md` "Cross-PDK transfer". The
slow `L1b` tier (`test_L1b_pdk_transfer_simulates`, plus the `L1b-gf180` tier) then sim-verifies the
AnalogGym amps across the PDKs (full matrix + caveats in `_shared/PDK_SIM.md`).
Tier 1 is the drift guard: it fails if a committed GENERATED file differs from a fresh regen.

## 6. CI (GitHub Actions)

Two workflows in `.github/workflows/` (both need the `PLATFORM_TOKEN` secret — a repo-scoped PAT
with read access to the private `spicexplorer-platform`):

| Workflow | When | What | Needs |
|---|---|---|---|
| `verify.yml` | every push / PR + nightly 05:00 UTC (cross-repo canary vs platform `main`) + manual | PDK-free: ruff (**blocking**) + pyright **count-ratchet** (`ci/pyright-baseline.txt` — fails only if the error count grows; lower it as errors get fixed) + Tier 0/1/2 + `pytest -m "not slow"` (incl. the CLI + detection E2E files) + **full-regen determinism** (`generate --all` must reproduce the committed tree byte-identically) + **notebook smoke** (`notebooks/execute_all.py`) | platform checkout |
| `verify-slow.yml` | nightly (06:00 UTC) + manual (`gh workflow run verify-slow.yml`) | **the SPICE tier**: builds `spice-base` (ngspice + IHP + sky130 + gf180mcu, `OSDI_MODE=vendor`, buildx `type=gha` layer cache) then `pytest -m slow` (L0 syntax → L1 sim → L1b PDK-swap → L1b-gf180 → L1c symbolic-vs-sim → **T3 every-raw-deck sweep** → **CLI `run --write` round-trip** vs the committed scoreboard baseline) | platform checkout + Docker |

`verify-slow` is the answer to "does CI run the SPICE tests?" — **yes**, on the nightly/dispatch
cadence (per plan D-13: per-PR stays fast, the sim matrix runs nightly). A failing **scheduled**
run files/updates a `ci-nightly` issue, so nightly breakage is visible without watching the
Actions tab. L2/L3 (spicelib wrapper / project_setup) need a running **api container** and
currently skip there — they light up once the api-image rebuild is fixed (see `_shared/PDK_SIM.md`).
