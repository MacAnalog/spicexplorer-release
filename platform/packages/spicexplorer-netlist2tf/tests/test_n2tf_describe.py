"""Stage-5 output-form + contract tests, plus the numpy lambdify-at-jω helper."""

from __future__ import annotations

import math

import numpy as np
import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Fidelity,
    TransferFunctionResult,
    build_system,
    describe_tf,
    extract_tf,
    from_string,
    small_signal_model,
)
from spicexplorer_netlist2tf.numeric import frequency_response, log_sweep
from spicexplorer_netlist2tf.tf import S


def _raw(netlist, output, input, *, level=Fidelity.SOME_PARASITIC, subs=None):
    ir = from_string(netlist, name="c")
    system = build_system(small_signal_model(ir, level=level), subs=subs)
    return extract_tf(system, output, input, numeric_subs=subs)


# ------------------------------------------------------------------------
# RC low-pass — one pole at -1/(RC), DC gain 1, no zeros
# ------------------------------------------------------------------------
def test_rc_description_symbolic():
    raw = _raw("* rc\nR1 in out R\nC1 out 0 C\n.end", ("out", "0"), ("in", "0"))
    res = describe_tf(raw)
    assert isinstance(res, TransferFunctionResult)
    assert res.dc_gain.expr == "1"
    assert len(res.poles) == 1 and len(res.zeros) == 0
    # pole at s = -1/(R*C)
    assert sp.simplify(sp.sympify(res.poles[0].expr) - (-1 / (sp.Symbol("r") * sp.Symbol("c")))) == 0
    assert res.conv_type == "se"


def test_rc_description_numeric_pole():
    raw = _raw("* rc\nR1 in out R\nC1 out 0 C\n.end", ("out", "0"), ("in", "0"))
    res = describe_tf(raw, operating_point={"r": 1e3, "c": 159.15e-9})  # f3dB ≈ 1 kHz
    p = res.poles[0]
    assert p.value_real is not None
    assert p.frequency_hz == pytest.approx(1000.0, rel=1e-2)
    assert res.dc_gain.value == pytest.approx(1.0)


# ------------------------------------------------------------------------
# Common-source — DC gain -gm(ro||RL), frequency-independent
# ------------------------------------------------------------------------
def test_common_source_dc_gain_numeric():
    raw = _raw("* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("out", "0"), ("in", "0"))
    res = describe_tf(raw, operating_point={"gm_m1": 1e-3, "ro_m1": 5e4, "rl": 5e4})
    # -1e-3 * (50k || 50k) = -1e-3 * 25k = -25
    assert res.dc_gain.value == pytest.approx(-25.0)
    assert len(res.poles) == 0  # no caps → no poles
    assert res.model_level == "some_parasitic"


# ------------------------------------------------------------------------
# Second-order RLC — a complex-conjugate pole pair with a Q
# ------------------------------------------------------------------------
def test_rlc_complex_poles_with_q():
    # series R-L then C to ground: H = 1/(1 + sRC + s^2 LC); underdamped for small R.
    raw = _raw("* rlc\nL1 in mid L\nR1 mid out R\nC1 out 0 C\n.end", ("out", "0"), ("in", "0"))
    res = describe_tf(raw, operating_point={"l": 1e-3, "r": 10.0, "c": 1e-6})
    assert len(res.poles) == 2
    # underdamped → complex conjugate pair with a finite Q
    assert any(p.value_imag and abs(p.value_imag) > 0 for p in res.poles)
    assert any(p.q is not None and p.q > 0.5 for p in res.poles)


# ------------------------------------------------------------------------
# Contract serialization + designer views
# ------------------------------------------------------------------------
def test_contract_round_trips_and_views():
    raw = _raw("* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end", ("out", "0"), ("in", "0"))
    res = describe_tf(raw)
    blob = res.model_dump_json()
    again = TransferFunctionResult.model_validate_json(blob)
    assert again.tf_exact_expr == res.tf_exact_expr
    # designer views computed from the canonical string (sympify → plain symbols, no assumptions)
    gm, ro, rl = sp.symbols("gm_m1 ro_m1 rl")
    assert sp.simplify(res.as_sympy() - (-gm * ro * rl / (ro + rl))) == 0
    assert "frac" in res.latex or "/" in res.latex or "{" in res.latex


# ------------------------------------------------------------------------
# numpy lambdify-at-jω helper
# ------------------------------------------------------------------------
def test_frequency_response_rc():
    h = 1 / (1 + sp.Symbol("r") * sp.Symbol("c") * S)
    defs = {"r": 1e3, "c": 159.15e-9}
    freqs = log_sweep(10, 1e6, points_per_decade=10)
    resp = frequency_response(h, defs, freqs)
    assert resp.shape == freqs.shape
    # |H| ≈ 1 at DC-ish, ≈ 1/√2 at ~1 kHz
    assert abs(resp[0]) == pytest.approx(1.0, abs=1e-2)
    i1k = int(np.argmin(np.abs(freqs - 1000.0)))
    assert abs(resp[i1k]) == pytest.approx(1 / math.sqrt(2), rel=5e-2)


def test_frequency_response_constant_broadcasts():
    # A frequency-independent gain must still return a full-length vector.
    resp = frequency_response(sp.Float(-25.0), {}, log_sweep(1, 1e3, 5))
    assert resp.shape[0] > 1 and np.allclose(resp, -25.0)


def test_frequency_response_rejects_unbound():
    with pytest.raises(ValueError, match="unbound"):
        frequency_response(sp.Symbol("gm_m1") / (1 + S), {}, log_sweep(1, 10, 2))
