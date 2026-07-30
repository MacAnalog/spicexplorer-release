"use client";
import { PlotlyChart, COLORS } from "./PlotlyChart";
import type { ParamSensitivity } from "@/types/api";

/**
 * Horizontal bar chart of per-parameter sensitivity for one spec. Positive bars
 * (indigo) raise the metric, negative bars (orange) lower it. Bars are ordered
 * most-influential-first (the backend sorts by |elasticity|); we keep that order
 * top-to-bottom via a reversed y-axis.
 */
export function SensitivityChart({
  params,
  metric,
}: {
  params: ParamSensitivity[];
  metric: "elasticity" | "sensitivity";
}) {
  const usable = params.filter((p) => p[metric] != null);
  if (usable.length === 0) {
    return (
      <div className="flex h-24 items-center justify-center text-[11px] text-faint">
        No finite sensitivities at this point.
      </div>
    );
  }
  const labels = usable.map((p) => `${p.device}·${p.kind}`);
  const values = usable.map((p) => p[metric] as number);
  const colors = values.map((v) => (v >= 0 ? COLORS.primary : COLORS.tertiary));

  return (
    <PlotlyChart
      data={[
        {
          type: "bar",
          orientation: "h",
          x: values,
          y: labels,
          marker: { color: colors },
          hovertemplate: "%{y}: %{x:.3g}<extra></extra>",
        },
      ]}
      layout={{
        margin: { l: 96, r: 14, t: 8, b: 30 },
        xaxis: {
          title: {
            text: metric === "elasticity" ? "elasticity (Δm/m ÷ Δp/p)" : "d(metric)/d(param)",
          },
        },
        yaxis: { automargin: true, autorange: "reversed" },
      }}
      height={Math.max(120, usable.length * 26 + 44)}
    />
  );
}
