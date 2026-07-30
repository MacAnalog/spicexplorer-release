/**
 * Shared accent color tokens — the ONE definition of the Studio accent hexes.
 * Imported by `tailwind.config.ts` (theme tokens), `lib/library/data.ts`
 * (class / PDK chip palettes) and `lib/waveview/config.ts` (trace colorway),
 * so changing a brand accent happens here once. Keys mirror the Tailwind
 * token names. Hex values only — which accent a view *uses* stays in that
 * view's config module.
 */
export const ACCENT = {
  primary: "#4f46e5",
  primarySoft: "#eef2ff",
  secondary: "#0891b2",
  secondarySoft: "#ecfeff",
  tertiary: "#ea580c",
  tertiarySoft: "#fff7ed",
  violet: "#7c3aed",
  violetSoft: "#f5f3ff",
  ok: "#059669",
  amber: "#b45309",
  amberSoft: "#fef3c7",
  faint: "#a1a1aa",
} as const;
