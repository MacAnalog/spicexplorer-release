"use client";
import { cn } from "@/lib/utils";
import type { CircuitCardData } from "@/lib/library/selectors";
import type { PdkKey } from "@/lib/library/types";
import { Hatch } from "./Hatch";
import { Chip, PdkChips } from "./chips";

/**
 * Circuit card for the Home and Circuits grids. `grid` (Circuits) shows the
 * mono id, sub line, PDK chips, a hairline, and a result dot + selected ring;
 * `home` is the compact variant (name + comp chip + hatch + gain/analyses).
 */
export function CircuitCard({
  card,
  pdks,
  variant,
  onOpen,
}: {
  card: CircuitCardData;
  pdks: PdkKey[];
  variant: "home" | "grid";
  onOpen: () => void;
}) {
  const grid = variant === "grid";
  return (
    <button
      type="button"
      onClick={onOpen}
      className={cn(
        "relative flex flex-col gap-2 rounded-lg border border-border bg-panel p-3 text-left transition",
        "hover:border-[#c7d2fe] hover:shadow-[0_4px_14px_-6px_rgba(79,70,229,0.25)]",
      )}
    >
      {grid && card.selected && (
        <span
          className="pointer-events-none absolute -inset-px rounded-lg border-[1.5px] border-primary"
          aria-hidden
        />
      )}
      <div className="flex items-start justify-between gap-1.5">
        {/* Long catalog names (compensation variants) used to wrap 5+ lines and turn
            the grid into a ragged masonry — clamp to 2, full name in the tooltip. */}
        <div
          title={card.name}
          className={cn(
            "line-clamp-2 font-semibold leading-tight tracking-[-0.01em]",
            grid ? "text-[12.5px]" : "text-[12px]",
          )}
        >
          {card.name}
        </div>
        <Chip
          bg={card.classBg}
          fg={card.classFg}
          className="max-w-[45%] shrink-0"
          title={card.compLabel}
        >
          <span className="truncate">{card.compLabel}</span>
        </Chip>
      </div>

      {grid && <div className="font-mono text-[9px] text-faint">{card.id}</div>}

      <Hatch label={`${card.id}.sch`} heightClass={grid ? "h-[46px]" : "h-[42px]"} />

      {grid && <div className="text-[10px] text-muted">{card.sub}</div>}
      {grid && <PdkChips pdks={pdks} />}
      {grid && <div className="h-px bg-hairline" />}

      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-1">
          <span className="text-[9px] uppercase text-faint">gain</span>
          <span className={cn("font-mono font-semibold", grid ? "text-[12.5px]" : "text-[12px]")}>{card.metricValue}</span>
          {card.metricUnit && <span className="font-mono text-[8.5px] text-muted">{card.metricUnit}</span>}
        </div>
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[8.5px] text-faint">{card.nTb} an.</span>
          <span
            className={cn("inline-block h-1.5 w-1.5 rounded-full", card.hasResults ? "bg-ok" : "bg-[#d4d4d8]")}
            aria-hidden
          />
        </div>
      </div>
    </button>
  );
}
