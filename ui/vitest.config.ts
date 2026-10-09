import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// Unit tests run in Node with no DOM. Most test pure data transforms under
// src/lib; a component test renders to an HTML string with react-dom/server
// (src/components/wizard/steps/OptimizerStep.test.tsx). The `@/` alias mirrors
// tsconfig `paths` so test imports match app imports.
export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
});
