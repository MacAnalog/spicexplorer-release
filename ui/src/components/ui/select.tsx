import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const sizeStyles = {
  sm: "h-[26px] py-0 text-xs",
  xs: "h-[22px] py-0 text-[11px]",
} as const;

type SelectSize = keyof typeof sizeStyles;

export function selectCn(selectSize: SelectSize = "sm") {
  return cn(
    // min-w-0 lets a select shrink inside a flex/grid track (toolbar items are
    // shrink-0 so they're unaffected). No w-full here — that would stretch
    // toolbar selects to fill the row.
    "min-w-0 rounded-sm border border-border bg-panel px-2 text-fg",
    sizeStyles[selectSize],
    "focus:outline-hidden focus:ring-1 focus:ring-primary",
    "disabled:bg-hairline disabled:text-faint disabled:opacity-60",
  );
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  selectSize?: SelectSize;
  options?: { value: string; label: string }[];
  children?: ReactNode;
  className?: string;
}

export function Select({
  label,
  selectSize = "sm",
  options,
  children,
  className,
  ...props
}: SelectProps) {
  const select = (
    <select
      className={cn("block", label ? "w-full" : "", selectCn(selectSize), className)}
      {...props}
    >
      {children ??
        options?.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
    </select>
  );
  if (!label) return select;
  return (
    <div className="flex flex-col gap-1">
      <label
        className="text-[10px] font-medium uppercase tracking-wider text-muted"
        htmlFor={props.id}
      >
        {label}
      </label>
      {select}
    </div>
  );
}
