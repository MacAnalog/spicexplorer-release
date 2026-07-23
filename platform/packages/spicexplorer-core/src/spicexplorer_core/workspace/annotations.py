"""Curated vs. derived annotations.

Two homes for subcircuit-role annotations:

- ``analyses/annotation/<key>/`` — RAW machine output, a disposable composite-keyed
  cache (GC'd like any analysis).
- ``design/cells/<cell>/annotations.yaml`` — CURATED, versioned design data with
  provenance, anchored to STRUCTURAL identities (device names / circuitgraph subgraph
  signatures), NOT file hashes — so a human correction survives unrelated netlist edits.

The load-bearing rule: **regeneration is a merge PROPOSAL, never a blind
overwrite.** :func:`merge_proposal` classifies a fresh raw labeling against the curated
set (add / agree / conflict / stale, flagging human-protected conflicts);
:func:`merge_curated` applies only the SAFE changes (new labels + updates to labels
that are EXPLICITLY ``reviewed_by: agent``) and PRESERVES everything else — a human
override *or* a hand-authored entry with no ``reviewed_by`` (default-protected).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from spicexplorer_core.atomic_io import atomic_write_text

ANNOTATIONS_NAME = "annotations.yaml"
ANNOTATIONS_VERSION = 1
REVIEW_HUMAN = "human"
REVIEW_AGENT = "agent"


def _cell_file(project_dir: Path, cell: str) -> Path:
    return project_dir / "design" / "cells" / cell / ANNOTATIONS_NAME


def _role(v: Any) -> Any:
    return v.get("role") if isinstance(v, dict) else v


def read_curated(project_dir: Path, cell: str) -> dict[str, dict[str, Any]]:
    """The cell's curated annotations, keyed by structural identity. Missing → ``{}``."""
    p = _cell_file(project_dir, cell)
    if not p.is_file():
        return {}
    data = yaml.safe_load(p.read_text()) or {}
    ann = data.get("annotations") if isinstance(data, dict) else None
    if not isinstance(ann, dict):
        return {}
    return {k: (dict(v) if isinstance(v, dict) else {"role": v}) for k, v in ann.items()}


def write_curated(
    project_dir: Path, cell: str, annotations: dict[str, dict[str, Any]],
    *, now: datetime | None = None,
) -> None:
    """Atomically write the cell's curated annotations (with a version + timestamp)."""
    p = _cell_file(project_dir, cell)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": ANNOTATIONS_VERSION,
        "updated": (now or datetime.now()).isoformat(timespec="seconds"),
        "annotations": annotations,
    }
    atomic_write_text(p, yaml.safe_dump(payload, sort_keys=False))


def merge_proposal(
    curated: dict[str, dict[str, Any]], raw: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Classify a fresh RAW labeling against the curated set WITHOUT changing anything.
    Buckets: ``add`` (new), ``agree`` (same role), ``conflict`` (different role —
    ``protected`` when the curated side is human-reviewed), ``stale`` (curated identity
    the raw pass no longer produces)."""
    prop: dict[str, list[dict[str, Any]]] = {"add": [], "agree": [], "conflict": [], "stale": []}
    for ident, rv in raw.items():
        rrole = _role(rv)
        if ident not in curated:
            prop["add"].append({"id": ident, "role": rrole})
            continue
        cur = curated[ident]
        crole = _role(cur)
        if crole == rrole:
            prop["agree"].append({"id": ident, "role": crole})
        else:
            reviewed = cur.get("reviewed_by") if isinstance(cur, dict) else None
            prop["conflict"].append({
                "id": ident, "curated": crole, "raw": rrole,
                # protected = anything NOT explicitly agent-owned (human or hand-authored),
                # matching merge_curated's default-protected rule.
                "reviewed_by": reviewed, "protected": reviewed != REVIEW_AGENT,
            })
    for ident, cur in curated.items():
        if ident not in raw:
            prop["stale"].append({"id": ident, "role": _role(cur)})
    return prop


def merge_curated(
    curated: dict[str, dict[str, Any]], raw: dict[str, Any],
    *, now: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Apply a raw regeneration to the curated set SAFELY: add new labels, update
    still-agent-owned labels, and PRESERVE every human-reviewed override (recording what
    raw proposed under ``overrides``). Stale curated entries are kept, not deleted —
    curated data is precious; staleness surfaces via :func:`merge_proposal`."""
    stamp = (now or datetime.now()).isoformat(timespec="seconds")
    out = {k: dict(v) for k, v in curated.items()}
    for ident, rv in raw.items():
        rrole = _role(rv)
        prov = rv.get("derived_from") if isinstance(rv, dict) else None
        if ident not in out:
            entry = {"role": rrole, "reviewed_by": REVIEW_AGENT, "updated": stamp}
            if prov:
                entry["derived_from"] = prov
            out[ident] = entry
            continue
        cur = out[ident]
        # An entry is safe to auto-update ONLY if it is EXPLICITLY agent-owned. Anything
        # else — reviewed_by: human, or a hand-authored entry with no reviewed_by at all
        # (the shape read_curated invites) — is protected, so a human edit is never
        # silently overwritten. This is the honest reading of "preserve every human
        # override": default-protected, opt-in-updatable.
        if cur.get("reviewed_by") != REVIEW_AGENT:
            if cur.get("role") != rrole:          # preserve the curated call; record the raw proposal
                cur["overrides"] = rrole
            continue
        if cur.get("role") != rrole:              # explicitly agent-owned → safe to update
            cur["role"] = rrole
            cur["updated"] = stamp
            if prov:
                cur["derived_from"] = prov
    return out
