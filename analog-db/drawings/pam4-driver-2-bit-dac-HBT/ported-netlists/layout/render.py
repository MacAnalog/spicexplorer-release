#!/usr/bin/env python3
"""Render the DUT GDS files to PNG with the IHP layer colors (headless)."""
from __future__ import annotations

import argparse
import os

import klayout.lay as klay

HERE = os.path.dirname(os.path.abspath(__file__))
LYP = os.path.join(os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks")),
                   "ihp-sg13g2/libs.tech/klayout/tech/sg13g2.lyp")


def render(gds: str, png: str, w: int = 1400, h: int = 900) -> None:
    lv = klay.LayoutView()
    lv.load_layout(gds, 0)
    if os.path.exists(LYP):
        lv.load_layer_props(LYP)
    lv.max_hier_levels = 10
    lv.zoom_fit()
    lv.save_image(png, w, h)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.join(HERE, "out"))
    a = ap.parse_args()
    for d in ("lsb", "msb", "pam4"):
        gds = os.path.join(a.out_dir, f"dut_{d}.gds")
        if os.path.exists(gds):
            png = os.path.join(a.out_dir, f"dut_{d}.png")
            render(gds, png)
            print(f"rendered {png}")


if __name__ == "__main__":
    main()
