// Number/label formatting for the Reference Library. Ported from the prototype's
// `fmtMeas` / `buildStats`; keep the exact rounding and units (dB 1dp, Hz→MHz
// 1dp, current→µA, settling→ns/µs, noise→mV) — they're part of the spec.

import type { Circuit, MeasuredResult } from "./types";

export type StatTone = "default" | "ok" | "warn";

export interface StatCell {
  eyebrow: string;
  value: string;
  unit: string;
  tone: StatTone;
}

/** Format a measured value by its result key. Returns null for undefined/null. */
export function fmtMeas(key: string, v: number | undefined | null): string | null {
  if (v === undefined || v === null) return null;
  if (key === "dcgain") return v.toFixed(1) + " dB";
  if (key === "ugf" || key === "bw_cl") return (v / 1e6).toFixed(1) + " MHz";
  if (key === "pm") return v.toFixed(0) + "°";
  if (key === "i_supply") return (v * 1e6).toFixed(1) + " µA";
  if (key === "inoise") return v >= 0.01 ? (v * 1e3).toFixed(0) + " mV" : (v * 1e3).toFixed(2) + " mV";
  if (key === "t_settle") return v < 1e-6 ? (v * 1e9).toFixed(1) + " ns" : (v * 1e6).toFixed(2) + " µs";
  if (key === "gain_cl") return v.toFixed(3) + " V/V";
  return String(v);
}

/** The 6-cell datasheet `Stat` grid for a circuit, given its display-PDK result. */
export function buildStats(c: Circuit, m: MeasuredResult | undefined): StatCell[] {
  const has = !!m;
  if (c.klass === "amplifier") {
    const g = m && m.dcgain;
    return [
      { eyebrow: "DC gain", value: has && m!.dcgain !== undefined ? m!.dcgain.toFixed(1) : "—", unit: "dB", tone: g !== undefined && g >= 100 ? "ok" : g !== undefined ? "warn" : "default" },
      { eyebrow: "UGF", value: has && m!.ugf !== undefined ? (m!.ugf / 1e6).toFixed(1) : "—", unit: "MHz", tone: "default" },
      { eyebrow: "Phase margin", value: has && m!.pm !== undefined ? m!.pm.toFixed(0) : "—", unit: "°", tone: m && m.pm !== undefined && m.pm >= 45 && m.pm <= 90 ? "ok" : m && m.pm !== undefined ? "warn" : "default" },
      { eyebrow: "I_supply", value: has && m!.i_supply !== undefined ? (m!.i_supply * 1e6).toFixed(1) : "—", unit: "µA", tone: "default" },
      { eyebrow: "Noise (in)", value: has && m!.inoise !== undefined ? (m!.inoise >= 0.01 ? (m!.inoise * 1e3).toFixed(0) : (m!.inoise * 1e3).toFixed(2)) : "—", unit: "mV", tone: "default" },
      { eyebrow: "t_settle", value: has && m!.t_settle !== undefined ? (m!.t_settle < 1e-6 ? (m!.t_settle * 1e9).toFixed(1) : (m!.t_settle * 1e6).toFixed(2)) : "—", unit: has && m!.t_settle !== undefined && m!.t_settle < 1e-6 ? "ns" : "µs", tone: m && m.t_settle !== undefined && m.t_settle <= 1e-6 ? "ok" : m && m.t_settle !== undefined ? "warn" : "default" },
    ];
  }
  // LDO regulation grid — values are the recorded result's flattened measures.
  return [
    { eyebrow: "V_out", value: has && m!.vout_dc !== undefined ? m!.vout_dc.toFixed(3) : "—", unit: "V", tone: "default" },
    { eyebrow: "Load reg", value: has && m!.load_reg !== undefined ? (m!.load_reg * 1e3).toFixed(1) : "—", unit: "mV", tone: "default" },
    { eyebrow: "Line reg", value: has && m!.line_reg !== undefined ? (m!.line_reg * 1e3).toFixed(2) : "—", unit: "mV", tone: "default" },
    { eyebrow: "Dropout", value: has && m!.v_dropout !== undefined ? (m!.v_dropout * 1e3).toFixed(0) : "—", unit: "mV", tone: "default" },
    { eyebrow: "PSRR", value: has && m!.psrr_vdd_db !== undefined ? m!.psrr_vdd_db.toFixed(1) : "—", unit: "dB", tone: "default" },
    { eyebrow: "I_q", value: has && m!.i_supply !== undefined ? (m!.i_supply * 1e6).toFixed(1) : "—", unit: "µA", tone: "default" },
  ];
}

/** "none" compensation renders as "no-comp". */
export function compLabel(comp: string): string {
  return comp === "none" ? "no-comp" : comp;
}
