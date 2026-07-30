"use client";
import { useEffect, useRef, useState } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { RefreshCw, X, Trash2, Play, Pencil, Check, Undo2 } from "lucide-react";
import { useExplorerStore } from "@/stores/explorerStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { useProjectStore } from "@/stores/projectStore";
import { api } from "@/lib/api";
import { resumeLiveRun } from "@/lib/launchRun";
import { cn, formatEng } from "@/lib/utils";
import { RailHeading, RailHint } from "./parts";
import type { ProjectRun, TrashItem } from "@/types/api";

const RUN_STATUS_CLS: Record<string, string> = {
  running: "bg-primary-soft text-primary",
  done: "bg-ok-soft text-ok",
  stopped: "bg-hairline text-muted",
  error: "bg-danger-soft text-danger",
};

/**
 * Run-centric rail (Optimize, Explore): the ACTIVE project's runs (rename/delete/restore)
 * plus its on-disk checkpoint list (refresh/delete/resume). The rail is project-scoped —
 * with no project selected it shows nothing but a hint, since runs and checkpoints only
 * have meaning relative to a project.
 */
export function RunsRail() {
  const router = useRouter();
  const { availableCheckpoints, setAvailableCheckpoints } = useExplorerStore();
  const { isRunning } = useRunStore();
  const env = useUIStore((s) => s.env);
  const isApplied = useProjectStore((s) => s.isApplied);
  const projectId = useProjectStore((s) => s.projectId);
  const [refreshing, setRefreshing] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [projectRuns, setProjectRuns] = useState<ProjectRun[]>([]);
  const [runTrash, setRunTrash] = useState<TrashItem[]>([]);
  // Per-run lifecycle UI state (report.md P4): inline rename draft + armed delete.
  const [editingRunId, setEditingRunId] = useState<string | null>(null);
  const [editRunLabel, setEditRunLabel] = useState("");
  const [pendingRunDelete, setPendingRunDelete] = useState<string | null>(null);
  // Guards against the run-rename input firing commit twice (Enter then the unmount blur).
  const runRenameInFlight = useRef(false);
  // Set on Escape so the unmount-triggered onBlur cancels instead of committing the draft (BUG-B51).
  const cancelRename = useRef(false);

  // Per-project run history (report.md P3) — server-persisted, replacing the
  // localStorage list when a registered project is active. Refetched on project
  // switch and when a run finishes (isRunning flips false).
  useEffect(() => {
    if (!projectId) {
      setProjectRuns([]);
      setRunTrash([]);
      return;
    }
    let alive = true;
    api.getProjectRuns(projectId)
      .then((r) => { if (alive) setProjectRuns(r.runs); })
      .catch(() => { if (alive) setProjectRuns([]); });
    api.listTrash()
      .then((r) => { if (alive) setRunTrash(r.trash.filter((t) => t.kind === "run" && t.project_id === projectId)); })
      .catch(() => { if (alive) setRunTrash([]); });
    return () => { alive = false; };
  }, [projectId, isRunning]);

  const refreshProjectRuns = async () => {
    if (!projectId) return;
    try {
      const [r, t] = await Promise.all([api.getProjectRuns(projectId), api.listTrash()]);
      setProjectRuns(r.runs);
      setRunTrash(t.trash.filter((x) => x.kind === "run" && x.project_id === projectId));
    } catch {
      /* best-effort */
    }
  };

  const handleRestoreRun = async (trashId: string) => {
    setError(null);
    try {
      await api.restoreTrash(trashId);
      await refreshProjectRuns();
      // The restored run's checkpoints are back on disk — re-scope the catalog so they
      // reappear immediately (mirrors handleDeleteRun, which removes them on delete).
      setAvailableCheckpoints(await api.listCheckpoints(projectId ?? undefined));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Restore failed");
    }
  };

  const commitRunRename = async (runId: string) => {
    if (cancelRename.current) { cancelRename.current = false; setEditingRunId(null); return; }
    if (runRenameInFlight.current) return;  // Enter + blur both fire — commit once.
    const label = editRunLabel.trim();
    if (!projectId || !label) { setEditingRunId(null); return; }
    runRenameInFlight.current = true;
    setError(null);
    try {
      await api.renameRun(projectId, runId, label);
      await refreshProjectRuns();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Rename failed");
    } finally {
      setEditingRunId(null);
      runRenameInFlight.current = false;
    }
  };

  const handleDeleteRun = async (runId: string) => {
    if (!projectId) return;
    setPendingRunDelete(runId);
    setError(null);
    try {
      await api.deleteRun(projectId, runId);
      await refreshProjectRuns();
      // A deleted run's checkpoints vanish too — re-scope the catalog.
      setAvailableCheckpoints(await api.listCheckpoints(projectId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setPendingRunDelete(null);
    }
  };

  // Re-scope the checkpoint catalog to the active project so it stops showing
  // OTHER projects' per-run checkpoints when you switch projects.
  useEffect(() => {
    api.listCheckpoints(projectId ?? undefined)
      .then(setAvailableCheckpoints)
      .catch(() => {});
  }, [projectId, isRunning, setAvailableCheckpoints]);

  // Resume needs an applied project, the PDK, and no run in flight.
  const canResume = isApplied && !(env != null && !env.live_runs_enabled) && !isRunning;

  const handleResume = async (id: string) => {
    setError(null);
    const res = await resumeLiveRun(id);
    if (res.ok) router.push("/optimize" as Route);
    else setError(res.error ?? "Resume failed");
  };

  const refreshCheckpoints = async () => {
    setRefreshing(true);
    setError(null);
    try {
      setAvailableCheckpoints(await api.listCheckpoints(projectId ?? undefined));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const handleDelete = async (id: string, label: string, path?: string) => {
    if (!window.confirm(`Delete checkpoint "${label}"? This removes the file on disk.`)) return;
    setPendingDelete(id);
    setError(null);
    try {
      // Pass the exact file path so the delete targets only this row's file, never a
      // same-named checkpoint in another run/project (BUG-B3).
      await api.deleteCheckpoint(id, projectId ?? undefined, path);
      setAvailableCheckpoints(await api.listCheckpoints(projectId ?? undefined));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setPendingDelete(null);
    }
  };

  // Project-scoped rail: with no active project there are no runs/checkpoints to show
  // (the legacy localStorage history + global preset catalog were intentionally removed).
  if (!projectId) {
    return (
      <>
        <RailHeading>Runs</RailHeading>
        <RailHint>No project selected. Open a project (⌘P) to see its runs and checkpoints.</RailHint>
      </>
    );
  }

  return (
    <>
      <RailHeading>Project runs</RailHeading>

      {/* Per-project server runs (report.md P3): honest status pills (the startup
          reconciler flips crashed 'running' → 'error'), best score, algo·budget. */}
      {projectRuns.length === 0 ? (
          <RailHint>No runs yet for this project.</RailHint>
        ) : (
          projectRuns.map((r) => {
            const isEditing = editingRunId === r.run_id;
            const isConfirming = pendingRunDelete === r.run_id;
            return (
              <div key={r.run_id} className="group flex w-full items-center gap-2 rounded-sm px-1.5 py-1 hover:bg-hairline">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-1">
                    {isEditing ? (
                      <input
                        autoFocus
                        value={editRunLabel}
                        onChange={(e) => setEditRunLabel(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") void commitRunRename(r.run_id);
                          if (e.key === "Escape") { cancelRename.current = true; setEditingRunId(null); }
                        }}
                        onBlur={() => void commitRunRename(r.run_id)}
                        aria-label="Rename run"
                        className="min-w-0 flex-1 rounded-sm border border-border bg-transparent px-1 py-0.5 text-[11px] text-fg outline-hidden"
                      />
                    ) : (
                      <span className="truncate text-[11px]">
                        {r.label ?? r.algorithm ?? r.run_id.slice(0, 8)}
                      </span>
                    )}
                    <span className="flex shrink-0 items-center gap-1">
                      {!isEditing && (
                        <span className="flex items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                          <button
                            type="button"
                            onClick={() => { setPendingRunDelete(null); setEditingRunId(r.run_id); setEditRunLabel(r.label ?? r.algorithm ?? ""); }}
                            aria-label="Rename run"
                            title="Rename run"
                            className="rounded-sm p-0.5 text-faint hover:bg-hairline hover:text-fg"
                          >
                            <Pencil className="h-3 w-3" />
                          </button>
                          {isConfirming ? (
                            <>
                              <button
                                type="button"
                                onClick={() => void handleDeleteRun(r.run_id)}
                                aria-label="Confirm delete run"
                                title="Confirm delete"
                                className="rounded-sm p-0.5 text-danger hover:bg-danger-soft"
                              >
                                <Check className="h-3 w-3" />
                              </button>
                              <button
                                type="button"
                                onClick={() => setPendingRunDelete(null)}
                                aria-label="Cancel delete run"
                                title="Cancel"
                                className="rounded-sm p-0.5 text-muted hover:bg-hairline hover:text-fg"
                              >
                                <X className="h-3 w-3" />
                              </button>
                            </>
                          ) : (
                            <button
                              type="button"
                              onClick={() => setPendingRunDelete(r.run_id)}
                              aria-label="Delete run"
                              title="Delete run (recoverable)"
                              className="rounded-sm p-0.5 text-faint hover:bg-danger-soft hover:text-danger"
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          )}
                        </span>
                      )}
                      <span className="font-mono text-[10px] text-muted">
                        {r.best_score != null ? formatEng(r.best_score) : "—"}
                      </span>
                    </span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-1.5 font-mono text-[9px] text-faint">
                    <span className={cn("rounded-sm px-1", RUN_STATUS_CLS[r.status] ?? "bg-hairline text-muted")}>
                      {r.status}
                    </span>
                    <span className="truncate">
                      {r.algorithm ?? r.kind}{r.budget ? ` · ${r.budget} it` : ""}
                    </span>
                    {isConfirming && <span className="text-danger">delete?</span>}
                  </div>
                </div>
              </div>
            );
          })
        )}
        {runTrash.length > 0 && (
          <div className="mt-1">
            <div className="px-1.5 pb-0.5 text-[9px] font-medium uppercase tracking-wider text-faint">
              Recently deleted
            </div>
            {runTrash.map((t) => (
              <div key={t.trash_id} className="flex items-center justify-between gap-1 rounded-sm px-1.5 py-1 text-muted">
                <span className="truncate text-[11px] line-through decoration-faint">{t.name}</span>
                <button
                  type="button"
                  onClick={() => void handleRestoreRun(t.trash_id)}
                  aria-label="Restore run"
                  title="Restore run"
                  className="inline-flex shrink-0 items-center gap-1 rounded-sm border border-border px-1.5 py-0.5 text-[10px] text-fg hover:bg-hairline"
                >
                  <Undo2 className="h-3 w-3" /> Restore
                </button>
              </div>
            ))}
          </div>
        )}

      <RailHeading
        right={
          <button
            type="button"
            onClick={refreshCheckpoints}
            disabled={refreshing}
            aria-label="Refresh checkpoint list"
            title="Re-scan the checkpoints directory"
            className="rounded-sm p-0.5 text-muted normal-case tracking-normal hover:bg-hairline hover:text-fg disabled:opacity-50"
          >
            <RefreshCw className={cn("h-3 w-3", refreshing && "animate-spin")} />
          </button>
        }
      >
        Checkpoints
      </RailHeading>

      {availableCheckpoints.length === 0 ? (
        <RailHint>No checkpoints found.</RailHint>
      ) : (
        availableCheckpoints.slice(0, 12).map((c) => {
          const deletable = c.source === "autosave";
          const isDeleting = pendingDelete === c.id;
          return (
            <div
              key={c.id}
              className="group flex items-start gap-1 rounded-sm px-1.5 py-1 hover:bg-hairline"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-1">
                  <span className="truncate text-[11px]">{c.label}</span>
                  {c.n_iters != null && (
                    <span className="font-mono text-[10px] text-muted">{c.n_iters}</span>
                  )}
                </div>
                <div className="mt-0.5 font-mono text-[9px] text-faint">
                  {c.source === "preset" ? "preset · " : ""}
                  {c.score_fn || c.type}
                </div>
              </div>
              {deletable && (
                <button
                  type="button"
                  onClick={() => handleResume(c.id)}
                  disabled={!canResume}
                  aria-label={`Resume from checkpoint ${c.label}`}
                  title={
                    canResume
                      ? "Resume an optimization from this checkpoint"
                      : isRunning
                        ? "A run is already active"
                        : "Apply a project (and the PDK) to resume"
                  }
                  className="rounded-sm p-0.5 text-faint opacity-0 transition-opacity hover:bg-primary-soft hover:text-primary group-hover:opacity-100 disabled:opacity-30"
                >
                  <Play className="h-3 w-3" />
                </button>
              )}
              {deletable && (
                <button
                  type="button"
                  onClick={() => handleDelete(c.id, c.label, c.path)}
                  disabled={isDeleting}
                  aria-label={`Delete checkpoint ${c.label}`}
                  title="Delete this autosaved checkpoint"
                  className="rounded-sm p-0.5 text-faint opacity-0 transition-opacity hover:bg-danger-soft hover:text-danger group-hover:opacity-100 disabled:opacity-50"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          );
        })
      )}
      {error && <div className="mt-1 px-1.5 py-1 text-[10px] text-danger">{error}</div>}
      <div className="mt-1 px-1.5 text-[10px] text-faint">
        Add new ones via Optimize → Save checkpoint. Presets are read-only.
      </div>
    </>
  );
}
