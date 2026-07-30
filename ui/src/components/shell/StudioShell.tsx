"use client";
import { useEffect } from "react";
import { useExplorerStore } from "@/stores/explorerStore";
import { useUIStore } from "@/stores/uiStore";
import { api } from "@/lib/api";
import { StudioTitleBar } from "./StudioTitleBar";
import { ActivityBar } from "./ActivityBar";
import { StudioLeftRail } from "./StudioLeftRail";
import { RightRail } from "./RightRail";
import { BottomPanel } from "./BottomPanel";
import { StatusBar } from "./StatusBar";
import { CommandPalette } from "@/components/overlays/CommandPalette";
import { WizardOverlay } from "@/components/overlays/WizardOverlay";
import { ProjectsOverlay } from "@/components/overlays/ProjectsOverlay";

/**
 * Studio shell — composition root rendered by the `(studio)` route-group layout.
 * Because it's a layout, it stays mounted across view (route) changes, so the
 * left rail, status bar, and (in later phases) the right rail + bottom panel +
 * live SSE stream survive navigation. The active route's page renders in the
 * center via {children}.
 *
 * Layout:
 *   StudioTitleBar
 *   [ ActivityBar | LeftRail | center children ]
 *   StatusBar
 *
 * The ActivityBar is the sole top-level nav; each center view renders its own
 * in-view sub-tabs (SubTabStrip), so there is no shared horizontal tab strip.
 */
export function StudioShell({ children }: { children: React.ReactNode }) {
  const setAppConfig = useUIStore((s) => s.setAppConfig);
  const setEnv = useUIStore((s) => s.setEnv);
  const setAvailableCheckpoints = useExplorerStore((s) => s.setAvailableCheckpoints);

  // Hydrate shared session data once. Lives here (not in a page) so it runs a
  // single time regardless of which view the user deep-links into.
  useEffect(() => {
    api.config().then(setAppConfig).catch(() => null);
    api.env().then(setEnv).catch(() => null);
    api.listCheckpoints().then(setAvailableCheckpoints).catch(() => null);
  }, [setAppConfig, setEnv, setAvailableCheckpoints]);

  return (
    <div className="flex h-screen flex-col bg-bg text-fg">
      <StudioTitleBar />
      <div className="flex min-h-0 flex-1 overflow-hidden">
        <ActivityBar />
        <StudioLeftRail />
        <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
          <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
            {children}
          </div>
          <BottomPanel />
        </section>
        <RightRail />
      </div>
      <StatusBar />
      <CommandPalette />
      <WizardOverlay />
      <ProjectsOverlay />
    </div>
  );
}
