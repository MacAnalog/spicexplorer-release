"use client";
import type { PVTCornerDef } from "@/types/api";
import { selectCn } from "@/components/ui/select";
import { cornerOptionLabel } from "@/lib/pvt";
import { cn } from "@/lib/utils";

export interface CornerSelectProps {
  corners: PVTCornerDef[];
  /** Selected corner name, or null = "project default (the YAML's active_corner)". */
  value: string | null;
  onChange: (name: string | null) => void;
  /** Include a "Project default" option that maps to null (default true). */
  allowDefault?: boolean;
  /** The YAML's active corner name, shown on the default option for clarity. */
  defaultCorner?: string | null;
  size?: "sm" | "xs";
  disabled?: boolean;
  className?: string;
  "aria-label"?: string;
}

/**
 * Reusable PVT corner picker. Lists every defined corner (Phase 1 runs against a
 * single one, so even `enabled: false` corners are selectable — `enabled` only
 * gates the deferred multi-corner sweep). The "Project default" option sends
 * `null`, meaning "don't override the YAML's active_corner".
 */
export function CornerSelect({
  corners,
  value,
  onChange,
  allowDefault = true,
  defaultCorner,
  size = "sm",
  disabled = false,
  className,
  ...rest
}: CornerSelectProps) {
  return (
    <select
      value={value ?? ""}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
      className={cn(selectCn(size), "w-full", className)}
      aria-label={rest["aria-label"] ?? "PVT corner"}
    >
      {allowDefault && (
        <option value="">
          Project default{defaultCorner ? ` (${defaultCorner})` : ""}
        </option>
      )}
      {corners.map((c) => (
        <option key={c.name} value={c.name}>
          {cornerOptionLabel(c)}
        </option>
      ))}
    </select>
  );
}
