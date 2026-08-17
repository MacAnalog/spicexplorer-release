#!/usr/bin/env python3
"""Pre- vs post-layout AC comparison for the 5T OTA (ngspice, sg13g2 models).

Simulates the same open-loop AC bench (amp_001_5t ``ac_open_loop``: VDD=1.5,
VCM=0.8, IBIAS=20u, CL=50f) on:

1. the **schematic** (the flat LVS reference netlist), and
2. the **PEX netlist** extracted by kpex (devices + parasitic R/C),

and reports dc gain / UGF / phase margin for both. This is the point of PEX:
the delta is what the layout parasitics cost you.

Both netlists use primitive ``M`` cards (LVS/kpex convention); the ngspice
sg13g2 devices are *subcircuits*, so cards are rewritten ``M...`` -> ``XM...``
(the subckt accepts w/l/as/ad/ps/pd/rfmode; with as/ad given, ``pre_layout``
junction estimation is bypassed).

    python sim_pex_compare.py --schematic 5t_ota_gf/ota_5t_gf_lvs.spice \\
        --pex 5t_ota_gf/pex_out/kpex/ota_5t_gf__ota_5t_gf/ota_5t_gf_k25d_pex_netlist.spice \\
        --cell ota_5t_gf
"""
from __future__ import annotations

import argparse
import math
import os
import re
import subprocess
import sys
import tempfile

PDK_ROOT: str = os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks"))
MODELS: str = os.path.join(PDK_ROOT, "ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib")

BENCH: dict[str, object] = dict(VDD=1.5, VCM=0.8, IBIAS="20u", CL="50f",
                                FSTART="1k", FSTOP="100MEG")


def prep_dut(netlist_path: str, cell: str, workdir: str) -> tuple[str, list[str]]:
    """M -> XM card rewrite + port order from the .subckt line."""
    ports = None
    out = []
    with open(netlist_path) as f:
        for line in f:
            m = re.match(rf"^\.subckt\s+{re.escape(cell)}\s+(.*)$", line, re.I)
            if m:
                ports = m.group(1).split()
            if re.match(r"^M", line):
                line = "X" + line
            elif re.match(r"^\+", line) and out and out[-1].startswith("XM"):
                pass  # continuation of a rewritten card — fine as-is
            out.append(line)
    if not ports:
        sys.exit(f"no .subckt {cell} in {netlist_path}")
    dut = os.path.join(workdir, os.path.basename(netlist_path) + ".sim")
    with open(dut, "w") as f:
        f.writelines(out)
    return dut, ports


def run_ac(netlist_path: str, cell: str, tag: str,
           workdir: str) -> tuple[float, float | None, float | None]:
    workdir = os.path.abspath(workdir)   # deck paths are used from cwd=workdir
    dut, ports = prep_dut(netlist_path, cell, workdir)
    node = {"vdd": "vdd", "vss": "0", "vout": "vout", "vinp": "vinp",
            "vinn": "vinn", "ibias": "ibias"}
    xline = "XDUT " + " ".join(node[p.lower()] for p in ports) + f" {cell}"
    data = os.path.join(workdir, f"{tag}.txt")
    deck = f"""* {tag} AC bench (amp_001_5t ac_open_loop conditions)
.lib {MODELS} mos_tt
.include {dut}
VDD vdd 0 {BENCH['VDD']}
IB  vdd ibias {BENCH['IBIAS']}
VIP vinp 0 DC {BENCH['VCM']} AC 0.5
VIN vinn 0 DC {BENCH['VCM']} AC -0.5
CL  vout 0 {BENCH['CL']}
{xline}
* nodeset: PEX netlists carry dense R-networks whose flat-start op sometimes
* fails gmin/source stepping; a rough bias guess makes convergence reliable.
.nodeset v(ibias)=0.55 v(vout)=0.8
.ac dec 101 {BENCH['FSTART']} {BENCH['FSTOP']}
.control
run
wrdata {data} vdb(vout) vp(vout)
.endc
.end
"""
    deckf = os.path.join(workdir, f"{tag}.sp")
    with open(deckf, "w") as f:
        f.write(deck)
    r = subprocess.run(["ngspice", "-b", deckf], capture_output=True, text=True,
                       cwd=workdir)
    if not os.path.exists(data):
        raise RuntimeError(f"{tag}: ngspice produced no data\n"
                           + r.stdout[-2000:] + r.stderr[-2000:])
    f_, gdb, ph = [], [], []
    for line in open(data):
        v = line.split()
        if len(v) >= 4:
            f_.append(float(v[0])); gdb.append(float(v[1])); ph.append(float(v[3]))
    dc = gdb[0]
    ugf = pm = None
    for i in range(1, len(f_)):
        if gdb[i - 1] >= 0 > gdb[i]:
            t = gdb[i - 1] / (gdb[i - 1] - gdb[i])
            ugf = f_[i - 1] * (f_[i] / f_[i - 1]) ** t
            phi = ph[i - 1] + t * (ph[i] - ph[i - 1])
            pm = 180 + math.degrees(phi) if abs(phi) < 7 else 180 + phi
            break
    return dc, ugf, pm


def main() -> None:
    ap = argparse.ArgumentParser(description="pre/post-layout AC compare (sg13g2)")
    ap.add_argument("--schematic", required=True, help="flat LVS reference netlist")
    ap.add_argument("--pex", required=True, help="kpex-extracted netlist")
    ap.add_argument("--cell", required=True)
    ap.add_argument("--workdir", default=None)
    a = ap.parse_args()
    work = a.workdir or tempfile.mkdtemp(prefix="pex_compare_")
    os.makedirs(work, exist_ok=True)

    rows = []
    for tag, path in (("pre-layout ", a.schematic), ("post-layout", a.pex)):
        dc, ugf, pm = run_ac(os.path.abspath(path), a.cell, tag.strip(), work)
        rows.append((tag, dc, ugf, pm))
        print(f"{tag}: dc_gain = {dc:6.2f} dB   ugf = {ugf/1e6:7.3f} MHz   pm = {pm:5.1f} deg")
    d = rows[1]
    p = rows[0]
    print(f"delta      : dc_gain = {d[1]-p[1]:+6.2f} dB   ugf = {(d[2]-p[2])/1e6:+7.3f} MHz   "
          f"pm = {d[3]-p[3]:+5.1f} deg   (work: {work})")


if __name__ == "__main__":
    main()
