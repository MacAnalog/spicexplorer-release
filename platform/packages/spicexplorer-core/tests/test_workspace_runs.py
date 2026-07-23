"""Run-envelope kernel tests.

Fast, NO SPICE. Pins: sortable dir==run_id minting (collision-proof), the
envelope record fields, heartbeat/owner-liveness semantics (the reconcile
gate), and content-addressed input snapshots that survive by hash.
"""
import json
import os
import socket
import time

from spicexplorer_core.workspace import runs as wr


def test_new_run_id_is_sortable_and_checkpoint_safe():
    rid = wr.new_run_id("Optimize!")
    ts, kind, hex8 = rid.split("_")
    assert len(ts) == 15 and kind == "optimize" and len(hex8) == 8
    assert "." not in rid and "/" not in rid and "::" not in rid
    # Lexical order == chronological order (the dir listing stays browsable).
    from datetime import datetime
    a = wr.new_run_id("sim", now=datetime(2026, 7, 14, 1, 0, 0))
    b = wr.new_run_id("sim", now=datetime(2026, 7, 14, 2, 0, 0))
    assert a < b


def test_mint_run_dir_dir_equals_run_id(tmp_path):
    rid, d = wr.mint_run_dir(tmp_path / "runs", "simulate")
    assert d.name == rid and d.is_dir()
    rid2, d2 = wr.mint_run_dir(tmp_path / "runs", "simulate")
    assert rid2 != rid and d2 != d


def test_envelope_fields_and_record_roundtrip(tmp_path):
    rid, d = wr.mint_run_dir(tmp_path / "runs", "simulate")
    rec = {"run_id": rid, "status": "running",
           **wr.envelope_fields("simulate", retention="full")}
    wr.write_run_record(d, rec)
    back = wr.read_run_record(d)
    assert back["envelope"] == wr.ENVELOPE_VERSION and back["kind"] == "simulate"
    assert back["owner"]["pid"] == os.getpid()
    assert back["owner"]["hostname"] == socket.gethostname()
    assert back["retention"] == "full"
    assert not list(d.glob(".*.tmp"))  # atomic write left no temp
    # Torn/missing record reads as {} — never raises.
    (d / "run.json").write_text('{"run_id": "x", ')
    assert wr.read_run_record(d) == {}


def test_owner_liveness_gates(tmp_path):
    rid, d = wr.mint_run_dir(tmp_path / "runs", "opt")
    wr.write_run_record(d, {"run_id": rid, "status": "running"})
    # Legacy record (no owner) → dead (old reconcile behavior preserved).
    assert wr.owner_is_dead({}, d)
    # Live pid on this host → NOT dead (an agent's run survives an API restart).
    rec = wr.envelope_fields("opt")
    assert not wr.owner_is_dead(rec, d)
    # Dead pid on this host → dead.
    rec_dead = dict(rec, owner=dict(rec["owner"], pid=2**22 + 12345))
    assert wr.owner_is_dead(rec_dead, d)
    # Same host, live pid, but a DIFFERENT start token (pid was recycled) → dead.
    rec_recycled = dict(rec, owner=dict(rec["owner"], start_token="0"))
    if wr._proc_start_token(os.getpid()) is not None:  # /proc available (Linux)
        assert wr.owner_is_dead(rec_recycled, d)
    # Foreign host + fresh heartbeat → not dead; stale heartbeat → dead.
    rec_remote = dict(rec, owner=dict(rec["owner"], hostname="elsewhere"))
    wr.touch_heartbeat(d)
    assert not wr.owner_is_dead(rec_remote, d)
    old = time.time() - 7200
    os.utime(d / wr.HEARTBEAT_NAME, (old, old))
    os.utime(d / "run.json", (old, old))
    assert wr.owner_is_dead(rec_remote, d, stale_after_s=3600)
    assert not wr.owner_is_dead(rec_remote, d, stale_after_s=10_000)


def test_touch_heartbeat_never_rewrites_run_json(tmp_path):
    rid, d = wr.mint_run_dir(tmp_path / "runs", "opt")
    wr.write_run_record(d, {"run_id": rid})
    before = (d / "run.json").stat().st_mtime_ns
    wr.touch_heartbeat(d)
    wr.touch_heartbeat(d)  # utime path (file exists)
    assert (d / "run.json").stat().st_mtime_ns == before
    assert (d / wr.HEARTBEAT_NAME).exists()


def test_snapshot_inputs_content_addresses_and_tolerates_errors(tmp_path):
    proj = tmp_path / "proj"
    netlist = tmp_path / "dut.spice"
    netlist.write_text("* netlist v1\n")
    objects = wr.project_objects_dir(proj)
    out = wr.snapshot_inputs(
        objects,
        files={"dut": netlist, "missing": tmp_path / "nope.spice"},
        values={"params": {"W1": 2e-6, "L1": 0.18e-6}},
    )
    sha = out["dut"]["sha256"]
    assert (proj / ".objects" / sha).read_bytes() == netlist.read_bytes()
    assert "error" in out["missing"] and "sha256" not in out["missing"]
    # Values hash over canonical JSON and land in the store too.
    vsha = out["params"]["sha256"]
    assert json.loads((proj / ".objects" / vsha).read_text()) == {
        "W1": 2e-6, "L1": 0.18e-6}
    # Idempotent: re-snapshot → same sha, no duplicate objects.
    out2 = wr.snapshot_inputs(objects, files={"dut": netlist})
    assert out2["dut"]["sha256"] == sha
    assert len(list((proj / ".objects").iterdir())) == 2
    # Unscoped (no project): hashes only, nothing written anywhere.
    out3 = wr.snapshot_inputs(None, files={"dut": netlist})
    assert out3["dut"]["sha256"] == sha
