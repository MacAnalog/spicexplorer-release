"""kind: reference circuits (plan D-9): the schema/harness contract + the ferrosim importer.

Reference circuits are imported foreign/proprietary decks registered in ``circuits/`` but never
lowered or simulated: a reference-only Tier-0 (schema + provenance + deck-exists) and T1-T4 skipped.
All PDK-free.
"""

from __future__ import annotations

from pathlib import Path

from spicexplorer_analog_db import catalog, generate, model, schema, verify
from spicexplorer_analog_db.importers import ferrosim


def _reference_ids() -> list[str]:
    return [c.id for c in model.load_all_circuits() if c.is_reference_only]


def test_reference_circuits_present_and_wellformed():
    ids = _reference_ids()
    assert ids, "expected imported kind: reference circuits (e.g. ferrosim_*)"
    for cid in ids:
        c = model.load_circuit(cid)
        assert c.kind == "reference"
        assert c.status == "reference"
        assert not c.pdks, f"{cid}: a reference circuit must not carry open-PDK bindings"
        # schema-valid manifest
        assert not schema.validation_errors(c.manifest, "circuit"), cid
        # mandatory provenance
        prov = c.manifest.get("provenance") or {}
        assert prov.get("source") and prov.get("license"), f"{cid}: missing provenance source/license"
        # every declared binding is either an upstream pointer or an on-disk deck dir
        assert c.references, f"{cid}: no reference bindings"
        for entry in c.references:
            if entry.get("upstream"):
                assert entry["upstream"].startswith("http"), f"{cid}: binding {entry} has a malformed upstream URL"
                continue
            bdir = c.reference_dir(entry)
            assert bdir.is_dir(), f"{cid}: binding {entry} missing"
            assert next(bdir.rglob("*.scs"), None) is not None, f"{cid}: binding {entry} has no decks"


def test_reference_tier0_passes_and_higher_tiers_skip():
    cid = _reference_ids()[0]
    results = verify.run([0, 1, 2], circuit_ids=[cid])
    rows = [r for r in results if r.circuit == cid]
    assert rows, cid
    assert not [r for r in rows if r.status == "fail"], [r for r in rows if r.status == "fail"]
    t0 = [r for r in rows if r.tier == 0]
    # tier-0 is environment-free except ref:parse, which skips on a pre-dialect
    # spicexplorer-core (it self-activates once the platform dialect feature is present)
    assert t0 and all(
        r.status == "pass" or (r.check.startswith("ref:parse") and r.status == "skip")
        for r in t0
    )
    for tier in (1, 2):
        tier_rows = [r for r in rows if r.tier == tier]
        assert tier_rows and all(r.status == "skip" for r in tier_rows)
    assert verify.derive_status(cid, results) == "reference"


def test_generate_skips_reference_circuits():
    cid = _reference_ids()[0]
    assert generate.write_generated(model.load_circuit(cid)) == []


def test_catalog_indexes_reference_bindings():
    cat = catalog.build_catalog()
    entry = next(c for c in cat["circuits"] if c["id"] in _reference_ids())
    assert entry["kind"] == "reference"
    assert entry["pdks"] == []
    assert entry.get("references"), "reference bindings must be indexed in the catalog"
    for b in entry["references"]:
        decks = [p for role in ("dut", "tb", "runs", "other") for p in b.get(role, [])]
        assert b.get("upstream") or decks, f"binding {b} indexes neither an upstream pointer nor a deck"
    assert any(b.get("upstream") for b in entry["references"]), "expected at least one upstream pointer binding"


def _make_fake_ferrosim(root: Path) -> Path:
    """A minimal ferrosim tests/ tree exercising each importer path (family / ported / files)."""
    tests = root / "tests"
    (tests / "decks/amp5t/netlist/dut").mkdir(parents=True)
    (tests / "decks/amp5t/netlist/dut/amp.scs").write_text("subckt amp a b\nends amp\n")
    (tests / "decks/amp5t/netlist/tb").mkdir(parents=True)
    (tests / "decks/amp5t/netlist/tb/tb.scs").write_text("// tb\n")
    (tests / "decks/ported").mkdir(parents=True)
    (tests / "decks/ported/two_stage_opamp_28.scs").write_text("// 28\n")
    (tests / "decks/ported/two_stage_opamp_65.scs").write_text("// 65\n")
    (tests / "va_demo").mkdir(parents=True)
    (tests / "va_demo/tb_tee.scs").write_text("// va\n")
    return tests


def test_import_ferrosim_authors_valid_manifests_and_is_idempotent(tmp_path):
    src = _make_fake_ferrosim(tmp_path)
    dest = tmp_path / "circuits"
    dest.mkdir()

    present = {"ferrosim_amp5t", "ferrosim_two_stage_opamp", "ferrosim_va_demo"}
    imported, _ = ferrosim.import_all(src, dest)
    # only the families present in the fake source are imported (others skip: source missing)
    assert set(imported) == present

    import yaml

    # ported circuit binds both nodes; manifests validate against the circuit schema
    two_stage = yaml.safe_load((dest / "ferrosim_two_stage_opamp/circuit.yaml").read_text())
    assert {b["node"] for b in two_stage["references"]} == {"28nm", "65nm"}
    for cy in dest.glob("*/circuit.yaml"):
        assert not schema.validation_errors(yaml.safe_load(cy.read_text()), "circuit"), cy

    # verbatim layout preserved (family subtree kept intact)
    assert (dest / "ferrosim_amp5t/spectre/28nm/netlist/dut/amp.scs").is_file()

    # idempotent: a second import clobbers nothing and imports nothing new; the present families
    # are now skipped as "(exists)".
    imported2, skipped2 = ferrosim.import_all(src, dest)
    assert imported2 == []
    exists = {s.split()[0] for s in skipped2 if s.endswith("(exists)")}
    assert exists == present
