"use client";
import { useEffect, useRef, useState } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { ChevronDown, Play, Square } from "lucide-react";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore, RUN_ALGORITHMS_FALLBACK } from "@/stores/uiStore";
import { api } from "@/lib/api";
import { launchLiveRun } from "@/lib/launchRun";
import { selectCn } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { CornerSelect } from "@/components/pvt/CornerSelect";
import { cn } from "@/lib/utils";

/**
 * Title-bar "Run ▾" control. The chevron opens a popover holding the ephemeral
 * live-run overrides (algorithm / budget / seed) shared with the Optimize
 * toolbar via uiStore.runConfig, plus a Start button that launches a live run
 * from any view. While a run is active the control collapses to a Stop button
 * with live progress. When the PDK is missing, Start is disabled and the user
 * is steered to Replay on the Optimize view.
 */
export function RunControl() {
  const router = useRouter();
  const isApplied = useProjectStore((s) => s.isApplied);
  const pvt = useProjectStore((s) => s.summary?.pvt ?? null);
  const projectAlgo = useProjectStore((s) => s.summary?.optimizer?.name ?? null);
  const { isRunning, isReplay, currentIter, budget, stopRun } = useRunStore();
  const env = useUIStore((s) => s.env);
  const runConfig = useUIStore((s) => s.runConfig);
  const setRunConfig = useUIStore((s) => s.setRunConfig);
  const algorithms = useUIStore((s) => s.algorithms);
  const setAlgorithms = useUIStore((s) => s.setAlgorithms);

  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);

  // The applied project's YAML algorithm is the natural default for its runs —
  // its optimizer_kwargs only take effect when the name matches (the backend
  // drops them on an override). Re-seeds on every apply; a manual pick after
  // that sticks until the next apply.
  useEffect(() => {
    if (projectAlgo) setRunConfig({ algorithm: projectAlgo });
  }, [projectAlgo, setRunConfig]);

  // Backend-derived algorithm lists, fetched once on first popover open.
  useEffect(() => {
    if (!open || algorithms) return;
    let cancelled = false;
    api
      .optimizeAlgorithms()
      .then((a) => {
        if (!cancelled) setAlgorithms(a);
      })
      .catch(() => {}); // fallback list keeps the popover usable
    return () => {
      cancelled = true;
    };
  }, [open, algorithms, setAlgorithms]);

  // Close on click-outside / Escape while the popover is open.
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const liveDisabled = env != null && !env.live_runs_enabled;
  const canStart = isApplied && !liveDisabled && !busy;

  // Grouped options: curated set first, then the configurable families, then
  // the full preset registry. All backend-derived; the fallback trio only
  // bridges until /api/optimize/algorithms responds.
  const recommended = algorithms?.recommended ?? [...RUN_ALGORITHMS_FALLBACK];
  const familyRest = (algorithms?.families ?? []).filter((n) => !recommended.includes(n));
  const registryRest = (algorithms?.registry ?? []).filter((n) => !recommended.includes(n));
  const currentUnlisted =
    !recommended.includes(runConfig.algorithm) &&
    !familyRest.includes(runConfig.algorithm) &&
    !registryRest.includes(runConfig.algorithm);
  const algoLabel = (n: string) => (n === projectAlgo ? `${n} — project default` : n);

  const handleStart = async () => {
    setBusy(true);
    setError(null);
    const res = await launchLiveRun();
    setBusy(false);
    if (res.ok) {
      setOpen(false);
      // Land the user on the run monitor so progress (or a failure) is visible
      // immediately — a run that dies at setup otherwise looks like "nothing ran".
      router.push("/optimize" as Route);
    } else {
      setError(res.error ?? "Failed to start run");
    }
  };

  // Active run → Stop + progress (overrides can't change mid-run).
  if (isRunning) {
    return (
      <div className="flex items-center gap-2">
        <span className="flex items-center gap-1.5 text-[11px] text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-primary obs-pulse" aria-hidden />
          {isReplay ? "replay" : "live"}
          {budget > 0 && (
            <span className="font-mono">
              {currentIter}/{budget}
            </span>
          )}
        </span>
        <Button variant="danger" onClick={stopRun}>
          <Square className="h-3 w-3" aria-hidden />
          Stop
        </Button>
      </div>
    );
  }

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="dialog"
        aria-expanded={open}
        title="Configure and start a live run"
        className={cn(
          "flex items-center gap-1.5 rounded-md border border-primary bg-primary px-2 py-1 text-[11px] font-medium text-white transition hover:bg-[#4338ca]",
        )}
      >
        <Play className="h-3 w-3" aria-hidden />
        Run
        <ChevronDown
          className={cn("h-3 w-3 transition-transform", open && "rotate-180")}
          aria-hidden
        />
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Run configuration"
          className="absolute right-0 top-full z-50 mt-1.5 w-[260px] rounded-lg border border-border bg-panel p-3 text-xs shadow-soft"
        >
          <div className="mb-2 text-[10px] font-medium uppercase tracking-wider text-faint">
            Run configuration
          </div>

          <div className="flex flex-col gap-2.5">
            <label className="flex flex-col gap-1">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                algorithm
              </span>
              <select
                aria-label="Optimization algorithm"
                value={runConfig.algorithm}
                onChange={(e) => setRunConfig({ algorithm: e.target.value })}
                className={selectCn("sm") + " w-full"}
              >
                {currentUnlisted && (
                  <option value={runConfig.algorithm}>{algoLabel(runConfig.algorithm)}</option>
                )}
                <optgroup label="Recommended">
                  {recommended.map((a) => (
                    <option key={a} value={a}>
                      {algoLabel(a)}
                    </option>
                  ))}
                </optgroup>
                {familyRest.length > 0 && (
                  <optgroup label="Configurable families (kwargs from YAML)">
                    {familyRest.map((a) => (
                      <option key={a} value={a}>
                        {algoLabel(a)}
                      </option>
                    ))}
                  </optgroup>
                )}
                {registryRest.length > 0 && (
                  <optgroup label={`All presets (${registryRest.length})`}>
                    {registryRest.map((a) => (
                      <option key={a} value={a}>
                        {algoLabel(a)}
                      </option>
                    ))}
                  </optgroup>
                )}
              </select>
            </label>

            <div className="grid grid-cols-2 gap-2">
              <label className="flex flex-col gap-1">
                <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                  budget
                </span>
                <input
                  aria-label="Run budget (iterations)"
                  type="number"
                  min={10}
                  max={5000}
                  value={runConfig.budget}
                  onChange={(e) => setRunConfig({ budget: Number(e.target.value) })}
                  className={selectCn("sm") + " w-full"}
                />
              </label>
              <label className="flex flex-col gap-1">
                <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                  seed
                </span>
                <input
                  aria-label="Random seed (blank = auto)"
                  type="number"
                  placeholder="auto"
                  value={runConfig.seed ?? ""}
                  onChange={(e) =>
                    setRunConfig({ seed: e.target.value === "" ? null : Number(e.target.value) })
                  }
                  className={selectCn("sm") + " w-full"}
                />
              </label>
            </div>

            {pvt && pvt.corners.length > 0 && (
              <label className="flex flex-col gap-1">
                <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                  PVT corner
                </span>
                <CornerSelect
                  corners={pvt.corners}
                  value={runConfig.activeCorner}
                  defaultCorner={pvt.active_corner}
                  onChange={(name) => setRunConfig({ activeCorner: name })}
                  aria-label="PVT corner to optimize against"
                />
              </label>
            )}

            <label className="flex flex-col gap-1">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                autosave every (trials)
              </span>
              <input
                aria-label="Autosave checkpoint every N trials (blank = end only)"
                type="number"
                min={1}
                placeholder="end only"
                value={runConfig.autosaveEvery ?? ""}
                onChange={(e) =>
                  setRunConfig({
                    autosaveEvery: e.target.value === "" ? null : Number(e.target.value),
                  })
                }
                className={selectCn("sm") + " w-full"}
              />
              <span className="text-[10px] leading-snug text-faint">
                Periodic, resumable checkpoints for long runs.
              </span>
            </label>
          </div>

          {error && (
            <div
              role="alert"
              className="mt-2.5 rounded-sm border border-danger bg-danger-soft px-2 py-1.5 text-[11px] text-danger"
            >
              {error}
            </div>
          )}

          {!isApplied && !error && (
            <p className="mt-2.5 text-[11px] leading-snug text-faint">
              Apply a project on Setup to start a live run.
            </p>
          )}
          {isApplied && liveDisabled && !error && (
            <p className="mt-2.5 text-[11px] leading-snug text-[#b45309]">
              PDK missing — live runs are disabled. Replay a cached checkpoint instead.
            </p>
          )}

          <div className="mt-3 flex items-center justify-between gap-2">
            {liveDisabled ? (
              <Button
                variant="secondary"
                onClick={() => {
                  setOpen(false);
                  router.push("/optimize" as Route);
                }}
              >
                Go to Replay
              </Button>
            ) : (
              <span />
            )}
            <Button variant="primary" onClick={handleStart} disabled={!canStart}>
              {busy ? "Starting…" : "Start run"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
