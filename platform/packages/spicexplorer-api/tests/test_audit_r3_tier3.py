"""Regression tests for the 2026-06 audit r3 **Tier 3** backend fixes (B13-B15).

- BUG-B13 per-run log handlers are thread-scoped so concurrent runs don't cross-contaminate.
- BUG-B14 the xschem allowed-roots whitelist includes WORK_ROOT (encapsulated-project schematics).
- BUG-B15 the wizard YAML round-trip preserves a frozen dut_param's `val` (operating point).

(B16 is a frontend store change — covered by tsc/eslint + manual reasoning, no Python test.)

Skipped unless the `ui` extra (FastAPI) is installed.
"""
import logging
import sys

import pytest
from _api_fixtures import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")


# ---------- BUG-B13: per-run log handler is thread-scoped ----------

def _record(thread_id: int) -> logging.LogRecord:
    rec = logging.LogRecord("spicexplorer.x", logging.INFO, __file__, 1, "msg", None, None)
    rec.thread = thread_id
    return rec


def test_run_thread_filter_passes_only_its_thread():
    from spicexplorer_api.services.optimizer_runner import _RunThreadFilter
    f = _RunThreadFilter(12345)
    assert f.filter(_record(12345)) is True
    assert f.filter(_record(99999)) is False


def test_run_thread_filter_isolates_two_runs():
    """Two runs (two thread ids) each only see their own records — the cross-contamination fix."""
    from spicexplorer_api.services.optimizer_runner import _RunThreadFilter
    fa, fb = _RunThreadFilter(111), _RunThreadFilter(222)
    rec_a, rec_b = _record(111), _record(222)
    assert fa.filter(rec_a) and not fa.filter(rec_b)
    assert fb.filter(rec_b) and not fb.filter(rec_a)


# ---------- BUG-B14: xschem allowed roots include WORK_ROOT ----------

def test_xschem_allowed_roots_include_work_root(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from spicexplorer_api.app_config import work_root
    from spicexplorer_api.routes import xschem
    wr = work_root().resolve()
    roots = xschem._allowed_roots()
    assert wr in roots, f"WORK_ROOT {wr} not in xschem allowed roots {roots}"


def test_xschem_validate_accepts_path_under_work_root(tmp_path, monkeypatch):
    """An encapsulated project's schematic under WORK_ROOT must NOT 403 (B14)."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from spicexplorer_api.app_config import work_root
    from spicexplorer_api.routes import xschem
    sch = work_root() / "projects" / "p-123" / "xschem" / "ota.sch"
    sch.parent.mkdir(parents=True, exist_ok=True)
    sch.write_text("v {xschem version=3.4.5}")
    assert xschem._validate_under_allowed(sch) == sch.resolve()  # no HTTPException


def test_xschem_validate_still_rejects_outside(tmp_path, monkeypatch):
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    from fastapi import HTTPException
    from spicexplorer_api.routes import xschem
    with pytest.raises(HTTPException) as ei:
        xschem._validate_under_allowed(__import__("pathlib").Path("/etc/passwd"))
    assert ei.value.status_code == 403


# ---------- BUG-B15: wizard round-trip preserves dut_param.val ----------

def test_build_dut_param_emits_val():
    from spicexplorer_api.services.yaml_generator import _build_dut_param
    out = _build_dut_param({"name": "x_l", "freeze": True, "val": "0.18u"})
    assert out.get("freeze") is True
    assert out.get("val") == "0.18u", "frozen operating point `val` was dropped on generate (B15)"


def test_build_dut_param_omits_blank_val():
    from spicexplorer_api.services.yaml_generator import _build_dut_param
    out = _build_dut_param({"name": "x", "min_val": 1, "max_val": 5})
    assert "val" not in out  # blank/absent val must not be emitted


def test_parse_to_form_carries_val():
    from spicexplorer_api.services.yaml_generator import project_dict_to_form
    form = project_dict_to_form({"project": {"dut_params": [
        {"name": "x_l", "freeze": True, "val": "0.18u"},
    ]}})
    rows = form["dut_params"]
    assert rows and rows[0]["val"] == "0.18u", "parse-to-form dropped `val` (B15)"


def test_dut_param_val_full_round_trip():
    """generate → parse → generate keeps a frozen param's val (the un-pinning bug)."""
    from spicexplorer_api.services.yaml_generator import _build_dut_param, project_dict_to_form
    emitted = _build_dut_param({"name": "x_l", "freeze": True, "val": "0.18u"})
    form = project_dict_to_form({"project": {"dut_params": [emitted]}})
    re_emitted = _build_dut_param(form["dut_params"][0])
    assert re_emitted.get("val") == "0.18u"
    assert re_emitted.get("freeze") is True
