import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

// eslint-config-next 16 ships native flat configs (arrays), so they are spread
// directly — the old FlatCompat.extends("next/…") wrapper now double-wraps a flat
// config and throws a circular-schema error.
const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypescript,
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts", "src/types/api.gen.ts"] },
  {
    rules: {
      "@next/next/no-img-element": "off",
    },
  },
  // eslint-config-next 16 turned on eslint-plugin-react-hooks v6/v7's React-Compiler
  // rules. They are ENABLED globally (new code is enforced). The entries below
  // grandfather the pre-existing hits that triage found to be intentional, not bugs
  // — deriving-in-render / hoisting them would change verified runtime behaviour and
  // there is no component-level test coverage to catch a regression. Pay these down
  // incrementally; do NOT add new files here. (One genuine hit — inline component
  // definitions that remounted every render, in ActivityBar/BottomPanel — was fixed,
  // not suppressed.)
  {
    // `setState` inside an effect: syncing local state to an external/prop change —
    // an open-flag reset, a controlled-input default, SSR localStorage hydration, an
    // async-fetch reset, or a 1 Hz timer tick. All intentional.
    files: [
      "src/components/library/panels/TestbenchesView.tsx",
      "src/components/overlays/CommandPalette.tsx",
      "src/components/overlays/ProjectsOverlay.tsx",
      "src/components/pvt/ManualSimPanel.tsx",
      "src/components/schematic/DeviceInspector.tsx",
      "src/components/schematic/SchematicViewer.tsx",
      "src/components/shell/rails/RunsRail.tsx",
      "src/components/tabs/OptimizeTab.tsx",
      "src/components/tabs/SchematicTab.tsx",
      "src/components/tabs/ScoreShapingTab.tsx",
      "src/components/ui/panel.tsx",
      "src/components/ui/resizable.tsx",
      "src/components/wizard/WizardShell.tsx",
    ],
    rules: { "react-hooks/set-state-in-effect": "off" },
  },
  {
    // Manual useMemo/useCallback the compiler can't statically prove it preserves;
    // the deps are correct and the memo is intentional.
    files: [
      "src/components/library/rails/LibraryRightRail.tsx",
      "src/components/tabs/SchematicTab.tsx",
    ],
    rules: { "react-hooks/preserve-manual-memoization": "off" },
  },
  {
    // Synchronous ref read during render to place the device-inspector popover
    // inside the SVG viewport — intentional measurement, not reactive state.
    files: ["src/components/schematic/SchematicViewer.tsx"],
    rules: { "react-hooks/refs": "off" },
  },
];

export default eslintConfig;
