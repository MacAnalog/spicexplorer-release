"""Owner ruling 2026-09-25: a datasheet metric that cannot be measured is FULLY FAILED.

``CircuitRun.evaluate`` records an unmeasurable metric (a recipe that raises, an absent trace, a
``meas`` the Tier-1 registry does not define) as ``value=nan, satisfied=False``. Platform TODO §21
asked whether ``MetricEval`` should gain a third "not measured" state; the owner ruled no: NaN stays
a failure, so a conformance report built off ``satisfied`` can never read an unmeasured metric as
met. These tests fail if that ruling changes, so a change to it has to be deliberate.
"""

from __future__ import annotations

import dataclasses
import math

import pytest
from spicexplorer.backends.analog_db import CircuitRun, MetricEval, MetricTarget


def test_metric_eval_stays_two_state():
    """No ``measured`` flag and no ``satisfied: bool | None``: two states only, as ruled."""
    assert [f.name for f in dataclasses.fields(MetricEval)] == [
        "name",
        "value",
        "satisfied",
        "spec_min",
        "spec_max",
    ]
    assert MetricEval.__annotations__["satisfied"] in (bool, "bool")


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize("spec_min, spec_max", [(None, None), (0.0, None), (None, 1.0), (0.0, 1.0)])
def test_a_non_finite_value_satisfies_no_band_not_even_an_open_one(value, spec_min, spec_max):
    target = MetricTarget(
        "m", {"meas": "dcgain", "out": "vout"}, "ac", spec_min=spec_min, spec_max=spec_max
    )
    assert target.satisfied(value) is False


def test_evaluate_reports_an_unmeasurable_metric_failed_even_without_a_band():
    """A metric with no spec band at all is still failed when it cannot be measured: an open band
    must not turn "could not measure" into "met"."""
    unbounded = MetricTarget(
        "unbounded", {"meas": "not_a_measurement", "out": "vout"}, "ac", analysis_id="ac_open_loop"
    )
    run = CircuitRun(
        "stub_amp", "ihp-sg13g2", "ngspice", "ac_open_loop", "tt", object(), [unbounded]
    )
    ev = run.evaluate()["unbounded"]
    assert math.isnan(ev.value)
    assert ev.satisfied is False


class _InDeckScalar:
    """A run result whose in-deck scalar holds ``value``; it records every ``scalar()`` call."""

    def __init__(self, value: float) -> None:
        self.value = value
        self.calls: list[tuple[object, object]] = []

    def scalar(self, name, analysis):
        self.calls.append((name, analysis))
        return self.value


def test_evaluate_does_not_fall_back_to_the_in_deck_scalar():
    """The buf_001 case: ``buf_001_super_follower/ihp-sg13g2/dc_op`` names ``meas: v_offset``,
    which the Tier-1 registry does not define, while the run's own raw holds ``v_offset = -0.405``
    inside the ``[-0.9, -0.2]`` band. A fall-back to ``result.scalar(meas, analysis)`` would score
    that metric as met. The ruling keeps it NaN and failed, and ``scalar()`` is never called."""
    from spicexplorer_core.measurements.registry import measurement_table

    assert "v_offset" not in measurement_table()  # the registry cannot measure it
    band = MetricTarget(
        "v_offset", {"meas": "v_offset"}, "op", spec_min=-0.9, spec_max=-0.2, analysis_id="dc_op"
    )
    assert band.satisfied(-0.405) is True  # the in-deck value would pass the band
    result = _InDeckScalar(-0.405)
    run = CircuitRun(
        "buf_001_super_follower", "ihp-sg13g2", "ngspice", "dc_op", "tt", result, [band]
    )
    ev = run.evaluate()["v_offset"]
    assert math.isnan(ev.value)
    assert ev.satisfied is False
    assert result.calls == []
