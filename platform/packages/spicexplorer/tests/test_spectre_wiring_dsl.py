"""YAML DSL round-trip for the Spectre + OCEAN wiring — aligned with the ngspice shape.

A Spectre testbench is a native `.scs` file via `netlist:` (exactly like an ngspice
`.spice`); the only new field is each target's `measurement:` OCEAN recipe. `from_yaml`
must carry the recipe through and validate a malformed one loudly at load (the
`TargetSpec(**item)` hook bypasses dacite, so validation lives in `__post_init__`); an
existing ngspice project (no `measurement:`) is unaffected.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from spicexplorer.core.domains import Project_Setup, TargetSpec
from spicexplorer.optimization.ocean_integration import build_recipes

_YAML = """
project:
  name: native-spectre-demo
  description: native Spectre testbench (a .scs file) with OCEAN measurements
  simulator: spectre
  ws_root: .
  netlist: dut.scs
  outdir: out
  sim_engine: spectre
  tech_spec: {name: generic-n65, constraints: {}}
  dut_params:
    - {name: w0, min_val: 1e-7, max_val: 1e-5}
  testbenches:
    - name: tb_ac
      netlist: spice/ota_tb_ac.scs      # <-- native Spectre deck, like an ngspice .spice
      params: []
    - name: tb_op
      netlist: spice/ota_tb_op.scs
      params: []
  optimizer_config:
    name: SamplingSearch
    type: nevergrad
    budget: 2
    target_specs:
      - name: ugf
        testbench: tb_ac
        sim_type: ac
        goal: exceed
        target: 2e6
        range: 1e6
        measurement: {result: ac, expr: 'gainBwProd(v("v_out"))'}
      - name: m1_gm
        testbench: tb_op
        sim_type: op
        goal: exceed
        target: 1e-3
        range: 1e-3
        measurement: {builder: device_op_param, instance: XM1, param: gm}
"""


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "project_setup.yaml"
    p.write_text(textwrap.dedent(body))
    return p


def test_yaml_round_trips_netlist_testbench_and_measurements(tmp_path):
    proj = Project_Setup.from_yaml(_write(tmp_path, _YAML))
    assert proj.sim_engine == "spectre"
    # the testbench is defined by its netlist file, exactly like ngspice
    tb = {t.name: t for t in proj.testbenches}
    assert tb["tb_ac"].netlist == "spice/ota_tb_ac.scs"
    assert tb["tb_op"].netlist == "spice/ota_tb_op.scs"

    specs = {t.name: t for t in proj.optimizer_config.target_specs.targets}
    assert specs["ugf"].measurement == {"result": "ac", "expr": 'gainBwProd(v("v_out"))'}
    assert specs["m1_gm"].measurement == {
        "builder": "device_op_param", "instance": "XM1", "param": "gm",
    }
    recipes = build_recipes(proj.optimizer_config.target_specs)
    assert {tb: [m.name for m in ms] for tb, ms in recipes.items()} == {
        "tb_ac": ["ugf"], "tb_op": ["m1_gm"],
    }


def test_malformed_measurement_is_rejected_at_load(tmp_path):
    bad = _YAML.replace(
        '{result: ac, expr: \'gainBwProd(v("v_out"))\'}', "{result: ac}"
    )  # expr missing → invalid raw recipe
    with pytest.raises(ValueError, match="measurement"):
        Project_Setup.from_yaml(_write(tmp_path, bad))


def test_measurement_is_optional_and_ngspice_projects_are_unaffected():
    t = TargetSpec(name="gain", testbench="tb", target=30, goal="exceed",
                   sim_type="ac", range=10)
    assert t.measurement is None and not t.has_ocean_measurement()
