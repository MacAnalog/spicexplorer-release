import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { PdkKey } from "@/lib/library/types";
import { engineMeta, engineMetaFallback, pdkChipMeta, pdkLabel } from "@/lib/library/data";

/**
 * Small palette chip used across the Library for class / compensation / PDK /
 * testbench-class tags. The catalog carries arbitrary per-class hex pairs (the
 * brand tokens), so this takes explicit bg/fg rather than a fixed variant set
 * like the shared `Badge`.
 */
export function Chip({
  bg,
  fg,
  mono = true,
  className,
  title,
  children,
}: {
  bg: string;
  fg: string;
  mono?: boolean;
  className?: string;
  /** Native tooltip — pass when the chip text may be truncated by the caller. */
  title?: string;
  children: ReactNode;
}) {
  return (
    <span
      title={title}
      className={cn(
        "inline-flex items-center gap-1 overflow-hidden rounded-sm px-1.5 py-[2px] text-[9px] font-semibold leading-none",
        mono && "font-mono",
        className,
      )}
      style={{ background: bg, color: fg }}
    >
      {children}
    </span>
  );
}

/** The wrapping row of PDK chips on a circuit card / preview. */
export function PdkChips({ pdks, className }: { pdks: PdkKey[]; className?: string }) {
  return (
    <div className={cn("flex flex-wrap gap-1", className)}>
      {pdks.map((p) => {
        const { bg, fg } = pdkChipMeta[p];
        return (
          <Chip key={p} bg={bg} fg={fg} className="font-medium">
            {pdkLabel[p]}
          </Chip>
        );
      })}
    </div>
  );
}

/** The row of supported-simulator chips for a testbench (repo-derived, never asserted). */
export function EngineChips({ engines, className }: { engines: string[]; className?: string }) {
  if (!engines.length) return <span className="font-mono text-[9.5px] text-faint">no source</span>;
  return (
    <div className={cn("flex flex-wrap gap-1", className)}>
      {engines.map((e) => {
        const { bg, fg } = engineMeta[e] ?? engineMetaFallback;
        return (
          <Chip key={e} bg={bg} fg={fg}>
            {e}
          </Chip>
        );
      })}
    </div>
  );
}

/** Uppercase section eyebrow (the Studio's signature small caps label). */
export function Eyebrow({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "text-[9.5px] font-bold uppercase tracking-[0.08em] text-faint",
        className,
      )}
    >
      {children}
    </div>
  );
}
