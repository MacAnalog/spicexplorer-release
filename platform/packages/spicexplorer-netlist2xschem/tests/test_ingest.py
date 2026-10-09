"""Ingest — device typing, polarity detection across PDK naming conventions, and subckt descent."""

import pytest
from spicexplorer_netlist2xschem import DeviceKind, MosPolarity, from_string


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("sg13_lv_nmos", MosPolarity.NMOS),  # IHP
        ("sg13_lv_pmos", MosPolarity.PMOS),
        ("nmos", MosPolarity.NMOS),  # abstract / generic
        ("pmos", MosPolarity.PMOS),
        ("sky130_fd_pr__nfet_01v8", MosPolarity.NMOS),  # sky130
        ("sky130_fd_pr__pfet_01v8", MosPolarity.PMOS),
        ("nfet_03v3", MosPolarity.NMOS),  # gf180
        ("pfet_03v3", MosPolarity.PMOS),
    ],
)
def test_polarity_across_pdk_naming(model, expected):
    circ = from_string(f"XM1 d g s b {model} w=1u l=0.5u\n.end\n")
    assert circ.devices[0].kind is DeviceKind.MOS
    assert circ.devices[0].polarity is expected


def test_two_terminal_and_subckt_typing():
    circ = from_string("* t\nR1 a b 1k\nC1 b 0 1p\nV1 a 0 1\nI1 a b 1u\nXsub a b c mysub\n.end\n")
    kinds = {d.ref.upper(): d.kind for d in circ.devices}
    assert kinds["R1"] is DeviceKind.RES
    assert kinds["C1"] is DeviceKind.CAP
    assert kinds["V1"] is DeviceKind.VSOURCE
    assert kinds["I1"] is DeviceKind.ISOURCE
    assert kinds["XSUB"] is DeviceKind.SUBCKT


def test_missing_title_is_tolerated():
    # pasted netlist starting straight with a device card still parses
    circ = from_string("XM1 d g s b sg13_lv_nmos w=1u l=0.5u\n.end\n")
    assert len(circ.devices) == 1


def test_x_prefixed_primitive_with_wrong_pin_count_falls_through_to_subckt():
    """An IHP 3-net poly resistor (`XR1 a b sub rhigh …`) is typed RES by its `XR` prefix, fails
    the 2-pin check, and used to be DROPPED ("3 nets but res expects 2") instead of falling
    through to the generic `X` SUBCKT branch."""
    circ = from_string("* t\nXR1 a b sub rhigh w=0.5u l=2u\n.end\n")
    assert len(circ.devices) == 1
    d = circ.devices[0]
    assert d.kind is DeviceKind.SUBCKT and (d.model or "").lower() == "rhigh"
    assert set(d.nets.values()) == {"a", "b", "sub"}
    assert len(d.nets) == 3


def test_x_prefixed_mos_with_wrong_pin_count_falls_through_to_subckt():
    circ = from_string("* t\nXM1 d g s mysub w=1u\n.end\n")
    assert len(circ.devices) == 1
    assert circ.devices[0].kind is DeviceKind.SUBCKT
    assert set(circ.devices[0].nets.values()) == {"d", "g", "s"}


def test_x_prefixed_primitives_with_the_right_pin_count_stay_primitives():
    """The fall-through must not reclassify: a 4-net XM1 is still a MOSFET, a 2-net XR1 a RES."""
    circ = from_string("* t\nXM1 d g s b sg13_lv_nmos w=1u l=0.5u\nXR1 a b rhigh w=1u\n.end\n")
    kinds = {d.ref: d.kind for d in circ.devices}
    assert kinds == {"XM1": DeviceKind.MOS, "XR1": DeviceKind.RES}


def test_non_x_primitives_with_a_bad_pin_count_are_still_skipped():
    """Only an `X` ref may be a subcircuit instance: a 3-net `M1` is still dropped, and a plain
    2-net `R1` still ingests as RES. (`R1 a b c` cannot reach the pin-count check — spicelib reads
    the third token as the resistor's VALUE, so it arrives with two nodes.)"""
    circ = from_string("* t\nM1 d g s sg13_lv_nmos\nR1 a b 1k\nR2 a b c\n.end\n")
    assert [d.ref for d in circ.devices] == ["R1", "R2"]
    assert {d.kind for d in circ.devices} == {DeviceKind.RES}


def test_the_analog_and_digital_rail_spellings_are_classified():
    """A commercial-kit design's sheets were drawn with NO rail at all, because `avdd`/`agnd` —
    what a real mixed-signal deck calls them — fell through to "not a supply" (issue #159)."""
    from spicexplorer_netlist2xschem.ingest import _classify_supply

    assert _classify_supply("avdd") == "VDD"
    assert _classify_supply("AVDD_1V2") == "VDD"
    assert _classify_supply("agnd") == "GND"
    assert _classify_supply("gnd!") == "GND"  # the Cadence global marker carries no role
    assert _classify_supply("vdd!") == "VDD"
    assert _classify_supply("avss") == "VSS"
    assert _classify_supply("out") is None and _classify_supply("vbias") is None


def test_a_sources_whole_stimulus_survives_ingest_and_reaches_the_sheet():
    """Issue #223 reported the waveform being dropped at ingest, leaving the sheet showing
    ``value=0``. It is NOT dropped on this package's path: a SPICE ``V1 a 0 PULSE(…)`` card lands
    whole in ``Device.model``, which is the slot ``emit`` writes into ``value=`` and ``vsource.sym``
    draws as ``@value``. This test keeps that true — placement now SIZES a source's text lane from
    that string, so losing it would silently un-fix #223 rather than fail loudly.
    """
    spec = "PULSE(0 1.8 120.5n 100.25p 100.25p 666.125n 1332.25n)"
    circuit = from_string(f"* bench\nV1 a 0 {spec}\nI1 b 0 SIN(0 1m 1MEG)\nR1 a b 1k\n.end\n")
    by_ref = {d.ref: d for d in circuit.devices}
    assert by_ref["V1"].model == spec
    assert by_ref["I1"].model == "SIN(0 1m 1MEG)"
