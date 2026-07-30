"use client";
import { useRef } from "react";
import { cn, statusForGoal } from "@/lib/utils";
import { ResizeHandle, useRailWidth } from "@/components/ui/resizable";
import { Segmented } from "@/components/ui/segmented";
import { selectCn } from "@/components/ui/select";
import { useProjectStore } from "@/stores/projectStore";
import { useWaveviewStore } from "@/stores/waveviewStore";
import { DOWNSAMPLE_OPTIONS, FMT_OPTIONS, MC_SIGMA_OPTIONS } from "@/lib/waveview/config";
import {
  baseAnalysis,
  isDbNativeSignal,
  parseDownsample,
  plotStyleFor,
  plottableSignals,
} from "@/lib/waveview/selectors";
import { cornerResults, headlineFor, specForMeas } from "@/lib/waveview/sweep";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-b border-hairline px-3 py-2.5">
      <div className="mb-1.5 text-[9.5px] font-bold uppercase tracking-[0.08em] text-muted">
        {title}
      </div>
      {children}
    </div>
  );
}

/** PVT CORNERS — checkbox rows over the run's per-corner datasets, each with
 *  its measured headline metric (pass/fail colored only via a project spec). */
function PvtCornersSection() {
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepMetrics = useWaveviewStore((s) => s.sweepMetrics);
  const cornerEnabled = useWaveviewStore((s) => s.cornerEnabled);
  const toggleCorner = useWaveviewStore((s) => s.toggleCorner);
  const catalog = useWaveviewStore((s) => s.catalog);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const summary = useProjectStore((s) => s.summary);

  const base = activeAnalysis ? baseAnalysis(activeAnalysis) : "";
  const headline = headlineFor(base, catalog);
  const spec = headline ? specForMeas(summary?.target_specs ?? null, headline.meas) : null;
  const corners = cornerResults(sweepMembers, sweepMetrics, cornerEnabled);
  const on = corners.filter((c) => c.enabled).length;

  return (
    <div className="border-b border-hairline px-3 py-2.5">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-[9.5px] font-bold uppercase tracking-[0.08em] text-muted">
          PVT corners
        </span>
        <span className="font-mono text-[9px] text-primary">
          {on}/{corners.length}
        </span>
      </div>
      {sweepStatus === "loading" ? (
        <div className="font-mono text-[9.5px] text-faint">discovering corners…</div>
      ) : corners.length === 0 ? (
        <div className="text-[10px] leading-relaxed text-faint">
          No per-corner artifacts in this run — a corners sweep writes{" "}
          <span className="font-mono">…__&lt;corner&gt;/</span> result folders.
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-px">
            {corners.map((c) => {
              const metricOk =
                spec && c.metric != null
                  ? statusForGoal(spec.goal, c.metric, spec.target, spec.tolerance ?? undefined)
                  : null;
              return (
                <button
                  key={c.key}
                  type="button"
                  onClick={() => toggleCorner(c.key)}
                  className="flex w-full items-center gap-1.5 rounded-[5px] px-1 py-[3px] text-left hover:bg-hairline"
                >
                  <span
                    className={cn(
                      "flex h-3 w-3 shrink-0 items-center justify-center rounded-[3px] text-[8px]",
                      c.enabled ? "bg-primary text-white" : "border border-[#d4d4d8] bg-panel",
                    )}
                    aria-hidden
                  >
                    {c.enabled && "✓"}
                  </span>
                  <span
                    className="h-[3px] w-3 shrink-0 rounded-[2px]"
                    style={{ background: c.color, opacity: c.enabled ? 1 : 0.3 }}
                    aria-hidden
                  />
                  <span
                    className={cn(
                      "min-w-0 flex-1 truncate font-mono text-[9.5px]",
                      c.enabled ? "text-fg" : "text-faint",
                    )}
                  >
                    {c.name}
                  </span>
                  <span
                    className={cn(
                      "shrink-0 font-mono text-[9px]",
                      metricOk === "pass"
                        ? "text-ok"
                        : metricOk === "fail"
                          ? "text-danger"
                          : "text-muted",
                    )}
                  >
                    {c.metric != null
                      ? `${c.metric.toPrecision(3)}${headline?.unit === "°" ? "°" : ""}`
                      : "—"}
                  </span>
                </button>
              );
            })}
          </div>
          <div className="mt-1.5 font-mono text-[9px] text-faint">
            /open_run?match=__&lt;corner&gt; · {on} corners
          </div>
        </>
      )}
    </div>
  );
}

/** MONTE CARLO — sample count from the run, the ±σ band, histogram metric. */
function McSection() {
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const mcSigma = useWaveviewStore((s) => s.mcSigma);
  const setMcSigma = useWaveviewStore((s) => s.setMcSigma);
  const catalog = useWaveviewStore((s) => s.catalog);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);

  const base = activeAnalysis ? baseAnalysis(activeAnalysis) : "";
  const headline = headlineFor(base, catalog);

  return (
    <Section title="Monte Carlo">
      {sweepStatus === "loading" ? (
        <div className="font-mono text-[9.5px] text-faint">discovering samples…</div>
      ) : sweepMembers.length === 0 ? (
        <div className="text-[10px] leading-relaxed text-faint">
          No MC sample artifacts in this run — a Monte Carlo sweep writes{" "}
          <span className="font-mono">…__mc&lt;n&gt;/</span> result folders.
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-[9px] text-muted">samples · from run</span>
            <span className="font-mono text-[10px] text-fg">{sweepMembers.length}</span>
          </div>
          <div>
            <div className="mb-1 text-[9px] text-muted">band</div>
            <Segmented
              value={String(mcSigma)}
              onChange={(v) => setMcSigma(Number(v))}
              options={MC_SIGMA_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
              className="w-full text-[10px]"
            />
          </div>
          {headline && (
            <div>
              <div className="mb-1 text-[9px] text-muted">histogram metric</div>
              <div className="rounded-md border border-border bg-bg px-2 py-1 font-mono text-[10px] text-fg">
                {headline.meas} · {headline.label}
              </div>
            </div>
          )}
        </div>
      )}
    </Section>
  );
}

/** Right rail — AXES · UNITS. Presentation controls over the /wave query params;
 *  hiding it hands the plot full width (Plotly re-fits via responsive resize). */
export function AxesRail() {
  const activeId = useWaveviewStore((s) => s.activeId);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const datasets = useWaveviewStore((s) => s.datasets);
  const xScale = useWaveviewStore((s) => s.xScale);
  const fmt = useWaveviewStore((s) => s.fmt);
  const downsample = useWaveviewStore((s) => s.downsample);
  const outSignal = useWaveviewStore((s) => s.outSignal);
  const wave = useWaveviewStore((s) => s.wave);
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const setXScale = useWaveviewStore((s) => s.setXScale);
  const setFmt = useWaveviewStore((s) => s.setFmt);
  const setDownsample = useWaveviewStore((s) => s.setDownsample);
  const setOutSignal = useWaveviewStore((s) => s.setOutSignal);
  const toggleRail = useWaveviewStore((s) => s.toggleRail);

  const railRef = useRef<HTMLElement>(null);
  const [railWidth, setRailWidth] = useRailWidth("ui:rail:analyze-axes", 214, 180, 420);

  const ds = datasets.find((d) => d.dataset_id === activeId);
  const style = plotStyleFor(activeAnalysis);
  const dual = !!style.dual;
  const effXScale = xScale ?? style.xScale;
  const { method, max_points } = parseDownsample(downsample);
  // deck-computed dB curves fetch fmt=re (already dB) and carry no phase — the
  // rail must report what was actually requested, not the Bode default
  const nDb = wave?.signals.filter((s) => isDbNativeSignal(s.name)).length ?? 0;
  const nSig = wave?.signals.length ?? 0;
  const dualFmt = nDb === 0 ? "mag_db" : nDb === nSig ? "re" : "mag_db·re";
  const dualPhase = dual && !(nSig > 0 && nDb === nSig);
  const allSignals = [
    ...new Set(ds?.analyses.flatMap((a) => plottableSignals(a)) ?? []),
  ];

  return (
    <aside
      ref={railRef}
      style={{ width: railWidth }}
      className="relative flex shrink-0 flex-col border-l border-border bg-panel"
    >
      <ResizeHandle
        edge="left"
        size={railWidth}
        compute={(x) => (railRef.current?.getBoundingClientRect().right ?? 0) - x}
        onSize={setRailWidth}
        resetTo={214}
        label="Resize the axes panel"
      />
      <div className="flex h-[34px] shrink-0 items-center justify-between border-b border-hairline px-3">
        <span className="text-[10px] font-bold uppercase tracking-[0.08em] text-muted">
          Axes · Units
        </span>
        <button
          type="button"
          onClick={toggleRail}
          className="font-mono text-[10px] text-faint hover:text-fg"
          title="Hide the axes panel"
        >
          ⟩ hide
        </button>
      </div>

      {/* sections scroll in a wrapper so the resize handle stays pinned to the edge */}
      <div className="min-h-0 flex-1 overflow-y-auto">
      {sweepMode === "pvt" && <PvtCornersSection />}
      {sweepMode === "mc" && <McSection />}
      <Section title="X scale">
        <Segmented
          value={effXScale}
          onChange={(v) => setXScale(v)}
          options={[
            { value: "log", label: "Log" },
            { value: "lin", label: "Linear" },
          ]}
        />
      </Section>

      <Section title="Axis map">
        <div className="space-y-1 font-mono text-[10px]">
          <div className="flex justify-between">
            <span className="text-faint">X</span>
            <span className="text-fg">
              {wave?.x_name ?? "—"} · {effXScale}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-faint">Y1</span>
            <span className="text-fg">{dual ? dualFmt : fmt}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-faint">Y2</span>
            <span className="text-fg">{dualPhase ? "phase_deg" : "—"}</span>
          </div>
        </div>
      </Section>

      <Section title="Format">
        <select
          className={selectCn("xs") + " w-full"}
          value={dual ? "mag_db" : fmt}
          disabled={dual}
          onChange={(e) => setFmt(e.target.value)}
          aria-label="Wave format"
          title={dual ? "Bode analyses are fixed to mag_db + phase_deg" : undefined}
        >
          {FMT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        {dual && (
          <div className="mt-1 font-mono text-[9px] text-faint">
            {nDb > 0
              ? "deck-dB traces fetch fmt=re (already dB)"
              : "dual-axis · mag_db + phase_deg"}
          </div>
        )}
      </Section>

      <Section title="Downsample · on displayed trace">
        <select
          className={selectCn("xs") + " w-full"}
          value={downsample}
          onChange={(e) => setDownsample(e.target.value)}
          aria-label="Downsample preset"
        >
          {DOWNSAMPLE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <div className="mt-1 font-mono text-[9px] text-faint">
          &method={method}&max_points={max_points}
        </div>
      </Section>

      <Section title="Measure · out signal">
        <select
          className={selectCn("xs") + " w-full font-mono"}
          value={outSignal ?? ""}
          onChange={(e) => setOutSignal(e.target.value)}
          aria-label="Measurement output signal"
        >
          {!outSignal && <option value="">—</option>}
          {allSignals.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
        <div className="mt-1 font-mono text-[9px] text-faint">
          Tier-1 recipes read this as `out`
        </div>
      </Section>

      <div className="px-3 py-2.5">
        <div className="mb-1.5 text-[9.5px] font-bold uppercase tracking-[0.08em] text-muted">
          /wave params
        </div>
        <div className="break-all rounded-md border border-hairline bg-bg p-2 font-mono text-[9px] leading-relaxed text-muted">
          analysis={activeAnalysis ?? "—"}
          <br />
          fmt={dual ? `${dualFmt}${dualPhase ? "·phase_deg" : ""}` : fmt}
          <br />
          method={method}&max_points={max_points}
        </div>
      </div>
      </div>
    </aside>
  );
}
