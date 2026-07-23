"""Emit — a byte-stable golden plus structural self-consistency checks.

The golden pins the exact ``.sch`` text for a tiny mixed-device circuit (nmos/pmos/R/C/V/I). The
structural checks run against the real OTA fixtures and assert, without xschem, that every device is
drawn and every net it touches appears as a label (so the schematic is fully wired).
"""

import re
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    GridPlacer,
    PhasedPlacer,
    TopologyPlacer,
    analyze,
    build_sch,
    contaminated_nets,
    from_file,
    plan_connections,
    to_sch,
)
from spicexplorer_netlist2xschem.connectivity import Seg, Terminal
from spicexplorer_netlist2xschem.geometry import apply_transform
from spicexplorer_netlist2xschem.ingest import DeviceKind
from spicexplorer_netlist2xschem.mapping import align_pins, symref_for
from spicexplorer_netlist2xschem.wiring import PlacedDevice

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN = FIXTURES / "golden" / "mixed_devices.sch"

# `C {symref} x y rot flip {attrs}`
_INSTANCE = re.compile(r"^C \{(\S+)\} (-?\d+) (-?\d+) (\d) (\d) \{(.*)\}$")
# A net name as drawn — either a net-label or a port pin (ipin/opin/iopin).
_NAMED_NET = re.compile(r"^C \{devices/(?:lab_wire|ipin|opin|iopin)\.sym\}.* lab=(\S+?)\}$")


def _named_nets(sch_text: str) -> set[str]:
    """Every net named in the schematic via a net-label or a port pin."""
    return {m.group(1) for line in sch_text.splitlines() if (m := _NAMED_NET.match(line))}


def _place_for_wiring(circuit, sym_lib, placer):
    """Resolve + place a circuit the way ``build_sch`` does, returning the PlacedDevice list."""
    placed = []
    placement = placer.place(circuit, sym_lib)
    for dev in circuit.devices:
        symref = symref_for(dev, pdk="ihp-sg13g2")
        sym = sym_lib.load(symref) if symref else None
        if sym is None:
            continue
        aligned = align_pins(dev, sym)
        if any(p not in aligned for p in dev.pins):
            continue
        placed.append(
            PlacedDevice(
                ref=dev.ref,
                transform=placement[dev.ref],
                nets=dev.nets,
                aligned=aligned,
                is_source=dev.kind in (DeviceKind.VSOURCE, DeviceKind.ISOURCE),
            )
        )
    return placed


def test_mixed_devices_golden(sym_lib):
    # The golden pins the deterministic grid + all-labels mode (placement-independent emitter check).
    circuit = from_file(FIXTURES / "mixed_devices.spice", name="mixed_devices")
    text = to_sch(
        circuit,
        pdk="ihp-sg13g2",
        lib=sym_lib,
        placer=GridPlacer(),
        wiring="labels",
        title="mixed_devices",
    )
    assert text == GOLDEN.read_text(), (
        "emit output drifted from the golden; if intentional, regenerate "
        "tests/fixtures/golden/mixed_devices.sch"
    )


def test_params_suppressed_by_default_only_swaps_the_symbol(sym_lib):
    """Default suppresses param text: devices use clean ``_np`` symbol twins. The *only* difference
    from ``--show-params`` is the symref — placement, attributes and wiring are byte-identical, so the
    instance still carries the values for netlisting and connectivity is unchanged."""
    circuit = from_file(FIXTURES / "ota-improved.spice")
    sup = build_sch(circuit, lib=sym_lib)  # default: suppress
    full = build_sch(circuit, lib=sym_lib, show_device_params=True)
    assert "devices/sg13_lv_nmos_np.sym" in sup.text and "sg13g2_pr/" not in sup.text
    assert "sg13g2_pr/sg13_lv_nmos.sym" in full.text and "_np.sym" not in full.text
    # The model/w/l attributes are still in the suppressed instance lines (only the symbol is clean).
    assert "model=" in sup.text and "w=" in sup.text
    # Blanking the leading {symref} of every component leaves the two outputs identical.
    def blank(t: str) -> str:
        return re.sub(r"^(C )\{[^}]*\}", r"\1{}", t, flags=re.M)

    assert blank(sup.text) == blank(full.text)
    assert (sup.device_count, sup.wire_count, sup.label_count) == (
        full.device_count, full.wire_count, full.label_count
    )


def test_clean_symbol_drops_param_text_keeps_pins_and_netlist(sym_lib):
    from spicexplorer_netlist2xschem.symbol_gen import clean_symbol

    src = (sym_lib.resolve("sg13g2_pr/sg13_lv_nmos.sym")).read_text()
    cleaned = clean_symbol(src)
    assert "T {w=@w}" not in cleaned and "T {@model}" not in cleaned  # display text gone
    assert "B 5" in cleaned  # pins kept
    assert "format=" in cleaned and "@w" in cleaned  # K-block netlist format kept (uses @w)
    assert "T {@name}" in cleaned  # the instance-name label stays


def test_mixed_devices_maps_all_six(sym_lib):
    circuit = from_file(FIXTURES / "mixed_devices.spice")
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib, placer=GridPlacer(), wiring="labels")
    assert doc.device_count == 6  # XM1, XM2, R1, C1, V1, I1
    assert doc.warnings == ()
    # labels mode: 2 MOS × 4 pins + 4 two-terminal × 2 pins = 16 labels, no wires
    assert doc.label_count == 16
    assert doc.wire_count == 0


def test_topology_hybrid_default_wires_and_rails(sym_lib):
    """Default mode (topology + hybrid) wires signal nets, draws VDD/VSS rails, names every net."""
    circuit = from_file(FIXTURES / "ota-improved.spice")  # telescopic cascode, flat, all-MOS
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib, title="ota")
    assert doc.warnings == ()
    assert doc.device_count == len(circuit.devices)
    assert doc.wire_count > 0  # signal nets are drawn as wires, not just labels
    assert doc.port_count > 0  # circuit I/O drawn as port pins
    named = _named_nets(doc.text)
    assert "vdd" in named and "vss" in named  # supply rails labelled
    assert not (set(circuit.nets) - named), "every net is named at least once"


@pytest.mark.parametrize(
    ("fixture", "kw"),
    [
        ("ota-5t_tb-ac.spice", {"into": "xota"}),
        ("ota-improved.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
    ],
)
def test_hybrid_wiring_is_connectivity_safe(sym_lib, fixture, kw):
    """The planner's invariant: after the verifier drops conflicts, no wire merges two nets.

    A host-side proxy for the Docker round-trip — reconstructs the placed devices, plans the wiring,
    then checks that the emitted wires + every device pin + label + port pin form net-homogeneous
    components (``contaminated_nets`` empty).
    """
    circuit = from_file(FIXTURES / fixture, **kw)
    placed = _place_for_wiring(circuit, sym_lib, TopologyPlacer())
    info = analyze(circuit)
    plan = plan_connections(placed, supply=circuit.supply, port_role=info.port_role)

    segs = [Seg(w.x1, w.y1, w.x2, w.y2, "") for w in plan.wires]
    terminals = [
        Terminal(*apply_transform(pd.transform, sp.x, sp.y), pd.nets[c])
        for pd in placed
        for c, sp in pd.aligned.items()
    ]
    terminals += [Terminal(lbl.x, lbl.y, lbl.lab) for lbl in plan.labels]
    terminals += [Terminal(p.x, p.y, p.net) for p in plan.ports]
    assert plan.wires, "expected some wiring"
    assert contaminated_nets(segs, terminals) == set(), "emitted wiring would short two nets"


def _nonbranching_dots(wires) -> int:
    """Count points where three-plus wire ends coincide yet every incident segment is collinear — an
    xschem solder dot drawn on a *straight* run, the clutter the collinear-merge pass removes. A genuine
    corner or T (segments on two axes) is a real junction and not counted."""
    from collections import defaultdict

    deg: dict[tuple[int, int], int] = defaultdict(int)
    axes: dict[tuple[int, int], set[str]] = defaultdict(set)
    pts = {p for w in wires for p in ((w.x1, w.y1), (w.x2, w.y2))}
    for w in wires:
        a = "v" if w.x1 == w.x2 else "h"
        for p in ((w.x1, w.y1), (w.x2, w.y2)):
            deg[p] += 1
            axes[p].add(a)
    for px, py in pts:  # a wire passing through a point's interior contributes two more ends + its axis
        for w in wires:
            if w.x1 == w.x2 == px and min(w.y1, w.y2) < py < max(w.y1, w.y2):
                deg[(px, py)] += 2
                axes[(px, py)].add("v")
            elif w.y1 == w.y2 == py and min(w.x1, w.x2) < px < max(w.x1, w.x2):
                deg[(px, py)] += 2
                axes[(px, py)].add("h")
    return sum(1 for p, d in deg.items() if d >= 3 and len(axes[p]) == 1)


@pytest.mark.parametrize(
    ("fixture", "kw"),
    [
        ("ota-5t_tb-ac.spice", {"into": "xota"}),
        ("ota-improved.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
    ],
)
def test_no_solder_dots_on_straight_wires(sym_lib, fixture, kw):
    """``_merge_collinear`` coalesces each terminal's (collinear) boundary-box lead and every split run
    back into one wire, so xschem draws a solder dot only where a net genuinely branches — never piled
    onto a straight drain/source column or gate bus (the dense-dot clutter)."""
    from spicexplorer_netlist2xschem.wiring import Wire

    circuit = from_file(FIXTURES / fixture, **kw)
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib)
    wires = [
        Wire(*map(int, line.split()[1:5]))
        for line in doc.text.splitlines()
        if line.startswith("N ")
    ]
    assert _nonbranching_dots(wires) == 0, "a solder dot landed on a straight (non-branching) wire"


def test_merge_collinear_coalesces_a_split_overlapping_run():
    """The pass unions touching/overlapping collinear segments (a lead abutting its bus, a run split at
    each tap) into maximal wires and drops degenerate points, leaving foreign-axis wires untouched."""
    from spicexplorer_netlist2xschem.wiring import Wire, _merge_collinear

    merged = _merge_collinear(
        [
            Wire(0, 0, 0, 30),  # a lead
            Wire(0, 30, 0, 60),  # abutting bus piece
            Wire(0, 50, 0, 100),  # overlapping bus piece
            Wire(0, 40, 40, 40),  # a real branch (perpendicular) — must survive on its own axis
            Wire(20, 20, 20, 20),  # degenerate point — dropped
        ]
    )
    verticals = sorted((w.y1, w.y2) for w in merged if w.x1 == w.x2 and w.x1 == 0)
    assert verticals == [(0, 100)], "the collinear pieces did not coalesce into one run"
    assert any(w.y1 == w.y2 == 40 for w in merged), "the perpendicular branch was lost"
    assert all(not (w.x1 == w.x2 and w.y1 == w.y2) for w in merged), "a degenerate point survived"


@pytest.mark.parametrize(
    ("fixture", "kw"),
    [
        ("mixed_devices.spice", {}),
        ("folded_cascode.spice", {"into": "XDUT"}),
        ("ota-improved.spice", {}),
    ],
)
def test_sources_named_in_place_not_wired(sym_lib, fixture, kw):
    """Independent V/I sources connect by net name only: each terminal is named where the source sits,
    and no routing wire ever reaches a source pin (at most its own short label stub touches it). The
    rest of each net is still wired among its non-source pins (the connectivity-safe test covers that)."""
    from spicexplorer_netlist2xschem.wiring import _LABEL_STUB

    circuit = from_file(FIXTURES / fixture, **kw)
    placed = _place_for_wiring(circuit, sym_lib, PhasedPlacer())
    info = analyze(circuit)
    plan = plan_connections(placed, supply=circuit.supply, port_role=info.port_role)

    source_pins = [
        (pd.nets[c], *apply_transform(pd.transform, sp.x, sp.y))
        for pd in placed
        if pd.is_source
        for c, sp in pd.aligned.items()
    ]
    assert source_pins, f"{fixture}: expected at least one source pin"
    labels_for: dict[str, list[tuple[int, int]]] = {}
    for lbl in plan.labels:
        labels_for.setdefault(lbl.lab, []).append((lbl.x, lbl.y))
    for net, px, py in source_pins:
        # (1) named in place: a label for this net sits within a label stub's reach of the source pin.
        assert any(
            abs(lx - px) + abs(ly - py) <= _LABEL_STUB + 4 for lx, ly in labels_for.get(net, [])
        ), f"{fixture}: source terminal on {net!r} at ({px},{py}) was not named in place"
        # (2) never wired: no drawn wire that touches the pin is longer than a label stub (so the only
        # thing attached to a source terminal is its own name, never a route into the circuit).
        for w in plan.wires:
            if (w.x1, w.y1) == (px, py) or (w.x2, w.y2) == (px, py):
                assert abs(w.x2 - w.x1) + abs(w.y2 - w.y1) <= _LABEL_STUB, (
                    f"{fixture}: a routing wire reaches the source pin on {net!r} at ({px},{py})"
                )


def test_every_net_is_labelled_ota_improved(sym_lib):
    """Each device pin gets a net-name label; assert every net in the circuit is represented."""
    circuit = from_file(FIXTURES / "ota-improved.spice")
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib)
    assert doc.warnings == (), doc.warnings
    missing = set(circuit.nets) - _named_nets(doc.text)
    assert not missing, f"nets without a label: {sorted(missing)}"


def test_subckt_descent_ota_5t(sym_lib):
    circuit = from_file(FIXTURES / "ota-5t_tb-ac.spice", into="xota", name="ota-5t")
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib)
    assert doc.device_count == 13  # the 13 XM* inside .subckt ota-5t
    assert doc.warnings == ()


def test_instances_are_wellformed(sym_lib):
    circuit = from_file(FIXTURES / "mixed_devices.spice")
    doc = build_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib)
    instance_lines = [ln for ln in doc.text.splitlines() if ln.startswith("C {")]
    assert instance_lines, "no instances emitted"
    for ln in instance_lines:
        m = _INSTANCE.match(ln)
        assert m is not None, f"malformed instance line: {ln}"
        assert m.group(1).endswith(".sym")
        assert "name=" in m.group(6)


def test_mos_instance_name_strips_x_prefix(sym_lib):
    """IHP MOS symbols carry spiceprefix=X, so the instance name drops the leading X (XM1→M1)."""
    circuit = from_file(FIXTURES / "mixed_devices.spice")
    text = to_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib)
    assert "name=M1 model=sg13_lv_nmos spiceprefix=X" in text
    assert "name=M2 model=sg13_lv_pmos spiceprefix=X" in text
    # passives keep their ref as-is (no spiceprefix)
    assert "name=R1 value=10k" in text


@pytest.mark.parametrize("net", ["out", "in", "vdd", "0"])
def test_known_nets_labelled(sym_lib, net):
    circuit = from_file(FIXTURES / "mixed_devices.spice")
    text = to_sch(circuit, pdk="ihp-sg13g2", lib=sym_lib)
    assert f"lab={net}" in text or f'lab="{net}"' in text
