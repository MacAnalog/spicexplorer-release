import { cn } from "@/lib/utils";

interface SeparatorProps {
  orientation?: "vertical" | "horizontal";
  className?: string;
}

export function Separator({
  orientation = "vertical",
  className,
}: SeparatorProps) {
  if (orientation === "horizontal") {
    return <hr className={cn("border-t border-border", className)} />;
  }
  return (
    <span
      role="separator"
      aria-orientation="vertical"
      className={cn("inline-block h-[18px] w-px bg-border", className)}
    />
  );
}
