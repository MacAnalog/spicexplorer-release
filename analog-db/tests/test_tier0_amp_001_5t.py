"""Phase-0 exit gate (plan todo_examples_db.md P0 Exit).

Proves the schema end-to-end on the `amp_001_5t` proof circuit:
  - Tier 0 (schema + cross-ref + catalog determinism) is fully green.
  - circuitgraph round-trips the abstract netlist.
  - netlist2tf ingests the abstract netlist.
  - project_setup.yaml `extends: circuit.yaml` resolves.
  - the committed generated artifacts (cgraph.json, lowered netlist) are up to date.
"""

from __future__ import annotations

import json

import pytest

from spicexplorer_analog_db import catalog, generate, model, paths, verify
from spicexplorer_analog_db.extends import resolve_extends

CIRCUIT = "amp_001_5t"


@pytest.fixture(scope="module")
def circuit() -> model.Circuit:
    return model.load_circuit(CIRCUIT)


def test_db_present_and_circuit_registered():
    assert paths.db_present()
    assert CIRCUIT in model.list_circuit_ids()


def test_tier0_is_fully_green():
    results = verify.run_tier0()
    failures = [r for r in results if r.status == "fail"]
    assert not failures, "Tier 0 failures:\n" + "\n".join(f"{r.circuit} {r.check}: {r.reason}" for r in failures)
    # at least the amp_001_5t checks ran
    assert any(r.circuit == CIRCUIT and r.status == "pass" for r in results)


def test_derived_status_is_generated():
    results = verify.run_tier0()
    assert verify.derive_status(CIRCUIT, results) == "generated"


def test_catalog_determinism_and_membership():
    committed = paths.catalog_path()
    assert committed.is_file(), "catalog.json not committed — run `analog-db catalog --write`"
    assert committed.read_text() == catalog.catalog_json()
    cat = json.loads(committed.read_text())
    assert CIRCUIT in cat["classes"]["amplifier"]
    assert any(c["id"] == CIRCUIT and c["class"] == "amplifier" for c in cat["circuits"])


def test_circuitgraph_roundtrips_abstract(circuit):
    from spicexplorer_circuitgraph import CircuitGraph, CircuitGraphDoc
    from spicexplorer_core.spice_engine import NetlistView

    nl = circuit.dir / "abstract" / "netlist.spice"
    g = CircuitGraph.from_netlist(NetlistView.from_file(str(nl)), name=CIRCUIT)
    assert g.component_count == 6  # the 5T core: input pair + mirror load + tail + mirror ref
    doc = CircuitGraphDoc.from_graph(g)
    rebuilt = CircuitGraphDoc.model_validate_json(doc.model_dump_json()).to_graph()
    assert CircuitGraphDoc.from_graph(rebuilt).model_dump() == doc.model_dump()


def test_generated_artifacts_are_up_to_date(circuit):
    """Pre-seeds the Tier 1 drift guard (lands fully in Phase 1)."""
    cg = circuit.dir / "abstract" / "topology.cgraph.json"
    assert cg.read_text() == generate.cgraph_json(circuit)
    for pdk in circuit.pdks:
        lowered = circuit.dir / "pdk" / pdk / "netlist.spice"
        assert lowered.read_text() == generate.lowered_netlist(circuit, pdk)


def test_lowered_netlist_retargets_to_pdk(circuit):
    lowered = (circuit.dir / "pdk" / "ihp-sg13g2" / "netlist.spice").read_text()
    assert "sg13_lv_nmos" in lowered and "sg13_lv_pmos" in lowered
    assert "nmos\n" not in lowered  # generic tokens fully retargeted


def test_extends_resolves(circuit):
    # the THIN projection extends circuit.yaml (the GENERATED project_setup.yaml is the full view)
    resolved = resolve_extends(circuit.dir / "optimizer" / "projection.yaml")
    r = resolved["_resolved"]
    assert r["knobs_from"] == "pdk/{pdk}/sizing.yaml"
    assert r["targets_from"] == "datasheet.yaml"
    assert r["circuit"]["id"] == CIRCUIT


def test_generated_project_setup_parses_as_optimizer_config(circuit):
    """The GENERATED project_setup.yaml is a real, loadable Project_Setup (plan D-3)."""
    Project_Setup = pytest.importorskip("spicexplorer.core.domains").Project_Setup
    proj = Project_Setup.from_yaml(str(circuit.dir / "project_setup.yaml"))
    assert proj.dut_params and proj.optimizer_config.target_specs.targets


def test_netlist2tf_ingests_abstract(circuit):
    n2tf = pytest.importorskip("spicexplorer_netlist2tf")
    ir = n2tf.from_file(str(circuit.dir / "abstract" / "netlist.spice"), name=CIRCUIT)
    assert len(ir.devices) == 6
