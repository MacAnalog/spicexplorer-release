"""Smoke tests for spicexplorer.optimization.

Coverage (layered — each layer builds on the previous):
  Layer 1 — no SPICE needed:
    - Project_Setup loads from YAML and has expected structure
    - Orchestrator can be created without auto_load
  Layer 2 — ngspice required:
    - Orchestrator.initialize() creates one wrapper per enabled testbench
    - Optimizer.parameterize() returns a valid Nevergrad parameter dict
  Layer 3 — ngspice required + slow:
    - One optimization_step() runs a real simulation without crashing
"""
import re
from pathlib import Path

import pytest
from _spicexplorer_fixtures import EXAMPLE_YAML, REPO_ROOT, requires_ngspice, requires_pdk, slow

# Example projects whose YAML parses today. folded_cascode now parses cleanly:
# its first-class `pvt:` block drives the simulator, while the legacy
# `pvt_map` / `pvt_corners` are display-only and silently ignored.
PORTABLE_EXAMPLE_YAMLS = [
    "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml",
    "examples/OTA/5t-ota/ihp-sg13g2/sizing/project_setup.yaml",
    "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml",
]


# ── Layer 1: no SPICE required ──────────────────────────────────────────────

@pytest.mark.parametrize("rel_yaml", PORTABLE_EXAMPLE_YAMLS)
def test_ws_root_resolves_relative_to_yaml(rel_yaml):
    """`ws_root` resolves against the YAML's own directory so the committed
    examples are portable on a fresh clone — no hardcoded absolute paths.

    Guards the resolution rule in Project_Setup.from_yaml(): the examples ship
    `ws_root: ..`, which must resolve to the design root (the YAML's grandparent)
    and contain every referenced netlist.
    """
    from spicexplorer.core.domains import Project_Setup

    yaml_path = (REPO_ROOT / rel_yaml).resolve()
    setup = Project_Setup.from_yaml(yaml_path)

    ws = Path(setup.ws_root)
    assert ws.is_absolute(), f"ws_root should be absolute, got {ws!r}"
    assert ws == yaml_path.parent.parent, (
        f"ws_root should resolve to the design root (yaml/../..); got {ws}"
    )
    assert ws.is_dir(), f"resolved ws_root does not exist: {ws}"

    dut_netlist = ws / setup.netlist
    assert dut_netlist.is_file(), f"DUT netlist not found at resolved path: {dut_netlist}"

    for tb in setup.testbenches:
        if not tb.enable:
            continue
        tb_netlist = ws / tb.netlist
        assert tb_netlist.is_file(), f"testbench netlist not found: {tb_netlist}"


def _example_yaml_with_ws_root(tmp_path, ws_root_value):
    """Copy the cascode example YAML into ``tmp_path``, overriding ``ws_root``.

    ``ws_root_value=None`` removes the field entirely (the omitted case). Returns
    the path to the written YAML. Only ws_root resolution is exercised here —
    from_yaml() does not stat the netlists, so they need not exist in tmp_path.
    """
    text = (REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml").read_text()
    if ws_root_value is None:
        text = re.sub(r"(?m)^[ \t]*ws_root[ \t]*:.*$", "", text)
    else:
        text = re.sub(r"(?m)^[ \t]*ws_root[ \t]*:.*$", f"  ws_root : {ws_root_value}", text)
    dest = tmp_path / "project_setup.yaml"
    dest.write_text(text)
    return dest


def test_ws_root_absolute_is_used_as_is(tmp_path):
    """An absolute ws_root is honoured verbatim (server / out-of-repo workspace),
    never joined to the YAML's directory."""
    from spicexplorer.core.domains import Project_Setup

    external_ws = (tmp_path.parent / "spx_external_ws").resolve()  # absolute, outside yaml dir
    yaml_path = _example_yaml_with_ws_root(tmp_path, str(external_ws))
    setup = Project_Setup.from_yaml(yaml_path)
    assert Path(setup.ws_root) == external_ws


@pytest.mark.parametrize("ws_root_value", [None, '""'], ids=["omitted", "empty"])
def test_ws_root_omitted_or_empty_defaults_to_yaml_dir(tmp_path, ws_root_value):
    """A missing or empty ws_root defaults to the YAML file's own directory."""
    from spicexplorer.core.domains import Project_Setup

    yaml_path = _example_yaml_with_ws_root(tmp_path, ws_root_value)
    setup = Project_Setup.from_yaml(yaml_path)
    assert Path(setup.ws_root) == tmp_path.resolve()


def test_ws_root_tilde_is_expanded(tmp_path):
    """A leading ~ in ws_root expands to the user's home, not the YAML directory."""
    from spicexplorer.core.domains import Project_Setup

    yaml_path = _example_yaml_with_ws_root(tmp_path, "~/spx_ws_unit_test")
    setup = Project_Setup.from_yaml(yaml_path)
    assert Path(setup.ws_root) == (Path.home() / "spx_ws_unit_test").resolve()


def test_project_setup_loads():
    """Project_Setup.from_yaml() parses the example OTA project correctly."""
    from spicexplorer.core.domains import Project_Setup

    setup = Project_Setup.from_yaml(EXAMPLE_YAML)

    assert setup.name, "Project name must be non-empty"
    assert len(setup.dut_params) > 0, "Expected at least one DUT parameter"
    assert len(setup.testbenches) > 0, "Expected at least one testbench"
    assert len(setup.optimizer_config.target_specs.targets) > 0, "Expected at least one target spec"
    assert setup.optimizer_config.budget > 0


def test_project_setup_param_bounds():
    """All DUT parameters have valid (non-None, min < max) bounds."""
    from spicexplorer.core.domains import Project_Setup

    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    for p in setup.dut_params:
        if p.freeze:
            continue
        assert p.min_val is not None, f"Param {p.name} has no min_val"
        assert p.max_val is not None, f"Param {p.name} has no max_val"
        assert float(p.min_val) < float(p.max_val), (
            f"Param {p.name}: min_val ({p.min_val}) >= max_val ({p.max_val})"
        )


def test_orchestrator_no_autoload():
    """Orchestrator can be constructed without calling initialize() (auto_load=False)."""
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=EXAMPLE_YAML,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
        auto_load=False,
    )
    assert orchestrator.project_setup is not None
    assert not hasattr(orchestrator, "spicelib_wrappers") or orchestrator.spicelib_wrappers is None


# ── Layer 2: ngspice required ────────────────────────────────────────────────

@requires_ngspice
def test_orchestrator_initialize_creates_wrappers(tmp_path):
    """initialize() creates one NGSpice_Wrapper per enabled testbench."""
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=EXAMPLE_YAML,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
        auto_load=False,
    )
    orchestrator.initialize()

    enabled_tbs = [tb for tb in orchestrator.project_setup.testbenches if tb.enable]
    assert len(orchestrator.spicelib_wrappers) == len(enabled_tbs), (
        f"Expected {len(enabled_tbs)} wrappers, got {len(orchestrator.spicelib_wrappers)}"
    )


@requires_ngspice
def test_optimizer_parameterize(tmp_path):
    """parameterize() builds the Nevergrad parameter space without running SPICE."""
    import nevergrad as ng
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=EXAMPLE_YAML,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
        auto_load=True,
    )
    optimizer = orchestrator.get_optimizer()
    param_dict = optimizer.parameterize()

    assert isinstance(param_dict, ng.p.Dict), "parameterize() must return a nevergrad Dict"
    assert len(param_dict) > 0, "parameterize() returned an empty parameter dict"
    # All nevergrad keys must correspond to known DUT parameter names
    dut_param_names = {p.name for p in orchestrator.project_setup.dut_params}
    unknown = set(param_dict.keys()) - dut_param_names
    assert not unknown, f"parameterize() produced keys not in dut_params: {unknown}"


# ── Layer 3: slow end-to-end ─────────────────────────────────────────────────

@requires_ngspice
@requires_pdk
@slow
def test_one_optimization_step():
    """A single optimization step runs a real SPICE simulation and returns a score."""
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=EXAMPLE_YAML,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
        auto_load=True,
    )
    optimizer = orchestrator.get_optimizer()
    optimizer.parameterize()
    # optimization_step() calls self.optimizer.ask(); build that object first — the same
    # contract the optimize() loop, sanity.py, and optimizer_runner all follow.
    assert optimizer._create_optimizer_obj(), "optimizer object failed to build"

    params, score, metadata = optimizer.optimization_step()

    assert isinstance(params, dict) and len(params) > 0, "optimization_step() must return a non-empty params dict"
    assert score is not None, "optimization_step() must return a numeric score"
    assert metadata is not None, "optimization_step() must return metadata"
