"""Regression tests for the 2026-06 UI/TODO completion work (ui/backend).

Covers the new backend surface added while closing out the planning-doc TODO:
  - §5c .meas auto-discovery (netlist_parser.parse_meas_candidates)
  - §5e spec library route (/api/spec-library)
  - §16 #4 checkpoint listing n_iters (_count_iters)
  - §10 run-report zip (/api/checkpoint/{id}/report)
  - §2 Apply-from-editor ws_root anchoring (/project/load with content + path)
  - §16 #7 score_service._normalized_penalties dedup helper

Pure dict/function/HTTP transforms — no ngspice / PDK / live sim needed. Skipped
unless the `ui` extra (FastAPI) is installed.
"""
import io
import sys
import zipfile
from pathlib import Path

import pytest
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")

CASCODE_YAML = REPO_ROOT / "examples" / "OTA" / "cascode" / "ihp-sg13g2" / "sizing" / "project_setup.yaml"


# ---------- §5c: .meas auto-discovery ----------

def test_parse_meas_candidates_extracts_result_names():
    from spicexplorer_api.services.netlist_parser import parse_meas_candidates

    nl = "\n".join([
        ".param cl=50f",
        ".meas ac ugf WHEN vdb(out)=0",
        ".measure tran sr TRIG v(out) VAL=0.1 RISE=1",
        ".meas ac ugf find foo",  # duplicate name — first wins
        "* a comment .meas ac bogus",  # comment line, not matched
    ])
    cands = parse_meas_candidates(nl)
    names = {c["name"]: c["sim_type"] for c in cands}
    assert names == {"ugf": "ac", "sr": "tran"}


def test_parse_meas_candidates_empty_when_none():
    from spicexplorer_api.services.netlist_parser import parse_meas_candidates

    assert parse_meas_candidates(".param x=1\nR1 a b 1k\n") == []


def test_netlist_parse_route_returns_meas_candidates():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    content = b".param cl=50f\n.meas ac ugf WHEN vdb(out)=0\n"
    res = c.post("/api/netlist/parse", files={"file": ("tb.spice", content, "text/plain")})
    assert res.status_code == 200
    body = res.json()
    assert body["meas_candidates"] == [{"name": "ugf", "sim_type": "ac"}]
    assert {p["name"] for p in body["params"]} == {"cl"}


# ---------- §5e: spec library ----------

def test_spec_library_route_serves_templates():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    res = c.get("/api/spec-library")
    assert res.status_code == 200
    specs = res.json()["specs"]
    names = {s["name"] for s in specs}
    # The shipped library covers the standard analog specs.
    assert {"ugf", "pm", "gbw", "cmrr", "psrr", "slew_rate"} <= names
    # Every entry has the fields the wizard form merges.
    for s in specs:
        assert "goal" in s and "target" in s


def test_spec_library_file_exists_and_parses():
    import yaml

    p = REPO_ROOT / "examples" / "spec_library.yaml"
    assert p.exists()
    data = yaml.safe_load(p.read_text())
    assert isinstance(data["specs"], list) and len(data["specs"]) >= 6


# ---------- §16 #4: checkpoint listing n_iters ----------

def test_checkpoint_list_populates_n_iters():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    items = c.get("/api/checkpoint").json()["checkpoints"]
    presets = [x for x in items if x.get("source") == "preset"]
    assert presets, "expected preset checkpoints"
    # Previously always None for the listing; now counted from the file.
    for x in presets:
        assert isinstance(x.get("n_iters"), int) and x["n_iters"] > 0


def test_count_iters_json_and_csv(tmp_path):
    import json

    from spicexplorer_api.routes.checkpoint import _count_iters

    j = tmp_path / "ck.json"
    j.write_text(json.dumps({"optimization_log": [{}, {}, {}]}))
    assert _count_iters(j) == 3

    csv = tmp_path / "ck.csv"
    csv.write_text("h1,h2\n1,2\n3,4\n")
    assert _count_iters(csv) == 2

    bad = tmp_path / "missing.json"
    assert _count_iters(bad) is None


# ---------- §10: run-report zip ----------

def test_checkpoint_report_returns_zip_with_summary():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    ids = [x["id"] for x in c.get("/api/checkpoint").json()["checkpoints"] if x.get("source") == "preset"]
    assert ids
    res = c.get(f"/api/checkpoint/{ids[0]}/report")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    z = zipfile.ZipFile(io.BytesIO(res.content))
    names = z.namelist()
    assert "summary.md" in names
    # The original checkpoint file is bundled too.
    assert any(n.endswith(".csv") or n.endswith(".json") for n in names)
    assert "# Run report" in z.read("summary.md").decode()


def test_checkpoint_report_404_unknown():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    assert c.get("/api/checkpoint/nope-not-real/report").status_code == 404


# ---------- §2: Apply-from-editor anchors ws_root to the original dir ----------

@pytest.mark.skipif(not CASCODE_YAML.exists(), reason="cascode example missing")
def test_load_content_with_path_anchors_relative_ws_root():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    content = CASCODE_YAML.read_text()  # uses `ws_root: ..`
    res = c.post("/api/project/load", json={"yaml_content": content, "yaml_path": str(CASCODE_YAML)})
    assert res.status_code == 200, res.text
    ws_root = res.json()["summary"]["ws_root"]
    # The relative `..` is resolved against the ORIGINAL yaml's dir, NOT the temp dir.
    expected = (CASCODE_YAML.parent / "..").resolve()
    assert Path(ws_root) == expected


@pytest.mark.skipif(not CASCODE_YAML.exists(), reason="cascode example missing")
def test_load_content_without_path_uses_temp_dir():
    """Uploads (no yaml_path) keep the prior behavior — no ws_root rewrite."""
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    c = TestClient(app)
    content = CASCODE_YAML.read_text()
    res = c.post("/api/project/load", json={"yaml_content": content})
    assert res.status_code == 200, res.text
    # Still loads/summarises fine; ws_root resolves against the temp file's dir.
    assert res.json()["summary"]["ws_root"]


# ---------- §16 #7: score_service penalty (SC-4: error_type + log_scale aware) ----------

def test_spec_penalties_zero_when_met_positive_when_violated():
    from spicexplorer.core.domains import TargetSpec
    from spicexplorer_api.services.score_service import _spec_penalties

    # MINIMIZE spec (target 200, tol 10, range 100). Met below target+tol; violated above it.
    spec = TargetSpec(name="power", testbench="tb", target=200.0, tolerance=10.0, range=100.0,
                      goal="minimize", sim_type="op", measurement={"meas": "power_uw", "probe": "i(i)"})
    assert _spec_penalties(150.0, spec) == (0.0, 0.0, True)   # comfortably met
    assert _spec_penalties(205.0, spec) == (0.0, 0.0, True)   # inside the tolerance band
    lin, sig, passes = _spec_penalties(260.0, spec)           # violated
    assert lin > 0.0 and sig > 0.0 and passes is False
