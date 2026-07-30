// Typed API client — all calls go to the FastAPI backend on :8000
import type {
  AppConfig,
  LoadProjectResponse,
  ValidateResponse,
  ScoreResponse,
  RunStartResponse,
  AlgorithmsInfo,
  CheckpointData,
  CheckpointMeta,
  EnvInfo,
  EnvelopeEntry,
  ScatterPoint,
  SanityCheckResponse,
  SimulateOnceResponse,
  NetlistParseResponse,
  SpecLibraryResponse,
  GenerateProjectResponse,
  ParseProjectResponse,
  WizardForm,
  SensitivityResponse,
  ProjectMeta,
  ProjectDetail,
  ProjectRun,
  ExampleMeta,
  TrashItem,
  XschemFromNetlistRequest,
  XschemSchematicResult,
  LibraryStatus,
  LibraryCatalog,
  LibraryCircuitDetail,
  LibraryResults,
  LibraryClassesResponse,
  LibraryPdksResponse,
  LibrarySchematicSources,
  LibrarySeedProjectResponse,
  LibraryTemplateNetlist,
  LibraryTemplatesResponse,
  LibraryTestbenchNetlist,
  CreateCircuitRequest,
  CreateCircuitResponse,
  WaveDatasetMeta,
  WaveDatasetListResponse,
  WaveResponse,
  WaveMeasureRequest,
  WaveMeasureResponse,
  MeasurementCatalogResponse,
  WaveScalarsResponse,
  WaveLogResponse,
  WaveBrowseResponse,
  WaveRunListResponse,
  WaveRunNetlistRequest,
  WaveRunNetlistResponse,
  WaveRunPruneResponse,
  WaveSnapshotRequest,
  WaveSnapshotResponse,
  WavePvtGroupResponse,
  WaveRunArtifactsResponse,
  WaveOpenRequest,
  WaveOpenRunRequest,
  WaveUploadResponse,
  WaveUploadListResponse,
  WaveUploadDeletedResponse,
} from "@/types/api";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// SSE must NOT go through the Next.js rewrite proxy: that proxy buffers
// `text/event-stream` responses (ignoring the backend's `X-Accel-Buffering: no`),
// so per-trial events arrive in one delayed burst instead of live — making a
// running optimization look frozen. Regular fetches stay same-origin (proxied) for
// portability, but the EventSource connects DIRECTLY to the backend origin.
//
//  • Explicit NEXT_PUBLIC_API_URL set → use it (already a direct backend origin).
//  • Same-origin mode (empty BASE) → derive the backend origin from the current
//    page host + the backend port, so it works wherever the browser runs
//    (localhost, a LAN IP, an SSH-forwarded host). CORS allows any localhost:<port>.
const BACKEND_PORT = process.env.NEXT_PUBLIC_BACKEND_PORT ?? "8000";

function streamBase(): string {
  if (BASE) return BASE;
  if (typeof window === "undefined") return "";
  return `${window.location.protocol}//${window.location.hostname}:${BACKEND_PORT}`;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    let msg = `API error ${res.status}`;
    try {
      const body = await res.json();
      msg = body.detail ?? body.error ?? msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Config
  config: () => req<AppConfig>("/api/config"),

  // Environment — ngspice + IHP PDK probe for graceful degradation (no live runs without PDK)
  env: () => req<EnvInfo>("/api/env"),

  // Project
  loadProject: (yaml_path: string) =>
    req<LoadProjectResponse>("/api/project/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ yaml_path }),
    }),

  // Apply edited/uploaded YAML. Pass yaml_path when the content was edited from a
  // loaded file so the backend anchors relative ws_root/netlist resolution to the
  // original directory (the applied YAML is persisted to a temp file).
  loadProjectContent: (yaml_content: string, yaml_path?: string) =>
    req<LoadProjectResponse>("/api/project/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ yaml_content, yaml_path }),
    }),

  validateYaml: (yaml_content: string) =>
    req<ValidateResponse>("/api/project/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ yaml_content }),
    }),

  // Score shaping
  computeScore: (
    yaml_path: string,
    metric_values: Record<string, number>,
    opts: {
      selectedSpec?: string;
      nCurvePoints?: number;
      /** Ephemeral per-spec edits (what-if); never written to YAML. */
      specOverrides?: Record<string, Record<string, string | number | boolean>>;
    } = {},
  ) =>
    req<ScoreResponse>("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        yaml_path,
        metric_values,
        selected_spec: opts.selectedSpec,
        n_curve_points: opts.nCurvePoints ?? 200,
        spec_overrides: opts.specOverrides,
      }),
    }),

  // Optimization run
  /** Backend-derived algorithm lists for the Run popover (never hardcode these). */
  optimizeAlgorithms: () => req<AlgorithmsInfo>("/api/optimize/algorithms"),

  startRun: (body: {
    yaml_path?: string;
    /** Owning project — the run is isolated under its runs/ dir (report.md P3). */
    project_id?: string;
    label?: string;
    replay?: boolean;
    checkpoint_id?: string;
    budget?: number;
    /** Ephemeral live-run overrides (ignored for replay). */
    algorithm?: string;
    seed?: number;
    /** PVT corner to optimize against (must match a corner in the project's `pvt:`). */
    active_corner?: string;
    /** Autosave a cumulative checkpoint every N trials (live only). */
    autosave_every?: number;
    /** Resume a live run from a saved checkpoint (load + keep_history). */
    resume_checkpoint_id?: string;
    /** Retain per-trial .raw files so the run is openable in the waveform viewer. */
    keep_raw?: boolean;
  }) =>
    req<RunStartResponse>("/api/optimize/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),

  stopRun: (run_id: string) =>
    req<{ ok: boolean }>(`/api/optimize/stop/${run_id}`, { method: "POST" }),

  streamUrl: (run_id: string) => `${streamBase()}/api/optimize/stream/${run_id}`,

  // Checkpoints
  // Pass projectId to scope per-run checkpoints to the active project (presets +
  // unscoped runs are always included); omit it for the global view.
  listCheckpoints: (projectId?: string) =>
    req<{ checkpoints: CheckpointMeta[] }>(
      `/api/checkpoint${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`,
    ).then((r) => r.checkpoints),

  loadCheckpoint: (id: string, limit = 0) =>
    req<CheckpointData>(`/api/checkpoint/${id}?limit=${limit}`),

  // Pass projectId to scope the delete to that project's own runs. `path` targets the EXACT
  // file behind a (deduped) catalog row so the delete can't fan out to a same-named checkpoint
  // in another run/project — checkpoint stems carry no project/run id (BUG-B3).
  deleteCheckpoint: (id: string, projectId?: string, path?: string) => {
    const q = new URLSearchParams();
    if (projectId) q.set("project_id", projectId);
    if (path) q.set("path", path);
    const qs = q.toString();
    return req<{ ok: boolean; deleted: string[] }>(
      `/api/checkpoint/${encodeURIComponent(id)}${qs ? `?${qs}` : ""}`,
      { method: "DELETE" },
    );
  },

  envelope: (id: string, yaml_path?: string) =>
    req<{ envelope: EnvelopeEntry[] }>(
      `/api/checkpoint/${id}/envelope${yaml_path ? `?yaml_path=${encodeURIComponent(yaml_path)}` : ""}`,
    ).then((r) => r.envelope),

  scatter: (id: string, metric_x: string, metric_y: string, yaml_path?: string) =>
    req<{ metric_x: string; metric_y: string; points: ScatterPoint[] }>(
      `/api/checkpoint/${id}/scatter?metric_x=${encodeURIComponent(metric_x)}&metric_y=${encodeURIComponent(metric_y)}${yaml_path ? `&yaml_path=${encodeURIComponent(yaml_path)}` : ""}`,
    ),

  schematicUrl: () => `${BASE}/api/schematic`,

  // URL for the downloadable run-report zip (checkpoint + YAML + summary.md).
  reportUrl: (checkpointId: string, yamlPath?: string) => {
    const q = new URLSearchParams();
    if (yamlPath) q.set("yaml_path", yamlPath);
    const qs = q.toString();
    return `${BASE}/api/checkpoint/${encodeURIComponent(checkpointId)}/report${qs ? `?${qs}` : ""}`;
  },

  sanityCheck: (yaml_path: string, active_corner?: string) =>
    req<SanityCheckResponse>("/api/sanity-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ yaml_path, active_corner }),
    }),

  // Manual single simulation — evaluate ONE chosen design point (live SPICE — needs PDK).
  // Mode B: pass `params` (engineering-real). Mode A: pass `checkpoint_id` (+ optional
  // `point`; omitted → best). `active_corner` optionally overrides the PVT corner.
  simulateOnce: (body: {
    yaml_path: string;
    // Values may be eng-strings ("250u") or numbers; parsed server-side.
    params?: Record<string, string | number>;
    checkpoint_id?: string;
    point?: number;
    active_corner?: string;
    /** Run testbenches × every enabled corner (ephemeral pvt.mode: multi). */
    sweep_corners?: boolean;
    /**
     * Monte Carlo: run N statistical samples of the active corner (mismatch model
     * sections + per-sample RNG seed) — artifacts land as `run_<n>_<tb>__mc<i>`,
     * which Analyze's "Monte Carlo" mode reads. `active_corner` picks the base.
     */
    monte_carlo?: number;
    /** RNG seed of the first MC sample (sample i uses mc_seed0 + i - 1). */
    mc_seed0?: number;
    /** Retain the sim's .raw so the returned run_id opens in the Analyze viewer. */
    keep_raw?: boolean;
  }) =>
    req<SimulateOnceResponse>("/api/simulate/once", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),

  // Finite-difference sensitivity of one spec to DUT params (live SPICE — needs PDK).
  // `params` scopes the sweep (e.g. one device's W/L); `at` overrides the baseline
  // operating point (absolute SI) so the inspector's sliders define the design point.
  specSensitivity: (
    spec: string,
    opts: {
      yaml_path?: string;
      params?: string[];
      at?: Record<string, number>;
      rel_delta?: number;
    } = {},
  ) => {
    const q = new URLSearchParams();
    if (opts.yaml_path) q.set("yaml_path", opts.yaml_path);
    if (opts.params?.length) q.set("params", opts.params.join(","));
    if (opts.at && Object.keys(opts.at).length)
      q.set("at", Object.entries(opts.at).map(([k, v]) => `${k}:${v}`).join(","));
    if (opts.rel_delta != null) q.set("rel_delta", String(opts.rel_delta));
    const qs = q.toString();
    return req<SensitivityResponse>(
      `/api/spec/${encodeURIComponent(spec)}/sensitivity${qs ? `?${qs}` : ""}`,
    );
  },

  // Wizard
  parseNetlist: async (file: File): Promise<NetlistParseResponse> => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${BASE}/api/netlist/parse`, { method: "POST", body: fd });
    if (!res.ok) {
      let msg = `API error ${res.status}`;
      try { const b = await res.json(); msg = b.detail ?? msg; } catch {}
      throw new Error(msg);
    }
    return res.json();
  },

  // Shipped analog-spec templates for the wizard's one-click "Spec library".
  specLibrary: () => req<SpecLibraryResponse>("/api/spec-library"),

  // Projects (report.md P3) — the registry IS WORK_ROOT/projects/.
  listProjects: () => req<{ projects: ProjectMeta[] }>("/api/projects"),
  listExamples: () => req<{ examples: ExampleMeta[] }>("/api/examples"),
  createProject: (name: string, yaml_content?: string) =>
    req<{ id: string }>("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, yaml_content }),
    }),
  fromExample: (example_key: string, name?: string) =>
    req<{ id: string }>("/api/projects/from-example", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ example_key, name }),
    }),
  getProject: (id: string) => req<ProjectDetail>(`/api/projects/${encodeURIComponent(id)}`),
  getProjectRuns: (id: string) =>
    req<{ runs: ProjectRun[] }>(`/api/projects/${encodeURIComponent(id)}/runs`),

  // Lifecycle (report.md P4) — rename keeps the stable dir id; delete is a recoverable
  // MOVE to WORK_ROOT/.trash; fork copies everything except run history.
  renameProject: (id: string, name: string) =>
    req<{ id: string; manifest: Record<string, unknown> }>(
      `/api/projects/${encodeURIComponent(id)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      },
    ),
  forkProject: (id: string, name?: string) =>
    req<{ id: string }>(`/api/projects/${encodeURIComponent(id)}/fork`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    }),
  deleteProject: (id: string) =>
    req<{ ok: boolean; trash_id: string }>(`/api/projects/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),
  listTrash: () => req<{ trash: TrashItem[] }>("/api/trash"),
  purgeTrash: (trashId: string) =>
    req<{ ok: boolean; trash_id: string }>(
      `/api/trash/${encodeURIComponent(trashId)}`,
      { method: "DELETE" },
    ),
  restoreTrash: (trashId: string) =>
    req<{ id: string }>(`/api/trash/${encodeURIComponent(trashId)}/restore`, {
      method: "POST",
    }),
  renameRun: (projectId: string, runId: string, label: string) =>
    req<{ run: ProjectRun }>(
      `/api/projects/${encodeURIComponent(projectId)}/runs/${encodeURIComponent(runId)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label }),
      },
    ),
  deleteRun: (projectId: string, runId: string) =>
    req<{ ok: boolean; trash_id: string }>(
      `/api/projects/${encodeURIComponent(projectId)}/runs/${encodeURIComponent(runId)}`,
      { method: "DELETE" },
    ),

  generateProject: (form: WizardForm, save_path?: string) =>
    req<GenerateProjectResponse>("/api/project/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ form, save_path: save_path ?? null }),
    }),

  parseProjectToForm: (args: { yaml_path?: string; yaml_content?: string }) =>
    req<ParseProjectResponse>("/api/project/parse-to-form", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(args),
    }),

  // Xschem viewer
  xschemFile: (path: string) =>
    req<{ path: string; content: string }>(
      `/api/xschem/file?path=${encodeURIComponent(path)}`,
    ),

  xschemResolve: (ref: string, base?: string) => {
    const q = `ref=${encodeURIComponent(ref)}${base ? `&base=${encodeURIComponent(base)}` : ""}`;
    return req<{ path: string; content: string; resolved_from: string }>(
      `/api/xschem/resolve?${q}`,
    );
  },

  xschemProject: (yaml_path: string) =>
    req<{ xschem_dir: string | null; files: { path: string; name: string }[] }>(
      `/api/xschem/project?yaml_path=${encodeURIComponent(yaml_path)}`,
    ),

  // Generate an xschem schematic from a SPICE netlist (+ optional SVG/PNG render).
  xschemFromNetlist: (body: XschemFromNetlistRequest) =>
    req<XschemSchematicResult>("/api/xschem/from-netlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),

  // Reference Library — the analog-db catalog browser. All data is read from the
  // repo (the optional examples/analog-db submodule); `libraryStatus` gates the UI
  // when the DB is absent (the data calls 503 in that case).
  libraryStatus: () => req<LibraryStatus>("/api/library/status"),
  libraryCatalog: () => req<LibraryCatalog>("/api/library/catalog"),
  libraryCircuit: (id: string) =>
    req<LibraryCircuitDetail>(`/api/library/circuits/${encodeURIComponent(id)}`),
  libraryResults: () => req<LibraryResults>("/api/library/results"),
  libraryClasses: () => req<LibraryClassesResponse>("/api/library/classes"),
  libraryPdks: () => req<LibraryPdksResponse>("/api/library/pdks"),
  libraryTemplates: () => req<LibraryTemplatesResponse>("/api/library/templates"),
  libraryTemplateNetlist: (id: string) =>
    req<LibraryTemplateNetlist>(
      `/api/library/templates/${encodeURIComponent(id)}/netlist`,
    ),
  librarySchematicSources: (circuitId: string) =>
    req<LibrarySchematicSources>(
      `/api/library/circuits/${encodeURIComponent(circuitId)}/schematic-sources`,
    ),
  libraryStartProject: (circuitId: string, body: { name?: string | null; pdk?: string | null } = {}) =>
    req<LibrarySeedProjectResponse>(
      `/api/library/circuits/${encodeURIComponent(circuitId)}/project`,
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
    ),
  // engine ids come from the DB (a bench profile's `engines`) — the route 400s unknown ones
  libraryTestbenchNetlist: (classId: string, name: string, engine: string = "ngspice") =>
    req<LibraryTestbenchNetlist>(
      `/api/library/testbenches/${encodeURIComponent(classId)}/${encodeURIComponent(name)}/netlist?engine=${encodeURIComponent(engine)}`,
    ),
  createCircuit: (payload: CreateCircuitRequest) =>
    req<CreateCircuitResponse>("/api/library/circuits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  // Waveform viewer (Analyze view) — spicexplorer-waveview over /api/waveview/*.
  // Datasets are opened by absolute path (whitelisted server-side) or by run id;
  // DELETE only evicts the in-memory dataset, it never touches files on disk.
  waveviewMeasurements: () =>
    req<MeasurementCatalogResponse>("/api/waveview/measurements"),
  waveviewOpen: (body: WaveOpenRequest) =>
    req<WaveDatasetMeta>("/api/waveview/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  waveviewOpenRun: (body: WaveOpenRunRequest) =>
    req<WaveDatasetMeta>("/api/waveview/open_run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  waveviewDatasets: () => req<WaveDatasetListResponse>("/api/waveview/datasets"),
  waveviewClose: (datasetId: string) =>
    req<{ closed: boolean }>(
      `/api/waveview/datasets/${encodeURIComponent(datasetId)}`,
      { method: "DELETE" },
    ),
  // `signals` is mandatory on the backend (no signals → 422); the store always
  // sends an explicit selection derived from the dataset's own signal list.
  waveviewWave: (
    datasetId: string,
    opts: {
      analysis: string;
      signals: string[];
      x?: string;
      fmt?: string;
      max_points?: number;
      method?: string;
    },
  ) => {
    const q = new URLSearchParams();
    q.set("analysis", opts.analysis);
    q.set("signals", opts.signals.join(","));
    if (opts.x) q.set("x", opts.x);
    if (opts.fmt) q.set("fmt", opts.fmt);
    if (opts.max_points != null) q.set("max_points", String(opts.max_points));
    if (opts.method) q.set("method", opts.method);
    return req<WaveResponse>(
      `/api/waveview/datasets/${encodeURIComponent(datasetId)}/wave?${q.toString()}`,
    );
  },
  waveviewMeasure: (datasetId: string, body: WaveMeasureRequest) =>
    req<WaveMeasureResponse>(
      `/api/waveview/datasets/${encodeURIComponent(datasetId)}/measure`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
    ),
  waveviewScalars: (datasetId: string, analysis = "op") =>
    req<WaveScalarsResponse>(
      `/api/waveview/datasets/${encodeURIComponent(datasetId)}/scalars?analysis=${encodeURIComponent(analysis)}`,
    ),
  waveviewLog: (datasetId: string, tail = 2000) =>
    req<WaveLogResponse>(
      `/api/waveview/datasets/${encodeURIComponent(datasetId)}/log?tail=${tail}`,
    ),
  waveviewRuns: (projectId?: string) =>
    req<WaveRunListResponse>(
      `/api/waveview/runs${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`,
    ),
  // Corner-grouped wave for a run's __<corner> artifacts (the viewer's PVT mode).
  waveviewPvtGroup: (
    runId: string,
    q: {
      analysis: string;
      signal: string;
      fmt?: string;
      phase?: boolean;
      meas?: string[];
      out?: string;
      match?: string;
      project_id?: string | null;
      max_points?: number;
    },
  ) => {
    const p = new URLSearchParams({ analysis: q.analysis, signal: q.signal });
    if (q.fmt) p.set("fmt", q.fmt);
    if (q.phase) p.set("phase", "true");
    if (q.meas?.length) p.set("meas", q.meas.join(","));
    if (q.out) p.set("out", q.out);
    if (q.match) p.set("match", q.match);
    if (q.project_id) p.set("project_id", q.project_id);
    if (q.max_points) p.set("max_points", String(q.max_points));
    return req<WavePvtGroupResponse>(
      `/api/waveview/runs/${encodeURIComponent(runId)}/pvt?${p.toString()}`,
    );
  },
  waveviewRunArtifacts: (runId: string, projectId?: string) =>
    req<WaveRunArtifactsResponse>(
      `/api/waveview/runs/${encodeURIComponent(runId)}/artifacts${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`,
    ),
  waveviewBrowse: (dir: string, limit = 500) =>
    req<WaveBrowseResponse>(
      `/api/waveview/browse?dir=${encodeURIComponent(dir)}&limit=${limit}`,
    ),

  // Enforce metrics_only retention on a finished run: drops sim/ waveforms,
  // keeps the record; idempotent, refuses running runs (skipped reason).
  waveviewPruneRun: (runId: string) =>
    req<WaveRunPruneResponse>(
      `/api/waveview/runs/${encodeURIComponent(runId)}/prune`,
      { method: "POST" },
    ),
  // Persist a client-rendered plot PNG into the run's own dir (snapshots/<name>.png);
  // serve it back via …/artifacts/file?rel= (the Library thumbnail path).
  waveviewSaveSnapshot: (runId: string, body: WaveSnapshotRequest) =>
    req<WaveSnapshotResponse>(
      `/api/waveview/runs/${encodeURIComponent(runId)}/snapshot`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
    ),
  // Run a SELF-CONTAINED ngspice deck as a first-class `kind: netlist` run and
  // open its newest raw (the drop-zone's "4a"). 422 keeps the run for log triage.
  waveviewRunNetlist: (body: WaveRunNetlistRequest) =>
    req<WaveRunNetlistResponse>("/api/waveview/run_netlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  waveviewUploads: () => req<WaveUploadListResponse>("/api/waveview/uploads"),
  waveviewDeleteUpload: (uploadId: string) =>
    req<WaveUploadDeletedResponse>(
      `/api/waveview/uploads/${encodeURIComponent(uploadId)}`,
      { method: "DELETE" },
    ),

  // Stage a result artifact from the browser (.raw / Spectre-PSF .zip / log);
  // raw artifacts auto-open server-side. Multipart, so no JSON header.
  waveviewUpload: async (file: File): Promise<WaveUploadResponse> => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${BASE}/api/waveview/upload`, { method: "POST", body: fd });
    if (!res.ok) {
      let msg = `API error ${res.status}`;
      try { const b = await res.json(); msg = b.detail ?? msg; } catch {}
      throw new Error(msg);
    }
    return res.json();
  },

  // SSE live tail of a simulator log — direct backend origin (see streamBase note):
  // the Next proxy buffers text/event-stream. Keyed by log *path* (whitelisted),
  // not dataset id.
  waveviewLogStreamUrl: (path: string, fromLine = 0) =>
    `${streamBase()}/api/waveview/log/stream?path=${encodeURIComponent(path)}&from_line=${fromLine}`,
};

/** Direct URL to a circuit's schematic SVG (for an `<img>`/`<object>` src), by mode.
 *  The backend serves `image/svg+xml`; only modes present in the detail's `schematics`
 *  map resolve (others 404). Uses the same backend origin as `streamBase()`. */
export function librarySchematicUrl(id: string, mode: string): string {
  const origin = BASE || streamBase();
  return `${origin}/api/library/circuits/${encodeURIComponent(id)}/schematic?mode=${encodeURIComponent(mode)}`;
}

/** Direct URL to a functional template's committed PNG render (for an `<img>` src). The
 *  backend serves `image/png`; templates without a render 404 (the `/library/templates`
 *  list's `image` field / the view type's `hasImage` says which have one). */
export function libraryTemplateImageUrl(id: string): string {
  const origin = BASE || streamBase();
  return `${origin}/api/library/templates/${encodeURIComponent(id)}/image`;
}

/** Direct URL to one displayable hand-drawn/paper reference image (for an `<img>` src).
 *  `name` is the reference-dir-relative path from `librarySchematicSources`. */
export function libraryReferenceImageUrl(circuitId: string, name: string): string {
  const origin = BASE || streamBase();
  return `${origin}/api/library/circuits/${encodeURIComponent(circuitId)}/reference-image?name=${encodeURIComponent(name)}`;
}
