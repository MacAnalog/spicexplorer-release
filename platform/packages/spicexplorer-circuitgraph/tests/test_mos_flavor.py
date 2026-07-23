"""Multi-flavor MOS lowering: a DUT that binds two NMOS (or PMOS) threshold flavors retargets each
instance to its own PDK model via the abstract token (``nmos`` vs ``nmos_hv``). Enables the ΔVth
voltage-reference class member; before this the emit collapsed every nmos to the first-per-polarity
(lv) model."""

from spicexplorer_circuitgraph import (
    IHP_SG13G2,
    CircuitGraph,
    PdkDevice,
    mos_flavor,
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
    # an absent flavor falls back to the default device (never None when a default exists)
    assert IHP_SG13G2.model_for(mos, nmos, "zzz") == "sg13_lv_nmos"


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
