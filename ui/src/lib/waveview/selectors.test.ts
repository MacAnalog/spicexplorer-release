import { describe, expect, it } from "vitest";
import type { WaveAnalysisMeta, WaveDatasetMeta } from "@/types/api";
import {
  analysisLabel,
  baseAnalysis,
  buildMeasureItems,
  defaultSignals,
  datasetShortName,
  groupScalars,
  guessOutSignal,
  isDbNativeSignal,
  measureValueMap,
  orderedAnalyses,
  parseDownsample,
  perfChips,
  plotStyleFor,
  plottableSignals,
} from "./selectors";

const sig = (name: string, n = 128) => ({
  name,
  units: null,
  complex: false,
  n_points: n,
});

const an = (
  analysis: string,
  sweep: string | null,
  signals: string[],
): WaveAnalysisMeta => ({
  analysis,
  native_name: analysis,
  sweep,
  n_points: 128,
  signals: signals.map((s) => sig(s)),
  n_scalars: 0,
});

const ds = (analyses: WaveAnalysisMeta[], path = "/work/runs/r42/sim/tb_ac.raw"): WaveDatasetMeta => ({
  dataset_id: "d1",
  path,
  engine: "ngspice",
  analyses,
  log_path: null,
  warnings: [],
});

describe("orderedAnalyses", () => {
  it("orders by the presentation order with unknowns appended alphabetically", () => {
    const d = ds([an("zz_custom", null, []), an("op", null, []), an("ac", "frequency", []), an("tran", "time", [])]);
    expect(orderedAnalyses(d).map((a) => a.analysis)).toEqual(["tran", "ac", "op", "zz_custom"]);
  });
  it("groups a merged dataset's suffixed keys next to their base", () => {
    const d = ds([an("op", null, []), an("ac#2", "frequency", []), an("tran", "time", []), an("ac", "frequency", [])]);
    expect(orderedAnalyses(d).map((a) => a.analysis)).toEqual(["tran", "ac", "ac#2", "op"]);
  });
});

describe("baseAnalysis / analysisLabel / plotStyleFor (merged-dataset suffixes)", () => {
  it("strips the #n suffix to the engine-neutral key", () => {
    expect(baseAnalysis("ac")).toBe("ac");
    expect(baseAnalysis("ac#2")).toBe("ac");
    expect(baseAnalysis("noise#3")).toBe("noise");
  });
  it("labels a suffixed analysis with its ordinal", () => {
    expect(analysisLabel("ac#2")).toBe(`${analysisLabel("ac")} #2`);
  });
  it("keeps the base key's plot style (a second AC bench is still a dual Bode)", () => {
    expect(plotStyleFor("ac#2")).toEqual(plotStyleFor("ac"));
    expect(plotStyleFor("ac#2").dual).toBe(true);
  });
  it("falls back to the default style for unknown keys and null", () => {
    expect(plotStyleFor(null)).toEqual(plotStyleFor("zz_custom"));
  });
});

describe("plottableSignals / defaultSignals", () => {
  const a = an("ac", "frequency", ["frequency", "v(vout)", "v(vin)", "v(n1)", "v(n2)", "v(n3)"]);
  it("excludes the sweep vector", () => {
    expect(plottableSignals(a)).not.toContain("frequency");
  });
  it("prefers output-looking signals and caps the selection", () => {
    const sel = defaultSignals(a, 3);
    expect(sel[0]).toBe("v(vout)");
    expect(sel).toHaveLength(3);
  });
  it("prefers a deck-computed dB curve over the residual output (rejection bench)", () => {
    // the cmrr bench raw carries both v_out (the residual) and the deck's
    // purpose-built +CMRR(f) — the dual cap of 1 must pick the curve
    const cmrr = an("ac#2", "frequency", ["frequency", "v_out", "cmrr_db_curve"]);
    expect(defaultSignals(cmrr, 1)).toEqual(["cmrr_db_curve"]);
  });
});

describe("isDbNativeSignal", () => {
  it("matches the deck _db_curve convention only", () => {
    expect(isDbNativeSignal("cmrr_db_curve")).toBe(true);
    expect(isDbNativeSignal("PSRR_DB_CURVE")).toBe(true);
    expect(isDbNativeSignal("v_out")).toBe(false);
    expect(isDbNativeSignal("db_curve")).toBe(false);
    expect(isDbNativeSignal("cmrr_db")).toBe(false);
  });
});

describe("guessOutSignal", () => {
  it("prefers an output-looking signal from the AC analysis", () => {
    const d = ds([
      an("tran", "time", ["time", "v(step_out)"]),
      an("ac", "frequency", ["frequency", "v(n1)", "v(vout)"]),
    ]);
    expect(guessOutSignal(d)).toBe("v(vout)");
  });
  it("falls back to the first plottable signal when nothing looks like an output", () => {
    const d = ds([an("ac", "frequency", ["frequency", "v(n1)", "v(n2)"])]);
    expect(guessOutSignal(d)).toBe("v(n1)");
  });
  it("returns null for an empty dataset", () => {
    expect(guessOutSignal(ds([]))).toBeNull();
  });
});

describe("buildMeasureItems", () => {
  const catalog = {
    measurements: {
      pm: { kind: "ac", required: ["out"], default_analysis: "ac" },
      ugf: { kind: "ac", required: ["out"], default_analysis: "ac" },
      thd: { kind: "tran", required: ["out", "f0"], default_analysis: "tran" },
    },
  };
  it("keeps only catalog-listed measures whose required args are fillable", () => {
    const req = buildMeasureItems(catalog, "v(vout)");
    const names = req.items.map((i) => i.name);
    expect(names).toContain("pm");
    expect(names).toContain("ugf");
    // thd needs f0 which the UI cannot fill → excluded, not sent-and-errored
    expect(names).not.toContain("thd");
    expect(req.items.find((i) => i.name === "pm")?.recipe).toEqual({ meas: "pm", out: "v(vout)" });
  });
  it("is empty without a catalog or an out signal", () => {
    expect(buildMeasureItems(null, "v(vout)").items).toEqual([]);
    expect(buildMeasureItems(catalog, null).items).toEqual([]);
  });
});

describe("buildMeasureItems — merged multi-bench routing", () => {
  const catalog = {
    measurements: {
      pm: { kind: "ac", required: ["out"], default_analysis: "ac" },
      dcgain: { kind: "ac", required: ["out"], default_analysis: "ac" },
      cmrr_db: { kind: "ac", required: ["out"], default_analysis: "ac" },
      psrr_vdd_db: { kind: "ac", required: ["out"], default_analysis: "ac" },
      inoise_total: { kind: "noise", required: ["out"], default_analysis: "noise" },
    },
  };
  // A merged sweep run: the FIRST ac member is the PSRR bench (the observed
  // failure — unpinned measures read −29.6 dB "DC gain" off the residual).
  const sweptAn = (key: string, member: string, signals: string[]): WaveAnalysisMeta => ({
    ...an(key, "frequency", signals),
    native_name: `AC Analysis · sim/${member}`,
  });
  const analyses = [
    sweptAn("ac", "run_1_tb_psrr__mc1", ["frequency", "out"]),
    sweptAn("ac#2", "run_1_tb_cmrr__mc1", ["frequency", "out"]),
    sweptAn("ac#3", "run_1_tb_ac__mc1", ["frequency", "out"]),
    {
      ...an("noise_spectrum", "frequency", ["frequency", "inoise_spectrum", "onoise_spectrum"]),
      native_name: "Noise Spectral Density Curves · sim/run_1_tb_noise__mc1",
    },
    {
      ...an("noise", null, ["v(inoise_total)"]),
      native_name: "Integrated Noise · sim/run_1_tb_noise__mc1",
    },
  ];
  const recipeOf = (name: string) =>
    buildMeasureItems(catalog, "v(out)", analyses).items.find((i) => i.name === name)?.recipe;

  it("pins generic ac measures to the non-rejection (loop-gain) bench", () => {
    expect(recipeOf("pm")?.analysis).toBe("ac#3");
    expect(recipeOf("dcgain")?.analysis).toBe("ac#3");
  });
  it("pins cmrr/psrr to their own benches", () => {
    expect(recipeOf("cmrr_db")?.analysis).toBe("ac#2");
    expect(recipeOf("psrr_vdd_db")?.analysis).toBe("ac");
  });
  it("routes noise totals to the density analysis + spectrum signal", () => {
    expect(recipeOf("inoise_total")).toEqual({
      meas: "inoise_total",
      out: "inoise_spectrum",
      analysis: "noise_spectrum",
    });
  });
  it("skips a rejection measure when benches are known but the bench is absent", () => {
    const noCmrr = analyses.filter((a) => a.analysis !== "ac#2");
    const names = buildMeasureItems(catalog, "v(out)", noCmrr).items.map((i) => i.name);
    expect(names).not.toContain("cmrr_db");
    expect(names).toContain("psrr_vdd_db");
  });
  it("leaves recipes unpinned for a single-bench dataset (legacy behavior)", () => {
    const single = [an("ac", "frequency", ["frequency", "out"])];
    expect(buildMeasureItems(catalog, "v(out)", single).items.find((i) => i.name === "pm")?.recipe)
      .toEqual({ meas: "pm", out: "v(out)" });
  });
});

describe("perfChips", () => {
  const catalog = {
    measurements: {
      pm: { kind: "ac", required: ["out"], default_analysis: "ac" },
      ugf: { kind: "ac", required: ["out"], default_analysis: "ac" },
    },
  };
  const spec = {
    name: "pm",
    testbench: "tb_ac",
    goal: "exceed",
    target: 60,
    tolerance: null,
    range: null,
    weight: 1,
    error_type: "linear",
    reward_type: "linear",
    enable: true,
    description: null,
  };
  it("joins measures to project specs by folded name and marks pass/fail", () => {
    const chips = perfChips(
      catalog,
      [
        { name: "pm", value: 63.2, error: null },
        { name: "ugf", value: 7.1e6, error: null },
      ],
      [spec],
    );
    const pm = chips.find((c) => c.meas === "pm")!;
    expect(pm.status).toBe("ok");
    expect(pm.target).toBe(60);
    const ugf = chips.find((c) => c.meas === "ugf")!;
    expect(ugf.status).toBe("neutral"); // no spec named ugf → no invented target
    expect(ugf.target).toBeNull();
  });
  it("keeps errored measures as null-valued neutral chips", () => {
    const chips = perfChips(catalog, [{ name: "pm", value: null, error: "no ac analysis" }], [spec]);
    expect(chips.find((c) => c.meas === "pm")).toMatchObject({ value: null, status: "neutral" });
  });
  it("joins a spec named for the RAW vector — v(inoise_total) — to the bare measure", () => {
    const noiseSpec = {
      ...spec,
      name: "v(inoise_total)",
      goal: "minimize",
      target: 1.2e-3,
    };
    const chips = perfChips(
      catalog,
      [{ name: "inoise_total", value: 1.379e-3, error: null }],
      [noiseSpec],
    );
    const vn = chips.find((c) => c.meas === "inoise_total")!;
    expect(vn.target).toBe(1.2e-3);
    expect(vn.status).toBe("fail"); // 1.379 mV over the ≤1.2 mV spec — judged, not neutral
  });
});

describe("measureValueMap", () => {
  it("maps names to values with nulls preserved", () => {
    expect(
      measureValueMap([
        { name: "pm", value: 63, error: null },
        { name: "ugf", value: null, error: "x" },
      ]),
    ).toEqual({ pm: 63, ugf: null });
  });
});

describe("groupScalars", () => {
  it("groups ngspice @dev[param] and dev:param keys into device rows", () => {
    const g = groupScalars({
      "@m.xdut.m1[gm]": 1e-4,
      "@m.xdut.m1[gds]": 2e-6,
      "@m.xdut.m2[gm]": 9e-5,
      "M0:vds": 0.4,
      "v(out)": 0.9,
    });
    expect(g.rows.map((r) => r.dev)).toEqual(["M0", "m.xdut.m1", "m.xdut.m2"]);
    expect(g.columns).toEqual(["gm", "gds", "vds"]);
    expect(g.rows[1].params).toEqual({ gm: 1e-4, gds: 2e-6 });
    expect(g.other).toEqual([["v(out)", 0.9]]);
  });
  it("puts everything ungroupable into other", () => {
    const g = groupScalars({ "v(out)": 1, "i(vdd)": -2e-3 });
    expect(g.rows).toEqual([]);
    expect(g.other).toHaveLength(2);
  });
});

describe("parseDownsample", () => {
  it("parses method:max presets with a safe fallback", () => {
    expect(parseDownsample("lttb:8000")).toEqual({ method: "lttb", max_points: 8000 });
    expect(parseDownsample("bogus")).toEqual({ method: "bogus", max_points: 4000 });
  });
});

describe("datasetShortName", () => {
  it("keeps the last two path segments", () => {
    expect(datasetShortName(ds([], "/work/runs/r42/sim/tb_ac.raw"))).toBe("sim/tb_ac.raw");
  });
});
