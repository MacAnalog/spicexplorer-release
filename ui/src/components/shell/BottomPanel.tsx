"use client";
import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { X } from "lucide-react";
import { UI } from "@/config";
import { ResizeHandle, useRailSize } from "@/components/ui/resizable";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { cn, formatEng } from "@/lib/utils";
import { viewForPath } from "./nav";
import type { BottomTab } from "@/stores/uiStore";

// Hoisted to module scope (not defined inside BottomPanel): an inner component is
// a new type each render and remounts. Presentational — active tab + handler as props.
function TabBtn({
  id,
  label,
  badge,
  activeTab,
  onSelect,
}: {
  id: BottomTab;
  label: string;
  badge?: number;
  activeTab: BottomTab;
  onSelect: (id: BottomTab) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(id)}
      className={cn(
        "border-b-[1.5px] px-3 py-1.5 text-[12px] transition",
        activeTab === id
          ? "border-primary font-medium text-primary"
          : "border-transparent text-muted hover:text-fg",
      )}
    >
      {label}
      {badge ? <span className="ml-1.5 text-[10px] text-faint">{badge}</span> : null}
    </button>
  );
}

/**
 * Collapsible bottom panel with two tabs, both rendered from runStore (so they
 * keep filling during a run even on another view):
 *   • Optimizer log — the structured per-trial summary (score / best).
 *   • SpiceXplorer log — the raw, human-readable library log for the ACTIVE run
 *     (per-run: reset when a run starts, kept after it finishes for inspection).
 * Toggled from the StatusBar.
 */
export function BottomPanel() {
  const bottomOpen = useUIStore((s) => s.bottomOpen);
  const bottomTab = useUIStore((s) => s.bottomTab);
  const toggleBottom = useUIStore((s) => s.toggleBottom);
  const setBottomTab = useUIStore((s) => s.setBottomTab);
  const events = useRunStore((s) => s.events);
  const logLines = useRunStore((s) => s.logLines);
  const pathname = usePathname();
  const panelRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useRailSize("ui:panel:shell-bottom", 192, 96, 560);

  // fullBleed views (Library) hide the shell's bottom panel — they own their own log
  if (!bottomOpen || viewForPath(pathname)?.fullBleed) return null;

  return (
    <div
      ref={panelRef}
      style={{ height }}
      className="relative flex shrink-0 flex-col border-t border-border bg-panel"
    >
      <ResizeHandle
        edge="top"
        size={height}
        compute={(y) => (panelRef.current?.getBoundingClientRect().bottom ?? 0) - y}
        onSize={setHeight}
        resetTo={192}
        label="Resize the bottom panel"
      />
      <div className="flex items-center justify-between border-b border-border px-2">
        <div className="flex items-stretch">
          <TabBtn id="log" label="Optimizer log" activeTab={bottomTab} onSelect={setBottomTab} />
          <TabBtn
            id="rawlog"
            label={`${UI.brand.name} log`}
            badge={logLines.length || undefined}
            activeTab={bottomTab}
            onSelect={setBottomTab}
          />
        </div>
        <button
          type="button"
          onClick={toggleBottom}
          aria-label="Close bottom panel"
          title="Close"
          className="rounded-sm p-1 text-faint hover:bg-hairline hover:text-fg"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      {bottomTab === "log" ? (
        <OptimizerLog events={events} />
      ) : (
        <RawLog lines={logLines} />
      )}
    </div>
  );
}

function OptimizerLog({ events }: { events: ReturnType<typeof useRunStore.getState>["events"] }) {
  // Show the most recent lines (cap for perf on long replays).
  const lines = events.slice(-500);
  return (
    <div className="min-h-0 flex-1 overflow-y-auto p-2 font-mono text-[11px] leading-relaxed text-muted">
      {lines.length === 0 ? (
        <div className="px-1 py-2 text-faint">
          No run yet — start a run or replay a checkpoint to stream the log.
        </div>
      ) : (
        lines.map((e, i) => {
          const iter = e.iter != null ? `#${e.iter}` : "·";
          const score = e.score != null ? formatEng(e.score) : "—";
          const best = e.best_score != null ? formatEng(e.best_score) : "—";
          return (
            <div key={i} className="whitespace-pre">
              <span className="text-faint">{iter.padStart(5)}</span>{"  "}
              score=<span className="text-fg">{score}</span>{"  "}
              best=<span className="text-primary">{best}</span>
            </div>
          );
        })
      )}
    </div>
  );
}

function levelClass(level: string): string {
  switch (level) {
    case "ERROR":
    case "CRITICAL":
      return "text-danger";
    case "WARNING":
      return "text-[#b45309]";
    case "DEBUG":
      return "text-faint";
    default:
      return "text-muted";
  }
}

function RawLog({ lines }: { lines: ReturnType<typeof useRunStore.getState>["logLines"] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  // Auto-scroll to the newest line as the run streams (only when already at bottom
  // so a user scrolled up to read isn't yanked back down).
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    if (nearBottom) el.scrollTop = el.scrollHeight;
  }, [lines]);

  return (
    <div
      ref={scrollRef}
      className="min-h-0 flex-1 overflow-y-auto p-2 font-mono text-[11px] leading-relaxed"
    >
      {lines.length === 0 ? (
        <div className="px-1 py-2 text-faint">
          No run yet — start a live run to stream the {UI.brand.name} library log here.
        </div>
      ) : (
        lines.map((l, i) => (
          <div key={i} className={cn("whitespace-pre-wrap break-all", levelClass(l.level))}>
            {l.text}
          </div>
        ))
      )}
    </div>
  );
}
