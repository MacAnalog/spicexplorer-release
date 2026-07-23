#!/usr/bin/env python3
"""Stamp out OTA wrapper-symbol variants from the HAND-DRAWN family bases.

This does NOT invent artwork. It reads a family's hand-drawn base .sym — the symbol
you edit in xschem (the fixed amplifier face) — and only *adds* the sanctioned extra
pins for each variant:
  - bias pins  vb1..vbN  evenly spaced along the bottom edge
  - chopper controls  vctl / vctl_not  on the lower-left (fully-diff family only)

Everything else (the Gm glyph, frame, core pins, labels) is your drawing, verbatim.

Pin ORDER is the contract
-------------------------
xschem's `@pinlist` expands pins in B-box **file order**, and the class benches bind
`${PORT_LINE}` POSITIONALLY against `circuit.yaml ports`. Both families therefore
match the LANDED analog-db corpus exactly (audited 2026-07-20):

    ota-fully-diff/    vinp vinn voutp voutn [extras] vdd vss
    ota-single-ended/  vdd vout vinp vinn   [extras] vss

    corpus evidence:  8x  ports: [vinp, vinn, voutp, voutn, vdd, vss]
                      3x  ports: [vdd, vout, vinp, vinn, ibias, vss]

Extras are spliced in immediately BEFORE the trailing supply pin(s) — `extras_before`
names that anchor per family — so `vb1` lands where `ibias` sits in the landed
single-ended entries rather than after `vss`.

⚠ Do NOT reorder a base's B-boxes without re-verifying every entry drawn from it.
  Swapping voutp/voutn inverts every feedback loop's sign; swapping vdd/vss swaps
  the rails. Both fail silently in the netlist.

Edit a base in xschem; then regen its variants:
    python gen_symbols.py                          # all families
    python gen_symbols.py --family ota-single-ended
"""
from __future__ import annotations

import argparse
import os

# base-frame constants (read off the hand-drawn art — only used to place NEW pins) --
X_R = 260          # right edge x  → bottom edge spans 0..X_R for spacing bias pins
Y_BOT = 0          # bottom edge y
STUB = 20          # pin stub length (matches the base)
HB = 2.5           # pin-box half-size; box CENTER is the wire snap point

MAX_BIAS = 4       # generate 0b..4b for every family

FAMILIES: dict[str, dict] = {
    "ota-fully-diff": {
        "base": "ota_fully_diff_base.sym",
        "prefix": "ota_fully_diff",
        "core": ["vinp", "vinn", "voutp", "voutn", "vdd", "vss"],
        "extras_before": "vdd",
        "chop": True,
    },
    "ota-single-ended": {
        "base": "ota_single_ended_base.sym",
        "prefix": "ota_single_ended",
        "core": ["vdd", "vout", "vinp", "vinn", "vss"],
        "extras_before": "vss",
        "chop": False,
    },
}


def _n(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else str(v)


def _snap(v: float, grid: int = 20) -> int:
    return int(round(v / grid)) * grid


def _pin_triple(x, y, name, edge, direction="in"):
    """Return (stub L, pin box B, label T) for one added pin.

    edge='bottom' → stub points down, label above the edge, inside.
    edge='left'   → stub points left,  label just inside the left edge.
    """
    if edge == "bottom":
        stub = f"L 4 {_n(x)} {_n(y)} {_n(x)} {_n(y + STUB)} {{}}"
        # pin box sits at the free end of the stub (below the body)
        box = (
            f"B 5 {_n(x - HB)} {_n(y + STUB - HB)} {_n(x + HB)} {_n(y + STUB + HB)} "
            f"{{name={name} dir={direction}}}"
        )
        label = f"T {{{name}}} {_n(x - 12)} {_n(y - 12)} 0 0 0.2 0.2 {{}}"
    else:  # left
        stub = f"L 4 {_n(-STUB)} {_n(y)} 0 {_n(y)} {{}}"
        box = (
            f"B 5 {_n(-STUB - HB)} {_n(y - HB)} {_n(-STUB + HB)} {_n(y + HB)} "
            f"{{name={name} dir={direction}}}"
        )
        label = f"T {{{name}}} 5 {_n(y - 4)} 0 0 0.2 0.2 {{}}"
    return stub, box, label


def _splice_boxes(lines: list[str], boxes: list[str], anchor: str | None) -> None:
    """Insert new pin B-boxes before `anchor`'s B-box (in place).

    Order of B-boxes IS the netlist port order, so this is the whole ballgame.
    L/T lines can go anywhere, but B lines must land in the right slot.
    """
    if not boxes:
        return
    idx = None
    if anchor:
        idx = next(
            (
                i
                for i, ln in enumerate(lines)
                if ln.startswith("B 5 ") and f"name={anchor} " in ln
            ),
            None,
        )
        if idx is None:
            raise SystemExit(f"anchor pin {anchor!r} has no B-box in the base symbol")
    if idx is None:  # no anchor → append after the last existing pin
        idx = max(i for i, ln in enumerate(lines) if ln.startswith("B 5 ")) + 1
    lines[idx:idx] = boxes


def variant(base_text: str, bias: int, chop: bool, anchor: str | None):
    stubs: list[str] = []
    boxes: list[str] = []
    labels: list[str] = []
    added: list[str] = []

    # bias pins evenly along the bottom edge: x_i = snap(X_R * i / (N+1))
    for i in range(1, bias + 1):
        x = _snap(X_R * i / (bias + 1))
        name = f"vb{i}"
        s, b, t = _pin_triple(x, Y_BOT, name, "bottom")
        stubs.append(s), boxes.append(b), labels.append(t), added.append(name)

    # chopper controls on the lower-left, below the two inputs (-130, -110)
    if chop:
        for y, name in ((-90, "vctl"), (-70, "vctl_not")):
            s, b, t = _pin_triple(0, y, name, "left")
            stubs.append(s), boxes.append(b), labels.append(t), added.append(name)

    lines = base_text.rstrip("\n").split("\n")
    _splice_boxes(lines, boxes, anchor)
    lines += stubs + labels
    return "\n".join(lines) + "\n", added


def pin_order(core: list[str], added: list[str], anchor: str | None) -> list[str]:
    """The resulting netlist port order — mirrors what _splice_boxes did."""
    if added and anchor and anchor in core:
        cut = core.index(anchor)
        return core[:cut] + added + core[cut:]
    return core + added


def generate(family: str, spec: dict, here: str) -> None:
    """Stamp every variant of one family into its own subdirectory."""
    fam_dir = os.path.join(here, family)
    with open(os.path.join(fam_dir, spec["base"])) as fh:
        base_text = fh.read()

    anchor = spec["extras_before"]
    print(f"[{family}]  base: {spec['base']} (hand-drawn — edit this in xschem)")
    for b in range(0, MAX_BIAS + 1):
        for chop in (False, True) if spec["chop"] else (False,):
            fname = f"{spec['prefix']}_{b}b{'_chop' if chop else ''}.sym"
            content, added = variant(base_text, b, chop, anchor)
            with open(os.path.join(fam_dir, fname), "w") as fh:
                fh.write(content)
            order = " ".join(pin_order(spec["core"], added, anchor))
            print(f"  {fname:34s} pins: {order}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--family",
        choices=sorted(FAMILIES),
        action="append",
        help="regen only this family (repeatable); default = all",
    )
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    for family in args.family or sorted(FAMILIES):
        generate(family, FAMILIES[family], here)


if __name__ == "__main__":
    main()
