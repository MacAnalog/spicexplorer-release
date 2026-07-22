"""Parameterization P4 (meta plan_parameterization.md §5) — the full-catalog atomic sweep.

Acceptance gates:

- **Numeric parity** for EVERY migrated circuit × PDK: the post-migration ``raw/<cid>/<pdk>/
  _dut.spice`` (atomic ``.param`` header + generated tie block) resolves to exactly the same
  per-device geometry / passive / bias values as the pre-migration deck. The pre-migration
  truth is the committed snapshot ``tests/data/premigration_dut_geometry.json``, resolved from
  the ``feat/parameterization-p1-p2`` tip decks by ``tools/migrate_params.py``'s oracle
  (:func:`spicexplorer_analog_db.ppa.resolve_deck_geometry`) at migration time — so the gate
  needs no git history at test time.
- **Full adoption + generator stability**: every verifiable circuit committed an
  ``abstract/params.yaml`` that equals its own ``gen-params`` refresh (drift-free).
- The inventory's **non-MOS echo semantics** (bias sources / passives stay first-class knobs).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spicexplorer_analog_db import model, params, ppa
from spicexplorer_analog_db.export import dut_path

_SNAPSHOT = json.loads(
    (Path(__file__).parent / "data" / "premigration_dut_geometry.json").read_text()
)
_CASES = [(cid, pdk) for cid, pdks in sorted(_SNAPSHOT.items()) for pdk in sorted(pdks)]


@pytest.mark.parametrize(("cid", "pdk"), _CASES, ids=[f"{c}@{p}" for c, p in _CASES])
def test_numeric_parity_with_pre_migration_deck(cid, pdk):
    """Same devices, same fields, same resolved numbers as before the atomic migration."""
    old = _SNAPSHOT[cid][pdk]
    new = ppa.resolve_deck_geometry(dut_path(model.load_circuit(cid), pdk).read_text())
    assert set(new) == set(old), f"device set changed: {sorted(set(new) ^ set(old))}"
    for dev, fields in old.items():
        assert set(new[dev]) == set(fields), (dev, sorted(set(new[dev]) ^ set(fields)))
        for f, v in fields.items():
            assert new[dev][f] == pytest.approx(v, rel=1e-9, abs=1e-21), (dev, f)


def test_every_verifiable_circuit_adopted_params_yaml():
    missing = [
        c.id
        for c in map(model.load_circuit, model.list_circuit_ids())
        if not c.is_reference_only and not (c.dir / "abstract" / "params.yaml").is_file()
    ]
    assert missing == []


@pytest.mark.parametrize("cid", sorted(_SNAPSHOT))
def test_committed_params_yaml_is_generator_stable(cid):
    """Committed file == its own gen-params refresh: devices: regenerates byte-identically
    (echo semantics included) and the authored groups:/ratios: round-trip."""
    c = model.load_circuit(cid)
    graph = params.load_graph(c.dir / "abstract" / "topology.cgraph.json")
    committed = (c.dir / "abstract" / "params.yaml").read_text()
    doc = params.refresh_params_doc(__import__("yaml").safe_load(committed), graph)
    assert params.render_params_yaml(doc, cid) == committed


# --------------------------------------------------------------------- non-MOS echo semantics


def test_knob_symbol_extraction_forms():
    assert params.knob_symbol("x_rl") == "x_rl"
    assert params.knob_symbol("'c_comp'") == "c_comp"
    assert params.knob_symbol("dc {i_tail}") == "i_tail"
    assert params.knob_symbol("{vref_val}") == "vref_val"
    assert params.knob_symbol("'sym*8'") is None
    assert params.knob_symbol(2e-12) is None


def test_atomic_inventory_echoes_sources_and_passives():
    """MOS fields are always mechanical (D-1); V/I bias sources and passives echo the free
    knob the netlist already binds — bias-branch values stay first-class knobs."""
    graph = {
        "components": [
            {
                "id": "XM1",
                "device_type": "MOS",
                "polarity": "NMOS",
                "connections": {},
                "params": {"w": "w_pass", "l": "l_pass", "m": 1.0},
            },
            {"id": "ITAIL", "device_type": "ISOURCE", "params": {"Value": "dc {i_tail}"}},
            {"id": "R1", "device_type": "RES", "params": {"Value": "'r_top'"}},
            {"id": "C1", "device_type": "CAP", "params": {"Value": 2e-12}},
        ],
        "nets": [],
    }
    inv = params.atomic_inventory(graph)
    assert inv["XM1"] == {"w": "x_dut_xm1_w", "l": "x_dut_xm1_l", "m": "x_dut_xm1_m"}
    assert inv["ITAIL"] == {"Value": "i_tail"}
    assert inv["R1"] == {"Value": "r_top"}
    assert inv["C1"] == {"Value": 2e-12}
