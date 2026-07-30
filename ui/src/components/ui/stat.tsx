import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatProps {
  eyebrow: ReactNode;
  value: ReactNode;
  /** Small unit suffix rendered next to the value (e.g. "MHz", "✅"). */
  unit?: ReactNode;
  /** Colors the value — pass for status KPIs (green pass / red fail). */
  tone?: "default" | "ok" | "danger" | "warn";
  delta?: ReactNode;
  deltaTone?: "up" | "down" | "neutral";
  /** Progress bar fraction 0..1 — rendered if provided. */
  progress?: number;
  className?: string;
}

export function Stat({
  eyebrow,
  value,
  unit,
  tone = "default",
  delta,
  deltaTone = "neutral",
  progress,
  className,
}: StatProps) {
  return (
    <div
      className={cn(
        "rounded-md border border-border bg-panel px-3 py-2",
        className,
      )}
    >
      <div className="text-[10px] font-medium uppercase tracking-wider text-muted">
        {eyebrow}
      </div>
      <div
        className={cn(
          "mt-0.5 font-mono text-[18px]",
          tone === "default" && "text-fg",
          tone === "ok" && "text-ok",
          tone === "danger" && "text-danger",
          tone === "warn" && "text-tertiary",
        )}
      >
        {value}
        {unit !== undefined && (
          <span className="ml-1 text-[11px] text-muted">{unit}</span>
        )}
      </div>
      {progress !== undefined && (
        <div className="mt-2 h-1 overflow-hidden rounded-xs bg-hairline">
          <div
            className="h-full bg-primary transition-[width] duration-300"
            style={{ width: `${Math.max(0, Math.min(1, progress)) * 100}%` }}
          />
        </div>
      )}
      {delta && (
        <div
          className={cn(
            "mt-1 text-[11px]",
            deltaTone === "up" && "text-ok",
            deltaTone === "down" && "text-danger",
            deltaTone === "neutral" && "text-muted",
          )}
        >
          {delta}
        </div>
      )}
    </div>
  );
}
