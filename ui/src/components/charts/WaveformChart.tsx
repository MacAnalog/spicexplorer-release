"use client";
import { PlotlyChart } from "./PlotlyChart";
import type { BuiltFigure } from "@/lib/waveview/figure";

/**
 * The Analyze view's waveform plot: a thin client wrapper over a prebuilt
 * figure from lib/waveview/figure.ts (the handoff's buildFigure/_layoutFor
 * split — data assembly and styling stay in the pure layer, never here).
 */
export function WaveformChart({
  figure,
  fill = true,
  height,
}: {
  figure: BuiltFigure;
  fill?: boolean;
  height?: number;
}) {
  return <PlotlyChart data={figure.data} layout={figure.layout} fill={fill} height={height} />;
}
