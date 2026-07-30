import { create } from "zustand";
import type { CheckpointData, CheckpointMeta, EnvelopeEntry } from "@/types/api";

interface ExplorerStore {
  availableCheckpoints: CheckpointMeta[];
  runA: CheckpointData | null;
  runB: CheckpointData | null;
  envelopeA: EnvelopeEntry[] | null;
  scatterMetricX: string;
  scatterMetricY: string;
  selectedMetric: string;

  setAvailableCheckpoints: (list: CheckpointMeta[]) => void;
  setRunA: (d: CheckpointData | null) => void;
  setRunB: (d: CheckpointData | null) => void;
  setEnvelopeA: (e: EnvelopeEntry[] | null) => void;
  setScatterMetrics: (x: string, y: string) => void;
  setSelectedMetric: (m: string) => void;
}

export const useExplorerStore = create<ExplorerStore>((set) => ({
  availableCheckpoints: [],
  runA: null,
  runB: null,
  envelopeA: null,
  scatterMetricX: "ugf",
  scatterMetricY: "i(idd_total)",
  selectedMetric: "ugf",

  setAvailableCheckpoints: (list) => set({ availableCheckpoints: list }),
  setRunA: (d) => set({ runA: d }),
  setRunB: (d) => set({ runB: d }),
  setEnvelopeA: (e) => set({ envelopeA: e }),
  setScatterMetrics: (x, y) => set({ scatterMetricX: x, scatterMetricY: y }),
  setSelectedMetric: (m) => set({ selectedMetric: m }),
}));
