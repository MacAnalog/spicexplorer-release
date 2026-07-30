"use client";
import { PlotlyChart, COLORS } from "./PlotlyChart";

export interface ParCoordDim {
  label: string;
  values: number[];
}

/**
 * Parallel-coordinates plot: one vertical axis per dimension (each spec metric +
 * each swept DUT param), one polyline per evaluated point, colored by a scalar
 * (feasibility or score). Native Plotly `parcoords` — the classic multidimensional
 * design-space view that the scatter (only 2 axes) can't show.
 */
export function ParallelCoordinatesChart({
  dims,
  color,
  colorLabel = "score",
  height = 300,
}: {
  dims: ParCoordDim[];
  /** Per-point scalar used for the line color (same length as each dim's values). */
  color: number[];
  colorLabel?: string;
  height?: number;
}) {
  return (
    <PlotlyChart
      height={height}
      data={[
        {
          type: "parcoords",
          line: {
            color,
            colorscale: [
              [0, COLORS.danger],
              [0.5, COLORS.tertiary],
              [1, COLORS.ok],
            ],
            showscale: true,
            colorbar: { title: { text: colorLabel }, thickness: 8, len: 0.9 },
          },
          dimensions: dims.map((d) => ({ label: d.label, values: d.values })),
        } as unknown as Plotly.Data,
      ]}
      layout={{ margin: { l: 60, r: 30, t: 28, b: 18 } }}
    />
  );
}
