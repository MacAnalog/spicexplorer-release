"""No tracked text file names a user's home or scratch directory.

**ADB-HOME-SCRUB** (owner ruling 2026-09-26): analog-db is a release candidate, and an absolute
``/home/<name>/``, ``/scratch/<name>/`` or ``/Users/<name>/`` in a committed run record, log or
provenance line publishes the account that produced it. So do the network and mount roots
``/nfs/<name>/`` and ``/mnt/<name>/``, and the home root under a mount prefix
(``/nfs/home/<name>/``, ``/mnt/home/<name>/``, ``/export/home/<name>/``), whether written plainly,
after an ANSI colour sequence, or with JSON-escaped slashes (L-ADB-2). The records name those
roots in the neutral ``/home/<user>/`` form (``/home/&lt;user&gt;/`` inside SVG text, where a bare
``<`` breaks the XML), and a runnable script builds its default from ``$HOME`` / ``~``. Any other
name fails this guard, which lists each file with its first offending line.

A fixture that must name one carries a reasoned marker, in the syntax of the meta-repo's
``pdk_guard.py`` under the tag ``home-path-guard``: ``allow <reason>`` on the line itself, or
``allow-file <reason>`` anywhere in the file. A marker without a reason is itself a failure. (This
docstring spells the marker in parts so that it does not allow this file.)
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from spicexplorer_analog_db import paths

_TAG = "home-path-guard"
# A root directory followed by a concrete account name. A placeholder starts with a character a
# name cannot (``<user>``, ``&lt;user&gt;``, ``...``, ``$USER``), and a ``/home/`` that follows a
# path character (``/tmp/home/``, ``./home/``, a URL path) is not an absolute root. A shell default
# (``${VAR:-/home/<name>/...}``) is one, so ``-`` does not end a match's left edge. So is a root
# after a JSON or Python-repr escape (``"boom\n/home/<name>/..."`` in a recorded log): the escape's
# last character is a word character, so each escape shape is its own left edge. So is a root
# joined to a compiler/linker flag (``-I/home/<name>``, ``-isystem/home/<name>``): a ``-`` that
# starts a token, then letters. A ``-`` inside a name (``sx-scratch/home/``) starts no flag.
# The roots: ``/home``, ``/scratch``, ``/Users``, ``/nfs`` and ``/mnt``, and ``/home`` under a
# ``/nfs``, ``/mnt`` or ``/export`` prefix. ``/nfs`` and ``/mnt`` do not match when ``/home`` follows
# them, so the neutral ``/nfs/home/<user>/`` is no hit through ``home`` read as the account name.
_NAMED_ROOT = re.compile(
    r"(?:(?<=\\[bfnrt])|(?<=\\u[0-9A-Fa-f]{4})|(?<=\\x[0-9A-Fa-f]{2})|(?<![\w.$~])"
    r"|(?<![\w.$~/-])-[A-Za-z]+)"
    r"/(?:(?:nfs/|mnt/|export/)?home|scratch|Users|nfs(?!/home\b)|mnt(?!/home\b))"
    r"/[A-Za-z0-9_][A-Za-z0-9_.-]*"
)
# Before the match, each line is normalised. An ANSI escape sequence (colour in a recorded log; raw
# ESC or its ``\x1b``, ``\u001b``, ``\033``, ``\e`` spelling) becomes a space: its last character
# is a letter, and deleting it would join the root to the text before the sequence. A JSON-escaped
# slash (``\/``, ``\u002f``) becomes ``/``.
_ANSI = re.compile(r"(?:\x1b|\\x1[bB]|\\u001[bB]|\\033|\\e)\[[0-9;]*[A-Za-z]")
_JSON_SLASH = re.compile(r"\\/|\\u002[fF]")
_MARKER = re.compile(re.escape(_TAG) + r":\s*allow(?P<file>-file)?\b[ \t:—-]*(?P<reason>.*)")
# the byte prefilter: ``\/home\/<name>`` and ``\u002fhome`` hold no ``/home/`` bytes
_NEEDLES = (
    b"/home/",
    b"/scratch/",
    b"/Users/",
    b"/nfs/",
    b"/mnt/",
    b"\\/",
    b"\\u002",
    _TAG.encode(),
)


def _scan(text: str) -> tuple[list[str], list[str]]:
    """``(hits, markers_without_reason)`` for one file's text: each line naming a home or scratch
    root that no marker allows. An ``allow-file`` marker with a reason clears the whole file."""
    hits: list[str] = []
    bad: list[str] = []
    file_allowed = False
    for n, line in enumerate(text.splitlines(), 1):
        marker = _MARKER.search(line)
        if marker:
            if not marker["reason"].strip():
                bad.append(f"{n}: {line.strip()}")
                continue
            if marker["file"]:
                file_allowed = True
            continue
        if _NAMED_ROOT.search(_JSON_SLASH.sub("/", _ANSI.sub(" ", line))):
            hits.append(f"{n}: {line.strip()[:160]}")
    return ([] if file_allowed else hits), bad


def _is_text(data: bytes) -> bool:
    return b"\0" not in data[:8000]


def _candidate(data: bytes) -> bool:
    """A file the sweep reads line by line: text that holds a needle. The byte test runs on every
    tracked file, so it keeps the sweep to the files that can hold a hit."""
    return _is_text(data) and any(needle in data for needle in _NEEDLES)


def _tracked_files(root: Path) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip(f"{root} is not a git checkout: the guard reads the tracked file list")
    return [root / rel for rel in out.decode().split("\0") if rel]


def test_no_tracked_text_file_names_a_home_or_scratch_directory():
    root = paths.db_root()
    leaks: list[str] = []
    for path in _tracked_files(root):
        if not path.is_file():  # tracked, but deleted in the working tree
            continue
        data = path.read_bytes()
        if not _candidate(data):
            continue
        hits, bad = _scan(data.decode("utf-8", errors="replace"))
        rel = path.relative_to(root).as_posix()
        leaks += [f"{rel}:{hit}" for hit in hits[:1]]
        leaks += [f"{rel}:{line}  (marker without a reason)" for line in bad]
    assert not leaks, (
        f"{len(leaks)} tracked file(s) name a home or scratch directory. Write /home/<user>/ in a "
        f"record and $HOME in a script, or mark a fixture '{_TAG}: allow <reason>':\n  "
        + "\n  ".join(leaks)
    )


_LEAK = "/home/alice/work/deck.spice"  # home-path-guard: allow the guard's own leak fixture


@pytest.mark.parametrize(
    "line",
    [
        f"** sch_path: {_LEAK}",
        f'include "{_LEAK}" section=tt',
        f'export MODEL_ROOT="${{MODEL_ROOT:-{_LEAK}}}"',
        f'"log": "  File \\"{_LEAK}\\", line 26"',
        _LEAK.replace("/home/", "/scratch/"),
        _LEAK.replace("/home/", "/Users/"),
        _LEAK.rsplit("/", 2)[0],
        json.dumps({"log": "boom\n" + _LEAK}),
        json.dumps({"why": "exit 1\r\n\t" + _LEAK}),
        json.dumps({"log": "\x1b" + _LEAK}),
        repr("stderr:\n" + _LEAK),
        repr("\x07" + _LEAK),
        f"-I{_LEAK}",
        f"gcc -c -I{_LEAK} -L{_LEAK} deck.c",
        f'CFLAGS="-isystem{_LEAK}"',
        f"LDFLAGS=-Wl,-L{_LEAK}",
        # L-ADB-2: network and mount roots, and the home root under a mount prefix
        _LEAK.replace("/home/", "/nfs/"),
        _LEAK.replace("/home/", "/mnt/"),
        "/nfs" + _LEAK,
        "/mnt" + _LEAK,
        "/export" + _LEAK,
        f'include "/nfs{_LEAK}" section=tt',
        # L-ADB-2: a root right after an ANSI colour sequence, raw or in an escaped spelling
        "\x1b[31m" + _LEAK + "\x1b[0m",
        "error: \x1b[1;31m" + _LEAK,
        json.dumps({"log": "boom\x1b[0m" + _LEAK}),
        repr("\x1b[33m" + _LEAK),
        "\\033[0m" + _LEAK,
        "\\e[1m" + _LEAK,
        # L-ADB-2: JSON-escaped slashes (``\/``, ``\u002f``), which some JSON writers emit
        _LEAK.replace("/", "\\/"),
        json.dumps({"path": _LEAK}).replace("/", "\\/"),
        _LEAK.replace("/", "\\u002f"),
        ("/nfs" + _LEAK).replace("/", "\\/"),
    ],
)
def test_a_named_home_or_scratch_directory_is_a_hit(line):
    assert _scan(line) == ([f"1: {line}"], [])


@pytest.mark.parametrize(
    "line",
    [
        "** sch_path: /home/<user>/work/deck.spice",
        "/scratch/<user>/run/0001_run.scs",
        "tran1: ** sch_path: /home/&lt;user&gt;/work/deck.sch",
        "PATH=/home/.../local/bin:$PATH",
        'export PDK_ROOT="${PDK_ROOT:-$HOME/local/pdks}"',
        "~/.spicexplorer/models",
        "$SX_SCRATCH/ldo-fix/w5/pex_rc/cell_pex.spice",
        "/home/<user>/sx-scratch/alice/run",
        f"https://example.org{_LEAK}",
        f"/tmp{_LEAK}",
        "under /home/ and /scratch/ roots",
        json.dumps({"log": "boom\n/home/<user>/work/deck.spice"}),
        "gcc -I/home/<user>/include -L$HOME/lib deck.c",
        f"sx-scratch{_LEAK}",
        f"run-a{_LEAK}",
        # L-ADB-2: the neutral forms of the wider roots, and non-root spellings of them
        "/nfs/home/<user>/work/deck.spice",
        "/mnt/home/<user>/work/deck.spice",
        "/export/home/<user>/work/deck.spice",
        "/nfs/<user>/run",
        "/mnt/<user>/run",
        "under /nfs/home and /mnt roots",
        "/tmp" + _LEAK.replace("/home/", "/nfs/"),
        "\x1b[31m/home/<user>/work\x1b[0m",
        json.dumps({"log": "\x1b[0m/home/<user>/work"}),
        "\\/home\\/<user>\\/work",
        ("https://example.org" + _LEAK).replace("/", "\\/"),
    ],
)
def test_a_neutral_or_non_root_form_is_not_a_hit(line):
    assert _scan(line) == ([], [])


def test_an_allow_marker_needs_a_reason():
    assert _scan(f"{_LEAK}  # {_TAG}: allow a parser fixture") == ([], [])
    assert _scan(f"# {_TAG}: allow-file a recorded fixture\n{_LEAK}\n{_LEAK}") == ([], [])
    hits, bad = _scan(f"# {_TAG}: allow-file\n{_LEAK}")
    assert hits == [f"2: {_LEAK}"]
    assert bad == [f"1: # {_TAG}: allow-file"]


def test_a_binary_file_is_not_scanned():
    assert not _is_text(b"\x89PNG\r\n\x1a\n\0\0" + _LEAK.encode())
    assert _is_text(_LEAK.encode())


@pytest.mark.parametrize(
    "text",
    [
        _LEAK.replace("/home/", "/nfs/"),
        _LEAK.replace("/home/", "/mnt/"),
        json.dumps({"path": _LEAK}).replace("/", "\\/"),
        _LEAK.replace("/", "\\u002f"),
    ],
)
def test_the_sweep_reads_every_file_a_hit_can_be_in(text):
    """L-ADB-2: the byte prefilter runs before ``_scan``; a hit in a file it skips is never seen.
    ``\\/home\\/<name>`` holds no ``/home/`` bytes, so each needle is checked on its own here."""
    assert _scan(text)[0], text
    assert _candidate(text.encode())
