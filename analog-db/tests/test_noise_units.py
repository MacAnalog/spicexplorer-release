"""Unit gate on the ``.noise`` integrated totals: ngspice already returns them as RMS.

ngspice's ``.noise`` reports ``onoise_total``/``inoise_total`` as the INTEGRATED RMS quantity
(V rms at the output, A or V per the input reference) — it takes the square root itself when it
accumulates the band. It does NOT report the mean-square ``V^2`` integral, so a testbench that
writes ``sqrt(onoise_total)`` reports the square root of an RMS voltage: dimensionally wrong, and
wrong by a factor ``1/sqrt(x)`` that GROWS as the true noise falls (the quieter the circuit, the
more the number is inflated).

That is not hypothetical. The ``ldo`` class template shipped ``let vn_out_rms = sqrt(onoise_total)``
and every recorded LDO ``vn_out_rms`` — and every ``datasheet.yaml`` limit calibrated beside one —
was the square root of the real answer, reading ~12 mVrms where the circuits are ~150 uVrms.

Measured (ngspice-45, 1 kOhm at 27 C, ``noise v(out) V1 dec 10 1 1meg``)::

    onoise_total        = 4.071369e-06      <- matches sqrt(4kTR*df) = 4.07e-06 V rms
    sqrt(onoise_total)  = 2.017763e-03      <- what the buggy template printed

:func:`test_no_rendered_deck_takes_a_second_sqrt` guards the TEMPLATES (the shared fresh render),
and :func:`test_no_committed_raw_deck_takes_a_second_sqrt` guards the committed ``raw/`` BYTES —
they are different artifacts. The render can only catch a bad template; a hand-edit that
reintroduced the sqrt directly into a committed deck would otherwise be caught only indirectly, by
the separate Tier-1 byte-drift check. :func:`test_ngspice_onoise_total_is_already_rms` is the live
proof of the premise, and is ``slow``-marked because it needs a real ngspice.
"""

from __future__ import annotations

import math
import re
import shutil

import pytest

from spicexplorer_analog_db import paths
from spicexplorer_analog_db import runner as runmod

# `sqrt` applied to an integrated total, in any spelling ngspice accepts — on a LIVE deck line,
# not a `*`-prefixed SPICE comment (the fixed template documents the old buggy expression in prose).
_SECOND_SQRT = re.compile(
    r"^(?!\s*\*).*sqrt\s*\(\s*[io]noise_total\s*\)", re.IGNORECASE | re.MULTILINE
)


@pytest.mark.corpus
def test_no_rendered_deck_takes_a_second_sqrt(generated_decks: dict[str, str]) -> None:
    """No committed/rendered deck may square-root an already-RMS integrated noise total."""
    offenders = sorted(name for name, text in generated_decks.items() if _SECOND_SQRT.search(text))
    assert not offenders, (
        "these decks take a second sqrt of an ngspice integrated noise total "
        f"(already V rms — see this module's docstring): {offenders}"
    )


@pytest.mark.corpus
def test_no_committed_raw_deck_takes_a_second_sqrt() -> None:
    """Same rule, applied to the committed ``raw/**/*.spice`` BYTES rather than a fresh render.

    The render guard above proves the templates are clean; this one proves the decks a clone
    actually runs are clean, which is not the same statement.
    """
    root = paths.db_root() / "raw"
    decks = sorted(root.rglob("*.spice"))
    assert decks, f"no committed raw decks under {root} — the layout moved"
    offenders = sorted(
        str(f.relative_to(root)) for f in decks if _SECOND_SQRT.search(f.read_text())
    )
    assert not offenders, (
        "these COMMITTED decks take a second sqrt of an ngspice integrated noise total "
        f"(already V rms — see this module's docstring): {offenders}"
    )


@pytest.mark.corpus
def test_ldo_noise_decks_bind_vn_out_rms_to_onoise_total(generated_decks: dict[str, str]) -> None:
    """The ``ldo`` noise bench keeps the metric NAME ``vn_out_rms`` (datasheet extraction and the
    scoreboard key on it) and binds it to ``onoise_total`` unchanged."""
    decks = {n: t for n, t in generated_decks.items() if "/noise.spice" in n and "/ldo_" in n}
    assert decks, "no ldo noise decks in the render — the fixture or the class binding moved"
    for name, text in decks.items():
        assert re.search(r"let\s+vn_out_rms\s*=\s*onoise_total\s*$", text, re.M), (
            f"{name}: expected `let vn_out_rms = onoise_total`"
        )


@pytest.mark.slow
def test_ngspice_onoise_total_is_already_rms() -> None:
    """The premise, measured: a 1 kOhm resistor's ``onoise_total`` equals sqrt(4kTR*df), NOT 4kTR*df.

    Resistor-only, so there is no PDK dependency — this needs nothing but ngspice on PATH.
    """
    if shutil.which("ngspice") is None:
        pytest.skip("ngspice not on PATH")

    deck = (
        "* thermal noise of a 1k resistor -- the .noise integrated-total unit check\n"
        "R1 out 0 1k\n"
        "V1 in 0 dc 0 ac 1\n"
        "Rlink in out 1e12\n"
        ".options temp=27\n"
        ".control\n"
        "  set filetype=ascii\n"
        "  noise v(out) V1 dec 10 1 1meg\n"
        "  print onoise_total\n"
        ".endc\n"
        ".end\n"
    )
    measures, _failed = runmod.parse_measures(runmod.local_runner(deck))
    onoise = measures["onoise_total"]

    # 4kTR*df with k=1.380649e-23, T=300.15 K (27 C), R=1k, df = 1 MHz - 1 Hz
    mean_square = 4 * 1.380649e-23 * 300.15 * 1e3 * (1e6 - 1.0)
    rms = math.sqrt(mean_square)

    assert onoise == pytest.approx(rms, rel=0.05), (
        f"onoise_total={onoise:.6e} should be the RMS {rms:.6e} V, "
        f"not the mean-square {mean_square:.6e} V^2"
    )
    # and unambiguously NOT the mean-square: the two differ by ~5 orders of magnitude here
    assert onoise > 1e3 * mean_square
