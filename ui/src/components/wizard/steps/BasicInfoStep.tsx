"use client";
import { useWizardStore } from "@/stores/wizardStore";
import { Field, TextInput, StepHeader } from "../wizard-controls";
import { selectCn } from "@/components/ui/select";

export function BasicInfoStep() {
  const { form, updateProject } = useWizardStore();
  const p = form.project;

  return (
    <div>
      <StepHeader title="Basic Info" description="Top-level project metadata that becomes the YAML's `project:` keys." />
      <div className="grid grid-cols-2 gap-3 p-4">
        <Field label="Project name" className="col-span-2">
          <TextInput value={p.name} onChange={(e) => updateProject({ name: e.target.value })} placeholder="my-ota-project" />
        </Field>
        <Field label="Description" className="col-span-2">
          <TextInput value={p.description} onChange={(e) => updateProject({ description: e.target.value })} placeholder="Cascode OTA sizing in ihp-sg13g2" />
        </Field>
        <Field label="Simulator">
          <select
            className={selectCn("sm") + " w-full"}
            value={p.simulator}
            onChange={(e) => updateProject({ simulator: e.target.value })}
          >
            <option value="ngspice">ngspice</option>
            <option value="spectre">spectre</option>
            <option value="hspice">hspice</option>
          </select>
        </Field>
        <Field label="Workspace root (absolute path)">
          <TextInput value={p.ws_root} onChange={(e) => updateProject({ ws_root: e.target.value })} placeholder="/path/to/project/root" />
        </Field>
        <Field label="DUT netlist (relative to ws_root)">
          <TextInput value={p.netlist} onChange={(e) => updateProject({ netlist: e.target.value })} placeholder="spice/dut.spice" />
        </Field>
        <Field label="Output directory (relative to ws_root)">
          <TextInput value={p.outdir} onChange={(e) => updateProject({ outdir: e.target.value })} placeholder="spice/temp_spice_out" />
        </Field>
        <label className="flex items-center gap-2 text-xs text-zinc-700">
          <input type="checkbox" checked={p.parallel_sim} onChange={(e) => updateProject({ parallel_sim: e.target.checked })} />
          parallel_sim
        </label>
        <label className="flex items-center gap-2 text-xs text-zinc-700">
          <input type="checkbox" checked={p.save_sim} onChange={(e) => updateProject({ save_sim: e.target.checked })} />
          save_sim
        </label>
      </div>
    </div>
  );
}
