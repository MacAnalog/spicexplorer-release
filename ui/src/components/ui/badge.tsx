import { cn } from "@/lib/utils";

export type BadgeVariant =
  | "ok"
  | "pass"
  | "fail"
  | "warn"
  | "warning"
  | "neutral"
  | "indigo"
  | "live"
  | "cyan";

const variants: Record<BadgeVariant, string> = {
  ok: "bg-ok-soft text-ok",
  pass: "bg-ok-soft text-ok",
  fail: "bg-danger-soft text-danger",
  warn: "bg-warn-soft text-[#b45309]",
  warning: "bg-warn-soft text-[#b45309]",
  neutral: "bg-hairline text-muted",
  indigo: "bg-primary-soft text-primary",
  live: "bg-primary-soft text-primary",
  cyan: "bg-secondary-soft text-secondary",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  dot?: boolean;
  pulse?: boolean;
  className?: string;
}

export function Badge({
  children,
  variant = "neutral",
  dot = false,
  pulse = false,
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2 py-[2px] text-[11px] font-medium leading-none",
        variants[variant],
        className,
      )}
    >
      {dot && (
        <span
          className={cn(
            "h-1.5 w-1.5 rounded-full bg-current",
            pulse && "obs-pulse",
          )}
        />
      )}
      {children}
    </span>
  );
}
