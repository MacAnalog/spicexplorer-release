"""LIVE golden chopper benches on the analog-db `ia_002` tsmc-n65 binding (opt-in).

The full config-driven stack, end to end: binding YAMLs → raw deck → translate (incl.
the `ac`→mag=+pacmag= marker and vcvs sense nodes) → template-DB `pss`+`pac` /
`pss`+`pnoise` composition → generic→kit corner shim → virtuoso-bridge Spectre →
swept-PSF reader (`pac.0.pac` baseband / `pnoise.pnoise`) → engine-neutral registry.

Golden figures ride the registry route (no datasheet rows — the stb posture; datasheet
conformance stays engine-neutral):

* ``pac_gain``       — {meas: gain_cl | dcgain, analysis: pac, out: vout} — the
  in-operation closed-loop gain the tran_chopper_ripple window approximates (cap-ratio
  Cin/Cfb = 20 ideal; the no-CMFB output-CM wander is the known detractor).
* ``pac_zin``        — {meas: zin_mag, analysis: pac, out: vzd, ref: vzs, scale: 2·RS}
  — the chopped input impedance in series-sense form; theory 1/(2·fc·Cin) = 6.25 MΩ,
  tran measured ~12 MΩ (bootstrapping). KNOWN LIMITATION: on this DUT the pss does not
  converge in the driven-input configuration (the no-CMFB core + TG choppers leave a
  plateaued shooting bounce on chopper-internal nodes) — the test xfails until the
  core common-mode closure; the pac impedance READ path itself is live-validated by
  test_pac_ideal_chopper_live.py.
* ``pnoise_chopped`` — {meas: onoise_pnoise_total, out: out} — chopped output noise.

Opt-in gating mirrors `test_amp022_tsmc65_configdriven_live.py`: bridge importable +
`SPICEXPLORER_TSMC65_MODEL_ROOT` holding the neutral corner wrapper.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_CIRCUIT = "ia_002_fan_chopper_simple"
_PDK = "tsmc-n65"
_MODEL_ROOT = os.environ.get("SPICEXPLORER_TSMC65_MODEL_ROOT", "")

_needs_live = pytest.mark.skipif(
    not (_MODEL_ROOT and (Path(_MODEL_ROOT).expanduser() / "tsmc_n65_models.scs").is_file()),
    reason="set SPICEXPLORER_TSMC65_MODEL_ROOT to a dir holding the neutral corner wrapper",
)


def _run(testbench: str, tmp_path: Path):
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.analog_db import raw_deck_path, run_circuit

    if not raw_deck_path(_CIRCUIT, _PDK, testbench).is_file():
        pytest.skip(f"analog-db {_CIRCUIT}/{_PDK}/{testbench} raw deck not checked out")
    return run_circuit(
        _CIRCUIT,
        _PDK,
        testbench=testbench,
        model_lib_root=_MODEL_ROOT,
        deck_dir=tmp_path / "decks",
        work_dir=tmp_path / "raw",
        label=f"ia002_{testbench}_live",
    )


@_needs_live
def test_live_ia002_pac_gain(tmp_path: Path) -> None:
    from spicexplorer_core.measurements import measure

    run = _run("pac_gain", tmp_path)
    out = np.asarray(run.result.wave("vout", "pac"))
    assert out.dtype.kind == "c" and out.size >= 8, "pac baseband not captured as phasors"

    gain = measure(run.result, {"meas": "gain_cl", "analysis": "pac", "out": "vout"},
                   default_analysis="ac")
    gain_db = measure(run.result, {"meas": "dcgain", "analysis": "pac", "out": "vout"},
                      default_analysis="ac")
    # cap-ratio gain Cin/Cfb = 20 (26 dB) ideal; the drawn core has no CMFB, so accept a
    # broad band and record the number — the POINT is that PSS+PAC reads the in-operation
    # transfer at all (a static ac on the frozen network cannot).
    assert np.isfinite(gain) and gain > 2.0, f"chopped closed-loop gain implausible: {gain} V/V"
    assert gain < 100.0, f"chopped closed-loop gain implausible: {gain} V/V"
    assert gain_db == pytest.approx(20.0 * np.log10(gain), abs=0.1)

    # visual-verification seam: artifact_path() → waveview snapshot (traces + PNGs).
    # Composition stays caller-side (waveview is a peer tool — path in, artifacts out).
    art = run.artifact_path()
    assert art is not None and art.exists()
    from spicexplorer_waveview import load_traces, snapshot

    snap = snapshot(art, tmp_path / "snap", label="ia002_pac_gain",
                    annotations={"pac": {"gain_cl [V/V]": gain, "gain [dB]": gain_db}})
    assert snap["traces"] is not None and any("pac" in p.name for p in snap["pngs"])
    stored = load_traces(snap["traces"])  # the stored traces round-trip standalone
    assert "pac" in stored.analyses and stored.analyses["pac"].n_points >= 8


@_needs_live
def test_live_ia002_pac_zin(tmp_path: Path) -> None:
    from spicexplorer_core.measurements import measure

    run = _run("pac_zin", tmp_path)
    # series-sense read: Zin = 2*RS * |vzd/vzs| (RS = 1Meg per side in the bench),
    # at an in-band spot (100 Hz — the chopped Zin is flat across the baseband)
    try:
        zin = measure(
            run.result,
            {"meas": "zin_mag", "analysis": "pac", "out": "vzd", "ref": "vzs",
             "scale": 2.0e6, "f": 100.0},
            default_analysis="ac",
        )
    except KeyError:
        # no pac PSF ⇒ the pss beneath it did not converge — the DUT's documented
        # limitation (see the module docstring), not a bench/vocabulary failure
        pytest.xfail(
            "ia_002 pss does not converge on the driven-input (Zin) configuration — "
            "no-CMFB core + TG choppers (see pac_zin.yaml); revisit after P4-4b. "
            "The pac impedance read path is live-validated on the ideal chopper."
        )
    # theory 1/(2*fc*Cin) = 6.25 MΩ at 5 kHz/16 pF; the tran approximation measured
    # ~12 MΩ on ihp (feedback bootstrapping helps)
    assert 1.0e6 < zin < 1.0e9, f"chopped |Zin| implausible: {zin:.4g} Ω"


@_needs_live
def test_live_ia002_pnoise_chopped(tmp_path: Path) -> None:
    from spicexplorer_core.measurements import measure

    run = _run("pnoise_chopped", tmp_path)
    onoise = measure(run.result, {"meas": "onoise_pnoise_total", "out": "out"},
                     default_analysis="pnoise")
    spot = measure(run.result, {"meas": "pnoise_spot", "out": "out", "f": 1.0e3},
                   default_analysis="pnoise")
    assert np.isfinite(onoise) and 0.0 < onoise < 1.0, f"chopped onoise implausible: {onoise}"
    assert np.isfinite(spot) and spot > 0.0, f"chopped spot density implausible: {spot}"
