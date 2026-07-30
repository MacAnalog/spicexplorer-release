import { describe, expect, it } from "vitest";
import type { MeasurementCatalogResponse, TargetSpec, WaveRunArtifact } from "@/types/api";
import {
  cornerFromPath,
  cornerResults,
  cornersInArtifacts,
  foldMeasName,
  headlineFor,
  isMcCorner,
  isNominalCorner,
  mcStats,
  meanSdCurves,
  pvtStats,
  specForMeas,
} from "./sweep";

const art = (path: string, type: WaveRunArtifact["type"] = "ngspice_raw"): WaveRunArtifact => ({
  name: path.split("/").slice(-2).join("/"),
  path,
  type,
  mtime: 0,
  size: 1,
});

describe("cornerFromPath", () => {
  it("parses the __corner suffix of the artifact's parent folder", () => {
    expect(
      cornerFromPath("/work/runs/r1/sim/run_3_tb_ac__ss_125C_1V35/deck.raw"),
    ).toBe("ss_125C_1V35");
    expect(cornerFromPath("/work/runs/r1/sim/run_1_tb_ac__tt/deck.raw")).toBe("tt");
  });
  it("returns null for un-suffixed run folders", () => {
    expect(cornerFromPath("/work/runs/r1/sim/run_1_tb_ac/deck.raw")).toBeNull();
  });
  it("ignores double-underscores earlier in the path", () => {
    expect(cornerFromPath("/work/some__dir/sim/run_1_tb_ac/deck.raw")).toBeNull();
  });
});

describe("cornersInArtifacts", () => {
  it("collects unique corners from raw artifacts, nominal first", () => {
    const corners = cornersInArtifacts([
      art("/r/sim/run_1_tb_ac__ss/d.raw"),
      art("/r/sim/run_2_tb_ac__tt/d.raw"),
      art("/r/sim/run_3_tb_ac__ff/d.raw"),
      art("/r/sim/run_4_tb_ac__tt/d.raw"),
      art("/r/sim/run_1_tb_ac__ss/d.log", "log"), // non-raw ignored
    ]);
    expect(corners).toEqual(["tt", "ff", "ss"]);
  });
});

describe("isNominalCorner / isMcCorner", () => {
  it("reads tt/typ/nom prefixes as nominal", () => {
    expect(isNominalCorner("tt_27C_1V50")).toBe(true);
    expect(isNominalCorner("typical")).toBe(true);
    expect(isNominalCorner("ff_m40C")).toBe(false);
  });
  it("reads mc<N> as a Monte Carlo sample", () => {
    expect(isMcCorner("mc17")).toBe(true);
    expect(isMcCorner("mc_003")).toBe(true);
    expect(isMcCorner("tt_27C")).toBe(false);
  });
});

const catalog = {
  measurements: {
    pm: { kind: "scalar", required: ["out"], default_analysis: "ac" },
    inoise_total: { kind: "scalar", required: ["out"], default_analysis: "noise" },
    needs_two: { kind: "scalar", required: ["out", "ref"], default_analysis: "ac" },
  },
} as unknown as MeasurementCatalogResponse;

describe("headlineFor", () => {
  it("picks the first catalog-measurable headline for the analysis", () => {
    expect(headlineFor("ac", catalog)?.meas).toBe("pm");
    expect(headlineFor("noise", catalog)?.meas).toBe("inoise_total");
  });
  it("returns null when the catalog can't measure it (or no headline exists)", () => {
    expect(headlineFor("ac", null)).toBeNull();
    expect(headlineFor("tran", catalog)).toBeNull();
  });
});

const spec = (target: number, goal = "exceed"): TargetSpec =>
  ({ name: "pm", enable: true, goal, target, tolerance: null }) as TargetSpec;

describe("pvtStats", () => {
  const members = [
    { key: "tt", name: "tt", color: "#111", nominal: true },
    { key: "ff", name: "ff", color: "#222", nominal: false },
    { key: "ss", name: "ss", color: "#333", nominal: false },
  ];
  const headline = { meas: "pm", label: "Phase margin", unit: "°", worse: "low" as const };

  it("finds the worst corner and the spread without a spec (pass=null)", () => {
    const corners = cornerResults(members, { tt: 60, ff: 50, ss: 70 }, {});
    const s = pvtStats(corners, headline, null);
    expect(s.worstKey).toBe("ff");
    expect(s.pass).toBeNull();
    expect(s.total).toBe(3);
    expect(s.spread).toBe(10);
  });

  it("judges pass counts only against a project spec", () => {
    const corners = cornerResults(members, { tt: 60, ff: 50, ss: 70 }, {});
    const s = pvtStats(corners, headline, spec(55));
    expect(s.pass).toBe(2);
  });

  it("respects the user's corner toggles", () => {
    const corners = cornerResults(members, { tt: 60, ff: 50, ss: 70 }, { ff: false });
    const s = pvtStats(corners, headline, null);
    expect(s.worstKey).toBe("tt");
    expect(s.total).toBe(2);
  });
});

describe("mcStats", () => {
  const headline = { meas: "pm", label: "Phase margin", unit: "°", worse: "low" as const };
  it("computes mean/sigma/worst; yield and Cpk require a spec", () => {
    const s = mcStats([60, 62, 58], headline, null)!;
    expect(s.mean).toBe(60);
    expect(s.worst).toBe(58);
    expect(s.yield).toBeNull();
    expect(s.cpk).toBeNull();
  });
  it("computes yield/Cpk against a spec", () => {
    const s = mcStats([60, 62, 58, 40], headline, spec(55))!;
    expect(s.yield).toBe(0.75);
    expect(s.cpk).not.toBeNull();
  });
  it("returns null on an empty sample set", () => {
    expect(mcStats([], headline, null)).toBeNull();
  });
});

describe("meanSdCurves", () => {
  it("computes pointwise mean and sd", () => {
    const r = meanSdCurves([
      [0, 10],
      [2, 14],
    ])!;
    expect(r.mean).toEqual([1, 12]);
    expect(r.sd[0]).toBeCloseTo(1);
    expect(r.sd[1]).toBeCloseTo(2);
  });
  it("bails on ragged sample lengths", () => {
    expect(meanSdCurves([[1, 2], [1]])).toBeNull();
    expect(meanSdCurves([])).toBeNull();
  });
});

describe("foldMeasName / specForMeas", () => {
  it("joins by folded name and skips disabled specs", () => {
    const specs = [
      { name: "PM", enable: true, goal: "exceed", target: 60 },
      { name: "dc_gain", enable: false, goal: "exceed", target: 60 },
    ] as TargetSpec[];
    expect(specForMeas(specs, "pm")?.target).toBe(60);
    expect(specForMeas(specs, "dcgain")).toBeNull();
  });
  it("strips a raw-trace v()/i() wrapper (optimizer specs name the RAW vector)", () => {
    expect(foldMeasName("v(inoise_total)")).toBe("inoisetotal");
    expect(foldMeasName("i(i_supply)")).toBe("isupply");
    expect(foldMeasName("inoise_total")).toBe("inoisetotal");
    // only a full wrapper strips — an interior paren isn't a wrapper
    expect(foldMeasName("vdb(out)")).toBe("vdbout");
    const specs = [
      { name: "v(inoise_total)", enable: true, goal: "minimize", target: 1.2e-3 },
    ] as TargetSpec[];
    expect(specForMeas(specs, "inoise_total")?.target).toBe(1.2e-3);
  });
});
