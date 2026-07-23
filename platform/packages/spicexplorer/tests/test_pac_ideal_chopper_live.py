"""LIVE PSS+PAC on a self-contained IDEAL CHOPPER — validates `pac_analysis` end-to-end.

The golden analysis for a chopper / switched-cap gain is Spectre **periodic AC** (`pac`)
riding a **periodic steady state** (`pss`): the operating point is periodic (the chop
clock), not DC, so a static `ac` on the frozen network reads ~0. This test builds a
textbook chopper entirely from IDEAL Spectre primitives (no PDK, no NDA models) —

    sig --[x sq]--> modulator --> gain(100)+pole --> [x sq] demodulator --> LPF --> out

drives the chop square at fund = 5 kHz, and reads the BASEBAND (`pac.0.pac`) small-signal
transfer from `sig` (pacmag = 1) to `out`. It must recover the amplifier gain (100 V/V =
40 dB) across the signal band — i.e. the chopper conveys the baseband — proving Spectre
accepts the emitted `pac` statement, produces the per-sideband PSF family, and that the
reader serves the harmonic-0 sibling.

Opt-in: needs the bridge importable AND a configured local Spectre profile
(`SPICEXPLORER_VB_ENV_FILE`); skips everywhere else. No PDK / model library required.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_ENV_FILE = os.environ.get("SPICEXPLORER_VB_ENV_FILE", "")

FCHOP = 5.0e3
TCHOP = 1.0 / FCHOP

# Z_in fixture values (the impedance test): Rin ∥ Cin at the chopper input, corner at 1 kHz.
RIN = 50.0e3
CIN = 1.0 / (2.0 * np.pi * RIN * 1.0e3)  # → f_c = 1 kHz exactly


def _chop_clock() -> str:
    return (
        f"Vsq ( sq 0 ) vsource type=pulse val0=-1 val1=1 period={TCHOP:.10g} "
        f"rise=1e-9 fall=1e-9 width={TCHOP / 2 - 1e-9:.10g}"
    )


def _chopper_core() -> list[str]:
    return [
        "Bmod ( ma 0 ) bsource v=v(sig)*v(sq)",             # up-modulate: sig x square
        "Eamp ( ea 0 ma 0 ) vcvs gain=100",                 # ideal gain block
        "Ra ( ea amp ) resistor r=1e3",                     # amp output pole (159 MHz)
        "Ca ( amp 0 ) capacitor c=1e-12",
        "Bdem ( dm 0 ) bsource v=v(amp)*v(sq)",             # down-modulate: amp x square
        "Ro ( dm out ) resistor r=1e4",                     # output LPF (159 kHz)
        "Co ( out 0 ) capacitor c=1e-10",
    ]


def _ideal_chopper_stimulus() -> str:
    return "\n".join([
        _chop_clock(),
        "Vsig ( sig 0 ) vsource dc=0 pacmag=1 pacphase=0",  # PAC small-signal excitation
        *_chopper_core(),
    ])


def _ideal_chopper_zin_stimulus() -> str:
    # pacmag=1 on a CURRENT source: the observed node voltage IS the input impedance
    # (V = Z·I with I = 1). The input network is a known Rin ∥ Cin; the chopper behind
    # it senses v(sig) through an ideal bsource (no loading), so the analytic answer is
    # |Z| = Rin at the low edge, Rin/√2 at the 1 kHz corner — while the operating point
    # is genuinely periodic (the pss chop drive runs underneath).
    return "\n".join([
        _chop_clock(),
        "Iin ( 0 sig ) isource dc=0 pacmag=1",              # unit small-signal current INTO sig
        f"Rin ( sig 0 ) resistor r={RIN:.10g}",
        f"Cin ( sig 0 ) capacitor c={CIN:.10e}",
        *_chopper_core(),
    ])


@pytest.mark.skipif(
    not (_ENV_FILE and Path(_ENV_FILE).expanduser().is_file()),
    reason="set SPICEXPLORER_VB_ENV_FILE to a configured local Spectre bridge profile",
)
def test_live_ideal_chopper_pac_baseband_gain(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.spectre import create_spectre_simulator
    from spicexplorer.backends.spectre_deck import (
        deck_spec_from_native,
        pac_analysis,
        pss_analysis,
    )

    spec = deck_spec_from_native(
        title="ideal chopper PSS+PAC (fund=5 kHz)",
        stimulus=_ideal_chopper_stimulus(),
        analyses=(
            pss_analysis(FCHOP, harms=21, tstab=5 * TCHOP),
            pac_analysis(start=1.0, stop=2.0e3, dec=8, maxsideband=15),
        ),
    )

    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=tmp_path / "decks",
        vb_env_file=Path(_ENV_FILE).expanduser(),
        work_dir=str(tmp_path / "raw"),
    )
    result = sim.run(label="ideal_chopper_pac_live")

    # the baseband (harmonic-0) small-signal transfer, sig -> out, read via the pac reader
    freq = np.asarray(result.wave("frequency", "pac"))
    out = np.asarray(result.wave("out", "pac"))
    assert out.dtype.kind == "c" and out.size >= 8, "pac baseband not captured as phasors"
    assert freq.size == out.size

    mag = np.abs(out)
    # the chopper conveys its signal band: baseband gain == the amp gain (100 V/V = 40 dB)
    assert mag.min() == pytest.approx(100.0, rel=0.05), f"chopper baseband gain off: {mag.min()} V/V"
    # …and it is essentially flat across the baseband (no roll-off inside 1 Hz–2 kHz)
    assert mag.max() / mag.min() < 1.1, f"baseband not flat: {mag.min()}..{mag.max()} V/V"


@pytest.mark.skipif(
    not (_ENV_FILE and Path(_ENV_FILE).expanduser().is_file()),
    reason="set SPICEXPLORER_VB_ENV_FILE to a configured local Spectre bridge profile",
)
def test_live_ideal_chopper_pac_input_impedance(tmp_path: Path) -> None:
    """The PAC impedance read: `pacmag=1` on a *current* source makes
    the baseband node voltage the input impedance. Known network (Rin ∥ Cin, corner at
    1 kHz) under a genuinely periodic operating point; read both as a raw wave and
    through the engine-neutral `{meas: zin_mag, analysis: pac}` registry recipe."""
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")

    from spicexplorer.backends.spectre import create_spectre_simulator
    from spicexplorer.backends.spectre_deck import (
        deck_spec_from_native,
        pac_analysis,
        pss_analysis,
    )
    from spicexplorer_core.measurements import measure

    spec = deck_spec_from_native(
        title="ideal chopper PSS+PAC input impedance (Rin || Cin, fc=1 kHz)",
        stimulus=_ideal_chopper_zin_stimulus(),
        analyses=(
            pss_analysis(FCHOP, harms=21, tstab=5 * TCHOP),
            pac_analysis(start=1.0, stop=2.0e3, dec=8, maxsideband=15),
        ),
    )
    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=tmp_path / "decks",
        vb_env_file=Path(_ENV_FILE).expanduser(),
        work_dir=str(tmp_path / "raw"),
    )
    result = sim.run(label="ideal_chopper_pac_zin_live")

    freq = np.asarray(result.wave("frequency", "pac"))
    zwave = np.abs(np.asarray(result.wave("sig", "pac")))  # V under 1 A ⇒ ohms
    assert freq.size == zwave.size >= 8

    # low edge: the resistive plateau
    assert zwave[np.argmin(freq)] == pytest.approx(RIN, rel=0.03), f"Z_in plateau off: {zwave[0]:.4g}"
    # the same numbers through the registry recipe (the chopper-bench vocabulary)
    zin_lo = measure(result, {"meas": "zin_mag", "analysis": "pac", "out": "sig"},
                     default_analysis="ac")
    assert zin_lo == pytest.approx(RIN, rel=0.03)
    zin_fc = measure(result, {"meas": "zin_mag", "analysis": "pac", "out": "sig", "f": 1.0e3},
                     default_analysis="ac")
    assert zin_fc == pytest.approx(RIN / np.sqrt(2.0), rel=0.07), (
        f"|Z| at the 1 kHz corner should be Rin/√2: {zin_fc:.4g}"
    )
