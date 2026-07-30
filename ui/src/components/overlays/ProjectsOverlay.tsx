"use client";
import { useEffect, useRef, useState } from "react";
import {
  FolderOpen, Plus, Beaker, Loader2, Pencil, GitFork, Trash2, Check, X, Undo2, Trash,
} from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { useProjectStore } from "@/stores/projectStore";
import { api } from "@/lib/api";
import { cn, formatEng } from "@/lib/utils";
import type { ExampleMeta, TrashItem } from "@/types/api";

/**
 * ⌘P Projects overlay (report.md P3/P4) — the project registry surface. A project IS a
 * directory under WORK_ROOT/projects. Lists existing projects (click to switch, hover to
 * rename/fork/delete), loads a demo AS a new project (copy-on-load), creates a new
 * (example-structured) project, and exposes the soft-delete trash (restore). NOT a new
 * ActivityBar view, so the nav 1..8 shortcut invariant is preserved.
 */
export function ProjectsOverlay() {
  const projectsOpen = useUIStore((s) => s.projectsOpen);
  const closeProjects = useUIStore((s) => s.closeProjects);
  const openWizard = useUIStore((s) => s.openWizard);
  const {
    projects, projectId, refreshProjects, switchProject,
    renameProject, deleteProject, forkProject,
  } = useProjectStore();

  const [query, setQuery] = useState("");
  const [examples, setExamples] = useState<ExampleMeta[]>([]);
  const [trash, setTrash] = useState<TrashItem[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);
  // Per-row UI state: which project is being renamed (+ the draft) and which is armed to delete.
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [trashOpen, setTrashOpen] = useState(false);
  const [confirmPurgeId, setConfirmPurgeId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const refreshTrash = () =>
    api.listTrash().then((r) => setTrash(r.trash.filter((t) => t.kind === "project"))).catch(() => setTrash([]));

  useEffect(() => {
    if (!projectsOpen) return;
    setQuery("");
    setNewName("");
    setError(null);
    setEditingId(null);
    setConfirmDeleteId(null);
    void refreshProjects();
    api.listExamples().then((r) => setExamples(r.examples)).catch(() => setExamples([]));
    void refreshTrash();
    requestAnimationFrame(() => inputRef.current?.focus());
  }, [projectsOpen, refreshProjects]);

  if (!projectsOpen) return null;

  const q = query.trim().toLowerCase();
  const filteredProjects = projects.filter((p) => p.name.toLowerCase().includes(q));
  const filteredExamples = examples.filter((e) => e.name.toLowerCase().includes(q));

  const doSwitch = async (id: string) => {
    setBusy(id);
    setError(null);
    const ok = await switchProject(id);
    setBusy(null);
    if (ok) closeProjects();
    else setError("Failed to load project.");
  };

  const doLoadExample = async (e: ExampleMeta) => {
    setBusy(e.key);
    setError(null);
    try {
      const { id } = await api.fromExample(e.key, e.name);
      await refreshProjects();
      const ok = await switchProject(id);
      if (ok) closeProjects();
      // Created on disk but failed to open — say so instead of a silent no-op (which invites a
      // retry → duplicate projects) (BUG-B52).
      else setError("Loaded the example, but failed to open it — it's in your projects list.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load example.");
    } finally {
      setBusy(null);
    }
  };

  const doCreate = async () => {
    const name = newName.trim();
    if (!name) return;
    setBusy("__new__");
    setError(null);
    try {
      const { id } = await api.createProject(name);
      await refreshProjects();
      const ok = await switchProject(id);
      if (ok) closeProjects();
      else setError("Created the project, but failed to open it — it's in your projects list.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project.");
    } finally {
      setBusy(null);
    }
  };

  const startRename = (id: string, current: string) => {
    setConfirmDeleteId(null);
    setEditingId(id);
    setEditName(current);
  };

  const commitRename = async (id: string) => {
    const name = editName.trim();
    if (!name) { setEditingId(null); return; }
    setBusy(id);
    setError(null);
    const ok = await renameProject(id, name);
    setBusy(null);
    setEditingId(null);
    if (!ok) setError("Rename failed.");
  };

  const doFork = async (id: string) => {
    setBusy(id);
    setError(null);
    try {
      const newId = await forkProject(id);
      if (!newId) { setError("Fork failed."); return; }
      const ok = await switchProject(newId);
      if (ok) closeProjects();
      else setError("Forked, but failed to open the new project.");
    } finally {
      setBusy(null);
    }
  };

  const doDelete = async (id: string) => {
    setBusy(id);
    setError(null);
    const ok = await deleteProject(id);
    setBusy(null);
    setConfirmDeleteId(null);
    if (!ok) setError("Delete failed.");
    else void refreshTrash();
  };

  const doPurge = async (trashId: string) => {
    setBusy(`purge:${trashId}`);
    setError(null);
    try {
      await api.purgeTrash(trashId);
      setTrash((t) => t.filter((x) => x.trash_id !== trashId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Permanent delete failed.");
    } finally {
      setBusy(null);
      setConfirmPurgeId(null);
    }
  };

  const doRestore = async (trashId: string) => {
    setBusy(trashId);
    setError(null);
    try {
      await api.restoreTrash(trashId);
      await refreshProjects();
      await refreshTrash();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Restore failed.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-[10vh]"
      onClick={closeProjects}
      role="dialog"
      aria-modal="true"
      aria-label="Projects"
    >
      <div
        className="flex max-h-[78vh] w-[640px] max-w-[92vw] flex-col overflow-hidden rounded-lg border border-border bg-panel shadow-soft"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search projects and examples…"
          aria-label="Search projects"
          className="w-full border-b border-border bg-transparent px-4 py-3 text-sm text-fg outline-hidden placeholder:text-faint"
        />

        <div className="min-h-0 flex-1 overflow-y-auto py-1">
          {/* Projects (the registry) */}
          <div className="px-4 pb-1 pt-2 text-[10px] font-medium uppercase tracking-wider text-faint">
            Projects ({projects.length})
          </div>
          {filteredProjects.length === 0 && (
            <div className="px-4 py-2 text-[12px] text-faint">No projects yet — create one or load a demo below.</div>
          )}
          {filteredProjects.map((p) => {
            const isEditing = editingId === p.id;
            const isConfirming = confirmDeleteId === p.id;
            return (
              <div
                key={p.id}
                className={cn(
                  "group flex items-center justify-between gap-2 px-4 py-1.5 text-[13px] transition",
                  p.id === projectId ? "bg-primary-soft" : "hover:bg-hairline",
                )}
              >
                {isEditing ? (
                  <div className="flex min-w-0 flex-1 items-center gap-2">
                    <FolderOpen className="h-3.5 w-3.5 shrink-0 text-faint" />
                    <input
                      autoFocus
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") void commitRename(p.id);
                        if (e.key === "Escape") setEditingId(null);
                      }}
                      className="min-w-0 flex-1 rounded-sm border border-border bg-transparent px-1.5 py-0.5 text-[13px] text-fg outline-hidden"
                      aria-label="Rename project"
                    />
                    <button type="button" onClick={() => void commitRename(p.id)} title="Save"
                      className="shrink-0 rounded-sm p-1 text-primary hover:bg-hairline">
                      <Check className="h-3.5 w-3.5" />
                    </button>
                    <button type="button" onClick={() => setEditingId(null)} title="Cancel"
                      className="shrink-0 rounded-sm p-1 text-muted hover:bg-hairline">
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => doSwitch(p.id)}
                      className={cn(
                        "flex min-w-0 flex-1 items-center gap-2 text-left",
                        p.id === projectId ? "text-primary" : "text-fg",
                      )}
                    >
                      <FolderOpen className="h-3.5 w-3.5 shrink-0 text-faint" />
                      <span className="truncate">{p.name}</span>
                      <span className="shrink-0 rounded-sm bg-hairline px-1.5 text-[10px] text-muted">{p.source}</span>
                    </button>
                    {isConfirming ? (
                      <span className="flex shrink-0 items-center gap-1 text-[11px] text-danger">
                        Delete?
                        <button type="button" onClick={() => void doDelete(p.id)} title="Confirm delete"
                          className="rounded-sm p-1 hover:bg-danger-soft">
                          {busy === p.id ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Check className="h-3.5 w-3.5" />}
                        </button>
                        <button type="button" onClick={() => setConfirmDeleteId(null)} title="Cancel"
                          className="rounded-sm p-1 text-muted hover:bg-hairline">
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </span>
                    ) : (
                      <span className="flex shrink-0 items-center gap-2">
                        <span className="flex items-center gap-2 font-mono text-[10px] text-muted">
                          {busy === p.id && <Loader2 className="h-3 w-3 animate-spin" />}
                          {p.run_count} run{p.run_count === 1 ? "" : "s"}
                          {p.best_score != null && <> · best {formatEng(p.best_score)}</>}
                        </span>
                        <span className="flex items-center gap-0.5 opacity-0 transition group-hover:opacity-100">
                          <button type="button" onClick={() => startRename(p.id, p.name)} title="Rename"
                            className="rounded-sm p-1 text-muted hover:bg-hairline hover:text-fg">
                            <Pencil className="h-3.5 w-3.5" />
                          </button>
                          <button type="button" onClick={() => void doFork(p.id)} title="Fork (copy without run history)"
                            className="rounded-sm p-1 text-muted hover:bg-hairline hover:text-fg">
                            <GitFork className="h-3.5 w-3.5" />
                          </button>
                          <button type="button" onClick={() => { setEditingId(null); setConfirmDeleteId(p.id); }} title="Delete"
                            className="rounded-sm p-1 text-muted hover:bg-danger-soft hover:text-danger">
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </span>
                      </span>
                    )}
                  </>
                )}
              </div>
            );
          })}

          {/* Examples (load demo as project) */}
          <div className="px-4 pb-1 pt-3 text-[10px] font-medium uppercase tracking-wider text-faint">
            Load a demo as a project
          </div>
          {filteredExamples.map((e) => (
            <button
              key={e.key}
              type="button"
              onClick={() => doLoadExample(e)}
              title={e.description ?? undefined}
              className="flex w-full items-center justify-between gap-3 px-4 py-1.5 text-left text-[13px] text-fg transition hover:bg-hairline"
            >
              <span className="flex min-w-0 flex-1 items-baseline gap-2">
                <Beaker className="h-3.5 w-3.5 shrink-0 self-center text-faint" />
                {/* Same treatment as the project rows: the name truncates (long
                    generated demo names must never widen the overlay). Capped so
                    the description keeps a slice of the row. */}
                <span className="max-w-[62%] flex-none truncate">{e.name}</span>
                {e.description && (
                  <span className="min-w-0 flex-1 truncate text-[11px] text-faint">
                    {e.description}
                  </span>
                )}
              </span>
              <span className="shrink-0 font-mono text-[10px] text-muted">
                {busy === e.key ? <Loader2 className="h-3 w-3 animate-spin" /> : "copy →"}
              </span>
            </button>
          ))}

          {/* Trash — collapsed by default; expand to restore or delete forever. */}
          {trash.length > 0 && (
            <>
              <button
                type="button"
                onClick={() => setTrashOpen((v) => !v)}
                className="flex w-full items-center gap-1.5 px-4 pb-1 pt-3 text-left text-[10px] font-medium uppercase tracking-wider text-faint transition hover:text-muted"
              >
                <Trash className="h-3 w-3" /> Recently deleted ({trash.length})
                <span className="font-mono normal-case">{trashOpen ? "▾ hide" : "▸ show"}</span>
              </button>
              {trashOpen &&
                trash.map((t) => (
                  <div
                    key={t.trash_id}
                    className="flex items-center justify-between gap-3 px-4 py-1.5 text-[13px] text-muted"
                  >
                    <span className="flex min-w-0 items-center gap-2">
                      <Trash2 className="h-3.5 w-3.5 shrink-0 text-faint" />
                      <span className="truncate line-through decoration-faint">{t.name}</span>
                      <span className="shrink-0 font-mono text-[10px] text-faint">{t.deleted}</span>
                    </span>
                    <span className="flex shrink-0 items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => void doRestore(t.trash_id)}
                        title="Restore"
                        className="inline-flex items-center gap-1 rounded-sm border border-border px-2 py-0.5 text-[11px] text-fg hover:bg-hairline"
                      >
                        {busy === t.trash_id ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <Undo2 className="h-3 w-3" />
                        )}
                        Restore
                      </button>
                      {confirmPurgeId === t.trash_id ? (
                        <button
                          type="button"
                          onClick={() => void doPurge(t.trash_id)}
                          title="This permanently deletes the files — no undo"
                          className="inline-flex items-center gap-1 rounded-sm bg-danger px-2 py-0.5 text-[11px] text-white hover:bg-[#b91c1c]"
                        >
                          {busy === `purge:${t.trash_id}` ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <Trash2 className="h-3 w-3" />
                          )}
                          Forever?
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setConfirmPurgeId(t.trash_id)}
                          title="Delete forever (asks to confirm)"
                          className="inline-flex items-center gap-1 rounded-sm border border-danger/40 px-2 py-0.5 text-[11px] text-danger hover:bg-danger-soft"
                        >
                          <Trash2 className="h-3 w-3" />
                          Delete
                        </button>
                      )}
                    </span>
                  </div>
                ))}
            </>
          )}
        </div>

        {error && (
          <div className="border-t border-border bg-danger-soft px-4 py-1.5 text-[11px] text-danger">{error}</div>
        )}

        {/* Footer: new project (= a new directory) + wizard */}
        <div className="flex items-center gap-2 border-t border-border px-3 py-2">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") void doCreate(); }}
            placeholder="New project name…"
            aria-label="New project name"
            className="min-w-0 flex-1 rounded-sm border border-border bg-transparent px-2 py-1 text-[12px] text-fg outline-hidden placeholder:text-faint"
          />
          <button
            type="button"
            onClick={doCreate}
            disabled={!newName.trim() || busy === "__new__"}
            className="inline-flex shrink-0 items-center gap-1 rounded-sm border border-border px-2 py-1 text-[12px] text-fg hover:bg-hairline disabled:opacity-40"
          >
            <Plus className="h-3 w-3" /> Create
          </button>
          <button
            type="button"
            onClick={() => { closeProjects(); openWizard(); }}
            className="shrink-0 rounded-sm border border-border px-2 py-1 text-[12px] text-muted hover:bg-hairline hover:text-fg"
            title="Author a project YAML in the wizard"
          >
            Wizard…
          </button>
        </div>
      </div>
    </div>
  );
}
