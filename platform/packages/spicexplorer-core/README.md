# spicexplorer-core

The **shared kernel** of the SpiceXplorer platform — the bottom layer of the `uv`
workspace. It carries the low-level primitives every other package and adapter depends on:
the SPICE engine wrappers, engineering-value parsing, runtime-environment detection, PVT
primitives, logging, and the workspace-root anchor. **It has no upward dependencies** —
nothing in `spicexplorer_core` imports a platform tool, an adapter, or a peer.

**Layering:** `core` is depended on by *everything* — `spicexplorer` (the optimizer), the
`spicexplorer-api` adapter (and the `spicexplorer-mcp` adapter, which lives in the
`spicexplorer-orchestration` repo), and all four leaf tools (`circuitgraph`, `netlist2tf`, `gmid`,
`netlist2xschem`). It depends only on `numpy` + `spicelib`.

Import name: `spicexplorer_core` (the distribution is `spicexplorer-core`).

## Install

Part of the `spicexplorer-platform` `uv` workspace — `uv sync` installs it editable into the
shared `.venv` alongside the other members. No extras; **library-only, there is no CLI**.

```python
import spicexplorer_core            # cheap — only the root anchor is re-exported
```

## Import discipline

Only the **cheap, dependency-free** root anchor is re-exported at the top level, so
`import spicexplorer_core` stays light:

```python
from spicexplorer_core import project_root, clear_cache, ROOT_ENV_VAR
```

Import the heavier primitives **from their submodules** (this keeps numpy/spicelib off the
import path until you actually need them):

```python
from spicexplorer_core.pvt import Corner, PVTConfig
from spicexplorer_core.spice_engine import NetlistView, NGSpice_Wrapper
```

## Public API — by module

| Module | Surface | What it's for |
|---|---|---|
| `paths` | `project_root()`, `clear_cache()`, `ROOT_ENV_VAR` | The workspace-root anchor — resolves repo-relative paths without depth-sensitive `parents[N]` walks. **Re-exported at the package root.** |
| `spice_engine` | `NetlistView`, `NetlistViewLike`; `NGSpice_Wrapper`, `LTspice_Wrapper`, `Sim_Execution_Type`, `Ngspice_Plot_Type` (+ `storage`) | NGSpice/LTspice + `spicelib` wrappers. `NetlistView` is the canonical parsed-netlist handle every *netlist-consuming* leaf tool starts from (none re-parse text; the gm/ID tool is LUT-based and doesn't use it). `NetlistViewLike` is the runtime-checkable Protocol of its ten topology accessors — consumers type against it. |
| `spice_engine.dialects` | `NetlistDialect`, `detect_dialect`, `get_reader`; `DialectSpec`, `Directive`, `ParsedDeck`, `DialectSyntaxError`, `SpectreReader`, `HspiceReader` (all re-exported from `spice_engine`) | **Spectre + HSPICE netlist reading.** `NetlistView.from_file(path, dialect="auto")` sniffs `.scs`/content markers and normalizes the foreign deck's *structural subset* to canonical SPICE (spicelib parses it); analyses/`.measure`/options/includes are preserved verbatim on `view.directives` (never translated, never resolved — foundry includes stay unread). `view.original_name(ref)` maps prefix-conformed refs back to the source names. Note: a bare-subckt HSPICE fragment (no `.end`, no HSPICE-only cards) needs an explicit `dialect="hspice"` — auto-detection is deliberately conservative so plain-SPICE behavior never changes. Design: meta `doc/plan_spectre_hspice_integration.md`. |
| `spice_engine.protocol` | `Simulator`, `SimResult`, `SimHandle` (re-exported from `spice_engine`, plus the ngspice adapters `NgspiceSimResult`, `NgspiceSimHandle` and `resolve_ngspice_plot_type`) | **The engine-neutral simulation seam** (P1 of meta `doc/plan_virtuoso_bridge.md`). Runtime-checkable structural `Protocol`s — `update_params` / `apply_corner(…, model_lib_root=)` / `run(label=)` / `submit(label=)`, results read via `scalar(name, analysis)` / `wave(name, analysis)` with an engine-neutral analysis string (`"op"`/`"ac"`/`"dc"`/`"tran"`/`"noise"`). `NGSpice_Wrapper` satisfies them via thin adapters (zero behaviour change to its legacy methods); the optimizer loop consumes ONLY this surface, so backends (e.g. the optional Spectre adapter in the `spicexplorer` package) plug in without core changes. Missing scalars degrade to NaN; missing waves raise. Optional duck-typed extras: `SimResult.log_path`, `Simulator.collect(handle)`. |
| `measurements` | `measure`, `validate_recipe`, `known_measurements`; the waveform math `dc_gain_db`, `unity_gain_freq`, `phase_margin`, `bandwidth_3db`, `gain_bandwidth_product`, `magnitude_at_db`, `band_worst_db`, `level_crossing_freq`, `settling_time`, `slew_rate`, `integrated_noise`, `harmonic_amplitudes`, `thd_from_waveform`, `thd_from_harmonics`, `hd_ratio`, `sfdr_from_harmonics`, `rejection_db`, `icmr_band`, `two_tone_indices`, `iip3_from_two_tone`, `iip3_from_harmonics`, `gain_margin_db`, `dc_gain_linear`, `magnitude_db` | **Engine-neutral Tier-1 measurement library** (P5 foundation of meta `doc/plan_virtuoso_bridge.md`). Canonical, version-controlled figures of merit computed from a `SimResult` — the SAME math for ngspice and Spectre. `measurements.waveforms` is pure numpy over raw arrays (unit-tested against analytic single/two-pole transfers; phase-margin is `180 − φ₀ + φ_ugf`, sign-convention agnostic). `measurements.registry.measure(result, {meas, …}, default_analysis=…)` evaluates a declarative recipe against the result's own waves/scalars (`validate_recipe` catches an unknown name / missing arg at load). **P5d distortion:** `thd_from_waveform` extracts THD from a transient output by *coherent* resampling + integer-bin `rfft` (the SPICE `.four` analogue, engine-neutral) — recipes `{meas: thd\|thd_pct\|thd_db, out, f0, n_harmonics?, n_periods?}` (`n_periods` analyses the clean tail past startup). **Native-PSS distortion twins:** `thd_from_harmonics`/`hd_ratio`/`sfdr_from_harmonics` compute the same figures from a complex per-harmonic phasor array (a Spectre `pss` fd-PSF) — no resample/window. **Bench validation (2026-07-09):** `rejection_db` (CMRR/PSRR = −dcgain of the unity-disturbance residual), `icmr_band` (widest CONTIGUOUS tracking band of a buffer DC sweep — the `dc` recipe kind), and the two-tone IIP3 family (`two_tone_indices` rationalizes the pair onto a common fundamental; `iip3_from_two_tone` = the tran+FFT route for ngspice, `iip3_from_harmonics` = the PSS-phasor route; recipes `iip3|iip3_dbv|im3_dbc` and `iip3_pss*` — the three spellings derive from one figure). **Loop margins (stb, 2026-07-10):** `gain_margin_db` (−|T|dB at the −180° crossing, referenced to the start phase snapped to its nearest 180° multiple — live == Spectre's own stb gainMargin to 4 digits) joins `phase_margin` for loop-gain waves; the `stb` recipe kind (`{meas: pm_loop|gain_margin_db|loopgain_db, out: loopGain}`) reads a Spectre `stb` analysis' loopGain trace — the only wave a LOOP margin is honestly defined on (a closed-loop AC transfer never crosses unity). **Input impedance (P3-2c):** `zin_mag` reads |Z| from a unit-current-driven node wave (direct form: `ac mag=1`/`pac pacmag=1` on a current source → the node voltage IS the impedance) or from a series-sense wave RATIO (`out`/`ref` with `scale: 2·Rs` — for high-impedance ports whose large-signal bias must stay stiff), at an optional spot `f`; with `{analysis: pac}` it is the chopper/SC Z_in a static ac cannot see. **Band-edge / spot reads (2026-08-18):** a swept `ac dec N` grid seldom lands on a spec's band edge (`dec 20` from 100 MHz never samples 32 or 50 GHz — its last in-band points are 31.62 / 44.67 GHz), so `max(mag[f <= f_edge])` silently reads a neighbouring frequency and flatters a rising reflection curve (0.04–0.5 dB on the PAM-4 driver: the difference between pass and fail). `magnitude_at_db(freq, h, f0)` (|H| dB at exactly `f0`, log-f interpolated), `band_worst_db(freq, h, f_edge, f_start=, worst=max|min)` (worst |H| dB over the band INCLUDING the interpolated edges) and `level_crossing_freq(freq, h, level_db)` (the "−10 dB edge" frequency) are the grid-independent reads; recipes `{meas: mag_at_db, out, f}`, `{meas: band_max_db|band_min_db, out, f_edge, f_start?}`, `{meas: level_cross_hz, out, level}` (+ optional `ref`). NaN outside the sweep, never extrapolated. Optimizer-side, `spicexplorer.optimization.measure_integration` merges these under the target-spec name so the scorer seam is unchanged. **Static power + active area (area/power optimization flow):** the `op` kind adds `{meas: power\|power_mw\|power_uw, probe, vdd}` (= |I_supply|·VDD off the same supply-current probe as `i_supply`); and a sibling `measurements.derived` module (`compute_derived`, `validate_derived_recipe`, `known_derived`, `active_area`) computes a **parameter-derived** figure — `active_area` = `Σ W·L·m` gate area — from the *candidate sizing itself*, with NO simulation (a `{derived: …}` recipe). It is merged into the performance map by `spicexplorer.optimization.derived_integration` and scored/normalized/aggregated exactly like any sim metric. **Netlist-driven active area (`measurements.area`):** `active_area_report(netlist, overrides=…, scale=…)` **recursively walks every device** in a self-contained deck (via the parse-only `NetlistView` — no ngspice/PDK), resolves each MOSFET's `W`/`L`/`m` from the deck's `.param` map (evaluating `{…}` brace ties/ratios like `{x_dut_xm14_m*8}` and eng literals; candidate `overrides` win over deck defaults), threads each subckt instance's own `m` down the hierarchy, and returns a JSON-serializable report: the scored `active_area`, a per-device `devices` breakdown, an `others` list (every non-MOS instance — R/C/sources — so the accounting is complete + verifiable), a `coverage` tally, and `warnings`. This is what an `active_area` recipe with **no `devices:` list** is scored by — a hand list can silently omit a device or its multiplier; a netlist walk cannot. CLI/verifier: `python -m spicexplorer_core.measurements.area <deck.spice> [--table] [--json out] [--set k=v]` (`format_area_table` for the debug table; nonzero exit if coverage is incomplete). `resolve_param_value(token, params)` exposes the resolver standalone. |
| `pvt` | `Corner`, `PVTConfig`, `ModelInclude`, `SupplyOverride`, `monte_carlo_corners`, `normalize_score_aggregation`, `PVT_MODES`, `SCORE_AGGREGATION_STRATEGIES` | Process/Voltage/Temperature primitives — a corner is a model-include set + supply/temperature overrides (+ `Corner.options`: extra engine-neutral `.options` cards, e.g. an RNG `seed`). `PVTConfig.mode` (`single`\|`multi`) + `score_aggregation` (`mean`\|`sum`\|`min`\|`worst_spec`, aliases like `add`/`average`/`worst_case`/`per_spec_min` normalized at load) drive the multi-corner sweep — the first three reduce the per-corner TOTALS, `worst_spec` reduces the SPEC axis across corners first (each spec keeps its worst corner) so feasibility means "feasible at every enabled corner" (and asking for it while `mode` is `single` warns at load — it has nothing to reduce over); the numeric collapse for all of them lives in the optimizer layer (`spicexplorer.core.utils`), core owns only the vocabulary. In `multi` mode a trial's simulation cost is multiplied by the number of enabled corners. multi mode fail-fast validates enabled-corner presence, checkpoint-safe names, and corner symmetry. **Monte Carlo mismatch:** `monte_carlo_corners(base, N, seed0=…)` clones a corner into `mc1..mcN` sample corners — every include whose library defines a `<section>_mismatch` sibling is swapped to it (the sections whose model cards carry `agauss()` draws) and each sample gets `options={"seed": seed0+i-1}` (→ `.options seed=` via `apply_corner`; same seed reproduces the draw). Raises when no include has a statistical sibling — never a silent fake MC. Guide: [`notebooks/monte_carlo_corners.ipynb`](notebooks/monte_carlo_corners.ipynb). |
| `env` | `probe_env`, `probe_ngspice`, `probe_pdk`; `probe_spectre`, `probe_cadence`, `probe_cadence_env` | Runtime capability detection — is ngspice on `PATH`, is a PDK present (`pdk_ok`). Backs the API's `/api/env` and the live-vs-degraded behaviour. The Cadence probes (`spectre_ok` / `cadence_ok` / `cadence_live_enabled`, P6 of the bridge plan) are **separate functions** — `probe_env`'s contract (and `/api/env`) is unchanged; CI skip-gates for Spectre-live tests key off them. |
| `atomic_io` | `atomic_write_json`, `atomic_write_text`, `atomic_write_bytes` | Crash-safe file writes: temp-in-same-dir → `fsync` → `os.replace`. A process killed mid-write can't leave a truncated file, so the optimizer's autosave/checkpoint (which both call this) is never corrupt for the next resume. `atomic_write_bytes` is the binary sibling used by the run-envelope object store. |
| `workspace` | `work_root`, `shared_root`, `scaffold_project`, `scaffold_shared`, `PROJECT_DIRS_V2`, `SHARED_DIRS`; `read_manifest`, `write_manifest`, `new_manifest`, `upgrade_manifest`, `MANIFEST_NAME`, `SCHEMA_VERSION`; `migrate_project`, `migrate_workspace`, `is_project_dir`; the run envelope (`workspace.runs`): `new_run_id`, `mint_run_dir`, `envelope_fields`, `write_run_record`, `read_run_record`, `touch_heartbeat`, `owner_is_dead`, `snapshot_inputs`, `project_objects_dir`, `ENVELOPE_VERSION`; retention/GC (`workspace.retention`): `prune_run`, `prune_workspace`, `iter_candidates`, `RETENTION_TIERS`; verification (`workspace.verify`): `load_verify_plan`, `VerifyPlan`, `Spec`, `parse_target`; derived rollup (`workspace.state`): `build_state`, `rebuild_state`, `read_state`; promotion (`workspace.promote`): `promote`, `current_promotion`, `list_promotions`; curated annotations (`workspace.annotations`): `read_curated`, `write_curated`, `merge_proposal`, `merge_curated` | **WORK_ROOT storage kernel** — the project-filesystem contract (layout v2) shared by the API's `project_service` and orchestration agents, so every process speaks ONE storage schema. `work_root()` is the canonical `$WORK_ROOT`-or-`<repo>/work` resolver (the API's `app_config.work_root` delegates here); `scaffold_project` idempotently creates the v2 per-project structure (`spec/ topology/ design/cells design/history testbenches/ jobs/ runs/ analyses/ layout/ context/` + the v1 dirs); `manifest.json` (schema v2: monotonic `rev`, `default_job`, `default_pdk`) is written atomically via `atomic_io` — a torn manifest never equals a vanished project. The v1→v2 migrator is **additive + idempotent** (never moves/renames anything; `project.yaml` stays at the project root): CLI `python -m spicexplorer_core.workspace [--work-root PATH] [--dry-run]`. **The run envelope (P3)** generalizes runs to every job kind: `mint_run_dir` mints a timestamp-sortable id whose name IS the run dir (`mkdir(exist_ok=False)`), `envelope_fields` stamps `kind`/`owner{pid,hostname}`/`retention`/`inputs` into `run.json` (written atomically via `write_run_record`), `touch_heartbeat` is the cheap per-step liveness signal (one utime, no JSON rewrite), `owner_is_dead` is the reconcile gate (pid probe on this host, heartbeat staleness on a foreign one — an agent's live run survives an API restart), and `snapshot_inputs` sha256-hashes every input and content-addresses the blobs into the owning project's `.objects/` so an immutable record's provenance dereferences forever. **Retention/GC (P3.1)** is the store's garbage collector: each run's `retention` tier (`full`/`metrics_only`/`none`) is enforced by `prune_run` (idempotent, terminal-only) and `prune_workspace` (age-gated sweep; CLI `python -m spicexplorer_core.workspace.retention [--older-than-days N] [--dry-run]`) — `metrics_only` drops the heavy `sim/` waveforms but keeps the record + history, `none` keeps only `run.json`. Per-trial candidates are already columnar rows in `events.ndjson` (not directories); `iter_candidates` is their stable reader. **Verification + state + promotion (P4)** make the design flow queryable: `verify/plan.yaml` is the spec×test×corner joining table (`load_verify_plan`; targets stay canonical in `spec/targets.yaml`), `build_state`/`rebuild_state` derive a rebuildable `state.json` (spec×corner compliance matrix from the plan × run history, best-run pointers with the election rule *stated*, cell inventory), `promote` snapshots the accepted design into a sortable `design/history/<id>/` and swaps an atomic `current` pointer under a per-project `fcntl` lock, and curated annotations (`design/cells/*/annotations.yaml`) survive regeneration — `merge_proposal`/`merge_curated` treat a raw re-label as a **proposal** that preserves every human override (D-6), never a blind overwrite. **Reuse + agent context (P5)**: `publish_cell`/`import_cell` are the `shared/lib/<cell>/<version>` shelf — publish-on-promote, **copy-on-import** with an `imported_from` record, versions immutable (D-9); and the agent context surface is append-only — `append_decision` O_APPENDs to `context/decisions.ndjson` and `render_project_md` GENERATES `context/PROJECT.md` from the decision log + `state.json` (agents write events, never documents — D-10). Design + locked decisions: meta `doc/plan_project_filesystem.md`. |
| `logging` | `setup_loggers` (the package-level export); `setup_loggers_with_spicelib_suppression` / `setup_spicelib_logging` are imported from the `spicexplorer_core.logging.logger_setup` submodule | Logger setup with spicelib-noise suppression + a Jupyter log filter. |

## Quickstart

```python
from spicexplorer_core import project_root
from spicexplorer_core.eng import parse_value
from spicexplorer_core.env import probe_env

project_root()                 # → workspace root Path (cached; override via $SPICEXPLORER_ROOT)
parse_value("0.18u")           # → 1.8e-7
probe_env()                    # → {"ngspice_ok": ..., "pdk_ok": ..., ...}
```

See [`notebooks/core_quickstart.ipynb`](notebooks/core_quickstart.ipynb) for a guided tour
(paths, `parse_value`, env probing, `NetlistView`), and
[`notebooks/workspace_quickstart.ipynb`](notebooks/workspace_quickstart.ipynb) for the
WORK_ROOT v2 storage kernel (scaffold, `manifest.json` + `rev`, additive migration, and the
run envelope: `dir == run_id`, owner-liveness, `.objects/` provenance).

**On-disk layout at a glance:** [`doc/workspace_layout.md`](doc/workspace_layout.md) is the
visual `WORK_ROOT/` tree (annotated by storage class) + lifecycle scenarios — a fresh
project, an optimizer run, retention/GC tiers, multi-kind runs, verify → `state.json`,
promotion history, the shared library, and the decisions → `PROJECT.md` context surface.
[`notebooks/project_lifecycle.ipynb`](notebooks/project_lifecycle.ipynb) is the runnable
version.

Reading a foreign-dialect netlist (Spectre / HSPICE):

```python
from spicexplorer_core.spice_engine import NetlistView

v = NetlistView.from_file("cell.scs")            # auto: .scs → Spectre reader
v.dialect                                        # NetlistDialect.SPECTRE
v.get_subcircuit_names()                         # topology accessors work as usual
[d.kind for d in v.directives]                   # analyses/options/includes, verbatim
tb = NetlistView.from_file("tb.sp", dialect="hspice")   # explicit for bare-subckt fragments
```

## Notes

- `spicelib` is pinned `>=1.5,<1.6` — 1.6 dropped `ParameterNotFoundError` /
  `ComponentNotFoundError` from `base_editor`, which `spice_engine.spicelib` relies on.
- `project_root()` is the single source of truth for repo-relative paths — never re-add a
  `Path(__file__).parents[N]` walk.

## Tests

```bash
uv run pytest packages/spicexplorer-core/tests -v
```
