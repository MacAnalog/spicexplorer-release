"""Upload (route "4a") + browse `parent`: /api/waveview/upload, /api/waveview/browse.

Uploads stage under WORK_ROOT/waveview_uploads/<id>/ and raw artifacts auto-open;
browse's `parent` is whitelist-aware so clients never do path arithmetic. All
fixtures are synthetic (no SPICE) under a monkeypatched WORK_ROOT.
"""

from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient
from spicexplorer_api.main import app
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def work(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path))
    return tmp_path


# --- upload: ngspice .raw ----------------------------------------------------
def test_upload_raw_stages_and_opens(client, work, tmp_path):
    src = tmp_path / "local_tb_ac.raw"
    synth_ac_raw(src)
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("local_tb_ac.raw", src.read_bytes(), "application/octet-stream")},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["kind"] == "ngspice_raw"
    assert body["staged_path"].startswith(str(work / "waveview_uploads"))
    assert body["dataset"] is not None
    assert [a["analysis"] for a in body["dataset"]["analyses"]] == ["ac"]
    # the staged copy is on disk (reviewable under the /work mount)
    assert (work / "waveview_uploads").is_dir()


# --- upload: Spectre PSF zip -------------------------------------------------
def test_upload_spectre_zip_extracts_and_opens(client, work, tmp_path):
    raw_dir = tmp_path / "amp-raw"
    synth_spectre_raw_dir(raw_dir)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for p in raw_dir.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=f"amp-raw/{p.relative_to(raw_dir)}")
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("amp-raw.zip", buf.getvalue(), "application/zip")},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["kind"] == "spectre_raw_dir"
    assert body["dataset"] is not None
    assert body["dataset"]["engine"] == "spectre"


# --- upload: guards ----------------------------------------------------------
def test_upload_rejects_netlist(client, work):
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("ota.spice", b"* netlist\n.end\n", "text/plain")},
    )
    assert res.status_code == 415


def test_upload_rejects_zip_traversal(client, work):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.raw", b"boom")
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
    )
    assert res.status_code == 400
    assert "escapes" in res.json()["detail"]


def test_upload_zip_without_artifact_is_415(client, work):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.md", b"nothing here")
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("docs.zip", buf.getvalue(), "application/zip")},
    )
    assert res.status_code == 415


def test_upload_log_stages_without_opening(client, work):
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("run.log", b"Note: fine\n", "text/plain")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["kind"] == "log"
    assert body["dataset"] is None


# --- browse: whitelist-aware parent ------------------------------------------
def test_browse_parent_inside_root(client, work):
    sub = work / "runs" / "r1"
    sub.mkdir(parents=True)
    res = client.get("/api/waveview/browse", params={"dir": str(sub)})
    assert res.status_code == 200
    assert res.json()["parent"] == str(work / "runs")


def test_browse_parent_null_at_root_boundary(client, work):
    # WORK_ROOT is a tmp dir whose parent is NOT under any allowed root — no "up".
    res = client.get("/api/waveview/browse", params={"dir": str(work)})
    assert res.status_code == 200
    assert res.json()["parent"] is None


# --- review findings: staging cleanup + spectre-member pruning ----------------
def test_rejected_upload_leaves_no_staging(client, work):
    # traversal zip → 400, and the staging dir must be gone afterwards
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.raw", b"boom")
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
    )
    assert res.status_code == 400
    uploads = work / "waveview_uploads"
    assert not uploads.exists() or list(uploads.iterdir()) == []


def test_unparseable_raw_is_rejected_and_cleaned(client, work):
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("garbage.raw", b"\x00\x01 not a raw at all", "application/octet-stream")},
    )
    assert res.status_code >= 400
    uploads = work / "waveview_uploads"
    assert not uploads.exists() or list(uploads.iterdir()) == []


def test_declared_oversize_rejected_early(client, work):
    res = client.post(
        "/api/waveview/upload",
        headers={"content-length": str(2 * 1024**3)},
        files={"file": ("big.raw", b"tiny", "application/octet-stream")},
    )
    assert res.status_code == 413


def test_spectre_zip_with_decoy_member_still_opens_the_dir(client, work, tmp_path):
    # a *.raw-named member INSIDE the PSF dir must not outrank the dir itself
    raw_dir = tmp_path / "amp-raw"
    synth_spectre_raw_dir(raw_dir)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for p in raw_dir.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=f"amp-raw/{p.relative_to(raw_dir)}")
        zf.writestr("amp-raw/decoy.raw", b"junk that would fail to parse")
    res = client.post(
        "/api/waveview/upload",
        files={"file": ("amp-raw.zip", buf.getvalue(), "application/zip")},
    )
    assert res.status_code == 200, res.text
    assert res.json()["kind"] == "spectre_raw_dir"
