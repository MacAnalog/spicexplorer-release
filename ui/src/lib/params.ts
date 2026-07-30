// DUT parameter naming helpers, shared by the device inspector and the outline
// rail. The convention X_DUT_{DEVICE}_{KIND} is not enforced in the backend, so
// unknown shapes fall back to kind "other" (mirrors routes/sensitivity.py).

export interface DeviceKind {
  device: string;
  kind: "W" | "L" | "NG" | "bias" | "other";
}

/** Parse 'X_DUT_M5_W' -> { device:'M5', kind:'W' }; 'X_DUT_V_BIAS_1' -> bias. */
export function parseDeviceKind(name: string): DeviceKind {
  const base = name.startsWith("X_DUT_") ? name.slice(6) : name;
  if (base.toUpperCase().includes("V_BIAS")) return { device: base, kind: "bias" };
  for (const [suffix, kind] of [["_W", "W"], ["_L", "L"], ["_NG", "NG"]] as const) {
    if (base.endsWith(suffix)) return { device: base.slice(0, -suffix.length), kind };
  }
  return { device: base, kind: "other" };
}
