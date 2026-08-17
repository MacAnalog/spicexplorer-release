#!/usr/bin/env python3
"""Generate the amp_001_5t 5T-OTA layout with **gdsfactory + the ihp-gdsfactory PDK**.

This is the gdsfactory lane — kept separate from the pure-KLayout/PyCell lane in
``../5t_ota/``. Same circuit, same LVS reference topology, different generator:

    M1 outm vinp tail vss nmos    M2 vout vinn tail vss nmos   (input pair)
    M3 outm outm vdd  vdd pmos    M4 vout outm vdd  vdd pmos   (mirror load)
    M5 tail ibias vss vss nmos    M6 ibias ibias vss vss nmos  (tail + bias ref)

What is *better* about this flow (vs the PyCell lane):

- **Devices expose real ports.** ``ihp.cells.nmos/pmos`` return gdsfactory
  components with named ``S``/``D``/``G`` ports — no reverse-engineering terminal
  positions by clustering Metal1 boxes.
- **Placement is computed, not hardcoded.** Devices are placed as three
  function rows (bias / input pair / mirror load), each row a mirrored pair
  about the x=0 symmetry axis; row y-positions come from live bounding boxes
  plus named clearance constants. Change any W/L and the floorplan re-derives.
- **Matching-aware**: M1|M2 and M3|M4 are true geometric mirror pairs (one
  instance mirrored), and the tail/bias pair shares a row — the standard
  analog stack-up.
- **Routing is port-driven.** Straps and rails are drawn between port
  coordinates; the two non-trivial nets (tail, vout) go through
  ``gf.routing.route_single`` on the PDK's metal cross-sections.
- **Taps/wells are derived**: p-taps ride the vss rails next to every nmos row
  (LU.b latch-up by construction), the n-well cover + n-taps are computed from
  the pmos row bbox.

Result: passes KLayout DRC (``--no_density``) and LVS ("Netlists match") with
the same signoff decks as the PyCell lane. See README.md.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os

import gdsfactory as gf
from ihp import PDK
from ihp import cells as C

PDK.activate()

# --- sizing (defaults = amp_001_5t/pdk/ihp-sg13g2/sizing.yaml) ---
SIZING: dict[str, float] = dict(in_w=0.5, in_l=5.0, pld_w=1.5, pld_l=5.0,
                                tail_w=2.0, tail_l=5.0, ref_w=2.0, ref_l=5.0)


@dataclasses.dataclass(frozen=True)
class LayoutParams:
    """The free layout constants (um) — the search space for layout optimization.

    Defaults = the optimize_layout.py winner (2026-07-09, budget 2x30, DRC/LVS
    hard-gated, kpex-CC + ngspice in the loop): 205.9 um2 / -0.699 MHz UGF vs
    the hand-tuned 232.1 um2 / -0.726 MHz. Hand-tuned values in comments.
    """

    gap_x: float = 1.46    # center channel between the two devices of a row (was 1.4)
    ch_y: float = 0.92     # routing channel between rows (was 1.8)
    edge_x: float = 1.57   # outermost device edge -> vss rail center (was 1.6)
    w_m1: float = 0.25     # Metal1 wire width (was 0.3)
    w_m2: float = 0.29     # Metal2 wire width (was 0.3)
    tab_w: float = 0.39    # gate poly tab width (was 0.4)
    ib_off: float = 1.1    # ibias strap drop below row N0 (was 1.0)
    vdd_off: float = 1.35  # vdd bar clearance above row P (was 1.2)
    vss_off: float = 1.44  # vss bar drop below the ibias strap (was 1.4)


def _pair(comp_l: gf.Component, comp_r: gf.Component, mirror_l: bool, mirror_r: bool,
          y: float, parent: gf.Component,
          gap_x: float) -> tuple[gf.ComponentReference, gf.ComponentReference]:
    """Place a mirrored device pair about x=0 with the inner edges at +-gap_x/2."""
    il, ir = parent << comp_l, parent << comp_r
    if mirror_l:
        il.dmirror_x()
    if mirror_r:
        ir.dmirror_x()
    il.dxmax = -gap_x / 2
    ir.dxmin = +gap_x / 2
    il.dymin = y
    ir.dymin = y
    return il, ir


CELL = "ota_5t_gf"
# legal range per knob (um) — the spicexplorer_layout generator contract; also the
# optimize_layout.py search space
BOUNDS: dict[str, tuple[float, float]] = {
    "gap_x": (0.8, 1.8), "ch_y": (0.9, 2.2), "edge_x": (0.8, 2.0),
    "w_m1": (0.2, 0.5), "w_m2": (0.2, 0.5), "tab_w": (0.3, 0.5),
    "ib_off": (0.55, 1.4), "vdd_off": (0.5, 1.6), "vss_off": (0.6, 1.8),
}


def build(p: LayoutParams = LayoutParams(),
          sizing: dict[str, float] | None = None) -> gf.Component:
    """Generator contract (spicexplorer_layout.gen): build(params, sizing=None) -> Component."""
    sizing = sizing or SIZING
    c = gf.Component(CELL)

    nm_in = C.nmos(width=sizing["in_w"], length=sizing["in_l"])
    nm_tail = C.nmos(width=sizing["tail_w"], length=sizing["tail_l"])
    nm_ref = C.nmos(width=sizing["ref_w"], length=sizing["ref_l"])
    pm_ld = C.pmos(width=sizing["pld_w"], length=sizing["pld_l"])

    # --- placement: three rows, bottom-up, y derived from live bboxes ---
    y0 = 0.0                                             # row N0: M6 | M5
    m6, m5 = _pair(nm_ref, nm_tail, False, True, y0, c, p.gap_x)  # D inner on both
    y1 = max(m6.dymax, m5.dymax) + p.ch_y                # row N1: M1 | M2
    m1, m2 = _pair(nm_in, nm_in, True, False, y1, c, p.gap_x)     # S inner (tail strap)
    y2 = max(m1.dymax, m2.dymax) + p.ch_y                # row P:  M3 | M4
    m3, m4 = _pair(pm_ld, pm_ld, False, True, y2, c, p.gap_x)     # D inner on both

    # --- drawing helpers (all coordinates come from ports) ---
    def rect(layer: str, x0: float, y0_: float, x1: float, y1_: float) -> None:
        c.add_polygon([(x0, y0_), (x1, y0_), (x1, y1_), (x0, y1_)], layer=layer)

    def hwire(y: float, x0: float, x1: float, layer: str = "Metal1drawing",
              w: float = p.w_m1) -> None:
        rect(layer, min(x0, x1), y - w / 2, max(x0, x1), y + w / 2)

    def vwire(x: float, y0_: float, y1_: float, layer: str = "Metal1drawing",
              w: float = p.w_m1) -> None:
        rect(layer, x - w / 2, min(y0_, y1_), x + w / 2, max(y0_, y1_))

    def via12(x: float, y: float) -> None:
        # Drawn explicitly: ihp-gdsfactory's VIA_RULES pins Via1 at 0.26 um, but
        # sg13g2 V1.a requires exactly 0.19x0.19 (and undersized via_stack sizes
        # silently drop the via). Pads 0.4x0.4 give >=0.05 enclosure (V1.c/d).
        rect("Metal1drawing", x - 0.2, y - 0.2, x + 0.2, y + 0.2)
        rect("Metal2drawing", x - 0.2, y - 0.2, x + 0.2, y + 0.2)
        rect("Via1drawing", x - 0.095, y - 0.095, x + 0.095, y + 0.095)

    def gate_via(inst: gf.ComponentReference, y_strap: float) -> float:
        """Poly tab from the gate down to y_strap + GatPoly->Metal1 contact there."""
        g = inst.ports["G"]
        gx, gy = g.center
        rect("GatPolydrawing", gx - p.tab_w / 2, y_strap - p.tab_w / 2, gx + p.tab_w / 2, gy)
        v = c << C.via_stack(bottom_layer="GatPoly", top_layer="Metal1", size=(0.4, 0.4))
        v.dcenter = (gx, y_strap)
        return gx

    def label(net: str, x: float, y: float, layer: str = "Metal1text") -> None:
        c.add_label(text=net, position=(x, y), layer=layer)

    P = lambda inst, name: inst.ports[name].center  # noqa: E731

    # --- routing channels / rails (derived) ---
    y_ib = y0 - p.ib_off                             # ibias strap (below row N0)
    y_in = (max(m6.dymax, m5.dymax) + y1) / 2.0      # vinp/vinn contacts (N0-N1 channel)
    y_om = (max(m1.dymax, m2.dymax) + y2) / 2.0      # outm strap (N1-P channel)
    y_vdd = max(m3.dymax, m4.dymax) + p.vdd_off      # vdd bar (above row P)
    y_vss = y_ib - p.vss_off                         # vss bar (below ibias strap)
    x_rail = max(m3.dxmax, m5.dxmax, m2.dxmax) + p.edge_x

    # --- vdd: pmos sources (outer) + n-taps, bar on Metal1 above row P ---
    for inst in (m3, m4):
        sx, sy = P(inst, "S")
        vwire(sx, sy, y_vdd)
    hwire(y_vdd, -x_rail, x_rail, w=0.5)
    label("vdd", 0, y_vdd)

    # --- nwell cover: union of the pmos wells + the n-taps, one rectangle ---
    ntap = C.ntap1(width=0.78, length=1.0, rows=2, cols=1)
    nt_l, nt_r = c << ntap, c << ntap
    nt_l.dcenter = (-x_rail + 0.2, (m3.dymin + m3.dymax) / 2)
    nt_r.dcenter = (x_rail - 0.2, (m4.dymin + m4.dymax) / 2)
    for nt in (nt_l, nt_r):
        tx, ty = P(nt, "TAP")
        vwire(tx, ty, y_vdd)
    rect("NWelldrawing", nt_l.dxmin - 0.31, min(m3.dymin, nt_l.dymin) - 0.31,
         nt_r.dxmax + 0.31, max(m3.dymax, nt_l.dymax) + 0.31)

    # --- vss: U-ring on Metal1 (two rails + bottom bar), nmos sources + p-taps ---
    for x in (-x_rail, x_rail):
        vwire(x, y_vss, y1 + 1.0, w=0.5)
    hwire(y_vss, -x_rail, x_rail, w=0.5)
    label("vss", 0, y_vss)
    for inst in (m6, m5):                            # nmos sources (outer ends)
        sx, sy = P(inst, "S")
        hwire(sy, sx, -x_rail if sx < 0 else x_rail)
    ptap = C.ptap1(width=0.78, length=1.0, rows=2, cols=1)
    for yr in (y0 + 0.5, y1 + 0.2):                  # a p-tap on each rail per nmos row
        for xr in (-x_rail, x_rail):
            pt = c << ptap
            pt.dcenter = (xr, yr)                    # tap Metal1 lands on the rail

    # --- ibias: M6 diode (D+G) + M5 gate, strap below row N0 ---
    gx6 = gate_via(m6, y_ib)
    gx5 = gate_via(m5, y_ib)
    hwire(y_ib, gx6, gx5)
    dx6, dy6 = P(m6, "D")
    vwire(dx6, y_ib, dy6)                            # M6 drain drop (inner column)
    label("ibias", (gx6 + gx5) / 2, y_ib)

    # --- tail: M1.S -- M2.S strap, then route down to M5.D (gf routing) ---
    s1, s2 = P(m1, "S"), P(m2, "S")
    hwire(s1[1], s1[0], s2[0])
    c.add_port(name="tail0", center=(0, s1[1]), width=p.w_m1, orientation=270,
               layer="Metal1drawing", port_type="electrical")
    d5 = c.add_port(name="m5d", center=P(m5, "D"), width=p.w_m1, orientation=180,
                    layer="Metal1drawing", port_type="electrical")
    gf.routing.route_single(c, c.ports["tail0"], d5, cross_section="metal1_routing",
                            auto_taper=False, port_type="electrical")

    # --- vinp/vinn: gate contacts in the N0-N1 channel, label-only ports ---
    for inst, net in ((m1, "vinp"), (m2, "vinn")):
        gx = gate_via(inst, y_in)
        label(net, gx, y_in)

    # --- outm: pmos gate straps + M3 drain + M1 drain, all Metal1 ---
    gate_via(m3, y_om)                               # inside the d1x..gx4 strap span
    gx4 = gate_via(m4, y_om)
    d3x, d3y = P(m3, "D")
    d1x, d1y = P(m1, "D")
    vwire(d3x, y_om, d3y)                            # M3 drain drop
    vwire(d1x, d1y, y_om)                            # M1 drain rise (outer left)
    hwire(y_om, d1x, gx4)                            # strap spans gate vias + both drains

    # --- vout: M4.D -> M2.D on Metal2 (crosses the outm strap legally) ---
    d4x, d4y = P(m4, "D")
    d2x, d2y = P(m2, "D")
    via12(d4x, d4y)
    via12(d2x, d2y)
    p4 = c.add_port(name="m4d", center=(d4x, d4y), width=p.w_m2, orientation=270,
                    layer="Metal2drawing", port_type="electrical")
    p2 = c.add_port(name="m2d", center=(d2x, d2y), width=p.w_m2, orientation=90,
                    layer="Metal2drawing", port_type="electrical")
    gf.routing.route_single(c, p4, p2, cross_section="metal2_routing",
                            auto_taper=False, port_type="electrical")
    label("vout", d2x, d2y, layer="Metal2text")

    return c


def write_lvs_reference(p: LayoutParams = LayoutParams(), sizing: dict[str, float] | None = None,
                        out: str | os.PathLike | None = None) -> str:
    """The flat `M`-card netlist the KLayout LVS deck compares against, for THIS sizing
    (`ota_5t_gf_lvs.spice` is the committed copy for the default SIZING). The layout knobs
    `p` do not change the devices, but the backend's `lvs: {writer: write_lvs_reference}`
    calls it per candidate so a co-optimization (sizing in the search space) stays LVS-honest.
    Sizes are in um (SIZING units); returns the netlist text (and writes it to `out`)."""
    sz = {**SIZING, **(sizing or {})}
    lines = [
        f"* amp_001_5t — LVS reference for topcell {CELL} (generated by write_lvs_reference)",
        f".subckt {CELL} vdd vout vinp vinn ibias vss",
        f"M1 outm vinp tail vss sg13_lv_nmos w={sz['in_w']:g}u l={sz['in_l']:g}u",
        f"M2 vout vinn tail vss sg13_lv_nmos w={sz['in_w']:g}u l={sz['in_l']:g}u",
        f"M3 outm outm vdd  vdd sg13_lv_pmos w={sz['pld_w']:g}u l={sz['pld_l']:g}u",
        f"M4 vout outm vdd  vdd sg13_lv_pmos w={sz['pld_w']:g}u l={sz['pld_l']:g}u",
        f"M5 tail ibias vss vss sg13_lv_nmos w={sz['tail_w']:g}u l={sz['tail_l']:g}u",
        f"M6 ibias ibias vss vss sg13_lv_nmos w={sz['ref_w']:g}u l={sz['ref_l']:g}u",
        ".ends",
    ]
    text = "\n".join(lines) + "\n"
    if out is not None:
        with open(out, "w") as f:
            f.write(text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate amp_001_5t (gdsfactory lane)")
    ap.add_argument("-o", "--out",
                    default=os.path.join(os.path.dirname(__file__), "ota_5t_gf.gds"))
    ap.add_argument("--params", default=None,
                    help='JSON overrides for LayoutParams, e.g. {"gap_x": 1.1}')
    a = ap.parse_args()
    p = LayoutParams(**json.loads(a.params)) if a.params else LayoutParams()
    comp = build(p=p)
    comp.write_gds(a.out)
    b = comp.bbox()
    area = (b.right - b.left) * (b.top - b.bottom)
    print(f"wrote {a.out} ({os.path.getsize(a.out)} bytes); bbox um: {b}; "
          f"area um2: {area:.1f}")


if __name__ == "__main__":
    main()
