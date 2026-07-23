"""The generalized run envelope.

A *run* is one user/agent-level action of any kind (optimize, simulate, sweep,
annotate, layout, …): a self-contained directory whose name IS its server-minted
``run_id``, carrying a ``run.json`` record, an ``events.ndjson`` stream, and its
artifacts. This module owns the primitives every writer (the API's
``optimizer_runner``/routes AND orchestration agents) shares, so no process
invents its own run shape:

- **Sortable ids, dir == run_id**: ``{YYYYMMDD-HHMMSS}_{kind}_{hex8}`` —
  collision-proof via ``mkdir(exist_ok=False)`` + retry, lexically ordered by
  start time so directory listings stay human-browsable, and only
  checkpoint-safe characters (no ``.``/``::``/path separators).
- **Owner liveness**: ``run.json`` gets an ``owner`` block
  (pid/hostname/started) and the run dir a ``.heartbeat`` file the writer
  touches as work progresses. A startup reconciler flips ``running → error``
  ONLY for a provably-dead owner (:func:`owner_is_dead`) — an agent's long job
  legitimately survives an API restart.
- **Provenance**: :func:`snapshot_inputs` hashes every input blob
  and copies it into the owning project's ``.objects/<sha256>`` store, so the
  hashes in an immutable run record dereference forever.

The envelope does NOT dictate the full ``run.json`` schema — each writer keeps
its own fields (the optimizer's UI contract is unchanged) and merges
:func:`envelope_fields` in. ``envelope: 1`` marks a record that carries these
semantics; legacy run.jsons (no marker, no owner) keep their old reconcile
behavior.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from spicexplorer_core.atomic_io import atomic_write_bytes, atomic_write_json

ENVELOPE_VERSION = 1
HEARTBEAT_NAME = ".heartbeat"
OBJECTS_DIR_NAME = ".objects"
# A writer heartbeats at least per trial/step; anything quieter than this on a
# FOREIGN host (where a pid probe is impossible) is presumed dead.
STALE_HEARTBEAT_S = 3600.0

_KIND_SAFE = re.compile(r"[^a-z0-9-]+")


def new_run_id(kind: str, *, now: datetime | None = None) -> str:
    """Sortable, checkpoint-safe run id: ``{ts}_{kind}_{hex8}``."""
    ts = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    k = _KIND_SAFE.sub("-", (kind or "run").lower()).strip("-") or "run"
    return f"{ts}_{k}_{uuid.uuid4().hex[:8]}"


def mint_run_dir(runs_base: Path, kind: str) -> tuple[str, Path]:
    """Create a fresh run dir whose NAME is the run_id. ``exist_ok=False``
    + retry makes server-side minting collision-proof even across processes."""
    runs_base.mkdir(parents=True, exist_ok=True)
    for _ in range(8):
        run_id = new_run_id(kind)
        d = runs_base / run_id
        try:
            d.mkdir(exist_ok=False)
            return run_id, d
        except FileExistsError:  # same-second hex8 collision — vanishingly rare
            continue
    raise RuntimeError(f"could not mint a unique run dir under {runs_base}")


def _proc_start_token(pid: int) -> str | None:
    """A process-identity token that changes when a pid is reused — the Linux
    ``/proc/<pid>/stat`` starttime (field 22, jiffies since boot). ``None`` when
    ``/proc`` is unavailable (macOS dev, some containers); callers then fall back
    to a bare liveness probe. ``comm`` (field 2) can contain ``) `` so we split
    on the LAST ``) `` — everything after it starts at field 3 (state), making
    starttime index 19 there."""
    try:
        with open(f"/proc/{pid}/stat", encoding="ascii", errors="replace") as f:
            after_comm = f.read().rsplit(") ", 1)[1]
        return after_comm.split()[19]
    except (OSError, IndexError):
        return None


def envelope_fields(
    kind: str,
    *,
    retention: str = "metrics_only",
    inputs: dict[str, Any] | None = None,
    coordinates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The envelope's standard ``run.json`` fields — merge into the writer's own
    record. ``retention``: ``full | metrics_only | none`` (what artifact tier
    the run keeps; the pruning pass keys off it). The ``owner`` block records a
    process-start token so :func:`owner_is_dead` can tell a live writer from a
    recycled pid across an API restart."""
    pid = os.getpid()
    return {
        "envelope": ENVELOPE_VERSION,
        "kind": kind,
        "owner": {
            "pid": pid,
            "hostname": socket.gethostname(),
            "start_token": _proc_start_token(pid),
            "started": datetime.now().isoformat(timespec="seconds"),
        },
        "retention": retention,
        "inputs": inputs or {},
        "coordinates": coordinates or {},
    }


def write_run_record(run_dir: Path, record: dict[str, Any]) -> None:
    """Atomic ``run.json`` write (a torn record must never orphan a run)."""
    atomic_write_json(run_dir / "run.json", record, indent=2)


def read_run_record(run_dir: Path) -> dict[str, Any]:
    """Tolerant read: missing/torn → ``{}``."""
    try:
        data = json.loads((run_dir / "run.json").read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def touch_heartbeat(run_dir: Path) -> None:
    """Cheap liveness signal (one utime/create — NO run.json rewrite, so it is
    safe to call per trial without index churn). Never raises."""
    hb = run_dir / HEARTBEAT_NAME
    try:
        os.utime(hb)
    except FileNotFoundError:
        try:
            hb.touch()
        except OSError:
            pass
    except OSError:
        pass


def owner_is_dead(
    record: Mapping[str, Any],
    run_dir: Path,
    *,
    stale_after_s: float = STALE_HEARTBEAT_S,
) -> bool:
    """Is the run's writer provably gone? (the reconcile gate)

    - legacy record (no ``owner``) → True — old behavior: a restart flips it;
    - owner on THIS host → pid probe (``kill 0``); pid alive → not dead;
    - owner on a FOREIGN host → the ``.heartbeat`` mtime (else ``run.json``
      mtime) must be fresher than ``stale_after_s``.
    """
    owner = record.get("owner")
    if not isinstance(owner, dict):
        return True
    if owner.get("hostname") == socket.gethostname():
        pid = owner.get("pid")
        if not isinstance(pid, int) or pid <= 0:
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:  # exists, owned by another user
            return False
        except OSError:
            return True
        # pid answers — but is it the SAME process, or a recycled pid after a
        # restart? Compare the recorded start token: a mismatch means the pid
        # was reused, so the original writer is gone (dead). Only trust "alive"
        # when the token matches (or neither side has one — the /proc-less
        # fallback keeps the old bare-liveness behavior).
        recorded = owner.get("start_token")
        current = _proc_start_token(pid)
        if recorded is not None and current is not None and recorded != current:
            return True
        return False
    for probe in (run_dir / HEARTBEAT_NAME, run_dir / "run.json"):
        try:
            return (time.time() - probe.stat().st_mtime) > stale_after_s
        except OSError:
            continue
    return True


# ---------- input provenance ----------

def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_inputs(
    objects_dir: Path | None,
    *,
    files: Mapping[str, Path] | None = None,
    values: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Hash (and content-address) a run's inputs for the record's ``inputs`` map.

    ``files``: name → path; each file's bytes are sha256'd and, when an
    ``objects_dir`` is given (the owning project's ``.objects/``), copied to
    ``<objects_dir>/<sha>`` so the hash dereferences forever. ``values``: name →
    JSON-serializable value, hashed over its canonical (sorted-keys) encoding
    and snapshotted the same way. Unscoped runs pass ``objects_dir=None`` —
    hashes only. Unreadable files record an error entry instead of raising
    (provenance must never fail the run itself).
    """
    out: dict[str, Any] = {}

    def _store(blob: bytes) -> str:
        sha = hash_bytes(blob)
        if objects_dir is not None:
            obj = objects_dir / sha
            # Content-addressed → an existing object is already this exact blob;
            # skip the rewrite. atomic_write_bytes (fsync + dir-fsync + guaranteed
            # temp cleanup) makes the object durable — the store's whole promise is
            # that a run's provenance hashes "dereference forever".
            if not obj.exists():
                try:
                    atomic_write_bytes(obj, blob)
                except OSError:
                    pass  # snapshot is best-effort; the sha is still recorded
        return sha

    for name, path in (files or {}).items():
        try:
            blob = Path(path).read_bytes()
        except OSError as e:
            out[name] = {"path": str(path), "error": str(e)}
            continue
        out[name] = {"path": str(path), "sha256": _store(blob)}
    for name, value in (values or {}).items():
        blob = json.dumps(value, sort_keys=True, default=str).encode()
        out[name] = {"sha256": _store(blob)}
    return out


def project_objects_dir(project_dir: Path | None) -> Path | None:
    """The owning project's content store (``.objects/``); None when unscoped."""
    return (project_dir / OBJECTS_DIR_NAME) if project_dir is not None else None
