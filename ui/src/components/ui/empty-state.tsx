import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  children: ReactNode;
  minHeight?: string;
  bordered?: boolean;
  className?: string;
}

export function EmptyState({
  children,
  minHeight = "min-h-40",
  bordered = false,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-center text-xs text-faint",
        minHeight,
        bordered && "rounded-md border border-dashed border-border bg-panel",
        className,
      )}
    >
      {children}
    </div>
  );
}
