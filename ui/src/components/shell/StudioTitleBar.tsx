"use client";
import { Command, Plus, FolderOpen } from "lucide-react";
import { UI } from "@/config";
import { useUIStore } from "@/stores/uiStore";
import { useProjectStore } from "@/stores/projectStore";
import { RunControl } from "./RunControl";

/**
 * Top title bar: brand + "+ New project" + ⌘K command-palette trigger. The
 * run/PDK status lives in the StatusBar. The ⌘K button opens the same palette
 * the global ⌘K shortcut does (see CommandPalette); "+ New project" opens the
 * wizard overlay (also reachable from the palette).
 */
export function StudioTitleBar() {
  const openCommand = useUIStore((s) => s.openCommand);
  const openWizard = useUIStore((s) => s.openWizard);
  const openProjects = useUIStore((s) => s.openProjects);
  const projectName = useProjectStore((s) => s.projectName);
  return (
    <header className="flex h-11 shrink-0 items-center gap-3 border-b border-border bg-panel px-3">
      <div className="flex items-baseline gap-2">
        <svg width="18" height="18" viewBox="0 0 18 18" className="self-center">
          <rect x="2" y="2" width="14" height="14" rx="3" fill="#4f46e5" />
          <path
            d="M5 9 L9 13 L13 5"
            stroke="white"
            strokeWidth="1.6"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span className="text-sm font-semibold tracking-[-0.01em] text-fg">
          {UI.brand.name}
        </span>
        <span className="text-[11px] font-medium text-faint">{UI.brand.product}</span>
      </div>

      {/* Project switcher (⌘P) — the active registered project, or a prompt to pick. */}
      <button
        type="button"
        onClick={openProjects}
        title="Switch / create / load project (⌘P)"
        aria-label="Projects"
        className="flex min-w-0 items-center gap-1.5 rounded-md border border-border bg-hairline px-2 py-1 text-[11px] text-fg transition hover:border-primary/40"
      >
        <FolderOpen className="h-3 w-3 shrink-0 text-faint" aria-hidden />
        <span className="max-w-[180px] truncate">{projectName ?? "Select project"}</span>
        <span className="font-mono text-[10px] text-faint">⌘P</span>
      </button>

      <div className="flex-1" />

      <RunControl />

      <button
        type="button"
        onClick={openWizard}
        title="Create a new project with the wizard"
        aria-label="New project"
        className="flex items-center gap-1.5 rounded-md border border-border bg-panel px-2 py-1 text-[11px] text-fg transition hover:border-primary/40 hover:bg-hairline"
      >
        <Plus className="h-3 w-3" aria-hidden />
        New project
      </button>

      <button
        type="button"
        onClick={openCommand}
        title="Command palette (⌘K)"
        aria-label="Open command palette"
        className="flex items-center gap-1.5 rounded-md border border-border bg-hairline px-2 py-1 text-[11px] text-muted transition hover:border-primary/40 hover:text-fg"
      >
        <Command className="h-3 w-3" aria-hidden />
        <span className="font-mono">K</span>
      </button>
    </header>
  );
}
