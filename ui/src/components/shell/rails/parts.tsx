import type { ReactNode } from "react";

/** Section heading used across the per-activity left rails. */
export function RailHeading({
  children,
  right,
}: {
  children: ReactNode;
  right?: ReactNode;
}) {
  return (
    <div className="mb-1.5 mt-3 flex items-center justify-between text-[10px] font-medium uppercase tracking-[0.08em] text-faint first:mt-0">
      <span>{children}</span>
      {right}
    </div>
  );
}

/** Muted placeholder shown when a rail has nothing to display yet. */
export function RailHint({ children }: { children: ReactNode }) {
  return <div className="px-1.5 py-1 text-[11px] leading-snug text-faint">{children}</div>;
}
