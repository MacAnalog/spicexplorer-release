"use client";
import { Plus, Trash2 } from "lucide-react";
import { useWizardStore } from "@/stores/wizardStore";
import { Button } from "@/components/ui/button";
import { Field, TextInput, StepHeader } from "../wizard-controls";

const DEFAULT_KEYS = [
  "min_nfet_w", "max_nfet_w", "min_nfet_l", "max_nfet_l",
  "min_pfet_w", "max_pfet_w", "min_pfet_l", "max_pfet_l",
];

export function PDKRulesStep() {
  const { form, setTechName, setConstraints } = useWizardStore();
  const rows = form.tech.constraints;

  const addRow = (key = "") => setConstraints([...rows, { key, value: "" }]);
  const removeRow = (i: number) => setConstraints(rows.filter((_, idx) => idx !== i));
  const updateRow = (i: number, patch: Partial<typeof rows[number]>) =>
    setConstraints(rows.map((r, idx) => (idx === i ? { ...r, ...patch } : r)));

  const seed = () => {
    const existing = new Set(rows.map((r) => r.key));
    const toAdd = DEFAULT_KEYS.filter((k) => !existing.has(k)).map((k) => ({ key: k, value: "" }));
    setConstraints([...rows, ...toAdd]);
  };

  return (
    <div>
      <StepHeader title="PDK Rules" description="Technology name + named constraints. DUT param bounds can reference these keys by name." />
      <div className="space-y-3 p-4">
        <Field label="Technology name">
          <TextInput value={form.tech.name} onChange={(e) => setTechName(e.target.value)} placeholder="ihp-sg13g2" />
        </Field>

        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-600">Constraints ({rows.length})</span>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={seed} className="h-7! px-2! text-xs!">Seed defaults</Button>
            <Button variant="secondary" onClick={() => addRow()} className="h-7! px-2! text-xs!">
              <Plus className="h-3 w-3" /> Add row
            </Button>
          </div>
        </div>

        {rows.length === 0 ? (
          <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-center text-xs text-zinc-500">
            No constraints yet. Add rows like <span className="font-mono">min_nfet_w = 0.18u</span>.
          </div>
        ) : (
          <div className="space-y-2">
            {rows.map((r, i) => (
              <div key={i} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] gap-2">
                <TextInput value={r.key} placeholder="key (e.g. min_nfet_w)" onChange={(e) => updateRow(i, { key: e.target.value })} />
                <TextInput value={r.value} placeholder="value (e.g. 0.18u)" onChange={(e) => updateRow(i, { value: e.target.value })} />
                <button
                  type="button"
                  className="rounded-md border border-zinc-200 px-2 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                  onClick={() => removeRow(i)}
                  aria-label="Remove constraint"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
