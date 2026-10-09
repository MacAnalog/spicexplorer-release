"""Connectivity is DRAWN — the four shapes a whole set of schematics-of-record came back wrong in.

Every one of them passed the netlist gate (``xschem -n`` re-netlists them correctly, because the
comparison matches nets by NAME), and a human reviewer could not read any of them:

1. **ports parked at the frame** — every circuit-I/O net drawn twice, a floating pin at the edge and
   a label on the real wire;
2. **a net drawn as two islands** — the straight join grazes a foreign pin, so it is dropped and the
   two halves are left linked by name (the transmission-gate tie that must pass a body pin);
3. **a bulk-only supply with no rail at all** — the rails simply absent from the sheet;
4. **a trunk that ends in mid-air** — the worst of the four and not a legibility complaint: one leg
   of an L is refused, the other is drawn anyway, and the wire that looks like the connection joins
   nothing. The island it fails to reach carries no name, so xschem invents one and the cell
   netlists one terminal short of the net the input netlist stated: a silent open.

Each shape is a hand floorplan (a ``FixedPlacer``) that reproduces it deterministically, so these
are regression fixtures and not luck. The invariant over all of them is the one gate that matters —
**a drawn route must never change connectivity**: the sheets are re-netlisted through real xschem
and compared pin-by-pin against the circuit they were drawn from.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    analyze,
    build_sch,
    contaminated_nets,
    from_string,
    plan_connections,
)
from spicexplorer_netlist2xschem.connectivity import Seg, Terminal, _point_on_seg
from spicexplorer_netlist2xschem.geometry import Transform, apply_transform
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity, N2XCircuit
from spicexplorer_netlist2xschem.mapping import align_pins, symref_for
from spicexplorer_netlist2xschem.sym_library import default_search_paths
from spicexplorer_netlist2xschem.wiring import ConnectionPlan, PlacedDevice, Wire, _wire_components

PDK = "ihp-sg13g2"
Point = tuple[int, int]


# --------------------------------------------------------------------------------------- scaffold


@dataclass
class FixedPlacer:
    """A hand floorplan: the exact transform per device ref (what a designer drew, not a placer)."""

    at: dict[str, Transform]

    def place(self, circuit, lib=None, *, hints=None) -> dict[str, Transform]:  # noqa: ARG002
        return dict(self.at)


def _mos(ref: str, polarity: MosPolarity, **nets: str) -> Device:
    model = "sg13_lv_nmos" if polarity is MosPolarity.NMOS else "sg13_lv_pmos"
    return Device(
        ref=ref,
        kind=DeviceKind.MOS,
        model=model,
        polarity=polarity,
        pins=("DRAIN", "GATE", "SOURCE", "BULK"),
        nets={k.upper(): v for k, v in nets.items()},
        params={"w": "1u", "l": "0.13u"},
    )


def _circuit(name: str, devices: list[Device], *, ports: tuple[str, ...] = ()) -> N2XCircuit:
    nets = sorted({n for d in devices for n in d.nets.values()})
    supply = {n: ("VDD" if "vdd" in n else "VSS") for n in nets if n.startswith(("vdd", "vss"))}
    return N2XCircuit(
        name=name, devices=tuple(devices), nets=tuple(nets), supply=supply, ports=ports
    )


def _placed(circuit: N2XCircuit, lib, placer: FixedPlacer) -> list[PlacedDevice]:
    out: list[PlacedDevice] = []
    placement = placer.place(circuit, lib)
    for dev in circuit.devices:
        symref = symref_for(dev, pdk=PDK)
        sym = lib.load(symref) if symref else None
        assert sym is not None, f"{dev.ref}: no symbol for {dev.model}"
        out.append(
            PlacedDevice(
                ref=dev.ref,
                transform=placement[dev.ref],
                nets=dev.nets,
                aligned=align_pins(dev, sym),
                is_source=dev.kind in (DeviceKind.VSOURCE, DeviceKind.ISOURCE),
            )
        )
    return out


def _plan(
    circuit: N2XCircuit, lib, placer: FixedPlacer
) -> tuple[list[PlacedDevice], ConnectionPlan]:
    placed = _placed(circuit, lib, placer)
    return placed, plan_connections(
        placed, supply=circuit.supply, port_role=analyze(circuit).port_role
    )


def _pin_points(placed: list[PlacedDevice]) -> dict[Point, str]:
    return {
        apply_transform(pd.transform, sp.x, sp.y): pd.nets[canon]
        for pd in placed
        for canon, sp in pd.aligned.items()
    }


def _net_points(placed: list[PlacedDevice], net: str, *, bulk: bool = True) -> list[Point]:
    return sorted(
        apply_transform(pd.transform, sp.x, sp.y)
        for pd in placed
        for canon, sp in pd.aligned.items()
        if pd.nets[canon] == net and (bulk or canon != "BULK")
    )


def _floating_runs(placed: list[PlacedDevice], plan: ConnectionPlan) -> list[Wire]:
    """Drawn wires that reach a point holding nothing — the silent open of shape 4.

    A run is floating when one of its ends lands on no pin, no label, no port pin and no other wire,
    *and* the run carries no name of its own anywhere along it. That exemption is what keeps a
    terminal's own whisker and a supply rail's overhang (both named on the pin/label they carry) out
    of the count: neither pretends to be a connection to somewhere else.
    """
    named = set(_pin_points(placed))
    named |= {(lbl.x, lbl.y) for lbl in plan.labels} | {(p.x, p.y) for p in plan.ports}
    segs = [Seg(w.x1, w.y1, w.x2, w.y2, "") for w in plan.wires]
    out: list[Wire] = []
    for i, w in enumerate(plan.wires):
        if any(_point_on_seg(px, py, segs[i]) for px, py in named):
            continue  # the run carries a pin or a name — a stub or a rail, not a join
        for end in ((w.x1, w.y1), (w.x2, w.y2)):
            if end in named:
                continue
            if any(j != i and _point_on_seg(end[0], end[1], s) for j, s in enumerate(segs)):
                continue
            out.append(w)
            break
    return out


def _unnamed_islands(placed: list[PlacedDevice], plan: ConnectionPlan) -> int:
    """Connected pieces of the drawn wiring that carry no net name at all (xschem invents one)."""
    named = set(_pin_points(placed))
    named |= {(lbl.x, lbl.y) for lbl in plan.labels} | {(p.x, p.y) for p in plan.ports}
    pieces = _wire_components(
        sorted({p for w in plan.wires for p in ((w.x1, w.y1), (w.x2, w.y2))} | named), plan.wires
    )
    touched = {p for w in plan.wires for p in ((w.x1, w.y1), (w.x2, w.y2))}
    return sum(
        1
        for comp in pieces
        if any(p in touched for p in comp) and not any(p in named for p in comp)
    )


def _assert_no_short(placed: list[PlacedDevice], plan: ConnectionPlan) -> None:
    segs = [Seg(w.x1, w.y1, w.x2, w.y2, "") for w in plan.wires]
    terminals = [Terminal(x, y, net) for (x, y), net in _pin_points(placed).items()]
    terminals += [Terminal(lbl.x, lbl.y, lbl.lab) for lbl in plan.labels]
    terminals += [Terminal(p.x, p.y, p.net) for p in plan.ports]
    assert contaminated_nets(segs, terminals) == set(), "the drawn wiring would short two nets"


# ------------------------------------------------------------------------------------- the shapes


def _shape_trunk_in_mid_air() -> tuple[N2XCircuit, FixedPlacer]:
    """Shape 4: six terminals of one net on a row, one more 2 200 below on the vertical axis.

    A hand floorplan that puts a cell's tail device on a centre line well below the rest. The row's
    gate ports sit at ``x = ox − 50``; the tail's is at ``x = −50``, so the L-bridge to it is drawn
    from the nearest row port at ``(−380, 0)``: h-leg along the row, then the trunk down. A foreign
    gate pin at ``(−200, 0)`` sits on that h-leg, so the h-leg is refused — and the trunk used to be
    drawn anyway, from ``(−50, 0)``, where there is nothing.
    """
    devs = [
        _mos(f"MC{i}", MosPolarity.NMOS, drain=f"o{i}", gate="clk", source="vss", bulk="vss")
        for i in range(6)
    ]
    devs.append(_mos("MT1", MosPolarity.NMOS, drain="ot", gate="clk", source="vss", bulk="vss"))
    devs.append(_mos("MX", MosPolarity.NMOS, drain="ox1", gate="other", source="vss", bulk="vss"))
    row = (-1430, -850, -330, 430, 950, 1530)
    at = {f"MC{i}": Transform(x, 0) for i, x in enumerate(row)}
    at["MT1"] = Transform(0, 2200)  # the tail on the centre line, 2 200 below the row
    at["MX"] = Transform(-180, 0)  # its gate pin lands on the row, between two of the six
    return _circuit("tail_on_the_axis", devs), FixedPlacer(at)


def _shape_two_islands() -> tuple[N2XCircuit, FixedPlacer]:
    """Shape 2: a drain/source tie whose straight column run has to pass a body pin between them."""
    devs = [
        _mos("MA", MosPolarity.NMOS, drain="ta", gate="ga", source="mid", bulk="vss"),
        _mos("MC", MosPolarity.NMOS, drain="tc", gate="gc", source="tc2", bulk="vss"),
        _mos("MB", MosPolarity.NMOS, drain="mid", gate="gb", source="tb", bulk="vss"),
    ]
    at = {"MA": Transform(0, 0), "MC": Transform(0, 200), "MB": Transform(0, 400)}
    return _circuit("stacked_tie", devs), FixedPlacer(at)


def _shape_bulk_only_supplies() -> tuple[N2XCircuit, FixedPlacer]:
    """Shape 3: vdd/vss appear ONLY as body pins — the sampler and every CDAC bit cell's rails."""
    devs = [
        _mos("MN1", MosPolarity.NMOS, drain="d1", gate="g1", source="s1", bulk="vss"),
        _mos("MN2", MosPolarity.NMOS, drain="d2", gate="g2", source="s2", bulk="vss"),
        _mos("MP1", MosPolarity.PMOS, drain="d1", gate="g1", source="s3", bulk="vdd"),
        _mos("MP2", MosPolarity.PMOS, drain="d2", gate="g2", source="s4", bulk="vdd"),
    ]
    at = {
        "MN1": Transform(0, 0),
        "MN2": Transform(400, 0),
        "MP1": Transform(0, 400),
        "MP2": Transform(400, 400),
    }
    return _circuit("bulk_only_rails", devs), FixedPlacer(at)


def _shape_ports() -> tuple[N2XCircuit, FixedPlacer]:
    """Shape 1: a cell with declared circuit-I/O — every port used to be parked at the frame."""
    devs = [
        _mos("MP1", MosPolarity.PMOS, drain="vout", gate="vin", source="vdd", bulk="vdd"),
        _mos("MN1", MosPolarity.NMOS, drain="vout", gate="vin", source="vss", bulk="vss"),
    ]
    circuit = _circuit("inverter_cell", devs, ports=("vin", "vout", "vdd", "vss"))
    return circuit, FixedPlacer({"MP1": Transform(0, 0), "MN1": Transform(0, 400)})


def _fence(circuit: N2XCircuit, placer: FixedPlacer) -> tuple[N2XCircuit, dict[str, Transform]]:
    """The same stacked tie, walled in on both sides by foreign pins (a crowded sheet)."""
    fence = [
        _mos(f"MF{i}", MosPolarity.NMOS, drain=f"f{i}", gate=f"fg{i}", source="vss", bulk="vss")
        for i in range(12)
    ]
    at = dict(placer.at)
    for i in range(6):
        at[f"MF{i}"] = Transform(-260, 40 + i * 70)
        at[f"MF{i + 6}"] = Transform(300, 40 + i * 70)
    return _circuit("fenced_tie", [*circuit.devices, *fence]), at


SHAPES = {
    "trunk-in-mid-air": _shape_trunk_in_mid_air,
    "two-islands": _shape_two_islands,
    "bulk-only-supplies": _shape_bulk_only_supplies,
    "ports": _shape_ports,
}


# ------------------------------------------------------------- shape 4: nothing ends in mid-air


def test_a_refused_leg_never_leaves_the_trunk_reaching_into_nothing(sym_lib):
    """The fourth shape: the L's h-leg is refused, so the trunk to the tail must not be drawn alone.

    The old planner emitted each leg as its own route, so the surviving trunk ran from the tail's
    gate up to a point on the row that touches neither of the terminals it lands between. This
    asserts the endpoint rule directly — every drawn run ends on a pin, a wire or a name of its own
    net — and that no piece of drawn wiring is left without a name for xschem to invent one for.
    """
    circuit, placer = _shape_trunk_in_mid_air()
    placed, plan = _plan(circuit, sym_lib, placer)

    assert _floating_runs(placed, plan) == [], "a run was drawn to a point that holds nothing"
    assert _unnamed_islands(placed, plan) == 0, "a drawn island carries no net name"
    _assert_no_short(placed, plan)
    # With the L kept whole the refused h-leg takes its trunk with it, and the detour pass then
    # reaches the tail the long way round: the seven terminals end up on ONE drawn piece.
    assert len(_wire_components(_net_points(placed, "clk"), plan.wires)) == 1
    assert "clk" not in plan.by_name


def test_the_tail_terminal_is_named_when_its_join_is_refused(sym_lib):
    """Whatever the geometry allows, every terminal of the split net carries its name.

    Drawing nothing is worse than drawing a name; drawing a wire to nowhere is worse than both. The
    fallback has to actually happen, so each piece of ``clk`` the wiring left apart gets a label.
    """
    circuit, placer = _shape_trunk_in_mid_air()
    placed, plan = _plan(circuit, sym_lib, placer)

    pins = _net_points(placed, "clk")
    named = {(lbl.x, lbl.y) for lbl in plan.labels if lbl.lab == "clk"}
    named |= {(p.x, p.y) for p in plan.ports if p.net == "clk"}
    assert named, "the net is not named anywhere"
    for comp in _wire_components(sorted(set(pins) | named), plan.wires):
        if any(c in pins for c in comp):
            assert any(c in named for c in comp), f"a piece of clk {comp} carries no name"


# ------------------------------------------------------------------- shape 3: bulk-only supplies


def test_a_supply_whose_terminals_are_all_body_pins_still_gets_its_rail(sym_lib):
    """The rails are the first thing a reader looks for; a bulk-only supply used to have none."""
    circuit, placer = _shape_bulk_only_supplies()
    placed, plan = _plan(circuit, sym_lib, placer)

    for net in ("vdd", "vss"):
        assert net in circuit.supply
        rails = [
            w
            for w in plan.wires
            if w.y1 == w.y2
            and abs(w.x2 - w.x1) > 400
            and any(
                lbl.lab == net and (lbl.x, lbl.y) in ((w.x1, w.y1), (w.x2, w.y2))
                for lbl in plan.labels
            )
        ]
        assert rails, f"{net}: no rail was drawn for a supply whose terminals are all body pins"
    _assert_no_short(placed, plan)


def test_a_wirable_supply_still_wins_the_rail_over_a_bulk_only_one(sym_lib):
    """Two-tier, not first-past-the-post: the net whose pins can flush onto the rail keeps it."""
    devs = [
        _mos("MN1", MosPolarity.NMOS, drain="d1", gate="g1", source="vss", bulk="agnd"),
        _mos("MN2", MosPolarity.NMOS, drain="d2", gate="g2", source="vss", bulk="agnd"),
    ]
    circuit = N2XCircuit(
        name="two_grounds",
        devices=tuple(devs),
        nets=("agnd", "d1", "d2", "g1", "g2", "vss"),
        supply={"agnd": "GND", "vss": "VSS"},  # 'agnd' sorts first but is bulk-only
        ports=(),
    )
    placed, plan = _plan(
        circuit, sym_lib, FixedPlacer({"MN1": Transform(0, 0), "MN2": Transform(400, 0)})
    )
    bottom = max(w.y1 for w in plan.wires if w.y1 == w.y2)
    on_rail = {lbl.lab for lbl in plan.labels if lbl.y == bottom}
    assert "vss" in on_rail and "agnd" not in on_rail


# ------------------------------------------------------------------------- shape 2: two islands


def test_a_tie_blocked_by_a_body_pin_is_detoured_not_dropped_to_a_name(sym_lib):
    """The straight column run grazes the middle device's pins, so the tie takes the lane beside it.

    This is the shape the issue names: two devices whose drain/source tie has to pass the body pin
    between them drew as two unconnected transistors. The detour is only ever accepted when
    ``connectivity.conflicting_routes`` clears it, so the join can never be a short.
    """
    circuit, placer = _shape_two_islands()
    placed, plan = _plan(circuit, sym_lib, placer)

    assert len(_wire_components(_net_points(placed, "mid"), plan.wires)) == 1, (
        "the tie is still drawn as two islands linked by name"
    )
    assert "mid" not in plan.by_name
    _assert_no_short(placed, plan)
    assert _floating_runs(placed, plan) == []


def test_a_crowded_sheet_still_draws_no_short_and_reports_what_it_could_not_draw(sym_lib):
    """A detour is an attempt, never a licence to draw through something.

    Fencing the stacked tie in two walls of foreign pins is the case where a route refused by the
    verifier is the norm rather than the exception. Nothing may short, nothing may end in mid-air,
    and every terminal the planner could not reach with a wire has to be reported — by name in
    ``by_name``, and as a parked port where the port pin had no drawn wire to sit on.
    """
    circuit, placer = _shape_two_islands()
    fenced, at = _fence(circuit, placer)
    placed, plan = _plan(fenced, sym_lib, FixedPlacer(at))

    _assert_no_short(placed, plan)
    assert _floating_runs(placed, plan) == []
    assert _unnamed_islands(placed, plan) == 0
    assert plan.parked_ports, "a port with no drawn wire was neither placed nor reported"
    assert set(plan.parked_ports) <= set(plan.by_name), "a parked port is missing from by_name"


# ------------------------------------------------------------------------------ shape 1: ports


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_every_port_pin_sits_on_its_own_nets_wiring(sym_lib, shape):
    """A port pin IS the connection: it lands on a drawn wire of its net, or it is reported parked."""
    circuit, placer = SHAPES[shape]()
    circuit = N2XCircuit(
        name=circuit.name,
        devices=circuit.devices,
        nets=circuit.nets,
        supply=circuit.supply,
        ports=tuple(n for n in circuit.nets if not n.startswith(("vdd", "vss"))),
    )
    placed, plan = _plan(circuit, sym_lib, placer)
    assert plan.ports, f"{shape}: expected port pins"
    for port in plan.ports:
        if port.net in plan.parked_ports:
            continue
        assert any(
            _point_on_seg(port.x, port.y, Seg(w.x1, w.y1, w.x2, w.y2, "")) for w in plan.wires
        ), f"{shape}: the {port.net} port pin sits on no wire of its net"


def test_a_port_replaces_the_duplicate_label_instead_of_adding_to_it(sym_lib):
    """The first shape's tell: every port drawn twice — a pin at the edge and a label on the wire."""
    circuit, placer = _shape_ports()
    placed, plan = _plan(circuit, sym_lib, placer)

    assert plan.parked_ports == [], "a port parked at the frame although its net is drawn"
    for port in plan.ports:
        assert not any(
            (lbl.x, lbl.y, lbl.lab) == (port.x, port.y, port.net) for lbl in plan.labels
        ), f"{port.net} is named twice at the same point"
        # the port is inside the drawing, not parked out at the frame margin
        assert any(
            _point_on_seg(port.x, port.y, Seg(w.x1, w.y1, w.x2, w.y2, "")) for w in plan.wires
        )
    _assert_no_short(placed, plan)


def test_the_plan_reports_what_is_still_carried_by_name(sym_lib):
    """``by_name`` is the number a caller can act on: nets the drawing still joins by label only."""
    circuit, placer = _shape_ports()
    _, plan = _plan(circuit, sym_lib, placer)
    assert plan.by_name == []  # a two-device cell draws entirely by wire

    # …and a sheet the geometry defeats says so, rather than looking the same as a wired one.
    circuit2, placer2 = _shape_two_islands()
    fenced, at = _fence(circuit2, placer2)
    _, plan2 = _plan(fenced, sym_lib, FixedPlacer(at))
    assert plan2.by_name, "a sheet that falls back to names reports nothing"


# ------------------------------------------------------- the invariant: connectivity is unchanged


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_the_drawn_sheet_is_connectivity_safe(sym_lib, shape):
    circuit, placer = SHAPES[shape]()
    placed, plan = _plan(circuit, sym_lib, placer)
    _assert_no_short(placed, plan)
    assert _floating_runs(placed, plan) == []
    assert _unnamed_islands(placed, plan) == 0


def _xschem_netlist(sch_text: str, stem: str, tmp_path: Path, fixtures: Path) -> str:
    """Re-netlist a sheet with real headless xschem (the third-party oracle, not our own reader)."""
    from spicexplorer_netlist2xschem.render import write_xschemrc

    work = tmp_path / stem
    work.mkdir(parents=True, exist_ok=True)
    source = work / f"{stem}.sch"
    source.write_text(sch_text)
    entries = [str(fixtures / "sym"), str(fixtures / "sym" / "devices")]
    for root in default_search_paths():
        entries.append(str(root))
        if (root / "devices").is_dir():
            entries.append(str(root / "devices"))
    library_path = os.pathsep.join(dict.fromkeys(entries))
    rc = write_xschemrc(work, library_path)
    env = dict(os.environ, XSCHEM_LIBRARY_PATH=library_path)
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-n", "-q", "-x", "-o", str(work), str(source)],
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(work),
    )
    out = work / f"{stem}.spice"
    assert out.is_file(), "xschem produced no netlist"
    return out.read_text()


@pytest.mark.parametrize("shape", sorted(SHAPES))
@pytest.mark.skipif(shutil.which("xschem") is None, reason="xschem is not on PATH")
def test_the_sheet_renetlists_to_the_circuit_it_was_drawn_from(sym_lib, shape, tmp_path):
    """The gate that matters: a drawn route must never change connectivity.

    Netlist the emitted sheet with xschem itself and compare terminal by terminal against the
    circuit it was drawn from, up to a renaming of the nets (an island xschem had to name itself
    would break the one-to-one mapping, which is exactly the fourth shape's failure).
    """
    circuit, placer = SHAPES[shape]()
    doc = build_sch(circuit, pdk=PDK, lib=sym_lib, placer=placer, show_device_params=True)
    text = _xschem_netlist(
        doc.text, shape.replace("-", "_"), tmp_path, Path(__file__).parent / "fixtures"
    )
    back = from_string(text, name=circuit.name)

    def terminals(c: N2XCircuit) -> dict[tuple[str, str], str]:
        # xschem instantiates a subckt-based device as ``X<ref>``; the terminal is the same one.
        return {
            (d.ref.upper().removeprefix("X"), pin): net
            for d in c.devices
            for pin, net in d.nets.items()
        }

    before, after = terminals(circuit), terminals(back)
    assert set(before) == set(after), "the sheet netlists a different set of device terminals"
    forward: dict[str, str] = {}
    backward: dict[str, str] = {}
    for key in sorted(before):
        was, now = before[key], after[key]
        assert forward.setdefault(was, now) == now, f"{key}: net {was} split into {now}"
        assert backward.setdefault(now, was) == was, f"{key}: nets {was} and {backward[now]} merged"


def test_the_emitted_document_carries_the_named_join_report(sym_lib):
    """A caller that never touches the plan still sees how much of the sheet is drawn by name."""
    circuit, placer = _shape_ports()
    doc = build_sch(circuit, pdk=PDK, lib=sym_lib, placer=placer)
    assert doc.nets_by_name == () and doc.parked_ports == ()
    by_label = build_sch(circuit, pdk=PDK, lib=sym_lib, placer=placer, wiring="labels")
    # that mode joins everything by name — every net with more than one terminal to join (vdd/vss
    # reach one channel pin each here, so only the two signal nets are actually *joined* by a name)
    assert set(by_label.nets_by_name) == {"vin", "vout"}


def test_the_collinear_merge_never_merges_a_junction_away():
    """The cosmetic pass must not turn a T into a crossing — xschem would stop connecting there.

    Two collinear pieces per axis meeting at one corner: merge both and the corner is the strict
    interior of BOTH runs, which xschem reads as two wires passing over each other, not a junction.
    The net silently splits in the emitted sheet even though every route was verified.
    """
    from spicexplorer_netlist2xschem.wiring import _merge_collinear

    merged = _merge_collinear(
        [
            Wire(0, 0, 0, 50),  # the stem, arriving from above
            Wire(0, 50, 0, 100),  # and continuing below the corner
            Wire(-50, 50, 0, 50),  # the crossbar, arriving from the left
            Wire(0, 50, 50, 50),  # and continuing to the right
        ]
    )
    assert len(_wire_components([(0, 0), (50, 50)], merged)) == 1, (
        "the merge buried the junction inside a run on both axes and broke the connection"
    )
