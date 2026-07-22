"""Cross-pipeline correctness gate: validate our generated IHP gm/ID LUTs against the iic-jku
``analog-circuit-design`` ground-truth ``.mat`` tables.

The iic-jku project (Harald Pretl, JKU) ships independently-characterized Murmann-kit LUTs for the
same IHP sg13g2 PSP models we extract. Loading both through ``pygmid.Lookup`` and comparing the
gm/ID-derived quantities (JD, intrinsic gain, fT, VGS) at matched bias points proves our
``gmid-extract`` pipeline reproduces a reference characterization — and is the **regression guard for
the pmos magnitude convention**: a sign bug (raw-negative axes / reversed slices) would blow VGS far
past the 5 mV tolerance.

Skips cleanly when the iic-jku reference isn't checked out (a standalone analog-db clone has no
platform ``submodules/``); set ``$IIC_JKU_GMID_DIR`` to point at it explicitly.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from spicexplorer_analog_db import paths

pytest.importorskip("pygmid")
from pygmid import Lookup  # noqa: E402

TWO_PI = 2 * np.pi


def _ground_truth_dir() -> Path | None:
    candidates = []
    if os.environ.get("IIC_JKU_GMID_DIR"):
        candidates.append(Path(os.environ["IIC_JKU_GMID_DIR"]))
    # platform layout: <platform>/examples/analog-db (db_root) + <platform>/submodules/…
    candidates.append(
        paths.db_root().parent.parent / "submodules" / "analog-circuit-design" / "gmid"
    )
    for c in candidates:
        if (c / "sg13_lv_nmos.mat").is_file():
            return c
    return None


GT = _ground_truth_dir()

# (our committed device LUT stem, the iic-jku ground-truth .mat) — both IHP sg13g2 lv, tt/NOM.
PAIRS = [
    ("sg13_lv_nmos", "sg13_lv_nmos.mat"),
    ("sg13_lv_pmos", "sg13_lv_pmos.mat"),
]


@pytest.mark.skipif(GT is None, reason="iic-jku analog-circuit-design/gmid ground-truth not present")
@pytest.mark.parametrize("device,matfile", PAIRS)
def test_ihp_lut_matches_iic_jku_ground_truth(device: str, matfile: str):
    assert GT is not None  # narrowed by skipif
    ours_path = paths.shared_root() / "gmid" / "ihp-sg13g2" / f"{device}__tt.pkl"
    if not ours_path.is_file():
        pytest.skip(f"{ours_path.name} not committed")
    ours, ref = Lookup(str(ours_path)), Lookup(str(GT / matfile))

    worst = {"jd": 0.0, "av0": 0.0, "ft": 0.0, "vgs": 0.0}
    where = dict(worst)
    n, vsb_covered = 0, False
    # Sweep a grid common to both tables — and ASSERT VARIATION coverage, not one cell (theme A).
    for L in (0.13, 0.2, 0.5, 1.0):
        for vds in (0.4, 0.6, 0.9):
            for vsb in (0.0, 0.4):
                for gid in (5, 8, 12, 18):
                    kw = dict(GM_ID=gid, VDS=vds, VSB=vsb, L=L)
                    jr, jo = float(ref.look_up("ID_W", **kw)), float(ours.look_up("ID_W", **kw))
                    ar, ao = float(ref.look_up("GM_GDS", **kw)), float(ours.look_up("GM_GDS", **kw))
                    fr = float(ref.look_up("GM_CGG", **kw)) / TWO_PI
                    fo = float(ours.look_up("GM_CGG", **kw)) / TWO_PI
                    vr, vo = float(ref.look_upVGS(**kw)), float(ours.look_upVGS(**kw))
                    if not all(np.isfinite([jr, jo, ar, ao, fr, fo, vr, vo])):
                        continue
                    for key, dev in (
                        ("jd", abs(jo / jr - 1)), ("av0", abs(ao / ar - 1)),
                        ("ft", abs(fo / fr - 1)), ("vgs", abs(vo - vr)),
                    ):
                        if dev > worst[key]:
                            worst[key], where[key] = dev, kw
                    n += 1
                    vsb_covered = vsb_covered or vsb > 0

    assert n >= 48, f"only {n} comparable bias points — grid coverage too thin to be a real check"
    assert vsb_covered, "body-effect (VSB>0) slices were never exercised"
    assert worst["jd"] < 0.05, f"JD off by {worst['jd'] * 100:.1f}% at {where['jd']}"
    assert worst["av0"] < 0.05, f"intrinsic gain off by {worst['av0'] * 100:.1f}% at {where['av0']}"
    assert worst["ft"] < 0.05, f"fT off by {worst['ft'] * 100:.1f}% at {where['ft']}"
    # the pmos sign-convention guard: a reversed/raw-negative table blows VGS by hundreds of mV
    assert worst["vgs"] < 5e-3, f"VGS off by {worst['vgs'] * 1e3:.1f} mV at {where['vgs']}"
