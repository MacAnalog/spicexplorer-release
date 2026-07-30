import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function inputCn(extra?: string) {
  return cn(
    // w-full + min-w-0 so inputs shrink with their grid/flex track instead of
    // forcing a ~20ch minimum that overflows the narrow wizard form column.
    "w-full min-w-0 rounded-md border border-zinc-300 bg-white px-2 py-1 text-sm",
    "focus:outline-hidden focus:ring-1 focus:ring-indigo-500",
    "disabled:bg-zinc-50 disabled:text-zinc-400",
    extra,
  );
}

interface FieldProps {
  label: string;
  hint?: string;
  children: React.ReactNode;
  className?: string;
}

export function Field({ label, hint, children, className }: FieldProps) {
  return (
    <label className={cn("flex min-w-0 flex-col gap-1", className)}>
      <span className="text-[10px] font-medium uppercase tracking-wide text-zinc-500">{label}</span>
      {children}
      {hint && <span className="text-[10px] text-zinc-400">{hint}</span>}
    </label>
  );
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={inputCn(props.className)} />;
}

export function StepHeader({ title, description }: { title: string; description?: string }) {
  return (
    <div className="border-b border-zinc-100 px-4 py-3">
      <div className="text-sm font-semibold text-zinc-800">{title}</div>
      {description && <div className="mt-0.5 text-xs text-zinc-500">{description}</div>}
    </div>
  );
}
