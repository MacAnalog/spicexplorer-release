#!/usr/bin/env python3
"""DRC + LVS signoff for the PAM-4 driver layout DUTs.

Reuses the engine-agnostic PDK-runner wrappers from the platform layout
example (``examples/layout/ihp-sg13g2/5t_ota/signoff.py``).

    python signoff.py                 # all three DUTs
    python signoff.py --dut pam4
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
# platform layout example (5T OTA) provides run_drc/run_lvs. Loaded by path
# under a distinct module name (this file is also called signoff.py).
_OTA = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "..", "layout", "ihp-sg13g2", "5t_ota"))


def _load_ota_signoff():
    import importlib.util
    sys.path.insert(0, _OTA)   # its own `import pdk` needs the dir on path
    spec = importlib.util.spec_from_file_location(
        "ota_signoff", os.path.join(_OTA, "signoff.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ota = _load_ota_signoff()
run_drc, run_lvs = _ota.run_drc, _ota.run_lvs


def signoff_dut(dut: str, out_dir: str = OUT) -> bool:
    gds = os.path.join(out_dir, f"dut_{dut}.gds")
    net = os.path.join(out_dir, f"dut_{dut}_lvs.spice")
    cell = f"pam4drv_{dut}_lay"
    run_dir = os.path.join(out_dir, "signoff", dut)
    drc_ok, dlog = run_drc(gds, cell, os.path.join(run_dir, "drc"))
    lvs_ok, _ = run_lvs(gds, net, cell, os.path.join(run_dir, "lvs"))
    print(f"[{dut}] DRC (--no_density): {'PASS' if drc_ok else 'FAIL'}   "
          f"LVS: {'PASS' if lvs_ok else 'FAIL'}")
    if not drc_ok:
        print("   " + "\n   ".join(
            l for l in dlog.splitlines() if "Violated" in l))
    return drc_ok and lvs_ok


def main() -> None:
    ap = argparse.ArgumentParser(description="layout signoff")
    ap.add_argument("--dut", default="all",
                    choices=["lsb", "msb", "pam4", "all"])
    ap.add_argument("--out-dir", default=OUT)
    a = ap.parse_args()
    duts = ["lsb", "msb", "pam4"] if a.dut == "all" else [a.dut]
    ok = all([signoff_dut(d, a.out_dir) for d in duts])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
