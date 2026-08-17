"""LIVE translate→compose→Spectre round-trip (opt-in; needs Cadence + a licensed kit).

The committed IHP ngspice 5T-OTA
testbench is translated (`deck_spec_from_ngspice`: dialect emitters + 65 nm
device-model mapping), parameters are injected at the kit operating point
(vdd 1.5→1.2, vcm 0.8→0.6), the corner is applied through `apply_corner`
(the self-contained *corner* section, never the raw device section), and
the composed per-run `.scs` runs through the bridge.

Opt-in gating (all, or the test skips):

* ``virtuoso_bridge`` importable in this venv;
* ``SPICEXPLORER_SPECTRE_MODELS`` — absolute path to the licensed Spectre model library
  `.scs` (NDA: lives only in the env / local config, never in the repo);
* ``SPICEXPLORER_VB_ENV_FILE`` (optional) — bridge profile pin, e.g.
  ``~/.virtuoso-bridge/local.env`` on a Cadence host.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_SPECTRE_MODELS", "")


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_SPECTRE_MODELS to the licensed Spectre model library .scs",
)
def test_live_translated_deck_runs_with_injected_params_and_corner(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.spectre import create_spectre_simulator
    from spicexplorer.backends.spectre_deck import (
        ac_analysis,
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
    )
    from spicexplorer_core import project_root
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

    example = project_root() / "examples/OTA/5t-ota/ihp-sg13g2/spice/ota-5t_tb-ac.spice"
    assert example.is_file(), "committed example deck missing"

    spec = deck_spec_from_ngspice(
        example,
        pdk="generic-n65",
        source_pdk="ihp-sg13g2",
        analyses=(dc_oppoint_analysis(), ac_analysis(1e3, 1e8, 101)),
        parameters={"vcm": 0.6},  # construction-time injection
    )

    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=tmp_path,
        vb_env_file=Path(env_file).expanduser() if env_file else None,
    )
    # run-time injection through the protocol seam: the closed-lane corner + supply
    sim.apply_corner(
        Corner(
            name="tt_27C_1V20",
            model_includes=[
                ModelInclude(lib_file=str(Path(_MODELS).expanduser()), section="tt_lvt")
            ],
            temp=27.0,
            supplies=[SupplyOverride(node="VDD", value=1.2)],
        )
    )

    result = sim.run(label="live_p2_translate")

    # the composed deck really was materialized under deck_dir with the injections
    composed = sorted(tmp_path.glob("*.scs"))
    assert composed, "no per-run .scs materialized"
    text = composed[-1].read_text()
    assert "section=tt_lvt" in text and "vdd=1.2" in text and "vcm=0.6" in text

    # unity-gain buffer at the injected operating point: v_out tracks vcm
    vout = result.scalar("v_out", "op")
    assert 0.4 < vout < 0.8, f"v_out should sit near vcm=0.6, got {vout}"

    # per-MOS op scalars come through the info post-parse, devices in saturation
    gm = result.scalar("XOTA.XM1:gm", "op")
    assert np.isfinite(gm) and gm > 0.0, f"XOTA.XM1:gm not a positive scalar: {gm}"
    region = result.scalar("XOTA.XM1:region", "op")
    assert region in (0.0, 1.0, 2.0, 3.0, 4.0), f"unexpected region code: {region}"

    # ac wave present (analysis named `ac`), closed-loop |gain| ~ 1 at the first point
    ac_vout = result.wave("v_out", "ac")
    assert ac_vout.size > 0 and np.iscomplexobj(ac_vout)
    assert 0.5 < abs(ac_vout[0]) < 1.2, f"closed-loop gain off: {abs(ac_vout[0])}"
