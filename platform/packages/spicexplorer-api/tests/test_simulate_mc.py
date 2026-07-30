"""POST /simulate/once Monte Carlo lane — request validation (fast, NO SPICE).

The MC lane clones the active corner into mc1..mcN statistical samples
(`monte_carlo_corners`: `_mismatch` section swap + per-sample `.options seed`)
and runs them through the existing multi-corner fan-out. These tests cover the
fail paths that must reject BEFORE any simulation.
"""
import sys

import pytest
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")

PVT_YAML = str(REPO_ROOT / "examples/OTA/5t-ota/ihp-sg13g2/sizing/project_setup_multicorner.yaml")
NO_PVT_YAML = str(REPO_ROOT / "examples/OTA/5t-ota/ihp-sg13g2/sizing/project_setup.yaml")
PARAMS = {"x_dut_nfet_input_w": "1u"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app
    return TestClient(app)


def _once(client, **body):
    r = client.post("/api/simulate/once", json={"yaml_path": PVT_YAML, "params": PARAMS, **body})
    assert r.status_code == 200
    return r.json()


def test_mc_and_sweep_are_mutually_exclusive(client):
    out = _once(client, monte_carlo=8, sweep_corners=True)
    assert not out["ok"] and "mutually exclusive" in out["error"]


def test_mc_requires_pvt_corners(client):
    out = _once(client, yaml_path=NO_PVT_YAML, monte_carlo=8)
    assert not out["ok"] and "no PVT corners" in out["error"]


def test_mc_sample_count_range(client):
    out = _once(client, monte_carlo=1)
    assert not out["ok"] and "between 2 and 100" in out["error"]
    out = _once(client, monte_carlo=101)
    assert not out["ok"] and "between 2 and 100" in out["error"]


def test_mc_unknown_base_corner(client):
    out = _once(client, monte_carlo=8, active_corner="no_such_corner")
    assert not out["ok"] and "not defined" in out["error"]
