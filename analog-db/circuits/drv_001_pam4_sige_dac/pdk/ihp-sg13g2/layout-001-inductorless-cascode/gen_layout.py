#!/usr/bin/env python3
"""Parameterized gdsfactory layout for the PAM-4 driver DUTs (IHP sg13g2 HBT).

Generates DRC/LVS-clean layouts for the three DUTs of the ported EuMIC-2022
PAM-4 driver (`../dut/dut_{lsb,msb,pam4}.spice`):

    lsb   1 gain cell            msb   2 gain cells       pam4  M0 | L0 | M1
    (Fig 2a)                     (Fig 2b)                 (Fig 1, 2-bit DAC)

One gain cell = differential cascode quad (4x npn13G2 Nx=3, foundry PyCell via
ihp-gdsfactory cells2) + 2x RE (rsil) + Cdeg (cmim) + tail node (exposed as a
port — the tail current source is ideal/off-chip, as in the schematic DUTs).
DUT level adds the shared RC pair (rsil), RB terminations (rsil), vcc/vcmb
rails, differential input (Metal3) and output (TopMetal1) buses, a vcc rail on
TopMetal2 and a p-substrate guard ring (labelled `sub`).

RF-driven layout choices (see README):
  - strict mirror symmetry of each differential pair about the cell axis
  - cascode c1/c2 nodes as short wide Metal2 plates (low-L, low-R, the
    Miller-critical node stays sub-3 um long)
  - outputs rise straight to thick TopMetal1 buses; vcc rail on TopMetal2
    (2/3 um thick metals for the 48 mA DC + RF current)
  - via *arrays* (not single vias) on every DC-current path
  - p-sub guard ring around the block + substrate tap columns between cells
    (substrate reference + isolation)

Every free spacing/width is a field of `LayoutParams` -> the search space for
the PEX+sim optimization loop (optimize_layout.py). The generator also emits,
from the same in-memory device records, a matching LVS reference netlist
(primitive Q/R/C cards, KLayout-LVS format) and an ngspice-runnable sim
netlist (X-cards on the PDK models) per DUT — layout and netlists cannot
drift apart.

    python gen_layout.py --dut all                 # -> out/dut_*.gds + netlists
    python gen_layout.py --dut lsb --params '{"gap_x": 8.0}'
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os

import gdsfactory as gf
import klayout.db as kdb
from ihp import PDK
from ihp import cells as C
import ihp.cells2.bjt_transistors as B2

PDK.activate()

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- constants
RSH_RSIL = 7.0          # rsil sheet resistance, ohm/sq (typ)
RZ_RSIL = 4.5           # rsil contact-head resistance, ohm*um per end
CMIM_EXT = 0.72         # extracted cap_cmim w = drawn width + 0.72 (MIM layer)
CMIM_FF_UM2 = 1.552     # cap_cmim density on the effective (drawn+0.72) area
HBT_LE, HBT_WE = 0.9, 0.07   # npn13G2 emitter mask (fixed device)
FINGER_PITCH = 1.85     # npn13G2 emitter finger pitch (x)

# metal stack (bottom -> top) + via rules: (name, size, pitch, encl_lo, encl_hi)
LEVELS = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5",
          "TopMetal1", "TopMetal2"]
VIAS = [("Via1", 0.19, 0.50, 0.10, 0.10),
        ("Via2", 0.19, 0.50, 0.10, 0.10),
        ("Via3", 0.19, 0.50, 0.10, 0.10),
        ("Via4", 0.19, 0.50, 0.10, 0.10),
        ("TopVia1", 0.42, 1.00, 0.15, 0.30),
        ("TopVia2", 0.90, 2.00, 0.50, 0.50)]
MIN_W = {"Metal1": 0.2, "Metal2": 0.2, "Metal3": 0.2, "Metal4": 0.2,
         "Metal5": 0.2, "TopMetal1": 1.64, "TopMetal2": 2.0}
TEXT_LAYER = {"Metal1": "Metal1text", "Metal2": "Metal2text",
              "Metal3": "Metal3text", "Metal4": "Metal4text",
              "Metal5": "Metal5text",
              "TopMetal1": "TopMetal1text", "TopMetal2": "TopMetal2text"}


def snap(v: float) -> float:
    """Snap to the sg13g2 0.005 um manufacturing grid."""
    return round(round(v / 0.005) * 0.005, 3)


# ---------------------------------------------------------------- parameters
@dataclasses.dataclass(frozen=True)
class LayoutParams:
    """Free layout constants (um) — the optimizer search space."""

    # cell floorplan
    gap_x: float = 7.0      # inner gap between the two devices of a pair
    row_gap: float = 1.6    # input row top -> cascode row bottom
    cell_gap: float = 6.0   # gap between neighbouring gain cells
    # ---- electrical sizing knobs (netlists re-derive automatically) ----
    nx: int = 3             # npn13G2 emitter fingers (1..10; I_C < 3*Nx mA)
    re_ohm: float = 2.5     # emitter degeneration per side
    rc_ohm: float = 50.0    # collector load per side
    rb_ohm: float = 50.0    # input termination per side
    cdeg_ff: float = 20.0   # emitter bridging cap (cmim width derives)
    # resistor widths (lengths follow from R target and the rsil model)
    re_w: float = 5.0       # RE path carries the 16 mA/cell tail current
    rc_w: float = 1.4       # RC carries up to 24 mA DC each
    rb_w: float = 0.5       # RB carries ~uA
    # wire widths
    w_m1: float = 0.4       # base input drop (Metal1)
    w_e: float = 2.0        # emitter Metal2 strap
    w_out: float = 2.0      # output Metal2 riser
    w_cap_arm: float = 1.0  # cap M5/M2 arms
    # vertical clearances
    re_gap: float = 1.2     # HBT row bottom -> RE P2 port
    tail_gap: float = 0.8   # RE P1 -> tail bus top
    tail_h: float = 1.0     # tail bus bar height
    in_off: float = 1.5     # tail bus bottom -> first input bus
    in_bus_w: float = 0.6   # input bus width (Metal3)
    in_bus_gap: float = 0.8
    # input-network RF options (layout-expert review, 2026-08-09):
    #  - input_feed "center": R_B columns on the block centreline, buses
    #    branch symmetrically (H-tree) -> halves the input line per branch,
    #    zeroes M0/M1 skew (edge feed gave the far MSB cell an ~80 um stub)
    #  - in_shield: grounded (vcmb-tied) Metal3 line between the MSB and
    #    LSB channel rows -> kills the lsbn<->msbp inter-channel coupling
    #  - in_bus_m4: stitch Metal4 over each Metal3 bus (halves bus R)
    # pam4 bus rows are ordered msbp|msbn|lsbp|lsbn (MSB innermost/topmost:
    # the MSB port dominates the S11 budget, so it gets the short drops).
    input_feed: str = "edge"
    in_shield: bool = False
    in_bus_m4: bool = False
    in_bus_layer: str = "Metal3"   # "Metal4": ~0.5 fF/net less substrate C
    drop_layer: str = "Metal1"     # "Metal2": lower-C base-drop descents
    rb_gap: float = 1.2     # lowest input bus -> RB top port
    rb_pitch: float = 2.4   # RB column pitch (x)
    vcmb_gap: float = 1.2   # RB P1 -> vcmb rail
    vcmb_w: float = 0.8
    sub_off: float = 1.4    # cascode row top -> substrate bus (Metal2)
    sub_w: float = 0.8
    out_off: float = 2.0    # substrate bus -> outp bus (out_layer)
    out_w: float = 2.0
    out_gap: float = 1.8    # outp bus <-> outn bus edge gap
    # output-bus metal: TopMetal1 (default) or TopMetal2. TM2 sits ~3 um
    # higher above the substrate, cutting the summing-bus C that dominates
    # post-layout S22. With TM2, out_w/out_gap must be >= 2.0 (TM2 min
    # width/space) and rc_sep should be ~4 so the isolated TM1 pads of the
    # riser/RC via stacks stay >= 1.64 um apart (TM1 space rule).
    out_layer: str = "TopMetal1"
    rc_sep: float = 8.0     # RCp <-> RCn column separation
    rc_gap: float = 2.0     # outn bus top -> RC body
    vcc_w: float = 5.0      # vcc rail (TopMetal2)
    ring_margin: float = 3.0
    ring_w: float = 1.0
    stack_w: float = 2.0    # default via-stack pad size


def res_len(r_ohm: float, w: float) -> float:
    """rsil body length for a TOTAL resistance target, accounting for the
    two contact heads (R = rsh*l/w + 2*RZ/w). Body length floors at 0.5 um
    — pick a width w > (0.5*rsh + 2*RZ)/R for low-ohmic resistors."""
    l = (r_ohm * w - 2 * RZ_RSIL) / RSH_RSIL
    if l < 0.5 - 1e-9:
        raise ValueError(
            f"rsil width {w} um too narrow for {r_ohm} ohm total "
            f"(need w >= {(0.5 * RSH_RSIL + 2 * RZ_RSIL) / r_ohm:.2f} um)")
    # 0.01 grid: the rsil cell halves this internally (0.005 mfg grid)
    return round(round(l / 0.01) * 0.01, 2)


def cap_drawn_w(c_ff: float) -> float:
    """cmim drawn width for a target capacitance (effective area model:
    C = CMIM_FF_UM2 * (w_drawn + CMIM_EXT)^2; 20 fF -> 2.87 um)."""
    w = (c_ff / CMIM_FF_UM2) ** 0.5 - CMIM_EXT
    if w < 1.2:
        raise ValueError(f"cdeg {c_ff} fF below the min cmim size")
    return round(round(w / 0.01) * 0.01, 2)


# ---------------------------------------------------------------- draw utils
def rect(c: gf.Component, layer: str, x0: float, y0: float,
         x1: float, y1: float) -> None:
    x0, x1 = sorted((snap(x0), snap(x1)))
    y0, y1 = sorted((snap(y0), snap(y1)))
    c.add_polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer=layer)


def via_fill(c: gf.Component, via: str, size: float, pitch: float,
             x0: float, y0: float, x1: float, y1: float) -> None:
    """Fill [x0,x1]x[y0,y1] with a centred array of square vias."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    w, h = x1 - x0, y1 - y0
    nx = max(1, int((w - size) / pitch) + 1)
    ny = max(1, int((h - size) / pitch) + 1)
    ox = (x0 + x1) / 2 - (nx - 1) * pitch / 2
    oy = (y0 + y1) / 2 - (ny - 1) * pitch / 2
    for i in range(nx):
        for j in range(ny):
            cx, cy = ox + i * pitch, oy + j * pitch
            rect(c, f"{via}drawing", cx - size / 2, cy - size / 2,
                 cx + size / 2, cy + size / 2)


def via12(c: gf.Component, x0: float, y0: float, x1: float, y1: float,
          draw_pads: bool = True) -> None:
    """Metal1<->Metal2 via array over the given rect (pads included)."""
    if draw_pads:
        rect(c, "Metal1drawing", x0, y0, x1, y1)
        rect(c, "Metal2drawing", x0, y0, x1, y1)
    via_fill(c, "Via1", 0.19, 0.50, x0 + 0.1, y0 + 0.1, x1 - 0.1, y1 - 0.1)


def place_at(ref, port: str, x: float, y: float) -> None:
    """Move a component reference so that its named port lands at (x, y)."""
    px, py = ref.ports[port].center
    ref.dmove((snap(x - px), snap(y - py)))


def stack(c: gf.Component, x: float, y: float, lo: str, hi: str,
          w: float = 2.0) -> None:
    """Full via stack from metal `lo` up to metal `hi` centred at (x, y).

    Pads are clamped per level to the via's size + enclosure requirement
    (a small `w` must not under-enclose e.g. TopVia2: 0.9 + 2x0.5)."""
    i0, i1 = LEVELS.index(lo), LEVELS.index(hi)
    assert i0 < i1
    need: dict[int, float] = {}
    for lev in range(i0, i1):
        via, size, pitch, encl, encl_hi = VIAS[lev]
        pad = max(w, size + 2 * max(encl, encl_hi))
        need[lev] = max(need.get(lev, 0.0), pad)
        need[lev + 1] = max(need.get(lev + 1, 0.0), pad)
    for lev in range(i0, i1 + 1):
        name = LEVELS[lev]
        ww = max(need.get(lev, w), MIN_W[name])
        rect(c, f"{name}drawing", x - ww / 2, y - ww / 2, x + ww / 2, y + ww / 2)
    for lev in range(i0, i1):
        via, size, pitch, encl, encl_hi = VIAS[lev]
        ww = max(need[lev], MIN_W[LEVELS[lev]], MIN_W[LEVELS[lev + 1]])
        e = max(encl, encl_hi)
        via_fill(c, via, size, pitch, x - ww / 2 + e, y - ww / 2 + e,
                 x + ww / 2 - e, y + ww / 2 - e)


def comp_layer_bbox(comp: gf.Component, layer: str):
    """Bbox of one drawn layer of a component, in um (None if empty)."""
    info = gf.get_layer_info(layer)
    idx = comp.kcl.layout.layer(kdb.LayerInfo(info.layer, info.datatype))
    reg = kdb.Region(comp.kdb_cell.begin_shapes_rec(idx))
    if reg.is_empty():
        return None
    b = reg.bbox()
    return (b.left / 1000, b.bottom / 1000, b.right / 1000, b.top / 1000)


# ---------------------------------------------------------------- HBT helper
def hbt_cell(nx: int) -> gf.Component:
    return B2.npn13G2(Nx=nx, emitter_width=HBT_WE, emitter_length=HBT_LE)


def place_hbt(c: gf.Component, comp: gf.Component, x_center: float,
              y_bottom: float, span: float):
    """Place one npn13G2 with its device center at x_center, bbox bottom at
    y_bottom, and overlay the Metal1 patches that fix the PyCell's CntB.h1
    (Metal1 enclosure of ContBar) violations on the B and C bar rows."""
    ref = c << comp
    b = ref.bbox()
    ref.dmove((snap(x_center - (b.left + b.right) / 2),
               snap(y_bottom - b.bottom)))
    bx, by = ref.ports["B"].center
    cx, cy = ref.ports["C"].center
    # patches (same-net overlays, stay inside the cell's own metal x-extent)
    rect(c, "Metal1drawing", bx - span / 2 - 0.85, by - 0.13,
         bx + span / 2 + 0.85, by + 0.13)
    rect(c, "Metal1drawing", cx - span / 2 - 0.87, cy - 0.24,
         cx + span / 2 + 0.87, cy + 0.22)
    return ref


# ---------------------------------------------------------------- cell build
def place_cell(c: gf.Component, X: float, y0: float, p: LayoutParams,
               geo: dict, nets: dict, rec: dict) -> dict:
    """One differential cascode gain cell centred at X, input row bottom at y0.

    nets: {"inp": .., "inn": .., "tail": .., "prefix": ..}
    Returns per-cell hookup info (drop x positions, riser x positions).
    """
    span = geo["span"]
    hbt = geo["hbt"]
    half = geo["half"]
    dev_cx = p.gap_x / 2 + half
    y1 = y0 + geo["H"] + p.row_gap
    pre = nets["prefix"]

    q1 = place_hbt(c, hbt, X - dev_cx, y0, span)
    q2 = place_hbt(c, hbt, X + dev_cx, y0, span)
    q3 = place_hbt(c, hbt, X - dev_cx, y1, span)
    q4 = place_hbt(c, hbt, X + dev_cx, y1, span)

    # device records (schematic names match ../dut/dut_*.spice)
    rec["hbt"] += [
        (f"Q1{pre}", f"c1{pre}", nets["inp"], f"e1{pre}"),
        (f"Q2{pre}", f"c2{pre}", nets["inn"], f"e2{pre}"),
        (f"Q3{pre}", "outp", "vcasc", f"c1{pre}"),
        (f"Q4{pre}", "outn", "vcasc", f"c2{pre}"),
    ]

    # --- cascode nodes c1/c2: wide M2 plate, Q_in C strip -> Q_cas E plate ---
    for qin, qcas in ((q1, q3), (q2, q4)):
        qcx, qcy = qin.ports["C"].center
        qey = qcas.ports["E"].center[1]
        via12(c, qcx - span / 2 - 0.6, qcy - 0.20, qcx + span / 2 + 0.6,
              qcy + 0.20, draw_pads=False)
        rect(c, "Metal2drawing", qcx - span / 2 - 0.7, qcy - 0.20,
             qcx + span / 2 + 0.7, qey + 0.72)

    # --- vcasc: M1 strap along the cascode B bar row across the cell ---
    bx3, by3 = q3.ports["B"].center
    bx4, _ = q4.ports["B"].center
    rect(c, "Metal1drawing", bx3 - span / 2 - 0.97, by3 - 0.12,
         bx4 + span / 2 + 0.97, by3 + 0.12)

    # --- emitters down to RE, tail bus (rsil P1 = top port, P2 = bottom) ---
    dy_re = res_len(p.re_ohm, p.re_w)
    y_re_top = y0 - p.re_gap                 # RE top port (P1) center
    y_re_bot = y_re_top - dy_re - 0.4        # RE bottom port (P2) center
    re_comp = C.rsil(dx=p.re_w, dy=dy_re)
    w_via = min(p.re_w, p.w_e) - 0.2
    for qin, side, enet in ((q1, -1, f"e1{pre}"), (q2, +1, f"e2{pre}")):
        ex, ey = qin.ports["E"].center
        r = c << re_comp
        place_at(r, "P1", ex, y_re_top)
        # M2 strap from E plate down over the P1 head + via array there
        rect(c, "Metal2drawing", ex - p.w_e / 2, y_re_top - 0.35,
             ex + p.w_e / 2, ey - 0.70)
        via12(c, ex - w_via / 2, y_re_top - 0.25,
              ex + w_via / 2, y_re_top + 0.25, draw_pads=False)
        rect(c, "Metal1drawing", ex - w_via / 2, y_re_top - 0.25,
             ex + w_via / 2, y_re_top + 0.25)
        # tail riser: P2 down to the tail bus
        rect(c, "Metal1drawing", ex - p.re_w / 2, geo["y_tail"] - p.tail_h,
             ex + p.re_w / 2, y_re_bot + 0.25)
        rec["res"].append((f"RE{1 if side < 0 else 2}{pre}", enet,
                           nets["tail"], p.re_w, dy_re))
    # tail bus + label
    rect(c, "Metal1drawing", X - dev_cx - p.re_w / 2, geo["y_tail"] - p.tail_h,
         X + dev_cx + p.re_w / 2, geo["y_tail"])
    c.add_label(text=nets["tail"], position=(X, geo["y_tail"] - p.tail_h / 2),
                layer="Metal1text")

    # --- Cdeg: single cmim at the cell center, M5 arm -> e1, TM1 arm -> e2 ---
    cap_w = cap_drawn_w(p.cdeg_ff)
    cap = C.cmim(width=cap_w, length=cap_w)
    cr = c << cap
    cb0 = cr.bbox()
    e_y = q1.ports["E"].center[1]
    offx = snap(X - (cb0.left + cb0.right) / 2)
    offy = snap(e_y - (cb0.bottom + cb0.top) / 2)
    cr.dmove((offx, offy))
    cb = cr.bbox()
    # placed plate extents (the plates are not centred in the cell bbox)
    tm1 = comp_layer_bbox(cap, "TopMetal1drawing")
    tm1_r = tm1[2] + offx                    # placed TM1 top-plate right edge
    tm1_h = tm1[3] - tm1[1]                  # top-plate height
    xs = (cb.right - cb.left) / 2 + 1.6      # stack columns just outside cap
    w_eff = snap(cap_w + CMIM_EXT)
    e_in_l = q1.ports["E"].center[0] + span / 2 + 0.925      # inner plate edge
    e_in_r = q2.ports["E"].center[0] - span / 2 - 0.925
    # left: e1 strap (M2) -> stack M2->M5 -> M5 arm onto the bottom plate
    stack(c, X - xs, e_y, "Metal2", "Metal5", p.stack_w)
    rect(c, "Metal2drawing", e_in_l - 0.5, e_y - p.w_cap_arm / 2,
         X - xs, e_y + p.w_cap_arm / 2)
    rect(c, "Metal5drawing", X - xs, e_y - p.w_cap_arm / 2,
         cb.left + 0.4, e_y + p.w_cap_arm / 2)
    # right: e2 strap (M2) -> stack M2->TM1 -> TM1 arm onto the top plate.
    # The arm is one flush full-height rect from the plate to past the stack
    # pad (any notch narrower than 1.64 um would violate TM1.b).
    stack(c, X + xs, e_y, "Metal2", "TopMetal1", p.stack_w)
    rect(c, "Metal2drawing", X + xs, e_y - p.w_cap_arm / 2,
         e_in_r + 0.5, e_y + p.w_cap_arm / 2)
    arm_h = max(tm1_h, max(p.stack_w, MIN_W["TopMetal1"]))
    rect(c, "TopMetal1drawing", tm1_r - 0.4, e_y - arm_h / 2,
         X + xs + max(p.stack_w, MIN_W["TopMetal1"]) / 2, e_y + arm_h / 2)
    rec["cap"].append((f"Cdeg{pre}", f"e2{pre}", f"e1{pre}", w_eff))

    # --- base input drops (M1) down to the input buses. The drop column
    # must clear the RE head / tail riser / tail bus (all re_w/2 wide about
    # the device center), so it sits outboard of both — with a short M1
    # extension of the B bar strip out to the drop x when needed. ---
    drops = []
    drop_hw = 0.35 if p.drop_layer == "Metal2" else p.w_m1 / 2
    x_off = max(span / 2 + 0.5, p.re_w / 2 + 0.3 + drop_hw)
    for qin, net in ((q1, nets["inp"]), (q2, nets["inn"])):
        qbx, qby = qin.ports["B"].center
        out = -1 if qbx < X else +1
        xd = qbx + out * x_off
        yb = geo["bus_y"][net]
        rect(c, "Metal1drawing", qbx + out * span / 2, qby - 0.15,
             xd + out * p.w_m1 / 2, qby + 0.15)
        if p.drop_layer == "Metal2":
            # descend on M2 (lower substrate C than M1): M1 stub below the
            # bar, M1->M2 via just under it (clear of the C-strap row above)
            rect(c, "Metal1drawing", xd - 0.35, qby - 0.7,
                 xd + 0.35, qby + 0.21)
            via12(c, xd - 0.3, qby - 0.7, xd + 0.3, qby - 0.2)
            rect(c, "Metal2drawing", xd - p.w_m1 / 2, yb - 0.5,
                 xd + p.w_m1 / 2, qby - 0.2)
            stack(c, xd, yb, "Metal2", p.in_bus_layer, 1.0)
        else:
            rect(c, "Metal1drawing", xd - p.w_m1 / 2, yb - 0.6,
                 xd + p.w_m1 / 2, qby + 0.12)
            stack(c, xd, yb, "Metal1", p.in_bus_layer, 1.0)
        drops.append((xd, net))

    # --- output risers (M2) from cascode C strips up to the TM1 buses ---
    risers = []
    for qcas, net, ybus in ((q3, "outp", geo["y_outP"]),
                            (q4, "outn", geo["y_outN"])):
        qcx, qcy = qcas.ports["C"].center
        via12(c, qcx - span / 2 - 0.6, qcy - 0.20, qcx + span / 2 + 0.6,
              qcy + 0.20, draw_pads=False)
        rect(c, "Metal2drawing", qcx - span / 2 - 0.7, qcy - 0.22,
             qcx + span / 2 + 0.7, qcy + 0.22)
        rect(c, "Metal2drawing", qcx - p.w_out / 2, qcy,
             qcx + p.w_out / 2, ybus)
        stack(c, qcx, ybus, "Metal2", p.out_layer, p.stack_w)
        risers.append((qcx, net))

    return {"drops": drops, "risers": risers,
            "vcasc_x": (bx3 - span / 2 - 0.97, bx4 + span / 2 + 0.97),
            "vcasc_y": by3}


# ---------------------------------------------------------------- DUT build
DUTS = {
    "lsb": {"cells": [("L0", "in", "tail")],
            "inputs": ["inp", "inn"],
            "subckt": "pam4drv_lsb_lay"},
    "msb": {"cells": [("M0", "in", "tail0"), ("M1", "in", "tail1")],
            "inputs": ["inp", "inn"],
            "subckt": "pam4drv_msb_lay"},
    "pam4": {"cells": [("M0", "msb", "tmsb0"), ("L0", "lsb", "tlsb0"),
                       ("M1", "msb", "tmsb1")],
             "inputs": ["lsbp", "lsbn", "msbp", "msbn"],
             "subckt": "pam4drv_pam4_lay"},
}


def input_nets_of(dut: str, group: str) -> tuple[str, str]:
    if dut != "pam4":
        return "inp", "inn"
    return (f"{group}p", f"{group}n")


def build_dut(dut: str, p: LayoutParams = LayoutParams()):
    spec = DUTS[dut]
    c = gf.Component(spec["subckt"])
    rec = {"hbt": [], "res": [], "cap": []}

    # --- geometry constants derived from a template HBT ---
    hbt = hbt_cell(p.nx)
    hb = hbt.bbox()
    H = hb.top - hb.bottom
    span = (p.nx - 1) * FINGER_PITCH
    half = (hb.right - hb.left) / 2
    cell_w = p.gap_x + 4 * half
    n = len(spec["cells"])
    pitch = cell_w + p.cell_gap
    Xs = [(i - (n - 1) / 2) * pitch for i in range(n)]

    # vertical zone map
    dy_re = res_len(p.re_ohm, p.re_w)
    dy_rb = res_len(p.rb_ohm, p.rb_w)
    dy_rc = res_len(p.rc_ohm, p.rc_w)
    y0 = 0.0
    y1 = y0 + H + p.row_gap
    y_tail = y0 - p.re_gap - dy_re - 0.4 - p.tail_gap        # tail bus top
    bus_y = {}
    rows = (["msbp", "msbn", "lsbp", "lsbn"] if dut == "pam4"
            else list(spec["inputs"]))
    if p.in_shield and dut == "pam4":
        rows.insert(2, "__shield__")
    yb = y_tail - p.tail_h - p.in_off - p.in_bus_w / 2
    y_shield = None
    yy = yb
    for net in rows:
        if net == "__shield__":
            y_shield = yy
        else:
            bus_y[net] = yy
        yy -= (p.in_bus_w + p.in_bus_gap)
    y_bus_lo = min(list(bus_y.values())
                   + ([y_shield] if y_shield is not None else []))
    y_rb_p2 = y_bus_lo - p.in_bus_w / 2 - p.rb_gap
    y_rb_p1 = y_rb_p2 - dy_rb - 0.4
    y_vcmb = y_rb_p1 - p.vcmb_gap
    y_sub = y1 + H + p.sub_off
    y_outP = y_sub + p.sub_w / 2 + p.out_off + p.out_w / 2
    y_outN = y_outP + p.out_w + p.out_gap
    y_rc_p1 = y_outN + p.out_w / 2 + p.rc_gap
    y_rc_p2 = y_rc_p1 + dy_rc + 0.4
    y_vcc = y_rc_p2

    geo = {"H": H, "span": span, "half": half, "hbt": hbt,
           "y_tail": y_tail, "bus_y": bus_y,
           "y_outP": y_outP, "y_outN": y_outN}

    # --- gain cells ---
    infos = []
    for (prefix, group, tail), X in zip(spec["cells"], Xs):
        inp, inn = input_nets_of(dut, group)
        infos.append(place_cell(c, X, y0, p, geo,
                                {"inp": inp, "inn": inn, "tail": tail,
                                 "prefix": prefix}, rec))

    # --- vcasc: per-cell M1 segments, extended into the gaps and bridged
    # on M2 only over the narrow substrate-tap corridor at each gap center
    # (a wide bridge would collide with the HBT E-columns / c-straps) ---
    yv = infos[0]["vcasc_y"]
    gap_xs = [(Xs[i] + Xs[i + 1]) / 2 for i in range(n - 1)]
    for (a, b), xg in zip(zip(infos[:-1], infos[1:]), gap_xs):
        xa, xb = a["vcasc_x"][1], b["vcasc_x"][0]
        rect(c, "Metal1drawing", xa, yv - 0.12, xg - 0.55, yv + 0.12)
        rect(c, "Metal1drawing", xg + 0.55, yv - 0.12, xb, yv + 0.12)
        via12(c, xg - 1.5, yv - 0.3, xg - 0.7, yv + 0.3)
        via12(c, xg + 0.7, yv - 0.3, xg + 1.5, yv + 0.3)
        rect(c, "Metal2drawing", xg - 1.45, yv - 0.2, xg + 1.45, yv + 0.2)
    x_vcasc_lbl = infos[0]["vcasc_x"][0] - 1.5
    rect(c, "Metal1drawing", x_vcasc_lbl, yv - 0.12,
         infos[0]["vcasc_x"][0], yv + 0.12)
    c.add_label(text="vcasc", position=(x_vcasc_lbl + 0.3, yv),
                layer="Metal1text")

    # --- RB block + input buses (Metal3, optional M4 stitch + shield) ---
    n_in = len(spec["inputs"])
    if p.input_feed == "center":
        x_rb0 = -(n_in - 1) * p.rb_pitch / 2       # H-tree: R_B on centreline
    else:
        x_rb0 = Xs[0] - cell_w / 2 - n_in * p.rb_pitch - 1.0
    rb_x = {}
    for i, net in enumerate(spec["inputs"]):
        rb_x[net] = x_rb0 + i * p.rb_pitch
    x_drop_max = max(x for info in infos for x, _ in info["drops"])
    rb_comp = C.rsil(dx=p.rb_w, dy=dy_rb)
    x_bus_lo_all, x_bus_hi_all = 1e9, -1e9
    for net in spec["inputs"]:
        xr = rb_x[net]
        # bus spans the R_B column and every drop of that net
        net_drops = [x for info in infos for x, nd in info["drops"] if nd == net]
        xs_all = (net_drops if net_drops else [x_drop_max]) + [xr]
        x_lo, x_hi = min(xs_all) - 1.0, max(xs_all) + 1.0
        x_bus_lo_all = min(x_bus_lo_all, x_lo)
        x_bus_hi_all = max(x_bus_hi_all, x_hi)
        rect(c, f"{p.in_bus_layer}drawing", x_lo,
             bus_y[net] - p.in_bus_w / 2, x_hi, bus_y[net] + p.in_bus_w / 2)
        if p.in_bus_m4 and p.in_bus_layer == "Metal3":
            rect(c, "Metal4drawing", x_lo, bus_y[net] - p.in_bus_w / 2,
                 x_hi, bus_y[net] + p.in_bus_w / 2)
            via_fill(c, "Via3", 0.19, 0.50, x_lo + 0.1,
                     bus_y[net] - p.in_bus_w / 2 + 0.1, x_hi - 0.1,
                     bus_y[net] + p.in_bus_w / 2 - 0.1)
        c.add_label(text=net, position=(xr, bus_y[net]),
                    layer=TEXT_LAYER[p.in_bus_layer])
        # bus -> RB.P1 (top) -> RB -> P2 (bottom) -> vcmb rail
        stack(c, xr, bus_y[net], "Metal1", p.in_bus_layer, 1.0)
        r = c << rb_comp
        place_at(r, "P1", xr, y_rb_p2)
        rect(c, "Metal1drawing", xr - p.w_m1 / 2, y_rb_p2 - 0.1,
             xr + p.w_m1 / 2, bus_y[net] + 0.6)
        rect(c, "Metal1drawing", xr - p.w_m1 / 2, y_vcmb - p.vcmb_w / 2,
             xr + p.w_m1 / 2, y_rb_p1 + 0.25)
        rec["res"].append((f"Rb{net}", net, "vcmb", p.rb_w, dy_rb))
    # inter-channel shield line (vcmb-tied Metal3, both ends strapped)
    if y_shield is not None:
        rect(c, f"{p.in_bus_layer}drawing", x_bus_lo_all,
             y_shield - p.in_bus_w / 2, x_bus_hi_all,
             y_shield + p.in_bus_w / 2)
        for xt in (x_bus_lo_all + 0.6, x_bus_hi_all - 0.6):
            stack(c, xt, y_shield, "Metal1", p.in_bus_layer, 1.0)
            rect(c, "Metal1drawing", xt - 0.3, y_vcmb, xt + 0.3,
                 y_shield + 0.3)
    # vcmb rail (M1, full width incl. shield ties)
    x_right = Xs[-1] + cell_w / 2 + 1.0
    rect(c, "Metal1drawing", min(x_rb0, x_bus_lo_all) - 1.0,
         y_vcmb - p.vcmb_w / 2,
         max(x_right, x_bus_hi_all + 1.0), y_vcmb + p.vcmb_w / 2)
    c.add_label(text="vcmb", position=(0, y_vcmb), layer="Metal1text")

    # --- output buses (TopMetal1) ---
    x_bus_l = min(x for info in infos for x, _ in info["risers"]) - 1.5
    x_bus_r = max(x for info in infos for x, _ in info["risers"]) + 1.5
    x_bus_l = min(x_bus_l, -p.rc_sep / 2 - 2.0)
    x_bus_r = max(x_bus_r, p.rc_sep / 2 + 2.0)
    assert p.out_w >= MIN_W[p.out_layer], "out_w below out_layer min width"
    for net, yb2 in (("outp", y_outP), ("outn", y_outN)):
        rect(c, f"{p.out_layer}drawing", x_bus_l, yb2 - p.out_w / 2,
             x_bus_r, yb2 + p.out_w / 2)
        c.add_label(text=net, position=(x_bus_l + 1.0, yb2),
                    layer=TEXT_LAYER[p.out_layer])

    # --- RC pair: bus -> M1 riser -> rsil -> vcc rail (TopMetal2) ---
    rc_comp = C.rsil(dx=p.rc_w, dy=dy_rc)
    for xr, net, ybus in ((-p.rc_sep / 2, "outp", y_outP),
                          (p.rc_sep / 2, "outn", y_outN)):
        stack(c, xr, ybus, "Metal1", p.out_layer, p.stack_w)
        r = c << rc_comp
        place_at(r, "P2", xr, y_rc_p1)       # P2 = bottom port -> bus side
        rect(c, "Metal1drawing", xr - p.rc_w / 2, ybus,
             xr + p.rc_w / 2, y_rc_p1 + 0.25)
        rect(c, "Metal1drawing", xr - p.rc_w / 2, y_rc_p2 - 0.25,
             xr + p.rc_w / 2, y_rc_p2 + 0.25)
        stack(c, xr, y_rc_p2, "Metal1", "TopMetal2", p.stack_w)
        rec["res"].append((f"Rc{net[-1]}", net, "vcc", p.rc_w, dy_rc))
    # NOTE: schematic names Rcp/Rcn -> net outp/outn; record uses last char
    # vcc rail
    rect(c, "TopMetal2drawing", x_bus_l, y_vcc - p.vcc_w / 2,
         x_bus_r, y_vcc + p.vcc_w / 2)
    c.add_label(text="vcc", position=(0, y_vcc), layer="TopMetal2text")

    # --- substrate: tap columns in the cell gaps (Metal1 — the gaps are
    # free of M1 at the vcasc row because vcasc bridges the gaps on M2),
    # joined by a Metal3 sub bus above the cascode row (the M2 output
    # risers cross that height legally) ---
    tap = C.ptap1(width=0.78, length=1.4, rows=1, cols=1)
    for xg in gap_xs:
        for yt in (y0 + H / 2, y1 + H / 2):
            t = c << tap
            tb = t.bbox()
            t.dmove((snap(xg - (tb.left + tb.right) / 2),
                     snap(yt - (tb.bottom + tb.top) / 2)))
        rect(c, "Metal1drawing", xg - 0.25, y0 + H / 2, xg + 0.25, y_sub)
        stack(c, xg, y_sub, "Metal1", "Metal3", 1.2)

    # --- guard ring (p-sub) around everything, labelled `sub` ---
    # hand-drawn (the ihp guard_ring PyCell violates Cnt.b at its corners):
    # pSD band + Activ + Metal1 + a single Cont row per edge, corners kept
    # contact-free.
    b = c.bbox()
    m = p.ring_margin
    rw = max(p.ring_w, 1.0)
    x0r, y0r = b.left - m - rw, b.bottom - m - rw    # ring outer bbox
    x1r, y1r = b.right + m + rw, b.top + m + rw
    for (ax0, ay0, ax1, ay1) in (
            (x0r, y0r, x1r, y0r + rw),               # bottom
            (x0r, y1r - rw, x1r, y1r),               # top
            (x0r, y0r, x0r + rw, y1r),               # left
            (x1r - rw, y0r, x1r, y1r)):              # right
        rect(c, "pSDdrawing", ax0 - 0.1, ay0 - 0.1, ax1 + 0.1, ay1 + 0.1)
        rect(c, "Activdrawing", ax0, ay0, ax1, ay1)
        rect(c, "Metal1drawing", ax0, ay0, ax1, ay1)
        horiz = (ax1 - ax0) >= (ay1 - ay0)
        cy = (ay0 + ay1) / 2
        cx = (ax0 + ax1) / 2
        if horiz:
            via_fill(c, "Cont", 0.16, 0.40, ax0 + rw + 0.3, cy - 0.08,
                     ax1 - rw - 0.3, cy + 0.08)
        else:
            via_fill(c, "Cont", 0.16, 0.40, cx - 0.08, ay0 + rw + 0.3,
                     cx + 0.08, ay1 - rw - 0.3)
    # sub bus (M3) from ring rail to ring rail through the tap columns
    if gap_xs:
        rect(c, "Metal3drawing", x0r + rw / 2, y_sub - p.sub_w / 2,
             x1r - rw / 2, y_sub + p.sub_w / 2)
        for xe in (x0r + rw / 2, x1r - rw / 2):
            stack(c, xe, y_sub, "Metal1", "Metal3", max(1.2, rw))
    c.add_label(text="sub", position=((x0r + x1r) / 2, y0r + rw / 2),
                layer="Metal1text")

    return c, rec, {"y_vcc": y_vcc, "area": None}


# ---------------------------------------------------------------- netlists
def ports_of(dut: str) -> list[str]:
    spec = DUTS[dut]
    tails = [t for _, _, t in spec["cells"]]
    # dedupe, keep order
    tails = list(dict.fromkeys(tails))
    return spec["inputs"] + ["outp", "outn", "vcc", "vcasc", "vcmb"] + \
        tails + ["sub"]


def lvs_netlist(dut: str, rec: dict, p: LayoutParams) -> str:
    ae = HBT_LE * HBT_WE
    pe = 2 * (HBT_LE + HBT_WE)
    lines = [f"* LVS reference for {DUTS[dut]['subckt']} (generated"
             f" by gen_layout.py — matches the GDS exactly)",
             f".subckt {DUTS[dut]['subckt']} " + " ".join(ports_of(dut))]
    for name, cn, bn, en in rec["hbt"]:
        lines.append(f"Q{name} {cn} {bn} {en} sub npn13G2 "
                     f"AE={ae:.3f}p PE={pe:.2f}u M={p.nx}")
    for name, n1, n2, w, l in rec["res"]:
        lines.append(f"R{name} {n1} {n2} rsil w={w:g}u l={l:g}u m=1")
    for name, plus, minus, w_eff in rec["cap"]:
        lines.append(f"C{name} {plus} {minus} cap_cmim W={w_eff:g}u "
                     f"L={w_eff:g}u M=1")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def kpex_netlist(dut: str, rec: dict, p: LayoutParams) -> str:
    """LVS reference in klayout-pex flavour: identical to lvs_netlist() but
    resistors carry the substrate as an explicit 3rd node (the kpex sg13g2
    deck models poly resistors as 3-terminal devices)."""
    txt = lvs_netlist(dut, rec, p)
    out = []
    for line in txt.splitlines():
        toks = line.split()
        if toks and toks[0].startswith("R") and "rsil" in line:
            out.append(" ".join(toks[:3] + ["sub"] + toks[3:]))
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def sim_netlist(dut: str, rec: dict, p: LayoutParams) -> str:
    lines = [f"* pre-layout sim netlist for {DUTS[dut]['subckt']} — same "
             "devices as the LVS reference, on the PDK models",
             "* (rsil / cap_cmim / npn13G2 subckts; tails + sub are ports)",
             f".subckt {DUTS[dut]['subckt']} " + " ".join(ports_of(dut))]
    for name, cn, bn, en in rec["hbt"]:
        lines.append(f"X{name} {cn} {bn} {en} sub npn13G2 Nx={p.nx}")
    for name, n1, n2, w, l in rec["res"]:
        lines.append(f"XR{name} {n1} {n2} sub rsil w={w:g}u l={l:g}u m=1")
    for name, plus, minus, w_eff in rec["cap"]:
        lines.append(f"X{name} {plus} {minus} cap_cmim w={w_eff:g}u "
                     f"l={w_eff:g}u")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- main
def generate(dut: str, p: LayoutParams, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    # repeated in-process generation (notebook / optimizer loops): drop the
    # previous component cache or the fixed subckt cell name collides
    gf.clear_cache()
    comp, rec, meta = build_dut(dut, p)
    comp.flatten()
    gds = os.path.join(out_dir, f"dut_{dut}.gds")
    comp.write_gds(gds)
    b = comp.bbox()
    area = (b.right - b.left) * (b.top - b.bottom)
    with open(os.path.join(out_dir, f"dut_{dut}_lvs.spice"), "w") as f:
        f.write(lvs_netlist(dut, rec, p))
    with open(os.path.join(out_dir, f"dut_{dut}_kpex.spice"), "w") as f:
        f.write(kpex_netlist(dut, rec, p))
    with open(os.path.join(out_dir, f"dut_{dut}_sim.spice"), "w") as f:
        f.write(sim_netlist(dut, rec, p))
    n_dev = len(rec["hbt"]) + len(rec["res"]) + len(rec["cap"])
    print(f"[{dut}] wrote {gds}: {n_dev} devices, "
          f"bbox {b.right - b.left:.1f} x {b.top - b.bottom:.1f} um, "
          f"area {area:.0f} um2")
    return {"gds": gds, "area_um2": area, "cell": DUTS[dut]["subckt"]}


# --------------------------------------------------------------- final point
# Signoff point (2026-08-09): passes ALL 8 post-layout specs (kpex 2.5D CC,
# confirmed identical in RC mode) with DRC+LVS clean on all 3 DUTs.
# Electrically this RETURNS to the paper's nominal topology values
# (nx=3, R_C=50, R_B~50) — the earlier nx=2/R_C=70 point compensated layout
# deficiencies that the RF layout fixes below removed (center-fed H-tree
# input, M4 input buses, M2 base drops, light/wide-gap TM1 output buses,
# compacted row). R_E rises 2.5->3.2 ohm (S11: degeneration shrinks the
# effective input C); tail drops 16->15 mA/cell.
FINAL_LAYOUT = dict(nx=3, rc_ohm=50.0, rb_ohm=48.0, re_ohm=3.2, cdeg_ff=16.0,
                    re_w=4.5, out_gap=8.0, out_w=1.64, w_out=1.5, rc_sep=4.0,
                    stack_w=1.7, input_feed="center", in_bus_gap=3.0,
                    in_off=2.2, in_bus_layer="Metal4", gap_x=6.0,
                    cell_gap=5.0, drop_layer="Metal2")
FINAL_BIASES = {"vcc": 4.0, "vcasc": 3.35, "vcmb": 1.9, "tail_ma": 15.0}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dut", default="all",
                    choices=["lsb", "msb", "pam4", "all"])
    ap.add_argument("--params", default=None,
                    help='JSON overrides for LayoutParams, e.g. {"gap_x": 8}')
    ap.add_argument("--out-dir", default=os.path.join(HERE, "out"))
    a = ap.parse_args()
    p = LayoutParams(**json.loads(a.params)) if a.params else LayoutParams()
    duts = ["lsb", "msb", "pam4"] if a.dut == "all" else [a.dut]
    for d in duts:
        generate(d, p, a.out_dir)


if __name__ == "__main__":
    main()
