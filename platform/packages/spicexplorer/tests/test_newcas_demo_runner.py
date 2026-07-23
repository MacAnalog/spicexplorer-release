from spicexplorer.demo.newcas_demo_runner import list_traces, load_demo_config, load_trace


def test_load_demo_config_uses_cascode_setup():
    config = load_demo_config()

    assert config["project"]["name"] == "CASCODE-OTA"
    assert config["project"]["wsRoot"].endswith("examples/OTA/cascode/ihp-sg13g2")
    assert len(config["enabledTestbenches"]) == 3
    assert {spec["name"] for spec in config["targetSpecs"]} >= {"ugf", "dcgain", "pm"}


def test_list_traces_exposes_newcas_csvs():
    traces = list_traces()

    assert traces
    assert all(trace["id"].startswith("CASCODE-OTA_") for trace in traces)
    assert any(trace["scoreShape"] == "relative-sigmoid" for trace in traces)


def test_load_trace_normalizes_metrics_and_candidates():
    trace = load_trace("CASCODE-OTA_LhsDE_2026-02-07_10-54-54_sigmoid-loss", limit=5)

    assert trace["rowCount"] == 5
    assert "ugf" in trace["metrics"]
    assert "X_DUT_M1M2_W" in trace["params"]
    assert trace["rows"][0]["metrics"]["ugf"]["value"] is not None
    assert trace["topCandidates"][0]["score"] >= trace["topCandidates"][-1]["score"]
