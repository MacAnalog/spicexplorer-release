"use client";
import { useMemo } from "react";
import { useProjectStore } from "@/stores/projectStore";
import { cn } from "@/lib/utils";
import { parseDeviceKind } from "@/lib/params";
import { RailHeading, RailHint } from "./parts";

/**
 * Structure rail (Setup, Schematic, Health): a compact outline of the applied
 * project — testbenches with enable state, DUT devices (parsed from param
 * names), and target specs. Read-only orientation, no actions.
 */
export function OutlineRail() {
  const { summary, isApplied } = useProjectStore();

  const devices = useMemo(() => {
    const out: string[] = [];
    for (const p of summary?.dut_params ?? []) {
      const { device } = parseDeviceKind(p.name);
      if (!out.includes(device)) out.push(device);
    }
    return out;
  }, [summary]);

  if (!isApplied || !summary) {
    return (
      <>
        <RailHeading>Outline</RailHeading>
        <RailHint>Apply a project on Setup to see its structure.</RailHint>
      </>
    );
  }

  return (
    <>
      <RailHeading>Testbenches</RailHeading>
      {summary.testbenches.length === 0 ? (
        <RailHint>None.</RailHint>
      ) : (
        summary.testbenches.map((tb) => (
          <div key={tb.name} className="flex items-center justify-between px-1.5 py-1">
            <span className="truncate text-[11px]">{tb.name}</span>
            <span
              className={cn("h-1.5 w-1.5 shrink-0 rounded-full", tb.enable ? "bg-ok" : "bg-faint")}
              title={tb.enable ? "enabled" : "disabled"}
              aria-hidden
            />
          </div>
        ))
      )}

      <RailHeading>Devices · {devices.length}</RailHeading>
      {devices.length === 0 ? (
        <RailHint>No DUT parameters.</RailHint>
      ) : (
        <div className="flex flex-wrap gap-1 px-1.5 py-1">
          {devices.map((d) => (
            <span
              key={d}
              className="rounded-sm border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted"
            >
              {d}
            </span>
          ))}
        </div>
      )}

      <RailHeading>Specs · {summary.target_specs.length}</RailHeading>
      {summary.target_specs.map((s) => (
        <div
          key={s.name}
          className={cn(
            "flex items-center justify-between px-1.5 py-0.5 text-[11px]",
            !s.enable && "opacity-50",
          )}
        >
          <span className="truncate">{s.name}</span>
          <span className="shrink-0 font-mono text-[9px] text-faint">{s.goal}</span>
        </div>
      ))}
    </>
  );
}
