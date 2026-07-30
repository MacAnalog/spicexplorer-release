"use client";
import { PlotlyChart, COLORS } from "./PlotlyChart";

export interface WaterfallBar {
  name: string;
  /** Weighted penalty contribution wᵢ·P̂ᵢ (≥ 0). */
  contribution: number;
  passes: boolean | null;
}

/**
 * Horizontal bar chart of each spec's weighted penalty contribution to the
 * aggregate F(x) = Σ wᵢ·P̂ᵢ. Bars are colored green (passing → ~0 penalty) /
 * red (failing → positive penalty), so the binding constraints read at a glance.
 * Updates live as the Score-Shaping try-values change.
 */
export function ScoreWaterfallChart({
  bars,
  height = 240,
}: {
  bars: WaterfallBar[];
  height?: number;
}) {
  // Largest contribution at the top.
  const sorted = [...bars].sort((a, b) => a.contribution - b.contribution);
  const names = sorted.map((b) => b.name);
  const x = sorted.map((b) => b.contribution);
  const colors = sorted.map((b) =>
    b.passes === false ? COLORS.danger : b.passes === true ? COLORS.ok : COLORS.muted,
  );
  return (
    <PlotlyChart
      height={height}
      data={[
        {
          type: "bar",
          orientation: "h",
          x,
          y: names,
          marker: { color: colors },
          hovertemplate: "%{y}: %{x:.3f}<extra></extra>",
        },
      ]}
      layout={{
        margin: { l: 90, r: 14, t: 8, b: 28 },
        xaxis: { title: { text: "weighted penalty wᵢ·P̂ᵢ" }, rangemode: "tozero" },
        yaxis: { automargin: true },
        bargap: 0.35,
      }}
    />
  );
}
