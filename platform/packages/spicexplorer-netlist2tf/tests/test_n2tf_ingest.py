"""Stage-1 ingestion tests — against the real committed IHP OTA fixtures under examples/OTA/**.

Fixtures used:
* the cascode DUT ``ota-improved.spice`` — a flat netlist (24 devices: MOSFETs + bias V-sources),
  the cleanest real ingestion target;
* the 5-transistor OTA, reached as the inline ``.subckt`` definition of its AC testbench
  (spicelib truncates the hyphenated name ``ota-5t`` → step in by *name* ``ota``).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import sympy as sp
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_netlist2tf import from_file, from_string, ingest_netlist
from spicexplorer_netlist2tf.ingest import classify_net_role, sympify_value
from spicexplorer_netlist2tf.model import Circuit2TF, DeviceKind, NetRole, PinRole

_FIX = Path(__file__).resolve().parent / "fixtures"


# ------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------
@pytest.fixture(scope="module")
def cascode() -> Circuit2TF:
    dut = _FIX / "ota-improved.spice"
    return from_file(dut, name="cascode")


@pytest.fixture(scope="module")
def ota5t() -> Circuit2TF:
    tb = _FIX / "ota-5t_tb-ac.spice"
    ota_def = NetlistView.from_file(tb).get_subcircuit_named("ota")
    assert ota_def is not None
    return ingest_netlist(ota_def, name="ota5t")


# ------------------------------------------------------------------------
# sympify_value — the value parser
# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("50f", sp.Float(50e-15)),
        ("0.13u", sp.Float(0.13e-6)),
        ("1.5", sp.Float(1.5)),
        ("0", sp.Integer(0)),
        ("1", sp.Integer(1)),
        (1, sp.Integer(1)),
        ("0P", sp.Integer(0)),  # the VMEAS4 value
    ],
)
def test_sympify_numeric(raw, expected):
    assert sympify_value(raw) == expected


def test_sympify_symbolic_lowercased():
    # A symbolic reference becomes a lower-cased Symbol (SPICE is case-insensitive).
    assert sympify_value("X_DUT_M5_W") == sp.Symbol("x_dut_m5_w")
    assert sympify_value("CL") == sp.Symbol("cl")


def test_sympify_brace_expression():
    assert sympify_value("{2*W}") == 2 * sp.Symbol("w")


# ------------------------------------------------------------------------
# Net role classification
# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "name, role",
    [
        ("0", NetRole.GROUND),
        ("gnd", NetRole.GROUND),
        ("GND", NetRole.GROUND),
        ("vdd", NetRole.SUPPLY_DC),
        ("v_dd", NetRole.SUPPLY_DC),
        ("VDD!", NetRole.SUPPLY_DC),
        ("vss", NetRole.SUPPLY_DC),
        ("vout", NetRole.SIGNAL),
        ("net1", NetRole.SIGNAL),
        ("vinp", NetRole.SIGNAL),
    ],
)
def test_classify_net_role(name, role):
    assert classify_net_role(name) is role


# ------------------------------------------------------------------------
# Cascode DUT (flat netlist)
# ------------------------------------------------------------------------
def test_cascode_counts(cascode):
    assert len(cascode.devices) == 24
    mos = cascode.devices_of(DeviceKind.NMOS, DeviceKind.PMOS)
    assert len(mos) == 20  # 20 MOSFETs (all XM…) + 4 V-sources = 24
    vsrc = cascode.devices_of(DeviceKind.VSOURCE)
    assert {d.ref for d in vsrc} == {"V1", "V2", "VMEAS1", "VMEAS4"}


def test_cascode_mos_polarity(cascode):
    assert cascode.device("XM1").kind is DeviceKind.NMOS  # sg13_lv_nmos
    assert cascode.device("XM4").kind is DeviceKind.PMOS  # sg13_lv_pmos


def test_cascode_mos_terminals(cascode):
    # XM5 nodes were [net6, gate, vss, vss] → D,G,S,B
    m5 = cascode.device("XM5")
    assert m5.net_of(PinRole.DRAIN) == "net6"
    assert m5.net_of(PinRole.GATE) == "gate"
    assert m5.net_of(PinRole.SOURCE) == "vss"
    assert m5.net_of(PinRole.BULK) == "vss"


def test_cascode_symbolic_geometry(cascode):
    # w/l are symbolic .param references, carried as (lower-cased) sympy Symbols.
    m5 = cascode.device("XM5")
    assert m5.params["w"] == sp.Symbol("x_dut_m5_w")
    assert m5.params["l"] == sp.Symbol("x_dut_m5_l")
    # a hard-coded geometry stays numeric
    assert cascode.device("XMPD5").params["w"] == sympify_value("1u")


def test_cascode_supply_roles(cascode):
    assert cascode.net("vdd").role is NetRole.SUPPLY_DC
    assert cascode.net("vss").role is NetRole.SUPPLY_DC
    assert cascode.net("vout").role is NetRole.SIGNAL
    assert cascode.net("vinp").role is NetRole.SIGNAL
    # both rails are AC grounds
    assert set(cascode.ac_ground_nets) >= {"vdd", "vss"}


def test_cascode_bias_source_kept(cascode):
    # V1 (vdd, gate_pc) is a symbolic DC bias source — preserved with its dc value.
    v1 = cascode.device("V1")
    assert v1.kind is DeviceKind.VSOURCE
    assert v1.params.get("dc") == sp.Symbol("x_dut_v_bias_2")


# ------------------------------------------------------------------------
# 5T OTA (inline subckt)
# ------------------------------------------------------------------------
def test_ota5t_counts(ota5t):
    assert len(ota5t.devices) == 13
    assert all(d.kind in (DeviceKind.NMOS, DeviceKind.PMOS) for d in ota5t.devices)


def test_ota5t_input_pair_symbolic(ota5t):
    m1 = ota5t.device("XM1")
    assert m1.kind is DeviceKind.NMOS
    assert m1.params["w"] == sp.Symbol("x_dut_nfet_input_w")
    # input pair shares net 'tail' at the source
    assert m1.net_of(PinRole.SOURCE) == "tail"
    assert ota5t.device("XM2").net_of(PinRole.SOURCE) == "tail"


def test_ota5t_free_symbols_recorded(ota5t):
    assert "x_dut_nfet_input_w" in ota5t.symbolic
    assert "x_dut_pfet_load_l" in ota5t.symbolic


# ------------------------------------------------------------------------
# Global .param ingestion (testbench top level)
# ------------------------------------------------------------------------
def test_global_params_ingested():
    tb = _FIX / "ota-5t_tb-ac.spice"
    ir = from_file(tb, name="tb")
    # CL=50f resolves to its numeric value (lower-cased key).
    assert ir.params["cl"] == sympify_value("50f")
    assert ir.params["ibias"] == sympify_value("20u")
    # flatten (P8, default on) splices the DUT in; XM1 lands with the instance postfix
    assert ir.device("XM1_XOTA").kind in (DeviceKind.NMOS, DeviceKind.PMOS)
    # with flatten off, the X… instance stays opaque with positional ports (pre-P8 behavior)
    xota = from_file(tb, name="tb", flatten=False).device("XOTA")
    assert xota.kind is DeviceKind.SUBCKT
    assert all(t.role is PinRole.PORT for t in xota.terminals)
    assert xota.model == "ota-5t"


# ------------------------------------------------------------------------
# JSON round-trip + determinism
# ------------------------------------------------------------------------
def test_json_round_trip(cascode):
    rebuilt = Circuit2TF.from_dict(cascode.to_dict())
    assert rebuilt.to_dict() == cascode.to_dict()


def test_ingestion_is_deterministic():
    dut = _FIX / "ota-improved.spice"
    a = from_file(dut, name="cascode").to_dict()
    b = from_file(dut, name="cascode").to_dict()
    assert a == b  # byte-identical IR from the same netlist


# ------------------------------------------------------------------------
# Hermetic from_string
# ------------------------------------------------------------------------
def test_from_string_hermetic():
    text = """* tiny RC
V1 in 0 dc 0 ac 1
R1 in out 10k
C1 out 0 1u
.end
"""
    ir = from_string(text, name="rc", ports={"in": ("in", "0"), "out": ("out", "0")})
    assert ir.device("R1").kind is DeviceKind.RESISTOR
    assert ir.device("R1").params["value"] == sympify_value("10k")
    assert ir.device("C1").params["value"] == sympify_value("1u")
    assert ir.device("V1").params["ac"] == sp.Integer(1)
    assert ir.net("0").role is NetRole.GROUND
    assert ir.ports["out"].is_single_ended()
