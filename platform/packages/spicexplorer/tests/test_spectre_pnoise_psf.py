"""Spectre periodic-noise swept-PSF reading + `pnoise_analysis` composer (offline).

A Spectre `pnoise` analysis (riding a preceding `pss`) lands its output/input-referred
densities in their own psfascii PSF (`pnoise.pnoise`) in the persisted `-raw` dir — the
same shape as `noise.noise` (sweep `freq`, top-level `out`/`in` V/√Hz + `gain`), plus a
`pnoise.pnoise.cache` sibling Spectre also writes (discovered live on the closed lane, 2026-07-11).
These tests generate a minimal *analytic* white-noise `pnoise.pnoise` (no simulator, no
PDK) and prove, on the same reader/registry path validated live:

* :func:`read_swept_psf` parses it (sweep aliased to ``frequency``) and is NOT confused by
  the ``.cache`` sibling or a coexisting small-signal ``noise.noise``,
* :meth:`SpectreSimResult.wave` serves the densities via the swept-PSF fallback,
* the registry's ``onoise_pnoise_total`` / ``inoise_pnoise_total`` integrate to a closed-form
  RMS, ``pnoise_spot`` reads the density at an offset, ``phase_noise_dbc`` converts it to a
  noise-to-carrier ratio,
* :func:`pnoise_analysis` emits a contract-correct Spectre statement (named ``pnoise`` →
  a ``pnoise.pnoise`` PSF; ``refsideband`` present exactly when ``iprobe`` is).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from spicexplorer.backends.spectre import SpectreSimResult, read_swept_psf
from spicexplorer.backends.spectre_deck import pnoise_analysis
from spicexplorer_core.measurements import measure

# Flat (white) one-sided spectral densities, V/√Hz. Constant ⇒ the trapezoid integral is
# exact, so RMS = W·√(f_hi − f_lo) closed-form.
_W_OUT = 150.0e-9  # 150 nV/√Hz output-referred (periodic drive)
_W_IN = 30.0e-9  # 30 nV/√Hz input-referred
_F_LO, _F_HI = 1.0e3, 4.0e7  # Spectre clips the pnoise band top (observed live)


def _psf_text(kind: str, w_out: float, w_in: float) -> str:
    """A minimal valid psfascii swept-noise file with flat ``out``/``in`` densities."""
    freqs = np.logspace(np.log10(_F_LO), np.log10(_F_HI), 101)
    lines = [
        "HEADER",
        '"PSFversion" "1.00"',
        '"simulator" "spectre"',
        f'"analysis type" "{kind}"',
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
    for f in freqs:
        lines.append(f'"freq" {f:.15e}')
        lines.append(f'"out" {w_out:.15e}')
        lines.append(f'"in" {w_in:.15e}')
    lines.append("END")
    return "\n".join(lines) + "\n"


@pytest.fixture()
def pnoise_raw_dir(tmp_path: Path) -> Path:
    (tmp_path / "pnoise.pnoise").write_text(_psf_text("pnoise", _W_OUT, _W_IN))
    # the live -raw dir also carries a cache sibling and (often) a small-signal noise PSF
    # with DIFFERENT densities — neither may leak into the pnoise read.
    (tmp_path / "pnoise.pnoise.cache").write_text("not a psf\n")
    (tmp_path / "noise.noise").write_text(_psf_text("noise", 1.0e-9, 1.0e-9))
    return tmp_path


def test_read_swept_psf_parses_pnoise_and_ignores_siblings(pnoise_raw_dir: Path) -> None:
    sigs = read_swept_psf(pnoise_raw_dir, "pnoise")
    assert "out" in sigs and "in" in sigs
    assert "freq" in sigs and "frequency" in sigs  # canonical abscissa alias
    assert np.allclose(sigs["frequency"], sigs["freq"])
    assert len(sigs["frequency"]) == len(sigs["out"]) == 101
    # the pnoise densities, not the small-signal noise.noise ones
    assert sigs["out"][0] == pytest.approx(_W_OUT)
    # …and the noise read still gets its own file, untouched by pnoise.pnoise
    noise = read_swept_psf(pnoise_raw_dir, "noise")
    assert noise["out"][0] == pytest.approx(1.0e-9)


def test_wave_falls_back_to_swept_pnoise_psf(pnoise_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(pnoise_raw_dir))
    freq = res.wave("frequency", "pnoise")
    out = res.wave("out", "pnoise")
    inp = res.wave("in", "pnoise")
    assert freq.shape == out.shape == inp.shape == (101,)
    # cached: a second read serves the same array object
    assert res.wave("out", "pnoise") is res._swept["pnoise"]["out"]


def test_measure_pnoise_recipes_on_spectre_result(pnoise_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(pnoise_raw_dir))
    band = np.sqrt(_F_HI - _F_LO)
    onoise = measure(res, {"meas": "onoise_pnoise_total", "out": "out"}, default_analysis="pnoise")
    inoise = measure(res, {"meas": "inoise_pnoise_total", "out": "in"}, default_analysis="pnoise")
    assert onoise == pytest.approx(_W_OUT * band, rel=1e-6)
    assert inoise == pytest.approx(_W_IN * band, rel=1e-6)
    assert inoise < onoise
    spot = measure(res, {"meas": "pnoise_spot", "out": "out", "f": 1.0e6}, default_analysis="pnoise")
    assert spot == pytest.approx(_W_OUT, rel=1e-9)
    l_f = measure(
        res,
        {"meas": "phase_noise_dbc", "out": "out", "f": 1.0e6, "carrier_ampl": 0.1},
        default_analysis="pnoise",
    )
    assert l_f == pytest.approx(10.0 * np.log10(_W_OUT**2 / (0.1**2 / 2.0)), abs=1e-9)


def test_missing_pnoise_psf_raises_on_wave(tmp_path: Path) -> None:
    assert read_swept_psf(tmp_path, "pnoise") == {}
    res = SpectreSimResult({}, raw_dir=str(tmp_path))
    with pytest.raises(KeyError):
        res.wave("out", "pnoise")


def test_pnoise_analysis_builder_emits_contract_statement() -> None:
    # output-only form: named `pnoise` → a `pnoise.pnoise` PSF; numeric start/stop
    line = pnoise_analysis("vout", start=1e3, stop=1e8, dec=20)
    assert line == "pnoise ( vout 0 ) pnoise start=1000 stop=100000000 dec=20 maxsideband=7"
    # input-referred form appends iprobe AND refsideband (Spectre errors without the
    # latter when an input probe is present — SPECTRE-16066)
    line_i = pnoise_analysis("vout", iprobe="Vinp", maxsideband=5, dec=10)
    assert line_i.endswith("dec=10 maxsideband=5 iprobe=Vinp refsideband=0")
    # a non-default reference node and refsideband are honored
    line_r = pnoise_analysis("outp", "outn", iprobe="Vin", refsideband=1)
    assert line_r.startswith("pnoise ( outp outn ) pnoise")
    assert line_r.endswith("iprobe=Vin refsideband=1")
    # refsideband is meaningless (and omitted) without an iprobe
    assert "refsideband" not in pnoise_analysis("vout")
