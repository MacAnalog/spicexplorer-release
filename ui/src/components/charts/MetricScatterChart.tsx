"use client";
import { PlotlyChart, COLORS } from "./PlotlyChart";
import { paretoFront } from "@/lib/pareto";
import type { ScatterPoint } from "@/types/api";

interface RunScatter {
  label: string;
  points: ScatterPoint[];
}

interface Props {
  runs: RunScatter[];
  metricX: string;
  metricY: string;
  targetX?: number | null;
  targetY?: number | null;
  goalX?: string;
  goalY?: string;
  height?: number;
  /** Overlay the non-dominated (Pareto) frontier over feasible points. */
  showPareto?: boolean;
  /** Click a point → inspect it (params/metrics at its iteration). */
  onPointClick?: (point: ScatterPoint, runIndex: number) => void;
}

function feasibleRect(
  pts: ScatterPoint[],
  targetX: number | null | undefined,
  targetY: number | null | undefined,
  goalX: string,
  goalY: string,
): Partial<Plotly.Shape> | null {
  if (targetX == null || targetY == null || pts.length === 0) return null;
  // An `exact` goal's feasible region is a BAND around target (needs tolerance, not available here),
  // NOT the corner half-plane this rect models — drawing the half-plane is misleading, so skip it and
  // rely on the (correct, backend-computed) per-point feasibility coloring instead (BUG-B45).
  if (goalX === "exact" || goalY === "exact") return null;
  // for-loop min/max, not Math.min(...xs): a long run's point array overflows
  // the call stack when spread as arguments.
  let xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity;
  for (const p of pts) {
    if (p.x < xmin) xmin = p.x;
    if (p.x > xmax) xmax = p.x;
    if (p.y < ymin) ymin = p.y;
    if (p.y > ymax) ymax = p.y;
  }
  const x0 = goalX === "minimize" ? xmin : targetX;
  const x1 = goalX === "minimize" ? targetX : xmax;
  const y0 = goalY === "minimize" ? ymin : targetY;
  const y1 = goalY === "minimize" ? targetY : ymax;
  return {
    type: "rect",
    x0,
    x1,
    y0,
    y1,
    xref: "x",
    yref: "y",
    line: { width: 0 },
    fillcolor: COLORS.ok,
    opacity: 0.05,
    layer: "below",
  };
}

export function MetricScatterChart({
  runs,
  metricX,
  metricY,
  targetX,
  targetY,
  goalX = "exceed",
  goalY = "minimize",
  height = 240,
  showPareto = true,
  onPointClick,
}: Props) {
  const traces: Plotly.Data[] = [];
  const feasibleColors = [COLORS.primary, COLORS.secondary];

  runs.forEach((run, ri) => {
    const feasible = run.points.filter((p) => p.feasible);
    const infeasible = run.points.filter((p) => !p.feasible);
    const col = feasibleColors[ri % feasibleColors.length];

    if (infeasible.length) {
      traces.push({
        x: infeasible.map((p) => p.x),
        y: infeasible.map((p) => p.y),
        customdata: infeasible as unknown as Plotly.Datum[],
        meta: ri,  // run slot index — disambiguates click attribution when labels collide (BUG-B49)
        type: "scatter",
        mode: "markers",
        name: `${run.label} (infeasible)`,
        marker: { color: COLORS.faint, size: 4, opacity: 0.5 },
      } as Plotly.Data);
    }
    if (feasible.length) {
      traces.push({
        x: feasible.map((p) => p.x),
        y: feasible.map((p) => p.y),
        customdata: feasible as unknown as Plotly.Datum[],
        meta: ri,  // run slot index (BUG-B49)
        type: "scatter",
        mode: "markers",
        name: `${run.label}`,
        marker: { color: col, size: 5, opacity: 0.85 },
      } as Plotly.Data);
    }
  });

  // Pareto frontier over the union of feasible points (non-dominated trade-offs).
  if (showPareto) {
    const feasibleAll = runs.flatMap((r) => r.points).filter((p) => p.feasible);
    const front = paretoFront(feasibleAll, goalX, goalY, targetX, targetY);
    if (front.length > 1) {
      traces.push({
        x: front.map((p) => p.x),
        y: front.map((p) => p.y),
        type: "scatter",
        mode: "lines+markers",
        name: "Pareto front",
        line: { color: COLORS.tertiary, width: 1.4 },
        marker: { color: COLORS.tertiary, size: 6, symbol: "diamond" },
        hoverinfo: "skip",
      });
    }
  }

  const allPoints = runs.flatMap((r) => r.points);
  const shapes: Partial<Plotly.Shape>[] = [];
  const region = feasibleRect(allPoints, targetX, targetY, goalX, goalY);
  if (region) shapes.push(region);

  if (targetX != null) {
    shapes.push({
      type: "line",
      x0: targetX,
      x1: targetX,
      xref: "x",
      y0: 0,
      y1: 1,
      yref: "paper",
      line: { color: COLORS.ok, dash: "dash", width: 1 },
    });
  }
  if (targetY != null) {
    shapes.push({
      type: "line",
      x0: 0,
      x1: 1,
      xref: "paper",
      y0: targetY,
      y1: targetY,
      yref: "y",
      line: { color: COLORS.ok, dash: "dash", width: 1 },
    });
  }

  return (
    <PlotlyChart
      data={traces}
      height={height}
      onClick={
        onPointClick
          ? (e) => {
              const pt = e.points?.[0];
              const sp = pt?.customdata as unknown as ScatterPoint | undefined;
              if (sp && typeof sp.iter === "number") {
                onPointClick(sp, Number((pt?.data as { meta?: number } | undefined)?.meta ?? 0));
              }
            }
          : undefined
      }
      layout={{
        xaxis: { title: { text: metricX } },
        yaxis: { title: { text: metricY } },
        shapes,
      }}
    />
  );
}
