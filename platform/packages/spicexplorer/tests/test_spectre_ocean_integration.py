"""Wiring seam: target_spec `measurement` recipes → OCEAN measurements → merged scalars.

Exercises `optimization/ocean_integration.py` with no Cadence: recipe construction (raw
and every `builder:` form, plus the rejections), grouping by testbench, and the
`OceanMergeContext.merge` behaviour — including the graceful skips (a non-Spectre result,
a Spectre run that left no raw dir) and the license-safe idempotent close. The one place
that actually spawns a process is driven by `fake_ocean.py` (a python stand-in), the same
stand-in the OCEAN runner's own unit suite uses.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from spicexplorer.backends.ocean_metrics import OceanMeasurement, OceanMetricsSession
from spicexplorer.backends.spectre import SpectreSimResult
from spicexplorer.core.domains import ListTargetSpec, TargetSpec
from spicexplorer.optimization.ocean_integration import (
    OceanMergeContext,
    build_ocean_measurement,
    build_recipes,
)

FAKE_OCEAN = Path(__file__).parent / "fake_ocean.py"


def _target(name, tb, measurement=None, enable=True):
    return TargetSpec(
        name=name, testbench=tb, target=1.0, goal="exceed", sim_type="ac",
        range=1.0, enable=enable, measurement=measurement,
    )


# -- recipe construction ----------------------------------------------------------
def test_raw_recipe_builds_verbatim_ocean_measurement():
    m = build_ocean_measurement("ugf", {"result": "ac", "expr": 'gainBwProd(v("v_out"))'})
    assert isinstance(m, OceanMeasurement)
    assert (m.name, m.result, m.expr) == ("ugf", "ac", 'gainBwProd(v("v_out"))')


@pytest.mark.parametrize(
    "recipe, expect_result, expect_in_expr",
    [
        ({"builder": "ac_gain_db_at", "signal": "v_out", "freq_hz": 1.0}, "ac", "dB20"),
        ({"builder": "ac_bandwidth_3db", "signal": "v_out"}, "ac", "bandwidth"),
        ({"builder": "ac_gain_bw_product", "signal": "v_out"}, "ac", "gainBwProd"),
        ({"builder": "ac_peak_mag", "signal": "v_out"}, "ac", "ymax"),
        ({"builder": "op_node_voltage", "node": "tail"}, "dc", 'v("tail")'),
        ({"builder": "device_op_param", "instance": "XM1", "param": "gm"}, "dcOpInfo", "OP"),
    ],
)
def test_builder_recipes_map_to_ocean_metrics_helpers(recipe, expect_result, expect_in_expr):
    m = build_ocean_measurement("metric", recipe)
    assert m.name == "metric"
    assert m.result == expect_result
    assert expect_in_expr in m.expr
    # signal helpers strip a leading slash (bare-name truth)
    if "signal" in recipe:
        assert '"v_out"' in m.expr


def test_unknown_builder_is_rejected():
    with pytest.raises(ValueError, match="unknown builder"):
        build_ocean_measurement("x", {"builder": "does_not_exist", "signal": "v"})


def test_builder_missing_arg_is_rejected():
    with pytest.raises(ValueError, match="needs"):
        build_ocean_measurement("x", {"builder": "device_op_param", "instance": "XM1"})


# -- grouping ---------------------------------------------------------------------
def test_build_recipes_groups_enabled_targets_with_measurements_by_testbench():
    specs = ListTargetSpec([
        _target("ugf", "tb_ac", {"result": "ac", "expr": 'gainBwProd(v("o"))'}),
        _target("pm", "tb_ac", {"result": "ac", "expr": 'phaseMargin(v("o"))'}),
        _target("gm", "tb_op", {"builder": "device_op_param", "instance": "XM1", "param": "gm"}),
        _target("no_recipe", "tb_ac", None),                       # skipped: no recipe
        _target("disabled", "tb_ac", {"result": "ac", "expr": "x"}, enable=False),  # skipped
    ])
    recipes = build_recipes(specs)
    assert {tb: [m.name for m in ms] for tb, ms in recipes.items()} == {
        "tb_ac": ["ugf", "pm"], "tb_op": ["gm"],
    }


def test_build_returns_none_when_no_target_has_a_recipe():
    specs = ListTargetSpec([_target("ugf", "tb_ac", None)])
    assert OceanMergeContext.build(specs) is None


# -- merge behaviour --------------------------------------------------------------
def _fake_ocean_ctx(recipes, tmp_path):
    ctx = OceanMergeContext(recipes)
    # inject a fake-ocean-backed session so no real `ocean` process is needed
    ctx._session = OceanMetricsSession(
        work_dir=tmp_path / "ocean_work", _argv=[sys.executable, str(FAKE_OCEAN)]
    )
    return ctx


def test_merge_evaluates_and_folds_ocean_scalars_by_spec_name(tmp_path):
    raw = tmp_path / "tb_ac.raw"
    raw.mkdir()
    recipes = {"tb_ac": [OceanMeasurement("ugf", "ac", 'gainBwProd(v("o"))')]}
    ctx = _fake_ocean_ctx(recipes, tmp_path)
    try:
        result = SpectreSimResult({"ac_o": 0.5}, raw_dir=str(raw))
        ctx.merge({"tb_ac": result})
        # fake_ocean answers every metric with 42.0; it now surfaces under the spec name
        assert result.scalar("ugf", "ac") == pytest.approx(42.0)
        # and the PSF signal is untouched
        assert result.scalar("o", "ac") == pytest.approx(0.5)
    finally:
        ctx.close()


def test_merge_skips_non_spectre_result_without_spawning_a_session(tmp_path):
    class _NgResult:  # no raw_dir / merge_scalars
        def scalar(self, name, analysis):
            return 0.0

    ctx = OceanMergeContext({"tb_ac": [OceanMeasurement("ugf", "ac", "x")]})
    ctx.merge({"tb_ac": _NgResult()})  # type: ignore[dict-item]  # ngspice-like duck type
    assert ctx._session is None  # never spawned
    ctx.close()


def test_merge_skips_spectre_result_with_no_raw_dir(tmp_path, caplog):
    ctx = OceanMergeContext({"tb_ac": [OceanMeasurement("ugf", "ac", "x")]})
    result = SpectreSimResult({"ac_o": 0.5}, raw_dir=None)
    ctx.merge({"tb_ac": result})
    assert ctx._session is None
    assert np.isnan(result.scalar("ugf", "ac"))  # stays NaN, no crash
    ctx.close()


def test_close_is_idempotent(tmp_path):
    ctx = _fake_ocean_ctx({"tb_ac": [OceanMeasurement("ugf", "ac", "x")]}, tmp_path)
    ctx.close()
    ctx.close()  # must not raise
