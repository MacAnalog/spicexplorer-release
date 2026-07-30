import { create } from "zustand";
import { api } from "@/lib/api";
import type { ProjectMeta, ProjectSummary } from "@/types/api";

interface ProjectStore {
  yaml: string;
  yamlPath: string;
  summary: ProjectSummary | null;
  validationErrors: string[];
  isValid: boolean;
  isApplied: boolean;
  // The active registered project (report.md P3). null = an ad-hoc/edited YAML
  // (Setup load/upload) that isn't tied to a project — its runs land unscoped.
  projectId: string | null;
  projectName: string | null;
  projects: ProjectMeta[];

  setYaml: (yaml: string) => void;
  setYamlPath: (path: string) => void;
  setSummary: (summary: ProjectSummary | null) => void;
  setValidationErrors: (errors: string[]) => void;
  /** Apply an ad-hoc/edited YAML (Setup) — detaches from any registered project. */
  apply: (summary: ProjectSummary, path: string) => void;
  setProjects: (projects: ProjectMeta[]) => void;
  refreshProjects: () => Promise<void>;
  /** Switch to a registered project: load its summary + bind project_id. */
  switchProject: (id: string) => Promise<boolean>;
  /** Rename a project (manifest only — the dir id is stable). Updates the active name. */
  renameProject: (id: string, name: string) => Promise<boolean>;
  /** Soft-delete (recoverable). Detaches the active binding if the deleted project was active. */
  deleteProject: (id: string) => Promise<boolean>;
  /** Fork = copy everything but run history into a new project. Returns the new id. */
  forkProject: (id: string, name?: string) => Promise<string | null>;
  reset: () => void;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  yaml: "",
  yamlPath: "",
  summary: null,
  validationErrors: [],
  isValid: false,
  isApplied: false,
  projectId: null,
  projectName: null,
  projects: [],

  setYaml: (yaml) => set({ yaml }),
  setYamlPath: (yamlPath) => set({ yamlPath }),
  setSummary: (summary) => set({ summary }),
  setValidationErrors: (errors) => set({ validationErrors: errors, isValid: errors.length === 0 }),
  apply: (summary, path) =>
    set({
      summary,
      yamlPath: path,
      isApplied: true,
      isValid: true,
      validationErrors: [],
      // An ad-hoc/edited YAML is not the registered project — clear the binding so a
      // run uses yaml_path (unscoped) rather than silently resolving to project.yaml.
      projectId: null,
      projectName: null,
    }),
  setProjects: (projects) => set({ projects }),
  refreshProjects: async () => {
    try {
      const { projects } = await api.listProjects();
      set({ projects });
    } catch {
      /* best-effort */
    }
  },
  switchProject: async (id) => {
    // A live run belongs to the project we're leaving; tear it down BEFORE rebinding so its SSE
    // events don't stream into the new project's UI and the EventSource isn't orphaned (BUG-B16).
    // stopRun() stops it server-side and records it to history — its run dir/checkpoints survive,
    // so it stays resumable. (Lazy import: runStore imports projectStore, so avoid a static cycle.)
    try {
      const { useRunStore } = await import("@/stores/runStore");
      if (useRunStore.getState().isRunning) useRunStore.getState().stopRun();
    } catch {
      /* best-effort teardown */
    }
    try {
      const d = await api.getProject(id);
      let yaml = "";
      try {
        const r = await fetch(`/api/yaml-text?path=${encodeURIComponent(d.yaml_path)}`);
        if (r.ok) yaml = await r.text();
      } catch {
        /* editor text is best-effort */
      }
      set({
        summary: d.summary,
        yamlPath: d.yaml_path,
        yaml,
        isApplied: true,
        isValid: true,
        validationErrors: [],
        projectId: d.id,
        projectName: (d.manifest?.name as string) ?? d.id,
      });
      return true;
    } catch {
      return false;
    }
  },
  renameProject: async (id, name) => {
    try {
      await api.renameProject(id, name);
      await get().refreshProjects();
      // Keep the active label in sync if we renamed the open project.
      if (get().projectId === id) set({ projectName: name });
      return true;
    } catch {
      return false;
    }
  },
  deleteProject: async (id) => {
    try {
      await api.deleteProject(id);
      await get().refreshProjects();
      // If the active project was deleted, FULLY reset — nulling only id/name would leave
      // isApplied=true with yamlPath/summary still pointing at the now-trashed project.yaml,
      // so a subsequent Start would POST that dead path (unscoped) instead of being blocked.
      if (get().projectId === id) {
        get().reset();
        // The backend already stopped the run (delete_project → stop_runs_for); also close the
        // orphaned client EventSource + clear the run UI so it doesn't show a phantom "running"
        // run for a project that no longer exists (BUG-B44).
        try {
          const { useRunStore } = await import("@/stores/runStore");
          useRunStore.getState().reset();
        } catch {
          /* best-effort teardown */
        }
      }
      return true;
    } catch {
      return false;
    }
  },
  forkProject: async (id, name) => {
    try {
      const { id: newId } = await api.forkProject(id, name);
      await get().refreshProjects();
      return newId;
    } catch {
      return null;
    }
  },
  reset: () =>
    set({
      yaml: "", yamlPath: "", summary: null, validationErrors: [], isValid: false,
      isApplied: false, projectId: null, projectName: null,
    }),
}));
