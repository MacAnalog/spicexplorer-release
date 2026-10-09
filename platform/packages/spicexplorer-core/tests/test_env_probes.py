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


def test_probe_spectre_via_vb_bin(
    clean_cadence_env: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_spectre = tmp_path / "spectre"
    fake_spectre.write_text("#!/bin/sh\n")
    monkeypatch.setenv("VB_SPECTRE_BIN", str(fake_spectre))
    res = env.probe_spectre()
    assert res["spectre_ok"] is True
    assert res["spectre_bin"] == str(fake_spectre)


def test_probe_spectre_reports_remote_host(
    clean_cadence_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_probe_cadence_via_install_var(
    clean_cadence_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CDS_INST_DIR", "/opt/cadence/SPECTRE")
    res = env.probe_cadence()
    assert res["cadence_ok"] is True
    assert res["cadence_source"] == "CDS_INST_DIR"


def test_probe_cadence_via_bridge_remote(
    clean_cadence_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VB_REMOTE_HOST", "eda-srv")
    res = env.probe_cadence()
    assert res["cadence_ok"] is True
    assert res["cadence_source"] == "VB_REMOTE_HOST"


# ---------------------------------------------------------------------------
# probe_cadence_env aggregate
# ---------------------------------------------------------------------------
def test_probe_cadence_env_live_requires_both(
    clean_cadence_env: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


# ---------------------------------------------------------------------------
# probe_pdk's model-lib search stays inside libs.tech/ngspice (OPT-18)
# ---------------------------------------------------------------------------
@pytest.fixture
def pdk_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """`tmp_path` as the only PDK root — the host's own PDK_ROOT must not leak in."""
    for var in env._PDK_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    return tmp_path


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("* model lib stand-in\n")
    return path


def test_probe_pdk_ignores_a_stray_model_lib(pdk_root: Path) -> None:
    # A copy of the lib somewhere under the root (a design's scratch, a test fixture) is not a
    # PDK install; the unbounded rglob fallback used to report pdk_ok on it.
    _touch(pdk_root / "designs" / "foo" / "models" / "cornerMOSlv.lib")
    assert env.probe_pdk()["pdk_ok"] is False


def test_probe_pdk_ignores_the_xyce_copy_of_the_lib(pdk_root: Path) -> None:
    # The PDK ships the same file name for Xyce; probe_pdk() must not take it as the ngspice lib.
    _touch(pdk_root / "src" / "ihp-sg13g2" / "libs.tech" / "xyce" / "models" / "cornerMOSlv.lib")
    assert env.probe_pdk()["pdk_ok"] is False


def test_probe_pdk_finds_a_nested_ngspice_libs_tech(pdk_root: Path) -> None:
    # An unpacked source tree one level deeper than the known sub-paths still resolves.
    lib = _touch(
        pdk_root
        / "ihp-sg13g2-src"
        / "ihp-sg13g2"
        / "libs.tech"
        / "ngspice"
        / "models"
        / "cornerMOSlv.lib"
    )
    res = env.probe_pdk()
    assert res["pdk_ok"] is True
    assert str(lib) in res["pdk_detail"]


def test_probe_pdk_finds_a_one_level_ngspice_libs_tech(pdk_root: Path) -> None:
    # A tech directory under an unusual name, one level down (not one of the known sub-paths).
    lib = _touch(
        pdk_root / "sg13g2-custom" / "libs.tech" / "ngspice" / "corners" / "cornerMOSlv.lib"
    )
    res = env.probe_pdk()
    assert res["pdk_ok"] is True
    assert str(lib) in res["pdk_detail"]


def test_probe_pdk_finds_a_root_level_libs_tech_in_an_unusual_subdir(pdk_root: Path) -> None:
    lib = _touch(pdk_root / "libs.tech" / "ngspice" / "models" / "v2" / "cornerMOSlv.lib")
    res = env.probe_pdk()
    assert res["pdk_ok"] is True
    assert str(lib) in res["pdk_detail"]


def test_probe_pdk_search_stops_two_levels_below_the_root(pdk_root: Path) -> None:
    # The fallback is bounded: an ngspice libs.tech three levels down is not searched for.
    _touch(pdk_root / "a" / "b" / "c" / "libs.tech" / "ngspice" / "models" / "cornerMOSlv.lib")
    assert env.probe_pdk()["pdk_ok"] is False


def test_find_model_lib_prefers_the_shallowest_then_the_first_sorted_hit(tmp_path: Path) -> None:
    """The fallback answer does not depend on directory-listing order: the shallowest pattern
    wins, and within one pattern the first path in sorted order."""
    deep = _touch(tmp_path / "a-tech" / "libs.tech" / "ngspice" / "models" / "cornerMOSlv.lib")
    _touch(tmp_path / "b-tech" / "libs.tech" / "ngspice" / "models" / "cornerMOSlv.lib")
    assert env._find_model_lib(tmp_path) == deep
    root_level = _touch(tmp_path / "libs.tech" / "ngspice" / "models" / "v2" / "cornerMOSlv.lib")
    assert env._find_model_lib(tmp_path) == root_level


def test_find_model_lib_of_a_missing_root_is_none(tmp_path: Path) -> None:
    assert env._find_model_lib(tmp_path / "no-such-pdk") is None


# ---------------------------------------------------------------------------
# the per-PDK open model table (#306)
# ---------------------------------------------------------------------------
def test_probe_pdk_default_is_byte_identical_for_ihp(
    pdk_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No `tech` (and `tech="ihp-sg13g2"`) gives exactly the pre-#306 IHP result: keys, key order
    and every string, for the three verdicts the UI shows."""
    missing = pdk_root / "nope"
    monkeypatch.setenv("PDK_ROOT", str(missing))
    want_missing = {
        "pdk_root": None,
        "pdk_ok": False,
        "pdk_detail": (
            f"IHP ihp-sg13g2 PDK root set but cornerMOSlv.lib not found under [PDK_ROOT={missing}]. "
            "Live simulation unavailable — replay enabled."
        ),
    }
    for res in (env.probe_pdk(), env.probe_pdk(tech="ihp-sg13g2")):
        assert list(res.items()) == list(want_missing.items())

    lib = _touch(pdk_root / "ihp-sg13g2" / "libs.tech" / "ngspice" / "models" / "cornerMOSlv.lib")
    monkeypatch.setenv("PDK_ROOT", str(pdk_root))
    want_found = {
        "pdk_root": str(pdk_root),
        "pdk_ok": True,
        "pdk_detail": f"IHP ihp-sg13g2 models found via PDK_ROOT ({lib}).",
    }
    assert list(env.probe_pdk().items()) == list(want_found.items())

    monkeypatch.delenv("PDK_ROOT")
    want_unset = {
        "pdk_root": None,
        "pdk_ok": False,
        "pdk_detail": (
            "IHP ihp-sg13g2 models not found (PDK_ROOT/PDK unset; .lib cornerMOSlv.lib unresolved). "
            "Live simulation unavailable — replay enabled."
        ),
    }
    assert list(env.probe_pdk().items()) == list(want_unset.items())
    res = env.probe_env()
    assert list(res)[-5:] == ["pdk_root", "pdk_ok", "pdk_detail", "tech", "live_runs_enabled"]
    assert res["tech"] == "ihp-sg13g2"
    assert {k: res[k] for k in want_unset} == want_unset


def test_open_pdk_table_holds_the_three_open_pdks() -> None:
    # the install dirs + corner libs the MCP adapter's copy (and analog-db's native runner) use
    assert sorted(env.OPEN_PDKS) == ["gf180mcu", "ihp-sg13g2", "sky130"]
    assert env.DEFAULT_TECH == "ihp-sg13g2"
    sky, gf = env.OPEN_PDKS["sky130"], env.OPEN_PDKS["gf180mcu"]
    assert sky.install_dirs == ("sky130A", "sky130B", "sky130")
    assert sky.corner_lib == "sky130.lib.spice"
    assert gf.install_dirs == ("gf180mcuD", "gf180mcuC", "gf180mcuB", "gf180mcuA", "gf180mcu")
    assert gf.corner_lib == "sm141064.ngspice"
    assert env.OPEN_PDKS["ihp-sg13g2"].model_lib == "cornerMOSlv.lib"


@pytest.mark.parametrize(
    ("pdk_id", "rel"),
    [
        ("sky130", "sky130B/libs.tech/ngspice/sky130.lib.spice"),
        ("gf180mcu", "gf180mcuC/libs.tech/ngspice/sm141064.ngspice"),
        ("ihp-sg13g2", "ihp-sg13g2/libs.tech/ngspice/models/cornerMOSlv.lib"),
    ],
)
def test_probe_pdk_models_says_true_only_for_the_installed_one(
    pdk_root: Path, pdk_id: str, rel: str
) -> None:
    _touch(pdk_root / rel)
    models = env.probe_pdk_models()
    assert models == {k: k == pdk_id for k in ("gf180mcu", "ihp-sg13g2", "sky130")}
    assert list(models) == sorted(models)
    assert all(type(v) is bool for v in models.values())
    for k, v in models.items():
        assert env.probe_pdk(tech=k)["pdk_ok"] is v


def test_probe_pdk_models_with_no_pdk_root_is_all_false(
    pdk_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("PDK_ROOT")
    assert env.probe_pdk_models() == {"gf180mcu": False, "ihp-sg13g2": False, "sky130": False}


def test_a_non_ihp_pdk_is_looked_up_only_at_its_install_dirs(pdk_root: Path) -> None:
    # no flat lib, no fallback search for the non-IHP rows: a stray copy is not an install
    _touch(pdk_root / "sky130.lib.spice")
    _touch(pdk_root / "src" / "libs.tech" / "ngspice" / "sky130.lib.spice")
    assert env.probe_pdk(tech="sky130")["pdk_ok"] is False


def test_probe_env_for_another_open_pdk(pdk_root: Path) -> None:
    lib = _touch(pdk_root / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice")
    res = env.probe_env(tech="sky130")
    assert res["tech"] == "sky130"
    assert res["pdk_ok"] is True
    assert res["pdk_detail"] == f"SkyWater sky130 models found via PDK_ROOT ({lib})."
    assert env.probe_env()["pdk_ok"] is False  # the default (IHP) row is untouched


def test_an_unknown_tech_is_a_value_error_naming_the_known_ones() -> None:
    with pytest.raises(ValueError, match="gf180mcu, ihp-sg13g2, sky130"):
        env.probe_pdk(tech="not-a-pdk")
    with pytest.raises(ValueError, match="unknown open PDK 'nope'"):
        env.probe_env(tech="nope")
