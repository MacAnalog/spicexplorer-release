import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// Unit tests for the pure logic layer (lib/library adapters + selectors). Node
// environment — these are pure data transforms, no DOM. The `@/` alias mirrors
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
