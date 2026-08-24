"""Cached YAML reading — the corpus is read far more often than it changes.

Profiling the verify tiers showed ~90% of a corpus sweep spent inside pyyaml's
pure-Python scanner, re-parsing the same committed YAML files once per
(analysis x pdk x corner) render. Every loader in this package funnels through
:func:`read_yaml`, which

- parses with libyaml's ``CSafeLoader`` when the extension is available
  (same safe-tag semantics as ``yaml.safe_load``, ~10x faster), and
- memoizes the parsed document keyed by ``(path, mtime_ns, size)``, returning a
  deep copy so callers may mutate their view freely.

A rewritten file (new mtime/size) misses the cache and re-parses, so
correctness never depends on an invalidation hook — authoring flows that write
YAML (``new-circuit``, ``add-binding``) are covered automatically.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

# CSafeLoader == SafeLoader semantics (safe tags only); pure-Python fallback
# keeps environments without libyaml working, just slower.
_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

_cache: dict[str, tuple[int, int, Any]] = {}


def parse_yaml(text: str) -> Any:
    """Uncached ``safe_load`` of a YAML string with the fast loader."""
    return yaml.load(text, Loader=_LOADER)


def read_yaml(path: str | Path) -> Any:
    """Parse the YAML file at ``path``, memoized on (mtime_ns, size).

    Returns a deep copy of the cached document; raises the same
    ``yaml.YAMLError`` / ``OSError`` a plain open+``safe_load`` would.
    """
    p = Path(path)
    st = p.stat()
    key = str(p)
    hit = _cache.get(key)
    if hit is not None and hit[0] == st.st_mtime_ns and hit[1] == st.st_size:
        return copy.deepcopy(hit[2])
    doc = parse_yaml(p.read_text())
    _cache[key] = (st.st_mtime_ns, st.st_size, doc)
    return copy.deepcopy(doc)
