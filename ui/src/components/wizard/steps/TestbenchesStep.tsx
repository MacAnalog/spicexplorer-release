"use client";
import { useState } from "react";
import { Plus, Trash2, Upload } from "lucide-react";
import { useWizardStore } from "@/stores/wizardStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StepHeader, TextInput, Field } from "../wizard-controls";
import type { WizardTbParam, WizardTestbench } from "@/types/api";

function blankTb(): WizardTestbench {
  return { name: "", netlist: "", enable: true, description: "", params: [] };
}

function blankTbParam(name = ""): WizardTbParam {
  return { name, val: "", description: "", source: "manual" };
}

export function TestbenchesStep() {
  const { form, setTestbenches } = useWizardStore();
  const tbs = form.testbenches;
  const [parsingIdx, setParsingIdx] = useState<number | null>(null);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const dutParamNames = new Set(form.dut_params.map((p) => p.name));

  const updateTb = (i: number, patch: Partial<WizardTestbench>) =>
    setTestbenches(tbs.map((t, idx) => (idx === i ? { ...t, ...patch } : t)));
  const addTb = () => setTestbenches([...tbs, blankTb()]);
  const removeTb = (i: number) => setTestbenches(tbs.filter((_, idx) => idx !== i));

  const addParam = (i: number) => updateTb(i, { params: [...tbs[i].params, blankTbParam()] });
  const removeParam = (i: number, pi: number) =>
    updateTb(i, { params: tbs[i].params.filter((_, x) => x !== pi) });
  const updateParam = (i: number, pi: number, patch: Partial<WizardTbParam>) =>
    updateTb(i, { params: tbs[i].params.map((p, x) => (x === pi ? { ...p, ...patch } : p)) });

  const uploadTbNetlist = async (i: number, file: File) => {
    setParsingIdx(i);
    setErrMsg(null);
    try {
      const res = await api.parseNetlist(file);
      const existing = new Set(tbs[i].params.map((p) => p.name));
      // Exclude DUT-owned params — testbench cards only track tb-specific overrides (CL, V_CM, etc.)
      const newRows: WizardTbParam[] = res.params
        .filter((p) => !existing.has(p.name) && !dutParamNames.has(p.name))
        .map((p) => ({ name: p.name, val: p.default_val, description: "", source: "netlist" }));
      updateTb(i, { params: [...tbs[i].params, ...newRows] });
    } catch (e) {
      setErrMsg(e instanceof Error ? e.message : String(e));
    } finally {
      setParsingIdx(null);
    }
  };

  return (
    <div>
      <StepHeader
        title="Testbenches"
        description="One card per testbench netlist. Upload to auto-fill non-DUT `.param` overrides like CL or V_CM."
      />
      <div className="space-y-4 p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-600">Testbenches ({tbs.length})</span>
          <Button variant="secondary" onClick={addTb} className="h-7! px-2! text-xs!">
            <Plus className="h-3 w-3" /> Add testbench
          </Button>
        </div>

        {errMsg && <div className="rounded-md border border-red-200 bg-red-50 p-2 text-xs text-red-700">{errMsg}</div>}

        {tbs.length === 0 && (
          <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-center text-xs text-zinc-500">
            No testbenches yet — at least one is required.
          </div>
        )}

        {tbs.map((tb, i) => (
          <div key={i} className="rounded-lg border border-zinc-200 bg-white">
            <div className="flex items-center justify-between border-b border-zinc-100 px-3 py-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-zinc-800">
                Testbench #{i + 1}
                {tb.enable ? <Badge variant="pass">enabled</Badge> : <Badge variant="neutral">disabled</Badge>}
              </div>
              <button
                type="button"
                className="rounded-md border border-zinc-200 px-2 py-1 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                onClick={() => removeTb(i)}
                aria-label="Remove testbench"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3 p-3">
              <Field label="Name"><TextInput value={tb.name} onChange={(e) => updateTb(i, { name: e.target.value })} placeholder="tb_ac" /></Field>
              <Field label="Netlist path (relative to ws_root)"><TextInput value={tb.netlist} onChange={(e) => updateTb(i, { netlist: e.target.value })} placeholder="spice/tb_ac.spice" /></Field>
              <Field label="Description" className="col-span-2"><TextInput value={tb.description} onChange={(e) => updateTb(i, { description: e.target.value })} placeholder="AC analysis for UGF, Gain, PM" /></Field>
              <label className="flex items-center gap-2 text-xs text-zinc-700">
                <input type="checkbox" checked={tb.enable} onChange={(e) => updateTb(i, { enable: e.target.checked })} />
                enable
              </label>
            </div>

            <div className="border-t border-zinc-100 p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-medium text-zinc-600">Params ({tb.params.length})</span>
                <div className="flex gap-2">
                  <label className="cursor-pointer">
                    <input
                      type="file"
                      accept=".spice,.cir,.sp,.net"
                      className="hidden"
                      onChange={(e) => { const f = e.target.files?.[0]; if (f) uploadTbNetlist(i, f); e.target.value = ""; }}
                    />
                    <span className="inline-flex items-center gap-1 rounded-md border border-zinc-300 bg-white px-2 py-1 text-xs text-zinc-700 hover:bg-zinc-50">
                      <Upload className="h-3 w-3" /> {parsingIdx === i ? "Parsing…" : "Upload netlist"}
                    </span>
                  </label>
                  <Button variant="secondary" onClick={() => addParam(i)} className="h-7! px-2! text-xs!">
                    <Plus className="h-3 w-3" /> Add param
                  </Button>
                </div>
              </div>

              {tb.params.length === 0 ? (
                <div className="rounded-md border border-dashed border-zinc-200 bg-zinc-50 p-3 text-center text-xs text-zinc-500">
                  No params yet (e.g. CL, V_CM, F_AC_START).
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)_minmax(0,1.6fr)_auto] gap-2 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
                    <div>Name</div><div>Value</div><div>Description</div><div></div>
                  </div>
                  {tb.params.map((p, pi) => (
                    <div key={pi} className="grid grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)_minmax(0,1.6fr)_auto] items-center gap-2">
                      <div className="flex items-center gap-1">
                        <TextInput value={p.name} onChange={(e) => updateParam(i, pi, { name: e.target.value })} />
                        {p.source === "netlist" && <Badge variant="indigo">net</Badge>}
                      </div>
                      <TextInput value={p.val} onChange={(e) => updateParam(i, pi, { val: e.target.value })} placeholder="50f" />
                      <TextInput value={p.description ?? ""} onChange={(e) => updateParam(i, pi, { description: e.target.value })} placeholder="load capacitance" />
                      <button
                        type="button"
                        className="rounded-md border border-zinc-200 px-2 py-1 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                        onClick={() => removeParam(i, pi)}
                        aria-label="Remove param"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
