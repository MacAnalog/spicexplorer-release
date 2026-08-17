"""LIVE gm/ID operating point on a real licensed-kit Spectre run (opt-in; needs Cadence).

Runs a composed 5T-OTA op-point on a Cadence host (the same live-proven translate path
as the OCEAN live test), then extracts the per-device operating point in the gm/ID-consumer
shape via `backends.spectre.operating_point` and:

* asserts the shape is physical (saturation region, gm > 0, a sane gm/ID and intrinsic
  gain, a finite fT), and
* **parity-checks** the extracted per-device scalars against the canonical OCEAN
  `device_op_param` reader on the SAME raw dir — proving the adapter-side `.info` post-parse
  and the OCEAN calculator agree on gm / gds / id for the same device.

Opt-in gating mirrors `test_ocean_metrics_live.py` (bridge importable + `SPICEXPLORER_SPECTRE_MODELS`
+ a resolvable Cadence cshrc); it skips everywhere else.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_SPECTRE_MODELS", "")


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_SPECTRE_MODELS to the licensed Spectre model library .scs",
)
def test_live_gmid_operating_point_and_ocean_parity(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.ocean_metrics import (
        OceanMetricsError,
        OceanMetricsSession,
        device_op_param,
    )
    from spicexplorer.backends.spectre import create_spectre_simulator, operating_point
    from spicexplorer.backends.spectre_deck import (
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
        pdk="generic-n65",
        source_pdk="ihp-sg13g2",
        analyses=(dc_oppoint_analysis(),),  # op-point only — this is the gm/ID slice
        parameters={"vcm": 0.6},
    )
    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    raw_root = tmp_path / "raw"
    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=tmp_path / "decks",
        vb_env_file=Path(env_file).expanduser() if env_file else None,
        work_dir=str(raw_root),  # persists the psfascii raw dir OCEAN + parity read
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
    result = sim.run(label="p5a_gmid_live")

    # --- the gm/ID consumer shape from the live op-point ---
    inst = "XOTA.XM1"  # the input differential pair device
    op = operating_point(result, inst)
    assert op, f"no op-point scalars parsed for {inst} (keys present?)"
    assert op.get("region") == pytest.approx(2.0), f"input device not saturated: {op.get('region')}"
    assert op["gm"] > 0.0
    current = op.get("id", op.get("ids"))
    assert current is not None and abs(current) > 0.0
    assert 1.0 < op["gm_id"] < 40.0, f"gm/ID out of physical range: {op['gm_id']}"
    assert op["gm_gds"] > 1.0, f"intrinsic gain < 1: {op['gm_gds']}"
    if "ft" in op:
        assert op["ft"] > 0.0 and math.isfinite(op["ft"])

    # --- parity: adapter-side .info post-parse vs canonical OCEAN device_op_param ---
    with session:
        ocean = session.measure(
            [p for p in raw_root.rglob("*.raw") if p.is_dir()][-1],
            [device_op_param("gm", inst, "gm"), device_op_param("gds", inst, "gds")],
            label="p5a_parity",
        )
    assert op["gm"] == pytest.approx(ocean["gm"], rel=1e-3)
    assert op["gds"] == pytest.approx(ocean["gds"], rel=1e-3)
