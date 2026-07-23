"""LIVE periodic noise on the analog-db `amp_022` tsmc-n65 deck (opt-in).

The cyclostationary companion of the small-signal noise proof
(`test_amp022_tsmc65_noise_live.py`) and the PSS distortion proof
(`test_amp022_tsmc65_pss_live.py`): runs a Spectre **pss + pnoise** pair on the same
unity-gain-follower testbench (100 mV sine @ 1 MHz) and reads the periodic output/input
noise densities off the `pnoise.pnoise` swept PSF through the engine-neutral registry
(`{meas: onoise_pnoise_total|inoise_pnoise_total|pnoise_spot|phase_noise_dbc}`).
Plausibility cross-check: the small-signal noise figures on this rig were ≈813 µV output /
≈210 µV input rms over 1 kHz–100 MHz — for a lightly-driven follower the periodic noise
should land in the same order of magnitude (the follower's output noise is the
input-referred one, ≈100–1000 µV scale, not nV or volts).

Opt-in gating mirrors `test_amp022_tsmc65_pss_live.py` (bridge importable +
`SPICEXPLORER_TSMC65_MODELS` + the analog-db raw deck present); it skips everywhere else.
`SPICEXPLORER_TSMC65_SECTION` selects the wrapper's corner section (default the generic
`tt` — the committed analog-db posture where the operator wrapper does the kit-section
indirection). Point `SPICEXPLORER_ANALOG_DB` at a populated analog-db checkout when the
submodule is empty.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_TSMC65_MODELS", "")
_SECTION = os.environ.get("SPICEXPLORER_TSMC65_SECTION", "tt")

_TB = {"vdd": 1.2, "ibias": "20u", "cl": "500f"}


def _sizing() -> dict[str, str]:
    # sizing.yaml defaults, read from the SAME analog-db checkout as the raw deck —
    # never hand-transcribed (the 2026-07-13 knob rename made hardcoded dicts drift).
    from spicexplorer.backends.analog_db import load_sizing

    return load_sizing("amp_022_fer_two_stage", "tsmc-n65")
_VCM, _AMPL, _FREQ = 0.6, 0.1, 1.0e6  # 100 mV @ 1 MHz around a 0.6 V input common-mode


def _subckt_source_deck() -> Path:
    from spicexplorer_core import project_root

    root = Path(os.environ.get("SPICEXPLORER_ANALOG_DB") or (project_root() / "examples/analog-db"))
    return root / "raw/amp_022_fer_two_stage/tsmc-n65/noise.spice"


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_TSMC65_MODELS to the TSMC-65 Spectre model library",
)
def test_live_amp022_tsmc65_pnoise(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    src = _subckt_source_deck()
    if not src.is_file():
        pytest.skip(f"analog-db tsmc-n65 raw deck not found ({src}); set SPICEXPLORER_ANALOG_DB")

    from spicexplorer.backends.spectre import create_spectre_simulator, operating_point
    from spicexplorer.backends.spectre_deck import (
        dc_oppoint_analysis,
        deck_spec_from_native,
        deck_spec_from_ngspice,
        pnoise_analysis,
        pss_analysis,
        sine_source,
    )
    from spicexplorer_core.measurements import measure
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

    ref = deck_spec_from_ngspice(src, pdk="tsmc-n65", source_pdk="tsmc-n65")
    stimulus = "\n".join([
        sine_source("Vinp", "vinp", "0", dc=_VCM, ampl=_AMPL, freq=_FREQ),
        "Vdd ( vdd 0 ) vsource dc=vdd",
        "Vss ( vss 0 ) vsource dc=0",
        "Ibias ( vdd ibias ) isource dc=ibias",
        "CLoad ( vout 0 ) capacitor c=cl",
        "Vfb ( vinn vout ) vsource dc=0",  # unity-gain follower
        "XDUT ( vdd vout vinp vinn ibias vss ) amp_022_fer_two_stage",
    ])
    spec = deck_spec_from_native(
        title="amp_022 tsmc-n65 pnoise (follower, sine)",
        stimulus=stimulus,
        subckt_blocks=ref.subckt_blocks,
        analyses=(
            dc_oppoint_analysis(),
            pss_analysis(_FREQ, harms=7, tstab=10.0 / _FREQ),
            pnoise_analysis("vout", iprobe="Vinp", start=1.0e3, stop=1.0e8, dec=20),
        ),
        # ref.parameters carries the deck's TIE definitions (x_dut_xm1_l=(x_dut_xm0_l), …)
        # that the subckt body references — dropping them leaves SFE-1997 unknown-parameter
        # errors post-rename; sizing overrides the free defaults, _TB adds conditions
        parameters={**ref.parameters, **_sizing(), **_TB},
    )

    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    sim = create_spectre_simulator(
        deck_spec=spec, deck_dir=tmp_path / "decks",
        vb_env_file=Path(env_file).expanduser() if env_file else None,
        work_dir=str(tmp_path / "raw"),
    )
    sim.apply_corner(Corner(
        name="tt_27C_1V2",
        model_includes=[ModelInclude(lib_file=str(Path(_MODELS).expanduser()), section=_SECTION)],
        temp=27.0, supplies=[SupplyOverride(node="VDD", value=1.2)],
    ))
    result = sim.run(label="amp022_tsmc65_pnoise_live")

    # op-point sanity (deck biases up before the PSS+pnoise solve)
    op = operating_point(result, "XDUT.XM0")
    assert op and op["gm"] > 0.0, "input-pair op-point missing/non-physical"

    # the pnoise densities land in the pnoise.pnoise swept PSF
    freq = np.asarray(result.wave("frequency", "pnoise"))
    out = np.asarray(result.wave("out", "pnoise"))
    assert freq.size > 10 and out.shape == freq.shape
    assert np.all(out > 0.0), "output pnoise density non-physical"

    # the deliverable: canonical figures through the registry
    onoise = measure(result, {"meas": "onoise_pnoise_total", "out": "out"}, default_analysis="pnoise")
    inoise = measure(result, {"meas": "inoise_pnoise_total", "out": "in"}, default_analysis="pnoise")
    spot = measure(result, {"meas": "pnoise_spot", "out": "out", "f": 1.0e4}, default_analysis="pnoise")
    l_1m = measure(
        result,
        {"meas": "phase_noise_dbc", "out": "out", "f": 1.0e4, "carrier_ampl": _AMPL},
        default_analysis="pnoise",
    )

    assert onoise > 0.0 and inoise > 0.0
    # a unity-gain follower refers noise ~1:1 — the two totals sit close together
    # (rel widened 0.5→0.6 with the 2026-07-17 `m=` fix: the input pair now really runs
    # m=5, which shifts the input-referral ratio; ~1.5:1 observed, still follower-plausible)
    assert inoise == pytest.approx(onoise, rel=0.6)
    # plausibility vs the small-signal noise rig (≈813 µV out / ≈210 µV in, 1 kHz–100 MHz):
    # same amp, same band order — the periodic totals must be µV-to-mV scale
    assert 1e-6 < onoise < 5e-3, f"periodic output noise out of plausible band: {onoise} V rms"
    assert 1e-6 < inoise < 5e-3, f"periodic input noise out of plausible band: {inoise} V rms"
    assert 1e-9 < spot < 1e-5, f"10 kHz spot density out of plausible band: {spot} V/sqrt(Hz)"
    assert np.isfinite(l_1m) and l_1m < -40.0, f"noise-to-carrier implausibly high: {l_1m} dBc/Hz"
