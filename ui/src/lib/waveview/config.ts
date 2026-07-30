// Presentation-only config for the Analyze waveform viewer (the lib/library/data.ts
// convention: no catalog/measurement DATA lives here — datasets, analyses, signals
// and the measurement catalog all come from /api/waveview/*). This file only says
// how backend-provided things are LABELLED, ORDERED and PLOTTED.

/** Display order for analysis tabs (unknown analyses append after, alphabetically). */
export const ANALYSIS_ORDER = [
  "tran",
  "ac",
  // the density spectrum ranks before the integrated-totals point analysis
  "noise_spectrum",
  "noise",
  "dc",
  "pss",
  "pac",
  "pnoise",
  "stb",
  "op",
] as const;

/** Tab / tree labels per engine-neutral analysis key (fallback = the raw key). */
export const ANALYSIS_LABEL: Record<string, string> = {
  tran: "Tran",
  ac: "AC Bode",
  noise: "Noise",
  noise_spectrum: "Noise Spec",
  dc: "DC",
  op: "OP",
  pss: "PSS",
  pac: "PAC",
  pnoise: "PNoise",
  stb: "STB",
};

/** Plot-header title + mono subtitle per base analysis (the handoff's `titles`). */
export const ANALYSIS_TITLES: Record<string, [string, string]> = {
  tran: ["Transient · time-domain response", "v(t) · step / large-signal"],
  ac: ["AC · loop-gain Bode", "|H| & ∠H · dual-axis"],
  // ngspice: `noise` is the integrated-totals point plot, `noise_spectrum` the
  // density curves; Spectre's density plot aliases to `noise` (engine chains).
  noise: ["Noise · totals & density", "integrated / per-device"],
  noise_spectrum: ["Noise · spectral density", "onoise / inoise"],
  dc: ["DC transfer", "output vs swept input"],
  pss: ["PSS · large-signal spectrum", "harmonics"],
  pac: ["PAC · periodic AC", "|H| & ∠H · dual-axis"],
  pnoise: ["PNoise · phase noise L(f)", "offset sweep"],
  stb: ["STB · loop stability", "loop gain & phase"],
  op: ["Operating point · DC scalars", "device table"],
};

/** The sweep-mode segmented options (the handoff's Single/PVT/Monte Carlo). */
export const SWEEP_OPTIONS = [
  { value: "single", label: "Single" },
  { value: "pvt", label: "PVT corners" },
  { value: "mc", label: "Monte Carlo" },
] as const;

/** MC band options (± half-width in σ). */
export const MC_SIGMA_OPTIONS = [
  { value: "1", label: "±1σ" },
  { value: "2", label: "±2σ" },
  { value: "3", label: "±3σ" },
] as const;

/** How each analysis is plotted. `dual` = magnitude (y1) + phase (y2) Bode split. */
export interface AnalysisPlotStyle {
  xScale: "log" | "lin";
  yScale: "log" | "lin";
  /** Fetch mag_db + phase_deg and render on twin y-axes (AC-family). */
  dual?: boolean;
  /** Render bars instead of lines (spectra). */
  bar?: boolean;
}

export const ANALYSIS_PLOT: Record<string, AnalysisPlotStyle> = {
  ac: { xScale: "log", yScale: "lin", dual: true },
  stb: { xScale: "log", yScale: "lin", dual: true },
  pac: { xScale: "log", yScale: "lin", dual: true },
  noise: { xScale: "log", yScale: "log" },
  noise_spectrum: { xScale: "log", yScale: "log" },
  pnoise: { xScale: "log", yScale: "log" },
  tran: { xScale: "lin", yScale: "lin" },
  dc: { xScale: "lin", yScale: "lin" },
  pss: { xScale: "lin", yScale: "lin", bar: true },
};

export const DEFAULT_PLOT_STYLE: AnalysisPlotStyle = { xScale: "lin", yScale: "lin" };

/** `fmt` values the /wave endpoint accepts, as Select options (complex is an
 *  internal transport format — not offered in the UI). */
export const FMT_OPTIONS = [
  { value: "auto", label: "auto" },
  { value: "mag_db", label: "mag · dB" },
  { value: "mag", label: "magnitude" },
  { value: "phase_deg", label: "phase · deg" },
  { value: "re", label: "real" },
  { value: "im", label: "imag" },
] as const;

/** Downsample presets for the /wave `method` + `max_points` params. */
export const DOWNSAMPLE_OPTIONS = [
  { value: "minmax:4000", label: "minmax · 4000" },
  { value: "minmax:2000", label: "minmax · 2000" },
  { value: "lttb:8000", label: "lttb · 8000" },
  { value: "none:200000", label: "none (full)" },
] as const;

/**
 * Tier-1 measures the performance strip *prefers*, in display order. This is a
 * presentation filter over the backend's measurement catalog — a measure renders
 * only if the catalog actually lists it AND all its required args can be filled
 * from the dataset (see buildMeasureItems). `unit` is display-only.
 */
export interface MeasurePresentation {
  meas: string;
  label: string;
  unit: string;
}

export const PREFERRED_MEASURES: MeasurePresentation[] = [
  { meas: "pm", label: "PM", unit: "°" },
  { meas: "ugf", label: "UGF", unit: "Hz" },
  { meas: "dcgain", label: "DC gain", unit: "dB" },
  { meas: "f3db", label: "f3dB", unit: "Hz" },
  { meas: "gbw", label: "GBW", unit: "Hz" },
  { meas: "cmrr_db", label: "CMRR", unit: "dB" },
  { meas: "psrr_vdd_db", label: "PSRR", unit: "dB" },
  { meas: "pm_loop", label: "PM·loop", unit: "°" },
  { meas: "gain_margin_db", label: "GM", unit: "dB" },
  { meas: "loopgain_db", label: "Loop gain", unit: "dB" },
  { meas: "inoise_total", label: "Vn,in", unit: "V" },
  { meas: "onoise_total", label: "Vn,out", unit: "V" },
];

/**
 * The four KPI Stat cards: each picks the first preferred measure that produced a
 * value (so an STB-only dataset's Stability card falls back to pm_loop, a dataset
 * without noise shows n/a).
 */
export const STAT_CARDS: { eyebrow: string; measures: string[] }[] = [
  { eyebrow: "stability · PM", measures: ["pm", "pm_loop"] },
  { eyebrow: "bandwidth · UGF", measures: ["ugf", "gbw", "f3db"] },
  { eyebrow: "dc gain", measures: ["dcgain", "loopgain_db"] },
  { eyebrow: "noise · integrated", measures: ["inoise_total", "onoise_total"] },
];

// Trace colors live in lib/waveview/figure.ts (signalRoles) — one role-based
// assignment shared by the plot and the tree swatches.
