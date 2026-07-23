"""Device→symbol mapping + canonical-pin → symbol-pin alignment.

The alias tables are the one place a silent mis-wire can hide, so every primitive pin is asserted to
align to a real symbol pin, and the subckt name/positional fallback is exercised.
"""

from spicexplorer_netlist2xschem import align_pins, symref_for
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity


def _dev(kind, pins, polarity=MosPolarity.UNKNOWN, model=None):
    return Device(
        ref="D1",
        kind=kind,
        model=model,
        polarity=polarity,
        pins=pins,
        nets={p: f"n_{p.lower()}" for p in pins},
        params={},
    )


def test_symref_for_mos_by_polarity():
    nmos = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.NMOS)
    pmos = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.PMOS)
    assert symref_for(nmos, pdk="ihp-sg13g2") == "sg13g2_pr/sg13_lv_nmos.sym"
    assert symref_for(pmos, pdk="ihp-sg13g2") == "sg13g2_pr/sg13_lv_pmos.sym"


def test_symref_for_unknown_polarity_or_pdk_is_none():
    unk = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.UNKNOWN)
    assert symref_for(unk, pdk="ihp-sg13g2") is None
    nmos = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.NMOS)
    assert symref_for(nmos, pdk="some-other-pdk") is None


def test_symref_for_generics():
    assert symref_for(_dev(DeviceKind.RES, ("P", "N")), pdk=None) == "devices/res.sym"
    assert symref_for(_dev(DeviceKind.CAP, ("P", "N")), pdk=None) == "devices/capa.sym"
    assert symref_for(_dev(DeviceKind.IND, ("P", "N")), pdk=None) == "devices/ind.sym"
    assert symref_for(_dev(DeviceKind.VSOURCE, ("P", "N")), pdk=None) == "devices/vsource.sym"
    assert symref_for(_dev(DeviceKind.ISOURCE, ("P", "N")), pdk=None) == "devices/isource.sym"


def test_symref_for_subckt_is_none():
    assert symref_for(_dev(DeviceKind.SUBCKT, ("a", "b", "c")), pdk="ihp-sg13g2") is None


def test_mos_pins_align_to_dgsb(sym_lib):
    nmos = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.NMOS)
    sym = sym_lib.load("sg13g2_pr/sg13_lv_nmos.sym")
    aligned = align_pins(nmos, sym)
    assert {c: p.name for c, p in aligned.items()} == {
        "DRAIN": "D",
        "GATE": "G",
        "SOURCE": "S",
        "BULK": "B",
    }
    # every canonical pin aligned — no silent drop
    assert set(aligned) == set(nmos.pins)


def test_resistor_aligns_P_N_to_P_M(sym_lib):
    res = _dev(DeviceKind.RES, ("P", "N"))
    aligned = align_pins(res, sym_lib.load("devices/res.sym"))
    assert {c: p.name for c, p in aligned.items()} == {"P": "P", "N": "M"}


def test_capacitor_aligns_to_lowercase(sym_lib):
    cap = _dev(DeviceKind.CAP, ("P", "N"))
    aligned = align_pins(cap, sym_lib.load("devices/capa.sym"))
    assert {c: p.name for c, p in aligned.items()} == {"P": "p", "N": "m"}


def test_subckt_positional_fallback(sym_lib):
    # a subckt instance with formal ports that don't match the symbol's pin names → positional
    sub = _dev(DeviceKind.SUBCKT, ("portA", "portB"))
    res_sym = sym_lib.load("devices/res.sym")  # pins P/M; names won't match portA/portB
    aligned = align_pins(sub, res_sym)
    # positional: portA -> first pin (P), portB -> second pin (M)
    assert aligned["portA"].name == "P"
    assert aligned["portB"].name == "M"
