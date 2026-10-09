"""PEX via **kpex** (klayout-pex, 2.5D engine) → :class:`PexResult` with per-net C sums.

kpex runs the KLayout LVS deck internally for connectivity, then extracts coupling /
ground C (``CC``), + wire R (``RC``), or R only. It writes
``<out_dir>/<gds-stem>__<cell>/<cell>_k25d_pex_netlist.spice``. Gotchas pinned by the
prototype: kpex needs a KLayout executable with Ruby ≥ 2.6 (``KPEX_KLAYOUT_EXE``) and an
**absolute** ``--out_dir``.

``RC``/``R`` mode needs one repair kpex does not do: the resistor mesh it writes is an
electrical ISLAND — no card joins any mesh node to a device pin, so ngspice reports a
singular matrix on the floating nodes and an RC run with ``.option rshunt=…`` returns the
``CC`` numbers unchanged. :func:`run_pex` stitches it from kpex's own report database and
refuses to return ``ok=True`` for a mesh that is still open (:func:`check_mesh_connectivity`);
the reasoning is in the block above :func:`stitch_rc_netlist`.

**kpex does not support IHP MIM caps (``cap_cmim``)**: its tech (``klayout_pex_protobuf/
ihp-sg13g2_tech.pb.json``) defines the MIM top layer ``cmim_top`` (GDS 36) with
``original_layer_name: "<TODO>"`` and the 2.5D sidewall/fringe extractor dies with
``KeyError: '<TODO>' in EdgeNeighborhoodVisitor.on_edge`` on any cell containing one.
Workaround (validated on the LPF H12 cell): extract a copy of the GDS with layers 36/0 (MIM)
and 129/0 (Vmim) cleared and TopMetal1 (126/0) minus the MIM regions (top plates removed,
stubs kept), against a schematic with the ``C`` cards removed; then add the schematic MIM
cards back into the extracted subckt for the benches — bottom-plate (Metal5) parasitics are
extracted, top-plate-to-neighbour C is lost. See :func:`strip_mim_for_pex`.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, NamedTuple

from .pdk import kpex_exe, kpex_klayout_exe, pdk_root
from .results import PexResult, proc_output, snapshot, tail, written_since

_ELEM = re.compile(r"^([CR])\S*\s+(\S+)\s+(\S+)\s+(\S+)", re.I)
_SI = {
    "a": 1e-18,
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "meg": 1e6,
    "g": 1e9,
    "t": 1e12,
}


def _num(tok: str) -> float | None:
    """SPICE number with optional SI suffix (kpex writes ``62.1879a`` = 62.19 aF)."""
    m = re.match(r"^([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(meg|[afpnumkgt])?", tok, re.I)
    if not m:
        return None
    return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0)


def _net(tok: str) -> str:
    return tok.replace("\\", "")  # kpex escapes internal nets as \$17


def _read_netlist(x: str | Path) -> str:
    """Accept a path or the netlist text itself (text = has a newline, or is not a file)."""
    if isinstance(x, Path):
        return x.read_text(errors="replace")
    if "\n" in x:
        return x
    try:
        q = Path(x)
        return q.read_text(errors="replace") if q.is_file() else x
    except OSError:
        return x


#: Node names that are ground rather than a signal net, compared lower-cased. ``vsubs`` is the
#: substrate node kpex connects every extracted ground C to (it is not a subckt pin). The layout
#: optimizer backend keeps an identical copy (it imports this package lazily); a test asserts the
#: two are equal.
GROUND_NETS = frozenset({"0", "gnd", "vss", "vsubs"})


class ParasiticSummary(NamedTuple):
    """The four values :func:`summarize_parasitics` returns, the self-loop count, the ground set."""

    n_c: int  # C cards counted (self-loops excluded)
    n_r: int  # R cards
    per_net_c_ff: dict[str, float]  # per signal net, the sum of every C card touching it [fF]
    coupling_ff: dict[str, float]  # "a|b" -> C between two signal nets [fF]
    n_self: int  # C cards with both terminals on one net, skipped
    ground_nets: list[str]  # every node name treated as ground, lower-cased and sorted


def scan_parasitics(netlist: str | Path, *, ground_nets: Iterable[str] = ()) -> ParasiticSummary:
    """C and R card counts and per-net C sums of a PEX netlist, with what was left out.

    A net in :data:`GROUND_NETS` or ``ground_nets`` (any case; e.g. ``sub`` when the substrate
    carries a pin name) is ground: it gets no per-net sum and is in no coupling pair, so a net's
    C to ground counts in its own sum only. A self-loop C card (both terminals on one net, which
    kpex does emit) has 0 V across it and stores no charge; it is skipped, left out of ``n_c``,
    and counted in ``n_self``.
    """
    gnd = GROUND_NETS | {n.lower() for n in ground_nets}
    n_c = n_r = n_self = 0
    per: dict[str, float] = {}
    coup: dict[str, float] = {}
    for line in Path(netlist).read_text(errors="replace").splitlines():
        m = _ELEM.match(line.strip())
        if not m:
            continue
        kind, a, b, val = m.group(1).upper(), _net(m.group(2)), _net(m.group(3)), _num(m.group(4))
        if kind == "R":
            n_r += 1
            continue
        if val is None:
            continue
        if a == b:
            n_self += 1
            continue
        n_c += 1
        ff = val * 1e15
        signal = [n for n in (a, b) if n.lower() not in gnd]
        for n in signal:
            per[n] = per.get(n, 0.0) + ff
        if len(signal) == 2:
            key = "|".join(sorted((a, b)))
            coup[key] = coup.get(key, 0.0) + ff
    return ParasiticSummary(n_c, n_r, per, coup, n_self, sorted(gnd))


def summarize_parasitics(
    netlist: str | Path,
    *,
    ground_nets: Iterable[str] = (),
) -> tuple[int, int, dict[str, float], dict[str, float]]:
    """(n_C, n_R, per-net ΣC [fF], coupling C between net pairs [fF]) from a PEX netlist.

    The ground and self-loop rules are those of :func:`scan_parasitics`, which also returns the
    self-loop count and the ground set applied.
    """
    s = scan_parasitics(netlist, ground_nets=ground_nets)
    return s.n_c, s.n_r, s.per_net_c_ff, s.coupling_ff


# --------------------------------------------------------------------------------------------
# RC / R mode: kpex extracts a resistor mesh but never wires it to the devices
# --------------------------------------------------------------------------------------------
# `RCX25NetlistExpander.expand` (kpex 0.3.12) dup()s the LVS netlist, creates one NEW net per
# resistor-mesh node -- named `<net>.<node>` -- and adds the R/C cards between those new nets. It
# never disconnects a single device terminal from its flat net, so the mesh is an electrically
# isolated island by construction: `mesh nodes INTERSECT device pins` is EMPTY, every device still
# sees the ideal flat node, and `.option rshunt=…` (needed to stop ngspice reporting a singular
# matrix on the floating mesh) makes an RC run return the CC numbers to five digits. `n_r > 0` is
# therefore NOT evidence that resistance was extracted. There is no kpex flag for this: `--mode`
# only selects CC/RC/R, and `--magic_short` belongs to the (unusable) magic engine.
#
# The stitch below repairs it from kpex's own report database, which is exact rather than
# heuristic: every mesh node that sits on a device terminal is emitted as a `[Device Terminal]`
# node whose marker polygon is the terminal's own region, and the same polygon appears under the
# request's device list against `<device name>: <class>` / `<terminal>`. Matching the two on
# (net, layer, polygon) gives `(device, terminal) -> mesh node` with no geometry search.
#
# WHERE the flat net joins the mesh decides every port-referred resistance, and kpex only names
# that point itself when the net has a real PIN. `RCX25NetlistExpander` names a mesh node
# `<net>.<node>` unless the node carries a plain net name, which happens for a `VertexPort` -- a
# kpex `[Pin]` node. A pin needs BOTH a text on the layer's label purpose AND a polygon on its pin
# purpose containing that text (`klayout_pex/klayout/lvsdb_extractor.py`, `pins_of_layer` /
# `labels_of_layer` / `pin_labels = labels & pins`); IHP SG13G2 spells those `<metal>/25` and
# `<metal>/2`. A layout with labels but no pin polygons -- the common case -- yields ZERO `[Pin]`
# nodes, kpex composes every node name as `<net>.<node>`, and the whole mesh floats off the net.
#
# So the tie point is ours to choose, and the choice is not cosmetic. Choosing it by name (the
# first cut did) can only ever land on a DEVICE TERMINAL, because those are the only mesh nodes we
# can name from the terminal map -- and a device terminal sits on diffusion or poly, BELOW the
# contact stack. On the LDO that referred the `vdd` port to a `pSD` node: port current then ran
# down one device's contacts and back up another's, and R(port -> each of 39 pass columns) read
# 49.04-49.19 Ohm -- near-constant, because it is two contact stacks in series, not metal -- where
# the same mesh gives 0.634 Ohm end to end on the TopMetal1 strap (hand solve: 0.59). The rule
# below excludes every layer that carries a device terminal anywhere in the design (exactly the
# diffusion/poly layers) and then takes the lowest sheet resistance among what is left, which is
# the routing layer the port is drawn on. Same mesh, same values: `vdd` -> column becomes ~9 Ohm,
# 0.63 of it the strap and the rest the target column's OWN contacts (SG13G2 `Cont` is
# 0.435 Ohm*um^2 over a 0.16 um square = ~17 Ohm per cut), which is physical.
#
# Three things stay approximations, and none is invented by this module:
#   * a device terminal drawn as several shapes becomes several mesh nodes; the device is attached
#     at the lowest-sorted one and the others stay as ordinary mesh nodes.
#   * without a `[Pin]` node the anchor is the best PROXY for the port, not the port: it is on the
#     right layer but not at the pin, so a port-referred R carries the metal between the two (0.63
#     Ohm on the LDO `vdd` strap). `mesh["anchors"]` records the node and whether it was a pin.
#   * kpex lumps coupling C per NET, so the whole `Cext_` load of a net hangs at its flat node.
#
# The join is a NODE MERGE, not a 0 Ohm resistor. ngspice coerces a 0 Ohm R to 1e-12 Ohm (1e12 S),
# and a mesh full of them is what made the LDO's `.op` drop from KLU to SPARSE 1.3 and then fail
# gmin/source stepping. The ties were only 33 of those; the other 3099 are kpex's own, because
# SG13G2 gives `nSD`/`pSD` 0.0 Ohm/sq, so every diffusion-to-diffusion edge is exactly 0. Merging
# both classes of zero edge is exact -- a 0 Ohm element IS one node -- and it is what makes the
# stitched netlist solvable.

_MESH_NODE = re.compile(r"^(?P<net>.+)\.(?P<sub>[$P]\d+\.\d+)$")
_CARD = re.compile(r"^([A-Za-z])(\S+)")
_PARASITIC = re.compile(r"^(ext|stitch)_", re.I)  # kpex's own cards, and the ties added below
_NODE_TITLE = re.compile(
    r"^\[(?P<kind>[^\]]+)\] (?P<name>\S+), port net (?P<node>\S+), layer (?P<layer>\S+)$"
)
# `18: Metal1 (LVS metal1_con), 0.11 mΩ/µm^2` -- kpex mislabels the unit; the value is Ω/square
# (`klayout_pex/tech_info.py`: "RExtractorTech.Conductor.resistance is in Ω/µm^2").
_CONDUCTOR = re.compile(r"^\d+:\s*(?P<name>\S+)\s*\(LVS [^)]*\),\s*(?P<r>[-+0-9.eE]+)\s")
# device-terminal order on a SPICE card, by card letter
_PINS: dict[str, tuple[str, ...]] = {
    "M": ("D", "G", "S", "B"),
    "Q": ("C", "B", "E", "S"),
    "D": ("A", "C"),
    "R": ("A", "B"),
    "C": ("A", "B"),
    "L": ("A", "B"),
}


def _cards(text: str) -> list[tuple[int, str]]:
    """`(index of the card's first physical line, card text with `+` continuations joined)`."""
    out: list[tuple[int, str]] = []
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s or s.startswith(("*", ".", "+")):
            continue
        j, joined = i + 1, s
        while j < len(lines) and lines[j].lstrip().startswith("+"):
            joined += " " + lines[j].lstrip()[1:].strip()
            j += 1
        out.append((i, joined))
    return out


def mesh_node(node: str) -> tuple[str, str] | None:
    r"""`(net, sub-node)` for a kpex mesh node like ``vss.P0.24`` / ``\$25.$0.17``; else None."""
    m = _MESH_NODE.match(node)
    return (m.group("net"), m.group("sub")) if m else None


def check_mesh_connectivity(netlist: str | Path) -> tuple[bool, dict[str, Any]]:
    """Is every resistor mesh actually part of the circuit?

    Returns ``(ok, detail)``. Only R cards are edges — a capacitor is not a DC path — and only
    nets that HAVE mesh nodes are checked, so a CC-mode netlist (no mesh at all) passes trivially.
    A net fails when its flat node and its mesh sit in different components, i.e. when nothing
    joins the mesh to the devices and ports that carry the net. A netlist that still carries a
    0 Ω parasitic card fails too: ngspice does not merge such a node pair, it clamps the value
    and solves a different circuit (``n_zero_r_cards``).
    """
    text = _read_netlist(netlist)
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    pin_nodes: set[str] = set()
    mesh_by_net: dict[str, set[str]] = {}
    zero_r: list[str] = []
    for _, card in _cards(text):
        toks = card.split()
        m = _CARD.match(toks[0])
        if not m:
            continue
        letter = m.group(1).upper()
        nodes = toks[1 : 1 + len(_PINS.get(letter, ()))]
        if letter == "R" and _PARASITIC.match(m.group(2)) and len(toks) >= 4:
            if _num(toks[3]) == 0.0:
                zero_r.append(toks[0])
        for n in nodes:
            split = mesh_node(n)
            if split:
                mesh_by_net.setdefault(split[0], set()).add(n)
        if letter == "R" and len(nodes) >= 2:
            union(nodes[0], nodes[1])  # a resistor IS a DC path, parasitic or not
        if letter in ("C", "L"):
            continue  # a capacitor is no DC path; an inductor carries no pin we need to place
        if letter != "R" or not _PARASITIC.match(m.group(2)):
            pin_nodes.update(nodes)  # a real device terminal — `Rext_`/`Rstitch_` are not
    open_nets: list[str] = []
    stub_nets: list[str] = []
    for net, mesh in sorted(mesh_by_net.items()):
        roots = {find(n) for n in mesh} | {find(net)}
        if len(roots) > 1:
            open_nets.append(net)
        elif not (pin_nodes & mesh):
            stub_nets.append(net)
    mesh_all = {n for s in mesh_by_net.values() for n in s}
    detail: dict[str, Any] = {
        "n_mesh_nodes": len(mesh_all),
        "n_device_pins": len(pin_nodes),
        "n_pins_on_mesh": len(pin_nodes & mesh_all),
        "n_nets_with_mesh": len(mesh_by_net),
        "open_nets": open_nets[:20],
        "n_open_nets": len(open_nets),
        # connected, but with no device pin ON the mesh: everything on the net hangs off the one
        # tie, so the mesh is a dangling stub and measures nothing. On the LDO these are the 18
        # resistor-divider nets, because kpex registers no terminal regions for `rhigh` devices
        # at all — there is no node to attach them to, and that is a limit worth seeing.
        "stub_nets": stub_nets[:20],
        "n_stub_nets": len(stub_nets),
        # ngspice coerces a 0 Ω resistor to 1e-12 Ω and puts a 1e12 S entry into a matrix whose
        # signal entries are ~1e-5 S; the direct solve then returns a NON-SOLUTION, quietly (the
        # LDO's `.op` violated KCL at `fb` by ~1.5 uA on two such cards). kpex writes them where
        # it means "these two nodes are one", so a stitched netlist must have none left.
        "zero_r_cards": zero_r[:20],
        "n_zero_r_cards": len(zero_r),
    }
    if not mesh_all:
        return True, detail
    ok = not open_nets and bool(pin_nodes & mesh_all) and not zero_r
    return ok, detail


def read_terminal_map(report_rdb: str | Path) -> dict[tuple[str, str], str]:
    """``(device name, terminal name) -> mesh node`` from kpex's ``*_k25d_pex_report.rdb.gz``.

    Matches the device terminal regions kpex logged under ``[R] Extraction Request / Devices``
    against the ``[Device Terminal]`` nodes it logged under ``[R] Extraction Result / Networks``,
    on (net, layer, polygon). A terminal drawn as several shapes yields several nodes; the
    lowest-sorted one is used, so the result is deterministic.
    """
    import klayout.rdb as krdb

    db = krdb.ReportDatabase("")
    db.load(str(report_rdb))

    def child(cat: Any, name: str) -> Any:
        it = cat.each_sub_category() if cat is not None else db.each_category()
        return next((c for c in it if c.name() == name), None)

    def polygons(cat: Any) -> list[str]:
        out = []
        for item in db.each_item_per_category(cat.rdb_id()):
            for v in item.each_value():
                s = str(v)
                if s.startswith("polygon:"):
                    out.append(s.split(":", 1)[1].strip())
        return out

    # (net, layer, polygon) -> mesh node name
    node_by_shape: dict[tuple[str, str, str], str] = {}
    networks = child(child(None, "[R] Extraction Result"), "Networks")
    for net_cat in networks.each_sub_category() if networks else []:
        nodes = child(net_cat, "Nodes")
        for node in nodes.each_sub_category() if nodes else []:
            m = re.match(r"^\[Device Terminal\] (\S+), port net (\S+), layer (\S+)$", node.name())
            if not m:
                continue
            net = net_cat.name()[4:] if net_cat.name().startswith("Net ") else net_cat.name()
            for poly in polygons(node):
                key = (net, m.group(3), poly)
                if key not in node_by_shape or m.group(2) < node_by_shape[key]:
                    node_by_shape[key] = m.group(2)

    out: dict[tuple[str, str], str] = {}
    devices = child(child(None, "[R] Extraction Request"), "Devices")
    for dev in devices.each_sub_category() if devices else []:
        name = dev.name().split(":", 1)[0].strip()
        terms = child(dev, "Terminals")
        for term in terms.each_sub_category() if terms else []:
            m = re.match(r"^(\S+): net (\S+), layer (\S+)$", term.name())
            if not m:
                continue
            hits = sorted(
                node_by_shape[k]
                for k in ((m.group(2), m.group(3), poly) for poly in polygons(term))
                if k in node_by_shape
            )
            if hits:
                out[(name, m.group(1))] = hits[0]
    return out


def read_mesh_info(report_rdb: str | Path) -> tuple[dict[str, tuple[str, str]], dict[str, float]]:
    """``({mesh node: (layer, kind)}, {conductor layer: Ω/square})`` from kpex's report database.

    The node key is the name kpex writes in the SPICE netlist (its ``port net`` field), the kind is
    one of ``Pin`` / ``Device Terminal`` / ``Wire Junction`` / ``Via Junction``, and the sheet
    resistances come from the request's own conductor table. Together they are what
    :func:`pick_anchor` needs to tell a routing node from a diffusion one.
    """
    import klayout.rdb as krdb

    db = krdb.ReportDatabase("")
    db.load(str(report_rdb))

    def child(cat: Any, name: str) -> Any:
        it = cat.each_sub_category() if cat is not None else db.each_category()
        return next((c for c in it if c.name() == name), None)

    nodes: dict[str, tuple[str, str]] = {}
    networks = child(child(None, "[R] Extraction Result"), "Networks")
    for net_cat in networks.each_sub_category() if networks else []:
        cat = child(net_cat, "Nodes")
        for node in cat.each_sub_category() if cat else []:
            m = _NODE_TITLE.match(node.name())
            if m:
                nodes[m.group("node")] = (m.group("layer"), m.group("kind"))

    sheet: dict[str, float] = {}
    request = child(None, "[R] Extraction Request")
    tech = next(
        (c for c in (request.each_sub_category() if request else []) if "Tech" in c.name()), None
    )
    conductors = child(tech, "Conductors")
    for c in conductors.each_sub_category() if conductors else []:
        m = _CONDUCTOR.match(c.name())
        if m:
            sheet[m.group("name")] = float(m.group("r"))
    return nodes, sheet


def pick_anchor(
    nodes: Sequence[str],
    node_info: dict[str, tuple[str, str]],
    sheet: dict[str, float],
    device_layers: set[str],
) -> tuple[str, str]:
    """The mesh node a net's flat node (and so its subckt port) should be merged onto.

    Returns ``(node, kind)`` where kind is ``"pin"`` (kpex's own ``[Pin]`` node — exact) or
    ``"proxy"``. A proxy is chosen on a ROUTING layer: every layer that carries a device terminal
    anywhere in the design is excluded (diffusion and poly, which sit below the contact stack and
    would add two contact stacks to every port-referred resistance), and of what is left the
    lowest sheet resistance wins — the widest, topmost metal the net is drawn on. Ties break on
    the sorted name, so the result is deterministic.
    """
    pins = sorted(n for n in nodes if node_info.get(n, ("", ""))[1].lower() == "pin")
    if pins:
        return pins[0], "pin"
    routing = [n for n in nodes if node_info.get(n, ("", ""))[0] not in device_layers]
    pool = routing or list(nodes)

    def rank(n: str) -> tuple[float, str, str]:
        layer = node_info.get(n, ("", ""))[0]
        return (sheet.get(layer, float("inf")), layer, n)

    return min(sorted(pool), key=rank), "proxy"


def stitch_rc(
    netlist: str | Path,
    terminal_map: dict[tuple[str, str], str],
    *,
    node_info: dict[str, tuple[str, str]] | None = None,
    sheet: dict[str, float] | None = None,
) -> tuple[str, dict[str, Any]]:
    """``(stitched netlist, detail)`` — see :func:`stitch_rc_netlist`."""
    text = _read_netlist(netlist)
    lines = text.splitlines()
    node_info = node_info or {}
    sheet = sheet or {}
    device_layers = {
        layer for layer, kind in node_info.values() if kind.lower() == "device terminal"
    }

    # every mesh node as it is SPELLED in the netlist (kpex escapes a leading `$` as `\$`)
    literal: dict[str, str] = {}
    mesh_by_net: dict[str, set[str]] = {}
    pinned: set[str] = set()  # nets whose flat node kpex already put on the mesh (a `[Pin]` node)
    for _, card in _cards(text):
        toks = card.split()
        m = _CARD.match(toks[0])
        if not m:
            continue
        parasitic = bool(_PARASITIC.match(m.group(2)))
        for n in toks[1 : 1 + len(_PINS.get(m.group(1).upper(), ()))]:
            plain = _net(n)
            literal[plain] = n
            split = mesh_node(plain)
            if split:
                mesh_by_net.setdefault(split[0], set()).add(plain)
            elif parasitic and m.group(1).upper() == "R":
                pinned.add(plain)  # a flat net name on an `Rext_` card is a VertexPort

    # --- 1. repoint each device pin onto the mesh node kpex built at that terminal --------------
    for i, card in _cards(text):
        toks = card.split()
        m = _CARD.match(toks[0])
        if not m or m.group(1).upper() in ("C", "L") or _PARASITIC.match(m.group(2)):
            continue
        pins = _PINS.get(m.group(1).upper())
        head = lines[i].split()
        if not pins or len(head) < 1 + len(pins):
            continue  # pins wrap onto a continuation: leave the card alone, the net tie covers it
        changed = False
        for k, terminal in enumerate(pins, start=1):
            node = terminal_map.get((m.group(2), terminal))
            if node is None or node not in literal:
                continue
            net = mesh_node(node)
            if net is None or _net(head[k]) != net[0]:
                continue  # the mesh node belongs to another net than the card's pin: don't touch
            head[k] = literal[node]
            changed = True
        if changed:
            lines[i] = " ".join(head)

    # --- 2. merge: every 0 Ω parasitic edge, and each flat net node onto its anchor -------------
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    def net_of(n: str) -> str | None:
        """The net a node belongs to — for a mesh node its prefix, for a `[Pin]` node itself.

        kpex spells a ``[Pin]``/VertexPort node with the PLAIN net name (`extraction_results.py`
        `node_name()`), so `fb` and `fb.$24.18` are two nodes of one net even though only the
        second parses as ``<net>.<sub>``. Anything else — a device pin the mesh never reached, a
        bulk node — returns None and is never merged.
        """
        split = mesh_node(n)
        if split:
            return split[0]
        return n if n in pinned else None

    n_zero = 0
    for _, card in _cards(text):
        toks = card.split()
        m = _CARD.match(toks[0])
        if not m or m.group(1).upper() != "R" or not _PARASITIC.match(m.group(2)) or len(toks) < 4:
            continue
        value = _num(toks[3])
        if value is None or value != 0.0:
            continue
        a, b = _net(toks[1]), _net(toks[2])
        na, nb = net_of(a), net_of(b)
        # never let a zero edge merge two different nets: that is a short, not a node identity
        if na is not None and na == nb:
            union(a, b)
            n_zero += 1

    anchors: dict[str, list[str]] = {}
    for net, mesh in sorted(mesh_by_net.items()):
        if net in pinned:
            anchors[net] = [net, node_info.get(net, ("", ""))[0], "pin"]
            continue
        anchor, kind = pick_anchor(sorted(mesh), node_info, sheet, device_layers)
        anchors[net] = [anchor, node_info.get(anchor, ("", ""))[0], kind]
        union(net, anchor)

    # the flat net name is always the class representative, so ports and bulk pins never move
    rep: dict[str, str] = {}
    members: dict[str, list[str]] = {}
    for n in {*literal, *(n for s in mesh_by_net.values() for n in s)}:
        members.setdefault(find(n), []).append(n)
    for root, group in members.items():
        flat = sorted(n for n in group if mesh_node(n) is None)
        rep[root] = flat[0] if flat else sorted(group)[0]
    rename: dict[str, str] = {}
    for group in members.values():
        for n in group:
            target = rep[find(n)]
            if target != n:
                rename[n] = target

    # --- 3. rewrite every node token through the merge, dropping the cards that collapse --------
    n_dropped = 0
    out: list[str] = []
    card_at = {i: card for i, card in _cards(text)}
    for i, raw in enumerate(lines):
        card = card_at.get(i)
        if card is None:
            out.append(raw)
            continue
        m = _CARD.match(card.split()[0])
        toks = raw.split()
        n_pins = len(_PINS.get(m.group(1).upper(), ())) if m else 0
        if m and n_pins and len(toks) >= 1 + n_pins:
            for k in range(1, 1 + n_pins):
                plain = _net(toks[k])
                if plain in rename:
                    toks[k] = literal.get(rename[plain], rename[plain])
            if _PARASITIC.match(m.group(2)) and n_pins >= 2 and _net(toks[1]) == _net(toks[2]):
                n_dropped += 1  # both ends merged into one node: the element is gone, not zero
                continue
            raw = " ".join(toks)
        out.append(raw)

    detail = {
        "anchors": anchors,
        "n_anchor_pins": sum(1 for a in anchors.values() if a[2] == "pin"),
        "n_anchor_proxies": sum(1 for a in anchors.values() if a[2] == "proxy"),
        "n_zero_edges_merged": n_zero,
        "n_cards_collapsed": n_dropped,
    }
    return "\n".join(out) + "\n", detail


def stitch_rc_netlist(
    netlist: str | Path,
    terminal_map: dict[tuple[str, str], str],
    *,
    node_info: dict[str, tuple[str, str]] | None = None,
    sheet: dict[str, float] | None = None,
) -> str:
    """Join each device terminal to the resistor mesh node kpex built at that terminal.

    Rewrites the device cards' pins to their mesh nodes, then MERGES (not 0 Ω-ties) each flat net
    node — which still carries the lumped ``Cext_`` cards, the subckt port and any terminal with no
    mesh node — onto the anchor :func:`pick_anchor` chooses for that net, and merges every 0 Ω
    parasitic edge with it. Only nodes that really occur in the netlist are used, so a terminal
    whose mesh node carries no R element is left on the flat net rather than being floated off it.
    ``node_info``/``sheet`` come from :func:`read_mesh_info`; without them the anchor falls back to
    the lowest-sorted mesh node, which is exactly the defect the block above describes.
    """
    return stitch_rc(netlist, terminal_map, node_info=node_info, sheet=sheet)[0]


class _Unset:
    """Sentinel type: "this keyword was not passed", which `None` cannot express here."""

    __slots__ = ()


_UNSET = _Unset()


def strip_mim_for_pex(
    gds_in: str | Path,
    gds_out: str | Path,
    *,
    mim: tuple[int, int] = (36, 0),
    vmim: tuple[int, int] = (129, 0),
    topmetal1: tuple[int, int] = (126, 0),
    margin_um: float | None = 0.2,
    layers: Sequence[tuple[int, int]] | None = None,
    topmetal_margin_um: float | None | _Unset = _UNSET,
) -> Path:
    """Write a PEX-only copy of ``gds_in`` with the IHP MIM device layers removed (see the
    module docstring). Flattens the top cell. Needs the ``klayout`` python module.

    ``layers`` (default ``(mim, vmim)``) are the (layer, datatype) pairs cleared — an HBT/BiCMOS
    block also drops ``MemCap`` (69, 0). ``topmetal_margin_um`` (alias of ``margin_um``, wins when
    given) is how far TopMetal1 is cut back over the MIM plates; ``None`` keeps TopMetal1 intact so
    the plates stay as plain metal and their coupling to the neighbourhood is still extracted.

    The alias defaults to a SENTINEL, not to ``None``. It used to default to ``None`` and be applied
    only ``if topmetal_margin_um is not None``, which made the documented way to keep the plates —
    passing ``topmetal_margin_um=None`` — indistinguishable from not passing it at all: the cut-back
    happened anyway, silently, and only the undocumented ``margin_um=None`` worked (Codex review,
    item SIGN-03). The whole chain from a flow YAML's ``strip_mim_topmetal_margin_um: null`` was
    affected."""
    import klayout.db as db

    if not isinstance(topmetal_margin_um, _Unset):
        margin_um = topmetal_margin_um
    strip = tuple(layers) if layers is not None else (mim, vmim)
    ly = db.Layout()
    ly.read(str(gds_in))
    top = ly.top_cell()
    lmim = ly.layer(*mim)
    region = db.Region(top.begin_shapes_rec(lmim)).merged()
    top.flatten(True)
    for lay in strip:
        top.shapes(ly.layer(*lay)).clear()
    if margin_um is not None:
        ltm = ly.layer(*topmetal1)
        tm = db.Region(top.begin_shapes_rec(ltm)).merged()
        top.shapes(ltm).clear()
        top.shapes(ltm).insert(tm - region.sized(int(round(margin_um / ly.dbu))))
    ly.write(str(gds_out))
    return Path(gds_out)


def strip_cards(netlist_text: str, prefixes: tuple[str, ...] = ("C",)) -> str:
    """Drop element cards starting with ``prefixes`` (default the ``C`` cards) — the schematic
    kpex compares against when the MIM devices were stripped from the GDS."""
    return (
        "\n".join(ln for ln in netlist_text.splitlines() if ln.lstrip()[:1].upper() not in prefixes)
        + "\n"
    )


def run_pex(
    gds: str | Path,
    cell: str,
    schematic: str | Path,
    out_dir: str | Path,
    *,
    mode: str = "CC",
    pdk: str = "ihp-sg13g2",
    engine: str = "--2.5D",
    timeout_s: int = 3600,
    halo_um: float | None = None,
    stitch_mesh: bool = True,
    ground_nets: Iterable[str] = (),
) -> PexResult:
    """Run kpex on ``cell`` of ``gds`` against ``schematic``.

    ``ground_nets`` adds node names (any case) to :data:`GROUND_NETS` when the extracted C is
    summed, e.g. ``("sub",)`` when the substrate is a subckt pin: that net then gets no
    ``per_net_c_ff`` entry and is in no ``coupling_ff`` pair, and C between it and a signal net
    counts as that signal net's C to ground. The result records the ground set applied
    (``ground_nets``) and the number of self-loop C cards skipped (``n_self``). The extracted
    netlist itself is unchanged.

    ``halo_um`` overrides the tech file's sidewall halo (kpex ``--halo``): couplings between
    shapes farther apart than the halo are DROPPED, so a knob that sweeps a spacing across
    the tech default (IHP: 8 um) sees a fake step in C — raise the halo (e.g. 20) when an
    optimizer explores spacings around it.

    In ``RC``/``R`` mode the extracted mesh kpex writes is an ELECTRICAL ISLAND (see the
    ``stitch_rc_netlist`` block above). ``stitch_mesh`` repairs it from kpex's own report
    database and points ``netlist_path`` at the repaired netlist, keeping the original as
    ``raw_netlist_path``; either way the result is checked with :func:`check_mesh_connectivity`
    and comes back ``ok=False`` with a ``reason`` when the mesh is still open, so a consumer
    cannot score a disconnected mesh as a pass."""
    gds, schematic, out_dir = (
        Path(gds).resolve(),
        Path(schematic).resolve(),
        Path(out_dir).resolve(),
    )
    kp, kl = kpex_exe(), kpex_klayout_exe()
    if not kp:
        return PexResult(
            False,
            False,
            mode,
            reason="kpex not found (SIGNOFF_KPEX / PATH / pex env)",
            halo_um=halo_um,
        )
    if not kl:
        return PexResult(
            False,
            False,
            mode,
            reason="no Ruby≥2.6 klayout for kpex (KPEX_KLAYOUT_EXE)",
            halo_um=halo_um,
        )
    for f in (gds, schematic):
        if not f.is_file():
            return PexResult(False, True, mode, reason=f"input not found: {f}", halo_um=halo_um)
    out_dir.mkdir(parents=True, exist_ok=True)
    # --- keep every artefact kpex's LVS pass writes inside `out_dir` -------------------------
    # kpex drives the PDK's KLayout LVS runset itself and never forwards `-rd target_netlist=`
    # (`klayout_pex/klayout/lvs_runner.py`), so the IHP deck takes the `else` branch of
    # `sg13g2.lvs` and writes `<cell>_extracted.cir` to
    # `Pathname.new(RBA::CellView.active.filename).parent`. That is the INPUT GDS's own directory
    # when a view is loaded, and `..` — the PARENT of the process cwd — when the filename is empty
    # (`Pathname.new("").parent` is `..`). Both branches used to escape: strays landed at the
    # meta-repo root, in `external/`, and beside example GDS files inside the repo.
    # Containment, with no PDK bytes touched:
    #   * run kpex from `out_dir/<gds stem>__<cell>` (the directory kpex writes into anyway), so
    #     the cwd-parent branch resolves to `out_dir`;
    #   * hand kpex a copy of the GDS inside `out_dir`, so the beside-the-GDS branch is `out_dir`.
    work_dir = out_dir / f"{gds.stem}__{cell}"
    work_dir.mkdir(parents=True, exist_ok=True)
    gds_arg = gds
    if not out_dir.samefile(gds.parent):
        gds_arg = out_dir / gds.name
        shutil.copy2(gds, gds_arg)
    env = dict(os.environ)
    env["KPEX_KLAYOUT_EXE"] = kl
    env.setdefault("PDK_ROOT", str(pdk_root()))
    cmd = [
        kp,
        "--pdk",
        pdk,
        "--gds",
        str(gds_arg),
        "--cell",
        cell,
        "--schematic",
        str(schematic),
        engine,
        "--mode",
        mode,
        "--out_dir",
        str(out_dir),
    ]
    if halo_um is not None:
        cmd += ["--halo", str(halo_um)]
    spice = work_dir / f"{cell}_k25d_pex_netlist.spice"
    # Same stale-artifact trap as LVS/DRC: `out_dir` survives between attempts, so a crashed kpex
    # would otherwise be summarized from the previous run's netlist.
    before = snapshot([spice])
    try:
        r = subprocess.run(
            cmd, env=env, cwd=work_dir, capture_output=True, text=True, timeout=timeout_s
        )
    except subprocess.TimeoutExpired as exc:
        partial = proc_output(exc.stdout) + proc_output(exc.stderr)
        return PexResult(
            False,
            True,
            mode,
            log=tail(partial),
            reason=(
                f"kpex timed out after {timeout_s}s: "
                f"{tail(partial.strip() or '(no output before the timeout)', 2000)}"
            ),
            halo_um=halo_um,
        )
    out = r.stdout + r.stderr
    if not written_since([spice], before):
        return PexResult(
            False,
            True,
            mode,
            log=tail(out, 6000),
            reason=(
                f"kpex exited {r.returncode} without writing {spice.name} during this run "
                f"({'a stale file is present' if spice.is_file() else 'no file'}): "
                f"{tail(r.stderr.strip() or r.stdout.strip() or '(no output)', 2000)}"
            ),
            halo_um=halo_um,
        )
    if r.returncode != 0 or not spice.is_file():
        return PexResult(
            False,
            True,
            mode,
            log=tail(out, 6000),
            reason=(
                f"kpex exited {r.returncode}; "
                f"netlist {'found' if spice.is_file() else 'missing'}: "
                f"{tail(r.stderr.strip() or r.stdout.strip() or '(no output)', 2000)}"
            ),
            halo_um=halo_um,
        )
    s = scan_parasitics(spice, ground_nets=ground_nets)
    result = PexResult(
        True,
        True,
        mode,
        netlist_path=str(spice),
        n_c=s.n_c,
        n_r=s.n_r,
        per_net_c_ff=s.per_net_c_ff,
        coupling_ff=s.coupling_ff,
        log=tail(out),
        raw_netlist_path=str(spice),
        ground_nets=s.ground_nets,
        n_self=s.n_self,
        halo_um=halo_um,
    )
    if mode.upper() not in ("RC", "R"):
        return result
    return _finish_rc(result, spice, work_dir / f"{cell}_k25d_pex_report.rdb.gz", stitch_mesh)


def _finish_rc(result: PexResult, spice: Path, report_rdb: Path, stitch_mesh: bool) -> PexResult:
    """Stitch the resistor mesh onto the device pins, then refuse to pass an open mesh."""
    stitch_detail: dict[str, Any] = {}
    if stitch_mesh:
        if not report_rdb.is_file():
            result.ok = False
            result.reason = (
                f"RC/R extraction cannot be stitched to the devices: kpex wrote no "
                f"{report_rdb.name}, which is the only record of which mesh node sits on which "
                f"device terminal. Without it the mesh is an island and n_r is meaningless."
            )
            return result
        try:
            tmap = read_terminal_map(report_rdb)
        except Exception as exc:  # a report we cannot read is a failed stage, not a pass
            result.ok = False
            result.reason = f"could not read the kpex report {report_rdb.name}: {exc}"
            return result
        if not tmap:
            result.ok = False
            result.reason = (
                f"kpex logged no [Device Terminal] mesh nodes in {report_rdb.name}, so the "
                f"resistor mesh cannot be joined to any device pin"
            )
            return result
        try:
            node_info, sheet = read_mesh_info(report_rdb)
        except Exception:  # the anchor degrades to name order, which is a worse tie, not a crash
            node_info, sheet = {}, {}
        stitched = spice.with_name(spice.stem + "_stitched" + spice.suffix)
        text, stitch_detail = stitch_rc(spice, tmap, node_info=node_info, sheet=sheet)
        stitched.write_text(text)
        result.netlist_path = str(stitched)
    ok, detail = check_mesh_connectivity(result.netlist_path or spice)
    detail.update(stitch_detail)
    result.mesh_connected, result.mesh = ok, detail
    if not ok and detail["n_zero_r_cards"] and not detail["n_open_nets"]:
        result.ok = False
        result.reason = (
            f"{detail['n_zero_r_cards']} zero-ohm parasitic card(s) survive in the extracted "
            f"netlist (e.g. {', '.join(detail['zero_r_cards'][:5])}). ngspice does not read a "
            f"0 ohm resistor as a node merge: it clamps it to 1e-12 ohm and solves a different "
            f"circuit, converging quietly to a point that violates KCL. Each such card is either "
            f"a node identity the stitch should have contracted, or a short between two nets"
        )
    elif not ok:
        result.ok = False
        result.reason = (
            f"the extracted resistor mesh is not connected to the circuit: "
            f"{detail['n_pins_on_mesh']} of {detail['n_device_pins']} device pins sit on a mesh "
            f"node and {detail['n_open_nets']} of {detail['n_nets_with_mesh']} nets have a mesh "
            f"with no path to their net node (e.g. {', '.join(detail['open_nets'][:5]) or 'none'})."
            f" n_r={result.n_r} counts cards, not extracted resistance"
        )
    return result
