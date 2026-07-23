"""Crash-safety contract for ``spicexplorer_core.atomic_io`` — the checkpoint
writer that must never leave a torn file for the next resume to choke on."""
from __future__ import annotations

import json

import pytest
from spicexplorer_core.atomic_io import atomic_write_json, atomic_write_text


def test_atomic_write_text_roundtrips_and_creates_parents(tmp_path):
    target = tmp_path / "nested" / "dir" / "out.txt"
    ret = atomic_write_text(target, "hello world")
    assert ret == target
    assert target.read_text() == "hello world"


def test_atomic_write_json_matches_plain_json_dump(tmp_path):
    """Output must be byte-identical to the old ``json.dump(data, f, indent=2)``
    so switching the save path can't change committed/checkpoint bytes."""
    data = {"schema_version": 3, "optimization_log": [{"a": 1, "b": [1, 2, 3]}]}
    target = tmp_path / "ck.json"
    atomic_write_json(target, data, indent=2)
    assert target.read_text() == json.dumps(data, indent=2)
    assert json.loads(target.read_text()) == data


def test_atomic_write_forwards_encoder(tmp_path):
    """A custom encoder (e.g. the checkpoint's Path/numpy encoder) is honored."""
    from pathlib import Path

    class _Enc(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, Path):
                return str(o)
            return super().default(o)

    target = tmp_path / "ck.json"
    atomic_write_json(target, {"p": Path("/tmp/x")}, cls=_Enc)
    assert json.loads(target.read_text()) == {"p": "/tmp/x"}


def test_no_temp_files_left_after_success(tmp_path):
    atomic_write_json(tmp_path / "ck.json", {"ok": True})
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "ck.json"]
    assert leftovers == [], f"stray temp files: {leftovers}"


def test_failed_serialization_leaves_no_temp_and_no_target(tmp_path):
    """If json.dumps raises (unserializable payload), we must not create the
    target at all and must clean up the temp — the previous good file (none here)
    stays untouched."""
    target = tmp_path / "ck.json"
    with pytest.raises(TypeError):
        atomic_write_json(target, {"bad": object()})
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_existing_file_preserved_when_new_write_fails(tmp_path):
    """The core crash-safety guarantee: a failed write never clobbers the
    existing complete file (os.replace only runs after a full, fsync'd temp)."""
    target = tmp_path / "ck.json"
    atomic_write_json(target, {"generation": 1})
    with pytest.raises(TypeError):
        atomic_write_json(target, {"generation": 2, "torn": object()})
    # Old content still fully intact and parseable.
    assert json.loads(target.read_text()) == {"generation": 1}
    assert [p.name for p in tmp_path.iterdir()] == ["ck.json"]
