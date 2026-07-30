import { create } from "zustand";
import { api } from "@/lib/api";
import { classReg, metricDefSpec } from "@/lib/library/data";
import type { CircuitClass } from "@/lib/library/types";
import {
  INITIAL_WIZ_FORM,
  SIM_PARAM_TEMPLATES,
  OP_ORDER,
  circuitPayload,
  tplPortsFor,
  flowLength,
  type WizForm,
  type WizKind,
  type WizStringKey,
  type WizArrayKey,
  type WizBoolKey,
} from "@/lib/library/wizard";
import { useLibraryStore } from "./libraryStore";

/**
 * Register-wizard state — the prototype's `wizForm` + step index, with the
 * mutation methods (`setClass`/`setTbSimType`/row editors) ported as actions.
 * Separate from `libraryStore` (browse state) so the large form model is
 * self-contained; the overlay reads derived view-data from `lib/library/wizard`.
 */
const DEFAULT_TB_PARAMS: [string, string][] = [["VDD", "1.5"], ["VCM", "0.8"], ["IBIAS", "20u"], ["CL", "50f"]];

interface LibraryWizardStore {
  open: boolean;
  step: number;
  form: WizForm;
  registering: boolean;
  registerError: string | null;

  openWizard: (kind?: WizKind) => void;
  close: () => void;
  next: () => void;
  back: () => void;
  goStep: (i: number) => void;
  /** Submit the form. The circuit kind POSTs a draft to /api/library/circuits and inserts it into
   *  the browse list; template/testbench kinds just close (no write-back yet). */
  register: () => Promise<void>;

  setKind: (k: WizKind) => void;
  /** Set a string field (covers the class-driven identity fields too). */
  setStr: (key: WizStringKey, value: string) => void;
  setBool: (key: WizBoolKey, value: boolean) => void;
  toggleArr: (key: WizArrayKey, value: string) => void;
  pickLicense: (license: string) => void;

  setClass: (klass: CircuitClass) => void;
  setTfamily: (family: string) => void;
  setTbSimType: (t: string) => void;

  addMetric: (key: string) => void;
  removeMetric: (key: string) => void;
  setMetricVal: (key: string, val: string) => void;
  cycleMetricOp: (key: string) => void;

  addTb: () => void;
  removeTb: (a: string) => void;

  setTbParam: (i: number, which: 0 | 1, v: string) => void;
  addTbParam: () => void;
  removeTbParam: (i: number) => void;

  setPort: (i: number, which: 0 | 1, v: string) => void;
  addPort: () => void;
  removePort: (i: number) => void;
}

export const useLibraryWizardStore = create<LibraryWizardStore>((set, get) => ({
  open: false,
  step: 0,
  form: INITIAL_WIZ_FORM,
  registering: false,
  registerError: null,

  openWizard: (kind) => set((s) => ({ open: true, step: 0, registerError: null, form: kind ? { ...s.form, kind } : s.form })),
  close: () => set({ open: false, registerError: null }),

  register: async () => {
    const { form } = get();
    // only the circuit kind has a backend write path today (POST /library/circuits)
    if (form.kind !== "circuit") {
      set({ open: false });
      return;
    }
    set({ registering: true, registerError: null });
    try {
      const res = await api.createCircuit(circuitPayload(form));
      useLibraryStore.getState().addCircuit(res.circuit);
      set({ registering: false, open: false });
      useLibraryStore.getState().openDetail(res.id); // jump to the new draft's datasheet
    } catch (e) {
      set({ registering: false, registerError: e instanceof Error ? e.message : "failed to register" });
    }
  },
  next: () => set((s) => ({ step: Math.min(flowLength(s.form.kind) - 1, s.step + 1) })),
  back: () => set((s) => ({ step: Math.max(0, s.step - 1) })),
  goStep: (i) => set({ step: i }),

  setKind: (kind) => set((s) => ({ step: 0, form: { ...s.form, kind } })),
  // The computed-key spreads below are sound (key is constrained to the matching
  // value-kind), but TS can't prove the assignment across WizForm's literal-union
  // string fields, so assert the result type at the boundary.
  setStr: (key, value) => set((s) => ({ form: { ...s.form, [key]: value } as WizForm })),
  setBool: (key, value) => set((s) => ({ form: { ...s.form, [key]: value } as WizForm })),
  toggleArr: (key, value) =>
    set((s) => {
      const arr = s.form[key];
      return { form: { ...s.form, [key]: arr.includes(value) ? arr.filter((x) => x !== value) : [...arr, value] } as WizForm };
    }),
  pickLicense: (license) => set((s) => ({ form: { ...s.form, license, licenseOpen: false } })),

  setClass: (klass) =>
    set((s) => {
      const r = classReg[klass];
      const metricRows = r.defM.map((k) => ({ key: k, op: metricDefSpec[k]?.op ?? "min", val: metricDefSpec[k]?.v ?? "" }));
      return { form: { ...s.form, klass, analyses: [...r.defAn], customAnalyses: [], metricRows } };
    }),
  setTfamily: (family) => set((s) => ({ form: { ...s.form, tfamily: family, tportRows: tplPortsFor(family) } })),
  setTbSimType: (t) => set((s) => ({ form: { ...s.form, tbSimType: t, tbParamRows: (SIM_PARAM_TEMPLATES[t] ?? DEFAULT_TB_PARAMS).map((p) => [p[0], p[1]] as [string, string]) } })),

  addMetric: (key) =>
    set((s) => {
      if (s.form.metricRows.some((r) => r.key === key)) return {};
      return { form: { ...s.form, metricRows: [...s.form.metricRows, { key, op: metricDefSpec[key]?.op ?? "min", val: metricDefSpec[key]?.v ?? "" }] } };
    }),
  removeMetric: (key) => set((s) => ({ form: { ...s.form, metricRows: s.form.metricRows.filter((r) => r.key !== key) } })),
  setMetricVal: (key, val) => set((s) => ({ form: { ...s.form, metricRows: s.form.metricRows.map((r) => (r.key === key ? { ...r, val } : r)) } })),
  cycleMetricOp: (key) =>
    set((s) => ({
      form: {
        ...s.form,
        metricRows: s.form.metricRows.map((r) => (r.key === key ? { ...r, op: OP_ORDER[(OP_ORDER.indexOf(r.op) + 1) % OP_ORDER.length] } : r)),
      },
    })),

  addTb: () =>
    set((s) => {
      const n = s.form.newTb.trim();
      if (!n) return {};
      const customAnalyses = s.form.customAnalyses.includes(n) ? s.form.customAnalyses : [...s.form.customAnalyses, n];
      const analyses = s.form.analyses.includes(n) ? s.form.analyses : [...s.form.analyses, n];
      return { form: { ...s.form, customAnalyses, analyses, newTb: "" } };
    }),
  removeTb: (a) => set((s) => ({ form: { ...s.form, customAnalyses: s.form.customAnalyses.filter((x) => x !== a), analyses: s.form.analyses.filter((x) => x !== a) } })),

  setTbParam: (i, which, v) => set((s) => ({ form: { ...s.form, tbParamRows: s.form.tbParamRows.map((p, j) => (j === i ? (which === 0 ? [v, p[1]] : [p[0], v]) : p)) } })),
  addTbParam: () => set((s) => ({ form: { ...s.form, tbParamRows: [...s.form.tbParamRows, ["PARAM", "0"]] } })),
  removeTbParam: (i) => set((s) => ({ form: { ...s.form, tbParamRows: s.form.tbParamRows.filter((_, j) => j !== i) } })),

  setPort: (i, which, v) => set((s) => ({ form: { ...s.form, tportRows: s.form.tportRows.map((p, j) => (j === i ? (which === 0 ? [v, p[1]] : [p[0], v]) : p)) } })),
  addPort: () => set((s) => ({ form: { ...s.form, tportRows: [...s.form.tportRows, ["port", "net"]] } })),
  removePort: (i) => set((s) => ({ form: { ...s.form, tportRows: s.form.tportRows.filter((_, j) => j !== i) } })),
}));
