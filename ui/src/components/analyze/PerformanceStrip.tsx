"use client";
import { Stat } from "@/components/ui/stat";
import { SpecChip } from "@/components/ui/spec-chip";
import { useProjectStore } from "@/stores/projectStore";
import { useWaveviewStore } from "@/stores/waveviewStore";
import { formatEng, goalSymbol, statusForGoal } from "@/lib/utils";
import { STAT_CARDS } from "@/lib/waveview/config";
import {
  baseAnalysis,
  perfChips,
  type PerfChip,
} from "@/lib/waveview/selectors";
import {
  cornerResults,
  headlineFor,
  mcStats,
  pvtStats,
  specForMeas,
  type HeadlineMetric,
} from "@/lib/waveview/sweep";
import type { TargetSpec } from "@/types/api";

/** Progress toward a spec target, direction-aware ("exceed" → value/target,
 *  "minimize" → target/value), clamped to [0, 1]. Null without a target. */
function progressFor(chip: PerfChip): number | undefined {
  if (chip.value == null || chip.target == null || chip.target === 0) return undefined;
  const ratio =
    chip.goal === "minimize" ? chip.target / chip.value : chip.value / chip.target;
  if (!Number.isFinite(ratio) || ratio < 0) return undefined;
  return Math.min(1, ratio);
}

const fmtMetric = (h: HeadlineMetric | null, v: number) =>
  h ? formatEng(v, h.unit) : v.toPrecision(3);

const specTarget = (spec: TargetSpec | null, h: HeadlineMetric | null) =>
  spec ? `${goalSymbol(spec.goal)} ${formatEng(spec.target, h?.unit ?? "")}` : undefined;

const specStatus = (
  spec: TargetSpec | null,
  v: number | null,
): "ok" | "fail" | "neutral" => {
  if (!spec || v == null) return "neutral";
  const s = statusForGoal(spec.goal, v, spec.target, spec.tolerance ?? undefined);
  return s === "pass" ? "ok" : s === "fail" ? "fail" : "neutral";
};

/**
 * PERFORMANCE — the strip under the plot. Single mode composites the Tier-1
 * measures (POST /measure, targets only from applied-project specs). PVT mode
 * shows worst-case across the enabled corners; MC mode shows μ/σ, yield and
 * Cpk over the run's samples. Nothing is invented client-side: no spec →
 * neutral chips, and yield/Cpk require a spec to judge against.
 */
export function PerformanceStrip() {
  const sweepMode = useWaveviewStore((s) => s.sweepMode);
  const activeId = useWaveviewStore((s) => s.activeId);
  if (!activeId) return null;
  if (sweepMode === "pvt") return <PvtStrip />;
  if (sweepMode === "mc") return <McStrip />;
  return <SingleStrip />;
}

function StripHeader({ label, route }: { label: string; route: string }) {
  return (
    <div className="mb-1.5 flex items-baseline justify-between">
      <span className="text-[9.5px] font-bold uppercase tracking-[0.08em] text-muted">
        {label}
      </span>
      <span className="font-mono text-[9px] text-faint">{route}</span>
    </div>
  );
}

function SweepNotice({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-md border border-dashed border-border px-3 py-2 text-[11px] text-faint">
      {children}
    </div>
  );
}

function SingleStrip() {
  const measures = useWaveviewStore((s) => s.measures);
  const catalog = useWaveviewStore((s) => s.catalog);
  const summary = useProjectStore((s) => s.summary);

  const chips = perfChips(catalog, measures, summary?.target_specs ?? null);

  const chipFor = (names: string[]) =>
    names.map((n) => chips.find((c) => c.meas === n && c.value != null)).find(Boolean) ??
    names.map((n) => chips.find((c) => c.meas === n)).find(Boolean);

  return (
    <div className="shrink-0 pb-3">
      <StripHeader
        label="Performance · composite of Tier-1 measures"
        route="POST /waveview/datasets/{id}/measure"
      />
      {chips.length === 0 ? (
        <SweepNotice>
          No measurable Tier-1 recipes for this dataset — pick a measure `out` signal in the
          axes panel, or open a dataset with an AC/STB/noise analysis.
        </SweepNotice>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
            {STAT_CARDS.map((card) => {
              const chip = chipFor(card.measures);
              return (
                <Stat
                  key={card.eyebrow}
                  eyebrow={card.eyebrow}
                  value={chip?.value != null ? formatEng(chip.value, chip.unit) : "n/a"}
                  tone={
                    chip?.status === "ok" ? "ok" : chip?.status === "fail" ? "danger" : "default"
                  }
                  progress={chip ? progressFor(chip) : undefined}
                />
              );
            })}
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {chips.map((c) => (
              <SpecChip
                key={c.meas}
                name={c.label}
                value={c.value != null ? formatEng(c.value, c.unit) : "—"}
                target={
                  c.target != null
                    ? `${goalSymbol(c.goal ?? "")} ${formatEng(c.target, c.unit)}`
                    : undefined
                }
                status={c.status === "ok" ? "ok" : c.status === "fail" ? "fail" : "neutral"}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function PvtStrip() {
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepMetrics = useWaveviewStore((s) => s.sweepMetrics);
  const cornerEnabled = useWaveviewStore((s) => s.cornerEnabled);
  const catalog = useWaveviewStore((s) => s.catalog);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const summary = useProjectStore((s) => s.summary);

  const base = activeAnalysis ? baseAnalysis(activeAnalysis) : "";
  const headline = headlineFor(base, catalog);
  const spec = headline ? specForMeas(summary?.target_specs ?? null, headline.meas) : null;
  const corners = cornerResults(sweepMembers, sweepMetrics, cornerEnabled);
  const stats = pvtStats(corners, headline, spec);
  const worst = corners.find((c) => c.key === stats.worstKey) ?? null;

  return (
    <div className="shrink-0 pb-3">
      <StripHeader
        label="PVT · worst-case across corners"
        route="POST /open_run?match=__corner · per-corner /measure"
      />
      {sweepStatus === "loading" ? (
        <SweepNotice>Discovering the run&apos;s corner datasets…</SweepNotice>
      ) : !stats.total || !headline ? (
        <SweepNotice>
          {headline
            ? "No per-corner artifacts in this run — start a corners sweep (PVT config) with keep_raw to compare corners here."
            : "This analysis has no headline Tier-1 measure to rank corners by."}
        </SweepNotice>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
            <Stat
              eyebrow={`worst ${headline.label}`}
              value={worst?.metric != null ? fmtMetric(headline, worst.metric) : "—"}
              tone={
                specStatus(spec, worst?.metric ?? null) === "ok"
                  ? "ok"
                  : specStatus(spec, worst?.metric ?? null) === "fail"
                    ? "danger"
                    : "default"
              }
            />
            <Stat eyebrow="worst corner" value={worst?.name ?? "—"} />
            <Stat
              eyebrow="corners pass"
              value={stats.pass != null ? `${stats.pass} / ${stats.total}` : `${stats.total}`}
              unit={stats.pass != null ? "meet spec" : "no spec to judge"}
              tone={
                stats.pass == null ? "default" : stats.pass === stats.total ? "ok" : "danger"
              }
              progress={stats.pass != null ? stats.pass / stats.total : undefined}
            />
            <Stat
              eyebrow="spread"
              value={stats.spread != null ? `±${fmtMetric(headline, stats.spread)}` : "—"}
            />
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {corners
              .filter((c) => c.enabled)
              .map((c) => (
                <SpecChip
                  key={c.key}
                  name={c.name.split("·")[0]}
                  value={c.metric != null ? fmtMetric(headline, c.metric) : "—"}
                  target={specTarget(spec, headline)}
                  status={specStatus(spec, c.metric)}
                />
              ))}
          </div>
        </>
      )}
    </div>
  );
}

function McStrip() {
  const sweepStatus = useWaveviewStore((s) => s.sweepStatus);
  const sweepMembers = useWaveviewStore((s) => s.sweepMembers);
  const sweepMetrics = useWaveviewStore((s) => s.sweepMetrics);
  const catalog = useWaveviewStore((s) => s.catalog);
  const activeAnalysis = useWaveviewStore((s) => s.activeAnalysis);
  const summary = useProjectStore((s) => s.summary);

  const base = activeAnalysis ? baseAnalysis(activeAnalysis) : "";
  const headline = headlineFor(base, catalog);
  const spec = headline ? specForMeas(summary?.target_specs ?? null, headline.meas) : null;
  const values = sweepMembers
    .map((m) => sweepMetrics[m.key])
    .filter((v): v is number => v != null);
  const stats = mcStats(values, headline, spec);

  return (
    <div className="shrink-0 pb-3">
      <StripHeader
        label={`Monte Carlo${stats ? ` · ${stats.n} samples · yield & Cpk` : ""}`}
        route="per-sample POST /measure"
      />
      {sweepStatus === "loading" ? (
        <SweepNotice>Discovering the run&apos;s sample datasets…</SweepNotice>
      ) : sweepMembers.length === 0 ? (
        <SweepNotice>
          No Monte Carlo samples in this run — launch one from Manual sim (the{" "}
          <span className="font-mono">MC</span> field) or{" "}
          <span className="font-mono">POST /simulate/once {"{monte_carlo: N}"}</span>; its{" "}
          <span className="font-mono">…__mc&lt;n&gt;/</span> artifacts appear here.
        </SweepNotice>
      ) : !stats || !headline ? (
        <SweepNotice>
          {sweepMembers.length} samples loaded, but the headline metric
          {headline ? ` (${headline.label})` : ""} did not measure on this analysis — switch
          to a tab it applies to (e.g. AC Bode for UGF/PM).
        </SweepNotice>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
            <Stat
              eyebrow={`${headline.label} μ`}
              value={fmtMetric(headline, stats.mean)}
              unit={`σ ${fmtMetric(headline, stats.sigma)}`}
              tone={specStatus(spec, stats.mean) === "fail" ? "danger" : "ok"}
            />
            <Stat
              eyebrow="yield"
              value={stats.yield != null ? `${(stats.yield * 100).toFixed(1)}%` : "n/a"}
              unit={stats.yield != null ? `${stats.n} samples` : "no spec to judge"}
              tone={
                stats.yield == null
                  ? "default"
                  : stats.yield >= 0.99
                    ? "ok"
                    : stats.yield >= 0.95
                      ? "warn"
                      : "danger"
              }
              progress={stats.yield ?? undefined}
            />
            <Stat
              eyebrow="Cpk"
              value={stats.cpk != null ? stats.cpk.toFixed(2) : "n/a"}
              unit={
                stats.cpk == null ? "no spec" : stats.cpk >= 1.33 ? "capable" : "marginal"
              }
              tone={
                stats.cpk == null
                  ? "default"
                  : stats.cpk >= 1.33
                    ? "ok"
                    : stats.cpk >= 1
                      ? "warn"
                      : "danger"
              }
              progress={stats.cpk != null ? Math.min(1, stats.cpk / 2) : undefined}
            />
            <Stat
              eyebrow={`worst ${headline.label}`}
              value={fmtMetric(headline, stats.worst)}
              tone={specStatus(spec, stats.worst) === "fail" ? "danger" : "default"}
            />
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <SpecChip
              name={`${headline.meas} μ`}
              value={fmtMetric(headline, stats.mean)}
              target={specTarget(spec, headline)}
              status={specStatus(spec, stats.mean)}
            />
            <SpecChip
              name="μ−3σ"
              value={fmtMetric(headline, stats.mean - 3 * stats.sigma)}
              target={specTarget(spec, headline)}
              status={specStatus(spec, stats.mean - 3 * stats.sigma)}
            />
            <SpecChip
              name="μ+3σ"
              value={fmtMetric(headline, stats.mean + 3 * stats.sigma)}
              target={specTarget(spec, headline)}
              status={specStatus(spec, stats.mean + 3 * stats.sigma)}
            />
            {stats.yield != null && (
              <SpecChip
                name="yield"
                value={`${(stats.yield * 100).toFixed(1)}%`}
                target="≥ 99%"
                status={stats.yield >= 0.99 ? "ok" : stats.yield >= 0.95 ? "neutral" : "fail"}
              />
            )}
            {stats.cpk != null && (
              <SpecChip
                name="Cpk"
                value={stats.cpk.toFixed(2)}
                target="≥ 1.33"
                status={stats.cpk >= 1.33 ? "ok" : stats.cpk >= 1 ? "neutral" : "fail"}
              />
            )}
            <SpecChip
              name="σ"
              value={fmtMetric(headline, stats.sigma)}
              target="—"
              status="neutral"
            />
          </div>
        </>
      )}
    </div>
  );
}
