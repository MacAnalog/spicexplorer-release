import { create } from "zustand";
import type {
  WizardForm,
  WizardDutParam,
  WizardTestbench,
  WizardTargetSpec,
  ConstraintRow,
  WizardPVTConfig,
} from "@/types/api";

export const WIZARD_STEPS = [
  "basic",
  "pdk",
  "dut",
  "pvt",
  "testbenches",
  "specs",
  "optimizer",
] as const;
export type WizardStepId = (typeof WIZARD_STEPS)[number];

export const STEP_LABELS: Record<WizardStepId, string> = {
  basic: "Basic Info",
  pdk: "PDK Rules",
  dut: "DUT Params",
  pvt: "PVT Corners",
  testbenches: "Testbenches",
  specs: "Target Specs",
  optimizer: "Optimizer",
};

const defaultForm = (): WizardForm => ({
  project: {
    name: "",
    description: "",
    simulator: "ngspice",
    save_sim: false,
    parallel_sim: true,
    ws_root: "",
    netlist: "",
    outdir: "spice/temp_spice_out",
  },
  tech: { name: "", constraints: [] },
  pvt: { active_corner: "", corners: [], model_lib_root: "" },
  dut_params: [],
  testbenches: [],
  target_specs: [],
  optimizer: {
    type: "nevergrad",
    name: "LhsDE",
    budget: 200,
    random_seed: 42,
    lin_min: "0",
    lin_max: "100",
    log_min: "1",
    log_max: "100",
    optimizer_kwargs: [],
  },
});

interface WizardStore {
  form: WizardForm;
  stepIdx: number;

  setStep: (i: number) => void;
  next: () => void;
  back: () => void;
  reset: () => void;
  setForm: (form: WizardForm) => void;

  // top-level updaters
  updateProject: (patch: Partial<WizardForm["project"]>) => void;
  setTechName: (name: string) => void;
  setConstraints: (rows: ConstraintRow[]) => void;
  setPvtConfig: (cfg: WizardPVTConfig) => void;
  setDutParams: (rows: WizardDutParam[]) => void;
  setTestbenches: (tbs: WizardTestbench[]) => void;
  setTargetSpecs: (specs: WizardTargetSpec[]) => void;
  updateOptimizer: (patch: Partial<WizardForm["optimizer"]>) => void;
}

export const useWizardStore = create<WizardStore>((set) => ({
  form: defaultForm(),
  stepIdx: 0,

  setStep: (i) => set({ stepIdx: Math.max(0, Math.min(WIZARD_STEPS.length - 1, i)) }),
  next: () => set((s) => ({ stepIdx: Math.min(WIZARD_STEPS.length - 1, s.stepIdx + 1) })),
  back: () => set((s) => ({ stepIdx: Math.max(0, s.stepIdx - 1) })),
  reset: () => set({ form: defaultForm(), stepIdx: 0 }),
  setForm: (form) => set({ form, stepIdx: 0 }),

  updateProject: (patch) => set((s) => ({ form: { ...s.form, project: { ...s.form.project, ...patch } } })),
  setTechName: (name) => set((s) => ({ form: { ...s.form, tech: { ...s.form.tech, name } } })),
  setConstraints: (rows) => set((s) => ({ form: { ...s.form, tech: { ...s.form.tech, constraints: rows } } })),
  setPvtConfig: (cfg) => set((s) => ({ form: { ...s.form, pvt: cfg } })),
  setDutParams: (rows) => set((s) => ({ form: { ...s.form, dut_params: rows } })),
  setTestbenches: (tbs) => set((s) => ({ form: { ...s.form, testbenches: tbs } })),
  setTargetSpecs: (specs) => set((s) => ({ form: { ...s.form, target_specs: specs } })),
  updateOptimizer: (patch) => set((s) => ({ form: { ...s.form, optimizer: { ...s.form.optimizer, ...patch } } })),
}));
