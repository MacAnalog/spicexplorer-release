import type { Config } from "tailwindcss";
import { ACCENT } from "./src/config/colors";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Surface
        bg: "#fafafa",
        panel: "#ffffff",
        hairline: "#f4f4f5",
        border: "#e4e4e7",
        // Ink
        fg: "#0a0a0a",
        muted: "#71717a",
        faint: ACCENT.faint,
        // Brand
        primary: ACCENT.primary,
        "primary-soft": ACCENT.primarySoft,
        secondary: ACCENT.secondary,
        "secondary-soft": ACCENT.secondarySoft,
        tertiary: ACCENT.tertiary,
        // Status
        ok: ACCENT.ok,
        "ok-soft": "#d1fae5",
        danger: "#dc2626",
        "danger-soft": "#fef2f2",
        "warn-soft": ACCENT.amberSoft,
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter Tight", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        soft: "0 14px 40px rgba(16, 20, 24, 0.08)",
        seg: "0 1px 2px rgba(0,0,0,0.06)",
      },
    },
  },
  plugins: [],
};

export default config;
