"use client";
import { useMemo } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useProjectStore } from "@/stores/projectStore";
import { useRunStore } from "@/stores/runStore";
import { useUIStore } from "@/stores/uiStore";
import { EmptyState } from "@/components/ui/empty-state";
import { cn, formatEng, goalSymbol, statusForGoal } from "@/lib/utils";
import { cornerSummary, cornerIncludes } from "@/lib/pvt";

/**
 * Read-only pipeline DAG of the optimization problem, derived entirely from
 * projectStore.summary. Four columns wired left→right:
 *   Optimizer ──▶ DUT params ──▶ Testbenches ──▶ Specs
 * Spec nodes are clickable: they deep-link into Score Shaping (the same
 * uiStore.selectedSpec mechanism the ⌘K "Jump to spec" uses), and show live
 * pass/fail tint from the active run's bestMetrics. Columns are flex stacks +
 * an SVG underlay isn't needed because the left→right ordering reads as flow;
 * connections are implied by the column headers and the testbench grouping.
 */
function Column({ title, count, children }: { title: string; count: number; children: React.ReactNode }) {
  return (
    <div className="flex min-w-[180px] flex-1 flex-col">
      <div className="mb-2 flex items-baseline gap-1.5">
        <span className="text-[11px] font-medium uppercase tracking-wide text-faint">{title}</span>
        <span className="font-mono text-[10px] text-faint">{count}</span>
      </div>
      <div className="flex flex-col gap-1.5">{children}</div>
    </div>
  );
}

function Node({
  title,
  subtitle,
  tone = "default",
  onClick,
  title2,
}: {
  title: string;
  subtitle?: string;
  tone?: "default" | "accent" | "ok" | "fail" | "muted";
  onClick?: () => void;
  title2?: string;
}) {
  const toneCls =
    tone === "accent"
      ? "border-primary/40 bg-primary-soft"
      : tone === "ok"
        ? "border-ok/40 bg-[#f0fdf4]"
        : tone === "fail"
          ? "border-danger/40 bg-danger-soft"
          : tone === "muted"
            ? "border-border bg-hairline opacity-60"
            : "border-border bg-panel";
  const Tag = onClick ? "button" : "div";
  return (
    <Tag
      type={onClick ? "button" : undefined}
      onClick={onClick}
      title={title2}
      className={cn(
        "rounded-md border px-2.5 py-1.5 text-left transition",
        toneCls,
        onClick && "cursor-pointer hover:border-primary hover:shadow-seg",
      )}
    >
      <div className="truncate font-mono text-[12px] text-fg">{title}</div>
      {subtitle && <div className="mt-0.5 truncate font-mono text-[10px] text-muted">{subtitle}</div>}
    </Tag>
  );
}

export function PipelineView() {
  const router = useRouter();
  const { summary, isApplied } = useProjectStore();
  const bestMetrics = useRunStore((s) => s.bestMetrics);
  const setSelectedSpec = useUIStore((s) => s.setSelectedSpec);

  const specsByTb = useMemo(() => {
    const map = new Map<string, number>();
    summary?.target_specs.forEach((s) => map.set(s.testbench, (map.get(s.testbench) ?? 0) + 1));
    return map;
  }, [summary]);

  if (!isApplied || !summary) {
    return (
      <div className="flex-1 p-3">
        <EmptyState bordered minHeight="min-h-60">
          Apply a project to see its optimization pipeline.
        </EmptyState>
      </div>
    );
  }

  const allParams = summary.dut_params;
  const freeCount = allParams.filter((p) => !p.freeze).length;
  const enabledTbs = summary.testbenches.filter((t) => t.enable);

  const pvt = summary.pvt;
  const activeCorner = pvt?.corners.find((c) => c.name === pvt.active_corner) ?? null;

  // Tolerance-aware verdict via the shared helper, so the DAG tint can't disagree
  // with the RightRail / HealthTab (the old inline check ignored tolerance).
  const specVerdict = (specName: string, goal: string, target: number, tol: number | null) =>
    statusForGoal(goal, bestMetrics[specName], target, tol ?? undefined);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-auto p-4">
      <div className="mb-3 text-[12px] text-muted">
        Read-only view of how <span className="font-mono text-fg">{summary.name}</span> is wired:
        the optimizer perturbs the free DUT parameters, each enabled testbench simulates, and the
        target specs score the result. Click a spec to shape its penalty.
      </div>

      {/* PVT corner — a global condition applied to every testbench's netlist before
          simulation. Shown as a banner because it feeds all testbenches at once. */}
      {pvt && activeCorner && (
        <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 rounded-md border border-secondary/40 bg-secondary-soft px-3 py-2 text-[11px]">
          <span className="text-[10px] font-medium uppercase tracking-wide text-secondary">
            PVT corner
          </span>
          <span className="font-mono text-[12px] text-fg">{activeCorner.name}</span>
          <span className="font-mono text-muted">{cornerSummary(activeCorner)}</span>
          <span className="font-mono text-[10px] text-faint" title={cornerIncludes(activeCorner)}>
            {cornerIncludes(activeCorner)}
          </span>
          <span className="ml-auto font-mono text-[10px] text-faint">
            {pvt.corners.length} corner(s) defined · applied to all {enabledTbs.length} testbench(es)
          </span>
        </div>
      )}

      <div className="flex items-stretch gap-3">
        {/* Optimizer */}
        <Column title="Optimizer" count={1}>
          <Node
            title={summary.optimizer.name}
            subtitle={`budget ${summary.optimizer.budget}`}
            tone="accent"
            title2={`${summary.optimizer.type} · seed ${summary.optimizer.random_seed ?? "—"}`}
          />
        </Column>

        <Arrow />

        {/* DUT params — show all; frozen ones dimmed (they're not optimized but
            are still part of the design, so hiding them misreads as "empty"). */}
        <Column title={`DUT params · ${freeCount} free`} count={allParams.length}>
          {allParams.length === 0 ? (
            <Node title="—" subtitle="none defined" />
          ) : (
            allParams.map((p) => (
              <Node
                key={p.name}
                title={p.name}
                subtitle={
                  p.freeze
                    ? "frozen"
                    : `${formatEng(p.min_val ?? 0)}…${formatEng(p.max_val ?? 0)}${p.log_scale ? " (log)" : ""}`
                }
                tone={p.freeze ? "muted" : "default"}
                title2={p.freeze ? "frozen (not optimized)" : p.is_integer ? "integer" : "continuous"}
              />
            ))
          )}
        </Column>

        <Arrow />

        {/* Testbenches */}
        <Column title="Testbenches" count={enabledTbs.length}>
          {enabledTbs.map((t) => (
            <Node
              key={t.name}
              title={t.name}
              subtitle={`${specsByTb.get(t.name) ?? 0} spec(s)`}
              title2={t.netlist}
            />
          ))}
        </Column>

        <Arrow />

        {/* Specs */}
        <Column title="Target specs" count={summary.target_specs.length}>
          {summary.target_specs.map((s) => {
            const verdict = specVerdict(s.name, s.goal, s.target, s.tolerance);
            const v = bestMetrics[s.name];
            return (
              <Node
                key={s.name}
                title={s.name}
                subtitle={`${goalSymbol(s.goal)} ${formatEng(s.target)}${s.enable ? (v != null ? ` · now ${formatEng(v)}` : "") : " · disabled"}`}
                tone={verdict === "unknown" ? "default" : verdict === "pass" ? "ok" : "fail"}
                title2={s.enable ? "Open in Score Shaping" : "Disabled — not in the objective"}
                onClick={
                  s.enable
                    ? () => {
                        setSelectedSpec(s.name);
                        router.push("/scoring" as Route);
                      }
                    : undefined
                }
              />
            );
          })}
        </Column>
      </div>
    </div>
  );
}

function Arrow() {
  return (
    <div className="flex items-center pt-7 text-faint" aria-hidden>
      <svg width="20" height="12" viewBox="0 0 20 12">
        <path d="M0 6 H16 M12 2 L16 6 L12 10" fill="none" stroke="currentColor" strokeWidth="1.3" />
      </svg>
    </div>
  );
}
