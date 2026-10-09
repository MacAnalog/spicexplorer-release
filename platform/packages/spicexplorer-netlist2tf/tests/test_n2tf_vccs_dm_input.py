"""The analog-db corpus follow-ups of issue #310: ``G`` VCCS cards, DM-pair input detection and
the numeric-determinant fast path.

* A linear ``G n+ n- nc+ nc- value`` card ingests as ``DeviceKind.VCCS`` and models as one
  ``VCCS`` primitive (it used to be ``UNKNOWN`` and listed in ``unmodelled``, so the CMFB loop of
  the fully differential benches was missing from their ``H(s)``).
* ``detect_ac_input`` pairs ``Vinp vinp vcm ac 0.5`` / ``Vinn vinn vcm ac -0.5`` into
  ``("vinp", "vinn")``; every other two-source case keeps the old error.
"""

from __future__ import annotations

import pytest
import sympy as sp
from spicexplorer_core import project_root
from spicexplorer_netlist2tf import (
    DeviceKind,
    PinRole,
    S,
    detect_ac_input,
    from_file,
    from_string,
    small_signal_model,
    transfer_function,
)
from spicexplorer_netlist2tf.model.primitives import VCCS
from spicexplorer_netlist2tf.tf import determinant

_DM_BENCH = """* dm bench
Vcm vcm 0 dc 0.9
Vinp vinp {ref_p} dc 0 ac {ac_p}
Vinn vinn {ref_n} dc 0 ac {ac_n}
M1 out vinp t 0 nmos
M2 out2 vinn t 0 nmos
RT t 0 10k
R1 out 0 10k
R2 out2 0 10k
.end
"""


def _dm(ref_p="vcm", ref_n="vcm", ac_p="0.5", ac_n="-0.5"):
    text = _DM_BENCH.format(ref_p=ref_p, ref_n=ref_n, ac_p=ac_p, ac_n=ac_n)
    return small_signal_model(from_string(text))


# ------------------------------------------------------------------ G cards
def test_g_card_is_a_vccs_with_dc_gain_minus_gm_r():
    """The issue's acceptance: ``GM out 0 in 0 1m`` into 10 kΩ has DC gain −10, nothing dropped."""
    res = transfer_function("* g\nGM out 0 in 0 1m\nR1 out 0 10k\n.end", ("out", "0"), ("in", "0"))
    assert res.dc_gain is not None and res.dc_gain.value == pytest.approx(-10.0)
    assert res.unmodelled == []


def test_g_card_ingests_its_four_nets_and_a_symbolic_gain():
    ir = from_string("* cmfb\n.param gm_val=1m\nGM vss vcmfb vcmfb_ref cm_det {gm_val}\n.end")
    (g,) = ir.devices
    assert g.kind is DeviceKind.VCCS
    assert [(t.role, t.net) for t in g.terminals] == [
        (PinRole.PLUS, "vss"),
        (PinRole.MINUS, "vcmfb"),
        (PinRole.CONTROL_PLUS, "vcmfb_ref"),
        (PinRole.CONTROL_MINUS, "cm_det"),
    ]
    assert str(g.params["value"]) == "gm_val"
    assert {"vcmfb_ref", "cm_det"} <= set(ir.nets)  # control nets are nets of the circuit
    ssir = small_signal_model(ir)
    assert ssir.unmodelled == ()
    assert ssir.primitives == (
        VCCS(
            name="g@GM", np="vss", nn="vcmfb", cp="vcmfb_ref", cn="cm_det", value=g.params["value"]
        ),
    )


def test_g_card_inside_a_subckt_flattens_with_its_control_nets():
    ir = from_string(
        "* sub\n.subckt servo out sense\nGM 0 out sense ref 2m\nRr ref 0 1k\n.ends\n"
        "x1 o s servo\nRo o 0 1k\nVs s 0 dc 0 ac 1\n.end"
    )
    g = ir.device("GM_X1")
    assert g.kind is DeviceKind.VCCS
    assert g.nets == ("0", "o", "s", "ref_x1")
    res = transfer_function(ir, ("o", "0"))
    assert res.dc_gain is not None and res.dc_gain.value == pytest.approx(2.0)  # 0→o: +gm·Ro


@pytest.mark.parametrize(
    "card", ["G1 a 0 value={v(c)*2}", "G1 a 0 poly(1) c 0 0 1m", "G1 a 0 c 0 1m m=2"]
)
def test_a_g_card_that_is_not_one_linear_gain_stays_unmodelled(card):
    ir = from_string(f"* nl\n{card}\nR1 a 0 1k\nRc c 0 1k\n.end")
    assert ir.device("G1").kind is DeviceKind.UNKNOWN
    assert small_signal_model(ir).unmodelled == ("G1",)


# ------------------------------------------------------------------ DM-pair input detection
def test_dm_pair_is_detected_positive_half_first():
    assert detect_ac_input(_dm()) == ("vinp", "vinn")
    assert detect_ac_input(_dm(ac_p="-0.5", ac_n="0.5")) == ("vinn", "vinp")


def test_dm_pair_with_a_symbolic_amplitude_is_detected():
    assert detect_ac_input(_dm(ac_p="{a}", ac_n="{-a}")) == ("vinp", "vinn")


@pytest.mark.parametrize(
    "kw",
    [
        {"ac_p": "0.5", "ac_n": "0.4"},  # not ±a
        {"ac_p": "0.5", "ac_n": "0.5"},  # same sign
        {"ref_n": "0"},  # different reference nets
    ],
)
def test_anything_but_a_matched_pair_still_raises(kw):
    with pytest.raises(ValueError, match="expected exactly one AC voltage source"):
        detect_ac_input(_dm(**kw))


def test_transfer_function_needs_no_input_on_a_dm_bench():
    res = transfer_function(
        _DM_BENCH.format(ref_p="vcm", ref_n="vcm", ac_p="0.5", ac_n="-0.5"),
        ("out", "out2"),
        operating_point={"gm_m1": 1e-3, "gm_m2": 1e-3, "ro_m1": 1e6, "ro_m2": 1e6},
    )
    assert res.unmodelled == []


_AMP_001 = project_root() / "examples/analog-db/raw/amp_001_5t/sky130/ac_open_loop.spice"


@pytest.mark.skipif(not _AMP_001.is_file(), reason="examples/analog-db is not checked out")
def test_amp_001_bench_input_is_its_dm_pair():
    assert detect_ac_input(small_signal_model(from_file(_AMP_001))) == ("vinp", "vinn")


# ------------------------------------------------------------------ the numeric determinant
def test_numeric_determinant_fast_path_equals_berkowitz():
    """A matrix whose only symbol is ``s`` goes through ``DomainMatrix`` (the ``--subs`` sweep's
    speed-up); it must be the same exact rational function Berkowitz gives."""
    s = S
    m = sp.Matrix(
        [
            [sp.Rational(1, 3) + s / 7, -sp.Rational(1, 3), 0],
            [-sp.Rational(1, 3), sp.Rational(5, 2) + 2 * s, -1 / (s * 10**12)],
            [sp.Rational(2, 1000), -1 / (s * 10**12), 1 + s * sp.Rational(1, 10**14)],
        ]
    )
    assert sp.cancel(determinant(m) - m.det(method="berkowitz")) == 0
    assert determinant(sp.zeros(0, 0)) == 1


def test_symbolic_determinant_still_takes_berkowitz():
    g = sp.Symbol("g", positive=True)
    m = sp.Matrix([[g + S, -g], [-g, 2 * g]])
    assert sp.expand(determinant(m) - m.det(method="berkowitz")) == 0
