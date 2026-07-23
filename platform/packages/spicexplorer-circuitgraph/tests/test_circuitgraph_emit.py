"""Graph → netlist emission + round-trip + cross-PDK device renaming."""

from pathlib import Path

import pytest
from spicexplorer_circuitgraph import (
    GF180MCU,
    IHP_SG13G2,
    SKYWATER_SKY130,
    CircuitGraph,
    to_netlist,
)
from spicexplorer_circuitgraph.model.edges import PinTypeMOSFET
from spicexplorer_circuitgraph.model.nodes import (
    DeviceType,
    MosfetNode,
    MosPolarityType,
    NetNode,
    SubcktInstanceNode,
)
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"
FOLDED_TB = _FIX / "cora_testbench_ac.spice"


def _graph(path, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(path), pdk=IHP_SG13G2, **kw)


def _regraph(netlist: str, **kw) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_string(netlist), **kw)


def _fingerprint(g: CircuitGraph) -> dict:
    """name → (type, polarity, ordered connections) — a structural device-for-device identity."""
    return {
        c.name: (
            type(c).__name__,
            getattr(c, "polarity", None),
            tuple(sorted(g.connections(c).items())),
        )
        for c in g.get_components()
    }


# --- structure / parseability --------------------------------------------------------------
def test_emitted_netlist_is_well_formed():
    nl = to_netlist(_graph(CASCODE_FLAT, name="ota-improved"))
    assert nl.splitlines()[0].startswith("* ota-improved")
    assert nl.strip().endswith(".end")
    assert "XM1 net4 vinp tail vss sg13_lv_nmos" in nl  # nodes in pin order + model + params


# --- netlist → graph → netlist round-trip (flat, lossless) ---------------------------------
def test_flat_roundtrip_is_isomorphic():
    g = _graph(CASCODE_FLAT, name="ota-improved")
    g2 = _regraph(to_netlist(g), pdk=IHP_SG13G2)
    assert g.component_count == g2.component_count == 24
    assert g.net_count == g2.net_count
    assert _fingerprint(g) == _fingerprint(g2)  # device-for-device identical


def test_emit_is_idempotent():
    g = _graph(CASCODE_FLAT, name="ota-improved")
    nl = to_netlist(g)
    assert to_netlist(_regraph(nl, name="ota-improved", pdk=IHP_SG13G2)) == nl


def test_emit_without_pdk_keeps_original_models():
    nl = to_netlist(_graph(CASCODE_FLAT))
    assert "sg13_lv_nmos" in nl and "sg13_lv_pmos" in nl
    assert "sky130" not in nl


# --- cross-PDK device renaming (#3b) -------------------------------------------------------
def test_cross_pdk_rename_ihp_to_skywater():
    g = _graph(CASCODE_FLAT)
    sky = to_netlist(g, pdk=SKYWATER_SKY130)
    # IHP names gone, Skywater device names present
    assert "sg13_lv_nmos" not in sky and "sg13_lv_pmos" not in sky
    assert "sky130_fd_pr__nfet_01v8" in sky and "sky130_fd_pr__pfet_01v8" in sky

    # re-graph with the Skywater PDK → polarity preserved device-for-device
    gs = _regraph(sky, pdk=SKYWATER_SKY130)
    assert g.component_count == gs.component_count
    ihp_pol = {c.name: c.polarity for c in g.get_components() if isinstance(c, MosfetNode)}
    sky_pol = {c.name: c.polarity for c in gs.get_components() if isinstance(c, MosfetNode)}
    assert ihp_pol == sky_pol
    # and the connectivity is unchanged by the rename
    assert {n: f[2] for n, f in _fingerprint(g).items()} == {
        n: f[2] for n, f in _fingerprint(gs).items()
    }


def test_finger_convention_retargeted_for_skywater():
    """sky130 is BSIM4 with `nf` → the device bins on per-finger `w/nf` *itself*, so emission renames
    `ng`→`nf` and keeps `w` TOTAL (dividing here too would double-divide into a defective bin). IHP
    keeps `ng`."""
    src = "* fingers\nXM1 d g s b sg13_lv_nmos w=10u l=0.5u ng=4 m=1\n.end\n"
    g = _regraph(src, pdk=IHP_SG13G2)

    # IHP (default convention): ng + total width preserved verbatim
    ihp = to_netlist(g, pdk=IHP_SG13G2)
    assert "ng=4" in ihp and "w=10u" in ihp and "nf=" not in ihp

    # sky130: ng -> nf, width stays TOTAL (NOT w/ng), no leftover ng
    sky = to_netlist(g, pdk=SKYWATER_SKY130)
    assert "nf=4" in sky and "w=10u" in sky and "/(4)" not in sky
    assert "ng=" not in sky
    # still re-parses as one device with the same connectivity
    assert _regraph(sky, pdk=SKYWATER_SKY130).component_count == g.component_count == 1


def test_finger_retarget_noop_without_fingers():
    """A single-finger device (no `ng`) is unchanged when emitted to an `nf` PDK."""
    src = "* no fingers\nXM1 d g s b sg13_lv_nmos w=2u l=0.5u m=1\n.end\n"
    sky = to_netlist(_regraph(src, pdk=IHP_SG13G2), pdk=SKYWATER_SKY130)
    assert "w=2u" in sky and "nf=" not in sky and "ng=" not in sky


def test_finger_convention_retargeted_for_gf180():
    """gf180 is also BSIM4 with `nf` → ng→nf, width stays TOTAL (same as sky130), device renamed."""
    src = "* fingers\nXM1 d g s b sg13_lv_nmos w=10u l=0.5u ng=4 m=1\n.end\n"
    gf = to_netlist(_regraph(src, pdk=IHP_SG13G2), pdk=GF180MCU)
    assert "nfet_03v3" in gf and "nf=4" in gf and "w=10u" in gf and "/(4)" not in gf and "ng=" not in gf


def test_pdk_reverse_lookup_for_skywater():
    assert SKYWATER_SKY130.model_for(DeviceType.MOS, MosPolarityType.NMOS) == "sky130_fd_pr__nfet_01v8"
    assert SKYWATER_SKY130.model_for(DeviceType.MOS, MosPolarityType.PMOS) == "sky130_fd_pr__pfet_01v8"


# --- subckt instance emission --------------------------------------------------------------
def test_subckt_instance_emitted_as_instance_line():
    g = _graph(FOLDED_TB)  # top level: X1 (opamp) + sources
    nl = to_netlist(g)
    # X1 emitted with its ports (in order) then the subckt name; no .subckt body (black box)
    assert "X1 vin- vin+ out vdd ib GND opamp" in nl
    assert ".subckt" not in nl.lower()

    # re-parses: X1 is still a subckt instance wired to the same nets (positional ports, since the
    # definition isn't emitted) — structurally preserved.
    g2 = _regraph(nl, pdk=IHP_SG13G2)
    x1, x1b = g._comp_map["X1"], g2._comp_map["X1"]
    assert isinstance(x1b, SubcktInstanceNode) and x1b.subckt_name == "opamp"
    assert list(g.connections(x1).values()) == list(g2.connections(x1b).values())  # same nets, in order


# --- hardening: don't silently corrupt on incomplete/programmatic graphs -------------------
def _mos_graph(*, spice_model, polarity=MosPolarityType.NMOS, connect_bulk=True) -> CircuitGraph:
    g = CircuitGraph("x")
    nets = {n: g.add_net(NetNode(n)) for n in ("d", "g", "s", "b")}
    m = g.add_component(
        MosfetNode(name="M1", device_type=DeviceType.MOS, polarity=polarity, spice_model=spice_model)
    )
    g.connect(m, nets["d"], PinTypeMOSFET.DRAIN)
    g.connect(m, nets["g"], PinTypeMOSFET.GATE)
    g.connect(m, nets["s"], PinTypeMOSFET.SOURCE)
    if connect_bulk:
        g.connect(m, nets["b"], PinTypeMOSFET.BULK)
    return g


def test_emit_raises_on_empty_value_slot():
    # A MOS with no model and no target PDK would emit `M1 d g s b` → a net swallowed as the model.
    with pytest.raises(ValueError, match="no model/value token"):
        to_netlist(_mos_graph(spice_model=None))


def test_emit_raises_on_unconnected_pin():
    with pytest.raises(ValueError, match="pin .* is unconnected"):
        to_netlist(_mos_graph(spice_model="sg13_lv_nmos", connect_bulk=False))


def test_cross_pdk_unresolved_polarity_warns_and_keeps_source_model(caplog):
    # UNKNOWN-polarity MOS can't be retargeted → warn, keep the source model (no silent rename).
    g = _mos_graph(spice_model="sg13_lv_nmos", polarity=MosPolarityType.UNKNOWN)
    with caplog.at_level("WARNING"):
        nl = to_netlist(g, pdk=SKYWATER_SKY130)
    assert "sg13_lv_nmos" in nl  # unchanged
    assert "cannot retarget" in caplog.text
