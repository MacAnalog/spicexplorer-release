import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ToolbarProps {
  children: ReactNode;
  className?: string;
}

export function Toolbar({ children, className }: ToolbarProps) {
  return (
    <div
      className={cn(
        // shrink-0 prevents the toolbar from collapsing inside its parent
        // flex-nowrap + overflow-x-auto keeps all controls on one line and
        // lets the toolbar scroll horizontally if the viewport is too narrow.
        // *:shrink-0 stops individual controls from being squashed.
        "flex shrink-0 flex-nowrap items-center gap-2 overflow-x-auto border-b border-border bg-panel px-4 py-2 whitespace-nowrap *:shrink-0",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function ToolbarLabel({ children }: { children: ReactNode }) {
  return (
    <span className="whitespace-nowrap text-[11px] text-muted">
      {children}
    </span>
  );
}

export function ToolbarSpacer() {
  return <div className="flex-1" />;
}
