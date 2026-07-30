"use client";
import { Plus, Trash2 } from "lucide-react";
import { useWizardStore } from "@/stores/wizardStore";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TextInput, Field, StepHeader } from "../wizard-controls";
import type { WizardPVTCorner, WizardModelInclude } from "@/types/api";

const emptyCorner = (n: number): WizardPVTCorner => ({
  name: `corner_${n}`,
  temp: "27",
  supply_node: "VDD",
  supply_value: "1.8",
  enabled: true,
  includes: [],
});

/**
 * PVT corner editor (Phase 1). Each corner is process model-includes + environment
 * (temp, supply). `active_corner` picks the single corner the optimizer runs
 * against; corners are emitted with inline `model_includes` (the wizard skips the
 * `process_bundles` sugar). An empty list emits no `pvt:` block, leaving the
 * netlist's own hardcoded corner in effect (legacy behavior).
 */
export function PVTStep() {
  const { form, setPvtConfig } = useWizardStore();
  const pvt = form.pvt ?? { active_corner: "", corners: [], model_lib_root: "" };
  const corners = pvt.corners;

  const commit = (next: Partial<typeof pvt>) => setPvtConfig({ ...pvt, ...next });

  // Names that collide (case-sensitive, trimmed) — the backend rejects these on
  // generate/save (PVTConfig.__post_init__), so flag them inline as you type too.
  const dupNames = new Set<string>();
  {
    const seen = new Set<string>();
    for (const c of corners) {
      const n = c.name.trim();
      if (!n) continue;
      if (seen.has(n)) dupNames.add(n);
      seen.add(n);
    }
  }

  const addCorner = () => {
    // Pick the lowest unused corner_N (length+1 collides after a deletion).
    const taken = new Set(corners.map((c) => c.name));
    let n = corners.length + 1;
    while (taken.has(`corner_${n}`)) n += 1;
    const c = emptyCorner(n);
    const next = [...corners, c];
    commit({ corners: next, active_corner: pvt.active_corner || c.name });
  };

  const removeCorner = (i: number) => {
    const removed = corners[i];
    const next = corners.filter((_, idx) => idx !== i);
    commit({
      corners: next,
      active_corner:
        pvt.active_corner === removed.name ? (next[0]?.name ?? "") : pvt.active_corner,
    });
  };

  const updateCorner = (i: number, patch: Partial<WizardPVTCorner>) => {
    const prevName = corners[i].name;
    const next = corners.map((c, idx) => (idx === i ? { ...c, ...patch } : c));
    // Keep active_corner pointing at the (possibly renamed) corner.
    const active =
      patch.name && pvt.active_corner === prevName ? patch.name : pvt.active_corner;
    commit({ corners: next, active_corner: active });
  };

  const updateInclude = (ci: number, ii: number, patch: Partial<WizardModelInclude>) => {
    const includes = corners[ci].includes.map((inc, idx) => (idx === ii ? { ...inc, ...patch } : inc));
    updateCorner(ci, { includes });
  };
  const addInclude = (ci: number) =>
    updateCorner(ci, { includes: [...corners[ci].includes, { lib_file: "", section: "" }] });
  const removeInclude = (ci: number, ii: number) =>
    updateCorner(ci, { includes: corners[ci].includes.filter((_, idx) => idx !== ii) });

  return (
    <div>
      <StepHeader
        title="PVT Corners"
        description="Process / voltage / temperature corners that drive the simulation. The active corner is the one the optimizer runs against."
      />
      <div className="space-y-4 p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-600">Corners ({corners.length})</span>
          <Button variant="secondary" onClick={addCorner} className="h-7! px-2! text-xs!">
            <Plus className="h-3 w-3" /> Add corner
          </Button>
        </div>

        {corners.length > 0 && (
          <Field label="Active corner" hint="Which corner the optimizer runs against (Phase 1).">
            <select
              aria-label="Active PVT corner"
              value={pvt.active_corner}
              onChange={(e) => commit({ active_corner: e.target.value })}
              className="w-full min-w-0 rounded-md border border-zinc-300 bg-white px-2 py-1 text-sm focus:outline-hidden focus:ring-1 focus:ring-indigo-500"
            >
              {corners.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>
        )}

        {corners.length > 0 && (
          <Field
            label="Model lib root"
            hint="Optional dir prepended to each include's lib_file at sim time (blank → use the netlist's .lib search path / PDK env)."
          >
            <TextInput
              value={pvt.model_lib_root ?? ""}
              placeholder="${PDK_ROOT}/ihp-sg13g2/libs.tech/ngspice/models"
              onChange={(e) => commit({ model_lib_root: e.target.value })}
            />
          </Field>
        )}

        {corners.map((c, i) => (
          <div key={i} className="space-y-2 rounded-md border border-zinc-200 p-3">
            <div className="flex items-center gap-2">
              {pvt.active_corner === c.name && <Badge variant="pass">active</Badge>}
              {!c.enabled && <Badge variant="neutral">disabled</Badge>}
              <span className="ml-auto" />
              <button
                type="button"
                className="rounded-md border border-zinc-200 px-2 py-1 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                onClick={() => removeCorner(i)}
                aria-label="Remove corner"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(0,0.7fr)_minmax(0,0.8fr)_minmax(0,0.8fr)] gap-2">
              <Field label="Name">
                <TextInput value={c.name} placeholder="tt_27C_1V8" onChange={(e) => updateCorner(i, { name: e.target.value })} />
                {dupNames.has(c.name.trim()) && (
                  <span className="text-[10px] text-red-600">Duplicate name — must be unique.</span>
                )}
              </Field>
              <Field label="Temp (°C)">
                <TextInput type="number" value={c.temp} onChange={(e) => updateCorner(i, { temp: e.target.value })} />
              </Field>
              <Field label="Supply node">
                <TextInput value={c.supply_node} placeholder="VDD" onChange={(e) => updateCorner(i, { supply_node: e.target.value })} />
              </Field>
              <Field label="Supply (V)">
                <TextInput type="number" step="0.01" value={c.supply_value} onChange={(e) => updateCorner(i, { supply_value: e.target.value })} />
              </Field>
            </div>

            <label className="flex items-center gap-2 text-xs text-zinc-600">
              <input type="checkbox" checked={c.enabled} onChange={(e) => updateCorner(i, { enabled: e.target.checked })} />
              enabled (included in multi-corner sweeps — Phase 2)
            </label>

            {/* model includes — inline (file, section) directives */}
            <div className="space-y-1.5 rounded-sm border border-zinc-100 bg-zinc-50 p-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-medium uppercase tracking-wide text-zinc-500">
                  process model includes ({c.includes.length})
                </span>
                <button
                  type="button"
                  className="text-[11px] text-indigo-600 hover:underline"
                  onClick={() => addInclude(i)}
                >
                  + add include
                </button>
              </div>
              {c.includes.length === 0 && (
                <div className="text-[10px] text-zinc-400">
                  None — corner sets only temp/supply (the netlist&apos;s <code>.lib</code> corner is kept).
                </div>
              )}
              {c.includes.map((inc, ii) => (
                <div key={ii} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] gap-2">
                  <TextInput value={inc.lib_file} placeholder="cornerMOSlv.lib" onChange={(e) => updateInclude(i, ii, { lib_file: e.target.value })} />
                  <TextInput value={inc.section} placeholder="mos_tt" onChange={(e) => updateInclude(i, ii, { section: e.target.value })} />
                  <button
                    type="button"
                    className="rounded-md border border-zinc-200 px-2 text-zinc-400 hover:bg-red-50 hover:text-red-600"
                    onClick={() => removeInclude(i, ii)}
                    aria-label="Remove include"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}

        {corners.length === 0 && (
          <div className="rounded-md border border-dashed border-zinc-300 bg-zinc-50 p-4 text-center text-xs text-zinc-500">
            No PVT corners. The simulation uses whatever corner the netlist hardcodes.
            Add a corner to make process/temp/supply first-class.
          </div>
        )}
      </div>
    </div>
  );
}
