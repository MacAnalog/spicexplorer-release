// Shared "start a live optimization run" flow, used by both the title-bar Run
// popover and the Optimize toolbar so the launch logic (and the algorithm/seed
// overrides) live in exactly one place. Reads the current stores via getState()
// — no hook, so it can be called from event handlers anywhere.
import { api } from "@/lib/api";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";

export interface LaunchResult {
  ok: boolean;
  error?: string;
}

/**
 * Start a live SPICE run using the shared run config (algorithm/budget/seed/
 * autosave). Validates that a project is applied and the PDK is present, sends
 * the overrides to the backend, and opens the SSE stream via runStore. When
 * `resumeCheckpointId` is given the backend continues that checkpoint's run
 * (load + keep_history). Returns a result instead of throwing so callers can
 * surface the error inline.
 */
async function startLive(resumeCheckpointId?: string): Promise<LaunchResult> {
  const { yamlPath, isApplied, projectId } = useProjectStore.getState();
  const { env, runConfig } = useUIStore.getState();
  const { startRun } = useRunStore.getState();

  if (!isApplied) {
    return { ok: false, error: "Apply a project on Setup before starting a live run." };
  }
  if (env && !env.live_runs_enabled) {
    return {
      ok: false,
      error: "PDK missing — live runs are disabled. Use Replay on the Optimize view.",
    };
  }

  try {
    const res = await api.startRun({
      yaml_path: yamlPath || undefined,
      project_id: projectId ?? undefined,
      budget: runConfig.budget,
      algorithm: runConfig.algorithm,
      seed: runConfig.seed ?? undefined,
      active_corner: runConfig.activeCorner ?? undefined,
      autosave_every: runConfig.autosaveEvery ?? undefined,
      resume_checkpoint_id: resumeCheckpointId,
    });
    startRun(res.run_id, res.replay, runConfig.budget, {
      kind: "live",
      label: `${resumeCheckpointId ? "Resume" : "Live"} · ${runConfig.algorithm}${
        runConfig.activeCorner ? ` · ${runConfig.activeCorner}` : ""
      }`,
    });
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : "Failed to start run" };
  }
}

/** Start a fresh live run from the current run config. */
export const launchLiveRun = (): Promise<LaunchResult> => startLive();

/**
 * Start a short live run with `keep_raw` so every trial's .raw survives for the
 * Analyze waveform viewer (the backend deletes trial raws by default — this flag
 * is the only path to an openable dataset from a fresh simulation). Same launch
 * plumbing as startLive; the caller opens the run in the viewer once it ends.
 */
export async function launchKeepRawRun(opts: {
  budget: number;
  activeCorner?: string | null;
}): Promise<LaunchResult & { runId?: string }> {
  const { yamlPath, isApplied, projectId } = useProjectStore.getState();
  const { env, runConfig } = useUIStore.getState();
  const { startRun } = useRunStore.getState();

  if (!isApplied) {
    return { ok: false, error: "Apply a project on Setup before running a simulation." };
  }
  if (env && !env.live_runs_enabled) {
    return { ok: false, error: "PDK missing — live runs are disabled on this host." };
  }

  try {
    const res = await api.startRun({
      yaml_path: yamlPath || undefined,
      project_id: projectId ?? undefined,
      budget: opts.budget,
      algorithm: runConfig.algorithm,
      active_corner: opts.activeCorner ?? undefined,
      keep_raw: true,
    });
    startRun(res.run_id, res.replay, opts.budget, {
      kind: "live",
      label: `Analyze · keep_raw · ${opts.budget} trial${opts.budget === 1 ? "" : "s"}${
        opts.activeCorner ? ` · ${opts.activeCorner}` : ""
      }`,
    });
    return { ok: true, runId: res.run_id };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : "Failed to start run" };
  }
}

/** Resume a live run from a saved checkpoint, continuing its history. */
export const resumeLiveRun = (checkpointId: string): Promise<LaunchResult> =>
  startLive(checkpointId);
