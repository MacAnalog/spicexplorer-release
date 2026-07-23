"""JSON-Schema validation of the database YAML docs (the agent contract, plan D-7).

The ``_shared/schema/*.schema.json`` files ARE the contract agents consume; here we just load
them and validate instances with ``jsonschema``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from jsonschema import Draft202012Validator

from . import paths

# logical name -> filename under _shared/schema/
_SCHEMA_FILES = {
    "circuit": "circuit.schema.json",
    "datasheet": "datasheet.schema.json",
    "analysis": "analysis.schema.json",
    "sizing": "sizing.schema.json",
    "class": "class.schema.json",
    "scoreboard-entry": "scoreboard-entry.schema.json",
    "params": "params.schema.json",
    "composition": "composition.schema.json",
}


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    try:
        fname = _SCHEMA_FILES[name]
    except KeyError as exc:
        raise KeyError(f"unknown schema {name!r}; known: {sorted(_SCHEMA_FILES)}") from exc
    with (paths.schema_root() / fname).open() as fh:
        return json.load(fh)


def validation_errors(doc: dict[str, Any], schema_name: str) -> list[str]:
    """Return human-readable validation errors for ``doc`` against the named schema (empty = ok)."""
    validator = Draft202012Validator(load_schema(schema_name))
    out: list[str] = []
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        out.append(f"{loc}: {err.message}")
    return out
