"use client";
import dynamic from "next/dynamic";
import type { BeforeMount } from "@monaco-editor/react";

// Monaco must stay SSR-disabled (uses window) — same pattern as SetupTab's YAML editor.
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

/**
 * Read-only SPICE netlist viewer — Monaco with a Monarch grammar for the deck
 * syntax the analog-db templates use: `*` and `$`/`;` comments, dot-commands,
 * `+` continuations, device cards (element letter at line head), engineering
 * numbers (`100n`, `2meg`), `{...}` brace expressions, and the templates'
 * `${...}` binding slots (highlighted loudest — they're the contract).
 */

const SPICE_LANG_ID = "spice";

const spiceMonarch = {
  ignoreCase: true,
  defaultToken: "",
  tokenizer: {
    root: [
      [/^\*.*/, "comment"],
      [/\$\{[^}]+\}/, "variable.name"], // template binding slot — before $-comment
      [/;.*$/, "comment"],
      [/\$(?!\{).*$/, "comment"], // ngspice end-of-line $ comment
      [
        /^\s*\.(subckt|ends|endc|end|param|params|ac|dc|tran|noise|pss|pnoise|op|four|meas|measure|lib|include|inc|model|options?|temp|ic|nodeset|save|print|plot|probe|control|global|csparam|func|if|else|endif|step|title|width)\b/,
      "keyword",
      ],
      [/^\s*\+/, "operator"], // card continuation
      [/^[a-z][\w.-]*/, "type.identifier"], // device/instance card head (R/C/M/X/V/…)
      [/'[^']*'/, "string"],
      [/"[^"]*"/, "string"],
      [/\{[^{}]*\}/, "attribute.value"], // brace expression
      [/\b\d+(\.\d+)?(e[+-]?\d+)?(meg|mil|[tgkmunpfa])?\w*/, "number"],
      [/[=(),]/, "delimiter"],
    ],
  },
};

const beforeMount: BeforeMount = (monaco) => {
  if (monaco.languages.getLanguages().some((l) => l.id === SPICE_LANG_ID)) return;
  monaco.languages.register({ id: SPICE_LANG_ID });
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- monarch grammar is untyped JSON
  monaco.languages.setMonarchTokensProvider(SPICE_LANG_ID, spiceMonarch as any);
  monaco.languages.setLanguageConfiguration(SPICE_LANG_ID, {
    comments: { lineComment: "*" },
    brackets: [["(", ")"], ["{", "}"]],
  });
  monaco.editor.defineTheme("spice-light", {
    base: "vs",
    inherit: true,
    rules: [
      { token: "variable.name", foreground: "ea580c", fontStyle: "bold" }, // ${SLOT}
      { token: "type.identifier", foreground: "4f46e5" }, // device cards
      { token: "attribute.value", foreground: "0891b2" }, // {expr}
      { token: "comment", foreground: "8a8a93", fontStyle: "italic" },
    ],
    colors: { "editor.background": "#ffffff" },
  });
};

export function SpiceEditor({
  value,
  height = "100%",
  language = SPICE_LANG_ID,
}: {
  value: string;
  height?: string | number;
  /** Monaco language id — "spice" (default) or any built-in (e.g. "yaml"). */
  language?: string;
}) {
  return (
    <MonacoEditor
      height={height}
      language={language}
      theme="spice-light"
      value={value}
      beforeMount={beforeMount}
      options={{
        readOnly: true,
        minimap: { enabled: false },
        fontSize: 11.5,
        fontFamily: "IBM Plex Mono, ui-monospace, monospace",
        lineNumbers: "on",
        scrollBeyondLastLine: false,
        renderLineHighlight: "none",
        automaticLayout: true, // rails/panes around it resize
        wordWrap: "off",
        domReadOnly: true,
        contextmenu: false,
      }}
    />
  );
}
