"use client";
import { useEffect, useMemo, useState } from "react";
import { Panel, PanelBody, PanelHeader } from "@/components/ui/panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useExplorerStore } from "@/stores/explorerStore";
import { useProjectStore } from "@/stores/projectStore";
import { useUIStore } from "@/stores/uiStore";
import { api } from "@/lib/api";
import { formatEng, goalSymbol, statusForGoal } from "@/lib/utils";
import { COLORS } from "@/components/charts/PlotlyChart";
import { ScoreConvergenceChart } from "@/components/charts/ScoreConvergenceChart";
import { MetricConvergenceChart } from "@/components/charts/MetricConvergenceChart";
import { MetricScatterChart } from "@/components/charts/MetricScatterChart";
import { MetricHistogramChart } from "@/components/charts/MetricHistogramChart";
import { ParallelCoordinatesChart } from "@/components/charts/ParallelCoordinatesChart";
import { Stat } from "@/components/ui/stat";
import { EmptyState } from "@/components/ui/empty-state";
import { selectCn } from "@/components/ui/select";
import { Thead, Th, Tr, Td } from "@/components/ui/table";
import type { CheckpointData, ScatterPoint, SimulateOnceResponse, TargetSpec } from "@/types/api";
import { Toolbar, ToolbarLabel, ToolbarSpacer } from "@/components/shell/Toolbar";
import { Separator } from "@/components/ui/separator";

function lastFinite(arr: (number | null)[] | undefined): number | null {
  if (!arr) return null;
  for (let i = arr.length - 1; i >= 0; i--) {
    const v = arr[i];
    if (v != null && Number.isFinite(v)) return v;
  }
  return null;
}

function bestOf(values: number[], goal: string, target?: number | string | null): number | null {
  if (!values.length) return null;
  // reduce, not Math.min(...values): spreading a long run's array as call
  // arguments overflows the stack (RangeError) above ~65k points.
  if (goal === "exact" && target != null && Number.isFinite(Number(target))) {
    // "Best" for an exact target is the sample CLOSEST to it — not the max, which an
    // outlier (e.g. 120° for a 60°±10° phase-margin spec) would otherwise win.
    const t = Number(target);
    return values.reduce((m, v) => (Math.abs(v - t) < Math.abs(m - t) ? v : m), values[0]);
  }
  return values.reduce((m, v) => (goal === "minimize" ? (v < m ? v : m) : v > m ? v : m), values[0]);
}

function passesSpec(s: TargetSpec, val: number | null): boolean | null {
  if (val == null) return null;
  return statusForGoal(s.goal, val, s.target, s.tolerance ?? undefined) === "pass";
}

export function ExplorerTab() {
  const { summary, yamlPath } = useProjectStore();
  const env = useUIStore((s) => s.env);
  const {
    availableCheckpoints,
    runA,
    runB,
    envelopeA,
    scatterMetricX,
    scatterMetricY,
    selectedMetric,
    setRunA,
    setRunB,
    setEnvelopeA,
    setScatterMetrics,
    setSelectedMetric,
  } = useExplorerStore();

  const [runAId, setRunAId] = useState<string>("");
  const [runBId, setRunBId] = useState<string>("");
  const [loadingBoth, setLoadingBoth] = useState(false);
  const [scatterPointsA, setScatterPointsA] = useState<ScatterPoint[]>([]);
  const [scatterPointsB, setScatterPointsB] = useState<ScatterPoint[]>([]);
  // Design-point inspector: which loaded run + iteration the user clicked in the scatter.
  const [inspect, setInspect] = useState<{ run: "A" | "B"; iter: number } | null>(null);
  const [resim, setResim] = useState<{
    loading: boolean;
    result: SimulateOnceResponse | null;
    error: string | null;
  }>({ loading: false, result: null, error: null });

  // Replace any selection (selectedMetric / scatter X / Y) that the freshly
  // loaded checkpoint doesn't actually contain, so non-cascode projects and
  // checkpoint switches don't leave the metric/scatter panels stuck empty.
  const reconcileMetrics = (keys: string[]) => {
    if (keys.length === 0) return;
    if (!keys.includes(selectedMetric)) setSelectedMetric(keys[0]);
    const x = keys.includes(scatterMetricX) ? scatterMetricX : keys[0];
    const y = keys.includes(scatterMetricY) ? scatterMetricY : keys[1] ?? keys[0];
    if (x !== scatterMetricX || y !== scatterMetricY) setScatterMetrics(x, y);
  };

  const loadBoth = async () => {
    if (!runAId && !runBId) return;
    setLoadingBoth(true);
    try {
      const tasks: Promise<unknown>[] = [];
      if (runAId) {
        tasks.push(
          api.loadCheckpoint(runAId).then(async (data) => {
            setRunA(data);
            reconcileMetrics(Object.keys(data.per_metric));
            const env = await api.envelope(runAId, yamlPath || undefined);
            setEnvelopeA(env);
          }),
        );
      } else {
        // Deselected: clear the stale A slot so it stops rendering.
        setRunA(null);
        setEnvelopeA(null);
        setScatterPointsA([]);
      }
      if (runBId) {
        tasks.push(
          api.loadCheckpoint(runBId).then((data) => {
            setRunB(data);
            if (!runAId) reconcileMetrics(Object.keys(data.per_metric));
          }),
        );
      } else {
        setRunB(null);
        setScatterPointsB([]);
      }
      await Promise.all(tasks);
    } finally {
      setLoadingBoth(false);
    }
  };

  useEffect(() => {
    if (!runA || !scatterMetricX || !scatterMetricY) return;
    api
      .scatter(runA.id, scatterMetricX, scatterMetricY, yamlPath || undefined)
      .then((r) => setScatterPointsA(r.points))
      .catch(() => setScatterPointsA([]));
  }, [runA, scatterMetricX, scatterMetricY, yamlPath]);

  useEffect(() => {
    if (!runB || !scatterMetricX || !scatterMetricY) return;
    api
      .scatter(runB.id, scatterMetricX, scatterMetricY, yamlPath || undefined)
      .then((r) => setScatterPointsB(r.points))
      .catch(() => setScatterPointsB([]));
  }, [runB, scatterMetricX, scatterMetricY, yamlPath]);

  const allMetrics = runA
    ? Object.keys(runA.per_metric)
    : runB
      ? Object.keys(runB.per_metric)
      : [];

  const scoreRuns = useMemo(
    () => [
      ...(runA
        ? [
            {
              label: runA.label,
              scores: runA.scores,
              best_scores: runA.best_scores,
              color: COLORS.primary,
              showRaw: false,
            },
          ]
        : []),
      ...(runB
        ? [
            {
              label: runB.label,
              scores: runB.scores,
              best_scores: runB.best_scores,
              color: COLORS.secondary,
              showRaw: false,
            },
          ]
        : []),
    ],
    [runA, runB],
  );

  const metricRuns = [
    ...(runA && runA.per_metric[selectedMetric]
      ? [{ label: runA.label, values: runA.per_metric[selectedMetric], color: COLORS.primary }]
      : []),
    ...(runB && runB.per_metric[selectedMetric]
      ? [{ label: runB.label, values: runB.per_metric[selectedMetric], color: COLORS.secondary }]
      : []),
  ];

  const histogramRuns = metricRuns;

  // Always emit BOTH slots (A first, B second) so the chart's positional color
  // (A=indigo, B=cyan) stays stable even when one run has no scatter points.
  const scatterRuns = [
    { label: runA?.label ?? "A", points: scatterPointsA },
    { label: runB?.label ?? "B", points: scatterPointsB },
  ];
  const hasScatter = scatterPointsA.length > 0 || scatterPointsB.length > 0;

  const selectedSpecObj = summary?.target_specs.find((s) => s.name === selectedMetric);
  const targetX = summary?.target_specs.find((s) => s.name === scatterMetricX)?.target;
  const targetY = summary?.target_specs.find((s) => s.name === scatterMetricY)?.target;
  const goalX = summary?.target_specs.find((s) => s.name === scatterMetricX)?.goal;
  const goalY = summary?.target_specs.find((s) => s.name === scatterMetricY)?.goal;

  const hasData = !!(runA || runB);

  // Envelope table data
  const enabledSpecs = summary?.target_specs.filter((s) => s.enable) ?? [];
  const envelopeRows = enabledSpecs.map((s) => {
    const aVals = runA?.per_metric[s.name]?.filter((v): v is number => v != null) ?? [];
    const bVals = runB?.per_metric[s.name]?.filter((v): v is number => v != null) ?? [];
    const aBest = bestOf(aVals, s.goal, s.target);
    const bBest = bestOf(bVals, s.goal, s.target);
    // Only a true head-to-head (both runs loaded, values differ) has a winner.
    // A tie, or only one run loaded, is neutral — previously ties silently went
    // to B and a single run was always declared the winner.
    let winner: "A" | "B" | null = null;
    if (aBest != null && bBest != null && aBest !== bBest) {
      const t = Number(s.target);
      if (s.goal === "exact" && Number.isFinite(t)) {
        // Closest-to-target wins; equidistant-but-different samples (e.g. 50 vs 70 for
        // target 60) are a neutral tie, not an arbitrary "B".
        const da = Math.abs(aBest - t);
        const db = Math.abs(bBest - t);
        winner = da === db ? null : da < db ? "A" : "B";
      } else {
        winner = (s.goal === "minimize" ? aBest < bBest : aBest > bBest) ? "A" : "B";
      }
    }
    return { spec: s, aBest, bBest, winner };
  });

  const totalEvals = (runA?.n_iters ?? 0) + (runB?.n_iters ?? 0);

  // KPI cards (A vs B). Pass rate over loaded specs; worst = the failing spec with
  // the biggest range-normalized miss; final score = last finite best-so-far.
  const passRate = (which: "aBest" | "bBest") => {
    const rows = envelopeRows.filter((r) => r[which] != null);
    if (!rows.length) return null;
    const pass = rows.filter((r) => passesSpec(r.spec, r[which]) === true).length;
    return { pass, total: rows.length };
  };
  const worstSpec = (which: "aBest" | "bBest") => {
    let name: string | null = null;
    let worst = 0;
    for (const r of envelopeRows) {
      const best = r[which];
      if (best == null || passesSpec(r.spec, best) !== false) continue;
      const rng = r.spec.range && r.spec.range > 0 ? r.spec.range : Math.max(Math.abs(Number(r.spec.target)) || 1, 1);
      const miss = Math.abs(best - Number(r.spec.target)) / rng;
      if (miss > worst) { worst = miss; name = r.spec.name; }
    }
    return name;
  };
  const finalA = lastFinite(runA?.best_scores);
  const finalB = lastFinite(runB?.best_scores);
  const passA = passRate("aBest");
  const passB = passRate("bBest");

  // Parallel-coordinates dimensions (metrics + params) + per-point color (score),
  // dropping points with any null across the dimensions so axes stay aligned.
  const parcoords = useMemo(() => {
    const run: CheckpointData | null = runA ?? runB;
    if (!run) return null;
    const dims = [
      ...Object.entries(run.per_metric).map(([k, v]) => ({ label: k, values: v })),
      ...Object.entries(run.params ?? {}).map(([k, v]) => ({ label: k, values: v })),
    ];
    if (dims.length < 2) return null;
    const n = run.scores.length;
    const clean = dims.map((d) => ({ label: d.label, values: [] as number[] }));
    const color: number[] = [];
    for (let i = 0; i < n; i++) {
      const row = dims.map((d) => d.values[i]);
      if (row.some((v) => v == null || !Number.isFinite(v as number))) continue;
      row.forEach((v, di) => clean[di].values.push(v as number));
      const sc = run.scores[i];
      color.push(sc != null && Number.isFinite(sc) ? sc : 0);
    }
    return clean[0].values.length > 0 ? { dims: clean, color } : null;
  }, [runA, runB]);

  // Resolve the inspected scatter point → its params + metrics at that iteration.
  const inspectedRun: CheckpointData | null = inspect ? (inspect.run === "B" ? runB : runA) : null;
  const inspected = (() => {
    if (!inspect || !inspectedRun) return null;
    const i = inspect.iter;
    const params: Record<string, number> = {};
    for (const [k, arr] of Object.entries(inspectedRun.params ?? {})) {
      const v = arr[i];
      if (v != null && Number.isFinite(v)) params[k] = v;
    }
    const metrics: Record<string, number> = {};
    for (const [k, arr] of Object.entries(inspectedRun.per_metric)) {
      const v = arr[i];
      if (v != null && Number.isFinite(v)) metrics[k] = v;
    }
    return { run: inspect.run, label: inspectedRun.label, iter: i, params, metrics, score: inspectedRun.scores[i] ?? null };
  })();

  const liveDisabled = env != null && !env.live_runs_enabled;
  const reSimulate = async () => {
    if (!inspected || !yamlPath) return;
    setResim({ loading: true, result: null, error: null });
    try {
      const res = await api.simulateOnce({ yaml_path: yamlPath, params: inspected.params });
      setResim({ loading: false, result: res, error: res.error ?? null });
    } catch (e) {
      setResim({ loading: false, result: null, error: e instanceof Error ? e.message : "Re-simulate failed" });
    }
  };

  return (
    <>
      <Toolbar>
        <ToolbarLabel>run A</ToolbarLabel>
        <select
          value={runAId}
          onChange={(e) => setRunAId(e.target.value)}
          className={selectCn("sm") + " w-[200px]"}
        >
          <option value="">— none —</option>
          {availableCheckpoints.map((ck) => (
            <option key={ck.id} value={ck.id}>
              {ck.label}
            </option>
          ))}
        </select>
        <ToolbarLabel>run B</ToolbarLabel>
        <select
          value={runBId}
          onChange={(e) => setRunBId(e.target.value)}
          className={selectCn("sm") + " w-[200px]"}
        >
          <option value="">— none —</option>
          {availableCheckpoints.map((ck) => (
            <option key={ck.id} value={ck.id}>
              {ck.label}
            </option>
          ))}
        </select>
        <Button variant="default" onClick={loadBoth} disabled={loadingBoth || (!runAId && !runBId)}>
          {loadingBoth ? "Loading…" : "Load both"}
        </Button>
        <Separator />
        <span className="font-mono text-[11px] text-muted">
          {[runA, runB].filter(Boolean).length} runs
          {totalEvals > 0 && <> · {totalEvals} evals</>}
        </span>
        <ToolbarSpacer />
        <Button
          variant="primary"
          disabled={!runA}
          onClick={() => { if (runA) window.open(api.reportUrl(runA.id, yamlPath || undefined), "_blank"); }}
          title={runA ? "Download a zip: checkpoint + project YAML + summary.md" : "Load run A first"}
        >
          Download report
        </Button>
      </Toolbar>

      {/* *:shrink-0 — keep Panels (overflow-hidden) from being flex-crushed/clipped;
          the container scrolls instead. */}
      <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-auto p-3 *:shrink-0">
        {!hasData && (
          <EmptyState bordered minHeight="min-h-32">
            Pick run A and/or B and click Load both to start exploring.
          </EmptyState>
        )}

        {hasData && (
          <div className="grid grid-cols-3 gap-2.5">
            <Stat
              eyebrow="final score"
              value={finalA != null ? formatEng(finalA) : "—"}
              delta={
                runB
                  ? `B ${finalB != null ? formatEng(finalB) : "—"}${finalA != null && finalB != null ? ` · Δ ${formatEng(finalA - finalB)}` : ""}`
                  : undefined
              }
              deltaTone={
                finalA != null && finalB != null
                  ? finalA > finalB ? "up" : finalA < finalB ? "down" : "neutral"
                  : "neutral"
              }
            />
            <Stat
              eyebrow="spec pass rate"
              value={passA ? `${passA.pass}/${passA.total}` : "—"}
              tone={passA && passA.pass === passA.total ? "ok" : passA && passA.pass === 0 ? "danger" : "warn"}
              delta={runB && passB ? `B ${passB.pass}/${passB.total}` : undefined}
            />
            <Stat
              eyebrow="worst spec (A)"
              value={worstSpec("aBest") ?? "all pass"}
              tone={worstSpec("aBest") ? "danger" : "ok"}
              delta={runB ? `B ${worstSpec("bBest") ?? "all pass"}` : undefined}
            />
          </div>
        )}

        {/* Row 1: F(x) overlay + metric overlay */}
        {hasData && (
          <div className="grid grid-cols-2 gap-2.5">
            <Panel>
              <PanelHeader
                title="F(x) convergence"
                mute="· A vs B"
                right={
                  <span className="font-mono text-[10px]">
                    {runA && (
                      <span style={{ color: COLORS.primary }}>● A</span>
                    )}{" "}
                    {runB && (
                      <span style={{ color: COLORS.secondary }}>● B</span>
                    )}
                  </span>
                }
              />
              <PanelBody>
                <ScoreConvergenceChart runs={scoreRuns} />
              </PanelBody>
            </Panel>
            <Panel>
              <PanelHeader
                title={
                  <>
                    <span className="font-mono">{selectedMetric || "—"}</span> · best-so-far
                  </>
                }
                right={
                  <select
                    value={selectedMetric}
                    onChange={(e) => setSelectedMetric(e.target.value)}
                    className={selectCn("xs")}
                  >
                    {allMetrics.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                }
              />
              <PanelBody>
                {metricRuns.length > 0 ? (
                  <MetricConvergenceChart
                    metric={selectedMetric}
                    runs={metricRuns}
                    target={selectedSpecObj?.target}
                    goal={selectedSpecObj?.goal}
                  />
                ) : (
                  <EmptyState minHeight="h-[220px]">No data.</EmptyState>
                )}
              </PanelBody>
            </Panel>
          </div>
        )}

        {/* Row 2: scatter + envelope */}
        {hasData && (
          <div className="grid grid-cols-2 gap-2.5">
            <Panel>
              <PanelHeader
                title="metric scatter"
                right={
                  <div className="flex items-center gap-1.5">
                    <select
                      value={scatterMetricX}
                      onChange={(e) =>
                        setScatterMetrics(e.target.value, scatterMetricY)
                      }
                      className={selectCn("xs")}
                    >
                      {allMetrics.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                    <span className="text-[10px] text-muted">vs</span>
                    <select
                      value={scatterMetricY}
                      onChange={(e) =>
                        setScatterMetrics(scatterMetricX, e.target.value)
                      }
                      className={selectCn("xs")}
                    >
                      {allMetrics.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </div>
                }
              />
              <PanelBody>
                {hasScatter ? (
                  <MetricScatterChart
                    runs={scatterRuns}
                    metricX={scatterMetricX}
                    metricY={scatterMetricY}
                    targetX={targetX}
                    targetY={targetY}
                    goalX={goalX}
                    goalY={goalY}
                    onPointClick={(sp, runIndex) => {
                      // Resolve by trace slot index (0=A, 1=B), not label — labels collide when the
                      // same checkpoint is loaded into both slots (BUG-B49).
                      setInspect({ run: runIndex === 1 ? "B" : "A", iter: sp.iter });
                      setResim({ loading: false, result: null, error: null });
                    }}
                  />
                ) : (
                  <EmptyState minHeight="h-[240px]">No scatter data.</EmptyState>
                )}
              </PanelBody>
            </Panel>

            <Panel className="flex min-h-0 flex-col">
              <PanelHeader title="performance envelope" mute="· best per spec" />
              <div className="min-h-0 flex-1 overflow-auto">
                {envelopeRows.length === 0 ? (
                  <EmptyState minHeight="min-h-32">No specs.</EmptyState>
                ) : (
                  <table className="w-full">
                    <Thead>
                      <Th>spec</Th>
                      <Th>target</Th>
                      <Th>run A best</Th>
                      <Th>run B best</Th>
                      <Th>winner</Th>
                    </Thead>
                    <tbody>
                      {envelopeRows.map(({ spec, aBest, bBest, winner }) => (
                        <Tr key={spec.name}>
                          <Td className="font-mono">{spec.name}</Td>
                          <Td className="font-mono text-muted">
                            {goalSymbol(spec.goal)} {formatEng(spec.target)}
                          </Td>
                          <Td
                            className="font-mono"
                            style={
                              winner === "A" ? { color: COLORS.primary, fontWeight: 500 } : {}
                            }
                          >
                            {aBest != null ? formatEng(aBest) : "—"}
                          </Td>
                          <Td
                            className="font-mono"
                            style={
                              winner === "B" ? { color: COLORS.secondary, fontWeight: 500 } : {}
                            }
                          >
                            {bBest != null ? formatEng(bBest) : "—"}
                          </Td>
                          <Td>
                            {winner ? (
                              <Badge variant={winner === "A" ? "indigo" : "cyan"}>
                                {winner}
                              </Badge>
                            ) : (
                              <Badge variant="neutral">—</Badge>
                            )}
                          </Td>
                        </Tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </Panel>
          </div>
        )}

        {/* Parallel coordinates — every metric + param dimension, one line per point */}
        {hasData && parcoords && (
          <Panel>
            <PanelHeader
              title="parallel coordinates"
              mute="· metrics + params · one line per evaluated point"
              right={<span className="font-mono text-[10px] text-muted">color = score</span>}
            />
            <PanelBody>
              <ParallelCoordinatesChart dims={parcoords.dims} color={parcoords.color} colorLabel="score" />
            </PanelBody>
          </Panel>
        )}

        {/* Row 3: histogram + spec summary */}
        {hasData && summary && (
          <div className="grid grid-cols-2 gap-2.5">
            <Panel>
              <PanelHeader
                title={
                  <>
                    <span className="font-mono">{selectedMetric}</span> distribution
                  </>
                }
                right={
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px]">
                      {runA && (
                        <span style={{ color: COLORS.primary }}>● A</span>
                      )}{" "}
                      {runB && (
                        <span style={{ color: COLORS.secondary }}>● B</span>
                      )}
                    </span>
                    <select
                      value={selectedMetric}
                      onChange={(e) => setSelectedMetric(e.target.value)}
                      className={selectCn("xs")}
                    >
                      {allMetrics.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </div>
                }
              />
              <PanelBody>
                {histogramRuns.length > 0 ? (
                  <MetricHistogramChart
                    runs={histogramRuns}
                    metric={selectedMetric}
                    target={selectedSpecObj?.target}
                  />
                ) : (
                  <EmptyState minHeight="h-[220px]">No data.</EmptyState>
                )}
              </PanelBody>
            </Panel>

            <Panel className="flex min-h-0 flex-col">
              <PanelHeader title="spec summary" mute="· pass / fail" />
              <div className="min-h-0 flex-1 overflow-auto">
                <table className="w-full">
                  <Thead>
                    <Th>spec</Th>
                    <Th>goal</Th>
                    {runA && <Th>A</Th>}
                    {runB && <Th>B</Th>}
                  </Thead>
                  <tbody>
                    {enabledSpecs.map((s) => {
                      const aVals = runA?.per_metric[s.name]?.filter(
                        (v): v is number => v != null,
                      );
                      const bVals = runB?.per_metric[s.name]?.filter(
                        (v): v is number => v != null,
                      );
                      const aBest = aVals?.length ? bestOf(aVals, s.goal, s.target) : null;
                      const bBest = bVals?.length ? bestOf(bVals, s.goal, s.target) : null;
                      const aPass = passesSpec(s, aBest);
                      const bPass = passesSpec(s, bBest);
                      return (
                        <Tr key={s.name}>
                          <Td className="font-mono">{s.name}</Td>
                          <Td className="font-mono text-muted">
                            {goalSymbol(s.goal)} {formatEng(s.target)}
                          </Td>
                          {runA && (
                            <Td>
                              {aPass == null ? (
                                <Badge variant="neutral" dot>
                                  —
                                </Badge>
                              ) : (
                                <Badge variant={aPass ? "ok" : "fail"} dot>
                                  {aPass ? "pass" : "fail"}
                                </Badge>
                              )}
                            </Td>
                          )}
                          {runB && (
                            <Td>
                              {bPass == null ? (
                                <Badge variant="neutral" dot>
                                  —
                                </Badge>
                              ) : (
                                <Badge variant={bPass ? "ok" : "fail"} dot>
                                  {bPass ? "pass" : "fail"}
                                </Badge>
                              )}
                            </Td>
                          )}
                        </Tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </Panel>
          </div>
        )}

        {envelopeA && (
          <Panel>
            <PanelHeader title="envelope (run A · raw)" mute="· server-side computed" />
            <div className="overflow-auto">
              <table className="w-full">
                <Thead>
                  <Th>metric</Th>
                  <Th>best ever</Th>
                  <Th>target</Th>
                  <Th>pass</Th>
                </Thead>
                <tbody>
                  {envelopeA.map((e) => (
                    <Tr key={e.metric}>
                      <Td className="font-mono">{e.metric}</Td>
                      <Td className="font-mono">{formatEng(e.best_ever)}</Td>
                      <Td className="font-mono text-muted">
                        {e.target != null ? formatEng(e.target) : "—"}
                      </Td>
                      <Td>
                        {e.passes != null ? (
                          <Badge variant={e.passes ? "ok" : "fail"} dot>
                            {e.passes ? "yes" : "no"}
                          </Badge>
                        ) : (
                          <Badge variant="neutral">—</Badge>
                        )}
                      </Td>
                    </Tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        )}

        {/* Design-point inspector — click a scatter point to open. Shows the point's
            full param vector + metrics at that iteration, and re-simulates it through
            the same /api/simulate/once primitive the Manual Sim view uses. */}
        {inspected && (
          <Panel>
            <PanelHeader
              title="design point"
              mute={`· run ${inspected.run} · iter ${inspected.iter}`}
              right={
                <div className="flex items-center gap-2">
                  <Button
                    variant="primary"
                    onClick={reSimulate}
                    disabled={resim.loading || liveDisabled || !yamlPath || Object.keys(inspected.params).length === 0}
                    title={liveDisabled ? "Re-simulate needs live SPICE (the IHP PDK)." : undefined}
                  >
                    {resim.loading ? "Simulating…" : "Re-simulate"}
                  </Button>
                  <button
                    type="button"
                    onClick={() => setInspect(null)}
                    className="rounded-sm px-1.5 text-muted hover:text-fg"
                    aria-label="Close inspector"
                  >
                    ✕
                  </button>
                </div>
              }
            />
            <PanelBody className="grid grid-cols-2 gap-4">
              <div>
                <div className="mb-1 text-[10px] font-medium uppercase tracking-wider text-muted">
                  params ({Object.keys(inspected.params).length})
                </div>
                <table className="w-full text-xs">
                  <tbody>
                    {Object.entries(inspected.params).map(([k, v]) => (
                      <tr key={k} className="border-b border-border last:border-0">
                        <td className="py-0.5 font-mono text-muted">{k}</td>
                        <td className="py-0.5 text-right font-mono">{formatEng(v)}</td>
                      </tr>
                    ))}
                    {Object.keys(inspected.params).length === 0 && (
                      <tr><td className="py-1 text-muted">No params in checkpoint.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
              <div>
                <div className="mb-1 text-[10px] font-medium uppercase tracking-wider text-muted">
                  metrics @ iter {inspected.iter}
                  {inspected.score != null && <> · score {formatEng(inspected.score)}</>}
                </div>
                <table className="w-full text-xs">
                  <tbody>
                    {Object.entries(inspected.metrics).map(([k, v]) => {
                      const re = resim.result?.metrics?.[k];
                      return (
                        <tr key={k} className="border-b border-border last:border-0">
                          <td className="py-0.5 font-mono text-muted">{k}</td>
                          <td className="py-0.5 text-right font-mono">{formatEng(v)}</td>
                          {resim.result && (
                            <td className="py-0.5 text-right font-mono text-secondary" title="re-simulated">
                              {re ? formatEng(re.curr_val) : "—"}
                            </td>
                          )}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {liveDisabled && (
                  <p className="mt-1.5 text-[10px] text-[#b45309]">PDK missing — re-simulate is disabled here (works in Docker).</p>
                )}
                {resim.error && (
                  <p className="mt-1.5 text-[11px] text-danger" role="alert">{resim.error}</p>
                )}
                {resim.result && !resim.error && (
                  <p className="mt-1.5 text-[10px] text-muted">
                    Re-simulated score {resim.result.score != null ? formatEng(resim.result.score) : "—"}
                    {resim.result.active_corner ? ` · corner ${resim.result.active_corner}` : ""}
                    {resim.result.elapsed_ms != null ? ` · ${(resim.result.elapsed_ms / 1000).toFixed(1)}s` : ""}
                  </p>
                )}
              </div>
            </PanelBody>
          </Panel>
        )}
      </div>
    </>
  );
}
