"""Cadence/Spectre env probes (the "Cadence absent" CI skip-gate).

Deterministic via monkeypatch: every probe is driven from a cleaned environment so the
result never depends on whatever the host happens to export. Also pins that
`probe_env` (the open-PDK `/api/env` contract) is UNCHANGED by this work.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_core import env

_ALL_CADENCE_VARS = (
    "VB_CADENCE_CSHRC",
    "CDS_INST_DIR",
    "CDSHOME",
    "CDS_ROOT",
    "VB_REMOTE_HOST",
    "VB_SPECTRE_BIN",
)


@pytest.fixture
def clean_cadence_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in _ALL_CADENCE_VARS:
        monkeypatch.delenv(var, raising=False)
    # no spectre binary on PATH, deterministically
    monkeypatch.setattr(env.shutil, "which", lambda _cmd: None)


# ---------------------------------------------------------------------------
# probe_spectre
# ---------------------------------------------------------------------------
def test_probe_spectre_absent(clean_cadence_env: None) -> None:
    res = env.probe_spectre()
    assert res["spectre_ok"] is False
    assert res["spectre_bin"] is None
    assert res["spectre_remote_host"] is None


def test_probe_spectre_via_vb_bin(clean_cadence_env: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_spectre = tmp_path / "spectre"
    fake_spectre.write_text("#!/bin/sh\n")
    monkeypatch.setenv("VB_SPECTRE_BIN", str(fake_spectre))
    res = env.probe_spectre()
    assert res["spectre_ok"] is True
    assert res["spectre_bin"] == str(fake_spectre)


def test_probe_spectre_reports_remote_host(clean_cadence_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VB_REMOTE_HOST", "eda-srv")
    res = env.probe_spectre()
    assert res["spectre_remote_host"] == "eda-srv"


# ---------------------------------------------------------------------------
# probe_cadence
# ---------------------------------------------------------------------------
def test_probe_cadence_absent(clean_cadence_env: None) -> None:
    res = env.probe_cadence()
    assert res["cadence_ok"] is False
    assert res["cadence_source"] is None
    assert "unavailable" in res["cadence_detail"]


def test_probe_cadence_via_install_var(clean_cadence_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CDS_INST_DIR", "/opt/cadence/SPECTRE")
    res = env.probe_cadence()
    assert res["cadence_ok"] is True
    assert res["cadence_source"] == "CDS_INST_DIR"


def test_probe_cadence_via_bridge_remote(clean_cadence_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VB_REMOTE_HOST", "eda-srv")
    res = env.probe_cadence()
    assert res["cadence_ok"] is True
    assert res["cadence_source"] == "VB_REMOTE_HOST"


# ---------------------------------------------------------------------------
# probe_cadence_env aggregate
# ---------------------------------------------------------------------------
def test_probe_cadence_env_live_requires_both(clean_cadence_env: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # absent → not live
    assert env.probe_cadence_env()["cadence_live_enabled"] is False

    # spectre binary but no cadence env → still not live
    fake_spectre = tmp_path / "spectre"
    fake_spectre.write_text("#!/bin/sh\n")
    monkeypatch.setenv("VB_SPECTRE_BIN", str(fake_spectre))
    assert env.probe_cadence_env()["cadence_live_enabled"] is False

    # add a cadence env → live
    monkeypatch.setenv("CDS_INST_DIR", "/opt/cadence")
    verdict = env.probe_cadence_env()
    assert verdict["cadence_live_enabled"] is True
    assert verdict["spectre_ok"] is True and verdict["cadence_ok"] is True


# ---------------------------------------------------------------------------
# probe_env is untouched
# ---------------------------------------------------------------------------
def test_probe_env_contract_unchanged() -> None:
    keys = set(env.probe_env())
    assert {"ngspice_ok", "pdk_ok", "live_runs_enabled", "tech"} <= keys
    # the Cadence probes must NOT have leaked into the open-PDK /api/env contract
    assert "cadence_ok" not in keys
    assert "spectre_ok" not in keys
