"""Tests for spicexplorer_core.paths.project_root."""

import pytest
from spicexplorer_core import paths
from spicexplorer_core.paths import ROOT_ENV_VAR, project_root


def test_finds_workspace_root_via_sentinel():
    paths.clear_cache()
    root = project_root()
    assert (root / ".spicexplorer-root").exists()
    # The core package lives under the located root.
    assert (root / "packages" / "spicexplorer-core").is_dir()


def test_does_not_escape_to_an_outer_git_repo():
    """The sentinel must win over any .git higher up (the sandbox lives inside one)."""
    paths.clear_cache()
    root = project_root()
    assert (root / ".spicexplorer-root").exists()
    assert not (root.parent / ".spicexplorer-root").exists()


def test_env_override_wins(tmp_path, monkeypatch):
    monkeypatch.setenv(ROOT_ENV_VAR, str(tmp_path))
    paths.clear_cache()
    try:
        assert project_root() == tmp_path.resolve()
    finally:
        paths.clear_cache()


def test_env_override_must_be_a_directory(tmp_path, monkeypatch):
    monkeypatch.setenv(ROOT_ENV_VAR, str(tmp_path / "does-not-exist"))
    paths.clear_cache()
    try:
        with pytest.raises(RuntimeError):
            project_root()
    finally:
        paths.clear_cache()
