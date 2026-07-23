"""Spectre noise swept-PSF reader + `noise_analysis` composer (offline, deterministic).

A Spectre `noise` analysis lands its output/input-referred spectral densities in their own
psfascii PSF (`noise.noise`) in the persisted `-raw` dir — NOT the bridge's flat op-point
dict. These tests generate a minimal *analytic* white-noise `noise.noise` (no simulator, no
PDK) and prove, on the same reader/registry path validated live on FOUNDRY-65:

* :func:`read_swept_psf` parses it (sweep vector aliased to the canonical ``frequency``),
* :meth:`SpectreSimResult.wave` serves the ``out``/``in`` densities via the swept-PSF fallback,
* the registry's ``onoise_total`` / ``inoise_total`` recipes integrate the density to an RMS,
* :func:`noise_analysis` emits a contract-correct Spectre statement (→ a ``noise.noise`` PSF).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from spicexplorer.backends.spectre import SpectreSimResult, read_swept_psf
from spicexplorer.backends.spectre_deck import noise_analysis
from spicexplorer_core.measurements import measure

# Flat (white) one-sided spectral densities, V/√Hz. Constant ⇒ the trapezoid integral over
# the band is exact, so RMS = W·√(f_hi − f_lo) closed-form — an exact target to assert on.
_W_OUT = 10.0e-9  # 10 nV/√Hz output-referred
_W_IN = 2.0e-9  # 2 nV/√Hz input-referred
_F_LO, _F_HI = 1.0, 1.0e6


def _write_noise_psf(path: Path) -> None:
    """Emit a minimal valid psfascii ``noise`` file with flat ``out``/``in`` densities."""
    freqs = np.logspace(np.log10(_F_LO), np.log10(_F_HI), 201)
    out = np.full_like(freqs, _W_OUT)
    inp = np.full_like(freqs, _W_IN)
    lines = [
        "HEADER",
        '"PSFversion" "1.00"',
        '"simulator" "spectre"',
        '"analysis type" "noise"',
        "TYPE",
        '"sweep" FLOAT DOUBLE PROP(',
        '"key" "sweep"',
        ")",
        '"V" FLOAT DOUBLE PROP(',
        '"units" "V/sqrt(Hz)"',
        ")",
        "SWEEP",
        '"freq" "sweep" PROP(',
        '"sweep_direction" 0',
        '"units" "Hz"',
        ")",
        "TRACE",
        '"out" "V"',
        '"in" "V"',
        "VALUE",
    ]
    for f, o, i in zip(freqs, out, inp):
        lines.append(f'"freq" {f:.15e}')
        lines.append(f'"out" {o:.15e}')
        lines.append(f'"in" {i:.15e}')
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


def _expected_rms(w: float) -> float:
    return w * np.sqrt(_F_HI - _F_LO)


@pytest.fixture()
def noise_raw_dir(tmp_path: Path) -> Path:
    _write_noise_psf(tmp_path / "noise.noise")
    return tmp_path


def test_read_swept_psf_parses_noise_and_aliases_frequency(noise_raw_dir: Path) -> None:
    sigs = read_swept_psf(noise_raw_dir, "noise")
    assert "out" in sigs and "in" in sigs
    # sweep exposed under both the PSF name and the registry's canonical abscissa
    assert "freq" in sigs and "frequency" in sigs
    assert np.allclose(sigs["frequency"], sigs["freq"])
    assert sigs["out"].dtype == np.float64 and sigs["in"].dtype == np.float64
    assert len(sigs["frequency"]) == len(sigs["out"]) == 201
    assert sigs["out"][0] == pytest.approx(_W_OUT)


def test_wave_falls_back_to_swept_noise_psf(noise_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(noise_raw_dir))
    freq = res.wave("frequency", "noise")
    out = res.wave("out", "noise")
    inp = res.wave("in", "noise")
    assert freq.shape == out.shape == inp.shape == (201,)
    assert not np.iscomplexobj(out)
    # cached: a second read serves the same array object
    assert res.wave("out", "noise") is res._swept["noise"]["out"]


def test_measure_integrated_noise_on_spectre_result(noise_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(noise_raw_dir))
    onoise = measure(res, {"meas": "onoise_total", "out": "out"}, default_analysis="noise")
    inoise = measure(res, {"meas": "inoise_total", "out": "in"}, default_analysis="noise")
    assert onoise == pytest.approx(_expected_rms(_W_OUT), rel=1e-6)  # ≈ 10 µV rms
    assert inoise == pytest.approx(_expected_rms(_W_IN), rel=1e-6)  # ≈ 2 µV rms
    assert inoise < onoise  # input-referred is the output density divided by the gain


def test_missing_noise_psf_raises_on_wave(tmp_path: Path) -> None:
    assert read_swept_psf(tmp_path, "noise") == {}  # no noise.noise present
    res = SpectreSimResult({}, raw_dir=str(tmp_path))
    with pytest.raises(KeyError):
        res.wave("out", "noise")


def test_noise_analysis_builder_emits_contract_statement() -> None:
    # output-only (onoise) form: named `noise` → a `noise.noise` PSF; numeric start/stop
    line = noise_analysis("vout", start=1e3, stop=1e8, dec=50)
    assert line == "noise ( vout 0 ) noise start=1000 stop=100000000 dec=50"
    # input-referred form appends the iprobe (the AC input source instance)
    line_i = noise_analysis("vout", iprobe="VINP", start=1e3, stop=1e8, dec=20)
    assert line_i == "noise ( vout 0 ) noise start=1000 stop=100000000 dec=20 iprobe=VINP"
    # a non-default reference node is honored
    assert noise_analysis("outp", "outn", dec=10).startswith("noise ( outp outn ) noise")
