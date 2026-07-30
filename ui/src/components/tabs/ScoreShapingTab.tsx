"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Panel, PanelBody, PanelHeader } from "@/components/ui/panel";
import { useProjectStore } from "@/stores/projectStore";
import { useUIStore } from "@/stores/uiStore";
import { api } from "@/lib/api";
import { formatEng, goalSymbol, parseEng } from "@/lib/utils";
import type { ScoreResponse, TargetSpec } from "@/types/api";
import { PenaltyCurveChart } from "@/components/charts/PenaltyCurveChart";
import { ScoreWaterfallChart } from "@/components/charts/ScoreWaterfallChart";
import { EmptyState } from "@/components/ui/empty-state";
import { selectCn } from "@/components/ui/select";
import { Thead, Th, Tr, Td } from "@/components/ui/table";
import { Slider } from "@/components/ui/slider";
import { Stat } from "@/components/ui/stat";
import { Segmented } from "@/components/ui/segmented";
import { Toolbar, ToolbarLabel, ToolbarSpacer } from "@/components/shell/Toolbar";
import { Separator } from "@/components/ui/separator";

type Shaping = "sigmoid" | "linear";

export function ScoreShapingTab() {
  const { summary, yamlPath, isApplied } = useProjectStore();
  // Deep-link target set by the ⌘K palette ("Jump to spec").
  const uiSelectedSpec = useUIStore((s) => s.selectedSpec);
  const [selectedSpec, setSelectedSpec] = useState<string>("");
  // Global shaping toggle — drives the waterfall + the F(x) KPI card so the user
  // sees how one normalization rebalances which spec binds (the penalty curve and
  // breakdown table keep showing both for direct comparison).
  const [shaping, setShaping] = useState<Shaping>("sigmoid");
  // Per-spec "try" values (each defaults to its target). The WHOLE vector is
  // sent to /api/score so the aggregate F(x) and the per-spec breakdown reflect
  // all specs simultaneously — not just the one in the slider.
  const [values, setValues] = useState<Record<string, number>>({});
  const [scoreData, setScoreData] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(false);
  // Ephemeral per-spec edits (what-if). Each edit is a partial patch keyed by spec
  // name; raw strings are kept so eng-values ("250u") pass straight to the backend's
  // parse_value. Local state ⇒ resets on unmount — never written to YAML.
  const [specEdits, setSpecEdits] = useState<
    Record<string, Partial<Record<"target" | "tolerance" | "range" | "weight" | "goal" | "enable", string | number | boolean>>>
  >({});
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const consumedDeepLink = useRef<string | null>(null);

  // Specs with the user's ephemeral edits merged in, so the slider range, target
  // marker, dropdown labels, and breakdown all reflect what the score call sees.
  const effectiveSpecs = useMemo<TargetSpec[]>(() => {
    const all = summary?.target_specs ?? [];
    return all.map((s) => {
      const e = specEdits[s.name];
      if (!e) return s;
      // Parse with parseEng (not bare Number) so the engineering strings the editor invites
      // ("250u") don't read as NaN and poison the slider/marker math (BUG-B48).
      const num = (v: string | number | boolean | undefined, fallback: number | null) =>
        v === undefined || v === "" ? fallback : parseEng(v as string | number);
      return {
        ...s,
        target: e.target !== undefined && e.target !== "" ? parseEng(e.target as string | number) : s.target,
        tolerance: num(e.tolerance, s.tolerance),
        range: num(e.range, s.range),
        weight: e.weight !== undefined && e.weight !== "" ? parseEng(e.weight as string | number) : s.weight,
        goal: (e.goal as TargetSpec["goal"]) ?? s.goal,
        enable: e.enable !== undefined ? Boolean(e.enable) : s.enable,
      };
    });
  }, [summary, specEdits]);

  const enabledSpecs = useMemo(
    () => effectiveSpecs.filter((s) => s.enable),
    [effectiveSpecs],
  );
  const hasEdits = Object.keys(specEdits).length > 0;

  // Seed the value map (and default selection) when a project loads.
  useEffect(() => {
    if (!summary || enabledSpecs.length === 0) return;
    setValues((prev) => {
      const next = { ...prev };
      for (const s of enabledSpecs) if (!(s.name in next)) next[s.name] = s.target;
      return next;
    });
    setSelectedSpec((cur) => cur || enabledSpecs[0].name);
  }, [summary, enabledSpecs]);

  // Honor a ⌘K / rail / pipeline deep-link — but only ONCE per distinct target,
  // so it doesn't fight the dropdown (which previously snapped back every pick).
  useEffect(() => {
    if (!uiSelectedSpec || consumedDeepLink.current === uiSelectedSpec) return;
    const match = enabledSpecs.find((s) => s.name === uiSelectedSpec);
    if (match) {
      consumedDeepLink.current = uiSelectedSpec;
      setSelectedSpec(match.name);
    }
  }, [uiSelectedSpec, enabledSpecs]);

  const handleSpecChange = (specName: string) => setSelectedSpec(specName);

  const setSpecValue = (specName: string, value: number) =>
    setValues((prev) => ({ ...prev, [specName]: value }));

  const computeScore = useCallback(
    (
      vals: Record<string, number>,
      specName: string,
      overrides: Record<string, Record<string, string | number | boolean>>,
    ) => {
      if (!yamlPath || !specName) return;
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(async () => {
        setLoading(true);
        try {
          // Full vector of current values; selected_spec only drives the curve.
          // specOverrides carry the ephemeral what-if spec edits (never persisted).
          const result = await api.computeScore(yamlPath, vals, {
            selectedSpec: specName,
            specOverrides: Object.keys(overrides).length ? overrides : undefined,
          });
          setScoreData(result);
        } finally {
          setLoading(false);
        }
      }, 150);
    },
    [yamlPath],
  );

  useEffect(() => {
    if (selectedSpec) computeScore(values, selectedSpec, specEdits);
  }, [values, selectedSpec, specEdits, computeScore]);

  if (!isApplied || !summary) {
    return (
      <div className="flex-1 p-3">
        <EmptyState bordered minHeight="min-h-60">
          Apply a project first to explore score shaping.
        </EmptyState>
      </div>
    );
  }

  const currentSpec: TargetSpec | undefined = effectiveSpecs.find(
    (s) => s.name === selectedSpec,
  );
  // Guard against a transiently-NaN target/range (mid-typing an eng-string) so the slider stays usable.
  const safeTarget = Number.isFinite(currentSpec?.target as number) ? (currentSpec!.target as number) : 0;
  const range =
    currentSpec?.range && Number.isFinite(currentSpec.range) && currentSpec.range > 0
      ? currentSpec.range
      : Math.max(Math.abs(safeTarget), 1) * 0.5;
  const target = safeTarget;
  const metricValue = values[selectedSpec] ?? target;
  const sliderMin = target - 3 * range;
  const sliderMax = target + 3 * range;

  const aggregate = scoreData?.aggregate;
  const weightSum = enabledSpecs.reduce((a, s) => a + (s.weight ?? 0), 0);

  // Find dominating spec under each shaping
  const dominantSig = scoreData
    ? Object.entries(scoreData.per_spec)
        .map(([k, v]) => [k, (v.sigmoid ?? 0) * (v.weight ?? 0)] as const)
        .sort(([, a], [, b]) => b - a)[0]
    : null;
  const dominantLin = scoreData
    ? Object.entries(scoreData.per_spec)
        .map(([k, v]) => [k, (v.linear ?? 0) * (v.weight ?? 0)] as const)
        .sort(([, a], [, b]) => b - a)[0]
    : null;

  // Shaping-aware derived values (KPI cards + waterfall).
  const dominant = shaping === "sigmoid" ? dominantSig : dominantLin;
  const aggValue = aggregate ? (shaping === "sigmoid" ? aggregate.sigmoid : aggregate.linear) : null;
  const waterfallBars = scoreData
    ? enabledSpecs.map((s) => {
        const e = scoreData.per_spec[s.name];
        const pen = (shaping === "sigmoid" ? e?.sigmoid : e?.linear) ?? 0;
        return { name: s.name, contribution: pen * (s.weight ?? 0), passes: e?.passes ?? null };
      })
    : [];

  return (
    <>
      <Toolbar>
        <ToolbarLabel>spec</ToolbarLabel>
        <select
          aria-label="Select target spec"
          value={selectedSpec}
          onChange={(e) => handleSpecChange(e.target.value)}
          className={selectCn("sm")}
        >
          {effectiveSpecs.map((s) => (
            <option key={s.name} value={s.name}>
              {s.name} · {goalSymbol(s.goal)} {formatEng(s.target)}
              {s.enable ? "" : " (off)"}
            </option>
          ))}
        </select>
        <Separator />
        <ToolbarLabel>shaping</ToolbarLabel>
        <Segmented<Shaping>
          value={shaping}
          onChange={setShaping}
          options={[
            { value: "sigmoid", label: "sigmoid" },
            { value: "linear", label: "linear" },
          ]}
        />
        <Separator />
        <ToolbarLabel>range</ToolbarLabel>
        <span className="font-mono text-[11px] text-fg">
          target ± 3 × {formatEng(range)}
        </span>
        <ToolbarSpacer />
        {hasEdits && (
          <button
            type="button"
            onClick={() => setSpecEdits({})}
            className="text-[11px] text-primary hover:underline"
          >
            Reset edits
          </button>
        )}
        <span className="font-mono text-[11px] text-muted">
          POST /api/score · 150ms debounce
        </span>
      </Toolbar>

      <div className="grid shrink-0 grid-cols-3 gap-2.5 border-b border-border px-3 py-2.5">
        <Stat
          eyebrow={`F(x) · ${shaping}`}
          value={aggValue != null ? aggValue.toFixed(3) : "—"}
          tone={aggValue != null && aggValue > 0 ? "warn" : "ok"}
        />
        <Stat
          eyebrow="highest-penalty spec"
          value={dominant && dominant[1] > 0 ? dominant[0] : "—"}
          unit={dominant && dominant[1] > 0 ? `wᵢ·P̂ ${dominant[1].toFixed(3)}` : "all pass"}
        />
        <Stat eyebrow="active specs" value={String(enabledSpecs.length)} unit={`Σw ${weightSum.toFixed(1)}`} />
      </div>

      <div
        className="grid min-h-0 flex-1 gap-3 overflow-auto p-3"
        style={{ gridTemplateColumns: "1.5fr 1fr" }}
      >
        {/* Left: spec editor + penalty chart + slider + callout */}
        <div className="flex min-w-0 flex-col gap-2.5">
          {currentSpec && (
            <SpecEditor
              spec={currentSpec}
              edit={specEdits[currentSpec.name]}
              onChange={(patch) =>
                setSpecEdits((prev) => {
                  const name = currentSpec.name;
                  const merged = { ...prev[name], ...patch };
                  // Drop keys set back to "" / undefined so a fully-reverted spec
                  // disappears from the override map (and "Reset edits" hides).
                  for (const k of Object.keys(merged) as (keyof typeof merged)[]) {
                    if (merged[k] === "" || merged[k] === undefined) delete merged[k];
                  }
                  const next = { ...prev };
                  if (Object.keys(merged).length === 0) delete next[name];
                  else next[name] = merged;
                  return next;
                })
              }
            />
          )}
          <Panel>
            <PanelHeader
              title="penalty curve"
              mute="· sigmoid vs linear"
              right={
                currentSpec && (
                  <span className="font-mono text-[10px] text-muted">
                    {currentSpec.name} · {goalSymbol(currentSpec.goal)}{" "}
                    {formatEng(currentSpec.target)}
                  </span>
                )
              }
            />
            <PanelBody>
              {scoreData?.curve ? (
                <PenaltyCurveChart
                  curve={scoreData.curve}
                  currentValue={metricValue}
                />
              ) : (
                <EmptyState minHeight="h-[280px]">
                  {loading ? "Computing…" : "No curve data."}
                </EmptyState>
              )}
              {currentSpec && (
                <div className="mt-2.5">
                  <Slider
                    value={metricValue}
                    min={sliderMin}
                    max={sliderMax}
                    step={(sliderMax - sliderMin) / 200}
                    onChange={(v) => setSpecValue(selectedSpec, v)}
                    markerValue={target}
                    markerLabel="target"
                  />
                  <div className="mt-1.5 flex items-center justify-between font-mono text-[11px]">
                    <span className="text-muted">{formatEng(sliderMin)}</span>
                    <span className="font-medium text-fg">
                      now {formatEng(metricValue)}
                    </span>
                    <span className="text-muted">{formatEng(sliderMax)}</span>
                  </div>
                </div>
              )}
            </PanelBody>
          </Panel>

          {dominantSig && dominantLin && (
            <div className="flex gap-2.5 rounded-md border-l-2 border-primary bg-primary-soft px-3 py-2.5 text-xs text-fg">
              <span className="font-mono text-sm text-primary">◆</span>
              <div>
                Under <b className="text-primary">sigmoid</b> shaping,{" "}
                <span className="font-mono">{dominantSig[0]}</span> dominates
                F(x) (weighted P̂ = {dominantSig[1].toFixed(3)}). Under{" "}
                <b className="text-secondary">linear</b> shaping,{" "}
                <span className="font-mono">{dominantLin[0]}</span> dominates
                (weighted P̂ = {dominantLin[1].toFixed(3)}). Switching shaping
                rebalances which constraint the optimizer chases.
              </div>
            </div>
          )}

          <Panel>
            <PanelHeader
              title="score contribution"
              mute={`· ${shaping} · wᵢ·P̂ᵢ per spec`}
              right={
                <span className="font-mono text-[10px] text-muted">
                  green = pass · red = binding
                </span>
              }
            />
            <PanelBody>
              {waterfallBars.length > 0 ? (
                <ScoreWaterfallChart bars={waterfallBars} />
              ) : (
                <EmptyState minHeight="h-[240px]">
                  {loading ? "Computing…" : "No data."}
                </EmptyState>
              )}
            </PanelBody>
          </Panel>
        </div>

        {/* Right: per-spec breakdown */}
        <Panel className="flex min-w-0 flex-col">
          <PanelHeader
            title="per-spec breakdown"
            mute="· F(x) = Σ wᵢ · P̂ᵢ"
            right={
              loading && (
                <span aria-live="polite" className="text-[10px] text-muted">
                  computing…
                </span>
              )
            }
          />
          <div className="min-h-0 flex-1 overflow-auto">
            <table className="w-full">
              <Thead>
                <Th>spec</Th>
                <Th>current</Th>
                <Th>sigmoid P̂</Th>
                <Th>linear P̂</Th>
                <Th>w</Th>
              </Thead>
              <tbody>
                {enabledSpecs.map((s) => {
                  const entry = scoreData?.per_spec[s.name];
                  const passes = entry?.passes;
                  return (
                    <Tr key={s.name} highlight={s.name === selectedSpec}>
                      <Td className="font-mono">
                        <span className={s.name === selectedSpec ? "font-medium" : ""}>
                          {s.name}
                        </span>
                      </Td>
                      <Td className="font-mono">
                        {/* Inline try-value editor — edits flow into the shared
                            `values` vector, so the aggregate F(x), waterfall, and
                            (for the selected spec) the slider all update live. */}
                        <input
                          aria-label={`${s.name} value`}
                          type="number"
                          step="any"
                          value={Number.isFinite(values[s.name]) ? values[s.name] : ""}
                          onChange={(e) => {
                            const v = Number(e.target.value);
                            if (Number.isFinite(v)) setSpecValue(s.name, v);
                          }}
                          className={
                            selectCn("xs") +
                            " w-[96px] " +
                            (passes === true ? "text-ok" : passes === false ? "text-danger" : "text-fg")
                          }
                        />
                      </Td>
                      <Td className="font-mono">
                        <PenaltyBar
                          value={entry?.sigmoid ?? null}
                          color="bg-primary"
                        />
                      </Td>
                      <Td className="font-mono">
                        <PenaltyBar
                          value={entry?.linear ?? null}
                          color="bg-secondary"
                        />
                      </Td>
                      <Td className="font-mono">{(s.weight ?? 0).toFixed(1)}</Td>
                    </Tr>
                  );
                })}
              </tbody>
              {aggregate && (
                <tfoot>
                  <tr className="border-t border-border bg-hairline font-medium">
                    <td className="px-2.5 py-1.5 font-mono text-[11px]" colSpan={2}>
                      F(x) aggregate
                    </td>
                    <td className="px-2.5 py-1.5 font-mono text-[11px] text-primary">
                      {aggregate.sigmoid.toFixed(3)}
                    </td>
                    <td className="px-2.5 py-1.5 font-mono text-[11px] text-secondary">
                      {aggregate.linear.toFixed(3)}
                    </td>
                    <td className="px-2.5 py-1.5 font-mono text-[11px]">
                      Σ {weightSum.toFixed(1)}
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </Panel>
      </div>
    </>
  );
}

type SpecEditPatch = Partial<
  Record<"target" | "tolerance" | "range" | "weight" | "goal" | "enable", string | number | boolean>
>;

/**
 * Inline editor for the selected spec's shaping-relevant fields. Edits are
 * EPHEMERAL (what-if): they feed the score preview via spec_overrides and are never
 * written to the YAML — reloading or re-applying the project discards them. Numeric
 * fields stay as raw strings (uncontrolled by the merged number) so engineering
 * values like "250u" pass straight through to the backend's parse_value; a blank
 * field reverts that one override.
 */
function SpecEditor({
  spec,
  edit,
  onChange,
}: {
  spec: TargetSpec;
  edit: SpecEditPatch | undefined;
  onChange: (patch: SpecEditPatch) => void;
}) {
  // Show the raw edit string if present, else the project's value (so the field is
  // pre-filled and editable). enable/goal come from the merged effective spec.
  const fieldVal = (key: "target" | "tolerance" | "range" | "weight", base: number | null) => {
    const e = edit?.[key];
    if (e !== undefined) return String(e);
    return base != null ? String(base) : "";
  };

  // Inlined (not a nested component) so editing one field doesn't remount the
  // inputs and steal focus on every keystroke.
  const numFields: { label: string; key: "target" | "tolerance" | "range" | "weight"; base: number | null }[] = [
    { label: "target", key: "target", base: spec.target },
    { label: "tolerance", key: "tolerance", base: spec.tolerance },
    { label: "range", key: "range", base: spec.range },
    { label: "weight", key: "weight", base: spec.weight },
  ];

  return (
    <Panel>
      <PanelHeader
        title="edit spec"
        mute="· what-if · not saved to YAML"
        right={
          <label className="flex items-center gap-1.5 text-[11px] text-muted">
            <input
              type="checkbox"
              checked={spec.enable}
              onChange={(e) => onChange({ enable: e.target.checked })}
              aria-label={`${spec.name} enabled`}
            />
            enabled
          </label>
        }
      />
      <PanelBody className="flex flex-wrap items-end gap-2.5">
        {numFields.map((f) => (
          <label key={f.key} className="flex flex-col gap-1">
            <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
              {f.label}
            </span>
            <input
              aria-label={`${spec.name} ${f.label}`}
              type="text"
              placeholder="—"
              value={fieldVal(f.key, f.base)}
              onChange={(e) => onChange({ [f.key]: e.target.value })}
              className={selectCn("xs") + " w-[88px]"}
            />
          </label>
        ))}
        <label className="flex flex-col gap-1">
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted">goal</span>
          <select
            aria-label={`${spec.name} goal`}
            value={spec.goal}
            onChange={(e) => onChange({ goal: e.target.value })}
            className={selectCn("xs")}
          >
            <option value="exceed">exceed (≥)</option>
            <option value="minimize">minimize (≤)</option>
            <option value="exact">exact (≈)</option>
          </select>
        </label>
        <span className="pb-1.5 font-mono text-[10px] text-faint">
          eng values ok (250u); blank reverts
        </span>
      </PanelBody>
    </Panel>
  );
}

function PenaltyBar({
  value,
  color,
}: {
  value: number | null;
  color: string;
}) {
  const pct =
    value == null
      ? 0
      : Math.max(0, Math.min(1, value)) * 100;
  return (
    <span className="inline-flex items-center">
      <span className="relative mr-1.5 inline-block h-1 w-9 rounded-xs bg-hairline align-middle">
        <span
          className={`absolute left-0 top-0 h-full rounded-xs ${color}`}
          style={{ width: `${pct}%` }}
        />
      </span>
      {value != null ? value.toFixed(2) : "—"}
    </span>
  );
}
