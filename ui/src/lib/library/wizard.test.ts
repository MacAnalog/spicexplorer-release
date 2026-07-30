import { describe, expect, it } from "vitest";

import { INITIAL_WIZ_FORM, circuitPayload } from "./wizard";

describe("circuitPayload", () => {
  it("maps the circuit form to the create payload", () => {
    const p = circuitPayload({
      ...INITIAL_WIZ_FORM,
      kind: "circuit",
      id: "my_ota",
      name: "My OTA",
      klass: "amplifier",
      comp: "Miller",
      stages: "2",
      pdks: ["sky130", "ihp"],
      analyses: ["ac_open_loop"],
      customAnalyses: ["dc_op"],
      source: "wizard",
      designer: "me",
      license: "MIT",
      aliases: "a, b · c",
    });
    expect(p.id).toBe("my_ota");
    expect(p.class).toBe("amplifier");
    expect(p.compensation).toBe("Miller");
    expect(p.stages).toBe(2); // coerced to number
    expect(p.pdks).toEqual(["sky130", "ihp-sg13g2"]); // short → long DB keys
    expect(p.ports).toContain("vinp"); // class-based draft ports
    expect(p.analyses).toEqual(["ac_open_loop", "dc_op"]); // analyses + customAnalyses, deduped
    expect(p.provenance).toMatchObject({ source: "wizard", designer: "me", license: "MIT", aliases: ["a", "b", "c"] });
    // status is never sent — the backend always forces draft
    expect("status" in p).toBe(false);
  });

  it("handles empty stages/aliases and dedupes analyses", () => {
    const p = circuitPayload({
      ...INITIAL_WIZ_FORM,
      klass: "ldo",
      stages: "",
      aliases: "",
      analyses: ["dc_op"],
      customAnalyses: ["dc_op", "psrr"],
    });
    expect(p.stages).toBeUndefined();
    expect(p.analyses).toEqual(["dc_op", "psrr"]);
    expect(p.ports?.[0]).toBe("vdd"); // ldo default ports
    expect((p.provenance as { aliases: string[] }).aliases).toEqual([]);
  });
});
