#!/usr/bin/env python3
"""DRC + LVS signoff for the gdsfactory-lane 5T OTA.

Reuses the PDK-runner wrappers from the PyCell lane (``../5t_ota/signoff.py``) —
the signoff decks are engine-agnostic: GDS in, verdict out.

    python signoff.py            # ota_5t_gf.gds vs ota_5t_gf_lvs.spice
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "5t_ota"))
from signoff import run_drc, run_lvs  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="DRC + LVS signoff (gdsfactory lane)")
    ap.add_argument("--gds", default=os.path.join(HERE, "ota_5t_gf.gds"))
    ap.add_argument("--netlist", default=os.path.join(HERE, "ota_5t_gf_lvs.spice"))
    ap.add_argument("--topcell", default="ota_5t_gf")
    ap.add_argument("--run-dir", default=os.path.join(HERE, "signoff_out"))
    a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)

    drc_ok, _ = run_drc(a.gds, a.topcell, os.path.join(a.run_dir, "drc"))
    print(f"DRC (--no_density): {'PASS' if drc_ok else 'FAIL'}")
    lvs_ok, _ = run_lvs(a.gds, a.netlist, a.topcell, os.path.join(a.run_dir, "lvs"))
    print(f"LVS:                {'PASS' if lvs_ok else 'FAIL'}")
    sys.exit(0 if (drc_ok and lvs_ok) else 1)


if __name__ == "__main__":
    main()
