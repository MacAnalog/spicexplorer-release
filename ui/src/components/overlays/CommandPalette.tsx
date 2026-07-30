"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Route } from "next";
import { useRouter, usePathname } from "next/navigation";
import { useUIStore } from "@/stores/uiStore";
import { useRunStore } from "@/stores/runStore";
import { useProjectStore } from "@/stores/projectStore";
import { ALL_VIEWS } from "@/components/shell/nav";
import { cn } from "@/lib/utils";

interface Command {
  id: string;
  group: string;
  label: string;
  hint?: string;
  /** Disabled commands render greyed and are skipped by keyboard/enter. */
  disabled?: boolean;
  run: () => void;
}

/**
 * ⌘K command palette + global keyboard map. Self-contained: it installs the
 * window keydown listener itself (⌘K toggles, ⌘1..6 switch view, Esc closes),
 * and composes already-built state — nav views, run history, target specs — into
 * one searchable list. Lives in StudioShell so it's available on every view.
 */
export function CommandPalette() {
  const router = useRouter();
  const pathname = usePathname();
  const { commandOpen, openCommand, closeCommand, setSelectedSpec, openRun, openWizard,
    helpOpen, toggleHelp, closeHelp, projectsOpen, openProjects, closeProjects } = useUIStore();
  const { summary, isApplied } = useProjectStore();
  const { history, isRunning, stopRun, rerun } = useRunStore();

  const [query, setQuery] = useState("");
  const [cursor, setCursor] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  // `g`-chord: pressing `g` then a view digit (1..8) navigates without ⌘. Holds the
  // timestamp of the last `g` so the chord expires after ~1s.
  const gChordRef = useRef<number>(0);

  // Stable navigation helper used by both the command list and the key map.
  const go = useCallback((path: string) => router.push(path as Route), [router]);

  // Build the full command list from current app state.
  const commands = useMemo<Command[]>(() => {
    const cmds: Command[] = [];

    // Switch view
    for (const v of ALL_VIEWS) {
      const locked = !!v.requiresProject && !isApplied;
      cmds.push({
        id: `view:${v.id}`,
        group: "Switch view",
        label: v.label,
        hint: `⌘${v.shortcut}`,
        disabled: locked,
        run: () => go(v.path),
      });
    }

    // Jump to spec (deep-link into Score Shaping)
    if (isApplied && summary) {
      for (const spec of summary.target_specs) {
        cmds.push({
          id: `spec:${spec.name}`,
          group: "Jump to spec",
          label: spec.name,
          // A disabled spec isn't shown in Score Shaping, so deep-linking it
          // would silently no-op — mark it non-actionable.
          hint: spec.enable ? "score shaping" : "disabled",
          disabled: !spec.enable,
          run: () => {
            setSelectedSpec(spec.name);
            go("/scoring");
          },
        });
      }
    }

    // Jump to run (focus a past run). Replay records can be re-loaded (rerun
    // re-opens the SSE stream and repopulates the charts); live records have no
    // reloadable event data, so they only get the rail highlight.
    for (const r of history) {
      const replayable = r.kind === "replay" && !!r.checkpointId;
      cmds.push({
        id: `run:${r.id}`,
        group: "Jump to run",
        label: r.label,
        hint: replayable
          ? r.bestScore != null
            ? `replay · best ${r.bestScore.toExponential(2)}`
            : "replay"
          : "live (view-only)",
        run: () => {
          openRun(r.id);
          go("/optimize");
          if (replayable) void rerun(r);
        },
      });
    }

    // Actions
    cmds.push({
      id: "action:new-project",
      group: "Actions",
      label: "New project…",
      hint: "wizard",
      run: () => openWizard(),
    });
    cmds.push({
      id: "action:stop",
      group: "Actions",
      label: "Stop run",
      hint: isRunning ? undefined : "no active run",
      disabled: !isRunning,
      run: () => stopRun(),
    });

    return cmds;
  }, [go, summary, isApplied, history, isRunning, setSelectedSpec, openRun, openWizard, stopRun, rerun]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter(
      (c) => c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q),
    );
  }, [commands, query]);

  // Global key map — installed once.
  useEffect(() => {
    const isTyping = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const tag = target?.tagName?.toLowerCase();
      return tag === "input" || tag === "textarea" || !!target?.isContentEditable;
    };
    const navTo = (shortcut: string) => {
      const view = ALL_VIEWS.find((v) => v.shortcut === shortcut);
      if (view && !(view.requiresProject && !isApplied)) go(view.path);
    };
    const onKey = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (commandOpen) closeCommand();
        else openCommand();
        return;
      }
      // ⌘P → Projects overlay (report.md P3); overrides the browser print dialog.
      if (mod && e.key.toLowerCase() === "p") {
        e.preventDefault();
        if (projectsOpen) closeProjects();
        else openProjects();
        return;
      }
      if (e.key === "Escape") {
        if (commandOpen) { e.preventDefault(); closeCommand(); return; }
        if (helpOpen) { e.preventDefault(); closeHelp(); return; }
        if (projectsOpen) { e.preventDefault(); closeProjects(); return; }
      }
      // `?` (Shift+/) toggles the keyboard-shortcut help sheet (not while typing).
      if (e.key === "?" && !mod && !isTyping(e)) {
        e.preventDefault();
        toggleHelp();
        return;
      }
      // ⌘1..9 / ⌘0 switch view — but not while typing in an input/editor.
      // ("0" belongs to Analyze — digits 1–9 were taken; keep [0-9] in sync with nav.ts.)
      if (mod && /^[0-9]$/.test(e.key)) {
        if (isTyping(e)) return;
        e.preventDefault();
        navTo(e.key);
        return;
      }
      // `g`-chord: `g` then a view digit navigates without a modifier.
      if (!mod && !isTyping(e)) {
        if (e.key.toLowerCase() === "g") {
          gChordRef.current = Date.now();
          return;
        }
        if (/^[0-9]$/.test(e.key) && Date.now() - gChordRef.current < 1000) {
          gChordRef.current = 0;
          e.preventDefault();
          navTo(e.key);
          return;
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // go/router are stable enough for this listener; re-bind on gating change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [commandOpen, helpOpen, projectsOpen, isApplied, openCommand, closeCommand, toggleHelp, closeHelp, openProjects, closeProjects]);

  // Reset query/cursor + focus on open.
  useEffect(() => {
    if (commandOpen) {
      setQuery("");
      setCursor(0);
      // focus after paint
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [commandOpen]);

  // Keep cursor in range as the filtered list changes.
  useEffect(() => {
    setCursor((c) => Math.min(c, Math.max(0, filtered.length - 1)));
  }, [filtered.length]);

  if (!commandOpen && !helpOpen) return null;
  if (!commandOpen && helpOpen) return <ShortcutHelp onClose={closeHelp} />;

  const runAt = (idx: number) => {
    const cmd = filtered[idx];
    if (!cmd || cmd.disabled) return;
    closeCommand();
    cmd.run();
  };

  const onInputKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setCursor((c) => Math.min(c + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setCursor((c) => Math.max(c - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      runAt(cursor);
    }
  };

  // Group the filtered commands while preserving a flat index for the cursor.
  let flatIndex = -1;
  const groups = [...new Set(filtered.map((c) => c.group))];

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-[12vh]"
      onClick={closeCommand}
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
    >
      <div
        className="w-[620px] max-w-[92vw] overflow-hidden rounded-lg border border-border bg-panel shadow-soft"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onInputKey}
          placeholder="Type a command or search… (views, specs, runs)"
          aria-label="Command search"
          className="w-full border-b border-border bg-transparent px-4 py-3 text-sm text-fg outline-hidden placeholder:text-faint"
        />
        <div className="max-h-[50vh] overflow-y-auto py-1">
          {filtered.length === 0 && (
            <div className="px-4 py-6 text-center text-[13px] text-faint">
              No matching commands.
            </div>
          )}
          {groups.map((group) => (
            <div key={group}>
              <div className="px-4 pb-1 pt-2 text-[10px] font-medium uppercase tracking-wider text-faint">
                {group}
              </div>
              {filtered
                .map((c, i) => ({ c, i }))
                .filter(({ c }) => c.group === group)
                .map(({ c }) => {
                  flatIndex += 1;
                  const idx = flatIndex;
                  const active = idx === cursor;
                  return (
                    <button
                      key={c.id}
                      type="button"
                      disabled={c.disabled}
                      onMouseEnter={() => setCursor(idx)}
                      onClick={() => runAt(idx)}
                      className={cn(
                        "flex w-full items-center justify-between gap-3 px-4 py-1.5 text-left text-[13px] transition",
                        active ? "bg-primary-soft text-primary" : "text-fg",
                        c.disabled && "cursor-not-allowed opacity-40",
                      )}
                    >
                      <span className="truncate">{c.label}</span>
                      {c.hint && (
                        <span className="shrink-0 font-mono text-[10px] text-muted">{c.hint}</span>
                      )}
                    </button>
                  );
                })}
            </div>
          ))}
        </div>
        <div className="flex items-center gap-3 border-t border-border px-4 py-1.5 text-[10px] text-faint">
          <span><span className="font-mono">↑↓</span> navigate</span>
          <span><span className="font-mono">↵</span> run</span>
          <span><span className="font-mono">esc</span> close</span>
          <span><span className="font-mono">?</span> shortcuts</span>
          <span className="ml-auto font-mono">{pathname}</span>
        </div>
      </div>
    </div>
  );
}

/** Keyboard-shortcut help sheet (opened with `?`). */
function ShortcutHelp({ onClose }: { onClose: () => void }) {
  const rows: { keys: string; desc: string }[] = [
    { keys: "⌘K", desc: "Open command palette" },
    { keys: "⌘P", desc: "Open projects" },
    { keys: "?", desc: "Toggle this help" },
    { keys: "esc", desc: "Close overlay" },
    { keys: "⌘1 … ⌘9, ⌘0", desc: "Switch view" },
    { keys: "g then 1 … 9, 0", desc: "Switch view (no modifier)" },
  ];
  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-[14vh]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Keyboard shortcuts"
    >
      <div
        className="w-[460px] max-w-[92vw] overflow-hidden rounded-lg border border-border bg-panel shadow-soft"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
          <span className="text-[13px] font-medium text-fg">Keyboard shortcuts</span>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded-sm px-1.5 text-muted hover:text-fg"
          >
            ✕
          </button>
        </div>
        <div className="px-4 py-2">
          {rows.map((r) => (
            <div key={r.keys} className="flex items-center justify-between py-1.5 text-[13px]">
              <span className="text-fg">{r.desc}</span>
              <kbd className="rounded-sm border border-border bg-hairline px-1.5 py-0.5 font-mono text-[11px] text-muted">
                {r.keys}
              </kbd>
            </div>
          ))}
        </div>
        <div className="border-t border-border px-4 py-1.5 text-[10px] text-faint">
          ViewNumbers follow the activity bar order (Setup … Health).
        </div>
      </div>
    </div>
  );
}
