"""``spicexplorer-signoff`` CLI — JSON verdicts for probe / drc / lvs / pex."""

from __future__ import annotations

import argparse
import json
import sys

from .drc import run_drc
from .lvs import run_lvs
from .pdk import probe
from .pex import run_pex


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="spicexplorer-signoff", description="physical signoff runners with JSON verdicts"
    )
    ap.add_argument("--pdk", default="ihp-sg13g2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe", help="which tools/decks are available")
    d = sub.add_parser("drc")
    d.add_argument("gds")
    d.add_argument("--cell", required=True)
    d.add_argument("--run-dir", required=True)
    d.add_argument("--density", action="store_true")
    lv = sub.add_parser("lvs")
    lv.add_argument("gds")
    lv.add_argument("--cell", required=True)
    lv.add_argument("--netlist", required=True)
    lv.add_argument("--run-dir", required=True)
    px = sub.add_parser("pex")
    px.add_argument("gds")
    px.add_argument("--cell", required=True)
    px.add_argument("--netlist", required=True)
    px.add_argument("--out-dir", required=True)
    px.add_argument("--mode", default="CC", choices=["CC", "RC", "R"])
    a = ap.parse_args(argv)
    if a.cmd == "probe":
        res = probe(a.pdk).to_dict()
        ok = True
    elif a.cmd == "drc":
        r = run_drc(a.gds, a.cell, a.run_dir, pdk=a.pdk, no_density=not a.density)
        res, ok = r.to_dict(), r.passed
    elif a.cmd == "lvs":
        r = run_lvs(a.gds, a.netlist, a.cell, a.run_dir, pdk=a.pdk)
        res, ok = r.to_dict(), r.passed
    else:
        r = run_pex(a.gds, a.cell, a.netlist, a.out_dir, mode=a.mode, pdk=a.pdk)
        res, ok = r.to_dict(), r.ok
    if "log" in res:
        res["log"] = res["log"][-1500:]
    json.dump(res, sys.stdout, indent=1, default=str)
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
