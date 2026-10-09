"""The Bode transfer-function optimizer is RETIRED (close-out WP-45, 2026-09-26).

`Spice_Bode_Optimizer` / `Nevergrad_Spice_Bode_Optimizer` were registered as
`Optimizer_Type_Enum.NEVERGRAD_BODE` but could not run: they called `extract_wave` on the
testbench DICT (AttributeError), the orchestrator never passed the required `target_tf`
(TypeError), and the fitter returned a lower-is-better loss to a loop that maximises. No YAML,
design, notebook or UI selected it. It was deleted with the helpers only it used:
`get_bode_fitness_loss`, `weighted_mse_loss` / `weighted_mae_loss`, `Frequency_Weight`, the
sympy<->control converters of `Transfer_Func_Helper`, and `core.tf_models` (the target-TF
models). With them went the last `import control`, so the `control` dependency went too.

This file is the proof the removal is complete and stays complete:

* the enum, the registry, the package exports and the classes carry no Bode optimizer;
* a project whose `optimizer_config.type` still says `nevergrad_bode` loads, and the
  orchestrator refuses it with a ValueError naming the retirement (the `_RETIRED_ENGINES`
  path the RL retirement added), not a bare "unknown engine";
* the Bode-only helpers are gone while the frequency-response plotting they sat beside stays;
* every `spicexplorer.*` module still imports, and none imports `control`;
* no live file names the retired classes or enum member (history under `doc/archive/` may).
"""

from __future__ import annotations

import ast
import dataclasses
import importlib
import os
import pkgutil
import re
import subprocess
import sys
from pathlib import Path

import pytest
from _spicexplorer_fixtures import EXAMPLE_YAML, REPO_ROOT

SPICEXPLORER_PKG = REPO_ROOT / "packages" / "spicexplorer"
SPICEXPLORER_SRC = SPICEXPLORER_PKG / "src" / "spicexplorer"
ORCHESTRATOR_PY = SPICEXPLORER_SRC / "optimization" / "orchestrator.py"

RETIRED_TYPE = "nevergrad_bode"
RETIRED_REASON = (
    "the Bode transfer-function optimizer was retired 2026-09-26 (it could not run as shipped)"
)

# The names only the Bode optimizer used, each checked gone from `spicexplorer.core.utils`.
BODE_ONLY_UTILS = (
    "get_bode_fitness_loss",
    "weighted_mse_loss",
    "weighted_mae_loss",
    "Frequency_Weight",
    "plot_ac_response",
    "_linear_interpolate",
)
BODE_ONLY_TF_METHODS = (
    "sympy_tf_to_control",
    "control_tf_to_sympy",
    "eval_tf",
    "get_ac_response_from_symbolic",
    "compute_cutoff",
)

# The project-YAML key that configured the Bode fitter's loss (#307): refused at load.
RETIRED_KEY = "optimizer_config.loss_function_config"

# A module that needs an optional extra may fail to import on a base install, but only on that
# extra's own packages: `bayesian_ax` needs `uv sync --extra ax`.
_OPTIONAL_EXTRA_PACKAGES = {"ax", "botorch", "torch"}

_SKIP_DIRS = {
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
}
_RETIRED_NAME = re.compile(r"Spice_Bode|NEVERGRAD_BODE|nevergrad_bode")


def _setup_with_type(value):
    """The example project with `optimizer_config.type` set to `value`."""
    from spicexplorer.core.domains import Project_Setup

    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    setattr(setup.optimizer_config, "type", value)
    return setup


# ── the optimizer is gone ─────────────────────────────────────────────────────


def test_the_optimizer_enum_and_registry_have_no_bode_member():
    from spicexplorer.optimization import SPICE_OPTIMIZER_CLASSES, Optimizer_Type_Enum

    assert "NEVERGRAD_BODE" not in Optimizer_Type_Enum.__members__
    assert RETIRED_TYPE not in {t.value for t in Optimizer_Type_Enum}
    assert not [t for t in SPICE_OPTIMIZER_CLASSES if "bode" in t.value]


def test_the_bode_optimizer_classes_are_gone():
    import spicexplorer.optimization as optimization
    from spicexplorer.optimization import base
    from spicexplorer.optimization.stochastic import nevergrad

    assert "Nevergrad_Spice_Bode_Optimizer" not in optimization.__all__
    assert not hasattr(optimization, "Nevergrad_Spice_Bode_Optimizer")
    assert not hasattr(nevergrad, "Nevergrad_Spice_Bode_Optimizer")
    assert not hasattr(base, "Spice_Bode_Optimizer")
    # the two live Nevergrad endpoints stay
    assert {"Nevergrad_Spice_Single_Objective", "Nevergrad_Spice_Constraint_Satisfaction"} <= set(
        optimization.__all__
    )


# ── a stale `nevergrad_bode` project is refused, naming the retirement ────────


@pytest.mark.parametrize("spelled", ["nevergrad_bode", "NEVERGRAD_BODE", " Nevergrad_Bode\n"])
def test_a_nevergrad_bode_type_is_refused_naming_the_retirement(spelled):
    from spicexplorer.core.domains import OptimizerType
    from spicexplorer.optimization.orchestrator import optimizer_type_from_config

    with pytest.raises(ValueError) as info:
        optimizer_type_from_config(_setup_with_type(spelled))
    msg = str(info.value)
    assert (
        f"optimizer_config.type='{RETIRED_TYPE}' is no longer supported: {RETIRED_REASON}; " in msg
    )
    assert msg.endswith(f"choose one of {[t.value for t in OptimizerType]}.")
    assert "not a known engine" not in msg


@pytest.mark.parametrize("near_miss", ["bode", "nevergrad-bode", "nevergrad_bode_v2"])
def test_a_near_miss_is_still_an_unknown_engine(near_miss):
    from spicexplorer.optimization.orchestrator import optimizer_type_from_config

    with pytest.raises(ValueError, match="is not a known engine; choose one of") as info:
        optimizer_type_from_config(_setup_with_type(near_miss))
    assert "retired" not in str(info.value)


def test_a_stale_bode_yaml_loads_but_the_orchestrator_refuses_it(tmp_path):
    """The file still opens (the UI can show it); the run stops where the engine is resolved,
    at the orchestrator's construction, before any simulator is built."""
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE

    text = EXAMPLE_YAML.read_text()
    text, n_root = re.subn(
        r"(?m)^([ \t]*ws_root[ \t]*:).*$",
        lambda m: f"{m.group(1)} {EXAMPLE_YAML.parent.parent}",
        text,
        count=1,
    )
    text, n_type = re.subn(
        r"(?m)^([ \t]*type:[ \t]*)nevergrad[ \t]*$", rf"\g<1>{RETIRED_TYPE}", text
    )
    assert (n_root, n_type) == (1, 1)
    stale = tmp_path / "stale_bode_project.yaml"
    stale.write_text(text)

    assert Project_Setup.from_yaml(stale).optimizer_config.type == RETIRED_TYPE
    with pytest.raises(ValueError, match=f"no longer supported: {re.escape(RETIRED_REASON)}"):
        Circuit_Optimizer_Orchestrator_with_SPICE(stale, auto_load=False)


# ── a stale `loss_function_config` block is refused at load (#307) ────────────


def _example_yaml_text_with_ws_root():
    text = EXAMPLE_YAML.read_text()
    text, n_root = re.subn(
        r"(?m)^([ \t]*ws_root[ \t]*:).*$",
        lambda m: f"{m.group(1)} {EXAMPLE_YAML.parent.parent}",
        text,
        count=1,
    )
    assert n_root == 1
    return text


@pytest.mark.parametrize("strict", [None, False, True])
def test_a_loss_function_config_block_is_refused_naming_the_retired_bode_fitter(tmp_path, strict):
    """`optimizer_config.loss_function_config` configured only the retired Bode fitter. A YAML that
    still carries it stops at load with a ValueError naming the key and the retirement, in every
    strictness mode, instead of loading with an ignored-key warning."""
    import yaml
    from spicexplorer.core.domains import Project_Setup

    data = yaml.safe_load(_example_yaml_text_with_ws_root())
    data["project"]["optimizer_config"]["loss_function_config"] = {
        "max_loss": 1.0,
        "loss_norm_method": None,
        "loss_type": None,
    }
    stale = tmp_path / "stale_loss_project.yaml"
    stale.write_text(yaml.safe_dump(data))

    with pytest.raises(ValueError) as info:
        Project_Setup.from_yaml(stale, strict=strict)
    msg = str(info.value)
    assert f"{RETIRED_KEY} is no longer supported" in msg
    assert "Bode transfer-function optimizer" in msg and "retired" in msg
    assert str(stale) in msg
    assert "unknown key" not in msg.lower()


def test_a_project_without_the_key_logs_nothing_about_it(caplog):
    import logging

    from spicexplorer.core.domains import Project_Setup

    with caplog.at_level(logging.DEBUG):
        setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    assert "loss_function_config" not in caplog.text
    assert not hasattr(setup.optimizer_config, "loss_function_config")


def test_the_loss_function_config_class_is_gone():
    from spicexplorer.core import domains

    assert not hasattr(domains, "LossFunctionConfig")
    assert "loss_function_config" not in {
        f.name for f in dataclasses.fields(domains.OptimizerConfig)
    }


def test_core_utils_does_not_import_sympy():
    """`eval_tf` was the only reason `core.utils` imported sympy. A fresh interpreter, because
    sympy may already be loaded in this one (netlist2tf). sympy stays installed in the workspace
    venv through netlist2tf, so this pins the import edge, not the package's absence."""
    code = (
        "import spicexplorer.core.utils, sys; assert 'sympy' not in sys.modules, 'sympy imported'"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_the_base_distribution_does_not_declare_sympy():
    # Text, not tomllib: the package still supports Python 3.10.
    text = (SPICEXPLORER_PKG / "pyproject.toml").read_text()
    assert re.findall(r"(?m)^\s*[\"']sympy\b.*$", text) == []


# ── the Bode-only helpers are gone; the plotting beside them stays ────────────


def test_the_bode_only_helpers_are_gone():
    from spicexplorer.core import utils

    assert [n for n in BODE_ONLY_UTILS if hasattr(utils, n)] == []
    assert [m for m in BODE_ONLY_TF_METHODS if hasattr(utils.Transfer_Func_Helper, m)] == []
    with pytest.raises(ModuleNotFoundError) as info:
        importlib.import_module("spicexplorer.core.tf_models")
    assert info.value.name == "spicexplorer.core.tf_models"


def test_the_frequency_response_helpers_stay():
    """`Spice_Base_Optimizer.plot` draws an AC result through `plot_complex_response`, which reads
    magnitude/phase through `Transfer_Func_Helper`: those are not Bode-only and must survive."""
    import numpy as np
    from spicexplorer.core.utils import Transfer_Func_Helper, plot_complex_response

    assert callable(plot_complex_response)
    mag, phase = Transfer_Func_Helper().get_mag_phase_from_complex_response(np.asarray([1.0, 1j]))
    assert mag.tolist() == pytest.approx([0.0, 0.0])
    assert phase.tolist() == pytest.approx([0.0, 90.0])


# ── every module imports; nothing imports `control` ───────────────────────────


def test_every_spicexplorer_module_imports():
    import spicexplorer

    failed = []
    for info in pkgutil.walk_packages(spicexplorer.__path__, "spicexplorer."):
        try:
            importlib.import_module(info.name)
        except ModuleNotFoundError as exc:
            if (exc.name or "").split(".")[0] not in _OPTIONAL_EXTRA_PACKAGES:
                failed.append(f"{info.name}: {exc!r}")
        except Exception as exc:  # noqa: BLE001 - report every broken module at once
            failed.append(f"{info.name}: {exc!r}")
    assert failed == [], "modules that no longer import:\n" + "\n".join(failed)


def _imports_control(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            a.name.split(".")[0] == "control" for a in node.names
        ):
            return True
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and (node.module or "").split(".")[0] == "control"
        ):
            return True
    return False


def test_the_imports_control_scan_sees_each_form():
    """Positive control for the scan below."""
    for src in (
        "import control",
        "import control as ctrl",
        "from control import tf",
        "from control.matlab import bode",
        "def f():\n    import control.xferfcn\n",
    ):
        assert _imports_control(ast.parse(src)), src
    for src in ("import controller", "from .control import x", "from spicexplorer import control"):
        assert not _imports_control(ast.parse(src)), src


def test_no_spicexplorer_module_imports_control_and_it_is_not_a_dependency():
    hits = [
        str(p.relative_to(REPO_ROOT))
        for p in sorted(SPICEXPLORER_SRC.rglob("*.py"))
        if _imports_control(ast.parse(p.read_text(encoding="utf-8"), filename=str(p)))
    ]
    assert hits == [], "`control` is imported again:\n" + "\n".join(hits)
    # the base `dependencies = [...]` list (tomllib is 3.11+, the package supports 3.10)
    pyproject = (SPICEXPLORER_PKG / "pyproject.toml").read_text()
    deps = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)^\]", pyproject)
    assert deps is not None
    assert not re.search(r"""(?m)^\s*["']control\b""", deps.group(1)), deps.group(1)


# ── no live file names the retired optimizer ──────────────────────────────────


_LIVE_SUFFIXES = (".py", ".md", ".toml", ".yaml", ".yml", ".cfg", ".ini")


def _live_text_files():
    """The repo's source, docs and configs: top-level files plus the tracked trees (not `work/`
    or `logs/` run output). `doc/archive/` keeps history and is not scanned."""
    yield from (
        p for p in sorted(REPO_ROOT.iterdir()) if p.is_file() and p.name.endswith(_LIVE_SUFFIXES)
    )
    archive = REPO_ROOT / "doc" / "archive"
    for top in ("doc", "packages", "examples", "tests", "scripts", "ci"):
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT / top):
            here = Path(dirpath)
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and here / d != archive]
            yield from (here / n for n in filenames if n.endswith(_LIVE_SUFFIXES))


def _allowed(path: Path, match: str) -> bool:
    """This file, and the retired-engine table's `nevergrad_bode` key that produces the refusal."""
    return path == Path(__file__).resolve() or (
        path == ORCHESTRATOR_PY.resolve() and match == RETIRED_TYPE
    )


def test_no_live_file_names_the_retired_optimizer():
    hits = []
    for path in _live_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in _RETIRED_NAME.finditer(text):
            if not _allowed(path.resolve(), m.group(0)):
                hits.append(
                    f"{path.relative_to(REPO_ROOT)}:{text.count(chr(10), 0, m.start()) + 1}: {m.group(0)}"
                )
    assert hits == [], "live files still name the retired Bode optimizer:\n" + "\n".join(hits)
