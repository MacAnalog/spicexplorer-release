import { create } from "zustand";
import { api } from "@/lib/api";
import { useExplorerStore } from "@/stores/explorerStore";
import { useProjectStore } from "@/stores/projectStore";
import type { SSEEvent, CheckpointEvent } from "@/types/api";

/**
 * The live SSE connection is held in a module-level variable, NOT in React
 * state — an EventSource isn't serializable, and keeping it out of the
 * component tree is exactly what lets a run keep streaming across view (route)
 * changes. This handler used to live in OptimizeTab; hoisting it here means the
 * RightRail, BottomPanel, and StatusBar update no matter which view is mounted.
 */
let es: EventSource | null = null;

function closeStream() {
  if (es) {
    es.close();
    es = null;
  }
}

/** Metadata describing a finished run (Phase 3 run history). */
export interface RunRecord {
  id: string;
  label: string;
  kind: "live" | "replay";
  /** Present for replays so the run can be re-triggered from history. */
  checkpointId?: string;
  budget: number;
  finalIter: number;
  bestScore: number | null;
  /** Down-sampled best-so-far curve for the history sparkline. */
  sparkline: number[];
  ts: number;
}

/** Mutable per-run context captured at start, consumed when the run finishes. */
interface ActiveMeta {
  kind: "live" | "replay";
  label: string;
  checkpointId?: string;
}

const HISTORY_KEY = "sx_run_history";
const HISTORY_CAP = 25;
const SPARK_POINTS = 40;

function loadHistory(): RunRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    return raw ? (JSON.parse(raw) as RunRecord[]) : [];
  } catch {
    return [];
  }
}

function saveHistory(history: RunRecord[]) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch {
    /* quota / serialization errors are non-fatal for the demo */
  }
}

/** Down-sample a best-so-far series to at most SPARK_POINTS evenly spaced values. */
function downsample(values: number[]): number[] {
  const clean = values.filter((v) => Number.isFinite(v));
  if (clean.length <= SPARK_POINTS) return clean;
  const step = (clean.length - 1) / (SPARK_POINTS - 1);
  return Array.from({ length: SPARK_POINTS }, (_, i) => clean[Math.round(i * step)]);
}

/** One raw SpiceXplorer-library log line streamed during the active run. */
export interface RunLogLine {
  text: string;
  level: string;
}

interface RunStore {
  runId: string | null;
  isRunning: boolean;
  isReplay: boolean;
  budget: number;
  events: SSEEvent[];
  /** Raw library log lines for the ACTIVE run (reset each run; per-run). */
  logLines: RunLogLine[];
  bestMetrics: Record<string, number>;
  bestParams: Record<string, number>;
  currentIter: number;
  /** Checkpoints autosaved during the active run (live, cumulative). */
  checkpoints: CheckpointEvent[];
  /** Last error surfaced by the run (mid-stream {error} event or a lost connection). */
  runError: string | null;
  /** Wall-clock ms timestamp when the active run started (for the Elapsed KPI). */
  runStartTs: number | null;
  /** Frozen elapsed-ms of the last finished run (so the card holds after Stop). */
  elapsedMs: number;
  history: RunRecord[];

  /** Begin a run: reset state, capture meta, open the SSE stream for `id`. */
  startRun: (id: string, replay: boolean, budget: number, meta?: Partial<ActiveMeta>) => void;
  pushEvent: (e: SSEEvent) => void;
  /** Append a raw library log line for the active run (capped for perf). */
  pushLog: (text: string, level: string) => void;
  /** Record an autosaved checkpoint + refresh the on-disk checkpoint list. */
  pushCheckpoint: (c: CheckpointEvent) => void;
  /** Stream ended on its own (done/error) — record to history, close locally. */
  finishRun: () => void;
  /** User pressed Stop — best-effort tell the backend, record, then close. */
  stopRun: () => void;
  /** Re-trigger a replay run from a history record (no-op for live records). */
  rerun: (rec: RunRecord) => Promise<void>;
  clearHistory: () => void;
  reset: () => void;
}

let activeMeta: ActiveMeta = { kind: "replay", label: "Run" };

const INITIAL = {
  runId: null,
  isRunning: false,
  isReplay: false,
  budget: 0,
  events: [] as SSEEvent[],
  logLines: [] as RunLogLine[],
  bestMetrics: {} as Record<string, number>,
  bestParams: {} as Record<string, number>,
  currentIter: 0,
  checkpoints: [] as CheckpointEvent[],
  runError: null as string | null,
  runStartTs: null as number | null,
  elapsedMs: 0,
};

export const useRunStore = create<RunStore>((set, get) => ({
  ...INITIAL,
  history: loadHistory(),

  startRun: (id, replay, budget, meta) => {
    // If a prior run is still in flight, tell the backend to stop it so we don't
    // orphan its optimizer thread/queue when this run supersedes it (e.g. clicking
    // a history replay mid-run).
    const prev = get();
    if (prev.isRunning && prev.runId && prev.runId !== id) {
      api.stopRun(prev.runId).catch(() => {});
      // Record the superseded run to history before we reset state — finishRun() is the only
      // writer of a history record, so without this the prior run's trials vanish (BUG-B47).
      get().finishRun();
    }
    closeStream();
    activeMeta = {
      kind: meta?.kind ?? (replay ? "replay" : "live"),
      label: meta?.label ?? (replay ? "Replay" : "Live run"),
      checkpointId: meta?.checkpointId,
    };
    set({
      runId: id,
      isRunning: true,
      isReplay: replay,
      budget,
      events: [],
      logLines: [],
      bestMetrics: {},
      bestParams: {},
      currentIter: 0,
      checkpoints: [],
      runError: null,
      runStartTs: Date.now(),
      elapsedMs: 0,
    });

    const source = new EventSource(api.streamUrl(id));
    es = source;
    source.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as SSEEvent;
        if (data.error) {
          // A mid-run failure (ngspice/PDK/parameterize error). Surface it; the
          // backend follows with a done event that drives finishRun().
          set({ runError: String(data.error) });
          return;
        }
        if (data.done) {
          get().finishRun();
          return;
        }
        if (data.heartbeat) return;
        if (data.checkpoint) {
          get().pushCheckpoint(data.checkpoint);
          return;
        }
        if (data.log != null) {
          get().pushLog(data.log, data.level ?? "INFO");
          return;
        }
        get().pushEvent(data);
      } catch {
        /* ignore malformed keepalive lines */
      }
    };
    source.onerror = () => {
      // Only a CLOSED connection is fatal. While CONNECTING the browser is
      // auto-reconnecting; calling finishRun()->closeStream() here would cancel
      // that reconnect and turn a transient blip into a permanent stop (orphaning
      // the still-running backend optimizer).
      if (source.readyState !== EventSource.CLOSED) return;
      if (es !== source) return; // a newer run already replaced this stream
      const { runId, isReplay } = get();
      if (runId && !isReplay) api.stopRun(runId).catch(() => {});
      set({ runError: "Connection to the run stream was lost." });
      get().finishRun();
    };
  },

  pushEvent: (e) =>
    set((state) => {
      const events = [...state.events, e];
      // Prefer the best trial's metrics (live runs emit `best_metrics`); fall back to
      // `metrics` for replay (metrics[i] paired with params[i] per row) AND when
      // best_metrics is an empty {} — e.g. a resume before the first new best — since `??`
      // would not fall through an (non-nullish) empty object.
      const metricsSource =
        e.best_metrics && Object.keys(e.best_metrics).length ? e.best_metrics : e.metrics;
      const bestMetrics = metricsSource
        ? {
            ...state.bestMetrics,
            ...(Object.fromEntries(
              Object.entries(metricsSource).filter(([, v]) => v !== null),
            ) as Record<string, number>),
          }
        : state.bestMetrics;
      const bestParams = e.best_params
        ? {
            ...state.bestParams,
            ...(Object.fromEntries(
              Object.entries(e.best_params).filter(([, v]) => v !== null),
            ) as Record<string, number>),
          }
        : state.bestParams;
      return { events, bestMetrics, bestParams, currentIter: e.iter ?? state.currentIter };
    }),

  pushLog: (text, level) =>
    set((state) => {
      // Cap the buffer so a long run can't grow it unbounded (keep the tail).
      const next = [...state.logLines, { text, level }];
      return { logLines: next.length > 2000 ? next.slice(-2000) : next };
    }),

  pushCheckpoint: (c) => {
    set((state) => ({ checkpoints: [...state.checkpoints, c] }));
    // Refresh the on-disk checkpoint list so the new file appears in the rail
    // (and becomes available to Resume / Explore) while the run is still going —
    // scoped to the active project so it doesn't list other projects' runs.
    api
      .listCheckpoints(useProjectStore.getState().projectId ?? undefined)
      .then(useExplorerStore.getState().setAvailableCheckpoints)
      .catch(() => {});
  },

  finishRun: () => {
    closeStream();
    const { runId, events, budget, currentIter, history, runStartTs } = get();
    set({ isRunning: false, elapsedMs: runStartTs ? Date.now() - runStartTs : 0 });
    if (!runId || events.length === 0) return;

    // Build a metadata-only history record (no full event arrays persisted).
    const bestSeries = events.map((e) => e.best_score ?? e.score).filter((v): v is number =>
      v != null && Number.isFinite(v),
    );
    const bestScore = bestSeries.length ? bestSeries[bestSeries.length - 1] : null;
    const record: RunRecord = {
      id: runId,
      label: activeMeta.label,
      kind: activeMeta.kind,
      checkpointId: activeMeta.checkpointId,
      budget,
      finalIter: currentIter,
      bestScore,
      sparkline: downsample(bestSeries),
      ts: Date.now(),
    };
    // De-dupe by id (a re-run keeps one entry), newest first, capped.
    const next = [record, ...history.filter((r) => r.id !== runId)].slice(0, HISTORY_CAP);
    set({ history: next });
    saveHistory(next);
  },

  stopRun: () => {
    const id = get().runId;
    if (id) api.stopRun(id).catch(() => {});
    get().finishRun();
  },

  rerun: async (rec) => {
    if (rec.kind !== "replay" || !rec.checkpointId) return;
    try {
      const res = await api.startRun({ replay: true, checkpoint_id: rec.checkpointId });
      get().startRun(res.run_id, true, rec.budget, {
        kind: "replay",
        label: rec.label,
        checkpointId: rec.checkpointId,
      });
    } catch {
      /* surfaced elsewhere; history click is best-effort */
    }
  },

  clearHistory: () => {
    set({ history: [] });
    saveHistory([]);
  },

  reset: () => {
    closeStream();
    set({ ...INITIAL });
  },
}));
