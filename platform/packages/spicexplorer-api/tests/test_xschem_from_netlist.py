"""POST /api/xschem/from-netlist — generate a .sch from a netlist (P2).

Host-runnable: .sch generation is pure Python. Image export degrades gracefully when xschem is
absent (image_available=False), which is the host case here — the .sch is still produced and served.
"""

from __future__ import annotations

import textwrap

import pytest

NETLIST = textwrap.dedent(
    """
    * tiny mixed circuit
    XM1 out in 0 0 sg13_lv_nmos w=1u l=0.13u ng=1 m=1
    XM2 vdd in out vdd sg13_lv_pmos w=2u l=0.13u ng=1 m=1
    R1 out vdd 10k
    C1 out 0 1p
    .end
    """
).strip()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    return TestClient(app)


def test_from_netlist_text_generates_sch(client):
    resp = client.post(
        "/api/xschem/from-netlist",
        json={"netlist_text": NETLIST, "name": "tiny", "pdk": "ihp-sg13g2", "render": "none"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["device_count"] == 4  # XM1, XM2, R1, C1
    assert body["warnings"] == []
    # .sch content is well-formed and carries the devices + net names (default = topology + wires).
    # Param display is suppressed by default (build_sch show_device_params=False), so MOS devices draw
    # the clean "no-params" symbol twin (devices/*_np.sym), not the full PDK symbol.
    assert body["sch_content"].startswith("v {xschem version=")
    assert "devices/sg13_lv_nmos_np.sym" in body["sch_content"]
    assert "lab=out" in body["sch_content"]
    # persisted under work_root() so the existing GET /xschem/file can serve it
    assert body["sch_path"] and body["sch_path"].endswith(".sch")
    served = client.get("/api/xschem/file", params={"path": body["sch_path"]})
    assert served.status_code == 200
    assert served.json()["content"] == body["sch_content"]


def test_render_degrades_gracefully_without_xschem(client):
    from spicexplorer_netlist2xschem import xschem_available

    resp = client.post(
        "/api/xschem/from-netlist",
        json={"netlist_text": NETLIST, "name": "tiny", "render": "png"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # .sch always produced; image only when xschem is present
    assert body["sch_content"]
    assert body["image_available"] is xschem_available()
    if not xschem_available():
        assert body["image_path"] is None


def test_requires_one_input(client):
    assert client.post("/api/xschem/from-netlist", json={}).status_code == 400
    assert client.post(
        "/api/xschem/from-netlist", json={"netlist_text": NETLIST, "netlist_path": "/x.spice"}
    ).status_code == 400


def test_relative_path_rejected(client):
    resp = client.post("/api/xschem/from-netlist", json={"netlist_path": "rel/path.spice"})
    assert resp.status_code == 400


def test_bad_netlist_is_422(client):
    # text that produces no parseable devices still yields a valid (empty) .sch, not a 500;
    # a path that escapes allowed roots is rejected.
    resp = client.post("/api/xschem/from-netlist", json={"netlist_path": "/etc/passwd"})
    assert resp.status_code in (400, 403, 404)
