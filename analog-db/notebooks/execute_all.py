"""Execute every notebook in this directory top-to-bottom (the CI notebook-smoke lane).

The notebooks are written to run PDK-free on a fresh clone — SPICE cells self-detect the
base image and skip — so a clean execution here is a real end-to-end check of the library
APIs they demonstrate (a gm/ID back-annotation bug was once caught only by a notebook cell).

Usage (borrowed platform venv, needs nbformat + nbclient):
    $VENV/bin/python notebooks/execute_all.py

Executes in-memory only — committed outputs are not rewritten.
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parent
TIMEOUT_S = 600  # per cell


def main() -> int:
    notebooks = sorted(HERE.glob("*.ipynb"))
    if not notebooks:
        print("no notebooks found", file=sys.stderr)
        return 1
    failed: list[str] = []
    for path in notebooks:
        print(f"== executing {path.name}", flush=True)
        nb = nbformat.read(path, as_version=4)
        client = NotebookClient(
            nb, timeout=TIMEOUT_S, kernel_name="python3", resources={"metadata": {"path": HERE}}
        )
        try:
            client.execute()
        except Exception as exc:  # nbclient raises CellExecutionError et al.
            print(f"!! {path.name} failed: {exc}", file=sys.stderr)
            failed.append(path.name)
    if failed:
        print(f"FAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"all {len(notebooks)} notebooks executed cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
