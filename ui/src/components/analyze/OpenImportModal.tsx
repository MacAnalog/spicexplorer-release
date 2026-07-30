"use client";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Segmented } from "@/components/ui/segmented";
import { selectCn } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { launchKeepRawRun } from "@/lib/launchRun";
import { cornerOptionLabel } from "@/lib/pvt";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { useWaveviewStore } from "@/stores/waveviewStore";
import type { WaveRunInfo } from "@/types/api";

type OpenMode = "runs" | "browse" | "path" | "upload";

/**
 * Open / Import — two columns: run a fresh keep_raw simulation (left; the only
 * way a new sim leaves an openable .raw) ‖ open existing results (right; recent
 * runs, a whitelisted directory browser, or a pasted absolute path).
 */
export function OpenImportModal() {
  const importOpen = useWaveviewStore((s) => s.importOpen);
  const closeImport = useWaveviewStore((s) => s.closeImport);

  useEffect(() => {
    if (!importOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        closeImport();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [importOpen, closeImport]);

  if (!importOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-[10vh]"
      onClick={closeImport}
      role="dialog"
      aria-modal="true"
      aria-label="Open or import simulation results"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex max-h-[78vh] w-[760px] max-w-[94vw] flex-col overflow-hidden rounded-lg border border-border bg-panel shadow-soft"
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
          <span className="text-[13px] font-medium text-fg">Open / Import</span>
          <button
            type="button"
            onClick={closeImport}
            aria-label="Close"
            className="rounded-sm px-1.5 text-muted hover:text-fg"
          >
            ✕
          </button>
        </div>
        <div className="flex min-h-0 flex-1 divide-x divide-hairline overflow-hidden">
          <RunColumn />
          <OpenColumn />
        </div>
        <ErrorFooter />
      </div>
    </div>
  );
}

function ErrorFooter() {
  const importError = useWaveviewStore((s) => s.importError);
  if (!importError) return null;
  return (
    <div className="border-t border-border bg-danger-soft px-4 py-2 text-[11px] text-danger">
      {importError}
    </div>
  );
}

/** Left — run a new simulation with keep_raw, then auto-open it. */
function RunColumn() {
  const summary = useProjectStore((s) => s.summary);
  const isApplied = useProjectStore((s) => s.isApplied);
  const env = useUIStore((s) => s.env);
  const isRunning = useRunStore((s) => s.isRunning);
  const currentIter = useRunStore((s) => s.currentIter);
  // The auto-open promise is STORE state: the waveviewStore's runStore
  // subscription opens the run when the stream ends, even if this modal (or
  // the whole Analyze view) unmounts mid-run.
  const pendingRunId = useWaveviewStore((s) => s.pendingOpenRunId);
  const setPendingOpenRun = useWaveviewStore((s) => s.setPendingOpenRun);

  const corners = summary?.pvt?.corners ?? [];
  const [corner, setCorner] = useState<string>("");
  const [budget, setBudget] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const canRun = isApplied && (!env || env.live_runs_enabled) && !isRunning;

  const start = async () => {
    setError(null);
    const res = await launchKeepRawRun({ budget, activeCorner: corner || null });
    if (!res.ok) setError(res.error ?? "Failed to start");
    else if (res.runId) setPendingOpenRun(res.runId);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-4">
      <div>
        <div className="text-[12px] font-semibold text-fg">Run a new simulation</div>
        <div className="mt-0.5 text-[10.5px] leading-relaxed text-muted">
          Live run with <span className="font-mono">keep_raw</span> — every trial&apos;s{" "}
          <span className="font-mono">.raw</span> is retained and the newest opens here when
          the run ends.
        </div>
      </div>

      <div className="rounded-md border border-hairline bg-bg p-2.5 font-mono text-[10px] text-muted">
        {isApplied && summary ? (
          <>
            <span className="font-semibold text-fg">{summary.name}</span>
            <br />
            {summary.simulator} · {summary.tech.name}
          </>
        ) : (
          "no applied project — load one on Setup"
        )}
      </div>

      {/* Sweep — decided by the project's `pvt:` block (the handoff's Sweep row;
          launch-time PVT/MC pickers need the /simulate/sweep · /montecarlo lanes). */}
      <div>
        <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-muted">
          Sweep
        </span>
        {summary?.pvt?.mode === "multi" ? (
          <div className="rounded-md border border-primary/40 bg-primary-soft px-2.5 py-1.5">
            <span className="text-[11px] font-semibold text-primary">
              PVT corners · {corners.filter((c) => c.enabled !== false).length} enabled
            </span>
            <div className="mt-0.5 font-mono text-[9.5px] leading-relaxed text-muted">
              each trial runs corners × testbenches → __&lt;corner&gt; artifacts; Analyze&apos;s
              “PVT corners” mode reads them
            </div>
          </div>
        ) : (
          <div className="font-mono text-[10px] text-muted">
            single corner · set <span className="text-fg">pvt.mode: multi</span> in the project
            for corner sweeps
          </div>
        )}
      </div>

      {corners.length > 0 && summary?.pvt?.mode !== "multi" && (
        <label className="block">
          <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-muted">
            PVT corner
          </span>
          <select
            className={selectCn("xs") + " w-full"}
            value={corner}
            onChange={(e) => setCorner(e.target.value)}
          >
            <option value="">project default ({summary?.pvt?.active_corner})</option>
            {corners.map((c) => (
              <option key={c.name} value={c.name}>
                {cornerOptionLabel(c)}
              </option>
            ))}
          </select>
        </label>
      )}

      <label className="block">
        <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-muted">
          Trials (budget)
        </span>
        <input
          type="number"
          min={1}
          max={50}
          value={budget}
          onChange={(e) => setBudget(Math.max(1, Number(e.target.value) || 1))}
          className="h-[26px] w-24 rounded-md border border-border bg-panel px-2 font-mono text-xs text-fg outline-hidden focus:ring-1 focus:ring-primary"
        />
      </label>

      <div className="flex items-center gap-2">
        <Button variant="primary" disabled={!canRun} onClick={() => void start()}>
          ▶ Run &amp; open
        </Button>
        {pendingRunId && isRunning && (
          <span className="font-mono text-[10px] text-muted">
            running · trial {currentIter}/{budget}…
          </span>
        )}
      </div>
      {!isApplied && (
        <div className="text-[10.5px] text-faint">Apply a project on Setup to enable this.</div>
      )}
      {env && !env.live_runs_enabled && (
        <div className="text-[10.5px] text-tertiary">
          PDK missing on this host — live runs are disabled; open existing results instead.
        </div>
      )}
      {error && <div className="text-[11px] text-danger">{error}</div>}
    </div>
  );
}

/** Right — open existing results: recent runs / browse / absolute path. */
function OpenColumn() {
  const runs = useWaveviewStore((s) => s.runs);
  const browse = useWaveviewStore((s) => s.browse);
  const importBusy = useWaveviewStore((s) => s.importBusy);
  const loadRuns = useWaveviewStore((s) => s.loadRuns);
  const loadBrowse = useWaveviewStore((s) => s.loadBrowse);
  const openRun = useWaveviewStore((s) => s.openRun);
  const openPath = useWaveviewStore((s) => s.openPath);
  const uploadFile = useWaveviewStore((s) => s.uploadFile);
  const summary = useProjectStore((s) => s.summary);

  const [mode, setMode] = useState<OpenMode>("runs");
  const [path, setPath] = useState("");
  const [dragOver, setDragOver] = useState(false);

  // Browse seed: the applied project's workspace, else the newest run's dir.
  const seedDir = useMemo(
    () => summary?.ws_root ?? runs[0]?.run_dir ?? "",
    [summary, runs],
  );

  useEffect(() => {
    if (mode === "browse" && !browse && seedDir) void loadBrowse(seedDir);
  }, [mode, browse, seedDir, loadBrowse]);

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-hidden p-4">
      <div className="text-[12px] font-semibold text-fg">Open existing results</div>
      <Segmented<OpenMode>
        value={mode}
        onChange={setMode}
        options={[
          { value: "runs", label: "from run" },
          { value: "browse", label: "browse" },
          { value: "path", label: "path" },
          { value: "upload", label: "upload" },
        ]}
      />

      {mode === "runs" && (
        <div className="flex min-h-0 flex-1 flex-col gap-1.5 overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-muted">
              Recent runs
            </span>
            <button
              type="button"
              onClick={() => void loadRuns()}
              className="text-[10px] text-primary hover:underline"
            >
              refresh
            </button>
          </div>
          <div className="min-h-0 flex-1 space-y-1 overflow-y-auto">
            {runs.length === 0 && (
              <div className="py-3 text-[11px] text-faint">
                No runs found under the work root.
              </div>
            )}
            {runs.map((r) => (
              <RunRow key={r.run_id} run={r} busy={importBusy} onOpen={() => void openRun(r.run_id, r.project_id ?? undefined)} />
            ))}
          </div>
        </div>
      )}

      {mode === "browse" && (
        <div className="flex min-h-0 flex-1 flex-col gap-1.5 overflow-hidden">
          {browse ? (
            <>
              <div className="flex items-center gap-1 font-mono text-[9.5px] text-faint">
                {/* backend-computed, whitelist-aware up target (null at a root) */}
                <button
                  type="button"
                  disabled={!browse.parent}
                  className="text-primary hover:underline disabled:text-faint disabled:no-underline"
                  onClick={() => browse.parent && void loadBrowse(browse.parent)}
                >
                  ↑ up
                </button>
                <span className="truncate">{browse.dir}</span>
              </div>
              <div className="min-h-0 flex-1 space-y-px overflow-y-auto rounded-md border border-hairline bg-bg p-1.5">
                {browse.entries.length === 0 && (
                  <div className="py-2 text-center text-[10.5px] text-faint">empty</div>
                )}
                {browse.entries.map((e) => (
                  <button
                    key={e.path}
                    type="button"
                    disabled={importBusy || e.type === "log"}
                    onClick={() =>
                      e.type === "dir" ? void loadBrowse(e.path) : void openPath(e.path)
                    }
                    className={cn(
                      "flex w-full items-center gap-2 rounded-sm px-1.5 py-[3px] text-left font-mono text-[10.5px] hover:bg-hairline",
                      e.type === "log" && "cursor-default opacity-50",
                    )}
                  >
                    <span className="w-4 shrink-0 text-faint">
                      {e.type === "dir" ? "▸" : "▤"}
                    </span>
                    <span className="min-w-0 flex-1 truncate text-fg">{e.name}</span>
                    {e.type !== "dir" && (
                      <span
                        className={cn(
                          "rounded-sm px-1 text-[9px] font-semibold",
                          e.type === "spectre_raw_dir"
                            ? "bg-secondary-soft text-secondary"
                            : e.type === "ngspice_raw"
                              ? "bg-primary-soft text-primary"
                              : "bg-hairline text-muted",
                        )}
                      >
                        {e.type}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <div className="py-3 text-[11px] text-faint">
              {seedDir
                ? "Loading directory…"
                : "No browse root available — apply a project or use the path mode."}
            </div>
          )}
        </div>
      )}

      {mode === "upload" && (
        <div className="flex flex-col gap-2">
          <label
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              const f = e.dataTransfer.files?.[0];
              if (f && !importBusy) void uploadFile(f);
            }}
            className={cn(
              "flex min-h-[110px] cursor-pointer flex-col items-center justify-center gap-1 rounded-lg border-2 border-dashed p-4 text-center",
              dragOver ? "border-primary bg-primary-soft" : "border-border bg-bg",
            )}
          >
            <span className="text-[12px] font-medium text-fg">
              ⤒ drop a result artifact — <span className="font-mono">.raw</span> ·{" "}
              <span className="font-mono">.zip</span> (Spectre PSF dir) ·{" "}
              <span className="font-mono">.log</span> — or a self-contained ngspice deck (
              <span className="font-mono">.spice</span> · <span className="font-mono">.cir</span>
              ) to run it
            </span>
            <span className="font-mono text-[9.5px] text-faint">
              results stage + auto-open · netlists run as a `kind: netlist` run (needs ngspice)
            </span>
            <input
              type="file"
              accept=".raw,.zip,.log,.out,.txt,.spice,.cir,.net,.sp"
              className="hidden"
              disabled={importBusy}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void uploadFile(f);
                e.target.value = "";
              }}
            />
          </label>
          {importBusy && (
            <span className="font-mono text-[10px] text-muted">
              uploading… (a netlist runs ngspice first — up to a few minutes)
            </span>
          )}
          <UploadsManager />
        </div>
      )}

      {mode === "path" && (
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-semibold uppercase tracking-wide text-muted">
            Absolute path to a .raw file or Spectre PSF directory
          </span>
          <input
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="/work/runs/…/sim/tb_ac.raw"
            className="h-[28px] w-full rounded-md border border-border bg-panel px-2 font-mono text-[11px] text-fg outline-hidden placeholder:text-faint focus:ring-1 focus:ring-primary"
          />
          <div>
            <Button
              variant="primary"
              disabled={!path.trim() || importBusy}
              onClick={() => void openPath(path.trim())}
            >
              Open in viewer
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

/** Staged-uploads inventory under the drop zone: what's parked in
 *  work/waveview_uploads (TTL-swept server-side), with a two-step delete that
 *  also evicts any open datasets backed by the staging dir. */
function UploadsManager() {
  const uploads = useWaveviewStore((s) => s.uploads);
  const importBusy = useWaveviewStore((s) => s.importBusy);
  const loadUploads = useWaveviewStore((s) => s.loadUploads);
  const deleteUpload = useWaveviewStore((s) => s.deleteUpload);
  const [armId, setArmId] = useState<string | null>(null);

  // refresh on mount and after each upload finishes
  useEffect(() => {
    if (!importBusy) void loadUploads();
  }, [importBusy, loadUploads]);

  return (
    <div className="flex min-h-0 flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-semibold uppercase tracking-wide text-muted">
          Staged uploads
        </span>
        <button
          type="button"
          onClick={() => void loadUploads()}
          className="text-[10px] text-primary hover:underline"
        >
          refresh
        </button>
      </div>
      {uploads.length === 0 ? (
        <div className="text-[10.5px] text-faint">
          Nothing staged — stale uploads are swept automatically.
        </div>
      ) : (
        <div className="max-h-[180px] space-y-1 overflow-y-auto">
          {uploads.map((u) => (
            <div
              key={u.upload_id}
              className="flex items-center gap-2 rounded-md border border-hairline px-2 py-1"
            >
              <div className="min-w-0 flex-1">
                <div className="truncate font-mono text-[10px] text-fg">{u.upload_id}</div>
                <div className="font-mono text-[9px] text-faint">
                  {formatBytes(u.size_bytes)} · {u.n_files} file{u.n_files === 1 ? "" : "s"}
                  {u.open_dataset_ids.length > 0 &&
                    ` · ${u.open_dataset_ids.length} open dataset${u.open_dataset_ids.length === 1 ? "" : "s"}`}
                </div>
              </div>
              <button
                type="button"
                onClick={() =>
                  armId === u.upload_id
                    ? (setArmId(null), void deleteUpload(u.upload_id))
                    : setArmId(u.upload_id)
                }
                onBlur={() => setArmId(null)}
                title="Delete the staged files (open datasets backed by them are closed)"
                className={cn(
                  "rounded-sm border px-1.5 py-px font-mono text-[9px]",
                  armId === u.upload_id
                    ? "border-danger bg-danger-soft text-danger"
                    : "border-hairline text-muted hover:border-border hover:text-fg",
                )}
              >
                {armId === u.upload_id ? "sure?" : "delete"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function formatBytes(n: number): string {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} GB`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)} MB`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)} kB`;
  return `${n} B`;
}

function RunRow({
  run,
  busy,
  onOpen,
}: {
  run: WaveRunInfo;
  busy: boolean;
  onOpen: () => void;
}) {
  const pruneRun = useWaveviewStore((s) => s.pruneRun);
  // free-raws is destructive (drops the run's sim/ waveforms) → two-step arm
  const [arm, setArm] = useState(false);
  const [pruning, setPruning] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  const prune = async () => {
    setArm(false);
    setPruning(true);
    setNote(await pruneRun(run.run_id));
    setPruning(false);
  };

  const pruned = !!run.retention_pruned;
  return (
    <div className="flex w-full items-center gap-2 rounded-md border border-hairline px-2.5 py-1.5 hover:border-border hover:bg-hairline">
      <button
        type="button"
        disabled={busy}
        onClick={onOpen}
        className="min-w-0 flex-1 text-left"
      >
        <div className="truncate text-[11px] font-medium text-fg">
          {run.label ?? run.run_id}
        </div>
        <div className="truncate font-mono text-[9.5px] text-faint">
          {run.run_id}
          {run.algorithm ? ` · ${run.algorithm}` : ""}
          {run.active_corner ? ` · ${run.active_corner}` : ""}
        </div>
      </button>
      {note && <span className="font-mono text-[9px] text-tertiary">{note}</span>}
      {pruned ? (
        <Badge variant="neutral">pruned</Badge>
      ) : (
        run.keep_raw && (
          <>
            <Badge variant="indigo" dot>
              keep_raw
            </Badge>
            {run.status !== "running" && (
              <button
                type="button"
                disabled={pruning}
                onClick={() => (arm ? void prune() : setArm(true))}
                onBlur={() => setArm(false)}
                title="Drop this run's sim/ waveforms (metrics_only retention) — the record and history stay"
                className={cn(
                  "rounded-sm border px-1.5 py-px font-mono text-[9px]",
                  arm
                    ? "border-danger bg-danger-soft text-danger"
                    : "border-hairline text-muted hover:border-border hover:text-fg",
                )}
              >
                {pruning ? "pruning…" : arm ? "sure?" : "free raws"}
              </button>
            )}
          </>
        )
      )}
      <Badge
        variant={
          run.status === "done" ? "ok" : run.status === "running" ? "live" : "neutral"
        }
      >
        {run.status ?? "?"}
      </Badge>
    </div>
  );
}
