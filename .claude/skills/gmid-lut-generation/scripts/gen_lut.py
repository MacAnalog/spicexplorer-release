"""gm/ID lookup-table generation for ngspice (skeleton, PDK-portable).

Architecture: Python outer loops over (L, VSB) tiles; ngspice runs the inner
2-D DC sweep (VGS x VDS) per tile. Tiles checkpoint to scratch; assembly
writes the .npz consumed by the gmid-sizing skill.

MANDATORY before a full run: debug_single_point() with your PDK, confirm the
device parameter handles (PARAM_MAP) against ngspice `display` output. OSDI
PSP models (IHP SG13G2) do not use builtin-MOS handle names.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


# --------------------------------------------------------------------------- #
# configuration
# --------------------------------------------------------------------------- #
@dataclass
class SweepConfig:
    name: str = "sg13_lv_nmos"
    polarity: str = "n"                      # 'n' or 'p'
    model_subckt: str = "sg13_lv_nmos"       # PDK device subckt/model name
    lib_include: str = ".lib /path/to/sg13g2/cornerMOSlv.lib mos_tt"  # EDIT
    corner: str = "NOM"
    temp_c: float = 27.0
    w_um: float = 5.0
    nfing: int = 1
    vdd: float = 1.5
    vgs: np.ndarray = field(default_factory=lambda: np.arange(0, 1.5 + 1e-9, 0.025))
    vds: np.ndarray = field(default_factory=lambda: np.arange(0, 1.5 + 1e-9, 0.025))
    vsb: np.ndarray = field(default_factory=lambda: np.arange(0, 0.8 + 1e-9, 0.1))
    lengths_um: np.ndarray = field(default_factory=lambda: np.concatenate(
        [np.arange(0.13, 0.30 + 1e-9, 0.01), np.arange(0.35, 1.00 + 1e-9, 0.05)]))
    scratch: Path = Path("/tmp/gmid_lut")
    ngspice: str = "ngspice"


# Verified-in-debug map: stored name -> list of (ngspice vector expr, weight).
# PLACEHOLDER handles below; REPLACE after debug_single_point() on your PDK.
PARAM_MAP: dict[str, list[tuple[str, float]]] = {
    "ID":  [("@n.xdut.ndev[id]",  +1.0)],
    "GM":  [("@n.xdut.ndev[gm]",  +1.0)],
    "GMB": [("@n.xdut.ndev[gmb]", +1.0)],
    "GDS": [("@n.xdut.ndev[gds]", +1.0)],
    "VT":  [("@n.xdut.ndev[vth]", +1.0)],
    # capacitances: sums of intrinsic + overlap + junction terms, model-specific
    "CGG": [("@n.xdut.ndev[cgg]", +1.0)],
    "CGS": [("@n.xdut.ndev[cgs]", -1.0)],   # sign conventions vary; verify!
    "CGD": [("@n.xdut.ndev[cgd]", -1.0)],
    "CGB": [("@n.xdut.ndev[cgb]", -1.0)],
    "CDD": [("@n.xdut.ndev[cdd]", +1.0)],
    "CSS": [("@n.xdut.ndev[css]", +1.0)],
    "CSG": [("@n.xdut.ndev[csg]", -1.0)],
    "CDG": [("@n.xdut.ndev[cdg]", -1.0)],
}
NOISE_VARS = ("STH", "SFL")  # harvested by a separate reduced-grid noise pass


def netlist_tile(cfg: SweepConfig, L_um: float, vsb: float) -> str:
    """One characterization deck: inner 2-D DC sweep over VGS x VDS."""
    sgn = 1.0 if cfg.polarity == "n" else -1.0
    saves = " ".join({expr for terms in PARAM_MAP.values() for expr, _ in terms})
    return f"""* gmid techsweep tile L={L_um}u VSB={vsb}
{cfg.lib_include}
.temp {cfg.temp_c}
.param lpar={L_um}u wpar={cfg.w_um}u
VG g 0 0
VD d 0 0
VS s 0 {-sgn*vsb}
VB b 0 0
xdut d g s b {cfg.model_subckt} W={{wpar}} L={{lpar}} ng={cfg.nfing}
.save {saves}
.control
dc VG 0 {sgn*cfg.vgs[-1]} {sgn*(cfg.vgs[1]-cfg.vgs[0])} VD 0 {sgn*cfg.vds[-1]} {sgn*(cfg.vds[1]-cfg.vds[0])}
wrdata {cfg.scratch}/tile_L{L_um:.3f}_VSB{vsb:.2f}.txt {saves.replace(' ', ' ')}
quit
.endc
.end
"""


def debug_single_point(cfg: SweepConfig) -> None:
    """Run one bias point, list ALL vectors, print harvested params.
    Use this to fix PARAM_MAP before any full sweep."""
    cfg.scratch.mkdir(parents=True, exist_ok=True)
    deck = netlist_tile(cfg, float(cfg.lengths_um[0]), 0.0).replace(
        ".control", ".control\nop\ndisplay\n* inspect handles above, then:")
    p = cfg.scratch / "debug.sp"
    p.write_text(deck)
    print(subprocess.run([cfg.ngspice, "-b", str(p)],
                         capture_output=True, text=True).stdout)


def run_sweep(cfg: SweepConfig) -> None:
    cfg.scratch.mkdir(parents=True, exist_ok=True)
    for L in cfg.lengths_um:
        for vsb in cfg.vsb:
            out = cfg.scratch / f"tile_L{L:.3f}_VSB{vsb:.2f}.txt"
            if out.exists():
                continue                       # restartable
            deck = cfg.scratch / "tile.sp"
            deck.write_text(netlist_tile(cfg, float(L), float(vsb)))
            t0 = time.time()
            r = subprocess.run([cfg.ngspice, "-b", str(deck)],
                               capture_output=True, text=True)
            if r.returncode != 0 or not out.exists():
                raise RuntimeError(f"tile L={L} VSB={vsb} failed:\n{r.stderr[-2000:]}")
            print(f"tile L={L:.3f} VSB={vsb:.2f}  {time.time()-t0:.1f}s")


def assemble(cfg: SweepConfig, out_npz: Path) -> None:
    """Parse wrdata tiles into 4-D arrays [L, VGS, VDS, VSB] and write .npz.
    TODO: implement the wrdata column parsing against the verified PARAM_MAP
    (column order follows the .save list; confirm in the debug run)."""
    shape = (len(cfg.lengths_um), len(cfg.vgs), len(cfg.vds), len(cfg.vsb))
    arrays = {k: np.full(shape, np.nan) for k in PARAM_MAP}
    # ... fill arrays per tile here ...
    np.savez_compressed(
        out_npz, L=cfg.lengths_um, VGS=cfg.vgs, VDS=cfg.vds, VSB=cfg.vsb,
        W=cfg.w_um, NFING=cfg.nfing, CORNER=cfg.corner, TEMP=273.15 + cfg.temp_c,
        INFO=f"{cfg.name} ngspice techsweep {time.strftime('%Y-%m-%d')}",
        **arrays)
    Path(str(out_npz) + ".provenance.json").write_text(json.dumps({
        "config": {k: (v.tolist() if isinstance(v, np.ndarray) else str(v))
                   for k, v in vars(cfg).items()},
        "param_map": {k: v for k, v in PARAM_MAP.items()}}, indent=2))


if __name__ == "__main__":
    cfg = SweepConfig()
    debug_single_point(cfg)   # ALWAYS first; then comment out and run_sweep(cfg)
