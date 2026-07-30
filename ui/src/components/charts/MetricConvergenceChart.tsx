"use client";
import { PlotlyChart, COLORS, STROKE } from "./PlotlyChart";

interface RunMetric {
  label: string;
  values: (number | null)[];
  color: string;
}

interface Props {
  metric: string;
  runs: RunMetric[];
  target?: number | null;
  goal?: string;
  unit?: string;
  height?: number;
}

function bestSoFar(
  values: (number | null)[],
  goal: string,
  target?: number | null,
): (number | null)[] {
  let best: number | null = null;
  const hasTarget = goal === "exact" && target !== null && target !== undefined;
  return values.map((v) => {
    if (v === null) return best;
    if (best === null) {
      best = v;
      return best;
    }
    if (goal === "minimize") best = Math.min(best, v);
    // For an exact target, "best so far" is the sample closest to the target — not a
    // monotonic running max that climbs straight past the target band.
    else if (hasTarget) best = Math.abs(v - target) < Math.abs(best - target) ? v : best;
    else best = Math.max(best, v);
    return best;
  });
}

export function MetricConvergenceChart({
  metric,
  runs,
  target,
  goal = "exceed",
  unit = "",
  height = 240,
}: Props) {
  const traces: Plotly.Data[] = [];

  for (const run of runs) {
    const bsf = bestSoFar(run.values, goal, target);
    const x = run.values.map((_, i) => i);
    traces.push({
      x,
      y: bsf,
      type: "scatter",
      mode: "lines",
      name: run.label,
      line: { color: run.color, width: STROKE.primary },
    });
  }

  const shapes: Partial<Plotly.Shape>[] = [];
  const annotations: Partial<Plotly.Annotations>[] = [];
  if (target !== null && target !== undefined) {
    shapes.push({
      type: "line",
      x0: 0,
      x1: 1,
      xref: "paper",
      y0: target,
      y1: target,
      yref: "y",
      line: { color: COLORS.danger, width: 1, dash: "dash" },
    });
    annotations.push({
      x: 1,
      xref: "paper",
      y: target,
      yref: "y",
      text: `target ${target}${unit}`,
      showarrow: false,
      xanchor: "right",
      yanchor: "bottom",
      font: { color: COLORS.danger, size: 10, family: "IBM Plex Mono, ui-monospace, monospace" },
      yshift: 2,
    });
  }

  return (
    <PlotlyChart
      data={traces}
      height={height}
      layout={{
        xaxis: { title: { text: "iteration" } },
        yaxis: { title: { text: metric } },
        shapes,
        annotations,
      }}
    />
  );
}
