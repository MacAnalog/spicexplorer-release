> **[REFERENCE]** — the concrete WORK_ROOT v2 on-disk layout + lifecycle scenarios for
> `spicexplorer_core.workspace`. Living; kept current with the kernel. Canonical design +
> locked decisions (D-1…D-11) live in the meta-repo `doc/plan_project_filesystem.md` — this
> doc shows what the code actually writes; that doc says *why*.

# WORK_ROOT v2 — filesystem layout & lifecycle

`spicexplorer_core.workspace` is the storage kernel: the single contract for *what lives
where under `WORK_ROOT`*, shared by the FastAPI `project_service` and orchestration agents
so every process speaks one data model. `WORK_ROOT` is `$WORK_ROOT` (the Docker backend
sets it to `/work`) else `<repo>/work`.

The **filesystem is canonical**. `index.db`, `state.json`, `PROJECT.md` are all *derived* —
delete any of them and a rebuild heals. `project.yaml` never moves (moving it re-anchors a
relative `ws_root`, D-2). Runs are immutable at terminal status — only trashed, never edited.

## Storage classes

Every path belongs to one of three classes:

| Mark | Class | Rule |
|---|---|---|
| ◆ | **design state** | mutable, curated — the source you/an agent edit; snapshotted on promote |
| ▸ | **run** | append-only; frozen once terminal; only trashed, never edited |
| · | **derived cache** | disposable, rebuildable — safe to delete, regenerates on demand |

## Master tree — `WORK_ROOT/`

```
WORK_ROOT/
├── index.db                          ·  derived SQLite index (rebuildable, API-single-writer)   [P2]
├── projects/
│   └── <slug>-<id8>/                    e.g. folded-cascode-0a1b2c3d
│       ├── manifest.json             ◆  IDENTITY (schema v2: id, name, rev, default_job, default_pdk)
│       ├── project.yaml              ◆  default optimize job — STAYS at root (D-2)
│       ├── spec/                     ◆  scaffolded
│       │   └── targets.yaml          ◆  canonical spec target VALUES            (on demand)   [P4]
│       ├── verify/                   ◆  (on demand)
│       │   └── plan.yaml             ◆  spec × test × corner joining table                    [P4]
│       ├── topology/                 ◆  scaffolded (catalog provenance)
│       ├── design/                   ◆  scaffolded
│       │   ├── cells/<cell>/         ◆    netlist.spice (MASTER) · cell.sch/.sym (derived) · sizing.yaml
│       │   │   ├── annotations.yaml  ◆    curated, structural-anchored           [P4 / D-6]
│       │   │   ├── bindings/<pdk>.yaml  ◆ per-cell PDK bindings
│       │   │   └── .imported_from.json  ▸ present if imported from shared/lib    [P5]
│       │   └── history/              ◆  promotion snapshots                       [P4]
│       │       ├── current.json      ◆    atomic pointer → the accepted snapshot
│       │       └── <ts>-<µs>-<hex4>/ ▸    immutable snapshot (sortable id)
│       ├── testbenches/  jobs/  layout/     ◆ scaffolded
│       ├── runs/                     ▸  scaffolded — EVERY execution, any kind    [P3]
│       │   └── <ts>_<kind>_<hex8>/   ▸    dir name IS the run_id
│       ├── analyses/<kind>/<key>/    ·  scaffolded — disposable composite-keyed caches
│       ├── context/                  ◆  scaffolded                               [P5 / D-10]
│       │   ├── decisions.ndjson      ▸    append-only agent/human decision log
│       │   └── PROJECT.md            ·    GENERATED from decisions + state (never hand-edited)
│       ├── state.json                ·  derived rollup: compliance matrix + best runs   [P4] (on demand)
│       ├── .objects/<sha256>         ▸  per-project content store for run-input blobs    [P3 / D-7]
│       └── spice/  xschem/  scratch/    v1 compat dirs (kept; project.yaml netlists resolve here)
├── shared/                              cross-project (never inside a project)
│   ├── gmid-luts/<pdk>/              ·  scaffolded
│   ├── xschem-cache/                 ·  scaffolded
│   └── lib/<cell>/<version>/         ◆  publish-on-promote user library          [P5 / D-9]
├── runs/                             ▸  v1 unscoped runs (legacy, kept)
├── auto_save/                           v1 legacy autosave (kept)
└── .trash/                              soft-delete bin (move-based, recoverable)
```

`scaffold_project` creates the ◆/▸/· dirs marked *scaffolded*; `verify/`, `state.json`,
`.objects/`, `spec/targets.yaml`, and the `history/` snapshots appear *on demand* as the
matching feature is used.

## Identity & run records

```
manifest.json  ◆   {id, slug, name, created, updated, source, schema_version:2,
                    rev,                 # monotonic write counter — optimistic-concurrency seam
                    default_job:"project.yaml", default_pdk}

run.json       ▸   {run_id, project_id, label, status, started, ended,
                    kind,                # optimize | simulate | sweep | xschem | tf | gmid | …
                    owner:{pid, hostname, start_token, started},   # owner-liveness reconcile
                    retention:"full|metrics_only|none",
                    inputs:{netlist:{sha256, path}},               # → .objects/<sha256>
                    coordinates:{cell, corner, temp, …},           # matrix coords (P4)
                    metrics:{spec:value}, best_score,
                    retention_pruned:{tier, at, freed_bytes}}      # after GC (P3.1)
```

---

## Scenario 1 — Fresh project (`scaffold_project`)

Structure + identity only; no runs, no `state.json`, no `.objects/`, no `verify/`.

```
projects/folded-cascode-0a1b2c3d/
├── manifest.json          ◆ {id, name, rev:1, default_job:"project.yaml"}
├── project.yaml           ◆
├── spec/ topology/ design/{cells,history}/ testbenches/ jobs/ runs/ analyses/ layout/
├── context/
│   ├── decisions.ndjson   ▸ (empty)
│   └── PROJECT.md         · (stub)
└── spice/ xschem/ scratch/
```

## Scenario 2 — An optimizer run lands  `[P3 + P3.1]`

One run = one `runs/<run_id>/` dir. Its thousands of trial candidates are **rows in
`events.ndjson`, not directories**; the only per-trial dirs are the heavy per-corner
waveforms under `sim/`.

```
runs/20260715-100000_optimize_a1b2c3d4/      ▸ dir == run_id  ({ts}_{kind}_{hex8})
├── run.json           ▸ kind:optimize · owner{…} · retention:metrics_only · inputs · coordinates · metrics
├── events.ndjson      ▸ {"iter":1,…}{"iter":2,…}   ← the "candidates table" (iter_candidates reads it)
├── .heartbeat         ▸ liveness (owner-liveness reconcile keys off this)
├── run.log            ▸
├── config_snapshot.yaml  ▸ absolute ws_root — reproduces the run
├── checkpoints/       ▸ auto_1.json …
└── sim/               ▸ HEAVY waveforms
    ├── run_1_tb_ac__tt/  out.raw
    └── run_2_tb_ac__ss/  out.raw

.objects/67c229d9…     ▸ the exact netlist bytes run.json's hash points to (dereferences forever)
```

## Scenario 3 — Retention / GC  `[P3.1a]` — same run at three tiers

`prune_run` enforces the run's `retention` tier (terminal-only, idempotent, age-gated).

```
full  (elected/promoted)   metrics_only  (default)        none  (throwaway)
─────────────────────      ─────────────────────────      ────────────────────
run.json         ▸         run.json         ▸ +marker     run.json  ▸ +marker
events.ndjson    ▸         events.ndjson    ▸  (kept)     ─ everything else gone ─
checkpoints/     ▸         checkpoints/     ▸  (kept)
config_snapshot  ▸         config_snapshot  ▸  (kept)
sim/  *.raw      ▸         sim/  ✗ DROPPED   (freed 12 KB)
```

`run.json` gains `retention_pruned:{tier, at, freed_bytes}` so re-running is a no-op. A
symlink resolving outside the run dir is never counted or deleted.

## Scenario 4 — Runs are multi-kind  `[P3 + P3.1c]`

A manual sim and an xschem generation are first-class runs alongside optimize — same
envelope, `?kind=` filterable, artifacts fetchable by identity.

```
runs/
├── 20260715-100000_optimize_a1b2c3d4/   ▸ kind:optimize
├── 20260715-101500_simulate_b2c3d4e5/   ▸ kind:simulate   ├─ run.json  └─ sim/ out.raw
└── 20260715-102000_xschem_c3d4e5f6/     ▸ kind:xschem      [P3.1c]
    ├── run.json          ▸ inputs:{netlist:{sha256}} · coordinates:{pdk, name}
    └── artifacts/folded-cascode.sch     ▸ self-contained

# id-based serving [P3.1b] — no path whitelist, traversal-safe:
GET /waveview/runs/<run_id>/artifacts/file?rel=run.json
GET /waveview/runs/<run_id>/artifacts/file?rel=artifacts/folded-cascode.sch
```

## Scenario 5 — Verification → `state.json`  `[P4]`

`verify/plan.yaml` (the matrix) × run history (metrics + coordinates) → a derived,
rebuildable compliance rollup an agent reads instead of globbing.

```
verify/plan.yaml   ◆              runs/*/run.json                →  state.json  ·  (derived)
─────────────────                ────────────────                   ──────────────────────────
specs:                           r_tt  {dcgain:44} corner:tt        compliance:
  gain_db:                       r_ss  {dcgain:41} corner:ss          gain_db:{value:39,  ← min over corners
    measurement: dcgain          r_ff  {dcgain:39} corner:ff                  pass:false, target:">=40",
    corners:[tt,ss,ff]                                                        by_corner:{tt:44,ss:41,ff:39}}
    aggregate: min               best_runs.overall → r_tt          best_runs:{overall:"…_a1b2",
    target: ">= 40"              (election rule STATED)                       election_rule:"max best_score…"}
```

Target *values* stay canonical in `spec/targets.yaml` (D-5: reference ids, never copy).

## Scenario 6 — Promotion  `[P4]` (accept a design, immutably)

Old snapshots are immutable; `current.json` swaps atomically under a per-project `fcntl`
lock held across the whole read-promote-write.

```
BEFORE 2nd promote                       AFTER 2nd promote
design/history/                          design/history/
├── current.json → …-ab12  ◆             ├── current.json → …-cd34   ◆  (atomic swap)
└── <ts>-…-ab12/  ▸  sizing "W:10u"       ├── <ts>-…-ab12/  ▸  sizing "W:10u"   ← still frozen
    ├── promotion.json                    └── <ts>-…-cd34/  ▸  sizing "W:20u"   (new current)
    └── cells/ota/sizing.yaml
# live design/cells/ota/sizing.yaml keeps iterating (10u → 20u) independently of frozen history
```

## Scenario 7 — Shared library  `[P5]` (reuse across projects)

Publish-on-promote → **copy**-on-import (not a live reference). Versions immutable; import
refuses to clobber a local cell unless `overwrite=True`.

```
project A (source)              shared/lib/               project B (importer)
design/cells/ota/       ──►     ota/v1/          ──►      design/cells/input_stage/
  netlist.spice  ◆                netlist.spice  ◆          netlist.spice   ◆  (copied)
  sizing.yaml    ◆                sizing.yaml    ◆          sizing.yaml     ◆  (copied)
  annotations.yaml                lib_meta.json  ▸          .imported_from.json  ▸ {cell:ota, version:v1}
# publish_cell(A,"ota","v1")     (immutable, staged      # import_cell("ota","v1",B,as_name="input_stage")
#                                 atomically)             # refuses if input_stage exists w/o overwrite=True
```

## Scenario 8 — Agent context  `[P5 / D-10]`

Agents **append events**; they never edit the rendered doc. `PROJECT.md` regenerates from
the log + `state.json`.

```
context/decisions.ndjson   ▸ (append-only, O_APPEND)     context/PROJECT.md   ·  (GENERATED)
─────────────────────────                                ─────────────────────────────────────
{"at":…,"by":"agent","summary":"folded cascode…"}        # Folded-Cascode OTA
{"at":…,"by":"human","summary":"accepted 44 dB…"}        > GENERATED — do not hand-edit
                                                         ## Compliance  ❌ gain_db=39 (>=40)
   append_decision(…)  ─────────────────────────────►    ## Best run  …_a1b2  (max best_score…)
                          render_project_md()             ## Recent decisions  · accepted 44 dB…

# Over HTTP:  GET /projects/{id}/state · GET /projects/{id}/context · POST /projects/{id}/decisions
#             (GETs are side-effect-free — they derive without writing)
```

## Scenario 9 — Soft-delete / restore (move-based)

```
delete  →  projects/<id>/      ──move──►  .trash/<id>-<ts>/   (+ .trashmeta.json written FIRST)
restore →  .trash/<id>-<ts>/   ──move──►  projects/<id>/      (v1 projects migrate lazily on restore)
```

---

## CLIs

```bash
python -m spicexplorer_core.workspace [--work-root PATH] [--dry-run]              # additive v1→v2 migrate
python -m spicexplorer_core.workspace.retention [--older-than-days N] [--dry-run] # retention GC sweep
```

See the runnable tours: [`../notebooks/workspace_quickstart.ipynb`](../notebooks/workspace_quickstart.ipynb)
(scaffold → manifest → run envelope) and
[`../notebooks/project_lifecycle.ipynb`](../notebooks/project_lifecycle.ipynb)
(retention → verify → state → promote → annotations → library → context).
