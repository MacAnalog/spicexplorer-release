"""Tests for the PVT corner system (single-corner).

All tests here are Layer 1 — they need neither a real ngspice simulation nor the
IHP PDK:

  • the `pvt:` YAML block parses; process bundles expand into concrete includes;
    a singular `supply` widens to `supplies`; the enabled filter + active resolution
    work; bad references raise.
  • `NGSpice_Wrapper.apply_corner()` mutates the in-memory netlist editor correctly
    (strips the hardcoded `.lib`, injects the corner includes, sets `.options temp`,
    overrides the supply `.param`) — asserted by inspecting `editor.netlist`, with NO
    simulation run.
"""
import re
from pathlib import Path

import pytest
from _spicexplorer_fixtures import REPO_ROOT, requires_ngspice
from spicexplorer.core.domains import (
    Corner,
    Project_Setup,
    PVTConfig,
    _normalize_pvt_block,
)

FC_YAML = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"
FC_TB_NETLIST = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/spice/cora_testbench.spice"
CASCODE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"


# ── parsing / desugaring ────────────────────────────────────────────────────

def test_pvt_block_parses_and_expands():
    p = Project_Setup.from_yaml(FC_YAML)
    assert p.pvt is not None
    assert p.pvt.active_corner == "tt_27C_1V8"
    assert [c.name for c in p.pvt.corners] == ["tt_27C_1V8", "ss_125C_1V62", "ff_m40C_1V98"]
    # enabled filter excludes the disabled ff corner
    assert [c.name for c in p.pvt.enabled_corners()] == ["tt_27C_1V8", "ss_125C_1V62"]

    # active resolves; its process bundle expanded into concrete, ordered includes
    a = p.pvt.get_active()
    assert a.temp == 27.0
    assert (a.supplies[0].node, a.supplies[0].value) == ("VDD", 1.8)
    assert [(m.lib_file, m.section) for m in a.model_includes] == [
        ("cornerMOSlv.lib", "mos_tt"),
        ("cornerRES.lib", "res_typ"),
        ("cornerCAP.lib", "cap_typ"),
    ]

    ss = p.pvt.get("ss_125C_1V62")
    assert ss.model_includes[0].section == "mos_ss"
    assert ss.temp == 125.0
    assert ss.supplies[0].value == 1.62


def test_get_active_unknown_raises():
    cfg = PVTConfig(active_corner="nope", corners=[Corner(name="tt")])
    with pytest.raises(ValueError):
        cfg.get_active()


def test_normalize_dangling_bundle_raises():
    proj = {"pvt": {"active_corner": "c", "corners": [{"name": "c", "process": "missing"}]}}
    with pytest.raises(ValueError):
        _normalize_pvt_block(proj)


def test_normalize_inline_includes_and_singular_supply():
    proj = {
        "pvt": {
            "active_corner": "x",
            "corners": [
                {
                    "name": "x",
                    "model_includes": [{"lib_file": "a.lib", "section": "s1"}],
                    "supply": {"node": "VDD", "value": "1.2"},  # eng-string + singular sugar
                    "temp": 27,
                }
            ],
        }
    }
    _normalize_pvt_block(proj)
    c = proj["pvt"]["corners"][0]
    assert c["model_includes"] == [{"lib_file": "a.lib", "section": "s1"}]
    assert c["supplies"] == [{"node": "VDD", "value": 1.2}]
    assert "supply" not in c
    assert c["temp"] == 27.0
    # process_bundles sugar key is dropped entirely
    assert "process_bundles" not in proj["pvt"]


def test_normalize_noop_without_pvt():
    proj = {"name": "x"}
    _normalize_pvt_block(proj)  # must not raise / must not invent a pvt key
    assert "pvt" not in proj


# ── apply_corner netlist mutation (no simulation) ───────────────────────────

def _make_wrapper(tmp_path):
    from spicexplorer_core.spice_engine.spicelib import NGSpice_Wrapper

    return NGSpice_Wrapper(
        netlist_filename=FC_TB_NETLIST,
        testbench_name="cora_tb",
        output_folder=tmp_path / "pvt_out",
    )


def _joined(wrapper) -> str:
    return "\n".join(ln for ln in wrapper.editor.netlist if isinstance(ln, str))


@pytest.mark.skipif(not FC_TB_NETLIST.exists(), reason="folded_cascode testbench netlist missing")
def test_apply_corner_mutates_netlist(tmp_path):
    p = Project_Setup.from_yaml(FC_YAML)
    ss = p.pvt.get("ss_125C_1V62")

    w = _make_wrapper(tmp_path)
    # sanity: the netlist ships the hardcoded tt corner
    assert ".lib cornerMOSlv.lib mos_tt" in _joined(w)

    w.apply_corner(ss)
    joined = _joined(w)

    # hardcoded tt corner replaced by the ss selection (all three families)
    assert ".lib cornerMOSlv.lib mos_tt" not in joined
    assert ".lib cornerMOSlv.lib mos_ss" in joined
    assert ".lib cornerRES.lib res_wcs" in joined
    assert ".lib cornerCAP.lib cap_wcs" in joined
    # authoritative temperature directive
    assert re.search(r"\.options?\s+temp\s*=\s*125", joined)
    # supply override applied to the .param
    assert abs(float(w.editor.get_parameter("VDD")) - 1.62) < 1e-9


@requires_ngspice
def test_post_init_skips_testbenches_without_a_wrapper(tmp_path):
    """Regression: `Spice_Base_Optimizer.__post_init__` iterates ALL testbenches but
    wrappers are built only for ENABLED ones — indexing a missing wrapper raised
    KeyError (e.g. a project with a disabled testbench). It must skip instead.

    Reproduced on the cascode example by omitting one wrapper, so the test does not
    depend on any project's `enable` flags or on a real simulation.
    """
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective
    from spicexplorer_core.spice_engine.spicelib import NGSpice_Wrapper

    p = Project_Setup.from_yaml(CASCODE_YAML)
    enabled = [tb for tb in p.testbenches if tb.enable]
    assert len(enabled) >= 2, "need at least two enabled testbenches to omit one"

    # Build wrappers for all but the last enabled testbench → it has no wrapper,
    # exactly like a disabled testbench would.
    wrappers = {}
    for tb in enabled[:-1]:
        wrappers[tb.name] = NGSpice_Wrapper(
            testbench_name=tb.name,
            netlist_filename=Path(p.ws_root) / Path(tb.netlist),
            output_folder=tmp_path / f"out_{tb.name}",
        )

    # __post_init__ runs here; previously KeyError on the omitted testbench.
    opt = Nevergrad_Spice_Single_Objective(setup_obj=p, spicelib_wrappers=wrappers)
    assert set(opt.spicelib_wrappers) == set(wrappers)


@pytest.mark.skipif(not FC_TB_NETLIST.exists(), reason="folded_cascode testbench netlist missing")
def test_apply_corner_idempotent_when_switching(tmp_path):
    p = Project_Setup.from_yaml(FC_YAML)

    w = _make_wrapper(tmp_path)
    w.apply_corner(p.pvt.get("ss_125C_1V62"))
    w.apply_corner(p.pvt.get_active())  # switch back to tt
    joined = _joined(w)

    # exactly one MOS corner line — directives are replaced, not accumulated
    assert joined.count(".lib cornerMOSlv.lib") == 1
    assert ".lib cornerMOSlv.lib mos_tt" in joined
    assert ".lib cornerMOSlv.lib mos_ss" not in joined
    # exactly one injected temp option
    assert len(re.findall(r"\.options?\s+temp\s*=", joined)) == 1


# ── apply_corner hardening ─────────────────────────────────────

@pytest.mark.skipif(not FC_TB_NETLIST.exists(), reason="folded_cascode testbench netlist missing")
def test_apply_corner_keeps_multiple_sections_of_one_lib(tmp_path):
    """Two model_includes sharing ONE lib_file (different sections) must BOTH survive — the
    per-include basename strip used to delete the sibling section just added."""
    from spicexplorer.core.domains import Corner, ModelInclude

    w = _make_wrapper(tmp_path)
    corner = Corner(
        name="multi_section",
        model_includes=[
            ModelInclude(lib_file="models.lib", section="nmos_tt"),
            ModelInclude(lib_file="models.lib", section="pmos_tt"),
        ],
        temp=27.0,
    )
    w.apply_corner(corner)
    joined = _joined(w)
    assert ".lib models.lib nmos_tt" in joined, "first section was collapsed (B11)"
    assert ".lib models.lib pmos_tt" in joined, "second section missing"


@pytest.mark.skipif(not FC_TB_NETLIST.exists(), reason="folded_cascode testbench netlist missing")
def test_apply_corner_multi_section_idempotent_on_reapply(tmp_path):
    """Re-applying the same multi-section corner replaces (not accumulates) both sections."""
    from spicexplorer.core.domains import Corner, ModelInclude

    w = _make_wrapper(tmp_path)
    corner = Corner(
        name="multi_section",
        model_includes=[ModelInclude(lib_file="models.lib", section="nmos_tt"),
                        ModelInclude(lib_file="models.lib", section="pmos_tt")],
        temp=27.0,
    )
    w.apply_corner(corner)
    w.apply_corner(corner)
    joined = _joined(w)
    assert joined.count(".lib models.lib nmos_tt") == 1
    assert joined.count(".lib models.lib pmos_tt") == 1


@pytest.mark.skipif(not FC_TB_NETLIST.exists(), reason="folded_cascode testbench netlist missing")
def test_apply_corner_warns_on_undeclared_supply(tmp_path, caplog):
    """A supply node that isn't a declared .param must produce a loud warning, not silently
    add a dangling .param and run at the netlist default supply."""
    import logging

    from spicexplorer.core.domains import Corner, SupplyOverride

    w = _make_wrapper(tmp_path)
    corner = Corner(name="bad_supply",
                    supplies=[SupplyOverride(node="NOT_A_PARAM_XYZ", value=1.2)], temp=27.0)
    with caplog.at_level(logging.WARNING, logger="spicexplorer.spice_engine.spicelib"):
        w.apply_corner(corner)
    assert any("NOT_A_PARAM_XYZ" in r.getMessage() for r in caplog.records), \
        "undeclared supply node was applied silently (B12)"


@pytest.mark.skipif(not FC_TB_NETLIST.exists(), reason="folded_cascode testbench netlist missing")
def test_apply_corner_no_warn_on_declared_supply(tmp_path, caplog):
    """A supply node that IS a declared .param (VDD) applies cleanly with no warning."""
    import logging

    from spicexplorer.core.domains import Corner, SupplyOverride

    w = _make_wrapper(tmp_path)
    corner = Corner(name="ok_supply",
                    supplies=[SupplyOverride(node="VDD", value=1.5)], temp=27.0)
    with caplog.at_level(logging.WARNING, logger="spicexplorer.spice_engine.spicelib"):
        w.apply_corner(corner)
    assert not any("VDD" in r.getMessage() and "not a declared" in r.getMessage().lower()
                   for r in caplog.records)
    assert abs(float(w.editor.get_parameter("VDD")) - 1.5) < 1e-9
