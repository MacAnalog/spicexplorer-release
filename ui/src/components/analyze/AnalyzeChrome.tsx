"use client";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { ResizeHandle, useRailSize } from "@/components/ui/resizable";
import { useUIStore } from "@/stores/uiStore";
import { useWaveviewStore } from "@/stores/waveviewStore";
import { analysisLabel } from "@/lib/waveview/selectors";

/** Meta strip — one mono line of facts about the active dataset+analysis,
 *  plus the sweep-mode pill (single run / N corners / N samples). */
export function MetaStrip() {
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeId = useWaveviewStore((s) => s.activeId);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const cornerEnabled = useWaveviewStore((s) => s.cornerEnabled);

  const ds = datasets.find((d) => d.dataset_id === activeId);
  if (!ds) return null;
  const a = ds.analyses.find((x) => x.analysis === activeAnalysis);
  const name = ds.path.split("/").filter(Boolean).pop() ?? ds.path;
  const enabled = sweepMembers.filter((m) => cornerEnabled[m.key] ?? true).length;
  const modeText =
    sweepMode === "pvt"
      ? `${enabled} corners`
      : sweepMode === "mc"
        ? `${sweepMembers.length} samples`
        : "single run";

  return (
    <div className="flex h-[30px] shrink-0 items-center gap-2.5 overflow-hidden whitespace-nowrap border-b border-hairline bg-panel px-3 font-mono text-[10px] text-muted">
      <span className="shrink-0 font-semibold text-fg">{name}</span>
      <span
        className={cn(
          "shrink-0 rounded-sm px-1.5 py-px text-[9.5px] font-semibold",
          ds.engine === "spectre"
            ? "bg-secondary-soft text-secondary"
            : "bg-primary-soft text-primary",
        )}
      >
        {ds.engine === "spectre" ? "spectre-psf" : "ngspice-raw"}
      </span>
      {a?.sweep && <span className="shrink-0">sweep={a.sweep}</span>}
      {a && <span className="shrink-0">{a.n_points} pts</span>}
      {a && <span className="shrink-0">{a.signals.length} signals</span>}
      <span className={cn("shrink-0", ds.warnings.length ? "text-tertiary" : "text-ok")}>
        {ds.warnings.length} warnings
      </span>
      <span
        className={cn(
          "shrink-0 rounded-sm px-1.5 py-px font-sans text-[9px] font-semibold",
          sweepMode === "pvt"
            ? "bg-primary-soft text-primary"
            : sweepMode === "mc"
              ? "bg-ok-soft text-ok"
              : "bg-hairline text-muted",
        )}
      >
        {modeText}
      </span>
      <div className="flex-1" />
      <span className="truncate text-faint" title={ds.path}>
        {ds.path}
      </span>
    </div>
  );
}

const LEVEL_COLOR: Record<string, string> = {
  error: "text-danger",
  warning: "text-tertiary",
  note: "text-secondary",
  info: "text-muted",
};
const LEVEL_RANK: Record<string, number> = { info: 0, note: 1, warning: 2, error: 3 };
const LEVEL_FLOORS = [
  { value: 0, label: "all" },
  { value: 1, label: "note+" },
  { value: 2, label: "warn+" },
  { value: 3, label: "errors" },
] as const;

/** Bottom sim-log bar (26px) + expandable SSE tail of the dataset's log file.
 *  Debug-oriented: vertically resizable (drag the top edge), severity floor,
 *  copy-visible-lines, and a follow toggle (auto-scroll pauses for reading). */
export function LogBar() {
  const activeId = useWaveviewStore((s) => s.activeId);
  const datasets = useWaveviewStore((s) => s.datasets);
  const logLines = useWaveviewStore((s) => s.logLines);
  const logCounts = useWaveviewStore((s) => s.logCounts);
  const logOpen = useWaveviewStore((s) => s.logOpen);
  const logStreaming = useWaveviewStore((s) => s.logStreaming);
  const toggleLogOpen = useWaveviewStore((s) => s.toggleLogOpen);

  const [floor, setFloor] = useState(0);
  const [follow, setFollow] = useState(true);
  const [copied, setCopied] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useRailSize("ui:panel:analyze-log", 144, 64, 560);

  const shown = logLines.filter((l) => (LEVEL_RANK[l.level] ?? 0) >= floor);
  useEffect(() => {
    if (logOpen && follow && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logOpen, follow, shown.length]);

  const ds = datasets.find((d) => d.dataset_id === activeId);
  const logName = ds?.log_path?.split("/").filter(Boolean).pop();
  const errors = logCounts.error ?? 0;
  const warnings = logCounts.warning ?? 0;

  const copyVisible = () => {
    void navigator.clipboard
      .writeText(shown.map((l) => `${l.no}\t${l.level}\t${l.text}`).join("\n"))
      .then(() => {
        setCopied(true);
        window.setTimeout(() => setCopied(false), 1200);
      });
  };

  return (
    <div className="shrink-0 border-t border-border bg-panel">
      {logOpen && (
        <div ref={panelRef} style={{ height }} className="relative border-b border-hairline">
          <ResizeHandle
            edge="top"
            size={height}
            compute={(y) => (panelRef.current?.getBoundingClientRect().bottom ?? 0) - y}
            onSize={setHeight}
            resetTo={144}
            label="Resize the sim log panel"
          />
          <div ref={scrollRef} className="h-full overflow-y-auto px-3 py-1">
            {logLines.length === 0 ? (
              <div className="py-2 font-mono text-[10px] leading-relaxed text-faint">
                {ds?.log_path ? (
                  <>log is empty — {ds.log_path}</>
                ) : ds ? (
                  <>
                    no log attached to this dataset · logs are auto-discovered beside the
                    artifact (same-stem <span className="text-muted">.log</span>), or pass{" "}
                    <span className="text-muted">log_path</span> when opening
                  </>
                ) : (
                  "no dataset open"
                )}
              </div>
            ) : shown.length === 0 ? (
              <div className="py-2 font-mono text-[10px] text-faint">
                no lines at this severity — {logLines.length} total below the floor
              </div>
            ) : (
              shown.map((l) => (
                <div key={l.no} className="flex gap-2 font-mono text-[10px] leading-normal">
                  <span className="w-10 shrink-0 text-right text-faint">{l.no}</span>
                  <span className={cn("w-14 shrink-0", LEVEL_COLOR[l.level] ?? "text-muted")}>
                    {l.level}
                  </span>
                  <span className="whitespace-pre-wrap break-all text-fg">{l.text}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
      <div className="flex h-[26px] items-center gap-3 px-3">
        <button
          type="button"
          onClick={toggleLogOpen}
          className="text-[10px] font-semibold text-muted hover:text-fg"
        >
          {logOpen ? "▾" : "▸"} sim log
        </button>
        <span
          className={cn(
            "flex items-center gap-1.5 font-mono text-[10px]",
            errors ? "text-danger" : warnings ? "text-tertiary" : "text-ok",
          )}
        >
          <span
            className={cn(
              "inline-block h-1.5 w-1.5 rounded-full",
              errors ? "bg-danger" : warnings ? "bg-tertiary" : "bg-ok",
            )}
            aria-hidden
          />
          {errors ? `${errors} errors` : `${warnings} warnings`}
        </span>
        {logName && (
          <span className="truncate font-mono text-[10px] text-faint" title={ds?.log_path ?? ""}>
            {logName}
            {logStreaming && " · streaming (SSE)"}
          </span>
        )}
        {logOpen && (
          <>
            <span className="font-mono text-[9.5px] text-faint">
              {shown.length}/{logLines.length} lines
            </span>
            <div className="flex items-center gap-0.5">
              {LEVEL_FLOORS.map((f) => (
                <button
                  key={f.value}
                  type="button"
                  onClick={() => setFloor(f.value)}
                  className={cn(
                    "rounded-sm px-1.5 py-px font-mono text-[9px] transition",
                    floor === f.value
                      ? "bg-primary-soft font-semibold text-primary"
                      : "text-faint hover:bg-hairline hover:text-fg",
                  )}
                >
                  {f.label}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setFollow((v) => !v)}
              title="Auto-scroll to new lines"
              className={cn(
                "rounded-sm px-1.5 py-px font-mono text-[9px] transition",
                follow
                  ? "bg-primary-soft font-semibold text-primary"
                  : "text-faint hover:bg-hairline hover:text-fg",
              )}
            >
              follow
            </button>
            <button
              type="button"
              onClick={copyVisible}
              disabled={shown.length === 0}
              className="rounded-sm px-1.5 py-px font-mono text-[9px] text-faint transition hover:bg-hairline hover:text-fg disabled:opacity-40"
            >
              {copied ? "copied ✓" : "copy"}
            </button>
          </>
        )}
        <div className="flex-1" />
        <span className="font-mono text-[9.5px] text-faint">GET /waveview/log/stream</span>
      </div>
    </div>
  );
}

/** The Analyze view's own indigo status bar (fullBleed hides the shell's). */
export function AnalyzeStatusBar() {
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const env = useUIStore((s) => s.env);

  const simReady = !!env?.ngspice_ok && !!env?.pdk_ok;
  const simText = !env
    ? "sim: checking…"
    : simReady
      ? "sim ready"
      : env.ngspice_ok
        ? "PDK missing — open results only"
        : "ngspice missing";

  return (
    <div className="flex h-6 shrink-0 items-center gap-2 bg-primary px-3 text-[10.5px] text-[#e0e7ff]">
      <span className="font-semibold">Analyze</span>
      <span className="opacity-60">▸</span>
      <span>Waveforms</span>
      {activeAnalysis && (
        <>
          <span className="opacity-60">›</span>
          <span className="font-mono">{analysisLabel(activeAnalysis)}</span>
        </>
      )}
      <span className="font-mono opacity-70">
        · {datasets.length} dataset{datasets.length === 1 ? "" : "s"}
      </span>
      <div className="flex-1" />
      <span className="font-mono opacity-80">spicexplorer-waveview</span>
      <span className="opacity-50">·</span>
      <span className="inline-flex items-center gap-1 font-mono">
        <span
          className={cn(
            "inline-block h-1.5 w-1.5 rounded-full",
            simReady ? "bg-[#a7f3d0]" : "bg-[#fcd34d]",
          )}
          aria-hidden
        />
        {simText}
      </span>
    </div>
  );
}
