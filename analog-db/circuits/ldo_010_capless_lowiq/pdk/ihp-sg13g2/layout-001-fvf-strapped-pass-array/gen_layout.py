#!/usr/bin/env python3
"""Parameterized gdsfactory layout of ``ldo_ihp_capless`` (IHP SG13G2, sg13_lv devices).

Generator contract (``spicexplorer_layout.gen``): ``build(params, sizing=None) -> Component``,
``write_lvs_reference(params, sizing, out)``, ``power_budgets(params, sizing)``.  It needs the
interpreter that has gdsfactory + ihp-gdsfactory (``$LDO_GF_PYTHON``, default
``~/miniconda3/envs/ai_env/bin/python``; see this entry's README) — never the analog-db venv,
which has neither.  ``analog-db layout run --step generate`` invokes this file with the CLI's own
interpreter, so the module re-execs itself under ``$LDO_GF_PYTHON`` when gdsfactory is missing,
rather than making the caller know which python draws.

**Vendored** from an agent-first design repo @ ``40cad45`` (``layout/gen_ldo.py``), byte for
byte apart from that re-exec block and this note.  Sizes still come from the certified netlist
through ``netlist_ref``, which now reads the entry's OWN ``pdk/ihp-sg13g2/netlist.spice`` and
``sizing.yaml`` one directory up: the same 24 MOS + 24 passive cards with the same values, in a
different card order (the lowered netlist is emitted sorted).  Order is not a dependency — every
device is looked up by name (``MD`` / ``PC`` are name-keyed) and the resistor chains sort
themselves — and ``lvs_reference()`` from either file is the same set of lines.

**Second drawing.**  The first (`experiments/005-layout`) was DRC-0 and LVS-matched and is
rejected on four counts, all fixed here and all planned in `layout/ldo_ihp_capless/PLAN.md`:

* **B1** — the 10 mA path was 12–28x over the process metal limit.  The load current now never
  touches a Metal1 conductor wider than one pass-array column: TopMetal1 straps (`pwr_w`), Metal5
  landing pads stitched with `pwr_stitch` TopVia1, `pwr_riser_vias` cuts per Via2/3/4 level, a
  Metal2 comb over the pass array, and the certified `ng` fingers so a shared diffusion
  column carries 0.26 mA against a 0.36 mA allowance (§3 of the PLAN).
* **m3** — matched pairs are common-centroid or same-row-same-orientation *by class*, with tied
  dummies at both ends of every group, and every well island carries a **closed** guard ring
  instead of periodic point taps.
* **M7** — the LVS reference is derived from the certified netlist (`netlist_ref.py`), not
  from a device table in this file.  This module no longer carries one.
* **M8** — `Builder.stub_clear` (the Metal1 obstacle map) has its own unit test,
  `test_builder.py`, which fails without it.

Floorplan (all y derived from live device bounding boxes; see the PLAN for the sketch):

    vdd TopMetal1 strap  (top edge)                                  <- vdd pin
    XMP island: nwell + ntap ring, the certified card's `ng` fingers, Metal2 combs
    vdd Metal1 rail
    row B: [nwell island "quiet": bias_p_group | ea_in_pair]  [nwell island "fvf": XMC XMCP XMD]
    channel: one Metal1 track per internal net, every vertical is Metal2
    row A: [XM5] [ea_nmos_load] [fvf_fold_n] [bias_n_group]           (one ptap ring)
    vss Metal1 rail
    passive band: [XR1/XR2 common centroid + XRB]   [XCC XCFF]   [XCOUT 2x2 array]
    vss Metal1 rail (bottom edge)                                    <- vss pin
    vout TopMetal1 strap down the right edge                         <- vout pin

Routing discipline: device straps, channel tracks and rails are Metal1 (horizontal); every
inter-row connection is a Metal2 vertical with a Via1 pad at each end, at an x unique to that
terminal, and no Metal1 stub may cross a foreign net's Metal1 (`stub_clear`).  Guard-ring metal is
claimed in the same obstacle map, so a stub can never walk out through a ring.

Sizes come from the certified netlist + the sizing record; they are never retyped here.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

# --- the drawing interpreter ------------------------------------------------------------------
# gdsfactory + ihp-gdsfactory live in their own environment; `analog-db layout run` launches this
# script with `sys.executable`, which is whichever interpreter ran the CLI. Re-exec once under
# $LDO_GF_PYTHON rather than failing with an ImportError the caller has to decode. The guard
# variable makes a wrong $LDO_GF_PYTHON say so instead of looping forever.
try:
    import gdsfactory as _gf_probe  # noqa: F401
except ModuleNotFoundError:
    _GF = os.environ.get("LDO_GF_PYTHON", str(Path.home() / "miniconda3/envs/ai_env/bin/python"))
    if os.environ.get("LDO_GF_REEXEC") or not Path(_GF).is_file():
        raise SystemExit(
            f"gen_layout.py needs gdsfactory + ihp-gdsfactory. Tried {_GF!r}"
            + (" and it still cannot import gdsfactory."
               if os.environ.get("LDO_GF_REEXEC") else ", which does not exist.")
            + " Point $LDO_GF_PYTHON at an interpreter that has them (README, 'Environment')."
        ) from None
    os.execve(_GF, [_GF, str(Path(__file__).resolve()), *sys.argv[1:]],
              {**os.environ, "LDO_GF_REEXEC": "1"})

import gdsfactory as gf
from ihp import PDK
from ihp import cells as C
from ihp.cells.fet_transistors import _mos_core

sys.path.insert(0, str(Path(__file__).resolve().parent))
import netlist_ref as NR  # noqa: E402
from router import ObstacleMap  # noqa: E402

PDK.activate()

CELL = NR.CELL
GRID = 0.005
VIA = 0.19       # V1.a / Vn.a exact
VIA_SP = 0.24    # Vn.b + grid slack
VIA_ENC = 0.06   # Mn.c
TVIA = 0.42      # TV1.a exact
TVIA_SP = 0.44   # TV1.b
TVIA_ENC_M5 = 0.42   # TV1.d (Metal5 enclosure)
TVIA_ENC_TM1 = 0.45  # TM1.c
VPAD = 0.38      # via pad (< 0.39 "wide line", so the 0.21 space rule applies)
STRAP = 0.5      # S/D strap centre offset from the active edge
GATE = 1.5       # gate bar centre offset from the active edge
GPAD = 0.5       # gate bar height — the DEFAULT of `LayoutParams.gpad` (F11); see there
CONT = 0.16      # Cnt.a exact
MIM_BIAS = 0.72  # gdsfactory grows the MIM box by 0.36/side vs the cmim() args
W_M1 = 0.2
W_M2 = 0.2
TM1_MIN_W = 1.64   # TM1.a
TM1_MIN_SP = 1.64  # TM1.b
COL_M1_W = 0.16    # the mos cell's own S/D column Metal1 width (measured from _mos_core)

_um, _count = NR.um, NR.count


def _val(expr: str, sz: dict) -> float:
    """A card parameter in micrometres (`NR.value` is in the file's own units, i.e. metres)."""
    return NR.value(expr, sz) * 1e6


SIZING: dict[str, object] = NR.load_sizing()


def _s(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


@dataclasses.dataclass(frozen=True)
class LayoutParams:
    """Free layout constants (um / counts) — the layout-optimizer search space (PLAN §5)."""

    dev_gap: float = 3.2       # x gap between devices in a row
    grp_gap: float = 2.0       # extra gap between matching groups
    track_pitch: float = 0.7   # channel Metal1 track pitch (0.38 pads -> 0.32 space)
    ch_margin: float = 0.9     # clearance from the gate/drain bars to the first track
    rail_w: float = 0.8        # vdd / vss Metal1 rail width (Iq only: 0.037 mA worst)
    rail_gap: float = 1.6      # active edge -> rail centre
    ring_w: float = 0.6        # guard-ring width (ntap / ptap)
    ring_gap: float = 1.4      # device/pad bbox -> guard ring inner edge
    isl_gap: float = 2.0       # Activ gap between two well islands (NW.b 0.62 + Act.b 0.21)
    n_dummy: int = 1           # dummy devices at each end of a matched group
    pwr_w: float = 4.0         # TopMetal1 power-strap width (TM1.a floor is 1.64)
    pwr_stitch: int = 12       # TopVia1 cuts per Metal5 -> TopMetal1 stitch
    pwr_riser_vias: int = 48   # Via2/3/4 cuts per riser level
    pwr_band_w: float = 6.0    # Metal2 comb spine / riser pad width
    col_vias: int = 2          # Via1 per pass-array S/D column
    mim_gap: float = 3.0       # gap between MIM units
    res_pitch: float = 2.0     # serpentine segment pitch (rhigh cell is 0.9 wide)
    blk_gap: float = 6.0       # transistor stack -> passive band
    gpad: float = 0.5          # gate-bar height (Metal1 + GatPoly): sets every gate's own C
    vss_ret_w: float = 3.0     # bottom vss rail + its two edge risers (brief's 17 Ohm budget)


BOUNDS: dict[str, tuple[float, float]] = {
    "dev_gap": (3.0, 6.0), "grp_gap": (0.0, 8.0), "track_pitch": (0.65, 1.2),
    "ch_margin": (0.8, 2.0), "rail_w": (0.5, 1.4), "rail_gap": (1.4, 2.5),
    "ring_w": (0.5, 1.5), "ring_gap": (0.6, 3.0), "isl_gap": (1.3, 6.0), "n_dummy": (1, 2),
    "pwr_w": (1.64, 8.0), "pwr_stitch": (8, 24), "pwr_riser_vias": (28, 72),
    "pwr_band_w": (5.1, 12.0), "col_vias": (1, 4),
    "mim_gap": (2.5, 8.0), "res_pitch": (1.9, 3.0),
    "blk_gap": (4.0, 15.0), "gpad": (0.34, 0.6), "vss_ret_w": (0.8, 6.0),
}

# review-003 **F11**: `tap_pitch` was in the search space and moved nothing (byte-identical GDS
# at both ends of its range), while `isl_gap` moved the floorplan and was in neither PLAN nor the
# reviewer's list.  A knob is a `LayoutParams` field AND a `BOUNDS` entry, or it is neither.
assert set(BOUNDS) == {f.name for f in dataclasses.fields(LayoutParams)}, (
    "BOUNDS and LayoutParams disagree: "
    f"{sorted(set(BOUNDS) ^ {f.name for f in dataclasses.fields(LayoutParams)})}")

_STACK = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5", "TopMetal1"]
_VIA = {  # bottom layer -> (via layer, size, space, min enclosure)
    "Metal1": ("Via1drawing", VIA, VIA_SP, VIA_ENC),
    "Metal2": ("Via2drawing", VIA, VIA_SP, VIA_ENC),
    "Metal3": ("Via3drawing", VIA, VIA_SP, VIA_ENC),
    "Metal4": ("Via4drawing", VIA, VIA_SP, VIA_ENC),
    "Metal5": ("TopVia1drawing", TVIA, TVIA_SP, TVIA_ENC_M5),
}

# ---------------------------------------------------------------- placement ----
# A row is a list of GROUPS; a group is a list of SLOTS.  One slot = one placed instance:
# (card name, fraction of that card's W, fingers).  A matching pattern draws unit devices, so the
# **certified netlist names each unit** (`XM1A`/`XM1B`, review F19): the fraction is 1.0 for every
# matched member and the split is a certified device parameter, not a layout liberty the compare
# happens to tolerate.  `--combine_devices` still folds the pair, which is why LVS never saw it.
# Patterns are the brief's (§6), by measured headroom.
Slot = tuple[str, float, int]
Group = tuple[str, str, list[Slot]]

# row A — NMOS, sources on the vss rail.  Left to right: stage 2, the EA load pair, the FVF folds,
# then the bias group.  The bias group is RIGHTMOST on purpose: XMS drives `gate`, whose 29.3 fF
# budget is 97 % spent, and `nbias`/`pbias` (which then run the cell's length) have no bound.
ROW_A: list[Group] = [
    ("ea_stage2", "any", [("XM5", 1.0, 1)]),
    ("ea_nmos_load", "common_centroid",
     [("XM3A", 1.0, 1), ("XM4A", 1.0, 1), ("XM4B", 1.0, 1), ("XM3B", 1.0, 1)]),
    ("fvf_fold_n", "same_row_same_orientation", [("XMA", 1.0, 1), ("XMB", 1.0, 1)]),
    ("bias_n_group", "common_centroid",
     [("XMSA", 1.0, 1), ("XMB1A", 1.0, 1), ("XMB0A", 1.0, 1),
      ("XMB0B", 1.0, 1), ("XMB1B", 1.0, 1), ("XMSB", 1.0, 1)]),
]
# row B — PMOS, in two nwell islands (brief §7): "quiet" and "fvf", both tied to vdd.
# review-003 **F5**: `ea_in_pair` comes FIRST, i.e. leftmost, nearest the divider block.  `fb`
# lands on XM1's gates, and with the pair second the track had to run 107 um — 53 % of the cell
# width, into the right half PLAN §6 forbids.  `bias_p_group` has 7.16 sigma of headroom and no
# routing constraint, so it is the group that takes the long trip.
ROW_B_QUIET: list[Group] = [
    ("ea_in_pair", "common_centroid",
     [("XM1A", 1.0, 1), ("XM2A", 1.0, 1), ("XM2B", 1.0, 1), ("XM1B", 1.0, 1)]),
    # XMT sits between XMBP and XM6: a linear gradient then WEAKENS XMT relative to the diode,
    # and brief §6 measures the S7 step only on the side that STRENGTHENS it.
    ("bias_p_group", "same_row_same_orientation",
     [("XMBP", 1.0, 1), ("XMT", 1.0, 1), ("XM6", 1.0, 1)]),
]
ROW_B_FVF: list[Group] = [
    ("fvf_ctrl", "any", [("XMC", 1.0, 1)]),
    ("fvf_fold_p", "same_row_same_orientation", [("XMCP", 1.0, 1), ("XMD", 1.0, 1)]),
]

# channel-1 tracks (Metal1, bottom to top); vdd/vss are rails, not tracks.  `gate` is the TOP
# track, immediately under the vout bus: brief §3 measures gate-to-vout at 10-24x cheaper than
# gate-to-rail.  `fb` is kept low and far from it.
TRACKS = ["fb", "vref", "lp_brk", "ea_n", "ea_o1", "ea_out", "ea_tail",
          "nbias", "pbias", "x1", "y", "vout", "gate"]

#: Channel nets whose track is NOT Metal1.  `gate` is the only one (review-003 **F3**): 34.5 fF
#: of its 47.5 fF sits on rails, and the biggest single contributor is the track itself — a
#: ~52 um Metal1 run from XMD / XMSA / XMSB at the right of the cell to the pass gate at x ~ 45,
#: 0.6 um above the substrate.  On Metal3 the same run is ~2.6 um up, and the layer also lets the
#: net hop the pass array's Metal2 comb without the hard-coded `to_track_m3` the review flagged
#: (F7) — the comb is a Metal2 obstacle, so a Metal3 column is simply not asked about it.
TRACK_LAYER = {"gate": "Metal3"}
# Side of the pin-purpose square drawn under every port label (review-004 F25). It has to
# fit inside the narrowest net a label lands on -- the 0.3 um Metal3 gate track -- and it is
# not a knob: no floorplan decision depends on it and the PDK has no rule on the purpose.
PIN_SIDE = 0.2
#: Width of a non-Metal1 track and of the column that reaches it.
W_TRK_UP = 0.3


@dataclasses.dataclass
class Dev:
    name: str
    kind: str
    ref: object
    cols: list[float]
    gates: list[float]
    ax0: float
    ax1: float
    ay0: float
    ay1: float
    wf: float
    term: dict[str, tuple[float, float]] = dataclasses.field(default_factory=dict)


class Builder(ObstacleMap):
    """The drawing side; the Metal1 obstacle map and the column allocator come from
    :class:`router.ObstacleMap`, which `test_builder.py` exercises directly (M8)."""

    def __init__(self, p: LayoutParams, sz: dict[str, object]):
        super().__init__()
        self.p, self.sz = p, sz
        self.c = gf.Component(CELL)
        self.track_y: dict[str, float] = {}
        self.track_pts: dict[str, list[float]] = {t: [] for t in TRACKS}
        self.rail_y: dict[str, float] = {}
        self.ring_m1: dict[str, tuple[float, float, float, float]] = {}
        self.dummies: list[NR.Dummy] = []
        self.budgets: list[dict] = []   # power-path segments, for the current-density stage

    # -- primitives --------------------------------------------------------
    def rect(self, layer: str, x0: float, y0: float, x1: float, y1: float) -> None:
        x0, x1 = sorted((_s(x0), _s(x1)))
        y0, y1 = sorted((_s(y0), _s(y1)))
        if x1 - x0 < GRID / 2 or y1 - y0 < GRID / 2:
            return
        self.c.add_polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer=layer)

    def h(self, layer: str, y: float, x0: float, x1: float, w: float) -> None:
        self.rect(layer, min(x0, x1) - w / 2, y - w / 2, max(x0, x1) + w / 2, y + w / 2)

    def v(self, layer: str, x: float, y0: float, y1: float, w: float) -> None:
        self.rect(layer, x - w / 2, min(y0, y1) - w / 2, x + w / 2, max(y0, y1) + w / 2)

    def m1h(self, y, x0, x1, w=W_M1):
        self.h("Metal1drawing", y, x0, x1, w)

    def m1v(self, x, y0, y1, w=W_M1):
        self.v("Metal1drawing", x, y0, y1, w)

    def vstack(self, x: float, y: float, bot: str, top: str, size: float = VPAD) -> None:
        """Small square via stack: as many cuts as fit in ``size`` (<= 3x3)."""
        i0, i1 = _STACK.index(bot), _STACK.index(top)
        for i in range(i0, i1 + 1):
            lay = _STACK[i]
            s = max(size, TM1_MIN_W) if lay == "TopMetal1" else size
            self.rect(lay + "drawing", x - s / 2, y - s / 2, x + s / 2, y + s / 2)
        for i in range(i0, i1):
            vl, vs, vsp, enc = _VIA[_STACK[i]]
            avail = size - 2 * enc
            n = max(1, min(3, int((avail + vsp + 1e-9) // (vs + vsp))))
            span = n * vs + (n - 1) * vsp
            for a in range(n):
                for b in range(n):
                    xx = x - span / 2 + a * (vs + vsp)
                    yy = y - span / 2 + b * (vs + vsp)
                    self.rect(vl, xx, yy, xx + vs, yy + vs)

    def via_row(self, layer_bot: str, xc: float, yc: float, n: int, rows: int = 1) -> tuple[float, float]:
        """``n`` cuts of ``layer_bot``'s via, laid out in ``rows`` rows centred on (xc, yc).
        Returns the (x, y) span the enclosing metal must cover.  This is the count-driven via
        array the power path needs; ``vstack``'s 3x3 cap cannot carry 10 mA."""
        vl, vs, vsp, enc = _VIA[layer_bot]
        rows = max(1, rows)
        per = -(-n // rows)
        spx = per * vs + (per - 1) * vsp
        spy = rows * vs + (rows - 1) * vsp
        k = 0
        for r in range(rows):
            for i in range(per):
                if k >= n:
                    break
                k += 1
                x0 = xc - spx / 2 + i * (vs + vsp)
                y0 = yc - spy / 2 + r * (vs + vsp)
                self.rect(vl, x0, y0, x0 + vs, y0 + vs)
        return spx + 2 * enc, spy + 2 * enc

    def label(self, net: str, x: float, y: float, layer: str = "Metal1text") -> None:
        """A port: the text on the layer's LABEL purpose plus a square on its PIN purpose.

        review-004 **F25** and the platform's own probe (`spicexplorer-platform @7d55218`): a
        text alone is *not* a pin.  kpex emits a ``[Pin]`` node — and names the mesh node after
        the net rather than after a polygon it picks — only when the label text sits inside a
        polygon on the same layer's **pin purpose** (`<metal>/2`, e.g. Metal1 8/2, TopMetal1
        126/2).  Without it the RC stitch anchors each port on an arbitrary node of the net
        (measured: a proxy 100 um from where the port is drawn), so every port-referred series-R
        number is referred to the wrong place.  The square is geometry only: the pin purpose is
        not a conducting layer, so LVS connectivity and the extracted capacitance do not move.
        """
        self.c.add_label(text=net, position=(_s(x), _s(y)), layer=layer)
        base = layer[:-4] if layer.endswith("text") else layer
        h = PIN_SIDE / 2
        self.rect(f"{base}pin", _s(x - h), _s(y - h), _s(x + h), _s(y + h))

    def vert(self, net: str, x: float, y0: float, y1: float) -> None:
        """Metal2 vertical between two Via1 pads (both drawn)."""
        self.vstack(x, y0, "Metal1", "Metal2")
        self.vstack(x, y1, "Metal1", "Metal2")
        self.v("Metal2drawing", x, y0, y1, W_M2)
        self.claim_vertical(net, x, y0, y1, "Metal2")

    def to_track(self, net: str, x: float, y: float, step: float = 0.6,
                 reserve: float | None = None) -> float:
        """Connect the Metal1 point (x, y) to the channel track / rail of ``net``.

        The column runs on ``TRACK_LAYER[net]`` (Metal2 unless the net asks for higher, F3) and is
        allocated against the obstacles **of that layer only**, so a Metal3 net crosses a Metal2
        comb without a special case (F7).  ``reserve`` forces the column to a pre-reserved x
        (F6: the two halves of a common-centroid pair get mirrored columns, not first-come ones).
        """
        yt = self.rail_y.get(net, self.track_y.get(net))
        if yt is None:
            raise KeyError(f"no track or rail for net {net}")
        layer = TRACK_LAYER.get(net, "Metal2")
        if reserve is not None and self.column_free(net, _s(reserve), min(y, yt), max(y, yt),
                                                    layer) and self.stub_clear(net, y, x, reserve):
            xx = _s(reserve)
        else:
            xx = self.alloc(net, x, y, yt, step, layer=layer)
        if xx != _s(x):
            self.m1h(y, x, xx)
            self.m1_claim(net, y, x, xx)
        if layer == "Metal2":
            self.vert(net, xx, y, yt)
        else:
            # the track itself is on `layer`, so only the terminal end needs a via stack
            self.vstack(xx, y, "Metal1", layer, VPAD)
            self.v(layer + "drawing", xx, y, yt, W_TRK_UP)
            self.claim_vertical(net, xx, y, yt, layer)
        self.track_pts.setdefault(net, []).append(xx)  # type: ignore[arg-type]
        return xx

    # -- transistor --------------------------------------------------------
    def mos(self, name: str, w: float, l: float, nf: int, pmos: bool, x0: float, y_act: float,
            *, d_top: bool, g_top: bool, gate_gap: float | None = None) -> Dev:
        """Place one lv MOS with its active's left edge at x0 and bottom at y_act."""
        cell = _mos_core(width=w, length=l, nf=nf, is_pmos=pmos, is_hv=False)
        ref = self.c << cell
        sx, sy = ref.ports["S"].center
        dx = ref.ports["D"].center[0]
        gx = ref.ports["G"].center[0]
        pitch = dx - sx
        wf = w / nf
        cols = [sx + k * pitch for k in range(nf + 1)]
        gates = [gx + k * pitch for k in range(nf)]
        ax0, ax1 = min(cols) - 0.15, max(cols) + 0.15
        ay0 = sy - wf / 2
        ddx, ddy = x0 - ax0, y_act - ay0
        ref.dmovex(_s(ddx))
        ref.dmovey(_s(ddy))
        cols = [_s(v + ddx) for v in cols]
        gates = [_s(v + ddx) for v in gates]
        ax0, ax1 = _s(ax0 + ddx), _s(ax1 + ddx)
        ay0, ay1 = _s(y_act), _s(y_act + wf)
        d = Dev(name, "p" if pmos else "n", ref, cols, gates, ax0, ax1, ay0, ay1, wf)
        # gate: poly tabs -> poly bar -> contacts -> Metal1 bar
        tab = min(self.p.gpad, l)
        gg = GATE if gate_gap is None else gate_gap
        y_g = (ay1 + gg) if g_top else (ay0 - gg)
        py = ay1 if g_top else ay0
        for gxx in gates:
            self.rect("GatPolydrawing", gxx - tab / 2, py, gxx + tab / 2, y_g)
        gb0, gb1 = min(gates) - 0.25, max(gates) + 0.25
        self.rect("GatPolydrawing", gb0, y_g - self.p.gpad / 2, gb1, y_g + self.p.gpad / 2)
        self.rect("Metal1drawing", gb0, y_g - self.p.gpad / 2, gb1, y_g + self.p.gpad / 2)
        for gxx in gates:
            self.rect("Contdrawing", gxx - CONT / 2, y_g - CONT / 2, gxx + CONT / 2, y_g + CONT / 2)
        d.term["_gate_bar"] = (y_g, gb0, gb1)  # type: ignore[assignment]
        self.m1_claim(f"@g:{name}", y_g, gb0, gb1, self.p.gpad)
        return d

    def strap(self, d: Dev, which: str, top: bool, ext_to: float | None = None,
              net: str | None = None) -> float:
        """Metal1 bar joining the S (even) or D (odd) columns outside the active."""
        grp = d.cols[0::2] if which == "S" else d.cols[1::2]
        y = d.ay1 + STRAP if top else d.ay0 - STRAP
        for xx in grp:
            self.m1v(xx, d.ay1 if top else d.ay0, y)
        x0, x1 = min(grp), max(grp)
        if ext_to is not None:
            x0, x1 = min(x0, ext_to), max(x1, ext_to)
        self.m1h(y, x0, x1)
        if net:
            self.m1_claim(net, y, x0, x1)
        return y

    def columns_to_rail(self, d: Dev, which: str, y_rail: float) -> None:
        grp = d.cols[0::2] if which == "S" else d.cols[1::2]
        for xx in grp:
            self.m1v(xx, d.ay0 if y_rail < d.ay0 else d.ay1, y_rail)

    def gate_pad(self, d: Dev, x: float, net: str) -> float:
        y_g, gb0, gb1 = d.term["_gate_bar"]  # type: ignore[misc]
        x0, x1 = min(gb0, x - VPAD / 2), max(gb1, x + VPAD / 2)
        self.rect("Metal1drawing", x0, y_g - self.p.gpad / 2, x1, y_g + self.p.gpad / 2)
        self.m1_retag(f"@g:{d.name}", net)
        self.m1_claim(net, y_g, x0, x1, self.p.gpad)
        return y_g

    def dummy(self, name: str, w: float, l: float, pmos: bool, x0: float, y_act: float,
              rail: str, y_rail: float) -> Dev:
        """A tied-off dummy device: gate bar on the RAIL side, every column shorted to the rail.

        It is a real extracted device (measured: the IHP LVS deck does not purge a fully shorted
        MOS), so it is declared in the LVS reference -- see `netlist_ref.lvs_reference`, which
        asserts all four terminals are on one rail."""
        d = self.mos(name, w, l, 1, pmos, x0, y_act, d_top=not (y_rail < y_act), g_top=(y_rail > y_act))
        y_g, gb0, gb1 = d.term["_gate_bar"]  # type: ignore[misc]
        # ONE Metal1 blanket from the rail over the whole device: source, drain, gate bar and the
        # rail are all the same net, and separate 0.2 um ties left a 0.09 um notch against the
        # gate bar that M1.b (0.21 um) rejects.
        bx0, bx1 = _s(min(min(d.cols), gb0) - 0.16), _s(max(max(d.cols), gb1) + 0.16)
        by0 = _s(min(y_rail, d.ay0, y_g - self.p.gpad / 2))
        by1 = _s(max(y_rail, d.ay1, y_g + self.p.gpad / 2))
        self.rect("Metal1drawing", bx0, by0, bx1, by1)
        self.m1_retag(f"@g:{name}", rail)
        self.m1_claim_box(rail, bx0, by0, bx1, by1)
        self.dummies.append(NR.Dummy(name, "p" if pmos else "n", rail, w, l))
        return d

    # -- guard rings -------------------------------------------------------
    def ring(self, kind: str, net: str, x0: float, y0: float, x1: float, y1: float,
             gap: float = 0.14) -> tuple[float, float, float, float]:
        """A CLOSED guard ring around the box: a continuous Activ/Metal1 frame with a uniform
        contact row, the implant as a frame and (for an n-well ring) the well as a FILLED rect
        that merges with the devices' own wells.

        Drawn here rather than with `ihp.cells.guard_ring`, whose corner contact arrays violate
        Cnt.b (min. Cont space 0.18 um) at every corner — measured on a standalone ring at seven
        width/spacing combinations, 2-4 hits each.  Placing the corner contact ON the corner and
        starting each side one pitch away makes every neighbour pair axis-aligned and >= one
        pitch apart.

        The ring's Metal1 is claimed in the obstacle map, so a routing stub can never walk out
        through it.  Returns the outer implant/well bbox.
        """
        w = self.p.ring_w
        ix0, iy0, ix1, iy1 = _s(x0 - gap), _s(y0 - gap), _s(x1 + gap), _s(y1 + gap)
        ox0, oy0, ox1, oy1 = _s(ix0 - w), _s(iy0 - w), _s(ix1 + w), _s(iy1 + w)
        frame = [(ox0, oy0, ox1, iy0), (ox0, iy1, ox1, oy1),
                 (ox0, iy0, ix0, iy1), (ix1, iy0, ox1, iy1)]
        imp = "pSDdrawing" if kind == "psub" else "nSDdrawing"
        for (a, b_, c, d) in frame:
            self.rect("Activdrawing", a, b_, c, d)
            self.rect("Metal1drawing", a, b_, c, d)
            self.rect(imp, a - 0.1, b_ - 0.1, c + 0.1, d + 0.1)
        if kind == "nwell":
            # filled, so the island's devices share one well with the ring
            self.rect("NWelldrawing", ox0 - 0.31, oy0 - 0.31, ox1 + 0.31, oy1 + 0.31)
        # contacts: one on each corner, then one pitch in along every side
        cx0, cy0, cx1, cy1 = _s(ix0 - w / 2), _s(iy0 - w / 2), _s(ix1 + w / 2), _s(iy1 + w / 2)
        pts: list[tuple[float, float]] = [(cx0, cy0), (cx1, cy0), (cx0, cy1), (cx1, cy1)]
        pitch = CONT + 0.20
        n_x = max(0, int((cx1 - cx0) / pitch) - 1)
        n_y = max(0, int((cy1 - cy0) / pitch) - 1)
        step_x = (cx1 - cx0) / (n_x + 1) if n_x else 0.0
        step_y = (cy1 - cy0) / (n_y + 1) if n_y else 0.0
        for i in range(1, n_x + 1):
            pts += [(_s(cx0 + i * step_x), cy0), (_s(cx0 + i * step_x), cy1)]
        for i in range(1, n_y + 1):
            pts += [(cx0, _s(cy0 + i * step_y)), (cx1, _s(cy0 + i * step_y))]
        for (px, py) in pts:
            self.rect("Contdrawing", px - CONT / 2, py - CONT / 2, px + CONT / 2, py + CONT / 2)
        for seg in ((cy0, ox0, ox1), (cy1, ox0, ox1)):
            self.m1_claim(net, seg[0], seg[1], seg[2], w)
        for x in (cx0, cx1):
            self.m1_claim_box(net, x - w / 2, oy0, x + w / 2, oy1)
        self.ring_m1[net] = (cx0, cy0, cx1, cy1)
        return (_s(ox0 - 0.31), _s(oy0 - 0.31), _s(ox1 + 0.31), _s(oy1 + 0.31))

    # -- passives ----------------------------------------------------------
    def serpentine(self, w: float, l_total: float, segs: int, x0: float, y0: float,
                   pitch: float | None = None) -> tuple[tuple[float, float], tuple[float, float],
                                                        list[float], tuple[float, float]]:
        """``segs`` vertical rhigh segments joined top/bottom by Metal1; returns the two end pads,
        the segment x list and the two port y's (bottom, top).  With ``segs`` even both ends come
        out at the bottom.

        The port y's are returned so the caller can CLAIM every segment's Metal1 end pads: a
        routing stub that walks along an unclaimed port row taps the chain in the middle and the
        string extracts as several resistors (measured on the divider in round 2, and again on
        XRB at `res_pitch` = 3.0 in the fix round)."""
        pitch = pitch or self.p.res_pitch
        seg = _s(l_total / segs)
        cell = C.rhigh(dy=seg, dx=w)
        ends = []
        xs = []
        for i in range(segs):
            ref = self.c << cell
            b = ref.bbox()
            ref.dmovex(_s(x0 + i * pitch - b.left))
            ref.dmovey(_s(y0 - b.bottom))
            p1, p2 = ref.ports["P1"].center, ref.ports["P2"].center
            ends.append((p1, p2))
            xs.append(_s(p1[0]))
        for i in range(segs - 1):
            top, bot = ends[i][0], ends[i][1]
            ntop, nbot = ends[i + 1][0], ends[i + 1][1]
            if i % 2 == 0:
                self.m1h(top[1], top[0], ntop[0], 0.3)
            else:
                self.m1h(bot[1], bot[0], nbot[0], 0.3)
        first = ends[0][1]
        last = ends[-1][1] if segs % 2 == 0 else ends[-1][0]
        return first, last, xs, (_s(ends[0][1][1]), _s(ends[0][0][1]))

    def mim(self, unit: float, x0: float, y0: float, mirror: bool = False,
            top_to: float | None = None, escape: float = 0.0) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float, float, float]]:
        """One MIM unit, Metal5 plate lower-left at (x0, y0).

        Bottom (Metal5) plate pad on the LEFT and top plate strap to the RIGHT -- ONE
        plate-connection side, so a unit array has one bus per terminal.  ``mirror`` swaps the two
        sides, which is what makes the XCOUT 2x2 array a common centroid about a central top-plate
        spine; ``top_to`` extends the top-plate strap to that x (the spine)."""
        cell = C.cmim(width=unit - MIM_BIAS, length=unit - MIM_BIAS)
        ref = self.c << cell
        b = ref.bbox()
        ref.dmovex(_s(x0 - b.left))
        ref.dmovey(_s(y0 - b.bottom))
        b = ref.bbox()
        yc = _s((b.bottom + b.top) / 2)
        sgn = -1.0 if not mirror else 1.0
        xb = _s((b.left - 1.2) if not mirror else (b.right + 1.2))
        self.vstack(xb, yc, "Metal1", "Metal5", 1.3)   # Metal1, so a shifted stub still lands
        self.h("Metal5drawing", yc, xb, (b.left + 0.3) if not mirror else (b.right - 0.3), 0.6)
        xt = _s((b.right + 2.4) if not mirror else (b.left - 2.4))
        if top_to is not None:
            xt = _s(top_to)
        self.vstack(xt, yc, "Metal1", "TopMetal1", 1.3)
        self.h("TopMetal1drawing", yc, ref.ports["PLUS"].center[0], xt, TM1_MIN_W)
        del sgn
        # The plate pad carries its own 1.3 um Metal1/Metal2 stack and a 3x3 Via1 array; claim it
        # so no routing pad lands beside it (three rounds of V1.a/V1.b/M1.b/M2.b came from that),
        # and hand the caller a Metal1 arm `escape` um clear of it to route from.
        for xp in (xb, xt):
            self.m1_claim_box(f"@mim{len(self.m1_rows)}", xp - 0.85, yc - 0.85, xp + 0.85, yc + 0.85)
        if escape > 0:
            # INWARD, under the plate: outward runs into the cell edge (round 7 shorted
            # ea_o1/fb/vss on the left-edge vss strap); under a Metal5 plate the Metal1 is free
            xb_e = _s(xb + (-escape if mirror else escape))
            xt_e = _s(xt + (escape if mirror else -escape))
            self.m1h(yc, xb, xb_e, 0.4)
            self.m1h(yc, xt, xt_e, 0.4)
            return (xb_e, yc), (xt_e, yc), (b.left, b.bottom, b.right, b.top)
        return (xb, yc), (xt, yc), (b.left, b.bottom, b.right, b.top)

    def climb(self, net: str, x: float, y0: float, y1: float, w: float = 0.3) -> None:
        """Take ``net`` from its Metal1 y up to the TopMetal1 strap at ``y1`` on a Metal2 column
        clear of every device row.  Only ever used for Iq-class currents."""
        self.vstack(x, y0, "Metal1", "Metal2", VPAD)
        self.v("Metal2drawing", x, y0, y1, w)
        self.vstack(x, y1, "Metal2", "TopMetal1", 1.3)
        self.claim_vertical(net, x, y0, y1, "Metal2")
        # register the landing x, or the channel track is not drawn out to it and the net splits
        if net in self.track_pts and abs(y0 - self.track_y.get(net, 1e9)) < 1e-6:
            self.track_pts[net].append(_s(x))

    # -- power path --------------------------------------------------------
    def budget(self, net: str, note: str, current_a: float, layer: str,
               width_um: float = 0.0, n_vias: int = 1) -> None:
        self.budgets.append({"net": net, "note": note, "current_a": current_a, "layer": layer,
                             "width_um": round(width_um, 4), "n_vias": int(n_vias)})

    def riser(self, net: str, xc: float, yc: float, bot: str, top: str, n: int,
              rows: int, pad_w: float, current_a: float) -> None:
        """A count-driven via stack from ``bot`` to ``top`` with pads sized for the current."""
        i0, i1 = _STACK.index(bot), _STACK.index(top)
        span_x = span_y = 0.0
        for i in range(i0, i1):
            lay = _STACK[i]
            if lay == "Metal5":
                sx, sy = self.via_row("Metal5", xc, yc, self.p.pwr_stitch, 1)
                sx, sy = sx + 2 * (TVIA_ENC_M5 - VIA_ENC), sy + 2 * (TVIA_ENC_M5 - VIA_ENC)
                self.budget(net, f"{net} Metal5->TopMetal1 stitch", current_a, "topvia1",
                            n_vias=self.p.pwr_stitch)
            else:
                sx, sy = self.via_row(lay, xc, yc, n, rows)
                self.budget(net, f"{net} riser {lay}->{_STACK[i+1]}", current_a,
                            f"via{i + 1}", n_vias=n)
            span_x, span_y = max(span_x, sx), max(span_y, sy)
        w = max(pad_w, span_y)
        lx = max(span_x, pad_w)
        for i in range(i0, i1 + 1):
            lay = _STACK[i]
            if lay == "TopMetal1":
                continue     # the strap itself is the top pad
            self.rect(lay + "drawing", xc - lx / 2, yc - w / 2, xc + lx / 2, yc + w / 2)
            self.claim_box(lay, net, xc - lx / 2, yc - w / 2, xc + lx / 2, yc + w / 2)
            if lay != bot:
                self.budget(net, f"{net} riser {lay} pad", current_a, lay.lower(), width_um=w)

    # -- checks ------------------------------------------------------------
    def check(self) -> None:
        """Every routed column against every other column AND every claimed rectangle, per layer.

        Before F7 this compared columns only, and only as a flat list: the pass array's Metal2
        comb was drawn with `rect`/`h` and never entered the map, which is the hole that produced
        the it02 -> it03 `gate` | `vout` short and still reproduced at `col_vias` in {3, 4}.
        """
        vs = self.verticals
        for i in range(len(vs)):
            a = vs[i]
            la = a[4] if len(a) > 4 else "Metal2"
            for j in range(i + 1, len(vs)):
                b = vs[j]
                lb = b[4] if len(b) > 4 else "Metal2"
                if a[0] == b[0] or la != lb:
                    continue
                if abs(a[1] - b[1]) < 0.6 - 1e-6 and not (a[3] < b[2] - 0.6 or b[3] < a[2] - 0.6):
                    raise AssertionError(f"{la} verticals collide: {a} vs {b}")
            if not self.column_free(a[0], a[1], a[2], a[3], la):
                raise AssertionError(f"{la} column {a} crosses a claimed shape of another net")




# ------------------------------------------------------------------ build ----
# Measured operating currents (brief §8: `decks/candidate` dc_op with 0 V ammeters, 10 mA load).
I_VDD = 10.0318e-3
I_XMP = 10.0041e-3
I_VSS = 27.7e-6
I_RAIL_VDD = 37.0e-6   # what the Metal1 vdd rail carries once XMP's source goes up, not sideways


def _wf_max(groups: list[Group], W) -> float:
    """The tallest finger a row will contain, dummies included — needed before placement, because
    the rail y (and therefore the dummies' tie direction) depends on it."""
    out = 0.0
    for _g, _p, slots in groups:
        out = max(out, max(W[n] * f for n, f, _nf in slots))
        out = max(out, max(W[n] * f / nf for n, f, nf in slots))
    return out


def _place_row(b: Builder, groups: list[Group], W, L, x: float, y_act: float, pmos: bool,
               rail: str, y_rail: float, tag: str) -> tuple[dict[str, list[Dev]], list[Dev], float]:
    """Place every group of a row left to right, with `n_dummy` tied dummies at each end of each
    group.  Returns {device: [instances]}, every placed Dev (dummies included), and the x cursor."""
    p = b.p
    out: dict[str, list[Dev]] = {}
    alld: list[Dev] = []
    k = 0
    for gi, (_gname, _pattern, slots) in enumerate(groups):
        if gi:
            x += p.grp_gap
        # review-003 **F12**: a dummy exists to give the END MEMBER the neighbourhood the inner
        # members have, so it is sized to the slot it stands next to — not to the widest slot in
        # the group, which gave `bias_p_group` a 10 um dummy beside its 5.53 um XM6.
        for side in (0, 1):
            if side:
                for name, frac, nf in slots:
                    d = b.mos(name, W[name] * frac, L[name], nf, pmos, x, y_act,
                              d_top=not pmos, g_top=not pmos)
                    out.setdefault(name, []).append(d)
                    alld.append(d)
                    x = d.ax1 + p.dev_gap
            nb = slots[-1] if side else slots[0]
            w_dum, l_dum = W[nb[0]] * nb[1], L[nb[0]]
            for _ in range(p.n_dummy):
                k += 1
                d = b.dummy(f"{tag}{k}", w_dum, l_dum, pmos, x, y_act, rail, y_rail)
                alld.append(d)
                x = d.ax1 + p.dev_gap
    return out, alld, x - p.dev_gap


def _row_box(devs: list[Dev], gpad: float = GPAD, pad: float = 1.15) -> tuple[float, float, float, float]:
    """Bounding box of a placed row including its gate bars and strap / via pads."""
    ys: list[float] = []
    for d in devs:
        y_g = d.term["_gate_bar"][0]  # type: ignore[index]
        ys += [d.ay0, d.ay1, y_g - gpad / 2, y_g + gpad / 2, d.ay1 + STRAP + VPAD / 2,
               d.ay0 - STRAP - VPAD / 2]
    return (min(d.ax0 for d in devs) - pad, min(ys) - 0.4,
            max(d.ax1 for d in devs) + pad, max(ys) + 0.4)


def _wire_dev(b: Builder, d: Dev, name: str, net, pmos: bool, y_rail: float,
              reserve: dict[str, float] | None = None) -> dict[str, float]:
    """Drain -> its track, gate -> its track, source -> the rail (or its track).

    Returns the x of every column it allocated, so a mirror partner can be given the same
    offsets instead of whatever the first-come walk happens to find (F6)."""
    dn, gn, sn = net[name]
    r = reserve or {}
    used: dict[str, float] = {}
    xr = _s(d.ax1 + 0.55)
    yd = b.strap(d, "D", not pmos, ext_to=xr, net=dn)
    used["d"] = b.to_track(dn, xr, yd, reserve=r.get("d"))
    xl = _s(d.ax0 - 0.55)
    yg = b.gate_pad(d, xl, gn)
    used["g"] = b.to_track(gn, xl, yg, step=-0.6, reserve=r.get("g"))
    if sn in ("vdd", "vss"):
        b.columns_to_rail(d, "S", y_rail)
    else:
        xs = _s(d.ax1 + 1.15)
        ys = b.strap(d, "S", pmos, ext_to=xs, net=sn)
        used["s"] = b.to_track(sn, xs, ys, reserve=r.get("s"))
    return used


def _terminals(d: Dev, name: str, net, pmos: bool) -> dict[str, tuple[str, float, float, float]]:
    """(net, terminal x, terminal y, step) for each terminal that gets its own column.

    Computed WITHOUT drawing, so a mirrored pair can be reserved before either half is wired."""
    dn, gn, sn = net[name]
    out = {"d": (dn, _s(d.ax1 + 0.55), _s(d.ay1 + STRAP) if not pmos else _s(d.ay0 - STRAP), 0.6),
           "g": (gn, _s(d.ax0 - 0.55), d.term["_gate_bar"][0], -0.6)}       # type: ignore[index]
    if sn not in ("vdd", "vss"):
        out["s"] = (sn, _s(d.ax1 + 1.15), _s(d.ay1 + STRAP) if pmos else _s(d.ay0 - STRAP), 0.6)
    return out


def _reserve_pair(b: Builder, da: Dev, na: str, db: Dev, nb: str, net, pmos: bool,
                  tries: int = 80) -> tuple[dict[str, float], dict[str, float]]:
    """Find, per terminal, ONE offset from the two devices' own terminal x that is legal for
    BOTH halves, and claim both columns before anything else is routed (review-003 F6).

    The mirrored column has to be reserved as a PAIR: giving the second half whatever the first
    half happened to get fails as soon as the second half's x is already taken (measured: the two
    `ea_in_pair` halves still XOR'd at 25 % that way, because one `ea_n` column was 0.38 um from
    another `ea_n` column and the pad pitch refused it)."""
    ta, tb = _terminals(da, na, net, pmos), _terminals(db, nb, net, pmos)
    ra: dict[str, float] = {}
    rb: dict[str, float] = {}
    for k in ta:
        (nn, xa, ya, step) = ta[k]
        (_n2, xb, yb, _s2) = tb[k]
        yt = b.rail_y.get(nn, b.track_y.get(nn))
        if yt is None:
            continue
        layer = TRACK_LAYER.get(nn, "Metal2")
        for m in range(tries):
            for s in (step, -step) if m else (step,):
                pa, pb = _s(xa + m * s), _s(xb + m * s)
                if (b.column_free(nn, pa, min(ya, yt), max(ya, yt), layer)
                        and b.stub_clear(nn, ya, xa, pa)
                        and b.column_free(nn, pb, min(yb, yt), max(yb, yt), layer)
                        and b.stub_clear(nn, yb, xb, pb)
                        and abs(pa - pb) >= b.M2_CLEAR - 1e-6):
                    ra[k], rb[k] = pa, pb
                    b.claim_vertical(nn, pa, ya, yt, layer)
                    b.claim_vertical(nn, pb, yb, yt, layer)
                    break
            if k in ra:
                break
    return ra, rb


def _wire_row(b: Builder, insts: dict[str, list[Dev]], net, pmos: bool, y_rail: float,
              groups: list[Group]) -> None:
    """Wire a row group by group.

    review-003 **F6**: device geometry was common-centroid but the ROUTING was not — the two
    halves of `ea_in_pair` XOR'd at 65 % / 33 % with 4 vs 3 Via1, because each half took whatever
    column the general allocator handed it.  Every common-centroid group now reserves a mirrored
    column pair per member **before** the general allocator runs, and only then draws."""
    for _gname, pattern, slots in groups:
        names = [s[0] for s in slots]
        res: dict[str, dict[str, float]] = {}
        if pattern == "common_centroid":
            for i in range(len(names) // 2):
                a, z = names[i], names[len(names) - 1 - i]
                res[a], res[z] = _reserve_pair(b, insts[a][0], a, insts[z][0], z, net, pmos)
        for name in names:
            for d in insts[name]:
                _wire_dev(b, d, name, net, pmos, y_rail, res.get(name))


def _seg_len(l_total: float, segs: int, what: str) -> float:
    """A serpentine segment length that keeps the `rhigh` cell on grid.

    A `dy` that is not a multiple of 0.01 um makes the PDK cell's own geometry off-grid: at
    `l = 138.5 um / 4 = 34.625 um` the rule deck reported 14 OffGrid / Sal.e / Rhi.d violations
    *inside* the rhigh cell.  Rather than silently rounding (which would change the resistance and
    fail LVS), refuse — the segment count is a knob and the caller can move it.
    """
    seg = l_total / segs
    if abs(round(seg, 2) - seg) > 1e-9:
        raise AssertionError(
            f"{what}: {l_total:g} um / {segs} = {seg:g} um is not a multiple of 0.01 um; the "
            f"rhigh cell goes off-grid there — pick another segment count")
    return _s(seg)


def build_full(p: LayoutParams = LayoutParams(),
               sizing: dict[str, object] | None = None) -> tuple[gf.Component, Builder]:
    sz = {**SIZING, **(sizing or {})}
    mos, passives = NR.devices(sz)
    MD = {d.name: d for d in mos}
    W = {n: d.w_total for n, d in MD.items()}
    L = {n: d.l for n, d in MD.items()}
    net = {n: (d.drain, d.gate, d.source) for n, d in MD.items()}
    PC = {c.name: c for c in passives}
    b = Builder(p, sz)

    # ================= row A: NMOS, sources on the vss rail =================
    y_vss = 0.0
    b.rail_y["vss"] = y_vss
    b.m1_claim("vss", y_vss, -1e4, 1e4, p.rail_w)
    yA = _s(y_vss + p.rail_gap)
    instA, allA, xA_end = _place_row(b, ROW_A, W, L, 0.6, yA, False, "vss", y_vss, "A")
    boxA = _row_box(allA, p.gpad)
    # the ring encloses the vss rail as well: the rail is the row's own vss distribution and
    # leaves through the ring's side segments, which is a merge of one net, not a crossing
    boxA = (-1.4, min(boxA[1], y_vss - p.rail_w / 2 - 0.5), xA_end + 1.4, boxA[3])
    ringA_top = boxA[3] + p.ring_gap + 0.14 + p.ring_w + 0.25
    y_ch0 = _s(ringA_top + p.ch_margin)
    for i, t in enumerate(TRACKS):
        b.track_y[t] = _s(y_ch0 + i * p.track_pitch)
    y_ch1 = b.track_y[TRACKS[-1]] + p.ch_margin
    b.ring("psub", "vss", boxA[0], boxA[1], boxA[2], boxA[3], gap=p.ring_gap)
    _wire_row(b, instA, net, False, y_vss, ROW_A)

    # ================= row B: PMOS, two nwell islands, sources on the vdd rail ==========
    wfB = max(_wf_max(ROW_B_QUIET, W), _wf_max(ROW_B_FVF, W))
    yB = _s(y_ch1 + p.ring_w + 0.14 + p.ring_gap + GATE + p.gpad / 2 + 0.45)
    y_vdd = _s(yB + wfB + p.rail_gap)
    b.rail_y["vdd"] = y_vdd
    b.m1_claim("vdd", y_vdd, -1e4, 1e4, p.rail_w)
    instQ, allQ, xQ_end = _place_row(b, ROW_B_QUIET, W, L, 0.6, yB, True, "vdd", y_vdd, "Q")
    # both rings plus NW.b (0.62 between two nwells on the same net) and Act.b (0.21) fit in
    # this gap: at 0.20 the two islands merged into ONE well and Act.b fired six times
    x_isl = _s(xQ_end + 2.8 + 2 * (p.ring_gap + p.ring_w) + p.isl_gap)
    instF, allF, xF_end = _place_row(b, ROW_B_FVF, W, L, x_isl, yB, True, "vdd", y_vdd, "F")
    boxQ = _row_box(allQ, p.gpad)
    boxQ = (-1.4, boxQ[1], _s(xQ_end + 1.4), max(boxQ[3], y_vdd + p.rail_w / 2 + 0.5))
    boxF = _row_box(allF, p.gpad)
    boxF = (_s(x_isl - 1.4), boxF[1], _s(xF_end + 1.4), max(boxF[3], y_vdd + p.rail_w / 2 + 0.5))
    for box in (boxQ, boxF):
        b.ring("nwell", "vdd", box[0], box[1], box[2], box[3], gap=p.ring_gap)
    _wire_row(b, instQ, net, True, y_vdd, ROW_B_QUIET)
    _wire_row(b, instF, net, True, y_vdd, ROW_B_FVF)

    # ================= the pass device: own island, Metal2 combs, TopMetal1 straps ======
    y_out_band = _s(y_vdd + p.rail_w / 2 + p.blk_gap + p.ring_w + p.pwr_band_w / 2 + 1.5)
    yC = _s(y_out_band + p.pwr_band_w / 2 + 1.4 + GATE + p.gpad / 2 + 0.6)
    # The certified XMP card is m unit fingers (review F19): the drawn finger count is a device
    # parameter the benches simulate, not a layout knob, so it is read here, never chosen.
    nf = MD["XMP"].m
    if abs(round(MD["XMP"].w, 2) - MD["XMP"].w) > 1e-9:
        raise AssertionError(
            f"XMP: unit finger {MD['XMP'].w:g} um is not a multiple of 0.01 um; the drawn finger "
            f"would round and LVS would see a different device")
    xC = _s(max(0.6, boxF[2] - 1.4 - (nf + 1) * 0.52))
    # The via column is `col_vias` cuts stacked in y; both the Metal1 stub and the Metal2 finger
    # must enclose it (M2.c1: Metal2 endcap enclosure of Via1 = 0.05), which is what 77 of the
    # first round's 118 violations were.  The DRAIN pad hangs below the active, so the gate bar
    # has to stand off far enough to clear it: at `col_vias` = 4 the drain Metal1 reached
    # 0.08 um INTO the gate bar and LVS returned `gate | vout` — DRC saw one legal polygon
    # (review-003 F2/F7).  The stand-off is therefore derived, not the module constant.
    v_span = p.col_vias * VIA + (p.col_vias - 1) * VIA_SP
    v_env = _s(v_span / 2 + 0.10)
    gate_gap_P = _s(max(GATE, 0.15 + 2 * v_env + 0.21 + p.gpad / 2))
    dP = b.mos("XMP", W["XMP"], L["XMP"], nf, True, xC, yC, d_top=False, g_top=False,
               gate_gap=gate_gap_P)
    i_col = 2 * I_XMP / nf                    # interior diffusion columns are SHARED by 2 fingers
    src, drn = dP.cols[0::2], dP.cols[1::2]
    # the n-well ring's Metal2 riser climbs into the SOURCE spine, so the spine has to reach it:
    # at `ring_gap` = 3.0 the ring sits 1.6 um further out than the spine's end and the pass
    # device's bulk extracted as an unnamed node (`M$26 ... \$34`, review-003 F2).
    x_ring_l = _s(dP.ax0 - 1.0 - p.ring_gap - p.ring_w / 2)
    y_s_pad = _s(dP.ay1 + 0.15 + v_env)
    y_d_pad = _s(dP.ay0 - 0.15 - v_env)
    y_s_band = _s(y_s_pad + v_env + 1.0 + p.pwr_band_w / 2)
    # Every one of these rectangles is CLAIMED in the obstacle map (review-003 F7): the comb is
    # the biggest Metal2 structure in the cell and it used to be invisible to the router.
    for xx in src:
        b.rect("Metal1drawing", xx - 0.155, dP.ay1 - 0.1, xx + 0.155, y_s_pad + v_env)
        b.claim_box("Metal1", "vdd", xx - 0.155, dP.ay1 - 0.1, xx + 0.155, y_s_pad + v_env)
        b.m1_claim_box("vdd", xx - 0.155, dP.ay1 - 0.1, xx + 0.155, y_s_pad + v_env)
        b.via_row("Metal1", xx, y_s_pad, p.col_vias, p.col_vias)
        b.rect("Metal2drawing", xx - 0.155, y_s_pad - v_env, xx + 0.155, y_s_band)
        b.claim_box("Metal2", "vdd", xx - 0.155, y_s_pad - v_env, xx + 0.155, y_s_band)
    for xx in drn:
        b.rect("Metal1drawing", xx - 0.155, y_d_pad - v_env, xx + 0.155, dP.ay0 + 0.1)
        b.claim_box("Metal1", "vout", xx - 0.155, y_d_pad - v_env, xx + 0.155, dP.ay0 + 0.1)
        b.m1_claim_box("vout", xx - 0.155, y_d_pad - v_env, xx + 0.155, dP.ay0 + 0.1)
        b.via_row("Metal1", xx, y_d_pad, p.col_vias, p.col_vias)
        b.rect("Metal2drawing", xx - 0.155, y_out_band, xx + 0.155, y_d_pad + v_env)
        b.claim_box("Metal2", "vout", xx - 0.155, y_out_band, xx + 0.155, y_d_pad + v_env)
    for netn, yb in (("vdd", y_s_band), ("vout", y_out_band)):
        x0b = min(_s(dP.ax0 - 0.6), x_ring_l) if netn == "vdd" else _s(dP.ax0 - 0.6)
        b.h("Metal2drawing", yb, x0b, dP.ax1 + 0.6, p.pwr_band_w)
        b.claim_box("Metal2", netn, x0b - p.pwr_band_w / 2, yb - p.pwr_band_w / 2,
                    dP.ax1 + 0.6 + p.pwr_band_w / 2, yb + p.pwr_band_w / 2)
    b.budget("vdd", "pass source column Metal1 riser (shared)", i_col, "metal1", width_um=0.31)
    b.budget("vout", "pass drain column Metal1 riser (shared)", i_col, "metal1", width_um=0.31)
    # `via_row(n=col_vias, rows=col_vias)` lays `col_vias` cuts out over `col_vias` rows, i.e.
    # ONE cut per row: the count is `col_vias`, not `col_vias**2` (review-003 F4, which counted
    # 2 cuts per column in the GDS against a table that claimed 4).
    b.budget("vdd", "pass source column Via1 (shared)", i_col, "via1", n_vias=p.col_vias)
    b.budget("vout", "pass drain column Via1 (shared)", i_col, "via1", n_vias=p.col_vias)
    b.budget("vdd", "pass source column Metal2 finger", i_col, "metal2", width_um=0.31)
    b.budget("vout", "pass drain column Metal2 finger", i_col, "metal2", width_um=0.31)
    b.budget("vdd", "pass source Metal2 comb spine", I_VDD, "metal2", width_um=p.pwr_band_w)
    b.budget("vout", "pass drain Metal2 comb spine", I_XMP, "metal2", width_um=p.pwr_band_w)
    # The `_mos_core` S/D column draws one contact row over the finger width; at 2.5 um / finger
    # that is 7 cuts (measured in the GDS), and BOTH sides carry the same shared-column current.
    n_cnt = max(1, int((MD["XMP"].w - 2 * 0.16) // (CONT + 0.18)) + 1)
    b.budget("vout", "pass drain diffusion contacts (shared column)", i_col, "cnt", n_vias=n_cnt)
    b.budget("vdd", "pass source diffusion contacts (shared column)", i_col, "cnt", n_vias=n_cnt)
    # `gate` leaves the array on its LEFT and drops onto the TOP channel track.  That track is
    # Metal3 (`TRACK_LAYER`, F3), so the column is allocated against Metal3 obstacles and simply
    # is not asked about the Metal2 comb it crosses — the special case `to_track_m3` existed to
    # paper over is gone, and the comb is now a claimed obstacle for anything that IS on Metal2.
    xg = _s(dP.ax0 - 0.75)
    ygp = b.gate_pad(dP, xg, "gate")
    b.to_track("gate", xg, ygp, step=-0.6)

    x_r = _s((dP.ax0 + dP.ax1) / 2)
    b.riser("vdd", x_r, y_s_band, "Metal2", "TopMetal1", p.pwr_riser_vias, 2, p.pwr_band_w, I_VDD)
    b.riser("vout", x_r, y_out_band, "Metal2", "TopMetal1", p.pwr_riser_vias, 2, p.pwr_band_w, I_XMP)
    b.budget("vdd", "cell Metal1 vdd rail (row-B sources + XRB, Iq only)", I_RAIL_VDD, "metal1",
             width_um=p.rail_w)
    b.budget("vss", "cell Metal1 vss rail (Iq only)", I_VSS, "metal1", width_um=p.rail_w)

    boxP = (dP.ax0 - 1.0, dP.ay0 - gate_gap_P - p.gpad / 2 - 0.5, dP.ax1 + 1.0, dP.ay1 + 1.15)
    gP = b.ring("nwell", "vdd", *boxP, gap=p.ring_gap)
    # the ntap ring reaches vdd up its LEFT segment on Metal2, into the source comb's spine
    rm = b.ring_m1["vdd"]
    x_rc = _s(rm[0])
    assert abs(x_rc - x_ring_l) < 1e-6, f"the source spine was extended to {x_ring_l}, ring at {x_rc}"
    b.vstack(x_rc, _s(dP.ay1), "Metal1", "Metal2", 0.5)
    b.v("Metal2drawing", x_rc, _s(dP.ay1), y_s_band, 0.5)
    b.claim_box("Metal2", "vdd", x_rc - 0.25, _s(dP.ay1), x_rc + 0.25, y_s_band)
    # brief §7: a second, p-substrate ring between XMP and everything else, outside the combs
    b.ring("psub", "vss", gP[0] - 0.6, y_out_band - p.pwr_band_w / 2 - 0.6,
           gP[2] + 0.6, y_s_band + p.pwr_band_w / 2 + 0.6, gap=0.3)

    y_top = _s(y_s_band + p.pwr_band_w / 2 + 3.4)
    x_stack = max(boxF[2], gP[2] + 2.4, xA_end + 1.4)

    # ================= passives: the left column ===============================
    # Everything with a channel connection lives at x < 0, so its Metal2 riser reaches the tracks
    # without crossing a device row.  XCOUT (§below) needs no track and goes under the stack.
    # The divider and the bias resistor are SEGMENT CHAINS in the certified netlist (F19), so the
    # segment count and length are read from it, not chosen here: `XR1_1..XR1_n` is n drawn
    # serpentines of `l`, and n is what the benches simulate.
    chains = {k: sorted((c for c in passives if c.name.startswith(k + "_")),
                        key=lambda c: int(c.name.rsplit("_", 1)[1])) for k in ("XR1", "XR2", "XRB")}
    r_segs, rb_segs = len(chains["XR1"]), len(chains["XRB"])
    assert r_segs == len(chains["XR2"]), "XR1 and XR2 must be drawn with the same segment count"
    r_w = _val(chains["XR1"][0].params["w"], sz)
    seg_l = _seg_len(_val(chains["XR1"][0].params["l"], sz), 1, "XR1/XR2")
    rb_seg_l = _seg_len(_val(chains["XRB"][0].params["l"], sz), 1, "XRB")
    ccw = _val(PC["XCC"].params["w"], sz)
    cffw = _val(PC["XCFF"].params["w"], sz)
    if r_segs % 2:
        raise AssertionError("XR1/XR2 need an even segment count: A B B A is built from pairs")
    # XR1 / XR2: one common-centroid block, [A B B A] repeated, both centroids at the block
    # centre, with a tied dummy segment at each end.  brief §6 makes this the tightest matching
    # class in the cell (1.71 sigma) and brief §9 asks for ABBA specifically.
    order: list[str] = []
    for _ in range(r_segs // 2):
        order += ["XR1", "XR2", "XR2", "XR1"]
    n_cols = len(order) + 2 * p.n_dummy
    x_res1 = _s(-p.blk_gap - max(n_cols * p.res_pitch, ccw + 6.0))
    y_res = _s(y_vss - 7.0 - seg_l)
    ports: dict[str, list[tuple[tuple[float, float], tuple[float, float]]]] = {"XR1": [], "XR2": []}
    for i in range(n_cols):
        xx = _s(x_res1 + i * p.res_pitch)
        lo, hi, _, _ = b.serpentine(r_w, seg_l, 1, xx, y_res)
        # the rhigh end pads are Metal1: claim them, or a stub walking the port row shorts the
        # comb into itself (round 2 extracted XR2 as 212.5 + 85 + 42.5 um with `fb` in the middle)
        for k, (px, py) in enumerate((lo, hi)):
            b.m1_claim(f"@r{i}{k}", py, px - 0.45, px + 0.45, 0.9)
        if i < p.n_dummy or i >= n_cols - p.n_dummy:
            # a dummy segment: both ends shorted together and tied to vss
            b.m1v(lo[0], lo[1], hi[1], 0.3)
            b.dummies.append(NR.Dummy(f"RD{i}", "r", "vss", r_w, seg_l))
            b.m1_retag(f"@r{i}0", "vss")
            b.m1_retag(f"@r{i}1", "vss")
            b.to_track("vss", lo[0], lo[1])
            continue
        ports[order[i - p.n_dummy]].append((lo, hi, i))

    def _chain(entries, on_m2: bool):
        """Series-connect one arm's segments.  One arm links on Metal1 (offset out of the way),
        the other on Metal2 at the port y: an interdigitated comb needs two levels, or the two
        arms' links short where their spans overlap."""
        y_lo = min(e[0][1] for e in entries) - 1.0
        y_hi = max(e[1][1] for e in entries) + 1.0
        for j in range(len(entries) - 1):
            at_bot = (j % 2 == 0)
            p0, p1 = entries[j][0 if at_bot else 1], entries[j + 1][0 if at_bot else 1]
            for e, k in ((entries[j], 0 if at_bot else 1), (entries[j + 1], 0 if at_bot else 1)):
                b.m1_retag(f"@r{e[2]}{k}", f"@arm{id(entries)}")
            if on_m2:
                # Metal3, not Metal2: the arm's links run the length of the comb at the port y,
                # and the fb / lp_brk Metal2 columns that leave the comb cross exactly there --
                # round 3 extracted XR2 as vss-212.5-fb-85-$16-42.5-fb, a loop back into fb.
                b.vstack(p0[0], p0[1], "Metal1", "Metal3", VPAD)
                b.vstack(p1[0], p1[1], "Metal1", "Metal3", VPAD)
                for px in (p0[0], p1[0]):
                    b.claim_vertical(f"@arm{id(entries)}", px, p0[1] - 0.3, p0[1] + 0.3, "Metal3")
                b.claim_box("Metal3", f"@arm{id(entries)}", min(p0[0], p1[0]), p0[1] - 0.15,
                            max(p0[0], p1[0]), p0[1] + 0.15)
                b.h("Metal3drawing", p0[1], p0[0], p1[0], 0.3)
            else:
                y = y_lo if at_bot else y_hi
                b.m1v(p0[0], p0[1], y, 0.3)
                b.m1v(p1[0], p1[1], y, 0.3)
                b.m1h(y, p0[0], p1[0], 0.3)
                b.m1_claim(f"@arm{id(entries)}", y, p0[0], p1[0], 0.3)
        k_last = 1 if (len(entries) - 2) % 2 == 0 else 0
        return ((entries[0][1], (entries[0][2], 1)),
                (entries[-1][k_last], (entries[-1][2], k_last)))

    (r1a, i1a), (r1b, i1b) = _chain(ports["XR1"], on_m2=False)
    (r2a, i2a), (r2b, i2b) = _chain(ports["XR2"], on_m2=True)
    for tag, nname in ((f"@r{i1a[0]}{i1a[1]}", "lp_brk"), (f"@r{i1b[0]}{i1b[1]}", "fb"),
                       (f"@r{i2a[0]}{i2a[1]}", "fb"), (f"@r{i2b[0]}{i2b[1]}", "vss")):
        b.m1_retag(tag, nname)
    b.to_track("lp_brk", r1a[0], r1a[1])       # XR1: lp_brk (divider top) -> fb
    b.to_track("fb", r1b[0], r1b[1])
    b.to_track("fb", r2a[0], r2a[1])           # XR2: fb -> vss
    b.to_track("vss", r2b[0], r2b[1])
    # XRB beside the divider block, equally far from XMP (brief §9: its tc1 sets every current).
    # review-003 **F12**: on the divider's own `res_pitch`, with `n_dummy` tied segments at each
    # end — at 1.6 um and no dummy the divider's right dummy saw XRB 1.1 um away and its left
    # dummy saw open field, i.e. the two ends of the divider array were not equivalent either.
    x_rb = _s(x_res1 + n_cols * p.res_pitch + 1.0)
    def _rb_dummy(xx: float, tag: int) -> tuple[float, float]:
        lo, hi, _xs, _ys = b.serpentine(r_w, rb_seg_l, 1, xx, y_res)
        b.m1v(lo[0], lo[1], hi[1], 0.3)
        b.m1_claim("vss", lo[1], lo[0] - 0.45, lo[0] + 0.45, 0.9)
        b.m1_claim("vss", hi[1], hi[0] - 0.45, hi[0] + 0.45, 0.9)
        b.dummies.append(NR.Dummy(f"RBD{tag}", "r", "vss", r_w, rb_seg_l))
        return lo

    for k in range(p.n_dummy):
        lo = _rb_dummy(_s(x_rb + k * p.res_pitch), k)
        b.to_track("vss", lo[0], lo[1])
    x_rb = _s(x_rb + p.n_dummy * p.res_pitch)
    rba, rbb, xs_rb, ys_rb = b.serpentine(r_w, rb_seg_l * rb_segs, rb_segs, x_rb, y_res,
                                          pitch=p.res_pitch)
    # claim EVERY segment's two Metal1 end pads before anything routes past them: at
    # `res_pitch` = 3.0 a dummy's `vss` stub walked the XRB port row and the five-segment string
    # extracted as `vss-27.7-$23`, `vss-27.7-nbias`, `vss-55.4-vdd` (review-003 F2 re-walk).
    for i, xx in enumerate(xs_rb):
        for k, yy in enumerate(ys_rb):
            b.m1_claim(f"@rb{i}{k}", yy, xx - 0.45, xx + 0.45, 0.9)
    b.m1_retag("@rb00", "vdd")
    b.m1_retag(f"@rb{rb_segs - 1}{0 if rb_segs % 2 == 0 else 1}", "nbias")
    b.to_track("vdd", rba[0], rba[1])
    b.to_track("nbias", rbb[0], rbb[1])
    for k in range(p.n_dummy):
        lo = _rb_dummy(_s(x_rb + (rb_segs + k) * p.res_pitch), p.n_dummy + k)
        b.to_track("vss", lo[0], lo[1])
    x_rb_r = _s(x_rb + (rb_segs + p.n_dummy) * p.res_pitch)

    # XCC (Miller) and XCFF (feed-forward): same orientation, same plate-connection side.
    # Which node is the TOP plate is NOT a layout choice: `cap_cmim` is a polarised device in the
    # LVS deck and the certified card fixes it -- nodes[0] is the top (PLUS) plate, nodes[1] the
    # Metal5 bottom (MINUS).  Round 4 followed brief §9 instead ("put the terminal that has a
    # budget on top") and LVS reported CFF and CC mismatched with fb/lp_brk and ea_o1/ea_out
    # swapped.  Swapping the plates moves the bottom-plate parasitic to the other node, i.e. it is
    # a design change, so the drawing follows the netlist and the brief's preference is recorded
    # as a re-sizing question, not applied here.
    y_cc = _s(y_res - p.mim_gap - ccw - 3.0)
    bt, tp, bbcc = b.mim(ccw, _s(x_res1 + 1.4), y_cc, escape=2.0)
    b.to_track(PC["XCC"].nodes[1], *bt)
    b.to_track(PC["XCC"].nodes[0], *tp)
    y_cff = _s(bbcc[1] - p.mim_gap - cffw - 1.0)
    bt, tp, bbff = b.mim(cffw, _s(x_res1 + 1.4), y_cff, escape=2.0)
    b.to_track(PC["XCFF"].nodes[1], *bt)
    b.to_track(PC["XCFF"].nodes[0], *tp)
    x_pass_r = _s(max(bbcc[2] + 3.2, x_rb_r + 1.0))

    # ================= XCOUT: a 2x2 common-centroid unit array under the stack ==========
    # A3 of the PLAN: `m = 4` already IS the unit array; the four certified 58 um units are drawn
    # on a common centroid about a central TopMetal1 top-plate spine, the right column mirrored so
    # the block has ONE plate-connection side per terminal.  No MIM dummy ring: brief §6 gives
    # `mim_cout_unit` no bound, and a ring of 58 um units would triple the block.
    cw = _val(PC["XCOUT"].params["w"], sz)
    cm = _count(NR.value(PC["XCOUT"].params["m"], sz))
    cols_ = 2 if cm > 1 else 1
    rows_ = -(-cm // cols_)
    y_cout_top = _s(y_vss - 8.0)
    unit_h = _s(cw + p.mim_gap)
    # The TopMetal1 `vout` spine runs BETWEEN the two columns and is `pwr_w` wide, so the column
    # pitch carries that width: at `pwr_w` = 8 the spine came within 0.4 um of the MIM (MIM.e is
    # 0.60) and 0.76 um of the top plate (TM1.b is 1.64).  4.0 is the room the default needs.
    pwr_extra = max(0.0, p.pwr_w - 4.0)
    pitch_x = _s(cw + 2 * p.mim_gap + 4.0 + pwr_extra)
    # The cap array starts where the passive column ends.  `x_pass_r` was computed and never used:
    # at `res_pitch` = 3.0 the XRB block slid right to x = -2..16 and XCOUT's bottom-plate drop —
    # 3.0 um wide since the Kelvin return — ran straight down through it, extracting XRB as
    # `vss-27.7-$23`, `vss-27.7-nbias`, `vss-55.4-vdd` (review-003 F2 re-walk).
    x_cout0 = _s(max(1.0, x_pass_r))
    vout_spine_x = _s(x_cout0 + cw + p.mim_gap + 2.0 + pwr_extra / 2)
    cout_bot = _s(y_cout_top - rows_ * unit_h)
    vss_pads: list[tuple[float, float]] = []
    for i in range(cm):
        col, row = i % cols_, i // cols_
        mir = bool(col)
        x0 = _s(x_cout0 + col * pitch_x)
        y0 = _s(y_cout_top - (row + 1) * unit_h + p.mim_gap / 2)
        bt, _tp, _bb = b.mim(cw, x0, y0, mirror=mir, top_to=vout_spine_x)
        vss_pads.append(bt)   # PC["XCOUT"].nodes[1] == "vss"; nodes[0] == "vout" is the top plate
    x_cout_r = _s(x_cout0 + (cols_ - 1) * pitch_x + cw + 3.0)

    # ================= rails, straps, pin frame ===============================
    # The two vss risers are `vss_ret_w` wide, so the cell reserves that much extra on each edge
    # rather than pushing them into the passive block: at 3.0 um and the old 2.5 um margin the
    # left riser landed ON the XCFF bottom-plate pad and LVS returned `ea_o1 | fb | vss` — the
    # "retrofitting width into a finished floorplan does not work" failure, one round later.
    # The right margin also sets where the `vout` TopMetal1 strap runs: at the old margin its
    # left edge was 0.76 um from the XCOUT top plate (TM1.b notch 1.64) and 0.40 um from the MIM
    # (MIM.e 0.60) once `pwr_w` went 2.0 -> 4.0.
    x_left = _s(x_res1 - 2.5 - p.vss_ret_w)
    # ... and the `vout` strap that runs down the right edge is `pwr_w` wide, so where the edge
    # sits also has to satisfy TM1.b (1.64) against the XCOUT top plates: at `pwr_w` = 8 the two
    # collided (5 x TM1.b, 4 x MIM.e).
    x_right = _s(max(x_stack + 2.0, x_cout_r + 2.0,
                     x_cout_r + TM1_MIN_SP + p.pwr_w))
    y_bot = _s(min(cout_bot, bbff[1] - 3.0) - 4.0)
    b.m1h(y_vss, x_left, x_right, p.rail_w)
    b.m1h(y_vdd, x_left, x_stack, p.rail_w)
    # The vss return, as a KELVIN CAP RETURN (review-003 F9, re-derived brief §4a).  The first
    # fix here widened the rail, on the reviewer's reading that 32 Ohm of return R was the
    # problem.  The re-derived brief settles the mechanism by splitting the injection: with only
    # the ACTIVE devices behind 32 Ohm, S7 moves +0.44 mV — nothing; with only XCOUT's bottom
    # plate behind it, S7 *improves* to 103.2 mV.  The 11 Ohm cliff needs BOTH halves behind one
    # R, because Cout's load-step displacement current develops a ground bounce the FVF sources
    # and the EA read as a reference step.  So the two returns are SEPARATED here rather than
    # widened together:
    #
    #   * the `vss` PIN is the foot of the single left-edge riser, and the ACTIVE devices reach
    #     it down that riser alone — `vss_ret_w` = 3.0 um over 134.8 um is 4.9 Ohm against the
    #     brief's 16 Ohm budget for the active-only return (S6, -0.4553 dB/Ohm);
    #   * XCOUT's four bottom plates reach the SAME PIN along the bottom rail on their own
    #     `vss_ret_w`-wide straps, and the active current never enters that rail, so the shared
    #     impedance between the two returns is the pin itself.
    #
    # A second, right-edge riser would halve the active return and put it straight back: the
    # active current would then run the length of the bottom rail, which is the cap's return.
    b.m1h(y_bot, x_left, x_right, p.vss_ret_w)
    x_ret_l = _s(x_left + p.vss_ret_w / 2)
    b.m1v(x_ret_l, y_bot, y_vss, p.vss_ret_w)
    b.m1_claim_box("vss", x_ret_l - p.vss_ret_w / 2, y_bot, x_ret_l + p.vss_ret_w / 2, y_vss)
    b.budget("vss", "vss active-device return: left edge riser (Iq only)", I_VSS, "metal1",
             width_um=p.vss_ret_w)
    b.budget("vss", "vss XCOUT bottom-plate return: bottom rail (displacement current)", I_VSS,
             "metal1", width_um=p.vss_ret_w)
    for (xb, yb) in vss_pads:                     # XCOUT bottom plates -> the bottom rail
        b.m1v(xb, yb, y_bot, p.vss_ret_w)       # the plate pad already reaches Metal1
    # vdd: the Metal1 rail climbs to the TopMetal1 strap on the left, clear of every device
    b.climb("vdd", _s(x_left + 2.6), y_vdd, y_s_band)
    b.h("TopMetal1drawing", y_s_band, x_left, x_right, p.pwr_w)
    b.budget("vdd", "vdd TopMetal1 strap (top edge)", I_VDD, "topmetal1", width_um=p.pwr_w)
    # vout: TopMetal1 from the pass-drain riser, right to the edge, down it, then over XCOUT
    b.h("TopMetal1drawing", y_out_band, dP.ax0 - 0.6, x_right, p.pwr_w)
    b.v("TopMetal1drawing", _s(x_right - p.pwr_w / 2), _s(cout_bot + 3.0), y_out_band, p.pwr_w)
    b.h("TopMetal1drawing", _s(cout_bot + 3.0), vout_spine_x, _s(x_right - p.pwr_w / 2), p.pwr_w)
    b.v("TopMetal1drawing", vout_spine_x, _s(cout_bot + 3.0), _s(y_cout_top - 1.0), p.pwr_w)
    b.budget("vout", "vout TopMetal1 strap (right edge + XCOUT bus)", I_XMP, "topmetal1",
             width_um=p.pwr_w)
    # the `vout` channel track (XMC's source, the divider sense return) joins the strap clear of
    # the stack; the vout PIN label sits at the far right edge, so the extraction's pin node is
    # the OUTPUT PIN and not the pass drain (brief §4: 0.126 Ohm -> 1.78 Ohm)
    b.climb("vout", _s(x_stack + 1.2), b.track_y["vout"], y_out_band)

    # ---------------- channel tracks + labels ----------------
    # review-003 **F8**: `lp_brk` is the divider's sense terminal and the loop-break port — the
    # certified netlist closes it with `VLP lp_brk vout dc 0`, so the cell cannot merge the two
    # nets without deleting a pin the benches drive.  What the LAYOUT decides is WHERE the short
    # lands: brief §4 wants the divider to sense at the OUTPUT PIN (0.026 mV of load regulation)
    # and not at the pass drain (~10 mV, against a 5 mV line).  So the track is escaped to the
    # right edge, beside the `vout` pin, and LABELLED THERE.  The run is the track's own 0.2 um
    # Metal1 (~104 Ohm), which at the divider's 1.2 uA is a 0.13 mV STATIC offset, not a
    # load-dependent one — the pin is what the loop regulates.  The cell's interface contract now
    # says where the tap is in geometry, not in prose.
    b.track_pts["lp_brk"].append(_s(x_right - 1.0))
    for t in TRACKS:
        xs = b.track_pts[t]
        if not xs:
            raise AssertionError(f"net {t} has no terminals")
        lay = TRACK_LAYER.get(t)
        if lay is None:
            b.m1h(b.track_y[t], min(xs) - VPAD / 2, max(xs) + VPAD / 2)
        else:
            b.h(lay + "drawing", b.track_y[t], min(xs), max(xs), W_TRK_UP)
            b.claim_box(lay, t, min(xs) - W_TRK_UP / 2, b.track_y[t] - W_TRK_UP / 2,
                        max(xs) + W_TRK_UP / 2, b.track_y[t] + W_TRK_UP / 2)
    # Label EVERY track, not just the pins: the extractor names a net after its label, which is
    # what makes the per-net C table readable and lets the post-layout deck re-attach the MIM
    # capacitors (stripped before extraction) to `ea_out`/`ea_o1`/`fb` by name.
    for t in TRACKS:
        xs = b.track_pts[t]
        lay = (TRACK_LAYER.get(t) or "Metal1") + "text"
        # A1 puts `vref` and `fb` on the LEFT edge (review-003 F13): label them at the left end of
        # their own track, not mid-channel, so the declared pin side is the drawn one.
        xl = min(xs) if t in ("vref", "fb") else (min(xs) + max(xs)) / 2
        if t == "lp_brk":
            xl = max(xs)
        b.label(t, xl, b.track_y[t], lay)
    # pin frame: vdd top (TopMetal1), vss bottom (Metal1), vout right (TopMetal1), fb/vref left
    b.label("vdd", _s(x_left + 6.0), y_s_band, "TopMetal1text")
    b.label("vout", _s(x_right - p.pwr_w / 2), _s(y_vss), "TopMetal1text")
    # ONE `vss` label (F9): with two, which one is the pin — and therefore what the return
    # resistance of the cell is — was ambiguous.  The pin is the bottom edge, as PLAN A1 says,
    # and specifically the FOOT OF THE RISER, which is what makes the active return and the
    # XCOUT return meet only at the pin.
    b.label("vss", x_ret_l, y_bot)
    b.label("vdd", _s(x_left + 6.0), y_vdd)
    b.check()
    return b.c, b


def build(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None) -> gf.Component:
    return build_full(p, sizing)[0]


def write_lvs_reference(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None,
                        out: str | os.PathLike | None = None, builder: Builder | None = None) -> str:
    """The LVS reference for THIS build: the certified netlist (via `netlist_ref`) plus the
    dummy devices this generator actually drew."""
    sz = {**SIZING, **(sizing or {})}
    b = builder or build_full(p, sizing)[1]
    text = NR.lvs_reference(sz, b.dummies)
    if out is not None:
        Path(out).write_text(text)
    return text


def power_budgets(p: LayoutParams = LayoutParams(), sizing: dict[str, object] | None = None,
                  builder: Builder | None = None) -> list[dict]:
    """Every current-carrying segment this build drew, as `current_density.Budget` kwargs.

    Derived from the drawn geometry and `LayoutParams`, never retyped: `layout/signoff.py` turns
    this into the blocking current-density stage (review-002 B1)."""
    b = builder or build_full(p, sizing)[1]
    return b.budgets


def main() -> None:
    ap = argparse.ArgumentParser(description=f"Generate {CELL} (gdsfactory, IHP SG13G2)")
    # A GDS is regenerable output, not an artefact: default it to the neutral working root
    # ($SX_SCRATCH/ldo-adb/layout, the same place signoff.py builds into) rather than into the
    # entry beside this file, where it would be a megabyte of untracked binary in the repo tree.
    _work = Path(os.environ.get("SX_SCRATCH", str(Path.home() / "sx-scratch"))) / "ldo-adb" / "layout"
    ap.add_argument("-o", "--out", default=str(_work / f"{CELL}.gds"))
    ap.add_argument("--params", default=None, help="JSON overrides for LayoutParams")
    ap.add_argument("--sizing", default=None, help="JSON file of sizing knobs (Design.knobs())")
    ap.add_argument("--lvs", default=None, help="also write the LVS reference netlist here")
    ap.add_argument("--power", default=None, help="also write the power-path budget JSON here")
    a = ap.parse_args()
    p = LayoutParams(**json.loads(a.params)) if a.params else LayoutParams()
    sizing = json.loads(Path(a.sizing).read_text()) if a.sizing else None
    comp, b = build_full(p, sizing)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    comp.write_gds(a.out)
    bb = comp.bbox()
    print(f"wrote {a.out}; bbox um: ({bb.left:.2f},{bb.bottom:.2f})-({bb.right:.2f},{bb.top:.2f}); "
          f"area um2: {(bb.right - bb.left) * (bb.top - bb.bottom):.0f}")
    if a.lvs:
        write_lvs_reference(p, sizing, a.lvs, builder=b)
        print("wrote", a.lvs)
    if a.power:
        Path(a.power).write_text(json.dumps(power_budgets(p, sizing, builder=b), indent=1) + "\n")
        print("wrote", a.power)


if __name__ == "__main__":
    main()
