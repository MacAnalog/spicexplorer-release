// Adapter: analog-db API shapes → the Reference Library view-model types.
//
// The FastAPI `library` routes return the analog-db-native contract (long PDK keys,
// `catalog@1` / `results@1` field names). The selectors were written against the
// design prototype's compact view types (`Circuit`, `MeasuredMap`, `Template` with
// short PDK keys + a flattened result). This module is the single seam that maps
// one to the other, so the (pure, tested) selector logic is unchanged when the data
// stops being a fixture and starts coming from the repo. Keep it pure + total.

import type {
  LibraryCatalog,
  LibraryCatalogCircuit,
  LibraryCircuitResult,
  LibraryClass,
  LibraryPdk,
  LibraryResults,
  LibrarySubcircuitTemplate,
  LibraryTemplatesResponse,
} from "@/types/api";
import type { Circuit, CircuitClass, MeasuredMap, MeasuredResult, PdkKey, Template } from "./types";

/** analog-db long PDK name → the UI's short display key. Unknown PDKs are dropped. */
const PDK_SHORT: Record<string, PdkKey> = {
  sky130: "sky130",
  "ihp-sg13g2": "ihp",
  gf180mcu: "gf180",
};

export function shortPdk(long: string): PdkKey | null {
  return PDK_SHORT[long] ?? null;
}

const PDK_LONG: Record<PdkKey, string> = { sky130: "sky130", ihp: "ihp-sg13g2", gf180: "gf180mcu" };

/** The UI's short PDK key → the analog-db-native long name (for the write path). */
export function longPdk(short: string): string {
  return PDK_LONG[short as PdkKey] ?? short;
}

/** Catalog `class` → the UI's `CircuitClass`; unknown classes fall back to amplifier. */
function asClass(klass: string): CircuitClass {
  return (["amplifier", "ldo", "pll", "adc"] as const).includes(klass as CircuitClass)
    ? (klass as CircuitClass)
    : "amplifier";
}

export function adaptCircuit(c: LibraryCatalogCircuit): Circuit {
  const p = c.provenance ?? {};
  const aliases = Array.isArray(p.aliases) ? p.aliases.join(", ") : "";
  return {
    id: c.id,
    name: c.display_name || c.id,
    klass: asClass(c.class),
    comp: c.compensation || "none",
    stages: c.stages ?? 0,
    pdks: c.pdks.map(shortPdk).filter((k): k is PdkKey => k !== null),
    analyses: [...c.analyses],
    source: (p.source as string) || "—",
    designer: (p.designer as string) || "—",
    license: (p.license as string) || "—",
    paper: (p.paper as string) || "—",
    aliases: aliases || "—",
    // the UI view type has no "measured" status; collapse anything non-draft to incomplete
    status: c.status === "draft" ? "draft" : "incomplete",
  };
}

/** Flatten one `results@1` record into the compact `MeasuredResult`. The flattened
 *  `measures` block uses the raw measure names (`inoise_total`); map to the UI keys. */
export function adaptResult(r: LibraryCircuitResult): MeasuredResult {
  const m = r.measures ?? {};
  const out: MeasuredResult = {};
  if (m.dcgain !== undefined) out.dcgain = m.dcgain;
  if (m.ugf !== undefined) out.ugf = m.ugf;
  if (m.pm !== undefined) out.pm = m.pm;
  if (m.i_supply !== undefined) out.i_supply = m.i_supply;
  if (m.inoise_total !== undefined) out.inoise = m.inoise_total;
  if (m.t_settle !== undefined) out.t_settle = m.t_settle;
  if (m.gain_cl !== undefined) out.gain_cl = m.gain_cl;
  if (m.bw_cl !== undefined) out.bw_cl = m.bw_cl;
  // LDO (regulation) measures
  if (m.vout_dc !== undefined) out.vout_dc = m.vout_dc;
  if (m.load_reg !== undefined) out.load_reg = m.load_reg;
  if (m.line_reg !== undefined) out.line_reg = m.line_reg;
  if (m.v_dropout !== undefined) out.v_dropout = m.v_dropout;
  if (m.psrr_vdd_db !== undefined) out.psrr_vdd_db = m.psrr_vdd_db;
  if (r.run_at) out.run = r.run_at.slice(0, 10); // ISO timestamp → YYYY-MM-DD
  // only carry the crosscheck when every field is numeric (the backend can null
  // individual sub-fields of a present dc_gain_db block), so the non-null type holds
  const s = r.symbolic;
  if (s && [s.sym, s.sim, s.err, s.tol].every((n) => typeof n === "number")) {
    out.symbolic = { sym: s.sym, sim: s.sim, err: s.err, tol: s.tol };
  }
  return out;
}

/** `{id: {pdk(long): result}}` → the UI `MeasuredMap` (`{id: {pdk(short): MeasuredResult}}`). */
export function adaptMeasured(results: LibraryResults["results"]): MeasuredMap {
  const out: MeasuredMap = {};
  for (const [id, perPdk] of Object.entries(results)) {
    const entry: Partial<Record<PdkKey, MeasuredResult>> = {};
    for (const [long, r] of Object.entries(perPdk)) {
      const short = shortPdk(long);
      if (short) entry[short] = adaptResult(r);
    }
    if (Object.keys(entry).length) out[id] = entry;
  }
  return out;
}

export function adaptTemplate(t: LibrarySubcircuitTemplate): Template {
  // the manifest carries no prose description; derive a short one from the repo fields
  const desc = [t.polarity, t.role, t.family].filter(Boolean).join(" · ");
  return {
    id: t.id,
    name: t.display_name || t.id,
    family: t.family,
    polarity: t.polarity ?? "",
    role: t.role ?? "",
    netlist: t.netlist ?? "",
    ports: Object.entries(t.ports ?? {}),
    desc,
    hasImage: Boolean(t.image),
  };
}

/** The fetched, adapted dataset the Library store holds and the selectors read. */
export interface LibraryData {
  circuits: Circuit[];
  measured: MeasuredMap;
  templates: Template[];
  templateFamilies: string[];
  /** Raw per-class registry (canonical metrics + analyses) — feeds the testbench catalog. */
  classes: LibraryClass[];
  classesById: Record<string, LibraryClass>;
  /** The DB's PDK registry: every bound PDK + the engine its committed marker routes to. */
  pdks: LibraryPdk[];
}

export function adaptLibraryData(
  catalog: LibraryCatalog,
  results: LibraryResults,
  templates: LibraryTemplatesResponse,
  classes: LibraryClass[],
  pdks: LibraryPdk[] = [],
): LibraryData {
  return {
    circuits: catalog.circuits.map(adaptCircuit),
    measured: adaptMeasured(results.results),
    templates: templates.templates.map(adaptTemplate),
    templateFamilies: templates.families,
    classes,
    classesById: Object.fromEntries(classes.map((c) => [c.class, c])),
    pdks,
  };
}

/** An empty dataset — the store's initial value before the first fetch resolves. */
export const EMPTY_LIBRARY_DATA: LibraryData = {
  circuits: [],
  measured: {},
  templates: [],
  templateFamilies: [],
  classes: [],
  classesById: {},
  pdks: [],
};
