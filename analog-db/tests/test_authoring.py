"""Scaffold (Register-wizard write path) — validation, id sanitization, overwrite refusal.

Runs against a throwaway DB root (``SPICEXPLORER_ANALOG_DB``) seeded with the real ``_shared/schema``
so the manifest is validated by the actual ``circuit.schema.json``. No SPICE.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from spicexplorer_analog_db import authoring, paths
from spicexplorer_analog_db.authoring import ScaffoldError

_REPO = Path(__file__).resolve().parents[1]


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    (tmp_path / "circuits").mkdir()
    shutil.copytree(_REPO / "_shared" / "schema", tmp_path / "_shared" / "schema")
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path))
    return tmp_path


def _manifest(**over):
    m = {
        "id": "my_new_ota",
        "class": "amplifier",
        "display_name": "My New OTA",
        "compensation": "Miller",
        "stages": 2,
        "ports": ["vdd", "vout", "vinp", "vinn", "vss"],
        "pdks": ["sky130"],
        "analyses": ["ac_open_loop", "dc_op"],
        "provenance": {"source": "wizard", "designer": "me"},
    }
    m.update(over)
    return m


def _doc(cdir: Path) -> dict:
    return yaml.safe_load((cdir / "circuit.yaml").read_text())


def test_scaffold_creates_valid_draft(tmp_db):
    cdir = authoring.scaffold_circuit(_manifest())
    assert cdir.is_dir() and cdir.name == "my_new_ota"
    doc = _doc(cdir)
    assert doc["schema"] == authoring.CIRCUIT_SCHEMA
    assert doc["class"] == "amplifier"
    assert doc["compensation"] == "Miller"
    assert doc["ports"] and doc["pdks"]
    assert doc["status"] == "draft"


def test_scaffold_forces_draft_status(tmp_db):
    # an incoming status is never trusted — a scaffold is always a draft
    cdir = authoring.scaffold_circuit(_manifest(status="validated"))
    assert _doc(cdir)["status"] == "draft"


def test_scaffold_only_emits_schema_keys(tmp_db):
    cdir = authoring.scaffold_circuit(_manifest(bogus="x", __proto__="y"))
    assert "bogus" not in _doc(cdir)  # additionalProperties: false is respected


@pytest.mark.parametrize("bad", ["../evil", "Evil", "has space", "9lead", "", "a/b"])
def test_scaffold_rejects_bad_id(tmp_db, bad):
    with pytest.raises(ScaffoldError):
        authoring.scaffold_circuit(_manifest(id=bad))


def test_scaffold_refuses_overwrite(tmp_db):
    authoring.scaffold_circuit(_manifest())
    with pytest.raises(FileExistsError):
        authoring.scaffold_circuit(_manifest())
    # explicit overwrite is allowed
    cdir = authoring.scaffold_circuit(_manifest(display_name="v2"), overwrite=True)
    assert _doc(cdir)["display_name"] == "v2"


@pytest.mark.parametrize("empty", [{"ports": []}, {"pdks": []}])
def test_scaffold_requires_ports_and_pdks(tmp_db, empty):
    with pytest.raises(ScaffoldError):
        authoring.scaffold_circuit(_manifest(**empty))
