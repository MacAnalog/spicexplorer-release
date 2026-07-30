"use client";
import { useEffect, useState } from "react";
import { Maximize2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { librarySchematicUrl } from "@/lib/api";
import { Lightbox } from "@/components/ui/lightbox";
import { useLibraryStore } from "@/stores/libraryStore";
import { Hatch } from "./Hatch";

/**
 * Datasheet schematic — renders the selected circuit's committed `.svg` and lets the
 * user switch between the three rendered views the analog-db harness produces:
 * **block-aware** (detected functional blocks as coloured boxes), **hierarchical**
 * (block-diagram, one symbol per block), and **pure** (plain topology) — a visual guide.
 *
 * The image only needs `selId` + `mode` (it streams from
 * `/api/library/circuits/{id}/schematic?mode=`), so it renders immediately and works in
 * the browse preview without waiting on the per-circuit detail. The detail's `schematics`
 * map, when loaded, refines which modes the toggle offers; a per-circuit detail fetch is
 * triggered (de-duped in the store) to get it. A mode that 404s is dropped via `onError`,
 * falling through to the next; an unrendered circuit shows a placeholder.
 */
const PRIMARY_MODES = ["block_aware", "hierarchical", "pure"] as const;
const MODE_LABEL: Record<string, string> = {
  block_aware: "Block-aware",
  hierarchical: "Hierarchical",
  pure: "Pure",
  abstract: "Abstract",
};

export function SchematicViewer({ heightClass = "h-[184px]" }: { heightClass?: string }) {
  const selId = useLibraryStore((s) => s.selId);
  const detail = useLibraryStore((s) => s.detail);
  const fetchDetail = useLibraryStore((s) => s.fetchDetail);
  const [mode, setMode] = useState<string>("block_aware");
  const [failed, setFailed] = useState<Record<string, boolean>>({});
  const [enlarged, setEnlarged] = useState(false);

  // pull the detail (for the accurate mode list + the rest of the datasheet); store de-dupes
  useEffect(() => {
    void fetchDetail(selId);
  }, [selId, fetchDetail]);

  const known = detail !== null && detail.id === selId ? detail.schematics : null;
  // offer the detail's real modes once known, else optimistically the primary three
  const offered = known
    ? PRIMARY_MODES.filter((m) => known[m]).length
      ? PRIMARY_MODES.filter((m) => known[m])
      : known.abstract
        ? ["abstract"]
        : []
    : [...PRIMARY_MODES];
  const modes = offered.filter((m) => !failed[`${selId}:${m}`]);
  const activeMode = modes.includes(mode) ? mode : modes[0];

  if (!activeMode) {
    return (
      <Hatch
        label={`${selId} — no schematic rendered`}
        note="analog-db export-raw --svg"
        heightClass={heightClass}
        className="rounded-lg border-border"
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-panel">
      <div className="flex items-center gap-1 border-b border-hairline px-2 py-1.5">
        {modes.map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={cn(
              "rounded-sm px-2 py-0.5 text-[10px] font-medium transition",
              activeMode === m ? "bg-primary text-white" : "text-muted hover:bg-hairline",
            )}
          >
            {MODE_LABEL[m] ?? m}
          </button>
        ))}
        <div className="flex-1" />
        <span className="font-mono text-[9px] text-faint">{activeMode}.svg</span>
        <button
          type="button"
          onClick={() => setEnlarged(true)}
          aria-label="Enlarge schematic"
          title="Enlarge (click the big view to zoom)"
          className="rounded-sm p-0.5 text-faint transition hover:bg-hairline hover:text-fg"
        >
          <Maximize2 className="h-3 w-3" />
        </button>
      </div>
      <button
        type="button"
        onClick={() => setEnlarged(true)}
        title="Click to enlarge"
        className={cn("flex w-full cursor-zoom-in items-center justify-center bg-white p-2", heightClass)}
      >
        {/* dynamic external SVG streamed from the API; a plain <img> (next/image can't optimize SVG) */}
        <img
          key={`${selId}:${activeMode}`}
          src={librarySchematicUrl(selId, activeMode)}
          alt={`${selId} ${activeMode} schematic`}
          onError={() => setFailed((f) => ({ ...f, [`${selId}:${activeMode}`]: true }))}
          className="max-h-full max-w-full object-contain"
        />
      </button>
      {enlarged && (
        <Lightbox
          src={librarySchematicUrl(selId, activeMode)}
          alt={`${selId} ${activeMode} schematic`}
          caption={`${selId} · ${activeMode}.svg`}
          onClose={() => setEnlarged(false)}
        />
      )}
    </div>
  );
}
