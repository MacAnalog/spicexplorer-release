import { createElement, isValidElement, type ReactElement, type ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import { OptimizerStep } from "./OptimizerStep";

// Renders the wizard's Optimizer step to HTML on the server (no DOM needed) and
// reads the <option> list of the "Optimizer type" <select>, which is the first
// <select> in the step.
//
// A server render reads a zustand store's initial state, not its current state,
// so the store module is replaced by one that returns the real default form with
// the optimizer fields in `override` applied on top.
const override = vi.hoisted(() => ({
  optimizer: {} as Record<string, unknown>,
  updateOptimizer: (() => {}) as (patch: Record<string, unknown>) => void,
}));

vi.mock("@/stores/wizardStore", async (importOriginal) => {
  const real = await importOriginal<typeof import("@/stores/wizardStore")>();
  const useWizardStore = () => {
    const form = real.useWizardStore.getInitialState().form;
    return {
      form: { ...form, optimizer: { ...form.optimizer, ...override.optimizer } },
      updateOptimizer: (patch: Record<string, unknown>) => override.updateOptimizer(patch),
    };
  };
  return { ...real, useWizardStore };
});

function renderStep(): string {
  return renderToStaticMarkup(createElement(OptimizerStep));
}

/** The <option> tags of the first <select> in `html`, as {value, disabled}. */
function typeOptions(html: string): { value: string; disabled: boolean }[] {
  const first = html.match(/<select[^>]*>([\s\S]*?)<\/select>/);
  if (!first) throw new Error("no <select> in the rendered step");
  return [...first[1].matchAll(/<option([^>]*)>/g)].map((m) => ({
    value: /value="([^"]*)"/.exec(m[1])?.[1] ?? "",
    disabled: /\sdisabled=""/.test(m[1]),
  }));
}

/** The <option> tags of the "Algorithm name" <select> (the second <select>), as {value, disabled, selected}. */
function algorithmOptions(html: string): { value: string; disabled: boolean; selected: boolean }[] {
  const second = [...html.matchAll(/<select[^>]*>([\s\S]*?)<\/select>/g)][1];
  if (!second) throw new Error("no algorithm <select> in the rendered step");
  return [...second[1].matchAll(/<option([^>]*)>/g)].map((m) => ({
    value: /value="([^"]*)"/.exec(m[1])?.[1] ?? "",
    disabled: /\sdisabled=""/.test(m[1]),
    selected: /\sselected=""/.test(m[1]),
  }));
}

/** True when the "Seed preset kwargs" <button> in `html` carries the disabled attribute. */
function seedButtonDisabled(html: string): boolean {
  const tags = [...html.matchAll(/<button([^>]*)>([\s\S]*?)<\/button>/g)].filter((m) =>
    m[2].includes("Seed preset kwargs"),
  );
  if (tags.length !== 1) throw new Error(`expected one Seed preset kwargs button, found ${tags.length}`);
  return /\sdisabled=""/.test(tags[0][1]);
}

function setOptimizer(type: string, name: string) {
  override.optimizer = { type, name };
}

/** Every <select> element in the tree `OptimizerStep()` returns, in document order. */
function selectElements(node: ReactNode): ReactElement<{ onChange: (e: unknown) => void }>[] {
  if (Array.isArray(node)) return node.flatMap(selectElements);
  if (!isValidElement<{ children?: ReactNode }>(node)) return [];
  const own = node.type === "select" ? [node as ReactElement<{ onChange: (e: unknown) => void }>] : [];
  return [...own, ...selectElements(node.props.children)];
}

/** Choose `value` in the n-th <select> (0 = engine, 1 = algorithm) and return the patches sent to the store. */
function chooseIn(n: number, value: string): Record<string, unknown>[] {
  const patches: Record<string, unknown>[] = [];
  override.updateOptimizer = (patch) => patches.push(patch);
  // OptimizerStep calls no React hook of its own (the store hook is replaced),
  // so it can be called as a plain function to get its element tree.
  const tree = OptimizerStep();
  selectElements(tree)[n].props.onChange({ target: { value } });
  return patches;
}

/** Choose `value` in the "Optimizer type" <select> and return the patch sent to the store. */
function chooseEngine(value: string): Record<string, unknown>[] {
  return chooseIn(0, value);
}

afterEach(() => {
  override.optimizer = {};
  override.updateOptimizer = () => {};
});

describe("OptimizerStep engine list (MacAnalog/spicexplorer-ui#64)", () => {
  it("offers exactly nevergrad and bayesian_ax on a new project", () => {
    const opts = typeOptions(renderStep());
    expect(opts.map((o) => o.value)).toEqual(["nevergrad", "bayesian_ax"]);
    expect(opts.every((o) => !o.disabled)).toBe(true);
  });

  it("never renders the retired reinforcement_learning engine or its algorithm list", () => {
    const html = renderStep();
    expect(html).not.toContain("reinforcement_learning");
    expect(html).not.toContain('value="ppo"');
  });

  it("offers the same two engines while bayesian_ax is selected", () => {
    setOptimizer("bayesian_ax", "AxAuto");
    const html = renderStep();
    expect(typeOptions(html).map((o) => o.value)).toEqual(["nevergrad", "bayesian_ax"]);
    expect(html).toContain('value="AxBoTorch"');
    expect(html).not.toContain('role="alert"');
  });

  it("marks a retired engine read from an old YAML as not selectable and says so", () => {
    // /api/project/parse-to-form still returns `type: reinforcement_learning` for
    // an old project file; the step must not show it as a valid choice.
    setOptimizer("reinforcement_learning", "ppo");
    const html = renderStep();
    const opts = typeOptions(html);
    const selectable = opts.filter((o) => !o.disabled).map((o) => o.value);
    expect(selectable).toEqual(["nevergrad", "bayesian_ax"]);
    expect(opts.filter((o) => o.disabled).map((o) => o.value)).toEqual(["reinforcement_learning"]);
    expect(html).toContain("was retired from the platform");
    // the algorithm list of the retired engine is gone; the stored name stays visible as text
    expect(html).not.toContain('value="sac"');
    expect(html).toMatch(/<input[^>]*value="ppo"/);
  });
});

describe("OptimizerStep \"Seed preset kwargs\" button", () => {
  it("is disabled for an engine the wizard does not offer, even with a preset name", () => {
    // DifferentialEvolution has a nevergrad preset, so only the engine check disables it.
    setOptimizer("reinforcement_learning", "DifferentialEvolution");
    expect(seedButtonDisabled(renderStep())).toBe(true);
  });

  it("is disabled for a nevergrad algorithm that has no preset", () => {
    setOptimizer("nevergrad", "LhsDE");
    expect(seedButtonDisabled(renderStep())).toBe(true);
  });

  it("is enabled for a nevergrad algorithm that takes settings and has a preset", () => {
    setOptimizer("nevergrad", "DifferentialEvolution");
    const html = renderStep();
    expect(seedButtonDisabled(html)).toBe(false);
    expect(html).toContain("DifferentialEvolution takes settings. “Seed preset kwargs” adds the DifferentialEvolution preset keys.");
  });

  it("is enabled for bayesian_ax", () => {
    setOptimizer("bayesian_ax", "AxAuto");
    expect(seedButtonDisabled(renderStep())).toBe(false);
  });
});

describe("OptimizerStep text", () => {
  it("shows the unoffered-engine warning as an alert, not as a field hint", () => {
    setOptimizer("reinforcement_learning", "ppo");
    expect(renderStep()).toMatch(/<span role="alert"[^>]*>&quot;reinforcement_learning&quot; was retired from the platform\./);
  });

  it("shows no alert for an offered engine", () => {
    setOptimizer("nevergrad", "LhsDE");
    expect(renderStep()).not.toContain('role="alert"');
  });

  it("says which optimizer_kwargs rows each engine reads", () => {
    const html = renderStep();
    expect(html).toContain("nevergrad never passes batch_size.");
    expect(html).toContain(
      "It passes num_workers to a fixed algorithm such as NGOpt or TwoPointsDE, but not to one that takes settings, such as DifferentialEvolution or ParametrizedCMA.",
    );
    expect(html).toContain(
      "It passes every other row to an algorithm that takes settings, and a row that algorithm does not know stops the run.",
    );
    expect(html).toContain("A fixed algorithm refuses the other rows and runs with its default settings.");
    expect(html).not.toContain("configurable family");
    expect(html).toContain("The Ax engine reads only batch_size.");
    expect(html).not.toContain("passed unchanged");
  });

  it("says the algorithm uses its default settings when there are no optimizer_kwargs rows", () => {
    setOptimizer("nevergrad", "LhsDE");
    override.optimizer.optimizer_kwargs = [];
    const html = renderStep();
    expect(html).toContain("No optimizer_kwargs rows: the algorithm runs with its default settings.");
    expect(html).not.toContain("out of the box");
  });

  it("names the Ax preset keys and says they do not change the run", () => {
    setOptimizer("bayesian_ax", "AxAuto");
    expect(renderStep()).toContain(
      "The preset keys (num_sobol_trials, acquisition_function, model_kwargs) are written to the YAML and do not change the run.",
    );
  });
});

describe("OptimizerStep engine change", () => {
  it("replaces an old ppo name with the nevergrad default when nevergrad is chosen", () => {
    setOptimizer("reinforcement_learning", "ppo");
    expect(chooseEngine("nevergrad")).toEqual([{ type: "nevergrad", name: "LhsDE" }]);
  });

  it("replaces a nevergrad name with the first Ax algorithm when bayesian_ax is chosen", () => {
    setOptimizer("nevergrad", "LhsDE");
    expect(chooseEngine("bayesian_ax")).toEqual([{ type: "bayesian_ax", name: "AxAuto" }]);
  });

  it("keeps a nevergrad name that the registry lists", () => {
    setOptimizer("bayesian_ax", "CMA");
    expect(chooseEngine("nevergrad")).toEqual([{ type: "nevergrad", name: "CMA" }]);
  });
});

describe("OptimizerStep nevergrad name the list does not have (an old YAML)", () => {
  // /api/project/parse-to-form copies optimizer_config.name unchanged, so an old
  // project file can hold one of the 13 names removed from NEVERGRAD_REGISTRY.
  it("keeps a removed name such as TinyDE as the selected, disabled entry", () => {
    setOptimizer("nevergrad", "TinyDE");
    const html = renderStep();
    const opts = algorithmOptions(html);
    expect(opts.filter((o) => o.selected)).toEqual([{ value: "TinyDE", disabled: true, selected: true }]);
    expect(opts.filter((o) => o.disabled).map((o) => o.value)).toEqual(["TinyDE"]);
    expect(html).toContain("TinyDE (not available)</option>");
    // the list the user chooses from is unchanged
    const selectable = opts.filter((o) => !o.disabled).map((o) => o.value);
    expect(selectable).toContain("LhsDE");
    expect(selectable).not.toContain("TinyDE");
  });

  it("says the platform cannot build a removed name and asks for another", () => {
    setOptimizer("nevergrad", "TinyDE");
    expect(renderStep()).toMatch(
      /<span role="alert"[^>]*>&quot;TinyDE&quot; is not an algorithm the platform can build: a run with it stops before the first trial\. Choose another algorithm before saving the project\.<\/span>/,
    );
  });

  it("says a name that is not one of the removed ones is not in the list, without claiming the platform cannot build it", () => {
    setOptimizer("nevergrad", "MyOwnDE");
    const html = renderStep();
    expect(algorithmOptions(html).filter((o) => o.selected)).toEqual([{ value: "MyOwnDE", disabled: true, selected: true }]);
    expect(html).toMatch(
      /<span role="alert"[^>]*>&quot;MyOwnDE&quot; is not in the nevergrad list\. Choose an algorithm from the list before saving the project\.<\/span>/,
    );
    expect(html).not.toContain("cannot build");
  });

  it("does not change the stored name while it renders the step", () => {
    const patches: Record<string, unknown>[] = [];
    override.updateOptimizer = (patch) => patches.push(patch);
    setOptimizer("nevergrad", "TinyDE");
    renderStep();
    OptimizerStep();
    expect(patches).toEqual([]);
  });

  it("stores the algorithm the user picks, after which the entry and the alert are gone", () => {
    setOptimizer("nevergrad", "TinyDE");
    expect(chooseIn(1, "CMA")).toEqual([{ name: "CMA" }]);
    setOptimizer("nevergrad", "CMA");
    const html = renderStep();
    const opts = algorithmOptions(html);
    expect(opts.filter((o) => o.selected)).toEqual([{ value: "CMA", disabled: false, selected: true }]);
    expect(opts.some((o) => o.disabled || o.value === "TinyDE")).toBe(false);
    expect(html).not.toContain('role="alert"');
  });

  it("shows a listed name as selected with no disabled entry", () => {
    setOptimizer("nevergrad", "LhsDE");
    const opts = algorithmOptions(renderStep());
    expect(opts.filter((o) => o.selected).map((o) => o.value)).toEqual(["LhsDE"]);
    expect(opts.some((o) => o.disabled)).toBe(false);
  });
});
