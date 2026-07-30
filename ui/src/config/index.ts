import ui from "./ui.json";

/**
 * Central UI content/constants (`src/config/ui.json`) — the ONE place to update
 * user-facing copy, branding, featured ids, and presentation knobs without
 * touching component code. Typed by inference from the JSON, so a typo'd key is
 * a compile error at the use site.
 *
 * Boundary: presentation content ONLY. Anything the backend knows (catalog,
 * runs, measurements, schematics) stays backend-driven — never mirror data
 * here. Per-view *styling* config (colors, plot styles, orderings) stays in its
 * view module (`lib/waveview/config.ts`, `lib/library/data.ts`).
 */
export const UI = ui;
