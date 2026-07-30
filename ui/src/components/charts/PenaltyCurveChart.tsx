"use client";
import { PlotlyChart, COLORS, STROKE } from "./PlotlyChart";
import type { ScoreCurve } from "@/types/api";

interface Props {
  curve: ScoreCurve;
  currentValue?: number | null;
  height?: number;
}

export function PenaltyCurveChart({ curve, currentValue, height = 280 }: Props) {
  const shapes: Partial<Plotly.Shape>[] = [
    // emerald dashed = target
    {
      type: "line",
      x0: curve.target,
      x1: curve.target,
      xref: "x",
      y0: 0,
      y1: 1,
      yref: "paper",
      line: { color: COLORS.ok, width: 1, dash: "dash" },
    },
  ];
  if (currentValue !== null && currentValue !== undefined) {
    // orange solid = current
    shapes.push({
      type: "line",
      x0: currentValue,
      x1: currentValue,
      xref: "x",
      y0: 0,
      y1: 1,
      yref: "paper",
      line: { color: COLORS.tertiary, width: 1.2 },
    });
  }

  return (
    <PlotlyChart
      data={[
        // linear (cyan dashed)
        {
          x: curve.values,
          y: curve.linear,
          type: "scatter",
          mode: "lines",
          name: "Linear P̂",
          line: { color: COLORS.secondary, width: STROKE.primary, dash: "dash" },
        },
        // sigmoid (indigo solid)
        {
          x: curve.values,
          y: curve.sigmoid,
          type: "scatter",
          mode: "lines",
          name: "Sigmoid P̂",
          line: { color: COLORS.primary, width: STROKE.primary },
        },
      ]}
      height={height}
      layout={{
        xaxis: { title: { text: "metric m" } },
        yaxis: { title: { text: "P̂" }, rangemode: "tozero" },
        shapes,
      }}
    />
  );
}
