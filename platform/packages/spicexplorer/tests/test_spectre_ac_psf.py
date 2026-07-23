"""Spectre swept-PSF (AC) reader + `SpectreSimResult.wave` fallback (offline, deterministic).

The bridge returns only a flat scalar dict (op-point / dc node values); a frequency-domain
AC transfer lands in its own psfascii PSF (`ac.ac`) in the persisted `-raw` dir. These tests
generate a minimal *analytic* single-pole `ac.ac` (no simulator, no PDK) and prove:

* :func:`read_swept_psf` parses it (sweep vector aliased to the canonical ``frequency``),
* :meth:`SpectreSimResult.wave` serves the AC waves via the swept-PSF fallback, and
* the engine-neutral measurement registry extracts dcgain / ugf / pm off the Spectre result —
  the same math path validated live on TSMC-65.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
from spicexplorer.backends.spectre import SpectreSimResult, read_swept_psf
from spicexplorer_core.measurements import measure

# Single-pole transfer: H(f) = A0 / (1 + j f/fp). A0=100 (40 dB), fp=1 kHz.
_A0 = 100.0
_FP = 1.0e3


def _write_ac_psf(path: Path, out_name: str = "vout") -> None:
    """Emit a minimal valid psfascii AC file for the single-pole transfer at ``path``."""
    freqs = np.logspace(0, 8, 241)  # 1 Hz .. 100 MHz, dense enough for a clean UGF/PM
    h = _A0 / (1.0 + 1j * freqs / _FP)
    lines = [
        "HEADER",
        '"PSFversion" "1.00"',
        '"simulator" "spectre"',
        '"analysis type" "ac"',
        "TYPE",
        '"sweep" FLOAT DOUBLE PROP(',
        '"key" "sweep"',
        ")",
        '"V" COMPLEX DOUBLE PROP(',
        '"units" "V"',
        '"key" "node"',
        ")",
        "SWEEP",
        '"freq" "sweep" PROP(',
        '"sweep_direction" 0',
        '"units" "Hz"',
        ")",
        "TRACE",
        f'"{out_name}" "V"',
        "VALUE",
    ]
    for f, hv in zip(freqs, h):
        lines.append(f'"freq" {f:.15e}')
        lines.append(f'"{out_name}" ({hv.real:.15e} {hv.imag:.15e})')
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


@pytest.fixture()
def ac_raw_dir(tmp_path: Path) -> Path:
    _write_ac_psf(tmp_path / "ac.ac")
    return tmp_path


def test_read_swept_psf_parses_ac_and_aliases_frequency(ac_raw_dir: Path) -> None:
    sigs = read_swept_psf(ac_raw_dir, "ac")
    assert "vout" in sigs
    # sweep exposed under both the PSF name and the registry's canonical abscissa
    assert "freq" in sigs and "frequency" in sigs
    assert np.allclose(sigs["frequency"], sigs["freq"])
    assert sigs["vout"].dtype == np.complex128
    assert len(sigs["frequency"]) == len(sigs["vout"]) == 241
    assert abs(sigs["vout"][0]) == pytest.approx(_A0, rel=1e-3)  # |H| at 1 Hz ≈ A0


def test_wave_falls_back_to_swept_psf(ac_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(ac_raw_dir))
    freq = res.wave("frequency", "ac")
    vout = res.wave("vout", "ac")
    assert freq.shape == vout.shape == (241,)
    assert np.iscomplexobj(vout)
    # cached: a second read doesn't re-parse into a different object identity per call
    assert res.wave("vout", "ac") is res._swept["ac"]["vout"]


def test_measure_ac_metrics_on_spectre_result(ac_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(ac_raw_dir))
    dcgain = measure(res, {"meas": "dcgain", "out": "vout"}, default_analysis="ac")
    ugf = measure(res, {"meas": "ugf", "out": "vout"}, default_analysis="ac")
    pm = measure(res, {"meas": "pm", "out": "vout"}, default_analysis="ac")
    assert dcgain == pytest.approx(20.0 * math.log10(_A0), abs=0.1)   # 40 dB
    assert ugf == pytest.approx(_A0 * _FP, rel=0.05)                  # ≈ A0·fp = 1e5 Hz
    assert pm == pytest.approx(90.0, abs=2.0)                         # single pole → ~90°


def test_flat_scalar_still_wins_over_swept(ac_raw_dir: Path) -> None:
    # A merged canonical scalar / flat op key is authoritative; the swept PSF is only a
    # fallback for waves the flat dict lacks.
    res = SpectreSimResult({"ac_vout": 1.23}, raw_dir=str(ac_raw_dir))
    assert res.scalar("vout", "ac") == pytest.approx(1.23)


def test_missing_or_non_swept_returns_empty(tmp_path: Path) -> None:
    assert read_swept_psf(None, "ac") == {}
    assert read_swept_psf(tmp_path, "op") == {}          # op-point is not a swept analysis
    assert read_swept_psf(tmp_path, "ac") == {}          # no ac.ac present
    res = SpectreSimResult({}, raw_dir=str(tmp_path))
    with pytest.raises(KeyError):
        res.wave("vout", "ac")
