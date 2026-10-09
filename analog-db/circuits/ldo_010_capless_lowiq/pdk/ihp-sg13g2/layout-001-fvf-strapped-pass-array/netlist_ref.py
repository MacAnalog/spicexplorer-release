"""The certified netlist, parsed once — the single source of device identity for the layout.

`review-002` **M7**: the layout generator used to write the LVS reference from its own hand-typed
`MOS` table, so "LVS-identical to the certified netlist" was never what the flow proved — a
divergence between the generator's table and
`circuits/ldo_ihp_capless/pdk/ihp-sg13g2/netlist.spice` would still pass. This module removes the
second table. It parses the **certified binding** and hands out:

* :func:`devices` — what the generator places (name, kind, nets, W/L in um, multiplicity);
* :func:`lvs_reference` — the flat M/R/C netlist the KLayout LVS deck compares against.

Both come from the same parse, so the drawing and the compare cannot disagree about a device.

Since the **F19 re-certification** (2026-09-05) the certified netlist carries the *drawn* device
set — `XMP` as one shared-diffusion device with `ng` fingers, every common-centroid member as two
half-width cards, the resistors as segment chains — so this module and
`circuits/…/netlist.spice` describe the same devices in the same numbers, and the benches simulate
what the layout draws.  Card parameters may therefore be `{expressions}` over sizing knobs
(`w={x_dut_xm1_w/2}`), which :func:`value` evaluates.

**The one thing the reference adds** to the certified netlist is the layout's **dummy devices**.
They are not optional and they are not schematic: a matched row needs tied-off dummies at both
ends (`review-002` m3), and the IHP LVS deck extracts a fully shorted dummy MOS as a real device
which ``--purge``/``--purge_nets`` does **not** remove (measured, see REPORT). So every dummy is
declared here — and :func:`lvs_reference` **asserts that each one has all four terminals on a
single rail**, which is what keeps M7 shut: a dummy card can only ever be electrically inert, and
a real device's size still comes from the certified file.

Sources (`VREF`, the loop-break marker `VLP`) are not devices: their nodes `vref` and `lp_brk`
become pins of the drawn cell.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: The DRAWN CELL name — the GDS top cell and the LVS/PEX cell, unchanged from the source repo.
#: It is deliberately NOT the analog-db accession id: renaming a signed-off physical cell would
#: invalidate every artefact that names it (REVIEW.yaml, SIGNOFF.md, the extracted netlists).
#: The bench-side rename to ldo_010_capless_lowiq happens once, in pex_sim.py.
CELL = "ldo_ihp_capless"
#: The certified binding, one directory up: this layout entry lives INSIDE the circuit entry it
#: draws (circuits/<id>/pdk/<pdk>/layout-<NNN>-<slug>/), so the netlist and the sizing record
#: it must not disagree with are its own parent's — not a path into another repo.
NETLIST = Path(__file__).resolve().parent.parent / "netlist.spice"
SIZING_YAML = Path(__file__).resolve().parent.parent / "sizing.yaml"

# model -> (n nodes in the certified card, LVS card letter, n nodes the LVS deck wants)
_MODELS = {
    "sg13_lv_nmos": (4, "M", 4),
    "sg13_lv_pmos": (4, "M", 4),
    # rhigh is drawn 3-terminal in SPICE (the third node is the poly body `bn`); the standalone
    # IHP LVS deck extracts it as a 2-terminal device, so the reference drops the body node.
    "rhigh": (3, "R", 2),
    "cap_cmim": (2, "C", 2),
}

_SI = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6}


def _num(v: object) -> float:
    """One sizing value as a plain float: a string carries an SI suffix and means metres
    (``"340u"`` -> 3.4e-4); a bare number is already in the file's own unit (metres for a length,
    a count for `m`/`ng`)."""
    if isinstance(v, str):
        m = re.match(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(meg|[afpnumk])?\s*$", v, re.I)
        if not m:
            raise ValueError(f"bad sizing value {v!r}")
        return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0)
    return float(v)


def value(expr: str, sizing: dict[str, object]) -> float:
    """A card parameter: either a bare sizing-knob name or a ``{...}`` arithmetic expression over
    knob names.  The namespace is every knob through :func:`_num`, so an expression mixes freely
    with the file's units — ``{r_fb_l/8}`` is metres, ``{x_dut_xmp_m*x_dut_xmp_nf_mult}`` a count.
    Only arithmetic on knob names is allowed; there are no calls and no builtins."""
    e = expr.strip()
    if not (e.startswith("{") and e.endswith("}")):
        return _num(sizing[e])
    body = e[1:-1]
    if not re.fullmatch(r"[A-Za-z0-9_+\-*/(). ]+", body):
        raise ValueError(f"unsupported parameter expression {expr!r}")
    ns = {k: _num(v) for k, v in sizing.items()}
    return float(eval(body, {"__builtins__": {}}, ns))  # noqa: S307 - vetted charset, no builtins


def um(v: object) -> float:
    """A sizing value in micrometres. Strings carry an SI suffix (``"8u"``); floats are metres
    (the optimizer's `design.json` convention)."""
    if isinstance(v, str):
        m = re.match(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(meg|[afpnumk])?", v, re.I)
        if not m:
            raise ValueError(f"bad sizing value {v!r}")
        return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0) * 1e6
    return float(v) * 1e6


def count(v: object) -> int:
    return int(round(float(v)))


@dataclass(frozen=True)
class Card:
    """One device of the certified netlist, with its parameters still symbolic."""

    name: str          # "XM1"
    model: str         # "sg13_lv_pmos"
    nodes: tuple[str, ...]
    params: dict[str, str]   # {"w": "x_dut_xm1_w", "l": "x_dut_xm1_l", "m": ...}

    @property
    def kind(self) -> str:
        return {"sg13_lv_nmos": "n", "sg13_lv_pmos": "p", "rhigh": "r", "cap_cmim": "c"}[self.model]


def load_sizing(path: Path | None = None) -> dict[str, object]:
    """`sizing.yaml` defaults — the design of record."""
    import yaml

    doc = yaml.safe_load((path or SIZING_YAML).read_text())
    return {v["name"]: v["default"] for v in doc["variables"]}


def parse(path: Path | None = None) -> list[Card]:
    """Every device card of the certified netlist, in file order."""
    out: list[Card] = []
    for raw in (path or NETLIST).read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith(("*", ".")) or not s[0].upper() == "X":
            continue
        tok = s.split()
        name, rest = tok[0], tok[1:]
        params = {}
        while rest and "=" in rest[-1]:
            k, v = rest.pop().split("=", 1)
            params[k.lower()] = v
        if not rest:
            raise ValueError(f"no model on card {s!r}")
        model = rest[-1]
        nodes = tuple(rest[:-1])
        if model not in _MODELS:
            raise ValueError(f"unknown model {model!r} on card {s!r} — teach netlist_ref about it")
        n_nodes, _, _ = _MODELS[model]
        if len(nodes) != n_nodes:
            raise ValueError(f"{name}: {len(nodes)} nodes, expected {n_nodes} for {model}")
        out.append(Card(name, model, nodes, params))
    return out


@dataclass(frozen=True)
class MosDev:
    """A transistor as the generator needs it: micrometres, and `m` already separated."""

    name: str
    kind: str          # "n" | "p"
    drain: str
    gate: str
    source: str
    bulk: str
    w: float           # the card's width, um (with `ng` fingers this is the TOTAL width)
    l: float           # um
    m: int             # parallel units (the layout folds them into fingers)
    # The PDK subckt's own finger parameter.  The certified netlist does NOT use it -- see
    # netlist.spice's header -- but a card that did would break `w_total`, so it is parsed and
    # asserted rather than silently ignored.
    ng: int = 1

    @property
    def w_total(self) -> float:
        return self.w * self.m


def devices(sizing: dict[str, object], path: Path | None = None) -> tuple[list[MosDev], list[Card]]:
    """(transistors, passive cards) at this sizing point."""
    mos, passives = [], []
    for c in parse(path):
        if c.kind in ("n", "p"):
            d, g, s, b = c.nodes
            mos.append(MosDev(c.name, c.kind, d, g, s, b,
                              value(c.params["w"], sizing) * 1e6,
                              value(c.params["l"], sizing) * 1e6,
                              count(value(c.params["m"], sizing)) if "m" in c.params else 1,
                              count(value(c.params["ng"], sizing)) if "ng" in c.params else 1))
        else:
            passives.append(c)
    return mos, passives


@dataclass(frozen=True)
class Dummy:
    """A layout-only, electrically inert device: every terminal on ``rail``."""

    name: str
    kind: str      # "n" | "p" | "r"
    rail: str      # "vss" | "vdd"
    w: float       # um
    l: float       # um


# The cell's pins. `vref` and `lp_brk` are the nodes of the two sources the subckt carries but the
# layout does not draw, so they are drawn as pins; `fb` is a test/trim pin on the left edge.
PINS = ["vdd", "vout", "vss", "vref", "lp_brk", "fb"]


def lvs_reference(sizing: dict[str, object], dummies: list[Dummy] | None = None,
                  path: Path | None = None) -> str:
    """The flat netlist the KLayout LVS deck compares the layout against.

    Derived from the certified binding, never from the generator's own device list (M7). The only
    transformations, all mechanical:

    * ``X<name> ... <model> w=<key> l=<key>`` -> a primitive ``M``/``R``/``C`` card with the
      sizing values substituted (the deck reads primitives, not subcircuit calls);
    * a transistor's ``m`` is folded into ``w``: ``m`` parallel units of the same net set are one
      device of the summed width to the deck (``--combine_devices``).  ``ng`` needs no
      transformation — a shared-diffusion device's ``w`` is already its total width — and the
      difference between the two, which is junction area and perimeter, is invisible to a deck
      that compares W and L.  That is exactly why it is in the **certified netlist** now (F19)
      rather than left for LVS to notice, which it cannot;
    * ``rhigh``'s third (poly body) node is dropped: the standalone IHP LVS deck extracts the poly
      resistor as a 2-terminal device;
    * the layout's dummy devices are appended, each asserted electrically inert.
    """
    mos, passives = devices(sizing, path)
    lines = [f"* {CELL} — LVS reference, derived from {NETLIST.name} (netlist_ref.py)",
             f".subckt {CELL} {' '.join(PINS)}"]
    for d in mos:
        assert d.ng == 1, f"{d.name}: ng={d.ng}; w_total = w*m assumes one finger per card"
        lines.append(f"M{d.name[1:]} {d.drain} {d.gate} {d.source} {d.bulk} "
                     f"sg13_lv_{d.kind}mos w={d.w_total:g}u l={d.l:g}u")
    for c in passives:
        w, l = value(c.params["w"], sizing) * 1e6, value(c.params["l"], sizing) * 1e6
        m = f" m={count(value(c.params['m'], sizing))}" if "m" in c.params else ""
        if c.kind == "r":
            lines.append(f"R{c.name[1:]} {c.nodes[0]} {c.nodes[1]} rhigh w={w:g}u l={l:g}u{m}")
        else:
            lines.append(f"C{c.name[1:]} {c.nodes[0]} {c.nodes[1]} cap_cmim w={w:g}u l={l:g}u{m}")
    for dm in dummies or []:
        # The guarantee that keeps M7 shut: a dummy card is inert by construction.
        assert dm.rail in ("vss", "vdd"), f"dummy {dm.name}: rail {dm.rail!r} is not a cell rail"
        if dm.kind in ("n", "p"):
            lines.append(f"M{dm.name} {dm.rail} {dm.rail} {dm.rail} {dm.rail} "
                         f"sg13_lv_{dm.kind}mos w={dm.w:g}u l={dm.l:g}u")
        elif dm.kind == "r":
            lines.append(f"R{dm.name} {dm.rail} {dm.rail} rhigh w={dm.w:g}u l={dm.l:g}u")
        else:
            raise ValueError(f"dummy {dm.name}: unknown kind {dm.kind!r}")
    lines.append(f".ends {CELL}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover - a look at what the parse produced
    sz = load_sizing()
    m, p = devices(sz)
    for d in m:
        print(f"{d.name:6s} {d.kind} {d.drain:8s} {d.gate:8s} {d.source:8s} "
              f"w={d.w:g} l={d.l:g} m={d.m}")
    for c in p:
        print(c)
    print(lvs_reference(sz))
