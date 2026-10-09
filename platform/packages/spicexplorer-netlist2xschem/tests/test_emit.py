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
    parse_sch,
    plan_connections,
    to_sch,
)
from spicexplorer_netlist2xschem.connectivity import Seg, Terminal
from spicexplorer_netlist2xschem.geometry import apply_transform
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity, N2XCircuit
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
        full.device_count,
        full.wire_count,
        full.label_count,
    )


def test_clean_symbol_drops_param_text_keeps_pins_and_netlist(sym_lib):
    from spicexplorer_netlist2xschem.symbol_gen import clean_symbol

    src = (sym_lib.resolve("sg13g2_pr/sg13_lv_nmos.sym")).read_text()
    cleaned = clean_symbol(src)
    assert "T {w=@w}" not in cleaned and "T {@model}" not in cleaned  # display text gone
    assert "B 5" in cleaned  # pins kept
    assert "format=" in cleaned and "@w" in cleaned  # K-block netlist format kept (uses @w)
    assert "T {@name}" in cleaned  # the instance-name label stays


def test_long_braced_expression_survives_the_full_value_not_abbreviated(sym_lib):
    """P4: ``_display_value`` used to abbreviate any attribute value over 24 characters to its tail,
    and that *abbreviated* string was written into the instance's netlisted ``w=``/``m=`` attribute --
    so a verbose braced sizing expression silently lost its front half in the schematic's own
    netlist (measured on the recertified LDO's pass device: ``w='...xmp_nf_mult}'`` against a
    certified ``w={x_dut_xmp_w/x_dut_xmp_nf_mult}``), even though the topology check (device/net
    counts) never saw it. Round-tripped through ``parse_sch`` (which mirrors xschem's own
    quote/brace unescaping) to prove the text on the wire carries the whole expression, not just the
    in-memory Python value."""
    w_expr = "{x_dut_xmp_w/x_dut_xmp_nf_mult}"
    m_expr = "{x_dut_xmp_m*x_dut_xmp_nf_mult}"
    assert len(w_expr) > 24  # exactly the "very long" case the old shortening caught
    dev = Device(
        ref="XMP",
        kind=DeviceKind.MOS,
        model="sg13_lv_pmos",
        polarity=MosPolarity.PMOS,
        pins=("DRAIN", "GATE", "SOURCE", "BULK"),
        nets={"DRAIN": "vout", "GATE": "vin", "SOURCE": "vdd", "BULK": "vdd"},
        params={"w": w_expr, "l": "0.15u", "m": m_expr},
    )
    circuit = N2XCircuit(
        name="pass_device",
        devices=(dev,),
        nets=("vout", "vin", "vdd"),
        supply={"vdd": "VDD"},
        ports=(),
    )
    doc = build_sch(
        circuit, pdk="ihp-sg13g2", lib=sym_lib, wiring="labels", show_device_params=True
    )
    sch = parse_sch(doc.text)
    inst = next(c for c in sch.components if c.attrs.get("model") == "sg13_lv_pmos")
    assert inst.attrs["w"] == w_expr
    assert inst.attrs["m"] == m_expr


def test_transient_stimulus_value_survives_the_full_string(sym_lib):
    """The actual regression the LDO bench sheets hit: a source's ``pulse(...)`` value, over 24
    characters, came back out of the netlister missing its front (``...00n 10u 20u)``) -- two of the
    13 certified bench decks were silently wrong until the deck-vs-drawing comparison caught it."""
    pulse = "pulse(0.1m 10m 1u 100n 100n 10u 20u)"
    assert len(pulse) > 24
    dev = Device(
        ref="V1",
        kind=DeviceKind.VSOURCE,
        model=pulse,
        polarity=MosPolarity.UNKNOWN,
        pins=("P", "N"),
        nets={"P": "stim", "N": "0"},
        params={},
    )
    circuit = N2XCircuit(name="bench", devices=(dev,), nets=("stim", "0"), supply={}, ports=())
    doc = build_sch(
        circuit, pdk="ihp-sg13g2", lib=sym_lib, wiring="labels", show_device_params=True
    )
    sch = parse_sch(doc.text)
    inst = next(c for c in sch.components if "vsource" in c.symref)
    assert inst.attrs["value"] == pulse


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
    for (
        px,
        py,
    ) in pts:  # a wire passing through a point's interior contributes two more ends + its axis
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


# --- PDK poly resistors: 3 nets, a 2-pin symbol, the substrate on `body=` --------------------

RESISTOR_DECK = """* poly resistors
XR1 a b sub rhigh w=0.5u l=340u
XR2 b 0 sub rppd w=1u l=10u
XSUB in out ctl mysub
M1 d g s bulk sg13_lv_nmos w=1u l=0.13u
.end
"""


def test_ihp_poly_resistor_subckt_is_drawn_with_its_body_attribute(tmp_path, sym_lib):
    from spicexplorer_netlist2xschem import from_string

    deck = tmp_path / "r.spice"
    deck.write_text(RESISTOR_DECK)
    doc = build_sch(from_string(RESISTOR_DECK), pdk="ihp-sg13g2", lib=sym_lib)
    assert doc.device_count == 3  # XR1, XR2, M1 — only the unknown XSUB is skipped
    assert [w for w in doc.warnings if "XSUB" in w] and not [w for w in doc.warnings if "XR" in w]
    r1 = next(ln for ln in doc.text.splitlines() if "rhigh.sym" in ln)
    # `format` is "@spiceprefix@name @pinlist @body @model w=@w l=@l m=@m b=@b": the name loses its
    # spiceprefix X, the substrate rides on body=, and w/l must be on the instance.
    assert "name=R1" in r1 and "model=rhigh" in r1 and "spiceprefix=X" in r1
    assert "body=sub" in r1 and "w=0.5u" in r1 and "l=340u" in r1
    r2 = next(ln for ln in doc.text.splitlines() if "rppd.sym" in ln)
    assert "name=R2" in r2 and "model=rppd" in r2 and "body=sub" in r2


def test_poly_resistor_wires_two_pins_and_keeps_the_body_net_off_the_wiring(sym_lib):
    from spicexplorer_netlist2xschem import from_string
    from spicexplorer_netlist2xschem.mapping import align_pins, symref_for

    circ = from_string("* t\nXR1 a b sub rhigh w=0.5u l=340u\n.end\n")
    dev = circ.devices[0]
    sym = sym_lib.load(symref_for(dev, pdk="ihp-sg13g2"))
    aligned = align_pins(dev, sym)
    # .sym file order (M, P) — what xschem's netlister writes @pinlist in; see test_mapping.py
    assert {c: sp.name for c, sp in aligned.items()} == {"1": "M", "2": "P"}
    assert "3" not in aligned and dev.nets["3"] == "sub"  # the substrate node is never wired


def test_body_subckt_never_invents_a_size_from_the_symbol_template(sym_lib):
    """N2: an unsized `XR1 a b sub rhigh` used to be back-filled with the SYMBOL template's
    w/l. That is the symbol author's default, not the model's — sg13g2_pr/rhigh.sym says
    l=0.5e-6 while the model library's `.subckt rhigh` defaults to l=0.96e-6 — so the emitter
    silently stated a size the netlist never gave, and the round trip produced a DIFFERENT
    device. It now omits the attribute and warns."""
    from spicexplorer_netlist2xschem import from_string

    doc = build_sch(from_string("* t\nXR1 a b sub rhigh\n.end\n"), pdk="ihp-sg13g2", lib=sym_lib)
    r1 = next(ln for ln in doc.text.splitlines() if "rhigh.sym" in ln)
    assert "body=sub" in r1 and "model=rhigh" in r1
    assert " w=" not in r1 and " l=" not in r1  # NOT 0.5e-6 from the template
    warn = " ".join(w for w in doc.warnings if "XR1" in w)
    assert "sets no w/l" in warn and "SYMBOL template's default" in warn


def test_body_subckt_carries_unknown_params_through_and_says_they_do_not_netlist(sym_lib):
    """N3: only w/l/m/b were emitted, so any other instance parameter vanished from the `.sch`
    entirely. It is kept now — the schematic can carry it — with a warning that the symbol's
    fixed `format` line still will not netlist it back."""
    from spicexplorer_netlist2xschem import from_string

    doc = build_sch(
        from_string("* t\nXR1 a b sub rhigh w=0.5u l=340u foo=3\n.end\n"),
        pdk="ihp-sg13g2",
        lib=sym_lib,
    )
    r1 = next(ln for ln in doc.text.splitlines() if "rhigh.sym" in ln)
    assert "foo=3" in r1 and "w=0.5u" in r1 and "l=340u" in r1
    warn = " ".join(w for w in doc.warnings if "XR1" in w)
    assert "'foo'" in warn and "will NOT reappear" in warn


def test_braced_param_value_is_quoted_and_escaped():
    """`V a b dc {vref_val}` must reach the .sch as `value="dc \\{vref_val\\}"`.

    Quoting alone is not enough: xschem's tokenizer takes the inner `}` for the end of the
    attribute block, drops `value` without a word (exit 0) and substitutes vsource.sym's template
    default, so the netlist came back out as `VREF vref vss 3` — a supply the schematic never
    stated. Escaping both braces is xschem's own convention for a `.param` reference.
    """
    from spicexplorer_netlist2xschem import from_string

    doc = build_sch(from_string("* v\nVREF vref vss dc {vref_val}\n.end\n", name="v"))
    line = next(ln for ln in doc.text.splitlines() if "name=VREF" in ln)
    assert 'value="dc \\{vref_val\\}"' in line, line
    assert "value=3" not in line


def test_braced_value_without_whitespace_is_still_quoted():
    """A brace forces quoting on its own — `value={vref_val}` unquoted closes the attribute block
    at the `}`, and xschem netlists the truncated `{vref_val` with the trailing brace eaten."""
    from spicexplorer_netlist2xschem.emit import _fmt_value

    assert _fmt_value("{vref_val}") == r'"\{vref_val\}"'
    assert _fmt_value("1p") == "1p"  # unchanged: no brace, no whitespace, still bare


def _pdk_lib():
    from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths

    return SymLibrary([*default_search_paths(), Path(__file__).parent / "fixtures" / "sym"])


def test_two_net_pdk_capacitor_carries_its_sizing_not_a_value_slot():
    """`XCFF a b cap_cmim w=7u l=7u m=2` has exactly two nets, so the prefix test types it a CAP
    and it never reached the subckt path that rescued rhigh: it drew as the generic capa.sym, whose
    `format` netlists only `@value @m`, so w and l were dropped on the floor. It must draw with the
    PDK's own symbol and carry model/spiceprefix/w/l/m instead."""
    from spicexplorer_netlist2xschem import from_string

    src = "* c\nXCFF a b cap_cmim w=7u l=7u m=2\n.end\n"
    doc = build_sch(from_string(src, name="c"), pdk="ihp-sg13g2", lib=_pdk_lib())
    line = next(ln for ln in doc.text.splitlines() if "name=" in ln and "cap_cmim" in ln)
    assert "sg13g2_pr/cap_cmim.sym" in line, line
    for expect in ("model=cap_cmim", "spiceprefix=X", "w=7u", "l=7u", "m=2"):
        assert expect in line, f"{expect} missing from {line}"
    assert "value=" not in line, f"still using the generic value slot: {line}"


def test_a_plain_two_terminal_capacitor_still_draws_generically():
    """The PDK-symbol preference is keyed on the X prefix + a known model name, so an ordinary
    `C1 a b 1p` is untouched: generic capa.sym, value slot, no model/spiceprefix."""
    from spicexplorer_netlist2xschem import from_string

    doc = build_sch(
        from_string("* c\nC1 a b 1p\n.end\n", name="c"), pdk="ihp-sg13g2", lib=_pdk_lib()
    )
    line = next(ln for ln in doc.text.splitlines() if "name=C1" in ln)
    assert "capa" in line and "value=1p" in line and "model=" not in line, line


def test_template_param_keys_are_read_off_each_symbol():
    """Which keys a PDK instance must carry is per-primitive, so it is derived from the symbol's
    own template rather than a hard-coded `w/l/m/b` list."""
    from spicexplorer_netlist2xschem.emit import template_param_keys

    lib = _pdk_lib()
    assert set(template_param_keys(lib.load("sg13g2_pr/cap_cmim.sym"))) == {"w", "l", "m"}
    assert set(template_param_keys(lib.load("sg13g2_pr/rhigh.sym"))) == {"w", "l", "m", "b"}
    assert set(template_param_keys(lib.load("sg13g2_pr/cap_rfcmim.sym"))) == {"w", "l", "wfeed"}


def test_pdk_instance_keeps_a_template_key_s_original_case():
    """xschem matches a `format` line's `@Nx` against the template key spelled exactly that way, so
    lowercasing it made the HBTs' `Nx=2` unmatchable and every instance netlisted back as the
    template default `Nx=1` — the sizing gone, silently, exactly like the cap_cmim case."""
    from spicexplorer_netlist2xschem import from_string
    from spicexplorer_netlist2xschem.emit import template_param_keys

    lib = _pdk_lib()
    assert template_param_keys(lib.load("sg13g2_pr/npn13G2.sym")) == ["Nx"]
    src = "* q\nXQ1 c b e s npn13G2 Nx=2\n.end\n"
    doc = build_sch(from_string(src, name="q"), pdk="ihp-sg13g2", lib=lib)
    line = next(ln for ln in doc.text.splitlines() if "npn13G2.sym" in ln)
    assert "Nx=2" in line and "nx=2" not in line, line


def test_a_commercial_kit_netlist_draws_with_the_generic_mos_symbols(sym_lib, tmp_path):
    """A PDK whose symbols cannot be vendored must still produce a full sheet, not an empty one.

    Before the generic fallback, `symref_for` returned None for every MOSFET of a kit with no
    entry in `_PDK_MOS_SYMREF`, so a ten-transistor amplifier emitted a schematic with no
    transistors in it. Three things have to hold for the drawing to be usable:

      * both polarities resolve to xschem's own 4-terminal generics;
      * the KIT's model name rides the instance, so re-netlisting reproduces the same devices;
      * NO `spiceprefix` is written. A plain SPICE MOSFET is `m1 d g s b <model> …`; the old
        default of "X" emitted `Xm1 …`, a subcircuit call, which fails netlist identity.
    """
    net = tmp_path / "commercial_pair.spice"
    net.write_text(
        "* a commercial-kit pair: models whose symbols cannot be vendored\n"
        "m1 d1 g1 0 0 nch_25 w=12u l=1u m=6\n"
        "m2 d2 g2 vdd vdd pch_25 w=28u l=1u m=14\n"
        ".end\n"
    )
    circuit = from_file(net, name="commercial_pair")
    text = to_sch(
        circuit,
        pdk="generic-n65",
        lib=sym_lib,
        placer=GridPlacer(),
        wiring="labels",
        title="commercial_pair",
        show_device_params=True,
    )

    assert "devices/nmos4.sym" in text and "devices/pmos4.sym" in text
    assert "model=nch_25" in text and "model=pch_25" in text
    assert "spiceprefix" not in text, "a generic MOSFET must netlist as `m1 …`, not `Xm1 …`"
    # the sizing must be on the instance, or xschem substitutes the symbol template's default
    assert "w=12u" in text and "l=1u" in text and "m=6" in text


def test_the_generic_mos_clean_twins_are_vendored(sym_lib):
    """The default mode swaps every device for its `_np` twin; a missing twin drops the device."""
    for stem in ("nmos4", "pmos4"):
        assert sym_lib.load(f"devices/{stem}_np.sym") is not None


# --- the parameters xschem's generic symbol would otherwise drop (issue #159) -------------

_GENERIC_LIB = None


def _generic(netlist: str) -> str:
    """Build a sheet on the GENERIC symbols and return its nmos instance line."""
    from spicexplorer_netlist2xschem import build_sch, from_string
    from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths

    doc = build_sch(
        from_string(netlist), pdk="", lib=SymLibrary(default_search_paths()), wiring="labels"
    )
    text = doc.text if hasattr(doc, "text") else str(doc)
    return next(ln for ln in text.splitlines() if "nmos4" in ln)


def test_the_finger_count_rides_into_extra_instead_of_being_dropped():
    """`w` is the TOTAL width on a commercial kit and `nf` divides it into fingers, so a
    `w=32.4747u nf=16` device drawn without the count re-netlists as a 32 um SINGLE-FINGER
    transistor — a different device, on a sheet that is supposed to BE the record."""
    line = _generic("* t\nM1 out in 0 0 nmos_lvt w=32.4747u l=0.15u nf=16 m=2\n.end\n")
    assert "extra=nf=16" in line
    assert "w=32.4747u" in line and "m=2" in line


def test_several_dropped_parameters_are_quoted_as_one_extra_string():
    line = _generic("* t\nM1 o i 0 0 nch w=32u l=0.15u nf=16 ad=1.2p sa=0.3u\n.end\n")
    assert 'extra="nf=16 ad=1.2p sa=0.3u"' in line


def test_a_parameter_the_symbol_already_netlists_is_not_duplicated_into_extra():
    """The generic format substitutes `w`, `l` and `m` by name; only what it would DROP is
    carried, so nothing is written twice and nothing is renamed."""
    line = _generic("* t\nM1 o i 0 0 nch w=1u l=0.15u m=3\n.end\n")
    assert "extra" not in line
    assert "w=1u" in line and "l=0.15u" in line and "m=3" in line


def test_a_symbol_with_no_extra_slot_carries_nothing():
    """A PDK symbol's `format` names its own fixed keys and has no `@extra`; inventing one
    would emit an attribute the symbol never substitutes."""
    from spicexplorer_netlist2xschem.emit import _extra_params
    from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity
    from spicexplorer_netlist2xschem.sym_library import Symbol

    sym = Symbol(ref="sg13g2_pr/x.sym", type="nmos", pins=(), template={"w": "1u"}, fmt="@name @w")
    dev = Device(
        ref="M1",
        kind=DeviceKind.MOS,
        model="x",
        polarity=MosPolarity.NMOS,
        pins=("d", "g", "s", "b"),
        nets={},
        params={"nf": "16"},
    )
    assert _extra_params(dev, sym) == ""
