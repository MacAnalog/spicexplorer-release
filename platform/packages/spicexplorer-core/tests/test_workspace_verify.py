"""The verification plan: spec × test × corner joining table (workspace.verify)."""
from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_core.workspace import (
    load_targets,
    load_verify_plan,
    parse_target,
)


def _plan(project_dir: Path, plan_yaml: str, targets_yaml: str | None = None) -> None:
    (project_dir / "verify").mkdir(parents=True, exist_ok=True)
    (project_dir / "verify" / "plan.yaml").write_text(plan_yaml)
    if targets_yaml is not None:
        (project_dir / "spec").mkdir(parents=True, exist_ok=True)
        (project_dir / "spec" / "targets.yaml").write_text(targets_yaml)


def test_parse_target_ops_and_eng_values():
    assert parse_target(">= 60").satisfies(60) is True
    assert parse_target(">= 60").satisfies(59.9) is False
    assert parse_target("<= 1.8u").value == pytest.approx(1.8e-6)
    assert parse_target("<= 1.8u").satisfies(1e-6) is True
    assert parse_target("== 1.2").satisfies(1.2) is True
    with pytest.raises(ValueError):
        parse_target("60")  # bare number — ambiguous, must specify an operator


def test_load_plan_builds_matrix_and_coordinates(tmp_path: Path):
    _plan(tmp_path, """
    specs:
      psrr_db:
        target: ">= 60"
        test: tb_psrr
        measurement: psrr
        corners: [tt, ss, ff]
        temps: [-40, 27, 125]
        aggregate: min
      power_w:
        measurement: itot
        corners: [tt]
        aggregate: max
        target: "<= 1m"
    """)
    plan = load_verify_plan(tmp_path)
    assert plan is not None
    assert set(plan.specs) == {"psrr_db", "power_w"}
    # 3 corners × 3 temps for psrr + 1×1 (default temp 27) for power
    assert len(plan.matrix()) == 9 + 1
    power = plan.specs["power_w"]
    assert power.temps == (27.0,)  # default temp
    assert power.coordinates()[0] == {"spec": "power_w", "test": None, "corner": "tt", "temp": 27.0}


def test_aggregate_and_pass_semantics(tmp_path: Path):
    _plan(tmp_path, """
    specs:
      gain_db:
        measurement: dcgain
        corners: [tt, ss, ff]
        aggregate: min
        target: ">= 40"
    """)
    spec = load_verify_plan(tmp_path).specs["gain_db"]
    assert spec.aggregate_value([44.0, 41.0, 40.5]) == 40.5   # worst-case (min)
    assert spec.passes([44.0, 41.0, 40.5]) is True            # 40.5 >= 40
    assert spec.passes([44.0, 39.0, 40.5]) is False           # worst 39 < 40
    assert spec.passes([]) is None                            # nothing measured


def test_targets_yaml_is_canonical_over_inline(tmp_path: Path):
    # targets.yaml wins over an inline echo (never copy values — resolve the id).
    _plan(
        tmp_path,
        """
    specs:
      gain_db:
        measurement: dcgain
        corners: [tt]
        target: ">= 30"
    """,
        targets_yaml="specs:\n  gain_db: \">= 45\"\n",
    )
    spec = load_verify_plan(tmp_path).specs["gain_db"]
    assert spec.target is not None and spec.target.value == 45.0
    assert load_targets(tmp_path) == {"gain_db": ">= 45"}


def test_missing_plan_is_none_and_malformed_raises(tmp_path: Path):
    assert load_verify_plan(tmp_path) is None                 # no verify/plan.yaml
    _plan(tmp_path, "specs:\n  bad: {corners: [tt]}\n")       # no measurement
    with pytest.raises(ValueError):
        load_verify_plan(tmp_path)
