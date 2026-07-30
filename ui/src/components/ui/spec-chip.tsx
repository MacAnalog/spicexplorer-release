import { cn } from "@/lib/utils";

interface SpecChipProps {
  name: string;
  value: string;
  target?: string;
  status: "ok" | "fail" | "neutral";
  className?: string;
}

export function SpecChip({ name, value, target, status, className }: SpecChipProps) {
  const colorClass =
    status === "ok"
      ? "border-ok bg-[#f0fdf4]"
      : status === "fail"
        ? "border-danger bg-danger-soft"
        : "border-border bg-panel";
  const dotColor =
    status === "ok" ? "bg-ok" : status === "fail" ? "bg-danger" : "bg-faint";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm border px-2 py-1 text-[11px]",
        colorClass,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", dotColor)} />
      <span className="font-mono">{name}</span>
      <span className="font-mono font-medium">{value}</span>
      {target && (
        <span className="font-mono text-[10px] text-muted">{target}</span>
      )}
    </span>
  );
}
