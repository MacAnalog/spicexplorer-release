"""Regression tests for fixes from the 2026-06 functional audit (no SPICE needed)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from spicexplorer.core.domains import (
    OptimizationLog,
    Project_Setup,
    TargetSpec,
)
from spicexplorer.core.utils import compute_error
from spicexplorer_core import project_root

EXAMPLE_YAML = (
    project_root()
    / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"
)


# --- BUG-32: OptimizationLog mutable-default aliasing -------------------------
_SENTINEL = object()  # OptimizationLog.append() does no type checking at runtime


def test_optimization_log_instances_do_not_share_storage():
    a = OptimizationLog()
    b = OptimizationLog()
    a.append(_SENTINEL)  # type: ignore[arg-type]
    assert len(a) == 1
    assert len(b) == 0, "two default OptimizationLog() must not share the same list"


def test_optimization_log_copies_supplied_list():
    seed: list = []
    log = OptimizationLog(seed)
    log.append(_SENTINEL)  # type: ignore[arg-type]
    assert seed == [], "OptimizationLog must copy, not alias, a caller-supplied list"


# --- BUG-34 / BUG-06: duplicate dut_param names ------------------------------
def test_example_project_loads_with_unique_param_names():
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    names = [p.name for p in proj.dut_params]
    assert len(names) == len(set(names)), f"duplicate dut_param names: {names}"
    assert "x_dut_Vb1" in names and "x_dut_Vb2" in names


def test_duplicate_dut_param_name_raises(tmp_path: Path):
    text = EXAMPLE_YAML.read_text()
    # Re-introduce a duplicate by renaming x_dut_Vb2 back to x_dut_Vb1.
    dup_text = text.replace("name : x_dut_Vb2", "name : x_dut_Vb1")
    p = tmp_path / "dup.yaml"
    p.write_text(dup_text)
    with pytest.raises(ValueError, match="Duplicate dut_param"):
        Project_Setup.from_yaml(p)


# --- BUG-37: omitted target_spec range must not become NaN -------------------
def _spec(**kw):
    base: dict = dict(name="m", testbench="tb", target=21e6, goal="exact", sim_type="ac")
    base.update(kw)
    return TargetSpec(**base)


def test_targetspec_missing_range_falls_back_finite():
    spec = _spec()  # no range given
    assert np.isfinite(spec.range) and spec.range > 0


def test_targetspec_explicit_range_preserved():
    spec = _spec(range=1e6)
    assert spec.range == np.float64(1e6)


def test_compute_error_rejects_nan_coeff():
    with pytest.raises(ValueError):
        compute_error(np.float64(1.0), np.float64(0.0), "relative-absolute", np.float64(np.nan))


# --- SCH-2 / BUG-A4: dut_param string `val` must resolve to a number ---------
def test_dut_param_string_val_is_resolved():
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    p = proj.dut_params[0]
    p.val = "0.18u"  # an engineering-string operating point
    proj.resolve_all_parameter_ranges()
    assert not isinstance(p.val, str), "dut_param.val should be resolved, not left a string"
    assert abs(float(p.val) - 0.18e-6) < 1e-15
