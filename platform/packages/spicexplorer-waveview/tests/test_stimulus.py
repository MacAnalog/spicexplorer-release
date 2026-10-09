"""Stimulus determinism: PRBS period, symbol alphabets, exact UI-delayed PWL taps."""

from __future__ import annotations

import math
import re

import numpy as np
import pytest
from spicexplorer_waveview import stimulus


def test_prbs_is_deterministic_and_periodic():
    a, b = stimulus.prbs(7, 300), stimulus.prbs(7, 300)
    assert (a == b).all() and set(a.tolist()) == {0, 1}
    assert (a[:127] == a[127:254]).all()
    assert not (stimulus.prbs(7, 300, seed=2) == a).all()
    with pytest.raises(ValueError):
        stimulus.prbs(8, 10)


@pytest.mark.parametrize("order", sorted(stimulus.PRBS_TAPS))
def test_prbs_is_maximal_length(order):
    n = 2**order - 1
    bits = stimulus.prbs(order, 2 * n)
    assert (bits[:n] == bits[n:]).all(), "period is exactly 2^order - 1"
    assert bits[:n].sum() == 2 ** (order - 1), "a maximal-length sequence has 2^(n-1) ones"


def test_symbol_levels():
    assert set(stimulus.symbols("nrz", 7, 200).tolist()) == {-1.0, 1.0}
    assert set(np.round(stimulus.symbols("pam4", 7, 200), 6).tolist()) == {
        -1.0,
        -0.333333,
        0.333333,
        1.0,
    }
    with pytest.raises(ValueError):
        stimulus.symbols("pam8", 7, 10)
    with pytest.raises(ValueError):
        stimulus.Data("pam8", 10.0)


def test_data_shape_and_recipe():
    d = stimulus.Data("pam4", 25.0, order=9, n_warm=4)
    assert d.n == 4 + 511 and d.bits_per_symbol == 2 and math.isclose(d.ui, 40e-12)
    assert d.window() == (d.t0 + 4 * d.ui, d.t_end) and d.syms.size == d.n
    r = stimulus.Data.from_recipe(
        {"meas": "vecp_db", "out": "v(x)", "fmt": "pam4", "rate_gbd": 25.0, "order": 9, "n_warm": 4}
    )
    assert r == d


def test_pwl_tap_delay_is_exact():
    d = stimulus.Data("nrz", 10.0)
    line = stimulus.pwl("Vt1", "in", "0", d, vcm=0.5, swing=0.2, delay_ui=1.0)
    assert line.startswith("Vt1 in 0 PWL(")
    pts = re.findall(r"([-+0-9.e]+) ([-+0-9.e]+)", line.split("PWL(")[1])
    first_edge = next(float(t) for t, v in pts if float(v) != 0.5)
    assert math.isclose(first_edge, d.t0 + d.ui + d.tr_ui * d.ui, rel_tol=1e-6)
    inv = stimulus.pwl("Vt1", "in", "0", d, vcm=0.5, swing=0.2, invert=True)
    v0 = float(re.findall(r"([-+0-9.e]+) ([-+0-9.e]+)", inv.split("PWL(")[1])[2][1])
    assert v0 == pytest.approx(0.5 - d.syms[0] * 0.1)


def test_ideal_waveform_is_zero_outside_the_sequence():
    d = stimulus.Data("nrz", 10.0, order=7, n_warm=0)
    t = np.arange(0, d.t_end + 2e-9, d.ui / 10)
    w = stimulus.ideal_waveform(t, d)
    assert (w[t < d.t0] == 0).all() and (w[t >= d.t_end] == 0).all()
    assert set(np.unique(w[(t >= d.t0) & (t < d.t_end)]).tolist()) == {-1.0, 1.0}


@pytest.mark.parametrize(
    "kw",
    [
        {"order": 8},  # no PRBS-8 taps
        {"order": 0},
        {"tr_ui": 0.0},  # a zero-width edge repeats a PWL time point
        {"tr_ui": 1.0},  # an edge as long as the UI: the level is never reached
        {"tr_ui": -0.1},
        {"t0": -1e-9},
        {"n_warm": -1},
        {"rate_gbd": 0.0},
    ],
)
def test_data_rejects_bad_fields_at_construction(kw):
    with pytest.raises(ValueError):
        stimulus.Data(**{"fmt": "nrz", "rate_gbd": 10.0, **kw})


def test_from_recipe_coerces_numerics():
    """A YAML recipe hands strings/ints; the fields come back typed."""
    d = stimulus.Data.from_recipe(
        {
            "meas": "eye_w_ui_1s",
            "fmt": "pam4",
            "rate_gbd": "25",
            "order": "9",
            "n_warm": 4.0,
            "seed": "2",
            "t0": "8e-9",
            "tr_ui": "0.25",
        }
    )
    assert d == stimulus.Data("pam4", 25.0, order=9, n_warm=4, seed=2, t0=8e-9, tr_ui=0.25)
    assert isinstance(d.order, int) and isinstance(d.rate_gbd, float)


@pytest.mark.parametrize("t0,delay_ui", [(0.0, 0.0), (0.0, 1.0), (8e-9, 0.0)])
def test_pwl_time_points_strictly_increase(t0, delay_ui):
    """ngspice warns `non-increasing PWL time points` and continues on a distorted stimulus,
    so a sequence starting at t=0 must not repeat the origin."""
    d = stimulus.Data("nrz", 10.0, order=7, t0=t0)
    line = stimulus.pwl("Vt", "in", "0", d, vcm=0.5, swing=0.2, delay_ui=delay_ui)
    ts = [float(t) for t, _v in re.findall(r"([-+0-9.e]+) ([-+0-9.e]+)", line.split("PWL(")[1])]
    assert all(b > a for a, b in zip(ts, ts[1:])), "PWL time points must strictly increase"
    assert ts[0] == 0.0
