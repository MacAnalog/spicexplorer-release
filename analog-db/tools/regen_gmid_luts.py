#!/usr/bin/env python
"""Regenerate the full gm/ID LUT store from the PDK registries (out-of-repo, not committed).

The gm/ID LUTs are **not** tracked in git — the open-PDK tables are large at the max-fidelity
25 mV grid, and the FOUNDRY-n65 tables come from a licensed kit (NDA). This script rebuilds the
whole device-characterization store into the out-of-repo location (`gmid.out_root`, default
``~/.spicexplorer/gmid/<pdk>/``) so a fresh checkout can reproduce every DUT with one command.

Lanes (auto-selected per PDK by the registry ``gmid.engine`` / ``sim_engine`` marker):
  * **open PDKs** (sky130 / ihp-sg13g2 / gf180mcu) → native ngspice + ``$PDK_ROOT`` (per-L
    parallel, ``gmid.simulator.workers``); falls back to the docker base image when native
    isn't available.
  * **FOUNDRY-n65** → headless Spectre via the virtuoso-bridge (both polarities per pass, one
    process per (L,VSB); the wrapper + Spectre come from ``~/.virtuoso-bridge/local.env``).

Grids, corners, flavours, W, temp all come from ``_shared/pdk/<pdk>.yaml`` → ``gmid:``.
Everything is registry-driven; this script only fans the extractions out and reports.

Examples
--------
    python tools/regen_gmid_luts.py                     # everything the environment can build
    python tools/regen_gmid_luts.py --pdk sky130        # one PDK
    python tools/regen_gmid_luts.py --open-only         # skip the licensed Spectre lane
    python tools/regen_gmid_luts.py --corner tt         # override the corner set (smoke)
    python tools/regen_gmid_luts.py --dry-run           # print the plan, run nothing
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time

# analog-db is importable in this venv; use it to read the registries (single source of truth).
from spicexplorer_analog_db import pdks

# Open-lane device sets. Each entry: (device_model, grid_override_flags). The override widens the
# bias grid for off-nominal-rail flavours (ihp HV is a 2.5 V device; the registry gmid.sweep is the
# 1.5 V LV rail) AND swaps the L set — the HV device's min-L is ~0.45 µm, so the LV lengths
# (0.13/0.15/0.2 µm) are BELOW it and characterize as garbage (ID=0, gm/ID spikes). HV needs its own
# L list ≥ its min-L. Empty list = use the registry default grid.
_HV25 = [
    "--vgs", "0,0.025,2.5", "--vds", "0,0.025,2.5", "--vsb", "0,-0.125,-1.25",
    "--length", "0.45,0.5,0.6,0.8,1.0,1.3,1.6,2.0,2.5,3.0",   # HV min-L ~0.45 µm
]
OPEN_DEVICES: dict[str, list[tuple[str, list[str]]]] = {
    "sky130": [
        ("sky130_fd_pr__nfet_01v8", []),
        ("sky130_fd_pr__pfet_01v8", []),
    ],
    "ihp-sg13g2": [
        ("sg13_lv_nmos", []),
        ("sg13_lv_pmos", []),
        ("sg13_hv_nmos", _HV25),
        ("sg13_hv_pmos", _HV25),
    ],
    "gf180mcu": [
        ("nfet_03v3", []),
        ("pfet_03v3", []),
    ],
}
SPECTRE_PDKS = ["FOUNDRY-n65"]

# Which open devices get narrow finger-width companions (--fingers). CORE devices only — the HV
# device is inherently large and its min finger width is well above the 0.5 µm narrow companion.
FINGER_COMPANION_DEVICES: dict[str, list[str]] = {
    "sky130": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
    "ihp-sg13g2": ["sg13_lv_nmos", "sg13_lv_pmos"],
    "gf180mcu": ["nfet_03v3", "pfet_03v3"],
}
_NOMINAL_WF = 5.0


def _companion_widths(pdk: str) -> list[float]:
    """Non-nominal finger widths (registry gmid.finger_widths minus the 5 µm nominal)."""
    fw = (pdks.load_registry(pdk).get("gmid", {}) or {}).get("finger_widths", []) or []
    return [float(w) for w in fw if abs(float(w) - _NOMINAL_WF) > 1e-9]


def _analog_db() -> list[str]:
    # ALWAYS the running interpreter's module — never a PATH `analog-db`, which on a conda-tainted
    # PATH resolves to a different (possibly stale) install than the venv this script imports from.
    return [sys.executable, "-m", "spicexplorer_analog_db.cli"]


def _run(cmd: list[str], *, dry: bool) -> int:
    print("  $ " + " ".join(cmd), flush=True)
    if dry:
        return 0
    t0 = time.time()
    proc = subprocess.run(cmd)
    print(f"    -> rc={proc.returncode} ({time.time() - t0:.0f}s)", flush=True)
    return proc.returncode


def regen_open(pdk: str, corner: str, dry: bool, wf: float | None = None) -> list[str]:
    """Nominal (wf=None → 5 µm) or a finger-width companion (wf set → only companion-eligible cores)."""
    fails = []
    if wf is None:
        devices = OPEN_DEVICES.get(pdk, [])
    else:
        eligible = set(FINGER_COMPANION_DEVICES.get(pdk, []))
        devices = [(d, ov) for d, ov in OPEN_DEVICES.get(pdk, []) if d in eligible]
    for device, override in devices:
        cmd = [*_analog_db(), "gmid-extract", "--pdk", pdk, "--device", device,
               "--corner", corner, *override]
        if wf is not None:
            cmd += ["--width", f"{wf:g}"]
        if _run(cmd, dry=dry) != 0:
            fails.append(f"{pdk}/{device}" + (f"@wf{wf:g}" if wf else ""))
    return fails


def regen_spectre(pdk: str, corner: str, flavor: str, dry: bool, wf: float | None = None) -> list[str]:
    cmd = [*_analog_db(), "gmid-extract-spectre", "--pdk", pdk,
           "--corner", corner, "--flavor", flavor]
    if wf is not None:
        cmd += ["--width", f"{wf:g}"]
    tag = f"{pdk}/{flavor}" + (f"@wf{wf:g}" if wf else "")
    return [tag] if _run(cmd, dry=dry) != 0 else []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdk", help="limit to one PDK (default: all registered)")
    ap.add_argument("--corner", default="all",
                    help="corner set: 'all' (registry gmid.corners), or a comma list (default: all)")
    ap.add_argument("--flavor", default="all",
                    help="Spectre-lane Vt flavours: 'all' (registry gmid.flavors) or a comma list")
    ap.add_argument("--open-only", action="store_true", help="skip the licensed Spectre lane")
    ap.add_argument("--spectre-only", action="store_true", help="only the licensed Spectre lane")
    ap.add_argument("--fingers", action="store_true",
                    help="ALSO generate the narrow finger-width companions (registry gmid.finger_widths "
                    "minus the 5 µm nominal) for the core devices — tagged __wf<W>u")
    ap.add_argument("--fingers-only", action="store_true",
                    help="ONLY the finger-width companions (assume the 5 µm nominal already exists)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    args = ap.parse_args(argv)

    all_pdks = list(pdks.registry_ids())
    targets = [args.pdk] if args.pdk else all_pdks
    fails: list[str] = []

    for pdk in targets:
        reg = pdks.load_registry(pdk)
        g = reg.get("gmid") or {}
        if not g:
            continue
        is_spectre = g.get("engine", reg.get("sim_engine")) == "spectre"
        if is_spectre and args.open_only:
            print(f"[skip] {pdk}: Spectre lane (--open-only)")
            continue
        if not is_spectre and args.spectre_only:
            continue
        print(f"\n=== {pdk} ({'spectre' if is_spectre else 'open ngspice'}) ===", flush=True)
        # nominal 5 µm unless --fingers-only; companion widths when --fingers/--fingers-only
        nominal_wfs: list[float | None] = [] if args.fingers_only else [None]
        companion_wfs: list[float | None] = (
            list(_companion_widths(pdk)) if (args.fingers or args.fingers_only) else []
        )
        if is_spectre:
            flavors = [str(f) for f in g.get("flavors", ["core"])] if args.flavor == "all" \
                else [f.strip() for f in args.flavor.split(",") if f.strip()]
            for fl in flavors:
                for wf in nominal_wfs + companion_wfs:
                    fails += regen_spectre(pdk, args.corner, fl, args.dry_run, wf)
        else:
            if pdk not in OPEN_DEVICES:
                print(f"[skip] {pdk}: no device set in OPEN_DEVICES")
                continue
            for wf in nominal_wfs + companion_wfs:
                fails += regen_open(pdk, args.corner, args.dry_run, wf)

    print("\n=== DONE ===")
    if fails:
        print("FAILURES: " + ", ".join(fails))
        return 1
    print("all extractions ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
