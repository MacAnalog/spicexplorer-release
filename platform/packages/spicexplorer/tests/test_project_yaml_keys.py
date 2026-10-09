"""Unknown project-YAML keys are reported, not dropped (BUG-35 / OPT-F8), and the optimizer
config's fallback messages state the values they actually set (OPT-17).

dacite maps the `project:` block onto the dataclasses non-strictly, so a key no dataclass
declares used to vanish without a word: `budgett: 999` left the budget at its old value,
`paralel_sim: false` left the run parallel, and the folded_cascode example's `freeze_to: 34u`
left the bias current swept over its whole range. `Project_Setup.from_yaml` now walks the block
against the dataclass fields first: one WARNING per unknown key by default, a ValueError in
strict mode (`strict=True`, or `SX_STRICT_PROJECT_KEYS=1` in the environment).
"""

import logging
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from _spicexplorer_fixtures import EXAMPLE_YAML
from spicexplorer.core.domains import (
    OptimizerConfig,
    Project_Setup,
    VariableBoundConfig,
    find_unknown_project_keys,
)

DOMAINS_LOGGER = "spicexplorer.designer_tools.domains"

# The typo probe from the audit, plus one typo at each nested level the walk descends into.
# Deliberately no target_specs typo: `TargetSpec(**item)` already raises on an unknown key.
TYPO_KEYS = [
    "paralel_sim",
    "optimizer_config.budgett",
    "dut_params[X_DUT_M1M2_W].freeze_to",
    "pvt.corners[tt_27C_1V5].tmep",
    "testbenches[tb_ac].params[CL].vall",
]


def _typo_project(tmp_path):
    """The cascode example with the TYPO_KEYS injected. Its `pvt:` block uses all three
    shorthand forms (`process_bundles`, `process:`, singular `supply:`), so it also checks that
    expanded keys are never reported as unknown."""
    data = yaml.safe_load(EXAMPLE_YAML.read_text())
    proj = data["project"]
    proj["ws_root"] = str(EXAMPLE_YAML.parent.parent)
    proj["paralel_sim"] = False
    proj["optimizer_config"]["budgett"] = 999
    proj["dut_params"][0]["freeze_to"] = "1u"
    proj["pvt"]["corners"][0]["tmep"] = 125
    tb = next(t for t in proj["testbenches"] if t["name"] == "tb_ac")
    next(p for p in tb["params"] if p["name"] == "CL")["vall"] = "1p"
    path = tmp_path / "project_setup.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path, proj


def test_the_typo_probe_names_every_unknown_key(tmp_path):
    _, proj = _typo_project(tmp_path)
    assert sorted(find_unknown_project_keys(proj)) == sorted(TYPO_KEYS)


def test_the_walk_does_not_mutate_the_block_it_is_given(tmp_path):
    """The walk expands `pvt:` on a copy: the caller's `process_bundles` must survive."""
    _, proj = _typo_project(tmp_path)
    find_unknown_project_keys(proj)
    assert "process_bundles" in proj["pvt"]
    assert proj["pvt"]["corners"][0]["process"] == "tt"


def test_unknown_keys_warn_by_default_and_the_project_still_loads(tmp_path, caplog, monkeypatch):
    # The default path, whatever the caller's shell exports (e.g. a strict `make ci-local`).
    monkeypatch.delenv("SX_STRICT_PROJECT_KEYS", raising=False)
    path, _ = _typo_project(tmp_path)
    budget = yaml.safe_load(EXAMPLE_YAML.read_text())["project"]["optimizer_config"]["budget"]
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        proj = Project_Setup.from_yaml(path)
    # Existing projects keep loading: the typo'd keys are still ignored, only no longer silently.
    assert proj.optimizer_config.budget == budget
    assert proj.parallel_sim is True
    warned = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    for key in TYPO_KEYS:
        assert any(f"'{key}'" in msg for msg in warned), f"no warning names {key!r}: {warned}"


def test_the_warning_suggests_the_key_that_was_probably_meant(tmp_path, caplog, monkeypatch):
    monkeypatch.delenv("SX_STRICT_PROJECT_KEYS", raising=False)
    path, _ = _typo_project(tmp_path)
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        Project_Setup.from_yaml(path)
    assert "did you mean 'budget'" in caplog.text
    assert "did you mean 'parallel_sim'" in caplog.text
    assert "did you mean 'freeze'" in caplog.text


def test_strict_mode_refuses_the_project_and_lists_every_unknown_key(tmp_path):
    path, _ = _typo_project(tmp_path)
    with pytest.raises(ValueError, match="unknown key") as exc:
        Project_Setup.from_yaml(path, strict=True)
    for key in TYPO_KEYS:
        assert key in str(exc.value)


@pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
def test_strict_mode_can_be_switched_on_from_the_environment(tmp_path, monkeypatch, value):
    path, _ = _typo_project(tmp_path)
    monkeypatch.setenv("SX_STRICT_PROJECT_KEYS", value)
    with pytest.raises(ValueError, match="budgett"):
        Project_Setup.from_yaml(path)


def test_an_explicit_strict_false_overrides_the_environment(tmp_path, monkeypatch):
    path, _ = _typo_project(tmp_path)
    monkeypatch.setenv("SX_STRICT_PROJECT_KEYS", "1")
    assert Project_Setup.from_yaml(path, strict=False).name


def test_a_clean_project_logs_no_unknown_key_warning(caplog):
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        Project_Setup.from_yaml(EXAMPLE_YAML, strict=True)
    assert "unknown key" not in caplog.text.lower()


# ------------------------------------------------------------ OPT-17: fallback messages
def _config(**kw) -> OptimizerConfig:
    # Typed Any: target_specs is a duck-typed stand-in for ListTargetSpec (pyright, not runtime).
    base: dict[str, Any] = dict(
        name="NGOpt",
        type="nevergrad",
        budget=10,
        optimizer_kwargs=None,
        target_specs=SimpleNamespace(targets=[]),
        lin_variable_bounds=None,
        log_variable_bounds=None,
        random_seed=None,
    )
    base.update(kw)
    return OptimizerConfig(**base)


@pytest.mark.parametrize("key", ["lin_variable_bounds", "log_variable_bounds"])
def test_the_missing_bounds_warning_states_the_default_it_sets(key, caplog):
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        cfg = _config()
    bounds = getattr(cfg, key)
    msg = next(r.getMessage() for r in caplog.records if key in r.getMessage())
    assert f"[{bounds.min}, {bounds.max}]" in msg, msg


def test_get_log_min_max_names_the_log_bounds_when_they_are_unset():
    cfg = _config()
    cfg.log_variable_bounds = None
    with pytest.raises(ValueError, match="Log variable bounds are not set"):
        cfg.get_log_min_max()


# ------------------------------------------------------------ more checks: what the walk reaches
def _example_project() -> dict:
    """A fresh, clean copy of the cascode example's raw `project:` block."""
    return yaml.safe_load(EXAMPLE_YAML.read_text())["project"]


def _write(tmp_path, proj: dict, **top) -> str:
    """Write `proj` (plus any extra top-level document keys) as a loadable project YAML."""
    proj["ws_root"] = str(EXAMPLE_YAML.parent.parent)
    path = tmp_path / "project_setup.yaml"
    path.write_text(yaml.safe_dump({"project": proj, **top}, sort_keys=False))
    return str(path)


def test_target_spec_keys_are_walked_and_runtime_state_is_not_a_key():
    """`target_specs` maps through DECITE_CONFIG's ListTargetSpec hook (a plain list of mappings,
    not a List[dataclass] field), and `TargetSpec.error_state` is runtime state (init=False): a
    public-helper caller walking raw YAML must see both as unknown."""
    proj = _example_project()
    spec = proj["optimizer_config"]["target_specs"][0]
    assert spec["name"] == "ugf"
    spec["tragte"] = 1
    spec["error_state"] = "stale"
    assert sorted(find_unknown_project_keys(proj)) == [
        "optimizer_config.target_specs[ugf].error_state",
        "optimizer_config.target_specs[ugf].tragte",
    ]


def test_strict_mode_names_a_target_spec_typo_before_the_constructor_trips_on_it(tmp_path):
    """The walk runs before dacite, so strict mode reports the typo by its dotted path instead of
    `TargetSpec(**item)`'s bare "unexpected keyword argument"."""
    proj = _example_project()
    proj["optimizer_config"]["target_specs"][0]["tragte"] = 1
    with pytest.raises(ValueError, match=r"optimizer_config\.target_specs\[ugf\]\.tragte"):
        Project_Setup.from_yaml(_write(tmp_path, proj), strict=True)


def test_an_unnamed_list_item_is_labelled_by_its_index():
    """A supply override has a `node`, not a `name`, so its item is labelled `[0]`. The typo sits in
    the singular `supply:` shorthand and is reported under the `supplies` path it expands to."""
    proj = _example_project()
    corner = proj["pvt"]["corners"][0]
    corner["supply"]["vlaue"] = 1.2
    assert find_unknown_project_keys(proj) == [f"pvt.corners[{corner['name']}].supplies[0].vlaue"]


def test_an_optional_nested_dataclass_is_walked():
    proj = _example_project()
    proj["optimizer_config"]["lin_variable_bounds"]["mni"] = 0
    proj["optimizer_config"]["log_variable_bounds"] = {"min": 1, "max": 100, "maxx": 1000}
    assert sorted(find_unknown_project_keys(proj)) == [
        "optimizer_config.lin_variable_bounds.mni",
        "optimizer_config.log_variable_bounds.maxx",
    ]


def test_free_form_mappings_are_opaque_to_the_walk():
    """Dict-typed fields carry user-named keys by design; walking them would flag real projects."""
    proj = _example_project()
    proj["tech_spec"]["constraints"]["max_rfet_w"] = "10u"
    proj["optimizer_config"]["optimizer_kwargs"] = {"popsize": 8, "anything": 1}
    proj["optimizer_config"]["aggregation_params"] = {"rho": 0.05}
    proj["optimizer_config"]["target_specs"][0]["error_params"] = {"sigma": 0.1}
    proj["pvt"]["corners"][0]["params"] = {"vcm": "0.6"}
    proj["pvt"]["corners"][0]["options"] = {"seed": 7}
    assert find_unknown_project_keys(proj) == []


@pytest.mark.parametrize(
    "patch",
    [
        {"pvt": None},
        {"optimizer_config": None},
        {"tech_spec": "ihp-sg13g2"},
        {"dut_params": None},
        {"dut_params": "X_DUT_M1M2_W"},
        {"dut_params": ["X_DUT_M1M2_W", 5, None]},
        {"testbenches": [{"name": "tb_ac", "params": None, "netlist": "x.spice"}]},
    ],
    ids=lambda p: repr(p)[:40],
)
def test_a_malformed_block_is_left_to_the_loader_and_does_not_crash_the_walk(patch):
    """A null, scalar or wrong-shaped block is dacite's to reject (with its own message); the walk
    must skip it rather than raise an AttributeError/TypeError that hides the real error."""
    assert find_unknown_project_keys({**_example_project(), **patch}) == []


def test_an_explicit_null_optional_block_loads_in_strict_mode(tmp_path):
    """`pvt: ~` (a project that opts out of corners) is valid and must load under strict mode."""
    proj = _example_project()
    proj["pvt"] = None
    loaded = Project_Setup.from_yaml(_write(tmp_path, proj), strict=True)
    assert loaded.pvt is None


def test_the_walk_is_idempotent_and_reports_in_document_order(tmp_path):
    """Same answer on a second call (the expansion ran on a copy), in the block's own key order:
    the example's `pvt`, `dut_params`, `testbenches`, `optimizer_config`, then the appended typo."""
    _, proj = _typo_project(tmp_path)
    first = find_unknown_project_keys(proj)
    assert (
        find_unknown_project_keys(proj)
        == first
        == [
            "pvt.corners[tt_27C_1V5].tmep",
            "dut_params[X_DUT_M1M2_W].freeze_to",
            "testbenches[tb_ac].params[CL].vall",
            "optimizer_config.budgett",
            "paralel_sim",
        ]
    )


def test_only_the_project_block_is_checked(tmp_path):
    """Other top-level document keys (analog-db's `assets:`) belong to other loaders."""
    path = _write(tmp_path, _example_project(), assets={"schematic": "x.sch"}, notes="free text")
    assert Project_Setup.from_yaml(path, strict=True).name


# ------------------------------------------------------------ more checks: the messages
def test_each_warning_names_the_file_once_per_key(tmp_path, caplog, monkeypatch):
    monkeypatch.delenv("SX_STRICT_PROJECT_KEYS", raising=False)
    path, _ = _typo_project(tmp_path)
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        Project_Setup.from_yaml(path)
    unknown = [r.getMessage() for r in caplog.records if r.getMessage().startswith("Unknown key")]
    assert len(unknown) == len(TYPO_KEYS), unknown
    assert all(str(path) in msg for msg in unknown), unknown


def test_the_strict_error_names_the_file_and_the_count(tmp_path):
    path, _ = _typo_project(tmp_path)
    with pytest.raises(ValueError) as exc:
        Project_Setup.from_yaml(path, strict=True)
    assert str(path) in str(exc.value)
    assert str(exc.value).startswith(f"{len(TYPO_KEYS)} unknown key(s)")


def test_no_hint_when_no_valid_key_is_close(tmp_path, caplog, monkeypatch):
    monkeypatch.delenv("SX_STRICT_PROJECT_KEYS", raising=False)
    proj = _example_project()
    proj["zzqqxx"] = 1
    proj["optimizer_config"]["lin_variable_bounds"]["mni"] = 0
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        Project_Setup.from_yaml(_write(tmp_path, proj))
    far = next(r.getMessage() for r in caplog.records if "'zzqqxx'" in r.getMessage())
    near = next(r.getMessage() for r in caplog.records if ".mni'" in r.getMessage())
    assert "did you mean" not in far, far
    assert "did you mean 'min'" in near, near


# ------------------------------------------------------------ more checks: the env switch
@pytest.mark.parametrize("value", ["", "0", "false", "no", "off", "strict"])
def test_any_other_env_value_leaves_strict_mode_off(tmp_path, caplog, monkeypatch, value):
    path, _ = _typo_project(tmp_path)
    monkeypatch.setenv("SX_STRICT_PROJECT_KEYS", value)
    with caplog.at_level(logging.WARNING, logger=DOMAINS_LOGGER):
        assert Project_Setup.from_yaml(path).name
    assert "'optimizer_config.budgett'" in caplog.text


@pytest.mark.parametrize("value", [" 1 ", "True\n", "\tON"])
def test_the_env_value_is_read_case_and_whitespace_insensitively(tmp_path, monkeypatch, value):
    path, _ = _typo_project(tmp_path)
    monkeypatch.setenv("SX_STRICT_PROJECT_KEYS", value)
    with pytest.raises(ValueError, match="budgett"):
        Project_Setup.from_yaml(path)


def test_an_explicit_strict_true_wins_over_an_off_environment(tmp_path, monkeypatch):
    path, _ = _typo_project(tmp_path)
    monkeypatch.setenv("SX_STRICT_PROJECT_KEYS", "0")
    with pytest.raises(ValueError, match="budgett"):
        Project_Setup.from_yaml(path, strict=True)


# ------------------------------------------------------------ more checks: OPT-17 values unchanged
def test_the_bound_defaults_themselves_are_unchanged():
    """OPT-17 corrected the MESSAGE; the defaults it describes are the historical ones."""
    cfg = _config()
    assert cfg.lin_variable_bounds == VariableBoundConfig(min=0.0, max=1.0)
    assert cfg.log_variable_bounds == VariableBoundConfig(min=1, max=100.0)
    assert cfg.get_log_min_max() == (1, 100.0)
