"""Workspace-root pytest config — the central example registry (§9).

Every committed `examples/**/project_setup.yaml` is discovered once here, so adding
a new example automatically adds coverage (any test that takes an `example_yaml`
parameter runs against all of them) without editing a hardcoded list per test file.
"""
import pytest
import yaml
from spicexplorer_core import project_root


def _is_super_dsl_projection(path):
    """True for analog-db super-DSL projections (`extends: circuit.yaml`).

    These are thin views over the canonical circuit.yaml (plan D-3), not standalone
    optimizer configs — the Phase-3 generator expands them. They are NOT part of the
    legacy optimizer example corpus, so the registry skips them.
    """
    try:
        with path.open() as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError):
        return False
    return isinstance(data, dict) and "extends" in data


def discover_example_yamls():
    """All committed standalone example project YAMLs (the demo / test corpus)."""
    found = (project_root() / "examples").rglob("project_setup.yaml")
    return sorted(p for p in found if not _is_super_dsl_projection(p))


def _example_id(path):
    # examples/OTA/<topology>/<pdk>/sizing/project_setup.yaml -> "OTA/<topology>"
    parts = path.parts
    i = parts.index("examples")
    return "/".join(parts[i + 1 : i + 3])


@pytest.fixture(scope="session")
def example_yamls():
    return discover_example_yamls()


def pytest_generate_tests(metafunc):
    """Parametrize any test that requests `example_yaml` over every discovered example."""
    if "example_yaml" in metafunc.fixturenames:
        ys = discover_example_yamls()
        metafunc.parametrize("example_yaml", ys, ids=[_example_id(y) for y in ys])
