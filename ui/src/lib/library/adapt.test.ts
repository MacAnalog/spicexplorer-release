import { describe, expect, it } from "vitest";

import type {
  LibraryCatalog,
  LibraryCatalogCircuit,
  LibraryCircuitResult,
  LibrarySubcircuitTemplate,
} from "@/types/api";
import {
  adaptCircuit,
  adaptLibraryData,
  adaptMeasured,
  adaptResult,
  adaptTemplate,
  shortPdk,
} from "./adapt";

// A faithful slice of the real analog-db API responses (amp_001_5t / telescopic), so the
// adapter is pinned against the actual contract, not invented shapes.
const FIVE_T: LibraryCatalogCircuit = {
  id: "amp_001_5t",
  class: "amplifier",
  display_name: "5-transistor OTA (single-stage)",
  compensation: "none",
  stages: 1,
  pdks: ["ihp-sg13g2", "sky130", "gf180mcu"],
  analyses: ["ac_open_loop", "dc_op"],
  status: "draft",
  provenance: {
    source: "analog-circuit-design",
    designer: "Harald Pretl",
    license: "Apache-2.0",
    paper: "JKU ihp-sg13g2 design textbook (Pretl)",
    aliases: ["ota-5t", "voltage-buffer-ota"],
  },
  schematic: { abstract: "circuits/amp_001_5t/abstract/schematic.svg" },
  raw: {},
};

const SKY_RESULT: LibraryCircuitResult = {
  corner: "tt",
  run_at: "2026-06-11T03:38:36+00:00",
  measures: {
    dcgain: 26.04454,
    ugf: 49270140.0,
    pm: 70.1067,
    i_supply: 2.406955e-5,
    inoise_total: 0.0008611845,
    t_settle: 1.0639e-8,
    gain_cl: 0.9094601,
    bw_cl: 44111750.0,
  },
  analyses: { ac_open_loop: { status: "ok", measures: { dcgain: 26.04454 } } },
  symbolic: null,
};

describe("shortPdk", () => {
  it("maps the long analog-db names to short UI keys", () => {
    expect(shortPdk("ihp-sg13g2")).toBe("ihp");
    expect(shortPdk("gf180mcu")).toBe("gf180");
    expect(shortPdk("sky130")).toBe("sky130");
  });
  it("drops unknown PDKs", () => {
    expect(shortPdk("unknown-pdk")).toBeNull();
  });
});

describe("adaptCircuit", () => {
  it("maps native catalog fields + flattens provenance", () => {
    const c = adaptCircuit(FIVE_T);
    expect(c.name).toBe("5-transistor OTA (single-stage)");
    expect(c.klass).toBe("amplifier");
    expect(c.comp).toBe("none");
    expect(c.stages).toBe(1);
    expect(c.pdks).toEqual(["ihp", "sky130", "gf180"]); // long → short, order preserved
    expect(c.analyses).toEqual(["ac_open_loop", "dc_op"]); // the manifest testbench list
    expect(c.designer).toBe("Harald Pretl");
    expect(c.aliases).toBe("ota-5t, voltage-buffer-ota");
    expect(c.status).toBe("draft");
  });

  it("supplies safe defaults for missing/null fields", () => {
    const c = adaptCircuit({
      ...FIVE_T,
      compensation: null,
      stages: null,
      provenance: {},
      pdks: ["sky130", "unknown-pdk"],
    });
    expect(c.comp).toBe("none");
    expect(c.stages).toBe(0);
    expect(c.source).toBe("—");
    expect(c.aliases).toBe("—");
    expect(c.pdks).toEqual(["sky130"]); // unknown PDK dropped
  });

  it("collapses a non-draft status to incomplete (the view type has no 'measured')", () => {
    expect(adaptCircuit({ ...FIVE_T, status: "measured" }).status).toBe("incomplete");
    expect(adaptCircuit({ ...FIVE_T, status: "incomplete" }).status).toBe("incomplete");
  });
});

describe("adaptResult", () => {
  it("flattens measures to the UI keys (inoise_total → inoise) and trims run_at", () => {
    const r = adaptResult(SKY_RESULT);
    expect(r.dcgain).toBeCloseTo(26.04454);
    expect(r.ugf).toBeCloseTo(49270140.0);
    expect(r.inoise).toBeCloseTo(0.0008611845); // inoise_total → inoise
    expect(r.run).toBe("2026-06-11");
    expect(r.symbolic).toBeUndefined();
  });

  it("carries the symbolic cross-check through when present", () => {
    const r = adaptResult({
      ...SKY_RESULT,
      symbolic: { sym: 52.19, sim: 52.81, err: 0.62, tol: 2.64, agrees: true },
    });
    expect(r.symbolic).toEqual({ sym: 52.19, sim: 52.81, err: 0.62, tol: 2.64 });
  });

  it("drops a symbolic block with a null sub-field (keeps the non-null type honest)", () => {
    const r = adaptResult({
      ...SKY_RESULT,
      // a present dc_gain_db crosscheck whose tolerance the backend couldn't fill
      symbolic: { sym: 52.19, sim: 52.81, err: 0.62, tol: null as unknown as number, agrees: true },
    });
    expect(r.symbolic).toBeUndefined();
  });

  it("maps the LDO regulation measures", () => {
    const r = adaptResult({
      ...SKY_RESULT,
      measures: { i_supply: 2.087656e-4, vout_dc: 1.205346, load_reg: 0.015569, line_reg: 0.001077, v_dropout: 0.284106, psrr_vdd_db: 59.16634 },
    });
    expect(r.vout_dc).toBeCloseTo(1.205346);
    expect(r.load_reg).toBeCloseTo(0.015569);
    expect(r.line_reg).toBeCloseTo(0.001077);
    expect(r.v_dropout).toBeCloseTo(0.284106);
    expect(r.psrr_vdd_db).toBeCloseTo(59.16634);
    expect(r.i_supply).toBeCloseTo(2.087656e-4);
  });
});

describe("adaptMeasured", () => {
  it("re-keys the bulk map to short PDK keys and skips empty circuits", () => {
    const m = adaptMeasured({
      "amp_001_5t": { "ihp-sg13g2": SKY_RESULT, sky130: SKY_RESULT },
      ghost: {}, // no recorded results → omitted
    });
    expect(Object.keys(m)).toEqual(["amp_001_5t"]);
    expect(Object.keys(m["amp_001_5t"])).toEqual(["ihp", "sky130"]);
    expect(m["amp_001_5t"].ihp!.dcgain).toBeCloseTo(26.04454);
  });
});

describe("adaptTemplate", () => {
  const BASE: LibrarySubcircuitTemplate = {
    id: "cm.nmos.simple",
    display_name: "Simple NMOS current mirror (2T)",
    family: "current_mirror",
    polarity: "nmos",
    role: "current_sink",
    class: "simple",
    netlist: "nmos_current_sink/simulation/basic_current_mirror.spice",
    ports: { supply: "VSS", ref_in: "iin", out: "iout" },
    image: "nmos_current_sink/basic_current_mirror.png",
  };

  it("maps the manifest row + turns the ports object into entry pairs", () => {
    const out = adaptTemplate(BASE);
    expect(out.name).toBe("Simple NMOS current mirror (2T)");
    expect(out.ports).toEqual([
      ["supply", "VSS"],
      ["ref_in", "iin"],
      ["out", "iout"],
    ]);
    expect(out.desc).toBe("nmos · current_sink · current_mirror");
  });

  it("flags whether a committed PNG render exists", () => {
    expect(adaptTemplate(BASE).hasImage).toBe(true);
    expect(adaptTemplate({ ...BASE, image: null }).hasImage).toBe(false);
  });
});

describe("adaptLibraryData", () => {
  it("assembles the dataset + indexes classes by id", () => {
    const catalog: LibraryCatalog = {
      schema: "spicexplorer/catalog@1",
      classes: { amplifier: ["amp_001_5t"] },
      circuits: [FIVE_T],
    };
    const data = adaptLibraryData(
      catalog,
      { results: { "amp_001_5t": { sky130: SKY_RESULT } } },
      { families: ["current_mirror"], templates: [] },
      [{ class: "amplifier", description: "OTAs", canonical_metrics: ["dc_gain_db"], templates: ["ac_open_loop"], testbenches: [{ name: "ac_open_loop", engines: ["ngspice", "spectre"], path: "_shared/classes/amplifier/testbench-templates/ac_open_loop.spice", description: "Open-loop AC gain/phase of an OTA.", slots: ["PDK_INCLUDE", "VDD"], spectre_analyses: 2, spectre_calculator: 3 }] }],
    );
    expect(data.circuits).toHaveLength(1);
    expect(data.measured["amp_001_5t"].sky130!.dcgain).toBeCloseTo(26.04454);
    expect(data.classesById.amplifier.canonical_metrics).toContain("dc_gain_db");
    expect(data.templateFamilies).toEqual(["current_mirror"]);
  });
});
