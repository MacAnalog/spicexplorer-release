"use client";
import { PlotlyChart, COLORS, STROKE } from "./PlotlyChart";

interface RunSeries {
  label: string;
  scores: (number | null)[];
  best_scores: (number | null)[];
  color: string;
  /** If false, hide the raw per-iteration line (used in comparison view). */
  showRaw?: boolean;
}

interface Props {
  runs: RunSeries[];
  height?: number;
}

export function ScoreConvergenceChart({ runs, height = 240 }: Props) {
  const traces: Plotly.Data[] = [];

  for (const run of runs) {
    const x = run.scores.map((_, i) => i);
    if (run.showRaw !== false) {
      traces.push({
        x,
        y: run.scores,
        type: "scatter",
        mode: "lines",
        name: `${run.label} (raw)`,
        line: { color: COLORS.muted, width: STROKE.raw },
        opacity: 0.55,
        hoverinfo: "skip",
      });
    }
    traces.push({
      x,
      y: run.best_scores,
      type: "scatter",
      mode: "lines",
      name: `${run.label} (best)`,
      line: { color: run.color, width: STROKE.primary },
    });
  }

  return (
    <PlotlyChart
      data={traces}
      height={height}
      layout={{
        xaxis: { title: { text: "iteration" } },
        yaxis: { title: { text: "F(x)" } },
        shapes: [
          // emerald dashed zero line
          {
            type: "line",
            x0: 0,
            x1: 1,
            xref: "paper",
            y0: 0,
            y1: 0,
            yref: "y",
            line: { color: COLORS.ok, width: 1, dash: "dash" },
          },
        ],
      }}
    />
  );
}
