"""Small numeric helpers shared across backend services."""
from __future__ import annotations

import math
from typing import Any


def safe_float(v: Any) -> float | None:
    """Coerce to a finite float, or None for non-numeric / NaN / inf inputs."""
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None
