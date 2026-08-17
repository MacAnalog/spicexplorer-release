#!/usr/bin/env python3
"""DEPRECATED shim — the Spectre gm/ID extraction is now a first-class analog-db tool.

The prototype that lived here was promoted to the package
(:mod:`spicexplorer_analog_db.gmid_spectre`) with registry-driven config
(`_shared/pdk/<pdk>.yaml` → ``gmid:`` block, incl. the ``simulator: {workers, timeout_s}``
parallelization knobs). Use the CLI:

    analog-db gmid-extract-spectre --pdk <spectre-pdk> [--corner all] [--workers N] [--smoke|--dry-run]

This shim just forwards there so old invocations keep working. See `_shared/GMID.md`
("The Spectre lane") for the full flow doc.
"""
from __future__ import annotations

import sys

from spicexplorer_analog_db import cli

if __name__ == "__main__":
    sys.exit(cli.main(["gmid-extract-spectre", *sys.argv[1:]]))
