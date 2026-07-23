"""Engineering-string parsing — the shared numeric value parser.

Moved out of the optimizer's DSL module (``core/domains.py``) so every package —
the spice engine, future tools, the API — can parse engineering strings without
importing the optimizer. It is re-exported from ``spicexplorer.core.domains`` for
backward compatibility, so existing ``from spicexplorer.core.domains import
parse_value`` call sites keep working unchanged.
"""

from __future__ import annotations

from typing import Dict, Union

import numpy as np

# ------------------ Constants ------------------

MULTIPLIERS = {
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
}

# ------------------ Helpers ------------------


def parse_value(val: Union[str, float, int]) -> np.float64:
    """
    Parse numeric values with optional suffix multipliers.
    Parses a string like '0.18u', '10u', '1.8', '5MEG', or a number into np.float64.
    Single-char suffixes ('f' 'p' 'n' 'u' 'm' 'k' 'M' 'G') are case-SENSITIVE — 'm' is milli and
    'M' is mega — while ngspice's multi-char mega spelling 'meg' is case-INSENSITIVE
    ('MEG'/'meg'/'Meg' all → 1e6).
    """
    if isinstance(val, (float, int)):
        return np.float64(val)
    if val is None:
        # A present-but-empty YAML key (e.g. `temp:` / supply `value:`) reaches here as None;
        # raise a descriptive error instead of an opaque AttributeError on `None.lower()` (BUG-B18).
        raise ValueError("parse_value received None (a YAML key was present but had no value)")
    if val.lower() == "inf":
        return np.float64(np.inf)

    val = val.strip()

    # Longest-suffix-first: match ngspice's multi-char 'meg' (case-insensitive — real netlists use
    # both '10meg' and '100MEG' for mega) BEFORE the single-char table. Otherwise '5MEG' strips one
    # char to float('5ME') and '5meg' falls through to float('5meg'), both raising — the reported
    # crash. The single-char table below keeps this DSL's documented case-sensitive convention
    # ('m'=milli vs 'M'=mega); an unlisted case like 'U'/'K' still raises rather than guessing.
    if val.lower().endswith("meg"):
        return np.float64(float(val[:-3]) * 1e6)
    for suffix, factor in MULTIPLIERS.items():
        if val.endswith(suffix):
            return np.float64(float(val[:-1]) * factor)
    return np.float64(float(val))


def resolve_reference(
    value: Union[str, float, int], constraints: Dict[str, np.float64 | float]
) -> np.float64:
    """If value is a reference to a constraint key, resolve it, else parse normally."""
    if isinstance(value, str) and value in constraints:
        return np.float64(constraints[value])
    return parse_value(value)
