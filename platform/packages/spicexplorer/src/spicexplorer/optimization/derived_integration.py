"""Wire parameter-derived metrics (``{derived: …}``) into the optimizer loop.

The param-derived twin of :mod:`spicexplorer.optimization.measure_integration`. A target
spec whose ``measurement`` recipe is ``{derived: <name>, ...args}`` (see
:class:`spicexplorer.core.domains.TargetSpec` and
:mod:`spicexplorer_core.measurements.derived`) names a figure of merit computed **from the
candidate sizing itself** — e.g. active area ``Σ W·L·m`` — with no simulation. This module
groups those recipes, and on each evaluation computes their scalar from the (denormalized,
frozen-injected) parameterization so the scorer treats them exactly like any sim metric:
``compute_fitness`` sees them in the ``performance_array`` under each spec's ``name`` and
applies the same per-spec normalization (``range``) and reward/penalty aggregation.

Unlike the sim-fed Tier-1/Tier-2 paths this needs no ``SimResult`` at all, so it is fed the
parameterization directly by :meth:`Spice_Constraint_Satisfaction._extract_and_score_current`
(overlaying the sim-read performance map). Built once per run (via :meth:`build`, ``None``
when no target carries a derived recipe) purely to avoid regrouping each evaluation.

Layering: the math lives in ``spicexplorer-core`` (:mod:`spicexplorer_core.measurements.derived`);
this module only groups the recipes and feeds them the candidate params.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional

from spicexplorer_core.measurements import area as _area
from spicexplorer_core.measurements import derived as _derived

if TYPE_CHECKING:
    from spicexplorer.core.domains import ListTargetSpec

logger = logging.getLogger(__name__)


class DerivedMetricContext:
    """Groups the run's ``{derived: …}`` recipes and computes their scalars from the
    candidate parameterization.

    Built once per run (:meth:`build` returns ``None`` when no target carries a derived
    recipe). :meth:`compute` runs each evaluation, before scoring, on the same
    (denormalized, frozen-injected) params the deck was written with — so a derived metric
    is consistent with the design point being scored. Holds no resource (:meth:`close` is a
    no-op) but supports the same close/context-manager contract as the sim-fed contexts so
    the optimizer tears every measurement context down uniformly.
    """

    def __init__(
        self,
        recipes: Dict[str, Dict[str, Any]],
        netlist_path: "Optional[Path]" = None,
    ) -> None:
        self._recipes = recipes  # spec name → validated recipe dict
        # The DUT deck (resolved under ws_root) that netlist-driven recipes are walked over. A
        # recipe with no explicit `devices:` list is scored by the recursive netlist walk, which
        # discovers every transistor + multiplier from the deck itself.
        self._netlist_path = netlist_path

    @classmethod
    def build(
        cls,
        target_specs: "ListTargetSpec",
        netlist_path: "Optional[Path]" = None,
    ) -> "DerivedMetricContext | None":
        recipes: Dict[str, Dict[str, Any]] = {}
        for target in target_specs.enabled_targets():
            if not target.has_derived_measurement():
                continue
            recipe = dict(target.measurement or {})
            _derived.validate_derived_recipe(target.name, recipe)
            recipes[target.name] = recipe
        if not recipes:
            return None
        netlist_driven = [n for n, r in recipes.items() if _is_netlist_driven(r)]
        if netlist_driven and netlist_path is None:
            logger.warning(
                "Netlist-driven derived metric(s) %s have no resolved deck; they will score NaN. "
                "Provide the DUT netlist to DerivedMetricContext.build().",
                sorted(netlist_driven),
            )
        logger.info(
            "Param-derived metric path active for %d spec(s): %s (netlist-driven: %s)",
            len(recipes),
            sorted(recipes),
            sorted(netlist_driven) or "none",
        )
        return cls(recipes, netlist_path=netlist_path)

    @property
    def spec_names(self) -> frozenset[str]:
        return frozenset(self._recipes)

    def compute(self, params: Mapping[str, float]) -> Dict[str, float]:
        """Evaluate every derived recipe against ``params`` → ``{spec_name: value}``. A
        recipe that raises degrades to NaN (→ a scorer penalty) so one bad derived metric
        never crashes the loop, mirroring the sim-fed measurement path."""
        out: Dict[str, float] = {}
        for name, recipe in self._recipes.items():
            try:
                if _is_netlist_driven(recipe):
                    out[name] = float(self._netlist_report(recipe, params)["active_area"])
                else:
                    out[name] = float(_derived.compute_derived(recipe, params))
            except Exception as exc:  # bad recipe / missing param → NaN (graceful degradation)
                logger.warning(
                    "Derived metric %r failed (%s); metric stays NaN", name, exc
                )
                out[name] = float("nan")
        return out

    def report(self, params: Mapping[str, float], spec_name: Optional[str] = None) -> Dict[str, Any]:
        """Full active-area breakdown (per-device + coverage tally) for a netlist-driven spec —
        for the JSON verification surface and debug logging. ``spec_name`` defaults to the sole
        netlist-driven spec; pass it explicitly when more than one exists."""
        driven = {n: r for n, r in self._recipes.items() if _is_netlist_driven(r)}
        if not driven:
            raise ValueError("no netlist-driven derived metric to report")
        if spec_name is None:
            if len(driven) > 1:
                raise ValueError(f"specify spec_name; netlist-driven specs: {sorted(driven)}")
            spec_name = next(iter(driven))
        return self._netlist_report(driven[spec_name], params)

    def _netlist_report(self, recipe: Mapping[str, Any], params: Mapping[str, float]) -> Dict[str, Any]:
        if self._netlist_path is None:
            raise ValueError(
                "netlist-driven active_area needs a resolved DUT deck (none provided to build())"
            )
        scale = float(recipe.get("scale", 1.0))
        return _area.active_area_report(self._netlist_path, overrides=params, scale=scale)

    def close(self) -> None:  # symmetry with the sim-fed contexts — nothing to release
        return None

    def __enter__(self) -> "DerivedMetricContext":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def _is_netlist_driven(recipe: Mapping[str, Any]) -> bool:
    """A derived ``active_area`` recipe with no explicit ``devices:`` list is scored by the
    recursive netlist walk instead of a hand-authored device sum."""
    return str(recipe.get("derived", "")).strip() == "active_area" and "devices" not in recipe


__all__ = ["DerivedMetricContext"]
