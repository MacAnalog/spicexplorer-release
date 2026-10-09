import { fixupConfigRules } from "@eslint/compat";
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

// eslint-config-next 16 ships flat configs (arrays of config objects), so they are
// spread directly. The older FlatCompat.extends("next/…") call wraps a flat config
// a second time and throws a circular-schema error.
//
// fixupConfigRules (@eslint/compat) is needed for ESLint 10 (MacAnalog/spicexplorer-ui#58).
// eslint-config-next 16.3.x depends on eslint-plugin-react 7.37.5, whose rules call
// context.getFilename(); ESLint 10 removed that method, so without the wrapper
// `npm run lint` stops with "Error while loading rule 'react/display-name':
// contextOrFilename.getFilename is not a function". The wrapper gives every rule in
// these two configs a context object that again has the methods ESLint removed
// (getFilename, getPhysicalFilename, getCwd, getSourceCode, getScope and others).
// The enabled rules and their options are unchanged (85 rules, the same under ESLint
// 9.39.4 and 10.11.0). Remove the wrapper once eslint-config-next depends on an
// eslint-plugin-react release whose peer range includes ESLint 10:
//   npm view eslint-config-next@latest dependencies.eslint-plugin-react
//   npm view eslint-plugin-react@latest peerDependencies
const eslintConfig = [
  ...fixupConfigRules([...nextCoreWebVitals, ...nextTypescript]),
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts", "src/types/api.gen.ts"] },
  {
    rules: {
      "@next/next/no-img-element": "off",
    },
  },
  // eslint-config-next 16 turned on eslint-plugin-react-hooks v6/v7's React-Compiler
  // rules. They are enabled for every file. The entries below switch a rule off only
  // in the files that already broke it when the rules arrived, where a review found
  // the code intentional, not a bug: moving the logic into render or out of the
  // component would change runtime behaviour that works today, and no
  // component-level test would catch a regression. Remove files from these lists as
  // they are fixed; do not add new files. (One real defect, inline component
  // definitions that remounted on every render in ActivityBar/BottomPanel, was fixed,
  // not switched off.)
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
