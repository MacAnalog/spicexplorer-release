"""Channel routing of a block-diagram sheet (issue #243).

The fixture is a synthetic top level, ``fixtures/blockdiag/blockdiag_top.spice``: 40 instances of
nine generic cells (``blk_a`` … ``blk_i``, each a placeholder resistor), every cell drawn with a
generated block symbol (inputs left, outputs right, ``vdd`` on top, ``vss`` at the bottom), laid on
a hand floorplan of 5 rows × 8 columns at a 360-unit pitch. On it the per-route planner leaves 26
of the 43 multi-pin signal nets in more than one drawn piece (``rst`` in 18) and ``vdd``/``vss`` in
33 pieces each: every inner-row tap to the sheet-wide rail runs through the supply pin of the block
above or below it and is refused. Those are the numbers these tests hold the channel router to.

Channel routing is a helper the caller asks for (``router="channel"``); the default is the
per-route planner, and the tests that measure both call the default by leaving ``router`` out.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    BlockPin,
    PhasedPlacer,
    RouterMode,
    SymLibrary,
    analyze,
    build_sch,
    from_file,
    from_string,
    generate_block_symbol,
    plan_connections,
    wiring,
)
from spicexplorer_netlist2xschem.channels import (
    LANE_MARGIN,
    LANE_PITCH,
    ChannelRoute,
    DevicePins,
    block_grid,
    channel_deficits,
    channel_layout,
)
from spicexplorer_netlist2xschem.geometry import Transform, apply_transform
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity, N2XCircuit
from spicexplorer_netlist2xschem.mapping import align_pins, register_subckt_symbol, symref_for
from spicexplorer_netlist2xschem.sym_library import default_search_paths, parse_symbol
from spicexplorer_netlist2xschem.wiring import (
    ConnectionPlan,
    PlacedDevice,
    _device_pins,
    _wire_components,
    device_extent,
    spread_channels,
)
from test_wiring_drawn_connectivity import (
    _assert_no_short,
    _floating_runs,
    _unnamed_islands,
)

FIXTURES = Path(__file__).parent / "fixtures"
BLOCKDIAG = FIXTURES / "blockdiag"
PDK = "blockdiag-fixture"  # a token of its own: the subckt symbol table is module-global
CELLS = [f"blk_{c}" for c in "abcdefghi"]
for _cell in CELLS:
    register_subckt_symbol(PDK, _cell, f"blockdiag/{_cell}.sym")

Point = tuple[int, int]


@dataclass
class FixedPlacer:
    """A hand floorplan: the exact transform per instance."""

    at: dict[str, Transform]

    def place(self, circuit, lib=None, *, hints=None) -> dict[str, Transform]:  # noqa: ARG002
        return dict(self.at)


@pytest.fixture
def lib() -> SymLibrary:
    return SymLibrary([FIXTURES / "sym", FIXTURES])


def _top() -> N2XCircuit:
    return from_file(BLOCKDIAG / "blockdiag_top.spice", into="xtop", name="blockdiag_top")


def _grid_at(circuit: N2XCircuit, pitch: int = 360, cols: int = 8) -> dict[str, Transform]:
    refs = sorted(d.ref for d in circuit.devices)
    return {r: Transform((i % cols) * pitch, (i // cols) * pitch) for i, r in enumerate(refs)}


def _placed(
    circuit: N2XCircuit, lib: SymLibrary, at: dict[str, Transform], *, blocks: bool = True
) -> list[PlacedDevice]:
    """The instances as ``build_sch`` hands them to the planner; ``blocks=False`` is how it hands
    them over when channel routing is not asked for (no block flag, no block body)."""
    out = []
    for d in circuit.devices:
        sym = lib.load(symref_for(d, pdk=PDK) or "")
        assert sym is not None, d.ref
        out.append(
            PlacedDevice(
                ref=d.ref,
                transform=at[d.ref],
                nets=d.nets,
                aligned=align_pins(d, sym),
                is_block=blocks,
                body=sym.bbox if blocks else None,
            )
        )
    return out


def _plan(
    circuit: N2XCircuit, placed: list[PlacedDevice], router: RouterMode | None = "channel"
) -> ConnectionPlan:
    """Plan the wires; ``router=None`` leaves the argument out, which is the default planner."""
    port_role = analyze(circuit).port_role
    if router is None:
        return plan_connections(placed, supply=circuit.supply, port_role=port_role)
    return plan_connections(placed, supply=circuit.supply, port_role=port_role, router=router)


def _pins_by_net(placed: list[PlacedDevice]) -> dict[str, list[Point]]:
    out: dict[str, list[Point]] = {}
    for pd in placed:
        for canon, sp in pd.aligned.items():
            out.setdefault(pd.nets[canon], []).append(apply_transform(pd.transform, sp.x, sp.y))
    return out


def _islands(placed: list[PlacedDevice], plan: ConnectionPlan) -> dict[str, int]:
    """Drawn pieces per multi-pin net: its pins' connected components over the drawn wires."""
    return {
        net: len(_wire_components(sorted(set(pts)), plan.wires))
        for net, pts in _pins_by_net(placed).items()
        if len(set(pts)) > 1
    }


def _routed_top(lib: SymLibrary, pitch: int = 360):
    circuit = _top()
    placed = spread_channels(_placed(circuit, lib, _grid_at(circuit, pitch)), supply=circuit.supply)
    return circuit, placed, _plan(circuit, placed)


# ------------------------------------------------------------------ the fixture's own shape


def test_the_fixture_is_the_shape_the_issue_measured():
    """40 instances of 9 generic cells, a clock and a reset fanning out to most of them."""
    circuit = _top()
    assert len(circuit.devices) == 40
    assert {d.model for d in circuit.devices} == set(CELLS)
    fanout = {n: sum(n in d.nets.values() for d in circuit.devices) for n in ("clk", "rst")}
    assert fanout == {"clk": 21, "rst": 19}
    assert circuit.supply == {"vdd": "VDD", "vss": "VSS"}


def test_the_committed_symbols_are_what_the_generator_writes():
    """The nine ``.sym`` files are generated, never hand-edited: regenerate and compare."""
    for cell in CELLS:
        sym = parse_symbol((BLOCKDIAG / f"{cell}.sym").read_text())
        pins = [BlockPin(p.name, _side(p)) for p in sym.pins]
        assert generate_block_symbol(cell, pins).text == (BLOCKDIAG / f"{cell}.sym").read_text()


def _side(p) -> str:
    if abs(p.x) >= abs(p.y):
        return "left" if p.x < 0 else "right"
    return "top" if p.y < 0 else "bottom"


# ---------------------------------------------------------------- acceptance on the fixture


def test_each_supply_is_one_drawn_rail_group(lib):
    """Step 3: ``vdd``/``vss`` were 33 pieces each (one stub per block); now one piece each."""
    circuit, placed, plan = _routed_top(lib)
    islands = _islands(placed, plan)
    assert (islands["vdd"], islands["vss"]) == (1, 1)
    assert plan.router == "channel"


def test_no_signal_net_is_left_in_pieces(lib):
    """Steps 1–2: 26 of 43 signal nets were split (``rst`` in 18 pieces); now none is."""
    circuit, placed, plan = _routed_top(lib)
    split = {n: k for n, k in _islands(placed, plan).items() if k > 1}
    assert split == {}
    assert plan.by_name == [] and plan.parked_ports == []


def test_the_emitted_document_reports_the_by_name_count(lib):
    """Step 4: what a caller reads without touching the plan — the count, and which router ran."""
    circuit = _top()
    placer = FixedPlacer(_grid_at(circuit))
    doc = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, router="channel")
    assert doc.router == "channel"
    assert doc.nets_by_name == () and doc.parked_ports == ()
    default = build_sch(circuit, pdk=PDK, lib=lib, placer=placer)
    assert default.router == "per-route" and len(default.nets_by_name) == 28
    labels = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, wiring="labels")
    assert labels.router == "labels" and len(labels.nets_by_name) == 45


def test_channel_routing_is_off_by_default(lib):
    """Not asked for, no channel layout is computed, no block is moved and no block body is used:
    ``build_sch`` hands the planner the devices with no block flag, so the default document is the
    ``router="per-route"`` one, and ``plan_connections`` with no ``router`` stays per-route even on
    devices flagged as blocks."""
    circuit = _top()
    placer = FixedPlacer(_grid_at(circuit))
    default = build_sch(circuit, pdk=PDK, lib=lib, placer=placer)
    asked = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, router="per-route")
    assert (default.text, default.router) == (asked.text, "per-route")
    plan = _plan(circuit, _placed(circuit, lib, _grid_at(circuit)), router=None)
    assert (plan.router, plan.lanes) == ("per-route", {})


def test_the_labels_mode_moves_no_block_even_with_channels_asked_for(lib):
    """The labels mode draws no wire, so there is no lane to make room for: at pitch 240, where
    channel routing moves the blocks up to 635 x 400 units, every block stays where it was placed."""
    circuit = _top()
    placer = FixedPlacer(_grid_at(circuit, 240))

    def instances(text: str) -> list[str]:
        return [ln for ln in text.splitlines() if ln.startswith("C {blockdiag/")]

    plain = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, wiring="labels")
    asked = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, wiring="labels", router="channel")
    assert len(instances(plain.text)) == 40
    assert instances(asked.text) == instances(plain.text)
    assert asked.router == "labels"
    routed = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, router="channel")
    assert instances(routed.text) != instances(plain.text)  # the hybrid wiring does move them


@pytest.mark.parametrize("router", ["channels", "", "Channel"])
def test_an_unknown_router_is_refused(lib, router):
    """A misspelt router name is an error, not a silent fall-back to the default."""
    circuit = _array(2)
    placed = _placed(circuit, lib, {"XB0": Transform(0, 0), "XB1": Transform(360, 0)})
    with pytest.raises(ValueError, match="router must be one of per-route, channel"):
        _plan(circuit, placed, router=router)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="router must be one of"):
        build_sch(circuit, pdk=PDK, lib=lib, router=router)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="router must be one of"):  # labels mode plans no wires
        build_sch(circuit, pdk=PDK, lib=lib, router=router, wiring="labels")  # type: ignore[arg-type]


#: The 40-block fixture as each router draws it, per floorplan (a hand grid at a pitch, or the
#: default placer: GridPlacer, 7 blocks to a row at a 240 pitch, refs in order). Columns: signal
#: nets drawn in more than one piece, (vdd, vss) drawn pieces, nets by name, parked port pins,
#: and how far ``build_sch`` moved the blocks apart to fit the lanes (max dx, max dy). The
#: default-router rows are the numbers issue #243 reports; they are also the base's, since the
#: default draws every sheet byte for byte as the base did (``test_default_output.py``).
FIXTURE_AS_DRAWN = [
    (240, None, 38, (33, 33), 41, ["dout"], (0, 0)),
    (240, "channel", 0, (1, 1), 0, [], (635, 400)),
    (300, None, 26, (33, 33), 28, [], (0, 0)),
    (300, "channel", 0, (1, 1), 0, [], (215, 160)),
    (360, None, 26, (33, 33), 28, [], (0, 0)),
    (360, "channel", 0, (1, 1), 0, [], (0, 25)),
    (500, None, 26, (33, 33), 28, [], (0, 0)),
    (500, "channel", 0, (1, 1), 0, [], (0, 0)),
    ("default placer", None, 32, (34, 34), 35, ["dout"], (0, 0)),
    ("default placer", "channel", 0, (1, 1), 0, [], (630, 525)),
]


@pytest.mark.parametrize(
    ("placement", "router", "split", "supplies", "named", "parked", "moved"), FIXTURE_AS_DRAWN
)
def test_the_fixture_as_each_router_draws_it(
    lib, placement, router, split, supplies, named, parked, moved
):
    """At 240 the gaps are 36 units (room for no lane): asked for channels, the blocks are moved
    apart first. The per-route planner splits ``rst`` into 18 pieces on every floorplan."""
    circuit = _top()
    at = (
        PhasedPlacer().place(circuit, lib)
        if placement == "default placer"
        else _grid_at(circuit, placement)
    )
    placed = _placed(circuit, lib, at, blocks=router == "channel")
    if router == "channel":
        placed = spread_channels(placed, supply=circuit.supply)
    plan = _plan(circuit, placed, router)
    islands = _islands(placed, plan)
    pieces = {n: k for n, k in islands.items() if k > 1 and n not in ("vdd", "vss")}
    assert len(pieces) == split
    if router is None:
        assert pieces["rst"] == 18
    assert (islands["vdd"], islands["vss"]) == supplies
    assert (len(plan.by_name), plan.parked_ports) == (named, parked)
    shift = [(b.transform.x - at[b.ref].x, b.transform.y - at[b.ref].y) for b in placed]
    assert (max(dx for dx, _ in shift), max(dy for _, dy in shift)) == moved
    # build_sch reports the same: it places, moves and plans the way this test does
    placer = None if placement == "default placer" else FixedPlacer(at)
    doc = (
        build_sch(circuit, pdk=PDK, lib=lib, placer=placer)
        if router is None
        else build_sch(circuit, pdk=PDK, lib=lib, placer=placer, router=router)
    )
    assert (doc.router, doc.nets_by_name) == (plan.router, tuple(plan.by_name))


@pytest.mark.parametrize(
    ("router", "extent", "labels"), [(None, (2930, 1860), 165), ("channel", (2904, 1730), 40)]
)
def test_the_drawn_sheet_at_360_as_each_router_draws_it(lib, router, extent, labels):
    """Read off the written sheet: the wire records' extent (x by y) and the net-name labels."""
    circuit = _top()
    kw = {} if router is None else {"router": router}
    text = build_sch(circuit, pdk=PDK, lib=lib, placer=FixedPlacer(_grid_at(circuit)), **kw).text
    wires = [[int(float(v)) for v in ln.split()[1:5]] for ln in text.splitlines() if ln[:2] == "N "]
    xs = [v for w in wires for v in (w[0], w[2])]
    ys = [v for w in wires for v in (w[1], w[3])]
    assert (max(xs) - min(xs), max(ys) - min(ys)) == extent
    assert sum("lab_wire.sym" in ln for ln in text.splitlines()) == labels


def test_the_channel_routed_sheet_is_connectivity_safe(lib):
    circuit, placed, plan = _routed_top(lib)
    _assert_no_short(placed, plan)
    assert _floating_runs(placed, plan) == []
    assert _unnamed_islands(placed, plan) == 0


@pytest.mark.parametrize("router", ["per-route", "channel"])
def test_the_output_is_deterministic(lib, router):
    circuit = _top()
    placer = FixedPlacer(_grid_at(circuit))
    texts = {
        build_sch(circuit, pdk=PDK, lib=lib, placer=placer, router=router).text for _ in range(2)
    }
    assert len(texts) == 1


def test_no_wire_crosses_a_block_body(lib):
    """The per-route planner ran row runs straight through the blocks; a lane stays in its channel.

    The body is the drawn rectangle: the symbol's extent less the 20-unit pin stubs and the
    2.5-unit pin boxes around it, so a tap leaving a pin outward does not count as a crossing.
    """
    circuit, placed, plan = _routed_top(lib)
    inset = 25
    bodies = [
        (x0 + inset, y0 + inset, x1 - inset, y1 - inset)
        for x0, y0, x1, y1 in (device_extent(pd) for pd in placed)
    ]
    for w in plan.wires:
        lo_x, hi_x = sorted((w.x1, w.x2))
        lo_y, hi_y = sorted((w.y1, w.y2))
        for x0, y0, x1, y1 in bodies:
            assert not (lo_x < x1 and hi_x > x0 and lo_y < y1 and hi_y > y0), (
                f"{w} crosses the body {(x0, y0, x1, y1)}"
            )


def test_each_row_has_its_own_rails_and_the_spines_sit_at_the_two_sides(lib):
    """One vdd rail above each of the 5 rows and one vss rail below, joined at the left / right."""
    circuit, placed, plan = _routed_top(lib)
    lefts = min(w.x1 for w in plan.wires)
    rights = max(w.x2 for w in plan.wires)
    vdd_pins = _pins_by_net(placed)["vdd"]
    vss_pins = _pins_by_net(placed)["vss"]
    spine_l = [w for w in plan.wires if w.x1 == w.x2 == lefts]
    spine_r = [w for w in plan.wires if w.x1 == w.x2 == rights]
    assert spine_l and spine_r
    # the leftmost column of wire is vdd's, the rightmost vss's
    pieces = _wire_components(sorted({*vdd_pins, (lefts, spine_l[0].y1)}), plan.wires)
    assert len(pieces) == 1
    pieces = _wire_components(sorted({*vss_pins, (rights, spine_r[0].y1)}), plan.wires)
    assert len(pieces) == 1
    for net, pins, up in (("vdd", vdd_pins, True), ("vss", vss_pins, False)):
        rails = set()
        for px, py in pins:  # every supply pin has its own tap: a vertical wire off the pin
            (tap,) = [
                w
                for w in plan.wires
                if w.x1 == w.x2 == px
                and (py in (w.y1, w.y2))
                and (min(w.y1, w.y2) < py if up else max(w.y1, w.y2) > py)
            ]
            rails.add(min(tap.y1, tap.y2) if up else max(tap.y1, tap.y2))
        assert len(rails) == 5, (net, sorted(rails))  # one rail per block row


@pytest.mark.skipif(shutil.which("xschem") is None, reason="xschem is not on PATH")
@pytest.mark.parametrize("router", ["per-route", "channel"])
def test_the_sheet_renetlists_to_the_top_level_it_was_drawn_from(lib, tmp_path, router):
    """Real xschem netlists either router's sheet back to the same 227 terminals and 46 nets."""
    circuit = _top()
    placer = FixedPlacer(_grid_at(circuit))
    doc = build_sch(circuit, pdk=PDK, lib=lib, placer=placer, router=router)
    assert doc.router == router
    text = _xschem_netlist(doc.text, tmp_path)
    cells = _cell_definitions()
    body = [ln for ln in text.splitlines() if ln[:1] in "xX"]
    back = from_string("* back\n" + "\n".join([*cells, *body]) + "\n.end\n", name="back")

    def terminals(c: N2XCircuit) -> dict[tuple[str, str], str]:
        return {(d.ref.upper(), pin): net for d in c.devices for pin, net in d.nets.items()}

    before, after = terminals(circuit), terminals(back)
    assert set(before) == set(after) and len(before) == 227
    forward: dict[str, str] = {}
    backward: dict[str, str] = {}
    for key in sorted(before):
        was, now = before[key], after[key]
        assert forward.setdefault(was, now) == now, f"{key}: net {was} split into {now}"
        assert backward.setdefault(now, was) == was, f"{key}: nets {was} and {backward[now]} merged"
    assert len(forward) == 46


def _cell_definitions() -> list[str]:
    out, keep = [], False
    for ln in (BLOCKDIAG / "blockdiag_top.spice").read_text().splitlines():
        keep = keep or ln.startswith(".subckt blk_")
        if keep:
            out.append(ln)
        if ln.startswith(".ends blk_"):
            keep = False
    return out


def _xschem_netlist(sch_text: str, tmp_path: Path) -> str:
    from spicexplorer_netlist2xschem.render import write_xschemrc

    work = tmp_path / "blockdiag_top"
    (work / "blockdiag").mkdir(parents=True)
    for sym in BLOCKDIAG.glob("*.sym"):
        shutil.copy(sym, work / "blockdiag" / sym.name)
    source = work / "blockdiag_top.sch"
    source.write_text(sch_text)
    entries = [str(FIXTURES / "sym"), str(FIXTURES / "sym" / "devices")]
    for root in default_search_paths():
        entries.append(str(root))
        if (root / "devices").is_dir():
            entries.append(str(root / "devices"))
    library_path = os.pathsep.join(dict.fromkeys(entries))
    rc = write_xschemrc(work, library_path)
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-n", "-q", "-x", "-o", str(work), str(source)],
        env=dict(os.environ, XSCHEM_LIBRARY_PATH=library_path),
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(work),
    )
    out = work / "blockdiag_top.spice"
    assert out.is_file(), "xschem produced no netlist"
    return out.read_text()


# ----------------------------------------------------------------- small block sheets


def _array(n: int) -> N2XCircuit:
    """``n`` bit cells in a row: shared clk/rst/vdd/vss, each cell's output the next one's input."""
    devs = [
        Device(
            ref=f"XB{i}",
            kind=DeviceKind.SUBCKT,
            model="blk_a",
            polarity=MosPolarity.UNKNOWN,
            pins=("clk", "rst", "vin", "q", "vdd", "vss"),
            nets={
                "clk": "clk",
                "rst": "rst",
                "vin": f"n{i}",
                "q": f"n{i + 1}",
                "vdd": "vdd",
                "vss": "vss",
            },
            params={},
        )
        for i in range(n)
    ]
    nets = sorted({v for d in devs for v in d.nets.values()})
    return N2XCircuit("array", tuple(devs), tuple(nets), {"vdd": "VDD", "vss": "VSS"})


@pytest.mark.parametrize("n", [2, 7])
def test_a_small_block_array_is_drawn_entirely_by_wire(lib, n):
    """The 7-cell array (and a 2-cell one) through the channel router: nothing is left by name.
    The default planner leaves ``rst`` to its name on both."""
    circuit = _array(n)
    at = {d.ref: Transform(i * 360, 0) for i, d in enumerate(circuit.devices)}
    default = _plan(circuit, _placed(circuit, lib, at, blocks=False), router=None)
    assert (default.router, default.by_name) == ("per-route", ["rst"])
    placed = spread_channels(_placed(circuit, lib, at), supply=circuit.supply)
    plan = _plan(circuit, placed)
    assert plan.router == "channel"
    assert plan.by_name == []
    assert max(_islands(placed, plan).values()) == 1
    _assert_no_short(placed, plan)


def test_a_sheet_with_a_mosfet_keeps_the_per_route_planner(lib, sym_lib):
    """A cell sheet is never channel-routed, even with block symbols on it."""
    circuit = _array(2)
    placed = _placed(circuit, lib, {"XB0": Transform(0, 0), "XB1": Transform(360, 0)})
    nmos = Device(
        "M1",
        DeviceKind.MOS,
        "sg13_lv_nmos",
        MosPolarity.NMOS,
        ("DRAIN", "GATE", "SOURCE", "BULK"),
        {"DRAIN": "n1", "GATE": "clk", "SOURCE": "vss", "BULK": "vss"},
        {},
    )
    sym = sym_lib.load(symref_for(nmos, pdk="ihp-sg13g2") or "")
    assert sym is not None
    placed.append(PlacedDevice("M1", Transform(180, 400), nmos.nets, align_pins(nmos, sym)))
    plan = plan_connections(placed, supply=circuit.supply, port_role={}, router="channel")
    assert plan.router == "per-route" and plan.lanes == {}
    assert spread_channels(placed, supply=circuit.supply) == placed


def test_a_sheet_with_a_bipolar_primitive_is_channel_routed(lib, sym_lib):
    """The rule is "no MOSFET": the SG13G2 HBT arrives as a subcircuit primitive with pins
    ``c b e bn`` and no transistor role, so two blocks and an HBT are still routed by channels."""
    circuit = _array(2)
    placed = _placed(circuit, lib, {"XB0": Transform(0, 0), "XB1": Transform(360, 0)})
    hbt = Device(
        "XQ1",
        DeviceKind.SUBCKT,
        "npn13g2",
        MosPolarity.UNKNOWN,
        ("c", "b", "e", "bn"),
        {"c": "n1", "b": "clk", "e": "vss", "bn": "vss"},
        {},
    )
    sym = sym_lib.load(symref_for(hbt, pdk="ihp-sg13g2") or "")
    assert sym is not None and sym.type == "vertical_npn"
    placed.append(PlacedDevice("XQ1", Transform(180, 400), hbt.nets, align_pins(hbt, sym)))
    placed = spread_channels(placed, supply=circuit.supply)
    plan = plan_connections(placed, supply=circuit.supply, port_role={}, router="channel")
    assert plan.router == "channel"
    _assert_no_short(placed, plan)


HBT_PAIR = """* two HBTs, two poly resistors, no MOSFET, no design block (synthetic)
XQ1 c1 b e 0 npn13G2 Nx=1
XQ2 c2 b e 0 npn13G2 Nx=1
XR1 vdd c1 rsil w=0.5e-6 l=1e-6
XR2 vdd c2 rsil w=0.5e-6 l=1e-6
V1 vdd 0 1.2
.end
"""


def test_kit_primitives_are_not_blocks(sym_lib):
    """A block is a subcircuit drawn with a design's own symbol. The HBTs and the rsil resistors
    are subcircuit instances too, but of kit symbols (``model`` and ``spiceprefix`` in the
    template): four of them and no MOSFET are not a block diagram, even with channels asked for."""
    circuit = from_string(HBT_PAIR, name="hbt_pair")
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib, router="channel")
    assert doc.device_count == 5
    assert doc.router == "per-route"


def test_one_block_is_not_a_block_diagram(lib):
    circuit = _array(1)
    placed = _placed(circuit, lib, {"XB0": Transform(0, 0)})
    assert block_grid([]) is None
    assert channel_layout(_device_pins(placed), circuit.supply) is None
    assert channel_deficits(_device_pins(placed), circuit.supply) is None
    assert _plan(circuit, placed).router == "per-route"


def test_blocks_that_do_not_stand_in_columns_fall_back(lib):
    """A block overlapping two columns merges them, two blocks share a cell: per-route planner."""
    circuit = _array(3)
    at = {"XB0": Transform(0, 0), "XB1": Transform(360, 0), "XB2": Transform(180, 360)}
    placed = _placed(circuit, lib, at)
    assert block_grid(_device_pins(placed)) is None
    assert _plan(circuit, placed).router == "per-route"


# -------------------------------------------------------------------- lanes and channels


def _dp(ref: str, box, pins, *, block: bool = True, source: bool = False) -> DevicePins:
    return DevicePins(ref, box, tuple(pins), is_block=block, is_source=source)


def test_nets_sharing_a_channel_get_distinct_lanes_and_apart_nets_share_one():
    """Left-edge numbering: overlapping spans, distinct x; spans 400 apart, the same x."""
    a = _dp(
        "A",
        (0, 0, 100, 600),
        [("o1", "n1", 100, 50), ("o2", "n2", 100, 100), ("o3", "n3", 100, 500)],
    )
    b = _dp(
        "B",
        (300, 0, 400, 600),
        [("i1", "n1", 300, 150), ("i2", "n2", 300, 200), ("i3", "n3", 300, 550)],
    )
    layout = channel_layout([a, b], {})
    assert layout is not None and layout.lanes == {("v", 1): 2}
    xs = {r.net: r.wires[0][0] for r in layout.routes if r.kind == "lane"}
    assert xs["n1"] != xs["n2"]  # both span y 50..200
    assert xs["n3"] == xs["n1"]  # 500..550 is clear of 50..150 by more than the sharing gap


def test_pins_facing_each_other_at_one_height_order_their_lanes():
    """The left pin's lane must lie left of the right pin's, or the two stubs overlap (a short)."""
    a = _dp("A", (0, 0, 100, 200), [("o", "p", 100, 100), ("x", "q", 100, 60)])
    b = _dp("B", (300, 0, 400, 200), [("i", "q", 300, 100), ("y", "p", 300, 180)])
    layout = channel_layout([a, b], {})
    assert layout is not None
    xs = {r.net: r.wires[0][0] for r in layout.routes if r.kind == "lane"}
    assert xs["p"] < xs["q"]
    stubs = {(r.net, r.wires[0][1]): r.wires[0] for r in layout.routes if r.kind == "stub"}
    left, right = stubs[("p", 100)], stubs[("q", 100)]
    assert max(left[0], left[2]) < min(right[0], right[2])


def test_an_order_loop_leaves_one_pin_to_its_name_and_says_so():
    """p before q at y=100 and q before p at y=180: one pin is left out, and its net reported."""
    a = _dp("A", (0, 0, 100, 200), [("o", "p", 100, 100), ("x", "q", 100, 180)])
    b = _dp("B", (300, 0, 400, 200), [("i", "q", 300, 100), ("y", "p", 300, 180)])
    layout = channel_layout([a, b], {})
    assert layout is not None
    assert layout.unrouted == ("p",)
    # the loop pin of p is left out, which leaves p a single pin: nothing of p is drawn, q is whole
    assert {r.net for r in layout.routes} == {"q"}
    assert len([r for r in layout.routes if r.kind == "stub"]) == 2


def test_a_lane_past_the_capacity_is_not_drawn_and_its_net_is_reported():
    """A 40-unit gap holds one lane; a second net there is left to its name, not drawn over a pin."""
    a = _dp("A", (0, 0, 100, 200), [("o1", "n1", 100, 50), ("o2", "n2", 100, 100)])
    b = _dp("B", (140, 0, 240, 200), [("i1", "n1", 140, 160), ("i2", "n2", 140, 150)])
    layout = channel_layout([a, b], {})
    assert layout is not None
    assert layout.lanes[("v", 1)] == 2 and len(layout.unrouted) == 1
    lanes = [r for r in layout.routes if r.kind == "lane"]
    assert len(lanes) == 1 and lanes[0].wires[0][0] == 100 + LANE_MARGIN
    shifts = channel_deficits([a, b], {})
    assert shifts == {"A": (0, 0), "B": (LANE_PITCH, 0)}


def test_the_widened_placement_routes_every_lane(lib):
    """At a 240 pitch the blocks leave 36-unit gaps (no lane fits); spreading makes room and
    nothing is dropped."""
    circuit = _top()
    placed = _placed(circuit, lib, _grid_at(circuit, 240))
    narrow = channel_layout(_device_pins(placed), circuit.supply)
    assert narrow is not None and narrow.unrouted  # before the move: lanes past capacity
    moved = spread_channels(placed, supply=circuit.supply)
    wide = channel_layout(_device_pins(moved), circuit.supply)
    assert wide is not None and wide.unrouted == () and wide.lanes == narrow.lanes
    # a wide placement is left where it is
    roomy = _placed(circuit, lib, _grid_at(circuit, 600))
    assert spread_channels(roomy, supply=circuit.supply) == roomy


def test_rails_sit_next_to_their_taps_and_the_spines_outermost():
    """Supplies first: vss (tapped from above) is the channel's top track, vdd (from below) its
    bottom one, a signal trunk between them; the VDD spine is the leftmost lane, VSS the rightmost."""
    top = [
        _dp(
            f"T{i}",
            (i * 300, 0, i * 300 + 100, 100),
            [("vss", "vss", i * 300 + 50, 100), ("o", "s", i * 300 + 100, 50)],
        )
        for i in range(2)
    ]
    bot = [
        _dp(
            f"B{i}",
            (i * 300, 400, i * 300 + 100, 500),
            [
                ("vdd", "vdd", i * 300 + 50, 400),
                ("vss", "vss", i * 300 + 50, 500),
                ("i", "s", i * 300, 450),
            ],
        )
        for i in range(2)
    ]
    top.append(_dp("V", (600, 0, 700, 100), [("vdd", "vdd", 650, 0), ("vss", "vss", 650, 100)]))
    layout = channel_layout([*top, *bot], {"vdd": "VDD", "vss": "VSS"})
    assert layout is not None
    tracks = {(r.net, r.wires[0][1]) for r in layout.routes if r.kind == "track"}
    in_gap = sorted((y, n) for n, y in tracks if 100 < y < 400)
    assert [n for _, n in in_gap] == ["vss", "s", "vdd"]
    lanes = sorted((r.wires[0][0], r.net) for r in layout.routes if r.kind == "lane")
    assert lanes[0][1] == "vdd" and lanes[-1][1] == "vss"
    assert [r.net for r in layout.routes][:1] == ["vdd"]  # supply routes come first


def test_a_top_pin_of_a_wide_short_block_leaves_upward():
    """Measured against the body box, not the origin: this pin is further out in x than in y."""
    a = _dp("A", (0, 0, 600, 100), [("t", "n", 560, 0), ("u", "n", 40, 0)])
    b = _dp("B", (0, 300, 600, 400), [("v", "m", 300, 300)])
    layout = channel_layout([a, b], {})
    assert layout is not None
    assert {r.kind for r in layout.routes if r.net == "n"} == {"stub", "track"}
    assert all(w[0] == w[2] for r in layout.routes if r.kind == "stub" for w in r.wires)


def test_a_signal_entering_two_horizontal_channels_gets_a_connector_lane():
    """Pins on top of a row-0 block and under a row-1 block: two tracks, joined by one lane in the
    vertical channel nearest their column (column 1 sits between channels 1 and 2; ties go low)."""
    blocks = [
        _dp("A0", (0, 0, 100, 100), [("o", "x", 100, 50)]),
        _dp("A1", (300, 0, 400, 100), [("t", "n", 350, 0), ("i", "x", 300, 50)]),
        _dp("B1", (300, 300, 400, 400), [("b", "n", 350, 400)]),
    ]
    layout = channel_layout(blocks, {})
    assert layout is not None
    kinds = sorted((r.kind, r.wires[0]) for r in layout.routes if r.net == "n")
    tracks = [w for k, w in kinds if k == "track"]
    lanes = [w for k, w in kinds if k == "lane"]
    assert len(tracks) == 2 and len(lanes) == 1
    assert 100 < lanes[0][0] < 300  # vertical channel 1, between the two columns
    assert {w[1] for w in tracks} == {lanes[0][1], lanes[0][3]}  # the lane ends on both tracks


def test_left_edge_refuses_an_order_loop_instead_of_spinning():
    from spicexplorer_netlist2xschem.channels import _left_edge

    with pytest.raises(RuntimeError, match="loop"):
        _left_edge({"a": (0, 10), "b": (0, 10)}, {("a", "b"): [], ("b", "a"): []})


def test_a_source_is_an_obstacle_not_a_route():
    a = _dp("A", (0, 0, 100, 100), [("o", "n", 100, 50)])
    b = _dp("B", (300, 0, 400, 100), [("i", "n", 300, 50)])
    v = _dp(
        "V1",
        (600, 0, 640, 100),
        [("P", "n", 620, 0), ("N", "0", 620, 100)],
        block=False,
        source=True,
    )
    layout = channel_layout([a, b, v], {})
    assert layout is not None and len(layout.grid.cols) == 3
    assert all(620 not in (w[0], w[2]) for r in layout.routes for w in r.wires)


# ------------------------------------------------------- supplies verified first, then held


def _pair_routed_with(lib, monkeypatch, edit):
    """The 2-cell array, planned with its real channel layout after ``edit`` changes the routes.

    ``plan_connections`` asks :func:`channel_layout` for the routes; the patch hands it the edited
    list instead, so the connectivity verifier sees a conflict the router itself never draws.
    """
    circuit = _array(2)
    at = {"XB0": Transform(0, 0), "XB1": Transform(360, 0)}
    placed = spread_channels(_placed(circuit, lib, at), supply=circuit.supply)
    real = channel_layout(_device_pins(placed), circuit.supply)
    assert real is not None
    crafted = replace(real, routes=tuple(edit(list(real.routes))))
    monkeypatch.setattr(wiring, "channel_layout", lambda _devices, _supply: crafted)
    return circuit, placed, _plan(circuit, placed)


def _only(routes, net: str, kind: str) -> ChannelRoute:
    (route,) = [r for r in routes if r.net == net and r.kind == kind]
    return route


def test_a_signal_track_laid_on_a_rail_is_refused_and_the_rail_kept(lib, monkeypatch):
    """The clk track moved onto the vdd rail's y overlaps it (a short). The supply routes were
    verified first and are held fixed, so the clk track is refused and the rail stays drawn.
    Verified in one pass, both routes would be dropped and vdd left to its name."""
    rail = {}

    def onto_the_rail(routes):
        vdd = _only(routes, "vdd", "track").wires
        clk = _only(routes, "clk", "track")
        (x0, _y, x1, _y), y = clk.wires[0], vdd[0][1]
        assert len(vdd) == 1 and max(x0, vdd[0][0]) < min(x1, vdd[0][2])  # the two overlap in x
        rail["wire"], rail["clk"] = vdd[0], (x0, y, x1, y)
        return [replace(r, wires=(rail["clk"],)) if r is clk else r for r in routes]

    circuit, placed, plan = _pair_routed_with(lib, monkeypatch, onto_the_rail)
    assert wiring.Wire(*rail["wire"]) in plan.wires
    assert wiring.Wire(*rail["clk"]) not in plan.wires
    assert "vdd" not in plan.by_name and _islands(placed, plan)["vdd"] == 1
    _assert_no_short(placed, plan)


def test_a_refused_supply_route_does_not_refuse_a_signal(lib, monkeypatch):
    """A supply wire laid over XB0's clk pin is refused in the supply check; it is not drawn, so it
    is no obstacle for the signals either: the plan is the one drawn without it."""

    def over_the_clk_pin(routes):
        # a stub starts at its pin: the leftmost clk stub starts at XB0's clk pin
        stubs = [r.wires[0] for r in routes if r.net == "clk" and r.kind == "stub"]
        x, y = min(stubs)[:2]
        rail_y = _only(routes, "vdd", "track").wires[0][1]
        return [*routes, ChannelRoute("vdd", "stub", ((x, y, x, rail_y),))]

    circuit, placed, plan = _pair_routed_with(lib, monkeypatch, over_the_clk_pin)
    monkeypatch.undo()
    clean = _plan(circuit, placed)
    assert (plan.wires, plan.labels, plan.by_name) == (clean.wires, clean.labels, clean.by_name)
    assert plan.by_name == []


def test_a_supply_wire_the_dangling_run_rule_removes_is_counted_refused(lib, monkeypatch):
    """A vdd stub drawn in empty space touches nothing, so the connectivity check keeps it and
    the dangling-run rule then removes it. The report counts it refused, not drawn, and the rest
    of the plan is the one drawn without it."""

    def a_stray_vdd_stub(routes):
        return [*routes, ChannelRoute("vdd", "stub", ((-600, -600, -600, -580),))]

    circuit, placed, plan = _pair_routed_with(lib, monkeypatch, a_stray_vdd_stub)
    monkeypatch.undo()
    clean = _plan(circuit, placed)
    assert (plan.wires, plan.by_name) == (clean.wires, clean.by_name)
    assert clean.supply["vdd"]["refused"] == 0
    assert plan.supply["vdd"] == {**clean.supply["vdd"], "refused": 1}


# ------------------------------------------------------------------------ block bodies


def test_a_symbol_bbox_covers_lines_boxes_polygons_and_arcs():
    text = "\n".join(
        [
            "v {xschem version=3.4.6 file_version=1.2}",
            "K {type=subcircuit}",
            "L 4 -80 -60 80 -60 {}",
            "B 5 -102.5 -2.5 -97.5 2.5 {name=a dir=in}",
            "P 4 3 0 70 10 90 -10 90 {}",
            "A 4 120 0 15 0 360 {}",
            "A 4 bad {}",
            "T {@name} -300 -300 0 0 0.2 0.2 {}",
        ]
    )
    assert parse_symbol(text).bbox == (-102.5, -60.0, 135.0, 90.0)
    assert parse_symbol("v {}\nK {type=primitive}\nT {x} 0 0 0 0 1 1 {}").bbox is None


def test_a_block_keeps_its_labels_and_detours_off_its_whole_body(lib):
    """``device_extent`` of a block is its drawn extent (body, pin stubs and pin boxes), not the
    transistor-sized default box: blk_a's body is 160 x 160 and its pins sit 20 outside it."""
    circuit = _array(1)
    (pd,) = _placed(circuit, lib, {"XB0": Transform(1000, 500)})
    assert device_extent(pd) == (898, 398, 1102, 602)
    plain = replace(pd, body=None)
    assert device_extent(plain) != device_extent(pd)


# ------------------------------------------------------------------------------ the CLI switch


@pytest.mark.parametrize(
    ("argv", "router"), [([], "per-route"), (["--router", "channel"], "channel")]
)
def test_the_cli_asks_for_channels_only_with_the_flag(tmp_path, monkeypatch, argv, router):
    """The flat lane hands ``build_sch`` the router named on the command line, per-route unless
    ``--router channel`` is given."""
    from spicexplorer_netlist2xschem import cli

    seen: list[str] = []
    real = cli.build_sch

    def spy(*a, **k):
        seen.append(k["router"])
        return real(*a, **k)

    monkeypatch.setattr(cli, "build_sch", spy)
    out = tmp_path / "mixed.sch"
    assert cli.main([str(FIXTURES / "mixed_devices.spice"), "-o", str(out), *argv]) == 0
    assert seen == [router]


@pytest.mark.parametrize("lane", [["--hierarchical"], ["--annotate-existing"]])
def test_the_cli_refuses_channels_where_it_plans_no_wires(tmp_path, capsys, lane):
    from spicexplorer_netlist2xschem.cli import main

    argv = [str(FIXTURES / "mixed_devices.spice"), "-o", str(tmp_path / "x.sch"), *lane]
    assert main([*argv, "--router", "channel"]) == 2
    assert "does not combine with --hierarchical or --annotate-existing" in capsys.readouterr().err
