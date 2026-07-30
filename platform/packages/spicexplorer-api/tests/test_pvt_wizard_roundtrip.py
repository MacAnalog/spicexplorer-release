"""Round-trip test for the wizard ⇄ YAML PVT mapping (yaml_generator).

Skipped unless the `ui` extra is installed (the backend imports FastAPI/pydantic).
No ngspice / PDK needed — pure dict transforms + a library re-parse.
"""
import os
import sys
import tempfile

import pytest
import yaml
from _api_fixtures import REPO_ROOT

# `ui` lives at the repo root (not under src/), so it isn't on sys.path by default
# under pytest. Add it, then skip cleanly if the `ui` extra (FastAPI/pydantic) is absent.
sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")

from spicexplorer.core.domains import Project_Setup
from spicexplorer_api.services.yaml_generator import generate_yaml, project_dict_to_form

FC_YAML = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"


def test_pvt_block_roundtrips_through_the_wizard():
    raw = yaml.safe_load(FC_YAML.read_text())

    # YAML (with process_bundles) → wizard form: bundles flatten to inline includes.
    form = project_dict_to_form(raw)
    assert form["pvt"]["active_corner"] == "tt_27C_1V8"
    names = [c["name"] for c in form["pvt"]["corners"]]
    assert names == ["tt_27C_1V8", "ss_125C_1V62", "ff_m40C_1V98"]
    tt = form["pvt"]["corners"][0]
    assert tt["supply_node"] == "VDD"
    assert [(m["lib_file"], m["section"]) for m in tt["includes"]][0] == ("cornerMOSlv.lib", "mos_tt")
    assert form["pvt"]["corners"][2]["enabled"] is False  # ff is disabled

    # the multi-corner (Phase 2) knobs survive YAML → form…
    assert form["pvt"]["mode"] == "multi"
    assert form["pvt"]["score_aggregation"] == "mean"

    # wizard form → YAML → library: re-parses to the same active corner.
    out_yaml = generate_yaml(form)
    assert "pvt:" in out_yaml and "active_corner" in out_yaml

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", dir=str(FC_YAML.parent), delete=False) as f:
        f.write(out_yaml)
        tmp = f.name
    try:
        project = Project_Setup.from_yaml(tmp)
        assert project.pvt is not None
        assert project.pvt.active_corner == "tt_27C_1V8"
        # …and form → YAML → library: a wizard Save must not silently revert a
        # multi-corner project to single-corner (the WIZ-2/BUG-A3 failure class).
        assert project.pvt.mode == "multi"
        assert project.pvt.score_aggregation == "mean"
        active = project.pvt.get_active()
        assert active.temp == 27.0
        assert active.supplies[0].value == 1.8
        assert [(m.lib_file, m.section) for m in active.model_includes][0] == ("cornerMOSlv.lib", "mos_tt")
    finally:
        os.unlink(tmp)


def test_non_default_aggregation_roundtrips_through_the_wizard():
    raw = yaml.safe_load(FC_YAML.read_text())
    raw["project"]["pvt"]["score_aggregation"] = "worst_case"  # alias of canonical "min"

    form = project_dict_to_form(raw)
    assert form["pvt"]["score_aggregation"] == "worst_case"

    out_yaml = generate_yaml(form)
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", dir=str(FC_YAML.parent), delete=False) as f:
        f.write(out_yaml)
        tmp = f.name
    try:
        project = Project_Setup.from_yaml(tmp)
        assert project.pvt.mode == "multi"
        assert project.pvt.score_aggregation == "min"  # alias normalized at load
    finally:
        os.unlink(tmp)


def test_project_without_pvt_yields_empty_wizard_pvt():
    raw = yaml.safe_load(
        (REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml").read_text()
    )
    # The cascode example now ships a first-class `pvt:` block (commit dc8b6f5) under
    # `project:`, so drop it here to exercise the genuine no-PVT path independently of how
    # the example evolves.
    (raw.get("project") or {}).pop("pvt", None)
    form = project_dict_to_form(raw)
    assert form["pvt"] == {
        "active_corner": "", "corners": [], "model_lib_root": "",
        # Phase-2 knobs are always present in the form, defaulted for no-PVT projects.
        "mode": "single", "score_aggregation": "mean",
    }
    # …and generating from it emits no `pvt:` block.
    assert "\npvt:" not in generate_yaml(form)


def test_pvt_model_lib_root_survives_wizard_roundtrip():
    """WIZ-2/BUG-A3: model_lib_root must round-trip through the wizard — it is load-bearing
    (apply_corner prepends it to each include's lib_file), not display-only."""
    from spicexplorer_api.services.yaml_generator import _build_pvt_block, _pvt_block_to_form

    root = "/pdk/ihp-sg13g2/libs.tech/ngspice/models"
    form_pvt = {
        "active_corner": "tt",
        "model_lib_root": root,
        "corners": [
            {
                "name": "tt", "temp": "27", "supply_node": "VDD", "supply_value": "1.5",
                "enabled": True,
                "includes": [{"lib_file": "cornerMOSlv.lib", "section": "mos_tt"}],
            }
        ],
    }
    block = _build_pvt_block({"pvt": form_pvt})
    assert block is not None and block["model_lib_root"] == root  # emitted, not dropped
    assert _pvt_block_to_form(block)["model_lib_root"] == root      # carried back to the form


def test_pvt_multi_rail_supplies_survive_wizard_roundtrip():
    """WIZ-4/BUG-A6: a corner's rails 2..N must not be silently dropped by the wizard."""
    from spicexplorer_api.services.yaml_generator import _build_pvt_block, _pvt_block_to_form

    form_pvt = {
        "active_corner": "tt",
        "corners": [
            {
                "name": "tt", "temp": "27",
                "supply_node": "VDD", "supply_value": "1.8",
                "extra_supplies": [{"node": "VDDH", "value": "3.3"}],
                "enabled": True,
                "includes": [{"lib_file": "cornerMOSlv.lib", "section": "mos_tt"}],
            }
        ],
    }
    block = _build_pvt_block({"pvt": form_pvt})
    rails = block["corners"][0]["supplies"]  # multi-rail → emitted as `supplies` list
    assert [r["node"] for r in rails] == ["VDD", "VDDH"]
    assert [float(r["value"]) for r in rails] == [1.8, 3.3]

    back = _pvt_block_to_form(block)["corners"][0]  # …and carried back through the form
    assert back["supply_node"] == "VDD"
    assert len(back["extra_supplies"]) == 1
    assert back["extra_supplies"][0]["node"] == "VDDH"
    assert float(back["extra_supplies"][0]["value"]) == 3.3
