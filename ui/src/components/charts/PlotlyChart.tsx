"use client";
import dynamic from "next/dynamic";
import type { PlotParams } from "react-plotly.js";

// Dynamic import avoids SSR issues with Plotly (uses window). The factory +
// plotly.js-dist-min pairing matters: the bare `react-plotly.js` entry pulls the
// FULL unminified plotly.js (~8 MB parsed on every dev compile/page load) — the
// dist-min build is the same API at less than half the parse cost.
const Plot = dynamic(
  () =>
    Promise.all([import("react-plotly.js/factory"), import("plotly.js-dist-min")]).then(
      ([factory, plotly]) => factory.default(plotly.default),
    ),
  { ssr: false },
);

const AXIS: Partial<Plotly.LayoutAxis> = {
  gridcolor: "rgba(0,0,0,0.06)",
  linecolor: "#a1a1aa",
  tickfont: { color: "#71717a", size: 10 },
  title: { font: { color: "#71717a", size: 10 } },
  zeroline: false,
  automargin: true,
};

const LAYOUT_BASE: Partial<Plotly.Layout> = {
  font: {
    family: "IBM Plex Mono, ui-monospace, monospace",
    size: 10,
    color: "#71717a",
  },
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  margin: { l: 44, r: 14, t: 14, b: 28 },
  showlegend: false,
  xaxis: AXIS,
  yaxis: AXIS,
  hoverlabel: {
    bgcolor: "#ffffff",
    bordercolor: "#e4e4e7",
    font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 11, color: "#0a0a0a" },
  },
};

export const COLORS = {
  // Observatory palette
  primary: "#4f46e5", // indigo-600
  primarySoft: "#eef2ff",
  secondary: "#0891b2", // cyan-600
  tertiary: "#ea580c", // orange-600 (current-value markers)
  ok: "#059669", // emerald-600 (targets / zero line)
  danger: "#dc2626", // metric target line
  muted: "#71717a",
  faint: "#a1a1aa",
  // Legacy aliases (kept so older code keeps compiling)
  indigo: "#4f46e5",
  sky: "#0891b2",
  emerald: "#059669",
  amber: "#dc2626",
  red: "#dc2626",
  zinc: "#71717a",
};

export const STROKE = {
  primary: 1.6,
  raw: 0.8,
  axis: 1,
};

interface Props extends Omit<PlotParams, "layout"> {
  layout?: Partial<Plotly.Layout>;
  height?: number;
  /** Fill the parent's height (flex plot areas) instead of a fixed `height` —
   *  the parent must own a real height; Plotly re-fits via the resize handler. */
  fill?: boolean;
  /** Override / extend the default Plotly config (merged over the curated default). */
  config?: Partial<Plotly.Config>;
}

// FontAwesome "download" glyph (512 viewbox) for the custom CSV modebar button.
const CSV_ICON = {
  width: 512,
  height: 512,
  path: "M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24z",
};

/** Serialize the chart's traces (x/y series) to CSV and trigger a download. */
function downloadTracesAsCsv(gd: { data?: unknown[] } | undefined) {
  const traces = (gd?.data ?? []) as Array<{
    x?: unknown[];
    y?: unknown[];
    name?: string;
  }>;
  if (!traces.length) return;
  const cols: { header: string; values: unknown[] }[] = [];
  traces.forEach((t, i) => {
    const label = (t.name ?? `trace${i}`).replace(/[",\n]/g, " ");
    if (Array.isArray(t.x)) cols.push({ header: `${label}.x`, values: t.x });
    if (Array.isArray(t.y)) cols.push({ header: `${label}.y`, values: t.y });
  });
  if (!cols.length) return;
  const rows = Math.max(...cols.map((c) => c.values.length));
  const esc = (v: unknown) => {
    const s = v == null ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [cols.map((c) => esc(c.header)).join(",")];
  for (let r = 0; r < rows; r++) {
    lines.push(cols.map((c) => esc(c.values[r])).join(","));
  }
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "chart-data.csv";
  a.click();
  URL.revokeObjectURL(url);
}

const DEFAULT_CONFIG: Partial<Plotly.Config> = {
  // Curated modebar: zoom/pan/autoscale/PNG + a custom CSV export; no lasso/select,
  // no Plotly logo. Shown on hover so it never crowds the small panels.
  displayModeBar: "hover",
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d"],
  modeBarButtonsToAdd: [
    {
      name: "Download CSV",
      title: "Download data as CSV",
      icon: CSV_ICON,
      click: (gd: unknown) => downloadTracesAsCsv(gd as { data?: unknown[] }),
    },
  ] as unknown as Plotly.Config["modeBarButtonsToAdd"],
};

function mergeAxis(
  base: Partial<Plotly.LayoutAxis>,
  override?: Partial<Plotly.LayoutAxis>,
): Partial<Plotly.LayoutAxis> {
  if (!override) return base;
  return {
    ...base,
    ...override,
    title: {
      ...(base.title || {}),
      ...(override.title || {}),
      font: { ...(base.title?.font || {}), ...(override.title?.font || {}) },
    },
    tickfont: { ...(base.tickfont || {}), ...(override.tickfont || {}) },
  };
}

export function PlotlyChart({ layout, height = 240, fill = false, config, ...rest }: Props) {
  const merged: Partial<Plotly.Layout> = {
    ...LAYOUT_BASE,
    ...layout,
    ...(fill ? { autosize: true } : { height }),
    xaxis: mergeAxis(AXIS, layout?.xaxis),
    yaxis: mergeAxis(AXIS, layout?.yaxis),
  };
  return (
    <Plot
      // react-plotly.js swallows plot failures (empty div, no exception) unless
      // an onError is supplied — surface them, or a bad trace/layout renders as
      // a silent blank panel. Callers may still override via {...rest}.
      onError={(err) => console.error("[PlotlyChart] plot failed:", err)}
      {...rest}
      layout={merged}
      config={{ ...DEFAULT_CONFIG, ...config }}
      style={fill ? { width: "100%", height: "100%" } : { width: "100%" }}
      useResizeHandler
    />
  );
}
