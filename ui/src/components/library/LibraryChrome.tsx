"use client";
import { PanelBottom, PanelRight } from "lucide-react";
import { UI } from "@/config";
import { useLibraryStore } from "@/stores/libraryStore";
import { filterAndSort, tbList, totalCircuits, tbCatalog } from "@/lib/library/selectors";

/**
 * The Library's own bottom "analog-db log" + indigo status bar (handoff §3.3–3.4).
 * The `fullBleed` `/library` view hides the shell's BottomPanel/StatusBar and owns
 * these instead. Both read live state from `libraryStore` — nothing is mock: the log
 * reflects the actual load, the status bar the real catalog schema + DB root + counts.
 */

const TAB_LABEL: Record<string, string> = {
  home: "Home",
  circuits: "Circuits",
  templates: "Templates",
  testbenches: "Testbenches",
};

export function LibraryLog() {
  const status = useLibraryStore((s) => s.status);
  const data = useLibraryStore((s) => s.data);
  const dbRoot = useLibraryStore((s) => s.dbRoot);
  const schema = useLibraryStore((s) => s.catalogSchema);
  const reason = useLibraryStore((s) => s.unavailableReason);
  const error = useLibraryStore((s) => s.error);
  const logOpen = useLibraryStore((s) => s.logOpen);
  if (!logOpen) return null;

  const dbName = dbRoot ? dbRoot.split("/").filter(Boolean).pop() : null;
  const lines: { level: "ok" | "info" | "warn"; msg: string }[] =
    status === "ready"
      ? [
          { level: "ok", msg: `catalog loaded — ${totalCircuits(data)} circuits · ${data.classes.length} classes · ${data.templates.length} templates` },
          { level: "info", msg: `GET /api/library/* · ${schema || "catalog"} · ${tbCatalog(data).length} testbenches indexed` },
        ]
      : status === "unavailable"
        ? [{ level: "warn", msg: `analog-db unavailable — ${reason ?? "submodule not installed"}` }]
        : status === "error"
          ? [{ level: "warn", msg: `load failed — ${error ?? "unknown error"}` }]
          : [{ level: "info", msg: "connecting to analog-db…" }];

  return (
    <div className="flex h-[60px] shrink-0 flex-col border-t border-border bg-panel">
      <div className="flex h-[26px] items-center gap-3 border-b border-hairline px-3">
        <span className="text-[10px] font-semibold text-muted">▾ analog-db log</span>
        <span className="font-mono text-[10px] text-primary">{UI.library.home.title}</span>
        <div className="flex-1" />
        <span className="font-mono text-[9.5px] text-faint">{dbName ? `examples/analog-db (${dbName})` : "examples/analog-db"}</span>
      </div>
      <div className="flex flex-1 flex-col justify-center gap-0.5 px-3 py-1">
        {lines.map((l, i) => (
          <div key={i} className="flex items-center gap-2 font-mono text-[10px] leading-tight">
            <span className="text-faint">library</span>
            <span
              className={
                l.level === "ok" ? "font-semibold text-ok" : l.level === "warn" ? "font-semibold text-tertiary" : "text-secondary"
              }
            >
              {l.level}
            </span>
            <span className="truncate text-muted">{l.msg}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function LibraryStatusBar() {
  const tab = useLibraryStore((s) => s.tab);
  const detailOpen = useLibraryStore((s) => s.detailOpen);
  const selId = useLibraryStore((s) => s.selId);
  const status = useLibraryStore((s) => s.status);
  const data = useLibraryStore((s) => s.data);
  const schema = useLibraryStore((s) => s.catalogSchema);
  const classSel = useLibraryStore((s) => s.classSel);
  const sourceSel = useLibraryStore((s) => s.sourceSel);
  const compSel = useLibraryStore((s) => s.compSel);
  const tbClassSel = useLibraryStore((s) => s.tbClassSel);
  const search = useLibraryStore((s) => s.search);
  const sort = useLibraryStore((s) => s.sort);
  const logOpen = useLibraryStore((s) => s.logOpen);
  const railOpen = useLibraryStore((s) => s.railOpen);
  const toggleLog = useLibraryStore((s) => s.toggleLog);
  const toggleRail = useLibraryStore((s) => s.toggleRail);

  const ready = status === "ready";
  const crumb = detailOpen ? selId : TAB_LABEL[tab] ?? tab;
  // Filter-aware: "N of M (filtered)" whenever the rail filters/search hide rows,
  // so the status bar always describes what's actually on screen.
  const shownOf = (shown: number, total: number, noun: string) =>
    shown < total ? `${shown} of ${total} ${noun} (filtered)` : `${total} ${noun}`;
  const count = detailOpen
    ? `${data.circuits.find((c) => c.id === selId)?.klass ?? ""}`
    : tab === "templates"
      ? `${data.templates.length} templates`
      : tab === "testbenches"
        ? shownOf(tbList(data, tbClassSel, "").length, tbCatalog(data).length, "analyses")
        : shownOf(
            filterAndSort(data, { classSel, sourceSel, compSel, search, sort }).length,
            totalCircuits(data),
            "circuits",
          );

  return (
    <div className="flex h-6 shrink-0 items-center gap-2 bg-primary px-3 text-[10.5px] text-[#e0e7ff]">
      <span className="font-semibold">Library</span>
      <span className="opacity-60">›</span>
      <span className="font-mono">{crumb}</span>
      {count && <span className="font-mono opacity-70">· {count}</span>}
      <div className="flex-1" />
      {/* same panel-toggle affordance as the shell StatusBar (this fullBleed view owns its own chrome) */}
      <button
        type="button"
        onClick={toggleLog}
        aria-label="Toggle analog-db log panel"
        title={logOpen ? "Hide analog-db log" : "Show analog-db log"}
        className={`rounded-sm p-0.5 transition hover:bg-white/15 ${logOpen ? "text-white" : "text-white/50"}`}
      >
        <PanelBottom className="h-3.5 w-3.5" />
      </button>
      <button
        type="button"
        onClick={toggleRail}
        aria-label="Toggle library preview rail"
        title={railOpen ? "Hide preview rail" : "Show preview rail"}
        className={`rounded-sm p-0.5 transition hover:bg-white/15 ${railOpen ? "text-white" : "text-white/50"}`}
      >
        <PanelRight className="h-3.5 w-3.5" />
      </button>
      <span className="opacity-50">·</span>
      <span className="font-mono opacity-80">{schema || "spicexplorer/catalog@1"}</span>
      <span className="opacity-50">·</span>
      <span className="inline-flex items-center gap-1 font-mono">
        <span className={`inline-block h-1.5 w-1.5 rounded-full ${ready ? "bg-[#a7f3d0]" : "bg-[#fca5a5]"}`} aria-hidden />
        {ready ? "analog-db ready" : status === "unavailable" ? "unavailable" : "loading"}
      </span>
    </div>
  );
}
