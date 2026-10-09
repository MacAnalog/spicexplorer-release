import { describe, expect, it } from "vitest";
import type { PVTCornerDef } from "@/types/api";
import { cornerIncludes, cornerOptionLabel, cornerSummary } from "./pvt";

// A gf180mcu-style corner: the bundle starts with a plain `.include design.ngspice`
// (no section), then a `.lib sm141064.ngspice typical` card. `/api/project/load`
// returns `section: null` for the first one (platform WP-04).
function corner(includes: PVTCornerDef["model_includes"]): PVTCornerDef {
  return {
    name: "typical",
    enabled: true,
    temp: 27,
    supplies: [{ node: "VDD", value: 3.3 }],
    model_includes: includes,
    params: {},
  };
}

describe("cornerIncludes (MacAnalog/spicexplorer-ui#63)", () => {
  it("prints a bare file name for an include whose section is null", () => {
    const c = corner([
      { lib_file: "design.ngspice", section: null },
      { lib_file: "sm141064.ngspice", section: "typical" },
    ]);
    expect(cornerIncludes(c)).toBe("design.ngspice, sm141064.ngspice:typical");
  });

  it("prints a bare file name when the section key is absent", () => {
    // the generated type makes `section` optional: the server may omit it
    const c = corner([{ lib_file: "design.ngspice" }, { lib_file: "sm141064.ngspice", section: "typical" }]);
    expect(cornerIncludes(c)).toBe("design.ngspice, sm141064.ngspice:typical");
  });

  it("prints a bare file name for an empty section, which the platform also reads as no section", () => {
    const c = corner([{ lib_file: "design.ngspice", section: "" }]);
    expect(cornerIncludes(c)).toBe("design.ngspice");
  });

  it("keeps file:section for every include that has a section", () => {
    const c = corner([
      { lib_file: "cornerMOSlv.lib", section: "mos_ss" },
      { lib_file: "cornerRES.lib", section: "res_wcs" },
    ]);
    expect(cornerIncludes(c)).toBe("cornerMOSlv.lib:mos_ss, cornerRES.lib:res_wcs");
  });

  it("returns an empty string for a corner with no includes", () => {
    expect(cornerIncludes(corner([]))).toBe("");
  });
});

describe("corner labels are unaffected by a sectionless include", () => {
  it("summarises temperature and supply only", () => {
    const c = corner([{ lib_file: "design.ngspice", section: null }]);
    expect(cornerSummary(c)).toBe("27°C · VDD 3.3V");
    expect(cornerOptionLabel(c)).toBe("typical — 27°C · VDD 3.3V");
  });
});
