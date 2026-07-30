"use client";
import { useRef } from "react";
import { ChevronDown, ChevronRight, X } from "lucide-react";
import { UI } from "@/config";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ResizeHandle, useRailWidth } from "@/components/ui/resizable";
import { useWaveviewStore } from "@/stores/waveviewStore";
import type { WaveAnalysisMeta, WaveDatasetMeta } from "@/types/api";
import { PREFERRED_MEASURES } from "@/lib/waveview/config";
import { signalRoles } from "@/lib/waveview/figure";
import {
  analysisLabel,
  baseAnalysis,
  datasetShortName,
  orderedAnalyses,
  plottableSignals,
} from "@/lib/waveview/selectors";

/** Left rail — DATASETS · TRACES. Every row derives from opened DatasetMeta:
 *  dataset header → analysis rows → (active) signal checkboxes + metric hints.
 *  Width is user-adjustable (drag the right edge; double-click resets; persisted). */
export function DatasetTree() {
  const allDatasets = useWaveviewStore((s) => s.datasets);
  const sweepDatasetIds = useWaveviewStore((s) => s.sweepDatasetIds);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const openImport = useWaveviewStore((s) => s.openImport);
  const ref = useRef<HTMLElement>(null);
  const [width, setWidth] = useRailWidth("ui:rail:analyze-tree", 246, 180, 480);

  // Sweep-opened corner/sample datasets are machinery, not user entries — the
  // axes rail's corner list is their surface; keep the tree to what was opened
  // deliberately.
  const datasets = allDatasets.filter((d) => !sweepDatasetIds.includes(d.dataset_id));

  return (
    <aside
      ref={ref}
      style={{ width }}
      className="relative flex shrink-0 flex-col border-r border-border bg-panel"
    >
      <ResizeHandle
        edge="right"
        size={width}
        compute={(x) => x - (ref.current?.getBoundingClientRect().left ?? 0)}
        onSize={setWidth}
        resetTo={246}
        label="Resize the datasets panel"
      />
      <div className="flex h-[34px] shrink-0 items-center justify-between border-b border-hairline px-3.5">
        <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted">
          Datasets · Traces
        </span>
        <button
          type="button"
          onClick={openImport}
          className="text-[10.5px] font-semibold text-primary hover:underline"
        >
          + Open
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto py-1.5">
        {datasets.length === 0 ? (
          <div className="px-3.5 py-4 text-[11px] leading-relaxed text-faint">
            {UI.analyze.tree.emptyHint}
          </div>
        ) : (
          datasets.map((ds) => <DatasetNode key={ds.dataset_id} ds={ds} />)
        )}
        {sweepMode !== "single" && sweepMembers.length > 0 && (
          <div className="mx-1.5 mt-1 rounded-md bg-hairline/60 px-2 py-1 font-mono text-[9px] text-faint">
            + {sweepMembers.length} {sweepMode === "pvt" ? "corner" : "sample"} dataset
            {sweepMembers.length === 1 ? "" : "s"} · managed by the sweep rail
          </div>
        )}
      </div>
      <div className="flex shrink-0 gap-2 border-t border-hairline p-2.5">
        <Button onClick={openImport} className="flex-1">
          Open .raw
        </Button>
        <Button onClick={openImport} className="flex-1">
          Browse…
        </Button>
      </div>
    </aside>
  );
}

function DatasetNode({ ds }: { ds: WaveDatasetMeta }) {
  const activeId = useWaveviewStore((s) => s.activeId);
  const overlayId = useWaveviewStore((s) => s.overlayId);
  const expanded = useWaveviewStore((s) => s.expanded[ds.dataset_id] ?? false);
  const toggleExpanded = useWaveviewStore((s) => s.toggleExpanded);
  const setActive = useWaveviewStore((s) => s.setActive);
  const setOverlay = useWaveviewStore((s) => s.setOverlay);
  const closeDataset = useWaveviewStore((s) => s.closeDataset);

  const isActive = activeId === ds.dataset_id;
  const isOverlay = overlayId === ds.dataset_id;
  const name = ds.path.split("/").filter(Boolean).pop() ?? ds.path;

  return (
    <div className="mb-1">
      <div
        className={cn(
          "group mx-1.5 flex items-center gap-1.5 rounded-md px-2 py-1",
          isActive ? "bg-primary-soft" : "hover:bg-hairline",
        )}
      >
        <button
          type="button"
          onClick={() => toggleExpanded(ds.dataset_id)}
          aria-label={expanded ? "Collapse dataset" : "Expand dataset"}
          className="shrink-0 text-faint hover:text-fg"
        >
          {expanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
        </button>
        <button
          type="button"
          onClick={() => setActive(ds.dataset_id)}
          className="min-w-0 flex-1 text-left"
          title={ds.path}
        >
          <span
            className={cn(
              "block truncate font-mono text-[11px] font-semibold",
              isActive ? "text-primary" : "text-fg",
            )}
          >
            ▣ {name}
          </span>
          <span className="block truncate font-mono text-[9.5px] text-faint">
            {datasetShortName(ds)}
            {ds.warnings.length > 0 && (
              <span className="text-tertiary"> · {ds.warnings.length} warn</span>
            )}
          </span>
        </button>
        <Badge variant={ds.engine === "spectre" ? "cyan" : "indigo"}>{ds.engine}</Badge>
        {!isActive && (
          <button
            type="button"
            onClick={() => setOverlay(isOverlay ? null : ds.dataset_id)}
            title={isOverlay ? "Remove overlay" : "Overlay on the active plot"}
            className={cn(
              "shrink-0 font-mono text-[10px]",
              isOverlay ? "text-secondary" : "text-faint opacity-0 group-hover:opacity-100",
            )}
          >
            ⧉
          </button>
        )}
        <button
          type="button"
          onClick={() => void closeDataset(ds.dataset_id)}
          aria-label="Close dataset"
          className="shrink-0 text-faint opacity-0 hover:text-danger group-hover:opacity-100"
        >
          <X className="h-3 w-3" />
        </button>
      </div>
      {expanded &&
        orderedAnalyses(ds).map((a) => (
          <AnalysisRow key={a.analysis} ds={ds} a={a} />
        ))}
    </div>
  );
}

function AnalysisRow({ ds, a }: { ds: WaveDatasetMeta; a: WaveAnalysisMeta }) {
  const activeId = useWaveviewStore((s) => s.activeId);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const setActive = useWaveviewStore((s) => s.setActive);
  const catalog = useWaveviewStore((s) => s.catalog);

  const isActive = activeId === ds.dataset_id && activeAnalysis === a.analysis;
  // Metric hint: preferred measures whose registry default analysis is this one
  // (base key — a merged dataset's "ac#2" still hints the AC measures).
  const metricNames = PREFERRED_MEASURES.filter(
    (p) => catalog?.measurements[p.meas]?.default_analysis === baseAnalysis(a.analysis),
  ).map((p) => p.meas);

  return (
    <div className="ml-6 mr-1.5">
      <button
        type="button"
        onClick={() => setActive(ds.dataset_id, a.analysis)}
        className={cn(
          "flex w-full items-center justify-between gap-2 rounded-md px-2 py-[3px] text-left",
          isActive ? "bg-primary-soft text-primary" : "text-fg hover:bg-hairline",
        )}
      >
        <span className="text-[11.5px] font-medium">{analysisLabel(a.analysis)}</span>
        <span className="font-mono text-[9.5px] text-faint">
          {a.native_name} · {a.n_points}p
        </span>
      </button>
      {isActive && (
        <div className="mb-1 mt-0.5 space-y-px pl-2">
          <div className="truncate font-mono text-[9.5px] text-faint">
            {a.sweep ?? "no sweep"} · {a.n_points} pts · {a.signals.length} sig
          </div>
          {a.analysis !== "op" && <SignalChecks ds={ds} a={a} />}
          {metricNames.length > 0 && (
            <div className="flex items-baseline gap-1.5 pt-0.5">
              <span className="font-mono text-[10px] font-bold text-tertiary">ƒ</span>
              <span className="truncate font-mono text-[9.5px] text-muted">
                {metricNames.join(" · ")}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SignalChecks({ ds, a }: { ds: WaveDatasetMeta; a: WaveAnalysisMeta }) {
  const selected = useWaveviewStore(
    (s) => s.selected[`${ds.dataset_id}::${a.analysis}`],
  );
  const wave = useWaveviewStore((s) => s.wave);
  const toggleSignal = useWaveviewStore((s) => s.toggleSignal);

  // Saved selection, else what's actually plotted right now (the store default).
  const on = new Set(selected ?? wave?.signals.map((s) => s.name) ?? []);
  const names = plottableSignals(a);
  const unitFor = (n: string) => a.signals.find((s) => s.name === n)?.units ?? "";
  // Swatch color = the SAME role-based assignment the figure layer applies to
  // the plotted wave (a file-order swatch lies whenever the two differ).
  const plottedColors = Object.fromEntries(
    signalRoles(wave?.signals.map((s) => s.name) ?? []).map((r) => [r.name, r.color]),
  );

  return (
    <div className="space-y-px">
      {names.map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => toggleSignal(ds.dataset_id, a.analysis, n)}
          className="flex w-full items-center gap-2 rounded-sm px-1 py-[2px] text-left hover:bg-hairline"
        >
          <span
            className={cn(
              "flex h-3 w-3 shrink-0 items-center justify-center rounded-[3px] text-[8px]",
              on.has(n) ? "bg-primary text-white" : "border border-[#d4d4d8] bg-panel",
            )}
            aria-hidden
          >
            {on.has(n) && "✓"}
          </span>
          <span
            className="h-[3px] w-3 shrink-0 rounded-full"
            style={{ background: plottedColors[n] ?? "#e4e4e7" }}
            aria-hidden
          />
          <span className="min-w-0 flex-1 truncate font-mono text-[10px] text-fg">{n}</span>
          <span className="shrink-0 font-mono text-[9px] text-faint">{unitFor(n)}</span>
        </button>
      ))}
    </div>
  );
}
