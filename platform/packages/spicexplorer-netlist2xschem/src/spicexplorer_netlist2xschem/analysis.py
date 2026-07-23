"""Topology analysis for readable placement.

Extracts the structure a human uses to draw an OTA: which nets are supply rails, the vertical
*rank* of each net (VDD at top → VSS at bottom, following the drain↔source current path), matched
**differential pairs** and **current mirrors** (the netlist's symmetry), and a left/right/centre
**side** for each device so symmetric structures sit mirror-imaged about a centre line.

All heuristics degrade gracefully: a device that doesn't fit a pattern lands in the centre column at
its rank row, so non-OTA netlists still get a sane (if plainer) layout.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations

from .ingest import Device, DeviceKind, MosPolarity, N2XCircuit

__all__ = ["TopologyInfo", "analyze"]

_SEP = (
    0.16  # rank separation a device imposes between its high (toward VDD) and low (toward VSS) net
)
_RELAX_ITERS = 240


@dataclass(frozen=True)
class TopologyInfo:
    vdd_nets: frozenset[str]
    vss_nets: frozenset[str]  # includes GND (both are AC grounds drawn at the bottom)
    net_rank: dict[str, float]  # 0.0 = top (VDD) … 1.0 = bottom (VSS)
    device_rank: dict[str, float]  # vertical rank of each device (midpoint of its current path)
    # discrete integer row coordinate: 0 = top (a VDD net) … L_max = bottom (VSS), one row per
    # longest-path layer of the drain↔source current graph. Unlike ``net_rank`` (a continuous
    # relaxation that smears a multistage amp across many fractional rows), levels are small
    # consecutive integers shared across stages — so a row of mirror outputs lines up exactly.
    net_level: dict[str, int] = field(default_factory=dict)
    device_level: dict[str, int] = field(default_factory=dict)  # a MOS's row = its high net's level
    side: dict[str, str] = field(default_factory=dict)  # device ref -> "L" | "R" | "C"
    pairs: list[tuple[str, str]] = field(default_factory=list)  # matched (left, right) device refs
    # net -> port direction ("in" | "out" | "inout") for nets that are circuit I/O (drawn as pins).
    port_role: dict[str, str] = field(default_factory=dict)
    # unordered device pairs whose GATE pins share a net (current-mirror / cascode-bias gate buses).
    gate_share_pairs: list[tuple[str, str]] = field(default_factory=list)
    # device refs that are diode-connected (gate net == drain net) — current-mirror references.
    diode_refs: frozenset[str] = field(default_factory=frozenset)
    # gate-net connected components of ≥2 MOSFETs (current mirrors / cascode-bias banks): every
    # member shares a gate, so they sit on one row with a single straight gate bus.
    mirror_groups: list[frozenset[str]] = field(default_factory=list)

    def is_supply(self, net: str) -> bool:
        return net in self.vdd_nets or net in self.vss_nets


def _high_low_nets(dev: Device) -> tuple[str, str] | None:
    """The device's (high, low) current-path nets — high is drawn toward VDD, low toward VSS.

    NMOS conducts drain→source (drain high); PMOS source→drain (source high). Gates/bulk are not on
    the vertical current path (gates are wired horizontally), so they don't set rank.
    """
    if dev.kind is not DeviceKind.MOS:
        return None
    if dev.polarity is MosPolarity.NMOS:
        return dev.nets["DRAIN"], dev.nets["SOURCE"]
    if dev.polarity is MosPolarity.PMOS:
        return dev.nets["SOURCE"], dev.nets["DRAIN"]
    return None


def _net_ranks(circuit: N2XCircuit) -> tuple[dict[str, float], frozenset[str], frozenset[str]]:
    vdd = frozenset(n for n, r in circuit.supply.items() if r == "VDD")
    vss = frozenset(n for n, r in circuit.supply.items() if r in ("VSS", "GND"))
    fixed = vdd | vss
    rank: dict[str, float] = {
        n: (0.0 if n in vdd else 1.0 if n in vss else 0.5) for n in circuit.nets
    }
    edges = [hl for d in circuit.devices if (hl := _high_low_nets(d)) is not None]
    if not edges:
        return rank, vdd, vss
    # Relax: across each device the high net wants to sit _SEP above its low net (smaller rank = up).
    for _ in range(_RELAX_ITERS):
        acc: dict[str, list[float]] = defaultdict(list)
        for high, low in edges:
            acc[high].append(rank[low] - _SEP)
            acc[low].append(rank[high] + _SEP)
        for net, wants in acc.items():
            if net in fixed:
                continue
            rank[net] = min(1.0, max(0.0, sum(wants) / len(wants)))
    return rank, vdd, vss


def _device_rank(dev: Device, net_rank: dict[str, float]) -> float:
    hl = _high_low_nets(dev)
    if hl is not None:
        return (net_rank[hl[0]] + net_rank[hl[1]]) / 2.0
    # passives / sources: midpoint of all their nets' ranks
    nets = list(dev.nets.values())
    return sum(net_rank[n] for n in nets) / len(nets) if nets else 0.5


def _size_key(dev: Device) -> tuple[str, str, str]:
    """A device's size signature: ``(W, L, M)`` as written. Two matched pair halves must agree on
    all three — including the multiplier ``M``, which AnalogGym varies (``*4`` vs ``*8``) between
    otherwise-identical bias devices, so W/L alone is too coarse a match."""

    def g(key: str) -> str:
        return next((str(v) for k, v in dev.params.items() if k.lower() == key), "")

    return g("w"), g("l"), g("m")


def _diff_pairs(circuit: N2XCircuit, supply: frozenset[str]) -> list[tuple[str, str]]:
    """Matched source-coupled (differential) pairs: same polarity + W/L/M, sharing a **non-supply**
    source net (a private tail), with different gate nets.

    The non-supply requirement is load-bearing. In a uniform-model import every same-size PMOS shares
    ``source=vdd`` and every NMOS shares ``source=vss``, so matching on a supply source spuriously
    pairs an entire bias bank (on ``ramos_pfc`` the old rule found 4 "pairs", 3 of them across the
    supply rail). A genuine differential pair is the *only* place two matched transistors share a
    private node — the tail — so that is the signature we key on. Deterministic: group by
    ``(source, polarity, size)`` in sorted order, then pair distinct-gate members by ref.
    """
    mos = [d for d in circuit.devices if d.kind is DeviceKind.MOS]
    by_key: dict[tuple[MosPolarity, str, tuple[str, str, str]], list[Device]] = defaultdict(list)
    for d in mos:
        src = d.nets.get("SOURCE")
        if src is None or src in supply:
            continue
        by_key[(d.polarity, src, _size_key(d))].append(d)
    pairs: list[tuple[str, str]] = []
    for key in sorted(by_key, key=lambda k: (k[1], k[0].value, k[2])):
        group = sorted(by_key[key], key=lambda d: d.ref)
        used: set[str] = set()
        for i, a in enumerate(group):
            if a.ref in used:
                continue
            for b in group[i + 1 :]:
                if b.ref not in used and a.nets.get("GATE") != b.nets.get("GATE"):
                    pairs.append((a.ref, b.ref))
                    used.update({a.ref, b.ref})
                    break
    return pairs


def _assign_sides(
    circuit: N2XCircuit, pairs: list[tuple[str, str]], supply: frozenset[str]
) -> dict[str, str]:
    """Seed L/R from the matched pairs (by drain net), then propagate along drain/source nets.

    A device follows the side of the non-supply net on its drain (the signal it drives), then its
    source; nets pulled by both sides — tails, bias rails, mirror gates — stay centre.
    """
    by_ref = {d.ref: d for d in circuit.devices}
    side: dict[str, str] = {}
    for left, right in pairs:
        # Orient so the left device is the one with the lexicographically smaller drain net, for
        # determinism (the pair is otherwise symmetric).
        a, b = by_ref[left], by_ref[right]
        if a.nets.get("DRAIN", "") <= b.nets.get("DRAIN", ""):
            side[left], side[right] = "L", "R"
        else:
            side[left], side[right] = "R", "L"

    def device_signal_nets(d: Device) -> list[str]:
        if d.kind is DeviceKind.MOS:
            return [d.nets["DRAIN"], d.nets["SOURCE"]]
        return [n for n in d.nets.values() if n not in supply]

    for _ in range(12):
        # net side from the devices already sided
        net_sides: dict[str, set[str]] = defaultdict(set)
        for ref, s in side.items():
            if s in ("L", "R"):
                for n in device_signal_nets(by_ref[ref]):
                    if n not in supply:
                        net_sides[n].add(s)
        net_side = {n: next(iter(ss)) for n, ss in net_sides.items() if len(ss) == 1}
        changed = False
        for d in circuit.devices:
            if side.get(d.ref) in ("L", "R"):
                continue
            cand = [net_side[n] for n in device_signal_nets(d) if n in net_side]
            uniq = set(cand)
            new = next(iter(uniq)) if len(uniq) == 1 else None
            if new is not None and side.get(d.ref) != new:
                side[d.ref] = new
                changed = True
        if not changed:
            break

    for d in circuit.devices:
        side.setdefault(d.ref, "C")
    return side


def _net_pins(circuit: N2XCircuit) -> dict[str, list[tuple[str, str]]]:
    """net -> list of ``(device ref, canonical pin name)`` touching it."""
    out: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for d in circuit.devices:
        for pin, net in d.nets.items():
            out[net].append((d.ref, pin))
    return out


def _port_roles(
    circuit: N2XCircuit, supply: frozenset[str], net_pins: dict[str, list[tuple[str, str]]]
) -> dict[str, str]:
    """Classify circuit-I/O nets and their direction (drawn as ipin/opin/iopin port symbols).

    A port is either a declared ``.subckt`` formal port or a non-supply net that touches exactly one
    device pin (a dangling external node). Direction follows the pins it touches: gate-only → input,
    anything on a drain → output, otherwise bidirectional (a bias/source connection).
    """
    candidates = set(circuit.ports) | {n for n, p in net_pins.items() if len(p) == 1}
    roles: dict[str, str] = {}
    for net in candidates:
        if net in supply or net not in net_pins:
            continue
        pin_names = {pin for _, pin in net_pins[net]}
        if pin_names <= {"GATE"}:
            roles[net] = "in"
        elif "DRAIN" in pin_names:
            roles[net] = "out"
        else:
            roles[net] = "inout"
    return roles


def _gate_share_pairs(circuit: N2XCircuit) -> list[tuple[str, str]]:
    """Device pairs whose GATE pins share a net — mirror/bias gate buses to face and wire together."""
    by_gate: dict[str, list[str]] = defaultdict(list)
    for d in circuit.devices:
        if d.kind is DeviceKind.MOS and "GATE" in d.nets:
            by_gate[d.nets["GATE"]].append(d.ref)
    pairs: list[tuple[str, str]] = []
    for refs in by_gate.values():
        if len(refs) >= 2:
            pairs.extend(combinations(sorted(refs), 2))
    return pairs


def _diode_refs(circuit: N2XCircuit) -> frozenset[str]:
    """MOSFETs whose gate net equals their drain net — diode-connected current-mirror references."""
    return frozenset(
        d.ref
        for d in circuit.devices
        if d.kind is DeviceKind.MOS and d.nets.get("GATE") is not None
        and d.nets.get("GATE") == d.nets.get("DRAIN")
    )


def _net_levels(
    circuit: N2XCircuit, vdd: frozenset[str], vss: frozenset[str]
) -> dict[str, int]:
    """Discrete row index per net by **longest-path layering** of the drain↔source current graph.

    Each MOS contributes a directed edge ``high → low`` (high = the net drawn toward VDD; reuse
    :func:`_high_low_nets`). VDD nets are level 0; a net's level is ``1 + max(level of its
    predecessors)`` along the longest path, so a device always sits one row below the net it hangs
    from and a cascode stack is rows 0,1,2,… This is the integer analogue of ``net_rank`` and the
    reason a multistage amp collapses to a few rows: stages share nets, so they share levels.

    The graph can contain cycles (a feedback node, a cross-coupled pair), so a deterministic DFS
    (children visited in sorted order) classifies any edge back to a node still on the recursion
    stack as a *back-edge* and drops it for layering only — connectivity is unaffected (the wiring
    layer is what actually connects nets). VSS/GND is pinned to the bottom row, and the occupied
    level values are renumbered to consecutive integers so there are no empty rows.
    """
    nets = list(circuit.nets)
    adj: dict[str, set[str]] = defaultdict(set)
    for d in circuit.devices:
        hl = _high_low_nets(d)
        if hl is not None and hl[0] != hl[1]:
            adj[hl[0]].add(hl[1])

    # 1. Break cycles → DAG (succ), keeping only non-back edges, in deterministic order.
    color: dict[str, int] = dict.fromkeys(nets, 0)  # 0=white 1=on-stack 2=done
    succ: dict[str, list[str]] = defaultdict(list)

    def visit(stack_root: str) -> None:
        stack = [(stack_root, iter(sorted(adj.get(stack_root, ()))))]
        color[stack_root] = 1
        while stack:
            u, it = stack[-1]
            for v in it:
                cv = color.get(v, 0)
                if cv == 1:
                    continue  # back-edge into the current path → drop for layering
                succ[u].append(v)
                if cv == 0:
                    color[v] = 1
                    stack.append((v, iter(sorted(adj.get(v, ())))))
                    break
            else:
                color[u] = 2
                stack.pop()

    for n in sorted(nets):
        if color.get(n, 0) == 0:
            visit(n)

    # 2. Topological order (Kahn); longest paths are order-independent given a valid topo order.
    preds: dict[str, list[str]] = defaultdict(list)
    indeg: dict[str, int] = dict.fromkeys(nets, 0)
    for u, vs in succ.items():
        for v in vs:
            preds[v].append(u)
            indeg[v] += 1
    topo: list[str] = [n for n in nets if indeg[n] == 0]
    head = 0
    while head < len(topo):
        u = topo[head]
        head += 1
        for v in succ.get(u, ()):
            indeg[v] -= 1
            if indeg[v] == 0:
                topo.append(v)

    # Longest path *down from VDD* (top depth) and *up from VSS* (bottom height). A net on a real
    # VDD→VSS path is fixed by its top depth; a bias node reachable only from VSS (e.g. a current-
    # mirror reference fed by an external ibias) has no top depth and is placed by its height above
    # VSS, so it lands near the bottom rail instead of defaulting to the top.
    UNSET = -1
    top: dict[str, int] = dict.fromkeys(nets, UNSET)
    for n in vdd:
        top[n] = 0
    for u in topo:
        if top[u] == UNSET:
            cand = [top[p] for p in preds[u] if top[p] != UNSET]
            if cand:
                top[u] = max(cand) + 1
    bot: dict[str, int] = dict.fromkeys(nets, UNSET)
    for n in vss:
        bot[n] = 0
    for u in reversed(topo):
        if bot[u] == UNSET:
            cand = [bot[s] for s in succ.get(u, ()) if bot[s] != UNSET]
            if cand:
                bot[u] = max(cand) + 1

    height = max([v for v in top.values() if v != UNSET] + [v for v in bot.values() if v != UNSET] + [0])
    level: dict[str, int] = {}
    for n in nets:
        if top[n] != UNSET:
            level[n] = top[n]
        elif bot[n] != UNSET:
            level[n] = height - bot[n]
        else:
            level[n] = height // 2  # floating (gate-only) net: park mid-height
    for n in vdd:
        level[n] = 0
    for n in vss:
        level[n] = height
    # 3. Renumber occupied levels to consecutive integers (collapse any empty row).
    remap = {v: i for i, v in enumerate(sorted(set(level.values())))}
    return {n: remap[v] for n, v in level.items()}


def _device_level(dev: Device, net_level: dict[str, int]) -> int:
    """A device's integer row: a MOS sits at its **high** net's level (the net it hangs from toward
    VDD); a passive/source sits at the midpoint of its terminals' levels."""
    hl = _high_low_nets(dev)
    if hl is not None:
        return net_level.get(hl[0], 0)
    levels = [net_level[n] for n in dev.nets.values() if n in net_level]
    return round(sum(levels) / len(levels)) if levels else 0


def _mirror_groups(circuit: N2XCircuit) -> list[frozenset[str]]:
    """Connected components of MOSFETs that share a gate net (mirrors / cascode-bias banks), each
    with ≥2 members. These are laid on one row with a single straight gate bus."""
    mos = [d for d in circuit.devices if d.kind is DeviceKind.MOS]
    by_gate: dict[str, list[str]] = defaultdict(list)
    for d in mos:
        g = d.nets.get("GATE")
        if g is not None:
            by_gate[g].append(d.ref)
    parent = {d.ref: d.ref for d in mos}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for refs in by_gate.values():
        for r in refs[1:]:
            parent[find(r)] = find(refs[0])
    comps: dict[str, set[str]] = defaultdict(set)
    for d in mos:
        comps[find(d.ref)].add(d.ref)
    groups = [frozenset(s) for s in comps.values() if len(s) >= 2]
    return sorted(groups, key=lambda g: min(g))


def analyze(circuit: N2XCircuit) -> TopologyInfo:
    """Compute supply rails, vertical ranks + levels, matched pairs, sides, ports, gate buses, and
    diodes."""
    net_rank, vdd, vss = _net_ranks(circuit)
    supply = vdd | vss
    net_level = _net_levels(circuit, vdd, vss)
    pairs = _diff_pairs(circuit, supply)
    side = _assign_sides(circuit, pairs, supply)
    device_rank = {d.ref: _device_rank(d, net_rank) for d in circuit.devices}
    device_level = {d.ref: _device_level(d, net_level) for d in circuit.devices}
    net_pins = _net_pins(circuit)
    return TopologyInfo(
        vdd_nets=vdd,
        vss_nets=vss,
        net_rank=net_rank,
        device_rank=device_rank,
        net_level=net_level,
        device_level=device_level,
        side=side,
        pairs=pairs,
        port_role=_port_roles(circuit, supply, net_pins),
        gate_share_pairs=_gate_share_pairs(circuit),
        diode_refs=_diode_refs(circuit),
        mirror_groups=_mirror_groups(circuit),
    )
