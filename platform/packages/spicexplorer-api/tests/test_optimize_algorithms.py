"""GET /optimize/algorithms + the ephemeral algorithm-override kwargs contract.

Covers the 2026-07 Run-popover failure lane: the popover offered a hardcoded
client-side list, and picking a registry preset (LhsDE) on a project whose YAML
configures a Family (SamplingSearch + sampler kwargs) crashed optimizer
construction — with the dead run finalized as status "done".
"""
import sys

import pytest
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")

# The 5T example is the one whose YAML configures a Family with kwargs
# (SamplingSearch + sampler=Hammersley) — the exact premise of the failure.
FAMILY_KWARGS_YAML = REPO_ROOT / "examples/OTA/5t-ota/ihp-sg13g2/sizing/project_setup.yaml"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app
    return TestClient(app)


def test_algorithms_endpoint_is_backend_derived(client):
    r = client.get("/api/optimize/algorithms")
    assert r.status_code == 200
    body = r.json()
    known = set(body["registry"]) | set(body["families"])
    # Curated set is non-empty and every entry actually exists in the installed
    # Nevergrad (a version bump must not advertise an unconstructable name).
    assert body["recommended"] and set(body["recommended"]) <= known
    assert "LhsDE" in body["registry"]
    assert "SamplingSearch" in body["families"]
    # Full registry is the power-user list — it is much larger than the curated one.
    assert len(body["registry"]) > len(body["recommended"])


def test_algorithm_override_drops_yaml_kwargs():
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer_api.services.optimizer_runner import _apply_overrides

    project = Project_Setup.from_yaml(str(FAMILY_KWARGS_YAML))
    cfg = project.optimizer_config
    assert cfg.name == "SamplingSearch" and cfg.optimizer_kwargs  # the fixture's premise

    _apply_overrides(project, run_id="testrun", budget=None, algorithm="LhsDE", seed=None)
    assert cfg.name == "LhsDE"
    assert cfg.optimizer_kwargs == {}  # family kwargs must not ride onto the preset


def test_same_algorithm_override_keeps_yaml_kwargs():
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer_api.services.optimizer_runner import _apply_overrides

    project = Project_Setup.from_yaml(str(FAMILY_KWARGS_YAML))
    cfg = project.optimizer_config
    kwargs_before = dict(cfg.optimizer_kwargs or {})

    _apply_overrides(project, run_id="testrun", budget=None, algorithm=cfg.name, seed=None)
    assert cfg.optimizer_kwargs == kwargs_before
