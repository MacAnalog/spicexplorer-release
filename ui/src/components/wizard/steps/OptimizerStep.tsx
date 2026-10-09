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
  OPTIMIZER_TYPES,
  isOfferedOptimizerType,
  nevergradNameNotice,
  optimizerTypeNotice,
  snapAlgorithmName,
} from "../optimizer-registry";
import type { OptimizerKwargRow } from "@/types/api";

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

  const handleTypeChange = (newType: string) =>
    updateOptimizer({ type: newType, name: snapAlgorithmName(newType, o.name) });

  // An old project YAML can carry an engine the wizard no longer offers
  // (reinforcement_learning). The step keeps it as a disabled entry with a warning:
  // deleting the option alone would make the <select> show "nevergrad" while the
  // form still holds the old value.
  const typeOffered = isOfferedOptimizerType(o.type);
  const typeNotice = optimizerTypeNotice(o.type);

  // The same holds for a nevergrad name the list does not have, such as one of the
  // 13 names removed because the platform cannot build them: the algorithm <select>
  // keeps the stored name as a disabled entry with a warning until the user picks another.
  const nameNotice = o.type === "nevergrad" ? nevergradNameNotice(o.name) : null;

  const presetHintForCurrentName: string | null = (() => {
    if (o.type === "bayesian_ax") {
      return "The Ax engine reads only batch_size from these rows. The preset keys (num_sobol_trials, acquisition_function, model_kwargs) are written to the YAML and do not change the run.";
    }
    const has = NEVERGRAD_KWARG_PRESETS[o.name];
    if (!has) return null;
    return `${o.name} takes settings. “Seed preset kwargs” adds the ${o.name} preset keys.`;
  })();

  return (
    <div>
      <StepHeader
        title="Optimizer"
        description="Engine, algorithm and evaluation budget. The optimizer_kwargs rows are settings for the algorithm. nevergrad never passes batch_size. It passes num_workers to a fixed algorithm such as NGOpt or TwoPointsDE, but not to one that takes settings, such as DifferentialEvolution or ParametrizedCMA. It passes every other row to an algorithm that takes settings, and a row that algorithm does not know stops the run. A fixed algorithm refuses the other rows and runs with its default settings. The Ax engine reads only batch_size."
      />
      <div className="grid grid-cols-2 gap-3 p-4">
        <Field label="Optimizer type">
          <select
            className={selectCn("sm") + " w-full"}
            value={o.type}
            onChange={(e) => handleTypeChange(e.target.value)}
          >
            {!typeOffered && (
              <option value={o.type} disabled>
                {o.type} (not available)
              </option>
            )}
            {OPTIMIZER_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          {typeNotice && (
            <span role="alert" className="text-[10px] text-danger">{typeNotice}</span>
          )}
        </Field>

        <Field label="Algorithm name">
          {o.type === "nevergrad" ? (
            <select
              className={selectCn("sm") + " w-full"}
              value={o.name}
              onChange={(e) => updateOptimizer({ name: e.target.value })}
            >
              {nameNotice && (
                <option value={o.name} disabled>
                  {o.name} (not available)
                </option>
              )}
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
            // engine not offered: show the stored name; choosing an engine replaces it
            <TextInput value={o.name} disabled readOnly />
          )}
          {nameNotice && (
            <span role="alert" className="text-[10px] text-danger">{nameNotice}</span>
          )}
        </Field>

        <Field label="Budget (evaluations)">
          <TextInput type="number" min={1} value={String(o.budget)} onChange={(e) => updateOptimizer({ budget: e.target.value })} />
        </Field>
        <Field label="Random seed">
          <TextInput type="number" value={String(o.random_seed)} onChange={(e) => updateOptimizer({ random_seed: e.target.value })} />
        </Field>

        <div className="col-span-2 mt-2 text-[10px] font-medium uppercase tracking-wide text-faint">
          Linear variable bounds
        </div>
        <Field label="lin_min"><TextInput value={o.lin_min} onChange={(e) => updateOptimizer({ lin_min: e.target.value })} /></Field>
        <Field label="lin_max"><TextInput value={o.lin_max} onChange={(e) => updateOptimizer({ lin_max: e.target.value })} /></Field>

        <div className="col-span-2 mt-2 text-[10px] font-medium uppercase tracking-wide text-faint">
          Log variable bounds
        </div>
        <Field label="log_min"><TextInput value={o.log_min} onChange={(e) => updateOptimizer({ log_min: e.target.value })} /></Field>
        <Field label="log_max"><TextInput value={o.log_max} onChange={(e) => updateOptimizer({ log_max: e.target.value })} /></Field>

        {/* Optimizer kwargs editor */}
        <div className="col-span-2 mt-3 border-t border-hairline pt-3">
          <div className="mb-2 flex items-center justify-between">
            <div>
              <div className="text-xs font-medium text-zinc-700">optimizer_kwargs</div>
              {presetHintForCurrentName && (
                <div className="text-[10px] text-muted">{presetHintForCurrentName}</div>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                onClick={applyPreset}
                className="h-7! px-2! text-xs!"
                disabled={!typeOffered || (o.type === "nevergrad" && !NEVERGRAD_KWARG_PRESETS[o.name])}
              >
                Seed preset kwargs
              </Button>
              <Button variant="secondary" onClick={addKwarg} className="h-7! px-2! text-xs!">
                <Plus className="h-3 w-3" /> Add kwarg
              </Button>
            </div>
          </div>

          {kwargs.length === 0 ? (
            <div className="rounded-md border border-dashed border-zinc-300 bg-bg p-3 text-center text-xs text-muted">
              No optimizer_kwargs rows: the algorithm runs with its default settings.
            </div>
          ) : (
            <div className="space-y-1">
              <div className="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1.6fr)_auto] gap-2 text-[10px] font-medium uppercase tracking-wide text-faint">
                <div>Key</div><div>Value (true / false / null / number / string)</div><div></div>
              </div>
              {kwargs.map((row, i) => (
                <div key={i} className="grid grid-cols-[minmax(0,1.2fr)_minmax(0,1.6fr)_auto] items-center gap-2">
                  <TextInput value={row.key} onChange={(e) => updateKwarg(i, { key: e.target.value })} placeholder="initialization" />
                  <TextInput value={row.value} onChange={(e) => updateKwarg(i, { value: e.target.value })} placeholder="LHS" />
                  <button
                    type="button"
                    className="rounded-md border border-border px-2 py-1 text-faint hover:bg-danger-soft hover:text-danger"
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
