"""Device→symbol mapping + canonical-pin → symbol-pin alignment.

The alias tables are the one place a silent mis-wire can hide, so every primitive pin is asserted to
align to a real symbol pin, and the subckt name/positional fallback is exercised.
"""

import pytest
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


def test_symref_for_unknown_polarity_is_none():
    """Polarity is what selects the symbol; without it there is nothing to draw."""
    unk = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.UNKNOWN)
    assert symref_for(unk, pdk="ihp-sg13g2") is None
    assert symref_for(unk, pdk="some-other-pdk") is None


def test_symref_for_an_unvendored_pdk_falls_back_to_the_generic_mos_symbols():
    """A commercial kit's symbols cannot be vendored, so its MOSFETs draw with xschem's generics.

    Before this fallback they resolved to None and were skipped, which emitted an EMPTY sheet for a
    netlist full of transistors. The model name rides the instance, so identity still holds.
    """
    nmos = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.NMOS)
    pmos = _dev(DeviceKind.MOS, ("DRAIN", "GATE", "SOURCE", "BULK"), MosPolarity.PMOS)
    assert symref_for(nmos, pdk="some-other-pdk") == "devices/nmos4.sym"
    assert symref_for(pmos, pdk="some-other-pdk") == "devices/pmos4.sym"
    assert symref_for(nmos, pdk=None) == "devices/nmos4.sym"
    # a vendored PDK still wins over the fallback
    assert symref_for(nmos, pdk="ihp-sg13g2") == "sg13g2_pr/sg13_lv_nmos.sym"


def test_symref_for_generics():
    assert symref_for(_dev(DeviceKind.RES, ("P", "N")), pdk=None) == "devices/res.sym"
    assert symref_for(_dev(DeviceKind.CAP, ("P", "N")), pdk=None) == "devices/capa.sym"
    assert symref_for(_dev(DeviceKind.IND, ("P", "N")), pdk=None) == "devices/ind.sym"
    assert symref_for(_dev(DeviceKind.VSOURCE, ("P", "N")), pdk=None) == "devices/vsource.sym"
    assert symref_for(_dev(DeviceKind.ISOURCE, ("P", "N")), pdk=None) == "devices/isource.sym"


def test_symref_for_subckt_is_none():
    assert symref_for(_dev(DeviceKind.SUBCKT, ("a", "b", "c")), pdk="ihp-sg13g2") is None


def test_register_subckt_symbol_makes_the_instance_drawable():
    """A design's own subcircuit (e.g. a bench sheet's ``XDUT ... my_cell``) has no PDK-table entry,
    so ``symref_for`` returns ``None`` and the instance is dropped from the drawing with a warning --
    the one instance a testbench exists to show. ``register_subckt_symbol`` is the public way to add
    one, keyed by (pdk, model)."""
    from spicexplorer_netlist2xschem.mapping import register_subckt_symbol

    dev = _dev(DeviceKind.SUBCKT, ("a", "b", "c"), model="ldo_ihp_capless")
    assert symref_for(dev, pdk="test-pdk-p3") is None  # not registered yet

    register_subckt_symbol("test-pdk-p3", "ldo_ihp_capless", "ldo_ihp_capless.sym")
    assert symref_for(dev, pdk="test-pdk-p3") == "ldo_ihp_capless.sym"

    # model matching is case-insensitive, mirroring the rest of symref_for
    dev_upper = _dev(DeviceKind.SUBCKT, ("a", "b", "c"), model="LDO_IHP_CAPLESS")
    assert symref_for(dev_upper, pdk="test-pdk-p3") == "ldo_ihp_capless.sym"


def test_register_subckt_symbol_is_idempotent_but_rejects_a_conflicting_reregistration():
    from spicexplorer_netlist2xschem.mapping import register_subckt_symbol

    register_subckt_symbol("test-pdk-p3-conflict", "my_cell", "my_cell.sym")
    register_subckt_symbol("test-pdk-p3-conflict", "my_cell", "my_cell.sym")  # same pair: no-op

    with pytest.raises(ValueError, match="my_cell"):
        register_subckt_symbol("test-pdk-p3-conflict", "my_cell", "other_symbol.sym")


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


@pytest.mark.parametrize("ref,symref", [("E1", "devices/vcvs.sym"), ("G1", "devices/vccs.sym")])
def test_a_controlled_source_aligns_its_controlling_pair_too(sym_lib, ref, symref):
    """E/G/F/H carry a CONTROLLING pair on top of their two output terminals.

    The generic symbols name that pair ``cp``/``cm``; ingest's canonical names are ``CP``/``CN``.
    With only the two-terminal alias table, ``CN`` matched nothing, the alignment came back
    incomplete and the caller dropped the device — so a testbench sheet lost every balun,
    behavioural CMFB and Gm stage on it, each with a warning and a drawing of another circuit.
    """
    dev = Device(
        ref=ref,
        kind=DeviceKind.BSOURCE,
        model="2",
        polarity=MosPolarity.UNKNOWN,
        pins=("P", "N", "CP", "CN"),
        nets={"P": "out", "N": "0", "CP": "in", "CN": "0"},
        params={},
    )
    aligned = align_pins(dev, sym_lib.load(symref))
    assert {c: p.name for c, p in aligned.items()} == {"P": "p", "N": "m", "CP": "cp", "CN": "cm"}
    assert set(aligned) == set(dev.pins), "an incomplete alignment makes the caller skip the device"


def test_subckt_positional_fallback(sym_lib):
    # a subckt instance with formal ports that don't match the symbol's pin names → positional
    sub = _dev(DeviceKind.SUBCKT, ("portA", "portB"))
    res_sym = sym_lib.load("devices/res.sym")  # pins P/M; names won't match portA/portB
    aligned = align_pins(sub, res_sym)
    # positional: portA -> first pin (P), portB -> second pin (M)
    assert aligned["portA"].name == "P"
    assert aligned["portB"].name == "M"


# --- PDK primitives shipped as 3-node subckts drawn with a 2-pin symbol ----------------------


def _rdev(model="rhigh", nets=("a", "b", "sub")):
    return Device(
        ref="XR1",
        kind=DeviceKind.SUBCKT,
        model=model,
        polarity=MosPolarity.UNKNOWN,
        pins=("1", "2", "3"),
        nets={"1": nets[0], "2": nets[1], "3": nets[2]},
        params={"w": "0.5u", "l": "340u"},
    )


def test_symref_for_ihp_poly_resistor_subckts():
    for model in ("rhigh", "rppd", "rsil", "RHIGH"):
        assert symref_for(_rdev(model), pdk="ihp-sg13g2") == f"sg13g2_pr/{model.lower()}.sym"
    assert symref_for(_rdev("mysub"), pdk="ihp-sg13g2") is None  # unknown subckt: still no symbol
    assert symref_for(_rdev("rhigh"), pdk="sky130A") is None


def test_body_pin_is_the_extra_net_and_is_never_wired(sym_lib):
    from spicexplorer_netlist2xschem.mapping import body_pin

    sym = sym_lib.load("sg13g2_pr/rhigh.sym")
    assert sym is not None and len(sym.pins) == 2
    dev = _rdev()
    assert body_pin(dev, sym) == "3"
    aligned = align_pins(dev, sym)
    assert set(aligned) == {"1", "2"}  # the substrate node is an attribute, not a pin
    # Positional order is the .sym FILE order (M then P), because that is the order xschem's
    # netlister writes @pinlist in — verified by the round-trip test in test_render.py, which
    # fails with the terminals swapped if `pinnumber` (P=1, M=2) is used instead.
    assert aligned["1"].name == "M" and aligned["2"].name == "P"


def test_body_pin_is_none_for_a_matching_pin_count_and_for_a_bodyless_symbol(sym_lib):
    from spicexplorer_netlist2xschem.mapping import body_pin

    rhigh = sym_lib.load("sg13g2_pr/rhigh.sym")
    two_net = Device(
        "XR1", DeviceKind.SUBCKT, "rhigh", MosPolarity.UNKNOWN, ("1", "2"), {"1": "a", "2": "b"}, {}
    )
    assert body_pin(two_net, rhigh) is None
    nmos = sym_lib.load("sg13g2_pr/sg13_lv_nmos.sym")
    assert nmos is not None and body_pin(_rdev(), nmos) is None  # no `body` in its template


def test_positional_subckt_alignment_uses_symbol_file_order_not_pinnumber(sym_lib):
    """rhigh.sym lists M before P but numbers them P=1, M=2. xschem's netlister writes @pinlist in
    FILE order, so the positional fallback must too — the round-trip test is the proof."""
    rhigh = sym_lib.load("sg13g2_pr/rhigh.sym")
    assert [p.name for p in rhigh.pins] == ["M", "P"]
    aligned = align_pins(_rdev(), rhigh)
    assert [aligned[c].name for c in ("1", "2")] == [p.name for p in rhigh.pins[:2]]


def test_pdk_two_net_primitives_prefer_the_pdk_symbol_over_the_generic_one():
    """`XCFF a b cap_cmim` is typed CAP by prefix (two nets), so without this it drew as the
    generic capa.sym and lost its sizing. The X prefix plus a known model name is what selects the
    PDK symbol; a bare `C1 a b 1p` keeps the generic one."""
    from spicexplorer_netlist2xschem import from_string
    from spicexplorer_netlist2xschem.mapping import symref_for

    (cff,) = from_string("* c\nXCFF a b cap_cmim w=7u l=7u\n.end\n").devices
    (c1,) = from_string("* c\nC1 a b 1p\n.end\n").devices
    assert symref_for(cff, pdk="ihp-sg13g2") == "sg13g2_pr/cap_cmim.sym"
    assert symref_for(c1, pdk="ihp-sg13g2") == "devices/capa.sym"
    # An unmapped PDK keeps the old generic fallback rather than becoming undrawable.
    assert symref_for(cff, pdk=None) == "devices/capa.sym"


def test_taps_are_deliberately_unmapped():
    """ntap1/ptap1 compute an `R=` from w and l in a `tcleval()` format line, so a round trip
    through them emits a resistance the input never had. Being skipped as "no symbol mapping" is
    the intended behaviour, not an oversight."""
    from spicexplorer_netlist2xschem.mapping import _PDK_SUBCKT_SYMREF

    for model in ("ntap1", "ptap1", "ntap1_ring", "ptap1_ring"):
        assert ("ihp-sg13g2", model) not in _PDK_SUBCKT_SYMREF


def test_every_mapped_pdk_symbol_can_actually_act_as_one():
    """A table entry is useless unless `is_pdk_primitive` recognises the symbol it points at — it
    needs both `model` and `spiceprefix` in the template, or the instance falls back to the generic
    single `value` slot and drops its sizing. This is what disqualified cap_cpara, whose one-line
    template `sym_library` parses into a single bogus `name` entry."""
    from pathlib import Path

    from spicexplorer_netlist2xschem.mapping import _PDK_SUBCKT_SYMREF
    from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths

    lib = SymLibrary([*default_search_paths(), Path(__file__).parent / "fixtures" / "sym"])
    checked = 0
    for (_pdk, model), symref in _PDK_SUBCKT_SYMREF.items():
        sym = lib.load(symref)
        if sym is None:
            continue  # symbol not vendored in this environment
        checked += 1
        assert "model" in sym.template, f"{model}: {symref} has no `model` in its template"
        assert "spiceprefix" in sym.template, f"{model}: {symref} has no `spiceprefix`"
    assert checked >= 5, f"only {checked} mapped symbols resolved — the check proved nothing"
