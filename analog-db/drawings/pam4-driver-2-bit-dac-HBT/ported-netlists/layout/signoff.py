#!/usr/bin/env python3
"""DRC + LVS signoff for the PAM-4 driver layout DUTs.

The runners are the platform's ``spicexplorer_signoff`` package: the PDK's own
KLayout decks under ``$PDK_ROOT``, run by the ``klayout`` on PATH (or
``$SIGNOFF_KLAYOUT``). ``run_drc`` and ``run_lvs`` below return the
``(passed, text)`` pair that ``optimize_layout.py`` and notebook 02 unpack.

    python signoff.py                 # all three DUTs
    python signoff.py --dut pam4
"""
from __future__ import annotations

import argparse
import os
import sys

from spicexplorer_signoff import run_drc as _run_drc
from spicexplorer_signoff import run_lvs as _run_lvs

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def _pair(res) -> tuple[bool, str]:
    """The verdict, and the runner's reason and output tail as one text."""
    return res.passed, "\n".join(t for t in (res.reason, res.log) if t)


def run_drc(gds: str, topcell: str, run_dir: str,
            no_density: bool = True) -> tuple[bool, str]:
    return _pair(_run_drc(gds, topcell, run_dir, no_density=no_density))


def run_lvs(gds: str, netlist: str, topcell: str, run_dir: str) -> tuple[bool, str]:
    return _pair(_run_lvs(gds, netlist, topcell, run_dir))


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
