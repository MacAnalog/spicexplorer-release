"""``run_deck``: a deck STRING through native ngspice into its own run directory.

The file-centric :class:`NGSpice_Wrapper` (spicelib) owns a netlist file, wipes its output
folder and runs from the caller's cwd, which is what the optimizer wants. A design lane
wants the opposite: text in, directory out, nothing shared between runs — that is this
module. One call = one directory ``<workdir>/<label>-<sha256(deck)[:8]>`` holding
``.spiceinit`` (written per run because ngspice reads the cwd's before ``~/.spiceinit``
and ``$SPICE_USERINIT_DIR``), ``deck.sp``, ``ngspice.out``, ``wall.txt``, the rawfile(s)
and any ``extra_files`` (basenames only — a key with a separator is refused, as is one of
the lane's own file names). Two runs of the same deck under one label share a directory and
serialize on a ``.busy`` marker holding ``<pid> <hostname>``: a marker whose owner is dead
(``kill(pid, 0)`` → no such process) or unparsable is reclaimed so a killed session cannot
wedge the lane; a marker some other user's live process holds (``PermissionError``) or one
written on another host stays busy — the foreign-host case only until it is older than
``timeout``, since no local ``kill`` can vouch for it. Different decks under one label never
collide.

ngspice exits 0 after a failed operating point, an ignored device line or a failed
``.meas``, so the log is read back before anything is trusted (:mod:`sim_log`): the
scalars land in ``RunResult.measures``, failed ``.meas`` names in ``RunResult.failed``,
and any fatal line in ``RunResult.fatal`` — a non-empty ``fatal``, a non-zero exit or a
timeout raises :class:`DeckRunError` (with the ``result`` attached where one exists).
Error text names the run by ``<label>-<hash>``, not by its absolute path, so it can be
quoted in a ledger or a ticket (the ngspice lines it quotes are verbatim, and a deck that
``.include``s an absolute path will show it).

Layering: core, stdlib only. The harness's ``deck_hash`` is the same sha256 of the deck
text (a longer prefix); core cannot import the harness, so the hash is computed here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import re
import shutil
import socket
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path

from .save_list import SaveList, apply_save_list_to_deck
from .sim_log import fatal_lines, parse_measures

__all__ = ["DeckRunError", "RunResult", "run_deck", "deck_digest", "slug"]

DECK_NAME = "deck.sp"
LOG_NAME = "ngspice.out"
WALL_NAME = "wall.txt"
BUSY_NAME = ".busy"
SPICEINIT_NAME = ".spiceinit"
RESERVED_NAMES = frozenset({DECK_NAME, LOG_NAME, WALL_NAME, BUSY_NAME, SPICEINIT_NAME})


class DeckRunError(RuntimeError):
    """ngspice timed out, exited non-zero, logged a fatal line, or the run dir is busy.

    ``result`` carries the :class:`RunResult` when the simulator did run (rc / fatal cases),
    so a caller can still open the log; it is ``None`` for a timeout or a busy directory.
    """

    def __init__(self, message: str, result: RunResult | None = None) -> None:
        super().__init__(message)
        self.result = result


@dataclasses.dataclass
class RunResult:
    """One finished run. ``os.fspath(r)`` / ``str(r)`` is its directory, so ``Path(r) / "x"``
    works and a ledger row can store ``str(r)``."""

    label: str
    dir: Path
    deck: Path
    log: Path
    raws: list[Path]
    wall: float
    rc: int
    measures: dict[str, float]
    failed: list[str]  # `.meas` names ngspice reported as failed
    fatal: list[str]  # log lines that make the run a failure whatever rc says
    # The deck AS RUN — after any save-list rewrite. It is what `deck` on disk holds and what
    # the run dir's hash is taken over, so a ledger row's deck hash must be computed from this,
    # never from the text the caller passed in.
    deck_text: str = ""

    @property
    def raw(self) -> Path | None:
        return self.raws[0] if self.raws else None

    @property
    def ok(self) -> bool:
        return self.rc == 0 and not self.fatal

    def __fspath__(self) -> str:
        return str(self.dir)

    def __str__(self) -> str:
        return str(self.dir)

    def text(self) -> str:
        return self.log.read_text(errors="replace")


def slug(s: str) -> str:
    """A label as a directory-name fragment (anything but ``[A-Za-z0-9_.-]`` becomes ``_``)."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s)


def deck_digest(deck: str, n: int = 8) -> str:
    """The first ``n`` hex digits of sha256 over the deck text."""
    return hashlib.sha256(deck.encode()).hexdigest()[:n]


def _tail(s: str, n: int = 30) -> str:
    return "\n".join([ln for ln in s.splitlines() if ln.strip()][-n:])


def _marker_alive(text: str, age_s: float, timeout: float) -> bool:
    """Whether a ``.busy`` marker (``<pid> [<hostname>]``) still guards a live run."""
    parts = text.split()
    try:
        pid = int(parts[0]) if parts else 0
    except ValueError:
        return False  # unparsable = stale
    if pid <= 0:
        return False  # never `kill(0, …)` (our own process group) or a negative group
    host = parts[1] if len(parts) > 1 else socket.gethostname()
    if host != socket.gethostname():
        return age_s < timeout  # no local kill can vouch for it: alive until it has aged out
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:  # PermissionError: another user's live process — alive
        return True
    return True


def _claim(busy: Path, name: str, timeout: float) -> None:
    """Create the ``.busy`` marker exclusively; reclaim it once if its owner is gone."""
    for attempt in (0, 1):
        try:
            fd = os.open(busy, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, f"{os.getpid()} {socket.gethostname()}".encode())
            finally:
                os.close(fd)
            return
        except FileExistsError:
            try:
                text = busy.read_text(errors="replace")
                age = time.time() - busy.stat().st_mtime
            except OSError:  # released between the open and the read
                continue
            if _marker_alive(text, age, timeout) or attempt:
                break
            busy.unlink(missing_ok=True)
    # reached only by a marker that stayed alive or kept reappearing: never run unlocked
    raise DeckRunError(f"{name} is busy (another run of the same deck is in progress)")


def _text(x: str | bytes | None) -> str:
    return x.decode(errors="replace") if isinstance(x, bytes) else (x or "")


def run_deck(
    deck: str,
    *,
    label: str,
    workdir: str | os.PathLike[str],
    spiceinit: str | None = None,
    ngspice: str | None = None,
    timeout: float = 3600.0,
    extra_files: Mapping[str, str] | None = None,
    env: Mapping[str, str] | None = None,
    save_list: SaveList | None = None,
    bench: str | None = None,
) -> RunResult:
    """Simulate ``deck`` (its own ``.control``: ``write <x>.raw`` and/or ``print``/``meas``)
    in ``<workdir>/<label>-<hash>/`` and read the result back.

    ``spiceinit`` is the text written to the run dir's ``.spiceinit`` (``None`` writes none —
    ngspice then falls back to ``$SPICE_USERINIT_DIR``/``~/.spiceinit``); ``ngspice`` is the
    binary (``None`` = ``ngspice`` on PATH); ``extra_files`` are ``{basename: text}`` written
    beside the deck (an include, a PWL file); ``env`` overlays the process environment.

    ``save_list`` (a :class:`~.save_list.SaveList`) OVERRIDES the deck's own ``.save``/``save``
    statements — see :func:`~.save_list.apply_save_list_to_deck`. It is applied BEFORE the run
    dir's hash is taken, because the rewritten deck genuinely is a different deck: two runs of
    the same source deck under different save lists must not share (and overwrite) one
    directory. ``bench`` names the ``benches:`` entry to look up; it defaults to ``label``.
    ``save_list=None`` leaves the deck byte-identical.
    """
    deck = apply_save_list_to_deck(deck, save_list, bench=bench if bench is not None else label)
    label = slug(label.strip())
    if not label:
        raise ValueError("run label must not be empty")
    for fname in extra_files or {}:
        if fname in ("", ".", "..") or fname != Path(fname).name:
            raise ValueError(f"extra_files key {fname!r} must be a bare file name (no separators)")
        if fname in RESERVED_NAMES:
            raise ValueError(f"extra_files key {fname!r} is one of the run's own files")
    exe = ngspice or shutil.which("ngspice")
    if not exe or not Path(exe).is_file():
        raise FileNotFoundError(
            f"no ngspice binary: {ngspice!r} is not a file and none is on PATH"
            if ngspice
            else "no ngspice binary on PATH (pass ngspice=<path>)"
        )
    name = f"{label}-{deck_digest(deck)}"
    rd = Path(workdir) / name
    rd.mkdir(parents=True, exist_ok=True)
    busy = rd / BUSY_NAME
    _claim(busy, name, timeout)
    try:
        for stale in rd.glob("*.raw"):
            stale.unlink()
        if spiceinit is not None:
            (rd / SPICEINIT_NAME).write_text(spiceinit)
        else:
            (rd / SPICEINIT_NAME).unlink(missing_ok=True)
        (rd / DECK_NAME).write_text(deck)
        for fname, text in (extra_files or {}).items():
            (rd / fname).write_text(text)
        run_env = dict(os.environ)
        if env:
            run_env.update(env)
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                [exe, "-b", DECK_NAME],
                cwd=rd,
                env=run_env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:  # keep what it printed before the kill
            partial = _text(exc.stdout) + "\n---- stderr ----\n" + _text(exc.stderr)
            (rd / LOG_NAME).write_text(partial + f"\n---- timed out after {timeout:g} s ----\n")
            raise DeckRunError(f"{name}: ngspice timed out after {timeout:g} s") from None
        wall = time.perf_counter() - t0
        log_text = proc.stdout + "\n---- stderr ----\n" + proc.stderr
        (rd / LOG_NAME).write_text(log_text)
        (rd / WALL_NAME).write_text(f"{wall:.3f}\n")
        # a body `.meas` (batch mode, no .control) reports on stderr: parse the whole log
        measures, failed = parse_measures(log_text)
        result = RunResult(
            label=label,
            dir=rd,
            deck=rd / DECK_NAME,
            log=rd / LOG_NAME,
            raws=sorted(rd.glob("*.raw")),
            wall=wall,
            rc=proc.returncode,
            measures=measures,
            failed=failed,
            fatal=fatal_lines(log_text),
            deck_text=deck,
        )
    finally:
        busy.unlink(missing_ok=True)
    if result.fatal:
        raise DeckRunError(f"{name}: simulator error\n  " + "\n  ".join(result.fatal[:8]), result)
    if proc.returncode != 0:
        raise DeckRunError(
            f"{name}: ngspice exited rc={proc.returncode}\n{_tail(log_text)}", result
        )
    return result
