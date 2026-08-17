#!/usr/bin/env python3
"""Before/after layout comparison figure for the v2 resize.

Regenerates the pam4 DUT at the notebook-02 v1 point (nx=2, R_C=70 on the
original edge-fed floorplan — reconstructed via the LayoutParams defaults)
and at the signed-off final point (`gen_layout.FINAL_LAYOUT`), renders
both, and composes the annotated side-by-side written next to this script
as ``before_after.png``.

    PDK_ROOT=~/local/pdks python compare_layouts.py
"""
from __future__ import annotations

import os
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_layout                                                  # noqa: E402
from render import render                                          # noqa: E402

# v1 winner: electrical knobs of the first co-optimization; every layout
# field at its (original) default -> edge-fed M3 input, M1 drops, 1.8 um
# out_gap, rc_sep 8, stack_w 2.0, gap_x 7, cell_gap 6.
V1 = dict(nx=2, rc_ohm=70.0, rb_ohm=58.0, re_ohm=1.5, re_w=9.0, cdeg_ff=20.0)

ANNOT = {
    "before": [
        ("edge-fed input:\nR_B block far left,\nfar MSB cell sees ~80 um stub",
         (0.11, 0.82), (0.16, 0.985)),
        ("4 x Metal3 buses full-width,\n0.8 um gaps -> 3.5 fF\nLSB<->MSB crosstalk",
         (0.45, 0.78), (0.52, 0.955)),
        ("outp/outn only 1.8 um apart:\n7 fF sidewall C (x2 differential)\n"
         "+ 2.0 um-wide TM1, +/-3 um overhang",
         (0.30, 0.36), (0.045, 0.20)),
        ("nx=2 HBTs\n(tail capped at 12 mA\n-> swing needs R_C=70\n-> S22 mismatch)",
         (0.475, 0.52), (0.62, 0.62)),
    ],
    "after": [
        ("center-fed H-tree:\nR_B on centreline, LSB buses\nshrink to short stubs,\n"
         "zero M0/M1 skew", (0.50, 0.885), (0.06, 0.94)),
        ("Metal4 buses, MSB rows innermost,\n3 um pair gap, Metal2 base drops",
         (0.62, 0.71), (0.66, 0.90)),
        ("out_gap 8 um, min-width (1.64) TM1,\nslim risers/stacks, +/-1.5 um "
         "overhang:\noutput C -7 fF/side -> S22 passes at R_C=50",
         (0.30, 0.31), (0.035, 0.16)),
        ("nx=3 HBTs @ 15 mA\n(swing 2.21 ok; S11 closed by\nR_E 3.2 + input fixes)",
         (0.47, 0.485), (0.63, 0.585)),
        ("row compacted:\ngap_x 7->6, cell_gap 6->5\n(shorter summing bus)",
         (0.35, 0.55), (0.045, 0.62)),
    ],
}

TITLES = {
    "before": ("BEFORE — notebook-02 v1 point",
               "nx=2, R_C=70 $\\Omega$, 12 mA  |  107.8 x 67.6 um\n"
               "S22 −8.3 dB ✗   swing 2.07 Vpp ✗   S11 −10.2 ✓"),
    "after": ("AFTER — final signed-off point",
              "nx=3, R_C=50 $\\Omega$, 15 mA  |  99.6 x 75.8 um\n"
              "ALL 8 SPECS PASS:  S22 −10.14   swing 2.21   S11 −10.03"),
}


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        pngs = {}
        for tag, params in (("before", V1),
                            ("after", gen_layout.FINAL_LAYOUT)):
            gen_layout.generate("pam4", gen_layout.LayoutParams(**params),
                                os.path.join(tmp, tag))
            pngs[tag] = os.path.join(tmp, f"{tag}.png")
            render(os.path.join(tmp, tag, "dut_pam4.gds"), pngs[tag])

        fig, axes = plt.subplots(1, 2, figsize=(19, 7.4),
                                 facecolor="#101014")
        kw_box = dict(boxstyle="round,pad=0.35", fc="#ffe9a8",
                      ec="#c8a03c", alpha=0.95)
        kw_arr = dict(arrowstyle="->", color="#ffd75e", lw=1.8)
        for ax, tag in zip(axes, ("before", "after")):
            img = mpimg.imread(pngs[tag])
            H, W = img.shape[0], img.shape[1]
            ax.imshow(img)
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color("#666")
            t, sub = TITLES[tag]
            ax.set_title(t + "\n" + sub, color="w", fontsize=12, pad=8)
            for text, (xa, ya), (xt, yt) in ANNOT[tag]:
                ax.annotate(text, xy=(xa * W, ya * H),
                            xytext=(xt * W, yt * H), fontsize=8.5,
                            bbox=kw_box, arrowprops=kw_arr)
        fig.suptitle("PAM-4 driver layout — before vs after the full-spec "
                     "resize + RF layout optimization (IHP SG13G2, pam4 DUT)",
                     color="w", fontsize=14, y=0.995)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        out = os.path.join(HERE, "before_after.png")
        fig.savefig(out, dpi=110, facecolor=fig.get_facecolor(),
                    bbox_inches="tight")
        # palette-quantize: flat-colour layout render, ~4x smaller in git
        from PIL import Image
        im = Image.open(out).convert("RGB")
        im.quantize(colors=256,
                    method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
        print("wrote", out)


if __name__ == "__main__":
    main()
