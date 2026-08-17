#!/usr/bin/env python3
"""IIC-OSIC-style signoff: **Magic DRC** + **netgen LVS** on the 5T OTA.

Complements ``signoff.py`` (KLayout DRC/LVS) with the classic open-source flow. Requires
``magic`` and ``netgen`` on PATH (see the workspace klayout/magic/netgen runtime shims).

- **Magic DRC** runs natively on the GDS via the self-contained ``ihp-sg13g2-GDS.tech``
  (use ``-rcfile /dev/null`` so the PDK ``.magicrc`` doesn't reload a cif-less tech).
- **netgen LVS** compares an *extracted* layout netlist against the schematic. Magic's own
  device extraction does **not** yet recognise the KLayout-PyCell GDS (its `.ext` shows
  POLY/DIFF nodes but no `fet` — a layer/implant-recognition gap between KLayout-generated
  geometry and magic's device rules), so we feed netgen the **KLayout-extracted** netlist
  (correct, from ``signoff.run_lvs``). netgen is the comparator either way — the tool the
  IIC-OSIC/CACE flow uses for LVS. Getting magic-native extraction is a documented follow-up.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys

import pdk as P
import signoff  # reuse the KLayout LVS extraction

MAGIC_TECH = os.path.join(P.KL.replace("klayout", "magic"), "ihp-sg13g2-GDS.tech")
NETGEN_SETUP = os.path.join(P.KL.replace("klayout", "netgen"), "ihp-sg13g2_setup.tcl")


def magic_drc(gds: str, topcell: str, work: str) -> tuple[int | None, str]:
    """Native Magic DRC on the GDS. Returns (n_violations, raw_output)."""
    os.makedirs(work, exist_ok=True)
    script = (
        f"gds read {gds}\n"
        f"load {topcell}\n"
        "select top cell\n"
        "drc euclidean on\n"
        "drc check\n"
        "drc catchup\n"
        "puts \"MAGIC_DRC_TOTAL=[drc list count total]\"\n"
        "quit -noprompt\n"
    )
    env = dict(os.environ, PDK_ROOT=os.environ.get("PDK_ROOT", P.PDK_ROOT))
    r = subprocess.run(["magic", "-dnull", "-noconsole", "-rcfile", "/dev/null",
                        "-T", MAGIC_TECH],
                       input=script, capture_output=True, text=True, cwd=work, env=env)
    out = r.stdout + r.stderr
    n = None
    for line in out.splitlines():
        if line.startswith("MAGIC_DRC_TOTAL="):
            n = int(line.split("=", 1)[1])
    return n, out


def netgen_lvs(layout_cir: str, schematic: str, topcell: str, work: str) -> tuple[bool, str]:
    """netgen LVS: extracted layout netlist vs schematic. Returns (matched, raw)."""
    os.makedirs(work, exist_ok=True)
    comp = os.path.join(work, "netgen_comp.out")
    r = subprocess.run(["netgen", "-batch", "lvs",
                        f"{layout_cir} {topcell}", f"{schematic} {topcell}",
                        NETGEN_SETUP, comp],
                       capture_output=True, text=True, cwd=work)
    out = r.stdout + r.stderr
    return ("match uniquely" in out.lower()), out


def main() -> None:
    here = os.path.dirname(__file__)
    ap = argparse.ArgumentParser(description="Magic DRC + netgen LVS signoff (IIC-OSIC style)")
    ap.add_argument("--gds", default=os.path.join(here, "ota_5t.gds"))
    ap.add_argument("--netlist", default=os.path.join(here, "ota_5t_lvs.spice"))
    ap.add_argument("--topcell", default="ota_5t")
    ap.add_argument("--run-dir", default=os.path.join(here, "signoff_mn_out"))
    a = ap.parse_args()

    n, _ = magic_drc(os.path.abspath(a.gds), a.topcell, os.path.join(a.run_dir, "magic"))
    print(f"Magic DRC:  {'PASS (0)' if n == 0 else f'FAIL ({n})' if n is not None else 'ERROR'}")

    # Get a correct extracted layout netlist from the KLayout LVS run, then netgen-compare it.
    klvs = os.path.join(a.run_dir, "klayout_lvs")
    signoff.run_lvs(os.path.abspath(a.gds), os.path.abspath(a.netlist), a.topcell, klvs)
    extracted = os.path.join(klvs, f"{a.topcell}_extracted.cir")
    if not os.path.exists(extracted):
        print("netgen LVS: ERROR (no extracted netlist)"); sys.exit(1)
    ok, _ = netgen_lvs(extracted, os.path.abspath(a.netlist), a.topcell,
                       os.path.join(a.run_dir, "netgen"))
    print(f"netgen LVS: {'PASS (match uniquely)' if ok else 'FAIL'}")
    sys.exit(0 if (n == 0 and ok) else 1)


if __name__ == "__main__":
    main()
