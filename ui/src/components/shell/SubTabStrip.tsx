"use client";
import { cn } from "@/lib/utils";

export interface SubTab<T extends string> {
  id: T;
  label: string;
  /** Disable the tab (e.g. needs an applied project). */
  disabled?: boolean;
  title?: string;
}

interface SubTabStripProps<T extends string> {
  tabs: SubTab<T>[];
  value: T;
  onChange: (id: T) => void;
  className?: string;
  "aria-label"?: string;
}

/**
 * In-view horizontal sub-tab bar. Repurposes the underline-tab styling of the old
 * top-level TabStrip (which was removed once the ActivityBar became the sole
 * top-level nav), but is generic and state-driven — each view owns its active
 * sub-tab as local state and mounts this above its content. Renders nothing for a
 * single (or empty) section so single-section views need no special-casing.
 */
export function SubTabStrip<T extends string>({
  tabs,
  value,
  onChange,
  className,
  ...rest
}: SubTabStripProps<T>) {
  if (tabs.length <= 1) return null;
  return (
    <nav
      role="tablist"
      aria-label={rest["aria-label"] ?? "Sub-views"}
      className={cn(
        "flex h-10 shrink-0 items-stretch gap-0.5 overflow-x-auto whitespace-nowrap border-b border-border bg-panel px-2 *:shrink-0",
        className,
      )}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === value;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            aria-label={tab.label}
            title={tab.title ?? tab.label}
            disabled={tab.disabled}
            onClick={() => !tab.disabled && onChange(tab.id)}
            className={cn(
              "relative -mb-px flex items-center gap-1.5 border-b-[1.5px] px-3 text-[13px] transition",
              isActive
                ? "border-primary font-medium text-primary"
                : "border-transparent text-muted hover:text-fg",
              tab.disabled && "cursor-not-allowed opacity-40 hover:text-muted",
            )}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}
