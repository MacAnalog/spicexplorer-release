"""LIVE OCEAN metrics on a real headless Spectre raw dir (opt-in; needs Cadence).

Run the composed 5T-OTA deck
through the bridge with a persisted `work_dir` (that is what leaves a psfascii raw dir
behind — adapter composed mode alone keeps only the `.scs`), then evaluate canonical
OCEAN calculators on that raw via one persistent `ocean -nograph` session, and
cross-check them against the Tier-1 Python parse of the *same* run.

Opt-in gating (all, or the test skips):

* ``virtuoso_bridge`` importable in this venv;
* ``SPICEXPLORER_FOUNDRY65_MODELS`` — FOUNDRY-65 Spectre model library path (NDA: env only);
* ``VB_CADENCE_CSHRC`` resolvable (process env or ``~/.virtuoso-bridge/local.env``) —
  the ocean session sources it;
* ``SPICEXPLORER_VB_ENV_FILE`` (optional) — bridge profile pin.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_FOUNDRY65_MODELS", "")


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_FOUNDRY65_MODELS to the FOUNDRY-65 Spectre model library .scs",
)
def test_live_ocean_metrics_match_python_on_same_raw(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.ocean_metrics import (
        OceanMeasurement,
        OceanMetricsError,
        OceanMetricsSession,
        ac_bandwidth_3db,
        ac_gain_db_at,
        ac_peak_mag,
        device_op_param,
        op_node_voltage,
    )
    from spicexplorer.backends.spectre import create_spectre_simulator
    from spicexplorer.backends.spectre_deck import (
        ac_analysis,
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
    )
    from spicexplorer_core import project_root
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

    try:
        session = OceanMetricsSession.from_vb_env()
    except OceanMetricsError:
        pytest.skip("VB_CADENCE_CSHRC not resolvable — no Cadence shell for ocean")

    example = project_root() / "examples/OTA/5t-ota/ihp-sg13g2/spice/ota-5t_tb-ac.spice"
    spec = deck_spec_from_ngspice(
        example,
        pdk="FOUNDRY-n65",
        source_pdk="ihp-sg13g2",
        analyses=(dc_oppoint_analysis(), ac_analysis(1e3, 1e8, 101)),
        parameters={"vcm": 0.6},
    )
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    raw_root = tmp_path / "raw"
    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=tmp_path / "decks",
        vb_env_file=Path(env_file).expanduser() if env_file else None,
        work_dir=str(raw_root),  # bridge kwarg: THIS is what persists the psfascii raw
    )
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
    result = sim.run(label="r2b_ocean_live")

    raw_dirs = [p for p in raw_root.rglob("*.raw") if p.is_dir()]
    assert raw_dirs, f"bridge left no raw dir under {raw_root}"
    raw = raw_dirs[-1]

    measurements = [
        ac_gain_db_at("gain_db", "v_out", 1e3),
        ac_bandwidth_3db("bw_hz", "v_out"),
        ac_peak_mag("peak", "v_out"),
        # closed-loop |H| never crosses 1 → OCEAN refuses phaseMargin (the naming-truth semantics
        # guard); the errset wrapping must degrade it to NaN, not kill the block
        OceanMeasurement("pm_deg", "ac", 'phaseMargin(v("v_out"))'),
        op_node_voltage("vtail", "XOTA.tail"),
        device_op_param("gm1", "XOTA.XM1", "gm"),
    ]
    with session:
        metrics = session.measure(raw, measurements, label="cand0")
        first_eval_s = session.last_eval_seconds
        again = session.measure(raw, measurements, label="cand0_warm")

    # canonical OCEAN values vs the Tier-1 Python parse of the SAME run
    ac_vout = result.wave("v_out", "ac")
    assert metrics["peak"] == pytest.approx(float(np.max(np.abs(ac_vout))), rel=1e-4)
    assert metrics["gm1"] == pytest.approx(result.scalar("XOTA.XM1:gm", "op"), rel=1e-4)
    assert metrics["vtail"] == pytest.approx(result.scalar("XOTA.tail", "op"), rel=1e-4)
    assert -3.0 < metrics["gain_db"] < 0.0, f"unity-buffer gain off: {metrics['gain_db']}"
    assert 1e6 < metrics["bw_hz"] < 1e9, f"bandwidth off: {metrics['bw_hz']}"
    assert math.isnan(metrics["pm_deg"])  # guarded failure → NaN, never a crash

    # the whole point of the persistent session: warm evals are ~ms, not ~s
    assert again["gain_db"] == pytest.approx(metrics["gain_db"], rel=1e-9)
    assert session.last_eval_seconds is not None and session.last_eval_seconds < 2.0, (
        f"warm eval not warm: {session.last_eval_seconds:.2f}s (first {first_eval_s:.2f}s)"
    )
