"""Layout-flow backend — LIVE (slow) test on the 5T OTA gdsfactory example.

Runs `examples/layout/ihp-sg13g2/5t_ota_gf/opt/flow.yaml` at the generator's committed
defaults through `LayoutSimulator.run()`: real gdsfactory build (in the `GDS_PYTHON` /
ai_env interpreter), KLayout DRC + LVS, kpex CC and the ngspice post-layout AC bench.
Skips unless every tool is present (the research server / a full EDA host).
"""

from __future__ import annotations

import math
import os
import shutil
from pathlib import Path

import pytest
from _spicexplorer_fixtures import REPO_ROOT

FLOW = REPO_ROOT / "examples/layout/ihp-sg13g2/5t_ota_gf/opt/flow.yaml"


def _gds_python() -> str | None:
    cand = os.environ.get("GDS_PYTHON") or os.path.expanduser("~/miniconda3/envs/ai_env/bin/python")
    return cand if os.path.exists(os.path.expanduser(cand)) else None


def _tools_ok() -> bool:
    try:
        from spicexplorer_signoff import probe
    except ImportError:
        return False
    p = probe()
    return bool(p.drc_ok and p.lvs_ok and p.kpex and p.kpex_klayout and shutil.which("ngspice") and _gds_python())


pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not _tools_ok(), reason="needs the gdsfactory env (GDS_PYTHON/ai_env), klayout, kpex, ngspice + PDK"),
]


def test_5t_ota_layout_flow_at_defaults(tmp_path: Path):
    """The committed defaults through the real flow, plus the pre-layout reference run of the
    same tb_ac.spice on the schematic DUT — the UGF loss is the known ≈0.7 MHz figure."""
    from spicexplorer.backends.layout import LayoutFlowSpec, LayoutSimulator
    from spicexplorer_core.measurements import registry

    spec = LayoutFlowSpec.from_yaml(FLOW)
    assert spec.postlayout is not None
    sim = LayoutSimulator(spec, output_folder=tmp_path / "out", testbench_name="layout", verbose=True,
                          path_to_simulator="ngspice")
    sim.update_params({k: v for k, v in spec.param_defaults.items() if k in spec.bounds})
    res = sim.run(label="layout__tt")
    assert res.status == "ok", res.summary.get("error")
    for k in ("drc_pass", "lvs_match", "pex_ok", "postlayout_ok"):
        assert res.scalar(k, "layout") == 1.0, k
    area = res.scalar("area_um2", "layout")
    assert 150.0 < area < 260.0, area  # committed defaults ≈ 205.9 um2 (README)
    assert not math.isnan(res.scalar("c_vout_ff", "layout"))
    assert res.log_path is not None and res.log_path.is_file()
    # post-layout metrics: registry recipes on the AC waves READ THROUGH the layout result
    post = {m: registry.measure(res, {"meas": m, "out": "v(vout)"}, default_analysis="ac") for m in ("dcgain", "ugf", "pm")}
    pre_res = sim.run_prelayout_reference(tmp_path / "pre")["tb_ac"]
    pre = {m: registry.measure(pre_res, {"meas": m, "out": "v(vout)"}, default_analysis="ac") for m in ("dcgain", "ugf", "pm")}
    assert 29.5e6 < pre["ugf"] < 31e6 and 25e6 < post["ugf"] < 31e6, (pre, post)
    loss_mhz = (pre["ugf"] - post["ugf"]) / 1e6
    assert 0.3 < loss_mhz < 1.5, loss_mhz  # ≈ 0.70 MHz at the defaults
    assert 55 < post["pm"] < 70 and 28 < post["dcgain"] < 31
    # inner delegation: op scalars via the qualified and unqualified names
    assert res.scalar("tb_ac:v(vout)", "op") == pytest.approx(res.scalar("v(vout)", "op"))
    assert not math.isnan(res.scalar("i(vdd)", "op"))
