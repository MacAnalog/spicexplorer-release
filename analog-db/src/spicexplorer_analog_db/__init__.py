"""SpiceXplorer analog circuit database — registry + tiered verify harness.

Resolve the on-disk database via ``paths.db_root()`` — the single env-overridable seam.
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
