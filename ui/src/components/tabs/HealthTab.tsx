"use client";
import { useState } from "react";
import { FlaskConical, Loader2, FileText } from "lucide-react";
import { Panel, PanelBody, PanelHeader } from "@/components/ui/panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Thead, Th, Tr, Td } from "@/components/ui/table";
import { EmptyState } from "@/components/ui/empty-state";
import { Toolbar, ToolbarLabel, ToolbarSpacer } from "@/components/shell/Toolbar";
import { CornerSelect } from "@/components/pvt/CornerSelect";
import { useProjectStore } from "@/stores/projectStore";
import { api } from "@/lib/api";
import { goalSymbol, statusForGoal } from "@/lib/utils";
import type { SanityCheckResponse, TargetSpec } from "@/types/api";

function passesSpec(s: TargetSpec, val: number | undefined | null): boolean | null {
  if (val == null) return null;
  return statusForGoal(s.goal, val, s.target, s.tolerance ?? undefined) === "pass";
}

function fmtMs(ms: number | null | undefined): string {
  if (ms == null || !Number.isFinite(ms)) return "—";
  if (ms < 1000) return `${ms.toFixed(0)} ms`;
  const s = ms / 1000;
  if (s < 60) return `${s.toFixed(2)} s`;
  const m = Math.floor(s / 60);
  return `${m}m ${Math.round(s - m * 60)}s`;
}

function fmtBytes(bytes: number | null | undefined): string {
  if (bytes == null) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function HealthTab() {
  const { summary, yamlPath, isApplied } = useProjectStore();
  const [result, setResult] = useState<SanityCheckResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [corner, setCorner] = useState<string | null>(null);

  const enabledSpecs = summary?.target_specs.filter((s) => s.enable) ?? [];
  const pvt = summary?.pvt ?? null;

  const handleRun = async () => {
    if (!yamlPath) return;
    setResult(null);
    setError(null);
    setRunning(true);
    try {
      const res = await api.sanityCheck(yamlPath, corner ?? undefined);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Health check failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <>
      <Toolbar>
        <ToolbarLabel>health check</ToolbarLabel>
        <span className="font-mono text-[11px] text-muted">
          1 SPICE sim per testbench · 1 trial optimizer step
        </span>
        {pvt && pvt.corners.length > 0 && (
          <>
            <ToolbarLabel>corner</ToolbarLabel>
            <div className="w-[210px]">
              <CornerSelect
                corners={pvt.corners}
                value={corner}
                defaultCorner={pvt.active_corner}
                onChange={setCorner}
                disabled={running}
                aria-label="PVT corner for the trial step"
              />
            </div>
          </>
        )}
        <ToolbarSpacer />
        <Button variant="primary" onClick={handleRun} disabled={running || !isApplied}>
          {running ? (
            <>
              <Loader2 className="h-3 w-3 animate-spin" /> Running…
            </>
          ) : (
            <>
              <FlaskConical className="h-3 w-3" /> Run health check
            </>
          )}
        </Button>
      </Toolbar>

      {/* *:shrink-0 — Panels (overflow-hidden ⇒ flex auto-min-size 0) would
          otherwise be crushed to fit and clip their content (trial sim log tails)
          instead of letting this container scroll. */}
      <div className="flex min-h-0 flex-1 flex-col gap-2.5 overflow-auto p-3 *:shrink-0">
        {!isApplied && (
          <EmptyState bordered minHeight="min-h-32">
            Apply a project on the Setup tab to enable the health check.
          </EmptyState>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-md border border-danger bg-danger-soft px-3 py-2 text-xs text-danger"
          >
            {error}
          </div>
        )}

        {isApplied && !result && !error && !running && (
          <Panel>
            <PanelBody>
              <p className="text-[11px] text-muted">
                Runs one SPICE simulation per enabled testbench, then a single
                trial optimization step. Use this before kicking off a full
                optimization to confirm the pipeline (netlists, parameters,
                ngspice, scoring) is working end-to-end.
              </p>
            </PanelBody>
          </Panel>
        )}

        {running && (
          <Panel>
            <PanelBody>
              <p className="flex items-center gap-2 text-[11px] text-muted">
                <Loader2 className="h-3 w-3 animate-spin" />
                Running SPICE simulations — this may take a moment.
              </p>
            </PanelBody>
          </Panel>
        )}

        {result && (
          <>
            {/* Overall status panel */}
            <Panel>
              <PanelHeader
                title="overall status"
                right={
                  result.elapsed_ms_total != null && (
                    <span className="font-mono text-[10px] text-muted">
                      total {fmtMs(result.elapsed_ms_total)}
                    </span>
                  )
                }
              />
              <PanelBody>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={result.ok ? "ok" : "fail"} dot>
                    {result.ok ? "all checks passed" : "one or more checks failed"}
                  </Badge>
                  {result.active_corner && (
                    <Badge variant="cyan">corner: {result.active_corner}</Badge>
                  )}
                  {result.elapsed_ms_load != null && (
                    <span className="font-mono text-[10px] text-muted">
                      YAML load {fmtMs(result.elapsed_ms_load)}
                    </span>
                  )}
                  {result.elapsed_ms_optimizer_init != null && (
                    <span className="font-mono text-[10px] text-muted">
                      · optimizer init {fmtMs(result.elapsed_ms_optimizer_init)}
                    </span>
                  )}
                  {result.ngspice_path && (
                    <span className="font-mono text-[10px] text-muted">
                      · {result.ngspice_path}
                    </span>
                  )}
                  {result.pdk_ok === false && (
                    <span className="rounded-sm bg-warn-soft px-1.5 py-0.5 font-mono text-[10px] text-[#b45309]">
                      PDK missing — replay only
                      {result.pdk_detail ? ` · ${result.pdk_detail}` : ""}
                    </span>
                  )}
                </div>
                {result.error && (
                  <p className="mt-2 rounded-sm bg-danger-soft px-2 py-1 font-mono text-[11px] text-danger">
                    {result.error}
                  </p>
                )}
              </PanelBody>
            </Panel>

            {/* Testbenches panel */}
            {result.testbenches.length > 0 && (
              <Panel>
                <PanelHeader
                  title="testbenches"
                  mute={`· ${result.testbenches.length}`}
                />
                <PanelBody className="space-y-1.5">
                  {result.testbenches.map((tb) => (
                    <div
                      key={tb.name}
                      className="rounded-sm border border-border bg-hairline/40"
                    >
                      <div className="flex flex-wrap items-center gap-2 px-2 py-1.5">
                        <Badge variant={tb.ok ? "ok" : "fail"} dot>
                          {tb.ok ? "ok" : "fail"}
                        </Badge>
                        <span className="font-mono text-[11px]">{tb.name}</span>
                        {tb.elapsed_ms != null && (
                          <span className="font-mono text-[10px] text-muted">
                            {fmtMs(tb.elapsed_ms)}
                          </span>
                        )}
                        {tb.log_size_bytes != null && (
                          <span className="font-mono text-[10px] text-faint">
                            · {fmtBytes(tb.log_size_bytes)} log
                          </span>
                        )}
                      </div>
                      {tb.error && (
                        <p className="px-2 pb-1.5 text-[11px] text-danger">
                          {tb.error}
                        </p>
                      )}
                      {tb.log_tail && (
                        <details className="border-t border-border px-2 py-1 text-[11px]">
                          <summary className="cursor-pointer text-muted hover:text-fg">
                            <FileText className="mr-1 inline h-3 w-3" />
                            ngspice log tail
                            {tb.log_path && (
                              <span className="ml-1 font-mono text-[10px] text-faint">
                                {tb.log_path}
                              </span>
                            )}
                          </summary>
                          <pre className="mt-1 max-h-60 overflow-auto rounded-sm bg-[#1c1c1f] p-2 font-mono text-[10px] leading-tight text-zinc-100">
                            {tb.log_tail}
                          </pre>
                        </details>
                      )}
                    </div>
                  ))}
                </PanelBody>
              </Panel>
            )}

            {/* Trial evaluation panel */}
            {result.trial && (
              <Panel>
                <PanelHeader
                  title="trial evaluation"
                  mute="· 1 iteration"
                  right={
                    result.trial.elapsed_ms != null && (
                      <span className="font-mono text-[10px] text-muted">
                        {fmtMs(result.trial.elapsed_ms)}
                      </span>
                    )
                  }
                />
                <PanelBody className="space-y-2">
                  {result.trial.error ? (
                    <p className="rounded-sm bg-danger-soft px-2 py-1 font-mono text-[11px] text-danger">
                      {result.trial.error}
                    </p>
                  ) : (
                    <>
                      {result.trial.score != null && (
                        <p className="text-[11px] text-muted">
                          Score:{" "}
                          <span className="font-mono font-medium text-fg">
                            {result.trial.score.toFixed(4)}
                          </span>
                        </p>
                      )}
                      {Object.keys(result.trial.metrics).length > 0 && (
                        <table className="w-full">
                          <Thead>
                            <Th>metric</Th>
                            <Th>simulated</Th>
                            <Th>target</Th>
                            <Th>status</Th>
                          </Thead>
                          <tbody>
                            {enabledSpecs.map((spec) => {
                              const val = result.trial!.metrics[spec.name];
                              if (val == null) return null;
                              const p = passesSpec(spec, val);
                              return (
                                <Tr key={spec.name}>
                                  <Td className="font-mono">{spec.name}</Td>
                                  <Td className="font-mono">{val.toPrecision(4)}</Td>
                                  <Td className="font-mono text-muted">
                                    {goalSymbol(spec.goal)} {spec.target}
                                  </Td>
                                  <Td>
                                    {p === null ? (
                                      <Badge variant="neutral">—</Badge>
                                    ) : (
                                      <Badge variant={p ? "ok" : "fail"} dot>
                                        {p ? "pass" : "fail"}
                                      </Badge>
                                    )}
                                  </Td>
                                </Tr>
                              );
                            })}
                          </tbody>
                        </table>
                      )}
                      {Object.keys(result.trial.log_tails || {}).length > 0 && (
                        <div className="space-y-1 pt-1">
                          <p className="text-[10px] font-medium uppercase tracking-wider text-muted">
                            Trial sim logs
                          </p>
                          {Object.entries(result.trial.log_tails).map(([name, tail]) => (
                            <details
                              key={name}
                              className="rounded-sm border border-border bg-hairline/40 px-2 py-1 text-[11px]"
                            >
                              <summary className="cursor-pointer text-muted hover:text-fg">
                                <FileText className="mr-1 inline h-3 w-3" />
                                <span className="font-mono">{name}</span>
                                {result.trial!.log_files[name] && (
                                  <span className="ml-1 font-mono text-[10px] text-faint">
                                    {result.trial!.log_files[name]}
                                  </span>
                                )}
                              </summary>
                              <pre className="mt-1 max-h-60 overflow-auto rounded-sm bg-[#1c1c1f] p-2 font-mono text-[10px] leading-tight text-zinc-100">
                                {tail}
                              </pre>
                            </details>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </PanelBody>
              </Panel>
            )}
          </>
        )}
      </div>
    </>
  );
}
