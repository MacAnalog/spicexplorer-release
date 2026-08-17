"""P8 — testbench ingestion: subckt flatten + AC-stimulus input detection.

Covers the two seams that make *actual* (testbench-level) netlists processable end to end:

* ``ingest_netlist(flatten=True)`` — step into resolvable ``X…`` instances, splice their devices
  in with the ``_<inst>`` postfix (nets + refs), keep AC-ground names global, recurse;
* ``detect_ac_input`` — the netlist's own ``ac``-bearing V source names the input port, so
  ``transfer_function(tb, output)`` needs no explicit ``input``.

The acceptance fixture is the real committed AC testbench ``ota-improved_tb-ac.spice`` (a
unity-gain buffer around the 20-transistor cascode OTA): it must solve end to end with the
loop closed, |Av(0)| just under 1.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    DeviceKind,
    Fidelity,
    detect_ac_input,
    from_file,
    from_string,
    small_signal_model,
    transfer_function,
)

_FIX = Path(__file__).resolve().parent / "fixtures"

# ----------------------------------------------------------------------
# Inline fixtures
# ----------------------------------------------------------------------
DIVIDER_TB = """* divider tb
.subckt div top mid
R1 top mid R
R2 mid 0 R
.ends
X1 in out div
X2 in out2 div
Vin in 0 dc 0.5 ac 1
.end
"""

NESTED_TB = """* nested tb
.subckt inner a b
R1 a n1 R
C1 n1 b C
.ends
.subckt outer p q
X9 p q inner
R3 p q RBIG
.ends
X1 in out outer
.end
"""


# ----------------------------------------------------------------------
# Flatten — structure
# ----------------------------------------------------------------------
def test_flatten_splices_subckt_devices_with_instance_postfix():
    ir = from_string(DIVIDER_TB)
    refs = {d.ref for d in ir.devices}
    assert refs == {"R1_X1", "R2_X1", "R1_X2", "R2_X2", "VIN"}
    assert all(d.kind is not DeviceKind.SUBCKT for d in ir.devices)


def test_flatten_maps_formal_ports_to_actual_nets():
    ir = from_string(DIVIDER_TB)
    r1 = ir.device("R1_X1")
    # formal `top` -> actual `in`; formal `mid` -> actual `out`
    assert [t.net for t in r1.terminals] == ["in", "out"]
    # X2 wires the same definition to different nets
    assert [t.net for t in ir.device("R1_X2").terminals] == ["in", "out2"]


def test_flatten_keeps_ground_global_and_localizes_internal_nets():
    nl = """* internal-net collision
.subckt amp a y
R1 a mid R
R2 mid 0 R
.ends
X1 in mid amp
Vin in 0 ac 1
.end
"""
    ir = from_string(nl)
    # the definition's internal `mid` must NOT merge with the top-level net also called `mid`
    assert [t.net for t in ir.device("R1_X1").terminals] == ["in", "mid_x1"]
    # ground inside the subckt stays the global reference
    assert [t.net for t in ir.device("R2_X1").terminals] == ["mid_x1", "0"]
    assert "mid" in ir.nets and "mid_x1" in ir.nets


def test_flatten_recurses_with_chained_postfixes():
    ir = from_string(NESTED_TB)
    refs = {d.ref for d in ir.devices}
    assert refs == {"R1_X9_X1", "C1_X9_X1", "R3_X1"}
    # inner internal net carries the full chain; the outer formals resolved to top nets
    assert [t.net for t in ir.device("R1_X9_X1").terminals] == ["in", "n1_x9_x1"]
    assert [t.net for t in ir.device("C1_X9_X1").terminals] == ["n1_x9_x1", "out"]


def test_flatten_params_stay_symbolic_per_definition():
    ir = from_string(DIVIDER_TB)
    # both instances share the definition's symbolic value `r`
    assert ir.device("R1_X1").params["value"] == sp.Symbol("r")
    assert ir.device("R1_X2").params["value"] == sp.Symbol("r")


def test_keep_opaque_and_flatten_off():
    ir = from_string(DIVIDER_TB, keep_opaque=("div",))
    assert ir.device("X1").kind is DeviceKind.SUBCKT
    ir2 = from_string(DIVIDER_TB, flatten=False)
    assert ir2.device("X1").kind is DeviceKind.SUBCKT


def test_unresolvable_definition_stays_opaque():
    nl = "* missing def\nX1 a b nowhere\nVin a 0 ac 1\n.end\n"
    ir = from_string(nl)
    assert ir.device("X1").kind is DeviceKind.SUBCKT
    assert ir.device("X1").model == "nowhere"


# ----------------------------------------------------------------------
# AC-stimulus input detection
# ----------------------------------------------------------------------
def test_detect_ac_input_finds_the_unique_ac_source():
    ssir = small_signal_model(from_string(DIVIDER_TB))
    assert detect_ac_input(ssir) == ("in", "0")


def test_detect_ac_input_rejects_none_and_multiple():
    no_ac = from_string("* none\nR1 in out R\nC1 out 0 C\n.end")
    with pytest.raises(ValueError, match="found none"):
        detect_ac_input(small_signal_model(no_ac))
    two = from_string("* two\nV1 a 0 ac 1\nV2 b 0 ac 1\nR1 a b R\n.end")
    with pytest.raises(ValueError, match="v@V1.*v@V2"):
        detect_ac_input(small_signal_model(two))


def test_detect_ac_input_rejects_ac_current_source():
    isrc = from_string("* iac\nI1 0 a ac 1\nR1 a 0 R\n.end")
    with pytest.raises(ValueError, match="i@I1"):
        detect_ac_input(small_signal_model(isrc))


def test_pipeline_auto_input_matches_explicit():
    rc_tb = "* rc tb\nVin in 0 dc 0 ac 1\nR1 in out R\nC1 out 0 C\n.end"
    auto = transfer_function(rc_tb, ("out", "0"))
    explicit = transfer_function(rc_tb, ("out", "0"), ("in", "0"))
    assert auto.tf_exact_expr == explicit.tf_exact_expr
    assert auto.as_sympy_exact() == sp.sympify("1/(c*r*s + 1)")


# ----------------------------------------------------------------------
# The real committed testbench — acceptance
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def tb_path():
    return _FIX / "ota-improved_tb-ac.spice"


def test_cascode_tb_flattens_to_one_level(tb_path):
    ir = from_file(tb_path)
    counts: dict[DeviceKind, int] = {}
    for d in ir.devices:
        counts[d.kind] = counts.get(d.kind, 0) + 1
    assert counts[DeviceKind.NMOS] == 12 and counts[DeviceKind.PMOS] == 8
    assert counts[DeviceKind.VSOURCE] == 8  # tb Vdd/Vss/Vin/Venable + DUT Vmeas1/Vmeas4/V1/V2
    assert counts[DeviceKind.CAPACITOR] == 1 and counts[DeviceKind.ISOURCE] == 1
    assert DeviceKind.SUBCKT not in counts
    # the DUT-internal `net1` was disambiguated from the testbench's own `net1`
    assert "net1" in ir.nets and "net1_xota" in ir.nets


def test_cascode_tb_solves_end_to_end_as_unity_buffer(tb_path):
    """The whole point of P8: the *actual* AC testbench, no manual grounds, no explicit input.

    The tb closes the loop (vinn tied to v_out), so with ball-park small-signal numbers the
    closed-loop DC gain must come out just under 1 (A0/(1+A0) with A0 ~ a few hundred).
    """
    ir = from_file(tb_path)
    ssir = small_signal_model(ir, level=Fidelity.SOME_PARASITIC)
    subs = {n: (1e-3 if n.startswith("gm") else 2e5) for n in ssir.introduced_symbols}
    res = transfer_function(ir, ("v_out", "0"), subs=subs, operating_point=subs)
    assert res.solve_path == "selectively_numericized"
    av0 = res.dc_gain.value
    assert av0 is not None and 0.9 < av0 < 1.0
