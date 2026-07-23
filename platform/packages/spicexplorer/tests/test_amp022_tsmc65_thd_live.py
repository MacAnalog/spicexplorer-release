"""LIVE transient THD on the analog-db `amp_022` tsmc-n65 deck (opt-in).

End-to-end proof that a Spectre **transient** run on the registered
`amp_022_fer_two_stage / pdk tsmc-n65` node yields the canonical Tier-1 THD figure of
merit through the engine-neutral measurement registry: reuses the translated DUT subckt
(from the dc/ac `noise.spice` deck the translator accepts — transient source specs are out
of scope for translation) and composes a **native** unity-gain-follower + large-signal
`vsource type=sine` testbench (the `sine_source` + `transient_analysis` composers), runs a
DC op-point + transient over the virtuoso-bridge, and extracts `thd` off the
`SpectreSimResult` (whose `time`/`vout` waves come from the swept-PSF reader reading
`tran.tran`) via the coherent-FFT `thd_from_waveform`.

Opt-in gating mirrors `test_amp022_tsmc65_noise_live.py` (bridge importable +
`SPICEXPLORER_TSMC65_MODELS` + the analog-db raw deck present); it skips everywhere else.
Point `SPICEXPLORER_ANALOG_DB` at a populated analog-db checkout when running from a
worktree whose submodule is empty.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_TSMC65_MODELS", "")

# TB conditions (TSMC-65 core rail 1.2 V) — same rig as the AC/noise proofs; sizing from the binding.
_TB = {"vdd": 1.2, "ibias": "20u", "cl": "500f"}


def _sizing() -> dict[str, str]:
    # sizing.yaml defaults, read from the SAME analog-db checkout as the raw deck —
    # never hand-transcribed (the 2026-07-13 knob rename made hardcoded dicts drift).
    from spicexplorer.backends.analog_db import load_sizing

    return load_sizing("amp_022_fer_two_stage", "tsmc-n65")

# large-signal sine stimulus: 100 mV around a 0.6 V input common-mode at 1 MHz (well below
# the ~18 MHz UGF, so the unity-gain follower tracks with loop-gain-suppressed distortion).
_VCM, _AMPL, _FREQ, _NPER = 0.6, 0.1, 1.0e6, 20


def _subckt_source_deck() -> Path:
    from spicexplorer_core import project_root

    root = Path(os.environ.get("SPICEXPLORER_ANALOG_DB") or (project_root() / "examples/analog-db"))
    return root / "raw/amp_022_fer_two_stage/tsmc-n65/noise.spice"


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_TSMC65_MODELS to the TSMC-65 Spectre model library",
)
def test_live_amp022_tsmc65_thd_metric(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    src = _subckt_source_deck()
    if not src.is_file():
        pytest.skip(f"analog-db tsmc-n65 raw deck not found ({src}); set SPICEXPLORER_ANALOG_DB")

    from spicexplorer.backends.spectre import create_spectre_simulator, operating_point
    from spicexplorer.backends.spectre_deck import (
        dc_oppoint_analysis,
        deck_spec_from_native,
        deck_spec_from_ngspice,
        sine_source,
        transient_analysis,
    )
    from spicexplorer_core.measurements import measure
    from spicexplorer_core.measurements.waveforms import harmonic_amplitudes
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

    # reuse the translated DUT subckt (dc/ac deck translates; transient sources do not)
    ref = deck_spec_from_ngspice(src, pdk="tsmc-n65", source_pdk="tsmc-n65")
    stimulus = "\n".join([
        sine_source("Vinp", "vinp", "0", dc=_VCM, ampl=_AMPL, freq=_FREQ),
        "Vdd ( vdd 0 ) vsource dc=vdd",
        "Vss ( vss 0 ) vsource dc=0",
        "Ibias ( vdd ibias ) isource dc=ibias",
        "CLoad ( vout 0 ) capacitor c=cl",
        "Vfb ( vinn vout ) vsource dc=0",  # unity-gain follower: vinn tracks vout
        "XDUT ( vdd vout vinp vinn ibias vss ) amp_022_fer_two_stage",
    ])
    spec = deck_spec_from_native(
        title="amp_022 tsmc-n65 THD (follower, sine)",
        stimulus=stimulus,
        subckt_blocks=ref.subckt_blocks,
        analyses=(
            dc_oppoint_analysis(),
            transient_analysis(_NPER / _FREQ, step=1.0 / (_FREQ * 200)),
        ),
        # ref.parameters carries the deck's TIE definitions (x_dut_xm1_l=(x_dut_xm0_l), …)
        # that the subckt body references — dropping them leaves SFE-1997 unknown-parameter
        # errors post-rename; sizing overrides the free defaults, _TB adds conditions
        parameters={**ref.parameters, **_sizing(), **_TB},
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
    result = sim.run(label="amp022_tsmc65_thd_live")

    # op-point sanity on the PMOS input pair (re-proves the deck biases up before the sweep)
    op = operating_point(result, "XDUT.XM0")
    assert op and op["gm"] > 0.0, "input-pair op-point missing/non-physical"

    # the follower actually passed the sine through: fundamental at vout ≈ input amplitude
    t = np.real(np.asarray(result.wave("time", "tran")))
    vout = np.real(np.asarray(result.wave("vout", "tran")))
    assert t.size > 4 * 200, "transient too short / not captured"
    amps = harmonic_amplitudes(t, vout, _FREQ, n_periods=_NPER - 5)
    assert amps[0] == pytest.approx(_AMPL, rel=0.3), f"follower did not track: A1={amps[0]} V"

    # the deliverable: THD off the tran.tran PSF through the engine-neutral registry,
    # skipping the first few periods of settling (analyse the clean tail).
    thd = measure(result, {"meas": "thd", "out": "vout", "f0": _FREQ, "n_periods": _NPER - 5},
                  default_analysis="tran")
    thd_pct = measure(result, {"meas": "thd_pct", "out": "vout", "f0": _FREQ, "n_periods": _NPER - 5},
                      default_analysis="tran")

    assert np.isfinite(thd) and thd > 0.0, f"THD non-physical: {thd}"
    assert thd_pct == pytest.approx(thd * 100.0, rel=1e-6)
    # a closed-loop follower well below UGF distorts little but not zero: plausible band, and
    # far under the ~43% of a hard-clipped sine (so we know it is not rail-slamming).
    assert 1e-5 < thd < 0.2, f"THD out of plausible follower band: {thd} ({thd_pct:.3f} %)"
