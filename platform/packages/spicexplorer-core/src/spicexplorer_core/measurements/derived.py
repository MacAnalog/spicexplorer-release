"""Parameter-derived metrics: figures of merit computed from the *candidate sizing*, not
from a simulation.

The Tier-1 registry (``registry.py``) reads scalars/waves off a ``SimResult`` — a sim has
to run first. Some datasheet figures are instead a closed-form function of the design
variables themselves, so they can (and should) be scored with **no** extra simulation. The
canonical one is **active area** ``Σ Wᵢ·Lᵢ·mᵢ`` (the summed gate area of the sized
devices, an ``m``-multiplier-aware silicon-cost proxy).

A ``TargetSpec.measurement`` recipe of the form ``{derived: <name>, ...args}`` names one of
these. The math lives here (pure Python, no numpy/simulator dependency) so it is engine- and
optimizer-agnostic and unit-testable in isolation; the optimizer wiring that feeds it the
candidate parameterization and merges the scalar into the performance map lives in
:mod:`spicexplorer.optimization.derived_integration` — the param-derived twin of
:mod:`spicexplorer.optimization.measure_integration`.

Layering: ``spicexplorer-core`` beside the measurement registry — no upward dependency.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

__all__ = ["known_derived", "validate_derived_recipe", "compute_derived", "active_area"]


# Canonical derived-metric name → required recipe keys (checked at project load, before any
# simulation, so a typo fails loudly and early — symmetric with registry.validate_recipe).
# `active_area` has NO required key: with an explicit `devices:` list it sums those terms
# (legacy, engine-agnostic — this module); with the list omitted it is computed by the
# **recursive netlist walk** in :mod:`spicexplorer_core.measurements.area` (the optimizer feeds
# it the deck), which cannot silently drop a device or its multiplier the way a hand list can.
_DERIVED_TABLE: Dict[str, tuple[str, ...]] = {
    "active_area": (),
}


def known_derived() -> tuple[str, ...]:
    """The canonical derived-metric names accepted in a ``{derived: …}`` recipe."""
    return tuple(sorted(_DERIVED_TABLE))


def _resolve(token: Any, params: Mapping[str, float]) -> float:
    """A device-term field is either a param NAME (resolved from the candidate sizing) or a
    literal number (a frozen/constant geometry, e.g. a fixed ``m`` or ``L``)."""
    if isinstance(token, str):
        if token not in params:
            raise KeyError(
                f"derived metric references param {token!r} not present in the "
                f"parameterization ({sorted(params)})"
            )
        return float(params[token])
    return float(token)


def active_area(recipe: Dict[str, Any], params: Mapping[str, float]) -> float:
    """``scale · Σ Wᵢ·Lᵢ·mᵢ`` over ``recipe['devices']``.

    Each device term is a mapping ``{w, l, m?}`` whose fields are each a param name (looked
    up in ``params``) or a literal number; ``m`` defaults to 1. ``scale`` (default 1.0) lets
    a recipe report in µm² or add a fixed overhead factor. Deterministic and sim-free."""
    devices = recipe["devices"]
    if not isinstance(devices, (list, tuple)) or not devices:
        raise ValueError("active_area: `devices` must be a non-empty list of {w, l, m?} terms.")
    scale = float(recipe.get("scale", 1.0))
    total = 0.0
    for term in devices:
        if not isinstance(term, Mapping) or "w" not in term or "l" not in term:
            raise ValueError(
                f"active_area: each device term needs `w` and `l` (got {term!r})."
            )
        w = _resolve(term["w"], params)
        length = _resolve(term["l"], params)
        m = _resolve(term.get("m", 1.0), params)
        total += w * length * m
    return scale * total


# name → callable(recipe, params) -> float
_DERIVED_FN: Dict[str, Any] = {
    "active_area": active_area,
}


def validate_derived_recipe(spec_name: str, recipe: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if ``recipe`` names an unknown derived metric or omits a required
    argument. Called at project load (before any sim) so typos fail loudly and early."""
    name = str(recipe.get("derived", "")).strip()
    required = _DERIVED_TABLE.get(name)
    if required is None:
        raise ValueError(
            f"target '{spec_name}': unknown derived metric derived={name!r}; "
            f"valid: {list(known_derived())}."
        )
    missing = [k for k in required if k not in recipe]
    if missing:
        raise ValueError(
            f"target '{spec_name}': derived {name!r} needs {list(required)}; missing {missing}."
        )


def compute_derived(recipe: Dict[str, Any], params: Mapping[str, float]) -> float:
    """Evaluate one ``{derived: …}`` recipe against the candidate ``params`` → a scalar."""
    name = str(recipe["derived"]).strip()
    fn = _DERIVED_FN.get(name)
    if fn is None:
        raise ValueError(f"unknown derived metric {name!r}; valid: {list(known_derived())}.")
    return float(fn(recipe, params))
