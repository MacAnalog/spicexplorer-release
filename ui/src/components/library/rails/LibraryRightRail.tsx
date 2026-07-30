"use client";
import { useCallback, useRef, useState } from "react";
import { useLibraryStore } from "@/stores/libraryStore";
import { Stat } from "@/components/ui/stat";
import { Button } from "@/components/ui/button";
import { ResizeHandle, useRailWidth } from "@/components/ui/resizable";
import { SpecChip } from "@/components/ui/spec-chip";
import { api } from "@/lib/api";
import { engineMeta, engineMetaFallback, tools } from "@/lib/library/data";
import { buildDetail, circuitById, tbCatalog, tbDetail, templateById } from "@/lib/library/selectors";
import { Hatch } from "../Hatch";
import { SchematicViewer } from "../SchematicViewer";
import { SourceOverlay } from "../SourceOverlay";
import { TemplatePreview } from "../TemplatePreview";
import { Chip, EngineChips, Eyebrow } from "../chips";

/** Library right rail — content swaps per tab / detail (circuit preview,
 *  template detail, testbench detail, or the datasheet active-analysis panel).
 *  Width is user-adjustable (drag the left edge; double-click resets; persisted). */
export function LibraryRightRail() {
  const tab = useLibraryStore((s) => s.tab);
  const detailOpen = useLibraryStore((s) => s.detailOpen);
  const selId = useLibraryStore((s) => s.selId);
  const tbIdx = useLibraryStore((s) => s.tbIdx);
  const tplId = useLibraryStore((s) => s.tplId);
  const selTb = useLibraryStore((s) => s.selTb);
  const ref = useRef<HTMLElement>(null);
  const [width, setWidth] = useRailWidth("ui:rail:library-right", 272, 200, 560);

  return (
    <aside
      ref={ref}
      style={{ width }}
      className="relative flex shrink-0 flex-col border-l border-border bg-panel"
    >
      <ResizeHandle
        edge="left"
        size={width}
        compute={(x) => (ref.current?.getBoundingClientRect().right ?? 0) - x}
        onSize={setWidth}
        resetTo={272}
        label="Resize the library preview panel"
      />
      {/* content scrolls in a wrapper so the resize handle stays pinned to the edge */}
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        {detailOpen ? (
          <ActiveAnalysis selId={selId} tbIdx={tbIdx} />
        ) : tab === "templates" ? (
          <TemplateDetail tplId={tplId} />
        ) : tab === "testbenches" ? (
          <TestbenchDetail selTb={selTb} />
        ) : (
          <CircuitPreview selId={selId} />
        )}
      </div>
    </aside>
  );
}

function RailHead({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-[34px] shrink-0 items-center border-b border-hairline px-3.5">
      <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted">{children}</span>
    </div>
  );
}

function CircuitPreview({ selId }: { selId: string }) {
  const openDetail = useLibraryStore((s) => s.openDetail);
  const data = useLibraryStore((s) => s.data);
  const detail = useLibraryStore((s) => s.detail);
  const d = buildDetail(data, detail, selId, 0);
  if (!d) return null;
  return (
    <>
      <RailHead>Preview</RailHead>
      <div className="flex flex-col gap-3 p-3.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[14px] font-semibold tracking-[-0.01em]">{d.name}</span>
          <Chip bg={d.classBg} fg={d.classFg}>{d.compLabel}</Chip>
        </div>
        <SchematicViewer heightClass="h-[120px]" />
        <div className="grid grid-cols-2 gap-2">
          {d.stats.slice(0, 4).map((s) => (
            <Stat key={s.eyebrow} eyebrow={s.eyebrow} value={s.value} unit={s.unit} tone={s.tone} />
          ))}
        </div>
        <div className="overflow-hidden rounded-lg border border-border text-[11px]">
          <div className="flex justify-between border-b border-hairline px-3 py-1.5">
            <span className="text-muted">analyses</span>
            <span className="font-mono">{d.nTb}</span>
          </div>
          <div className="flex justify-between px-3 py-1.5">
            <span className="text-muted">PDK bindings</span>
            <span className="font-mono">{d.pdkRows.length}</span>
          </div>
        </div>
        <Button variant="primary" className="w-full" onClick={() => openDetail(selId)}>
          Open datasheet →
        </Button>
      </div>
    </>
  );
}

function TemplateDetail({ tplId }: { tplId: string }) {
  const data = useLibraryStore((s) => s.data);
  const t = templateById(data, tplId);
  const [viewNetlist, setViewNetlist] = useState(false);
  const loadNetlist = useCallback(() => api.libraryTemplateNetlist(t?.id ?? ""), [t?.id]);
  if (!t) {
    return (
      <>
        <RailHead>Template</RailHead>
        <div className="p-3.5 text-[11px] text-muted">No templates loaded.</div>
      </>
    );
  }
  return (
    <>
      <RailHead>Template</RailHead>
      <div className="flex flex-col gap-3 p-3.5">
        <div>
          <div className="text-[14px] font-semibold tracking-[-0.01em]">{t.name}</div>
          <div className="font-mono text-[10.5px] text-faint">{t.id}</div>
        </div>
        <TemplatePreview
          key={t.id}
          id={t.id}
          hasImage={t.hasImage}
          label={t.netlist}
          heightClass="h-[120px]"
          className="rounded-lg border-border"
          enlargeable
        />
        <div className="text-[11px] leading-relaxed text-muted">{t.desc}</div>
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="border-b border-hairline bg-bg px-3 py-1.5">
            <Eyebrow>Ports</Eyebrow>
          </div>
          {t.ports.map(([role, net]) => (
            <div key={role} className="flex justify-between border-b border-hairline px-3 py-1.5 text-[11px] last:border-0">
              <span className="text-muted">{role}</span>
              <span className="font-mono">{net}</span>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <Button variant="default" className="flex-1" onClick={() => setViewNetlist(true)}>
            View netlist
          </Button>
        </div>
      </div>
      {viewNetlist && (
        <SourceOverlay title={t.id} load={loadNetlist} onClose={() => setViewNetlist(false)} />
      )}
    </>
  );
}

function TestbenchDetail({ selTb }: { selTb: string }) {
  const data = useLibraryStore((s) => s.data);
  const t = tbDetail(data, selTb);
  const [srcEngine, setSrcEngine] = useState<string | null>(null);
  const loadSrc = useCallback(
    () => api.libraryTestbenchNetlist(t.klass, t.name, srcEngine ?? "ngspice"),
    [t.klass, t.name, srcEngine],
  );
  return (
    <>
      <RailHead>Testbench</RailHead>
      <div className="flex flex-col gap-3 p-3.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[14px] font-semibold">{t.name}</span>
          <Chip bg={t.classBg} fg={t.classFg} className="font-medium">{t.klass}</Chip>
        </div>
        {/* the template's own authored header line (from the repo, not curated copy) */}
        <div className="text-[11px] leading-relaxed text-muted">{t.desc || t.measures}</div>
        <div className="overflow-hidden rounded-lg border border-border text-[11px]">
          <div className="flex justify-between border-b border-hairline px-3 py-1.5">
            <span className="text-muted">registered with</span>
            <span className="font-mono">{t.klass}</span>
          </div>
          <div className="flex justify-between border-b border-hairline px-3 py-1.5">
            <span className="text-muted">used by</span>
            <span className="font-mono">{t.circuits} circuits</span>
          </div>
          <div className="flex items-center justify-between border-b border-hairline px-3 py-1.5">
            <span className="text-muted">simulators</span>
            <EngineChips engines={t.engines} />
          </div>
          {t.engines.includes("spectre") && (
            <div className="flex justify-between border-b border-hairline px-3 py-1.5">
              <span className="text-muted">spectre wiring</span>
              <span className="font-mono">{t.spectreAnalyses} analyses · {t.spectreCalculator} SKILL</span>
            </div>
          )}
          {t.path && (
            <div className="flex min-w-0 items-center justify-between gap-2 px-3 py-1.5">
              <span className="shrink-0 text-muted">source</span>
              <span className="min-w-0 truncate font-mono text-[9.5px] text-faint" title={t.path}>{t.path}</span>
            </div>
          )}
        </div>
        {t.engines.length > 0 && (
          <div className="flex gap-2">
            {t.engines.map((e) => (
              <Button key={e} variant="default" className="flex-1" onClick={() => setSrcEngine(e)}>
                {(engineMeta[e] ?? engineMetaFallback).srcLabel}
              </Button>
            ))}
          </div>
        )}
        {t.slots.length > 0 && (
          <div>
            <Eyebrow className="mb-2">Binding slots</Eyebrow>
            {/* the ${...} placeholders the analysis resolver binds — the template's contract */}
            <div className="flex flex-wrap gap-1.5">
              {t.slots.map((s) => (
                <span key={s} className="inline-flex items-center rounded-sm bg-hairline px-1.5 py-1 font-mono text-[10px] text-tertiary">{"${" + s + "}"}</span>
              ))}
            </div>
          </div>
        )}
        <div>
          <Eyebrow className="mb-2">Extracted metrics</Eyebrow>
          <div className="flex flex-wrap gap-1.5">
            {t.metrics.map((m) => (
              <span key={m} className="inline-flex items-center rounded-sm bg-hairline px-1.5 py-1 font-mono text-[10px] text-muted">{m}</span>
            ))}
          </div>
        </div>
      </div>
      {srcEngine && (
        <SourceOverlay
          title={`${t.klass}/${t.name} · ${srcEngine}`}
          load={loadSrc}
          onClose={() => setSrcEngine(null)}
        />
      )}
    </>
  );
}

function ActiveAnalysis({ selId, tbIdx }: { selId: string; tbIdx: number }) {
  const data = useLibraryStore((s) => s.data);
  const detail = useLibraryStore((s) => s.detail);
  const d = buildDetail(data, detail, selId, tbIdx);
  const klass = circuitById(data, selId)?.klass ?? "amplifier";
  const tbName = d?.tbActiveName ?? "";
  // the analysis IS a class bench — offer exactly the engines it has committed sources for
  const benchEngines = tbCatalog(data).find((b) => b.id === `${klass}/${tbName}`)?.engines ?? [];
  const [srcEngine, setSrcEngine] = useState<string | null>(null);
  const loadBench = useCallback(
    () => api.libraryTestbenchNetlist(klass, tbName, srcEngine ?? "ngspice"),
    [klass, tbName, srcEngine],
  );
  if (!d) return null;
  return (
    <>
      <RailHead>Active analysis</RailHead>
      <div className="flex flex-col gap-3 p-3.5">
        <div>
          <div className="font-mono text-[14px] font-semibold">{d.tbActiveName}</div>
          <div className="text-[11px] text-muted">{d.tbActiveMeasures}</div>
          {/* the analysis IS a class testbench — open its per-engine source in place
              (spectre = bench wiring + analyses + SKILL calculator expressions) */}
          {benchEngines.length > 0 && (
            <div className="mt-1.5 flex items-center gap-1">
              <span className="font-mono text-[9px] text-faint">bench source:</span>
              {benchEngines.map((e) => {
                const meta = engineMeta[e] ?? engineMetaFallback;
                return (
                  <button
                    key={e}
                    type="button"
                    onClick={() => setSrcEngine(e)}
                    style={{ background: meta.bg, color: meta.fg }}
                    className="rounded-sm px-1.5 py-px font-mono text-[9.5px] font-semibold transition hover:opacity-80"
                    title={e === "spectre" ? "Bench wiring + analysis templates + SKILL calculator expressions" : undefined}
                  >
                    {e === "spectre" ? meta.srcLabel : e}
                  </button>
                );
              })}
            </div>
          )}
        </div>
        <Hatch label={d.tbActivePlot} heightClass="h-[120px]" className="rounded-lg border-border" />
        <div className="flex flex-col gap-1.5">
          {d.chips.map((c) => (
            <SpecChip key={c.name} name={c.name} value={c.value} target={c.target} status={c.status} />
          ))}
        </div>
        {d.hasSymbolic && (
          <div className="rounded-lg bg-secondary-soft px-3 py-2 text-[10.5px] leading-relaxed text-secondary">
            <div className="mb-0.5 font-bold uppercase tracking-[0.06em]">Symbolic cross-check</div>
            {d.symbolicText}
          </div>
        )}
        {srcEngine && (
          <SourceOverlay
            title={`${klass}/${d.tbActiveName} · ${srcEngine}`}
            load={loadBench}
            onClose={() => setSrcEngine(null)}
          />
        )}
        <div>
          <Eyebrow className="mb-2">Design with this circuit</Eyebrow>
          <div className="flex flex-col gap-1.5">
            {tools.map((t) => (
              <button
                key={t.label}
                type="button"
                className="flex items-center gap-2.5 rounded-lg border border-border bg-panel px-3 py-2 text-left transition hover:border-[#c7d2fe] hover:bg-bg"
              >
                <span className="w-4 text-center text-[14px] text-primary">{t.icon}</span>
                <span className="min-w-0 flex-1">
                  <span className="block text-[11.5px] font-medium">{t.label}</span>
                  <span className="block text-[10px] text-faint">{t.desc}</span>
                </span>
                <span className="text-faint">→</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
