"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import type { OnMount } from "@monaco-editor/react";
import { Panel, PanelBody, PanelHeader } from "@/components/ui/panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Stat } from "@/components/ui/stat";
import { useProjectStore } from "@/stores/projectStore";
import { useWizardStore } from "@/stores/wizardStore";
import { api } from "@/lib/api";
import { formatEng, goalSymbol } from "@/lib/utils";
import { cornerSummary, cornerIncludes } from "@/lib/pvt";
import { EmptyState } from "@/components/ui/empty-state";
import { selectCn } from "@/components/ui/select";
import { Thead, Th, Tr, Td } from "@/components/ui/table";
import { SubTabStrip } from "@/components/shell/SubTabStrip";
import { Toolbar, ToolbarSpacer } from "@/components/shell/Toolbar";
import type { AppConfig } from "@/types/api";
import { WizardShell } from "@/components/wizard/WizardShell";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

interface Props {
  appConfig: AppConfig | null;
}

type SetupMode = "load" | "wizard";

export function SetupTab({ appConfig }: Props) {
  const {
    yaml,
    yamlPath,
    summary,
    validationErrors,
    isApplied,
    setYaml,
    setYamlPath,
    setValidationErrors,
    apply,
  } = useProjectStore();
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [mode, setMode] = useState<SetupMode>("load");
  const [hydrateError, setHydrateError] = useState<string | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  // The on-disk text last loaded — Apply sends the editor buffer (not a stale disk
  // re-read) whenever it differs from this, so unsaved Monaco edits aren't dropped.
  const [diskYaml, setDiskYaml] = useState<string>("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { setForm } = useWizardStore();
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const monacoRef = useRef<Parameters<OnMount>[1] | null>(null);
  const handleEditorMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
  };

  // Surface backend YAML validation errors as Monaco markers (red squiggles +
  // hover tooltips). The validator returns plain messages (no line/col), so we
  // anchor at the line named in the message when present, else line 1.
  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const model = editor?.getModel();
    if (!editor || !monaco || !model) return;
    const lineCount = model.getLineCount();
    const markers = validationErrors.map((msg) => {
      const m = /line\s+(\d+)/i.exec(msg);
      const line = Math.min(Math.max(1, m ? parseInt(m[1], 10) : 1), lineCount);
      return {
        severity: monaco.MarkerSeverity.Error,
        message: msg,
        startLineNumber: line,
        startColumn: 1,
        endLineNumber: line,
        endColumn: model.getLineMaxColumn(line),
      };
    });
    monaco.editor.setModelMarkers(model, "spx-yaml", markers);
  }, [validationErrors]);

  const loadDemoYaml = useCallback(
    async (path: string) => {
      setLoading(true);
      try {
        const result = await api.loadProject(path);
        if (result.ok) {
          apply(result.summary, path);
          const rawRes = await fetch(
            `/api/yaml-text?path=${encodeURIComponent(path)}`,
          );
          if (rawRes.ok) {
            const text = await rawRes.text();
            setYaml(text);
            setDiskYaml(text);
          }
        }
      } finally {
        setLoading(false);
      }
    },
    [apply, setYaml],
  );

  const handleEditorChange = useCallback(
    (value: string | undefined) => {
      const v = value ?? "";
      setYaml(v);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(async () => {
        if (!v.trim()) return;
        setValidating(true);
        try {
          const res = await api.validateYaml(v);
          setValidationErrors(res.errors);
        } finally {
          setValidating(false);
        }
      }, 600);
    },
    [setYaml, setValidationErrors],
  );

  const handleValidate = async () => {
    if (!yaml.trim()) return;
    setValidating(true);
    try {
      const res = await api.validateYaml(yaml);
      setValidationErrors(res.errors);
    } finally {
      setValidating(false);
    }
  };

  const handleApply = async () => {
    if (!yamlPath && !yaml.trim()) return;
    setLoading(true);
    try {
      // Apply the EDITOR buffer whenever it differs from what we loaded (so unsaved
      // Monaco edits aren't silently dropped). Pass yamlPath so the backend anchors
      // relative ws_root/netlist resolution to the original dir. Only when the buffer
      // is clean (or empty) do we re-read the on-disk path directly.
      const dirty = yaml.trim() !== "" && yaml !== diskYaml;
      const res = dirty
        ? await api.loadProjectContent(yaml, yamlPath || undefined)
        : yamlPath
          ? await api.loadProject(yamlPath)
          : await api.loadProjectContent(yaml);
      if (res.ok) {
        apply(res.summary, res.yaml_path);
        setDiskYaml(yaml); // applied buffer becomes the new clean baseline
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      // Uploaded content has no on-disk path; clear any stale path so Apply uses
      // the uploaded YAML (and the button enables on content alone).
      setYamlPath("");
      setYaml(text);
    };
    reader.readAsText(file);
  };

  const editInWizard = useCallback(async () => {
    setHydrateError(null);
    if (!yaml.trim() && !yamlPath) {
      setHydrateError("Load a YAML first.");
      return;
    }
    try {
      const res = yaml.trim()
        ? await api.parseProjectToForm({ yaml_content: yaml })
        : await api.parseProjectToForm({ yaml_path: yamlPath });
      setForm(res.form);
      setMode("wizard");
    } catch (e) {
      setHydrateError(e instanceof Error ? e.message : String(e));
    }
  }, [yaml, yamlPath, setForm]);

  const handleWizardSaved = useCallback(
    async (path: string) => {
      setMode("load");
      await loadDemoYaml(path);
    },
    [loadDemoYaml],
  );

  const lineCount = yaml.split("\n").length;
  const isValid = validationErrors.length === 0 && !!yaml.trim();

  return (
    <>
      <SubTabStrip<SetupMode>
        aria-label="Setup mode"
        value={mode}
        onChange={setMode}
        tabs={[
          { id: "load", label: "Load / Edit YAML" },
          { id: "wizard", label: "Create Wizard" },
        ]}
      />
      <Toolbar>
        {mode === "load" ? (
          <>
            {appConfig && (
              <select
                className={selectCn("sm")}
                value=""
                onChange={(e) => {
                  if (e.target.value) loadDemoYaml(e.target.value);
                }}
              >
                <option value="">Load example…</option>
                <option value={appConfig.default_yaml}>
                  OTA Cascode (default)
                </option>
              </select>
            )}
            <label className="cursor-pointer" aria-label="Upload YAML file">
              <input
                type="file"
                accept=".yaml,.yml"
                className="hidden"
                onChange={handleUpload}
              />
              <span className="inline-flex h-[26px] cursor-pointer items-center rounded-sm border border-border bg-panel px-2.5 text-[11px] font-medium hover:bg-hairline">
                Upload .yaml
              </span>
            </label>
            <Button variant="default" onClick={editInWizard} disabled={!yaml && !yamlPath}>
              Edit in wizard
            </Button>
          </>
        ) : null}
        <ToolbarSpacer />
        <Button
          variant={showSummary ? "primary" : "default"}
          onClick={() => setShowSummary((v) => !v)}
          disabled={!summary}
          title={
            summary
              ? showSummary
                ? "Hide project summary panels"
                : "Show project summary, target specs, and schematic"
              : "Apply a project first"
          }
        >
          {showSummary ? "Hide summary" : "Show summary"}
        </Button>
        {mode === "load" && (
          <>
            <Button
              variant="default"
              onClick={handleValidate}
              disabled={validating || !yaml}
            >
              {validating ? "Checking…" : "Validate"}
            </Button>
            <Button
              variant="primary"
              onClick={handleApply}
              disabled={loading || (!yamlPath && !yaml.trim())}
            >
              {loading ? "Loading…" : "Apply →"}
            </Button>
          </>
        )}
      </Toolbar>

      {summary && (
        <div className="grid shrink-0 grid-cols-4 gap-2.5 border-b border-border px-3 py-2.5">
          <Stat eyebrow="DUT params" value={String(summary.dut_params.length)} unit={`${summary.dut_params.filter((p) => !p.freeze).length} free`} />
          <Stat eyebrow="testbenches" value={String(summary.testbenches.length)} unit={`${summary.testbenches.filter((t) => t.enable).length} on`} />
          <Stat eyebrow="target specs" value={String(summary.target_specs.length)} unit={`${summary.target_specs.filter((s) => s.enable).length} on`} />
          <Stat eyebrow="PVT corners" value={String(summary.pvt?.corners.length ?? 0)} unit={summary.pvt ? summary.pvt.active_corner : undefined} />
        </div>
      )}

      <div
        className="grid min-h-0 flex-1 gap-3 overflow-auto p-3"
        style={{
          // Summary panels appear on the right only when the user toggles
          // them on (and a project is loaded).
          gridTemplateColumns: showSummary && summary ? "1fr 1fr" : "1fr",
        }}
      >
        {/* LEFT: Monaco editor or Wizard */}
        {mode === "load" ? (
          <Panel className="flex min-h-0 flex-col">
            <PanelHeader
              title="project_setup.yaml"
              mute={yamlPath ? `· ${yamlPath}` : ""}
              right={
                <>
                  <span className="font-mono text-[10px] text-muted">
                    UTF-8 · {lineCount} lines
                  </span>
                  {yaml.trim() && (
                    <Badge variant={isValid ? "ok" : "fail"} dot>
                      {isValid ? "valid" : "invalid"}
                    </Badge>
                  )}
                </>
              }
            />
            <div className="min-h-0 flex-1">
              <MonacoEditor
                height="100%"
                language="yaml"
                value={yaml}
                onChange={handleEditorChange}
                onMount={handleEditorMount}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 11.5,
                  lineNumbers: "on",
                  scrollBeyondLastLine: false,
                  wordWrap: "on",
                  fontFamily: "IBM Plex Mono, ui-monospace, monospace",
                  renderLineHighlight: "none",
                }}
                loading={
                  <div className="flex h-60 items-center justify-center text-xs text-faint">
                    Loading editor…
                  </div>
                }
              />
            </div>
            {(validationErrors.length > 0 || hydrateError) && (
              <div className="border-t border-border bg-danger-soft px-3 py-2">
                {validationErrors.map((e, i) => (
                  <div key={i} className="font-mono text-[11px] text-danger">
                    • {e}
                  </div>
                ))}
                {hydrateError && (
                  <div className="font-mono text-[11px] text-danger">
                    • {hydrateError}
                  </div>
                )}
              </div>
            )}
          </Panel>
        ) : (
          <div className="flex h-full min-h-0 min-w-0 flex-col">
            <WizardShell onSaved={handleWizardSaved} defaultSavePath={yamlPath} />
          </div>
        )}

        {/* RIGHT: stacked summary panels — toggled via the Show summary button */}
        {showSummary && summary && (
        <div className="flex min-w-0 flex-col gap-2.5">
          {!summary ? (
            <Panel>
              <PanelBody>
                <EmptyState minHeight="min-h-32">
                  Apply a project to see the parsed summary.
                </EmptyState>
              </PanelBody>
            </Panel>
          ) : (
            <>
              <Panel>
                <PanelHeader
                  title="project summary"
                  mute="· live preview"
                  right={
                    <span className="font-mono text-[10px] text-muted">
                      {summary.name}
                    </span>
                  }
                />
                <PanelBody>
                  <dl
                    className="grid gap-y-1 gap-x-3 text-xs"
                    style={{ gridTemplateColumns: "100px 1fr" }}
                  >
                    <dt className="text-muted">name</dt>
                    <dd className="m-0 font-mono text-[11px]">{summary.name}</dd>
                    <dt className="text-muted">simulator</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.simulator}
                    </dd>
                    <dt className="text-muted">technology</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.tech.name || "—"}
                    </dd>
                    <dt className="text-muted">workspace</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.ws_root || "—"}
                    </dd>
                    <dt className="text-muted">params</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.dut_params.length} ·{" "}
                      {summary.dut_params.filter((p) => p.log_scale).length} log ·{" "}
                      {summary.dut_params.filter((p) => p.is_integer).length} int ·{" "}
                      {summary.dut_params.filter((p) => p.freeze).length} frozen
                    </dd>
                    <dt className="text-muted">pvt corner</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.pvt
                        ? `${summary.pvt.active_corner} · ${summary.pvt.corners.length} defined`
                        : "none (netlist-hardcoded)"}
                    </dd>
                    <dt className="text-muted">testbenches</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.testbenches.length} ·{" "}
                      {summary.testbenches.filter((t) => t.enable).length} enabled
                    </dd>
                    <dt className="text-muted">specs</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.target_specs.length} · weight Σ ={" "}
                      {summary.target_specs
                        .reduce((a, s) => a + (s.weight ?? 0), 0)
                        .toFixed(1)}
                    </dd>
                    <dt className="text-muted">optimizer</dt>
                    <dd className="m-0 font-mono text-[11px]">
                      {summary.optimizer.name} · budget{" "}
                      {summary.optimizer.budget}
                    </dd>
                  </dl>
                  {isApplied && (
                    <div className="mt-2.5">
                      <Badge variant="ok" dot>
                        applied
                      </Badge>
                    </div>
                  )}
                </PanelBody>
              </Panel>

              <Panel>
                <PanelHeader
                  title="target specs"
                  mute={`· ${summary.target_specs.length}`}
                />
                <table className="w-full">
                  <Thead>
                    <Th>name</Th>
                    <Th>goal</Th>
                    <Th>target</Th>
                    <Th>tol</Th>
                    <Th>weight</Th>
                  </Thead>
                  <tbody>
                    {summary.target_specs.map((s) => (
                      <Tr key={s.name}>
                        <Td className="font-mono">{s.name}</Td>
                        <Td className="font-mono">{goalSymbol(s.goal)}</Td>
                        <Td className="font-mono">{formatEng(s.target)}</Td>
                        <Td className="font-mono">
                          {s.tolerance != null ? `±${formatEng(s.tolerance)}` : "—"}
                        </Td>
                        <Td className="font-mono">{(s.weight ?? 0).toFixed(1)}</Td>
                      </Tr>
                    ))}
                  </tbody>
                </table>
              </Panel>

              {summary.pvt && summary.pvt.corners.length > 0 && (
                <Panel>
                  <PanelHeader
                    title="pvt corners"
                    mute={`· ${summary.pvt.corners.length}`}
                    right={
                      <span className="font-mono text-[10px] text-secondary">
                        active: {summary.pvt.active_corner}
                      </span>
                    }
                  />
                  <table className="w-full">
                    <Thead>
                      <Th>corner</Th>
                      <Th>env</Th>
                      <Th>process</Th>
                      <Th>on</Th>
                    </Thead>
                    <tbody>
                      {summary.pvt.corners.map((c) => {
                        const isActive = c.name === summary.pvt!.active_corner;
                        return (
                          <Tr key={c.name} highlight={isActive}>
                            <Td className="font-mono">
                              {c.name}
                              {isActive && (
                                <span className="ml-1 text-[9px] uppercase tracking-wider text-secondary">
                                  active
                                </span>
                              )}
                            </Td>
                            <Td className="font-mono text-[10px] text-muted">
                              {cornerSummary(c)}
                            </Td>
                            <Td
                              className="max-w-[160px] truncate font-mono text-[10px] text-faint"
                              title={cornerIncludes(c)}
                            >
                              {cornerIncludes(c) || "—"}
                            </Td>
                            <Td>
                              <Badge variant={c.enabled ? "ok" : "neutral"}>
                                {c.enabled ? "yes" : "no"}
                              </Badge>
                            </Td>
                          </Tr>
                        );
                      })}
                    </tbody>
                  </table>
                </Panel>
              )}

              <Panel>
                <PanelHeader
                  title="device under test"
                  mute="· schematic"
                  right={
                    <span className="font-mono text-[10px] text-muted">
                      {summary.netlist || "—"}
                    </span>
                  }
                />
                <div className="bg-hairline/40 p-1.5">
                  <SchematicImg />
                </div>
              </Panel>
            </>
          )}
        </div>
        )}
      </div>
    </>
  );
}

function SchematicImg() {
  const [errored, setErrored] = useState(false);
  if (errored) {
    return (
      <div className="flex h-32 items-center justify-center text-[11px] text-faint">
        No schematic available.
      </div>
    );
  }
  return (
    <img
      src={api.schematicUrl()}
      alt="DUT schematic"
      className="max-h-[220px] w-full object-contain"
      onError={() => setErrored(true)}
    />
  );
}
