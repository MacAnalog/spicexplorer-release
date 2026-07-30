"use client";
import { useRef } from "react";
import { usePathname } from "next/navigation";
import { UI } from "@/config";
import { ResizeHandle, useRailSize } from "@/components/ui/resizable";
import { useProjectStore } from "@/stores/projectStore";
import { viewForPath } from "./nav";
import { RailHeading } from "./rails/parts";
import { RunsRail } from "./rails/RunsRail";
import { SpecsRail } from "./rails/SpecsRail";
import { OutlineRail } from "./rails/OutlineRail";

/**
 * Left rail — a persistent frame (project header + version footer) wrapping a
 * per-activity body. The active view's `rail` (nav.ts, the single source of
 * truth) selects the variant: `runs` (history + checkpoints), `specs` (target
 * spec list → Score Shaping), or `outline-solid` (project structure). The frame stays
 * mounted across navigation; only the body swaps.
 */
export function StudioLeftRail() {
  const pathname = usePathname();
  const { summary, isApplied } = useProjectStore();
  const view = viewForPath(pathname);
  const rail = view?.rail ?? "runs";

  const ref = useRef<HTMLElement>(null);
  const [width, setWidth] = useRailSize("ui:rail:shell-left", 200, 160, 420);

  // fullBleed views (Library) supply their own rails — hide the shell's.
  if (view?.fullBleed) return null;

  return (
    <aside
      ref={ref}
      style={{ width }}
      className="relative flex shrink-0 flex-col border-r border-border bg-panel text-xs"
    >
      <ResizeHandle
        edge="right"
        size={width}
        compute={(x) => x - (ref.current?.getBoundingClientRect().left ?? 0)}
        onSize={setWidth}
        resetTo={200}
        label="Resize the left rail"
      />
      <div className="shrink-0 border-b border-border p-3">
        <RailHeading>Project</RailHeading>
        <div className="flex items-center justify-between gap-2 rounded-sm px-1.5 py-1 text-fg">
          <span className="min-w-0 truncate">{summary?.name ?? "no project"}</span>
          <span className="shrink-0 font-mono text-[10px] text-muted">
            {isApplied ? "active" : "draft"}
          </span>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {rail === "runs" && <RunsRail />}
        {rail === "specs" && <SpecsRail />}
        {rail === "outline-solid" && <OutlineRail />}
      </div>

      <div className="shrink-0 border-t border-border p-3 font-mono text-[10px] text-muted">
        {UI.brand.version} · {UI.brand.product}
      </div>
    </aside>
  );
}
