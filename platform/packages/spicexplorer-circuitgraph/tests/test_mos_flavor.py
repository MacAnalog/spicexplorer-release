"""Multi-flavor MOS lowering: a DUT that binds two NMOS (or PMOS) threshold flavors retargets each
instance to its own PDK model via the abstract token (``nmos`` vs ``nmos_hv``). Enables the ΔVth
voltage-reference class member; before this the emit collapsed every nmos to the first-per-polarity
(lv) model."""

import logging

import pytest
from spicexplorer_circuitgraph import (
    GF180MCU,
    IHP_SG13G2,
    SKYWATER_SKY130,
    TSMC_N65,
    CircuitGraph,
    PdkDevice,
    model_flavor,
    mos_flavor,
    split_flavor,
    to_netlist,
)
from spicexplorer_circuitgraph.model.nodes import DeviceType, MosPolarityType
from spicexplorer_core.spice_engine import NetlistView


def test_mos_flavor_helper():
    assert mos_flavor("nmos") == ""
    assert mos_flavor("pmos") == ""
    assert mos_flavor("nmos_hv") == "hv"
    assert mos_flavor("pmos_io") == "io"
    assert mos_flavor("NMOS_HV") == "hv"  # case-insensitive
    assert mos_flavor(None) == ""
    assert mos_flavor("sg13_hv_nmos") == ""  # a PDK model name is not an abstract flavor token


def test_model_for_flavor_and_default_fallback():
    mos, nmos = DeviceType.MOS, MosPolarityType.NMOS
    # default (no flavor) stays byte-identical: the first/core (lv) device
    assert IHP_SG13G2.model_for(mos, nmos) == "sg13_lv_nmos"
    assert IHP_SG13G2.model_for(mos, nmos, "") == "sg13_lv_nmos"
    # an explicit flavor resolves the flavored model
    assert IHP_SG13G2.model_for(mos, nmos, "hv") == "sg13_hv_nmos"
    assert IHP_SG13G2.model_for(mos, MosPolarityType.PMOS, "hv") == "sg13_hv_pmos"
    # an absent NON-EMPTY flavor resolves to nothing. It used to fall back to the core device,
    # which is a silent voltage-class change: the caller asked for a part this table does not
    # have and got a different one, with the same confidence as a real hit.
    assert IHP_SG13G2.model_for(mos, nmos, "zzz") is None


def test_two_flavors_lower_in_one_dut():
    """The ΔVth reference: a Vgs=0 lv source over an hv diode, both NMOS, in ONE subckt."""
    netlist = (
        "* delta-Vth ref\n"
        "XM0 vdd vref vref vss nmos w=2.5u l=2u\n"
        "XM1 vref vref vss vss nmos_hv w=1u l=2u\n"
        ".end\n"
    )
    g = CircuitGraph.from_netlist(NetlistView.from_string(netlist))
    lowered = to_netlist(g, pdk=IHP_SG13G2)
    assert "sg13_lv_nmos" in lowered  # XM0 (default flavor) -> lv
    assert "sg13_hv_nmos" in lowered  # XM1 (hv flavor)      -> hv
    # each instance keeps its own model (the collapse regression would map both to lv)
    xm0 = next(ln for ln in lowered.splitlines() if ln.startswith("XM0"))
    xm1 = next(ln for ln in lowered.splitlines() if ln.startswith("XM1"))
    assert "sg13_lv_nmos" in xm0 and "sg13_hv_nmos" not in xm0
    assert "sg13_hv_nmos" in xm1 and "sg13_lv_nmos" not in xm1


def test_flavor_field_default_is_empty():
    assert PdkDevice("m", DeviceType.MOS, MosPolarityType.NMOS).flavor == ""
    assert PdkDevice("m", DeviceType.MOS, MosPolarityType.NMOS, flavor="hv").flavor == "hv"


# --- cross-PDK retargeting must carry the voltage class -------------------------------------
def test_model_flavor_reads_the_pdk_declaration_not_the_spelling():
    # `mos_flavor` parses the ABSTRACT token; a PDK model name spells its class its own way, so
    # only the device table knows. Retargeting consults `model_flavor`, which reads the table.
    assert model_flavor("sg13_hv_nmos") == "hv"
    assert model_flavor("sg13_lv_nmos") == ""
    assert model_flavor("SG13_HV_PMOS") == "hv"  # classification is case-insensitive
    assert model_flavor("nmos_hv") == "hv"  # unregistered token → the abstract convention
    assert model_flavor("some_unknown_model") == ""
    assert model_flavor(None) == ""


def _hv_nmos_graph() -> CircuitGraph:
    return CircuitGraph.from_netlist(
        NetlistView.from_string("* hv\nM1 d g s 0 sg13_hv_nmos w=10u l=0.5u\n.end\n")
    )


def test_hv_device_retargets_to_the_targets_hv_part_not_its_core_part():
    """A 3.3 V IHP device must never come out as sky130's 1.8 V core model."""
    lowered = to_netlist(_hv_nmos_graph(), pdk=SKYWATER_SKY130)
    assert "sky130_fd_pr__nfet_g5v0d10v5" in lowered
    assert "nfet_01v8" not in lowered

    lowered_gf = to_netlist(_hv_nmos_graph(), pdk=GF180MCU)
    assert "nfet_06v0" in lowered_gf and "nfet_03v3" not in lowered_gf


def test_retarget_refuses_a_flavor_the_target_pdk_does_not_have():
    # TSMC-N65's table declares core devices only. Silently emitting `nch_lvt` for a 3.3 V part
    # produces a deck that simulates happily and answers a different circuit.
    with pytest.raises(ValueError, match="voltage class"):
        to_netlist(_hv_nmos_graph(), pdk=TSMC_N65)


def test_core_devices_still_retarget_unchanged():
    g = CircuitGraph.from_netlist(
        NetlistView.from_string("* lv\nM1 d g s 0 sg13_lv_nmos w=10u l=0.5u\n.end\n")
    )
    assert "sky130_fd_pr__nfet_01v8" in to_netlist(g, pdk=SKYWATER_SKY130)


# --- the flavor field carries TWO vocabularies: voltage class vs threshold --------------------
def test_split_flavor_separates_the_two_vocabularies():
    assert split_flavor("hv") == ("hv", "")  # a voltage class (thick oxide / IO)
    assert split_flavor("io") == ("io", "")
    assert split_flavor("lvt") == ("", "lvt")  # a threshold bin of the CORE device
    assert split_flavor("ulvt") == ("", "ulvt")
    assert split_flavor("hv_nvt") == ("hv", "nvt")  # gf180's native-Vt 6 V part is both
    assert split_flavor("") == ("", "")
    assert split_flavor("3v3") == ("3v3", "")  # unknown label => treated as a class (strict)


def _nmos_graph(model: str) -> CircuitGraph:
    return CircuitGraph.from_netlist(
        NetlistView.from_string(f"* m\nM1 d g s 0 {model} w=1u l=0.1u\n.end\n")
    )


def test_a_threshold_flavor_substitutes_loudly_instead_of_raising(caplog):
    """`nmos_lvt` must not be un-retargetable to a PDK whose default NMOS IS an lvt device.

    No reference table declares a threshold flavor, so treating `lvt` like a voltage class made
    every threshold-flavored token raise against every PDK — including tsmc-n65, whose first NMOS
    is literally `nch_lvt` (the right answer sits in the table and the guard refused it). A
    threshold retarget is a bias-point change, not a voltage-class violation: substitute, and say
    so.
    """
    g = _nmos_graph("nmos_lvt")
    with caplog.at_level(logging.WARNING, logger="spicexplorer_circuitgraph.emit"):
        lowered = to_netlist(g, pdk=TSMC_N65)
    assert "nch_lvt" in lowered
    assert "lvt" in caplog.text and "NOT preserved" in caplog.text
    # …and against a PDK that really has no lvt part, the substitution is the core device
    assert "sky130_fd_pr__nfet_01v8" in to_netlist(g, pdk=SKYWATER_SKY130)
    assert "nfet_03v3" in to_netlist(g, pdk=GF180MCU)
    # the PMOS twin of the same rule (`pmos_ulvt` -> the target's core PMOS)
    assert "pfet_03v3" in to_netlist(_nmos_graph("pmos_ulvt"), pdk=GF180MCU)


def test_a_voltage_class_mismatch_still_raises():
    # The half of the guard that is correct: an hv part has no counterpart in tsmc-n65's table and
    # substituting the core device would put a 3.3 V part on a 1.2 V model.
    with pytest.raises(ValueError, match="voltage class"):
        to_netlist(_nmos_graph("sg13_hv_nmos"), pdk=TSMC_N65)
    # the message names the CLASS, not the whole flavor string
    with pytest.raises(ValueError, match="'hv'-class"):
        to_netlist(_nmos_graph("nfet_06v0_nvt"), pdk=TSMC_N65)


def test_a_threshold_modifier_does_not_strand_a_declared_voltage_class():
    # gf180's `nfet_06v0_nvt` is flavor 'hv_nvt'. sky130 declares 'hv', so the oxide class is
    # preserved and only the threshold is substituted — it used to raise against every PDK.
    lowered = to_netlist(_nmos_graph("nfet_06v0_nvt"), pdk=SKYWATER_SKY130)
    assert "sky130_fd_pr__nfet_g5v0d10v5" in lowered and "nfet_01v8" not in lowered


def test_model_for_stays_exact_so_a_declared_threshold_would_win():
    mos, nmos = DeviceType.MOS, MosPolarityType.NMOS
    assert TSMC_N65.model_for(mos, nmos, "lvt") is None  # exact lookup is unchanged
    assert TSMC_N65.resolve_model(mos, nmos, "lvt")[0] == "nch_lvt"
    assert TSMC_N65.resolve_model(mos, nmos, "hv") == (None, "")
    assert TSMC_N65.resolve_model(mos, nmos, "") == ("nch_lvt", "")  # unflavored: byte-identical
