"""Edge-input contract tests: exotic devices, case sensitivity, hyphenated subckts, finger
retarget edges, malformed netlists.
"""

from __future__ import annotations

import pytest
from spicexplorer_circuitgraph import (
    GF180MCU,
    IHP_SG13G2,
    SKYWATER_SKY130,
    CircuitGraph,
    CircuitGraphDoc,
    to_netlist,
)
from spicexplorer_core.spice_engine import NetlistView

EXOTIC = (
    "* exotic prefixes\n"
    "D1 a 0 dmodel\n"
    "Q1 c b e qmodel\n"
    "J1 d g s jmodel\n"
    "T1 a 0 b 0 z0=50\n"
    "R1 a b 1k\n"
    ".end\n"
)


# ── exotic / unsupported device policy ────────────────────────────────────────────────────────
def test_exotic_devices_skip_policy_keeps_the_rest():
    """D/Q/J/T prefixes are unsupported: 'skip' drops them (logged) and builds the rest."""
    g = CircuitGraph.from_netlist(NetlistView.from_string(EXOTIC), pdk=IHP_SG13G2)
    assert [c.name for c in g.get_components()] == ["R1"]


def test_exotic_devices_raise_policy_names_the_offender():
    with pytest.raises(ValueError, match="D1"):
        CircuitGraph.from_netlist(NetlistView.from_string(EXOTIC), pdk=IHP_SG13G2,
                                  on_unknown="raise")


def test_unclosed_subckt_is_rejected_at_parse():
    """Malformed netlists die in NetlistView (spicelib), before graph build — pin the seam."""
    with pytest.raises(SyntaxError, match=r"\.END"):
        NetlistView.from_string("* m\n.subckt amp a b\nR1 a b 1k\nX1 n1 n2 amp\n.end\n")


# ── supply classification across name case ────────────────────────────────────────────────────
def test_supply_detection_is_case_insensitive():
    """`VDD`, `Vdd` → supply VDD; `vss_a` → supply VSS (underscore-suffixed rail). (A literal
    `vdd!` global marker can't even reach the graph: spicelib rejects `!` in M-card node names.)"""
    nl = ("* s\nM1 out in VDD VDD sg13_lv_pmos\nM2 out2 in Vdd Vdd sg13_lv_pmos\n"
          "M3 out3 in vss_a vss_a sg13_lv_nmos\n.end\n")
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    roles = {n.name: (n.is_supply, n.supply_type) for n in g.get_nets()}
    assert roles["VDD"] == (True, "VDD")
    assert roles["Vdd"] == (True, "VDD")
    assert roles["vss_a"] == (True, "VSS")
    assert roles["out"] == (False, "")


# ── hyphenated subckt names through emit ──────────────────────────────────────────────────────
def test_hyphenated_subckt_instance_emits_intact():
    """The known hyphenated-name limitation must not corrupt emission: the instance line keeps
    its `ota-5t` reference verbatim (the definition itself is black-box — caller's concern)."""
    nl = ("* h\n.subckt ota-5t inp inn out vdd vss\nM1 out inp vss vss sg13_lv_nmos\n.ends\n"
          "X1 a b c d e ota-5t\nR1 c 0 10k\n.end\n")
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    out = to_netlist(g)
    assert "X1 a b c d e ota-5t" in out


def test_subckt_instance_params_roundtrip():
    """Instance k=v params (`X1 … amp gain=2 w=10u`) survive graph → netlist → graph."""
    nl = "* p\n.subckt amp a b o\nR1 a o 1k\n.ends\nX1 n1 n2 n3 amp gain=2 w=10u\n.end\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    emitted = to_netlist(g)
    assert "gain=2" in emitted and "w=10u" in emitted
    g2 = CircuitGraph.from_netlist(NetlistView.from_string("* t\n" + emitted.split("\n", 1)[1]),
                                   pdk=IHP_SG13G2)
    assert (g2.component_count, g2.net_count) == (g.component_count, g.net_count)


# ── finger retargeting edges (incl. the case-sensitivity bug this file pinned) ────────────────
def _mos_lines(netlist: str) -> list[str]:
    return [ln for ln in netlist.splitlines() if ln.lower().startswith("m")]


@pytest.mark.parametrize("w_key,ng_key", [("w", "ng"), ("W", "ng"), ("w", "NG"), ("W", "NG")])
def test_finger_retarget_renames_count_any_param_case(w_key, ng_key):
    """SPICE params are case-insensitive: `W=10u NG=4` must rename to `nf=4` exactly like
    `w=10u ng=4`, keeping the width TOTAL (sky130/gf180 BSIM4 finger internally on w/nf)."""
    nl = f"* f\nM1 out in 0 0 sg13_lv_nmos {w_key}=10u l=0.5u {ng_key}=4\n.end\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    (line,) = _mos_lines(to_netlist(g, pdk=SKYWATER_SKY130))
    assert "nf=4" in line and "=10u" in line and "/(4)" not in line  # width total (any w/W case)
    assert "ng" not in line.lower().replace("nf", "")


def test_finger_retarget_no_ng_unchanged_and_gf180_matches_sky130():
    nl = ("* f\nM1 out in 0 0 sg13_lv_nmos w=10u l=0.5u ng=4\n"
          "M2 o2 in 0 0 sg13_lv_nmos w=2u l=0.5u\n.end\n")
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    for pdk in (SKYWATER_SKY130, GF180MCU):
        m1, m2 = _mos_lines(to_netlist(g, pdk=pdk))
        assert "nf=4" in m1 and "w=10u" in m1 and "/(4)" not in m1   # total width, BSIM4 fingers it
        assert "w=2u" in m2 and "nf=" not in m2       # single-finger device untouched
    ihp_m1, _ = _mos_lines(to_netlist(g))             # IHP keeps the canonical convention
    assert "ng=4" in ihp_m1 and "w=10u" in ihp_m1


def test_finger_retarget_survives_json_contract_roundtrip():
    """Params (incl. ng) must come back from CircuitGraphDoc such that retarget still fires."""
    nl = "* f\nM1 out in 0 0 sg13_lv_nmos w=10u l=0.5u ng=4\n.end\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    g2 = CircuitGraphDoc.from_graph(g).to_graph()
    (line,) = _mos_lines(to_netlist(g2, pdk=SKYWATER_SKY130))
    assert "nf=4" in line and "w=10u" in line and "/(4)" not in line
