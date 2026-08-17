#!/usr/bin/env python3
"""Parasitic extraction (PEX) for IHP sg13g2 layouts via **klayout-pex** (kpex).

Engine-agnostic: works on any signoff-clean GDS — both the PyCell lane
(``5t_ota/ota_5t.gds``) and the gdsfactory lane (``5t_ota_gf/ota_5t_gf.gds``).

kpex (https://github.com/iic-jku/klayout-pex) is the KLayout-integrated PEX tool
with first-class ihp-sg13g2 support. It runs the KLayout LVS engine internally
(to get a connectivity database), then extracts:

- ``--mode CC``: coupling + ground capacitances only
- ``--mode RC``: capacitances + wire resistances (default here)
- ``--mode R``:  resistances only

Requirements (see INSTALL.md):
- conda env ``pex`` (Python >= 3.12) with ``pip install klayout-pex``
- a KLayout executable with Ruby >= 2.6 for the kpex LVS deck — the py3.11
  source build's batch wrapper (``~/local/klayout-py311/klayout-batch.sh``);
  the rpm-shim batch klayout (Ruby 2.5) can NOT parse the deck.

    conda activate pex
    python pex_kpex.py --gds 5t_ota_gf/ota_5t_gf.gds --cell ota_5t_gf \\
                       --schematic 5t_ota_gf/ota_5t_gf_lvs.spice

Output: ``<out_dir>/<cell>__<cell>/<cell>_k25d_pex_netlist.spice`` — the layout
netlist (devices + parasitic R/C) ready for ngspice.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

DEFAULT_KLAYOUT: str = os.path.expanduser("~/local/klayout-py311/klayout-batch.sh")


def run_kpex(gds: str, cell: str, schematic: str, out_dir: str,
             mode: str = "RC", engine: str = "--2.5D") -> tuple[bool, str, str]:
    env = dict(os.environ)
    env.setdefault("KPEX_KLAYOUT_EXE", DEFAULT_KLAYOUT)
    env.setdefault("PDK_ROOT", os.path.expanduser("~/local/pdks"))
    kpex = shutil.which("kpex")
    if not kpex:
        sys.exit("kpex not on PATH — `conda activate pex` first (see INSTALL.md)")
    cmd = [kpex, "--pdk", "ihp-sg13g2", "--gds", gds, "--cell", cell,
           "--schematic", schematic, engine, "--mode", mode, "--out_dir", out_dir]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    # kpex writes to <out_dir>/<gds-stem>__<cell>/<cell>_k25d_pex_netlist.spice
    stem = os.path.splitext(os.path.basename(gds))[0]
    spice = os.path.join(out_dir, f"{stem}__{cell}", f"{cell}_k25d_pex_netlist.spice")
    ok = r.returncode == 0 and os.path.exists(spice)
    return ok, spice, r.stdout + r.stderr


def main() -> None:
    ap = argparse.ArgumentParser(description="kpex PEX for sg13g2 layouts")
    ap.add_argument("--gds", required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--schematic", required=True, help="LVS reference netlist")
    ap.add_argument("--mode", default="RC", choices=["CC", "RC", "R"])
    ap.add_argument("--out-dir", default=None,
                    help="default: pex_out/kpex next to the GDS")
    a = ap.parse_args()

    out_dir = a.out_dir or os.path.join(os.path.dirname(os.path.abspath(a.gds)),
                                        "pex_out", "kpex")
    ok, spice, log = run_kpex(os.path.abspath(a.gds), a.cell,
                              os.path.abspath(a.schematic), out_dir, a.mode)
    if not ok:
        print(log[-3000:])
        sys.exit(f"kpex FAILED (see {out_dir})")
    nR = nC = 0
    with open(spice) as f:
        for line in f:
            nR += line.startswith("R")
            nC += line.startswith("C")
    print(f"PEX OK ({a.mode}): {spice}")
    print(f"  parasitics: {nC} C, {nR} R")


if __name__ == "__main__":
    main()
