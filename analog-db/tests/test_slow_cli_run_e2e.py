"""Real-SPICE CLI E2E (nightly): the full user path — ``analog-db run --docker-image … --write``
— assemble → simulate (ngspice in the base image) → extract → record a scoreboard design point.

Runs against a scratch copy of the DB (``SPICEXPLORER_ANALOG_DB``) so the checkout stays clean,
then compares the freshly-recorded baseline entry against the committed one: same analyses, all
``ok``, measures within loose tolerance (guards against silent extraction/recording regressions
while allowing ngspice-version drift).
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[1]
_BASE_IMAGE = "spicexplorer-spice-base:local"
_PDK = "sky130"
_CIRCUITS = ["amp_001_5t", "ldo_004_basic_pmos"]

REL_TOL = 0.25  # loose: allows engine drift, still catches wrong-by-an-order regressions
ABS_TOL = 1e-9


def _base_image_available() -> bool:
    # probe with a real `docker run` — `docker image inspect` can false-negative (see test_slow_sim)
    try:
        return (
            subprocess.run(
                ["docker", "run", "--rm", _BASE_IMAGE, "true"], capture_output=True, timeout=120
            ).returncode
            == 0
        )
    except Exception:
        return False


pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        not _base_image_available(),
        reason=f"{_BASE_IMAGE} not built (docker compose --profile base build spice-base)",
    ),
]


def _cli() -> str:
    exe = Path(sys.executable).with_name("analog-db")
    return str(exe) if exe.exists() else "analog-db"


@pytest.fixture(scope="module")
def scratch_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dst = tmp_path_factory.mktemp("scratch") / "analog-db"
    shutil.copytree(
        _REPO,
        dst,
        ignore=shutil.ignore_patterns(".git", ".github", "__pycache__", "raw", "notebooks"),
    )
    return dst


def _baseline_entry(root: Path, circuit: str) -> dict:
    sb = root / "circuits" / circuit / "scoreboard"
    did = yaml.safe_load((sb / "baselines.yaml").read_text())["baselines"][_PDK]
    return json.loads((sb / _PDK / f"{did}.json").read_text())


@pytest.mark.parametrize("circuit", _CIRCUITS)
def test_run_write_round_trip(scratch_db: Path, circuit: str) -> None:
    env = os.environ.copy()
    env["SPICEXPLORER_ANALOG_DB"] = str(scratch_db)
    proc = subprocess.run(
        [
            _cli(),
            "run",
            "--circuit",
            circuit,
            "--pdk",
            _PDK,
            "--docker-image",
            _BASE_IMAGE,
            "--write",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=1800,
    )
    assert proc.returncode == 0, f"run failed:\n{proc.stdout}\n{proc.stderr}"
    assert "wrote" in proc.stdout

    fresh = _baseline_entry(scratch_db, circuit)  # default sizing -> upserts the baseline entry
    committed = _baseline_entry(_REPO, circuit)
    assert fresh["design_id"] == committed["design_id"], "default sizing no longer hashes to the baseline design point"

    fresh_tt = fresh["corners"]["tt"]["analyses"]
    committed_tt = committed["corners"]["tt"]["analyses"]
    assert set(fresh_tt) == set(committed_tt), "analysis set changed"
    for name, block in fresh_tt.items():
        assert block["status"] in ("ok", "disabled"), f"{name}: {block['status']}"
        for measure, value in block.get("measures", {}).items():
            ref = committed_tt[name].get("measures", {}).get(measure)
            if not isinstance(ref, (int, float)) or not isinstance(value, (int, float)):
                continue
            assert math.isclose(value, ref, rel_tol=REL_TOL, abs_tol=ABS_TOL), (
                f"{circuit}/{name}/{measure}: fresh {value} vs committed {ref} "
                f"(rel_tol={REL_TOL})"
            )
