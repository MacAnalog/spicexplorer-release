"""Regression tests for the 2026-06 audit-REDO backend fixes (ui/backend).

Pure dict/function transforms — no ngspice / PDK / live sim needed. Skipped unless the
`ui` extra (FastAPI) is installed, since these import the backend package.
"""
import sys

import pytest
from _api_fixtures import REPO_ROOT

# `ui` lives at the repo root (not under src/), so add it then skip cleanly if the
# `ui` extra (FastAPI) is absent.
sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


# ---------- EXP-2: compute_envelope exact-goal best = closest-to-target ----------

def test_compute_envelope_exact_goal_picks_closest_not_max():
    from spicexplorer_api.services.checkpoint_reader import compute_envelope

    data = {"per_metric": {"pm": [120.0, 58.0, 200.0, 61.0]}}
    specs = [{"name": "pm", "goal": "exact", "target": 60.0, "tolerance": 10.0}]
    (row,) = compute_envelope(data, specs)
    # Closest to 60 is 61 (|1|), NOT the 200 outlier the old `else: max` returned.
    assert row["best_ever"] == 61.0
    assert row["passes"] is True


def test_compute_envelope_exact_goal_fails_when_no_sample_in_band():
    from spicexplorer_api.services.checkpoint_reader import compute_envelope

    data = {"per_metric": {"pm": [120.0, 95.0, 200.0]}}
    specs = [{"name": "pm", "goal": "exact", "target": 60.0, "tolerance": 10.0}]
    (row,) = compute_envelope(data, specs)
    assert row["best_ever"] == 95.0  # closest to 60, still out of the ±10 band
    assert row["passes"] is False


def test_compute_envelope_minimize_and_exceed_unchanged():
    from spicexplorer_api.services.checkpoint_reader import compute_envelope

    data = {"per_metric": {"power": [3.0, 1.0, 2.0], "gain": [40.0, 55.0, 50.0]}}
    specs = [
        {"name": "power", "goal": "minimize", "target": 2.0, "tolerance": 0.5},
        {"name": "gain", "goal": "exceed", "target": 50.0, "tolerance": 1.0},
    ]
    rows = {r["metric"]: r for r in compute_envelope(data, specs)}
    assert rows["power"]["best_ever"] == 1.0   # min
    assert rows["gain"]["best_ever"] == 55.0   # max


# ---------- WIZ-1: yaml_generator emits freeze:true (not the inverted false) ----------

def test_frozen_dut_param_serializes_freeze_true():
    from spicexplorer_api.services.yaml_generator import _build_dut_param

    out = _build_dut_param({"name": "x_W", "min_val": 1, "max_val": 2, "freeze": True})
    assert out.get("freeze") is True


def test_unfrozen_dut_param_omits_freeze():
    from spicexplorer_api.services.yaml_generator import _build_dut_param

    out = _build_dut_param({"name": "x_W", "min_val": 1, "max_val": 2, "freeze": False})
    assert "freeze" not in out  # False is the dataclass default; nothing to serialize


# ---------- ENV-1: PDK fast-path covers the real tech-prefixed models/ layout ----------

def test_pdk_fastpath_includes_tech_prefixed_models_layout():
    from spicexplorer_api.services.env_probe import (
        _PDK_LIB_SUBPATHS,
        _PDK_MODEL_LIB,
        _PDK_TECH,
    )

    assert f"{_PDK_TECH}/libs.tech/ngspice/models/{_PDK_MODEL_LIB}" in _PDK_LIB_SUBPATHS


# ---------- BUG-A1: xschem resolver finds the PDK without the singular PDK env ----------

def test_pdk_xschem_dir_resolves_with_pdk_root_only(tmp_path, monkeypatch):
    """PDK_ROOT points at the parent of <tech>/; PDK is unset (the broken deployment)."""
    import spicexplorer_api.routes.xschem as X
    from spicexplorer_api.services.env_probe import _PDK_TECH

    xdir = tmp_path / _PDK_TECH / "libs.tech" / "xschem"
    xdir.mkdir(parents=True)
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    monkeypatch.delenv("PDK", raising=False)
    monkeypatch.delenv("IHP_PDK_ROOT", raising=False)
    X._pdk_xschem_dir_cached = None
    try:
        assert X._pdk_xschem_dir() == xdir
    finally:
        X._pdk_xschem_dir_cached = None


def test_pdk_xschem_dir_matches_root_already_at_tech_dir(tmp_path, monkeypatch):
    """A root (e.g. IHP_PDK_ROOT) that already points at the tech dir resolves too."""
    import spicexplorer_api.routes.xschem as X

    xdir = tmp_path / "libs.tech" / "xschem"
    xdir.mkdir(parents=True)
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    monkeypatch.delenv("PDK", raising=False)
    X._pdk_xschem_dir_cached = None
    try:
        assert X._pdk_xschem_dir() == xdir
    finally:
        X._pdk_xschem_dir_cached = None
