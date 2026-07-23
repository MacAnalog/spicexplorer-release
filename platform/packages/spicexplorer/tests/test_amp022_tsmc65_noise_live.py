"""LIVE input/output-referred noise on the analog-db `amp_022` tsmc-n65 deck (opt-in).

End-to-end proof that a Spectre `noise` analysis on the registered
`amp_022_fer_two_stage / pdk tsmc-n65` node yields the canonical Tier-1 integrated-noise
figures of merit through the engine-neutral measurement registry: composes the analog-db raw
deck via the translator, runs a DC op-point + noise sweep over the virtuoso-bridge, and
integrates `onoise_total` / `inoise_total` off the `SpectreSimResult` (whose noise densities
come from the swept-PSF reader reading `noise.noise`).

Opt-in gating mirrors `test_amp022_tsmc65_ac_live.py` (bridge importable + `SPICEXPLORER_TSMC65_MODELS`
+ the analog-db raw deck present); it skips everywhere else. Point `SPICEXPLORER_ANALOG_DB` at a
populated analog-db checkout when running from a worktree whose submodule is empty.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_TSMC65_MODELS", "")

# TB conditions (TSMC-65 core rail 1.2 V); sizing comes from the committed binding.
_TB = {"vdd": 1.2, "vcm": 0.6, "ibias": "20u", "cl": "500f"}


def _sizing() -> dict[str, str]:
    # sizing.yaml defaults, read from the SAME analog-db checkout as the raw deck —
    # never hand-transcribed (the 2026-07-13 knob rename made hardcoded dicts drift).
    from spicexplorer.backends.analog_db import load_sizing

    return load_sizing("amp_022_fer_two_stage", "tsmc-n65")


def _raw_deck() -> Path:
    from spicexplorer_core import project_root

    root = Path(os.environ.get("SPICEXPLORER_ANALOG_DB") or (project_root() / "examples/analog-db"))
    return root / "raw/amp_022_fer_two_stage/tsmc-n65/noise.spice"


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_TSMC65_MODELS to the TSMC-65 Spectre model library",
)
def test_live_amp022_tsmc65_noise_metrics(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    deck = _raw_deck()
    if not deck.is_file():
        pytest.skip(f"analog-db tsmc-n65 raw deck not found ({deck}); set SPICEXPLORER_ANALOG_DB")

    from spicexplorer.backends.spectre import create_spectre_simulator, operating_point
    from spicexplorer.backends.spectre_deck import (
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
        noise_analysis,
    )
    from spicexplorer_core.measurements import measure
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

    spec = deck_spec_from_ngspice(
        deck, pdk="tsmc-n65", source_pdk="tsmc-n65",
        analyses=(dc_oppoint_analysis(), noise_analysis("vout", iprobe="VINP",
                                                        start=1.0e3, stop=1.0e8, dec=50)),
        parameters={**_sizing(), **_TB},
    )
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=tmp_path / "decks",
        vb_env_file=Path(env_file).expanduser() if env_file else None,
        work_dir=str(tmp_path / "raw"),
    )
    sim.apply_corner(Corner(
        name="tt_lvt_27C_1V2",
        model_includes=[ModelInclude(lib_file=str(Path(_MODELS).expanduser()), section="tt_lvt")],
        temp=27.0,
        supplies=[SupplyOverride(node="VDD", value=1.2)],
    ))
    result = sim.run(label="amp022_tsmc65_noise_live")

    # op-point sanity on the PMOS input pair (re-proves the deck biases up before noise)
    op = operating_point(result, "XDUT.XM0")
    assert op and op["gm"] > 0.0, "input-pair op-point missing/non-physical"

    # the deliverable: integrated output- and input-referred noise off the swept noise PSF
    onoise = measure(result, {"meas": "onoise_total", "out": "out"}, default_analysis="noise")
    inoise = measure(result, {"meas": "inoise_total", "out": "in"}, default_analysis="noise")

    assert onoise > 0.0, f"output-referred RMS noise non-physical: {onoise} V"
    assert inoise > 0.0, f"input-referred RMS noise non-physical: {inoise} V"
    # a two-stage OTA has voltage gain ≫ 1, so referring the output noise to the input shrinks it
    assert inoise < onoise, f"input-referred noise {inoise} should be < output-referred {onoise}"
    # sanity envelope: µV-to-mV-scale integrated noise for a 1 kHz–100 MHz band
    assert 1e-9 < inoise < 1e-2, f"input-referred RMS noise out of plausible band: {inoise} V"
