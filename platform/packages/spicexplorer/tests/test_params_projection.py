"""DUT-parameterization: group/atomic knob resolution + `ungroup:` (offline, synthetic).

Covers the `spicexplorer/params@1` consumer end-to-end without SPICE/PDK/submodule:
loader roundtrip + validation, `<group>.<field>` → first-member atomic symbol, unknown
group/field errors, `ungroup:` by name / by kind / by ratio producing the tie-shadowing
`.param` set, and — critically — that a project WITHOUT `params_file:`/`ungroup:` loads
exactly as before (everything here is synthetic fixtures against the schema contract).
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from spicexplorer.backends.params import (
    CircuitParams,
    ParamsError,
    load_params_file,
    netlist_param_defaults,
    resolve_knob,
    select_ungroup,
    shadow_params,
)
from spicexplorer.core.domains import Project_Setup

# --------------------------------------------------------------------------- fixtures

# Synthetic 5T-ish contract: matched input/load pairs, a mirror-L group, and two
# ratios (one whose base is a symbol, one whose base is a frozen literal).
_PARAMS_YAML = """
schema: spicexplorer/params@1
devices:
  XM1: {w: x_dut_xm1_w, l: x_dut_xm1_l, m: x_dut_xm1_m}
  XM2: {w: x_dut_xm2_w, l: x_dut_xm2_l, m: x_dut_xm2_m}
  XM3: {w: x_dut_xm3_w, l: x_dut_xm3_l, m: x_dut_xm3_m}
  XM4: {w: x_dut_xm4_w, l: x_dut_xm4_l, m: x_dut_xm4_m}
  XM5: {w: x_dut_xm5_w, l: x_dut_xm5_l, m: x_dut_xm5_m}
  XM6: {w: x_dut_xm6_w, l: x_dut_xm6_l, m: 2}
groups:
  - {name: input_pair,   kind: matched_pair,  members: [XM1, XM2], tie: [w, l, m]}
  - {name: load_pair,    kind: matched_pair,  members: [XM3, XM4], tie: [w, l]}
  - {name: nmos_mirror_l, kind: mirror_length, members: [XM6, XM5], tie: [l]}
ratios:
  - {param: m, ref: XM5, of: XM6, ratio: "17/3"}   # base m is the frozen literal 2
  - {param: m, ref: XM4, of: XM3, ratio: 2}        # base m is a symbol
"""

# The lowered deck header: atomic defaults on first members, tie lines on the rest.
_DECK = """\
* synthetic lowered deck (lowered header shape)
.param x_dut_xm1_w=0.5u
.param x_dut_xm1_l=5u
.param x_dut_xm1_m=1
.param x_dut_xm2_w={x_dut_xm1_w}
.param x_dut_xm2_l={x_dut_xm1_l}
.param x_dut_xm2_m={x_dut_xm1_m}
.param x_dut_xm3_w=1.5u x_dut_xm3_l=5u
.param x_dut_xm3_m=3
.param x_dut_xm4_w={x_dut_xm3_w}
.param x_dut_xm4_l={x_dut_xm3_l}
.param x_dut_xm4_m={x_dut_xm3_m}
.param x_dut_xm6_w=2u
.param x_dut_xm6_l=1u
.param x_dut_xm5_w=2u
.param x_dut_xm5_l={x_dut_xm6_l}
.param x_dut_xm5_m=11
.end
"""


@pytest.fixture()
def contract(tmp_path: Path) -> CircuitParams:
    f = tmp_path / "params.yaml"
    f.write_text(_PARAMS_YAML)
    return load_params_file(f)


def _write_circuit(tmp_path: Path) -> Path:
    """A synthetic circuit dir: deck + params.yaml side by side (ws_root = tmp_path)."""
    (tmp_path / "dut.spice").write_text(_DECK)
    (tmp_path / "params.yaml").write_text(_PARAMS_YAML)
    return tmp_path


def _project_yaml(extra: str = "") -> str:
    return textwrap.dedent(f"""
    project:
      name: p3-synthetic
      description: P3 projection fixture
      simulator: ngspice
      ws_root: .
      netlist: dut.spice
      outdir: out
      tech_spec: {{name: synthetic, constraints: {{}}}}
      {extra}
      dut_params:
        - {{name: input_pair.w, min_val: 0.3u, max_val: 4u}}
        - {{name: x_dut_xm3_l,  min_val: 1u,   max_val: 8u}}
        - {{name: i_tail,       min_val: 1u,   max_val: 50u}}
      testbenches:
        - {{name: tb_ac, params: [], netlist: dut.spice}}
      optimizer_config:
        name: SamplingSearch
        type: nevergrad
        budget: 2
        target_specs:
          - {{name: dcgain, testbench: tb_ac, sim_type: ac, goal: exceed, target: 40, range: 40}}
    """)


def _load(tmp_path: Path, extra: str = "") -> Project_Setup:
    _write_circuit(tmp_path)
    y = tmp_path / "project_setup.yaml"
    y.write_text(_project_yaml(extra))
    return Project_Setup.from_yaml(y)


# --------------------------------------------------------------------------- loader


def test_loader_roundtrip(contract: CircuitParams):
    assert set(contract.devices) == {"XM1", "XM2", "XM3", "XM4", "XM5", "XM6"}
    assert contract.devices["XM1"]["w"] == "x_dut_xm1_w"
    assert contract.devices["XM6"]["m"] == 2  # frozen literal survives as a number
    assert [g.name for g in contract.groups] == ["input_pair", "load_pair", "nmos_mirror_l"]
    g = contract.group("input_pair")
    assert g.kind == "matched_pair" and g.members == ("XM1", "XM2") and g.tie == ("w", "l", "m")
    assert contract.groups_of_kind("matched_pair") == contract.groups[:2]
    assert contract.ratios[0].value() == pytest.approx(17 / 3)
    assert contract.ratios[1].value() == 2.0


def test_loader_absent_returns_none(tmp_path: Path):
    from spicexplorer.backends.analog_db import load_circuit_params

    # synthetic analog-db layout WITHOUT abstract/params.yaml → None, never a raise
    (tmp_path / "circuits/amp_x/abstract").mkdir(parents=True)
    assert load_circuit_params("amp_x", root=tmp_path) is None
    # …and WITH it → a parsed contract
    (tmp_path / "circuits/amp_x/abstract/params.yaml").write_text(_PARAMS_YAML)
    cp = load_circuit_params("amp_x", root=tmp_path)
    assert cp is not None and cp.group("input_pair").members[0] == "XM1"


def test_loader_wrong_schema(tmp_path: Path):
    f = tmp_path / "params.yaml"
    f.write_text(_PARAMS_YAML.replace("spicexplorer/params@1", "spicexplorer/params@9"))
    with pytest.raises(ParamsError, match="schema"):
        load_params_file(f)


def test_loader_validation_errors(tmp_path: Path):
    f = tmp_path / "params.yaml"
    # a group member missing from devices:
    f.write_text(_PARAMS_YAML.replace("members: [XM1, XM2]", "members: [XM1, XM9]"))
    with pytest.raises(ParamsError, match="XM9"):
        load_params_file(f)
    # a tie field a member doesn't carry
    f.write_text(_PARAMS_YAML.replace("tie: [w, l]}", "tie: [w, zz]}"))
    with pytest.raises(ParamsError, match="zz"):
        load_params_file(f)
    # a ratio instance missing from devices:
    f.write_text(_PARAMS_YAML.replace("ref: XM5", "ref: XM9"))
    with pytest.raises(ParamsError, match="XM9"):
        load_params_file(f)
    # an unparsable ratio fraction
    f.write_text(_PARAMS_YAML.replace('"17/3"', '"17//3"'))
    with pytest.raises(ParamsError, match="ratio"):
        load_params_file(f)
    # missing file
    with pytest.raises(ParamsError, match="not found"):
        load_params_file(tmp_path / "nope.yaml")


# --------------------------------------------------------------------------- resolve_knob


def test_resolve_group_field_to_first_member(contract: CircuitParams):
    assert resolve_knob(contract, "input_pair.w") == "x_dut_xm1_w"
    assert resolve_knob(contract, "input_pair.m") == "x_dut_xm1_m"
    assert resolve_knob(contract, "load_pair.l") == "x_dut_xm3_l"
    # member ORDER matters: nmos_mirror_l lists XM6 first
    assert resolve_knob(contract, "nmos_mirror_l.l") == "x_dut_xm6_l"


def test_resolve_atomic_and_free_symbols_pass_through(contract: CircuitParams):
    assert resolve_knob(contract, "x_dut_xm2_w") == "x_dut_xm2_w"
    assert resolve_knob(contract, "i_tail") == "i_tail"  # free bias knob, not in the inventory


def test_resolve_bare_group_name(contract: CircuitParams):
    # single tied field → unambiguous → first member's symbol
    assert resolve_knob(contract, "nmos_mirror_l") == "x_dut_xm6_l"
    # multi-field group → ambiguous, must name the field
    with pytest.raises(ParamsError, match="ambiguous"):
        resolve_knob(contract, "input_pair")


def test_resolve_errors(contract: CircuitParams):
    with pytest.raises(ParamsError, match="unknown group"):
        resolve_knob(contract, "no_such_group.w")
    with pytest.raises(ParamsError, match="not tied"):
        resolve_knob(contract, "load_pair.m")  # load_pair ties only [w, l]


# --------------------------------------------------------------------------- ungroup


def test_shadow_by_group_name(contract: CircuitParams, tmp_path: Path):
    deck = tmp_path / "dut.spice"
    deck.write_text(_DECK)
    defaults = netlist_param_defaults(deck)
    shadows = shadow_params(contract, ["input_pair"], defaults)
    # every NON-FIRST member-field gets the tie target's current default
    assert shadows == {
        "x_dut_xm2_w": "0.5u",
        "x_dut_xm2_l": "5u",
        "x_dut_xm2_m": "1",
    }


def test_shadow_by_kind(contract: CircuitParams, tmp_path: Path):
    deck = tmp_path / "dut.spice"
    deck.write_text(_DECK)
    shadows = shadow_params(contract, ["kind:matched_pair"], netlist_param_defaults(deck))
    assert set(shadows) == {
        "x_dut_xm2_w", "x_dut_xm2_l", "x_dut_xm2_m",  # input_pair
        "x_dut_xm4_w", "x_dut_xm4_l",                 # load_pair (ties w, l only)
    }
    assert shadows["x_dut_xm4_w"] == "1.5u"


def test_shadow_ratio(contract: CircuitParams, tmp_path: Path):
    deck = tmp_path / "dut.spice"
    deck.write_text(_DECK)
    defaults = netlist_param_defaults(deck)
    # base m is the frozen literal 2 → 2 × 17/3
    shadows = shadow_params(contract, ["ratio:XM5"], defaults)
    assert shadows["x_dut_xm5_m"] == pytest.approx(2 * 17 / 3)
    # base m is a symbol → deck default 3 × 2 = 6 (integral → clean int-valued float)
    shadows = shadow_params(contract, ["ratio:XM4"], defaults)
    assert shadows["x_dut_xm4_m"] == 6.0


def test_ungroup_selector_errors(contract: CircuitParams):
    with pytest.raises(ParamsError, match="unknown group"):
        select_ungroup(contract, ["no_such_group"])
    with pytest.raises(ParamsError, match="matches no group"):
        select_ungroup(contract, ["kind:bias_chain"])
    with pytest.raises(ParamsError, match="matches no ratios"):
        select_ungroup(contract, ["ratio:XM1"])


def test_shadow_missing_default_errors(contract: CircuitParams):
    with pytest.raises(ParamsError, match="no current default"):
        shadow_params(contract, ["input_pair"], {})


def test_shadow_expression_default_errors(contract: CircuitParams):
    # a tie target whose deck default is itself an expression → loud, never propagated
    with pytest.raises(ParamsError, match="expression"):
        shadow_params(
            contract, ["input_pair"],
            {"x_dut_xm1_w": "{x_dut_xm3_w}", "x_dut_xm1_l": "5u", "x_dut_xm1_m": "1"},
        )


# ----------------------------------------------------------------- deck-header reader


def test_netlist_param_defaults(tmp_path: Path):
    deck = tmp_path / "dut.spice"
    deck.write_text(_DECK)
    d = netlist_param_defaults(deck)
    assert d["x_dut_xm1_w"] == "0.5u"
    assert d["x_dut_xm2_w"] == "{x_dut_xm1_w}"  # tie lines survive as expressions
    assert d["x_dut_xm3_w"] == "1.5u" and d["x_dut_xm3_l"] == "5u"  # two per card
    # .include following (relative) + continuation lines
    (tmp_path / "inc.spice").write_text(".param a=1\n+ b=2u\n")
    top = tmp_path / "top.spice"
    top.write_text("* t\n.include inc.spice\n.param c=3\n")
    d = netlist_param_defaults(top)
    assert d == {"a": "1", "b": "2u", "c": "3"}


# ------------------------------------------------------------- projection (from_yaml)


def test_from_yaml_group_resolution(tmp_path: Path):
    proj = _load(tmp_path, "params_file: params.yaml")
    names = [p.name for p in proj.dut_params]
    # input_pair.w resolved to the first member's atomic symbol; the rest untouched
    assert names == ["x_dut_xm1_w", "x_dut_xm3_l", "i_tail"]
    assert all(not p.freeze for p in proj.dut_params)


def test_from_yaml_ungroup_appends_frozen_shadows(tmp_path: Path):
    proj = _load(
        tmp_path,
        "params_file: params.yaml\n      ungroup: [nmos_mirror_l, 'ratio:XM5']",
    )
    by_name = {p.name: p for p in proj.dut_params}
    # the non-first mirror member's L is now an explicit frozen .param at its default (1u)
    shadow = by_name["x_dut_xm5_l"]
    assert shadow.freeze is True
    assert shadow.get_val() == pytest.approx(1e-6)  # "1u" resolved by the load machinery
    # the dissolved ratio froze the derived m at its computed default
    assert by_name["x_dut_xm5_m"].get_val() == pytest.approx(2 * 17 / 3)
    # free knobs unchanged and still free
    assert not by_name["x_dut_xm1_w"].freeze and not by_name["i_tail"].freeze


def test_from_yaml_ungroup_skips_user_listed_symbols(tmp_path: Path):
    # the user promotes the shadowed symbol to a knob of their own → no frozen duplicate
    _write_circuit(tmp_path)
    y = tmp_path / "project_setup.yaml"
    body = _project_yaml(
        "params_file: params.yaml\n      ungroup: [nmos_mirror_l]"
    ).replace(
        "- {name: i_tail,       min_val: 1u,   max_val: 50u}",
        "- {name: x_dut_xm5_l,  min_val: 0.5u, max_val: 6u}",
    )
    y.write_text(body)
    proj = Project_Setup.from_yaml(y)
    xm5 = [p for p in proj.dut_params if p.name == "x_dut_xm5_l"]
    assert len(xm5) == 1 and xm5[0].freeze is False  # stays a FREE search dimension


def test_from_yaml_duplicate_after_resolution_raises(tmp_path: Path):
    _write_circuit(tmp_path)
    y = tmp_path / "project_setup.yaml"
    body = _project_yaml("params_file: params.yaml").replace(
        "- {name: i_tail,       min_val: 1u,   max_val: 50u}",
        "- {name: x_dut_xm1_w,  min_val: 1u,   max_val: 50u}",  # == input_pair.w resolved
    )
    y.write_text(body)
    with pytest.raises(ValueError, match="duplicate atomic symbol"):
        Project_Setup.from_yaml(y)


def test_from_yaml_ungroup_without_params_file_raises(tmp_path: Path):
    _write_circuit(tmp_path)
    y = tmp_path / "project_setup.yaml"
    y.write_text(_project_yaml("ungroup: [nmos_mirror_l]"))
    with pytest.raises(ValueError, match="requires `params_file:`"):
        Project_Setup.from_yaml(y)


def test_from_yaml_absent_params_is_todays_behavior(tmp_path: Path):
    """No params_file/ungroup keys → the load is exactly today's (group syntax untouched,
    no shadows appended, dut_params list identical to a control load)."""
    _write_circuit(tmp_path)
    y = tmp_path / "project_setup.yaml"
    # control uses only plain atomic names (a legacy project)
    body = _project_yaml().replace("input_pair.w", "x_dut_xm1_w")
    y.write_text(body)
    proj = Project_Setup.from_yaml(y)
    assert proj.params_file is None and proj.ungroup is None
    assert [p.name for p in proj.dut_params] == ["x_dut_xm1_w", "x_dut_xm3_l", "i_tail"]
    assert all(not p.freeze for p in proj.dut_params)
    # and byte-equality of the search-space definition against a params_file-carrying twin
    y2 = tmp_path / "project_setup2.yaml"
    y2.write_text(_project_yaml("params_file: params.yaml").replace("input_pair.w", "x_dut_xm1_w"))
    proj2 = Project_Setup.from_yaml(y2)
    assert [(p.name, p.min_val, p.max_val, p.freeze) for p in proj.dut_params] == [
        (p.name, p.min_val, p.max_val, p.freeze) for p in proj2.dut_params
    ]
