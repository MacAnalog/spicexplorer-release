"""xschem generation recorded as a first-class `kind: xschem` run (project-fs P3.1c).

Generation keeps its existing behavior/response (the legacy work_root()/xschem/generated
write + /xschem/file serving is untouched); ADDITIVELY it now mints a run with input
provenance and copies its outputs into the run's own artifacts/.
"""
from __future__ import annotations

import json
import textwrap

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app

NETLIST = textwrap.dedent(
    """
    * tiny mixed circuit
    XM1 out in 0 0 sg13_lv_nmos w=1u l=0.13u ng=1 m=1
    R1 out vdd 10k
    C1 out 0 1p
    .end
    """
).strip()


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    return tmp_path / "work"


@pytest.fixture()
def client(work):
    return TestClient(app)


def _runs(work):
    base = work / "runs"
    return [d for d in base.glob("*") if (d / "run.json").is_file()] if base.exists() else []


def test_successful_generation_records_an_xschem_run(client, work):
    resp = client.post("/api/xschem/from-netlist",
                       json={"netlist_text": NETLIST, "name": "tiny", "render": "none"})
    assert resp.status_code == 200, resp.text

    runs = _runs(work)
    assert len(runs) == 1
    rec = json.loads((runs[0] / "run.json").read_text())
    assert rec["kind"] == "xschem"
    assert rec["status"] == "done"
    assert rec["coordinates"]["name"] == "tiny"
    # the source netlist is content-addressed for provenance
    assert "sha256" in rec["inputs"]["netlist_text"]
    # the run is self-contained: the generated .sch lives under its own artifacts/
    sch = list((runs[0] / "artifacts").glob("*.sch"))
    assert sch and sch[0].read_text().strip()


def test_client_errors_do_not_mint_a_run(client, work):
    assert client.post("/api/xschem/from-netlist", json={}).status_code == 400
    assert client.post("/api/xschem/from-netlist",
                       json={"netlist_text": NETLIST, "netlist_path": "/x.spice"}).status_code == 400
    assert _runs(work) == []


def test_generation_failure_records_an_error_run(work, monkeypatch):
    # Force a failure AFTER the run is minted; the status code must be preserved and
    # the run recorded as error.
    def _boom(*a, **k):
        raise RuntimeError("synthetic build failure")

    monkeypatch.setattr("spicexplorer_api.routes.xschem.build_sch", _boom)
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/api/xschem/from-netlist",
                       json={"netlist_text": NETLIST, "name": "tiny", "render": "none"})
    assert resp.status_code == 500  # RuntimeError propagates unchanged

    runs = _runs(work)
    assert len(runs) == 1
    rec = json.loads((runs[0] / "run.json").read_text())
    assert rec["kind"] == "xschem"
    assert rec["status"] == "error"
    assert "synthetic build failure" in rec["error"]
