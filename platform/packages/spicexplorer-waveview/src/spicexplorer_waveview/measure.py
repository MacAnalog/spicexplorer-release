"""Run Tier-1 registry measurements against a loaded :class:`WaveDataset`.

Thin bridge to :mod:`spicexplorer_core.measurements.registry`: the dataset goes behind
the ``SimResult`` protocol (:class:`~spicexplorer_waveview.dataset.DatasetResult`) and
any ``{meas: …}`` recipe the optimizer accepts evaluates on viewer-loaded data with the
identical math. Nothing is re-implemented here — requirement #1 (every measurement type
the core supports) holds by construction.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from spicexplorer_core.measurements.registry import (
    kind_default_analysis,
    measure,
    measurement_table,
    validate_recipe,
)

from .dataset import DatasetResult, WaveDataset

__all__ = ["measurement_catalog", "measure_dataset", "measure_many"]


def measurement_catalog() -> dict[str, dict[str, Any]]:
    """Every canonical measurement → ``{kind, required, default_analysis}``.

    The viewer/UI's discovery surface: which recipes exist, which args each needs, and
    which analysis it reads by default — straight from the core registry's table.
    """
    defaults = kind_default_analysis()
    return {
        name: {
            "kind": kind,
            "required": list(required),
            "default_analysis": defaults.get(kind, kind),
        }
        for name, (kind, required) in sorted(measurement_table().items())
    }


def measure_dataset(
    dataset: WaveDataset, recipe: dict[str, Any], *, name: str | None = None
) -> float:
    """Evaluate one ``{meas: …}`` recipe against a loaded dataset → a scalar.

    Validates the recipe first (unknown measurement / missing args raise ``ValueError``
    with the registry's own message), then runs the registry math over the dataset's
    ``SimResult`` adapter. Missing signals raise ``KeyError`` (a wave is a hard request,
    matching engine semantics); callers that prefer NaN degrade catch it.
    """
    label = name or str(recipe.get("meas", "measurement"))
    validate_recipe(label, recipe)
    kind, _required = measurement_table()[str(recipe["meas"]).strip()]
    default_analysis = kind_default_analysis().get(kind, "ac")
    return float(measure(DatasetResult(dataset), recipe, default_analysis=default_analysis))


def measure_many(
    dataset: WaveDataset, recipes: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Evaluate several named recipes; failures degrade per-item, never in bulk.

    Returns ``{name: {"value": float|None, "error": str|None}}`` — a NaN/inf value is
    reported as ``value=None`` with the reason in ``error`` (JSON-safe by construction).
    """
    out: dict[str, dict[str, Any]] = {}
    for name, recipe in recipes.items():
        try:
            value = measure_dataset(dataset, recipe, name=name)
        except (ValueError, KeyError, TypeError) as exc:
            # TypeError included: validate_recipe checks arg PRESENCE only, so a
            # null/list arg value survives to the registry's float()/int() casts —
            # one malformed item must degrade, not kill the batch.
            out[name] = {"value": None, "error": str(exc)}
            continue
        if not np.isfinite(value):
            out[name] = {"value": None, "error": f"non-finite result ({value})"}
        else:
            out[name] = {"value": value, "error": None}
    return out
