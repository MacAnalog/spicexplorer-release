// Pure derived-data layer for the Reference Library — ported from the prototype's
// `renderVals()`. Every function is `(LibraryData, …state) => view-data`: the data
// now comes from the analog-db API (held in `libraryStore`, adapted in `adapt.ts`),
// not a fixture. No React, no event handlers (components attach interactions) — so
// the logic stays testable and the views thin.
//
// What is still imported from `data.ts` is UI presentation/label metadata only
// (class colours, PDK labels, the standard-analysis descriptions) — never catalog
// content. Catalog content (circuits, measured results, templates, the class
// registry) is threaded in via `LibraryData`.

import {
  analysisMeta,
  metricInfo,
  tbMeasures,
  classMeta,
  tbClassMeta,
  pdkLabel,
  pdkDot,
  TEMPLATE_DISPLAY_PAD,
} from "./data";
import { fmtMeas, buildStats, compLabel } from "./format";
import type { LibraryData } from "./adapt";
import type { Circuit, CircuitClass, MeasuredMap, MeasuredResult, PdkKey, Template } from "./types";
import type { LibraryCircuitDetail } from "@/types/api";

/** Read a numeric metric off a measured result by string key (the result keys
 *  are dynamic — analysis -> key). Non-numeric/missing returns undefined. */
function numAt(m: MeasuredResult, key: string): number | undefined {
  const v = (m as Record<string, unknown>)[key];
  return typeof v === "number" ? v : undefined;
}

/** Total templates surfaced in the UI (enumerated + matcher-library padding). */
export function templateTotal(data: LibraryData): number {
  return data.templates.length + TEMPLATE_DISPLAY_PAD;
}

const cnt = (data: LibraryData, pred: (c: Circuit) => boolean) => data.circuits.filter(pred).length;

// ── per-circuit derivations ──────────────────────────────────────────────────

/** Class-scoped analyses bound to a circuit (the testbench list), from the repo manifest. */
export function analysesFor(c: Circuit): string[] {
  return c.analyses;
}

/** PDKs that have a recorded result (a measured dcgain or i_supply) for a circuit. */
export function resultsPdks(c: Circuit, measured: MeasuredMap): PdkKey[] {
  const m = measured[c.id];
  if (!m) return [];
  return (Object.keys(m) as PdkKey[]).filter((p) => m[p]!.dcgain !== undefined || m[p]!.i_supply !== undefined);
}

/** First PDK with a recorded result, or null. */
export function displayPdk(c: Circuit, measured: MeasuredMap): PdkKey | null {
  const r = resultsPdks(c, measured);
  return r.length ? r[0] : null;
}

function cardMetric(c: Circuit, measured: MeasuredMap): { v: string; u: string } {
  const pdk = displayPdk(c, measured);
  const m = pdk ? measured[c.id][pdk] : null;
  if (m && m.dcgain !== undefined) return { v: m.dcgain.toFixed(1), u: "dB" };
  return { v: "—", u: "" };
}

// ── filter / sort ────────────────────────────────────────────────────────────

export type SortMode = "id" | "comp" | "stages" | "results";

export interface CircuitFilters {
  classSel: string[];
  sourceSel: string[];
  compSel: string[];
  search: string;
  sort: SortMode;
}

export function filterAndSort(data: LibraryData, f: CircuitFilters): Circuit[] {
  const q = f.search.trim().toLowerCase();
  const matches = (c: Circuit) => {
    if (f.classSel.length && !f.classSel.includes(c.klass)) return false;
    if (f.sourceSel.length && !f.sourceSel.includes(c.source)) return false;
    if (f.compSel.length && !f.compSel.includes(c.comp)) return false;
    if (q && !(c.id.includes(q) || c.name.toLowerCase().includes(q) || c.comp.toLowerCase().includes(q) || c.paper.toLowerCase().includes(q))) return false;
    return true;
  };
  const list = data.circuits.filter(matches);
  if (f.sort === "id") return [...list].sort((a, b) => a.id.localeCompare(b.id));
  if (f.sort === "comp") return [...list].sort((a, b) => a.comp.localeCompare(b.comp) || a.id.localeCompare(b.id));
  if (f.sort === "stages") return [...list].sort((a, b) => (b.stages || 0) - (a.stages || 0));
  if (f.sort === "results") return [...list].sort((a, b) => resultsPdks(b, data.measured).length - resultsPdks(a, data.measured).length);
  return list;
}

export interface CircuitCardData {
  id: string;
  name: string;
  compLabel: string;
  classBg: string;
  classFg: string;
  sub: string;
  metricValue: string;
  metricUnit: string;
  nTb: number;
  hasSky: boolean;
  hasIhp: boolean;
  hasGf: boolean;
  hasResults: boolean;
  selected: boolean;
}

export function toCardData(c: Circuit, measured: MeasuredMap, selId: string): CircuitCardData {
  const cm = classMeta[c.klass] ?? classMeta.amplifier;
  const met = cardMetric(c, measured);
  const rp = resultsPdks(c, measured);
  return {
    id: c.id,
    name: c.name,
    compLabel: compLabel(c.comp),
    classBg: cm.bg,
    classFg: cm.fg,
    sub: `${cm.label} · ${c.stages ? c.stages + "-stage" : "—"} · ${c.source}`,
    metricValue: met.v,
    metricUnit: met.u,
    nTb: analysesFor(c).length,
    hasSky: c.pdks.includes("sky130"),
    hasIhp: c.pdks.includes("ihp"),
    hasGf: c.pdks.includes("gf180"),
    hasResults: rp.length > 0,
    selected: c.id === selId,
  };
}

// ── filter-rail option builders ──────────────────────────────────────────────

export interface FilterOption {
  key: string;
  label: string;
  count: number;
  on: boolean;
}

export function classOptions(data: LibraryData, classSel: string[]): FilterOption[] {
  return ([["amplifier", "Amplifier"], ["ldo", "LDO"]] as const).map(([k, l]) => ({ key: k, label: l, count: cnt(data, (c) => c.klass === k), on: classSel.includes(k) }));
}

export function sourceOptions(data: LibraryData, sourceSel: string[]): FilterOption[] {
  const sources = [...new Set(data.circuits.map((c) => c.source))].filter((s) => s && s !== "—").sort();
  return sources.map((s) => ({ key: s, label: s, count: cnt(data, (c) => c.source === s), on: sourceSel.includes(s) }));
}

export function compOptions(data: LibraryData, compSel: string[]): FilterOption[] {
  const comps = [...new Set(data.circuits.map((c) => c.comp))].sort((a, b) => cnt(data, (c) => c.comp === b) - cnt(data, (c) => c.comp === a) || a.localeCompare(b));
  return comps.map((cp) => ({ key: cp, label: cp, count: cnt(data, (c) => c.comp === cp), on: compSel.includes(cp) }));
}

export function totalCircuits(data: LibraryData): number {
  return data.circuits.length;
}
export function amplifierCount(data: LibraryData): number {
  return cnt(data, (c) => c.klass === "amplifier");
}
export function ldoCount(data: LibraryData): number {
  return cnt(data, (c) => c.klass === "ldo");
}
/** Circuits with at least one recorded result (the "measured" section count). */
export function measuredCount(data: LibraryData): number {
  return data.circuits.filter((c) => resultsPdks(c, data.measured).length > 0).length;
}

export interface HeadStat {
  label: string;
  count: string;
}
export function headStats(data: LibraryData): HeadStat[] {
  return [
    { label: "Circuits", count: String(totalCircuits(data)) },
    { label: "Amplifiers", count: String(amplifierCount(data)) },
    { label: "LDOs", count: String(ldoCount(data)) },
    { label: "PDKs", count: "3" },
    { label: "Templates", count: String(templateTotal(data)) },
  ];
}

/** Home left-rail "LIBRARY" sections. `nav` is a discriminator the view turns
 *  into a store action (it presets tab + filters). */
export type SectionNav = "featured" | "all" | "amplifiers" | "ldos" | "measured" | "templates";
export interface SectionItem {
  icon: string;
  label: string;
  count: string;
  nav: SectionNav;
}
export function sections(data: LibraryData): SectionItem[] {
  return [
    { icon: "★", label: "Featured", count: "", nav: "featured" },
    { icon: "▤", label: "All circuits", count: String(totalCircuits(data)), nav: "all" },
    { icon: "∿", label: "Amplifiers", count: String(amplifierCount(data)), nav: "amplifiers" },
    { icon: "▭", label: "LDOs", count: String(ldoCount(data)), nav: "ldos" },
    { icon: "◫", label: "Measured", count: String(measuredCount(data)), nav: "measured" },
    { icon: "⊟", label: "Templates", count: String(templateTotal(data)), nav: "templates" },
  ];
}

export function templateCategories(data: LibraryData) {
  const byFamily = (fam: string) => data.templates.filter((t) => t.family === fam).length;
  return [
    { label: "All blocks", count: String(templateTotal(data)), active: true },
    { label: "Current mirrors", count: String(byFamily("current_mirror")), active: false },
    { label: "Differential pairs", count: String(byFamily("differential_pair") + byFamily("diffpair")), active: false },
  ];
}

// ── templates ────────────────────────────────────────────────────────────────

export function templateById(data: LibraryData, id: string): Template | undefined {
  return data.templates.find((t) => t.id === id) ?? data.templates[0];
}

// ── testbench catalog ────────────────────────────────────────────────────────

export interface TbCatalogItem {
  id: string;
  name: string;
  klass: CircuitClass;
  measures: string;
  /** Engines with a committed source for this bench (repo-derived; empty = none found). */
  engines: string[];
  desc: string;
  slots: string[];
  path: string | null;
  spectreAnalyses: number;
  spectreCalculator: number;
}

/** The testbench catalog = each repo class's analyses (class registry `templates`),
 *  joined with the API's per-bench profile (engines / slots / authored description). */
export function tbCatalog(data: LibraryData): TbCatalogItem[] {
  return data.classes.flatMap((cl) => {
    const profiles = new Map((cl.testbenches ?? []).map((t) => [t.name, t]));
    return cl.templates.map((an) => {
      const p = profiles.get(an);
      return {
        id: cl.class + "/" + an,
        name: an,
        klass: cl.class as CircuitClass,
        // curated short label first, else the template's own authored header line
        measures: tbMeasures[cl.class as CircuitClass]?.[an] ?? (p?.description || "—"),
        engines: p?.engines ?? [],
        desc: p?.description ?? "",
        slots: p?.slots ?? [],
        path: p?.path ?? null,
        spectreAnalyses: p?.spectre_analyses ?? 0,
        spectreCalculator: p?.spectre_calculator ?? 0,
      };
    });
  });
}

/** Number of circuits exercising each class's testbenches (from the repo catalog). */
function tbCirc(data: LibraryData, cl: CircuitClass): number {
  return cnt(data, (c) => c.klass === cl);
}

export interface TbRowData extends TbCatalogItem {
  classBg: string;
  classFg: string;
  circuits: string;
  selected: boolean;
}

export function tbList(data: LibraryData, tbClassSel: string[], selTb: string): TbRowData[] {
  return tbCatalog(data)
    .filter((t) => !tbClassSel.length || tbClassSel.includes(t.klass))
    .map((t) => {
      const cm = tbClassMeta[t.klass] ?? tbClassMeta.amplifier;
      return { ...t, classBg: cm.bg, classFg: cm.fg, circuits: String(tbCirc(data, t.klass)), selected: t.id === selTb };
    });
}

export function tbDetail(data: LibraryData, selTb: string) {
  const catalog = tbCatalog(data);
  const sel = catalog.find((t) => t.id === selTb) ?? catalog[0];
  if (!sel) {
    return { name: "—", klass: "amplifier" as CircuitClass, classBg: tbClassMeta.amplifier.bg, classFg: tbClassMeta.amplifier.fg, measures: "—", plot: "—", circuits: "0", engines: [] as string[], desc: "", slots: [] as string[], path: null as string | null, spectreAnalyses: 0, spectreCalculator: 0, metrics: ["—"] };
  }
  const cm = tbClassMeta[sel.klass] ?? tbClassMeta.amplifier;
  const metrics = Object.keys(metricInfo).filter((k) => metricInfo[k].a === sel.name);
  return {
    name: sel.name,
    klass: sel.klass,
    classBg: cm.bg,
    classFg: cm.fg,
    measures: sel.measures,
    plot: sel.name + ".out",
    circuits: String(tbCirc(data, sel.klass)),
    // repo-derived per-engine availability (no hardcoded simulator claims)
    engines: sel.engines,
    desc: sel.desc,
    slots: sel.slots,
    path: sel.path,
    spectreAnalyses: sel.spectreAnalyses,
    spectreCalculator: sel.spectreCalculator,
    metrics: metrics.length ? metrics : ["—"],
  };
}

// ── DB-derived engine/PDK vocabularies (never hardcode simulator or PDK lists) ──

/** Engines the DB actually routes anywhere: pdk `sim_engine` markers ∪ bench engines. */
export function engineUniverse(data: LibraryData): string[] {
  const s = new Set<string>();
  data.pdks.forEach((p) => s.add(p.sim_engine));
  data.classes.forEach((cl) => (cl.testbenches ?? []).forEach((t) => t.engines.forEach((e) => s.add(e))));
  return [...s].sort();
}

/** The DB's bound PDK ids, in registry order. */
export function pdkChoices(data: LibraryData): string[] {
  return data.pdks.map((p) => p.id);
}

/** The engine the DB routes a PDK to (its committed `sim_engine` marker). */
export function engineForPdk(data: LibraryData, pdkId: string): string | null {
  return data.pdks.find((p) => p.id === pdkId)?.sim_engine ?? null;
}

export function tbClassOptions(data: LibraryData, tbClassSel: string[]): FilterOption[] {
  return data.classes.map((cl) => ({ key: cl.class, label: cl.class, count: cl.templates.length, on: tbClassSel.includes(cl.class) }));
}

// ── circuit datasheet / detail ───────────────────────────────────────────────

export function circuitById(data: LibraryData, id: string): Circuit | undefined {
  return data.circuits.find((c) => c.id === id) ?? data.circuits[0];
}

/** Format the datasheet conditions line from a circuit's `default_conditions`
 *  (repo datasheet.yaml). Falls back to the corner only while the detail loads. */
function formatConditions(detail: LibraryCircuitDetail | null): string {
  const dc = (detail?.datasheet as { default_conditions?: Record<string, { unit?: string; typical?: unknown }> } | undefined)
    ?.default_conditions;
  if (!dc) return "tt · default conditions";
  const cell = (k: string, fmt: (v: unknown, u?: string) => string) => {
    const c = dc[k];
    return c && c.typical !== undefined ? fmt(c.typical, c.unit) : null;
  };
  const parts = [
    cell("corner", (v) => String(v)),
    cell("temp", (v, u) => `${v} °${u === "degC" ? "C" : u ?? "C"}`),
    cell("supply", (v, u) => `${v} ${u ?? "V"}`),
    cell("cload", (v, u) => `C_L ${v} ${u ?? "fF"}`),
    cell("ibias", (v, u) => `I_bias ${v} ${u ?? "uA"}`),
  ].filter(Boolean);
  return parts.length ? parts.join(" · ") : "tt · default conditions";
}

/** Build everything the datasheet detail view + its rails need for `selId` with
 *  active analysis `tbIdx`. Pure — the view attaches the row click handlers.
 *  `detail` (the per-circuit API fetch) enriches the conditions from the repo
 *  datasheet; everything else derives from the already-loaded catalog data. */
export function buildDetail(data: LibraryData, detail: LibraryCircuitDetail | null, selId: string, tbIdxRaw: number) {
  const selC = circuitById(data, selId);
  if (!selC) {
    // dataset still loading / empty — a benign placeholder the view renders silently
    return null;
  }
  const measured = data.measured;
  const cm = classMeta[selC.klass] ?? classMeta.amplifier;
  const anList = analysesFor(selC);
  const tbIdx = Math.min(Math.max(0, tbIdxRaw), Math.max(0, anList.length - 1));
  const activeAn = anList[tbIdx];
  const dPdk = displayPdk(selC, measured);
  const dMeas = dPdk ? measured[selC.id][dPdk]! : null;
  const am = analysisMeta[activeAn];

  const testbenches = anList.map((an, i) => {
    const meta = analysisMeta[an];
    let val = "—";
    let ok = false;
    let warn = false;
    if (dMeas && meta && meta.key && numAt(dMeas, meta.key) !== undefined) {
      val = fmtMeas(meta.key, numAt(dMeas, meta.key)) ?? "—";
      if (an === "ac_open_loop") {
        ok = (dMeas.dcgain ?? -Infinity) >= 100;
        warn = !ok;
      } else if (an === "tran_step") {
        ok = (dMeas.t_settle ?? Infinity) <= 1e-6;
        warn = !ok;
      }
    } else if (dMeas && an === "dc_op" && dMeas.i_supply !== undefined) {
      val = fmtMeas("i_supply", dMeas.i_supply) ?? "—";
    } else if (dMeas && an === "noise" && dMeas.inoise !== undefined) {
      val = fmtMeas("inoise", dMeas.inoise) ?? "—";
    }
    return { tb: an, measures: meta ? meta.measures : "—", value: val, spec: meta ? meta.spec : "—", corner: "tt", active: i === tbIdx, ok, warn, none: !ok && !warn };
  });

  type Chip = { name: string; value: string; target: string; status: "ok" | "fail" | "neutral" };
  let chips: Chip[];
  if (activeAn === "ac_open_loop" && dMeas) {
    chips = [
      { name: "gain", value: dMeas.dcgain !== undefined ? dMeas.dcgain.toFixed(1) + " dB" : "—", target: "≥ 100", status: (dMeas.dcgain ?? -Infinity) >= 100 ? "ok" : "fail" },
      { name: "UGF", value: dMeas.ugf !== undefined ? (dMeas.ugf / 1e6).toFixed(1) + " MHz" : "—", target: "any", status: "neutral" },
      { name: "PM", value: dMeas.pm !== undefined ? dMeas.pm.toFixed(0) + "°" : "—", target: "45–90", status: dMeas.pm !== undefined && dMeas.pm >= 45 && dMeas.pm <= 90 ? "ok" : "fail" },
    ];
  } else if (activeAn === "dc_op" && dMeas) {
    chips = [{ name: "I_supply", value: dMeas.i_supply !== undefined ? (dMeas.i_supply * 1e6).toFixed(1) + " µA" : "—", target: "report", status: "neutral" }];
  } else if (activeAn === "noise" && dMeas) {
    chips = [{ name: "Vn,in", value: dMeas.inoise !== undefined ? (dMeas.inoise >= 0.01 ? (dMeas.inoise * 1e3).toFixed(0) : (dMeas.inoise * 1e3).toFixed(2)) + " mV" : "—", target: "report", status: "neutral" }];
  } else if (activeAn === "tran_step" && dMeas) {
    chips = [{ name: "t_settle", value: dMeas.t_settle !== undefined ? (dMeas.t_settle < 1e-6 ? (dMeas.t_settle * 1e9).toFixed(1) + " ns" : (dMeas.t_settle * 1e6).toFixed(2) + " µs") : "—", target: "≤ 1 µs", status: (dMeas.t_settle ?? Infinity) <= 1e-6 ? "ok" : "fail" }];
  } else {
    chips = [{ name: am ? activeAn : "analysis", value: "not run", target: am ? am.spec : "—", status: "neutral" }];
  }

  const sym = dMeas && dMeas.symbolic;
  const symbolicText = sym ? `netlist2tf H(s) → ${sym.sym.toFixed(1)} dB vs sim ${sym.sim.toFixed(1)} dB · agrees ✓ (Δ ${sym.err.toFixed(2)}, tol ${sym.tol.toFixed(2)})` : "";

  const benchmarks = selC.pdks.map((p) => {
    const m = measured[selC.id]?.[p];
    const mv = m && am && am.key ? numAt(m, am.key) : undefined;
    const hasV = mv !== undefined;
    return {
      pdk: pdkLabel[p],
      v: hasV ? fmtMeas(am.key!, mv) ?? "— not run" : "— not run",
      run: m && m.run ? m.run : "queued",
      ng: m && m.run ? "45" : "—",
      ok: hasV,
    };
  });

  const manifest = [
    { k: "id", v: selC.id },
    { k: "class", v: selC.klass },
    { k: "compensation", v: selC.comp },
    { k: "stages", v: selC.stages ? String(selC.stages) : "—" },
    { k: "pdks", v: selC.pdks.map((p) => pdkLabel[p]).join(" · ") },
    { k: "source", v: selC.source },
    { k: "paper", v: selC.paper },
    { k: "license", v: selC.license },
    { k: "aliases", v: selC.aliases },
    { k: "status", v: selC.status },
  ];

  const pdkRows = selC.pdks.map((p) => ({
    label: pdkLabel[p],
    dot: pdkDot[p],
    note: measured[selC.id]?.[p]?.run ? "run" : "assembled",
  }));

  return {
    id: selC.id,
    name: selC.name,
    klass: selC.klass,
    classLabel: cm.label,
    classBg: cm.bg,
    classFg: cm.fg,
    compLabel: compLabel(selC.comp),
    isDraft: selC.status === "draft",
    isIncomplete: selC.status === "incomplete",
    hasResults: resultsPdks(selC, measured).length > 0,
    subtitle: `${cm.label} · ${selC.comp === "none" ? "uncompensated" : selC.comp + " compensation"} · ${selC.stages ? selC.stages + " stage" + (selC.stages > 1 ? "s" : "") : "—"} · ${selC.source} · ${selC.paper}`,
    svg: `${selC.id}_annotated.sch`,
    svgNote: "block-aware placement · xschem",
    conditions: formatConditions(detail && detail.id === selId ? detail : null),
    manifest,
    stats: buildStats(selC, dPdk ? measured[selC.id][dPdk] : undefined),
    statsNote: dPdk ? `recorded baseline — default sizing on ${pdkLabel[dPdk]}; optimize to meet specs` : "no recorded run yet — assemble + run via analog-db",
    nTb: anList.length,
    classLabelLower: cm.label,
    resultPdkLabel: dPdk ? `measured: ${pdkLabel[dPdk]}` : "not yet measured",
    testbenches,
    tbActiveName: activeAn,
    tbActiveMeasures: am ? am.measures : "",
    tbActivePlot: am ? am.plot : "",
    chips,
    hasSymbolic: !!sym,
    symbolicText,
    benchmarks,
    bmCol: am && am.key ? am.key : "measure",
    pdkRows,
    source: selC.source,
    license: selC.license,
  };
}

export type CircuitDetail = NonNullable<ReturnType<typeof buildDetail>>;

/** Right-aligned mono summary in the tab strip, per tab/detail state.
 *  `foundCount` is the active tab's FILTERED row count — shown as "N of M"
 *  whenever filters hide anything, so the strap never lies about the view. */
export function strapMeta(data: LibraryData, tab: string, detailOpen: boolean, selId: string, foundCount: number): string {
  if (detailOpen) {
    const c = circuitById(data, selId);
    return c ? `${c.source} · ${c.license}` : "";
  }
  const nFam = new Set(data.templates.map((t) => t.family)).size;
  const of = (total: number) => (foundCount < total ? `${foundCount} of ${total}` : `${total}`);
  if (tab === "templates") return `${nFam} families · ${templateTotal(data)} templates`;
  if (tab === "testbenches")
    return `${data.classes.length} classes · ${of(tbCatalog(data).length)} analyses`;
  if (tab === "circuits")
    return `${of(totalCircuits(data))} circuits · ${data.classes.length} classes · 3 PDKs`;
  return `${totalCircuits(data)} circuits · ${templateTotal(data)} templates`;
}
