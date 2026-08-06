"""Scoreboard entries: identity, upsert, baselines, migration."""

from __future__ import annotations

import json
import shutil

import pytest

from spicexplorer_analog_db import model, schema, scoreboard


def test_design_id_is_formatting_proof():
    a = scoreboard.design_id("x", "sky130", {"w": "0.5u"})
    b = scoreboard.design_id("x", "sky130", {"w": 5e-7})
    c = scoreboard.design_id("x", "sky130", {"w": "0.51u"})
    assert a == b != c
    assert scoreboard.design_id("x", "sky130", {"w": "0.5u"}) != scoreboard.design_id(
        "y", "sky130", {"w": "0.5u"}
    )


@pytest.fixture()
def tmp_circuit(tmp_path):
    src = model.load_circuit("ldo_007_pmos")
    dst = tmp_path / src.id
    shutil.copytree(src.dir, dst)
    shutil.rmtree(dst / "scoreboard", ignore_errors=True)
    return model.Circuit(id=src.id, dir=dst, manifest=src.manifest)


def _results(pdk: str, corner: str, i_q: float) -> dict:
    return {
        "schema": "spicexplorer/results@1",
        "circuit": "ldo_007_pmos",
        "pdk": pdk,
        "corner": corner,
        "analyses": {
            "dc_op": {"status": "ok", "measures": {"vout_dc": 1.2, "i_supply": i_q}},
        },
        "provenance": {"run_at": "2026-07-03T00:00:00+00:00", "ngspice": "45", "generator": "test"},
    }


def test_record_upserts_corners_into_one_design_point(tmp_circuit):
    p1 = scoreboard.record(tmp_circuit, _results("sky130", "tt", 2.0e-4))
    p2 = scoreboard.record(tmp_circuit, _results("sky130", "ss", 2.4e-4))
    assert p1 == p2  # same sizing -> same design point -> same entry file
    entry = json.loads(p1.read_text())
    assert sorted(entry["corners"]) == ["ss", "tt"]
    assert entry["ppa"]["corners_run"] == ["ss", "tt"]
    assert entry["ppa"]["power_w"] == pytest.approx(2.4e-4 * 1.8)  # worst corner
    assert entry["metrics"]["tt"]["i_q"]["spec"] == "pass"
    assert not schema.validation_errors(entry, "scoreboard-entry")


def test_first_record_auto_names_the_baseline(tmp_circuit):
    scoreboard.record(tmp_circuit, _results("sky130", "tt", 2.0e-4))
    base = scoreboard.baselines(tmp_circuit)
    assert set(base) == {"sky130"}
    assert scoreboard.entry_path(tmp_circuit, "sky130", base["sky130"]).is_file()


def test_sizing_override_records_a_foreign_design_point(tmp_circuit):
    scoreboard.record(tmp_circuit, _results("sky130", "tt", 2.0e-4))
    scoreboard.record(
        tmp_circuit, _results("sky130", "tt", 1.5e-4), sizing_override={"w_pass": 123e-6}
    )
    entries = scoreboard.load_entries(tmp_circuit, "sky130")
    assert len(entries) == 2  # a second design point, not an overwrite
    assert len(scoreboard.baselines(tmp_circuit)) == 1  # baseline stays with the first


def test_set_baseline_requires_an_existing_entry(tmp_circuit):
    with pytest.raises(FileNotFoundError):
        scoreboard.set_baseline(tmp_circuit, "sky130", "0000000000")


def test_migrated_db_state():
    """Every verifiable circuit carries the absorbed results/ as schema-valid entries, and every
    baseline pointer resolves."""
    for cid in model.list_circuit_ids():
        c = model.load_circuit(cid)
        if c.is_reference_only:
            continue
        assert not (c.dir / "results").exists(), f"{cid}: legacy results/ still present"
        entries = scoreboard.load_entries(c)
        if not entries and not (c.dir / "scoreboard" / "baselines.yaml").is_file():
            continue  # landed post-migration (2026-07-16 drawn fleet): no recorded points yet
        assert entries, f"{cid}: no scoreboard entries"
        for e in entries:
            assert not schema.validation_errors(e, "scoreboard-entry"), (cid, e["design_id"])
        base = scoreboard.baselines(c)
        assert base, f"{cid}: no baselines.yaml"
        for pdk, did in base.items():
            assert scoreboard.entry_path(c, pdk, did).is_file(), (cid, pdk, did)


def test_pareto_front_is_direction_aware():
    def entry(did, power, gain):
        return {
            "design_id": did,
            "ppa": {"power_w": power, "active_gate_area_um2": 10.0,
                    "performance": {"dc_gain_db": gain, "ugf_hz": 1e6, "pm_deg": 60.0}},
        }

    a = entry("a" * 10, 1e-4, 60.0)   # more power, more gain
    b = entry("b" * 10, 5e-5, 40.0)   # less power, less gain
    c = entry("c" * 10, 2e-4, 30.0)   # dominated by both
    front = scoreboard.pareto_front([a, b, c], "amplifier")
    assert front == {"a" * 10, "b" * 10}


def test_pareto_missing_axis_never_dominates():
    full = {"design_id": "f" * 10,
            "ppa": {"power_w": 1e-4, "active_gate_area_um2": 10.0,
                    "performance": {"dc_gain_db": 60.0, "ugf_hz": 1e6, "pm_deg": 60.0}}}
    sparse = {"design_id": "s" * 10, "ppa": {"performance": {}, "corners_run": []}}
    assert scoreboard.pareto_front([full, sparse], "amplifier") == {"f" * 10}


def test_committed_index_matches_fresh_build():
    committed = scoreboard.index_path().read_text()
    assert committed == scoreboard.index_json()
    doc = json.loads(committed)
    assert doc["schema"] == "spicexplorer/scoreboard@1"
    # The telescopic's ihp design points span several axes, so more than one sits on the
    # Pareto front — nothing is ranked scalar-best. Deliberately NOT pinned to a
    # fixed row count: every new design point recorded for this circuit used to break this
    # assertion, which says nothing about the invariant being tested.
    rows = doc["classes"]["amplifier"]["ihp-sg13g2"]["amp_018_telescopic_cascode"]["entries"]
    assert len(rows) >= 2
    assert any(r["pareto"] for r in rows)
    assert sum(r["baseline"] for r in rows) == 1


def test_catalog_carries_baseline_ppa():
    cat = json.loads((model.load_circuit("amp_001_5t").dir.parent.parent / "catalog.json").read_text())
    entry = next(c for c in cat["circuits"] if c["id"] == "amp_001_5t")
    sky = entry["scoreboard"]["sky130"]
    assert sky["ppa"]["power_w"] > 0 and sky["ppa"]["active_gate_area_um2"] > 0
    assert set(sky["spec"]) == {"pass", "fail", "none"}


def test_migration_preserved_the_symbolic_crosscheck():
    """The telescopic's migrated ihp entry carried a netlist2tf sym-vs-sim report — it
    must survive AS A RECORDED ENTRY. It need not stay the *baseline*: since the
    2026-08 sizing campaign, baselines track the best current design point, and the
    migrated entry keeps its historical design_id beside it."""
    c = model.load_circuit("amp_018_telescopic_cascode")
    entries = scoreboard.load_entries(c, "ihp-sg13g2")
    assert any("dc_gain_db" in ((e["corners"]["tt"].get("symbolic_crosscheck") or {})
                                .get("metrics") or {})
               for e in entries), "migrated symbolic_crosscheck entry lost"
