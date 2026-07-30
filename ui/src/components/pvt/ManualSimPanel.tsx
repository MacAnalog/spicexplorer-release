"use client";
import { useEffect, useMemo, useState } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useProjectStore } from "@/stores/projectStore";
import { useUIStore } from "@/stores/uiStore";
import { useWaveviewStore } from "@/stores/waveviewStore";
import { api } from "@/lib/api";
import { formatEng, statusForGoal } from "@/lib/utils";
import { Panel, PanelBody, PanelHeader } from "@/components/ui/panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Stat } from "@/components/ui/stat";
import { EmptyState } from "@/components/ui/empty-state";
import { Segmented } from "@/components/ui/segmented";
import { Thead, Th, Tr, Td } from "@/components/ui/table";
import { selectCn } from "@/components/ui/select";
import { CornerSelect } from "@/components/pvt/CornerSelect";
import type { CheckpointMeta, SimulateOnceResponse } from "@/types/api";

type Mode = "manual" | "checkpoint";

/**
 * Manual Sim / Evaluate Point — run all enabled testbenches ONCE for a chosen
 * design vector and show metrics + score, using the same evaluate() primitive a
 * real trial uses (so results are directly comparable to checkpoint rows).
 *
 *  • Manual entry — a numeric form pre-filled from each dut_param's init/val.
 *  • From checkpoint — replay a stored point's vector (best, or a given index).
 *
 * PDK-gated (needs live SPICE), like the live Start button. The synchronous call
 * blocks; a spinner + elapsed time cover it.
 */
export function ManualSimPanel() {
  const router = useRouter();
  const { summary, yamlPath, isApplied, projectId } = useProjectStore();
  const env = useUIStore((s) => s.env);
  const openRunInViewer = useWaveviewStore((s) => s.openRun);

  const dutParams = useMemo(() => summary?.dut_params ?? [], [summary]);
  const specs = useMemo(() => summary?.target_specs ?? [], [summary]);
  const pvt = summary?.pvt ?? null;

  const [mode, setMode] = useState<Mode>("manual");
  const [values, setValues] = useState<Record<string, string>>({});
  const [corner, setCorner] = useState<string | null>(null);
  const [checkpointId, setCheckpointId] = useState<string>("");
  const [pointIdx, setPointIdx] = useState<string>(""); // "" = best point
  const [checkpoints, setCheckpoints] = useState<CheckpointMeta[]>([]);

  const [busy, setBusy] = useState(false);
  const [keepRaw, setKeepRaw] = useState(false);
  // Corners sweep — run testbenches × EVERY enabled corner in one sim (the
  // launch-time PVT lane; Analyze's "PVT corners" mode reads the artifacts).
  const [sweepCorners, setSweepCorners] = useState(false);
  // Monte Carlo — N statistical samples of the selected corner (mismatch model
  // sections + per-sample seed; Analyze's "Monte Carlo" mode reads the
  // __mc<i> artifacts). Blank = off. Mutually exclusive with the corners sweep.
  const [mcSamples, setMcSamples] = useState("");
  // keep_raw as SENT with the sim that produced `result` — the live checkbox can
  // be retoggled afterwards and must not fabricate/hide the open-in-Analyze button.
  const [ranKeepRaw, setRanKeepRaw] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SimulateOnceResponse | null>(null);
  const [showLogs, setShowLogs] = useState(false);

  // Seed the manual form from init (fallback val) whenever the project changes.
  const initDefaults = useMemo(() => {
    const out: Record<string, string> = {};
    for (const p of dutParams) {
      const seed = p.init ?? p.val;
      out[p.name] = seed != null ? String(seed) : "";
    }
    return out;
  }, [dutParams]);

  useEffect(() => setValues(initDefaults), [initDefaults]);

  // Checkpoint list for Mode A (best-effort; empty list just disables the mode),
  // scoped to the active project.
  useEffect(() => {
    let alive = true;
    api
      .listCheckpoints(projectId ?? undefined)
      .then((cks) => alive && setCheckpoints(cks))
      .catch(() => alive && setCheckpoints([]));
    return () => {
      alive = false;
    };
  }, [projectId]);

  const pdkMissing = env != null && !env.live_runs_enabled;
  const canSimulate =
    isApplied &&
    !pdkMissing &&
    !busy &&
    (mode === "manual" ? Object.values(values).some((v) => v.trim() !== "") : !!checkpointId);

  const runSim = async () => {
    setBusy(true);
    setError(null);
    setResult(null);
    setRanKeepRaw(keepRaw);
    try {
      const mcN = mcSamples.trim() === "" ? undefined : Number(mcSamples);
      const body: Parameters<typeof api.simulateOnce>[0] = {
        yaml_path: yamlPath,
        // With MC the corner select picks the BASE corner to perturb.
        active_corner: sweepCorners ? undefined : (corner ?? undefined),
        sweep_corners: (sweepCorners && mcN === undefined) || undefined,
        monte_carlo: mcN,
        keep_raw: keepRaw || undefined,
      };
      if (mode === "manual") {
        // Send raw strings; the backend parses engineering values ("250u", "0.18u")
        // via parse_value, so we don't coerce (and don't reject) here.
        const params: Record<string, string> = {};
        for (const [k, v] of Object.entries(values)) {
          if (v.trim() === "") continue;
          params[k] = v.trim();
        }
        body.params = params;
      } else {
        body.checkpoint_id = checkpointId;
        if (pointIdx.trim() !== "") body.point = Number(pointIdx);
      }
      const res = await api.simulateOnce(body);
      setResult(res);
      if (!res.ok) setError(res.error ?? "Simulation failed");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setBusy(false);
    }
  };

  const specByName = useMemo(
    () => Object.fromEntries(specs.map((s) => [s.name, s])),
    [specs],
  );

  // Standalone-view guard: deep-linking to /manual without an applied project
  // shows the empty state rather than a bare control row with no params.
  if (!isApplied || !summary) {
    return (
      <EmptyState bordered minHeight="min-h-60">
        Apply a project first to evaluate a design point.
      </EmptyState>
    );
  }

  return (
    <Panel>
      <PanelHeader
        title="Manual sim · evaluate a point"
        mute="· one shot, all enabled testbenches"
        right={
          result?.active_corner ? (
            <Badge variant="cyan">corner: {result.active_corner}</Badge>
          ) : null
        }
      />
      <PanelBody className="flex flex-col gap-3">
        {/* controls */}
        <div className="flex flex-wrap items-center gap-2">
          <Segmented<Mode>
            value={mode}
            onChange={setMode}
            options={[
              { value: "manual", label: "Manual entry" },
              { value: "checkpoint", label: "From checkpoint" },
            ]}
          />
          {pvt && pvt.corners.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                corner
              </span>
              <div className="w-[230px]">
                <CornerSelect
                  corners={pvt.corners}
                  value={corner}
                  defaultCorner={pvt.active_corner}
                  onChange={setCorner}
                  size="xs"
                  disabled={sweepCorners}
                  aria-label="PVT corner for this manual sim"
                />
              </div>
              <label
                className="flex cursor-pointer items-center gap-1.5 text-[11px] text-muted"
                title="Run testbenches × every enabled corner in one sim — with keep .raw, Analyze's PVT mode reads the per-corner artifacts"
              >
                <input
                  type="checkbox"
                  checked={sweepCorners}
                  disabled={mcSamples.trim() !== ""}
                  onChange={(e) => setSweepCorners(e.target.checked)}
                  className="accent-primary"
                />
                sweep all {pvt.corners.filter((c) => c.enabled !== false).length}
              </label>
              <label
                className="flex items-center gap-1.5 text-[11px] text-muted"
                title="Monte Carlo: N statistical samples of the selected corner (mismatch model sections + per-sample RNG seed) — with keep .raw, Analyze's Monte Carlo mode reads the __mc artifacts"
              >
                MC
                <input
                  type="number"
                  min={2}
                  max={100}
                  placeholder="off"
                  value={mcSamples}
                  disabled={sweepCorners}
                  onChange={(e) => setMcSamples(e.target.value)}
                  className={selectCn("xs") + " w-[52px]"}
                  aria-label="Monte Carlo sample count (blank = off)"
                />
              </label>
            </div>
          )}
          <div className="ml-auto flex items-center gap-2.5">
            <label
              className="flex cursor-pointer items-center gap-1.5 text-[11px] text-muted"
              title="Retain the sim's .raw files so the run opens in the Analyze waveform viewer"
            >
              <input
                type="checkbox"
                checked={keepRaw}
                onChange={(e) => setKeepRaw(e.target.checked)}
                className="accent-primary"
              />
              keep <span className="font-mono">.raw</span>
            </label>
            <Button
              variant="primary"
              onClick={runSim}
              disabled={!canSimulate}
              title={
                pdkMissing
                  ? "Manual sim needs live SPICE (the IHP PDK isn't installed on this machine)."
                  : undefined
              }
            >
              {busy ? "Simulating…" : "Simulate"}
            </Button>
          </div>
        </div>

        {pdkMissing && (
          <div className="rounded-sm border border-warn-soft bg-warn-soft px-2.5 py-1.5 text-[11px] text-[#b45309]">
            PDK missing — manual sim is disabled (it runs real SPICE). Replay/compare on
            cached checkpoints still works.
          </div>
        )}

        {/* Mode B: checkpoint picker */}
        {mode === "checkpoint" && (
          <div className="flex flex-wrap items-end gap-2">
            <label className="flex flex-col gap-1">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                checkpoint
              </span>
              <select
                aria-label="Checkpoint to evaluate"
                value={checkpointId}
                onChange={(e) => setCheckpointId(e.target.value)}
                className={selectCn("sm") + " w-[260px]"}
              >
                <option value="">— select a checkpoint —</option>
                {checkpoints.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
                point index
              </span>
              <input
                aria-label="Checkpoint point index (blank = best)"
                type="number"
                min={0}
                placeholder="best"
                value={pointIdx}
                onChange={(e) => setPointIdx(e.target.value)}
                className={selectCn("sm") + " w-[90px]"}
              />
            </label>
            <span className="pb-1.5 text-[11px] text-faint">
              Blank index → best point (re-sim should reproduce its stored metrics).
            </span>
          </div>
        )}

        {/* Mode A: manual param table */}
        {mode === "manual" && dutParams.length > 0 && (
          <div className="max-h-[230px] overflow-auto rounded-sm border border-border">
            <table className="w-full border-collapse text-xs">
              <Thead>
                <Th>param</Th>
                <Th className="text-right">value</Th>
                <Th className="text-right">min</Th>
                <Th className="text-right">max</Th>
              </Thead>
              <tbody>
                {dutParams.map((p) => (
                  <Tr key={p.name}>
                    <Td className="font-mono text-[11px]">{p.name}</Td>
                    <Td className="text-right">
                      <input
                        aria-label={`Value for ${p.name}`}
                        type="text"
                        inputMode="text"
                        placeholder="e.g. 250u"
                        value={values[p.name] ?? ""}
                        onChange={(e) =>
                          setValues((v) => ({ ...v, [p.name]: e.target.value }))
                        }
                        className={selectCn("xs") + " w-[120px] text-right"}
                      />
                    </Td>
                    <Td className="text-right font-mono text-[10px] text-faint">
                      {p.min_val != null ? formatEng(p.min_val) : "—"}
                    </Td>
                    <Td className="text-right font-mono text-[10px] text-faint">
                      {p.max_val != null ? formatEng(p.max_val) : "—"}
                    </Td>
                  </Tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {mode === "manual" && dutParams.length > 0 && (
          <div>
            <button
              type="button"
              onClick={() => setValues(initDefaults)}
              className="text-[11px] text-primary hover:underline"
            >
              Reset to init
            </button>
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-sm border border-danger bg-danger-soft px-2.5 py-1.5 text-[11px] text-danger"
          >
            {error}
          </div>
        )}

        {/* result */}
        {result?.ok && (
          <div className="flex flex-col gap-2.5">
            <div className="flex flex-wrap items-center gap-2">
              <Stat
                eyebrow="total score"
                value={result.score != null ? result.score.toFixed(4) : "n/a"}
                className="min-w-[140px]"
              />
              {result.elapsed_ms != null && (
                <span className="text-[11px] text-faint">
                  {(result.elapsed_ms / 1000).toFixed(2)}s
                </span>
              )}
              {result.run_id && ranKeepRaw && (
                <Button
                  variant="secondary"
                  onClick={() => {
                    const runId = result.run_id;
                    if (!runId) return;
                    void openRunInViewer(runId, projectId ?? undefined).then((ok) => {
                      if (ok) router.push("/analyze" as Route);
                      else
                        setError(
                          "This run has no openable waveforms — its raw files may have been cleaned.",
                        );
                    });
                  }}
                >
                  ∿ Open waveforms in Analyze
                </Button>
              )}
            </div>

            {result.warnings.length > 0 && (
              <ul className="rounded-sm border border-warn-soft bg-warn-soft px-2.5 py-1.5 text-[11px] text-[#b45309]">
                {result.warnings.map((w, i) => (
                  <li key={i}>• {w}</li>
                ))}
              </ul>
            )}

            <div className="overflow-auto rounded-sm border border-border">
              <table className="w-full border-collapse text-xs">
                <Thead>
                  <Th>spec</Th>
                  <Th className="text-right">value</Th>
                  <Th className="text-right">target</Th>
                  <Th>goal</Th>
                  <Th className="text-right">score</Th>
                  <Th className="text-center">status</Th>
                </Thead>
                <tbody>
                  {Object.entries(result.metrics).map(([name, m]) => {
                    const spec = specByName[name];
                    const status = spec
                      ? statusForGoal(spec.goal, m.curr_val, spec.target, spec.tolerance ?? undefined)
                      : "unknown";
                    return (
                      <Tr key={name}>
                        <Td className="font-mono text-[11px]">{name}</Td>
                        <Td className="text-right font-mono">{formatEng(m.curr_val)}</Td>
                        <Td className="text-right font-mono text-faint">
                          {spec ? formatEng(spec.target) : "—"}
                        </Td>
                        <Td className="text-muted">{spec?.goal ?? "—"}</Td>
                        <Td className="text-right font-mono text-faint">
                          {m.score != null ? m.score.toFixed(3) : "—"}
                        </Td>
                        <Td className="text-center">
                          {status === "pass" ? (
                            <Badge variant="pass">pass</Badge>
                          ) : status === "fail" ? (
                            <Badge variant="fail">fail</Badge>
                          ) : (
                            <Badge variant="neutral">—</Badge>
                          )}
                        </Td>
                      </Tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {Object.keys(result.log_tails).length > 0 && (
              <div>
                <button
                  type="button"
                  onClick={() => setShowLogs((v) => !v)}
                  className="text-[11px] text-primary hover:underline"
                >
                  {showLogs ? "Hide" : "Show"} per-testbench log tails
                </button>
                {showLogs && (
                  <div className="mt-1.5 flex flex-col gap-2">
                    {Object.entries(result.log_tails).map(([tb, tail]) => (
                      <div key={tb}>
                        <div className="mb-0.5 font-mono text-[10px] text-muted">{tb}</div>
                        <pre className="max-h-[160px] overflow-auto rounded-sm border border-border bg-hairline px-2 py-1 text-[10px] leading-snug text-fg">
                          {tail || "(empty)"}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </PanelBody>
    </Panel>
  );
}
