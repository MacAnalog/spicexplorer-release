"use client";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { PreviewLine } from "@/lib/library/wizard";

/** Small bold uppercase-ish field label (the wizard form's field caption). */
export function FieldLabel({ children, hint }: { children: ReactNode; hint?: ReactNode }) {
  return (
    <div className="mb-1.5 text-[10px] font-semibold text-[#52525b]">
      {children}
      {hint && <span className="font-normal text-faint"> · {hint}</span>}
    </div>
  );
}

/** Labelled text input (mono by default — the Studio's signature for ids/params). */
export function TextField({
  label,
  hint,
  value,
  onChange,
  placeholder,
  mono = true,
  caption,
}: {
  label?: ReactNode;
  hint?: ReactNode;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  mono?: boolean;
  caption?: ReactNode;
}) {
  return (
    <div>
      {label && <FieldLabel hint={hint}>{label}</FieldLabel>}
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={cn(
          "h-[30px] w-full rounded-md border border-border bg-panel px-2.5 text-[11.5px] outline-hidden focus:border-[#c7d2fe]",
          mono ? "font-mono" : "text-[12px]",
        )}
      />
      {caption && <div className="mt-1 font-mono text-[9.5px] text-faint">{caption}</div>}
    </div>
  );
}

/** A pill choice (filled indigo when active, outline otherwise). */
export function PillChoice({
  active,
  onClick,
  mono = false,
  children,
}: {
  active: boolean;
  onClick: () => void;
  mono?: boolean;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex h-[26px] items-center gap-1.5 rounded-md px-2.5 text-[10.5px] transition",
        mono && "font-mono",
        active ? "bg-primary font-semibold text-white" : "border border-border text-muted hover:border-[#c7d2fe]",
      )}
    >
      {children}
    </button>
  );
}

/** The 40×23 pill switch (Run block detection, testbench Enabled). */
export function Toggle({ on, onClick, label }: { on: boolean; onClick: () => void; label: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      role="switch"
      aria-checked={on}
      aria-label={label}
      className={cn(
        "flex h-[23px] w-10 items-center rounded-full p-0.5 transition",
        on ? "justify-end bg-primary" : "justify-start bg-border",
      )}
    >
      <span className="h-[19px] w-[19px] rounded-full bg-white" />
    </button>
  );
}

/** A 14px checkbox row (analyses, detect families, produces list). */
export function CheckRow({
  on,
  onClick,
  children,
  right,
  bordered = true,
}: {
  on: boolean;
  onClick: () => void;
  children: ReactNode;
  right?: ReactNode;
  bordered?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2.5 px-2.5 py-2 text-left transition",
        bordered ? "rounded-md border border-border hover:border-[#c7d2fe]" : "border-b border-hairline last:border-0 hover:bg-bg",
      )}
    >
      <span
        className={cn(
          "flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded-[4px] text-[9px]",
          on ? "bg-primary text-white" : "border border-[#d4d4d8] bg-panel",
        )}
        aria-hidden
      >
        {on && "✓"}
      </span>
      <span className="min-w-0 flex-1">{children}</span>
      {right}
    </button>
  );
}

/** Mac-window "editor" card rendering a line-numbered, syntax-tinted file. */
export function EditorPane({ title, lines, maxH = "max-h-[270px]" }: { title: string; lines: PreviewLine[]; maxH?: string }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
      <div className="flex h-7 items-center gap-1.5 border-b border-border bg-[#f0f0f1] px-2.5">
        <span className="h-2 w-2 rounded-full bg-[#ef4444]" />
        <span className="h-2 w-2 rounded-full bg-[#eab308]" />
        <span className="h-2 w-2 rounded-full bg-[#22c55e]" />
        <span className="ml-1.5 font-mono text-[10px] text-muted">{title}</span>
      </div>
      <div className={cn("overflow-auto bg-panel py-1.5", maxH)}>
        {lines.map((l) => (
          <div key={l.n} className="flex items-baseline font-mono text-[10px] leading-[1.65]">
            <span className="w-8 shrink-0 select-none pr-2.5 text-right text-[#c4c4cc]">{l.n}</span>
            <span className={cn("whitespace-pre-wrap", l.comment ? "text-[#16a34a]" : "text-[#334155]")}>{l.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
