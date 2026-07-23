"""Device placement strategies.

A :class:`Placer` assigns an xschem :class:`~.geometry.Transform` to every device in a circuit. The
protocol takes the abstract :class:`~.ingest.N2XCircuit` (not a graph), so a richer placer can be
dropped in later — e.g. a topology-aware one that reads ``circuit.supply`` to put PMOS near VDD and
NMOS near VSS — without changing the emit pipeline.

v1 ships :class:`GridPlacer`: a deterministic grid (devices sorted by ref). :class:`TopologyPlacer`
is the readable one used by default.

**Block-aware placement.** ``place`` also accepts an optional :class:`PlacementHints` carrying
*device-ref clusters* — groups of instance refs an upstream detector recognised as one functional
sub-circuit (a current mirror, a differential pair, …; see
:mod:`~spicexplorer_netlist2xschem.annotation`). When given, :class:`PhasedPlacer` biases its column
ordering so a block's devices end up *adjacent* (tight, non-overlapping annotation boxes) instead of
scattered by raw topology. Hints are a pure layout *suggestion* — they never change connectivity, and
``hints=None`` reproduces the block-agnostic layout byte-for-byte, so the no-annotation path is
unchanged. The structure is deliberately open to richer signals later (per-device *stage* / *role*).
"""

from __future__ import annotations

import inspect
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .analysis import TopologyInfo, analyze
from .geometry import Transform, snap
from .ingest import DeviceKind, N2XCircuit
from .sym_library import SymLibrary

__all__ = ["Placer", "PlacementHints", "GridPlacer", "TopologyPlacer", "PhasedPlacer", "place_with_hints"]

_SOURCE_KINDS = frozenset({DeviceKind.VSOURCE, DeviceKind.ISOURCE})  # independent V/I sources


@dataclass(frozen=True)
class PlacementHints:
    """Layout suggestions from an upstream structural detector — never connectivity, only readability.

    ``clusters`` is the load-bearing field: each entry is a group of **device instance refs** that
    form one recognised functional block (e.g. a current mirror's reference + outputs, a differential
    pair's two halves). A block-aware placer keeps each cluster's devices spatially together so the
    functional-block annotation overlay draws tight, non-overlapping boxes. Refs not in any cluster are
    placed by topology as before. A device may appear in at most one cluster (the producer merges
    nested / device-sharing blocks into one coherent group — see
    :meth:`~spicexplorer_netlist2xschem.annotation.BlockAnnotationSet.placement_clusters`).

    The dataclass is intentionally extensible: future detectors can
    add per-device *stage* index or functional *role* maps here to drive richer placement, without
    changing the :class:`Placer` protocol or any call site.
    """

    clusters: tuple[tuple[str, ...], ...] = ()
    # Reserved for later signals (P10 / research 3a) — a per-device stage band and functional role.
    stage: dict[str, int] = field(default_factory=dict)
    role: dict[str, str] = field(default_factory=dict)

    def cluster_of(self) -> dict[str, int]:
        """``device ref -> cluster index`` (a device is in at most one cluster)."""
        return {ref: i for i, members in enumerate(self.clusters) for ref in members}

    def __bool__(self) -> bool:
        return bool(self.clusters or self.stage or self.role)


@runtime_checkable
class Placer(Protocol):
    """Assigns a placement transform to each device ref in a circuit.

    ``hints`` is an optional :class:`PlacementHints` (block clusters from an upstream detector); a
    placer is free to ignore it (the layout is then identical to ``hints=None``)."""

    def place(
        self,
        circuit: N2XCircuit,
        lib: SymLibrary | None = None,
        *,
        hints: PlacementHints | None = None,
    ) -> dict[str, Transform]: ...


def place_with_hints(
    placer: Placer,
    circuit: N2XCircuit,
    lib: SymLibrary | None,
    hints: PlacementHints | None,
) -> dict[str, Transform]:
    """Call ``placer.place`` with ``hints`` when it accepts them, else fall back to the 2-arg form.

    Keeps :func:`~spicexplorer_netlist2xschem.emit.build_sch` working with a third-party placer that
    predates the ``hints`` keyword (added later) — we never mask a real ``TypeError``
    by inspecting the signature instead of catching."""
    if hints is not None:
        params = inspect.signature(placer.place).parameters
        if "hints" in params or any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()):
            return placer.place(circuit, lib, hints=hints)
    return placer.place(circuit, lib)


@dataclass
class GridPlacer:
    """Lay devices on a coarse grid, sorted by ref. rot/flip are 0 (v1)."""

    cols: int | None = None
    pitch_x: int = 240
    pitch_y: int = 240
    origin_x: int = 0
    origin_y: int = 0

    def place(
        self,
        circuit: N2XCircuit,
        lib: SymLibrary | None = None,
        *,
        hints: PlacementHints | None = None,  # noqa: ARG002 — grid layout ignores block hints
    ) -> dict[str, Transform]:
        devices = sorted(circuit.devices, key=lambda d: d.ref)
        n = len(devices)
        cols = self.cols or max(1, math.ceil(math.sqrt(n)))
        out: dict[str, Transform] = {}
        for i, dev in enumerate(devices):
            col, row = i % cols, i // cols
            out[dev.ref] = Transform(
                x=snap(self.origin_x + col * self.pitch_x),
                y=snap(self.origin_y + row * self.pitch_y),
                rot=0,
                flip=0,
            )
        return out


@dataclass
class TopologyPlacer:
    """Topology-aware placement that reads like a hand-drawn OTA.

    * **Rows** follow the VDD→VSS *rank* (PMOS/VDD at top, NMOS/VSS at bottom) so current flows
      top-to-bottom.
    * **Columns** are *current-path branches*: same-side devices linked drain↔source share one column,
      so a cascode/output leg is a clean vertical stack (the longest VDD→VSS path is a straight line).
    * The two symmetric **main legs** straddle centre with the **differential pair** between them; the
      channel between the legs holds nothing else — the tail source and bias mirrors are pushed into a
      compact **bias block** just outside the legs (a device only sits between the legs when it ties to
      a node on a leg's current path, e.g. a 5T/telescopic tail sink under the pair).
    * **Flips** mirror the two halves so that two MOSFETs **sharing a gate net face gate-to-gate**
      across the centre line (left half's gates point right, right half's point left).
    """

    # Pitches give the symbol-baked parameter-text band (~165 units of w/l/model text just outside each
    # device, mirrored onto the gate-opposite side by a flip) a clear lane between columns without making
    # wide (many-branch) circuits sprawl: a modest bump over the symbol size, with the per-label
    # clearance pass (``wiring._device_keepouts``) doing the fine work of keeping names off the text.
    col_pitch: int = 340
    row_pitch: int = 260
    bias_pitch: int = 290  # column pitch inside the bias block (tighter than the main col pitch)
    bias_gap: int = 380  # gap from the outermost main column to the first bias column
    min_dx: int = 160  # minimum x-gap between devices on one row (< half col_pitch; avoids overlap)
    row_merge: float = 0.07  # ranks within this are drawn on the same row

    def place(
        self,
        circuit: N2XCircuit,
        lib: SymLibrary | None = None,
        *,
        hints: PlacementHints | None = None,  # noqa: ARG002 — TopologyPlacer ignores block hints
    ) -> dict[str, Transform]:
        info = analyze(circuit)
        drank = info.device_rank

        # 1. Quantise device ranks into ordered row bands (merge near-equal ranks).
        # 2. Column per branch (the compact floorplan) + the anchor set row-alignment must not move.
        x_of, leg_anchors = self._columns(circuit, info)

        # 3. Rows. Anchor the grid on the **backbone** — the busiest column (an output leg) — so its
        # devices land on consecutive rows 0,1,2,… (a gapless vertical stack), and every other device
        # maps onto that grid by interpolating its rank between the backbone's ranks. Two symmetric legs
        # share the backbone's ranks, so they align; a stub branch lands on the nearest row.
        cols: dict[int, list[str]] = defaultdict(list)
        for ref, x in x_of.items():
            cols[x].append(ref)
        backbone = max(cols.values(), key=lambda refs: (len(refs), -min(x_of[r] for r in refs)))
        anchors = sorted({drank[r] for r in backbone})
        row_int = self._row_assigner(drank, anchors)

        out: dict[str, Transform] = {}
        used_rows: dict[int, set[int]] = defaultdict(set)  # x -> rows taken (keep a column gapless)
        for ref in sorted(x_of, key=lambda r: (drank[r], r)):
            x = x_of[ref]
            row = row_int(ref)
            while row in used_rows[x]:  # two devices rounded onto one cell: stack downward
                row += 1
            used_rows[x].add(row)
            out[ref] = Transform(x=snap(x), y=snap(row * self.row_pitch))
        self._spread_collisions(out)

        # 4. Gate-align current mirrors: pull a mirror's reference / bias devices onto the row of the
        # devices they bias, so the shared gate (and shared source) net is a straight horizontal bus.
        self._align_gate_groups(circuit, info, out, leg_anchors)

        # 5. Flip each device so gate-shared partners face across the centre line (see _assign_flips).
        self._assign_flips(circuit, info, out)
        return out

    # ----------------------------------------------------------------- columns

    def _columns(
        self, circuit: N2XCircuit, info: TopologyInfo
    ) -> tuple[dict[str, int], set[str]]:
        """An x per device plus the set of **anchor** refs (the two main-leg stacks and the centred tail
        device) that row-alignment must not move: vertical branches become columns, the two main legs sit
        astride centre with the diff pair between them, and every other (bias) branch is packed into a
        compact block outside the legs."""
        supply = info.vdd_nets | info.vss_nets
        side = info.side
        by_ref = {d.ref: d for d in circuit.devices}

        net_pins: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for d in circuit.devices:
            for pin, net in d.nets.items():
                net_pins[net].append((d.ref, pin))

        def path_nets(d) -> list[str]:
            if d.kind is DeviceKind.MOS:
                return [d.nets["DRAIN"], d.nets["SOURCE"]]
            return list(d.nets.values())  # passives / sources: both terminals are on the path

        def is_side_feed(ref: str) -> bool:
            """A diff input whose drain joins a node already carrying another device's drain *and*
            source — a fold node feeding a cascode stack. Such an input sits *beside* the stack
            (folded cascode), not inside it."""
            drain = by_ref[ref].nets.get("DRAIN")
            if drain is None:
                return False
            others = [(r, p) for r, p in net_pins[drain] if r != ref]
            return any(p == "DRAIN" for _, p in others) and any(p == "SOURCE" for _, p in others)

        diff_refs = {r for pair in info.pairs for r in pair}
        side_feeds = {r for r in diff_refs if is_side_feed(r)}
        folded = bool(side_feeds)

        # --- branches: union same-side, non-excluded devices that share a non-supply drain/source net.
        # Only the *folded* (side-feed) inputs sit outside their branch; an inline diff device (5T,
        # telescopic) stays stacked with its load so the leg is one column.
        excluded = side_feeds
        parent = {d.ref: d.ref for d in circuit.devices}

        def find(a: str) -> str:
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a: str, b: str) -> None:
            parent[find(b)] = find(a)

        net_devs: dict[str, list[str]] = defaultdict(list)
        for d in circuit.devices:
            if d.ref in excluded:
                continue
            for net in path_nets(d):
                if net not in supply:
                    net_devs[net].append(d.ref)
        for refs in net_devs.values():
            by_s: dict[str, list[str]] = defaultdict(list)
            for r in refs:
                by_s[side.get(r, "C")].append(r)
            for grp in by_s.values():
                for r in grp[1:]:
                    union(grp[0], r)

        branches: dict[str, list[str]] = defaultdict(list)
        for d in circuit.devices:
            if d.ref not in excluded:
                branches[find(d.ref)].append(d.ref)

        def members(root: str) -> list[str]:
            return branches[root]

        def minref(root: str) -> str:
            return min(branches[root])

        def branch_side(root: str) -> str:
            sides = {side.get(r, "C") for r in members(root)}
            if "L" in sides and "R" not in sides:
                return "L"
            if "R" in sides and "L" not in sides:
                return "R"
            return "C"

        # --- main legs: the symmetric output branches the diff pair feeds.
        diff_drains = {by_ref[r].nets.get("DRAIN") for r in diff_refs} - {None}
        main_roots: list[str] = []
        for root in branches:
            if folded:
                if any(set(path_nets(by_ref[m])) & diff_drains for m in members(root)):
                    main_roots.append(root)
            elif any(m in diff_refs for m in members(root)):
                main_roots.append(root)

        out_nets = {n for n, role in info.port_role.items() if role == "out"}

        def carries_output(root: str) -> bool:
            return bool(out_nets & self._branch_nets(root, branches, by_ref))

        left_leg: str | None = None
        right_leg: str | None = None
        if len(main_roots) >= 2:
            # Two legs: keep the **output** leg on the right (beside its output port), so the output
            # net doesn't bus across the whole circuit and clip the other leg's drain/source stack.
            two = sorted(main_roots, key=lambda r: (branch_side(r) != "L", minref(r)))[:2]
            a, b = two
            if carries_output(a) and not carries_output(b):
                left_leg, right_leg = b, a
            elif carries_output(b) and not carries_output(a):
                left_leg, right_leg = a, b
            else:
                left_leg, right_leg = a, b
        elif main_roots:
            (left_leg,) = main_roots[:1]

        # Anchors that row-alignment must not move: the two main-leg stacks (their cascode rows define
        # the grid) and, added below, the centred tail current device.
        anchor_refs: set[str] = set()
        for leg in (left_leg, right_leg):
            if leg is not None:
                anchor_refs.update(members(leg))

        def feeds_left(ref: str) -> bool:
            dn = by_ref[ref].nets.get("DRAIN")
            return left_leg is not None and dn in self._branch_nets(left_leg, branches, by_ref)

        # --- centre block: [left leg] [diff pair, each beside the leg it feeds] [right leg].
        center: list[list[str]] = []
        if left_leg is not None:
            center.append(members(left_leg))
        if folded and diff_refs:
            for r in sorted(diff_refs, key=lambda r: (not feeds_left(r), r)):
                center.append([r])
        if right_leg is not None and right_leg != left_leg:
            center.append(members(right_leg))
        if not center:  # no diff pair / legs at all — fall back to one column per branch, by minref
            center = [members(r) for r in sorted(branches, key=minref)]

        # --- lay out the centre columns. They straddle x=0 (diff pair / leg gap centred).
        x_of: dict[str, int] = {}
        n = len(center)
        origin = (n - 1) / 2.0
        for i, col in enumerate(center):
            x = int(round((i - origin) * self.col_pitch))
            for r in col:
                x_of[r] = x
        left_x = min(x_of.values(), default=0)
        right_x = max(x_of.values(), default=0)

        # --- the bias network: every branch that is not a main leg.
        used = {left_leg, right_leg} - {None}
        bias_roots = [r for r in branches if r not in used]
        placed: set[str] = set()

        def gate_nets(root: str) -> set[str]:
            gs = (by_ref[m].nets.get("GATE") for m in members(root))
            return {g for g in gs if g is not None}

        # --- tail device: the branch whose drain/source ties the diff pair's shared *source* node. It
        # stacks directly above/below the pair, centred between the two legs — the 5T/telescopic/folded
        # tail current source (so the current flowing into the pair's common node reads straight down the
        # middle). Centred between the two pair branches when exactly two feed the node; with more than
        # two it sits over the lowest-numbered branch. Its diode *reference* is parked immediately beside
        # it (a compact, adjacent current mirror) rather than co-centred — so the tail device stays
        # exactly between the pair instead of being shoved off-centre by its reference (the bug this fixes).
        if info.pairs:
            tail_net = by_ref[info.pairs[0][0]].nets.get("SOURCE")
            if tail_net is not None and tail_net not in supply:
                on_tail = sorted(
                    (r for r in diff_refs if r in x_of and tail_net in path_nets(by_ref[r])),
                    key=lambda r: (x_of[r], r),
                )
                if len(on_tail) > 2:
                    center_x = x_of[min(on_tail)]
                elif on_tail:
                    center_x = int(round((x_of[on_tail[0]] + x_of[on_tail[-1]]) / 2))
                else:
                    center_x = 0
                tail_gates: set[str] = set()
                for root in bias_roots:
                    bnets = self._branch_nets(root, branches, by_ref)
                    # only the *current source* into the tail node is centred: a branch that drives the
                    # tail node from a supply rail and is not itself a leg/diff-input branch (so we never
                    # drag a whole output leg that merely shares the tail node, nor a vb↔tail vsource).
                    if (
                        root not in placed
                        and tail_net in bnets
                        and supply & bnets
                        and not (set(members(root)) & diff_refs)
                    ):
                        for r in members(root):
                            x_of[r] = center_x
                        anchor_refs.update(members(root))  # the tail device defines its mirror's row
                        tail_gates |= gate_nets(root)
                        placed.add(root)
                # the tail mirror's diode reference parks just beside the centred device so the pair
                # reads as an adjacent mirror with a short gate bus. The reference is a single-device
                # branch whose own diode gate net *is* the tail device's gate net (so e.g. an unrelated
                # nbias diode that merely shares a column with an ibias mirror leg is not pulled in).
                adj = center_x - self.bias_pitch
                for root in sorted(bias_roots, key=minref):
                    ms = members(root)
                    if root not in placed and len(ms) == 1 and (
                        ms[0] in info.diode_refs and by_ref[ms[0]].nets.get("GATE") in tail_gates
                    ):
                        x_of[ms[0]] = adj
                        placed.add(root)
                        adj -= self.bias_pitch

        # Remaining bias branches: keep gate-share groups contiguous, then deal whole groups to the
        # side with fewer columns so the block stays balanced and every mirror stays together.
        groups = self._gate_groups([r for r in bias_roots if r not in placed], gate_nets, minref)
        left_cols: list[list[str]] = []
        right_cols: list[list[str]] = []
        for group in groups:
            cols = [members(r) for r in group]
            if len(left_cols) <= len(right_cols):
                left_cols = cols[::-1] + left_cols  # grow leftward, group stays contiguous
            else:
                right_cols = right_cols + cols
        x = left_x - self.bias_gap
        for col in reversed(left_cols):  # nearest the leg first
            for r in col:
                x_of[r] = x
            x -= self.bias_pitch
        x = right_x + self.bias_gap
        for col in right_cols:
            for r in col:
                x_of[r] = x
            x += self.bias_pitch

        for d in circuit.devices:  # safety net: anything unplaced lands just right of the block
            x_of.setdefault(d.ref, right_x + self.bias_gap)
        return x_of, anchor_refs

    @staticmethod
    def _branch_nets(root, branches, by_ref) -> set[str]:
        """All drain/source/terminal nets a branch's devices touch (gates excluded for MOS)."""
        out: set[str] = set()
        for m in branches[root]:
            d = by_ref[m]
            if d.kind is DeviceKind.MOS:
                out.update({d.nets.get("DRAIN"), d.nets.get("SOURCE")})
            else:
                out.update(d.nets.values())
        return out - {None}

    @staticmethod
    def _gate_groups(roots, gate_nets, minref) -> list[list[str]]:
        """Cluster bias branch roots into connected groups (sharing a gate net = a current mirror),
        each group a contiguous, deterministically-ordered list."""
        adj: dict[str, set[str]] = {r: set() for r in roots}
        for i, a in enumerate(roots):
            for b in roots[i + 1 :]:
                if gate_nets(a) & gate_nets(b):
                    adj[a].add(b)
                    adj[b].add(a)
        seen: set[str] = set()
        groups: list[list[str]] = []
        for seed in sorted(roots, key=minref):
            if seed in seen:
                continue
            comp: list[str] = []
            stack = [seed]
            while stack:
                cur = stack.pop()
                if cur in seen:
                    continue
                seen.add(cur)
                comp.append(cur)
                stack.extend(sorted(adj[cur] - seen, key=minref, reverse=True))
            groups.append(sorted(comp, key=minref))
        return groups

    # ----------------------------------------------------------------- alignment

    def _align_gate_groups(
        self,
        circuit: N2XCircuit,
        info: TopologyInfo,
        out: dict[str, Transform],
        anchors: set[str],
    ) -> None:
        """Pull current-mirror / shared-gate (and shared non-supply source) MOSFETs onto one row.

        A mirror's reference and its other (bias) outputs are snapped to the row of the device(s) they
        bias, so the shared gate net draws as a single straight horizontal bus rather than a jog. The
        **anchors** — the two main-leg cascode stacks, the diff-pair inputs and the centred tail device —
        never move and define the target row; everything else in a group is pulled onto it. So an unrelated
        mirror's reference that landed on the wrong rank (e.g. a folded-cascode bias mirror split across the
        tail device and the side block) is realigned, while the signal legs keep their vertical stacks.
        """
        by_ref = {d.ref: d for d in circuit.devices}
        supply = info.vdd_nets | info.vss_nets
        diff_refs = {r for pair in info.pairs for r in pair}
        fixed = anchors | diff_refs

        def movable(ref: str) -> bool:
            return ref not in fixed

        # Union MOS into groups by shared gate net and shared non-supply source net (current mirrors and
        # source-coupled clusters); a group is aligned together.
        mos = [d.ref for d in circuit.devices if d.kind is DeviceKind.MOS and d.ref in out]
        parent = {r: r for r in mos}

        def find(a: str) -> str:
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for key in ("GATE", "SOURCE"):
            by_net: dict[str, list[str]] = defaultdict(list)
            for r in mos:
                net = by_ref[r].nets.get(key)
                if net is not None and not (key == "SOURCE" and net in supply):
                    by_net[net].append(r)
            for refs in by_net.values():
                for r in refs[1:]:
                    parent[find(r)] = find(refs[0])

        groups: dict[str, list[str]] = defaultdict(list)
        for r in mos:
            groups[find(r)].append(r)

        for members in groups.values():
            if len(members) < 2:
                continue
            free = [r for r in members if movable(r)]
            if not free:
                continue
            fixed = [r for r in members if r not in free]
            anchor_ys = [out[r].y for r in (fixed or members)]
            target_y = min(Counter(anchor_ys).most_common(), key=lambda kv: (-kv[1], kv[0]))[0]
            for r in free:
                t = out[r]
                if t.y != target_y:
                    out[r] = Transform(x=t.x, y=target_y, rot=t.rot, flip=t.flip)
        self._spread_collisions(out)

    # ----------------------------------------------------------------- flips

    def _assign_flips(
        self, circuit: N2XCircuit, info: TopologyInfo, out: dict[str, Transform]
    ) -> None:
        _assign_gate_flips(circuit, info, out)

    @staticmethod
    def _row_assigner(drank: dict[str, float], anchors: list[float]):
        """Build ``ref -> int row``: the backbone ranks ``anchors`` map to rows 0,1,2,…; any other
        rank is linearly interpolated between the bracketing anchors (and extrapolated past the ends),
        then rounded — so a symmetric leg lands on the same rows and a stub branch on the nearest one."""
        if len(anchors) <= 1:
            return lambda ref: 0

        def row_int(ref: str) -> int:
            r = drank[ref]
            if r <= anchors[0]:
                span = anchors[1] - anchors[0] or 1.0
                frac = (r - anchors[0]) / span
            elif r >= anchors[-1]:
                span = anchors[-1] - anchors[-2] or 1.0
                frac = (len(anchors) - 1) + (r - anchors[-1]) / span
            else:
                frac = next(
                    i + (r - anchors[i]) / (anchors[i + 1] - anchors[i] or 1.0)
                    for i in range(len(anchors) - 1)
                    if anchors[i] <= r <= anchors[i + 1]
                )
            return int(round(frac))

        return row_int

    def _spread_collisions(self, out: dict[str, Transform]) -> None:
        """Enforce a minimum x-gap between devices sharing a row, pushing the right one over.

        Catches exact (x, y) overlaps (same branch + row) and near-overlaps where two columns ended up
        too close, whose pins would otherwise coincide. ``min_dx`` is below half the column pitch, so
        the regular columns are untouched and only genuine collisions move."""
        rows: dict[int, list[str]] = defaultdict(list)
        for ref, t in out.items():
            rows[t.y].append(ref)
        for y, refs in rows.items():
            refs.sort(key=lambda r: (out[r].x, r))
            prev: int | None = None
            for ref in refs:
                t = out[ref]
                nx = t.x if prev is None or t.x - prev >= self.min_dx else prev + self.min_dx
                out[ref] = Transform(x=snap(nx), y=y, rot=t.rot, flip=t.flip)
                prev = nx


def _assign_gate_flips(
    circuit: N2XCircuit, info: TopologyInfo, out: dict[str, Transform]
) -> None:
    """Flip each device so that two MOSFETs sharing a gate net face **gate-to-gate**.

    The gate sits on a MOS symbol's left edge, so ``flip=1`` points it right. A column points its
    gates toward the average position of the devices it shares a gate net with — so a left device
    and its right gate-mate meet gate-to-gate across the gap, and a mirror's members all point at
    each other. A device with **no** gate-shared partner just points inward (toward centre); a
    differential-pair column is always drawn mirror-imaged about the centre (its inputs are not a
    shared gate). Flip is uniform within a column, so each branch's drain/source stack stays
    vertically aligned. (Both placers centre their columns about x=0, so "inward" is ``x < 0``.)
    """
    by_ref = {d.ref: d for d in circuit.devices}
    diff_refs = {r for pair in info.pairs for r in pair}
    gate_users: dict[str, list[str]] = defaultdict(list)
    for d in circuit.devices:
        g = d.nets.get("GATE")
        if g is not None:
            gate_users[g].append(d.ref)

    cols: dict[int, list[str]] = defaultdict(list)
    for ref, t in out.items():
        cols[t.x].append(ref)
    for x, refs in cols.items():
        here = set(refs)
        partner_xs = [
            out[o].x
            for ref in refs
            for o in gate_users.get(by_ref[ref].nets.get("GATE") or "", [])
            if o not in here
        ]
        if here & diff_refs:  # the differential pair is mirror-imaged about centre
            flip = 1 if x < 0 else 0
        elif partner_xs:  # point the column's gates toward its gate-mates
            flip = 1 if (sum(partner_xs) / len(partner_xs)) > x else 0
        else:  # no gate-mate: just face inward
            flip = 1 if x < 0 else 0
        for ref in refs:
            t = out[ref]
            out[ref] = Transform(x=t.x, y=t.y, rot=t.rot, flip=flip)


@dataclass
class PhasedPlacer:
    """Phased, level-banded placement — the readable default.

    The strategy follows how an analog designer drafts a multistage amp, in three phases:

    * **Phase 1 — rows from rails.** Every MOSFET's row is its discrete longest-path *level*
      (:attr:`~.analysis.TopologyInfo.device_level`): the VDD-source bank lands on row 0, a cascode
      sits one row below the device it stacks on, VSS devices at the bottom. A whole multistage amp
      collapses to a handful of rows (one per current-path layer) instead of one row per fractional
      rank — the cure for the vertical sprawl.
    * **Phase 2 — columns from vertical chains.** Devices linked drain↔source through a *true series
      node* (a non-supply net with exactly two drain/source connections) are unioned into a **chain**;
      every member of a chain shares one column x, so a cascode/output leg draws as a dead-straight
      vertical stack (the fix for zig-zag legs). Chains are then ordered left-to-right by the
      barycentre heuristic over their inter-chain neighbour weight (drain/source links strong, gate
      buses weak), so a mirror bank and the stacks it biases end up adjacent. A fan-out/summing node
      (3+ d/s pins — a diff-pair tail, an output node) is *not* a series link, so the signal path is
      never collapsed into a single column. Finally :func:`_assign_gate_flips` mirrors gate-shared
      devices to face gate-to-gate.
    * **Phase 3 — passives, then sources.** A 2-terminal *passive* (R/C/L) whose terminals sit in one
      column drops *into* that column (drawn vertically); one bridging two different columns is laid
      *between* them (drawn horizontally) — e.g. a Miller/feed-forward cap across two stage outputs.
      Independent **sources** (V/I) are instead parked in a stack at the **bottom-left**, just left of
      the floorplan and above the VSS rail (:meth:`_place_sources`): they connect to the circuit by net
      name only (the wiring layer draws no wire for them), so keeping the bias/test sources out of the
      signal path stops them cutting across the schematic.

    Output is deterministic (sorted iteration, fixed sweep count). The wiring layer guarantees no
    short regardless of coordinates, so placement only affects readability.
    """

    col_pitch: int = 340  # x-gap between two devices on a row (reserves the parameter-text lane)
    row_pitch: int = 260
    sweeps: int = 24  # barycentric relaxation passes (fixed for determinism)
    min_dx: int = 160  # absolute minimum x-gap, enforced last (incl. injected passives)
    _W_DS: float = 3.0  # pull from a shared drain/source net (vertical leg) — strong
    _W_GATE: float = 1.0  # pull from a shared gate net (horizontal mirror bus) — weak
    # Block-aware cohesion: extra inter-column pull between every two devices a detector flagged
    # as one functional block. Set above _W_GATE so a recognised mirror's reference + output columns
    # settle adjacent (tight annotation boxes) even when only a weak gate bus links them, yet below
    # _W_DS so it never reorders a genuine vertical current path. Applied only when hints are given.
    _W_BLOCK: float = 2.0
    # Parameter-text geometry, mirrored from emit/wiring so the column-spread can keep two devices'
    # w/l/model bands from overlapping (the symbol draws its text just outside the body, on the +x side,
    # flipped to −x by a device flip). Estimated from the device's own strings — conservative (raw,
    # un-abbreviated) so a lane is never under-sized.
    _SYM_HALF: int = 30  # half the device body width (gate at −20, drain/source/bulk at +20)
    _TEXT_X0: int = 22  # where the parameter text starts, just past the body
    _CHAR_W: int = 8  # drawn width of one attribute-text character
    _TEXT_CLEAR: int = 24  # clear gap kept between one device's text band and the next device

    def place(
        self,
        circuit: N2XCircuit,
        lib: SymLibrary | None = None,
        *,
        hints: PlacementHints | None = None,
    ) -> dict[str, Transform]:
        info = analyze(circuit)
        supply = info.vdd_nets | info.vss_nets
        mos = [d for d in circuit.devices if d.kind is DeviceKind.MOS]
        if not mos:  # nothing to lay out topologically — fall back to the plain grid
            return GridPlacer().place(circuit, lib)

        # Phase 1: row = discrete level. Phase 2: columns from vertical chains (see _chains).
        row = {d.ref: info.device_level[d.ref] for d in mos}
        # A differential pair tied at the source by a *current source* (not a MOS) shares a source net
        # with exactly two drain/source pins — which would otherwise read as a series link and collapse
        # the pair into one column. Exclude those source nets so the pair keeps its two legs.
        by_ref = {d.ref: d for d in mos}
        pair_src_nets = {
            s
            for a, b in info.pairs
            if (s := by_ref[a].nets.get("SOURCE")) is not None
            and s == by_ref[b].nets.get("SOURCE")
        }
        chain_of = self._chains(mos, supply, pair_src_nets, row)
        chains: dict[str, list[str]] = defaultdict(list)
        for d in mos:
            chains[chain_of[d.ref]].append(d.ref)

        # non-supply drain/source net -> the devices on it (the current path)
        ds_devs: dict[str, list[str]] = defaultdict(list)
        gate_devs: dict[str, list[str]] = defaultdict(list)
        for d in mos:
            for pin, net in d.nets.items():
                if net in supply:
                    continue
                if pin in ("DRAIN", "SOURCE"):
                    ds_devs[net].append(d.ref)
                elif pin == "GATE":
                    gate_devs[net].append(d.ref)

        # A *real column* is a vertical stack worth its own x: a multi-device chain, or a singleton
        # whose terminals don't hang off another column's node. A singleton that *does* tie a fan-out
        # node shared with another chain — a diff-pair input, a tail current sink, a mirror output leg —
        # is **interstitial**: it is dropped between the columns it bridges (at their centroid), never
        # given a column of its own. That keeps the two legs a diff pair feeds adjacent instead of being
        # shoved apart by the tail/bias devices that sit between and below them.
        def connected_cols(ref: str, real: set[str]) -> set[str]:
            cols: set[str] = set()
            for pin in ("DRAIN", "SOURCE"):
                net = by_ref[ref].nets.get(pin)
                if net is not None and net not in supply:
                    cols.update(chain_of[o] for o in ds_devs[net] if chain_of[o] in real)
            return cols - {chain_of[ref]}

        interstitial = {
            c
            for c, members in chains.items()
            if len(members) == 1 and connected_cols(members[0], set(chains) - {c})
        }
        real_chains = [c for c in chains if c not in interstitial] or list(chains)
        real_set = set(real_chains)

        weight: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

        def link(refs: list[str], w: float) -> None:
            for a in refs:
                for b in refs:
                    if a != b:
                        weight[a][b] += w

        for refs in ds_devs.values():
            link(refs, self._W_DS)
        for refs in gate_devs.values():
            link(refs, self._W_GATE)

        # Block-aware cohesion: pull the columns of one detected functional block together so its
        # annotation box stays tight and non-overlapping. Only the block's MOSFETs participate (passives
        # and sources are placed in later phases); weight between two members of the *same* column is a
        # no-op in the ordering, so this only ever orders columns *across* a block. Gated on hints — with
        # none, ``weight`` is exactly the ds/gate graph and the layout is byte-identical to before.
        clusters = hints.clusters if hints else ()
        cluster_of: dict[str, int] = {}
        for ci, members in enumerate(clusters):
            present = [r for r in members if r in chain_of]
            for r in present:
                cluster_of[r] = ci
            link(present, self._W_BLOCK)

        col_x = self._assign_columns(real_chains, chain_of, weight)  # real chain -> x
        x: dict[str, float] = {}
        for c in real_chains:
            for r in chains[c]:
                x[r] = col_x[c]

        def cluster_cols(ref: str) -> set[str]:
            """Real columns holding this device's block-mates — so a clustered interstitial whose only
            tie to its block is a gate bus (a current mirror's diode reference) drops *among its own
            block* rather than at the global centroid. Empty without hints, so the drop is unchanged."""
            ci = cluster_of.get(ref)
            if ci is None:
                return set()
            return {
                chain_of[o]
                for o in clusters[ci]
                if o != ref and o in chain_of and chain_of[o] in real_set
            } - {chain_of[ref]}

        for c in interstitial:  # drop each between the real columns it bridges (else among its block)
            r = chains[c][0]
            cols = connected_cols(r, real_set) or cluster_cols(r)
            x[r] = sum(col_x[c2] for c2 in cols) / len(cols) if cols else (
                sum(col_x.values()) / len(col_x) if col_x else 0.0
            )

        # Centre about x=0 on the differential pair's midpoint when there is one (so the input stage
        # sits in the middle and its two legs straddle centre — which is what lets _assign_gate_flips
        # mirror them); otherwise centre on the bounding box.
        if info.pairs:
            a, b = info.pairs[0]
            cx = (x[a] + x[b]) / 2.0
        else:
            cx = (min(x.values()) + max(x.values())) / 2.0
        out: dict[str, Transform] = {
            ref: Transform(x=snap(int(round(x[ref] - cx))), y=row[ref] * self.row_pitch)
            for ref in x
        }
        _assign_gate_flips(circuit, info, out)
        self._place_passives(circuit, info, out)
        # A multi-device chain is a column whose x must match across rows: pin its members as
        # immovable anchors so the overlap pass can't drift one off the stack.
        sizes = Counter(chain_of.values())
        anchored = frozenset(r for r in chain_of if sizes[chain_of[r]] >= 2)
        self._spread(out, anchored)
        # Open up any column gap too narrow for the two devices' parameter-text bands to clear (an
        # interstitial dropped a half-pitch from a column whose w/l/model text points at it). Runs after
        # the min-dx nudge so it can't pull a movable device back under a neighbour's text; whole columns
        # shift together, so chains stay straight and the floorplan only grows rightward.
        self._space_columns(circuit, out)
        # Finally, park the independent sources at the bottom-left, against the now-final floorplan (so
        # their placement can't perturb the signal-path columns). They wire by net name only.
        self._place_sources(circuit, out)
        return out

    @staticmethod
    def _chains(
        mos,
        supply: frozenset[str],
        exclude: frozenset[str] | set[str],
        level: dict[str, int],
    ) -> dict[str, str]:
        """Union MOSFETs into vertical **chains**: two devices are joined iff they share a non-supply
        drain/source net that has exactly **two** drain/source connections *and* the two devices sit on
        **different levels** — a true series node (one device's terminal feeding the next on the row
        below, the link of a cascode/output stack). A node with three or more drain/source pins (a
        diff-pair tail, an output summing node) is a fan-out, and two *same-level* devices on a 2-pin
        node are in **parallel** (e.g. an enable switch shunting a bias node) — neither is a series
        link, so the signal path never collapses into one column and two devices never land on one
        cell. Nets in ``exclude`` (e.g. a current-source-tailed diff pair's shared source) are never
        series links. Returns ``ref -> chain id`` (the chain's lexicographically smallest ref)."""
        refs = sorted(d.ref for d in mos)
        parent = {r: r for r in refs}

        def find(a: str) -> str:
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        ds_on: dict[str, list[str]] = defaultdict(list)
        for d in mos:
            for pin in ("DRAIN", "SOURCE"):
                net = d.nets.get(pin)
                if net is not None and net not in supply and net not in exclude:
                    ds_on[net].append(d.ref)
        for net in sorted(ds_on):
            on = ds_on[net]
            uniq = sorted(set(on))
            if len(on) == 2 and len(uniq) == 2 and level[uniq[0]] != level[uniq[1]]:
                parent[find(uniq[0])] = find(uniq[1])  # two distinct devices, different rows → series
        return {r: find(r) for r in refs}

    def _assign_columns(
        self,
        real_chains: list[str],
        chain_of: dict[str, str],
        weight: dict[str, dict[str, float]],
    ) -> dict[str, float]:
        """Order the **real columns** left-to-right by the barycentre heuristic; return ``chain -> x``.

        Each column repeatedly moves to the weighted-mean index of the columns it connects to (the
        *inter-column* neighbour weight: drain/source links strong, gate buses weak), so a mirror bank
        and the stacks it biases settle adjacent. Interstitial chains don't take part — their pull is
        what used to shove a diff pair's two legs apart — they're dropped in afterwards by the caller.
        Order is a bounded permutation, so this converges (no runaway like a free relaxation)."""
        real = set(real_chains)
        cw: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for a, nbrs in weight.items():
            ca = chain_of[a]
            if ca not in real:
                continue
            for b, w in nbrs.items():
                cb = chain_of[b]
                if cb in real and cb != ca:
                    cw[ca][cb] += w

        chain_ids = sorted(real_chains)
        pos = {c: i for i, c in enumerate(chain_ids)}
        for _ in range(self.sweeps):
            order = sorted(chain_ids, key=lambda c, p=pos: self._bary(c, cw, p))
            pos = {c: i for i, c in enumerate(order)}
        return {c: float(pos[c] * self.col_pitch) for c in chain_ids}

    @staticmethod
    def _bary(c: str, cw: dict[str, dict[str, float]], pos: dict[str, int]) -> tuple[float, int]:
        """A chain's barycentre key: the weighted-mean index of its inter-chain neighbours (ties and
        neighbourless chains keep their current index, so the ordering is stable and deterministic)."""
        nb = cw.get(c)
        if nb:
            return (sum(w * pos[d] for d, w in nb.items()) / sum(nb.values()), pos[c])
        return (float(pos[c]), pos[c])

    def _place_passives(
        self, circuit: N2XCircuit, info: TopologyInfo, out: dict[str, Transform]
    ) -> None:
        """Inject 2-terminal **passives** (R/C/L) after the MOS grid is fixed (sources are handled
        separately by :meth:`_place_sources`).

        A device's terminal "column" is the mean x of the MOSFETs that put a **drain/source** pin on
        that terminal's net — i.e. the *current-path* column, not the gate fan-out (a bias node gates a
        whole mirror bank, so averaging gate pins would land the device at a meaningless centroid and
        let it shove a leg off its column). With a single non-supply terminal (a cap to a rail) the
        device drops vertically into that column; with two non-supply terminals it is *inline*
        (vertical) when both resolve to the same column and *bridging* (horizontal, ``rot=1``) when
        they straddle two columns — the Miller/feed-forward case. Placed in sorted order so a later
        passive can stack beside an earlier one deterministically."""
        supply = info.vdd_nets | info.vss_nets
        xds_on_net: dict[str, list[int]] = defaultdict(list)  # drain/source columns (the current path)
        xany_on_net: dict[str, list[int]] = defaultdict(list)  # any pin (fallback for gate-only nets)
        for d in circuit.devices:
            if d.kind is DeviceKind.MOS and d.ref in out:
                for pin, net in d.nets.items():
                    xany_on_net[net].append(out[d.ref].x)
                    if pin in ("DRAIN", "SOURCE"):
                        xds_on_net[net].append(out[d.ref].x)
        fallback = int(round(sum(t.x for t in out.values()) / len(out))) if out else 0

        def net_x(net: str) -> int:
            xs = xds_on_net.get(net) or xany_on_net.get(net)
            return int(round(sum(xs) / len(xs))) if xs else fallback

        passives = [
            d for d in circuit.devices if d.kind is not DeviceKind.MOS and d.kind not in _SOURCE_KINDS
        ]
        for d in sorted(passives, key=lambda d: d.ref):
            nets = [n for n in d.nets.values() if n is not None]
            if not nets:
                continue
            free = [n for n in nets if n not in supply] or nets
            cols = sorted(net_x(n) for n in free)
            bridging = len(cols) >= 2 and (cols[-1] - cols[0]) > self.col_pitch
            px = (cols[0] + cols[-1]) // 2 if bridging else net_x(free[0])
            levels = [info.net_level[n] for n in nets if n in info.net_level]
            lvl = sum(levels) / len(levels) if levels else 0.0
            out[d.ref] = Transform(
                x=snap(px), y=snap(int(round(lvl * self.row_pitch))), rot=1 if bridging else 0
            )
            for n in nets:  # let a later passive on this net stack beside this one
                xds_on_net[n].append(out[d.ref].x)
                xany_on_net[n].append(out[d.ref].x)

    def _place_sources(self, circuit: N2XCircuit, out: dict[str, Transform]) -> None:
        """Park every independent source (V/I) in a stack at the **bottom-left** of the floorplan.

        Sources connect to the rest of the circuit by net name only — the wiring layer draws no wire for
        them — so their position is purely cosmetic; clustering them just left of the leftmost column,
        climbing up from the bottom row, keeps the bias/test sources out of the signal path instead of
        cutting across it. They sit above where the VSS rail lands (the rail clears every pin, sources
        included). Runs against the final MOS+passive floorplan, so it can't perturb the columns. Many
        sources wrap into further-left columns once a stack reaches the top of the floorplan."""
        sources = [d for d in circuit.devices if d.kind in _SOURCE_KINDS]
        if not sources or not out:
            return
        xs = [t.x for t in out.values()]
        ys = [t.y for t in out.values()]
        left, bottom, top = min(xs) - self.col_pitch, max(ys), min(ys)
        x, y = left, bottom
        for d in sorted(sources, key=lambda d: d.ref):
            if y < top:  # stack reached the top of the floorplan — wrap to a new column further left
                x -= self.col_pitch
                y = bottom
            out[d.ref] = Transform(x=snap(x), y=snap(y), rot=0, flip=0)
            y -= self.row_pitch

    def _text_reach(self, dev) -> int:
        """How far a device's parameter text reaches from its body, estimated from its own drawn
        strings (model + w/l/ng/m, or a passive's value). Conservative: uses the raw, un-abbreviated
        param values, so the reserved lane is never shorter than what emit actually draws."""
        if dev.kind is DeviceKind.MOS:
            params = {k.lower(): v for k, v in dev.params.items()}
            strings = [str(dev.model or "")]
            strings += [f"{k}={params[k]}" for k in ("w", "l", "ng", "m") if k in params]
        else:
            strings = [str(dev.model or "")]
        return self._TEXT_X0 + max((len(s) for s in strings), default=0) * self._CHAR_W

    def _space_columns(self, circuit: N2XCircuit, out: dict[str, Transform]) -> None:
        """Widen any inter-column gap too small for the two columns' facing parameter-text bands.

        A column's right edge reaches its text band when its devices face right (``flip==0``); its left
        edge when they face left (``flip==1``); otherwise just the body. For every pair of columns that
        share a row, the gap must clear the left column's right reach plus the right column's left reach.
        Columns are swept left-to-right and shifted **as a unit** (so a chain stays a straight stack),
        accumulating only rightward — original gaps are preserved wherever the text already fits, so a
        cleanly mirror-flipped layout (text pointing outward) is untouched."""
        reach = {d.ref: self._text_reach(d) for d in circuit.devices if d.ref in out}
        col: dict[int, dict[int, str]] = defaultdict(dict)  # x -> {row y: ref}
        for ref, t in out.items():
            col[t.x][t.y] = ref
        xs = sorted(col)
        if len(xs) < 2:
            return

        def right_reach(ref: str) -> int:  # how far the device extends to the +x side
            return reach[ref] if out[ref].flip == 0 else self._SYM_HALF

        def left_reach(ref: str) -> int:  # how far the device extends to the −x side
            return reach[ref] if out[ref].flip == 1 else self._SYM_HALF

        new_x = {xs[0]: xs[0]}
        for i in range(1, len(xs)):
            xi = xs[i]
            cand = xi + (new_x[xs[i - 1]] - xs[i - 1])  # default: preserve the original gap (carry shift)
            for j in range(i):
                shared = col[xs[j]].keys() & col[xi].keys()
                if not shared:
                    continue
                need = max(
                    right_reach(col[xs[j]][y]) + left_reach(col[xi][y]) + self._TEXT_CLEAR
                    for y in shared
                )
                cand = max(cand, new_x[xs[j]] + max(need, self.min_dx))
            new_x[xi] = cand

        for x, refs in col.items():
            dx = new_x[x] - x
            if dx:
                for ref in refs.values():
                    t = out[ref]
                    out[ref] = Transform(x=snap(t.x + dx), y=t.y, rot=t.rot, flip=t.flip)

    def _spread(self, out: dict[str, Transform], anchored: frozenset[str]) -> None:
        """Final overlap pass: enforce ``min_dx`` between devices on a row.

        **Chain members never move** — a multi-device chain is a column whose x must match across its
        rows, so its devices are fixed anchors here. Only *movable* devices (passives/sources and
        single-device chains) are nudged, each to the nearest x that clears ``min_dx`` from every
        already-fixed device on its row. So an injected source can't shove a leg off its column (the
        25-unit drift that used to break a stack)."""
        rows: dict[int, list[str]] = defaultdict(list)
        for ref, t in out.items():
            rows[t.y].append(ref)
        for y, refs in rows.items():
            taken = sorted(out[r].x for r in refs if r in anchored)
            for ref in sorted((r for r in refs if r not in anchored), key=lambda r: (out[r].x, r)):
                t = out[ref]
                nx = self._nearest_free(t.x, taken)
                taken = sorted([*taken, nx])
                out[ref] = Transform(x=snap(nx), y=y, rot=t.rot, flip=t.flip)

    def _nearest_free(self, want: int, taken: list[int]) -> int:
        """The x closest to ``want`` that is at least ``min_dx`` from every value in sorted ``taken``."""

        def clear(x: int) -> bool:
            return all(abs(x - t) >= self.min_dx for t in taken)

        if clear(want):
            return want
        for step in range(1, len(taken) + 2):  # widen the search symmetrically until a slot is free
            for cand in (want + step * self.min_dx, want - step * self.min_dx):
                if clear(cand):
                    return cand
        return want
