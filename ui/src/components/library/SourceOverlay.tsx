"use client";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { SpiceEditor } from "@/components/ui/SpiceEditor";

interface Source {
  path: string;
  language: string;
  content: string;
}

/**
 * Full-screen read-only source viewer (netlists, bench wiring YAML). The caller
 * hands a loader so each open fetches fresh from the DB; Esc or ✕ closes. Used
 * by the Templates "View netlist" button and the datasheet's bench-source links.
 */
export function SourceOverlay({
  title,
  load,
  onClose,
}: {
  title: string;
  load: () => Promise<Source>;
  onClose: () => void;
}) {
  const [src, setSrc] = useState<Source | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    load()
      .then((s) => live && setSrc(s))
      .catch((e) => live && setError(e instanceof Error ? e.message : "failed to load source"));
    return () => {
      live = false;
    };
  }, [load]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div role="dialog" aria-modal="true" aria-label={title} className="fixed inset-0 z-100 flex flex-col bg-panel">
      <div className="flex h-[36px] shrink-0 items-center gap-2.5 border-b border-border px-4">
        <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted">Source</span>
        <span className="font-mono text-[11px] font-semibold">{title}</span>
        {src && <span className="min-w-0 truncate font-mono text-[9.5px] text-faint">{src.path}</span>}
        <div className="flex-1" />
        <span className="font-mono text-[9px] text-faint">read-only · Esc closes</span>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close source viewer"
          className="rounded-sm p-1 text-muted transition hover:bg-hairline hover:text-fg"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="min-h-0 flex-1">
        {error ? (
          <div className="flex h-full items-center justify-center px-6 text-center text-[11px] text-muted">{error}</div>
        ) : src ? (
          <SpiceEditor value={src.content} language={src.language} />
        ) : (
          <div className="flex h-full items-center justify-center font-mono text-[10px] text-faint">loading…</div>
        )}
      </div>
    </div>
  );
}
