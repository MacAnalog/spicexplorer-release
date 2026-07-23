"""Programmatic circuit scaffolding — the write path behind the UI Register wizard.

Creates a **new draft** circuit directory from a manifest dict: sanitizes the id, coerces the
payload into a schema-valid ``circuit.yaml`` (forcing ``status: draft``), validates it against
``circuit.schema.json``, and refuses to clobber an existing circuit. It writes only the manifest
(+ an optional minimal ``datasheet.yaml``) — **no netlist/bindings** yet; a designer fills those in
before the circuit can assemble or run. Deliberately guarded (id sanitization, overwrite refusal)
because it can be driven from a web request (``POST /api/library/circuits``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from . import paths, schema

CIRCUIT_SCHEMA = "spicexplorer/circuit@1"
DATASHEET_SCHEMA = "spicexplorer/datasheet@1"

# lowercase, digits, underscore; must start with a letter — also the on-disk directory name, so
# this doubles as path-traversal protection (no ``/``, ``..``, leading dot).
_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# The only keys ``circuit.schema.json`` permits (additionalProperties: false).
_ALLOWED = {
    "schema", "id", "class", "display_name", "compensation", "stages",
    "ports", "provenance", "artifacts", "pdks", "analyses", "optimize", "status",
}


class ScaffoldError(ValueError):
    """A manifest that can't be turned into a valid draft circuit (bad id / missing fields)."""


_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


def allocate_id(class_id: str, slug: str) -> str:
    """The next free accession id for ``class_id``: ``<id_code>_<nnn>_<slug>``.

    Allocation is max+1 over the checked-out registry — append-only by construction (a concurrent
    branch claiming the same number surfaces as a Tier-0 ``id:accession_unique`` failure at merge,
    never silently). Raises :class:`ScaffoldError` for an unknown class / undeclared ``id_code`` /
    malformed slug."""
    from .model import class_id_code, next_accession

    if not _SLUG_RE.match(slug):
        raise ScaffoldError(f"invalid slug {slug!r} — must match {_SLUG_RE.pattern}")
    code = class_id_code(class_id)
    if not code:
        raise ScaffoldError(
            f"class {class_id!r} declares no id_code in _shared/classes/{class_id}/metrics.yaml"
        )
    return f"{code}_{next_accession(code):03d}_{slug}"


def normalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Coerce a (wizard) payload into a schema-valid ``circuit.yaml`` doc — ``status`` is always
    forced to ``draft`` and only schema-permitted keys survive. Raises :class:`ScaffoldError` for a
    malformed id / missing class."""
    cid = str(manifest.get("id", "")).strip()
    if not _ID_RE.match(cid):
        raise ScaffoldError(f"invalid circuit id {cid!r} — must match {_ID_RE.pattern}")
    klass = str(manifest.get("class", "")).strip()
    if not klass:
        raise ScaffoldError("class is required")

    doc: dict[str, Any] = {
        "schema": CIRCUIT_SCHEMA,
        "id": cid,
        "class": klass,
        "display_name": str(manifest.get("display_name") or cid),
    }
    if manifest.get("compensation"):
        doc["compensation"] = str(manifest["compensation"])
    if manifest.get("stages") is not None:
        try:
            doc["stages"] = int(manifest["stages"])
        except (TypeError, ValueError):
            pass
    doc["ports"] = [str(p) for p in (manifest.get("ports") or [])]
    prov = manifest.get("provenance") or {}
    if isinstance(prov, dict) and prov:
        doc["provenance"] = prov
    doc["pdks"] = [str(p) for p in (manifest.get("pdks") or [])]
    if manifest.get("analyses"):
        doc["analyses"] = [str(a) for a in manifest["analyses"]]
    doc["status"] = "draft"  # a scaffold is always a draft, never trust an incoming status
    return {k: v for k, v in doc.items() if k in _ALLOWED}


def _yaml(header: str, doc: dict[str, Any]) -> str:
    return header + yaml.safe_dump(doc, sort_keys=False, width=100)


def scaffold_circuit(
    manifest: dict[str, Any], *, overwrite: bool = False, datasheet: dict[str, Any] | None = None
) -> Path:
    """Create ``circuits/<id>/`` with a schema-valid draft ``circuit.yaml`` (+ optional
    ``datasheet.yaml``) and return the directory.

    Raises :class:`ScaffoldError` (bad manifest — the caller maps it to 400), ``FileExistsError``
    (circuit already exists and ``overwrite`` is false — 409), or ``FileNotFoundError`` when the DB
    root isn't present.
    """
    doc = normalize_manifest(manifest)
    errs = schema.validation_errors(doc, "circuit")
    if errs:
        raise ScaffoldError("manifest fails circuit@1 schema: " + "; ".join(errs))

    root = paths.circuits_root()
    if not root.parent.is_dir():
        raise FileNotFoundError(f"analog-db root not found at {paths.db_root()}")
    cdir = root / doc["id"]
    if cdir.exists() and not overwrite:
        raise FileExistsError(f"circuit {doc['id']!r} already exists")

    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "circuit.yaml").write_text(
        _yaml("# GENERATED by the Register wizard (analog-db authoring) — DRAFT.\n"
              "# Fill in abstract/netlist.spice + pdk/<pdk>/ bindings before it can assemble/run.\n", doc)
    )

    # Optional datasheet stub — best-effort: only written if it validates (the schema may require
    # more than a bare stub, in which case the draft circuit simply has no datasheet yet).
    ds = {"schema": DATASHEET_SCHEMA, **(datasheet or {})}
    if datasheet and not schema.validation_errors(ds, "datasheet"):
        (cdir / "datasheet.yaml").write_text(_yaml("# GENERATED (draft) by the Register wizard.\n", ds))

    return cdir
