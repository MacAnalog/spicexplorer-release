"""No tracked ``.html``/``.htm`` or ``.ipynb`` file.

Owner ruling 2026-10-09: the repositories store no HTML pages and no Jupyter notebooks. A notebook
is kept as Python (marimo, or jupytext percent format via ``uvx jupytext --to py:percent``), and a
recorded run is kept as a Python script that prints the record (the case study's
``*_recorded_outputs.py``). Executed notebooks and HTML exports are megabytes of embedded output, and
they made GitHub classify the public release repository as HTML.

A file that must stay (a vendored asset, a test fixture) goes into ``_ALLOWED`` with its reason.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from spicexplorer_analog_db import paths

_BANNED_SUFFIXES = frozenset({".html", ".htm", ".ipynb"})
# repo-relative POSIX path -> why it must stay; empty: nothing needs an exception today
_ALLOWED: dict[str, str] = {}


def _tracked_files(root: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip(f"{root} is not a git checkout: the guard reads the tracked file list")
    return [rel for rel in out.decode().split("\0") if rel]


def banned(rels: list[str], allowed: dict[str, str]) -> list[str]:
    """The paths in ``rels`` with a banned suffix that ``allowed`` does not list."""
    return [r for r in rels if Path(r).suffix.lower() in _BANNED_SUFFIXES and r not in allowed]


def test_no_tracked_html_or_ipynb():
    root = paths.db_root()
    # a file deleted in the working tree but not yet committed is on its way out
    found = [r for r in banned(_tracked_files(root), _ALLOWED) if (root / r).is_file()]
    assert not found, (
        f"{len(found)} tracked .html/.ipynb file(s). Store a notebook as Python (marimo or "
        "`uvx jupytext --to py:percent`) and a recorded run as a script that prints it, or list "
        "the file in _ALLOWED with its reason:\n  " + "\n  ".join(found)
    )


def test_every_allowed_entry_is_still_tracked():
    """A stale allowlist entry would silently allow the path again if it came back."""
    tracked = set(_tracked_files(paths.db_root()))
    assert not [r for r in _ALLOWED if r not in tracked]


def test_banned_matches_each_suffix_in_any_case():
    rels = ["a/b.html", "c.HTM", "nb/run.ipynb", "x.py", "y.json", "notes.md", "keep.html"]
    assert banned(rels, {"keep.html": "fixture"}) == ["a/b.html", "c.HTM", "nb/run.ipynb"]
