// Single source of truth for Studio navigation.
//
// The shell's top-level nav is the vertical ActivityBar (the redundant horizontal
// TabStrip was removed; views now render their own in-view sub-tabs). The
// ActivityBar and the per-activity left rail are both driven from this one list so
// a view is added/renamed in exactly one place. Routes live under the `(studio)`
// App-Router group, so each view has a real URL.
import {
  Library,
  Wrench,
  SlidersHorizontal,
  Zap,
  Compass,
  CircuitBoard,
  AudioWaveform,
  Workflow,
  FlaskConical,
  Activity,
  type LucideIcon,
} from "lucide-react";

export type StudioViewId =
  | "library"
  | "setup"
  | "scoring"
  | "optimize"
  | "compare"
  | "schematic"
  | "analyze"
  | "pipeline"
  | "manual"
  | "health";

/**
 * Which left-rail variant a view shows. `runs` = run history + checkpoints
 * (run-centric views), `specs` = clickable target-spec list (spec-centric
 * views, deep-link to Score Shaping), `outline-solid` = project structure outline.
 */
export type RailKind = "runs" | "specs" | "outline-solid";

export interface StudioView {
  id: StudioViewId;
  /** Full label (ActivityBar tooltips, command palette). */
  label: string;
  /** App-Router path under the (studio) group. */
  path: string;
  icon: LucideIcon;
  /** ⌘<key> / bare-<key> shortcut. */
  shortcut: string;
  /**
   * When true the view needs an applied project to be useful, so the
   * ActivityBar renders it disabled until `isApplied`. Mirrors the pre-Studio
   * Topbar gating (optimize + shaping were locked until applied).
   */
  requiresProject?: boolean;
  /** Which left-rail variant this view shows (defaults to "runs" if unset). */
  rail: RailKind;
  /**
   * When true the view owns the full window area and supplies its own left/right
   * rails, so the shell hides its default `StudioLeftRail` + `RightRail` (and
   * `rail` is unused). The Library catalog browser is the first such view.
   */
  fullBleed?: boolean;
}

/**
 * Primary workflow views — the top group of the ActivityBar (the sole top-level
 * nav since the redundant horizontal TabStrip was removed). Each view renders its
 * own in-view sub-tabs (see SubTabStrip) instead of a shared top tab bar.
 */
export const PRIMARY_VIEWS: StudioView[] = [
  { id: "library", label: "Library", path: "/library", icon: Library, shortcut: "9", rail: "outline-solid", fullBleed: true },
  { id: "setup", label: "Setup", path: "/setup", icon: Wrench, shortcut: "1", rail: "outline-solid" },
  { id: "scoring", label: "Score Shaping", path: "/scoring", icon: SlidersHorizontal, shortcut: "2", requiresProject: true, rail: "specs" },
  { id: "optimize", label: "Optimize", path: "/optimize", icon: Zap, shortcut: "3", requiresProject: true, rail: "runs" },
  { id: "compare", label: "Explore", path: "/compare", icon: Compass, shortcut: "4", rail: "runs" },
  { id: "schematic", label: "Schematic", path: "/schematic", icon: CircuitBoard, shortcut: "5", rail: "outline-solid" },
  // Waveform viewer. Digits 1–9 were already assigned when this view landed, so it
  // takes "0" (the ⌘/g-chord regex in CommandPalette is widened to [0-9] to match).
  { id: "analyze", label: "Analyze", path: "/analyze", icon: AudioWaveform, shortcut: "0", rail: "outline-solid", fullBleed: true },
];

/**
 * Utility views — the bottom group of the ActivityBar, just above the Health gear.
 * Secondary tools (read-only Pipeline, one-shot Manual Sim) kept apart from the
 * primary workflow so the main flow reads top-to-bottom uninterrupted.
 */
export const UTILITY_VIEWS: StudioView[] = [
  { id: "pipeline", label: "Pipeline", path: "/pipeline", icon: Workflow, shortcut: "6", requiresProject: true, rail: "specs" },
  { id: "manual", label: "Manual Sim", path: "/manual", icon: FlaskConical, shortcut: "7", requiresProject: true, rail: "runs" },
];

/** Settings/diagnostics — reached via the ActivityBar gear (the Health check). */
export const SETTINGS_VIEW: StudioView = {
  id: "health",
  label: "Health",
  path: "/health",
  icon: Activity,
  shortcut: "8",
  rail: "outline-solid",
};

export const ALL_VIEWS: StudioView[] = [...PRIMARY_VIEWS, ...UTILITY_VIEWS, SETTINGS_VIEW];

/** Resolve the active view from a pathname (e.g. "/optimize" -> optimize view). */
export function viewForPath(pathname: string): StudioView | undefined {
  return ALL_VIEWS.find(
    (v) => pathname === v.path || pathname.startsWith(v.path + "/"),
  );
}
