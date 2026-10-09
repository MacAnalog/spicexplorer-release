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
- **One run lifecycle** (§6 — out-of-envelope writers): :func:`begin_run` /
  :func:`finalize_run` mint, record and close a run, with an optional
  ``on_change`` hook where a host keeps a derived index — no sqlite here. Today
  only the API's one-shot routes call it; the optimizer CLI (OPT-F7) and
  orchestration campaigns (ORCH-F05) are still to move onto it.
  :class:`RunWriter` is an incremental run on that pair (one ``events.ndjson``
  line + heartbeat per row) whose context manager finishes the run ``error``
  when its body raises.

The envelope does NOT dictate the full ``run.json`` schema — each writer keeps
its own fields (the optimizer's UI contract is unchanged) and merges
:func:`envelope_fields` in. ``envelope: 1`` marks a record that carries these
semantics; legacy run.jsons (no marker, no owner) keep their old reconcile
behavior.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import socket
import time
import uuid
from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any

from spicexplorer_core.atomic_io import atomic_write_bytes, atomic_write_json

logger = logging.getLogger(__name__)

ENVELOPE_VERSION = 1
HEARTBEAT_NAME = ".heartbeat"
OBJECTS_DIR_NAME = ".objects"
# A writer heartbeats at least per trial/step; anything quieter than this on a
# FOREIGN host (where a pid probe is impossible) is presumed dead.
STALE_HEARTBEAT_S = 3600.0
EVENTS_FILE = "events.ndjson"
# A RunWriter's default event: one harness ledger row (campaigns were its first writer).
EVENT_LEDGER_ROW = "ledger_row"
# The platform's run-status vocabulary (what the API writes and the retention pass reads).
STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_ERROR = "error"
TERMINAL_STATUSES = frozenset({STATUS_DONE, STATUS_ERROR})

# ``on_change(run_dir)``: a host's hook after a run.json commit (the API's index
# write-through). It must not raise: run.json on disk is the record; the index is derived from it.
OnChange = Callable[[Path], None]

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


# ---------- the run lifecycle (§6: one kernel entry point for every writer) ----------


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def begin_run(
    runs_base: Path,
    kind: str,
    *,
    project_id: str | None = None,
    project_dir: Path | None = None,
    label: str | None = None,
    inputs: Mapping[str, Any] | None = None,
    input_files: Mapping[str, Path] | None = None,
    input_values: Mapping[str, Any] | None = None,
    coordinates: dict[str, Any] | None = None,
    retention: str = "metrics_only",
    record_extras: Mapping[str, Any] | None = None,
    on_change: OnChange | None = None,
) -> tuple[str, Path]:
    """Mint a run dir under ``runs_base`` (dir == run_id), content-address its
    inputs into ``project_dir``'s ``.objects/`` (hashes only when unscoped), and
    commit the initial ``status: running`` envelope record. Returns
    ``(run_id, run_dir)``.

    ``inputs`` is provenance the caller already holds (merged as-is, e.g. a
    harness name); ``input_files``/``input_values`` go through
    :func:`snapshot_inputs`. ``record_extras`` merge last, so a caller can also
    override presentation fields such as ``label``. No heartbeat is touched — a
    one-shot run's ``run.json`` mtime stands in for it; incremental writers
    (:class:`RunWriter`) heartbeat per row. ``on_change`` fires once the record is
    committed. Raises ``OSError`` if the run dir can't be created or recorded —
    the caller decides whether that's fatal."""
    run_id, rdir = mint_run_dir(Path(runs_base), kind)
    snap = snapshot_inputs(project_objects_dir(project_dir), files=input_files, values=input_values)
    write_run_record(
        rdir,
        {
            "run_id": run_id,
            "project_id": project_id,
            "label": label,
            "status": STATUS_RUNNING,
            "started": _now(),
            **envelope_fields(
                kind,
                retention=retention,
                inputs={**(inputs or {}), **snap},
                coordinates=coordinates,
            ),
            **(record_extras or {}),
        },
    )
    if on_change is not None:
        on_change(rdir)
    return run_id, rdir


def finalize_run(
    run_dir: Path,
    *,
    status: str,
    score: float | None = None,
    metrics: Mapping[str, float] | None = None,
    error: str | None = None,
    record_extras: Mapping[str, Any] | None = None,
    on_change: OnChange | None = None,
) -> dict[str, Any]:
    """Stamp a run's terminal record: ``status``, ``ended``, ``best_score`` and
    ``metrics`` (always present — the index reads them), ``error`` when given,
    then ``record_extras``. Returns the committed record.

    The status is NOT validated here (the API's streaming optimizer also ends
    runs ``stopped``); :meth:`RunWriter.finish` holds its writers to
    :data:`TERMINAL_STATUSES`. A failed write raises ``OSError`` — a best-effort
    caller catches it — and ``on_change`` fires either way, so a derived index
    re-reads whatever the filesystem now holds."""
    try:
        rec = read_run_record(run_dir)
        rec.update(status=status, best_score=score, metrics=dict(metrics or {}), ended=_now())
        if error:
            rec["error"] = error
        rec.update(record_extras or {})
        write_run_record(run_dir, rec)
        return rec
    finally:
        if on_change is not None:
            on_change(run_dir)


def sanitize(obj: Any) -> Any:
    """A strict-JSON-safe copy: non-finite floats → ``None``, unknown objects → ``str``,
    dict keys → ``str``; lists/tuples/sets become lists."""
    if isinstance(obj, bool) or obj is None or isinstance(obj, (str, int)):
        return obj
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [sanitize(v) for v in obj]
    return str(obj)


class RunWriter:
    """One incremental run envelope: rows in, one ``events.ndjson`` line each.

    ``__init__`` opens the run through :func:`begin_run` (status ``running``,
    ``n_events: 0``) and touches the heartbeat; :meth:`append` adds one event line
    per row and touches the heartbeat; :meth:`finish` closes it through
    :func:`finalize_run` with the event count. Lifted from orchestration's
    ``workflows.events.RunMirror`` (same constructor, event shape and status
    vocabulary), which is to become a re-export of it (ORCH-F05; today
    orchestration still defines its own).

    Event line shape (keys are stable; add, never rename)::

        {"event": "<event>", "ts": "<ISO-8601>", "iter": <1-based row index>, "data": <row>}

    Lines are strict JSON (:func:`sanitize`), and ``iter`` makes each one a
    candidate row for :func:`~spicexplorer_core.workspace.retention.iter_candidates`.

    As a context manager the run can't be left ``running`` by a crash: a clean
    exit finishes it ``done``, an exception (``KeyboardInterrupt`` included)
    finishes it ``error`` with the exception recorded — and the exception always
    propagates, even if that last write fails. A run already finished inside the
    block keeps its explicit verdict.
    """

    def __init__(
        self,
        runs_base: Path,
        *,
        kind: str = "campaign",
        label: str = "",
        inputs: dict[str, Any] | None = None,
        coordinates: dict[str, Any] | None = None,
        retention: str = "metrics_only",
    ) -> None:
        self.run_id, self.run_dir = begin_run(
            Path(runs_base),
            kind,
            label=label,
            inputs=inputs,
            coordinates=coordinates,
            retention=retention,
            record_extras={"n_events": 0},
        )
        self.n = 0
        self.finished = False
        touch_heartbeat(self.run_dir)

    def append(self, row: dict, *, event: str = EVENT_LEDGER_ROW) -> dict:
        """Append one row as an event line (1-based ``iter``); returns the event."""
        self.n += 1
        line = {"event": event, "ts": _now(), "iter": self.n, "data": sanitize(row)}
        with (self.run_dir / EVENTS_FILE).open("a") as fh:
            fh.write(json.dumps(line, allow_nan=False) + "\n")
        touch_heartbeat(self.run_dir)
        return line

    def finish(
        self,
        status: str = STATUS_DONE,
        *,
        best_score: float | None = None,
        metrics: dict[str, float] | None = None,
        error: str | None = None,
    ) -> dict:
        """Close the envelope: status (:data:`TERMINAL_STATUSES` only), end time, event
        count (and optional score/metrics/error). Returns the committed record."""
        if status not in TERMINAL_STATUSES:
            raise ValueError(
                f"status {status!r} is not a terminal platform run status {sorted(TERMINAL_STATUSES)}"
            )
        record = finalize_run(
            self.run_dir,
            status=status,
            score=best_score,
            metrics=metrics,
            error=error,
            record_extras={"n_events": self.n},
        )
        self.finished = True
        return record

    def __enter__(self) -> RunWriter:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self.finished:
            return
        if exc_type is None:
            self.finish(STATUS_DONE)
            return
        detail = str(exc) if exc is not None else ""
        try:
            self.finish(
                STATUS_ERROR,
                error=f"{exc_type.__name__}: {detail}" if detail else exc_type.__name__,
            )
        except Exception:
            # never mask the body's exception with a bookkeeping failure
            logger.warning("could not record the error status of %s", self.run_dir, exc_info=True)
