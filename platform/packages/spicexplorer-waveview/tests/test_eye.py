"""Eye metrics on ideal and closed eyes, polarity, FFT latency; the registry `eye` kind."""

from __future__ import annotations

import json
import math

import numpy as np
import pytest
from spicexplorer_waveview import (
    WaveAnalysis,
    WaveDataset,
    WaveSignal,
    eye,
    measure_dataset,
    measure_many,
    measurement_catalog,
    stimulus,
)


def _synthetic(fmt: str, closed: bool = False, bipolar: bool = False):
    d = stimulus.Data(fmt, 10.0, order=7, n_warm=8)
    t = np.arange(0, d.t_end + 2e-9, d.ui / 50)
    x = stimulus.ideal_waveform(t, d) if bipolar else 0.5 + 0.5 * stimulus.ideal_waveform(t, d)
    if closed:
        x = 0.5 + 0.02 * np.random.default_rng(0).standard_normal(t.size)
    return t, x, d


@pytest.mark.parametrize("fmt,h_min", [("nrz", 0.4), ("pam4", 0.1)])
def test_eye_ideal_is_open(fmt, h_min):
    m = eye.eye_metrics(*_synthetic(fmt))
    assert m["ok"] == 1 and m["eye_h_norm"] > h_min and m["eye_w_ui_1s"] > 0.5 and m["vecp_db"] < 6
    assert m["er_db"] > 10 and m["polarity"] == 1
    assert all(math.isfinite(v) for v in m.values() if isinstance(v, float))
    json.dumps(m)  # plain floats only, so rows land in the ledger


@pytest.mark.parametrize("fmt", ["nrz", "pam4"])
def test_eye_closed_is_finite(fmt):
    m = eye.eye_metrics(*_synthetic(fmt, closed=True))
    assert m["eye_h_norm"] <= 0 and m["eye_w_ui_1s"] == 0 and m["vecp_db"] == eye.VECP_CAP_DB
    assert all(math.isfinite(v) for v in m.values() if isinstance(v, float))


def test_eye_bipolar_electrical_signal():
    """Levels -1/+1: OMA and VECP come from the level difference, ER is undefined (nan)."""
    m = eye.eye_metrics(*_synthetic("nrz", bipolar=True), full_scale=2.0)
    assert m["ok"] == 1 and 0 <= m["vecp_db"] < 3 and m["eye_h_norm"] > 0.4
    assert math.isnan(m["er_db"]) and abs(m["oma_norm"] - 2.0) < 0.2


def test_eye_is_polarity_safe():
    t, x, d = _synthetic("pam4")
    up = eye.eye_metrics(t, x, d)
    down = eye.eye_metrics(t, 1.0 - x, d)  # an inverting stage
    assert up["polarity"] == 1 and down["polarity"] == -1
    assert down["eye_h_norm"] == pytest.approx(up["eye_h_norm"], rel=0.05)
    assert down["rlm"] == pytest.approx(up["rlm"], rel=0.05)


def test_pam4_rlm_of_ideal_levels_is_one():
    m = eye.eye_metrics(*_synthetic("pam4"))
    assert m["rlm"] == pytest.approx(1.0, abs=0.05) and len(m["pam4_eye_heights"]) == 3


def test_latency_is_exact_and_matches_a_direct_correlation():
    """Exact to the sample on a PRBS-15 at 200x oversampling, polarity included; and on a short
    sequence the FFT correlation picks the same lag as a direct bounded-lag dot product (no
    wall-clock assertion: this server is shared)."""
    d = stimulus.Data("nrz", 20.0, order=15, n_warm=8)
    dt = d.ui / eye.OVERSAMPLE
    t = np.arange(0, d.t_end + 3e-9, dt)
    delay = 37 * dt
    y = 0.3 * stimulus.ideal_waveform(t - delay, d)
    lag, sign = eye.latency(t, -y, d)
    assert sign == -1 and abs(lag - delay) < dt / 2

    d = stimulus.Data("nrz", 20.0, order=7, n_warm=2)
    dt = d.ui / 20
    t = np.arange(0, d.t_end + 3e-9, dt)
    y = 0.3 * stimulus.ideal_waveform(t - 11 * dt, d)
    ideal, yy = stimulus.ideal_waveform(t, d), y - y.mean()
    n_max = int(max(3 * d.ui, 2e-9) / dt) + 1
    direct = [float(np.dot(yy[k:], ideal[: len(ideal) - k])) for k in range(n_max)]
    assert eye.latency(t, y, d) == (int(np.argmax(np.abs(direct))) * dt, 1)


def test_unknown_format_raises():
    with pytest.raises(ValueError):
        eye.levels("pam8")
    with pytest.raises(ValueError):
        eye.rx_bandwidth("pam8", 10.0)
    assert eye.rx_bandwidth("nrz", 10.0) == 7.5e9 and eye.rx_bandwidth("pam4", 10.0) == 5e9


def test_bessel_lowpass_is_unit_dc_gain():
    t = np.arange(0, 2e-9, 1e-12)
    y = eye.bessel_lowpass(t, np.where(t > 0.2e-9, 1.0, 0.0), 5e9)
    assert y[-1] == pytest.approx(1.0, abs=1e-3) and y[0] == pytest.approx(0.0)


def test_fold_returns_two_ui_window():
    t, x, d = _synthetic("nrz")
    ph, y = eye.fold(t, x, d, n_ui=2)
    assert ph.min() >= 0 and ph.max() < 2 * d.ui and y.size == ph.size


# ------------------------------------------------------------------ registry ----------


def _dataset(fmt: str, bipolar: bool = False) -> tuple[WaveDataset, stimulus.Data]:
    t, x, d = _synthetic(fmt, bipolar=bipolar)
    tran = WaveAnalysis(
        analysis="tran",
        native_name="Transient Analysis",
        signals={
            "time": WaveSignal("time", t, "s"),
            "v(pout)": WaveSignal("v(pout)", x, "V"),
            "v(pref)": WaveSignal("v(pref)", np.zeros_like(x), "V"),
        },
        sweep="time",
    )
    return WaveDataset(source="synthetic", engine="ngspice", analyses={"tran": tran}), d


def test_eye_is_a_registered_measurement():
    cat = measurement_catalog()
    for name in eye.EYE_MEASUREMENTS:
        assert cat[name]["kind"] == "eye" and cat[name]["default_analysis"] == "tran"
        assert cat[name]["required"] == ["out", "fmt", "rate_gbd"]


def test_eye_recipe_through_measure_dataset():
    ds, d = _dataset("pam4")
    base = {"out": "v(pout)", "fmt": "pam4", "rate_gbd": 10.0, "order": 7, "n_warm": 8}
    direct = eye.eye_metrics(*_synthetic("pam4"))
    assert measure_dataset(ds, {"meas": "vecp_db", **base}) == pytest.approx(direct["vecp_db"])
    assert measure_dataset(ds, {"meas": "ecp_db", **base}) == pytest.approx(direct["vecp_db"])
    assert measure_dataset(ds, {"meas": "rlm", **base}) == pytest.approx(direct["rlm"])
    assert measure_dataset(ds, {"meas": "eye_h_norm", **base, "ref": "v(pref)"}) == pytest.approx(
        direct["eye_h_norm"]
    )
    out = measure_many(ds, {"er": {"meas": "er_db", **base}, "bad": {"meas": "er_db", "out": "x"}})
    assert out["er"]["value"] == pytest.approx(direct["er_db"]) and out["bad"]["error"]
    with pytest.raises(ValueError, match="needs"):
        measure_dataset(ds, {"meas": "eye_w_ui_1s", "out": "v(pout)"})


def test_eye_recipe_bipolar_er_is_nan_degrades_in_measure_many():
    ds, _ = _dataset("nrz", bipolar=True)
    base = {"out": "v(pout)", "fmt": "nrz", "rate_gbd": 10.0, "full_scale": 2.0}
    assert math.isnan(measure_dataset(ds, {"meas": "er_db", **base}))
    assert measure_many(ds, {"er": {"meas": "er_db", **base}})["er"]["value"] is None
    assert measure_dataset(ds, {"meas": "oma_norm", **base}) == pytest.approx(2.0, abs=0.2)
