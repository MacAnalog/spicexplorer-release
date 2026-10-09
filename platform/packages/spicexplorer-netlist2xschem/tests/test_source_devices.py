"""Behavioural and controlled sources survive ingest, and a subckt instance keeps its parameters.

Two defects a design repo had to work around by hand:

* ``B`` / ``E`` / ``G`` / ``F`` / ``H`` cards were **dropped on ingest** ("unrecognized device
  prefix"), so a bench whose stimulus or whose model IS a behavioural source drew a sheet with
  the source missing — a drawing that netlists to a different circuit, silently.
* a subcircuit instance's ``w=…``/``l=…``/``m=…`` never reached the drawn instance, so the sheet
  netlisted the call with **no parameters** — every sized device back at its model default.
"""

from __future__ import annotations

import pytest
from spicexplorer_netlist2xschem.ingest import DeviceKind, from_string
from spicexplorer_netlist2xschem.mapping import symref_for

DECK = """* behavioural + controlled sources
R1 in mid 1k
B1 out 0 v=v(mid)*2
G1 out2 0 in 0 1m
E1 out3 0 in 0 2
F1 out4 0 V1 3
H1 out5 0 V1 4
V1 in 0 dc 1
XSUB in out sub w=3u l=0.5u m=2
.subckt sub a b
R9 a b 1k
.ends
.end
"""


@pytest.fixture
def circuit():
    return from_string(DECK, name="srcs")


def _by_ref(circuit) -> dict:
    return {d.ref.upper(): d for d in circuit.devices}


def test_a_behavioural_source_is_ingested_not_dropped(circuit):
    d = _by_ref(circuit)["B1"]
    assert d.kind is DeviceKind.BSOURCE
    assert d.nets == {"P": "out", "N": "0"}


def test_a_voltage_controlled_source_keeps_all_four_nets(circuit):
    for ref, out in (("G1", "out2"), ("E1", "out3")):
        d = _by_ref(circuit)[ref]
        assert d.kind is DeviceKind.BSOURCE
        assert d.nets == {"P": out, "N": "0", "CP": "in", "CN": "0"}


def test_a_current_controlled_source_is_two_terminal(circuit):
    for ref, out in (("F1", "out4"), ("H1", "out5")):
        d = _by_ref(circuit)[ref]
        assert d.kind is DeviceKind.BSOURCE
        assert d.nets == {"P": out, "N": "0"}


def test_every_source_kind_resolves_to_its_own_symbol(circuit):
    want = {
        "B1": "devices/bsource.sym",
        "E1": "devices/vcvs.sym",
        "G1": "devices/vccs.sym",
        "F1": "devices/cccs.sym",
        "H1": "devices/ccvs.sym",
    }
    by_ref = _by_ref(circuit)
    for ref, sym in want.items():
        assert symref_for(by_ref[ref], pdk="ihp-sg13g2") == sym, ref


def test_the_nets_of_a_behavioural_source_reach_the_circuit(circuit):
    """A dropped card also drops its nets — the sheet then has no `out` at all."""
    for net in ("out", "out2", "out3", "out4", "out5"):
        assert net in circuit.nets, net


def test_a_subckt_instance_keeps_its_parameters(circuit):
    d = _by_ref(circuit)["XSUB"]
    assert d.kind is DeviceKind.SUBCKT
    assert {k.lower(): str(v) for k, v in d.params.items()} == {"w": "3u", "l": "0.5u", "m": "2"}


# ------------------------------------------------------ the generated block symbol ----


def _body_extent(text: str) -> tuple[float, float]:
    """(width, height) of the symbol body rectangle."""
    import re

    xs: list[float] = []
    ys: list[float] = []
    for ln in text.splitlines():
        if not ln.startswith("L "):
            continue
        n = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", ln)][1:]
        if len(n) >= 4:
            xs += [n[0], n[2]]
            ys += [n[1], n[3]]
    return max(xs) - min(xs), max(ys) - min(ys)


@pytest.mark.parametrize("n", [2, 4, 8, 9, 12, 20])
def test_a_block_symbol_is_never_taller_than_it_is_wide(n: int):
    """At nine same-side pins the body used to grow only in HEIGHT: the parent then reaches it
    with vertical stubs instead of horizontal ones, and two net labels land on top of each other.
    A body at least as wide as it is tall keeps the stubs horizontal whatever the pin count."""
    from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

    sym = generate_block_symbol("blk", [BlockPin(net=f"p{i}", side="left") for i in range(n)])
    w, h = _body_extent(sym.text)
    assert w >= h, f"{n} pins: {w} x {h}"


def test_every_pin_still_gets_its_own_coordinate():
    from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

    sym = generate_block_symbol("blk", [BlockPin(net=f"p{i}", side="left") for i in range(9)])
    assert len(sym.pins) == 9
    assert len(set(sym.pins.values())) == 9


def test_a_generated_subckt_symbol_netlists_its_instance_parameters():
    """`format="@name @pinlist @symname"` netlists the CALL with no parameters at all, so every
    sized device silently falls back to its model default."""
    from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

    sym = generate_block_symbol(
        "sub", [BlockPin(net="a", side="left"), BlockPin(net="b", side="right")]
    )
    fmt = next(ln for ln in sym.text.splitlines() if "format=" in ln)
    assert "@params" in fmt, fmt
    # The template must NOT declare an empty `params=`: xschem then emits a malformed call and
    # the hierarchy stops round-tripping (test_hierarchy catches it). An ABSENT attribute
    # expands to nothing, which is what a parameterless instance needs.
    tmpl = next(ln for ln in sym.text.splitlines() if "template=" in ln)
    assert "params=" not in tmpl, tmpl
