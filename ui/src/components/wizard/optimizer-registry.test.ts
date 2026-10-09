import { describe, expect, it } from "vitest";
import {
  AX_ALGORITHMS,
  NEVERGRAD_REGISTRY,
  NEVERGRAD_UNBUILDABLE_NAMES,
  OPTIMIZER_TYPES,
  isListedNevergradName,
  isOfferedOptimizerType,
  nevergradNameNotice,
  optimizerTypeNotice,
  snapAlgorithmName,
} from "./optimizer-registry";
// Snapshot of nevergrad 1.0.12, the version the platform's uv.lock pins. Regenerate it
// in spicexplorer-platform after a nevergrad update:
//   uv run python -c "import json, nevergrad as ng; print(json.dumps({'nevergrad': ng.__version__,
//     'registry': sorted(ng.optimizers.registry),
//     'families': sorted(n for n in dir(ng.families) if not n.startswith('_'))}, indent=1))"
import nevergradNames from "./nevergrad-1.0.12-names.json";

describe("OPTIMIZER_TYPES (MacAnalog/spicexplorer-ui#64)", () => {
  it("lists exactly the two engines the platform runs, in display order", () => {
    expect(OPTIMIZER_TYPES.map((t) => t.value)).toEqual(["nevergrad", "bayesian_ax"]);
  });

  it("does not list the retired reinforcement_learning engine", () => {
    expect(isOfferedOptimizerType("reinforcement_learning")).toBe(false);
    expect(OPTIMIZER_TYPES.some((t) => /reinforcement|ppo/i.test(`${t.value} ${t.label}`))).toBe(false);
  });

  it("recognises each listed engine and rejects near-misses", () => {
    expect(isOfferedOptimizerType("nevergrad")).toBe(true);
    expect(isOfferedOptimizerType("bayesian_ax")).toBe(true);
    expect(isOfferedOptimizerType("Nevergrad")).toBe(false);
    expect(isOfferedOptimizerType("")).toBe(false);
  });
});

describe("optimizerTypeNotice", () => {
  it("is null for an offered engine", () => {
    expect(optimizerTypeNotice("nevergrad")).toBeNull();
    expect(optimizerTypeNotice("bayesian_ax")).toBeNull();
  });

  it("names the retirement for reinforcement_learning and lists the choices", () => {
    expect(optimizerTypeNotice("reinforcement_learning")).toBe(
      '"reinforcement_learning" was retired from the platform. Choose nevergrad or bayesian_ax before saving the project.',
    );
  });

  it("warns about any other unknown engine without claiming it was retired", () => {
    const msg = optimizerTypeNotice("genetic");
    expect(msg).toBe(
      '"genetic" is not an optimizer engine the platform runs. Choose nevergrad or bayesian_ax before saving the project.',
    );
  });
});

describe("snapAlgorithmName", () => {
  it("keeps a nevergrad name when switching to nevergrad", () => {
    expect(snapAlgorithmName("nevergrad", "CMA")).toBe("CMA");
  });

  it("falls back to LhsDE when the name is not in the nevergrad registry", () => {
    expect(snapAlgorithmName("nevergrad", "AxBoTorch")).toBe("LhsDE");
    expect(NEVERGRAD_REGISTRY.some((g) => g.items.includes("LhsDE"))).toBe(true);
  });

  it("keeps an Ax name when switching to bayesian_ax", () => {
    expect(snapAlgorithmName("bayesian_ax", "AxSobol")).toBe("AxSobol");
  });

  it("falls back to the first Ax algorithm when the name is not an Ax one", () => {
    expect(snapAlgorithmName("bayesian_ax", "LhsDE")).toBe(AX_ALGORITHMS[0]);
    expect(AX_ALGORITHMS[0]).toBe("AxAuto");
  });

  it("never produces the retired ppo name", () => {
    expect(snapAlgorithmName("reinforcement_learning", "LhsDE")).toBe("LhsDE");
    for (const t of OPTIMIZER_TYPES) expect(snapAlgorithmName(t.value, "ppo")).not.toBe("ppo");
  });
});

describe("NEVERGRAD_REGISTRY against nevergrad 1.0.12", () => {
  const listed = NEVERGRAD_REGISTRY.flatMap((g) => g.items);
  const registry = new Set(nevergradNames.registry);
  const families = new Set(nevergradNames.families);

  // Names a run with the platform's locked packages cannot build. The platform
  // (optimization/stochastic/nevergrad.py) first looks a name up in ng.families,
  // then in ng.optimizers.registry, and raises "not found" otherwise.
  const NOT_BUILDABLE: Record<string, string> = {
    TinyDE: "not in the registry",
    MEDA: "not in the registry",
    PCEDA: "not in the registry",
    MPCEDA: "not in the registry",
    NGOpt38: "not in the registry",
    Rescaled: "not in the registry",
    SplitOptimizer: "not in the registry",
    MultipleSingleRuns: "not in the registry",
    Chaining: "ng.families class that needs optimizer objects, which a YAML row cannot hold",
    BayesOptim: "ng.families class that imports bayes_optim, which the platform does not install",
    PCABO: "imports bayes_optim, which the platform does not install",
    FCMA: "imports fcmaes, which the platform does not install",
    AX: "imports ax.optimize, which ax-platform 1.3.1 does not have",
  };

  it("is checked against the snapshot of nevergrad 1.0.12", () => {
    expect(nevergradNames.nevergrad).toBe("1.0.12");
  });

  it("lists only names in ng.families or ng.optimizers.registry", () => {
    expect(listed.filter((n) => !families.has(n) && !registry.has(n))).toEqual([]);
  });

  it("lists none of the names the platform cannot build", () => {
    expect(listed.filter((n) => n in NOT_BUILDABLE)).toEqual([]);
  });

  it("lists each name once", () => {
    expect(listed.filter((n, i) => listed.indexOf(n) !== i)).toEqual([]);
  });

  it("names the same 13 removed names in NEVERGRAD_UNBUILDABLE_NAMES", () => {
    expect([...NEVERGRAD_UNBUILDABLE_NAMES].sort()).toEqual(Object.keys(NOT_BUILDABLE).sort());
  });
});

describe("nevergradNameNotice (a name read from an old YAML)", () => {
  it("is null for a name the list has", () => {
    expect(isListedNevergradName("LhsDE")).toBe(true);
    expect(nevergradNameNotice("LhsDE")).toBeNull();
    expect(nevergradNameNotice("DifferentialEvolution")).toBeNull();
  });

  it("says the platform cannot build each of the 13 removed names", () => {
    for (const name of NEVERGRAD_UNBUILDABLE_NAMES) {
      expect(isListedNevergradName(name)).toBe(false);
      expect(nevergradNameNotice(name)).toBe(
        `"${name}" is not an algorithm the platform can build: a run with it stops before the first trial. Choose another algorithm before saving the project.`,
      );
    }
  });

  it("says any other missing name is not in the list, without claiming the platform cannot build it", () => {
    // RecES is in nevergrad 1.0.12's registry but not in the wizard's list.
    expect(nevergradNameNotice("RecES")).toBe(
      '"RecES" is not in the nevergrad list. Choose an algorithm from the list before saving the project.',
    );
  });
});
