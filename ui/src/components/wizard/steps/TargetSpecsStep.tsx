"use client";
import { useEffect, useState } from "react";
import { ChevronDown, ChevronRight, Plus, Trash2, Upload, BookOpen } from "lucide-react";
import { useWizardStore } from "@/stores/wizardStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StepHeader, TextInput, Field } from "../wizard-controls";
import { selectCn } from "@/components/ui/select";
import type { WizardTargetSpec, SpecLibraryEntry, MeasCandidate } from "@/types/api";

const SIM_TYPES: WizardTargetSpec["sim_type"][] = ["ac", "dc", "op", "tran", "noise", "noise_spectrum"];
const GOALS: WizardTargetSpec["goal"][] = ["exceed", "minimize", "exact"];
const ERROR_TYPES = ["relative-absolute", "absolute", "squared", "relative-squared", "relative-exponential", "relative-sigmoid"];
const REWARD_TYPES = ["none", "log", "relative-log", "relative-absolute", "absolute", "relative-sigmoid"];

function blankSpec(testbench = ""): WizardTargetSpec {
  return {
    name: "",
    testbench,
    sim_type: "ac",
    goal: "exceed",
    target: "",
    range: "",
    tolerance: "",
    weight: "1.0",
    log_scale: false,
    error_type: "relative-absolute",
    reward_type: "none",
    enable: true,
    description: "",
  };
}

export function TargetSpecsStep() {
  const { form, setTargetSpecs } = useWizardStore();
  const specs = form.target_specs;
  const tbNames = form.testbenches.map((t) => t.name).filter(Boolean);
  const [openIdx, setOpenIdx] = useState<number | null>(0);
  // §5e spec library (one-click adds) + §5c .meas auto-discovery.
  const [library, setLibrary] = useState<SpecLibraryEntry[]>([]);
  const [candidates, setCandidates] = useState<MeasCandidate[]>([]);
  const [picked, setPicked] = useState<Set<string>>(new Set());
  const [parsing, setParsing] = useState(false);
  const [discoverErr, setDiscoverErr] = useState<string | null>(null);

  useEffect(() => {
    api.specLibrary().then((r) => setLibrary(r.specs)).catch(() => setLibrary([]));
  }, []);

  const existingNames = new Set(specs.map((s) => s.name).filter(Boolean));

  const addFromLibrary = (name: string) => {
    const entry = library.find((e) => e.name === name);
    if (!entry) return;
    const next = [...specs, { ...blankSpec(tbNames[0] ?? ""), ...entry }];
    setTargetSpecs(next);
    setOpenIdx(next.length - 1);
  };

  const uploadForDiscovery = async (file: File) => {
    setParsing(true);
    setDiscoverErr(null);
    try {
      const res = await api.parseNetlist(file);
      const cands = (res.meas_candidates ?? []).filter((c) => !existingNames.has(c.name));
      setCandidates(cands);
      setPicked(new Set(cands.map((c) => c.name)));
    } catch (e) {
      setDiscoverErr(e instanceof Error ? e.message : String(e));
    } finally {
      setParsing(false);
    }
  };

  const SIM = ["ac", "dc", "op", "tran", "noise", "noise_spectrum"];
  const addPicked = () => {
    const toAdd = candidates.filter((c) => picked.has(c.name) && !existingNames.has(c.name));
    if (!toAdd.length) return;
    const newSpecs = toAdd.map((c) => ({
      ...blankSpec(tbNames[0] ?? ""),
      name: c.name,
      sim_type: (SIM.includes(c.sim_type) ? c.sim_type : "ac") as WizardTargetSpec["sim_type"],
    }));
    setTargetSpecs([...specs, ...newSpecs]);
    setCandidates([]);
    setPicked(new Set());
  };

  const add = () => {
    const next = [...specs, blankSpec(tbNames[0] ?? "")];
    setTargetSpecs(next);
    setOpenIdx(next.length - 1);
  };
  const remove = (i: number) => {
    setTargetSpecs(specs.filter((_, idx) => idx !== i));
    if (openIdx === i) setOpenIdx(null);
  };
  const update = (i: number, patch: Partial<WizardTargetSpec>) =>
    setTargetSpecs(specs.map((s, idx) => (idx === i ? { ...s, ...patch } : s)));

  return (
    <div>
      <StepHeader
        title="Target Specs"
        description="Each spec maps a measurement to a goal/target/tolerance — these drive the loss function."
      />
      <div className="space-y-3 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="text-xs font-medium text-zinc-600">Specs ({specs.length})</span>
          <div className="flex flex-wrap items-center gap-2">
            {library.length > 0 && (
              <select
                aria-label="Add a spec from the library"
                value=""
                onChange={(e) => { if (e.target.value) addFromLibrary(e.target.value); e.target.value = ""; }}
                className={selectCn("sm") + " w-[180px]"}
                title="Add a standard analog spec template"
              >
                <option value="">
                  + from library…
                </option>
                {library.map((e) => (
                  <option key={e.name} value={e.name}>
                    {e.name}{e.description ? ` — ${e.description}` : ""}
                  </option>
                ))}
              </select>
            )}
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".spice,.cir,.sp,.net"
                className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) uploadForDiscovery(f); e.target.value = ""; }}
              />
              <span className="inline-flex items-center gap-1 rounded-md border border-zinc-300 bg-white px-2 py-1 text-xs text-zinc-700 hover:bg-zinc-50">
                <Upload className="h-3 w-3" /> {parsing ? "Scanning…" : "Discover from netlist"}
              </span>
            </label>
            <Button variant="secondary" onClick={add} className="h-7! px-2! text-xs!">
              <Plus className="h-3 w-3" /> Add spec
            </Button>
          </div>
        </div>

        {discoverErr && (
          <div className="rounded-md border border-red-200 bg-red-50 p-2 text-xs text-red-700">{discoverErr}</div>
        )}

        {candidates.length > 0 && (
          <div className="rounded-md border border-indigo-200 bg-indigo-50/60 p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-xs font-medium text-indigo-700">
                <BookOpen className="h-3.5 w-3.5" /> {candidates.length} measurement(s) found — pick specs to add
              </span>
              <Button variant="primary" onClick={addPicked} className="h-7! px-2! text-xs!" disabled={picked.size === 0}>
                Add {picked.size} selected
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {candidates.map((c) => (
                <label key={c.name} className="flex items-center gap-1.5 rounded-sm border border-indigo-200 bg-white px-2 py-1 text-xs">
                  <input
                    type="checkbox"
                    checked={picked.has(c.name)}
                    onChange={(e) =>
                      setPicked((prev) => {
                        const next = new Set(prev);
                        if (e.target.checked) next.add(c.name); else next.delete(c.name);
                        return next;
                      })
                    }
                  />
                  <span className="font-mono">{c.name}</span>
                  <Badge variant="neutral">{c.sim_type}</Badge>
                </label>
              ))}
            </div>
          </div>
        )}

        {specs.length === 0 && (
          <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-center text-xs text-zinc-500">
            No specs yet — add at least one for the optimizer to chase.
          </div>
        )}

        {specs.map((s, i) => {
          const isOpen = openIdx === i;
          return (
            <div key={i} className="rounded-md border border-zinc-200 bg-white">
              <button
                type="button"
                className="flex w-full items-center justify-between px-3 py-2 text-left text-xs hover:bg-zinc-50"
                onClick={() => setOpenIdx(isOpen ? null : i)}
              >
                <span className="flex items-center gap-2">
                  {isOpen ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
                  <span className="font-mono font-medium text-zinc-800">{s.name || `spec-${i + 1}`}</span>
                  <Badge variant={s.goal === "exceed" ? "indigo" : s.goal === "minimize" ? "warning" : "neutral"}>
                    {s.goal}
                  </Badge>
                  <span className="text-zinc-500">target: {s.target || "—"}</span>
                  <span className="text-zinc-400">@ {s.testbench || "—"}</span>
                  {!s.enable && <Badge variant="neutral">disabled</Badge>}
                </span>
                <span
                  className="rounded-md border border-zinc-200 px-2 py-1 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                  role="button"
                  aria-label="Remove spec"
                  onClick={(e) => { e.stopPropagation(); remove(i); }}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </span>
              </button>

              {isOpen && (
                <div className="grid grid-cols-3 gap-3 border-t border-zinc-100 p-3">
                  <Field label="Name"><TextInput value={s.name} onChange={(e) => update(i, { name: e.target.value })} placeholder="ugf" /></Field>
                  <Field label="Testbench">
                    <select className={selectCn("sm") + " w-full"} value={s.testbench} onChange={(e) => update(i, { testbench: e.target.value })}>
                      <option value="">— select —</option>
                      {tbNames.map((n) => <option key={n} value={n}>{n}</option>)}
                    </select>
                  </Field>
                  <Field label="Sim type">
                    <select className={selectCn("sm") + " w-full"} value={s.sim_type} onChange={(e) => update(i, { sim_type: e.target.value as WizardTargetSpec["sim_type"] })}>
                      {SIM_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </Field>
                  <Field label="Goal">
                    <select className={selectCn("sm") + " w-full"} value={s.goal} onChange={(e) => update(i, { goal: e.target.value as WizardTargetSpec["goal"] })}>
                      {GOALS.map((g) => <option key={g} value={g}>{g}</option>)}
                    </select>
                  </Field>
                  <Field label="Target"><TextInput value={s.target} onChange={(e) => update(i, { target: e.target.value })} placeholder="200e6" /></Field>
                  <Field label="Range"><TextInput value={s.range} onChange={(e) => update(i, { range: e.target.value })} placeholder="100e6" /></Field>
                  <Field label="Tolerance"><TextInput value={s.tolerance} onChange={(e) => update(i, { tolerance: e.target.value })} placeholder="10e6" /></Field>
                  <Field label="Weight"><TextInput value={s.weight} onChange={(e) => update(i, { weight: e.target.value })} placeholder="1.0" /></Field>
                  <Field label="Error type">
                    <select className={selectCn("sm") + " w-full"} value={s.error_type} onChange={(e) => update(i, { error_type: e.target.value })}>
                      {ERROR_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </Field>
                  <Field label="Reward type">
                    <select className={selectCn("sm") + " w-full"} value={s.reward_type} onChange={(e) => update(i, { reward_type: e.target.value })}>
                      {REWARD_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </Field>
                  <Field label="Description" className="col-span-3">
                    <TextInput value={s.description} onChange={(e) => update(i, { description: e.target.value })} placeholder="Unity gain frequency" />
                  </Field>
                  <div className="col-span-3 flex items-center gap-4">
                    <label className="flex items-center gap-2 text-xs text-zinc-700">
                      <input type="checkbox" checked={s.log_scale} onChange={(e) => update(i, { log_scale: e.target.checked })} /> log_scale
                    </label>
                    <label className="flex items-center gap-2 text-xs text-zinc-700">
                      <input type="checkbox" checked={s.enable} onChange={(e) => update(i, { enable: e.target.checked })} /> enable
                    </label>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
