"""Locate the SpiceXplorer workspace root in a layout-independent way.

The monolith located the repo root by climbing a hard-coded number of parent
directories (``Path(__file__).parents[3]``, ``parent.parent.parent`` …). There
were **four** such walks and they disagreed; any change to directory depth —
exactly what the modularization does — silently broke them.

``project_root()`` replaces all four with a single marker/env-anchored lookup:

1. ``$SPICEXPLORER_ROOT`` if set (used in containers, e.g. ``/app``);
2. otherwise walk up from this module to the first directory containing the
   ``.spicexplorer-root`` sentinel (falling back to a ``.git`` directory).

It is independent of the current working directory and of how deeply any caller
is nested, so it survives every package move in the migration.

Note on the ``.git`` fallback: the sentinel is checked first at *every* level, so
a closer ``.spicexplorer-root`` always wins over a ``.git`` higher up — a nested
checkout's closer sentinel wins over an outer ``.git``.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

#: Marker names that identify the workspace root, in priority order.
_ROOT_MARKERS: tuple[str, ...] = (".spicexplorer-root", ".git")

#: Environment variable that overrides marker discovery (set in containers).
ROOT_ENV_VAR = "SPICEXPLORER_ROOT"


def _find_root(start: Path) -> Path:
    override = os.environ.get(ROOT_ENV_VAR)
    if override:
        root = Path(override).expanduser().resolve()
        if not root.is_dir():
            raise RuntimeError(
                f"{ROOT_ENV_VAR}={override!r} does not point to a directory"
            )
        return root

    start = start.resolve()
    for candidate in (start, *start.parents):
        if any((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate

    raise RuntimeError(
        "Could not locate the SpiceXplorer workspace root: no "
        f"{_ROOT_MARKERS} marker found at or above {start}, and "
        f"{ROOT_ENV_VAR} is unset."
    )


@lru_cache(maxsize=1)
def project_root() -> Path:
    """Return the absolute path of the SpiceXplorer workspace root."""
    return _find_root(Path(__file__))


def clear_cache() -> None:
    """Reset the cached root (for tests that manipulate ``$SPICEXPLORER_ROOT``)."""
    project_root.cache_clear()
