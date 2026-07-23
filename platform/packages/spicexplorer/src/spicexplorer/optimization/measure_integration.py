"""Wire canonical Tier-1 (engine-neutral Python) measurements into the optimizer loop.

The Python-tier twin of :mod:`spicexplorer.optimization.ocean_integration`. A target spec
whose ``measurement`` recipe is ``{meas: <name>, ...args}`` (see
:class:`spicexplorer.core.domains.TargetSpec` and
:mod:`spicexplorer_core.measurements.registry`) names a canonical figure of merit computed
in pure Python from the testbench's :class:`~spicexplorer_core.spice_engine.protocol.SimResult`.
This module groups those recipes per testbench, evaluates them **post-sim** on each
candidate's result, and merges the scalars back under each spec's own ``name`` — so the
scorer is unchanged: ``result.scalar(target.name, target.get_analysis())`` (base.py) finds
the value via the result's merged-scalar lookup.

Unlike the OCEAN (Tier-2) path this holds **no license and no external process**: the math
lives in ``spicexplorer-core`` and runs on the raw waves the result already carries, so it
works identically for ngspice and Spectre results and needs no teardown. It is built once
per run (via :meth:`build`, ``None`` when no target carries a Tier-1 recipe) purely to
avoid recomputing the recipe grouping each evaluation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from spicexplorer_core.measurements import registry as _registry

if TYPE_CHECKING:
    from spicexplorer.core.domains import ListTargetSpec
    from spicexplorer_core.spice_engine import SimResult

logger = logging.getLogger(__name__)

# Per testbench: (spec name, recipe dict, engine-neutral analysis string).
_Recipe = Tuple[str, Dict[str, Any], str]


def build_recipes(target_specs: "ListTargetSpec") -> Dict[str, List[_Recipe]]:
    """Group enabled targets carrying a Tier-1 ``{meas: …}`` recipe into ``{tb: [recipe]}``.

    Only enabled specs with a Python-tier measurement are included, and each recipe's name
    and required args are validated here (before any sim) so a typo fails loudly at load —
    symmetric with the OCEAN builder validation.
    """
    recipes: Dict[str, List[_Recipe]] = {}
    for target in target_specs.enabled_targets():
        if not target.has_python_measurement():
            continue
        recipe = dict(target.measurement or {})
        _registry.validate_recipe(target.name, recipe)
        recipes.setdefault(target.testbench, []).append(
            (target.name, recipe, target.get_analysis())
        )
    return recipes


class MeasureMergeContext:
    """Groups the run's Tier-1 recipes and merges their computed scalars into results.

    Built once per run (:meth:`build` returns ``None`` when no target carries a Tier-1
    recipe). :meth:`merge` runs after each corner's ``simulate_circuit`` and before scoring
    — so per-corner results are measured with their own waves. No resource to release
    (:meth:`close` is a no-op), but the object supports the same close/context-manager
    contract as the OCEAN context so the optimizer can tear both down uniformly.
    """

    def __init__(self, recipes: Dict[str, List[_Recipe]]) -> None:
        self._recipes = recipes

    @classmethod
    def build(cls, target_specs: "ListTargetSpec") -> "MeasureMergeContext | None":
        recipes = build_recipes(target_specs)
        if not recipes:
            return None
        logger.info(
            "Tier-1 measurement path active for testbench(es) %s (%d measurement(s) total)",
            sorted(recipes),
            sum(len(v) for v in recipes.values()),
        )
        return cls(recipes)

    @property
    def testbenches(self) -> frozenset[str]:
        return frozenset(self._recipes)

    def merge(self, results: "Dict[str, SimResult]", *, label: str | None = None) -> None:
        """Evaluate each testbench's Tier-1 measurements and merge the scalars into its
        result under the spec names. A result lacking ``merge_scalars`` is skipped (the
        metric stays NaN → scorer penalty); a measurement that raises degrades to NaN so
        one bad extraction never crashes the loop."""
        for testbench, items in self._recipes.items():
            result = results.get(testbench)
            if result is None:
                continue
            merge_scalars = getattr(result, "merge_scalars", None)
            if not callable(merge_scalars):
                logger.warning(
                    "testbench %r has Tier-1 measurements but its result is not mergeable; "
                    "metrics %s stay NaN",
                    testbench,
                    [name for name, _r, _a in items],
                )
                continue
            scalars: Dict[str, float] = {}
            for name, recipe, analysis in items:
                try:
                    scalars[name] = float(
                        _registry.measure(result, recipe, default_analysis=analysis)
                    )
                except Exception as exc:  # extraction failure → NaN (graceful degradation)
                    logger.warning(
                        "Tier-1 measurement %r on testbench %r failed (%s); metric stays NaN",
                        name,
                        testbench,
                        exc,
                    )
                    scalars[name] = float("nan")
            merge_scalars(scalars)

    def close(self) -> None:  # symmetry with OceanMergeContext — nothing to release
        return None

    def __enter__(self) -> "MeasureMergeContext":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = ["build_recipes", "MeasureMergeContext"]
