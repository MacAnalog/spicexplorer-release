"""The committed verify record: each circuit's DERIVED status rung (plan §6 / D-13).

``catalog.json`` carries two statuses per circuit. ``status`` is the AUTHORED value from
``circuit.yaml``. ``derived_status`` is the highest rung of the verify ladder the circuit cleared
(``verify.derive_status``): ``generated`` = Tiers 0, 1 and 2, ``simulated`` = + Tier 3,
``validated`` = + Tier 4 with every spec-bounded ``conform:*`` row passing.

The catalog build is deterministic and PDK-free, and Tier 0 byte-compares it with the committed
file, so it cannot run the tiers itself. It reads the rung from ``verify_status.json`` at the DB
root, which this module reduces from a ``analog-db verify --json`` matrix report::

    analog-db verify --tier 0 --tier 1 --tier 2 --json > <scratch>/matrix.json
    analog-db verify-status --from <scratch>/matrix.json --write
    analog-db catalog --write

A record holds, per circuit: the rung, the tiers that ran (a tier with at least one pass or fail
row for the circuit; an all-skip tier did not run), the date, the platform commit, the
``conform:*`` tally when Tier 4 ran, and a fingerprint (``fingerprint``) of the files under
``circuits/<id>/`` and, for a composite, those of each block its ``composition.yaml`` instantiates.
``scoreboard/`` is left out on purpose: T0's ``scoreboard:*`` rows read it, but
``analog-db run --write`` appends to it, so neither a new design point nor a failing
``scoreboard:*`` row drops the rung.

The catalog publishes a recorded rung only while it still holds:

- the fingerprint equals the one computed now. An edit to those files voids the rung, and with it
  every T1 drift that starts in them: a hand edit to a generated file, a block edit that leaves a
  composite's generated netlist or sizing stale, and the regeneration that follows either;
- the tiers that ran back the rung (``RUNG_TIERS``);
- ``validated`` only when every ``conform:*`` row of that run passed.

Otherwise the catalog keeps the provenance and says why in ``derived_from.invalidated``.

The fingerprint does not read ``_shared/`` or the platform packages. A tier failure that starts
there (a PDK device map, a class testbench template, a platform upgrade) leaves the rung published
until a new run is recorded. When it leaves generated files stale, Tier 1 fails on that tree, and
the regeneration that clears it changes the circuit's files and voids the rung.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml

from . import compose, model, paths, schema, yamlio

SCHEMA = "spicexplorer/verify-status@1"

# The tiers each rung needs to have run (and cleared, which derive_status checks).
RUNG_TIERS: dict[str, tuple[int, ...]] = {
    "draft": (),
    "incomplete": (),
    "reference": (0,),
    "generated": (0, 1, 2),
    "simulated": (0, 1, 2, 3),
    "validated": (0, 1, 2, 3, 4),
}

# Left out of a circuit's fingerprint: design points (``scoreboard/``), which T0's scoreboard:*
# integrity rows do read but which `analog-db run --write` appends to, so neither a new design
# point nor a failing scoreboard:* row drops the rung; layout entries (``pdk/<pdk>/layout-*/``,
# which verify skips), prose and figures, and machine-local by-products (all in .gitignore).
_SKIP_DIRS = frozenset({"scoreboard", "__pycache__", ".ipynb_checkpoints", "temp_spice_out"})
_SKIP_SUFFIXES = frozenset({".md", ".png", ".svg", ".pdf", ".pyc", ".log", ".raw"})
_SKIP_NAMES = frozenset({".DS_Store"})

# DB-level rows that do not block a reduction: the stale catalog and the old record are what the
# reduction and the `catalog --write` after it replace.
_DB_ROWS_REPLACED = ("catalog:determinism", "verify_status:")


class ReportError(ValueError):
    """A matrix report that cannot back a record (wrong shape, a ``--pdk`` run, a failed DB row)."""


# --------------------------------------------------------------------------- fingerprint


def _fingerprinted(rel: Path) -> bool:
    parts = rel.parts
    if any(p in _SKIP_DIRS for p in parts[:-1]):
        return False
    if len(parts) > 3 and parts[0] == "pdk" and parts[2].startswith("layout-"):
        return False
    return rel.suffix not in _SKIP_SUFFIXES and rel.name not in _SKIP_NAMES


def _file_entries(circuit_dir: Path) -> list[bytes]:
    """One entry per fingerprinted file of ``circuit_dir``, in sorted path order: its
    ``/``-separated relative path, a NUL byte, and the SHA-256 of its bytes."""
    files: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(circuit_dir):
        dirnames.sort()
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(circuit_dir)
            if _fingerprinted(rel):
                files.append((rel.as_posix(), p))
    return [
        rel_posix.encode() + b"\0" + hashlib.sha256(p.read_bytes()).digest()
        for rel_posix, p in sorted(files)
    ]


def _hex16(entries: list[bytes]) -> str:
    h = hashlib.sha256()
    for entry in entries:
        h.update(entry)
    return h.hexdigest()[:16]


def composed_blocks(circuit_dir: Path) -> list[str]:
    """The block ids the ``composition.yaml`` of ``circuit_dir`` instantiates, sorted and
    unique. Empty for an atomic circuit, and for a composition.yaml that does not parse or
    names no block (Tier 1 ``gen:compose`` reports that one)."""
    path = circuit_dir / compose.COMPOSITION_FILE
    if not path.is_file():
        return []
    try:
        doc = yamlio.read_yaml(path)
    except yaml.YAMLError:
        return []
    rows = doc.get("instances") if isinstance(doc, dict) else None
    if not isinstance(rows, list):
        return []
    return sorted({str(row["block"]) for row in rows if isinstance(row, dict) and row.get("block")})


def fingerprint(circuit_dir: Path) -> str:
    """16 hex digits of a SHA-256 over every fingerprinted file of ``circuit_dir``.

    For a composite the hash also covers, per block its ``composition.yaml`` instantiates, the
    block id and the fingerprint of that block's own files (``absent`` when ``circuits/<block>/``
    holds no ``circuit.yaml``). Tier 1 ``gen:compose`` composes from those files; a block that is
    itself a composite is read through its own committed flat netlist, so only one level is
    included.
    """
    entries = _file_entries(circuit_dir)
    for block_id in composed_blocks(circuit_dir):
        block_dir = circuit_dir.parent / block_id  # model.load_circuit(block_id).dir
        block_fp = (
            _hex16(_file_entries(block_dir)) if (block_dir / "circuit.yaml").is_file() else "absent"
        )
        entries.append(b"\0block\0" + block_id.encode() + b"\0" + block_fp.encode())
    return _hex16(entries)


# --------------------------------------------------------------------------- platform pin


def git_pin(directory: Path) -> str:
    """The commit ``directory`` is checked out at (12 hex digits), ``-modified`` appended when
    tracked files differ from it; ``unknown`` when it is not in a git checkout."""

    def git(*argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(directory), *argv], capture_output=True, text=True, timeout=30
        )

    try:
        head = git("rev-parse", "--short=12", "HEAD")
        if head.returncode != 0 or not head.stdout.strip():
            return "unknown"
        modified = git("diff", "--quiet", "HEAD", "--").returncode != 0
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return head.stdout.strip() + ("-modified" if modified else "")


def platform_pin() -> str:
    """The platform commit whose packages this harness runs: the checkout holding
    ``spicexplorer_core`` (``unknown`` when that package is absent or not in a checkout)."""
    try:
        import spicexplorer_core
    except ImportError:
        return "unknown"
    return git_pin(Path(spicexplorer_core.__file__).resolve().parent)


# --------------------------------------------------------------------------- reduce


def _rows(report: Any) -> list[dict]:
    if not isinstance(report, list):
        raise ReportError("a verify report is the JSON list `analog-db verify --json` prints")
    for i, row in enumerate(report):
        ok = (
            isinstance(row, dict)
            and isinstance(row.get("circuit"), str)
            and isinstance(row.get("tier"), int)
            and isinstance(row.get("check"), str)
            and row.get("status") in ("pass", "fail", "skip")
        )
        if not ok:
            raise ReportError(f"row {i} is not a verify result row: {row!r}")
        if "pdk_scope" in row:
            raise ReportError(
                "the report comes from a `verify --pdk` run, which lists only part of the rows; "
                "re-run without --pdk"
            )
    return report


def reduce_report(report: Any, *, date: str, platform: str) -> dict[str, dict]:
    """``{circuit: record}`` from a ``verify --json`` report (see the module doc)."""
    from .verify import CheckResult, derive_status  # verify imports this module

    rows = _rows(report)
    red = sorted(
        {
            r["check"]
            for r in rows
            if not r["circuit"]
            and r["status"] == "fail"
            and not r["check"].startswith(_DB_ROWS_REPLACED)
        }
    )
    if red:
        raise ReportError(f"DB-level check(s) failed, so no rung can be recorded: {red}")
    ids = sorted({r["circuit"] for r in rows if r["circuit"]})
    unknown = sorted(set(ids) - set(model.list_circuit_ids()))
    if unknown:
        raise ReportError(f"the report names circuits this database does not have: {unknown}")
    results = [
        CheckResult(r["circuit"], r["tier"], r["check"], r["status"], r.get("reason", ""))
        for r in rows
    ]
    records: dict[str, dict] = {}
    for cid in ids:
        mine = [r for r in results if r.circuit == cid]
        tiers = sorted({r.tier for r in mine if r.status != "skip"})
        record: dict[str, Any] = {
            "status": derive_status(cid, results),
            "tiers": tiers,
            "date": date,
            "platform": platform,
            "fingerprint": fingerprint(model.load_circuit(cid).dir),
        }
        if 4 in tiers:
            conform = [
                r for r in mine if r.tier == 4 and r.check.startswith("conform:") and "@" in r.check
            ]
            record["conform"] = {
                "passed": sum(r.status == "pass" for r in conform),
                "total": len(conform),
            }
        records[cid] = record
    return records


def document(records: dict[str, dict]) -> dict[str, Any]:
    return {"schema": SCHEMA, "circuits": dict(sorted(records.items()))}


def to_json(doc: dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


# --------------------------------------------------------------------------- read


def read_committed() -> dict[str, Any] | None:
    """The committed report as parsed JSON; ``None`` when there is no file."""
    path = paths.verify_status_path()
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def problems(doc: Any) -> list[str]:
    """Why ``doc`` is not a usable record: schema errors, then circuits the DB does not have."""
    if not isinstance(doc, dict):
        return ["not a JSON object"]
    errs = schema.validation_errors(doc, "verify-status")
    if errs:
        return errs
    gone = sorted(set(doc["circuits"]) - set(model.list_circuit_ids()))
    return [f"records circuits the database no longer has: {gone}"] if gone else []


def load() -> dict[str, dict]:
    """The committed records the catalog may use: ``{}`` with no file or an unusable one (the
    Tier-0 ``verify_status:record`` row says why)."""
    try:
        doc = read_committed()
    except ValueError:
        return {}
    if doc is None or problems(doc):
        return {}
    return doc["circuits"]


def void_reason(record: dict, fingerprint_now: str) -> str | None:
    """Why a recorded rung no longer holds, or ``None`` when it does."""
    status, tiers = record["status"], set(record["tiers"])
    if record["fingerprint"] != fingerprint_now:
        return (
            f"the circuit's files, or those of a block its composition.yaml instantiates, "
            f"changed after the verify run of {record['date']}; re-run "
            "`analog-db verify --json` and `analog-db verify-status`"
        )
    missing = sorted(set(RUNG_TIERS[status]) - tiers)
    if missing:
        return f"rung {status!r} needs tier(s) {missing}, which the run did not cover"
    if status == "validated":
        tally = record.get("conform") or {}
        passed, total = tally.get("passed", 0), tally.get("total", 0)
        if not total or passed != total:
            return (
                f"'validated' needs every conform:* row to pass; the run passed {passed} of {total}"
            )
    return None


def published(record: dict | None, circuit_dir: Path) -> dict[str, Any]:
    """The catalog fields for one circuit: none without a record, else ``derived_from``
    (date, platform, tiers) plus ``derived_status`` while the rung holds."""
    if record is None:
        return {}
    source = {"date": record["date"], "platform": record["platform"], "tiers": record["tiers"]}
    reason = void_reason(record, fingerprint(circuit_dir))
    if reason:
        return {"derived_from": {**source, "invalidated": reason}}
    return {"derived_status": record["status"], "derived_from": source}
