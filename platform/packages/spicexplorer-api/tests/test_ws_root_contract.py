"""Phase 0 contract test (report.md) — pin ws_root resolution + the de-CWD autosave.

Fast, NO SPICE. Guards two things a future workspace/run-isolation refactor must not
break: (1) ``Project_Setup.from_yaml``'s three ws_root branches + ``~`` expansion (the
portability contract the committed examples ship on), and (2) the WORK_ROOT-rooted
autosave that fixes the Docker checkpoint data-loss bug — i.e. ``output_root`` routes
checkpoints off the CWD while the default stays byte-identical for CLI/example scripts.
This is the test that would have caught the ``yaml_path=""`` regression.
"""
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pytest
import yaml
from _api_fixtures import REPO_ROOT
from spicexplorer.core.domains import Project_Setup
from spicexplorer.optimization.base import Base_Optimizer

sys.path.insert(0, str(REPO_ROOT))  # so `ui.backend.app_config` imports

CASCODE_YAML = REPO_ROOT / "examples" / "OTA" / "cascode" / "ihp-sg13g2" / "sizing" / "project_setup.yaml"
pytestmark = pytest.mark.skipif(not CASCODE_YAML.exists(), reason="cascode example missing")


def _load_with(tmp_path: Path, *, ws_root: Any = ..., subdir: str = "") -> Project_Setup:
    """Round-trip the cascode example with an edited (or omitted) ws_root, written into
    tmp_path/subdir, and parse it. ``ws_root=...`` keeps the original; ``None`` omits it."""
    data = yaml.safe_load(CASCODE_YAML.read_text())
    if ws_root is None:
        data["project"].pop("ws_root", None)
    elif ws_root is not ...:
        data["project"]["ws_root"] = ws_root
    d = (tmp_path / subdir) if subdir else tmp_path
    d.mkdir(parents=True, exist_ok=True)
    p = d / "project_setup.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False))
    return Project_Setup.from_yaml(p)


# ---------- (1) ws_root resolution branches ----------

def test_ws_root_absolute_kept_as_is(tmp_path):
    abs_ws = (tmp_path / "ws").resolve()
    abs_ws.mkdir()
    proj = _load_with(tmp_path, ws_root=str(abs_ws))
    assert Path(proj.ws_root).resolve() == abs_ws
    # The derived output_folder is under the absolute ws_root and NOT inside the repo
    # tree — the exact invariant a path-resolution regression would violate.
    outdir = (Path(proj.ws_root) / proj.outdir).resolve()
    assert outdir == abs_ws or abs_ws in outdir.parents
    assert REPO_ROOT.resolve() not in outdir.parents


def test_ws_root_relative_against_yaml_dir(tmp_path):
    proj = _load_with(tmp_path, ws_root=".")
    assert Path(proj.ws_root).resolve() == tmp_path.resolve()


def test_ws_root_omitted_defaults_to_yaml_dir(tmp_path):
    proj = _load_with(tmp_path, ws_root=None)
    assert Path(proj.ws_root).resolve() == tmp_path.resolve()


def test_ws_root_tilde_expanded(tmp_path):
    proj = _load_with(tmp_path, ws_root="~")
    assert Path(proj.ws_root).resolve() == Path.home().resolve()


# ---------- (2) de-CWD autosave (report.md P1) ----------

class _NoopOpt(Base_Optimizer):
    """Concrete Base_Optimizer with no-op abstracts, so __init__'s autosave-path logic
    is testable without any SPICE/optimizer machinery."""
    def _create_optimizer_obj(self) -> bool:
        return True

    def parameterize(self) -> Any:
        return {}

    def evaluate(self, parameterization: Dict[str, float]) -> Tuple[np.floating, Dict[str, Any]]:
        return np.float64(0.0), {}

    def compute_fitness(self, performance_array):
        return np.float64(0.0), {}

    def optimization_step(self):
        return {}, np.float64(0.0), {}

    def plot_solution(self, parameterization, **kwargs):
        return None


def test_autosave_default_is_work_root_anchored(tmp_path, monkeypatch):
    # P3 (plan §6): the no-output_root default is WORK_ROOT/auto_save/<run-name> —
    # NOT CWD-relative — so a CLI/example/agent run can't spray ./auto_save dirs
    # wherever the process was launched.
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    proj = _load_with(tmp_path, ws_root=".")
    opt = _NoopOpt(proj)  # no output_root → WORK_ROOT/auto_save
    resolved = opt.autosave_checkpoint_dir.resolve()
    assert (tmp_path / "wr" / "auto_save").resolve() in resolved.parents
    # …and nothing anchored at the CWD.
    assert (tmp_path / "elsewhere" / "auto_save").resolve() not in resolved.parents


def test_autosave_output_root_routes_off_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    proj = _load_with(tmp_path, ws_root=".")
    work = (tmp_path / "work" / "runs" / "r1" / "checkpoints").resolve()
    opt = _NoopOpt(proj, output_root=work)
    resolved = opt.autosave_checkpoint_dir.resolve()
    # output_root is used AS the exact checkpoint dir (per-run isolation), NOT ./auto_save.
    assert resolved == work
    assert (tmp_path / "auto_save").resolve() not in resolved.parents


# ---------- (3) WORK_ROOT resolution (app_config) ----------

def test_work_root_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    import importlib

    from spicexplorer_api import app_config
    importlib.reload(app_config)
    assert app_config.work_root() == (tmp_path / "wr").resolve()
    assert app_config.auto_save_root() == (tmp_path / "wr" / "auto_save").resolve()


def test_work_root_default_under_repo(monkeypatch):
    monkeypatch.delenv("WORK_ROOT", raising=False)
    import importlib

    from spicexplorer_api import app_config
    importlib.reload(app_config)
    assert app_config.work_root() == (REPO_ROOT / "work").resolve()
