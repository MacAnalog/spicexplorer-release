import { create } from "zustand";
import { api } from "@/lib/api";
import { adaptCircuit, adaptLibraryData, EMPTY_LIBRARY_DATA, type LibraryData } from "@/lib/library/adapt";
import type { SortMode, SectionNav } from "@/lib/library/selectors";
import type { LibraryCatalogCircuit, LibraryCircuitDetail } from "@/types/api";

/**
 * Reference Library view state + the fetched catalog data. Mirrors the design
 * prototype's top-level component state (tab / selection / filters / sort / register
 * overlay), and additionally owns the data loaded from the analog-db API
 * (`/api/library/*`) — so the Library's self-managed rails (siblings of the center
 * column) read one source without prop-drilling, the selection survives navigating
 * away and back, and the (one-time) fetch is shared across every panel.
 *
 * All catalog content is loaded from the repo via `load()`; nothing is hardcoded.
 * `status` gates the UI: `unavailable` when the analog-db submodule isn't installed
 * (the API answers `available:false`), `error` on a fetch failure.
 */
export type LibraryTab = "home" | "circuits" | "templates" | "testbenches";
export type LibraryStatus = "idle" | "loading" | "ready" | "unavailable" | "error";

/** Multi-select filter arrays that share a generic toggle. */
export type FilterKey = "classSel" | "sourceSel" | "compSel" | "tbClassSel";

interface LibraryStore {
  // ── fetched data ──
  data: LibraryData;
  status: LibraryStatus;
  error: string | null;
  /** Why the catalog is unavailable (the API status `reason`), for the empty state. */
  unavailableReason: string | null;
  /** Catalog schema id + DB root from the API — shown in the library status bar / log. */
  catalogSchema: string;
  dbRoot: string | null;
  detail: LibraryCircuitDetail | null;
  detailId: string | null;
  detailLoading: boolean;
  load: () => Promise<void>;
  /** Fetch one circuit's full detail (datasheet + results) for the datasheet view. */
  fetchDetail: (id: string) => Promise<void>;
  /** Optimistically add a newly-registered circuit to the browse list (the committed
   *  catalog.json won't include it until an offline `analog-db catalog`). */
  addCircuit: (entry: LibraryCatalogCircuit) => void;

  // ── view state ──
  tab: LibraryTab;
  selId: string;
  detailOpen: boolean;
  /** Active analysis index within the selected circuit's datasheet. */
  tbIdx: number;
  tplId: string;
  /** Selected testbench, keyed `class/analysis`. */
  selTb: string;

  classSel: string[];
  sourceSel: string[];
  compSel: string[];
  tbClassSel: string[];
  search: string;
  sort: SortMode;

  /** Library chrome visibility (the fullBleed view owns its own log + right rail,
   *  so it needs its own toggles — same affordance as the shell's StatusBar). */
  logOpen: boolean;
  railOpen: boolean;
  toggleLog: () => void;
  toggleRail: () => void;

  setTab: (tab: LibraryTab) => void;
  openDetail: (id: string) => void;
  goBack: () => void;
  goCircuits: () => void;
  setTbIdx: (i: number) => void;
  setTplId: (id: string) => void;
  setSelTb: (id: string) => void;
  navSection: (nav: SectionNav) => void;

  toggleFilter: (key: FilterKey, val: string) => void;
  clearFilters: () => void;
  setSearch: (v: string) => void;
  setSort: (v: SortMode) => void;
}

export const useLibraryStore = create<LibraryStore>((set, get) => ({
  data: EMPTY_LIBRARY_DATA,
  status: "idle",
  error: null,
  unavailableReason: null,
  catalogSchema: "",
  dbRoot: null,
  detail: null,
  detailId: null,
  detailLoading: false,

  load: async () => {
    const s = get();
    if (s.status === "loading" || s.status === "ready") return; // once
    set({ status: "loading", error: null });
    try {
      const probe = await api.libraryStatus();
      if (!probe.available) {
        set({ status: "unavailable", unavailableReason: probe.reason });
        return;
      }
      const [catalog, results, templates, classes, pdks] = await Promise.all([
        api.libraryCatalog(),
        api.libraryResults(),
        api.libraryTemplates(),
        api.libraryClasses(),
        api.libraryPdks(),
      ]);
      const data = adaptLibraryData(catalog, results, templates, classes.classes, pdks.pdks);
      // keep the initial selection valid against the real catalog
      const haveSel = data.circuits.some((c) => c.id === get().selId);
      set({
        data,
        status: "ready",
        catalogSchema: catalog.schema,
        dbRoot: probe.db_root,
        selId: haveSel ? get().selId : (data.circuits[0]?.id ?? get().selId),
      });
    } catch (e) {
      set({ status: "error", error: e instanceof Error ? e.message : "failed to load the library" });
    }
  },

  fetchDetail: async (id: string) => {
    if (get().detail?.id === id) return; // already have this circuit's detail
    set({ detailLoading: true, detailId: id });
    try {
      const detail = await api.libraryCircuit(id);
      // ignore a stale response if the selection moved on while in flight
      if (get().selId === id) set({ detail, detailLoading: false });
      else set({ detailLoading: false });
    } catch {
      if (get().selId === id) set({ detailLoading: false });
    }
  },

  tab: "home",
  selId: "amp_018_telescopic_cascode",
  detailOpen: false,
  tbIdx: 0,
  tplId: "cm.nmos.cascode",
  selTb: "amplifier/ac_open_loop",

  classSel: [],
  sourceSel: [],
  compSel: [],
  tbClassSel: [],
  search: "",
  sort: "id",
  logOpen: true,
  railOpen: true,
  toggleLog: () => set((s) => ({ logOpen: !s.logOpen })),
  toggleRail: () => set((s) => ({ railOpen: !s.railOpen })),

  setTab: (tab) => set({ tab, detailOpen: false }),
  addCircuit: (entry) =>
    set((s) => {
      const c = adaptCircuit(entry);
      if (s.data.circuits.some((x) => x.id === c.id)) return {};
      return { data: { ...s.data, circuits: [...s.data.circuits, c] } };
    }),

  openDetail: (id) => {
    set({ selId: id, detailOpen: true, tbIdx: 0 });
    void get().fetchDetail(id);
  },
  goBack: () => set({ detailOpen: false, tab: "circuits" }),
  goCircuits: () => set({ tab: "circuits", detailOpen: false }),
  setTbIdx: (tbIdx) => set({ tbIdx }),
  setTplId: (tplId) => set({ tplId }),
  setSelTb: (selTb) => set({ selTb }),

  navSection: (nav) =>
    set(() => {
      switch (nav) {
        case "featured":
          return { tab: "home" as LibraryTab, detailOpen: false };
        case "all":
          return { tab: "circuits" as LibraryTab, detailOpen: false, classSel: [] };
        case "amplifiers":
          return { tab: "circuits" as LibraryTab, detailOpen: false, classSel: ["amplifier"] };
        case "ldos":
          return { tab: "circuits" as LibraryTab, detailOpen: false, classSel: ["ldo"] };
        case "measured":
          return { tab: "circuits" as LibraryTab, detailOpen: false, sort: "results" as SortMode };
        case "templates":
          return { tab: "templates" as LibraryTab, detailOpen: false };
      }
    }),

  toggleFilter: (key, val) =>
    set((s) => {
      const arr = s[key];
      return { [key]: arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val] } as Pick<LibraryStore, FilterKey>;
    }),
  clearFilters: () => set({ classSel: [], sourceSel: [], compSel: [], search: "" }),
  setSearch: (search) => set({ search }),
  setSort: (sort) => set({ sort }),
}));
