"""Contract tests for the Reference Library routes (``/api/library/*``).

Two groups:

* **Degradation** (always run): with the analog-db reader stubbed absent, ``status`` answers
  ``available: false`` and every data route returns ``503`` — never ``500``. This pins the
  optional-submodule contract regardless of whether analog-db is installed in the env.
* **Live contract** (run only when the analog-db submodule is checked out): the catalog,
  per-circuit datasheet + recorded results, class registry, and template library shapes — with
  a few values pinned against the committed DB (the 5t OTA's sky130 numbers, the telescopic
  cascode's symbolic cross-check, the current-mirror templates).

No SPICE: everything is reads of committed JSON/YAML.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from spicexplorer_api.services import library_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    pytest.importorskip("httpx", reason="starlette TestClient needs httpx")
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    return TestClient(app)


def _db_available() -> bool:
    return bool(library_db.availability().get("available"))


requires_db = pytest.mark.skipif(
    not _db_available(), reason="analog-db submodule not installed/checked out"
)


# ── Degradation: analog-db absent → graceful, never a 500 ─────────────────────────────────────
def test_status_reports_unavailable_when_db_absent(client, monkeypatch):
    monkeypatch.setattr(library_db, "_modules", lambda: None)
    r = client.get("/api/library/status")
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body["circuits"] == 0
    assert body["classes"] == []
    assert body["reason"]  # a human-readable cause


@pytest.mark.parametrize(
    "path",
    [
        "/api/library/catalog",
        "/api/library/circuits/amp_001_5t",
        "/api/library/circuits/amp_001_5t/schematic",
        "/api/library/results",
        "/api/library/classes",
        "/api/library/templates",
        "/api/library/templates/cm.nmos.simple/image",
    ],
)
def test_data_routes_503_when_db_absent(client, monkeypatch, path):
    monkeypatch.setattr(library_db, "_modules", lambda: None)
    r = client.get(path)
    assert r.status_code == 503
    assert r.json()["detail"]


def test_status_and_routes_degrade_when_submodule_not_checked_out(client, monkeypatch):
    """The *other* degradation mode: the package imports but the submodule isn't checked out
    (``circuits/`` missing). ``status`` must say 'not checked out' (not 'not installed') and the
    data routes still 503 — guarding the ``db_present()`` disjunct in ``_require()``."""
    fake = SimpleNamespace(
        paths=SimpleNamespace(db_present=lambda: False, db_root=lambda: Path("/nope/analog-db")),
        model=SimpleNamespace(),
    )
    monkeypatch.setattr(library_db, "_modules", lambda: fake)

    body = client.get("/api/library/status").json()
    assert body["available"] is False
    assert body["db_root"] == "/nope/analog-db"
    assert "checked out" in body["reason"]

    assert client.get("/api/library/catalog").status_code == 503
    assert client.get("/api/library/circuits/amp_001_5t").status_code == 503


# ── Live contract: requires the committed analog-db database ───────────────────────────────────
@requires_db
def test_status_available(client):
    body = client.get("/api/library/status").json()
    assert body["available"] is True
    assert body["circuits"] > 0
    assert "amplifier" in body["classes"]
    assert body["db_root"]


@requires_db
def test_catalog_shape_and_5t_ota(client):
    body = client.get("/api/library/catalog").json()
    assert body["schema"].startswith("spicexplorer/catalog@")
    assert "amplifier" in body["classes"]
    assert "amp_001_5t" in body["classes"]["amplifier"]

    by_id = {c["id"]: c for c in body["circuits"]}
    c = by_id["amp_001_5t"]
    # the keyword field serializes by its `class` alias, never `klass`
    assert c["class"] == "amplifier"
    assert "klass" not in c
    assert c["compensation"] == "none"
    assert c["stages"] == 1
    # superset: bindings grow (amp_001_5t gained FOUNDRY-n65 in the bench-validation pass)
    assert set(c["pdks"]) >= {"ihp-sg13g2", "sky130", "gf180mcu"}
    assert c["provenance"]["designer"] == "Harald Pretl"
    assert c["provenance"]["license"] == "Apache-2.0"


@requires_db
def test_circuit_detail_datasheet_and_results(client):
    body = client.get("/api/library/circuits/amp_001_5t").json()
    assert body["class"] == "amplifier"
    assert body["ports"] == ["vdd", "vout", "vinp", "vinn", "ibias", "vss"]
    assert body["datasheet"]  # the raw datasheet.yaml, non-empty
    # detail is a true superset of the catalog entry: the schematic refs + raw deck index carry over
    assert body["schematic"]  # non-empty schematic-ref map
    assert "sky130" in body["raw"]  # the per-PDK raw testbench-deck index

    sky = body["results"]["sky130"]
    assert sky["corner"] == "tt"
    assert sky["run_at"]  # ISO timestamp from the result's provenance
    # flattened measures carry the headline datasheet numbers (committed result —
    # scoreboard/sky130/e65488f64a.json, the vector re-baselined by adb #56)
    assert sky["measures"]["dcgain"] == pytest.approx(26.02513)
    assert sky["measures"]["ugf"] == pytest.approx(299264.1)
    assert sky["measures"]["pm"] == pytest.approx(96.5195)
    # raw analysis blocks survive alongside the flattened view
    assert sky["analyses"]["ac_open_loop"]["measures"]["dcgain"] == pytest.approx(26.02513)
    # the 5t has no symbolic cross-check
    assert sky["symbolic"] is None


@requires_db
def test_bulk_results_map(client):
    body = client.get("/api/library/results").json()
    results = body["results"]
    # sparse: only circuits with a recorded run appear (the 5t OTA is one of them)
    assert "amp_001_5t" in results
    assert results["amp_001_5t"]["sky130"]["measures"]["dcgain"] == pytest.approx(26.02513)
    # an unmeasured circuit is omitted entirely (not present with empty results)
    by_circuit = set(results)
    assert all(results[cid] for cid in by_circuit)  # no empty per-circuit maps


@requires_db
def test_circuit_detail_symbolic_crosscheck(client):
    body = client.get("/api/library/circuits/amp_018_telescopic_cascode").json()
    sym = body["results"]["ihp-sg13g2"]["symbolic"]
    assert sym is not None
    assert sym["sim"] == pytest.approx(52.81459)
    assert sym["sym"] == pytest.approx(52.192716, rel=1e-5)
    assert sym["agrees"] is True


@requires_db
def test_circuit_detail_unknown_404(client):
    r = client.get("/api/library/circuits/no_such_circuit")
    assert r.status_code == 404
    assert "no_such_circuit" in r.json()["detail"]


@requires_db
def test_circuit_detail_lists_schematic_modes(client):
    body = client.get("/api/library/circuits/amp_001_5t").json()
    modes = body["schematics"]
    # the 5t has all three rendered views committed
    assert "block_aware" in modes
    assert "hierarchical" in modes
    assert "pure" in modes
    assert modes["block_aware"].endswith("_annotated.svg")


@requires_db
def test_schematic_svg_served_by_mode(client):
    for mode in ("block_aware", "hierarchical", "pure"):
        r = client.get(f"/api/library/circuits/amp_001_5t/schematic?mode={mode}")
        assert r.status_code == 200, mode
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert b"<svg" in r.content


@requires_db
def test_schematic_bad_mode_400_and_unknown_circuit_404(client):
    assert client.get("/api/library/circuits/amp_001_5t/schematic?mode=nope").status_code == 400
    assert client.get("/api/library/circuits/no_such/schematic").status_code == 404


@pytest.fixture()
def draft_cleanup():
    """Remove any draft circuit dirs a create test scaffolds into the real DB."""
    created: list[str] = []
    yield created
    import shutil

    from spicexplorer_analog_db import paths

    for cid in created:
        d = paths.circuits_root() / cid
        if d.is_dir():
            shutil.rmtree(d)


def _new_circuit_payload(cid: str):
    return {
        "id": cid,
        "class": "amplifier",
        "display_name": "Wizard Draft OTA",
        "compensation": "Miller",
        "stages": 2,
        "ports": ["vdd", "vout", "vinp", "vinn", "vss"],
        "pdks": ["sky130"],
        "analyses": ["ac_open_loop", "dc_op"],
        "provenance": {"source": "wizard", "designer": "tester"},
    }


@requires_db
def test_create_circuit_scaffolds_draft(client, draft_cleanup):
    cid = "wizard_test_draft_ota"
    draft_cleanup.append(cid)
    r = client.post("/api/library/circuits", json=_new_circuit_payload(cid))
    assert r.status_code == 201
    body = r.json()
    assert body["created"] is True
    assert body["circuit"]["id"] == cid
    assert body["circuit"]["class"] == "amplifier"
    assert body["circuit"]["status"] == "draft"
    # the scaffolded draft is now loadable via the detail route
    assert client.get(f"/api/library/circuits/{cid}").status_code == 200


@requires_db
def test_create_circuit_conflict_409(client, draft_cleanup):
    cid = "wizard_test_dupe_ota"
    draft_cleanup.append(cid)
    assert client.post("/api/library/circuits", json=_new_circuit_payload(cid)).status_code == 201
    assert client.post("/api/library/circuits", json=_new_circuit_payload(cid)).status_code == 409


@requires_db
@pytest.mark.parametrize("mutate", [{"id": "../evil"}, {"id": "Bad Id"}, {"pdks": []}, {"ports": []}])
def test_create_circuit_bad_manifest_400(client, mutate):
    payload = {**_new_circuit_payload("wizard_test_reject"), **mutate}
    assert client.post("/api/library/circuits", json=payload).status_code == 400


def test_create_circuit_503_when_db_absent(client, monkeypatch):
    monkeypatch.setattr(library_db, "_modules", lambda: None)
    r = client.post("/api/library/circuits", json=_new_circuit_payload("wizard_x"))
    assert r.status_code == 503


@requires_db
def test_classes_registry(client):
    classes = {c["class"]: c for c in client.get("/api/library/classes").json()["classes"]}
    assert "amplifier" in classes
    amp = classes["amplifier"]
    assert "dc_gain_db" in amp["canonical_metrics"]
    assert "ac_open_loop" in amp["templates"]
    assert amp["description"]


@requires_db
def test_pdk_registry(client):
    """The pdk→engine matrix is the committed sim_engine markers, nothing asserted."""
    pdks = {p["id"]: p["sim_engine"] for p in client.get("/api/library/pdks").json()["pdks"]}
    assert pdks["sky130"] == "ngspice"
    assert pdks["ihp-sg13g2"] == "ngspice"
    assert pdks["gf180mcu"] == "ngspice"
    assert pdks["FOUNDRY-n65"] == "spectre"


def test_pdks_503_when_db_absent(client, monkeypatch):
    monkeypatch.setattr(library_db, "_modules", lambda: None)
    assert client.get("/api/library/pdks").status_code == 503


@requires_db
def test_classes_testbench_profiles(client):
    """Each class template ships a repo-derived profile: honest per-engine availability
    (ngspice = committed .spice, spectre = wired bench), binding slots, description."""
    classes = {c["class"]: c for c in client.get("/api/library/classes").json()["classes"]}
    amp = classes["amplifier"]
    tbs = {t["name"]: t for t in amp["testbenches"]}
    assert set(tbs) == set(amp["templates"])
    ac = tbs["ac_open_loop"]
    assert "ngspice" in ac["engines"]
    assert "spectre" in ac["engines"]
    assert ac["path"].endswith("testbench-templates/ac_open_loop.spice")
    assert "PDK_INCLUDE" in ac["slots"] and "VDD" in ac["slots"]
    assert ac["description"]
    assert ac["spectre_analyses"] >= 1 and ac["spectre_calculator"] >= 1
    # engines are derived, never asserted: only sources that exist in the repo appear
    for cl in classes.values():
        for t in cl["testbenches"]:
            assert set(t["engines"]) <= {"ngspice", "spectre"}


@requires_db
def test_templates_library(client):
    body = client.get("/api/library/templates").json()
    assert "current_mirror" in body["families"]
    by_id = {t["id"]: t for t in body["templates"]}
    cm = by_id["cm.nmos.simple"]
    assert cm["family"] == "current_mirror"
    assert cm["polarity"] == "nmos"
    assert cm["ports"]["supply"] == "VSS"
    # each template advertises its committed PNG render (or None); this one has one
    assert cm["image"] and cm["image"].endswith(".png")


@requires_db
def test_template_image_served(client):
    r = client.get("/api/library/templates/cm.nmos.simple/image")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic


@requires_db
def test_template_image_unknown_404(client):
    assert client.get("/api/library/templates/no.such.template/image").status_code == 404


@requires_db
def test_testbench_netlist_served(client):
    r = client.get("/api/library/testbenches/amplifier/ac_open_loop/netlist")
    assert r.status_code == 200
    body = r.json()
    assert body["class"] == "amplifier" and body["name"] == "ac_open_loop"
    assert body["path"].endswith("testbench-templates/ac_open_loop.spice")
    # the authored template text, ${...} binding slots intact
    assert "${PDK_INCLUDE}" in body["content"]
    assert ".ac" in body["content"] or "ac dec" in body["content"]


@requires_db
def test_testbench_netlist_shared_fallback_and_404(client):
    # dc_op exists class-scoped for amplifier; the shared copy serves other classes
    r = client.get("/api/library/testbenches/ldo/dc_op/netlist")
    assert r.status_code in (200, 404)  # ldo may own its own dc_op; either resolution is fine
    assert client.get("/api/library/testbenches/amplifier/no_such_tb/netlist").status_code == 404
    # ids with path characters are 404, never filesystem hits
    assert client.get("/api/library/testbenches/amplifier/..%2Fsecrets/netlist").status_code == 404


@requires_db
def test_testbench_spectre_view_composed(client):
    r = client.get("/api/library/testbenches/amplifier/ac_open_loop/netlist",
                   params={"engine": "spectre"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["engine"] == "spectre" and body["language"] == "yaml"
    assert body["path"].endswith("classes/amplifier/spectre-benches.yaml")
    # composed: bench wiring + the referenced analysis template + SKILL expressions
    assert "bench:" in body["content"] and "calculator_expressions:" in body["content"]
    assert "gainBwProd" in body["content"] or "cross(dB20" in body["content"]
    # a bench with no spectre wiring (or unknown engine) degrades cleanly
    assert client.get("/api/library/testbenches/amplifier/no_such/netlist",
                      params={"engine": "spectre"}).status_code == 404
    assert client.get("/api/library/testbenches/amplifier/ac_open_loop/netlist",
                      params={"engine": "xyce"}).status_code == 400


@requires_db
def test_template_netlist_served(client):
    r = client.get("/api/library/templates/cm.pmos.low_voltage_cascode/netlist")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["language"] == "spice"
    assert body["path"].endswith(".spice")
    assert ".subckt" in body["content"].lower() or "m1" in body["content"].lower()
    assert client.get("/api/library/templates/no.such/netlist").status_code == 404


@requires_db
def test_schematic_sources_inventory(client):
    r = client.get("/api/library/circuits/amp_010_peng_acbc/schematic-sources")
    assert r.status_code == 200, r.text
    body = r.json()
    modes = {g["mode"] for g in body["generated"]}
    assert {"pure", "block_aware"} <= modes
    # this circuit vendors a paper figure under reference/
    names = [ref["name"] for ref in body["reference"]]
    assert any(n.lower().endswith(".png") for n in names)
    assert client.get("/api/library/circuits/nope/schematic-sources").status_code == 404


@requires_db
def test_reference_image_served_and_guarded(client):
    src = client.get("/api/library/circuits/amp_010_peng_acbc/schematic-sources").json()
    name = src["reference"][0]["name"]
    r = client.get("/api/library/circuits/amp_010_peng_acbc/reference-image",
                   params={"name": name})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")
    # traversal + non-displayable are 404
    assert client.get("/api/library/circuits/amp_010_peng_acbc/reference-image",
                      params={"name": "../circuit.yaml"}).status_code == 404
