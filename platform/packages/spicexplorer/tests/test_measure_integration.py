"""Tier-1 (engine-neutral Python) measurement wiring — offline, no simulator.

Covers the `{meas: …}` recipe path end to end at the optimizer seam: TargetSpec tier
discrimination + shape validation (core.domains), recipe grouping/validation, and
`MeasureMergeContext.merge` folding computed scalars into a result so
`scalar(name, analysis)` returns them (the same seam the scorer reads).
"""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer.core.domains import ListTargetSpec, TargetSpec
from spicexplorer.optimization.measure_integration import (
    MeasureMergeContext,
    build_recipes,
)


# --------------------------------------------------------------------------- fixtures
def _single_pole(freq: np.ndarray, a0: float = 1000.0, fp: float = 1e3) -> np.ndarray:
    return a0 / (1.0 + 1j * freq / fp)


class _FakeResult:
    """SimResult-shaped stub with preloaded waves + op scalars; mergeable."""

    def __init__(self, waves: dict, scalars: dict | None = None) -> None:
        self._w = waves
        self._s = dict(scalars or {})
        self._merged: dict[str, float] = {}

    def wave(self, name: str, analysis: str) -> np.ndarray:
        return np.asarray(self._w[name])  # KeyError → missing signal (→ NaN upstream)

    def scalar(self, name: str, analysis: str) -> float:
        if name in self._merged:
            return self._merged[name]
        return float(self._s.get(name, np.nan))

    def merge_scalars(self, d: dict) -> None:
        self._merged.update({k: float(v) for k, v in d.items()})


class _UnmergeableResult:
    def wave(self, name, analysis):
        return np.asarray([1.0])

    def scalar(self, name, analysis):
        return float("nan")


def _ac_target(name: str, meas: str) -> TargetSpec:
    return TargetSpec(
        name=name, testbench="tb_ac", target=1e6, goal="exceed", sim_type="ac",
        range=1e6, measurement={"meas": meas, "out": "v_out"},
    )


# ------------------------------------------------------------- TargetSpec tier + shape
def test_target_tier_discrimination():
    py = _ac_target("ugf_hz", "ugf")
    assert py.measurement_tier() == "python"
    assert py.has_python_measurement() and not py.has_ocean_measurement()

    oc = TargetSpec(
        name="gain", testbench="tb_ac", target=1.0, goal="exceed", sim_type="ac",
        range=1.0, measurement={"builder": "device_op_param", "instance": "XM1", "param": "gm"},
    )
    assert oc.measurement_tier() == "ocean"
    assert oc.has_ocean_measurement() and not oc.has_python_measurement()

    plain = TargetSpec(name="v_out", testbench="tb", target=1.0, goal="exceed", sim_type="dc", range=1.0)
    assert plain.measurement_tier() is None


def test_target_measurement_shape_validation():
    with pytest.raises(ValueError, match="meas"):
        TargetSpec(name="g", testbench="tb", target=1.0, goal="exceed", sim_type="ac",
                   range=1.0, measurement={"meas": ""})
    with pytest.raises(ValueError, match="one of"):
        TargetSpec(name="g", testbench="tb", target=1.0, goal="exceed", sim_type="ac",
                   range=1.0, measurement={"nonsense": 1})


# ------------------------------------------------------------- build_recipes + validate
def test_build_recipes_python_only_and_validated():
    specs = ListTargetSpec([
        _ac_target("ugf_hz", "ugf"),
        TargetSpec(name="gain", testbench="tb_ac", target=1.0, goal="exceed", sim_type="ac",
                   range=1.0, measurement={"builder": "ac_peak_mag", "signal": "v_out"}),  # OCEAN — skipped
        TargetSpec(name="v_out", testbench="tb_dc", target=1.0, goal="exceed", sim_type="dc", range=1.0),  # no recipe
    ])
    recipes = build_recipes(specs)
    assert set(recipes) == {"tb_ac"}
    assert [name for name, _r, _a in recipes["tb_ac"]] == ["ugf_hz"]


def test_build_recipes_rejects_unknown_meas_at_load():
    specs = ListTargetSpec([_ac_target("x", "not_a_metric")])
    with pytest.raises(ValueError, match="unknown measurement"):
        build_recipes(specs)


def test_build_returns_none_without_python_recipes():
    specs = ListTargetSpec([
        TargetSpec(name="v_out", testbench="tb", target=1.0, goal="exceed", sim_type="dc", range=1.0),
    ])
    assert MeasureMergeContext.build(specs) is None


# --------------------------------------------------------------------------- merge path
def test_merge_folds_scalars_into_result():
    freq = np.logspace(0, 9, 4000)
    result = _FakeResult({"frequency": freq, "v_out": _single_pole(freq)})
    ctx = MeasureMergeContext.build(ListTargetSpec([_ac_target("ugf_hz", "ugf"), _ac_target("pm_deg", "pm")]))
    assert ctx is not None

    ctx.merge({"tb_ac": result})
    # after merge the scorer's scalar(name, analysis) finds the computed metrics
    assert result.scalar("ugf_hz", "ac") == pytest.approx(1e6, rel=0.02)
    assert result.scalar("pm_deg", "ac") == pytest.approx(90.0, abs=1.0)


def test_merge_missing_signal_degrades_to_nan():
    result = _FakeResult({"frequency": np.logspace(0, 9, 100)})  # no v_out wave
    ctx = MeasureMergeContext.build(ListTargetSpec([_ac_target("ugf_hz", "ugf")]))
    assert ctx is not None
    ctx.merge({"tb_ac": result})
    assert np.isnan(result.scalar("ugf_hz", "ac"))


def test_merge_skips_unmergeable_result():
    ctx = MeasureMergeContext.build(ListTargetSpec([_ac_target("ugf_hz", "ugf")]))
    assert ctx is not None
    # must not raise even though the result has no merge_scalars
    ctx.merge({"tb_ac": _UnmergeableResult()})
