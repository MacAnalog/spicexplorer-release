// Mirrors examples/nevergrad_reference_registry.yaml and
// examples/nevergrad_reference_configurable_families.yaml so the wizard's
// dropdowns stay in sync with the upstream registry. Keys are family labels;
// values are algorithm names accepted as `optimizer_config.name`.

export interface AlgorithmGroup {
  label: string;
  items: string[];
}

export const NEVERGRAD_REGISTRY: AlgorithmGroup[] = [
  {
    // Configurable-family classes (resolved via ng.families). These take
    // optimizer_kwargs; the shipped folded_cascode example uses SamplingSearch.
    // (ParametrizedCMA / ConfPSO / ParametrizedOnePlusOne / ParametrizedBO are
    // listed under their own groups below.)
    label: "Configurable Families",
    items: ["DifferentialEvolution", "SamplingSearch"],
  },
  {
    label: "Differential Evolution",
    items: [
      "DE", "TwoPointsDE", "OnePointDE", "LhsDE",
      "NoisyDE", "DiscreteDE", "GeneticDE", "MiniDE", "TinyDE",
      "RotatedTwoPointsDE", "RotationInvariantDE", "AlmostRotationInvariantDE",
    ],
  },
  {
    label: "CMA-ES",
    items: [
      "CMA", "DiagonalCMA", "ParametrizedCMA",
      "MetaCMA", "DoubleFastGADiscreteOnePlusOne", "FCMA",
      "EDA", "MEDA", "PCEDA", "MPCEDA", "EMNA",
      "LargeCMA", "TinyCMA", "MicroCMA",
    ],
  },
  {
    label: "AutoML / NGOpt",
    items: [
      "NGOpt", "NGO", "NGOptRW",
      "NGOpt4", "NGOpt8", "NGOpt10", "NGOpt38", "NGOpt39",
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
    items: ["Chaining", "Rescaled", "SplitOptimizer", "NoisySplit", "MultipleSingleRuns"],
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
    items: ["BO", "BayesOptim", "ParametrizedBO", "PCABO", "NoisyBandit"],
  },
  {
    label: "Other",
    items: ["SPSA", "TBPSA", "ParametrizedTBPSA", "cGA", "VoronoiDE", "AX", "AXP"],
  },
];

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

// Ax-platform / Bayesian. The project's bayesian_ax.py currently only consumes
// random_seed at runtime, but we still expose these so the YAML carries the
// intent and lights up when the integration is enhanced.
export const AX_ALGORITHMS = [
  "AxAuto",        // Ax's default GenerationStrategy (Sobol → BoTorch GP)
  "AxBoTorch",     // Force BoTorch model after init
  "AxSobol",       // Pure quasi-random Sobol baseline
];

export const AX_KWARG_PRESETS: KwargPreset[] = [
  { key: "num_sobol_trials", value: "10", hint: "Initial quasi-random trials before GP kicks in" },
  { key: "acquisition_function", value: "qNoisyExpectedImprovement", hint: "qNEI | qEI | qUCB | qPI" },
  { key: "model_kwargs", value: "", hint: "Free-form: any extra kwargs for BoTorch model" },
];
