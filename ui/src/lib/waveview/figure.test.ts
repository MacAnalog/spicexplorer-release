import { describe, expect, it } from "vitest";
import type { WaveResponse } from "@/types/api";
import {
  buildHistogramFigure,
  buildMcFigure,
  buildPvtFigure,
  buildWaveFigure,
  formatHz,
  layoutFor,
  signalRoles,
  type WaveFigureOpts,
} from "./figure";

const OPTS: WaveFigureOpts = {
  analysis: "ac",
  xLog: true,
  dual: true,
  bar: false,
  yLog: false,
};

const wave = (names: string[]): WaveResponse =>
  ({
    dataset_id: "d",
    analysis: "ac",
    x_name: "frequency",
    fmt: "mag_db",
    signals: names.map((name) => ({
      name,
      x: [1, 10, 100],
      y: [10, 0, -10],
      n_total: 3,
      n_returned: 3,
      downsampled: false,
    })),
  }) as unknown as WaveResponse;

describe("signalRoles", () => {
  it("first non-reference signal is the indigo primary", () => {
    const roles = signalRoles(["v(vin)", "v(vout)", "v(vmid)"]);
    expect(roles[0].role).toBe("reference");
    expect(roles[1].role).toBe("primary");
    expect(roles[1].color).toBe("#4f46e5");
    expect(roles[2].role).toBe("extra");
  });
  it("threshold/limit vectors are reference even when they mention out", () => {
    expect(signalRoles(["vout_limit"])[0].role).toBe("reference");
  });
});

describe("formatHz", () => {
  it("uses engineering units", () => {
    expect(formatHz(7.1e6)).toBe("7.1 MHz");
    expect(formatHz(5400)).toBe("5.4 kHz");
    expect(formatHz(12)).toBe("12 Hz");
  });
});

describe("layoutFor", () => {
  it("dual (Bode) gets a right phase axis and the 0 dB reference line", () => {
    const l = layoutFor(OPTS, {});
    expect(l.yaxis2).toMatchObject({ overlaying: "y", side: "right", showgrid: false });
    expect(l.shapes?.length).toBe(1); // 0 dB line only (no UGF without derived)
  });
  it("draws the UGF marker + annotation from derived measures", () => {
    const l = layoutFor(OPTS, { ugf: 1e6, pm: 60 });
    expect(l.shapes?.length).toBe(2);
    // plotly v3: shapes take RAW data coords on log axes; annotations log10.
    const ugfLine = l.shapes?.[1] as { x0?: number };
    expect(ugfLine.x0).toBe(1e6);
    const note = l.annotations?.[0] as { x?: number; text?: string };
    expect(note.x).toBeCloseTo(6);
    expect(note.text).toContain("UGF 1.0 MHz");
    expect(note.text).toContain("PM 60°");
  });
  it("noise gets log-log axes", () => {
    const l = layoutFor(
      { ...OPTS, analysis: "noise", dual: false, yLog: true, yUnits: "V/√Hz" },
      {},
    );
    expect((l.yaxis as { type?: string }).type).toBe("log");
  });
});

describe("buildWaveFigure", () => {
  it("routes phase to y2 and styles the overlay dashed", () => {
    const fig = buildWaveFigure(
      wave(["out"]),
      wave(["out"]),
      wave(["out"]),
      "golden",
      {},
      OPTS,
    );
    const [mag, phase, overlay] = fig.data as Array<Record<string, unknown>>;
    expect(mag).toMatchObject({ name: "|H| · out" });
    expect(phase).toMatchObject({ yaxis: "y2" });
    expect((overlay.line as { dash?: string }).dash).toBe("dash");
    expect(overlay.name).toBe("out · golden");
  });
  it("renders bar analyses as bars", () => {
    const fig = buildWaveFigure(wave(["h"]), null, null, undefined, {}, {
      ...OPTS,
      analysis: "pss",
      dual: false,
      bar: true,
    });
    expect((fig.data[0] as { type?: string }).type).toBe("bar");
  });
});

describe("buildPvtFigure", () => {
  const corner = (key: string, nominal: boolean, worst: boolean, y: number[]) => ({
    key,
    name: key,
    color: "#123456",
    nominal,
    worst,
    x: [1, 10],
    y,
    phase: null,
  });
  it("draws the envelope band plus per-corner lines with emphasis", () => {
    const fig = buildPvtFigure(
      [corner("tt", true, false, [1, 2]), corner("ff", false, true, [3, 4])],
      {},
      OPTS,
    );
    // 2 envelope traces + 2 corner lines
    expect(fig.data.length).toBe(4);
    const [lo, hi, tt, ff] = fig.data as Array<Record<string, unknown>>;
    expect(lo).toMatchObject({ showlegend: false });
    expect((hi.fillcolor as string).startsWith("rgba(79,70,229")).toBe(true);
    expect((tt.line as { width?: number }).width).toBe(2.6);
    expect((ff.line as { color?: string }).color).toBe("#ea580c");
  });
  it("envelope spans the min/max across corners", () => {
    const fig = buildPvtFigure(
      [corner("a", true, false, [1, 5]), corner("b", false, false, [3, 2])],
      {},
      OPTS,
    );
    const lo = fig.data[0] as { y: number[] };
    const hi = fig.data[1] as { y: number[] };
    expect(lo.y).toEqual([1, 2]);
    expect(hi.y).toEqual([3, 5]);
  });
});

describe("buildMcFigure", () => {
  it("draws ghost samples, a ±kσ band and the mean", () => {
    const fig = buildMcFigure(
      { x: [1, 2], samples: [[1, 2], [3, 4]], mean: [2, 3], sd: [1, 1] },
      3,
      {},
      OPTS,
    );
    const names = (fig.data as Array<{ name?: string }>).map((d) => d.name);
    expect(names).toContain("±3σ");
    expect(names).toContain("mean");
    const band = fig.data.find((d) => (d as { name?: string }).name === "±3σ") as {
      y: number[];
    };
    expect(band.y).toEqual([5, 6]); // mean + 3σ
  });
});

describe("buildHistogramFigure", () => {
  it("bins values and marks the spec + mean lines", () => {
    const fig = buildHistogramFigure([1, 2, 3, 4], { value: 2.5, cmp: "ge" }, "PM", "°");
    const bar = fig.data[0] as { x: number[]; y: number[]; marker: { color: string[] } };
    expect(bar.y.reduce((a, b) => a + b, 0)).toBe(4);
    // fail bins (below spec) are red, pass bins indigo
    expect(bar.marker.color).toContain("#dc2626");
    expect(bar.marker.color).toContain("#4f46e5");
    expect(fig.layout.shapes?.length).toBe(2);
  });
  it("works without a spec (no spec line, all bins indigo)", () => {
    const fig = buildHistogramFigure([1, 2, 3], null, "PM", "°");
    const bar = fig.data[0] as { marker: { color: string[] } };
    expect(new Set(bar.marker.color)).toEqual(new Set(["#4f46e5"]));
    expect(fig.layout.shapes?.length).toBe(1); // mean only
  });
});
