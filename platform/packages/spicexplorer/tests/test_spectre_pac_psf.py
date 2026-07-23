"""PAC — Spectre periodic-AC swept-PSF reading + `pac_analysis` composer (offline).

A Spectre `pac` analysis (riding a preceding `pss`) writes ONE PSF per sideband —
`pac.<k>.pac` is harmonic k — plus a metadata-only `pac.pac` "pac parent" index. The
signal-band transfer of a chopper / switched-cap circuit is the BASEBAND response
(harmonic 0), so the reader pins the `pac` analysis to the `pac.0.pac` sibling (the same
"pick the meaningful sibling" rule that pins `pss` to `.fd.pss`). These tests generate a
minimal *analytic* complex `pac.0.pac` (no simulator, no PDK) and prove, on the same
reader path validated live on an ideal chopper (2026-07-17, baseband gain 100 V/V ==
the amp gain):

* :func:`read_swept_psf` selects `pac.0.pac` and is NOT confused by the `pac.pac` parent,
  a non-baseband sideband `pac.1.pac`, or the glob-boundary `pac.10.pac`,
* the sweep is aliased to the canonical ``frequency`` abscissa,
* :meth:`SpectreSimResult.wave` serves the complex baseband response via the swept-PSF
  fallback,
* :func:`pac_analysis` emits a contract-correct Spectre statement (named ``pac`` → the
  `pac.pac`/`pac.<k>.pac` family; numeric start/stop, the eng-suffix-case landmine).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from spicexplorer.backends.spectre import SpectreSimResult, read_swept_psf
from spicexplorer.backends.spectre_deck import pac_analysis

_F_LO, _F_HI = 1.0, 2.0e3  # baseband sweep (well inside the chop period)
_GAIN = 100.0  # flat baseband gain, V/V — a chopper conveying its signal band


def _pac_psf_text(gain: float, *, npts: int = 21) -> str:
    """A minimal valid psfascii swept-PAC file: complex ``out`` = a flat baseband gain."""
    freqs = np.logspace(np.log10(_F_LO), np.log10(_F_HI), npts)
    lines = [
        "HEADER",
        '"PSFversion" "1.00"',
        '"simulator" "spectre"',
        '"analysis type" "pac"',
        "TYPE",
        '"sweep" FLOAT DOUBLE PROP(',
        '"key" "sweep"',
        ")",
        '"V" COMPLEX DOUBLE PROP(',
        '"units" "V"',
        ")",
        "SWEEP",
        '"freq" "sweep" PROP(',
        '"units" "Hz"',
        ")",
        "TRACE",
        '"out" "V"',
        "VALUE",
    ]
    for f in freqs:
        lines.append(f'"freq" {f:.15e}')
        lines.append(f'"out" ({gain:.15e} 0.000000000000000e+00)')
    lines.append("END")
    return "\n".join(lines) + "\n"


@pytest.fixture()
def pac_raw_dir(tmp_path: Path) -> Path:
    # harmonic 0 (baseband) — the response the reader must serve for `pac`
    (tmp_path / "pac.0.pac").write_text(_pac_psf_text(_GAIN))
    # decoys that must NOT win: the metadata-only parent, a non-baseband sideband, and the
    # glob-boundary file (`*.0.pac` must NOT match `pac.10.pac`).
    (tmp_path / "pac.pac").write_text("PSF parent index — not node data\n")
    (tmp_path / "pac.1.pac").write_text(_pac_psf_text(5.0))
    (tmp_path / "pac.10.pac").write_text(_pac_psf_text(7.0))
    return tmp_path


def test_read_swept_psf_selects_baseband_pac0(pac_raw_dir: Path) -> None:
    sigs = read_swept_psf(pac_raw_dir, "pac")
    assert "out" in sigs
    assert "freq" in sigs and "frequency" in sigs  # canonical abscissa alias
    assert np.allclose(sigs["frequency"], sigs["freq"])
    assert len(sigs["frequency"]) == len(sigs["out"]) == 21
    # the BASEBAND gain (harmonic 0), not the sideband (5) or the glob-boundary (7) decoys
    assert np.iscomplexobj(sigs["out"])
    assert np.abs(sigs["out"][0]) == pytest.approx(_GAIN)


def test_wave_falls_back_to_baseband_pac_psf(pac_raw_dir: Path) -> None:
    res = SpectreSimResult({}, raw_dir=str(pac_raw_dir))
    freq = res.wave("frequency", "pac")
    out = res.wave("out", "pac")
    assert freq.shape == out.shape == (21,)
    assert np.abs(out).min() == pytest.approx(_GAIN, rel=1e-9)
    # cached: a second read serves the same array object
    assert res.wave("out", "pac") is res._swept["pac"]["out"]


def test_missing_pac_psf_raises_on_wave(tmp_path: Path) -> None:
    # only the parent index present — no baseband harmonic, so nothing to serve
    (tmp_path / "pac.pac").write_text("parent only\n")
    assert read_swept_psf(tmp_path, "pac") == {}
    res = SpectreSimResult({}, raw_dir=str(tmp_path))
    with pytest.raises(KeyError):
        res.wave("out", "pac")


def test_pac_analysis_builder_emits_contract_statement() -> None:
    line = pac_analysis(start=1.0, stop=1.0e5, dec=20, maxsideband=7)
    tokens = line.split()
    assert tokens[0] == "pac" and tokens[1] == "pac"  # named `pac` (P0 PSF-key contract)
    assert "start=1" in line and "stop=100000" in line
    assert "dec=20" in line and "maxsideband=7" in line


def test_sideband_selection_via_analysis_spelling(pac_raw_dir: Path) -> None:
    """`pac.<k>` reads the k-th sideband PSF (conversion-gain / ripple analysis) —
    the fixture's sidebands carry distinct gains (k=1 → 5, k=10 → 7), so a wrong
    sibling pick is unmistakable. Plain `pac` stays the baseband."""
    assert np.abs(read_swept_psf(pac_raw_dir, "pac.1")["out"][0]) == pytest.approx(5.0)
    assert np.abs(read_swept_psf(pac_raw_dir, "pac.10")["out"][0]) == pytest.approx(7.0)
    assert np.abs(read_swept_psf(pac_raw_dir, "pac.0")["out"][0]) == pytest.approx(_GAIN)
    res = SpectreSimResult({}, raw_dir=str(pac_raw_dir))
    assert np.abs(res.wave("out", "pac.1")).max() == pytest.approx(5.0)
    # abscissa aliasing works on a sideband read too
    assert res.wave("frequency", "pac.1").shape == (21,)
    # a sideband Spectre never wrote is a hard miss, like any absent wave
    with pytest.raises(KeyError):
        res.wave("out", "pac.7")


def test_registry_recipes_read_pac_baseband(pac_raw_dir: Path) -> None:
    """The engine-neutral registry reads the periodic-AC baseband via `{analysis: pac}`:
    the closed-loop gain recipes and the new `zin_mag` (unit-current drive → the node
    voltage IS the impedance)."""
    from spicexplorer_core.measurements import measure

    res = SpectreSimResult({}, raw_dir=str(pac_raw_dir))
    gain = measure(res, {"meas": "gain_cl", "analysis": "pac", "out": "out"}, default_analysis="ac")
    assert gain == pytest.approx(_GAIN, rel=1e-6)
    gain_db = measure(res, {"meas": "dcgain", "analysis": "pac", "out": "out"}, default_analysis="ac")
    assert gain_db == pytest.approx(40.0, abs=1e-6)
    # zin_mag: with pacmag=1 on a current source the flat 100 V wave reads as 100 Ω
    zin = measure(res, {"meas": "zin_mag", "analysis": "pac", "out": "out"}, default_analysis="ac")
    assert zin == pytest.approx(_GAIN, rel=1e-6)
    zin_spot = measure(
        res, {"meas": "zin_mag", "analysis": "pac", "out": "out", "f": 1.0e3},
        default_analysis="ac",
    )
    assert zin_spot == pytest.approx(_GAIN, rel=1e-6)
