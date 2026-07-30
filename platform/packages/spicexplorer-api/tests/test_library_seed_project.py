"""Start a new project seeded from an analog-db catalog circuit (project-fs P5).

`library_db.seed_from_catalog` reads a circuit dir directly and creates a registered v2
project seeded with its netlist + topology provenance. Tests are hermetic: a fixture corpus
+ a monkeypatched `_require`, so they run without the analog-db package installed (the
worktree submodule is empty) and still exercise the full seeding + degradation paths.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app
from spicexplorer_api.services import library_db, project_service


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    return tmp_path / "work"


@pytest.fixture()
def client(work):
    return TestClient(app)


@pytest.fixture()
def corpus(tmp_path, monkeypatch) -> Path:
    """A minimal analog-db-shaped fixture + a `_require` that points at it."""
    root = tmp_path / "adb"
    cdir = root / "circuits" / "amp_demo"
    (cdir / "abstract").mkdir(parents=True)
    (cdir / "abstract" / "netlist.spice").write_text("* demo amp\nM1 vout vin 0 0 nch\n")
    (cdir / "pdk" / "ihp-sg13g2").mkdir(parents=True)
    (cdir / "pdk" / "ihp-sg13g2" / "sizing.yaml").write_text("W: 10u\n")
    (cdir / "circuit.yaml").write_text(
        "class: amplifier\ndisplay_name: Demo Amp\npdks: [ihp-sg13g2]\n"
        "provenance: {source: test-corpus, designer: nobody}\n")
    fake = SimpleNamespace(paths=SimpleNamespace(db_root=lambda: root, db_present=lambda: True))
    monkeypatch.setattr(library_db, "_require", lambda: fake)
    return root


def test_seed_service_copies_netlist_and_provenance(work, corpus):
    out = library_db.seed_from_catalog("amp_demo", pdk="ihp-sg13g2")
    pid = out["id"]
    assert out["cell"] == "amp_demo" and out["pdk"] == "ihp-sg13g2" and out["netlist_seeded"] is True

    pd = work / "projects" / pid
    assert (pd / "design" / "cells" / "amp_demo" / "netlist.spice").read_text().startswith("* demo amp")
    assert (pd / "design" / "cells" / "amp_demo" / "sizing.yaml").read_text() == "W: 10u\n"
    sel = json.loads((pd / "topology" / "selection.json").read_text())
    assert sel["source"] == "analog-db" and sel["circuit_id"] == "amp_demo"
    assert sel["provenance"]["source"] == "test-corpus" and sel["netlist_from"] == "abstract/netlist.spice"
    man = json.loads((pd / "manifest.json").read_text())
    assert man["source"] == {"kind": "analog-db", "ref": "amp_demo", "pdk": "ihp-sg13g2"}
    assert man["default_pdk"] == "ihp-sg13g2"
    # it is a real, registered, browsable project
    assert project_service.project_exists(pid)


def test_seed_route_returns_201_and_registers(client, work, corpus):
    r = client.post("/api/library/circuits/amp_demo/project", json={"name": "My Amp"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["circuit_id"] == "amp_demo" and body["netlist_seeded"] is True
    # the new project shows up in the registry
    pid = body["id"]
    assert any(p["id"] == pid for p in client.get("/api/projects").json()["projects"])
    assert json.loads((work / "projects" / pid / "manifest.json").read_text())["name"] == "My Amp"


def test_seed_defaults_pdk_to_first_when_unspecified(work, corpus):
    out = library_db.seed_from_catalog("amp_demo")   # no pdk → first in circuit.yaml
    assert out["pdk"] == "ihp-sg13g2"


def test_unknown_circuit_404(client, corpus):
    assert client.post("/api/library/circuits/no_such/project", json={}).status_code == 404
    # traversal in the id is rejected the same way
    assert client.post("/api/library/circuits/..%2Fetc/project", json={}).status_code in (404, 400)


def test_degrades_503_when_analog_db_absent(client, monkeypatch):
    monkeypatch.setattr(library_db, "_modules", lambda: None)   # analog-db not installed
    r = client.post("/api/library/circuits/amp_demo/project", json={})
    assert r.status_code == 503
