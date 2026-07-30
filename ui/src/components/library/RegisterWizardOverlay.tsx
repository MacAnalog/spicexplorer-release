"use client";
import { useEffect, useRef } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ResizeHandle, useRailSize } from "@/components/ui/resizable";
import { useLibraryWizardStore } from "@/stores/libraryWizardStore";
import { classReg } from "@/lib/library/data";
import { buildWizard } from "@/lib/library/wizard";
import {
  TypeStep,
  CircuitIdentityStep,
  ProvenanceStep,
  TopologyStep,
  AnalysesStep,
  DatasheetStep,
  TbIdentityStep,
  TbParamsStep,
  TbProducesStep,
  TplIdentityStep,
  TplPortsStep,
  ReviewStep,
  EditorPane,
} from "./wizard/steps";

/**
 * Register wizard — full-surface overlay (handoff screen 6). A class-driven,
 * 3-flow form (circuit / template / testbench) with a step rail, the live YAML +
 * catalog-entry preview, and Back/Next/Register. Form state + mutations live in
 * `libraryWizardStore`; the pure flow/YAML logic in `lib/library/wizard`.
 * For the circuit kind, Register POSTs a draft to `/api/library/circuits` (see
 * `libraryWizardStore.register`); template/testbench kinds still just close.
 */
export function RegisterWizardOverlay() {
  const open = useLibraryWizardStore((s) => s.open);
  const form = useLibraryWizardStore((s) => s.form);
  const step = useLibraryWizardStore((s) => s.step);
  const close = useLibraryWizardStore((s) => s.close);
  const next = useLibraryWizardStore((s) => s.next);
  const back = useLibraryWizardStore((s) => s.back);
  const goStep = useLibraryWizardStore((s) => s.goStep);
  const register = useLibraryWizardStore((s) => s.register);
  const registering = useLibraryWizardStore((s) => s.registering);
  const registerError = useLibraryWizardStore((s) => s.registerError);
  const stepRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const [stepW, setStepW] = useRailSize("ui:rail:wizard-steps", 214, 160, 360);
  const [previewW, setPreviewW] = useRailSize("ui:rail:wizard-preview", 340, 240, 640);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && close();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close]);

  if (!open) return null;
  const d = buildWizard(form, step, classReg[form.klass].id);
  const { show } = d;

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-bg">
      {/* header */}
      <header className="flex h-12 shrink-0 items-center gap-3 border-b border-border bg-panel px-4">
        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-[14px] font-bold text-white">+</span>
        <div className="min-w-0">
          <div className="text-[13px] font-semibold capitalize leading-none tracking-[-0.01em]">Register {form.kind}</div>
          <div className="font-mono text-[10px] text-faint">analog-db ▸ register {form.kind}</div>
        </div>
        <div className="flex-1" />
        <span className="font-mono text-[10px] text-faint">{d.progress}</span>
        <button type="button" onClick={close} aria-label="Close" className="flex h-7 w-7 items-center justify-center rounded-md text-muted hover:bg-hairline">
          <X className="h-4 w-4" />
        </button>
      </header>

      {/* body */}
      <div className="flex min-h-0 flex-1">
        {/* step rail */}
        <div
          ref={stepRef}
          style={{ width: stepW }}
          className="relative flex shrink-0 flex-col border-r border-border bg-panel p-3"
        >
          <ResizeHandle
            edge="right"
            size={stepW}
            compute={(x) => x - (stepRef.current?.getBoundingClientRect().left ?? 0)}
            onSize={setStepW}
            resetTo={214}
            label="Resize the wizard steps panel"
          />
          {d.steps.map((s, i) => (
            <button
              key={s.label}
              type="button"
              onClick={() => goStep(i)}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-left transition",
                s.active ? "bg-primary-soft text-primary" : "hover:bg-hairline",
              )}
            >
              <span
                className={cn(
                  "flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold",
                  s.active ? "bg-primary text-white" : s.done ? "bg-ok-soft font-bold text-ok" : "border border-border text-faint",
                )}
              >
                {s.done ? "✓" : s.n}
              </span>
              <span className={cn("text-[11.5px]", s.active ? "font-semibold" : s.done ? "text-muted" : "text-faint")}>{s.label}</span>
            </button>
          ))}
          <div className="flex-1" />
          <div className="rounded-lg border border-hairline bg-bg p-2.5 text-[10px] leading-relaxed text-muted">
            Registered circuits join the catalog and can seed optimization projects — <span className="font-mono text-[9.5px] text-faint">datasheet ▸ Use as project</span>.
          </div>
        </div>

        {/* form */}
        <div className="min-h-0 flex-1 overflow-y-auto px-6 py-5">
          <div className="max-w-[600px]">
            <div className="text-[16px] font-semibold tracking-[-0.01em]">{d.title}</div>
            <div className="mb-5 mt-0.5 text-[11.5px] text-muted">{d.hint}</div>
            {show.type && <TypeStep />}
            {show.circIdentity && <CircuitIdentityStep />}
            {show.provenance && <ProvenanceStep />}
            {show.topology && <TopologyStep />}
            {show.analyses && <AnalysesStep />}
            {show.datasheet && <DatasheetStep />}
            {show.tbIdentity && <TbIdentityStep />}
            {show.tbParams && <TbParamsStep />}
            {show.tbProduces && <TbProducesStep />}
            {show.tplIdentity && <TplIdentityStep />}
            {show.tplPorts && <TplPortsStep />}
            {show.review && <ReviewStep d={d} />}
          </div>
        </div>

        {/* live preview — resizable; content scrolls in a wrapper so the handle stays pinned */}
        <div
          ref={previewRef}
          style={{ width: previewW }}
          className="relative flex shrink-0 flex-col border-l border-border bg-bg"
        >
          <ResizeHandle
            edge="left"
            size={previewW}
            compute={(x) => (previewRef.current?.getBoundingClientRect().right ?? 0) - x}
            onSize={setPreviewW}
            resetTo={340}
            label="Resize the wizard preview panel"
          />
          <div className="flex min-h-0 flex-1 flex-col gap-3.5 overflow-y-auto p-3.5">
            <EditorPane title={d.yamlTitle} lines={d.yamlLines} />
            <EditorPane title={d.catTitle} lines={d.catLines} maxH="max-h-[220px]" />
          </div>
        </div>
      </div>

      {/* footer */}
      <footer className="flex h-[54px] shrink-0 items-center gap-2.5 border-t border-border bg-panel px-4">
        <button type="button" onClick={close} className="text-[11.5px] text-muted hover:text-fg">Cancel</button>
        {registerError && <span className="max-w-[360px] truncate font-mono text-[10px] text-danger" title={registerError}>⚠ {registerError}</span>}
        <div className="flex-1" />
        {d.canBack && (
          <button type="button" onClick={back} className="inline-flex h-8 items-center rounded-lg border border-border px-4 text-[11.5px] font-semibold text-muted hover:bg-hairline">
            ‹ Back
          </button>
        )}
        {d.isLast ? (
          <button
            type="button"
            onClick={() => void register()}
            disabled={registering}
            className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-ok px-4 text-[11.5px] font-semibold text-white hover:bg-[#047857] disabled:opacity-60"
          >
            {registering ? "Registering…" : form.kind === "circuit" ? `✓ Register ${form.kind}` : `Done`}
          </button>
        ) : (
          <button type="button" onClick={next} className="inline-flex h-8 items-center rounded-lg bg-primary px-4 text-[11.5px] font-semibold text-white hover:bg-[#4338ca]">
            Next ›
          </button>
        )}
      </footer>
    </div>
  );
}
