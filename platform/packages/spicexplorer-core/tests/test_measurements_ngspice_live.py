"""Live-ngspice validation of the engine-neutral measurement library.

Proves the Tier-1 path works on **real ngspice RAW data**, not just synthetic arrays: a
behavioral two-pole op-amp (no PDK, runs on any ngspice host) has an analytically known
transfer H(f) = 1000 / (1+jf/1k)(1+jf/1M), so the metrics extracted from the ngspice AC
sweep must match both (a) the analytic model evaluated on the same frequency grid and
(b) the closed-form figures (60 dB / 1 kHz / ~52° PM). This is the "validate on ngspice
first" gate before the same definitions drive Spectre.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest
from spicexplorer_core.measurements import registry
from spicexplorer_core.measurements import waveforms as wf
from spicexplorer_core.spice_engine import NGSpice_Wrapper

needs_ngspice = pytest.mark.skipif(
    shutil.which("ngspice") is None, reason="ngspice not on PATH"
)

# Behavioral 2-pole op-amp: A0=1000 (60 dB), pole1 = 1/(2π·1k·159.155n) = 1 kHz, pole2 =
# 1/(2π·1k·159.155p) = 1 MHz. Each RC is isolated by a unity VCVS so the poles don't load
# one another → the deck realizes the exact analytic transfer used below. No PDK models.
TWO_POLE_DECK = """* Behavioral two-pole op-amp AC testbench (no PDK)
Vin in 0 dc 0 ac 1
Eamp a 0 in 0 1000
R1 a b 1k
C1 b 0 159.155n
Ebuf c 0 b 0 1
R2 c out 1k
C2 out 0 159.155p
.ac dec 40 1 1e8
.end
"""


def _analytic(freq: np.ndarray) -> np.ndarray:
    return 1000.0 / ((1.0 + 1j * freq / 1e3) * (1.0 + 1j * freq / 1e6))


@pytest.fixture
def two_pole_result(tmp_path: Path):
    deck = tmp_path / "two_pole.cir"
    deck.write_text(TWO_POLE_DECK)
    wrapper = NGSpice_Wrapper(
        netlist_filename=deck, output_folder=tmp_path / "runs", testbench_name="amp"
    )
    return wrapper.run()


@needs_ngspice
def test_ac_metrics_match_analytic_and_closed_form(two_pole_result) -> None:
    res = two_pole_result
    freq = res.wave("frequency", "ac", is_real=True)
    h = res.wave("v(out)", "ac")
    href = _analytic(freq)

    # (a) ngspice-extracted metrics track the analytic model on the SAME grid
    assert wf.dc_gain_db(freq, h) == pytest.approx(wf.dc_gain_db(freq, href), abs=0.05)
    assert wf.unity_gain_freq(freq, h) == pytest.approx(wf.unity_gain_freq(freq, href), rel=0.01)
    assert wf.phase_margin(freq, h) == pytest.approx(wf.phase_margin(freq, href), abs=0.5)

    # (b) absolute closed-form values
    assert wf.dc_gain_db(freq, h) == pytest.approx(60.0, abs=0.1)
    assert wf.bandwidth_3db(freq, h) == pytest.approx(1e3, rel=0.03)
    assert 48.0 < wf.phase_margin(freq, h) < 56.0  # ~52° for this 2-pole


@needs_ngspice
def test_registry_over_real_ngspice_result(two_pole_result) -> None:
    """The declarative recipe path (the same one the optimizer uses) over a real result."""
    res = two_pole_result
    assert registry.measure(res, {"meas": "dcgain", "out": "v(out)"}, default_analysis="ac") == pytest.approx(60.0, abs=0.1)
    assert registry.measure(res, {"meas": "f3db", "out": "v(out)"}, default_analysis="ac") == pytest.approx(1e3, rel=0.03)
    pm = registry.measure(res, {"meas": "pm", "out": "v(out)"}, default_analysis="ac")
    assert 48.0 < pm < 56.0


@needs_ngspice
def test_merge_scalars_round_trip_on_real_result(two_pole_result) -> None:
    """A real NgspiceSimResult is mergeable, and merged canonical scalars win in scalar()."""
    res = two_pole_result
    pm = registry.measure(res, {"meas": "pm", "out": "v(out)"}, default_analysis="ac")
    res.merge_scalars({"pm_deg": pm})
    assert res.scalar("pm_deg", "ac") == pytest.approx(pm)
