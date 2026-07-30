// Pure derivations for the Analyze waveform viewer (the lib/library/selectors.ts
// convention: no fetching, no store access — dataset/catalog shapes in, view
// models out; vitest-covered). Everything derives from backend data.
import type {
  MeasurementCatalogResponse,
  TargetSpec,
  WaveAnalysisMeta,
  WaveDatasetMeta,
  WaveMeasureRequest,
  WaveMeasureResult,
} from "@/types/api";
import { statusForGoal } from "@/lib/utils";
import { foldMeasName, tbMatchFromPath } from "./sweep";
import type { AnalysisPlotStyle } from "./config";
import {
  ANALYSIS_LABEL,
  ANALYSIS_ORDER,
  ANALYSIS_PLOT,
  DEFAULT_PLOT_STYLE,
  PREFERRED_MEASURES,
} from "./config";

/**
 * The engine-neutral key behind a possibly-suffixed analysis key. A merged
 * open_run dataset disambiguates duplicate analyses as "ac#2"/"ac#3" — every
 * config lookup (label, plot style, ordering, measure defaults) works off the
 * base so a second AC testbench still renders as a Bode.
 */
export function baseAnalysis(key: string): string {
  const i = key.indexOf("#");
  return i === -1 ? key : key.slice(0, i);
}

/** Tab label for an engine-neutral analysis key (falls back to the raw key).
 *  A merged-dataset suffix ("ac#2") keeps its ordinal: "AC Bode #2". */
export function analysisLabel(key: string): string {
  const base = baseAnalysis(key);
  const label = ANALYSIS_LABEL[base] ?? base.toUpperCase();
  return base === key ? label : `${label} #${key.slice(base.length + 1)}`;
}

/** Plot style for a (possibly suffixed) analysis key, with the config fallback. */
export function plotStyleFor(key: string | null): AnalysisPlotStyle {
  return (key ? ANALYSIS_PLOT[baseAnalysis(key)] : undefined) ?? DEFAULT_PLOT_STYLE;
}

/** A dataset's analyses in presentation order (config order, unknowns appended A→Z). */
export function orderedAnalyses(ds: WaveDatasetMeta): WaveAnalysisMeta[] {
  const rank = (a: WaveAnalysisMeta) => {
    const i = (ANALYSIS_ORDER as readonly string[]).indexOf(baseAnalysis(a.analysis));
    return i === -1 ? ANALYSIS_ORDER.length : i;
  };
  return [...ds.analyses].sort(
    (a, b) => rank(a) - rank(b) || a.analysis.localeCompare(b.analysis),
  );
}

/** Non-sweep signal names of an analysis (the sweep vector is the x axis). */
export function plottableSignals(a: WaveAnalysisMeta): string[] {
  return a.signals.map((s) => s.name).filter((n) => n !== a.sweep);
}

/** Whether a signal name looks like a circuit output (drives default selection). */
function looksLikeOutput(name: string): boolean {
  return /out/i.test(name);
}

/**
 * Deck-computed traces that are ALREADY in dB (`let cmrr_db_curve = -vdb(v_out)`
 * — the rejection benches' +CMRR(f)/+PSRR(f)). The fetch layer pulls these with
 * fmt=re and plots them directly on the dB magnitude axis: an ngspice AC plot
 * stores even `let`-derived vectors as complex (the value in the real part), so
 * fmt=auto/mag_db resolve to 20·log10(|v|) and silently double-log the curve.
 * Their phase is that of a real vector (0°/180°) and is never fetched.
 */
export function isDbNativeSignal(name: string): boolean {
  return /_db_curve$/i.test(name.trim());
}

/**
 * Default plotted signals for an analysis: deck-computed dB curves first (on a
 * rejection bench they ARE the bench's purpose-built view), then output-looking
 * voltages, then the rest — and within each group, top-level vectors before
 * subcircuit-internal (dotted) ones, so a noise raw defaults to
 * inoise/onoise_spectrum rather than 200 per-device contributions. Capped so a
 * huge raw doesn't flood the plot.
 */
export function defaultSignals(a: WaveAnalysisMeta, cap = 4): string[] {
  const all = plottableSignals(a);
  const rank = (n: string) =>
    (isDbNativeSignal(n) ? -4 : 0) +
    (looksLikeOutput(n) ? 0 : 2) +
    (n.includes(".") ? 1 : 0);
  return [...all].sort((x, y) => rank(x) - rank(y)).slice(0, cap);
}

/**
 * The signal used as the Tier-1 measures' `out` argument. Prefer an
 * output-looking signal from the AC-family analysis (that's what dcgain/ugf/pm
 * read), then any output-looking signal, then the first plottable one.
 */
export function guessOutSignal(ds: WaveDatasetMeta): string | null {
  const acFirst = orderedAnalyses(ds).sort(
    (a, b) =>
      Number(baseAnalysis(b.analysis) === "ac") - Number(baseAnalysis(a.analysis) === "ac"),
  );
  for (const a of acFirst) {
    const hit = plottableSignals(a).find(looksLikeOutput);
    if (hit) return hit;
  }
  for (const a of acFirst) {
    const [first] = plottableSignals(a);
    if (first) return first;
  }
  return null;
}

/**
 * Route one composite measure to the analysis it should run against in a merged
 * multi-bench dataset (`{analysis: …}` recipe override; the registry honors it).
 *
 * Without a pin, the server resolves each measure's KIND to the FIRST matching
 * analysis — in a merged sweep run whose first ac member is the PSRR bench, PM
 * comes back null and "DC gain"/"CMRR" quietly report the −residual (the
 * observed −29.6 dB DC gain). Rules:
 *  - cmrr_db / psrr_vdd_db → the ac analysis of the matching bench (by the
 *    member's testbench name); when bench names are known and no such bench
 *    exists, the measure is SKIPPED rather than mis-measured.
 *  - other ac measures (pm/ugf/dcgain/…) → the first ac analysis that is NOT a
 *    rejection bench (the loop-gain/main bench).
 *  - noise totals → the DENSITY analysis + signal (inoise/onoise_spectrum);
 *    integrating the integrated-noise scalar (or the display signal) is
 *    meaningless.
 * Returns extra recipe fields, or "skip" to drop the item.
 */
function routeMeasure(
  meas: string,
  kindAnalysis: string,
  analyses: WaveAnalysisMeta[],
): Record<string, unknown> | "skip" | null {
  if (!analyses.length) return null;
  const infos = analyses.map((a) => ({
    key: a.analysis,
    base: baseAnalysis(a.analysis),
    tb: (tbMatchFromPath(a.native_name ?? "") ?? "").replace(/^tb[-_]/, "").toLowerCase(),
    signals: new Set(a.signals.map((s) => s.name)),
  }));

  if (kindAnalysis === "noise") {
    const density = meas.startsWith("inoise") ? "inoise_spectrum" : "onoise_spectrum";
    const spec =
      infos.find((i) => i.base === "noise_spectrum" && i.signals.has(density)) ??
      infos.find((i) => i.base === "noise" && i.signals.has(density));
    return spec ? { analysis: spec.key, out: density } : "skip";
  }

  const ofKind = infos.filter((i) => i.base === kindAnalysis);
  if (ofKind.length === 0) return null; // server-side per-item error stays the signal
  const benchNamesKnown = ofKind.some((i) => i.tb !== "");
  const want = meas.includes("cmrr") ? "cmrr" : meas.includes("psrr") ? "psrr" : null;
  if (want) {
    const hit = ofKind.find((i) => i.tb.includes(want));
    if (hit) return { analysis: hit.key };
    return benchNamesKnown ? "skip" : null; // unknown benches → legacy behavior
  }
  const main = ofKind.find((i) => !i.tb.includes("cmrr") && !i.tb.includes("psrr")) ?? ofKind[0];
  return main.key === kindAnalysis ? null : { analysis: main.key };
}

/**
 * Build the /measure request from the backend's measurement catalog: only
 * preferred measures the catalog actually lists, and only those whose required
 * args can all be filled (currently just `out`). In a merged multi-bench
 * dataset each item is pinned to its bench's analysis (see `routeMeasure`).
 * Per-item failures degrade server-side (value=null + error), so requesting
 * e.g. `pm` against a dataset with no AC analysis is safe.
 */
export function buildMeasureItems(
  catalog: MeasurementCatalogResponse | null,
  outSignal: string | null,
  analyses: WaveAnalysisMeta[] | null = null,
): WaveMeasureRequest {
  if (!catalog || !outSignal) return { items: [] };
  const fillable: Record<string, string> = { out: outSignal };
  const items: { name: string; recipe: Record<string, unknown> }[] = [];
  for (const p of PREFERRED_MEASURES) {
    const info = catalog.measurements[p.meas];
    if (!info || !info.required.every((arg) => arg in fillable)) continue;
    const recipe: Record<string, unknown> = { meas: p.meas };
    for (const arg of info.required) recipe[arg] = fillable[arg];
    const route = routeMeasure(p.meas, info.default_analysis, analyses ?? []);
    if (route === "skip") continue;
    if (route) Object.assign(recipe, route);
    items.push({ name: p.meas, recipe });
  }
  return { items };
}

/** name → value map over /measure results (errors and non-finite become null). */
export function measureValueMap(
  results: WaveMeasureResult[] | null,
): Record<string, number | null> {
  const out: Record<string, number | null> = {};
  for (const r of results ?? []) out[r.name] = r.value ?? null;
  return out;
}

/** A performance chip: a measured value joined (by name) to a project spec. */
export interface PerfChip {
  meas: string;
  label: string;
  unit: string;
  value: number | null;
  /** The matched target spec, when the applied project has one with this name. */
  target: number | null;
  goal: string | null;
  status: "ok" | "fail" | "neutral";
}

/**
 * Join measured values with the applied project's Tier-1 target specs by
 * (folded) name — `foldMeasName` strips a raw-trace `v(...)`/`i(...)` wrapper
 * then folds case/punctuation ("phase_margin" ⇄ "pm" stays apart; semantics
 * stay backend-owned). Specs are the only source of targets — no thresholds are
 * invented client-side; without a matching spec a chip is `neutral`.
 */
export function perfChips(
  catalog: MeasurementCatalogResponse | null,
  results: WaveMeasureResult[] | null,
  specs: TargetSpec[] | null,
): PerfChip[] {
  if (!results?.length) return [];
  const values = measureValueMap(results);
  const specByName = new Map<string, TargetSpec>();
  for (const s of specs ?? []) if (s.enable) specByName.set(foldMeasName(s.name), s);
  return PREFERRED_MEASURES.filter((p) => p.meas in values).map((p) => {
    const value = values[p.meas];
    const spec = specByName.get(foldMeasName(p.meas)) ?? null;
    let status: PerfChip["status"] = "neutral";
    if (spec && value != null) {
      const v = statusForGoal(spec.goal, value, spec.target, spec.tolerance ?? undefined);
      status = v === "pass" ? "ok" : v === "fail" ? "fail" : "neutral";
    }
    return {
      meas: p.meas,
      label: p.label,
      unit: p.unit,
      value,
      target: spec?.target ?? null,
      goal: spec?.goal ?? null,
      status,
    };
  });
}

/** One device row of the OP table (columns are data-driven, see groupScalars). */
export interface DeviceRow {
  dev: string;
  params: Record<string, number | null>;
}

export interface GroupedScalars {
  rows: DeviceRow[];
  /** Union of parameter names across rows, in first-seen order. */
  columns: string[];
  /** Scalars that didn't parse as device params (node voltages, currents…). */
  other: [string, number | null][];
}

// "@m.xdut.m1[gm]" / "@mn1[gds]"  → dev "m.xdut.m1" / "mn1", param "gm"/"gds"
// "M0:gm"                          → dev "M0", param "gm"
const DEV_BRACKET = /^@?([^[\]]+)\[([^[\]]+)\]$/;
const DEV_COLON = /^([^:]+):([^:]+)$/;

/**
 * Group the flat /scalars dict (keys like "@m.xdut.m1[gm]" or "M0:gm") into
 * per-device rows for the OP table. Non-device keys (node voltages, branch
 * currents) land in `other` and render as a plain name/value list.
 */
export function groupScalars(
  scalars: Record<string, number | null>,
): GroupedScalars {
  const byDev = new Map<string, Record<string, number | null>>();
  const columns: string[] = [];
  const other: [string, number | null][] = [];
  for (const [key, value] of Object.entries(scalars)) {
    const m = DEV_BRACKET.exec(key) ?? DEV_COLON.exec(key);
    if (!m) {
      other.push([key, value]);
      continue;
    }
    const [, dev, param] = m;
    if (!byDev.has(dev)) byDev.set(dev, {});
    byDev.get(dev)![param] = value;
    if (!columns.includes(param)) columns.push(param);
  }
  // Code-unit compare (not localeCompare): device names are identifiers, and the
  // order must be deterministic across locales.
  const rows = [...byDev.entries()]
    .map(([dev, params]) => ({ dev, params }))
    .sort((a, b) => (a.dev < b.dev ? -1 : a.dev > b.dev ? 1 : 0));
  return { rows, columns, other };
}

/** Parse a "method:max_points" downsample preset (see DOWNSAMPLE_OPTIONS). */
export function parseDownsample(preset: string): { method: string; max_points: number } {
  const [method, max] = preset.split(":");
  return { method: method || "minmax", max_points: Number(max) || 4000 };
}

/**
 * The marks the plot annotates (UGF marker, PM label, THD note) from REAL
 * measured values — the handoff's `derived`, sourced from POST /measure
 * results instead of curve math.
 */
export function derivedMarksFor(
  analysis: string | null,
  results: WaveMeasureResult[] | null,
): { ugf?: number | null; pm?: number | null; thd?: number | null } {
  if (!analysis) return {};
  const base = baseAnalysis(analysis);
  const v = measureValueMap(results);
  if (base === "ac" || base === "pac") return { ugf: v.ugf ?? null, pm: v.pm ?? null };
  if (base === "stb") return { ugf: v.ugf ?? null, pm: v.pm_loop ?? v.pm ?? null };
  if (base === "thd") return { thd: v.thd ?? null };
  return {};
}

/** Units of a named signal in a dataset analysis (SignalMeta lookup). */
export function unitsForSignal(
  a: WaveAnalysisMeta | undefined,
  name: string | undefined,
): string | null {
  if (!a || !name) return null;
  return a.signals.find((s) => s.name === name)?.units ?? null;
}

/** Compact dataset display name: last two path segments ("r42/tb_ac.raw"). */
export function datasetShortName(ds: WaveDatasetMeta): string {
  const parts = ds.path.split("/").filter(Boolean);
  return parts.slice(-2).join("/") || ds.path;
}
