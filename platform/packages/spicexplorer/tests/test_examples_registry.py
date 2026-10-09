"""Every committed example project parses (no SPICE) — driven by the central
example registry in the workspace-root conftest. Adding an example auto-covers it."""

import pytest
import yaml
from spicexplorer.core.domains import Project_Setup, find_unknown_project_keys
from spicexplorer_core import project_root


def test_every_example_parses(example_yaml):
    # strict: a key no dataclass declares (a typo, a misplaced or legacy key) fails the example
    # instead of being dropped with no warning (BUG-35).
    proj = Project_Setup.from_yaml(example_yaml, strict=True)
    assert proj.dut_params, f"{example_yaml} parsed but has no dut_params"
    assert proj.optimizer_config.target_specs.targets, "no target specs parsed"


def _shipped_project_yamls():
    """Every project-shaped YAML under examples/ — the registry above only globs
    `project_setup.yaml`, so this also covers the `project_setup_*.yaml` variants, the
    ax_area_power configs and (when the submodule is checked out) the analog-db campaign
    configs. Super-DSL projections (`extends:`) are views, not optimizer configs."""
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)  # ~1.8k YAMLs with the analog-db corpus
    out = []
    for path in sorted((project_root() / "examples").rglob("*.yaml")):
        try:
            data = yaml.load(path.read_text(), Loader=loader)
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            continue
        if (
            isinstance(data, dict)
            and isinstance(data.get("project"), dict)
            and "extends" not in data
        ):
            out.append((path, data["project"]))
    return out


def test_no_shipped_project_yaml_carries_an_unknown_key():
    shipped = _shipped_project_yamls()
    names = {path.name for path, _ in shipped}
    # Never an empty scan: the platform's own variants are always present (analog-db may be absent).
    assert {"project_setup.yaml", "project_setup_multicorner.yaml"} <= names, names
    root = project_root()
    offenders = {
        str(path.relative_to(root)): keys
        for path, proj in shipped
        if (keys := find_unknown_project_keys(proj))
    }
    assert not offenders, f"unknown project keys (ignored at load): {offenders}"


def test_folded_cascode_bias_current_is_frozen_at_34u():
    """OPT-F8's example fix: `freeze_to: 34u` was dropped at load, so x_dut_IB was searched over
    1u..100u. The replacement must actually freeze it, at the value the comment always claimed."""
    proj = Project_Setup.from_yaml(
        project_root() / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml",
        strict=True,
    )
    ib = next(p for p in proj.dut_params if p.name == "x_dut_IB")
    assert ib.freeze is True
    assert ib.val == pytest.approx(34e-6)


def test_5t_ota_multicorner_fans_out_the_corner_axis():
    """The key moved from `optimizer_config` (where it was dropped) to `project:`; its comment says
    the corners simulate concurrently, so it must load as True."""
    proj = Project_Setup.from_yaml(
        project_root() / "examples/OTA/5t-ota/ihp-sg13g2/sizing/project_setup_multicorner.yaml",
        strict=True,
    )
    assert proj.parallel_sim is True
    assert proj.pvt is not None and len(proj.pvt.corners) == 5
