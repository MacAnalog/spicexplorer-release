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
