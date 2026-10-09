"""CLI: ``python -m spicexplorer_core.workspace.retention`` — run pruning (see ``__init__``).

A package ``__main__`` rather than a guard block in the retention module: the workspace package
``__init__`` imports the retention module, so running that module itself as ``__main__`` made
runpy warn on every run and execute a second copy of it. This module reuses the imported one, and
keeps the guard so a plain import of it runs no (non-dry-run) sweep.
"""

from spicexplorer_core.workspace.retention import main

if __name__ == "__main__":
    raise SystemExit(main())
