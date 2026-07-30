"use client";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLibraryStore } from "@/stores/libraryStore";
import { templateTotal } from "@/lib/library/selectors";
import { TemplatePreview } from "../TemplatePreview";

const GRID_STYLE = { gridTemplateColumns: "repeat(auto-fill,minmax(184px,1fr))" } as const;

/** Templates grid — functional sub-circuits overlaid by the circuitgraph matcher. */
export function TemplatesView() {
  const data = useLibraryStore((s) => s.data);
  const tplId = useLibraryStore((s) => s.tplId);
  const setTplId = useLibraryStore((s) => s.setTplId);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex shrink-0 items-center gap-2.5 border-b border-border bg-bg px-4 py-2.5">
        <span className="max-w-[120px] text-[14px] font-semibold leading-tight tracking-[-0.01em]">
          Functional sub-circuits
        </span>
        <span className="font-mono text-[10.5px] text-faint">templates/ · {templateTotal(data)} blocks</span>
        <div className="flex-1" />
        <div className="flex h-7 w-[190px] items-center gap-1.5 rounded-md border border-border bg-panel px-2.5 opacity-60">
          <Search className="h-3 w-3 shrink-0 text-faint" aria-hidden />
          <input disabled placeholder="Search blocks…" className="w-full bg-transparent text-[11.5px] outline-hidden placeholder:text-faint" />
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3.5">
        <div className="grid gap-2.5" style={GRID_STYLE}>
          {data.templates.map((t) => {
            const selected = t.id === tplId;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setTplId(t.id)}
                className={cn(
                  "relative flex flex-col gap-2 rounded-lg border border-border bg-panel p-3 text-left transition",
                  "hover:border-[#c7d2fe] hover:shadow-[0_4px_14px_-6px_rgba(79,70,229,0.25)]",
                )}
              >
                {selected && (
                  <span className="pointer-events-none absolute -inset-px rounded-lg border-[1.5px] border-primary" aria-hidden />
                )}
                <TemplatePreview id={t.id} hasImage={t.hasImage} heightClass="h-[62px]" />
                <div className="text-[11.5px] font-semibold leading-tight tracking-[-0.01em]">{t.name}</div>
                <div className="flex items-center justify-between gap-1.5">
                  <span className="inline-flex items-center rounded-sm bg-hairline px-1.5 py-[2px] text-[9px] font-medium text-muted">
                    {t.polarity}
                  </span>
                  <span className="text-[10px] text-faint">{t.role}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
