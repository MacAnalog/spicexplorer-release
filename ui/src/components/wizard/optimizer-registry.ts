// Taken from the platform's examples/nevergrad_reference_registry.yaml and
// examples/nevergrad_reference_configurable_families.yaml, without the 13 names
// that nevergrad 1.0.12 (the version the platform locks) lacks or that the
// platform cannot build; optimizer-registry.test.ts checks every name against a
// snapshot of that version. Keys are family labels; values are algorithm names
// accepted as `optimizer_config.name`.

export interface AlgorithmGroup {
  label: string;
  items: string[];
}

export const NEVERGRAD_REGISTRY: AlgorithmGroup[] = [
  {
    // Classes in ng.families: the platform passes them optimizer_kwargs and
    // not num_workers. The shipped folded_cascode example uses SamplingSearch.
    // Eight more ng.families names are listed in the groups below: ParametrizedCMA,
    // EMNA, ConfPortfolio, NoisySplit, ParametrizedOnePlusOne, ConfPSO,
    // ParametrizedBO, ParametrizedTBPSA (nevergrad 1.0.12). The platform
    // looks up every other name in ng.optimizers.registry, as a fixed algorithm.
    label: "Configurable Families",
    items: ["DifferentialEvolution", "SamplingSearch"],
  },
  {
    label: "Differential Evolution",
    items: [
      "DE", "TwoPointsDE", "OnePointDE", "LhsDE",
      "NoisyDE", "DiscreteDE", "GeneticDE", "MiniDE",
      "RotatedTwoPointsDE", "RotationInvariantDE", "AlmostRotationInvariantDE",
    ],
  },
  {
    label: "CMA-ES",
    items: [
      "CMA", "DiagonalCMA", "ParametrizedCMA",
      "MetaCMA", "DoubleFastGADiscreteOnePlusOne",
      "EDA", "EMNA",
      "LargeCMA", "TinyCMA", "MicroCMA",
    ],
  },
  {
    label: "AutoML / NGOpt",
    items: [
      "NGOpt", "NGO", "NGOptRW",
      "NGOpt4", "NGOpt8", "NGOpt10", "NGOpt39",
      "NgDS", "NgDS11", "NgDS2",
      "NgIoh", "NgIoh10", "NgIoh21",
    ],
  },
  {
    label: "Portfolios",
    items: [
      "Portfolio", "ConfPortfolio", "ParaPortfolio",
      "Shiwa", "CM", "CMandAS2", "CMandAS3", "Wiz",
      "BFGSCMA", "BFGSCMAPlus", "LogBFGSCMA", "LogBFGSCMAPlus",
      "SqrtBFGSCMA", "SqrtBFGSCMAPlus",
      "SQPCMA", "SQPCMAPlus", "SqrtSQPCMAPlus",
      "MultiBFGS", "MultiBFGSPlus", "LogMultiBFGSPlus", "SqrtMultiBFGSPlus",
      "MultiCobyla", "MultiCobylaPlus", "MultiSQP", "MultiSQPPlus",
    ],
  },
  {
    label: "Meta-wrappers",
    items: ["NoisySplit"],
  },
  {
    label: "One Plus One",
    items: [
      "OnePlusOne", "ParametrizedOnePlusOne",
      "DiscreteOnePlusOne", "OptimisticDiscreteOnePlusOne", "MultiDiscrete",
      "NoisyOnePlusOne", "OptimisticNoisyOnePlusOne",
    ],
  },
  {
    label: "Sampling / Quasi-random",
    items: [
      "RandomSearch", "RandomSearchPlusMiddlePoint",
      "HaltonSearch", "ScrHaltonSearch",
      "HammersleySearch", "ScrHammersleySearch", "LHSSearch",
    ],
  },
  {
    label: "PSO",
    items: ["PSO", "ConfPSO", "RealSpacePSO", "SQOPSO"],
  },
  {
    label: "Gradient-based / SciPy",
    items: ["NelderMead", "BFGS", "LBFGSB", "Cobyla", "SQP", "Powell", "ForceMultiCobyla"],
  },
  {
    label: "Bayesian (Nevergrad)",
    items: ["BO", "ParametrizedBO", "NoisyBandit"],
  },
  {
    label: "Other",
    items: ["SPSA", "TBPSA", "ParametrizedTBPSA", "cGA", "VoronoiDE", "AXP"],
  },
];

// The 13 names removed from NEVERGRAD_REGISTRY: nevergrad 1.0.12 lacks the first 8,
// and the platform cannot build the other 5 (optimizer-registry.test.ts gives the
// reason for each). A run with any of them stops before the first trial. An old
// project YAML can still store one, so the Optimizer step names it in a warning.
export const NEVERGRAD_UNBUILDABLE_NAMES: readonly string[] = [
  "TinyDE", "MEDA", "PCEDA", "MPCEDA", "NGOpt38", "Rescaled", "SplitOptimizer", "MultipleSingleRuns",
  "Chaining", "BayesOptim", "PCABO", "FCMA", "AX",
];

/** True when `name` is one of the algorithms in `NEVERGRAD_REGISTRY`. */
export function isListedNevergradName(name: string): boolean {
  return NEVERGRAD_REGISTRY.some((g) => g.items.includes(name));
}

/**
 * The warning the Optimizer step shows when the form holds a nevergrad algorithm
 * name that `NEVERGRAD_REGISTRY` does not list, or null when the list has it. That
 * happens when an old project YAML is opened in the wizard: the parser keeps the
 * stored `name` unchanged.
 */
export function nevergradNameNotice(name: string): string | null {
  if (isListedNevergradName(name)) return null;
  if (NEVERGRAD_UNBUILDABLE_NAMES.includes(name)) {
    return `"${name}" is not an algorithm the platform can build: a run with it stops before the first trial. Choose another algorithm before saving the project.`;
  }
  return `"${name}" is not in the nevergrad list. Choose an algorithm from the list before saving the project.`;
}

// Recommended-kwarg presets for the "Configurable Families" set, used to seed
// the optimizer_kwargs editor when the user picks one of these algorithm names.
export interface KwargPreset {
  key: string;
  value: string;
  hint?: string;
}

export const NEVERGRAD_KWARG_PRESETS: Record<string, KwargPreset[]> = {
  DifferentialEvolution: [
    { key: "initialization", value: "LHS", hint: 'LHS | random | gaussian | QR' },
    { key: "crossover", value: "twopoints", hint: "twopoints | onepoint | dimension | random" },
    { key: "popsize", value: "standard", hint: 'int or "standard" | "dimension" | "large"' },
    { key: "recommendation", value: "pessimistic", hint: "pessimistic | optimistic | noisy | mean" },
    { key: "scale", value: "1.0" },
  ],
  SamplingSearch: [
    { key: "sampler", value: "Halton", hint: "Halton | Hammersley | LHS | random" },
    { key: "scrambled", value: "true" },
    { key: "rescaled", value: "true" },
    { key: "cauchy", value: "false" },
  ],
  ParametrizedCMA: [
    { key: "diagonal", value: "false", hint: "true for >100 dims" },
    { key: "elitist", value: "false" },
    { key: "popsize", value: "null", hint: "null = auto" },
    { key: "random_init", value: "false" },
  ],
  ConfPSO: [
    { key: "popsize", value: "40" },
    { key: "omega", value: "0.72" },
    { key: "phip", value: "1.2" },
    { key: "phig", value: "1.2" },
  ],
  ParametrizedOnePlusOne: [
    { key: "noise_handling", value: "optimistic", hint: "null | random | optimistic" },
    { key: "mutation", value: "gaussian", hint: "gaussian | cauchy | discrete | fastga | doublefastga" },
    { key: "crossover", value: "false" },
  ],
  ParametrizedBO: [
    { key: "initialization", value: "Hammersley", hint: "Hammersley | random | LHS" },
    { key: "init_budget", value: "10" },
    { key: "utility_kind", value: "ucb", hint: "ucb | ei | poi" },
  ],
};

// Ax platform (Bayesian optimization). The platform's Ax engine code
// (`optimization/stochastic/bayesian_ax.py`) reads the bounds, budget,
// `random_seed` and `optimizer_kwargs.batch_size`. It does not read the
// algorithm name or the three preset keys below: the wizard writes them to the
// YAML so a project records the intended setting.
export const AX_ALGORITHMS = [
  "AxAuto",        // Ax's default GenerationStrategy (Sobol → BoTorch GP)
  "AxBoTorch",     // Force BoTorch model after init
  "AxSobol",       // Pure quasi-random Sobol baseline
];

export const AX_KWARG_PRESETS: KwargPreset[] = [
  { key: "num_sobol_trials", value: "10", hint: "Quasi-random (Sobol) trials run before the Gaussian-process model proposes points" },
  { key: "acquisition_function", value: "qNoisyExpectedImprovement", hint: "qNEI | qEI | qUCB | qPI" },
  { key: "model_kwargs", value: "", hint: "Extra keyword arguments for the BoTorch model" },
];

// The optimizer engines the wizard offers, as `optimizer_config.type` values.
// These are the two engines the platform runs. `reinforcement_learning` is not
// listed: the platform retired it, and a project YAML that still names it fails
// when a run resolves its optimizer (MacAnalog/spicexplorer-ui#64).
export interface OptimizerTypeOption {
  value: string;
  label: string;
}

export const OPTIMIZER_TYPES: OptimizerTypeOption[] = [
  { value: "nevergrad", label: "nevergrad" },
  { value: "bayesian_ax", label: "bayesian_ax (Ax platform)" },
];

/** True when `type` is one of the engines in `OPTIMIZER_TYPES`. */
export function isOfferedOptimizerType(type: string): boolean {
  return OPTIMIZER_TYPES.some((t) => t.value === type);
}

/**
 * The warning the Optimizer step shows when the form holds an engine it does not
 * offer, or null when the engine is offered. That happens when an old project
 * YAML is opened in the wizard: the parser keeps the stored `type` unchanged.
 */
export function optimizerTypeNotice(type: string): string | null {
  if (isOfferedOptimizerType(type)) return null;
  const choices = OPTIMIZER_TYPES.map((t) => t.value).join(" or ");
  const what =
    type === "reinforcement_learning"
      ? "was retired from the platform"
      : "is not an optimizer engine the platform runs";
  return `"${type}" ${what}. Choose ${choices} before saving the project.`;
}

/**
 * The algorithm name to store after the engine changes to `type`. A name that the
 * new engine lists is kept; otherwise the engine's default is used: `LhsDE` for
 * nevergrad, the first entry of `AX_ALGORITHMS` for bayesian_ax. For an engine the
 * wizard does not offer, the name is returned unchanged.
 */
export function snapAlgorithmName(type: string, currentName: string): string {
  if (type === "nevergrad") {
    return isListedNevergradName(currentName) ? currentName : "LhsDE";
  }
  if (type === "bayesian_ax") {
    return AX_ALGORITHMS.includes(currentName) ? currentName : AX_ALGORITHMS[0];
  }
  return currentName;
}
