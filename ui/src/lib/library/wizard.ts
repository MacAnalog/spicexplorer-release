// Pure logic for the Register wizard — ported from the prototype's
// `wizardVals()`. Owns the per-kind step flow, the live YAML + catalog-entry
// generation, and the review/file-list summaries. No React, no handlers: the
// form + mutations live in `libraryWizardStore`; the overlay wires interactions.

import type { CircuitClass, IdFieldKey } from "./types";
import type { CreateCircuitRequest } from "@/types/api";
import { longPdk } from "./adapt";

export type WizKind = "circuit" | "template" | "testbench";

/** Placeholder port lists for a scaffolded draft, per class — the designer edits the real
 *  netlist afterward (the wizard doesn't collect ports). */
const DRAFT_PORTS: Record<CircuitClass, string[]> = {
  amplifier: ["vdd", "vout", "vinp", "vinn", "ibias", "vss"],
  ldo: ["vdd", "vout", "vfb", "vref", "ibias", "vss"],
  pll: ["vdd", "refclk", "clkout", "vss"],
  adc: ["vdd", "vinp", "vinn", "clk", "vss"],
};

/** Map the circuit-kind form to the `POST /api/library/circuits` payload (draft scaffold).
 *  PDK keys are converted back to the DB-native long names; aliases split to a list. */
export function circuitPayload(form: WizForm): CreateCircuitRequest {
  const stages = form.stages ? Number(form.stages) || undefined : undefined;
  const aliases = form.aliases
    ? form.aliases.split(/[,·]/).map((s) => s.trim()).filter(Boolean)
    : [];
  return {
    id: form.id,
    class: form.klass,
    display_name: form.name || form.id,
    compensation: form.comp || undefined,
    stages,
    ports: DRAFT_PORTS[form.klass] ?? ["vdd", "out", "in", "vss"],
    pdks: form.pdks.map(longPdk),
    analyses: [...new Set([...form.analyses, ...form.customAnalyses])],
    provenance: {
      source: form.source || "wizard",
      designer: form.designer || undefined,
      paper: form.paper || undefined,
      license: form.license || undefined,
      aliases,
    },
  };
}

/** The full register-wizard form model (one object, like the prototype). */
export interface WizForm {
  kind: WizKind;
  // circuit identity
  id: string;
  name: string;
  klass: CircuitClass;
  // class-driven identity fields (one pair per class)
  comp: string;
  stages: string;
  pass_device: string;
  vco_type: string;
  div_n: string;
  architecture: string;
  resolution: string;
  // provenance
  source: string;
  designer: string;
  paper: string;
  license: string;
  aliases: string;
  licenseOpen: boolean;
  schematicFile: string;
  // topology
  deviceCount: number;
  pdks: string[];
  corners: string[];
  netOrigin: "abstract" | "pdk";
  netPdk: string;
  netSim: string;
  detect: boolean;
  detectTemplates: string[];
  // analyses + datasheet
  analyses: string[];
  customAnalyses: string[];
  newTb: string;
  metricRows: { key: string; op: string; val: string }[];
  supply: string;
  temp: string;
  cload: string;
  vcm: string;
  ibias: string;
  // testbench
  tbId: string;
  tbTemplate: string;
  tbDesc: string;
  tbClass: CircuitClass;
  tbSimType: string;
  tbEnabled: boolean;
  tbFlags: string[];
  tbProduces: string[];
  tbProduceSearch: string;
  tbParamRows: [string, string][];
  // template
  tid: string;
  tname: string;
  tfamily: string;
  tpolarity: string;
  trole: string;
  tnetlist: string;
  matchSupply: boolean;
  tportRows: [string, string][];
}

/** Form keys that hold a string value (for the generic text setter). */
export type WizStringKey = {
  [K in keyof WizForm]: WizForm[K] extends string ? K : never;
}[keyof WizForm];

/** Form keys that hold a string[] (for the generic multi-select toggle). */
export type WizArrayKey = {
  [K in keyof WizForm]: WizForm[K] extends string[] ? K : never;
}[keyof WizForm];

/** Form keys that hold a boolean (for the generic switch setter). */
export type WizBoolKey = {
  [K in keyof WizForm]: WizForm[K] extends boolean ? K : never;
}[keyof WizForm];

export const INITIAL_WIZ_FORM: WizForm = {
  kind: "circuit",
  id: "amp_022_myteam_nmcf",
  name: "3-Stage OTA — NMCF (MyTeam)",
  klass: "amplifier",
  comp: "NMCF",
  stages: "3",
  pass_device: "PMOS",
  vco_type: "ring-3",
  div_n: "8",
  architecture: "SAR",
  resolution: "10",
  source: "spicexplorer",
  designer: "",
  paper: "",
  license: "BSD-3-Clause",
  aliases: "",
  licenseOpen: false,
  schematicFile: "schematic.sch",
  deviceCount: 14,
  pdks: ["sky130", "ihp"],
  corners: ["tt"],
  netOrigin: "abstract",
  netPdk: "ihp-sg13g2",
  netSim: "ngspice",
  detect: true,
  detectTemplates: ["current_mirror", "differential_pair"],
  analyses: ["ac_open_loop", "dc_op", "noise", "tran_step"],
  customAnalyses: [],
  newTb: "",
  metricRows: [
    { key: "dc_gain_db", op: "min", val: "100 dB" },
    { key: "ugf_hz", op: "none", val: "" },
    { key: "pm_deg", op: "min", val: "45 deg" },
    { key: "i_supply", op: "minimize", val: "" },
    { key: "t_settle", op: "max", val: "1 us" },
  ],
  supply: "1.8",
  temp: "27",
  cload: "10p",
  vcm: "0.3",
  ibias: "3u",
  tbId: "ac_open_loop",
  tbTemplate: "ac_open_loop",
  tbDesc: "Open-loop AC gain / phase",
  tbClass: "amplifier",
  tbSimType: "ac",
  tbEnabled: true,
  tbFlags: [],
  tbProduces: ["dc_gain_db", "ugf_hz", "pm_deg"],
  tbProduceSearch: "",
  tbParamRows: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FSTART", "1k"], ["FSTOP", "100MEG"], ["PPD", "101"]],
  tid: "cm.nmos.cascode",
  tname: "Cascode NMOS current mirror (4T)",
  tfamily: "current_mirror",
  tpolarity: "nmos",
  trole: "current_sink",
  tnetlist: "cascode_current_mirror.spice",
  matchSupply: true,
  tportRows: [["supply", "VSS"], ["ref_in", "iin"], ["out", "iout"]],
};

/** Default testbench param rows per sim type (rewritten when sim type changes). */
export const SIM_PARAM_TEMPLATES: Record<string, [string, string][]> = {
  ac: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FSTART", "1k"], ["FSTOP", "100MEG"], ["PPD", "101"]],
  dc: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"]],
  tran: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["VSTEP", "0.2"], ["VTOL", "2m"], ["TSTART", "1u"], ["TSTEP", "1n"], ["TSTOP", "5u"]],
  noise: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FSTART", "1k"], ["FSTOP", "100MEG"], ["PPD", "101"]],
  pss: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FUND", "1G"], ["HARMS", "10"], ["TSTAB", "10n"]],
  pac: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FUND", "1G"], ["FSTART", "1k"], ["FSTOP", "100MEG"], ["PPD", "51"]],
  pnoise: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FUND", "1G"], ["FSTART", "1k"], ["FSTOP", "100MEG"], ["MAXSIDEBANDS", "7"]],
  linearity: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FIN", "1MEG"], ["AMP", "0.1"], ["NFFT", "1024"]],
  pz: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"]],
  sp: [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"], ["FSTART", "1k"], ["FSTOP", "100MEG"], ["PPD", "51"], ["Z0", "50"]],
};

/** Default port roles per template family (rewritten when family changes). */
export function tplPortsFor(f: string): [string, string][] {
  if (f === "differential_pair") return [["supply", "VSS"], ["in_p", "vinp"], ["in_n", "vinn"], ["CM_tail", "CM_tail"], ["out_n", "drain_n"], ["out_p", "drain_p"]];
  if (f === "cascode") return [["supply", "VSS"], ["in", "drain_in"], ["out", "drain_out"], ["bias", "VBIAS"]];
  if (f === "custom") return [["supply", "VSS"], ["in", "in"], ["out", "out"]];
  return [["supply", "VSS"], ["ref_in", "iin"], ["out", "iout"]];
}

// ── flow definitions ─────────────────────────────────────────────────────────

type StepName = "Type" | "Identity" | "Provenance" | "Topology" | "Analyses" | "Datasheet" | "Ports" | "Parameters" | "Produces" | "Review";

const FLOWS: Record<WizKind, StepName[]> = {
  testbench: ["Type", "Identity", "Parameters", "Produces", "Review"],
  template: ["Type", "Identity", "Ports", "Review"],
  circuit: ["Type", "Identity", "Provenance", "Topology", "Analyses", "Datasheet", "Review"],
};

/** Number of steps in a kind's flow (for Next/Back clamping). */
export function flowLength(kind: WizKind): number {
  return FLOWS[kind].length;
}

const LABEL_MAP: Record<StepName, string> = { Type: "Register", Identity: "Identity", Provenance: "Provenance", Topology: "Topology", Analyses: "Analyses", Datasheet: "Datasheet", Ports: "Ports & netlist", Parameters: "Parameters", Produces: "Produces & flags", Review: "Review" };

function titleFor(s: StepName, kind: WizKind): string {
  const m: Record<StepName, string> = { Type: "What to register", Identity: kind === "template" ? "Template identity" : kind === "testbench" ? "Testbench identity" : "Identity & class", Provenance: "Provenance", Topology: "Abstract topology", Analyses: "Class analyses", Datasheet: "Datasheet specs", Ports: "Ports & netlist", Parameters: "Testbench parameters", Produces: "Produces & flags", Review: "Review & generate" };
  return m[s];
}

function hintFor(s: StepName, kind: WizKind): string {
  const m: Record<StepName, string> = {
    Type: "A circuit (a full DUT topology) or a functional template used by the subcircuit matcher.",
    Identity: kind === "template" ? "A stable id, family and polarity — the id tags every detected match." : "A unique id and class. Class drives the fields, analyses and metrics below.",
    Provenance: "Where the topology came from — license and citation travel with the circuit.",
    Topology: "Upload the PDK-neutral netlist. Block detection is optional and configurable.",
    Analyses: "Bind class-scoped testbenches; add or register your own.",
    Datasheet: "Add metrics from the registry and edit their target specs.",
    Ports: "Port roles and the matching netlist for the subgraph matcher.",
    Parameters: "Template parameter overrides — bias, load (C_L), common-mode and sweep ranges.",
    Produces: "Which datasheet metrics this analysis extracts, plus template feature flags.",
    Review: "Pick a source category, review the files, then register.",
  };
  return m[s];
}

const PDK_FULL = (p: string) => (p === "ihp" ? "ihp-sg13g2" : p === "gf180" ? "gf180mcu" : p);

export const OP_ORDER = ["min", "max", "exact", "minimize", "none"];
export const OP_LABEL: Record<string, string> = { min: "≥ min", max: "≤ max", exact: "= exact", minimize: "↓ minim", none: "— none" };

// ── static choice sets (no form dependency) ──────────────────────────────────

export const KIND_CHOICES: { kind: WizKind; label: string; desc: string; icon: string }[] = [
  { kind: "circuit", label: "Circuit", desc: "A full DUT topology — sized, scored and optimized.", icon: "◧" },
  { kind: "template", label: "Template", desc: "A functional sub-circuit for monomorphism / detection.", icon: "⊞" },
  { kind: "testbench", label: "Testbench", desc: "A class-scoped analysis with its params and outputs.", icon: "▷" },
];

export const SOURCE_CHOICES = ["AnalogGym", "CORA", "spicexplorer", "analog-circuit-design", "custom"];
export const LICENSE_CHOICES = ["Apache-2.0", "BSD-3-Clause", "MIT", "CC-BY-4.0", "PolyForm-NC-1.0.0", "proprietary"];
// (PDK + simulator choices are NOT hardcoded here — the wizard derives them from the
// DB registry via `selectors.pdkChoices` / `engineUniverse`; see GET /api/library/pdks.)
export const TB_SIM_TYPES = ["ac", "dc", "tran", "noise", "pss", "pac", "pnoise", "linearity", "pz", "sp"];
export const TB_FLAGS = ["bias_wrap", "differential", "ac_couple"];

export const ORIGIN_CHOICES: { value: "abstract" | "pdk"; label: string }[] = [
  { value: "abstract", label: "Abstract · PDK-neutral" },
  { value: "pdk", label: "PDK-specific deck" },
];

/** [family key, label, note] — template families offered to block detection. */
export const DETECT_FAMILIES: [string, string, string][] = [
  ["current_mirror", "Current mirrors", "16 templates"],
  ["differential_pair", "Differential pairs", "2 templates"],
  ["cascode", "Cascodes", "misc"],
];

/** [family key, label] for the template-identity family picker. */
export const TPL_FAMILIES: [string, string][] = [
  ["current_mirror", "current mirror"],
  ["differential_pair", "differential pair"],
  ["cascode", "cascode"],
  ["custom", "custom"],
];

export const TPL_POLARITIES: { value: string; label: string }[] = [
  { value: "nmos", label: "nmos" },
  { value: "pmos", label: "pmos" },
  { value: "na", label: "N/A" },
];

/** Detected blocks shown in the topology preview when detection is on. */
export const WIZ_BLOCKS = [
  { fam: "differential_pair", tid: "dp.nmos.simple", dev: "M1–M2" },
  { fam: "current_mirror", tid: "cm.pmos.simple", dev: "M3–M4" },
  { fam: "current_mirror", tid: "cm.nmos.simple", dev: "M5–M6" },
];

export interface PreviewLine {
  n: string;
  text: string;
  comment: boolean;
}

function toLines(src: string): PreviewLine[] {
  return src.split("\n").map((t, i) => ({ n: String(i + 1), text: t, comment: t.trim().indexOf("#") === 0 }));
}

export interface WizStep {
  n: string;
  label: string;
  active: boolean;
  done: boolean;
  todo: boolean;
}

/** Everything the overlay needs to render for a given form + step — the pure
 *  half of the prototype's `wizardVals` (flow, titles, YAML/catalog, review). */
export function buildWizard(form: WizForm, rawStep: number, idFields: [IdFieldKey, string, string][]) {
  const { kind } = form;
  const flow = FLOWS[kind];
  const step = Math.min(rawStep, flow.length - 1);
  const cur = flow[step];

  const steps: WizStep[] = flow.map((n, i) => ({ n: String(i + 1), label: LABEL_MAP[n], active: i === step, done: i < step, todo: i > step }));
  const at = (n: StepName) => cur === n;

  // ── YAML + catalog entry ───────────────────────────────────────────────────
  let yamlTitle: string;
  let yaml: string;
  let catTitle: string;
  let catText: string;
  if (kind === "testbench") {
    yamlTitle = "analysis.yaml";
    const pstr = form.tbParamRows.map((p) => "  " + p[0] + ": " + p[1]).join("\n");
    yaml = `# circuits/<id>/analyses/${form.tbId}.yaml\nschema: spicexplorer/analysis@1\nid: ${form.tbId}\ntemplate: ${form.tbTemplate}\ndescription: "${form.tbDesc}"\nenabled: ${form.tbEnabled}\nparams:\n${pstr}\nflags: [${form.tbFlags.join(", ")}]\nproduces: [${form.tbProduces.join(", ")}]`;
    catTitle = "binding";
    catText = `analog-db analysis binding\n  class   ${form.tbClass}\n  sim     ${form.tbSimType}\n  reused by every ${form.tbClass} circuit`;
  } else if (kind === "template") {
    yamlTitle = "manifest.yaml";
    const portsInline = "{" + form.tportRows.map((p) => p[0] + ": " + p[1]).join(", ") + "}";
    yaml = `# templates/${form.tfamily}/manifest.yaml\n- id: ${form.tid}\n  display_name: "${form.tname}"\n  family: ${form.tfamily}\n  polarity: ${form.tpolarity}\n  role: ${form.trole}\n  netlist: ${form.tnetlist}\n  match_supply: ${form.matchSupply}\n  ports: ${portsInline}`;
    catTitle = "matcher registration";
    catText = `spicexplorer_circuitgraph.match\n  + template  ${form.tid}\n    family    ${form.tfamily}\n    polarity  ${form.tpolarity}\n  matched on type + polarity + pin wiring`;
  } else {
    yamlTitle = "circuit.yaml";
    const extra = idFields.map(([k]) => `${k}: ${form[k]}`).join("\n");
    yaml = `# circuits/${form.id}/circuit.yaml\nschema: spicexplorer/circuit@1\nid: ${form.id}\ndisplay_name: "${form.name}"\nclass: ${form.klass}\n${extra}\norigin: ${form.netOrigin === "pdk" ? "{pdk: " + form.netPdk + ", simulator: " + form.netSim + "}" : "abstract (PDK-neutral)"}\npdks: [${form.pdks.map(PDK_FULL).join(", ")}]\nprovenance:\n  source: ${form.source}\n  license: ${form.license}\nanalyses: [${form.analyses.join(", ")}]`;
    catTitle = "catalog.json entry";
    catText = `{\n  "id": "${form.id}",\n  "class": "${form.klass}",\n  "pdks": ${JSON.stringify(form.pdks.map(PDK_FULL))},\n  "analyses": ${JSON.stringify(form.analyses)},\n  "status": "incomplete"\n}`;
  }

  // ── review summary + file list ─────────────────────────────────────────────
  const reviewRaw: [string, string][] =
    kind === "testbench"
      ? [["kind", "testbench"], ["id", form.tbId], ["template", form.tbTemplate], ["class", form.tbClass], ["sim", form.tbSimType], ["params", String(form.tbParamRows.length)], ["produces", String(form.tbProduces.length)]]
      : kind === "template"
        ? [["kind", "template"], ["id", form.tid], ["family", form.tfamily], ["polarity", form.tpolarity], ["role", form.trole], ["source", form.source]]
        : [["kind", "circuit"], ["id", form.id], ["class", form.klass], ["origin", form.netOrigin === "pdk" ? form.netSim + " · " + form.netPdk : "abstract"], ["analyses", String(form.analyses.length)], ["metrics", String(form.metricRows.length)], ["PDKs", form.pdks.map(PDK_FULL).join(" · ")], ["detect", form.detect ? "on" : "off"], ["source", form.source]];

  const fileList =
    kind === "testbench"
      ? ["analyses/" + form.tbId + ".yaml  (binding)", "(gen) raw deck per PDK × corner", "(gen) catalog.json  analyses[]"]
      : kind === "template"
        ? [`templates/${form.tfamily}/manifest.yaml  (entry)`, `templates/${form.tfamily}/.../${form.tnetlist}`, "(gen) re-index matcher library"]
        : ["circuit.yaml", "datasheet.yaml", "abstract/netlist.spice", `analyses/*.yaml  (${form.analyses.length})`, `pdk/<pdk>/...  (${form.pdks.length})`, "(gen) raw/ decks + catalog.json"];

  return {
    flow,
    step,
    cur,
    steps,
    title: titleFor(cur, kind),
    hint: hintFor(cur, kind),
    progress: `Step ${step + 1} of ${flow.length}`,
    canBack: step > 0,
    isLast: step === flow.length - 1,
    // step visibility
    show: {
      type: at("Type"),
      circIdentity: at("Identity") && kind === "circuit",
      tplIdentity: at("Identity") && kind === "template",
      tbIdentity: at("Identity") && kind === "testbench",
      provenance: at("Provenance"),
      topology: at("Topology"),
      analyses: at("Analyses"),
      datasheet: at("Datasheet"),
      tplPorts: at("Ports"),
      tbParams: at("Parameters"),
      tbProduces: at("Produces"),
      review: at("Review"),
    },
    yamlTitle,
    yamlLines: toLines(yaml),
    catTitle,
    catLines: toLines(catText),
    review: reviewRaw.map(([k, v]) => ({ k, v })),
    fileList,
  };
}

export type WizardDerived = ReturnType<typeof buildWizard>;
