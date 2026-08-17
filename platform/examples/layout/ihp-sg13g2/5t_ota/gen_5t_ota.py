#!/usr/bin/env python3
"""Generate a rough IHP sg13g2 layout of the analog-db ``amp_001_5t`` 5T-OTA from
foundry PyCells, and write GDS.

Topology (ports vdd vout vinp vinn ibias vss), from
``examples/analog-db/circuits/amp_001_5t/pdk/ihp-sg13g2/netlist.spice``:

    M1 outm vinp tail vss nmos    M2 vout vinn tail vss nmos   (input pair)
    M3 outm outm vdd  vdd pmos    M4 vout outm vdd  vdd pmos   (mirror load)
    M5 tail ibias vss vss nmos    M6 ibias ibias vss vss nmos  (tail + bias ref)

Routing: horizontal per-net trunks on Metal2, vertical terminal stubs on Metal1, joined
only where same-net by a ``via_stack`` (Via1). Gate poly is lifted to Metal1 by a
``via_stack`` (GatPoly->Metal1) poly contact. Bulk ties use raw diffusion taps (Activ +
pSD + Cont + Metal1) — pure connectivity, so they don't extract as devices; extra p-taps
are interspersed so every nmos is within the LU.b 20 um latch-up distance.

Result: passes ``run_drc.py --no_density`` (0 violations) and ``run_lvs.py`` ("Netlists
match"). See README.md.
"""
from __future__ import annotations

import argparse
import os
from typing import Any

import pdk as P

pya = P.bootstrap()

# The klayout module is loaded dynamically by bootstrap(), so its classes are not
# statically importable — alias them for readable signatures.
PyaLayout = Any
PyaCell = Any

DBU: float = 0.001

# --- sizing (defaults = amp_001_5t/pdk/ihp-sg13g2/sizing.yaml) ---
SIZING: dict[str, str] = dict(in_w="0.5u", in_l="5u", pld_w="1.5u", pld_l="5u",
                              tail_w="2u", tail_l="5u", ref_w="2u", ref_l="5u")


def build(sizing: dict[str, str] = SIZING) -> tuple[PyaLayout, PyaCell]:
    ly = pya.Layout(); ly.dbu = DBU
    top = ly.create_cell("ota_5t")

    def layer(t: tuple[int, int]) -> int: return ly.layer(t[0], t[1])
    def um(v: float) -> int: return int(round(v / DBU))
    def box(lt: tuple[int, int], x0: float, y0: float, x1: float, y1: float) -> None:
        top.shapes(layer(lt)).insert(pya.Box(um(x0), um(y0), um(x1), um(y1)))
    def text(lt: tuple[int, int], s: str, x: float, y: float) -> None:
        top.shapes(layer(lt)).insert(pya.Text(s, pya.Trans(pya.Vector(um(x), um(y)))))

    def mos(kind: str, w: str, l: str) -> PyaCell:
        return ly.create_cell(kind, "SG13_dev",
                              {"w": w, "l": l, "ng": "1", "guardRingType": "none"})

    dev = {
        "M1": mos("nmos", sizing["in_w"], sizing["in_l"]),
        "M2": mos("nmos", sizing["in_w"], sizing["in_l"]),
        "M3": mos("pmos", sizing["pld_w"], sizing["pld_l"]),
        "M4": mos("pmos", sizing["pld_w"], sizing["pld_l"]),
        "M5": mos("nmos", sizing["tail_w"], sizing["tail_l"]),
        "M6": mos("nmos", sizing["ref_w"], sizing["ref_l"]),
    }

    # --- placement: nmos row, then a gap, then the pmos pair ---
    PITCH = 9.0
    place = {}
    x = 0.0
    for name in ("M6", "M5", "M1", "M2", "M3", "M4"):
        if name == "M3":
            x += 4.0                      # extra gap for nwell-to-nActiv separation
        top.insert(pya.CellInstArray(dev[name].cell_index(),
                                     pya.Trans(pya.Vector(um(x), 0))))
        place[name] = (dev[name], x)
        x += PITCH

    def terminals(cell: PyaCell, dx: float) -> dict:
        """gate contact point + S/D finger access points (top-cell um)."""
        poly = None
        for s in cell.shapes(layer(P.L_POLY)).each():
            poly = s.dbbox() if poly is None else poly + s.dbbox()
        cols = {}                          # cluster Metal1 boxes into x-columns (pmos stacks 2)
        for s in cell.shapes(layer(P.L_M1)).each():
            if s.is_box() or s.is_polygon():
                b = s.dbbox(); k = round(b.center().x, 1)
                cols[k] = (cols[k] + b) if k in cols else b
        sd = [(b.center().x + dx, b.bottom) for _, b in sorted(cols.items())]
        return {"gate": (poly.center().x + dx, poly.top), "sd": sd}

    term = {n: terminals(c, dx) for n, (c, dx) in place.items()}

    # --- shared nwell over the pmos pair + raw taps (n->vdd, p->vss) ---
    p3x, pbb = place["M3"][1], place["M3"][0].dbbox()
    p4x = place["M4"][1]
    box(P.L_NWELL, p3x + pbb.left - 0.8, pbb.bottom - 0.8, p4x + pbb.right + 2.2, pbb.top + 0.8)

    def draw_tap(cx: float, cy: float, ptype: str, size: float = 1.0) -> tuple[float, float]:
        h = size / 2.0
        box(P.L_ACTIV, cx - h, cy - h, cx + h, cy + h)
        if ptype == "p":
            box(P.L_PSD, cx - h - 0.1, cy - h - 0.1, cx + h + 0.1, cy + h + 0.1)
        box(P.L_M1, cx - h, cy - h, cx + h, cy + h)
        n = int((size - 0.14) / 0.34)
        x0 = cx - (n - 1) * 0.34 / 2.0; y0 = cy - (n - 1) * 0.34 / 2.0
        for i in range(n):
            for j in range(n):
                X, Y = x0 + i * 0.34, y0 + j * 0.34
                box(P.L_CONT, X - 0.08, Y - 0.08, X + 0.08, Y + 0.08)
        return (cx, cy)

    ntx = p4x + pbb.right + 1.0
    ntap_c = draw_tap(ntx, 0.75, "n")
    ptap_cs = [draw_tap(px, 0.5, "p") for px in (-2.5, 16.5, 35.5)]  # LU.b: within 20 um of nmos

    # --- net trunks on Metal2 (unique y each) ---
    xL, xR = -4.0, ntx + 1.5
    TRUNK = {"vss": -2.5, "tail": 8.0, "ibias": 9.2, "outm": 10.4,
             "vout": 11.6, "vdd": 13.0, "vinp": 7.0, "vinn": 7.0}
    PORTS = {"vdd", "vss", "vout", "vinp", "vinn", "ibias"}
    M2W = 0.3

    for net in ("vss", "tail", "ibias", "outm", "vout", "vdd"):
        y = TRUNK[net]
        box(P.L_M2, xL, y - M2W / 2, xR, y + M2W / 2)
        if net in PORTS:
            text(P.L_M2_TXT, net, (xL + xR) / 2, y)   # label ONLY real ports

    def vstack(x: float, y: float, b: str = "Metal1", t: str = "Metal2") -> None:
        vc = ly.create_cell("via_stack", "SG13_dev", {"b_layer": b, "t_layer": t})
        top.insert(pya.CellInstArray(vc.cell_index(), pya.Trans(pya.Vector(um(x), um(y)))))

    def m1_v(x: float, y0: float, y1: float, w: float = 0.2) -> None:
        box(P.L_M1, x - w / 2, min(y0, y1), x + w / 2, max(y0, y1))

    def connect_sd(name: str, fi: int, net: str) -> None:
        fx, fbot = term[name]["sd"][fi]
        m1_v(fx, fbot, TRUNK[net]); vstack(fx, TRUNK[net])

    def connect_gate(name: str, net: str) -> None:
        gx, gtop = term[name]["gate"]
        box(P.L_POLY, gx - 0.2, gtop - 0.1, gx + 0.2, gtop + 0.9)   # poly tab clear of channel
        ycon = gtop + 0.5
        vstack(gx, ycon, b="GatPoly", t="Metal1")
        m1_v(gx, ycon, TRUNK[net]); vstack(gx, TRUNK[net])

    # S/D permutable for LVS, so finger->net order is free.
    connect_sd("M1", 0, "outm"); connect_sd("M1", 1, "tail"); connect_gate("M1", "vinp")
    connect_sd("M2", 0, "vout"); connect_sd("M2", 1, "tail"); connect_gate("M2", "vinn")
    connect_sd("M3", 0, "outm"); connect_sd("M3", 1, "vdd");  connect_gate("M3", "outm")
    connect_sd("M4", 0, "vout"); connect_sd("M4", 1, "vdd");  connect_gate("M4", "outm")
    connect_sd("M5", 0, "tail"); connect_sd("M5", 1, "vss");  connect_gate("M5", "ibias")
    connect_sd("M6", 0, "ibias"); connect_sd("M6", 1, "vss"); connect_gate("M6", "ibias")

    for pc in ptap_cs:
        m1_v(pc[0], pc[1], TRUNK["vss"]); vstack(pc[0], TRUNK["vss"])
    m1_v(ntap_c[0], ntap_c[1], TRUNK["vdd"]); vstack(ntap_c[0], TRUNK["vdd"])

    for name, net in (("M1", "vinp"), ("M2", "vinn")):     # input pins
        text(P.L_M2_TXT, net, term[name]["gate"][0], TRUNK[net])

    return ly, top


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the amp_001_5t IHP layout")
    ap.add_argument("-o", "--out", default=os.path.join(os.path.dirname(__file__), "ota_5t.gds"))
    a = ap.parse_args()
    ly, top = build()
    ly.write(a.out)
    print(f"wrote {a.out} ({os.path.getsize(a.out)} bytes); bbox um: {top.dbbox().to_s()}")


if __name__ == "__main__":
    main()
