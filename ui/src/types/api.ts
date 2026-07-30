// API response types. Most are hand-written; a growing subset is ADOPTED from the
// OpenAPI codegen (api.gen.ts) as routes gain response_models — see src/types/README.md.
import type { components } from "./api.gen";

// Loaded-project shapes (the `_summarise()` tree) — adopted from codegen. The backend
// `/project/load` + `/projects/{id}` now carry a response_model, so the whole
// ProjectSummary tree is a one-line alias set over the generated schemas. Note: the
// generated `TargetSpec.goal` is `string` (the wire value), not the old narrowed
// "exceed" | "minimize" | "exact" — the editable union lives in WizardTargetSpec.
export type DutParam = components["schemas"]["DutParam"];
export type TbParam = components["schemas"]["TbParam"];
export type Testbench = components["schemas"]["Testbench"];
// PVT corner system (Phase 1) — the simulator-driving config (`pvt:` block).
export type ModelInclude = components["schemas"]["ModelInclude"];
export type SupplyOverride = components["schemas"]["SupplyOverride"];
export type PVTCornerDef = components["schemas"]["PVTCornerDef"];
export type PVTConfig = components["schemas"]["PVTConfig"];
export type TargetSpec = components["schemas"]["TargetSpec"];

// Adopted from codegen (api.gen.ts → ParamSensitivity / SensitivityResponse).
export type ParamSensitivity = components["schemas"]["ParamSensitivity"];
export type SensitivityResponse = components["schemas"]["SensitivityResponse"];

export type ProjectSummary = components["schemas"]["ProjectSummary"];

// Adopted from codegen (api.gen.ts). The backend route now carries a response_model,
// so these are one-line aliases over the generated schema (single source of truth).
export type LoadProjectResponse = components["schemas"]["LoadProjectResponse"];
export type ValidateResponse = components["schemas"]["ValidateResponse"];

// Score shaping — adopted from codegen.
export type SpecScore = components["schemas"]["SpecScore"];
export type ScoreCurve = components["schemas"]["ScoreCurve"];
export type ScoreResponse = components["schemas"]["ScoreResponse"];

// Optimization run

// Adopted from codegen — the backend always emits resumed + n_iters (now required).
export type RunStartResponse = components["schemas"]["RunStartResponse"];

/** Backend-derived Nevergrad algorithm lists (GET /api/optimize/algorithms). */
export type AlgorithmsInfo = components["schemas"]["AlgorithmsResponse"];

/** Emitted when a live run autosaves a (cumulative) checkpoint. */
export interface CheckpointEvent {
  id: string | null;
  index: number;
  iter: number;
}

export interface SSEEvent {
  iter?: number;
  score?: number | null;
  best_score?: number | null;
  metrics?: Record<string, number | null>;
  best_params?: Record<string, number | null>;
  /** Snapshot of the BEST trial's metrics (live runs) — distinct from `metrics`, the
   *  latest trial. The right-rail / Pipeline key their pass-fail off this. */
  best_metrics?: Record<string, number | null>;
  checkpoint?: CheckpointEvent;
  done?: boolean;
  error?: string;
  heartbeat?: boolean;
  /** A raw SpiceXplorer-library log line (per-run), with its level for coloring. */
  log?: string;
  level?: string;
}

// Checkpoints

// Checkpoints — adopted from codegen.
export type CheckpointMeta = components["schemas"]["CheckpointMeta"];
export type CheckpointData = components["schemas"]["CheckpointData"];
export type EnvelopeEntry = components["schemas"]["EnvelopeEntry"];
export type ScatterPoint = components["schemas"]["ScatterPoint"];

// Sanity check

// Sanity check (POST /api/sanity-check) — adopted from codegen (api.gen.ts →
// SanityResponse). Replaces the hand-written type, which had also drifted (it was
// missing the backend's `warnings` field). Sub-shapes are inlined in the schema.
export type SanityCheckResponse = components["schemas"]["SanityResponse"];

// Manual single simulation — evaluate ONE chosen design point (POST /api/simulate/once)
// Adopted from codegen (api.gen.ts → SimulateOnceResponse).
export type SimulateOnceResponse = components["schemas"]["SimulateOnceResponse"];

// Environment probe — simulator + PDK availability (GET /api/env)
// Adopted from codegen (api.gen.ts → EnvResponse).
export type EnvInfo = components["schemas"]["EnvResponse"];

// Config — adopted from codegen (api.gen.ts → ConfigResponse). Config presets carry
// `exists` (PresetCheckpoint), distinct from the checkpoint-listing CheckpointMeta above.
export type AppConfig = components["schemas"]["ConfigResponse"];

// Wizard

export interface NetlistParam {
  name: string;
  default_val: string;
}

export interface MeasCandidate {
  name: string;
  sim_type: string;
}

// Adopted from codegen (api.gen.ts → NetlistParseResponse).
export type NetlistParseResponse = components["schemas"]["NetlistParseResponse"];

/** A shipped analog-spec template (examples/spec_library.yaml) for one-click adds. */
export type SpecLibraryEntry = Partial<WizardTargetSpec> & { name: string };

export interface SpecLibraryResponse {
  specs: SpecLibraryEntry[];
}

// ---- Projects (report.md P3) — adopted from codegen ----
export type ProjectMeta = components["schemas"]["ProjectMeta"];
export type ProjectDetail = components["schemas"]["ProjectDetailResponse"];
export type ProjectRun = components["schemas"]["ProjectRun"];
/** `description` is server-new (from the example YAML) — typed here until the
 *  next openapi regen catches up. */
export type ExampleMeta = components["schemas"]["ExampleMeta"] & {
  description?: string | null;
};
// Soft-delete bin (report.md P4) — a deleted project/run MOVED to WORK_ROOT/.trash.
export type TrashItem = components["schemas"]["TrashItem"];

// Adopted from codegen (api.gen.ts → GenerateProjectResponse).
export type GenerateProjectResponse = components["schemas"]["GenerateProjectResponse"];

// NOTE: ParseProjectResponse is intentionally kept hand-written — its `form` is the
// EDITABLE WizardForm (constructed/mutated in wizardStore), whose richer optional/union
// shapes are deliberately stricter than the generated all-required schema.
export interface ParseProjectResponse {
  ok: boolean;
  form: WizardForm;
}

// Wizard form shapes — mirrors yaml_generator.py expectations
export interface WizardProjectInfo {
  name: string;
  description: string;
  simulator: string;
  save_sim: boolean;
  parallel_sim: boolean;
  ws_root: string;
  netlist: string;
  outdir: string;
}

export interface ConstraintRow { key: string; value: string }

export interface WizardTech {
  name: string;
  constraints: ConstraintRow[];
}

// New PVT corner system (Phase 1) — wizard editing shapes. Corners are emitted
// with inline `model_includes` (no process_bundles) to keep the wizard flat.
export interface WizardModelInclude {
  lib_file: string;
  section: string;
}

export interface WizardPVTCorner {
  name: string;
  temp: string;
  supply_node: string;
  supply_value: string;
  /** Rails 2..N, carried losslessly through the wizard (the form edits only the primary
   *  rail; multi-rail corners are authored/edited in the raw YAML). */
  extra_supplies?: { node: string; value: string }[];
  enabled: boolean;
  includes: WizardModelInclude[];
}

export interface WizardPVTConfig {
  active_corner: string;
  corners: WizardPVTCorner[];
  /** Optional root prepended to each corner include's lib_file at sim time. */
  model_lib_root?: string;
}

export interface WizardDutParam {
  name: string;
  default_val?: string; // from netlist, displayed only
  min_val: string;
  max_val: string;
  init?: string;
  val?: string; // frozen operating point (pins a freeze:true param); round-tripped (BUG-B15)
  is_integer: boolean;
  log_scale: boolean;
  freeze: boolean;
  source?: "netlist" | "manual";
}

export interface WizardTbParam {
  name: string;
  val: string;
  description?: string;
  source?: "netlist" | "manual";
}

export interface WizardTestbench {
  name: string;
  netlist: string;
  enable: boolean;
  description: string;
  params: WizardTbParam[];
}

export interface WizardTargetSpec {
  name: string;
  testbench: string;
  sim_type: "ac" | "dc" | "op" | "tran" | "noise" | "noise_spectrum";
  goal: "exceed" | "minimize" | "exact";
  target: string;
  range: string;
  tolerance: string;
  weight: string;
  log_scale: boolean;
  error_type: string;
  reward_type: string;
  enable: boolean;
  description: string;
}

export interface OptimizerKwargRow { key: string; value: string }

export interface WizardOptimizer {
  type: string;
  name: string;
  budget: number | string;
  random_seed: number | string;
  lin_min: string;
  lin_max: string;
  log_min: string;
  log_max: string;
  optimizer_kwargs: OptimizerKwargRow[];
}

export interface WizardForm {
  project: WizardProjectInfo;
  tech: WizardTech;
  /** PVT corner system (Phase 1) — the simulator-driving config. */
  pvt: WizardPVTConfig;
  dut_params: WizardDutParam[];
  testbenches: WizardTestbench[];
  target_specs: WizardTargetSpec[];
  optimizer: WizardOptimizer;
}

// --- Netlist → xschem schematic (POST /api/xschem/from-netlist) ---------------
export interface XschemFromNetlistRequest {
  netlist_path?: string;
  netlist_text?: string;
  name?: string;
  pdk?: string;
  /** Optional subckt *instance* name to descend into before generating. */
  into?: string;
  render?: "none" | "svg" | "png";
}

export interface XschemSchematicResult {
  sch_content: string;
  sch_path: string | null;
  image_path: string | null;
  image_fmt: "svg" | "png" | null;
  image_available: boolean;
  device_count: number;
  label_count: number;
  warnings: string[];
}

// --- Reference Library (GET /api/library/*) -----------------------------------
// The analog-db catalog browser contract. These mirror the FastAPI `library`
// router (spicexplorer-platform) verbatim — note PDK keys are the analog-db-native
// LONG names (`ihp-sg13g2` / `sky130` / `gf180mcu`); `lib/library/adapt.ts` maps
// them to the UI's short display keys. These stay **hand-written** (not codegen
// aliases): the backend types the heterogeneous `measures` / `symbolic` / `datasheet`
// as `dict[str, Any]`, so the generated `api.gen.ts` renders them as
// `Record<string, unknown>` — losing the precise field typing the adapter relies on
// (`r.symbolic.sym`, `m.dcgain`). Same rationale as `SpecLibraryResponse`.
// The `analog-db` submodule is optional → `LibraryStatus.available` gates the UI;
// the data routes 503 when it is absent.
export interface LibraryStatus {
  available: boolean;
  db_root: string | null;
  circuits: number;
  classes: string[];
  reason: string | null;
}

export interface LibraryProvenance {
  source?: string;
  designer?: string;
  license?: string;
  paper?: string;
  aliases?: string[];
  [k: string]: unknown;
}

/** One catalog entry (analog-db `catalog@1`). `class`/`compensation`/`stages` are
 *  the native field names; `pdks` are long keys. */
export interface LibraryCatalogCircuit {
  id: string;
  class: string;
  display_name: string;
  compensation: string | null;
  stages: number | null;
  pdks: string[];
  analyses: string[];
  status: string;
  provenance: LibraryProvenance;
  schematic: Record<string, string>;
  raw: Record<string, unknown>;
}

export interface LibraryCatalog {
  schema: string;
  classes: Record<string, string[]>;
  circuits: LibraryCatalogCircuit[];
}

/** One recorded result (`tt` corner). `measures` flattens the per-analysis blocks;
 *  `analyses` keeps them raw; `symbolic` is the netlist2tf dc-gain cross-check. */
export interface LibraryCircuitResult {
  corner: string;
  run_at: string | null;
  measures: Record<string, number>;
  analyses: Record<string, { status?: string; measures?: Record<string, number> }>;
  symbolic: { sym: number; sim: number; err: number; tol: number; agrees: boolean } | null;
}

export interface LibraryCircuitDetail extends LibraryCatalogCircuit {
  ports: string[];
  datasheet: Record<string, unknown>;
  /** Available schematic views → repo-relative `.svg` path. Keys are a subset of
   *  `block_aware` / `hierarchical` / `pure` / `abstract`; fetch the bytes from
   *  `GET /api/library/circuits/{id}/schematic?mode=`. */
  schematics: Record<string, string>;
  /** Keyed by the long PDK name; omits PDKs with no recorded run. */
  results: Record<string, LibraryCircuitResult>;
}

/** Bulk recorded-results map (sparse — only measured circuits): `{id: {pdk: result}}`. */
export interface LibraryResults {
  results: Record<string, Record<string, LibraryCircuitResult>>;
}

/** One class testbench's engine availability + authored profile — repo-derived, never
 *  hardcoded: `ngspice` iff the committed `.spice` template exists, `spectre` iff the
 *  bench is wired in the class `spectre-benches.yaml`. */
export interface LibraryClassTestbench {
  name: string;
  engines: string[];
  path: string | null;
  description: string;
  slots: string[];
  spectre_analyses: number;
  spectre_calculator: number;
}

export interface LibraryClass {
  class: string;
  description: string;
  canonical_metrics: string[];
  templates: string[];
  testbenches: LibraryClassTestbench[];
}

export interface LibraryClassesResponse {
  classes: LibraryClass[];
}

/** One bound PDK + the simulator the DB's committed `sim_engine` marker routes it to. */
export interface LibraryPdk {
  id: string;
  sim_engine: string;
}

export interface LibraryPdksResponse {
  pdks: LibraryPdk[];
}

/** One functional template's committed netlist source (the matcher's topology). */
export interface LibraryTemplateNetlist {
  id: string;
  path: string;
  language: string;
  content: string;
}

/** Every schematic the DB holds for one circuit, by provenance. */
export interface LibrarySchematicSources {
  circuit_id: string;
  /** netlist2xschem export-raw renders (browser-displayable SVGs). */
  generated: { mode: string; path: string }[];
  /** Displayable hand-drawn / paper images — present for SOME circuits only. */
  reference: { name: string; path: string }[];
  /** Vendored non-displayable sources (.sch etc.) — named for honesty. */
  reference_other: string[];
}

/** `POST /api/library/circuits/{id}/project` — seed a project from a catalog circuit. */
export interface LibrarySeedProjectResponse {
  id: string;
  circuit_id: string;
  cell: string;
  pdk: string | null;
  netlist_seeded: boolean;
}

/** One testbench's engine source: the authored ngspice `.spice` template
 *  (`${...}` binding slots intact), or the composed Spectre bench wiring +
 *  SKILL calculator expressions (YAML). */
export interface LibraryTestbenchNetlist {
  class: string;
  name: string;
  engine: "ngspice" | "spectre";
  /** What to highlight the content as: "spice" | "yaml". */
  language: string;
  /** db-root-relative source path (template, or the spectre bench wiring). */
  path: string;
  content: string;
}

export interface LibrarySubcircuitTemplate {
  id: string;
  display_name: string;
  family: string;
  polarity: string | null;
  role: string | null;
  class: string | null;
  netlist: string | null;
  ports: Record<string, string>;
  /** Repo-relative path of the committed PNG render, or null if none exists. Fetch the
   *  bytes via `libraryTemplateImageUrl(id)` → GET /api/library/templates/{id}/image. */
  image: string | null;
}

export interface LibraryTemplatesResponse {
  families: string[];
  templates: LibrarySubcircuitTemplate[];
}

/** Register-wizard write payload (`POST /api/library/circuits`). Scaffolds a draft;
 *  `status` is not accepted (always draft). `pdks` are the long DB names. */
export interface CreateCircuitRequest {
  id: string;
  class: string;
  display_name?: string;
  compensation?: string | null;
  stages?: number | null;
  ports?: string[];
  pdks?: string[];
  analyses?: string[];
  provenance?: Record<string, unknown>;
  datasheet?: Record<string, unknown> | null;
}

export interface CreateCircuitResponse {
  id: string;
  created: boolean;
  circuit: LibraryCatalogCircuit;
}

// ── Waveform viewer (Analyze view) ──────────────────────────────────────────
// All waveview shapes are backend-owned: one-line aliases over the generated
// OpenAPI types (src/types/README.md adoption pattern). The UI holds no local
// copies — `npm run gen:types` is the single source of truth.

/** One signal's metadata inside an analysis (GET /api/waveview/datasets). */
export type WaveSignalMeta = components["schemas"]["SignalMeta"];
/** One analysis (engine-neutral key, native name, sweep, signals). */
export type WaveAnalysisMeta = components["schemas"]["AnalysisMeta"];
/** An opened dataset (ngspice .raw / Spectre PSF dir) and its analyses. */
export type WaveDatasetMeta = components["schemas"]["DatasetMeta"];
export type WaveDatasetListResponse = components["schemas"]["DatasetListResponse"];
/** Wave data for requested signals (`y` — or `y_re`/`y_im` for fmt=complex). */
export type WaveSignalData = components["schemas"]["WaveSignalData"];
export type WaveResponse = components["schemas"]["WaveResponse"];
export type WaveMeasureRequest = components["schemas"]["MeasureRequest"];
export type WaveMeasureResult = components["schemas"]["MeasureResult"];
export type WaveMeasureResponse = components["schemas"]["MeasureResponse"];
/** Registry discovery surface: measurement name → {kind, required, default_analysis}. */
export type MeasurementInfo = components["schemas"]["MeasurementInfo"];
export type MeasurementCatalogResponse = components["schemas"]["MeasurementCatalogResponse"];
export type WaveScalarsResponse = components["schemas"]["ScalarsResponse"];
export type WaveLogLine = components["schemas"]["LogLineModel"];
export type WaveLogResponse = components["schemas"]["LogResponse"];
export type WaveBrowseEntry = components["schemas"]["BrowseEntry"];
export type WaveBrowseResponse = components["schemas"]["BrowseResponse"];
export type WaveRunInfo = components["schemas"]["RunInfo"];
export type WaveRunListResponse = components["schemas"]["RunListResponse"];
export type WaveRunPruneResponse = components["schemas"]["RunPruneResponse"];
export type WaveSnapshotRequest = components["schemas"]["SnapshotRequest"];
export type WaveSnapshotResponse = components["schemas"]["SnapshotResponse"];
export type WaveRunNetlistRequest = components["schemas"]["RunNetlistRequest"];
export type WaveRunNetlistResponse = components["schemas"]["RunNetlistResponse"];
export type WaveUploadEntry = components["schemas"]["UploadEntry"];
export type WaveUploadListResponse = components["schemas"]["UploadListResponse"];
export type WaveUploadDeletedResponse = components["schemas"]["UploadDeletedResponse"];
export type WaveRunArtifact = components["schemas"]["RunArtifact"];
export type WaveRunArtifactsResponse = components["schemas"]["RunArtifactsResponse"];
export type WaveOpenRequest = components["schemas"]["OpenRequest"];
/** One corner of GET /waveview/runs/{id}/pvt — hand-written until codegen adoption. */
export interface WavePvtCorner {
  corner: string;
  dataset_id: string | null;
  x: (number | null)[] | null;
  y: (number | null)[] | null;
  phase: (number | null)[] | null;
  /** Requested Tier-1 measures per corner (null on failure). */
  metrics: Record<string, number | null>;
  error: string | null;
}
export interface WavePvtGroupResponse {
  run_id: string;
  analysis: string;
  signal: string;
  corners: WavePvtCorner[];
}
export type WaveOpenRunRequest = components["schemas"]["OpenRunRequest"];
/** Staged browser upload (route "4a"): raw artifacts auto-open into `dataset`. */
export type WaveUploadResponse = components["schemas"]["UploadResponse"];
