# SpiceXplorer UI

The optional web front-end for the [SpiceXplorer platform](https://github.com/MacAnalog/spicexplorer-platform) circuit-optimization library — the same `project_setup.yaml` and optimization engine you can also drive directly from Python. It is a **Studio workspace** — a persistent VS Code-style shell (activity bar, contextual left rail, tabbed center views, always-on run rail, command palette) — providing a guided project setup wizard, interactive score shaping, live SPICE-backed optimization runs, run history, multi-run exploration, the **Reference Library** browser over the analog-db catalog, and the **Analyze** waveform viewer for any simulation artifact. The bundled cascode OTA on the IHP `ihp-sg13g2` PDK serves as the reference case study; nothing here is specific to it.

> **Live SPICE needs the PDK.** Live optimization and the sanity check require both `ngspice` and the IHP `ihp-sg13g2` PDK (present on the research-group server). On a machine without the PDK the app detects this (`GET /api/env`), shows a **"PDK missing — replay only"** status pill, and disables live runs — while score shaping, checkpoint replay/compare, the wizard, and the pipeline view all work fully.

---

## Quick Start

**Prerequisites:** `uv`, `node`, `npm`, `ngspice` (for live runs).

The backend now lives in the [`spicexplorer-platform`](https://github.com/MacAnalog/spicexplorer-platform)
repo. The easiest way to run both together is from the
[`spicexplorer-workspace`](https://github.com/MacAnalog/spicexplorer-workspace)
meta-repo (which has both as submodules):

```bash
# From the spicexplorer-workspace checkout — starts api (:8000) + UI (:4000)
./scripts/run_dev.sh

# Verbose logging (DEBUG shows all spicexplorer library events)
LOG_LEVEL=DEBUG ./scripts/run_dev.sh
```

Open **http://localhost:4000** in your browser.  
VS Code Remote SSH auto-detects the port and offers to forward it — accept.

> **Why port 4000?** VS Code Remote SSH occupies port 3000 on the server side. The script uses 4000 to avoid the conflict.

### Manual startup (two terminals)

```bash
# Terminal 1 — FastAPI backend (from the spicexplorer-platform checkout)
LOG_LEVEL=INFO uv run uvicorn spicexplorer_api.main:app --reload --port 8000

# Terminal 2 — Next.js frontend (from this repo)
npm run dev -- -p 4000
```

---

## Architecture

```
Browser (localhost:4000)
  └─ Next.js 15 (TypeScript, App Router — Studio shell)
        │ REST + SSE
  FastAPI — spicexplorer_api (localhost:8000)   ← spicexplorer-platform repo
        │ Python imports
  spicexplorer (optimizer) + spicexplorer_core (spice_engine, env, pvt, …)
        │ subprocess
  ngspice  (+ IHP sg13g2 PDK, for live runs)
```

> **Repo split:** everything below the REST/SSE line — the FastAPI adapter
> (`spicexplorer_api`) and the Python libraries — lives in the
> [`spicexplorer-platform`](https://github.com/MacAnalog/spicexplorer-platform)
> repo (see its README for the route/service map and the Python test suite). **This
> repo is frontend-only**; every path in the file table below is relative to its root.

### Shell anatomy

The app is one persistent workspace. `app/page.tsx` redirects to `/setup`; all real views live under the `app/(studio)/` route group. `(studio)/layout.tsx` renders the shell once and only the center segment swaps on navigation, so the rails and the live SSE stream persist across views:

```
StudioTitleBar          brand · + New project · ⌘K · Run ▾
ActivityBar | LeftRail  | center view (SubTabStrip     | RightRail
(icons)     | (per-     | per view, e.g. Setup         | (live run:
            |  activity:|  Load/Wizard)                |  iteration,
            |  runs /   | BottomPanel (optimizer log)  |  specs, params)
            |  specs /  |                              |
            |  outline) |                              |
StudioStatusBar         active view · project · panel toggles · PDK/sim pill
Overlays: CommandPalette (⌘K) · WizardOverlay (+ New project) · ProjectsOverlay (⌘P)
```

### Key files

| Path | Role |
|---|---|
| *(backend)* | The FastAPI app, routes, and services (`optimizer_runner`, `env_probe`, `checkpoint_reader`, `yaml_generator`) live in `spicexplorer-platform/packages/spicexplorer-api/` — see that repo. |
| `src/app/page.tsx` | Redirect → `/setup` |
| `src/app/(studio)/layout.tsx` | Mounts `StudioShell`; persists across view navigation |
| `src/app/(studio)/<view>/page.tsx` | One thin segment per view (setup, scoring, optimize, compare, schematic, analyze, pipeline, manual, health, library) |
| `src/components/shell/` | `StudioShell`, `ActivityBar`, `SubTabStrip`, `StudioTitleBar`, `RunControl`, `Toolbar`, `StudioLeftRail`, `RightRail`, `BottomPanel`, `StatusBar`, `nav.ts` |
| `src/components/shell/rails/` | Per-activity left-rail variants: `RunsRail`, `SpecsRail`, `OutlineRail` (+ shared `parts`) |
| `src/components/shell/nav.ts` | **Single source of truth** for the 10 views (id, label, route, icon, shortcut, gating, `rail`, `fullBleed`) |
| `src/components/overlays/` | `CommandPalette` (⌘K), `WizardOverlay` (+ New project), `ProjectsOverlay` (⌘P) |
| `src/components/tabs/` | The center views: SetupTab, ScoreShapingTab, OptimizeTab, ExplorerTab, SchematicTab, PipelineView, ManualSimTab, HealthTab |
| `src/components/wizard/` | `WizardShell` + step components (`steps/`) |
| `src/components/charts/` | Plotly-backed chart components (all SSR-disabled) |
| `src/components/pvt/` | PVT corner UI: `CornerSelect`, `ManualSimPanel` |
| `src/components/schematic/` | Xschem hierarchy browser + device sensitivity inspector |
| `src/components/library/` | Reference Library (`/library`): browse panels, datasheet, source viewers, Register wizard |
| `src/components/analyze/` | Analyze waveform viewer (`/analyze`): dataset tree, plot, axes rail, log bar, open/import modal |
| `src/components/ui/` | Shared primitives: Button, Badge, Panel, Select, Table, EmptyState, SpecChip, Stat, Sparkline, `resizable` (drag-to-size rails), `SpiceEditor` (Monaco + SPICE grammar), `lightbox`, … |
| `src/stores/` | Zustand state: `projectStore`, `runStore` (+ SSE + history), `explorerStore`, `uiStore` (nav/selection/overlays), `wizardStore`, `libraryStore` (catalog + browse state), `libraryWizardStore` (Register wizard), `waveviewStore` (open datasets + wave fetches) |
| `src/lib/api.ts` | Typed fetch client — all backend calls go through here |
| `src/lib/library/` | Library data layer: `adapt.ts` (API→view types), `selectors.ts` (pure derivations), `data.ts` (presentation/authoring config) |
| `src/lib/waveview/` | Analyze data layer: `config.ts` (presentation), `selectors.ts` (pure derivations) |
| `src/config/ui.json` | Central user-facing copy/branding (imported as `UI` from `@/config`); `src/config/colors.ts` holds the `ACCENT` color tokens |
| `src/lib/xschem/` | Xschem `.sch`/symbol parsing + resolution helpers |
| `src/types/api.ts` | TypeScript mirrors of FastAPI response shapes (+ generated `api.gen.ts`; see `types/README.md`) |
| `.env.local` | `NEXT_PUBLIC_API_URL=` — empty (same-origin; the `/api/*` rewrite in `next.config.mjs` proxies to the backend). `src/lib/api.ts` falls back to `http://localhost:8000` when unset; set a direct backend origin here only when the browser runs on a different host than the backend (VS Code Remote, network IP). |

---

## Workflow

Navigate views via the activity-bar icons, the activity bar, or **⌘0–⌘9** (also `g`+digit chord; `?` opens the shortcut help sheet). Views that need an applied project (Score Shaping, Optimize, Pipeline) stay disabled until you apply one on Setup.

| View | What it does |
|---|---|
| **Library** (⌘9) | Browse the reference circuit catalog (analog-db): filter by class/PDK/compensation, view datasheet metrics, schematic renders (autogenerated modes + vendored hand-drawn references, zoomable lightbox), recorded benchmark results, functional sub-circuit templates (committed netlists open in a SPICE-highlighted viewer), and the class testbench catalog — each bench with its repo-derived simulator support (ngspice/Spectre chips), binding slots, and per-engine source. **Use as project** seeds a new optimization project from a catalog circuit. Register new circuits via the wizard (`POST /api/library/circuits`). Degrades gracefully when analog-db is absent. |
| **Analyze** (⌘0) | The waveform viewer: open any ngspice `.raw`, Spectre PSF dir, `keep_raw` optimizer run, or browser-uploaded artifact and inspect it as a dataset/trace tree + dual-axis plot + Tier-1 measurement strip (targets joined from the applied project's specs), with op-point tables and a live SSE simulator-log tail. |
| **Setup** | Load a project YAML (example dropdown or file upload) or **build one from scratch** with the 7-step wizard; edit in Monaco, validate, apply. Apply sends the current editor buffer (not a disk re-read), so unsaved Monaco edits are preserved. Shows project metadata, testbenches, DUT params, target specs. |
| **Score Shaping** | Select a spec, drag a slider to explore metric values. Compares linear vs sigmoid penalty curves with a per-spec breakdown. Deep-linkable from the ⌘K palette and the Pipeline view. |
| **Optimize** | Select algorithm/budget, then start a live SPICE run or replay a preset checkpoint. Streams score + metric convergence; live run progress, spec status, and best params appear in the always-on right rail. Live Start is disabled (steered to Replay) when the PDK is absent. |
| **Explore** | Load two checkpoints (Run A / Run B), overlay convergence, plot metric scatter, inspect the performance envelope and best design params. |
| **Schematic** | Browse the project's Xschem `.sch` hierarchy with symbol resolution. |
| **Pipeline** | Read-only DAG of the problem: Optimizer → DUT params → Testbenches → Target specs. Clicking a spec node deep-links into Score Shaping; spec nodes tint pass/fail live during a run. |
| **Manual Sim** | Evaluate one chosen design point through the optimizer's `evaluate` primitive (same scoring as a trial) — either an explicit param vector (engineering strings ok) or a checkpoint point. PDK-gated; isolated output folder. |
| **Health** (gear) | On-demand sanity check — runs one simulation per testbench + a trial optimizer step, reporting ngspice path, PDK verdict, and per-testbench log tails. |

### Shell features

- **Run history** — every finished run (live or replay) is recorded under its project and listed in the left rail with a score sparkline, served from the backend via `GET /api/projects/{id}/runs` (the client also keeps a recent-run cache in `localStorage`). Click a replay run to re-run it.
- **Command palette (⌘K)** — search to switch views, jump to a spec (→ Score Shaping), jump to a run (→ Optimize), start the new-project wizard, or stop a run.
- **Right rail / bottom panel** — toggle from the status bar; both stay live during a run regardless of the active view (the SSE stream lives in `runStore`).
- **Resizable panels** — every rail and panel (shell left/right/bottom, Library rails, Analyze tree/axes/log, wizard columns) drags to size from its edge; double-click resets, sizes persist per panel in `localStorage`.

---

## Feature Summary

### Implemented ✅

- **Studio shell** — App-Router route group with a persistent layout: activity bar, contextual left rail, always-on right rail, collapsible bottom panel, status bar. Views are deep-linkable (`/setup`, `/scoring`, …) and switchable via ⌘1–⌘9.
- **Per-activity left rails** — a persistent frame (project header + version) wrapping a body that swaps per active view (`rail` in `nav.ts`): `runs` (history + checkpoints, for Optimize/Explore), `specs` (clickable target-spec list → Score Shaping, for Score Shaping/Pipeline), `outline` (project structure: testbenches, devices, specs, for Setup/Schematic/Health).
- **Setup view** — Monaco YAML editor (debounced validation), example dropdown, Upload, Validate, Apply, plus the **Create Wizard** toggle.
- **New-project wizard** — 7-step form (Basic Info → PDK Rules → DUT Params w/ netlist upload → PVT → Testbenches → Target Specs → Optimizer) with a live YAML preview; generates + applies a `project_setup.yaml`. Launchable from Setup, the title-bar **+ New project**, or the ⌘K palette. Backed by `POST /api/project/generate`, `POST /api/project/parse-to-form`, `POST /api/netlist/parse`.
- **Score Shaping view** — Spec selector + slider (range = target ± 3×range), live penalty curve, per-spec breakdown (linear/sigmoid), highest-penalty callout. Honors deep-linked spec selection.
- **Optimize view** — Algorithm dropdown, budget input, preset checkpoint replay, Start/Stop with SSE streaming, score + metric convergence charts. **Algorithm and budget overrides are honored on live runs** (applied in-memory; YAML not rewritten); seed and autosave-every are set via the Run ▾ popover. Live Start disables + steers to Replay when the PDK is absent.
- **Run ▾ popover** — title-bar control to set the shared live-run overrides (algorithm/budget/seed/**autosave-every**) and start a run from any view; collapses to Stop + progress while a run is active, disables + steers to Replay when the PDK is absent. The Optimize toolbar shares the same `runConfig` (uiStore) for **algorithm and budget**, so those stay in sync; seed and autosave-every are editable only in the popover.
- **Checkpointing for long runs** — set "autosave every N trials" to write periodic, *cumulative* checkpoints during a live run; each one streams a `checkpoint` SSE event so the left-rail checkpoint list (and the right-rail "N checkpoints saved" counter) update live. Any autosave checkpoint has a **Resume** action (▶ in the rail) that continues that optimization from where it left off (`load_checkpoint` + `optimize(keep_history=True)`), seeding the iteration count and best-so-far from the restored history. A run also writes a `_FINAL` checkpoint on completion **and on Stop**, so an interrupted run is always resumable.
- **Right rail + bottom panel** — Live run progress, spec status chips, best params, and the optimizer log; keep updating across view changes (SSE hoisted into `runStore`).
- **Run history** — Server-persisted run list (per project, via the projects/runs API) with score sparklines; click a replay run to re-run.
- **Command palette (⌘K)** — Switch view · jump to spec · jump to run · new project · stop run.
- **Explore view** — Run A/B checkpoint selectors, overlaid convergence, metric scatter (X/Y), performance envelope, metric histogram, best design params, spec summary.
- **Schematic view** — Xschem `.sch` hierarchy browser with symbol resolution, plus a **device inspector**: pick a spec + device, set W/L (and bias/NG) operating points with sliders, and compute finite-difference sensitivity (`d(metric)/d(param)` and dimensionless elasticity); the inspector displays **elasticity** as a ranked bar chart. Backed by `GET /api/spec/{name}/sensitivity` (live SPICE — needs the PDK).
- **Pipeline view** — Read-only DAG (Optimizer → DUT params → Testbenches → Specs) with clickable spec nodes that deep-link to Score Shaping.
- **Health / sanity check** — One sim per testbench + a trial optimizer step; reports ngspice path, PDK verdict, per-testbench log tails.
- **PDK-aware degradation** — `GET /api/env` drives the status-bar sim/PDK pill and gates live runs.
- **Reference Library** — the full `/library` browser over the analog-db catalog: class/PDK/compensation filters, datasheets with recorded per-PDK results, schematic picker (autogenerated render modes + available hand-drawn references, zoomable lightbox), functional-template netlist viewer, the class testbench catalog with repo-derived simulator support + per-engine source viewers (ngspice deck / composed Spectre bench + SKILL calculator), **Use as project** seeding, and the Register wizard (PDK + simulator choices come from the DB registry). Its log strip and preview rail toggle from the Library status bar.
- **Analyze waveform viewer** — full-bleed result viewer over `/api/waveview/*`: open by path, browse, upload, or `keep_raw` run (server-side multi-artifact merge); per-analysis tabs with dual-axis Bode; measurement strip from the backend Tier-1 catalog joined to project specs; OP scalar tables; severity-filtered live log bar.
- **SPICE source viewing** — Monaco with a custom SPICE grammar (dot-commands, device cards, `{expr}`, `${...}` binding slots highlighted) used across the Library's netlist/testbench viewers.
- **Central UI config** — user-facing copy/branding in `src/config/ui.json`; accent color tokens in `src/config/colors.ts` (imported by the Tailwind theme and all chart/chip palettes).
- **UI primitives** — `Button`, `Badge`, `Panel`, `Select` + `selectCn()`, `Table`, `EmptyState`, `SpecChip`, `Stat`, `Sparkline`, `Segmented`, `Slider`, `ResizeHandle`/`useRailSize`, `SpiceEditor`, `Lightbox`.
- **Logging** — `setup_loggers(console_level=...)`; backend reads `LOG_LEVEL`. Files in `logs/SpiceXplorer_<timestamp>.log`.
- **CORS** — Allows any `localhost:<port>`.

---

## Logging

Set `LOG_LEVEL` when you start the stack — it is read by the **backend**, which does
the library logging (this repo only logs to the browser console):

```bash
LOG_LEVEL=DEBUG   ./scripts/run_dev.sh   # everything — all optimizer steps
LOG_LEVEL=INFO    ./scripts/run_dev.sh   # default — startup + milestones
LOG_LEVEL=WARNING ./scripts/run_dev.sh   # quiet — warnings and errors only
```

`run_dev.sh` lives in the [`spicexplorer-workspace`](https://github.com/MacAnalog/spicexplorer-workspace)
meta-repo. The backend's log **file** always captures `DEBUG` regardless of the
console level; the logger names and log-file layout are documented in the
[`spicexplorer-platform`](https://github.com/MacAnalog/spicexplorer-platform) repo.

---

## Checks

This is a frontend repo, so its checks are type-check, lint, vitest, and build:

```bash
npm run typecheck    # tsc --noEmit
npm run lint         # eslint src — zero warnings allowed
npm run build        # production build (delete .next before restarting dev)
npm run gen:types    # regenerate src/types/api.gen.ts from openapi.json
npm test             # vitest — unit tests for lib/library pure logic (adapt, selectors)
npm run test:watch   # vitest watch mode
```

> The CI workflow (`.github/workflows/ci.yml`) covers `typecheck`, `lint`, vitest
> (`npm test`), and `build`.

The Python library + backend test suite — fast smoke tests and slow real-ngspice
simulation tests (`uv run pytest [-m slow]`) — lives in the
[`spicexplorer-platform`](https://github.com/MacAnalog/spicexplorer-platform) repo.

---

## Common Bugs & Debugging

### "Load example…" dropdown missing

**Cause:** The dropdown renders only when the backend responds to `GET /api/config`. If the backend was not yet running when the page loaded, `appConfig` stays `null`.

**Fix:** Make sure both processes are running, then **hard-refresh** the page (`Ctrl+Shift+R`).

### App loads but backend calls fail (CORS error in browser console)

**Cause:** Next.js landed on a different port than the backend's CORS allowlist.

**Fix:** The CORS config uses `allow_origin_regex` matching any `localhost:<port>`. If you still see this after the fix, restart the backend.

### Port 4000 already in use / Next.js falls back to 4001

**Cause:** A previous dev session left Next.js running.

**Fix:**
```bash
lsof -ti tcp:4000 | xargs kill   # kill whatever is on 4000
npm run dev -- -p 4000
```
> Do **not** kill port 3000 blindly — VS Code Remote SSH may be using it.

### "Start Live Run" button stops immediately with no events

**Cause:** The optimizer thread threw an exception (SPICE binary not found, bad netlist path, missing PDK models, etc.).

**Fix:** Check the error message shown below the Start button. Also check the backend log — the full traceback is printed at `ERROR` level with `[run <id>]` prefix.

**Common root causes:**
- `ngspice` not in PATH → run `which ngspice`; add its directory to PATH or pass `path_to_simulator` in the YAML
- PDK model files not found → check `ws_root` and testbench netlist `.include` paths in the YAML
- YAML `simulator:` field points to wrong binary name

### Stale `.next` build cache after `npm run build`

**Cause:** Running `npm run build` for type-checking leaves production chunks that the dev server can't use.

**Fix:**
```bash
rm -rf .next
# then restart the dev server
```

### Monaco editor shows blank / "Loading editor…" forever

**Cause:** Monaco is SSR-disabled via `dynamic(..., { ssr: false })`; it needs the browser. Usually resolves on its own after hydration. If persistent, check the browser console for chunk load errors.

**Fix:** Hard-refresh. If chunks are missing, delete `.next` and restart.

### `TypeError: object of type 'ListTargetSpec' has no len()`

**Cause:** `project.optimizer_config.target_specs` is a custom `ListTargetSpec` object, not a plain list.

**Fix:** Use `.targets` to access the underlying list: `setup.optimizer_config.target_specs.targets`.

---

## API Reference

> The authoritative contract is the backend's generated `openapi.json` → `src/types/api.gen.ts`
> (run `npm run gen:types`). This table is a human-oriented map, grouped by feature.

**Config & health**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/config` | App config (preset checkpoints, default YAML path) |
| GET | `/api/env` | ngspice + IHP PDK probe → `{ngspice_ok, pdk_ok, live_runs_enabled, pdk_detail, …}` |
| GET | `/health` | Liveness probe → `{status: "ok"}` (no `/api` prefix) |

**Author / validate / generate a project**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/project/load` | Load + parse a project (by `yaml_path`, raw `yaml_content`, or `project_id`) |
| GET | `/api/yaml-text` | Raw YAML text (`text/plain`) for the Monaco editor (`?path=`) |
| POST | `/api/project/validate` | Validate YAML text without applying |
| POST | `/api/project/generate` | Wizard form → validated YAML (optionally save to disk) |
| POST | `/api/project/parse-to-form` | YAML → wizard form (round-trip for "Edit in wizard") |
| POST | `/api/netlist/parse` | Extract `.param` rows from an uploaded `.spice` netlist |
| GET | `/api/spec-library` | Shipped target-spec templates for the wizard's one-click specs |

**Projects & runs (server-persisted)**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/projects` | List saved projects |
| POST | `/api/projects` | Create a project (optional wizard YAML) |
| GET | `/api/projects/{id}` | Project detail (summary + manifest) |
| PATCH | `/api/projects/{id}` | Rename a project |
| POST | `/api/projects/{id}/fork` | Fork (duplicate) a project |
| DELETE | `/api/projects/{id}` | Soft-delete a project → trash |
| GET | `/api/projects/{id}/runs` | List a project's runs |
| PATCH | `/api/projects/{id}/runs/{run_id}` | Rename a run |
| DELETE | `/api/projects/{id}/runs/{run_id}` | Soft-delete a run |
| GET | `/api/examples` | List in-repo example projects |
| POST | `/api/projects/from-example` | Create a project from an example |
| GET | `/api/trash` | List soft-deleted items |
| POST | `/api/trash/{trash_id}/restore` | Restore a trashed project |

**Score shaping**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/score` | Compute sigmoid + linear penalties for given metric values |

**Optimization (live / replay)**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/optimize/start` | Start live run or replay; accepts `algorithm`/`budget`/`seed` overrides, `autosave_every` (periodic cumulative checkpoints), `resume_checkpoint_id` (continue a saved run), and `keep_raw` (retain per-trial `.raw` waveforms for the result viewer — off by default, disk grows with budget × testbenches); returns `run_id` |
| POST | `/api/optimize/stop/{run_id}` | Signal the run to stop |
| GET | `/api/optimize/stream/{run_id}` | SSE stream of optimization events |

**Checkpoints (history / analysis / export)**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/checkpoint` | List available checkpoints (`?project_id=` scopes to a project family) |
| GET | `/api/checkpoint/{id}` | Load checkpoint data (scores, metrics, params) |
| GET | `/api/checkpoint/{id}/envelope` | Best-ever per metric with pass/fail |
| GET | `/api/checkpoint/{id}/scatter` | X/Y scatter points with feasibility |
| GET | `/api/checkpoint/{id}/report` | Download a run report (zip: checkpoint + YAML + summary) |
| DELETE | `/api/checkpoint/{id}` | Delete an autosaved checkpoint (presets are read-only) |

**Single-shot SPICE**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/simulate/once` | Evaluate ONE design point (explicit param vector or a checkpoint point); PDK-gated |
| POST | `/api/sanity-check` | Health check: one sim per testbench + trial step; includes `pdk_ok`/`pdk_detail` |
| GET | `/api/spec/{name}/sensitivity` | Finite-difference `d(metric)/d(param)` for one spec; `?params=` scopes the sweep, `?at=name:val,…` overrides the baseline operating point (live SPICE) |

**Schematic**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/schematic` | Serve circuit SVG |
| GET | `/api/xschem/{file,list,project,resolve}` | Xschem hierarchy browsing for the Schematic view |
| POST | `/api/xschem/from-netlist` | Generate an xschem `.sch` from a netlist (optional SVG/PNG render) |

**Reference Library (analog-db catalog)** — backs the `/library` browser. Reads the optional
`examples/analog-db` submodule; degrades to `503` / `available:false` when it isn't installed.
PDK keys are the analog-db-native long names (`ihp-sg13g2`/`sky130`/`gf180mcu`) — `lib/library/adapt.ts`
maps them to the UI's short keys. The UI loads these once into `libraryStore` (`load()` on mount)
and the selectors derive every view from the result; nothing in the Library is hardcoded.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/library/status` | Availability probe → `{available, db_root, circuits, classes, reason}` (gates the UI) |
| GET | `/api/library/catalog` | Class-grouped catalog → `{schema, classes, circuits[]}` (the browse list) |
| GET | `/api/library/circuits/{id}` | One circuit's datasheet + per-PDK recorded results + available schematic modes (the datasheet view) |
| GET | `/api/library/circuits/{id}/schematic?mode=` | Serve a schematic `.svg` (`block_aware`/`hierarchical`/`pure`/`abstract`) — the datasheet's mode-switching viewer |
| GET | `/api/library/circuits/{id}/schematic-sources` | Everything viewable for a circuit: generated render modes + vendored hand-drawn reference images (the "Open in Schematic" picker) |
| GET | `/api/library/circuits/{id}/reference-image?name=` | Serve one vendored reference image (hand-drawn schematic scans, paper figures) |
| POST | `/api/library/circuits/{id}/project` | Seed a new optimization project from a catalog circuit (master netlist + PDK sizing copied in, provenance recorded) — the datasheet's **Use as project** |
| GET | `/api/library/results` | Bulk recorded-results map `{id: {pdk: result}}` (the browse cards' measured numbers) |
| GET | `/api/library/classes` | Per-class metric registry + per-testbench profiles: repo-derived engine availability (`ngspice`/`spectre`), `${...}` binding slots, authored description, Spectre wiring counts |
| GET | `/api/library/pdks` | The PDK registry: every bound PDK + the engine its committed `sim_engine` marker routes to (feeds the wizard's PDK/simulator choices) |
| GET | `/api/library/testbenches/{class}/{name}/netlist?engine=` | One bench's engine source: the authored ngspice `.spice` template, or the composed Spectre view (bench wiring + analysis templates + SKILL calculator expressions) |
| GET | `/api/library/templates` | Functional sub-circuit template library (current mirrors, diff pairs, …); each row carries an `image` ref |
| GET | `/api/library/templates/{id}/image` | Serve a template's committed net-colour-coded PNG render (`image/png`); 404 when absent |
| GET | `/api/library/templates/{id}/netlist` | A template's committed netlist source (the "View netlist" viewer) |
| POST | `/api/library/circuits` | Scaffold a **draft** circuit from a manifest (the Register wizard write path); `400` bad manifest / `409` id conflict |

The Library is fully repo-driven: the browse view, datasheet, template previews, testbench
profiles, and the PDK/simulator vocabularies all render committed artifacts (`catalog.json`,
`results/*.json`, `raw/**.svg`, template `*.png`, `_shared/` registries) — nothing about the
catalog is hardcoded client-side.

**Result viewer (waveview)** — the universal simulation-result viewer backend: open any
ngspice `.raw` file or Spectre psfascii raw dir and serve display-ready waves, every Tier-1
`{meas: …}` measurement, op-point tables, and classified simulator logs. Path posture:
absolute paths under `REPO_ROOT`/`WORK_ROOT` (+ `SPICEXPLORER_WAVEVIEW_ROOTS` opt-in).
Optimizer runs are openable by `run_id` — trial raws exist only when the run was started
with `keep_raw: true` (logs are always retained; Spectre `-raw` dirs persist regardless).

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/waveview/open` | Open an artifact by absolute path → dataset meta (idempotent: same path+mtime → same `dataset_id`) |
| GET | `/api/waveview/runs` | Optimizer runs the viewer can open (from their on-disk `run.json`s), newest first; `?project_id=` scopes |
| GET | `/api/waveview/runs/{run_id}/artifacts` | A run's openable artifacts: per-trial raws, Spectre raw dirs, logs (incl. `run.log`) |
| POST | `/api/waveview/open_run` | Open a run's result artifacts by `run_id` (optional `match` substring; `merge: true` combines the newest testbench raws into ONE dataset, duplicate analyses suffixed `#2`…) |
| POST | `/api/waveview/runs/{run_id}/prune` | Free a `keep_raw` run's sim raws on demand (`metrics_only` retention; metrics/checkpoints/logs kept; idempotent, open datasets evicted) |
| POST | `/api/waveview/upload` | Upload an artifact from the browser (`.raw` / Spectre-PSF `.zip` / log) → staged under `work/waveview_uploads/`, raws auto-open |
| GET | `/api/waveview/uploads` | Inventory of staged uploads (flags dirs backing open datasets); stale entries TTL-swept (`SPICEXPLORER_UPLOAD_TTL_DAYS`, default 14 d) |
| DELETE | `/api/waveview/uploads/{id}` | Delete one staged upload |
| GET | `/api/waveview/runs/{run_id}/artifacts/file` | Serve one run artifact file (whitelisted) |
| GET | `/api/waveview/datasets` | List open datasets (oldest first) |
| GET | `/api/waveview/datasets/{id}` | One open dataset's meta (analyses, signals, log path, warnings) |
| DELETE | `/api/waveview/datasets/{id}` | Close a dataset (frees its arrays) |
| GET | `/api/waveview/datasets/{id}/wave` | Waveform data: `fmt=auto\|mag_db\|mag\|phase_deg\|re\|im\|complex`, `max_points` budget + `method=minmax\|lttb\|stride\|none` downsampling; non-finite → `null` |
| POST | `/api/waveview/datasets/{id}/measure` | Evaluate Tier-1 `{meas: …}` recipes against the dataset (per-item error degradation) |
| GET | `/api/waveview/datasets/{id}/scalars` | Point scalars: op-point node values / per-device `inst:param` tables (`?prefix=` filters) |
| GET | `/api/waveview/datasets/{id}/log` | The dataset's simulator log, parsed + severity-classified (`?min_level=`, `?tail=`) |
| GET | `/api/waveview/log/stream` | **SSE live tail** of any whitelisted simulator log (works while the sim is still writing); `event: eof` marker + heartbeats |
| GET | `/api/waveview/browse` | List result artifacts in a directory (`.raw`, Spectre raw dirs, logs, subdirs) |
| GET | `/api/waveview/measurements` | Measurement catalog: every Tier-1 recipe name → kind / required args / default analysis |

SSE events (`/api/optimize/stream/{id}`):

```json
{ "iter": 42, "score": 0.31, "best_score": 0.18, "metrics": {"ugf": 1.9e8}, "best_params": {"X_DUT_M1M2_W": 2e-6} }
{ "checkpoint": {"id": "CASCODE-OTA_LhsDE_..._trial40", "index": 1, "iter": 40} }
{ "heartbeat": true }
{ "done": true }
{ "error": "ngspice exited with code 1: ..." }
```
