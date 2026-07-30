"use client";
import { useEffect, useRef, useState } from "react";
import { Maximize2, Minimize2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { ResizeHandle, useRailSize } from "@/components/ui/resizable";
import { useLibraryStore } from "@/stores/libraryStore";
import { useLibraryWizardStore } from "@/stores/libraryWizardStore";
import { engineUniverse, tbCatalog, tbDetail, tbList } from "@/lib/library/selectors";
import { engineMeta, engineMetaFallback } from "@/lib/library/data";
import { SpiceEditor } from "@/components/ui/SpiceEditor";
import { Chip, EngineChips } from "../chips";

const ROW = { gridTemplateColumns: "1.5fr 0.7fr 1.6fr 0.9fr 0.6fr 22px" } as const;

/** Testbenches table — class-scoped analyses reused by every circuit of a class. */
export function TestbenchesView() {
  const tbClassSel = useLibraryStore((s) => s.tbClassSel);
  const selTb = useLibraryStore((s) => s.selTb);
  const data = useLibraryStore((s) => s.data);
  const setSelTb = useLibraryStore((s) => s.setSelTb);
  const openWizard = useLibraryWizardStore((s) => s.openWizard);
  const rows = tbList(data, tbClassSel, selTb);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center gap-2.5 border-b border-border bg-bg px-4 py-2.5">
        <span className="text-[14px] font-semibold tracking-[-0.01em]">Testbenches</span>
        <span className="font-mono text-[10.5px] text-faint">class-scoped analyses · {tbCatalog(data).length}</span>
        <div className="flex-1" />
        <button
          type="button"
          onClick={() => openWizard("testbench")}
          className="inline-flex h-[26px] items-center rounded-md border border-primary px-2.5 text-[11px] font-semibold text-primary transition hover:bg-primary-soft"
        >
          + Register testbench
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3.5">
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="grid items-center gap-2.5 border-b border-border bg-bg px-3 py-2" style={ROW}>
            {["TESTBENCH", "CLASS", "MEASURES", "SIMULATORS", "CIRCUITS"].map((h) => (
              <span key={h} className="text-[9px] font-bold uppercase tracking-[0.06em] text-faint">{h}</span>
            ))}
            <span />
          </div>
          {rows.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setSelTb(t.id)}
              className={cn(
                "grid w-full items-center gap-2.5 border-b border-hairline px-3 py-2.5 text-left transition last:border-0 hover:bg-bg",
                t.selected && "bg-[#fafaff]",
              )}
              style={ROW}
            >
              <span className="font-mono text-[11px] font-medium">{t.name}</span>
              <span>
                <Chip bg={t.classBg} fg={t.classFg} className="font-medium">{t.klass}</Chip>
              </span>
              <span className="text-[10.5px] text-muted">{t.measures}</span>
              <span>
                <EngineChips engines={t.engines} />
              </span>
              <span className="font-mono text-[11px] text-muted">{t.circuits}</span>
              <span
                className={cn("h-1.5 w-1.5 justify-self-center rounded-full", t.selected ? "bg-primary" : "bg-transparent")}
                aria-hidden
              />
            </button>
          ))}
        </div>
      </div>

      {selTb && <NetlistPane />}
    </div>
  );
}

/** The selected testbench's engine source, highlighted (read-only Monaco).
 *  Bottom split of the table — vertically resizable + maximizable. The engine
 *  toggle swaps the ngspice `.spice` template (`${...}` binding slots ARE the
 *  contract) for the composed Spectre view: bench wiring + the analysis
 *  templates and SKILL calculator expressions it references. */
function NetlistPane() {
  const selTb = useLibraryStore((s) => s.selTb);
  const data = useLibraryStore((s) => s.data);
  const t = tbDetail(data, selTb);
  // the toggle's universe = engines the DB routes anywhere; per-bench availability below
  const universe = engineUniverse(data);
  const [engine, setEngine] = useState<string>("ngspice");
  const [maximized, setMaximized] = useState(false);
  const [loaded, setLoaded] = useState<{
    key: string;
    path: string;
    content: string;
    language: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useRailSize("ui:panel:testbench-source", 300, 140, 720);

  const key = `${t.klass}/${t.name}@${engine}`;
  useEffect(() => {
    if (t.name === "—") return;
    let live = true;
    setError(null);
    api
      .libraryTestbenchNetlist(t.klass, t.name, engine)
      .then((r) => {
        if (live)
          setLoaded({
            key: `${r.class}/${r.name}@${r.engine}`,
            path: r.path,
            content: r.content,
            language: r.language,
          });
      })
      .catch((err) => {
        if (live) {
          setLoaded(null);
          setError(
            engine === "spectre"
              ? `No Spectre bench wiring for ${t.klass}/${t.name} — this bench runs on the open (ngspice) lane only.`
              : err instanceof Error
                ? err.message
                : "No template source found",
          );
        }
      });
    return () => {
      live = false;
    };
  }, [t.klass, t.name, engine]);

  // switching to a bench that lacks the selected engine falls back to one it has
  useEffect(() => {
    if (t.engines.length && !t.engines.includes(engine)) setEngine(t.engines[0]);
  }, [t.engines, engine]);

  const fileLabel = engine === "spectre" ? "spectre-benches.yaml" : `${t.name}.spice`;
  const body = (
    <>
      <div className="flex h-[32px] shrink-0 items-center gap-2.5 border-b border-hairline px-4">
        <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted">
          Testbench source
        </span>
        <span className="font-mono text-[10.5px] font-semibold">{fileLabel}</span>
        {loaded?.key === key && (
          <span className="min-w-0 truncate font-mono text-[9.5px] text-faint">{loaded.path}</span>
        )}
        <div className="flex-1" />
        {/* engines differ: ngspice = authored deck template; spectre = analyses + OCEAN calculator */}
        <div className="flex items-center gap-0.5" role="tablist" aria-label="Engine">
          {universe.map((e) => {
            // repo-derived availability: a bench only offers engines with committed sources
            const available = !t.engines.length || t.engines.includes(e);
            const meta = engineMeta[e] ?? engineMetaFallback;
            return (
              <button
                key={e}
                type="button"
                role="tab"
                aria-selected={engine === e}
                disabled={!available}
                title={available ? undefined : `no committed ${e} source for this bench`}
                onClick={() => setEngine(e)}
                style={engine === e ? { background: meta.bg, color: meta.fg } : undefined}
                className={cn(
                  "rounded-sm px-2 py-0.5 font-mono text-[9.5px] transition",
                  engine === e
                    ? "font-semibold"
                    : available
                      ? "text-faint hover:bg-hairline hover:text-fg"
                      : "cursor-not-allowed text-faint opacity-40",
                )}
              >
                {e}
              </button>
            );
          })}
        </div>
        <span className="font-mono text-[9px] text-faint">
          {engine === "spectre" ? "wiring + SKILL calculator" : "${...} = binding slots"}
        </span>
        <button
          type="button"
          onClick={() => setMaximized((m) => !m)}
          aria-label={maximized ? "Restore panel" : "Maximize panel"}
          title={maximized ? "Restore" : "Maximize"}
          className="rounded-sm p-0.5 text-faint transition hover:bg-hairline hover:text-fg"
        >
          {maximized ? <Minimize2 className="h-3 w-3" /> : <Maximize2 className="h-3 w-3" />}
        </button>
      </div>
      <div className="min-h-0 flex-1">
        {error ? (
          <div className="flex h-full items-center justify-center px-6 text-center text-[11px] text-muted">
            {error}
          </div>
        ) : loaded?.key === key ? (
          <SpiceEditor value={loaded.content} language={loaded.language} />
        ) : (
          <div className="flex h-full items-center justify-center font-mono text-[10px] text-faint">
            loading {fileLabel}…
          </div>
        )}
      </div>
    </>
  );

  if (maximized) {
    return (
      <div className="fixed inset-0 z-100 flex flex-col bg-panel">
        {body}
      </div>
    );
  }
  return (
    <div
      ref={panelRef}
      style={{ height }}
      className="relative flex shrink-0 flex-col border-t border-border bg-panel"
    >
      <ResizeHandle
        edge="top"
        size={height}
        compute={(y) => (panelRef.current?.getBoundingClientRect().bottom ?? 0) - y}
        onSize={setHeight}
        resetTo={300}
        label="Resize the testbench source panel"
      />
      {body}
    </div>
  );
}
