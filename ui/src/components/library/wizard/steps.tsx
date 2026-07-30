"use client";
import { Search, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { Segmented } from "@/components/ui/segmented";
import { useLibraryWizardStore } from "@/stores/libraryWizardStore";
import { useLibraryStore } from "@/stores/libraryStore";
import { classReg, metricInfo } from "@/lib/library/data";
import { engineForPdk, engineUniverse, pdkChoices } from "@/lib/library/selectors";
import type { CircuitClass } from "@/lib/library/types";
import {
  KIND_CHOICES,
  SOURCE_CHOICES,
  LICENSE_CHOICES,
  ORIGIN_CHOICES,
  DETECT_FAMILIES,
  WIZ_BLOCKS,
  TPL_FAMILIES,
  TPL_POLARITIES,
  TB_SIM_TYPES,
  TB_FLAGS,
  OP_LABEL,
  type WizardDerived,
} from "@/lib/library/wizard";
import { FieldLabel, TextField, PillChoice, Toggle, CheckRow, EditorPane } from "./controls";

const CLASS_OPTIONS: { value: CircuitClass; label: string }[] = [
  { value: "amplifier", label: "amplifier" },
  { value: "ldo", label: "ldo" },
  { value: "pll", label: "pll" },
  { value: "adc", label: "adc" },
];

const PILL_ROW = "flex flex-wrap gap-1.5";

// ── Type ─────────────────────────────────────────────────────────────────────
export function TypeStep() {
  const kind = useLibraryWizardStore((s) => s.form.kind);
  const setKind = useLibraryWizardStore((s) => s.setKind);
  return (
    <div className="flex gap-3">
      {KIND_CHOICES.map((k) => {
        const active = kind === k.kind;
        return (
          <button
            key={k.kind}
            type="button"
            onClick={() => setKind(k.kind)}
            className={cn(
              "flex-1 rounded-[11px] border p-4 text-left transition",
              active ? "border-[1.5px] border-primary bg-[#fafaff]" : "border-border bg-panel hover:border-[#c7d2fe]",
            )}
          >
            <div className="flex items-center gap-2">
              <span className={cn("text-[18px]", active ? "text-primary" : "text-faint")}>{k.icon}</span>
              <span className="text-[13px] font-semibold">{k.label}</span>
              {active && <span className="ml-auto flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[9px] text-white">✓</span>}
            </div>
            <div className="mt-1.5 text-[11px] leading-snug text-muted">{k.desc}</div>
          </button>
        );
      })}
    </div>
  );
}

// ── Circuit identity ─────────────────────────────────────────────────────────
export function CircuitIdentityStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const setClass = useLibraryWizardStore((s) => s.setClass);
  const idFields = classReg[form.klass].id;
  return (
    <div className="flex flex-col gap-4">
      <TextField label="CIRCUIT ID" value={form.id} onChange={(v) => setStr("id", v)} caption={`→ circuits/${form.id}/  ·  catalog key`} />
      <TextField label="DISPLAY NAME" value={form.name} onChange={(v) => setStr("name", v)} mono={false} />
      <div>
        <FieldLabel>CLASS</FieldLabel>
        <Segmented value={form.klass} onChange={(v) => setClass(v)} options={CLASS_OPTIONS} />
        <div className="mt-1.5 text-[9.5px] text-faint">Class drives the identity fields, analyses and metrics below.</div>
      </div>
      <div className="flex gap-3">
        {idFields.map(([key, label, ph]) => (
          <div key={key} className="flex-1">
            <TextField label={label} value={form[key]} onChange={(v) => setStr(key, v)} placeholder={ph} />
          </div>
        ))}
      </div>
      <div>
        <FieldLabel hint="grouping">SOURCE CATEGORY</FieldLabel>
        <div className={cn(PILL_ROW, "mb-2")}>
          {SOURCE_CHOICES.map((s) => (
            <PillChoice key={s} mono active={form.source === s} onClick={() => setStr("source", s)}>
              {s}
            </PillChoice>
          ))}
        </div>
        <TextField value={form.source} onChange={(v) => setStr("source", v)} placeholder="…or type a new source name" />
      </div>
    </div>
  );
}

// ── Provenance ───────────────────────────────────────────────────────────────
export function ProvenanceStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const setBool = useLibraryWizardStore((s) => s.setBool);
  const pickLicense = useLibraryWizardStore((s) => s.pickLicense);
  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-3">
        <div className="flex-1">
          <TextField label="DESIGNER" value={form.designer} onChange={(v) => setStr("designer", v)} placeholder="optional" mono={false} />
        </div>
        <div className="w-[200px]">
          <FieldLabel>LICENSE</FieldLabel>
          <div className="relative">
            <button
              type="button"
              onClick={() => setBool("licenseOpen", !form.licenseOpen)}
              className="flex h-[30px] w-full items-center rounded-md border border-border bg-panel px-2.5 font-mono text-[11.5px]"
            >
              <span className="flex-1 text-left">{form.license}</span>
              <span className="text-faint">▾</span>
            </button>
            {form.licenseOpen && (
              <div className="absolute left-0 right-0 top-[34px] z-10 overflow-hidden rounded-lg border border-border bg-panel shadow-[0_8px_24px_-8px_rgba(0,0,0,0.2)]">
                {LICENSE_CHOICES.map((l) => (
                  <button
                    key={l}
                    type="button"
                    onClick={() => pickLicense(l)}
                    className={cn(
                      "block w-full px-2.5 py-1.5 text-left font-mono text-[11px]",
                      l === form.license ? "bg-primary-soft text-primary" : "text-muted hover:bg-hairline",
                    )}
                  >
                    {l}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <TextField label="PAPER / CITATION" value={form.paper} onChange={(v) => setStr("paper", v)} placeholder="Author, Journal vol(no):pp, year" mono={false} />
      <TextField label="ALIASES" value={form.aliases} onChange={(v) => setStr("aliases", v)} placeholder="comma-separated upstream names" />
      <Note>Provenance travels with the circuit. The <b>source category</b> is set on the Identity step.</Note>
    </div>
  );
}

// ── Topology ─────────────────────────────────────────────────────────────────
export function TopologyStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const setBool = useLibraryWizardStore((s) => s.setBool);
  const toggleArr = useLibraryWizardStore((s) => s.toggleArr);
  const data = useLibraryStore((s) => s.data);
  // PDK + simulator choices come from the DB registry (never a hardcoded list);
  // picking a PDK pre-selects the engine its committed sim_engine marker routes to.
  const pdkOpts = pdkChoices(data);
  const simOpts = engineUniverse(data);
  const pdk = form.netOrigin === "pdk";
  return (
    <div className="flex flex-col gap-4">
      <div>
        <FieldLabel>NETLIST ORIGIN</FieldLabel>
        <div className="mb-3 flex gap-2">
          {ORIGIN_CHOICES.map((o) => (
            <button
              key={o.value}
              type="button"
              onClick={() => setStr("netOrigin", o.value)}
              className={cn(
                "inline-flex h-[30px] items-center rounded-lg px-3.5 text-[11px] transition",
                form.netOrigin === o.value ? "border border-[#c7d2fe] bg-primary-soft font-semibold text-primary" : "border border-border text-muted hover:border-[#c7d2fe]",
              )}
            >
              {o.label}
            </button>
          ))}
        </div>
        <DropZone>
          {pdk ? (
            <span>Drop a PDK-specific deck <span className="font-mono text-[10.5px]">.spice / .scs</span></span>
          ) : (
            <span>Drop <span className="font-mono text-[10.5px]">abstract/netlist.spice</span> — PDK-neutral topology</span>
          )}
        </DropZone>
        {pdk && (
          <div className="mt-3 flex gap-3">
            <div className="flex-1">
              <div className="mb-1.5 text-[9px] text-faint">PDK</div>
              <div className={PILL_ROW}>
                {pdkOpts.map((p) => (
                  <PillChoice
                    key={p}
                    mono
                    active={form.netPdk === p}
                    onClick={() => {
                      setStr("netPdk", p);
                      const eng = engineForPdk(data, p);
                      if (eng) setStr("netSim", eng);
                    }}
                  >
                    {p}
                  </PillChoice>
                ))}
              </div>
            </div>
            <div className="flex-1">
              <div className="mb-1.5 text-[9px] text-faint">SIMULATOR</div>
              <div className={PILL_ROW}>
                {simOpts.map((sm) => (
                  <PillChoice key={sm} mono active={form.netSim === sm} onClick={() => setStr("netSim", sm)}>{sm}</PillChoice>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <div>
        <FieldLabel hint="optional">SCHEMATIC</FieldLabel>
        <DropZone small>
          Drop xschem <span className="font-mono text-[10px]">.sch</span> or an image <span className="font-mono text-[10px]">.png / .svg / .jpg</span>
        </DropZone>
        <div className="mt-2">
          <div className="mb-1 text-[9px] text-faint">FILE NAME · rename</div>
          <TextField value={form.schematicFile} onChange={(v) => setStr("schematicFile", v)} />
        </div>
      </div>

      <div className="flex items-center gap-2.5 rounded-lg border border-border p-3">
        <div className="flex-1">
          <div className="text-[11.5px] font-semibold">Run block detection</div>
          <div className="text-[10px] text-muted">Optional — circuitgraph subgraph matching over chosen template families</div>
        </div>
        <Toggle on={form.detect} onClick={() => setBool("detect", !form.detect)} label="Run block detection" />
      </div>

      {form.detect ? (
        <>
          <div>
            <FieldLabel>TEMPLATE FAMILIES TO MATCH</FieldLabel>
            <div className="flex flex-col gap-1">
              {DETECT_FAMILIES.map(([key, label, note]) => (
                <CheckRow key={key} on={form.detectTemplates.includes(key)} onClick={() => toggleArr("detectTemplates", key)} right={<span className="font-mono text-[9.5px] text-faint">{note}</span>}>
                  <span className="text-[11.5px]">{label}</span>
                </CheckRow>
              ))}
            </div>
          </div>
          <div className="overflow-hidden rounded-lg border border-border">
            <div className="flex items-center gap-2 border-b border-hairline bg-bg px-3 py-2">
              <span className="h-[7px] w-[7px] rounded-full bg-ok" />
              <span className="font-mono text-[10.5px]">netlist.spice</span>
              <div className="flex-1" />
              <span className="font-mono text-[10px] text-muted">{form.deviceCount} devices · 3 blocks</span>
            </div>
            <div className="flex flex-col gap-1.5 px-3 py-2.5">
              {WIZ_BLOCKS.map((b) => (
                <div key={b.tid} className="flex items-center gap-2 text-[10.5px]">
                  <span className="h-[7px] w-[7px] rounded-[2px] bg-primary" />
                  <span className="flex-1 text-muted">{b.fam}</span>
                  <span className="font-mono text-[9.5px] text-faint">{b.tid} · {b.dev}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <Note>Block detection skipped — the topology is registered without annotated functional blocks. You can run it later from Detect ▸ Blocks.</Note>
      )}
    </div>
  );
}

// ── Analyses ─────────────────────────────────────────────────────────────────
export function AnalysesStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const toggleArr = useLibraryWizardStore((s) => s.toggleArr);
  const addTb = useLibraryWizardStore((s) => s.addTb);
  const removeTb = useLibraryWizardStore((s) => s.removeTb);
  return (
    <div className="flex flex-col gap-1">
      {classReg[form.klass].an.map((a) => (
        <CheckRow key={a} on={form.analyses.includes(a)} onClick={() => toggleArr("analyses", a)}>
          <span className="font-mono text-[11px]">{a}</span>
        </CheckRow>
      ))}
      {form.customAnalyses.map((a) => (
        <div key={a} className="flex items-center gap-2.5 rounded-md border border-[#c7d2fe] bg-[#fafaff] px-2.5 py-2">
          <span className="flex h-[15px] w-[15px] items-center justify-center rounded-[4px] bg-primary text-[10px] text-white">✓</span>
          <span className="flex-1 font-mono text-[11px]">{a}</span>
          <span className="text-[9px] text-primary">custom</span>
          <button type="button" onClick={() => removeTb(a)} className="text-faint hover:text-fg" aria-label={`Remove ${a}`}>✕</button>
        </div>
      ))}
      <div className="mt-2 flex gap-1.5">
        <input
          value={form.newTb}
          onChange={(e) => setStr("newTb", e.target.value)}
          placeholder="register a new testbench id — e.g. psrr_vss"
          className="h-[30px] flex-1 rounded-md border border-border bg-panel px-2.5 font-mono text-[11px] outline-hidden focus:border-[#c7d2fe]"
        />
        <button type="button" onClick={addTb} className="inline-flex h-[30px] items-center rounded-md border border-primary px-3.5 text-[11px] font-semibold text-primary hover:bg-primary-soft">
          + Register
        </button>
      </div>
    </div>
  );
}

// ── Datasheet ────────────────────────────────────────────────────────────────
const COND_FIELDS: { key: "supply" | "temp" | "cload" | "vcm" | "ibias"; label: string }[] = [
  { key: "supply", label: "supply (V)" },
  { key: "temp", label: "temp (°C)" },
  { key: "cload", label: "C_load" },
  { key: "vcm", label: "V_cm" },
  { key: "ibias", label: "I_bias" },
];
const METRIC_ROW = { gridTemplateColumns: "92px 1fr 58px 78px 68px 20px" } as const;

export function DatasheetStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const cycleMetricOp = useLibraryWizardStore((s) => s.cycleMetricOp);
  const setMetricVal = useLibraryWizardStore((s) => s.setMetricVal);
  const removeMetric = useLibraryWizardStore((s) => s.removeMetric);
  const addMetric = useLibraryWizardStore((s) => s.addMetric);
  const avail = classReg[form.klass].metrics.filter((k) => !form.metricRows.some((r) => r.key === k));
  return (
    <div className="flex flex-col gap-[18px]">
      <div>
        <FieldLabel>DEFAULT CONDITIONS</FieldLabel>
        <div className="grid grid-cols-5 gap-2">
          {COND_FIELDS.map((f) => (
            <div key={f.key}>
              <div className="mb-1 text-[9px] text-faint">{f.label}</div>
              <input aria-label={f.label} value={form[f.key]} onChange={(e) => setStr(f.key, e.target.value)} className="h-7 w-full rounded-md border border-border bg-panel px-2 font-mono text-[11px] outline-hidden focus:border-[#c7d2fe]" />
            </div>
          ))}
        </div>
      </div>
      <div>
        <FieldLabel>METRICS &amp; TARGET SPECS</FieldLabel>
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="grid items-center gap-1.5 border-b border-border bg-panel px-3 py-1.5" style={METRIC_ROW}>
            {["METRIC", "DESCRIPTION", "ANALYSIS", "TYPE", "VALUE"].map((h) => (
              <span key={h} className="text-[9px] font-bold uppercase tracking-wider text-faint">{h}</span>
            ))}
            <span />
          </div>
          {form.metricRows.map((m) => {
            const info = metricInfo[m.key];
            return (
              <div key={m.key} className="grid items-center gap-1.5 border-b border-hairline px-3 py-1.5 last:border-0" style={METRIC_ROW}>
                <span className="font-mono text-[10px]">{m.key}</span>
                <span className="truncate text-[10.5px] text-muted">{info?.d ?? m.key}</span>
                <span className="font-mono text-[9px] text-faint">{info?.a ?? "—"}</span>
                <button type="button" onClick={() => cycleMetricOp(m.key)} title="click to change" className="flex h-[26px] items-center justify-center rounded-md border border-border bg-panel font-mono text-[9.5px] hover:border-[#c7d2fe] hover:bg-[#fafaff]">
                  {OP_LABEL[m.op] ?? m.op}
                </button>
                <input aria-label={`${m.key} target value`} value={m.val} onChange={(e) => setMetricVal(m.key, e.target.value)} className="h-[26px] w-full rounded-md border border-border bg-panel px-2 font-mono text-[10px] outline-hidden focus:border-[#c7d2fe]" />
                <button type="button" onClick={() => removeMetric(m.key)} className="text-center text-faint hover:text-fg" aria-label={`Remove ${m.key}`}>✕</button>
              </div>
            );
          })}
        </div>
      </div>
      <div>
        <FieldLabel>ADD FROM METRICS REGISTRY</FieldLabel>
        <div className={PILL_ROW}>
          {avail.map((k) => (
            <button key={k} type="button" onClick={() => addMetric(k)} className="inline-flex h-6 items-center rounded-md border border-dashed border-[#c7d2fe] px-2.5 font-mono text-[10px] text-primary hover:bg-primary-soft">
              + {k}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Testbench identity ───────────────────────────────────────────────────────
export function TbIdentityStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const setTbSimType = useLibraryWizardStore((s) => s.setTbSimType);
  return (
    <div className="flex flex-col gap-4">
      <TextField label="ANALYSIS ID" value={form.tbId} onChange={(v) => setStr("tbId", v)} caption={`→ circuits/<id>/analyses/${form.tbId}.yaml`} />
      <TextField label="TEMPLATE" value={form.tbTemplate} onChange={(v) => setStr("tbTemplate", v)} />
      <div>
        <FieldLabel>SIM TYPE</FieldLabel>
        <div className={PILL_ROW}>
          {TB_SIM_TYPES.map((t) => (
            <PillChoice key={t} mono active={form.tbSimType === t} onClick={() => setTbSimType(t)}>{t}</PillChoice>
          ))}
        </div>
      </div>
      <TextField label="DESCRIPTION" value={form.tbDesc} onChange={(v) => setStr("tbDesc", v)} mono={false} />
      <div>
        <FieldLabel>REGISTERED WITH CLASS</FieldLabel>
        <div className={PILL_ROW}>
          {CLASS_OPTIONS.map((c) => (
            <PillChoice key={c.value} active={form.tbClass === c.value} onClick={() => setStr("tbClass", c.value)}>{c.label}</PillChoice>
          ))}
        </div>
        <div className="mt-1.5 text-[9.5px] text-faint">Reused by every circuit of this class — the same params drive each binding.</div>
      </div>
    </div>
  );
}

// ── Testbench parameters ─────────────────────────────────────────────────────
const PARAM_ROW = { gridTemplateColumns: "1fr 1fr 24px" } as const;
export function TbParamsStep() {
  const rows = useLibraryWizardStore((s) => s.form.tbParamRows);
  const setTbParam = useLibraryWizardStore((s) => s.setTbParam);
  const addTbParam = useLibraryWizardStore((s) => s.addTbParam);
  const removeTbParam = useLibraryWizardStore((s) => s.removeTbParam);
  return (
    <div className="flex flex-col gap-3.5">
      <div className="overflow-hidden rounded-lg border border-border">
        <div className="grid gap-2 border-b border-border bg-panel px-3 py-1.5" style={PARAM_ROW}>
          <span className="text-[9px] font-bold uppercase tracking-wider text-faint">PARAM</span>
          <span className="text-[9px] font-bold uppercase tracking-wider text-faint">VALUE</span>
          <span />
        </div>
        {rows.map((p, i) => (
          <div key={i} className="grid items-center gap-2 border-b border-hairline px-2.5 py-1.5" style={PARAM_ROW}>
            <input aria-label={`parameter ${i + 1} name`} value={p[0]} onChange={(e) => setTbParam(i, 0, e.target.value)} className="h-7 w-full rounded-md border border-border bg-panel px-2 font-mono text-[10.5px] outline-hidden focus:border-[#c7d2fe]" />
            <input aria-label={`parameter ${i + 1} value`} value={p[1]} onChange={(e) => setTbParam(i, 1, e.target.value)} className="h-7 w-full rounded-md border border-border bg-panel px-2 font-mono text-[10.5px] outline-hidden focus:border-[#c7d2fe]" />
            <button type="button" onClick={() => removeTbParam(i)} className="text-center text-faint hover:text-fg" aria-label="Remove parameter">✕</button>
          </div>
        ))}
        <button type="button" onClick={addTbParam} className="w-full px-3 py-1.5 text-left text-[10.5px] text-primary hover:bg-[#fafaff]">+ Add parameter</button>
      </div>
      <Note>Common: <span className="font-mono text-[10px]">VDD · VCM · IBIAS · CL</span>. AC adds <span className="font-mono text-[10px]">FSTART/FSTOP/PPD</span>; tran adds <span className="font-mono text-[10px]">VSTEP/VTOL/TSTART/TSTEP/TSTOP</span>. Engineering suffixes ok (f, p, u, MEG).</Note>
    </div>
  );
}

// ── Testbench produces & flags ───────────────────────────────────────────────
export function TbProducesStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const toggleArr = useLibraryWizardStore((s) => s.toggleArr);
  const all = classReg[form.tbClass].metrics;
  const q = form.tbProduceSearch.trim().toLowerCase();
  const avail = all.filter((k) => !form.tbProduces.includes(k) && (!q || k.toLowerCase().includes(q) || (metricInfo[k]?.d ?? "").toLowerCase().includes(q)));
  return (
    <div className="flex flex-col gap-[18px]">
      <div>
        <FieldLabel hint="datasheet metrics this analysis extracts">PRODUCES</FieldLabel>
        <div className="mb-2 flex flex-wrap gap-1.5">
          {form.tbProduces.map((k) => (
            <span key={k} className="inline-flex h-[26px] items-center gap-1.5 rounded-md bg-primary px-2.5 font-mono text-[10px] font-semibold text-white">
              {k}
              <button type="button" onClick={() => toggleArr("tbProduces", k)} className="opacity-75 hover:opacity-100" aria-label={`Remove ${k}`}>✕</button>
            </span>
          ))}
          {form.tbProduces.length === 0 && <span className="py-1 text-[10.5px] text-faint">No metrics selected — add from the registry below.</span>}
        </div>
        <div className="mb-1.5 flex h-[30px] items-center gap-1.5 rounded-md border border-border bg-panel px-2.5">
          <Search className="h-3 w-3 text-faint" aria-hidden />
          <input value={form.tbProduceSearch} onChange={(e) => setStr("tbProduceSearch", e.target.value)} placeholder="Search metrics registry…" className="w-full bg-transparent font-mono text-[10.5px] outline-hidden placeholder:text-faint" />
        </div>
        <div className="max-h-[168px] overflow-y-auto rounded-lg border border-border">
          {avail.map((k) => (
            <CheckRow key={k} bordered={false} on={false} onClick={() => toggleArr("tbProduces", k)}>
              <span className="flex items-center gap-2.5">
                <span className="w-[100px] shrink-0 font-mono text-[10.5px]">{k}</span>
                <span className="text-[10.5px] text-muted">{metricInfo[k]?.d ?? ""}</span>
              </span>
            </CheckRow>
          ))}
          {avail.length === 0 && <div className="px-3 py-2.5 text-[10.5px] text-faint">No more metrics for this class.</div>}
        </div>
      </div>
      <div>
        <FieldLabel>TEMPLATE FLAGS</FieldLabel>
        <div className={PILL_ROW}>
          {TB_FLAGS.map((f) => {
            const on = form.tbFlags.includes(f);
            return (
              <PillChoice key={f} mono active={on} onClick={() => toggleArr("tbFlags", f)}>
                {on ? `✓ ${f}` : f}
              </PillChoice>
            );
          })}
        </div>
      </div>
      <EnabledToggle />
    </div>
  );
}

function EnabledToggle() {
  const enabled = useLibraryWizardStore((s) => s.form.tbEnabled);
  const setBool = useLibraryWizardStore((s) => s.setBool);
  return (
    <div className="flex items-center gap-2.5 rounded-lg border border-border p-3">
      <div className="flex-1">
        <div className="text-[11.5px] font-semibold">Enabled</div>
        <div className="text-[10px] text-muted">false = scaffolded but skipped by the runner &amp; sim tiers (T3/T4)</div>
      </div>
      <Toggle on={enabled} onClick={() => setBool("tbEnabled", !enabled)} label="Enabled" />
    </div>
  );
}

// ── Template identity ────────────────────────────────────────────────────────
export function TplIdentityStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const setTfamily = useLibraryWizardStore((s) => s.setTfamily);
  return (
    <div className="flex flex-col gap-4">
      <TextField label="TEMPLATE ID" value={form.tid} onChange={(v) => setStr("tid", v)} caption="tags every detected match · e.g. cm.nmos.cascode" />
      <TextField label="DISPLAY NAME" value={form.tname} onChange={(v) => setStr("tname", v)} mono={false} />
      <div>
        <FieldLabel>FAMILY</FieldLabel>
        <div className={PILL_ROW}>
          {TPL_FAMILIES.map(([key, label]) => (
            <PillChoice key={key} active={form.tfamily === key} onClick={() => setTfamily(key)}>{label}</PillChoice>
          ))}
        </div>
      </div>
      <div className="flex gap-3">
        <div>
          <FieldLabel>POLARITY</FieldLabel>
          <Segmented value={form.tpolarity} onChange={(v) => setStr("tpolarity", v)} options={TPL_POLARITIES} />
        </div>
        <div className="flex-1">
          <TextField label="ROLE" value={form.trole} onChange={(v) => setStr("trole", v)} />
        </div>
      </div>
    </div>
  );
}

// ── Template ports ───────────────────────────────────────────────────────────
export function TplPortsStep() {
  const { form } = useLibraryWizardStore();
  const setStr = useLibraryWizardStore((s) => s.setStr);
  const setPort = useLibraryWizardStore((s) => s.setPort);
  const addPort = useLibraryWizardStore((s) => s.addPort);
  const removePort = useLibraryWizardStore((s) => s.removePort);
  return (
    <div className="flex flex-col gap-4">
      <div>
        <FieldLabel hint="edit role → net; add or remove rows">PORT ROLES</FieldLabel>
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="grid gap-2 border-b border-border bg-panel px-2.5 py-1.5" style={PARAM_ROW}>
            <span className="text-[9px] font-bold uppercase tracking-wider text-faint">ROLE</span>
            <span className="text-[9px] font-bold uppercase tracking-wider text-faint">NET</span>
            <span />
          </div>
          {form.tportRows.map((p, i) => (
            <div key={i} className="grid items-center gap-2 border-b border-hairline px-2.5 py-1.5" style={PARAM_ROW}>
              <input aria-label={`port ${i + 1} role`} value={p[0]} onChange={(e) => setPort(i, 0, e.target.value)} className="h-7 w-full rounded-md border border-border bg-panel px-2 font-mono text-[10.5px] outline-hidden focus:border-[#c7d2fe]" />
              <input aria-label={`port ${i + 1} net`} value={p[1]} onChange={(e) => setPort(i, 1, e.target.value)} className="h-7 w-full rounded-md border border-border bg-panel px-2 font-mono text-[10.5px] outline-hidden focus:border-[#c7d2fe]" />
              <button type="button" onClick={() => removePort(i)} className="text-center text-faint hover:text-fg" aria-label="Remove port">✕</button>
            </div>
          ))}
          <button type="button" onClick={addPort} className="w-full px-3 py-1.5 text-left text-[10.5px] text-primary hover:bg-[#fafaff]">+ Add port</button>
        </div>
      </div>
      <div>
        <FieldLabel>NETLIST</FieldLabel>
        <DropZone small>
          Drop the template netlist <span className="font-mono text-[10px]">.spice</span> — or <span className="text-primary">browse</span>
        </DropZone>
        <div className="mt-2 flex items-center gap-2 rounded-lg border border-border px-2.5 py-1.5">
          <span className="h-[7px] w-[7px] rounded-full bg-ok" />
          <span className="font-mono text-[10.5px] text-muted">{form.tnetlist}</span>
          <span className="text-[10px] text-faint">uploaded</span>
          <div className="flex-1" />
          <span className="font-mono text-[9.5px] text-faint">netlisted from xschem</span>
        </div>
        <div className="mt-2">
          <div className="mb-1 text-[9px] text-faint">FILE NAME · rename</div>
          <TextField value={form.tnetlist} onChange={(v) => setStr("tnetlist", v)} />
        </div>
      </div>
      <div className="rounded-lg bg-secondary-soft px-3 py-2.5 text-[10.5px] leading-relaxed text-[#155e75]">
        Matching is topological — only device type, MOS polarity and pin-level wiring matter (<span className="font-mono text-[10px]">match_supply</span> anchors the rail). A differential pair additionally requires its <span className="font-mono text-[10px]">CM_tail</span> on a detected current-mirror output.
      </div>
    </div>
  );
}

// ── Review ───────────────────────────────────────────────────────────────────
export function ReviewStep({ d }: { d: WizardDerived }) {
  const kind = useLibraryWizardStore((s) => s.form.kind);
  return (
    <div className="flex flex-col gap-4">
      <SummaryCard title="SUMMARY">
        {d.review.map((r) => (
          <div key={r.k} className="flex justify-between gap-2.5 px-3 py-1.5 text-[11px]">
            <span className="text-muted">{r.k}</span>
            <span className="text-right font-mono">{r.v}</span>
          </div>
        ))}
      </SummaryCard>
      <SummaryCard title={kind === "circuit" ? "analog-db generate WILL WRITE" : "WILL WRITE"}>
        <div className="flex flex-col gap-1 px-3 py-2">
          {d.fileList.map((f) => (
            <div key={f} className="font-mono text-[10px] text-muted">{f}</div>
          ))}
        </div>
      </SummaryCard>
      {kind === "template" ? (
        <div className="rounded-lg bg-secondary-soft px-3 py-2.5 text-[10.5px] leading-relaxed text-[#155e75]">
          Once registered, this template is available to the subcircuit matcher for every circuit&apos;s block detection.
        </div>
      ) : (
        <div className="flex gap-2">
          {["T0 schema", "T1 generation", "T2 assembly"].map((t) => (
            <span key={t} className="flex flex-1 items-center gap-1.5 rounded-lg bg-ok-soft px-2.5 py-2 text-[10.5px] font-semibold text-ok">
              <span className="h-1.5 w-1.5 rounded-full bg-ok" />{t}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// ── small shared bits ────────────────────────────────────────────────────────
function Note({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg border border-hairline bg-bg px-3 py-2.5 text-[10.5px] leading-relaxed text-muted">{children}</div>;
}

function SummaryCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <div className="border-b border-hairline bg-bg px-3 py-2 text-[9.5px] font-bold uppercase tracking-[0.08em] text-muted">{title}</div>
      <div className="py-1">{children}</div>
    </div>
  );
}

function DropZone({ children, small }: { children: React.ReactNode; small?: boolean }) {
  return (
    <div
      className={cn("flex flex-col items-center justify-center gap-1.5 rounded-[10px] border-[1.5px] border-dashed border-[#c7d2fe] bg-[#fafaff] text-center", small ? "h-[78px]" : "h-[94px]")}
      style={{ backgroundImage: "repeating-linear-gradient(135deg,#fafafa 0,#fafafa 6px,#f4f4f5 6px,#f4f4f5 7px)" }}
    >
      <Upload className="h-4 w-4 text-primary" aria-hidden />
      <span className="text-[11px] text-muted">{children}</span>
      <span className="text-[10px] text-primary">or browse files</span>
    </div>
  );
}

// re-export so the overlay can use the editor preview without a second import path
export { EditorPane };
