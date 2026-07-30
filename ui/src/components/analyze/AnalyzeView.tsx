"use client";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Segmented } from "@/components/ui/segmented";
import { WaveformChart } from "@/components/charts/WaveformChart";
import { UI } from "@/config";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useProjectStore } from "@/stores/projectStore";
import { useWaveviewStore } from "@/stores/waveviewStore";
import {
  ANALYSIS_TITLES,
  SWEEP_OPTIONS,
} from "@/lib/waveview/config";
import {
  analysisLabel,
  baseAnalysis,
  datasetShortName,
  derivedMarksFor,
  orderedAnalyses,
  perfChips,
  plotStyleFor,
  unitsForSignal,
} from "@/lib/waveview/selectors";
import {
  buildHistogramFigure,
  buildMcFigure,
  buildPvtFigure,
  buildWaveFigure,
  type CornerCurve,
  type WaveFigureOpts,
} from "@/lib/waveview/figure";
import {
  cornerResults,
  headlineFor,
  mcStats,
  meanSdCurves,
  pvtStats,
  specForMeas,
  tbMatchFromPath,
  type SweepMode,
} from "@/lib/waveview/sweep";
import { DatasetTree } from "./DatasetTree";
import { AxesRail } from "./AxesRail";
import { MetaStrip, LogBar, AnalyzeStatusBar } from "./AnalyzeChrome";
import { OpTable } from "./OpTable";
import { OpenImportModal } from "./OpenImportModal";
import { PerformanceStrip } from "./PerformanceStrip";

/**
 * Analyze — the waveform viewer (fullBleed: like Library, this view owns its
 * rails, bottom log, and status bar). Layout follows the design handoff's
 * golden ref: dataset/trace tree · center column (meta strip → analysis tabs →
 * plot header with the sweep-mode segmented → viewport-filling plot →
 * MC histogram strip → performance strip) · axes rail. Backend-driven via
 * /api/waveview/*; PVT/MC read real per-corner datasets from the active run.
 */
export function AnalyzeView() {
  const status = useWaveviewStore((s) => s.status);
  const error = useWaveviewStore((s) => s.error);
  const init = useWaveviewStore((s) => s.init);

  useEffect(() => {
    void init();
  }, [init]);

  return (
    <div className="flex h-full min-h-0 flex-col">
      {status === "error" ? (
        <div className="flex min-h-0 flex-1 items-center justify-center bg-bg p-8">
          <div className="max-w-[420px] text-center">
            <div className="text-[14px] font-semibold tracking-[-0.01em]">
              Waveform viewer unavailable
            </div>
            <div className="mt-2 text-[12px] text-muted">{error}</div>
            <Button variant="primary" className="mt-3" onClick={() => void init()}>
              Retry
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1">
          <DatasetTree />
          <CenterColumn />
          <RailSlot />
        </div>
      )}
      <LogBar />
      <AnalyzeStatusBar />
      <OpenImportModal />
    </div>
  );
}

function RailSlot() {
  const railOpen = useWaveviewStore((s) => s.railOpen);
  const activeId = useWaveviewStore((s) => s.activeId);
  if (!railOpen || !activeId) return null;
  return <AxesRail />;
}

function CenterColumn() {
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeId = useWaveviewStore((s) => s.activeId);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const openImport = useWaveviewStore((s) => s.openImport);

  const ds = datasets.find((d) => d.dataset_id === activeId);

  if (!ds) {
    return (
      <main className="flex min-h-0 min-w-0 flex-1 flex-col bg-bg">
        <EmptyState minHeight="min-h-0" className="flex-1">
          <div className="text-center">
            <div className="text-[13px] font-medium text-muted">{UI.analyze.emptyState.title}</div>
            <div className="mt-1 font-mono text-[10px] text-faint">
              {UI.analyze.emptyState.hint}
            </div>
            <Button variant="primary" className="mt-3" onClick={openImport}>
              {UI.analyze.emptyState.action}
            </Button>
          </div>
        </EmptyState>
      </main>
    );
  }

  const isOp = activeAnalysis ? baseAnalysis(activeAnalysis) === "op" : false;

  return (
    <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-bg">
      <MetaStrip />
      <AnalysisTabs />
      <div className="flex min-h-0 flex-1 flex-col px-3.5 pt-2.5">
        <PlotHeader />
        <PlotArea />
        {!isOp && <HistogramStrip />}
        <div className="max-h-[45%] shrink-0 overflow-y-auto pt-3">
          <PerformanceStrip />
        </div>
      </div>
    </main>
  );
}

/** Browser-style analysis tabs — the handoff's tab strip (active tab connects
 *  to the plot region through the divider). */
function AnalysisTabs() {
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeId = useWaveviewStore((s) => s.activeId);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const setAnalysis = useWaveviewStore((s) => s.setAnalysis);
  const railOpen = useWaveviewStore((s) => s.railOpen);
  const toggleRail = useWaveviewStore((s) => s.toggleRail);

  const ds = datasets.find((d) => d.dataset_id === activeId);
  if (!ds) return null;

  const analyses = orderedAnalyses(ds);
  // When a merged run carries several analyses of the same kind (loopgain,
  // CMRR and PSRR are all "ac"), label the tabs by their TESTBENCH instead of
  // an opaque "#2"/"#3" ordinal — the tb name rides in the member's native_name.
  const baseCounts = new Map<string, number>();
  for (const a of analyses) {
    const b = baseAnalysis(a.analysis);
    baseCounts.set(b, (baseCounts.get(b) ?? 0) + 1);
  }
  const tabLabel = (a: (typeof analyses)[number]) => {
    if ((baseCounts.get(baseAnalysis(a.analysis)) ?? 0) < 2) {
      return analysisLabel(a.analysis);
    }
    const tb = tbMatchFromPath(a.native_name ?? "");
    if (!tb) return analysisLabel(a.analysis);
    const short = tb.replace(/^tb[-_]/, "");
    return `${analysisLabel(baseAnalysis(a.analysis))} · ${short}`;
  };
  // A merged sweep run carries one analysis PER CORNER/SAMPLE of the same
  // testbench — identical labels (e.g. 8 × "Tran · thd") collapse to the first;
  // the sweep rail owns the per-member view.
  const seenLabels = new Set<string>();
  const tabAnalyses = analyses.filter((a) => {
    const label = tabLabel(a);
    if (seenLabels.has(label)) return false;
    seenLabels.add(label);
    return true;
  });

  return (
    <div className="flex shrink-0 items-end gap-0.5 overflow-x-auto border-b border-border bg-panel px-3.5 pt-2">
      {tabAnalyses.map((a) => {
        const active = a.analysis === activeAnalysis;
        return (
          <button
            key={a.analysis}
            type="button"
            onClick={() => setAnalysis(a.analysis)}
            className={cn(
              "relative top-px whitespace-nowrap rounded-t-[7px] border border-b-0 px-3 py-1.5 text-[11.5px] transition",
              active
                ? "border-border bg-bg font-semibold text-primary"
                : "border-hairline bg-hairline font-normal text-muted hover:text-fg",
            )}
          >
            {tabLabel(a)}
          </button>
        );
      })}
      <div className="min-w-2 flex-1" />
      {!railOpen && (
        <button
          type="button"
          onClick={toggleRail}
          className="mb-1.5 shrink-0 rounded-md border border-border bg-panel px-2.5 py-1 text-[11px] text-muted hover:bg-hairline"
          title="Show the axes panel"
        >
          ⟨ axes · units
        </button>
      )}
    </div>
  );
}

/** Per-mode verdict for the plot-header badge. Judgements come only from
 *  project specs (single: Tier-1 chips; pvt/mc: the headline metric's spec). */
function useVerdict(): { text: string; variant: "pass" | "warn" | "fail" | "neutral" } | null {
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepMetrics = useWaveviewStore((s) => s.sweepMetrics);
  const cornerEnabled = useWaveviewStore((s) => s.cornerEnabled);
  const catalog = useWaveviewStore((s) => s.catalog);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const measures = useWaveviewStore((s) => s.measures);
  const summary = useProjectStore((s) => s.summary);
  const specs = summary?.target_specs ?? null;

  const base = activeAnalysis ? baseAnalysis(activeAnalysis) : "";
  const headline = headlineFor(base, catalog);
  const spec = headline ? specForMeas(specs, headline.meas) : null;

  if (sweepMode === "single") {
    const chips = perfChips(catalog, measures, specs);
    const judged = chips.filter((c) => c.target != null && c.value != null);
    if (!judged.length) return null;
    const failing = judged.filter((c) => c.status === "fail").length;
    return failing === 0
      ? { text: "PASS · all Tier-1", variant: "pass" }
      : { text: `marginal · ${failing}/${judged.length} failing`, variant: "warn" };
  }
  if (sweepStatus !== "ready") {
    return {
      text: sweepMode === "pvt" ? "no corners" : "no samples",
      variant: "neutral",
    };
  }
  if (sweepMode === "pvt") {
    const corners = cornerResults(sweepMembers, sweepMetrics, cornerEnabled);
    const stats = pvtStats(corners, headline, spec);
    if (!stats.total) return { text: "no corners", variant: "neutral" };
    if (stats.pass == null) return { text: `${stats.total} corners`, variant: "neutral" };
    if (stats.pass === stats.total)
      return { text: `PASS · ${stats.total} corners`, variant: "pass" };
    const worst = corners.find((c) => c.key === stats.worstKey);
    return { text: `FAIL @ ${worst?.name.split("·")[0] ?? "corner"}`, variant: "fail" };
  }
  const values = sweepMembers
    .map((m) => sweepMetrics[m.key])
    .filter((v): v is number => v != null);
  const stats = mcStats(values, headline, spec);
  if (!stats) return { text: "no samples", variant: "neutral" };
  if (stats.yield == null) return { text: `${stats.n} samples`, variant: "neutral" };
  const y = stats.yield * 100;
  return {
    text: `yield ${y.toFixed(1)}%`,
    variant: y >= 99 ? "pass" : y >= 95 ? "warn" : "fail",
  };
}

/**
 * Save the mounted main plot as a PNG into the active dataset's run
 * (snapshots/<analysis>.png) — the persistent-thumbnail path other surfaces
 * (Library datasheet cards) read via …/artifacts/file. Hidden when the active
 * dataset doesn't belong to a run (uploads, pathed opens have no run identity).
 */
function SnapshotButton({ dsPath, analysis }: { dsPath: string; analysis: string }) {
  const runs = useWaveviewStore((s) => s.runs);
  const loadRuns = useWaveviewStore((s) => s.loadRuns);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  useEffect(() => {
    if (!runs.length) void loadRuns();
  }, [runs.length, loadRuns]);

  const run = runs.find((r) => dsPath === r.run_dir || dsPath.startsWith(`${r.run_dir}/`));
  if (!run) return null;

  const snap = async () => {
    const gd = document.querySelector<HTMLElement>("#analyze-main-plot .js-plotly-plot");
    if (!gd) return;
    setBusy(true);
    try {
      // same module instance PlotlyChart already loaded — a shared chunk, not a refetch
      const Plotly = (await import("plotly.js-dist-min")).default;
      const url = await Plotly.toImage(gd, {
        format: "png",
        width: 1200,
        height: 675,
        scale: 2,
      });
      const res = await api.waveviewSaveSnapshot(run.run_id, {
        png_base64: url.split(",", 2)[1],
        name: analysis,
      });
      setNote(`saved ${res.rel}`);
    } catch {
      setNote("snapshot failed");
    }
    setBusy(false);
    window.setTimeout(() => setNote(null), 4000);
  };

  return (
    <>
      {note && <span className="font-mono text-[9.5px] text-muted">{note}</span>}
      <button
        type="button"
        disabled={busy}
        onClick={() => void snap()}
        title="Save this plot as a PNG snapshot into the run (snapshots/) — thumbnails for other views"
        className="rounded-sm border border-hairline px-1.5 py-px font-mono text-[9.5px] text-muted hover:border-border hover:text-fg"
      >
        {busy ? "saving…" : "📷 snapshot"}
      </button>
    </>
  );
}

function PlotHeader() {
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const setSweepMode = useWaveviewStore((s) => s.setSweepMode);
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeId = useWaveviewStore((s) => s.activeId);
  const verdict = useVerdict();

  const ds = datasets.find((d) => d.dataset_id === activeId);
  if (!ds || !activeAnalysis) return null;

  const base = baseAnalysis(activeAnalysis);
  const [title, sub] = ANALYSIS_TITLES[base] ?? [analysisLabel(activeAnalysis), ""];

  return (
    <div className="mb-1.5 flex shrink-0 items-center gap-2">
      <span className="text-[13px] font-semibold tracking-[-0.01em] text-fg">{title}</span>
      <span className="truncate font-mono text-[10px] text-faint">
        {sub && `${sub} · `}
        {datasetShortName(ds)}
      </span>
      <div className="flex-1" />
      {base !== "op" && <SnapshotButton dsPath={ds.path} analysis={activeAnalysis} />}
      <Segmented
        value={sweepMode}
        onChange={(v) => setSweepMode(v as SweepMode)}
        options={SWEEP_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
        className="text-[11px]"
      />
      {verdict && (
        <Badge variant={verdict.variant === "neutral" ? "neutral" : verdict.variant} dot>
          {verdict.text}
        </Badge>
      )}
    </div>
  );
}

/** Assemble the figure for the active mode from store state (pure builders). */
function useActiveFigure() {
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeId = useWaveviewStore((s) => s.activeId);
  const wave = useWaveviewStore((s) => s.wave);
  const wavePhase = useWaveviewStore((s) => s.wavePhase);
  const overlayWave = useWaveviewStore((s) => s.overlayWave);
  const overlayId = useWaveviewStore((s) => s.overlayId);
  const xScale = useWaveviewStore((s) => s.xScale);
  const measures = useWaveviewStore((s) => s.measures);
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepWaves = useWaveviewStore((s) => s.sweepWaves);
  const sweepMetrics = useWaveviewStore((s) => s.sweepMetrics);
  const sweepUgfs = useWaveviewStore((s) => s.sweepUgfs);
  const cornerEnabled = useWaveviewStore((s) => s.cornerEnabled);
  const mcSigma = useWaveviewStore((s) => s.mcSigma);
  const catalog = useWaveviewStore((s) => s.catalog);
  const summary = useProjectStore((s) => s.summary);

  return useMemo(() => {
    if (!activeAnalysis || !wave) return null;
    const base = baseAnalysis(activeAnalysis);
    const style = plotStyleFor(activeAnalysis);
    const ds = datasets.find((d) => d.dataset_id === activeId);
    const meta = ds?.analyses.find((a) => a.analysis === activeAnalysis);
    const primaryName = wave.signals[0]?.name;
    const opts: WaveFigureOpts = {
      analysis: base,
      xLog: (xScale ?? style.xScale) === "log",
      dual: !!style.dual,
      bar: !!style.bar,
      yLog: style.yScale === "log",
      xName: wave.x_name ?? null,
      yUnits: unitsForSignal(meta, primaryName),
    };
    const marks = derivedMarksFor(activeAnalysis, measures);
    const overlayDs = datasets.find((d) => d.dataset_id === overlayId);

    if (sweepMode === "pvt" && sweepStatus === "ready") {
      const results = cornerResults(sweepMembers, sweepMetrics, cornerEnabled);
      const headline = headlineFor(base, catalog);
      const spec = headline ? specForMeas(summary?.target_specs ?? null, headline.meas) : null;
      const stats = pvtStats(results, headline, spec);
      const curves: CornerCurve[] = results
        .filter((c) => c.enabled && sweepWaves[c.key])
        .map((c) => ({
          key: c.key,
          name: c.name,
          color: c.color,
          nominal: c.nominal,
          worst: c.key === stats.worstKey && !c.nominal,
          x: sweepWaves[c.key].x,
          y: sweepWaves[c.key].y,
          phase: sweepWaves[c.key].phase,
        }));
      if (curves.length) {
        // The worst corner's UGF/PM (real per-corner measures) annotate the plot,
        // matching the handoff's "UGF … · PM …" mark on the PVT Bode.
        const marks =
          opts.dual && stats.worstKey && headline?.meas.startsWith("pm")
            ? {
                ugf: sweepUgfs[stats.worstKey] ?? null,
                pm: sweepMetrics[stats.worstKey] ?? null,
              }
            : {};
        return buildPvtFigure(curves, marks, opts);
      }
    }
    if (sweepMode === "mc" && sweepStatus === "ready") {
      const enabledWaves = sweepMembers.map((m) => sweepWaves[m.key]).filter(Boolean);
      const curves = meanSdCurves(enabledWaves.map((w) => w.y));
      if (curves && enabledWaves.length) {
        return buildMcFigure(
          {
            x: enabledWaves[0].x,
            samples: enabledWaves.map((w) => w.y),
            mean: curves.mean,
            sd: curves.sd,
          },
          mcSigma,
          {},
          opts,
        );
      }
    }
    return buildWaveFigure(
      wave,
      wavePhase,
      overlayWave,
      overlayDs ? datasetShortName(overlayDs) : undefined,
      marks,
      opts,
    );
  }, [
    activeAnalysis,
    wave,
    wavePhase,
    overlayWave,
    overlayId,
    datasets,
    activeId,
    xScale,
    measures,
    sweepMode,
    sweepStatus,
    sweepMembers,
    sweepWaves,
    sweepMetrics,
    sweepUgfs,
    cornerEnabled,
    mcSigma,
    catalog,
    summary,
  ]);
}

function PlotArea() {
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const waveStatus = useWaveviewStore((s) => s.waveStatus);
  const waveError = useWaveviewStore((s) => s.waveError);
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepError = useWaveviewStore((s) => s.sweepError);
  const wave = useWaveviewStore((s) => s.wave);
  const figure = useActiveFigure();

  const isOp = activeAnalysis ? baseAnalysis(activeAnalysis) === "op" : false;
  // A point analysis (ngspice's integrated-noise plot: 1 pt × N per-device
  // contributions) can't line-plot — show its values as a scalar table instead.
  const isPointData =
    !isOp && !!wave && wave.signals.length > 0 && wave.signals.every((s) => s.x.length <= 1);

  return (
    <div
      id="analyze-main-plot"
      className="relative min-h-[190px] flex-1 overflow-hidden rounded-[9px] border border-border bg-panel"
    >
      {isOp ? (
        <div className="h-full overflow-y-auto">
          <OpTable />
        </div>
      ) : isPointData ? (
        <PointValueTable />
      ) : waveStatus === "error" ? (
        <EmptyState minHeight="min-h-full" bordered={false}>
          <span className="text-danger">{waveError}</span>
        </EmptyState>
      ) : figure ? (
        <>
          <WaveformChart figure={figure} fill />
          {sweepMode !== "single" && sweepStatus !== "ready" && (
            <div className="absolute bottom-10 left-14 rounded-md border border-border bg-panel/90 px-2.5 py-1.5 font-mono text-[10px] text-muted">
              {sweepStatus === "loading"
                ? `discovering ${sweepMode === "pvt" ? "corner" : "sample"} datasets…`
                : sweepStatus === "error"
                  ? (sweepError ?? "sweep discovery failed")
                  : sweepMode === "pvt"
                    ? "no per-corner artifacts in this run — showing the single result"
                    : "no Monte Carlo samples in this run — showing the single result"}
            </div>
          )}
        </>
      ) : waveStatus === "loading" ? (
        <EmptyState minHeight="min-h-full" bordered={false}>
          <span className="font-mono text-[11px] text-faint">rendering waveform…</span>
        </EmptyState>
      ) : (
        <EmptyState minHeight="min-h-full" bordered={false}>
          No signals selected — tick traces in the dataset tree.
        </EmptyState>
      )}
    </div>
  );
}

/** Point-analysis values (e.g. integrated noise totals) as a scalar table —
 *  the OP-table treatment for any 1-point analysis the tree has ticked. */
function PointValueTable() {
  const wave = useWaveviewStore((s) => s.wave);
  const datasets = useWaveviewStore((s) => s.datasets);
  const activeId = useWaveviewStore((s) => s.activeId);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);

  const ds = datasets.find((d) => d.dataset_id === activeId);
  const meta = ds?.analyses.find((a) => a.analysis === activeAnalysis);

  const rows = (wave?.signals ?? []).map((s) => ({
    name: s.name,
    value: Array.isArray(s.y) && s.y.length ? (s.y[0] as number) : null,
    units: unitsForSignal(meta, s.name) ?? "",
  }));

  return (
    <div className="h-full overflow-y-auto p-0.5">
      <table className="w-full border-collapse font-mono text-[11px]">
        <thead>
          <tr className="text-left font-sans text-[10px] uppercase tracking-[0.06em] text-faint">
            <th className="border-b border-border px-3 py-2 font-bold">Signal</th>
            <th className="border-b border-border px-3 py-2 text-right font-bold">Value</th>
            <th className="border-b border-border px-3 py-2 font-bold">Units</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.name} className="hover:bg-bg">
              <td className="border-b border-hairline px-3 py-1.5 font-medium text-fg">
                {r.name}
              </td>
              <td className="border-b border-hairline px-3 py-1.5 text-right text-[#3f3f46]">
                {r.value != null ? r.value.toExponential(3) : "—"}
              </td>
              <td className="border-b border-hairline px-3 py-1.5 text-faint">{r.units}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="px-3 py-2 font-mono text-[9px] text-faint">
        point analysis · {rows.length} of {meta?.signals.length ?? rows.length} values shown —
        tick more traces in the tree
      </div>
    </div>
  );
}

/** MC metric histogram — the handoff's distribution strip under the plot. */
function HistogramStrip() {
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepMetrics = useWaveviewStore((s) => s.sweepMetrics);
  const catalog = useWaveviewStore((s) => s.catalog);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const summary = useProjectStore((s) => s.summary);

  const base = activeAnalysis ? baseAnalysis(activeAnalysis) : "";
  const headline = headlineFor(base, catalog);
  const values = sweepMembers
    .map((m) => sweepMetrics[m.key])
    .filter((v): v is number => v != null);

  if (sweepMode !== "mc" || sweepStatus !== "ready" || !headline || values.length < 2) {
    return null;
  }
  // No memo: ≤32 samples over 26 bins is trivial to rebin per render.
  const spec = specForMeas(summary?.target_specs ?? null, headline.meas);
  const goalSpec =
    spec == null
      ? null
      : { value: spec.target, cmp: (spec.goal === "minimize" ? "le" : "ge") as "le" | "ge" };
  const figure = buildHistogramFigure(values, goalSpec, headline.label, headline.unit);

  return (
    <div className="shrink-0">
      <div className="flex items-center gap-2 py-1">
        <span className="text-[11px] font-semibold text-fg">
          {headline.label} · {values.length} samples
        </span>
        <span className="font-mono text-[9px] text-faint">per-sample POST /measure</span>
      </div>
      <div className="h-[118px] overflow-hidden rounded-[9px] border border-border bg-panel">
        <WaveformChart figure={figure} fill />
      </div>
    </div>
  );
}
