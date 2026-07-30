"use client";
import { useState } from "react";
import { Plus, Trash2, Upload } from "lucide-react";
import { useWizardStore } from "@/stores/wizardStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StepHeader, TextInput } from "../wizard-controls";
import type { WizardDutParam } from "@/types/api";

function blankRow(name = ""): WizardDutParam {
  return {
    name,
    min_val: "",
    max_val: "",
    is_integer: false,
    log_scale: false,
    freeze: false,
    source: "manual",
  };
}

export function DutParamsStep() {
  const { form, setDutParams } = useWizardStore();
  const rows = form.dut_params;
  const constraintKeys = form.tech.constraints.map((c) => c.key).filter(Boolean);
  const [parsing, setParsing] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);

  const update = (i: number, patch: Partial<WizardDutParam>) =>
    setDutParams(rows.map((r, idx) => (idx === i ? { ...r, ...patch } : r)));
  const remove = (i: number) => setDutParams(rows.filter((_, idx) => idx !== i));
  const add = () => setDutParams([...rows, blankRow()]);

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setParsing(true);
    setParseError(null);
    try {
      const res = await api.parseNetlist(file);
      const existing = new Set(rows.map((r) => r.name));
      const newRows: WizardDutParam[] = res.params
        .filter((p) => !existing.has(p.name))
        .map((p) => ({
          ...blankRow(p.name),
          default_val: p.default_val,
          init: p.default_val,
          source: "netlist",
        }));
      setDutParams([...rows, ...newRows]);
    } catch (err) {
      setParseError(err instanceof Error ? err.message : String(err));
    } finally {
      setParsing(false);
      e.target.value = "";
    }
  };

  return (
    <div>
      <StepHeader
        title="DUT Parameters"
        description="Sized variables. Upload the DUT netlist to auto-detect `.param` names, then set bounds (raw values or PDK constraint keys)."
      />
      <div className="space-y-3 p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-600">Parameters ({rows.length})</span>
          <div className="flex items-center gap-2">
            <label className="cursor-pointer">
              <input type="file" accept=".spice,.cir,.sp,.net" className="hidden" onChange={onUpload} />
              <span className="inline-flex items-center gap-1 rounded-md border border-zinc-300 bg-white px-2 py-1 text-xs text-zinc-700 hover:bg-zinc-50">
                <Upload className="h-3 w-3" /> {parsing ? "Parsing…" : "Upload netlist"}
              </span>
            </label>
            <Button variant="secondary" onClick={add} className="h-7! px-2! text-xs!">
              <Plus className="h-3 w-3" /> Add param
            </Button>
          </div>
        </div>

        {parseError && (
          <div className="rounded-md border border-red-200 bg-red-50 p-2 text-xs text-red-700">
            Netlist parse failed: {parseError}
          </div>
        )}

        {rows.length === 0 ? (
          <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-center text-xs text-zinc-500">
            No parameters yet — upload a netlist or add one manually.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <div className="grid min-w-[860px] grid-cols-[1.6fr_1.1fr_1.1fr_0.8fr_0.5fr_0.5fr_0.5fr_auto] gap-2 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
              <div>Name</div>
              <div>Min</div>
              <div>Max</div>
              <div>Init</div>
              <div title="Integer">int</div>
              <div title="Log scale">log</div>
              <div title="Freeze at init">frz</div>
              <div></div>
            </div>
            {rows.map((r, i) => (
              <div key={i} className="grid min-w-[860px] grid-cols-[1.6fr_1.1fr_1.1fr_0.8fr_0.5fr_0.5fr_0.5fr_auto] items-center gap-2 py-1">
                <div className="flex items-center gap-2">
                  <TextInput value={r.name} onChange={(e) => update(i, { name: e.target.value })} placeholder="X_DUT_..." />
                  {r.source === "netlist" && <Badge variant="indigo">netlist</Badge>}
                </div>
                <TextInput list={`pdk-keys-${i}`} value={r.min_val} onChange={(e) => update(i, { min_val: e.target.value })} placeholder="0.18u or key" />
                <TextInput list={`pdk-keys-${i}`} value={r.max_val} onChange={(e) => update(i, { max_val: e.target.value })} placeholder="200u or key" />
                <TextInput value={r.init ?? ""} onChange={(e) => update(i, { init: e.target.value })} placeholder={r.default_val ?? ""} />
                <input type="checkbox" checked={r.is_integer} onChange={(e) => update(i, { is_integer: e.target.checked })} />
                <input type="checkbox" checked={r.log_scale} onChange={(e) => update(i, { log_scale: e.target.checked })} />
                <input type="checkbox" checked={r.freeze} onChange={(e) => update(i, { freeze: e.target.checked })} />
                <button
                  type="button"
                  className="rounded-md border border-zinc-200 px-2 py-1 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                  onClick={() => remove(i)}
                  aria-label="Remove param"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
                {constraintKeys.length > 0 && (
                  <datalist id={`pdk-keys-${i}`}>
                    {constraintKeys.map((k) => <option key={k} value={k} />)}
                  </datalist>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
