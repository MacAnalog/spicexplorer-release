"""Topology analysis + placement: symmetry detection and PMOS-top/NMOS-bottom ranking."""

from pathlib import Path

from spicexplorer_netlist2xschem import (
    GridPlacer,
    PhasedPlacer,
    TopologyPlacer,
    analyze,
    from_file,
)
from spicexplorer_netlist2xschem.ingest import DeviceKind, MosPolarity

FIXTURES = Path(__file__).parent / "fixtures"


def test_5t_analysis_pairs_ranks_sides():
    c = from_file(FIXTURES / "ota-5t_tb-ac.spice", into="xota")
    info = analyze(c)
    rank = {d.ref: info.device_rank[d.ref] for d in c.devices}
    pol = {d.ref: d.polarity for d in c.devices if d.kind is DeviceKind.MOS}

    # the differential pair is detected and split left/right
    assert info.pairs, "no differential pair detected"
    a, b = info.pairs[0]
    assert {info.side[a], info.side[b]} == {"L", "R"}

    # PMOS (toward VDD) ranks above every NMOS that ties to VSS — top-to-bottom current flow
    pmos = [r for r, p in pol.items() if p is MosPolarity.PMOS]
    nmos_tail = [
        d.ref
        for d in c.devices
        if d.kind is DeviceKind.MOS
        and d.polarity is MosPolarity.NMOS
        and d.nets["SOURCE"] in info.vss_nets
    ]
    if pmos and nmos_tail:
        assert max(rank[r] for r in pmos) < max(rank[r] for r in nmos_tail)


def test_topology_branch_columns_align_cascode_stack():
    """A cascode stack (devices linked drain↔source on one side) shares a single column."""
    c = from_file(FIXTURES / "folded_cascode.spice", into="XDUT")
    info = analyze(c)
    placement = TopologyPlacer().place(c)
    supply = info.vdd_nets | info.vss_nets

    def ds_nets(d):  # the non-supply drain/source nets that define a vertical branch
        return {d.nets.get("DRAIN"), d.nets.get("SOURCE")} - supply - {None}

    mos = [d for d in c.devices if d.kind is DeviceKind.MOS]
    branch_pairs = [
        (d.ref, e.ref)
        for d in mos
        for e in mos
        if d.ref < e.ref
        and info.side.get(d.ref) == info.side.get(e.ref)
        and ds_nets(d) & ds_nets(e)
    ]
    aligned = [(d, e) for d, e in branch_pairs if placement[d].x == placement[e].x]
    assert aligned, "no cascode branch ended up column-aligned"


def test_topology_diff_pair_split_and_mirrored():
    """The diff pair occupies two columns and is drawn mirror-imaged (right half flipped)."""
    c = from_file(FIXTURES / "ota-improved.spice")
    info = analyze(c)
    placement = TopologyPlacer().place(c)
    a, b = info.pairs[0]
    assert placement[a].x != placement[b].x, "diff pair not split into two columns"
    assert placement[a].flip != placement[b].flip, "diff pair not mirrored"


def test_grid_and_topology_place_all_devices():
    c = from_file(FIXTURES / "ota-improved.spice")
    for placer in (GridPlacer(), TopologyPlacer()):
        placement = placer.place(c)
        assert set(placement) == {d.ref for d in c.devices}


def test_ports_detected_with_directions():
    """The 5T's external nets are classified as ports: gate-driven → input, drain → output."""
    c = from_file(FIXTURES / "ota-5t_tb-ac.spice", into="xota")
    info = analyze(c)
    assert info.port_role.get("vinp") == "in"  # a gate-only net is an input
    assert info.port_role.get("vinn") == "in"
    assert info.port_role.get("vout") == "out"  # a net on a drain is an output
    assert "vdd" not in info.port_role and "vss" not in info.port_role  # rails aren't ports


def test_gate_share_pairs_face_gate_to_gate():
    """Mirror/cascode gate buses are detected, and a shared-gate pair is flipped to face gate-to-gate.

    The gate sits on a MOS symbol's left edge, so ``flip=1`` points it right. For a pair in different
    columns the left device's gate should point right (toward its mate) and the right device's left.
    """
    c = from_file(FIXTURES / "ota-improved.spice")
    info = analyze(c)
    assert info.gate_share_pairs, "no gate-sharing devices detected"
    placement = TopologyPlacer().place(c)

    def gate_right(ref: str) -> bool:  # flip=1 puts the gate on the +x side
        return placement[ref].flip == 1

    faced = 0
    for a, b in info.gate_share_pairs:
        xa, xb = placement[a].x, placement[b].x
        if xa == xb:
            continue  # same column: the gate net runs along the column, not across a gap
        lo, hi = (a, b) if xa < xb else (b, a)
        if gate_right(lo) and not gate_right(hi):  # left gate points right, right gate points left
            faced += 1
    assert faced, "no gate-sharing pair ended up facing gate-to-gate"


def test_diode_connected_detected():
    """A diode-connected MOSFET (gate net == drain net) is detected as a current-mirror reference."""
    c = from_file(FIXTURES / "folded_cascode.spice", into="XDUT")
    info = analyze(c)
    by_ref = {d.ref: d for d in c.devices}
    assert info.diode_refs, "no diode-connected device detected"
    for ref in info.diode_refs:  # every flagged device really is gate==drain
        assert by_ref[ref].nets["GATE"] == by_ref[ref].nets["DRAIN"]
    # XM11 (ibias ibias vdd vdd) and XM13 (nbias nbias vss vss) are the diode references here.
    assert {"XM11", "XM13"} <= info.diode_refs


# --------------------------------------------------------------------- PhasedPlacer (default)


def test_phased_places_all_devices():
    c = from_file(FIXTURES / "ota-improved.spice")
    placement = PhasedPlacer().place(c)
    assert set(placement) == {d.ref for d in c.devices}


def test_phased_diff_pair_split_and_mirrored():
    """The default placer splits the diff pair into two columns and mirrors them about centre."""
    c = from_file(FIXTURES / "ota-improved.spice")
    info = analyze(c)
    placement = PhasedPlacer().place(c)
    a, b = info.pairs[0]
    assert placement[a].x != placement[b].x, "diff pair not split into two columns"
    assert placement[a].flip != placement[b].flip, "diff pair not mirrored"


def test_phased_levels_are_compact_and_rail_ordered():
    """Discrete levels collapse a circuit to a few rows (one per current-path layer), with a
    VDD-sourced PMOS strictly above a VSS-sourced device — top-to-bottom current flow."""
    c = from_file(FIXTURES / "folded_cascode.spice", into="XDUT")
    info = analyze(c)
    levels = {d.ref: info.device_level[d.ref] for d in c.devices}
    # far fewer rows than devices (the sprawl cure): a ~16-device amp lands in a handful of rows.
    assert max(levels.values()) - min(levels.values()) + 1 <= 6
    pmos_top = [
        d.ref
        for d in c.devices
        if d.kind is DeviceKind.MOS
        and d.polarity is MosPolarity.PMOS
        and d.nets["SOURCE"] in info.vdd_nets
    ]
    nmos_bot = [
        d.ref
        for d in c.devices
        if d.kind is DeviceKind.MOS
        and d.polarity is MosPolarity.NMOS
        and d.nets["SOURCE"] in info.vss_nets
    ]
    if pmos_top and nmos_bot:
        assert max(levels[r] for r in pmos_top) < max(levels[r] for r in nmos_bot)


def test_phased_vss_tied_diode_ref_sits_low():
    """Regression: a diode-connected mirror reference whose source is VSS (its drain a bias node not
    reachable from VDD) must land below the VDD rail devices, not default to the top row."""
    c = from_file(FIXTURES / "folded_cascode.spice", into="XDUT")
    info = analyze(c)
    # XM13 (nbias nbias vss vss) is the VSS-tied NMOS diode reference; XM11 (ibias ibias vdd vdd) the
    # VDD-tied PMOS one. The NMOS ref must sit strictly below the PMOS ref.
    assert info.device_level["XM13"] > info.device_level["XM11"]


def test_phased_chains_are_vertically_aligned():
    """A vertical chain (MOSFETs linked drain↔source through a true series node) draws as one
    straight column: every member shares a single x. This is the core fix for the zig-zag legs."""
    placer = PhasedPlacer()
    for fixture, kw in (
        ("ota-improved.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
    ):
        circuit = from_file(FIXTURES / fixture, **kw)
        info = analyze(circuit)
        supply = info.vdd_nets | info.vss_nets
        mos = [d for d in circuit.devices if d.kind is DeviceKind.MOS]
        by_ref = {d.ref: d for d in mos}
        pair_src = frozenset(  # same exclusion place() uses: a current-source-tailed pair's source
            s
            for a, b in info.pairs
            if (s := by_ref[a].nets.get("SOURCE")) is not None
            and s == by_ref[b].nets.get("SOURCE")
        )
        level = {d.ref: info.device_level[d.ref] for d in mos}
        chain_of = PhasedPlacer._chains(mos, supply, pair_src, level)
        chains: dict[str, list[str]] = {}
        for r, c in chain_of.items():
            chains.setdefault(c, []).append(r)
        placement = placer.place(circuit)
        for members in chains.values():
            if len(members) >= 2:  # a real stack — its devices must line up in one column
                xs = {placement[r].x for r in members}
                assert len(xs) == 1, f"{fixture}: chain {sorted(members)} split across columns {xs}"


def test_phased_text_bands_do_not_overlap():
    """No two devices on a row sit so close their parameter-text bands collide. The symbol draws its
    w/l/model text just outside the body on the +x side (−x when flipped); the column-spread pass opens
    any gap narrower than the two facing reaches — the fix for an interstitial dropped a half-pitch from
    a column whose text points straight at it (M0 vs M10 in the folded cascode)."""
    placer = PhasedPlacer()
    for fixture, kw in (
        ("ota-improved.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
        ("ota-5t_tb-ac.spice", {"into": "xota"}),
    ):
        circuit = from_file(FIXTURES / fixture, **kw)
        placement = placer.place(circuit)
        reach = {d.ref: placer._text_reach(d) for d in circuit.devices if d.ref in placement}
        rows: dict[int, list[str]] = {}
        for ref, t in placement.items():
            rows.setdefault(t.y, []).append(ref)
        for refs in rows.values():
            refs.sort(key=lambda r: placement[r].x)
            for a, b in zip(refs, refs[1:]):
                ta, tb = placement[a], placement[b]
                right = reach[a] if ta.flip == 0 else placer._SYM_HALF  # a's reach toward b
                left = reach[b] if tb.flip == 1 else placer._SYM_HALF  # b's reach toward a
                assert tb.x - ta.x >= right + left, (
                    f"{fixture}: {a}@{ta.x} and {b}@{tb.x} text bands overlap"
                )


def test_phased_sources_parked_bottom_left():
    """Independent V/I sources stack at the bottom-left, out of the signal path: every source sits
    strictly left of the rest of the floorplan, and the stack is anchored at its very bottom row (so
    the sources land above where the VSS rail goes — the rail always clears the lowest pin). They wire
    by net name only (see test_emit)."""
    placer = PhasedPlacer()
    for fixture, kw in (
        ("mixed_devices.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
        ("ota-improved.spice", {}),
    ):
        circuit = from_file(FIXTURES / fixture, **kw)
        placement = placer.place(circuit)
        kind = {d.ref: d.kind for d in circuit.devices}
        sources = {r for r in placement if kind[r] in (DeviceKind.VSOURCE, DeviceKind.ISOURCE)}
        others = [r for r in placement if r not in sources]
        assert sources, f"{fixture}: expected at least one source"
        assert others, f"{fixture}: expected some non-source devices"
        assert max(placement[s].x for s in sources) < min(placement[r].x for r in others), (
            f"{fixture}: sources are not left of the rest of the floorplan"
        )
        assert max(placement[s].y for s in sources) == max(placement[r].y for r in placement), (
            f"{fixture}: the source stack is not anchored at the bottom row"
        )


def test_phased_width_is_bounded():
    """The floorplan can't run away: total x-span stays within a column pitch per device (the guard
    the rigid-coordinate pass used to need, now intrinsic to the discrete column ordering)."""
    placer = PhasedPlacer()
    for fixture, kw in (
        ("ota-improved.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
    ):
        placement = placer.place(from_file(FIXTURES / fixture, **kw))
        xs = [t.x for t in placement.values()]
        assert max(xs) - min(xs) <= len(placement) * placer.col_pitch


# ------------------------------------------------------------------- block-aware placement hints


def test_phased_no_hints_is_byte_identical_to_empty_hints():
    """The block-aware hook is inert without hints: ``place(c)``, ``place(c, hints=None)`` and
    ``place(c, hints=PlacementHints())`` (no clusters) all produce the identical placement — so the
    no-annotation path is unchanged (the byte-stable layout the rest of the suite locks)."""
    from spicexplorer_netlist2xschem import PlacementHints

    placer = PhasedPlacer()
    for fixture, kw in (
        ("ota-improved.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
        ("ota-5t_tb-ac.spice", {"into": "xota"}),
    ):
        c = from_file(FIXTURES / fixture, **kw)
        base = placer.place(c)
        assert placer.place(c, hints=None) == base
        assert placer.place(c, hints=PlacementHints()) == base
        assert placer.place(c, hints=PlacementHints(clusters=())) == base


def test_phased_cluster_hint_keeps_block_no_more_scattered():
    """A cluster hint never *increases* a block's footprint: clustering the two members of a real
    same-gate mirror pair leaves their column gap ≤ the un-hinted gap (it pulls them together, or, if
    the topology already had them adjacent, leaves them put)."""
    from spicexplorer_netlist2xschem import PlacementHints

    placer = PhasedPlacer()
    c = from_file(FIXTURES / "folded_cascode.spice", into="XDUT")
    base = placer.place(c)
    # XM11 / XM13 are the two diode references (different rails); cluster them and confirm the hint
    # does not push them farther apart than the block-agnostic layout did.
    pair = ("XM11", "XM13")
    assert {*pair} <= set(base), "expected the known diode refs in the fixture"
    hinted = placer.place(c, hints=PlacementHints(clusters=(pair,)))
    assert abs(hinted[pair[0]].x - hinted[pair[1]].x) <= abs(base[pair[0]].x - base[pair[1]].x)


def test_place_with_hints_tolerates_a_legacy_two_arg_placer():
    """``place_with_hints`` lets ``build_sch`` drive a placer that predates the ``hints`` keyword: it
    inspects the signature and falls back to the 2-arg call instead of raising ``TypeError``."""
    from spicexplorer_netlist2xschem import PlacementHints
    from spicexplorer_netlist2xschem.geometry import Transform
    from spicexplorer_netlist2xschem.placement import place_with_hints

    class LegacyPlacer:  # only the old 2-arg protocol — no `hints` (intentionally non-conforming)
        def place(self, circuit, lib=None):  # noqa: ARG002
            return {d.ref: Transform(x=0, y=0) for d in circuit.devices}

    c = from_file(FIXTURES / "ota-improved.spice")
    hints = PlacementHints(clusters=(("XM1", "XM2"),))
    out = place_with_hints(LegacyPlacer(), c, None, hints)  # type: ignore[arg-type]  # must not raise
    assert set(out) == {d.ref for d in c.devices}
