// Reference Library — UI presentation + authoring metadata ONLY.
//
// The catalog CONTENT (circuits, measured results, templates, the per-class metric
// registry) is no longer here — it is loaded from the repo via the analog-db API
// (`/api/library/*`, see `lib/api.ts` + `adapt.ts` + `libraryStore`). What remains
// is strictly non-content:
//   • presentation: class/PDK colours + display labels, the datasheet tool list;
//   • standard-analysis reference labels (`analysisMeta` / `metricInfo` / `tbMeasures`)
//     — descriptions of the *standard* testbenches/metrics, used as display labels
//     next to the live values (not per-circuit catalog data);
//   • the Register-wizard AUTHORING config (`classReg` / `metricDefSpec`) — defaults
//     for *creating* a new circuit, including the speculative pll/adc classes that
//     don't exist in the repo yet. The repo-backed classes (amplifier/ldo) get their
//     real metric/analysis vocabularies from `/api/library/classes` at runtime.

import { ACCENT } from "@/config/colors";
import type {
  ClassRegEntry,
  MetricInfo,
  MetricDefSpec,
  AnalysisMeta,
  LibraryTool,
  CircuitClass,
  PdkKey,
} from "./types";

export const metricInfo: Record<string, MetricInfo> = {
  dc_gain_db: { d: "DC open-loop gain", a: "ac_open_loop", s: "≥ 100 dB" },
  gbw_hz: { d: "Gain-bandwidth", a: "ac_open_loop", s: "≥ 100 MHz" },
  ugf_hz: { d: "Unity-gain freq", a: "ac_open_loop", s: "any" },
  pm_deg: { d: "Phase margin", a: "ac_open_loop", s: "45–90°" },
  gm_deg: { d: "Gain margin", a: "ac_open_loop", s: "≥ 10 dB" },
  cmrr_db: { d: "CMRR", a: "ac_open_loop", s: "≥ 80 dB" },
  psrr_vdd_db: { d: "PSRR (Vdd)", a: "psrr", s: "≥ 60 dB" },
  slew_rate: { d: "Slew rate", a: "tran_step", s: "≥ 10 V/µs" },
  t_settle: { d: "Settling time", a: "tran_step", s: "≤ 1 µs" },
  i_supply: { d: "Supply current", a: "dc_op", s: "minimize" },
  vn_in: { d: "Input noise", a: "noise", s: "minimize" },
  vos: { d: "Input offset", a: "dc_op", s: "≤ 5 mV" },
  area_um2: { d: "Active area", a: "layout", s: "minimize" },
  v_out: { d: "Output voltage", a: "dc_op", s: "target 1.2 V" },
  load_reg: { d: "Load regulation", a: "load_regulation", s: "minimize" },
  line_reg: { d: "Line regulation", a: "line_regulation", s: "minimize" },
  v_dropout: { d: "Dropout voltage", a: "dropout", s: "≤ 200 mV" },
  i_q: { d: "Quiescent current", a: "dc_op", s: "minimize" },
  zout_peak_db: { d: "Zout peaking", a: "loop_stability", s: "minimize" },
  v_undershoot: { d: "LS undershoot", a: "tran_load_step", s: "≤ 100 mV" },
  t_transient: { d: "Recovery time", a: "tran_load_step", s: "≤ 2 µs" },
  lock_time_s: { d: "Lock time", a: "lock_transient", s: "≤ 10 µs" },
  jitter_rms_s: { d: "RMS jitter", a: "jitter_tran", s: "≤ 2 ps" },
  pn_dbc_1mhz: { d: "Phase noise @1MHz", a: "phase_noise", s: "≤ −100 dBc/Hz" },
  ref_spur_dbc: { d: "Reference spur", a: "spur_fft", s: "≤ −60 dBc" },
  kvco_hz_v: { d: "VCO gain Kvco", a: "kvco_dc", s: "tuning" },
  loop_bw_hz: { d: "Loop bandwidth", a: "loop_ac", s: "tuning" },
  enob_bits: { d: "ENOB", a: "dynamic_fft", s: "≥ 9 bits" },
  sndr_db: { d: "SNDR", a: "dynamic_fft", s: "report" },
  sfdr_db: { d: "SFDR", a: "sfdr_fft", s: "≥ 65 dB" },
  dnl_lsb: { d: "DNL", a: "static_dnl_inl", s: "≤ 1 LSB" },
  inl_lsb: { d: "INL", a: "static_dnl_inl", s: "≤ 1 LSB" },
  power_w: { d: "Power", a: "power_dc", s: "minimize" },
};

export const metricDefSpec: Record<string, MetricDefSpec> = {
  dc_gain_db: { op: "min", v: "100 dB" }, gbw_hz: { op: "min", v: "100 MHz" }, ugf_hz: { op: "none", v: "" }, pm_deg: { op: "min", v: "45 deg" }, gm_deg: { op: "min", v: "10 dB" }, cmrr_db: { op: "min", v: "80 dB" }, psrr_vdd_db: { op: "min", v: "60 dB" }, slew_rate: { op: "min", v: "10 V/us" }, t_settle: { op: "max", v: "1 us" }, i_supply: { op: "minimize", v: "" }, vn_in: { op: "minimize", v: "" }, vos: { op: "max", v: "5 mV" }, area_um2: { op: "minimize", v: "" }, v_out: { op: "exact", v: "1.2 V" }, load_reg: { op: "minimize", v: "" }, line_reg: { op: "minimize", v: "" }, v_dropout: { op: "max", v: "200 mV" }, i_q: { op: "minimize", v: "" }, zout_peak_db: { op: "minimize", v: "" }, v_undershoot: { op: "max", v: "100 mV" }, t_transient: { op: "max", v: "2 us" }, lock_time_s: { op: "max", v: "10 us" }, jitter_rms_s: { op: "max", v: "2 ps" }, pn_dbc_1mhz: { op: "max", v: "-100 dBc/Hz" }, ref_spur_dbc: { op: "max", v: "-60 dBc" }, kvco_hz_v: { op: "none", v: "" }, loop_bw_hz: { op: "none", v: "" }, enob_bits: { op: "min", v: "9 bits" }, sndr_db: { op: "none", v: "" }, sfdr_db: { op: "min", v: "65 dB" }, dnl_lsb: { op: "max", v: "1 LSB" }, inl_lsb: { op: "max", v: "1 LSB" }, power_w: { op: "minimize", v: "" },
};

/** Register-wizard authoring config. amplifier/ldo `an`/`metrics` are mirrored from
 *  the repo at runtime (`/api/library/classes`); the identity fields, defaults, and
 *  the speculative pll/adc classes are wizard scaffolding (no repo source yet). */
export const classReg: Record<CircuitClass, ClassRegEntry> = {
  amplifier: { id: [["comp", "Compensation", "NMCF"], ["stages", "Stages", "3"]], an: ["ac_open_loop", "ac_open_loop_biaswrap", "ac_closed_loop", "dc_op", "dc_sweep", "noise", "tran_step", "linearity"], defAn: ["ac_open_loop", "dc_op", "noise", "tran_step"], metrics: ["dc_gain_db", "gbw_hz", "ugf_hz", "pm_deg", "gm_deg", "cmrr_db", "psrr_vdd_db", "slew_rate", "t_settle", "i_supply", "vn_in", "vos", "area_um2"], defM: ["dc_gain_db", "ugf_hz", "pm_deg", "i_supply", "t_settle"] },
  ldo: { id: [["pass_device", "Pass device", "PMOS"], ["comp", "Compensation", "Miller"]], an: ["dc_op", "load_regulation", "line_regulation", "dropout", "psrr", "tran_load_step", "loop_stability"], defAn: ["dc_op", "load_regulation", "line_regulation", "psrr"], metrics: ["v_out", "load_reg", "line_reg", "v_dropout", "i_q", "psrr_vdd_db", "zout_peak_db", "v_undershoot", "t_transient"], defM: ["v_out", "load_reg", "v_dropout", "psrr_vdd_db", "i_q"] },
  pll: { id: [["vco_type", "VCO type", "ring-3"], ["div_n", "Divider N", "8"]], an: ["lock_transient", "phase_noise", "jitter_tran", "spur_fft", "kvco_dc", "loop_ac"], defAn: ["lock_transient", "jitter_tran", "phase_noise"], metrics: ["lock_time_s", "jitter_rms_s", "pn_dbc_1mhz", "ref_spur_dbc", "kvco_hz_v", "loop_bw_hz", "i_supply", "area_um2"], defM: ["lock_time_s", "jitter_rms_s", "pn_dbc_1mhz", "ref_spur_dbc"] },
  adc: { id: [["architecture", "Architecture", "SAR"], ["resolution", "Resolution (bits)", "10"]], an: ["static_dnl_inl", "dynamic_fft", "sfdr_fft", "power_dc", "inbw_ac"], defAn: ["static_dnl_inl", "dynamic_fft", "power_dc"], metrics: ["enob_bits", "sndr_db", "sfdr_db", "dnl_lsb", "inl_lsb", "power_w", "area_um2"], defM: ["enob_bits", "sfdr_db", "dnl_lsb", "inl_lsb"] },
};

/** Display labels for the standard analyses (measures prose · result key · spec · plot). */
export const analysisMeta: Record<string, AnalysisMeta> = {
  ac_open_loop: { measures: "DC gain · UGF · phase margin", key: "dcgain", spec: "gain ≥ 100 dB", plot: "ac_open_loop.bode" },
  ac_closed_loop: { measures: "Closed-loop gain · −3 dB BW", key: "gain_cl", spec: "unity buffer", plot: "ac_closed_loop.bode" },
  dc_op: { measures: "Operating point · supply current", key: "i_supply", spec: "report", plot: "dc_op.table" },
  noise: { measures: "Input-referred noise (integ.)", key: "inoise", spec: "report", plot: "noise_psd.ac" },
  tran_step: { measures: "Slew rate · 1% settling", key: "t_settle", spec: "t_settle ≤ 1 µs", plot: "tran_step.tr" },
  linearity: { measures: "THD / HD3 sweep", key: null, spec: "—", plot: "linearity.sweep" },
  load_regulation: { measures: "ΔV_out over load sweep", key: null, spec: "load_reg report", plot: "load_reg.dc" },
  line_regulation: { measures: "ΔV_out over supply sweep", key: null, spec: "line_reg report", plot: "line_reg.dc" },
  psrr: { measures: "PSRR vs supply", key: null, spec: "≥ 50 dB", plot: "psrr.ac" },
  dropout: { measures: "Dropout voltage", key: null, spec: "V_dropout", plot: "dropout.dc" },
  tran_load_step: { measures: "Undershoot · recovery", key: null, spec: "report", plot: "load_step.tr" },
  loop_stability: { measures: "Closed-loop Zout peaking · PM", key: null, spec: "PM ≥ 60°", plot: "loop_gain.bode" },
};

/** Number of matcher-library blocks beyond the enumerated templates (display padding). */
export const TEMPLATE_DISPLAY_PAD = 7;

/** Display labels for what each class's standard testbenches measure. */
export const tbMeasures: Record<CircuitClass, Record<string, string>> = {
  amplifier: { ac_open_loop: "DC gain · UGF · phase margin", ac_open_loop_biaswrap: "open-loop gain in closed-loop bias", ac_closed_loop: "closed-loop gain · −3 dB BW", dc_op: "operating point · I_supply", dc_sweep: "DC transfer · output swing", noise: "input-referred noise", tran_step: "slew rate · settling", linearity: "THD / HD3 sweep" },
  ldo: { dc_op: "V_out · I_q", load_regulation: "ΔV_out over load", line_regulation: "ΔV_out over V_in", dropout: "dropout voltage", psrr: "PSRR vs frequency", tran_load_step: "undershoot · recovery", loop_stability: "phase margin · Z_out" },
  pll: { lock_transient: "lock time", phase_noise: "phase noise vs offset", jitter_tran: "RMS / pp jitter", spur_fft: "reference spur", kvco_dc: "VCO gain Kvco", loop_ac: "loop bandwidth" },
  adc: { static_dnl_inl: "DNL / INL", dynamic_fft: "SNDR · ENOB", sfdr_fft: "SFDR", power_dc: "total power", inbw_ac: "input bandwidth" },
};

/** "Design with this circuit" tools shown in the datasheet right rail. */
export const tools: LibraryTool[] = [
  { icon: "⊟", label: "Size · gm/ID", desc: "gmid-extract LUT sizing" },
  { icon: "◎", label: "Score shaping", desc: "target specs + penalties" },
  { icon: "⟳", label: "Optimize", desc: "live SPICE optimization" },
  { icon: "ƒ", label: "Transfer fn", desc: "symbolic H(s) cross-check" },
  { icon: "⊞", label: "Detect blocks", desc: "circuitgraph annotation" },
];

// ── Static presentation maps ─────────────────────────────────────────────────

export const classMeta: Record<string, { bg: string; fg: string; label: string }> = {
  amplifier: { bg: ACCENT.primarySoft, fg: ACCENT.primary, label: "amplifier" },
  ldo: { bg: ACCENT.secondarySoft, fg: ACCENT.secondary, label: "LDO" },
};

/** Per-class chip palette for the testbench catalog (amplifier/ldo/pll/adc). */
export const tbClassMeta: Record<string, { bg: string; fg: string }> = {
  amplifier: { bg: ACCENT.primarySoft, fg: ACCENT.primary },
  ldo: { bg: ACCENT.secondarySoft, fg: ACCENT.secondary },
  pll: { bg: ACCENT.tertiarySoft, fg: ACCENT.tertiary },
  adc: { bg: ACCENT.violetSoft, fg: ACCENT.violet },
};

export const pdkLabel: Record<PdkKey, string> = { sky130: "sky130", ihp: "ihp-sg13g2", gf180: "gf180mcu" };
export const pdkDot: Record<PdkKey, string> = { sky130: ACCENT.secondary, ihp: ACCENT.amber, gf180: ACCENT.primary };

/** Per-PDK chip palette (the catalog's three open PDKs). */
export const pdkChipMeta: Record<PdkKey, { bg: string; fg: string }> = {
  sky130: { bg: ACCENT.secondarySoft, fg: ACCENT.secondary },
  ihp: { bg: ACCENT.amberSoft, fg: ACCENT.amber },
  gf180: { bg: ACCENT.primarySoft, fg: ACCENT.primary },
};

/** Per-engine chip palette + source-button label. Keys are the API's engine ids —
 *  WHICH engines exist comes from the DB (`selectors.engineUniverse` / a bench's
 *  `engines`); this map only styles/labels the known ones. */
export const engineMeta: Record<string, { bg: string; fg: string; srcLabel: string }> = {
  ngspice: { bg: ACCENT.primarySoft, fg: ACCENT.primary, srcLabel: "ngspice source" },
  spectre: { bg: ACCENT.secondarySoft, fg: ACCENT.secondary, srcLabel: "spectre · SKILL" },
};
export const engineMetaFallback = { bg: "#f4f4f5", fg: "#71717a", srcLabel: "source" };
