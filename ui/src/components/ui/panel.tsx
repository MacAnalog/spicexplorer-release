"use client";
import type { HTMLAttributes, ReactNode } from "react";
import { useEffect, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function Panel({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <section
      className={cn(
        "overflow-hidden rounded-md border border-border bg-panel",
        className,
      )}
      {...props}
    />
  );
}

interface PanelHeaderProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  title?: ReactNode;
  mute?: ReactNode;
  right?: ReactNode;
}

export function PanelHeader({
  className,
  title,
  mute,
  right,
  children,
  ...props
}: PanelHeaderProps) {
  if (title !== undefined || mute !== undefined || right !== undefined) {
    return (
      <div
        className={cn(
          "flex items-center justify-between border-b border-border px-3 py-[7px]",
          className,
        )}
        {...props}
      >
        <div className="text-[11px] font-medium leading-none text-fg">
          {title}
          {mute && (
            <span className="ml-1 font-normal text-muted">{mute}</span>
          )}
        </div>
        {right && <div className="flex items-center gap-1.5">{right}</div>}
      </div>
    );
  }
  return (
    <div
      className={cn(
        "flex items-center justify-between border-b border-border px-3 py-[7px] text-[11px] font-medium leading-none",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function PanelBody({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-3 py-2.5", className)} {...props} />;
}

interface CollapsiblePanelProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  /** Stable key — collapse state persists to localStorage as `panel:<storageId>`. */
  storageId: string;
  title?: ReactNode;
  mute?: ReactNode;
  right?: ReactNode;
  defaultOpen?: boolean;
  children?: ReactNode;
}

/**
 * A Panel whose body collapses via a header chevron, persisting per-panel open
 * state to localStorage. Opt-in wrapper so the ~25 plain Panels are unaffected.
 */
export function CollapsiblePanel({
  storageId,
  title,
  mute,
  right,
  defaultOpen = true,
  className,
  children,
  ...props
}: CollapsiblePanelProps) {
  const key = `panel:${storageId}`;
  const [open, setOpen] = useState(defaultOpen);
  // Hydrate from localStorage after mount (avoids SSR mismatch).
  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(key);
      if (saved != null) setOpen(saved === "1");
    } catch {
      /* ignore */
    }
  }, [key]);
  const toggle = () => {
    setOpen((prev) => {
      const next = !prev;
      try {
        window.localStorage.setItem(key, next ? "1" : "0");
      } catch {
        /* ignore */
      }
      return next;
    });
  };
  return (
    <Panel className={className} {...props}>
      <div className="flex items-center justify-between border-b border-border px-3 py-[7px]">
        <button
          type="button"
          onClick={toggle}
          className="flex items-center gap-1 text-[11px] font-medium leading-none text-fg"
          aria-expanded={open ? "true" : "false"}
        >
          {open ? (
            <ChevronDown className="h-3 w-3 text-faint" />
          ) : (
            <ChevronRight className="h-3 w-3 text-faint" />
          )}
          {title}
          {mute && <span className="ml-1 font-normal text-muted">{mute}</span>}
        </button>
        {right && <div className="flex items-center gap-1.5">{right}</div>}
      </div>
      {open && children}
    </Panel>
  );
}
