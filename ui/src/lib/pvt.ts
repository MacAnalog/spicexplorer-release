// Small presentation helpers for the PVT corner system (Phase 1).
import type { PVTCornerDef } from "@/types/api";

/** Compact one-line summary of a corner's environment, e.g. "125°C · VDD 1.62V". */
export function cornerSummary(c: PVTCornerDef): string {
  const t = `${c.temp}°C`;
  const sup = c.supplies.map((s) => `${s.node} ${s.value}V`).join(", ");
  return sup ? `${t} · ${sup}` : t;
}

/**
 * Process model-include summary, e.g. "cornerMOSlv.lib:mos_ss, cornerRES.lib:res_wcs".
 * An include with no section (a plain `.include <file>`, which gf180mcu corner
 * bundles start with) prints as the bare file name: "design.ngspice, sm141064.ngspice:typical".
 * The API sends `section: null` for it; a missing or empty section means the same.
 */
export function cornerIncludes(c: PVTCornerDef): string {
  return c.model_includes.map((m) => (m.section ? `${m.lib_file}:${m.section}` : m.lib_file)).join(", ");
}

/** A dropdown-friendly label: "ss_125C_1V62 — 125°C · VDD 1.62V". */
export function cornerOptionLabel(c: PVTCornerDef): string {
  return `${c.name} — ${cornerSummary(c)}${c.enabled ? "" : " (disabled)"}`;
}
