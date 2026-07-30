// Types for the Reference Library / analog-db catalog browser.
//
// These mirror the in-memory data shapes embedded in the design prototype
// (`SpiceXplorer Library.dc.html`). In production they become the contract for
// the analog-db catalog API (catalog.json, recorded results, templates, the
// per-class testbench registry) — see the handoff README "Data" section. For
// now everything is served from the fixtures in `data.ts`.

/** Circuit class. The catalog ships amplifiers + LDOs; pll/adc exist only in
 *  the per-class registry (`classReg`) for the register wizard. */
export type CircuitClass = "amplifier" | "ldo" | "pll" | "adc";

/** Short PDK keys used throughout the catalog; `pdkLabel` maps them to display
 *  names (ihp -> ihp-sg13g2, gf180 -> gf180mcu). */
export type PdkKey = "sky130" | "ihp" | "gf180";

export type CircuitStatus = "draft" | "incomplete" | "measured";

export interface Circuit {
  id: string;
  name: string;
  klass: CircuitClass;
  /** Frequency-compensation scheme, or "none" (rendered as "no-comp"). */
  comp: string;
  stages: number;
  pdks: PdkKey[];
  /** Class-scoped analyses bound to the circuit (the testbench list), from the manifest. */
  analyses: string[];
  source: string;
  designer: string;
  license: string;
  paper: string;
  aliases: string;
  status: Exclude<CircuitStatus, "measured">;
}

/** One recorded SPICE result for a circuit on one PDK (corner tt). All metric
 *  fields are optional — only a few circuits have full numbers. */
export interface MeasuredResult {
  // amplifier measures
  dcgain?: number;
  ugf?: number;
  pm?: number;
  i_supply?: number;
  inoise?: number;
  t_settle?: number;
  gain_cl?: number;
  bw_cl?: number;
  // LDO measures (regulation)
  vout_dc?: number;
  load_reg?: number;
  line_reg?: number;
  v_dropout?: number;
  psrr_vdd_db?: number;
  run?: string;
  /** Symbolic (netlist2tf) cross-check, present only on circuits that have it. */
  symbolic?: { sym: number; sim: number; err: number; tol: number };
}

/** circuit id -> pdk key -> recorded result. */
export type MeasuredMap = Record<string, Partial<Record<PdkKey, MeasuredResult>>>;

/** A functional sub-circuit template (current mirror, diff pair, …). */
export interface Template {
  id: string;
  name: string;
  family: string;
  polarity: string;
  role: string;
  netlist: string;
  ports: [string, string][];
  desc: string;
  /** Whether a committed PNG render exists (fetch via `libraryTemplateImageUrl(id)`). */
  hasImage: boolean;
}

/** Class-specific identity field keys (the wizard Identity step writes these
 *  onto the form; all exist on `WizForm`). */
export type IdFieldKey =
  | "comp"
  | "stages"
  | "pass_device"
  | "vco_type"
  | "div_n"
  | "architecture"
  | "resolution";

/** Per-class registry: identity fields, available + default analyses, available
 *  + default datasheet metrics. Drives the register wizard and the testbench
 *  catalog. */
export interface ClassRegEntry {
  /** [key, label, placeholder] identity fields shown on the wizard Identity step. */
  id: [IdFieldKey, string, string][];
  /** All class-scoped analyses. */
  an: string[];
  /** Default analyses bound when a circuit of this class is registered. */
  defAn: string[];
  /** All datasheet metrics available for this class. */
  metrics: string[];
  /** Default metric rows. */
  defM: string[];
}

/** Metric registry entry: description, owning analysis, default spec string. */
export interface MetricInfo {
  d: string;
  a: string;
  s: string;
}

/** Default target spec for a metric (operator + value) used by the wizard. */
export interface MetricDefSpec {
  op: string;
  v: string;
}

/** Analysis metadata: what it measures, the measured-result key it maps to (or
 *  null), its headline spec, and the plot name. */
export interface AnalysisMeta {
  measures: string;
  key: string | null;
  spec: string;
  plot: string;
}

/** A "design with this circuit" tool shown in the datasheet right rail. */
export interface LibraryTool {
  icon: string;
  label: string;
  desc: string;
}
