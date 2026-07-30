"""Checkpoint-CSV dot-column contract + hostile project names (test-suite review 2026-06-11,
api backlog)."""

from __future__ import annotations

import textwrap

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app
    return TestClient(app)


# ── checkpoint reader: pandas dot-columns (the documented .iterrows() constraint) ─────────────
def test_csv_checkpoint_reads_dot_columns_and_nans(tmp_path):
    """Columns like ``point.score`` are only reachable via ``.iterrows()`` (``.itertuples()``
    silently sanitizes them away) — CLAUDE.md pins this; the test makes it executable. NaN cells
    become ``None`` (JSON-clean), and best-score tracking skips them."""
    from spicexplorer_api.services.checkpoint_reader import read_csv_checkpoint

    csv = tmp_path / "ck.csv"
    csv.write_text(textwrap.dedent("""\
        point.score,fit_summary.gain.curr_val,point.params.w_m1
        -10.0,55.0,5e-06
        ,60.0,6e-06
        -5.0,nan,7e-06
    """))
    out = read_csv_checkpoint(csv)
    assert out["scores"] == [-10.0, None, -5.0]            # empty cell → None, not 0/NaN
    assert out["best_scores"] == [-10.0, -10.0, -5.0]      # None row keeps the running best
    assert out["per_metric"]["gain"] == [55.0, 60.0, None]  # NaN cell → None
    assert out["params"]["w_m1"] == [5e-06, 6e-06, 7e-06]
    assert out["iterations"] == [0, 1, 2] and out["n_iters"] == 3


# ── corner-namespaced metric keys (multi-corner PVT, Phase 2) ────────────────────────────────
def test_csv_checkpoint_reads_corner_namespaced_columns(tmp_path):
    """Multi-corner checkpoints flatten fit_summary keys like ``tt_27C::gain`` into
    columns ``fit_summary.tt_27C::gain.curr_val`` — the prefix/suffix slicing must
    recover the full namespaced metric name (inner ``::`` survives)."""
    from spicexplorer_api.services.checkpoint_reader import read_csv_checkpoint

    csv = tmp_path / "mc.csv"
    csv.write_text(textwrap.dedent("""\
        point.score,fit_summary.tt_27C::gain.curr_val,fit_summary.ss_125C::gain.curr_val
        -10.0,55.0,48.0
        -5.0,60.0,51.0
    """))
    out = read_csv_checkpoint(csv)
    assert out["per_metric"]["tt_27C::gain"] == [55.0, 60.0]
    assert out["per_metric"]["ss_125C::gain"] == [48.0, 51.0]


def test_envelope_and_scatter_resolve_specs_from_namespaced_keys():
    """``<corner>::<spec>`` metric keys must still find the (corner-independent) spec
    definition: the envelope reports pass/fail per corner, and a point is feasible
    only when it passes at EVERY corner."""
    from spicexplorer_api.services.checkpoint_reader import compute_envelope, compute_scatter

    data = {
        # tt passes the 50-target everywhere; ss fails it at point 0, passes at point 1
        "per_metric": {"tt_27C::gain": [55.0, 60.0], "ss_125C::gain": [30.0, 52.0]},
        "scores": [-10.0, -5.0],
    }
    specs = [{"name": "gain", "goal": "exceed", "target": 50.0, "tolerance": 0.0}]

    env = {row["metric"]: row for row in compute_envelope(data, specs)}
    assert env["tt_27C::gain"]["target"] == 50.0 and env["tt_27C::gain"]["passes"] is True
    assert env["ss_125C::gain"]["target"] == 50.0 and env["ss_125C::gain"]["passes"] is True  # best-ever 52

    pts = compute_scatter(data, "tt_27C::gain", "ss_125C::gain", specs)
    assert [p["feasible"] for p in pts] == [False, True]  # point 0 fails at the ss corner


def test_json_checkpoint_pads_sparse_metric_keys(tmp_path):
    """A mixed-era log (bare Phase-1 keys resumed into a multi-corner run) must keep
    per_metric[k][i] aligned with iteration i — absent keys pad with None instead of
    silently compacting the series."""
    import json

    from spicexplorer_api.services.checkpoint_reader import read_json_checkpoint

    def entry(score, fit_summary):
        return {"point": {"params": {"w": 1e-6}, "score": score, "metadata": {}},
                "fit_summary": fit_summary, "log_file": None}

    ckpt = tmp_path / "mixed.json"
    ckpt.write_text(json.dumps({
        "schema_version": "1.0.0",
        "timestamp": "2026-07-03_00-00-00",
        "optimization_log": [
            entry(-10.0, {"gain": {"curr_val": 55.0, "score": -10.0}}),               # bare (old)
            entry(-5.0, {"tt::gain": {"curr_val": 60.0, "score": -5.0},               # namespaced (new)
                          "ss::gain": {"curr_val": 50.0, "score": -6.0}}),
            entry(-4.0, {"tt::gain": {"curr_val": 61.0, "score": -4.0},
                          "ss::gain": {"curr_val": 52.0, "score": -5.0}}),
        ],
    }))
    out = read_json_checkpoint(ckpt)
    assert out["per_metric"]["gain"] == [55.0, None, None]        # old key: padded at the tail
    assert out["per_metric"]["tt::gain"] == [None, 60.0, 61.0]    # new key: padded at the head
    assert out["per_metric"]["ss::gain"] == [None, 50.0, 52.0]
    assert out["n_iters"] == 3


# ── hostile project names ─────────────────────────────────────────────────────────────────────
def test_slugify_neutralizes_path_separators():
    from spicexplorer_api.services.project_service import _slugify, new_project_id

    assert "/" not in _slugify("../../etc/passwd") and ".." not in _slugify("../../etc/passwd")
    assert _slugify("") == "project"                        # empty name falls back
    pid = new_project_id("../evil\x00name")
    assert "/" not in pid and "\x00" not in pid


def test_create_project_with_traversal_name_stays_under_work_root(client, tmp_path):
    r = client.post("/api/projects", json={"name": "../../escape"})
    assert r.status_code == 200, r.text
    pid = r.json()["id"]
    work = tmp_path / "work"
    matches = list(work.rglob("manifest.json"))
    assert matches, "project landed nowhere?"
    for m in matches:
        assert work.resolve() in m.resolve().parents        # nothing escaped WORK_ROOT
    assert ".." not in pid and "/" not in pid
