"""Compute sigmoid vs. linear score penalties for a project's target specs."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
from spicexplorer.core.domains import OptimizationGoalType, Project_Setup, parse_value
from spicexplorer.core.utils import (
    compute_error,
    compute_relative_sigmoid_error,
    log_space_band,
    log_space_range_coeff,
)

# Floor a non-positive metric before the log10 transform of a `log_scale` spec (a swept curve point
# can go <= 0; a real frequency reading never does) — matches core/utils `_LOG_BAND_FLOOR`.
_LOG_FLOOR = 1e-12

logger = logging.getLogger(__name__)


def apply_spec_overrides(
    project: Project_Setup,
    overrides: dict[str, dict] | None,
) -> None:
    """Apply ephemeral, request-scoped target-spec edits to the loaded project.

    Score Shaping lets the user tune spec fields (target/tolerance/weight/range/
    goal/enable) for a *what-if* preview. Because /api/score reloads the project
    from disk every call (stateless), these edits travel in the request payload and
    are applied here to the freshly-loaded, in-memory project before scoring. This
    **never** rewrites the YAML — the edits vanish with the request, exactly the
    ephemeral semantics the UI promises.

    `overrides` maps spec name → a partial dict of fields to set. Numeric fields
    accept engineering strings ("250u") via parse_value. Unknown spec names and
    unknown goal values are ignored (rather than 500-ing a preview).
    """
    if not overrides:
        return
    by_name = {s.name: s for s in project.optimizer_config.target_specs.targets}
    for name, patch in overrides.items():
        spec = by_name.get(name)
        if spec is None or not isinstance(patch, dict):
            continue
        for field in ("target", "tolerance", "weight", "range"):
            if field in patch and patch[field] is not None and patch[field] != "":
                try:
                    setattr(spec, field, float(parse_value(patch[field])))
                except (ValueError, TypeError):
                    logger.warning("score override: bad %s for spec '%s': %r",
                                   field, name, patch[field])
        if "enable" in patch and patch["enable"] is not None:
            spec.enable = bool(patch["enable"])
        if patch.get("goal"):
            try:
                spec.goal = OptimizationGoalType(str(patch["goal"]).lower())
            except ValueError:
                logger.warning("score override: unknown goal for spec '%s': %r",
                               name, patch["goal"])


def _resolve_penalty_space(value: float, spec: Any) -> tuple[float, float, float, float]:
    """Return ``(curr, target, tolerance, coeff)`` in the SPACE the optimizer scores this spec in.

    For a ``log_scale`` spec the optimizer works in DECADES (``compute_constraint_violation_penalty_for_spec``
    transforms value/target/tolerance via :func:`log_space_band` and normalizes by
    :func:`log_space_range_coeff`), so the preview must too — otherwise a GBW-type constraint that the
    run scores in decades is previewed against the raw linear range and the "what-if" number is off by
    orders of magnitude (SC-4). Linear specs pass through unchanged. ``value`` may be a metric reading
    or a swept curve point (which can go ``<= 0`` — floored before ``log10``)."""
    target = float(spec.target)
    # `is not None`, NOT falsy: an explicit `tolerance: 0` is a real zero-width band, and a
    # falsy test silently turned it into 5 % of target here while the scorer did the same — so
    # preview and run agreed on the WRONG number. Both fixed together (SC-4 keeps them one).
    tolerance = float(spec.tolerance) if spec.tolerance is not None else 0.0
    rang = float(spec.range) if spec.range and spec.range > 0 else max(abs(target), 1.0)
    if getattr(spec, "log_scale", False) and target > 0:
        coeff = float(log_space_range_coeff(target, rang))
        c, t, tol = log_space_band(value if value > 0 else _LOG_FLOOR, target, tolerance)
        return float(c), float(t), float(tol), coeff
    return float(value), target, tolerance, rang


def _spec_penalties(value: float, spec: Any) -> tuple[float, float, bool]:
    """``(linear, sigmoid, passes)`` for one metric value, computed EXACTLY as the run scores it.

    ``linear`` is the penalty under the spec's own ``error_type`` (via the shared
    :func:`compute_error` kernel) — i.e. *what the optimizer minimizes* — and equals the historical
    relative-absolute number for the default error type, so the common case is unchanged.
    ``sigmoid`` keeps the bounded relative-sigmoid shaping the UI compares against. Both are measured
    from the tolerance-adjusted target edge and normalized in the resolved (decade-for-log) space, so
    the preview matches the run for ``log_scale`` and non-default ``error_type`` specs alike
    (review §1.21 / SC-4). ``(0, 0, True)`` when the constraint is met."""
    curr, target, tol, coeff = _resolve_penalty_space(value, spec)
    if spec.goal == OptimizationGoalType.EXCEED:
        violated, adjusted = curr < target - tol, target - tol
    elif spec.goal == OptimizationGoalType.MINIMIZE:
        violated, adjusted = curr > target + tol, target + tol
    else:  # EXACT
        violated = abs(curr - target) > tol
        adjusted = target - tol if curr < target else target + tol
    if not violated:
        return 0.0, 0.0, True
    c = np.float64(coeff)
    cur = np.float64(curr)
    adj = np.float64(adjusted)
    linear_p = float(compute_error(cur, adj, spec.error_type, c))
    sigmoid_p = float(compute_relative_sigmoid_error(cur, adj, c))
    return linear_p, sigmoid_p, False


def compute_score(
    project: Project_Setup,
    metric_values: dict[str, float],
    selected_spec: str | None = None,
    n_curve_points: int = 200,
) -> dict[str, Any]:
    """
    Compute per-spec linear and sigmoid penalties for the given metric values.

    Returns per_spec penalties, aggregate scores, and a curve for the selected_spec.
    """
    specs = project.optimizer_config.target_specs.enabled_targets()

    per_spec: dict[str, Any] = {}
    total_linear = 0.0
    total_sigmoid = 0.0

    for spec in specs:
        value = metric_values.get(spec.name)
        target = float(spec.target)
        tolerance = float(spec.tolerance) if spec.tolerance is not None else 0.0
        weight = float(spec.weight) if spec.weight is not None else 1.0
        # (the per-spec `range` normalizer is resolved inside `_spec_penalties`/`_resolve_penalty_space`)

        if value is None:
            # Emit `tolerance` here too (it's already resolved above) so every per_spec
            # entry carries the same key set — the value-present branch below includes it,
            # and a uniform shape lets the response_model type `tolerance` as a required
            # float (matching the UI's SpecScore.tolerance) instead of conditionally absent.
            per_spec[spec.name] = {
                "linear": None, "sigmoid": None,
                "value": None, "target": target, "tolerance": tolerance,
                "goal": spec.goal.value, "passes": None, "weight": weight,
            }
            continue

        # Penalties honoring the spec's error_type + log_scale, exactly as the run scores it (SC-4).
        linear_p, sigmoid_p, passes = _spec_penalties(float(value), spec)

        per_spec[spec.name] = {
            "linear": linear_p,
            "sigmoid": sigmoid_p,
            "value": float(value),
            "target": target,
            "tolerance": tolerance,
            "goal": spec.goal.value,
            "passes": passes,
            "weight": weight,
        }
        total_linear += weight * linear_p
        total_sigmoid += weight * sigmoid_p

    # Build penalty curve for selected spec (used by PenaltyCurveChart)
    curve: dict[str, Any] | None = None
    if selected_spec:
        spec_obj = next((s for s in specs if s.name == selected_spec), None)
        if spec_obj:
            target = float(spec_obj.target)
            tolerance = float(spec_obj.tolerance) if spec_obj.tolerance is not None else 0.0
            rang = float(spec_obj.range) if spec_obj.range and spec_obj.range > 0 else max(abs(target), 1.0)
            lo = target - 3 * rang
            hi = target + 3 * rang
            xs = np.linspace(lo, hi, n_curve_points).tolist()
            linears, sigmoids = [], []
            for x in xs:
                lin_p, sig_p, _ = _spec_penalties(x, spec_obj)
                linears.append(lin_p)
                sigmoids.append(sig_p)
            curve = {"values": xs, "linear": linears, "sigmoid": sigmoids,
                     "target": target, "tolerance": tolerance, "goal": spec_obj.goal.value}

    return {
        "per_spec": per_spec,
        # F(x) = Σ wᵢ · P̂ᵢ — the non-negative weighted penalty sum the UI header and the
        # per-spec columns show. Do NOT negate here: the optimizer's maximize-score
        # convention lives in the library scorer, not this preview service; negating made
        # the footer print a negative number under its own "sum of penalties" label.
        "aggregate": {"linear": total_linear, "sigmoid": total_sigmoid},
        "curve": curve,
    }
