// Plotly figure builders for the Analyze viewer — the design handoff's
// buildFigure/_layoutFor split, ported against real /wave responses (see
// doc/handoffs/design_handoff_waveform_viewer/golden_ref/). Pure presentation:
// data comes in as WaveResponse/number[] series, styling and layout live here.
// The golden ref fixes axis ranges to its mock OTA; real datasets autorange —
// everything else (fonts, margins, grid, trace roles, derived-mark annotations)
// follows the handoff's Plotly tokens exactly.
import type { WaveResponse } from "@/types/api";
import { ACCENT } from "@/config/colors";
import { isDbNativeSignal } from "./selectors";

const SANS = "Inter Tight, system-ui, sans-serif";
const MONO = "IBM Plex Mono, ui-monospace, monospace";

/** Design-token grays used by the chart chrome (see the handoff's token table). */
const INK = {
  grid: "#f4f4f5",
  line: "#e4e4e7",
  tick: "#a1a1aa",
  legend: "#52525b",
  body: "#71717a",
  fg: "#0a0a0a",
} as const;

/** Trace palette for extra y1 series beyond the primary indigo. */
const EXTRA_SERIES = [
  ACCENT.secondary,
  ACCENT.violet,
  ACCENT.ok,
  "#d97706",
  "#2563eb",
  "#9333ea",
] as const;

/** Derived Tier-1 marks drawn on the plot (from POST /measure — never invented). */
export interface DerivedMarks {
  ugf?: number | null;
  pm?: number | null;
  thd?: number | null;
}

export interface BuiltFigure {
  data: Plotly.Data[];
  layout: Partial<Plotly.Layout>;
}

export interface WaveFigureOpts {
  /** Base analysis key ("ac", not "ac#2"). */
  analysis: string;
  xLog: boolean;
  /** Bode split: phase series ride y2. */
  dual: boolean;
  /** Whether any phase trace is actually plotted — a dual plot of only
   *  deck-computed dB curves has none, and drawing the empty y2 axis would
   *  imply a phase that was never fetched. Defaults to true. */
  hasPhase?: boolean;
  bar: boolean;
  yLog: boolean;
  /** Sweep-vector name for the x-axis title (e.g. "time", "frequency"). */
  xName?: string | null;
  /** Units of the plotted y series (from the dataset's SignalMeta). */
  yUnits?: string | null;
}

/** Base layout — the handoff's `base()`: margins l58 r56 t10 b44, white paper,
 *  Inter Tight 11, horizontal mono legend at the top, x-unified hover. */
export function baseLayout(overrides: Partial<Plotly.Layout>): Partial<Plotly.Layout> {
  return {
    autosize: true,
    margin: { l: 58, r: 56, t: 10, b: 44 },
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    font: { family: SANS, size: 11, color: INK.body },
    showlegend: true,
    legend: {
      orientation: "h",
      x: 0,
      y: 1.16,
      font: { size: 10, family: MONO, color: INK.legend },
      bgcolor: "rgba(0,0,0,0)",
    },
    hovermode: "x unified",
    hoverlabel: {
      font: { family: MONO, size: 10, color: INK.fg },
      bgcolor: "#ffffff",
      bordercolor: INK.line,
    },
    ...overrides,
  };
}

/** Axis defaults — the handoff's `ax()`: mono ticks/titles, hairline grid. */
export function axis(
  title: string,
  overrides: Partial<Plotly.LayoutAxis> = {},
): Partial<Plotly.LayoutAxis> {
  return {
    title: { text: title, font: { size: 10, family: MONO, color: INK.tick }, standoff: 8 },
    gridcolor: INK.grid,
    zeroline: false,
    linecolor: INK.line,
    ticks: "outside",
    tickcolor: INK.line,
    ticklen: 3,
    tickfont: { size: 9, family: MONO, color: INK.tick },
    ...overrides,
  };
}

/** Engineering-notation frequency ("7.1 MHz") for annotations. */
export function formatHz(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(v >= 1e10 ? 0 : 1)} GHz`;
  if (v >= 1e6) return `${(v / 1e6).toFixed(v >= 1e7 ? 0 : 1)} MHz`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)} kHz`;
  return `${v.toFixed(0)} Hz`;
}

/** Signals that read as stimulus/reference get the faint dotted treatment. */
function isReferenceSignal(name: string): boolean {
  // Threshold/marker vectors are reference even when they mention the output.
  if (/(^|[^a-z])(limit|floor|ref)/i.test(name)) return true;
  return /(^|[^a-z])(v?in|input|step)([^a-z]|$)/i.test(name) && !/out/i.test(name);
}

export type SignalRole = "primary" | "extra" | "reference";

/**
 * Role + color per plotted y1 signal — the single source the figure AND the
 * tree swatches read, so the rail never disagrees with the plot. First
 * non-reference signal is the indigo primary; other outputs cycle the extra
 * palette; stimulus/reference names go faint-dotted.
 */
export function signalRoles(
  names: string[],
): { name: string; role: SignalRole; color: string }[] {
  let extraIdx = 0;
  let sawPrimary = false;
  return names.map((name) => {
    if (isReferenceSignal(name)) return { name, role: "reference" as const, color: ACCENT.faint };
    if (!sawPrimary) {
      sawPrimary = true;
      return { name, role: "primary" as const, color: ACCENT.primary };
    }
    return {
      name,
      role: "extra" as const,
      color: EXTRA_SERIES[extraIdx++ % EXTRA_SERIES.length],
    };
  });
}

const numericY = (y: unknown): number[] => (Array.isArray(y) ? (y as number[]) : []);

/** Marks (0 dB line, UGF marker + "UGF · PM" note, THD note) for an analysis. */
function marksFor(
  analysis: string,
  derived: DerivedMarks,
  xLog: boolean,
): Pick<Plotly.Layout, "shapes" | "annotations"> {
  const shapes: Partial<Plotly.Shape>[] = [];
  const annotations: Partial<Plotly.Annotations>[] = [];
  if (analysis === "ac" || analysis === "stb" || analysis === "pac") {
    // 0 dB reference on the magnitude axis (only visible when the data crosses it).
    shapes.push({
      type: "line",
      xref: "paper",
      x0: 0,
      x1: 1,
      yref: "y",
      y0: 0,
      y1: 0,
      line: { color: ACCENT.ok, width: 1, dash: "dot" },
    });
    const { ugf, pm } = derived;
    if (ugf != null && ugf > 0) {
      // plotly.js v3 log-axis quirk: SHAPES take raw data coordinates, but
      // ANNOTATIONS still take log10 coordinates (verified empirically — the
      // handoff's all-log10 approach drew the marker at ~10⁰·⁹ Hz).
      shapes.push({
        type: "line",
        xref: "x",
        x0: ugf,
        x1: ugf,
        yref: "paper",
        y0: 0,
        y1: 1,
        line: { color: INK.tick, width: 1, dash: "dash" },
      });
      annotations.push({
        xref: "x",
        x: xLog ? Math.log10(ugf) : ugf,
        yref: "paper",
        y: 0.97,
        xanchor: "right",
        xshift: -5,
        text: `UGF ${formatHz(ugf)}${pm != null ? ` · PM ${pm.toFixed(0)}°` : ""}`,
        showarrow: false,
        font: { size: 9.5, family: MONO, color: INK.legend },
        align: "right",
      });
    }
  }
  if (analysis === "thd" && derived.thd != null) {
    annotations.push({
      xref: "paper",
      x: 0.98,
      yref: "paper",
      y: 0.03,
      xanchor: "right",
      yanchor: "bottom",
      text: `THD = ${derived.thd.toFixed(1)} dB`,
      showarrow: false,
      font: { size: 10, family: MONO, color: INK.legend },
    });
  }
  return { shapes: shapes as Plotly.Shape[], annotations: annotations as Plotly.Annotations[] };
}

/** Per-analysis layout — the handoff's `_layoutFor` with autoranged axes. */
export function layoutFor(opts: WaveFigureOpts, derived: DerivedMarks): Partial<Plotly.Layout> {
  const { analysis, xLog, dual, bar, yLog } = opts;
  const freqAxis = (title: string) =>
    axis(title, xLog ? { type: "log", dtick: 1 } : { type: "linear", exponentformat: "SI" });
  const linAxis = (title: string) =>
    axis(title, { type: xLog ? "log" : "linear", exponentformat: "SI" });
  const firstUnits = opts.yUnits ?? null;

  if (dual) {
    return baseLayout({
      xaxis: freqAxis("frequency · Hz"),
      yaxis: axis("magnitude · dB"),
      ...(opts.hasPhase === false
        ? {}
        : {
            yaxis2: axis("phase · deg", {
              overlaying: "y",
              side: "right",
              dtick: 45,
              showgrid: false,
            }),
          }),
      ...marksFor(analysis, derived, xLog),
    });
  }
  if (analysis === "noise" || analysis === "noise_spectrum") {
    return baseLayout({
      xaxis: freqAxis("frequency · Hz"),
      yaxis: axis(`noise · ${firstUnits ?? "V/√Hz"}`, { type: "log", exponentformat: "SI" }),
    });
  }
  if (analysis === "pnoise") {
    return baseLayout({
      showlegend: false,
      xaxis: freqAxis("offset frequency · Hz"),
      yaxis: axis(`L(f) · ${firstUnits ?? "dBc/Hz"}`),
    });
  }
  if (bar) {
    return baseLayout({
      showlegend: false,
      xaxis: axis("harmonic", { type: "category" }),
      yaxis: axis(`level · ${firstUnits ?? "dB"}`),
      ...marksFor(analysis, derived, false),
    });
  }
  if (analysis === "tran") {
    return baseLayout({
      xaxis: linAxis("time · s"),
      yaxis: axis(
        !firstUnits || firstUnits === "V" ? "voltage · V" : `signal · ${firstUnits}`,
        { exponentformat: "SI", ...(yLog ? { type: "log" } : {}) },
      ),
    });
  }
  if (analysis === "dc") {
    return baseLayout({
      showlegend: false,
      xaxis: linAxis(opts.xName ? `${opts.xName}` : "sweep"),
      yaxis: axis(firstUnits ?? "value", { exponentformat: "SI" }),
    });
  }
  return baseLayout({
    xaxis: linAxis(opts.xName ?? ""),
    yaxis: axis(firstUnits ?? "", {
      exponentformat: "SI",
      ...(yLog ? { type: "log" } : {}),
    }),
    ...marksFor(analysis, derived, xLog),
  });
}

/**
 * Single-run figure: the active wave (+ phase on y2 for Bode splits, + a dashed
 * overlay dataset). Trace roles per the handoff: primary output indigo w2.4,
 * stimulus/reference faint dotted, phase orange w2 on y2, overlay cyan dashed.
 */
export function buildWaveFigure(
  wave: WaveResponse,
  phase: WaveResponse | null | undefined,
  overlay: WaveResponse | null | undefined,
  overlayLabel: string | undefined,
  derived: DerivedMarks,
  opts: WaveFigureOpts,
): BuiltFigure {
  const data: Plotly.Data[] = [];
  const roles = signalRoles(wave.signals.map((s) => s.name));

  wave.signals.forEach((s, i) => {
    if (opts.bar) {
      data.push({
        type: "bar",
        x: s.x.map((v) => String(v)),
        y: numericY(s.y),
        name: s.name,
        width: 0.55,
        marker: { color: ACCENT.primary },
      });
      return;
    }
    const { role, color } = roles[i];
    data.push({
      type: "scatter",
      mode: "lines",
      x: s.x,
      y: numericY(s.y),
      // a deck-computed dB curve is not a magnitude-of-H — keep its own name
      name: opts.dual && !isDbNativeSignal(s.name) ? `|H| · ${s.name}` : s.name,
      line: {
        color,
        width: role === "reference" ? 1.4 : role === "primary" ? 2.4 : 1.8,
        ...(role === "reference" ? { dash: "dot" } : {}),
      },
    });
  });

  (phase?.signals ?? []).forEach((s, i) => {
    data.push({
      type: "scatter",
      mode: "lines",
      x: s.x,
      y: numericY(s.y),
      name: `∠ · ${s.name}`,
      yaxis: "y2",
      line: { color: ACCENT.tertiary, width: i === 0 ? 2 : 1.4, ...(i > 0 ? { dash: "dot" } : {}) },
    });
  });

  for (const s of overlay?.signals ?? []) {
    data.push({
      type: "scatter",
      mode: "lines",
      x: s.x,
      y: numericY(s.y),
      name: `${s.name} · ${overlayLabel ?? "overlay"}`,
      line: { color: ACCENT.secondary, width: 1.6, dash: "dash" },
    });
  }

  return {
    data,
    layout: layoutFor({ ...opts, hasPhase: (phase?.signals.length ?? 0) > 0 }, derived),
  };
}

// ── PVT corners ──────────────────────────────────────────────────────────────

/** One corner's curve set, already fetched + flagged by the sweep selectors. */
export interface CornerCurve {
  key: string;
  name: string;
  color: string;
  nominal: boolean;
  worst: boolean;
  x: number[];
  y: number[];
  phase?: number[] | null;
}

/**
 * PVT figure — the handoff's `_figurePVT`: a soft indigo min/max envelope band
 * across enabled corners, every corner's curve (nominal indigo w2.6, worst
 * orange w2, others their palette color at 0.42 opacity), and phase (Bode only)
 * for the nominal + worst corners as dotted y2 lines.
 */
export function buildPvtFigure(
  corners: CornerCurve[],
  derived: DerivedMarks,
  opts: WaveFigureOpts,
): BuiltFigure {
  const data: Plotly.Data[] = [];
  const ref = corners[0];
  if (ref) {
    const n = ref.x.length;
    const lo: number[] = new Array(n);
    const hi: number[] = new Array(n);
    for (let i = 0; i < n; i++) {
      let mn = Infinity;
      let mx = -Infinity;
      for (const c of corners) {
        const v = c.y[i];
        if (v == null || Number.isNaN(v)) continue;
        if (v < mn) mn = v;
        if (v > mx) mx = v;
      }
      lo[i] = mn === Infinity ? NaN : mn;
      hi[i] = mx === -Infinity ? NaN : mx;
    }
    data.push({
      type: "scatter",
      mode: "lines",
      x: ref.x,
      y: lo,
      line: { width: 0 },
      hoverinfo: "skip",
      showlegend: false,
    });
    data.push({
      type: "scatter",
      mode: "lines",
      x: ref.x,
      y: hi,
      line: { width: 0 },
      fill: "tonexty",
      fillcolor: "rgba(79,70,229,0.10)",
      name: "corner envelope",
      hoverinfo: "skip",
    });
  }
  for (const c of corners) {
    const color = c.nominal ? ACCENT.primary : c.worst ? ACCENT.tertiary : c.color;
    data.push({
      type: "scatter",
      mode: "lines",
      x: c.x,
      y: c.y,
      name: c.name,
      opacity: c.nominal || c.worst ? 1 : 0.42,
      showlegend: c.nominal || c.worst,
      line: { color, width: c.nominal ? 2.6 : c.worst ? 2 : 1 },
    });
    if (opts.dual && c.phase && (c.nominal || c.worst)) {
      data.push({
        type: "scatter",
        mode: "lines",
        x: c.x,
        y: c.phase,
        yaxis: "y2",
        opacity: 1,
        showlegend: false,
        name: `∠ · ${c.name}`,
        line: { color: c.worst ? ACCENT.tertiary : "#f59e0b", width: 1.4, dash: "dot" },
      });
    }
  }
  const hasPhase = corners.some((c) => (c.nominal || c.worst) && !!c.phase);
  return { data, layout: layoutFor({ ...opts, hasPhase }, derived) };
}

// ── Monte Carlo ──────────────────────────────────────────────────────────────

export interface McCurves {
  x: number[];
  /** Individual sample curves (a thin ghost is drawn for up to 48 of them). */
  samples: number[][];
  mean: number[];
  sd: number[];
}

/** MC figure — the handoff's `_figureMC`: ghost samples, a ±kσ band, the mean. */
export function buildMcFigure(
  mc: McCurves,
  sigmaBand: number,
  derived: DerivedMarks,
  opts: WaveFigureOpts,
): BuiltFigure {
  const data: Plotly.Data[] = [];
  const step = Math.max(1, Math.floor(mc.samples.length / 48));
  for (let i = 0; i < mc.samples.length; i += step) {
    data.push({
      type: "scatter",
      mode: "lines",
      x: mc.x,
      y: mc.samples[i],
      line: { color: ACCENT.primary, width: 0.7 },
      opacity: 0.1,
      hoverinfo: "skip",
      showlegend: false,
    });
  }
  const lo = mc.mean.map((m, i) => m - sigmaBand * mc.sd[i]);
  const hi = mc.mean.map((m, i) => m + sigmaBand * mc.sd[i]);
  data.push({
    type: "scatter",
    mode: "lines",
    x: mc.x,
    y: lo,
    line: { width: 0 },
    hoverinfo: "skip",
    showlegend: false,
  });
  data.push({
    type: "scatter",
    mode: "lines",
    x: mc.x,
    y: hi,
    line: { width: 0 },
    fill: "tonexty",
    fillcolor: "rgba(79,70,229,0.13)",
    name: `±${sigmaBand}σ`,
    hoverinfo: "skip",
  });
  data.push({
    type: "scatter",
    mode: "lines",
    x: mc.x,
    y: mc.mean,
    name: "mean",
    line: { color: ACCENT.primary, width: 2.4 },
  });
  // the MC figure never plots phase — don't draw an empty y2 axis
  return { data, layout: layoutFor({ ...opts, hasPhase: false }, derived) };
}

/**
 * Metric histogram — the handoff's `buildHistogram`: 26 bins over the sampled
 * metric, pass bins indigo / fail bins red, dashed red spec line + green mean.
 */
export function buildHistogramFigure(
  values: number[],
  spec: { value: number; cmp: "ge" | "le" } | null,
  label: string,
  unit: string,
): BuiltFigure {
  let mn = Math.min(...values);
  let mx = Math.max(...values);
  if (spec) {
    mn = Math.min(mn, spec.value);
    mx = Math.max(mx, spec.value);
  }
  const pad = (mx - mn || 1) * 0.08;
  mn -= pad;
  mx += pad;
  const bins = 26;
  const w = (mx - mn) / bins;
  const counts = new Array<number>(bins).fill(0);
  for (const v of values) {
    let k = Math.floor((v - mn) / w);
    if (k < 0) k = 0;
    if (k >= bins) k = bins - 1;
    counts[k]++;
  }
  const centers: number[] = [];
  const colors: string[] = [];
  for (let i = 0; i < bins; i++) {
    const c = mn + (i + 0.5) * w;
    centers.push(c);
    const ok = !spec || (spec.cmp === "ge" ? c >= spec.value : c <= spec.value);
    colors.push(ok ? ACCENT.primary : "#dc2626");
  }
  const mean = values.reduce((a, b) => a + b, 0) / (values.length || 1);
  const shapes: Partial<Plotly.Shape>[] = [
    {
      type: "line",
      xref: "x",
      x0: mean,
      x1: mean,
      yref: "paper",
      y0: 0,
      y1: 1,
      line: { color: ACCENT.ok, width: 1.5 },
    },
  ];
  const annotations: Partial<Plotly.Annotations>[] = [
    {
      xref: "x",
      x: mean,
      yref: "paper",
      y: 1,
      yanchor: "top",
      xanchor: "left",
      text: `μ ${mean.toFixed(1)}`,
      showarrow: false,
      font: { size: 9, family: MONO, color: ACCENT.ok },
    },
  ];
  if (spec) {
    shapes.unshift({
      type: "line",
      xref: "x",
      x0: spec.value,
      x1: spec.value,
      yref: "paper",
      y0: 0,
      y1: 1,
      line: { color: "#dc2626", width: 1.5, dash: "dash" },
    });
    annotations.unshift({
      xref: "x",
      x: spec.value,
      yref: "paper",
      y: 1,
      yanchor: "top",
      xanchor: spec.cmp === "ge" ? "left" : "right",
      text: `spec ${spec.value}`,
      showarrow: false,
      font: { size: 9, family: MONO, color: "#dc2626" },
    });
  }
  return {
    data: [
      {
        type: "bar",
        x: centers,
        y: counts,
        marker: { color: colors },
        width: w * 0.92,
        hovertemplate: `%{y} samples<br>%{x:.2f} ${unit}<extra></extra>`,
      },
    ],
    layout: baseLayout({
      showlegend: false,
      margin: { l: 44, r: 14, t: 6, b: 34 },
      bargap: 0.04,
      xaxis: axis(`${label} · ${unit}`),
      yaxis: axis("count"),
      shapes: shapes as Plotly.Shape[],
      annotations: annotations as Plotly.Annotations[],
    }),
  };
}
