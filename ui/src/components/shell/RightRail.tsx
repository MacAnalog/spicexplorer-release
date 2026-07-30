"use client";
import { PanelRightClose } from "lucide-react";
import { useMemo, useRef } from "react";
import { usePathname } from "next/navigation";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { ResizeHandle, useRailSize } from "@/components/ui/resizable";
import { Stat } from "@/components/ui/stat";
import { Badge } from "@/components/ui/badge";
import { SpecChip } from "@/components/ui/spec-chip";
import { formatEng, goalSymbol, statusForGoal } from "@/lib/utils";
import { viewForPath } from "./nav";

/**
 * Always-on right rail: live run progress + spec status + best params. Hoisted
 * out of OptimizeTab so it's visible on every view and keeps updating during a
 * run regardless of which view is mounted (the SSE stream lives in runStore).
 */
export function RightRail() {
  const pathname = usePathname();
  const rightOpen = useUIStore((s) => s.rightOpen);
  const toggleRight = useUIStore((s) => s.toggleRight);
  const summary = useProjectStore((s) => s.summary);
  const railRef = useRef<HTMLElement>(null);
  const [railWidth, setRailWidth] = useRailSize("ui:rail:shell-right", 300, 220, 520);
  const { isRunning, isReplay, events, bestMetrics, bestParams, currentIter, budget, checkpoints } =
    useRunStore();

  const bestScore = useMemo(() => {
    if (!events.length) return "—";
    // best_score is a running maximum (higher is better). Use the maximum
    // (== the final value), not Math.min which returned the first/worst. Reduce
    // instead of spreading to avoid a stack overflow on long runs.
    const best = events.reduce((m, e) => {
      const v = e.best_score ?? e.score;
      return v != null && Number.isFinite(v) && v > m ? v : m;
    }, -Infinity);
    return Number.isFinite(best) ? formatEng(best) : "—";
  }, [events]);

  const specStatuses = useMemo(() => {
    if (!summary) return [];
    return summary.target_specs.map((spec) => {
      const val = bestMetrics[spec.name];
      // Shared tolerance-aware verdict (HealthTab/ExplorerTab use the same), so the rail
      // can't disagree with other surfaces. The old inline check ignored tolerance for
      // exceed/minimize and defaulted exact's tolerance to Infinity (too lenient).
      const verdict = statusForGoal(spec.goal, val, spec.target, spec.tolerance ?? undefined);
      const status: "ok" | "fail" | "neutral" =
        verdict === "pass" ? "ok" : verdict === "fail" ? "fail" : "neutral";
      const goalSym = goalSymbol(spec.goal);
      return { spec, val, status, goalSym };
    });
  }, [summary, bestMetrics]);

  // fullBleed views (Library) supply their own rails — hide the shell's.
  if (viewForPath(pathname)?.fullBleed) return null;
  if (!rightOpen) return null;

  return (
    <aside
      ref={railRef}
      style={{ width: railWidth }}
      className="relative flex shrink-0 flex-col border-l border-border bg-panel text-xs"
    >
      <ResizeHandle
        edge="left"
        size={railWidth}
        compute={(x) => (railRef.current?.getBoundingClientRect().right ?? 0) - x}
        onSize={setRailWidth}
        resetTo={300}
        label="Resize the run rail"
      />
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="text-[11px] font-medium uppercase tracking-wide text-faint">
          Run
        </span>
        <div className="flex items-center gap-2">
          {isRunning && (
            <Badge variant="live" dot pulse>
              {isReplay ? "replay" : "live"}
            </Badge>
          )}
          <button
            type="button"
            onClick={toggleRight}
            aria-label="Collapse right rail"
            title="Collapse"
            className="rounded-sm p-0.5 text-faint hover:bg-hairline hover:text-fg"
          >
            <PanelRightClose className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3 space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <Stat eyebrow="iteration" value={currentIter > 0 ? String(currentIter) : "—"} />
          <Stat eyebrow="best score" value={bestScore} />
        </div>
        {budget > 0 && (
          <div className="h-1 overflow-hidden rounded-sm bg-hairline">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${Math.min(100, (currentIter / budget) * 100)}%` }}
            />
          </div>
        )}
        {checkpoints.length > 0 && (
          <div className="text-[10px] text-faint">
            {checkpoints.length} checkpoint{checkpoints.length === 1 ? "" : "s"} saved
            <span className="ml-1 font-mono">@{checkpoints[checkpoints.length - 1].iter}</span>
          </div>
        )}

        <div>
          <div className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-faint">
            Spec status
          </div>
          {specStatuses.length === 0 ? (
            <div className="rounded-sm border border-dashed border-border px-2 py-3 text-center text-[11px] text-faint">
              Apply a project to see live specs.
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {specStatuses.map(({ spec, val, status, goalSym }) => (
                <SpecChip
                  key={spec.name}
                  name={spec.name}
                  value={val != null ? formatEng(val) : "—"}
                  target={`${goalSym}${formatEng(spec.target)}`}
                  status={status}
                />
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-faint">
            Best params
          </div>
          <div className="overflow-hidden rounded-sm border border-border">
            <table className="w-full table-fixed text-xs">
              <tbody>
                {Object.entries(bestParams).map(([k, v]) => (
                  <tr key={k} className="border-b border-border last:border-0">
                    <td className="max-w-0 truncate px-2 py-1 font-mono text-muted" title={k}>{k}</td>
                    <td className="max-w-0 truncate px-2 py-1 text-right font-mono" title={formatEng(v)}>{formatEng(v)}</td>
                  </tr>
                ))}
                {Object.keys(bestParams).length === 0 && (
                  <tr>
                    <td className="px-2 py-2 text-center text-muted">No params yet</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </aside>
  );
}
