"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ChevronRight, ArrowUp, ArrowDown, FileCode, Upload, FileInput } from "lucide-react";
import { useProjectStore } from "@/stores/projectStore";
import { api } from "@/lib/api";
import { parseXschem } from "@/lib/xschem/parser";
import { isSubcircuit } from "@/lib/xschem/render";
import type { XschemFile, Instance } from "@/lib/xschem/types";
import { SchematicViewer } from "@/components/schematic/SchematicViewer";
import { DeviceInspector } from "@/components/schematic/DeviceInspector";

interface LoadedSchematic {
  path: string;
  name: string;
  parsed: XschemFile;
}

export function SchematicTab() {
  const { yamlPath, isApplied, summary } = useProjectStore();
  const [projectFiles, setProjectFiles] = useState<{ path: string; name: string }[]>([]);
  const [projectXschemDir, setProjectXschemDir] = useState<string | null>(null);
  const [historyStack, setHistoryStack] = useState<LoadedSchematic[]>([]);
  const [current, setCurrent] = useState<LoadedSchematic | null>(null);
  const [symbols, setSymbols] = useState<Map<string, XschemFile>>(new Map());
  /** Symbol refs whose sibling .sch is known to exist — these are clickable for hierarchy. */
  const [navigableSymrefs, setNavigableSymrefs] = useState<Set<string>>(new Set());
  /** Resolved symbol .sym paths, keyed by symref — used to compute sibling .sch path. */
  const [symPaths, setSymPaths] = useState<Map<string, string>>(new Map());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  /** Informational banner (e.g. devices skipped while generating from a netlist). */
  const [notice, setNotice] = useState<string | null>(null);

  // Discover .sch files in the project's xschem/ dir when a project is applied.
  useEffect(() => {
    if (!isApplied || !yamlPath) {
      setProjectFiles([]);
      setProjectXschemDir(null);
      return;
    }
    api
      .xschemProject(yamlPath)
      .then((r) => {
        setProjectFiles(r.files);
        setProjectXschemDir(r.xschem_dir);
      })
      .catch(() => {
        setProjectFiles([]);
        setProjectXschemDir(null);
      });
  }, [isApplied, yamlPath]);

  // Absolute path of the YAML-declared schematic, if any (`project.schematic` joined to `ws_root`).
  const yamlSchematicPath = useMemo(() => {
    if (!isApplied || !summary?.schematic || !summary.ws_root) return null;
    const root = summary.ws_root.replace(/\/+$/, "");
    const rel = summary.schematic.replace(/^\/+/, "");
    return `${root}/${rel}`;
  }, [isApplied, summary?.schematic, summary?.ws_root]);
  const lastAutoLoadedRef = useRef<string | null>(null);

  // Surface PDK-missing degradation: count device symbols that failed to resolve
  // (rendered as red "?" placeholders) — usually because the xschem symbol
  // library / PDK isn't reachable by the backend, instead of failing silently.
  const missingSymbolCount = useMemo(() => {
    if (!current) return 0;
    const refs = new Set(current.parsed.instances.map((i) => i.symref));
    let missing = 0;
    for (const ref of refs) if (!symbols.has(ref)) missing += 1;
    return missing;
  }, [current, symbols]);

  /** Parse text, resolve every referenced symbol, probe navigable subcircuits, then commit. */
  const loadFromContent = useCallback(
    async (
      content: string,
      displayPath: string,
      displayName: string,
      pushHistory: boolean,
      /** Absolute path of the loaded file, used as `base` for relative symbol lookups.
       *  Null for uploads (only library-rooted refs like `devices/foo.sym` will resolve). */
      resolveBase: string | null,
    ) => {
      setLoading(true);
      setError(null);
      try {
        const parsed = parseXschem(content);
        const loaded: LoadedSchematic = { path: displayPath, name: displayName, parsed };

        // Resolve unique symbol references in parallel.
        const uniqueRefs = Array.from(new Set(parsed.instances.map((i) => i.symref)));
        const results = await Promise.all(
          uniqueRefs.map(async (ref) => {
            try {
              const r = await api.xschemResolve(ref, resolveBase ?? undefined);
              return { ref, parsed: parseXschem(r.content), path: r.path };
            } catch {
              return null;
            }
          }),
        );
        const symMap = new Map<string, XschemFile>();
        const symPathMap = new Map<string, string>();
        for (const r of results) {
          if (!r) continue;
          symMap.set(r.ref, r.parsed);
          symPathMap.set(r.ref, r.path);
        }

        // Probe sibling .sch for each subcircuit symbol — these become navigable.
        const navigable = new Set<string>();
        const subcircuitCandidates = uniqueRefs.filter((ref) => {
          const sym = symMap.get(ref);
          return sym && isSubcircuit(sym);
        });
        await Promise.all(
          subcircuitCandidates.map(async (ref) => {
            const symPath = symPathMap.get(ref);
            if (!symPath) return;
            const candidate = symPath.replace(/\.sym$/, ".sch");
            try {
              await api.xschemFile(candidate);
              navigable.add(ref);
            } catch {
              /* no sibling .sch */
            }
          }),
        );

        setSymbols(symMap);
        setSymPaths(symPathMap);
        setNavigableSymrefs(navigable);
        if (pushHistory && current) {
          // Dedup: if the top of the stack is already this path, skip — protects against
          // closure-captured duplicate pushes when the user clicks multiple instances rapidly.
          setHistoryStack((s) =>
            s.length > 0 && s[s.length - 1].path === current.path ? s : [...s, current],
          );
        }
        setCurrent(loaded);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    },
    [current],
  );

  /** Load by absolute path (project schematics + hierarchy navigation). */
  const loadSchematic = useCallback(
    async (path: string, name: string, pushHistory: boolean) => {
      try {
        const res = await api.xschemFile(path);
        await loadFromContent(res.content, res.path, name, pushHistory, res.path);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
        setLoading(false);
      }
    },
    [loadFromContent],
  );

  // Auto-load the YAML-declared schematic when a project is applied and the path hasn't been
  // auto-loaded yet. Re-triggers when switching to a different project.
  useEffect(() => {
    if (!yamlSchematicPath || lastAutoLoadedRef.current === yamlSchematicPath) return;
    lastAutoLoadedRef.current = yamlSchematicPath;
    const name = yamlSchematicPath.split("/").pop() ?? yamlSchematicPath;
    void loadSchematic(yamlSchematicPath, name, false);
  }, [yamlSchematicPath, loadSchematic]);

  const handleNavigateInto = useCallback(
    async (inst: Instance) => {
      if (loading) return; // Ignore clicks while a previous load is in flight.
      const symPath = symPaths.get(inst.symref);
      if (!symPath) return;
      const candidate = symPath.replace(/\.sym$/, ".sch");
      const stem = inst.symref.split("/").pop()?.replace(/\.sym$/, "") ?? inst.symref;
      const childName = `${stem}.sch${inst.attrs["name"] ? ` (${inst.attrs["name"]})` : ""}`;
      await loadSchematic(candidate, childName, true);
    },
    [loading, symPaths, loadSchematic],
  );

  const handleBack = useCallback(() => {
    setHistoryStack((stack) => {
      if (stack.length === 0) return stack;
      const prev = stack[stack.length - 1];
      void loadSchematic(prev.path, prev.name, false).then(() => {
        // Drop the head we just restored.
      });
      return stack.slice(0, -1);
    });
  }, [loadSchematic]);

  const handleClear = useCallback(() => {
    setCurrent(null);
    setHistoryStack([]);
    setSymbols(new Map());
    setSymPaths(new Map());
    setNavigableSymrefs(new Set());
    setError(null);
  }, []);

  const uploadInputRef = useRef<HTMLInputElement | null>(null);
  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.toLowerCase().endsWith(".sch")) {
        setError("Upload requires a .sch file");
        return;
      }
      try {
        const text = await file.text();
        // Reset hierarchy state: uploaded files start a fresh, isolated browse session.
        setHistoryStack([]);
        setCurrent(null);
        setNotice(null);
        await loadFromContent(text, `<uploaded>/${file.name}`, file.name, false, null);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [loadFromContent],
  );

  // Generate a schematic from a SPICE netlist: POST it to the backend, then load the returned .sch
  // through the same render path as an upload (symbols resolve via the PDK / xschem libraries).
  const netlistInputRef = useRef<HTMLInputElement | null>(null);
  const handleNetlistUpload = useCallback(
    async (file: File) => {
      setError(null);
      setNotice(null);
      try {
        const text = await file.text();
        const stem = file.name.replace(/\.[^.]+$/, "") || file.name;
        setHistoryStack([]);
        setCurrent(null);
        setLoading(true);
        const res = await api.xschemFromNetlist({ netlist_text: text, name: stem, render: "none" });
        if (res.warnings.length > 0) {
          const head = res.warnings.slice(0, 3).join("; ");
          setNotice(
            `${res.device_count} device${res.device_count === 1 ? "" : "s"} drawn; ` +
              `${res.warnings.length} skipped — ${head}${res.warnings.length > 3 ? " …" : ""}`,
          );
        }
        const path = res.sch_path ?? `<generated>/${stem}.sch`;
        await loadFromContent(res.sch_content, path, `${stem}.sch`, false, res.sch_path);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    },
    [loadFromContent],
  );

  const breadcrumb = useMemo(() => {
    const items = [...historyStack.map((h) => h.name)];
    if (current) items.push(current.name);
    return items;
  }, [historyStack, current]);

  // Subcircuit instances in the current schematic, in instance-order.
  const descendableInstances = useMemo(() => {
    if (!current) return [] as { inst: Instance; label: string }[];
    return current.parsed.instances
      .map((inst, idx) => ({ inst, idx }))
      .filter(({ inst }) => navigableSymrefs.has(inst.symref))
      .map(({ inst, idx }) => {
        const stem = inst.symref.split("/").pop()?.replace(/\.sym$/, "") ?? inst.symref;
        const name = inst.attrs["name"];
        const label = name ? `${name} — ${stem}` : `#${idx} — ${stem}`;
        return { inst, label };
      });
  }, [current, navigableSymrefs]);

  return (
    <div className="flex h-full min-h-0 flex-col">
      {/* Toolbar */}
      <div className="flex shrink-0 items-center gap-3 border-b border-border bg-panel px-4 py-2 text-sm">
        <div className="flex items-center gap-1">
          <button
            type="button"
            title="Go up to parent schematic"
            onClick={handleBack}
            disabled={historyStack.length === 0 || loading}
            className="flex items-center gap-1 rounded-sm border border-border bg-bg px-2 py-1 text-fg disabled:opacity-40"
          >
            <ArrowUp className="h-3.5 w-3.5" /> Up
          </button>

          {descendableInstances.length > 0 ? (
            <label className="flex items-center" title="Descend into a subcircuit instance">
              <span className="sr-only">Down into</span>
              <div className="relative">
                <select
                  className="appearance-none rounded-sm border border-border bg-bg py-1 pl-7 pr-6 text-fg disabled:opacity-40"
                  value=""
                  disabled={loading}
                  onChange={(e) => {
                    const idx = Number(e.target.value);
                    const entry = descendableInstances[idx];
                    if (entry) void handleNavigateInto(entry.inst);
                  }}
                >
                  <option value="" disabled>
                    Down…
                  </option>
                  {descendableInstances.map((d, i) => (
                    <option key={i} value={i}>
                      {d.label}
                    </option>
                  ))}
                </select>
                <ArrowDown
                  className="pointer-events-none absolute left-1.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-fg"
                  aria-hidden
                />
              </div>
            </label>
          ) : (
            <button
              type="button"
              title="No subcircuits in this schematic"
              disabled
              className="flex items-center gap-1 rounded-sm border border-border bg-bg px-2 py-1 text-fg opacity-40"
            >
              <ArrowDown className="h-3.5 w-3.5" /> Down
            </button>
          )}
        </div>

        <div className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto whitespace-nowrap text-xs text-muted">
          {breadcrumb.length === 0 ? (
            <span>No schematic loaded</span>
          ) : (
            breadcrumb.map((name, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <ChevronRight className="h-3 w-3" />}
                <span className={i === breadcrumb.length - 1 ? "text-fg" : ""}>{name}</span>
              </span>
            ))
          )}
        </div>

        {projectFiles.length > 0 && (
          <label className="flex items-center gap-2 text-xs text-muted">
            Open
            <select
              aria-label="Open schematic"
              className="rounded-sm border border-border bg-bg px-2 py-1 text-fg"
              value={current?.path ?? ""}
              disabled={loading}
              onChange={(e) => {
                const f = projectFiles.find((p) => p.path === e.target.value);
                if (f) {
                  handleClear();
                  void loadSchematic(f.path, f.name, false);
                }
              }}
            >
              <option value="">— select —</option>
              {projectFiles.map((f) => (
                <option key={f.path} value={f.path}>
                  {f.name}
                </option>
              ))}
            </select>
          </label>
        )}

        <input
          ref={netlistInputRef}
          type="file"
          accept=".spice,.cir,.net,.sp,.scs"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void handleNetlistUpload(f);
            e.target.value = "";
          }}
        />
        <button
          type="button"
          title="Generate a schematic from a SPICE netlist (.spice/.cir/.net). Devices are placed on a grid and wired by net-name label."
          onClick={() => netlistInputRef.current?.click()}
          disabled={loading}
          className="flex items-center gap-1 rounded-sm border border-border bg-bg px-2 py-1 text-xs text-fg disabled:opacity-40"
        >
          <FileInput className="h-3.5 w-3.5" /> From netlist
        </button>

        <input
          ref={uploadInputRef}
          type="file"
          accept=".sch"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void handleUpload(f);
            // Reset so re-selecting the same file fires onChange again.
            e.target.value = "";
          }}
        />
        <button
          type="button"
          title="Upload a .sch file from your machine. Symbols are resolved against the PDK and xschem libraries; sibling-of-source refs won't resolve."
          onClick={() => uploadInputRef.current?.click()}
          disabled={loading}
          className="flex items-center gap-1 rounded-sm border border-border bg-bg px-2 py-1 text-xs text-fg disabled:opacity-40"
        >
          <Upload className="h-3.5 w-3.5" /> Upload .sch
        </button>
      </div>

      {/* Body: schematic viewer + device inspector */}
      <div className="flex min-h-0 flex-1">
        <div className="relative flex min-h-0 min-w-0 flex-1">
          {!current && !loading && (
            <EmptyHint
              isApplied={isApplied}
              projectFiles={projectFiles}
              projectXschemDir={projectXschemDir}
            />
          )}

          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-bg/70 text-sm text-muted">
              Loading schematic…
            </div>
          )}

          {error && (
            <div className="absolute left-3 top-3 max-w-md rounded-sm border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-300">
              {error}
            </div>
          )}

          {notice && (
            <div className="absolute right-3 top-3 max-w-md rounded-sm border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-[11px] text-amber-300">
              {notice}
            </div>
          )}

          {current && missingSymbolCount > 0 && (
            <div className="pointer-events-none absolute bottom-3 left-3 max-w-md rounded-sm border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-[11px] text-amber-300">
              {missingSymbolCount} symbol{missingSymbolCount === 1 ? "" : "s"} unavailable — device
              bodies show as placeholders. The xschem symbol library (PDK) is not reachable by the
              backend on this machine.
            </div>
          )}

          {current && (
            <SchematicViewer
              sch={current.parsed}
              symbols={symbols}
              navigableSymrefs={navigableSymrefs}
              onNavigateInto={handleNavigateInto}
            />
          )}
        </div>

        <aside className="w-[290px] shrink-0 overflow-hidden border-l border-border bg-panel">
          <DeviceInspector />
        </aside>
      </div>
    </div>
  );
}

function EmptyHint({
  isApplied,
  projectFiles,
  projectXschemDir,
}: {
  isApplied: boolean;
  projectFiles: { path: string; name: string }[];
  projectXschemDir: string | null;
}) {
  return (
    <div className="m-auto max-w-md p-6 text-center text-sm text-muted">
      <FileCode className="mx-auto mb-3 h-10 w-10 opacity-50" />
      {!isApplied ? (
        <p>
          Apply a project in the <span className="text-fg">Setup</span> tab to discover its xschem
          files.
        </p>
      ) : projectFiles.length === 0 ? (
        <p>
          No <code>.sch</code> files found
          {projectXschemDir ? (
            <>
              {" "}in <code className="break-all text-xs">{projectXschemDir}</code>
            </>
          ) : null}
          .
        </p>
      ) : (
        <p>Select a schematic from the dropdown to view it.</p>
      )}
    </div>
  );
}
