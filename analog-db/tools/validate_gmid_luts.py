"""Validate the generated gm/ID LUT store: physicality + (sampled) live-.op round-trip.

Per-LUT physical acceptance (the gmid-lut-generation skill's checklist, encoded):
  * every stored array finite;
  * weak-inversion gm/ID peak in a physical band (~18-45 S/A);
  * ID monotonic non-decreasing in VGS (at Lmin, mid-VDS, VSB=0);
  * DeviceTable.at(gm/ID=10) solves a VGS inside the characterized range, av0>0, fT>0;
  * a grid-point lookup reproduces the stored value (reader/axes sanity).

Then a SAMPLED live round-trip (open PDKs, native ngspice): bias one nmos + one pmos per PDK at the
LUT-predicted VGS for gm/ID=15 and compare the simulated gm/ID (<3% target).

Usage:
    python tools/validate_gmid_luts.py               # physicality over the whole store
    python tools/validate_gmid_luts.py --live         # + the sampled live round-trip
    python tools/validate_gmid_luts.py --pdk sky130
"""

from __future__ import annotations

import argparse

import numpy as np
from spicexplorer_gmid import DeviceTable

from spicexplorer_analog_db import gmid

PEAK_LO, PEAK_HI = 18.0, 46.0  # physical weak-inversion gm/ID band (S/A)


def check_lut(pdk: str, device: str, corner: str, temp_c: float) -> dict:
    r: dict = {"pdk": pdk, "device": device, "corner": corner, "temp_c": temp_c,
               "ok": True, "notes": []}
    path = gmid.find_lut_path(pdk, device, corner, temp_c if temp_c != 27.0 else None)
    try:
        t = DeviceTable.load(path)
        d = t.lut  # pygmid Lookup; index like a dict
    except Exception as e:  # noqa: BLE001
        r["ok"] = False
        r["notes"].append(f"load: {type(e).__name__}: {e}")
        return r

    ID, GM = np.asarray(d["ID"]), np.asarray(d["GM"])
    L, VGS, VDS, VSB = (np.asarray(d[k]) for k in ("L", "VGS", "VDS", "VSB"))
    r["grid"] = f"{L.size}x{VGS.size}x{VDS.size}x{VSB.size}"

    # 1. finite
    for k in ("ID", "VT", "GM", "GDS", "CGG"):
        if k in d and not np.all(np.isfinite(np.asarray(d[k]))):
            r["ok"] = False
            r["notes"].append(f"non-finite {k}")

    # 2. gm/ID peak physical — measured only where the device is meaningfully ON (ID above a
    # current floor). Off/deep-subthreshold points sit at the gmin numerical floor (ID~1e-16..1e-31)
    # where GM/ID is dominated by round-off and spikes to 1e6-1e9; that is a numerical artifact of
    # the off region, not a table defect (the weak-inversion peak the book cares about is at turn-on).
    ID_FLOOR = 1e-9  # A — 1 nA, safely above the gmin floor, below any real weak-inversion current
    on = ID > ID_FLOOR
    with np.errstate(divide="ignore", invalid="ignore"):
        gm_id_on = np.where(on, GM / ID, np.nan)
    peak = float(np.nanmax(gm_id_on)) if on.any() else float("nan")
    r["gm_id_peak"] = round(peak, 1)
    if not (PEAK_LO <= peak <= PEAK_HI):
        r["ok"] = False
        r["notes"].append(f"gm/ID peak {peak:.1f} (ID>1nA) out of [{PEAK_LO},{PEAK_HI}]")

    # 3. ID monotonic non-decreasing in VGS (Lmin, mid VDS, VSB=0) — in the ON region only (the
    # off-region floor is noise). Allow a small negative tolerance for numerical wiggle.
    jvds = VDS.size // 2
    idv = ID[0, :, jvds, 0]
    onv = idv > ID_FLOOR
    if onv.sum() >= 2:
        d_on = np.diff(idv[onv])
        if np.any(d_on < -1e-3 * max(abs(idv[onv]).max(), 1e-18)):
            r["ok"] = False
            r["notes"].append("ID non-monotonic in VGS (ON region)")

    # 4. DeviceTable.at solves in-range
    Lmid = float(L[L.size // 3])
    vds = float(VDS.max()) / 2
    try:
        op = t.at(10.0, Lmid, vds, 0.0)
        if not (VGS.min() <= op.vgs <= VGS.max()) or op.av0 <= 0 or op.ft <= 0:
            r["ok"] = False
            r["notes"].append(f"at() off: vgs={op.vgs:.3g} av0={op.av0:.3g} ft={op.ft:.3g}")
        r["vgs@10"] = round(op.vgs, 4)
        r["av0@10"] = round(op.av0, 1)
        r["fT@10_GHz"] = round(op.ft / 1e9, 2)
    except Exception as e:  # noqa: BLE001
        r["ok"] = False
        r["notes"].append(f"at(): {type(e).__name__}: {e}")

    # 5. grid-point lookup reproduces stored value (reader/axes sanity)
    il, ig, jd, kb = L.size // 2, VGS.size // 2, VDS.size // 2, 0
    got = float(np.asarray(d.look_up("ID", L=float(L[il]), VGS=float(VGS[ig]),
                                     VDS=float(VDS[jd]), VSB=float(VSB[kb]))).reshape(-1)[0])
    want = float(ID[il, ig, jd, kb])
    if want != 0 and abs(got - want) / abs(want) > 1e-3:
        r["ok"] = False
        r["notes"].append(f"grid-point lookup {got:.3e} != stored {want:.3e}")
    return r


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdk")
    ap.add_argument("--live", action="store_true", help="add the sampled native-ngspice round-trip")
    args = ap.parse_args(argv)

    rows = gmid.list_luts(args.pdk)
    if not rows:
        print("no LUTs found in the store")
        return 1
    print(f"validating {len(rows)} LUTs\n")
    results = [check_lut(r["pdk"], r["device"], r["corner"], r["temp_c"]) for r in rows]
    fails = [r for r in results if not r["ok"]]

    hdr = f"{'pdk':11s} {'device':26s} {'cnr':3s} {'grid':16s} {'peak':>5s} {'av0@10':>7s} {'fT@10':>7s}  ok"
    print(hdr); print("-" * len(hdr))
    for r in sorted(results, key=lambda x: (x["pdk"], x["device"], x["corner"])):
        print(f"{r['pdk']:11s} {r['device']:26s} {r['corner']:3s} {r.get('grid',''):16s} "
              f"{r.get('gm_id_peak',''):>5} {r.get('av0@10',''):>7} {r.get('fT@10_GHz',''):>7}  "
              f"{'PASS' if r['ok'] else 'FAIL: ' + '; '.join(r['notes'])}")
    print(f"\n{len(results) - len(fails)}/{len(results)} physical-acceptance PASS")

    if args.live:
        rc = _live_roundtrip(args.pdk)
        if rc:
            return rc
    return 1 if fails else 0


def _live_roundtrip(pdk_filter: str | None) -> int:
    """Bias a real device at the LUT-predicted VGS (gm/ID=15) and compare simulated gm/ID."""
    from dataclasses import replace
    samples = [
        ("sky130", "sky130_fd_pr__nfet_01v8", 0.5, 0.9),
        ("sky130", "sky130_fd_pr__pfet_01v8", 0.5, 0.9),
        ("ihp-sg13g2", "sg13_lv_nmos", 0.5, 0.75),
        ("gf180mcu", "nfet_03v3", 0.5, 1.65),
    ]
    print("\n=== sampled live-.op round-trip (target <3% on gm/ID) ===")
    bad = 0
    for pdk, device, L, vds in samples:
        if pdk_filter and pdk != pdk_filter:
            continue
        try:
            t = DeviceTable.load(gmid.find_lut_path(pdk, device, "tt"))
            op = t.at(15.0, L, vds, 0.0)
            cfg = gmid.GmidConfig.from_registry(pdk, device=device)
            cfg = replace(cfg, length_um=[L], vgs=(op.vgs, 0.05, op.vgs), vds=(vds, 0.1, vds),
                          vsb=(0.0, -0.4, 0.0))
            run = gmid.native_deck_runner(pdk)
            lut = gmid.extract(cfg, run)
            gm_id_sim = float((lut["GM"] / lut["ID"]).reshape(-1)[0])
            err = abs(gm_id_sim - 15.0) / 15.0 * 100
            flag = "ok" if err < 3.0 else "HIGH"
            if err >= 3.0:
                bad += 1
            print(f"  {pdk:11s} {device:24s} VGS={op.vgs:.4f} -> sim gm/ID={gm_id_sim:.2f} "
                  f"(target 15.0, err {err:.1f}% {flag})")
        except Exception as e:  # noqa: BLE001
            print(f"  {pdk:11s} {device:24s} round-trip ERR: {type(e).__name__}: {e}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
