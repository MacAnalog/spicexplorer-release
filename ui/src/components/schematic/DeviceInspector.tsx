"use client";
import { useEffect, useMemo, useState } from "react";
import { useProjectStore } from "@/stores/projectStore";
import { useUIStore } from "@/stores/uiStore";
import { api } from "@/lib/api";
import { formatEng, goalSymbol } from "@/lib/utils";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Segmented } from "@/components/ui/segmented";
import { selectCn } from "@/components/ui/select";
import { SensitivityChart } from "@/components/charts/SensitivityChart";
import { parseDeviceKind } from "@/lib/params";
import type { DutParam, SensitivityResponse } from "@/types/api";

type Scope = "device" | "all";

/** Default operating point, matching the backend `_nominal`: prefer an explicit
 *  val/init, else the range centre. */
function midpoint(p: DutParam): number {
  if (p.val != null && Number.isFinite(p.val)) return p.val;
  if (p.init != null && Number.isFinite(p.init)) return p.init;
  const lo = p.min_val ?? 0;
  const hi = p.max_val ?? 1;
  if (p.is_integer) return Math.round((lo + hi) / 2);
  if (p.log_scale && lo > 0 && hi > 0) return Math.sqrt(lo * hi);
  return 0.5 * (lo + hi);
}

const KIND_UNIT: Record<string, string> = { W: "m", L: "m", bias: "V", NG: "", other: "" };

/**
 * Device inspector — finite-difference sensitivity of a target spec to DUT
 * parameters. Driven by the applied project's `dut_params` (grouped by device),
 * not the xschem instances, so it works regardless of how the schematic is
 * browsed. The W/L sliders set the operating point sent to the backend as `at`,
 * so the sensitivity is computed at the design point on screen. Needs live SPICE.
 */
export function DeviceInspector() {
  const { summary, yamlPath, isApplied } = useProjectStore();
  const env = useUIStore((s) => s.env);

  const dutParams = useMemo(() => summary?.dut_params ?? [], [summary]);
  const specs = useMemo(
    () => (summary?.target_specs ?? []).filter((s) => s.enable),
    [summary],
  );

  // device id -> its params, in declaration order.
  const devices = useMemo(() => {
    const map = new Map<string, DutParam[]>();
    for (const p of dutParams) {
      const { device } = parseDeviceKind(p.name);
      if (!map.has(device)) map.set(device, []);
      map.get(device)!.push(p);
    }
    return map;
  }, [dutParams]);
  const deviceIds = useMemo(() => Array.from(devices.keys()), [devices]);

  const [spec, setSpec] = useState<string>("");
  const [device, setDevice] = useState<string>("");
  const [scope, setScope] = useState<Scope>("device");
  // Persistent operating-point overrides across device switches (absolute SI).
  const [at, setAt] = useState<Record<string, number>>({});
  const [result, setResult] = useState<SensitivityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset all inspector state when the applied project changes — otherwise the
  // selected spec/device and the `at` operating-point overrides keep keys from
  // the previous project, which the backend would reject as unknown params.
  const projectSig = useMemo(
    () => (summary ? `${summary.name}|${dutParams.map((p) => p.name).join(",")}` : ""),
    [summary, dutParams],
  );
  useEffect(() => {
    setSpec("");
    setDevice("");
    setAt({});
    setResult(null);
    setError(null);
  }, [projectSig]);

  // Default selections once the project is known.
  const effSpec = spec || specs[0]?.name || "";
  const effDevice = device || deviceIds[0] || "";
  const deviceParams = devices.get(effDevice) ?? [];

  const liveDisabled = env != null && !env.live_runs_enabled;
  const valueAt = (p: DutParam) => at[p.name] ?? midpoint(p);

  const compute = async () => {
    if (!effSpec) return;
    setLoading(true);
    setError(null);
    try {
      const deviceNames = deviceParams.map((p) => p.name);
      const params = scope === "device" ? deviceNames : undefined;
      // Only send overrides for the params on screen, so the computed baseline
      // matches the visible sliders (and never leaks stale keys from another
      // device). "All params" sweeps at the range midpoint, so it sends none.
      const atPayload =
        scope === "device"
          ? Object.fromEntries(deviceNames.filter((n) => n in at).map((n) => [n, at[n]]))
          : {};
      const res = await api.specSensitivity(effSpec, {
        yaml_path: yamlPath || undefined,
        params,
        at: atPayload,
        rel_delta: 0.05,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sensitivity failed");
    } finally {
      setLoading(false);
    }
  };

  if (!isApplied || dutParams.length === 0) {
    return (
      <div className="p-3 text-[11px] leading-snug text-faint">
        Apply a project with DUT parameters to inspect device sensitivity.
      </div>
    );
  }

  const goalSym = goalSymbol(result?.goal ?? "");

  return (
    <div className="flex h-full min-h-0 flex-col overflow-y-auto p-3 text-xs">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-fg">
        Device inspector
      </div>

      <label className="mb-2 flex flex-col gap-1">
        <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
          sensitivity of spec
        </span>
        <select
          aria-label="Target spec"
          value={effSpec}
          onChange={(e) => {
            setSpec(e.target.value);
            setResult(null);
          }}
          className={selectCn("sm") + " w-full"}
        >
          {specs.map((s) => (
            <option key={s.name} value={s.name}>
              {s.name} ({s.goal} {formatEng(s.target)})
            </option>
          ))}
        </select>
      </label>

      <div className="mb-2">
        <Segmented<Scope>
          value={scope}
          onChange={setScope}
          options={[
            { value: "device", label: "This device" },
            { value: "all", label: "All params" },
          ]}
        />
      </div>

      {scope === "device" && (
        <>
          <label className="mb-2 flex flex-col gap-1">
            <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
              device
            </span>
            <select
              aria-label="Device"
              value={effDevice}
              onChange={(e) => setDevice(e.target.value)}
              className={selectCn("sm") + " w-full"}
            >
              {deviceIds.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </label>

          <div className="mb-2 flex flex-col gap-2.5 rounded-sm border border-border p-2">
            {deviceParams.map((p) => {
              const { kind } = parseDeviceKind(p.name);
              const lo = p.min_val ?? 0;
              const hi = p.max_val ?? 1;
              const v = valueAt(p);
              const step = p.is_integer ? 1 : (hi - lo) / 200 || undefined;
              const unit = KIND_UNIT[kind] ?? "";
              return (
                <div key={p.name}>
                  <div className="mb-0.5 flex items-center justify-between">
                    <span className="font-mono text-[10px] text-muted">{kind}</span>
                    <span className="font-mono text-[11px] text-fg">
                      {formatEng(v, unit)}
                    </span>
                  </div>
                  <Slider
                    value={v}
                    min={lo}
                    max={hi}
                    step={step}
                    onChange={(nv) => setAt((a) => ({ ...a, [p.name]: nv }))}
                  />
                </div>
              );
            })}
            <button
              type="button"
              onClick={() =>
                setAt((a) => {
                  const next = { ...a };
                  for (const p of deviceParams) delete next[p.name];
                  return next;
                })
              }
              className="self-start text-[10px] text-muted hover:text-fg"
            >
              reset to nominal
            </button>
          </div>
        </>
      )}

      {scope === "all" && (
        <p className="mb-2 text-[11px] leading-snug text-faint">
          Sweeps all {dutParams.length} DUT params at their range midpoint
          (~{dutParams.length + 1} sims, slower).
        </p>
      )}

      <Button
        variant="primary"
        onClick={compute}
        disabled={loading || liveDisabled || !effSpec}
        title={
          liveDisabled
            ? "Sensitivity needs live SPICE (the IHP PDK), which isn't available here."
            : undefined
        }
      >
        {loading ? "Computing…" : "Compute sensitivity"}
      </Button>
      {liveDisabled && (
        <p className="mt-1.5 text-[10px] leading-snug text-[#b45309]">
          PDK missing — sensitivity needs live simulation.
        </p>
      )}
      {error && (
        <div
          role="alert"
          className="mt-2 rounded-sm border border-danger bg-danger-soft px-2 py-1.5 text-[11px] text-danger"
        >
          {error}
        </div>
      )}

      {result && (
        <div className="mt-3">
          <div className="mb-1.5 flex items-center justify-between">
            <span className="font-mono text-[11px] text-fg">
              {result.spec} = {formatEng(result.baseline_value)}
            </span>
            <span className="font-mono text-[10px] text-muted">
              target {goalSym} {formatEng(result.target)}
            </span>
          </div>
          <SensitivityChart params={result.params} metric="elasticity" />
          <div className="mt-1 font-mono text-[9px] text-faint">
            {result.n_sims} sims · {result.elapsed_ms != null ? `${(result.elapsed_ms / 1000).toFixed(1)}s` : "—"} · Δ{Math.round(result.rel_delta * 100)}%
          </div>
        </div>
      )}
    </div>
  );
}
