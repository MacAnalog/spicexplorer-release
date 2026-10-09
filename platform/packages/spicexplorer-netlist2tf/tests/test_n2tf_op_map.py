"""``operating_point_from``: a simulator operating point → netlist2tf's minted symbols (issue #313).

Offline: the ngspice case replays the recorded PSP operating point of the IHP 5T OTA bench
(``fixtures/ota-5t_open_loop_ngspice.txt``, the OD-8 acceptance's own run); the Spectre case uses
``read_oppoint_info``-shaped keys. The end-to-end numbers (DC gain, −3 dB, UGF against ngspice)
are the OD-8 acceptance, which now calls this function: live in ``test_n2tf_slow_sim`` and
replayed offline in ``test_n2tf_ota_bench_helpers``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import test_n2tf_slow_sim as slow
from spicexplorer_netlist2tf import (
    Fidelity,
    from_string,
    operating_point_from,
    small_signal_model,
)

_REPLAY = Path(__file__).resolve().parent / "fixtures" / "ota-5t_open_loop_ngspice.txt"
_LINE = re.compile(r"^(\S+)\s*=\s*(\S+)\s*$", re.M)

#: One distinct value per PSP output, so a swapped or dropped term shows.
_PSP = {
    "gm": 1.0e-4,
    "gds": 2.0e-6,
    "gmb": 3.0e-5,
    "cgs": 10.0,
    "cgsol": 100.0,
    "cgd": 20.0,
    "cgdol": 200.0,
    "cjd": 5.0,
    "cjs": 7.0,
    "cdb": 999.0,
    "csb": 888.0,
}  # PSP's trans-capacitances: must NOT be used
_HYBRID_PI = {
    "gm": 1.0e-4,
    "ro": 5.0e5,
    "gmb": 3.0e-5,
    "cgs": 110.0,
    "cgd": 220.0,
    "cdb": 5.0,
    "csb": 7.0,
}

_SUBCKT_DECK = """* a subckt-wrapped device, flattened
.subckt amp out in vss
XM1 out in vss vss sg13_lv_nmos w=1u l=1u
.ends
xamp vout vin 0 amp
.end
"""


def _recorded_op() -> dict[str, float]:
    return {k.lower(): float(v) for k, v in _LINE.findall(_REPLAY.read_text())}


def _ota_ssir():
    ir = from_string(slow._bench(slow._OPEN_LOOP_N2TF), name="ota_5t_open_loop")
    return ir, small_signal_model(ir, level=Fidelity.FULL)


def test_recorded_ngspice_op_fills_every_symbol_of_the_flattened_ota():
    """The OD-8 bench: 13 subckt-flattened PSP devices (``@n.xota.xm5.nsg13_lv_nmos[gm]`` →
    ``gm_m5_xota``) plus the bench's ``.param`` CL — nothing left unmapped."""
    op = _recorded_op()
    ir, ssir = _ota_ssir()
    values, unmapped = operating_point_from(op, ssir)
    assert unmapped == []
    key = "@n.xota.xm5.nsg13_lv_nmos"
    assert values["gm_m5_xota"] == op[f"{key}[gm]"]
    assert values["ro_m5_xota"] == pytest.approx(1.0 / op[f"{key}[gds]"])
    assert values["cgs_m5_xota"] == pytest.approx(op[f"{key}[cgs]"] + op[f"{key}[cgsol]"])
    assert values["cgd_m5_xota"] == pytest.approx(op[f"{key}[cgd]"] + op[f"{key}[cgdol]"])
    assert values["cdb_m5_xota"] == op[f"{key}[cjd]"]
    assert values["csb_m5_xota"] == op[f"{key}[cjs]"]
    assert values["cl"] == float(ir.params["cl"])
    # the same answer when handed the IR (modelled at FULL inside)
    assert operating_point_from(op, ir) == (values, unmapped)


def test_psp_mapping_adds_the_overlaps_and_uses_the_junctions_not_the_transcapacitances():
    ssir = small_signal_model(from_string("* m\nM1 d g 0 0 nmos\n.end"), level=Fidelity.FULL)
    values, unmapped = operating_point_from({f"@m1[{p}]": v for p, v in _PSP.items()}, ssir)
    assert unmapped == []
    assert values == pytest.approx({f"{role}_m1": v for role, v in _HYBRID_PI.items()})


def test_bsim_names_fill_the_same_roles():
    """BSIM spells the body transconductance ``gmbs`` and the junctions ``capbd``/``capbs``."""
    ssir = small_signal_model(from_string("* m\nM1 d g 0 0 nmos\n.end"), level=Fidelity.FULL)
    op = {
        "gm": 1e-4,
        "gds": 1e-6,
        "gmbs": 2e-5,
        "cgs": 1e-15,
        "cgd": 2e-16,
        "capbd": 3e-16,
        "capbs": 4e-16,
    }
    values, unmapped = operating_point_from({f"@m1[{p}]": v for p, v in op.items()}, ssir)
    assert unmapped == []
    assert values["gmb_m1"] == 2e-5 and values["cdb_m1"] == 3e-16 and values["csb_m1"] == 4e-16


@pytest.mark.parametrize(
    "key",
    [
        "@m.xamp.xm1[{p}]",  # ngspice: type letter, then the instance path
        "@n.xamp.xm1.nsg13_lv_nmos[{p}]",  # ngspice through the PDK's subckt wrapper (OSDI)
        "xamp.XM1:{p}",  # Spectre read_oppoint_info
        "xamp.xm1.m0:{p}",  # Spectre through the wrapper
    ],
)
def test_a_flattened_device_is_found_by_its_instance_path(key):
    ssir = small_signal_model(from_string(_SUBCKT_DECK), level=Fidelity.SOME_PARASITIC)
    assert set(ssir.symbols) == {"XM1_XAMP"}
    values, unmapped = operating_point_from(
        {key.format(p="gm"): 1e-4, key.format(p="gds"): 1e-6}, ssir
    )
    assert unmapped == []
    assert values == pytest.approx({"gm_m1_xamp": 1e-4, "ro_m1_xamp": 1e6})


def test_colliding_labels_map_onto_the_names_the_mint_chose():
    """``M1`` and ``XM1`` both read as ``m1``; the mint gives XM1 ``gm_xm1``, and so must this."""
    ssir = small_signal_model(
        from_string("* two\nM1 a g 0 0 nmos\nXM1 a g2 0 0 sg13_lv_nmos\nR1 a 0 1k\n.end"),
        level=Fidelity.IDEAL,
    )
    op = {"@m1[gm]": 1e-3, "@n.xm1.nsg13_lv_nmos[gm]": 2e-3}
    values, unmapped = operating_point_from(op, ssir)
    assert (values, unmapped) == ({"gm_m1": 1e-3, "gm_xm1": 2e-3}, [])


def test_nothing_is_defaulted():
    """A missing device, a missing parameter, a non-positive gds and a symbolic .param are all
    reported in ``unmapped``; node voltages and measurements in the result are ignored."""
    ir = from_string(
        "* cs\n.param rl=10k\nM1 out in 0 0 nmos\nM2 out b vdd vdd pmos\n"
        "RL out vdd {rl}\nC1 out 0 {cx}\n.end"
    )
    op = {"@m1[gm]": 1e-3, "@m1[gds]": 0.0, "v(out)": 0.6, "a0": 32.0, "@m1[cgs]": "n/a"}
    values, unmapped = operating_point_from(op, ir, level=Fidelity.SOME_PARASITIC)
    assert values == {"gm_m1": 1e-3, "rl": 1e4}
    assert unmapped == ["cx", "gm_m2", "ro_m1", "ro_m2"]
    # and with params=False the deck's own .param is not filled either
    assert "rl" in operating_point_from(op, ir, level=Fidelity.SOME_PARASITIC, params=False)[1]


def test_an_empty_result_maps_nothing():
    ssir = small_signal_model(from_string("* m\nM1 d g 0 0 nmos\n.end"))
    assert operating_point_from({}, ssir) == ({}, ["gm_m1", "ro_m1"])
