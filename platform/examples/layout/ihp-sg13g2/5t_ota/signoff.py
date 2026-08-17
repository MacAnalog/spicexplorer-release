#!/usr/bin/env python3
"""Run IHP sg13g2 DRC + LVS on a GDS via the PDK's own runners.

Thin wrapper around ``$PDK/libs.tech/klayout/tech/{drc,lvs}/run_{drc,lvs}.py``. Requires a
working ``klayout`` executable on PATH (see the workspace klayout-runtime shim) plus the
pip ``klayout`` module for the runners' own imports.

    python signoff.py --gds ota_5t.gds --netlist ota_5t_lvs.spice --topcell ota_5t
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys

import pdk as P

DRC = os.path.join(P.KL, "tech/drc/run_drc.py")
LVS = os.path.join(P.KL, "tech/lvs/run_lvs.py")


def run_drc(gds: str, topcell: str, run_dir: str, no_density: bool = True) -> tuple[bool, str]:
    # abspath: the PDK runners chdir into the deck dir, so a relative run_dir
    # would silently land the output inside the PDK tree (and report FAIL).
    gds, run_dir = os.path.abspath(gds), os.path.abspath(run_dir)
    cmd = [sys.executable, DRC, f"--path={gds}", f"--topcell={topcell}", f"--run_dir={run_dir}"]
    if no_density:
        cmd.append("--no_density")
    r = subprocess.run(cmd, cwd=os.path.dirname(DRC), capture_output=True, text=True)
    out = r.stdout + r.stderr
    passed = "DRC Check Passed" in out or "Number of DRC errors for maximum rule set: 0" in out and "Violated" not in out
    return passed, out


def run_lvs(gds: str, netlist: str, topcell: str, run_dir: str) -> tuple[bool, str]:
    gds, netlist, run_dir = (os.path.abspath(p) for p in (gds, netlist, run_dir))
    cmd = [sys.executable, LVS, f"--layout={gds}", f"--netlist={netlist}",
           f"--topcell={topcell}", f"--run_dir={run_dir}"]
    r = subprocess.run(cmd, cwd=os.path.dirname(LVS), capture_output=True, text=True)
    out = r.stdout + r.stderr
    return ("Netlists match" in out), out


def main() -> None:
    here = os.path.dirname(__file__)
    ap = argparse.ArgumentParser(description="DRC + LVS signoff for the 5T OTA")
    ap.add_argument("--gds", default=os.path.join(here, "ota_5t.gds"))
    ap.add_argument("--netlist", default=os.path.join(here, "ota_5t_lvs.spice"))
    ap.add_argument("--topcell", default="ota_5t")
    ap.add_argument("--run-dir", default=os.path.join(here, "signoff_out"))
    a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)

    drc_ok, _ = run_drc(a.gds, a.topcell, os.path.join(a.run_dir, "drc"))
    print(f"DRC (--no_density): {'PASS' if drc_ok else 'FAIL'}")
    lvs_ok, _ = run_lvs(a.gds, a.netlist, a.topcell, os.path.join(a.run_dir, "lvs"))
    print(f"LVS:                {'PASS' if lvs_ok else 'FAIL'}")
    sys.exit(0 if (drc_ok and lvs_ok) else 1)


if __name__ == "__main__":
    main()
