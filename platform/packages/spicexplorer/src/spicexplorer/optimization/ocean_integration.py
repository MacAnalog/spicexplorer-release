"""Wire canonical OCEAN measurements into the optimizer loop (native-first).

The Spectre metric seam: a Spectre-backed testbench's
`target_spec`s each carry a declarative `measurement` recipe (see
`core.domains.TargetSpec.measurement`); this module turns those recipes into
`backends.ocean_metrics.OceanMeasurement`s, evaluates them **post-sim** on each
candidate's persisted PSF raw dir through **one persistent** `OceanMetricsSession`, and
merges the resulting scalars back into the `SpectreSimResult` under the spec's own
`name`. The optimizer's scorer is then unchanged: `result.scalar(target.name,
target.get_analysis())` (base.py) finds the OCEAN value via the result's bare-name
lookup.

Layering / blast-radius: this lives in the optimizer package (never `core`), and imports
`backends.ocean_metrics` **lazily** (inside methods) — `ocean_metrics` itself imports no
`virtuoso_bridge`, but keeping the import lazy means an ngspice-only run never touches it,
and construction of the actual `ocean` process is deferred to the first `measure()`.

One `OceanMetricsSession` holds one ADE/OCEAN license token for its lifetime, so the
context is created once per run and MUST be closed at run teardown (use it as a context
manager, or `try/finally` around the loop) — a leaked session leaks the token.
"""

from __future__ import annotations

import logging
import weakref
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from spicexplorer.core.domains import ListTargetSpec
    from spicexplorer_core.spice_engine import SimResult

logger = logging.getLogger(__name__)


def _close_quietly(session: Any) -> None:
    """Best-effort close for the GC/atexit finalizer — never raises (the interpreter may
    be shutting down; the goal is only to release the license token)."""
    try:
        session.close()
    except Exception:  # pragma: no cover - shutdown-time best effort
        pass


#: The declarative `builder:` names accepted in a `measurement:` recipe, mapping to the
#: `backends.ocean_metrics` constructor + its required argument keys. Kept here (not in
#: `core.domains`) so the DSL stays decoupled from the OCEAN backend; `core.domains` only
#: validates the recipe *shape*, this module validates builder name + args.
_BUILDER_ARGS: Dict[str, tuple[str, ...]] = {
    "ac_gain_db_at": ("signal", "freq_hz"),
    "ac_bandwidth_3db": ("signal",),
    "ac_gain_bw_product": ("signal",),
    "ac_peak_mag": ("signal",),
    "op_node_voltage": ("node",),
    "device_op_param": ("instance", "param"),
}


def build_ocean_measurement(name: str, recipe: Dict[str, Any]) -> Any:
    """One validated `measurement` recipe → an `OceanMeasurement` named `name`.

    `recipe` is either `{result, expr}` (raw OCEAN) or `{builder, ...args}` (a named
    `ocean_metrics` constructor). Raises `ValueError` on an unknown builder or a missing
    argument — before any simulation runs.
    """
    from spicexplorer.backends import ocean_metrics as om

    if "builder" in recipe:
        builder = str(recipe["builder"])
        required = _BUILDER_ARGS.get(builder)
        if required is None:
            raise ValueError(
                f"measurement for '{name}': unknown builder {builder!r}; "
                f"valid: {sorted(_BUILDER_ARGS)}."
            )
        missing = [k for k in required if k not in recipe]
        if missing:
            raise ValueError(
                f"measurement for '{name}': builder {builder!r} needs {list(required)}; "
                f"missing {missing}."
            )
        fn = getattr(om, builder)
        if builder == "ac_gain_db_at":
            return fn(name, str(recipe["signal"]), float(recipe["freq_hz"]))
        if builder in ("ac_bandwidth_3db", "ac_gain_bw_product", "ac_peak_mag"):
            return fn(name, str(recipe["signal"]))
        if builder == "op_node_voltage":
            return fn(name, str(recipe["node"]))
        # device_op_param
        return fn(name, str(recipe["instance"]), str(recipe["param"]))

    # raw form — shape already validated in TargetSpec._validate_measurement
    return om.OceanMeasurement(
        name=name, result=str(recipe["result"]), expr=str(recipe["expr"])
    )


def build_recipes(target_specs: "ListTargetSpec") -> Dict[str, List[Any]]:
    """Group enabled targets that carry an OCEAN measurement into `{testbench: [OceanMeasurement]}`.

    Only enabled specs are included (the scorer scores `enabled_targets()`), and only the ones
    whose recipe is the **OCEAN tier** (`{result, expr}` / `{builder, …}`) — filtered by
    `has_ocean_measurement()`, symmetric with `measure_integration` (Tier-1 `{meas}`) and
    `derived_integration` (`{derived}`). A Tier-1 or param-derived recipe on a `spectre` run
    would otherwise be fed to `build_ocean_measurement` and KeyError on the missing `result`
    key (both are engine-agnostic and handled by their own contexts). An empty result means no
    OCEAN wiring is needed at all.
    """
    recipes: Dict[str, List[Any]] = {}
    for target in target_specs.enabled_targets():
        recipe = target.measurement
        if recipe is None or not target.has_ocean_measurement():
            continue
        recipes.setdefault(target.testbench, []).append(
            build_ocean_measurement(target.name, recipe)
        )
    return recipes


class OceanMergeContext:
    """Owns the run's persistent `OceanMetricsSession` and merges its scalars into results.

    Built once per optimization run (via :meth:`build`, which returns ``None`` when no
    target has an OCEAN recipe — so an ngspice or PSF-only Spectre run spawns no session).
    `merge` runs after each corner's `simulate_circuit` and before scoring, so per-corner
    raw dirs are read correctly. Close it at run teardown (context manager or
    ``try/finally``) to release the OCEAN license token.
    """

    def __init__(self, recipes: Dict[str, List[Any]], *, vb_env_file: str | None = None) -> None:
        self._recipes = recipes
        self._vb_env_file = vb_env_file
        self._session: Any | None = None  # lazily spawned on first measure
        # GC / interpreter-exit backstop: if this context is dropped without an explicit
        # close() (e.g. a bare evaluate() that never enters optimize()'s teardown), the
        # finalizer still quits the ocean process and releases its ADE token. Registered
        # lazily in _ensure_session (there's nothing to close until a session exists); it
        # holds the SESSION, not `self`, so it never keeps this context alive.
        self._finalizer: weakref.finalize | None = None

    @classmethod
    def build(
        cls, target_specs: "ListTargetSpec", *, vb_env_file: str | None = None
    ) -> "OceanMergeContext | None":
        """Construct from the project's target specs, or `None` if none carry a recipe."""
        recipes = build_recipes(target_specs)
        if not recipes:
            return None
        logger.info(
            "OCEAN metric path active for testbench(es) %s (%d measurement(s) total)",
            sorted(recipes),
            sum(len(v) for v in recipes.values()),
        )
        return cls(recipes, vb_env_file=vb_env_file)

    @property
    def testbenches(self) -> frozenset[str]:
        return frozenset(self._recipes)

    def _ensure_session(self) -> Any:
        if self._session is None:
            from spicexplorer.backends.ocean_metrics import OceanMetricsSession

            self._session = OceanMetricsSession.from_vb_env(env_file=self._vb_env_file)
            self._finalizer = weakref.finalize(self, _close_quietly, self._session)
        return self._session

    def merge(self, results: "Dict[str, SimResult]", *, label: str | None = None) -> None:
        """For each OCEAN-backed testbench in `results`, evaluate its measurements on that
        run's raw dir and merge the scalars into the result under each spec's name.

        A result that isn't a Spectre result (no `raw_dir`/`merge_scalars` — e.g. an
        ngspice testbench in a mixed-engine project), or a Spectre run that persisted no
        raw dir (fixed-deck without `work_dir=`), is skipped — the affected metric stays
        NaN and scores as a penalty, matching the loop's existing graceful degradation.
        """
        for testbench, measurements in self._recipes.items():
            result = results.get(testbench)
            if result is None:
                continue
            raw_dir = getattr(result, "raw_dir", None)
            merge_scalars = getattr(result, "merge_scalars", None)
            if not callable(merge_scalars):
                continue  # not a Spectre result
            if not raw_dir:
                logger.warning(
                    "testbench %r has OCEAN measurements but its run left no raw dir "
                    "(pass work_dir= / use composed-deck mode); metrics %s stay NaN",
                    testbench,
                    [m.name for m in measurements],
                )
                continue
            scalars = self._ensure_session().measure(raw_dir, measurements, label=label)
            merge_scalars(scalars)

    def close(self) -> None:
        """Quit the OCEAN process (releases the license token). Idempotent."""
        if self._finalizer is not None:
            self._finalizer.detach()  # explicit close supersedes the GC backstop
            self._finalizer = None
        if self._session is not None:
            try:
                self._session.close()
            finally:
                self._session = None

    def __enter__(self) -> "OceanMergeContext":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = ["build_ocean_measurement", "build_recipes", "OceanMergeContext"]
