import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Diagonal-hatch placeholder standing in for a schematic render. In production
 * these are replaced by the real xschem render / stored SVG (see the handoff
 * "Assets" note). The gradient is the prototype's exact hatch.
 */
const HATCH_BG =
  "repeating-linear-gradient(135deg,#fafafa 0,#fafafa 6px,#f4f4f5 6px,#f4f4f5 7px)";

interface HatchProps {
  label?: ReactNode;
  note?: ReactNode;
  className?: string;
  /** Tailwind height class (e.g. "h-[46px]"). */
  heightClass?: string;
}

export function Hatch({ label, note, className, heightClass = "h-[46px]" }: HatchProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-1 rounded-md border border-hairline",
        heightClass,
        className,
      )}
      style={{ backgroundImage: HATCH_BG }}
    >
      {label !== undefined && (
        <span className="font-mono text-[9.5px] text-faint">{label}</span>
      )}
      {note !== undefined && (
        <span className="font-mono text-[8.5px] text-[#d4d4d8]">{note}</span>
      )}
    </div>
  );
}
