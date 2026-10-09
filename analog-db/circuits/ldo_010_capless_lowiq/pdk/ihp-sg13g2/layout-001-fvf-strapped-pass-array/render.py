#!/usr/bin/env python3
"""Renders of the drawn cell: the plain PDK-coloured raster, and the LABELLED figure.

Neither drawing lives here — both are platform runsets over the built GDS:

* ``spicexplorer_layout.cli render`` paints the layers in the PDK's own colours;
* ``spicexplorer_signoff.annotate`` draws ``labels.yaml`` (matched groups and the pattern each is
  drawn in, dummies, guard rings, power straps, the pin frame, the 10 mA load path, a 50 um scale
  bar) over that raster. Nothing in ``labels.yaml`` is drawn by hand and no coordinate in it is
  eyeballed: the ranges are placement ordinals of the generator's own rows, and the file says how
  to audit them.

The GDS is regenerable and gitignored, so it is read from the working root
(``$SX_SCRATCH/ldo-adb/layout`` by default, the same place ``signoff.py`` builds into) and only
the small PNGs land in ``out/``.

    analog-db layout run --circuit ldo_010_capless_lowiq --step render
    python render.py --gds <a GDS> --out-dir out
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

CELL = "ldo_ihp_capless"
HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get("SX_SCRATCH", str(Path.home() / "sx-scratch"))) / "ldo-adb" / "layout"


def _run(cmd: list[str]) -> int:
    print("  $", " ".join(str(c) for c in cmd)[:170], flush=True)
    return subprocess.run([str(c) for c in cmd]).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gds", default=str(WORK / f"{CELL}.gds"))
    ap.add_argument("--out-dir", default=str(HERE / "out"))
    ap.add_argument("--labels", default=str(HERE / "labels.yaml"))
    ap.add_argument("--plain-only", action="store_true", help="skip the annotated figures")
    a = ap.parse_args()

    gds, out = Path(a.gds), Path(a.out_dir)
    if not gds.is_file():
        raise SystemExit(
            f"no GDS at {gds} — build it first:\n"
            "  analog-db layout run --circuit ldo_010_capless_lowiq --step signoff -- "
            "--stages build")
    out.mkdir(parents=True, exist_ok=True)

    rc = _run([sys.executable, "-m", "spicexplorer_layout.cli", "render",
               str(gds), str(out / f"{CELL}.png")])
    if rc or a.plain_only:
        return rc

    # The plain raster the overlays sit on is a by-product, so it goes to the working root, not
    # into out/ beside the figures a reviewer reads.
    for ground, variant in (("dark", ""), ("white", "_white")):
        rc = _run([sys.executable, "-m", "spicexplorer_signoff.annotate", str(gds), a.labels,
                   str(out / CELL), "--base", str(WORK / "annotate_base.png"),
                   "--ground", ground, "--variant", variant,
                   "--quantize", "256", "--formats", "png"])
        if rc:
            return rc
    print("  wrote", ", ".join(sorted(p.name for p in out.glob(f"{CELL}*.png"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
