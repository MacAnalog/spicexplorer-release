"""Regression tests for the 2026-06 UI restructure (no SPICE needed).

Covers: duplicate PVT corner rejection, ephemeral Score-Shaping spec overrides,
and engineering-string param parsing in the manual-sim request.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer.core.domains import (
    Corner,
    OptimizationGoalType,
    Project_Setup,
    PVTConfig,
)
from spicexplorer_core import project_root

EXAMPLE_YAML = (
    project_root()
    / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"
)

pytest.importorskip("fastapi", reason="ui extra not installed")


# --- Duplicate PVT corner names must be rejected -----------------------------
def test_pvtconfig_rejects_duplicate_corner_names():
    with pytest.raises(ValueError, match="Duplicate PVT corner"):
        PVTConfig(
            active_corner="tt",
            corners=[Corner(name="tt"), Corner(name="tt")],
        )


def test_pvtconfig_allows_unique_corner_names():
    cfg = PVTConfig(
        active_corner="tt",
        corners=[Corner(name="tt"), Corner(name="ss")],
    )
    assert [c.name for c in cfg.corners] == ["tt", "ss"]


def test_duplicate_corner_name_in_yaml_raises(tmp_path: Path):
    text = EXAMPLE_YAML.read_text()
    # Collide ss_125C_1V62 with the typical corner's name.
    dup_text = text.replace("name: ss_125C_1V62", "name: tt_27C_1V8")
    assert dup_text != text, "fixture corner name changed — update this test"
    p = tmp_path / "dup_corner.yaml"
    p.write_text(dup_text)
    with pytest.raises(ValueError, match="Duplicate PVT corner"):
        Project_Setup.from_yaml(p)


def test_example_project_loads_with_unique_corner_names():
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    assert proj.pvt is not None
    names = [c.name for c in proj.pvt.corners]
    assert len(names) == len(set(names)), f"duplicate corner names: {names}"


# --- Ephemeral Score-Shaping spec overrides ----------------------------------
def test_apply_spec_overrides_mutates_in_memory_only():
    from spicexplorer_api.services.score_service import apply_spec_overrides, compute_score

    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    spec = proj.optimizer_config.target_specs.targets[0]
    name = spec.name

    apply_spec_overrides(
        proj,
        {name: {"target": "250u", "weight": 2.0, "goal": "minimize"}},
    )

    assert abs(float(spec.target) - 250e-6) < 1e-12
    assert spec.weight is not None and float(spec.weight) == 2.0
    assert spec.goal == OptimizationGoalType.MINIMIZE

    # The override feeds compute_score (it reads spec.target/weight/goal off the
    # mutated objects). Smoke that it runs and reports the overridden weight.
    result = compute_score(proj, {name: 250e-6}, selected_spec=name)
    assert result["per_spec"][name]["weight"] == 2.0

    # Reloading from disk discards the edit (proves it never touched the YAML).
    fresh = Project_Setup.from_yaml(EXAMPLE_YAML)
    fresh_spec = fresh.optimizer_config.target_specs.targets[0]
    assert float(fresh_spec.target) != 250e-6 or fresh_spec.goal != OptimizationGoalType.MINIMIZE


def test_apply_spec_overrides_ignores_unknown_spec_and_bad_goal():
    from spicexplorer_api.services.score_service import apply_spec_overrides

    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    spec = proj.optimizer_config.target_specs.targets[0]
    orig_goal = spec.goal

    # Unknown spec name + an invalid goal value must not raise (it's a preview).
    apply_spec_overrides(proj, {"___nope___": {"target": 1.0}})
    apply_spec_overrides(proj, {spec.name: {"goal": "not_a_goal"}})
    assert spec.goal == orig_goal  # invalid goal ignored


def test_apply_spec_overrides_none_is_noop():
    from spicexplorer_api.services.score_service import apply_spec_overrides

    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    apply_spec_overrides(proj, None)  # must not raise


# --- Manual-sim request accepts engineering strings --------------------------
def test_simulate_once_request_accepts_eng_string_params():
    from spicexplorer_api.routes.simulate import SimulateOnceRequest

    # The widened type must validate eng-strings (previously a 422).
    req = SimulateOnceRequest(yaml_path="x.yaml", params={"w": "250u", "l": 0.18e-6})
    assert req.params == {"w": "250u", "l": 0.18e-6}
