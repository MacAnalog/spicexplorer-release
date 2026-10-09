"""`register_measurements`: a downstream family is first-class in the registry."""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_core.measurements import registry as R


class _Res:
    def scalar(self, name, analysis):
        return float("nan")

    def wave(self, name, analysis):
        return np.arange(4.0)


def _extract(result, recipe, analysis):
    w = result.wave(recipe["out"], analysis)
    return float(w.max() if recipe["meas"] == "ext_max" else w.sum())


def test_register_dispatch_validate_and_clash(monkeypatch):
    monkeypatch.setattr(R, "_MEAS_TABLE", dict(R._MEAS_TABLE))
    monkeypatch.setattr(R, "_KIND_DEFAULT_ANALYSIS", dict(R._KIND_DEFAULT_ANALYSIS))
    monkeypatch.setattr(R, "_EXTENSIONS", dict(R._EXTENSIONS))
    names = {"ext_max": ("out",), "ext_sum": ("out",)}
    R.register_measurements("ext", names, _extract, default_analysis="tran")
    assert R.measurement_table()["ext_max"] == ("ext", ("out",))
    assert R.kind_default_analysis()["ext"] == "tran"
    R.validate_recipe("t", {"meas": "ext_max", "out": "v(a)"})
    with pytest.raises(ValueError, match="needs"):
        R.validate_recipe("t", {"meas": "ext_sum"})
    assert R.measure(_Res(), {"meas": "ext_max", "out": "v(a)"}, default_analysis="ac") == 3.0
    assert R.measure(_Res(), {"meas": "ext_sum", "out": "v(a)"}, default_analysis="ac") == 6.0
    R.register_measurements("ext", names, _extract)  # re-import: a no-op
    with pytest.raises(ValueError, match="already registered"):
        R.register_measurements("other", {"ugf": ("out",)}, _extract)
    with pytest.raises(ValueError, match="already registered"):
        R.register_measurements("other", {"ext_max": ("out",)}, _extract)


def _other_extract(result, recipe, analysis):
    return 0.0


def test_reregister_same_kind_must_agree(monkeypatch):
    """The no-op path is only for a true re-import: the same names, the same required keys
    and the same extractor. A subset, a superset, changed keys or another function raises."""
    monkeypatch.setattr(R, "_MEAS_TABLE", dict(R._MEAS_TABLE))
    monkeypatch.setattr(R, "_KIND_DEFAULT_ANALYSIS", dict(R._KIND_DEFAULT_ANALYSIS))
    monkeypatch.setattr(R, "_EXTENSIONS", dict(R._EXTENSIONS))
    names = {"ext_max": ("out",), "ext_sum": ("out",)}
    R.register_measurements("ext", names, _extract)
    R.register_measurements("ext", dict(names), _extract)  # identical: no-op
    with pytest.raises(ValueError, match="already registered"):
        R.register_measurements("ext", {"ext_max": ("out",)}, _extract)  # subset
    with pytest.raises(ValueError, match="already registered"):
        R.register_measurements("ext", {**names, "ext_min": ("out",)}, _extract)  # superset
    with pytest.raises(ValueError, match="already registered"):
        R.register_measurements("ext", {"ext_max": ("out", "ref"), "ext_sum": ("out",)}, _extract)
    with pytest.raises(ValueError, match="already registered"):
        R.register_measurements("ext", names, _other_extract)  # another function
    assert R._EXTENSIONS["ext"] is _extract and R.measurement_table()["ext_max"] == (
        "ext",
        ("out",),
    )
