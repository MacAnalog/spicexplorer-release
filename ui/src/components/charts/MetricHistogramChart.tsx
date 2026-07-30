"use client";
import { PlotlyChart, COLORS } from "./PlotlyChart";

interface RunHistogram {
  label: string;
  values: (number | null)[];
  color: string;
}

interface Props {
  runs: RunHistogram[];
  metric: string;
  target?: number | null;
  nbins?: number;
  height?: number;
}

export function MetricHistogramChart({
  runs,
  metric,
  target,
  nbins = 40,
  height = 220,
}: Props) {
  // A: indigo 70%, B: cyan 55%
  const opacities = [0.7, 0.55];
  const traces: Plotly.Data[] = runs.map((run, i) => ({
    x: run.values.filter((v): v is number => v !== null),
    type: "histogram",
    name: run.label,
    nbinsx: nbins,
    opacity: opacities[i] ?? 0.55,
    marker: { color: run.color, line: { width: 0 } },
  }));

  const shapes: Partial<Plotly.Shape>[] = [];
  if (target != null) {
    shapes.push({
      type: "line",
      x0: target,
      x1: target,
      xref: "x",
      y0: 0,
      y1: 1,
      yref: "paper",
      line: { color: COLORS.danger, width: 1, dash: "dash" },
    });
  }

  return (
    <PlotlyChart
      data={traces}
      height={height}
      layout={{
        xaxis: { title: { text: metric } },
        yaxis: { title: { text: "count" } },
        barmode: "overlay",
        bargap: 0.02,
        shapes,
      }}
    />
  );
}
