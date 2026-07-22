"""End-to-end CLI checks — every subcommand through the real ``analog-db`` console script
(subprocess, not in-process imports), the ``new-circuit`` authoring flow against a throwaway
DB root, and catalog/scoreboard stdout determinism vs the committed files. No SPICE, no Docker.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from spicexplorer_analog_db import paths

_REPO = Path(__file__).resolve().parents[1]

SUBCOMMANDS = [
    "verify",
    "generate",
    "export-raw",
    "run",
    "import-analoggym",
    "import-ferrosim",
    "new-circuit",
    "add-binding",
    "gmid-extract",
    "catalog",
    "scoreboard",
]


def _cli() -> str:
    """The installed ``analog-db`` console script — the true entry point under test."""
    exe = Path(sys.executable).with_name("analog-db")
    if exe.exists():
        return str(exe)
    found = shutil.which("analog-db")
    if found:
        return found
    pytest.fail("analog-db console script not installed (uv pip install --no-deps -e .)")


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        [_cli(), *args], capture_output=True, text=True, env=merged, cwd=_REPO, timeout=300
    )


def test_top_level_help_lists_every_subcommand() -> None:
    proc = _run("--help")
    assert proc.returncode == 0, proc.stderr
    for cmd in SUBCOMMANDS:
        assert cmd in proc.stdout, f"subcommand {cmd!r} missing from --help"


@pytest.mark.parametrize("cmd", SUBCOMMANDS)
def test_subcommand_help(cmd: str) -> None:
    # argparse renders --help after wiring the whole subparser, so this catches
    # entry-point/argument-registration breakage that in-process unit tests bypass.
    proc = _run(cmd, "--help")
    assert proc.returncode == 0, proc.stderr


def test_verify_tier0_single_circuit() -> None:
    proc = _run("verify", "--tier", "0", "--circuit", "amp_001_5t")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_catalog_stdout_matches_committed() -> None:
    proc = _run("catalog")
    assert proc.returncode == 0, proc.stderr
    committed = (_REPO / "catalog.json").read_text()
    assert json.loads(proc.stdout) == json.loads(committed)
    # the CLI is the only writer, so stdout must be byte-identical to the committed file
    assert proc.stdout == committed


def test_scoreboard_stdout_matches_committed() -> None:
    proc = _run("scoreboard")
    assert proc.returncode == 0, proc.stderr
    committed = (_REPO / "scoreboard.json").read_text()
    assert json.loads(proc.stdout) == json.loads(committed)
    assert proc.stdout == committed


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    # a minimal registry: schema + class metrics (for id_code) + one taken accession
    (tmp_path / "circuits" / "amp_004_seed").mkdir(parents=True)
    shutil.copytree(_REPO / "_shared" / "schema", tmp_path / "_shared" / "schema")
    shutil.copytree(_REPO / "_shared" / "classes", tmp_path / "_shared" / "classes")
    return tmp_path


def test_new_circuit_scaffold_e2e(tmp_db: Path) -> None:
    proc = _run(
        "new-circuit",
        "--class",
        "amplifier",
        "--slug",
        "ci_probe",
        "--ports",
        "vdd,vout,vinp,vinn,vss",
        "--pdks",
        "sky130",
        env={paths.ENV_VAR: str(tmp_db)},
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "allocated amp_005_ci_probe" in proc.stdout  # max+1 over the seeded amp_004
    doc = yaml.safe_load((tmp_db / "circuits" / "amp_005_ci_probe" / "circuit.yaml").read_text())
    assert doc["id"] == "amp_005_ci_probe"
    assert doc["class"] == "amplifier"
    assert doc["status"] == "draft"  # a scaffold is never trusted as anything else


def test_new_circuit_rejects_unknown_class(tmp_db: Path) -> None:
    proc = _run(
        "new-circuit",
        "--class",
        "flux_capacitor",
        "--slug",
        "nope",
        "--ports",
        "vdd,vss",
        env={paths.ENV_VAR: str(tmp_db)},
    )
    assert proc.returncode == 2
    assert "flux_capacitor" in proc.stderr
