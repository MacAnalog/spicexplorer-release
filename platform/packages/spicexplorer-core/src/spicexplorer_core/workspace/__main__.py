"""CLI: additively migrate a WORK_ROOT to layout v2 (see ``migrate.py``).

Usage::

    uv run python -m spicexplorer_core.workspace [--work-root PATH] [--dry-run]

Prints the JSON report. Safe to re-run (idempotent); ``--dry-run`` reports what
would change without touching the filesystem.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from spicexplorer_core.workspace.migrate import migrate_workspace


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m spicexplorer_core.workspace",
        description="Additively migrate a WORK_ROOT to project-filesystem layout v2.",
    )
    ap.add_argument(
        "--work-root",
        type=Path,
        default=None,
        help="WORK_ROOT to migrate (default: $WORK_ROOT, else <repo>/work)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without writing anything",
    )
    args = ap.parse_args(argv)
    report = migrate_workspace(args.work_root, dry_run=args.dry_run)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
