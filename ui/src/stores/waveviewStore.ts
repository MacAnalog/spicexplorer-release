import { create } from "zustand";
import { api } from "@/lib/api";
import { useRunStore } from "@/stores/runStore";
import type {
  MeasurementCatalogResponse,
  WaveBrowseResponse,
  WaveDatasetMeta,
  WaveLogLine,
  WaveMeasureResult,
  WaveResponse,
  WaveRunInfo,
  WaveScalarsResponse,
  WaveUploadEntry,
} from "@/types/api";
import {
  baseAnalysis,
  buildMeasureItems,
  defaultSignals,
  guessOutSignal,
  isDbNativeSignal,
  orderedAnalyses,
  parseDownsample,
  plotStyleFor,
} from "@/lib/waveview/selectors";
import {
  cornerColor,
  cornersInArtifacts,
  headlineFor,
  isMcCorner,
  isNominalCorner,
  sweepResidueIds,
  tbMatchFromPath,
  type SweepMode,
} from "@/lib/waveview/sweep";

/** Signal-selection key: one saved selection per dataset+analysis. */
const selKey = (dsId: string, analysis: string) => `${dsId}::${analysis}`;

// The SSE log tail lives OUTSIDE React state (runStore convention): an
// EventSource isn't serializable and must survive re-renders; the store only
// mirrors the received lines.
let logEs: EventSource | null = null;
// Monotonic tokens so a slow response can't clobber a newer selection — one per
// independent fetch family (review finding: the log/measure/scalar paths had no
// token, so rapid dataset switches leaked EventSources and wiped fresh results).
let waveSeq = 0;
let logSeq = 0;
let measureSeq = 0;
let scalarSeq = 0;

/** In-memory cap for the streamed log tail (the full log stays on disk). */
const LOG_CAP = 400;

/** Max raw artifacts the server merges per opened run (guards a huge sweep run).
 *  Must cover a full bench suite — the server merges ONE member per testbench
 *  (5T-OTA-ADVANCED has 7; 6 silently dropped the noise bench → Vn n/a). */
const MAX_RUN_DATASETS = 12;

/** Caps on per-corner / per-sample datasets a sweep mode auto-opens. */
const MAX_PVT_CORNERS = 12;
const MAX_MC_SAMPLES = 32;

/** run_id::corner → dataset_id for corner datasets already opened this session. */
const cornerDsCache = new Map<string, string>();
let sweepSeq = 0;

/** One PVT corner (or MC sample) resolved to its own opened dataset. */
export interface SweepMember {
  key: string;
  name: string;
  datasetId: string;
  nominal: boolean;
  color: string;
}

/** The corner/sample's fetched curve for the active analysis. */
export interface SweepWave {
  x: number[];
  y: number[];
  phase: number[] | null;
}

interface WaveviewStore {
  // Backend-owned data
  catalog: MeasurementCatalogResponse | null;
  datasets: WaveDatasetMeta[];
  runs: WaveRunInfo[];
  browse: WaveBrowseResponse | null;

  // Selection
  activeId: string | null;
  activeAnalysis: string | null;
  /** Dataset overlaid (dashed) on the active plot, e.g. a golden reference. */
  overlayId: string | null;
  expanded: Record<string, boolean>;
  selected: Record<string, string[]>;

  // Wave data for the active dataset+analysis
  wave: WaveResponse | null;
  /** Second axis (phase) for dual (Bode) analyses. */
  wavePhase: WaveResponse | null;
  overlayWave: WaveResponse | null;
  waveStatus: "idle" | "loading" | "ready" | "error";
  waveError: string | null;

  // Plot params (presentation + /wave query)
  /** null = the analysis' own default from ANALYSIS_PLOT. */
  xScale: "log" | "lin" | null;
  fmt: string;
  downsample: string;
  railOpen: boolean;

  // Sweep modes (the handoff's Single / PVT corners / Monte Carlo segmented).
  // PVT/MC members are REAL per-corner datasets discovered from the active
  // run's artifact naming (`…__<corner>/`) and opened via POST /open_run.
  sweepMode: SweepMode;
  sweepMembers: SweepMember[];
  sweepWaves: Record<string, SweepWave>;
  sweepMetrics: Record<string, number | null>;
  sweepStatus: "idle" | "loading" | "empty" | "ready" | "error";
  sweepError: string | null;
  /** Corner key → measured UGF (Bode sweeps; drives the PVT plot annotation). */
  sweepUgfs: Record<string, number | null>;
  /** Corner key → user toggle (unset = enabled). */
  cornerEnabled: Record<string, boolean>;
  /** MC band half-width in σ (the ±1σ/±2σ/±3σ segmented). */
  mcSigma: number;
  /** Dataset ids the sweep machinery opened for itself — hidden from the tree
   *  (8 corners must not flood it; the rail's corner list is their surface). */
  sweepDatasetIds: string[];

  // Tier-1 measures (dataset-wide composite)
  outSignal: string | null;
  measures: WaveMeasureResult[] | null;

  // OP scalars
  scalars: WaveScalarsResponse | null;

  // Simulator log
  logLines: WaveLogLine[];
  logCounts: Record<string, number>;
  logOpen: boolean;
  logStreaming: boolean;

  // Open/Import modal
  importOpen: boolean;
  importBusy: boolean;
  importError: string | null;
  /** A keep_raw run to auto-open when its live stream ends. Store-owned (not
   *  modal-local) so closing the modal or leaving Analyze mid-run keeps the
   *  promise — the runStore subscription below fires regardless of what's mounted. */
  pendingOpenRunId: string | null;

  status: "idle" | "loading" | "ready" | "error";
  error: string | null;

  init: () => Promise<void>;
  openPath: (path: string) => Promise<boolean>;
  openRun: (runId: string, projectId?: string) => Promise<boolean>;
  uploadFile: (file: File) => Promise<boolean>;
  closeDataset: (dsId: string) => Promise<void>;
  setActive: (dsId: string, analysis?: string) => void;
  setAnalysis: (analysis: string) => void;
  toggleExpanded: (dsId: string) => void;
  toggleSignal: (dsId: string, analysis: string, name: string) => void;
  setOverlay: (dsId: string | null) => void;
  setOutSignal: (name: string) => void;
  setXScale: (v: "log" | "lin" | null) => void;
  setFmt: (v: string) => void;
  setDownsample: (v: string) => void;
  setSweepMode: (m: SweepMode) => void;
  toggleCorner: (key: string) => void;
  setMcSigma: (k: number) => void;
  refreshSweep: () => Promise<void>;
  toggleRail: () => void;
  toggleLogOpen: () => void;
  loadRuns: () => Promise<void>;
  loadBrowse: (dir: string) => Promise<void>;
  /** Staged browser uploads (the Open/Import upload tab's manager list). */
  uploads: WaveUploadEntry[];
  loadUploads: () => Promise<void>;
  deleteUpload: (uploadId: string) => Promise<void>;
  /** Enforce metrics_only retention on a run (drops sim/ raws; idempotent).
   *  Returns the server's skip reason, or null when pruning happened. */
  pruneRun: (runId: string) => Promise<string | null>;
  openImport: () => void;
  closeImport: () => void;
  setPendingOpenRun: (runId: string | null) => void;
  refreshWave: () => Promise<void>;
  refreshMeasures: () => Promise<void>;
  refreshScalars: () => Promise<void>;
}

export const useWaveviewStore = create<WaveviewStore>((set, get) => {
  /** Saved-or-default signal selection for a dataset+analysis. A Bode (dual)
   *  analysis defaults to the primary output only — an AC raw carries derived
   *  vectors (out_mag, dcgain, …) that turn the plot into spaghetti. */
  const signalsFor = (ds: WaveDatasetMeta, analysis: string): string[] => {
    const saved = get().selected[selKey(ds.dataset_id, analysis)];
    if (saved) return saved;
    const meta = ds.analyses.find((a) => a.analysis === analysis);
    if (!meta) return [];
    return defaultSignals(meta, plotStyleFor(analysis).dual ? 1 : 4);
  };

  const activeDataset = (): WaveDatasetMeta | undefined =>
    get().datasets.find((d) => d.dataset_id === get().activeId);

  /** (Re)start the SSE tail on the active dataset's log. */
  const restartLogStream = (ds: WaveDatasetMeta | undefined) => {
    // The seq token — not just the active-dataset check — gates the async tail:
    // two in-flight snapshot fetches for the SAME dataset would otherwise both
    // pass the id check and each open an EventSource, orphaning the first.
    const seq = ++logSeq;
    logEs?.close();
    logEs = null;
    set({ logLines: [], logCounts: {}, logStreaming: false });
    if (!ds?.log_path) return;
    const path = ds.log_path;
    // Parsed snapshot first (level counts for the bar), then follow via SSE.
    void api
      .waveviewLog(ds.dataset_id)
      .then((res) => {
        if (seq !== logSeq || activeDataset()?.dataset_id !== ds.dataset_id) return;
        set({
          logCounts: res.counts,
          logLines: res.lines.slice(-LOG_CAP),
        });
        const source = new EventSource(api.waveviewLogStreamUrl(path, res.n_lines));
        logEs = source;
        set({ logStreaming: true });
        source.onmessage = (ev) => {
          try {
            const line = JSON.parse(ev.data) as WaveLogLine;
            set((s) => ({
              logLines: [...s.logLines, line].slice(-LOG_CAP),
              logCounts: {
                ...s.logCounts,
                [line.level]: (s.logCounts[line.level] ?? 0) + 1,
              },
            }));
          } catch {
            // ignore non-JSON keepalives
          }
        };
        source.onerror = () => {
          // EventSource auto-reconnects; only mark closed when it gave up.
          if (source.readyState === EventSource.CLOSED) set({ logStreaming: false });
        };
      })
      .catch(() => {
        if (seq === logSeq) set({ logCounts: {}, logLines: [] });
      });
  };

  /** Re-sync the dataset registry after a server-side eviction (prune / upload
   *  delete): datasets whose files went away vanish from the server list, so the
   *  local tree, overlay, and active selection must follow. */
  const resyncAfterEviction = async () => {
    const list = await api.waveviewDatasets();
    const ids = new Set(list.datasets.map((d) => d.dataset_id));
    set((s) => ({
      datasets: list.datasets,
      overlayId: s.overlayId && ids.has(s.overlayId) ? s.overlayId : null,
      overlayWave: s.overlayId && ids.has(s.overlayId) ? s.overlayWave : null,
    }));
    const { activeId } = get();
    if (activeId && !ids.has(activeId)) {
      const next = list.datasets[0];
      if (next) {
        get().setActive(next.dataset_id, orderedAnalyses(next)[0]?.analysis);
      } else {
        set({
          activeId: null,
          activeAnalysis: null,
          wave: null,
          wavePhase: null,
          overlayWave: null,
          measures: [],
        });
      }
    }
  };

  const afterOpen = (meta: WaveDatasetMeta, activate = true) => {
    set((s) => ({
      datasets: [
        ...s.datasets.filter((d) => d.dataset_id !== meta.dataset_id),
        meta,
      ],
      // auto-expand only what the user opened — sweep-opened corner datasets
      // stay collapsed so 8 corners don't flood the tree
      expanded: activate ? { ...s.expanded, [meta.dataset_id]: true } : s.expanded,
      importOpen: false,
      importBusy: false,
      importError: null,
    }));
    if (activate) {
      const first = orderedAnalyses(meta)[0];
      get().setActive(meta.dataset_id, first?.analysis);
    }
  };

  return {
    catalog: null,
    datasets: [],
    runs: [],
    browse: null,
    activeId: null,
    activeAnalysis: null,
    overlayId: null,
    expanded: {},
    selected: {},
    wave: null,
    wavePhase: null,
    overlayWave: null,
    waveStatus: "idle",
    waveError: null,
    xScale: null,
    fmt: "auto",
    downsample: "minmax:4000",
    railOpen: true,
    sweepMode: "single" as SweepMode,
    sweepMembers: [],
    sweepWaves: {},
    sweepMetrics: {},
    sweepStatus: "idle" as const,
    sweepError: null,
    sweepUgfs: {},
    cornerEnabled: {},
    mcSigma: 3,
    sweepDatasetIds: [],
    outSignal: null,
    measures: null,
    scalars: null,
    logLines: [],
    logCounts: {},
    logOpen: false,
    logStreaming: false,
    importOpen: false,
    importBusy: false,
    importError: null,
    pendingOpenRunId: null,
    status: "idle",
    error: null,

    init: async () => {
      if (get().status === "loading") return;
      set({ status: "loading", error: null });
      try {
        const [catalog, list] = await Promise.all([
          api.waveviewMeasurements(),
          api.waveviewDatasets(),
        ]);
        // Server-registered corner groups from an earlier session's sweep start
        // hidden — the sweep rail (not the tree) is their surface.
        const residue = sweepResidueIds(list.datasets);
        set((s) => ({
          catalog,
          datasets: list.datasets,
          status: "ready",
          sweepDatasetIds: [...new Set([...s.sweepDatasetIds, ...residue])],
        }));
        const { activeId } = get();
        if (!activeId && list.datasets.length) {
          const first =
            list.datasets.find((d) => !residue.includes(d.dataset_id)) ??
            list.datasets[0];
          get().setActive(
            first.dataset_id,
            orderedAnalyses(first)[0]?.analysis,
          );
        }
      } catch (err) {
        set({
          status: "error",
          error: err instanceof Error ? err.message : "Failed to reach /api/waveview",
        });
      }
    },

    openPath: async (path) => {
      set({ importBusy: true, importError: null });
      try {
        afterOpen(await api.waveviewOpen({ path }));
        return true;
      } catch (err) {
        set({
          importBusy: false,
          importError: err instanceof Error ? err.message : "Failed to open path",
        });
        return false;
      }
    },

    openRun: async (runId, projectId) => {
      set({ importBusy: true, importError: null });
      try {
        // A run usually carries one raw PER TESTBENCH (ac + tran + noise …).
        // The server merges the newest raws into ONE multi-analysis dataset —
        // one tree entry whose tabs are the whole run; duplicate analysis keys
        // come back suffixed ("ac#2") and every config lookup uses the base key.
        afterOpen(
          await api.waveviewOpenRun({
            run_id: runId,
            project_id: projectId ?? null,
            merge: true,
            limit: MAX_RUN_DATASETS,
          }),
        );
        return true;
      } catch (err) {
        set({
          importBusy: false,
          importError: err instanceof Error ? err.message : "Failed to open run",
        });
        return false;
      }
    },

    uploadFile: async (file) => {
      set({ importBusy: true, importError: null });
      try {
        // A netlist isn't a result artifact — it RUNS: the drop-zone's "4a".
        // The deck becomes a first-class `kind: netlist` run server-side and
        // its newest raw opens like any other dataset.
        if (/\.(spice|cir|net|sp)$/i.test(file.name)) {
          const res = await api.waveviewRunNetlist({
            content: await file.text(),
            filename: file.name,
          });
          afterOpen(res.dataset);
          void get().loadRuns(); // the new netlist run shows up in "from run"
          return true;
        }
        const res = await api.waveviewUpload(file);
        if (res.dataset) {
          afterOpen(res.dataset);
        } else {
          set({
            importBusy: false,
            importError: `${file.name} staged (${res.kind}) — no waveform dataset to open.`,
          });
        }
        return true;
      } catch (err) {
        set({
          importBusy: false,
          importError: err instanceof Error ? err.message : "Upload failed",
        });
        return false;
      }
    },

    closeDataset: async (dsId) => {
      try {
        await api.waveviewClose(dsId);
      } catch {
        // eviction is idempotent — a 404 just means it's already gone
      }
      set((s) => ({
        datasets: s.datasets.filter((d) => d.dataset_id !== dsId),
        overlayId: s.overlayId === dsId ? null : s.overlayId,
        // drop the closed overlay's traces immediately — otherwise its dashed
        // ghost stays on the plot until some unrelated refresh
        overlayWave: s.overlayId === dsId ? null : s.overlayWave,
      }));
      if (get().activeId === dsId) {
        const next = get().datasets[0];
        if (next) {
          get().setActive(next.dataset_id, orderedAnalyses(next)[0]?.analysis);
        } else {
          logEs?.close();
          logEs = null;
          set({
            activeId: null,
            activeAnalysis: null,
            wave: null,
            wavePhase: null,
            overlayWave: null,
            measures: null,
            scalars: null,
            logLines: [],
            logCounts: {},
            logStreaming: false,
            waveStatus: "idle",
          });
        }
      }
    },

    setActive: (dsId, analysis) => {
      const ds = get().datasets.find((d) => d.dataset_id === dsId);
      if (!ds) return;
      const prevId = get().activeId;
      const nextAnalysis =
        analysis ??
        (prevId === dsId ? get().activeAnalysis : null) ??
        orderedAnalyses(ds)[0]?.analysis ??
        null;
      set((s) => ({
        activeId: dsId,
        activeAnalysis: nextAnalysis,
        expanded: { ...s.expanded, [dsId]: true },
        // out signal follows the dataset unless the user already picked one for it
        outSignal: prevId === dsId ? s.outSignal : guessOutSignal(ds),
        scalars: prevId === dsId ? s.scalars : null,
        measures: prevId === dsId ? s.measures : null,
      }));
      if (prevId !== dsId) {
        restartLogStream(ds);
        void get().refreshMeasures();
      }
      void get().refreshWave();
      if (get().sweepMode !== "single") void get().refreshSweep();
      if (nextAnalysis === "op") void get().refreshScalars();
    },

    setAnalysis: (analysis) => {
      const { activeId } = get();
      if (!activeId) return;
      get().setActive(activeId, analysis);
    },

    toggleExpanded: (dsId) =>
      set((s) => ({ expanded: { ...s.expanded, [dsId]: !s.expanded[dsId] } })),

    toggleSignal: (dsId, analysis, name) => {
      const ds = get().datasets.find((d) => d.dataset_id === dsId);
      if (!ds) return;
      const current = signalsFor(ds, analysis);
      const next = current.includes(name)
        ? current.filter((n) => n !== name)
        : [...current, name];
      set((s) => ({ selected: { ...s.selected, [selKey(dsId, analysis)]: next } }));
      if (get().activeId === dsId && get().activeAnalysis === analysis) {
        void get().refreshWave();
      }
    },

    setOverlay: (dsId) => {
      set({ overlayId: dsId });
      void get().refreshWave();
    },

    setOutSignal: (name) => {
      set({ outSignal: name });
      void get().refreshMeasures();
    },

    setXScale: (v) => set({ xScale: v }),
    setFmt: (v) => {
      set({ fmt: v });
      void get().refreshWave();
    },
    setDownsample: (v) => {
      set({ downsample: v });
      void get().refreshWave();
    },

    setSweepMode: (m) => {
      set({ sweepMode: m });
      void get().refreshSweep();
    },
    toggleCorner: (key) =>
      set((s) => ({
        cornerEnabled: { ...s.cornerEnabled, [key]: !(s.cornerEnabled[key] ?? true) },
      })),
    setMcSigma: (k) => set({ mcSigma: k }),

    /**
     * Discover + load the active run's corner/sample datasets for the current
     * sweep mode: run artifacts → `__<corner>` names → one merged dataset per
     * corner (POST /open_run match=) → per-corner wave + headline metric.
     */
    refreshSweep: async () => {
      const seq = ++sweepSeq;
      const mode = get().sweepMode;
      const clear = {
        sweepMembers: [] as SweepMember[],
        sweepWaves: {} as Record<string, SweepWave>,
        sweepMetrics: {} as Record<string, number | null>,
        sweepUgfs: {} as Record<string, number | null>,
        sweepError: null as string | null,
      };
      if (mode === "single") {
        set({ ...clear, sweepStatus: "idle" });
        return;
      }
      const ds = activeDataset();
      const analysis = get().activeAnalysis;
      if (!ds || !analysis || baseAnalysis(analysis) === "op") {
        set({ ...clear, sweepStatus: "empty" });
        return;
      }
      set({ sweepStatus: "loading", sweepError: null });
      try {
        let runs = get().runs;
        if (!runs.length) {
          runs = (await api.waveviewRuns()).runs;
          if (seq !== sweepSeq) return;
          set({ runs });
        }
        const run = runs.find(
          (r) => ds.path === r.run_dir || ds.path.startsWith(`${r.run_dir}/`),
        );
        if (!run) {
          set({ ...clear, sweepStatus: "empty" });
          return;
        }

        const primarySignal = signalsFor(ds, analysis)[0];
        const isDual = !!plotStyleFor(analysis).dual;
        // a deck-computed `*_db_curve` primary is already in dB: fetch its real
        // part (fmt=re — AC vectors are stored complex; auto/mag_db double-log),
        // and skip its meaningless phase
        const primaryDb = !!primarySignal && isDbNativeSignal(primarySignal);
        const head = headlineFor(baseAnalysis(analysis), get().catalog);
        const outSig = get().outSignal;

        // ---- Preferred path: ONE corner-grouped call (GET /runs/{id}/pvt — the
        // handoff's ?group=pvt). Falls back to per-corner client orchestration
        // below when the backend predates the route.
        if (primarySignal) {
          try {
            const activeMeta = ds.analyses.find((a) => a.analysis === analysis);
            const res = await api.waveviewPvtGroup(run.run_id, {
              analysis: baseAnalysis(analysis),
              signal: primarySignal,
              fmt: isDual ? (primaryDb ? "re" : "mag_db") : get().fmt,
              phase: isDual && !primaryDb,
              meas: head
                ? [head.meas, ...(isDual && head.meas !== "ugf" ? ["ugf"] : [])]
                : [],
              out: outSig ?? undefined,
              match:
                tbMatchFromPath(ds.path) ??
                tbMatchFromPath(activeMeta?.native_name ?? "") ??
                undefined,
              project_id: run.project_id ?? undefined,
              max_points: 1500,
            });
            if (seq !== sweepSeq) return;
            const wanted = res.corners
              .filter((c) => (mode === "pvt" ? !isMcCorner(c.corner) : isMcCorner(c.corner)))
              .slice(0, mode === "pvt" ? MAX_PVT_CORNERS : MAX_MC_SAMPLES);
            if (!wanted.length) {
              set({ ...clear, sweepStatus: "empty" });
              return;
            }
            const members: SweepMember[] = [];
            const waves: Record<string, SweepWave> = {};
            const metrics: Record<string, number | null> = {};
            const ugfs: Record<string, number | null> = {};
            const hidden: string[] = [];
            wanted.forEach((c, i) => {
              members.push({
                key: c.corner,
                name: c.corner.replace(/_/g, "·"),
                datasetId: c.dataset_id ?? "",
                nominal: mode === "pvt" && (isNominalCorner(c.corner) || i === 0),
                color: cornerColor(c.corner, Math.max(0, i - 1)),
              });
              if (c.dataset_id) hidden.push(c.dataset_id);
              if (c.x && c.y) {
                waves[c.corner] = {
                  x: c.x.map((v) => v ?? NaN),
                  y: c.y.map((v) => v ?? NaN),
                  phase: c.phase ? c.phase.map((v) => v ?? NaN) : null,
                };
              }
              if (head) {
                metrics[c.corner] = c.metrics[head.meas] ?? null;
                ugfs[c.corner] = c.metrics.ugf ?? null;
              }
            });
            set((state) => ({
              sweepMembers: members,
              sweepWaves: waves,
              sweepMetrics: metrics,
              sweepUgfs: ugfs,
              sweepDatasetIds: [...new Set([...state.sweepDatasetIds, ...hidden])],
              sweepStatus: "ready",
              sweepError: null,
            }));
            return;
          } catch (err) {
            if (seq !== sweepSeq) return;
            // "no per-corner artifacts" is a real empty; anything else (route
            // missing on an older backend) drops to the client-side flow.
            if (err instanceof Error && /no per-corner artifacts/i.test(err.message)) {
              set({ ...clear, sweepStatus: "empty" });
              return;
            }
          }
        }

        const arts = await api.waveviewRunArtifacts(
          run.run_id,
          run.project_id ?? undefined,
        );
        if (seq !== sweepSeq) return;
        const all = cornersInArtifacts(arts.artifacts);
        const names =
          mode === "pvt" ? all.filter((c) => !isMcCorner(c)) : all.filter(isMcCorner);
        if (!names.length) {
          set({ ...clear, sweepStatus: "empty" });
          return;
        }
        const capped = names.slice(0, mode === "pvt" ? MAX_PVT_CORNERS : MAX_MC_SAMPLES);

        // One merged dataset per corner, cached per run for the session.
        const opened = await Promise.all(
          capped.map(async (c, i): Promise<SweepMember | null> => {
            const cacheKey = `${run.run_id}::${c}`;
            let datasetId = cornerDsCache.get(cacheKey) ?? null;
            if (datasetId && !get().datasets.some((d) => d.dataset_id === datasetId)) {
              datasetId = null; // was closed — reopen
            }
            if (!datasetId) {
              try {
                // merge:false — the newest artifact matching the corner opens as
                // exactly ONE dataset (a merged open would also register every
                // member raw and flood the tree with 3× datasets per corner).
                const meta = await api.waveviewOpenRun({
                  run_id: run.run_id,
                  project_id: run.project_id ?? null,
                  match: `__${c}`,
                  merge: false,
                  limit: 1,
                });
                datasetId = meta.dataset_id;
                cornerDsCache.set(cacheKey, datasetId);
                afterOpen(meta, false);
              } catch {
                return null;
              }
            }
            return {
              key: c,
              name: c.replace(/_/g, "·"),
              datasetId,
              nominal: mode === "pvt" && (isNominalCorner(c) || i === 0),
              color: cornerColor(c, Math.max(0, i - 1)),
            };
          }),
        );
        if (seq !== sweepSeq) return;
        const members = opened.filter((m): m is SweepMember => m !== null);
        // every dataset the sweep machinery has ever opened stays hidden from
        // the tree (session-wide — the cache may resurface them on re-entry)
        set({ sweepDatasetIds: [...cornerDsCache.values()] });
        if (!members.length) {
          set({ ...clear, sweepStatus: "empty" });
          return;
        }

        // Per-corner curve (primary signal) + headline metric — all parallel.
        const primary = signalsFor(ds, analysis)[0];
        const dual = !!plotStyleFor(analysis).dual;
        const headline = headlineFor(baseAnalysis(analysis), get().catalog);
        const out = get().outSignal;
        const waves: Record<string, SweepWave> = {};
        const metrics: Record<string, number | null> = {};
        const fetchWave = async (datasetId: string, fmt: string) => {
          const base = {
            signals: primary ? [primary] : [],
            fmt,
            method: "minmax",
            max_points: 1500,
          };
          try {
            return await api.waveviewWave(datasetId, { ...base, analysis });
          } catch {
            // a per-corner merge may carry the un-suffixed analysis key
            return api.waveviewWave(datasetId, { ...base, analysis: baseAnalysis(analysis) });
          }
        };
        await Promise.all(
          members.map(async (m) => {
            if (primary) {
              try {
                const db = isDbNativeSignal(primary);
                const wave = await fetchWave(m.datasetId, dual ? (db ? "re" : "mag_db") : get().fmt);
                const phase = dual && !db ? await fetchWave(m.datasetId, "phase_deg") : null;
                const sig = wave.signals[0];
                if (sig && Array.isArray(sig.y)) {
                  waves[m.key] = {
                    x: sig.x,
                    y: sig.y as number[],
                    phase:
                      phase?.signals[0] && Array.isArray(phase.signals[0].y)
                        ? (phase.signals[0].y as number[])
                        : null,
                  };
                }
              } catch {
                // corner curve unavailable — the rail still lists the corner
              }
            }
            if (headline && out) {
              try {
                const res = await api.waveviewMeasure(m.datasetId, {
                  items: [{ name: headline.meas, recipe: { meas: headline.meas, out } }],
                });
                metrics[m.key] = res.results[0]?.value ?? null;
              } catch {
                metrics[m.key] = null;
              }
            }
          }),
        );
        if (seq !== sweepSeq) return;
        set({
          sweepMembers: members,
          sweepWaves: waves,
          sweepMetrics: metrics,
          sweepStatus: "ready",
          sweepError: null,
        });
      } catch (err) {
        if (seq !== sweepSeq) return;
        set({
          ...clear,
          sweepStatus: "error",
          sweepError: err instanceof Error ? err.message : "Failed to load sweep data",
        });
      }
    },

    toggleRail: () => set((s) => ({ railOpen: !s.railOpen })),
    toggleLogOpen: () => set((s) => ({ logOpen: !s.logOpen })),

    loadRuns: async () => {
      try {
        const res = await api.waveviewRuns();
        set({ runs: res.runs });
      } catch (err) {
        set({ importError: err instanceof Error ? err.message : "Failed to list runs" });
      }
    },

    loadBrowse: async (dir) => {
      try {
        set({ browse: await api.waveviewBrowse(dir), importError: null });
      } catch (err) {
        set({ importError: err instanceof Error ? err.message : "Failed to browse" });
      }
    },

    uploads: [],
    loadUploads: async () => {
      try {
        set({ uploads: (await api.waveviewUploads()).uploads, importError: null });
      } catch (err) {
        set({ importError: err instanceof Error ? err.message : "Failed to list uploads" });
      }
    },
    deleteUpload: async (uploadId) => {
      try {
        const res = await api.waveviewDeleteUpload(uploadId);
        set((s) => ({ uploads: s.uploads.filter((u) => u.upload_id !== uploadId) }));
        if (res.closed_datasets > 0) await resyncAfterEviction();
      } catch (err) {
        set({ importError: err instanceof Error ? err.message : "Failed to delete upload" });
      }
    },
    pruneRun: async (runId) => {
      try {
        const res = await api.waveviewPruneRun(runId);
        // the badge state (keep_raw → pruned) lives on the runs list
        await get().loadRuns();
        if (res.closed_datasets > 0) await resyncAfterEviction();
        return res.pruned ? null : (res.skipped ?? "nothing to prune");
      } catch (err) {
        set({ importError: err instanceof Error ? err.message : "Failed to prune run" });
        return "prune failed";
      }
    },

    openImport: () => {
      set({ importOpen: true, importError: null });
      void get().loadRuns();
    },
    closeImport: () => set({ importOpen: false, importBusy: false }),
    setPendingOpenRun: (runId) => set({ pendingOpenRunId: runId }),

    refreshWave: async () => {
      const ds = activeDataset();
      const { activeAnalysis, downsample, fmt, overlayId } = get();
      if (!ds || !activeAnalysis || activeAnalysis === "op") {
        set({ wave: null, wavePhase: null, overlayWave: null, waveStatus: ds ? "ready" : "idle" });
        return;
      }
      const signals = signalsFor(ds, activeAnalysis);
      if (!signals.length) {
        set({ wave: null, wavePhase: null, overlayWave: null, waveStatus: "ready" });
        return;
      }
      const seq = ++waveSeq;
      set({ waveStatus: "loading", waveError: null });
      const { method, max_points } = parseDownsample(downsample);
      const dual = !!plotStyleFor(activeAnalysis).dual;
      const base = { analysis: activeAnalysis, signals, method, max_points };
      // On a dual (Bode) analysis, deck-computed `*_db_curve` traces are ALREADY
      // in dB — they land on the magnitude axis as-is, while ordinary signals
      // still fetch fmt=mag_db (splitting one request in two where the selection
      // mixes both). They must fetch fmt=re: an ngspice AC plot stores even
      // `let`-derived vectors as complex (value in the real part), so
      // fmt=auto/mag_db resolve to 20·log10(|v|) and double-log the curve —
      // deceptively (20·log10(30.6 dB) ≈ 29.7, verified live).
      const fetchDual = async (datasetId: string, sigs: string[]): Promise<WaveResponse> => {
        const lin = sigs.filter((s) => !isDbNativeSignal(s));
        const db = sigs.filter(isDbNativeSignal);
        const [linRes, dbRes] = await Promise.all([
          lin.length
            ? api.waveviewWave(datasetId, { ...base, signals: lin, fmt: "mag_db" })
            : Promise.resolve(null),
          db.length
            ? api.waveviewWave(datasetId, { ...base, signals: db, fmt: "re" })
            : Promise.resolve(null),
        ]);
        const first = linRes ?? dbRes;
        if (!first) throw new Error("no signals selected");
        if (!linRes || !dbRes) return first;
        const byName = new Map(
          [...linRes.signals, ...dbRes.signals].map((s) => [s.name, s] as const),
        );
        // selection order decides trace roles/colors — reassemble in that order
        return {
          ...first,
          signals: sigs.flatMap((n) => byName.get(n) ?? []),
        };
      };
      // phase rides y2 for the FIRST ordinary trace only — one ∠ per plot; an
      // already-dB curve is a real vector whose phase (0°/180°) means nothing.
      const phaseSignal = signals.find((s) => !isDbNativeSignal(s)) ?? null;
      try {
        const overlayDs =
          overlayId && overlayId !== ds.dataset_id
            ? get().datasets.find(
                (d) =>
                  d.dataset_id === overlayId &&
                  d.analyses.some((a) => a.analysis === activeAnalysis),
              )
            : undefined;
        const [wave, wavePhase, overlayWave] = await Promise.all([
          dual
            ? fetchDual(ds.dataset_id, signals)
            : api.waveviewWave(ds.dataset_id, { ...base, fmt }),
          dual && phaseSignal
            ? api.waveviewWave(ds.dataset_id, {
                ...base,
                signals: [phaseSignal],
                fmt: "phase_deg",
              })
            : Promise.resolve(null),
          overlayDs
            ? (dual
                ? fetchDual(overlayDs.dataset_id, signalsFor(overlayDs, activeAnalysis))
                : api.waveviewWave(overlayDs.dataset_id, {
                    ...base,
                    signals: signalsFor(overlayDs, activeAnalysis),
                    fmt,
                  })
              ).catch(() => null)
            : Promise.resolve(null),
        ]);
        if (seq !== waveSeq) return; // superseded by a newer selection
        set({ wave, wavePhase, overlayWave, waveStatus: "ready" });
      } catch (err) {
        if (seq !== waveSeq) return;
        set({
          waveStatus: "error",
          waveError: err instanceof Error ? err.message : "Failed to fetch wave",
          wave: null,
          wavePhase: null,
          overlayWave: null,
        });
      }
    },

    refreshMeasures: async () => {
      const ds = activeDataset();
      const { catalog, outSignal } = get();
      if (!ds) return;
      const seq = ++measureSeq;
      const current = () =>
        seq === measureSeq && activeDataset()?.dataset_id === ds.dataset_id;
      const req = buildMeasureItems(catalog, outSignal, ds.analyses);
      if (!req.items.length) {
        set({ measures: [] });
        return;
      }
      try {
        const res = await api.waveviewMeasure(ds.dataset_id, req);
        if (current()) set({ measures: res.results });
      } catch {
        // guard the failure path too: a late rejection from a superseded request
        // must not wipe the results the newer request just wrote
        if (current()) set({ measures: [] });
      }
    },

    refreshScalars: async () => {
      const ds = activeDataset();
      if (!ds) return;
      const seq = ++scalarSeq;
      const current = () =>
        seq === scalarSeq && activeDataset()?.dataset_id === ds.dataset_id;
      try {
        const res = await api.waveviewScalars(ds.dataset_id, "op");
        if (current()) set({ scalars: res });
      } catch {
        if (current()) set({ scalars: null });
      }
    },
  };
});

// Auto-open a pending keep_raw run the moment its live stream finishes.
// Module-level subscription (not a component effect) so it survives the
// Open/Import modal unmounting and Studio view changes — the run keeps
// streaming in runStore either way. No import cycle: runStore never imports
// this store.
let wasRunning = useRunStore.getState().isRunning;
useRunStore.subscribe((s) => {
  if (wasRunning && !s.isRunning) {
    const pending = useWaveviewStore.getState().pendingOpenRunId;
    if (pending) {
      useWaveviewStore.setState({ pendingOpenRunId: null });
      void useWaveviewStore.getState().openRun(pending);
    }
  }
  wasRunning = s.isRunning;
});
