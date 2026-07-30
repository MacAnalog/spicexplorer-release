# spicexplorer-api

The **FastAPI REST + SSE adapter** over the SpiceXplorer optimizer and SPICE kernel — the
single HTTP contract the Next.js "Studio" front-end is built against. It is a **thin
adapter: no business logic.** Every route loads a `Project_Setup`, drives the
`spicexplorer` optimizer (or a `spicexplorer-core` probe / a leaf tool), shapes the result,
and returns it; the science lives one layer down. Its OpenAPI is the source of truth the UI
generates its TypeScript types from (`openapi.json` → `openapi-typescript`).

**Layering:** sits at the top of the platform stack — it imports
[`spicexplorer`](../spicexplorer) (optimizer + YAML DSL),
[`spicexplorer-core`](../spicexplorer-core) (SPICE engine, env probe, `project_root`), and
[`spicexplorer-netlist2xschem`](../spicexplorer-netlist2xschem) (netlist → `.sch`). Nothing
imports *it*; it is an edge adapter, peer to the `spicexplorer-mcp` adapter. Import name:
`spicexplorer_api` (distribution `spicexplorer-api`).

## Install

Part of the `spicexplorer-platform` `uv` workspace — `uv sync` installs it editable into the
shared `.venv` with its dependencies. It is **not** a library you import symbols from: both
`spicexplorer_api/__init__.py` and `spicexplorer_api/routes/__init__.py` are empty — the
public surface is the **ASGI app** (`spicexplorer_api.main:app`) and its HTTP routes, not a
Python API.

Declared dependencies (`pyproject.toml`): `spicexplorer[torch]`, `spicexplorer-core`,
`spicexplorer-netlist2xschem`, `fastapi>=0.115`, `uvicorn[standard]>=0.32`,
`python-multipart>=0.0.12`.

> The `[torch]` extra on `spicexplorer` keeps the deployed app's Bode / AC transfer-function
> optimizer working. Dropping it (→ bare `spicexplorer`) makes the api/Docker image
> torch-free — safe only if no project uses the Bode optimizer; the common
> single-objective / constraint optimizers and all scoring are pure numpy.

## Routes surface

`main.py` mounts **15 routers** under the `/api` prefix (one OpenAPI tag each), for **78
routed endpoints**, plus an un-prefixed `GET /health` liveness probe defined in `main.py` —
**79 endpoints total**. Each router is one file under
[`src/spicexplorer_api/routes/`](src/spicexplorer_api/routes/):

| Router (tag) | Endpoints | One-line role |
|---|---|---|
| `config` | 1 | `GET /api/config` — `app_config.json` with repo-relative paths resolved + preset checkpoints. |
| `project` | 5 | Load / validate / generate / parse-to-form a project YAML (`/project/load`, `/yaml-text`, `/project/validate`, `/project/generate`, `/project/parse-to-form`). |
| `score` | 1 | `POST /api/score` — sigmoid-vs-linear score shaping for a project's target specs. |
| `optimize` | 4 | Start / stop a run and stream live progress: `/optimize/start` (ephemeral algorithm/budget/seed/corner overrides + opt-in `keep_raw` per-trial waveform retention), `/optimize/stop/{run_id}`, **SSE** `/optimize/stream/{run_id}`, and `GET /optimize/algorithms` — the selectable algorithms derived from the *installed* Nevergrad (`recommended` curated presets / `families` configurable kwargs-accepting classes / `registry` all 500+ presets), so the UI never hardcodes algorithm names. Guide: [`notebooks/run_launch_api_tour.ipynb`](notebooks/run_launch_api_tour.ipynb). |
| `checkpoint` | 6 | List / load / delete checkpoints + envelope / scatter / report analyses. |
| `schematic` | 1 | `GET /api/schematic` — the project schematic SVG asset. |
| `sanity` | 1 | `POST /api/sanity-check` — pre-flight testbench + single-trial sanity evaluation. |
| `netlist` | 2 | `POST /api/netlist/parse` (inspect `.param`s) + `GET /api/spec-library` (wizard spec library). |
| `xschem` | 5 | Serve / resolve / list xschem `.sch`/`.sym` for the in-browser viewer + `POST /xschem/from-netlist` (→ netlist2xschem) — each generation is recorded as a first-class **`kind: xschem` run** (input provenance + outputs copied into the run's own `artifacts/`; degrades gracefully; P3.1c). |
| `env` | 1 | `GET /api/env` — simulator + PDK availability probe (live-vs-replay degradation). |
| `sensitivity` | 1 | `GET /api/spec/{name}/sensitivity` — finite-difference per-parameter sensitivity sweep. |
| `simulate` | 1 | `POST /api/simulate/once` — evaluate ONE chosen design point through the optimizer's `evaluate(...)`. Sweep lanes on the same call: `sweep_corners: true` runs every enabled PVT corner; `monte_carlo: N` (2..100, `mc_seed0` reproducibility pin, exclusive with `sweep_corners`) clones the active corner into `mc1..mcN` mismatch samples via core `monte_carlo_corners` — artifacts land `run_<n>_<tb>__mc<i>` and feed the Analyze viewer's MC mode. |
| `projects` | 16 | Project registry + per-run lifecycle: list/create/from-example/detail/runs (`?kind=` filter), rename (PATCH), fork, soft-delete, `examples` (**curated by `examples/demos.yaml`** — list order = display order, invalid entries warn-skipped, no file → alphabetical scan; `from-example` also seeds a demo YAML's top-level `assets.xschem` schematics into the new project's `xschem/` tree), `trash` + restore, per-run rename/delete. **Agent context surface (P5c):** `GET /projects/{id}/state` (derived `state.json` rollup — compliance matrix + best-run pointers + cell inventory), `GET /projects/{id}/context` (generated `PROJECT.md` + decision log), `POST /projects/{id}/decisions` (append-only decision event) — the same kernel an MCP server exposes to agents. |
| `library` | 15 | **Reference Library** browser over the optional `examples/analog-db` submodule: `GET /library/status` (availability probe), `/library/catalog` (class-grouped circuits), `/library/circuits/{id}` (datasheet + recorded results + schematic modes), `/library/circuits/{id}/schematic?mode=` (serve a schematic `.svg`), `/library/circuits/{id}/schematic-sources` (everything viewable: generated modes + vendored hand-drawn reference images), `/library/circuits/{id}/reference-image` (serve one reference image), `/library/results` (bulk measured-results map), `/library/classes` (metric registry + per-testbench profiles: repo-derived `ngspice`/`spectre` engine availability, `${...}` binding slots, authored descriptions), `/library/pdks` (the pdk→engine routing matrix from the committed `sim_engine` markers), `/library/testbenches/{class}/{name}/netlist?engine=` (a bench's ngspice deck or composed Spectre view: wiring + analysis templates + SKILL calculator), `/library/templates` (functional sub-circuits, each with its `image` render ref), `/library/templates/{id}/image` (serve a template's PNG render), `/library/templates/{id}/netlist` (a template's committed netlist source), **`POST /library/circuits`** (scaffold a new draft circuit — the Register wizard write path, 409 on conflict / 400 on a bad manifest), and **`POST /library/circuits/{id}/project`** (start a new WORK_ROOT v2 project **seeded from a catalog circuit** — master netlist copied into `design/cells/`, provenance into `topology/selection.json` + the manifest; project-fs P5). Degrades to `503` / `available:false` when the DB is absent. |

| `waveview` | 21 | **Universal result viewer** over [`spicexplorer-waveview`](../spicexplorer-waveview): open any ngspice `.raw` / Spectre psfascii raw dir by whitelisted path (`POST /waveview/open`) or by optimizer run (`GET /waveview/runs[/{run_id}/artifacts]`, `POST /waveview/open_run` — `merge: true` combines a run's newest testbench raws into ONE dataset), **fetch ANY run artifact by identity** (`GET /waveview/runs/{run_id}/artifacts/file?rel=…` — `run.json`/`config_snapshot.yaml`/logs, traversal-safe, no path whitelist; P3.1b), **on-demand raw retention** (`POST /waveview/runs/{run_id}/prune` — `metrics_only`, idempotent, open datasets evicted), **plot snapshots** (`POST /waveview/runs/{run_id}/snapshot` — client-rendered PNG persisted into the run's `snapshots/`, served back via `…/artifacts/file?rel=` — the thumbnail path), **run a netlist** (`POST /waveview/run_netlist` — a self-contained deck becomes a first-class `kind: netlist` run under `work/runs/`, ngspice batch-runs it and the newest raw auto-opens; 422 keeps the failed run for log triage), **browser uploads** (`POST /waveview/upload` staged under `work/waveview_uploads/` + `GET /waveview/uploads` inventory + `DELETE /waveview/uploads/{id}`, TTL-swept), dataset lifecycle, downsampled wave data, Tier-1 `{meas:…}` evaluation, op-point scalars, parsed simulator logs + **SSE** `/waveview/log/stream` live tail, `/waveview/browse`, and the measurement catalog. Path posture: `REPO_ROOT`/`WORK_ROOT` + `SPICEXPLORER_WAVEVIEW_ROOTS` opt-in. End-to-end usage guide: meta [`doc/guide_analyze_view.md`](../../../doc/guide_analyze_view.md). |

> The **canonical endpoint table** (all rows, request/response shapes, the UI's `lib/api.ts`
> mapping) lives in the **UI repo's README** and is not duplicated here to avoid drift — see
> [`../../../spicexplorer-ui/README.md`](../../../spicexplorer-ui/README.md) (§ *API Reference*).

## Service layer

Routes stay thin by delegating to the service modules under
[`src/spicexplorer_api/services/`](src/spicexplorer_api/services/):

| Module | Role |
|---|---|
| `optimizer_runner.py` | Background **live-run + SSE bridge** and **replay** (see below). |
| `library_db.py` | Read-only adapter over the **optional** `spicexplorer-analog-db` submodule (lazy import + `availability()` degradation); locates + parses the committed catalog / results / class + template registries for the `library` routes. |
| `env_probe.py` | Thin shim over `spicexplorer_core.env` adding the optional `app_config.pdk_root` override; backs `GET /api/env`. |
| `project_service.py` | Project encapsulation + per-run isolation bookkeeping; owns the **owner-aware stale-run reconciler**, the project/run/trash lifecycle, and the canonical **run-envelope seam** (`begin_run`/`finalize_run` for one-shot run kinds + `project_for_yaml` reverse resolver). Run resolution is id-addressed: `find_run_dir` is O(1) via `dir == run_id` (legacy run.json scan fallback) and `resolve_run_file` maps `(run_id, rel)` → a traversal-safe absolute file (P3.1b). FS logic builds on the storage kernel (`spicexplorer_core.workspace`). |
| `index_db.py` | **Derived SQLite index over WORK_ROOT** (plan_project_filesystem P2): indexed twins of the project/run listers (same shape + order), rebuilt at API startup, content-freshened by write-through at the API's own mutation points, existence-probed per read so out-of-band FS changes self-heal, and degrading to the FS scan on any DB error. Single-writer contract: only the API process writes it (agents/kernel are FS-only). `$SPICEXPLORER_INDEX_DB` overrides the `WORK_ROOT/index.db` location; rebuild CLI: `python -m spicexplorer_api.services.index_db`. |
| `waveview_service.py` | Path-whitelisted adapter over `spicexplorer-waveview` (dataset load/measure/plot + sim-log tail) for the `/api/waveview/*` routes. |
| `checkpoint_reader.py` | Read + normalize checkpoint data from JSON (`OptimizationLog`) and CSV trace files (uses `.iterrows()` so dotted columns like `point.score` survive). Multi-corner–aware: envelope/scatter resolve `"<corner>::<spec>"` keys back to the corner-independent spec. The JSON reader emits a `per_metric_present` key-presence mask (dropped by the `CheckpointData` response model) so scatter feasibility **skips** a corner not simulated for a trial (one added on resume) yet still **fails** a corner that ran but returned NaN at every spec; a bare-vs-namespaced axis pair is realigned onto a shared corner so a mixed-era log still renders points. |
| `score_service.py` | Compute sigmoid-vs-linear score penalties for a project's target specs. |
| `yaml_generator.py` | Convert the Setup-wizard form payload into a `project_setup.yaml` string. |
| `netlist_parser.py` | Lightweight extractor for `.param name=val` lines from a SPICE netlist. |
| `num.py` | Small numeric helpers (`safe_float`) shared across services. |

## Run

From the `spicexplorer-platform` checkout:

```bash
LOG_LEVEL=INFO uv run uvicorn spicexplorer_api.main:app --reload --port 8000
```

Dump the OpenAPI **offline** (no server; feeds the UI's TypeScript codegen):

```bash
uv run python -c "import json; from spicexplorer_api.main import app; print(json.dumps(app.openapi()))"
```

For the full Docker / native lanes and running the API **with** the UI, see the
`spicexplorer-platform` [`CLAUDE.md`](../../CLAUDE.md) (REST API + Docker sections).

## Operational contracts (confirmed in code)

- **PDK-aware env degradation** — `services/env_probe.py` → `GET /api/env` returns
  `{ngspice_path, ngspice_ok, pdk_root, pdk_ok, pdk_detail, tech, live_runs_enabled}`
  (`EnvResponse` in `routes/env.py`). When `pdk_ok` / `live_runs_enabled` is false the UI
  shows the replay-only pill and disables live Start; score shaping, compare/explore on cached
  checkpoints, and the wizard all still work. PVT design + degradation rationale:
  [`../../doc/PVT_plan.md`](../../doc/PVT_plan.md).
- **CORS** — `main.py` uses `allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?"`
  (`allow_credentials=True`, all methods/headers), so any `localhost:<port>` dev origin is
  accepted. Do **not** replace it with a static origin list.
- **SSE optimizer-runner bridge** — `services/optimizer_runner.py` runs the optimizer in a
  daemon `threading.Thread`; a `_StreamingOpt` subclass pushes one event per trial (and a
  `checkpoint` event per autosave) onto an `asyncio.Queue` via `run_coroutine_threadsafe`.
  `GET /api/optimize/stream/{run_id}` drains that queue into a `text/event-stream`
  `StreamingResponse`, emitting `{"heartbeat": true}` every 60 s of idle and `{"done": true}`
  on the `None` sentinel. **Replay mode** (`_run_replay`) drip-feeds checkpoint CSV/JSON rows
  as the same event shape at ~50 ms each, so a PDK-less host can still animate a finished run.
  Each run is self-contained under `WORK_ROOT` (config snapshot, `run.log`, replayable
  `events.ndjson`, `checkpoints/`, `sim/`); overrides (algorithm/budget/seed/active PVT
  corner) are applied **in-memory** — the YAML on disk is never rewritten.
- **Stale-run reconciler** — on startup the FastAPI `lifespan` calls
  `project_service.reconcile_stale_runs()`, which scans `run.json` files under the projects,
  runs, and trash roots and flips any left `status: running` (a crashed/killed backend) to
  `error`, so the run list is honest after a restart.
- **Library / analog-db is an OPTIONAL dependency** — `spicexplorer-analog-db` was extracted
  to its own repo and is **not** a `uv` workspace member (root `pyproject.toml`), so it is not
  installed by a plain `uv sync` and the api **must not** import it at module load.
  `services/library_db.py` imports it **lazily** and reports presence via `availability()`;
  `GET /api/library/status` always answers (`available:false` with a `reason` when absent) and
  every other library route returns **`503`**, never a `500` — the same degradation contract as the
  PDK probe. To serve real data, install the submodule into the env
  (`uv pip install --no-deps -e examples/analog-db && uv pip install jsonschema` — analog-db
  imports `jsonschema` at import time and it is not in `uv.lock`, so the second step is required;
  the dev venv and the Docker api images `Dockerfile.api.{dev,prod}` already do both). PDK keys are the
  analog-db-native long names (`ihp-sg13g2`/`sky130`/`gf180mcu`); the UI maps them to its short
  display keys.

## Notebooks

Two, both **server-free** tours via FastAPI's `TestClient` (no uvicorn), committed executed:

- [`notebooks/library_api_tour.ipynb`](notebooks/library_api_tour.ipynb) — the `/api/library/*`
  Reference Library routes: catalog → circuit detail → bulk results → class registry →
  templates → the schematic SVG (rendered inline) → the graceful-degradation contract (needs
  the `examples/analog-db` submodule installed — see the Library contract below). The
  end-to-end feature guide is the meta-repo's
  [`doc/guide_library_catalog.md`](../../../doc/guide_library_catalog.md).
- [`notebooks/run_launch_api_tour.ipynb`](notebooks/run_launch_api_tour.ipynb) — the run-launch
  surface: `GET /optimize/algorithms` (recommended/families/registry semantics + the
  preset-kwargs guards), the `examples/demos.yaml` curated demo registry (+ `assets.xschem`
  schematic seeding on `from-example`), and the `POST /simulate/once {monte_carlo}` launch
  shape (mechanism: the core `monte_carlo_corners` notebook).

The rest of the api surface stays notebook-free by design (it is an HTTP edge adapter): the
optimizer's worked notebooks live under `examples/OTA/...` (see
[`../spicexplorer/README.md`](../spicexplorer/README.md)) and the kernel's `core_quickstart.ipynb`
is referenced from [`../spicexplorer-core/README.md`](../spicexplorer-core/README.md).

## Tests

The [`tests/`](tests/) suite (route contracts, project/run lifecycle, the PVT
wizard round-trip, checkpoint/name edges, audit regressions, the waveview routes/runs,
the Reference Library catalog/datasheet/degradation contract). The fast lane runs with
no SPICE:

```bash
uv run pytest packages/spicexplorer-api/tests -v
```
