"""Every committed example project parses (no SPICE) — driven by the central
example registry in the workspace-root conftest. Adding an example auto-covers it."""
from spicexplorer.core.domains import Project_Setup


def test_every_example_parses(example_yaml):
    proj = Project_Setup.from_yaml(example_yaml)
    assert proj.dut_params, f"{example_yaml} parsed but has no dut_params"
    assert proj.optimizer_config.target_specs.targets, "no target specs parsed"
