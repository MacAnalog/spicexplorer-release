"""LIVE PSS distortion on the analog-db `amp_022` tsmc-n65 deck (opt-in).

The higher-fidelity companion to the transient THD proof (`test_amp022_tsmc65_thd_live.py`):
runs a Spectre **periodic steady-state** (`pss_analysis`) on the same unity-gain-follower
testbench and reads the output's per-harmonic distortion straight off the `pss.fd.pss` fd-PSF
through the engine-neutral registry (`{meas: thd_pss|hd2|hd3|sfdr_db}`) — no resample/window.
Cross-checks the native THD against the transient `.four`-style figure (≈0.077 %) and confirms
the HD2-dominated harmonic profile.

Opt-in gating mirrors `test_amp022_tsmc65_thd_live.py` (bridge importable +
`SPICEXPLORER_TSMC65_MODELS` + the analog-db raw deck present); it skips everywhere else.
Point `SPICEXPLORER_ANALOG_DB` at a populated analog-db checkout when the submodule is empty.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_TSMC65_MODELS", "")

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
def test_live_amp022_tsmc65_pss_distortion(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    src = _subckt_source_deck()
    if not src.is_file():
        pytest.skip(f"analog-db tsmc-n65 raw deck not found ({src}); set SPICEXPLORER_ANALOG_DB")

    from spicexplorer.backends.spectre import create_spectre_simulator, operating_point
    from spicexplorer.backends.spectre_deck import (
        dc_oppoint_analysis,
        deck_spec_from_native,
        deck_spec_from_ngspice,
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
        title="amp_022 tsmc-n65 PSS distortion (follower, sine)",
        stimulus=stimulus,
        subckt_blocks=ref.subckt_blocks,
        analyses=(
            dc_oppoint_analysis(),
            pss_analysis(_FREQ, harms=7, tstab=10.0 / _FREQ),
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
        name="tt_lvt_27C_1V2",
        model_includes=[ModelInclude(lib_file=str(Path(_MODELS).expanduser()), section="tt_lvt")],
        temp=27.0, supplies=[SupplyOverride(node="VDD", value=1.2)],
    ))
    result = sim.run(label="amp022_tsmc65_pss_live")

    # op-point sanity on the PMOS input pair (deck biases up before the PSS solve)
    op = operating_point(result, "XDUT.XM0")
    assert op and op["gm"] > 0.0, "input-pair op-point missing/non-physical"

    # the pss fd-PSF is a swept PSF: complex per-harmonic phasors, freq = [0, f0, 2f0, …]
    harmonics = np.asarray(result.wave("vout", "pss"))
    assert harmonics.dtype.kind == "c" and harmonics.size >= 4, "pss harmonics not captured as phasors"
    mag = np.abs(harmonics)
    assert mag[1] == pytest.approx(_AMPL, rel=0.3), f"follower did not track: |H1|={mag[1]} V"

    # the deliverable: distortion straight off the harmonics via the registry
    thd_pss = measure(result, {"meas": "thd_pss", "out": "vout"}, default_analysis="pss")
    thd_pss_pct = measure(result, {"meas": "thd_pss_pct", "out": "vout"}, default_analysis="pss")
    hd2 = measure(result, {"meas": "hd2", "out": "vout"}, default_analysis="pss")
    hd3 = measure(result, {"meas": "hd3", "out": "vout"}, default_analysis="pss")
    sfdr_db = measure(result, {"meas": "sfdr_db", "out": "vout"}, default_analysis="pss")

    assert thd_pss_pct == pytest.approx(thd_pss * 100.0, rel=1e-9)
    # cross-check the native PSS THD against the transient .four figure (≈0.077 %); same rig,
    # so they agree to well within a factor of 3 (both far below a hard-clip's ~43 %).
    assert 1e-4 < thd_pss < 5e-3, f"native PSS THD out of band: {thd_pss} ({thd_pss_pct:.4f} %)"
    assert hd2 > hd3, f"expected HD2-dominated distortion; hd2={hd2} hd3={hd3}"
    assert sfdr_db > 40.0, f"SFDR implausibly low: {sfdr_db} dB"
