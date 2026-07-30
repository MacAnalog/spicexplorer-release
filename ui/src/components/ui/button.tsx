import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "primary" | "danger" | "ghost" | "secondary";
  size?: "sm" | "md";
};

export function Button({
  className,
  variant = "default",
  size = "sm",
  ...props
}: ButtonProps) {
  const variants = {
    default:
      "border border-border bg-panel text-fg hover:bg-hairline",
    secondary:
      "border border-border bg-panel text-fg hover:bg-hairline",
    primary:
      "border border-primary bg-primary text-white hover:bg-[#4338ca]",
    danger:
      "border border-danger bg-danger text-white hover:bg-[#b91c1c]",
    ghost:
      "border border-transparent bg-transparent text-fg hover:bg-hairline",
  } as const;

  const sizes = {
    sm: "h-[26px] px-2.5 text-[11px]",
    md: "h-8 px-3 text-xs",
  } as const;

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-1.5 rounded-sm font-medium transition disabled:pointer-events-none disabled:opacity-50",
        sizes[size],
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
