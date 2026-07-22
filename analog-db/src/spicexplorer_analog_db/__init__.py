"""SpiceXplorer analog circuit database — registry + tiered verify harness.

See ``doc/plan_examples_db.md`` (design) and ``doc/todo_examples_db.md`` (phases).
The on-disk database lives under ``examples/`` in-tree (Phases 0–3), then extracts to the
``spicexplorer-analog-db`` submodule at the P3→P4 boundary (D-9). Resolve it via
``paths.db_root()`` — the single env-overridable seam.
"""

from . import catalog, generate, gmid, model, paths, schema, verify
from .extends import ExtendsError, resolve_extends
from .model import Circuit, list_circuit_ids, load_circuit
from .verify import CheckResult, run, run_tier0

__all__ = [
    "Circuit",
    "CheckResult",
    "ExtendsError",
    "catalog",
    "generate",
    "gmid",  # gm/ID LUT extraction + `gmid.lut(pdk, device, corner)` one-step load
    "list_circuit_ids",
    "load_circuit",
    "model",
    "paths",
    "resolve_extends",
    "run",
    "run_tier0",
    "schema",
    "verify",
]
