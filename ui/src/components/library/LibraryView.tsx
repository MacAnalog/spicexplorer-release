"use client";
import { useEffect } from "react";
import { UI } from "@/config";
import { useLibraryStore } from "@/stores/libraryStore";
import { LibraryTabStrip } from "./LibraryTabStrip";
import { LibraryLeftRail } from "./rails/LibraryLeftRail";
import { LibraryRightRail } from "./rails/LibraryRightRail";
import { RegisterWizardOverlay } from "./RegisterWizardOverlay";
import { HomeView } from "./panels/HomeView";
import { CircuitsView } from "./panels/CircuitsView";
import { TemplatesView } from "./panels/TemplatesView";
import { TestbenchesView } from "./panels/TestbenchesView";
import { DatasheetView } from "./panels/DatasheetView";
import { LibraryLog, LibraryStatusBar } from "./LibraryChrome";

/**
 * Reference Library — the self-contained three-pane feature rendered by the
 * `/library` route. Because the design needs library-specific left/right rails
 * (filters, preview, datasheet nav) that differ entirely from the shell's
 * run-centric rails, the `library` nav entry is `fullBleed`: the shell hides its
 * default rails and this view owns the full window area (tab strip + its own
 * three columns). State + the analog-db catalog data live in `libraryStore`;
 * `load()` fetches everything from `/api/library/*` on mount.
 */
export function LibraryView() {
  const tab = useLibraryStore((s) => s.tab);
  const detailOpen = useLibraryStore((s) => s.detailOpen);
  const status = useLibraryStore((s) => s.status);
  const error = useLibraryStore((s) => s.error);
  const unavailableReason = useLibraryStore((s) => s.unavailableReason);
  const railOpen = useLibraryStore((s) => s.railOpen);
  const load = useLibraryStore((s) => s.load);

  useEffect(() => {
    void load();
  }, [load]);

  const center = detailOpen ? (
    <DatasheetView />
  ) : tab === "home" ? (
    <HomeView />
  ) : tab === "circuits" ? (
    <CircuitsView />
  ) : tab === "templates" ? (
    <TemplatesView />
  ) : (
    <TestbenchesView />
  );

  return (
    <div className="flex h-full min-h-0 flex-col">
      {status === "ready" ? (
        <>
          <LibraryTabStrip />
          <div className="flex min-h-0 flex-1">
            <LibraryLeftRail />
            <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">{center}</div>
            {railOpen && <LibraryRightRail />}
          </div>
          <RegisterWizardOverlay />
        </>
      ) : (
        <div className="min-h-0 flex-1">
          <LibraryStatusPanel status={status} error={error} reason={unavailableReason} onRetry={load} />
        </div>
      )}
      {/* the fullBleed view owns its own bottom log + status bar (shell's are hidden) */}
      <LibraryLog />
      <LibraryStatusBar />
    </div>
  );
}

/** Full-bleed status surface shown until the catalog is loaded — loading, the
 *  analog-db-unavailable empty state, or a fetch error with retry. */
function LibraryStatusPanel({
  status,
  error,
  reason,
  onRetry,
}: {
  status: string;
  error: string | null;
  reason: string | null;
  onRetry: () => void;
}) {
  return (
    <div className="flex h-full min-h-0 items-center justify-center bg-bg p-8">
      <div className="max-w-[460px] text-center">
        {status === "idle" || status === "loading" ? (
          <>
            <div className="mx-auto mb-3 h-6 w-6 animate-spin rounded-full border-2 border-border border-t-primary" aria-hidden />
            <div className="text-[13px] font-medium text-muted">Loading the {UI.library.home.title}…</div>
            <div className="mt-1 font-mono text-[10px] text-faint">analog-db catalog · /api/library</div>
          </>
        ) : status === "unavailable" ? (
          <>
            <div className="text-[14px] font-semibold tracking-[-0.01em]">{UI.library.home.title} unavailable</div>
            <div className="mt-2 text-[12px] leading-relaxed text-muted">
              The <span className="font-mono text-[11px]">analog-db</span> catalog isn&apos;t reachable on the
              backend. {reason ? <span className="text-faint">({reason})</span> : null}
            </div>
            <div className="mt-3 rounded-lg border border-hairline bg-panel p-3 text-left font-mono text-[10.5px] leading-relaxed text-muted">
              Install the submodule into the API env:
              <br />
              <span className="text-faint">uv pip install --no-deps -e examples/analog-db &amp;&amp; uv pip install jsonschema</span>
            </div>
          </>
        ) : (
          <>
            <div className="text-[14px] font-semibold tracking-[-0.01em]">Couldn&apos;t load the library</div>
            <div className="mt-2 text-[12px] text-muted">{error ?? "Unexpected error."}</div>
            <button
              type="button"
              onClick={onRetry}
              className="mt-3 inline-flex h-8 items-center rounded-lg bg-primary px-4 text-[11.5px] font-semibold text-white hover:bg-[#4338ca]"
            >
              Retry
            </button>
          </>
        )}
      </div>
    </div>
  );
}
