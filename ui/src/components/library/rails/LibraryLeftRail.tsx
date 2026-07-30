"use client";
import { useRef } from "react";
import { cn } from "@/lib/utils";
import { ResizeHandle, useRailWidth } from "@/components/ui/resizable";
import { useLibraryStore } from "@/stores/libraryStore";
import {
  classOptions,
  sourceOptions,
  compOptions,
  sections,
  templateCategories,
  tbClassOptions,
  buildDetail,
  type FilterOption,
} from "@/lib/library/selectors";
import type { FilterKey } from "@/stores/libraryStore";
import type { LibraryData } from "@/lib/library/adapt";
import { UI } from "@/config";
import { Eyebrow } from "../chips";

/** Section header row (34px) atop each rail variant. */
function RailHead({ children, action }: { children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div className="flex h-[34px] shrink-0 items-center justify-between border-b border-hairline px-3.5">
      <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted">{children}</span>
      {action}
    </div>
  );
}

/** A 14px checkbox + label + count, used by every filter list. */
function CheckRow({ opt, onToggle, mono = false }: { opt: FilterOption; onToggle: () => void; mono?: boolean }) {
  return (
    <button type="button" onClick={onToggle} className="flex items-center gap-2.5 rounded-md px-1.5 py-1 text-left transition hover:bg-hairline">
      <span
        className={cn(
          "flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded-[4px] text-[9px]",
          opt.on ? "bg-primary text-white" : "border border-[#d4d4d8] bg-panel",
        )}
        aria-hidden
      >
        {opt.on && "✓"}
      </span>
      <span className={cn("flex-1 text-[11.5px]", mono && "font-mono text-[10.5px]")}>{opt.label}</span>
      <span className="font-mono text-[10px] text-faint">{opt.count}</span>
    </button>
  );
}

/** Library left rail — content swaps per tab / detail (filters, sections,
 *  families, class filter, or the datasheet on-this-page nav). Width is
 *  user-adjustable (drag the right edge; double-click resets; persisted). */
export function LibraryLeftRail() {
  const tab = useLibraryStore((s) => s.tab);
  const detailOpen = useLibraryStore((s) => s.detailOpen);
  const selId = useLibraryStore((s) => s.selId);
  const tbIdx = useLibraryStore((s) => s.tbIdx);
  const classSel = useLibraryStore((s) => s.classSel);
  const sourceSel = useLibraryStore((s) => s.sourceSel);
  const compSel = useLibraryStore((s) => s.compSel);
  const tbClassSel = useLibraryStore((s) => s.tbClassSel);
  const data = useLibraryStore((s) => s.data);
  const detail = useLibraryStore((s) => s.detail);
  const toggleFilter = useLibraryStore((s) => s.toggleFilter);
  const clearFilters = useLibraryStore((s) => s.clearFilters);
  const navSection = useLibraryStore((s) => s.navSection);

  const ref = useRef<HTMLElement>(null);
  const [width, setWidth] = useRailWidth("ui:rail:library-left", 200, 160, 440);

  return (
    <aside
      ref={ref}
      style={{ width }}
      className="relative flex shrink-0 flex-col border-r border-border bg-panel"
    >
      <ResizeHandle
        edge="right"
        size={width}
        compute={(x) => x - (ref.current?.getBoundingClientRect().left ?? 0)}
        onSize={setWidth}
        resetTo={200}
        label="Resize the library filters panel"
      />
      {detailOpen ? (
        <DetailRail data={data} detail={detail} selId={selId} tbIdx={tbIdx} />
      ) : tab === "circuits" ? (
        <FiltersRail
          data={data}
          classSel={classSel}
          sourceSel={sourceSel}
          compSel={compSel}
          onToggle={toggleFilter}
          onClear={clearFilters}
        />
      ) : tab === "home" ? (
        <SectionsRail data={data} onNav={navSection} />
      ) : tab === "testbenches" ? (
        <TbClassRail data={data} tbClassSel={tbClassSel} onToggle={toggleFilter} />
      ) : (
        <FamiliesRail data={data} />
      )}
    </aside>
  );
}

function FiltersRail({
  data,
  classSel,
  sourceSel,
  compSel,
  onToggle,
  onClear,
}: {
  data: LibraryData;
  classSel: string[];
  sourceSel: string[];
  compSel: string[];
  onToggle: (k: FilterKey, v: string) => void;
  onClear: () => void;
}) {
  const draftCount = data.circuits.filter((c) => c.status === "draft").length;
  const incompleteCount = data.circuits.filter((c) => c.status === "incomplete").length;
  return (
    <>
      <RailHead action={<button type="button" onClick={onClear} className="text-[10.5px] text-primary hover:underline">Clear</button>}>
        Filters
      </RailHead>
      <div className="min-h-0 flex-1 overflow-y-auto p-3.5">
        <Eyebrow className="mb-2">Class</Eyebrow>
        <div className="mb-4 flex flex-col gap-px">
          {classOptions(data, classSel).map((o) => (
            <CheckRow key={o.key} opt={o} onToggle={() => onToggle("classSel", o.key)} />
          ))}
        </div>
        <Eyebrow className="mb-2">Source</Eyebrow>
        <div className="mb-4 flex flex-col gap-px">
          {sourceOptions(data, sourceSel).map((o) => (
            <CheckRow key={o.key} opt={o} onToggle={() => onToggle("sourceSel", o.key)} />
          ))}
        </div>
        <Eyebrow className="mb-2">Compensation</Eyebrow>
        <div className="mb-4 flex flex-col gap-px">
          {compOptions(data, compSel).map((o) => (
            <CheckRow key={o.key} opt={o} mono onToggle={() => onToggle("compSel", o.key)} />
          ))}
        </div>
        <Eyebrow className="mb-2">Status</Eyebrow>
        <div className="flex gap-1.5">
          <span className="flex-1 rounded-md bg-hairline py-1.5 text-center text-[10.5px] font-semibold text-muted">draft · {draftCount}</span>
          <span className="flex-1 rounded-md border border-border py-1.5 text-center text-[10.5px] text-muted">incomplete · {incompleteCount}</span>
        </div>
      </div>
    </>
  );
}

function SectionsRail({ data, onNav }: { data: LibraryData; onNav: ReturnType<typeof useLibraryStore.getState>["navSection"] }) {
  return (
    <>
      <RailHead>Library</RailHead>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="flex flex-col gap-px p-2.5">
          {sections(data).map((s) => {
            const active = s.nav === "featured";
            return (
              <button
                key={s.label}
                type="button"
                onClick={() => onNav(s.nav)}
                className={cn(
                  "flex items-center gap-2.5 rounded-[7px] px-2.5 py-1.5 text-left transition",
                  active ? "bg-primary-soft font-semibold text-primary" : "text-muted hover:bg-hairline",
                )}
              >
                <span className={cn("w-4 text-center text-[13px]", !active && "text-faint")}>{s.icon}</span>
                <span className="flex-1 text-[11.5px]">{s.label}</span>
                <span className={cn("font-mono text-[10px]", !active && "text-faint")}>{s.count}</span>
              </button>
            );
          })}
        </div>
        <div className="mx-3.5 h-px bg-hairline" />
        <div className="px-3.5 pb-3.5 pt-2">
          <Eyebrow className="mb-2">Recently run</Eyebrow>
          <div className="flex flex-col gap-1.5">
            {UI.library.home.recentlyRun.map((id) => (
              <div key={id} className="font-mono text-[10.5px] text-muted">{id}</div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function TbClassRail({ data, tbClassSel, onToggle }: { data: LibraryData; tbClassSel: string[]; onToggle: (k: FilterKey, v: string) => void }) {
  return (
    <>
      <RailHead>Circuit class</RailHead>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="flex flex-col gap-px p-2.5">
          {tbClassOptions(data, tbClassSel).map((o) => (
            <CheckRow key={o.key} opt={o} onToggle={() => onToggle("tbClassSel", o.key)} />
          ))}
        </div>
        <div className="mx-3.5 h-px bg-hairline" />
        <div className="px-3.5 pb-3.5 pt-2 text-[10.5px] leading-relaxed text-muted">
          Each testbench is registered with a circuit class and reused by every circuit of that class.
        </div>
      </div>
    </>
  );
}

function FamiliesRail({ data }: { data: LibraryData }) {
  return (
    <>
      <RailHead>Families</RailHead>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="flex flex-col gap-px p-2.5">
          {templateCategories(data).map((c) => (
            <div
              key={c.label}
              className={cn(
                "flex items-center gap-2 rounded-[7px] px-2.5 py-1.5",
                c.active ? "bg-primary-soft font-semibold text-primary" : "text-muted hover:bg-hairline",
              )}
            >
              <span className="flex-1 text-[11.5px]">{c.label}</span>
              <span className={cn("font-mono text-[10px]", !c.active && "text-faint")}>{c.count}</span>
            </div>
          ))}
        </div>
        <div className="mx-3.5 h-px bg-hairline" />
        <div className="px-3.5 pb-3.5 pt-2 text-[10.5px] leading-relaxed text-muted">
          Topological matches overlaid by the <span className="font-mono text-[10px]">circuitgraph</span> subcircuit
          matcher — type + polarity + pin wiring only.
        </div>
      </div>
    </>
  );
}

function DetailRail({
  data,
  detail,
  selId,
  tbIdx,
}: {
  data: LibraryData;
  detail: ReturnType<typeof useLibraryStore.getState>["detail"];
  selId: string;
  tbIdx: number;
}) {
  const d = buildDetail(data, detail, selId, tbIdx);
  if (!d) return null;
  const nav = [
    { icon: "◧", label: "Schematic", active: true },
    { icon: "≣", label: "Manifest", active: false },
    { icon: "⊞", label: "Analyses", active: false, count: d.nTb },
    { icon: "◫", label: "Results", active: false },
  ];
  return (
    <>
      <RailHead>On this page</RailHead>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="flex flex-col gap-px px-2.5 py-2.5">
          {nav.map((n) => (
            <div
              key={n.label}
              className={cn(
                "flex items-center gap-2.5 rounded-[7px] px-2.5 py-1.5 text-[11.5px]",
                n.active ? "bg-primary-soft font-semibold text-primary" : "text-muted hover:bg-hairline",
              )}
            >
              <span className={cn("w-3.5 text-center", !n.active && "text-faint")}>{n.icon}</span>
              {n.label}
              {n.count !== undefined && <span className="ml-auto font-mono text-[10px] text-faint">{n.count}</span>}
            </div>
          ))}
        </div>
        <div className="mx-3.5 h-px bg-hairline" />
        <div className="px-3.5 pb-3.5 pt-2">
          <Eyebrow className="mb-2">Schematic views</Eyebrow>
          <div className="flex flex-col gap-1.5">
            {[`${d.id}.sch`, `${d.id}_annotated.sch`, `hier/${d.id}.sch`].map((f) => (
              <div key={f} className="font-mono text-[10px] text-muted">{f}</div>
            ))}
          </div>
          <Eyebrow className="mb-2 mt-3.5">PDK bindings</Eyebrow>
          <div className="flex flex-col gap-1">
            {d.pdkRows.map((p) => (
              <div key={p.label} className="flex items-center gap-2 text-[11px] text-muted">
                <span className="h-[7px] w-[7px] rounded-[2px]" style={{ background: p.dot }} aria-hidden />
                <span className="flex-1">{p.label}</span>
                <span className="font-mono text-[9px] text-faint">{p.note}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
