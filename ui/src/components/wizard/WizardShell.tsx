"use client";
import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { Panel, PanelHeader } from "@/components/ui/panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { STEP_LABELS, WIZARD_STEPS, useWizardStore } from "@/stores/wizardStore";
import { BasicInfoStep } from "./steps/BasicInfoStep";
import { PDKRulesStep } from "./steps/PDKRulesStep";
import { DutParamsStep } from "./steps/DutParamsStep";
import { PVTStep } from "./steps/PVTStep";
import { TestbenchesStep } from "./steps/TestbenchesStep";
import { TargetSpecsStep } from "./steps/TargetSpecsStep";
import { OptimizerStep } from "./steps/OptimizerStep";
import { TextInput } from "./wizard-controls";
import { cn } from "@/lib/utils";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

interface Props {
  onSaved?: (savedPath: string) => void;
  /** Absolute path to pre-fill the Save field (e.g. the loaded project's path). */
  defaultSavePath?: string;
}

export function WizardShell({ onSaved, defaultSavePath }: Props) {
  const { form, stepIdx, setStep, next, back, reset } = useWizardStore();
  const [yamlText, setYamlText] = useState("");
  const [yamlErrors, setYamlErrors] = useState<string[]>([]);
  const [savePath, setSavePath] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  useEffect(() => {
    if (savePath) return;
    // Prefer an explicit absolute default (the loaded project's path).
    if (defaultSavePath) {
      setSavePath(defaultSavePath);
      return;
    }
    // Otherwise only auto-fill from ws_root when it is ABSOLUTE. A relative root
    // (e.g. the examples' "..") would be written relative to the backend CWD —
    // /app in Docker → a non-writable "/project_setup.yaml" — so leave the field
    // empty and let the user enter an absolute path (the backend also rejects
    // relative save paths with a clear message).
    const root = form.project.ws_root?.replace(/\/$/, "");
    if (root && (root.startsWith("/") || root.startsWith("~"))) {
      setSavePath(`${root}/project_setup.yaml`);
    }
  }, [defaultSavePath, form.project.ws_root, savePath]);

  useEffect(() => {
    const t = setTimeout(async () => {
      try {
        const res = await api.generateProject(form);
        setYamlText(res.yaml);
        setYamlErrors(res.errors);
      } catch (e) {
        setYamlText("");
        setYamlErrors([e instanceof Error ? e.message : String(e)]);
      }
    }, 350);
    return () => clearTimeout(t);
  }, [form]);

  const StepBody = useMemo(() => {
    switch (WIZARD_STEPS[stepIdx]) {
      case "basic":
        return <BasicInfoStep />;
      case "pdk":
        return <PDKRulesStep />;
      case "dut":
        return <DutParamsStep />;
      case "pvt":
        return <PVTStep />;
      case "testbenches":
        return <TestbenchesStep />;
      case "specs":
        return <TargetSpecsStep />;
      case "optimizer":
        return <OptimizerStep />;
    }
  }, [stepIdx]);

  const handleSave = async () => {
    if (!savePath) {
      setSaveMsg("Specify a save path first.");
      return;
    }
    setSaving(true);
    setSaveMsg(null);
    try {
      const res = await api.generateProject(form, savePath);
      if (res.saved_path) {
        setSaveMsg(`Saved to ${res.saved_path}`);
        onSaved?.(res.saved_path);
      }
      setYamlErrors(res.errors);
    } catch (e) {
      setSaveMsg(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col gap-3">
      {/* Stepper bar — full width */}
      <div className="flex flex-wrap items-center gap-x-0.5 gap-y-1">
        {WIZARD_STEPS.map((id, i) => {
          const active = i === stepIdx;
          const done = i < stepIdx;
          return (
            <div key={id} className="flex items-center">
              <button
                type="button"
                onClick={() => setStep(i)}
                className={cn(
                  "flex items-center gap-1.5 rounded-sm px-2.5 py-1 text-xs transition",
                  active && "bg-primary-soft text-primary",
                  done && !active && "text-ok",
                  !active && !done && "text-muted hover:text-fg",
                )}
              >
                <span
                  className={cn(
                    "inline-flex h-4 w-4 items-center justify-center rounded-full font-mono text-[10px]",
                    active && "bg-primary text-white",
                    done && !active && "bg-ok text-white",
                    !active && !done && "bg-hairline",
                  )}
                >
                  {done ? "✓" : i + 1}
                </span>
                {STEP_LABELS[id]}
              </button>
              {i < WIZARD_STEPS.length - 1 && (
                <span className="px-0.5 text-faint">›</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Two-column body: form on the left, live YAML preview on the right */}
      <div className="grid min-h-0 flex-1 gap-3" style={{ gridTemplateColumns: "1fr 1fr" }}>
        {/* LEFT column: step form (scrolls internally) + pinned navigation */}
        <div className="flex min-h-0 min-w-0 flex-col gap-3">
          <Panel className="flex min-h-0 flex-1 flex-col">
            <div className="min-h-0 flex-1 overflow-y-auto">{StepBody}</div>
          </Panel>
          <div className="flex shrink-0 items-center justify-between">
            <Button variant="ghost" onClick={reset}>
              Reset wizard
            </Button>
            <div className="flex gap-1.5">
              <Button variant="default" onClick={back} disabled={stepIdx === 0}>
                ← Back
              </Button>
              <Button
                variant="primary"
                onClick={next}
                disabled={stepIdx === WIZARD_STEPS.length - 1}
              >
                Next →
              </Button>
            </div>
          </div>
        </div>

        {/* RIGHT column: live YAML preview + save controls */}
        <Panel className="flex min-h-0 min-w-0 flex-col">
          <PanelHeader
            title="live YAML preview"
            right={
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  disabled={!yamlText}
                  onClick={() => { if (yamlText) navigator.clipboard?.writeText(yamlText); }}
                  className="rounded-sm px-1.5 py-0.5 text-[10px] text-muted hover:bg-hairline hover:text-fg disabled:opacity-40"
                  title="Copy YAML to clipboard"
                >
                  Copy
                </button>
                <button
                  type="button"
                  disabled={!yamlText}
                  onClick={() => {
                    if (!yamlText) return;
                    const blob = new Blob([yamlText], { type: "text/yaml;charset=utf-8" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "project_setup.yaml";
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="rounded-sm px-1.5 py-0.5 text-[10px] text-muted hover:bg-hairline hover:text-fg disabled:opacity-40"
                  title="Download YAML"
                >
                  Download
                </button>
                {yamlErrors.length === 0 && yamlText ? (
                  <Badge variant="ok" dot>
                    valid
                  </Badge>
                ) : yamlErrors.length > 0 ? (
                  <Badge variant="fail" dot>
                    invalid
                  </Badge>
                ) : null}
              </div>
            }
          />
          <div className="min-h-0 flex-1">
            <MonacoEditor
              height="100%"
              language="yaml"
              value={yamlText}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 11.5,
                lineNumbers: "on",
                readOnly: true,
                scrollBeyondLastLine: false,
                wordWrap: "on",
                fontFamily: "IBM Plex Mono, ui-monospace, monospace",
                renderLineHighlight: "none",
              }}
              loading={
                <div className="flex h-40 items-center justify-center text-xs text-faint">
                  Rendering…
                </div>
              }
            />
          </div>
          {yamlErrors.length > 0 && (
            <div className="border-t border-border bg-danger-soft px-3 py-2 font-mono text-[11px] text-danger">
              {yamlErrors.map((e, i) => (
                <div key={i}>• {e}</div>
              ))}
            </div>
          )}
          <div className="border-t border-border px-3 py-2.5">
            <div className="flex items-end gap-2">
              <label className="flex flex-1 flex-col gap-1">
                <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                  Save path
                </span>
                <TextInput
                  value={savePath}
                  onChange={(e) => setSavePath(e.target.value)}
                  placeholder="/absolute/path/to/project_setup.yaml"
                />
              </label>
              <Button variant="primary" onClick={handleSave} disabled={saving || !yamlText}>
                {saving ? "Saving…" : "Save YAML"}
              </Button>
            </div>
            {saveMsg && <div className="mt-2 text-[11px] text-muted">{saveMsg}</div>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
