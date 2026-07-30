// Pure sweep-mode derivations (PVT corners / Monte Carlo) for the Analyze
// viewer. Everything works off REAL backend shapes: corner membership comes
// from run-artifact naming (`run_<n>_<tb>__<corner>/…`), metrics from POST
// /measure results, pass/fail only from applied-project target specs — no
// thresholds are invented client-side (the perfChips rule). The handoff's
// `?group=pvt` / `/mc` routes don't exist yet; these selectors implement the
// same contract over N per-corner datasets opened via POST /open_run.
import type {
  MeasurementCatalogResponse,
  TargetSpec,
  WaveRunArtifact,
} from "@/types/api";
import { statusForGoal } from "@/lib/utils";
import { ACCENT } from "@/config/colors";

/** Sweep presentation mode for the active dataset. */
export type SweepMode = "single" | "pvt" | "mc";

// ── corner discovery ─────────────────────────────────────────────────────────

/** `…/sim/run_3_tb_ac__ss_125c/deck.raw` → "ss_125c" (null when un-suffixed). */
export function cornerFromPath(path: string): string | null {
  const dir = path.split("/").slice(0, -1).pop() ?? "";
  const m = /__([A-Za-z0-9][A-Za-z0-9_.-]*)$/.exec(dir);
  return m ? m[1] : null;
}

/** `…/sim/run_3_tb_ac__ss/x.raw` → "tb_ac" — the testbench-identifying segment
 *  of a sweep artifact's folder (several testbenches can emit the same analysis
 *  kind, so corner grouping must pin the bench). Works on a folder name too. */
export function tbMatchFromPath(path: string): string | null {
  const dir = path.split("/").filter(Boolean).pop() ?? "";
  const fromDir = /^run_\d+_(.+?)(?:__|$)/.exec(dir);
  if (fromDir) return fromDir[1];
  const parent = path.split("/").filter(Boolean).slice(0, -1).pop() ?? "";
  const fromParent = /^run_\d+_(.+?)(?:__|$)/.exec(parent);
  return fromParent ? fromParent[1] : null;
}

/** Whether a corner name reads as the nominal/typical one. */
export function isNominalCorner(name: string): boolean {
  return /^(tt|typ|nom)/i.test(name);
}

/**
 * Dataset ids that read as sweep residue on a fresh page load: corner-suffixed
 * artifacts appearing in groups of ≥2 for the same run+testbench (a PVT/MC
 * sweep's per-corner opens, server-registered across sessions). These start
 * hidden from the tree — the sweep rail is their surface. A single corner raw
 * someone opened deliberately stays visible.
 */
export function sweepResidueIds(
  datasets: { dataset_id: string; path: string }[],
): string[] {
  const groups = new Map<string, string[]>();
  for (const d of datasets) {
    if (!cornerFromPath(d.path)) continue;
    const key = `${d.path.split("/sim/")[0]}::${tbMatchFromPath(d.path) ?? ""}`;
    groups.set(key, [...(groups.get(key) ?? []), d.dataset_id]);
  }
  return [...groups.values()].filter((g) => g.length >= 2).flat();
}

/** Corner names present in a run's artifacts (raw kinds only), nominal first. */
export function cornersInArtifacts(artifacts: WaveRunArtifact[]): string[] {
  const seen = new Set<string>();
  for (const a of artifacts) {
    if (a.type !== "ngspice_raw" && a.type !== "spectre_raw_dir") continue;
    const c = cornerFromPath(a.path);
    if (c) seen.add(c);
  }
  return [...seen].sort(
    (a, b) => Number(isNominalCorner(b)) - Number(isNominalCorner(a)) || a.localeCompare(b),
  );
}

/** Corner swatch palette (nominal is always indigo; the handoff's corner set). */
const CORNER_COLORS = [
  ACCENT.tertiary,
  ACCENT.secondary,
  ACCENT.violet,
  "#0d9488",
  "#d97706",
  "#2563eb",
  "#9333ea",
] as const;

export function cornerColor(name: string, index: number): string {
  if (isNominalCorner(name)) return ACCENT.primary;
  return CORNER_COLORS[index % CORNER_COLORS.length];
}

// ── headline metric (what a sweep is ranked by) ──────────────────────────────

/**
 * The measure a sweep mode ranks corners/samples by, per base analysis. Purely
 * presentational choice of WHICH Tier-1 measure to headline; the measure itself
 * must exist in the backend catalog to be used. `worse` says which direction is
 * the bad tail when no project spec pins a goal.
 */
export interface HeadlineMetric {
  meas: string;
  label: string;
  unit: string;
  worse: "low" | "high";
}

const HEADLINES: Record<string, HeadlineMetric[]> = {
  ac: [
    { meas: "pm", label: "Phase margin", unit: "°", worse: "low" },
    { meas: "ugf", label: "UGF", unit: "Hz", worse: "low" },
  ],
  stb: [
    { meas: "pm_loop", label: "Phase margin", unit: "°", worse: "low" },
    { meas: "pm", label: "Phase margin", unit: "°", worse: "low" },
  ],
  dc: [{ meas: "dcgain", label: "DC gain", unit: "dB", worse: "low" }],
  noise: [
    { meas: "inoise_total", label: "Input noise", unit: "V", worse: "high" },
    { meas: "onoise_total", label: "Output noise", unit: "V", worse: "high" },
  ],
  noise_spectrum: [
    { meas: "inoise_total", label: "Input noise", unit: "V", worse: "high" },
    { meas: "onoise_total", label: "Output noise", unit: "V", worse: "high" },
  ],
};

/** First headline metric the backend catalog can actually measure (out-arg only). */
export function headlineFor(
  baseAnalysis: string,
  catalog: MeasurementCatalogResponse | null,
): HeadlineMetric | null {
  for (const h of HEADLINES[baseAnalysis] ?? []) {
    const info = catalog?.measurements[h.meas];
    if (info && info.required.every((arg) => arg === "out")) return h;
  }
  return null;
}

/**
 * Normalize a spec/measure name for joins: strip a raw-trace `v(...)`/`i(...)`
 * wrapper, then fold case/punctuation. The optimizer spec convention names the
 * RAW vector (`v(inoise_total)` — exact-name lookup in the deck), while the
 * viewer's measures name the bare signal (`inoise_total`); without the strip the
 * Vn chip renders neutral instead of being judged against its spec. Semantic
 * aliasing ("phase_margin" ⇄ "pm") stays backend-owned — only spelling folds.
 */
export function foldMeasName(n: string): string {
  const m = /^\s*[iv]\(([^()]+)\)\s*$/i.exec(n);
  return (m ? m[1] : n).toLowerCase().replace(/[^a-z0-9]/g, "");
}

/** The applied project's target spec matching a measure name, if any. */
export function specForMeas(specs: TargetSpec[] | null, meas: string): TargetSpec | null {
  return specs?.find((s) => s.enable && foldMeasName(s.name) === foldMeasName(meas)) ?? null;
}

// ── PVT stats ────────────────────────────────────────────────────────────────

export interface CornerResult {
  key: string;
  name: string;
  color: string;
  nominal: boolean;
  enabled: boolean;
  metric: number | null;
}

/** Join sweep members with their measured metric + the user's corner toggles. */
export function cornerResults(
  members: { key: string; name: string; color: string; nominal: boolean }[],
  metrics: Record<string, number | null>,
  enabled: Record<string, boolean>,
): CornerResult[] {
  return members.map((m) => ({
    key: m.key,
    name: m.name,
    color: m.color,
    nominal: m.nominal,
    enabled: enabled[m.key] ?? true,
    metric: metrics[m.key] ?? null,
  }));
}

export interface PvtStats {
  worstKey: string | null;
  /** Corners meeting the spec — null when no project spec exists to judge by. */
  pass: number | null;
  total: number;
  /** Half the metric spread across enabled corners (±). */
  spread: number | null;
}

/** Worst-corner + pass/spread stats over the enabled corners' measured metric. */
export function pvtStats(
  corners: CornerResult[],
  headline: HeadlineMetric | null,
  spec: TargetSpec | null,
): PvtStats {
  const en = corners.filter((c) => c.enabled && c.metric != null);
  if (!en.length || !headline) return { worstKey: null, pass: null, total: 0, spread: null };
  const worse = spec ? (spec.goal === "minimize" ? "high" : "low") : headline.worse;
  let worst = en[0];
  for (const c of en) {
    if (worse === "low" ? c.metric! < worst.metric! : c.metric! > worst.metric!) worst = c;
  }
  const vals = en.map((c) => c.metric!);
  const spread = (Math.max(...vals) - Math.min(...vals)) / 2;
  let pass: number | null = null;
  if (spec) {
    pass = en.filter(
      (c) =>
        statusForGoal(spec.goal, c.metric!, spec.target, spec.tolerance ?? undefined) === "pass",
    ).length;
  }
  return { worstKey: worst.key, pass, total: en.length, spread };
}

// ── Monte Carlo stats ────────────────────────────────────────────────────────

/** `…/run_1_tb_ac__mc17/…` or `…/mc_017/…` reads as an MC sample artifact. */
export function isMcCorner(name: string): boolean {
  return /^mc[_-]?\d+$/i.test(name);
}

export interface McStats {
  n: number;
  mean: number;
  sigma: number;
  worst: number;
  /** Fraction meeting spec — null without a project spec. */
  yield: number | null;
  cpk: number | null;
}

export function mcStats(
  values: number[],
  headline: HeadlineMetric | null,
  spec: TargetSpec | null,
): McStats | null {
  if (!values.length) return null;
  const n = values.length;
  const mean = values.reduce((a, b) => a + b, 0) / n;
  const sigma = Math.sqrt(values.reduce((a, b) => a + (b - mean) * (b - mean), 0) / n);
  const worse = spec ? (spec.goal === "minimize" ? "high" : "low") : (headline?.worse ?? "low");
  const worst = worse === "low" ? Math.min(...values) : Math.max(...values);
  let yield_: number | null = null;
  let cpk: number | null = null;
  if (spec) {
    const pass = values.filter(
      (v) => statusForGoal(spec.goal, v, spec.target, spec.tolerance ?? undefined) === "pass",
    ).length;
    yield_ = pass / n;
    const dist = spec.goal === "minimize" ? spec.target - mean : mean - spec.target;
    cpk = dist / (3 * (sigma || 1));
  }
  return { n, mean, sigma, worst, yield: yield_, cpk };
}

/** Mean/sd curves across equal-length sample curves (null on a ragged set). */
export function meanSdCurves(samples: number[][]): { mean: number[]; sd: number[] } | null {
  const n = samples.length;
  if (!n) return null;
  const len = samples[0].length;
  if (samples.some((s) => s.length !== len)) return null;
  const mean = new Array<number>(len).fill(0);
  const m2 = new Array<number>(len).fill(0);
  for (const s of samples) {
    for (let i = 0; i < len; i++) {
      mean[i] += s[i];
      m2[i] += s[i] * s[i];
    }
  }
  for (let i = 0; i < len; i++) {
    mean[i] /= n;
    m2[i] = Math.sqrt(Math.max(0, m2[i] / n - mean[i] * mean[i]));
  }
  return { mean, sd: m2 };
}
