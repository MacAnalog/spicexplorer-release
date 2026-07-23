"""LIVE AC gain/UGF/PM on the registered analog-db `amp_022` tsmc-n65 deck (opt-in).

End-to-end proof that the freshly-registered `amp_022_fer_two_stage / pdk tsmc-n65` node
simulates on real TSMC-65 Spectre and yields the canonical Tier-1 AC figures of merit through
the engine-neutral measurement registry: composes the analog-db raw deck via the translator,
runs a DC op-point + AC sweep over the virtuoso-bridge, and extracts dcgain / ugf / pm off the
`SpectreSimResult` (whose AC waves come from the new swept-PSF reader).

Opt-in gating mirrors `test_spectre_oppoint_live.py` (bridge importable + `SPICEXPLORER_TSMC65_MODELS`
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
    return root / "raw/amp_022_fer_two_stage/tsmc-n65/ac_open_loop.spice"


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_TSMC65_MODELS to the TSMC-65 Spectre model library",
)
def test_live_amp022_tsmc65_ac_metrics(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    deck = _raw_deck()
    if not deck.is_file():
        pytest.skip(f"analog-db tsmc-n65 raw deck not found ({deck}); set SPICEXPLORER_ANALOG_DB")

    from spicexplorer.backends.spectre import create_spectre_simulator, operating_point
    from spicexplorer.backends.spectre_deck import (
        ac_analysis,
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
    )
    from spicexplorer_core.measurements import measure
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

    spec = deck_spec_from_ngspice(
        deck, pdk="tsmc-n65", source_pdk="tsmc-n65",
        analyses=(dc_oppoint_analysis(), ac_analysis(1.0, 1e9, 20)),
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
    result = sim.run(label="amp022_tsmc65_ac_live")

    # op-point sanity on the PMOS input pair (bonus; re-proves the gm/ID extractor on this deck)
    op = operating_point(result, "XDUT.XM0")
    assert op and op["gm"] > 0.0, "input-pair op-point missing/non-physical"

    # the deliverable: canonical AC metrics off the Spectre result's swept-PSF waves
    dcgain = measure(result, {"meas": "dcgain", "out": "vout"}, default_analysis="ac")
    ugf = measure(result, {"meas": "ugf", "out": "vout"}, default_analysis="ac")
    pm = measure(result, {"meas": "pm", "out": "vout"}, default_analysis="ac")

    assert 20.0 < dcgain < 80.0, f"dc gain out of range: {dcgain} dB"
    assert ugf > 1.0e5, f"UGF implausibly low: {ugf} Hz"
    assert 20.0 < pm < 90.0, f"phase margin out of range: {pm} deg"
