"use client";
import { usePathname } from "next/navigation";
import { PanelBottom, PanelRight } from "lucide-react";
import { UI } from "@/config";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";
import { viewForPath } from "./nav";

function Dot({ className }: { className: string }) {
  return <span className={cn("inline-block h-1.5 w-1.5 rounded-full", className)} aria-hidden />;
}

/**
 * Bottom status strip — always-on summary of project, active run, and the
 * simulator/PDK environment. The PDK pill is the first-class surfacing of the
 * graceful-degradation state (see /api/env): on a PDK-less machine it reads
 * "PDK missing — replay only" so the limitation is explicit, not a silent error.
 */
export function StatusBar() {
  const pathname = usePathname();
  const view = viewForPath(pathname);
  const { summary, isApplied } = useProjectStore();
  // fullBleed views (Library) own their own status bar
  const hidden = view?.fullBleed;
  const { isRunning, isReplay, currentIter, budget } = useRunStore();
  const env = useUIStore((s) => s.env);
  const { rightOpen, bottomOpen, toggleRight, toggleBottom } = useUIStore();

  // Environment pill
  let envDot = "bg-faint";
  let envText = "sim: checking…";
  if (env) {
    if (!env.ngspice_ok) {
      envDot = "bg-danger";
      envText = "ngspice missing";
    } else if (env.pdk_ok) {
      envDot = "bg-ok";
      envText = "sim ready";
    } else {
      envDot = "bg-tertiary";
      envText = "PDK missing — replay only";
    }
  }

  if (hidden) return null; // Library (fullBleed) renders its own status bar

  return (
    <footer className="flex h-6 shrink-0 items-center gap-3 overflow-hidden border-t border-border bg-panel px-3 text-[11px] text-muted">
      <span className="shrink-0 font-medium text-fg">{view?.label ?? UI.brand.product}</span>

      <span className="shrink-0 text-faint">·</span>
      <span className="min-w-0 truncate">
        {summary?.name ?? "no project"}
        <span className="ml-1 font-mono text-faint">{isApplied ? "active" : "draft"}</span>
      </span>

      {isRunning && (
        <>
          <span className="text-faint">·</span>
          <span className="flex items-center gap-1.5 text-fg">
            <Dot className="bg-primary obs-pulse" />
            {isReplay ? "replay" : "live"}
            {budget > 0 && (
              <span className="font-mono text-muted">
                {currentIter}/{budget}
              </span>
            )}
          </span>
        </>
      )}

      <div className="flex-1" />

      <button
        type="button"
        onClick={toggleBottom}
        aria-label="Toggle optimizer log panel"
        title={bottomOpen ? "Hide optimizer log" : "Show optimizer log"}
        className={cn(
          "rounded-sm p-0.5 hover:bg-hairline hover:text-fg",
          bottomOpen ? "text-primary" : "text-faint",
        )}
      >
        <PanelBottom className="h-3.5 w-3.5" />
      </button>
      <button
        type="button"
        onClick={toggleRight}
        aria-label="Toggle run rail"
        title={rightOpen ? "Hide run rail" : "Show run rail"}
        className={cn(
          "rounded-sm p-0.5 hover:bg-hairline hover:text-fg",
          rightOpen ? "text-primary" : "text-faint",
        )}
      >
        <PanelRight className="h-3.5 w-3.5" />
      </button>

      <span className="text-faint">·</span>
      <span
        className="flex items-center gap-1.5"
        title={env?.pdk_detail ?? "Probing simulator + PDK availability…"}
      >
        <Dot className={envDot} />
        {envText}
      </span>
    </footer>
  );
}
