"use client";
import { Plus, Trash2 } from "lucide-react";
import { useWizardStore } from "@/stores/wizardStore";
import { Field, TextInput, StepHeader } from "../wizard-controls";
import { selectCn } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import {
  NEVERGRAD_REGISTRY,
  NEVERGRAD_KWARG_PRESETS,
  AX_ALGORITHMS,
  AX_KWARG_PRESETS,
} from "../optimizer-registry";
import type { OptimizerKwargRow } from "@/types/api";

function flatNevergradNames(): string[] {
  return NEVERGRAD_REGISTRY.flatMap((g) => g.items);
}

export function OptimizerStep() {
  const { form, updateOptimizer } = useWizardStore();
  const o = form.optimizer;
  const kwargs: OptimizerKwargRow[] = o.optimizer_kwargs ?? [];

  const updateKwargs = (rows: OptimizerKwargRow[]) => updateOptimizer({ optimizer_kwargs: rows });
  const addKwarg = () => updateKwargs([...kwargs, { key: "", value: "" }]);
  const removeKwarg = (i: number) => updateKwargs(kwargs.filter((_, idx) => idx !== i));
  const updateKwarg = (i: number, patch: Partial<OptimizerKwargRow>) =>
    updateKwargs(kwargs.map((r, idx) => (idx === i ? { ...r, ...patch } : r)));

  const applyPreset = () => {
    const ngPreset = NEVERGRAD_KWARG_PRESETS[o.name];
    const presets =
      o.type === "bayesian_ax"
        ? AX_KWARG_PRESETS
        : ngPreset ?? [];
    if (presets.length === 0) return;
    const existing = new Set(kwargs.map((r) => r.key));
    const additions = presets
      .filter((p) => !existing.has(p.key))
      .map((p) => ({ key: p.key, value: p.value }));
    updateKwargs([...kwargs, ...additions]);
  };

  const handleTypeChange = (newType: string) => {
    // Snap algorithm name to a sensible default for the new family
    let nextName = o.name;
    if (newType === "nevergrad" && !flatNevergradNames().includes(o.name)) nextName = "LhsDE";
    if (newType === "bayesian_ax" && !AX_ALGORITHMS.includes(o.name)) nextName = AX_ALGORITHMS[0];
    if (newType === "reinforcement_learning") nextName = "ppo";
    updateOptimizer({ type: newType, name: nextName });
  };

  const presetHintForCurrentName: string | null = (() => {
    if (o.type === "bayesian_ax") return "Ax-platform supports per-trial settings (consumed when wiring lands).";
    const has = NEVERGRAD_KWARG_PRESETS[o.name];
    if (!has) return null;
    return `Configurable family — “Seed preset kwargs” fills the recommended ${o.name} options.`;
  })();

  return (
    <div>
      <StepHeader
        title="Optimizer"
        description="Family + algorithm + budget. `optimizer_kwargs` are passed through verbatim to the optimizer factory."
      />
      <div className="grid grid-cols-2 gap-3 p-4">
        <Field label="Optimizer type">
          <select
            className={selectCn("sm") + " w-full"}
            value={o.type}
            onChange={(e) => handleTypeChange(e.target.value)}
          >
            <option value="nevergrad">nevergrad</option>
            <option value="bayesian_ax">bayesian_ax (Ax platform)</option>
            <option value="reinforcement_learning">reinforcement_learning</option>
          </select>
        </Field>

        <Field label="Algorithm name">
          {o.type === "nevergrad" ? (
            <select
              className={selectCn("sm") + " w-full"}
              value={o.name}
              onChange={(e) => updateOptimizer({ name: e.target.value })}
            >
              {NEVERGRAD_REGISTRY.map((group) => (
                <optgroup key={group.label} label={group.label}>
                  {group.items.map((a) => <option key={a} value={a}>{a}</option>)}
                </optgroup>
              ))}
            </select>
          ) : o.type === "bayesian_ax" ? (
            <select
              className={selectCn("sm") + " w-full"}
              value={o.name}
              onChange={(e) => updateOptimizer({ name: e.target.value })}
            >
              {AX_ALGORITHMS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          ) : (
            <select
              className={selectCn("sm") + " w-full"}
              value={o.name}
              onChange={(e) => updateOptimizer({ name: e.target.value })}
            >
              {["ppo", "sac", "ddpg", "td3", "custom-ddpg", "custom-sac"].map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          )}
        </Field>

        <Field label="Budget (evaluations)">
          <TextInput type="number" min={1} value={String(o.budget)} onChange={(e) => updateOptimizer({ budget: e.target.value })} />
        </Field>
        <Field label="Random seed">
          <TextInput type="number" value={String(o.random_seed)} onChange={(e) => updateOptimizer({ random_seed: e.target.value })} />
        </Field>

        <div className="col-span-2 mt-2 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
          Linear variable bounds
        </div>
        <Field label="lin_min"><TextInput value={o.lin_min} onChange={(e) => updateOptimizer({ lin_min: e.target.value })} /></Field>
        <Field label="lin_max"><TextInput value={o.lin_max} onChange={(e) => updateOptimizer({ lin_max: e.target.value })} /></Field>

        <div className="col-span-2 mt-2 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
          Log variable bounds
        </div>
        <Field label="log_min"><TextInput value={o.log_min} onChange={(e) => updateOptimizer({ log_min: e.target.value })} /></Field>
        <Field label="log_max"><TextInput value={o.log_max} onChange={(e) => updateOptimizer({ log_max: e.target.value })} /></Field>

        {/* Optimizer kwargs editor */}
        <div className="col-span-2 mt-3 border-t border-zinc-100 pt-3">
          <div className="mb-2 flex items-center justify-between">
            <div>
              <div className="text-xs font-medium text-zinc-700">optimizer_kwargs</div>
              {presetHintForCurrentName && (
                <div className="text-[10px] text-zinc-500">{presetHintForCurrentName}</div>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                onClick={applyPreset}
                className="h-7! px-2! text-xs!"
                disabled={o.type === "nevergrad" && !NEVERGRAD_KWARG_PRESETS[o.name]}
              >
                Seed preset kwargs
              </Button>
              <Button variant="secondary" onClick={addKwarg} className="h-7! px-2! text-xs!">
                <Plus className="h-3 w-3" /> Add kwarg
              </Button>
            </div>
          </div>

          {kwargs.length === 0 ? (
            <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-3 text-center text-xs text-zinc-500">
              No optimizer_kwargs — most defaults work out of the box.
            </div>
          ) : (
            <div className="space-y-1">
              <div className="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1.6fr)_auto] gap-2 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
                <div>Key</div><div>Value (true / false / null / number / string)</div><div></div>
              </div>
              {kwargs.map((row, i) => (
                <div key={i} className="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1.6fr)_auto] items-center gap-2">
                  <TextInput value={row.key} onChange={(e) => updateKwarg(i, { key: e.target.value })} placeholder="initialization" />
                  <TextInput value={row.value} onChange={(e) => updateKwarg(i, { value: e.target.value })} placeholder="LHS" />
                  <button
                    type="button"
                    className="rounded-md border border-zinc-200 px-2 py-1 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                    onClick={() => removeKwarg(i)}
                    aria-label="Remove kwarg"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
