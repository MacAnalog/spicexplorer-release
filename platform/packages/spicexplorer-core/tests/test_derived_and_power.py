"""Tests for the power measurement (registry `op` kind) and the active-area param-derived
metric — the two new figures of merit added for the area/power optimization flow."""
import numpy as np
import pytest
from spicexplorer_core.measurements import derived, registry


class _FakeResult:
    """Minimal SimResult-shaped stub: op scalars only (power reads a single op probe)."""

    def __init__(self, scalars: dict) -> None:
        self._s = dict(scalars)
        self._merged: dict = {}

    def scalar(self, name: str, analysis: str) -> float:
        if name in self._merged:
            return self._merged[name]
        return float(self._s.get(name, np.nan))

    def wave(self, name: str, analysis: str):  # unused by op measurements
        raise KeyError(name)

    def merge_scalars(self, d: dict) -> None:
        self._merged.update({k: float(v) for k, v in d.items()})


# ── power (P = |I_supply|·VDD) ────────────────────────────────────────────────

def test_power_measurement_watts_mw_uw():
    res = _FakeResult({"i_supply": -3.232978e-4})  # signed supply current, 1.5 V rail
    vdd = 1.5
    p_w = 3.232978e-4 * vdd
    assert registry.measure(res, {"meas": "power", "probe": "i_supply", "vdd": vdd},
                            default_analysis="op") == pytest.approx(p_w)
    assert registry.measure(res, {"meas": "power_mw", "probe": "i_supply", "vdd": vdd},
                            default_analysis="op") == pytest.approx(p_w * 1e3)
    assert registry.measure(res, {"meas": "power_uw", "probe": "i_supply", "vdd": vdd},
                            default_analysis="op") == pytest.approx(p_w * 1e6)


def test_power_is_positive_regardless_of_current_sign():
    # power uses |I|, so a sink vs source current gives the same magnitude
    for i in (2.0e-4, -2.0e-4):
        assert registry.measure(_FakeResult({"i_supply": i}),
                                {"meas": "power", "probe": "i_supply", "vdd": 1.2},
                                default_analysis="op") == pytest.approx(2.0e-4 * 1.2)


def test_power_requires_vdd_arg():
    with pytest.raises(ValueError):
        registry.validate_recipe("p", {"meas": "power", "probe": "i_supply"})  # missing vdd
    # i_supply itself still needs only the probe (unchanged)
    registry.validate_recipe("i", {"meas": "i_supply", "probe": "i_supply"})


def test_i_supply_unchanged_by_power_addition():
    res = _FakeResult({"i_supply": -2.5e-4})
    assert registry.measure(res, {"meas": "i_supply", "probe": "i_supply"},
                            default_analysis="op") == pytest.approx(2.5e-4)


# ── active area (Σ W·L·m) ─────────────────────────────────────────────────────

def test_active_area_sum_of_gate_areas():
    params = {"w1": 2e-6, "l1": 0.5e-6, "w2": 4e-6, "l2": 0.5e-6, "m2": 2.0}
    recipe = {"derived": "active_area",
              "devices": [{"w": "w1", "l": "l1"},
                          {"w": "w2", "l": "l2", "m": "m2"}]}
    expected = 2e-6 * 0.5e-6 + 4e-6 * 0.5e-6 * 2.0
    assert derived.compute_derived(recipe, params) == pytest.approx(expected)


def test_active_area_scale_to_um2():
    params = {"w": 10e-6, "l": 1e-6}
    recipe = {"derived": "active_area", "scale": 1e12, "devices": [{"w": "w", "l": "l"}]}
    assert derived.compute_derived(recipe, params) == pytest.approx(10.0)  # 10 µm²


def test_active_area_literal_length_and_multiplier():
    # w is searched (a param name); l and m are frozen literals in the recipe
    params = {"w": 3e-6}
    recipe = {"derived": "active_area", "devices": [{"w": "w", "l": 0.5e-6, "m": 4}]}
    assert derived.compute_derived(recipe, params) == pytest.approx(3e-6 * 0.5e-6 * 4)


def test_active_area_missing_param_raises():
    recipe = {"derived": "active_area", "devices": [{"w": "w1", "l": "l1"}]}
    with pytest.raises(KeyError):
        derived.compute_derived(recipe, {"w1": 1e-6})  # l1 absent


def test_derived_validation_rejects_unknown_but_allows_netlist_mode():
    with pytest.raises(ValueError):
        derived.validate_derived_recipe("t", {"derived": "nope", "devices": []})
    # A devices-less active_area is now VALID — it is scored by the recursive netlist walk
    # (spicexplorer_core.measurements.area), which discovers every device from the deck.
    derived.validate_derived_recipe("t", {"derived": "active_area"})
    derived.validate_derived_recipe("t", {"derived": "active_area", "devices": [{"w": "a", "l": "b"}]})
