"use client";
import { useCallback } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { useProjectStore } from "@/stores/projectStore";
import { useWizardStore } from "@/stores/wizardStore";
import { api } from "@/lib/api";
import { WizardShell } from "@/components/wizard/WizardShell";

/**
 * Full-screen "+ New project" overlay hosting the existing 7-step WizardShell,
 * launchable from the title bar and the ⌘K palette. On save it loads + applies
 * the generated project (same flow SetupTab uses), closes, and routes to /setup
 * so the user lands on the freshly-applied YAML.
 */
export function WizardOverlay() {
  const router = useRouter();
  const wizardOpen = useUIStore((s) => s.wizardOpen);
  const closeWizard = useUIStore((s) => s.closeWizard);
  const { apply } = useProjectStore();
  const resetWizard = useWizardStore((s) => s.reset);

  const handleSaved = useCallback(
    async (savedPath: string) => {
      try {
        const res = await api.loadProject(savedPath);
        if (res.ok) apply(res.summary, savedPath);
      } catch {
        /* the wizard surfaces save/validation errors inline */
      }
      closeWizard();
      router.push("/setup" as Route);
    },
    [apply, closeWizard, router],
  );

  if (!wizardOpen) return null;

  return (
    <div
      className="fixed inset-0 z-40 flex flex-col bg-bg"
      role="dialog"
      aria-modal="true"
      aria-label="New project wizard"
    >
      <header className="flex h-11 shrink-0 items-center justify-between border-b border-border bg-panel px-4">
        <span className="text-sm font-semibold text-fg">
          New project
          <span className="ml-2 text-[11px] font-normal text-faint">
            generate a project_setup.yaml
          </span>
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              resetWizard();
            }}
            className="rounded-sm border border-border px-2 py-1 text-[11px] text-muted hover:bg-hairline hover:text-fg"
          >
            Reset
          </button>
          <button
            type="button"
            onClick={closeWizard}
            aria-label="Close wizard"
            title="Close"
            className="rounded-sm p-1 text-faint hover:bg-hairline hover:text-fg"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </header>
      <div className="min-h-0 flex-1 overflow-hidden p-3">
        <WizardShell onSaved={handleSaved} />
      </div>
    </div>
  );
}
