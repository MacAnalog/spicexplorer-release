"""Every Tier-1 measurement kind evaluated on loaded artifacts (analytic ground truth).

This is requirement #1's proof: the registry's math — AC family, DC/ICMR, transient,
noise integral, native-PSS distortion, STB loop margins, op-point — all run against
viewer-loaded data and hit the analytic values the synthetic artifacts encode.
"""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_waveview import (
    load_result,
    measure_dataset,
    measure_many,
    measurement_catalog,
)
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir, synth_tran_raw


@pytest.fixture(scope="module")
def ngspice_ac(tmp_path_factory):
    p = tmp_path_factory.mktemp("ng") / "ac.raw"
    truth = synth_ac_raw(p)
    return load_result(p), truth


@pytest.fixture(scope="module")
def ngspice_tran(tmp_path_factory):
    p = tmp_path_factory.mktemp("ng") / "tran.raw"
    truth = synth_tran_raw(p)
    return load_result(p), truth


@pytest.fixture(scope="module")
def spectre(tmp_path_factory):
    d = tmp_path_factory.mktemp("sp") / "amp-raw"
    truth = synth_spectre_raw_dir(d)
    return load_result(d), truth


def test_catalog_covers_registry():
    from spicexplorer_core.measurements.registry import known_measurements

    cat = measurement_catalog()
    assert set(cat) == set(known_measurements())
    for info in cat.values():
        assert set(info) == {"kind", "required", "default_analysis"}


# --- ngspice lane ---------------------------------------------------------------
def test_ac_family_ngspice(ngspice_ac):
    ds, truth = ngspice_ac
    out = truth["out"]
    assert measure_dataset(ds, {"meas": "dcgain", "out": out}) == pytest.approx(truth["dcgain_db"], abs=0.01)
    assert measure_dataset(ds, {"meas": "ugf", "out": out}) == pytest.approx(truth["ugf_hz"], rel=0.02)
    assert measure_dataset(ds, {"meas": "pm", "out": out}) == pytest.approx(truth["pm_deg"], abs=0.5)
    assert measure_dataset(ds, {"meas": "f3db", "out": out}) == pytest.approx(truth["f3db_hz"], rel=0.05)
    gbw = measure_dataset(ds, {"meas": "gbw", "out": out})
    assert np.isfinite(gbw) and gbw > 0
    # bare signal name resolves through the v(...) wrap tolerance
    assert measure_dataset(ds, {"meas": "dcgain", "out": "vout"}) == pytest.approx(truth["dcgain_db"], abs=0.01)


def test_tran_family_ngspice(ngspice_tran):
    ds, truth = ngspice_tran
    ts = measure_dataset(ds, {"meas": "t_settle", "out": truth["out"], "tol_frac": 0.01})
    assert ts == pytest.approx(truth["t_settle_1pct"], rel=0.05)
    slew = measure_dataset(ds, {"meas": "slew", "out": truth["out"]})
    assert slew == pytest.approx(truth["slew_max"], rel=0.05)


# --- spectre lane ---------------------------------------------------------------
def test_ac_family_spectre(spectre):
    ds, truth = spectre
    out = truth["ac_out"]
    assert measure_dataset(ds, {"meas": "dcgain", "out": out}) == pytest.approx(truth["dcgain_db"], abs=0.01)
    assert measure_dataset(ds, {"meas": "ugf", "out": out}) == pytest.approx(truth["ugf_hz"], rel=0.02)
    assert measure_dataset(ds, {"meas": "pm", "out": out}) == pytest.approx(90.0, abs=1.0)


def test_icmr_spectre(spectre):
    ds, truth = spectre
    base = {"out": "vout", "vin": "vin", "vtrack": truth["vtrack"]}
    lo = measure_dataset(ds, {"meas": "icmr_min", **base})
    hi = measure_dataset(ds, {"meas": "icmr_max", **base})
    rng = measure_dataset(ds, {"meas": "icmr_range", **base})
    assert lo == pytest.approx(truth["icmr"][0], abs=0.05)
    assert hi == pytest.approx(truth["icmr"][1], abs=0.05)
    assert rng == pytest.approx(hi - lo, abs=1e-9)


def test_noise_spectre(spectre):
    ds, truth = spectre
    total = measure_dataset(ds, {"meas": "onoise_total", "out": "out"})
    assert total == pytest.approx(truth["onoise_total"], rel=0.02)
    # the registry's noise_spectrum alias reads the same sweep on Spectre
    total2 = measure_dataset(ds, {"meas": "onoise_total", "out": "out", "analysis": "noise_spectrum"})
    assert total2 == pytest.approx(total, rel=1e-9)


def test_pss_distortion_spectre(spectre):
    ds, truth = spectre
    out = "vout"
    assert measure_dataset(ds, {"meas": "thd_pss", "out": out}) == pytest.approx(truth["thd_pss"], rel=0.01)
    assert measure_dataset(ds, {"meas": "thd_pss_pct", "out": out}) == pytest.approx(100 * truth["thd_pss"], rel=0.01)
    assert measure_dataset(ds, {"meas": "hd2_db", "out": out}) == pytest.approx(truth["hd2_db"], abs=0.05)
    assert measure_dataset(ds, {"meas": "hd3_db", "out": out}) == pytest.approx(truth["hd3_db"], abs=0.05)
    assert measure_dataset(ds, {"meas": "hd", "out": out, "n": 2}) == pytest.approx(0.01, rel=0.01)
    sfdr = measure_dataset(ds, {"meas": "sfdr_db", "out": out})
    assert sfdr == pytest.approx(40.0, abs=0.1)


def test_pnoise_spectre(spectre):
    """The pnoise recipe family (Spectre pnoise-riding-PSS) end-to-end on loaded data."""
    ds, truth = spectre
    total = measure_dataset(ds, {"meas": "onoise_pnoise_total", "out": "out"})
    assert total == pytest.approx(truth["onoise_pnoise_total"], rel=0.02)
    spot = measure_dataset(ds, {"meas": "pnoise_spot", "out": "out", "f": 1e5})
    assert spot == pytest.approx(truth["pnoise_spot_1e5"], rel=0.02)
    pn = measure_dataset(
        ds, {"meas": "phase_noise_dbc", "out": "out", "f": 1e5, "carrier_ampl": 1.0}
    )
    # ℒ(f) = 10·log10(density²/(A²/2)) — for A=1 V: 20·log10(spot) + 10·log10(2)
    assert pn == pytest.approx(20 * np.log10(spot) + 10 * np.log10(2.0), abs=0.1)


def test_stb_family_spectre(spectre):
    ds, truth = spectre
    assert measure_dataset(ds, {"meas": "loopgain_db", "out": "loopGain"}) == pytest.approx(truth["loopgain_db"], abs=0.01)
    assert measure_dataset(ds, {"meas": "pm_loop", "out": "loopGain"}) == pytest.approx(90.0, abs=1.0)


def test_op_scalar_spectre(spectre):
    ds, truth = spectre
    assert measure_dataset(ds, {"meas": "i_supply", "probe": "Vdd:p"}) == pytest.approx(truth["i_supply"])
    assert measure_dataset(ds, {"meas": "i_supply", "probe": "Vdd:p", "signed": True}) == pytest.approx(-truth["i_supply"])


def test_t_settle_spectre(spectre):
    ds, truth = spectre
    ts = measure_dataset(ds, {"meas": "t_settle", "out": "vout", "tol_frac": 0.01, "analysis": "tran"})
    assert ts == pytest.approx(-np.log(0.01) * truth["tau"], rel=0.05)


# --- error paths ------------------------------------------------------------------
def test_unknown_measurement_raises(ngspice_ac):
    ds, _ = ngspice_ac
    with pytest.raises(ValueError, match="unknown measurement"):
        measure_dataset(ds, {"meas": "not_a_meas", "out": "v(vout)"})


def test_missing_required_arg_raises(ngspice_ac):
    ds, _ = ngspice_ac
    with pytest.raises(ValueError, match="needs"):
        measure_dataset(ds, {"meas": "thd"})


def test_missing_signal_raises_keyerror(ngspice_ac):
    ds, _ = ngspice_ac
    with pytest.raises(KeyError):
        measure_dataset(ds, {"meas": "dcgain", "out": "v(nope)"})


def test_measure_many_degrades_per_item(ngspice_ac):
    ds, truth = ngspice_ac
    out = measure_many(
        ds,
        {
            "gain": {"meas": "dcgain", "out": truth["out"]},
            "broken": {"meas": "dcgain", "out": "v(nope)"},
            "typo": {"meas": "dcgian", "out": truth["out"]},
        },
    )
    assert out["gain"]["value"] == pytest.approx(truth["dcgain_db"], abs=0.01)
    assert out["gain"]["error"] is None
    assert out["broken"]["value"] is None and "no signal" in out["broken"]["error"]
    assert out["typo"]["value"] is None and "unknown measurement" in out["typo"]["error"]


def test_measure_many_null_arg_degrades(ngspice_tran):
    """A null recipe-arg VALUE passes presence-only validation but must degrade per-item
    (the registry's float() cast raises TypeError), never kill the batch."""
    ds, truth = ngspice_tran
    out = measure_many(
        ds,
        {
            "bad": {"meas": "thd", "out": truth["out"], "f0": None},
            "bad2": {"meas": "t_settle", "out": truth["out"], "tol": [1, 2]},
            "good": {"meas": "slew", "out": truth["out"]},
        },
    )
    assert out["bad"]["value"] is None and out["bad"]["error"]
    assert out["bad2"]["value"] is None and out["bad2"]["error"]
    assert out["good"]["value"] == pytest.approx(truth["slew_max"], rel=0.05)
