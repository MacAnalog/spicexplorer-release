"""Figure builders: correct trace shapes, measurement overlays, safe HTML."""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_waveview import (
    bode_figure,
    dc_figure,
    fft_spectrum_figure,
    load_result,
    log_view_html,
    noise_figure,
    parse_log_text,
    pss_spectrum_figure,
    tran_figure,
    waveform_figure,
)
from spicexplorer_waveview.plotting import figure_title, format_y
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir, synth_tran_raw


@pytest.fixture(scope="module")
def ng_ac(tmp_path_factory):
    p = tmp_path_factory.mktemp("plt") / "ac.raw"
    truth = synth_ac_raw(p)
    return load_result(p), truth


@pytest.fixture(scope="module")
def ng_tran(tmp_path_factory):
    p = tmp_path_factory.mktemp("plt") / "tran.raw"
    truth = synth_tran_raw(p)
    return load_result(p), truth


@pytest.fixture(scope="module")
def sp(tmp_path_factory):
    d = tmp_path_factory.mktemp("plt") / "amp-raw"
    truth = synth_spectre_raw_dir(d)
    return load_result(d), truth


def test_format_y_variants():
    z = np.array([1 + 1j, 2 + 0j])
    y, label = format_y(z, "mag_db")
    assert label.endswith("(dB)") and y[1] == pytest.approx(20 * np.log10(2))
    assert format_y(z, "auto")[1].endswith("(dB)")  # complex → mag_db
    assert format_y(np.array([1.0, 2.0]), "auto")[1] == "value"
    with pytest.raises(ValueError):
        format_y(z, "bogus")


def test_waveform_figure_excludes_sweep(ng_ac):
    ds, _ = ng_ac
    fig = waveform_figure(ds, "ac")
    names = [t.name for t in fig.data]
    assert names == ["v(vout)"]
    assert fig.to_dict()["layout"]["xaxis"]["type"] == "log"  # auto log-x for ac


def test_waveform_figure_downsamples(ng_tran):
    ds, _ = ng_tran
    fig = waveform_figure(ds, "tran", max_points=100)
    assert len(fig.data[0].x) <= 102


def test_waveform_figure_unknown_analysis(ng_ac):
    ds, _ = ng_ac
    with pytest.raises(KeyError):
        waveform_figure(ds, "tran")


def test_bode_annotations(ng_ac):
    ds, truth = ng_ac
    fig = bode_figure(ds, truth["out"])
    assert len(fig.data) >= 2  # mag + phase (+ PM marker)
    title = figure_title(fig)
    assert "UGF" in title and "PM" in title and "DC gain" in title


def test_bode_stb_lane(sp):
    ds, _ = sp
    fig = bode_figure(ds, "loopGain", analysis="stb")
    assert "loop gain" in figure_title(fig)


def test_tran_settle_overlay(ng_tran):
    ds, truth = ng_tran
    fig = tran_figure(ds, settle={"out": truth["out"], "tol_frac": 0.01})
    assert "t_settle" in figure_title(fig)
    assert len(fig.to_dict()["layout"].get("shapes", [])) >= 2  # settle vline + tolerance band


def test_settle_band_is_step_fraction():
    """tol_frac band must mirror waveforms.settling_time: a fraction of the STEP, not of
    the final value — a 1.6→1.7 V step with tol_frac=0.01 shades ±1 mV, not ±17 mV."""
    from spicexplorer_waveview import WaveAnalysis, WaveDataset, WaveSignal

    t = np.linspace(0.0, 2e-5, 2001)
    v = 1.6 + 0.1 * (1.0 - np.exp(-t / 1e-6))
    an = WaveAnalysis(analysis="tran", native_name="Transient Analysis", sweep="time")
    an.signals["time"] = WaveSignal("time", t)
    an.signals["v(out)"] = WaveSignal("v(out)", v)
    ds = WaveDataset(source="mem", engine="ngspice", analyses={"tran": an})
    fig = tran_figure(ds, ["v(out)"], settle={"out": "v(out)", "tol_frac": 0.01})
    shapes = fig.to_dict()["layout"]["shapes"]
    bands = [s for s in shapes if s.get("type") == "rect"]
    assert bands, "settle tolerance band missing"
    height = bands[0]["y1"] - bands[0]["y0"]
    assert height == pytest.approx(2 * 0.01 * 0.1, rel=0.05)  # 2·|tol_frac·step|


def test_bode_pm_marker_rides_the_curve_inverting():
    """The PM marker must sit ON the plotted unwrapped phase at UGF, including for an
    INVERTING transfer (φ₀ ≈ ±180°) where pm−180 alone floats 180° off the trace."""
    from spicexplorer_waveview import WaveAnalysis, WaveDataset, WaveSignal

    f = np.logspace(0, 9, 901)
    h = -1000.0 / (1.0 + 1j * f / 1e3)  # inverting single pole
    an = WaveAnalysis(analysis="ac", native_name="AC Analysis", sweep="frequency")
    an.signals["frequency"] = WaveSignal("frequency", f.astype(complex))
    an.signals["v(out)"] = WaveSignal("v(out)", h)
    ds = WaveDataset(source="mem", engine="ngspice", analyses={"ac": an})
    fig = bode_figure(ds, "v(out)")
    marker = next(tr for tr in fig.data if tr.mode and "markers" in tr.mode)
    ugf = float(marker.x[0])
    phase = np.degrees(np.unwrap(np.angle(h)))
    curve_at_ugf = float(np.interp(np.log10(ugf), np.log10(f), phase))
    assert float(marker.y[0]) == pytest.approx(curve_at_ugf, abs=2.0)


def test_dc_icmr_overlay(sp):
    ds, truth = sp
    fig = dc_figure(ds, "vout", vin="vin", icmr={"vin": "vin", "vtrack": truth["vtrack"]})
    assert "ICMR" in figure_title(fig)


def test_noise_total_overlay(sp):
    ds, _ = sp
    fig = noise_figure(ds, "out", analysis="noise")
    assert "integrated" in figure_title(fig)
    assert fig.to_dict()["layout"]["yaxis"]["type"] == "log"


def test_pss_spectrum_labels(sp):
    ds, _ = sp
    fig = pss_spectrum_figure(ds, "vout")
    t = figure_title(fig)
    assert "THD" in t and "HD2" in t and "SFDR" in t


def test_fft_spectrum(ng_tran):
    ds, _ = ng_tran
    fig = fft_spectrum_figure(ds, "v(vout)")
    assert len(fig.data) == 1 and len(fig.data[0].x) > 10


def test_log_view_html_escapes():
    s = parse_log_text("Error: <script>alert(1)</script>\nplain line\n")
    html = log_view_html(s)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "error: 1" in html
