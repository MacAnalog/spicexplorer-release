"use client";
import { useEffect, useMemo, useState } from "react";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { api } from "@/lib/api";
import { launchLiveRun } from "@/lib/launchRun";
import { COLORS } from "@/components/charts/PlotlyChart";
import { ScoreConvergenceChart } from "@/components/charts/ScoreConvergenceChart";
import { MetricConvergenceChart } from "@/components/charts/MetricConvergenceChart";
import { Panel, PanelBody, PanelHeader } from "@/components/ui/panel";
import { Button } from "@/components/ui/button";
import { Stat } from "@/components/ui/stat";
import { Toolbar, ToolbarLabel, ToolbarSpacer } from "@/components/shell/Toolbar";
import { Separator } from "@/components/ui/separator";
import { selectCn } from "@/components/ui/select";
import { EmptyState } from "@/components/ui/empty-state";
import { CornerSelect } from "@/components/pvt/CornerSelect";
import { formatEng, formatDuration, statusForGoal } from "@/lib/utils";
import type { AppConfig } from "@/types/api";

interface Props {
  appConfig: AppConfig | null;
}

/**
 * Optimize view — run configuration + convergence charts. Phase 2 moved the
 * live spec status, best params, and run progress to the always-on RightRail,
 * and the per-iteration log to the BottomPanel. The SSE stream is owned by
 * runStore (see startRun), so a run keeps streaming if the user navigates away.
 *
 * Live runs need the IHP PDK; when it's absent (env.live_runs_enabled === false)
 * the Start button is disabled and the user is steered to Replay.
 */
export function OptimizeTab({ appConfig }: Props) {
  const { summary, isApplied } = useProjectStore();
  const { isReplay, isRunning, events, startRun, stopRun, runError } = useRunStore();
  const bestMetrics = useRunStore((s) => s.bestMetrics);
  const currentIter = useRunStore((s) => s.currentIter);
  const budget = useRunStore((s) => s.budget);
  const runStartTs = useRunStore((s) => s.runStartTs);
  const storedElapsedMs = useRunStore((s) => s.elapsedMs);
  const env = useUIStore((s) => s.env);
  const runConfig = useUIStore((s) => s.runConfig);
  const setRunConfig = useUIStore((s) => s.setRunConfig);

  const [replayCheckpoint, setReplayCheckpoint] = useState<string>("");
  const [selectedMetric, setSelectedMetric] = useState<string>("");
  const [startError, setStartError] = useState<string | null>(null);
  // Tick every second while running so the Elapsed / Est. remaining KPIs advance.
  const [nowTick, setNowTick] = useState<number>(() => Date.now());
  useEffect(() => {
    if (!isRunning) return;
    setNowTick(Date.now());
    const t = setInterval(() => setNowTick(Date.now()), 1000);
    return () => clearInterval(t);
  }, [isRunning]);

  const enabledSpecs = useMemo(
    () => summary?.target_specs.filter((s) => s.enable) ?? [],
    [summary],
  );

  useEffect(() => {
    if (enabledSpecs.length > 0 && !selectedMetric) {
      setSelectedMetric(enabledSpecs[0].name);
    }
  }, [enabledSpecs, selectedMetric]);

  // Live runs require the PDK; without it disable Start and steer to Replay.
  const liveDisabled = env != null && !env.live_runs_enabled;
  const canStart = (isApplied && !liveDisabled) || !!replayCheckpoint;

  const handleStart = async () => {
    setStartError(null);
    // Replay is Optimize-specific (preset checkpoint dropdown); live runs go
    // through the shared launcher so algorithm/budget/seed overrides are sent.
    if (replayCheckpoint) {
      try {
        const res = await api.startRun({ replay: true, checkpoint_id: replayCheckpoint });
        const ckptLabel = appConfig?.preset_checkpoints.find((c) => c.id === replayCheckpoint)?.label;
        // Use the checkpoint length as the progress denominator, not the live budget.
        startRun(res.run_id, res.replay, res.n_iters ?? runConfig.budget, {
          kind: "replay",
          label: `Replay · ${ckptLabel ?? replayCheckpoint}`,
          checkpointId: replayCheckpoint,
        });
      } catch (err) {
        setStartError(err instanceof Error ? err.message : "Failed to start run");
      }
      return;
    }
    const res = await launchLiveRun();
    if (!res.ok) setStartError(res.error ?? "Failed to start run");
  };

  const scoreRuns = useMemo(
    () => [
      {
        label: isReplay ? "Replay" : "Live",
        scores: events.map((e) => e.score ?? null),
        best_scores: events.map((e) => e.best_score ?? null),
        color: COLORS.primary,
      },
    ],
    [events, isReplay],
  );

  // KPI row values. Best-score mirrors the RightRail (running max over best_score).
  const kpis = useMemo(() => {
    const best = events.reduce((m, e) => {
      const v = e.best_score ?? e.score;
      return v != null && Number.isFinite(v) && v > m ? v : m;
    }, -Infinity);
    const passing = enabledSpecs.filter(
      (s) => statusForGoal(s.goal, bestMetrics[s.name], s.target, s.tolerance ?? undefined) === "pass",
    ).length;
    return {
      bestScore: Number.isFinite(best) ? best : null,
      passing,
      total: enabledSpecs.length,
    };
  }, [events, enabledSpecs, bestMetrics]);

  const elapsedMs = isRunning && runStartTs ? Math.max(0, nowTick - runStartTs) : storedElapsedMs;
  const estRemainingMs =
    isRunning && currentIter > 0 && budget > currentIter
      ? (elapsedMs / currentIter) * (budget - currentIter)
      : null;
  const hasRun = events.length > 0 || isRunning;

  const selectedSpec = enabledSpecs.find((s) => s.name === selectedMetric);
  const metricRuns = useMemo(
    () =>
      selectedMetric
        ? [
            {
              label: isReplay ? "Replay" : "Live",
              values: events.map((e) => e.metrics?.[selectedMetric] ?? null),
              color: COLORS.primary,
            },
          ]
        : [],
    [events, isReplay, selectedMetric],
  );

  return (
    <>
      <Toolbar>
        <ToolbarLabel>budget</ToolbarLabel>
        <input
          aria-label="Run budget (iterations)"
          type="number"
          min={10}
          max={5000}
          value={runConfig.budget}
          onChange={(e) => setRunConfig({ budget: Number(e.target.value) })}
          disabled={isRunning}
          className={selectCn("sm") + " w-[72px]"}
        />

        {summary?.pvt && summary.pvt.corners.length > 0 && (
          <>
            <ToolbarLabel>corner</ToolbarLabel>
            <div className="w-[210px]">
              <CornerSelect
                corners={summary.pvt.corners}
                value={runConfig.activeCorner}
                defaultCorner={summary.pvt.active_corner}
                onChange={(name) => setRunConfig({ activeCorner: name })}
                disabled={isRunning}
                aria-label="PVT corner to optimize against"
              />
            </div>
          </>
        )}

        <Separator />

        <ToolbarLabel>demo replay</ToolbarLabel>
        <select
          aria-label="Replay checkpoint"
          value={replayCheckpoint}
          onChange={(e) => setReplayCheckpoint(e.target.value)}
          disabled={isRunning}
          className={selectCn("sm") + " w-[200px]"}
        >
          <option value="">— live —</option>
          {appConfig?.preset_checkpoints.map((ck) => (
            <option key={ck.id} value={ck.id}>
              {ck.label}
            </option>
          ))}
        </select>

        <ToolbarSpacer />

        {isRunning ? (
          <Button variant="danger" onClick={stopRun}>
            <span className="h-1.5 w-1.5 rounded-full bg-white obs-pulse" /> Stop
          </Button>
        ) : (
          <Button
            variant="primary"
            onClick={handleStart}
            disabled={!canStart}
            title={
              liveDisabled && !replayCheckpoint
                ? "Live optimization needs the IHP sg13g2 PDK, which isn't installed on this machine. Use Replay to drive the demo from cached runs."
                : undefined
            }
          >
            {replayCheckpoint ? "Replay" : "Start"}
          </Button>
        )}
      </Toolbar>

      {liveDisabled && (
        <div className="border-b border-warn-soft bg-warn-soft px-4 py-1.5 text-[11px] text-[#b45309]">
          PDK missing — live runs are disabled. Replay a cached checkpoint to drive the demo.
        </div>
      )}

      {/* *:shrink-0 — children are Panels (overflow-hidden ⇒ flex auto-min-size 0),
          so without this the flex column crushes them to fit and clips their content
          (the Manual Sim result + log tails) instead of letting this container scroll. */}
      <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-auto p-3 *:shrink-0">
        {(startError || runError) && (
          <div
            role="alert"
            className="rounded-md border border-danger bg-danger-soft px-3 py-2 text-xs text-danger"
          >
            {startError ?? runError}
          </div>
        )}

        {!canStart && events.length === 0 && (
          <EmptyState bordered minHeight="min-h-32">
            Apply a project or select a preset checkpoint to enable a run.
          </EmptyState>
        )}

        {hasRun && (
          <div className="grid grid-cols-5 gap-2.5">
            <Stat eyebrow="best score" value={kpis.bestScore != null ? formatEng(kpis.bestScore) : "—"} />
            <Stat
              eyebrow="iterations"
              value={currentIter > 0 ? String(currentIter) : "—"}
              unit={budget > 0 ? `/ ${budget}` : undefined}
            />
            <Stat
              eyebrow="specs passing"
              value={`${kpis.passing}/${kpis.total}`}
              tone={kpis.total > 0 && kpis.passing === kpis.total ? "ok" : kpis.passing === 0 ? "danger" : "warn"}
            />
            <Stat eyebrow="elapsed" value={formatDuration(elapsedMs)} />
            <Stat eyebrow="est. remaining" value={estRemainingMs != null ? formatDuration(estRemainingMs) : "—"} />
          </div>
        )}

        <div className="grid grid-cols-2 gap-2.5">
          <Panel>
            <PanelHeader
              title="F(x) convergence"
              mute="· raw + best-so-far"
              right={
                <span className="font-mono text-[10px]">
                  <span style={{ color: COLORS.primary }}>● best</span>{" "}
                  <span style={{ color: COLORS.muted }}>● raw</span>
                </span>
              }
            />
            <PanelBody>
              {events.length > 0 ? (
                <ScoreConvergenceChart runs={scoreRuns} />
              ) : (
                <EmptyState minHeight="h-[240px]">No data yet.</EmptyState>
              )}
            </PanelBody>
          </Panel>

          <Panel>
            <PanelHeader
              title={
                <>
                  metric · <span className="font-mono">{selectedMetric || "—"}</span> best-so-far
                </>
              }
              right={
                <select
                  aria-label="Metric to chart"
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className={selectCn("xs")}
                >
                  {enabledSpecs.map((s) => (
                    <option key={s.name} value={s.name}>
                      {s.name}
                    </option>
                  ))}
                </select>
              }
            />
            <PanelBody>
              {events.length > 0 && selectedMetric ? (
                <MetricConvergenceChart
                  metric={selectedMetric}
                  runs={metricRuns}
                  target={selectedSpec?.target}
                  goal={selectedSpec?.goal}
                />
              ) : (
                <EmptyState minHeight="h-[240px]">No data yet.</EmptyState>
              )}
            </PanelBody>
          </Panel>
        </div>

      </div>
    </>
  );
}
