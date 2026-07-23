"""Crash-safe file writes.

A checkpoint written with a plain ``open(path, "w"); json.dump(...)`` is left
**corrupt** if the process dies mid-write — a SIGKILL/OOM/power-loss between the
first and last byte truncates the JSON, and the next resume then fails to parse
it, losing the whole run's accumulated history. That is the classic
checkpoint-reliability trap.

``atomic_write_*`` closes it: the payload is written to a temp file **in the same
directory**, flushed + ``fsync``ed to stable storage, then ``os.replace``d over
the target. On POSIX the rename is atomic, so any concurrent reader — including
the next resume — always observes either the previous complete file or the new
complete file, never a half-written one. The temp lives beside the target (not in
``/tmp``) so the rename is a same-filesystem operation; a cross-device rename
would silently degrade to a non-atomic copy.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> Path:
    """Write ``text`` to ``path`` atomically (temp-in-same-dir → fsync → replace).

    Returns the resolved ``Path``. Creates parent directories as needed. On any
    error the temp file is cleaned up and the exception re-raised, so a failed
    write never leaves a stray ``.tmp`` behind and never clobbers an existing
    good file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # mkstemp in the destination dir keeps os.replace on one filesystem (atomic).
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())  # payload durable before the rename
        os.replace(tmp, path)  # atomic swap on POSIX
    except BaseException:
        # Never leave a partial temp behind (incl. on KeyboardInterrupt).
        try:
            tmp.unlink()
        except OSError:
            pass
        raise

    # Best-effort: fsync the directory so the rename itself survives a crash.
    # Harmless where a dir can't be fsync'd (e.g. some network mounts) — the
    # rename is already atomic; this only strengthens durability.
    try:
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass

    return path


def atomic_write_bytes(path: str | Path, data: bytes) -> Path:
    """Write ``data`` bytes to ``path`` atomically (temp-in-same-dir → fsync →
    replace), the binary sibling of :func:`atomic_write_text`. Used by the
    content-addressed object store (``workspace.runs``) so a blob a run's
    provenance points at is durable and can never be a torn half-write.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    try:
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass
    return path


def atomic_write_json(path: str | Path, data: Any, **dumps_kwargs: Any) -> Path:
    """Serialize ``data`` to JSON and write it atomically (see
    :func:`atomic_write_text`). ``dumps_kwargs`` is forwarded to ``json.dumps``
    (e.g. ``cls=`` for a custom encoder); ``indent=2`` is applied by default to
    match the human-readable checkpoint layout.
    """
    dumps_kwargs.setdefault("indent", 2)
    return atomic_write_text(path, json.dumps(data, **dumps_kwargs))
